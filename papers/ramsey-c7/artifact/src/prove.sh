#!/bin/bash
# usage: prove.sh file.cnf tag   -> runs CaDiCaL (LRAT) + cake_lpr + lrat-check, and kissat (DRAT) + drat-trim.
set -u
R=/workspace/ramsey-c7; T=$R/tools; F=$1; TAG=$2; P=$R/proofs; L=$R/logs/proof_$TAG.log
echo "== $TAG $(date)  cnf=$F sha256=$(sha256sum $F|cut -c1-16)" > $L
s=$(date +%s.%N); $T/cadical/build/cadical -q --lrat --no-binary $F $P/$TAG.lrat >> $L 2>&1; echo "cadical exit=$? secs=$(awk -v a=$(date +%s.%N) -v b=$s "BEGIN{printf \"%.1f\", a-b}") proof_bytes=$(stat -c%s $P/$TAG.lrat)" >> $L
s=$(date +%s.%N); $T/cake_lpr/cake_lpr $F $P/$TAG.lrat >> $L 2>&1; echo "cake_lpr exit=$? secs=$(awk -v a=$(date +%s.%N) -v b=$s "BEGIN{printf \"%.1f\", a-b}")" >> $L
s=$(date +%s.%N); $T/drat-trim/lrat-check $F $P/$TAG.lrat > $P/$TAG.lratcheck.out 2>&1; grep -m1 "VERIFIED\|FAIL\|rror" $P/$TAG.lratcheck.out >> $L; echo "lrat-check exit=$? secs=$(awk -v a=$(date +%s.%N) -v b=$s "BEGIN{printf \"%.1f\", a-b}")" >> $L
s=$(date +%s.%N); $T/kissat/build/kissat -q --no-binary $F $P/$TAG.drat >> $L 2>&1; echo "kissat exit=$? secs=$(awk -v a=$(date +%s.%N) -v b=$s "BEGIN{printf \"%.1f\", a-b}") proof_bytes=$(stat -c%s $P/$TAG.drat)" >> $L
s=$(date +%s.%N); $T/drat-trim/drat-trim $F $P/$TAG.drat -t 200000 > $P/$TAG.drattrim.out 2>&1; echo "drat-trim exit=$? secs=$(awk -v a=$(date +%s.%N) -v b=$s "BEGIN{printf \"%.1f\", a-b}") verdict=$(grep -o 's VERIFIED\|s NOT VERIFIED' $P/$TAG.drattrim.out)" >> $L
grep -v "^c \|^v " $L | grep -v "^$"
