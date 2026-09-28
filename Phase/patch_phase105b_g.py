"""patch_phase105bg.py"""
NAME = 'patch_phase105bg'
BASE = '76a630789eed16a6aec35a7564aed37924d7e159fbaad2ca0973952a04355569'
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
# --- patch g: a room is bounded by the faces of its walls, not by their centrelines.

rep("""    return {pts:hit.face.pts,bulges:hit.face.bulges,area:hit.area,
            islands:bimFaceHasIsland(g,hit),edges:arr.edges.length,faces:faces.length,
            srcIds:hit.face.srcIds||[]};   /* __acad3dV98: which objects bound it */""",
"""    return {pts:hit.face.pts,bulges:hit.face.bulges,area:hit.area,
            islands:bimFaceHasIsland(g,hit),edges:arr.edges.length,faces:faces.length,
            srcs:hit.face.srcs||null,   /* __acad3dV105b: which object bounds EACH edge */
            srcIds:hit.face.srcIds||[]};   /* __acad3dV98: which objects bound it */""",1)

rep("""    return {ring:flat,pts:res.pts,bulges:bimHasBulge(res.bulges)?res.bulges.slice():null,y:y,
            srcIds:(res.srcIds||[]).slice(),islands:!!res.islands,sig:sig,type:'region'};""",
"""    return {ring:flat,pts:res.pts,bulges:bimHasBulge(res.bulges)?res.bulges.slice():null,y:y,
            srcs:res.srcs?res.srcs.slice():null,   /* __acad3dV105b */
            srcIds:(res.srcIds||[]).slice(),islands:!!res.islands,sig:sig,type:'region'};""",1)

rep("""  function bimCreateRoom(boundary){
    pushUndo();
    A3D.counts.room=(A3D.counts.room||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:'#7fd4c4',
      pos:[0,0,0],pts:boundary.pts,y:boundary.y,area:bimPolyArea(boundary.pts),levelId:A3D.activeLevel,""",
"""  /* __acad3dV105b: a room is bounded by the FACES of the walls around it, not by their
     centerlines.

     The bug this fixes: a plan drawn as one closed wall measured its inner loop, and the SAME
     plan drawn as four separate walls measured the centerline rectangle -- larger by a wall
     thickness all round. Nothing caught it until a level reported a net area bigger than its
     gross, which cannot happen. The inset is the one the gross ring uses, taken to the left of
     travel because an interior face traces counter-clockwise.

     Only the room takes it. A floor or a foundation slab placed in the same region still runs to
     the centerlines, because a slab genuinely does run under the walls that sit on it. */
  function bimRoomFaceRing(reg){
    if(!reg||!reg.pts||!reg.srcs||!reg.srcs.length)return null;
    var ring;
    try{ring=bimInsetFaceRing(reg.pts,reg.bulges||[],reg.srcs,{},-1);}
    catch(eRF){console.warn('[BIM] Room face inset failed: ',eRF);return null;}
    if(!ring||ring.length<3)return null;
    if(!(bimPolyArea(ring)>1e-6))return null;
    return ring;
  }
  function bimCreateRoom(boundary){
    pushUndo();
    A3D.counts.room=(A3D.counts.room||0)+1;
    var rpts=boundary.roomPts||boundary.pts;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:'#7fd4c4',
      pos:[0,0,0],pts:rpts,y:boundary.y,area:bimPolyArea(rpts),levelId:A3D.activeLevel,""",1)

rep("""      return {pts:reg.ring,y:y0,sourceType:allW?'wallgroup':'region',sourceId:null,wallHeight:wh,
              rawPts:reg.pts,bulges:reg.bulges,islands:reg.islands,""",
"""      return {pts:reg.ring,y:y0,sourceType:allW?'wallgroup':'region',sourceId:null,wallHeight:wh,
              roomPts:bimRoomFaceRing(reg),   /* __acad3dV105b: what a ROOM measures here */
              rawPts:reg.pts,bulges:reg.bulges,islands:reg.islands,""",1)

rep("""      var rq=bimObjOffset(room);
      room.pts=bimToFrame(room,rb.ring);
      room.y=rb.y-rq[1];
      room.area=bimPolyArea(room.pts);
      bimRegionRecord(room,rb);""",
"""      var rq=bimObjOffset(room);
      room.pts=bimToFrame(room,bimRoomFaceRing(rb)||rb.ring);   /* __acad3dV105b */
      room.y=rb.y-rq[1];
      room.area=bimPolyArea(room.pts);
      bimRegionRecord(room,rb);""",1)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
