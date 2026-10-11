# Paper outline (GRL style; draft 9 Oct 2026)

Working title: Ocean tides modulate the 26-second Gulf of Guinea microseism

Target: Geophysical Research Letters (fallback: Seismological Research Letters). About 12 publication units, 4 figures plus Supporting Information.

## Key Points (each ≤140 characters)
1. The 26 s Gulf of Guinea microseism strengthens by about 11% in power (+0.45 dB) near M2 high water, lagging it by about 1.7-2 h, at four stations.
2. All stations share the same phase, while their own background noise does not. The modulation is therefore at the source, not at the sites.
3. Linear changes in tidal water depth at shelf depths are 5-40 times too weak, which points to very shallow coupling or a nonlinear source.

## Abstract (draft, ~240 words; numbers from results.txt, source_vs_site.txt, multistation.txt, components.txt, model.txt)
The 26 s microseism from the Bight of Bonny is a narrow, persistent seismic line. It was discovered in the 1960s, and its source mechanism is still debated. We analyse 7.4 years (2019-2026) of continuous broadband data from station G.EDA in Cameroon. We add G.TAM (Algeria), II.MBAR (Uganda) and II.SHEL (St Helena) for a common period, 2022-2024.

The line is detected in 31% of quality-controlled hours, at a 1% false-alarm rate set in a nearby control band. Its median period is 26.341 s. Regressing hourly line power on tidal constituents shows a significant M2 modulation. At EDA it is +0.47-0.53 dB relative to the local background, with p ≤ 0.01 against phase-randomised surrogates. TAM, MBAR and SHEL show the same phase, peaking 1.7-2.4 h after M2 high water at Limbe. Their own background noise peaks about 8 h after high water, so the phase is not set at the sites. Both spectral components of the line, and a weaker 28 s line, are modulated together. The M4 harmonic is small, which argues against control by the magnitude of the tidal current.

A linear-wave model of tidal changes in depth, shoaling, bed pressure and wavy-bottom primary-microseism coupling predicts ≤0.1 dB, often with the opposite sign, at shelf depths ≥20 m. Matching the observation requires coupling in water ≤5-10 m deep, or a nonlinear (threshold-like) source. The tidal modulation is a new constraint on source models of the 26 s microseism. We also confirm the line's doublet structure, first suggested by Holcomb (1998), and show that the dominant component changed in 2025. The line period shows no tidal modulation (≤10-15 µHz).

## Figures (4 main)
- **Fig. 1. Signal and detection.** (a) July 2023 spectrogram at EDA (fig1_spectrogram_2023-07.png). (b) Multi-year spectra and peak period (from fig2_longterm_spectra_period.png). (c) Map: EDA, TAM, MBAR, SHEL, the Bight of Bonny source region (Holcomb 1998; Shapiro et al. 2006; Xia et al. 2013) and the tide gauges Port Sonara, São Tomé and Lagos. The map is still to be made with Cartopy or plain coastlines.
- **Fig. 2. Tidal periodogram and phase bins at EDA.** Zoomed periodogram with tidal lines and surrogate 95/99% levels (fig3_periodogram_tidal.png), plus line and background power binned by M2 phase (fig5_M2_phase_controls.png / fig4_tide_binned_xcorr.png).
- **Fig. 3. Source, not site.** M2 phasors of line minus background at EDA, TAM, MBAR and SHEL, with the background phasors (fig8_multistation_M2_phasors.png, fig6_source_vs_site.png).
- **Fig. 4. Physical interpretation.** Toy-model modulation against depth, with the observed band (fig9_tide_coupling_model.png). Possible inset: per-component and 28 s-line M2 amplitudes.
- **Supporting Information:** yearly stacks and the doublet/2025 dominance switch (fig7_yearly_stacks.png); full-band periodogram (fig3a); QC and false-alarm calibration; surrogate method; tide-gauge comparison (Port Sonara vs São Tomé vs Lagos, UTide); ERA5 swell correlation (r = 0.20); sub-period robustness; failed or null tests (frequency modulation, 20-24 s background).

## 1. Introduction (~1 paragraph each)
- History of the 26 s signal: Oliver (1962); Holcomb (1980, 1998); location in the Bight of Bonny by Shapiro, Ritzwoller & Bensen (2006); Xia, Ni & Zeng (2013).
- Competing mechanisms:
  - swell/primary-microseism coupling: Longuet-Higgins (1950); Hasselmann (1963); Ardhuin (2018);
  - shelf or sediment resonance: Chen, Xie & Ni (2022);
  - a fluid-filled crack or resonator excited by swell: Poli et al. (2026).
  Related persistent localised sources: Xia & Chen (2020); Xia, Feng & Chen (2024); Takano & Poli (2025); Bruland & Hadziioannou (2023).
- Gap: no published test of tidal modulation, which is a standard probe of triggered or forced sources (e.g., Rubinstein et al. 2008 for tremor). Poli et al. (2026, peer-review file) considered tidal effects higher order and did not test them.

## 2. Data and Methods
- Seismic data:
  - G.EDA.00.LHZ (2019-05 to 2026-09) and G.TAM (RESIF/GEOSCOPE);
  - II.MBAR and II.SHEL (EarthScope FDSN);
  - instrument response removed from StationXML.
