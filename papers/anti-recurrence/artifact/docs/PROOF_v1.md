# Anti-recurrence sequences: boundedness and automaticity (draft proof, 2026-10-09)

Status: a hand proof written by the bot. It is backed by exact computer checks (listed at the end) but has not been refereed.
Notation follows Fokkink–Joshi, "Anti-recurrence sequences", arXiv:2506.13337 / Integers 26 (2026) A24 (FJ).

## Setup
- a = (a_1..a_k), with k >= 2 and every a_j >= 1.
- tau = sum a_j, K = k*tau, kappa = K+1, A1 = sum_j j*a_j.
- (A_n), (B_n) are complementary, strictly increasing sequences in N = {1,2,...} with
  A_n = sum_j a_j B_{k(n-1)+j}.
- FJ Lemma 3: the pair (A, B) exists and is unique.
- FJ Lemma 2: A_{n+1} - A_n >= K.
- d(n) := A_n - kappa*n.

## Step 1 (counting identity)
For m >= 1, let c(m) = #{i : A_i < B_m}. Then B_m = m + c(m).

Since A is strictly increasing, exactly A_i - i of the B's are smaller than A_i. Hence
A_i < B_m  <=>  A_i - i <= m-1  <=>  K*i + d(i) <= m-1.

Every B in the n-th block lies below A_n (k >= 2). So A_n - n >= kn >= m_j, where m_j := k(n-1)+j. Also A_i - i is increasing in i. Hence indices i >= n are never counted in c(m_j).

Let n-1 = tau*q + r with 0 <= r < tau, and let u_j := k*r + j - 1. As (r, j) runs over all pairs, u_j takes every value in {0, ..., K-1} exactly once. Then m_j - 1 = K*q + u_j, and

    d(n) = A1 - K - n + sum_j a_j c(m_j),   c(m_j) = #{1 <= i < n : d(i) <= K(q-i) + u_j}.      (*)

## Step 2 (boundedness: the weak Clergyman conjecture, for every a)
Let Phi(r,x) = A1 - K - 1 - r + sum_j a_j floor((k r + j - 1 - x)/K).

Claim: suppose integers L <= U satisfy
- (i) Phi(r,L) <= U for all r,
- (ii) Phi(r,U) >= L for all r,
- (iii) U >= -k(tau-1),
- (iv) L <= 0.

Then L <= d(n) <= U for all n >= 1.

Proof, by strong induction on n (the n = 1 case is included):
- Upper bound. Since d(i) >= L for i < n, c(m_j) <= #{i >= 1 : K i + L <= m_j - 1} = floor((m_j-1-L)/K). This uses (iv).
- Lower bound. Since d(i) <= U for i < n, and by (iii) no i >= n satisfies K i + U <= m_j - 1, we get c(m_j) >= max(0, floor((m_j-1-U)/K)) >= floor((m_j-1-U)/K).
- Substituting floor((K q + u_j - x)/K) = q + floor((u_j - x)/K) and n = tau*q + r + 1 into (*) gives
  Phi(r,U) <= d(n) <= Phi(r,L). Conditions (i) and (ii) then finish the step.

Such a box always exists:
- Since sum_j a_j*k*r/K = r and sum_j a_j(j-1) = A1 - tau, we get
  c0 - x/k - tau < Phi(r,x) <= c0 - x/k, where c0 = A1 - K - 1 + (A1 - tau)/K.
- Because k >= 2, the map x -> c0 - x/k is a contraction. So taking L very negative and U = floor(c0 - L/k) satisfies (i)-(iv).
- Conclusion: **A_n - kappa*n is bounded for every positive linear form a.**
- The smallest such box usually equals the observed range exactly (boxproof.py; for a=(1,4) it is [-6,1]).

## Step 3 (automaticity: Conjecture 4 of FJ, for every a)
Let d be in [L,U]. Pick T >= 1 with K*T >= U, and T' with K*T' > K - 1 - L.

