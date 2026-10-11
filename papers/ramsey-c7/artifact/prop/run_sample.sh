#!/bin/bash
# run_sample.sh W n a b c timeout jobs : solve sampled cubes (W/sample.txt indices into W/cubes) with cycprop under assumptions
R=/workspace/ramsey-c7; W=$1; n=$2; a=$3; b=$4; c=$5; to=$6; J=$7
run1() { R=/workspace/ramsey-c7; W=$1; i=$2; to=$3; n=$4; a=$5; b=$6; c=$7; base=$R/cnf/L_n${n}_${a}${b}${c}_tradj_amo.cnf
  t0=$(date +%s.%N); timeout $((to+30)) $R/prop/cycprop $base $n $a $b $c 6 1 $W/c$i 0 $W/cubes $i $to > $W/c$i.log 2>&1
  r=$(grep -o '"result": "[A-Z]*"' $W/c$i.log | cut -d'"' -f4); [ -z "$r" ] && r=TIMEOUT
  echo "$i $r $(awk -v x=$(date +%s.%N) -v y=$t0 'BEGIN{printf "%.1f", x-y}') ext=$(grep -c . $W/c$i.ext)"; rm -f $W/c$i.final.cnf; }
export -f run1
cat $W/sample.txt | xargs -P $J -I{} bash -c "run1 $W {} $to $n $a $b $c" >> $W/results.txt