- Spectral estimation: 3-h Hann windows with a 1-h step; Welch SNR.
- Detection threshold: 99th percentile of the same statistic in the 30-32.5 mHz control band.
- QC: secondary-microseism band level relative to its 15-day running median, and a peak/MAD limit.
- Tides: UTide fit to the UHSLC Port Sonara gauge (98.9% of variance explained; M2 0.59 m), cross-checked against São Tomé and Lagos (HW within ±0.3 h).
- Tidal statistics:
  - joint harmonic regression (M2, S2, N2, K1, O1, Q1, M4, S1, S3) on a 72-h high-passed hourly series;
  - significance from smoothed-spectrum phase-randomised surrogates plus shuffle and local-rank tests;
  - weight is put on M2, N2 and O1 because S2 and K1 are confounded with solar and thermal cycles.
- Line-minus-background metric to remove site and propagation noise.
- Toy model: Airy waves with shoaling, bed pressure, bed velocity, wavy-bottom coupling with bottom spectrum ~k^-n, depth-limited forcing and wave-current flux; standing-tide current estimate.

## 3. Results
1. Detection and period: median 26.341 s (95% CI 26.336-26.347 s).
2. M2 modulation at EDA: amplitude, phase and significance; S2 at a tide-like ratio; N2 weak; robust across sub-periods and SNR conditioning; detection rate 26% at low water vs 36% at high water.
3. Multi-station phase coherence:
   - EDA 1.73±0.21 h, TAM 1.75±0.17 h, MBAR 2.40±0.64 h, SHEL 1.99±0.54 h;
   - background phases differ;
   - EDA–TAM hourly correlation r = 0.48.
4. Spectral components: both 26 s components are modulated together; the 28 s line is weaker (~0.16 dB, +2.3-2.5 h); M4 is small; no frequency modulation.
5. Long-term behaviour: the doublet and the switch in the dominant component in 2025 (seen at EDA and TAM; the 28 s line is unchanged, so it is not instrumental). Probably Supporting Information.

## 4. Discussion
- Size problem: linear depth effects at plausible shelf source depths are ≤0.1 dB (model.txt). Bed pressure and velocity even give the wrong sign.
- Options:
  - (i) coupling in very shallow water (≤5-10 m: nearshore, surf zone or estuarine), which is compatible with surf-zone ideas raised in the Poli et al. review;
  - (ii) a nonlinear or threshold source (exponential sensitivity p0 ≈ 50-65 kPa to the 5.9 kPa tidal load), consistent with a triggered resonator;
  - (iii) a modulated swell supply through currents, which is too small except in shallow water.
- Lag of 1.7-2 h:
  - a mixture of height and opposing-current terms (needs a current/height ratio of 1.2-1.6);
  - delayed tides at the coupling site (estuaries and creeks lag the open coast);
  - a poroelastic delay.
- Testable predictions:
  - spring-neap scaling (S2/M2 and N2 amplitude);
  - phase relative to tidal currents from a validated regional tide model;
  - ocean-bottom or coastal pressure data near Bioko and the Rio del Rey.
- Limitations:
  - single-gauge tide reference;
  - the 2023-02 and 2024-05..07 gaps;
  - fragile component fits;
  - Xia et al. 2013/2024 full texts not checked.

## 5. Conclusions (3-4 sentences)

## References (verified: each has been read in full or its bibliographic details confirmed; "abstract only" is flagged)
- Ardhuin, F. (2018). Large-scale forces under surface gravity waves at a wavy bottom: A mechanism for the generation of primary microseisms. GRL 45, 8173-8181. [details verified; cite only for the coupling concept]
- Bernard, P. & Martel, L. (1990). PEPI 63, 229-231. [read]
- Bruland, C. & Hadziioannou, C. (2023). Commun. Earth Environ. 4, 176. [read]
- Chen, Y., Xie, J. & Ni, S. (2022). EPSL 578, 117334. [read in full]
- Hasselmann, K. (1963). Rev. Geophys. 1, 177-210. [cited via secondary literature; check before submission]
- Holcomb, L. G. (1980). BSSA 70, 1055-1070. [read]
- Holcomb, L. G. (1998). BSSA 88, 744-757. [read in full; doublet on p. 755]
- Longuet-Higgins, M. S. (1950). Phil. Trans. R. Soc. A 243, 1-35. [cited via secondary literature; check before submission]
- Oliver, J. (1962). BSSA 52, 507-517. [read]
- Poli, P. et al. (2026). Nat. Commun. 17, 4234. doi:10.1038/s41467-026-71541-6. [read in full, plus the peer-review file]
- Rubinstein, J. L. et al. (2008). Tidal modulation of nonvolcanic tremor. Science 319, 186-189. [details verified; cite as an analogue only]
- Shapiro, N. M., Ritzwoller, M. H. & Bensen, G. D. (2006). GRL 33, L18310. [read]
- Takano, T. & Poli, P. (2025). GRL 52, e2024GL113290. [details verified]
- Xia, Y. & Chen, X. (2020). GRL 47, e2020GL088137. [details verified]
- Xia, Y., Ni, S. & Zeng, X. (2013). GJI 194, 362-366. [ABSTRACT ONLY; read in full before submission]
- Xia, Y., Feng, X. & Chen, X. (2024). GJI 237, 1079-1092. [ABSTRACT ONLY; read in full before submission]
- Data: RESIF / GEOSCOPE (network G); IRIS/IDA network II via EarthScope; UHSLC research-quality tide gauge data (Port Sonara 816, São Tomé 225, Lagos 233); ERA5 (Copernicus). Software: ObsPy, UTide.
- Add the formal data DOIs (G network, II network, UHSLC) before submission. Not looked up here, so none are listed.

## Open items before submission
- Read Xia 2013 and 2024 in full (OUP blocks automated access; needs a human with browser or library access).
- Map figure; a bootstrap uncertainty on the multi-station mean phase.
- Optionally, a validated regional tidal-current product for the lag test (HAMTIDE needs registration; not used).
