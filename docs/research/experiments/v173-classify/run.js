/* V173 research experiment runner. Usage: node run.js [fixtures|edges|timing|sampling|stretch|all]
   Prints raw numbers; the note copies them. */
'use strict';
var C=require('./classify.js');
var cal=require('./calemp.json');
var which=process.argv[2]||'all';
function r(a,d){return a.map(function(v){return +v.toFixed(d===undefined?4:d);});}
function eq(a,b,tol){if(a.length!==b.length)return false;for(var i=0;i<a.length;i++)if(Math.abs(a[i]-b[i])>(tol||1e-6))return false;return true;}
function line(s){process.stdout.write(s+'\n');}
function rng(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;var t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function lognormal(n,seed){var R=rng(seed),a=[],i,u,v;for(i=0;i<n;i++){u=R()||1e-12;v=R();a.push(Math.exp(1.5*Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)));}return a;}

if(which==='fixtures'||which==='all'){
  line('== (a) fixtures: published worked examples ==');
  line('node '+process.version+' '+process.platform+' '+process.arch);
  /* mapclassify tests (calemp, n=58) */
  var fj=C.fisherJenksDP(cal,5),fjd=C.fisherJenksDC(cal,5),x=fj.x;
  line('calemp n='+x.length+' min='+x[0]+' max='+x[x.length-1]);
  line('FisherJenks k=5 DP bins='+JSON.stringify(fj.bins)+' counts='+JSON.stringify(C.counts(x,fj.bins))+' adcm='+C.adcm(x,fj.bins).toFixed(2)+' gvf='+C.gvf(x,fj.bins).gvf.toFixed(6));
  line('  expected (mapclassify test) bins=[75.29,192.05,370.5,722.85,4111.45] counts=[49,3,4,1,1] adcm=799.24 -> '+(eq(fj.bins,[75.29,192.05,370.5,722.85,4111.45])?'MATCH':'DIFFER'));
  line('FisherJenks k=5 D&C bins='+JSON.stringify(fjd.bins)+' same as DP: '+eq(fj.bins,fjd.bins));
  var fj9=C.fisherJenksDP(cal,9),toclass=[0,1,3,5,50,70,101,202,390,505,800,5000,5001];
  line('FisherJenks k=9 bins='+JSON.stringify(fj9.bins)+' find_bin='+JSON.stringify(toclass.map(function(v){var j=C.assign(fj9.bins,v);return j<0?fj9.bins.length-1:j;})));
  line('  expected (mapclassify TestFindBin k=9) [0,0,0,0,2,2,3,5,7,7,8,8,8]');
  line('  k=5 find_bin='+JSON.stringify(toclass.map(function(v){var j=C.assign(fj.bins,v);return j<0?4:j;}))+' expected [0,0,0,0,0,0,1,2,3,3,4,4,4]');
  var q=C.quantileBins(cal,5);
  line('Quantiles k=5 (type 7) bins='+JSON.stringify(r(q.bins))+' counts='+JSON.stringify(C.counts(x,q.bins)));
  line('  expected bins=[1.464,5.798,13.278,54.616,4111.45] counts=[12,11,12,11,12] -> '+(eq(q.bins,[1.464,5.798,13.278,54.616,4111.45],1e-9)?'MATCH':'DIFFER'));
  var qr=C.quantileBins(cal,5,'rank');
  line('Quantiles k=5 (geostats nearest-rank) bins='+JSON.stringify(qr.bins)+' counts='+JSON.stringify(C.counts(x,qr.bins)));
  var ei=C.equalIntervalBins(cal,5);
  line('EqualInterval k=5 bins='+JSON.stringify(r(ei.bins,3))+' counts='+JSON.stringify(C.counts(x,ei.bins))+' expected [822.394,1644.658,2466.922,3289.186,4111.45] [57,0,0,0,1]');
  var sm=C.stdMeanBins(cal,[-2,-1,1,2]);
  line('StdMean [-2,-1,1,2] bins='+JSON.stringify(r(sm.bins,8))+' counts='+JSON.stringify(C.counts(x,sm.bins))+' mean='+sm.mean+' sd(ddof1)='+sm.sd);
  line('  expected [-967.36235382,-420.71712519,672.57333208,1219.21856072,4111.45] counts [0,0,56,1,1]');
  line('StdDev 1sd, mean as break (ddof0): '+JSON.stringify(r(C.stdIntervalBins(cal,1,'break',0).bins,3)));
  line('StdDev 1sd, mean-centred class (ddof0): '+JSON.stringify(r(C.stdIntervalBins(cal,1,'class',0).bins,3)));
  line('StdDev 1/2sd, mean as break (ddof0): '+JSON.stringify(r(C.stdIntervalBins(cal,0.5,'break',0).bins,3)));
  line('R pretty(range(calemp), 5) = '+JSON.stringify(C.rPretty(x[0],x[x.length-1],5))+' ; mapclassify _pretty = '+JSON.stringify(C.mcPretty(cal,5))+' (mapclassify test bins 1000..5000)');
  line('R pretty(c(0,1),5)='+JSON.stringify(C.rPretty(0,1,5))+' pretty(c(1,1000),5)='+JSON.stringify(C.rPretty(1,1000,5))+' pretty(c(-3.2,7.9),5)='+JSON.stringify(C.rPretty(-3.2,7.9,5))+' pretty(c(5,5),5)='+JSON.stringify(C.rPretty(5,5,5)));
  line('log-equal k=5 bins='+JSON.stringify(r(C.logEqualBins(cal,5).bins,3))+' counts='+JSON.stringify(C.counts(x,C.logEqualBins(cal,5).bins)));
  /* GVF table on calemp */
  line('GVF on calemp, k=5: FJ='+C.gvf(x,fj.bins).gvf.toFixed(4)+' Q='+C.gvf(x,q.bins).gvf.toFixed(4)+' EI='+C.gvf(x,ei.bins).gvf.toFixed(4)+' logEq='+C.gvf(x,C.logEqualBins(cal,5).bins).gvf.toFixed(4));
  var ks=[2,3,4,5,6,7,8,9];line('FJ GVF by k: '+ks.map(function(k){return k+':'+C.gvf(x,C.fisherJenksDP(cal,k).bins).gvf.toFixed(4);}).join(' '));
  /* simple-statistics tests (lower-limit convention there; we convert) */
  var ss=[[[1,2,4,5,7,9,10,20],3,'[1,7,20,20] lower limits = classes {1..5},{7..10},{20}'],[[2,32,33,34,100],3,'[2,32,100,100] = {2},{32..34},{100}'],[[9,10,11,12,13],5,'[9..13] one per class']];
  ss.forEach(function(t){var o=C.fisherJenksDP(t[0],t[1]);line('ss jenks '+JSON.stringify(t[0])+' k='+t[1]+' -> upper bins '+JSON.stringify(o.bins)+' counts '+JSON.stringify(C.counts(o.x,o.bins))+' (ss expects '+t[2]+')');});
  var ck=[[[-1,2,-1,2,4,5,6,-1,2,-1],3],[[0,1,2,50,100,101,103],3],[[3,2,3,5,2,1],3],[[64.64249127327881,64.64249127328245,57.79216426169771],2]];
  ck.forEach(function(t){var o=C.fisherJenksDC(t[0],t[1]);line('ss ckmeans '+JSON.stringify(t[0])+' k='+t[1]+' -> '+JSON.stringify(o.bins)+' counts '+JSON.stringify(C.counts(o.x,o.bins)));});
  /* geostats getClassJenks starts its backtrack at row n-1 (reads as: optimises the first n-1 values) */
  var d=[1,2,4,5,7,9,10,20],o1=C.fisherJenksDP(d,3),o2=C.fisherJenksDP(d.slice(0,7),3);
  line('backtrack from n vs n-1 on '+JSON.stringify(d)+' k=3: from n '+JSON.stringify(o1.bins)+' gvf '+C.gvf(d,o1.bins).gvf.toFixed(4)+' ; from n-1 (max appended) '+JSON.stringify(o2.bins.slice(0,2).concat([20]))+' gvf '+C.gvf(d,o2.bins.slice(0,2).concat([20])).gvf.toFixed(4));
  var cs=cal.slice().sort(function(a,b){return a-b;}),o3=C.fisherJenksDP(cs.slice(0,57),5),b3=o3.bins.slice(0,4).concat([4111.45]);
  line('  calemp k=5 from n-1: '+JSON.stringify(b3)+' counts '+JSON.stringify(C.counts(x,b3))+' gvf '+C.gvf(x,b3).gvf.toFixed(4)+' vs exact '+C.gvf(x,fj.bins).gvf.toFixed(4));
}

