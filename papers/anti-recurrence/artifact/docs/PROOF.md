# Linear anti-recurrence sequences: boundedness and automaticity (proof, v2.1, 2026-10-09)

Status: v2 is a hand proof revised after an internal adversarial review by a separate AI agent (review/REVIEW.md; not peer review), which judged v1 sound as mathematics with expository gaps. Every step is backed by exact computer checks (listed at the end). v1 is kept unchanged as PROOF_v1.md. v2.1 applies the text fixes of the second review pass (review/REVIEW2.md), which judged all of v2's mathematics sound; v2.0 is kept as v2/PROOF_v2.0_before_r2fixes.md.

Notation follows Fokkink–Joshi (FJ): "Anti-recurrence sequences", arXiv:2506.13337v1 (2025), published as Integers 26 (2026), #A24. Theorem and conjecture numbers differ between the two versions, so both are given:
- Precise conjecture: Conj. 4 in arXiv v1, Conj. 2 in Integers.
- Meta-conjecture: Conj. 1 in both.
- Anti-k-bonacci theorem: Thm 8 in arXiv v1, Thm 3 in Integers.
- A1-bounded theorem: Thm 12 in arXiv v1, Thm 4 in Integers.
- Uniqueness: Lemma 3 in arXiv v1, Lemma 2 in Integers.
- Gap bound: Lemma 2 in arXiv v1, Lemma 1 in Integers.

## Changes in v2.1 (second review pass, review/REVIEW2.md)
1. Theorem 6 bound improved to 1 + (K + tau - k + 1)^3: V(1) = (0, d(1), d(2)) lies in [-K, tau-k]^3 because d(0) = 0 and tau >= k. The v2.0 bound 2 + (...)^3 was true but not needed.
2. Remarks after Lemma 4 corrected. (L*, U*) can exceed the narrowest box by 2 units, not "at most one". Lemma 4 bounds the range of d, not "the smallest box". Added sharpness data and a conjecture that the narrowest box equals the exact range.
3. Automaton size conventions stated, and FJ-convention sizes added.
4. (1,3): FJ's "4-DFAO" means base 4. Their Fig. 7 automaton has 6 states.
5. FJ lemma numbers given for both versions. "Referee" checks are described as an independently written second implementation (an AI agent), not peer review.
6. Added the second-pass checks: 2270 forms, (1,1,5) B-B disjointness in Walnut, and exact ranges.

## Changes from v1
1. Step 1 now defines c(m_j) over all i >= 1, with no i < n restriction. The fact that indices i >= n are never counted is now a separate Lemma 1(b), and it is used only in Step 2.
2. Step 2: the existence of a box now checks condition (ii) explicitly and gives an explicit (L*, U*).
3. New Lemma 4 (proved): the box [-K, U*] with U* = max(-k(tau-1), max_r Phi(r,-K)) <= tau-k always satisfies (i)-(iv). Hence -K <= d(n) <= tau-k for every form. This proves the referee's "optional lemma" in a slightly different form (upper end tau-k rather than K/3).
4. New Theorem 5: a universal two-term recursion d(tau q+r+1) = G_r(d(q), d(q+1)) for all q >= 0, with d(0) := 0.
5. Step 3 is rewritten. It gives an explicit msd-first tau-DFAO with states {start, V(1)} ∪ [-K,U*]^3, so at most 2+(K+U*+1)^3 states. The digit order is explicit. The general window argument is also stated, with explicit o, W, P0 and with o <= 0 <= o+W-1. The k-kernel route cites Allouche–Shallit, Automatic Sequences (2003), Thm 6.6.2. Shift-invariance is no longer needed, because d is handled on n >= 0 directly with d(0) := 0.
6. The FJ comparison section is corrected:
   - version-specific numbering;
   - FJ do not give Walnut queries for (1,3); they only state that their method applies;
   - (1,3) is not A1-bounded;
   - the inconsistent timestamp is removed (v1 said "added 19:40 PT", but the file was last written at 19:19 PT).
7. Added a prior-art summary (see priorart/ and the paper).

