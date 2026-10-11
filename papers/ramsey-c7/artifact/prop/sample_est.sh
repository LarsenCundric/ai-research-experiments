#!/bin/bash
# sample_est.sh n a b c warm_ext depth nsample per_cube_timeout jobs tag
# Estimate total solve time: cubes from march_cu on (lazy base + warm-up external clauses); solve a random sample of cubes with
# cycprop under assumptions; total ~= ncubes * mean(sample time) (timeouts counted at the cap => lower bound).
R=/workspace/ramsey-c7; n=$1; a=$2; b=$3; c=$4; warm=$5; d=$6; ns=$7; to=$8; J=$9; tag=${10}
W=$R/prop/est_$tag; mkdir -p $W; base=$R/cnf/L_n${n}_${a}${b}${c}_tradj_amo.cnf
hdr=$(grep -m1 "^p cnf" $base); nv=$(echo $hdr|cut -d' ' -f3); ncl=$(echo $hdr|cut -d' ' -f4); ne=$(grep -c . $warm)
{ echo "p cnf $nv $((ncl+ne))"; grep -v "^[cp]" $base; cat $warm; } > $W/warm.cnf
s=$(date +%s); $R/tools/CnC/march_cu/march_cu $W/warm.cnf -o $W/cubes -d $d > $W/march.log 2>&1
nc=$(grep -c "^a" $W/cubes); echo "cubes=$nc march_secs=$(( $(date +%s)-s ))"
shuf -i 0-$((nc-1)) -n $ns --random-source=<(yes) > $W/sample.txt
run1() { R=/workspace/ramsey-c7; W=$1; i=$2; to=$3; n=$4; a=$5; b=$6; c=$7; base=$R/cnf/L_n${n}_${a}${b}${c}_tradj_amo.cnf
  t0=$(date +%s.%N); timeout $((to+30)) $R/prop/cycprop $base $n $a $b $c 6 1 $W/c$i 0 $W/cubes $i $to > $W/c$i.log 2>&1; ec=$?
  r=$(grep -o '"result": "[A-Z]*"' $W/c$i.log | cut -d'"' -f4); [ -z "$r" ] && r=TIMEOUT
  echo "$i $r $(awk -v x=$(date +%s.%N) -v y=$t0 'BEGIN{printf "%.1f", x-y}')"; rm -f $W/c$i.ext $W/c$i.final.cnf; }
export -f run1
cat $W/sample.txt | xargs -P $J -I{} bash -c "run1 $W {} $to $n $a $b $c" > $W/results.txt
awk -v nc=$nc '{s+=$3; k++; if($2=="TIMEOUT") t++; if($2=="SAT") sat++} END{printf "sampled=%d timeouts=%d sat=%d mean=%.1fs  est_total_cpu=%.0fs (%.2f core-days)%s\n", k, t, sat, s/k, nc*s/k, nc*s/k/86400, (t>0?" LOWER BOUND":"")}' $W/results.txt