if(which==='edges'||which==='all'){
  line('== (c) edge cases ==');
  var cases=[['n<k',[3,1,2],5],['all equal',[7,7,7,7],4],['duplicates',[1,1,1,1,2,2,9,9,9,30],4],['NaN/null/undefined/""/strings',[NaN,null,undefined,'',3,'4',Infinity,-Infinity,1,true,'x'],2],['negatives',[-50,-49,-48,-10,-9,0,1,2,40,41],3],['two distinct',[0,0,0,5,5],5],['empty',[],3],['single',[42],3]];
  cases.forEach(function(c){
    var v=c[1],k=c[2],fj=C.fisherJenksDP(v,k),dc=C.fisherJenksDC(v,k),q=C.quantileBins(v,k),ei=C.equalIntervalBins(v,k);
    line(c[0]+' k='+k+' cleaned='+JSON.stringify(fj.x)+' distinct='+C.distinctCount(fj.x));
    line('   FJ dp k_eff='+fj.k+' bins='+JSON.stringify(fj.bins)+' counts='+JSON.stringify(C.counts(fj.x,fj.bins))+' | dc bins='+JSON.stringify(dc.bins));
    line('   Q bins='+JSON.stringify(q.bins.map(function(b){return +b.toFixed(4);}))+' (asked '+k+', got '+q.bins.length+') counts='+JSON.stringify(C.counts(q.x,q.bins)));
    line('   EI bins='+JSON.stringify(ei.bins.map(function(b){return +b.toFixed(4);}))+' counts='+JSON.stringify(C.counts(ei.x,ei.bins)));
  });
  /* the existing lens rule (colour-lens.js line 96) when hi===lo */
  var lo=5,hi=5,len=6,iv=Math.min(len-1,Math.max(0,Math.floor((5-lo)/(hi-lo)*len)));
  line('colour-lens bin index rule with all values equal: '+iv+' (NaN means no colour)');
  /* quantile with heavy ties */
  var tie=[0,0,0,0,0,0,0,1,2,3];line('quantile ties [0x7,1,2,3] k=4 type7 '+JSON.stringify(C.quantileBins(tie,4).bins)+' counts '+JSON.stringify(C.counts(C.cleanSorted(tie),C.quantileBins(tie,4).bins)));
  /* tie-breaking within the DP: equal-cost partitions */
  var sym=[0,1,2,3];line('equal-cost tie [0,1,2,3] k=2: dp '+JSON.stringify(C.fisherJenksDP(sym,2).bins)+' dc '+JSON.stringify(C.fisherJenksDC(sym,2).bins));
  var sym3=[0,1,2];line('equal-cost tie [0,1,2] k=2: dp '+JSON.stringify(C.fisherJenksDP(sym3,2).bins)+' (both {0},{1,2} and {0,1},{2} cost 0.5)');
  /* large offset numeric stability */
  var off=[],i;for(i=0;i<12;i++)off.push(1.7e12+i);line('offset 1.7e12+0..11 k=3: '+JSON.stringify(C.fisherJenksDP(off,3).bins.map(function(b){return b-1.7e12;})));
}

