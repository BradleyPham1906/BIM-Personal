"""patch_phase123b.py -- V123: an element keeps what it is through every rebuild, copy and turn.

A push or pull rebuilds an element, and V123's audit of the paths that already rebuild them found
the same fault in eleven places: each rebuild, copy or transform decided for itself which of the
element's fields survived, and each remembered a different few.

1. A wall's type was dropped by Properties' Height, Thickness and Location Line, by a grip drag of
   its end, by Join and Trim, and by every copy of it (Ctrl+D, the gizmo's Ctrl-drag,
   arrays, mirror). Copies of floors and columns had theirs re-guessed from their sizes. Measured on
   V122: a wall's Height typed in Properties left it with no type at all.
2. Turning or scaling a floor turned its solid and not its outline (the transform returned no record
   for it), so the next rebuild -- a thickness edit -- put it back where it had been. Mirroring a
   floor threw.
3. A copy of a moved wall, floor, column, room, dimension, text, roof or stair was made where the
   original had been BEFORE it was moved: its geometry was copied in the original's own frame and
   the frame's offset thrown away. Measured on V122: a wall moved 10 m east, copied with Ctrl+D,
   came out 9 m west of it. The gizmo's Ctrl-drag copies through the same function.
4. Pad and Pocket of a moved sketch were made where the sketch had been before the move -- the same
   fault as 3, in the sketch-to-solid operations V123's pull turns a sketch into a solid with.

bimCarryBim is the one rule for 1 and 2: every field of the old record the new one does not set is
carried, except the geometry a wall build writes only sometimes (its arcs, its loops), which would
otherwise outlive the shape it described. Every rebuild, copy and transform of a wall, floor or
column goes through it."""
NAME = 'patch_phase123b.py'
BASE = '96f805c370e9497f692bd34c44b299660704f8cd41e3dcf19898169e70819375'
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

# 1. the one rule: carry what the build does not own
rep("""  function buildWallSolid(pts,y0,height,thickness,align,closed,bulges){""",
"""  /* __acad3dV123: WHAT A REBUILD OWNS. An element's record is its geometry and everything else about
     it -- its type, its level, whatever a later phase adds. A rebuild makes the geometry again; it
     must not decide what else survives. Before V123 every rebuild, copy and transform carried the
     fields its author remembered: Properties' Height, a grip drag, Join and Trim dropped a wall's
     type, every copy of a wall had none, copies of floors and columns had theirs re-guessed from
     their sizes, and a turned floor kept the outline it had before the turn. bimCarryBim copies every
     field of the old record the new one does not set -- except the geometry a wall build writes
     only sometimes (its arcs, its loops), which would outlive the shape it described. Declared
     here, beside the build that writes them. */
  var BIM_BUILT_OPTIONAL={wall:['bulges','innerLoop','outerLoop']};
  function bimCarryBim(from,to){
    if(!from||!to)return to;
    var skip=BIM_BUILT_OPTIONAL[to.type||from.type]||[],k,v;
    for(k in from){
      if(!from.hasOwnProperty(k)||to.hasOwnProperty(k)||skip.indexOf(k)>=0)continue;
      v=from[k];
      to[k]=(v&&typeof v==='object')?JSON.parse(JSON.stringify(v)):v;
    }
    return to;
  }
  function buildWallSolid(pts,y0,height,thickness,align,closed,bulges){""")

# 2. every wall rebuild
rep("""      var kT=o.bim.typeId,kC=o.bim.typeCat,kL=o.bim.levelId;
      o.mesh=r.mesh;o.bim=r.bim;o.bim.typeId=kT;o.bim.typeCat=kC;o.bim.levelId=kL;""",
"""      o.mesh=r.mesh;o.bim=bimCarryBim(o.bim,r.bim);   /* __acad3dV123 */""")
rep("""      var keepType=o.bim.typeId,keepCat=o.bim.typeCat,keepLevel=o.bim.levelId;
      o.mesh=res.mesh;
      o.bim=res.bim;
      o.bim.typeId=keepType;o.bim.typeCat=keepCat;o.bim.levelId=keepLevel;""",
"""      o.mesh=res.mesh;
      o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123 */""")
