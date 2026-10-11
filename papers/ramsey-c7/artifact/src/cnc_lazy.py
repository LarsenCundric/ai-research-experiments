#!/usr/bin/env python3
"""Certified, resumable cube-and-conquer with the lazy cycle-clause solver (prop/cycprop).
  cnc_lazy.py BASE.cnf n a b c CUBES WORKDIR [--jobs J] [--cube-timeout S] [--sb tradj] [--keep]
BASE.cnf = lazy base formula from genA.py --eager-upto 5 (ALO, AMO, SB, short-cycle clauses; same variable numbering as the
full encoding A). Steps:
  0. check_cnf.py BASE (mode = sb): every clause legitimate (ALO / AMO / forbidden cycle / regenerated SB clause).
  1. Coverage: T = negated cubes; T UNSAT (CaDiCaL LRAT + cake_lpr). Fallback: BASE + negated cubes.
  2. Per cube i: cycprop BASE under assumptions Q_i -> E_i (all cycle clauses it added) and UNSAT/SAT.
     UNSAT: check_cnf.py E_i cyclesonly (every added clause is a genuine forbidden-cycle clause);
            F_i = BASE + E_i + units(Q_i); CaDiCaL --lrat F_i; cake_lpr F_i proof.
     SAT:   decode model, verify with checkA.py and checkB.py; stop.
  Conclusion: BASE + E_i are all satisfied by the lex-leader of any good colouring (step 0 + cycle legitimacy), F_i UNSAT means
  that colouring falsifies Q_i, coverage means it satisfies some Q_j: contradiction for every good colouring, so none exists.
  status.jsonl records finished cubes; rerun the same command to resume. Proofs, E_i and F_i deleted after success (sha256 logged)
  unless --keep."""
import sys, os, json, time, hashlib, subprocess, argparse, threading, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
R = "/workspace/ramsey-c7"; T = R + "/tools"
CADICAL = T + "/cadical/build/cadical"; CAKE = T + "/cake_lpr/cake_lpr"; CYC = R + "/prop/cycprop"
lock = threading.Lock()

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def log(W, msg):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + msg
    print(line, flush=True)
    with lock, open(W + "/run.log", "a") as f: f.write(line + "\n")

def read_cnf(F):
    nv = ncl = None; body = []
    for l in open(F):
        if l.startswith("p cnf"): _, _, a, b = l.split(); nv, ncl = int(a), int(b)
        elif not l.startswith("c"): body.append(l)
    return nv, ncl, "".join(body)