if(which==='timing'||which==='all'){
  line('== (b) timing ==');
  line('node '+process.version+' '+process.platform+' '+process.arch+' cpus='+require('os').cpus().length+' '+require('os').cpus()[0].model);
  function time(fn,reps){var best=Infinity,t,i,out;for(i=0;i<reps;i++){t=process.hrtime.bigint();out=fn();t=Number(process.hrtime.bigint()-t)/1e6;if(t<best)best=t;}return {ms:best,out:out};}
  var sizes=(process.argv[3]||'1000,3000,10000,30000').split(',').map(Number),ksz=[5,9];
  sizes.forEach(function(n){
    var d=lognormal(n,n);
    ksz.forEach(function(k){
      var dp=n<=30000?time(function(){return C.fisherJenksDP(d,k);},n<=3000?5:1):null;
      var dc=time(function(){return C.fisherJenksDC(d,k);},n<=100000?5:1);
      var qq=time(function(){return C.quantileBins(d,k);},5);
      line('n='+n+' k='+k+' DP='+(dp?dp.ms.toFixed(1)+'ms':'skipped')+' D&C='+dc.ms.toFixed(1)+'ms quantile(sort)='+qq.ms.toFixed(1)+'ms'+(dp?' sameSSE='+(Math.abs(dp.out.sdcm-dc.out.sdcm)<=1e-9*Math.max(1,dp.out.sdcm))+' sameBins='+eq(dp.out.bins,dc.out.bins):'')+' sdcm='+dc.out.sdcm.toExponential(6));
    });
  });
}