## Setup
- a = (a_1, ..., a_k), with k >= 2 and every a_j >= 1 an integer.
- tau = sum_j a_j and K = k*tau. Since k >= 2 and tau >= k, we have tau >= 2.
- kappa = K+1 and A1 = sum_j j*a_j.
- (A_n)_{n>=1} and (B_m)_{m>=1} are complementary, strictly increasing sequences in N = {1,2,...} with A_n = sum_j a_j B_{k(n-1)+j}. FJ Lemma 3 (arXiv v1) = Lemma 2 (Integers): such a pair exists and is unique.
- d(n) := A_n - kappa*n for n >= 1. Set d(0) := 0, which matches the convention A_0 = 0.
- Two facts used below:
  - tau <= A1 <= K-(k-1). The upper bound holds because K - A1 = sum_j (k-j) a_j >= sum_{j<k} (k-j) >= k-1.
  - The first block gives A_1 = sum_j j a_j = A1 (B_j = j for j <= k), so d(1) = A1 - K - 1.

## Step 1 (counting identity)
**Lemma 1.** For m >= 1, let c(m) := #{i >= 1 : A_i < B_m}.
- (a) B_m = m + c(m), and A_i < B_m <=> K*i + d(i) <= m-1.
- (b) Let n >= 1 and m_j := k(n-1)+j for 1 <= j <= k. No index i >= n satisfies A_i < B_{m_j}.
- (c) Write n-1 = tau*q + r with 0 <= r < tau, and set u_j := k*r + j - 1, which lies in [0, K-1]. Then m_j - 1 = K*q + u_j, and

      d(n) = A1 - K - n + sum_j a_j c(m_j),   where   c(m_j) = #{ i >= 1 : d(i) <= K(q-i) + u_j }.      (*)

