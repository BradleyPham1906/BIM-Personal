/* V173 research experiment: classification methods, written here from the papers and specs
   (Fisher 1958 / Jenks 1977 as restated by Wang & Song 2011; R's pretty(); mapclassify's and
   QGIS's definitions read as text). ES5 style, no dependencies. Not app code.
   Convention: every classifier returns the UPPER bound of each class, ascending, last = max
   (mapclassify's convention). A value v is in class j when bins[j-1] < v <= bins[j]. */
'use strict';

function cleanSorted(values){
  var out=[],i,v;
  for(i=0;i<values.length;i++){
    v=values[i];
    if(v===null||v===undefined||v===''||typeof v==='boolean')continue;
    v=+v;
    if(isFinite(v))out.push(v);
  }
  out.sort(function(a,b){return a-b;});
  return out;
}
function distinctCount(x){var c=0,i;for(i=0;i<x.length;i++)if(i===0||x[i]!==x[i-1])c++;return c;}

/* prefix sums of (x - shift) and its square; shift = median for numeric stability */
function prefix(x){
  var n=x.length,S=new Float64Array(n+1),Q=new Float64Array(n+1),sh=x[Math.floor(n/2)],i,d;
  for(i=0;i<n;i++){d=x[i]-sh;S[i+1]=S[i]+d;Q[i+1]=Q[i]+d*d;}
  return {S:S,Q:Q};
}
function ssq(P,j,i){ /* sum of squared deviations of x[j..i] about their mean, inclusive, 0-based */
  var c=i-j+1,s=P.S[i+1]-P.S[j],q=P.Q[i+1]-P.Q[j],r=q-s*s/c;
  return r<0?0:r;
}
function backtrack(x,B,k){
  var bins=new Array(k),i=x.length-1,m;
  for(m=k-1;m>=0;m--){bins[m]=x[i];if(m>0)i=B[m][i]-1;}
  return bins;
}

/* Fisher (1958) exact optimum, plain dynamic programme: O(k n^2) time, O(k n) memory.
   Ties: strict '<' keeps the smallest start index j for the last class. */
function fisherJenksDP(values,k){
  var x=cleanSorted(values),n=x.length,u,P,D,B,m,i,j,best,bj,c,iFrom;
  if(!n)return {bins:[],k:0,x:x};
  u=distinctCount(x);
  if(k>u)k=u;
  if(k<=1)return {bins:[x[n-1]],k:1,x:x};
  P=prefix(x);D=[];B=[];
  for(m=0;m<k;m++){D.push(new Float64Array(n));B.push(new Int32Array(n));}
  for(i=0;i<n;i++){D[0][i]=ssq(P,0,i);B[0][i]=0;}
  for(m=1;m<k;m++){
    iFrom=(m===k-1)?n-1:m;          /* the last row needs only i=n-1 */
    for(i=iFrom;i<n;i++){
      best=Infinity;bj=m;
      for(j=m;j<=i;j++){c=D[m-1][j-1]+ssq(P,j,i);if(c<best){best=c;bj=j;}}
      D[m][i]=best;B[m][i]=bj;
    }
  }
  return {bins:backtrack(x,B,k),k:k,x:x,sdcm:D[k-1][n-1]};
}

/* The same optimum, divide and conquer on the monotone argmin (the idea of Ckmeans.1d.dp 3.4.6):
   O(k n log n). Relies on B[m][i] being non-decreasing in i. */
function fisherJenksDC(values,k){
  var x=cleanSorted(values),n=x.length,u,P,D,B,m;
  if(!n)return {bins:[],k:0,x:x};
  u=distinctCount(x);
  if(k>u)k=u;
  if(k<=1)return {bins:[x[n-1]],k:1,x:x};
  P=prefix(x);D=[];B=[];
  for(m=0;m<k;m++){D.push(new Float64Array(n));B.push(new Int32Array(n));}
  for(var i0=0;i0<n;i0++){D[0][i0]=ssq(P,0,i0);}
  function fill(m,lo,hi,jlo,jhi){
    /* iterative stack instead of recursion: no deep call stacks on old browsers */
    var st=[[lo,hi,jlo,jhi]],t,mid,a,b,j,c,best,bj;
    while(st.length){
      t=st.pop();if(t[0]>t[1])continue;
      mid=(t[0]+t[1])>>1;a=Math.max(m,t[2]);b=Math.min(mid,t[3]);
      best=Infinity;bj=a;
      for(j=a;j<=b;j++){c=D[m-1][j-1]+ssq(P,j,mid);if(c<best){best=c;bj=j;}}
      D[m][mid]=best;B[m][mid]=bj;
      st.push([t[0],mid-1,t[2],bj]);st.push([mid+1,t[1],bj,t[3]]);
    }
  }
  for(m=1;m<k;m++){
    if(m===k-1)fill(m,n-1,n-1,m,n-1);
    else fill(m,m,n-1,m,n-1);
  }
  return {bins:backtrack(x,B,k),k:k,x:x,sdcm:D[k-1][n-1]};
}

