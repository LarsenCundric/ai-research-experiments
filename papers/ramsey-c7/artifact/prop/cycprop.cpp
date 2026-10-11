// cycprop: CaDiCaL + external propagator that adds forbidden monochromatic cycle clauses lazily.
// usage: cycprop base.cnf n a b c lazy_from mode out_prefix [--lrat]
//   base.cnf : encoding-A CNF (vars 3e+c+1, row-major edges) with ALO/AMO/SB and eager short-cycle clauses
//   colors with L[c] >= lazy_from are handled lazily by the propagator
//   mode 0: only check complete models; 1: conflict clauses on partial assignments; 2: also unit-propagating clauses
// Writes out_prefix.ext (all external clauses, DIMACS lines) and on UNSAT out_prefix.final.cnf (= base + ext);
// on SAT writes model line "v ..." to out_prefix.model.
#include "../tools/cadical/src/cadical.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <deque>
#include <unordered_set>
#include <string>
#include <chrono>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <csignal>
using namespace std;
typedef unsigned int u32;

static int N, L[3], LAZY_FROM, MODE;
static int EID[32][32];
static int EU[600], EV[600];
static inline int var_of(int u, int v, int c) { return 3 * EID[u][v] + c + 1; }

struct Prop : CaDiCaL::ExternalPropagator {
  int nbase;
  vector<signed char> val;            // per var (1..nbase): 0 unassigned, 1 true, -1 false
  vector<int> trail; vector<size_t> lvl;
  u32 adjT[3][32], adjP[3][32];       // true graph, possible (not false) graph
  deque<int> pending;                 // newly true base vars of lazy colors
  deque<vector<int>> cq;              // clause queue
  vector<int> cur; size_t curpos = 0; bool emitting = false;
  unordered_set<string> seen;
  FILE *ext;
  long nconf = 0, nunit = 0, nmodel = 0, nclauses = 0;
  bool lazy[3];
  Prop(int nb, FILE *f) : nbase(nb), val(nb + 1, 0), ext(f) {
    for (int c = 0; c < 3; c++) { lazy[c] = L[c] >= LAZY_FROM;
      for (int v = 0; v < N; v++) { adjT[c][v] = 0; adjP[c][v] = ((1u << N) - 1) & ~(1u << v); } }
  }
  void assign(int lit) {
    int v = abs(lit); if (v > nbase) return;
    int e = (v - 1) / 3, c = (v - 1) % 3, a = EU[e], b = EV[e];
    if (lit > 0) { val[v] = 1; adjT[c][a] |= 1u << b; adjT[c][b] |= 1u << a; if (lazy[c] && MODE > 0) pending.push_back(v); }
    else { val[v] = -1; adjP[c][a] &= ~(1u << b); adjP[c][b] &= ~(1u << a); }
    trail.push_back(lit);
  }
  void unassign(int lit) {
    int v = abs(lit); int e = (v - 1) / 3, c = (v - 1) % 3, a = EU[e], b = EV[e];
    if (lit > 0) { adjT[c][a] &= ~(1u << b); adjT[c][b] &= ~(1u << a); }
    else { adjP[c][a] |= 1u << b; adjP[c][b] |= 1u << a; }
    val[v] = 0;
  }
  void notify_assignment(const vector<int> &lits) override { for (int l : lits) assign(l); }
  void notify_new_decision_level() override { lvl.push_back(trail.size()); }
  void notify_backtrack(size_t nl) override {
    size_t keep = lvl[nl]; while (trail.size() > keep) { unassign(trail.back()); trail.pop_back(); }
    lvl.resize(nl);
    deque<int> keepq; for (int v : pending) if (val[v] == 1) keepq.push_back(v); pending.swap(keepq);
  }
  // queue clause for cycle cyc (vertex list) in color c, dedup
  bool queue_cycle(const vector<int> &cyc, int c) {
    int k = cyc.size(); vector<int> cl(k);
    for (int t = 0; t < k; t++) cl[t] = -var_of(cyc[t], cyc[(t + 1) % k], c);
    vector<int> key = cl; sort(key.begin(), key.end());
    string s((char *)key.data(), key.size() * sizeof(int));
    if (!seen.insert(s).second) return false;
    cq.push_back(cl); nclauses++;
    bool allf = true; for (int x : cl) if (val[-x] != 1) { allf = false; break; }
    if (allf) nconf++; else nunit++;
    for (int x : cl) fprintf(ext, "%d ", x); fprintf(ext, "0\n");
    return true;
  }
  // DFS: find paths from x to target of exactly 'rem' more edges in color c, with at most 'budget' non-true (unassigned) edges
  int found_here; int limit;
  vector<int> path;
  void dfs(int x, int target, int rem, int budget, u32 used, int c) {
    if (found_here >= limit) return;
    if (rem == 1) {
      if (adjP[c][x] >> target & 1) {
        bool tr = adjT[c][x] >> target & 1;
        if (tr || budget > 0) { vector<int> cyc = path; if (queue_cycle(cyc, c)) found_here++; }
      }
      return;
    }
    u32 cand = adjP[c][x] & ~used & ~(1u << target);
    if (budget == 0) cand &= adjT[c][x];
    while (cand) { int y = __builtin_ctz(cand); cand &= cand - 1;
      bool tr = adjT[c][x] >> y & 1;
      path.push_back(y); dfs(y, target, rem - 1, budget - (tr ? 0 : 1), used | (1u << y), c); path.pop_back();
      if (found_here >= limit) return; }
  }
  void process_pending() {
    while (!pending.empty() && cq.empty()) {
      int v = pending.front(); pending.pop_front();
      if (val[v] != 1) continue;
      int e = (v - 1) / 3, c = (v - 1) % 3, a = EU[e], b = EV[e];
      // cycles containing edge a-b: path b -> ... -> a with L-1 edges
      path.clear(); path.push_back(a); path.push_back(b);
      found_here = 0; limit = 64;
      dfs(b, a, L[c] - 1, MODE == 2 ? 1 : 0, (1u << a) | (1u << b), c);
    }
  }
  bool cb_check_found_model(const vector<int> &model) override {
    nmodel++;
    // full check of complete model (with current val arrays consistent with model)
    u32 G[3][32]; for (int c = 0; c < 3; c++) for (int v = 0; v < N; v++) G[c][v] = 0;
    for (int lit : model) { int v = abs(lit); if (lit > 0 && v <= nbase) { int e = (v - 1) / 3, c = (v - 1) % 3; G[c][EU[e]] |= 1u << EV[e]; G[c][EV[e]] |= 1u << EU[e]; } }
    int added = 0;
    for (int c = 0; c < 3 && added < 200; c++) { if (!lazy[c]) continue;
      // enumerate cycles with min vertex s
      for (int s = 0; s < N && added < 200; s++) {
        vector<int> p = {s}; vector<u32> cands = {G[c][s] & ~((2u << s) - 1)}; u32 used = 1u << s;
        while (!cands.empty() && added < 200) {
          u32 &cd = cands.back(); if (!cd) { cands.pop_back(); used &= ~(1u << p.back()); p.pop_back(); continue; }
          int w = __builtin_ctz(cd); cd &= cd - 1;
          if ((int)p.size() == L[c] - 1) { if ((G[c][w] >> s & 1) && p[1] < w) { vector<int> cyc = p; cyc.push_back(w); if (queue_cycle(cyc, c)) added++; } continue; }
          p.push_back(w); used |= 1u << w; cands.push_back(G[c][w] & ~used & ~((2u << s) - 1));
        }
      }
    }
    return added == 0;
  }
  bool cb_has_external_clause(bool &forgettable) override {
    forgettable = false;
    if (cq.empty()) process_pending();
    return !cq.empty();
  }
  int cb_add_external_clause_lit() override {
    if (!emitting) { cur = cq.front(); cq.pop_front(); curpos = 0; emitting = true; }
    if (curpos < cur.size()) return cur[curpos++];
    emitting = false; return 0;
  }
};

