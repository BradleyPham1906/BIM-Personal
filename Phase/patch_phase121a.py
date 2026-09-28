"""patch_phase121a.py -- V121: one test per question, asked of a layer and everything above it.

The owner's first panel is Layers: "i should be able to manipulate a table like how autocad do like
linetype, color, hide/show, layer, sub layer, transparency". Before a table can switch anything, the
drawing has to agree on what a switched layer means. It did not. 28 places read a layer's `visible`
and `locked` flags for themselves, and three of them got it wrong:

  - bimAnnotDrawable treated a LOCKED layer as a hidden one. It decides whether a room tag is drawn,
    exported and counted, so locking a layer made its room tags disappear from the canvas, the SVG,
    the DXF and every sheet -- and the room's own label came back, since its room no longer counted
    as tagged. Locked means displayed and not modified; it is the picking that stops.
  - bimSnapCandidates asked nothing: a line or wall on a hidden layer went on offering its corners
    as snap points, so new geometry pulled to things that were not on screen. The construction
    lines beside it did ask.
  - no sub-layer could exist, because nothing looked above a layer.

AutoCAD's definitions (Layer Properties Manager and SELECT, AutoCAD 2024 help) are the ones used:
  On      off: not displayed, not plotted; still in the drawing's extents, and still taken by
          SELECT ALL, whose documented rule leaves out only frozen and locked layers.
  Freeze  frozen: not displayed, not plotted, not regenerated, not in the extents, never selected.
  Lock    locked: displayed (faded), snapped to, plotted; not selected or modified.
  Plot    no-plot: displayed, not plotted.
A sub-layer is off, frozen, locked or no-plot when any layer above it is (Rayon nests layers;
AutoCAD groups them).

Three questions, each asked in one place: bimLayerShown(o) -- is it drawn, snapped to, traced and
measured (and, in a plot, plotted); bimLayerPickable(o) -- can a click, a window or a list row pick
it; bimLayerSelectable(o) -- does SELECT ALL take it. All 28 sites ask the first two. Layers are
read tolerantly (a layer without `frozen` is thawed), so an older acad3dV1 loads unchanged."""
NAME = 'patch_phase121a.py'
BASE = '91e664dbde3634599c0d020a7d9b63a41bca67e306c28d714ef2bee40c6acb1f'
import re
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
# ---- 1. the two questions, and what they are asked of
rep("""  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }
""", r"""  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }
  /* ================= __acad3dV121: what a layer's switches mean, asked in one place =================

     A layer is {id, name, color, visible, locked} since V6; V121 adds frozen, plot, linetype,
     lineweight, transparency, description and parent. Every flag is read tolerantly -- a layer
     without `frozen` is thawed, one without `plot` plots -- so an older acad3dV1 needs no migration.

     AutoCAD's meanings (Layer Properties Manager and SELECT, AutoCAD 2024 help):
       On (visible)  off: not displayed and not plotted; still in the drawing's extents, and still
                     selected by SELECT ALL, whose documented rule leaves out only frozen and
                     locked layers.
       Freeze        frozen: not displayed, not plotted, not regenerated, not in the extents, not
                     selected by anything.
       Lock          locked: displayed faded, snapped to and plotted; not selected or modified.
       Plot          no-plot: displayed, not plotted.
     A sub-layer is off, frozen, locked or no-plot when any layer above it is.

     Three questions, each asked in one place:
       bimLayerShown(o)       drawn, snapped to, traced, measured -- and, in a plot, plotted
       bimLayerPickable(o)    picked by a click, a window or a list row: shown and unlocked
       bimLayerSelectable(o)  taken by SELECT ALL and every select-by-criteria: thawed and unlocked
     Before V121, 28 sites read the flags for themselves. */
  /* A plot in progress: `on` while a plot or an export is being drawn -- a no-plot layer is left
     out and a locked layer is not faded, as AutoCAD plots them; `pres` when it is a presentation,
     the one kind that draws a layer's transparency; `pxmm`, the paper's pixels per millimetre while
     a sheet is painted, which linetypes and lineweights are drawn at. */
  var A3D_PLOT={on:false,pres:false,pxmm:0};
  function bimLayerById(id){
    var i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return null;
  }
  /* The layer and every layer above it, nearest first. A parent that is missing ends the chain, and
     one already seen ends it too, so a loop in stored data cannot hang a paint. */
  function bimLayerChain(ly){
    var out=[],seen={},c=ly;
    while(c&&!seen[c.id]){
      seen[c.id]=1;out.push(c);
      c=(typeof c.parent==='string'&&c.parent)?bimLayerById(c.parent):null;
    }
    return out;
  }
  function bimLayerEff(ly){
    var s={on:true,frozen:false,locked:false,plot:true},ch=bimLayerChain(ly),i;
    for(i=0;i<ch.length;i++){
      if(ch[i].visible===false)s.on=false;
      if(ch[i].frozen)s.frozen=true;
      if(ch[i].locked)s.locked=true;
      if(ch[i].plot===false)s.plot=false;
    }
    return s;
  }
  function bimObjLayerState(o){
    var ly=bimLayerOf(o);
    return ly?bimLayerEff(ly):{on:true,frozen:false,locked:false,plot:true};
  }
  function bimLayerShown(o){
    var s=bimObjLayerState(o);
    return s.on&&!s.frozen&&(s.plot||!A3D_PLOT.on);
  }
  function bimLayerPickable(o){
    var s=bimObjLayerState(o);
    return s.on&&!s.frozen&&!s.locked;
  }
  /* AutoCAD's ALL: everything except frozen and locked layers -- a layer that is off included,
     which is why AutoCAD's users freeze a layer rather than turn it off when it must stay out of
     a selection. Whoever selects this way says how many of the selection cannot be seen. */
  function bimLayerSelectable(o){
    var s=bimObjLayerState(o);
    return !s.frozen&&!s.locked;
  }
""")

