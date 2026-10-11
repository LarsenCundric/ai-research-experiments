"""Toy model: how much should M2 tidal depth/current changes modulate swell-to-seafloor forcing in the Bight of Bonny?
Linear (Airy) waves, exact dispersion. For an offshore wave of fixed energy flux arriving at local depth h = h0 + eta(t):
  shoaling  Ks = sqrt(cg_deep/cg(h))
  (1) bottom pressure      p_b  ~ Ks / cosh(kh)                  power ~ p_b^2
  (2) bed orbital velocity u_b  ~ Ks * w / sinh(kh)              power ~ u_b^2
  (3) primary microseism, wavy-bottom coupling (Hasselmann 1963 / Ardhuin 2018 type):
      power ~ p_b^2 * F_B(k),  bottom-elevation spectrum F_B ~ k^-n  (n = 2, 3 bracket typical seafloor roughness slopes)
  (4) depth-limited (breaking) forcing: H ~ gamma*h -> power ~ h^2 (only for waves that break; NOT the cm-high 26 s swell)
  (5) wave-current: energy ~ 1/(cg + U) (crude action/flux argument), U = tidal current along the swell direction;
      standing-wave current estimate U = a*w_tide*L/h0 (continuity; L = shelf length scale), opposing (ebb) peak at +T/4.
Modulation amplitude in dB = 10*log10(P(h0+a)/P(h0-a))/2, sign + means maximum at high water.
Observed: +0.40-0.55 dB (line minus background, EDA/TAM), peak ~1.7-2.4 h after M2 HW."""
import numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
g = 9.81; a = 0.59; wt = 2 * np.pi / (12.4206 * 3600)
def k_of(w, h):
    k = w / np.sqrt(g * h)                      # Newton on w^2 = g k tanh(kh)
    for _ in range(50): k -= (g * k * np.tanh(k * h) - w ** 2) / (g * np.tanh(k * h) + g * k * h / np.cosh(k * h) ** 2)
    return k
def cg(w, h):
    k = k_of(w, h); c = w / k; return 0.5 * c * (1 + 2 * k * h / np.sinh(2 * k * h)), k
def powers(T, h, n_list=(2, 3)):
    w = 2 * np.pi / T; cgh, k = cg(w, h); cg0 = g / (2 * w); Ks = np.sqrt(cg0 / cgh)
    pb = Ks / np.cosh(k * h); ub = Ks * w / np.sinh(k * h)
    out = {"bottom pressure": pb ** 2, "bed orbital velocity": ub ** 2}
    for n in n_list: out[f"primary microseism, F_B~k^-{n}"] = pb ** 2 * k ** (-n)
    out["depth-limited (breaking)"] = h ** 2
    return out
def mod_db(T, h0):
    p1, p2 = powers(T, h0 + a), powers(T, h0 - a); return {m: 5 * np.log10(p1[m] / p2[m]) for m in p1}
rows = []
H0 = [3, 5, 10, 20, 30, 50, 75, 100]
lines = ["Toy-model M2 power modulation (dB amplitude; + = max at high water), tide a = 0.59 m"]
for T in (14.0, 26.0):
    lines.append(f"-- swell period {T:.0f} s")
    lines.append("   h0(m) " + " | ".join(f"{m[:28]:>28s}" for m in mod_db(T, 50)))
    for h0 in H0:
        d = mod_db(T, h0); lines.append(f"   {h0:5.0f} " + " | ".join(f"{v:+28.3f}" for v in d.values()))
lines.append("-- wave-current (standing tide, U = a*w*L/h0, opposing ebb current peaks +3.1 h after HW), swell 26 s")
for L in (20e3, 50e3):
    for h0 in (10, 20, 50):
        U = a * wt * L / h0; c_g, _ = cg(2 * np.pi / 26, h0); dlnE = U / c_g
        lines.append(f"   L={L/1e3:.0f} km h0={h0:3d} m: U={U:.2f} m/s, cg={c_g:.1f} m/s -> {4.343*dlnE:.3f} dB at +3.1 h (opposing peak)")
lines.append("-- exponential (threshold-like) triggering: rate ~ exp(dp/p0), tidal bottom-pressure amplitude rho*g*a = %.1f kPa" % (1025 * g * a / 1e3))
for obs in (0.40, 0.55):
    dln = obs / 4.343; lines.append(f"   observed {obs:.2f} dB -> d ln(power) = {dln:.3f} -> p0 = {1025*g*a/dln/1e3:.0f} kPa")
lines.append("-- phasor: height term at 0 h + opposing-current term at +3.1 h reproduce the +1.7-2.0 h lag if A_current/A_height = tan(lag*2pi/12.42):")
for lag in (1.7, 2.0, 2.4):
    r = np.tan(lag / 12.42 * 2 * np.pi); lines.append(f"   lag {lag:.1f} h -> ratio {r:.2f}")
txt = "\n".join(lines); print(txt); open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.txt"), "w").write(txt + "\n")
# figure
fig, ax = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
hh = np.geomspace(3, 120, 80)
for i, T in enumerate((14.0, 26.0)):
    D = {m: [] for m in mod_db(T, 50)}
    for h0 in hh:
        for m, v in mod_db(T, h0).items(): D[m].append(v)
    for m, v in D.items(): ax[i].plot(hh, v, label=m)
    ax[i].axhspan(0.40, 0.55, color="C3", alpha=0.2, label="observed (+0.40-0.55 dB, max ~+1.7-2 h after HW)")
    ax[i].axhline(0, color="k", lw=0.6); ax[i].set_xscale("log"); ax[i].set_xlabel("mean water depth at the coupling site h0 (m)")
    ax[i].set_title(f"swell period {T:.0f} s", fontsize=9); ax[i].set_ylim(-1.5, 1.5)
ax[0].set_ylabel("M2 modulation amplitude (dB; + = max at HW)"); ax[1].legend(fontsize=6.5, loc="lower right")
fig.suptitle("Linear depth-modulation toy model vs observed M2 modulation of the 26 s line", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig9_tide_coupling_model.png"), dpi=120)
