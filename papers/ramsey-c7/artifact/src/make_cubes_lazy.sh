#!/bin/bash
# make_cubes_lazy.sh n a b c depth warm_secs maxwarm out_cubes
# march_cu segfaults on the full K15 CNF (4.6M clauses), so cube a smaller formula with the SAME variable numbering:
# lazy base CNF (ALO/AMO/SB/short cycles, from genA.py --eager-upto 5) + the first maxwarm cycle clauses found by a cycprop warm-up.
# Cubes are only a split; completeness is certified separately by cnc_lrat.py's coverage step (F + negated cubes, cake_lpr).
R=/workspace/ramsey-c7; n=$1; a=$2; b=$3; c=$4; d=$5; ws=$6; mw=$7; out=$8; tmp=$(mktemp -d)
base=$R/cnf/L_n${n}_${a}${b}${c}_tradj_amo.cnf
[ -f $base ] || python3 $R/src/genA.py $n $a $b $c $base --sb tradj --amo --eager-upto 5
timeout $((ws+60)) $R/prop/cycprop $base $n $a $b $c 6 1 $tmp/warm 0 x 0 $ws > $tmp/warm.log 2>&1
head -$mw $tmp/warm.ext > $tmp/w.ext; k=$(grep -c . $tmp/w.ext)
hdr=$(grep -m1 "^p cnf" $base); nv=$(echo $hdr|cut -d' ' -f3); ncl=$(echo $hdr|cut -d' ' -f4)
{ echo "p cnf $nv $((ncl+k))"; grep -v "^[cp]" $base; cat $tmp/w.ext; } > $tmp/w.cnf
$R/tools/CnC/march_cu/march_cu $tmp/w.cnf -o $tmp/cubes -d $d > $tmp/march.log 2>&1
grep "^a" $tmp/cubes > $out; echo "warm_clauses=$k cubes=$(grep -c . $out) -> $out"; tail -2 $tmp/march.log; rm -rf $tmp
