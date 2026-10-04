"""patch_phase150a.py -- V150: a tool palette for a phone and a tablet.

The owner: "improve the UI for the tool panel on the phone and tablet ... a dragable one and able
to expand and contract. Make it clean like how Apple did it. Only key tools like line, mouse ...
only the essential ones."

- In the drawer layouts (a phone, a tablet upright, V149) the dock gives way to a palette: a
  frosted capsule in the manner of Freeform's and the Apple Pencil's -- Select, Pan, Line,
  Rectangle, Circle, Wall, Door, Window, Dimension, Delete, and More (every tool, and the search).
- The tool in use is filled in blue; Select puts the tool away; Pan is a toggle.
- Drag it by its grip anywhere over the drawing. Let go near the left or right edge and it docks
  there, upright; anywhere else it lies flat. Kept where it was left, in this browser.
- The chevron folds it to one round button showing the tool in use; a tap opens it again, and the
  button drags too.
- A phone starts with it upright on the right edge, a tablet flat at the foot of the drawing."""
NAME = 'patch_phase150a.py'
BASE = '2afd8924b9723bd3a771dc885f6c531234fd6222136b97dd150a9074d544f550'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


CSS = r"""
/* __acad3dV150: the tool palette (phone and tablet) */
.a3d-tpal{position:fixed;z-index:9600;display:none;align-items:center;gap:2px;padding:5px;border-radius:24px;background:rgba(38,40,44,.74);
  -webkit-backdrop-filter:saturate(180%) blur(22px);backdrop-filter:saturate(180%) blur(22px);border:.5px solid rgba(255,255,255,.16);
  box-shadow:0 10px 32px rgba(0,0,0,.38),inset 0 .5px 0 rgba(255,255,255,.08);touch-action:none;user-select:none;-webkit-user-select:none;box-sizing:border-box;font-family:Inter,system-ui,-apple-system,sans-serif}
body.a3d-tier-overlay.a3d-mode .a3d-tpal{display:flex}
body.a3d-tier-overlay #a3d-dock{display:none!important}
body.a3d-tier-overlay.a3d-mode:has(#a3d-right.open) .a3d-tpal{display:none}
.a3d-tpal[data-orient="v"]{flex-direction:column}
.a3d-tptools{display:flex;align-items:center;gap:2px;overflow:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;touch-action:pan-x;max-width:calc(100vw - 104px)}
.a3d-tptools::-webkit-scrollbar{display:none}
.a3d-tpal[data-orient="v"] .a3d-tptools{flex-direction:column;touch-action:pan-y;max-width:none;max-height:calc(100vh - var(--a3d-top-h,44px) - 170px)}
.a3d-tpb,.a3d-tpcur,.a3d-tptoggle{border:0;background:transparent;color:#e9ebee;display:grid;place-items:center;padding:0;cursor:pointer;-webkit-tap-highlight-color:transparent}
.a3d-tpb{width:42px;height:42px;flex:0 0 42px;border-radius:14px;transition:background .12s,color .12s}
.a3d-tpb:active{background:rgba(255,255,255,.12)}
.a3d-tpb.on{background:#0a84ff;color:#fff}
.a3d-tpb svg,.a3d-tpcur svg,.a3d-tptoggle svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
.a3d-tpsep{flex:0 0 1px;width:1px;height:24px;margin:0 4px;background:rgba(255,255,255,.16)}
.a3d-tpal[data-orient="v"] .a3d-tpsep{width:24px;height:1px;margin:4px 0}
.a3d-tpgrip{flex:0 0 16px;width:16px;height:42px;display:grid;place-items:center;cursor:grab;color:rgba(255,255,255,.42);border:0;background:transparent;padding:0;touch-action:none}
.a3d-tpgrip svg{width:6px;height:16px;fill:currentColor}
.a3d-tpal[data-orient="v"] .a3d-tpgrip{width:42px;height:16px}
.a3d-tpal[data-orient="v"] .a3d-tpgrip svg{transform:rotate(90deg)}
.a3d-tptoggle{width:30px;height:42px;flex:0 0 30px;color:rgba(255,255,255,.6);border-radius:12px}
.a3d-tpal[data-orient="v"] .a3d-tptoggle{width:42px;height:30px}
.a3d-tptoggle svg{transform:rotate(-90deg)}
.a3d-tpal[data-side="r"] .a3d-tptoggle svg{transform:rotate(180deg)}
.a3d-tpal[data-side="l"] .a3d-tptoggle svg{transform:none}
.a3d-tpcur{display:none;width:50px;height:50px;border-radius:50%;background:#0a84ff;color:#fff;touch-action:none}
.a3d-tpal.min{padding:4px;border-radius:50%}
.a3d-tpal.min .a3d-tptools,.a3d-tpal.min .a3d-tpgrip,.a3d-tpal.min .a3d-tptoggle{display:none}
.a3d-tpal.min .a3d-tpcur{display:grid}
.a3d-tpal.drag{box-shadow:0 18px 44px rgba(0,0,0,.5);transform:scale(1.03)}
body.a3d-tier-overlay:not(.a3d-tier-phone) #a3d-toast{bottom:146px!important}
body.a3d-tier-overlay .a3d-touchlen{bottom:80px}
body.light-theme .a3d-tpal{background:rgba(250,250,252,.8);border-color:rgba(0,0,0,.1);box-shadow:0 10px 30px rgba(0,0,0,.18)}
body.light-theme .a3d-tpb,body.light-theme .a3d-tptoggle{color:#1c1c1e}
body.light-theme .a3d-tpb.on{color:#fff}
body.light-theme .a3d-tpsep{background:rgba(0,0,0,.12)}
body.light-theme .a3d-tpgrip{color:rgba(0,0,0,.35)}
"""
rep("""/* __acad3dV149b: iOS zooms the page in on a field under 16 px""", CSS.strip('\n') + """
/* __acad3dV149b: iOS zooms the page in on a field under 16 px""")

