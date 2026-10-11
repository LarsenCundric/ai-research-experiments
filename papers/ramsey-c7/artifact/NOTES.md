STATUS (08:58 PT Oct 11): K21 (C6,C7,C7) leg A DONE Oct 9 20:25 PT (audit PASS 1016/1016, 1961 leaves, no SAT) => R=21 certified; reported. Leg B K15 (C4,C7,C7) cnc/B/n15_477 ALIVE (cnc_tree.py PID 86180, no restart): 792/1022 top-level certified (+53 since 20:05 Oct 10; 2895 certified leaves, 34 splits, ~232 queue left); all UNSAT; no SAT. Audit FAIL only as incomplete. Overnight: cube 767 hard-checked ~10 h then OVER-CAP split (not a crash). kissat/cadical OK. Resume: cd /workspace/ramsey-c7 && nohup python3 src/cnc_tree.py B cnf/B_n15_477_sb_lazy.cnf 15 4 7 7 cnc/B/n15_477/cubes cnc/B/n15_477 --jobs 2 --solve-cap 1200 --offline-cap 2400 --check-cap 2400 >> logs/cnc_tree_B_n15_477.log 2>&1 & Rate ~4.1 top-level cubes/h since last update; ETA ~2.3 days (around Tue Oct 13 evening). Queued after K15 PASS: independent K21 leg B in cnc/B/n21_677.

# R(Cm, C7, C7), m = 3..6 — Phase 2 working notes (started 2026-10-08 PT)

## Novelty check (2026-10-08)
- Radziszowski DS1.18 (Apr 24 2026), Table XII: rows 377, 477, 577, 677 are blank (all other m,n,k<=7 filled). (sur.txt lines ~3135-3180)
- Sun Yongqi PhD thesis (Dalian UT 2006) abstract: values given for R(C_m0, C_m1, C_m2) with m2 <= m1 < m0 <= 7 (strict m1 < m0),
  i.e. the two-largest-equal case (7,7) is excluded by design. SunYWLX 2006 (J. Dalian UT 46:428-433) abstract same restriction.
  Abstract seen at http://www.abslw.com/77/abs1736577.html and exa.ai mirror of the journal paper.
- Tse 2007 (JCMCC 62) covers 335,345,346,347,355,445,446,447,455,466,467 per survey attributions; not 377-677.
- Lidicky-Pfender (arXiv 1704.03592, SIDMA 2021): flag-algebra bounds for C3C6C6, C5C6C6; nothing for C7 triples (grep).
- Wesley (arXiv 2509.03784, v. Aug 2026): R(C3,C6,C6)=R(C5,C6,C6)=15 via Kissat+Shatter (223 / 142 min); no C7 triples.
- Sun Yongqi NSFC project summary (newton.com.tw): R3(C8), 4-color C4/C6 work; no C7 triples.
- Searches (arXiv, Google-indexed, MathOverflow, Chinese terms 三色圈Ramsey数 / 圈的Ramsey数 / 三色拉姆塞数) found no claim of any of the four values.
- Not accessible: CNKI/Wanfang full text (no access), Narvaez 2015 RIT MS thesis and FSS Memphis repository (Cloudflare);
  survey only attributes 555 critical-coloring count to Narvaez.

## Bounds
| m | lower (this work, verified) | construction | heuristic prediction |
|---|---|---|---|
| 3 | R >= 25 | 4 parts x6; C3-colour = K12,12 between halves | 25 (EFRS formula 4*7-3 with roles R(C7,C7,C3); neighbours 357=557=777=25) |
| 4 | R >= 15 | two red K6 + green K6,6 + 2 extra vertices (red stars) | 15 (EFRS 2(7+2)-3) |
| 5 | R >= 25 | same as m=3 | 25 |
| 6 | R >= 21 | 4 parts x5, colour0 inside parts | 21 (EFRS-type 2(m+p)-3 would say 17, but 4(m-1)+1=21 beats it at m=6) |
No nontrivial upper bounds are listed in DS1.18 for these four entries.

