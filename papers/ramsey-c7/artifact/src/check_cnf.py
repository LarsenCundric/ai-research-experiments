#!/usr/bin/env python3
"""Independent CNF legitimacy checker for encoding-A formulas (one-hot vars 3e+c+1, edges in row-major order).
Every clause must be (i) an at-least-one-color clause, (ii) a forbidden monochromatic cycle clause whose edges
really form a simple cycle of the forbidden length for that color, or (iii) one of the symmetry-breaking clauses,
regenerated here from the specification (lex-leader X <=lex sigma(X) for vertex transpositions).
usage: check_cnf.py file.cnf n a b c sbmode   (sbmode in none,tradj,tr)"""
import sys
from collections import Counter

def regen_sb(n, mode, nv0):
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    pos = {e: k for k, e in enumerate(edges)}
    def v(i, j, c):
        if i > j: i, j = j, i
        return 3 * pos[(i, j)] + c + 1
    if mode == "none": return set(), nv0
    T = [(i, i + 1) for i in range(n - 1)] if mode == "tradj" else [(i, j) for i in range(n) for j in range(i + 1, n)]
    out = set(); nv = nv0
    for (i, j) in T:
        sw = {i: j, j: i}
        X = []; Y = []
        for (u, w) in edges:
            for c in range(3):
                x = v(u, w, c); y = v(sw.get(u, u), sw.get(w, w), c)
                if x != y: X.append(x); Y.append(y)
        e_prev = 0
        for t in range(len(X)):
            pre = (-e_prev,) if e_prev else ()
            out.add(frozenset(pre + (-X[t], Y[t])))
            if t + 1 < len(X):
                nv += 1
                out.add(frozenset(pre + (-X[t], -Y[t], nv))); out.add(frozenset(pre + (X[t], Y[t], nv)))
                e_prev = nv
    return out, nv

def main():
    f, n, a, b, c, mode = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
    # mode 'cyclesonly': every clause must be a genuine forbidden-cycle clause (used for solver-added clause files)
    L = (a, b, c)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m = len(edges)
    sb, nvmax = regen_sb(n, "none" if mode == "cyclesonly" else mode, 3 * m)
    if mode == "cyclesonly": nvmax = 3 * m
    kinds = Counter(); bad = 0; seen = set()
    for line in open(f):
        if line[0] in "cp": continue
        lits = list(map(int, line.split()))
        assert lits[-1] == 0
        lits = lits[:-1]
        if any(abs(x) > nvmax for x in lits): bad += 1; continue
        if mode == "cyclesonly": pass
        elif all(x > 0 for x in lits) and len(lits) == 3 and all(x <= 3 * m for x in lits):
            es = {(x - 1) // 3 for x in lits}; cs = {(x - 1) % 3 for x in lits}
            if len(es) == 1 and cs == {0, 1, 2}: kinds["alo"] += 1; continue
        if mode != "cyclesonly" and len(lits) == 2 and all(x < 0 and -x <= 3 * m for x in lits) and (-lits[0]-1)//3 == (-lits[1]-1)//3 and lits[0] != lits[1]:
            kinds["amo"] += 1; continue
        if all(x < 0 and -x <= 3 * m for x in lits):
            cs = {(-x - 1) % 3 for x in lits}
            if len(cs) == 1:
                col = cs.pop(); E = [edges[(-x - 1) // 3] for x in lits]
                if len(set(E)) == len(E) == L[col]:
                    deg = Counter(); adj = {}
                    for (u, w) in E:
                        deg[u] += 1; deg[w] += 1; adj.setdefault(u, []).append(w); adj.setdefault(w, []).append(u)
                    if len(deg) == L[col] and all(d == 2 for d in deg.values()):
                        start = E[0][0]; seenv = {start}; st = [start]
                        while st:
                            x = st.pop()
                            for y in adj[x]:
                                if y not in seenv: seenv.add(y); st.append(y)
                        if len(seenv) == L[col]:
                            kinds[f"cycle_color{col}_C{L[col]}"] += 1; continue
        if frozenset(lits) in sb: kinds["sb"] += 1; continue
        bad += 1
        if bad <= 5: print("ILLEGITIMATE clause:", lits)
    print(dict(kinds), "illegitimate:", bad)
    print("CNF CHECK", "PASS" if bad == 0 else "FAIL")
    sys.exit(0 if bad == 0 else 1)

main()
