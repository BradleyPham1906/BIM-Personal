
  /* ================= __acad3dV173: classifying a layer's numbers =================
     The methods a GIS offers for graduated colours, and the stretches for a surface of values,
     as docs/research/research-contents-pane/classification.md read them: exact Fisher-Jenks for
     natural breaks (the divide-and-conquer form, checked against mapclassify's worked examples),
     quantiles of type 7 (R's default, as QGIS and mapclassify), equal interval, a fraction of a
     standard deviation, R's pretty(), equal steps on a log scale, and breaks by hand.
     Every method returns the UPPER bound of each class, ascending, the last the highest value:
     a value v is in class j when breaks[j-1] < v <= breaks[j]. Pure: no state, no drawing. */
  var BIM_CLS_METHODS=['natural','quantile','equal','stddev','pretty','log','manual'];
  var BIM_CLS_LABEL={natural:'Natural breaks (Jenks)',quantile:'Quantile',equal:'Equal interval',
    stddev:'Standard deviation',pretty:'Pretty breaks',log:'Log interval',manual:'Manual'};
  var BIM_CLS_MAXK=12;
  var BIM_CLS_SAMPLE=100000;   /* above this, natural breaks reads an even sample, said on the result */
  var BIM_CLS_STRETCHES=['minmax','stddev','clip','histeq'];
  /* the numbers in a list: numbers and numeric strings kept, everything else dropped, sorted */
  function bimClsValues(values){
    var out=[],i,v;
    for(i=0;i<(values||[]).length;i++){
      v=values[i];
      if(v===null||v===undefined||v===''||typeof v==='boolean')continue;
      if(typeof v==='string'){if(!/^\s*-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?\s*$/.test(v))continue;v=parseFloat(v);}
      if(typeof v==='number'&&isFinite(v))out.push(v);
    }
    out.sort(function(a,b){return a-b;});
    return out;
  }
  function bimClsDistinct(x){var c=0,i;for(i=0;i<x.length;i++)if(i===0||x[i]!==x[i-1])c++;return c;}
  /* an even sample of a sorted list, its lowest and highest kept: never a random one, so a
     classification is the same every time it is made */
  function bimClsSample(x,m){
    if(x.length<=m)return x;
    var out=[],i,step=(x.length-1)/(m-1);
    for(i=0;i<m;i++)out.push(x[Math.round(i*step)]);
    return out;
  }
  /* Fisher (1958), exact: the least sum of squared deviations within classes. Prefix sums about the
     median keep it stable; the best start of the last class is non-decreasing in i, so each row is
     filled by divide and conquer, O(k n log n), with a stack rather than recursion. */
  function bimClsJenks(x,k){
    var n=x.length,S=[0],Q=[0],sh=x[Math.floor(n/2)],D=[],B=[],i,m,d,row;
    for(i=0;i<n;i++){d=x[i]-sh;S.push(S[i]+d);Q.push(Q[i]+d*d);}
    function ssq(j,e){var c=e-j+1,s=S[e+1]-S[j],r=Q[e+1]-Q[j]-s*s/c;return r<0?0:r;}
    row=[];for(i=0;i<n;i++)row.push(ssq(0,i));
    D.push(row);B.push(null);
    for(m=1;m<k;m++){
      var Dm=new Array(n),Bm=new Array(n),st=[],t,mid,a,b,j,c,best,bj;
      st.push(m===k-1?[n-1,n-1,m,n-1]:[m,n-1,m,n-1]);
      while(st.length){
        t=st.pop();
        if(t[0]>t[1])continue;
        mid=(t[0]+t[1])>>1;a=Math.max(m,t[2]);b=Math.min(mid,t[3]);best=Infinity;bj=a;
        for(j=a;j<=b;j++){c=D[m-1][j-1]+ssq(j,mid);if(c<best){best=c;bj=j;}}
        Dm[mid]=best;Bm[mid]=bj;
        st.push([t[0],mid-1,t[2],bj]);st.push([mid+1,t[1],bj,t[3]]);
      }
      D.push(Dm);B.push(Bm);
    }
    var out=new Array(k),e=n-1;
    for(m=k-1;m>=0;m--){out[m]=x[e];if(m>0)e=B[m][e]-1;}
    return out;
  }
  function bimClsQ7(x,p){var h=(x.length-1)*p,lo=Math.floor(h);return lo>=x.length-1?x[x.length-1]:x[lo]+(h-lo)*(x[lo+1]-x[lo]);}
  function bimClsMeanSd(x){
    var n=x.length,m=0,s=0,i;
    for(i=0;i<n;i++)m+=x[i];
    m/=n;
    for(i=0;i<n;i++)s+=(x[i]-m)*(x[i]-m);
    return {mean:m,sd:n>1?Math.sqrt(s/(n-1)):0};   /* the sample's (n - 1), as mapclassify */
  }
  /* R's pretty(), its defaults (h = 1.5, h5 = 0.5 + 1.5 h), as src/appl/pretty.c computes the unit */
  function bimClsPretty(lo,up,ndiv){
    var h=1.5,h5=0.5+1.5*h,minN=Math.floor(ndiv/3),eps=1e-10,dx=up-lo,cell,U,small,base,unit,ns,nu,k,out=[],i;
    if(dx===0&&up===0){cell=1;small=true;}
    else{cell=Math.max(Math.abs(lo),Math.abs(up));U=(1+1/(1+h))*Math.max(1,ndiv)*2.220446049250313e-16;small=dx<cell*U*3;}
    if(small){if(cell>10)cell=9+cell/10;cell*=0.75;if(minN>1)cell/=minN;}
    else{cell=dx;if(ndiv>1)cell/=ndiv;}
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
  /* the class of a value: its index, or -1 when it is above the highest break */
  function bimClsAssign(breaks,v){
    var lo=0,hi=breaks.length-1,mid;
    if(hi<0||!(v<=breaks[hi]))return -1;
    while(lo<hi){mid=(lo+hi)>>1;if(v<=breaks[mid])hi=mid;else lo=mid+1;}
    return lo;
  }
  /* goodness of variance fit, 1 - SDCM / SDAM: 1 when every class is one value */
  function bimClsGvf(x,breaks){
    var n=x.length,m=0,sdam=0,sum=[],cnt=[],sq=[],i,j,sdcm=0;
    if(!n)return 1;
    for(i=0;i<n;i++)m+=x[i];
    m/=n;
    for(i=0;i<n;i++)sdam+=(x[i]-m)*(x[i]-m);
    for(j=0;j<breaks.length;j++){sum.push(0);cnt.push(0);sq.push(0);}
    for(i=0;i<n;i++){j=bimClsAssign(breaks,x[i]);if(j<0)continue;sum[j]+=x[i];sq[j]+=x[i]*x[i];cnt[j]++;}
    for(j=0;j<breaks.length;j++)if(cnt[j])sdcm+=Math.max(0,sq[j]-sum[j]*sum[j]/cnt[j]);
    return sdam>0?1-sdcm/sdam:1;
  }
  /* classify: o = {k, step (stddev: 1, 0.5, 1/3, 0.25), centre ('class' or 'break'), breaks (manual)}.
     Returns {method, breaks, counts, n, lo, hi, k, asked, sampled, gvf, note} or {error}. */
  function bimClsBreaks(values,method,o){
    o=o||{};
    var x=bimClsValues(values),n=x.length,k=Math.round(+o.k||5),asked,b=[],i,lo,hi,w,t,ms,note='',sampled=0,s;
    if(BIM_CLS_METHODS.indexOf(method)<0)return {error:'There is no classification called '+method};
    if(!n)return {error:'There are no numbers to classify'};
    k=Math.max(1,Math.min(BIM_CLS_MAXK,isFinite(k)?k:5));asked=k;
    lo=x[0];hi=x[n-1];
    if(lo===hi)b=[hi];
    else if(method==='natural'){
      s=bimClsSample(x,BIM_CLS_SAMPLE);
      if(s!==x)sampled=s.length;
      k=Math.min(k,bimClsDistinct(s));
      b=k<=1?[hi]:bimClsJenks(s,k);
      b[b.length-1]=hi;
    }else if(method==='quantile'){
      for(i=1;i<k;i++)b.push(bimClsQ7(x,i/k));
      b.push(hi);
    }else if(method==='equal'){
      w=(hi-lo)/k;
      for(i=1;i<k;i++)b.push(lo+w*i);
      b.push(hi);
    }else if(method==='stddev'){
      ms=bimClsMeanSd(x);w=ms.sd*([1,0.5,1/3,0.25].indexOf(+o.step)>=0?+o.step:1);
      t=o.centre==='break'?ms.mean:ms.mean-w/2;
      t=t-Math.floor((t-lo)/w)*w;
      if(t<=lo)t+=w;
      for(;t<hi&&b.length<BIM_CLS_MAXK-1;t+=w)b.push(t);
      b.push(hi);
      note='Mean '+ms.mean+', standard deviation '+ms.sd+' (of the sample, n - 1)';
    }else if(method==='pretty'){
      t=bimClsPretty(lo,hi,k);
      for(i=1;i<t.length;i++)if(t[i]>lo&&t[i]<hi)b.push(t[i]);
      b.push(hi);
    }else if(method==='log'){
      if(!(lo>0))return {error:'Log interval needs every value above 0; the lowest is '+lo};
      w=(Math.log(hi)-Math.log(lo))/k;
      for(i=1;i<k;i++)b.push(Math.exp(Math.log(lo)+w*i));
      b.push(hi);
    }else{
      for(i=0;i<(o.breaks||[]).length;i++){t=+o.breaks[i];if(isFinite(t)&&t>=lo&&t<hi)b.push(t);}
      b.sort(function(p,q){return p-q;});
      b.push(hi);
    }
    var u=[];
    for(i=0;i<b.length;i++)if(!u.length||b[i]>u[u.length-1])u.push(b[i]);   /* a repeated break is one */
    var cnt=[];for(i=0;i<u.length;i++)cnt.push(0);
    for(i=0;i<n;i++){t=bimClsAssign(u,x[i]);if(t>=0)cnt[t]++;}
    if(sampled)note=(note?note+'. ':'')+'Natural breaks read an even sample of '+sampled+' of the '+n+' values';
    if(u.length<asked&&method!=='stddev'&&method!=='manual'&&method!=='pretty')note=(note?note+'. ':'')+u.length+' class'+(u.length===1?'':'es')+' of the '+asked+' asked: the values allow no more';
    return {method:method,breaks:u,counts:cnt,n:n,lo:lo,hi:hi,k:u.length,asked:asked,sampled:sampled,gvf:bimClsGvf(x,u),note:note};
  }
  /* a stretch over a surface's values: o = {n (stddev, default 2), lo and hi percent (clip, default 2
     and 98, QGIS's cumulative count cut)}. Returns {type, lo, hi, cdf?} for bimClsStretchAt. */
  function bimClsStretch(values,type,o){
    o=o||{};
    var x=bimClsValues(values),n=x.length,ms,f,a,b,s;
    if(BIM_CLS_STRETCHES.indexOf(type)<0)return {error:'There is no stretch called '+type};
    if(!n)return {error:'There are no numbers to stretch'};
    if(type==='minmax')return {type:type,lo:x[0],hi:x[n-1]};
    if(type==='stddev'){
      ms=bimClsMeanSd(x);f=isFinite(+o.n)&&+o.n>0?+o.n:2;
      return {type:type,lo:Math.max(x[0],ms.mean-f*ms.sd),hi:Math.min(x[n-1],ms.mean+f*ms.sd),n:f};
    }
    if(type==='clip'){
      a=isFinite(+o.lo)?Math.max(0,Math.min(49,+o.lo)):2;b=isFinite(+o.hi)?Math.max(51,Math.min(100,+o.hi)):98;
      return {type:type,lo:bimClsQ7(x,a/100),hi:bimClsQ7(x,b/100),pl:a,ph:b};
    }
    s=bimClsSample(x,4096);
    return {type:type,lo:x[0],hi:x[n-1],cdf:s};
  }
  /* where a value falls on the ramp, 0 to 1 */
  function bimClsStretchAt(st,v){
    if(!st||st.error||typeof v!=='number'||!isFinite(v))return null;
    if(st.cdf){
      var c=st.cdf,lo=0,hi=c.length;
      if(c.length<2||c[0]===c[c.length-1])return 1;
      while(lo<hi){var mid=(lo+hi)>>1;if(c[mid]<=v)lo=mid+1;else hi=mid;}
      return Math.max(0,Math.min(1,(lo-1)/(c.length-1)));
    }
    if(st.hi<=st.lo)return 1;
    return Math.max(0,Math.min(1,(v-st.lo)/(st.hi-st.lo)));
  }
export { bimClsBreaks, bimClsStretch, bimClsStretchAt };
