  // ---- __acad3dV30: Revit-style discipline tabs. Previously all 11 panels were crammed into a
  // single "3D Tools" tab, so panels ran off the right edge and were unreachable. Revit splits
  // by discipline (Architecture / Structure / Annotate / Insert / View / Modify / Manage) with a
  // handful of panels each, and uses split-buttons with a caret to group related commands
  // compactly. Same structure here. Anything Revit has that this app genuinely does not do is
  // marked disabled rather than omitted, so the gap is visible instead of silently missing.
  var A3DR_TABS=[
    {id:'arch',name:'Architecture',disc:'arch',panels:[
      {t:'Build',big:[
        {act:'bim:wall',label:'Wall',menu:[['bim:wall','Wall: Architectural'],['bim:joinwalls','Join Walls']]},
        {act:'bim:door',label:'Door'},
        {act:'bim:window',label:'Window'},
        {act:'bim:component',label:'Component',menu:[['bim:component','Place a Component'],['bim:famsave','Save Selection as Family'],['bim:famimport','Import Family (OBJ/STL)']]}
      ],small:['bim:column','bim:roof','bim:ceiling','bim:floor','bim:stair']},
      {t:'Room & Area',small:['bim:room','bim:tagroom','bim:tagallrooms','bim:usage']},   /* __acad3dV131: Usage */
      {t:'Datum',small:['bim:level','bim:grid']},
      {t:'Work Plane',small:['v:top','v:front','v:right']}
    ]},
    {id:'struct',name:'Structure',disc:'struct',panels:[
      {t:'Structure',small:['bim:column','bim:beam','bim:wall','bim:floor','bim:truss','bim:brace','bim:analyze']},   /* __acad3dV125 */
      {t:'Datum',small:['bim:grid','bim:level']},
      {t:'Foundation',small:['bim:footing','bim:foundwall','bim:foundslab']},
      {t:'Reinforcement',small:['bim:rebar']}
    ]},
    {id:'a3ddraft',name:'Drafting',panels:[
      {t:'Draw',big:[
        {act:'s:poly',label:'Polyline'},
        {act:'s:rect',label:'Rectangle'},
        {act:'s:circle',label:'Circle'}
      ],small:['bim:arc','bim:wall','bim:room','bim:floor','bim:column']},
      {t:'Modify',small:['bim:trim','bim:extend','bim:fillet','bim:chamfer','bim:break','bim:lengthen','bim:scale','bim:offset','bim:align','bim:mirror','bim:rotate','bim:presspull','m:array','bim:polararray','m:dup','m:del']},
      {t:'Constraints',small:['con:coincident','con:horizontal','con:vertical','con:parallel','con:perpendicular','con:equal','con:distance','con:angle','con:pointonline','con:midpoint','con:symmetric_pt','con:symmetric_line']},
      {t:'Dimension',big:[
        {act:'bim:dim',label:'Dimension',menu:[['bim:dim','Aligned / Linear'],['bim:dimang','Angular'],['bim:dimrad','Radial'],['bim:dimdia','Diameter']]}
      ],small:['bim:text','bim:leader','bim:tagroom']},
      {t:'View',small:['bim:level','v:top','bim:saveview']}
    ]},
    {id:'a3dannotate',name:'Annotate',panels:[
      {t:'Dimension',big:[
        {act:'bim:dim',label:'Dimension',menu:[['bim:dim','Aligned / Linear'],['bim:dimang','Angular'],['bim:dimrad','Radial'],['bim:dimdia','Diameter']]}
      ],small:['bim:dimang','bim:dimrad','bim:dimdia']},
      {t:'Text',small:['bim:text','bim:leader']},
      {t:'Tag',small:['bim:tagroom','bim:tagallrooms','bim:tagcat']}
    ]},
    {id:'a3dinsert',name:'Insert',panels:[
      {t:'Link',small:['bim:linkifc','bim:linkcad']},
      {t:'Import',small:['bim:importcad']},
      {t:'Load from Library',small:['bim:famimport','bim:famsave']}
    ]},
    {id:'a3dview',name:'View',panels:[
      {t:'Create',big:[
        {act:'v:iso',label:'3D View',menu:[['v:iso','Default 3D View'],['v:home','Home'],['v:fit','Fit to Model']]},
        {act:'bim:section',label:'Section'}
      ],small:['v:top','v:front','v:right','bim:saveview']},
      {t:'Section',small:['m:exitsection','m:flipsection']},
      {t:'Sheet Composition',small:['bim:sheet','bim:titleblock']},
      {t:'Windows',small:['bim:uipanels']}
    ]},
    {id:'a3dmodify',name:'Modify',panels:[
      {t:'Modify',big:[
        {act:'m:dup',label:'Copy'},
        {act:'bim:mirror',label:'Mirror'},
        {act:'bim:rotate',label:'Rotate'}
      ],small:['m:array','bim:polararray','bim:joinwalls','bim:mergewalls','m:del','m:desel','bim:trim','bim:extend','bim:fillet','bim:chamfer','bim:break','bim:lengthen','bim:scale','bim:offset','bim:align','bim:clonelinked','bim:syncclones']},
      {t:'Geometry',small:['b:union','b:cut','b:isect']},
      {t:'Sketch',small:['s:rect','s:circle','s:poly','p:pad','p:pocket','bim:presspull']},
      {t:'Constraints',small:['con:coincident','con:horizontal','con:vertical','con:parallel','con:perpendicular','con:equal','con:distance','con:angle','con:pointonline','con:midpoint','con:symmetric_pt','con:symmetric_line']}
    ]},
    {id:'a3dmassing',name:'Massing & Site',panels:[
      {t:'Conceptual Mass',small:['box','cyl','sphere','cone','torus']},
      {t:'Program',small:['bim:usage','bim:usages']},   /* __acad3dV131 */
      {t:'Model by Face',small:['tube','prism','wedge','ellipsoid']},
      {t:'Site',small:['bim:map','bim:findaddress','bim:geoimport','bim:context','bim:datalayers','bim:property','bim:propshape','bim:truenorth','bim:alignment']}   /* __acad3dV132: the map first */   /* __acad3dV103; __acad3dV127: Alignment */
    ]},
    {id:'a3dmanage',name:'Manage',panels:[
      {t:'Settings',small:['bim:layers','bim:levels','bim:classification','bim:units']},
      {t:'Project',small:['m:saveproj','m:openproj','bim:projinfo','bim:purge','bim:checkmodel']},
      {t:'Export',small:['m:exportpng','m:exportpdf','m:exportdxf','m:exportsvg','m:exportgeojson']}
    ]}
  ];
  // Commands Revit has that this app does not implement yet. Listed so the tool dock shows the
  // real shape of the toolset, greyed out, rather than pretending the gap is not there.
  var A3DR_UNIMPL={
    'bim:truss':1,'bim:brace':1,'bim:rebar':1,   /* __acad3dV102: foundwall and foundslab implemented */
    'bim:tagcat':1,'bim:linkcad':1,   /* __acad3dV101: bim:tagroom implemented */
    'bim:units':1,'bim:projinfo':1,'bim:purge':1
  };
  /* __acad3dV71: DISCIPLINES, and the extension API that makes a new engineering domain cheap.

     The scaling problem this solves, stated as it was measured. Before this phase a command
     cost FOUR edits in four places roughly 700 lines apart -- A3DR_ICONS, a tab's panel list,
     the a3drLabel literal, and a branch of the 60-case dispatch chain -- and the dock's rows
     were a hardcoded [[5 ids],[4 ids]] that nine groups already filled. Adding Bridge,
     Mechanical and MEP would have meant 12-15 groups with nowhere to put them, every tool from
     every domain on screen at once, and four scattered edits per command.

     Three changes fix that, and none of them touches the existing commands:
       - a tab may declare a `disc`; the dock shows the ACTIVE discipline's tabs plus the
         shared ones, the way Revit's discipline filter works. A domain is data now.
       - dock rows are COMPUTED from the group count, so any number of groups lays out.
       - a command registered through __a3dRegisterCommand supplies its label, icon and runner
         in ONE call. Existing commands keep their four sites; new ones cost one.
     The ext maps are consulted FIRST everywhere, so a registered command can also override a
     built-in one -- which is what makes a domain plug-in able to specialise, say, Column. */
  var A3D_DISCIPLINES=[{id:'arch',name:'Architecture'},{id:'struct',name:'Structure'}];
  var A3D_DISC_CUR='arch';
  var A3D_CMD_EXT={};   // id -> {label, icon, run, unimpl}
  function a3drExt(act){return A3D_CMD_EXT[act]||null;}
  function a3drIsUnimpl(act){
    var e=a3drExt(act);
    if(e&&typeof e.unimpl!=='undefined')return !!e.unimpl;
    return !!A3DR_UNIMPL[act];
  }
  /* A tab belongs to the dock when it declares no discipline (shared: Drafting, Annotate,
     Modify, View, Insert, Massing, Manage) or declares the active one. */
  function a3drTabInDiscipline(t,disc){return !t.disc||t.disc===(disc||A3D_DISC_CUR);}
  function a3drDockTabs(disc){
    var out=[],i;
    for(i=0;i<A3DR_TABS.length;i++)if(a3drTabInDiscipline(A3DR_TABS[i],disc))out.push(A3DR_TABS[i]);
    return out;
  }
  function a3drRegisterCommand(spec){
    if(!spec||!spec.id)return false;
    A3D_CMD_EXT[spec.id]={label:spec.label||spec.id,icon:spec.icon||'',
      run:(typeof spec.run==='function')?spec.run:null,unimpl:!!spec.unimpl};
    return true;
  }
  function a3drRegisterDiscipline(spec){
    if(!spec||!spec.id)return false;
    var i;
    for(i=0;i<A3D_DISCIPLINES.length;i++)if(A3D_DISCIPLINES[i].id===spec.id)return false;
    A3D_DISCIPLINES.push({id:spec.id,name:spec.name||spec.id});
    return true;
  }
  function a3drRegisterTab(spec){
    if(!spec||!spec.id||!spec.panels)return false;
    var i;
    for(i=0;i<A3DR_TABS.length;i++)if(A3DR_TABS[i].id===spec.id)return false;
    A3DR_TABS.push({id:spec.id,name:spec.name||spec.id,disc:spec.disc||null,panels:spec.panels});
    return true;
  }
  function a3drIcon(act){
    var xi=a3drExt(act);
    if(xi&&xi.icon)return xi.icon;
    if(act.indexOf('b:')===0)return A3DR_ICONS[act.slice(2)]||'';
    if(act.indexOf('v:')===0)return A3DR_ICONS['v'+act.slice(2)]||'';
    if(act.indexOf('m:')===0)return A3DR_ICONS[act.slice(2)]||'';
    return A3DR_ICONS[act]||'';
  }
  function a3drLabel(act){
    var xl=a3drExt(act);
    if(xl&&xl.label)return xl.label;
    var L={'s:rect':'Rect','s:circle':'Circle','s:poly':'Polyline','p:pad':'Pad','p:pocket':'Pocket','bim:wall':'Wall','bim:floor':'Floor','bim:room':'Room','bim:roof':'Roof','bim:stair':'Stair','bim:column':'Column','bim:door':'Door','bim:window':'Window','bim:dim':'Dimension','bim:text':'Text','bim:section':'Section','bim:ceiling':'Ceiling','bim:dimang':'Angular','bim:dimrad':'Radius','bim:dimdia':'Diameter','bim:leader':'Leader','m:exportdxf':'DXF','m:exportsvg':'SVG','bim:mirror':'Mirror','bim:rotate':'Rotate','bim:polararray':'Polar Array','bim:joinwalls':'Join Walls','bim:extend':'Extend','bim:arc':'Arc','bim:fillet':'Fillet','bim:chamfer':'Chamfer','bim:break':'Break','bim:lengthen':'Lengthen','bim:scale':'Scale','b:union':'Union','b:cut':'Cut','b:isect':'Intersect','v:home':'Home','v:fit':'Fit','v:top':'Top','v:front':'Front','v:right':'Right','v:iso':'Iso','m:del':'Delete','m:desel':'Deselect','m:dup':'Duplicate','m:array':'Array','m:exportpng':'PNG','m:exportpdf':'PDF','m:exitsection':'Exit Section','m:flipsection':'Flip Section','m:saveproj':'Save Project','m:openproj':'Open\u2026',
      'bim:component':'Component','bim:famsave':'Save Family','bim:famimport':'Load Family',
      'bim:tagroom':'Tag Room','bim:tagallrooms':'Tag All Rooms','bim:tagcat':'Tag by Category','bim:level':'Level','bim:grid':'Grid',
      'bim:beam':'Beam','bim:analyze':'Analyze','bim:truss':'Truss','bim:brace':'Brace','bim:foundwall':'Wall Foundation','bim:footing':'Isolated Footing','bim:property':'Property Line','bim:propshape':'Property from Shape','bim:truenorth':'True North','bim:alignment':'Alignment','bim:usage':'Usage','bim:usages':'Usages','bim:map':'Map','bim:findaddress':'Find Address','bim:geoimport':'Import GeoJSON','bim:context':'Site Context','bim:datalayers':'Data Layers','m:exportgeojson':'GeoJSON',
      'bim:foundslab':'Foundation Slab','bim:rebar':'Rebar','bim:linkifc':'Link IFC','bim:linkcad':'Link CAD',
      'bim:importcad':'Import CAD','bim:saveview':'Save View','bim:sheet':'Sheet','bim:titleblock':'Title Block',
      'bim:uipanels':'User Interface','bim:trim':'Trim','bim:offset':'Offset','bim:align':'Align',
      'bim:layers':'Layers','bim:levels':'Levels','bim:classification':'Classifications','bim:units':'Project Units','bim:projinfo':'Project Info',
      'bim:purge':'Purge Unused','bim:mergewalls':'Merge Walls','bim:checkmodel':'Check Model',
      'bim:clonelinked':'Linked Clone','bim:syncclones':'Sync Clones','bim:presspull':'Push/Pull',   /* __acad3dV123 */
      'con:coincident':'Coincident','con:horizontal':'Horizontal','con:vertical':'Vertical',
      'con:parallel':'Parallel','con:perpendicular':'Perpendicular','con:equal':'Equal',
      'con:distance':'Distance','con:angle':'Angle','con:pointonline':'Point on Line','con:midpoint':'Midpoint',
      'con:symmetric_pt':'Symmetric (Point)','con:symmetric_line':'Symmetric (Line)'};
    if(L[act])return L[act];
    return (TYPES[act]||{}).n||act;
  }
  /* __acad3dV70: the floating tool dock, GENERATED from A3DR_TABS rather than hand-listed: a
     hand-built dock would quietly drop commands, and a command that exists but cannot be reached
     is the same failure as one that does not work. One group per registry TAB (nine groups over
     two rows, the reference tool's density); the group shows that tab's headline tools and its
     caret opens every action the tab has, grouped under its panel headings. Buttons carry
     data-a3dr, so the document-level dispatcher wires them by construction. */
  function a3drActOf(entry){return (typeof entry==='string')?entry:entry.act;}
  /* Every action a tab can reach, in registry order, grouped by panel and de-duplicated within
     the tab. Drop-down entries hanging off a big button (e.g. Dimension > Angular) are pulled
     in too -- they are actions of that panel, and leaving them out is exactly how a rebuild
     loses tools without anyone noticing. */
  function a3drTabGroups(tab){
    var out=[],seen={},i,j,k,p,acts,a;
    for(i=0;i<tab.panels.length;i++){
      p=tab.panels[i];acts=[];
      if(p.big)for(j=0;j<p.big.length;j++){
        a=a3drActOf(p.big[j]);
        if(!seen[a]){seen[a]=1;acts.push(a);}
        if(p.big[j].menu)for(k=0;k<p.big[j].menu.length;k++){
          a=p.big[j].menu[k][0];
          if(!seen[a]){seen[a]=1;acts.push(a);}
        }
      }
      if(p.small)for(j=0;j<p.small.length;j++){
        a=p.small[j];
        if(!seen[a]){seen[a]=1;acts.push(a);}
      }
      if(acts.length)out.push({t:p.t,acts:acts});
    }
    return out;
  }
  /* Up to three headline buttons per group: the tab's big buttons first, then its smalls.
     Unimplemented commands are never promoted to the dock face -- they stay listed, greyed,
     inside the caret, where the ribbon already showed them, so the dock's visible row is all
     working tools. */
  function a3drTabPrimary(tab){
    var out=[],i,j,p,a;
    for(i=0;i<tab.panels.length&&out.length<3;i++){
      p=tab.panels[i];
      if(!p.big)continue;
      for(j=0;j<p.big.length&&out.length<3;j++){
        a=a3drActOf(p.big[j]);
        if(!a3drIsUnimpl(a)&&out.indexOf(a)<0)out.push(a);
      }
    }
    for(i=0;i<tab.panels.length&&out.length<3;i++){
      p=tab.panels[i];
      if(!p.small)continue;
      for(j=0;j<p.small.length&&out.length<3;j++){
        a=p.small[j];
        if(!a3drIsUnimpl(a)&&out.indexOf(a)<0)out.push(a);
      }
    }
    return out;
  }
  /* __acad3dV130: the dock is one row -- the discipline, the tools pinned for it, All tools and the
     search. Everything else is in the Tools and shortcuts panel. */
  function bimBuildDock(){
    var host=document.getElementById('a3d-dock');
    if(!host)return false;
    var cat=bimCmdCatalog(),pins=bimDockPins(A3D_DISC_CUR),i,a;
    var names=bimDockLabelsOn();   /* __acad3dV129: tool names under the icons, unless Icons only */
    host.classList.toggle('a3d-docklabels',names);
    var h='<div class="a3d-dockbody"><div class="a3d-dockrow a3d-dockone">'+
      '<select id="a3d-discsel" class="a3d-discsel" aria-label="Discipline: which tools the dock and the panel start with">'+
      (function(){var o='',d;for(d=0;d<A3D_DISCIPLINES.length;d++)
        o+='<option value="'+bimEsc(A3D_DISCIPLINES[d].id)+'"'+
          (A3D_DISCIPLINES[d].id===A3D_DISC_CUR?' selected':'')+'>'+
          bimEsc(A3D_DISCIPLINES[d].name)+'</option>';return o;})()+
      '</select><div class="a3d-dsep"></div>'+
      '<div class="a3d-dockgrp a3d-dockpins" data-dockgrp="__pins">';
    for(i=0;i<pins.length;i++){
      a=pins[i];
      h+='<button type="button" class="a3d-dbtn" data-a3dr="'+a+'" data-a3dtip="'+a+'" aria-label="'+
        bimEsc(a3drLabel(a)+bimActHint(a,cat))+'">'+a3drIcon(a)+
        (names?'<span class="a3d-dblbl">'+bimEsc(a3drLabel(a))+'</span>':'')+'</button>';
    }
    h+='</div><div class="a3d-dsep"></div>'+
      '<button type="button" class="a3d-dall" id="a3d-dall" data-a3dtip="__all" aria-label="All tools and shortcuts">'+A3DR_ALL_ICON+
      (names?'<span class="a3d-dblbl">All tools</span>':'')+'</button>'+
      '<button type="button" class="a3d-dsearchpill" id="a3d-dsearch" aria-label="Search tools and commands" data-a3dtip="__search">'+
      A3DR_SEARCH_ICON+'<span>Search</span><kbd>'+bimEsc(A3D_MODKEY)+' K</kbd></button>'+
      '</div></div>';
    bimRenderInto(host,h);   /* __acad3dV118: the Discipline dropdown keeps the focus */
    bimTipHide();bimBindDockTips(host);   /* __acad3dV129 */
    return true;
  }
  /* The tools on the dock when nobody has pinned any: the ones a person reaches for most, per
     discipline. A discipline added later (a domain pack) starts with its own tabs' first tools. */
  var A3D_DOCK_PIN_DEFAULTS={
    arch:['bim:wall','bim:door','bim:window','bim:floor','bim:column','bim:room','s:poly','bim:dim','m:dup'],
    struct:['bim:column','bim:beam','bim:floor','bim:brace','bim:footing','bim:grid','bim:level','bim:analyze','bim:dim']
  };
  var A3D_DOCK_PIN_MAX=12;
  function bimDockPins(disc){
    var p=bimLoadUIPanelPrefs(),set=p.dockPins&&p.dockPins[disc],known={},all=a3drAllCommands(),i,out=[];
    for(i=0;i<all.length;i++)known[all[i].act]=1;
    if(!set){
      set=A3D_DOCK_PIN_DEFAULTS[disc];
      if(!set){set=[];var tabs=a3drDockTabs(disc);for(i=0;i<tabs.length;i++)if(tabs[i].disc===disc)set=set.concat(a3drTabPrimary(tabs[i]));}
    }
    for(i=0;i<set.length&&out.length<A3D_DOCK_PIN_MAX;i++)if(known[set[i]]&&!a3drIsUnimpl(set[i])&&out.indexOf(set[i])<0)out.push(set[i]);
    return out;
  }
  function bimSetDockPin(act,on){
    var pins=bimDockPins(A3D_DISC_CUR),ix=pins.indexOf(act),lab=a3drLabel(act);
    if(on&&ix<0){
      if(pins.length>=A3D_DOCK_PIN_MAX){a3dToast('The dock holds '+A3D_DOCK_PIN_MAX+' tools: take one off first');return false;}
      pins.push(act);
    }else if(!on&&ix>=0)pins.splice(ix,1);
    else return true;
    var p=bimLoadUIPanelPrefs();p.dockPins=p.dockPins||{};p.dockPins[A3D_DISC_CUR]=pins;bimSaveUIPanelPrefs(p);
    bimBuildDock();
    a3dToast(on?lab+' is on the dock':lab+' is off the dock; it stays in All tools');
    return true;
  }
  function bimToggleDockPin(p,act){
    var row=p.querySelector('.a3d-rkrow[data-rkact="'+act+'"]'),on=!(row&&row.getAttribute('data-rkpinned')==='1');
    if(!bimSetDockPin(act,on))return false;
    var now=bimDockPins(A3D_DISC_CUR),rows=p.querySelectorAll('.a3d-rktool'),i;
    for(i=0;i<rows.length;i++){
      var a=rows[i].getAttribute('data-rkact'),pin=now.indexOf(a)>=0,b=rows[i].querySelector('[data-rkpin]'),l=a3drLabel(a);
      rows[i].setAttribute('data-rkpinned',pin?'1':'0');
      if(b){b.setAttribute('aria-pressed',pin?'true':'false');b.setAttribute('aria-label',pin?'Take '+l+' off the dock':'Put '+l+' on the dock');
        b.title=pin?'On the dock: click to take it off':'Put it on the dock';}
    }
    var pc=p.querySelector('.a3d-rkpinn');if(pc)pc.textContent=String(now.length);
    var f=p.querySelector('.a3d-rkfind');bimFilterShortcuts(p,f?f.value:'');
    return true;
  }
  /* the panel, from the dock's All tools, SHORTCUTS or ? -- opened once, never toggled shut */
  function bimOpenToolsPanel(){
    var hp=document.getElementById('a3d-rupop');
    if(hp&&hp.classList.contains('open')&&hp.getAttribute('data-for')==='help')return true;
    var b=document.querySelector('[data-a3drumenu="help"]');
    if(!b){a3dToast('The tools and shortcuts panel is not available here');return false;}
    b.click();
    return true;
  }
  /* a tool run from the dock or the panel is a use, as one run from the search is */
  function bimActUsed(act){
    var it=bimCatForAct(bimCmdCatalog(),act);
    if(it)bimCmdUsed(it.id);
  }