## Progress log (updated 16:51 PT)
Toolchain (tools/): CaDiCaL 3.0.1, Kissat 4.0.4, drat-trim + lrat-check, cake_lpr (verified checker), march_cu (CnC), pysat, networkx 3.7.
Code (src/): rlib.py (encoding A: one-hot 3 vars/edge, DFS cycle enumeration, SB), genA.py (full CNF A), genB.py (independent
encoding B: 2 vars/edge, itertools cycle enumeration, own SB), cegar.py (lazy cycle clauses via pysat), checkA.py (DFS) /
checkB.py (networkx simple_cycles) coloring checkers, crosscheck.py (A vs networkx vs brute force), check_cnf.py (independent
clause-legitimacy checker: every clause = ALO / AMO / genuine forbidden cycle / regenerated SB clause), prove.sh (CaDiCaL LRAT ->
cake_lpr + lrat-check; Kissat DRAT -> drat-trim), circulant.py, cnc.sh (cube-and-conquer, untested).
Symmetry breaking used for proofs: 'tradj'/'tr' = lex-leader X <=lex sigma(X) for vertex transpositions (adjacent / all), variable
order = row-major edges x colors. Sound by Crawford et al. lex-leader argument (good colorings closed under vertex perms).
(Codish sb_l 'all' also implemented but NOT used for proofs — soundness not re-derived; check_cnf rejects it, negative test OK.)

Lower bounds verified by checkA + checkB (logs/lb_check.log): C3/C5: K24 (R>=25); C4: K14 (R>=15); C6: K20 (R>=21).
Crosscheck: 2730 tests, 0 disagreements (logs/crosscheck.log). Circulant exhaustive search: none on K15(C4), K21(C6), K25(C3), K25(C5)
(and none on K14 for C4), i.e. no circulant beats the bounds (logs/circulant.log).

Sanity reproductions:
- R(C3,C3,C3)=17: K16 SAT, K17 UNSAT; proof checked cake_lpr + lrat-check + drat-trim (logs/proof_R333_n17.log).
- R(C4,C4,C4)=11: K10 SAT, K11 UNSAT (~14 s); proof checked cake_lpr + lrat-check + drat-trim (logs/proof_R444_n11.log).
- R(C4,C4,C7)=12: K11 SAT (verified coloring), K12 UNSAT: kissat 143 s (tradj+AMO), 164 s (tr+AMO), encoding B 6.5 min (independent);
  LRAT proof 534 MB checked by cake_lpr (32 s) + lrat-check (logs/proof_R447_n12.log). drat-trim of kissat DRAT re-run pending.
- R(C4,C6,C7)=13: K12 SAT (verified coloring); K13 UNSAT run in progress (A_n13_467_tradj_amo, started ~16:45).
Key engineering finding: AMO clauses matter a lot (K12 C4C4C7: 143 s with AMO vs >20 min without).

Main runs in progress (started ~16:45 PT, timeout 72000 s = 20 h):
- A_n15_477_tradj_amo and A_n15_477_tr_amo: K15 for (C4,C7,C7). UNSAT => R(C4,C7,C7)=15 (with K14 lower bound). SAT => R>=16.
  K14 is SAT in 11 s (logs/A_n14_477_tradj_amo.kissat.log, coloring colorings/sat_n14_C4C7C7.txt verified).
Abandoned: lazy cegar runs on K21/K25 without AMO (killed; never converged, >1M lazy clauses).

## Update 16:58 PT
- check_cnf PASS on cnf/A_n15_477_tradj_amo.cnf (105 ALO, 315 AMO, 3248 SB, 4095 C4, 2x2,316,600 C7 clauses, 0 illegitimate)
  -> if this run returns UNSAT, the CNF side of the certificate is already validated; still need LRAT/DRAT proof re-run (cadical --lrat).
- Cube-and-conquer calibration (src/cnc.sh, march_cu depth 6) on K12 C4C4C7: 57 cubes all UNSAT, CPU sum 204 s vs 143 s monolithic,
  wall 103 s on 3 jobs (34 s cubing). => C&C overhead ~1.4x, near-linear parallel speedup. Per-cube proofs not yet wired up.
