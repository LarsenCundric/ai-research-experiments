# Build a 5-DFAO (msd-first, leading zeros allowed) for d(n)=A_n-11n of the 4-rusty numbers, from the
# proved recursion d(5q+j)=F_j(d(q),d(q+1)) (q>=1), base values d(1..4)=-2,-3,-4,-5.
# State for n>=1 is v(n)=(d(n),d(n+1)); v(5q+j)=G_j(v(q)) for q>=1.  Extra start state 'S' for n=0.
import json,sys
def F(j,x,y): return -j-6+(x<=2*j-2)+4*(x<=2*j-1)+(y<=2*j-12)+4*(y<=2*j-11)
def G(j,v):
    x,y=v
    if j<4: return (F(j,x,y),F(j+1,x,y))
    return (F(4,x,y),F(0,y,None if False else 0))  # F_0 ignores 2nd arg (2*0-12<-6 and 2*0-11<-6)
# sanity: F_0 independent of y in range
assert all(F(0,x,y)==F(0,x,-99+0*y) or True for x in range(-6,2) for y in range(-6,2))
assert all(F(0,x,y)==F(0,x,1) for x in range(-6,2) for y in range(-6,2))
base={1:-2,2:-3,3:-4,4:-5,5:-1}
start_children={j:(base[j],base[j+1]) for j in range(1,5)}
# reachable states
states=set(start_children.values()); stack=list(states)
while stack:
    v=stack.pop()
    for j in range(5):
        w=G(j,v)
        if w not in states: states.add(w); stack.append(w)
states=sorted(states)
print("reachable pair-states:",len(states))
# Moore minimisation with output d=first coordinate; S separate (output 0 for n=0)
Q=['S']+states
out={'S':0}; out.update({v:v[0] for v in states})
delta={'S':{0:'S',**{j:start_children[j] for j in range(1,5)}}}
for v in states: delta[v]={j:G(j,v) for j in range(5)}
part={q:out[q] for q in Q}
while True:
    sig={q:(part[q],tuple(part[delta[q][j]] for j in range(5))) for q in Q}
    ids={s:i for i,s in enumerate(sorted(set(sig.values()),key=str))}
    newp={q:ids[sig[q]] for q in Q}
    if len(set(newp.values()))==len(set(part.values())): part=newp; break
    part=newp
print("minimal DFAO states:",len(set(part.values())))
# emit minimal DFAO
cls=sorted(set(part.values())); rep={c:next(q for q in Q if part[q]==c) for c in cls}
ren={c:i for i,c in enumerate(sorted(cls,key=lambda c:(c!=part['S'],c)))}
M={ren[c]:{"out":out[rep[c]],"next":[ren[part[delta[rep[c]][j]]] for j in range(5)]} for c in cls}
json.dump(M,open("dfao_min.json","w"),indent=0)
# verify against data
N=10_000_000; D=open("d_%d.bin"%N,"rb").read()
def run(n):
    s=ren[part['S']]
    digs=[]
    while n: digs.append(n%5); n//=5
    for dg in reversed(digs): s=M[s]["next"][dg]
    return M[s]["out"]
import random
bad=0
idx=list(range(1,200001))+random.sample(range(1,N+1),200000)
for n in idx:
    if run(n)!=(D[n-1]+128)%256-128: bad+=1
print("DFAO vs generated terms: checked",len(idx),"indices, mismatches",bad)
for i in sorted(M): print(i,M[i])
