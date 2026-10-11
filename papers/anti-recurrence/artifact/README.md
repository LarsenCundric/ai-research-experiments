# Reproducibility artifact: "Linear anti-recurrence sequences are linear plus automatic"

Author: Larsen Cundric (draft, 2026-10-09). Affiliation: TODO. Licence: TODO. DOI: TODO (Zenodo).

This directory holds every script, Walnut file and log that the paper relies on (paper/main.tex, Sections 4-6).
- None of the computations is needed for the proofs of Theorems A-C, which are pen-and-paper (docs/PROOF.md, paper Section 3).
- The Walnut runs (Section 4 and Section 6) are independent machine proofs for specific forms.

## Requirements
- Python >= 3.9. Uses the standard library only (fractions, itertools, array); no numpy needed.
- A C compiler, for code/referee/arseq.c.
- Walnut v7.1, https://github.com/Walnut-Theorem-Prover/Walnut. We built it with plain javac on JDK 21.
- Every run fits in a single core and less than 500 MB of RAM. We ran everything under `nice -n 19` with hard timeouts.

## Layout

### code/ (our scripts)

| file | purpose |
|---|---|
| gen.py | 10^7 terms of the 4-rusty sequence a=(1,4) by brute force. Writes d_10000000.bin (int8, d(n)=A_n-11n), about 10 MB, not included. |
| recur_check.py | Checks recursion (eq. 2 of the paper) for all n <= 10^7 (needs gen.py output). |
| dfao.py | Builds the 17-state msd 5-DFAO for (1,4) and writes dfao_min.json. |
| recheck.py | Exact re-check of identity (*), the boxes (i)-(iv) and the window recursion on 50 forms. Also provides gen_AB (brute-force generator) used by the scripts below. Log: logs/recheck_60000.log. |
| verify_v2.py | Explicit constants of Prop. 3.3 and Remark 3.6 (L*, U*, T, T', o, W, P0, maps H_c), checked coordinate by coordinate. Log: logs/verify_v2_20000.log. Usage: `python verify_v2.py 20000` |
| twoterm.py | Lemma 3.4 (universal box, U <= tau-k), Theorem B (two-term recursion), and the Theorem C automaton with Moore minimisation. Logs: logs/twoterm_named.log, logs/twoterm_sweep_6000.log. Usage: `python twoterm.py 20000 named` and `python twoterm.py 6000 sweep` |
| r2checks.py | Exact range of d (outputs of reachable states of the Theorem C automaton), narrowest box vs (L*,U*), V(1) in [-K,tau-k]^3, minimal DFAO sizes in our convention (input n>=0, d(0)=0) and in the Fokkink-Joshi convention (input n-1). Logs: logs/r2checks_named.log, logs/r2checks_sweep.log (736 forms). Usage: `python r2checks.py named`, `python r2checks.py sweep` |
| zaslavsky_check.py | Anti-Fibonacci check: A_n = 5n-2+PD_{n-1} (n<=3000), and literal vs. swapped reading of Zaslavsky's Thm 1. |
| walnut_forms.py | Builds the closure DFAO for a form and emits the Walnut word automaton plus command file. Set WALNUT_HOME to the Walnut directory. |
| general.py, cert.py, boxproof.py, kernel.py | Earlier exploratory checks: window identity, closure certificates, explicit boxes, kernel exploration. Kept for completeness. |

### code/referee/ (a separately written second implementation, by a different AI agent acting as internal reviewer; not peer review)

| file | purpose |
|---|---|
| arseq.c | Independent C generator and checker. Build: `cc -O2 -o arseq arseq.c`. Usage: `./arseq N a1 a2 ...` |
| sweep.py | The 585-form sweep. Calls ./arseq. Log: logs/sweep.log. |
| closure.py | Independent DFAO construction plus minimisation, and equivalence check against a Walnut word automaton file. Writes /tmp/cl_d.txt. |
| boxrange.py | Minimal-box statistics. |

logs/growth.log holds the 2*10^6-term runs for 8 forms.

Erratum: the `tight` flag in logs/sweep.log compares against finite-prefix ranges and is unreliable; see the note at the top of docs/REVIEW.md.

### code/referee2/ (second pass of the separately written implementation)

| file | purpose |
|---|---|
| arseq2.c | Second C generator/checker. Build: `cc -O2 -o arseq2 arseq2.c` (also `cc -O2 -o arseq arseq.c`). |
| sweep2.py | 2270-form sweep (k=2..8, entries up to 200, tau up to 1600): Lemma 3.4, Theorem B, maps H_c, closure in box, exact ranges. Log: logs/sweep2.log. |
| closure.py, closure_shift.py | Formula-based closure of the Theorem C automaton (exact ranges; shifted indexing). |
| prop33.py | Exact rational check of (L*,U*) and o, W, P0 on 1420 forms. |

logs/big.log holds the 3*10^6-term runs for 7 large forms.

### walnut/

automata/ (copy into Walnut's "Word Automata Library/"):

| automaton | form | states | stored output |
|---|---|---|---|
| RUS | (1,4) | 17 | d+6 |
| RUX | (1,4) | 17 | d+6 |
| RFV | (1,5) | 19 | d+7 |
| RTS | (2,7) | 37 | d+12 |
| RQF | (1,1,5) | 24 | d+9 |

- RUS is the guessed-then-verified automaton (Table 1 of the paper).
- RUX is the closure-built automaton for the same form; it is equivalent to RUS.
- Each stored output is d minus the lower end of its range (see the `def ...a` lines in the scripts).
- dfao_min.json holds RUS as JSON.

scripts/ (Walnut command files) and logs/ (their outputs):

| script(s) | contents |
|---|---|
| walnut_rusty.txt, walnut_rusty2.txt | Main (1,4) proof, plus sanity and control queries. |
| walnut_ref14.txt | Referee's independently written (1,4) query set (10 TRUE, 2 controls FALSE). |
| walnut_forms_all.txt | RUX, RFV and RTS, plus RQF up to its linear-relation query. RQF_lin ran out of the 400 MB heap. |
| walnut_RQF_rest.txt | The remaining RQF queries. |
| walnut_ref115.txt | Referee's reformulated (1,1,5) linear relation (q_lin and q_lin_tot both TRUE). |
| walnut_forms_rerun.txt | Referee's full re-run of all queries except RQF_lin (every verdict reproduced). |
| walnut_rqf_disjB.txt | Second pass: (1,1,5) pairwise disjointness of B1, B2, B3 (q_disj12, q_disj13, q_disj23: all TRUE). Also implied by RQF_incB. |

To run, from the Walnut directory:

    nice -n 19 timeout 3600 java -Xmx400m -cp "classes:<deps>" Main.Prover < walnut_rusty.txt

### paper/
- main.tex, main.pdf: copy of the paper draft this artifact accompanies.

### docs/
- PROOF.md: the proof, version 2.1 (after the second review pass).
- PROOF_v1.md: the proof, version 1.
- REVIEW.md: the first internal review report (on v1), with an erratum note at the top.
- REVIEW2.md: the second internal review report (on v2 and the paper draft).

## Integrity
SHA256SUMS lists the SHA-256 of every file in this directory except itself. Check with `sha256sum -c SHA256SUMS`.

## Notes
- Every check generates (A,B) from the definition by brute force (mex plus linear form), so it does not depend on the formulas being tested.
- The uniqueness step behind the Walnut certificates is Fokkink-Joshi, arXiv:2506.13337v1, Lemma 3 (= Integers 26 (2026) #A24, Lemma 2).
- Automaton sizes: "states" above are in our convention (input n>=0, output d(n), d(0)=0, msd first, leading zeros allowed). In the Fokkink-Joshi convention (input n-1) the minimal sizes are (1,4) 9, (1,5) 11, (2,7) 20, (1,1,5) 9, and (1,3) 6.
- "Referee" throughout means an AI agent acting as internal reviewer; none of this is peer review.
