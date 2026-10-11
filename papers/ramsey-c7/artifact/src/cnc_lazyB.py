#!/usr/bin/env python3
"""Second, independent certified cube-and-conquer leg (encoding B), resumable.
  cnc_lazyB.py BASE_B.cnf n a b c CUBES WORKDIR [--jobs J] [--cube-timeout S] [--keep]
Independent of leg 1 at every step except the cube splitter (march_cu) and the colouring checkers:
  encoding  : genB.py (2 vars/edge, itertools cycle enumeration) instead of rlib.EncA (one-hot, DFS)
  SB        : genB lex-leader, adjacent transpositions over encoding-B variable order (brute-force tested: test_sbB.py)
  legitimacy: check_cnfB.py instead of check_cnf.py
  lazy solver: lazyB.py (pysat CaDiCaL CEGAR, own cycle DFS) instead of prop/cycprop.cpp (external propagator)
  proofs    : kissat DRAT + drat-trim per cube instead of CaDiCaL LRAT + cake_lpr
  coverage  : negated cubes UNSAT, checked by BOTH kissat+drat-trim and CaDiCaL+cake_lpr (fallback BASE + negated cubes)
Per cube: lazyB (cube as assumptions) -> E_i; check_cnfB E_i cyclesonly; F_i = BASE + E_i + cube units; kissat DRAT; drat-trim.
SAT cube: colouring checked by checkA.py and checkB.py; stop."""
import sys, os, json, time, hashlib, subprocess, argparse, threading, shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
R = "/workspace/ramsey-c7"; T = R + "/tools"
KISSAT = T + "/kissat/build/kissat"; DT = T + "/drat-trim/drat-trim"; CADICAL = T + "/cadical/build/cadical"; CAKE = T + "/cake_lpr/cake_lpr"
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

