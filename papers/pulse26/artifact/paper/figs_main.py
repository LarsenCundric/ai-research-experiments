"""Main-text Figures 2 and 4 for the paper (clean versions). Fig 2 recomputed from the robustness.py series (LMB metric);
Fig 4 plotted from numbers already in robustness.txt (5-bin spring-neap test) and model.txt (toy model, 26 s swell)."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import sys, re, numpy as np
sys.argv = [sys.argv[0]]
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P); os.chdir(P)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
F = os.path.join(P, "paper", "figs")
# ---------------- Fig 4 (from text results; no recomputation) ----------------
txt = open("robustness.txt").read()
def bins(sta):
    m = re.search(sta + r"\s+full\s+5 bins: E_k\(m\)=([\d.,]+) \| in-phase A_k\(dB\)=([\d.,±]+) \|", txt)
    E = np.array(m.group(1).split(","), float); A = np.array([v.split("±") for v in m.group(2).split(",")], float); return E, A[:, 0], A[:, 1]
mt = open("model.txt").read().split("-- swell period 26 s")[1].split("-- wave-current")[0]
rows = [l.split() for l in mt.strip().splitlines()[1:]]
rows = [[float(x) for x in r if x != "|"] for r in rows]; M = np.array(rows)
fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
a = ax[0]
for sta, col, off in [("EDA", "k", -0.004), ("TAM", "C1", 0.004)]:
    E, A, s = bins(sta); a.errorbar(E + off, A, yerr=1.96 * s, fmt="o", color=col, capsize=3, label=f"{sta} (full span)")
    k = np.sum(A * E / s ** 2) / np.sum(E ** 2 / s ** 2); xx = np.linspace(0, 0.9, 10); a.plot(xx, k * xx, color=col, lw=0.8, ls="--")
a.set_xlim(0, 0.9); a.set_ylim(0, 0.8); a.set_xlabel("semidiurnal tidal envelope in bin (m)"); a.set_ylabel("in-phase M2-band response (dB)")
a.legend(fontsize=8, loc="upper left"); a.set_title("(a) Spring-neap scaling (dashed: proportional)", fontsize=9.5, loc="left")
a = ax[1]; labs = ["bottom pressure", "bed orbital velocity", r"primary coupling, $F_B\propto k^{-2}$", r"primary coupling, $F_B\propto k^{-3}$", "depth-limited (breaking)"]
for j, (lab, col) in enumerate(zip(labs, ["C0", "C1", "C2", "C3", "C4"])): a.plot(M[:, 0], M[:, j + 1], "o-", ms=3, color=col, label=lab)
a.axhspan(0.40, 0.55, color="C3", alpha=0.18, label="observed (0.40-0.55 dB)"); a.axhline(0, color="k", lw=0.6)
a.set_xscale("log"); a.set_xlabel("mean water depth at the coupling site (m)"); a.set_ylabel("predicted M2 modulation (dB; + = max at HW)")
a.set_ylim(-1.5, 1.9); a.legend(fontsize=7, loc="upper right"); a.set_title("(b) Linear depth-modulation toy model, 26 s swell", fontsize=9.5, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(F, "fig4_springneap_model.png"), dpi=220); plt.close(fig)
print("fig4 done", flush=True)
# ---------------- Fig 2 (recomputed from the LMB series) ----------------
import robustness as RB
from tidelib import surrogates, tg_d, W, NH
SER = RB.SER; TC = RB.TC
fig = plt.figure(figsize=(10, 6.2)); gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1])
for i, sta in enumerate(["EDA", "TAM"]):
    s = SER[sta]; x, m = s["y"].copy(), s["m"]; lo, hi = RB.span(m); xs, ms = x[lo:hi], m[lo:hi]
    f = np.fft.rfftfreq(len(xs), 1 / 24.0); band = (f > 1.85) & (f < 2.05)
    Pw = np.abs(np.fft.rfft(xs)) ** 2; norm = np.median(Pw[band]); mx = []
    for y in surrogates(xs, ms, 200): mx.append((np.abs(np.fft.rfft(y)) ** 2)[band].max() / norm)
    a = fig.add_subplot(gs[i, 0]); a.plot(f[band], Pw[band] / norm, color="k", lw=0.6)
    a.axhline(np.percentile(mx, 95), color="C0", ls="--", lw=0.9, label="95% band-max (phase-randomised surrogates)")
    a.axhline(np.percentile(mx, 99), color="C0", ls=":", lw=0.9, label="99% band-max")
    for nm, fq in [("N2", W["N2"]), ("M2", W["M2"]), ("S2", W["S2"])]: a.axvline(fq, color="C3" if nm != "S2" else "C1", lw=0.5, alpha=0.6); a.text(fq, a.get_ylim()[1] * 0.92, nm, fontsize=8, ha="center", color="C3" if nm != "S2" else "C1")
    a.set_xlim(1.85, 2.05); a.set_ylabel("power / band median"); a.set_title(f"({'ab'[i]}) {sta}: periodogram of line-minus-background power", fontsize=9.5, loc="left")
    if i == 0: a.legend(fontsize=7, loc="center right")
    else: a.set_xlabel("frequency (cycles per day)")
    print(sta, "M2 peak / median", float((Pw[band] / norm).max()), "95% band-max", float(np.percentile(mx, 95)), flush=True)
a = fig.add_subplot(gs[:, 1]); wm2 = 2 * np.pi * W["M2"]
ph = ((wm2 * tg_d + np.angle(TC["M2"])) % (2 * np.pi)) / (2 * np.pi) * 12.42   # hours after M2 HW at Port Sonara
edges = np.linspace(0, 12.42, 13); cen = (edges[:-1] + edges[1:]) / 2
for sta, key, col, ls, lab in [("EDA", "y", "k", "-", "EDA line - bg"), ("TAM", "y", "C1", "-", "TAM line - bg"), ("SACV", "y", "C6", "-", "SACV line - bg (2022-24)"),
                               ("EDA", "b1", "0.5", ":", "EDA bg 20-24 s"), ("EDA", "b2", "0.5", "--", "EDA bg 29-34 s")]:
    s = SER[sta]; m = s["m"]; v = s[key]; mu, se = [], []
    for k in range(12):
        sel = m & (ph >= edges[k]) & (ph < edges[k + 1]); vv = v[sel]; mu.append(vv.mean()); se.append(vv.std() / np.sqrt(sel.sum() / 3))
    mu = np.array(mu) - np.mean(mu)
    a.errorbar(cen, mu, yerr=se if key == "y" else None, color=col, ls=ls, marker="o" if key == "y" else None, ms=3, capsize=2, label=lab)
a.axvline(0, color="C0", lw=0.6); a.set_xlim(0, 12.42); a.set_xlabel("hours after M2 high water (Port Sonara)"); a.set_ylabel("power anomaly (dB)")
a.legend(fontsize=7, loc="lower left"); a.set_title("(c) Binned by M2 phase (±1 SE, n/3)", fontsize=9.5, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(F, "fig2_tidal_periodogram_phase.png"), dpi=220); plt.close(fig)
print("fig2 done", flush=True)
