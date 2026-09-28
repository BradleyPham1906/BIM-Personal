"""falsify_phase88.py -- break the V88 build five ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the sign error the prototype caught, put back.
    'flipped_perpendicular': [(
        "    var mx=uz,mz=-ux;                     /* chord direction rotated -90deg; see the note above */",
        "    var mx=-uz,mz=ux;")],
    # 2. ARC tessellates on the way in instead of storing an arc: draws identically, stores chords.
    'arc_tessellates': [(
        "    var arc=bimBulgeArc(p1,p2,b);\n    return addSketchObj([[p1[0],p1[1]],[p2[0],p2[1]]],\n      {bulges:[b,0],closed:false,",
        "    var arc=bimBulgeArc(p1,p2,b);\n    return addSketchObj(bimFlattenPoly([[p1[0],p1[1]],[p2[0],p2[1]]],[b,0],false),\n      {closed:false,")],
    # 3. picking goes back to the chord.
    'pick_uses_chord': [(
        "      var pts=bimFlattenSketch(o),n=pts.length,segCount=(o.closed!==false)?n:n-1,k;",
        "      var pts=o.pts,n=pts.length,segCount=(o.closed!==false)?n:n-1,k;")],
    # 4. the DXF export drops the bulge, so an arc leaves as a straight chord.
    'dxf_drops_bulge': [(
        "        var bq=bimBulgeAt(bulges,q);\n        if(Math.abs(bq)>BIM_BULGE_EPS)out+=P(42,bq.toFixed(8));",
        "        var bq=0;")],
    # 5. every sketch gains a bulges key, so straight geometry stops being the object it was.
    'always_writes_bulges': [(
        "    if(opts.bulges&&bimHasBulge(opts.bulges))o.bulges=opts.bulges.slice();",
        "    o.bulges=(opts.bulges||pts2.map(function(){return 0;})).slice();")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV88' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