*Proof.*
- (a) Every integer below B_m is either some B_{m'} with m' < m or some A_i < B_m. Since A_i is strictly increasing, exactly A_i - i of the B's lie below A_i. So A_i < B_m <=> A_i - i <= m-1, and A_i - i = K*i + d(i).
- (b) A_n = sum_j a_j B_{m_j} >= B_{kn} + B_{kn-1} > B_{kn}, because k >= 2 and a_j >= 1. So at least kn of the B's lie below A_n, which gives A_n - n >= kn >= m_j > m_j - 1. The quantity A_i - i is strictly increasing in i (FJ Lemma 2 (arXiv v1) = Lemma 1 (Integers) gives A_{i+1} - A_i >= K >= 4 > 1). So for i >= n, A_i - i > m_j - 1, and by (a) these i are not counted.
- (c) A_n = sum_j a_j (m_j + c(m_j)), and sum_j a_j m_j = K(n-1) + A1. Subtracting kappa*n gives the formula. The description of c(m_j) is (a) with m - 1 = Kq + u_j. []

## Step 2 (boundedness: the weak form of the conjecture, for every a)
Let Phi(r,x) := A1 - K - 1 - r + sum_j a_j floor((k r + j - 1 - x)/K), for 0 <= r < tau and integer x.

**Proposition 2 (box criterion).** Suppose integers L <= U satisfy
- (i) Phi(r,L) <= U for all r,
- (ii) Phi(r,U) >= L for all r,
- (iii) U >= -k(tau-1),
- (iv) L <= 0.

Then L <= d(n) <= U for all n >= 1.

*Proof.* Strong induction on n; the case n = 1 is included, with an empty hypothesis. Let n = tau q + r + 1. By Lemma 1(b), c(m_j) = #{1 <= i < n : d(i) <= Kq + u_j - K i}.
- Upper bound. Use d(i) >= L for i < n. Then c(m_j) <= #{i >= 1 : K i <= Kq + u_j - L}. By (iv), Kq + u_j - L >= 0, so this count equals floor((Kq + u_j - L)/K) = q + floor((u_j - L)/K).
- Lower bound. Use d(i) <= U for i < n. Every i >= 1 with K i <= Kq + u_j - U is counted, as long as i < n. Such i satisfy i <= q + floor((u_j - U)/K).
  - By (iii), u_j - U <= (K-1) + K - k < 2K, so i <= q + 1.
  - If q >= 1, then q + 1 <= tau q < n. If q = 0 and r >= 1, then i <= 1 < n.
  - If q = r = 0 (so n = 1), then u_j <= k-1 and u_j - U <= k-1+k(tau-1) = K-1 < K, so no i >= 1 qualifies.
  - In all cases c(m_j) >= max(0, q + floor((u_j - U)/K)) >= q + floor((u_j - U)/K).
- Substitute into (*) with n = tau q + r + 1 and sum_j a_j q = tau q. This gives Phi(r,U) <= d(n) <= Phi(r,L). Then (i) and (ii) finish the step. []

**Proposition 3 (some box exists; explicit).** Let c0 := A1 - K - 1 + (A1 - tau)/K.
- Bounds on Phi. Note sum_j a_j (k r)/K = r and sum_j a_j (j-1) = A1 - tau. Using y - 1 < floor(y) <= y, summed with weights a_j, gives for all r and x:

      c0 - x/k - tau  <  Phi(r,x)  <=  c0 - x/k.        (**)

- The box. Let L be an integer and U := floor(c0 - L/k).
  - (i): Phi(r,L) <= c0 - L/k, and Phi is an integer, so Phi(r,L) <= U.
  - (ii): Phi(r,U) > c0 - U/k - tau >= c0 - (c0 - L/k)/k - tau = c0(1-1/k) + L/k^2 - tau. Since Phi is an integer, Phi(r,U) >= L holds as soon as c0(1-1/k) + L/k^2 - tau >= L - 1, that is, as soon as L(1-1/k^2) <= c0(1-1/k) - tau + 1.
  - (iii): U > c0 - L/k - 1, so (iii) holds once L <= k(c0-1) + k^2(tau-1).
  - U >= L holds once L <= k(c0-1)/(k+1).
  - (iv): needs L <= 0.
- Therefore

      L* := min{ 0, floor((c0(1-1/k) - tau + 1)/(1-1/k^2)), floor(k(c0-1) + k^2(tau-1)), floor(k(c0-1)/(k+1)) },   U* := floor(c0 - L*/k)

  satisfy (i)-(iv). **Hence A_n - kappa n is bounded for every positive integral linear form a.** []

**Lemma 4 (a universal box).** Let L = -K and U := max(-k(tau-1), max_r Phi(r,-K)). Then (i)-(iv) hold and U <= tau - k. Consequently, for every form,

    -K <= d(n) <= tau - k   for all n >= 1.

*Proof.*
- (i), (iii) and (iv) hold by definition, and L = -K < -K + k = -k(tau-1) <= U.
- U <= tau - k. By (**), Phi(r,-K) <= c0 + tau < A1 - K - 1 + tau + 1 <= tau - k + 1, using (A1-tau)/K < 1 and A1 <= K-k+1. Since Phi is an integer, Phi(r,-K) <= tau - k. Also -k(tau-1) <= 0 <= tau - k.
- (ii) We need Phi(r,U) >= -K. By (**), Phi(r,U) > c0 - U/k - tau. Recall c0 >= tau - K - 1, because A1 >= tau.
  - Case U = max_r Phi(r,-K). Then U <= c0 + tau, so Phi(r,U) > c0(1-1/k) - tau(1+1/k) >= (tau-K-1)(1-1/k) - tau(1+1/k) = -K - 1 + tau(1-2/k) + 1/k > -K - 1.
  - Case U = -k(tau-1). Then Phi(r,U) > c0 + (tau-1) - tau = c0 - 1 >= tau - K - 2 >= -K - 1.
  - In both cases Phi(r,U) is an integer > -K-1, so Phi(r,U) >= -K. []

Remarks (v2.1; data in v2/r2checks_named.log, v2/r2checks_sweep.log, review/r2/sweep2.log).
- Narrowest box. For fixed L <= 0 the least admissible U is max(-k(tau-1), max_r Phi(r,L)), so a narrowest box satisfying (i)-(iv) is found by a one-dimensional search over L (recheck.min_box). Every valid box contains the range of d.
- Exact ranges must come from the automaton (the output values of the reachable states of the Theorem 6 DFAO), not from finite prefixes. For example, (200,1) has exact min -400 but stays above -370 for the first 3*10^6 terms (review/r2/big.log).
- On the 10 named forms and on 736 further forms (all k=2 forms with a_j <= 20, all k=3 forms with a_j <= 6, and 120 random forms with k=4..6, a_j <= 12), the narrowest box equals the exact range. The independent second implementation found the same on 1682/1682 forms. For (1,4) both are [-6,1].
  - **Conjecture.** The narrowest box satisfying (i)-(iv) is always exactly [min d, max d].
- (L*, U*) is NOT always within one unit of the narrowest box. Over the 736-form sweep, its total-width excess is 0, 1 or 2 for 49, 277 and 410 forms respectively, and never more than 2. Example: (1,2) has (L*, U*) = [-4,0] but exact range [-3,-1].
- Sharpness of Lemma 4. Lemma 4 bounds the range of d. The lower end is within 2 of optimal: in every tested form min d >= -K+2, with equality exactly for (a,1), 1 <= a <= 20, in our sweep (the second implementation reports 36 such forms on its larger set). We have not proved d >= -K+2. The upper end tau - k is loose; the second implementation found max d <= 0.66(tau-k) on all its forms.
- The upper end tau - k is <= K/3 when k >= 3, and when k = 2 with tau <= 6. This answers the referee's earlier empirical [-K, K/3] for those forms. A K/3 upper bound for all k = 2 forms is not proved and is not needed.

## Step 3 (automaticity: FJ arXiv Conj. 4 = Integers Conj. 2, for every a)
**Theorem 5 (two-term recursion).** For 0 <= r < tau and y0, y1 in Z, put

    G_r(y0, y1) := A1 - K - 1 - r - tau + sum_{j=1}^{k} a_j ( [y0 <= k r + j - 1] + [y1 <= k r + j - 1 - K] ).

Then for all q >= 0 and 0 <= r < tau (with d(0) = 0):

    d(tau q + r + 1) = G_r( d(q), d(q+1) ).

*Proof.* Use (*) with n = tau q + r + 1 and write i = q - t.
- Indices i <= q - 1 (t >= 1) are always counted, since d(i) <= tau - k < K <= K t + u_j by Lemma 4.
- Indices i >= q + 2 are never counted, since K(q-i) + u_j <= -2K + K - 1 = -K - 1 < -K <= d(i) by Lemma 4.
- Hence for q >= 1, c(m_j) = (q-1) + [d(q) <= u_j] + [d(q+1) <= u_j - K].
- For q = 0, c(m_j) = [d(1) <= u_j - K]. This is the same formula, because d(0) = 0 <= u_j makes [d(0) <= u_j] = 1.
- Substitute into (*) and use sum_j a_j (q-1) = tau q - tau. []

**Theorem 6 (automaticity, explicit DFAO).** The sequence (d(n))_{n>=0} is tau-automatic. An msd-first tau-DFAO for it has at most 1 + (K + max(U,0) + 1)^3 <= 1 + (K + tau - k + 1)^3 states. Hence A_n - kappa n (n >= 1) is tau-automatic for every positive integral linear form a of dimension k >= 2.

*Proof.* For m >= 1, let V(m) := (d(m-1), d(m), d(m+1)). For m >= 2 it lies in [-K,U]^3 by Lemma 4. V(1) = (0, d(1), d(2)) lies in [-K, max(U,0)]^3, because d(0) = 0 (U itself can be negative). Since max(U,0) <= tau - k, every V(m) lies in [-K, tau-k]^3. Fix a digit 0 <= c < tau.
- Each coordinate of V(tau m + c) is d(tau m + c + e) with e in {-1, 0, 1}. Write tau m + c + e = tau q' + r' + 1.
  - If c + e - 1 >= 0, then q' = m and r' = c + e - 1.
  - If c + e - 1 in {-2, -1}, then q' = m - 1 and r' = tau + c + e - 1, which lies in [0, tau-1] because tau >= 2.
- By Theorem 5 (q' >= 0 because m >= 1), each coordinate equals G_{r'} applied to two consecutive entries of V(m). So V(tau m + c) = H_c(V(m)) for a fixed map H_c: Z^3 -> Z^3 that depends only on c (and a).
- Build the DFAO as follows.
  - States: a start state S, plus all vectors V(m) for m >= 1.
  - Transitions: S --0--> S (leading zeros); S --c--> V(c) for 1 <= c < tau; V --c--> H_c(V).
  - Outputs: S outputs d(0) = 0, and V outputs its middle coordinate.
- Read n = (c_{e-1} ... c_1 c_0)_tau most significant digit first. Since V(tau m + c) = H_c(V(m)) for m >= 1, induction on the length of the representation shows that the DFAO ends in state V(n) for n >= 1 (and in S for n = 0). So it outputs d(n).
- The set of states lies in {S} ∪ [-K, max(U,0)]^3, which is finite.
- Shift: the sequence n -> A_n - kappa n on n >= 1 is the restriction of this automatic sequence. Equivalently, the same DFAO computes it, so no shift lemma is needed. []

*Alternative (kernel) formulation, general window.* The argument does not need Lemma 4 specifically. Take any valid box [L,U]. Let T := max(1, ceil(U/K)), and let T' be the least integer with K T' > K - 1 - L. Then (*) gives, for q >= T,

    d(tau q + r + 1) = A1 - K - 1 - r - tau T + sum_j a_j sum_{t=-T+1}^{T'-1} [ d(q+t) <= u_j - K t ].

- Set o := -2T, W := 2T + 2T' + 1 and P0 := 2T + 1. Then o <= 0 <= o + W - 1.
- Containment conditions: floor((o-1)/tau) - T + 1 >= o and floor((tau + o + W - 3)/tau) + T' - 1 <= o + W - 1. Both hold for every tau >= 2: ceil((2T+1)/tau) <= T+1, and floor((2T' + tau - 2)/tau) <= T'.
- Also p + o >= 1 and p + floor((o-1)/tau) >= T for p >= P0.
- So, with V(p) := (d(p+o), ..., d(p+o+W-1)), we get V(tau p + c) = H_c(V(p)) for p >= P0, for fixed maps H_c on [L,U]^W.
- Iterating: for b = sum_{i<e} c_i tau^i (digits c_0 least significant),

      V(tau^e p + b) = H_{c_0} ∘ H_{c_1} ∘ ... ∘ H_{c_{e-1}} ( V(p) )   for p >= P0.

