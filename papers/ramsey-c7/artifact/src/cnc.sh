#!/bin/bash
# cube-and-conquer: cnc.sh file.cnf depth jobs tag
# cubes from march_cu (complete cube tree), each cube solved by kissat with cube literals appended as unit clauses.
R=/workspace/ramsey-c7; F=$1; D=$2; J=$3; TAG=$4; W=$R/cnc/$TAG; mkdir -p $W
s=$(date +%s)
$R/tools/CnC/march_cu/march_cu $F -o $W/cubes -d $D > $W/march.log 2>&1
nc=$(grep -c "^a" $W/cubes); echo "cubes=$nc march_secs=$(( $(date +%s)-s ))"
solve() { R=/workspace/ramsey-c7; F=$1; W=$2; i=$3; line=$(sed -n "${i}p" $W/cubes)
  lits=$(echo "$line" | sed 's/^a //; s/ 0$//'); nl=$(echo $lits | wc -w)
  hdr=$(grep -m1 "^p cnf" $F); nv=$(echo $hdr|cut -d' ' -f3); ncl=$(echo $hdr|cut -d' ' -f4)
  { echo "p cnf $nv $((ncl+nl))"; grep -v "^[cp]" $F; for l in $lits; do echo "$l 0"; done; } > /dev/shm/cube_${i}_$$.cnf
  t0=$(date +%s.%N); $R/tools/kissat/build/kissat -q /dev/shm/cube_${i}_$$.cnf > /dev/null 2>&1; ec=$?
  echo "$i $ec $(awk -v a=$(date +%s.%N) -v b=$t0 'BEGIN{printf "%.2f", a-b}')"; rm -f /dev/shm/cube_${i}_$$.cnf; }
export -f solve
seq 1 $nc | xargs -P $J -I{} bash -c "solve $F $W {}" > $W/results.txt
echo "wall_secs=$(( $(date +%s)-s )) results: $(awk '{print $2}' $W/results.txt | sort | uniq -c | tr '\n' ' ') cpu_sum=$(awk '{s+=$3} END{printf "%.0f", s}' $W/results.txt) max=$(sort -k3 -g $W/results.txt | tail -1)"
