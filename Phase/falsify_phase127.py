"""falsify_phase127.py -- break the V127 build one way at a time, keeping the marker.

Each variant takes back one thing V127 does, or gets one formula wrong, and the V127 suite must fail
on every one of them. Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 127a: the horizontal geometry
    'tangent_uses_sin': [("pi.R=R;pi.T=R*Math.tan(pi.D/2);", "pi.R=R;pi.T=R*Math.sin(pi.D/2);")],
    'curve_length_chord': [("pi.L=R*pi.D;", "pi.L=2*R*Math.sin(pi.D/2);")],
    'external_wrong': [("pi.E=R*(1/Math.cos(pi.D/2)-1);", "pi.E=R*(1-Math.cos(pi.D/2));")],
    'no_overlap_check': [("      if(pis[j].T+pis[j+1].T>legs[j].len+1e-9)\n", "      if(false)\n")],
    'centre_wrong_side': [("nrm=pk.turn>0?[-u[1],u[0]]:[u[1],-u[0]];", "nrm=pk.turn>0?[u[1],-u[0]]:[-u[1],u[0]];")],
    'sta0_ignored': [("var sta0=isFinite(o.sta0)?o.sta0:0,legs=[],pis=[];", "var sta0=0,legs=[],pis=[];")],
    'offset_left_positive': [("off:dx*(-f.d[1])+dz*f.d[0]};", "off:-(dx*(-f.d[1])+dz*f.d[0])};")],
    'arc_station_chord': [("        t=da*e.R;\n", "        t=2*e.R*Math.sin(da/2);\n")],
    'beyond_never': [("beyond:(best.sta<=g.sta0+1e-9&&along<-1e-6)?'before the start'", "beyond:false?'before the start'")],
    'station_format_hundreds': [("var neg=s<0,a=Math.abs(s),k=Math.floor(a/1000+1e-9),m=a-k*1000;", "var neg=s<0,a=Math.abs(s),k=Math.floor(a/100+1e-9),m=a-k*100;")],
    # ---- 127a: the profile and the ground
    'parabola_half': [("return {elev:p.elev-p.gIn*p.L/2+p.gIn*x+(p.gOut-p.gIn)*x*x/(2*p.L)", "return {elev:p.elev-p.gIn*p.L/2+p.gIn*x+(p.gOut-p.gIn)*x*x/(4*p.L)")],
    'curve_grade_constant': [(",grade:p.gIn+(p.gOut-p.gIn)*x/p.L,onCurve:i};", ",grade:p.gIn,onCurve:i};")],
    'high_point_at_pvi': [("var x=Math.abs(p.gOut-p.gIn)>1e-15?-p.gIn*p.L/(p.gOut-p.gIn):-1;", "var x=p.L/2;")],
    'k_uses_fraction': [("p.K=Math.abs(p.A)>1e-12?p.L/Math.abs(p.A):Infinity;", "p.K=Math.abs(p.A)>1e-12?p.L/Math.abs(p.A/100):Infinity;")],
    'profile_range_unchecked': [("    if(g&&!g.error&&(v[0].sta<g.sta0-1e-6||v[n-1].sta>g.sta1+1e-6))\n", "    if(false)\n")],
    'vertical_overlap_unchecked': [("      if(v[i].L>0&&(v[i].pvc<lo-1e-9||v[i].pvt>hi+1e-9))\n", "      if(false)\n")],
    'tin_nearest_vertex': [("if(l1>=-1e-9&&l2>=-1e-9&&l1+l2<=1+1e-9)return H[tr[0]]+l1*(H[tr[1]]-H[tr[0]])+l2*(H[tr[2]]-H[tr[0]]);",
                            "if(l1>=-1e-9&&l2>=-1e-9&&l1+l2<=1+1e-9)return H[tr[0]];")],
    'fit_radius_ignores_legs': [("    var r=Math.min(BIM_ALIGN_R0,fit*0.95);", "    var r=BIM_ALIGN_R0;")],
    'arc_polyline_accepted': [("    if(bimHasBulge(o.bulges)){a3dToast('An alignment is built from straight legs", "    if(false){a3dToast('An alignment is built from straight legs")],
    'polyline_kept': [("    if(ix>=0)A3D.objs.splice(ix,1,al);else A3D.objs.push(al);", "    A3D.objs.push(al);")],
    # ---- 127b: drawing, picking, transforms
    'no_major_labels': [("            rec.majors.push(s);\n", "")],
    'no_pc_labels': [("        rec.pcpt.push(gp[j].t+' '+bimFmtStation(gp[j].s));\n", "")],
    'profile_view_not_drawn': [("      var ground=bimAlignGround(o,g),F=bimProfileViewFrame(o,g,pg,ground);\n      if(F){", "      var ground=bimAlignGround(o,g),F=bimProfileViewFrame(o,g,pg,ground);\n      if(false){")],
    'profile_view_not_picked': [("      if(F&&!best){", "      if(false){")],
    'mirror_drops_alignment': [("    else if(g.kind==='alignment'){   /* __acad3dV127 */\n      A3D.counts.alignment", "    else if(false){\n      A3D.counts.alignment")],
    'rotate_ignores_pis': [("  function bimRotateObjectInPlace(o,center,angleRad){\n    var transformPt=function(p){return bimRotatePoint(p,center,angleRad);};",
                            "  function bimRotateObjectInPlace(o,center,angleRad){\n    if(o.t==='alignment')return true;\n    var transformPt=function(p){return bimRotatePoint(p,center,angleRad);};")],
    # ---- 127c: editing and commands
    'edit_not_checked': [("    if(g.error){a3dToast(o.name+' was not changed: '+g.error);refreshProps();return false;}", "")],
    'edit_no_undo': [("    if(c.profile){var pg=bimProfileGeom(c.profile,g);if(pg.error){a3dToast(o.name+'\\'s profile was not changed: '+pg.error);refreshProps();return false;}}\n    pushUndo();",
                      "    if(c.profile){var pg=bimProfileGeom(c.profile,g);if(pg.error){a3dToast(o.name+'\\'s profile was not changed: '+pg.error);refreshProps();return false;}}")],
    'sta0_leaves_profile': [("var d=v-c.sta0;c.sta0=v;if(c.profile)", "var d=v-c.sta0;c.sta0=v;if(false)")],
    'addpvi_no_split': [("    v.splice(best+1,0,{sta:+sm.toFixed(3)", "    if(false)v.splice(best+1,0,{sta:+sm.toFixed(3)")],
    'station_not_live': [("      bimStationAt(sk.alignId,[gx,gz]);\n", "      A3D.sk=null;\n")],
    'profileview_at_origin': [("c.profileView={at:[pt[0]-q[0],pt[1]-q[2]],", "c.profileView={at:[0,0],")],
    'no_alignment_pages': [("    if(bimIsAlignment(o))h+=bimAlignPropsHtml(o);       /* __acad3dV127 */\n", "")],
    'no_site_button': [("'bim:truenorth','bim:alignment']}", "'bim:truenorth']}")],
    # ---- 127d: the tables and export
    'schedule_pc_is_pt': [("pc:p.T>0?bimFmtStation(p.pc):''", "pc:p.T>0?bimFmtStation(p.pt):''")],
    'dxf_no_labels': [("        for(alD=0;alD<axD.labels.length;alD++)text(axD.labels[alD].p,axD.labels[alD].t,0.25,lay);\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV127' in txt
out.write_text(txt, encoding='utf-8')