- Hence the kernel sequence p -> d(tau^e p + b) is determined by two pieces of data, of which there are finitely many choices:
  - the map pi ∘ H_{c_0} ∘ ... ∘ H_{c_{e-1}} : [L,U]^W -> [L,U], where pi is the coordinate at offset 0 (index -o);
  - its first P0 values, which lie in [L,U] ∪ {d(0)}.
- So the tau-kernel is finite, and d is tau-automatic by Allouche–Shallit, Automatic Sequences (CUP 2003), Theorem 6.6.2 (a sequence is k-automatic iff its k-kernel is finite). That theorem number is checked against several independent secondary citations, not against the book itself.
- With the universal box of Lemma 4, T = 1 and T' = 2. This reduces to Theorem 5, with o = -2, W = 7, P0 = 3, or with the tighter (o, W, P0) = (-1, 3, 1) used in Theorem 6.

## The 4-rusty numbers a = (1,4) explicitly
- tau = 5, K = 10, kappa = 11, A1 = 9, d(n) = A_n - 11n.
- Box [-6,1]: proved by Proposition 2 and attained. The Lemma 4 box is [-10,3].
- Theorem 5 specializes to the following, for q >= 0 and j = 1..5 (n = 5q + j), with d(0) = 0:
  d(5q+j) = -j-6 + [d(q) <= 2j-2] + 4[d(q) <= 2j-1] + [d(q+1) <= 2j-12] + 4[d(q+1) <= 2j-11].
  - This is the v1 recursion. In v1 it was stated for q >= 1 with d(1..4) = -2,-3,-4,-5 given; with d(0) = 0 the case q = 0 reproduces those values.
