# The three-colour cycle Ramsey numbers R(C4, C7, C7) and R(C6, C7, C7)

[Read the manuscript](ramsey-c7.pdf)

**Status: AI-generated research manuscript with reported machine-checked computations. Not peer reviewed or reviewed by a human expert, according to the supplied manuscript. Larsen has not independently verified the mathematics or computations.**

## What the manuscript claims

The manuscript reports R(C4, C7, C7) = 15 and R(C6, C7, C7) = 21, using explicit lower-bound colourings and SAT-based upper-bound computations. It also gives colourings for the lower bounds R(C3, C7, C7) >= 25 and R(C5, C7, C7) >= 25.

These are the manuscript's claims. This repository release does not independently establish the upper bounds, the correctness of the overall proof pipeline, or novelty.

## Contribution and attribution

Grok Bot carried out the literature search, designed and implemented the encodings, checkers and solver drivers, ran the computations, and drafted the manuscript and proofs, according to the manuscript's AI disclosure. Larsen Cundric initiated and guided the experiment and maintains this repository. He does not claim to have developed or independently verified the mathematical arguments.

The PDF retains Larsen's name, labels his organizing role on its first page, and states the limits of his verification in Section 6.

## Materials and provenance

- [`ramsey-c7.pdf`](ramsey-c7.pdf): the supplied manuscript, copied without modification. It is byte-identical to `artifact/paper/main.pdf`.
- [`artifact/`](artifact/): all 294 files from `ramsey-c7-code-and-proofs.zip`, extracted without content changes, preserving their internal paths.
- [`artifact/ZIP_README.txt`](artifact/ZIP_README.txt): snapshot details and files excluded from the original ZIP.
- [`artifact/artifact/README.md`](artifact/artifact/README.md): original toolchain and reproduction instructions. Run its commands from this experiment's `artifact/` directory, which corresponds to the original project root.
- [`artifact/paper/main.tex`](artifact/paper/main.tex): bundled LaTeX source. Earlier source drafts and open-item notes are historical records.
- [`SHA256SUMS`](SHA256SUMS): release checksums for this README, the supplied PDF, and all extracted files.

The snapshot was packaged on October 11, 2026 at 09:21 PDT. Statements about work being in progress or queued describe that snapshot; this repository is not monitoring those runs. The PDF's statement that the artifact is available only on request predates this public release.

## Verification status and limitations

The original experiment reports:

| Computation | Status in the supplied snapshot |
| --- | --- |
| K15, leg A, for R(C4, C7, C7) | 988 cubes certified; audit passed |
| K21, leg A, for R(C6, C7, C7) | 1,016 top-level cubes covered through 1,961 certified leaves; audit passed |
| K15, leg B, using a different encoding and checker | In progress: 792 of 1,022 top-level cubes certified as of 08:58 PDT on October 11 |
| K21, leg B | Not started |

Leg A is reported to use CaDiCaL LRAT proofs checked by cake_lpr. Leg B uses Kissat DRAT proofs checked by drat-trim. These are computational checks, not human peer review. The manuscript identifies remaining trusted components, including the symmetry-breaking argument, clause checkers, formula assembly, and coverage argument.

**The main per-subproblem LRAT/DRAT proof files are not included.** The original pipeline deleted them after successful checks and retained their sizes and hashes in the logs. A hash alone cannot replace a proof file or allow its rechecking. Rechecking those certificates requires regenerating the missing proofs. Some small validation proofs are included; other large validation proofs and third-party tool binaries are excluded as documented in `ZIP_README.txt`.

During this repository release:

- All 139 entries in the original `artifact/artifact/SHA256SUMS` matched, with no missing files or mismatches.
- All extracted files were compared byte-for-byte against their ZIP entries.
- The supplied `src/checkA.py` was rerun on the four lower-bound colourings for (C4, C7, C7) on 14 vertices, (C6, C7, C7) on 20 vertices, and (C3, C7, C7) and (C5, C7, C7) on 24 vertices. All returned `GOOD`.
- The upper-bound computations, certificate checks, and solver-dependent audits were not rerun. Running the supplied colouring checker is a limited reproduction, not an independent proof review.

## Review or take this further

[Open an issue](https://github.com/LarsenCundric/ai-research-experiments/issues) to report a gap, reproduce a computation, or discuss preparing a verified version for publication. Identify the theorem, run, or file involved and provide reproducible details.

Larsen is not seeking mathematical coauthorship for initiating this experiment. An acknowledgment of his organizing role would be sufficient. Any future authorship should reflect actual contributions and disclose the AI-generated origin.
