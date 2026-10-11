#!/bin/bash
# Reproducible pipeline for the 26 s Gulf of Guinea microseism tidal study (single process at a time, low priority).
# Requires ../venv (obspy, numpy, scipy, matplotlib, utide). Total disk ~0.5 GB.
set -euo pipefail
cd "$(dirname "$0")"
PY="nice -n 19 ../venv/bin/python -u"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p meta tide
# 1. metadata (StationXML with response) from RESIF FDSN
[ -s meta/G.EDA.00.LHZ.xml ] || curl -s -o meta/G.EDA.00.LHZ.xml "https://ws.resif.fr/fdsnws/station/1/query?net=G&sta=EDA&loc=00&cha=LHZ&level=response"
[ -s meta/G.TAM.00.LHZ.xml ] || curl -s -o meta/G.TAM.00.LHZ.xml "https://ws.resif.fr/fdsnws/station/1/query?net=G&sta=TAM&loc=00&cha=LHZ&level=response&starttime=2022-02-01"
# 2. waveforms, month by month, one request at a time
$PY download.py G EDA 00 LHZ 2019 5 2026 9
$PY download.py G TAM 00 LHZ 2022 3 2026 9
# 3. tide: UHSLC Port Sonara (Limbe, Cameroon) hourly RQ data 2008-2011 -> UTide harmonic fit -> hourly prediction 2019-2026
[ -s tide/port_sonara_global_hourly_rqds.csv ] || curl -s -o tide/port_sonara_global_hourly_rqds.csv \
  "https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_rqds.csv?time,sea_level&uhslc_id=816"
$PY tide_model.py
# 4. swell: ERA5 ocean waves at 3N 8E via Open-Meteo (no key)
[ -s meta/era5_ocean_3N8E.json ] || curl -s -o meta/era5_ocean_3N8E.json \
  "https://marine-api.open-meteo.com/v1/marine?latitude=3.0&longitude=8.0&hourly=wave_height,wave_period,wave_peak_period&start_date=2019-05-01&end_date=2026-09-30&models=era5_ocean&timezone=GMT"
# 5. per-window features (3-h windows, 1-h step, response removed)
$PY features.py G.EDA.00.LHZ
$PY features.py G.TAM.00.LHZ
# 6. analyses
$PY analysis.py        > analysis.log 2>&1      # detection, period stability, tidal spectral tests, xcorr, phase bins, swell
$PY controls.py        > controls.log 2>&1      # line vs background, SNR-conditioning of the frequency signal, sub-periods
$PY source_vs_site.py  > source_vs_site.log 2>&1  # EDA vs TAM, background bands 20-24 s / 29-34 s, yearly stacks
# 7. paper-push additions: extra GSN stations (EarthScope FDSN), per-component tests, gauge phase spread, multistation phases
[ -s meta/II.MBAR.00.LHZ.xml ] || curl -s -o meta/II.MBAR.00.LHZ.xml "https://service.earthscope.org/fdsnws/station/1/query?net=II&sta=MBAR&loc=00&cha=LHZ&level=response&starttime=2022-01-01"
[ -s meta/II.SHEL.00.LHZ.xml ] || curl -s -o meta/II.SHEL.00.LHZ.xml "https://service.earthscope.org/fdsnws/station/1/query?net=II&sta=SHEL&loc=00&cha=LHZ&level=response&starttime=2022-01-01"
[ -s tide/sao_tome_rqds.csv ] || curl -s -o tide/sao_tome_rqds.csv "https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_rqds.csv?time,sea_level&uhslc_id=225"
[ -s tide/lagos_rqds.csv ] || curl -s -o tide/lagos_rqds.csv "https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_rqds.csv?time,sea_level&uhslc_id=233&time>=1992-01-01"
$PY download.py II MBAR 00 LHZ 2022 3 2024 2
$PY features.py II.MBAR.00.LHZ
$PY download.py II SHEL 00 LHZ 2022 3 2024 2
$PY features.py II.SHEL.00.LHZ
$PY components.py   > components.log 2>&1
$PY tide_compare.py > tide_compare.log 2>&1
$PY multistation.py > multistation.log 2>&1
# 8. robustness round (10 Oct 2026): three more stations (II.ASCN Ascension, II.SACV Cape Verde from EarthScope; GE.WIN Windhoek from GEOFON),
#    spring-neap / amplitude-scaling tests, moving-block bootstrap, block-resampled + phase-randomised nulls, joint multi-station phase,
#    leave-one-year-out. Writes robustness.txt/json, fig10_springneap.png, fig11_loyo.png and overwrites fig8 (v1 kept as fig8_..._v1.png).
[ -s meta/II.ASCN.00.LHZ.xml ] || curl -s -o meta/II.ASCN.00.LHZ.xml "https://service.earthscope.org/fdsnws/station/1/query?net=II&sta=ASCN&loc=00&cha=LHZ&level=response&starttime=2022-01-01"
[ -s meta/II.SACV.00.LHZ.xml ] || curl -s -o meta/II.SACV.00.LHZ.xml "https://service.earthscope.org/fdsnws/station/1/query?net=II&sta=SACV&loc=00&cha=LHZ&level=response&starttime=2022-01-01"
[ -s meta/GE.WIN.--.LHZ.xml ] || curl -s -o meta/GE.WIN.--.LHZ.xml "https://geofon.gfz.de/fdsnws/station/1/query?net=GE&sta=WIN&loc=--&cha=LHZ&level=response&starttime=2022-01-01"
$PY download.py II ASCN 00 LHZ 2022 3 2024 2
$PY features.py II.ASCN.00.LHZ
$PY download.py II SACV 00 LHZ 2022 3 2024 2
$PY features.py II.SACV.00.LHZ
$PY download.py GE WIN -- LHZ 2022 3 2024 2
$PY features.py GE.WIN.--.LHZ
(ulimit -v 3000000; NBOOT=2000 NSUR=1000 $PY robustness.py > robustness.log 2>&1)
$PY springneap_L2.py > springneap_L2.log 2>&1   # N2 vs L2 decomposition of the perigean-envelope test -> robustness_extra.txt

# 9. caveats round (10 Oct 2026): diagnoses of the three spring-neap caveats -> caveats.txt, caveats.json, fig12-14
(ulimit -v 3000000; timeout 7200 $PY caveats.py > caveats.log 2>&1)
(ulimit -v 3000000; timeout 3600 $PY caveats_bg.py > caveats_bg.log 2>&1)    # appends: LMB envelope term = raw line - background bands
(ulimit -v 3000000; timeout 3600 $PY caveats_bg2.py > caveats_bg2.log 2>&1)   # appends: sideband test per series (line / bg bands / LMB)

# 10. paper figures and PDFs (10 Oct 2026)
$PY paper/make_figs.py
$PY paper/figs_main.py
(cd paper && ../../tools/tectonic/tectonic main.tex && ../../tools/tectonic/tectonic si.tex)
