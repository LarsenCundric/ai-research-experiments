# Check the derived recursion  d(5q+j) = F_j(d(q), d(q+1)),  q>=1, j=0..4  (and q=0, j=1..4 with virtual d(0)<=0)
# F_j(x,y) = -j-6 + [x<=2j-2] + 4[x<=2j-1] + [y<=2j-12] + 4[y<=2j-11]
N=10_000_000
D=open("d_%d.bin"%N,"rb").read()
d=[0]+[(b+128)%256-128 for b in D]   # d[n] for n>=1; d[0]=0 virtual
def F(j,x,y): return -j-6+(x<=2*j-2)+4*(x<=2*j-1)+(y<=2*j-12)+4*(y<=2*j-11)
bad=0
for n in range(1,N+1):
    q,j=divmod(n,5)
    if q+1>N: break
    if F(j,d[q],d[q+1])!=d[n]:
        bad+=1
        if bad<10: print("mismatch",n,q,j,d[q],d[q+1],d[n])
print("checked up to",n,"mismatches",bad)
