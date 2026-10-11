#!/bin/bash
# certification overhead for one sampled K21 C6C7C7 cube (ext clauses from the uncertified sample run)
R=/workspace/ramsey-c7; D=$R/cnc/k21_overhead; E=$R/prop/est_n21_677_w100k; i=$1
B=$R/cnf/L_n21_677_tradj_amo.cnf
t=$(date +%s.%N); python3 $R/src/check_cnf.py $E/c$i.ext 21 6 7 7 cyclesonly | tail -1; echo "check_cnf_secs $(echo "$(date +%s.%N) $t" | awk '{print $1-$2}')"
python3 - <<PY
cubes=[l.split()[1:-1] for l in open("$E/cubes") if l.startswith("a ")]; q=cubes[$i]
h=[l for l in open("$B") if l.startswith("p cnf")][0].split(); nv,nc=int(h[2]),int(h[3])
ext=open("$E/c$i.ext").read(); k=ext.count("\n")
with open("$D/F$i.cnf","w") as f:
    f.write(f"p cnf {nv} {nc+k+len(q)}\n"); f.write("".join(l for l in open("$B") if l[0] not in "cp")); f.write(ext)
    for x in q: f.write(f"{x} 0\n")
PY
t=$(date +%s.%N); $R/tools/cadical/build/cadical -q --lrat $D/F$i.cnf $D/F$i.lrat; echo "cadical_rc $? secs $(echo "$(date +%s.%N) $t" | awk '{print $1-$2}') proof_bytes $(stat -c %s $D/F$i.lrat)"
t=$(date +%s.%N); $R/tools/cake_lpr/cake_lpr $D/F$i.cnf $D/F$i.lrat | tail -1; echo "cake_secs $(echo "$(date +%s.%N) $t" | awk '{print $1-$2}')"
rm -f $D/F$i.lrat $D/F$i.cnf
