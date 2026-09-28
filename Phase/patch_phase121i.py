"""patch_phase121i.py -- V121: what the suite reads.

The V121 suite asserts on the model, not on the picture: the layer rules answer through the same
functions the panel, the manager and the commands call, and the three questions -- shown, pickable,
selectable -- are read for an object as the drawing reads them. The look a plot draws a sheet's
linework with is read from the paper render itself."""
NAME = 'patch_phase121i.py'
BASE = '6eedf593112c40769b1ba408ce09fdd1e5293df309be36ca19a79eff0c013476'
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
rep("  window.__a3dSetLayer=setActiveLayer;\n", r"""  window.__a3dSetLayer=setActiveLayer;
  /* __acad3dV121: the layer rules, the three questions and the tree, through the functions the panel,
     the manager and the commands call */
  window.__a3dLayerNew=function(opts){var l=bimLayerNew(opts||{});return l?l.id:null;};
  window.__a3dLayerSet=function(id,field,val){return bimLayerSet(id,field,val);};
  window.__a3dLayerDelete=function(id){return bimLayerDelete(id);};
  window.__a3dLayerCurrent=function(id){return bimLayerMakeCurrent(id);};
  window.__a3dObjSetLayer=function(objId,layerId){return bimObjSetLayer(objId,layerId);};
  window.__a3dLayerQ=function(objId){
    var o=objById(objId);
    if(!o)return null;
    var s=bimObjLayerState(o),ly=bimLayerOf(o);
    return {layer:ly?ly.id:null,on:s.on,frozen:s.frozen,locked:s.locked,plot:s.plot,
      shown:bimLayerShown(o),pickable:bimLayerPickable(o),selectable:bimLayerSelectable(o),alpha:bimLayerAlpha(o)};
  };
  window.__a3dLayerTree=function(){return bimLayerTree().map(function(t){return {id:t.ly.id,name:t.ly.name,depth:t.depth};});};
  window.__a3dLinetypes=function(){return JSON.parse(JSON.stringify(BIM_LINETYPES));};
  window.__a3dLineweights=function(){return BIM_LINEWEIGHTS.slice();};
  window.__a3dActiveLayer=function(){return A3D.activeLayer;};
  /* the look a sketch is drawn with on the open sheet's paper, when the sheet is plotted */
  window.__a3dPlotLook=function(objId,pxPerMM){
    var s=bimSheetById(A3D.activeSheetId);
    if(!s)return null;
    A3D.lastLook={};
    bimRenderSheet(s,pxPerMM||SHEET_EXPORT_PXMM,true);
    return window.__a3dLastLook(objId);
  };
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
