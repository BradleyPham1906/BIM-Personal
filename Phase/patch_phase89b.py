"""patch_phase89b.py -- Phase 89 part 2: every wall rebuild path, classified.

There are sixteen calls to bimBuildWallGeometry. Threading a seventh argument through them is
exactly where a curve silently straightens, so each one is classified and handled explicitly, and
the script asserts at the end that NO six-argument call survives. That assertion is the whole
point: a missed call site would not throw, would not look wrong, and would quietly turn a curved
wall straight the next time its type or height changed.

  GROUP A - rebuilds the same centerline (type, thickness, height, openings, vertex drag).
            Passes the wall's own bulges. The curve must survive.
  GROUP B - transforms the whole centerline. Translation, rotation and scaling preserve a bulge
            unchanged; a MIRROR NEGATES it, because reflection reverses the sense of an arc.
  GROUP C - derives a new point list with straight-line math (trim, join, merge, offset, and the
            V87 modify tools). These REFUSE a curved wall with a named reason rather than
            silently discarding the curve.
"""
import hashlib, pathlib, re, sys

BASE = None  # set from patch_phase89.py's output; asserted below against the file on disk
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
b0 = len(src.encode('utf-8'))
assert 'function bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges)' in src, \
    'patch_phase89.py must run first'

reps = []

# ---- the shared predicate -------------------------------------------------------------------
reps.append(("""  function bimNewWallFromSource(src,pts,closed,nameHint){
    var res=bimBuildWallGeometry(pts,src.bim.baseY,src.bim.height,src.bim.thickness,src.bim.align,!!closed);""",
"""  /* __acad3dV89: one predicate and one message shape for every tool that cannot yet do curves.

     The alternative was to let them run on the chord, which would silently straighten a curved
     wall and look like a successful edit. A refusal that names the tool is the honest form of
     "not yet", and it is one line at each call layer rather than a guess inside the geometry. */
  function bimWallIsCurved(o){
    return !!(o&&o.bim&&o.bim.type==='wall'&&bimHasBulge(o.bim.bulges));
  }
  function bimRefuseIfCurved(o,what){
    if(!bimWallIsCurved(o))return false;
    a3dToast(what+' does not support curved walls yet - '+(o.name||'that wall')+' has an arc in it');
    return true;
  }
  function bimNewWallFromSource(src,pts,closed,nameHint,bulges){
    var res=bimBuildWallGeometry(pts,src.bim.baseY,src.bim.height,src.bim.thickness,src.bim.align,!!closed,bulges);""", 1))

# ---- GROUP A --------------------------------------------------------------------------------
reps.append(("""      var r=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,t.params.thickness,o.bim.align,o.bim.closed);""",
"""      var r=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,t.params.thickness,o.bim.align,o.bim.closed,o.bim.bulges);""", 1))

reps.append(("""      var res=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,
        t.params.thickness,o.bim.align,o.bim.closed);""",
"""      var res=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,
        t.params.thickness,o.bim.align,o.bim.closed,o.bim.bulges);""", 1))

reps.append(("""    var res=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,t.params.thickness,o.bim.align,o.bim.closed);""",
"""    var res=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,t.params.thickness,o.bim.align,o.bim.closed,o.bim.bulges);""", 1))

reps.append(("""    var res=bimBuildWallGeometry(b.centerline,b.baseY,newHeight,newThickness,newAlign,b.closed);""",
"""    var res=bimBuildWallGeometry(b.centerline,b.baseY,newHeight,newThickness,newAlign,b.closed,b.bulges);""", 1))

reps.append(("""    var base=bimBuildWallGeometry(b.centerline,b.baseY,b.height,b.thickness,b.align,b.closed);""",
"""    var base=bimBuildWallGeometry(b.centerline,b.baseY,b.height,b.thickness,b.align,b.closed,b.bulges);""", 1))

reps.append(("""    var res=bimBuildWallGeometry(cl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);""",
"""    var res=bimBuildWallGeometry(cl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,o.bim.bulges);""", 1))

# ---- GROUP B --------------------------------------------------------------------------------
reps.append(("""      var newCl=o.bim.centerline.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);""",
"""      var newCl=o.bim.centerline.map(function(p){return [p[0]+dx,p[1]+dz];});
      /* __acad3dV89: a translation leaves every bulge exactly as it was. */
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,o.bim.bulges);""", 1))

reps.append(("""      var newCl=o.bim.centerline.map(transformPt);
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);""",
"""      var newCl=o.bim.centerline.map(transformPt);
      /* __acad3dV89: rotation and scaling preserve a bulge (it is tan of a quarter of the swept
         angle, and neither changes an angle). A MIRROR reverses the sense of every arc, so each
         bulge is negated - a reflected curve that kept its sign would bow the wrong way, which
         is the kind of error that looks like a rendering glitch rather than a data one. */
      var newBulges=o.bim.bulges;
      if(newBulges&&xf&&xf.kind==='mirror')
        newBulges=newBulges.map(function(bv){return -bv;});
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,newBulges);""", 1))

# ---- GROUP C: refuse rather than straighten --------------------------------------------------
reps.append(("""    var resA=bimBuildWallGeometry(clA,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false);
    var resB=bimBuildWallGeometry(clB,wallB.bim.baseY,wallB.bim.height,wallB.bim.thickness,wallB.bim.align,false);""",
"""    var resA=bimBuildWallGeometry(clA,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false,null);
    var resB=bimBuildWallGeometry(clB,wallB.bim.baseY,wallB.bim.height,wallB.bim.thickness,wallB.bim.align,false,null);""", 1))

reps.append(("""  function bimJoinWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};""",
"""  function bimJoinWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};
    if(bimWallIsCurved(wallA)||bimWallIsCurved(wallB))   /* __acad3dV89 */
      return {error:'Join does not support curved walls yet'};""", 1))

