"""Per-component M2 tests: 26.5 s (37.55-37.85 mHz) and 26.3 s (37.92-38.22 mHz) members of the 26 s doublet,
the 28 s line (35.55-36.15 mHz), and a between-line gap band (36.6-37.1 mHz) + 39.3-40.0 mHz as local background.
Uses per-window 3-h Hann periodograms (logP36) from features.py. Also fits a two-Gaussian model to yearly stacks."""
import os, json, numpy as np
from tidelib import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
BANDS = {"26.5 s comp (37.55-37.85 mHz)": (0.03755, 0.03785), "26.3 s comp (37.92-38.22 mHz)": (0.03792, 0.03822),
         "28 s line (35.55-36.15 mHz)": (0.03555, 0.03615), "gap 36.6-37.1 mHz": (0.0366, 0.0371), "high 39.3-40.0 mHz": (0.0393, 0.0400)}
OUT = {}
for sta in [s for s in ["EDA", "TAM", "MBAR", "SHEL", "SACV"] if os.path.exists(os.path.join(D, "features.npz" if s == "EDA" else f"features_{s}.npz"))]:
    S = load(sta); log(f"== {sta}: QC {S['qc'].sum()}"); R = {}
    bp = {k: band_power(S, *v) for k, v in BANDS.items()}
    X = {}
    for k, v in bp.items():
        X[k] = prep(hp(grid(S, v, S["qc"]))); R[k] = test(k, X[k][0], X[k][1], DB, " dB")
    bg = 0.5 * (X["gap 36.6-37.1 mHz"][0] + X["high 39.3-40.0 mHz"][0]); m = X["gap 36.6-37.1 mHz"][1]
    for k in list(BANDS)[:3]:
        y = X[k][0]; G = np.c_[np.ones(m.sum()), bg[m]]; beta = np.linalg.lstsq(G, y[m], rcond=None)[0]
        res = np.zeros(NH); res[m] = y[m] - G @ beta; res[m] -= res[m].mean()
        R[k + " minus local bg"] = test(k + " minus local bg", res, m, DB, " dB")
    d = np.zeros(NH); d[m] = X[list(BANDS)[0]][0][m] - X[list(BANDS)[1]][0][m]; d[m] -= d[m].mean()
    R["log ratio 26.5/26.3"] = test("log ratio 26.5/26.3 (differential)", d, m, DB, " dB")
    # two-Gaussian fit to yearly median spectra (in dB) -> component centre frequencies and amplitude ratio
    yr = S["t"].astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970; f = S["f36"]; sel_f = (f >= 0.0368) & (f <= 0.0392)
    g2 = lambda x, a1, f1, w1, a2, f2, w2, c0: a1 * np.exp(-0.5 * ((x - f1) / w1) ** 2) + a2 * np.exp(-0.5 * ((x - f2) / w2) ** 2) + c0
    R["yearly_fit"] = {}
    for y in np.unique(yr):
        s = S["qc"] & (yr == y)
        if s.sum() < 500: continue
        st = 10 * np.median(S["logP"][s][:, sel_f], axis=0); st = st - np.median(st)
        try:
            p, cv = curve_fit(g2, f[sel_f], st, p0=[3, 0.03770, 0.0002, 3, 0.03805, 0.0002, 0], maxfev=20000,
                              bounds=([0, 0.0373, 5e-5, 0, 0.03785, 5e-5, -10], [30, 0.03785, 6e-4, 30, 0.0384, 6e-4, 10]))
            e = np.sqrt(np.diag(cv))
            R["yearly_fit"][int(y)] = dict(T1=1 / p[1], eT1=e[1] / p[1] ** 2, A1=p[0], T2=1 / p[4], eT2=e[4] / p[4] ** 2, A2=p[3], n=int(s.sum()))
            log(f"  {sta} {y}: comp1 {1/p[1]:.3f}±{e[1]/p[1]**2:.3f} s amp {p[0]:.2f} dB width {p[2]*1e3:.3f} mHz | comp2 {1/p[4]:.3f}±{e[4]/p[4]**2:.3f} s amp {p[3]:.2f} dB width {p[5]*1e3:.3f} mHz")
        except Exception as ex:
            log(f"  {sta} {y}: fit failed {ex}")
    OUT[sta] = R
json.dump(js(OUT), open(os.path.join(D, "components.json"), "w"), indent=1)
open(os.path.join(D, "components.txt"), "w").write("\n".join(LOG) + "\n"); log("done")