if(which==='dp100k'){
  var n=+(process.argv[3]||100000),d=lognormal(n,n),t=Date.now(),o=C.fisherJenksDP(d,5);
  line('DP n='+n+' k=5: '+(Date.now()-t)+' ms; sdcm='+o.sdcm.toExponential(6)+' D&C='+C.fisherJenksDC(d,5).sdcm.toExponential(6));
}

if(which==='sampling'||which==='all'){
  line('== sampling ==');
  /* model of QGIS master qgsclassificationjenks.cpp sampling, transcribed as arithmetic (C int division, int32 product) */
  [3001,10000,30000,100000,1000000].forEach(function(n){
    var M=3000,size=Math.max(M,Math.floor(n/10)),written=2,j=-1,i,prod,overflow=false;
    for(i=1;i<n-2;i++){prod=i*(M-2);if(prod>2147483647)overflow=true;prod=prod|0;if(Math.trunc(prod/(n-2))>j){j++;written++;}}
    line('QGIS model n='+n+' sample size='+size+' slots written='+written+' never written (stay 0.0)='+(size-written)+(overflow?' int32 overflow in i*(M-2)':''));
  });
  /* effect of sampling on fit: exact vs stride sample vs random sample, lognormal n=100000 */
  var n=100000,d=lognormal(n,7),xs=C.cleanSorted(d),ex=C.fisherJenksDC(d,5),g0=C.gvf(xs,ex.bins).gvf;
  [1000,3000,10000].forEach(function(m){
    var s=[],i;for(i=0;i<m;i++)s.push(xs[Math.floor(i*(n-1)/(m-1))]);
    var sb=C.fisherJenksDC(s,5).bins;sb[sb.length-1]=xs[n-1];
    var R=rng(m),rs=[xs[0],xs[n-1]];for(i=2;i<m;i++)rs.push(xs[Math.floor(R()*n)]);
    var rb=C.fisherJenksDC(rs,5).bins;
    line('n=1e5 lognormal k=5 exact GVF='+g0.toFixed(6)+' | stride sample '+m+' GVF='+C.gvf(xs,sb).gvf.toFixed(6)+' | random sample '+m+' GVF='+C.gvf(xs,rb).gvf.toFixed(6));
  });
  /* QGIS-like sample with zeros padded, on strictly positive data */
  var size=10000,z=[],i2;for(i2=0;i2<3000;i2++)z.push(xs[Math.floor(i2*(n-1)/2999)]);for(i2=3000;i2<size;i2++)z.push(0);
  var zb=C.fisherJenksDC(z,5).bins;line('zero-padded sample (3000 real + 7000 zeros) bins='+JSON.stringify(r(zb,3))+' GVF on full data='+C.gvf(xs,zb).gvf.toFixed(6)+' (data min='+xs[0].toFixed(4)+')');
}

