# Referee review of rusty/PROOF.md and Walnut claims (2026-10-09, ~20:00 PT)

> **Erratum (added 2026-10-09, after the second review pass; see docs/REVIEW2.md).** The `tight=1/0` flag in logs/sweep.log
> (tight=1 for 415 of the 585 forms) compares the minimal box (i)-(iv) with the range *observed on a finite prefix* (`obs=[..]`).
> This is unreliable: extreme values of d can first appear very late. For example, (200,1) has exact min -400 but stays above -370 for
> the first 3*10^6 terms (logs/big.log). So the "tight 415/585" statistic should not be used. Using exact ranges (the outputs of the
> reachable states of the Theorem C automaton) instead, the minimal box equals the exact range in 1682/1682 forms (second implementation,
> logs/sweep2.log, `exact=[..]`) and in 736/736 + 10 named forms (code/r2checks.py, logs/r2checks_*.log). The "[-K, K/3]" observation
> in item 4 below is likewise prefix-based; Lemma 3.4 of the paper proves -K <= d <= tau-k. The report text below is otherwise unchanged.
> The "referee" of this report is an AI agent that wrote a separate implementation; it is not peer review.

## Verdict
- (1) (1,4) 17-state 5-DFAO, Walnut: SOUND. Re-ran an independently written query set (walnut_ref14.txt/.log): 10/10 TRUE, 2 controls FALSE.
  Queries + FJ Lemma 3 uniqueness (re-proved below) pin the sequence down. RUS agrees with an independent C generator for n<=2e6;
  independent closure construction (closure.py) gives a minimal 17-state DFAO equivalent to RUS.
- (2) (1,5),(2,7),(1,1,5): SOUND after one fix. Original run had RQF_lin OOM; replaced by hand identity (valid: per-case arithmetic,
  7t=s+3/4/5 residues distinct). Now Walnut-checked via reformulation (walnut_ref115.txt/.log: q_lin TRUE, q_lin_tot TRUE, 24 s, -Xmx400m).
  Full re-run of walnut_forms_all minus RQF_lin reproduced every TRUE/FALSE (walnut_forms_rerun.log, 658 s).
  Independent closure automata match RFV(19), RTS(37), RQF(24) states exactly.
- (3) general hand proof: SOUND as mathematics; I could not break it. Gaps are expository only (see list).
  No counterexample on 585 forms (sweep.log; all k=2 with a_j<=12, all k=3 with a_j<=6, 25 adversarial, 200 random k=3..5 a_j<=12;
  178 of them not A1-bounded), up to 1e5 terms (2e6 for 8 forms): identity (*), B_m=m+c(m), box (i)-(iv) & pointwise Phi bounds,
  window recursion, window-map determinism: 0 failures.

## Precise statement of FJ
- arXiv v1 numbering: Conjecture 1 (meta), Conjecture 4 (precise: A_n - kappa n is tau-automatic, kappa=k tau+1). Theorem 12 (A1-bounded),
  Theorem 8 (anti-k-bonacci). Integers 26 A24 renumbers: precise conjecture is "Conjecture 2", anti-bonacci "Theorem 3" (per published PDF text).
  Cite by version.
- "tau-automatic" is the right base. Automatic => finite range, so bounded is implied; FJ explicitly call boundedness the "weak form" and
  do not prove it in general. For (1,3) FJ only assert their Walnut check applies (no queries shown).

## Line-by-line notes on PROOF.md
All inequalities re-derived; correct. Fixable/expository items:
1. Step 2 existence: "contraction" sentence skips (ii). Write: with U=floor(c0-L/k), Phi(r,U) > c0(1-1/k)+L/k^2-tau, so (ii) holds once
   L(1-1/k^2) <= c0(1-1/k)-tau+1; (iii) and U>=L hold for L very negative.
2. Step 3: state c(m_j)=#{i>=1: d(i)<=K(q-i)+u_j} (drop i<n, justified by Step 1), else window indices >= n look unjustified for small q.
3. Step 3: specify W and P0 explicitly; require o<=0<=o+W-1 so pi is defined; specify digit order in H_w; cite the k-kernel theorem
   (Allouche-Shallit Thm 6.6.2) and shift-invariance of automaticity.
4. Observed (not needed, worth a lemma): minimal box always lies in [-K, K/3] in tests (worst L=-K+2 for (a,1)), so T=1,T'=2 and
   d(tau q+r+1)=G_r(d(q),d(q+1)) universally, giving DFAO size <= (U-L+1)^3+O(1). Needs a proof (k=2 is borderline).
5. Cosmetic: section stamp "added 19:40 PT" is later than the file mtime (19:19).
6. Prior art: boundedness argument is elementary; check Kimberling-Moses (Fib. Quart. 2019) and Bosma et al. arXiv:2503.04122 before
   claiming the weak conjecture is new.

## Files
arseq.c (independent generator+checker), sweep.py/sweep.log, growth.log, closure.py (exact DFAO from recursion + minimisation +
equivalence vs Walnut files), boxrange.py, walnut_ref14.*, walnut_ref115.*, walnut_forms_rerun.*
