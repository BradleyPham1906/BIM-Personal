"""patch_phase104.py -- __acad3dV104: every export writes objects where they ARE, north up.

Found in V103, measured before this patch:
  1. POSITION. The three plan exporters (DXF, plan SVG, sheet viewport) wrote each object's
     LOCAL points. An object moved by the gizmo or a drag keeps its points and changes its pos,
     so it exported where it was drawn: a line at pos (100,0,50) came out at the origin. The
     canvas was fixed for this in V75; the exporters never were.
  2. MIRROR. Model +Z runs DOWN the plan (project north is -Z), and the DXF wrote plan Y = Z, so
     every DXF was the plan's mirror image in AutoCAD (+Y up): a line at N 45 E arrived as S 45 E,
     and every arc turned the wrong way. The SVG writers are y-down like the canvas and were right.
  3. FRAMING. Sheet viewports framed themselves from meshed objects only, so a viewport of
     sketches, rooms, text or a property line framed nothing.

The fix is one mapping each way, written once:
  bimExportOffset(o)      the object's offset -- zero for a property, whose geometry is derived
                          in world terms already
  bimModelToDxf(x,z,o)    world, north up: [x, -z]; a bulge changes sign under the reflection
  bimDxfToModel(x,y,s)    the inverse, used by every DXF entity the importer reads
so export and import cannot disagree, and a round trip is exact.

Compatibility: a DXF written by an earlier build of this app is a mirror image; it re-imports
mirrored. A DXF from AutoCAD -- the case that matters -- now imports the right way up.
"""
import hashlib, pathlib, re
SRC = pathlib.Path('canvas_v10.html')
BASE = '87019e75535f8f3503c29775c5ed5c0b5de7b847645c22c79460e81b557d0b74'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

def js_ascii(v):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in v)

HELPERS = """  /* ================= __acad3dV104: the export mappings ================= */
  function bimExportOffset(o){
    if(!o||bimIsProperty(o))return [0,0,0];   /* derived in world terms already */
    return bimObjOffset(o);
  }
  function bimDxfToModel(x,y,s){return [x*(s||1),-y*(s||1)];}
  function bimDxfBulgesToModel(b){return b?b.map(function(v){return -(v||0);}):b;}
"""

