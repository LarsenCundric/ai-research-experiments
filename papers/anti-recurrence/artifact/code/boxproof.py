# General boundedness ("weak Clergyman") via an explicit invariant box.
# Claim (see notes): for any box [L,U] with U >= -k(tau-1), max_r Phi(r,L) <= U and min_r Phi(r,U) >= L,
#   where Phi(r,x) = A1 - K - 1 - r + sum_j a_j floor((k r + j - 1 - x)/K),  K = k*tau,
# every n satisfies L <= A_n - (K+1) n <= U   (induction on n; no base cases needed).
import sys, random
from general import gen
def Phi(a,r,x):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*c for j,c in enumerate(a))
    return A1-K-1-r+sum(a[j-1]*((k*r+j-1-x)//K) for j in range(1,k+1))
def best_box(a):
    k=len(a); tau=sum(a); best=None
    for L in range(0,-2000,-1):
        U=max(max(Phi(a,r,L) for r in range(tau)), -k*(tau-1))
        if U<L: continue
        if min(Phi(a,r,U) for r in range(tau))>=L:
            if best is None or U-L<best[1]-best[0]: best=(L,U)
    return best
if __name__=="__main__":
    N=int(sys.argv[1]); random.seed(1)
    forms=[(1,1),(1,2),(2,1),(1,3),(1,4),(1,5),(1,10),(1,20),(2,3),(7,3),(1,1,1),(1,1,1,1),(1,2,3),(3,2,1),(9,1),(1,9)]
    forms+=[tuple(random.randint(1,9) for _ in range(random.randint(2,5))) for _ in range(24)]
    allok=True
    for a in forms:
        tau=sum(a); k=len(a); K=k*tau
        box=best_box(a)
        A=gen(a,N); d=[A[i]-(K+1)*(i+1) for i in range(N)]
        lo,hi=min(d),max(d); ok= box is not None and box[0]<=lo and hi<=box[1]
        allok&=ok
        print(a,"proved box",box,"observed",(lo,hi),"OK" if ok else "VIOLATION",flush=True)
    print("ALL OK" if allok else "SOME VIOLATION")