- Minimal msd-first 5-DFAO for d(n) (output d+6 in RUS.txt): 17 states, in dfao_min.json and RUS.txt.
  - Convention for all sizes here: input n >= 0 in base tau, msd first, leading zeros allowed, output d(n) with d(0) = 0.
  - FJ convention: input n-1, i.e. s(m) = d(m+1) up to a constant (FJ Integers Fig. 7 outputs A_n - 9n - 4 with A indexed from 0). The automaton is the Theorem 6 DFAO with S outputting d(1) and each triple outputting its last coordinate.
  - Minimal sizes (ours / FJ convention), from v2/r2checks_named.log: (1,4) 17/9, (1,5) 19/11, (2,7) 37/20, (1,1,5) 24/9, (1,3) 13/6, (1,1) 3/2, (1,2) 5/3, (2,1) 10/4, (1,1,1) 7/3, (1,1,1,1) 10/4. The FJ-convention (1,3) size 6 matches FJ's 6-state Fig. 7.
  - The Theorem 6 construction (v2/twoterm.py) gives 28 states, which minimise to 17.
- Corollary: A_{5q+1} = 9 + 55q <=> d(q) != 1 (q >= 1). The first q with d(q) = 1 is q = 348, which explains FJ's observation that A_1741 != 9 + 55*348.
- Independent Walnut v7.1.0 verification (walnut_rusty*.txt / *.log; re-done with a separately written query set in review/walnut_ref14.*): the sequences defined from the DFAO satisfy
  - A(1) = 9, B1(1) = 1, B2(1) = 2;
  - A strictly increasing;
  - B1(n) < B2(n) < B1(n+1);
  - A and B disjoint, with A ∪ B = N;
  - A = B1 + 4*B2.
  By uniqueness (FJ arXiv Lemma 3 = Integers Lemma 2) these are the rusty numbers. Every query is TRUE, and the control queries are FALSE.
  This Walnut proof does not depend on Steps 1-3.

