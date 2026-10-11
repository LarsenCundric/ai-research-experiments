#!/bin/bash
# make_cubesB.sh BASE n a b c depth warm_secs maxwarm out_cubes  -- cubes for encoding B: march_cu on BASE + first maxwarm
# clauses found by a lazyB warm-up (same variables). The split is untrusted; coverage is certified separately.
R=/workspace/ramsey-c7; base=$1; n=$2; a=$3; b=$4; c=$5; d=$6; ws=$7; mw=$8; out=$9; tmp=$(mktemp -d)
python3 $R/src/lazyB.py $base $n $a $b $c x -1 $tmp/warm --maxsecs $ws > $tmp/warm.log
head -$mw $tmp/warm.ext > $tmp/w.ext; k=$(grep -c . $tmp/w.ext)
hdr=$(grep -m1 "^p cnf" $base); nv=$(echo $hdr|cut -d' ' -f3); ncl=$(echo $hdr|cut -d' ' -f4)
{ echo "p cnf $nv $((ncl+k))"; grep -v "^[cp]" $base; cat $tmp/w.ext; } > $tmp/w.cnf
$R/tools/CnC/march_cu/march_cu $tmp/w.cnf -o $tmp/cubes -d $d > $tmp/march.log 2>&1
grep "^a" $tmp/cubes > $out; echo "warm: $(cat $tmp/warm.log) used=$k cubes=$(grep -c . $out) -> $out"; tail -2 $tmp/march.log; rm -rf $tmp
