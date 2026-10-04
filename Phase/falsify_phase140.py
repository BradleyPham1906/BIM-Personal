"""falsify_phase140.py -- break the V140 build one way at a time, keeping the marker.

Each variant takes back one thing V140 does, and the V140 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the shapes
    'gabled_one_plane': [("        planes.push(bimRoofPlane(V,sv.lo,s1,E),bimRoofPlane([-V[0],-V[1]],-sv.hi,s1,E));", "        planes.push(bimRoofPlane(V,sv.lo,s1,E));")],
    'gable_slope_full_width': [("        s1=roofH/W2;", "        s1=roofH/(2*W2);")],
    'halfhip_no_ends': [("          planes.push(bimRoofPlane(U,su.lo,s1,E+BIM_ROOF_HALFHIP*roofH),bimRoofPlane([-U[0],-U[1]],-su.hi,s1,E+BIM_ROOF_HALFHIP*roofH));", "")],
    'gambrel_no_knee': [("          bimRoofPlane(V,sv.lo+kx*W2,s2,E+ky*roofH),bimRoofPlane([-V[0],-V[1]],-sv.hi+kx*W2,s2,E+ky*roofH));", ");")],
    'mansard_no_upper': [("          planes.push(bimRoofPlane(en,eo,s1,E),bimRoofPlane(en,eo+kx*W2,s2,E+ky*roofH));", "          planes.push(bimRoofPlane(en,eo,s1,E));")],
    'skillion_wrong_way': [("      if(shape==='skillion')planes.push(bimRoofPlane([-V[0],-V[1]],-sv.hi,roofH/(sv.hi-sv.lo),E));", "      if(shape==='skillion')planes.push(bimRoofPlane(V,sv.lo,roofH/(sv.hi-sv.lo),E));")],
    'pyramid_apex_at_corner': [("      var apex=[cx/(3*ar),E+roofH,cz/(3*ar)];", "      var apex=[P[0][0],E+roofH,P[0][1]];")],
    'hip_pitch_unscaled': [("      var s=roofH/tm;", "      var s=1;")],
    'envelope_max_not_min': [("        Q=bimRoofClip(Q,U[i].a-U[j].a,U[i].b-U[j].b,U[i].c-U[j].c);", "        Q=bimRoofClip(Q,U[j].a-U[i].a,U[j].b-U[i].b,U[j].c-U[i].c);")],
    'walls_flat_topped': [("        on.push({s:s,p:tops[j]});", "        if(Math.abs(s)<1e-9||Math.abs(s-1)<1e-9)on.push({s:s,p:tops[j]});")],
    'roof_faces_down': [("    roofs.forEach(function(r){face(r.slice().reverse().map(vid));});", "    roofs.forEach(function(r){face(r.map(vid));});")],
    'concave_allowed': [("    if(!convex&&shape!=='hipped'&&shape!=='flat')return {shape:shape,why:", "    if(false)return {shape:shape,why:")],
    'curved_faked_flat': [("    if(!BIM_ROOF_SHAPES[shape])return {shape:shape,why:", "    if(!BIM_ROOF_SHAPES[shape])shape='flat';if(false)return {shape:shape,why:")],
    # ---- directions
    'direction_ignored': [("      if(dir){V=dir;U=[-dir[1],dir[0]];how='ridge across its roof:direction';}", "      if(false){V=dir;U=[-dir[1],dir[0]];how='ridge across its roof:direction';}")],
    'orientation_ignored': [("      else if(across){V=ob.u;U=ob.v;how=", "      else if(false){V=ob.u;U=ob.v;how=")],
    'compass_degrees_only': [("    var az=BIM_COMPASS.hasOwnProperty(s)?BIM_COMPASS[s]:", "    var az=false?BIM_COMPASS[s]:")],
    'obb_short_side': [("    if(best.v1-best.v0>best.u1-best.u0+1e-9)best=", "    if(best.v1-best.v0<best.u1-best.u0-1e-9)best=")],
    # ---- heights
    'height_tag_on_top': [("    if(hFrom==='height'){total=h;eave=h-roofH;", "    if(false){total=h;eave=h-roofH;")],
    'levels_include_roof': [("    else{eave=h;total=h+roofH;}", "    else{eave=h-roofH;total=h;}")],
    'roof_levels_ignored': [("    if(isFinite(L)&&L>0&&L<50)return {h:L*BIM_CTX_LEVEL_H,from:'roof:levels'};", "")],
    'angle_ignored': [("    if(isFinite(ang)&&ang>0&&ang<85)return {h:Math.tan(ang*BIM_D2R)*half,from:'roof:angle',angle:ang};", "")],
    'no_clamp': [("if(eave<BIM_ROOF_MINWALL){eave=Math.min(BIM_ROOF_MINWALL,h/2);roofH=h-eave;clamped=true;}", "")],
    'part_base_dropped': [("            try{rf=bimOsmRoof(Pp,f.tags,y0+rg.min,rg.h-rg.min,rg.from);}", "            try{rf=bimOsmRoof(Pp,f.tags,y0,rg.h-rg.min,rg.from);}")],
    # ---- the context and labels
    'roof_not_used': [("            try{mesh=(rf&&rf.mesh)?rf.mesh:padMesh(Pp,y0+rg.min,rg.h-rg.min);}", "            try{mesh=padMesh(Pp,y0+rg.min,rg.h-rg.min);}")],
    'lod_stays_1': [("              c.roof=rf.info;c.lod='2.0';c.height=Math.round((rg.min+rf.total)*100)/100;", "              c.roof=rf.info;c.height=Math.round((rg.min+rf.total)*100)/100;")],
    'height_not_total': [("              c.roof=rf.info;c.lod='2.0';c.height=Math.round((rg.min+rf.total)*100)/100;", "              c.roof=rf.info;c.lod='2.0';")],
    'skip_reason_lost': [("            }else if(rf&&rf.why){c.roofSkipped={shape:rf.shape,why:rf.why};", "            }else if(rf&&rf.why){")],
    'roofs_unsaid': [("      bimRoofCountText(nRoofs,nNoRoof)+   /* __acad3dV140 */", "")],
    'no_roof_row': [("    if(c&&c.roof)r+='<div class=\"a3d-prow\" data-lodrow=\"roof\">", "    if(false)r+='<div class=\"a3d-prow\" data-lodrow=\"roof\">")],
    'how_no_roof': [("    if(c.roof){   /* __acad3dV140 */", "    if(false){   /* __acad3dV140 */")],
    # ---- CityJSON
    'cj_roof_from_footprint': [("    if(c&&c.kind==='buildings'&&c.footprint&&c.footprint.length>=3&&!c.roof){", "    if(c&&c.kind==='buildings'&&c.footprint&&c.footprint.length>=3){")],
    'cj_slopes_are_walls': [("    if(n[1]>0.01)return 'roof';   /* __acad3dV140: a sloped roof faces up */", "    if(n[1]>0.99)return 'roof';")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV140' in txt
out.write_text(txt, encoding='utf-8')
