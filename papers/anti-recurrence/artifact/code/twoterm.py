"""Exact checks for PROOF.md v2, Lemma 4 (universal box [-K, U*] with U* <= tau-k) and
Theorem 2 (two-term recursion d(tau q+r+1)=G_r(d(q),d(q+1)) for all q>=0 with d(0):=0) and
the explicit msd-first DFAO (states = start + triples (d(m-1),d(m),d(m+1))).
Brute-force generator from recheck.gen_AB (independent of the formulas being tested)."""
import sys, random, itertools
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from recheck import gen_AB, Phi, conds
def data(a):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*c for j,c in enumerate(a)); return k,tau,K,A1
def G(a,r,y0,y1):
    k,tau,K,A1=data(a)
    return A1-K-1-r-tau+sum(a[j-1]*((y0<=k*r+j-1)+(y1<=k*r+j-1-K)) for j in range(1,k+1))
def dfao(a):
    k,tau,K,A1=data(a)
    # first-digit vectors V(c)=(d(c-1),d(c),d(c+1)) for c=1..tau-1 computed from the recursion itself
    d=[0]; 
    # compute d(1..tau+1) via recursion with q=0,1 (self-consistent: d(1) from q=0,r=0 uses d(1) only in an indicator that is 0)
    A,_=gen_AB(a,tau+3); d+= [A[n-1]-(K+1)*n for n in range(1,tau+3)]
    def H(V,c):
        out=[]
        for e in (-1,0,1):
            m=c+e-1
            if m>=0: out.append(G(a,m,V[1],V[2]))
            else: out.append(G(a,tau+m,V[0],V[1]))
        return tuple(out)
    start='S'; trans={}; outp={'S':0}; todo=[]
    trans['S']={0:'S'}
    for c in range(1,tau):
        V=(d[c-1],d[c],d[c+1]); trans['S'][c]=V; todo.append(V)
    while todo:
        V=todo.pop()
        if V in trans: continue
        outp[V]=V[1]; trans[V]={}
        for c in range(tau):
            W=H(V,c); trans[V][c]=W
            if W not in trans: todo.append(W)
    for V in list(trans):
        outp.setdefault(V, V[1] if V!='S' else 0)
    return trans,outp
def run(trans,outp,n,tau):
    digs=[]
    while n: digs.append(n%tau); n//=tau
    s='S'
    for c in reversed(digs): s=trans[s][c]
    return outp[s]
def minimize(trans,outp,tau):
    Q=list(trans); part={q:outp[q] for q in Q}
    while True:
        sig={q:(part[q],tuple(part[trans[q][c]] for c in range(tau))) for q in Q}
        ids={}; new={q:ids.setdefault(sig[q],len(ids)) for q in Q}
        if len(set(new.values()))==len(set(part.values())): return len(set(new.values()))
        part=new
def check(a,N,full=False):
    k,tau,K,A1=data(a)
    U=max(-k*(tau-1),max(Phi(a,r,-K) for r in range(tau)))
    assert conds(a,-K,U) and U<=tau-k, (a,U)
    A,_=gen_AB(a,N); d=[0]+[A[n-1]-(K+1)*n for n in range(1,N+1)]
    assert all(-K<=x<=U for x in d[1:]),a
    for q in range(0,(N-1)//tau):
        for r in range(tau):
            assert d[tau*q+r+1]==G(a,r,d[q],d[q+1]),(a,q,r)
    res=dict(U=U,lo=min(d[1:]),hi=max(d[1:]))
    if full:
        tr,op=dfao(a)
        bad=sum(run(tr,op,n,tau)!=d[n] for n in range(0,N+1))
        assert bad==0,(a,bad)
        res.update(states=len(tr),minstates=minimize(tr,op,tau))
    return res
if __name__=="__main__":
    N=int(sys.argv[1]); mode=sys.argv[2]
    if mode=="named":
        for a in [(1,1),(1,2),(2,1),(1,3),(1,4),(1,5),(2,7),(1,1,1),(1,1,5),(1,1,1,1),(1,12),(12,1)]:
            print(a,check(a,N,full=True),flush=True)
    else:
        forms=[(x,y) for x in range(1,13) for y in range(1,13)]+[f for f in itertools.product(range(1,6),repeat=3)]
        rnd=random.Random(20261009)
        for _ in range(150):
            k=rnd.randint(3,5); forms.append(tuple(rnd.randint(1,12) for _ in range(k)))
        forms+=[(1,)*k for k in range(2,8)]+[(1,)*(k-1)+(20,) for k in range(2,6)]+[(20,)+(1,)*(k-1) for k in range(2,6)]
        worst=0
        for i,a in enumerate(forms):
            r=check(a,N); 
        print(f"{len(forms)} forms, N={N}: Lemma 4 box, bound U<=tau-k, two-term recursion (all q>=0, d(0)=0): 0 failures")