def lrat_check(cnf, proof):
    t0 = time.time(); p = subprocess.run([CADICAL, "-q", "--lrat", cnf, proof], capture_output=True, text=True)
    out = {"offline_result": {10: "SAT", 20: "UNSAT"}.get(p.returncode, f"exit{p.returncode}"), "offline_secs": round(time.time() - t0, 1)}
    if p.returncode != 20: return out
    out["proof_bytes"] = os.path.getsize(proof); out["proof_sha256"] = sha(proof)
    t1 = time.time(); c = subprocess.run([CAKE, cnf, proof], capture_output=True, text=True)
    out["check_secs"] = round(time.time() - t1, 1)
    out["cake_lpr"] = "s VERIFIED UNSAT" if "s VERIFIED UNSAT" in c.stdout else "FAIL: " + (c.stdout + c.stderr)[-300:]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("n", type=int); ap.add_argument("a", type=int); ap.add_argument("b", type=int); ap.add_argument("c", type=int)
    ap.add_argument("cubes"); ap.add_argument("W")
    ap.add_argument("--jobs", type=int, default=3); ap.add_argument("--cube-timeout", type=int, default=21600)
    ap.add_argument("--sb", default="tradj"); ap.add_argument("--keep", action="store_true")
    A = ap.parse_args()
    n, L = A.n, (A.a, A.b, A.c)
    W = os.path.abspath(A.W); os.makedirs(W + "/tmp", exist_ok=True); os.makedirs(W + "/proofs", exist_ok=True)
    base = os.path.abspath(A.base); cubes_f = os.path.abspath(A.cubes)
    meta = W + "/meta.json"
    if not os.path.exists(meta):
        if os.path.abspath(cubes_f) != W + "/cubes": shutil.copy(cubes_f, W + "/cubes")
        json.dump({"base": base, "base_sha256": sha(base), "cubes_sha256": sha(W + "/cubes"), "n": n, "L": L, "sb": A.sb,
                   "started": time.ctime()}, open(meta, "w"), indent=1)
    m = json.load(open(meta))
    assert m["base_sha256"] == sha(base) and m["cubes_sha256"] == sha(W + "/cubes"), "inputs changed since workdir creation"
    cubes_f = W + "/cubes"
    log(W, f"start base={base} n={n} L={L} jobs={A.jobs}")
    if not os.path.exists(W + "/check_base.log"):
        r = subprocess.run(["python3", R + "/src/check_cnf.py", base, str(n), *map(str, L), A.sb], capture_output=True, text=True)
        open(W + "/check_base.log", "w").write(r.stdout + r.stderr)
        log(W, "check_cnf(base): " + r.stdout.strip().splitlines()[-1])
        if r.returncode != 0: sys.exit("base formula failed legitimacy check")
    cubes = [[int(x) for x in l.split()[1:-1]] for l in open(cubes_f) if l.startswith("a ")]
    nv, ncl, body = read_cnf(base)
    log(W, f"cubes={len(cubes)}")
    cov = W + "/coverage.json"
    if not os.path.exists(cov):
        tc = W + "/tmp/coverage.cnf"
        with open(tc, "w") as f:
            f.write(f"p cnf {nv} {len(cubes)}\n")
            for cb in cubes: f.write(" ".join(str(-x) for x in cb) + " 0\n")
        r = lrat_check(tc, W + "/proofs/coverage.lrat"); r["kind"] = "negated cubes alone"
        if r["offline_result"] == "SAT":
            with open(tc, "w") as f:
                f.write(f"p cnf {nv} {ncl + len(cubes)}\n"); f.write(body)
                for cb in cubes: f.write(" ".join(str(-x) for x in cb) + " 0\n")
            r = lrat_check(tc, W + "/proofs/coverage.lrat"); r["kind"] = "base + negated cubes"
        json.dump(r, open(cov, "w")); log(W, f"coverage: {r}")
        for x in (tc, W + "/proofs/coverage.lrat"):
            if os.path.exists(x): os.remove(x)
    covr = json.load(open(cov))
    if covr.get("cake_lpr") != "s VERIFIED UNSAT": sys.exit("coverage not certified: " + str(covr))
    status_f = W + "/status.jsonl"; done = {}
    if os.path.exists(status_f):
        for l in open(status_f):
            d = json.loads(l)
            if d.get("certified"): done[d["cube"]] = d
    todo = [i for i in range(len(cubes)) if i not in done]
    log(W, f"already certified: {len(done)}  to do: {len(todo)}")
    stop = threading.Event()
    def work(i):
        if stop.is_set(): return None
        pre = f"{W}/tmp/c{i}"
        t0 = time.time()
        try:
            p = subprocess.run([CYC, base, str(n), *map(str, L), "6", "1", pre, "0", cubes_f, str(i)],
                               capture_output=True, text=True, timeout=A.cube_timeout)
            js = [l for l in p.stdout.splitlines() if l.startswith("{")]
            res = json.loads(js[0])["result"] if js else f"crash{p.returncode}"
        except subprocess.TimeoutExpired:
            res = "TIMEOUT"
        r = {"cube": i, "lits": cubes[i], "solve_result": res, "solve_secs": round(time.time() - t0, 1), "certified": False}
        if res == "SAT":
            stop.set()
            col = f"{W}/model_cube{i}.txt"
            subprocess.run(["python3", R + "/src/model2col.py", pre + ".model", str(n), col], capture_output=True)
            a = subprocess.run(["python3", R + "/src/checkA.py", col, *map(str, L)], capture_output=True, text=True)
            b = subprocess.run(["python3", R + "/src/checkB.py", col, *map(str, L)], capture_output=True, text=True)
            r["checkA"] = a.stdout.strip().splitlines()[-1]; r["checkB"] = b.stdout.strip().splitlines()[-1]
        elif res == "UNSAT":
            ext = pre + ".ext"; r["ext_clauses"] = sum(1 for _ in open(ext))
            c = subprocess.run(["python3", R + "/src/check_cnf.py", ext, str(n), *map(str, L), "cyclesonly"], capture_output=True, text=True)
            r["ext_check"] = c.stdout.strip().splitlines()[-1]
            if c.returncode == 0:
                fi = pre + ".Fi.cnf"
                with open(fi, "w") as f:
                    f.write(f"p cnf {nv} {ncl + r['ext_clauses'] + len(cubes[i])}\n"); f.write(body)
                    with open(ext) as e: shutil.copyfileobj(e, f)
                    for x in cubes[i]: f.write(f"{x} 0\n")
                r.update(lrat_check(fi, pre + ".lrat"))
                r["certified"] = r.get("cake_lpr") == "s VERIFIED UNSAT"
        if r["certified"] and not A.keep:
            for x in (pre + ".ext", pre + ".Fi.cnf", pre + ".lrat", pre + ".final.cnf", pre + ".model"):
                if os.path.exists(x): os.remove(x)
        else:
            for x in (pre + ".lrat", pre + ".final.cnf"):
                if os.path.exists(x): os.remove(x)
        with lock, open(status_f, "a") as f: f.write(json.dumps(r) + "\n")
        return r
    t0 = time.time()
    with ThreadPoolExecutor(A.jobs) as ex:
        futs = [ex.submit(work, i) for i in todo]
        for k, fu in enumerate(as_completed(futs)):
            r = fu.result()
            if r: log(W, f"cube {r['cube']}: {r['solve_result']} solve={r['solve_secs']}s offline={r.get('offline_secs')}s check={r.get('check_secs')}s certified={r['certified']} [{k+1}/{len(todo)}]")
    allr = {}
    for l in open(status_f):
        d = json.loads(l); allr[d["cube"]] = d
    cert = [i for i, d in allr.items() if d["certified"]]
    sat = [i for i, d in allr.items() if d["solve_result"] == "SAT"]
    other = sorted(i for i in range(len(cubes)) if i not in cert and i not in sat)
    summ = {"cubes": len(cubes), "certified_unsat": len(cert), "sat": sat, "unfinished_or_failed": other[:50], "n_unfinished": len(other),
            "coverage": covr.get("cake_lpr"), "coverage_kind": covr.get("kind"), "wall_secs_this_run": round(time.time() - t0, 1),
            "cpu_solve": round(sum(d.get("solve_secs", 0) for d in allr.values()), 1),
            "cpu_offline": round(sum(d.get("offline_secs", 0) or 0 for d in allr.values()), 1),
            "cpu_check": round(sum(d.get("check_secs", 0) or 0 for d in allr.values()), 1)}
    summ["VERDICT"] = ("UNSAT CERTIFIED (base legit, coverage + every cube: cycle clauses legit, LRAT checked by cake_lpr)"
                       if len(cert) == len(cubes) else ("SAT cube found" if sat else "INCOMPLETE"))
    json.dump(summ, open(W + "/summary.json", "w"), indent=1)
    log(W, "SUMMARY " + json.dumps(summ))

if __name__ == "__main__":
    main()