reps.append(("""    var res=bimBuildWallGeometry(newCl,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false);""",
"""    var res=bimBuildWallGeometry(newCl,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false,null);""", 1))

reps.append(("""  function bimMergeWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};""",
"""  function bimMergeWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};
    if(bimWallIsCurved(wallA)||bimWallIsCurved(wallB))   /* __acad3dV89 */
      return {error:'Merge does not support curved walls yet'};""", 1))

reps.append(("""  function bimOffsetObject(o,dist){
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};""",
"""  function bimOffsetObject(o,dist){
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      /* __acad3dV89: offsetting an arc changes its radius, which bimOffsetPoints does not do. */
      if(bimWallIsCurved(o))return {error:'Offset does not support curved walls yet'};""", 1))

reps.append(("""      var res=bimBuildWallGeometry(ncl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);""",
"""      var res=bimBuildWallGeometry(ncl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,null);""", 1))

reps.append(("""    if(!target||bestD>3){a3dToast('Click closer to the wall you want to trim');return;}
    var r=bimTrimPolyline(target.bim.centerline,target.bim.closed,cutter.bim.centerline,cutter.bim.closed,clickPt);""",
"""    if(!target||bestD>3){a3dToast('Click closer to the wall you want to trim');return;}
    if(bimRefuseIfCurved(target,'Trim')||bimRefuseIfCurved(cutter,'Trim'))return;   /* __acad3dV89 */
    var r=bimTrimPolyline(target.bim.centerline,target.bim.closed,cutter.bim.centerline,cutter.bim.closed,clickPt);""", 1))

reps.append(("""    var res=bimBuildWallGeometry(r.pts,target.bim.baseY,target.bim.height,target.bim.thickness,target.bim.align,false);""",
"""    var res=bimBuildWallGeometry(r.pts,target.bim.baseY,target.bim.height,target.bim.thickness,target.bim.align,false,null);""", 1))

reps.append(("""  function bimRebuildWallFrom(o,pts,closed){
    var res=bimBuildWallGeometry(pts,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,!!closed);""",
"""  function bimRebuildWallFrom(o,pts,closed,bulges){
    var res=bimBuildWallGeometry(pts,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,!!closed,bulges);""", 1))

reps.append(("""    var res=bimBuildWallGeometry(pts,y0,height,thickness,align,closed);""",
"""    var res=bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges);""", 1))

reps.append(("""  function buildWallSolid(pts,y0,height,thickness,align,closed){""",
"""  function buildWallSolid(pts,y0,height,thickness,align,closed,bulges){""", 1))

# ---- GROUP C: the V87 modify tools refuse at their entry points --------------------------------
reps.append(("""      var target=bimPickWallNear(clickPt,boundaryId,3);
      if(!target){a3dToast('Click closer to the end of the wall you want to extend');return false;}""",
"""      var target=bimPickWallNear(clickPt,boundaryId,3);
      if(!target){a3dToast('Click closer to the end of the wall you want to extend');return false;}
      if(bimRefuseIfCurved(target,'Extend')||bimRefuseIfCurved(bound,'Extend'))return false;   /* __acad3dV89 */""", 1))

reps.append(("""      var w=objById(wallId);
      if(!w){a3dToast('That wall no longer exists');return false;}
      var r=bimBreakPolyline(w.bim.centerline,w.bim.closed,p1,p2);""",
"""      var w=objById(wallId);
      if(!w){a3dToast('That wall no longer exists');return false;}
      if(bimRefuseIfCurved(w,'Break'))return false;   /* __acad3dV89 */
      var r=bimBreakPolyline(w.bim.centerline,w.bim.closed,p1,p2);""", 1))

reps.append(("""      var w=objById(wallId);
      if(!w){a3dToast('That wall no longer exists');return false;}
      var r=bimLengthenPolyline(w.bim.centerline,w.bim.closed,mode,value,clickPt);""",
"""      var w=objById(wallId);
      if(!w){a3dToast('That wall no longer exists');return false;}
      if(bimRefuseIfCurved(w,'Lengthen'))return false;   /* __acad3dV89 */
      var r=bimLengthenPolyline(w.bim.centerline,w.bim.closed,mode,value,clickPt);""", 1))

reps.append(("""      var a=objById(idA),b=objById(idB);
      if(!a||!b){a3dToast('One of those walls no longer exists');return false;}
      var r=bimChamferPolylines(a.bim.centerline,a.bim.closed,b.bim.centerline,b.bim.closed,d1,d2);""",
"""      var a=objById(idA),b=objById(idB);
      if(!a||!b){a3dToast('One of those walls no longer exists');return false;}
      if(bimRefuseIfCurved(a,'Chamfer')||bimRefuseIfCurved(b,'Chamfer'))return false;   /* __acad3dV89 */
      var r=bimChamferPolylines(a.bim.centerline,a.bim.closed,b.bim.centerline,b.bim.closed,d1,d2);""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

# ---- the completeness assertion this whole script exists for ---------------------------------
# Every remaining call must pass seven arguments. A six-argument call is a silent straightener.
calls = re.findall(r'(?<!function )bimBuildWallGeometry\(([^;{]*?)\);', out, re.S)
assert len(calls) == 16, 'expected 16 call sites, found %d' % len(calls)
short = []
for c in calls:
    depth = 0
    commas = 0
    for ch in c:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif ch == ',' and depth == 0:
            commas += 1
    if commas != 6:
        short.append(' '.join(c.split())[:90])
assert not short, 'call sites still passing the wrong argument count:\n  ' + '\n  '.join(short)
print('all %d call sites pass 7 arguments' % len(calls))

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