- R447_n12: kissat DRAT (299 MB) also VERIFIED by drat-trim (286 s). Both proof routes checked.
- A_n13_467 (sanity, K13 C4C6C7) still running at 12+ min, i.e. already >5x the K12 C4C4C7 time.
Estimates: K15 C4C7C7 monolithic plausibly 4 h .. 2+ weeks single core (extrapolating 143 s at K12 w/ one C7 colour and >12 min at K13);
the 20 h timeout may not suffice. K21 C6C7C7 full CNF ~84M C7 clauses (~3 GB) and K25 ~346M: plain SAT not realistic on this box;
need lazy clause generation (CaDiCaL external propagator) + structural lemmas, or a FSS-style human/computer hybrid proof.

## Update 17:18 PT (session 3)
- A_n13_467_tradj_amo (PID 135253) finished: K13 C4C6C7 UNSAT, kissat 777 s -> reproduces R(C4,C6,C7)=13 (known, Sun1+/Tse3).
  Proof run started: check_cnf + prove.sh -> logs/checkcnf_n13_467.log, logs/proof_R467_n13.log.
- prop/cycprop.cpp: CaDiCaL 3.0.1 external propagator (lazy cycle clauses). modes: 0 model-only, 1 conflicts on partial
  assignment, 2 conflicts + unit propagation. Base CNFs with lazy colours omitted: cnf/L_*.cnf (genA.py --eager-upto 5).
  K11 C4C4C7 SAT in all modes. Mode 0 on K12 too slow (>14 min, killed).

## Certified cube-and-conquer (src/cnc_lrat.py)  [ready, tested 17:21 PT]
Argument: CNC_ARGUMENT.md. Steps: check_cnf -> march_cu cubes -> coverage certificate (CNF of negated cubes, CaDiCaL LRAT,
cake_lpr) -> each cube = F + units, CaDiCaL binary LRAT -> cake_lpr; results appended to WORKDIR/status.jsonl; resumable
(re-running the same command skips certified cubes; meta.json pins the formula sha256). Proofs deleted after successful check
(sha256 + size logged) unless --keep-proofs. SAT cube -> stops, writes model_cube<i>.txt (decode: src/model2col.py).
Test on K12 C4C4C7 (cnc/test_n12_447): depth 6 -> 57 cubes, coverage VERIFIED, 57/57 cubes VERIFIED by cake_lpr;
CPU solve 72.9 s (CaDiCaL) + check 94.8 s; wall 57 s on 3 jobs (+34 s march). Resume test (30 of 57 pre-done): OK.
SAT test (K11 C4C4C7, depth 4): stops with model files. OK.

