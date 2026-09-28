"""falsify_phase111.py -- break the V111 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_axis_rings': [("    if(g.caps.tilt){\n      defs.push({axis:'x',kind:'tilt',A:fr.x,B:fr.z,C:fr.y});", "    if(false){\n      defs.push({axis:'x',kind:'tilt',A:fr.x,B:fr.z,C:fr.y});")],
    'no_screen_ring': [("      if(1-Math.abs(vdot(fr.y,vd))>0.03)\n        defs.push({axis:'view',kind:'view',A:vd.slice(),B:V.r.slice(),C:V.u.slice()});", "      if(false)\n        defs.push({axis:'view',kind:'view',A:vd.slice(),B:V.r.slice(),C:V.u.slice()});")],
    'screen_ring_in_plan': [("      if(1-Math.abs(vdot(fr.y,vd))>0.03)", "      if(true)")],
    'screen_ring_same_size': [("      var RR=(D.kind==='view')?R*A3D_GIZ.viewRing:(D.kind==='vertical'?g.ring.R:R);", "      var RR=(D.kind==='view')?R:(D.kind==='vertical'?g.ring.R:R);")],
    'vertical_ring_radius': [("(D.kind==='vertical'?g.ring.R:R)", "(D.kind==='vertical'?g.ring.R*1.07:R)")],
    'wall_gets_tilt_rings': [("    }else{\n      defs.push({axis:'y',kind:'vertical',A:[0,1,0],B:[1,0,0],C:[0,0,1]});\n    }", "    }else{\n      defs.push({axis:'y',kind:'vertical',A:[0,1,0],B:[1,0,0],C:[0,0,1]});\n      defs.push({axis:'x',kind:'tilt',A:fr.x,B:fr.z,C:fr.y});\n    }")],
    'everything_near': [("        near=(D.kind==='view')||(s[2]<=so[2]);", "        near=true;")],
    'near_flag_inverted': [("        near=(D.kind==='view')||(s[2]<=so[2]);", "        near=(D.kind==='view')||(s[2]>so[2]);")],
    'far_half_picked_first': [("    var hr=bimPickGizmoRing(g,x,y,true);\n    if(hr)return hr;\n    if(g.uniform&&bimGizInTri(g.uniform.tri,x,y))return {kind:'uniform',giz:g};\n    hr=bimPickGizmoRing(g,x,y,false);", "    var hr=bimPickGizmoRing(g,x,y,false);\n    if(hr)return hr;\n    if(g.uniform&&bimGizInTri(g.uniform.tri,x,y))return {kind:'uniform',giz:g};\n    hr=bimPickGizmoRing(g,x,y,true);")],
    'far_half_not_pickable': [("    hr=bimPickGizmoRing(g,x,y,false);\n    if(hr)return hr;\n    return null;", "    return null;")],
    'ring_halves_not_separated': [("      var isNear=!!(r.pts[i][2]&&r.pts[i+1][2]);\n      if(isNear!==nearHalf)continue;", "")],
    'view_ring_not_about_camera': [("        defs.push({axis:'view',kind:'view',A:vd.slice(),B:V.r.slice(),C:V.u.slice()});", "        defs.push({axis:'view',kind:'view',A:[0,1,0],B:[1,0,0],C:[0,0,1]});")],
    'view_ring_left_handed': [("        defs.push({axis:'view',kind:'view',A:vd.slice(),B:V.r.slice(),C:V.u.slice()});", "        defs.push({axis:'view',kind:'view',A:vd.slice(),B:V.u.slice(),C:V.r.slice()});")],
    'no_uniform_triangle': [("    geom.uniform=bimGizmoUniformGeom(geom,V,W,H);   /* __acad3dV111 */", "    geom.uniform=null;   /* __acad3dV111 */")],
    'triangle_without_three_axes': [("    if(!g.scales||g.scales.length<3||!isFinite(R)||R<=0)return null;", "    if(!g.scales||g.scales.length<1||!isFinite(R)||R<=0)return null;")],
    'uniform_scales_one_axis': [("    return {giz:true,gk:'scale',axis:null,uniform:true,radial:true,L0:L,sox:g.ox,soy:g.oy,", "    return {giz:true,gk:'scale',axis:(g.scales[0]||{}).axis||'x',uniform:false,radial:true,L0:L,sox:g.ox,soy:g.oy,")],
    'uniform_factor_from_press': [("      var rx=xy[0]-drag.sox,ry=xy[1]-drag.soy;\n      s=Math.sqrt(rx*rx+ry*ry)/drag.L0;", "      var rx=xy[0]-drag.x0,ry=xy[1]-drag.y0;\n      s=1+Math.sqrt(rx*rx+ry*ry)/drag.L0;")],
    'no_hover_tracking': [("      if(hk!==A3D.gizHover){\n        A3D.gizHover=hk;", "      if(false){\n        A3D.gizHover=hk;")],
    'hover_never_clears': [("      var hh=bimPickGizmo(hxy[0],hxy[1]);", "      var hh=bimPickGizmo(hxy[0],hxy[1])||{kind:'centre'};")],
    'hover_names_by_key': [("        A3D.gizHoverName=hh?bimGizmoHandleName(hh).replace(/^the /,'').toUpperCase():null;", "        A3D.gizHoverName=hh?String(bimGizmoHoverKey(hh)).toUpperCase():null;")],
    'ring_name_by_axis_key': [("    if(h.kind==='tilt')return 'the '+bimGizRingLab(h.arc)+' rotate ring';", "    if(h.kind==='tilt')return 'the '+h.axis.toUpperCase()+' rotate ring';")],
    'pick_surface_hand_listed': [("    var k=bimGizmoHoverKey(h);\n    return (k&&k.indexOf('axis:')===0)?k.slice(5):k;", "    if(h.rot)return 'rotate';\n    if(h.kind==='centre')return 'centre';\n    if(h.kind==='plane')return 'plane:'+h.plane.k;\n    if(h.kind==='scale')return 'scale:'+h.axis;\n    if(h.kind==='tilt')return 'tilt:'+h.axis;\n    return h.axis;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV111' in txt
out.write_text(txt, encoding='utf-8')
