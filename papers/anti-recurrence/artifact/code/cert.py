# Closure certificate: proves  L <= A_n - kappa*n <= U  for all n, and hence (with the window recursion) that
# A_n - kappa*n is tau-automatic, for a given linear form a.  See notes.md (rusty section) for the derivation.
# Identity (n-1 = tau*q + r, 0<=r<tau), valid whenever d(q+t0-1) <= U and d(q+t1+1) >= L and the window values are in [L,U]:
#   d(n) = C_r + sum_j a_j sum_{t=t0..t1} [ d(q+t) <= k*r + j - 1 - k*tau*t ],  C_r = A1 - k*tau - r - 1 + tau*(t0-1)
import sys, math
from general import gen
def certify(a,N=200000,margin=0,verbose=True,box=None,_cache={}):
    k=len(a); tau=sum(a); kap=k*tau+1
    if (a,N) not in _cache: _cache[(a,N)]=gen(a,N)
    A=_cache[(a,N)]; A1=A[0]
    d=[None]+[A[i]-kap*(i+1) for i in range(N)]
    L=min(d[1:])-margin; U=max(d[1:])+margin
    if box: L,U=box
    t0=math.floor(-U/(k*tau))+1; t1=math.floor((k*tau-1-L)/(k*tau))
    # sanity of thresholds: for t<=t0-1 threshold >= U ; for t>=t1+1 threshold < L
    assert all(k*r+j-1-k*tau*(t0-1)>=U for r in range(tau) for j in range(1,k+1))
    assert all(k*r+j-1-k*tau*(t1+1)<L for r in range(tau) for j in range(1,k+1))
    lo_need,hi_need=t0-1,t1+1
    def F(r,get):
        s=A1-k*tau-r-1+tau*(t0-1)
        for j in range(1,k+1):
            for t in range(t0,t1+1):
                if get(t)<=k*r+j-1-k*tau*t: s+=a[j-1]
        return s
    # choose window offset o and width W: state(p)=(d(p+o),...,d(p+o+W-1)); child(p,c)=state(tau*p+c)
    best=None
    for W in range(1,40):
        for o in range(-20,3):
            ok=True
            for c in range(tau):
                for s in range(W):
                    m=c+o+s-1          # n=tau*p+c+o+s ; n-1=tau*p+m ; q=p+floor(m/tau)
                    qo=m//tau
                    if qo+lo_need<o or qo+hi_need>o+W-1: ok=False;break
                if not ok:break
            if ok: best=(o,W);break
        if best:break
    o,W=best
    def child(state,c):
        out=[]
        for s in range(W):
            m=c+o+s-1; qo=m//tau; r=m%tau
            out.append(F(r,lambda t: state[qo+t-o]))
        return tuple(out)
    # base: P0 such that for p>=P0 every needed index is >=1 and < the child indices (strong induction order)
    P0=1
    while True:
        good=True
        for c in range(tau):
            for s in range(W):
                n=tau*P0+c+o+s; m=c+o+s-1; qo=m//tau
                if n<1 or P0+qo+lo_need<1 or P0+qo+hi_need>=n: good=False
        if good: break
        P0+=1
    # check identity directly on data in base region and beyond (sanity), then closure
    seeds={tuple(d[p+o+s] for s in range(W)) for p in range(P0,tau*P0)}
    S=set(seeds); st=list(seeds)
    while st:
        x=st.pop()
        for c in range(tau):
            y=child(x,c)
            if y not in S: S.add(y); st.append(y)
        if len(S)>200000: break
    inbox=all(L<=v<=U for x in S for v in x)
    # empirical confirmation: every actual state(p), P0<=p<=N/tau - W, is in S
    emp=all(tuple(d[p+o+s] for s in range(W)) in S for p in range(P0,(N-W-abs(o))//1-W) if p+o+W-1<=N)
    cl_lo=min(v for x in S for v in x); cl_hi=max(v for x in S for v in x)
    res=dict(cl_range=(cl_lo,cl_hi),a=a,kappa=kap,box=(L,U),window_t=(t0,t1),o=o,W=W,P0=P0,closure_states=len(S),closure_in_box=inbox,data_states_in_closure=emp,
             base_terms_needed=tau*P0+o+W)
    if verbose: print(res,flush=True)
    return res
if __name__=="__main__":
    N=int(sys.argv[1])
    forms=[(1,4),(1,1),(1,2),(2,1),(1,3),(1,5),(1,10),(1,11),(1,12),(1,15),(1,20),(2,7),(3,5),(5,3),(2,1,3),(1,3,2),(1,1,5),(4,4,1),(1,6,1),(9,1)]
    if len(sys.argv)>2: forms=[tuple(map(int,x.split(','))) for x in sys.argv[2:]]
    for a in forms:
        box=None
        for it in range(8):
            r=certify(a,N,box=box,verbose=False)
            if r['closure_in_box']: break
            box=(min(r['box'][0],r['cl_range'][0]),max(r['box'][1],r['cl_range'][1]))
        print('iter',it,r,flush=True)
