#!/usr/bin/env python3
"""Lazy (counterexample-guided) SAT search for a 3-coloring of K_n with no C_a in color 0, C_b in color 1, C_c in color 2.
Cycles of length <= full_upto are added eagerly; longer ones lazily from models. On UNSAT writes the final
CNF (every clause is a base ALO clause, a genuine forbidden-cycle clause, or a symmetry-breaking clause).
On SAT with no forbidden cycle, writes the coloring."""
import sys, time, argparse, json
from pysat.solvers import Solver
from rlib import EncA, kcycles, color_graphs, lex_sb, tr_sb, write_dimacs, write_coloring

def complete_adj(n):
    return [((1 << n) - 1) ^ (1 << v) for v in range(n)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int); ap.add_argument("a", type=int); ap.add_argument("b", type=int); ap.add_argument("c", type=int)
    ap.add_argument("--sb", default="none", choices=["none", "adj", "all", "tr", "tradj"])
    ap.add_argument("--full-upto", type=int, default=5)
    ap.add_argument("--limit", type=int, default=400, help="max new cycles per color per iteration")
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--amo", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--assume", default=None, help="json list of literals fixed as unit clauses (for cubes)")
    args = ap.parse_args()
    n, L = args.n, (args.a, args.b, args.c)
    tag = f"n{n}_C{L[0]}C{L[1]}C{L[2]}_sb{args.sb}"
    out = args.out or f"/workspace/ramsey-c7/cnf/{tag}"
    enc = EncA(n, amo=args.amo)
    clauses = enc.base()
    if args.sb in ("adj", "all"):
        clauses += lex_sb(enc, args.sb)
    elif args.sb in ("tr", "tradj"):
        clauses += tr_sb(enc, "all" if args.sb == "tr" else "adj")
    full = complete_adj(n)
    ncyc0 = 0
    for c in range(3):
        if L[c] <= args.full_upto:
            for cy in kcycles(full, n, L[c]):
                clauses.append(enc.cycle_clause(c, cy)); ncyc0 += 1
    lazy = [c for c in range(3) if L[c] > args.full_upto]
    t0 = time.time()
    s = Solver(name=args.solver, bootstrap_with=clauses)
    it = 0; added = 0
    while True:
        it += 1
        r = s.solve()
        if not r:
            dt = time.time() - t0
            write_dimacs(out + ".cnf", enc.nv, clauses, [f"R-coloring K{n} C{L} sb={args.sb} UNSAT-candidate", f"edges={enc.m} base_vars={3*enc.m}"])
            print(json.dumps({"tag": tag, "result": "UNSAT", "iters": it, "eager_cycles": ncyc0, "lazy_cycles": added,
                              "clauses": len(clauses), "vars": enc.nv, "secs": round(dt, 2)}))
            return
        col = enc.decode(s.get_model())
        adjs = color_graphs(col, n)
        new = 0
        for c in range(3):
            for cy in kcycles(adjs[c], n, L[c], limit=args.limit):
                cl = enc.cycle_clause(c, cy)
                s.add_clause(cl); clauses.append(cl); new += 1
        added += new
        if it % 50 == 0:
            print(f"  iter {it} lazy={added} t={time.time()-t0:.1f}s", file=sys.stderr, flush=True)
        if new == 0:
            dt = time.time() - t0
            write_coloring(out + "_good.txt", col, f"good coloring K{n} for C{L} found by cegar.py")
            print(json.dumps({"tag": tag, "result": "SAT", "iters": it, "lazy_cycles": added, "secs": round(dt, 2),
                              "coloring": out + "_good.txt"}))
            return

if __name__ == "__main__":
    main()
