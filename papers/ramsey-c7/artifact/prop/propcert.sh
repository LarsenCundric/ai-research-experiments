#!/bin/bash
# propcert.sh n a b c mode tag [timeout]: lazy solve with cycprop, then certify: check_cnf on final CNF, CaDiCaL LRAT, cake_lpr.
R=/workspace/ramsey-c7; n=$1; a=$2; b=$3; c=$4; mode=$5; tag=$6; to=${7:-86400}
base=$R/cnf/L_n${n}_${a}${b}${c}_tradj_amo.cnf; out=$R/prop/runs/$tag; mkdir -p $R/prop/runs
[ -f $base ] || python3 $R/src/genA.py $n $a $b $c $base --sb tradj --amo --eager-upto 5
timeout $to $R/prop/cycprop $base $n $a $b $c 6 $mode $out 1 > $out.solver.log 2>&1
res=$(grep '^{' $out.solver.log); echo "solve: $res"
if echo "$res" | grep -q '"UNSAT"'; then
  echo "check_cnf: $(python3 $R/src/check_cnf.py $out.final.cnf $n $a $b $c tradj | tail -1)"
  s=$(date +%s.%N); $R/tools/cadical/build/cadical -q --lrat $out.final.cnf $out.lrat > /dev/null; ec=$?
  echo "offline cadical exit=$ec secs=$(awk -v a=$(date +%s.%N) -v b=$s 'BEGIN{printf "%.1f", a-b}') proof_bytes=$(stat -c%s $out.lrat)"
  s=$(date +%s.%N); v=$($R/tools/cake_lpr/cake_lpr $out.final.cnf $out.lrat | grep "^s"); echo "cake_lpr: $v secs=$(awk -v a=$(date +%s.%N) -v b=$s 'BEGIN{printf "%.1f", a-b}')"
  rm -f $out.lrat
elif echo "$res" | grep -q '"SAT"'; then
  python3 $R/src/model2col.py $out.model $n $out.coloring.txt > /dev/null
  echo "checkA: $(python3 $R/src/checkA.py $out.coloring.txt $a $b $c | tail -1)  checkB: $(python3 $R/src/checkB.py $out.coloring.txt $a $b $c | tail -1)"
fi
