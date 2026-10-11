"""Stage C: controls for the tidal tests. Separates line power (numerator) from local background noise
(denominator), tests other bands (primary/secondary microseism, control band, 28 s line), checks whether the
peak-frequency M2 signal survives conditioning on SNR, and checks phase stability across sub-periods.
Harmonic regression on 72-h high-passed hourly series, with M2,S2,N2,K1,O1,Q1,M4,S1,S3 fitted jointly.
Null: 'smoothed-spectrum' phase-randomised surrogates (red-noise background with narrow lines removed), re-masked."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view as swv
D = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(7)
F = np.load(os.path.join(D, "features.npz")); c = {k: F["X"][:, i] for i, k in enumerate(F["cols"])}; t = F["t"]
R = json.load(open(os.path.join(D, "results.json"))); thr = R["thr99"]
T0 = np.datetime64("2019-05-01T00:00", "s").astype(np.int64); T1 = np.datetime64("2026-10-01T00:00", "s").astype(np.int64)
NH = int((T1 - T0) // 3600); hidx = ((t - T0) // 3600).astype(int); grid_t = T0 + 5400.0 + 3600.0 * np.arange(NH)
day = (t // 86400).astype(int); lp = c["lp_psd"]
ud, inv_d = np.unique(day, return_inverse=True); dmed = np.array([np.median(lp[inv_d == k]) for k in range(len(ud))])
runmed = np.median(swv(np.pad(dmed, 7, mode="edge"), 15), axis=1)
qc = (lp < 5 * runmed[inv_d]) & (c["peak_mad"] < 30); det = qc & (c["snr_w"] >= thr)
TP = np.load(os.path.join(D, "tide/tide_pred_hourly.npz")); tide_g = np.interp(grid_t, TP["t"].astype(float), TP["h"])
W = dict(M2=1.9322736, S2=2.0, N2=1.8959820, K1=1.0027379, O1=0.9295357, Q1=0.8932441, M4=3.8645472, S1=1.0, S3=3.0)
NAMES = list(W)
tg_d = (grid_t - T0) / 86400.0
def design(m):
    cols = [np.ones(m.sum())]
    for nm in NAMES: cols += [np.cos(2 * np.pi * W[nm] * tg_d[m]), np.sin(2 * np.pi * W[nm] * tg_d[m])]
    return np.array(cols).T
_pinv = {}
def fit(x, m):
    key = (m.sum(), int(np.flatnonzero(m)[:50].sum()), int(np.flatnonzero(m)[-50:].sum()))
    if key not in _pinv: _pinv[key] = np.linalg.pinv(design(m))
    b = _pinv[key] @ x[m]
    return {nm: (b[1 + 2 * i], b[2 + 2 * i]) for i, nm in enumerate(NAMES)}
# reference: tide M2 phase (time of M2 high water)
bt = fit(tide_g - tide_g.mean(), np.ones(NH, bool)); tideM2 = np.arctan2(bt["M2"][1], bt["M2"][0])
btS = bt["S2"]; tideS2 = np.arctan2(btS[1], btS[0])
def lag_hours(ab, ref, f):   # hours after tidal HW (that constituent) at which modulation peaks
    return ((np.arctan2(ab[1], ab[0]) - ref) % (2 * np.pi)) / (2 * np.pi * f) * 24.0
def grid(v, m):
    g = np.full(NH, np.nan); ii = hidx[m]; g[ii] = v[m]; return g
def hp(g, hw=36):
    p = np.pad(g, hw, mode="constant", constant_values=np.nan); out = np.empty_like(g)
    for s in range(0, len(g), 8192):
        with np.errstate(all="ignore"): out[s:s + 8192] = np.nanmedian(swv(p[s:s + 8192 + 2 * hw], 2 * hw + 1), axis=1)
    return g - out
def prep(g):
    m = np.isfinite(g); return np.where(m, g - np.nanmean(g), 0.0), m
def surrogates(x, m, n, k=401):
    X = np.fft.rfft(x); amp = np.abs(X); p = np.pad(amp, k // 2, mode="reflect"); sm = np.empty_like(amp)
    for s in range(0, len(amp), 4096): sm[s:s + 4096] = np.median(swv(p[s:s + 4096 + k - 1], k), axis=1)
    sd = np.std(x[m])
    for _ in range(n):
        ph = np.exp(2j * np.pi * rng.random(len(amp))); ph[0] = 1
        y = np.fft.irfft(sm * ph, len(x)) * m; y[m] -= y[m].mean(); y *= sd / np.std(y[m]); yield y
def test(name, v, m, nsur=200, unit_scale=1.0, unit=""):
    x, mm = prep(hp(grid(v, m))); b = fit(x, mm)
    A = {nm: np.hypot(*b[nm]) * unit_scale for nm in NAMES}
    sur = []
    for y in surrogates(x, mm, nsur):
        bb = fit(y, mm); sur.append([np.hypot(*bb[nm]) * unit_scale for nm in ["M2", "S2", "N2"]])
    sur = np.array(sur); p = {nm: (np.sum(sur[:, i] >= A[nm]) + 1) / (nsur + 1) for i, nm in enumerate(["M2", "S2", "N2"])}
    lagM2 = lag_hours(b["M2"], tideM2, W["M2"]); lagS2 = lag_hours(b["S2"], tideS2, W["S2"])
    s = (f"{name:34s} n={mm.sum():6d}  M2 {A['M2']:.4g}{unit} (null95 {np.percentile(sur[:,0],95):.3g}, p={p['M2']:.3f}, peak {lagM2:.1f} h after M2 HW)  "
         f"S2 {A['S2']:.4g} (p={p['S2']:.3f}, {lagS2:.1f} h after S2 HW)  N2 {A['N2']:.4g} (p={p['N2']:.3f})  S1 {A['S1']:.3g}  O1 {A['O1']:.3g}")
    print(s, flush=True); LOG.append(s)
    return dict(A=A, p=p, lagM2=lagM2, lagS2=lagS2, null95_M2=float(np.percentile(sur[:, 0], 95)))
LOG = []; OUT = {}
L10 = lambda v: np.log10(np.maximum(v, 1e-30))
db = 10.0   # log10 power -> dB (amplitude of modulation in dB; peak-to-peak = 2x)
print("== power-type series (amplitude of M2 modulation in dB of PSD)")
OUT["logsnr_all"] = test("log SNR 26s (all QC)", L10(c["snr_w"]), qc, unit_scale=db, unit=" dB")
OUT["line_abs_all"] = test("26s peak abs PSD (all QC)", L10(c["snr_w"] * c["bg_w"]), qc, unit_scale=db, unit=" dB")
OUT["bg_all"] = test("background 30-34/42-46 mHz (QC)", L10(c["bg_w"]), qc, unit_scale=db, unit=" dB")
OUT["line_abs_det"] = test("26s peak abs PSD (detected)", L10(c["snr_w"] * c["bg_w"]), det, unit_scale=db, unit=" dB")
OUT["bg_det"] = test("background (detected windows)", L10(c["bg_w"]), det, unit_scale=db, unit=" dB")
OUT["ctrl_snr"] = test("control-band SNR 30-32.5 mHz", L10(c["csnr_w"]), qc, unit_scale=db, unit=" dB")
OUT["snr28"] = test("28 s line SNR (35-36.5 mHz)", L10(c["snr28"]), qc, unit_scale=db, unit=" dB")
OUT["lp"] = test("20-30 mHz background", L10(c["lp_psd"]), qc, unit_scale=db, unit=" dB")
OUT["pm"] = test("primary microseism 50-80 mHz", L10(c["pm_psd"]), qc, unit_scale=db, unit=" dB")
OUT["sm"] = test("secondary microseism 0.1-0.3 Hz", L10(c["sm_psd"]), qc, unit_scale=db, unit=" dB")
print("== peak frequency (µHz)")
f = c["fpk"] * 1e6
OUT["freq_det"] = test("freq (detected)", f, det, unit=" µHz")
hi = qc & (c["snr_w"] >= 2 * thr); OUT["freq_hi"] = test("freq (SNR >= 2x thr)", f, hi, unit=" µHz")
vhi = qc & (c["snr_w"] >= 4 * thr); OUT["freq_vhi"] = test("freq (SNR >= 4x thr)", f, vhi, unit=" µHz")
# condition on SNR: residual of freq after regressing on log SNR (within 72-h high-passed space)
xs, ms = prep(hp(grid(L10(c["snr_w"]), det))); xf, mf = prep(hp(grid(f, det))); mm = ms & mf
B = np.polyfit(xs[mm], xf[mm], 2); resid = np.full(NH, np.nan); resid[mm] = xf[mm] - np.polyval(B, xs[mm])
print(f"freq-vs-logSNR quadratic coefs {B}")
xr, mr = prep(resid); b = fit(xr, mr); A = np.hypot(*b["M2"]); sur = [np.hypot(*fit(y, mr)["M2"]) for y in surrogates(xr, mr, 200)]
s = f"freq residual after logSNR regression: M2 {A:.3g} µHz, null95 {np.percentile(sur,95):.3g}, p={(np.sum(np.array(sur)>=A)+1)/201:.3f}, peak {lag_hours(b['M2'], tideM2, W['M2']):.1f} h after HW"
print(s); LOG.append(s); OUT["freq_resid_M2"] = dict(A=float(A), p=float((np.sum(np.array(sur) >= A) + 1) / 201))
# sub-period phase consistency
print("== sub-period consistency (M2 amplitude, lag after HW)")
yr = t.astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970
sub = {}
for lab, sel in [("2019-2020", (yr <= 2020)), ("2021-2022", (yr >= 2021) & (yr <= 2022)), ("2023-2024", (yr >= 2023) & (yr <= 2024)), ("2025-2026", yr >= 2025)]:
    for nm, v, m, sc in [("logSNR", L10(c["snr_w"]), qc, db), ("lineabs", L10(c["snr_w"] * c["bg_w"]), qc, db), ("bg", L10(c["bg_w"]), qc, db), ("freq", f, det, 1.0)]:
        x, mm = prep(hp(grid(v, m & sel))); b = fit(x, mm)
        sub[(lab, nm)] = (np.hypot(*b["M2"]) * sc, lag_hours(b["M2"], tideM2, W["M2"]))
    s = f"  {lab}: " + "; ".join(f"{nm} {sub[(lab,nm)][0]:.3g} @ {sub[(lab,nm)][1]:.1f} h" for nm in ["logSNR", "lineabs", "bg", "freq"])
    print(s); LOG.append(s)
OUT["subperiods"] = {f"{k[0]}|{k[1]}": v for k, v in sub.items()}
# Figure: M2-phase-binned (12 bins) line abs PSD, background, SNR, detection rate, freq; tide height for reference
ph = ((2 * np.pi * W["M2"] * tg_d - tideM2) % (2 * np.pi)); nb = 12; bins = (ph / (2 * np.pi) * nb).astype(int)
ang = (np.arange(nb) + 0.5) * 360 / nb
fig, ax = plt.subplots(1, 3, figsize=(14, 4))
for nm, v, m in [("26 s peak abs PSD", L10(c["snr_w"] * c["bg_w"]), qc), ("background 30-46 mHz", L10(c["bg_w"]), qc), ("SNR", L10(c["snr_w"]), qc),
                 ("primary microseism", L10(c["pm_psd"]), qc), ("control-band SNR", L10(c["csnr_w"]), qc)]:
    x, mm = prep(hp(grid(v, m))); bm = np.array([x[mm & (bins == k)].mean() for k in range(nb)]) * db
    se = np.array([x[mm & (bins == k)].std() / np.sqrt((mm & (bins == k)).sum() / 3) for k in range(nb)]) * db  # /3: overlapping windows
    ax[0].errorbar(ang, bm, yerr=se, fmt="o-", ms=3, capsize=2, label=nm)
ax[0].set_xlabel("M2 phase (deg, 0 = M2 high water at Port Sonara)"); ax[0].set_ylabel("dB anomaly (72-h high-passed)"); ax[0].legend(fontsize=7)
x, mm = prep(hp(grid(det.astype(float), qc))); dr = np.array([x[mm & (bins == k)].mean() for k in range(nb)]) + det[qc].mean()
ax[1].plot(ang, dr * 100, "o-", color="C3"); ax[1].set_ylabel("detection rate (%)"); ax[1].set_xlabel("M2 phase (deg)")
ax1b = ax[1].twinx(); ax1b.plot(ang, np.cos(np.radians(ang)) * np.hypot(*bt["M2"]), "k--", lw=0.8); ax1b.set_ylabel("M2 tide (m)")
x, mm = prep(hp(grid(f, det))); fb = np.array([x[mm & (bins == k)].mean() for k in range(nb)])
fse = np.array([x[mm & (bins == k)].std() / np.sqrt((mm & (bins == k)).sum() / 3) for k in range(nb)])
ax[2].errorbar(ang, fb, yerr=fse, fmt="o-", color="C4", ms=3, capsize=2); ax[2].set_ylabel("peak-frequency anomaly (µHz)"); ax[2].set_xlabel("M2 phase (deg)")
ax2b = ax[2].secondary_yaxis("right", functions=(lambda u: -u * 1e-6 / (0.03796 ** 2) * 1e3, lambda v: -v * 1e-3 * 0.03796 ** 2 * 1e6)); ax2b.set_ylabel("period anomaly (ms)")
fig.suptitle("G.EDA 26 s pulse vs M2 tidal phase, 2019-2026 (error bars: ±1 SE, effective n = n/3 for 3-h windows at 1-h step)", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig5_M2_phase_controls.png"), dpi=120); plt.close(fig)
def js(o):
    if isinstance(o, dict): return {str(k): js(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [js(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
json.dump(js(OUT), open(os.path.join(D, "controls.json"), "w"), indent=1)
open(os.path.join(D, "controls.txt"), "w").write("\n".join(LOG) + "\n"); print("done")
