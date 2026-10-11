"""Caveats round add-on: decompose the spring-neap (envelope) term of LMB into raw line minus the regressed background bands.
For each station/window: in-phase Q (projected on the LMB M2 response phase, dB per unit e) for raw line, 20-24 s band, 29-34 s band, and LMB,
with joint 30-d day-aligned block-bootstrap CIs. Appends to caveats.txt."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import sys, numpy as np
sys.argv = [sys.argv[0]]
import robustness as RB
from tidelib import *
import tidelib as TL
TL.LOG.clear(); SER, ENV, k0, k1 = RB.SER, RB.ENV, RB.k0, RB.k1; solve = RB.solve; FULL = ENV["full"]
log("\n==== ADD-ON (caveats_bg.py): where does the LMB envelope term come from? in-phase Q (dB per unit e, projected on LMB M2 phase) = raw line - w1*bg(20-24 s) - w2*bg(29-34 s)")
for sta, (lo, hi) in [("EDA", RB.span(SER["EDA"]["m"], k0, k1)), ("TAM", RB.span(SER["TAM"]["m"], k0, k1)), ("SACV", RB.span(SER["SACV"]["m"], k0, k1)),
                      ("EDA", RB.span(SER["EDA"]["m"])), ("TAM", RB.span(SER["TAM"]["m"]))]:
    s = SER[sta]; mm = np.zeros(NH, bool); mm[lo:hi] = s["m"][lo:hi]; X, e = RB.env_design("full", mm); ii = np.flatnonzero(mm)
    ys = [s["line"], s["b1"], s["b2"], s["y"]]; names = ["raw line", "bg 20-24 s", "bg 29-34 s", "LMB"]
    G = np.c_[np.ones(len(ii)), s["b1"][ii], s["b2"][ii]]; w = np.linalg.lstsq(G, s["line"][ii], rcond=None)[0]
    B = solve(X[ii], np.array([v[ii] for v in ys]).T); P = complex(B[1, 3], -B[2, 3]); u = np.conj(P / abs(P))
    def proj(Bm): return np.array([(complex(Bm[3, k], -Bm[4, k]) * u).real for k in range(4)]), np.array([(complex(Bm[1, k], -Bm[2, k]) * u).real for k in range(4)])
    q0, p0 = proj(B); DS = RB.DayStats(X, ys, mm, lo, hi); QB = []; PB = []
    for _ in range(1000):
        a, b_ = proj(DS.boot(30)); QB.append(a); PB.append(b_)
    QB = np.array(QB); PB = np.array(PB); ci = np.percentile(QB, [2.5, 97.5], axis=0); cip = np.percentile(PB, [2.5, 97.5], axis=0)
    comb = q0[0] - w[1] * q0[1] - w[2] * q0[2]
    tag = f"{sta} {str(np.int64(grid_t[lo]).astype('datetime64[s]'))[:7]}..{str(np.int64(grid_t[hi-1]).astype('datetime64[s]'))[:7]}"
    log(f"  {tag}: " + " | ".join(f"{n}: P {p0[k]:+.3f} [{cip[0,k]:+.3f},{cip[1,k]:+.3f}], Q {q0[k]:+.3f} [{ci[0,k]:+.3f},{ci[1,k]:+.3f}]" for k, n in enumerate(names))
        + f" | weights w1 {w[1]:.2f}, w2 {w[2]:.2f}; line - w.bg = {comb:+.3f}; gamma_LMB = Q/P = {q0[3]/p0[3]:+.2f}, gamma_line = {q0[0]/p0[0]:+.2f}")
open(os.path.join(D, "caveats.txt"), "a").write("\n".join(TL.LOG) + "\n")
