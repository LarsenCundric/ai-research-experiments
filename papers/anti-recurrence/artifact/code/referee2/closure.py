"""Independent exact DFAO construction from the window recursion (T=1,T'=2 case), plus Moore minimisation,
and comparison with a Walnut word automaton file. Own code; uses only arseq's d-dump for the first few terms."""
import sys, subprocess, itertools
def fdiv(a,b): return a//b
def setup(a):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*x for j,x in enumerate(a)); return k,tau,K,A1
def box(a):
    k,tau,K,A1=setup(a)
    Phi=lambda r,x: A1-K-1-r+sum(a[j-1]*fdiv(k*r+j-1-x,K) for j in range(1,k+1))
    best=None
    for L in range(0,-5000,-1):
        U=max([Phi(r,L) for r in range(tau)]+[-k*(tau-1)])
        if U>=L and all(Phi(r,U)>=L for r in range(tau)):
            if best is None or U-L<best[1]-best[0]: best=(L,U)
    return best
def G(a,r,y0,y1):
    k,tau,K,A1=setup(a); s=A1-K-1-r-tau
    for j in range(1,k+1):
        u=k*r+j-1
        if y0<=u: s+=a[j-1]
        if y1<=u-K: s+=a[j-1]
    return s
def build(a,N=4000):
    k,tau,K,A1=setup(a); L,U=box(a)
    assert K*1>=U and K*2>K-1-L, "T,T' not (1,2)"
    out=subprocess.run(['nice','-n','19','./arseq',str(N)]+[str(x) for x in a],env={'DUMP':'/tmp/cl_d.txt'},capture_output=True,text=True)
    d=[0]+[int(x) for x in open('/tmp/cl_d.txt')]   # d[0]=0 convention
    P0=3
    def H(V,c):
        dm1,d0,d1=V
        def dd(idx_rel):  # d(tau*p+c+idx_rel) for idx_rel in -1,0,1 as function of window
            m=c+idx_rel        # tau*p+m, m in -1..tau
            # tau*p+m = tau*q + r + 1
            qoff,r=divmod(m-1,tau)   # q=p+qoff
            y={-1:dm1,0:d0,1:d1,2:None}
            return G(a,r,y[qoff],y[qoff+1])
        return (dd(-1),dd(0),dd(1))
    states={}; trans={}; outp={}
    def sid(key):
        if key not in states: states[key]=len(states)
        return states[key]
    todo=[('num',0)]; sid(('num',0)); seen=set()
    while todo:
        s=todo.pop(); 
        if s in seen: continue
        seen.add(s)
        if s[0]=='num':
            p=s[1]; outp[states[s]]=d[p]
            for c in range(tau):
                n=tau*p+c
                t=('num',n) if n<P0 else ('win',(d[n-1],d[n],d[n+1]))
                trans[(states[s],c)]=sid(t); todo.append(t)
        else:
            V=s[1]; outp[states[s]]=V[1]
            for c in range(tau):
                t=('win',H(V,c)); trans[(states[s],c)]=sid(t); todo.append(t)
    nwin=sum(1 for s in states if s[0]=='win')
    return states,trans,outp,tau,nwin,d
def minimize(n,trans,outp,tau):
    part={s:outp[s] for s in range(n)}
    while True:
        sig={s:(part[s],)+tuple(part[trans[(s,c)]] for c in range(tau)) for s in range(n)}
        keys={}; new={s:keys.setdefault(sig[s],len(keys)) for s in range(n)}
        if len(set(new.values()))==len(set(part.values())): return new
        part=new
def eval_dfao(trans,outp,tau,n,start=0):
    s=start; digs=[]
    while n: digs.append(n%tau); n//=tau
    for c in reversed(digs): s=trans[(s,c)]
    return outp[s]
def read_walnut(path):
    lines=[l.split() for l in open(path) if l.strip()]
    base=lines[0]; tr={}; out={}; cur=None
    for l in lines[1:]:
        if '->' in l: tr[(cur,int(l[0]))]=int(l[2])
        else: cur=int(l[0]); out[cur]=int(l[1])
    return tr,out
if __name__=='__main__':
    a=tuple(int(x) for x in sys.argv[1].split(','))
    states,trans,outp,tau,nwin,d=build(a)
    n=len(states); m=minimize(n,trans,outp,tau)
    print('form',a,'raw states',n,'window states',nwin,'minimal states',len(set(m.values())))
    if len(sys.argv)>2:
        tr,out=read_walnut(sys.argv[2]); off=int(sys.argv[3])
        # product equivalence check: (my state, walnut state) pairs reachable, outputs must agree (walnut out - off == my out), except we skip n=0
        from collections import deque
        bad=0; seen=set(); dq=deque()
        for c in range(1,tau):
            dq.append((trans[(0,c)],tr[(0,c)]))
        while dq:
            x,y=dq.popleft()
            if (x,y) in seen: continue
            seen.add((x,y))
            if outp[x]!=out[y]-off: bad+=1
            for c in range(tau): dq.append((trans[(x,c)],tr[(y,c)]))
        print('equivalence vs',sys.argv[2],': product pairs',len(seen),'output mismatches',bad)
