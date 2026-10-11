pulse26 — code and results for "Ocean tides modulate the 26-second Gulf of Guinea microseism"
Archive built 11 Oct 2026 (America/Los_Angeles). AI-generated work produced using Grok Bot; experiment initiated
and guided by Larsen Cundric. Not independently verified; not reviewed by a domain expert.

LAYOUT (paths are relative to the archive root pulse26/)
  *.py, run_all.sh, queue*.sh   analysis scripts and the pipeline driver (run_all.sh lists every step in order)
  *.txt, *.json, *.log          result files: results, controls, source_vs_site, components, multistation, model,
                                robustness (+ robustness_extra), caveats; logs of each run
  fig*.png                      analysis figures
  features*.npz                 per-window (3-h window, 1-h step) derived features for each station (see note below)
  tide/                         UHSLC hourly gauge CSVs (Port Sonara, Sao Tome, Lagos, Praia) and the hourly tide prediction
  meta/                         StationXML (with responses), ERA5 wave series from Open-Meteo, Natural Earth coastline
  download*.log                 download logs (what was fetched, when, sizes)
  paper/                        main.tex, si.tex, refs.bib, main.pdf, si.pdf, figs/, figure scripts (make_figs.py,
                                figs_main.py), refcheck.py/refcheck.txt (reference verification), outline.md, OPEN_ITEMS.md
  NOTES_pulse26.md              the pulse26 sections of the research notebook (progress notes, verdicts, corrections)

STATION LIST (FDSN)
  G.EDA.00.LHZ   2019-05..2026-09  RESIF (ws.resif.fr)            GEOSCOPE doi:10.18715/GEOSCOPE.G
  G.TAM.00.LHZ   2022-03..2026-09  RESIF
  II.MBAR.00.LHZ, II.SHEL.00.LHZ, II.ASCN.00.LHZ, II.SACV.00.LHZ  2022-03..2024-02  EarthScope (service.earthscope.org)  doi:10.7914/SN/II
  GE.WIN.--.LHZ  2022-03..2024-02  GEOFON (geofon.gfz.de)           doi:10.14470/TR560404
  Tide gauges (UHSLC research quality, doi:10.7289/V5V40S7W): Port Sonara 816, Sao Tome 225, Lagos 233, Praia 222.

EXCLUDED (re-downloadable or not ours to redistribute)
  data/, data_TAM/, data_MBAR/, data_SHEL/, data_ASCN/, data_SACV/, data_WIN/  raw miniSEED waveforms (~1.05 GB);
      re-fetch with download.py (see run_all.sh steps 2, 7, 8)
  lit/                 copies of published papers (copyright; obtain from the publishers / DOIs in paper/refs.bib)
  features_v1.npz      superseded first-pass feature file
  backup_* folders, run_all.sh.bak_*  editing backups
  contacts.md          contact research notes (not part of the scientific record)
  Python virtual environment and the LaTeX (tectonic) cache

NOTE ON FEATURE FILES
  features.npz (EDA) is the original file. For the six other stations the archive holds slimmed copies with the
  arrays jul_t/jul_f/jul_P (July-2023 spectrogram), dspec/days/fspec (daily spectra) removed; those arrays are only
  used by analysis.py, which reads EDA alone. All arrays used by the other scripts (t, cols, X, logP36, f36) are
  unchanged. Re-running features.py regenerates the full files.

HOW TO RE-RUN
  1. Python >= 3.10 with: numpy scipy matplotlib obspy utide  (e.g. python3 -m venv venv; venv/bin/pip install ...).
     run_all.sh expects the interpreter at ../venv/bin/python relative to pulse26/ (edit PY= at the top if needed).
     The package versions used originally were not recorded (see paper/OPEN_ITEMS.md item 4).
  2. With the included features*.npz and tide/ files you can skip downloads and run the analyses directly, e.g.
       cd pulse26; nice -n 19 ../venv/bin/python -u robustness.py   (also analysis.py, controls.py, source_vs_site.py,
       components.py, multistation.py, model.py, caveats.py, caveats_bg.py, caveats_bg2.py)
     robustness.py and caveats.py take tens of minutes and up to ~3 GB of memory (they were run under ulimit -v 3000000).
  3. Full rebuild from raw data: bash run_all.sh (downloads ~1 GB of miniSEED, one request at a time).
  4. Paper: cd paper; python make_figs.py; python figs_main.py; tectonic main.tex; tectonic si.tex
