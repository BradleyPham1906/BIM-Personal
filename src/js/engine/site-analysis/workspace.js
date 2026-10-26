  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================
     The standard is reference/research-site-analysis-process.md: ten fixed categories, and findings
     that each name a source, a date and how sure they are, classed as a constraint, an opportunity,
     a red flag or a fact. Kept with the project in A3D.site.analysis. __acad3dV164: the findings are
     the ones the data writes; the stages, the questions, typed findings, photographs, pins and
     checklists are gone from it, and what a project stored of them stays in its file, unread. */
  var BIM_SA_CATS=[
    {id:'location',n:'Location and context',q:'Where it is, what surrounds it, figure-ground, land use.'},
    {id:'legal',n:'Legal and regulatory',q:'Zoning, permitted uses, FAR, height, setbacks, coverage, parking, easements, ownership, heritage.'},
    {id:'landform',n:'Landform',q:'Topography, slope, aspect, relief, geology, soils.'},
    {id:'water',n:'Water',q:'Drainage, flood zones, water bodies, runoff.'},
    {id:'climate',n:'Climate',q:'Temperature, rain, climate zone, sun path, shadows, wind, solar.'},
    {id:'ecology',n:'Ecology',q:'Vegetation, trees, habitat, protected areas.'},
    {id:'risk',n:'Environmental risk',q:'Seismic, contamination, air quality, noise, wildfire.'},
    {id:'access',n:'Access and circulation',q:'Street hierarchy, street use, transit, walking and cycling, parking, entries.'},
    {id:'utilities',n:'Utilities',q:'Water, sewer, power, stormwater, telecoms.'},
    {id:'people',n:'People and place',q:'Demographics, amenities within a walk, history, views, landmarks, noise sources.'}];
  var BIM_SA_CLS=[['neutral','Fact'],['opportunity','Opportunity'],['constraint','Constraint'],['redflag','Red flag']];
  var BIM_SA_CONF=[['desktop','Desktop'],['site','Seen on site'],['surveyed','Surveyed']];
  var BIM_SA_SEV=[['1','Low'],['2','Medium'],['3','High']];
  function bimSaPair(L,k){var i;for(i=0;i<L.length;i++)if(L[i][0]===k)return L[i][1];return '';}
  function bimSaCat(id){var i;for(i=0;i<BIM_SA_CATS.length;i++)if(BIM_SA_CATS[i].id===id)return BIM_SA_CATS[i];return null;}
  function bimSaToday(){return new Date().toISOString().slice(0,10);}
  /* the record, made when first asked for; read-only callers get the same shape */
  function bimSa(){
    A3D.site=A3D.site||{};
    var s=A3D.site.analysis;
    if(!s||typeof s!=='object')s=A3D.site.analysis={};
    if(!Array.isArray(s.findings))s.findings=[];
    if(!(s.seq>=0))s.seq=0;
    return s;
  }
  /* __acad3dV164: the findings shown -- those the data writes; one typed by hand before stays unread */
  function bimSaShown(){return bimSa().findings.filter(function(f){return !!f.auto;});}
  function bimSaFind(id){var F=bimSa().findings,i;for(i=0;i<F.length;i++)if(F[i].id===id)return F[i];return null;}
  /* "4.2": the category's number, then the finding's place in it */
  function bimSaNumber(f){
    var F=bimSaShown(),ci=-1,k=0,i;
    for(i=0;i<BIM_SA_CATS.length;i++)if(BIM_SA_CATS[i].id===f.cat)ci=i;
    for(i=0;i<F.length;i++){if(F[i].cat===f.cat)k++;if(F[i]===f)break;}
    return (ci+1)+'.'+k;
  }
  function bimSaOf(cat){return bimSaShown().filter(function(f){return f.cat===cat;});}
  function bimSaNew(cat,f){
    var s=bimSa();
    s.seq++;
    return {id:'saf'+s.seq,cat:cat,title:String(f.title||'Finding').slice(0,120),value:String(f.value||'').slice(0,2000),
      cls:bimSaPair(BIM_SA_CLS,f.cls)?f.cls:'neutral',sev:(f.sev>=1&&f.sev<=3)?+f.sev:1,conf:bimSaPair(BIM_SA_CONF,f.conf)?f.conf:'desktop',
      source:String(f.source||'').slice(0,200),date:/^\d{4}-\d{2}-\d{2}$/.test(f.date||'')?f.date:bimSaToday(),note:String(f.note||'').slice(0,2000),
      at:null,photo:null,auto:f.auto||''};
  }
  function bimSaDone(){refreshProps();paint();saveSoon();bimSaRefresh(true);}
  /* ---- what the model already knows ---- */
  function bimSaN(n,one,many){return n+' '+(n===1?one:(many||one+'s'));}
  function bimSaSlope(tin){
    var T=tin.tris||[],out=tin.outside||{},i,a,b,c,P=tin.P,H=tin.H,area=0,sum=0,mx=0,steep=0,sb3=bimStd('land.slope','b3')/100;   /* __acad3dV167h */
    for(i=0;i<T.length;i++){
      if(out[i])continue;
      var v=T[i].v||T[i];a=v[0];b=v[1];c=v[2];
      if(!P[a]||!P[b]||!P[c])continue;
      var x1=P[b][0]-P[a][0],z1=P[b][1]-P[a][1],y1=H[b]-H[a],x2=P[c][0]-P[a][0],z2=P[c][1]-P[a][1],y2=H[c]-H[a];
      var nx=z1*y2-y1*z2,ny=x1*z2-z1*x2,nz=y1*x2-x1*y2,A=Math.abs(ny)/2;
      if(!(A>1e-9))continue;
      var g=Math.sqrt(nx*nx+nz*nz)/Math.abs(ny);
      area+=A;sum+=g*A;if(g>mx)mx=g;if(g>sb3)steep+=A;
    }
    return area>0?{mean:sum/area,max:mx,steepShare:steep/area,area:area}:null;
  }
  function bimSaDayLen(lat,lon,md){
    var r=bimSunCalc(lat,lon,0,new Date().getFullYear()+'-'+md,'12:00');
    if(!r)return null;
    if(r.polar==='day')return 'no sunset';
    if(r.polar==='night')return 'no sunrise';
    var m=Math.round(r.sunset-r.sunrise);
    return Math.floor(m/60)+' h '+bimPad2(m%60)+' min';
  }
  function bimSaAuto(){
    var A=[],today=bimSaToday(),st=bimSunSettings(),ctx=(A3D.site&&A3D.site.context&&A3D.site.context.last)||null,i,o,c;
    var cnt={},uses={},lu={},bh=[],nBr=0,nTu=0,ter=null,cterr=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];c=o.context;
      if(o.t==='terrain'&&o.survey&&!o.grading){if(c&&c.kind==='terrain')cterr=o;else if(!ter)ter=o;}
      if(!c)continue;
      cnt[c.kind]=(cnt[c.kind]||0)+(c.part==='hole'?0:1);
      if(c.kind==='buildings'&&c.height>0)bh.push(c.height);
      if(c.use)uses[c.use]=(uses[c.use]||0)+1;
      if(c.bridge)nBr++;if(c.tunnel)nTu++;
      if(c.kind==='landuse'&&c.tags&&c.tags.landuse)lu[c.tags.landuse]=(lu[c.tags.landuse]||0)+1;
    }
    ter=ter||cterr;
    var osm='OpenStreetMap (ODbL), via Overpass',od=ctx?ctx.date:today,rr=ctx?' within '+ctx.radius+' m':'';
    if(bimSunNum(st.lat)&&bimSunNum(st.lon))
      A.push({auto:'location.place',cat:'location',title:'Location',value:Math.abs(st.lat).toFixed(5)+'\u00b0 '+(st.lat<0?'S':'N')+', '+Math.abs(st.lon).toFixed(5)+'\u00b0 '+(st.lon<0?'W':'E')+((A3D.site&&A3D.site.name)?' ('+A3D.site.name+')':''),source:'Project location',date:today});
    if(cnt.buildings){
      var hs=0,hm=0;for(i=0;i<bh.length;i++){hs+=bh[i];if(bh[i]>hm)hm=bh[i];}
      A.push({auto:'location.built',cat:'location',title:'Built context',value:bimSaN(cnt.buildings,'building')+rr+(bh.length?'; mean height '+(hs/bh.length).toFixed(1)+' m, tallest '+hm.toFixed(1)+' m':''),source:osm,date:od});
    }
    var P=A3D.objs.filter(bimIsProperty);
    if(P.length){
      var g=bimPropertyGeometry(P[0]);
      A.push({auto:'legal.boundary',cat:'legal',title:'Property line',value:P[0].name+': '+bimDispNum(g.area,1)+' m\u00b2, perimeter '+bimDispNum(g.perimeter,1)+' m'+(g.misclosure>0.001?'; does not close by '+bimDispNum(g.misclosure,3)+' m':'')+(P.length>1?' ('+P.length+' property lines)':''),
        cls:g.misclosure>0.01?'constraint':'neutral',sev:g.misclosure>0.01?2:1,source:'Property line'+(P[0].source?' ('+P[0].source+')':''),date:today});
    }
    var DL=bimDataList();
    if(DL.length)A.push({auto:'legal.layers',cat:'legal',title:'Data layers',value:DL.map(function(L){return L.name;}).join(', '),source:DL.map(function(L){return L.credit;}).filter(function(x,j,a){return x&&a.indexOf(x)===j;}).join('; ')||'Data layers',date:today});
    var fl=DL.filter(function(L){return /flood/i.test(L.name||'');});
    if(fl.length)A.push({auto:'water.flood',cat:'water',title:'Flood zones',value:'Loaded: '+fl.map(function(L){return L.name;}).join(', ')+'. Read the zone at the site from the layer.',source:fl[0].credit||'Data layer',date:today});
    if(ter){
      var tin=bimTerrainTin(ter),rg=tin?bimTerrainRange(tin):null,sl=tin?bimSaSlope(tin):null,dat=bimCtxDatum();
      if(rg&&isFinite(rg[0])){
        var off=dat!==null&&dat!==undefined?dat:0,mean=sl?sl.mean*100:0,cl='neutral',sv=1;
        if(sl&&mean>=30){cl='constraint';sv=3;}else if(sl&&mean>=bimStd('land.slope','b3')){cl='constraint';sv=2;}else if(sl&&mean<bimStd('land.slope','b1')){cl='opportunity';}   /* __acad3dV167h */
        A.push({auto:'landform.terrain',cat:'landform',title:'Relief and slope',
          value:'Ground '+(rg[0]+off).toFixed(1)+' to '+(rg[1]+off).toFixed(1)+' m'+(dat!==null&&dat!==undefined?' above sea level':'')+' (relief '+(rg[1]-rg[0]).toFixed(1)+' m)'+
            (sl?'; mean slope '+mean.toFixed(1)+'%, steepest '+(sl.max*100).toFixed(0)+'%, '+Math.round(sl.steepShare*100)+'% of it steeper than '+bimDispNum(bimStd('land.slope','b3'),2)+'%':''),
          cls:cl,sev:sv,source:(ter.context?ter.context.credit:((ter.source&&ter.source.format)?ter.source.format+' survey':'Survey'))||'Terrain',date:ter.context?ter.context.fetched:today});
      }
    }
    if(cnt.water)A.push({auto:'water.bodies',cat:'water',title:'Water',value:bimSaN(cnt.water,'water feature')+rr+' (water bodies and streams)',source:osm,date:od});
    if(A3D_SIM.rain&&A3D_SIM.rain.ponds)A.push({auto:'water.rain',cat:'water',title:'Rain flow',value:bimSaN(A3D_SIM.rain.ponds.length,'pond')+' where rain collects on the terrain',cls:A3D_SIM.rain.ponds.length?'constraint':'neutral',sev:1,source:'RAINFLOW on the terrain',date:today});
    if(bimSunNum(st.lat)&&bimSunNum(st.lon)){
      var dj=bimSaDayLen(st.lat,st.lon,'06-21'),dd=bimSaDayLen(st.lat,st.lon,'12-21');
      if(dj&&dd)A.push({auto:'climate.sun',cat:'climate',title:'Day length',value:'21 June: '+dj+'; 21 December: '+dd,source:'Sun position (NOAA equations)',date:today});
    }
    if(cnt.trees||cnt.green)A.push({auto:'ecology.green',cat:'ecology',title:'Trees and green',value:bimSaN(cnt.trees||0,'tree')+', '+bimSaN(cnt.green||0,'green area')+rr,cls:cnt.trees?'opportunity':'neutral',source:osm,date:od});
    if(cnt.roads){
      var uw=[],uk;for(uk in uses)if(uses.hasOwnProperty(uk))uw.push(bimSaN(uses[uk],BIM_ROAD_USE_LABEL[uk]||uk));
      A.push({auto:'access.roads',cat:'access',title:'Streets',value:bimSaN(cnt.roads,'road')+rr+(uw.length?': '+uw.join(', '):'')+(nBr?'; '+bimSaN(nBr,'bridge'):'')+(nTu?'; '+bimSaN(nTu,'tunnel'):''),cls:'opportunity',source:osm,date:od});
    }
    if(cnt.rail)A.push({auto:'access.rail',cat:'access',title:'Railways',value:bimSaN(cnt.rail,'railway feature')+rr+' (tracks, trams, platforms): transit, and noise and vibration',cls:'opportunity',source:osm,date:od});
    if(cnt.airports)A.push({auto:'access.airport',cat:'access',title:'Airport',value:bimSaN(cnt.airports,'airport feature')+rr+': aircraft noise and height limits are likely',cls:'constraint',sev:2,source:osm,date:od});
    if(cnt.power)A.push({auto:'utilities.power',cat:'utilities',title:'Overhead power',value:bimSaN(cnt.power,'pylon or line','pylons and lines')+rr+': keep the clearances',cls:'constraint',sev:2,source:osm,date:od});
    var lw=[],lk;for(lk in lu)if(lu.hasOwnProperty(lk))lw.push(bimSaN(lu[lk],lk+' area'));
    if(lw.length)A.push({auto:'people.landuse',cat:'people',title:'Land use around',value:lw.join(', ')+rr,source:osm,date:od});
    return A.concat(bimClimAuto()).concat(bimZnAuto()).concat(bimAccAuto()).concat(bimLandAuto()).concat(bimMvAuto()).concat(bimLdAuto());   /* __acad3dV168: land */   /* __acad3dV159: climate and risk; __acad3dV160: zoning; __acad3dV161: access and people; __acad3dV165: land and water; __acad3dV166: movement */
  }
  /* Fill from the model: what it knows, as findings; refilled in place, what was said about them kept */
  function bimSaFill(quiet){   /* __acad3dV159: quiet when the climate fetch fills it */
    var s=bimSa(),A=bimSaAuto(),i,f,seen={},add=0,upd=0,del=0;
    pushUndo();
    for(i=0;i<A.length;i++){
      seen[A[i].auto]=1;
      f=null;s.findings.forEach(function(x){if(x.auto===A[i].auto)f=x;});
      if(f){
        if(f.value!==A[i].value||f.title!==A[i].title||f.source!==A[i].source)upd++;
        f.title=A[i].title;f.value=A[i].value;f.source=A[i].source;f.date=A[i].date;f.cat=A[i].cat;
        f.cls=bimSaPair(BIM_SA_CLS,A[i].cls)?A[i].cls:'neutral';f.sev=A[i].sev||1;   /* __acad3dV164: the data's class; one set by hand before gives way */
      }else{s.findings.push(bimSaNew(A[i].cat,A[i]));add++;}
    }
    s.findings=s.findings.filter(function(x){
      if(!x.auto||seen[x.auto])return true;
      if(x.note||x.photo||x.at||x.touched){x.auto='';return true;}   /* what was said about it stays, no longer refilled */
      del++;return false;
    });
    bimSaDone();
    if(!quiet)a3dToast('Site analysis: '+(A.length?bimSaN(add,'finding')+' added, '+upd+' updated'+(del?', '+del+' gone':'')+' from the model':'nothing known yet: place the site and get its context first'));
    return {added:add,updated:upd,removed:del,total:A.length};
  }

