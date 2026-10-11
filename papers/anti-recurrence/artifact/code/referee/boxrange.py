import random
from closure import setup
def box(a):
    k,tau,K,A1=setup(a)
    Phi=lambda r,x: A1-K-1-r+sum(a[j-1]*((k*r+j-1-x)//K) for j in range(1,k+1))
    best=None
    for L in range(0,-2*K-5,-1):
        U=max([Phi(r,L) for r in range(tau)]+[-k*(tau-1)])
        if U>=L and all(Phi(r,U)>=L for r in range(tau)):
            if best is None or U-L<best[1]-best[0]: best=(L,U)
    return best
random.seed(1)
worst=(0,None); worstU=(-1e9,None); none=[]
forms=[(1,b) for b in range(1,80)]+[(b,1) for b in range(1,80)]+[(1,300),(300,1),(1,299,1),(150,1,150)]
forms+=[tuple(random.randint(1,random.choice([3,12,30])) for _ in range(random.randint(2,8))) for _ in range(300)]
for a in forms:
    k,tau,K,A1=setup(a); b=box(a)
    if b is None: none.append(a); continue
    L,U=b
    if L/K<worst[0]: worst=(L/K,a,L,U,K)
    if U/K>worstU[0]: worstU=(U/K,a,L,U,K)
print('forms',len(forms),'no box within L>=-2K-4:',none[:5]); print('min L/K',worst); print('max U/K',worstU)
