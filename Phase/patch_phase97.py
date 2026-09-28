"""patch_phase97.py -- __acad3dV97: one answer to "where is this source's boundary".

A room, floor, ceiling, roof or hatch built on a sketch or a closed wall depends on that source's
boundary. Before this phase that boundary was read in THREE different ways -- raw o.pts, the
flattened outline, innerLoop -- in local coordinates at creation and in world coordinates on
re-measure. Each mismatch was a separate bug, and the user found them by editing a sketch and
watching the room not follow:

  - a CURVED sketch (a V93 circle is two vertices) failed the re-measure's `pts.length<3` check,
    so the room stayed where it was and a "could not be re-measured" toast appeared;
  - a sketch that had been MOVED before the room was made could not be picked at all, because
    creation tested the click against local coordinates while the sketch was drawn in world
    coordinates -- the V75 bug, in a place the V75 fix never reached;
  - a room moved TOGETHER with its sketch kept its link, then re-measured into world coordinates
    and was drawn with its own pos added on top -- so it landed twice as far away as it should.

bimSourceBoundaryWorld is now the only function that reads a source's boundary. It returns the
flattened ring (what a room or slab needs), the raw vertices and bulges (what a hatch needs, so
it stays curve-exact), and the plane -- all in WORLD coordinates. Every dependent converts into
its OWN frame by subtracting its own offset, so no path can add a pos twice.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'f9de9dcd2458cc5d4bd8e5dcb704cdd20de498685645bf033a551e5be2a7c5fa'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

# --- 1. the contract, placed directly before the room re-measure that is its first client
OLD_HEAD = """  function bimRemeasureRoomFromSource(room,ctx){"""
NEW_HEAD = """  /* ================= __acad3dV97: the source contract =================

     The ONE reader of a boundary source. Everything built on a sketch or a closed wall -- room,
     floor, ceiling, roof, hatch -- gets its boundary from here, at creation and on every change
     after, so the two can no longer disagree about which points, which curve, or which frame.

     Returned in WORLD coordinates. A dependent converts into its own frame by subtracting its
     own offset (bimToFrame), which is the step whose absence doubled a moved room's offset. */
  function bimSourceBoundaryWorld(src){
    if(!src)return {error:'its source no longer exists'};
    var q=bimObjOffset(src),ring,pts,bulges=null,y;
    if(src.t==='sketch'&&!bimIsPoint(src)){
      if(src.closed===false)return {error:'its source sketch is no longer closed'};
      ring=bimSketchOutline(src);
      if(!ring||ring.length<3)return {error:'its source sketch has too few points'};
      pts=src.pts;bulges=bimHasBulge(src.bulges)?src.bulges.slice():null;
      y=(src.y||0)+q[1];
    }else if(src.t==='solid'&&src.bim&&src.bim.type==='wall'){
      if(!src.bim.closed||!src.bim.innerLoop||src.bim.innerLoop.length<3)
        return {error:'its source wall is no longer a closed loop'};
      ring=src.bim.innerLoop;pts=ring;
      y=(src.bim.baseY||0)+q[1];
    }else if(src.t==='room'&&src.pts&&src.pts.length>=3){
      /* a room is itself a boundary, so a hatch can be built on one and follow it -- a chain the
         graph orders correctly because a room is always visited before what depends on it */
      ring=src.pts;pts=ring;
      y=(src.y||0)+q[1];
    }else{
      return {error:'its source is not a closed boundary'};
    }
    function w(p){return [p[0]+q[0],p[1]+q[2]];}
    var outRing=ring.map(w);
    if(!(bimPolyArea(outRing)>1e-6))return {error:'its source boundary has no area'};
    return {ring:outRing,pts:pts.map(w),bulges:bulges,y:y,
            type:(src.t==='solid'?'wall':src.t),id:src.id};
  }
  /* World points into a dependent's own frame. */
  function bimToFrame(o,pts){
    var q=bimObjOffset(o);
    return pts.map(function(p){return [p[0]-q[0],p[1]-q[2]];});
  }
  function bimRemeasureRoomFromSource(room,ctx){"""
assert txt.count(OLD_HEAD) == 1
txt = txt.replace(OLD_HEAD, NEW_HEAD, 1)

# --- 2. the room re-measure reads the contract, and writes in the room's own frame
head = txt.index("  function bimRemeasureRoomFromSource(room,ctx){")
tail = txt.index("  function bimGraphVisit(node,g,ctx){")
old_fn = txt[head:tail]
assert 'newPts=src.pts.map' in old_fn and 'innerLoop' in old_fn, 'wrong span'
NEW_FN = """  function bimRemeasureRoomFromSource(room,ctx){
    if(!room||room.t!=='room')return false;
    var st=room.sourceType,sid=room.sourceId;
    if(!sid||(st!=='wall'&&st!=='sketch'))return false;
    /* __acad3dV97: through the source contract. The version this replaces read raw src.pts,
       so a curved sketch was re-measured as chords, and a two-vertex circle failed outright;
       and it wrote WORLD points into a room that is drawn with its own pos added. */
    var b=bimSourceBoundaryWorld(objById(sid));
    if(b.error){
      console.warn('[BIM] '+room.name+': '+b.error+'; its boundary was NOT updated.');
      if(ctx){ctx.roomsFailed++;ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;}
      return false;
    }
    var q=bimObjOffset(room);
    room.pts=bimToFrame(room,b.ring);
    room.y=b.y-q[1];
    room.area=bimPolyArea(room.pts);
    if(ctx){ctx.roomsUpdated++;ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;}
    return true;
  }
"""
txt = txt[:head] + NEW_FN + txt[tail:]

# --- 3. creation reads the same contract, so a moved sketch or wall can be picked
OLD_FIND = """      if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3){
        if(Math.abs(o.bim.baseY-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.bim.innerLoop))candidates.push({pts:o.bim.innerLoop.slice(),y:o.bim.baseY,sourceType:'wall',sourceId:o.id,wallHeight:o.bim.height});
      }else if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=2){
        /* __acad3dV93: >=2, because a circle is two vertices. The test and the boundary it
           hands back are both the flattened outline, so a curved sketch encloses a room. */
        if(Math.abs(o.y-y0)>0.5)continue;
        var skOut=bimSketchOutline(o);
        if(skOut.length>=3&&bimPointInPoly(pt,skOut))candidates.push({pts:skOut.slice(),y:o.y,sourceType:'sketch',sourceId:o.id});
      }"""
NEW_FIND = """      /* __acad3dV97: through the source contract, in WORLD coordinates. This tested the click
         against a moved sketch's or wall's LOCAL points, so a sketch that had been moved could
         not be picked where it was drawn. */
      var isWall=(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3);
      var isSk=(o.t==='sketch'&&!bimIsPoint(o)&&o.closed!==false&&o.pts&&o.pts.length>=2);
      if(!isWall&&!isSk)continue;
      var sb=bimSourceBoundaryWorld(o);
      if(sb.error)continue;
      if(Math.abs(sb.y-y0)>0.5)continue;
      if(!bimPointInPoly(pt,sb.ring))continue;
      if(isWall)candidates.push({pts:sb.ring.slice(),y:sb.y,sourceType:'wall',sourceId:o.id,wallHeight:o.bim.height});
      else candidates.push({pts:sb.ring.slice(),y:sb.y,sourceType:'sketch',sourceId:o.id});"""
assert txt.count(OLD_FIND) == 1, 'find anchor count %d' % txt.count(OLD_FIND)
txt = txt.replace(OLD_FIND, NEW_FIND, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
