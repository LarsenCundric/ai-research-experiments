import json, urllib.request, urllib.parse, time
def cr(doi=None, q=None):
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi)}" if doi else "https://api.crossref.org/works?rows=2&query.bibliographic=" + urllib.parse.quote(q)
    try:
        m = json.load(urllib.request.urlopen(url, timeout=30))["message"]
    except Exception as e: return f"ERR {e}"
    items = [m] if doi else m["items"]
    out = []
    for it in items:
        au = "; ".join(f"{a.get('family','')}, {a.get('given','')}" for a in it.get("author", [])[:8])
        yr = (it.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0]
        out.append(f"DOI {it.get('DOI')} | {au} | {yr} | {(it.get('title') or [''])[0]} | {(it.get('container-title') or [''])[0]} | vol {it.get('volume')} | p {it.get('page') or it.get('article-number')}")
    return "\n   ".join(out)
Q = {
 "oliver1962": "Oliver 1962 A worldwide storm of microseisms with periods of about 27 seconds Bulletin Seismological Society of America",
 "holcomb1980": "Holcomb 1980 Microseisms: a twenty-six-second spectral line in long-period earth motion BSSA",
 "holcomb1998": "Holcomb 1998 Spectral structure in the Earth's microseismic background between 20 and 40 seconds BSSA",
 "shapiro2006": "Shapiro Ritzwoller Bensen 2006 Source location of the 26 sec microseism from cross-correlations of ambient seismic noise",
 "chen2022": "Chen Xie Ni 2022 Generation mechanism of the 26 s and 28 s tremors in the Gulf of Guinea Earth and Planetary Science Letters",
 "ardhuin2018": "Ardhuin 2018 Large-scale forces under surface gravity waves at a wavy bottom: a mechanism for the generation of primary microseisms",
 "hasselmann1963": "Hasselmann 1963 A statistical analysis of the generation of microseisms Reviews of Geophysics",
 "longuet1950": "Longuet-Higgins 1950 A theory of the origin of microseisms Philosophical Transactions",
 "rubinstein2008": "Rubinstein La Rocca Vidale Creager Wech 2008 Tidal modulation of nonvolcanic tremor Science",
 "takano2025": "Takano Poli 2025 Geophysical Research Letters e2024GL113290",
 "xia2020": "Xia Chen 2020 Geophysical Research Letters e2020GL088137",
 "bruland2023": "Bruland Hadziioannou 2023 Communications Earth & Environment 4 176",
 "beyreuther2010": "Beyreuther ObsPy: A Python Toolbox for Seismology 2010",
 "hersbach2020": "Hersbach The ERA5 global reanalysis 2020 Quarterly Journal",
 "kunsch1989": "Kunsch 1989 The jackknife and the bootstrap for general stationary observations Annals of Statistics",
 "theiler1992": "Theiler 1992 Testing for nonlinearity in time series: the method of surrogate data Physica D",
 "bernard1990": "Bernard Martel 1990 Physics of the Earth and Planetary Interiors 63 229",
 "pawlowicz2002": "Pawlowicz Beardsley Lentz 2002 Classical tidal harmonic analysis including error estimates in MATLAB using T_TIDE",
}
DOIS = {"poli2026": "10.1038/s41467-026-71541-6", "xia2013": "10.1093/gji/ggt076", "xia2024": "10.1093/gji/ggae090"}
for k, d in DOIS.items(): print(k, "\n   " + cr(doi=d)); time.sleep(1)
for k, q in Q.items(): print(k, "\n   " + cr(q=q)); time.sleep(1)
for d in ["10.18715/GEOSCOPE.G", "10.7914/SN/II", "10.14470/TR560404", "10.7289/V5V40S7W"]:
    try:
        m = json.load(urllib.request.urlopen(f"https://api.datacite.org/dois/{d}", timeout=30))["data"]["attributes"]
        print("DATACITE", d, "|", m["titles"][0]["title"], "|", m.get("publisher"), "|", m.get("publicationYear"), "|", "; ".join(c.get("name","") for c in m.get("creators", [])[:3]))
    except Exception as e:
        print("DATACITE", d, "ERR", e, "| crossref:", cr(doi=d))
    time.sleep(1)
