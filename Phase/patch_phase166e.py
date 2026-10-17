"""patch_phase166e.py -- V166b: the left panel is sized by its edge, as Properties is.

  the edge     dragged (a mouse, a pen or a finger), 242 to 560 px, the drawing keeping 320 px beside
               Properties; a double click puts it back; remembered in this browser
  the keys     the edge is the W3C's window splitter: a separator with its value, Left and Right move
               it (Shift, further), Home and End to the narrowest and the widest, Enter shuts the panel
  where        a computer's, and a tablet's on its side: a phone's and an upright tablet's drawer keeps
               its width, as Properties' sheet and drawer do
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'a1441cdee986ad30d000b44f68657540689f57d8b16aafbae51dfa3677c77106'   # after patch_phase166d.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimAnzFrameHtml(){' in txt, 'run patch_phase166d.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- the width is a variable; the edge ----
rep("""#a3d-leftpanel{width:242px;height:100%;""", """#a3d-leftpanel{width:var(--a3d-lp-w,242px);height:100%;""")
rep("""#a3d-shell.collapsed #a3d-leftpanel{width:0;opacity:0;border-right:0}
""", """#a3d-shell.collapsed #a3d-leftpanel{width:0;opacity:0;border-right:0}
/* __acad3dV166b: the panel's edge, dragged to size it as Properties' is; inside the panel, so the
   drawing beside it keeps every pixel */
.a3d-lgrip{position:absolute;top:0;bottom:0;left:calc(var(--a3d-left-w,296px) - 6px);width:6px;cursor:col-resize;z-index:4;pointer-events:auto;touch-action:none;outline:0}
.a3d-lgrip:hover,.a3d-lgrip.drag,.a3d-lgrip:focus-visible{background:linear-gradient(90deg,transparent 2px,#4ea1ff 2px,#4ea1ff 4px,transparent 4px)}
#a3d-shell.collapsed .a3d-lgrip,body.a3d-tier-overlay .a3d-lgrip{display:none}
body.a3d-lpdrag #a3d-leftpanel{transition:none}
body.a3d-lpdrag,body.a3d-lpdrag *{cursor:col-resize!important;user-select:none;-webkit-user-select:none}
@media(pointer:coarse){
.a3d-lgrip{width:12px;left:calc(var(--a3d-left-w,296px) - 12px);background:linear-gradient(90deg,transparent 8px,rgba(255,255,255,.16) 8px,rgba(255,255,255,.16) 10px,transparent 10px)}
.a3d-lgrip.drag{background:linear-gradient(90deg,transparent 7px,#4ea1ff 7px,#4ea1ff 10px,transparent 10px)}
body.light-theme .a3d-lgrip:not(.drag){background:linear-gradient(90deg,transparent 8px,rgba(0,0,0,.14) 8px,rgba(0,0,0,.14) 10px,transparent 10px)}
}
""")

# ---- the width, and the dock's ----
rep("""  function bimShellDockW(){
    try{
      var sh=document.getElementById('a3d-shell');
      document.documentElement.style.setProperty('--a3d-left-w',
        A3D_SHELL_TIER==='phone'?'0px':A3D_SHELL_TIER==='overlay'?'54px':   /* __acad3dV149: a drawer leaves the drawing where it is */
        (sh&&sh.classList.contains('collapsed'))?'54px':'296px');
    }catch(eW){console.warn('[BIM] Dock width could not be set',eW);}
  }
""", """  /* __acad3dV166b: the left panel's width, remembered, and its edge -- dragged, double-clicked back,
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
    bimLeftSave(p);bimShellDockW();
    try{size();paint();}catch(eS){console.warn('[BIM] The drawing could not be resized',eS);}
    return bimLeftState();
  }
  function bimLeftState(){
    var pn=document.getElementById('a3d-leftpanel'),g=document.getElementById('a3d-lgrip'),p=bimLeftPrefs();
    return {w:pn?Math.round(pn.getBoundingClientRect().width):0,set:bimLeftW(),kept:typeof p.w==='number'?p.w:null,min:BIM_LEFT_MIN,max:bimLeftMax(),
      grip:!!(g&&getComputedStyle(g).display!=='none'),tier:A3D_SHELL_TIER,dock:getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim()};
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
      try{size();paint();}catch(eS){}
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
    }catch(eW){console.warn('[BIM] Dock width could not be set',eW);}
  }
""")
rep("""    bimWirePresPanel(sh.querySelector('#a3d-leftpanel'));     /* __acad3dV122 */
""", """    bimWirePresPanel(sh.querySelector('#a3d-leftpanel'));     /* __acad3dV122 */
    bimLeftWire(sh);   /* __acad3dV166b */
""")
# Properties widened or minimised: the left panel keeps the drawing its room
rep("""    if(b){b.setAttribute('aria-pressed',p.min?'true':'false');b.title=p.min?'Show the Properties panel':'Minimise the Properties panel';}
    return {w:rp.getBoundingClientRect().width,min:!!p.min};
""", """    if(b){b.setAttribute('aria-pressed',p.min?'true':'false');b.title=p.min?'Show the Properties panel':'Minimise the Properties panel';}
    bimShellDockW();   /* __acad3dV166b: the left panel keeps the drawing its room */
    return {w:rp.getBoundingClientRect().width,min:!!p.min};
""")
# a focused edge owns its keys, as a dropdown does: the model does not nudge, the search does not open
rep("""    if(tg.tagName==='SELECT')return !(ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key));
    return false;
  }
""", """    if(tg.tagName==='SELECT')return !(ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key));
    if(tg.getAttribute&&tg.getAttribute('role')==='separator'&&tg.tabIndex>=0)return !(ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key));   /* __acad3dV166b */
    return false;
  }
""")

# ---- hooks and the marker ----
rep("""  window.__a3dRightPanel=function(){var r=bimRightApply();return r;};   /* __acad3dV147 */
""", """  window.__a3dRightPanel=function(){var r=bimRightApply();return r;};   /* __acad3dV147 */
  window.__a3dLeftPanel=function(){return bimLeftState();};   /* __acad3dV166b */
  window.__a3dSetLeftWidth=function(w){return bimLeftSetWidth(w);};
""")
rep("""  window.__acad3dV166='""", """  window.__acad3dV166b='noanalysistab,usagesonproject,anzframe,anzfloorloads,anzareas,anzfields,anzsearchsettings,leftresize,leftremembered,leftreset,leftkeys,leftclamp,leftdesktop';
  window.__acad3dV166='""")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('patch_phase166e applied:', hashlib.sha256(out).hexdigest(), len(out))
