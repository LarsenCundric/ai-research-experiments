"""Polite sequential month-by-month download of G.EDA.00.LHZ (GEOSCOPE, Edea, Cameroon)
from the RESIF FDSN dataselect service. One request at a time, skips existing files."""
import os, sys, time, urllib.request, datetime as dt
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
URL = ("https://ws.resif.fr/fdsnws/dataselect/1/query?net=G&sta=EDA&loc=00&cha=LHZ"
       "&starttime={s}&endtime={e}&nodata=404")
def months(y0, m0, y1, m1):
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
if __name__ == "__main__":
    # usage: download.py [NET STA LOC CHA Y0 M0 Y1 M1]   default: G EDA 00 LHZ 2019 5 2026 9
    a = sys.argv[1:] or ["G", "EDA", "00", "LHZ", "2019", "5", "2026", "9"]
    net, sta, loc, cha = a[:4]; y0, m0, y1, m1 = map(int, a[4:8])
    if sta != "EDA": OUT = OUT + "_" + sta
    URL = URL.replace("net=G&sta=EDA&loc=00&cha=LHZ", f"net={net}&sta={sta}&loc={loc}&cha={cha}")
    if net in ("II", "IU"):   # GSN stations: EarthScope (IRIS) FDSN
        URL = URL.replace("https://ws.resif.fr/", "https://service.earthscope.org/")
    elif net == "GE":         # GEOFON
        URL = URL.replace("https://ws.resif.fr/", "https://geofon.gfz.de/")
    os.makedirs(OUT, exist_ok=True)
    for y, m in months(y0, m0, y1, m1):
        fn = os.path.join(OUT, f"{net}.{sta}.{loc}.{cha}.{y}-{m:02d}.mseed")
        if os.path.exists(fn) and os.path.getsize(fn) > 0:
            continue
        s = dt.datetime(y, m, 1); e = dt.datetime(y + (m == 12), m % 12 + 1, 1)
        url = URL.format(s=s.isoformat(), e=e.isoformat())
        for attempt in range(3):
            try:
                raw = urllib.request.urlopen(url, timeout=300).read()
                open(fn + ".part", "wb").write(raw); os.replace(fn + ".part", fn)
                print(y, m, f"{len(raw)/1e6:.2f} MB", flush=True); break
            except urllib.error.HTTPError as ex:
                if ex.code == 404:
                    open(fn, "wb").close(); print(y, m, "no data", flush=True); break
                print(y, m, "HTTP", ex.code, flush=True); time.sleep(30)
            except Exception as ex:
                print(y, m, "err", ex, flush=True); time.sleep(30)
        time.sleep(3)
    print("DONE", flush=True)
