  /* __acad3dV128: the command search */
  window.__a3dCommandSearch=function(q,limit){
    try{return bimCmdSearch(q,limit);}catch(eQ){console.warn('[BIM] The command search failed',eQ);return [];}
  };
  window.__a3dCommandRecent=function(k){
    try{return bimCmdRecent(k);}catch(eR){console.warn('[BIM] The recent commands could not be read',eR);return [];}
  };
  window.__a3dCommandRun=function(id){
    try{return bimCmdRun(id);}catch(eX){console.warn('[BIM] Command failed: '+id,eX);a3dToast('That command could not run');return false;}
  };
  window.__a3dCommandCatalog=function(){return bimCmdCatalog().map(function(it){return bimCmdPublic(it);});};
  window.__a3dRunAct=function(act){return bimRunAct(act)!==false;};
  window.__a3dCommandUsageClear=function(){try{localStorage.removeItem(BIM_CMD_USE_KEY);}catch(eC){}return true;};
  window.__a3dTypeAnywhere=function(ev){
    try{
      if(!A3D.on||!ev||ev.ctrlKey||ev.metaKey||ev.altKey||!/^[A-Za-z?]$/.test(ev.key||''))return false;
      if(bimKeyForControl(ev))return false;
      if(bimStartShowing()||bimSheetOnScreen()||A3D_SLIDESHOW.on||el.dlg)return false;
      if(A3D.sk||A3D.face||A3D.facePick||A3D.conPick||A3D.zoomWindow||A3D_TYPING.active||drag||bimTypingDrag())return false;
      if(document.getElementById('a3d-gizmenu'))return false;
      var rp=document.getElementById('a3d-rupop');if(rp&&rp.classList.contains('open'))return false;
      return true;
    }catch(eT){console.warn('[BIM] Type-anywhere check failed',eT);return false;}
  };
  /* __acad3dV129: the shortcuts panel and the dock's names */
  window.__a3dDockTip=function(spec){return bimDockTipData(spec);};
  window.__a3dDockTipShown=function(){var e=document.getElementById('a3d-tip');return e&&e.classList.contains('show')?e.textContent:null;};
  window.__a3dDockLabels=function(on){if(on!==undefined)bimSetDockLabels(!!on);return bimDockLabelsOn();};
  /* __acad3dV134: data layers */
  window.__a3dDataLayers=function(){return JSON.parse(JSON.stringify(bimDataList()));};
  window.__a3dDataFeatures=function(id){return JSON.parse(JSON.stringify(bimDataFeats(id)));};
  window.__a3dDataPresets=function(){return JSON.parse(JSON.stringify(BIM_DATA_PRESETS));};
  window.__a3dDataKind=function(u){return bimDataKind(u);};
  window.__a3dDataQueryUrl=function(id){var L=bimDataById(id),a=bimCtxArea();return L&&a?bimDataQueryUrl(L,a):null;};
  window.__a3dDataAdd=function(u,n,c,cr){var id=bimDataAdd(u,n,c,cr);return Promise.resolve(id?A3D_DATA.pending[id]:null).then(function(r){return {id:id,result:r||null};});};
  window.__a3dDataFetch=function(id){return Promise.resolve(bimDataFetch(id));};
  window.__a3dDataBusy=function(id){return !!A3D_DATA.busy[id];};
  window.__a3dDataRemove=function(id){return bimDataRemove(id);};
  window.__a3dDataSet=function(id,f,v){return bimDataSet(id,f,v);};
  window.__a3dDataPick=function(sx,sy){return bimDataPick(sx,sy);};
  window.__a3dDataSel=function(){return A3D_DATA.sel?JSON.parse(JSON.stringify(A3D_DATA.sel)):null;};
  window.__a3dDataSelect=function(layer,fi){A3D_DATA.sel=layer?{layer:layer,fi:fi}:null;refreshProps();paint();return true;};
  window.__a3dDataToProperty=function(){var p=bimDataToProperty();return p?p.id:null;};
  window.__a3dDataDrawn=function(){return A3D.lastDataDrawn||0;};
  window.__a3dDataCredit=function(){return bimDataCreditHtml();};
  /* __acad3dV138: verify the survey */
  window.__a3dSurveyImport=function(text,fmt,units,base,code){
    var res=bimParseSurvey(text,fmt||'PNEZD');if(res.error)return {error:res.error};
    if(res.points.length<3)return {error:'too few points: '+res.points.length};
    var b=base||{};b={n:b.n==null?res.points[0].n:b.n,e:b.e==null?res.points[0].e:b.e,z:b.z==null?0:b.z};
    var o=bimImportSurvey(res,fmt||'PNEZD',units||'m',b,code);return o?{id:o.id,points:o.survey.length,checks:(o.checks||[]).length,bad:res.bad}:{error:'no surface'};};
  window.__a3dSurveyCheck=function(id){var o=objById(id);return o?JSON.parse(JSON.stringify(bimSurveyCheck(o))):null;};   /* the cache as the panel sees it */
  window.__a3dSurveyControl=function(id,txt){var o=objById(id);return o?bimSurveySetControl(o,txt):false;};
  window.__a3dSurveyReportHtml=function(id){var o=objById(id);return o?bimSurveyReportHtml(o):'';};
  window.__a3dSurveyTol=function(){return JSON.parse(JSON.stringify(BIM_SURVEY_TOL));};
  window.__acad3dV138='surveyread,surveyduplicates,surveyfidelity,surveytriangles,surveybusts,surveychecks,surveycontrol,surveypublic,'+
    'surveyverdict,surveypanel,surveyreport,surveyfile,surveycheckcode,surveycommand';
  /* __acad3dV137: the map on 3D terrain */
  window.__a3dTerrain3d=function(){return A3D.lastTerrain3d?JSON.parse(JSON.stringify(A3D.lastTerrain3d)):null;};
  window.__a3dCtxStand=function(on){return bimCtxStand(!!on);};
  window.__a3dDrapeTiles=function(ext,z,maxz){return bimDrapeTiles(ext,z,maxz||19);};
  window.__a3dTerrainPolys=function(){return (A3D.lastPolys||[]).filter(function(p){return p.terrain;}).length;};
  window.__acad3dV137='terrain3d,terrainshaded,terraindrape,drapetiles,drapeparent,drapediscard,terrain2d,ctxonground,ctxgroundsetting,ctxgroundundo,ctxgroundfetch';
  /* __acad3dV136: the lens */
  window.__a3dLens=function(by,prop){if(by!==undefined)bimLensSet(by,prop);return bimLensSettings();};
  window.__a3dLensCol=function(id){var o=objById(id);A3D_LENS.cur=null;return o?bimLensCol(o):null;};
  window.__a3dLensValue=function(id){var o=objById(id);return o?bimLensValue(o,bimLensSettings()):null;};
  window.__a3dLensLegend=function(){return A3D.lastLensLegend?JSON.parse(JSON.stringify(A3D.lastLensLegend)):null;};
  window.__a3dLensPropKeys=function(){return bimLensPropKeys();};
  window.__a3dLensRamp=function(){return BIM_LENS_RAMP.slice();};
  window.__a3dLensNone=function(){return BIM_LENS_NONE;};
  window.__a3dDataAttrKeys=function(id){return bimDataAttrKeys(id);};
  window.__a3dDataFeatCol=function(id,fi){var L=bimDataById(id);return L?bimDataFeatCol(L,bimDataLensScale(L),fi):null;};
  window.__a3dLensCommand=function(){return bimLensCommand();};
  window.__a3dTestLegendOnPaper=function(){var s=A3D.sheetCapture;A3D.sheetCapture=true;try{drawLensLegend(el.ctx,null,0,0);}finally{A3D.sheetCapture=s;}return A3D.lastLensLegend;};
  window.__a3dTestLevelName=function(id,n){var i;for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id){A3D.levels[i].name=n;A3D_LENS.cur=null;return true;}return false;};
  window.__a3dTestObjSet=function(id,k,v){var o=objById(id);if(!o)return false;if(v===null)delete o[k];else o[k]=v;A3D_LENS.cur=null;return true;};
  window.__acad3dV136='lensby,lensusage,lenslevel,lenstype,lenslayer,lensmaterial,lensheight,lensprop,lensramp,lensnovalue,lensgl,lens2d,'+
    'lensoverpresentation,lensundo,lenssaved,lenslegend,datalens,dataopacity,lenspanel,lenscommand';
  /* __acad3dV135: find open data */
  window.__a3dFindPortals=function(){return JSON.parse(JSON.stringify(BIM_DATA_PORTALS));};
  window.__a3dFindPortal=function(h){if(h!==undefined)bimFindSetPortal(h);var P=bimFindCurrent();return P?JSON.parse(JSON.stringify(P)):null;};
  window.__a3dFindGuess=function(){return bimFindGuess();};
  window.__a3dFindReset=function(){A3D_FIND.portal='';A3D_FIND.res=[];A3D_FIND.next=0;A3D_FIND.err='';A3D_FIND.said='';A3D_FIND.pick=null;A3D_FIND.groups={};A3D_FIND.busy=false;A3D_FIND.q='';A3D_FIND.near=true;return true;};
  window.__a3dFindHubUrl=function(q,o){return bimHubSearchUrl(q,o||{});};
  window.__a3dFindSocrataUrl=function(d,q,off){return bimSocrataSearchUrl(d,q,off||0);};
  window.__a3dFindSearch=function(q,more){return Promise.resolve(bimFindSearch(q,more));};
  window.__a3dFindState=function(){return JSON.parse(JSON.stringify({portal:A3D_FIND.portal,q:A3D_FIND.q,near:A3D_FIND.near,busy:A3D_FIND.busy,res:A3D_FIND.res,
    next:A3D_FIND.next,total:A3D_FIND.total,err:A3D_FIND.err,said:A3D_FIND.said,pick:A3D_FIND.pick,groups:A3D_FIND.groups}));};
  window.__a3dFindNear=function(v){A3D_FIND.near=!!v;return A3D_FIND.near;};
  window.__a3dFindAdd=function(ix,ly){return Promise.resolve(bimFindAdd(ix,ly)).then(function(r){
    var L=bimDataList(),id=typeof r==='string'?r:null;return Promise.resolve(id?A3D_DATA.pending[id]:null).then(function(f){return {id:id,result:r&&typeof r==='object'?r:null,fetch:f||null,layers:L.length};});});};
  window.__a3dFindCommand=function(){return bimFindCommand();};
  window.__a3dSetSiteAddress=function(a){if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};A3D.site.address=String(a||'');return true;};
  window.__acad3dV135='portallist,portalguess,portalremembered,hubsearch,hubgroups,hubbbox,socratasearch,socrataspatial,socratabox,'+
    'addfeaturelayer,addservicelayers,addgeojsonitem,addsocrata,more,failuresnamed,findcredit,findpanel,findcommand';
  window.__acad3dV134d='overpassmirrors,overpassget';
  window.__a3dOverpassMirrors=function(){return BIM_OVERPASS_MIRRORS.slice();};
  window.__acad3dV134='datakinds,arcgisquery,wfsgetfeature,geojsonfile,presets,areafilter,maxfeatures,featuresoutsideundo,'+
    'featuressaved,planoverlay,notonpaper,clicktoread,pickorder,parceltoproperty,failuresnamed,datacredit,datapanel,datacommand';
  /* __acad3dV133: site context */
  window.__a3dCtxSettings=function(){return bimCtxSettings();};
  window.__a3dCtxSet=function(f,v){return bimCtxSet(f,v);};
  window.__a3dCtxArea=function(){return bimCtxArea();};
  window.__a3dCtxQuery=function(){var a=bimCtxArea();return a?bimCtxQuery(a,bimCtxSettings().kinds):null;};
  window.__a3dCtxFetch=function(){return bimCtxFetch();};
  window.__a3dCtxBusy=function(){return !!A3D_CTX.busy;};
  window.__a3dCtxRemove=function(){return bimCtxRemove();};
  window.__a3dCtxOf=function(id){var o=objById(id);return o&&o.context?JSON.parse(JSON.stringify(o.context)):null;};
  window.__a3dCtxHeight=function(tags){return bimOsmHeight(tags);};
  /* __acad3dV139: LOD, solids, UTM, CityJSON */
  window.__a3dCtxPartRange=function(tags){return bimOsmPartRange(tags);};
  window.__a3dLodOf=function(id){var o=objById(id);return o?bimLodOf(o):null;};
  window.__a3dSolidCheck=function(id){var o=objById(id);return o?bimObjSolidCheck(o):null;};
  window.__a3dSolidCheckMesh=function(m,surface){return bimSolidCheck(m,{surface:!!surface});};
  window.__a3dLodCheck=function(){return bimLodCheck();};
  window.__a3dUtm=function(lon,lat,zone,south){return bimUtmFwd(lon,lat,zone||bimUtmZone(lon),!!south);};
  window.__a3dUtmInv=function(E,N,zone,south){return bimUtmInv(E,N,zone,!!south);};
  window.__a3dCityJson=function(){return bimCityJsonDoc();};
  window.__a3dCityJsonExport=function(){var d=bimCityJsonExport();return d&&d.error?d:{ok:true};};
  window.__a3dCityJsonImport=function(text,name){return bimCityJsonImportText(text,name);};
  window.__a3dImportFileText=function(text,name){bimHandleImportFile(new File([text],name));return true;};
  /* __acad3dV143: simulation */
  window.__a3dSunHours=function(o){var r=bimSunHoursCommand(o||{});if(r.error)return r;
    return {date:r.date,step:r.step,x0:r.x0,z0:r.z0,cell:r.cell,nx:r.nx,nz:r.nz,day:r.day,min:r.min,max:r.max,sixPlus:r.sixPlus,ground:r.ground,steps:r.steps,
      hours:Array.prototype.slice.call(r.hours),roof:Array.prototype.slice.call(r.roof)};};
  window.__a3dSolar=function(o){return bimSolarCommand(o||{}).then(function(r){return r.error?r:JSON.parse(JSON.stringify({count:r.count,steps:r.steps,roofMean:r.roofMean,best:r.best,shaded:r.shaded,objects:r.objects}));});};
  window.__a3dSolarYear=function(){return (bimSolarYear()||[]).map(function(s){return {el:s.sun.elevation,az:s.sun.azimuth,v:s.v,dni:s.dni,w:s.w};});};
  window.__a3dRainFlow=function(id,o){var r=bimRainCommand(id,o||{});if(r.error)return r;
    return {terrain:r.terrain,x0:r.x0,z0:r.z0,cell:r.cell,nx:r.nx,nz:r.nz,cells:r.cells,ponds:r.ponds,pondVolume:r.pondVolume,threshold:r.threshold,outlets:r.outlets,
      maxAcc:r.maxAcc,segs:r.segs.length,acc:Array.prototype.slice.call(r.acc),dir:Array.prototype.slice.call(r.dir)};};
  window.__a3dSimClear=function(w){return bimSimClear(w);};
  window.__a3dSimState=function(){return {sun:!!A3D_SIM.sun,solar:!!A3D_SIM.solar,rain:!!A3D_SIM.rain,busy:A3D_SIM.busy,
    stale:{sun:bimSimStale(A3D_SIM.sun),solar:bimSimStale(A3D_SIM.solar),rain:bimSimStale(A3D_SIM.rain)}};};
  /* __acad3dV142: the guide and the version */
  window.__a3dVersion=function(){return JSON.parse(JSON.stringify(BIM_APP_VERSION));};
  window.__a3dDocsOpen=function(page,id){return bimDocsOpen(page,id?bimDocsAnchor(id):'');};
  window.__a3dDocsOpened=function(){return A3D_GUIDE.opened.slice();};
  window.__a3dDocsAnchor=function(id){return bimDocsAnchor(id);};
  /* __acad3dV148: Analyze as a list; results as layers */
  window.__a3dAnzSearch=function(q){
    A3D_ANZ.q=String(q==null?'':q);
    var w=document.querySelector('.a3d-analyze-wrap'),s=w?w.querySelector('[data-anzsearch]'):null;
    if(s)s.value=A3D_ANZ.q;
    if(w)bimAnzFilter(w);
    return w?[].filter.call(w.querySelectorAll('[data-anzcard]'),function(e){return !e.closest('[hidden]');}).map(function(e){return e.getAttribute('data-anzcard');}):null;   /* __acad3dV162: in a category the search hid too */
  };
  window.__a3dAnzWordsHit=function(q,s){return bimAnzWordsHit(q,s);};
  window.__a3dResultLayers=function(){return bimResLayers().map(function(R){
    return {id:R.id,name:R.name,kind:R.kind,mode:R.mode||null,src:R.src||null,visible:R.visible!==false,opacity:bimResOpacity(R),stale:bimResStale(R),gone:bimResGone(R),
      created:R.created||null,run:R.run||null,cells:R.data?R.data.cells.length:0,date:R.data&&R.data.date||null,segs:R.data&&R.data.segs?R.data.segs.length:0};});};
  window.__a3dResultLayerData=function(id){var R=bimResById(id);return R&&R.data?JSON.parse(JSON.stringify(R.data)):null;};
  window.__a3dResultLayerAdd=function(k,o){var R=bimResultLayerAdd(k,o||{});return R?R.id:null;};
  window.__a3dResultLayerSet=function(id,f,v){return bimResultLayerSet(id,f,v);};
  window.__a3dResultLayerRemove=function(id){return bimResultLayerRemove(id);};
  window.__a3dResultLayerUpdate=function(id){return bimResultLayerUpdate(id);};
  window.__a3dResultLayerMove=function(id,to){return bimResultLayerMove(id,to);};
  window.__a3dResultDrawn=function(){return (A3D.lastResultDrawn||[]).slice();};
  window.__a3dResultLayersValid=function(a){return bimResValid(a).map(function(R){return R.id;});};
  window.__a3dSimHolds=function(){return {sun:bimResHolds(A3D_SIM.sun),rain:bimResHolds(A3D_SIM.rain)};};
  /* __acad3dV149: the shell on a phone and a tablet */
  window.__a3dShellTier=function(){return {tier:A3D_SHELL_TIER,computed:bimShellTier(),open:!document.getElementById('a3d-shell').classList.contains('collapsed'),
    more:document.body.classList.contains('a3d-railutil-open'),leftW:getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim()};};
  window.__a3dShellDrawer=function(open,tab){return bimShellDrawer(open,tab);};
  window.__a3dShellMore=function(on){return bimShellMore(on);};
  window.__a3dShellApplyTier=function(){return bimShellApplyTier();};
  window.__a3dKbFit=function(kb){return bimKbFit(kb);};   /* __acad3dV149b */
  window.__a3dMapDraft=function(){return A3D_MAP_DRAFT;};
  /* __acad3dV150: the tool palette */
  window.__a3dToolPal=function(){var p=document.getElementById('a3d-tpal');if(!p)return null;var r=p.getBoundingClientRect(),cs=getComputedStyle(p);
    return {shown:cs.display!=='none',orient:p.getAttribute('data-orient'),min:p.classList.contains('min'),x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),
      active:bimTPalActive(),nav:A3D.navMode,tools:[].map.call(p.querySelectorAll('[data-tpact]'),function(b){return b.getAttribute('data-tpact');}),prefs:bimTPalPrefs()};};
  window.__a3dToolPalAct=function(id){return bimTPalAct(id);};
  window.__a3dToolPalDrop=function(x,y){return bimTPalDrop(x,y);};
  window.__a3dToolPalFold=function(m){return bimTPalFold(m);};
  /* __acad3dV151: branches and merge */
  window.__a3dBranches=function(){return JSON.parse(JSON.stringify(bimHistBranches()));};
  window.__a3dBranchNew=function(n){return bimHistBranchNew(n);};
  window.__a3dBranchSwitch=function(n){return bimHistSwitch(n);};
  window.__a3dBranchDelete=function(n){return bimHistBranchDelete(n);};
  window.__a3dMergeStart=function(n){var r=bimHistMergeStart(n);return JSON.parse(JSON.stringify(r));};
  window.__a3dMergeState=function(){return A3D_MERGE?JSON.parse(JSON.stringify({from:A3D_MERGE.from,into:A3D_MERGE.into,base:A3D_MERGE.base,
    conflicts:A3D_MERGE.conflicts.map(function(c){return {key:c.key,kind:c.kind,label:c.label,gone:c.gone||null,choice:c.choice||null,fields:c.fields.map(function(f){return {f:f.f,base:f.base===undefined?null:f.base,ours:f.ours===undefined?null:f.ours,theirs:f.theirs===undefined?null:f.theirs};})};})})):null;};
  window.__a3dMergeChoose=function(i,s){return bimHistMergeChoose(i,s);};
  window.__a3dMergeFinish=function(){return JSON.parse(JSON.stringify(bimHistMergeFinish()));};
  window.__a3dMergeAbort=function(){return bimHistMergeAbort();};
  window.__a3dBranchCompare=function(){return JSON.parse(JSON.stringify(bimHistCompare()));};
  window.__a3dHistBase=function(a,b){return bimHistBase(a,b);};
  /* __acad3dV163: the SketchUp import, for the tests. A file is passed as base64. */
  function bimB64Buf(s){
    var bin=atob(String(s||'')),u=new Uint8Array(bin.length),i;
    for(i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
    return u.buffer;
  }
  window.__a3dSkpImport=function(b64,name,opt){try{return bimSkpImportBuffer(bimB64Buf(b64),name,opt);}catch(e){console.warn('[BIM] __a3dSkpImport',e);return {error:String(e&&e.message||e)};}};
  window.__a3dSkpScan=function(b64,name){var S=bimSkpScan(bimB64Buf(b64),name||'x.skp');return S.error?S:{parts:S.parts.length,blocks:S.blocks.map(function(b){return b.name;}),tris:S.tris,format:S.format,zip:S.zip,tags:S.tags};};
  window.__a3dSkpGenerated=function(n,defs){var G={};(defs||[]).forEach(function(d){G[d]=1;});return bimSkpGenerated(n,G);};
  window.__a3dSkpReader=function(){var R=bimSkpReader();return R?['SkpParseError','buildInstancedScene','buildScene','parseSkp'].filter(function(k){return typeof R[k]==='function';}):null;};
  /* every object a SketchUp file brought in: its record, and its area and world bounds from its mesh */
  window.__a3dSkpObjects=function(){
    return A3D.objs.filter(function(o){return !!o.skp;}).map(function(o){
      var m=o.mesh,q=bimObjOffset(o),A=0,V=0,mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity],i,k;
      for(i=0;i<m.v.length;i++)for(k=0;k<3;k++){mn[k]=Math.min(mn[k],m.v[i][k]+q[k]);mx[k]=Math.max(mx[k],m.v[i][k]+q[k]);}
      for(i=0;i<m.f.length;i++){
        var a=m.v[m.f[i][0]],b=m.v[m.f[i][1]],c=m.v[m.f[i][2]],u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],w=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];
        A+=Math.sqrt(Math.pow(u[1]*w[2]-u[2]*w[1],2)+Math.pow(u[2]*w[0]-u[0]*w[2],2)+Math.pow(u[0]*w[1]-u[1]*w[0],2))/2;
        V+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6;   /* signed: positive when the faces point out */
      }
      var ly=bimLayerById(o.layer);
      return {id:o.id,name:o.name,t:o.t,col:o.col,locked:!!o.locked,layer:o.layer,layerName:ly?ly.name:null,skp:JSON.parse(JSON.stringify(o.skp)),
        area:A,vol:V,min:mn,max:mx,tris:m.f.length,verts:m.v.length,faceSizes:m.f.reduce(function(s,f){s[f.length]=(s[f.length]||0)+1;return s;},{})};
    });
  };
  window.__a3dSkpLimits=function(v){if(v&&typeof v==='object'){var k;for(k in v)if(v.hasOwnProperty(k)&&BIM_SKP.hasOwnProperty(k))BIM_SKP[k]=+v[k];}return {maxTris:BIM_SKP.maxTris,blockTris:BIM_SKP.blockTris,blockChars:BIM_SKP.blockChars};};
  window.__acad3dV163='skpreader,skpclassic,skpzip,skpfaces,skpbacks,skpweld,skpmirror,skptags,skphidden,skpmaterials,skptextures,skpseethrough,skpblocks,skplibrary,skpprops,skpcommand,skpimport';
  window.__acad3dV162='oneanalyze,categories,modelgroup,onesearch,heldrefresh,boardpages,boardorder,boardthumbs,boardinview,boardwidth,boardpresent,boardprint,printset';
  window.__acad3dV161='accessfetch,walknetwork,walktimes,frontageseeds,dailyneeds,parkedges,transitstops,routes,frontage,connectivity,directness,census,acs,moe,pyramid,accessfindings,walklayer';
  window.__a3dAccQuery=function(lat,lon,rn,rp){return bimAccQuery(lat,lon,rn,rp);};
  window.__a3dAccFetch=function(){return bimAccFetch();};
  window.__a3dAccBusy=function(){return !!A3D_ACC.busy;};
  window.__a3dAcc=function(){return JSON.parse(JSON.stringify({access:(A3D.site&&A3D.site.access)||null,people:(A3D.site&&A3D.site.people)||null}));};
  window.__a3dAccWork=function(js){var org=bimMapOrigin();if(!org)return {error:'no site place'};return JSON.parse(JSON.stringify(bimAccWork(js,org,bimAccLot())));};
  window.__a3dAccLot=function(){return bimAccLot();};
  window.__a3dAccAuto=function(){return bimAccAuto();};
  window.__a3dCenUrls=function(lat,lon,y,G){return bimCenUrls(lat,lon,y||bimCenYear(),G);};
  window.__a3dCenYear=function(){return bimCenYear();};
  window.__a3dCenShare=function(X,Y){return bimCenShare(X,Y);};
  window.__a3dCenSum=function(L){return bimCenSum(L);};
  window.__acad3dV160='zoningrecord,fromlayers,farheightfromlayers,envelope,rolesbyside,cornerlot,steps,angularplanes,skyplane,stepback,heightlimit,exactplates,exactvolume,wholefaces,yield,compliance,zoningboard,zoningtable,sections,rulesbyside,plandiagram';
  window.__acad3dV159='climatefetch,normals,koppen,degreedays,hourly,windrose,psychrometric,comfort,airquality,earthquakes,climatefindings,board,figures,kpis,tables,print';
  window.__a3dClimUrls=function(lat,lon){return bimClimUrls(lat,lon);};
  window.__a3dClimFetch=function(){return bimClimFetch();};
  window.__a3dClimBusy=function(){return !!A3D_CLIM.busy;};
  window.__a3dClim=function(){return JSON.parse(JSON.stringify({climate:(A3D.site&&A3D.site.climate)||null,risk:(A3D.site&&A3D.site.risk)||null}));};
  window.__a3dKoppen=function(T,P,lat){return bimKoppen(T,P,lat);};
  window.__a3dHumRatio=function(T,RH){return bimHumRatio(T,RH);};
  window.__a3dClimAuto=function(){return bimClimAuto();};
  window.__a3dClbOpen=function(k){return bimClbOpen(k);};   /* __acad3dV160: 'climate' or 'zoning'; none keeps the last */
  window.__a3dClbClose=function(){return bimClbClose();};
  window.__a3dClbHtml=function(){return bimClbHtml();};
  window.__a3dZn=function(){return JSON.parse(JSON.stringify(bimZn()));};   /* __acad3dV160 */
  window.__a3dZnSet=function(k,v){return bimZnSet(k,v);};
  window.__a3dZnStepAdd=function(r){return bimZnStepAdd(r);};
  window.__a3dZnStepDel=function(r,i){return bimZnStepDel(r,i);};
  window.__a3dZnCalc=function(){var C=bimZnCalc();if(!C.ok)return {error:C.error};
    return {lot:C.lot,fpArea:C.fpArea,fp:C.fp,volume:C.volume,top:C.top,hTop:C.hTop,plates:C.plates,capacity:C.capacity,farGFA:C.farGFA,achievable:C.achievable,governs:C.governs,
      storeysUsed:C.storeysUsed,nsa:C.nsa,units:C.units,parking:C.parking,maxH:C.maxH,lotD:C.lotD,convex:C.convex,split:C.split,roles:C.legs.legs.map(function(l){return l.role;}),
      pieces:C.pieces,breaks:C.Z,proposed:C.proposed};};
  window.__a3dZnPlate=function(h,side){var C=bimZnCalc();if(!C.ok)return null;var q=bimZnPlate(C,+h,side===undefined?-1:side);
    return q?{area:Math.abs(bimZnArea2(q)),pts:q.map(function(c){return c.p;}),tags:q.map(function(c){return c.t;})}:{split:true};};
  window.__a3dZnInset=function(role,h,side){var z=bimZn(),R=bimZnRules(z);return R[role]?bimZnInset(R[role],+h,side===undefined?-1:side):null;};
  window.__a3dZnAllows=function(x,zc,y){var C=bimZnCalc();return C.ok?bimZnAllows(C,[x,zc],y):null;};
  window.__a3dZnBuild=function(){var C=bimZnBuild();return C&&C.ok?true:(C&&C.error)||false;};
  window.__a3dZnFromLayer=function(apply){var r=bimZnFromLayer(!!apply);return r?JSON.parse(JSON.stringify(r)):null;};
  window.__a3dZnEnvelope=function(){var o=bimZnEnvelopeObj();return o?{id:o.id,name:o.name,layer:o.layer,locked:o.locked,envelope:o.envelope,nv:o.mesh.v.length,nf:o.mesh.f.length,
    v:o.mesh.v,f:o.mesh.f}:null;};
  window.__a3dZnEdit=function(on){A3D_ZN.edit=!!on;bimSaRefresh(true);return true;};
  window.__a3dAnzView=function(v){if(v)return bimAnzView();return 'analyze';};   /* __acad3dV162: one view; opening it to either opens it */
  window.__a3dSaGoto=function(id){return bimSaGoto(id);};
  window.__a3dAnalyzeRefresh=function(f){return bimAnalyzeRefresh(!!f);};
  window.__a3dAnzPending=function(){return A3D_ANZ.pend;};
  window.__a3dAnzCats=function(){return bimAnzCards().map(function(c){return {id:c.id,group:c.group};});};
  window.__acad3dV158='layergroups,stages,categories,findings,sources,confidence,classes,checklists,fillfrommodel,pins,photos,sitetab';
  window.__a3dSa=function(){return JSON.parse(JSON.stringify(bimSa()));};
  window.__a3dSaStandard=function(){return {cats:BIM_SA_CATS.map(function(c){return {id:c.id,n:c.n};})};};   /* __acad3dV164: no stages, no checklists */
  window.__a3dSaAuto=function(){return bimSaAuto();};
  window.__a3dSaSlope=function(tin){return bimSaSlope(tin);};
  window.__a3dLySecVisible=function(key,v){return bimLySecVisible(key,v);};
  window.__a3dLySecHidden=function(key){return bimLySecHidden(key);};
  window.__a3dSaFill=function(){return bimSaFill();};
  window.__a3dSaNumber=function(id){var f=bimSaFind(id);return f&&f.auto?bimSaNumber(f):null;};
  /* __acad3dV164: Analyze site and the analyses in the model */
  window.__a3dSiteRun=function(q){return bimSiteAnalyze(q);};
  window.__a3dSiteRunState=function(){return JSON.parse(JSON.stringify({busy:A3D_SITERUN.busy,steps:A3D_SITERUN.steps}));};
  window.__a3dDgRun=function(a){return bimDgRunAll(a||null);};
  window.__a3dDgState=function(){return JSON.parse(JSON.stringify(bimDgState()));};
  window.__a3dDgSite=function(){return JSON.parse(JSON.stringify(bimDgSite()));};
  window.__a3dDgList=function(a){return bimDgDiags(a||null).map(function(o){return {id:o.id,name:o.name,a:o.dg.a,k:o.dg.k,kind:o.dg.g.kind,layer:o.layer,edited:bimDgEdited(o),newer:!!o.dg.newer,orphan:!!o.dg.orphan,mine:!o.dg.gen};});};
  window.__a3dDgSet=function(id,f,v){return bimDgSet(objById(id),f,v);};
  window.__a3dDgReset=function(id){return bimDgReset(id);};
  window.__a3dDgResetAnalysis=function(a){return bimDgResetAnalysis(a);};
  window.__a3dDgAct=function(v){return bimDgAct(v);};
  window.__a3dDgPick=function(x,y){var o=bimPickDiag(x,y);return o?o.id:null;};
  window.__a3dDgHits=function(){return A3D_DG.hits.map(function(h){return {id:h.id,segs:h.segs.length,dots:h.dots.length,boxes:h.boxes.map(function(b){return b.slice();})};});};
  window.__a3dDgLegend=function(){return A3D_DG.legend?JSON.parse(JSON.stringify(A3D_DG.legend)):null;};
  window.__a3dDgCrtn=function(Q18,V,p,dcl,half){var L0=bimDgL0(Q18,V,p);return {L0:L0,at:bimDgLat(L0,dcl,half||0),reach:BIM_DG_NOISE_BANDS.map(function(b){return bimDgReach(L0,b[0],half||0);})};};
  window.__a3dDgRoadClass=function(hw){return bimDgRoadClass(hw);};
  window.__a3dDgBarrier=function(a,H,x){return bimDgBarrier(a,H,x);};
  window.__a3dUndoDepth=function(){return UNDO_STACK.length;};
  window.__a3dDgToScreen=function(p){var q=toScreen(p,camVecs(A3D.cam),cvW(),cvH());return [q[0],q[1],q[2]];};
  /* __acad3dV165: land and water, for the tests */
  window.__a3dLandFetch=function(){return bimLandFetch();};
  window.__a3dLandDem=function(){var D=bimLandGround(bimDgSite()),H=[],k;if(!D)return null;for(k=0;k<D.H.length;k++)H.push(D.ok[k]?D.H[k]:null);
    return {x0:D.x0,z0:D.z0,cell:D.cell,nx:D.nx,nz:D.nz,H:H,from:D.from,datum:D.datum,src:D.src};};
  window.__a3dLandHorn=function(){var D=bimLandGround(bimDgSite()),h,s=[],a=[],k;if(!D)return null;h=bimLandHornOf(D);
    for(k=0;k<D.H.length;k++){s.push(isFinite(h.slope[k])?h.slope[k]:null);a.push(isFinite(h.aspect[k])?h.aspect[k]:null);}return {slope:s,aspect:a};};
  window.__a3dLandHydro=function(){var S=bimDgSite(),D=bimLandGround(S),Y,M;if(!D)return null;Y=bimLandHydroOf(D);M=bimLandSiteMask(D,S);
    function A(v){return Array.prototype.slice.call(v);}
    return {F:A(Y.F),down:A(Y.down),acc:A(Y.acc),order:A(Y.order),lab:A(Y.lab),stream:A(Y.stream),site:A(M),upstream:A(bimLandUpstream(D,Y,M)),exits:bimLandExits(D,Y,M),
      ponds:Y.ponds.map(function(p){return {cells:p.cells.slice(),volume:p.volume,depth:p.depth,deep:p.deep,level:p.level,area:p.area};}),pondsAll:Y.pondsAll,
      links:bimLandLinks(D,Y).map(function(l){return {from:l.from,to:l.to,order:l.order,outlet:l.outlet,n:l.nodes.length};})};};
  window.__a3dLandMs=function(V,nx,nz,lev,pad){return bimLandMs(V,nx,nz,lev,pad);};
  window.__a3dLandGet=function(){var L=A3D.site&&A3D.site.land;return L?JSON.parse(JSON.stringify(L)):null;};
  window.__a3dLandSet=function(v){A3D.site=A3D.site||{};if(v===null)delete A3D.site.land;else A3D.site.land=JSON.parse(JSON.stringify(v));A3D_LAND.key=null;A3D_LAND.D=null;return true;};
  window.__a3dLandZoneOf=function(p){return bimLandZoneOf(p||{});};
  window.__a3dLandBfe=function(p){return bimLandBfe(p||{});};
  window.__a3dLandUS=function(lat,lon){return bimLandUS({lat:lat,lon:lon});};
  window.__a3dLandWarm=function(d8,lat){return bimLandWarm(d8,lat);};
  window.__a3dDgLabelBoxes=function(){return (A3D_DG.labelBoxes||[]).map(function(b){return b.slice();});};
  /* __acad3dV166: movement, for the tests */
  window.__a3dMvGet=function(){var S=A3D.site&&A3D.site.access;return S&&S.mv?JSON.parse(JSON.stringify(S.mv)):null;};
  window.__a3dMvSet=function(v){var S=A3D.site&&A3D.site.access;if(!S)return false;if(v===null)delete S.mv;else S.mv=JSON.parse(JSON.stringify(v));return true;};
  window.__a3dMvLts=function(t){var r=bimMvLts(t||{});return {lts:r.lts,why:r.why,sp:r.sp,ln:r.ln,fac:r.fac,pk:r.pk};};
  window.__a3dMvKmh=function(s){return bimMvKmhOf(s);};
  window.__a3dMvRow=function(v){return bimMvRow(v);};
  window.__a3dMvInterval=function(v){return bimMvInterval(v);};
  window.__a3dMvParking=function(t){return bimMvParking(t||{});};
  window.__a3dMvStress=function(){var mv=bimMvOf();if(!mv)return null;var ST=bimMvStress(mv);
    return {W:ST.W.map(function(r){return r.lts;}),X:ST.X.map(function(c){return {n:c.n,x:c.x,z:c.z,lts:c.lts,ctl:c.ctl,minors:c.minors.slice(),main:c.main?String(c.main.t.name||c.main.t.highway):''};})};};
  window.__a3dMvReach=function(){var S=A3D.site&&A3D.site.access,mv=bimMvOf();if(!mv)return null;var ST=bimMvStress(mv),R=bimMvReach(mv,ST,bimMvLotOf(S));
    function f(D){return D.map(function(v){return isFinite(v)?Math.round(v*1000)/1000:null;});}
    return {Da:f(R.Da),Dl:f(R.Dl),ok:R.ok,seeds:R.seeds};};
  window.__a3dMvPtal=function(){var S=A3D.site&&A3D.site.access;if(!S)return null;return JSON.parse(JSON.stringify(bimMvPtal(S,bimMvOf())));};
  window.__a3dMvPtalBand=function(ai){return bimMvPtalBand(ai);};
  /* __acad3dV167: the standards registry */
  window.__a3dStd=function(t,n){return bimStd(t,n);};
  window.__a3dStdSay=function(t,n){return bimStdSay(t,n);};
  window.__a3dStdEdition=function(t){return bimStdEdition(t);};
  window.__a3dStdUsed=function(t){return bimStdUsedText(t);};
  window.__a3dStdStamp=function(ts){return bimStdStamp(ts);};
  window.__a3dStdChanged=function(st){return bimStdChanged(st);};
  window.__a3dStdRecords=function(){return JSON.parse(JSON.stringify(bimStdRecs().map(function(r){return {id:r.id,title:r.title,pub:r.pub,kind:r.kind,area:r.area,cat:!!r.cat,anywhere:!!r.anywhere,
    eds:r.eds.map(function(e){return {id:e.id,name:e.name,pub:e.pub,st:e.st,where:e.where,adopt:e.adopt,src:e.src,method:e.method||'',pack:e.pack||null,v:e.v};})};})));};
  window.__a3dStdPath=function(){return bimStdPath();};
  window.__a3dStdPlace=function(){var p=bimStdPlace();return p?JSON.parse(JSON.stringify(p)):null;};
  window.__a3dStdSetPlace=function(p,src){return bimStdSetPlace(p,src||'hand');};
  window.__a3dStdPlaceFromAddress=function(a){pushUndo();var ok=bimStdPlaceFromAddress(a);bimStdDone();return ok;};
  window.__a3dStdSetDate=function(d){return bimStdSetDate(d);};
  window.__a3dStdOverride=function(t,n,v,why){return bimStdOverride(t,n,v,why);};
  window.__a3dStdClear=function(t,n){return bimStdClear(t,n);};
  window.__a3dStdPick=function(t,id){return bimStdPick(t,id||null);};
  window.__a3dStdPackDiff=function(text){return bimStdPackDiff(text);};
  window.__a3dStdPackApply=function(text){return bimStdPackApply(text);};
  window.__a3dStdPackRemove=function(sha){return bimStdPackRemove(sha);};
  window.__a3dStdState=function(){var s=A3D.site&&A3D.site.std;return s?JSON.parse(JSON.stringify(s)):null;};
  window.__a3dSha256=function(t){return bimSha256(t);};
  window.__a3dStdCommand=function(){return bimStdCommand();};
  window.__a3dStdUi=function(){return JSON.parse(JSON.stringify({open:A3D_STD_UI.open,edit:A3D_STD_UI.edit,place:A3D_STD_UI.place,pending:A3D_STD_UI.pending?{file:A3D_STD_UI.pending.file,diff:A3D_STD_UI.pending.diff}:null}));};
  window.__a3dStdPackLook=function(text,file){return bimStdPackLook(text,file);};
  window.__a3dDgStdChanged=function(a){return bimDgStdChanged(a);};
  window.__a3dStdDataChanged=function(k,only){return bimStdDataChanged(k,only||null);};
  window.__a3dSaStdText=function(auto){return bimSaStdText({auto:auto});};
  window.__acad3dV167='registry,records,reader,place,placefromaddress,date,overrides,reasons,ordered,picks,stamps,outofdate,findingstd,accessstd,contextstd,packs,sha256,packdiff,catalogue,standardsgroup,standardscommand,valuesinwords,datastamps,usedvalues,valuestamps,framestd,refill,touchsizes,drafts,sheet,packadopted,packagain,whonoise,noliterals,dm2unread,classeswhole,groupclosed';
  window.__acad3dV168='lbcs,crosswalk,landuse,mix,entropy,figureground,spacematrix,cells,grain,courtyards,green,canopy,treesseen,greenwalk,33300,zoningaround,drawinginfo,textures,lids,findings,registry';
  window.__acad3dV169='assets,people,wheelchair,cycles,stands,bay,trees,leaf,gsl,shadows,turning,contexttrees,registry,vehicles,turningpaths,refit';
  window.__acad3dV170='clock,play,pause,stop,march,drawon,rings,reveal,sun,shadowday,motionstyle,reducedmotion,hidden,saveimage3d,command';
  /* __acad3dV170: the analyses in motion */
  window.__a3dAnim=function(){var F=A3D_ANIM.fr||bimAnimFrame();return JSON.parse(JSON.stringify({on:A3D_ANIM.on,paused:A3D_ANIM.paused,t:A3D_ANIM.t,playAt:A3D_ANIM.playAt,sunTime:A3D_ANIM.sunTime,can:A3D_ANIM.can,frames:A3D_ANIM.frames,live:bimAnimLive(),
    raf:!!A3D_ANIM.raf,north:bimTrueNorthDeg(),fr:{order:F.order,idx:F.idx,rings:F.rings,Rmax:F.Rmax,any:F.any,sun:F.sun,sunAt:F.sunAt||null,shadowDone:F.shadowDone}}));};
  window.__a3dAnimPlay=function(on){return bimAnimPlay(on);};
  window.__a3dAnimStop=function(){return bimAnimStop();};
  /* the clock set by hand, paused there: the frame at t seconds, the last Play at playAt */
  window.__a3dAnimAt=function(t,playAt){bimAnimHalt();A3D_ANIM.on=false;A3D_ANIM.paused=true;A3D_ANIM.t=+t||0;A3D_ANIM.playAt=+playAt||0;A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();A3D_ANIM.sunDate=bimAnimSunDate();paint();return window.__a3dAnim();};
  window.__a3dAnimOf=function(id){var o=objById(id);if(!bimIsDiag(o))return null;var R=bimAnimRingOf(o);
    return {motion:bimAnimMotion(o),kinds:bimAnimKinds(o),auto:bimAnimAuto(o),out:bimAnimOut(o),ring:R,k:bimAnimLive()&&bimAnimMotion(o)==='ring'?bimAnimRingK(o):null,draw:bimAnimLive()&&bimAnimMotion(o)==='draw'?bimAnimDrawOf(o):null,reveal:bimAnimReveal(o.dg.a)};};
  window.__a3dAnimSettings=function(){return JSON.parse(JSON.stringify({anim:BIM_ANIM,names:BIM_ANIM_NAMES,auto:BIM_ANIM_AUTO}));};
  window.__a3dAnimTint=function(h){return bimAnimTint(h);};
  /* a march's way: the points' order after the turn -- a line's, each pair's of segments, each polyline's */
  window.__a3dAnimWay=function(id){var o=objById(id),g,I;if(!bimIsDiag(o))return null;g=o.dg.g;A3D_ANIM.c=null;
    function idx(n){var P=[],i;for(i=0;i<n;i++)P.push([i,0,1]);return P;}
    if(g.kind==='lines')return (g.lines||[]).map(function(Wl){return bimAnimOrientLine(o,Wl,idx(Wl.length)).map(function(p){return p[0];});});
    I=bimAnimOrient(o,idx((g.pts||[]).length));return I.map(function(p){return p[0];});};
  window.__a3dAnimCentre=function(){A3D_ANIM.c=null;return bimAnimCentre();};
  /* the clock fed these frame times (ms), as requestAnimationFrame would: the frames drawn and the time gone on */
  window.__a3dAnimTicks=function(ts){var f0=A3D_ANIM.frames,t0=A3D_ANIM.t,i;bimAnimHalt();A3D_ANIM.on=true;A3D_ANIM.paused=false;A3D_ANIM.last=0;A3D_ANIM.painted=0;
    for(i=0;i<ts.length;i++){bimAnimTick(ts[i]);if(A3D_ANIM.raf){cancelAnimationFrame(A3D_ANIM.raf);A3D_ANIM.raf=0;}}
    A3D_ANIM.on=false;A3D_ANIM.paused=true;return {frames:A3D_ANIM.frames-f0,dt:A3D_ANIM.t-t0};};
  window.__a3dAnimSunTime=function(t){var k=A3D_ANIM.t;A3D_ANIM.t=+t||0;var r=bimAnimSunTime();A3D_ANIM.t=k;return r;};
  window.__a3dViewportImage=function(){var r=bimViewportCanvas();return {url:r.cv.toDataURL('image/png'),engine:r.engine,w:r.cv.width,h:r.cv.height};};
  window.__a3dEntKinds=function(){return BIM_ENT.map(function(e){return {k:e.k,name:e.name,cat:e.cat,kind:e.kind,p:JSON.parse(JSON.stringify(e.p))};});};
  window.__a3dEntPlace=function(key,x,z,p){var o=bimEntPlace(key,[x,z],p||null);return o?o.id:null;};
  /* an asset as placed: its parameters, its frame, and its size in its own frame (the markers left out) */
  window.__a3dEntInfo=function(id){
    var o=objById(id);
    if(!o||!o.asset||!o.mesh)return null;
    var F=bimEntFrame(o),q=bimObjOffset(o),v=o.mesh.v,ca=Math.cos(F.a),sa=Math.sin(F.a),mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],i,k;
    for(i=2;i<v.length;i++){
      var dx=v[i][0]-F.c[0],dz=v[i][2]-F.c[1],L=[dx*ca-dz*sa,v[i][1]-F.y,dx*sa+dz*ca];
      for(k=0;k<3;k++){if(L[k]<mn[k])mn[k]=L[k];if(L[k]>mx[k])mx[k]=L[k];}
    }
    return {k:o.asset.k,key:o.asset.key,p:JSON.parse(JSON.stringify(o.asset.p||{})),cf:o.asset.cf,heading:F.a,centre:[F.c[0]+q[0],F.c[1]+q[2]],base:q[1]+F.y,
      min:mn,max:mx,size:[mx[0]-mn[0],mx[1],mx[2]-mn[2]],faces:o.mesh.f.length,verts:v.length,name:o.name,col:o.col,layer:o.layer,
      body:o.asset.k==='person'?bimEntBody(o.asset.p||{}):null,tree:o.asset.k==='tree'?bimEntTreeSize(o.asset.p||{}):null,
      veh:o.asset.k==='vehicle'?bimEntVeh(o.asset.p||{}):null};
  };
  window.__a3dEntSet=function(id,key,val){var o=objById(id);return o&&o.asset?bimEntPropSet(o,key,val,val===true):false;};
  window.__a3dEntInLeaf=function(date){return bimEntInLeaf(date);};
  window.__a3dEntSeason=function(){var G=bimEntSeason();return G?JSON.parse(JSON.stringify(G)):null;};
  window.__a3dClimGsl=function(js,lat){var G=bimClimGsl(js,lat);return G?{s:G.s,e:G.e,years:G.years,sh:G.sh}:null;};
  window.__a3dEntTurns=function(){return {turns:bimEntTurns(),drawn:A3D.lastTurns||0};};
  window.__a3dEntRefit=function(){return {n:bimEntRefit(),last:A3D.lastRefit};};
  window.__a3dEntCrown=function(tags){return {ratio:bimEntCrownRatio(tags||{}),leaf:bimEntLeafOf(tags||{})};};
  /* the faces each solid casts a shadow with, on a date */
  window.__a3dShadowFaces=function(date){var L=bimShadowCasters(bimShadowGround(),date),o={};L.forEach(function(it){o[it.id]=it.f.length;});return o;};
  window.__a3dLand=function(){
    try{
      var S=bimDgSite(),Ar=bimLdAreas(),B=bimLdBuildings(),W=bimLdWin(S),Q=bimLd33300(S),Z=bimLdZnAround(S);
      return JSON.parse(JSON.stringify({S:{c:S.c,y:S.y,r:S.r},W:W,reach:bimLdReach(),
        areas:Ar.map(function(a){return {key:a.key,cls:a.cls,area:a.area,name:a.name,outer:a.outer.length,holes:a.holes.length};}),
        buildings:B.map(function(b){return {id:b.id,name:b.name,cls:b.cls,s:b.s,from:b.from,area:b.area,ground:b.ground,whole:b.whole,holes:b.holes.length,yards:b.yards};}),
        mix:bimLdMix(S,B,Ar),form:bimLdForm(B,W.x0,W.z0,W.x1,W.z1),grain:bimLdGrain(B,W),seen:Q.seen,canopy:Q.can,
        greens:Q.G.map(function(g){return {key:g.key,name:g.name,area:g.area,big:g.big,walk:Q.walks[g.key]||null};}),best:Q.best?{key:Q.best.g.key,d:Q.best.d,p:Q.best.p}:null,
        ok:[Q.ok3,Q.ok30,Q.ok300],walkData:Q.walkData,
        zn:Z?{attr:Z.Z.attr,layer:Z.Z.L.name,lot:Z.lot,by:Z.by,order:Z.order,tot:Z.tot,col:Z.col,drawing:Z.Z.L.drawing||null}:null}));
    }catch(e){console.warn('[BIM] __a3dLand',e);return {error:String(e&&e.message||e)};}
  };
  window.__a3dLandClass=function(t,b){return bimLdClassOf(t||{},!!b);};
  window.__a3dLandCell=function(pts){var S=bimDgSite(),G=bimLdRaster(S,bimLdBuildings(),bimLdAreas());return pts.map(function(p){var i=Math.floor((p[0]-G.W.x0)/G.rc),j=Math.floor((p[1]-G.W.z0)/G.rc);return (i<0||j<0||i>=G.nx||j>=G.nx)?null:G.R[j*G.nx+i];});};
  window.__a3dLandForm=function(x0,z0,x1,z1){return JSON.parse(JSON.stringify(bimLdForm(bimLdBuildings(),x0,z0,x1,z1)));};
  window.__a3dZnDrawing=function(js){return bimZnDrawing(js);};
  window.__a3dZnStyleOf=function(D,p){return bimZnStyleOf(D,p||{});};
  window.__a3dZnDrawingFetch=function(){return bimZnDrawingFetch();};
  window.__a3dDgTexCss=function(k,i){return bimDgTexCss(k,i);};
  window.__acad3dV166d='rightstep,rightsteplabel,rightstepscreen,rightstephidden,rightedgekeys,rightedgepointer,rightdocked,auditproperties';
  window.__acad3dV166b='noanalysistab,usagesonproject,anzframe,anzfloorloads,anzareas,anzfields,anzsearchsettings,leftresize,leftremembered,leftreset,leftkeys,leftclamp,leftdesktop,leftstep';
  window.__acad3dV166='mvquery,mvdata,mvstreets,mvthin,mvbudget,crossings,doors,carparks,garages,intervals,routeways,paths,walklayeronrequest,'+
    'hierarchy,lts2012,crossings2016,lowstressreach,ptal,catchments,routes,walkbands,needs,vehicleentry,provisionalentry,onstreetparking,maprgb,ptalfinding,cyclingfinding,vehiclesfinding';
  window.__acad3dV165='landgrid,landfetch,ownsurface,contextfallback,horn,marchingsquares,contours,hypsometric,slopeclasses,aspectwarmth,priorityflood,d8,strahler,catchments,divides,'+
    'upstream,exits,ponds,fema,floodzones,bfe,sitezone,bandrings,bandgroups,bandpick,lines,coverhidden,legendcompact,legendrecent,keepclear,labelspots,landstep,landfindings';
  window.__acad3dV164='diagobjects,live,editable,keptedits,deletedstay,newer,orphans,copies,reset,resetanalysis,layers,sublayers,legend,underover,bandsbatched,pick,transform,props,'+
    'frame,sunpaths,sunnow,shadows,winds,seasons,secmean,strongest,rose,isovist,views,noise,crtn,fhwa,dinbands,rails,timezone,'+
    'analyzesite,address,steps,onestep,radius,zoningstep,cards,command,removedstages,removeddefine,removedtyped,removedphotos,removedpins,removedchecklists';
  window.__acad3dV157='railkind,airportkind,powerkind,landusekind,roadsurface,roaduse,bridgedeck,piers,tunnels,trees3d,treerows,pylons,drapedsurfaces';
  window.__acad3dV156='seencount,typecolour,gpupick,pickidpass,picklockedcpu,picksmallcpu';
  window.__acad3dV155='spatialchunks,chunkboxes,culling,bundleperchunk,benchmark,benchstat';
  window.__acad3dV154='edgepull,gpumap,gputerrain,gpudrape,tilemipmaps,tilefreed,terraindata,sitefirst';
  window.__acad3dV153='webgpu,sharedscene,storagetable,renderbundle,glfallback,maptogl,terraintogl,devicelost,graphicscommand,graphicsstat';
  window.__acad3dV152='batches,objecttable,chunkrebuild,hiddenstays,transparentpass,edgebatch,fallback,stressmodel,bench';
  window.__acad3dV151='branches,branchnew,branchswitch,switchrefused,mainbranch,mergebase,merge3,fieldmerge,conflicts,deleteconflict,fastforward,uptodate,mergecommit,compare,branchcommands,branchsaved';
  window.__acad3dV150='toolpalette,essentialtools,activetool,selectputsaway,pantoggle,draggable,edgedock,flat,fold,remembered,dockgivesway,moretools';
  window.__acad3dV149='addrdraft,typing16,keyboardlift,focusscroll,tierphone,tieroverlay,tabbar,tablabels,railmore,leftdrawer,drawerclosed,drawerscrim,tabtoggles,escshuts,fullwidth,safeareas,viewportfit,burgerdrawer,toastclear,tierfollows';
  window.__acad3dV148='anzlist,anzgroups,anzsearch,anzwords,anzexpand,anzremember,addaslayer,reslayers,ressnapshot,reslive,resstale,resupdate,resorder,resopacity,ressaved,resundo,layersanalysis,layersdata,touchrows';
  window.__acad3dV147='phonesheet,tabletdrawer,touchtargets,paneltokens,sentencecase,rowgrid,inputstyle,buttonstyle,typeheader,showall,resizable,minimise,lightdark';
  window.__acad3dV146='canon,hash128,elementtree,blobstore,commit,diff,fielddiff,idrecords,restore,elementhistory,historygroup,historycommands,savedwithproject';
  window.__acad3dV145='daylight,fans,valleys,proposedsurface,regrade,tinvolume,cutfillbands,cutfillmap,spotelevations,slopearrows,gradingcard,gradecommands';
  window.__acad3dV144='breaklines,surveybreaklines,boundary,ownfaces,slopebands,elevationbands,aspectbands,terrainlegend,landxmlout,landxmlin,terraincard,terraincommands';
  window.__acad3dV143='sunhours,solarclearsky,solarshading,solarlens,rainfill,rainponds,rainflowlines,simcards,simcommands,simstale';
  window.__acad3dV142='appversion,versionrow,docscommand,releasenotescommand,f1help,docsanchors';
  /* __acad3dV141: tabs and the Analyze tab */
  window.__a3dPropTab=function(){return A3D_PTAB;};
  window.__a3dSetPropTab=function(t){return bimSetPropTab(t);};
  window.__a3dPropTabOf=function(n){return bimPropTabOf(n);};
  window.__a3dAnalyzeCards=function(){return JSON.parse(JSON.stringify(bimAnzCards()));};
  window.__a3dAnalyzeAct=function(a){return bimAnzAct(a);};
  window.__acad3dV141='proptabs,locationgroup,tabremembered,tabreveal,analyzerail,analyzecards,analyzeopen,analyzerun,analysescommand';
  /* __acad3dV140: LOD2 roofs */
  window.__a3dOsmRoof=function(fp,tags,base,h,from){var r=bimOsmRoof(sketchCCW(fp),tags,base||0,h,from||'height');return r?JSON.parse(JSON.stringify(r)):null;};
  window.__a3dRoofDir=function(s){return bimRoofDir(s);};
  window.__acad3dV140='roofshapes,roofgabled,roofhipped,roofpyramidal,roofskillion,roofhalfhipped,roofgambrel,roofmansard,roofflat,roofheights,roofdirection,lod20,roofrow,roofcityjson';
  window.__acad3dV139='buildingparts,lod13,lodlabels,lodgroup,solidcheck,lodcheck,utm,cityjsonout,cityjsonin,cityjsonfile,cityjsoncommands';
  window.__a3dCtxRings=function(members,role){return bimOsmRings(members,role);};
  window.__a3dCtxCredit=function(){return bimCtxCreditHtml(false);};
  window.__a3dCtxDatum=function(){return bimCtxDatum();};
  window.__a3dOsmKind=function(el){return bimOsmKind(el);};                 /* __acad3dV157 */
  window.__a3dRoadUse=function(tags){return bimRoadUse(tags||{});};
  window.__a3dTagMetres=function(v){return bimTagMetres(v);};
  window.__a3dCtxWidth=function(kind,tags){return bimCtxWidth(kind,tags||{});};
  window.__a3dCtxAlong=function(pts,step){return bimCtxAlong(pts,step);};
  window.__acad3dV133f='esristreet';
  window.__acad3dV133e='zoomrange,zoomaboutcursor,farplanefollows';
  window.__a3dZoomAbout=function(f,sx,sy){var d=bimZoomAbout(f,sx,sy);paint();return d;};
  window.__a3dZoomLimits=function(){return [BIM_ZOOM_MIN,BIM_ZOOM_MAX];};
  window.__acad3dV133d='cartostreet,retinatiles,dprzoom,mipmaps,nominatimrefusal';
  window.__a3dMapDpr=function(){return bimMapDpr();};
  window.__a3dMapMipmapped=function(){var k,n=0,m=0;for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)&&A3D_MAP.cache[k].tex){n++;if(A3D_MAP.cache[k].mip)m++;}return {textures:n,mipmapped:m};};
  window.__acad3dV133='contextarea,overpassquery,osmkinds,multipolygonrings,buildingheights,extrudedbuildings,roadswatergreentrees,'+
    'terrarium,bilinearground,terraindatum,contextlayers,pinned,replacebykind,oneundo,failuresnamed,contextcredit,contextexport,'+
    'notamass,contextproperties,contextcommand,contextremove,contextribbon';
  /* __acad3dV132: the map */
  window.__a3dModelToGeo=function(x,z){return bimModelToGeo(x,z);};
  window.__a3dGeoToModel=function(lon,lat){return bimGeoToModel(lon,lat);};
  window.__a3dMapSettings=function(){return bimMapSettings();};
  window.__a3dMapSet=function(f,v){return bimMapSet(f,v);};
  window.__a3dMapCommand=function(){return bimMapCommand();};
  window.__a3dMapTiles=function(){
    var c=A3D.cam,r=bimMapPlan(camVecs(c),cvW(),cvH());
    return {style:r.style,reason:r.reason,z:r.z,mpp:r.mpp||null,extent:r.extent||null,
      tiles:r.tiles.map(function(x){return {x:x.x,y:x.y,z:x.z,url:bimMapTileUrl(r.tpl,x.x,x.y,x.z)};})};
  };
  window.__a3dMapTileCorners=function(x,y,z){var o=bimMapOrigin();return o?bimMapTileCorners({x:x,y:y,z:z},o,0):null;};
  window.__a3dMapDrawn=function(){return A3D.lastMapDrawn?JSON.parse(JSON.stringify(A3D.lastMapDrawn)):null;};
  window.__a3dMapFooter=function(){return bimMapFooterHtml();};
  window.__a3dMapCache=function(){
    var k,s={ok:0,loading:0,fail:0},n=0;
    for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)){n++;s[A3D_MAP.cache[k].state]=(s[A3D_MAP.cache[k].state]||0)+1;}
    return {n:n,count:A3D_MAP.n,inflight:A3D_MAP.inflight,states:s,fail:JSON.parse(JSON.stringify(A3D_MAP.fail))};
  };
  window.__a3dMapFind=function(q){return bimMapFind(q);};
  window.__a3dMapFindReset=function(){A3D_MAP.lastFind=0;};
  window.__a3dGeoImportText=function(text,name){return bimGeoImportText(text,name);};
  window.__a3dGeoExport=function(){return JSON.parse(JSON.stringify(bimGeoExportFC()));};
  window.__a3dGeoOf=function(id){var o=objById(id);return o&&o.geo?JSON.parse(JSON.stringify(o.geo)):null;};
  /* the camera's fields, set and painted: the suite's views of the map at a known scale */
  window.__a3dCamSet=function(c){
    var k;
    for(k in c)if(c.hasOwnProperty(k)&&typeof c[k]==='number'&&isFinite(c[k])&&A3D.cam.hasOwnProperty(k))A3D.cam[k]=c[k];
    paint();
    return JSON.parse(JSON.stringify(A3D.cam));
  };
  window.__acad3dV132='mapstyles,mapoffbydefault,georefwgs84,truenorthonmap,webmercatortiles,zoomfrommpp,tilecap,'+
    'tilestore,parentfallback,corsfailuresnamed,glbasemap,canvasbasemap,notonpaper,mapcredit,mapsettingsinsite,'+
    'nominatimfind,onefindasecond,geojsonimport,kmlimport,projectedrefused,sitedatalayer,geojsonexport,massfootprint,'+
    'mapcommand,findaddresscommand,geoimportcommand,geoexportcommand,mapribbon';
  /* __acad3dV131: usages and live areas */
  window.__a3dUsages=function(){return JSON.parse(JSON.stringify(bimUsages()));};
  window.__a3dUsageDefaults=function(){return JSON.parse(JSON.stringify(BIM_USAGE_DEFAULTS));};
  window.__a3dUsageAssign=function(ids,usageId){return bimUsageAssign(ids,usageId||null);};
  window.__a3dUsageAdd=function(name){return bimUsageAdd(name);};
  window.__a3dUsageRemove=function(id){return bimUsageRemove(id);};
  window.__a3dUsageMeasure=function(id){var o=objById(id);return o?JSON.parse(JSON.stringify(bimUsageMeasure(o))):null;};
  window.__a3dUsageSummary=function(ids){return JSON.parse(JSON.stringify(bimUsageSummary(ids||null)));};
  window.__a3dUsageOf=function(id){var o=objById(id);return o?(o.usage||null):null;};
  window.__a3dExpr=function(src,vars){return bimExpr(src,vars||{});};
  window.__a3dSliceArea=function(id,y){var o=objById(id);return o?bimMeshSliceArea(o,y):null;};
  window.__acad3dV131='usagelibrary,usageintypes,usageonroomfloormass,massslicedbyfloor,floorslabgross,roomnetmeasured,'+
    'gbagfansa,formulaevaluator,formulaerrors,usageparams,usagepage,selectionareas,projectareas,usageeditor,usageschedule,'+
    'usagecommand,usagescommand,usageribbon,mirrorkeepsusage';
  /* __acad3dV130: every tool in the panel, and the dock's pins */
  window.__a3dDockPins=function(disc){return bimDockPins(disc||A3D_DISC_CUR);};
  window.__a3dSetDockPin=function(act,on){return bimSetDockPin(act,!!on);};
  window.__a3dDockPinDefaults=function(){return JSON.parse(JSON.stringify(A3D_DOCK_PIN_DEFAULTS));};
  window.__a3dToolsPanel=function(){return bimOpenToolsPanel();};
  window.__a3dToolActions=function(){   /* every tool the panel lists: every action of every tab */
    var out={},i,g,j,grs;
    for(i=0;i<A3DR_TABS.length;i++){grs=a3drTabGroups(A3DR_TABS[i]);for(g=0;g<grs.length;g++)for(j=0;j<grs[g].acts.length;j++)out[grs[g].acts[j]]=1;}
    return Object.keys(out).sort();
  };
  window.__a3dCmdUsageOf=function(act){var it=bimCatForAct(bimCmdCatalog(),act),u=bimCmdUsage();return it&&u[it.id]?u[it.id].n:0;};
  window.__acad3dV130='toolspanel,everytool,toolgroups,kindfilter,sortgroupnameused,pinnedcategory,pintodock,pinsperdiscipline,'+
    'pindefaults,pinsremembered,rowruns,panelcloses,usefromdock,dockonerow,alltoolsbutton,compactsearch';
  window.__acad3dV129='shortcutspanel,centred,categories,keysright,typingpoints,questionkey,docknames,grouplabels,'+
    'docktooltips,tooltipdelay,tooltipfocus,morebutton,searchpill,appearancetoggle';
  window.__acad3dV128='commandcatalog,ribbonmerged,aliases,synonyms,keysfromsheet,ribbonplace,layeredmatch,fuzzy,typo,'+
    'keychordsearch,frequency,recent,unavailablereason,typeanywhere,tabcycle,shortcutmode,ariacombobox,docksearchunified,'+
    'ribbontooltips,shortcutsheetsearch';
  window.__a3dRunCmd=function(act){
    var f=BIM_CMD_MAP[act];
    if(!f)return false;
    /* __acad3dV115: on the Start page no project is current, so there is nothing to act on */
    if(bimStartShowing()&&!BIM_START_CMDS[act]){a3dToast('Open a project to use that command');return false;}
    /* __acad3dV116: on a sheet only the commands that make sense on paper run */
    if(bimSheetOnScreen()&&!BIM_SHEET_CMDS[act]){a3dToast('That works on the model: go to the Model tab first');return false;}
    try{f();bimRecordCmd(f,act);return true;}
    catch(eC){
      console.warn('[BIM] Command failed: '+act,eC);
      a3dToast('That command could not run');
      return false;
    }
  };
  window.__a3dParseCoord=function(s){return bimParseCoordInput(s,A3D.sk);};
  window.__a3dSkPts=function(){return A3D.sk?A3D.sk.pts.map(function(p){return [p[0],p[1]];}):null;};
  window.__a3dPrompt=function(){return A3D.sk?bimPromptFor(A3D.sk):'Ready';};
  window.__a3dTyping=function(){return {active:A3D_TYPING.active,buf:A3D_TYPING.buf};};
  window.__a3dLastCmd=function(){return A3D.lastCmd?(A3D.lastCmd.label||''):null;};
