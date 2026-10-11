# Referee report, pass 2 (PROOF.md v2 + paper/main.tex, 2026-10-09 ~20:40 PT)

Work files: review/r2/ (arseq2.c = new independent checker; sweep2.py/.log = 2270 forms; big.log = 3e6-term runs;
prop33.py; closure_shift.py; walnut_rqf_disjB.*). Build: cc -O2 -o arseq2 arseq2.c ; cc -O2 -o arseq arseq.c

## Verdicts on the new claims
| claim | verdict |
|---|---|
| Lemma 3.4 (universal box, -K <= d <= tau-k) | SOUND. Every step re-derived. 2270 forms, 0 failures (k=2..8, entries up to 200, tau up to 1600). Lower end nearly sharp: exact min is >= -K+2 in every form, = -K+2 for 36 forms (the (a,1) family). Upper end loose: exact max <= 0.66(tau-k). |
| Theorem B (d(tau q+r+1)=G_r(d(q),d(q+1)), q>=0, d(0)=0) | SOUND. Proof checked, q=0 case included. 0 mismatches on all 2270 forms, plus 3e6 terms for 7 large forms. |
| Theorem C (msd DFAO, <= 2+(K+tau-k+1)^3 states) | SOUND. V(tau m+c)=H_c(V(m)) holds on all data. Formula-based closure: every reachable triple lies in the box. The bound is true but very loose (e.g. 7083 vs 3e12 states); V(1) is already in [-K,tau-k]^3, so 1+(...)^3 suffices. (1,4): 28 states, as claimed. |
| Prop 3.3 explicit (L*,U*), Remark 3.6 (o,W,P0) | SOUND. Exact rational check on 1420 forms. |
| 1741 explanation, A_{5q+2}=19+55q | SOUND. Hand derivation checked. Numerically: A_1741=19148, chain 14/70/348, rec (j=1..5) and A_{5q+2} for n<=2e6. |
| Table 1 = RUS | Matches the file exactly (parsed). |
| Walnut (Sec. 4, 6) | SOUND. But (1,1,5) "disjointness of the B's from each other" was never run. I ran it: 3x TRUE (r2/walnut_rqf_disjB.*). |

## Earlier gaps: all fixed
(ii) is made explicit (Prop 3.3). c(m_j) is now counted over i>=1. o, W, P0, digit order and the kernel citation are explicit. Shift-invariance is avoided via d(0)=0. The optional lemma is proved (Lemma 3.4). The bad timestamp is gone. The prior-art search is partly done.

## Required fixes before arXiv
1. (1,3): FJ show a 4-DFAO, i.e. base 4, not a "4-state automaton". Integers Fig. 7 has 6 states (a..f). Cross-check: under FJ's index shift the minimal msd DFAO for (1,3) has exactly 6 states.
2. "Hofstadter defined the anti-Fibonacci numbers" is wrong. Per the OEIS record and FJ: A075326 is by A. Murthy (2002); the mex description is due to Lallouet (2008); the name and observations are Hofstadter's (2014).
3. Zaslavsky's formula is quoted via Math StackExchange. Cite the primary sources instead: Zaslavsky's Theorem 1 is stated with "utterly odd" numbers; the PD form is FJ eq. (2), and Bosma et al. Sec. 3 verify it in Walnut.
4. Overclaims. "Exhaustive computational check" should be "extensive". The title "...are automatic" is wrong because A_n is unbounded; suggest "...are linear plus automatic" or "The Fokkink-Joshi conjecture holds for all linear anti-recurrences".
5. Sec. 6 claims B-B disjointness for all forms. Add r2/walnut_rqf_disjB.* to the artifact, or say it follows from interleaving.
6. Remark 3.5. (a) "(L*,U*) is at most one unit wider" is false in general: on 1236 forms the excess is 2 for 735 of them, e.g. (1,2) gives [-4,0] vs [-3,-1]. (b) Lemma 3.4 bounds the range of d, not "the smallest box"; reword.
7. "Minimal 17-state automaton": state the convention (n>=0, d(0)=0, msd, leading zeros). Under FJ's own convention (input n-1) the minimal sizes are (1,4) 9, (1,5) 11, (2,7) 20, (1,1,5) 9, (1,3) 6. Give these, or say why not.
8. Resolve every TODO:
   - AI-use disclosure: truthful, and it must say that proofs, code and refereeing were done by AI agents and what the author personally checked;
   - affiliation and email;
   - Zenodo DOI;
   - Allouche-Shallit theorem numbers checked against the book (6.6.2 for the kernel is, I believe, right; reading direction is likely Thm 5.2.3, so verify);
   - Shallit page numbers;
   - a repeat of the prior-art search including Google Scholar, zbMATH and MathSciNet, Fraenkel 1982, and Fraenkel-Peled 2007 ("Harnessing the unwieldy MEX function", cited by KM).
9. Sec. 5 item 3 calls an AI agent an "independent referee". Reword as "an independently written second implementation"; do not imply peer review.

## Optional
- New empirical fact: the minimal box (i)-(iv) equals the EXACT range of d in 1682/1682 forms. Exact ranges come from the formula-based closure, not from finite prefixes. Could be stated as a conjecture. Prefix ranges are unreliable: (200,1) has exact min -400 but stays above -370 for the first 3e6 terms. My pass-1 "tight 415/585" statistic was a prefix artefact; correct artifact/docs/REVIEW.md.
- Sharpness remark: lower bound -K is within 2 of optimal, upper bound tau-k is not sharp. Proving d >= -K+2 might be easy.
- Missing related work: Lambek-Moser 1954 (the counting identity), Fraenkel 1982, Fraenkel-Peled 2007, Cobham 1972, Shallit's Walnut book (2022), Allouche-Shallit "ring of k-regular sequences".
- Cite FJ lemmas in both numberings: arXiv L2/L3 = Integers L1/L2.
- Trim the Semantic Scholar/OpenAlex detail from the paper.
- KM pages 96-110 are correct (checked against the PDF footers); FJ's own reference (97-111) is wrong.
- Sec. 5 item 1: the DFAO actually agrees with all n<=2e6 (referee check), not just 4e5 samples.

## Citations verified against primary PDFs/pages
- FJ arXiv and Integers numbering, quotes and dates: OK, apart from the (1,3) state count.
- KM: Thm 2.1, Thm 3.2, Sec. 6 "conjectured answer is yes!", Ex. 12: OK.
- Bosma Sec. 3 and Conj. 2 (Clergyman): OK.
- Hofstadter and Zaslavsky notes: dates OK.
- MSE 5090531: exists, as described.
- OEIS: 3- and 4-rusty term searches give no match: OK.

## Readiness
Mathematics: correct, and I could not break it. Ready for arXiv once required fixes 1-9 are done. Fixes 1-7 are text edits under an hour; 8-9 need the author. The named author must personally read and be able to defend the roughly 2-page proof in Sec. 3 before posting.
