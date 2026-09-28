"""patch_phase93c.py -- __acad3dV93: the sketch OUTLINE, everywhere it is consumed.

Law 2, patched as a class. Five consumers took o.pts as the outline of a sketch:

    doPad, doPocket, bimGetFloorProfile, bimFindRoomBoundaryAt, bimObjBounds2D

While the only bulged sketches were ARC (two points, open) and a PLINE carrying arcs, a raw
o.pts was a chord approximation -- wrong, but quietly. A circle stored the DXF way is two
points, and every one of these turns into a hard failure: Pad refuses it for having fewer than
three points, Room cannot find it, and its bounding box spans the horizontal diameter and
nothing above or below it.

bimSketchOutline is the one place that answers 'what shape is this sketch', and it calls
bimFlattenSketch, the same flattener the DXF, SVG, sheet and viewport paths call.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'dbf3dfb9a0dece819ed41faca7dd2eb9acf7604bef80b41c9202ca0be5731eb1'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # the one definition, placed beside sketchCCW which every consumer already pairs it with
    ("""  function doPad(s,h){
    var P=sketchCCW(s.pts);""",
     """  /* __acad3dV93: what shape is this sketch. The ONE answer, so the five consumers that
     each used to read o.pts directly cannot disagree with each other or with what is drawn. */
  function bimSketchOutline(o){
    if(!o||!o.pts)return [];
    return bimFlattenSketch(o)||o.pts;
  }
  function doPad(s,h){
    var P=sketchCCW(bimSketchOutline(s));"""),
    ("""  function doPocket(s,depth){
    var P=sketchCCW(s.pts);""",
     """  function doPocket(s,depth){
    var P=sketchCCW(bimSketchOutline(s));"""),
    ("""    if(o.t==='sketch'){
      var P=sketchCCW(o.pts);
      if(P.length<3)return null;
      return {pts:P,y:o.y};
    }""",
     """    if(o.t==='sketch'){
      var P=sketchCCW(bimSketchOutline(o));   /* __acad3dV93 */
      if(P.length<3)return null;
      return {pts:P,y:o.y};
    }"""),
    ("""      }else if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=3){
        if(Math.abs(o.y-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.pts))candidates.push({pts:o.pts.slice(),y:o.y,sourceType:'sketch',sourceId:o.id});""",
     """      }else if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=2){
        /* __acad3dV93: >=2, because a circle is two vertices. The test and the boundary it
           hands back are both the flattened outline, so a curved sketch encloses a room. */
        if(Math.abs(o.y-y0)>0.5)continue;
        var skOut=bimSketchOutline(o);
        if(skOut.length>=3&&bimPointInPoly(pt,skOut))candidates.push({pts:skOut.slice(),y:o.y,sourceType:'sketch',sourceId:o.id});"""),
    ("""    else if(o.t==='room'||o.t==='sketch')pts=o.pts;""",
     """    else if(o.t==='sketch')pts=bimSketchOutline(o);   /* __acad3dV93 */
    else if(o.t==='room')pts=o.pts;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
