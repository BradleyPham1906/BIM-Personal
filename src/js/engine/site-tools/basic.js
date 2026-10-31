  /* ================= __acad3dV172: the site analysis tools: Buffer, Distance, Slope classes, Exclusions =================
     Esri's Buffer, Euclidean Distance and Reclassify of the slope, read at the source (research-site-analysis-tools.md,
     2), on the tool grid; Exclusions is the Suitability Modeler's restricted locations: what is excluded because of
     what is known to be there, kept apart from NoData, where nothing is known. */
  var BIM_TL_BUF_COL='#e8833a';
  var BIM_TL_EXCL=[
    {id:'outside',name:'Outside the lot',col:'#c9ccd1'},
    {id:'setbacks',name:'Inside the zoning setbacks',col:'#a0a6ad'},
    {id:'flood',name:'Flood zones (1% annual chance)',col:'#4f81bd'},
    {id:'wetlands',name:'Wetlands',col:'#3d9970'},
    {id:'steep',name:'Steep slopes',col:'#c0504d'},
    {id:'buildings',name:'Buildings standing now',col:'#6b6b6b'},
    {id:'buffer',name:'A buffer from History',col:BIM_TL_BUF_COL}];
  /* stats rows for a mask: its area, and the lot's share */
  function bimTlMaskStats(G,lv,rows){
    var all=0,inl=0,k;
    for(k=0;k<G.n;k++)if(lv[k]>=0){all++;if(G.lot&&G.lot[k])inl++;}
    rows.push(['Area',bimTlAreaText(bimTlArea(all,G))]);
    if(G.lot)rows.push(['On the lot',bimTlAreaText(bimTlArea(inl,G))+' of '+bimTlAreaText(G.lotArea)+' ('+bimDispNum(G.lotArea?100*bimTlArea(inl,G)/G.lotArea:0,1)+'%)']);
    return {all:all,lot:inl};
  }
  /* the cells inside the zoning setbacks: the lot less the plate at the ground; null with no setbacks to apply */
  function bimTlSetbackMask(G,W){
    var z=A3D.site&&A3D.site.zoning,C,pl,m,k,inPlate;
    if(!G.lot){W.push('No lot: no setbacks');return null;}
    if(!z||!(z.front>0||z.side>0||z.rear>0||(z.frontSteps||[]).length||(z.sideSteps||[]).length||(z.rearSteps||[]).length)){W.push('No setbacks are recorded in the zoning (Legal): none is excluded');return null;}
    try{C=bimZnCalc();}catch(eZ){C={error:String(eZ&&eZ.message||eZ)};}
    if(!C||C.error){W.push('The setbacks could not be worked out: '+(C&&C.error||'no zoning'));return null;}
    pl=bimZnPlate(C,0,-1);
    if(pl===null){W.push('The setbacks could not be drawn for this lot\'s shape');return null;}
    m=new Uint8Array(G.n);inPlate=new Uint8Array(G.n);
    if(pl.length>=3)bimTlFillPoly(G,pl.map(function(c){return c.p;}),inPlate,1);
    for(k=0;k<G.n;k++)if(G.lot[k]&&!inPlate[k])m[k]=1;
    return m;
  }
  /* the cells of the ground plate: inside the lot and its setbacks (the lot itself with none) */
  function bimTlPlateMask(G){
    var W=[],sb=bimTlSetbackMask(G,W),m=new Uint8Array(G.n),k;
    if(!G.lot)return {m:null,why:'No lot'};
    for(k=0;k<G.n;k++)m[k]=G.lot[k]&&!(sb&&sb[k])?1:0;
    return {m:m,why:sb?'':W[0]};
  }
  /* ---- Buffer ---- */
  BIM_TL_TOOLS.push({id:'buffer',name:'Buffer',cmd:'BUFFER',
    sum:'The area within a distance of a layer\'s features: around the streets, the lot line, the trees or the flood zones.',
    how:'Each cell whose centre is within the distance of a cell of the features, measured centre to centre in a straight line (planar: the model is in metres). '+
      'For an area, Outside keeps only what is around it and Inside only the band within its edge. Overlapping buffers are one area, as Esri\'s Dissolve All makes them.',
    params:[
      {id:'src',label:'Input layer',t:'src',req:true,kinds:['area','line','point'],def:'streets',help:'The features to buffer'},
      {id:'dist',label:'Distance',t:'num',req:true,unit:'m',min:0,gt:true,max:BIM_TL_MARGIN,def:10,help:'Up to the extent\'s margin around the lot'},
      {id:'side',label:'Side',t:'sel',def:'full',opts:[['full','The features and around them'],['outside','Outside an area only'],['inside','Inside an area only']],help:'Outside and Inside are for an area layer'}],
    check:function(P,G,E){var s=bimTlSrc(P.src);if(s&&s.kind!=='area'&&P.side!=='full')E.side='Outside or Inside is for an area layer';},
    run:function(P,G,M){
      var s=bimTlSourceOf(G,P.src),sd=bimTlSrc(P.src),m=s.m,lv=new Int16Array(G.n),k,D,out,rows=[],c;
      if(P.side==='inside'){out=new Uint8Array(G.n);for(k=0;k<G.n;k++)out[k]=m[k]?0:1;D=bimTlDistance(G,out);for(k=0;k<G.n;k++)lv[k]=m[k]&&(!D||D[k]<=P.dist+1e-9)?0:-1;}
      else{D=bimTlDistance(G,m);for(k=0;k<G.n;k++)lv[k]=D&&D[k]<=P.dist+1e-9&&(P.side==='full'||!m[k])?0:-1;}
      c=bimTlMaskStats(G,lv,rows);
      bimTlInfo(M,'Within the processing extent: '+bimTlExtentText(G)+'; features beyond it are not counted');
      var nm=sd.name+', '+bimDispNum(P.dist,2)+' m'+(P.side==='outside'?', outside':P.side==='inside'?', inside':'');
      return {stats:rows,label:nm,sum:bimTlAreaText(bimTlArea(c.all,G))+(G.lot?', '+bimTlAreaText(bimTlArea(c.lot,G))+' on the lot':''),
        layer:{name:nm,lv:lv,n:1,pal:[BIM_TL_BUF_COL],keys:[{name:'Within '+bimDispNum(P.dist,2)+' m of '+sd.name.toLowerCase(),col:BIM_TL_BUF_COL}],opacity:0.55}};
    }});
  /* ---- Distance ---- */
  BIM_TL_TOOLS.push({id:'distance',name:'Distance',cmd:'DISTANCEFROM',
    sum:'The straight-line distance from each cell to the nearest of a layer\'s features, as Esri\'s Euclidean Distance gives it.',
    how:'Felzenszwalb and Huttenlocher\'s exact distance transform over the grid, from each cell\'s centre to the nearest feature cell\'s centre. '+
      'With a maximum distance, the cells beyond it have no value.',
    params:[
      {id:'src',label:'Input layer',t:'src',req:true,kinds:['area','line','point'],def:'streets',help:'The features to measure from'},
      {id:'max',label:'Maximum distance',t:'num',unit:'m',min:0,gt:true,def:null,help:'Optional: beyond it, no value'}],
    run:function(P,G,M){
      var s=bimTlSourceOf(G,P.src),sd=bimTlSrc(P.src),D=bimTlDistance(G,s.m),V=new Float64Array(G.n),k,rg,lo,hi,lv,pal,rows=[],L=bimTlInLot(G),n=0,sum=0,mn=Infinity,mx=-Infinity;
      if(!D)return {error:'None of '+sd.name.toLowerCase()+' is within the processing extent'};
      for(k=0;k<G.n;k++)V[k]=P.max!==null&&D[k]>P.max+1e-9?NaN:D[k];
      rg=bimTlRange(V);lo=0;hi=P.max!==null?P.max:(rg?rg[1]:0);
      lv=bimTlQuant(V,lo,hi,BIM_TL_LEVELS);pal=bimTlRamp(BIM_TL_RAMP_DIST,BIM_TL_LEVELS);
      for(k=0;k<G.n;k++)if(L[k]&&isFinite(V[k])){n++;sum+=V[k];if(V[k]<mn)mn=V[k];if(V[k]>mx)mx=V[k];}
      if(n){rows.push([G.lot?'On the lot, nearest':'Nearest',bimDispNum(mn,1)+' m']);rows.push([G.lot?'On the lot, mean':'Mean',bimDispNum(sum/n,1)+' m']);rows.push([G.lot?'On the lot, farthest':'Farthest',bimDispNum(mx,1)+' m']);}
      else rows.push(['On the lot','beyond the maximum distance']);
      bimTlInfo(M,'Within the processing extent: '+bimTlExtentText(G)+'; features beyond it are not counted');
      var nm='from '+sd.name.toLowerCase()+(P.max!==null?', up to '+bimDispNum(P.max,2)+' m':'');
      return {stats:rows,label:nm,sum:n?bimDispNum(mn,1)+' to '+bimDispNum(mx,1)+' m '+(G.lot?'on the lot':'around the site'):'Nothing within the maximum distance',
        layer:{name:nm,lv:lv,n:BIM_TL_LEVELS,pal:pal,lo:lo,hi:hi,unit:'m',keys:[{name:'0 m',col:pal[0]},{name:bimDispNum(hi,0)+' m',col:pal[pal.length-1]}],opacity:0.7}};
    }});
  /* ---- Slope classes ---- */
  BIM_TL_TOOLS.push({id:'slopecls',name:'Slope classes',cmd:'SLOPECLASSES',
    sum:'The ground\'s slope in the standards registry\'s classes for development, on the lot and around it.',
    how:'The slope of V165\'s 5 m ground (Horn\'s method), between its points, reclassified by the registry\'s bounds (Slope classes for development): a slope at a bound is in the class above it.',
    params:[],
    check:function(P,G,E){var s=bimTlSourceOf(G,'slope');if(s.why)E._=s.why;},
    run:function(P,G,M){
      var s=bimTlSourceOf(G,'slope'),C=bimLandSlope(),lv=new Int16Array(G.n),cnt=[],k,i,L=bimTlInLot(G),rows=[],tot=0;
      for(i=0;i<C.length;i++)cnt.push(0);
      for(k=0;k<G.n;k++){
        if(!isFinite(s.v[k])){lv[k]=-1;continue;}
        for(i=0;i<C.length-1;i++)if(s.v[k]<C[i][1])break;
        lv[k]=i;if(L[k]){cnt[i]++;tot++;}
      }
      for(i=0;i<C.length;i++)if(cnt[i])rows.push([C[i][2],bimTlAreaText(bimTlArea(cnt[i],G))+' ('+bimDispNum(100*cnt[i]/(tot||1),1)+'%)']);
      bimTlInfo(M,'The slope is '+(s.src||'the ground')+', between its points; '+bimStdUsedText('land.slope'));
      return {stats:rows,std:['land.slope'],label:G.lot?'the lot and around it':'around the site',sum:rows.map(function(r){return r[0]+' '+r[1];}).join('; '),
        layer:{name:'by the registry\'s classes',lv:lv,n:C.length,pal:C.map(function(c){return c[5];}),cats:C.map(function(c){return c[2];}),
          keys:C.filter(function(c,j){return cnt[j]>0;}).map(function(c){return {name:c[2],col:c[5]};}),opacity:0.7}};
    }});
  /* ---- Exclusions ---- */
  BIM_TL_TOOLS.push({id:'exclude',name:'Exclusions',cmd:'EXCLUSIONS',
    sum:'Where building is restricted, by what is known to be there: outside the lot, the setbacks, flood zones, wetlands, steep slopes, buildings, a buffer.',
    how:'Each cell takes the first of the reasons ticked that applies to it, in the order listed. Restricted is a decision about what is there; a cell where nothing is known stays without a value, '+
      'as Esri keeps Restricted apart from NoData. Suitability leaves the restricted cells out.',
    params:[
      {id:'outside',label:'Outside the lot',t:'bool',def:true},
      {id:'setbacks',label:'Inside the zoning setbacks',t:'bool',def:true},
      {id:'flood',label:'Flood zones (1% annual chance)',t:'bool',def:true},
      {id:'wetlands',label:'Wetlands',t:'bool',def:true},
      {id:'steep',label:'Steep slopes',t:'bool',def:true},
      {id:'steepAt',label:'Steep from',t:'num',unit:'%',min:0,gt:true,max:100,def:function(){return bimStd('land.slope','b4');},help:'The registry\'s steep bound by default'},
      {id:'buildings',label:'Buildings standing now',t:'bool',def:false},
      {id:'buffer',label:'A buffer from History',t:'run',of:'buffer',def:''}],
    check:function(P,G,E,W){
      if(!P.outside&&!P.setbacks&&!P.flood&&!P.wetlands&&!P.steep&&!P.buildings&&!P.buffer)E._='Tick at least one reason, or pick a buffer';
      if((P.outside||P.setbacks)&&!G.lot)E[P.outside?'outside':'setbacks']='No lot yet: draw the property line (Site, Property)';
      if(P.steep&&(P.steepAt===null||!isFinite(P.steepAt)))E.steepAt='Required for steep slopes';
      [['flood','flood'],['wetlands','wetlands'],['steep','slope'],['buildings','buildings']].forEach(function(x){
        if(!P[x[0]])return;var s=bimTlSourceOf(G,x[1]);if(s.why)W[x[0]]=s.why+': nothing is excluded for it';});
    },
    run:function(P,G,M){
      var lv=new Int16Array(G.n),k,i,masks=[],cnt=[],rows=[],W=[],L=bimTlInLot(G),s,on=[];
      lv.fill(-1);
      function add(i,m){masks[i]=m;}
      if(P.outside&&G.lot){var o=new Uint8Array(G.n);for(k=0;k<G.n;k++)o[k]=G.lot[k]?0:1;add(0,o);}
      if(P.setbacks){var sb=bimTlSetbackMask(G,W);if(sb)add(1,sb);}
      if(P.flood){s=bimTlSourceOf(G,'flood');if(s.m)add(2,s.m);}
      if(P.wetlands){s=bimTlSourceOf(G,'wetlands');if(s.m)add(3,s.m);}
      if(P.steep){s=bimTlSourceOf(G,'slope');if(s.v){var st=new Uint8Array(G.n);for(k=0;k<G.n;k++)st[k]=isFinite(s.v[k])&&s.v[k]>=P.steepAt-1e-9?1:0;add(4,st);}}
      if(P.buildings){s=bimTlSourceOf(G,'buildings');if(s.m)add(5,s.m);}
      if(P.buffer){var B=bimTlRunOut(P.buffer,G);if(B.lv){var bm=new Uint8Array(G.n);for(k=0;k<G.n;k++)bm[k]=B.lv[k]>=0?1:0;add(6,bm);}}
      for(i=0;i<BIM_TL_EXCL.length;i++)cnt.push(0);
      for(k=0;k<G.n;k++)for(i=0;i<BIM_TL_EXCL.length;i++)if(masks[i]&&masks[i][k]){lv[k]=i;if(L[k])cnt[i]++;break;}
      W.forEach(function(w){bimTlWarn(M,w);});
      var tot=0;for(i=0;i<cnt.length;i++){if(masks[i])on.push(BIM_TL_EXCL[i].name.toLowerCase());if(cnt[i]&&i>0){rows.push([BIM_TL_EXCL[i].name,bimTlAreaText(bimTlArea(cnt[i],G))]);tot+=cnt[i];}}
      if(G.lot){rows.unshift(['Restricted on the lot',bimTlAreaText(bimTlArea(tot,G))+' of '+bimTlAreaText(G.lotArea)]);rows.push(['Left to use',bimTlAreaText(Math.max(0,G.lotArea-bimTlArea(tot,G)))]);}
      if(P.steep)bimTlInfo(M,'Steep from '+bimDispNum(P.steepAt,2)+'%'+(P.steepAt===bimStd('land.slope','b4')?': '+bimStdUsedText('land.slope'):', set here'));
      return {stats:rows,std:P.steep&&P.steepAt===bimStd('land.slope','b4')?['land.slope|b4']:[],label:on.join(', ')||'nothing',sum:G.lot?bimTlAreaText(bimTlArea(tot,G))+' of the lot restricted':'',
        layer:{name:on.join(', ')||'nothing',lv:lv,n:BIM_TL_EXCL.length,pal:BIM_TL_EXCL.map(function(x){return x.col;}),cats:BIM_TL_EXCL.map(function(x){return x.name;}),
          keys:BIM_TL_EXCL.filter(function(x,j){return !!masks[j];}).map(function(x){return {name:x.name,col:x.col};}),opacity:0.6}};
    }});