EDITS = [
    ("""  function bimBuildDXF(){""", HELPERS + """  function bimBuildDXF(){"""),
    # --- DXF: offset + north up + bulge sign
    ("""    var stats={lwpolyline:0,line:0,text:0,skipped:0};""",
     """    var stats={lwpolyline:0,line:0,text:0,skipped:0};
    var EX=[0,0,0];   /* __acad3dV104: the current object's offset */
    function DX(p){return (p[0]+EX[0]).toFixed(6);}
    function DY(p){return (-(p[1]+EX[2])).toFixed(6);}   /* north up: DXF +Y is -Z */"""),
    ("""        out+=P(10,pts[q][0].toFixed(6))+P(20,pts[q][1].toFixed(6));
        var bq=bimBulgeAt(bulges,q);
        if(Math.abs(bq)>BIM_BULGE_EPS)out+=P(42,bq.toFixed(8));""",
     """        out+=P(10,DX(pts[q]))+P(20,DY(pts[q]));
        var bq=-bimBulgeAt(bulges,q);   /* __acad3dV104: a reflection reverses every arc */
        if(Math.abs(bq)>BIM_BULGE_EPS)out+=P(42,bq.toFixed(8));"""),
    ("""      out+=P(0,'LINE')+P(8,lay)+P(10,a[0].toFixed(6))+P(20,a[1].toFixed(6))+P(30,'0.0')+P(11,b[0].toFixed(6))+P(21,b[1].toFixed(6))+P(31,'0.0');""",
     """      out+=P(0,'LINE')+P(8,lay)+P(10,DX(a))+P(20,DY(a))+P(30,'0.0')+P(11,DX(b))+P(21,DY(b))+P(31,'0.0');"""),
    ("""      out+=P(0,'TEXT')+P(8,lay)+P(10,pt[0].toFixed(6))+P(20,pt[1].toFixed(6))+P(30,'0.0')""",
     """      out+=P(0,'TEXT')+P(8,lay)+P(10,DX(pt))+P(20,DY(pt))+P(30,'0.0')"""),
    # --- plan SVG: offset (y-down already matches the plan)
    ("""    var stats={polyline:0,line:0,text:0,skipped:0};""",
     """    var stats={polyline:0,line:0,text:0,skipped:0};
    var EX=[0,0,0];   /* __acad3dV104 */
    function W(p){return [p[0]+EX[0],p[1]+EX[2]];}
    function WL(ps){return ps?ps.map(W):ps;}"""),
    ("""      if(!pts||pts.length<2)return;
      var q;for(q=0;q<pts.length;q++)trackPt(pts[q]);
      bucket(lay);""",
     """      if(!pts||pts.length<2)return;
      pts=WL(pts);   /* __acad3dV104 */
      var q;for(q=0;q<pts.length;q++)trackPt(pts[q]);
      bucket(lay);"""),
    ("""    function line(a,b,lay,objId,rg){
      trackPt(a);trackPt(b);""",
     """    function line(a,b,lay,objId,rg){
      a=W(a);b=W(b);   /* __acad3dV104 */
      trackPt(a);trackPt(b);"""),
    ("""    function text(pt,str,h,lay,objId,rg){
      trackPt(pt);""",
     """    function text(pt,str,h,lay,objId,rg){
      pt=W(pt);   /* __acad3dV104 */
      trackPt(pt);"""),
    ("""      if(!outer||outer.length<3||!inner||inner.length<3)return;
      var q;for(q=0;q<outer.length;q++)trackPt(outer[q]);for(q=0;q<inner.length;q++)trackPt(inner[q]);""",
     """      if(!outer||outer.length<3||!inner||inner.length<3)return;
      outer=WL(outer);inner=WL(inner);   /* __acad3dV104 */
      var q;for(q=0;q<outer.length;q++)trackPt(outer[q]);for(q=0;q<inner.length;q++)trackPt(inner[q]);"""),
    # --- sheet viewport: offset through its projection
    ("""    var parts=[],strokeW=0.18,drew=false;""",
     """    var parts=[],strokeW=0.18,drew=false;
    var EX=[0,0,0];   /* __acad3dV104: the current object's offset, applied at projection */
    var projLocal=projPt;
    projPt=function(wx,wz,wy){
      return projLocal(wx+EX[0],wz+EX[2],(wy==null||!isFinite(wy))?wy:wy+EX[1]);
    };"""),
    # --- per-object offset, at the top of each exporter's loop (DXF and SVG share the text)
    ("""    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;""",
     """    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;
      EX=bimExportOffset(o);   /* __acad3dV104 */"""),
    ("""      var b=o.bim;
      var rg=pres?bimResolveGraphics(o,'presentation'):null;
      if(b&&b.type==='wall'&&b.centerline){
        poly(b.centerline,!!b.closed,o.id,b.baseY,rg,false);""",
     """      var b=o.bim;
      EX=bimExportOffset(o);   /* __acad3dV104 */
      var rg=pres?bimResolveGraphics(o,'presentation'):null;
      if(b&&b.type==='wall'&&b.centerline){
        poly(b.centerline,!!b.closed,o.id,b.baseY,rg,false);"""),
    # --- viewport framing sees every kind of object
    ("""      var bb=objBBox(o);if(!bb)continue;
      for(j=0;j<8;j++){""",
     """      var bb=bimWorldBounds([o.id]);if(!bb)continue;   /* __acad3dV104: sketches, rooms, text, parcels too */
      for(j=0;j<8;j++){"""),
    # --- import: the inverse, for every entity
    ("""            o=bimMakeImportedSketch([[e.p1[0]*scale,e.p1[1]*scale],[e.p2[0]*scale,e.p2[1]*scale]],baseY+(e.p1[2]||0)*scale,false);""",
     """            o=bimMakeImportedSketch([bimDxfToModel(e.p1[0],e.p1[1],scale),bimDxfToModel(e.p2[0],e.p2[1],scale)],baseY+(e.p1[2]||0)*scale,false);   /* __acad3dV104 */"""),
    ("""            var pts=e.pts.map(function(p){return [p[0]*scale,p[1]*scale];});""",
     """            var pts=e.pts.map(function(p){return bimDxfToModel(p[0],p[1],scale);});   /* __acad3dV104 */"""),
    ("""            o=bimMakeImportedSketch(pts,baseY,!!e.closed,e.bulges);""",
     """            o=bimMakeImportedSketch(pts,baseY,!!e.closed,bimDxfBulgesToModel(e.bulges));"""),
    ("""            for(k=0;k<n;k++){var an=k/n*Math.PI*2;cpts.push([(e.c[0]+Math.cos(an)*e.r)*scale,(e.c[1]+Math.sin(an)*e.r)*scale]);}""",
     """            for(k=0;k<n;k++){var an=k/n*Math.PI*2;cpts.push(bimDxfToModel(e.c[0]+Math.cos(an)*e.r,e.c[1]+Math.sin(an)*e.r,scale));}"""),
    ("""            var ap1=[(e.c[0]+Math.cos(a1)*e.r)*scale,(e.c[1]+Math.sin(a1)*e.r)*scale];
            var ap2=[(e.c[0]+Math.cos(a2)*e.r)*scale,(e.c[1]+Math.sin(a2)*e.r)*scale];
            o=bimMakeImportedSketch([ap1,ap2],baseY+(e.c[2]||0)*scale,false,[Math.tan(sweep/4),0]);""",
     """            var ap1=bimDxfToModel(e.c[0]+Math.cos(a1)*e.r,e.c[1]+Math.sin(a1)*e.r,scale);
            var ap2=bimDxfToModel(e.c[0]+Math.cos(a2)*e.r,e.c[1]+Math.sin(a2)*e.r,scale);
            /* __acad3dV104: counter-clockwise in DXF is clockwise in the model -- the bulge flips */
            o=bimMakeImportedSketch([ap1,ap2],baseY+(e.c[2]||0)*scale,false,[-Math.tan(sweep/4),0]);"""),
    ("""    var verts=pts3.map(function(p){return [p[0]*scale,baseY+(p[2]||0)*scale,p[1]*scale];});""",
     """    var verts=pts3.map(function(p){return [p[0]*scale,baseY+(p[2]||0)*scale,-p[1]*scale];});   /* __acad3dV104: north up */"""),
]
EDITS = [(a, js_ascii(b)) for (a, b) in EDITS]
COUNTS = {"""    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;""": 2}
for old, new in EDITS:
    n = COUNTS.get(old, 1)
    assert txt.count(old) == n, 'anchor count %d (want %d) for %r' % (txt.count(old), n, old[:70])
    txt = txt.replace(old, new)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