In (*), indices i <= q - T are always counted, and i >= q + T' never are. For q >= T this gives

    d(tau*q + r + 1) = G_r( d(q-T+1), ..., d(q+T'-1) )

where G_r(y) = A1 - K - 1 - r - tau*T + sum_j a_j sum_t [ y_t <= u_j - K t ]. This is a fixed finite "window recursion".

Window vectors:
- Let V(p) = (d(p+o), ..., d(p+o+W-1)), with o <= min(0, floor((-T)*tau/(tau-1))) and W large enough. Note tau >= 2.
- Then for all p >= P0 and 0 <= c < tau, V(tau*p + c) = H_c(V(p)) for fixed maps H_c on the finite set [L,U]^W.
- (Checking this only needs floor((o-1)/tau) - T + 1 >= o and floor((tau+o+W-3)/tau) + T' - 1 <= o + W - 1.)

Hence d(tau^e p + b) = pi(H_w(V(p))) for p >= P0, where w is the length-e base-tau word of b. So every tau-kernel sequence is determined by:
- a map from the finite set [L,U]^W to [L,U], and
- a prefix of length P0 with values in [L,U].

There are only finitely many such choices, so the kernel is finite and d is tau-automatic. Shifting the index and changing finitely many terms do not affect this.

**Hence A_n - kappa*n is tau-automatic for every positive integral linear form a of dimension k >= 2. This is FJ Conjecture 4, the "Clergyman's conjecture".**

## The 4-rusty numbers a = (1,4) explicitly
- tau = 5, kappa = 11, d(n) = A_n - 11n.
- Box [-6,1]: proved, and attained.
- Recursion (q >= 1, j = 0..4, with d(1..4) = -2,-3,-4,-5):
  d(5q+j) = -j-6 + [d(q) <= 2j-2] + 4[d(q) <= 2j-1] + [d(q+1) <= 2j-12] + 4[d(q+1) <= 2j-11].
- Minimal msd-first 5-DFAO for d(n): 17 states. It is in dfao_min.json and RUS.txt (Walnut word automaton, output d+6).
- Corollary: A_{5q+1} = 9 + 55q  <=>  d(q) != 1. The first q with d(q) = 1 is q = 348, which explains FJ's observation about A_1741.
- Independent Walnut v7.1.0 verification (walnut_rusty*.txt / *.log) shows that the sequences defined from the DFAO satisfy all of the following:
  - A(1) = 9, B1(1) = 1, B2(1) = 2;
  - A is strictly increasing;
  - B1(n) < B2(n) < B1(n+1);
  - A and B are disjoint and together cover N;
  - A = B1 + 4*B2.
  By uniqueness (FJ Lemma 3), these are the rusty numbers. Every query returned TRUE, and the control queries returned FALSE as expected.

## Computer checks (all in /workspace/research2/rusty)
- gen.py: 10^7 terms of the (1,4) sequence; d in [-6,1].
- recur_check.py: the (1,4) recursion holds for all n <= 10^7 (0 mismatches).
- dfao.py: the 17-state DFAO agrees with 400k sampled terms.
- general.py: the window identity holds with 0 mismatches for 24 forms (3*10^5 terms each).
- cert.py: closure certificates for 20+ forms.
- boxproof.py: the explicit proved box contains the observed range for 40 forms (16 chosen + 24 random, k <= 5, entries <= 9; 10^5 terms each).

## What this establishes vs what Fokkink–Joshi (FJ) already proved (added 2026-10-09, 19:40 PT)

What FJ already proved:
- Conjecture 4 for A1-bounded forms (A1 <= (k-1)tau+2; Thm 12). For k=2 this means exactly the forms with a2 <= 2.
- The anti-k-bonaccis (Thm 8).
- (1,2), (2,1) and the 4-DFAO for (1,3), via Walnut.
- Earlier work: Zaslavsky for (1,1); Bosma et al. for (1,1,1) and (1,1,1,1).
- FJ explicitly leave the rusty numbers (1,d), d >= 4, and the general case open.

What is new here:
1. Rusty a=(1,4): A_n - 11n is 5-automatic, with values in [-6,1] and a 17-state msd DFAO.
   - Walnut v7.1.0 proves this outright (characterisation via FJ Lemma 3). It does not depend on Steps 1-3.
   - Steps 1-3 give a second, independent hand proof.
   - Status: proved (computer-verified).
2. Also proved via Walnut, again without relying on Steps 1-3:
   - (1,5): 19 states, values in [-7,1].
   - (2,7): 37 states, values in [-12,3].
   - (1,1,5): 24 states, values in [-9,-1]. Here the identity A = B1+B2+5B3 holds by construction of the B-definitions; that query alone exceeded the 400 MB heap and was replaced by this hand identity. All other queries were TRUE.
   - None of these forms is A1-bounded.
   - Automata come from the Step-3 closure construction, not from guessing (walnut_forms.py). Scripts and logs: walnut_forms_all.txt/.log, walnut_RQF_rest.txt/.log.
3. General theorem (Steps 1-3): for EVERY positive integral linear form, A_n - kappa*n is bounded (explicit box) and tau-automatic. This would settle FJ Conjecture 4 / Conjecture 1 for linear anti-recurrences.
   - Status: hand proof, a few pages long, not refereed. Every step was re-checked by exact computation (recheck.py, recheck_60000.log) on 50 forms, 20 of them not A1-bounded, with 6*10^4 terms each and 0 failures:
     - (a) identity (*) and B_m = m + c(m), computed from the raw sequences;
     - (b) the explicit-recipe box satisfies (i)-(iv), and Phi(r,U) <= d(n) <= Phi(r,L) holds pointwise;
     - (c) the window recursion holds.
   - Computation cannot prove the general statement. Step 2 is a short induction, and Step 3 is the standard "finite-state window recursion => finite kernel" argument. A human should re-derive both before submission.
