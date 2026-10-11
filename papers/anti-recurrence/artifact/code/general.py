# General "window recursion" test for linear anti-recurrences (Fokkink-Joshi setting).
# For a=(a_1..a_k), tau=sum a, kappa=k*tau+1, d(n)=A_n-kappa*n.  Derived identity (valid when d stays in a box [L,U]):
#   d(tau*q+r+1) = A1 - k*tau - r - 1 + tau*(t0-1) + sum_j a_j * sum_{t=t0..t1} [ d(q+t) <= k*r + j - 1 - k*tau*t ]
# where t0 = smallest t with "always true" failing, t1 = largest t with "always false" failing (computed from L,U).
# Proof certificate ("box invariance"): F_r(all L) <= U and F_r(all U) >= L for all r, plus base cases checked directly.
import sys, math
def gen(a,N):
    k=len(a); used=bytearray((k*sum(a)+1)*N+10*sum(a)*k+100); m=1; A=[]
    for n in range(N):
        bs=[]
        for _ in a:
            while used[m]: m+=1
            used[m]=1; bs.append(m)
        x=sum(c*b for c,b in zip(a,bs)); used[x]=1; A.append(x)
    return A
def analyse(a,N):
    k=len(a); tau=sum(a); kap=k*tau+1; A=gen(a,N); A1=A[0]
    d=[None]+[A[i]-kap*(i+1) for i in range(N)]
    L=min(d[1:]); U=max(d[1:])
    # t always-true region: t <= tA where -k*tau*t >= U  (worst r=0,j=1 threshold = -k*tau*t)
    tA=math.floor(-U/(k*tau))        # all t<=tA always true
    tB=math.floor((k*tau-1-L)/(k*tau))  # all t>tB always false  (worst threshold k*tau-1-k*tau*t < L)
    t0,t1=tA+1,tB
    def F(r,win):  # win: dict t->value
        s=A1-k*tau-r-1+tau*(t0-1)
        for j in range(1,k+1):
            for t in range(t0,t1+1):
                if win[t]<=k*r+j-1-k*tau*t: s+=a[j-1]
        return s
    # empirical check of identity
    bad=0; q0=max(1,1-t0+1)
    for n in range(1,N+1):
        q,r=divmod(n-1,tau)
        if q<q0 or q+t1>N: continue
        if F(r,{t:d[q+t] for t in range(t0,t1+1)})!=d[n]: bad+=1
    # box invariance
    inv=all(F(r,{t:L for t in range(t0,t1+1)})<=U and F(r,{t:U for t in range(t0,t1+1)})>=L for r in range(tau))
    # induction needs q+t1<n and q>=q0 ; base region n<=N0
    N0=max(n for n in range(1,10*tau*(abs(t1)+abs(t0)+3)) if not ((n-1)//tau>=q0 and (n-1)//tau+t1<n)) if True else 0
    states=(U-L+1)**(t1-t0+1)
    return dict(a=a,A1=A1,kappa=kap,range=(L,U),window=(t0,t1),identity_mismatches=bad,box_invariant=inv,base_upto=N0,naive_state_bound=states)
if __name__=="__main__":
    N=int(sys.argv[1])
    forms=[(1,1),(1,2),(2,1),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),(2,3),(3,2),(3,1),(1,1,1),(1,1,1,1),(1,2,3),(3,2,1),(2,5),(5,2),(4,1),(1,1,4),(2,2,1),(7,3)]
    for a in forms:
        print(analyse(a,N),flush=True)
