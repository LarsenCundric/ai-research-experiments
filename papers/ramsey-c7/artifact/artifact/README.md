# Artifact: R(C4,C7,C7) = 15 and R(C6,C7,C7) = 21, certified SAT computations

Status (updated Oct 11 2026, 09:21 PT): both values certified by leg A (CaDiCaL LRAT + cake_lpr), audits PASS.
Independent leg B: K15 in progress (792/1022 top-level cubes certified at 08:58 PT Oct 11, all UNSAT); K21 leg B queued, not started.

All paths are relative to the project root `/workspace/ramsey-c7` (this artifact references files in place; `make_tarball.sh`
packs them). `SHA256SUMS` lists checksums of every file below (`sha256sum -c artifact/SHA256SUMS` from the project root).

## 1. Toolchain (pinned)
| tool | version / git | path |
|---|---|---|
| CaDiCaL | 3.0.1 (c607304) | tools/cadical/build/cadical (also built with the IPASIR-UP propagator, prop/cycprop) |
| Kissat | 4.0.4 (8af8e56) | tools/kissat/build/kissat |
| cake_lpr | a36874a | tools/cake_lpr/cake_lpr (CakeML-verified LRAT checker) |
| drat-trim / lrat-check | 2e3b2dc | tools/drat-trim/ |
| march_cu (CnC) | 705b60c | tools/CnC/march_cu/march_cu |
| Python 3, PySAT 1.9.dev15 (CaDiCaL 1.9.5), NetworkX 3.7 | | |
Build: `git clone` each repo at the hash above, `./configure && make` (CaDiCaL, Kissat), `make` (drat-trim, march_cu), cake_lpr
from its release C file (`make` in tools/cake_lpr). cycprop: `g++ -O3 -std=c++17 prop/cycprop.cpp -Itools/cadical/src
tools/cadical/build/libcadical.a -o prop/cycprop`.

## 2. Lower bounds (colourings, seconds)
    for f in colorings/lb_C4C7C7_n14.txt colorings/lb_C6C7C7_n20.txt; do python3 src/checkA.py $f <m> 7 7; python3 src/checkB.py $f <m> 7 7; done
    # m = 4 for the K14 file, 6 for the K20 file; colorings/lb_C3C7C7_n24.txt (m=3), lb_C5C7C7_n24.txt (m=5)
checkA = DFS cycle search; checkB = networkx.simple_cycles(length_bound). Cross-validation: `python3 src/crosscheck.py`.

## 3. Upper bound R(C4,C7,C7) <= 15, leg A (encoding A, cycprop, CaDiCaL LRAT + cake_lpr)  ~16 min on 3 cores
    python3 src/genA.py 15 4 7 7 cnf/L_n15_477_tradj_amo.cnf --sb tradj --amo --eager-upto 5      # lazy base formula
    src/make_cubes_lazy.sh 15 4 7 7 10 300 100000 cubes_A.txt                                     # (optional: cubes are shipped)
    python3 src/cnc_lazy.py cnf/L_n15_477_tradj_amo.cnf 15 4 7 7 cnc/lazy_n15_477/cubes WORKDIR_A --jobs 3
    python3 src/audit_cnc.py WORKDIR_A
Expected: `WORKDIR_A/summary.json` VERDICT "UNSAT CERTIFIED ...", 988/988 cubes; audit PASS.

## 4. Upper bound R(C4,C7,C7) <= 15, leg B (encoding B, lazyB CEGAR, Kissat DRAT + drat-trim) -- IN PROGRESS
    python3 src/genB.py 15 4 7 7 cnf/B_n15_477_sb_lazy.cnf --sb --eager-upto 5
    python3 src/test_sbB.py 5 400; python3 src/test_sbB.py 6 60                                   # SB brute-force sanity
    python3 src/cnc_tree.py B cnf/B_n15_477_sb_lazy.cnf 15 4 7 7 cnc/B/n15_477/cubes WORKDIR_B --jobs 2 \
        --solve-cap 1200 --offline-cap 2400 --check-cap 2400                                      # adaptive re-splitting driver
    python3 src/audit_cnc.py WORKDIR_B
