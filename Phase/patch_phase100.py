"""patch_phase100.py -- __acad3dV100: ending a drawing command keeps what was drawn.

REPORTED IN V99 (found while writing its suite): Escape during LINE threw away every segment
already drawn. cancelSketch() discards the whole point list, and it was the only way out.
AutoCAD's rule is the opposite: each LINE segment exists the moment its second point is
clicked, so Escape (or starting another command, or changing view) ends LINE with the segments
kept; PLINE ends as an open polyline; a wall chain keeps the walls placed.

Measured, same class (law 2):
  * Escape                      -> discarded LINE, PLINE and WALL in progress
  * switching plan / 3D          -> toggleFlat() called cancelSketch(): discarded
  * starting another command     -> every starter overwrote A3D.sk: discarded
  * Enter in PLINE               -> CLOSED the polyline, and with two points made nothing.
                                    AutoCAD: Enter ends PLINE OPEN; Close is C, or clicking the
                                    first point. The start toast even documented the wrong rule.

One function, bimEndSketch, now decides what an interruption keeps, and every exit calls it:
Escape, the plan/3D switch, and bimEnterDraftingMode (which every tool starter calls first),
plus the Section starter, which is the one starter that does not. The keep rule is derived
from the same finishers Enter uses, so Escape and Enter cannot disagree about what a command
with N points produces.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '8af95338f952a262f251877329a4714476270ff1a830d19f48d201433e4543ff'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""  function cancelSketch(){A3D.sk=null;paint();}""",
     """  function cancelSketch(){A3D.sk=null;paint();}
  /* ================= __acad3dV100: ending a command keeps what was drawn =================
     Which in-progress commands have something worth keeping: a LINE, PLINE or WALL with at
     least one complete segment. Everything else (an arc with two of its three points, a
     rectangle with one corner, a pick tool) has nothing complete and is simply ended. */
  function bimSketchKeepable(sk){
    return !!(sk&&sk.pts&&sk.pts.length>=2&&(sk.tool==='line'||sk.tool==='poly'||sk.tool==='wall'));
  }
  /* The one way a command is interrupted -- Escape, a view change, another command starting.
     Keeps through the SAME finisher Enter uses, so the two cannot produce different things. */
  function bimEndSketch(){
    var sk=A3D.sk;
    if(!sk)return false;
    try{
      if(bimSketchKeepable(sk))bimFinishCurrent();
      else cancelSketch();
    }catch(eE){
      console.warn('[BIM] Ending the command failed; the points drawn were not kept.',eE);
      a3dToast('The command could not be ended cleanly - see the console');
      A3D.sk=null;paint();
    }
    bimSyncStatusHint();
    return true;
  }"""),
    ("""  function bimEnterDraftingMode(){
    if(A3D.section)bimExitSection();""",
     """  function bimEnterDraftingMode(){
    if(A3D.sk)bimEndSketch();   /* __acad3dV100: a new command ends the old one, keeping it */
    if(A3D.section)bimExitSection();"""),
    ("""    if(A3D.sk)cancelSketch();
    if(A3D.flat){""",
     """    if(A3D.sk)bimEndSketch();   /* __acad3dV100: a view change used to discard the drawing */
    if(A3D.flat){"""),
    ("""      if(A3D.sk){cancelSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}""",
     """      if(A3D.sk){bimEndSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}   /* __acad3dV100 */"""),
    ("""  function startSectionTool(){
    closeDlg();""",
     """  function startSectionTool(){
    closeDlg();
    if(A3D.sk)bimEndSketch();   /* __acad3dV100: the one starter that skips bimEnterDraftingMode */"""),
    ("""  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice(),{bulges:sk.bulges});   /* __acad3dV90 */
  }""",
     """  /* __acad3dV100: open is AutoCAD's Enter -- the polyline ends where it is, and two points
     are a valid polyline. Closed (no argument) is Close: C, or clicking the first point. */
  function finishPoly(open){
    var sk=A3D.sk;if(!sk)return null;
    if(open){
      if(sk.pts.length<2)return null;
      var ob=sk.bulges?sk.bulges.slice(0,sk.pts.length-1):null;
      return addSketchObj(sk.pts.slice(),{bulges:ob,closed:false,
        toast:'Polyline created, open, '+(sk.pts.length-1)+' segment'+(sk.pts.length===2?'':'s')});
    }
    if(sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice(),{bulges:sk.bulges});   /* __acad3dV90 */
  }"""),
    ("""    else if(sk.tool==='poly'){if(sk.pts.length>=3)finishPoly();else{A3D.sk=null;paint();}}""",
     """    else if(sk.tool==='poly'){if(sk.pts.length>=2)finishPoly(true);else{A3D.sk=null;paint();}}   /* __acad3dV100: Enter ends it OPEN */"""),
    ("""(tool==='poly'?'; click the first point again or press Enter to close':'')""",
     """(tool==='poly'?'; C or click the first point to close, Enter to leave it open':'')"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
