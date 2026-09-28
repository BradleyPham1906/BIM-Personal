"""patch_phase89.py -- Phase 89 part 1: curved wall geometry.

A wall centerline may now carry bulges. The ribbon builder flattens the centerline FIRST and runs
the existing miter/offset/ribbon code over the result, so there is one ribbon builder rather than
a second curved one that could disagree with it.

Wall length becomes arc length in the same patch: a schedule that reports the chord of a curved
wall is wrong, and "accuracy before feature count" makes that part of shipping the curve, not a
follow-up.
"""
import hashlib, pathlib, sys

BASE = '4d8a3c064442ff62bd546835ce4c45a6589552d3c7bffcc531e77a4450568665'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. the builder ------------------------------------------------------------------------
reps.append(("""  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed){
    var off=bimAlignOffsets(thickness,align);
    var cleanPts=[pts[0]],i;
    for(i=1;i<pts.length;i++){
      var prevp=cleanPts[cleanPts.length-1],curp=pts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }""",
"""  /* __acad3dV89: the centerline may now carry bulges (the V88 storage), so a wall can curve.

     HOW: flatten the centerline FIRST, then run the existing clean / CCW / offset / miter /
     ribbon code over the flattened points. One ribbon builder, not a second curved one that
     could drift from it.

     WHAT IS STORED is the ORIGINAL pts and bulges, never the flattened copy. Storing the
     flattened version would re-tessellate an already tessellated centerline on every rebuild -
     a type change, an opening, a height edit - and the wall would coarsen a little each time it
     was touched, with no single moment where anything looked wrong.

     Flattening before sketchCCW also avoids a real trap: reversing a point list that carries
     bulges requires reversing AND NEGATING them, because reversing the vertex order reverses
     the sense of every arc. Flattened points carry no such baggage. */
  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges){
    var off=bimAlignOffsets(thickness,align);
    var geomPts=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;
    var cleanPts=[geomPts[0]],i;
    for(i=1;i<geomPts.length;i++){
      var prevp=cleanPts[cleanPts.length-1],curp=geomPts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }""", 1))

reps.append(("""    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};""",
"""    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
    if(bimHasBulge(bulges))bim.bulges=bulges.slice();   /* __acad3dV89 */""", 1))

# ---- 2. wall length is ARC length ------------------------------------------------------------
reps.append(("""  function bimWallLength(centerline,closed){
    if(!centerline||centerline.length<2)return 0;
    var len=0,n=centerline.length,i;
    var segCount=closed?n:n-1;
    for(i=0;i<segCount;i++){
      var a=centerline[i],b=centerline[(i+1)%n];
      var dx=b[0]-a[0],dz=b[1]-a[1];
      len+=Math.sqrt(dx*dx+dz*dz);
    }
    return len;
  }""",
"""  /* __acad3dV89: a curved wall's length is the ARC length. The chord is the wrong number
     everywhere it appears - the properties panel, the wall schedule, and any quantity taken off
     that schedule - and it is wrong quietly, which is worse than wrong loudly. bimBulgedLength
     returns exactly this function's old result when there are no bulges. */
  function bimWallLength(centerline,closed,bulges){
    if(!centerline||centerline.length<2)return 0;
    return bimBulgedLength(centerline,bulges||null,!!closed);
  }""", 1))

reps.append(("""        dims+=bimPropLenText('Length',bimWallLength(o.bim.centerline,o.bim.closed));""",
"""        dims+=bimPropLenText('Length',bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges));""", 1))

reps.append(("""      var length=hasCenterline?bimWallLength(o.bim.centerline,o.bim.closed):null;""",
"""      var length=hasCenterline?bimWallLength(o.bim.centerline,o.bim.closed,o.bim.bulges):null;""", 1))

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
