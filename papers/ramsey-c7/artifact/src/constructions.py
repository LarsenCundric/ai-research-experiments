#!/usr/bin/env python3
"""Explicit lower-bound colorings for R(Cm, C7, C7). Color 0 = the C_m color, colors 1,2 = the C7 colors."""
from rlib import write_coloring
OUT = "/workspace/ramsey-c7/colorings"

def four_part(s, inside, between_halves, within_halves):
    """4 parts P0..P3 of size s. edges inside parts -> 'inside'; P0-P1 and P2-P3 -> within_halves;
    (P0 u P1)-(P2 u P3) -> between_halves."""
    n = 4 * s
    part = [v // s for v in range(n)]
    col = [[-1] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j: continue
            pi, pj = part[i], part[j]
            if pi == pj: c = inside
            elif pi // 2 == pj // 2: c = within_halves
            else: c = between_halves
            col[i][j] = c
    return col

def m4_14():
    # A = 0..5, B = 6..11, s1 = 12, s2 = 13
    n = 14
    A = range(0, 6); B = range(6, 12); s1, s2 = 12, 13
    col = [[-1] * n for _ in range(n)]
    def setc(i, j, c): col[i][j] = col[j][i] = c
    for X in (A, B):
        for i in X:
            for j in X:
                if i < j: setc(i, j, 1)
    for i in A:
        for j in B: setc(i, j, 2)
    for a in A: setc(s1, a, 0); setc(s2, a, 2)
    for b in B: setc(s2, b, 0); setc(s1, b, 2)
    setc(s1, s2, 2)
    return col

if __name__ == "__main__":
    # odd m (3,5): 4 parts of size 6; C_m color (0) is bipartite between halves; C7 colors: 1 inside parts (4 x K6), 2 within halves (2 x K_{6,6})
    for m in (3, 5):
        col = four_part(6, inside=1, between_halves=0, within_halves=2)
        write_coloring(f"{OUT}/lb_C{m}C7C7_n24.txt", col,
            f"Lower bound R(C{m},C7,C7) >= 25: 3-coloring of K24, color0 has no C{m}, colors 1,2 have no C7.\n"
            "Construction: 4 parts of size 6; inside parts color 1 (4 disjoint K6); P0-P1, P2-P3 color 2 (bipartite);\n"
            "(P0+P1)-(P2+P3) color 0 (complete bipartite K12,12, no odd cycle).")
    col = four_part(5, inside=0, between_halves=1, within_halves=2)
    write_coloring(f"{OUT}/lb_C6C7C7_n20.txt", col,
        "Lower bound R(C6,C7,C7) >= 21: K20, 4 parts of size 5; color 0 inside parts (4 x K5, no C6);\n"
        "colors 1,2 bipartite (no odd cycles).")
    col = four_part(3, inside=0, between_halves=1, within_halves=2)
    write_coloring(f"{OUT}/lb_C4C7C7_n12_fourpart.txt", col, "R(C4,C7,C7) >= 13 (4 parts of size 3; superseded by n14)")
    write_coloring(f"{OUT}/lb_C4C7C7_n14.txt", m4_14(),
        "Lower bound R(C4,C7,C7) >= 15: K14. A=0..5, B=6..11 color1 inside (2 x K6), A-B color 2;\n"
        "s1=12: s1-A color 0, s1-B color 2; s2=13: s2-B color 0, s2-A color 2; s1-s2 color 2.\n"
        "color0 = two disjoint stars K1,6 (no C4); color2 bipartite (A+s1 | B+s2); color1 = 2 x K6.")
