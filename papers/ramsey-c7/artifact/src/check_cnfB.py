#!/usr/bin/env python3
"""Legitimacy checker for encoding B (independent of rlib / check_cnf.py).
  check_cnfB.py FILE n a b c MODE      MODE = base (exclusion / forbidden-cycle / genB SB clauses) | cyclesonly
Variables: r(e) = 2e+1 (colour 0), g(e) = 2e+2 (colour 1), colour 2 = neither, edges e in itertools.combinations order.
Cycle clause for colour 0: {-r(e) : e in C}; colour 1: {-g(e)}; colour 2: {r(e), g(e)}; C must be a simple cycle of the length
forbidden in that colour (k distinct edges, k vertices, all degree 2, connected)."""
import sys, itertools
from collections import Counter

def is_simple_cycle(edges, k):
    if len(edges) != k or len(set(edges)) != k: return False
    deg = Counter(); adj = {}
    for u, v in edges:
        deg[u] += 1; deg[v] += 1; adj.setdefault(u, []).append(v); adj.setdefault(v, []).append(u)
    if len(deg) != k or any(d != 2 for d in deg.values()): return False
    start = edges[0][0]; seen = {start}; st = [start]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen: seen.add(y); st.append(y)
    return len(seen) == k

def main():
    f, n, a, b, c, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    L = (a, b, c)
    pairs = list(itertools.combinations(range(n), 2)); m = len(pairs)
    allowed_sb = set()
    if mode == "base":
        from genB import sb_clauses
        s, _ = sb_clauses(n, 2 * m)
        allowed_sb = {tuple(sorted(cl)) for cl in s}
    kinds = Counter(); bad = 0; badex = []
    for line in open(f):
        if line[0] in "cp" or not line.strip(): continue
        lits = [int(x) for x in line.split()]
        assert lits[-1] == 0; lits = lits[:-1]
        kind = None
        if all(abs(x) <= 2 * m for x in lits):
            if mode == "base" and len(lits) == 2 and all(x < 0 for x in lits):
                e1, e2 = (-lits[0] - 1) // 2, (-lits[1] - 1) // 2
                if e1 == e2 and {-lits[0], -lits[1]} == {2 * e1 + 1, 2 * e1 + 2}: kind = "exclusion"
            if kind is None and all(x < 0 for x in lits):
                par = {(-x) % 2 for x in lits}
                if len(par) == 1:
                    col = 0 if par == {1} else 1
                    es = [pairs[(-x - 1) // 2] for x in lits]
                    if is_simple_cycle(es, L[col]): kind = f"cycle_col{col}_C{L[col]}"
            if kind is None and all(x > 0 for x in lits) and len(lits) % 2 == 0:
                ids = Counter((x - 1) // 2 for x in lits)
                if all(v == 2 for v in ids.values()) and len(set(lits)) == len(lits):
                    es = [pairs[e] for e in ids]
                    if is_simple_cycle(es, L[2]): kind = f"cycle_col2_C{L[2]}"
        if kind is None and mode == "base" and tuple(sorted(lits)) in allowed_sb: kind = "sb"
        if kind is None:
            bad += 1
            if len(badex) < 3: badex.append(lits)
        else:
            kinds[kind] += 1
    print(dict(kinds), "illegitimate:", bad, badex if bad else "")
    print("CNF-B CHECK PASS" if bad == 0 else "CNF-B CHECK FAIL")
    sys.exit(0 if bad == 0 else 1)

if __name__ == "__main__":
    main()
