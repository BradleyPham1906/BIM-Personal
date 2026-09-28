"""patch_phase90c.py -- Phase 90 part 3: Offset understands curves, and stops refusing them.

The V89 refusal in bimOffsetObject is REMOVED, not bypassed. A guard that survives the work it
was waiting for is the leftover Standing Law 1 is about, and this script asserts it is gone.
"""
import hashlib, pathlib, sys

BASE = 'b163bc36ebc629a5530dea335c7e365fcff6f0ef88bb7ac7fcc385d459a606e5'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. walls: offset the curve, and drop the refusal -----------------------------------------
reps.append(("""  function bimOffsetObject(o,dist){
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      /* __acad3dV89: offsetting an arc changes its radius, which bimOffsetPoints does not do. */
      if(bimWallIsCurved(o))return {error:'Offset does not support curved walls yet'};
      var ncl=bimOffsetPoints(o.bim.centerline,dist,o.bim.closed);
      if(!ncl)return {error:'Offset distance cannot be zero'};
      var res=bimBuildWallGeometry(ncl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,null);""",
"""  function bimOffsetObject(o,dist){
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      /* __acad3dV90: a curved wall offsets to CONCENTRIC arcs. The V89 refusal that stood here
         was waiting for exactly this and is gone rather than bypassed. */
      var ncl,nbulge=null;
      if(bimHasBulge(o.bim.bulges)){
        var ob=bimOffsetBulged(o.bim.centerline,o.bim.bulges,o.bim.closed,dist);
        if(ob.error)return {error:'Offset: '+ob.error};
        ncl=ob.pts;nbulge=ob.bulges;
      }else{
        ncl=bimOffsetPoints(o.bim.centerline,dist,o.bim.closed);
      }
      if(!ncl)return {error:'Offset distance cannot be zero'};
      var res=bimBuildWallGeometry(ncl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,nbulge);""", 1))

# ---- 2. sketches too --------------------------------------------------------------------------
reps.append(("""    if(o.t==='sketch'){
      var npts=bimOffsetPoints(o.pts,dist,o.closed!==false);
      if(!npts)return {error:'Offset distance cannot be zero'};
      return {obj:{id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:(o.name||'Sketch')+' offset',
        col:o.col,pos:[0,0,0],pts:npts,y:o.y,closed:o.closed,layer:o.layer}};
    }""",
"""    if(o.t==='sketch'){
      /* __acad3dV90: same treatment for a sketch that carries arcs. */
      var npts,nb=null;
      if(bimHasBulge(o.bulges)){
        var sb=bimOffsetBulged(o.pts,o.bulges,o.closed!==false,dist);
        if(sb.error)return {error:'Offset: '+sb.error};
        npts=sb.pts;nb=sb.bulges;
      }else{
        npts=bimOffsetPoints(o.pts,dist,o.closed!==false);
      }
      if(!npts)return {error:'Offset distance cannot be zero'};
      var so={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:(o.name||'Sketch')+' offset',
        col:o.col,pos:[0,0,0],pts:npts,y:o.y,closed:o.closed,layer:o.layer};
      if(bimHasBulge(nb))so.bulges=nb.slice();
      return {obj:so};
    }""", 1))

# ---- 3. hooks and marker ----------------------------------------------------------------------
reps.append(("""  /* __acad3dV89 */
  window.__a3dFilletCorner=bimFilletCorner;""",
"""  /* __acad3dV90 */
  window.__a3dTangentBulge=bimTangentBulge;
  window.__a3dSegEndDir=bimSegEndDir;
  window.__a3dOffsetBulged=bimOffsetBulged;
  window.__a3dCircleLineIntersect=bimCircleLineIntersect;
  window.__a3dSetArcMode=function(on){return bimSetArcMode(A3D.sk,on);};
  window.__a3dSkBulges=function(){return A3D.sk&&A3D.sk.bulges?A3D.sk.bulges.slice():null;};
  window.__a3dSkArcMode=function(){return !!(A3D.sk&&A3D.sk.arcMode);};
  window.__acad3dV90='arcmodeonwallandpline,tangentcontinuation,arcawareoffset,curvedpreview,offsetrefusalremoved';
  /* __acad3dV89 */
  window.__a3dFilletCorner=bimFilletCorner;""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

assert 'Offset does not support curved walls yet' not in out, \
    'the V89 offset refusal is still in the file'

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
