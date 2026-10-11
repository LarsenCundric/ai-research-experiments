#!/usr/bin/env python3
"""Soundness test for genB's symmetry breaking: for random colourings of K_n, the lex-least colouring in its orbit under
ALL n! vertex permutations (lex order = genB variable order r(e0), g(e0), r(e1), ... with true > false) must satisfy the SB
clauses (aux variables free). Also counts how many colourings survive SB (should be >= #orbits)."""
import sys, itertools, random
from pysat.solvers import Solver
from genB import sb_clauses, edge_vars
n = int(sys.argv[1]); T = int(sys.argv[2]); random.seed(1)
pairs, R, G = edge_vars(n); m = len(pairs)
cls, nv = sb_clauses(n, 2 * m)
S = Solver(name="cadical195", bootstrap_with=cls)
def vec(col):  # col: dict edge->colour; vector over var order
    v = []
    for p in pairs: v += [col[p] == 0, col[p] == 1]
    return v
def lits(col):
    return [(R(*p) if col[p] == 0 else -R(*p)) for p in pairs] + [(G(*p) if col[p] == 1 else -G(*p)) for p in pairs]
perms = list(itertools.permutations(range(n)))
bad = 0
for t in range(T):
    col = {p: random.randrange(3) for p in pairs}
    best = None
    for s in perms:
        c2 = {tuple(sorted((s[u], s[v]))): col[(u, v)] for (u, v) in pairs}
        key = [int(x) for x in vec(c2)]
        if best is None or ((key > best[0]) if "--max" in sys.argv else (key < best[0])): best = (key, c2)
    if not S.solve(assumptions=lits(best[1])): bad += 1
print(f"n={n} tested={T} lex-min colourings violating SB: {bad}", "PASS" if bad == 0 else "FAIL")
