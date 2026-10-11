import itertools, random, subprocess, sys
random.seed(20261009)
forms=[]
forms += [((a,b),100000) for a in range(1,13) for b in range(1,13)]
forms += [(f,60000) for f in itertools.product(range(1,7),repeat=3)]
adv=[(12,1),(12,1,1),(12,1,1,1),(12,1,1,1,1),(1,1,1,1,12),(1,1,1,12),(12,12,12,12,12),(1,12,1,12,1),(12,1,12,1,12),
     (12,11,10,9,8),(8,9,10,11,12),(1,2,3,4,5),(5,4,3,2,1),(1,1,1,1,1),(2,2,2,2,2),(12,12),(1,12),(12,1,12),(1,12,12,12,12),
     (12,12,12,12,1),(7,1,1,1,7),(1,7,7,7,1),(3,1,4,1,5),(9,2,6,5,3),(11,1,11,1,11)]
forms += [(f,100000) for f in adv]
forms += [(tuple(random.randint(1,12) for _ in range(random.choice([3,4,5]))),50000) for _ in range(200)]
fails=0; tight=0; tot=0
with open('sweep.log','w') as log:
    for f,N in forms:
        try:
            r=subprocess.run(['nice','-n','19','timeout','60','./arseq',str(N)]+[str(x) for x in f],capture_output=True,text=True)
            out=r.stdout.strip() or ('ERR '+str(f)+' rc=%d'%r.returncode)
        except Exception as e:
            out='EXC %s %s'%(f,e); r=None
        log.write(out+'\n'); log.flush(); tot+=1
        if r is None or r.returncode!=0: fails+=1; print('FAIL',out,flush=True)
        if 'tight=1' in out: tight+=1
print('forms',tot,'fails',fails,'box tight',tight)
