"""falsify_phase87.py -- deliberately break the V87 build, four ways, keeping the marker.

A suite that has never failed proves nothing about the code. Each variant breaks one thing the
suite claims to measure; each must make the suite FAIL.
"""
import pathlib, sys, shutil

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. EXTEND runs backwards as happily as forwards -- the "forward only" rule gone.
    'backwards_extend': [(
        "      if(r.t<1e-9)continue;                       /* forward only: EXTEND never runs backwards */",
        "      if(false)continue;")],
    # 2. the typed coordinate lands on sk.pts and nothing acts on it (the pre-V87 behaviour).
    'typed_point_inert': [(
        "    skPlacePoint(p[0],p[1],null);   /* __acad3dV87: the same handler a click reaches */",
        "    sk.pts.push([p[0],p[1]]);\n    if(sk.tool==='rect'&&sk.pts.length>=2)finishRect();\n    else if(sk.tool==='circle'&&sk.pts.length>=2)finishCircle();")],
    # 3. SCALE scales the wall thickness too -- geometry and BIM parameters confused.
    'scale_eats_thickness': [(
        "  function bimScaleObjectInPlace(o,base,k){\n    var transformPt=function(p){return bimScalePoint(p,base,k);};",
        "  function bimScaleObjectInPlace(o,base,k){\n    if(o.bim&&o.bim.thickness)o.bim.thickness*=k;\n    var transformPt=function(p){return bimScalePoint(p,base,k);};")],
    # 4. BREAK keeps only the first piece: one object in, one object out.
    'break_loses_piece': [(
        "      A3D.objs.push(made.obj);\n      A3D.sel=w.id;A3D.sel2=null;A3D.selSet=[w.id,made.obj.id];",
        "      A3D.sel=w.id;A3D.sel2=null;A3D.selSet=[w.id];")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV87' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s (%d bytes)' % (out, len(txt.encode('utf-8'))))
