# Linear anti-recurrence sequences are linear plus automatic

[Read the manuscript (v4)](anti-recurrence-v4.pdf)

**Status: AI-generated proposed proof. Not peer reviewed. Larsen has not independently verified the mathematics.**

## What the manuscript claims

The manuscript proposes a proof of the Fokkink-Joshi conjecture that every positive integral linear anti-recurrence sequence is a linear sequence plus an automatic sequence. It gives a uniform discrepancy bound, a two-term recursion, and an explicit automaton construction, with additional analysis of the 4-rusty numbers.

This describes the manuscript's claims; this release does not independently establish their correctness or novelty.

## Contribution and attribution

Grok Bot generated the mathematical work and manuscript during an experiment initiated and guided by Larsen Cundric. The manuscript also attributes the code, computations, most of the literature search, and internal cross-checks to AI agents. Larsen is the experiment organizer and repository maintainer, not a claimant to independently developing the mathematical arguments.

The PDF retains Larsen's name and explicitly labels his organizing role on its first page. Its AI disclosure states that he has not independently verified the mathematics.

## Materials and provenance

- `anti-recurrence-v4.pdf`: current manuscript, copied without modification from the supplied PDF.
- [`artifact/`](artifact/): the reproducibility artifact extracted from `anti-recurrence-code.zip`, with its original files and checksums preserved.
- [`artifact/README.md`](artifact/README.md): original technical instructions for the code and Walnut files. This document predates the current manuscript; its section references and authorship placeholders are historical.
- [`SHA256SUMS`](SHA256SUMS): checksums for the current manuscript and all included artifact files.

The artifact contains an **older** manuscript in `artifact/paper/`. It is preserved for provenance, not presented as the current paper. Its authorship language and responsibility statements are superseded by the role disclosure above and in v4. The bundled LaTeX source belongs to that older draft; the exact v4 LaTeX source is not included.

The `referee` directory names and review documents refer to AI agents acting as internal reviewers. They do not indicate journal refereeing or independent human verification. The artifact's original README also records an unreliable finite-prefix `tight` flag in `logs/sweep.log`; consult its erratum before interpreting that output.

Full experiment conversation logs are not included in this release.

## Verification status

The manuscript reports finite computational checks and Walnut certificates for specific forms. It explicitly states that the general proofs are not machine-checked. The stored logs are outputs from the original experiment, not fresh reproduction results from this repository release.

During repository preparation, every file in the artifact's original checksum manifest matched its recorded SHA-256. This verifies the integrity of the packaged files, not the mathematical claims. The full computational suite and Walnut certificates have not been rerun for this release.

## Help review or publish

[Open an issue](https://github.com/LarsenCundric/ai-research-experiments/issues) to report a gap, share a reproduction, or discuss developing a verified version for publication. Include the theorem or file involved and enough detail to reproduce any discrepancy.

Larsen would be satisfied with acknowledgment for initiating and guiding the experiment. Future mathematical authorship should reflect actual contributions, with the AI-generated origin disclosed.
