# Ocean tides modulate the 26-second Gulf of Guinea microseism

[Read the manuscript](26s-pulse-guinea.pdf) · [Supporting information](si.pdf)

**Status: AI-generated observational analysis. Not independently verified or reviewed by a domain expert, according to the supplied manuscript.**

## What the manuscript reports

The manuscript reports a tidal modulation of the 26-second seismic signal from the Gulf of Guinea, using 7.4 years of recordings at station EDA and data from six other stations. It reports an M2 amplitude of 0.47 dB (95% interval 0.42–0.53 dB; approximately ±11% in power) at EDA, peaking about 1.6 hours after predicted high water. It interprets the timing across stations as evidence of modulation at the source and compares it with a simple model of water-depth effects.

These are the manuscript's reported results and interpretation. This release does not independently establish the statistical findings, the proposed physical interpretation, or novelty. The mention of Geophysical Research Letters on the title page describes the draft's intended format, not publication or acceptance by that journal.

## Contribution and attribution

Grok Bot obtained the source data, wrote the analysis code, designed and ran the statistical tests, developed the toy model, searched the literature, generated figures, and drafted and revised the text, according to the AI-use disclosure. Larsen Cundric chose the topic, set the scope and constraints, guided priorities, and requested revisions.

Larsen is the experiment organizer and repository maintainer. He has not independently verified the analysis and does not claim to have developed the scientific findings himself. Both PDFs label his role and identify the manuscript as AI-generated.

## Materials and provenance

The supplied PDFs are preserved without modification and are byte-identical to `artifact/paper/main.pdf` and `artifact/paper/si.pdf`.

All four supplied ZIPs were combined into [`artifact/`](artifact/), preserving all 141 files and their contents:

| Source archive | Contents |
| --- | --- |
| `pulse26-1-code-results-paper.zip` | 133 files: analysis code, results, logs, figures, gauge data, metadata, manuscript source and PDFs |
| `pulse26-2-features-EDA.zip` | Derived EDA features |
| `pulse26-3-features-TAM-MBAR-ASCN.zip` | Derived TAM, MBAR and ASCN features |
| `pulse26-4-features-SHEL-WIN-SACV.zip` | Derived SHEL, WIN and SACV features, plus hourly tide prediction |

- [`artifact/ZIP_README.txt`](artifact/ZIP_README.txt): original snapshot description, data provenance and reproduction instructions.
- [`artifact/run_all.sh`](artifact/run_all.sh): original pipeline driver.
- [`artifact/paper/`](artifact/paper/): LaTeX sources, bibliography, figures, historical outlines and open items.
- [`SOURCE_SHA256SUMS`](SOURCE_SHA256SUMS): hashes of the six supplied files; the ZIPs themselves are represented here by their extracted contents.
- [`SHA256SUMS`](SHA256SUMS): hashes of the files in this release.

The archives were built on October 11, 2026. The PDFs' statement that materials are available on request predates this public release. Historical notes and outlines are preserved as experiment records, not additional reviewed findings. Full agent conversation logs are not included.

## Data sources and reproduction

The original documentation attributes seismic recordings to GEOSCOPE/RESIF (EDA, TAM), EarthScope network II (MBAR, SHEL, ASCN, SACV), and GEOFON (WIN); tide-gauge records to UHSLC; wave-reanalysis series to ERA5 via Open-Meteo; and coastline data to Natural Earth. See the manuscript's Open Research section and bibliography for the source citations. Third-party data retain their applicable source terms; this repository does not grant new rights over them.

The roughly 1.05 GB of raw miniSEED waveforms are not included. The download scripts describe how they were retrieved. The included derived feature files and tide files support rerunning analyses without downloading the waveforms. The six non-EDA feature files omit daily spectra and July 2023 spectrogram arrays; the original archive README says the arrays used by those stations' analysis scripts are unchanged.

Run the original instructions from `artifact/`, which corresponds to the original `pulse26/` directory. The pipeline expects a Python interpreter at `../venv/bin/python`; configure that path for your environment. Dependencies listed by the archive are NumPy, SciPy, Matplotlib, ObsPy and UTide. **Versions used for the original analysis were not recorded**, limiting exact environment reproduction. Some analyses take tens of minutes and approximately 3 GB of memory. Use a working copy if rerunning scripts, since they write result files alongside the preserved snapshot.

## Verification status and limitations

During repository preparation:

- All four ZIPs passed CRC checks; every extracted file was compared byte-for-byte against its archive entry.
- Both standalone PDFs matched their bundled copies.
- The seven station feature NPZ files and hourly tide prediction passed internal CRC checks; their NumPy array headers were parsed without executing the analysis.
- All nine `.json` files parsed successfully.

These are packaging and readability checks. The statistical analysis, raw-data processing, bootstrap/null tests, and physical model were not rerun or independently validated for this release.

The manuscript and original open-item notes identify several limitations:

- The tide reference is a harmonic prediction from a 2008–2011 gauge record, not contemporaneous observations for the seismic study period.
- Distant-station signals are weaker, station noise is correlated, and the stations are not fully independent.
- Background subtraction affects the estimated response; nearby spectral background is itself weakly modulated at some stations.
- The physical model is deliberately simple and does not establish a unique source mechanism.
- The supporting information retains an older envelope figure flagged in its caption, and the original notes list remaining figure-layout issues.

Domain review of the statistics, tide reference and physical interpretation remains outstanding.

## Review or take this further

[Open an issue](https://github.com/LarsenCundric/ai-research-experiments/issues) to report an error, reproduce the analysis, assess the physical interpretation, or discuss preparing a verified version for publication. Identify the relevant figure, result or script and include reproducible details.

Larsen is not seeking scientific coauthorship for initiating this experiment. An acknowledgment of his organizing role would be sufficient. Future authorship should reflect actual contributions and disclose the AI-generated origin.
