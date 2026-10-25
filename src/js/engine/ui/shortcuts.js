  /* ---- __acad3dV85: the shortcut registry ----

     One list, rendered into the sheet AND driven by the Phase 85 suite: every row carrying a
     `k` is dispatched as a real key event and asserted to do what its label claims. The key
     handlers in this app are a switch chain rather than a table, so this list cannot be derived
     from them the way V74 derived the schedule categories. Holding it to account with the suite
     is the next best thing, and it is what stops the sheet drifting into fiction -- which is
     precisely what the button this replaces had become.

     `k` is the ev.key value; `mod` means Ctrl (Cmd on a Mac). A row with k:null documents
     something a single synthetic keypress cannot demonstrate, and says so here rather than
     pretending. */
  var A3D_MODKEY=(navigator.platform&&/Mac|iPhone|iPad/.test(navigator.platform))?'Cmd':'Ctrl';
  var A3D_KEYS=[
    {grp:'Views',rows:[
      /* The handler tests ev.key === '>' and does not look at shiftKey. Producing '>' on a
         US keyboard involves Shift, but ">" reads as Shift AND '>', which is a
         different chord and is not what the app listens for. Measured: Playwright's 'Shift+.'
         delivers key='.' and does nothing; 'Shift+Period' delivers key='>' and works. */
      {keys:['>'],k:'>',label:'Switch between the plan and 3D'},
      {keys:['Esc'],k:'Escape',label:'Back out one step: menu, zoom window, dialog, sketch, section, then clear the selection'},
      {keys:['Enter'],k:null,label:'With nothing running, repeats the last command'}
    ]},
    /* __acad3dV86: rewritten for the AutoCAD input model. The previous rows described a
       grammar that accepted a bare length and nothing else, which is what the tools took
       before this phase. A help sheet describing the previous version is the same fault V85
       built its suite to catch, arriving from the other direction: the keys changed, not the
       sheet. */
    {grp:'Drawing',rows:[
      {keys:['Enter'],k:null,label:'Finish the current line, polyline, wall or stair'},
      {keys:['C'],k:null,label:'Close the path (from three points on)'},
      {keys:['U'],k:null,label:'Undo the last point'},
      {keys:['Arrows'],k:null,label:'Nudge the selected object'}
    ]},
    /* __acad3dV129: the grammar of a typed point is not a key: a group of its own, saying when */
    {grp:'Typing points',note:'While a tool is taking points, type a position instead of clicking, then press Enter.',rows:[
      {keys:['x,y'],k:null,label:'Absolute point. @x,y is relative to the last point; # forces absolute'},
      {keys:['d<a'],k:null,label:'Polar point: distance, then angle. @5<45 is relative'},
      {keys:['0-9'],k:null,label:'A bare length draws that far along the current direction'}
    ]},
    {grp:'Snaps',rows:[
      {keys:['F3'],k:'F3',label:'Object snap on or off',cmd:'OSNAP'},   /* __acad3dV128: cmd -- the command a chord runs */
      {keys:['F8'],k:'F8',label:'Ortho on or off',cmd:'ORTHO'},
      {keys:['F9'],k:'F9',label:'Grid snap on or off',cmd:'GRID'}
    ]},
    {grp:'Editing',rows:[
      {keys:[A3D_MODKEY,'Z'],k:'z',mod:true,label:'Undo',cmd:'UNDO'},
      {keys:[A3D_MODKEY,'Y'],k:'y',mod:true,label:'Redo',cmd:'REDO'},
      {keys:[A3D_MODKEY,'D'],k:'d',mod:true,label:'Duplicate the selection',cmd:'COPY'},
      {keys:['Delete'],k:null,label:'Delete the selection',cmd:'ERASE'}
    ]},
    {grp:'Project',rows:[
      {keys:[A3D_MODKEY,'S'],k:null,label:'Export the project file',cmd:'SAVE'},
      {keys:[A3D_MODKEY,'O'],k:null,label:'Open a project file',cmd:'OPEN'},   /* __acad3dV128: bound since V115, never listed */
      {keys:[A3D_MODKEY,'K'],k:null,label:'Command search, or just start typing a command'},
      {keys:['?'],k:null,label:'This panel: the keyboard shortcuts'}   /* __acad3dV129 */
    ]}
  ];
  /* __acad3dV122: the sheet's groups -- A3D_KEYS, and the keys of the Pages display and of Present,
     read from the tables their handlers read. A row of alternatives (`alt`) is any one of its keys.
     They carry no `k`: the V85 suite presses keys with nothing open, and these work on the pages or
     in a presentation, where the V122 suite presses them. */
  function bimShortcutGroups(){
    function rows(tbl){
      return tbl.map(function(r){return {keys:r.say.slice(),k:null,alt:true,label:r.label};});
    }
    return A3D_KEYS.concat([{grp:'Faces',rows:rows(A3D_FACE_GESTURES).concat(rows(A3D_FACE_KEYS))},   /* __acad3dV123 */
      {grp:'Pages',rows:rows(A3D_PAGEVIEW_KEYS)},{grp:'Presenting',rows:rows(A3D_SHOW_KEYS)}]);
  }
  /* __acad3dV129: the shortcuts panel -- the categories on the left, one list, the keys on the right */
  /* __acad3dV130: tools and shortcuts -- every tool and every key in one list, the categories on
     the left (the ribbon's tabs, then the key groups), a filter by kind, a sort, and a pin for the
     dock. Every child of the list carries its place (data-rkord), so By group can put it back. */
  function bimShortcutsHtml(){
    var groups=bimShortcutGroups(),g,r,i,j,k,total=0,nav='',list='',ord=0,use=bimCmdUsage(),cat=bimCmdCatalog();
    var pins=bimDockPins(A3D_DISC_CUR),tabs=A3DR_TABS,seen={},nTools=0,nPinned=0,tnav='',tlist='';
    for(i=0;i<tabs.length;i++){
      var tab=tabs[i],gid='tool:'+tab.id,grs=a3drTabGroups(tab),rows='',n=0,gi,ai,a;
      for(gi=0;gi<grs.length;gi++)for(ai=0;ai<grs[gi].acts.length;ai++){
        a=grs[gi].acts[ai];
        if(seen[a])continue;   /* every ribbon action, even one the search leaves out (BIM_ACT_HIDE) */
        seen[a]=1;n++;
        var it=bimCatForAct(cat,a),off=a3drIsUnimpl(a),lab=a3drLabel(a),pinned=pins.indexOf(a)>=0;
        var desc=off?'Not built yet':((it&&it.desc)||BIM_ACT_DESC[a]||'');
        var ks=(it&&it.keys)||null,nuse=(it&&use[it.id]&&use[it.id].n)||0;
        if(pinned)nPinned++;
        rows+='<div class="a3d-rkrow a3d-rktool'+(off?' off':'')+'" data-rkg="'+gid+'" data-rkkind="tool" data-rkact="'+bimEsc(a)+'" data-rkord="'+(ord++)+'"'+
          ' data-rkname="'+bimEsc(String(lab).toLowerCase())+'" data-rkuse="'+nuse+'" data-rkpinned="'+(pinned?1:0)+'"'+
          ' data-rkhay="'+bimEsc((lab+' '+desc+' '+tab.name+' '+grs[gi].t+' '+(it?it.name+' '+it.aliases.join(' ')+' '+(it.terms||''):'')+' '+(ks?ks.join(' ')+' '+ks.join('+'):'')).toLowerCase())+'">'+
          '<button type="button" class="a3d-rkrun"'+(off?' disabled':' data-a3dr="'+bimEsc(a)+'"')+'>'+a3drIcon(a)+
          '<span class="a3d-rklab">'+bimEsc(lab)+'</span><span class="a3d-rkdesc">'+bimEsc(desc)+'</span></button>'+
          '<span class="a3d-rkcmd">'+(it?'type '+bimEsc(it.name):'')+'</span><span class="a3d-rkkeys">';
        if(ks)for(k=0;k<ks.length;k++)rows+=(k?'<span class="a3d-rkplus">+</span>':'')+'<kbd>'+bimEsc(ks[k])+'</kbd>';
        rows+='</span>'+(off?'<span class="a3d-rkpinx"></span>':'<button type="button" class="a3d-rkpin" data-rkpin="'+bimEsc(a)+'" aria-pressed="'+(pinned?'true':'false')+'"'+
          ' aria-label="'+bimEsc((pinned?'Take '+lab+' off the dock':'Put '+lab+' on the dock'))+'" title="'+(pinned?'On the dock: click to take it off':'Put it on the dock')+'">'+A3DR_PIN_ICON+'</button>')+'</div>';
      }
      if(!n)continue;
      nTools+=n;
      var dn=tab.disc?bimDiscName(tab.disc):'';
      tnav+='<button type="button" class="a3d-rkcat" data-rkcat="'+gid+'"><span>'+bimEsc(tab.name)+(dn&&dn!==tab.name?' <i>'+bimEsc(dn)+'</i>':'')+'</span><span class="a3d-rkn">'+n+'</span></button>';
      tlist+='<div class="a3d-rkgrp" data-rkg="'+gid+'" data-rkord="'+(ord++)+'">'+bimEsc(tab.name)+'</div>'+rows;
    }
    for(i=0;i<groups.length;i++){
      g=groups[i];total+=g.rows.length;
      nav+='<button type="button" class="a3d-rkcat" data-rkcat="'+bimEsc(g.grp)+'"><span>'+bimEsc(g.grp)+'</span><span class="a3d-rkn">'+g.rows.length+'</span></button>';
      list+='<div class="a3d-rkgrp" data-rkg="'+bimEsc(g.grp)+'" data-rkord="'+(ord++)+'">'+bimEsc(g.grp)+'</div>';
      if(g.note)list+='<div class="a3d-rkgnote" data-rkg="'+bimEsc(g.grp)+'" data-rkord="'+(ord++)+'">'+bimEsc(g.note)+'</div>';
      for(j=0;j<g.rows.length;j++){
        r=g.rows[j];
        var ru=(r.cmd&&use['cmd:'+r.cmd]&&use['cmd:'+r.cmd].n)||0;
        list+='<div class="a3d-rkrow" data-rkg="'+bimEsc(g.grp)+'" data-rkkind="key" data-rkord="'+(ord++)+'" data-rkname="'+bimEsc(r.label.toLowerCase())+'" data-rkuse="'+ru+'"'+
          ' data-rkhay="'+bimEsc((r.keys.join(' ')+' '+r.keys.join('+')+' '+r.label+' '+g.grp+' '+(r.cmd||'')).toLowerCase())+'">'+
          '<span class="a3d-rklab">'+bimEsc(r.label)+'</span>'+
          '<span class="a3d-rkcmd">'+(r.cmd?'type '+bimEsc(r.cmd):'')+'</span><span class="a3d-rkkeys">';
        for(k=0;k<r.keys.length;k++){
          if(k)list+='<span class="a3d-rkplus">'+(r.alt?'/':'+')+'</span>';   /* __acad3dV122: a slash between alternatives */
          list+='<kbd>'+bimEsc(r.keys[k])+'</kbd>';
        }
        list+='</span><span class="a3d-rkpinx"></span></div>';
      }
    }
    tlist=bimRkReorder(tlist);
    return '<div class="a3d-rkhead"><h2 class="a3d-rktitle">Tools and shortcuts</h2>'+
      '<input type="search" class="a3d-rkfind" placeholder="Search tools and keys: wall, undo, ctrl z, F8" aria-label="Search the tools and keyboard shortcuts" autocomplete="off" spellcheck="false">'+   /* __acad3dV128 */
      '<button type="button" class="a3d-rkclose" data-rkclose aria-label="Close the tools and shortcuts">\u00d7</button></div>'+
      '<div class="a3d-rkbar"><div class="a3d-rkkinds" role="group" aria-label="Show">'+
      '<button type="button" class="a3d-rkkind on" data-rkkindf="all" aria-pressed="true">All</button>'+
      '<button type="button" class="a3d-rkkind" data-rkkindf="tool" aria-pressed="false">Tools</button>'+
      '<button type="button" class="a3d-rkkind" data-rkkindf="key" aria-pressed="false">Keys</button></div>'+
      '<label class="a3d-rksortl">Sort <select class="a3d-rksort" aria-label="Sort the list">'+
      '<option value="group">By group</option><option value="name">By name</option><option value="used">Most used</option></select></label>'+
      '<span class="a3d-rkshown" aria-live="polite"></span></div>'+
      '<div class="a3d-rkbody"><nav class="a3d-rknav" aria-label="Categories">'+
      '<button type="button" class="a3d-rkcat on" data-rkcat="all" aria-pressed="true"><span>All</span><span class="a3d-rkn">'+(nTools+total)+'</span></button>'+
      '<button type="button" class="a3d-rkcat" data-rkcat="__pinned"><span>On the dock</span><span class="a3d-rkn a3d-rkpinn">'+nPinned+'</span></button>'+
      '<div class="a3d-rknavh">Tools</div>'+tnav+'<div class="a3d-rknavh">Keys</div>'+nav+
      '<div class="a3d-rknote">Pin a tool to put it on the dock. Every command by name: <kbd>'+bimEsc(A3D_MODKEY)+'</kbd>+<kbd>K</kbd>, or start typing on the drawing.</div></nav>'+
      '<div class="a3d-rukeys">'+tlist+list+'<div class="a3d-rkempty" hidden>Nothing matches. Try what it does, like \u201csnap\u201d, or a key, like \u201cF8\u201d.</div></div></div>';
  }
  /* the tools' rows were numbered before their header was: number the list again, as it stands */
  function bimRkReorder(html){
    var box=document.createElement('div'),i;
    box.innerHTML=html;
    for(i=0;i<box.children.length;i++)box.children[i].setAttribute('data-rkord',String(i));
    return box.innerHTML;
  }
  function bimDiscName(id){
    for(var i=0;i<A3D_DISCIPLINES.length;i++)if(A3D_DISCIPLINES[i].id===id)return A3D_DISCIPLINES[i].name;
    return id;
  }
  /* the catalogue's entry for a ribbon action: its own, or the typed command it runs */
  function bimCatForAct(cat,act){
    var cad=BIM_ACT_CMD[act],i;
    for(i=0;i<cat.length;i++)if((cad&&cat[i].cad===cad)||cat[i].act===act||cat[i].ribbon===act)return cat[i];
    return null;
  }
  /* By group puts every row back in its place; By name and Most used make one list */
  function bimSortShortcuts(p){
    var lst=p.querySelector('.a3d-rukeys');if(!lst)return;
    var how=p.getAttribute('data-rksort')||'group',em=lst.querySelector('.a3d-rkempty');
    var kids=Array.prototype.slice.call(lst.children).filter(function(e){return e!==em;});
    kids.sort(function(a,b){
      if(how==='group')return (+a.getAttribute('data-rkord'))-(+b.getAttribute('data-rkord'));
      var ar=a.classList.contains('a3d-rkrow'),br=b.classList.contains('a3d-rkrow');
      if(ar!==br)return ar?1:-1;   /* the headers, hidden, first */
      if(how==='used'){var du=(+b.getAttribute('data-rkuse')||0)-(+a.getAttribute('data-rkuse')||0);if(du)return du;}
      var an=a.getAttribute('data-rkname')||'',bn=b.getAttribute('data-rkname')||'';
      return an<bn?-1:(an>bn?1:0);
    });
    kids.forEach(function(e){lst.appendChild(e);});
    if(em)lst.appendChild(em);
    lst.scrollTop=0;
  }
  function bimRailStackHtml(){
    var h='<div id="a3d-railutil">',i;
    for(i=0;i<A3D_RAIL_UTILS.length;i++){
      var u=A3D_RAIL_UTILS[i];
      h+='<button class="a3d-ru" title="'+bimEsc(u.label)+'" '+
         (u.menu?('data-a3drumenu="'+u.id+'"'):('data-a3druact="'+u.id+'"'))+'>'+
         A3D_RAIL_ICONS[u.id]+'</button>';
    }
    return h+'</div>';
  }
  function bimEnsureRailStack(){
    var rail=document.getElementById('a3d-rail');
    if(!rail||!A3D.on)return false;
    if(rail.querySelector('#a3d-railutil'))return false;
    var box=document.createElement('div');
    box.innerHTML=bimRailStackHtml();
    rail.appendChild(box.firstChild);
    return true;
  }
  /* ---- the popover ----
     Appended to document.body and positioned in fixed coordinates against the button's own
     rectangle, then CLAMPED to the window. V70 is the reason for the clamp and for the suite that
     measures it: a fixed-position popover inside a transformed ancestor resolves against that
     ancestor, and the dock's carets once opened hundreds of pixels off-screen while every state
     check passed. */
  function bimRailPop(){
    var p=document.getElementById('a3d-rupop');
    if(!p){
      p=document.createElement('div');
      p.id='a3d-rupop';
      document.body.appendChild(p);
      p.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3druitem]'):null;
        if(b){bimRailAction(b.getAttribute('data-a3druitem'));return;}
        /* __acad3dV130: a tool row runs (the document's dispatcher runs it) and the panel goes */
        if(ev.target&&ev.target.closest&&ev.target.closest('.a3d-rkrun[data-a3dr]')){bimCloseRailPop();return;}
        var pn=ev.target&&ev.target.closest?ev.target.closest('[data-rkpin]'):null;
        if(pn){bimToggleDockPin(p,pn.getAttribute('data-rkpin'));return;}
        var kf=ev.target&&ev.target.closest?ev.target.closest('[data-rkkindf]'):null;
        if(kf){
          var kbs=p.querySelectorAll('[data-rkkindf]'),kk;
          for(kk=0;kk<kbs.length;kk++){var kon=kbs[kk]===kf;kbs[kk].classList.toggle('on',kon);kbs[kk].setAttribute('aria-pressed',kon?'true':'false');}
          p.setAttribute('data-rkkind',kf.getAttribute('data-rkkindf'));
          var kfi=p.querySelector('.a3d-rkfind');bimFilterShortcuts(p,kfi?kfi.value:'');
          return;
        }
        /* __acad3dV129: the shortcuts panel's categories and its close button */
        var rc=ev.target&&ev.target.closest?ev.target.closest('.a3d-rkcat[data-rkcat]'):null;
        if(rc){
          var cats=p.querySelectorAll('[data-rkcat]'),ci;
          for(ci=0;ci<cats.length;ci++){var on=cats[ci]===rc;cats[ci].classList.toggle('on',on);cats[ci].setAttribute('aria-pressed',on?'true':'false');}
          p.setAttribute('data-rkcat',rc.getAttribute('data-rkcat'));
          var rf=p.querySelector('.a3d-rkfind');
          bimFilterShortcuts(p,rf?rf.value:'');
          var lst=p.querySelector('.a3d-rukeys');if(lst)lst.scrollTop=0;
          /* a click leaves the typing where it was, in the search box; a key press (Tab, Enter) keeps its place */
          if(ev.detail&&rf){try{rf.focus({preventScroll:true});}catch(eRf){}}
          return;
        }
        if(ev.target&&ev.target.closest&&ev.target.closest('[data-rkclose]')){bimCloseRailPop();return;}
      });
      p.addEventListener('change',function(ev){
        var f=ev.target&&ev.target.closest?ev.target.closest('[data-a3druset]'):null;
        if(f)bimRailSet(f.getAttribute('data-a3druset'),f);
        if(ev.target&&ev.target.classList&&ev.target.classList.contains('a3d-rksort')){   /* __acad3dV130 */
          p.setAttribute('data-rksort',ev.target.value);bimSortShortcuts(p);
        }
      });
      /* __acad3dV128: the shortcut sheet's search box */
      p.addEventListener('input',function(ev){
        if(ev.target&&ev.target.classList&&ev.target.classList.contains('a3d-rkfind'))bimFilterShortcuts(p,ev.target.value);
      });
      p.addEventListener('keydown',function(ev){
        if(!(ev.target&&ev.target.classList&&ev.target.classList.contains('a3d-rkfind'))||ev.key!=='Escape')return;
        ev.preventDefault();ev.stopPropagation();
        if(ev.target.value){ev.target.value='';bimFilterShortcuts(p,'');}
        else{bimCloseRailPop();try{ev.target.blur();}catch(eBl){}}
      });
    }
    return p;
  }
  function bimCloseRailPop(){
    var p=document.getElementById('a3d-rupop');
    if(p)p.classList.remove('open');
    var opened=document.querySelectorAll('#a3d-railutil .a3d-ru.on'),i;
    for(i=0;i<opened.length;i++)opened[i].classList.remove('on');
  }
  function bimRailMenuHtml(id){
    var s,u;
    if(id==='zoom'){
      return '<div class="a3d-ruhd">Zoom</div>'+
        '<button class="a3d-ruitem" data-a3druitem="zoom:extents">Zoom extents</button>'+
        '<button class="a3d-ruitem" data-a3druitem="zoom:selection">Zoom to selection</button>'+
        '<button class="a3d-ruitem" data-a3druitem="zoom:window">Zoom window</button>';
    }
    if(id==='appear'){
      var pres=!!bimPresentModeOn();
      var light=document.body.classList.contains('light-theme');
      return '<div class="a3d-ruhd">Appearance</div>'+
        '<button class="a3d-ruitem'+(pres?'':' on')+'" data-a3druitem="appear:technical">Technical</button>'+
        '<button class="a3d-ruitem'+(pres?' on':'')+'" data-a3druitem="appear:presentation">Presentation</button>'+
        '<div class="a3d-rusep"></div>'+
        '<button class="a3d-ruitem'+(light?'':' on')+'" data-a3druitem="appear:dark">Dark interface</button>'+
        '<button class="a3d-ruitem'+(light?' on':'')+'" data-a3druitem="appear:light">Light interface</button>'+
        '<div class="a3d-rusep"></div>'+   /* __acad3dV129 */
        '<button class="a3d-ruitem'+(bimDockLabelsOn()?' on':'')+'" data-a3druitem="appear:docknames">Tool names on the dock</button>'+
        '<button class="a3d-ruitem'+(bimDockLabelsOn()?'':' on')+'" data-a3druitem="appear:dockicons">Icons only</button>';
    }
    if(id==='snaps'){
      s=A3D_SNAP;
      return '<div class="a3d-ruhd">Snaps</div>'+
        '<label class="a3d-rurow"><input type="checkbox" data-a3druset="snap:point"'+(s.point?' checked':'')+'> Point snap</label>'+
        '<label class="a3d-rurow"><input type="checkbox" data-a3druset="snap:grid"'+(s.grid?' checked':'')+'> Grid snap</label>'+
        '<label class="a3d-rurow"><input type="checkbox" data-a3druset="snap:ortho"'+(s.ortho?' checked':'')+'> Ortho / 15&deg; rotate</label>'+
        '<label class="a3d-rurow">Grid size (m)<input type="number" step="0.1" min="0.05" data-a3druset="snap:size" value="'+s.gridSize+'"></label>';
    }
    if(id==='units'){
      u=A3D_UNITS.key;
      return '<div class="a3d-ruhd">Project units</div>'+
        '<button class="a3d-ruitem'+(u==='m'?' on':'')+'" data-a3druitem="units:m">Metres</button>'+
        '<button class="a3d-ruitem'+(u==='cm'?' on':'')+'" data-a3druitem="units:cm">Centimetres</button>'+
        '<button class="a3d-ruitem'+(u==='mm'?' on':'')+'" data-a3druitem="units:mm">Millimetres</button>'+
        '<label class="a3d-rurow">Decimals<input type="number" step="1" min="0" max="4" data-a3druset="units:dp" value="'+bimUnitDp()+'"></label>';
    }
    if(id==='help')return bimShortcutsHtml();
    return '<div class="a3d-ruhd">'+bimEsc(id)+'</div>';
  }
  function bimPresentModeOn(){return !!A3D.presentMode;}
  /* __acad3dV128: the sheet's search -- a row stays when every word typed is in its keys, its
     label or its group; Ctrl and Cmd read as one */
  function bimFilterShortcuts(p,q){
    var norm=function(s){return String(s).toLowerCase().replace(/cmd|ctrl|control|meta|\u2318/g,'mod');};
    var cat=p.getAttribute('data-rkcat')||'all',note=null;   /* __acad3dV129: the category chosen on the left */
    var kind=p.getAttribute('data-rkkind')||'all',pinnedOnly=cat==='__pinned';   /* __acad3dV130: Tools or Keys, and On the dock */
    if(pinnedOnly)cat='all';
    var words=norm(q).split(/\s+/).filter(function(w){return !!w;}),kids=p.querySelectorAll('.a3d-rukeys > *'),i,grp=null,any=false,shown=0;
    for(i=0;i<kids.length;i++){
      var e=kids[i];
      if(e.classList.contains('a3d-rkgrp')){if(grp){grp.hidden=!any;if(note)note.hidden=!any;}grp=e;note=null;any=false;continue;}
      if(e.classList.contains('a3d-rkgnote')){note=e;continue;}
      if(!e.classList.contains('a3d-rkrow'))continue;
      var hay=norm(e.getAttribute('data-rkhay')||''),ok=(cat==='all'||e.getAttribute('data-rkg')===cat)&&words.every(function(w){return hay.indexOf(w)>=0;});
      if(ok&&kind!=='all'&&e.getAttribute('data-rkkind')!==kind)ok=false;
      if(ok&&pinnedOnly&&e.getAttribute('data-rkpinned')!=='1')ok=false;
      e.hidden=!ok;if(ok){any=true;shown++;}
    }
    if(grp){grp.hidden=!any;if(note)note.hidden=!any;}
    var em=p.querySelector('.a3d-rkempty');if(em)em.hidden=shown>0;
    var sh=p.querySelector('.a3d-rkshown');if(sh)sh.textContent=shown+' shown';   /* __acad3dV130 */
    return shown;
  }
  function bimOpenRailMenu(id,btn){
    var p=bimRailPop();
    var already=p.classList.contains('open')&&p.getAttribute('data-for')===id;
    bimCloseRailPop();
    if(already)return false;
    p.setAttribute('data-for',id);
    p.classList.toggle('a3d-rksheet',id==='help');   /* __acad3dV129: the shortcuts are a panel, centred */
    p.setAttribute('data-rkcat','all');
    p.setAttribute('data-rkkind','all');p.setAttribute('data-rksort','group');   /* __acad3dV130 */
    p.innerHTML=bimRailMenuHtml(id);
    p.classList.add('open');
    btn.classList.add('on');
    var r=btn.getBoundingClientRect();
    // measure AFTER the content is in, then clamp -- the height is not knowable before
    var pw=p.offsetWidth,ph=p.offsetHeight;
    var left=r.right+8,top=r.top+r.height/2-ph/2;
    if(left+pw>window.innerWidth-8)left=Math.max(8,r.left-pw-8);
    if(top+ph>window.innerHeight-8)top=window.innerHeight-8-ph;
    if(top<8)top=8;
    if(id==='help'){left=Math.max(8,(window.innerWidth-pw)/2);top=Math.max(8,(window.innerHeight-ph)/2);}   /* __acad3dV129 */
    p.style.left=Math.round(left)+'px';
    p.style.top=Math.round(top)+'px';
    if(id==='help')bimFilterShortcuts(p,'');   /* __acad3dV130: the count shown */
    var rkf=id==='help'?p.querySelector('.a3d-rkfind'):null;   /* __acad3dV128: ready to type into */
    if(rkf){try{rkf.focus({preventScroll:true});}catch(eFo){}}
    return true;
  }
  function bimRailSet(spec,field){
    var parts=spec.split(':'),grp=parts[0],key=parts[1];
    if(grp==='snap'){
      if(key==='size'){
        var gv=parseFloat(field.value);
        if(!isFinite(gv)||gv<=0){a3dToast('Grid size must be a positive number');return false;}
        A3D_SNAP.gridSize=gv;
      }else{
        var o={};o[key]=!!field.checked;bimSetSnap(o);
      }
      bimSyncSnapPill();paint();saveSoon();
      return true;
    }
    if(grp==='units'&&key==='dp'){bimSetUnits(null,field.value);return true;}
    return false;
  }
  function bimSetSnap(o){
    if(o&&o.hasOwnProperty('point'))A3D_SNAP.point=!!o.point;
    if(o&&o.hasOwnProperty('grid'))A3D_SNAP.grid=!!o.grid;
    if(o&&o.hasOwnProperty('ortho'))A3D_SNAP.ortho=!!o.ortho;
    return {point:A3D_SNAP.point,grid:A3D_SNAP.grid,ortho:A3D_SNAP.ortho};
  }
  function bimSyncSnapPill(){
    try{
      var sp=document.getElementById('acad-snap');
      if(sp)sp.classList.toggle('on',!!A3D_SNAP.point);
      var op=document.getElementById('acad-ortho');
      if(op)op.classList.toggle('on',!!A3D_SNAP.ortho);
      var gp=document.getElementById('acad-grid');
      if(gp)gp.classList.toggle('on',!!A3D_SNAP.grid);
    }catch(eS){}
  }
  function bimRailAction(spec){
    var parts=spec.split(':'),grp=parts[0],key=parts[1];
    if(grp==='zoom'){
      if(key==='extents'){bimCloseRailPop();fitScene();a3dToast('Zoomed to extents');return true;}
      if(key==='selection'){bimCloseRailPop();return bimZoomToSelection();}
      if(key==='window'){bimCloseRailPop();return bimStartZoomWindow();}
    }
    if(grp==='appear'){
      if(key==='docknames'||key==='dockicons'){bimSetDockLabels(key==='docknames');}   /* __acad3dV129 */
      else if(key==='technical'||key==='presentation'){
        A3D.presentMode=(key==='presentation');
        bimSyncPresentPill();
        refreshProps();paint();saveSoon();
      }else{
        var light=(key==='light');
        document.body.classList.toggle('light-theme',light);
        bimThemeStore(light);   /* __acad3dV121b: under the app's own name, and read back at every start */
        paint();
      }
      bimOpenRailMenu('appear',document.querySelector('[data-a3drumenu="appear"]'));
      return true;
    }
    if(grp==='units'){
      bimSetUnits(key,null);
      bimOpenRailMenu('units',document.querySelector('[data-a3drumenu="units"]'));
      return true;
    }
    return false;
  }
