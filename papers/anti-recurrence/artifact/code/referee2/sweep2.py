import itertools, random, subprocess, sys, time
random.seed(99)
F=[]
F += [((a,b),30000) for a in range(1,31) for b in range(1,31)]
F += [(f,20000) for f in itertools.product(range(1,9),repeat=3)]
for k in range(2,9):
    for a in [13,20,37,50,80,100,150,200]:
        F.append(((a,)+(1,)*(k-1),20000)); F.append(((1,)*(k-1)+(a,),20000))
        F.append(((a,)*k,20000)); F.append((tuple(a if j%2==0 else 1 for j in range(k)),20000))
        F.append(((a,a-1)+(1,)*(k-2),20000)); F.append(((1,)+(a,)*(k-1),20000)); F.append(((a,)*(k-1)+(1,),20000))
for _ in range(500):
    k=random.randint(4,8); M=random.choice([5,12,30,60,100])
    F.append((tuple(random.randint(1,M) for _ in range(k)),20000))
seen=set(); FF=[]
for f,N in F:
    if f not in seen: seen.add(f); FF.append((f,N))
fails=0; t0=time.time()
with open('sweep2.log','w') as log:
    for f,N in FF:
        r=subprocess.run(['nice','-n','19','timeout','120','./arseq2',str(N)]+[str(x) for x in f],capture_output=True,text=True)
        out=r.stdout.strip() or 'ERR %s rc=%d %s'%(f,r.returncode,r.stderr[:200])
        log.write(out+'\n'); log.flush()
        if r.returncode!=0: fails+=1; print('FAIL',out,flush=True)
print('forms',len(FF),'fails',fails,'time',round(time.time()-t0))
