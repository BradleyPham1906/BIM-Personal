"""falsify_phase104.py -- break the V104 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'dxf_no_offset': [("    function DX(p){return (p[0]+EX[0]).toFixed(6);}", "    function DX(p){return (p[0]).toFixed(6);}"),
                      ("    function DY(p){return (-(p[1]+EX[2])).toFixed(6);}", "    function DY(p){return (-(p[1])).toFixed(6);}")],
    'dxf_mirrored': [("    function DY(p){return (-(p[1]+EX[2])).toFixed(6);}", "    function DY(p){return ((p[1]+EX[2])).toFixed(6);}")],
    'dxf_bulge_not_flipped': [("        var bq=-bimBulgeAt(bulges,q);", "        var bq=bimBulgeAt(bulges,q);")],
    'svg_no_offset': [("    function W(p){return [p[0]+EX[0],p[1]+EX[2]];}", "    function W(p){return [p[0],p[1]];}")],
    'svg_mirrored': [("+','+(cmd.pts[q][1]).toFixed(6)+' ';", "+','+(-cmd.pts[q][1]).toFixed(6)+' ';")],
    'svg_viewbox_old': [("var vbX=minX-margin,vbY=minZ-margin,", "var vbX=minX-margin,vbY=-(maxZ)-margin,")],
    'viewport_no_offset': [("      return projLocal(wx+EX[0],wz+EX[2],(wy==null||!isFinite(wy))?wy:wy+EX[1]);", "      return projLocal(wx,wz,wy);")],
    'viewport_framing_meshes_only': [("      var bb=bimWorldBounds([o.id]);if(!bb)continue;", "      var bb=objBBox(o);if(!bb)continue;")],
    'import_mirrored': [("  function bimDxfToModel(x,y,s){return [x*(s||1),-y*(s||1)];}", "  function bimDxfToModel(x,y,s){return [x*(s||1),y*(s||1)];}")],
    'import_arc_bulge_not_flipped': [("            o=bimMakeImportedSketch([ap1,ap2],baseY+(e.c[2]||0)*scale,false,[-Math.tan(sweep/4),0]);",
                                      "            o=bimMakeImportedSketch([ap1,ap2],baseY+(e.c[2]||0)*scale,false,[Math.tan(sweep/4),0]);")],
    'import_poly_bulge_not_flipped': [("  function bimDxfBulgesToModel(b){return b?b.map(function(v){return -(v||0);}):b;}", "  function bimDxfBulgesToModel(b){return b;}")],
    'property_offset_twice': [("    if(!o||bimIsProperty(o))return [0,0,0];   /* derived in world terms already */", "    if(!o)return [0,0,0];")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV104' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
