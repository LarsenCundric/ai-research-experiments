/* Referee pass 2: independent checks of Lemma 3.4 (universal box), Theorem B (two-term recursion, all q>=0, d(0)=0)
   and Theorem C (msd DFAO on triples). Generator rewritten from the FJ definition (queue-based mex), not shared with authors.
   Usage: arseq2 N a1..ak   Output one line; exit 1 on any failure. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef long long ll;
static ll fdiv(ll a, ll b){ ll q=a/b; if((a%b!=0)&&((a<0)!=(b<0))) q--; return q; }
int k; ll a[64], S[66], tau, K, A1;
ll Phi(ll r, ll x){ ll s=A1-K-1-r; for(int j=1;j<=k;j++) s+=a[j-1]*fdiv(k*r+j-1-x,K); return s; }
/* sum_j a_j [y <= kr+j-1]  =  sum over j >= y-kr+1 */
static inline ll suf(ll t){ if(t<1) t=1; if(t>k+1) return 0; return S[t]; }
static inline ll G(ll r, ll y0, ll y1){ return A1-K-1-r-tau + suf(y0-k*r+1) + suf(y1+K-k*r+1); }
static int *d; ll N;
static inline void H(ll c, const ll *V, ll *out){ /* V=(d(m-1),d(m),d(m+1)) -> V(tau m + c) */
  for(int e=-1;e<=1;e++){ ll mm=c+e-1; ll r, i0;
    if(mm>=0){ r=mm; i0=1; } else { r=tau+mm; i0=0; }
    out[e+1]=G(r,V[i0],V[i0+1]); } }
/* hash set of triples */
static uint64_t *hs; static size_t HS; static ll nst=0;
static int insert(uint64_t key){ size_t i=(key*0x9E3779B97F4A7C15ULL)>>20 & (HS-1); key|=1ULL<<63;
  while(hs[i]){ if(hs[i]==key) return 0; i=(i+1)&(HS-1);} hs[i]=key; nst++; return 1; }
int main(int argc,char**argv){
  N=atoll(argv[1]); k=argc-2; tau=0; A1=0;
  for(int j=0;j<k;j++){a[j]=atoll(argv[j+2]); tau+=a[j]; A1+=(j+1)*a[j];}
  K=k*tau; S[k+1]=0; for(int j=k;j>=1;j--) S[j]=S[j+1]+a[j-1];
  ll *A=malloc(sizeof(ll)*(N+2)); d=malloc(sizeof(int)*(N+3));
  ll x=1, front=0; int bad=0;
  for(ll n=0;n<N;n++){ ll s=0, last=0;
    for(int j=0;j<k;j++){ while(front<n && A[front]==x){x++;front++;} last=x; s+=a[j]*x; x++; }
    A[n]=s; if(n>0 && A[n]<=A[n-1]) bad=1; if(s<=last) bad=1; }
  d[0]=0; ll dmin=1LL<<60,dmax=-(1LL<<60);
  for(ll n=1;n<=N;n++){ ll v=A[n-1]-(K+1)*n; d[n]=(int)v; if(v<dmin)dmin=v; if(v>dmax)dmax=v; }
  /* Lemma 3.4: U4 = max(-k(tau-1), max_r Phi(r,-K)); check (i)-(iv), U4<=tau-k, d in [-K,U4] */
  ll U4=-k*(tau-1); for(ll r=0;r<tau;r++){ll v=Phi(r,-K); if(v>U4)U4=v;}
  int l4=1; for(ll r=0;r<tau;r++) if(Phi(r,U4)< -K) l4=0;           /* (ii) */
  if(!(U4<=tau-k)) l4=0; if(!(-K<U4)) l4=0;
  int inbox = (dmin>=-K && dmax<=U4);
  /* Theorem B for all q>=0 with tau q + r + 1 <= N and q+1 <= N */
  ll mB=0, cB=0;
  for(ll n=1;n<=N;n++){ ll q=(n-1)/tau, r=(n-1)%tau; if(q+1>N) continue; cB++; if(G(r,d[q],d[q+1])!=d[n]) mB++; }
  /* Theorem C: eq (H) V(tau m+c)=H_c(V(m)) for all m>=1 with indices in range  */
  ll mH=0;
  for(ll m=1; tau*m+tau <= N; m++){ ll V[3]={d[m-1],d[m],d[m+1]}, o[3];
    for(ll c=0;c<tau;c++){ H(c,V,o); ll n=tau*m+c; if(o[0]!=d[n-1]||o[1]!=d[n]||o[2]!=d[n+1]) mH++; } }
  /* reachable-state count of the Theorem C automaton (closure from V(1..tau-1)), capped */
  ll W=K+tau-k+1; HS=1<<22; hs=calloc(HS,8); ll cap=3000000; int capped=0;
  ll *queue=malloc(sizeof(ll)*3*(cap+tau+5)); ll qh=0,qt=0;
  #define KEY(v) ((uint64_t)((v)[0]+K) + (uint64_t)((v)[1]+K)*(uint64_t)(W+2) + (uint64_t)((v)[2]+K)*(uint64_t)(W+2)*(uint64_t)(W+2))
  int outside=0; ll emin=1LL<<60, emax=-(1LL<<60);
  for(ll c=1;c<tau && c+1<=N;c++){ ll V[3]={d[c-1],d[c],d[c+1]}; if(insert(KEY(V))){ memcpy(&queue[3*qt],V,24); qt++; } }
  while(qh<qt){ ll V[3]; memcpy(V,&queue[3*qh],24); qh++;
    for(int t=0;t<3;t++){ if(V[t]<-K||V[t]>tau-k) outside=1; if(t==1){ if(V[1]<emin)emin=V[1]; if(V[1]>emax)emax=V[1]; } }
    for(ll c=0;c<tau;c++){ ll o[3]; H(c,V,o); if(insert(KEY(o))){ if(qt>=cap){capped=1;break;} memcpy(&queue[3*qt],o,24); qt++; } }
    if(capped) break; }
  double bound=2.0+(double)W*W*W;
  printf("a=(");for(int j=0;j<k;j++)printf("%s%lld",j?",":"",a[j]);
  printf(") k=%d tau=%lld K=%lld N=%lld gen_bad=%d obs=[%lld,%lld] L4=[%lld,%lld] tau-k=%lld lemma4_ok=%d inbox=%d minGapToMinusK=%lld B_chk=%lld B_mism=%lld H_mism=%lld states=%lld%s outside=%d exact=[%lld,%lld] bound=%.3g\n",
    k,tau,K,N,bad,dmin,dmax,-K,U4,tau-k,l4,inbox,dmin+K,cB,mB,mH,nst+1,capped?"(capped)":"",outside,emin,emax,bound);
  return (bad||!l4||!inbox||mB||mH||outside)?1:0;
}
