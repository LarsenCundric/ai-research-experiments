#!/usr/bin/env python3
"""Full CNF, encoding A (rlib one-hot, DFS cycle enumeration). usage: genA.py n a b c out.cnf --sb {none,adj,all,tr,tradj} [--amo]"""
import sys, argparse
from rlib import EncA, kcycles, lex_sb, tr_sb
ap = argparse.ArgumentParser()
ap.add_argument("n", type=int); ap.add_argument("a", type=int); ap.add_argument("b", type=int); ap.add_argument("c", type=int)
ap.add_argument("out"); ap.add_argument("--sb", default="none"); ap.add_argument("--amo", action="store_true"); ap.add_argument("--eager-upto", type=int, default=99)
A = ap.parse_args()
n, L = A.n, (A.a, A.b, A.c)
enc = EncA(n, amo=A.amo)
base = enc.base()
sb = lex_sb(enc, A.sb) if A.sb in ("adj", "all") else (tr_sb(enc, "all" if A.sb == "tr" else "adj") if A.sb in ("tr", "tradj") else [])
full = [((1 << n) - 1) ^ (1 << v) for v in range(n)]
cnt = len(base) + len(sb)
with open(A.out, "w") as f:
    f.write(f"c encA n={n} cycles={L} sb={A.sb} amo={A.amo}\n")
    # count cycles first for header
    cyc = [(kcycles(full, n, L[c]) if L[c] <= A.eager_upto else []) if L[c] not in L[:c] else None for c in range(3)]
    for c in range(3):
        if cyc[c] is None: cyc[c] = cyc[L.index(L[c])]
    cyc = [cyc[c] if L[c] <= A.eager_upto else [] for c in range(3)]
    total = cnt + sum(len(x) for x in cyc)
    f.write(f"p cnf {enc.nv} {total}\n")
    for cl in base + sb:
        f.write(" ".join(map(str, cl)) + " 0\n")
    for c in range(3):
        for cy in cyc[c]:
            f.write(" ".join(map(str, enc.cycle_clause(c, cy))) + " 0\n")
print(f"wrote {A.out}: vars={enc.nv} clauses={total}")
