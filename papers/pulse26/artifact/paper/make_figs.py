"""Paper figures: new map (Natural Earth 50m coastline, public domain) and crops of existing analysis figures."""
import json, os, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(D); F = os.path.join(D, "figs")
# ---------- map ----------
gj = json.load(open(os.path.join(P, "meta/naturalearth/ne_50m_coastline.geojson")))
lines = []
for ft in gj["features"]:
    g = ft["geometry"]; cs = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    lines += [np.array(c) for c in cs]
# station coordinates from the StationXML-derived metadata (robustness.txt)
STA = {"EDA": (3.778868, 10.153427, "G"), "TAM": (22.79149, 5.52838, "G"), "MBAR": (-0.6019, 30.7382, "II"), "SHEL": (-15.9594, -5.7455, "II"),
       "SACV": (14.9702, -23.6085, "II"), "ASCN": (-7.9327, -14.3601, "II"), "WIN": (-22.5691, 17.0915, "GE")}
SIG = {"EDA", "TAM", "MBAR", "SHEL", "SACV"}
# tide gauges: coordinates from the UHSLC ERDDAP metadata (global_hourly_rqds; queried 11 Oct 2026)
GAU = {"Port Sonara": (4.0067, 9.1267), "São Tomé": (0.3483, 6.7367), "Lagos": (6.4233, 3.4117), "Praia": (14.9167, -23.5)}
XIA = {"0.038 Hz (26 s)": (4.50, 4.25), "0.036 Hz (28 s)": (-0.50, 7.50)}   # Xia, Ni & Zeng (2013) source estimates
fig, ax = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw=dict(width_ratios=[1.25, 1]))
for a, (lo0, lo1, la0, la1) in zip(ax, [(-30, 40, -28, 30), (1, 13, -2, 8)]):
    for l in lines:
        if l[:, 0].max() < lo0 - 5 or l[:, 0].min() > lo1 + 5 or l[:, 1].max() < la0 - 5 or l[:, 1].min() > la1 + 5: continue
        a.plot(l[:, 0], l[:, 1], color="0.35", lw=0.7)
    a.set_xlim(lo0, lo1); a.set_ylim(la0, la1); a.set_aspect(1 / np.cos(np.deg2rad((la0 + la1) / 2))); a.grid(color="0.85", lw=0.5)
    a.set_xlabel("longitude (°E)"); a.set_ylabel("latitude (°N)")
a = ax[0]
for s, (la, lo, net) in STA.items():
    ok = s in SIG
    a.plot(lo, la, "^", ms=10, mfc="C3" if ok else "white", mec="k", zorder=5)
    a.annotate(f"{net}.{s}", (lo, la), xytext=(5, 5), textcoords="offset points", fontsize=8.5, fontweight="bold" if ok else "normal")
a.add_patch(plt.Rectangle((1, -2), 12, 10, fill=False, ec="C0", lw=1.2, ls="--"))
for g, (la, lo) in GAU.items():
    if g == "Praia": a.plot(lo, la, "o", ms=5, mfc="C2", mec="k", zorder=6)
a.plot([], [], "^", ms=9, mfc="C3", mec="k", ls="", label="M2 modulation detected (5 stations)")
a.plot([], [], "^", ms=9, mfc="white", mec="k", ls="", label="line rarely detected (uninformative)")
a.plot([], [], "o", ms=5, mfc="C2", mec="k", ls="", label="tide gauge (UHSLC)")
a.legend(loc="lower left", fontsize=7.5, framealpha=0.9); a.set_title("(a) Stations", fontsize=10, loc="left")
a = ax[1]
la, lo, net = STA["EDA"]; a.plot(lo, la, "^", ms=11, mfc="C3", mec="k", zorder=5); a.annotate("G.EDA", (lo, la), xytext=(6, -12), textcoords="offset points", fontsize=9, fontweight="bold")
for g, (la, lo) in GAU.items():
    if g == "Praia": continue
    a.plot(lo, la, "o", ms=7, mfc="C2", mec="k", zorder=6); a.annotate(g, (lo, la), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
for k, (la, lo) in XIA.items():
    a.plot(lo, la, "*", ms=13, mfc="gold", mec="k", zorder=6); a.annotate(f"{k}\n(Xia et al., 2013)", (lo, la), xytext=(6, -16), textcoords="offset points", fontsize=7.5)
a.text(6.6, 3.0, "Bight of\nBonny", fontsize=9, style="italic", color="C0", ha="center")
a.text(8.75, 3.55, "Bioko", fontsize=7.5, color="0.3")
a.set_title("(b) Gulf of Guinea: proposed source locations and gauges", fontsize=10, loc="left")
fig.tight_layout(); fig.savefig(os.path.join(F, "fig1a_map.png"), dpi=200); plt.close(fig)
