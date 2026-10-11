#!/usr/bin/env python3
"""Certified, resumable cube-and-conquer with ADAPTIVE RE-SPLITTING, for both legs.
  cnc_tree.py {A|B} BASE.cnf n a b c CUBES WORKDIR [--jobs J] [--solve-cap S] [--offline-cap S] [--check-cap S] [--split-depth D]
Leg A: base = genA lazy base; lazy solver prop/cycprop (CaDiCaL IPASIR-UP); clause checker check_cnf.py; per-cube proof CaDiCaL LRAT
       checked by cake_lpr.
Leg B: base = genB lazy base; lazy solver src/lazyB.py (PySAT CEGAR); clause checker check_cnfB.py; per-cube proof Kissat DRAT
       checked by drat-trim.
Compatible with workdirs of cnc_lazy.py / cnc_lazyB.py (old records: integer "cube"; new records: string "id").
Cube tree: top-level ids "0".."s-1"; a split of node P (literals P) into children "P.0".."P.(k-1)" with literals P + D_j is recorded
in splits.jsonl together with a checked coverage certificate: units(P) & AND_j not(D_j) is UNSAT (fallback: BASE & units(P) &
AND_j not(D_j)). A node is certified iff it has a certified UNSAT record, or a verified split all of whose children are certified.
A node is split when the lazy solve exceeds --solve-cap, or the offline proof run exceeds --offline-cap, or the proof check exceeds
--check-cap. Splitting runs march_cu on BASE + (up to 1e5 cycle clauses the lazy solver had added) + units(P); the split is untrusted,
only its coverage certificate counts. Re-running the same command resumes: certified nodes and verified splits are kept."""
import sys, os, json, time, hashlib, subprocess, argparse, threading, shutil, fcntl
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
R = "/workspace/ramsey-c7"; T = R + "/tools"
CADICAL = T + "/cadical/build/cadical"; CAKE = T + "/cake_lpr/cake_lpr"; CYC = R + "/prop/cycprop"
KISSAT = T + "/kissat/build/kissat"; DT = T + "/drat-trim/drat-trim"; MARCH = T + "/CnC/march_cu/march_cu"
BIGLOCK = R + "/.bigcheck.lock"; BIG = 300 * 10**6
lock = threading.Lock()

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def run(cmd, timeout=None):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, round(time.time() - t0, 1)
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "", round(time.time() - t0, 1)

class BigCheck:
    """inter-process lock so that at most one checker with a > 300 MB proof runs at a time (box-wide, both legs)"""
    def __init__(self, proof): self.big = os.path.exists(proof) and os.path.getsize(proof) > BIG
    def __enter__(self):
        if self.big: self.f = open(BIGLOCK, "w"); fcntl.flock(self.f, fcntl.LOCK_EX)
    def __exit__(self, *a):
        if self.big: fcntl.flock(self.f, fcntl.LOCK_UN); self.f.close()

def prove(leg, cnf, proof, offline_cap, check_cap):
    """offline proof + check of an UNSAT claim. Leg A: CaDiCaL LRAT + cake_lpr. Leg B: Kissat DRAT + drat-trim."""
    out = {}
    if leg == "A":
        rc, so, t = run([CADICAL, "-q", "--lrat", cnf, proof], offline_cap)
    else:
        rc, so, t = run([KISSAT, "-q", cnf, proof], offline_cap)
    out["offline_result"] = {10: "SAT", 20: "UNSAT", "TIMEOUT": "TIMEOUT"}.get(rc, f"exit{rc}"); out["offline_secs"] = t
    if rc != 20: return out
    out["proof_bytes"] = os.path.getsize(proof); out["proof_sha256"] = sha(proof)
    with BigCheck(proof):
        if leg == "A":
            rc, so, t = run([CAKE, cnf, proof], check_cap)
            out["cake_lpr"] = "s VERIFIED UNSAT" if (rc != "TIMEOUT" and "s VERIFIED UNSAT" in so) else ("TIMEOUT" if rc == "TIMEOUT" else "FAIL: " + so[-200:])
        else:
            rc, so, t = run([DT, cnf, proof, "-t", str(check_cap + 60)], check_cap)
            ok = rc != "TIMEOUT" and "s VERIFIED" in so and "NOT VERIFIED" not in so
            out["drat_trim"] = "s VERIFIED" if ok else ("TIMEOUT" if (rc == "TIMEOUT" or "TIMEOUT" in so.upper()) else "FAIL: " + so[-200:])
    out["check_secs"] = t
    return out

