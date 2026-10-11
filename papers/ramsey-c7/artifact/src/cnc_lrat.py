#!/usr/bin/env python3
"""Certified, resumable cube-and-conquer.
  cnc_lrat.py F.cnf WORKDIR [--depth D] [--jobs J] [--keep-proofs] [--cube-timeout S] [--n N --cycles a b c --sb MODE]
Pipeline
  0. (optional, if --n given) clause-legitimacy check of F with check_cnf.py.
  1. Cubes: march_cu F -d D  -> WORKDIR/cubes (kept; sha256 recorded). Skipped if cubes file exists (resume).
  2. Coverage certificate: T = { (-l1 v ... v -lk) : cube (l1..lk) }.  T UNSAT <=> every total assignment satisfies some
     cube.  T is solved by CaDiCaL with an LRAT proof and checked by cake_lpr.
  3. Each cube i: F_i = F + unit clauses of cube i; CaDiCaL --lrat (binary) -> cake_lpr check. Result appended to
     WORKDIR/status.jsonl (one JSON line per finished cube); finished cubes are skipped on restart.
     Proof file deleted after a successful check unless --keep-proofs (its sha256 and size are logged).
  Conclusion: if T is UNSAT (checked) and every F_i is UNSAT (checked), then F is UNSAT: a model of F would satisfy
  some cube i (step 2), hence be a model of F_i.
  A SAT cube stops the run and writes WORKDIR/model_cube<i>.txt.  A cube that exceeds --cube-timeout is logged as
  'timeout' (re-split it later by running this script on F_i with its own workdir; the coverage argument composes).
"""
import sys, os, json, time, hashlib, subprocess, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
R = "/workspace/ramsey-c7"; T = R + "/tools"
CADICAL = T + "/cadical/build/cadical"; CAKE = T + "/cake_lpr/cake_lpr"; MARCH = T + "/CnC/march_cu/march_cu"
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
    with open(F) as f:
        for l in f:
            if l.startswith("p cnf"): _, _, nv, ncl = l.split(); nv, ncl = int(nv), int(ncl)
            elif not l.startswith("c"): body.append(l)
    return nv, ncl, "".join(body)

