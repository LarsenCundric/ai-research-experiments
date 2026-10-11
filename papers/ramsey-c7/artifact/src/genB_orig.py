#!/usr/bin/env python3
"""Encoding B (independent of rlib.py): full CNF for 'K_n has a 3-coloring with no C_a in color 0, no C_b in color 1,
no C_c in color 2'. Two vars per edge: r (color0), g (color1); color2 = neither; clause (-r v -g).
Cycles enumerated via itertools (k-subsets x permutations), a different method from rlib's DFS.
Optional symmetry breaking: lex-leader for adjacent vertex transpositions over this encoding's own variable order.
usage: genB.py n a b c out.cnf [--sb]"""
import sys, itertools

def main():
    n, a, b, c = map(int, sys.argv[1:5]); out = sys.argv[5]; sb = "--sb" in sys.argv
    pairs = list(itertools.combinations(range(n), 2))
    eid = {p: k for k, p in enumerate(pairs)}
    R = lambda u, v: 2 * eid[(min(u, v), max(u, v))] + 1
    G = lambda u, v: 2 * eid[(min(u, v), max(u, v))] + 2
    nv = 2 * len(pairs)
    cls = [[-R(u, v), -G(u, v)] for (u, v) in pairs]
    for color, k in enumerate((a, b, c)):
        for S in itertools.combinations(range(n), k):
            first, rest = S[0], S[1:]
            for perm in itertools.permutations(rest):
                if perm[0] > perm[-1]:
                    continue
                cyc = (first,) + perm
                es = [(cyc[t], cyc[(t + 1) % k]) for t in range(k)]
                if color == 0:
                    cls.append([-R(u, v) for u, v in es])
                elif color == 1:
                    cls.append([-G(u, v) for u, v in es])
                else:
                    cls.append([x for u, v in es for x in (R(u, v), G(u, v))])
    if sb:
        for i in range(n - 1):
            j = i + 1
            sw = lambda w: j if w == i else (i if w == j else w)
            X = []; Y = []
            for (u, v) in pairs:
                for f in (R, G):
                    x = f(u, v); y = f(sw(u), sw(v))
                    if x != y:
                        X.append(x); Y.append(y)
            prev = None
            for t in range(len(X)):
                pre = [] if prev is None else [-prev]
                cls.append(pre + [-X[t], Y[t]])
                if t < len(X) - 1:
                    nv += 1; e = nv
                    cls.append(pre + [-X[t], -Y[t], e]); cls.append(pre + [X[t], Y[t], e])
                    prev = e
    with open(out, "w") as f:
        f.write(f"c encB n={n} cycles=({a},{b},{c}) sb={sb}\n")
        f.write(f"p cnf {nv} {len(cls)}\n")
        for cl in cls:
            f.write(" ".join(map(str, cl)) + " 0\n")
    print(f"wrote {out}: vars={nv} clauses={len(cls)}")

main()