JS = r"""  /* ================= __acad3dV150: the tool palette, on a phone and a tablet =================
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
"""
rep("""  /* the phone's More: the rail's tools, over the tab bar */""", JS + """  /* the phone's More: the rail's tools, over the tab bar */""")

# built with the shell, placed when the layout is chosen
rep("""    bimShellApplyTier();   /* __acad3dV149: the layout for this screen, and the dock's width */""",
    """    bimShellApplyTier();   /* __acad3dV149: the layout for this screen, and the dock's width */
    try{bimTPalBuild();bimTPalPlace();}catch(eTP){console.warn('[BIM] The tool palette could not be built',eTP);}   /* __acad3dV150 */""")
rep("""      if(tr!=='phone')bimShellMore(false);
    }
    bimShellDockW();""", """      if(tr!=='phone')bimShellMore(false);
    }
    bimShellDockW();
    try{bimTPalPlace();}catch(eTP){}   /* __acad3dV150 */""")
# entering the workspace: the canvas has its size only now
rep("""      if(shellEl&&shellEl.classList.contains('collapsed')&&!bimShellOverlay()){   /* __acad3dV149: a drawer stays shut */""",
    """      setTimeout(function(){try{bimTPalPlace();bimTPalSync();}catch(eTP){}},0);   /* __acad3dV150: the palette over the drawing */
      if(shellEl&&shellEl.classList.contains('collapsed')&&!bimShellOverlay()){   /* __acad3dV149: a drawer stays shut */""")

rep("""    {sel:'[data-railmore]',why:'on a phone, shows the rail\\'s tools over the tab bar'},   /* __acad3dV149 */""",
    """    {sel:'[data-railmore]',why:'on a phone, shows the rail\\'s tools over the tab bar'},   /* __acad3dV149 */
    {sel:'[data-tpact]',why:'the palette: a tool, Select, Pan or every tool'},   /* __acad3dV150 */
    {sel:'[data-tpgrip]',why:'the palette\\'s grip: drag to move it'},
    {sel:'[data-tptoggle]',why:'folds the palette to one button'},
    {sel:'[data-tpcur]',why:'the folded palette: tap to open it, drag to move it'},""")

rep("""  var BIM_APP_VERSION={v:'V149',date:'2026-10-04'};   /* __acad3dV149 */""",
    """  var BIM_APP_VERSION={v:'V150',date:'2026-10-04'};   /* __acad3dV150 */""")
rep("""  window.__a3dMapDraft=function(){return A3D_MAP_DRAFT;};""",
    """  window.__a3dMapDraft=function(){return A3D_MAP_DRAFT;};
  /* __acad3dV150: the tool palette */
  window.__a3dToolPal=function(){var p=document.getElementById('a3d-tpal');if(!p)return null;var r=p.getBoundingClientRect(),cs=getComputedStyle(p);
    return {shown:cs.display!=='none',orient:p.getAttribute('data-orient'),min:p.classList.contains('min'),x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),
      active:bimTPalActive(),nav:A3D.navMode,tools:[].map.call(p.querySelectorAll('[data-tpact]'),function(b){return b.getAttribute('data-tpact');}),prefs:bimTPalPrefs()};};
  window.__a3dToolPalAct=function(id){return bimTPalAct(id);};
  window.__a3dToolPalDrop=function(x,y){return bimTPalDrop(x,y);};
  window.__a3dToolPalFold=function(m){return bimTPalFold(m);};
  window.__acad3dV150='toolpalette,essentialtools,activetool,selectputsaway,pantoggle,draggable,edgedock,flat,fold,remembered,dockgivesway,moretools';""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
