# Generate the 4-rusty anti-recurrence (Fokkink-Joshi, linear form a=(1,4)):
# step n: b1<b2 = two smallest positive integers not yet used; A_n = b1 + 4*b2; mark b1,b2,A_n used.
# Saves d(n) = A_n - 11 n for n=1..N as int8 (d[0] corresponds to n=1), plus B1 (first b) offsets.
import sys, time
from array import array
N=int(sys.argv[1]); a1,a2=1,4
t=time.time()
used=bytearray(11*N+200); m=1
d=array('b',bytes(N)); e=array('i',bytes(4*N))  # e(n)=10*b1-22n
for n in range(1,N+1):
    while used[m]: m+=1
    b1=m; used[m]=1
    while used[m]: m+=1
    b2=m; used[m]=1
    x=a1*b1+a2*b2; used[x]=1
    d[n-1]=x-11*n; e[n-1]=10*b1-22*n
open("d_%d.bin"%N,"wb").write(d.tobytes()); open("e_%d.bin"%N,"wb").write(e.tobytes())
print("N",N,"time %.1fs"%(time.time()-t),"d range",min(d),max(d),"e range",min(e),max(e))
print("first d:",d[:30].tolist())
