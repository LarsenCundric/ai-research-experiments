#!/usr/bin/env python3
"""Independent consistency audit of a cube-and-conquer workdir (cnc_lazy.py, cnc_lazyB.py or cnc_tree.py; cube trees supported).
Checks: input hashes unchanged; top-level coverage verified (and re-proved here with kissat DRAT + drat-trim); for every verified
split: file hash, children literals contain the parent literals, coverage of the split re-proved here with kissat + drat-trim from
the stored files; every leaf certified record: literals equal the tree literals, offline UNSAT, proof verified (leg A cake_lpr,
leg B drat-trim), added clauses all genuine cycles; base legitimacy check PASS; every top-level cube certified directly or through
splits whose children are all certified (recursively)."""
import sys, json, hashlib, subprocess, os, tempfile
W = sys.argv[1]; R = "/workspace/ramsey-c7"
KISSAT = R + "/tools/kissat/build/kissat"; DT = R + "/tools/drat-trim/drat-trim"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
m = json.load(open(W + "/meta.json")); legB = m.get("leg") == "B"
ok = True
def chk(c, msg):
    global ok
    print(("OK   " if c else "FAIL ") + msg); ok &= bool(c)
tmp = tempfile.mkdtemp()
def unsat_drat(nv, clauses):
    f = tmp + "/t.cnf"
    with open(f, "w") as o:
        o.write(f"p cnf {nv} {len(clauses)}\n")
        for c in clauses: o.write(" ".join(map(str, c)) + " 0\n")
    k = subprocess.run([KISSAT, "-q", "--no-binary", f, tmp + "/t.drat"], capture_output=True, text=True)
    t = subprocess.run([DT, f, tmp + "/t.drat"], capture_output=True, text=True)
    return k.returncode == 20 and "s VERIFIED" in t.stdout and "NOT VERIFIED" not in t.stdout
chk(sha(m["base"]) == m["base_sha256"], "base sha256 unchanged")
chk(sha(W + "/cubes") == m["cubes_sha256"], "cubes sha256 unchanged")
P = "CNF-B CHECK PASS" if legB else "CNF CHECK PASS"
chk(open(W + "/check_base.log").read().strip().endswith(P), "base formula legitimacy check PASS")
base_cl = []; nv = 0
for l in open(m["base"]):
    if l.startswith("p cnf"): nv = int(l.split()[2])
    elif not l.startswith("c") and l.strip(): base_cl.append([int(x) for x in l.split()[:-1]])
lits = {str(i): [int(x) for x in l.split()[1:-1]] for i, l in enumerate(x for x in open(W + "/cubes") if x.startswith("a "))}
top = list(lits)
cov = json.load(open(W + "/coverage.json")); chk(cov.get("cake_lpr") == "s VERIFIED UNSAT", f"top coverage cake_lpr ({cov.get('kind')})")
if legB: chk(cov.get("drat_trim") == "s VERIFIED", "top coverage drat-trim")
chk(unsat_drat(nv, [[-x for x in lits[i]] for i in top]), "top coverage re-proved here (kissat DRAT + drat-trim, negated cubes alone)")
children = {}; nsplit_bad = 0
if os.path.exists(W + "/splits.jsonl"):
    recs = [json.loads(l) for l in open(W + "/splits.jsonl")]
    recs = [d for d in recs if d.get("ok")]
    pending = list(recs)
    while pending:                                        # parents must be known before children (nested splits)
        nxt = []
        for d in pending:
            if d["parent"] not in lits: nxt.append(d); continue
            Pl = lits[d["parent"]]; fn = W + "/" + d["file"]
            good = sha(fn) == d["file_sha256"]
            kids = [[int(x) for x in z.split()[1:-1]] for z in open(fn) if z.startswith("a ")]
            good &= len(kids) == len(d["children"]) and all(set(Pl) <= set(k) for k in kids)
            covr = d["coverage"]
            good &= (covr.get("drat_trim") == "s VERIFIED") if legB else (covr.get("cake_lpr") == "s VERIFIED UNSAT")
            D = [[x for x in k if x not in Pl] for k in kids]
            cl = ([c for c in base_cl] if "base" in covr.get("kind", "").split(" + ")[0] else []) + [[x] for x in Pl] + [[-x for x in dd] for dd in D]
            good &= all(len(dd) > 0 for dd in D) and unsat_drat(nv, cl)
            if good:
                children[d["parent"]] = d["children"]
                for cid, k in zip(d["children"], kids): lits[cid] = k
            else: nsplit_bad += 1
        if len(nxt) == len(pending): nsplit_bad += len(nxt); break
        pending = nxt
chk(nsplit_bad == 0, f"all {len(children)} verified splits re-checked (files, literal containment, coverage re-proved)")
rec = {}
for l in open(W + "/status.jsonl"):
    d = json.loads(l); i = d.get("id", str(d.get("cube")))
    if d.get("certified"): rec[i] = d
bad = []
for i, d in rec.items():
    v = (d.get("drat_trim") == "s VERIFIED") if legB else (d.get("cake_lpr") == "s VERIFIED UNSAT")
    if not (i in lits and d["lits"] == lits[i] and v and d.get("offline_result") == "UNSAT" and d.get("ext_check") == P): bad.append(i)
chk(not bad, f"all {len(rec)} certified leaf records consistent (literals, offline UNSAT, proof verified, cycle clauses legit) {bad[:5]}")
def cert(i): return (i in rec and i not in bad) or (i in children and all(cert(c) for c in children[i]))
nc = sum(cert(i) for i in top)
chk(nc == len(top), f"top-level cubes certified (directly or via splits): {nc}/{len(top)}")
print("AUDIT", "PASS" if ok else "FAIL")