# ---- 2. the 28 sites
SHOWN = "   /* __acad3dV121 */\n"
rep("      var lyr=bimLayerOf(o);\n      if(lyr&&lyr.visible===false)continue;\n",
    "      if(!bimLayerShown(o))continue;" + SHOWN, 12)
rep("      lyr=bimLayerOf(o);\n      if(lyr&&lyr.visible===false)continue;\n",
    "      if(!bimLayerShown(o))continue;" + SHOWN, 2)
rep("    var drawn=[],i,j,k,s,o,lyr,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg;\n",
    "    var drawn=[],i,j,k,s,o,tin,step,cs,sel,sp,a,b,c,best,bl,L,txt,ang,nseg;\n")
rep("    var out=[],i,k,o,q,v,w,top,lyr;\n", "    var out=[],i,k,o,q,v,w,top;\n")
rep("      var lyr=bimLayerOf(o);\n      if(lyr&&(lyr.visible===false||lyr.locked))continue;\n",
    "      if(!bimLayerPickable(o))continue;" + SHOWN, 7)
rep("    var lyr=bimLayerOf(o);\n    if(lyr&&lyr.visible===false)return null;\n",
    "    if(!bimLayerShown(o))return null;" + SHOWN)
rep("      var lyr=bimLayerOf(o);\n      if(lyr&&(lyr.visible===false||lyr.locked))return false;\n",
    "      if(!bimLayerPickable(o))return false;" + SHOWN)
rep("      var lyr=bimLayerOf(ob);\n      if(lyr&&lyr.visible===false)continue;\n",
    "      if(!bimLayerShown(ob))continue;" + SHOWN, 2)
rep("lock:!!(lyr&&lyr.locked)", "lock:!bimLayerPickable(ob)", 2)
rep("var lyr=bimLayerOf(o);if(lyr&&lyr.visible===false)continue;",
    "if(!bimLayerShown(o))continue;   /* __acad3dV121 */", 2)

# ---- 3. a locked layer's annotation is drawn; it is the picking that stops
rep("    var lyr=bimLayerOf(o);\n    if(lyr&&(lyr.visible===false||lyr.locked))return false;\n",
    "    /* __acad3dV121: shown, not pickable -- a locked layer is drawn. This read `locked` as hidden,\n"
    "       and it decides whether a room tag is drawn, exported and counted: locking a layer took its\n"
    "       tags off the canvas, the exports and every sheet, and brought the rooms' own labels back.\n"
    "       Picking asks bimLayerPickable below. */\n"
    "    if(!bimLayerShown(o))return false;\n")
rep("      if(o.t!==t||!bimAnnotDrawable(o))continue;\n",
    "      if(o.t!==t||!bimAnnotDrawable(o)||!bimLayerPickable(o))continue;   /* __acad3dV121 */\n")

# ---- 4. nothing snaps to what is not drawn
rep("      if(skip&&skip.indexOf(o.id)>=0)continue;   /* __acad3dV112 */\n",
    "      if(skip&&skip.indexOf(o.id)>=0)continue;   /* __acad3dV112 */\n"
    "      if(!bimLayerShown(o))continue;   /* __acad3dV121: a hidden layer's corners were snap targets */\n")
rep("          if(bimIsCline(t))continue;\n",
    "          if(bimIsCline(t)||!bimLayerShown(t))continue;   /* __acad3dV121 */\n")

# ---- 5. the extents leave out frozen layers, as AutoCAD's do (an off layer stays in them)
rep("      var o=list[i],m=meshOf(o),q=bimObjOffset(o);\n",
    "      var o=list[i],m=meshOf(o),q=bimObjOffset(o);\n"
    "      if(!ids&&bimObjLayerState(o).frozen)continue;   /* __acad3dV121 */\n")

# ---- nothing reads the flags for itself any more
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
if re.search(r'lyr\s*&&\s*\(?\s*lyr\.(visible|locked)', code):
    sys.exit('ABORT: a site still reads a layer flag for itself')
callers = len(re.findall(r'(?<![\w.])bimLayerOf\(', code)) - 1
if callers != 1:
    sys.exit('ABORT: bimLayerOf has %d callers besides the state lookup, expected 1' % callers)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
