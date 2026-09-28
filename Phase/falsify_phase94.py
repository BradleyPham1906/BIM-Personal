"""falsify_phase94.py -- break the V94 build ten ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the clipper written from a slope: every direction works except the one drafters use.
    'clip_from_slope': [(
        "      if(Math.abs(p[i])<1e-12){\n"
        "        /* Parallel to this pair of edges. Outside them, no value of t brings it in. */\n"
        "        if(q[i]<0)return null;\n"
        "        continue;\n"
        "      }",
        "      if(Math.abs(p[i])<1e-12){return null;}")],
    # 2. a ray stops being half a line: it runs backwards like an xline.
    'ray_runs_both_ways': [(
        "    var tMin=isRay?0:-Infinity,tMax=Infinity;",
        "    var tMin=-Infinity,tMax=Infinity;")],
    # 3. the crossing test bounds the wrong parameter, so crossings land past the wall's end.
    'crossing_bounds_swapped': [(
        "    if(u<-1e-9||u>1+1e-9)return null;\n    if(isRay&&t<-1e-9)return null;",
        "    if(t<-1e-9||t>1+1e-9)return null;\n    if(isRay&&u<-1e-9)return null;")],
    # 4. the drawing extent becomes a constant: right on a room, short on a bridge.
    'extent_is_constant': [(
        "    if(!any){mnx=-10;mxx=10;mnz=-10;mxz=10;}",
        "    mnx=-10;mxx=10;mnz=-10;mxz=10;any=true;")],
    # 5. a construction line sets the extent it is drawn across, which runs away.
    'cline_sets_extent': [(
        "      if(bimIsCline(o))continue;           /* an infinite line cannot set the extent it needs */",
        "      if(bimIsCline(o)&&false)continue;")],
    # 6. the prompt advertises a mode nothing implements -- the V86 fault.
    'prompt_offers_bisect': [(
        "    return out;\n  }\n  function bimClineModeForKey(k){",
        "    out.push('Bisect');\n    return out;\n  }\n  function bimClineModeForKey(k){")],
    # 7. the arc sweep is ignored, so a crossing on the unswept half counts.
    'arc_ignores_sweep': [(
        "      if(bimPointOnSweptArc(arc,hits[i],1e-7))out.push(hits[i]);",
        "      out.push(hits[i]);")],
    # 8. the construction line is not offered as a snap target at all.
    'no_crossing_snap': [(
        "          hits=bimClineCrossings(C.p,C.dir,C.ray,moved,src.bulges,src.closed);",
        "          hits=[];")],
    # 9. the Canvas-era gate goes back to swallowing V, H and N.
    'gate_swallows_letters': [(
        "      try{ if(window.__a3dOn&&window.__a3dWantsKey&&window.__a3dWantsKey(e))return; }catch(err4){}\n      e.stopImmediatePropagation();return;",
        "      e.stopImmediatePropagation();return;")],
    # 10. a POINT goes back to being unclickable, as it was in V93.
    'point_unpickable': [(
        "      if(bimIsPoint(o)){\n"
        "        var pp=toScreen(bimWorldPt(o,o.pts[0],o.y),V,W,H);",
        "      if(false){\n"
        "        var pp=toScreen(bimWorldPt(o,o.pts[0],o.y),V,W,H);")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV94' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