## Computer checks (all in /workspace/research2/rusty)
- gen.py: 10^7 terms of (1,4); d in [-6,1]. recur_check.py: the (1,4) recursion holds for n <= 10^7.
- dfao.py: the 17-state DFAO agrees with 400k sampled terms; the second implementation checked all n <= 2*10^6.
- general.py, cert.py, boxproof.py: window identity, closure certificates, and explicit boxes (v1).
- recheck.py / recheck_60000.log: exact re-check of (*), B_m = m + c(m), box (i)-(iv) with pointwise Phi bounds, and the window recursion. 50 forms (20 not A1-bounded), 6*10^4 terms each, 0 failures.
- review/ (an independently written second implementation by a separate AI agent; a check against implementation errors, not peer review):
  - arseq.c: separately written C generator.
  - sweep.py / sweep.log: 585 forms (178 not A1-bounded), up to 1e5 terms; growth.log: 2e6 terms for 8 forms. 0 failures.
  - closure.py: independent DFAO construction, matching the Walnut automata state counts exactly.
- v2 (new, for this revision):
  - v2/verify_v2.py / verify_v2_20000.log: the explicit (L*, U*) of Prop. 3 and the minimal box both satisfy (i)-(iv) and contain d. With the explicit T, T', o, W, P0 of the kernel formulation, the containment inequalities hold and V(tau p + c) = H_c(V(p)) holds for every p in range. 17 forms, 2*10^4 terms, about 1.4*10^5 coordinate checks per box per form, 0 failures.
  - v2/twoterm.py:
    - twoterm_sweep_6000.log: Lemma 4 box + bound U <= tau - k + Theorem 5 recursion (all q >= 0, d(0) = 0) on 433 forms (all k=2 with a_j <= 12, all k=3 with a_j <= 5, 150 random k=3..5 with a_j <= 12, plus extremes), 6000 terms each, 0 failures.
    - twoterm_named.log: the Theorem 6 DFAO reproduces d(0..2*10^4) exactly for 12 named forms. Minimised state counts: (1,4) 17, (1,5) 19, (2,7) 37, (1,1,5) 24, identical to the Walnut-verified automata.
  - v2/r2checks.py (v2.1): exact ranges from the reachable states, narrowest box vs (L*, U*), V(1) in the box, minimal sizes in both conventions. r2checks_named.log covers 10 named forms; r2checks_sweep.log covers 736 forms: narrowest box = exact range 736/736, all triples in [-K,tau-k]^3 736/736, excess {0:49, 1:277, 2:410}, min(exact min + K) = 2 for 20 forms.
  - v2/zaslavsky_check.py: anti-Fibonacci A_n = 5n-2+PD_{n-1} for n <= 3000. It also shows that Zaslavsky's Thm 1, read literally with his definition of "utterly odd", has the two odd cases interchanged: the literal reading fails at every odd index, while the swapped reading has 0 failures.
- review/r2/ (second pass of the second implementation):
  - arseq2.c / sweep2.py / sweep2.log: 2270 forms (k=2..8, entries up to 200, tau up to 1600). Lemma 4, Theorem 5, H_c maps and closure-in-box are checked, with 0 failures.
  - big.log: 3*10^6 terms for 7 large forms.
  - prop33.py: exact rational check of (L*, U*), o, W, P0 on 1420 forms.
  - closure.py, closure_shift.py.
  - walnut_rqf_disjB.txt / .log: (1,1,5) pairwise B-B disjointness q_disj12/13/23, all TRUE. Also implied by the interleaving query RQF_incB.

