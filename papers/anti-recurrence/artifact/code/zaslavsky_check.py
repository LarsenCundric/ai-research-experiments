def antifib(N):
    A=[];used=set();B=[];x=1
    while len(A)<N:
        b=[]
        while len(b)<2:
            while x in used: x+=1
            b.append(x); used.add(x); x+=1
        s=sum(b); A.append(s); used.add(s)
    return A
A=antifib(3000)
pd=lambda n: (( (n+1)&-(n+1)).bit_length()-1)%2
print(A[:10], all(A[n-1]==5*n-2+pd(n-1) for n in range(1,3001)))
def uo(m):
    t=0
    while m&1: t+=1; m>>=1
    return t%2==1
lit=lambda n: 5*n+3 if n%2==0 else (5*n+4 if uo((n-1)//2) else 5*n+3)
sw=lambda n: 5*n+3 if n%2==0 else (5*n+3 if uo((n-1)//2) else 5*n+4)
print(sum(A[n]!=lit(n) for n in range(2999)), sum(A[n]!=sw(n) for n in range(2999)))
