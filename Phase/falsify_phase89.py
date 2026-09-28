"""falsify_phase89.py -- break the V89 build five ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the builder stores what it flattened, so every rebuild re-tessellates the centerline.
    'stores_flattened': [(
        "    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};",
        "    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:cleanPts.slice()};")],
    # 2. one rebuild path forgets the bulges -- the silent straightener this phase guards against.
    'rebuild_drops_bulges': [(
        "    var res=bimBuildWallGeometry(b.centerline,b.baseY,newHeight,newThickness,newAlign,b.closed,b.bulges);",
        "    var res=bimBuildWallGeometry(b.centerline,b.baseY,newHeight,newThickness,newAlign,b.closed,null);")],
    # 3. a mirrored curve keeps its sign, so it bows the wrong way.
    'mirror_keeps_sign': [(
        "      if(newBulges&&xf&&xf.kind==='mirror')\n        newBulges=newBulges.map(function(bv){return -bv;});",
        "      if(false)newBulges=null;")],
    # 4. wall length goes back to the chord.
    'length_is_chord': [(
        "  function bimWallLength(centerline,closed,bulges){\n    if(!centerline||centerline.length<2)return 0;\n    return bimBulgedLength(centerline,bulges||null,!!closed);",
        "  function bimWallLength(centerline,closed,bulges){\n    if(!centerline||centerline.length<2)return 0;\n    return bimBulgedLength(centerline,null,!!closed);")],
    # 5. the fillet takes its turn direction from the wall-back vectors instead of travel.
    'fillet_sign_from_back_vectors': [(
        "    var inDir=[-ra.u[0],-ra.u[1]],outDir=rb.u;",
        "    var inDir=ra.u,outDir=rb.u;")],
    # 6. BREAK stops refusing, so it straightens a curved wall while reporting success.
    'break_eats_curve': [(
        "      if(bimRefuseIfCurved(w,'Break'))return false;   /* __acad3dV89 */",
        "      if(false)return false;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV89' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
