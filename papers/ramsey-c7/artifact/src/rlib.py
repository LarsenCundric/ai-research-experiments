"""Core library: edge indexing, cycle enumeration (DFS, canonical), CNF encoding A.
Colors are 0,1,2 ; target cycle lengths L=(a,b,c): no C_a in color 0, no C_b in color 1, no C_c in color 2."""
import itertools

def edge_index(n):
    idx = {}
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            idx[(i, j)] = k
            idx[(j, i)] = k
            k += 1
    return idx

def kcycles(adj, n, k, limit=None):
    """Enumerate k-cycles (k>=3) of graph with adjacency bitmasks adj[v]. Each cycle reported once as
    vertex tuple (v0, v1, ..., v_{k-1}) with v0 = min and v1 < v_{k-1}."""
    out = []
    path = []
    for v0 in range(n):
        higher = ~((1 << (v0 + 1)) - 1)
        path = [v0]
        stack = [(v0, adj[v0] & higher)]
        used = 1 << v0
        while stack:
            v, cand = stack[-1]
            if cand == 0:
                stack.pop(); path.pop(); used &= ~(1 << v)
                continue
            w = (cand & -cand).bit_length() - 1
            stack[-1] = (v, cand & (cand - 1))
            if len(path) == k - 1:
                # w is last vertex; must close to v0 and satisfy orientation
                if (adj[w] >> v0) & 1 and path[1] < w if k > 2 else True:
                    out.append(tuple(path) + (w,))
                    if limit and len(out) >= limit:
                        return out
                continue
            path.append(w); used |= 1 << w
            stack.append((w, adj[w] & higher & ~used))
    return out

def has_kcycle(adj, n, k):
    return len(kcycles(adj, n, k, limit=1)) > 0

def color_graphs(col, n):
    """col: dict (i,j)->color or n x n matrix. returns list of 3 adjacency bitmask lists"""
    adjs = [[0] * n for _ in range(3)]
    for i in range(n):
        for j in range(i + 1, n):
            c = col[i][j]
            adjs[c][i] |= 1 << j
            adjs[c][j] |= 1 << i
    return adjs

def bad_cycles(col, n, L, limit=None):
    adjs = color_graphs(col, n)
    res = []
    for c in range(3):
        cyc = kcycles(adjs[c], n, L[c], limit)
        res.extend((c, cy) for cy in cyc)
    return res

class EncA:
    """One-hot encoding: var(e,c) = 3*e + c + 1. Clauses: ALO per edge (+ optional AMO),
    forbidden cycle clause: OR_{e in cycle} -var(e,c)."""
    def __init__(self, n, amo=False):
        self.n = n
        self.E = edge_index(n)
        self.m = n * (n - 1) // 2
        self.nv = 3 * self.m
        self.amo = amo
    def var(self, i, j, c):
        return 3 * self.E[(i, j)] + c + 1
    def base(self):
        cl = []
        for i in range(self.n):
            for j in range(i + 1, self.n):
                cl.append([self.var(i, j, c) for c in range(3)])
                if self.amo:
                    for a in range(3):
                        for b in range(a + 1, 3):
                            cl.append([-self.var(i, j, a), -self.var(i, j, b)])
        return cl
    def cycle_clause(self, c, cyc):
        k = len(cyc)
        return [-self.var(cyc[t], cyc[(t + 1) % k], c) for t in range(k)]
    def new_var(self):
        self.nv += 1
        return self.nv
    def decode(self, model):
        s = set(l for l in model if l > 0)
        col = [[-1] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(i + 1, self.n):
                for c in range(3):
                    if self.var(i, j, c) in s:
                        col[i][j] = col[j][i] = c
                        break
        return col

def lex_sb(enc, pairs="all"):
    """Codish et al. sb_l: for i<j, row_i (cols != i,j) <=lex row_j (cols != i,j), where each entry is the
    bit-vector (x_c0, x_c1, x_c2). Encoded with auxiliary 'equal-prefix' vars. Returns clauses."""
    n = enc.n
    cls = []
    if pairs == "all":
        P = [(i, j) for i in range(n) for j in range(i + 1, n)]
    else:
        P = [(i, i + 1) for i in range(n - 1)]
    for (i, j) in P:
        a = []; b = []
        for k in range(n):
            if k in (i, j):
                continue
            for c in range(3):
                a.append(enc.var(i, k, c)); b.append(enc.var(j, k, c))
        cls.extend(lex_leq(enc, a, b))
    return cls

def lex_leq(enc, a, b):
    """clauses for a <=lex b (bit vectors, MSB first). e_t: prefix a[0..t-1]==b[0..t-1]."""
    cls = []
    prev = None  # None means true
    for t in range(len(a)):
        # if prefix equal then a[t] <= b[t]  : prev -> (-a[t] or b[t])
        base = [] if prev is None else [-prev]
        cls.append(base + [-a[t], b[t]])
        if t == len(a) - 1:
            break
        e = enc.new_var()
        # e -> prev ; e -> (a[t] == b[t]) ; we only need e implied by (prev & a==b)
        # (prev & a[t]==b[t]) -> e
        cls.append(base + [-a[t], -b[t], e])
        cls.append(base + [a[t], b[t], e])
        prev = e
    return cls

def write_dimacs(path, nv, clauses, comments=()):
    with open(path, "w") as f:
        for c in comments:
            f.write("c " + c + "\n")
        f.write(f"p cnf {nv} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")

def read_coloring(path):
    rows = [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]
    n = len(rows)
    col = [[-1] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                col[i][j] = int(rows[i][j])
    for i in range(n):
        for j in range(n):
            assert i == j or col[i][j] == col[j][i], "asymmetric"
    return col

def write_coloring(path, col, header=""):
    n = len(col)
    with open(path, "w") as f:
        if header:
            for h in header.split("\n"):
                f.write("# " + h + "\n")
        for i in range(n):
            f.write("".join("x" if i == j else str(col[i][j]) for j in range(n)) + "\n")

def edge_order(n):
    return [(i, j) for i in range(n) for j in range(i + 1, n)]

def tr_sb(enc, pairs="all"):
    """Provably sound lex-leader constraints (Crawford et al. 1996) for vertex transpositions.
    Variable order: edges in row-major upper-triangle order, within an edge colors 0,1,2.
    For transposition s=(i j), add  X <=lex s(X)  where s(X)[t] = value of variable mapped to position t.
    Every vertex permutation preserves the set of good colorings, so the lex-least member of any orbit
    satisfies all such constraints simultaneously."""
    n = enc.n
    order = edge_order(n)
    P = [(i, j) for i in range(n) for j in range(i + 1, n)] if pairs == "all" else [(i, i + 1) for i in range(n - 1)]
    cls = []
    for (i, j) in P:
        def s(v):
            return j if v == i else (i if v == j else v)
        a = []; b = []
        for (u, v) in order:
            su, sv = s(u), s(v)
            for c in range(3):
                x = enc.var(u, v, c); y = enc.var(su, sv, c)
                a.append(x); b.append(y)
        # drop positions where both sides are the same variable (always equal)
        aa = []; bb = []
        seen_pairs = set()
        for x, y in zip(a, b):
            if x == y:
                continue
            aa.append(x); bb.append(y)
        cls.extend(lex_leq(enc, aa, bb))
    return cls
