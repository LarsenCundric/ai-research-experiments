"""Spatial variation of tidal phase across the Gulf of Guinea (substitute for a gridded tide model; FES/TPXO need
registration, HAMTIDE currents are account-restricted). UTide fits to UHSLC hourly RQ gauges: Port Sonara (Limbe,
near Bioko / source region), Sao Tome (south), Lagos (west). Reports M2/S2 amplitude and Greenwich phase, and the
M2 high-water time offset relative to Port Sonara."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS"): os.environ[_v] = "1"
import numpy as np, utide
D = os.path.dirname(os.path.abspath(__file__))
G = {"Port Sonara (4.01N 9.13E)": ("port_sonara_global_hourly_rqds.csv", 4.0), "Sao Tome (0.35N 6.74E)": ("sao_tome_rqds.csv", 0.35),
     "Lagos (6.42N 3.41E)": ("lagos_rqds.csv", 6.42)}
res = {}
for name, (fn, lat) in G.items():
    d = np.genfromtxt(os.path.join(D, "tide", fn), delimiter=",", skip_header=2, dtype=None, encoding=None)
    t = np.array([np.datetime64(r[0].replace("Z", "")) for r in d]); h = np.array([float(r[1]) for r in d]); h[h < -9000] = np.nan; ok = np.isfinite(h)
    c = utide.solve(t[ok], h[ok] / 1000, lat=lat, method="ols", conf_int="linear", verbose=False, trend=False)
    i = {n: k for k, n in enumerate(c.name)}
    res[name] = {n: (c.A[i[n]], c.g[i[n]], c.g_ci[i[n]]) for n in ["M2", "S2", "K1", "O1", "M4"]}
    print(name, f"{t[ok][0]}..{t[ok][-1]}", " ".join(f"{n}: {a:.3f} m g={g:.1f}±{e:.1f}" for n, (a, g, e) in res[name].items()), flush=True)
ref = res["Port Sonara (4.01N 9.13E)"]["M2"][1]
for name in res:
    dg = (res[name]["M2"][1] - ref + 180) % 360 - 180
    print(f"{name}: M2 HW {dg/28.984:.2f} h relative to Port Sonara (positive = later)")
