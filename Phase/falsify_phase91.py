"""falsify_phase91.py -- break the V91 build six ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the arc parameter becomes the CHORD fraction -- right on straight work, wrong on curves.
    'chord_parameter': [(
        "  function bimArcPointAt(arc,t){\n    var a=arc.a1+arc.sweep*t;",
        "  function bimArcPointAt(arc,t){\n    var A=[arc.center[0]+Math.cos(arc.a1)*arc.radius,arc.center[1]+Math.sin(arc.a1)*arc.radius];\n    var B=[arc.center[0]+Math.cos(arc.a2)*arc.radius,arc.center[1]+Math.sin(arc.a2)*arc.radius];\n    return [A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t];\n    /*unreachable*/var a=arc.a1+arc.sweep*t;")],
    # 2. the swept-range filter is dropped: intersections anywhere on the circles count.
    'no_range_filter': [(
        "      if(bimSegRangeOk(A1,B1,b1,hits[i])&&bimSegRangeOk(A2,B2,b2,hits[i]))out.push(hits[i]);",
        "      out.push(hits[i]);")],
    # 3. a split arc keeps the whole arc's bulge instead of recomputing each half.
    'split_keeps_bulge': [(
        "    leftB.push(arc?bimArcBulgeBetween(arc.center,A,Pt,arc.sweep):0);",
        "    leftB.push(arc?bl:0);")],
    # 4. trim drops the bulges on the way out, leaving a straight wall between the same ends.
    'trim_drops_curve': [(
        "    return {pts:keep.pts,bulges:keep.bulges,cutAt:best.pt};",
        "    return {pts:keep.pts,bulges:null,cutAt:best.pt};")],
    # 5. break keeps only the first piece's curve.
    'break_drops_curve': [(
        "      var made=bimNewWallFromSource(w,r.b.pts,false,'Wall',r.b.bulges);",
        "      var made=bimNewWallFromSource(w,r.b.pts,false,'Wall',null);")],
    # 6. the degenerate guard goes back to counting vertices.
    'count_not_length': [(
        "    if(bimBulgedLength(s1.a.pts,s1.a.bulges,false)<1e-9)",
        "    if(s1.a.pts.length<2)")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV91' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
