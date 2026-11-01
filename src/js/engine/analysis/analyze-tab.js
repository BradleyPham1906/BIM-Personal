  /* ================= __acad3dV141: Properties' tabs, with nothing selected =================
     The model's groups, sorted into tabs. Every tab's groups are in the page and the others
     hidden, so each field keeps its handler and a command can reach it; the tab shown is the
     viewer's, remembered in this browser.
     __acad3dV166b: three tabs. The Analysis tab was Analyze's settings, left behind when Analyze moved
     to the left; they are in Analyze now, in the rows they set, and the usages are on Project. */
  var BIM_PTABS=[{id:'project',label:'Project'},{id:'site',label:'Site'},{id:'view',label:'View'}];
  var BIM_PTAB_KEY='acad3dPropTab';
  function bimPTabOk(t){return BIM_PTABS.some(function(b){return b.id===t;});}
  var A3D_PTAB=(function(){try{var v=localStorage.getItem(BIM_PTAB_KEY);return bimPTabOk(v)?v:'project';}catch(eT){return 'project';}})();
  function bimPTab(tab,html){
    if(!html)return '';
    return '<div class="a3d-ptabpane'+(tab===A3D_PTAB?' on':'')+'" data-ptab="'+tab+'">'+html+'</div>';
  }
  function bimPropTabsHtml(){
    return '<div class="a3d-ptabs" role="tablist">'+BIM_PTABS.map(function(b){
      return '<button type="button" role="tab" class="a3d-ptabbtn'+(b.id===A3D_PTAB?' on':'')+'" data-ptabbtn="'+b.id+'" aria-selected="'+(b.id===A3D_PTAB)+'">'+b.label+'</button>';
    }).join('')+'</div>';
  }
  /* the tab a model group is on; null for a group that is not tabbed */
  function bimPropTabOf(name){
    name=String(name||'');
    if(name==='Identity Data'||name==='Usages'||name==='Statistics'||name==='History')return 'project';   /* __acad3dV146: History; __acad3dV166b: Usages */
    if(name==='Location'||name==='Map'||name==='Site Context'||name==='Data Layers'||name==='Standards')return 'site';   /* __acad3dV167: Standards */
    if(name==='View')return 'view';
    return null;
  }
  /* show a tab, in place: no re-render, so nothing typed is lost */
  function bimSetPropTab(tab){
    if(!bimPTabOk(String(tab)))return false;
    A3D_PTAB=tab;
    try{localStorage.setItem(BIM_PTAB_KEY,tab);}catch(eS){}
    if(el.propsbody){
      var P=el.propsbody.querySelectorAll('.a3d-ptabpane'),B=el.propsbody.querySelectorAll('.a3d-ptabbtn'),i;
      for(i=0;i<P.length;i++)P[i].classList.toggle('on',P[i].getAttribute('data-ptab')===tab);
      for(i=0;i<B.length;i++){var on=B[i].getAttribute('data-ptabbtn')===tab;B[i].classList.toggle('on',on);B[i].setAttribute('aria-selected',String(on));}
    }
    return true;
  }
  /* a command's way to a model group: nothing selected, the group open, on its tab */
  function bimPropReveal(name){
    var tb=bimPropTabOf(name);
    A3D_PROP_GROUPS_OPEN[name]=true;
    if(A3D_AW.on)A3D_AW.props=true;   /* __acad3dV171c: in Analyze, the model's Properties, and a way back to the analysis above them */
    if(tb){A3D_PTAB=tb;try{localStorage.setItem(BIM_PTAB_KEY,tb);}catch(eS){}}
    return tb;
  }
  function bimPropTabClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-ptabbtn]'):null;
    if(!b)return false;
    bimSetPropTab(b.getAttribute('data-ptabbtn'));
    return true;
  }
  /* ================= __acad3dV141: the Analyze tab ================= */
  var A3D_ANZ={lod:null,q:'',pend:false};   /* __acad3dV148: the search; __acad3dV162: a refresh held while a field is typed in */
  /* __acad3dV162: one Analyze. The analyses and the site analysis were two views behind a switch;
     they are one list now. Opening it to either is opening it. */
  function bimAnzView(){
    bimShellSetTab('analyze');
    var p=document.getElementById('a3d-leftpanel');
    return !!(p&&p.querySelector('.a3d-analyze-wrap'));
  }
  /* a category, on the right, its row in the list in view; a search that hides it is cleared. __acad3dV171c: picked,
     where it was opened in the list */
  function bimSaGoto(id){
    if(!bimSaCat(id))return false;
    A3D_ANZ.q='';
    bimAwPick('cat',id);
    return !!document.querySelector('.a3d-analyze-wrap [data-sacat="'+id+'"]');
  }
  /* __acad3dV148: a row, not a card. __acad3dV171c: a row of the list, its name and its state; what it says,
     its settings and its buttons on the right when it is picked */
  /* __acad3dV162: an analysis sits in the category it answers; what reads the model itself is Model */
  var BIM_ANZ_GROUP_OF={survey:'landform',terrain:'landform',grading:'landform',rain:'water',sun:'climate',sunhours:'climate',solar:'climate',
    dgframe:'location',dgsun:'climate',dgshadow:'climate',dgwind:'climate',dgviews:'people',dgnoise:'risk'};   /* __acad3dV164: the analyses in the model */
  /* __acad3dV165: land and water */
  BIM_ANZ_GROUP_OF.dgcontours='landform';BIM_ANZ_GROUP_OF.dgslope='landform';BIM_ANZ_GROUP_OF.dgaspect='landform';
  BIM_ANZ_GROUP_OF.dgflow='water';BIM_ANZ_GROUP_OF.dgponds='water';BIM_ANZ_GROUP_OF.dgflood='water';
  /* __acad3dV166: movement */
  BIM_ANZ_GROUP_OF.dgstreets='access';BIM_ANZ_GROUP_OF.dgcycling='access';BIM_ANZ_GROUP_OF.dgtransit='access';
  BIM_ANZ_GROUP_OF.dgwalk='access';BIM_ANZ_GROUP_OF.dgvehicles='access';BIM_ANZ_GROUP_OF.dgneeds='people';
  BIM_ANZ_GROUP_OF.dgtraffic='access';   /* __acad3dV171 */
  /* __acad3dV168: land */
  BIM_ANZ_GROUP_OF.dglanduse='location';BIM_ANZ_GROUP_OF.dgfigure='location';BIM_ANZ_GROUP_OF.dggreen='ecology';BIM_ANZ_GROUP_OF.dgzoning='legal';
  var BIM_ANZ_MODEL=['lens','areas','lod','stats','structure'];
  function bimAnzStateText(s){return s==='on'?'On':s==='warn'?'Check':s==='fail'?'Problems':s==='stale'?'Out of date':s==='busy'?'Running':'Off';}
  function bimAnzBtn(a){
    return '<button type="button" class="a3d-anzbtn'+(a.pri?' pri':'')+(a.lay?' lay':'')+'" data-anzact="'+a.act+'"'+(a.off?' disabled title="'+bimEsc(a.off)+'"':(a.tip?' title="'+bimEsc(a.tip)+'"':''))+'>'+bimEsc(a.label)+'</button>';
  }
  /* the surface shown by slope, elevation or aspect, if one is */
  function bimAnzTerrainShown(){return A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey&&o.tview&&o.tview!=='cutfill';})[0]||null;}
  /* Add as layer, on the analyses whose result is a picture on the plan */
  function bimAnzLayerAct(id){
    var tip='Keep it as a layer, in Layers under Analysis',s,o;
    if(id==='sunhours'||id==='rain'){
      s=id==='sunhours'?A3D_SIM.sun:A3D_SIM.rain;
      return {act:'layer:'+id,label:'Add as layer',lay:true,tip:tip,off:!s?'Run it first':bimResHolds(s)?'This run is a layer already':''};
    }
    if(id==='terrain'){o=bimAnzTerrainShown();return {act:'layer:terrain',label:'Add as layer',lay:true,tip:tip,off:o?'':'Show slope, elevation or aspect first'};}
    if(id==='grading'){
      o=A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading;})[0];
      return {act:'layer:cutfill',label:'Add as layer',lay:true,tip:tip,off:!o?'Grade first':bimResLayers().some(function(R){return R.kind==='terrain'&&R.mode==='cutfill'&&R.src===o.id;})?'Its cut and fill is a layer already':''};
    }
    return null;
  }
  /* each analysis: what it shows now, and its buttons */
  function bimAnzCards(){
    var C=[],i,o,nC=0,nB=0,nU=0,nTer=0,sv={pass:0,warn:0,fail:0},lods={};
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(bimIsFrameMember(o)){if(o.bim.type==='column')nC++;else nB++;}
      if(o.usage)nU++;
      if(o.t==='terrain'&&o.survey&&!o.grading){nTer++;try{var rs=bimSurveyCheck(o);if(rs)sv[rs.verdict]=(sv[rs.verdict]||0)+1;}catch(eS){}}
      var L=bimLodOf(o);if(L)lods[L.lod]=(lods[L.lod]||0)+1;
    }
    var fr=nC+nB;
    C.push({id:'structure',title:'Frame analysis',state:A3D_STRUCT.show?'on':'off',
      status:fr?nC+' column'+(nC===1?'':'s')+', '+nB+' beam'+(nB===1?'':'s')+(A3D_STRUCT.show?': forces and deflection shown':''):'No frame yet: place columns and beams',
      extra:bimAnzFrameHtml(),   /* __acad3dV166b: its settings, and the floor loads, in the row */
      acts:[{act:'structure:run',label:A3D_STRUCT.show?'Run again':'Run',pri:true,off:fr?'':'Place columns and beams first'},
        {act:'structure:off',label:'Hide',off:A3D_STRUCT.show?'':'Not shown'}]});
    var sun=bimSunNow();
    C.push({id:'sun',title:'Sun and shadows',state:A3D.showSun?'on':'off',
      status:sun.missing?'Set the site '+sun.missing.join(', ')+' (Site: Location)':(sun.settings.time+' on '+sun.settings.date+(sun.elevation>0?', the sun at '+sun.elevation.toFixed(1)+'\u00b0':', the sun below the horizon')),
      acts:[{act:'sun:toggle',label:A3D.showSun?'Hide':'Show',pri:!A3D.showSun},{act:'open:Location',label:'Settings'}]});
    var ls=bimLensSettings();
    C.push({id:'lens',title:'Colour by',state:ls.by?'on':'off',status:ls.by?(BIM_LENS_LABEL[ls.by]||ls.by)+(ls.by==='prop'&&ls.prop?': '+ls.prop:''):'Off: colour the model by usage, level, type or any property',
      acts:[{act:'open:View',label:'Settings',pri:true}]});
    var us=bimUsageSummary(null);
    C.push({id:'areas',title:'Areas by usage',state:null,status:us.rows.length?us.rows.length+' usage'+(us.rows.length===1?'':'s')+' on '+nU+' object'+(nU===1?'':'s')+', GBA '+bimDispNum(us.total.GBA,2)+' m\u00b2':'No usages given yet',
      extra:bimAnzAreasHtml(),   /* __acad3dV166b: the areas, in the row; the usages are in Properties, Project */
      acts:[{act:'open:Usages',label:'Usages'}]});
    C.push({id:'survey',title:'Survey check',state:nTer?(sv.fail?'fail':sv.warn?'warn':'on'):null,
      status:nTer?nTer+' surface'+(nTer===1?'':'s')+': '+sv.pass+' pass, '+sv.warn+' warn, '+sv.fail+' fail':'No survey surface yet: make one with SURVEY',
      acts:[{act:'survey:run',label:'Check',pri:true,off:nTer?'':'No survey surface yet'}]});
    /* __acad3dV144: terrain analysis */
    var TT=A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey;}),tv=TT.filter(function(o){return o.tview;})[0],tvs='';
    if(tv){try{var tvb=bimBandsOf(tv,tv.tview),tvt=tvb.bands.slice().sort(function(x,y){return y.area-x.area;})[0];
      tvs=tv.name+' coloured by '+tv.tview+(tvt&&tvt.area>0?': most of it '+tvt.label+' ('+Math.round(tvt.share*100)+'%)':'');}catch(eTv){tvs=tv.name+' could not be measured';}}
    C.push({id:'terrain',title:'Slope, elevation, aspect',state:TT.length?(tv?'on':'off'):null,
      status:TT.length?(tvs||TT.length+' surface'+(TT.length===1?'':'s')+': colour by slope, elevation or the way the ground faces'):'No terrain yet: make one with SURVEY, or import LandXML',
      acts:[{act:'terrain:slope',label:'Slope',pri:true,off:TT.length?'':'No terrain yet'},{act:'terrain:elevation',label:'Elevation',off:TT.length?'':'No terrain yet'},
        {act:'terrain:aspect',label:'Aspect',off:TT.length?'':'No terrain yet'},{act:'terrain:off',label:'Off',off:tv?'':'Not coloured'},
        {act:'terrain:landxml',label:'Export LandXML',off:TT.length?'':'No terrain yet'}]});
    /* __acad3dV145: grading */
    var GP=A3D.objs.filter(bimIsPad),GS=A3D.objs.filter(function(o){return o.t==='terrain'&&o.grading;}),gs0=GS[0],gv=gs0&&gs0.grading.volume,gst=gs0&&bimGradeStale(gs0);
    C.push({id:'grading',title:'Grading, cut and fill',state:gs0?(gst?'stale':'on'):(GP.length?'off':null),
      status:gs0?gs0.name+(gv?': cut '+bimDispNum(gv.cut,1)+' m\u00b3, fill '+bimDispNum(gv.fill,1)+' m\u00b3, net '+(gv.net>=0?bimDispNum(gv.net,1)+' m\u00b3 to take away':bimDispNum(-gv.net,1)+' m\u00b3 to bring in'):'')+
        (gst?' (the pads or the ground have changed since)':''):
        (GP.length?GP.length+' pad'+(GP.length===1?'':'s')+' ready: Grade runs their slopes out to the ground':'No pads yet: give a closed outline a Pad Elevation'),
      acts:[{act:'grade:run',label:gs0?'Grade again':'Grade',pri:true,off:GP.length?'':'No pads yet'},{act:'grade:map',label:'Cut and fill map',off:gs0?'':'Grade first'},
        {act:'grade:arrows',label:'Slope arrows',off:TT.length?'':'No terrain yet'}]});
    var lk=Object.keys(lods).sort(),nb=0;lk.forEach(function(k){nb+=lods[k];});
    var last=A3D_ANZ.lod;
    C.push({id:'lod',title:'Buildings, LOD and solids',state:last?(last.bad.length?'fail':'on'):null,
      status:nb?nb+' '+(nb===1?'building or city object':'buildings and city objects')+' ('+lk.map(function(k){return lods[k]+' LOD'+k;}).join(', ')+')'+(last?'; last check: '+last.valid+' valid'+(last.bad.length?', '+last.bad.length+' with problems':''):''):'No buildings yet: get them with Site Context, or import CityJSON',
      acts:[{act:'lod:run',label:'Check',pri:true,off:nb?'':'No buildings yet'},{act:'lod:cityjson',label:'Export CityJSON',off:nb?'':'No buildings yet'}]});
    C.push({id:'stats',title:'Statistics',state:null,status:A3D.objs.length+' object'+(A3D.objs.length===1?'':'s')+', '+A3D.levels.length+' level'+(A3D.levels.length===1?'':'s')+', '+A3D.sheets.length+' sheet'+(A3D.sheets.length===1?'':'s'),
      acts:[{act:'open:Statistics',label:'Open'}]});
    /* __acad3dV143: the simulations */
    var miss=bimSunNow().missing,ms=miss?'Set the site '+miss.join(', ')+' first (Site: Location)':'',sh=A3D_SIM.sun,so=A3D_SIM.solar,ra=A3D_SIM.rain;
    var nSol=bimSolarTargets(null).length,ter=bimRainTerrain(null);
    C.push({id:'sunhours',sim:true,title:'Sun hours',state:sh?(bimSimStale(sh)?'stale':'on'):'off',
      status:ms||(sh?'Ground in direct sun on '+sh.date+': '+bimDispNum(sh.min,1)+' to '+bimDispNum(sh.max,1)+' h of '+bimDispNum(sh.day,1)+' h; '+Math.round(sh.sixPlus*100)+'% has 6 h or more'+(bimSimStale(sh)?' (the model or the date has changed since)':''):
        'Hours of direct sun on the ground through the site\'s date, every 15 minutes'),
      extra:sh?'<div class="a3d-anzleg"><span>'+bimDispNum(0,0)+' h</span><span class="a3d-anzramp">'+BIM_SIM_RAMP.map(function(c){return '<i style="background:'+c+'"></i>';}).join('')+'</span><span>'+bimDispNum(sh.day,1)+' h</span></div>':'',
      acts:[{act:'sunhours:run',label:sh?'Run again':'Run',pri:true,off:ms},{act:'sim:clear:sun',label:'Clear',off:sh?'':'Not run'},{act:'open:Location',label:'Date'}]});
    C.push({id:'solar',sim:true,title:'Solar on roofs and facades',state:A3D_SIM.busy==='solar'?'busy':so?(bimSimStale(so)?'stale':'on'):'off',
      status:ms||(A3D_SIM.busy==='solar'?'Running ...':so?so.count+' solid'+(so.count===1?'':'s')+(so.roofMean!==null?': roofs '+Math.round(so.roofMean)+' kWh/m\u00b2 a year on average':'')+
        ' (clear sky, no clouds'+(so.shaded?', shaded by the others':'')+')'+(bimSimStale(so)?'; the model has changed since':''):
        (nSol?'A clear-sky year of sun on the faces of '+nSol+' solid'+(nSol===1?'':'s')+' (the selection, if any)':'No buildings or solids yet')),
      acts:[{act:'solar:run',label:so?'Run again':'Run',pri:true,off:ms||(nSol?'':'No buildings or solids yet')||(A3D_SIM.busy?'Running':'')},
        {act:'solar:colour',label:'Colour by',off:so?'':'Run it first'},{act:'sim:clear:solar',label:'Clear',off:so?'':'Not run'}]});
    C.push({id:'rain',sim:true,title:'Rain on terrain',state:ra?(bimSimStale(ra)?'stale':'on'):'off',
      status:ra?ra.name+': '+ra.ponds.length+' pond'+(ra.ponds.length===1?'':'s')+(ra.ponds.length?', '+bimDispNum(ra.pondVolume,1)+' m\u00b3 held, the deepest '+bimDispNum(ra.ponds[0].depth,2)+' m':'')+
        '; flow lines where '+bimDispNum(ra.threshold*ra.cell*ra.cell,0)+' m\u00b2 or more drains'+(bimSimStale(ra)?' (the surface has changed since)':''):
        (ter?'Where rain runs and ponds on '+ter.name:'No terrain yet: make one with SURVEY, or get the site context'),
      acts:[{act:'rain:run',label:ra?'Run again':'Run',pri:true,off:ter?'':'No terrain yet'},{act:'sim:clear:rain',label:'Clear',off:ra?'':'Not run'}]});
    C=bimDgCards().concat(C);   /* __acad3dV164: what Analyze site draws, first in its category */
    bimLbCards().forEach(function(c){C.push(c);});   /* __acad3dV172b: Ladybug's rows, in Climate */
    C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});   /* __acad3dV148 */
    return C;
  }
  function bimAnzCountText(C){
    var n=C.filter(function(c){return c.state==='on'||c.state==='stale'||c.state==='busy';}).length,F=bimSaShown(),r=0;
    F.forEach(function(f){if(f.cls==='redflag')r++;});
    return bimSaN(F.length,'finding')+(r?', '+bimSaN(r,'red flag'):'')+(n?' · '+n+' on':'');
  }
  /* every word asked for starts a word of the text: rain is not in terrain */
  function bimAnzWordsHit(q,text){
    var s=' '+String(text).toLowerCase().replace(/[^a-z0-9\u00c0-\u024f]+/g,' ')+' ',W=String(q).toLowerCase().split(/[^a-z0-9\u00c0-\u024f]+/),i;
    for(i=0;i<W.length;i++)if(W[i]&&s.indexOf(' '+W[i])<0)return false;
    return true;
  }
  /* __acad3dV162: the search, in place. __acad3dV171c: over the list. A category asked for by its own words -- its
     name, its question, where its data is, what was found -- shows whole; otherwise the analyses in it that match,
     by their name, what they show, what they report and their buttons */
  function bimAnzFilter(w){
    var q=String(A3D_ANZ.q||'').toLowerCase().replace(/^\s+|\s+$/g,''),root=w?w.querySelector('.a3d-awl'):null,n=0,C={},K,i,j,R,k,c,nm,whole,hit,e,ov;
    if(!root)return 0;
    function show(x,v){if(v)x.removeAttribute('hidden');else x.setAttribute('hidden','');}
    root.classList.toggle('q',!!q);
    if(q){bimAnzCards().forEach(function(x){C[x.id]=x;});bimTlCards().forEach(function(x){C[x.id]=x;});}   /* __acad3dV172: the tools' rows */
    ov=root.querySelector('.a3d-awl-ov');
    if(ov)show(ov,!q);
    K=root.querySelectorAll('[data-sacat],[data-anzgrp]');
    for(i=0;i<K.length;i++){
      c=bimSaCat(K[i].getAttribute('data-sacat'));nm=c?c.n:(K[i].getAttribute('data-anzgrp')==='tools'?'Tools':'Model');
      whole=!q||(!!c&&bimAnzWordsHit(q,c.n+' '+c.q+' '+(BIM_SA_SEE[c.id]?BIM_SA_SEE[c.id][1]:'')+' '+bimSaOf(c.id).map(function(f){return f.title+' '+f.value+' '+bimSaPair(BIM_SA_CLS,f.cls)+' '+f.source;}).join(' ')));
      R=K[i].querySelectorAll('[data-anzcard]');k=0;
      for(j=0;j<R.length;j++){hit=whole||bimAnzWordsHit(q,bimAwRowWords(C[R[j].getAttribute('data-anzcard')],nm));show(R[j],hit);if(hit)k++;}
      show(K[i],whole||k>0);
      if(q)n+=k+(whole&&c?1:0);
    }
    e=root.querySelector('.a3d-anzempty');
    if(e)show(e,!!q&&!n);
    return n;
  }
  /* the list again, when Analyze is open: the search, its focus and the scroll stay.
     __acad3dV162: not under a field being typed in, whose words would go -- then when it is left. */
  function bimAnalyzeRefresh(force){
    var sh=document.getElementById('a3d-shell'),w=sh&&sh.dataset.tab==='analyze'?sh.querySelector('.a3d-analyze-wrap'):null,a=document.activeElement;
    if(!w)return false;
    if(!force&&a&&w.contains(a)&&/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)&&!a.hasAttribute('data-anzsearch')&&a.type!=='checkbox'&&a.type!=='file'){A3D_ANZ.pend=true;return false;}
    A3D_ANZ.pend=false;
    try{bimRenderInto(w,bimAwListHtml());bimAnzFilter(w);}   /* __acad3dV171c: one list, the workspace's */
    catch(eA){console.warn('[BIM] Analyze panel',eA);}
    return true;
  }
  /* a button: run it, or open its settings in Properties */
  function bimAnzAct(a){
    var k=String(a||''),g;
    if(k.indexOf('aw:')===0)return bimAwAct(k.slice(3));   /* __acad3dV171b: the workspace */
    if(k.indexOf('open:')===0){
      g=k.slice(5);
      A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
      bimPropReveal(g);
      refreshTree();refreshProps();paint();
      var gEl=null,all=el.propsbody?el.propsbody.querySelectorAll('[data-a3dpgrp]'):[],i;
      for(i=0;i<all.length;i++)if(all[i].getAttribute('data-a3dpgrp').indexOf(g)===0){gEl=all[i];break;}
      if(gEl){try{gEl.scrollIntoView({block:'start'});}catch(eS){}}
      bimAnalyzeRefresh();
      return true;
    }
    if(k==='structure:run')bimAnalyzeCommand();
    else if(k==='structure:off')bimAnalyzeOff();
    else if(k==='sun:toggle')bimToggleSun();
    else if(k==='survey:run')bimSurveyCheckCommand();
    else if(k==='terrain:landxml')bimLandXmlExport(null);   /* __acad3dV144 */
    else if(k==='grade:run')bimGradeCommand();   /* __acad3dV145 */
    else if(k==='grade:map')bimCutFillMapCommand();
    else if(k==='grade:arrows')bimSlopeArrowsCommand();
    else if(k.indexOf('terrain:')===0)bimTerrainViewCommand(k==='terrain:off'?'':k.slice(8));
    else if(k==='lod:run')bimLodCheck();
    else if(k==='lod:cityjson')bimCityJsonExport();
    else if(k==='sunhours:run')bimSunHoursCommand();   /* __acad3dV143 */
    else if(k==='solar:run'){bimSolarCommand();bimAnalyzeRefresh();return true;}
    else if(k==='solar:colour'){bimLensSet('prop','Solar on roof (kWh/m2 a year)');}
    else if(k==='rain:run')bimRainCommand(null);
    else if(k.indexOf('sim:clear:')===0)bimSimClear(k.slice(10));
    else if(k.indexOf('layer:')===0)bimResultLayerAdd(k.slice(6));   /* __acad3dV148 */
    else if(k.indexOf('dg:')===0)bimDgAct(k.slice(3));   /* __acad3dV164 */
    else if(k.indexOf('tr:')===0)bimTrAct(k.slice(3));   /* __acad3dV171 */
    else if(k.indexOf('lb:')===0)return bimLbAct(k.slice(3));   /* __acad3dV172b: Ladybug's rows refresh as their work ends */
    else return false;
    bimAnalyzeRefresh();
    return true;
  }
  function bimAnalyzeCommandTab(){bimShellSetTab('analyze');return true;}
  /* ================= __acad3dV164: site analysis drawn in the model =================
     reference/research-site-analysis-in-model.md. The owner: "a live analysis that is editable".
     Each analysis draws its diagram as elements of the model -- objects of their own kind, 'diag',
     on a layer of their own under Site analysis -- so each can be selected, moved, turned, restyled,
     relabelled or deleted like anything drawn by hand, and each is live: the analysis lays it down
     again whenever it runs.

     An element keeps the analysis's own version of itself (gen). One the owner has changed -- moved,
     turned, restyled, relabelled -- no longer matches it, and a run leaves it as it is (marking it
     when the analysis would now draw it differently); one the owner deleted stays deleted; Reset
     gives either back to the analysis. That is worked out by comparison when a run comes, so no
     editing path has to report itself.

     An element: {t:'diag', name, layer, pos, dg:{a, k, g, s, lb, sym, info, gen}}
       a, k   the analysis and the element's key within it
       g      its geometry, in metres, [x, y, z] points about pos:
                line   pts, closed            segs   pts in pairs
                marks  pts (a path), marks [{p, t}] (dots with labels on it)
                live   {kind:'shadow', date, time, c, r}: drawn from the model each time, never stored
                bands  [{lv, col, pts}]: areas in classes (a road's noise), the higher class over
                       __acad3dV165: or {lv, col, rings:[[p...]...]}, an area of many parts, holes
                       and islands read even-odd (a slope class); drawn in its element's fill
                lines  lines [[p...]...]: several polylines (a contour level, the divides)
       s      stroke, fill, w (pixels), dash, op, fop (the fill's opacity), head (an arrowhead)
       lb     labels [{t, p, sz, col, al, pri}]: placed by priority, so none is drawn over another
       sym    a symbol {type:'noise'|'storm'|'dot', p, r, col, toward}
       info   {title, rows:[[label, value]], method, source, date}
     The colour -- bands, fills, shadows -- is drawn under the model, as the result layers are; the
     lines, symbols and words over it, so a building never hides what it is measured against.
     Diagram elements carry no mesh, so schedules, quantities, the LOD checks and the IFC, DXF and
     CityJSON exports, which read meshes and building types, pass them by. */
