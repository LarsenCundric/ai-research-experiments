"""Shared helpers: hourly gridding, 72-h running-median high-pass, joint tidal harmonic regression,
smoothed-spectrum phase-randomised surrogates (red-noise null with narrow lines removed), station loader."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv
D = os.path.dirname(os.path.abspath(__file__)); rng = np.random.default_rng(23)
T0 = np.datetime64("2019-05-01T00:00", "s").astype(np.int64); T1 = np.datetime64("2026-10-01T00:00", "s").astype(np.int64)
NH = int((T1 - T0) // 3600); grid_t = T0 + 5400.0 + 3600.0 * np.arange(NH); tg_d = (grid_t - T0) / 86400.0
TP = np.load(os.path.join(D, "tide/tide_pred_hourly.npz")); tide_g = np.interp(grid_t, TP["t"].astype(float), TP["h"])
W = dict(M2=1.9322736, S2=2.0, N2=1.8959820, K1=1.0027379, O1=0.9295357, Q1=0.8932441, M4=3.8645472, S1=1.0, S3=3.0)
NAMES = list(W); LOG = []
def log(s): print(s, flush=True); LOG.append(s)
_pinv = {}
def fit(x, m):
    key = (int(m.sum()), int(np.flatnonzero(m)[:50].sum()), int(np.flatnonzero(m)[-50:].sum()))
    if key not in _pinv:
        cols = [np.ones(m.sum())]
        for nm in NAMES: cols += [np.cos(2 * np.pi * W[nm] * tg_d[m]), np.sin(2 * np.pi * W[nm] * tg_d[m])]
        _pinv[key] = np.linalg.pinv(np.array(cols).T)
    b = _pinv[key] @ x[m]; return {nm: (b[1 + 2 * i], b[2 + 2 * i]) for i, nm in enumerate(NAMES)}
_bt = fit(tide_g - tide_g.mean(), np.ones(NH, bool)); REF = {nm: np.arctan2(_bt[nm][1], _bt[nm][0]) for nm in ["M2", "S2", "N2"]}
TIDE_M2_AMP = float(np.hypot(*_bt["M2"]))
def lag_h(ab, nm="M2"): return ((np.arctan2(ab[1], ab[0]) - REF[nm]) % (2 * np.pi)) / (2 * np.pi * W[nm]) * 24.0
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
    sig = np.sqrt(np.mean(sur[:, 0] ** 2) / 2); dlag = float(np.degrees(min(np.pi, sig / max(A["M2"], 1e-12))) / 360 * 12.42)
    r = dict(A=A, p=p, lagM2=float(lag_h(b["M2"])), lagS2=float(lag_h(b["S2"], "S2")), dlagM2=dlag, null95=float(np.percentile(sur[:, 0], 95)), n=int(m.sum()))
    log(f"  {label:44s} n={m.sum():6d}  M2 {A['M2']:.3g}{unit} (null95 {r['null95']:.2g}, p={p['M2']:.3f}, +{r['lagM2']:.1f}±{dlag:.1f} h after HW)  "
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
    g = np.full(NH, np.nan); mm = m if sel is None else (m & sel); ii = S["hidx"][mm]; ok = (ii >= 0) & (ii < NH); g[ii[ok]] = v[mm][ok]; return g
L10 = lambda v: np.log10(np.maximum(v, 1e-30)); DB = 10.0
def band_power(S, f1, f2):
    m = (S["f36"] >= f1) & (S["f36"] <= f2); return np.log10(np.mean(10.0 ** (S["logP"][:, m].astype(np.float64) + 15.0), axis=1)) - 15.0
def js(o):
    if isinstance(o, dict): return {str(k): js(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [js(v) for v in o]
    if isinstance(o, (np.floating, np.integer)): return o.item()
    return o