def solve_and_check(cnf, proof, timeout=None):
    t0 = time.time()
    try:
        p = subprocess.run([CADICAL, "-q", "--lrat", cnf, proof], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"result": "timeout", "solve_secs": round(time.time() - t0, 1)}
    st = time.time() - t0
    res = {10: "SAT", 20: "UNSAT"}.get(p.returncode, f"exit{p.returncode}")
    out = {"result": res, "solve_secs": round(st, 1)}
    if res == "SAT":
        out["model"] = [int(x) for l in p.stdout.splitlines() if l.startswith("v ") for x in l.split()[1:]]
        return out
    if res != "UNSAT": return out
    out["proof_bytes"] = os.path.getsize(proof); out["proof_sha256"] = sha(proof)
    t1 = time.time()
    c = subprocess.run([CAKE, cnf, proof], capture_output=True, text=True)
    out["check_secs"] = round(time.time() - t1, 1)
    out["cake_lpr"] = "s VERIFIED UNSAT" if "s VERIFIED UNSAT" in c.stdout else ("FAIL: " + (c.stdout + c.stderr)[-300:])
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("F"); ap.add_argument("W")
    ap.add_argument("--depth", type=int, default=8); ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--keep-proofs", action="store_true"); ap.add_argument("--cube-timeout", type=float, default=None)
    ap.add_argument("--n", type=int); ap.add_argument("--cycles", type=int, nargs=3); ap.add_argument("--sb", default="tradj")
    ap.add_argument("--tmp", default=None, help="dir for per-cube CNFs (default WORKDIR/tmp)")
    A = ap.parse_args()
    W = os.path.abspath(A.W); os.makedirs(W, exist_ok=True)
    tmp = A.tmp or W + "/tmp"; os.makedirs(tmp, exist_ok=True); os.makedirs(W + "/proofs", exist_ok=True)
    F = os.path.abspath(A.F)
    meta = W + "/meta.json"
    if not os.path.exists(meta):
        json.dump({"F": F, "F_sha256": sha(F), "depth": A.depth, "started": time.ctime()}, open(meta, "w"), indent=1)
    else:
        m = json.load(open(meta)); assert m["F_sha256"] == sha(F), "formula changed since this workdir was created"
    log(W, f"start F={F} jobs={A.jobs}")
    # 0. legitimacy
    if A.n and not os.path.exists(W + "/check_cnf.log"):
        a, b, c = A.cycles
        r = subprocess.run(["python3", R + "/src/check_cnf.py", F, str(A.n), str(a), str(b), str(c), A.sb], capture_output=True, text=True)
        open(W + "/check_cnf.log", "w").write(r.stdout + r.stderr)
        log(W, "check_cnf: " + r.stdout.strip().splitlines()[-1])
        if r.returncode != 0: sys.exit("CNF legitimacy check failed")
    # 1. cubes
    cubes_f = W + "/cubes"
    if not os.path.exists(cubes_f):
        t0 = time.time()
        subprocess.run([MARCH, F, "-o", cubes_f + ".tmp", "-d", str(A.depth)], capture_output=True, text=True)
        os.rename(cubes_f + ".tmp", cubes_f)
        log(W, f"march_cu depth {A.depth}: {time.time()-t0:.1f}s")
    cubes = [[int(x) for x in l.split()[1:-1]] for l in open(cubes_f) if l.startswith("a ")]
    log(W, f"cubes={len(cubes)} sha256={sha(cubes_f)[:16]}")
    nv, ncl, body = read_cnf(F)
    # 2. coverage certificate
    cov = W + "/coverage.json"
    if not os.path.exists(cov):
        tc = W + "/coverage.cnf"
        with open(tc, "w") as f:
            f.write(f"p cnf {nv} {len(cubes)}\n")
            for cb in cubes: f.write(" ".join(str(-x) for x in cb) + " 0\n")
        r = solve_and_check(tc, W + "/proofs/coverage.lrat")
        r.pop("model", None); r["kind"] = "negated cubes alone"
        if r.get("result") == "SAT":
            # march_cu drops leaves it refuted itself; prove F AND (negated cubes) UNSAT instead
            log(W, "pure coverage CNF is SAT (march refuted some leaves itself); using F + negated cubes")
            with open(tc, "w") as f:
                f.write(f"p cnf {nv} {ncl + len(cubes)}\n"); f.write(body)
                for cb in cubes: f.write(" ".join(str(-x) for x in cb) + " 0\n")
            r = solve_and_check(tc, W + "/proofs/coverage.lrat")
            r.pop("model", None); r["kind"] = "F + negated cubes"
        if os.path.exists(W + "/proofs/coverage.lrat") and r.get("cake_lpr") == "s VERIFIED UNSAT": os.remove(W + "/proofs/coverage.lrat")
        json.dump(r, open(cov, "w"))
        log(W, f"coverage: {r}")
    covr = json.load(open(cov))
    if covr.get("result") != "UNSAT" or covr.get("cake_lpr") != "s VERIFIED UNSAT":
        sys.exit("cube set does not provably cover the space: " + str(covr))
    # 3. cubes
    status_f = W + "/status.jsonl"
    done = {}
    if os.path.exists(status_f):
        for l in open(status_f):
            d = json.loads(l)
            if d["result"] in ("UNSAT",) and d.get("cake_lpr") == "s VERIFIED UNSAT": done[d["cube"]] = d
    todo = [i for i in range(len(cubes)) if i not in done]
    log(W, f"already certified: {len(done)}  to do: {len(todo)}")
    stop = threading.Event()
    def work(i):
        if stop.is_set(): return None
        cnf = f"{tmp}/cube{i}.cnf"; proof = f"{W}/proofs/cube{i}.lrat"
        with open(cnf, "w") as f:
            f.write(f"p cnf {nv} {ncl + len(cubes[i])}\n"); f.write(body)
            for x in cubes[i]: f.write(f"{x} 0\n")
        r = solve_and_check(cnf, proof, A.cube_timeout)
        r["cube"] = i; r["lits"] = cubes[i]
        if r["result"] == "SAT":
            stop.set()
            with open(f"{W}/model_cube{i}.txt", "w") as f: f.write("v " + " ".join(map(str, r["model"])) + " 0\n")
            r.pop("model")
        os.remove(cnf)
        if os.path.exists(proof) and not A.keep_proofs and r.get("cake_lpr") == "s VERIFIED UNSAT": os.remove(proof)
        with lock, open(status_f, "a") as f: f.write(json.dumps(r) + "\n")
        return r
    t0 = time.time()
    with ThreadPoolExecutor(A.jobs) as ex:
        futs = [ex.submit(work, i) for i in todo]
        for k, fu in enumerate(as_completed(futs)):
            r = fu.result()
            if r: log(W, f"cube {r['cube']}: {r['result']} solve={r.get('solve_secs')}s check={r.get('check_secs')}s {r.get('cake_lpr','')} [{k+1}/{len(todo)}]")
    # summary
    allr = {}
    for l in open(status_f):
        d = json.loads(l); allr[d["cube"]] = d
    cert = [i for i, d in allr.items() if d["result"] == "UNSAT" and d.get("cake_lpr") == "s VERIFIED UNSAT"]
    sat = [i for i, d in allr.items() if d["result"] == "SAT"]
    other = [i for i in range(len(cubes)) if i not in cert and i not in sat]
    summ = {"cubes": len(cubes), "certified_unsat": len(cert), "sat": sat, "unfinished_or_failed": other,
            "coverage": covr.get("cake_lpr"), "wall_secs_this_run": round(time.time() - t0, 1),
            "cpu_solve_secs_total": round(sum(d.get("solve_secs", 0) for d in allr.values()), 1),
            "cpu_check_secs_total": round(sum(d.get("check_secs", 0) for d in allr.values()), 1)}
    summ["VERDICT"] = ("FORMULA UNSAT (certified: coverage + all cubes checked by cake_lpr)" if len(cert) == len(cubes)
                       else ("SAT cube found" if sat else "INCOMPLETE"))
    json.dump(summ, open(W + "/summary.json", "w"), indent=1)
    log(W, "SUMMARY " + json.dumps(summ))

if __name__ == "__main__":
    main()
