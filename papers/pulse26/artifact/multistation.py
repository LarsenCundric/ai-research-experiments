"""Multi-station check of the source-side M2 phase of the 26 s line: EDA (Cameroon, ~240 km from 4N 8E), TAM (Algeria, N, 2100 km),
MBAR (Uganda, E, inland, ~2500 km), SHEL (St Helena, SSW, ocean island ~2700 km; its own local tide differs).
Common period 2022-03..2024-02 for all stations (plus full spans). Fixed-band line PSD, line minus 20-24/29-34 s background."""
import os, json, numpy as np
from tidelib import *
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
c0 = np.datetime64("2022-03-01T00:00", "s").astype(np.int64); c1 = np.datetime64("2024-03-01T00:00", "s").astype(np.int64)
OUT = {}; ph = {}
for sta in ["EDA", "TAM", "MBAR", "SHEL", "SACV"]:
    if not os.path.exists(os.path.join(D, "features.npz" if sta == "EDA" else f"features_{sta}.npz")): continue
    S = load(sta); sel = (S["t"] >= c0) & (S["t"] < c1); c = S["c"]
    log(f"== {sta} common period 2022-03..2024-02: QC {int((S['qc']&sel).sum())}, detected {int((S['det']&sel).sum())} ({(S['det']&sel).sum()/max(1,(S['qc']&sel).sum()):.1%})")
    R = {}
    y, m = prep(hp(grid(S, L10(c["fixband"]), S["qc"], sel))); R["fixband"] = test("26 s line PSD (fixed band)", y, m, DB, " dB")
    b1, _ = prep(hp(grid(S, L10(c["bg_2024"]), S["qc"], sel))); b2, _ = prep(hp(grid(S, L10(c["bg_2834"]), S["qc"], sel)))
    R["bg_2024"] = test("background 20-24 s", b1, m, DB, " dB"); R["bg_2834"] = test("background 29-34 s", b2, m, DB, " dB")
    G = np.c_[np.ones(m.sum()), b1[m], b2[m]]; beta = np.linalg.lstsq(G, y[m], rcond=None)[0]; res = np.zeros(NH); res[m] = y[m] - G @ beta; res[m] -= res[m].mean()
    R["line_minus_bg"] = test("line minus background (regressed)", res, m, DB, " dB")
    bb = fit(y, m); R["M4_fixband_dB"] = float(np.hypot(*bb["M4"]) * DB)
    log(f"  M4 term in line PSD: {R['M4_fixband_dB']:.3f} dB")
    OUT[sta] = R; ph[sta] = R["line_minus_bg"]
lags = {k: (v["lagM2"], v["dlagM2"], v["A"]["M2"], v["p"]["M2"]) for k, v in ph.items()}
log("M2 lag after Limbe HW (line minus background), common period: " + "; ".join(f"{k} {a:.2f}±{b:.2f} h ({c:.2f} dB, p={p:.2f})" for k, (a, b, c, p) in lags.items()))
fig = plt.figure(figsize=(5.5, 5.5)); ax = fig.add_subplot(111, projection="polar")
for k, (lg, dl, A, p) in lags.items():
    th = lg / 12.42 * 2 * np.pi; ax.errorbar(th, A, xerr=dl / 12.42 * 2 * np.pi, fmt="o", capsize=3, label=f"{k} (p={p:.2f})")
ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False)); ax.set_xticklabels([f"{h:.0f}h" for h in np.linspace(0, 12.42, 12, endpoint=False)])
ax.set_title("M2 modulation of 26 s line (minus background), 2022-03..2024-02\nangle = lag after M2 HW at Limbe, radius = amplitude (dB)", fontsize=9)
ax.legend(fontsize=7, loc="lower left", bbox_to_anchor=(-0.15, -0.15)); fig.tight_layout(); fig.savefig(os.path.join(D, "fig8_multistation_M2_phasors.png"), dpi=120)
json.dump(js(OUT), open(os.path.join(D, "multistation.json"), "w"), indent=1)
open(os.path.join(D, "multistation.txt"), "w").write("\n".join(LOG) + "\n"); log("done")
