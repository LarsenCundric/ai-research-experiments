# Open items for paper/main.tex (updated Sun Oct 11 2026, 09:21 PT)

The compiled PDF (paper/main.pdf, 9 pages) has no visible TODOs.
Backups: main_pre_todo.tex/.pdf (before the TODO pass, Oct 10) and main_pre_readability.tex/.pdf (before the Oct 11 changes).

## Resolved on Oct 11
- K21 leg A audit: re-ran `src/audit_cnc.py cnc/lazy_n21_677` (read-only; output written to paper/audit_K21_legA.txt, NOT into
  cnc/). Result: AUDIT PASS. Top coverage and all 15 split coverages were re-proved with kissat + drat-trim, 1961 leaf records are
  consistent, and 1016/1016 top-level cubes are certified. The paper now states this.
- Tool versions: `cadical --build` reports c60730422e75 (3.0.1) and `kissat --build` reports 8af8e56f174b (4.0.4), matching the
  hashes in the paper. The VM hostname confirms "virtual machine" in the hardware line.
- artifact/README.md: K21 is no longer pending. Sections 4 and 5 now describe the cnc_tree.py runs, the leg B status and the audit
  result. make_checksums.sh now also covers cnc_tree.py, splits files, NOTES.md and the K21 audit. SHA256SUMS was regenerated
  on Oct 11.
- Role labels under the author name, and the AI disclosure sentence about not having verified the work, were added. There was no
  "full responsibility" wording to remove.

## 1. Leg B for K15, i.e. R(C4,C7,C7) <= 15 (cnc/B/n15_477, running; ETA about Tue Oct 13 evening)
Status in the paper (Remark 10 and Appendix C): "As of 11 October 2026, 792 of the 1022 top-level cubes have been certified, all UNSAT".
When it finishes with an audit PASS:
- [ ] Abstract: change "An independent re-check ... is in progress" to say the result was obtained a second time.
- [ ] Proof of Theorem 1: add leg B (top-level 1022/1022, splits, leaves, coverage by drat-trim + cake_lpr, audit). Drop "The proof
      of the upper bound rests on leg A" if both legs are reported.
- [ ] Remark 10 and Appendix C "K15, leg B (in progress)": replace them with the final statistics (solve / Kissat DRAT / drat-trim
      times, wall clock). Save the audit output, e.g. paper/audit_K15_legB.txt.
- [ ] Section 3.4: if needed, say that leg B was also re-split (34 splits as of Oct 11).
- [ ] If leg B finds a SAT cube, STOP: that contradicts leg A and has to be investigated before anything is published.

## 2. Leg B for K21, i.e. R(C6,C7,C7) <= 21 (cnc/B/n21_677, queued; not started)
- [ ] Remark 10: replace "has not yet been run" with the results. Update the abstract ("will follow") and the cube counts in
      Section 3.4.

## 3. Facts that are approximate or unverifiable from files
- [ ] K21 timings are sums over status.jsonl. Solves killed by restarts are probably not recorded, so the true total may be
      slightly higher than "about 60 core-hours".
- [ ] The CPU model is not exposed ("Intel(R) Xeon(R) Processor"). The paper says only "8-core Intel Xeon virtual machine, 15 GiB".

## 4. Larsen's decisions
- [ ] Personal e-mail: there is no \address or \email. Add `\email{...}` after the \author line once chosen (no xAI/SpaceXAI
      affiliation, no x.ai address).
- [ ] Authorship: the role labels now make the AI authorship explicit. Decide whether to look for a co-author or expert reviewer
      before submitting anywhere.
- [ ] Venue policy: many journals require an author-responsibility statement and do not accept AI-generated manuscripts. The paper
      deliberately makes no responsibility claim. Check the target venue (arXiv also has AI policies).
- [ ] Acknowledgements: none for now.
- [ ] "Not reviewed by a human expert": update when it has been.

## 5. Data / code availability
- [ ] No public repository or DOI. The paper says "available from the author on request". /workspace/ramsey-c7-code-and-proofs.zip
      (made Oct 11) is a candidate for a Zenodo deposit. When it is deposited, replace the sentence with the DOI. The K15 leg B files
      in that zip are an in-progress snapshot.

## 6. References (checked Oct 10 2026, unchanged)
All DOIs were verified via Crossref or DataCite. These items have no DOI:
- [ ] Crawford-Ginsberg-Luks-Roy KR'96 (148-159): checked against the KR'96 table of contents. SAT Competition 2024 description
      (B-2024-1, 8-10): checked against the authors' page.
- [ ] Tse 2007, Sun-Yang-Lin-Zheng 2007, Sun-Yang-Wang-Li-Xu 2006: match only the bibliography in Radziszowski's survey. I did not
      see the papers themselves.
- [ ] Kohayakawa-Simonovits-Skokan full version: not found in Crossref. The paper cites the verified 2005 extended abstract and
      points to [Rad, 6.3.1] for the full proof.
