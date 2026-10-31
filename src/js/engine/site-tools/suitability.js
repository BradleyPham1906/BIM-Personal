  /* ================= __acad3dV172: the site analysis tools: Suitability and Locate =================
     Esri's four steps (research-site-analysis-tools.md, 2): the criteria; each transformed to a common scale, 1 to 10
     by default -- Range of Classes, Unique Categories, or a continuous function between a lower and an upper threshold
     (by default the data's least and greatest), its values rescaled to the scale's ends; weighted by a multiplier (the
     transformed values times their weights, added) or by percent (summing to 100, the added result rescaled to the
     scale); then Locate, the best region of a given area. The functions are QGIS's fuzzy membership formulas (f1 the
     spread, f2 the midpoint): Small 1/(1+(x/f2)^f1), Large 1/(1+(x/f2)^-f1), Near 1/(1+f1(x-f2)^2). A cell where a
     criterion has no value has none in the result; a restricted cell is not scored, and is drawn grey. */
  var BIM_TL_HOW_V=[['linear','Linear'],['small','Small (lower is better)'],['large','Large (higher is better)'],['near','Near a value'],['classes','Range of classes']];
  var BIM_TL_HOW_C=[['cats','Unique categories']];
  var BIM_TL_CRIT=[
    {id:'slope',name:'Slope',kind:'value',src:'slope',unit:'%',dir:'down',on:true},
    {id:'streets',name:'Distance to the streets',kind:'dist',src:'streets',unit:'m',dir:'down',on:true},
    {id:'arterials',name:'Distance from arterial roads',kind:'dist',src:'arterials',unit:'m',dir:'up',on:true},
    {id:'sunhours',name:'Sun hours',kind:'value',src:'sunhours',unit:'h',dir:'up',on:true},
    {id:'trees',name:'Distance to trees',kind:'dist',src:'trees',unit:'m',dir:'down',on:false},
    {id:'slopecls',name:'Slope class',kind:'cat',src:'slope',on:false}];
  var BIM_TL_CRIT_F={on:'bool',how:'sel',dir:'sel',lo:'num',hi:'num',mid:'num',spread:'num',breaks:'text',vals:'text',w:'num'};
  function bimTlScale(P){var m=+P.scale;return [1,m===5||m===9?m:10];}
  /* a criterion's default: on where its layer is there (and its own default is on), linear its way, weight 1 */
  function bimTlCritDef(c){return function(G){
    var s=bimTlSourceOf(G,c.src),D={on:!!c.on&&!s.why,how:c.kind==='cat'?'cats':'linear',dir:c.dir||'up',lo:null,hi:null,mid:null,spread:null,breaks:'',vals:'',w:1};
    return D;
  };}
  function bimTlList(s){
    var a=String(s==null?'':s).split(/[,;\s]+/).filter(function(x){return x!=='';}).map(function(x){return bimTlNum(x);});
    return a.some(function(v){return !isFinite(v);})?null:a;
  }
  /* a criterion's raw values on the grid: a value, a distance in metres, or a class's index; NaN where none */
  function bimTlCritValues(G,c){
    var s=bimTlSourceOf(G,c.src),V=new Float64Array(G.n),k,D,C,i;
    if(s.why)return {why:s.why};
    if(c.kind==='value'){for(k=0;k<G.n;k++)V[k]=s.v[k];return {V:V};}
    if(c.kind==='dist'){D=bimTlDistance(G,s.m);if(!D)return {why:'None of it is within the processing extent'};for(k=0;k<G.n;k++)V[k]=D[k];return {V:V};}
    C=bimLandSlope();
    for(k=0;k<G.n;k++){if(!isFinite(s.v[k])){V[k]=NaN;continue;}for(i=0;i<C.length-1;i++)if(s.v[k]<C[i][1])break;V[k]=i;}
    return {V:V,classes:C.map(function(x){return x[2];})};
  }
  /* the function's value before it is rescaled, x already within the thresholds */
  function bimTlFn(how,x,mid,spread){
    if(how==='small')return 1/(1+Math.pow(Math.max(0,x)/mid,spread));
    if(how==='large')return x<=0?0:1/(1+Math.pow(x/mid,-spread));
    if(how==='near')return 1/(1+spread*(x-mid)*(x-mid));
    return x;
  }
  /* the transform worked out for a criterion: its thresholds, the function's ends, and the value of any x */
  function bimTlTransformOf(o,c,V,sc){
    var T={how:o.how,lo:o.lo,hi:o.hi,s0:sc[0],s1:sc[1]},rg,f0,f1,mid,sp;
    if(o.how==='cats'){
      T.vals=bimTlList(o.vals);
      if(!T.vals||!T.vals.length){var nc=bimLandSlope().length,i;T.vals=[];T.even=true;for(i=0;i<nc;i++)T.vals.push(Math.round((sc[1]-i*(sc[1]-sc[0])/(nc-1))*100)/100);}   /* none given: spread over the scale, the first class best */
      T.f=function(x){var v=T.vals[Math.round(x)];return v===undefined?NaN:v;};return T;
    }
    if(o.how==='classes'){
      T.breaks=bimTlList(o.breaks);T.vals=bimTlList(o.vals);
      T.f=function(x){var i=0;while(i<T.breaks.length&&x>=T.breaks[i])i++;return T.vals[i];};
      return T;
    }
    rg=bimTlRange(V);
    if(T.lo===null||T.lo===undefined)T.lo=rg?rg[0]:0;
    if(T.hi===null||T.hi===undefined)T.hi=rg?rg[1]:0;
    T.flat=!(T.hi>T.lo);
    mid=o.mid!==null&&o.mid!==undefined?o.mid:(T.lo+T.hi)/2;
    sp=o.spread!==null&&o.spread!==undefined?o.spread:(o.how==='near'?(T.hi>T.lo?4/((T.hi-T.lo)*(T.hi-T.lo)):1):5);
    T.mid=mid;T.spread=sp;
    if(T.flat){T.f=function(){return (sc[0]+sc[1])/2;};return T;}
    f0=bimTlFn(o.how,T.lo,mid,sp);f1=bimTlFn(o.how,T.hi,mid,sp);
    T.fmin=Math.min(f0,f1);T.fmax=Math.max(f0,f1);
    if(o.how==='near'&&mid>=T.lo&&mid<=T.hi)T.fmax=bimTlFn('near',mid,mid,sp);
    var down=o.how==='linear'&&o.dir==='down';
    T.f=function(x){
      var xx=Math.max(T.lo,Math.min(T.hi,x)),f=bimTlFn(o.how,xx,mid,sp),t=T.fmax>T.fmin?(f-T.fmin)/(T.fmax-T.fmin):0.5;
      return down?sc[1]-t*(sc[1]-sc[0]):sc[0]+t*(sc[1]-sc[0]);
    };
    return T;
  }
  /* a criterion's transform in words, for the messages */
  function bimTlTransformText(c,T){
    var u=c.unit==='%'?'%':(c.unit?' '+c.unit:'');
    if(T.how==='cats')return c.name+': unique categories, '+T.vals.join(', ')+(T.even?' (spread over the scale)':'');
    if(T.how==='classes')return c.name+': classes at '+T.breaks.map(function(b){return bimDispNum(b,2)+u;}).join(', ')+' given '+T.vals.join(', ');
    if(T.flat)return c.name+' does not vary over the extent: it adds the scale\'s middle everywhere';
    var w={linear:'linear',small:'small',large:'large',near:'near'}[T.how];
    return c.name+': '+w+(T.how==='linear'?' ('+(T.dir==='down'?'lower is better':'higher is better')+')':', midpoint '+bimDispNum(T.mid,2)+u+', spread '+bimDispNum(T.spread,4))+
      ', between '+bimDispNum(T.lo,2)+u+' and '+bimDispNum(T.hi,2)+u;
  }
  BIM_TL_TOOLS.push({id:'suit',name:'Suitability',cmd:'SUITABILITY',
    sum:'Where on the site is best to build: the criteria each turned to a common scale, weighted and added, the restricted cells left out.',
    how:'Esri\'s weighted overlay, as its Suitability Modeler does it: each criterion transformed to the scale (a function between its thresholds, classes or categories), '+
      'then by Multiplier the transformed values times their weights added, or by Percent added at their share and the result rescaled to the scale. A cell where a criterion has no value has none; '+
      'a restricted cell, from an Exclusions run, is not scored.',
    params:[
      {id:'scale',label:'Suitability scale',t:'sel',def:'10',opts:[['10','1 to 10'],['9','1 to 9'],['5','1 to 5']]},
      {id:'weightBy',label:'Weight by',t:'sel',def:'mult',opts:[['mult','Multiplier'],['pct','Percent']]},
      {id:'restrict',label:'Restricted cells from',t:'run',of:'exclude',def:function(){return bimTlLast('exclude');}},
      {id:'crit',label:'Criteria',t:'crit',crit:BIM_TL_CRIT.map(function(c){var x={id:c.id,name:c.name,kind:c.kind,src:c.src,unit:c.unit,fields:BIM_TL_CRIT_F,def:bimTlCritDef(c)};return x;})}],
    check:function(P,G,E,W){
      var sc=bimTlScale(P),on=0,sum=0;
      BIM_TL_CRIT.forEach(function(c){
        var o=P.crit[c.id],key='crit.'+c.id,s,b,v,H;
        if(!o||!o.on)return;
        on++;
        s=bimTlSourceOf(G,c.src);
        if(s.why){E[key]=c.name+': '+s.why;return;}
        H=(c.kind==='cat'?BIM_TL_HOW_C:BIM_TL_HOW_V).map(function(x){return x[0];});
        if(H.indexOf(o.how)<0){E[key]=c.name+': not a transform for it';return;}
        if(!(isFinite(o.w))||o.w===null){E[key]=c.name+': a weight is required';return;}
        if(P.weightBy==='pct'?(o.w<0||o.w>100):(o.w<=0||o.w>100)){E[key]=c.name+': the weight is '+(P.weightBy==='pct'?'0 to 100%':'more than 0, at most 100');return;}
        sum+=o.w;
        if(o.how==='cats'){v=bimTlList(o.vals);if(v&&!v.length)return;if(!v||v.length!==bimLandSlope().length){E[key]=c.name+': one value for each of the '+bimLandSlope().length+' classes, or none to spread them over the scale';return;}
          if(v.some(function(x){return x<sc[0]||x>sc[1];})){E[key]=c.name+': each value within the scale, '+sc[0]+' to '+sc[1];return;}return;}
        if(o.how==='classes'){b=bimTlList(o.breaks);v=bimTlList(o.vals);
          if(!b||!b.length){E[key]=c.name+': the class breaks, in order, separated by commas';return;}
          for(var i=1;i<b.length;i++)if(!(b[i]>b[i-1])){E[key]=c.name+': the breaks must rise';return;}
          if(!v||v.length!==b.length+1){E[key]=c.name+': '+(b.length+1)+' values, one more than the breaks';return;}
          if(v.some(function(x){return x<sc[0]||x>sc[1];})){E[key]=c.name+': each value within the scale, '+sc[0]+' to '+sc[1];return;}return;}
        if(o.lo!==null&&o.hi!==null&&isFinite(o.lo)&&isFinite(o.hi)&&!(o.hi>o.lo)){E[key]=c.name+': the upper threshold must be above the lower';return;}
        if([o.lo,o.hi,o.mid,o.spread].some(function(x){return x!==null&&!isFinite(x);})){E[key]=c.name+': type a number';return;}
        if((o.how==='small'||o.how==='large')&&o.mid!==null&&!(o.mid>0)){E[key]=c.name+': the midpoint must be more than 0';return;}
        if(o.how!=='linear'&&o.spread!==null&&!(o.spread>0)){E[key]=c.name+': the spread must be more than 0';return;}
      });
      if(!on)E._='Tick at least one criterion';
      else if(P.weightBy==='pct'&&!E._&&Math.abs(sum-100)>1e-6)E._='The percentages add to '+bimDispNum(sum,2)+'%: they must add to 100%';
      if(!P.restrict)W.restrict='No restricted cells: every cell is scored';
    },
    run:function(P,G,M){
      var sc=bimTlScale(P),U=[],k,j,R=null,rest=null,S=new Float64Array(G.n),lv,pal,rg,L=bimTlInLot(G),rows=[],n=0,sum=0,mn=Infinity,mx=-Infinity,nr=0,nn=0;
      BIM_TL_CRIT.forEach(function(c){
        var o=P.crit[c.id];if(!o||!o.on)return;
        var cv=bimTlCritValues(G,c);if(cv.why){U.push({c:c,why:cv.why});return;}
        var T=bimTlTransformOf(o,c,cv.V,sc);T.dir=o.dir;
        U.push({c:c,V:cv.V,T:T,w:o.w});
        (T.flat?bimTlWarn:bimTlInfo)(M,bimTlTransformText(c,T)+'; weight '+bimDispNum(o.w,2)+(P.weightBy==='pct'?'%':''));
      });
      for(j=0;j<U.length;j++)if(U[j].why)return {error:U[j].c.name+': '+U[j].why};
      if(P.restrict){R=bimTlRunOut(P.restrict,G);if(R.why)return {error:'Restricted cells: '+R.why};rest=R.lv;}
      for(k=0;k<G.n;k++){
        if(rest&&rest[k]>=0){S[k]=NaN;continue;}
        var s=0,ok=true;
        for(j=0;j<U.length;j++){var x=U[j].V[k];if(!isFinite(x)){ok=false;break;}var t=U[j].T.f(x);if(!isFinite(t)){ok=false;break;}s+=(P.weightBy==='pct'?U[j].w/100:U[j].w)*t;}
        S[k]=ok?s:NaN;
      }
      if(P.weightBy==='pct'){
        rg=bimTlRange(S);
        if(rg&&rg[1]>rg[0])for(k=0;k<G.n;k++){if(isFinite(S[k]))S[k]=sc[0]+(S[k]-rg[0])/(rg[1]-rg[0])*(sc[1]-sc[0]);}
        else if(rg){bimTlWarn(M,'The suitability is the same everywhere: it is the scale\'s middle');for(k=0;k<G.n;k++)if(isFinite(S[k]))S[k]=(sc[0]+sc[1])/2;}
      }
      rg=bimTlRange(S);
      if(!rg)return {error:'No cell could be scored: every cell is restricted or has no value'};
      lv=bimTlQuant(S,rg[0],rg[1],BIM_TL_LEVELS);
      if(rest)for(k=0;k<G.n;k++)if(rest[k]>=0)lv[k]=BIM_TL_LEVELS;
      pal=bimTlRamp(BIM_TL_RAMP_SUIT,BIM_TL_LEVELS).concat([BIM_TL_REST_PAL]);
      for(k=0;k<G.n;k++){if(!L[k])continue;if(rest&&rest[k]>=0){nr++;continue;}if(!isFinite(S[k])){nn++;continue;}n++;sum+=S[k];if(S[k]<mn)mn=S[k];if(S[k]>mx)mx=S[k];}
      if(n){rows.push([G.lot?'On the lot, mean':'Mean',bimDispNum(sum/n,2)]);rows.push([G.lot?'On the lot, least':'Least',bimDispNum(mn,2)]);rows.push([G.lot?'On the lot, best':'Best',bimDispNum(mx,2)]);}
      rows.push(['Scored',bimTlAreaText(bimTlArea(n,G))]);
      if(rest)rows.push(['Restricted',bimTlAreaText(bimTlArea(nr,G))]);
      if(nn)rows.push(['No value',bimTlAreaText(bimTlArea(nn,G))]);
      bimTlInfo(M,(P.weightBy==='pct'?'Weighted by percent, the result rescaled to ':'Weighted by multiplier, on ')+'the scale '+sc[0]+' to '+sc[1]+'; the output from '+bimDispNum(rg[0],2)+' to '+bimDispNum(rg[1],2));
      var nm=U.map(function(u){return u.c.name.toLowerCase();}).join(', ');
      return {stats:rows,label:nm,sum:n?'mean '+bimDispNum(sum/n,2)+(G.lot?' on the lot':'')+', best '+bimDispNum(mx,2):'',
        layer:{name:nm,lv:lv,n:BIM_TL_LEVELS,pal:pal,lo:rg[0],hi:rg[1],rest:BIM_TL_LEVELS,unit:'',
          keys:[{name:'Least suitable, '+bimDispNum(rg[0],2),col:pal[0]},{name:'Most suitable, '+bimDispNum(rg[1],2),col:pal[BIM_TL_LEVELS-1]}].concat(rest?[{name:'Restricted',col:BIM_TL_REST}]:[]),opacity:0.75}};
    }});
  /* ---- Locate: the best region of a given area ---- */
  /* a max-heap of cells by value, the lower index first among equals */
  function bimTlHeap(V){
    var h=[];
    function above(a,b){return V[a]>V[b]||(V[a]===V[b]&&a<b);}
    return {n:function(){return h.length;},
      push:function(k){h.push(k);var i=h.length-1,p;while(i>0){p=(i-1)>>1;if(!above(h[i],h[p]))break;var t=h[i];h[i]=h[p];h[p]=t;i=p;}},
      pop:function(){var top=h[0],last=h.pop(),i=0,l,r,m,t;if(h.length){h[0]=last;for(;;){l=2*i+1;r=l+1;m=i;if(l<h.length&&above(h[l],h[m]))m=l;if(r<h.length&&above(h[r],h[m]))m=r;if(m===i)break;t=h[i];h[i]=h[m];h[m]=t;i=m;}}return top;}};
  }
  /* from a seed, the next best neighbouring cell each time (rook's case), until the region has need cells */
  function bimTlGrow(G,V,ok,seed,need){
    var q=new Uint8Array(G.n),H=bimTlHeap(V),got=[],sum=0,k,i,j,nb;
    H.push(seed);q[seed]=1;
    while(H.n()&&got.length<need){
      k=H.pop();got.push(k);sum+=V[k];
      i=k%G.nx;j=(k-i)/G.nx;
      nb=[i>0?k-1:-1,i<G.nx-1?k+1:-1,j>0?k-G.nx:-1,j<G.nz-1?k+G.nx:-1];
      nb.forEach(function(x){if(x>=0&&!q[x]&&ok[x]){q[x]=1;H.push(x);}});
    }
    return got.length>=need?{cells:got,mean:sum/got.length}:null;
  }
  /* the seeds: the best cells, each at least half the region's side from the others, at most 24 */
  function bimTlSeeds(G,V,ok,need){
    var C=[],k,S=[],sp=Math.max(1,Math.sqrt(need)/2),i,a,b,far;
    for(k=0;k<G.n;k++)if(ok[k])C.push(k);
    C.sort(function(x,y){return V[y]-V[x]||x-y;});
    for(i=0;i<C.length&&S.length<24;i++){
      a=C[i];far=true;
      for(b=0;b<S.length;b++){var dx=(a%G.nx)-(S[b]%G.nx),dz=Math.floor(a/G.nx)-Math.floor(S[b]/G.nx);if(dx*dx+dz*dz<sp*sp){far=false;break;}}
      if(far)S.push(a);
    }
    return S;
  }
  function bimTlLocateInputs(P,G){
    var R=bimTlRunOut(P.from,G),V,ok,k,n=0;
    if(R.why)return {why:R.why};
    V=new Float64Array(G.n);ok=new Uint8Array(G.n);
    for(k=0;k<G.n;k++){var v=bimTlValue(R.d,R.lv[k]);V[k]=v===null?NaN:v;ok[k]=v!==null&&(P.within!=='lot'||!G.lot||G.lot[k])?1:0;if(ok[k])n++;}
    return {R:R,V:V,ok:ok,n:n};
  }
  BIM_TL_TOOLS.push({id:'locate',name:'Locate',cmd:'LOCATE',
    sum:'The best place of a given area in a suitability map: one connected region, the highest mean suitability.',
    how:'A simplified Locate Regions: the 24 best cells, each at least half the region\'s side from the others, are seeds; from each, the region grows by the best neighbouring cell '+
      '(sharing a side) until it has the area; the region with the highest mean suitability is kept, the earlier seed among equals. Esri\'s own algorithm also weighs shape and spacing, which this does not.',
    params:[
      {id:'from',label:'Suitability from',t:'run',of:'suit',req:true,def:function(){return bimTlLast('suit');}},
      {id:'area',label:'Area',t:'num',req:true,unit:'m\u00b2',min:0,gt:true,def:600},
      {id:'within',label:'Within',t:'sel',def:'lot',opts:[['lot','The lot'],['all','The whole extent']]}],
    check:function(P,G,E){
      if(P.within==='lot'&&!G.lot)E.within='No lot yet: pick the whole extent';
      if(E.from||E.area||E.within)return;
      var I=bimTlLocateInputs(P,G);
      if(I.why){E.from=I.why;return;}
      if(bimTlArea(I.n,G)<P.area-1e-9)E.area='Only '+bimTlAreaText(bimTlArea(I.n,G))+' can be used there';
    },
    run:function(P,G,M){
      var I=bimTlLocateInputs(P,G),need=Math.ceil(P.area/(G.cell*G.cell)-1e-9),S,best=null,i,r,lv=new Int16Array(G.n),k,cx=0,cz=0,rows=[];
      if(I.why)return {error:I.why};
      S=bimTlSeeds(G,I.V,I.ok,need);
      for(i=0;i<S.length;i++){r=bimTlGrow(G,I.V,I.ok,S[i],need);if(r&&(!best||r.mean>best.mean+1e-12)){best=r;best.seed=i;}}
      if(!best)return {error:'No connected region of '+bimTlAreaText(P.area)+' fits there'};
      lv.fill(-1);
      best.cells.forEach(function(c){lv[c]=0;cx+=bimTlCx(G,c%G.nx);cz+=bimTlCz(G,Math.floor(c/G.nx));});
      cx/=best.cells.length;cz/=best.cells.length;
      rows.push(['Area',bimTlAreaText(bimTlArea(best.cells.length,G))]);
      rows.push(['Mean suitability',bimDispNum(best.mean,2)]);
      rows.push(['Its centre',bimDispNum(cx,1)+', '+bimDispNum(cz,1)+' (model x, z)']);
      rows.push(['Seeds compared',String(S.length)]);
      bimTlInfo(M,'From the run of '+I.R.h.at+'; neighbours share a side; cells of '+bimDispNum(G.cell,2)+' m');
      return {stats:rows,label:bimTlAreaText(P.area),sum:bimTlAreaText(bimTlArea(best.cells.length,G))+', mean suitability '+bimDispNum(best.mean,2),
        keep:function(T,h){h.region={cx:cx,cz:cz,mean:best.mean,n:best.cells.length,seed:best.seed};},
        layer:{name:bimTlAreaText(P.area)+(P.within==='lot'?' on the lot':''),lv:lv,n:1,pal:['#e8336c'],keys:[{name:'The best '+bimTlAreaText(P.area),col:'#e8336c'}],opacity:0.85}};
    }});
