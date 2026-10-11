"""For a linear form a (k=2 or 3), guess an msd-tau DFAO for W(n)=d(n)-L (Myhill-Nerode on data), verify it on all data,
and emit a Walnut word automaton + Walnut script that PROVES (independently of PROOF.md) that the DFAO-defined sequences
are the anti-recurrence (A,B) sequences: initial block, A increasing, B interleaved increasing, A,B disjoint, A u B = N,
A = sum a_j B_j.  By FJ Lemma 3 (uniqueness) this certifies A_n - kappa n = W(n)+L is tau-automatic."""
import sys, json, os
from recheck import gen_AB
def guess(s,tau,Lt,N):
    def sig(v):
        out=[]
        for l in range(Lt+1):
            base=v*tau**l
            if base+tau**l>N: return None
            out.extend(s[base+u] for u in range(tau**l))
        return tuple(out)
    states={}; trans={}; queue=[0]; sigs={}
    S0=sig(0); states[S0]=0; rep=[0]
    while queue:
        v=queue.pop(0); sid=states[sig(v)]
        if sid in trans: continue
        trans[sid]=[]
        for c in range(tau):
            w=v*tau+c; g=sig(w)
            if g is None: raise RuntimeError("not enough data")
            if g not in states: states[g]=len(states); rep.append(w); queue.append(w)
            trans[sid].append(states[g])
    out={states[g]:s[rep[states[g]]] for g in states}
    return trans,out
