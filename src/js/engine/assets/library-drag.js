  /* ================= __acad3dV124: drag from the library onto the drawing =================
     A press is not a drag until it travels past the click distance (V123); a drag ends with a drop
     on the drawing, or with nothing. Pointer events, so a finger drags as a mouse does. */
  var A3D_ASDRAG=null,A3D_ASDRAG_EAT=false;
  /* the click the browser sends with this release, if any, is the drag's: eaten this turn only */
  function bimAssetEatClick(){
    A3D_ASDRAG_EAT=true;
    setTimeout(function(){A3D_ASDRAG_EAT=false;},0);
  }
  function bimAssetDragDown(ev){
    if(ev.button!==0||!A3D.on)return;
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dassets]'):null;
    if(!b||b.disabled)return;
    A3D_ASDRAG={spec:b.getAttribute('data-a3dassets'),src:b,x0:ev.clientX,y0:ev.clientY,pid:ev.pointerId,on:false,ghost:null,cancelled:false};
  }
  /* the drawing under a viewport point, or null: only the model's own canvas takes a drop */
  function bimAssetDropCanvas(x,y){
    var tg=document.elementFromPoint(x,y);
    return (tg&&el.cv&&tg===el.cv)?el.cv:null;
  }
  function bimAssetDragGhostOff(d){
    if(d&&d.ghost&&d.ghost.parentNode)d.ghost.parentNode.removeChild(d.ghost);
    if(d)d.ghost=null;
  }
  function bimAssetDragEnd(){
    var d=A3D_ASDRAG;
    A3D_ASDRAG=null;
    bimAssetDragGhostOff(d);
    return d;
  }
  /* Escape: the card goes and nothing will be placed, but the drag is held until the pointer is let
     go, so that release -- and any click it sends -- does nothing either */
  function bimAssetDragCancel(){
    var d=A3D_ASDRAG;
    if(!d||!d.on)return false;
    bimAssetDragGhostOff(d);
    d.cancelled=true;d.on=false;
    return true;
  }
  function bimAssetDragMove(ev){
    var d=A3D_ASDRAG;
    if(!d||ev.pointerId!==d.pid||d.cancelled)return;
    if(!d.on){
      var dx=ev.clientX-d.x0,dy=ev.clientY-d.y0,cl=A3D_GIZ.click;
      if(dx*dx+dy*dy<=cl*cl)return;
      d.on=true;
      var g=document.createElement('div');
      g.className='a3d-asghost';
      var im=d.src.querySelector('img'),nm=d.src.querySelector('.a3d-asnm');
      g.innerHTML=(im?'<img src="'+im.getAttribute('src')+'" alt="">':'')+'<span>'+bimEsc(nm?nm.textContent:'')+'</span>';
      document.body.appendChild(g);
      d.ghost=g;
    }
    d.ghost.style.left=(ev.clientX+14)+'px';
    d.ghost.style.top=(ev.clientY+14)+'px';
    d.ghost.classList.toggle('ok',!!bimAssetDropCanvas(ev.clientX,ev.clientY));
    ev.preventDefault();
  }
  function bimAssetDragUp(ev){
    var d=A3D_ASDRAG;
    if(!d||ev.pointerId!==d.pid)return;
    bimAssetDragEnd();
    if(d.cancelled){bimAssetEatClick();return;}
    if(!d.on)return;   /* a press that did not travel is a click, and the click does it */
    bimAssetEatClick();
    var cv=bimAssetDropCanvas(ev.clientX,ev.clientY);
    if(!cv){a3dToast('Drop onto the drawing to place it');return;}
    var r=cv.getBoundingClientRect();
    try{bimAssetDropAt(d.spec,ev.clientX-r.left,ev.clientY-r.top);}
    catch(eD){console.warn('[BIM] The drop failed',eD);a3dToast('That could not be placed \u2014 see the console');}
    refreshAssets();
  }
  /* What a drop at canvas point (cx, cy) does: the same action as a click, given where and on what. */
  function bimAssetDropAt(spec,cx,cy){
    var kind=spec.split(':')[0],lvl=bimGetActiveLevel(),y0=lvl?lvl.elev:0;
    var g=groundPoint(cx,cy,y0),pt=null,obj=null;
    if(g){
      var sn=bimSnapPoint([cx,cy],g,{tool:'familyplace',pts:[],y:y0,on:null});
      pt=[sn[0],sn[1]];
    }
    if(kind==='material'||kind==='pattern'||kind==='walltype'||kind==='section')obj=pick(cx,cy)||null;
    if(!pt&&(kind==='family'||kind==='block'||kind==='note'||kind==='asset')){
      a3dToast('That point is not on the level: drop it where the drawing is');
      return false;
    }
    return bimAssetAction(spec,{pt:pt,obj:obj});
  }
  /* The pass itself. Idempotent, and it only touches anything when there is something to fix, so
     the MutationObserver that drives it cannot feed itself. */
  function bimCleanShell(){
    if(!A3D.on)return false;
    var shell=document.getElementById('a3d-shell');
    var panel=document.getElementById('a3d-leftpanel');
    if(!shell||!panel)return false;
    var did=false;
    // The panel's header names the project and its site.
    var t=panel.querySelector('.a3d-projtitle'),s2=panel.querySelector('.a3d-projsub');
    if(t){
      var pn=bimProjectLabel();   /* __acad3dV115: the one derivation of the name */
      if(t.textContent!==pn){t.textContent=pn;did=true;}
    }
    if(s2){
      var site=(A3D.site&&A3D.site.name)||'Site';
      var want='<span>'+bimEsc(site)+'</span><span class="a3d-pill">BIM</span>';
      if(s2.innerHTML!==want){s2.innerHTML=want;did=true;}
    }
    // __acad3dV83: the utility stack is part of the shell the same way the rest of this pass is
    if(bimEnsureRailStack())did=true;
    bimWireRailStack();
    if(shell.dataset.tab==='layers'&&!panel.querySelector('.a3d-layers-wrap')){   /* __acad3dV121 */
      var lbox=document.createElement('div');
      lbox.className='a3d-tabbody a3d-layers-wrap';
      lbox.innerHTML=bimLayersPanelHtml();
      panel.appendChild(lbox);
      did=true;
    }
    if(shell.dataset.tab!=='layers'){
      var lstale=panel.querySelector('.a3d-layers-wrap');
      if(lstale){lstale.parentNode.removeChild(lstale);did=true;}
    }
    if(shell.dataset.tab==='presentation'&&!panel.querySelector('.a3d-pres-wrap')){   /* __acad3dV122 */
      var pbox=document.createElement('div');
      pbox.className='a3d-tabbody a3d-pres-wrap';
      pbox.innerHTML=bimPresPanelHtml();
      panel.appendChild(pbox);
      bimPresThumbsQueue();
      did=true;
    }
    if(shell.dataset.tab!=='presentation'){
      var pstale=panel.querySelector('.a3d-pres-wrap');
      if(pstale){pstale.parentNode.removeChild(pstale);A3D_PRP.edit=null;did=true;}
    }
    if(shell.dataset.tab==='assets'&&!panel.querySelector('.a3d-assets')){
      var box=document.createElement('div');
      box.className='a3d-tabbody a3d-assets-wrap';
      box.innerHTML=bimAssetsHtml();
      panel.appendChild(box);
      did=true;
    }
    if(shell.dataset.tab!=='assets'){
      var stale=panel.querySelector('.a3d-assets-wrap');
      if(stale){stale.parentNode.removeChild(stale);did=true;}
    }
    if(shell.dataset.tab==='analyze'&&!panel.querySelector('.a3d-analyze-wrap')){   /* __acad3dV141; __acad3dV162: the site analysis in it, one list; __acad3dV171c: the workspace's */
      var abox=document.createElement('div');
      abox.className='a3d-tabbody a3d-analyze-wrap a3d-sa-wrap';
      abox.innerHTML=bimAwListHtml();
      bimAnzFilter(abox);   /* __acad3dV148: the search kept from before */
      abox.addEventListener('click',function(ev){
        var b=ev.target&&ev.target.closest?ev.target.closest('[data-anzact]'):null;
        if(!b||b.disabled)return;
        try{bimAnzAct(b.getAttribute('data-anzact'));}catch(eZ){console.warn('[BIM] Analyze',eZ);a3dToast('That did not work - see the console');}
      });
      abox.addEventListener('input',function(ev){
        var s=ev.target;
        if(s&&s.hasAttribute&&s.hasAttribute('data-anzsearch')){A3D_ANZ.q=s.value;bimAnzFilter(abox);}
      });
      abox.addEventListener('keydown',function(ev){
        var s=ev.target;
        if(s&&s.hasAttribute&&s.hasAttribute('data-anzsearch')&&ev.key==='Escape'&&s.value){ev.preventDefault();ev.stopPropagation();s.value='';A3D_ANZ.q='';bimAnzFilter(abox);}
      });
      /* a refresh held for a field being typed in happens when it is left */
      abox.addEventListener('focusout',function(){if(A3D_ANZ.pend)setTimeout(function(){if(A3D_ANZ.pend)bimAnalyzeRefresh();},0);});
      bimSaWire(abox);   /* __acad3dV158 */
      panel.appendChild(abox);
      did=true;
    }
    if(shell.dataset.tab!=='analyze'){
      var astale=panel.querySelector('.a3d-analyze-wrap');
      if(astale){astale.parentNode.removeChild(astale);A3D_ANZ.pend=false;did=true;}
    }
    return did;
  }
  var A3D_SHELL_OBS=null;
  /* __acad3dV113b: the BIM shell builds its own left rail and panel. bimCleanShell is their render
     pass -- the panel's header, the V83 rail stack and the Assets tab -- and it is idempotent, so
     running it on a shell that is already correct changes nothing. */
  /* __acad3dV113c: named A3D_SHELL_ICONS, not A3D_RAIL_ICONS. V83 already owns that name for the
     rail utility stack, and declaring it again here made every one of those buttons render the
     word "undefined". */
  var A3D_SHELL_ICONS={
    /* __acad3dV119: the top button shows and hides the panel, and now looks like it: a sidebar */
    panel:'<rect x="2.5" y="3" width="13" height="12" rx="2"/><path d="M7 3v12"/>',
    /* __acad3dV119: the Project Browser's icon is a tree -- what the panel is -- not a page */
    browser:'<rect x="2.5" y="2.5" width="5" height="3.5" rx="1"/><rect x="9.5" y="7.2" width="6" height="3.2" rx="1"/><rect x="9.5" y="12.3" width="6" height="3.2" rx="1"/><path d="M5 6v7.9h4.5M5 8.8h4.5"/>',
    /* __acad3dV121: three stacked sheets, the Layers tab */
    layers:'<path d="M9 2.5 16 6 9 9.5 2 6z"/><path d="M2 9l7 3.5L16 9"/><path d="M2 12l7 3.5 7-3.5"/>',
    /* __acad3dV122: a screen on a stand with a play mark, the Presentation tab */
    presentation:'<rect x="2.5" y="2.5" width="13" height="9.5" rx="1.5"/><path d="M7.6 5.2v4.1l3.4-2.05z"/><path d="M9 12v3.2M6.2 15.5h5.6"/>',
    assets:'<path d="m9 2 1.8 4.2L15 8l-4.2 1.8L9 14l-1.8-4.2L3 8l4.2-1.8z"/>',
    /* __acad3dV141: bars and a trend, the Analyze tab */
    analyze:'<path d="M2.5 15.5h13"/><path d="M4.5 13V9.5M8 13V6.5M11.5 13V8.5M15 13V4"/><path d="M3.5 7.5 7.5 4l3.5 2.5 4.5-4" stroke-dasharray="1.6 1.4"/>',
    /* __acad3dV158: a pin on a site outline, the Site analysis tab */
    site:'<path d="M2.5 11.5 6 9.5l3.5 1.5 3-1.5 3 1.8v4.2l-3-1.8-3 1.5L6 13.7l-3.5 2z"/><path d="M9 8.6S6.4 6.2 6.4 4.4a2.6 2.6 0 0 1 5.2 0C11.6 6.2 9 8.6 9 8.6z"/>'
  };
  function bimRailIcon(k){return '<svg viewBox="0 0 18 18">'+(A3D_SHELL_ICONS[k]||'')+'</svg>';}
  /* __acad3dV149: which layout the screen gets -- 'phone' (upright, up to 720 px: a tab bar and a
     drawer), 'overlay' (a tablet upright, a phone on its side: the rail and a drawer), 'desktop' */
  var A3D_SHELL_TIER=null,A3D_SHELL_DESK_SHUT=false;
  function bimShellTier(){
    var mm=window.matchMedia;
    if(!mm)return 'desktop';
    if(mm('(max-width:720px) and (orientation:portrait)').matches)return 'phone';
    if(mm('(max-width:720px),(max-height:500px)').matches||mm('(min-width:721px) and (max-width:1024px) and (orientation:portrait)').matches)return 'overlay';
    return 'desktop';
  }
  function bimShellOverlay(){return A3D_SHELL_TIER==='phone'||A3D_SHELL_TIER==='overlay';}
  /* the layout for the screen now: on the way into a drawer layout the panel closes, and on the way
     back it opens as it was */
  function bimShellApplyTier(){
    var sh=document.getElementById('a3d-shell'),tr=bimShellTier(),was=A3D_SHELL_TIER,b=document.body;
    if(!sh||!b)return tr;
    if(tr!==was){
      if(tr!=='desktop'&&(was==='desktop'||was===null)){A3D_SHELL_DESK_SHUT=sh.classList.contains('collapsed');sh.classList.add('collapsed');}
      else if(tr==='desktop'&&was!==null)sh.classList.toggle('collapsed',A3D_SHELL_DESK_SHUT);
      A3D_SHELL_TIER=tr;
      b.classList.toggle('a3d-tier-phone',tr==='phone');
      b.classList.toggle('a3d-tier-overlay',tr!=='desktop');
      if(tr!=='phone')bimShellMore(false);
    }
    bimShellDockW();
    try{bimTPalPlace();}catch(eTP){}   /* __acad3dV150 */
    return tr;
  }
  /* the drawer: open on a tab, or shut; on a computer the panel's own toggle */
  function bimShellDrawer(open,tab){
    var sh=document.getElementById('a3d-shell');
    if(!sh)return false;
    if(open===undefined)open=sh.classList.contains('collapsed');
    if(open){bimShellSetTab(tab||sh.getAttribute('data-tab')||'browser');}
    else{sh.classList.add('collapsed');bimShellDockW();}
    bimShellMore(false);
    return !sh.classList.contains('collapsed');
  }
  /* __acad3dV149b: the on-screen keyboard's height, from the visual viewport (or given, for a test):
     what is fixed to the bottom of the screen sits on it rather than under it */
  function bimKbFit(kb){
    var vv=window.visualViewport,b=document.body;
    if(kb===undefined)kb=vv?Math.max(0,window.innerHeight-vv.height-vv.offsetTop):0;
    kb=Math.round(+kb||0);
    if(kb<80)kb=0;   /* a browser's bar showing and hiding is not a keyboard */
    document.documentElement.style.setProperty('--a3d-kb',kb+'px');
    if(b)b.classList.toggle('a3d-kb-up',kb>0);
    return kb;
  }
