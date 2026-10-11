"""Stage A: per-window spectral features of the 26 s Gulf of Guinea microseism at G.EDA.00.LHZ.
Processes one month file at a time (memory << 700 MB). Run under `nice -n 19`.
Windows: 3 h long, stepped by 1 h, aligned to UTC hours, gap-free only.
Response: removed in the frequency domain using the RESIF StationXML (counts -> m/s velocity).
Output: features.npz (one row per window) + daily mean spectra + hourly spectra for 2023-07."""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"): os.environ[_v] = "1"
import glob, numpy as np
from obspy import read, read_inventory, UTCDateTime
from scipy.signal import welch
import sys
D = os.path.dirname(os.path.abspath(__file__))
# usage: features.py [NET.STA.LOC.CHA]   (default G.EDA.00.LHZ; data in data/ or data_<STA>/, response in meta/<id>.xml)
SID = sys.argv[1] if len(sys.argv) > 1 else "G.EDA.00.LHZ"
DATADIR = os.path.join(D, "data" if SID == "G.EDA.00.LHZ" else "data_" + SID.split(".")[1])
OUTFN = os.path.join(D, "features.npz" if SID == "G.EDA.00.LHZ" else "features_" + SID.split(".")[1] + ".npz")
WIN, STEP, NPAD = 10800, 3600, 2 ** 17
SEARCH = (0.0370, 0.0395)            # 25.3-27.0 s : the 26 s line (excludes 28 s line at ~0.0357 Hz)
REF = [(0.0300, 0.0340), (0.0420, 0.0460)]
LINEHW = 0.0004                      # half-width (Hz) for line-power integration
CTRL_SEARCH = (0.0300, 0.0325); CTRL_REF = [(0.0270, 0.0295), (0.0330, 0.0345)]
fpad = np.fft.rfftfreq(NPAD, 1.0); hann = np.hanning(WIN); U = (hann ** 2).sum()
fw = np.fft.rfftfreq(3600, 1.0)
inv = read_inventory(os.path.join(D, "meta", SID + ".xml"))
_rcache = {}
def resp2(t, freqs, key):
    """|R(f)|^2 (counts per m/s)^2 for the epoch containing t."""
    ch = inv.select(time=t)[0][0][0]
    k = (str(ch.start_date), key)
    if k not in _rcache:
        r = ch.response.get_evalresp_response_for_frequencies(np.maximum(freqs, 1e-4), output="VEL")
        _rcache[k] = np.abs(r) ** 2
    return _rcache[k]
mpad = (fpad >= 0.02) & (fpad <= 0.07)
fp = fpad[mpad]; mw = (fw >= 0.0) & (fw <= 0.5)
def bandmask(f, bands): return np.any([(f >= a) & (f <= b) for a, b in bands], axis=0)
ref_p = bandmask(fp, REF); s_p = bandmask(fp, [SEARCH])
ref_w = bandmask(fw, REF); s_w = bandmask(fw, [SEARCH])
c_s_w = bandmask(fw, [CTRL_SEARCH]); c_ref_w = bandmask(fw, CTRL_REF)
c_s_p = bandmask(fp, [CTRL_SEARCH]); c_ref_p = bandmask(fp, CTRL_REF)
pm1 = bandmask(fw, [(0.05, 0.08)]); sm = bandmask(fw, [(0.10, 0.30)]); lp = bandmask(fw, [(0.020, 0.030)])
f28 = bandmask(fp, [(0.0350, 0.0365)])
b2024 = bandmask(fw, [(0.0417, 0.0500)])      # 20-24 s, no 26 s energy
b2834 = bandmask(fw, [(0.0294, 0.0345)])      # 29-34 s (stops short of the 28 s line at ~35.7 mHz)
bfix = bandmask(fw, [(0.0375, 0.0386)])       # fixed band on the 26 s line (no peak picking)
b36 = (fp >= 0.0345) & (fp <= 0.0400); fp36 = fp[b36][::5]
spec_band = (fp >= 0.030) & (fp <= 0.046); dec = 5
fp_spec = fp[spec_band][::dec]
jul_band = (fp >= 0.020) & (fp <= 0.060); fp_jul = fp[jul_band][::dec]

