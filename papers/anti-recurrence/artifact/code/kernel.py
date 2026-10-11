# Base-5 kernel exploration of d(n)=A_n-11n.  off=1: s(n)=d(n) with n>=1 indexing (s(0) undefined -> we use n>=1 only via shift)
# We study s_off(n) = d(n+off) for n>=0 (off=0 means s(0)=d(0) which we set via A_0 extrapolation; use off in {1} primarily)
import sys
N=10_000_000
D=open("d_%d.bin"%N,"rb").read()   # D[i]=d(i+1)
def seq(off):
    # s(n)=d(n+off-? ) ; s(n) defined for n>=0 as d(n+off) with d index starting at 1 -> need n+off>=1
    return D[off-1:] if off>=1 else None
MINLEN=int(sys.argv[1]) if len(sys.argv)>1 else 400
for off in (1,2,0):
    if off==0:
        s=bytes([0])+D   # s(0)=0 guess (A_0 := 0), s(n)=d(n)
    else:
        s=D[off-1:]
    # BFS over kernel; nodes = (e,r), sequence s[r::5^e]
    reps=[(0,0)]; keyseq={(0,0):s}
    frontier=[(0,0)]; lev=0; hist=[]
    newcount=1
    while frontier:
        nf=[]
        for (e,r) in frontier:
            for j in range(5):
                e2=e+1; r2=r+j*5**e
                t=s[r2::5**e2]
                if len(t)<MINLEN: continue
                found=None
                for (ee,rr) in reps:
                    u=keyseq[(ee,rr)]; L=min(len(u),len(t))
                    if u[:L]==t[:L]: found=(ee,rr); break
                if found is None:
                    reps.append((e2,r2)); keyseq[(e2,r2)]=t; nf.append((e2,r2))
        lev+=1; hist.append((lev,len(reps),len(nf)))
        frontier=nf
        if len(reps)>3000: hist.append("abort>3000"); break
    print("off",off,"MINLEN",MINLEN,"levels (level, total distinct, new at level):",hist)
