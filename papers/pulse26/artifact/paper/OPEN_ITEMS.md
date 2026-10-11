# Open items for the pulse26 manuscript (updated 11 Oct 2026)

Resolved on 11 Oct 2026: author line and AI-generation lines; detailed AI-use disclosure; software citations
(NumPy, SciPy, Matplotlib via Crossref; Python UTide port via GitHub/PyPI, no DOI exists); II network creator string
(EarthScope Consortium, per DataCite and the FDSN network page); Praia and other gauge coordinates (UHSLC ERDDAP metadata);
SI figure distance labels (EDA 240 km, TAM 2096 km; figures regenerated, numbers reproduced identically);
"4-40x" wording in outline/notes; stale outline lines; data/code availability ("available from the author on request").

## Still open
1. **Author contact**: personal e-mail to be added by Larsen (no work e-mail or affiliation).
2. **Independent verification**: the analysis has not been checked by the author or by a domain expert. An expert read
   of the statistics (block nulls, gamma estimator) and the toy model is the most important remaining step.
3. **Tide reference**: harmonic prediction from one 2008-2011 gauge record. Contemporaneous gauge data or a validated
   regional tide model with currents (FES/TPXO/HAMTIDE need registration, so they were not used) would test the lag.
4. **Software environment**: the original Python venv (/workspace/research2/venv) disappeared from the box between
   sessions; it was recreated on 11 Oct with numpy 2.5.4, scipy 1.18.1, matplotlib 3.11.2 (obspy and utide NOT
   reinstalled). The versions used for the original analysis were not recorded. Re-running source_vs_site.py with the
   new venv reproduced source_vs_site.txt exactly. Full re-runs from download need `pip install obspy utide`.
5. **Unpinned citations**: the Python UTide port and Natural Earth have no DOI and are cited by URL ("n.d."). ERA5,
   NumPy and SciPy entries use "and others" for long author lists; check journal style for full lists.
6. **Code/data deposit**: currently "available from the author on request". A Zenodo deposit with DOI would be needed
   for AGU's data policy at submission. A local archive exists at /workspace/pulse26-code-and-results.zip.
7. **Figures**: SI figures are 100-120 dpi PNGs with titles baked in. Fig. S7 (fig10_springneap) still shows the
   older, incomplete M2+N2 lunar envelope (flagged in its caption). The right-hand "period (s)" axis of the Fig. 1c
   spectrogram overlaps the colour bar. Consider vector re-renders for submission.
8. **Template**: plain LaTeX article class with natbib/plainnat, not the official AGU template; reformat for submission.
9. **Minor**: caveats.py uses latitude 14.91 for the Praia UTide fit (UHSLC gives 14.9167); the effect on nodal
   corrections is negligible, but it is not re-run.
10. **Separate task (not started)**: the e-mail to Piero Poli. Nobody has been contacted.