def window_features(x, t0):
    x = x - x.mean(); n = np.arange(WIN); x = x - np.polyval(np.polyfit(n, x, 1), n)
    X = np.fft.rfft(x * hann, NPAD)[mpad]
    P = 2 * np.abs(X) ** 2 / U / resp2(t0, fp, "pad")          # one-sided PSD, (m/s)^2/Hz
    fW, PW = welch(x, fs=1.0, nperseg=3600, noverlap=1800, window="hann")
    PW = PW / resp2(t0, fW, "welch")
    # 26 s line
    i0 = np.flatnonzero(s_p); j = i0[np.argmax(P[s_p])]
    if 0 < j < len(P) - 1:   # parabolic refinement on log power
        a, b, c = np.log(P[j - 1:j + 2]); d = 0.5 * (a - c) / (a - 2 * b + c); fpk = fp[j] + d * (fp[1] - fp[0])
    else: fpk = fp[j]
    bg_p = np.median(P[ref_p]); snr_p = P[j] / bg_p
    bg_w = np.median(PW[ref_w]); snr_w = PW[s_w].max() / bg_w
    lm = np.abs(fp - fpk) <= LINEHW; df = fp[1] - fp[0]
    linepow = max(0.0, (P[lm] - bg_p).sum() * df)            # (m/s)^2
    csnr_w = PW[c_s_w].max() / np.median(PW[c_ref_w]); csnr_p = P[c_s_p].max() / np.median(P[c_ref_p])
    snr28 = P[f28].max() / bg_p
    row = (fpk, snr_w, snr_p, np.sqrt(linepow) * 1e9, bg_w, csnr_w, csnr_p, snr28,
           np.median(PW[pm1]), np.median(PW[sm]), np.median(PW[lp]), np.abs(x).max() / (1.4826 * np.median(np.abs(x)) + 1e-12),
           np.median(PW[b2024]), np.median(PW[b2834]), PW[bfix].mean(), P[j])
    return row, P

COLS = ["fpk", "snr_w", "snr_p", "amp_nms", "bg_w", "csnr_w", "csnr_p", "snr28", "pm_psd", "sm_psd", "lp_psd", "peak_mad", "bg_2024", "bg_2834", "fixband", "peak_abs_p"]
rows, times, daily = [], [], {}
jul_t, jul_P = [], []
P36 = []
files = sorted(glob.glob(os.path.join(DATADIR, SID + ".*.mseed")))
for fn in files:
    if os.path.getsize(fn) == 0: continue
    st = read(fn); st.merge(method=1); st = st.split()
    nm = 0
    for tr in st:
        fs = tr.stats.sampling_rate
        if abs(fs - 1.0) > 1e-6 or tr.stats.npts < WIN: continue
        x = tr.data.astype(np.float64); ts, te = tr.stats.starttime, tr.stats.endtime
        tk = UTCDateTime(int(np.ceil(ts.timestamp / 3600.0)) * 3600)
        while tk + WIN <= te + 1:
            i = int(round(tk - ts))
            if i + WIN > len(x): break
            row, P = window_features(x[i:i + WIN], tk)
            rows.append(row); times.append(tk.timestamp); nm += 1; P36.append(np.log10(P[b36][::5]))
            day = int(tk.timestamp // 86400)
            if day not in daily: daily[day] = [np.zeros(spec_band.sum()), 0]
            daily[day][0] += P[spec_band]; daily[day][1] += 1
            if tk.year == 2023 and tk.month == 7:
                jul_t.append(tk.timestamp); jul_P.append(P[jul_band][::dec].astype(np.float32))
            tk += STEP
        del x
    print(os.path.basename(fn), nm, "windows", flush=True)
rows = np.array(rows); times = np.array(times)
days = np.array(sorted(daily)); dspec = np.array([daily[d][0][::dec] / daily[d][1] for d in days], dtype=np.float32)
np.savez_compressed(OUTFN, logP36=np.array(P36, dtype=np.float16), f36=fp36, t=times, cols=np.array(COLS), X=rows,
                    days=days, fspec=fp_spec, dspec=dspec, jul_t=np.array(jul_t), jul_f=fp_jul, jul_P=np.array(jul_P))
print("total windows", len(times))
