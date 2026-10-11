#!/usr/bin/env python3
"""Adversarial cross-check: checker A (rlib DFS) vs checker B logic (networkx simple_cycles) vs brute force
(itertools permutations over k-subsets) on random mutants of the lower-bound colorings and random colorings."""
import random, itertools, sys
import networkx as nx
from rlib import read_coloring, color_graphs, kcycles

def nx_has(n, col, c, k):
    G = nx.Graph(); G.add_nodes_from(range(n))
    G.add_edges_from((i, j) for i in range(n) for j in range(i+1, n) if col[i][j] == c)
    return any(len(cy) == k for cy in nx.simple_cycles(G, length_bound=k))

def brute_has(n, col, c, k):
    for S in itertools.combinations(range(n), k):
        if any(sum(1 for y in S if y != x and col[x][y] == c) < 2 for x in S):
            continue
        f, rest = S[0], S[1:]
        for p in itertools.permutations(rest):
            cyc = (f,) + p
            if all(col[cyc[t]][cyc[(t+1) % k]] == c for t in range(k)):
                return True
    return False

random.seed(12345)
cases = [("lb_C3C7C7_n24.txt", (3,7,7)), ("lb_C5C7C7_n24.txt", (5,7,7)), ("lb_C6C7C7_n20.txt", (6,7,7)), ("lb_C4C7C7_n14.txt", (4,7,7))]
tests = 0; disagree = 0; detected = 0
for fn, L in cases:
    base = read_coloring("/workspace/ramsey-c7/colorings/" + fn); n = len(base)
    for trial in range(int(sys.argv[1]) if len(sys.argv) > 1 else 40):
        col = [r[:] for r in base]
        for _ in range(random.randint(1, 3)):
            i, j = random.sample(range(n), 2); c = random.randrange(3); col[i][j] = col[j][i] = c
        adjs = color_graphs(col, n)
        for c in range(3):
            a = bool(kcycles(adjs[c], n, L[c], limit=1)); b = nx_has(n, col, c, L[c])
            res = [a, b]
            if n <= 14: res.append(brute_has(n, col, c, L[c]))
            tests += 1
            if len(set(res)) > 1:
                disagree += 1; print("DISAGREE", fn, c, res)
            detected += a
# random small colorings with brute force for all lengths 3..7
for trial in range(150):
    n = random.randint(7, 11); col = [[-1]*n for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            col[i][j] = col[j][i] = random.choices([0,1,2], weights=[random.random() for _ in range(3)])[0]
    adjs = color_graphs(col, n)
    for c in range(3):
        for k in range(3, 8):
            res = [bool(kcycles(adjs[c], n, k, limit=1)), nx_has(n, col, c, k), brute_has(n, col, c, k)]
            tests += 1
            if len(set(res)) > 1: disagree += 1; print("DISAGREE random", n, c, k, res)
print(f"tests={tests} disagreements={disagree} mutant-cycles-detected={detected}")
