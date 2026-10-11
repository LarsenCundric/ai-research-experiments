"""Independent exact re-check of each step of PROOF.md on generated data (integer arithmetic only).
For each form a: (a) identity (*) from the raw definition of c(m) = #{i: A_i < B_m} (computed from the A/B lists, not from d);
(b) Step-2 box: built from the EXPLICIT existence recipe (not a search), conditions (i)-(iv) checked exactly,
    and pointwise Phi(r,U) <= d(n) <= Phi(r,L) for all n<=N; also the search-minimal box;
(c) Step-3 window recursion d(tau q+r+1)=G_r(window) for all T<=q with window inside data.
Also reports whether a is A1-bounded (i.e. already covered by Fokkink-Joshi Thm 12)."""
import sys, random, math, bisect
from fractions import Fraction
def gen_AB(a,N):
    k=len(a); used=bytearray((k*sum(a)+1)*(N+2)+50); m=1; A=[]; B=[]
    for n in range(N):
        bs=[]
        for _ in a:
            while used[m]: m+=1
            used[m]=1; bs.append(m)
        x=sum(c*b for c,b in zip(a,bs)); used[x]=1; A.append(x); B.extend(bs)
    return A,B
def Phi(a,r,x):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*c for j,c in enumerate(a))
    return A1-K-1-r+sum(a[j-1]*((k*r+j-1-x)//K) for j in range(1,k+1))
def conds(a,L,U):
    k=len(a); tau=sum(a)
    return (all(Phi(a,r,L)<=U for r in range(tau)) and all(Phi(a,r,U)>=L for r in range(tau))
            and U>=-k*(tau-1) and L<=0 and L<=U)
def explicit_box(a):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*c for j,c in enumerate(a))
    c0=Fraction(A1-K-1)+Fraction(A1-tau,K)
    Lr=(c0*(1-Fraction(1,k))-tau)/(1-Fraction(1,k*k))
    L=min(0,math.floor(Lr))
    while True:
        U=math.floor(c0-Fraction(L,k))
        if U>=-k*(tau-1) and U>=L: return L,U
        L-=1
def min_box(a):
    best=None
    for L in range(0,-3000,-1):
        U=max(max(Phi(a,r,L) for r in range(sum(a))),-len(a)*(sum(a)-1))
        if conds(a,L,U) and (best is None or U-L<best[1]-best[0]): best=(L,U)
    return best
def check(a,N):
    k=len(a); tau=sum(a); K=k*tau; kap=K+1; A1=sum((j+1)*c for j,c in enumerate(a))
    A,B=gen_AB(a,N); d=[None]+[A[i]-kap*(i+1) for i in range(N)]
    # (a) identity from raw definitions
    bad_a=0
    for n in range(1,N+1):
        cs=0
        for j in range(1,k+1):
            m=k*(n-1)+j; Bm=B[m-1]
            c=bisect.bisect_left(A,Bm)        # #{i: A_i < B_m}
            assert Bm==m+c                     # Step 1: B_m = m + c(m)
            cs+=a[j-1]*c
        if d[n]!=A1-K-n+cs: bad_a+=1
    # (b) boxes
    Le,Ue=explicit_box(a); okE=conds(a,Le,Ue)
    Lm,Um=min_box(a)
    bad_b=0
    for n in range(1,N+1):
        r=(n-1)%tau
        if not (Phi(a,r,Um)<=d[n]<=Phi(a,r,Lm) and Lm<=d[n]<=Um and Le<=d[n]<=Ue): bad_b+=1
    # (c) window recursion with the minimal box
    L,U=Lm,Um; T=max(1,-(-U//K)) if U>0 else 1
    Tp=(K-1-L)//K+1                     # smallest T' with K*T' > K-1-L
    bad_c=0; cnt=0
    for n in range(1,N+1):
        q,r=divmod(n-1,tau)
        if q<T or q+Tp-1>N: continue
        cnt+=1
        s=A1-K-1-r-tau*T
        for j in range(1,k+1):
            u=k*r+j-1
            for t in range(-T+1,Tp):
                if d[q+t]<=u-K*t: s+=a[j-1]
        if s!=d[n]: bad_c+=1
    a1b = A1<=(k-1)*tau+2
    return dict(a=a,A1_bounded_FJ=a1b,obs=(min(d[1:]),max(d[1:])),explicit_box=(Le,Ue),explicit_ok=okE,min_box=(Lm,Um),
                identity_mism=bad_a,box_pointwise_viol=bad_b,window=(T,Tp),window_checked=cnt,window_mism=bad_c)
if __name__=="__main__":
    N=int(sys.argv[1]); random.seed(7)
    forms=[(1,4),(1,3),(1,5),(1,6),(1,10),(1,20),(2,3),(2,7),(3,5),(7,3),(1,1),(1,2),(2,1),(1,1,5),(1,1,1),(1,2,3),(1,1,1,1),(9,1),(1,9),(4,9)]
    forms+=[tuple(random.randint(1,12) for _ in range(random.randint(2,5))) for _ in range(30)]
    tot=0
    for a in forms:
        r=check(a,N); print(r,flush=True)
        tot+=r['identity_mism']+r['box_pointwise_viol']+r['window_mism']+(not r['explicit_ok'])
    print("TOTAL FAILURES:",tot)
