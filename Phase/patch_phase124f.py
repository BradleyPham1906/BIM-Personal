"""patch_phase124f.py -- V124: drag from the library onto the drawing.

The owner: the library is "a way to quickly drag and drop stuff". A tile or row is pressed, dragged
onto the drawing and let go; what it is lands there.

  - A press is not a drag until it moves past the click distance (A3D_GIZ.click, V123's rule): a
    press that does not travel is a click, and does what a click does.
  - While dragging, a small card with the thing's picture and name follows the pointer and is marked
    when it is over the drawing.
  - Let go over the drawing: a model or a block lands at that point on the active level, snapped as
    a click of the family tool is (bimSnapPoint); an annotation is placed there; a material, wall
    type or pattern goes on the object under the pointer (pick, the click's own picking); a template
    opens a new project.
  - Let go anywhere else, or press Escape, and nothing changes; letting go off the drawing says
    where to drop. Escape is read first in the app's own key handler (onKey), which is registered at
    load and stops Escape for whatever is selected: a listener of the drag's own is never reached
    once anything is selected -- the V83 lesson, found again by this phase's suite.
  - The click a browser sends with the release that ends a drag -- the pointer let go over the tile
    it started from -- is the drag's, not a second placement. Only that click: it is dispatched in
    the same turn as the release, so the flag that eats it is cleared by the next turn and a click
    made any time later is a click.

Pointer events, not HTML5 drag and drop, so it works with a finger as well as a mouse: a tile does
not scroll the panel under a finger (touch-action: none), which is what lets it be dragged."""
NAME = 'patch_phase124f.py'
BASE = '1432781931be21f10292839e4afff9ab80204e07030ce146f7019f41489e3374'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


# ---- the drag itself, after the library's refresh
rep("""  /* The pass itself. Idempotent""", r"""  /* ================= __acad3dV124: drag from the library onto the drawing =================
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
    catch(eD){console.warn('[BIM] The drop failed',eD);a3dToast('That could not be placed — see the console');}
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
    if(kind==='material'||kind==='pattern'||kind==='walltype')obj=pick(cx,cy)||null;
    if(!pt&&(kind==='family'||kind==='block'||kind==='note')){
      a3dToast('That point is not on the level: drop it where the drawing is');
      return false;
    }
    return bimAssetAction(spec,{pt:pt,obj:obj});
  }
  /* The pass itself. Idempotent""")

# ---- a click that follows a drag is the drag's, not a second placement
rep("""        var b=cl('[data-a3dassets]');
        if(!b||b.disabled)return;
        ev.preventDefault();ev.stopPropagation();
        try{bimAssetAction(b.getAttribute('data-a3dassets'));}""",
    """        var b=cl('[data-a3dassets]');
        if(!b||b.disabled)return;
        ev.preventDefault();ev.stopPropagation();
        if(A3D_ASDRAG_EAT)return;   /* __acad3dV124: the click sent with the release that ended a drag */
        try{bimAssetAction(b.getAttribute('data-a3dassets'));}""")

# ---- wired once, with the rest of the library
rep("""      shell.addEventListener('input',function(ev){   /* __acad3dV124: the search */""",
    """      shell.addEventListener('pointerdown',bimAssetDragDown,true);   /* __acad3dV124: drag onto the drawing */
      window.addEventListener('pointermove',bimAssetDragMove,true);
      window.addEventListener('pointerup',bimAssetDragUp,true);
      window.addEventListener('pointercancel',function(ev){if(A3D_ASDRAG&&ev.pointerId===A3D_ASDRAG.pid)bimAssetDragEnd();},true);
      shell.addEventListener('input',function(ev){   /* __acad3dV124: the search */""")

# ---- Escape ends a drag first: in the app's own key handler, because that handler is registered at
#      load and stops the key for anything selected -- a listener of the drag's own was never reached
#      once something was selected (V83 recorded the same)
rep("""  function onKey(ev){
    if(!A3D.on)return;
""", """  function onKey(ev){
    if(!A3D.on)return;
    /* __acad3dV124: a drag from the library is the innermost thing Escape can end */
    if(ev.key==='Escape'&&bimAssetDragCancel()){a3dToast('Nothing placed');ev.preventDefault();ev.stopImmediatePropagation();return;}
""")

# ---- the card that follows the pointer
rep(""".a3d-impprev{display:flex;""", """.a3d-astile,.a3d-asrow{user-select:none;-webkit-user-select:none}
.a3d-asghost{position:fixed;z-index:100000;pointer-events:none;display:flex;align-items:center;gap:6px;padding:4px 8px 4px 4px;background:rgba(34,38,43,.94);border:1px solid #46505a;border-radius:7px;color:#dfe4ea;font:11px/1.3 Inter,system-ui,sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.35);opacity:.7}
.a3d-asghost.ok{border-color:#4d86c0;opacity:1}
.a3d-asghost img{width:40px;height:30px;object-fit:contain;background:#1b1f24;border-radius:4px}
.a3d-impprev{display:flex;""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