rep("""    if(!res.error){
      var lvl=o.bim.levelId;
      o.mesh=res.mesh;o.bim=res.bim;
      o.bim.typeId=typeId;o.bim.typeCat='wall';o.bim.levelId=lvl;""",
"""    if(!res.error){
      o.mesh=res.mesh;o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123: the new type was set above */""")
rep("""    res.bim.levelId=b.levelId;
    o.mesh=res.mesh;
    o.bim=res.bim;
    bimAfterWallRebuild(o);   // __acad3dV51: re-cut openings lost to the thickness/height/align rebuild""",
"""    o.mesh=res.mesh;
    o.bim=bimCarryBim(b,res.bim);   /* __acad3dV123: it kept the level and dropped the type */
    bimAfterWallRebuild(o);   // __acad3dV51: re-cut openings lost to the thickness/height/align rebuild""")
rep("""    res.bim.levelId=o.bim.levelId;
    o.mesh=res.mesh;
    o.bim=res.bim;
    return true;""",
"""    o.mesh=res.mesh;
    o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123: a grip drag dropped the wall's type */
    return true;""")
rep("""    a.mesh=res.meshA;a.bim=res.bimA;
    b.mesh=res.meshB;b.bim=res.bimB;""",
"""    a.mesh=res.meshA;a.bim=bimCarryBim(a.bim,res.bimA);   /* __acad3dV123: Join dropped both walls' */
    b.mesh=res.meshB;b.bim=bimCarryBim(b.bim,res.bimB);   /* types and levels */""")
rep("""    var lvl=a.bim.levelId,typeId=a.bim.typeId,typeCat=a.bim.typeCat;
    a.mesh=res.mesh;a.bim=res.bim;a.bim.levelId=lvl;a.bim.typeId=typeId;a.bim.typeCat=typeCat;""",
"""    a.mesh=res.mesh;a.bim=bimCarryBim(a.bim,res.bim);   /* __acad3dV123 */""")
rep("""    res.bim.levelId=target.bim.levelId;
    target.mesh=res.mesh;
    target.bim=res.bim;
    bimAfterWallRebuild(target);""",
"""    target.mesh=res.mesh;
    target.bim=bimCarryBim(target.bim,res.bim);   /* __acad3dV123: Trim dropped the type */
    bimAfterWallRebuild(target);""")
rep("""    var keepLevel=o.bim.levelId,keepType=o.bim.typeId,keepCat=o.bim.typeCat;
    o.mesh=res.mesh;
    o.bim=res.bim;
    o.bim.levelId=keepLevel;
    if(keepType)o.bim.typeId=keepType;
    if(keepCat)o.bim.typeCat=keepCat;
    bimAfterWallRebuild(o);""",
"""    o.mesh=res.mesh;
    o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123 */
    bimAfterWallRebuild(o);""")

# 3. a transform: a floor's record carries its new outline, and every in-place transform carries
rep("""      return {kind:'floor',mesh:res2.mesh,bim:res2.bim};""",
"""      /* __acad3dV123: bimBuildFloorGeometry returns a solid and no record, so this returned no
         outline: a turned floor kept its old one, the next rebuild put it back, and a mirrored copy
         threw on the missing record */
      return {kind:'floor',mesh:res2.mesh,bim:{type:'floor',profile:newProf}};""")
rep("""o.mesh=g.mesh;o.bim=Object.assign(o.bim,g.bim);""",
    """o.mesh=g.mesh;o.bim=bimCarryBim(o.bim,g.bim);""", 2)
rep("""copy.mesh=g.mesh;copy.bim=g.bim;copy.bim.levelId=o.bim.levelId;}""",
    """copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}""", 4)
rep("""copy.name='Column_'+A3D.counts.column;copy.mesh=g.mesh;copy.bim=g.bim;}""",
    """copy.name='Column_'+A3D.counts.column;copy.mesh=g.mesh;copy.bim=bimCarryBim(o.bim,g.bim);}""", 2)

