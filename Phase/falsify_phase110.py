"""falsify_phase110.py -- break the V110 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'dispatcher_local_frame': [("    if(q[0]||q[2])transformPt=function(p){", "    if(false)transformPt=function(p){")],
    'primitive_not_materialized': [("    var srcMesh=o.mesh||bimPrimitiveMesh(o);", "    var srcMesh=o.mesh;")],
    'mirror_winding_kept': [("      var newF=(xf&&xf.kind==='mirror')?", "      var newF=(false)?")],
    'mirror_copy_at_origin': [("    var g=bimComputeTransformedGeometry(o,transformPt,{kind:'mirror',P1:P1,P2:P2});\n    if(g.error)return g;\n    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:bimObjOffset(o),",
                               "    var g=bimComputeTransformedGeometry(o,transformPt,{kind:'mirror',P1:P1,P2:P2});\n    if(g.error)return g;\n    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:[0,0,0],")],
    'array_copy_at_origin': [("  function bimBuildArrayCopyFromGeometry(o,g){\n    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:bimObjOffset(o),",
                              "  function bimBuildArrayCopyFromGeometry(o,g){\n    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:[0,0,0],")],
    'no_materialized_toast': [("    var n=A3D_MATERIALIZED.length;\n    if(!n)return 0;", "    var n=A3D_MATERIALIZED.length;\n    if(n||!n)return 0;")],
    'materialized_keeps_prm': [("    o.mesh=mesh;\n    delete o.prm;\n    o.t='solid';", "    o.mesh=mesh;")],
    'ring_turn_not_reported': [("      bimFlushMaterialized();   /* __acad3dV110: a turned primitive says it is now a plain solid */\n", "")],
    'y_axis_south': [("    return {x:[1,0,0],z:[0,0,-1],y:[0,1,0],mode:'world',asked:asked,fallback:false};", "    return {x:[1,0,0],z:[0,0,1],y:[0,1,0],mode:'world',asked:asked,fallback:false};")],
    'y_axis_blue': [("    {k:'z',col:'#5ec98a',lab:'Y'},", "    {k:'z',col:'#4ea1ff',lab:'Y'},")],
    'origin_y_up': [("    {k:'Y',to:[0,0,-13],col:'#4f8a5f'},", "    {k:'Y',to:[0,13,0],col:'#4f8a5f'},")],
    'ray_mismatch': [("    var a=(sx-W/2)/f,b=(H/2-sy)/f;\n    var d=[V.r[0]*a+V.u[0]*b-V.d[0],", "    var a=(sx-W/2)/(f*1.08),b=(H/2-sy)/(f*1.08);\n    var d=[V.r[0]*a+V.u[0]*b-V.d[0],")],
    'plane_grid_ignored': [("      if(gs){da=Math.round(da/gs)*gs;db=Math.round(db/gs)*gs;}\n", "")],
    'plane_leaves_plane': [("      v=[drag.a[0]*da+drag.b[0]*db,drag.a[1]*da+drag.b[1]*db,drag.a[2]*da+drag.b[2]*db];", "      v=[drag.a[0]*da+drag.b[0]*db,drag.a[1]*da+drag.b[1]*db+0.05,drag.a[2]*da+drag.b[2]*db];")],
    'plane_quadrant_unmeasured': [("        if(k===0&&cl>=A3D_GIZ.planeClear){best={q:q,cl:cl};break;}", "        if(k===0){best={q:q,cl:cl};break;}")],
    'centre_plan_uses_screen': [("    }else if(A3D.flat){\n      a=g.frame.x;b=g.frame.z;", "    }else if(false){\n      a=g.frame.x;b=g.frame.z;")],
    'scale_ignores_pos': [("        var v=base.v[i],wx=v[0]+q[0]-O[0],wy=v[1]+q[1]-O[1],wz=v[2]+q[2]-O[2];", "        var v=base.v[i],wx=v[0]-O[0],wy=v[1]-O[1],wz=v[2]-O[2];")],
    'uniform_ignored': [("    var M=drag.uniform?[s,0,0,0,s,0,0,0,s]:bimGizScaleMat(drag.dir,s);", "    var M=bimGizScaleMat(drag.dir,s);")],
    'shift_pans_scale_box': [("      if(gz&&(!ev.shiftKey||gz.kind==='scale')){", "      if(gz&&!ev.shiftKey){")],
    'arcs_not_refused': [("    if(!uniform&&g.caps.arcs){", "    if(false){")],
    'sketch_even_scale_3d': [("      var Mo=(drag.uniform&&bimGizmoKind(o)==='sketch')?Mplan:M;", "      var Mo=M;")],
    'caps_any_not_all': [("    return {tilt:n>0&&solids===n,scale:sc,", "    return {tilt:solids>0,scale:sc,")],
    'wall_scales': [("      sc[keys[i]]=allScal&&(sketches===0||Math.abs(fr[keys[i]][1])<1e-6);", "      sc[keys[i]]=solids>0||sketches>0;")],
    'sketch_scales_vertically': [("      sc[keys[i]]=allScal&&(sketches===0||Math.abs(fr[keys[i]][1])<1e-6);", "      sc[keys[i]]=allScal;")],
    'tilt_left_handed': [("    var M=bimGizRotMat(drag.A,d),i,failed=0;", "    var M=bimGizRotMat(drag.A,-d),i,failed=0;")],
    'tilt_ortho_ignored': [("    drag.tiltAngle=d;\n    bimGizmoRestoreObjs(drag.ids,drag.snap);", "    d=d*1.0003;drag.tiltAngle=d;\n    bimGizmoRestoreObjs(drag.ids,drag.snap);")],
    'menu_never_opens': [("    if(gizMenu&&!moved){bimOpenGizmoMenu(gizMenu.x,gizMenu.y);return;}   /* __acad3dV110 */\n", "")],
    'right_drag_opens_menu': [("    if(gizMenu&&!moved){bimOpenGizmoMenu(gizMenu.x,gizMenu.y);return;}", "    if(gizMenu){bimOpenGizmoMenu(gizMenu.x,gizMenu.y);return;}")],
    'escape_not_consumed': [("    if(ev.key==='Escape'&&document.getElementById('a3d-gizmenu')){\n      bimCloseGizmoMenu();\n      ev.preventDefault();ev.stopImmediatePropagation();\n      return;\n    }\n", "")],
    'local_ignored': [("      if(dir)return {x:[dir[0],0,dir[1]],z:[dir[1],0,-dir[0]],y:[0,1,0],mode:'local',asked:asked,fallback:false};", "      if(false)return {x:[dir[0],0,dir[1]],z:[dir[1],0,-dir[0]],y:[0,1,0],mode:'local',asked:asked,fallback:false};")],
    'wall_local_ignored': [("    if(o.bim.type==='wall'&&o.bim.centerline&&o.bim.centerline.length>=2){\n      var a=o.bim.centerline[0],b=o.bim.centerline[1];", "    if(false){\n      var a=o.bim.centerline[0],b=o.bim.centerline[1];")],
    'view_ignored': [("    if(asked==='view'){\n      var V=camVecs(A3D.cam);", "    if(false){\n      var V=camVecs(A3D.cam);")],
    'hide_ignored': [("&&!A3D.sheetCapture&&!A3D.gizHidden;", "&&!A3D.sheetCapture;")],
    'gizmo_cmd_noop': [("    gizmo:function(){bimGizmoCommand();},", "    gizmo:function(){},")],
    'mirror_arc_dropped': [("      if(o.bulges)copy.bulges=o.bulges.map(function(bv){return -bv;});}   /* __acad3dV110: arcs kept, reflected */", "      }")],
    'mirror_arc_not_reflected': [("      if(o.bulges)copy.bulges=o.bulges.map(function(bv){return -bv;});}", "      if(o.bulges)copy.bulges=o.bulges.slice();}")],
    'array_arc_dropped': [("      if(o.bulges)copy.bulges=o.bulges.slice();}   /* __acad3dV110: a turned arc is the same arc */", "      }")],
    'handle_name_by_key': [("    return 'the '+bimGizAxis(h.axis).lab+' move handle';", "    return 'the '+h.axis.toUpperCase()+' move handle';")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV110' in txt
out.write_text(txt, encoding='utf-8')
