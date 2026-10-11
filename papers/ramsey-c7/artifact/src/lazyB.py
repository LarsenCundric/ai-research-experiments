#!/usr/bin/env python3
"""Lazy (CEGAR) solver for encoding B, independent of rlib.py and prop/cycprop.cpp.
  lazyB.py BASE.cnf n a b c CUBES idx OUTPREFIX [--limit L]      (idx = -1: no cube)
Solves BASE (+ cube literals as assumptions) with pysat's CaDiCaL; on each model, decodes the colouring and enumerates
forbidden monochromatic cycles with its own DFS, adds their clauses, repeats. Writes OUTPREFIX.ext (all added clauses),
on SAT OUTPREFIX.col (colouring), and prints one JSON line with the result."""
import sys, json, time, itertools, os, signal
from pysat.solvers import Solver
from pysat.formula import CNF

def cycles(adj, n, k, limit):
    """simple k-cycles, each once: min vertex s first, second vertex < last vertex"""
    out = []
    for s in range(n):
        path = [s]; onp = {s}
        def dfs(u):
            if len(out) >= limit: return
            if len(path) == k:
                if s in adj[u] and path[1] < path[-1]: out.append(list(path))
                return
            for w in adj[u]:
                if w > s and w not in onp:
                    path.append(w); onp.add(w); dfs(w); path.pop(); onp.discard(w)
                    if len(out) >= limit: return
        dfs(s)
        if len(out) >= limit: break
    return out

def main():
    base, n, a, b, c, cubes, idx, pre = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6], int(sys.argv[7]), sys.argv[8]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 200
    maxsecs = float(sys.argv[sys.argv.index("--maxsecs") + 1]) if "--maxsecs" in sys.argv else 1e18
    L = (a, b, c)
    pairs = list(itertools.combinations(range(n), 2))
    R = lambda e: 2 * e + 1; G = lambda e: 2 * e + 2
    eid = {p: k for k, p in enumerate(pairs)}
    cube = []
    if idx >= 0:
        cube = [[int(x) for x in l.split()[1:-1]] for l in open(cubes) if l.startswith("a ")][idx]
    t0 = time.time(); it = 0; nadd = 0
    wpid = None
    if maxsecs < 1e17:   # hard time limit: pysat's CaDiCaL holds the GIL and cannot be interrupted, so a forked watchdog reports
        parent = os.getpid(); wpid = os.fork()         # TIMEOUT on our stdout and kills us (clauses are flushed every iteration)
        if wpid == 0:
            time.sleep(maxsecs + 30)
            try:
                os.kill(parent, 0)
                print(json.dumps({"result": "TIMEOUT", "secs": round(time.time() - t0, 2), "watchdog": True}), flush=True)
                os.kill(parent, signal.SIGKILL)
            except OSError: pass
            os._exit(0)
    S = Solver(name="cadical195", bootstrap_with=CNF(from_file=base).clauses)
    fe = open(pre + ".ext", "w")
    while True:
        it += 1
        if time.time() - t0 > maxsecs:
            res = "TIMEOUT"; break
        if not S.solve(assumptions=cube):
            res = "UNSAT"; break
        mod = S.get_model(); val = lambda v: mod[v - 1] > 0
        colour = {p: (0 if val(R(e)) else (1 if val(G(e)) else 2)) for e, p in enumerate(pairs)}
        new = 0
        for col in range(3):
            adj = [set() for _ in range(n)]
            for (u, v), cc in colour.items():
                if cc == col: adj[u].add(v); adj[v].add(u)
            for cy in cycles(adj, n, L[col], limit):
                es = [eid[tuple(sorted((cy[t], cy[(t + 1) % len(cy)])))] for t in range(len(cy))]
                cl = [-R(e) for e in es] if col == 0 else ([-G(e) for e in es] if col == 1 else [x for e in es for x in (R(e), G(e))])
                S.add_clause(cl); fe.write(" ".join(map(str, cl)) + " 0\n"); new += 1
        nadd += new
        fe.flush()
        if new == 0:
            res = "SAT"
            with open(pre + ".col", "w") as f:
                f.write(f"# lazyB model n={n} cycles={L}\n")
                for i in range(n):
                    f.write("".join("x" if i == j else str(colour[(min(i, j), max(i, j))]) for j in range(n)) + "\n")
            break
    fe.close()
    if wpid:
        try: os.kill(wpid, signal.SIGKILL); os.waitpid(wpid, 0)
        except OSError: pass
    print(json.dumps({"result": res, "secs": round(time.time() - t0, 2), "iterations": it, "ext_clauses": nadd}))

if __name__ == "__main__":
    main()
