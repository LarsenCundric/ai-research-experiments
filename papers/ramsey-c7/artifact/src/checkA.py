#!/usr/bin/env python3
"""Checker A: uses rlib DFS cycle enumeration. usage: checkA.py coloring.txt a b c"""
import sys
from rlib import read_coloring, color_graphs, kcycles
col = read_coloring(sys.argv[1]); n = len(col)
L = list(map(int, sys.argv[2:5]))
adjs = color_graphs(col, n)
ok = True
for c in range(3):
    cyc = kcycles(adjs[c], n, L[c], limit=1)
    ne = sum(bin(a).count("1") for a in adjs[c]) // 2
    print(f"color {c}: {ne} edges, C{L[c]} present: {bool(cyc)}" + (f" e.g. {cyc[0]}" if cyc else ""))
    ok &= not cyc
print(f"n={n} RESULT: {'GOOD' if ok else 'BAD'}")
sys.exit(0 if ok else 1)