def drat(cnf, proof, timeout=None):
    t0 = time.time()
    try:
        p = subprocess.run([KISSAT, "-q", cnf, proof], capture_output=True, text=True, timeout=timeout)
        rc = p.returncode
    except subprocess.TimeoutExpired:
        return {"offline_result": "TIMEOUT", "offline_secs": round(time.time() - t0, 1)}
    out = {"offline_result": {10: "SAT", 20: "UNSAT"}.get(rc, f"exit{rc}"), "offline_secs": round(time.time() - t0, 1)}
    if rc != 20: return out
    out["proof_bytes"] = os.path.getsize(proof); out["proof_sha256"] = sha(proof)
    t1 = time.time(); c = subprocess.run([DT, cnf, proof, "-t", "200000"], capture_output=True, text=True)
    out["check_secs"] = round(time.time() - t1, 1)
    out["drat_trim"] = "s VERIFIED" if "s VERIFIED" in c.stdout and "NOT VERIFIED" not in c.stdout else "FAIL: " + c.stdout[-300:]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("n", type=int); ap.add_argument("a", type=int); ap.add_argument("b", type=int); ap.add_argument("c", type=int)
    ap.add_argument("cubes"); ap.add_argument("W")
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--cube-timeout", type=int, default=21600)
    ap.add_argument("--keep", action="store_true")
    A = ap.parse_args()
    n, L = A.n, (A.a, A.b, A.c)
    W = os.path.abspath(A.W); os.makedirs(W + "/tmp", exist_ok=True)
    base = os.path.abspath(A.base)
    meta = W + "/meta.json"
    if not os.path.exists(meta):
        if os.path.abspath(A.cubes) != W + "/cubes": shutil.copy(A.cubes, W + "/cubes")
        json.dump({"leg": "B", "base": base, "base_sha256": sha(base), "cubes_sha256": sha(W + "/cubes"), "n": n, "L": L,
                   "started": time.ctime()}, open(meta, "w"), indent=1)
    m = json.load(open(meta))
    assert m["base_sha256"] == sha(base) and m["cubes_sha256"] == sha(W + "/cubes"), "inputs changed"
    cubes_f = W + "/cubes"
    log(W, f"start leg B base={base} n={n} L={L} jobs={A.jobs}")
    if not os.path.exists(W + "/check_base.log"):
        r = subprocess.run(["python3", R + "/src/check_cnfB.py", base, str(n), *map(str, L), "base"], capture_output=True, text=True)
        open(W + "/check_base.log", "w").write(r.stdout + r.stderr)
        log(W, "check_cnfB(base): " + r.stdout.strip().splitlines()[-1])
        if r.returncode != 0: sys.exit("base failed legitimacy check")
    cubes = [[int(x) for x in l.split()[1:-1]] for l in open(cubes_f) if l.startswith("a ")]
    nv, ncl, body = read_cnf(base)
    cov = W + "/coverage.json"
    if not os.path.exists(cov):
        tc = W + "/tmp/coverage.cnf"
        def write_cov(with_base):
            with open(tc, "w") as f:
                f.write(f"p cnf {nv} {(ncl if with_base else 0) + len(cubes)}\n")
                if with_base: f.write(body)
                for cb in cubes: f.write(" ".join(str(-x) for x in cb) + " 0\n")
        write_cov(False); r = drat(tc, W + "/tmp/cov.drat"); r["kind"] = "negated cubes alone"
        if r["offline_result"] == "SAT":
            write_cov(True); r = drat(tc, W + "/tmp/cov.drat"); r["kind"] = "base + negated cubes"
        c1 = subprocess.run([CADICAL, "-q", "--lrat", tc, W + "/tmp/cov.lrat"], capture_output=True)
        c2 = subprocess.run([CAKE, tc, W + "/tmp/cov.lrat"], capture_output=True, text=True)
        r["cake_lpr"] = "s VERIFIED UNSAT" if c1.returncode == 20 and "s VERIFIED UNSAT" in c2.stdout else "FAIL"
        json.dump(r, open(cov, "w")); log(W, f"coverage: {r}")
        for x in (tc, W + "/tmp/cov.drat", W + "/tmp/cov.lrat"):
            if os.path.exists(x): os.remove(x)
    covr = json.load(open(cov))
    if covr.get("drat_trim") != "s VERIFIED" or covr.get("cake_lpr") != "s VERIFIED UNSAT": sys.exit("coverage not certified")
    status_f = W + "/status.jsonl"; done = {}
    if os.path.exists(status_f):
        for l in open(status_f):
            d = json.loads(l)
            if d.get("certified"): done[d["cube"]] = d
    todo = [i for i in range(len(cubes)) if i not in done]
    log(W, f"cubes={len(cubes)} already certified: {len(done)}  to do: {len(todo)}")
    stop = threading.Event()
    def work(i):
        if stop.is_set(): return None
        pre = f"{W}/tmp/c{i}"; t0 = time.time()
        try:
            p = subprocess.run(["python3", R + "/src/lazyB.py", base, str(n), *map(str, L), cubes_f, str(i), pre,
                                "--maxsecs", str(A.cube_timeout)], capture_output=True, text=True, timeout=A.cube_timeout + 600)
            js = [l for l in p.stdout.splitlines() if l.startswith("{")]
            res = json.loads(js[0])["result"] if js else f"crash{p.returncode}"
        except subprocess.TimeoutExpired:
            res = "TIMEOUT"
        r = {"cube": i, "lits": cubes[i], "solve_result": res, "solve_secs": round(time.time() - t0, 1), "certified": False}
        if res == "SAT":
            stop.set()
            shutil.copy(pre + ".col", f"{W}/model_cube{i}.col")
            a = subprocess.run(["python3", R + "/src/checkA.py", pre + ".col", *map(str, L)], capture_output=True, text=True)
            b = subprocess.run(["python3", R + "/src/checkB.py", pre + ".col", *map(str, L)], capture_output=True, text=True)
            r["checkA"] = a.stdout.strip().splitlines()[-1]; r["checkB"] = b.stdout.strip().splitlines()[-1]
        elif res == "UNSAT":
            ext = pre + ".ext"; r["ext_clauses"] = sum(1 for _ in open(ext))
            c = subprocess.run(["python3", R + "/src/check_cnfB.py", ext, str(n), *map(str, L), "cyclesonly"], capture_output=True, text=True)
            r["ext_check"] = c.stdout.strip().splitlines()[-1]
            if c.returncode == 0:
                fi = pre + ".Fi.cnf"
                with open(fi, "w") as f:
                    f.write(f"p cnf {nv} {ncl + r['ext_clauses'] + len(cubes[i])}\n"); f.write(body)
                    with open(ext) as e: shutil.copyfileobj(e, f)
                    for x in cubes[i]: f.write(f"{x} 0\n")
                r.update(drat(fi, pre + ".drat", A.cube_timeout))
                r["certified"] = r.get("drat_trim") == "s VERIFIED"
        for x in ([pre + ".ext", pre + ".Fi.cnf", pre + ".col"] if (r["certified"] and not A.keep) else []) + [pre + ".drat"]:
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
    cert = [i for i, d in allr.items() if d["certified"]]; sat = [i for i, d in allr.items() if d["solve_result"] == "SAT"]
    other = sorted(i for i in range(len(cubes)) if i not in cert and i not in sat)
    summ = {"leg": "B", "cubes": len(cubes), "certified_unsat": len(cert), "sat": sat, "n_unfinished": len(other), "unfinished": other[:50],
            "coverage_drat_trim": covr.get("drat_trim"), "coverage_cake_lpr": covr.get("cake_lpr"), "coverage_kind": covr.get("kind"),
            "wall_secs_this_run": round(time.time() - t0, 1),
            "cpu_solve": round(sum(d.get("solve_secs", 0) for d in allr.values()), 1),
            "cpu_offline": round(sum(d.get("offline_secs", 0) or 0 for d in allr.values()), 1),
            "cpu_check": round(sum(d.get("check_secs", 0) or 0 for d in allr.values()), 1)}
    summ["VERDICT"] = ("UNSAT CERTIFIED (leg B: base legit, coverage + every cube: cycle clauses legit, DRAT checked by drat-trim)"
                       if len(cert) == len(cubes) else ("SAT cube found" if sat else "INCOMPLETE"))
    json.dump(summ, open(W + "/summary.json", "w"), indent=1)
    log(W, "SUMMARY " + json.dumps(summ))

if __name__ == "__main__":
    main()
