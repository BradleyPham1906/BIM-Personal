"""falsify_phase93.py -- break the V93 build eight ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. CIRCLE goes back to tessellating, which still looks like a circle and still closes.
    'circle_is_24gon': [(
        "    var cir=bimCircleSketch(c,r);",
        "    var tess=[],ti;for(ti=0;ti<24;ti++){var ta=ti/24*Math.PI*2;"
        "tess.push([c[0]+Math.cos(ta)*r,c[1]+Math.sin(ta)*r]);}\n"
        "    var cir={pts:tess,bulges:null};")],
    # 2. the viewport goes back to drawing the stored points raw: every arc renders as a chord.
    'viewport_draws_chords': [(
        "    var path=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;",
        "    var path=pts;")],
    # 3. the two POLYGON forms stop differing: circumscribed silently becomes inscribed.
    'polygon_forms_identical': [(
        "    var R=circumscribed?radius/Math.cos(Math.PI/sides):radius;",
        "    var R=radius;")],
    # 4. the walk measures CHORDS, so marks bunch up wherever the line bends.
    'walk_measures_chord': [(
        "  function bimSegLengthAt(A,B,bulge){\n    var arc=bimBulgeArc(A,B,bulge);\n"
        "    if(arc)return Math.abs(arc.sweep)*arc.radius;",
        "  function bimSegLengthAt(A,B,bulge){\n    var arc=null;\n"
        "    if(arc)return Math.abs(arc.sweep)*arc.radius;")],
    # 5. MEASURE stops reporting what is left at the far end.
    'measure_hides_leftover': [(
        "    return {points:out,spacing:d,total:total,leftover:total-Math.floor(total/d+1e-9)*d};",
        "    return {points:out,spacing:d,total:total,leftover:0};")],
    # 6. DIVIDE marks the endpoints too, so dividing into 4 places 5 points.
    'divide_marks_ends': [(
        "    for(i=1;i<n;i++){\n      p=bimPointAtLength(pts,bulges,closed,total*i/n);",
        "    for(i=0;i<=n;i++){\n      p=bimPointAtLength(pts,bulges,closed,total*i/n);")],
    # 7. POINT stops repeating: the tool ends after the first click, as every other tool does.
    'point_tool_ends_early': [(
        "      return;                                   /* sk stays live: POINT keeps placing */",
        "      A3D.sk=null;return;")],
    # 8. the outline goes back to the raw points, so a two-vertex circle cannot be extruded.
    'outline_not_flattened': [(
        "  function bimSketchOutline(o){\n    if(!o||!o.pts)return [];\n    return bimFlattenSketch(o)||o.pts;",
        "  function bimSketchOutline(o){\n    if(!o||!o.pts)return [];\n    return o.pts;")],
    # 9. Offset stops naming the point and falls through to a generic message.
    'offset_point_generic': [(
        "    if(bimIsPoint(o))return {error:'Offset: a point has no side to offset to'};   /* __acad3dV93 */\n",
        "")],
    # 10. a point stops being a snap candidate, so nothing can be drawn to it.
    'point_not_snappable': [(
        "      if(o.t==='sketch'&&Math.abs((o.y||0)+q[1]-y0)<0.05){",
        "      if(o.t==='sketch'&&!bimIsPoint(o)&&Math.abs((o.y||0)+q[1]-y0)<0.05){")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV93' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
