"""patch_phase121e.py -- V121: every object is on a layer.

Building the Layers panel showed a wall listed under the Model layer that had been made on A-WALL.
Nine of the ways an object is made never gave it a layer -- walls, columns, floors, pads, pockets,
property lines, imported sketches and faces, copied rooms -- and bimLayerOf reads a missing layer as
the CURRENT one. So each of those objects was on whichever layer happened to be current: make another
layer current and every wall went with it; make an off layer current and every wall disappeared;
lock the current layer and none of them could be picked. The same held for every object in a project
saved before this phase.

Rather than a tenth fix at each of nine places (and the next place someone writes), the layer is
given where every change already passes: saveSoon adopts, onto the current layer, any object without
one -- the layer it was made on, since every maker calls saveSoon at once -- and an object whose layer
no longer exists onto the first layer, which is what bimLayerOf already read it as. A stored project
is adopted as it loads, onto the layer that was current when it was saved: the one its layerless
objects were being drawn as, so nothing changes on screen."""
NAME = 'patch_phase121e.py'
BASE = '42e296489cb72e9ead89e617632c38de7467d3d5cd798e749f3d2a39fcc7f32d'
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
rep("  function saveSoon(){\n",
    r"""  /* __acad3dV121: every object is on a layer. An object without one is adopted by the current layer
     -- the layer it was made on, since every maker calls saveSoon at once -- and one whose layer no
     longer exists by the first layer, which is what bimLayerOf reads it as. Nine makers never gave
     an object a layer, and a missing layer read as the CURRENT one: every wall followed whichever
     layer was current, out of sight when it was off and out of reach when it was locked. */
  function bimAdoptLayers(){
    var ids={},i,o,n=0,cur=bimLayerById(A3D.activeLayer)||A3D.layers[0],first=A3D.layers[0];
    if(!cur||!first)return 0;
    for(i=0;i<A3D.layers.length;i++)ids[A3D.layers[i].id]=1;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(typeof o.layer!=='string'||!o.layer){o.layer=cur.id;n++;}
      else if(!ids[o.layer]){o.layer=first.id;n++;}
    }
    return n;
  }
  function saveSoon(){
    bimAdoptLayers();   /* __acad3dV121 */
""")
rep("        if(A3D.classifications.length!==st.classifications.length)console.warn('[BIM] Discarded malformed classification(s) from '+LSK+' storage.');\n      }\n  }\n",
    "        if(A3D.classifications.length!==st.classifications.length)console.warn('[BIM] Discarded malformed classification(s) from '+LSK+' storage.');\n      }\n"
    "      /* __acad3dV121: an older project's layerless objects join the layer that was current when it\n"
    "         was saved -- the one they were being drawn as, so nothing changes on screen */\n"
    "      try{bimAdoptLayers();}\n"
    "      catch(eAd){console.warn('[BIM] Objects could not be given their layers; they follow the current one until the next save.',eAd);}\n"
    "  }\n")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
