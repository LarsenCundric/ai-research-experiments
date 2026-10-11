"""Caveats round (10 Oct 2026): diagnose the three spring-neap caveats from robustness.py.
 Caveat 1: gamma strong in long EDA/TAM records, weak in the 2022-24 window, negative at SACV.
 Caveat 2: gamma < 1 (sub-proportional).
 Caveat 3: lunar-only (perigean) envelope gamma low at EDA; traced to an L2 term.
Framework (amplitude-modulation, AM): if the M2-band response amplitude scales as E^gamma, with E the semidiurnal envelope,
then for a tidal sideband X (S2, N2) with r = T_X/T_M, the response has a main term P_X = a_M T_X (1+gamma)/2 and a MIRROR term at
2*w_M - w_X (MU2 = 2MS2 for S2; L2 = 2MN2 for N2) equal to a_M T_M conj(r) (gamma-1)/2 (plus the tide-following part a_M T_mirror).
So g_X = Re[P_X/(a_M T_X)] = (1+gamma)/2, g_mir = Re[(P_mir - a_M T_mir)/(a_M T_M conj r)] = (gamma-1)/2 and the envelope
regression estimates gamma = g_X + g_mir. Consistency g_mir = g_X - 1 is a test of the AM picture vs a fluke/additive line.
Metric: line minus background (LMB, all QC hours = continuous power metric, not detected-only). Same nulls/bootstrap helpers as robustness.py.
Outputs: caveats.txt, caveats.json, fig12_caveat1.png, fig13_caveat2.png, fig14_caveat3.png."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import sys, json, time, numpy as np
sys.argv = [sys.argv[0]]
import robustness as RB
from tidelib import *
import tidelib as TL
import utide
from scipy import stats, optimize
from scipy.signal import hilbert
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
TL.LOG.clear(); R = RB.R; OUT = {}; t0 = time.time()
NBS = int(os.environ.get("NBOOT", 500)); NSIM = int(os.environ.get("NSIM", 300)); NSUR = int(os.environ.get("NSUR", 1000))
TXT = os.path.join(D, "caveats.txt")
def flush(): open(TXT, "w").write("\n".join(TL.LOG) + "\n")
def el(): return f"[{(time.time()-t0)/60:.1f} min]"
solve, cplx, IH, XH, WM2 = RB.solve, RB.cplx, RB.IH, RB.XH, RB.WM2
SER, ENV, k0, k1 = RB.SER, RB.ENV, RB.k0, RB.k1
EQ = {"M2": 0.90812, "S2": 0.42286, "N2": 0.17387, "K2": 0.11506, "NU2": 0.03303, "MU2": 0.02776, "L2": 0.02567, "2N2": 0.02301}   # Doodson/Cartwright
WX = dict(W); WX.update({"K2": 2.0054758, "L2": 1.9685645, "MU2": 1.8645472, "NU2": 1.9008208, "2N2": 1.8596904})
EXTRA_C = ["K2", "L2", "MU2", "NU2", "2N2"]
def hc(nms): return sum([[np.cos(2 * np.pi * WX[n] * tg_d), np.sin(2 * np.pi * WX[n] * tg_d)] for n in nms], [])
XE = np.c_[XH, np.array(sum([[np.cos(2 * np.pi * WX[n] * tg_d), np.sin(2 * np.pi * WX[n] * tg_d)] for n in EXTRA_C], [])).T]
IE = dict(IH); IE.update({n: XH.shape[1] + 2 * i for i, n in enumerate(EXTRA_C)})
def cx(b, nm): return complex(b[IE[nm]], -b[IE[nm] + 1])
bT = solve(XE, tide_g - tide_g.mean()); TT = {n: cx(bT, n) for n in ["M2", "S2", "N2"] + EXTRA_C}
def zcx(nm): return TT[nm] * np.exp(1j * 2 * np.pi * WX[nm] * tg_d)
sm25 = RB.sm25
def env_of(h):
    Z = np.fft.rfft(h - h.mean()); fz = np.fft.rfftfreq(len(h), 1 / 24.0); z = hilbert(np.fft.irfft(Z * ((fz > 1.5) & (fz < 2.5)), len(h)))
    return dict(E=sm25(np.abs(z)), th=np.angle(z), z=z)
def envX(E, th, mm, extra=(), ctrl=()):
    e = E / E[mm].mean() - 1; c_, s_ = np.cos(th), np.sin(th)
    cols = [np.ones(NH), c_, s_, e * c_, e * s_] + RB.NUIS + [np.cos(2 * th), np.sin(2 * th)] + hc(extra)
    for v in ctrl: cols += [v * c_, v * s_]
    return np.array(cols).T.copy()
def win(m, lo, hi): mm = np.zeros(NH, bool); mm[lo:hi] = m[lo:hi]; return mm
def gam(y, m, lo, hi, env, extra=(), nb=NBS, ctrl=()):
    mm = win(m, lo, hi); X = envX(env["E"], env["th"], mm, extra, ctrl); ii = np.flatnonzero(mm); b = solve(X[ii], y[ii]); g, gq, P = RB.gamma_of(b)
    r = dict(gamma=float(g), quad=float(gq), A=abs(P), n=int(len(ii)))
    if nb:
        DS = RB.DayStats(X, [y], mm, lo, hi); gb = np.array([RB.gamma_of(DS.boot(30)[:, 0])[0] for _ in range(nb)])
        r.update(sd=float(gb.std()), ci=[float(v) for v in np.percentile(gb, [2.5, 97.5])])
    return r
def fmt(r): return f"gamma {r['gamma']:+.2f}" + (f" [{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}]" if "ci" in r else "") + f" (A {r['A']:.3f} dB, n {r['n']})"
SP = {s: RB.span(SER[s]["m"]) for s in SER}; CW = {s: RB.span(SER[s]["m"], k0, k1) for s in SER}
FULL = ENV["full"]
# =================== A. tide-side facts ===================
log(f"==== A. TIDE GAUGES (UTide, despiked; 25-h running median removed) {el()}")
def read_gauge(fn):
    d = np.genfromtxt(os.path.join(D, "tide", fn), delimiter=",", skip_header=2, dtype=None, encoding=None)
    t = np.array([np.datetime64(r[0].replace("Z", "")) for r in d]).astype("datetime64[h]"); h = np.array([float(r[1]) for r in d]) / 1000; h[h < -9] = np.nan
    th = np.arange(t.min(), t.max() + np.timedelta64(1, "h"), np.timedelta64(1, "h")); hh = np.full(len(th), np.nan); hh[(t - t.min()).astype(int)] = h
    from numpy.lib.stride_tricks import sliding_window_view as swv
    p = np.pad(hh, 12, constant_values=np.nan)
    with np.errstate(all="ignore"): rm = np.nanmedian(swv(p, 25), axis=1)
    r = hh - rm; mad = np.nanmedian(np.abs(r - np.nanmedian(r))) * 1.4826; r[np.abs(r - np.nanmedian(r)) > 5 * mad] = np.nan
    ok = np.isfinite(r); return th[ok], r[ok]
GAUGES = {"Port Sonara": ("port_sonara_global_hourly_rqds.csv", 4.007), "Sao Tome": ("sao_tome_rqds.csv", 0.35), "Lagos": ("lagos_rqds.csv", 6.42), "Praia (SACV island)": ("praia_rqds.csv", 14.91)}
GC = {}; GPRED = {}
tgrid = grid_t.astype(np.int64).astype("datetime64[s]")
for name, (fn, lat) in GAUGES.items():
    t_, h_ = read_gauge(fn)
    co = utide.solve(t_, h_, lat=lat, method="ols", conf_int="none", verbose=False, trend=False)
    i = {n: k for k, n in enumerate(co.name)}; A = {n: (float(co.A[i[n]]) if n in i else np.nan) for n in EQ}
    GC[name] = A
    rr = [f"{n}/M2 {A[n]/A['M2']:.3f} (eq {EQ[n]/EQ['M2']:.3f})" for n in ["S2", "N2", "K2", "L2", "MU2", "NU2", "2N2"]]
    log(f"  {name:20s} {str(t_[0])[:10]}..{str(t_[-1])[:10]} n={len(t_)}: M2 {A['M2']:.3f} m; " + "; ".join(rr))
    GPRED[name] = utide.reconstruct(tgrid, co, verbose=False).h
    GPRED[name] = GPRED[name] - np.nanmean(GPRED[name])
OUT["gauges"] = GC
log(f"  Port Sonara prediction used in all analyses (joint fit on 2019-26 grid): " + ", ".join(f"{n} {abs(v):.4f} m" for n, v in TT.items()))
log("  NOTE: Port Sonara observations cover only 2008-06..2011-06 (RQ and fast files identical) -> no observed gauge envelope overlaps the seismic data;"
    " all envelopes are harmonic predictions (gauge constants + UTide nodal corrections).")
GENV = {n: env_of(v) for n, v in GPRED.items()}; GENV["Port Sonara (pipeline)"] = FULL
flush()
# =================== caveat 2(a) + 1(c) prerequisites: noise-free synthetic tests ===================
log(f"\n==== B. NOISE-FREE SYNTHETIC TESTS OF THE gamma ESTIMATOR (EDA mask, Limbe envelope model) {el()}")
mE = SER["EDA"]["m"]; loE, hiE = SP["EDA"]; PHI = 1.7 * WM2
def syn_gamma(ysyn, env=FULL, m=mE, lo=loE, hi=hiE, extra=()):
    return gam(ysyn, m, lo, hi, env, extra, nb=0)["gamma"]
zL = FULL["z"] if "z" in FULL else None
Zt = np.fft.rfft(tide_g); fz = np.fft.rfftfreq(NH, 1 / 24.0); zsd = hilbert(np.fft.irfft(Zt * ((fz > 1.5) & (fz < 2.5)), NH))
def scale05(y): return 0.5 * y / np.abs(zsd).mean()
EIV = {}
variants = {"Limbe itself (control)": zsd,
            "Limbe, S2 x0.8": zsd - 0.2 * zcx("S2"), "Limbe, S2 x1.2": zsd + 0.2 * zcx("S2"),
            "Limbe, N2 x0.8": zsd - 0.2 * zcx("N2"),
            "Limbe envelope delayed 12 h": np.roll(np.abs(zsd), 12) * np.exp(1j * np.angle(zsd)),
            "Limbe envelope delayed 24 h": np.roll(np.abs(zsd), 24) * np.exp(1j * np.angle(zsd)),
            "Limbe envelope delayed 48 h": np.roll(np.abs(zsd), 48) * np.exp(1j * np.angle(zsd))}
for n in ["Sao Tome", "Lagos"]: variants[f"{n} tide (true site)"] = GENV[n]["z"]
for k, z in variants.items():
    EIV[k] = syn_gamma(scale05((z * np.exp(-1j * PHI)).real))
    log(f"  true response proportional to [{k:30s}] -> gamma estimated with Limbe envelope = {EIV[k]:.3f}")
OUT["eiv_attenuation"] = EIV
# log/linear and nonlinear transforms of the tide: what gamma (and M4/M2) do they predict?
hm = (zsd * np.exp(-1j * PHI)).real; hraw = tide_g - tide_g.mean()
hraw_l = np.roll(hraw, 2)   # ~1.7-2 h lag
u = np.gradient(hraw_l)
TR = {}
def tr_report(name, ysyn):
    g = syn_gamma(ysyn); ii = np.flatnonzero(mE); b = solve(XH[ii], ysyn[ii]); m2 = abs(cplx(b, IH["M2"])); m4 = abs(cplx(b, IH["M4"]))
    TR[name] = (g, m4 / m2); log(f"  {name:58s} gamma {g:+.2f}   M4/M2 {m4/m2:.3f}")
kap = 0.5 / (10 / np.log(10) * np.abs(zsd).mean())
_ii = np.flatnonzero(mE); _b = solve(XH[_ii], SER["EDA"]["y"][_ii]); _bt_ = solve(XH, tide_g - tide_g.mean())
OBS_M4 = abs(cplx(_b, IH["M4"])) / abs(cplx(_b, IH["M2"])); TIDE_M4 = abs(cplx(_bt_, IH["M4"])) / abs(cplx(_bt_, IH["M2"]))
log(f"  -- transforms of tide height h (lagged 2 h). Observed EDA full span: gamma 0.70 [0.41,0.99] (robustness.txt), M4/M2 {OBS_M4:.3f}; Port Sonara tide itself M4/M2 {TIDE_M4:.3f}")
tr_report("linear in log power: dB = k*h", 10 * kap / np.log(10) * hraw_l)
for dbamp in [0.5, 1.5, 3.0]:
    kk = kap * dbamp / 0.5; tr_report(f"linear in power: dB = 10log10(1+k h), {dbamp} dB at mean range", 10 * np.log10(np.maximum(1 + kk * hraw_l, 1e-3)))
tr_report("current-like, linear: u = dh/dt", u)
tr_report("quadratic friction: u|u|", u * np.abs(u))
for h0 in [0.3, 0.6, 1.0]: tr_report(f"symmetric saturation: tanh(h/{h0} m)", np.tanh(hraw_l / h0))
for hc_ in [0.2, 0.4]: tr_report(f"one-sided clipping at high water: min(h, {hc_} m)", np.minimum(hraw_l, hc_))
for hc_ in [-0.2, 0.0]: tr_report(f"one-sided threshold: max(h - ({hc_}) m, 0)", np.maximum(hraw_l - hc_, 0))
tr_report("depth-limited power ~ (D+h)^2, D=5 m, in dB", 20 * np.log10(5 + hraw_l))
OUT["transforms"] = TR
flush()
# =================== CAVEAT 1 ===================
log(f"\n==== CAVEAT 1: gamma in short windows / SACV {el()}")
# (a) power analysis by injection: gamma_true in {0.7, 1.0}, residual moved in random-start 15-d blocks
def power_sim(sta, lo, hi, gts=(0.7, 1.0), nsim=NSIM):
    s = SER[sta]; mm = win(s["m"], lo, hi); X = envX(FULL["E"], FULL["th"], mm); ii = np.flatnonzero(mm); b = solve(X[ii], s["y"][ii])
    res = np.zeros(NH); res[ii] = s["y"][ii] - X[ii] @ b; out = {}
    for gt in gts:
        bh = b.copy(); bh[3:5] = gt * b[1:3]; yh = X @ bh; gs = []
        for _ in range(nsim):
            idx = RB.bidx(lo, hi, 360); mb = mm[idx]; dest = np.arange(lo, hi)[mb]; gs.append(RB.gamma_of(solve(X[dest], yh[dest] + res[idx][mb]))[0])
        out[gt] = np.array(gs)
    return RB.gamma_of(b)[0], out
PW = {}
for lab, sta, (lo, hi) in [("EDA 2019-26", "EDA", SP["EDA"]), ("EDA 2022-24", "EDA", CW["EDA"]), ("TAM 2022-26", "TAM", SP["TAM"]), ("TAM 2022-24", "TAM", CW["TAM"]), ("SACV 2022-24", "SACV", CW["SACV"])]:
    g0, sims = power_sim(sta, lo, hi); PW[lab] = dict(gobs=float(g0))
    for gt, gs in sims.items():
        sd = gs.std(); PW[lab][gt] = dict(mean=float(gs.mean()), sd=float(sd), p_le_obs=float(np.mean(gs <= g0)), power_excl0=float(np.mean(gs > 1.96 * sd)))
    log(f"  {lab:13s} observed gamma {g0:+.2f} | if true 0.7: mean {PW[lab][0.7]['mean']:.2f} sd {PW[lab][0.7]['sd']:.2f}, P(gamma_hat<=obs) {PW[lab][0.7]['p_le_obs']:.3f}, "
        f"P(CI excludes 0) {PW[lab][0.7]['power_excl0']:.2f} | if true 1.0: sd {PW[lab][1.0]['sd']:.2f}, P(<=obs) {PW[lab][1.0]['p_le_obs']:.3f}, P(excl 0) {PW[lab][1.0]['power_excl0']:.2f}")
OUT["power"] = PW; flush()
# (b)+(c) rolling windows: gamma, M2 amplitude, detection, coverage, and the noise-free gamma of a proportional synthetic (nodal/perigee mix)
log(f"  -- rolling 2-yr windows (3-month step) and calendar years {el()}")
ysyn_prop = scale05(hm)
ROLL = {}
for sta in ["EDA", "TAM"]:
    s = SER[sta]; lo0, hi0 = SP[sta]; rows = []
    y0_ = int(str(grid_t[lo0].astype(np.int64).astype("datetime64[s]"))[:4]); y1_ = int(str(grid_t[hi0 - 1].astype(np.int64).astype("datetime64[s]"))[:4])
    WINS = [(st, st + 17520, "2yr") for st in range(lo0, hi0 - 17520 + 1, 2184)]
    WINS += [(int((np.datetime64(f"{y}-01-01T00:00", "s").astype(np.int64) - T0) // 3600), int((np.datetime64(f"{y+1}-01-01T00:00", "s").astype(np.int64) - T0) // 3600), "1yr") for y in range(y0_, y1_ + 1)]
    for st, en, tag in WINS:
        if True:
            lo, hi = max(st, 0), min(en, NH); mm = win(s["m"], lo, hi)
            if mm.sum() >= (6000 if tag == "2yr" else 2500):
                r = gam(s["y"], s["m"], lo, hi, FULL, nb=300); rms = gam(s["y"], s["m"], lo, hi, ENV["M2+S2"], ("N2",), nb=0)
                ii = np.flatnonzero(mm); b = solve(XH[ii], s["y"][ii]); m2 = abs(cplx(b, IH["M2"]))
                gs = gam(ysyn_prop, s["m"], lo, hi, FULL, nb=0)["gamma"]; esd = float((FULL["E"][mm] / FULL["E"][mm].mean() - 1).std())
                tm = (grid_t[lo] + grid_t[min(hi, NH) - 1]) / 2
                rows.append(dict(tag=tag, start=str(grid_t[lo].astype(np.int64).astype("datetime64[s]"))[:7], end=str(grid_t[min(hi, NH) - 1].astype(np.int64).astype("datetime64[s]"))[:7], tmid=float(tm),
                                 gamma=r["gamma"], sd=r["sd"], gMS=rms["gamma"], M2=m2, cover=float(mm.sum() / (hi - lo)), det=float(np.nanmean(s["det"][mm])), gsyn=gs, esd=esd,
                                 Mtide=abs(cplx(solve(XH[lo:hi], tide_g[lo:hi] - tide_g[lo:hi].mean()), IH["M2"]))))
                q = rows[-1]
                log(f"  {sta} {tag} {q['start']}..{q['end']}: gamma {q['gamma']:+.2f}±{q['sd']:.2f} (M2+S2 env {q['gMS']:+.2f}); M2 {q['M2']:.3f} dB; coverage {q['cover']:.2f}; det {q['det']:.3f}; "
                    f"envelope sd {q['esd']:.3f}; tide M2 {q['Mtide']:.3f} m; noise-free proportional synthetic -> gamma {q['gsyn']:.3f}")
    ROLL[sta] = rows
OUT["rolling"] = ROLL
# heterogeneity of 2-yr gammas vs their sd (are windows consistent with one gamma?) using non-overlapping windows
for sta in ROLL:
    yrs = [q for q in ROLL[sta] if q["tag"] == "1yr"]
    if len(yrs) >= 2:
        g = np.array([q["gamma"] for q in yrs]); sd = np.array([q["sd"] for q in yrs]); w = 1 / sd ** 2; gm = (w * g).sum() / w.sum(); Q = float((w * (g - gm) ** 2).sum())
        log(f"  {sta}: calendar-year gammas " + ", ".join(f"{q['start'][:4]} {q['gamma']:+.2f}±{q['sd']:.2f}" for q in yrs) + f"; weighted mean {gm:+.2f}; heterogeneity Q={Q:.1f} on {len(yrs)-1} dof, p={stats.chi2.sf(Q, len(yrs)-1):.2f}")
        OUT[f"het_{sta}"] = dict(Q=Q, dof=len(yrs) - 1, p=float(stats.chi2.sf(Q, len(yrs) - 1)), mean=float(gm))
# split EDA: 2019-24 vs 2025-26 (doublet switch / amplitude drop)
c25 = int((np.datetime64("2025-01-01T00:00", "s").astype(np.int64) - T0) // 3600)
for lab, (lo, hi) in [("EDA 2019-05..2024-12", (SP["EDA"][0], c25)), ("EDA 2025-01..2026-09", (c25, SP["EDA"][1])), ("TAM 2022-03..2024-12", (SP["TAM"][0], c25)), ("TAM 2025-01..2026-09", (c25, SP["TAM"][1]))]:
    sta = lab[:3]; r = gam(SER[sta]["y"], SER[sta]["m"], lo, hi, FULL); OUT[f"split {lab}"] = r; log(f"  {lab}: {fmt(r)}")
flush()
# joint bootstrap correlation of gamma between stations (2022-24) -> is the low common-window gamma a shared source fluctuation?
log(f"  -- joint (same-block) bootstrap of gamma, 2022-03..2024-02 {el()}")
JS = ["EDA", "TAM", "SACV"]; DSJ = {}; gobs = {}
for sta in JS:
    s = SER[sta]; mm = win(s["m"], k0, k1); X = envX(FULL["E"], FULL["th"], mm); ii = np.flatnonzero(mm); gobs[sta] = RB.gamma_of(solve(X[ii], s["y"][ii]))[0]
    DSJ[sta] = RB.DayStats(X, [s["y"]], mm, k0, k1)
GB = {s: [] for s in JS}
for _ in range(1000):
    st_ = R.bit_generator.state
    for sta in JS: R.bit_generator.state = st_; GB[sta].append(RB.gamma_of(DSJ[sta].boot(30)[:, 0])[0])
GB = {k: np.array(v) for k, v in GB.items()}
C = np.corrcoef(np.array([GB[s] for s in JS]))
log("  bootstrap correlation of gamma estimates: " + ", ".join(f"{JS[i]}-{JS[j]} {C[i,j]:+.2f}" for i in range(3) for j in range(i + 1, 3)))
for a, b_ in [("SACV", "TAM"), ("SACV", "EDA"), ("TAM", "EDA")]:
    d = GB[a] - GB[b_]; log(f"  gamma difference {a}-{b_}: {gobs[a]-gobs[b_]:+.2f}, joint-bootstrap 95% [{np.percentile(d, 2.5):+.2f},{np.percentile(d, 97.5):+.2f}], P(diff>=0) {np.mean(d >= 0):.3f}")
cm = np.flatnonzero(win(SER["EDA"]["m"], k0, k1) & win(SER["TAM"]["m"], k0, k1) & win(SER["SACV"]["m"], k0, k1))
rc = np.corrcoef(np.array([SER[s]["y"][cm] for s in JS]))
log(f"  hourly LMB correlation (72-h high-passed, common hours n={len(cm)}): EDA-TAM {rc[0,1]:+.2f}, EDA-SACV {rc[0,2]:+.2f}, TAM-SACV {rc[1,2]:+.2f}")
OUT["joint_gamma_corr"] = C.tolist(); flush()
# (d)/(e) SACV and far-station metric checks
log(f"  -- SACV-specific checks and far-station metric comparison {el()}")
LS = {}
for sta in ["EDA", "TAM", "MBAR", "SHEL", "SACV"]:
    S = load(sta); v, _ = prep(hp(grid(S, L10(S["c"]["snr_w"]), S["qc"]))); LS[sta] = v * DB; del S
for sta in ["EDA", "TAM", "MBAR", "SHEL", "SACV"]:
    lo, hi = CW[sta]; s = SER[sta]; parts = []
    for nm, yv in [("LMB", s["y"]), ("raw line PSD (no bg regression)", s["line"]), ("log SNR", LS[sta])]:
        r = gam(yv, s["m"], lo, hi, FULL, nb=300); parts.append(f"{nm}: {fmt(r)}"); OUT[f"metric {sta} {nm}"] = r
    log(f"  {sta} 2022-24 | " + " | ".join(parts))
s = SER["SACV"]; lo, hi = CW["SACV"]; mm = win(s["m"], lo, hi); uu = s["u"]
med = np.nanmedian(uu[mm]); t3 = np.nanpercentile(uu[mm], 66.7)
for lab, sel in [("all QC hours (as in robustness)", s["m"]), ("slow line SNR above median", s["m"] & (uu > med)), ("slow line SNR top tercile", s["m"] & (uu > t3)),
                 ("slow line SNR below median", s["m"] & (uu <= med)), ("detected-only hours", s["m"] & (s["det"] == 1))]:
    if win(sel, lo, hi).sum() < 800: log(f"  SACV {lab}: too few hours"); continue
    r = gam(s["y"], sel, lo, hi, FULL, nb=300); OUT[f"SACV {lab}"] = r; log(f"  SACV {lab:34s}: {fmt(r)}")
# local tide (Praia, same island) and local swell (ERA5 15N 23.5W)
r = gam(s["y"], s["m"], lo, hi, GENV["Praia (SACV island)"], nb=300); OUT["SACV praia env"] = r; log(f"  SACV with Praia (local) tide envelope/phase: {fmt(r)}")
zP = GENV["Praia (SACV island)"]["z"]; dphi = np.angle(np.mean(zP * np.conj(zsd))); log(f"  Praia semidiurnal HW relative to Limbe: {(-dphi)/WM2:+.2f} h (phase of mean zP*conj(zL)); envelope corr {np.corrcoef(GENV['Praia (SACV island)']['E'], FULL['E'])[0,1]:.3f}")
E5 = json.load(open(os.path.join(D, "meta/era5_ocean_15N23.5W.json")))["hourly"]
et = np.array([np.datetime64(x) for x in E5["time"]]).astype("datetime64[s]").astype(np.int64); hs5 = np.array([np.nan if v is None else v for v in E5["wave_height"]], float)
hsc = np.full(NH, np.nan); kk_ = ((et - T0) // 3600).astype(int); okk = (kk_ >= 0) & (kk_ < NH - 1); okk &= kk_ >= 1; hsc[kk_[okk] - 1] = hs5[okk]   # same alignment as robustness.py (ERA5 hour k+1 -> grid k)
lslow = RB.runmean(np.log(hsc), 72); r = gam(s["y"], s["m"], lo, hi, FULL, nb=300, ctrl=(RB.zs(lslow, mm),)); OUT["SACV local swell ctrl"] = r
log(f"  SACV with local-swell (ERA5 15N 23.5W, 3-d mean log Hs) interaction control: {fmt(r)}")
E_ = FULL["E"]; q3 = np.quantile(E_[mm], [1 / 3, 2 / 3]); qq = np.digitize(E_, q3)
log("  SACV by envelope tercile (neap->spring): mean local Hs " + ", ".join(f"{np.nanmean(hsc[mm & (qq == k)]):.2f} m" for k in range(3))
    + "; mean slow log10 SNR " + ", ".join(f"{np.nanmean(uu[mm & (qq == k)]):.3f}" for k in range(3)) + "; det rate " + ", ".join(f"{np.nanmean(s['det'][mm & (qq == k)]):.3f}" for k in range(3)))
for lab, (a_, b2_) in [("SACV 2022-03..2023-02", (lo, (lo + hi) // 2)), ("SACV 2023-03..2024-02", ((lo + hi) // 2, hi))]:
    r = gam(s["y"], s["m"], a_, b2_, FULL, nb=300); log(f"  {lab}: {fmt(r)}")
flush()
# =================== CAVEAT 2 ===================
log(f"\n==== CAVEAT 2: sub-proportional gamma {el()}")
log("  (a) errors-in-variables: gamma using envelopes predicted at other gauges (harmonic predictions; same LMB data)")
for sta in ["EDA", "TAM"]:
    lo, hi = SP[sta]
    for gname in ["Port Sonara (pipeline)", "Port Sonara", "Sao Tome", "Lagos"]:
        r = gam(SER[sta]["y"], SER[sta]["m"], lo, hi, GENV[gname], nb=300); OUT[f"eiv {sta} {gname}"] = r; log(f"  {sta} full span, envelope from {gname:24s}: {fmt(r)}")
# (c) binned shapes
log(f"  (c) shape fits to 8 envelope bins (in-phase amplitude; covariance from 30-d block bootstrap) {el()}")
def bins8(sta, nq=8, nb=600):
    s = SER[sta]; lo, hi = SP[sta]; mm = win(s["m"], lo, hi); E, th = FULL["E"], FULL["th"]
    edges = np.quantile(E[mm], np.linspace(0, 1, nq + 1)); q = np.clip(np.digitize(E, edges[1:-1]), 0, nq - 1)
    Xb = np.array([np.ones(NH), np.cos(th), np.sin(th)] + RB.NUIS + [np.cos(2 * th), np.sin(2 * th)]).T.copy()
    ii = np.flatnonzero(mm); Pk = []
    for k in range(nq):
        jj = ii[q[ii] == k]; b = solve(Xb[jj], s["y"][jj]); Pk.append(complex(b[1], -b[2]))
    Pk = np.array(Pk); Pall = RB.gamma_of(solve(envX(E, th, mm)[ii], s["y"][ii]))[2]; uvec = Pall / abs(Pall); A = (Pk * np.conj(uvec)).real
    DSk = [RB.DayStats(Xb, [s["y"]], mm & (q == k), lo, hi) for k in range(nq)]; B = []
    for _ in range(nb):
        st_ = R.bit_generator.state; row = []
        for k in range(nq): R.bit_generator.state = st_; bb = DSk[k].boot(30)[:, 0]; row.append(complex(bb[1], -bb[2]))
        B.append(row)
    B = (np.array(B) * np.conj(uvec)).real; Ek = np.array([E[ii][q[ii] == k].mean() for k in range(nq)])
    return Ek, A, np.cov(B.T)
SHAPES = {}
for sta in ["EDA", "TAM"]:
    Ek, A, Cv = bins8(sta); Li = np.linalg.cholesky(np.linalg.inv(Cv)); Em = Ek.mean()
    models = {"constant": (lambda p, E: p[0] + 0 * E, [0.4]), "proportional": (lambda p, E: p[0] * E, [0.8]),
              "linear+offset": (lambda p, E: p[0] + p[1] * E, [0.2, 0.5]), "power law": (lambda p, E: p[0] * (E / Em) ** p[1], [0.5, 0.7]),
              "saturating 1-exp": (lambda p, E: p[0] * (1 - np.exp(-E / max(p[1], 1e-3))), [0.8, 0.6])}
    res_ = {}
    for nm, (f, p0) in models.items():
        fit_ = optimize.least_squares(lambda p: Li.T @ (A - f(p, Ek)), p0); chi2 = float(np.sum(fit_.fun ** 2)); k_ = len(p0)
        p = fit_.x
        gimp = {"constant": 0.0, "proportional": 1.0, "linear+offset": p[1] * Em / (p[0] + p[1] * Em) if len(p) > 1 else np.nan, "power law": p[1] if len(p) > 1 else np.nan,
                "saturating 1-exp": (Em / p[1]) * np.exp(-Em / p[1]) / (1 - np.exp(-Em / p[1])) if len(p) > 1 else np.nan}[nm]
        res_[nm] = dict(params=p.tolist(), chi2=chi2, dof=len(A) - k_, p=float(stats.chi2.sf(chi2, len(A) - k_)), aic=chi2 + 2 * k_, gamma_at_mean=float(gimp))
        log(f"  {sta} {nm:17s}: chi2 {chi2:5.1f}/{len(A)-k_} (p={res_[nm]['p']:.3f}), AIC {chi2+2*k_:5.1f}, params " + ", ".join(f"{v:.3f}" for v in p) + f", implied dlnA/dlnE at mean {gimp:.2f}")
    SHAPES[sta] = dict(Ek=Ek.tolist(), A=A.tolist(), sd=np.sqrt(np.diag(Cv)).tolist(), fits=res_)
OUT["shapes"] = SHAPES; flush()
# (d)+(caveat 3) sideband (main + mirror) decomposition
log(f"\n  (d) + caveat 3: sideband decomposition of the response (joint fit incl. K2, L2, MU2, NU2, 2N2; 30-d day-aligned block bootstrap) {el()}")
SB = {}
def sideband(sta, lo, hi, nb=2000):
    s = SER[sta]; mm = win(s["m"], lo, hi); ii = np.flatnonzero(mm); b = solve(XE[ii], s["y"][ii]); DS = RB.DayStats(XE, [s["y"]], mm, lo, hi)
    def comp(bb):
        P = {n: cx(bb, n) for n in ["M2", "S2", "N2", "L2", "MU2", "K2"]}; aM = P["M2"] / TT["M2"]; out = {}
        for X_, Mi in [("S2", "MU2"), ("N2", "L2")]:
            rX = TT[X_] / TT["M2"]; gX = (P[X_] / (aM * TT[X_])).real; gm = ((P[Mi] - aM * TT[Mi]) / (aM * TT["M2"] * np.conj(rX))).real
            out[X_] = gX; out[Mi] = gm
        out["K2"] = (P["K2"] / (aM * TT["K2"])).real; out["L2amp"] = abs(P["L2"]); out["L2exp"] = abs(aM * TT["L2"]); out["MU2amp"] = abs(P["MU2"]); out["MU2exp"] = abs(aM * TT["MU2"])
        return out
    o = comp(b); Bb = [comp(DS.boot(30)[:, 0]) for _ in range(nb)]
    ci = {k: np.percentile([x[k] for x in Bb], [2.5, 97.5]).tolist() for k in o}
    dd = {k: np.array([x[k] for x in Bb]) for k in o}
    o["cons_N"] = o["L2"] - (o["N2"] - 1); o["cons_S"] = o["MU2"] - (o["S2"] - 1)
    ci["cons_N"] = np.percentile(dd["L2"] - (dd["N2"] - 1), [2.5, 97.5]).tolist(); ci["cons_S"] = np.percentile(dd["MU2"] - (dd["S2"] - 1), [2.5, 97.5]).tolist()
    gN = dd["N2"] + dd["L2"]; gS = dd["S2"] + dd["MU2"]
    return o, ci, dict(gamma_N=(o["N2"] + o["L2"], np.percentile(gN, [2.5, 97.5]).tolist()), gamma_S=(o["S2"] + o["MU2"], np.percentile(gS, [2.5, 97.5]).tolist()),
                       gN_from_main=(2 * o["N2"] - 1, np.percentile(2 * dd["N2"] - 1, [2.5, 97.5]).tolist()), gN_from_mirror=(2 * o["L2"] + 1, np.percentile(2 * dd["L2"] + 1, [2.5, 97.5]).tolist()),
                       gS_from_main=(2 * o["S2"] - 1, np.percentile(2 * dd["S2"] - 1, [2.5, 97.5]).tolist()), gS_from_mirror=(2 * o["MU2"] + 1, np.percentile(2 * dd["MU2"] + 1, [2.5, 97.5]).tolist()))
for lab, sta, (lo, hi) in [("EDA 2019-26", "EDA", SP["EDA"]), ("TAM 2022-26", "TAM", SP["TAM"]), ("EDA 2022-24", "EDA", CW["EDA"]), ("TAM 2022-24", "TAM", CW["TAM"]), ("SACV 2022-24", "SACV", CW["SACV"])]:
    o, ci, gg = sideband(sta, lo, hi); SB[lab] = dict(o=o, ci=ci, gg=gg)
    log(f"  {lab}: g_S2 {o['S2']:.2f} [{ci['S2'][0]:.2f},{ci['S2'][1]:.2f}]  g_MU2(mirror) {o['MU2']:+.2f} [{ci['MU2'][0]:+.2f},{ci['MU2'][1]:+.2f}]  | g_N2 {o['N2']:.2f} [{ci['N2'][0]:.2f},{ci['N2'][1]:.2f}]  "
        f"g_L2(mirror) {o['L2']:+.2f} [{ci['L2'][0]:+.2f},{ci['L2'][1]:+.2f}]  | g_K2 {o['K2']:.2f} [{ci['K2'][0]:.2f},{ci['K2'][1]:.2f}]")
    log(f"      implied gamma: spring-neap (S2 pair) main {gg['gS_from_main'][0]:+.2f} {np.round(gg['gS_from_main'][1],2).tolist()}, mirror {gg['gS_from_mirror'][0]:+.2f} {np.round(gg['gS_from_mirror'][1],2).tolist()}, "
        f"pair {gg['gamma_S'][0]:+.2f} {np.round(gg['gamma_S'][1],2).tolist()} | perigean (N2 pair) main {gg['gN_from_main'][0]:+.2f} {np.round(gg['gN_from_main'][1],2).tolist()}, "
        f"mirror {gg['gN_from_mirror'][0]:+.2f} {np.round(gg['gN_from_mirror'][1],2).tolist()}, pair {gg['gamma_N'][0]:+.2f} {np.round(gg['gamma_N'][1],2).tolist()}")
    log(f"      AM consistency (mirror - (main-1); 0 expected): N2/L2 {o['cons_N']:+.2f} [{ci['cons_N'][0]:+.2f},{ci['cons_N'][1]:+.2f}], S2/MU2 {o['cons_S']:+.2f} [{ci['cons_S'][0]:+.2f},{ci['cons_S'][1]:+.2f}]; "
        f"|L2| {o['L2amp']:.3f} dB (tide-following {o['L2exp']:.3f}), |MU2| {o['MU2amp']:.3f} dB (tide-following {o['MU2exp']:.3f})")
OUT["sidebands"] = SB; flush()
# =================== CAVEAT 3 ===================
log(f"\n==== CAVEAT 3: the L2 term {el()}")
L2R = {}
for lab, sta, (lo, hi) in [("EDA 2019-26", "EDA", SP["EDA"]), ("TAM 2022-26", "TAM", SP["TAM"])]:
    s = SER[sta]; mm = win(s["m"], lo, hi); ii = np.flatnonzero(mm); b = solve(XE[ii], s["y"][ii]); aL = abs(cx(b, "L2"))
    # nulls: random-start block resampling (data moved relative to tide)
    Xf = XE[lo:hi]; nl = {}
    for L in (360, 720):
        a = []
        for _ in range(NSUR):
            idx = RB.bidx(lo, hi, L); mb = s["m"][idx]; a.append(abs(cx(solve(Xf[mb], s["y"][idx][mb]), "L2")))
        nl[L] = (np.sum(np.array(a) >= aL) + 1) / (NSUR + 1)
    # look-elsewhere / local rank: residual amplitude at off-line frequencies 1.80-2.10 cpd
    resid = np.zeros(NH); resid[ii] = s["y"][ii] - XE[ii] @ b; span_d = (hi - lo) / 24
    lines = [WX[n] for n in WX] + [1.0, 2.0, 3.0, 4.0] + [2 * WX["M2"] - WX[n] for n in ["S2", "N2", "K2"]]
    fr = np.arange(1.80, 2.10, 1 / (2 * span_d)); fr = np.array([f for f in fr if min(abs(f - l_) for l_ in lines) > 3 / span_d])
    td = tg_d[ii]; amps = []
    for f in fr:
        G = np.c_[np.cos(2 * np.pi * f * td), np.sin(2 * np.pi * f * td)]; c_ = np.linalg.lstsq(G, resid[ii], rcond=None)[0]; amps.append(np.hypot(*c_))
    amps = np.array(amps); p_rank = (np.sum(amps >= aL) + 1) / (len(amps) + 1)
    # leakage: base model with L2 = 0 injected noise-free on the same mask
    leak = {}
    for gt in (1.0, 0.5, 0.3):
        ys_ = scale05((np.abs(zsd) ** (gt - 1) * zsd * np.exp(-1j * PHI)).real); bs_ = solve(XE[ii], ys_[ii]); aM_ = cx(bs_, "M2") / TT["M2"]
        leak[gt] = (float(((cx(bs_, "L2") - aM_ * TT["L2"]) / (aM_ * TT["M2"] * np.conj(TT["N2"] / TT["M2"]))).real), float((cx(bs_, "N2") / (aM_ * TT["N2"])).real),
                    float(((cx(bs_, "MU2") - aM_ * TT["MU2"]) / (aM_ * TT["M2"] * np.conj(TT["S2"] / TT["M2"]))).real), float((cx(bs_, "S2") / (aM_ * TT["S2"])).real))
    Cn = np.corrcoef(XE[ii][:, 1:].T); jL = IE["L2"] - 1; mx = np.max(np.abs(np.delete(Cn[jL], [jL, jL + 1])))
    L2R[lab] = dict(amp=aL, p15=nl[360], p30=nl[720], p_rank=p_rank, n_freq=len(fr), leak=leak, maxcorr=float(mx))
    log(f"  {lab}: |L2| {aL:.3f} dB; block-resampled nulls p15={nl[360]:.3f}, p30={nl[720]:.3f}; local rank among {len(fr)} off-line frequencies 1.80-2.10 cpd p={p_rank:.3f} "
        f"(x~5 sidebands that could have been blamed -> look-elsewhere p~{min(1, 5*p_rank):.2f}); max |corr| of L2 regressors with others {mx:.3f}")
    log("      estimator check on this mask, noise-free response |z|^(g-1) z (true AM, full Limbe tide): " + "; ".join(f"g={k}: g_L2 {v[0]:+.2f} (theory {(k-1)/2:+.2f}), g_N2 {v[1]:.2f} ({(k+1)/2:.2f}), g_MU2 {v[2]:+.2f}, g_S2 {v[3]:.2f}" for k, v in leak.items()))
# stability: L2 projected on the AM-predicted direction (-a_M T_M conj(r_N)) per calendar year and 2-yr window (EDA)
s = SER["EDA"]; rN = TT["N2"] / TT["M2"]; lo0, hi0 = SP["EDA"]; rows = []
for L, step in [(17520, 8760)]:
    st = lo0
    while st + L <= hi0 + 4000:
        lo, hi = st, min(st + L, NH); mm = win(s["m"], lo, hi)
        if mm.sum() > 5000:
            ii = np.flatnonzero(mm); b = solve(XE[ii], s["y"][ii]); aM = cx(b, "M2") / TT["M2"]
            gm = ((cx(b, "L2") - aM * TT["L2"]) / (aM * TT["M2"] * np.conj(rN))).real; gn = (cx(b, "N2") / (aM * TT["N2"])).real
            rows.append((str(grid_t[lo].astype(np.int64).astype("datetime64[s]"))[:7], float(gm), float(gn)))
        st += step
log("  EDA 2-yr windows (1-yr step): g_L2(mirror) / g_N2: " + "; ".join(f"{a} {b_:+.2f}/{c_:.2f}" for a, b_, c_ in rows))
OUT["L2"] = L2R; OUT["L2_windows"] = rows
# 3-h window: transfer of power modulation through Hann^2-weighted 3-h window at M2 vs L2
w = np.hanning(10800) ** 2; tt = np.arange(10800) / 86400.0
Hm = abs(np.sum(w * np.exp(-2j * np.pi * WX["M2"] * tt)) / w.sum()); Hl = abs(np.sum(w * np.exp(-2j * np.pi * WX["L2"] * tt)) / w.sum())
log(f"  3-h Hann^2 window transfer of a power modulation: M2 {Hm:.4f}, L2 {Hl:.4f} (ratio {Hl/Hm:.4f}) -> smoothing cannot enhance L2")
# (d) lunar envelope from gauge-fitted lunar constituents (M2, N2, L2, NU2, 2N2) and from M2+N2 only
zlun = zcx("M2") + zcx("N2") + zcx("L2") + zcx("NU2") + zcx("2N2"); ENVL = dict(E=sm25(np.abs(zlun)), th=np.angle(zlun))
zmn = zcx("M2") + zcx("N2"); ENVMN = dict(E=sm25(np.abs(zmn)), th=np.angle(zmn))
for lab, sta, (lo, hi) in [("EDA 2019-26", "EDA", SP["EDA"]), ("TAM 2022-26", "TAM", SP["TAM"]), ("SACV 2022-24", "SACV", CW["SACV"])]:
    r1 = gam(SER[sta]["y"], SER[sta]["m"], lo, hi, ENVMN, ("S2", "K2"), nb=NBS); r2 = gam(SER[sta]["y"], SER[sta]["m"], lo, hi, ENVL, ("S2", "K2"), nb=NBS)
    OUT[f"lunar {lab}"] = (r1, r2); log(f"  {lab}: lunar envelope M2+N2 (as before): {fmt(r1)} | gauge lunar set M2+N2+L2+NU2+2N2: {fmt(r2)}")
flush()
# =================== UNIFIED ===================
log(f"\n==== UNIFIED: envelope = full harmonic prediction from gauge constants, metric = continuous LMB (all QC hours), EIV range {el()}")
att = [EIV[k] for k in EIV if ("control" not in k and "delayed" not in k)]; amin, amax = min(att), max(att)
UN = {}
for lab, sta, (lo, hi) in [("EDA 2019-26", "EDA", SP["EDA"]), ("TAM 2022-26", "TAM", SP["TAM"]), ("SACV 2022-24", "SACV", CW["SACV"]), ("EDA 2022-24", "EDA", CW["EDA"]), ("TAM 2022-24", "TAM", CW["TAM"])]:
    r = gam(SER[sta]["y"], SER[sta]["m"], lo, hi, FULL, nb=1000); UN[lab] = r
    log(f"  {lab}: {fmt(r)}; divided by the gauge/constituent-error attenuation range {amin:.2f}-{amax:.2f}: {r['gamma']/amax:+.2f} to {r['gamma']/amin:+.2f}")
OUT["unified"] = UN
# =================== EXTRA discriminating tests (added after first pass; RNG draws above unchanged) ===================
log(f"\n==== EXTRA TESTS {el()}")
# (1) caveat 2: does the response follow a DELAYED envelope? (a lag would attenuate gamma with the instantaneous envelope)
LAGSC = {}
for sta in ["EDA", "TAM"]:
    lo, hi = SP[sta]; s = SER[sta]; mm = win(s["m"], lo, hi); ii = np.flatnonzero(mm); rows = []
    for lag in range(-48, 145, 12):
        X = envX(np.roll(FULL["E"], lag), FULL["th"], mm); b = solve(X[ii], s["y"][ii]); rss = float(np.sum((s["y"][ii] - X[ii] @ b) ** 2)); g, gq, P = RB.gamma_of(b)
        rows.append((lag, float(g), float(gq), rss))
    r0 = [r for r in rows if r[0] == 0][0][3]; LAGSC[sta] = rows; best = min(rows, key=lambda r: r[3])
    log(f"  {sta} envelope-delay scan (response follows E(t-lag)): " + ", ".join(f"{r[0]:+d}h {r[1]:+.2f}" for r in rows) + f"; best lag by RSS {best[0]:+d} h (gamma {best[1]:+.2f}, dRSS vs lag 0 {best[3]-r0:+.1f} dB^2)")
OUT["lagscan"] = LAGSC
# (2) caveat 1(d/e): tidal response of the two background bands that LMB regresses out (if the background is itself spring-neap modulated, LMB inherits it)
for sta in ["EDA", "TAM", "SACV"]:
    lo, hi = CW[sta]; s = SER[sta]; parts = []
    for nm in ["b1", "b2"]:
        r = gam(s[nm], s["m"], lo, hi, FULL, nb=300); parts.append(f"{'20-24 s' if nm == 'b1' else '29-34 s'} band: Q/P {r['gamma']:+.2f} [{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}], M2-band A {r['A']:.3f} dB")
        mm = win(s["m"], lo, hi); X = envX(FULL["E"], FULL["th"], mm); ii = np.flatnonzero(mm); b = solve(X[ii], s[nm][ii]); parts[-1] += f", spring-neap amplitude |Q| {abs(complex(b[3], -b[4])):.3f} dB"
    mm = win(s["m"], lo, hi); ii = np.flatnonzero(mm); G = np.c_[np.ones(len(ii)), s["b1"][ii], s["b2"][ii]]; beta = np.linalg.lstsq(G, s["line"][ii], rcond=None)[0]
    log(f"  {sta} 2022-24 background bands | " + " | ".join(parts) + f" | LMB regression weights b1 {beta[1]:.2f}, b2 {beta[2]:.2f}")
# (3) caveat 1: joint power simulation in the common window (same blocks for all stations): how unusual is it that all three are low together?
log(f"  -- joint power simulation 2022-03..2024-02 (shared random-start 15-d blocks; inverse-variance mean of EDA, TAM, SACV gamma) {el()}")
JP = {}
fits = {}
for sta in JS:
    s = SER[sta]; mm = win(s["m"], k0, k1); X = envX(FULL["E"], FULL["th"], mm); ii = np.flatnonzero(mm); b = solve(X[ii], s["y"][ii])
    res = np.zeros(NH); res[ii] = s["y"][ii] - X[ii] @ b; fits[sta] = (mm, X, b, res)
wts = {sta: 1 / PW[{"EDA": "EDA 2022-24", "TAM": "TAM 2022-24", "SACV": "SACV 2022-24"}[sta]][0.7]["sd"] ** 2 for sta in JS}
gobs_m = sum(wts[k] * gobs[k] for k in JS) / sum(wts.values())
for gt in (0.7, 1.0):
    ms = []
    for _ in range(NSIM):
        idx = RB.bidx(k0, k1, 360); gg = {}
        for sta in JS:
            mm, X, b, res = fits[sta]; bh = b.copy(); bh[3:5] = gt * b[1:3]; mb = mm[idx]; dest = np.arange(k0, k1)[mb]
            gg[sta] = RB.gamma_of(solve(X[dest], (X @ bh)[dest] + res[idx][mb]))[0]
        ms.append(sum(wts[k] * gg[k] for k in JS) / sum(wts.values()))
    ms = np.array(ms); JP[gt] = dict(mean=float(ms.mean()), sd=float(ms.std()), p=float(np.mean(ms <= gobs_m)))
    log(f"  true gamma {gt}: weighted-mean gamma_hat {ms.mean():.2f} ± {ms.std():.2f}; observed weighted mean {gobs_m:+.2f}; P(<= observed) {np.mean(ms <= gobs_m):.3f}")
OUT["joint_power"] = JP
# (4) caveat 3(d): rebuilt lunar envelope -> bootstrap P(gamma<=0), P(gamma>=1)
for lab, sta, (lo, hi) in [("EDA 2019-26", "EDA", SP["EDA"]), ("TAM 2022-26", "TAM", SP["TAM"])]:
    s = SER[sta]
    for nm, env in [("M2+N2", ENVMN), ("M2+N2+L2+NU2+2N2", ENVL)]:
        mm = win(s["m"], lo, hi); X = envX(env["E"], env["th"], mm, ("S2", "K2")); DS = RB.DayStats(X, [s["y"]], mm, lo, hi)
        gb = np.array([RB.gamma_of(DS.boot(30)[:, 0])[0] for _ in range(NBS)])
        e_ = env["E"][mm] / env["E"][mm].mean() - 1
        log(f"  {lab} lunar envelope {nm:17s}: boot P(gamma<=0) {np.mean(gb <= 0):.3f}, P(gamma>=1) {np.mean(gb >= 1):.3f}; envelope e 5-95% {np.percentile(e_,5):+.2f}..{np.percentile(e_,95):+.2f}; corr with M2+N2 env {np.corrcoef(env['E'], ENVMN['E'])[0,1]:.3f}")
# (5) caveat 1(b): post-hoc early/late split at EDA (split chosen after seeing rolling windows -> descriptive only)
c22 = int((np.datetime64("2022-01-01T00:00", "s").astype(np.int64) - T0) // 3600)
rA = gam(SER["EDA"]["y"], SER["EDA"]["m"], SP["EDA"][0], c22, FULL, nb=1000); rB_ = gam(SER["EDA"]["y"], SER["EDA"]["m"], c22, SP["EDA"][1], FULL, nb=1000)
z_ = (rA["gamma"] - rB_["gamma"]) / np.hypot(rA["sd"], rB_["sd"])
log(f"  EDA post-hoc split: 2019-05..2021-12 {fmt(rA)} | 2022-01..2026-09 {fmt(rB_)} | difference z={z_:.2f} (nominal two-sided p={2*stats.norm.sf(abs(z_)):.3f}; NOT corrected for choosing the split)")
# (6) solar S2 bound: extra S2 (beyond AM prediction from MU2) in dB
for lab in ["EDA 2019-26", "TAM 2022-26"]:
    o, ci = SB[lab]["o"], SB[lab]["ci"]; sta = lab[:3]; s = SER[sta]; lo, hi = SP[sta]; mm = win(s["m"], lo, hi); ii = np.flatnonzero(mm); b = solve(XE[ii], s["y"][ii])
    aS = abs(cx(b, "M2") / TT["M2"] * TT["S2"])
    log(f"  {lab}: S2 excess over AM prediction (= -consistency) {-o['cons_S']:+.2f} [{-ci['cons_S'][1]:+.2f},{-ci['cons_S'][0]:+.2f}] x |a_M T_S2| {aS:.3f} dB -> additive S2 bound {-ci['cons_S'][0]*aS:+.3f} dB (95% upper)")
flush()
# ---------------- figures ----------------
fig, ax = plt.subplots(1, 2, figsize=(14, 4.8))
for sta, col in [("EDA", "k"), ("TAM", "C1")]:
    rows = [q for q in ROLL[sta] if q["tag"] == "2yr"]
    t_ = np.array([int(q["tmid"]) for q in rows]).astype("datetime64[s]").astype("O"); g = np.array([q["gamma"] for q in rows]); sd = np.array([q["sd"] for q in rows])
    ax[0].plot(t_, g, "o-", color=col, label=f"{sta} 2-yr windows (3-month step)"); ax[0].fill_between(t_, g - 1.96 * sd, g + 1.96 * sd, color=col, alpha=0.15)
ax[0].axhline(1, color="C3", ls="--", lw=0.8); ax[0].axhline(0, color="C0", ls="--", lw=0.8)
ax[0].set_ylabel("gamma (full envelope)"); ax[0].set_title("Caveat 1: gamma in rolling 2-yr windows (window centre), 95% bootstrap band", fontsize=9); ax[0].legend(fontsize=7)
labs = list(PW); xs = np.arange(len(labs))
ax[1].errorbar(xs - 0.1, [PW[l][0.7]["mean"] for l in labs], yerr=[1.96 * PW[l][0.7]["sd"] for l in labs], fmt="s", color="0.5", capsize=3, label="simulated, true gamma 0.7 (±1.96 sd)")
ax[1].errorbar(xs + 0.1, [PW[l][1.0]["mean"] for l in labs], yerr=[1.96 * PW[l][1.0]["sd"] for l in labs], fmt="s", color="C3", capsize=3, label="simulated, true gamma 1.0")
ax[1].plot(xs, [PW[l]["gobs"] for l in labs], "k*", ms=12, label="observed"); ax[1].set_xticks(xs); ax[1].set_xticklabels(labs, fontsize=8); ax[1].axhline(0, color="C0", lw=0.8, ls="--")
ax[1].set_title("power analysis (injection into real residuals, 15-d random-start blocks)", fontsize=9); ax[1].legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig12_caveat1_power_rolling.png"), dpi=120); plt.close(fig)
fig, ax = plt.subplots(1, 3, figsize=(16, 4.8))
for i, sta in enumerate(["EDA", "TAM"]):
    S_ = SHAPES[sta]; Ek = np.array(S_["Ek"]); A = np.array(S_["A"]); sd = np.array(S_["sd"]); a = ax[i]
    a.errorbar(Ek, A, yerr=1.96 * sd, fmt="ko", capsize=3); xx = np.linspace(0.01, Ek.max() * 1.1, 100); Em = Ek.mean()
    for nm, col in [("proportional", "C3"), ("linear+offset", "C2"), ("power law", "C4"), ("saturating 1-exp", "C1"), ("constant", "C0")]:
        p = S_["fits"][nm]["params"]
        f = {"constant": lambda E: p[0] + 0 * E, "proportional": lambda E: p[0] * E, "linear+offset": lambda E: p[0] + p[1] * E, "power law": lambda E: p[0] * (E / Em) ** p[1],
             "saturating 1-exp": lambda E: p[0] * (1 - np.exp(-E / p[1]))}[nm]
        a.plot(xx, f(xx), color=col, label=f"{nm}: chi2 {S_['fits'][nm]['chi2']:.1f}/{S_['fits'][nm]['dof']}, AIC {S_['fits'][nm]['aic']:.1f}")
    a.set_xlim(0, None); a.set_ylim(0, None); a.set_xlabel("envelope (m)"); a.set_ylabel("in-phase M2-band response (dB)"); a.set_title(f"Caveat 2: {sta} full span, 8 envelope bins", fontsize=9); a.legend(fontsize=6.5)
a = ax[2]; ks = [k for k in EIV]; a.barh(range(len(ks)), [EIV[k] for k in ks], color="0.6"); a.set_yticks(range(len(ks))); a.set_yticklabels(ks, fontsize=7); a.axvline(1, color="C3", ls="--")
a.set_xlabel("recovered gamma (true response proportional to listed tide)", fontsize=8); a.set_title("errors-in-variables attenuation (noise-free)", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig13_caveat2_shapes_eiv.png"), dpi=120); plt.close(fig)
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
a = ax[0]; labs = list(SB); y0 = 0; yt = []; yl = []
for lab in labs:
    gg = SB[lab]["gg"]
    for j, (k, col, nm) in enumerate([("gS_from_main", "k", "S2 (main)"), ("gS_from_mirror", "0.5", "MU2 (mirror)"), ("gN_from_main", "C3", "N2 (main)"), ("gN_from_mirror", "C1", "L2 (mirror)")]):
        v, ci = gg[k]; a.errorbar(v, y0, xerr=[[v - ci[0]], [ci[1] - v]], fmt="o", color=col, capsize=2); yt.append(y0); yl.append(f"{lab}: {nm}"); y0 += 1
    y0 += 1
a.axvline(1, color="C3", ls="--", lw=0.8); a.axvline(0, color="C0", ls="--", lw=0.8); a.set_yticks(yt); a.set_yticklabels(yl, fontsize=6); a.set_xlim(-4, 5)
a.set_xlabel("implied gamma (AM model): main 2g-1, mirror 2g+1"); a.set_title("Caveat 3: main vs mirror sidebands (95% CI)", fontsize=9)
a = ax[1]; a.plot([r[0] for r in OUT["L2_windows"]], [r[1] for r in OUT["L2_windows"]], "o-", color="C1", label="g_L2 (mirror)"); a.plot([r[0] for r in OUT["L2_windows"]], [r[2] - 1 for r in OUT["L2_windows"]], "s--", color="C3", label="g_N2 - 1 (AM prediction for mirror)")
a.axhline(0, color="0.5", lw=0.8); a.set_title("EDA 2-yr windows (1-yr step): L2 mirror term vs AM prediction from N2", fontsize=9); a.legend(fontsize=7); a.tick_params(axis="x", labelsize=7)
fig.tight_layout(); fig.savefig(os.path.join(D, "fig14_caveat3_sidebands.png"), dpi=120); plt.close(fig)
json.dump(js(OUT), open(os.path.join(D, "caveats.json"), "w"), indent=1, default=lambda o: str(o))
log(f"done {el()}"); flush()
