/* Independent generator + checker for linear anti-recurrences (Fokkink-Joshi definition).
   Written from scratch for the referee review; does not reuse gen.py/recheck.py.
   Usage: arseq N a1 a2 ... ak   [env DUMP=file writes d(1..N) as int8 text]
   Checks:
     (G) complementarity/increase sanity of the generated A,B
     (S1) B_m = m + #{i: A_i < B_m}  and identity (*)
     (S2) own computation of a box (L,U) satisfying (i)-(iv); d in box; Phi(r,U)<=d(n)<=Phi(r,L)
     (S3) window recursion d(tau q + r + 1) = G_r(d(q-T+1..q+T'-1)) for q>=T
     (W) empirical window-map determinism: V(tau p + c) is a function of V(p)  (hash table)  */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef long long ll;
static ll fdiv(ll a, ll b){ ll q=a/b; if((a%b!=0)&&((a<0)!=(b<0))) q--; return q; }
int k; ll a[16], tau, K, kap, A1;
ll Phi(ll r, ll x){ ll s=A1-K-1-r; for(int j=1;j<=k;j++) s+=a[j-1]*fdiv(k*r+j-1-x,K); return s; }
int main(int argc,char**argv){
  ll N=atoll(argv[1]); k=argc-2; tau=0; A1=0;
  for(int j=0;j<k;j++){a[j]=atoll(argv[j+2]); tau+=a[j]; A1+=(j+1)*a[j];}
  K=k*tau; kap=K+1;
  ll *A=malloc(sizeof(ll)*(N+2)); ll *B=malloc(sizeof(ll)*(k*N+2)); int *d=malloc(sizeof(int)*(N+2));
  /* generation: B's are the mex of numbers not yet used, A_n = sum a_j B_{k(n-1)+j} */
  ll x=1; ll front=0; ll nb=0; int bad=0;
  for(ll n=0;n<N;n++){
    ll s=0;
    for(int j=0;j<k;j++){
      while(front<n && A[front]==x){x++;front++;}
      if(front<n && A[front]<x){bad=1;}
      B[nb++]=x; s+=a[j]*x; x++;
    }
    A[n]=s;
    if(n>0 && A[n]<=A[n-1]) bad=1;
    if(A[n]<x) bad=1;           /* A_n must exceed its own block */
  }
  ll dmin=1LL<<60,dmax=-(1LL<<60);
  for(ll n=1;n<=N;n++){ ll v=A[n-1]-kap*n; d[n]=(int)v; if(v<dmin)dmin=v; if(v>dmax)dmax=v; }
  /* gap set of A */
  /* (S1) identity: walk B with pointer into A */
  ll mism1=0, mismStar=0; { ll p=0; /* p = #{i: A_i < B_m} */
    ll *cm=malloc(sizeof(ll)*(k*N+2));
    for(ll m=1;m<=k*N;m++){ while(p<N && A[p]<B[m-1]) p++; cm[m]=p; if(B[m-1]!=m+p) mism1++; }
    for(ll n=1;n<=N;n++){ ll s=A1-K-n; for(int j=1;j<=k;j++) s+=a[j-1]*cm[k*(n-1)+j]; if(s!=d[n]) mismStar++; }
    free(cm);}
  /* (S2) own box: scan L downward, U := max(max_r Phi(r,L), -k(tau-1)); require (ii) and L<=U; keep narrowest */
  ll bestL=1,bestU=0; int found=0;
  for(ll L=0; L>=-20000; L--){
    ll U=-k*(tau-1); for(ll r=0;r<tau;r++){ll v=Phi(r,L); if(v>U)U=v;}
    if(U<L) continue;
    int ok=1; for(ll r=0;r<tau;r++) if(Phi(r,U)<L){ok=0;break;}
    if(ok && (!found || U-L<bestU-bestL)){bestL=L;bestU=U;found=1;}
    if(found && L < bestL-3000) break;
  }
  ll viol2=0;
  for(ll n=1;n<=N;n++){ ll r=(n-1)%tau; if(!(d[n]>=bestL && d[n]<=bestU && Phi(r,bestU)<=d[n] && d[n]<=Phi(r,bestL))) viol2++; }
  /* (S3) window recursion */
  ll L=bestL,U=bestU; ll T=1; while(K*T<U) T++; ll Tp=1; while(K*Tp<=K-1-L) Tp++;
  ll mism3=0, cnt3=0;
  for(ll n=1;n<=N;n++){ ll q=(n-1)/tau, r=(n-1)%tau; if(q<T || q+Tp-1>N) continue; cnt3++;
    ll s=A1-K-1-r-tau*T;
    for(int j=1;j<=k;j++){ ll u=k*r+j-1; for(ll t=-T+1;t<=Tp-1;t++) if(d[q+t]<=u-K*t) s+=a[j-1]; }
    if(s!=d[n]) mism3++; }
  /* (W) window determinism, using o and W from the proof's inequalities */
  ll o=0; while(!(fdiv(o-1,tau)-T+1>=o)) o--;
  ll W=1; while(!(fdiv(tau+o+W-3,tau)+Tp-1<=o+W-1 && o+W-1>=0)) W++;
  /* hash V(p) -> id; store successor ids for each c */
  ll P0=T+2-o+2; ll maxp=(N-(o+W))/tau - 1; ll nwin=0, conflicts=0;
  if(maxp>P0){
    size_t HS=1<<22; uint64_t *hk=calloc(HS,8); int32_t *hv=malloc(HS*4); int32_t *succ=NULL; ll cap=1<<16; succ=malloc(sizeof(int32_t)*cap*tau); 
    #define WHASH(p) ({uint64_t h=1469598103934665603ULL; for(ll i=0;i<W;i++){h^=(uint64_t)(d[(p)+o+i]+128); h*=1099511628211ULL;} h|1;})
    /* exact compare via storing representative p */
    ll *rep=malloc(sizeof(ll)*cap);
    for(ll p=P0;p<=maxp;p++){
      ll ids[64]; ll pp[65]; pp[0]=p; for(ll c=0;c<tau&&c<64;c++) pp[c+1]=tau*p+c;
      for(int z=0; z<=tau && z<65; z++){
        ll q=pp[z]; if(q+o+W-1>N){ids[z]=-1;continue;} uint64_t h=WHASH(q); size_t i=h&(HS-1);
        while(1){ if(hk[i]==0){ hk[i]=h; if(nwin>=cap){cap*=2; rep=realloc(rep,sizeof(ll)*cap); succ=realloc(succ,sizeof(int32_t)*cap*tau);} 
                    hv[i]=nwin; rep[nwin]=q; for(ll c=0;c<tau;c++) succ[nwin*tau+c]=-1; nwin++; break;}
                  if(hk[i]==h){ ll r0=rep[hv[i]]; int eq=1; for(ll t=0;t<W;t++) if(d[r0+o+t]!=d[q+o+t]){eq=0;break;} if(eq) break; }
                  i=(i+1)&(HS-1); }
        ids[z]=hv[i];
      }
      for(ll c=0;c<tau;c++){ if(ids[c+1]<0) continue; int32_t *sl=&succ[ids[0]*tau+c]; if(*sl<0) *sl=ids[c+1]; else if(*sl!=ids[c+1]) conflicts++; }
    }
  }
  int a1b = (A1 <= (k-1)*tau+2);
  printf("a=(");for(int j=0;j<k;j++)printf("%s%lld",j?",":"",a[j]);
  printf(") N=%lld tau=%lld A1=%lld A1bdd=%d gen_bad=%d obs=[%lld,%lld] box=[%lld,%lld] tight=%d S1=%lld star=%lld S2viol=%lld T=%lld Tp=%lld S3chk=%lld S3mism=%lld o=%lld W=%lld windows=%lld Wconfl=%lld\n",
    N,tau,A1,a1b,bad,dmin,dmax,bestL,bestU,(dmin==bestL&&dmax==bestU),mism1,mismStar,viol2,T,Tp,cnt3,mism3,o,W,nwin,conflicts);
  char*dump=getenv("DUMP"); if(dump){FILE*f=fopen(dump,"w"); for(ll n=1;n<=N;n++) fprintf(f,"%d\n",d[n]); fclose(f);}
  return (bad||mism1||mismStar||viol2||mism3||conflicts)?1:0;
}