# 4. a copy: where the original IS, with what it is
rep("""      res.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:o.layer};""",
"""      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:[0,0,0],mesh:res.mesh,bim:bimCarryBim(o.bim,res.bim),layer:o.layer};""")
rep("""        bim:{type:'floor',thickness:o.bim.thickness,material:o.bim.material,levelId:o.bim.levelId,baseY:o.bim.baseY,profile:newProf},layer:o.layer};""",
    """        bim:bimCarryBim(o.bim,{type:'floor',profile:newProf}),layer:o.layer};""")
rep("""        bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter,rotation:o.bim.rotation||0},layer:o.layer};""",
    """        bim:bimCarryBim(o.bim,{type:'column',center:newCenter}),layer:o.layer};""")
# every copy rebuilt in the original's own frame keeps the original's offset: the frame's offset was
# thrown away, so a copy of a moved element came out where it had been before the move
fh = "  function bimDuplicateObject(o,dx,dz){"
if t.count(fh) != 1:
    sys.exit('ABORT: bimDuplicateObject head')
fs = t.index(fh)
fe = t.find('\n  function duplicateSelection(){', fs + len(fh))
if fe < 0 or t.count('\n  function duplicateSelection(){') != 1:
    sys.exit('ABORT: bimDuplicateObject tail')
body = t[fs:fe]
nz = body.count('pos:[0,0,0]')
if nz != 8:
    sys.exit('ABORT: %d pos:[0,0,0] in bimDuplicateObject, expected 8' % nz)
body = body.replace('pos:[0,0,0]', 'pos:bimObjOffset(o)')
body = body.replace("""  function bimDuplicateObject(o,dx,dz){
    var copy;""", """  function bimDuplicateObject(o,dx,dz){
    /* __acad3dV123: every copy below that is rebuilt from the original's geometry keeps the
       original's offset (pos) -- the geometry is in the original's own frame, and the frame's offset
       was thrown away, so a copy of a wall moved 10 m came out 10 m from where it should be. The
       gizmo's Ctrl-drag copies through here too. */
    var copy;""", 1)
t = t[:fs] + body + t[fe:]

# 5. Pad and Pocket where the sketch is
rep("""    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Pad '+A3D.counts.pad,col:'#9db4c8',pos:[0,0,0],mesh:m};""",
"""    /* __acad3dV123: at the sketch's own offset -- the outline is in the sketch's frame, so a sketch
       that had been moved was padded where it had been before the move */
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Pad '+A3D.counts.pad,col:'#9db4c8',pos:bimObjOffset(s),mesh:m};""")
rep("""  function doPocket(s,depth){
    var P=sketchCCW(bimSketchOutline(s));
    if(P.length<3){a3dToast('Sketch needs at least 3 points');return null;}""",
"""  function doPocket(s,depth){
    var P=sketchCCW(bimSketchOutline(s));
    if(P.length<3){a3dToast('Sketch needs at least 3 points');return null;}
    /* __acad3dV123: the outline in the WORLD, where the solids are measured -- it was compared and
       cut in the sketch's own frame, so a sketch that had been moved cut where it had been */
    var sq=bimObjOffset(s),sy=(s.y||0)+sq[1];
    P=P.map(function(p){return [p[0]+sq[0],p[1]+sq[2]];});""")
rep("""        if(cx>=bb.mn[0]-0.01&&cx<=bb.mx[0]+0.01&&cz>=bb.mn[2]-0.01&&cz<=bb.mx[2]+0.01&&s.y>=bb.mn[1]-0.05&&s.y<=bb.mx[1]+0.05){""",
    """        if(cx>=bb.mn[0]-0.01&&cx<=bb.mx[0]+0.01&&cz>=bb.mn[2]-0.01&&cz<=bb.mx[2]+0.01&&sy>=bb.mn[1]-0.05&&sy<=bb.mx[1]+0.05){""")
rep("""    var tool={mesh:padMesh(P,s.y-depth,depth+0.02),pos:[0,0,0]};""",
    """    var tool={mesh:padMesh(P,sy-depth,depth+0.02),pos:[0,0,0]};""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
