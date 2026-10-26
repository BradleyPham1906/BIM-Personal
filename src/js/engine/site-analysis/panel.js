  /* ---- the panel ---- */
  /* __acad3dV164: a finding the data wrote, to read: its number, what it says, its class and source */
  function bimSaFindingHtml(f){
    var cl=bimSaPair(BIM_SA_CLS,f.cls);
    return '<div class="a3d-safind c-'+bimEsc(f.cls)+'" data-safind="'+bimEsc(f.id)+'">'+
      '<div class="a3d-safhd"><span class="a3d-safno">'+bimSaNumber(f)+'</span><span class="a3d-saftt">'+bimEsc(f.title)+'</span></div>'+
      (f.value?'<div class="a3d-safv">'+bimEsc(f.value)+'</div>':'')+
      '<div class="a3d-safm"><b class="k-'+bimEsc(f.cls)+'">'+bimEsc(cl)+(f.cls!=='neutral'?', '+bimSaPair(BIM_SA_SEV,String(f.sev)).toLowerCase():'')+'</b> \u00b7 '+
      bimEsc(f.source||'no source given')+' \u00b7 '+bimEsc(f.date)+'</div>'+
      (bimSaStdText(f)?'<div class="a3d-safstd" data-safstd="'+bimEsc(f.auto)+'">'+bimEsc(bimSaStdText(f))+'</div>':'')+'</div>';   /* __acad3dV167 */
  }
  /* __acad3dV162: what each category holds besides its findings. Risk and People share the data
     Climate and Access fetch, and say where it is. */
  var BIM_SA_DATA={location:function(){return bimSaCtxHtml();},legal:function(){return bimZnSaHtml();},climate:function(){return bimClbSaHtml();},access:function(){return bimAccSaHtml();}};
  var BIM_SA_SEE={risk:['climate','Air quality and earthquakes come with the climate data'],people:['access','The census and the daily needs within a walk come with the access data']};
  /* __acad3dV162: Location's data: where the site is, and its context (V133) */
  function bimSaCtxHtml(){
    var c=A3D.site&&A3D.site.context&&A3D.site.context.last,st=bimSunSettings(),at='';
    if(bimSunNum(st.lat)&&bimSunNum(st.lon))at=Math.abs(st.lat).toFixed(4)+'° '+(st.lat<0?'S':'N')+', '+Math.abs(st.lon).toFixed(4)+'° '+(st.lon<0?'W':'E');
    return '<div class="a3d-clsec" data-ctxsec="1"><div class="a3d-sasechd">Site context</div>'+
      '<p class="a3d-clsum">'+(at?bimEsc('The site: '+at+'.'):'The site is not placed yet: give its latitude and longitude, or find its address, in Location.')+' '+
      (c?bimEsc('Context of '+c.date+': '+bimCtxCountsText(c.counts)+'.'):'The buildings, roads, water and trees around it, from OpenStreetMap, and the terrain: free, no account.')+'</p>'+
      '<div class="a3d-saacts"><button type="button" class="a3d-anzbtn'+(c?'':' pri')+'" data-saact="cmd:context">'+(c?'Get the context again':'Get the context')+'</button>'+
      '<button type="button" class="a3d-anzbtn" data-anzact="open:Location">Location</button></div></div>';
  }
  /* the site's part of Analyze's list: its buttons, and Enter in the address runs it. __acad3dV171c: a category's
     buttons and the zoning's fields are on the right (bimAwWire) */
  function bimSaWire(w){
    w.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-saact]'):null;
      if(!b||b.disabled)return;
      try{bimSaAct(b.getAttribute('data-saact'));}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV164: Enter in the address runs it */
    w.addEventListener('keydown',function(ev){
      var e=ev.target;
      if(ev.key!=='Enter'||!e||!e.getAttribute||!e.getAttribute('data-saaddr'))return;
      ev.preventDefault();
      try{bimSaAct('analyze');}catch(eS){console.warn('[BIM] Site analysis',eS);a3dToast('That did not work - see the console');}
    });
  }
  function bimSaAct(a){
    var k=String(a||''),i=k.indexOf(':'),v=i<0?'':k.slice(i+1),c=i<0?k:k.slice(0,i);
    if(c==='goto')return bimSaGoto(v);   /* __acad3dV162 */
    if(c==='climget')return bimClimFetch();   /* __acad3dV159 */
    if(c==='climboard')return bimBoardShow('climate');   /* __acad3dV162: a page of the set */
    if(c==='znedit'){A3D_ZN.edit=!A3D_ZN.edit;bimSaRefresh(true);return true;}   /* __acad3dV160 */
    if(c==='znbuild')return bimZnBuild();
    if(c==='znboard')return bimBoardShow('zoning');
    if(c==='accget')return bimAccFetch();   /* __acad3dV161 */
    if(c==='accboard')return bimBoardShow('access');
    if(c==='acclayer')return bimResultLayerAdd('walk');
    if(c==='znlayer')return bimZnFromLayer(true);
    if(c==='znclear')return bimZnRemoveEnvelope();
    if(c==='znstepadd')return bimZnStepAdd(v);
    if(c==='znstepdel'){var di=v.indexOf('.');return bimZnStepDel(v.slice(0,di),+v.slice(di+1));}
    if(c==='analyze'){   /* __acad3dV164 */
      var ai=document.querySelector('.a3d-analyze-wrap [data-saaddr]');
      return bimSiteAnalyze(ai?ai.value:'');
    }
    if(c==='dglegend'){var D=bimDgState();D.legendOff=!D.legendOff;saveSoon();paint();bimSaRefresh(true);return true;}
    if(c==='cmd'&&/^(propertyshape|propertyline|context)$/.test(v))return window.__a3dRunCmd(v);
    return false;
  }
  /* __acad3dV162: the site analysis is in Analyze's one list; its refresh is that list's. __acad3dV171c: and the right's,
     which shows a category's data as it arrives, and the run's steps */
  function bimSaRefresh(force){var r=bimAnalyzeRefresh(force);if(A3D_AW.on)refreshProps();return r;}
  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the
     title block and site record that the sheet title block already prints. Level, Layer and
     Appearance are the three switches that change what the drawing shows, and each one already
     had a control elsewhere -- gathering them here does not add state, it stops a user hunting
     for them. Statistics are counted from the model, never stored. */
  function bimModelPropsHtml(){
    var h='',i,lv,ly;
    bimEnsureBuildings();
    var rows='';
    rows+=bimPropRow('Project','<input type="text" data-propmodel="project" value="'+
      bimEsc(A3D.titleBlock.project||'')+'" placeholder="Untitled project">');
    rows+=bimPropRow('Client','<input type="text" data-propmodel="client" value="'+
      bimEsc(A3D.titleBlock.client||'')+'">');
    var loc='';   /* __acad3dV141: where the site is, in its own group on the Site tab */
    loc+=bimPropRow('True North (deg)','<input type="number" step="any" data-propmodel="truenorth" value="'+bimTrueNorthDeg()+'">');   /* __acad3dV103 */
    var sunS=bimSunSettings();   /* __acad3dV107: where the site is, and the moment studied */
    loc+=bimPropRow('Latitude (deg N)','<input type="number" step="any" min="-90" max="90" data-propmodel="sunlat" value="'+(bimSunNum(sunS.lat)?sunS.lat:'')+'" placeholder="not set" title="Site latitude in degrees, north positive">');
    loc+=bimPropRow('Longitude (deg E)','<input type="number" step="any" min="-180" max="180" data-propmodel="sunlon" value="'+(bimSunNum(sunS.lon)?sunS.lon:'')+'" placeholder="not set" title="Site longitude in degrees, east positive: west is negative">');
    loc+=bimPropRow('UTC Offset (h)','<input type="number" step="any" min="-12" max="14" data-propmodel="suntz" value="'+(bimSunNum(sunS.tz)?sunS.tz:'')+'" placeholder="not set" title="Standard time\'s hours from UTC: -5 for New York">');
    loc+=bimSunZoneRows();   /* __acad3dV171d: the zone, and daylight saving */
    loc+=bimPropRow('Sun Date','<input type="date" data-propmodel="sundate" value="'+bimEsc(sunS.date)+'">');
    loc+=bimPropRow('Sun Time','<input type="time" data-propmodel="suntime" value="'+bimEsc(sunS.time)+'">');
    loc+=bimPropText('Sun',bimSunText(bimSunNow(true)));
    rows+=bimPropRow('Site','<input type="text" data-propmodel="site" value="'+
      bimEsc(A3D.site.name||'')+'">');
    h+=bimDataFeatureHtml();   /* __acad3dV134: the data clicked on the plan, first */
    h+=bimPropTabsHtml();   /* __acad3dV141: Project | Site | View */
    h+=bimPTab('project',bimPropGroup('Identity Data',rows));
    h+=bimPTab('site',bimPropGroup('Location',loc));   /* __acad3dV141 */
    h+=bimPTab('site',bimPropGroup('Map',bimMapPropsHtml()));   /* __acad3dV132 */
    h+=bimPTab('site',bimPropGroup('Site Context',bimCtxModelHtml()));   /* __acad3dV133 */
    h+=bimPTab('site',bimPropGroup('Data Layers',bimDataModelHtml()));   /* __acad3dV134 */
    h+=bimPTab('site',bimPropGroup('Standards',bimStdPropsHtml()));   /* __acad3dV167 */

    var vrows='',lvlOpts='';
    for(i=0;i<A3D.levels.length;i++){
      lv=A3D.levels[i];
      lvlOpts+='<option value="'+bimEsc(lv.id)+'"'+(lv.id===A3D.activeLevel?' selected':'')+'>'+
        bimEsc(lv.name)+'</option>';
    }
    vrows+=bimPropRow('Active Level','<select data-propmodel="level">'+lvlOpts+'</select>');
    /* __acad3dV121: the same tree as every other Layer field; this one listed the layers for itself */
    vrows+=bimPropRow('Active Layer','<select data-propmodel="layer">'+bimLayerOptionsHtml(A3D.activeLayer)+'</select>');
    vrows+=bimLensHtml();   /* __acad3dV136: the lens */
    vrows+=bimPropRow('Appearance','<select data-propmodel="present">'+
      '<option value="0"'+(A3D.presentMode?'':' selected')+'>Technical</option>'+
      '<option value="1"'+(A3D.presentMode?' selected':'')+'>Presentation</option></select>');
    /* Read-only and honest: the engine works in metres throughout and there is no unit
       conversion layer, so this states the fact rather than offering a switch that would not
       convert anything. */
    vrows+=bimPropText('Units','Meters');
    /* __acad3dV84: "A3D.flat ? 'Plan' : '3D'" is the flat-is-not-plan confusion a third
       time -- an elevation and a section are flat too, and both of them reported "Plan" here.
       The active view is what the user is in, so the active view is what this says. */
    vrows+=bimPropText('View',(typeof A3D_VIEW!=='undefined'&&A3D_VIEW&&A3D_VIEW.name)
      ?A3D_VIEW.name:(A3D.flat?'Plan':'3D'));
    h+=bimPTab('view',bimPropGroup('View',vrows));   /* __acad3dV141 */

    var nRooms=0,nWalls=0,nOpen=0;
    for(i=0;i<A3D.objs.length;i++){
      var ob=A3D.objs[i];
      if(ob.t==='room')nRooms++;
      else if(ob.t==='opening')nOpen++;
      else if(ob.bim&&ob.bim.type==='wall')nWalls++;
    }
    var srows='';
    srows+=bimPropText('Objects',A3D.objs.length);
    srows+=bimPropText('Walls',nWalls);
    srows+=bimPropText('Openings',nOpen);
    srows+=bimPropText('Rooms',nRooms);
    srows+=bimPropText('Levels',A3D.levels.length);
    srows+=bimPropText('Layers',A3D.layers.length);
    srows+=bimPropText('Sheets',A3D.sheets.length);
    srows+=bimPropRow('Version','<span class="a3d-pstatic">'+bimVersionHtml()+'</span>');   /* __acad3dV142 */
    srows+=bimPropRow('Graphics','<span class="a3d-pstatic" data-graphics="1">'+bimEsc(bimGraphicsLabel())+'</span>');   /* __acad3dV153 */
    if(A3D_BENCH&&!A3D_BENCH.running)srows+=bimPropRow('Benchmark','<span class="a3d-pstatic" data-bench="1">'+bimEsc(bimBenchmarkText(A3D_BENCH))+'</span>');   /* __acad3dV155 */
    /* __acad3dV166b: the active level's floor loads and the frame's settings are in Analyze's Frame
       analysis, the project's areas by usage in its Areas by usage. The usages are the project's own --
       the rooms, floors and masses take them, Colour by and the schedules read them -- so they are here. */
    h+=bimPTab('project',bimPropGroup('Usages',bimUsageLibraryHtml()));   /* __acad3dV131 */
    h+=bimPTab('project',bimPropGroup('Statistics',srows));
    h+=bimPTab('project',bimPropGroup('History',bimHistHtml()));   /* __acad3dV146 */
    return h;
  }
  /* __acad3dV118: the one way to re-render a panel the user may be working in.

     Assigning innerHTML replaces every element in a panel, the focused one included, and the focus
     falls to the page -- where the next key belongs to the model. With the wall's Type dropdown
     focused, ArrowDown stepped the type, the change re-rendered Properties, and the second ArrowDown
     moved the wall a metre. A Tab in Model Properties landed nowhere; a click from one field into
     another was lost, the element clicked being gone before the mouse came up.

     Here the new markup is parsed off the document and the live panel is brought into line with it,
     element by element. An element that is still there keeps its identity -- its focus, its caret,
     an open dropdown -- and only what differs is touched. Elements are matched by what they are: an
     id or their data-* attributes, or, for a container with neither, those of the first element
     inside it that has them; anything else by position. The result is the markup, attribute for
     attribute, and every field shows the value the markup gives it, as innerHTML did. If the focused
     element had to be moved or rebuilt, the focus and the caret are put back on it by the same key. */
  function bimOwnKey(n){
    if(!n||n.nodeType!==1)return null;
    if(n.id)return n.nodeName+'#'+n.id;
    var a=n.attributes,i,k=[];
    for(i=0;i<a.length;i++)if(a[i].name.indexOf('data-')===0)k.push(a[i].name+'='+a[i].value);
    return k.length?(n.nodeName+'['+k.sort().join('|')+']'):null;
  }
  function bimMorphKey(n){
    var k=bimOwnKey(n),c;
    if(k!==null||!n||n.nodeType!==1)return k;
    for(c=n.firstElementChild;c;c=c.nextElementSibling){
      k=bimMorphKey(c);
      if(k!==null)return n.nodeName+'>'+k;
    }
    return null;
  }
  function bimMorphKids(live,next){
    var pool={},need={},c,k,cur,nn,nx,m;
    for(c=live.firstChild;c;c=c.nextSibling){
      k=bimMorphKey(c);
      if(k!==null)(pool[k]=pool[k]||[]).push(c);
    }
    for(c=next.firstChild;c;c=c.nextSibling){k=bimMorphKey(c);if(k!==null)need[k]=(need[k]||0)+1;}
    cur=live.firstChild;
    for(nn=next.firstChild;nn;nn=nx){
      nx=nn.nextSibling;
      /* a keyed element that nothing still to come wants is gone: remove it here, rather than move
         everything after it past it -- a moved element loses the focus */
      while(cur&&(k=bimMorphKey(cur))!==null&&!need[k]){m=cur.nextSibling;live.removeChild(cur);cur=m;}
      k=bimMorphKey(nn);m=null;
      if(k!==null){need[k]--;if(pool[k]&&pool[k].length)m=pool[k].shift();}
      else if(cur&&bimMorphKey(cur)===null&&cur.nodeType===nn.nodeType&&cur.nodeName===nn.nodeName)m=cur;
      if(!m){live.insertBefore(nn,cur);continue;}   /* new: it leaves the parsed markup for the panel */
      /* unkeyed nodes between here and the match go, rather than the match being moved past them */
      while(cur&&cur!==m&&bimMorphKey(cur)===null){c=cur.nextSibling;live.removeChild(cur);cur=c;}
      if(m===cur)cur=cur.nextSibling;
      else live.insertBefore(m,cur);                 /* a true reorder: kept, and moved into its place */
      bimMorphNode(m,nn);
    }
    while(cur){nx=cur.nextSibling;live.removeChild(cur);cur=nx;}
  }
  function bimMorphNode(a,b){
    if(a.nodeType!==1){if(a.nodeValue!==b.nodeValue)a.nodeValue=b.nodeValue;return;}
    var i,n,aa=a.attributes,ba=b.attributes;
    for(i=aa.length-1;i>=0;i--){n=aa[i].name;if(!b.hasAttribute(n))a.removeAttribute(n);}
    for(i=0;i<ba.length;i++){n=ba[i].name;if(a.getAttribute(n)!==ba[i].value)a.setAttribute(n,ba[i].value);}
    bimMorphKids(a,b);
    /* the markup's value, as innerHTML gave it -- a rejected edit shows the model's value again */
    if(a.nodeName==='INPUT'){
      if(a.type==='checkbox'||a.type==='radio'){if(a.checked!==b.checked)a.checked=b.checked;}
      else if(a.type!=='file'&&a.value!==b.value)a.value=b.value;
    }else if(a.nodeName==='TEXTAREA'){
      if(a.value!==b.value)a.value=b.value;
    }else if(a.nodeName==='SELECT'){
      for(i=0;i<a.options.length&&i<b.options.length;i++)
        if(a.options[i].selected!==b.options[i].selected)a.options[i].selected=b.options[i].selected;
    }
  }
  function bimFindByKey(host,k){
    if(k===null)return null;
    var all=host.getElementsByTagName('*'),i;
    for(i=0;i<all.length;i++)if(bimOwnKey(all[i])===k)return all[i];
    return null;
  }
  function bimRenderInto(host,html){
    if(!host)return;
    var a=document.activeElement,keep=null,t,s;
    if(a&&a!==document.body&&host.contains(a)){
      keep={el:a,key:bimOwnKey(a),v:a.value,s:null,e:null,d:null};
      try{if(typeof a.selectionStart==='number'){keep.s=a.selectionStart;keep.e=a.selectionEnd;keep.d=a.selectionDirection;}}
      catch(eS){}
    }
    try{
      t=document.createElement('template');
      t.innerHTML=html;
      bimMorphKids(host,t.content);
    }catch(eM){
      console.warn('[BIM] A panel update fell back to a full redraw.',eM);
      a3dToast('A panel was redrawn in full; the focus may have moved');
      host.innerHTML=html;
    }
    if(!keep)return;
    s=keep.el;
    if(!host.contains(s))s=bimFindByKey(host,keep.key);
    if(!s||document.activeElement===s)return;
    try{s.focus({preventScroll:true});}catch(eF){}
    if(keep.s!==null&&s.value===keep.v){try{s.setSelectionRange(keep.s,keep.e,keep.d||'none');}catch(eR){}}
  }
  window.__a3dRenderInto=bimRenderInto;   /* the helper's own contract is tested directly, reorders included */
  function refreshProps(){
    /* __acad3dV67: the status bar's hint names the selection, so it has to re-render on EVERY
       selection-change path. refreshTree() calls this, but several call sites (property edits,
       programmatic selection, the constraint picker) call refreshProps alone -- syncing from
       refreshTree only would leave the bar naming an object that is no longer selected. */
    bimSyncStatusHint();
    bimAnalyzeRefresh();   /* __acad3dV141; __acad3dV162: the site analysis with it */
    bimAwTitleSync();   /* __acad3dV171b */
    if(!el.propsbody)return;
    if(bimAwOwns()){bimAwRender();return;}   /* __acad3dV171b: the one analysis; __acad3dV171c: or what was picked */
    var o=objById(A3D.sel);
    var gP=o?null:bimSelectedGrid();   /* __acad3dV98 */
    if(gP){bimRenderInto(el.propsbody,bimGridPropsHtml(gP));return;}   /* __acad3dV118 */
    if(!o){
      /* __acad3dV73: with nothing selected the inspector describes the MODEL, the way the
         reference tool does. "No object selected" wastes the panel exactly when a user is
         orienting themselves. Every field below is backed by state that already exists and is
         already persisted -- no new settings were invented to fill the space. */
      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */
      return;
    }
    if(bimIsDiag(o)){bimRenderInto(el.propsbody,bimDgPropsHtml(o));return;}   /* __acad3dV164: a site analysis element */
    var h='';
    // ---- type selector header, as in Revit ----
    h+='<div class="a3d-ptypehd">'+
       '<div class="a3d-ptypeic">'+(a3drIcon('bim:'+((o.bim&&o.bim.type)||o.t))||a3drIcon('box'))+'</div>'+
       '<div class="a3d-ptypetx"><div class="a3d-ptypename">'+bimEsc(o.name)+'</div>'+
       '<div class="a3d-ptypesub">'+bimEsc(bimObjTypeLabel(o))+'</div></div>'+
       '<button class="a3d-pedit" data-propf="edittype" title="Type properties">Edit Type</button>'+
       '</div>';

    // ---- Constraints ----
    var lvlName=bimLevelName((o.bim&&o.bim.levelId)||o.levelId)||'-';
    var cons='';
    if(o.bim&&o.bim.type==='wall'&&o.bim.centerline){
      bimEnsureTypes();
      cons+=bimPropRow('Type','<select data-propf="walltype">'+
        A3D.types.wall.map(function(x){return '<option value="'+x.id+'"'+(o.bim.typeId===x.id?' selected':'')+'>'+bimEsc(x.name)+'</option>';}).join('')+
        '</select>');
    }
    /* __acad3dV102: a Type selector for every typed category (walls keep their own row above) */
    if(o.bim&&TYPE_CATS[o.bim.type]&&o.bim.type!=='wall'){
      bimEnsureTypes();
      var cur=bimEnsureObjType(o);
      cons+=bimPropRow('Type','<select data-propf="objtype">'+bimTypeOptionsHtml(o.bim.type,cur&&cur.id)+'</select>');
    }
    cons+=bimPropText('Level',lvlName);
    /* __acad3dV77: Revit's own name for this field, and Revit's own home for Location Line --
       it constrains where the wall sits relative to its centreline, which is a constraint, not
       a dimension. Dimensions is left holding dimensions. */
    var pbO=bimPrimBase(o);   /* __acad3dV123: a primitive's base, not its middle */
    cons+=bimPropLen('Base Offset',pbO!==null?pbO:((o.pos&&o.pos[1])||0),'posy');
    if(o.bim&&o.bim.type==='wall'&&o.bim.centerline){
      cons+=bimPropRow('Location Line','<select data-propf="align">'+
        ['center','left','right'].map(function(a){return '<option value="'+a+'"'+(o.bim.align===a?' selected':'')+'>'+(a==='center'?'Wall Centerline':(a==='left'?'Finish Face: Exterior':'Finish Face: Interior'))+'</option>';}).join('')+'</select>');
    }
    if(o.bim&&o.bim.baseY!==undefined)cons+=bimPropLenText('Base Elevation',o.bim.baseY);
    h+=bimPropGroup('Constraints',cons);
    if(o.asset&&o.asset.k)h+=bimEntPropsHtml(o);   /* __acad3dV169: the asset's sizes and their standards */

    // ---- Graphics ----
    var gfx='';
    gfx+=bimPropRow('Layer','<select data-propf="layer">'+bimLayerOptionsHtml(o.layer||A3D.activeLayer)+'</select>');
    h+=bimPropGroup('Graphics',gfx);

    /* __acad3dV59: Phase 51 graphic override. Instance-level only here -- the shared TYPE default
       is edited via "Edit Type" above, exactly like thickness/width already are. Two independent
       sub-groups (Technical / Presentation) rather than a mode toggle, so both are visible and
       editable at once without an extra click, matching how Constraints/Dimensions are already
       always-both-visible rather than tabbed. */
    var gModes=[['technical','Technical'],['presentation','Presentation']],gmi;
    for(gmi=0;gmi<gModes.length;gmi++){
      var gm=gModes[gmi][0],gLabel=gModes[gmi][1];
      var resolved=bimResolveGraphics(o,gm);
      var ovSet=(o.graphicsOverride&&o.graphicsOverride[gm])?o.graphicsOverride[gm]:{};
      var grows='';
      var gReset=function(key){return ovSet[key]!==undefined?' <button data-propgfxreset="'+gm+':'+key+'" title="Reset to type default">↶</button>':'';};
      grows+=bimPropRow('Line Weight (mm)','<input type="number" step="0.05" min="0.05" data-propgfx="'+gm+':lineWeight" value="'+resolved.lineWeight+'">'+gReset('lineWeight'));
      grows+=bimPropRow('Line Color','<input type="color" data-propgfx="'+gm+':lineColor" value="'+resolved.lineColor+'">'+gReset('lineColor'));
      grows+=bimPropRow('Fill (Poché)','<input type="checkbox" data-propgfxfillon="'+gm+'"'+(resolved.fill!=='none'?' checked':'')+
        '> <input type="color" data-propgfx="'+gm+':fill" value="'+(resolved.fill!=='none'?resolved.fill:'#cccccc')+'"'+(resolved.fill==='none'?' disabled':'')+'>'+gReset('fill'));
      grows+=bimPropRow('Pattern','<select data-propgfx="'+gm+':pattern">'+BIM_HATCH_PATTERNS.map(function(p){
        return '<option value="'+p+'"'+(resolved.pattern===p?' selected':'')+'>'+bimEsc(bimPatternLabel(p))+'</option>';
      }).join('')+'</select>'+gReset('pattern'));
      /* __acad3dV63: the two controls that make the hatch usable. Both are hidden while the
         pattern is 'none', so an object with no hatch shows exactly the rows it showed before
         Phase 53 rather than two permanently inert fields. */
      if(bimPatternDraws(resolved.pattern)){
        grows+=bimPropRow('Pattern Color','<input type="color" data-propgfx="'+gm+':patternColor" value="'+resolved.patternColor+'">'+gReset('patternColor'));
        if(resolved.pattern!=='solid')
          grows+=bimPropRow('Pattern Scale','<input type="number" step="0.1" min="0.1" max="8" data-propgfx="'+gm+':patternScale" value="'+resolved.patternScale+'">'+gReset('patternScale'));
      }
      grows+=bimPropRow('Opacity','<input type="range" min="0" max="1" step="0.05" data-propgfx="'+gm+':opacity" value="'+resolved.opacity+'"> '+Math.round(resolved.opacity*100)+'%'+gReset('opacity'));
      grows+=bimPropRow('Shadow','<input type="checkbox" data-propgfx="'+gm+':shadow"'+(resolved.shadow?' checked':'')+'>'+gReset('shadow'));
      h+=bimPropGroup('Graphics — '+gLabel,grows);
    }

    /* ---- __acad3dV69: Materials and Finishes (Revit's own group name for this). One select
       assigns a card; everything under it is DERIVED and read-only, because those figures come
       from the shared library and the model's own geometry -- editing them here would be
       editing a copy. Volume and Mass show an em dash when the solid's mesh does not bound a
       closed volume rather than a number that would be wrong. ---- */
    var matRows='',matCards=bimMaterialCards(),mci,curMat=bimMaterialOf(o);
    if(matCards.length&&o.t==='solid'){
      var matOpts='<option value=""'+(o.materialName?'':' selected')+'>\u2014 none \u2014</option>';
      for(mci=0;mci<matCards.length;mci++){
        matOpts+='<option value="'+bimEsc(matCards[mci].name)+'"'+
          (o.materialName===matCards[mci].name?' selected':'')+'>'+
          bimEsc(matCards[mci].name)+' \u00b7 '+bimEsc(matCards[mci].kind)+'</option>';
      }
      matRows+=bimPropRow('Material','<select data-propmat="1">'+matOpts+'</select>');
      if(curMat){
        matRows+=bimPropText('Density (kg/m\u00b3)',bimDispNum(curMat.density,0));
        /* __acad3dV77: a structural parameter the assigned card does not carry is OMITTED,
           not rendered as a blank. The shipped library defines density for every material
           and stiffness for none, so these two rows were permanently empty -- and a row
           that is always empty reads as a value the app failed to compute rather than as a
           property the material has not been given. Revit hides parameters that do not
           apply for the same reason. A card that does carry them shows them. */
        if(isFinite(curMat.youngsModulus))
          matRows+=bimPropText('Young\u2019s Modulus (GPa)',bimDispNum(curMat.youngsModulus,1));
        if(isFinite(curMat.poissonRatio))
          matRows+=bimPropText('Poisson\u2019s Ratio',bimDispNum(curMat.poissonRatio,2));
      }
      var mVol=bimObjVolume(o),mMass=bimObjMass(o);
      // bimDispNum returns an em dash for null, which is the same 'no closed volume' signal
      // this row carried before -- now produced in one place instead of at every call site.
      matRows+=bimPropText('Volume (m\u00b3)',bimDispNum(mVol,3));
      matRows+=bimPropText('Mass (kg)',bimDispNum(mMass,1));
      h+=bimPropGroup('Materials and Finishes',matRows);
    }

    // ---- Dimensions (type-specific, editable where the model supports it) ----
    var dims='';
    if(o.bim&&o.bim.type==='wall'){
      if(o.bim.centerline){
        // __acad3dV77: Location Line moved up to Constraints; the rest now share one format.
        dims+=bimPropLen('Thickness',o.bim.thickness,'thickness',0.01);
        dims+=bimPropLen('Height',o.bim.height,'height',0.01);
        dims+=bimPropLenText('Length',bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges));
      }else{
        dims+=bimPropText('Geometry','Imported \u2014 not parametric');
      }
    }else if(o.bim&&o.bim.type==='floor'){
      dims+=bimPropLen('Thickness',o.bim.thickness,'fthickness',0.01);
      if(o.bim.profile)dims+=bimPropText('Area (m\u00b2)',bimDispNum(bimPolyArea(o.bim.profile),2));
    }else if(o.bim&&o.bim.type==='ceiling'){
      dims+=bimPropLenText('Height Above Level',o.bim.heightAbove);
      dims+=bimPropLenText('Thickness',o.bim.thickness);
      if(o.bim.profile)dims+=bimPropText('Area (m\u00b2)',bimDispNum(bimPolyArea(o.bim.profile),2));
      dims+=bimPropText('Follows',bimFollowsText(o));   /* __acad3dV99 */
    }else if(bimIsProperty(o)){   /* __acad3dV103: the survey, its closure, its setbacks */
      var pg=bimPropertyGeometry(o),li;
      dims+=bimPropText('Point of beginning',o.start[0].toFixed(3)+', '+o.start[1].toFixed(3));
      for(li=0;li<o.legs.length;li++)
        dims+=bimPropText('Leg '+(li+1),bimFormatBearing(o.legs[li].az)+'  '+o.legs[li].d.toFixed(3)+' m');
      dims+=bimPropText('Closure',pg.misclosure<0.0005?'Closes':('Misclosure '+pg.misclosure.toFixed(3)+' m (1:'+Math.round(pg.precision)+')'));
      dims+=bimPropText('Perimeter (m)',bimDispNum(pg.perimeter,3));
      dims+=bimPropText('Area (m\u00b2)',bimDispNum(pg.area,2));
      dims+=bimPropText('Area (ha)',bimDispNum(pg.area/10000,4));
      dims+=bimPropRow('Survey','<button class="a3d-pedit" data-propact="propedit">Edit legs...</button>');
      var sbr=bimPropRow('All sides (m)','<input type="number" step="any" min="0" data-propsetback="all" value="">');
      for(li=0;li<o.legs.length;li++)
        sbr+=bimPropRow('Side '+(li+1)+' (m)','<input type="number" step="any" min="0" data-propsetback="'+li+'" value="'+((o.setbacks&&o.setbacks[li])||0)+'">');
      if(pg.setback&&pg.setback.error)sbr+=bimPropText('Buildable area',pg.setback.error);
      else if(pg.setback)sbr+=bimPropText('Buildable area (m\u00b2)',bimDispNum(bimPolyArea(pg.setback.ring),2));
      var vio=bimSetbackViolations(o);
      sbr+=bimPropText('Violations',vio.list.length?vio.list.map(function(v){return v.name;}).join(', '):'None');
      h+=bimPropGroup('Setbacks',sbr);
    }else if(bimIsFooting(o)){   /* __acad3dV102: sizes come from the type (Edit Type) */
      var fHost=bimFootingHostOf(o);
      dims+=bimPropText('Sits under',fHost?fHost.name:'Nothing - placed on its own');
      dims+=bimPropLenText('Width',o.bim.width);
      if(o.bim.type==='footing')dims+=bimPropLenText('Length',o.bim.length);
      else dims+=bimPropLenText('Length',bimFootingLength(o));
      dims+=bimPropLenText('Thickness',o.bim.thickness);
      dims+=bimPropText('Concrete (m\u00b3)',bimDispNum(bimFootingVolume(o),3));
    }else if(o.bim&&o.bim.type==='column'){
      dims+=bimPropLen('Width',o.bim.width,'cwidth',0.01);
      dims+=bimPropLen('Depth',o.bim.depth,'cdepth',0.01);
      dims+=bimPropLen('Height',o.bim.height,'cheight',0.01);
      /* __acad3dV81: orientation is real state now, so it is editable here as well as by the
         rotate ring -- a number is the only way to set an exact angle. */
      dims+=bimPropRow('Rotation (\u00b0)','<input type="number" step="any" data-propf="crot" '+
        'value="'+bimDispNum((o.bim.rotation||0)*180/Math.PI,2)+'">');
    }else if(o.bim&&o.bim.type==='roof'){
      var rs=o.bim.style||'shed';
      dims+=bimPropRow('Roof Style','<select data-propf="rstyle">'+
        '<option value="shed"'+(rs==='shed'?' selected':'')+'>Shed (single plane)</option>'+
        '<option value="hip"'+(rs==='hip'?' selected':'')+'>Hip</option>'+
        '<option value="gable"'+(rs==='gable'?' selected':'')+'>Gable</option></select>');
      dims+=bimPropRow('Slope','<input type="number" step="any" data-propf="rpitch" value="'+o.bim.pitch+'">');
      dims+=bimPropLen('Thickness',o.bim.thickness,'rthick',0.01);
    }else if(o.bim&&o.bim.type==='stair'){
      dims+=bimPropText('Risers',o.bim.numSteps);
      dims+=bimPropLenText('Riser Height',o.bim.riserH);
      dims+=bimPropLenText('Tread Depth',o.bim.treadD);
      dims+=bimPropLenText('Total Rise',o.bim.totalRise);
    }else if(o.t==='room'){
      dims+=bimPropText('Area (m\u00b2)',bimDispNum(o.area,2));
      dims+=bimPropText('Perimeter Points',o.pts.length);
      dims+=bimPropText('Follows',bimFollowsText(o));   /* __acad3dV99 */
    }else if(o.t==='dim'){
      var dk=bimDimKind(o);
      if(dk==='linear')dims+=bimPropLenText('Length',o.length);
      else if(dk==='angular')dims+=bimPropText('Angle (\u00b0)',bimDispNum(o.degrees,2));
      else if(dk==='radius'||dk==='diameter')dims+=bimPropLenText(dk==='diameter'?'Diameter':'Radius',o.value);
    }else if(o.t==='note'){
      /* __acad3dV82: width and height are SCREEN pixels, not metres -- an annotation is meant to
         stay the same readable size at every zoom, which is why the app's text labels already
         behave this way. They are deliberately NOT bimPropLen rows, which would convert them
         through the project's length units and make them mean something they do not. */
      dims+=bimPropRow('Width (px)','<input type="number" step="1" min="8" data-propf="nw" value="'+(o.w||0)+'">');
      if(o.kind!=='line')
        dims+=bimPropRow('Height (px)','<input type="number" step="1" min="0" data-propf="nh" value="'+(o.h||0)+'">');
      dims+=bimPropText('Kind',bimNoteDef(o.kind).label);
    }else if(bimIsHatch(o)){                    /* __acad3dV96 */
      dims+=bimPropText('Pattern',bimPatternLabel(o.pattern));
      dims+=bimPropText('Angle',(o.patternAngle||0).toFixed(1)+' deg');
      dims+=bimPropText('Scale',(o.patternScale||1).toFixed(2));
      dims+=bimPropText('Area',bimHatchArea(o).toFixed(3)+' m2');
      dims+=bimPropText('Boundary points',o.pts.length);
      dims+=bimPropText('Follows',bimFollowsText(o));   /* __acad3dV99 */
    }else if(bimIsCline(o)){                    /* __acad3dV94 */
      dims+=bimPropText('Through',o.p[0].toFixed(3)+', '+o.p[1].toFixed(3));
      dims+=bimPropText('Angle',(Math.atan2(o.dir[1],o.dir[0])*180/Math.PI).toFixed(3)+' deg');
      dims+=bimPropText('Extent',o.ray?'One direction (ray)':'Both directions (xline)');
    }else if(bimIsPoint(o)){                    /* __acad3dV93 */
      dims+=bimPropText('X',o.pts[0][0].toFixed(3));
      dims+=bimPropText('Y',o.pts[0][1].toFixed(3));
      if(o.spot){var spe=bimSpotElev(o);dims+=bimPropText('Spot Elevation',spe.h===null?'not over a surface':bimDispNum(spe.h,3)+' m on '+spe.name);}   /* __acad3dV145 */
    }else if(o.t==='terrain'){   /* __acad3dV108 */
      var ttin=null,trg,tsrc=o.source;
      try{ttin=bimTerrainTin(o);}catch(eT){console.warn('[BIM] terrain',eT);}
      dims+=bimPropText('Survey Points',o.survey.length);
      if(!ttin){dims+=bimPropText('Triangles','could not be triangulated');}else{
      trg=bimTerrainRange(ttin);
      dims+=bimPropText('Triangles',ttin.tris.length);
      dims+=bimPropText('Elevations',trg[0].toFixed(3)+' to '+trg[1].toFixed(3)+' m');
      dims+=bimPropRow('Contour Interval (m)','<input type="number" step="any" min="0" data-propf="terrint" value="'+(isFinite(parseFloat(o.interval))?o.interval:'')+'" placeholder="'+bimTerrainInterval(o,ttin)+' from the relief">');
      }
      if(tsrc&&tsrc.base)dims+=bimPropText('Source',tsrc.format+', '+tsrc.units+'; base N '+tsrc.base.n+', E '+tsrc.base.e+', Z '+tsrc.base.z);
    }else if(!o.mesh&&o.prm&&TYPES[o.t]){
      /* __acad3dV123: a primitive's parameters, lengths in the project's unit -- a box's size was
         shown nowhere once it was placed. Named as a pushed face reads them out. */
      var tpP=TYPES[o.t],ppP=mergePrm(o.t,o.prm),pi;
      for(pi=0;pi<tpP.prm.length;pi++){
        var pn=tpP.prm[pi][0],pl=bimPrmLabel(o.t,pn);
        if(pn==='Angle')dims+=bimPropRow('Angle (\u00b0)','<input type="number" step="any" min="1" max="360" data-propf="prm:Angle" value="'+bimDispNum(ppP.Angle,2)+'">');
        else if(pn==='Polygon')dims+=bimPropRow('Sides','<input type="number" step="1" min="3" data-propf="prm:Polygon" value="'+Math.round(ppP.Polygon)+'">');
        else dims+=bimPropLen(pl,ppP[pn]*SCALE,'prm:'+pn,0);
      }
    }else if(o.t==='sketch'){
      dims+=bimPropText('Points',o.pts.length);
      dims+=bimPropText('Closed',o.closed!==false?'Yes':'No');
      if(o.closed!==false){   /* __acad3dV108: a closed outline can be a building pad */
        dims+=bimPropRow('Pad Elevation (m)','<input type="number" step="any" data-propf="gradeelev" value="'+(isFinite(parseFloat(o.gradeElev))?o.gradeElev:'')+'" placeholder="not a pad">');
        if(bimIsPad(o)){   /* __acad3dV145: its slopes, and the surface it is graded into */
          dims+=bimPropRow('Cut Slope (H:V)','<input type="number" step="any" min="0" data-propf="cutslope" value="'+(isFinite(parseFloat(o.cutSlope))?o.cutSlope:'')+'" placeholder="'+BIM_GRADE.cut+' (2:1)">');
          dims+=bimPropRow('Fill Slope (H:V)','<input type="number" step="any" min="0" data-propf="fillslope" value="'+(isFinite(parseFloat(o.fillSlope))?o.fillSlope:'')+'" placeholder="'+BIM_GRADE.fill+' (2:1)">');
          var gby=bimGradedBy(o);
          dims+=bimPropText('Graded',gby?gby.name+(bimGradeStale(gby)?' (out of date: GRADE again)':''):'not yet: GRADE');
        }
        if(isFinite(parseFloat(o.gradeElev)))bimEarthwork().filter(function(r){return r.padId===o.id;}).forEach(function(r){
          dims+=bimPropText('Earthwork',r.surface?('cut '+r.cut.toFixed(2)+' m\u00b3, fill '+r.fill.toFixed(2)+' m\u00b3 against '+r.surface+' (TIN prism)'+(r.note?'; '+r.note:'')):r.note);
        });
      }
    }
    h+=bimPropGroup('Dimensions',dims);
    if(o.t==='terrain'&&o.survey&&!o.grading)h+=bimPropGroup('Survey Check',bimSurveyCheckHtml(o));   /* __acad3dV138; __acad3dV145: not a proposed one */
    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Terrain Analysis',bimTerrainPropsHtml(o));   /* __acad3dV144 */
    if(o.t==='terrain'&&o.grading)h+=bimPropGroup('Grading',bimGradePropsHtml(o));            /* __acad3dV145 */
    if(bimIsFrameMember(o))h+=bimStructPropsHtml(o);   /* __acad3dV125 */
    if(bimIsAlignment(o))h+=bimAlignPropsHtml(o);       /* __acad3dV127 */
    if(bimUsageTarget(o))h+=bimUsagePropsHtml(o);       /* __acad3dV131 */
    if(o.geo)h+=bimGeoPropsHtml(o);                     /* __acad3dV132 */
    if(bimLodOf(o))h+=bimPropGroup('LOD',bimLodHtml(o));   /* __acad3dV139 */
    if(A3D.history&&A3D.history.commits&&A3D.history.commits.length)h+=bimPropGroup('History',bimHistObjHtml(o));   /* __acad3dV146 */
    if(o.context)h+=bimCtxPropsHtml(o);                 /* __acad3dV133 */
    if(o.skp)h+=bimPropGroup('SketchUp',bimSkpPropsHtml(o));   /* __acad3dV163 */

    // ---- Sketch Constraints (V45) -- only for sketches, and only shown once at least one point
    // exists to constrain. Lists each stored constraint in plain English with a per-row delete,
    // plus an approximate remaining-degrees-of-freedom readout (bimEstimateSketchDOF is explicitly
    // labelled approximate everywhere it surfaces, since it is not a rigorous rank analysis). ----
    if(o.t==='sketch'){
      var sc=o.constraints||[];
      var scRows='';
      if(sc.length){
        var si;
        for(si=0;si<sc.length;si++){
          scRows+='<div class="a3d-prow"><div class="a3d-plabel">'+bimEsc(bimSketchConstraintDesc(o,sc[si]))+'</div>'+
            '<div class="a3d-pval"><button data-concondel="'+bimEsc(sc[si].id)+'" title="Delete constraint">Delete</button></div></div>';
        }
      }else{
        scRows+='<div class="a3d-propnote">No constraints yet — select a constraint tool on the Constraints panel, then click points on this sketch.</div>';
      }
      scRows+=bimPropText('Degrees of Freedom (approx.)',bimEstimateSketchDOF(o.pts.length,sc));
      h+=bimPropGroup('Sketch Constraints',scRows);
    }

    // ---- Identity Data ----
    var idd='';
    idd+=bimPropRow('Name','<input type="text" data-propf="name" value="'+bimEsc(o.name)+'">');
    if(o.t==='text')idd+=bimPropRow('Text','<input type="text" data-propf="textcontent" value="'+bimEsc(o.text||'')+'">');
    if(o.t==='note'){
      if(o.kind==='note'){
        idd+=bimPropRow('Title','<input type="text" data-propf="ntitle" value="'+bimEsc(o.title||'')+'">');
        idd+=bimPropRow('Text','<input type="text" data-propf="nbody" value="'+bimEsc(o.body||'')+'">');
      }
      if(o.kind==='table')
        idd+=bimPropRow('Cells (tab / newline)','<input type="text" data-propf="ncells" value="'+
          bimEsc(String(o.cells||'').replace(/\t/g,' \u2192 ').replace(/\n/g,' | '))+'" '+
          'title="Use -> between columns and | between rows">');
      idd+=bimPropRow('Fill','<input type="color" data-propf="nfill" value="'+
        bimEsc(bimNoteHex(o.style&&o.style.fill))+'">');
      idd+=bimPropRow('Line','<input type="color" data-propf="nstroke" value="'+
        bimEsc(bimNoteHex(o.style&&o.style.stroke))+'">');
    }
    if(o.t==='dim'&&bimDimKind(o)==='leader')idd+=bimPropRow('Text','<input type="text" data-propf="leadertext" value="'+bimEsc(o.label||'')+'">');
    idd+=bimPropRow('Pinned','<input type="checkbox" data-propf="locked"'+(bimIsLocked(o)?' checked':'')+'>');
    idd+=bimPropRow('Classification','<select data-propf="classid"><option value="">(none)</option>'+
      A3D.classifications.map(function(c){
        return '<option value="'+c.id+'"'+(o.classId===c.id?' selected':'')+'>'+bimEsc(c.code)+(c.description?' — '+bimEsc(c.description):'')+'</option>';
      }).join('')+'</select> <button data-propf="editclass" title="Manage Classifications">Manage…</button>');
    if(o.bim&&o.bim.imported)idd+=bimPropText('Source','Imported ('+(o.bim.ifcType||'external')+')');
    if(o.linkSourceId){
      var srcObj=objById(o.linkSourceId);
      idd+=bimPropText('Linked From',srcObj?srcObj.name:'(source deleted)');
    }
    var myClones=bimLinkedClonesOf(o.id);
    if(myClones.length){
      idd+=bimPropRow('Linked Clones','<span class="a3d-pstatic">'+myClones.length+'</span> <button data-propf="syncclones">Sync Clones</button>');
      idd+='<div class="a3d-propnote">Clones follow this object automatically as it changes; Sync Clones re-applies immediately.</div>';
    }
    var finRows='';   /* __acad3dV101: the room's own data, from the one field list */
    if(o.t==='roomtag'){
      var tRoom=objById(o.roomId);
      if(tRoom){
        idd+=bimPropText('Tags',tRoom.name);
        idd+=bimPropRow('Room Number','<input type="text" data-roomf="number" value="'+bimEsc(bimRoomField(tRoom,'number'))+'">');
        idd+=bimPropRow('Room Name','<input type="text" data-roomf="name" value="'+bimEsc(tRoom.name||'')+'">');
      }
      idd+=bimPropRow('Show Area','<input type="checkbox" data-tagf="showArea"'+(o.showArea!==false?' checked':'')+'>');
    }
    if(o.t==='room'){
      var rfi;
      for(rfi=0;rfi<BIM_ROOM_FIELDS.length;rfi++){
        var rf=BIM_ROOM_FIELDS[rfi];
        /* __acad3dV105: Occupancy offers the IBC functions and stays free text -- a name not in the
           table is the owner's own; Load Factor shows the default it would override. */
        var rext=rf.k==='occupancy'?' list="bimOccList"':(rf.k==='loadFactor'?' placeholder="'+bimEsc(bimRoomLoadFactorHint(o))+'"':'');
        var rrow=bimPropRow(rf.label,'<input type="text" data-roomf="'+rf.k+'"'+rext+' value="'+bimEsc(bimRoomField(o,rf.k))+'">'+(rf.k==='occupancy'?bimOccDatalist():''));
        if(rf.grp==='fin')finRows+=rrow;else idd+=rrow;
      }
      idd+=bimPropRow('Occupant Load','<span data-roomload="'+bimEsc(o.id)+'">'+bimEsc(bimRoomOccupantsText(o))+'</span>');   /* __acad3dV105 */
    }
    h+=bimPropGroup('Identity Data',idd);
    if(finRows)h+=bimPropGroup('Finishes',finRows);

    /* __acad3dV50: Dependencies. Reads the parametric graph so the relationships an element takes
       part in are visible rather than implicit -- what governs this element, and what would be
       affected by changing it. Each related element is clickable, so the graph doubles as
       navigation. Built from bimGraphRelationsOf, which derives edges from the live model. */
    var rel=null;
    try{rel=bimGraphRelationsOf(o.id);}
    catch(eR){console.warn('[BIM] Could not read dependencies for '+o.name,eR);rel=null;}
    if(rel){
      var depHtml='',rr,ri;
      function depRowHtml(entry){
        var nm=bimEsc(entry.name);
        if(entry.objId)return bimPropRow(entry.label,'<button class="a3d-pedit" data-propsel="'+bimEsc(entry.objId)+'" title="Select this element">'+nm+'</button>');
        return bimPropText(entry.label,entry.name);
      }
      for(ri=0;ri<rel.depends.length;ri++)depHtml+=depRowHtml(rel.depends[ri]);
      for(ri=0;ri<rel.dependents.length;ri++)depHtml+=depRowHtml(rel.dependents[ri]);
      if(!depHtml)depHtml='<div class="a3d-propnote">This element is not linked to any other element.</div>';
      else{
        rr=rel.dependents.length;
        depHtml+='<div class="a3d-propnote">'+(rr?(rr+' element'+(rr===1?'':'s')+' depend'+(rr===1?'s':'')+' on this one and update when it changes.'):'Nothing depends on this element.')+'</div>';
      }
      h+=bimPropGroup('Dependencies',depHtml);
    }

    if(bimIsLocked(o))h+='<div class="a3d-propnote">Pinned: move, grip-edit and delete are blocked until unpinned.</div>';
    if(o.t==='room'){
      if(o.sourceType==='wall'||o.sourceType==='sketch')h+='<div class="a3d-propnote">Boundary tracks its source '+o.sourceType+' live \u2014 it re-measures automatically whenever that shape changes.</div>';
      else h+='<div class="a3d-propnote">Boundary is a snapshot'+(o.sourceType?(' of its source '+o.sourceType):'')+' \u2014 it will not update if that shape is edited later.</div>';
    }
    h+='<div class="a3d-papply"><button data-propf="apply">Apply</button></div>';
    bimRenderInto(el.propsbody,h);   /* __acad3dV118: the panel keeps the focus through its own rebuild */
  }
  function bimMakeImportedSketch(pts,y,closed,bulges){
    if(!pts||pts.length<2)return null;
    A3D.counts.sketch=(A3D.counts.sketch||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:'Import '+A3D.counts.sketch,col:'#5ec4b8',pos:[0,0,0],pts:pts,y:y,on:null,closed:!!closed};
    /* __acad3dV88: only when there is a real arc in it, so an imported straight polyline is the
       same object it was before this phase - no bulges key at all. */
    if(bimHasBulge(bulges))o.bulges=bulges.slice();
    A3D.objs.push(o);
    return o;
  }
  function bimMakeImportedFace(pts3,scale,baseY){
    if(!pts3||pts3.length<3)return null;
    var verts=pts3.map(function(p){return [p[0]*scale,baseY+(p[2]||0)*scale,-p[1]*scale];});   /* __acad3dV104: north up */
    var uniq=[verts[0]],k;
    for(k=1;k<verts.length;k++){
      var last=uniq[uniq.length-1];
      if(Math.abs(last[0]-verts[k][0])>1e-9||Math.abs(last[1]-verts[k][1])>1e-9||Math.abs(last[2]-verts[k][2])>1e-9)uniq.push(verts[k]);
    }
    if(uniq.length<3)return null;
    var faces=uniq.length===3?[[0,1,2]]:[[0,1,2,3]];
    A3D.counts.face=(A3D.counts.face||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Face_'+A3D.counts.face,col:'#9db4c8',pos:[0,0,0],mesh:{v:uniq,f:faces}};
    A3D.objs.push(o);
    return o;
  }
  function bimDecodeUtf8(buf){
    if(typeof TextDecoder!=='undefined')return new TextDecoder('utf-8').decode(buf);
    var bytes=new Uint8Array(buf),s='',i;
    for(i=0;i<bytes.length;i++)s+=String.fromCharCode(bytes[i]);
    return s;
  }