def closure_dfao(a,A1,Lobs,dlist,s,N):
    """DFAO built from the PROOF.md window recursion (box = minimal proved box), no guessing."""
    import math
    from recheck import min_box
    k=len(a); tau=sum(a); K=k*tau
    L,U=min_box(a); d=[None]+dlist
    t0=math.floor(-U/K)+1; t1=math.floor((K-1-L)/K)
    def F(r,get):
        v=A1-K-r-1+tau*(t0-1)
        for j in range(1,k+1):
            for t in range(t0,t1+1):
                if get(t)<=k*r+j-1-K*t: v+=a[j-1]
        return v
    lo,hi=t0-1,t1+1
    for W in range(1,60):
        o=next((o for o in range(-30,3) if all(((c+o+x-1)//tau)+lo>=o and ((c+o+x-1)//tau)+hi<=o+W-1 for c in range(tau) for x in range(W))),None)
        if o is not None and o<=0<=o+W-1: break
    def child(st,c):
        return tuple(F((c+o+x-1)%tau, lambda t,x=x: st[(c+o+x-1)//tau+t-o]) for x in range(W))
    P0=1
    while not all(tau*P0+c+o+x>=1 and P0+(c+o+x-1)//tau+lo>=1 and P0+(c+o+x-1)//tau+hi<tau*P0+c+o+x for c in range(tau) for x in range(W)): P0+=1
    win=lambda p: tuple(d[p+o+x] for x in range(W))
    # states: ('p',p) small, ('w',window)
    trans={}; out={}; todo=[('p',0)]
    while todo:
        q=todo.pop()
        if q in trans: continue
        if q[0]=='p':
            p=q[1]; out[q]=s[p]
            nxt=[('p',tau*p+c) if tau*p+c<P0 else ('w',win(tau*p+c)) for c in range(tau)]
        else:
            out[q]=q[1][-o]-L if False else q[1][-o]-Lobs
            nxt=[('w',child(q[1],c)) for c in range(tau)]
        trans[q]=nxt; todo+=nxt
    # Moore minimisation
    Q=list(trans); part={q:out[q] for q in Q}
    while True:
        sig={q:(part[q],tuple(part[t] for t in trans[q])) for q in Q}
        ids={}; newp={q:ids.setdefault(sig[q],len(ids)) for q in Q}
        if len(ids)==len(set(part.values())): part=newp; break
        part=newp
    start=part[('p',0)]; ren={}; order=[start]+[c for c in sorted(set(part.values())) if c!=start]
    ren={c:i for i,c in enumerate(order)}; rep={part[q]:q for q in Q}
    T2={ren[c]:[ren[part[t]] for t in trans[rep[c]]] for c in order}; O2={ren[c]:out[rep[c]] for c in order}
    print("  closure states",len(Q),"-> minimal",len(T2),"box",(L,U),"window W",W,"o",o,"P0",P0)
    return T2,O2
def run(trans,out,n,tau):
    st=0; digs=[]
    while n: digs.append(n%tau); n//=tau
    for dg in reversed(digs): st=trans[st][dg]
    return out[st]
def main(a,N,Lt,name):
    k=len(a); tau=sum(a); K=k*tau; kap=K+1; A1=sum((j+1)*c for j,c in enumerate(a))
    A,B=gen_AB(a,N); d=[A[i]-kap*(i+1) for i in range(N)]
    L=min(d); s=[0]+[x-L for x in d]      # s(0)=0 placeholder
    trans,out=closure_dfao(a,A1,L,d,s,N)
    bad=sum(run(trans,out,n,tau)!=s[n] for n in range(1,N+1))
    print(a,"states",len(trans),"verified on n<=%d mismatches"%N,bad)
    lines=[f"msd_{tau}",""]
    for q in sorted(trans):
        lines.append(f"{q} {out[q]}"); lines+= [f"{c} -> {t}" for c,t in enumerate(trans[q])]; lines.append("")
    open(os.path.join(os.environ.get("WALNUT_HOME","."),"Word Automata Library",f"{name}.txt"),"w").write("\n".join(lines))
    m=f"?msd_{tau}"; off=-L
    cmds=[f'def {name}a "{m} n>0 & s+{off}={kap}*n+{name}[n]";']
    if k==2:
        a1,a2=a
        cmds+=[f'def {name}b2 "{m} Es ${name}a(n,s) & ({tau}*t=s+{a1} | {tau}*t=s+{2*a1})";',
               f'def {name}b1 "{m} Es,t ${name}a(n,s) & ${name}b2(n,t) & {a1}*u+{a2}*t=s";']
        Bs=[f"{name}b1",f"{name}b2"]
        cmds+=[f'eval {name}_totB "{m} An (n>0) => ((Eu ${name}b1(n,u)) & (Et ${name}b2(n,t)))";',
               f'eval {name}_init "{m} ${name}b1(1,1) & ${name}b2(1,2) & ${name}a(1,{A1})";',
               f'eval {name}_incB "{m} An,u,t,v (${name}b1(n,u) & ${name}b2(n,t) & ${name}b1(n+1,v)) => (u<t & t<v)";',
               f'eval {name}_lin "{m} An,s,u,t (${name}a(n,s) & ${name}b1(n,u) & ${name}b2(n,t)) => s={a1}*u+{a2}*t";']
    else:
        assert a==(1,1,5)
        c3=f'(Es ${name}a(n,s) & (7*t=s+3 | 7*t=s+4 | 7*t=s+5))'
        cmds+=[f'def {name}b3 "{m} Es ${name}a(n,s) & (7*t=s+3 | 7*t=s+4 | 7*t=s+5)";',
               f'def {name}b2 "{m} Es,t ${name}a(n,s) & ${name}b3(n,t) & ((7*t=s+3 & u+1=t) | (7*t=s+4 & u+1=t) | (7*t=s+5 & u+2=t))";',
               f'def {name}b1 "{m} Es,t ${name}a(n,s) & ${name}b3(n,t) & ((7*t=s+3 & u+2=t) | (7*t=s+4 & u+3=t) | (7*t=s+5 & u+3=t))";']
        Bs=[f"{name}b1",f"{name}b2",f"{name}b3"]
        cmds+=[f'eval {name}_totB "{m} An (n>0) => ((Eu ${name}b1(n,u)) & (Eu ${name}b2(n,u)) & (Et ${name}b3(n,t)))";',
               f'eval {name}_init "{m} ${name}b1(1,1) & ${name}b2(1,2) & ${name}b3(1,3) & ${name}a(1,{A1})";',
               f'eval {name}_incB "{m} An,w,u,t,v (${name}b1(n,w) & ${name}b2(n,u) & ${name}b3(n,t) & ${name}b1(n+1,v)) => (w<u & u<t & t<v)";',
               f'eval {name}_lin "{m} An,s,w,u,t (${name}a(n,s) & ${name}b1(n,w) & ${name}b2(n,u) & ${name}b3(n,t)) => s=w+u+5*t";']
    anyB=" | ".join(f"${b}(m,x)" for b in Bs); anyBp=" | ".join(f"${b}(p,x)" for b in Bs)
    cmds+=[f'eval {name}_totA "{m} An (n>0) => (Es ${name}a(n,s))";',
           f'eval {name}_incA "{m} An,s,t (${name}a(n,s) & ${name}a(n+1,t)) => s<t";',
           f'eval {name}_cover "{m} Ax (x>0) => (Em (${name}a(m,x) | {anyB}))";',
           f'eval {name}_disj "{m} ~(Ex,m,p (${name}a(m,x) & ({anyBp})))";',
           f'eval {name}_ctrl_false "{m} ${name}a(1,{A1+1})";']
    if k==2:
        cmds.append(f'eval {name}_disjB "{m} ~(Ex,m,p (${name}b1(m,x) & ${name}b2(p,x)))";')
    open(f"walnut_{name}.txt","w").write("\n".join(cmds)+"\n")
if __name__=="__main__":
    for spec in sys.argv[2:]:
        a,name=spec.split(":"); main(tuple(map(int,a.split(","))),int(sys.argv[1]),3,name)