## What this establishes vs what FJ already proved
What FJ proved, cited by version:
- Precise conjecture (arXiv v1 Conj. 4 = Integers Conj. 2) for A1-bounded forms, A1 <= (k-1)tau + 2 (arXiv v1 Thm 12 = Integers Thm 4). For k = 2 these are exactly the forms with a_2 <= 2.
- Anti-k-bonaccis, for all k (arXiv v1 Thm 8 = Integers Thm 3).
- Anti-Pell a = (1,2) and anti-Jacobsthal a = (2,1): full Walnut proofs, with queries shown. Both forms are A1-bounded.
- a = (1,3) (3-rusty): FJ show a guessed 4-DFAO, i.e. base 4 with 6 states (Integers Fig. 7), and state that their Walnut verification "can also be applied", but no queries are shown. (1,3) is NOT A1-bounded (A1 = 7 > 6). So FJ assert (1,3) but do not give a complete proof in the paper. The general theorem here covers it.
- Earlier work on (1,1): the sequence is OEIS A075326, entered by A. Murthy (2002); Lallouet gave the mex definition (2008) and Hofstadter named it (2014). Zaslavsky (unpublished note, 2016, Thm 1, stated with "utterly odd" numbers) gave the formula; its PD form is FJ arXiv eq. (2), and Bosma et al. §3 verify it in Walnut. Also Bosma et al. (arXiv:2503.04122 = J. Integer Seq. 28 (2025) 25.3.8) for (1,1,1) and (1,1,1,1).
- FJ explicitly leave open the general case and the rusty numbers (1,d) with d >= 4 (Integers §6 "Final Remarks"; arXiv v1 likewise).

What is new here:
1. a = (1,4): A_n - 11n is 5-automatic with values in [-6,1] and a 17-state msd DFAO (9 states in the FJ convention). Walnut proof, independent of Steps 1-3; a separately written query set gives the same verdicts.
2. a = (1,5), (2,7), (1,1,5): Walnut proofs.
   - State counts and value ranges: (1,5) 19 states, [-7,1]; (2,7) 37 states, [-12,3]; (1,1,5) 24 states, [-9,-1].
   - The (1,1,5) linear-relation query originally ran out of heap. It was closed with a reformulated Walnut query (review/walnut_ref115.*: TRUE). B-B disjointness for (1,1,5) was also run directly (review/r2/walnut_rqf_disjB.*: 3x TRUE).
   - None of these forms is A1-bounded.
3. General theorem (Steps 1-3):
   - For every positive integral linear form, -K <= A_n - kappa n <= tau - k.
   - d satisfies the two-term recursion of Theorem 5.
   - d is tau-automatic, with an explicit DFAO of at most 1 + (K + tau - k + 1)^3 states.
   - This proves FJ's precise conjecture (arXiv v1 Conj. 4 = Integers Conj. 2) and its weak (boundedness) form, for all positive integral linear forms.
   - Status: hand proof plus exact computational checks. Two internal review passes, both by AI agents (on v1 and on v2), found it sound. No human peer review yet. The author must personally read the proof.

## Prior art (checked 2026-10-09; details in paper §8 and priorart/)
No source found states or proves boundedness or automaticity for general linear forms. Checked:
- Kimberling–Moses, Fib. Quart. 57(5) (2019): conjectures and limit theorems only.
- Bosma et al. 2025: k = 2, 3, 4 anti-k-naccis; states the Clergyman's Conjecture.
- FJ arXiv v1 and Integers versions: A1-bounded only; general case stated as open.
- Semantic Scholar: 0 citing papers for FJ. 5 papers cite Bosma et al.; none is on anti-recurrences, apart from FJ itself.
- OpenAlex: both FJ records cited_by = 0.
- arXiv phrase searches ("anti-recurrence sequences", "anti-Fibonacci", "anti-k-nacci", "Clergyman", ...): no new relevant paper.
- OEIS A075326, A249031, A249032, A265389, A299409, A304499, A304502: bounds stated as conjectures, or proved only for specific forms. The 3- and 4-rusty sequences are not in the OEIS (term searches return "No results").
- MSE 5090531: a 2025 answer derives a residue corollary from FJ Thm 8 (anti-bonacci only).
- Kimberling JIS 2007 and 2008 complementary-equation surveys: different equation families (b(n) = a(jn) ± r, etc.).
- Not checked: Google Scholar (bot-blocked), and paywalled Fraenkel 1982.

Verdict: novel as far as can be determined.
