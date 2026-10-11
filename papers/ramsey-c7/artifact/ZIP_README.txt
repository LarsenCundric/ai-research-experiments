ramsey-c7 code and proofs -- snapshot 2026-10-11 09:21 PDT

Contents: R(C4,C7,C7)=15 and R(C6,C7,C7)=21 (both certified by leg A: CaDiCaL LRAT + cake_lpr; audits PASS).
Independent leg B for K15 was still RUNNING when this zip was made (792/1022 top-level cubes certified at 08:58 PT Oct 11);
cnc/B/n15_477/* and logs/cnc_tree_B_n15_477.log are an in-progress snapshot (a trailing partial JSON line, if any, was dropped).
K21 leg B has not started. See artifact/README.md (commands, toolchain), CNC_ARGUMENT.md (why the certificate proves the bound),
paper/main.pdf, paper/OPEN_ITEMS.md, and paper/audit_K21_legA.txt (K21 audit re-run Oct 11 09:19 PT: PASS).
artifact/SHA256SUMS lists hashes (computed Oct 11 ~09:21 PT; files of the running leg B will differ).

Layout (paths relative to ramsey-c7/):
  src/            generators (genA.py, genB.py, rlib.py), clause checkers (check_cnf.py, check_cnfB.py), colouring checkers
                  (checkA.py, checkB.py, crosscheck.py), lazy solvers/drivers (lazyB.py, cnc_lazy.py, cnc_lazyB.py, cnc_tree.py),
                  audit (audit_cnc.py), cubing scripts, prove.sh, circulant/construction scripts
  prop/           cycprop.cpp (CaDiCaL IPASIR-UP lazy cycle propagator) + helper scripts
  cnf/            lazy base formulas (B in the paper) and small validation CNFs
  cnc/            per-run cubes, meta.json (input hashes), coverage.json (coverage certificates' check results + proof hashes),
                  check_base.log, status.jsonl (per-cube verdicts, proof sizes and SHA-256), splits.jsonl + splits/*.cubes, summary.json, audit.txt
  colorings/      lower-bound colourings (lb_*.txt) and solver-found colourings
  proofs/         small proofs (R333_n17 LRAT+DRAT) and checker outputs (*.out) for the monolithic validation runs
  logs/           run logs
  artifact/       README, SHA256SUMS, checksum/tarball scripts
  paper/          LaTeX source, PDF, open items, K21 audit output

EXCLUDED (and why):
- compiled binary (rebuild from prop/cycprop.cpp, see artifact/README.md):
    prop/cycprop
- uncertified cost-estimation / exploratory runs under prop/ (est_*, runs/; ~200 MB, not part of any certificate):
    prop/runs/n11_447_m1.cert.log
    prop/runs/n11_447_m1.coloring.txt
    prop/runs/n11_447_m1.ext
    prop/runs/n11_447_m1.model
    prop/runs/n11_447_m1.solver.log
    prop/runs/n12_447_m1.cert.log
    prop/runs/n12_447_m1.ext
    prop/runs/n12_447_m1.final.cnf
    prop/runs/n12_447_m1.solver.log
    prop/runs/n12_447_warm.ext
    prop/runs/n13_467_m1.cert.log
    prop/runs/n13_467_m1.ext
    ... and 301 more
- full (non-lazy) CNF, 3.9-161 MB each; not used by the certified lazy runs; regenerable with src/genA.py / src/genB.py:
    cnf/A_n11_447_tradj_amo.cnf
    cnf/A_n12_447_tr.cnf
    cnf/A_n12_447_tr_amo.cnf
    cnf/A_n12_447_tradj.cnf
    cnf/A_n12_447_tradj_amo.cnf
    cnf/A_n12_467_tradj_amo.cnf
    cnf/A_n13_467_tradj_amo.cnf
    cnf/A_n14_477_tradj_amo.cnf
    cnf/A_n15_477_tr_amo.cnf
    cnf/A_n15_477_tradj_amo.cnf
    cnf/B_n12_447.cnf
    cnf/B_n12_447_sb.cnf
- large lazy base for the open K25 case; not used by any result, regenerable with src/genA.py:
    cnf/L_n25_577_tradj_amo.cnf
- 9.6 MB intermediate coverage CNF of a pipeline test (regenerable):
    cnc/test_fallback/coverage.cnf
- in-flight temporary files of running/finished workers (cnc/*/tmp, locks):
    cnc/B/n15_477/tmp/c796.cube
    cnc/B/n15_477/tmp/c796.ext
    cnc/B/n15_477/tmp/c797.cube
    cnc/B/n15_477/tmp/c797.ext
    cnc/lazy_n12_467_sat/tmp/c164.ext
    cnc/lazy_n12_467_sat/tmp/c164.model
- LRAT proofs of a SAT-detection test run (6.5 MB, test only):
    cnc/test_sat/proofs/coverage.lrat
    cnc/test_sat/proofs/cube0.lrat
    cnc/test_sat/proofs/cube1.lrat
    cnc/test_sat/proofs/cube2.lrat
- propagator clause dumps / final CNFs of K12 propagator tests (intermediates, regenerable):
    logs/cp_n12_447_m1.ext
    logs/cp_n12_447_m1.final.cnf
    logs/cp_n12_447_m2.ext
    logs/cp_n12_447_m2.final.cnf
- monolithic validation proofs for known values (56 MB - 2.25 GB each; checker outputs *.out are included):
    proofs/R444_n11.drat
    proofs/R444_n11.lrat
    proofs/R447_n12.drat
    proofs/R447_n12.lrat
    proofs/R467_n13.drat
    proofs/R467_n13.lrat
- third-party tools; pinned versions + build commands in artifact/README.md:
    tools/ (solver sources and binaries)
- stale LaTeX build intermediates / old PDFs:
    paper/main.aux, main.fls, main.fdb_latexmk, main.out, build.log, main.log, main_pre_*.pdf
- copies of third-party papers and of Radziszowski's survey used for the literature check (copyrighted; cite instead):
    novelty/, ref.pdf, ref.txt, sur.txt
- no longer exist: deleted after successful cake_lpr/drat-trim check by design; sizes + SHA-256 kept in status.jsonl:
    per-cube LRAT/DRAT proofs of the main runs
