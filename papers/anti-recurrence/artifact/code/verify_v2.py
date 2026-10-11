"""Exact check of the explicit constants in PROOF.md v2 (Step 2 box recipe, Step 3 W,o,P0, H_c).
For each form: build (A,B) by brute force (recheck.gen_AB), compute d(n)=A_n-kappa n, then
 (a) explicit box (L*,U*) satisfies (i)-(iv) and contains d;
 (b) with T=max(1,ceil(U/K)), T'=floor((K-1-L)/K)+1, o=-2T, W=2T+2T'+1, P0=2T+1:
     window containment inequalities hold, and V(tau p+c)=H_c(V(p)) for all P0<=p, tau p+c+o+W-1<=N;
 done for both the explicit box and the minimal box."""
import sys, math
from fractions import Fraction
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from recheck import gen_AB, Phi, conds, min_box
def star_box(a):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*c for j,c in enumerate(a))
    c0=Fraction(A1-K-1)+Fraction(A1-tau,K)
    L=min(0, math.floor((c0*(1-Fraction(1,k))-tau+1)/(1-Fraction(1,k*k))),
          math.floor(k*(c0-1)+k*k*(tau-1)), math.floor(k*(c0-1)/(k+1)))
    return L, math.floor(c0-Fraction(L,k))
def check(a,N):
    k=len(a); tau=sum(a); K=k*tau; kap=K+1; A1=sum((j+1)*c for j,c in enumerate(a))
    A,_=gen_AB(a,N); d=[None]+[A[n-1]-kap*n for n in range(1,N+1)]
    out=[]
    for name,(L,U) in (('star',star_box(a)),('min',min_box(a))):
        assert conds(a,L,U), (a,name,L,U)
        assert all(L<=x<=U for x in d[1:]), (a,name)
        T=max(1,-(-U//K)); Tp=(K-1-L)//K+1; o=-2*T; W=2*T+2*Tp+1; P0=2*T+1
        assert K*T>=U and K*Tp>K-1-L and K*(Tp-1)<=K-1-L
        assert (o-1)//tau-T+1>=o and (tau+o+W-3)//tau+Tp-1<=o+W-1 and o<=0<=o+W-1
        G=lambda r,y: A1-K-1-r-tau*T+sum(a[j-1]*sum(1 for t in range(-T+1,Tp) if y(t)<=k*r+j-1-K*t) for j in range(1,k+1))
        # direct window recursion for q>=T
        for q in range(T,(N-1)//tau):
            for r in range(tau):
                assert d[tau*q+r+1]==G(r,lambda t:d[q+t]),(a,q,r)
        # H_c maps
        cnt=0
        for p in range(P0,N):
            Vp={s:d[p+s] for s in range(o,o+W)}
            if tau*p+tau-1+o+W-1>N: break
            for c in range(tau):
                for s in range(o,o+W):
                    m=c+s-1; qq=m//tau; r=m%tau   # tau p+c+s = tau(p+qq)+r+1
                    val=G(r,lambda t:Vp[qq+t])
                    assert val==d[tau*p+c+s],(a,p,c,s); cnt+=1
        out.append(f"{name}:[{L},{U}] T={T} T'={Tp} o={o} W={W} P0={P0} Hchecks={cnt}")
    return out
forms=[(1,1),(1,2),(2,1),(1,3),(1,4),(1,5),(1,12),(12,1),(2,7),(3,5),(1,1,1),(1,1,5),(5,1,1),(1,2,3),(1,1,1,1),(2,1,3,1),(1,1,1,1,1)]
N=int(sys.argv[1]) if len(sys.argv)>1 else 20000
for a in forms:
    print(a, *check(a,N), flush=True)
print("ALL OK")
