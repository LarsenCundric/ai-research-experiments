#!/bin/bash
# Regenerate artifact/SHA256SUMS (paths relative to /workspace/ramsey-c7). Re-run after any run finishes.
cd /workspace/ramsey-c7
{
  ls src/rlib.py src/genA.py src/genB.py src/check_cnf.py src/check_cnfB.py src/checkA.py src/checkB.py src/crosscheck.py \
     src/lazyB.py src/cnc_lazy.py src/cnc_lazyB.py src/cnc_tree.py src/audit_cnc.py src/make_cubes_lazy.sh src/make_cubesB.sh src/test_sbB.py \
     src/model2col.py src/constructions.py src/circulant.py src/prove.sh prop/cycprop.cpp 2>/dev/null
  ls colorings/*.txt cnc/B/*.col 2>/dev/null
  ls cnf/L_n15_477_tradj_amo.cnf cnf/L_n21_677_tradj_amo.cnf cnf/L_n13_467_tradj_amo.cnf cnf/L_n12_447_tradj_amo.cnf \
     cnf/B_n15_477_sb_lazy.cnf cnf/B_n12_447_sb_lazy.cnf 2>/dev/null
  for d in cnc/lazy_n15_477 cnc/lazy_n21_677 cnc/lazy_n13_467 cnc/lazy_n12_447 cnc/B/n15_477 cnc/B/n12_447; do
    for f in cubes meta.json coverage.json check_base.log status.jsonl summary.json audit.txt run.log splits.jsonl; do [ -f $d/$f ] && echo $d/$f; done
    ls $d/splits/*.cubes 2>/dev/null
  done
  ls CNC_ARGUMENT.md NOTES.md paper/main.tex paper/main.pdf paper/audit_K21_legA.txt
} | xargs sha256sum > artifact/SHA256SUMS
echo "$(wc -l < artifact/SHA256SUMS) files hashed -> artifact/SHA256SUMS"
