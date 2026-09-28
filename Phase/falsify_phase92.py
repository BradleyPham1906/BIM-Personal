"""falsify_phase92.py -- break the V92 build six ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the endpoint slides along the CHORD instead of the circle: still longer, wrong arc.
    'grows_along_chord': [(
        "    var ang=seg.atStart?(arc.a1-sign*dTheta):(arc.a2+sign*dTheta);\n"
        "    out[endIdx]=[arc.center[0]+Math.cos(ang)*arc.radius,arc.center[1]+Math.sin(ang)*arc.radius];",
        "    var oth=seg.atStart?seg.B:seg.A,cur=pts[endIdx];\n"
        "    var cdx=cur[0]-oth[0],cdz=cur[1]-oth[1],cL=Math.sqrt(cdx*cdx+cdz*cdz)||1;\n"
        "    out[endIdx]=[cur[0]+cdx/cL*delta,cur[1]+cdz/cL*delta];")],
    # 2. both ends grow the same way, so one of them moves the wrong direction.
    'ends_symmetric': [(
        "    var ang=seg.atStart?(arc.a1-sign*dTheta):(arc.a2+sign*dTheta);",
        "    var ang=seg.atStart?(arc.a1+sign*dTheta):(arc.a2+sign*dTheta);")],
    # 3. EXTEND ranks candidates by distance in space rather than angle swept forward.
    'extend_by_distance': [(
        "        if(!best||turn<best.turn)best={turn:turn,pt:chits[k]};",
        "        var dd=Math.pow(chits[k][0]-pts[endIdx][0],2)+Math.pow(chits[k][1]-pts[endIdx][1],2);\n"
        "        if(!best||dd<best.dd)best={turn:turn,pt:chits[k],dd:dd};")],
    # 4. growing past a full circle is allowed again.
    'no_full_circle_guard': [(
        "    if(Math.abs(newSweep)>=Math.PI*2-1e-9)\n      return {error:'That would take the arc past a full circle'};",
        "    if(false)return {error:'x'};")],
    # 5. shrinking past the other end is allowed, flipping the arc's direction.
    'no_shrink_guard': [(
        "    if(sign*newSweep<0)\n      return {error:'That would shorten the arc past its other end — use Break or Trim for that'};",
        "    if(false)return {error:'x'};")],
    # 6. LENGTHEN measures the chord, so every target length is computed from the wrong start.
    'lengthen_measures_chord': [(
        "    var L=bimBulgedLength(pts,bulges,false);\n    var target;\n    if(mode==='total')target=value;",
        "    var L=bimBulgedLength(pts,null,false);\n    var target;\n    if(mode==='total')target=value;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV92' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
