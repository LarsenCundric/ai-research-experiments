"""Follow-up to robustness.py: why does the perigean-envelope test (M2+N2 envelope) give a lower gamma than the N2 admittance?
The envelope regressor e*exp(i theta) projects equally on N2 and on its mirror sideband L2 (= 2*M2 - N2, 1.96857 cpd), where the
tidal forcing is tiny. Fit N2 and L2 (and K2) jointly with the usual constituents and compare with tidal expectations.
Moving-block (30-d, day-aligned) bootstrap. Appends to robustness_extra.txt."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import sys, numpy as np
os.environ.setdefault("NBOOT", "2000")
sys.argv = [sys.argv[0]]
import robustness as RB   # module import only builds the series (main block not executed)
from tidelib import *
W2 = dict(L2=1.9685645, K2=2.0054758)
EX = np.array(sum([[np.cos(2 * np.pi * f * tg_d), np.sin(2 * np.pi * f * tg_d)] for f in W2.values()], [])).T
XE = np.c_[RB.XH, EX]; iL, iK = RB.XH.shape[1], RB.XH.shape[1] + 2
bt = RB.solve(XE, tide_g - tide_g.mean()); T = {nm: RB.cplx(bt, RB.IH[nm]) for nm in ["M2", "N2", "S2"]}; T["L2"] = complex(bt[iL], -bt[iL + 1]); T["K2"] = complex(bt[iK], -bt[iK + 1])
out = [f"tide (Port Sonara prediction, joint fit): " + ", ".join(f"{k} {abs(v):.3f} m" for k, v in T.items())]
for sta in ["EDA", "TAM"]:
    s = RB.SER[sta]; lo, hi = RB.span(s["m"]); ii = np.arange(lo, hi); ii = ii[s["m"][ii]]
    b = RB.solve(XE[ii], s["y"][ii]); P = {nm: RB.cplx(b, RB.IH[nm]) for nm in ["M2", "N2", "S2"]}; P["L2"] = complex(b[iL], -b[iL + 1]); P["K2"] = complex(b[iK], -b[iK + 1])
    DS = RB.DayStats(XE, [s["y"]], s["m"], lo, hi); B = []
    for _ in range(int(os.environ["NBOOT"])):
        bb = DS.boot(30)[:, 0]; B.append([RB.cplx(bb, RB.IH["M2"]), RB.cplx(bb, RB.IH["N2"]), complex(bb[iL], -bb[iL + 1])])
    B = np.array(B); aM = P["M2"] / T["M2"]
    expL = abs(aM * T["L2"]); sdL = 0.5 * (B[:, 2].real.std() + B[:, 2].imag.std())
    # what the envelope estimator sees: Re[(a_N + a_L)/(r a_M)], r = T_N/T_M (complex)
    r = T["N2"] / T["M2"]; gN = ((P["N2"]) / (r * P["M2"])).real; gL = ((P["L2"]) / (r * P["M2"])).real
    gNb = (B[:, 1] / (r * B[:, 0])).real; gLb = (B[:, 2] / (r * B[:, 0])).real
    out.append(f"{sta}: L2 response {abs(P['L2']):.3f} dB (bootstrap s.d. per component {sdL:.3f} dB; expected if proportional {expL:.3f} dB); "
               f"envelope-gamma decomposition: N2 part {gN:+.2f} [{np.percentile(gNb,2.5):+.2f},{np.percentile(gNb,97.5):+.2f}], L2 part {gL:+.2f} [{np.percentile(gLb,2.5):+.2f},{np.percentile(gLb,97.5):+.2f}], "
               f"sum {gN+gL:+.2f} (cf. M2+N2 envelope gamma in robustness.txt)")
txt = "\n== springneap_L2.py ==\n" + "\n".join(out) + "\n"; print(txt); open(os.path.join(D, "robustness_extra.txt"), "a").write(txt)
