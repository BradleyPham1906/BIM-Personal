  /* ================= __acad3dV150: the tool palette, on a phone and a tablet =================
     The essential tools in a capsule over the drawing, dragged where the hand wants them, folded
     to one button when the drawing wants the room. Where it was left is kept in this browser. */
  var BIM_TPAL_KEY='acad3dToolPal';
  function bimTPalIc(p){return '<svg viewBox="0 0 24 24" aria-hidden="true">'+p+'</svg>';}
  var BIM_TPAL_TOOLS=[
    {id:'select',label:'Select',ic:bimTPalIc('<path d="M6 3.5 18.5 12l-5.6 1.2 3.3 6.1-2.3 1.2-3.2-6.1L6 18.4z"/>')},
    {id:'pan',label:'Pan',ic:bimTPalIc('<path d="M8.5 12V6.2a1.5 1.5 0 0 1 3 0V11M11.5 10.5V4.7a1.5 1.5 0 0 1 3 0v5.8M14.5 10.6V6.3a1.5 1.5 0 0 1 3 0v7.2c0 4-2.6 6.9-6.2 6.9-2.6 0-4.1-1.1-5.4-3.4l-2-3.7c-.5-1 .7-2 1.6-1.3L8.5 15"/>')},
    {sep:1},
    {id:'s:line',label:'Line',ic:bimTPalIc('<path d="M5 19 19 5"/><circle cx="5" cy="19" r="1.6"/><circle cx="19" cy="5" r="1.6"/>')},
    {id:'s:rect',label:'Rectangle',ic:bimTPalIc('<rect x="4" y="6" width="16" height="12" rx="1.5"/>')},
    {id:'s:circle',label:'Circle',ic:bimTPalIc('<circle cx="12" cy="12" r="7.5"/>')},
    {sep:1},
    {id:'bim:wall',label:'Wall',ic:bimTPalIc('<path d="M3.5 8.5h17v7h-17z"/><path d="M8 8.5v7M12.5 8.5v7M17 8.5v7"/>')},
    {id:'bim:door',label:'Door',ic:bimTPalIc('<path d="M4 20h16"/><path d="M6 20V5h7v15"/><path d="M13 5c4.2.6 6 4.3 6 8"/><circle cx="11" cy="12.5" r=".6"/>')},
    {id:'bim:window',label:'Window',ic:bimTPalIc('<rect x="4.5" y="4.5" width="15" height="15" rx="1.5"/><path d="M12 4.5v15M4.5 12h15"/>')},
    {sep:1},
    {id:'bim:dim',label:'Dimension',ic:bimTPalIc('<path d="M4 9v6M20 9v6M4 12h16"/><path d="m7 10-3 2 3 2M17 10l3 2-3 2"/>')},
    {id:'m:del',label:'Delete',ic:bimTPalIc('<path d="M5 7h14M9.5 7V5h5v2M7 7l1 12.5h8L17 7"/>')},
    {sep:1},
    {id:'more',label:'All tools',ic:bimTPalIc('<circle cx="6" cy="12" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="18" cy="12" r="1.4"/>')}
  ];
  var BIM_TPAL_SKTOOL={line:'s:line',poly:'s:line',rect:'s:rect',circle:'s:circle',wall:'bim:wall',door:'bim:door',window:'bim:window',dim:'bim:dim'};
  var A3D_TPAL={drag:null,active:'select'};
  function bimTPalPrefs(){try{var v=JSON.parse(localStorage.getItem(BIM_TPAL_KEY)||'null');return v&&typeof v==='object'?v:{};}catch(eP){return {};}}
  function bimTPalSave(p){try{localStorage.setItem(BIM_TPAL_KEY,JSON.stringify(p));}catch(eS){}}
  function bimTPalTool(id){var i;for(i=0;i<BIM_TPAL_TOOLS.length;i++)if(BIM_TPAL_TOOLS[i].id===id)return BIM_TPAL_TOOLS[i];return null;}
  function bimTPalHtml(){
    var h='<button type="button" class="a3d-tpgrip" data-tpgrip="1" aria-label="Move the tools" title="Drag to move">'+
      '<svg viewBox="0 0 6 16"><circle cx="1.5" cy="2" r="1.3"/><circle cx="4.5" cy="2" r="1.3"/><circle cx="1.5" cy="8" r="1.3"/><circle cx="4.5" cy="8" r="1.3"/><circle cx="1.5" cy="14" r="1.3"/><circle cx="4.5" cy="14" r="1.3"/></svg></button>'+
      '<div class="a3d-tptools">';
    BIM_TPAL_TOOLS.forEach(function(x){
      h+=x.sep?'<span class="a3d-tpsep" aria-hidden="true"></span>':
        '<button type="button" class="a3d-tpb" data-tpact="'+x.id+'" aria-label="'+x.label+'" title="'+x.label+'" aria-pressed="false">'+x.ic+'</button>';
    });
    return h+'</div><button type="button" class="a3d-tptoggle" data-tptoggle="1" aria-label="Fold the tools away" aria-expanded="true">'+
      bimTPalIc('<path d="m14.5 6-6 6 6 6"/>')+'</button>'+
      '<button type="button" class="a3d-tpcur" data-tpcur="1" aria-label="Open the tools" aria-expanded="false"></button>';
  }
  /* the tool in use: a drawing tool, else Pan when panning, else Select */
  function bimTPalActive(){
    var sk=A3D.sk,a=sk&&sk.tool?BIM_TPAL_SKTOOL[sk.tool]:null;
    if(a)return a;
    return A3D.navMode==='pan'?'pan':'select';
  }
  function bimTPalSync(){
    var p=document.getElementById('a3d-tpal');
    if(!p)return null;
    var a=bimTPalActive(),B=p.querySelectorAll('[data-tpact]'),i,on,cur;
    A3D_TPAL.active=a;
    for(i=0;i<B.length;i++){on=B[i].getAttribute('data-tpact')===a;B[i].classList.toggle('on',on);B[i].setAttribute('aria-pressed',String(on));}
    cur=p.querySelector('[data-tpcur]');
    if(cur&&cur.getAttribute('data-for')!==a){var tl=bimTPalTool(a)||bimTPalTool('select');cur.innerHTML=tl.ic;cur.setAttribute('data-for',a);cur.setAttribute('aria-label','Open the tools ('+tl.label+' in use)');}
    return a;
  }
  /* where the drawing is, to keep the palette over it */
  function bimTPalArea(){
    var c=document.getElementById('a3d-canvas'),r=c?c.getBoundingClientRect():null;
    if(!r||!r.width)return {l:0,t:60,r:window.innerWidth,b:window.innerHeight-60};
    return {l:r.left,t:r.top,r:r.right,b:r.bottom};
  }
  /* place it from the kept spot: x and y are fractions of the drawing area, side 'l'/'r' when docked */
  function bimTPalPlace(){
    var p=document.getElementById('a3d-tpal');
    if(!p||!bimShellOverlay())return null;
    var pr=bimTPalPrefs(),k=A3D_SHELL_TIER,s=pr[k]||null,A=bimTPalArea(),m=8,w,h,x,y;
    if(!s)s=k==='phone'?{side:'r',fy:0.42}:{side:null,fx:0.5,fy:1};
    p.setAttribute('data-orient',s.side?'v':'h');p.setAttribute('data-side',s.side||'');
    p.classList.toggle('min',!!pr.min);
    w=p.offsetWidth;h=p.offsetHeight;
    if(s.side==='l')x=A.l+m;
    else if(s.side==='r')x=A.r-w-m;
    else x=A.l+(A.r-A.l-w)*(isFinite(s.fx)?s.fx:0.5);
    y=A.t+(A.b-A.t-h)*(isFinite(s.fy)?s.fy:1);
    x=Math.max(A.l+m,Math.min(A.r-w-m,x));y=Math.max(A.t+m,Math.min(A.b-h-m,y));
    p.style.left=Math.round(x)+'px';p.style.top=Math.round(y)+'px';
    return {x:x,y:y,w:w,h:h,side:s.side||null};
  }
  /* let go at a point: near a side it docks there upright, anywhere else it lies flat */
  function bimTPalDrop(cx,cy){
    var p=document.getElementById('a3d-tpal');
    if(!p)return null;
    var A=bimTPalArea(),pr=bimTPalPrefs(),k=A3D_SHELL_TIER||'phone',s,w,h,edge=Math.min(72,(A.r-A.l)*0.18);
    if(cx<A.l+edge)s={side:'l'};else if(cx>A.r-edge)s={side:'r'};else s={side:null};
    p.setAttribute('data-orient',s.side?'v':'h');
    w=p.offsetWidth;h=p.offsetHeight;
    s.fx=Math.max(0,Math.min(1,(cx-w/2-A.l)/Math.max(1,A.r-A.l-w)));
    s.fy=Math.max(0,Math.min(1,(cy-h/2-A.t)/Math.max(1,A.b-A.t-h)));
    pr[k]=s;bimTPalSave(pr);
    return bimTPalPlace();
  }
  function bimTPalFold(min){
    var pr=bimTPalPrefs();
    pr.min=min===undefined?!pr.min:!!min;
    bimTPalSave(pr);
    var p=document.getElementById('a3d-tpal'),tg=p&&p.querySelector('[data-tptoggle]'),cu=p&&p.querySelector('[data-tpcur]');
    if(tg)tg.setAttribute('aria-expanded',String(!pr.min));
    if(cu)cu.setAttribute('aria-expanded',String(!pr.min));
    bimTPalPlace();
    return pr.min;
  }
  function bimTPalAct(id){
    if(id==='select'){
      if(A3D.sk){try{document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));}catch(eE){}if(A3D.sk)cancelSketch();}
      if(A3D.navMode==='pan')setNav('orbit');
    }else if(id==='pan'){
      setNav(A3D.navMode==='pan'?'orbit':'pan');
    }else if(id==='more'){
      setTimeout(bimOpenToolsPanel,0);   /* after this tap: the panel shuts on a click outside it, and this tap is one */
    }else{
      if(A3D.navMode==='pan')setNav('orbit');
      bimRunAct(id);
    }
    bimTPalSync();
    return bimTPalActive();
  }
  function bimTPalBuild(){
    if(document.getElementById('a3d-tpal'))return false;
    var p=document.createElement('div');
    p.id='a3d-tpal';p.className='a3d-tpal';p.setAttribute('role','toolbar');p.setAttribute('aria-label','Tools');
    p.innerHTML=bimTPalHtml();
    document.body.appendChild(p);
    var moved=false;
    p.addEventListener('pointerdown',function(ev){
      var g=ev.target.closest('[data-tpgrip],[data-tpcur]');
      if(!g)return;
      var r=p.getBoundingClientRect();
      A3D_TPAL.drag={id:ev.pointerId,dx:ev.clientX-r.left,dy:ev.clientY-r.top,x0:ev.clientX,y0:ev.clientY};
      moved=false;
      try{g.setPointerCapture(ev.pointerId);}catch(eC){}
      ev.preventDefault();
    });
    p.addEventListener('pointermove',function(ev){
      var d=A3D_TPAL.drag;
      if(!d||ev.pointerId!==d.id)return;
      if(!moved&&Math.abs(ev.clientX-d.x0)+Math.abs(ev.clientY-d.y0)<6)return;
      moved=true;p.classList.add('drag');
      p.style.left=Math.round(ev.clientX-d.dx)+'px';p.style.top=Math.round(ev.clientY-d.dy)+'px';
    });
    function up(ev){
      var d=A3D_TPAL.drag;
      if(!d||ev.pointerId!==d.id)return;
      A3D_TPAL.drag=null;p.classList.remove('drag');
      if(moved){
        /* the edge is judged by where the finger lets go; the spot by the palette's middle */
        var r=p.getBoundingClientRect(),A=bimTPalArea(),edge=Math.min(72,(A.r-A.l)*0.18);
        bimTPalDrop(ev.clientX<A.l+edge?A.l:ev.clientX>A.r-edge?A.r:r.left+r.width/2,r.top+r.height/2);
      }
      else if(ev.target.closest&&ev.target.closest('[data-tpcur]'))bimTPalFold(false);   /* a tap on the folded button opens it */
    }
    p.addEventListener('pointerup',up);
    p.addEventListener('pointercancel',up);
    p.addEventListener('click',function(ev){
      var b=ev.target.closest('[data-tpact]');
      if(b){bimTPalAct(b.getAttribute('data-tpact'));return;}
      if(ev.target.closest('[data-tptoggle]'))bimTPalFold(true);
    });
    /* the tool in use follows whatever ended or changed it: a tap on the drawing, Esc, a command */
    var pend=false;
    function later(){if(pend)return;pend=true;setTimeout(function(){pend=false;bimTPalSync();},60);}
    document.addEventListener('pointerup',later,true);
    document.addEventListener('keyup',later,true);
    document.addEventListener('click',later,true);
    window.addEventListener('resize',function(){bimTPalPlace();});
    bimTPalSync();
    return true;
  }
  /* the phone's More: the rail's tools, over the tab bar */
  function bimShellMore(on){
    var b=document.body,m=document.querySelector('#a3d-rail [data-railmore]');
    if(!b)return false;
    if(on===undefined)on=!b.classList.contains('a3d-railutil-open');
    on=!!on&&A3D_SHELL_TIER==='phone';
    b.classList.toggle('a3d-railutil-open',on);
    if(m){m.classList.toggle('on',on);m.setAttribute('aria-expanded',String(on));}
    return on;
  }
  /* __acad3dV166b: the left panel's width, remembered, and its edge -- dragged, double-clicked back,
     or moved from the keyboard as the W3C's window splitter is (role separator, its value, the arrow
     keys, Home and End, Enter to shut the panel). A computer's, and a tablet's on its side: a phone's
     and an upright tablet's drawer keeps its width, as Properties' sheet and drawer do. */
  var BIM_LEFT_KEY='acad3dLeftPanel',BIM_LEFT_MIN=242,BIM_LEFT_MAX=560,BIM_LEFT_KEEP=320,BIM_LEFT_RAIL=54;
  function bimLeftPrefs(){try{var v=JSON.parse(localStorage.getItem(BIM_LEFT_KEY)||'null');return v&&typeof v==='object'?v:{};}catch(eL){return {};}}
  function bimLeftSave(p){try{localStorage.setItem(BIM_LEFT_KEY,JSON.stringify(p));}catch(eW){}}
  /* the widest it may be now: the drawing keeps BIM_LEFT_KEEP px beside Properties, where Properties
     sits beside the drawing rather than over it */
  function bimLeftMax(){
    var rp=document.getElementById('a3d-right'),rw=0,cs;
    if(rp){cs=getComputedStyle(rp);if(cs.display!=='none'&&cs.position!=='absolute'&&cs.position!=='fixed')rw=rp.getBoundingClientRect().width;}
    return Math.max(BIM_LEFT_MIN,Math.min(BIM_LEFT_MAX,Math.floor((window.innerWidth||0)-BIM_LEFT_RAIL-rw-BIM_LEFT_KEEP)));
  }
  /* the width the panel gets: the one kept, within what the screen allows now; the one kept stays */
  function bimLeftW(){var p=bimLeftPrefs();return typeof p.w==='number'&&isFinite(p.w)?Math.max(BIM_LEFT_MIN,Math.min(bimLeftMax(),Math.round(p.w))):BIM_LEFT_MIN;}
  function bimLeftSetWidth(w){
    var p=bimLeftPrefs();
    if(w===null)delete p.w;
    else{w=+w;if(!isFinite(w))return bimLeftState();p.w=Math.round(Math.max(BIM_LEFT_MIN,Math.min(bimLeftMax(),w)));}
    bimLeftSave(p);bimShellDockW();   /* the drawing follows by its own ResizeObserver (V72) */
    return bimLeftState();
  }
  /* the next width up, within what the screen allows; from the widest, back to the narrowest */
  var BIM_LEFT_STEPS=[242,320,400,480,560];
  function bimLeftNext(){
    var w=bimLeftW(),mx=bimLeftMax(),i;
    for(i=0;i<BIM_LEFT_STEPS.length;i++)if(BIM_LEFT_STEPS[i]>w&&BIM_LEFT_STEPS[i]<=mx)return BIM_LEFT_STEPS[i];
    return w<mx?mx:BIM_LEFT_MIN;
  }
  function bimLeftStep(){return bimLeftSetWidth(bimLeftNext());}
  function bimLeftState(){
    var pn=document.getElementById('a3d-leftpanel'),g=document.getElementById('a3d-lgrip'),p=bimLeftPrefs();
    return {w:pn?Math.round(pn.getBoundingClientRect().width):0,set:bimLeftW(),kept:typeof p.w==='number'?p.w:null,min:BIM_LEFT_MIN,max:bimLeftMax(),
      grip:!!(g&&getComputedStyle(g).display!=='none'),next:bimLeftNext(),tier:A3D_SHELL_TIER,dock:getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim()};
  }
  function bimLeftWire(sh){
    if(!sh||document.getElementById('a3d-lgrip'))return;
    var g=document.createElement('div'),dr=null,root=document.documentElement;
    g.id='a3d-lgrip';g.className='a3d-lgrip';g.tabIndex=0;g.title='Drag to resize; double-click to put it back';
    g.setAttribute('role','separator');g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-leftpanel');g.setAttribute('aria-label','Panel width');
    sh.appendChild(g);
    g.addEventListener('pointerdown',function(ev){
      if(A3D_SHELL_TIER!=='desktop'||ev.button>0)return;
      ev.preventDefault();
      dr={x:ev.clientX,w:bimLeftW(),id:ev.pointerId,now:null};
      try{g.setPointerCapture(ev.pointerId);}catch(eC){}
      g.classList.add('drag');document.body.classList.add('a3d-lpdrag');
    });
    g.addEventListener('pointermove',function(ev){
      if(!dr||ev.pointerId!==dr.id)return;
      var w=Math.round(Math.max(BIM_LEFT_MIN,Math.min(bimLeftMax(),dr.w+ev.clientX-dr.x)));
      if(w===dr.now)return;
      dr.now=w;
      root.style.setProperty('--a3d-lp-w',w+'px');root.style.setProperty('--a3d-left-w',(BIM_LEFT_RAIL+w)+'px');
    });
    function end(ev,keep){
      if(!dr||ev.pointerId!==dr.id)return;
      var w=dr.now;dr=null;
      g.classList.remove('drag');document.body.classList.remove('a3d-lpdrag');
      if(keep&&w!==null)bimLeftSetWidth(w);else bimShellDockW();   /* a cancelled drag puts it back */
    }
    g.addEventListener('pointerup',function(ev){end(ev,true);});
    g.addEventListener('pointercancel',function(ev){end(ev,false);});
    g.addEventListener('dblclick',function(){bimLeftSetWidth(null);});
    g.addEventListener('keydown',function(ev){
      var k=ev.key,st=ev.shiftKey?64:16;
      if(k==='ArrowLeft'||k==='ArrowRight'){ev.preventDefault();bimLeftSetWidth(bimLeftW()+(k==='ArrowRight'?st:-st));return;}
      if(k==='Home'||k==='End'){ev.preventDefault();bimLeftSetWidth(k==='Home'?BIM_LEFT_MIN:bimLeftMax());return;}
      if(k==='Enter'){
        ev.preventDefault();
        sh.classList.add('collapsed');bimShellDockW();
        var t=sh.querySelector('#a3d-rail .a3d-paneltoggle');if(t)t.focus();   /* Enter on it opens the panel again */
      }
    });
    bimShellDockW();
  }
  function bimShellDockW(){
    try{
      var sh=document.getElementById('a3d-shell'),w=bimLeftW(),g=document.getElementById('a3d-lgrip');
      document.documentElement.style.setProperty('--a3d-lp-w',w+'px');   /* __acad3dV166b */
      document.documentElement.style.setProperty('--a3d-left-w',
        A3D_SHELL_TIER==='phone'?'0px':A3D_SHELL_TIER==='overlay'?'54px':   /* __acad3dV149: a drawer leaves the drawing where it is */
        (sh&&sh.classList.contains('collapsed'))?'54px':(BIM_LEFT_RAIL+w)+'px');
      if(g){g.setAttribute('aria-valuenow',String(w));g.setAttribute('aria-valuemin',String(BIM_LEFT_MIN));g.setAttribute('aria-valuemax',String(bimLeftMax()));}
      var b=document.querySelector('#a3d-leftpanel [data-lpwidth]'),nx=bimLeftNext();
      if(b){b.setAttribute('aria-label','Panel width '+w+' px: '+(nx>w?'widen to '+nx:'back to '+nx));b.title=b.getAttribute('aria-label');}
    }catch(eW){console.warn('[BIM] Dock width could not be set',eW);}
  }
  function bimShellSetTab(t){
    var sh=document.getElementById('a3d-shell'),was;
    if(!sh)return false;
    was=sh.getAttribute('data-tab');
    sh.classList.remove('collapsed');
    sh.setAttribute('data-tab',t);
    var btns=sh.querySelectorAll('#a3d-rail .a3d-railbtn[data-tab]'),i;
    for(i=0;i<btns.length;i++)
      btns[i].classList.toggle('active',btns[i].getAttribute('data-tab')===t);
    bimShellDockW();
    try{bimCleanShell();}
    catch(eT){console.warn('[BIM] Shell tab render failed',eT);a3dToast('That panel could not be drawn');}
    bimAwTab(t,was);   /* __acad3dV171c: Analyze is the workspace, opened and left with its tab */
    return true;
  }
  function bimBuildShell(){
    var old=document.getElementById('a3d-shell');
    if(old)return old;
    var sh=document.createElement('aside');
    sh.id='a3d-shell';
    sh.setAttribute('data-tab','browser');
    sh.innerHTML='<nav id="a3d-rail">'+
      '<button type="button" class="a3d-paneltoggle" data-toggle title="Show or hide the panel" aria-label="Show or hide the panel">'+bimRailIcon('panel')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="layers" data-short="Layers" title="Layers" aria-label="Layers">'+   /* __acad3dV121 */
      bimRailIcon('layers')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="presentation" data-short="Present" title="Presentation" aria-label="Presentation">'+   /* __acad3dV122 */
      bimRailIcon('presentation')+'</button>'+
      '<button type="button" class="a3d-railbtn active" data-tab="browser" data-short="Browser" title="Project Browser" aria-label="Project Browser">'+
      bimRailIcon('browser')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="assets" data-short="Assets" title="Assets" aria-label="Assets">'+
      bimRailIcon('assets')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="analyze" data-short="Analyze" title="Analyze" aria-label="Analyze">'+   /* __acad3dV141 */
      bimRailIcon('analyze')+'</button>'+
      '<div class="a3d-railspacer"></div>'+
      '<button type="button" class="a3d-railmore" data-railmore="1" data-short="More" title="More: zoom, appearance, snaps, units, save image, shortcuts" aria-label="More" aria-expanded="false">'+   /* __acad3dV149 */
      '<svg viewBox="0 0 18 18"><circle cx="4" cy="9" r="1.3"/><circle cx="9" cy="9" r="1.3"/><circle cx="14" cy="9" r="1.3"/></svg></button>'+
      '</nav>'+
      '<div id="a3d-shellscrim" data-toggle="1" aria-hidden="true"></div>'+
      '<section id="a3d-leftpanel">'+
      '<div class="a3d-projhead"><div><div class="a3d-projtitle">Untitled project</div>'+
      '<div class="a3d-projsub"><span>Site</span><span class="a3d-pill">BIM</span></div></div>'+
      '<div class="a3d-projbtns"><button type="button" class="a3d-lpwbtn" data-lpwidth="1">'+   /* __acad3dV166b: the width, by one press */
      '<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M2.5 9h13M5.5 6 2.5 9l3 3M12.5 6l3 3-3 3"/></svg></button>'+
      '<button type="button" class="a3d-panelcollapse" data-toggle title="Collapse the panel">\u2039</button></div></div>'+
      '</section>';
    document.body.appendChild(sh);
    sh.addEventListener('click',function(ev){
      var mo=ev.target&&ev.target.closest?ev.target.closest('[data-railmore]'):null;   /* __acad3dV149 */
      if(mo){bimShellMore();return;}
      if(ev.target&&ev.target.closest&&ev.target.closest('[data-lpwidth]')){bimLeftStep();return;}   /* __acad3dV166b */
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-toggle]'):null;
      if(tg){sh.classList.toggle('collapsed');bimShellDockW();bimShellMore(false);return;}
      var tb=ev.target&&ev.target.closest?ev.target.closest('.a3d-railbtn[data-tab]'):null;
      if(tb){
        /* __acad3dV149: in a drawer layout the open tab's button shuts the drawer */
        if(bimShellOverlay()&&!sh.classList.contains('collapsed')&&sh.getAttribute('data-tab')===tb.getAttribute('data-tab')){bimShellDrawer(false);return;}
        bimShellSetTab(tb.getAttribute('data-tab'));
        bimShellMore(false);
      }
    });
    /* __acad3dV149: the layout follows the screen; More shuts when something else is touched; Esc
       shuts an open drawer */
    window.addEventListener('resize',function(){bimShellApplyTier();});
    /* __acad3dV149b: the keyboard, and the field it would cover */
    if(window.visualViewport){
      window.visualViewport.addEventListener('resize',function(){bimKbFit();});
      window.visualViewport.addEventListener('scroll',function(){bimKbFit();});
    }
    document.addEventListener('focusin',function(ev){
      var f=ev.target;
      if(!bimShellOverlay()||!f||!f.matches||!f.matches('input,select,textarea'))return;
      setTimeout(function(){bimKbFit();try{f.scrollIntoView({block:'center',inline:'nearest'});}catch(eSI){}},280);
    });
    document.addEventListener('focusout',function(){setTimeout(function(){bimKbFit();},300);});
    document.addEventListener('pointerdown',function(ev){
      if(!document.body.classList.contains('a3d-railutil-open'))return;
      var x=ev.target;
      if(x&&x.closest&&(x.closest('#a3d-rail')||x.closest('#a3d-rupop')))return;
      bimShellMore(false);
    },true);
    document.addEventListener('keydown',function(ev){
      if(ev.key!=='Escape'||!bimShellOverlay()||sh.classList.contains('collapsed'))return;
      var a=document.activeElement;
      if(a&&(a.tagName==='INPUT'||a.tagName==='TEXTAREA'||a.tagName==='SELECT'))return;
      bimShellDrawer(false);
    });
    bimWireLayersPanel(sh.querySelector('#a3d-leftpanel'));   /* __acad3dV121 */
    bimWirePresPanel(sh.querySelector('#a3d-leftpanel'));     /* __acad3dV122 */
    bimLeftWire(sh);   /* __acad3dV166b */
    bimShellApplyTier();   /* __acad3dV149: the layout for this screen, and the dock's width */
    try{bimTPalBuild();bimTPalPlace();}catch(eTP){console.warn('[BIM] The tool palette could not be built',eTP);}   /* __acad3dV150 */
    try{bimCleanShell();}
    catch(eB){console.warn('[BIM] Shell first render failed',eB);}
    return sh;
  }
  function bimWatchShell(){
    bimBuildShell();   /* __acad3dV113b: the shell is ours, so build it before watching it */
    var panel=document.getElementById('a3d-leftpanel');
    if(!panel||A3D_SHELL_OBS||typeof MutationObserver==='undefined')return false;
    bimCleanShell();
    A3D_SHELL_OBS=new MutationObserver(function(){
      if(A3D_SHELL_CLEANING)return;
      A3D_SHELL_CLEANING=true;
      try{bimCleanShell();}catch(eC){console.warn('[BIM] Shell cleanup failed',eC);}
      A3D_SHELL_CLEANING=false;
    });
    A3D_SHELL_OBS.observe(panel,{childList:true,subtree:false});
    /* __acad3dV85: the RAIL is watched too. It is a SIBLING of the panel, not a child, so a
       rail re-render never fired this observer and the rail stack was not put back. */
    var railEl=document.getElementById('a3d-rail');
    if(railEl)A3D_SHELL_OBS.observe(railEl,{childList:true,subtree:false});
    var shell=document.getElementById('a3d-shell');
    if(shell&&!shell.__a3dAssetsWired){
      shell.__a3dAssetsWired=true;
      shell.addEventListener('click',function(ev){
        var cl=function(s){return ev.target&&ev.target.closest?ev.target.closest(s):null;};
        /* __acad3dV124: the library's own controls */
        var ab=cl('[data-a3dasact]'),db=cl('[data-a3dasdel]'),gh=cl('[data-a3dassetgrp]');
        if(ab||db||gh){
          ev.preventDefault();ev.stopPropagation();
          try{
            if(ab&&!ab.disabled)bimAssetsAct(ab.getAttribute('data-a3dasact'));
            else if(db)bimAssetRemove(db.getAttribute('data-a3dasdel'));
            else if(gh){var gid=gh.getAttribute('data-a3dassetgrp');A3D_ASSETS_UI.closed[gid]=!A3D_ASSETS_UI.closed[gid];refreshAssets();}
          }catch(eL){console.warn('[BIM] Library action failed',eL);a3dToast('That library action failed \u2014 see the console');}
          return;
        }
        var b=cl('[data-a3dassets]');
        if(!b||b.disabled)return;
        ev.preventDefault();ev.stopPropagation();
        if(A3D_ASDRAG_EAT)return;   /* __acad3dV124: the click sent with the release that ended a drag */
        try{bimAssetAction(b.getAttribute('data-a3dassets'));}
        catch(eA){console.warn('[BIM] Asset action failed',eA);a3dToast('That asset action failed \u2014 see the console');}
        refreshAssets();
      },true);
      shell.addEventListener('pointerdown',bimAssetDragDown,true);   /* __acad3dV124: drag onto the drawing */
      window.addEventListener('pointermove',bimAssetDragMove,true);
      window.addEventListener('pointerup',bimAssetDragUp,true);
      window.addEventListener('pointercancel',function(ev){if(A3D_ASDRAG&&ev.pointerId===A3D_ASDRAG.pid)bimAssetDragEnd();},true);
      shell.addEventListener('input',function(ev){   /* __acad3dV124: the search */
        var s=ev.target&&ev.target.matches&&ev.target.matches('[data-a3dassearch]')?ev.target:null;
        if(!s)return;
        A3D_ASSETS_UI.q=s.value;
        refreshAssets();
      });
      shell.addEventListener('keydown',function(ev){
        var tg=ev.target;
        if(tg&&tg.matches&&tg.matches('[data-a3dassearch]')&&ev.key==='Escape'&&tg.value){
          ev.preventDefault();ev.stopPropagation();tg.value='';A3D_ASSETS_UI.q='';refreshAssets();
          return;
        }
        if(tg&&tg.matches&&tg.matches('[data-a3dassetgrp]')&&(ev.key==='Enter'||ev.key===' ')){
          ev.preventDefault();ev.stopPropagation();tg.click();
        }
      },true);
    }
    return true;
  }
  var A3D_SHELL_CLEANING=false;
  /* __acad3dV119: with nothing to fit, the framing goes back to the default and the direction stays --
     an empty plan is still a plan. fitScene used to open the Home view here, a switch to 3D: Fit to
     Model in an empty plan swung the camera into 3D, and a section aimed at an empty model turned
     into a 3D view. */
  function bimFrameNothing(){
    var c=A3D.cam;
    c.dist=DEFCAM.dist;c.tx=DEFCAM.tx;c.ty=DEFCAM.ty;c.tz=DEFCAM.tz;
    paint();saveSoon();
  }
  function fitScene(){
    /* __acad3dV79: this used to centre the model on the CANVAS and size it to the canvas, which
       put the bottom of every fitted model directly behind the tool dock -- and with it any
       grip or gizmo arm down there. It now frames into the rectangle handles can be clicked in.
       It also fits sketches and rooms, which have no mesh and which the old loop skipped
       entirely, so a drawing made only of sketches fit to nothing at all. */
    var bb=bimWorldBounds(null);
    if(!bb){bimFrameNothing();return;}
    bimFrameBounds(bb);
  }
