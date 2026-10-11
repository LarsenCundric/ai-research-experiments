"""Robustness round (10 Oct 2026) for the M2 modulation of the 26 s Gulf of Guinea line.
Metric throughout: 'line minus background' (LMB) = 72-h high-passed fixed-band 26 s PSD (37.5-38.6 mHz, dB) with the
72-h high-passed 20-24 s and 29-34 s background bands regressed out (as in multistation.py / source_vs_site.py).
 1. Spring-neap / amplitude-scaling tests
    a) per-bin (terciles, quintiles) of the tidal envelope: in-phase semidiurnal response amplitude and lag
    b) envelope-interaction regression y = Re[(P + Q e(t)) exp(i theta(t))]; gamma = Re(Q/P) (1 = proportional to the
       tide, 0 = constant amplitude). Three envelopes: full semidiurnal band (spring-neap+perigee; S2 is solar-confounded),
       M2+S2 only (classic spring-neap), M2+N2 only (perigean, lunar only: no solar confound)
       + admittance ratios S2/M2, N2/M2 against the Port Sonara gauge and the equilibrium potential
    c) significance: block bootstrap CIs, H0 (gamma=0) surrogates = constant-amplitude fit + residual resampled in random-start
       15-d blocks, and + smoothed-spectrum phase-randomised residual
    controls: slow line strength (5-d mean log SNR) and ERA5 swell (3-d mean log Hs) interactions; additive swell covariates
 2. Moving-block bootstrap (15 d, 30 d) of M2 amplitude/phase per station; joint (same blocks) multi-station mean phase;
    conservative nulls: random-start block-resampled surrogates (15 d, 30 d) + phase-randomised (smoothed spectrum)
 3. All stations with features_*.npz (EDA, TAM, MBAR, SHEL, ASCN, WIN, SACV)
 4. Leave-one-year-out and single-year EDA M2 phasor
Outputs: robustness.txt, robustness.json, fig10_springneap.png, fig8_multistation_M2_phasors.png (fig8 v1 kept as *_v1.png),
fig11_loyo.png. Single process; run with nice -n 19 and ulimit -v."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import sys, json, time, shutil, numpy as np
from tidelib import *
import tidelib as TL
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import hilbert
from scipy import stats
R = np.random.default_rng(20261010)
NB = int(os.environ.get("NBOOT", 2000)); NS = int(os.environ.get("NSUR", 1000))
TL.LOG.clear(); OUT = {}; t_start = time.time()
def el(): return f"[{(time.time()-t_start)/60:.1f} min]"
c0 = np.datetime64("2022-03-01T00:00", "s").astype(np.int64); c1 = np.datetime64("2024-03-01T00:00", "s").astype(np.int64)
k0, k1 = int((c0 - T0) // 3600), int((c1 - T0) // 3600)
ALL = ["EDA", "TAM", "MBAR", "SHEL", "ASCN", "WIN", "SACV"]
STA = [s for s in ALL if os.path.exists(os.path.join(D, "features.npz" if s == "EDA" else f"features_{s}.npz"))]
SID = dict(EDA="G.EDA.00.LHZ", TAM="G.TAM.00.LHZ", MBAR="II.MBAR.00.LHZ", SHEL="II.SHEL.00.LHZ", ASCN="II.ASCN.00.LHZ", WIN="GE.WIN.--.LHZ", SACV="II.SACV.00.LHZ")
SRC = (4.0, 8.0)   # nominal Bight of Bonny reference point, used ONLY for distance/azimuth bookkeeping
WM2 = 2 * np.pi * W["M2"] / 24.0   # rad/h
# ---------------- tide: analytic signals and envelopes ----------------
Zt = np.fft.rfft(tide_g); fz = np.fft.rfftfreq(NH, 1 / 24.0)
zsd = hilbert(np.fft.irfft(Zt * ((fz > 1.5) & (fz < 2.5)), NH))
def zc(nm): a, b = TL._bt[nm]; return (a - 1j * b) * np.exp(1j * 2 * np.pi * W[nm] * tg_d)
sm25 = lambda v: np.convolve(np.pad(v, 12, mode="edge"), np.ones(25) / 25, mode="valid")
ENV = {}
for key, z in [("full", zsd), ("M2+S2", zc("M2") + zc("S2")), ("M2+N2", zc("M2") + zc("N2"))]:
    ENV[key] = dict(E=sm25(np.abs(z)), th=np.angle(z))
TC = {nm: complex(TL._bt[nm][0], -TL._bt[nm][1]) for nm in ["M2", "S2", "N2"]}   # complex tide coefficient (m) at Port Sonara
EQ = dict(M2=0.9081, S2=0.4229, N2=0.1739)   # Doodson/Cartwright equilibrium-tide coefficients (relative)
log(f"Port Sonara tide (UTide prediction, joint fit on grid): M2 {abs(TC['M2']):.3f} m, S2 {abs(TC['S2']):.3f} m, N2 {abs(TC['N2']):.3f} m; "
    f"S2/M2 {abs(TC['S2'])/abs(TC['M2']):.3f} (equilibrium {EQ['S2']/EQ['M2']:.3f}), N2/M2 {abs(TC['N2'])/abs(TC['M2']):.3f} (equilibrium {EQ['N2']/EQ['M2']:.3f})")
for k, v in ENV.items():
    log(f"envelope '{k}': mean {v['E'].mean():.3f} m, 5-95% {np.percentile(v['E'],5):.3f}-{np.percentile(v['E'],95):.3f} m")
# ---------------- ERA5 swell (cached) ----------------
E5 = json.load(open(os.path.join(D, "meta/era5_ocean_3N8E.json")))["hourly"]
hs = np.array([np.nan if v is None else v for v in E5["wave_height"]], float); tp = np.array([np.nan if v is None else v for v in E5["wave_peak_period"]], float)
hsg = np.full(NH, np.nan); tpg = np.full(NH, np.nan); n5 = min(NH - 1, len(hs) - 1)
hsg[:n5] = hs[1:n5 + 1]; tpg[:n5] = tp[1:n5 + 1]   # window centre = grid hour + 1.5 h -> ERA5 hour k+1
def runmean(v, n):
    ok = np.isfinite(v); a = np.convolve(np.where(ok, v, 0), np.ones(n), "same"); b = np.convolve(ok.astype(float), np.ones(n), "same")
    with np.errstate(all="ignore"): return a / b
lhs_slow = runmean(np.log(hsg), 72); lhs_hp, _ = prep(hp(np.log(hsg))); tp_hp, _ = prep(hp(tpg))
def zs(v, m):
    v = v.copy(); mu, sd = np.nanmean(v[m]), np.nanstd(v[m]); v = (v - mu) / sd; v[~np.isfinite(v)] = 0; return v
# ---------------- station series ----------------
def harm_cols(nms):
    cols = []
    for nm in nms: cols += [np.cos(2 * np.pi * W[nm] * tg_d), np.sin(2 * np.pi * W[nm] * tg_d)]
    return cols
XH = np.array([np.ones(NH)] + harm_cols(NAMES)).T.copy()          # joint harmonic design (19 cols), like tidelib.fit
IH = {nm: 1 + 2 * i for i, nm in enumerate(NAMES)}
def cplx(b, i): return complex(b[i], -b[i + 1])                      # a cos + b sin  ->  (a - i b)
def lagh(Pc, ref): return float(((np.angle(ref) - np.angle(Pc)) % (2 * np.pi)) / WM2)   # hours after HW (M2 rate); peak of Re[P e^{i theta}] at theta=-arg P
def lag_nm(Pc, nm): return float(((np.angle(TC[nm]) - np.angle(Pc)) % (2 * np.pi)) / (2 * np.pi * W[nm] / 24))
def solve(X, y): return np.linalg.solve(X.T @ X, X.T @ y)
SER = {}; META = {}
from obspy import read_inventory
from obspy.geodetics import gps2dist_azimuth
for sta in STA:
    S = load(sta); c = S["c"]
    yy, m = prep(hp(grid(S, L10(c["fixband"]), S["qc"]))); b1, _ = prep(hp(grid(S, L10(c["bg_2024"]), S["qc"]))); b2, _ = prep(hp(grid(S, L10(c["bg_2834"]), S["qc"])))
    G = np.c_[np.ones(m.sum()), b1[m], b2[m]]; beta = np.linalg.lstsq(G, yy[m], rcond=None)[0]
    res = np.zeros(NH); res[m] = yy[m] - G @ beta; res[m] -= res[m].mean()
    lsnr = grid(S, L10(c["snr_w"]), S["qc"]); u = runmean(lsnr, 120)
    qcg = grid(S, np.ones(len(S["t"])), S["qc"]); detg = grid(S, S["det"].astype(float), S["qc"])
    SER[sta] = dict(y=res * DB, m=m, b1=b1 * DB, b2=b2 * DB, line=yy * DB, u=u, det=detg)
    try:
        inv = read_inventory(os.path.join(D, "meta", SID[sta] + ".xml")); ch = inv[0][0]
        dist, az, _ = gps2dist_azimuth(SRC[0], SRC[1], ch.latitude, ch.longitude); META[sta] = dict(lat=ch.latitude, lon=ch.longitude, dist_km=dist / 1e3, az=az)
    except Exception as ex: META[sta] = dict(err=str(ex))
    sel = (S["t"] >= c0) & (S["t"] < c1)
    META[sta].update(qc_common=int((S["qc"] & sel).sum()), det_common=int((S["det"] & sel).sum()), qc_all=int(S["qc"].sum()), det_all=int(S["det"].sum()),
                     span=f"{str(S['t'].min().astype('datetime64[s]'))[:10]}..{str(S['t'].max().astype('datetime64[s]'))[:10]}")
    del S
    log(f"{sta}: {META[sta]}")
OUT["meta"] = META
def span(m, lo=0, hi=NH):
    v = np.flatnonzero(m[lo:hi]); return lo + v[0], lo + v[-1] + 1
def bidx(lo, hi, L):
    nb = int(np.ceil((hi - lo) / L)); st = R.integers(lo, hi - L + 1, nb); return (st[:, None] + np.arange(L)).ravel()[:hi - lo]
class DayStats:
    """Per-day X'X and X'y (masked) on [lo,hi) -> fast moving-block pairs bootstrap with day-aligned block starts."""
    def __init__(self, X, ys, m, lo, hi):
        dlo, dhi = lo // 24, -(-hi // 24); n = (dhi - dlo) * 24; w = np.zeros(n); r0 = dlo * 24
        sel = np.arange(lo, hi); w[sel - r0] = m[sel]
        Xr = np.zeros((n, X.shape[1])); Xr[sel - r0] = X[sel]; Xr = Xr.reshape(dhi - dlo, 24, -1); wr = w.reshape(dhi - dlo, 24, 1)
        Y = np.zeros((n, len(ys))); Y[sel - r0] = np.array([yv[sel] for yv in ys]).T; Y = Y.reshape(dhi - dlo, 24, -1)
        A = np.einsum("dhp,dhq->dpq", Xr * wr, Xr); B = np.einsum("dhp,dhk->dpk", Xr * wr, Y)
        self.cA = np.concatenate([np.zeros((1,) + A.shape[1:]), np.cumsum(A, 0)]); self.cB = np.concatenate([np.zeros((1,) + B.shape[1:]), np.cumsum(B, 0)])
        self.nd = dhi - dlo
    def boot(self, Ld):
        nfull, rem = divmod(self.nd, Ld); st = R.integers(0, self.nd - Ld + 1, nfull)
        A = (self.cA[st + Ld] - self.cA[st]).sum(0); B = (self.cB[st + Ld] - self.cB[st]).sum(0)
        if rem:
            s0 = R.integers(0, self.nd - rem + 1); A = A + self.cA[s0 + rem] - self.cA[s0]; B = B + self.cB[s0 + rem] - self.cB[s0]
        return np.linalg.solve(A, B)   # p x k
# ---------------- main harmonic fit + bootstrap + conservative nulls ----------------
def mainfit(y, m, lo, hi, extra=None):
    ii = np.arange(lo, hi); ii = ii[m[ii]]; X = XH[ii] if extra is None else np.c_[XH[ii], extra[ii]]
    return solve(X, y[ii])
def harmonic_block(sta, lo, hi, label, nb=NB, Ls=(360, 720), do_null=True):
    s = SER[sta]; y, m = s["y"], s["m"]; b = mainfit(y, m, lo, hi)
    P = {nm: cplx(b, IH[nm]) for nm in ["M2", "S2", "N2", "S1", "K1", "O1", "M4"]}
    r = dict(n=int(m[lo:hi].sum()), A={k: abs(v) for k, v in P.items()}, lagM2=lag_nm(P["M2"], "M2"), lagS2=lag_nm(P["S2"], "S2"), lagN2=lag_nm(P["N2"], "N2"))
    # OLS (white-noise) variance of M2 coefficient
    ii = np.arange(lo, hi); ii = ii[m[ii]]; X = XH[ii]; resid = y[ii] - X @ b; s2 = resid.var()
    covO = s2 * np.linalg.inv(X.T @ X); varO = 0.5 * (covO[IH["M2"], IH["M2"]] + covO[IH["M2"] + 1, IH["M2"] + 1])
    DS = DayStats(XH, [y], m, lo, hi)
    for L in Ls:
        Bs = []
        for _ in range(nb):
            bb = DS.boot(L // 24)[:, 0]
            Bs.append([cplx(bb, IH[nm]) for nm in ["M2", "S2", "N2"]])
        Bs = np.array(Bs); M2b = Bs[:, 0]
        amp = np.abs(M2b); lagb = ((np.angle(TC["M2"]) - np.angle(M2b)) % (2 * np.pi)) / WM2
        lagb = (lagb - r["lagM2"] + 6.21) % 12.42 - 6.21 + r["lagM2"]
        varB = 0.5 * (np.var(M2b.real) + np.var(M2b.imag)); vif = varB / varO
        # Mahalanobis distance of the M2 coefficient from zero using the bootstrap covariance
        C = np.cov(np.c_[M2b.real, M2b.imag].T); v = np.array([P["M2"].real, P["M2"].imag]); d2 = float(v @ np.linalg.solve(C, v))
        aS = np.abs(Bs[:, 1]) / np.abs(Bs[:, 0]); aN = np.abs(Bs[:, 2]) / np.abs(Bs[:, 0])
        adm_S = (Bs[:, 1] / TC["S2"]) / (Bs[:, 0] / TC["M2"]); adm_N = (Bs[:, 2] / TC["N2"]) / (Bs[:, 0] / TC["M2"])
        r[f"boot{L//24}d"] = dict(A_ci=list(np.percentile(amp, [2.5, 97.5])), A_sd=float(amp.std()), lag_ci=list(np.percentile(lagb, [2.5, 97.5])), lag_sd=float(lagb.std()),
                                 vif=float(vif), n_eff=float(r["n"] / vif), z_maha=float(np.sqrt(d2)), p_maha=float(stats.chi2.sf(d2, 2)),
                                 S2M2_ci=list(np.percentile(aS, [2.5, 97.5])), N2M2_ci=list(np.percentile(aN, [2.5, 97.5])),
                                 admS_ratio_ci=list(np.percentile(np.abs(adm_S), [2.5, 97.5])), admS_dphase_ci=list(np.percentile(-np.degrees(np.angle(adm_S)), [2.5, 97.5])),
                                 admN_ratio_ci=list(np.percentile(np.abs(adm_N), [2.5, 97.5])), admN_dphase_ci=list(np.percentile(-np.degrees(np.angle(adm_N)), [2.5, 97.5])),
                                 M2b=M2b)
    admS = (P["S2"] / TC["S2"]) / (P["M2"] / TC["M2"]); admN = (P["N2"] / TC["N2"]) / (P["M2"] / TC["M2"])
    r.update(S2M2=abs(P["S2"]) / abs(P["M2"]), N2M2=abs(P["N2"]) / abs(P["M2"]), admS=abs(admS), admS_dph=float(-np.degrees(np.angle(admS))), admN=abs(admN), admN_dph=float(-np.degrees(np.angle(admN))))
    if do_null:
        nulls = {}
        for L in Ls:   # random-start block-resampled surrogates: data blocks moved to random tidal phase, design fixed
            Xf = XH[lo:hi]; a = []; aSN = []
            for _ in range(NS):
                idx = bidx(lo, hi, L); mb = m[idx]; bb = solve(Xf[mb], y[idx][mb]); a.append(abs(cplx(bb, IH["M2"]))); aSN.append([abs(cplx(bb, IH["S2"])), abs(cplx(bb, IH["N2"]))])
            aSN = np.array(aSN); r[f"p_S2_blockres{L//24}d"] = float((np.sum(aSN[:, 0] >= r["A"]["S2"]) + 1) / (NS + 1)); r[f"p_N2_blockres{L//24}d"] = float((np.sum(aSN[:, 1] >= r["A"]["N2"]) + 1) / (NS + 1))
            a = np.array(a); nulls[f"blockres{L//24}d"] = dict(p=float((np.sum(a >= r["A"]["M2"]) + 1) / (NS + 1)), null95=float(np.percentile(a, 95)),
                                                               z=float((r["A"]["M2"] - a.mean()) / a.std()), exceed=int(np.sum(a >= r["A"]["M2"])), n=int(len(a)))
        x, mm = np.zeros(NH), np.zeros(NH, bool); x[lo:hi] = y[lo:hi]; mm[lo:hi] = m[lo:hi]; a = []
        XHm = XH[mm]; Pm = np.linalg.solve(XHm.T @ XHm, XHm.T)
        for ys in surrogates(x, mm, NS // 2):
            bb = Pm @ ys[mm]; a.append(abs(cplx(bb, IH["M2"])))
        a = np.array(a); nulls["phaserand"] = dict(p=float((np.sum(a >= r["A"]["M2"]) + 1) / (len(a) + 1)), null95=float(np.percentile(a, 95)),
                                                   z=float((r["A"]["M2"] - a.mean()) / a.std()), exceed=int(np.sum(a >= r["A"]["M2"])), n=int(len(a)))
        r["nulls"] = nulls
    b15, b30 = r.get("boot15d"), r.get("boot30d")
    line = (f"  {label:26s} n={r['n']:6d} M2 {r['A']['M2']:.3f} dB [{b30['A_ci'][0]:.3f},{b30['A_ci'][1]:.3f}] lag +{r['lagM2']:.2f} h "
            f"[{b30['lag_ci'][0]:.2f},{b30['lag_ci'][1]:.2f}] (30-d blocks; 15-d: [{b15['lag_ci'][0]:.2f},{b15['lag_ci'][1]:.2f}] h); "
            f"VIF {b30['vif']:.2f} n_eff {b30['n_eff']:.0f}; z_boot {b30['z_maha']:.1f}")
    log(line)
    if do_null:
        log("      nulls: " + "; ".join(f"{k}: p={v['p']:.4f} ({v['exceed']}/{v['n']} exceed, null95 {v['null95']:.3f} dB, z={v['z']:.1f})" for k, v in r["nulls"].items()))
    if do_null: log(f"      block-resampled nulls for S2: p15={r['p_S2_blockres15d']:.4f}, p30={r['p_S2_blockres30d']:.4f}; N2: p15={r['p_N2_blockres15d']:.4f}, p30={r['p_N2_blockres30d']:.4f}")
    log(f"      S2 {r['A']['S2']:.3f} dB (+{r['lagS2']:.2f} h), N2 {r['A']['N2']:.3f} dB (+{r['lagN2']:.2f} h), S1 {r['A']['S1']:.3f}, M4 {r['A']['M4']:.3f}; "
        f"S2/M2 {r['S2M2']:.3f} [{b30['S2M2_ci'][0]:.3f},{b30['S2M2_ci'][1]:.3f}] (gauge {abs(TC['S2'])/abs(TC['M2']):.3f}, equil {EQ['S2']/EQ['M2']:.3f}); "
        f"N2/M2 {r['N2M2']:.3f} [{b30['N2M2_ci'][0]:.3f},{b30['N2M2_ci'][1]:.3f}] (gauge {abs(TC['N2'])/abs(TC['M2']):.3f}, equil {EQ['N2']/EQ['M2']:.3f})")
    log(f"      admittance rel. to M2 (1 = proportional to gauge tide): S2 {r['admS']:.2f} [{b30['admS_ratio_ci'][0]:.2f},{b30['admS_ratio_ci'][1]:.2f}] extra phase lag {r['admS_dph']:+.0f} deg "
        f"[{b30['admS_dphase_ci'][0]:+.0f},{b30['admS_dphase_ci'][1]:+.0f}]; N2 {r['admN']:.2f} [{b30['admN_ratio_ci'][0]:.2f},{b30['admN_ratio_ci'][1]:.2f}] extra phase lag {r['admN_dph']:+.0f} deg "
        f"[{b30['admN_dphase_ci'][0]:+.0f},{b30['admN_dphase_ci'][1]:+.0f}]")
    return r
# ---------------- spring-neap: envelope regression and bins ----------------
NUIS = harm_cols(["K1", "O1", "Q1", "S1", "S3"])
def env_design(key, m, extra_nuis=(), ctrl=()):
    E, th = ENV[key]["E"], ENV[key]["th"]; e = E / E[m].mean() - 1; cth, sth = np.cos(th), np.sin(th)
    cols = [np.ones(NH), cth, sth, e * cth, e * sth] + NUIS + [np.cos(2 * th), np.sin(2 * th)] + harm_cols(extra_nuis)
    for v in ctrl: cols += [v * cth, v * sth]
    return np.array(cols).T.copy(), e
EXTRA = {"full": (), "M2+S2": ("N2",), "M2+N2": ("S2",)}
def gamma_of(b): P = complex(b[1], -b[2]); Q = complex(b[3], -b[4]); g = Q / P; return g.real, g.imag, P
def env_test(sta, key, lo, hi, ctrl_names=(), nb=NB, L=720, nsur=NS):
    s = SER[sta]; y, m = s["y"], s["m"]
    mm = np.zeros(NH, bool); mm[lo:hi] = m[lo:hi]
    ctrl = []
    for cn in ctrl_names:
        if cn == "linestrength": ctrl.append(zs(s["u"], mm))
        if cn == "swell": ctrl.append(zs(lhs_slow, mm))
    X, e = env_design(key, mm, EXTRA[key], ctrl)
    ii = np.flatnonzero(mm); b = solve(X[ii], y[ii]); g, gq, P = gamma_of(b)
    gb = []; DS = DayStats(X, [y], mm, lo, hi)
    for _ in range(nb):
        gb.append(gamma_of(DS.boot(L // 24)[:, 0])[:2])
    gb = np.array(gb)
    # H0 surrogates (gamma = 0): constant-amplitude fitted model + residual moved in random-start 15-d blocks / phase-randomised
    b0 = b.copy(); b0[3:5] = 0; yhat0 = X @ b0; resid = np.zeros(NH); resid[ii] = y[ii] - X[ii] @ b
    g0 = []
    for _ in range(nsur):
        idx = bidx(lo, hi, 360); mb = mm[idx]; dest = np.arange(lo, hi)[mb]; ys = yhat0[dest] + resid[idx][mb]
        g0.append(gamma_of(solve(X[dest], ys))[0])
    g0 = np.array(g0)
    b1h = b.copy(); b1h[3], b1h[4] = b[1], b[2]; yhat1 = X @ b1h; gh1 = []   # injection under H1 (exactly proportional, Q=P) to check estimator bias
    for _ in range(max(50, nsur // 10)):
        idx = bidx(lo, hi, 360); mb = mm[idx]; dest = np.arange(lo, hi)[mb]; gh1.append(gamma_of(solve(X[dest], yhat1[dest] + resid[idx][mb]))[0])
    gh1 = np.array(gh1); g1 = []
    for ys in surrogates(resid, mm, nsur // 4):
        g1.append(gamma_of(solve(X[ii], yhat0[ii] + ys[ii]))[0])
    g1 = np.array(g1)
    r = dict(gamma=g, gamma_quad=gq, ci=list(np.percentile(gb[:, 0], [2.5, 97.5])), sd=float(gb[:, 0].std()), quad_ci=list(np.percentile(gb[:, 1], [2.5, 97.5])),
             p_gamma_le0_boot=float((np.sum(gb[:, 0] <= 0) + 1) / (nb + 1)), p_gamma_ge1_boot=float((np.sum(gb[:, 0] >= 1) + 1) / (nb + 1)),
             p_null_block=float((np.sum(g0 >= g) + 1) / (nsur + 1)), p_null_phase=float((np.sum(g1 >= g) + 1) / (len(g1) + 1)),
             null_block_sd=float(g0.std()), h1_mean=float(gh1.mean()), h1_sd=float(gh1.std()), A=abs(P), lag=lagh(P, 1.0), n=int(len(ii)), env_range=(float(np.percentile(e[ii], 5)), float(np.percentile(e[ii], 95))))
    log(f"  {sta:5s} {key:6s} {'+'.join(ctrl_names) or 'no ctrl':22s} gamma={g:+.2f} [{r['ci'][0]:+.2f},{r['ci'][1]:+.2f}] (quad {gq:+.2f}) "
        f"P(H0 gamma=0): block-surr p={r['p_null_block']:.4f}, phase-surr p={r['p_null_phase']:.4f}; boot P(gamma>=1)={r['p_gamma_ge1_boot']:.3f}; "
        f"H1-injection gamma {r['h1_mean']:.2f}±{r['h1_sd']:.2f}; A={abs(P):.3f} dB @ +{r['lag']:.2f} h; e 5-95% {r['env_range'][0]:+.2f}..{r['env_range'][1]:+.2f}")
    return r
def bins_test(sta, key, lo, hi, nq, nb=NB, L=720):
    s = SER[sta]; y, m = s["y"], s["m"]; mm = np.zeros(NH, bool); mm[lo:hi] = m[lo:hi]
    E, th = ENV[key]["E"], ENV[key]["th"]
    edges = np.quantile(E[mm], np.linspace(0, 1, nq + 1)); q = np.clip(np.digitize(E, edges[1:-1]), 0, nq - 1)
    Xb = np.array([np.ones(NH), np.cos(th), np.sin(th)] + NUIS + [np.cos(2 * th), np.sin(2 * th)] + harm_cols(EXTRA[key])).T.copy()
    def one(ii):
        out = []
        for k in range(nq):
            jj = ii[q[ii] == k]; b = solve(Xb[jj], y[jj]); out.append(complex(b[1], -b[2]))
        return np.array(out)
    ii = np.flatnonzero(mm); Pk = one(ii); Xa = env_design(key, mm, EXTRA[key])[0]; Pall = gamma_of(solve(Xa[ii], y[ii]))[2]
    u = Pall / abs(Pall); inph = (Pk * np.conj(u)).real
    Ek = np.array([E[ii][q[ii] == k].mean() for k in range(nq)])
    DSk = [DayStats(Xb, [y], mm & (q == k), lo, hi) for k in range(nq)]
    B = []
    for _ in range(nb):   # same block starts for all bins (state of R duplicated per bin)
        st = R.bit_generator.state; row = []
        for k in range(nq):
            R.bit_generator.state = st; bb = DSk[k].boot(L // 24)[:, 0]; row.append(complex(bb[1], -bb[2]))
        B.append(row)
    B = np.array(B); inB = (B * np.conj(u)).real; sd = inB.std(axis=0)
    lagk = ((-np.angle(Pk)) % (2 * np.pi)) / WM2; lagB = ((-np.angle(B)) % (2 * np.pi)) / WM2
    lagB = (lagB - lagk + 6.21) % 12.42 - 6.21 + lagk
    # hypotheses: proportional A_k = a*E_k (1 free param), constant A_k = c (1 free param); weighted LS with bootstrap covariance
    C = np.cov(inB.T); Ci = np.linalg.inv(C)
    def wls(Xh):
        beta = np.linalg.solve(Xh.T @ Ci @ Xh, Xh.T @ Ci @ inph); rr = inph - Xh @ beta; return beta, float(rr @ Ci @ rr)
    bp, chp = wls(Ek[:, None]); bc, chc = wls(np.ones((nq, 1))); bl, chl = wls(np.c_[np.ones(nq), Ek])
    slope_rel = bl[1] * Ek.mean() / (bl[0] + bl[1] * Ek.mean())   # d ln A / d ln E at mean envelope (gamma-like)
    r = dict(Ek=Ek.tolist(), inphase=inph.tolist(), sd=sd.tolist(), amp=np.abs(Pk).tolist(), lag=lagk.tolist(), lag_sd=lagB.std(axis=0).tolist(),
             chi2_prop=chp, chi2_const=chc, p_prop=float(stats.chi2.sf(chp, nq - 1)), p_const=float(stats.chi2.sf(chc, nq - 1)),
             spring_over_neap=float(inph[-1] / inph[0]) if inph[0] > 0 else float("nan"), E_ratio=float(Ek[-1] / Ek[0]), gamma_lin=float(slope_rel),
             ratio_boot_ci=list(np.percentile(inB[:, -1] / np.where(inB[:, 0] > 0.01, inB[:, 0], np.nan), [2.5, 97.5])) if True else None)
    log(f"  {sta:5s} {key:6s} {nq} bins: E_k(m)=" + ",".join(f"{v:.2f}" for v in Ek) + " | in-phase A_k(dB)=" + ",".join(f"{a:.3f}±{s_:.3f}" for a, s_ in zip(inph, sd))
        + " | lag_k(h)=" + ",".join(f"{l:.1f}" for l in lagk)
        + f" | top/bottom {r['spring_over_neap']:.2f} (E ratio {r['E_ratio']:.2f}); chi2 prop {chp:.1f} (p={r['p_prop']:.3f}) vs const {chc:.1f} (p={r['p_const']:.3g}) [{nq-1} dof]; dlnA/dlnE {slope_rel:.2f}")
    return r
# =====================================================================================
if __name__ == "__main__":
    only = os.environ.get("ONLY", "")
    # ---- 1. spring-neap at EDA (full span), TAM (full span), then all stations common period
    log(f"\n==== 1. SPRING-NEAP / AMPLITUDE-SCALING TESTS (LMB, dB) {el()}")
    log("gamma = Re(Q/P) in y = Re[(P + Q e(t)) exp(i theta)], e = E/mean(E) - 1:  gamma=1 proportional to tidal range, gamma=0 constant amplitude")
    SN = {}
    spans = {}
    for sta in STA:
        lo, hi = span(SER[sta]["m"]); spans[sta] = (lo, hi)
    for sta, (lo, hi) in [("EDA", spans["EDA"])] + ([("TAM", spans["TAM"])] if "TAM" in STA else []):
        SN[sta] = {}
        for key in ["full", "M2+S2", "M2+N2"]:
            SN[sta][key] = env_test(sta, key, lo, hi)
        for key in ["full", "M2+N2"]:
            SN[sta][key + "+ctrl"] = env_test(sta, key, lo, hi, ("linestrength", "swell"))
        for key, nq in [("full", 3), ("full", 5), ("M2+S2", 5), ("M2+N2", 3), ("M2+N2", 5)]:
            SN[sta][f"bins_{key}_{nq}"] = bins_test(sta, key, lo, hi, nq)
        # confound check: mean slow line strength / swell / detection by envelope tercile
        mm = SER[sta]["m"].copy(); mm[:lo] = False; mm[hi:] = False
        E = ENV["full"]["E"]; edges = np.quantile(E[mm], [1 / 3, 2 / 3]); q = np.digitize(E, edges)
        log(f"  {sta} confounds by full-envelope tercile (neap->spring): mean 5-d log10 SNR " + ", ".join(f"{np.nanmean(SER[sta]['u'][mm & (q == k)]):.3f}" for k in range(3))
            + "; mean ERA5 Hs " + ", ".join(f"{np.nanmean(hsg[mm & (q == k)]):.3f} m" for k in range(3))
            + "; detection rate " + ", ".join(f"{np.nanmean(SER[sta]['det'][mm & (q == k)]):.3f}" for k in range(3))
            + f"; corr(e, slow lineSNR) {np.corrcoef(E[mm & np.isfinite(SER[sta]['u'])], SER[sta]['u'][mm & np.isfinite(SER[sta]['u'])])[0,1]:+.3f}")
    log(f"  -- common period 2022-03..2024-02, all stations {el()}")
    for sta in STA:
        lo, hi = span(SER[sta]["m"], k0, k1)
        SN.setdefault(sta, {})
        SN[sta]["common_full"] = env_test(sta, "full", lo, hi, nsur=NS // 4)
        SN[sta]["common_M2+N2"] = env_test(sta, "M2+N2", lo, hi, nsur=NS // 4)
    # combined gamma (inverse-variance; EDA full + TAM full counted once each; other stations common period)
    def comb(keyE, keyO):
        vals = [(SN["EDA"][keyE]["gamma"], SN["EDA"][keyE]["sd"])] + ([(SN["TAM"][keyE]["gamma"], SN["TAM"][keyE]["sd"])] if "TAM" in SN else [])
        vals += [(SN[s][keyO]["gamma"], SN[s][keyO]["sd"]) for s in STA if s not in ("EDA", "TAM")]
        w = np.array([1 / sd ** 2 for _, sd in vals]); g = np.array([v for v, _ in vals]); return float((w * g).sum() / w.sum()), float(1 / np.sqrt(w.sum()))
    for kE, kO in [("full", "common_full"), ("M2+N2", "common_M2+N2")]:
        g, sg = comb(kE, kO); SN[f"combined_{kE}"] = (g, sg)
        log(f"  combined gamma ({kE}; inverse-variance, treats stations as independent -> optimistic): {g:+.2f} ± {sg:.2f}")
    OUT["springneap"] = SN
    # ---- 2. bootstrap + conservative nulls per station
    log(f"\n==== 2. BLOCK BOOTSTRAP AND CONSERVATIVE SIGNIFICANCE (LMB M2) {el()}")
    HB = {}
    HB["EDA_full"] = harmonic_block("EDA", *spans["EDA"], "EDA 2019-05..2026-09")
    if "TAM" in STA: HB["TAM_full"] = harmonic_block("TAM", *spans["TAM"], "TAM 2022-03..2026-09")
    for sta in STA:
        lo, hi = span(SER[sta]["m"], k0, k1); HB[sta + "_common"] = harmonic_block(sta, lo, hi, f"{sta} common 2022-03..2024-02")
    # swell covariates / detrending sensitivity at EDA
    lo, hi = spans["EDA"]; s = SER["EDA"]
    bsw = mainfit(s["y"], s["m"], lo, hi, extra=np.c_[lhs_hp, tp_hp]); Psw = cplx(bsw, IH["M2"])
    W["K2"] = 2.0054758; WK = np.array([np.cos(2 * np.pi * W["K2"] * tg_d), np.sin(2 * np.pi * W["K2"] * tg_d)]).T
    bk = mainfit(s["y"], s["m"], lo, hi, extra=WK); PK2 = complex(bk[-2], -bk[-1]); PM2k = cplx(bk, IH["M2"]); PS2k = cplx(bk, IH["S2"])
    bt_k = solve(np.c_[XH, WK], tide_g - tide_g.mean()); TK2 = complex(bt_k[-2], -bt_k[-1]); TM2k = cplx(bt_k, IH["M2"])
    XK = np.c_[XH, WK]; kb = []
    DSK = DayStats(XK, [s["y"]], s["m"], lo, hi)
    for _ in range(NB):
        bb = DSK.boot(30)[:, 0]; kb.append([complex(bb[-2], -bb[-1]), cplx(bb, IH["M2"])])
    kb = np.array(kb); admK = (kb[:, 0] / TK2) / (kb[:, 1] / TM2k); admK0 = (PK2 / TK2) / (PM2k / TM2k)
    zK = np.array([PK2.real, PK2.imag]); CK = np.cov(np.c_[kb[:, 0].real, kb[:, 0].imag].T); dK = float(zK @ np.linalg.solve(CK, zK))
    log(f"  EDA with K2 added (lunisolar; separable from S2 over 7.4 yr): K2 {abs(PK2):.3f} dB [{np.percentile(np.abs(kb[:,0]),2.5):.3f},{np.percentile(np.abs(kb[:,0]),97.5):.3f}] "
        f"(p vs 0 from bootstrap covariance {stats.chi2.sf(dK, 2):.3f}); gauge K2/M2 {abs(TK2)/abs(TM2k):.3f} -> expected if proportional {abs(PM2k)*abs(TK2)/abs(TM2k):.3f} dB; "
        f"K2 admittance rel. M2 {abs(admK0):.2f} [{np.percentile(np.abs(admK),2.5):.2f},{np.percentile(np.abs(admK),97.5):.2f}], extra lag {-np.degrees(np.angle(admK0)):+.0f} deg; S2 then {abs(PS2k):.3f} dB, M2 {abs(PM2k):.3f} dB")
    OUT["K2"] = dict(A=abs(PK2), adm=abs(admK0), adm_ci=list(np.percentile(np.abs(admK), [2.5, 97.5])), p=float(stats.chi2.sf(dK, 2)))
    log(f"  EDA with additive ERA5 covariates (72-h high-passed log Hs, Tp): M2 {abs(Psw):.3f} dB at +{lag_nm(Psw,'M2'):.2f} h")
    # ---- joint multi-station bootstrap (same blocks), common period
    log(f"\n  joint (same-block) bootstrap, common period, 30-d blocks {el()}")
    lo, hi = k0, k1; Js = {sta: [] for sta in STA}; JB = {sta: {"b1": [], "b2": []} for sta in STA}
    obs = {}
    for sta in STA:
        s = SER[sta]; ii = np.arange(lo, hi); ii = ii[s["m"][ii]]
        obs[sta] = {k: cplx(solve(XH[ii], s[k][ii]), IH["M2"]) for k in ["y", "b1", "b2"]}
    DSJ = {sta: DayStats(XH, [SER[sta][k] for k in ["y", "b1", "b2"]], SER[sta]["m"], lo, hi) for sta in STA}
    for _ in range(NB):
        st = R.bit_generator.state
        for sta in STA:   # identical block starts for every station
            R.bit_generator.state = st; bb = DSJ[sta].boot(30)
            for j, k in enumerate(["y", "b1", "b2"]): (Js[sta] if k == "y" else JB[sta][k]).append(cplx(bb[:, j], IH["M2"]))
    def lag_arr(z): return ((np.angle(TC["M2"]) - np.angle(z)) % (2 * np.pi)) / WM2
    def wrap_near(a, c): return (a - c + 6.21) % 12.42 - 6.21 + c
    J = {}
    for sta in STA:
        z = np.array(Js[sta]); l0 = lag_arr(obs[sta]["y"]); lb = wrap_near(lag_arr(z), l0)
        J[sta] = dict(lag=float(l0), lag_ci=list(np.percentile(lb, [2.5, 97.5])), lag_sd=float(lb.std()), A=abs(obs[sta]["y"]), A_ci=list(np.percentile(np.abs(z), [2.5, 97.5])), zb=z, lb=lb)
        for k in ["b1", "b2"]:
            zk = np.array(JB[sta][k]); lk = lag_arr(obs[sta][k]); J[sta][k] = dict(A=abs(obs[sta][k]), lag=float(lk), A_ci=list(np.percentile(np.abs(zk), [2.5, 97.5])),
                                                                                 lag_ci=list(np.percentile(wrap_near(lag_arr(zk), lk), [2.5, 97.5])))
        log(f"  {sta:5s} LMB M2 {J[sta]['A']:.3f} dB [{J[sta]['A_ci'][0]:.3f},{J[sta]['A_ci'][1]:.3f}] lag +{J[sta]['lag']:.2f} h [{J[sta]['lag_ci'][0]:.2f},{J[sta]['lag_ci'][1]:.2f}]"
            f" | bg20-24 {J[sta]['b1']['A']:.3f} dB +{J[sta]['b1']['lag']:.1f} h [{J[sta]['b1']['lag_ci'][0]:.1f},{J[sta]['b1']['lag_ci'][1]:.1f}]"
            f" | bg29-34 {J[sta]['b2']['A']:.3f} dB +{J[sta]['b2']['lag']:.1f} h [{J[sta]['b2']['lag_ci'][0]:.1f},{J[sta]['b2']['lag_ci'][1]:.1f}]")
    # combined phase: inverse-variance weighted circular mean of lags (weights from joint bootstrap phase SD)
    def combined(stas):
        w = np.array([1 / J[s]["lag_sd"] ** 2 for s in stas]); w /= w.sum()
        def cm(lags): return (np.angle(np.sum(w[:, None] * np.exp(1j * WM2 * np.array(lags)), axis=0)) % (2 * np.pi)) / WM2
        c_obs = float(cm([[J[s]["lag"]] for s in stas])[0]); cb = wrap_near(cm([J[s]["lb"] for s in stas]), c_obs)
        Q = float(sum((1 / J[s]["lag_sd"] ** 2) * (wrap_near(J[s]["lag"], c_obs) - c_obs) ** 2 for s in stas))
        return dict(stations=stas, lag=c_obs, ci=list(np.percentile(cb, [2.5, 97.5])), sd=float(cb.std()), Q=Q, dof=len(stas) - 1, p_homog=float(stats.chi2.sf(Q, len(stas) - 1)),
                    weights=dict(zip(stas, w.round(3).tolist())))
    J["combined_all"] = combined(STA); J["combined_noEDA"] = combined([s for s in STA if s != "EDA"])
    J["combined_orig4"] = combined([s for s in ["EDA", "TAM", "MBAR", "SHEL"] if s in STA])
    sig = [s for s in STA if max(HB[s + "_common"]["nulls"][k]["p"] for k in HB[s + "_common"]["nulls"]) < 0.05]
    J["combined_significant"] = combined(sig); J["combined_significant_noEDA"] = combined([s for s in sig if s != "EDA"])
    log(f"  stations whose common-period M2 passes all three nulls at p<0.05: {sig}")
    for k in ["combined_orig4", "combined_all", "combined_noEDA", "combined_significant", "combined_significant_noEDA"]:
        v = J[k]; log(f"  {k}: mean lag +{v['lag']:.2f} h [95% {v['ci'][0]:.2f},{v['ci'][1]:.2f}] (joint-bootstrap); homogeneity Q={v['Q']:.2f}, dof {v['dof']}, p={v['p_homog']:.2f}; weights {v['weights']}")
    OUT["harmonic"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("M2b",)} for k, v in HB.items()}
    for k in OUT["harmonic"]:
        for L in ("boot15d", "boot30d"):
            if L in OUT["harmonic"][k]: OUT["harmonic"][k][L] = {kk: vv for kk, vv in OUT["harmonic"][k][L].items() if kk != "M2b"}
    OUT["joint"] = {k: ({kk: vv for kk, vv in v.items() if kk not in ("zb", "lb")} if isinstance(v, dict) else v) for k, v in J.items()}
    # ---- 4. leave-one-year-out, single-year (EDA)
    log(f"\n==== 4. LEAVE-ONE-YEAR-OUT / SINGLE-YEAR (EDA LMB M2) {el()}")
    s = SER["EDA"]; yrs = (grid_t.astype("datetime64[s]").astype("datetime64[Y]").astype(int) + 1970)
    LO = {}
    for yv in range(2019, 2027):
        for mode in ["drop", "only"]:
            mm = s["m"] & ((yrs != yv) if mode == "drop" else (yrs == yv))
            if mm.sum() < 500: continue
            ii = np.flatnonzero(mm); b = solve(XH[ii], s["y"][ii]); P = cplx(b, IH["M2"]); LO[f"{mode}{yv}"] = (abs(P), lag_nm(P, "M2"), int(mm.sum()))
        log(f"  {yv}: drop -> " + (f"{LO[f'drop{yv}'][0]:.3f} dB +{LO[f'drop{yv}'][1]:.2f} h" if f"drop{yv}" in LO else "n/a")
            + "; only -> " + (f"{LO[f'only{yv}'][0]:.3f} dB +{LO[f'only{yv}'][1]:.2f} h (n={LO[f'only{yv}'][2]})" if f"only{yv}" in LO else "n/a"))
    d = np.array([v[1] for k, v in LO.items() if k.startswith("drop")]); a = np.array([v[0] for k, v in LO.items() if k.startswith("drop")])
    o = np.array([v[1] for k, v in LO.items() if k.startswith("only")]); oa = np.array([v[0] for k, v in LO.items() if k.startswith("only")])
    log(f"  LOYO range: amplitude {a.min():.3f}-{a.max():.3f} dB, lag {d.min():.2f}-{d.max():.2f} h; single years: amplitude {oa.min():.3f}-{oa.max():.3f} dB, lag {o.min():.2f}-{o.max():.2f} h")
    OUT["loyo"] = LO
    # ---------------- figures ----------------
    fig, axs = plt.subplots(2, 3, figsize=(15, 8.5))
    def binpanel(ax, sta, key, nq, title):
        r = SN[sta][f"bins_{key}_{nq}"]; Ek = np.array(r["Ek"]); A = np.array(r["inphase"]); sd = np.array(r["sd"])
        ax.errorbar(Ek, A, yerr=1.96 * sd, fmt="o", capsize=3, color="k", label="in-phase amplitude ±95% (30-d block bootstrap)")
        xx = np.linspace(0, Ek.max() * 1.1, 10); Abar = np.average(A, weights=1 / sd ** 2)
        a_p = np.sum(A * Ek / sd ** 2) / np.sum(Ek ** 2 / sd ** 2)
        ax.plot(xx, a_p * xx, "C3-", label=f"∝ tidal range (χ²={r['chi2_prop']:.1f}, p={r['p_prop']:.2f})")
        ax.axhline(Abar, color="C0", ls="--", label=f"constant (χ²={r['chi2_const']:.1f}, p={r['p_const']:.2g})")
        ax.set_xlim(0, Ek.max() * 1.1); ax.set_ylim(bottom=min(0, (A - 2 * sd).min())); ax.set_xlabel(f"mean semidiurnal envelope in bin (m) [{key}]"); ax.set_ylabel("M2-band response (dB)")
        ax.set_title(title, fontsize=9); ax.legend(fontsize=7, loc="upper left")
    binpanel(axs[0, 0], "EDA", "full", 5, "EDA 2019-26: quintiles of spring-neap+perigee envelope")
    binpanel(axs[0, 1], "EDA", "M2+N2", 5, "EDA: quintiles of lunar-only (M2+N2, perigean) envelope")
    if "TAM" in SN: binpanel(axs[0, 2], "TAM", "full", 5, "TAM 2022-26: quintiles of full envelope")
    ax = axs[1, 0]
    for sta, col in [("EDA", "k"), ("TAM", "C1")]:
        if sta not in SN: continue
        r = SN[sta]["bins_full_5"]; ax.errorbar(np.array(r["Ek"]), r["lag"], yerr=1.96 * np.array(r["lag_sd"]), fmt="o-", color=col, capsize=3, label=sta)
    ax.set_xlabel("envelope (m)"); ax.set_ylabel("lag after local semidiurnal HW (h)"); ax.set_title("lag by envelope quintile (should be constant)", fontsize=9); ax.legend(fontsize=7); ax.set_ylim(0, 4)
    ax = axs[1, 1]; rows = []
    for sta in STA:
        for key, lab in [("full", "full env"), ("M2+N2", "lunar env")]:
            if sta in ("EDA", "TAM"): r = SN[sta][key]; tag = "full span"
            else: r = SN[sta]["common_" + key]; tag = "2022-24"
            rows.append((f"{sta} {lab} ({tag})", r["gamma"], r["ci"]))
    for i, (lab, g, ci) in enumerate(rows):
        ax.errorbar(g, i, xerr=[[g - ci[0]], [ci[1] - g]], fmt="o", color="C3" if "lunar" in lab else "k", capsize=2)
    ax.axvline(0, color="C0", ls="--", lw=0.8); ax.axvline(1, color="C3", ls="--", lw=0.8)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=6); ax.set_xlim(-4, 5)
    ax.set_xlabel("gamma (0 = constant amplitude, 1 = proportional to tidal range)"); ax.set_title("envelope-scaling index, 95% block-bootstrap CI", fontsize=9)
    ax = axs[1, 2]
    for i, k in enumerate([k for k in HB if k.endswith("_common") or k.endswith("_full")]):
        r = HB[k]; b = r["boot30d"]
        ax.errorbar(r["S2M2"], i, xerr=[[r["S2M2"] - b["S2M2_ci"][0]], [b["S2M2_ci"][1] - r["S2M2"]]], fmt="o", color="k", capsize=2)
        ax.errorbar(r["N2M2"], i + 0.25, xerr=[[r["N2M2"] - b["N2M2_ci"][0]], [b["N2M2_ci"][1] - r["N2M2"]]], fmt="s", color="C2", capsize=2)
    ax.axvline(abs(TC["S2"]) / abs(TC["M2"]), color="k", ls="--", lw=0.8, label="gauge S2/M2"); ax.axvline(EQ["S2"] / EQ["M2"], color="k", ls=":", lw=0.8, label="equilibrium S2/M2")
    ax.axvline(abs(TC["N2"]) / abs(TC["M2"]), color="C2", ls="--", lw=0.8, label="gauge N2/M2"); ax.axvline(EQ["N2"] / EQ["M2"], color="C2", ls=":", lw=0.8, label="equilibrium N2/M2")
    kk = [k for k in HB if k.endswith("_common") or k.endswith("_full")]
    ax.set_yticks(range(len(kk))); ax.set_yticklabels(kk, fontsize=6); ax.set_xlim(0, 1.5); ax.legend(fontsize=6); ax.set_xlabel("response amplitude ratio (circles S2/M2, squares N2/M2)")
    ax.set_title("constituent ratios of the LMB response, 95% CI", fontsize=9)
    fig.suptitle("Spring-neap tests of the M2 modulation of the 26 s line (line minus background, dB)", fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(D, "fig10_springneap.png"), dpi=120); plt.close(fig)
    f8 = os.path.join(D, "fig8_multistation_M2_phasors.png")
    if os.path.exists(f8) and not os.path.exists(f8.replace(".png", "_v1.png")): shutil.copy(f8, f8.replace(".png", "_v1.png"))
    fig = plt.figure(figsize=(7, 7)); ax = fig.add_subplot(111, projection="polar")
    for i, sta in enumerate(STA):
        col = f"C{i}"; j = J[sta]; th = j["lag"] / 12.42 * 2 * np.pi
        ax.plot(th, j["A"], "o", color=col, ms=7, label=f"{sta} line−bg ({META[sta].get('dist_km', 0):.0f} km, az {META[sta].get('az', 0):.0f}°)")
        tt = np.linspace(j["lag_ci"][0], j["lag_ci"][1], 30) / 12.42 * 2 * np.pi; ax.plot(tt, np.full(30, j["A"]), "-", color=col, lw=2)
        ax.plot([th, th], j["A_ci"], "-", color=col, lw=1)
        for k, mk in [("b1", "^"), ("b2", "v")]:
            ax.plot(j[k]["lag"] / 12.42 * 2 * np.pi, j[k]["A"], mk, mfc="none", color=col, ms=6)
    cj = J["combined_all"]; tt = np.linspace(cj["ci"][0], cj["ci"][1], 30) / 12.42 * 2 * np.pi
    ax.plot(tt, np.full(30, 0.62), "k-", lw=3); ax.plot(cj["lag"] / 12.42 * 2 * np.pi, 0.62, "k*", ms=12, label=f"weighted mean lag +{cj['lag']:.2f} h [{cj['ci'][0]:.2f},{cj['ci'][1]:.2f}]")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1); ax.set_rlim(0, 0.66)
    ax.set_xticks(np.linspace(0, 2 * np.pi, 12, endpoint=False)); ax.set_xticklabels([f"{h:.1f}h" for h in np.linspace(0, 12.42, 12, endpoint=False)])
    ax.set_title("M2 modulation, 2022-03..2024-02, angle = lag after M2 HW at Limbe, radius = dB\nfilled: line minus background (95% 30-d block-bootstrap arcs); open ▲▼: 20-24 s / 29-34 s background", fontsize=8)
    ax.legend(fontsize=6.5, loc="lower left", bbox_to_anchor=(-0.18, -0.2)); fig.tight_layout(); fig.savefig(f8, dpi=120); plt.close(fig)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    yy_ = [yv for yv in range(2019, 2027) if f"drop{yv}" in LO]
    ax[0].plot(yy_, [LO[f"drop{yv}"][0] for yv in yy_], "o-", label="leave year out"); ax[0].plot([yv for yv in yy_ if f"only{yv}" in LO], [LO[f"only{yv}"][0] for yv in yy_ if f"only{yv}" in LO], "s--", label="single year")
    ax[0].set_ylabel("M2 amplitude (dB)"); ax[0].legend(fontsize=8); ax[0].set_ylim(0, None)
    ax[1].plot(yy_, [LO[f"drop{yv}"][1] for yv in yy_], "o-"); ax[1].plot([yv for yv in yy_ if f"only{yv}" in LO], [LO[f"only{yv}"][1] for yv in yy_ if f"only{yv}" in LO], "s--")
    ax[1].set_ylabel("lag after M2 HW (h)"); ax[1].set_ylim(0, 4)
    fig.suptitle("EDA line minus background: leave-one-year-out and single-year M2 phasor"); fig.tight_layout(); fig.savefig(os.path.join(D, "fig11_loyo.png"), dpi=120); plt.close(fig)
    json.dump(js(OUT), open(os.path.join(D, "robustness.json"), "w"), indent=1, default=lambda o: str(o))
    open(os.path.join(D, "robustness.txt"), "w").write("\n".join(TL.LOG) + "\n"); log(f"done {el()}")
