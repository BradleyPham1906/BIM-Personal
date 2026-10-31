  /* ================= __acad3dV172: the site analysis tools: what they read =================
     The layers a tool can take as input, each drawn on the tool grid from what the project already keeps: the lot
     and its edge (the property line), the streets (V161's network, every class, and the arterials alone), the
     buildings and the trees around (V157's context), FEMA's 1% annual chance zones (V165), the wetlands (the
     National Wetlands Inventory, fetched here), the ground's slope (V165's 5 m grid, Horn's method) and the sun
     hours of the last run (V143). Each says why it is empty when it is. */
  var BIM_TL_NWI='https://fwspublicservices.wim.usgs.gov/wetlandsmapservice/rest/services/Wetlands/MapServer/0/query';
  var BIM_TL_SRC=[
    {id:'lot',name:'The lot',kind:'area'},
    {id:'lotedge',name:'The lot line',kind:'line'},
    {id:'streets',name:'Streets and paths',kind:'line'},
    {id:'arterials',name:'Arterial roads',kind:'line'},
    {id:'buildings',name:'Buildings around',kind:'area'},
    {id:'trees',name:'Trees',kind:'point'},
    {id:'forest',name:'Woods and tree crowns',kind:'area'},
    {id:'water',name:'Ponds and water',kind:'area'},
    {id:'flood',name:'Flood zones (1% annual chance)',kind:'area'},
    {id:'wetlands',name:'Wetlands (NWI)',kind:'area'},
    {id:'slope',name:'Slope of the ground',kind:'value',unit:'%'},
    {id:'sunhours',name:'Sun hours (the last run)',kind:'value',unit:'h'}];
  function bimTlSrc(id){var i;for(i=0;i<BIM_TL_SRC.length;i++)if(BIM_TL_SRC[i].id===id)return BIM_TL_SRC[i];return null;}
  /* what the project keeps for the tools: their history and the wetlands fetched */
  function bimTlState(){
    A3D.site=A3D.site||{};
    var T=A3D.site.tools;
    if(!T||typeof T!=='object')T=A3D.site.tools={};
    if(!Array.isArray(T.history))T.history=[];
    if(!T.params||typeof T.params!=='object')T.params={};
    return T;
  }
  /* a source on the grid: {m: a mask of its cells} for a feature layer, {v: values, NaN where none} for a value
     layer; or {why} when the project has none of it yet */
  function bimTlSource(G,id){
    var m=new Uint8Array(G.n),n=0,i,k,S=G.site;
    function lineRing(r){for(k=0;k<r.length;k++)bimTlStroke(G,r[k],r[(k+1)%r.length],m,1);}
    if(id==='lot'){if(!G.lot)return {why:'No property line yet: draw the lot (Site, Property)'};return {m:G.lot};}
    if(id==='lotedge'){if(!G.ring)return {why:'No property line yet: draw the lot (Site, Property)'};lineRing(G.ring);return {m:m};}
    if(id==='streets'||id==='arterials'){
      var A=A3D.site&&A3D.site.access,segs=A&&Array.isArray(A.segs)?A.segs:null;
      if(!segs)return {why:'No streets yet: Analyze site gets them from OpenStreetMap'};
      segs.forEach(function(s){
        if(!Array.isArray(s)||s.length<7)return;
        if(id==='arterials'&&s[0]!=='a')return;
        for(k=1;k+5<s.length;k+=3){bimTlStroke(G,[s[k],s[k+1]],[s[k+3],s[k+4]],m,1);n++;}
      });
      if(!n)return {why:id==='arterials'?'No arterial road within the walk the access data kept':'The access data has no street'};
      return {m:m};
    }
    if(id==='buildings'){
      var B=bimLdBuildings();
      if(!B.length)return {why:'No buildings around yet: Analyze site gets the context'};
      B.forEach(function(b){if(b.ground)bimTlFillPoly(G,b.fp,m,1);});
      return {m:m};
    }
    if(id==='trees'){
      var Tr=bimLdTrees();
      if(!Tr.length)return {why:'No trees yet: Analyze site gets the context'};
      Tr.forEach(function(t){bimTlPoint(G,[t.x,t.z],t.r,m,1);});
      return {m:m};
    }
    if(id==='forest'){
      var Tf=bimLdTrees(),Wd=bimLdAreas().filter(bimLdWood);
      if(!Tf.length&&!Wd.length)return {why:'No trees or woods yet: Analyze site gets the context'};
      Tf.forEach(function(t){bimTlPoint(G,[t.x,t.z],t.r,m,1);});
      bimTlFillAreas(G,Wd,m);
      return {m:m,none:!bimTlCount(G,m)};
    }
    if(id==='water'){
      var Wa=bimTlContextAreas('water');
      if(Wa===null)return {why:'No context yet: Analyze site gets the water around'};
      bimTlFillAreas(G,Wa,m);
      return {m:m,none:!bimTlCount(G,m)};
    }
    if(id==='flood'){
      var LD=A3D.site&&A3D.site.land,F=LD&&LD.flood;
      if(!F)return {why:'Not fetched yet: Analyze site gets FEMA\'s flood map'};
      if(F.outside)return {why:'FEMA maps US sites only'};
      var Z=bimLandFloodZones(S),sh=new Uint8Array(G.n);
      Z.zones.forEach(function(z){if(z.zc==='floodway'||z.zc==='coastal'||z.zc==='sfha'){z.rings.forEach(function(r){sh.fill(0);bimTlFillPoly(G,r,sh,1);for(k=0;k<G.n;k++)if(sh[k])m[k]=1;});}});
      return {m:m,none:!bimTlCount(G,m)};
    }
    if(id==='wetlands'){
      var W=bimTlState().wetlands;
      if(!W)return {why:'Not fetched yet: Get wetlands, in Buildable area'};
      if(W.outside)return {why:'The National Wetlands Inventory maps US sites only'};
      if(W.error)return {why:'The wetlands could not be fetched: '+W.error};
      var sw=new Uint8Array(G.n);
      (W.f||[]).forEach(function(f){f.rings.forEach(function(r){sw.fill(0);bimTlFillPoly(G,r,sw,1);for(k=0;k<G.n;k++)if(sw[k])m[k]=1;});});
      return {m:m,none:!bimTlCount(G,m)};
    }
    if(id==='slope'){
      var D=bimLandGround(S);
      if(!D)return {why:'No ground yet: Analyze site gets the terrain'};
      var hs=bimLandHornOf(D).slope,v=new Float64Array(G.n),j,gx,gz,i0,j0,fx,fz,q,w,s,t,mm;
      for(j=0;j<G.nz;j++)for(i=0;i<G.nx;i++){
        gx=(bimTlCx(G,i)-D.x0)/D.cell;gz=(bimTlCz(G,j)-D.z0)/D.cell;k=j*G.nx+i;
        if(gx<0||gz<0||gx>D.nx-1||gz>D.nz-1){v[k]=NaN;continue;}
        i0=Math.min(D.nx-2,Math.floor(gx));j0=Math.min(D.nz-2,Math.floor(gz));fx=gx-i0;fz=gz-j0;
        q=[j0*D.nx+i0,j0*D.nx+i0+1,(j0+1)*D.nx+i0,(j0+1)*D.nx+i0+1];w=[(1-fx)*(1-fz),fx*(1-fz),(1-fx)*fz,fx*fz];s=0;t=0;
        for(mm=0;mm<4;mm++)if(isFinite(hs[q[mm]])){s+=w[mm]*hs[q[mm]];t+=w[mm];}
        v[k]=t>1e-9?s/t:NaN;
      }
      return {v:v,src:D.srcShort};
    }
    if(id==='sunhours'){
      var r=A3D_SIM.sun;
      if(!r||!r.hours)return {why:'Run Sun hours first (Analyze, Model)'};
      var vv=new Float64Array(G.n),jj,ii,a,b;
      for(jj=0;jj<G.nz;jj++)for(ii=0;ii<G.nx;ii++){
        a=Math.floor((bimTlCx(G,ii)-r.x0)/r.cell);b=Math.floor((bimTlCz(G,jj)-r.z0)/r.cell);k=jj*G.nx+ii;
        vv[k]=a>=0&&b>=0&&a<r.nx&&b<r.nz&&!r.roof[b*r.nx+a]?r.hours[b*r.nx+a]:NaN;
      }
      return {v:vv,src:'Sun hours on '+r.date};
    }
    return {why:'No such layer'};
  }
  /* areas with their holes ({outer:[rings], holes:[rings]}), filled on a mask */
  function bimTlFillAreas(G,A,m){
    var sh=new Uint8Array(G.n),k;
    A.forEach(function(a){
      sh.fill(0);
      a.outer.forEach(function(r){var t=new Uint8Array(G.n);bimTlFillPoly(G,r,t,1);for(k=0;k<G.n;k++)if(t[k])sh[k]=1;});
      a.holes.forEach(function(r){var t=new Uint8Array(G.n);bimTlFillPoly(G,r,t,1);for(k=0;k<G.n;k++)if(t[k])sh[k]=0;});
      for(k=0;k<G.n;k++)if(sh[k])m[k]=1;
    });
  }
  /* the context's closed areas of a kind, grouped with their holes as V168 groups them; null with no context at all */
  function bimTlContextAreas(kind){
    var G={},order=[],i,o,c,q,any=false;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(!c)continue;
      any=true;
      if(c.kind!==kind||!o.closed||!o.pts||o.pts.length<3)continue;
      q=bimObjOffset(o);
      var key=(c.osm||'')+':'+(c.id===undefined?o.id:c.id),P=o.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
      if(!G[key]){G[key]={outer:[],holes:[]};order.push(key);}
      (c.part==='hole'?G[key].holes:G[key].outer).push(P);
    }
    return any?order.map(function(k){return G[k];}).filter(function(a){return a.outer.length;}):null;
  }
  /* ---- the wetlands: the National Wetlands Inventory's map service, over the grid's extent ---- */
  function bimTlWetlandsFetch(done){
    var G=bimTlGrid(),org=bimMapOrigin(),T=bimTlState(),c,ll,lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,url;
    if(!org){a3dToast('Place the site on the map first (Site, Location)');if(done)done(false);return false;}
    c=[[G.x0,G.z0],[G.x0+G.nx*G.cell,G.z0],[G.x0,G.z0+G.nz*G.cell],[G.x0+G.nx*G.cell,G.z0+G.nz*G.cell]];
    c.forEach(function(p){ll=bimModelToGeo(p[0],p[1]);lo0=Math.min(lo0,ll[0]);lo1=Math.max(lo1,ll[0]);la0=Math.min(la0,ll[1]);la1=Math.max(la1,ll[1]);});
    if(!bimLandUS(org)){T.wetlands={outside:true,fetched:bimSaToday()};saveSoon();if(done)done(true);return true;}   /* the inventory maps the US only */
    url=BIM_TL_NWI+'?'+bimClimQs({where:'1=1',geometry:[lo0,la0,lo1,la1].map(function(x){return x.toFixed(6);}).join(','),geometryType:'esriGeometryEnvelope',
      inSR:4326,outSR:4326,spatialRel:'esriSpatialRelIntersects',outFields:'WETLAND_TYPE,ATTRIBUTE',returnGeometry:'true',geometryPrecision:6,f:'json'});
    fetch(url).then(function(r){if(!r.ok)throw new Error('the service answered '+r.status);return r.json();}).then(function(js){
      if(js&&js.error)throw new Error(String(js.error.message||'an error'));
      var F=[];
      (js.features||[]).forEach(function(f){
        var g=f.geometry,a=f.attributes||{};
        if(!g||!Array.isArray(g.rings))return;
        F.push({type:String(a.WETLAND_TYPE||'Wetland'),code:String(a.ATTRIBUTE||''),rings:g.rings.map(function(r){return r.map(function(p){var q=bimGeoToModel(p[0],p[1]);return [Math.round(q[0]*100)/100,Math.round(q[1]*100)/100];});})});
      });
      pushUndo();
      T.wetlands={f:F,fetched:bimSaToday(),src:'U.S. Fish and Wildlife Service, National Wetlands Inventory (fwspublicservices.wim.usgs.gov)',more:!!js.exceededTransferLimit};
      saveSoon();
      if(done)done(true);
    }).catch(function(e){
      console.warn('[BIM] The wetlands could not be fetched',e);
      T.wetlands={error:String(e&&e.message||e).slice(0,160),fetched:bimSaToday()};
      a3dToast('The wetlands could not be fetched: '+T.wetlands.error);
      if(done)done(false);
    });
    return true;
  }
