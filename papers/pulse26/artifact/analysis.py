"""Stage B: detection, period stability and tidal-modulation tests for the 26 s microseism at G.EDA.
Inputs: features.npz (features.py), tide/tide_pred_hourly.npz (tide_model.py), meta/era5_ocean_3N8E.json.
Outputs: figures (fig*.png), results.json, results.txt. Single process; run with `nice -n 19`."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view as swv
D = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(20261009)
OUT = {}; LOG = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s, flush=True); LOG.append(s)
F = np.load(os.path.join(D, "features.npz")); cols = list(F["cols"]); X = F["X"]; t = F["t"]
c = {k: X[:, i] for i, k in enumerate(cols)}
T0 = np.datetime64("2019-05-01T00:00", "s").astype(np.int64); T1 = np.datetime64("2026-10-01T00:00", "s").astype(np.int64)
NH = int((T1 - T0) // 3600); hidx = ((t - T0) // 3600).astype(int); tc = t + 5400.0   # window centre
def to_dt(s): return np.array(s, dtype="int64").astype("datetime64[s]")
# ---------------- quality control ----------------
lp = c["lp_psd"]; day = (t // 86400).astype(int)
# transient (earthquake) flag: 20-33 s background > 5x its 15-day running median, or impulsive samples
ud, inv_d = np.unique(day, return_inverse=True); dmed = np.array([np.median(lp[inv_d == k]) for k in range(len(ud))])
pad = np.pad(dmed, 7, mode="edge"); runmed = np.median(swv(pad, 15), axis=1)
qc = (lp < 5 * runmed[inv_d]) & (c["peak_mad"] < 30)
log(f"windows total {len(t)}, QC-pass {qc.sum()} ({qc.mean():.1%})")
# ---------------- detection threshold from control band ----------------
thr99 = np.quantile(c["csnr_w"][qc], 0.99); thr999 = np.quantile(c["csnr_w"][qc], 0.999)
det = qc & (c["snr_w"] >= thr99)
det_strict = qc & (c["snr_w"] >= thr999)
log(f"control-band SNR thresholds: 1% FAR {thr99:.2f}, 0.1% FAR {thr999:.2f}")
log(f"detection rate (1% FAR): {det.sum()}/{qc.sum()} = {det.sum()/qc.sum():.1%};  strict (0.1% FAR): {det_strict.sum()/qc.sum():.1%}")
OUT.update(n_windows=int(len(t)), n_qc=int(qc.sum()), thr99=float(thr99), thr999=float(thr999),
           det_rate=float(det.sum() / qc.sum()), det_rate_strict=float(det_strict.sum() / qc.sum()))
per = 1.0 / c["fpk"]
# ---------------- July 2023 confirmation (6-h comparable + 3-h) ----------------
dt_t = to_dt(t); yr = dt_t.astype("datetime64[Y]").astype(int) + 1970; mo = dt_t.astype("datetime64[M]").astype(int) % 12 + 1
jm = (yr == 2023) & (mo == 7)
dj = det & jm
def boot_median_ci(v, groups, n=2000):
    ug = np.unique(groups); idx = [np.flatnonzero(groups == g) for g in ug]; meds = []
    for _ in range(n):
        s = rng.integers(0, len(ug), len(ug)); meds.append(np.median(v[np.concatenate([idx[k] for k in s])]))
    return np.percentile(meds, [2.5, 97.5])
ci = boot_median_ci(per[dj], day[dj])
log(f"July 2023: QC windows {(qc&jm).sum()}, detected {dj.sum()} ({dj.sum()/max(1,(qc&jm).sum()):.1%}); median period {np.median(per[dj]):.3f} s "
    f"(95% day-block bootstrap CI {ci[0]:.3f}-{ci[1]:.3f}); robust spread (1.4826*MAD) {1.4826*np.median(np.abs(per[dj]-np.median(per[dj]))):.3f} s")
OUT["jul2023"] = dict(qc=int((qc & jm).sum()), det=int(dj.sum()), median_period=float(np.median(per[dj])), ci=list(map(float, ci)))
# Figure 1: July 2023 spectrogram
jt, jf, jP = F["jul_t"], F["jul_f"], F["jul_P"]
fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw=dict(height_ratios=[3, 1]))
tt = to_dt(jt + 5400).astype("datetime64[m]").astype("O")
im = ax[0].pcolormesh(tt, jf * 1e3, 10 * np.log10(jP.T), shading="nearest", cmap="magma",
                      vmin=np.percentile(10 * np.log10(jP), 5), vmax=np.percentile(10 * np.log10(jP), 99.7))
ax[0].axhspan(37.0, 39.5, xmin=0, xmax=0.01, color="c")
ax[0].set_ylabel("frequency (mHz)"); plt.colorbar(im, ax=ax[0], label="dB rel. 1 (m/s)$^2$/Hz", pad=0.01)
ax2 = ax[0].secondary_yaxis("right", functions=(lambda f: 1e3 / np.maximum(f, 1e-3), lambda p: 1e3 / np.maximum(p, 1e-3)))
ax2.set_ylabel("period (s)")
ax[0].set_title("G.EDA.00.LHZ (Edea, Cameroon), July 2023: 3-h Hann periodograms, 1-h step, response removed")
ax[1].semilogy(to_dt(tc[jm & qc]).astype("O"), c["snr_w"][jm & qc], ".", ms=3, color="0.5", label="26 s SNR (Welch)")
ax[1].semilogy(to_dt(tc[dj]).astype("O"), c["snr_w"][dj], ".", ms=3, color="C3", label="detected")
ax[1].axhline(thr99, color="k", lw=0.8, ls="--", label="1% control-band FAR"); ax[1].legend(fontsize=7, loc="upper right"); ax[1].set_ylabel("SNR")
fig.tight_layout(); fig.savefig(os.path.join(D, "fig1_spectrogram_2023-07.png"), dpi=130); plt.close(fig)
# ---------------- long-term: daily/monthly series ----------------
ndays = int((T1 - T0) // 86400); d0 = int(T0 // 86400)
def daily_stat(v, m, fn=np.median, minn=3):
    out = np.full(ndays, np.nan)
    dd = day[m] - d0; vv = v[m]; o = np.argsort(dd); dd, vv = dd[o], vv[o]
    u, s = np.unique(dd, return_index=True); e = np.r_[s[1:], len(dd)]
    for k, a, b in zip(u, s, e):
        if b - a >= minn and 0 <= k < ndays: out[k] = fn(vv[a:b])
    return out
f_day = daily_stat(c["fpk"], det); n_qc_day = daily_stat(np.ones(len(t)), qc, np.sum, 1)
n_det_day = daily_stat(np.ones(len(t)), det, np.sum, 1); n_det_day[np.isnan(n_det_day)] = 0
rate_day = np.where(n_qc_day >= 12, n_det_day / n_qc_day, np.nan)
amp_day = daily_stat(np.log10(np.maximum(c["amp_nms"], 1e-3)), det)
dates = (np.arange(ndays) + d0) * 86400
# monthly medians with bootstrap CI
months = np.unique(dt_t.astype("datetime64[M]")); mrows = []
for m in months:
    sel = det & (dt_t.astype("datetime64[M]") == m)
    if sel.sum() >= 30 and len(np.unique(day[sel])) >= 5:
        ci_m = boot_median_ci(per[sel], day[sel], 500)
        mrows.append((str(m), np.median(per[sel]), ci_m[0], ci_m[1], sel.sum(), sel.sum() / (qc & (dt_t.astype("datetime64[M]") == m)).sum()))
log("monthly median period (s) [95% CI] n_det det_rate:")
for r in mrows: log(f"  {r[0]}  {r[1]:.3f} [{r[2]:.3f},{r[3]:.3f}]  n={r[4]}  rate={r[5]:.2f}")
yrs = np.unique(yr); yrows = []
for y in yrs:
    sel = det & (yr == y)
    if sel.sum() > 50:
        ci_y = boot_median_ci(per[sel], day[sel], 500)
        yrows.append((int(y), float(np.median(per[sel])), float(ci_y[0]), float(ci_y[1]), int(sel.sum()), float(sel.sum() / (qc & (yr == y)).sum())))
        log(f"  year {y}: median {yrows[-1][1]:.3f} s [{ci_y[0]:.3f},{ci_y[1]:.3f}] n={sel.sum()} rate={yrows[-1][5]:.2f}")
OUT["yearly"] = yrows; OUT["monthly"] = [list(map(lambda z: z if isinstance(z, str) else float(z), r)) for r in mrows]
ci_all = boot_median_ci(per[det], day[det], 1000)
log(f"ALL: median period {np.median(per[det]):.3f} s [day-bootstrap 95% CI {ci_all[0]:.3f},{ci_all[1]:.3f}], spread (1.4826 MAD) {1.4826*np.median(np.abs(per[det]-np.median(per[det]))):.3f} s")
OUT["all_period"] = [float(np.median(per[det])), float(ci_all[0]), float(ci_all[1])]
# linear trend + seasonal harmonics on daily median frequency, moving-block bootstrap (30-day blocks)
ok = np.isfinite(f_day); td = (dates[ok] - dates[ok].mean()) / (365.25 * 86400); y = f_day[ok]
w = 2 * np.pi * td
G = np.c_[np.ones_like(td), td, np.cos(w), np.sin(w), np.cos(2 * w), np.sin(2 * w)]
beta = np.linalg.lstsq(G, y, rcond=None)[0]; res = y - G @ beta
dayk = np.flatnonzero(ok); blocks = dayk // 30; ub = np.unique(blocks); bidx = [np.flatnonzero(blocks == b) for b in ub]
bt = []
for _ in range(2000):   # residual block bootstrap
    s = rng.integers(0, len(ub), len(ub)); rr = np.concatenate([res[bidx[k]] for k in s])[:len(res)]
    if len(rr) < len(res): rr = np.r_[rr, res[:len(res) - len(rr)]]
    bt.append(np.linalg.lstsq(G, G @ beta + rr, rcond=None)[0])
bt = np.array(bt); f0 = beta[0]
trend_s_per_yr = -beta[1] / f0 ** 2; trend_ci = np.percentile(-bt[:, 1] / f0 ** 2, [2.5, 97.5])
ann_amp_s = np.hypot(beta[2], beta[3]) / f0 ** 2; ann_ci = np.percentile(np.hypot(bt[:, 2], bt[:, 3]) / f0 ** 2, [2.5, 97.5])
log(f"period trend {trend_s_per_yr*1e3:.2f} ms/yr (95% block-bootstrap CI {trend_ci[0]*1e3:.2f} to {trend_ci[1]*1e3:.2f}); "
    f"annual amplitude {ann_amp_s*1e3:.1f} ms [{ann_ci[0]*1e3:.1f},{ann_ci[1]*1e3:.1f}]; n_days {ok.sum()}")
OUT.update(trend_ms_per_yr=float(trend_s_per_yr * 1e3), trend_ci_ms=list(map(float, trend_ci * 1e3)), annual_amp_ms=float(ann_amp_s * 1e3))
# frequency vs excitation: daily median freq vs daily median log amplitude
m2 = np.isfinite(f_day) & np.isfinite(amp_day)
r_fa = np.corrcoef(1 / f_day[m2], amp_day[m2])[0, 1]; log(f"corr(daily period, daily log amplitude) = {r_fa:.3f} (n={m2.sum()})")
OUT["corr_period_amp_daily"] = float(r_fa)
# Figure 2: long-term daily spectra + figure 3 period time series
fig, ax = plt.subplots(4, 1, figsize=(12, 11), sharex=True, gridspec_kw=dict(height_ratios=[2.2, 1.6, 1, 1]))
ds, dsd, fs_ = F["dspec"], F["days"], F["fspec"]
full = np.full((ndays, ds.shape[1]), np.nan); kk = dsd - d0; okk = (kk >= 0) & (kk < ndays); full[kk[okk]] = ds[okk]
L = 10 * np.log10(full); L = L - np.nanmedian(L, axis=1, keepdims=True)
im = ax[0].pcolormesh(to_dt(dates).astype("datetime64[D]").astype("O"), fs_ * 1e3, L.T, shading="nearest", cmap="magma", vmin=-3, vmax=15)
ax[0].set_ylabel("freq (mHz)"); ax[0].set_title("G.EDA.00.LHZ daily-mean spectra (dB rel. daily median over 30-46 mHz)")
plt.colorbar(im, ax=ax[0], pad=0.01, label="dB")
tdt = to_dt(tc).astype("datetime64[m]").astype("O")
ax[1].plot(tdt[det], per[det], ",", color="0.6", alpha=0.4)
ax[1].plot(to_dt(dates).astype("datetime64[D]").astype("O"), 1 / f_day, ".", ms=2, color="C0", label="daily median")
mx = [np.datetime64(r[0]) + np.timedelta64(15, "D") for r in mrows]
ax[1].errorbar(np.array(mx).astype("O"), [r[1] for r in mrows], yerr=[[r[1] - r[2] for r in mrows], [r[3] - r[1] for r in mrows]],
               fmt="o", ms=3, color="C3", label="monthly median ±95% CI")
ax[1].set_ylim(25.9, 26.8); ax[1].set_ylabel("peak period (s)"); ax[1].legend(fontsize=7, loc="upper right")
ax[2].plot(to_dt(dates).astype("datetime64[D]").astype("O"), rate_day, ".", ms=2, color="C2"); ax[2].set_ylabel("daily det. rate")
ax[3].plot(to_dt(dates).astype("datetime64[D]").astype("O"), amp_day, ".", ms=2, color="C1"); ax[3].set_ylabel("log10 line amp (nm/s)")
fig.tight_layout(); fig.savefig(os.path.join(D, "fig2_longterm_spectra_period.png"), dpi=120); plt.close(fig)
# ---------------- tide series ----------------
TP = np.load(os.path.join(D, "tide/tide_pred_hourly.npz")); th, hh = TP["t"].astype(float), TP["h"]
tide_c = np.interp(tc, th, hh)                                  # tide height (m) at window centre
grid_t = T0 + 1800.0 + 3600.0 * np.arange(NH)                    # hourly grid of window centres? use centre = start+5400
grid_t = T0 + 5400.0 + 3600.0 * np.arange(NH)
tide_g = np.interp(grid_t, th, hh)
# window-averaged tide (3-h Hann-weighted average over the window) - what the window "sees"
wts = np.hanning(5)[1:-1]; wts /= wts.sum()
W_M2 = 1.9322736; W_S2 = 2.0; W_N2 = 1.8959820; W_K1 = 1.0027379; W_O1 = 0.9295357; W_Q1 = 0.8932441; W_M4 = 3.8645472
W_MSF = W_S2 - W_M2; W_MF = 0.0732022
LINES = dict(M2=W_M2, N2=W_N2, O1=W_O1, Q1=W_Q1, M4=W_M4, MSf=W_MSF, Mf=W_MF, S2=W_S2, K1=W_K1)
SOLAR = [1.0, 2.0, 3.0, 4.0]
# M2 phase: fit M2 sinusoid to predicted tide, phase 0 = M2 high water
tg_d = (grid_t - T0) / 86400.0
A = np.c_[np.cos(2 * np.pi * W_M2 * tg_d), np.sin(2 * np.pi * W_M2 * tg_d)]; ab = np.linalg.lstsq(A, tide_g, rcond=None)[0]
phi0 = np.arctan2(ab[1], ab[0]); log(f"M2 amplitude in prediction {np.hypot(*ab):.3f} m")
def m2phase(ts): return np.mod(2 * np.pi * W_M2 * (ts - T0) / 86400.0 - phi0, 2 * np.pi)
# spring-neap envelope: semidiurnal band analytic amplitude, 25-h smoothed
Z = np.fft.rfft(tide_g); fz = np.fft.rfftfreq(NH, 1 / 24.0); Zb = Z * ((fz > 1.6) & (fz < 2.4))
from scipy.signal import hilbert
env = np.abs(hilbert(np.fft.irfft(Zb, NH))); env = np.convolve(env, np.ones(25) / 25, mode="same")
# ---------------- build hourly-grid series ----------------
def grid_series(v, m):
    g = np.full(NH, np.nan); ii = hidx[m]; ok = (ii >= 0) & (ii < NH); g[ii[ok]] = v[m][ok]; return g
def hp_runmed(g, hw=36):
    p = np.pad(g, hw, mode="constant", constant_values=np.nan); out = np.empty_like(g)
    for s in range(0, len(g), 8192):
        blk = swv(p[s:s + 8192 + 2 * hw], 2 * hw + 1)
        with np.errstate(all="ignore"): out[s:s + len(blk)] = np.nanmedian(blk, axis=1)
    return g - out
def lp_daily_detrend(g, days_hw=30):
    dm = np.array([np.nanmedian(g[i:i + 24]) if np.isfinite(g[i:i + 24]).sum() >= 3 else np.nan for i in range(0, NH, 24)])
    p = np.pad(dm, days_hw, mode="constant", constant_values=np.nan)
    with np.errstate(all="ignore"): sm = np.nanmedian(swv(p, 2 * days_hw + 1), axis=1)
    return g - np.repeat(sm, 24)[:NH]
series = {}
fg = grid_series(c["fpk"] * 1e6, det)                    # µHz
series["freq"] = fg
series["logamp"] = grid_series(np.log10(np.maximum(c["amp_nms"], 1e-3)), det)
series["logsnr"] = grid_series(np.log10(c["snr_w"]), qc)  # detectability, all QC windows
series["det"] = grid_series(det.astype(float), qc)
series["bg"] = grid_series(np.log10(c["bg_w"]), qc)       # background near 26 s (control for noise level)
# ---------------- periodogram with surrogate nulls ----------------
NF = 2 ** 17; fq = np.fft.rfftfreq(NF, 1 / 24.0)   # cpd
def pgram(x):  # x: zero-filled anomaly
    return np.abs(np.fft.rfft(x, NF)) ** 2
def prep(g):
    m = np.isfinite(g); x = np.where(m, g - np.nanmean(g), 0.0); return x, m
def smooth_spec_surrogates(x, m, n):
    X = np.fft.rfft(x); amp = np.abs(X); k = 401
    p = np.pad(amp, k // 2, mode="reflect"); sm = np.empty_like(amp)
    for s in range(0, len(amp), 4096):
        sm[s:s + 4096] = np.median(swv(p[s:s + 4096 + k - 1], k), axis=1)
    sd = np.std(x[m])
    for _ in range(n):
        ph = np.exp(2j * np.pi * rng.random(len(amp))); ph[0] = 1
        y = np.fft.irfft(sm * ph, len(x)) * m; y[m] -= y[m].mean(); y *= sd / np.std(y[m]); yield y
def phase_rand_surrogates(x, m, n):
    X = np.fft.rfft(x); sd = np.std(x[m])
    for _ in range(n):
        ph = np.exp(2j * np.pi * rng.random(len(X))); ph[0] = 1
        y = np.fft.irfft(np.abs(X) * ph, len(x)) * m; y[m] -= y[m].mean(); y *= sd / np.std(y[m]); yield y
def shuffle_surrogates(x, m, n):
    v = x[m].copy()
    for _ in range(n):
        y = np.zeros_like(x); y[m] = rng.permutation(v); yield y
def line_power(P, f0, hw=1):
    j = int(round(f0 / fq[1])); return P[j - hw:j + hw + 1].max()
NSUR = 300
spec_res = {}
for name, hpf in [("freq", "short"), ("freq", "long"), ("logamp", "short"), ("logamp", "long"), ("logsnr", "short"), ("logsnr", "long"), ("det", "short")]:
    g = series[name]
    g = hp_runmed(g, 36) if hpf == "short" else lp_daily_detrend(g, 30)
    x, m = prep(g); P = pgram(x)
    tested = ["M2", "N2", "O1", "Q1", "M4", "S2", "K1"] if hpf == "short" else ["MSf", "Mf"]
    obs = {L: line_power(P, LINES[L]) for L in tested}
    sur_s = {L: [] for L in tested}; sur_w = {L: [] for L in tested}; Ps_all = []
    for y in smooth_spec_surrogates(x, m, NSUR):
        Ps = pgram(y)
        for L in tested: sur_s[L].append(line_power(Ps, LINES[L]))
        Ps_all.append(Ps[(fq < 4.5)].astype(np.float32)) if len(Ps_all) < 200 else None
    for y in shuffle_surrogates(x, m, 100):
        Ps = pgram(y)
        for L in tested: sur_w[L].append(line_power(Ps, LINES[L]))
    Ps_all = np.array(Ps_all); lvl95 = np.percentile(Ps_all, 95, axis=0); lvl99 = np.percentile(Ps_all, 99, axis=0)
    # empirical local rank: bins within +-0.1 cpd excluding +-3 bins around tidal and solar lines
    res = {}
    for L in tested:
        f0 = LINES[L]; band = (np.abs(fq - f0) < 0.1)
        for z in list(LINES.values()) + SOLAR + [1 - 1 / 365.2422, 2 + 2 / 365.2422, 2 - 2 / 365.2422]:
            band &= np.abs(fq - z) > 3 * fq[1]
        p_loc = (np.sum(P[band] >= obs[L]) + 1) / (band.sum() + 1)
        p_s = (np.sum(np.array(sur_s[L]) >= obs[L]) + 1) / (NSUR + 1)
        p_w = (np.sum(np.array(sur_w[L]) >= obs[L]) + 1) / 101
        bgl = np.median(P[band])
        res[L] = dict(power_over_local_median=float(obs[L] / bgl), p_redsur=float(p_s), p_local_rank=float(p_loc), p_shuffle=float(p_w))
        log(f"[{name}/{hpf}] {L}: P/median_local={obs[L]/bgl:.2f}  p(red-noise surrogate)={p_s:.3f}  p(local rank)={p_loc:.3f}  p(shuffle)={p_w:.3f}")
    spec_res[f"{name}_{hpf}"] = dict(P=P[fq < 4.5], lvl95=lvl95, lvl99=lvl99, res=res, nvalid=int(m.sum()),
                                      shuf95=float(np.percentile(np.concatenate([np.array(v) for v in sur_w.values()]), 95)))
OUT["spectral"] = {k: v["res"] for k, v in spec_res.items()}
# harmonic regression amplitudes (freq series, short high-pass): M2 amplitude in µHz and ms, with red-noise surrogate CI
def harm_fit(x, m, freqs):
    td = (grid_t[m] - T0) / 86400.0; cols_ = [np.ones(m.sum())]
    for f0 in freqs: cols_ += [np.cos(2 * np.pi * f0 * td), np.sin(2 * np.pi * f0 * td)]
    b = np.linalg.lstsq(np.array(cols_).T, x[m], rcond=None)[0]; return b
FIT = [W_M2, W_N2, W_O1, W_Q1, W_M4, 1.0, 2.0, 3.0, W_K1, 1 - 1 / 365.2422, 2 + 2 / 365.2422, 2 - 2 / 365.2422]
gx = hp_runmed(series["freq"], 36); x, m = prep(gx); b = harm_fit(x, m, FIT)
amps = {nm: np.hypot(b[1 + 2 * i], b[2 + 2 * i]) for i, nm in enumerate(["M2", "N2", "O1", "Q1", "M4", "S1", "S2", "S3", "K1", "P1~", "K2~", "T2~"])}
sur_amp = []
for y in smooth_spec_surrogates(x, m, 200):
    bb = harm_fit(y, m, FIT); sur_amp.append(np.hypot(bb[1], bb[2]))
sur_amp = np.array(sur_amp); f_mean = np.nanmean(c["fpk"][det])
for nm in ["M2", "N2", "O1", "M4", "S1", "S2"]:
    log(f"harmonic fit freq anomaly {nm}: {amps[nm]:.3f} µHz  (= {amps[nm]*1e-6/f_mean**2*1e3:.3f} ms in period)")
log(f"  M2 red-noise surrogate amplitude 95th pct {np.percentile(sur_amp,95):.3f} µHz; p={np.mean(sur_amp>=amps['M2']):.3f}")
OUT["harm_M2_uHz"] = float(amps["M2"]); OUT["harm_M2_sur95_uHz"] = float(np.percentile(sur_amp, 95))
OUT["harm_S1_uHz"] = float(amps["S1"]); OUT["harm_S2_uHz"] = float(amps["S2"])
OUT["harm_M2_ms"] = float(amps["M2"] * 1e-6 / f_mean ** 2 * 1e3); OUT["harm_M2_sur95_ms"] = float(np.percentile(sur_amp, 95) * 1e-6 / f_mean ** 2 * 1e3)
# ---------------- cross-correlation with tide + phase-binned stacking (phase-randomised nulls) ----------------
lags = np.arange(-12, 13)
def xcorr(x, m, ref):
    out = []
    for L in lags:
        r = np.roll(ref, -L); mm = m.copy()
        if L > 0: mm[-L:] = False
        if L < 0: mm[:-L] = False
        out.append(np.corrcoef(x[mm], r[mm])[0, 1])
    return np.array(out)
phase_g = m2phase(grid_t); nb = 12; edges = np.linspace(0, 2 * np.pi, nb + 1); bins = np.digitize(phase_g, edges) - 1
def binned(x, m):
    return np.array([x[m & (bins == k)].mean() for k in range(nb)])
def harm1(bm):
    ang = (edges[:-1] + edges[1:]) / 2; return np.hypot((bm * np.cos(ang)).mean(), (bm * np.sin(ang)).mean()) * 2
utc_hr = ((grid_t % 86400) // 3600).astype(int)
def hour_binned(x, m): return np.array([x[m & (utc_hr == k)].mean() for k in range(24)])
env_q = np.digitize(env, np.quantile(env, [0.2, 0.4, 0.6, 0.8]))
def env_binned(x, m): return np.array([x[m & (env_q == k)].mean() for k in range(5)])
xc_res = {}; bin_res = {}
for name in ["freq", "logamp", "logsnr", "det"]:
    g = hp_runmed(series[name], 36); x, m = prep(g)
    xc = xcorr(x, m, tide_g); bm = binned(x, m); A1 = harm1(bm); hb = hour_binned(x, m)
    gl = lp_daily_detrend(series[name], 30); xl, ml = prep(gl); eb = env_binned(xl, ml); erange = eb.max() - eb.min()
    sx, sA, sE = [], [], []
    for y in phase_rand_surrogates(x, m, NSUR):
        sx.append(np.abs(xcorr(y, m, tide_g)).max()); sA.append(harm1(binned(y, m)))
    for y in phase_rand_surrogates(xl, ml, NSUR):
        e_ = env_binned(y, ml); sE.append(e_.max() - e_.min())
    sx, sA, sE = map(np.array, (sx, sA, sE))
    pxc = (np.sum(sx >= np.abs(xc).max()) + 1) / (NSUR + 1); pA = (np.sum(sA >= A1) + 1) / (NSUR + 1); pE = (np.sum(sE >= erange) + 1) / (NSUR + 1)
    sd = np.std(x[m])
    log(f"[{name}] max|xcorr(tide)| = {np.abs(xc).max():.4f} at lag {lags[np.argmax(np.abs(xc))]} h, p={pxc:.3f}; "
        f"M2-phase 1st-harmonic amp = {A1:.4g} (= {A1/sd:.3f} SD), p={pA:.3f}; spring-neap quintile range = {erange:.4g}, p={pE:.3f}; "
        f"UTC-hour range = {np.nanmax(hb)-np.nanmin(hb):.4g}")
    xc_res[name] = dict(xc=xc, sx95=np.percentile(sx, 95), bm=bm, sA95=np.percentile(sA, 95), A1=A1, hb=hb, eb=eb, sE95=np.percentile(sE, 95), m=m, x=x, xl=xl, ml=ml)
    bin_res[name] = dict(max_abs_xcorr=float(np.abs(xc).max()), lag_h=int(lags[np.argmax(np.abs(xc))]), p_xcorr=float(pxc),
                         m2_phase_amp=float(A1), m2_phase_amp_sd=float(A1 / sd), p_m2phase=float(pA), springneap_range=float(erange), p_springneap=float(pE),
                         utc_hour_range=float(np.nanmax(hb) - np.nanmin(hb)))
OUT["tide_tests"] = bin_res
# ---------------- swell (ERA5 via Open-Meteo, 3N 8E) ----------------
try:
    E = json.load(open(os.path.join(D, "meta/era5_ocean_3N8E.json")))["hourly"]
    et = np.array([np.datetime64(s) for s in E["time"]]).astype("datetime64[s]").astype(np.int64)
    hs = np.array([np.nan if v is None else v for v in E["wave_height"]], float)
    tp = np.array([np.nan if v is None else v for v in E["wave_peak_period"]], float)
    eday = ((et - T0) // 86400).astype(int)
    hs_d = np.array([np.nanmean(hs[eday == k]) if np.any(eday == k) else np.nan for k in range(ndays)])
    tp_d = np.array([np.nanmean(tp[eday == k]) if np.any(eday == k) else np.nan for k in range(ndays)])
    sw = {}
    for lagd in [0, 1, 2]:
        a = np.roll(hs_d, lagd); mm = np.isfinite(a) & np.isfinite(rate_day); mm[:lagd] = False
        b_ = np.roll(tp_d, lagd); mb = np.isfinite(b_) & np.isfinite(rate_day); mb[:lagd] = False
        sw[lagd] = (np.corrcoef(a[mm], rate_day[mm])[0, 1], np.corrcoef(b_[mb], rate_day[mb])[0, 1])
        log(f"daily det-rate vs ERA5 Hs (lag {lagd} d): r={sw[lagd][0]:.3f}; vs ERA5 peak period: r={sw[lagd][1]:.3f}")
    # monthly climatology
    mon = to_dt(dates).astype("datetime64[M]").astype(int) % 12
    clim = [(k + 1, np.nanmean(rate_day[mon == k]), np.nanmean(hs_d[mon == k]), np.nanmean(tp_d[mon == k]), np.nanmedian(1 / f_day[mon == k])) for k in range(12)]
    log("month  det_rate  ERA5_Hs  ERA5_Tp  median_period")
    for r in clim: log(f"  {r[0]:2d}   {r[1]:.2f}   {r[2]:.2f}   {r[3]:.1f}   {r[4]:.3f}")
    OUT["swell"] = dict(corr_lag=sw, climatology=clim)
    # daily period vs Hs
    mm = np.isfinite(hs_d) & np.isfinite(f_day); log(f"daily median period vs ERA5 Hs: r={np.corrcoef(1/f_day[mm], hs_d[mm])[0,1]:.3f}")
except Exception as ex:
    log("swell analysis skipped:", ex)
# ---------------- figures 4 & 5 ----------------
fqp = fq[fq < 4.5]
fig, axs = plt.subplots(3, 2, figsize=(13, 10), gridspec_kw=dict(width_ratios=[2.2, 1]))
for row, name in enumerate(["freq", "logamp", "logsnr"]):
    for col, hpf, xl_ in [(0, "short", (0.75, 4.1)), (1, "long", (0.02, 0.2))]:
        S = spec_res[f"{name}_{hpf}"]; a = axs[row, col]; mk = (fqp >= xl_[0]) & (fqp <= xl_[1])
        norm = np.median(S["P"][mk]); a.semilogy(fqp[mk], S["P"][mk] / norm, lw=0.5, color="k")
        a.semilogy(fqp[mk], S["lvl95"][mk] / norm, color="C0", lw=0.8, label="95% red-noise surrogate")
        a.semilogy(fqp[mk], S["lvl99"][mk] / norm, color="C0", lw=0.8, ls="--", label="99%")
        a.axhline(S["shuf95"] / norm, color="C2", lw=0.8, ls=":", label="95% shuffled")
        for L, f0 in LINES.items():
            if xl_[0] < f0 < xl_[1]:
                a.axvline(f0, color="C3" if L not in ("S2", "K1") else "C1", lw=0.8, alpha=0.6)
                a.text(f0, a.get_ylim()[1] if False else (S["P"][mk] / norm).max() * 1.3, L, color="C3" if L not in ("S2", "K1") else "C1", fontsize=7, ha="center")
        for f0 in SOLAR:
            if xl_[0] < f0 < xl_[1]: a.axvline(f0, color="0.5", lw=0.8, ls="--", alpha=0.6)
        a.set_xlim(*xl_); a.set_title(f"{name} ({'72-h running-median high-pass' if hpf=='short' else '61-d detrended'})", fontsize=9)
        if row == 2: a.set_xlabel("frequency (cycles/day)")
        if col == 0: a.set_ylabel("power / median")
axs[0, 0].legend(fontsize=7, loc="lower left")
fig.suptitle("Periodograms of hourly 26 s pulse series (zero-filled gaps). Red: lunar tidal lines; orange: S2/K1 (solar-confounded); grey dashed: 1-4 cpd", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig3a_periodogram_fullband.png"), dpi=120); plt.close(fig)
fig, axs = plt.subplots(4, 4, figsize=(15, 11))
ang = np.degrees((edges[:-1] + edges[1:]) / 2)
for row, name in enumerate(["freq", "logamp", "logsnr", "det"]):
    R = xc_res[name]
    a = axs[row, 0]; a.plot(lags, R["xc"], "o-", ms=3); a.axhline(R["sx95"], color="C0", ls="--", lw=0.8); a.axhline(-R["sx95"], color="C0", ls="--", lw=0.8)
    a.set_title(f"{name}: xcorr with tide height", fontsize=8); a.set_xlabel("lag (h)")
    a = axs[row, 1]; a.plot(ang, R["bm"], "o-", ms=3)
    hs_ = R["sA95"] / 2; a.fill_between(ang, -hs_ + R["bm"].mean(), hs_ + R["bm"].mean(), color="C0", alpha=0.15, label="95% null (1st harm.)")
    a.set_title(f"{name}: M2-phase binned (0=HW)", fontsize=8); a.set_xlabel("M2 phase (deg)")
    a = axs[row, 2]; a.plot(np.arange(24), R["hb"], "o-", ms=3, color="C1"); a.set_title(f"{name}: UTC-hour binned (local=UTC+1)", fontsize=8); a.set_xlabel("UTC hour")
    a = axs[row, 3]; a.plot(np.arange(5), R["eb"], "o-", ms=3, color="C2"); a.set_title(f"{name}: spring-neap quintile (61-d detrended)", fontsize=8)
    a.set_xticks(range(5)); a.set_xticklabels(["neap", "", "", "", "spring"])
fig.suptitle("Tidal tests (rows: peak freq [µHz anomaly], log amplitude, log SNR, detection); dashed/shaded: 95% phase-randomised surrogate levels", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig4_tide_binned_xcorr.png"), dpi=110); plt.close(fig)
def jsonable(o):
    if isinstance(o, dict): return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
json.dump(jsonable(OUT), open(os.path.join(D, "results.json"), "w"), indent=1)
open(os.path.join(D, "results.txt"), "w").write("\n".join(LOG) + "\n")
log("done")
