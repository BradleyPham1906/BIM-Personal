"""patch_phase97h.py -- __acad3dV97: a click never changes geometry, and a stale grip is dead.

Found by the V88 regression suite, which failed two checks this phase broke: after drawing an
ARC and deselecting it, a click on the arc's apex -- to select it -- added a vertex to it. Two
separate faults produced that, and each is worth naming:

1. A STALE GRIP WAS STILL LIVE. bimPickGrip matched against A3D.grips, the list built during the
   LAST paint. Deselecting without a repaint left the previous selection's grips in that list,
   and a press on the spot where one had been drawn acted on an object that was no longer
   selected. Pre-existing for vertex grips, but invisible until midpoint grips put a grip
   exactly where a user clicks to select a curve -- its apex. A grip now counts only for the
   object that is selected right now.

2. A PRESS INSERTED THE VERTEX. The midpoint grip inserted on mousedown, so a plain click with no
   drag changed the drawing. "Drag a midpoint grip to add a vertex" means no drag, no vertex:
   the insert is now pending until the drag actually moves, and a click that goes up where it
   went down leaves the sketch exactly as it was. The undo snapshot is taken at the insert, not
   the press, so a click does not leave an empty undo step behind either.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '81c8ce08079407ee6594566d05032b9016d961bb6d02ee7cfa6eb99f74a08098'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # 1. a grip counts only for the current selection
    ("""  function bimPickGrip(x,y){
    if(!A3D.grips)return null;
    var i,best=null,bestD=8;
    for(i=0;i<A3D.grips.length;i++){
      var g=A3D.grips[i],dx=g.x-x,dy=g.y-y,d=Math.sqrt(dx*dx+dy*dy);""",
     """  function bimPickGrip(x,y){
    if(!A3D.grips)return null;
    var i,best=null,bestD=8;
    for(i=0;i<A3D.grips.length;i++){
      var g=A3D.grips[i];
      /* __acad3dV97: A3D.grips is whatever the LAST paint drew. After a selection change with
         no repaint in between, it still holds the previous object's grips, and a press there
         acted on an object that was no longer selected. Only the selection's grips are live. */
      if(g.objId!==A3D.sel)continue;
      var dx=g.x-x,dy=g.y-y,d=Math.sqrt(dx*dx+dy*dy);"""),

    # 2a. the press only arms the insert
    ("""        pushUndo();
        var mo=objById(grip.objId);
        var ins=mo?bimInsertSketchVertex(mo,grip.seg,bimSketchSegMid(mo,grip.seg)):{error:'That sketch no longer exists'};
        if(ins.error){a3dToast('Add vertex: '+ins.error);ev.preventDefault();return;}
        bimPropagateFrom([mo.id],'rebuild');
        drag={grip:true,objId:grip.objId,idx:ins.idx,kind:'sketch',elev:grip.elev,moved:false};
        refreshProps();paint();saveSoon();
        ev.preventDefault();
        return;""",
     """        /* The press only ARMS the insert. No drag, no vertex: a click that goes up where it
           went down must leave the sketch exactly as it was. */
        drag={grip:true,objId:grip.objId,idx:-1,kind:'sketch',elev:grip.elev,moved:false,
              pendingMid:{seg:grip.seg}};
        ev.preventDefault();
        return;"""),

    # 2b. the first real movement performs it, then the drag carries on as a vertex drag
    ("""    if(drag.grip){
      var g0=groundPoint(xy[0],xy[1],drag.elev);
      if(!g0)return;""",
     """    if(drag.grip){
      if(drag.pendingMid){   /* __acad3dV97: the drag moved, so now the vertex is added */
        var pmo=objById(drag.objId);
        var pins=pmo?bimInsertSketchVertex(pmo,drag.pendingMid.seg,bimSketchSegMid(pmo,drag.pendingMid.seg))
                    :{error:'That sketch no longer exists'};
        drag.pendingMid=null;
        if(pins.error){a3dToast('Add vertex: '+pins.error);drag=null;paint();return;}
        pushUndo();
        drag.idx=pins.idx;
        refreshProps();
      }
      var g0=groundPoint(xy[0],xy[1],drag.elev);
      if(!g0)return;"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
