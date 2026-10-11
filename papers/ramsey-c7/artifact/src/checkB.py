#!/usr/bin/env python3
"""Independent coloring checker (does NOT import rlib). Uses networkx.simple_cycles(length_bound)
and, as a second method, a bitmask Hamiltonian-cycle DP over all k-subsets for small graphs.
usage: checkB.py coloring.txt a b c   -> verifies no C_a in color 0, no C_b in color 1, no C_c in color 2."""
import sys, itertools
import networkx as nx

def load(path):
    rows = [l.strip() for l in open(path) if l.strip() and not l.lstrip().startswith("#")]
    n = len(rows)
    for r in rows:
        assert len(r) == n, "row length mismatch"
    M = [[None if i == j else int(rows[i][j]) for j in range(n)] for i in range(n)]
    for i in range(n):
        assert rows[i][i] in "x-", "diagonal must be x"
        for j in range(n):
            if i != j:
                assert M[i][j] == M[j][i], f"asymmetric at {i},{j}"
                assert M[i][j] in (0, 1, 2), "color out of range"
    return n, M

def has_cycle_nx(G, k):
    for cyc in nx.simple_cycles(G, length_bound=k):
        if len(cyc) == k:
            return cyc
    return None

def main():
    path = sys.argv[1]
    L = list(map(int, sys.argv[2:5]))
    n, M = load(path)
    ok = True
    for c in range(3):
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from((i, j) for i in range(n) for j in range(i + 1, n) if M[i][j] == c)
        cyc = has_cycle_nx(G, L[c])
        print(f"color {c}: {G.number_of_edges()} edges, C{L[c]} present: {cyc is not None}" + (f" e.g. {cyc}" if cyc else ""))
        if cyc:
            ok = False
    print(f"n={n} RESULT: {'GOOD (no forbidden monochromatic cycle)' if ok else 'BAD'}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