The run started with src/cnc_lazyB.py (Oct 8, 19:22 PT) and was continued with src/cnc_tree.py (compatible workdir) from Oct 9.
Status at 08:58 PT Oct 11: 792/1022 top-level cubes certified (34 splits, 2895 certified leaves), all UNSAT, no SAT; coverage verified
by drat-trim and cake_lpr. Expected when finished: 1022/1022 top-level cubes certified; audit PASS. The cnc/B/n15_477 files shipped in
any snapshot taken before then are a partial, in-progress state.

## 5. Upper bound R(C6,C7,C7) <= 21, leg A (encoding A, cycprop, CaDiCaL LRAT + cake_lpr) -- CERTIFIED
    python3 src/genA.py 21 6 7 7 cnf/L_n21_677_tradj_amo.cnf --sb tradj --amo --eager-upto 5      # lazy base formula
    python3 src/cnc_tree.py A cnf/L_n21_677_tradj_amo.cnf 21 6 7 7 cnc/lazy_n21_677/cubes WORKDIR_K21 --jobs 3 \
        --solve-cap 1200 --offline-cap 2400 --check-cap 2400
    python3 src/audit_cnc.py WORKDIR_K21
The certified run started with src/cnc_lazy.py (Oct 8, 18:45 PT; 199 cubes certified) and was continued with src/cnc_tree.py
(Oct 9, 09:16 PT onward, compatible workdir); finished Oct 9, 20:25 PT. Result (cnc/lazy_n21_677/summary.json): 1016/1016 top-level
cubes certified, 15 verified splits (64 children each), 1961 certified leaves, no SAT. Audit re-run Oct 11, 09:19 PT:
paper/audit_K21_legA.txt -> AUDIT PASS (top coverage and all 15 split coverages re-proved with kissat + drat-trim).
Logged CPU: leaves 152,289 s solve + 32,366 s offline LRAT + 6,588 s cake_lpr; plus 24,485 s on the 15 over-cap runs (~60 core-h);
~26 h wall-clock on 3 jobs including restarts. (The earlier estimate of ~30 core-hours was too low.)
Independent leg B for K21 (cnc/B/n21_677) is queued after K15 leg B; not started.

## 6. Validation runs (known values)
    python3 src/cnc_lazy.py cnf/L_n12_447_tradj_amo.cnf 12 4 4 7 cnc/lazy_n12_447/cubes W1 --jobs 2     # R(C4,C4,C7)=12 (UNSAT)
    python3 src/cnc_lazy.py cnf/L_n13_467_tradj_amo.cnf 13 4 6 7 cnc/lazy_n13_467/cubes W2 --jobs 2     # R(C4,C6,C7)=13 (UNSAT)
    python3 src/cnc_lazyB.py cnf/B_n12_447_sb_lazy.cnf 12 4 4 7 cnc/B/n12_447/cubes W3 --jobs 2         # leg B, R(C4,C4,C7)=12
    src/prove.sh <full CNF> <tag>       # monolithic CaDiCaL LRAT (cake_lpr, lrat-check) + Kissat DRAT (drat-trim): R333 n17, R444 n11, R447 n12, R467 n13

## 7. What is trusted
Soundness of lex-leader symmetry breaking (paper, Lemma 3), the clause checkers `src/check_cnf.py` / `src/check_cnfB.py`,
the proof checkers (`cake_lpr`, formally verified; `drat-trim`), the assembly of F_i in `cnc_lazy*.py` (re-audited by
`audit_cnc.py`) and the coverage argument (`CNC_ARGUMENT.md`). Solvers, cubers, and the lazy propagators are untrusted.
Per-cube proofs are deleted after a successful check; `status.jsonl` keeps each proof's size and SHA-256.
Toolchain note: after a box tool wipe on Oct 10 (~14:00 PT), Kissat 4.0.4 was restored and CaDiCaL 3.0.1 rebuilt; on Oct 11 the
binaries report `--build` versions c60730422e75... (CaDiCaL) and 8af8e56f174b... (Kissat), matching the pinned hashes above.

## 8. Layout
    src/ prop/          generators, checkers, lazy solvers, drivers
    cnf/                lazy base formulas (B in the paper)
    cnc/<run>/          cubes, meta.json (input hashes), coverage.json, check_base.log, status.jsonl, summary.json, audit.txt,
                        splits.jsonl + splits/<id>.cubes (cube-tree runs)
    colorings/          lower-bound and solver-found colourings
    paper/              LaTeX source and PDF
    artifact/           this README, SHA256SUMS, make_checksums.sh, make_tarball.sh
