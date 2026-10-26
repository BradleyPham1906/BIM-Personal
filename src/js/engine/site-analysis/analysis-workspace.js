  /* ================= __acad3dV171b: the analysis workspace =================
     reference/research-analysis-workspace.md. The site analysis is a place one goes into and leaves, as archiMap's
     and Forma's are: a bar over the view with the analysis in focus and a cross; on the left the analyses in their
     groups, one in focus and others ticked under it; on the right, where Properties is while nothing is selected,
     the one analysis: what it shows, its settings, its chart, its key, what the run said and its source. The view
     goes quiet in the app's mode, light or dark: its ground, the map greyed and faded, the context in the mode's
     greys, so only the data keeps its colour. The focus and the ticks are the layers' visibility, one undo step
     each, so Layers and the sheets agree; they are the project's, kept with it.
     __acad3dV171c: one Analyze. The owner: "The analyze should be combined with the site analysis. It should not be
     two separate hubs." The workspace is Analyze itself, opened with its tab and left with it. On the left, the site
     and Analyze site, Overview, the ten categories with the analyses that answer each under it, and the model's
     own. On the right, what was picked: the overview, a category with its findings and its data, an analysis in the
     model with what it found, or one of the model's analyses with its settings and its buttons. */
  var BIM_AW_ABOUT={
    frame:'True north and rings every 100 m from the site: the bearing and the scale of everything else.',
    sun:'The sun\'s path over the site on the solstices and the equinoxes and on the day studied, with its hours; where it is now, its altitude and azimuth; and the temperature where it passes. They follow the place, the date and the time.',
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
  /* __acad3dV171c: the findings the data wrote that each analysis in the model draws; one with none says where its
     category's are */
  var BIM_AW_FINDS={frame:['location.place'],sun:['climate.sun'],shadow:['climate.sun'],wind:['climate.wind','climate.comfort'],
    contours:['landform.terrain'],slope:['landform.slope','landform.terrain'],flow:['water.drainage'],ponds:['water.rain'],flood:['water.flood','water.fema'],
    streets:['access.roads','access.frontage','access.connectivity'],cycling:['access.cycling'],transit:['access.transit','access.rail'],walk:['access.walk'],
    needs:['people.daily'],vehicles:['access.vehicles'],landuse:['location.landuse','people.landuse'],figure:['location.built','location.density'],
    green:['ecology.green','ecology.33300'],zoning:['legal.zoningaround']};
  /* the view's quiet tones in each mode; only the data keeps its colour */
  var BIM_AW_LOOK={
    light:{light:true,bg:'#f2f2ef',fade:0.35,grey:1,grid:'#e2e2de',ink:'#2a2e33',halo:'rgba(255,255,255,0.92)',
      ctx:{buildings:'#fbfbfa',roads:'#dcdcd8',water:'#bdd5ea',green:'#d4e7cd',trees:'#a9cd9f',rail:'#cbc6bf',airports:'#e4e4e0',power:'#d6d6d2',landuse:'#ebeae5',terrain:'#e9e8e3'},
      key:{bg:'rgba(255,255,255,0.95)',line:'rgba(0,0,0,0.12)',ink:'#1f2328',sub:'#6b7280'}},
    dark:{light:false,bg:'#17191c',fade:0.3,grey:1,grid:'#24282d',ink:'#e8edf2',halo:'rgba(10,12,15,0.86)',
      ctx:{buildings:'#4c525b',roads:'#363b42',water:'#22384d',green:'#25372a',trees:'#2f5236',rail:'#3d3a35',airports:'#2c3035',power:'#3a3e44',landuse:'#25282d',terrain:'#25292e'},
      key:{bg:'rgba(22,26,32,0.92)',line:'rgba(255,255,255,0.16)',ink:'#e8edf2',sub:'#9aa7b4'}}};
  /* __acad3dV171c: pick, what the right shows besides the focus ({k:'cat'|'card', id}); props, the model's
     Properties opened from a button; prev, the tab Analyze was opened from; over, the selection a pick was made over;
     pend, the panel's refresh held while one of its fields is typed in */
  var A3D_AW={on:false,wired:false,pick:null,props:false,prev:'browser',over:null,pend:false};
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
  /* the right panel read from its top when what it shows changes */
  function bimAwTop(){var b=el.propsbody;while(b&&b!==document.body){b.scrollTop=0;b=b.parentNode;if(b&&b.id==='a3d-right')break;}}
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
    bimAwBlur();
    A3D_AW.pick=null;A3D_AW.props=false;A3D_AW.over=bimAwSelKey();   /* __acad3dV171c: the right follows the focus */
    if(!A3D_AW.on)bimAwOpen();
    bimAwRefresh();
    bimAwTop();
    bimAwFold(false);   /* a drawer layout: the view, with the key on it */
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
  /* __acad3dV171c: a category, or one of the model's analyses, on the right; its row in the list in view */
  function bimAwCard(id){return bimAnzCards().filter(function(c){return c.id===id&&c.id.indexOf('dg')!==0;})[0]||null;}
  function bimAwPick(k,id){
    id=String(id||'');
    if(k==='cat'?!bimSaCat(id):!(k==='card'&&bimAwCard(id)))return false;
    bimAwBlur();
    A3D_AW.pick={k:k,id:id};A3D_AW.props=false;A3D_AW.over=bimAwSelKey();
    if(!A3D_AW.on)bimAwOpen();
    bimAwRefresh();
    bimAwTop();
    bimAwFold(true);   /* a drawer layout: the panel, to read */
    var r=document.querySelector('.a3d-analyze-wrap '+(k==='cat'?'[data-sacat="'+id+'"]':'[data-anzcard="'+id+'"]')),lp=document.getElementById('a3d-leftpanel'),a,b;
    if(r&&lp&&r.scrollIntoView){   /* its row in view, when it is not: a category at the top, its rows under it */
      a=r.getBoundingClientRect();b=lp.getBoundingClientRect();
      if(a.height&&(a.top<b.top+44||a.bottom>b.bottom)){try{r.scrollIntoView({block:k==='cat'?'start':'nearest'});}catch(eS){}}
    }
    return true;
  }
  /* the panel's field in use left before the panel changes, its words committed as a click elsewhere commits them */
  function bimAwBlur(){var a=document.activeElement;if(a&&a!==document.body&&el.propsbody&&el.propsbody.contains(a)&&a.blur)a.blur();}
  /* the selection, as a key: a pick shows its panel over what is selected, which stays selected for the buttons that
     act on it (Solar, the terrain's colours), until the selection changes */
  function bimAwSelKey(){var g=bimSelectedGrid();return String(A3D.sel||'')+'|'+(A3D.selSet||[]).join(',')+'|'+(g?g.id:'');}
  /* Properties is Analyze's panel: nothing selected, or a pick made since the selection */
  function bimAwOwns(){
    var none=!objById(A3D.sel)&&!bimSelectedGrid();
    if(none)A3D_AW.over=null;
    return A3D_AW.on&&(none||A3D_AW.over===bimAwSelKey());
  }
  /* a drawer layout (a phone, a tablet upright): the drawer shut so the view shows, and the panel open when what
     was picked is to be read */
  function bimAwFold(panel){
    if(!bimShellOverlay())return false;
    var sh=document.getElementById('a3d-shell'),rp=document.getElementById('a3d-right');
    if(sh&&!sh.classList.contains('collapsed'))bimShellDrawer(false);
    if(rp)rp.classList.toggle('open',!!panel);
    return true;
  }
  /* ---- in and out: Analyze's tab ---- */
  function bimAwOpen(){
    A3D_AW.on=true;
    document.body.classList.add('a3d-aw');
    var sh=document.getElementById('a3d-shell');
    if(sh&&sh.getAttribute('data-tab')!=='analyze')bimShellSetTab('analyze');
    bimAwWire();
  }
  /* __acad3dV171c: the tab opened opens it; another tab leaves it */
  function bimAwTab(t,was){
    if(t==='analyze'){
      if(was&&was!=='analyze')A3D_AW.prev=was;
      if(!A3D_AW.on){bimAwOpen();bimAwRefresh();}
    }else if(A3D_AW.on)bimAwLeave();
  }
  function bimAwEnter(focus){
    if(focus!==undefined)return bimAwFocus(focus);
    bimAwOpen();
    bimAwRefresh();
    return true;
  }
  /* out of it, to the tab it was opened from, the drawer as it was; what was drawn stays drawn */
  function bimAwLeave(){
    if(!A3D_AW.on)return false;
    A3D_AW.on=false;A3D_AW.props=false;
    A3D_SUNX.lat=null;A3D_SUNX.lon=null;A3D_SUNX.date=null;A3D_SUNX.time=null;   /* __acad3dV171d: a place tried ends with Analyze */
    document.body.classList.remove('a3d-aw');
    var sh=document.getElementById('a3d-shell'),shut;
    if(sh&&sh.getAttribute('data-tab')==='analyze'){
      shut=sh.classList.contains('collapsed');
      bimShellSetTab(A3D_AW.prev&&A3D_AW.prev!=='analyze'?A3D_AW.prev:'browser');
      if(shut){sh.classList.add('collapsed');bimShellDockW();}
    }
    bimAwBar();
    refreshProps();
    paint();
    return true;
  }
  /* Analyze site, as it ends, inside its one undo step: the first time the site and its context, and the overview;
     again, what was in focus and ticked, drawn again */
  function bimAwAfterRun(){
    var S=bimAwState(),held=bimUndoHold;
    if(!bimDgState().last){S.focus=null;S.add=[];A3D_AW.pick=null;}
    bimUndoHold=true;
    try{bimAwApply(false);}finally{bimUndoHold=held;}
    bimAwOpen();
    bimAwFold(false);
    bimAwBar();
  }
  /* TRAFFIC: in focus, inside the step the command took */
  function bimAwTraffic(){
    var S=bimAwState(),held=bimUndoHold;
    S.focus='traffic';S.add=S.add.filter(function(x){return x!=='traffic';});
    A3D_AW.pick=null;A3D_AW.props=false;
    bimUndoHold=true;
    try{bimAwApply(false);}finally{bimUndoHold=held;}
    bimAwOpen();
    bimAwFold(false);
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
    bimRenderInto(b,'<div class="a3d-awbar-row"><span class="a3d-awbar-k">Analyze</span><span class="a3d-awbar-sep" aria-hidden="true"></span>'+
      '<span class="a3d-awbar-t" data-awbart="1">'+bimEsc(A?A.name:'Overview')+'</span>'+
      (S.add.filter(bimAwShown).length?'<span class="a3d-awbar-n">+ '+S.add.filter(bimAwShown).length+'</span>':'')+
      '<button type="button" class="a3d-awbar-d" data-awact="panel" title="What is picked, to read" aria-label="What is picked, to read">Details</button>'+
      '<button type="button" class="a3d-awbar-x" data-awact="leave" title="Leave Analyze" aria-label="Leave Analyze">'+
      '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8"/></svg></button></div>'+
      (ch?'<div class="a3d-awchips" role="group" aria-label="The analyses">'+ch+'</div>':''));
    var on=b.querySelector('.a3d-awchip.on'),row=b.querySelector('.a3d-awchips');   /* a phone's row: the one in focus in sight */
    if(on&&row&&row.clientWidth&&(on.offsetLeft<row.scrollLeft||on.offsetLeft+on.offsetWidth>row.scrollLeft+row.clientWidth))row.scrollLeft=Math.max(0,on.offsetLeft-12);
    return b;
  }
  /* ---- the left: the site, Overview, the ten categories with their analyses, the model's ---- */
  function bimAwRowState(a){
    var D=bimDgState(),R=D.runs[a],n=R?bimDgDiags(a).length:0;
    if(!R)return {cls:' none',st:'Not run'};
    var SC=bimDgStdChanged(a);
    if(SC.run.length||SC.data.length)return {cls:' stale',st:'Out of date'};
    if(!n&&a!=='traffic')return {cls:' none',st:'Nothing'};
    return {cls:'',st:''};
  }
  function bimAwCatCounts(id){var F=bimSaOf(id),r=0;F.forEach(function(f){if(f.cls==='redflag')r++;});return {n:F.length,r:r};}
  function bimAwCatSub(k){return k.n?bimSaN(k.n,'finding')+(k.r?', '+bimSaN(k.r,'red flag'):''):'No findings yet';}
  /* where Analyze site starts: the site's place (or its address), its boundary, the button and how the run goes */
  function bimAwSiteHtml(){
    var st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),D=bimDgState(),R=A3D_SITERUN,P=A3D.objs.filter(bimIsProperty),h,dn,now;
    h='<div class="a3d-awl-site" data-anzsec="site"><div class="a3d-awl-place">'+bimEsc(placed?bimSitePlaceText():'Not placed yet')+'</div>';
    if(!placed)h+='<input type="text" id="a3d-saaddr" class="a3d-awl-addr" data-saaddr="1" maxlength="200" enterkeyhint="search" autocomplete="off" placeholder="A street address or a place" aria-label="The site\'s address">';
    h+='<div class="a3d-awl-bd">'+(P.length?bimEsc(P[0].name+', '+bimDispNum(bimPropertyGeometry(P[0]).area,1)+' m\u00b2'):
      'No boundary yet: <button type="button" class="a3d-awl-lk" data-saact="cmd:propertyshape">from a shape</button> or <button type="button" class="a3d-awl-lk" data-saact="cmd:propertyline">from bearings</button>')+'</div>';
    dn=R.steps.filter(function(s){return s.state!=='wait'&&s.state!=='busy';}).length;
    now=R.steps.filter(function(s){return s.state==='busy';}).map(function(s){return s.name;});
    h+='<button type="button" class="a3d-anzbtn pri a3d-awl-go" data-saact="analyze"'+(R.busy?' disabled':'')+'>'+(R.busy?'Analyzing ...':(D.last?'Analyze site again':'Analyze site'))+'</button>'+
      '<div class="a3d-awl-run">'+bimEsc(R.busy?dn+' of '+R.steps.length+' done'+(now.length?': '+now.join(', ')+' ...':''):
        (D.last?'Last run '+D.last.date+'. One undo step.':'Free open data around the site, every analysis drawn in the model. One undo step.'))+'</div></div>';
    return h;
  }
  /* a row: an analysis in the model (a tick, its colour, its name), or one of the others (its name, its state) */
  function bimAwRowHtml(c,f,pk){
    if(c.id.indexOf('dg')===0){
      var a=c.id.slice(2),A=bimDgAn(a),on=bimAwShown(a),rs=bimAwRowState(a),run=!!bimDgState().runs[a];
      return '<div class="a3d-awl-row'+(a===f?' focus':'')+(on&&a!==f?' add':'')+(!pk&&a===f?' pick':'')+rs.cls+'" data-awrow="'+a+'" data-anzcard="'+c.id+'">'+
        '<input type="checkbox" class="a3d-awl-tick" data-anzact="aw:tick:'+a+'"'+(on?' checked':'')+(run?'':' disabled')+' aria-label="'+bimEsc((on?'Hide ':'Draw ')+A.name+(on?'':' with the one in focus'))+'">'+
        '<i class="a3d-awl-sw" style="background:'+bimEsc(A.col)+'" aria-hidden="true"></i>'+
        '<button type="button" class="a3d-awl-nm" data-anzact="aw:focus:'+a+'"'+(run?'':' disabled')+' aria-pressed="'+(a===f)+'">'+bimEsc(A.name)+'</button>'+
        (rs.st?'<span class="a3d-awl-st">'+bimEsc(rs.st)+'</span>':'')+'</div>';
    }
    var p=!!(pk&&pk.k==='card'&&pk.id===c.id);
    return '<div class="a3d-awl-row a3d-awl-tool'+(p?' pick':'')+'" data-anzcard="'+c.id+'">'+
      '<i class="a3d-awl-dot" aria-hidden="true"></i>'+
      '<button type="button" class="a3d-awl-nm" data-anzact="aw:card:'+c.id+'" aria-pressed="'+p+'">'+bimEsc(c.title)+'</button>'+
      (c.state?'<span class="a3d-anzstate a3d-anzstate-'+c.state+'">'+bimAnzStateText(c.state)+'</span>':'')+'</div>';
  }
  function bimAwListHtml(){
    var f=bimAwFocusNow(),pk=A3D_AW.pick,C=bimAnzCards(),h,M;
    h='<div class="a3d-anz a3d-awl" data-awlist="1">'+
      '<div class="a3d-awl-hd"><span class="a3d-awl-ttl">Analyze</span><span class="a3d-anzcount">'+bimEsc(bimAnzCountText(C))+'</span></div>'+
      '<input type="search" class="a3d-anzsearch" data-anzsearch="1" placeholder="Search analyses and findings" aria-label="Search Analyze" autocomplete="off" value="'+bimEsc(A3D_ANZ.q||'')+'">'+
      bimAwSiteHtml()+
      '<button type="button" class="a3d-awl-row a3d-awl-ov'+(!pk&&!f?' pick':'')+'" data-anzact="aw:focus:" aria-pressed="'+(!pk&&!f)+'"><span class="a3d-awl-nm">Overview</span><span class="a3d-awl-st">The site and what was found</span></button>';
    BIM_SA_CATS.forEach(function(c,i){
      var T=C.filter(function(x){return x.group===c.id;}),k=bimAwCatCounts(c.id),p=!!(pk&&pk.k==='cat'&&pk.id===c.id);
      h+='<div class="a3d-awl-grp" data-sacat="'+c.id+'">'+
        '<button type="button" class="a3d-awl-cat'+(p?' pick':'')+'" data-anzact="aw:cat:'+c.id+'" aria-pressed="'+p+'" title="'+bimEsc(c.q)+'">'+
        '<span class="a3d-awl-no">'+(i+1)+'</span><span class="a3d-awl-cn">'+bimEsc(c.n)+'</span>'+
        (k.r?'<span class="a3d-awl-rf" title="'+bimEsc(bimSaN(k.r,'red flag'))+'">'+k.r+'</span>':'')+
        '<span class="a3d-awl-fn" title="'+bimEsc(bimAwCatSub(k))+'">'+(k.n||'')+'</span></button>'+
        T.map(function(x){return bimAwRowHtml(x,f,pk);}).join('')+'</div>';
    });
    M=BIM_ANZ_MODEL.map(function(id){return C.filter(function(c){return c.id===id;})[0];}).filter(function(c){return !!c;});
    h+='<div class="a3d-awl-grp" data-anzgrp="model"><div class="a3d-awl-grphd">Model</div>'+M.map(function(x){return bimAwRowHtml(x,f,pk);}).join('')+'</div>';
    return h+'<div class="a3d-anzempty" hidden>Nothing matches</div></div>';
  }
  /* a row's words for the search: its name, what it says it shows, what it reports now, its settings, its buttons */
  function bimAwRowWords(x,grp){
    if(!x)return '';
    var a=x.id.indexOf('dg')===0?x.id.slice(2):'';
    return x.title+' '+x.status+' '+(a?(BIM_AW_ABOUT[a]||''):'')+' '+String(x.extra||'').replace(/<[^>]*>/g,' ')+' '+
      (x.acts||[]).map(function(b){return b.label;}).join(' ')+' '+grp;
  }
  /* ---- the right: what is picked ---- */
  function bimAwSec(t){return '<div class="a3d-awp-sec">'+bimEsc(t)+'</div>';}
  function bimAwBtn(act,label,pri,off){return '<button type="button" class="a3d-anzbtn'+(pri?' pri':'')+'" data-awact="'+bimEsc(act)+'"'+(off?' disabled title="'+bimEsc(off)+'"':'')+'>'+bimEsc(label)+'</button>';}
  function bimAwHd(sw,no,ttl,sub){
    return '<div class="a3d-awp-hd">'+(no?'<span class="a3d-awp-no" aria-hidden="true">'+no+'</span>':(sw?'<i class="a3d-awp-sw" style="background:'+bimEsc(sw)+'" aria-hidden="true"></i>':''))+
      '<div><div class="a3d-awp-ttl">'+bimEsc(ttl)+'</div><div class="a3d-awp-sub">'+bimEsc(sub)+'</div></div></div>';
  }
  /* the category an analysis answers, a link to it */
  function bimAwInHtml(cardId){
    var g=BIM_ANZ_GROUP_OF[cardId],i=-1,k;
    for(k=0;k<BIM_SA_CATS.length;k++)if(BIM_SA_CATS[k].id===g)i=k;
    return i<0?'':'<p class="a3d-awp-in">Answers <button type="button" class="a3d-awl-lk" data-awact="cat:'+g+'">'+(i+1)+'. '+bimEsc(BIM_SA_CATS[i].n)+'</button></p>';
  }
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
      if(a==='sun')return bimSunChartsHtml();   /* __acad3dV171d: the turning points, the two diagrams, the temperature */
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
      bimAwBtn('anim:stop','Stop',false,A3D_ANIM.on||A3D_ANIM.paused?'':'Not playing')+'</div>'+
      (a==='sun'||a==='shadow'?bimSunModeHtml():'');   /* __acad3dV171d: through the day or the year */
  }
  /* the overview: the site, the red flags first, every category's findings counted, what the run fetched */
  function bimAwOverviewHtml(){
    var D=bimDgState(),R=A3D_SITERUN,st=bimSunSettings(),placed=bimSunNum(st.lat)&&bimSunNum(st.lon),P=A3D.objs.filter(bimIsProperty),h,steps,n=0,
      F=bimSaShown(),RF=F.filter(function(f){return f.cls==='redflag';});
    BIM_DG_AN.forEach(function(A){if(D.runs[A.id])n++;});
    h='<div class="a3d-awp a3d-sa" data-awpanel="overview">'+bimAwHd(null,0,'Overview','Analyze')+
      '<p class="a3d-awp-about">'+bimEsc(D.last?'What Analyze site found around the site, by category. Pick a category on the left to read its findings, or an analysis to draw it alone with its key; tick others to draw them under it.':
        'Analyze site gets what is around the site from free open data, draws each analysis in the model and writes what it finds, by category.')+'</p>'+
      '<div class="a3d-awp-rows"><div class="a3d-awp-r"><span>Place</span><b>'+bimEsc(placed?bimSitePlaceText():'Not placed yet')+'</b></div>'+
      '<div class="a3d-awp-r"><span>Boundary</span><b>'+(P.length?bimEsc(P[0].name+', '+bimDispNum(bimPropertyGeometry(P[0]).area,1)+' m\u00b2'):'None yet')+'</b></div>'+
      (D.last?'<div class="a3d-awp-r"><span>Analysed</span><b>'+bimEsc(D.last.date)+'</b></div><div class="a3d-awp-r"><span>Analyses</span><b>'+n+' of '+BIM_DG_AN.length+'</b></div>':'')+
      '<div class="a3d-awp-r"><span>Findings</span><b>'+bimEsc(F.length?bimSaN(F.length,'finding')+(RF.length?', '+bimSaN(RF.length,'red flag'):''):'None yet')+'</b></div></div>';
    if(RF.length)h+=bimAwSec('Red flags')+'<div class="a3d-awp-flags">'+RF.map(function(f){
      return '<button type="button" class="a3d-awp-flag" data-awact="cat:'+bimEsc(f.cat)+'"><span class="a3d-safno">'+bimSaNumber(f)+'</span><span>'+bimEsc(f.title)+(f.value?': '+bimEsc(f.value):'')+'</span></button>';}).join('')+'</div>';
    h+=bimAwSec('The ten categories')+'<div class="a3d-awp-cats">'+BIM_SA_CATS.map(function(c,i){
      var k=bimAwCatCounts(c.id);
      return '<button type="button" class="a3d-awp-cat" data-awact="cat:'+c.id+'"><span class="a3d-awp-catno">'+(i+1)+'</span><span class="a3d-awp-catn">'+bimEsc(c.n)+'</span>'+
        '<span class="a3d-awp-catf'+(k.r?' rf':'')+'">'+bimEsc(bimAwCatSub(k))+'</span></button>';}).join('')+'</div>';
    steps=R.steps.length?R.steps:((D.last&&D.last.steps)||[]);
    if(steps.length)h+=bimAwSec('What it fetched')+'<ol class="a3d-awp-steps" data-sasteps="1">'+steps.map(function(s){
      return '<li class="'+(BIM_SITERUN_CLS[s.state]||'s-wait')+'" data-sastep="'+bimEsc(s.id)+'"><span class="a3d-awp-dot" aria-hidden="true"></span><span class="a3d-awp-stn">'+bimEsc(s.name)+'</span><span class="a3d-awp-sts">'+bimEsc(BIM_SITERUN_WORD[s.state]||s.state)+'</span>'+
        (s.text?'<span class="a3d-awp-stt">'+bimEsc(s.text)+'</span>':'')+'</li>';}).join('')+'</ol>';
    h+='<div class="a3d-awp-acts"><button type="button" class="a3d-anzbtn pri" data-saact="analyze"'+(R.busy?' disabled':'')+'>'+(R.busy?'Analyzing ...':(D.last?'Analyze site again':'Analyze site'))+'</button>'+
      (D.last?'<button type="button" class="a3d-anzbtn" data-saact="dglegend" aria-pressed="'+(!D.legendOff)+'">'+(D.legendOff?'Show the key on the view':'Hide the key on the view')+'</button>':'')+'</div>';
    return h+'</div>';
  }
  /* a category: its question, what was found, the analyses that answer it, its data */
  function bimAwCatHtml(id){
    var c=bimSaCat(id),i=BIM_SA_CATS.indexOf(c),F=bimSaOf(id),T=bimAnzCards().filter(function(x){return x.group===id;}),D=bimDgState(),dat=BIM_SA_DATA[id],see=BIM_SA_SEE[id],h,j;
    h='<div class="a3d-awp a3d-sa" data-awpanel="cat:'+id+'">'+bimAwHd(null,i+1,c.n,bimAwCatSub(bimAwCatCounts(id)))+
      '<p class="a3d-awp-about">'+bimEsc(c.q)+'</p>';
    h+=bimAwSec('What was found')+(F.length?F.map(bimSaFindingHtml).join(''):'<p class="a3d-awp-note">None yet: Analyze site writes them from the data.</p>');
    if(T.length)h+=bimAwSec('Analyses')+'<div class="a3d-awp-ans">'+T.map(function(x){
      var dg=x.id.indexOf('dg')===0,a=dg?x.id.slice(2):'',A=dg?bimDgAn(a):null,st=dg?(bimAwRowState(a).st||bimSaN(bimDgDiags(a).length,'element')):bimAnzStateText(x.state);
      return '<button type="button" class="a3d-awp-an" data-awact="'+(dg?'focus:'+a:'card:'+x.id)+'"'+(dg&&!D.runs[a]?' disabled title="Not run yet: Analyze site draws it"':'')+'>'+
        '<i'+(A?' style="background:'+bimEsc(A.col)+'"':' class="o"')+' aria-hidden="true"></i><span class="a3d-awp-ann">'+bimEsc(x.title)+'</span><span class="a3d-awp-anst">'+bimEsc(st)+'</span></button>';}).join('')+'</div>';
    if(dat)h+=dat();
    if(see){for(j=0;j<BIM_SA_CATS.length;j++)if(BIM_SA_CATS[j].id===see[0])break;
      h+='<div class="a3d-salink">'+bimEsc(see[1])+' <button type="button" class="a3d-anzbtn" data-saact="goto:'+see[0]+'">'+(j+1)+'. '+bimEsc(BIM_SA_CATS[j].n)+'</button></div>';}
    return h+'</div>';
  }
  /* one of the model's analyses, or one Analyze site does not draw: its state, its settings, its buttons */
  function bimAwCardHtml(c){
    var acts=c.acts.slice(),ly=bimAnzLayerAct(c.id),g=bimSaCat(c.group);
    if(ly)acts.push(ly);
    return '<div class="a3d-awp a3d-sa" data-awpanel="card:'+c.id+'">'+bimAwHd(null,0,c.title,(g?g.n:'Model')+(c.state?' \u00b7 '+bimAnzStateText(c.state):''))+
      '<p class="a3d-awp-about">'+bimEsc(c.status)+'</p>'+(c.extra||'')+
      (acts.length?'<div class="a3d-awp-acts">'+acts.map(bimAnzBtn).join('')+'</div>':'')+bimAwInHtml(c.id)+'</div>';
  }
  /* an analysis in the model: V171b's panel, and what it found */
  function bimAwAnHtml(f){
    var A=bimDgAn(f),D=bimDgState(),R=D.runs[f],L=bimDgDiags(f),g=bimSaCat(BIM_ANZ_GROUP_OF['dg'+f]),ed=L.filter(bimDgEdited).length,h,sx=R?bimDgStdText(f):'',
      FK=BIM_AW_FINDS[f]||[],FF=bimSaShown().filter(function(x){return FK.indexOf(x.auto)>=0;});
    h='<div class="a3d-awp a3d-sa" data-awpanel="'+f+'">'+bimAwHd(A.col,0,A.name,(g?g.n:'Analyze')+(R?' \u00b7 '+R.date:''))+
      '<p class="a3d-awp-about">'+bimEsc(BIM_AW_ABOUT[f]||'')+'</p>';
    if(f==='sun')h+=bimSunPanelHtml();   /* __acad3dV171d: the sun now, and the sliders */
    if(f==='traffic'){
      var s=bimTrSettings(),mv=bimMvOf();
      h+=bimAwSec('Simulation')+'<div class="a3d-awp-acts">'+bimAwBtn('tr:sim:'+(s.on?'off':'on'),s.on?'Stop the simulation':'Simulate',!s.on,mv?'':bimMvWhyNot())+'</div>'+
        '<div class="a3d-awp-tr">'+bimTrCardHtml()+'</div>';
    }
    h+=bimAwClockHtml(f);
    h+=bimAwChart(f);
    if(R&&R.legend&&R.legend.length)h+=bimAwSec('Key')+bimAwKeyHtml(R.legend);
    h+=bimAwSec('What it found')+(FF.length?FF.map(bimSaFindingHtml).join(''):
      '<p class="a3d-awp-note">'+bimEsc(R?'It writes no finding of its own; its category\'s are under '+(g?g.n:'its category')+'.':'Nothing yet: Analyze site writes the findings.')+'</p>');
    h+=bimAwSec('What it shows')+'<div class="a3d-awp-rows"><div class="a3d-awp-r"><span>Drawn</span><b>'+bimEsc(R?bimSaN(L.length,'element')+(ed?', '+ed+' changed by you':''):'Not run yet')+'</b></div></div>';
    var SC=R?bimDgStdChanged(f):null;   /* __acad3dV167: a standard it used changed since */
    if(SC&&(SC.run.length||SC.data.length))h+='<p class="a3d-awp-note a3d-awp-stale">'+bimEsc(bimDgStaleText(SC))+'</p>';
    if(R&&R.note)h+='<p class="a3d-awp-note">'+bimEsc(R.note)+'</p>';
    if(R&&R.source)h+=bimAwSec('Source')+'<p class="a3d-awp-note">'+bimEsc(R.source)+'</p>';
    if(sx)h+='<p class="a3d-awp-note a3d-awp-std" data-dgstd="'+f+'">'+bimEsc(sx)+'</p>';
    h+='<div class="a3d-awp-acts">'+bimAwBtn('dg:run:'+f,R?'Run again':'Run',false)+bimAwBtn('dg:select:'+f,'Select',false,L.length?'':'Nothing drawn yet')+
      bimAwBtn('dg:reset:'+f,'Reset',false,R?'':'Not run yet')+'</div>'+bimAwInHtml('dg'+f);
    return h+'</div>';
  }
  /* the panel again; not under one of its fields being typed in, whose words would go -- then when it is left
     (V162's rule for Analyze's list, kept for its panel) */
  function bimAwRender(force){
    var a=document.activeElement,b=el.propsbody;
    if(!force&&a&&b.contains(a)&&a.closest&&a.closest('.a3d-awp')&&(a.tagName==='TEXTAREA'||(a.tagName==='INPUT'&&!/^(checkbox|radio|file|range|color|button)$/.test(a.type)))){A3D_AW.pend=true;return false;}
    A3D_AW.pend=false;
    bimRenderInto(b,bimAwPanelHtml());
    return true;
  }
  function bimAwPanelHtml(){
    if(A3D_AW.props)return '<div class="a3d-awp-backrow"><button type="button" class="a3d-awl-lk" data-awact="back">Back to the analysis</button></div>'+bimModelPropsHtml();
    var pk=A3D_AW.pick,c,f;
    if(pk&&pk.k==='cat'&&bimSaCat(pk.id))return bimAwCatHtml(pk.id);
    if(pk&&pk.k==='card'&&(c=bimAwCard(pk.id)))return bimAwCardHtml(c);
    f=bimAwFocusNow();
    return f?bimAwAnHtml(f):bimAwOverviewHtml();
  }
  /* ---- what a press does, on the bar, the list or the panel ---- */
  function bimAwAct(v){
    v=String(v||'');
    var i=v.indexOf(':'),c=i<0?v:v.slice(0,i),a=i<0?'':v.slice(i+1),r=false;
    try{
      if(c==='leave')r=bimAwLeave();
      else if(c==='panel'){var rp=document.getElementById('a3d-right');if(rp){rp.classList.toggle('open');refreshProps();}r=!!rp;}
      else if(c==='focus')r=bimAwFocus(a||null);
      else if(c==='tick')r=bimAwTick(a);
      else if(c==='cat'||c==='card')r=bimAwPick(c,a);
      else if(c==='back'){bimAwBlur();A3D_AW.props=false;bimAwRefresh();bimAwTop();r=true;}
      else if(c==='dg'){r=bimDgAct(a);bimAwRefresh();}
      else if(c==='tr'){r=bimTrAct(a);bimAwRefresh();}
      else if(c==='sun')r=bimSunAct(a);   /* __acad3dV171d */
      else if(c==='anim'){
        if(a==='play')r=bimAnimPlay(!A3D_ANIM.on);
        else if(a==='stop'){r=bimAnimStop();}
        bimAwRefresh();
      }
    }catch(eA){console.warn('[BIM] Analyze',eA);a3dToast('That did not work - see the console');}
    return r;
  }
  /* Properties' body answers the panel's buttons and fields; wired once */
  function bimAwWire(){
    if(A3D_AW.wired||!el.propsbody)return;
    A3D_AW.wired=true;
    el.propsbody.addEventListener('click',function(ev){
      if(!A3D_AW.on)return;
      var t=ev.target&&ev.target.closest?ev.target.closest('[data-awact],[data-anzact],[data-saact]'):null,k;
      if(!t||t.disabled||!el.propsbody.contains(t)||!t.closest('.a3d-awp,.a3d-awp-backrow'))return;
      try{
        if(t.hasAttribute('data-awact'))bimAwAct(t.getAttribute('data-awact'));
        else if(t.hasAttribute('data-anzact')){k=t.getAttribute('data-anzact');if(/^tr:/.test(k))bimAwAct(k);else{bimAnzAct(k);bimAwRefresh();}}
        else{bimSaAct(t.getAttribute('data-saact'));bimAwRefresh();}
      }catch(eW){console.warn('[BIM] Analyze',eW);a3dToast('That did not work - see the console');}
    });
    el.propsbody.addEventListener('change',function(ev){
      var e=ev.target,k;
      if(!A3D_AW.on||!e||!e.getAttribute||!e.closest||!e.closest('.a3d-awp'))return;
      try{
        /* a field's change is its words committed, taken or refused: the panel shows the model again at once */
        if((k=e.getAttribute('data-znf'))){bimZnSet(k,e.value);if(bimAwOwns())bimAwRender(true);}   /* __acad3dV160: the zoning, in Legal */
        else if((k=e.getAttribute('data-anzload'))){updateLevel(A3D.activeLevel,k,e.value);if(bimAwOwns())bimAwRender(true);}   /* __acad3dV166b: the floor loads, in Frame analysis */
        else if((k=e.getAttribute('data-sunsl'))){   /* __acad3dV171d: a slider let go; the same slider in the hand again */
          bimSunSlide(k,e.value,true);
          setTimeout(function(){var s=el.propsbody.querySelector('[data-sunsl="'+k+'"]');if(s&&document.activeElement!==s)s.focus();},0);
        }
      }catch(eF){console.warn('[BIM] Analyze setting failed',eF);a3dToast('That setting could not be changed - see the console');}
    },true);   /* in the capture: V118's refresh after every change, the panel's last handler, would put the model's value back first */
    el.propsbody.addEventListener('focusout',function(){if(A3D_AW.pend)setTimeout(function(){if(A3D_AW.pend)refreshProps();},0);});   /* the refresh held for a field, as it is left */
    el.propsbody.addEventListener('input',function(ev){   /* __acad3dV171d: a slider moving: the view and the numbers follow it */
      var e=ev.target,k;
      if(!A3D_AW.on||!e||!e.getAttribute||!(k=e.getAttribute('data-sunsl')))return;
      try{bimSunSlide(k,e.value,false);}catch(eS){console.warn('[BIM] The sun\'s slider',eS);}
    });
  }
  /* WebGPU's clear, in the view's background */
  function bimAwClear(){var b=bimAwBg();return {r:b[0],g:b[1],b:b[2],a:1};}
  /* Properties' title, the analysis's while it is the panel; and the bar, as an undo or a selection leaves things */
  function bimAwTitleSync(){
    var t=document.getElementById('a3d-rpttl');
    if(A3D_AW.on||document.getElementById('a3d-awbar'))bimAwBar();
    if(!t)return;
    t.textContent=bimAwOwns()&&!A3D_AW.props?'Analysis':'Properties';
  }