def verified(leg, r):
    return r.get("cake_lpr") == "s VERIFIED UNSAT" if leg == "A" else r.get("drat_trim") == "s VERIFIED"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("leg", choices=["A", "B"]); ap.add_argument("base")
    ap.add_argument("n", type=int); ap.add_argument("a", type=int); ap.add_argument("b", type=int); ap.add_argument("c", type=int)
    ap.add_argument("cubes"); ap.add_argument("W")
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--solve-cap", type=int, default=1200)
    ap.add_argument("--offline-cap", type=int, default=2400); ap.add_argument("--check-cap", type=int, default=2400)
    ap.add_argument("--split-depth", type=int, default=6); ap.add_argument("--sb", default="tradj")
    A = ap.parse_args(); leg = A.leg
    n, L = A.n, (A.a, A.b, A.c); Ls = list(map(str, L))
    W = os.path.abspath(A.W); os.makedirs(W + "/tmp", exist_ok=True); os.makedirs(W + "/splits", exist_ok=True)
    base = os.path.abspath(A.base)
    def log(msg):
        line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
        print(line, flush=True)
        with lock, open(W + "/run.log", "a") as f: f.write(line + "\n")
    meta = W + "/meta.json"
    if not os.path.exists(meta):
        if os.path.abspath(A.cubes) != W + "/cubes": shutil.copy(A.cubes, W + "/cubes")
        json.dump({"leg": leg, "base": base, "base_sha256": sha(base), "cubes_sha256": sha(W + "/cubes"), "n": n, "L": L,
                   "started": time.ctime()}, open(meta, "w"), indent=1)
    m = json.load(open(meta)); m.setdefault("leg", leg)
    assert m["leg"] == leg, "workdir belongs to the other leg"
    assert m["base_sha256"] == sha(base) and m["cubes_sha256"] == sha(W + "/cubes"), "inputs changed since workdir creation"
    json.dump(m, open(meta, "w"), indent=1)
    checker = [R + "/src/check_cnf.py"] if leg == "A" else [R + "/src/check_cnfB.py"]
    PASS = "CNF CHECK PASS" if leg == "A" else "CNF-B CHECK PASS"
    if not os.path.exists(W + "/check_base.log"):
        rc, so, _ = run(["python3", *checker, base, str(n), *Ls, A.sb if leg == "A" else "base"])
        open(W + "/check_base.log", "w").write(so)
        if rc != 0: sys.exit("base failed legitimacy check")
    nv = ncl = None; body = []
    for l in open(base):
        if l.startswith("p cnf"): _, _, x, y = l.split(); nv, ncl = int(x), int(y)
        elif not l.startswith("c"): body.append(l)
    body = "".join(body)
    lits = {str(i): [int(x) for x in l.split()[1:-1]] for i, l in enumerate(x for x in open(W + "/cubes") if x.startswith("a "))}
    top = [str(i) for i in range(len(lits))]
    if not os.path.exists(W + "/coverage.json"):
        tc = W + "/tmp/coverage.cnf"
        with open(tc, "w") as f:
            f.write(f"p cnf {nv} {len(top)}\n")
            for i in top: f.write(" ".join(str(-x) for x in lits[i]) + " 0\n")
        r = prove(leg, tc, W + "/tmp/coverage.proof", 3600, 3600); r["kind"] = "negated cubes alone"
        if leg == "A": r["cake_lpr"] = r.get("cake_lpr")
        else:
            rc1, _, _ = run([CADICAL, "-q", "--lrat", tc, W + "/tmp/coverage.lrat"]); rc2, so2, _ = run([CAKE, tc, W + "/tmp/coverage.lrat"])
            r["cake_lpr"] = "s VERIFIED UNSAT" if rc1 == 20 and "s VERIFIED UNSAT" in so2 else "FAIL"
        json.dump(r, open(W + "/coverage.json", "w"))
        for x in (tc, W + "/tmp/coverage.proof", W + "/tmp/coverage.lrat"):
            if os.path.exists(x): os.remove(x)
    covr = json.load(open(W + "/coverage.json"))
    if covr.get("cake_lpr") != "s VERIFIED UNSAT": sys.exit("top-level coverage not certified")
    # ---- load state
    status_f = W + "/status.jsonl"; splits_f = W + "/splits.jsonl"
    cert = set(); last = {}; sat = []
    if os.path.exists(status_f):
        for l in open(status_f):
            d = json.loads(l); i = d.get("id", str(d.get("cube")))
            last[i] = d
            if d.get("certified"): cert.add(i)
            if d.get("solve_result") == "SAT": sat.append(i)
    children = {}
    if os.path.exists(splits_f):
        for l in open(splits_f):
            d = json.loads(l)
            if d.get("ok"):
                children[d["parent"]] = d["children"]
                for cid, cl in zip(d["children"], [[int(x) for x in z.split()[1:-1]] for z in open(W + "/" + d["file"]) if z.startswith("a ")]):
                    lits[cid] = cl
    if sat: sys.exit(f"SAT records present for {sat}: inspect before resuming")
    todo = deque()
    def expand(i):
        if i in cert: return
        if i in children:
            for c in children[i]: expand(c)
        else: todo.append(i)
    for i in top: expand(i)
    log(f"start leg {leg} n={n} L={L} jobs={A.jobs} caps solve/offline/check={A.solve_cap}/{A.offline_cap}/{A.check_cap} "
        f"certified={len(cert)} splits={len(children)} leaves_to_do={len(todo)}")
    stop = threading.Event()

    def split(i, warm):
        P = lits[i]; pre = f"{W}/tmp/s{i}"
        wl = []
        if warm and os.path.exists(warm):
            with open(warm) as f:
                for l in f:
                    if l.endswith(" 0\n"): wl.append(l)
                    if len(wl) >= 100000: break
        with open(pre + ".cnf", "w") as f:
            f.write(f"p cnf {nv} {ncl + len(wl) + len(P)}\n"); f.write(body); f.writelines(wl)
            for x in P: f.write(f"{x} 0\n")
        rc, so, t = run([MARCH, pre + ".cnf", "-o", pre + ".icubes", "-d", str(A.split_depth)], 1800)
        D = [[int(x) for x in l.split()[1:-1]] for l in open(pre + ".icubes")] if os.path.exists(pre + ".icubes") else []
        D = [d for d in D if d]
        rec = {"parent": i, "march_secs": t, "warm_clauses": len(wl), "ok": False}
        if len(D) < 2:
            rec["error"] = f"march gave {len(D)} cubes"
        else:
            def cov(with_base):
                f2 = pre + ".cov.cnf"
                with open(f2, "w") as f:
                    f.write(f"p cnf {nv} {(ncl if with_base else 0) + len(P) + len(D)}\n")
                    if with_base: f.write(body)
                    for x in P: f.write(f"{x} 0\n")
                    for d in D: f.write(" ".join(str(-x) for x in d) + " 0\n")
                r = prove(leg, f2, pre + ".cov.proof", 1800, 1800)
                if leg == "B" and r.get("offline_result") == "UNSAT":   # leg B: also CaDiCaL LRAT + cake_lpr, as at top level
                    rc1, _, _ = run([CADICAL, "-q", "--lrat", f2, pre + ".cov.lrat"], 1800)
                    rc2, so2, _ = run([CAKE, f2, pre + ".cov.lrat"], 1800)
                    r["cake_lpr"] = "s VERIFIED UNSAT" if rc1 == 20 and "s VERIFIED UNSAT" in so2 else "FAIL"
                r["kind"] = "base + parent units + negated subcubes" if with_base else "parent units + negated subcubes"
                return r
            r = cov(False)
            if r.get("offline_result") == "SAT": r = cov(True)
            rec["coverage"] = r
            ok = verified(leg, r) and (leg == "A" or r.get("cake_lpr") == "s VERIFIED UNSAT")
            if ok:
                kids = [f"{i}.{k}" for k in range(len(D))]
                fn = f"splits/{i}.cubes"
                with open(W + "/" + fn, "w") as f:
                    for d in D:
                        full = P + [x for x in d if x not in P]
                        f.write("a " + " ".join(map(str, full)) + " 0\n")
                rec.update({"ok": True, "children": kids, "file": fn, "file_sha256": sha(W + "/" + fn)})
        for x in (".cnf", ".icubes", ".cov.cnf", ".cov.proof", ".cov.lrat"):
            if os.path.exists(pre + x): os.remove(pre + x)
        with lock, open(splits_f, "a") as f: f.write(json.dumps(rec) + "\n")
        if rec["ok"]:
            with lock:
                children[i] = rec["children"]
                for cid, l in zip(rec["children"], [z for z in open(W + "/" + rec["file"]) if z.startswith("a ")]):
                    lits[cid] = [int(x) for x in l.split()[1:-1]]
        return rec

    nocap = set()
    def work(i):
        if stop.is_set(): return ("skip", i, None)
        cap = 10**7 if i in nocap else A.solve_cap; ocap = 10**7 if i in nocap else A.offline_cap; ccap = 10**7 if i in nocap else A.check_cap
        pre = f"{W}/tmp/c{i}"
        with open(pre + ".cube", "w") as f: f.write("a " + " ".join(map(str, lits[i])) + " 0\n")
        r = {"id": i, "depth": i.count("."), "lits": lits[i], "certified": False}
        if leg == "A":
            rc, so, t = run([CYC, base, str(n), *Ls, "6", "1", pre, "0", pre + ".cube", "0", str(cap)], cap + 300)
        else:
            rc, so, t = run(["python3", R + "/src/lazyB.py", base, str(n), *Ls, pre + ".cube", "0", pre, "--maxsecs", str(cap)], cap + 600)
        js = [l for l in so.splitlines() if l.startswith("{")]
        res = json.loads(js[0])["result"] if js else ("TIMEOUT" if rc in ("TIMEOUT", 3) else f"crash{rc}")
        if res == "UNKNOWN": res = "TIMEOUT"
        r["solve_result"] = res; r["solve_secs"] = t
        over = res == "TIMEOUT"
        if res == "SAT":
            stop.set(); col = f"{W}/model_{i}.col"
            if leg == "A": run(["python3", R + "/src/model2col.py", pre + ".model", str(n), col])
            else: shutil.copy(pre + ".col", col)
            for k, chk in (("checkA", "checkA.py"), ("checkB", "checkB.py")):
                _, so2, _ = run(["python3", f"{R}/src/{chk}", col, *Ls]); r[k] = so2.strip().splitlines()[-1] if so2.strip() else "?"
        elif res == "UNSAT":
            ext = pre + ".ext"; r["ext_clauses"] = sum(1 for _ in open(ext))
            rc, so2, _ = run(["python3", *checker, ext, str(n), *Ls, "cyclesonly"])
            r["ext_check"] = so2.strip().splitlines()[-1] if so2.strip() else "?"
            if rc == 0:
                fi = pre + ".Fi.cnf"
                with open(fi, "w") as f:
                    f.write(f"p cnf {nv} {ncl + r['ext_clauses'] + len(lits[i])}\n"); f.write(body)
                    with open(ext) as e: shutil.copyfileobj(e, f)
                    for x in lits[i]: f.write(f"{x} 0\n")
                r.update(prove(leg, fi, pre + ".proof", ocap, ccap))
                r["certified"] = verified(leg, r)
                if r.get("offline_result") == "TIMEOUT" or "TIMEOUT" in (r.get("cake_lpr", "") + r.get("drat_trim", "")): over = True
        if over: r["over_cap"] = True
        with lock, open(status_f, "a") as f: f.write(json.dumps(r) + "\n")
        kids = None
        if over and not stop.is_set():
            s = split(i, pre + ".ext"); kids = s.get("children") if s["ok"] else None
            if not s["ok"]:
                with lock: nocap.add(i); todo.append(i)     # cannot split: rerun this node without caps
        keep = (not r["certified"]) and not over and res != "SAT"
        for x in (".ext", ".Fi.cnf", ".proof", ".final.cnf", ".model", ".col", ".cube"):
            if os.path.exists(pre + x) and not (keep and x in (".ext", ".Fi.cnf")): os.remove(pre + x)
        return ("done", i, (r, kids))

    t0 = time.time(); done_n = 0
    with ThreadPoolExecutor(A.jobs) as ex:
        running = set()
        while (todo or running) and not stop.is_set():
            while todo and len(running) < A.jobs:
                running.add(ex.submit(work, todo.popleft()))
            fin, running = wait(running, return_when=FIRST_COMPLETED)
            for fu in fin:
                kind, i, payload = fu.result()
                if kind != "done": continue
                r, kids = payload; done_n += 1
                if kids:
                    for c in reversed(kids): todo.appendleft(c)
                msg = (f"{i}: {r['solve_result']} solve={r['solve_secs']}s offline={r.get('offline_secs')}s check={r.get('check_secs')}s "
                       f"certified={r['certified']}" + (f" OVER-CAP -> split into {len(kids)}" if kids else (" OVER-CAP, split FAILED" if r.get("over_cap") else ""))
                       + f" [queue {len(todo)}, done {done_n}]")
                log(msg)
                if r["solve_result"] == "SAT": log(f"SAT at {i}: checkA={r.get('checkA')} checkB={r.get('checkB')}")
    # ---- summary
    cert = set(); sat = []
    for l in open(status_f):
        d = json.loads(l); i = d.get("id", str(d.get("cube")))
        if d.get("certified"): cert.add(i)
        if d.get("solve_result") == "SAT": sat.append(i)
    def ok(i): return i in cert or (i in children and all(ok(c) for c in children[i]))
    ntop = sum(ok(i) for i in top)
    summ = {"leg": leg, "top_cubes": len(top), "top_certified": ntop, "splits": len(children),
            "leaves_certified": len(cert), "sat": sat, "wall_secs_this_run": round(time.time() - t0, 1)}
    summ["VERDICT"] = ("UNSAT CERTIFIED (tree: every top-level cube certified directly or via verified splits)" if ntop == len(top)
                       else ("SAT found" if sat else "INCOMPLETE"))
    json.dump(summ, open(W + "/summary.json", "w"), indent=1); log("SUMMARY " + json.dumps(summ))

if __name__ == "__main__":
    main()
