"""Harmonic tide model for the Bight of Bonny from the UHSLC Port Sonara (Limbe, Cameroon;
4.007N 9.127E, UHSLC id 816) hourly research-quality record 2008-2011, via UTide.
Writes hourly predictions 2019-05-01..2026-10-01 (UTC) to tide/tide_pred_hourly.npz."""
import numpy as np, utide, os
D = os.path.dirname(os.path.abspath(__file__))
d = np.genfromtxt(os.path.join(D, "tide/port_sonara_global_hourly_rqds.csv"), delimiter=",",
                  skip_header=2, dtype=None, encoding=None)
t = np.array([np.datetime64(r[0].replace("Z", "")) for r in d])
h = np.array([float(r[1]) for r in d]); h[h < -9000] = np.nan
ok = np.isfinite(h)
print("gauge samples", ok.sum(), t[ok][0], t[ok][-1])
coef = utide.solve(t[ok], h[ok] / 1000.0, lat=4.0067, method="ols", conf_int="linear",
                   verbose=False, trend=False)
order = np.argsort(-coef.A)
with open(os.path.join(D, "tide/constituents.txt"), "w") as f:
    f.write("name amp_m phase_deg(Greenwich)\n")
    for i in order[:20]:
        line = f"{coef.name[i]:6s} {coef.A[i]:.4f} {coef.g[i]:7.2f}"
        print(line); f.write(line + "\n")
tp = np.arange(np.datetime64("2019-05-01T00:00"), np.datetime64("2026-10-01T00:00"), np.timedelta64(1, "h"))
rec = utide.reconstruct(tp, coef, verbose=False)
hp = rec.h - coef.mean
# also predict over the gauge period to report fit quality
rr = utide.reconstruct(t[ok], coef, verbose=False)
var_expl = 1 - np.nanvar(h[ok] / 1000 - rr.h) / np.nanvar(h[ok] / 1000)
print("variance explained by tide model over gauge record: %.3f" % var_expl)
np.savez(os.path.join(D, "tide/tide_pred_hourly.npz"), t=tp.astype("datetime64[s]").astype(np.int64), h=hp)