/* quantile of a sorted array, Hyndman & Fan type 7 (R default, numpy linear, QGIS, mapclassify via scipy) */
function q7(x,p){var h=(x.length-1)*p,lo=Math.floor(h);if(lo>=x.length-1)return x[x.length-1];return x[lo]+(h-lo)*(x[lo+1]-x[lo]);}
function quantileBins(values,k,type){
  var x=cleanSorted(values),n=x.length,b=[],i,v,out=[];
  if(!n)return {bins:[],x:x};
  for(i=1;i<k;i++){
    if(type==='rank'){v=x[Math.round(i*n/k+0.49)-1];}   /* geostats' nearest-rank rule */
    else v=q7(x,i/k);
    b.push(v);
  }
  b.push(x[n-1]);
  for(i=0;i<b.length;i++)if(!out.length||b[i]!==out[out.length-1])out.push(b[i]);  /* collapse duplicates */
  return {bins:out,x:x,requested:k};
}
function equalIntervalBins(values,k){
  var x=cleanSorted(values),n=x.length,lo,hi,w,b=[],i;
  if(!n)return {bins:[],x:x};
  lo=x[0];hi=x[n-1];
  if(lo===hi)return {bins:[hi],x:x};
  w=(hi-lo)/k;
  for(i=1;i<k;i++)b.push(lo+w*i);
  b.push(hi);
  return {bins:b,x:x};
}
function meanSd(x,ddof){
  var n=x.length,m=0,s=0,i;for(i=0;i<n;i++)m+=x[i];m/=n;
  for(i=0;i<n;i++)s+=(x[i]-m)*(x[i]-m);
  return {mean:m,sd:Math.sqrt(s/(n-ddof))};
}
/* mapclassify StdMean: cuts at mean + s*multiple, sample sd (ddof=1), max appended */
function stdMeanBins(values,multiples){
  var x=cleanSorted(values),ms=meanSd(x,1),b=[],i;
  for(i=0;i<multiples.length;i++)b.push(ms.mean+ms.sd*multiples[i]);
  if(b[b.length-1]<x[x.length-1])b.push(x[x.length-1]);
  return {bins:b,x:x,mean:ms.mean,sd:ms.sd};
}
/* interval-of-a-fraction-of-sd classing within [min,max]; centre='break' puts the mean on a break,
   centre='class' puts a class of width f*sd centred on the mean. Both conventions exist (geostats
   uses 'class' for odd k and 'break' for even k). */