int main(int argc, char **argv) {
  if (argc < 9) { fprintf(stderr, "usage: cycprop base.cnf n a b c lazy_from mode out_prefix\n"); return 1; }
  const char *cnf = argv[1]; N = atoi(argv[2]); L[0] = atoi(argv[3]); L[1] = atoi(argv[4]); L[2] = atoi(argv[5]);
  LAZY_FROM = atoi(argv[6]); MODE = atoi(argv[7]); string out = argv[8];
  int e = 0; for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) { EID[i][j] = EID[j][i] = e; EU[e] = i; EV[e] = j; e++; }
  int nbase = 3 * e;
  auto t0 = chrono::steady_clock::now();
  CaDiCaL::Solver S;
  if (argc > 9) S.set("verbose", atoi(argv[9]));
  // read CNF
  ifstream in(cnf); string line; int nv = 0; long ncl = 0; vector<string> keep;
  while (getline(in, line)) { if (line.empty() || line[0] == 'c') continue;
    if (line[0] == 'p') { sscanf(line.c_str(), "p cnf %d %ld", &nv, &ncl); continue; }
    istringstream ss(line); int x; while (ss >> x) S.add(x); }
  FILE *ext = fopen((out + ".ext").c_str(), "w");
  Prop P(nbase, ext);
  S.connect_external_propagator(&P);
  for (int v = 1; v <= nbase; v++) S.add_observed_var(v);
  vector<int> assumptions;
  if (argc > 11) { // cube file + index (0-based): line "a l1 ... lk 0"
    ifstream cf(argv[10]); string cl; int idx = atoi(argv[11]), k = 0;
    while (getline(cf, cl)) { if (cl.size() < 2 || cl[0] != 'a') continue; if (k++ == idx) { istringstream ss(cl.substr(1)); int x; while (ss >> x && x) assumptions.push_back(x); break; } }
    for (int a : assumptions) S.assume(a);
  }
  if (argc > 12) S.limit("conflicts", -1), signal(SIGALRM, [](int){ exit(3); }), alarm(atoi(argv[12]));
  int r = S.solve();
  fflush(ext); fclose(ext);
  double secs = chrono::duration<double>(chrono::steady_clock::now() - t0).count();
  printf("{\"result\": \"%s\", \"secs\": %.2f, \"ext_clauses\": %ld, \"conflict_found\": %ld, \"unit_found\": %ld, \"model_checks\": %ld}\n",
         r == 20 ? "UNSAT" : (r == 10 ? "SAT" : "UNKNOWN"), secs, P.nclauses, P.nconf, P.nunit, P.nmodel);
  if (r == 10) { FILE *m = fopen((out + ".model").c_str(), "w"); fprintf(m, "v");
    for (int v = 1; v <= nbase; v++) fprintf(m, " %d", S.val(v) > 0 ? v : -v); fprintf(m, " 0\n"); fclose(m); }
  if (r == 20) { // final CNF = base + ext
    string cmd = "{ echo \"p cnf " + to_string(nv) + " " + to_string(ncl + P.nclauses) + "\"; grep -v '^[cp]' " + string(cnf) + "; cat " + out + ".ext; } > " + out + ".final.cnf";
    if (system(cmd.c_str()) != 0) fprintf(stderr, "failed writing final cnf\n"); }
  return 0;
}
