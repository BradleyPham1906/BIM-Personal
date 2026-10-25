  /* ================= __acad3dV171b: the analysis workspace =================
     reference/research-analysis-workspace.md. The site analysis is a place one goes into and leaves, as archiMap's
     and Forma's are: a bar over the view with the analysis in focus and a cross; on the left the analyses in their
     groups, one in focus and others ticked under it; on the right, where Properties is while nothing is selected,
     the one analysis: what it shows, its settings, its chart, its key, what the run said and its source. The view
     goes quiet in the app's mode, light or dark: its ground, the map greyed and faded, the context in the mode's
     greys, so only the data keeps its colour. The focus and the ticks are the layers' visibility, one undo step
     each, so Layers and the sheets agree; they are the project's, kept with it. */
  var BIM_AW_GROUPS=[
    {id:'site',name:'Site',an:['frame']},
    {id:'sun',name:'Sun and wind',an:['sun','shadow','wind']},
    {id:'see',name:'Views and noise',an:['views','noise']},
    {id:'ground',name:'Land and water',an:['contours','slope','aspect','flow','ponds','flood']},
    {id:'move',name:'Movement',an:['streets','cycling','transit','walk','needs','vehicles','traffic']},
    {id:'land',name:'Land',an:['landuse','figure','green','zoning']}];
  var BIM_AW_ABOUT={
    frame:'True north and rings every 100 m from the site: the bearing and the scale of everything else.',
    sun:'The sun\'s path over the site on the solstices and the equinoxes, with its hours, and where it is now.',
    shadow:'Where the buildings cast their shadows at 9, 12 and 15 on the solstices and the equinox.',
    wind:'The winds by season from a year of hourly data, and the direction of the strongest.',
    views:'What can be seen from the site, at eye level and from the top floor.',
    noise:'The road and rail noise reaching the site, in bands of 5 dB.',
    contours:'The ground\'s height in lines, from the terrain around the site.',
    slope:'How steep the ground is, in classes.',
    aspect:'Which way the ground faces.',
    flow:'Where rain runs over the ground, where the divides are, and where it drains.',
    ponds:'Where water would gather in the hollows.',
    flood:'The flood zones mapped around the site.',
    streets:'The streets by class, from motorway to path, and their speeds.',
    cycling:'How stressful each street is to ride a bicycle on.',
    transit:'The bus and rail stops within reach, their lines, and the walk to them.',
    walk:'How long it takes to walk from the site along the streets.',
    needs:'The daily needs within a walk: food, health, learning, parks, eating out and services.',
    vehicles:'How cars reach the site: the driveway, its entry, the doors, the car parks and parking on the street.',
    traffic:'Cars and walkers on the streets around the site in the peak hour, played on the clock.',
    landuse:'What the land around the site is used for, in the planners\' colours.',
    figure:'The buildings in black on white: the grain of the place.',
    green:'The trees, the green spaces, and the green that can be seen.',
    zoning:'The zoning districts around the site.'};
  /* the view's quiet tones in each mode; only the data keeps its colour */
  var BIM_AW_LOOK={
    light:{light:true,bg:'#f2f2ef',fade:0.35,grey:1,grid:'#e2e2de',ink:'#2a2e33',halo:'rgba(255,255,255,0.92)',
      ctx:{buildings:'#fbfbfa',roads:'#dcdcd8',water:'#bdd5ea',green:'#d4e7cd',trees:'#a9cd9f',rail:'#cbc6bf',airports:'#e4e4e0',power:'#d6d6d2',landuse:'#ebeae5',terrain:'#e9e8e3'},
      key:{bg:'rgba(255,255,255,0.95)',line:'rgba(0,0,0,0.12)',ink:'#1f2328',sub:'#6b7280'}},
    dark:{light:false,bg:'#17191c',fade:0.3,grey:1,grid:'#24282d',ink:'#e8edf2',halo:'rgba(10,12,15,0.86)',
      ctx:{buildings:'#4c525b',roads:'#363b42',water:'#22384d',green:'#25372a',trees:'#2f5236',rail:'#3d3a35',airports:'#2c3035',power:'#3a3e44',landuse:'#25282d',terrain:'#25292e'},
      key:{bg:'rgba(22,26,32,0.92)',line:'rgba(255,255,255,0.16)',ink:'#e8edf2',sub:'#9aa7b4'}}};
  var A3D_AW={on:false,wired:false};
  function bimAwState(){
    var D=bimDgState(),S=D.aw;
    if(!S||typeof S!=='object')S=D.aw={focus:null,add:[]};
    if(S.focus!==null&&!bimDgAn(S.focus))S.focus=null;
    if(!Array.isArray(S.add))S.add=[];
    S.add=S.add.filter(function(a,i,L){return !!bimDgAn(a)&&a!==S.focus&&L.indexOf(a)===i;});
    return S;
  }
  /* an analysis drawn now: its layer, and those above it, on */
  function bimAwShown(a){var ly=bimLayerById(bimDgState().layers[a]);return !!(ly&&bimLayerEff(ly).on);}
  /* the focus as the view shows it: an undo can hide a layer the focus names */
  function bimAwFocusNow(){var S=bimAwState();return S.focus&&bimAwShown(S.focus)?S.focus:null;}
  function bimAwLook(){
    if(!A3D_AW.on||A3D.sheetCapture||A3D_PLOT.on)return null;
    return document.body.classList.contains('light-theme')?BIM_AW_LOOK.light:BIM_AW_LOOK.dark;
  }
  function bimAwRgb(hex){var n=parseInt(String(hex).slice(1),16);return [((n>>16)&255)/255,((n>>8)&255)/255,(n&255)/255];}
  /* the view's background, for WebGL, WebGPU and the canvas */
  function bimAwBg(){var L=bimAwLook();return L?bimAwRgb(L.bg):[0.114,0.125,0.141];}
  function bimAwBgHex(){var L=bimAwLook();return L?L.bg:'#1d2024';}
  /* a context object's quiet tone, by the kind Site Context recorded on it */
  function bimAwCtxCol(o){
    var L=bimAwLook(),k=o&&o.context&&o.context.kind;
    return L&&k&&L.ctx.hasOwnProperty(k)?L.ctx[k]:null;
  }
  /* a word's colour on the quiet ground: on paper a light colour is darkened to be read */
  function bimAwInk(col){
    var L=bimAwLook();
    if(!L)return col;
    if(!col)return L.ink;
    if(!L.light)return col;
    var c=bimAwRgb(col),y=0.299*c[0]+0.587*c[1]+0.114*c[2];
    return y>0.55?shade(col,0.55/y):col;
  }
  /* ---- the focus and the ticks, as the layers' visibility; one undo step, none inside a run's ---- */
  function bimAwApply(push){
    var D=bimDgState(),S=bimAwState(),ch=[],i,A,ly,v,root=bimLayerById(D.layers.root);
    for(i=0;i<BIM_DG_AN.length;i++){
      A=BIM_DG_AN[i];ly=bimLayerById(D.layers[A.id]);
      if(!ly)continue;
      v=A.id===S.focus||S.add.indexOf(A.id)>=0;
      if((ly.visible!==false)!==v)ch.push([ly,v]);
    }
    if(root&&root.visible===false&&(S.focus||S.add.length))ch.push([root,true]);
    if(!ch.length)return 0;
    if(push)pushUndo();
    ch.forEach(function(c){c[0].visible=c[1];});
    bimLayerChanged();
    return ch.length;
  }
  function bimAwRefresh(){
    bimAwBar();
    bimAnalyzeRefresh(true);
    refreshProps();
    paint();
  }
  function bimAwFocus(a){
    a=a?String(a):null;
    if(a&&!bimDgAn(a))return false;
    var S=bimAwState(),add=S.add.filter(function(x){return x!==a;});
    if(S.focus!==a||add.length!==S.add.length||bimAwFocusNow()!==a){
      pushUndo();   /* the step taken before the change, so undoing it gives the focus back with the layers */
      S.focus=a;S.add=add;
      var held=bimUndoHold;bimUndoHold=true;
      try{bimAwApply(false);}finally{bimUndoHold=held;}
      saveSoon();
    }
    if(!A3D_AW.on)bimAwOpen();
    bimAwRefresh();
    return true;
  }
  /* a tick: drawn under the focus, or no longer; the focus unticked is no longer in focus */
  function bimAwTick(a){
    if(!bimDgAn(a))return false;
    var S=bimAwState(),on=bimAwShown(a);
    pushUndo();
    if(on){if(S.focus===a)S.focus=null;S.add=S.add.filter(function(x){return x!==a;});}
    else if(S.add.indexOf(a)<0)S.add.push(a);
    var held=bimUndoHold;bimUndoHold=true;
    try{bimAwApply(false);}finally{bimUndoHold=held;}
    saveSoon();
    bimAwRefresh();
    return true;
  }
  /* ---- in and out ---- */
  /* the surface, the focus as it is */
  function bimAwOpen(){
    A3D_AW.on=true;
    document.body.classList.add('a3d-aw');
    bimShellSetTab('analyze');
    if(bimShellTier()==='phone'){var sh=document.getElementById('a3d-shell');if(sh)sh.classList.add('collapsed');}   /* a phone: the view, not the drawer */
    bimAwWire();
  }
  function bimAwEnter(focus){
    if(focus!==undefined)return bimAwFocus(focus);
    bimAwOpen();
    bimAwRefresh();
    return true;
  }
  function bimAwLeave(){
    if(!A3D_AW.on)return false;
    A3D_AW.on=false;
    document.body.classList.remove('a3d-aw');
    bimAwBar();
    var w=document.querySelector('.a3d-analyze-wrap');
    if(w)w.innerHTML=bimAnalyzeHtml();
    bimAnalyzeRefresh(true);
    refreshProps();
    paint();
    return true;
  }
  /* Analyze site, as it ends, inside its one undo step: the first time the site and its context, and the list; again,
     what was in focus and ticked, drawn again */
  function bimAwAfterRun(){
    var S=bimAwState(),held=bimUndoHold;
    if(!bimDgState().last){S.focus=null;S.add=[];}
    bimUndoHold=true;
    try{bimAwApply(false);}finally{bimUndoHold=held;}
    bimAwOpen();
    bimAwBar();
  }
  /* TRAFFIC: in focus, inside the step the command took */
  function bimAwTraffic(){
    var S=bimAwState(),held=bimUndoHold;
    S.focus='traffic';S.add=S.add.filter(function(x){return x!=='traffic';});
    bimUndoHold=true;
    try{bimAwApply(false);}finally{bimUndoHold=held;}
    bimAwOpen();
    bimAwRefresh();
  }
  /* ---- the bar over the view, and a phone's row of analyses under it ---- */
  function bimAwBar(){
    var vp=el.cv?el.cv.parentNode:null,b=document.getElementById('a3d-awbar');
    if(!A3D_AW.on){if(b)b.parentNode.removeChild(b);return null;}
    if(!vp)return null;
    if(!b){
      b=document.createElement('div');b.id='a3d-awbar';b.className='a3d-awbar';
      b.addEventListener('click',function(ev){
        var t=ev.target&&ev.target.closest?ev.target.closest('[data-awact]'):null;
        if(t)bimAwAct(t.getAttribute('data-awact'));
      });
      vp.appendChild(b);
    }
    var f=bimAwFocusNow(),A=f?bimDgAn(f):null,S=bimAwState(),D=bimDgState(),ch='';
    BIM_DG_AN.forEach(function(X){
      if(!D.runs[X.id])return;
      ch+='<button type="button" class="a3d-awchip'+(X.id===f?' on':(bimAwShown(X.id)?' add':''))+'" data-awact="focus:'+X.id+'" aria-pressed="'+(X.id===f)+'">'+
        '<i style="background:'+bimEsc(X.col)+'"></i>'+bimEsc(X.name)+'</button>';
    });
    bimRenderInto(b,'<div class="a3d-awbar-row"><span class="a3d-awbar-k">Site analysis</span><span class="a3d-awbar-sep" aria-hidden="true"></span>'+
      '<span class="a3d-awbar-t" data-awbart="1">'+bimEsc(A?A.name:'Overview')+'</span>'+
      (S.add.filter(bimAwShown).length?'<span class="a3d-awbar-n">+ '+S.add.filter(bimAwShown).length+'</span>':'')+
      '<button type="button" class="a3d-awbar-d" data-awact="panel" title="The analysis\'s panel" aria-label="The analysis\'s panel">Details</button>'+
      '<button type="button" class="a3d-awbar-x" data-awact="leave" title="Leave the site analysis" aria-label="Leave the site analysis">'+
      '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg></button></div>'+
      (ch?'<div class="a3d-awchips" role="group" aria-label="The analyses">'+ch+'</div>':''));
    var on=b.querySelector('.a3d-awchip.on'),row=b.querySelector('.a3d-awchips');   /* a phone's row: the one in focus in sight */
    if(on&&row&&row.clientWidth&&(on.offsetLeft<row.scrollLeft||on.offsetLeft+on.offsetWidth>row.scrollLeft+row.clientWidth))row.scrollLeft=Math.max(0,on.offsetLeft-12);
    return b;
  }
  /* ---- the left: the analyses in their groups ---- */
  function bimAwRowState(a){
    var D=bimDgState(),R=D.runs[a],n=R?bimDgDiags(a).length:0;
    if(!R)return {cls:' none',st:'Not run'};
    var SC=bimDgStdChanged(a);
    if(SC.run.length||SC.data.length)return {cls:' stale',st:'Out of date'};
    if(!n&&a!=='traffic')return {cls:' none',st:'Nothing'};
    return {cls:'',st:''};
  }
  function bimAwListHtml(){
    var f=bimAwFocusNow(),D=bimDgState(),h,P=A3D.objs.filter(bimIsProperty),st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon);
    h='<div class="a3d-awl" data-awlist="1">'+
      '<div class="a3d-awl-hd"><button type="button" class="a3d-awl-back" data-anzact="aw:leave" title="Back to Analyze: leave the site analysis">'+
      '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 3.5 5.5 8 10 12.5"/></svg>Analyze</button>'+
      '<span class="a3d-awl-ttl">Site analysis</span></div>'+
      '<div class="a3d-awl-site">'+bimEsc(placed?bimSitePlaceText():'Not placed yet')+(P.length?'<br>'+bimEsc(P[0].name):'')+(D.last?' &middot; '+bimEsc(D.last.date):'')+
      (D.last&&placed?' <button type="button" class="a3d-awl-again" data-anzact="aw:analyze"'+(A3D_SITERUN.busy?' disabled':'')+'>'+(A3D_SITERUN.busy?'Analyzing ...':'Analyze again')+'</button>':'')+'</div>'+
      '<button type="button" class="a3d-awl-row a3d-awl-ov'+(f?'':' focus')+'" data-anzact="aw:focus:" aria-pressed="'+(!f)+'"><span class="a3d-awl-nm">Overview</span><span class="a3d-awl-st">The site and its context</span></button>';
    BIM_AW_GROUPS.forEach(function(G){
      h+='<div class="a3d-awl-grp" data-awgrp="'+G.id+'"><div class="a3d-awl-grphd">'+bimEsc(G.name)+'</div>';
      G.an.forEach(function(a){
        var A=bimDgAn(a),on=bimAwShown(a),rs=bimAwRowState(a),run=!!D.runs[a];
        h+='<div class="a3d-awl-row'+(a===f?' focus':'')+(on&&a!==f?' add':'')+rs.cls+'" data-awrow="'+a+'">'+
          '<input type="checkbox" class="a3d-awl-tick" data-anzact="aw:tick:'+a+'"'+(on?' checked':'')+(run?'':' disabled')+' aria-label="'+bimEsc((on?'Hide ':'Draw ')+A.name+(on?'':' with the one in focus'))+'">'+
          '<i class="a3d-awl-sw" style="background:'+bimEsc(A.col)+'" aria-hidden="true"></i>'+
          '<button type="button" class="a3d-awl-nm" data-anzact="aw:focus:'+a+'"'+(run?'':' disabled')+' aria-pressed="'+(a===f)+'">'+bimEsc(A.name)+'</button>'+
          (rs.st?'<span class="a3d-awl-st">'+bimEsc(rs.st)+'</span>':'')+'</div>';
      });
      h+='</div>';
    });
    if(!D.last)h+='<div class="a3d-awl-empty">Nothing analysed yet: Analyze site, in Analyze, draws every analysis.</div>';
    return h+'</div>';
  }
  /* ---- the right: the one analysis ---- */
  function bimAwSec(t){return '<div class="a3d-awp-sec">'+bimEsc(t)+'</div>';}
  function bimAwBtn(act,label,pri,off){return '<button type="button" class="a3d-anzbtn'+(pri?' pri':'')+'" data-awact="'+bimEsc(act)+'"'+(off?' disabled title="'+bimEsc(off)+'"':'')+'>'+bimEsc(label)+'</button>';}
  function bimAwKeyHtml(rows){
    if(!rows||!rows.length)return '';
    return '<div class="a3d-awp-key">'+rows.map(function(r){
      var stl=(r.kind==='line'||r.kind==='dash')?'color:'+r.col:'background:'+r.col;
      if(r.tex)stl+=';'+bimDgTexCss(r.tex,r.ink);
      return '<span class="a3d-awp-keyi"><i class="'+(BIM_DG_KEYCLS[r.kind]||'k-fill')+'" style="'+bimEsc(stl)+'"></i>'+bimEsc(r.name)+'</span>';}).join('')+'</div>';
  }
  /* a chart where the app has one: the winds' rose, the sun's paths */
  function bimAwChart(a){
    var C=A3D.site&&A3D.site.climate,Hh=C&&C.hourly,st=bimSunSettings();
    try{
      if(a==='wind'&&Hh&&Hh.wind&&Hh.wind.year&&Hh.wind.year.n){
        var Wy=Hh.wind.year;
        return '<div class="a3d-awp-chart">'+bimClbRoseSvg(Wy,true,'Wind rose, '+Hh.year)+'</div>'+
          '<div class="a3d-awp-cap">'+bimEsc('From the '+BIM_CLIM_DIRS[Wy.prev]+' most often, '+bimClimFmt(Wy.mean,1)+' m/s on average; '+Hh.year+'\'s hours by direction and speed')+'</div>';
      }
      if((a==='sun'||a==='shadow')&&bimSunNum(st.lat)&&bimSunNum(st.lon)){
        var sn=bimClbSunSvg(st.lat,st.lon,bimSunNum(st.tz)?st.tz:Math.round(st.lon/15));
        return '<div class="a3d-awp-chart">'+sn.svg+'</div>'+
          '<div class="a3d-awp-cap">'+bimEsc('Looking up: the centre overhead, the rim the horizon; the sun at '+bimClimFmt(sn.days[0].alt,0)+'\u00b0 at midsummer noon and '+bimClimFmt(sn.days[2].alt,0)+'\u00b0 at midwinter')+'</div>';
      }
    }catch(eC){console.warn('[BIM] The analysis chart could not be drawn',eC);}
    return '';
  }
  /* the clock, for what moves */
  function bimAwClockHtml(a){
    var can=a==='traffic'?bimTrCanPlay():bimAnimFrame().any;
    if(!can)return '';
    return bimAwSec('Play')+'<div class="a3d-awp-acts">'+
      bimAwBtn('anim:play',A3D_ANIM.on?'Pause':(A3D_ANIM.paused?'Go on':'Play'),!A3D_ANIM.on)+
      bimAwBtn('anim:stop','Stop',false,A3D_ANIM.on||A3D_ANIM.paused?'':'Not playing')+'</div>';
  }
  function bimAwOverviewHtml(){
    var D=bimDgState(),R=A3D_SITERUN,st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),P=A3D.objs.filter(bimIsProperty),h,steps,n=0;
    BIM_DG_AN.forEach(function(A){if(D.runs[A.id])n++;});
    h='<div class="a3d-awp" data-awpanel="overview"><div class="a3d-awp-hd"><div><div class="a3d-awp-ttl">Overview</div><div class="a3d-awp-sub">Site analysis</div></div></div>'+
      '<p class="a3d-awp-about">'+bimEsc(D.last?'The site and its context. Pick an analysis on the left: it is drawn alone, with its key; tick others to draw them under it.':
        'Analyze site gets what is around the site from free open data and draws each analysis in the model.')+'</p>'+
      '<div class="a3d-awp-rows"><div class="a3d-awp-r"><span>Place</span><b>'+bimEsc(placed?bimSitePlaceText():'Not placed yet')+'</b></div>'+
      '<div class="a3d-awp-r"><span>Boundary</span><b>'+(P.length?bimEsc(P[0].name+', '+bimDispNum(bimPropertyGeometry(P[0]).area,1)+' m\u00b2'):'None yet')+'</b></div>'+
      (D.last?'<div class="a3d-awp-r"><span>Analysed</span><b>'+bimEsc(D.last.date)+'</b></div><div class="a3d-awp-r"><span>Analyses</span><b>'+n+' of '+BIM_DG_AN.length+'</b></div>':'')+'</div>';
    steps=R.steps.length?R.steps:((D.last&&D.last.steps)||[]);
    if(steps.length)h+=bimAwSec('What it fetched')+'<ol class="a3d-awp-steps">'+steps.map(function(s){
      return '<li class="'+(BIM_SITERUN_CLS[s.state]||'s-wait')+'"><span class="a3d-awp-dot" aria-hidden="true"></span><span class="a3d-awp-stn">'+bimEsc(s.name)+'</span><span class="a3d-awp-sts">'+bimEsc(BIM_SITERUN_WORD[s.state]||s.state)+'</span>'+
        (s.text?'<span class="a3d-awp-stt">'+bimEsc(s.text)+'</span>':'')+'</li>';}).join('')+'</ol>';
    h+='<div class="a3d-awp-acts">'+bimAwBtn('analyze',R.busy?'Analyzing ...':(D.last?'Analyze site again':'Analyze site'),true,R.busy?'Running':(placed?'':'Place the site first: Analyze, Site, Address'))+'</div>';
    return h+'</div>';
  }
  function bimAwPanelHtml(){
    var f=bimAwFocusNow();
    if(!f)return bimAwOverviewHtml();
    var A=bimDgAn(f),D=bimDgState(),R=D.runs[f],L=bimDgDiags(f),G=BIM_AW_GROUPS.filter(function(g){return g.an.indexOf(f)>=0;})[0],ed=L.filter(bimDgEdited).length,h,sx=R?bimDgStdText(f):'';
    h='<div class="a3d-awp" data-awpanel="'+f+'"><div class="a3d-awp-hd"><i class="a3d-awp-sw" style="background:'+bimEsc(A.col)+'" aria-hidden="true"></i>'+
      '<div><div class="a3d-awp-ttl">'+bimEsc(A.name)+'</div><div class="a3d-awp-sub">'+bimEsc((G?G.name:'Site analysis')+(R?' \u00b7 '+R.date:''))+'</div></div></div>'+
      '<p class="a3d-awp-about">'+bimEsc(BIM_AW_ABOUT[f]||'')+'</p>';
    if(f==='traffic'){
      var s=bimTrSettings(),mv=bimMvOf();
      h+=bimAwSec('Simulation')+'<div class="a3d-awp-acts">'+bimAwBtn('tr:sim:'+(s.on?'off':'on'),s.on?'Stop the simulation':'Simulate',!s.on,mv?'':bimMvWhyNot())+'</div>'+
        '<div class="a3d-awp-tr">'+bimTrCardHtml()+'</div>';
    }
    h+=bimAwClockHtml(f);
    h+=bimAwChart(f);
    if(R&&R.legend&&R.legend.length)h+=bimAwSec('Key')+bimAwKeyHtml(R.legend);
    h+=bimAwSec('What it shows')+'<div class="a3d-awp-rows"><div class="a3d-awp-r"><span>Drawn</span><b>'+bimEsc(R?bimSaN(L.length,'element')+(ed?', '+ed+' changed by you':''):'Not run yet')+'</b></div></div>';
    if(R&&R.note)h+='<p class="a3d-awp-note">'+bimEsc(R.note)+'</p>';
    if(R&&R.source)h+=bimAwSec('Source')+'<p class="a3d-awp-note">'+bimEsc(R.source)+'</p>';
    if(sx)h+='<p class="a3d-awp-note a3d-awp-std">'+bimEsc(sx)+'</p>';
    h+='<div class="a3d-awp-acts">'+bimAwBtn('dg:run:'+f,R?'Run again':'Run',false)+bimAwBtn('dg:select:'+f,'Select',false,L.length?'':'Nothing drawn yet')+
      bimAwBtn('dg:reset:'+f,'Reset',false,R?'':'Not run yet')+'</div>';
    return h+'</div>';
  }
  /* ---- what a press does, on the bar, the list or the panel ---- */
  function bimAwAct(v){
    v=String(v||'');
    var i=v.indexOf(':'),c=i<0?v:v.slice(0,i),a=i<0?'':v.slice(i+1),r=false;
    try{
      if(c==='leave')r=bimAwLeave();
      else if(c==='open')r=a?bimAwEnter(a):bimAwEnter();
      else if(c==='panel'){var rp=document.getElementById('a3d-right');if(rp){rp.classList.toggle('open');refreshProps();}r=!!rp;}
      else if(c==='focus')r=bimAwFocus(a||null);
      else if(c==='tick')r=bimAwTick(a);
      else if(c==='analyze'){bimSiteAnalyze('');r=true;}
      else if(c==='dg'){r=bimDgAct(a);bimAwRefresh();}
      else if(c==='tr'){r=bimTrAct(a);bimAwRefresh();}
      else if(c==='anim'){
        if(a==='play')r=bimAnimPlay(!A3D_ANIM.on);
        else if(a==='stop'){r=bimAnimStop();}
        bimAwRefresh();
      }
    }catch(eA){console.warn('[BIM] The site analysis',eA);a3dToast('That did not work - see the console');}
    return r;
  }
  /* Properties' body answers the panel's buttons; wired once */
  function bimAwWire(){
    if(A3D_AW.wired||!el.propsbody)return;
    A3D_AW.wired=true;
    el.propsbody.addEventListener('click',function(ev){
      if(!A3D_AW.on)return;
      var t=ev.target&&ev.target.closest?ev.target.closest('[data-awact],[data-anzact]'):null;
      if(!t||t.disabled||!el.propsbody.contains(t))return;
      if(t.hasAttribute('data-awact'))bimAwAct(t.getAttribute('data-awact'));
      else if(/^tr:/.test(t.getAttribute('data-anzact')))bimAwAct(t.getAttribute('data-anzact'));
    });
  }
  /* WebGPU's clear, in the view's background */
  function bimAwClear(){var b=bimAwBg();return {r:b[0],g:b[1],b:b[2],a:1};}
  /* Properties' title, the analysis's while it is the panel; and the bar, as an undo or a selection leaves things */
  function bimAwTitleSync(){
    var t=document.getElementById('a3d-rpttl');
    if(A3D_AW.on||document.getElementById('a3d-awbar'))bimAwBar();
    if(!t)return;
    var on=A3D_AW.on&&!objById(A3D.sel)&&!bimSelectedGrid();
    t.textContent=on?'Analysis':'Properties';
  }
