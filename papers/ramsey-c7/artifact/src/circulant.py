#!/usr/bin/env python3
"""Exhaustive search over circulant 3-colorings of K_n (color of edge {i,j} depends on min(|i-j|, n-|i-j|))
avoiding C_a in color 0, C_b in color 1, C_c in color 2. Backtracking with monotone pruning.
usage: circulant.py n a b c [max_solutions]"""
import sys
from rlib import kcycles, write_coloring

def has_cycle_through0(n, S, k):
    # circulant graph is vertex transitive: a k-cycle exists iff one passes through vertex 0
    adj = [0] * n
    for v in range(n):
        for d in S:
            adj[v] |= 1 << ((v + d) % n); adj[v] |= 1 << ((v - d) % n)
    # DFS for k-cycles starting at 0 (0 is min vertex automatically)
    cyc = kcycles(adj, n, k, limit=1)
    return bool(cyc)

def main():
    n, a, b, c = map(int, sys.argv[1:5]); L = (a, b, c)
    maxsol = int(sys.argv[5]) if len(sys.argv) > 5 else 5
    D = list(range(1, n // 2 + 1))
    sols = []; nodes = [0]
    cls = [[], [], []]
    def rec(t):
        nodes[0] += 1
        if t == len(D):
            sols.append([list(x) for x in cls]); return len(sols) >= maxsol
        d = D[t]
        for col in range(3):
            if col == 2 and L[1] == L[2] and not cls[2] and not any(cls[1]):
                pass
            cls[col].append(d)
            if not has_cycle_through0(n, cls[col], L[col]):
                if rec(t + 1): return True
            cls[col].pop()
        return False
    rec(0)
    print(f"n={n} L={L} circulant solutions found: {len(sols)} (cap {maxsol}), nodes={nodes[0]}")
    for s in sols[:maxsol]:
        print("  distance classes:", s)
    if sols:
        s = sols[0]; col = [[-1] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    d = min((i - j) % n, (j - i) % n)
                    col[i][j] = [x for x in range(3) if d in s[x]][0]
        write_coloring(f"/workspace/ramsey-c7/colorings/circ_n{n}_C{a}C{b}C{c}.txt", col, f"circulant classes {s}")

main()