if(which==='stretch'||which==='all'){
  line('== raster stretch ==');
  /* synthetic band: 10000 lognormal values plus 20 extreme outliers */
  var b=lognormal(10000,3),i;for(i=0;i<20;i++)b.push(500+i*50);
  var xs=C.cleanSorted(b),N=xs.length,ms=C.meanSd(xs,0);
  function lin(lo,hi){return function(v){var t=Math.floor((v-lo)/(hi-lo)*255);return t<0?0:t>255?255:t;};}
  function usage(f){var h=new Array(256),i,used=0,s=0;for(i=0;i<256;i++)h[i]=0;for(i=0;i<N;i++){var o=f(xs[i]);h[o]++;s+=o;}for(i=0;i<256;i++)if(h[i])used++;return 'levels used='+used+' mean out='+(s/N).toFixed(1)+' share at 0='+(h[0]/N).toFixed(3)+' at 255='+(h[255]/N).toFixed(3);}
  line('band N='+N+' min='+xs[0].toFixed(4)+' max='+xs[N-1]+' mean='+ms.mean.toFixed(4)+' sd(pop)='+ms.sd.toFixed(4));
  line('min-max ['+xs[0].toFixed(3)+','+xs[N-1]+']: '+usage(lin(xs[0],xs[N-1])));
  [2,2.5].forEach(function(k){var lo=Math.max(xs[0],ms.mean-k*ms.sd),hi=Math.min(xs[N-1],ms.mean+k*ms.sd);line('stddev n='+k+' ['+lo.toFixed(3)+','+hi.toFixed(3)+']: '+usage(lin(lo,hi)));});
  [[0.02,0.98],[0.005,0.995]].forEach(function(p){var lo=C.q7(xs,p[0]),hi=C.q7(xs,p[1]);line('percent clip '+p[0]*100+'%/'+(100-p[1]*100).toFixed(1)+'% (exact quantile) ['+lo.toFixed(3)+','+hi.toFixed(3)+']: '+usage(lin(lo,hi)));});
  /* QGIS-style cumulative cut on a 256-bin histogram: bin lower edges */
  var bins=256,step=(xs[N-1]-xs[0])/bins,h=[],c=0,lo=null,hi=null,mn=Math.round(0.02*N),mx=Math.round(0.98*N);
  for(i=0;i<bins;i++)h.push(0);for(i=0;i<N;i++)h[Math.min(bins-1,Math.floor((xs[i]-xs[0])/step))]++;
  for(i=0;i<bins;i++){c+=h[i];if(lo===null&&c>mn)lo=xs[0]+i*step;if(c>=mx){hi=xs[0]+i*step;break;}}
  line('cumulative cut 2-98% on 256-bin histogram (QGIS rule) ['+lo.toFixed(3)+','+hi.toFixed(3)+'] vs exact ['+C.q7(xs,0.02).toFixed(3)+','+C.q7(xs,0.98).toFixed(3)+']');
  /* histogram equalisation on the exact values: out = round((cdf(v)-cdf_min)/(N-cdf_min)*255) */
  var cdf={},cmin=null;for(i=0;i<N;i++){cdf[xs[i]]=i+1;}cmin=cdf[xs[0]];
  line('histogram equalise: '+usage(function(v){return Math.round((cdf[v]-cmin)/(N-cmin)*255);}));
}