function stdIntervalBins(values,f,centre,ddof){
  var x=cleanSorted(values),ms=meanSd(x,ddof),w=ms.sd*f,lo=x[0],hi=x[x.length-1],b=[],t,start;
  if(!(w>0))return {bins:[hi],x:x};
  start=centre==='class'?ms.mean-w/2:ms.mean;
  t=start-Math.floor((start-lo)/w)*w;  /* first break at or above min on the lattice */
  if(t<=lo)t+=w;
  for(;t<hi;t+=w)b.push(t);
  b.push(hi);
  return {bins:b,x:x,mean:ms.mean,sd:ms.sd};
}
/* log-equal intervals (geostats 'geometric progression'); positive data only */
function logEqualBins(values,k){
  var x=cleanSorted(values),lo=x[0],hi=x[x.length-1],b=[],i,a,c;
  if(!(lo>0))return {bins:null,x:x,error:'needs all values > 0'};
  a=Math.log(lo);c=(Math.log(hi)-a)/k;
  for(i=1;i<k;i++)b.push(Math.exp(a+c*i));
  b.push(hi);
  return {bins:b,x:x};
}
/* R's pretty() (src/appl/pretty.c, R 4.x defaults), re-expressed: returns the tick sequence */
function rPretty(lo,up,ndiv){
  var h=1.5,h5=0.5+1.5*h,minN=Math.floor(ndiv/3),shrink=0.75,eps=1e-10,dx=up-lo,cell,U,small,base,unit,ns,nu,k,out=[],i;
  if(dx===0&&up===0){cell=1;small=true;}
  else{
    cell=Math.max(Math.abs(lo),Math.abs(up));
    U=1+((h5>=1.5*h+0.5)?1/(1+h):1.5/(1+h5));
    U*=Math.max(1,ndiv)*2.220446049250313e-16;
    small=dx<cell*U*3;
  }
  if(small){if(cell>10)cell=9+cell/10;cell*=shrink;if(minN>1)cell/=minN;}
  else{cell=dx;if(ndiv>1)cell/=ndiv;}
  if(cell<2.2250738585072014e-308*Math.pow(2,-20))cell=2.2250738585072014e-308;
  base=Math.pow(10,Math.floor(Math.log(cell)/Math.LN10));
  unit=base;
  if((U=2*base)-cell<h*(cell-unit)){unit=U;
    if((U=5*base)-cell<h5*(cell-unit)){unit=U;
      if((U=10*base)-cell<h*(cell-unit))unit=U;}}
  ns=Math.floor(lo/unit+eps);nu=Math.ceil(up/unit-eps);
  while(ns*unit>lo+eps*unit)ns--;
  while(nu*unit<up-eps*unit)nu++;
  k=Math.floor(0.5+nu-ns);
  if(k<minN){k=minN-k;if(lo===0&&ns===0&&up!==0)nu+=k;else if(up===0&&nu===0&&lo!==0)ns-=k;else if(ns>=0){nu+=Math.floor(k/2);ns-=Math.floor(k/2)+k%2;}else{ns-=Math.floor(k/2);nu+=Math.floor(k/2)+k%2;}}
  for(i=ns;i<=nu;i++)out.push(+(i*unit).toPrecision(15));
  return out;
}
/* mapclassify's own _pretty (a different, simpler rule) */
function mcPrettyNumber(x,rounded){
  var e=Math.floor(Math.log(x)/Math.LN10),f=x/Math.pow(10,e),nf;
  if(rounded)nf=f<1.5?1:f<3?2:f<7?5:10;else nf=f<=1?1:f<=2?2:f<=5?5:10;
  return nf*Math.pow(10,e);
}
function mcPretty(values,k){
  var x=cleanSorted(values),lo=x[0],hi=x[x.length-1],rg=mcPrettyNumber(hi-lo,false),d=mcPrettyNumber(rg/(k-1),true),a=Math.floor(lo/d)*d,b=Math.ceil(hi/d)*d,out=[],t;
  for(t=a;t<b+0.5*d;t+=d)out.push(+t.toPrecision(15));
  return out;
}

function assign(bins,v){var lo=0,hi=bins.length-1,mid;if(v>bins[hi])return -1;while(lo<hi){mid=(lo+hi)>>1;if(v<=bins[mid])hi=mid;else lo=mid+1;}return lo;}
function counts(x,bins){var c=[],i,j;for(i=0;i<bins.length;i++)c.push(0);for(i=0;i<x.length;i++){j=assign(bins,x[i]);if(j>=0)c[j]++;}return c;}
/* goodness of variance fit: 1 - SDCM/SDAM */
function gvf(x,bins){
  var n=x.length,m=0,sdam=0,sdcm=0,i,j,cls=[],s,c,mu;
  for(i=0;i<n;i++)m+=x[i];m/=n;
  for(i=0;i<n;i++)sdam+=(x[i]-m)*(x[i]-m);
  for(i=0;i<bins.length;i++)cls.push([]);
  for(i=0;i<n;i++){j=assign(bins,x[i]);if(j>=0)cls[j].push(x[i]);}
  for(j=0;j<cls.length;j++){if(!cls[j].length)continue;s=0;for(i=0;i<cls[j].length;i++)s+=cls[j][i];mu=s/cls[j].length;for(i=0;i<cls[j].length;i++){c=cls[j][i]-mu;sdcm+=c*c;}}
  return {gvf:sdam===0?1:1-sdcm/sdam,sdcm:sdcm,sdam:sdam};
}
function adcm(x,bins){
  var cls=[],i,j,t=0,med;for(i=0;i<bins.length;i++)cls.push([]);
  for(i=0;i<x.length;i++){j=assign(bins,x[i]);if(j>=0)cls[j].push(x[i]);}
  for(j=0;j<cls.length;j++){var a=cls[j];if(!a.length)continue;med=a.length%2?a[(a.length-1)/2]:(a[a.length/2-1]+a[a.length/2])/2;for(i=0;i<a.length;i++)t+=Math.abs(a[i]-med);}
  return t;
}

module.exports={cleanSorted:cleanSorted,distinctCount:distinctCount,fisherJenksDP:fisherJenksDP,fisherJenksDC:fisherJenksDC,
  q7:q7,quantileBins:quantileBins,equalIntervalBins:equalIntervalBins,stdMeanBins:stdMeanBins,stdIntervalBins:stdIntervalBins,
  logEqualBins:logEqualBins,rPretty:rPretty,mcPretty:mcPretty,assign:assign,counts:counts,gvf:gvf,adcm:adcm,meanSd:meanSd};
