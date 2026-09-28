"""falsify_phase90.py -- break the V90 build six ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the arc no longer leaves tangent: it uses the chord direction instead of the heading.
    'not_tangent': [(
        "      var tb=heading?bimTangentBulge(heading,sk.pts[segIdx],[gx,gz]):null;",
        "      var tb=heading?bimTangentBulge([1,0],sk.pts[segIdx],[gx,gz]):null;")],
    # 2. the prompt offers Arc when the key would refuse it -- prompt and key drift apart.
    'prompt_lies': [(
        "    if(sk&&sk.arcMode)o.push('Line');\n    else if(bimCanArc(sk))o.push('Arc');",
        "    if(sk&&sk.arcMode)o.push('Line');\n    else if(sk.tool==='wall'||sk.tool==='poly')o.push('Arc');")],
    # 3. the offset keeps the original bulge instead of recomputing it from the moved endpoints.
    'offset_keeps_bulge': [(
        "      outBulges.push(bimArcBulgeBetween(sg.center,outPts[i],outPts[(i+1)%n],sg.bulge));",
        "      outBulges.push(sg.bulge);")],
    # 4. the offset arc is not concentric: the radius moves the wrong way.
    'offset_wrong_side': [(
        "    var nr=arc.radius-s*dist;",
        "    var nr=arc.radius+s*dist;")],
    # 5. Undo leaves the bulge behind, so every later arc describes the wrong segment.
    'undo_keeps_bulge': [(
        "    if(sk.bulges&&sk.bulges.length>Math.max(0,sk.pts.length-1))sk.bulges.length=Math.max(0,sk.pts.length-1);",
        "    if(false)sk.bulges.length=0;")],
    # 6. the bulge is written to the wrong segment index -- off by one.
    'bulge_off_by_one': [(
        "      sk.bulges[segIdx]=tb;",
        "      sk.bulges[segIdx===0?0:segIdx-1]=tb;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV90' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
