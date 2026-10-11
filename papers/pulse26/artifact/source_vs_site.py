"""Stage D: is the M2 modulation in the 26 s SOURCE or in the station noise floor / site?
For G.EDA (Cameroon, ~240 km from 4N 8E) and G.TAM (Tamanrasset, Algeria, ~2100 km, far from any ocean):
 - M2/S2/N2 harmonic regression (jointly with K1,O1,Q1,M4,S1,S3) of 72-h high-passed hourly series:
   fixed-band 26 s line PSD (37.5-38.6 mHz, no peak picking), background bands 20-24 s and 29-34 s,
   line PSD after regressing out the background bands, SNR, detection, peak frequency.
 - null: smoothed-spectrum phase-randomised surrogates (red-noise, narrow lines removed), re-masked.
 - modulation phase expressed as hours after M2 high water at Port Sonara (Limbe), i.e. in the source region.
 - yearly stacked spectra (34.5-40 mHz) of QC windows to check the period history and the 28 s line.
Writes source_vs_site.txt/json and fig3_periodogram_tidal.png, fig6_source_vs_site.png, fig7_yearly_stacks.png."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view as swv
D = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(11)
T0 = np.datetime64("2019-05-01T00:00", "s").astype(np.int64); T1 = np.datetime64("2026-10-01T00:00", "s").astype(np.int64)
NH = int((T1 - T0) // 3600); grid_t = T0 + 5400.0 + 3600.0 * np.arange(NH); tg_d = (grid_t - T0) / 86400.0
TP = np.load(os.path.join(D, "tide/tide_pred_hourly.npz")); tide_g = np.interp(grid_t, TP["t"].astype(float), TP["h"])
W = dict(M2=1.9322736, S2=2.0, N2=1.8959820, K1=1.0027379, O1=0.9295357, Q1=0.8932441, M4=3.8645472, S1=1.0, S3=3.0)
NAMES = list(W); LOG = []; OUT = {}
def log(s): print(s, flush=True); LOG.append(s)
_pinv = {}
def fit(x, m):
    key = (int(m.sum()), int(np.flatnonzero(m)[:50].sum()), int(np.flatnonzero(m)[-50:].sum()))
    if key not in _pinv:
        cols = [np.ones(m.sum())]
        for nm in NAMES: cols += [np.cos(2 * np.pi * W[nm] * tg_d[m]), np.sin(2 * np.pi * W[nm] * tg_d[m])]
        _pinv[key] = np.linalg.pinv(np.array(cols).T)
    b = _pinv[key] @ x[m]; return {nm: (b[1 + 2 * i], b[2 + 2 * i]) for i, nm in enumerate(NAMES)}
bt = fit(tide_g - tide_g.mean(), np.ones(NH, bool)); REF = {nm: np.arctan2(bt[nm][1], bt[nm][0]) for nm in ["M2", "S2", "N2"]}
def lag_h(ab, nm): return ((np.arctan2(ab[1], ab[0]) - REF[nm]) % (2 * np.pi)) / (2 * np.pi * W[nm]) * 24.0
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
def test(label, x, m, scale=1.0, unit="", nsur=100):
    b = fit(x, m); A = {nm: float(np.hypot(*b[nm]) * scale) for nm in NAMES}
    sur = np.array([[np.hypot(*bb[nm]) * scale for nm in ["M2", "S2", "N2"]] for bb in (fit(y, m) for y in surrogates(x, m, nsur))])
    p = {nm: float((np.sum(sur[:, i] >= A[nm]) + 1) / (nsur + 1)) for i, nm in enumerate(["M2", "S2", "N2"])}
    # phase uncertainty: surrogate scatter of a single cos/sin component ~ sigma; dphi ~ sigma/A
    sig = np.sqrt(np.mean(sur[:, 0] ** 2) / 2); dlag = float(np.degrees(min(np.pi, sig / max(A["M2"], 1e-12))) / 360 * 12.42)
    r = dict(A=A, p=p, lagM2=float(lag_h(b["M2"], "M2")), lagS2=float(lag_h(b["S2"], "S2")), dlagM2=dlag, null95=float(np.percentile(sur[:, 0], 95)), n=int(m.sum()))
    log(f"  {label:40s} n={m.sum():6d}  M2 {A['M2']:.3g}{unit} (null95 {r['null95']:.2g}, p={p['M2']:.3f}, +{r['lagM2']:.1f}±{dlag:.1f} h after HW)  "
        f"S2 {A['S2']:.3g} (p={p['S2']:.3f}, +{r['lagS2']:.1f} h)  N2 {A['N2']:.3g} (p={p['N2']:.3f})  S1 {A['S1']:.2g}")
    return r
def load(sta):
    fn = os.path.join(D, "features.npz" if sta == "EDA" else f"features_{sta}.npz"); F = np.load(fn)
    c = {k: F["X"][:, i] for i, k in enumerate(F["cols"])}; t = F["t"]
    day = (t // 86400).astype(int); lp = c["lp_psd"]
    ud, inv_d = np.unique(day, return_inverse=True); dmed = np.array([np.median(lp[inv_d == k]) for k in range(len(ud))])
    runmed = np.median(swv(np.pad(dmed, 7, mode="edge"), 15), axis=1)
    qc = (lp < 5 * runmed[inv_d]) & (c["peak_mad"] < 30)
    thr = np.quantile(c["csnr_w"][qc], 0.99); det = qc & (c["snr_w"] >= thr)
    return dict(c=c, t=t, qc=qc, det=det, thr=thr, hidx=((t - T0) // 3600).astype(int), logP=F["logP36"].astype(np.float32), f36=F["f36"])
def grid(S, v, m, sel=None):
    g = np.full(NH, np.nan); mm = m if sel is None else (m & sel); g[S["hidx"][mm]] = v[mm]; return g
L10 = lambda v: np.log10(np.maximum(v, 1e-30)); DB = 10.0
def station_tests(sta, S, sel=None, tag=""):
    c, qc, det = S["c"], S["qc"], S["det"]; R = {}
    n_q = int((qc if sel is None else qc & sel).sum()); n_d = int((det if sel is None else det & sel).sum())
    log(f"== {sta}{tag}: QC windows {n_q}, detected {n_d} ({n_d/max(n_q,1):.1%}; control-band 1% FAR threshold {S['thr']:.2f})")
    ser = {"fixband 26 s line PSD (37.5-38.6 mHz)": L10(c["fixband"]), "background 20-24 s": L10(c["bg_2024"]),
           "background 29-34 s": L10(c["bg_2834"]), "background 33-50 s (20-30 mHz)": L10(c["lp_psd"]),
           "SNR (Welch)": L10(c["snr_w"])}
    X = {}
    for k, v in ser.items():
        X[k] = prep(hp(grid(S, v, qc, sel))); R[k] = test(k, X[k][0], X[k][1], DB, " dB")
    # line PSD with the background bands regressed out (same windows)
    y, m = X["fixband 26 s line PSD (37.5-38.6 mHz)"]; b1, _ = X["background 20-24 s"]; b2, _ = X["background 29-34 s"]
    G = np.c_[np.ones(m.sum()), b1[m], b2[m]]; beta = np.linalg.lstsq(G, y[m], rcond=None)[0]
    res = np.zeros(NH); res[m] = y[m] - G @ beta; res[m] -= res[m].mean()
    log(f"  (regression of line PSD on background bands: coefs {beta[1]:.2f}, {beta[2]:.2f})")
    R["line PSD minus background (regressed)"] = test("line PSD minus background (regressed)", res, m, DB, " dB")
    xd, md = prep(hp(grid(S, det.astype(float), qc, sel))); R["detection"] = test("detection (fraction)", xd, md, 100.0, " %pts")
    xf, mf = prep(hp(grid(S, c["fpk"] * 1e6, det, sel))); R["freq"] = test("peak frequency (detected)", xf, mf, 1.0, " µHz")
    return R
E = load("EDA"); OUT["EDA"] = station_tests("G.EDA.00.LHZ 2019-05..2026-09", E)
have_tam = os.path.exists(os.path.join(D, "features_TAM.npz"))
if have_tam:
    T = load("TAM"); OUT["TAM"] = station_tests("G.TAM.00.LHZ 2022-03..2026-09", T)
    ov0 = np.datetime64("2022-03-01T00:00", "s").astype(np.int64)
    OUT["EDA_overlap"] = station_tests("G.EDA.00.LHZ", E, sel=E["t"] >= ov0, tag=" (overlap 2022-03..2026-09)")
    # simultaneous windows: does TAM SNR co-vary with EDA SNR at the same hour (shared source)?
    ge = hp(grid(E, L10(E["c"]["snr_w"]), E["qc"])); gt = hp(grid(T, L10(T["c"]["snr_w"]), T["qc"])); mm = np.isfinite(ge) & np.isfinite(gt)
    r = np.corrcoef(ge[mm], gt[mm])[0, 1]; log(f"hourly corr of 72-h high-passed log SNR, EDA vs TAM: r={r:.3f} (n={mm.sum()})")
    ge2 = grid(E, L10(E["c"]["snr_w"]), E["qc"]); gt2 = grid(T, L10(T["c"]["snr_w"]), T["qc"]); mm2 = np.isfinite(ge2) & np.isfinite(gt2)
    r2 = np.corrcoef(ge2[mm2], gt2[mm2])[0, 1]; log(f"hourly corr of raw log SNR, EDA vs TAM: r={r2:.3f}")
    OUT["corr_snr_EDA_TAM"] = dict(hp=float(r), raw=float(r2))
# ---------------- figure 6: M2-phase binned, both stations ----------------
ph = ((2 * np.pi * W["M2"] * tg_d - REF["M2"]) % (2 * np.pi)); nb = 12; bins = (ph / (2 * np.pi) * nb).astype(int); ang = (np.arange(nb) + 0.5) * 30
def binned(S, v, m, sel=None):
    x, mm = prep(hp(grid(S, v, m, sel)))
    bm = np.array([x[mm & (bins == k)].mean() for k in range(nb)]); se = np.array([x[mm & (bins == k)].std() / np.sqrt((mm & (bins == k)).sum() / 3) for k in range(nb)])
    return bm, se
stations = [("G.EDA (240 km)", E)] + ([("G.TAM (2096 km)", T)] if have_tam else [])
fig, ax = plt.subplots(1, len(stations) + 1, figsize=(5.2 * (len(stations) + 1), 4.2))
for i, (lab, S) in enumerate(stations):
    for nm, key, col in [("26 s line PSD (fixed band)", "fixband", "C3"), ("background 20-24 s", "bg_2024", "C0"), ("background 29-34 s", "bg_2834", "C2")]:
        bm, se = binned(S, L10(S["c"][key]), S["qc"]); ax[i].errorbar(ang, bm * DB, yerr=se * DB, fmt="o-", ms=3, capsize=2, color=col, label=nm)
    ax[i].set_title(lab, fontsize=9); ax[i].set_xlabel("M2 phase (deg; 0 = HW at Port Sonara)"); ax[i].set_ylabel("dB (72-h high-passed)"); ax[i].legend(fontsize=7)
a = ax[-1]
for (lab, S), col in zip(stations, ["C3", "C1"]):
    bm, se = binned(S, S["det"].astype(float), S["qc"]); a.errorbar(ang, (bm + S["det"][S["qc"]].mean()) * 100, yerr=se * 100, fmt="o-", ms=3, capsize=2, color=col, label=lab)
a.set_ylabel("26 s detection rate (%)"); a.set_xlabel("M2 phase (deg)"); a.legend(fontsize=7)
ab = a.twinx(); ab.plot(ang, np.cos(np.radians(ang)) * np.hypot(*bt["M2"]), "k--", lw=0.8); ab.set_ylabel("M2 tide at Port Sonara (m)")
fig.suptitle("Source or site? 26 s line power vs background, binned by M2 tidal phase (±1 SE, n_eff = n/3)", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig6_source_vs_site.png"), dpi=120); plt.close(fig)
# ---------------- figure 3 (replaces earlier version): zoomed periodograms around tidal bands ----------------
NF = 2 ** 18; fq = np.fft.rfftfreq(NF, 1 / 24.0)
ser = [("EDA 26 s line PSD (fixed band)", E, L10(E["c"]["fixband"]), E["qc"]), ("EDA background 20-24 s", E, L10(E["c"]["bg_2024"]), E["qc"]),
       ("EDA background 29-34 s", E, L10(E["c"]["bg_2834"]), E["qc"]), ("EDA peak frequency (detected)", E, E["c"]["fpk"] * 1e6, E["det"])]
if have_tam: ser.append(("TAM 26 s line PSD (fixed band)", T, L10(T["c"]["fixband"]), T["qc"]))
bands = [(0.86, 1.04), (1.86, 2.04), (0.02, 0.12)]
fig, ax = plt.subplots(len(ser), 3, figsize=(14, 2.3 * len(ser)), gridspec_kw=dict(width_ratios=[1, 1, 0.8]))
for i, (lab, S, v, m) in enumerate(ser):
    g = grid(S, v, m)
    for j, (f1, f2) in enumerate(bands):
        x, mm = prep(hp(g) if j < 2 else g - np.nanmedian(g)); sel = (fq >= f1) & (fq <= f2)
        P = np.abs(np.fft.rfft(x, NF)) ** 2; P = P[sel]
        lv = []
        for y in surrogates(x, mm, 50): lv.append((np.abs(np.fft.rfft(y, NF)) ** 2)[sel])
        lv = np.array(lv); norm = np.median(lv); a = ax[i, j]
        a.plot(fq[sel], P / norm, color="k", lw=0.6); a.plot(fq[sel], np.percentile(lv, 95, axis=0) / norm, color="C0", lw=0.8, label="95% surrogate (per freq)")
        a.plot(fq[sel], np.percentile(lv.max(axis=1), 95) * np.ones(sel.sum()) / norm, color="C0", lw=0.8, ls="--", label="95% band-max surrogate")
        for nm, f0 in [("Q1", 0.8932441), ("O1", 0.9295357), ("K1", 1.0027379), ("N2", 1.8959820), ("M2", 1.9322736), ("S2", 2.0), ("MSf", 0.0677), ("Mf", 0.0732)]:
            if f1 < f0 < f2:
                colr = "C1" if nm in ("S2", "K1") else "C3"; a.axvline(f0, color=colr, lw=0.8, alpha=0.5); a.text(f0, a.get_ylim()[1] * 0.92, nm, color=colr, fontsize=7, ha="center")
        for f0 in (1.0, 2.0):
            if f1 < f0 < f2: a.axvline(f0, color="0.5", lw=0.6, ls=":")
        a.set_xlim(f1, f2)
        if j == 0: a.set_ylabel(lab, fontsize=7)
        if i == len(ser) - 1: a.set_xlabel("cycles/day")
ax[0, 0].legend(fontsize=6)
fig.suptitle("Periodograms of hourly series (72-h high-passed for diurnal/semidiurnal panels; zero-filled gaps); red = lunar tidal lines, orange = solar-confounded S2/K1", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig3_periodogram_tidal.png"), dpi=115); plt.close(fig)
# ---------------- figure 7: yearly stacked spectra (QC windows), period history incl. 28 s line ----------------
fig, ax = plt.subplots(1, len(stations), figsize=(6.5 * len(stations), 4.5), squeeze=False)
yrs_res = {}
for i, (lab, S) in enumerate(stations):
    yr = S["t"].astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970; f36 = S["f36"]
    for y in np.unique(yr):
        sel = S["qc"] & (yr == y)
        if sel.sum() < 500: continue
        st = np.median(S["logP"][sel], axis=0); st -= np.median(st)
        ax[0, i].plot(f36 * 1e3, 10 * st, lw=1, label=str(y))
        m26 = (f36 > 0.0370) & (f36 < 0.0395); m28 = (f36 > 0.0350) & (f36 < 0.0368)
        yrs_res[f"{lab}|{y}"] = (float(1 / f36[m26][np.argmax(st[m26])]), float(1 / f36[m28][np.argmax(st[m28])]))
        log(f"  {lab} {y}: stacked-spectrum peak period 26 s line {yrs_res[f'{lab}|{y}'][0]:.3f} s; 28 s band peak {yrs_res[f'{lab}|{y}'][1]:.3f} s")
    ax[0, i].set_xlabel("frequency (mHz)"); ax[0, i].set_ylabel("dB rel. median"); ax[0, i].set_title(f"{lab}: median spectrum of QC 3-h windows, per year", fontsize=9); ax[0, i].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig7_yearly_stacks.png"), dpi=120); plt.close(fig)
OUT["yearly_stack_peaks"] = yrs_res
def js(o):
    if isinstance(o, dict): return {str(k): js(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [js(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
json.dump(js(OUT), open(os.path.join(D, "source_vs_site.json"), "w"), indent=1)
open(os.path.join(D, "source_vs_site.txt"), "w").write("\n".join(LOG) + "\n"); log("done")
