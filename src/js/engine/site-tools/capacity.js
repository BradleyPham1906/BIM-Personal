  /* ================= __acad3dV172: the site analysis tools: Buildable area and Constraints and opportunities =================
     Buildable area is Pennsylvania's site capacity calculation (research-site-analysis-tools.md, 4; the owner chose it,
     2026-10-27), its ratios the standards registry's (Chalfont's section 440-17 the first record): the base site area, the
     total less rights-of-way and land set aside; each resource's land on the lot times its open space ratio, where
     resources overlap only the highest ratio counting (and forest with another resource its own ratio); the net
     buildable site area, the base less that; the dwelling units it allows at the district's density, not rounded up;
     the impervious surface at its ratio; and where to build, within the setbacks and clear of every resource.
     Constraints and opportunities is the summary the councils ask a site analysis plan for: what limits the site and
     what it offers, on one plan, each from the layer it came from. */
  var BIM_TL_CAP=[
    {id:'flood',name:'Floodplain',r:function(){return bimStd('land.site_capacity','floodplain');},col:'#3d85d8'},
    {id:'wetland',name:'Wetland',r:function(){return bimStd('land.site_capacity','wetland');},col:'#3d9970'},
    {id:'water',name:'Pond or water',r:function(){return Math.max(bimStd('land.site_capacity','pond'),bimStd('land.site_capacity','waters'));},col:'#1f5f8b'},
    {id:'steep2',name:'Steep slope, the upper class',r:function(){return bimStd('land.site_capacity','slope_b');},col:'#c0504d'},
    {id:'steep1',name:'Steep slope, the lower class',r:function(){return bimStd('land.site_capacity','slope_a');},col:'#e8833a'},
    {id:'forestw',name:'Forest with another resource',r:function(){return bimStd('land.site_capacity','forest_with');},col:'#2e7d32'},
    {id:'forest',name:'Forest',r:function(){return bimStd('land.site_capacity','forest');},col:'#7cb342'}];
  var BIM_TL_CAP_OK='#ffe58a',BIM_TL_CAP_SB='#d9d9d9';
  /* a category's name with its bounds and ratio, in words */
  function bimTlCapName(c){
    var lo=bimStdSay('land.site_capacity','slope_lo'),hi=bimStdSay('land.site_capacity','slope_hi');
    var n=c.id==='steep2'?'Slope of '+hi+' or more':c.id==='steep1'?'Slope of '+lo+' to '+hi:c.name;
    return n+', ratio '+bimDispNum(c.r(),2);
  }
  /* each lot cell's resource: the one with the highest ratio of those there, in the list's order among equals */
  function bimTlCapCells(G,M){
    var R={},k,i,lv=new Int16Array(G.n),lo=bimStd('land.site_capacity','slope_lo'),hi=bimStd('land.site_capacity','slope_hi'),fl,we,wa,sl,fo,miss=[];
    function mask(id,what){var s=bimTlSourceOf(G,id);if(s.why){miss.push(what+': '+s.why);return null;}return s;}
    fl=mask('flood','Floodplains');we=mask('wetlands','Wetlands');wa=mask('water','Ponds and water');sl=mask('slope','Steep slopes');fo=mask('forest','Forest');
    var r=BIM_TL_CAP.map(function(c){return c.r();});
    lv.fill(-1);
    for(k=0;k<G.n;k++){
      if(!G.lot[k])continue;
      var has=[fl&&fl.m[k],we&&we.m[k],wa&&wa.m[k],sl&&isFinite(sl.v[k])&&sl.v[k]>=hi-1e-9,sl&&isFinite(sl.v[k])&&sl.v[k]>=lo-1e-9&&sl.v[k]<hi-1e-9,false,fo&&fo.m[k]],
        other=has[0]||has[1]||has[2]||has[3]||has[4],best=-1,bv=-1;
      if(has[6]&&other){has[5]=true;has[6]=false;}
      for(i=0;i<has.length;i++)if(has[i]&&r[i]>bv+1e-12){bv=r[i];best=i;}
      lv[k]=best;
    }
    return {lv:lv,r:r,miss:miss};
  }
  BIM_TL_TOOLS.push({id:'capacity',name:'Buildable area',cmd:'BUILDABLE',
    sum:'Pennsylvania\'s site capacity calculation: the base site area less the resource protection land gives the net buildable site area; then where to build, inside the setbacks and clear of the resources.',
    how:'Each resource\'s land on the lot (floodplains, wetlands, ponds and water, steep slopes in two classes, forest) times its open space ratio, from the standards registry. '+
      'Where resources overlap only the highest ratio counts, and forest with another resource takes its own ratio. The resources are counted on the grid\'s cells; the site\'s total area is the property line\'s.',
    params:[
      {id:'less',label:'Rights-of-way and land set aside',t:'num',unit:'m\u00b2',min:0,def:0,max:function(P,G){return G.ring?Math.abs(bimPolyArea(G.ring)):null;},help:'Future road and utility rights-of-way, land cut off, land reserved as open space'},
      {id:'density',label:'Density allowed',t:'num',unit:'du/acre',min:0,gt:true,def:null,help:'Optional: dwelling units an acre, from the district\'s regulations'},
      {id:'imperv',label:'Impervious surface ratio',t:'num',unit:'%',min:0,max:100,def:null,help:'Optional: the district\'s maximum'}],
    check:function(P,G,E,W){
      if(!G.lot){E._='No lot yet: draw the property line (Site, Property)';return;}
      var wl=bimTlState().wetlands;
      if(!wl)W._='The wetlands are not fetched: Get wetlands counts them';
    },
    run:function(P,G,M){
      var C=bimTlCapCells(G,M),k,i,cnt=[],rows=[],tot=Math.abs(bimPolyArea(G.ring)),base=Math.max(0,tot-(P.less||0)),prot=0,land=0,pl=bimTlPlateMask(G),ok=0,okSb=0,lv=C.lv,j;
      for(i=0;i<BIM_TL_CAP.length;i++)cnt.push(0);
      for(k=0;k<G.n;k++){
        if(!G.lot[k])continue;
        if(lv[k]>=0){cnt[lv[k]]++;continue;}
        if(pl.m&&pl.m[k]){lv[k]=BIM_TL_CAP.length;ok++;}else{lv[k]=BIM_TL_CAP.length+1;okSb++;}
      }
      C.miss.forEach(function(w){bimTlWarn(M,w+' -- counted as none');});
      if(pl.why)bimTlInfo(M,pl.why);
      function ac(m2){return bimDispNum(m2/BIM_TL_ACRE,2)+' acres';}
      rows.push(['Total site area',bimTlAreaText(tot)+' ('+ac(tot)+')']);
      if(P.less)rows.push(['Less rights-of-way and land set aside',bimTlAreaText(P.less)]);
      rows.push(['Base site area',bimTlAreaText(base)+' ('+ac(base)+')']);
      for(i=0;i<BIM_TL_CAP.length;i++){
        if(!cnt[i])continue;
        var a=bimTlArea(cnt[i],G);land+=a;prot+=a*C.r[i];
        rows.push([bimTlCapName(BIM_TL_CAP[i]),bimTlAreaText(a)+', protecting '+bimTlAreaText(a*C.r[i])]);
      }
      rows.push(['Land with resource restrictions',bimTlAreaText(land)]);
      rows.push(['Resource protection land',bimTlAreaText(prot)+' ('+ac(prot)+')']);
      var net=Math.max(0,base-prot);
      rows.push(['Net buildable site area',bimTlAreaText(net)+' ('+ac(net)+')']);
      if(P.density!==null)rows.push(['Dwelling units allowed',String(Math.floor(net/BIM_TL_ACRE*P.density+1e-9))+' at '+bimDispNum(P.density,2)+' an acre (not rounded up)']);
      if(P.imperv!==null)rows.push(['Impervious surface allowed',bimTlAreaText(net*P.imperv/100)+' at '+bimDispNum(P.imperv,2)+'%']);
      rows.push(['Buildable within the setbacks, clear of every resource',bimTlAreaText(bimTlArea(ok,G))]);
      bimTlInfo(M,'Pond shores and wetland margins are not counted: their extent is defined elsewhere in the ordinance, not read');
      bimTlInfo(M,bimStdUsedText('land.site_capacity'));
      var cats=BIM_TL_CAP.map(bimTlCapName).concat(['Buildable within the setbacks','Clear, in the setbacks']),pal=BIM_TL_CAP.map(function(c){return c.col;}).concat([BIM_TL_CAP_OK,BIM_TL_CAP_SB]),keys=[];
      for(j=0;j<cats.length;j++)if((j<BIM_TL_CAP.length?cnt[j]:(j===BIM_TL_CAP.length?ok:okSb))>0)keys.push({name:cats[j],col:pal[j]});
      return {stats:rows,std:['land.site_capacity'],label:'site capacity',sum:'net buildable '+bimTlAreaText(net)+' of '+bimTlAreaText(tot),
        keep:function(T,h){h.capacity={total:tot,base:base,land:land,prot:prot,net:net,ok:bimTlArea(ok,G)};},
        layer:{name:'site capacity',lv:lv,n:cats.length,pal:pal,cats:cats,keys:keys,opacity:0.7}};
    }});
  /* ---- Constraints and opportunities ---- */
  var BIM_TL_SYN=[
    {id:'flood',name:'Flood zone (1% annual chance)',con:true,col:'#c0392b'},
    {id:'wetland',name:'Wetland',con:true,col:'#a04000'},
    {id:'steep',name:'Steep slope',con:true,col:'#e67e22'},
    {id:'building',name:'Building standing now',con:true,col:'#7f4f24'},
    {id:'setback',name:'In the setbacks',con:true,col:'#d98880'},
    {id:'noise',name:'Near an arterial road',con:true,col:'#f5b041'},
    {id:'shade',name:'Overshadowed',con:true,col:'#8e6c8a'},
    {id:'frontage',name:'Street frontage',con:false,col:'#1f77b4'},
    {id:'sun',name:'Sunny',con:false,col:'#f1c40f'},
    {id:'green',name:'Near trees and woods',con:false,col:'#2e8b57'},
    {id:'flat',name:'Flat to gentle ground',con:false,col:'#76b7b2'}];
  BIM_TL_TOOLS.push({id:'synth',name:'Constraints and opportunities',cmd:'CONSTRAINTSMAP',
    sum:'What limits the site and what it offers, on one plan: flood, wetlands, steep ground, buildings, the setbacks, road noise and shade against frontage, sun, trees and flat ground.',
    how:'Each cell takes the first constraint that applies to it, in the order of the key, else the first opportunity. Each comes from a layer the project has: '+
      'FEMA\'s zones, the wetlands, the ground\'s slope (the registry\'s classes), the buildings, the zoning setbacks, the streets, the sun hours of the last run, the trees. '+
      'Its distances and hours are the app\'s working set in the standards registry.',
    params:[{id:'scope',label:'Where',t:'sel',def:'lot',opts:[['lot','On the lot'],['all','The whole extent']]}],
    check:function(P,G,E){if(P.scope==='lot'&&!G.lot)E.scope='No lot yet: pick the whole extent';},
    run:function(P,G,M){
      var lv=new Int16Array(G.n),k,i,L=P.scope==='lot'?G.lot:null,ms=[],cnt=[],rows=[],miss=[],s,D,
        na=bimStd('app.synthesis','near_art'),fr=bimStd('app.synthesis','front'),su=bimStd('app.synthesis','sunny'),sh=bimStd('app.synthesis','shade'),gr=bimStd('app.synthesis','green'),
        flat=bimStd('land.slope','b1'),steep=bimStd('land.slope','b4');
      function src(id,what){var x=bimTlSourceOf(G,id);if(x.why){miss.push(what+': '+x.why);return null;}return x;}
      function near(x,d){if(!x)return null;var DD=bimTlDistance(G,x.m),m=new Uint8Array(G.n);if(!DD)return m;for(k=0;k<G.n;k++)m[k]=DD[k]<=d+1e-9?1:0;return m;}
      var fl=src('flood','Flood zones'),we=src('wetlands','Wetlands'),sl=src('slope','Slope'),bu=src('buildings','Buildings'),st=src('streets','Streets'),ar=src('arterials','Arterial roads'),sn=src('sunhours','Sun hours'),fo=src('forest','Trees and woods'),W=[];
      var sb=G.lot?bimTlSetbackMask(G,W):null;
      function vm(x,f){if(!x)return null;var m=new Uint8Array(G.n);for(k=0;k<G.n;k++)m[k]=isFinite(x.v[k])&&f(x.v[k])?1:0;return m;}
      ms=[fl&&fl.m,we&&we.m,vm(sl,function(v){return v>=steep-1e-9;}),bu&&bu.m,sb,near(ar,na),vm(sn,function(v){return v<sh-1e-9;}),
        near(st,fr),vm(sn,function(v){return v>=su-1e-9;}),near(fo,gr),vm(sl,function(v){return v<flat-1e-9;})];
      for(i=0;i<BIM_TL_SYN.length;i++)cnt.push(0);
      lv.fill(-1);
      for(k=0;k<G.n;k++){
        if(L&&!L[k])continue;
        for(i=0;i<ms.length;i++)if(ms[i]&&ms[i][k]){lv[k]=i;cnt[i]++;break;}
      }
      miss.forEach(function(w){bimTlInfo(M,w+' -- not shown');});
      W.forEach(function(w){bimTlInfo(M,w);});
      [true,false].forEach(function(con){
        for(i=0;i<BIM_TL_SYN.length;i++)if(BIM_TL_SYN[i].con===con&&cnt[i])rows.push([(con?'Constraint: ':'Opportunity: ')+BIM_TL_SYN[i].name,bimTlAreaText(bimTlArea(cnt[i],G))]);
      });
      bimTlInfo(M,'Near an arterial within '+bimStdSay('app.synthesis','near_art')+', frontage within '+bimStdSay('app.synthesis','front')+' of a street, sunny from '+bimStdSay('app.synthesis','sunny')+
        ' of sun, overshadowed under '+bimStdSay('app.synthesis','shade')+', near trees within '+bimStdSay('app.synthesis','green')+'; '+bimStdUsedText('app.synthesis'));
      var nc=0,no=0;for(i=0;i<BIM_TL_SYN.length;i++){if(cnt[i]){if(BIM_TL_SYN[i].con)nc++;else no++;}}
      return {stats:rows,std:['app.synthesis','land.slope'],label:P.scope==='lot'?'on the lot':'the whole extent',sum:nc+' constraint'+(nc===1?'':'s')+', '+no+' opportunit'+(no===1?'y':'ies'),
        layer:{name:P.scope==='lot'?'on the lot':'the whole extent',lv:lv,n:BIM_TL_SYN.length,pal:BIM_TL_SYN.map(function(x){return x.col;}),cats:BIM_TL_SYN.map(function(x){return x.name;}),
          keys:BIM_TL_SYN.filter(function(x,j){return cnt[j]>0;}).map(function(x){return {name:(x.con?'Constraint: ':'Opportunity: ')+x.name,col:x.col};}),opacity:0.7}};
    }});
