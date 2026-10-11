"""Pass-2 cross-checks (own code):
 (a) exact range of d via closure of the Theorem C automaton (all reachable triples are realised, so the
     set of middle coordinates is exactly {d(n): n>=1}) vs. the minimal box (i)-(iv) and vs. (L*,U*);
 (b) minimal msd DFAO sizes under two indexing conventions:
     ours: input n>=0, output d(n), d(0)=0;  FJ: input n-1>=0, output d(n) (i.e. s(n)=d(n+1)).
     Both built exactly from Theorem B (states = triples V(m)), then Moore-minimised.
 (c) V(1)=(0,d(1),d(2)) lies in [-K,tau-k]^3 (for the 1+(...)^3 bound)."""
import sys, itertools, random
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recheck import gen_AB, min_box
from twoterm import G, data, minimize
import math
from fractions import Fraction
def star_box(a):  # same formula as verify_v2.star_box (Prop. 3.3)
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*c for j,c in enumerate(a))
    c0=Fraction(A1-K-1)+Fraction(A1-tau,K)
    L=min(0, math.floor((c0*(1-Fraction(1,k))-tau+1)/(1-Fraction(1,k*k))),
          math.floor(k*(c0-1)+k*k*(tau-1)), math.floor(k*(c0-1)/(k+1)))
    return L, math.floor(c0-Fraction(L,k))
def closure(a, conv):
    k,tau,K,A1=data(a)
    A,_=gen_AB(a,tau+3); d=[0]+[A[n-1]-(K+1)*n for n in range(1,tau+3)]
    def H(V,c):
        out=[]
        for e in (-1,0,1):
            m=c+e-1
            out.append(G(a,m,V[1],V[2]) if m>=0 else G(a,tau+m,V[0],V[1]))
        return tuple(out)
    trans={'S':{0:'S'}}; todo=[]
    for c in range(1,tau):
        V=(d[c-1],d[c],d[c+1]); trans['S'][c]=V; todo.append(V)
    while todo:
        V=todo.pop()
        if V in trans: continue
        trans[V]={c:H(V,c) for c in range(tau)}; todo.extend(W for W in trans[V].values() if W not in trans)
    if conv=='ours': outp={q:(0 if q=='S' else q[1]) for q in trans}
    else:            outp={q:(d[1] if q=='S' else q[2]) for q in trans}
    return trans,outp,d
def run(a):
    k,tau,K,A1=data(a)
    tr,op,d=closure(a,'ours')
    vals=[q[1] for q in tr if q!='S']; ex=(min(vals),max(vals))
    allin=all(-K<=x<=tau-k for q in tr if q!='S' for x in q)
    mb=min_box(a); sb=star_box(a)
    trF,opF,_=closure(a,'fj')
    return dict(exact=ex, minbox=mb, star=sb, excess=(mb[0]-sb[0])+(sb[1]-mb[1]), boxeq=(tuple(mb)==ex),
                states=len(tr), min_ours=minimize(tr,op,tau), min_fj=minimize(trF,opF,tau), V1in=(0,d[1],d[2]) in tr and allin,
                gapK=ex[0]+K)
if __name__=="__main__":
    mode=sys.argv[1]
    if mode=="named":
        for a in [(1,3),(1,4),(1,5),(2,7),(1,1,5),(1,1),(1,2),(2,1),(1,1,1),(1,1,1,1)]:
            print(a, run(a), flush=True)
    else:
        forms=[(x,y) for x in range(1,21) for y in range(1,21)]+list(itertools.product(range(1,7),repeat=3))
        rnd=random.Random(7)
        forms+=[tuple(rnd.randint(1,12) for _ in range(rnd.randint(4,6))) for _ in range(120)]
        from collections import Counter
        exc=Counter(); eq=0; v1=0; mingap=10**9; argmin=[]
        for a in forms:
            r=run(a); exc[r['excess']]+=1; eq+=r['boxeq']; v1+=r['V1in']
            if r['gapK']<mingap: mingap=r['gapK']; argmin=[a]
            elif r['gapK']==mingap: argmin.append(a)
        print(f"forms={len(forms)} minbox==exact_range: {eq}/{len(forms)}  V(1) and all triples in [-K,tau-k]^3: {v1}/{len(forms)}")
        print("excess of (L*,U*) over minimal box (total width units):",dict(sorted(exc.items())))
        print("min over forms of (exact min + K):",mingap,"attained by",len(argmin),"forms, e.g.",argmin[:8])