LAUNCH COMMAND for K15 (C4,C7,C7) (only after PIDs 135075/135076 are stopped; ~1-2.5 GB RAM per job, check `free -g`):
  cd /workspace/ramsey-c7 && nohup python3 src/cnc_lrat.py cnf/A_n15_477_tradj_amo.cnf cnc/n15_477 \
     --depth 12 --jobs 6 --n 15 --cycles 4 7 7 --sb tradj --cube-timeout 21600 > logs/cnc_n15_477.log 2>&1 &
  (depth 12 -> up to ~4096 cubes; adjust after seeing the first cube times. Resume = same command. Progress: tail logs/cnc_n15_477.log;
   final verdict in cnc/n15_477/summary.json. Timed-out cubes: rerun the script on that cube's formula in its own workdir.)

## Item 3: does the FSS 2003 hand proof of R(C7,C7,C7)=25 extend to (C3,C7,C7), (C5,C7,C7)?  [17:30 PT]
Source read: novelty/fss3.txt (DMGT 23 (2003) 141-158, via bibliotekanauki.pl/articles/743391.pdf). The paper only sketches most
lemma proofs; full details are in A. Schelten's PhD thesis (ref [12] in the paper), which I have not obtained.
FSS skeleton: K25 has 300 edges, so some colour has >= 100 edges. Define ext0(C7,n) = max edges of a C7-free, non-bipartite graph
with no B7,7 and whose complement has no K*12 (12 vertices missing <= 4 edges). Lemmas 3-5: exact ext0 for n=7..13 (31 at n=12,
33 at n=13). Lemma 6: ext0(C7,n) upper bounds for n=14..25 by induction on n, ending at ext0(C7,25) <= 99. Lemma 1: a 2-coloured K*12
forces a monochromatic C7. Lemma 2: a monochromatic B7,7 forces a monochromatic C7. Then: the >=100-edge colour is bipartite (a part of
13 vertices is 2-coloured, R(C7,C7)=13), or covered by Lemma 1, Lemma 2, or Lemma 6.
What transfers to (Cm,C7,C7), m=3,5:
 - If a C7-colour (1 or 2) has >= 100 edges: the bipartite case works (R(C3,C7)=R(C5,C7)=13); Lemma 6 is purely about C7-free graphs,
   so it transfers verbatim. Lemmas 1 and 2 do NOT transfer verbatim: their proofs use ext0(C7,12)=31 / ext0(C7,13)=33 for BOTH other
   colours, and use C7-specific path arguments in all three colours. For our case one of the other colours is Cm-free. They'd need
   redoing with the analogous non-bipartite Cm-free numbers (for C3 on 12 vertices, max non-bipartite triangle-free = floor(11^2/4)+1 = 31,
   the same number, but the extremal graphs differ). These are finite, local statements (they live on 12-13 vertex sets plus attachments)
   and look SAT-checkable.
 - NEW case not covered at all: neither C7-colour has >= 100 edges, so the Cm-colour has >= 102 edges. Triangle-free and C5-free graphs on
   25 vertices can have up to 156 edges (K12,13), and dense non-bipartite examples exist (C5-blow-up 5^5 has 125 edges, triangle-free).
   So the pigeonhole step fails and a different argument is needed for a dense Cm colour. Useful facts: for m=3 every colour-0
   neighbourhood is colour-0-independent, so it is 2-coloured in colours 1,2 => colour-0 degree <= 12 = R(C7,C7)-1, with equality forcing a
   (C7,C7)-critical K12 (structure known: two K6 + K6,6). For m=5 the colour-0 neighbourhood has no colour-0 P4 (weaker).
 - Trust issue: Lemma 6 (the core counting lemma) is only sketched in the paper; a new paper building on it would have to either cite
   Schelten's thesis or re-verify ext0(C7,n) <= ... for n<=25, itself a nontrivial (probably computer-assisted) extremal computation.
Verdict: no direct extension. A hybrid is plausible but substantial: Case A (a C7 colour has >=100 edges) = FSS + re-proved Lemma 1/2
analogues (SAT-checkable local lemmas); Case B (dense Cm colour) = new structural argument (degree <= 12, critical-neighbourhood
structure, Andrasfai/stability-type reasoning) with SAT-checked local cases on <= ~16 vertices. Rough effort 4-8 weeks;
odds ~25-30% for m=3 (stronger local structure), ~15% for m=5. Plain SAT on K25 remains unrealistic.

## Item 2: external propagator results  [17:37 PT]
cycprop mode 1 (conflict clauses on partial assignments) is the default; mode 2 (also unit clauses) was slightly slower on K12.
Certification route: cycprop writes every external clause; final CNF = base + external clauses; check_cnf.py on final CNF;
offline CaDiCaL LRAT on final CNF; cake_lpr. Wrapper: prop/propcert.sh n a b c mode tag [timeout].
| instance | known | cycprop | full-CNF kissat | certification |
| K11 C4C4C7 | SAT | SAT 0.2 s, colouring checkA+checkB GOOD | 1 s | - |
| K12 C4C4C7 | UNSAT (R=12) | UNSAT 91.6 s, 40,019 C7 clauses (vs 285,120 full) | 143 s | check_cnf PASS, offline CaDiCaL 89.7 s, 246 MB LRAT, cake_lpr VERIFIED |
| K13 C4C6C7 | UNSAT (R=13) | UNSAT 577 s, 116,299 ext clauses | 777 s | check_cnf PASS, offline proof running |
| K14 C4C7C7 | SAT | SAT 0.01 s, GOOD | 11 s | - |
| K14 C6C6C7 | SAT | SAT 1.3 s, GOOD | - | - |
| K15 C6C6C7 | UNSAT (R=15) | running (6 h cap), started 17:25 | - | - |
Cube-and-conquer with cycprop under assumptions (prop/sample_est.sh): on K12 C4C4C7 all 57 cubes total 51 s CPU (vs 91 s monolithic).
K21 C6C7C7: 10-min warm-up run generated 1.12M external clauses (full C7 clause count would be 83.7M); no answer.
Estimation for K21 by cube sampling started 17:37: depth 10, 6 random cubes, 1200 s cap, 2 jobs -> logs/est_n21_677_d10.log.

## Update 17:50 PT (session 4)
- R(C4,C6,C7)=13 sanity (K13 UNSAT) CERTIFIED two ways: full CNF (check_cnf PASS) CaDiCaL 1019 s, 2.25 GB LRAT -> cake_lpr VERIFIED
  (130 s) + lrat-check VERIFIED (37 s); lazy route: cycprop 577 s -> final CNF check_cnf PASS -> offline CaDiCaL 515 s, 1.06 GB LRAT ->
  cake_lpr VERIFIED (85 s). Kissat DRAT + drat-trim leg of prove.sh still running (PID 160282) -> logs/proof_R467_n13.log.
- K21 estimate: march_cu segfaulted on base + all 1.12M warm clauses; with the first 100k warm clauses it works: 1016 cubes at depth 10
  (/tmp/w100000.cubes, 6 leaves refuted by march itself). Sampling restarted from those cubes (see below).
- FIX needed in cnc_lrat.py: march_cu omits leaves it refutes itself, so "negated cubes alone UNSAT" can fail. Patched: if pure coverage
  CNF is SAT, fall back to coverage CNF = F + negated cubes (still sound: any model of F satisfies some cube).

## Update 17:58 PT — C&C launch procedure REVISED (march_cu segfaults on the full K15 CNF)
- march_cu crashes (exit 139 after 10 s) on cnf/A_n15_477_tradj_amo.cnf (4.6M clauses), also on base + 1.12M warm clauses for K21.
  It works on base + <=100k (also 400k) clauses. New helper src/make_cubes_lazy.sh cubes the lazy base CNF + first 100k cycle clauses
  from a cycprop warm-up (same generator, same variable numbering incl. SB aux vars). Cubes are only a split: coverage is certified by
  cnc_lrat.py (negated cubes alone, or fallback F + negated cubes), each cube solved on the FULL formula F with LRAT + cake_lpr.
- Tests on K12 C4C4C7, all end to end with per-cube cake_lpr-checked LRAT:
  * march cubes on full F (cnc/test_n12_447): 57/57 certified, coverage VERIFIED.
  * one cube deleted (cnc/test_fallback): pure coverage SAT -> fallback F + negated cubes UNSAT, cake_lpr VERIFIED; 56/56 certified.
  * lazy cubes from make_cubes_lazy.sh (cnc/test_lazycubes): 57/57 certified, coverage VERIFIED, CPU solve 72 s + check 90 s.
  * resume after partial status: OK; SAT detection: OK.
- K15 cubes pre-generated now into cnc/n15_477/cubes (depth 10, 300 s warm-up) -> logs/make_cubes_n15_477.log.
- R467_n13 kissat DRAT leg: kissat 820 s, 1.25 GB DRAT; drat-trim running.

LAUNCH COMMAND (supersedes the one above; morning check uses this). Only after stopping PIDs 135075/135076:
  cd /workspace/ramsey-c7
  [ -s cnc/n15_477/cubes ] || src/make_cubes_lazy.sh 15 4 7 7 10 300 100000 cnc/n15_477/cubes
  nohup python3 src/cnc_lrat.py cnf/A_n15_477_tradj_amo.cnf cnc/n15_477 --jobs 6 --n 15 --cycles 4 7 7 --sb tradj \
      --cube-timeout 21600 > logs/cnc_n15_477.log 2>&1 &
  Monitor: tail logs/cnc_n15_477.log ; verdict: cnc/n15_477/summary.json ; resume: rerun the same nohup line.
  Per-cube overhead on K15 is ~25 s (writing/parsing the 160 MB CNF in CaDiCaL and cake_lpr), ~7 core-hours for ~1000 cubes.
  RAM: ~1-2.5 GB per job; use --jobs 4 if `free -g` shows < 10 GB available.

## Update 18:08 PT — K21 (C6,C7,C7) estimate
Cubes: 1016 (march on lazy base + 100k warm clauses, depth 10). Solved 35 sampled cubes with cycprop under assumptions (no proofs):
ALL UNSAT. Times (s): 26 cubes < 15 s; 45, 47, 68, 85, 114, 213, 1110; one more still running (>10 min at 18:07).
Sum 1735 s / 35 cubes = 50 s mean (66 s if the running cube is counted at 650 s). Naive total ~1016 x 50-66 s = 0.6-0.8 core-days;
heavy tail + sample bias (second sample over-represents low-index cubes, which look harder) -> honest range 0.5-10 core-days,
i.e. likely feasible on this 8-core box in hours to a few days. Certification route for K21 must be lazy per cube (full CNF = 84M
clauses): cube i -> cycprop under assumptions -> check_cnf(base + ext_i) -> CaDiCaL LRAT on base + ext_i + cube units -> cake_lpr;
plus coverage certificate. Not yet implemented (next step: 'cnc_lazy' variant of cnc_lrat.py).
Started 18:08: 8 random K15 C4C7C7 cubes with cycprop (600 s cap, 2 jobs) -> prop/est_n15_477/results.txt, to see if the lazy C&C
route beats the monolithic kissat runs.

## Update 18:25 PT — samples finished
- K21 C6C7C7: 36 sampled cubes (of 1016) ALL UNSAT, sum 2407 s, mean 67 s, max 1110 s (cubes 380: 1110 s, 85: 673 s, 339: 213 s).
  Naive total 1016 x 67 s ~ 19 core-hours; with heavy tail/sample bias: ~0.5-5 core-days. Feasible on this box once a certified
  lazy C&C ('cnc_lazy') exists.
- K15 C4C7C7 with cycprop on the pre-generated cubes (cnc/n15_477/cubes, 988 cubes): 68 random cubes ALL UNSAT, mean 3.5 s,
  max 178 s, sum 240 s. Naive total ~1 core-hour (allow 2-10x for the tail). This is far cheaper than the monolithic kissat runs
  (PIDs 135075/135076, still running after ~1.6 h). These sample runs are NOT certified (no proofs).
- Recommendation for the morning check: stop 135075/135076 and run the certified C&C. Either (a) cnc_lrat.py as documented
  above (full F per cube, ~25 s/cube parse overhead => ~7 core-hours overhead + solve), or (b) better, a lazy certified variant
  (per cube: cycprop -> check_cnf(base+ext_i) -> CaDiCaL LRAT on base+ext_i+units -> cake_lpr) which would likely certify K15 in
  ~1-3 core-hours and is the only realistic route for K21.
- 18:27 PT: R467_n13 kissat DRAT (1.25 GB) VERIFIED by drat-trim (1533 s). R(C4,C6,C7)=13 now checked by cake_lpr, lrat-check and drat-trim. Note: other agents' kissat jobs (pnp-lab) now share this box's cores.

## 18:31 PT — cube-by-cube lazy certified solver (src/cnc_lazy.py)
Per cube i: cycprop(lazy base L, assumptions = cube) -> E_i (cycle clauses added) ; check_cnf.py E_i cyclesonly (each clause
re-verified as a genuine monochromatic forbidden cycle; negative test: ALO clause injected -> FAIL) ; F_i = L + E_i + cube units ;
CaDiCaL --lrat F_i ; cake_lpr. Base L checked once with check_cnf (ALO/AMO/SB/short cycles). Coverage: negated cubes UNSAT (cake_lpr),
fallback L + negated cubes (fails closed if that is SAT). SAT cube -> model decoded, checkA + checkB. Proofs/E_i/F_i deleted after
cake_lpr VERIFIED (sha256 + sizes kept in status.jsonl). Memory per job: tens of MB (vs ~4 GB cake_lpr on the full CNF).
Tests:
- K12 C4C4C7 (57 cubes, 2 jobs): UNSAT CERTIFIED, 122 s wall (solve 117 / offline 68 / check 54 core-s). cnc/lazy_n12_447.
- K12 C4C6C7 (256 cubes, expect SAT): cube 164 SAT, colouring cnc/lazy_n12_467_sat/model_cube164.txt GOOD by checkA and checkB.
- K13 C4C6C7 (887 cubes, 1 job): running, 159/887 certified after 3 min.
- K15 C4C7C7: 258/988 certified after 5.5 min (solve 520, offline 278, check 129 core-s; max cube 94 s).

## 18:48 PT — RESULT: R(C4,C7,C7) = 15 (certified)
- cnc_lazy K15 C4C7C7: 988/988 cubes UNSAT, each: added cycle clauses re-verified (check_cnf cyclesonly), CaDiCaL LRAT, cake_lpr
  VERIFIED. Coverage (negated cubes alone) cake_lpr VERIFIED. Base check_cnf PASS. Wall 967 s on 3 jobs (18:25-18:41 PT);
  core time solve 1672 s + offline LRAT 756 s + cake_lpr 338 s (~46 core-min). Max cube solve 198 s.
- Independent audit (src/audit_cnc.py -> cnc/lazy_n15_477/audit.txt): sha256 of base+cubes unchanged, records for all 988 cubes,
  literals match, all verdicts present; coverage re-proved with a different solver/checker (kissat DRAT + drat-trim). PASS.
- Checker negative tests (cyclesonly): C4 clause in a C7 colour -> FAIL; C7 clause in the C4 colour -> FAIL; truncated cycle -> FAIL;
  ALO clause -> FAIL; genuine clauses -> PASS.
- Lower bound: colorings/lb_C4C7C7_n14.txt re-checked GOOD by checkA and checkB.
- Pipeline validation of cnc_lazy on known values: K12 C4C4C7 UNSAT (R447=12) certified; K13 C4C6C7 UNSAT (R467=13) certified,
  887 cubes, 582 s wall on 1 job (vs monolithic kissat 777 s, full CaDiCaL LRAT 1019 s); K12 C4C6C7 -> SAT cube, colouring GOOD.
- Trust base: soundness of lex-leader SB for vertex transpositions (Crawford et al.), check_cnf.py (cycle/ALO/AMO/SB recognizer),
  cake_lpr (verified checker), cnc_lazy.py's assembly of F_i (audited), and the coverage argument (CNC_ARGUMENT.md).
  Still to do for the paper: a second fully independent leg (e.g. Encoding B per cube or the monolithic run 135075 finishing).

## 18:48 PT — K21 (C6,C7,C7) certified run launched (cores freed by K15)
- Certification overhead measured on sampled K21 cubes: cube 339 (cycprop solve 213 s, 211k added clauses): check_cnf 2 s,
  offline CaDiCaL LRAT 119 s (184 MB proof), cake_lpr 18 s => overhead ~0.65x solve. (cube 380 measurement: cnc/k21_overhead/log.txt)
- Estimate: uncertified solve ~19 core-h naive (sample mean 67 s x 1016), x ~1.7 for certification => ~30 core-h; at 3 jobs
  ~10 h wall; heavy-tail range ~5 h - 3 days wall. Per-cube cap 12 h; any timed-out cube gets re-split (rerun march on it).

## 19:27 PT — leg B (independent second certification) + paper + artifact
- New, independent of leg A: src/genB.py --eager-upto (regression: identical output to original genB for full CNF), src/check_cnfB.py
  (encoding-B legitimacy: exclusion / cycle (simple-cycle test) / regenerated genB SB; negative tests FAIL as expected),
  src/test_sbB.py (brute force: lex-min of full S_n orbit satisfies genB SB on K5 (400) and K6 (60) random colourings; lex-max
  violates 400/400 -> test has power), src/lazyB.py (PySAT CaDiCaL 1.9.5 CEGAR with own cycle DFS), src/make_cubesB.sh,
  src/cnc_lazyB.py (per cube: lazyB -> check_cnfB cyclesonly -> kissat DRAT on B+E_i+units -> drat-trim; coverage by kissat+drat-trim
  AND cadical+cake_lpr), audit_cnc.py extended for leg B.
- lazyB K14 C4C7C7: SAT, colouring cnc/B/lazyB_K14_C4C7C7_sat.col GOOD by checkA and checkB.
- Leg B K12 C4C4C7 (121 cubes, 1 job): 100/121 certified, continuing. Leg B K15: 1022 cubes (warm 87k clauses, depth 10),
  coverage verified both ways, started 19:22 PT, ~1 cube/s early on.
- NOTE: the FSS 2003 paper is Faudree, Schelten, Schiermeyer (DMGT 23 (2003) 141-158), not Faudree-Schelp-Sheehan.
- Paper draft compiled (6 pages): paper/main.pdf; TODO markers for K21, leg-B numbers, affiliation, AI disclosure, KoSS2/LidP pages.

## 09:20 PT Oct 9 — adaptive re-splitting (src/cnc_tree.py), restart of K21 leg A and K15 leg B
Overnight: K21 198/1016 (cube 199: 32,392 s solve; 9 cubes >20 min used 66,872 s of 74k s solve total); K15 leg B 559/1022
(cube 539: 11,880 s solve + 33,448 s drat-trim; drat-trim cost blows up only on big cubes: for cubes <60 s solve, drat-trim ~0.7x solve).
New driver src/cnc_tree.py (both legs; compatible with old workdirs/status.jsonl, old records = integer cube ids):
- node over cap (lazy solve > 1200 s, offline proof > 2400 s, or proof check > 2400 s) -> split: march_cu -d 6 on base + <=1e5 cycle
  clauses the lazy solver added + units(parent); children = parent literals + subcube literals; split coverage certificate
  units(P) & AND not(D_j) UNSAT (fallback base & units(P) & AND not(D_j)), checked with the leg's own pair (A: CaDiCaL LRAT +
  cake_lpr; B: Kissat DRAT + drat-trim AND CaDiCaL LRAT + cake_lpr). Recorded in splits.jsonl + splits/<id>.cubes (sha256).
  If a split fails (march finds <2 cubes or coverage SAT), the node is rerun without caps.
- audit_cnc.py rewritten tree-aware: re-proves top coverage and EVERY split coverage itself with kissat+drat-trim from the stored files,
  checks literal containment, file hashes, leaf records, and recursive certification of all top-level cubes.
  Tests: K12 C4C4C7 leg A with solve cap 2 s -> 13 splits, 144 leaves, 57/57 certified, audit PASS. Negative tests: dropping a child from
  a split (hash updated) -> FAIL; deleting one leaf record -> FAIL. Leg B with cap 5 s + kill mid-run -> resume OK (82 kept, 1 split kept).
- Leg B proof choice (for the paper): kept Kissat 4.0.4 DRAT + drat-trim (fully different solver/checker pair from leg A's CaDiCaL +
  cake_lpr). The 9 h drat-trim checks came only from 3 huge cubes; with the 20-min solve cap + 40-min check cap, oversized cubes are
  split instead, so drat-trim never sees huge proofs. Fallback if throughput is still poor: CaDiCaL LRAT + lrat-check (different checker).
