# Exact check of Prop 3.3 (L*,U*) and Remark 3.6 (T,T',o,W,P0) inequalities, with Fractions.
import itertools, random, math
from fractions import Fraction as Fr
def chk(a):
    k=len(a); tau=sum(a); K=k*tau; A1=sum((j+1)*x for j,x in enumerate(a))
    Phi=lambda r,x: A1-K-1-r+sum(a[j-1]*((k*r+j-1-x)//K) for j in range(1,k+1))
    c0=Fr(A1-K-1)+Fr(A1-tau,K)
    Ls=min(0, math.floor((c0*(1-Fr(1,k))-tau+1)/(1-Fr(1,k*k))), math.floor(k*(c0-1)+k*k*(tau-1)), math.floor(k*(c0-1)/(k+1)))
    Us=math.floor(c0-Fr(Ls,k))
    ok=(all(Phi(r,Ls)<=Us for r in range(tau)) and all(Phi(r,Us)>=Ls for r in range(tau)) and Us>=-k*(tau-1) and Ls<=0 and Ls<=Us)
    # envelope (eq Phibounds)
    env=all(c0-Fr(x,k)-tau < Phi(r,x) <= c0-Fr(x,k) for r in range(tau) for x in (Ls,Us,-K,0,7,-3*K))
    T=max(1,-(-Us//K)); Tp=1
    while K*Tp<=K-1-Ls: Tp+=1
    o=-2*T; W=2*T+2*Tp+1
    rem=((o-1)//tau - T + 1 >= o) and ((tau+o+W-3)//tau + Tp - 1 <= o+W-1) and o<=0<=o+W-1
    return ok,env,rem,(Ls,Us)
random.seed(5); forms=[(a,b) for a in range(1,31) for b in range(1,31)]+list(itertools.product(range(1,7),repeat=3))
forms+=[tuple(random.randint(1,random.choice([5,30,100])) for _ in range(random.randint(4,8))) for _ in range(300)]
forms+=[(200,1),(1,200),(1,)*8,(200,)*8]
bad=[f for f in forms if not all(chk(f)[:3])]
print('forms',len(forms),'failures',bad[:5])
