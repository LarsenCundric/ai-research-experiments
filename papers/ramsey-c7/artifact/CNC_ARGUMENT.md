# Why the certified cube-and-conquer run proves R(C4,C7,C7) <= 15 (if all checks pass)

Let F be cnf/A_n15_477_tradj_amo.cnf. Variables 1..315 are x(e,c) = 3e+c+1 for the 105 edges e of K15 (row-major) and colours c in {0,1,2};
the rest are auxiliary variables of the symmetry-breaking (SB) constraints.

1. Encoding soundness (checked by src/check_cnf.py, independent of the generator): every clause of F is
   (a) an at-least-one-colour clause for an edge, (b) an at-most-one clause (-x(e,a) v -x(e,b)),
   (c) a clause OR_{e in C} -x(e,c) where the edges of C form a simple cycle of length 4 (c=0) or 7 (c=1,2), or
   (d) one of the lex-leader clauses X <=lex sigma(X) for an adjacent vertex transposition sigma=(i i+1), regenerated
       from the specification (with the same auxiliary "equal-prefix" variables).
   If a 3-colouring of K15 with no red C4 and no green/blue C7 existed, then so would every relabelling of it (the set of good
   colourings is invariant under vertex permutations). Take the relabelling whose one-hot vector X is lexicographically least in
   its orbit. It satisfies (a),(b),(c), and X <=lex sigma(X) for every sigma, so (d) is satisfiable by setting the auxiliary
   variables to their intended values (Crawford-Ginsberg-Luks-Roy lex-leader argument). Hence: good colouring exists => F SAT.
2. Coverage: march_cu produces cubes Q_1..Q_k (conjunctions of literals). Let T = { NOT Q_i : i = 1..k } (one clause per cube).
   T is shown UNSAT by CaDiCaL with an LRAT proof checked by cake_lpr (coverage.json). T UNSAT means every total assignment
   falsifies some clause NOT Q_i, i.e. satisfies some cube Q_i. (We do NOT rely on march_cu's tree structure being correct.)
3. Each F_i = F AND Q_i (Q_i added as unit clauses) is shown UNSAT by CaDiCaL with a binary LRAT proof checked by cake_lpr
   (a formally verified checker, CakeML). Results with proof sha256 are in status.jsonl.
4. If F had a model M, then by 2 M satisfies some Q_i, so M is a model of F_i, contradicting 3. So F is UNSAT, so by 1 no good
   colouring of K15 exists: R(C4,C7,C7) <= 15. With the verified K14 colouring (colorings/lb_C4C7C7_n14.txt), R(C4,C7,C7) = 15.
Trusted base: check_cnf.py (short, readable), cake_lpr (verified), the cube file and formula files identified by sha256 in meta.json.

## Addendum (18:48 PT Oct 8): the lazy per-cube route actually used (src/cnc_lazy.py)
The full-CNF route above was aborted (cake_lpr needs ~4.2 GB per check on the 4.6M-clause formula; parallel checks hit OOM).
The certificate used instead:
1. L = lazy base (genA.py --eager-upto 5: ALO, AMO, tradj lex-leader SB, all forbidden cycles of length <= 5). check_cnf.py: every
   clause is ALO / AMO / a genuine forbidden monochromatic cycle / a regenerated SB clause. So the lex-leader representative c* of
   any good colouring satisfies L (in the one-hot encoding).
2. Coverage: the clauses {not Q_i} are UNSAT (CaDiCaL LRAT + cake_lpr; independently kissat DRAT + drat-trim). So every
   assignment, in particular c*, satisfies some cube Q_j.
3. For each cube i: E_i = the clauses the lazy solver added; check_cnf.py cyclesonly verifies every clause of E_i forbids a
   genuine monochromatic C_k in a colour where C_k is forbidden, so c* satisfies E_i. F_i = L + E_i + units(Q_i) is UNSAT by a
   cake_lpr-verified LRAT proof. Hence c* does not satisfy Q_i.
2 and 3 contradict, so no good colouring of K_n exists. The solver (cycprop) is untrusted: only E_i (checked) and the offline proof
(checked) enter the argument. audit_cnc.py re-checks the bookkeeping (hashes, one certified record per cube, literals match).
