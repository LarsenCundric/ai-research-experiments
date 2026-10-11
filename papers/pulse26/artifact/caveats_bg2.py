"""Caveats add-on 2: is the envelope-locked term in the background bands a solar-S2 contamination (S2 only, no MU2 mirror; also S1/S3)
or genuine AM (S2+MU2 and N2+L2 consistent)? Sideband decomposition for raw line, bg 20-24 s, bg 29-34 s and LMB, joint block bootstrap.
All coefficients normalised by a_M = P_M2(LMB)/T_M2 so that numbers are comparable across series. Appends to caveats.txt."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import sys, numpy as np
sys.argv = [sys.argv[0]]
import robustness as RB
from tidelib import *
import tidelib as TL
TL.LOG.clear(); SER, k0, k1 = RB.SER, RB.k0, RB.k1; solve = RB.solve
WX = dict(W); WX.update({"K2": 2.0054758, "L2": 1.9685645, "MU2": 1.8645472, "NU2": 1.9008208, "2N2": 1.8596904})
EX = ["K2", "L2", "MU2", "NU2", "2N2"]
XE = np.c_[RB.XH, np.array(sum([[np.cos(2 * np.pi * WX[n] * tg_d), np.sin(2 * np.pi * WX[n] * tg_d)] for n in EX], [])).T]
IE = dict(RB.IH); IE.update({n: RB.XH.shape[1] + 2 * i for i, n in enumerate(EX)})
def cx(b, nm, k): return complex(b[IE[nm], k], -b[IE[nm] + 1, k])
bT = solve(XE, tide_g - tide_g.mean()); TT = {n: complex(bT[IE[n]], -bT[IE[n] + 1]) for n in ["M2", "S2", "N2", "L2", "MU2"]}
log("\n==== ADD-ON 2 (caveats_bg2.py): sideband test per series (raw line / bg 20-24 s / bg 29-34 s / LMB). g_X = Re[P_X/(a_M T_X)], a_M from the LMB M2 term; "
    "gamma_S = g_S2+g_MU2, gamma_N = g_N2+g_L2; 'S2 excess' = g_S2-(g_MU2+1) (solar S2 contamination -> excess != 0). Amplitudes in dB; [95% joint block-bootstrap].")
for sta, (lo, hi) in [("EDA", RB.span(SER["EDA"]["m"])), ("TAM", RB.span(SER["TAM"]["m"])), ("SACV", RB.span(SER["SACV"]["m"], k0, k1))]:
    s = SER[sta]; mm = np.zeros(NH, bool); mm[lo:hi] = s["m"][lo:hi]; ii = np.flatnonzero(mm)
    ys = [s["line"], s["b1"], s["b2"], s["y"]]; names = ["raw line", "bg 20-24 s", "bg 29-34 s", "LMB"]
    def stats_(B):
        aM = cx(B, "M2", 3) / TT["M2"]; out = []
        for k in range(4):
            gS = (cx(B, "S2", k) / (aM * TT["S2"])).real; gN = (cx(B, "N2", k) / (aM * TT["N2"])).real
            gMU = ((cx(B, "MU2", k) - (aM * TT["MU2"] if k in (0, 3) else 0)) / (aM * TT["M2"] * np.conj(TT["S2"] / TT["M2"]))).real
            gL = ((cx(B, "L2", k) - (aM * TT["L2"] if k in (0, 3) else 0)) / (aM * TT["M2"] * np.conj(TT["N2"] / TT["M2"]))).real
            out.append([abs(cx(B, "M2", k)), abs(cx(B, "S2", k)), abs(cx(B, "S1", k)), abs(cx(B, "S3", k)), gS, gMU, gN, gL, gS + gMU, gN + gL, gS - gMU - 1])
        return np.array(out)
    B = solve(XE[ii], np.array([v[ii] for v in ys]).T); o = stats_(B); DS = RB.DayStats(XE, ys, mm, lo, hi)
    BB = np.array([stats_(DS.boot(30)) for _ in range(1000)]); ci = np.percentile(BB, [2.5, 97.5], axis=0)
    log(f"  {sta} {str(np.int64(grid_t[lo]).astype('datetime64[s]'))[:7]}..{str(np.int64(grid_t[hi-1]).astype('datetime64[s]'))[:7]}:")
    lab = ["|M2|", "|S2|", "|S1|", "|S3|", "g_S2", "g_MU2", "g_N2", "g_L2", "gamma_S", "gamma_N", "S2 excess"]
    for k, n in enumerate(names):
        log(f"    {n:11s} " + "  ".join(f"{lab[j]} {o[k,j]:+.3f} [{ci[0,k,j]:+.2f},{ci[1,k,j]:+.2f}]" if j >= 4 else f"{lab[j]} {o[k,j]:.3f}" for j in range(11)))
open(os.path.join(D, "caveats.txt"), "a").write("\n".join(TL.LOG) + "\n")
