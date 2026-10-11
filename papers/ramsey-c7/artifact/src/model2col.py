#!/usr/bin/env python3
"""Decode a solver model (v-lines) of an encoding-A CNF into a coloring file. usage: model2col.py log n out.txt"""
import sys
from rlib import EncA, write_coloring
log, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
lits = []
for l in open(log):
    if l.startswith("v "): lits += [int(x) for x in l.split()[1:]]
enc = EncA(n); col = enc.decode(lits)
assert all(col[i][j] >= 0 for i in range(n) for j in range(n) if i != j), "uncolored edge"
write_coloring(out, col, f"decoded from {log}")
print("wrote", out)
