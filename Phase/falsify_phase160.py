"""falsify_phase160.py -- break the V160 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # the record
    'blank_cover_is_zero': [("var BIM_ZN_ZERO={step:1,front:1,side:1,rear:1,res:1,parkNon:1,frontLeg:1};", "var BIM_ZN_ZERO={step:1,front:1,side:1,rear:1,res:1,parkNon:1,frontLeg:1,cover:1};")],
    'range_unchecked': [("if(!isFinite(v)||v<F[1]||v>F[2]){a3dToast('That value is out of range ('+F[1]+' to '+F[2]+')');bimSaRefresh(true);return false;}", "if(!isFinite(v)){bimSaRefresh(true);return false;}")],
    'edit_not_undoable': [("  function bimZnEdit(fn){\n    pushUndo();", "  function bimZnEdit(fn){")],
    'edit_findings_stale': [("    try{fn();if(bimZnEnvelopeObj())bimZnPlaceEnvelope(true);bimSaFill(true);}finally{undoSuspend=false;}", "    try{fn();if(bimZnEnvelopeObj())bimZnPlaceEnvelope(true);}finally{undoSuspend=false;}")],
    'envelope_not_followed': [("    try{fn();if(bimZnEnvelopeObj())bimZnPlaceEnvelope(true);bimSaFill(true);}finally{undoSuspend=false;}", "    try{fn();bimSaFill(true);}finally{undoSuspend=false;}")],
    # the sides and their rules
    'rear_never_found': [("      if(l.n[0]*L[f].n[0]+l.n[1]*L[f].n[1]<-0.7)l.role='rear';", "      if(l.n[0]*L[f].n[0]+l.n[1]*L[f].n[1]<-1.1)l.role='rear';")],
    'role_pick_ignored': [("      if(o==='front'||o==='side'||o==='rear'){l.role=o;l.auto=false;return;}", "")],
    'step_taken_at_its_height': [("if((side>0?t<=h+1e-9:t<h-1e-9)&&o.steps[k][1]>s)s=o.steps[k][1];", "if(t<=h+1e-9&&o.steps[k][1]>s)s=o.steps[k][1];")],
    'street_wall_ignored': [("      if(r==='front'&&z.baseH!==null&&z.step>0)o.steps.push([z.baseH,(+z.front||0)+z.step]);   /* the street wall, then the stepback */", "")],
    'plane_ignored': [("    if(o.plane){t=(h-o.plane[0])/o.plane[1];if(t>s)s=t;}\n    return s;", "    return s;")],
    'plane_from_setback': [("    if(o.plane){t=(h-o.plane[0])/o.plane[1];if(t>s)s=t;}\n    return s;", "    if(o.plane){t=o.base+(h-o.plane[0])/o.plane[1];if(t>s)s=t;}\n    return s;")],
    # the working
    'plates_at_floor': [("for(i=0;i<nSt;i++){var pa=Math.min(covA,bimZnArea(C,(i+1)*z.f2f,-1));", "for(i=0;i<nSt;i++){var pa=Math.min(covA,bimZnArea(C,i*z.f2f,1));")],
    'coverage_not_capped': [("for(i=0;i<nSt;i++){var pa=Math.min(covA,bimZnArea(C,(i+1)*z.f2f,-1));", "for(i=0;i<nSt;i++){var pa=bimZnArea(C,(i+1)*z.f2f,-1);")],
    'storeys_not_capped': [("var nSt=Math.floor(top/z.f2f+1e-9);if(z.maxStoreys)nSt=Math.min(nSt,z.maxStoreys);", "var nSt=Math.floor(top/z.f2f+1e-9);")],
    'volume_midpoint': [("    return rec(a,b,fa,fm,fb,(b-a)/6*(fa+4*fm+fb),0);", "    return (b-a)*fm;")],
    'far_governs_backwards': [("gov=farGFA===null?'envelope':(farGFA<=cap+1e-6?'FAR':'envelope');", "gov=farGFA===null?'envelope':(farGFA<=cap+1e-6?'envelope':'FAR');")],
    'units_rounded_up': [("units=Math.floor(resN/z.unit+1e-9)", "units=Math.ceil(resN/z.unit-1e-9)")],
    'parking_rounded_down': [("C.parking=Math.ceil(units*z.park+non/100*z.parkNon-1e-9);", "C.parking=Math.floor(units*z.park+non/100*z.parkNon+1e-9);")],
    'split_not_stopped': [("    if(C.split!==null&&top>C.split-0.001)top=Math.max(0,C.split-0.001);", "")],
    # the envelope
    'build_not_undoable': [("    if(!C0.ok){a3dToast('No envelope: '+C0.error);return C0;}\n    pushUndo();", "    if(!C0.ok){a3dToast('No envelope: '+C0.error);return C0;}")],
    'no_terraces': [("          for(j=0;j<m;j++){var j2=(j+1)%m;face([tb+j,tb+j2,prev.b+j2,prev.b+j]);}", "")],
    'no_roof': [("    if(prev)cap(prev.b,prev.R,true);\n    return {v:v,f:f};", "    return {v:v,f:f};")],
    'caps_flipped': [("        face(up?F.reverse():F);   /* a ring that turns positive faces down */", "        face(up?F:F.reverse());")],
    'caps_not_convex': [("    if(convex(all))return [all];", "    return [all];")],
    'caps_left_as_triangles': [("            if(convex(U)){parts[i]=U;parts.splice(j2,1);merged=true;}", "")],
    'envelope_on_active_layer': [("mesh:bimZnMesh(C),col:'#e0b85e',locked:true,layer:ly?ly.id:A3D.activeLayer,", "mesh:bimZnMesh(C),col:'#e0b85e',locked:true,layer:A3D.activeLayer,")],
    # the design against it
    'height_not_checked': [("    if(y>C.top+0.01)return false;\n    var h=Math.max(0,y-0.01)", "    var h=0")],
    'basement_checked': [("    if(y<=0.05)return true;", "")],
    'basement_covers': [("      if((ut==='mass'||ut==='floor')&&lo>-0.5)base.push(", "      if(ut==='mass'||ut==='floor')base.push(")],
    'never_a_redflag': [("cls:gfaOver||hOver?'redflag':'constraint',sev:3", "cls:'constraint',sev:3")],
    # from the layers
    'layer_attrs_misread': [("        var pr=(F[f.fi]&&F[f.fi].p)||{},k,src=", "        var pr=(F[f.fi]&&F[f.fi].props)||{},k,src=")],
    'pluto_far_any': [("return s==='residfar'?(z.res>=50?0:2):s==='commfar'?(z.res>=50?2:0):s==='facilfar'?3:1;", "return 1;")],
    'feet_kept': [("found.height.value=Math.min(1000,Math.round((ft?hv*0.3048:hv)*100)/100);", "found.height.value=Math.min(1000,Math.round(hv*100)/100);")],
    # the panel
    'no_step_rows': [("  function bimZnStepsHtml(role){\n    var z=bimZn(),L=z[role+'Steps']||[];", "  function bimZnStepsHtml(role){\n    return '';\n    var z=bimZn(),L=z[role+'Steps']||[];")],
    'front_role_editable': [("data-znf=\"legRoles.'+i+'\"'+(i===G.front?' disabled':'')+'>'", "data-znf=\"legRoles.'+i+'\">'")],
    'form_unclaimed': [("    {sel:'[data-znf]',why:'Site analysis: a control of the zoning record'},   /* __acad3dV160 */\n", "")],
    'no_envelope_keywords': [("    ENVELOPE:'zoning envelope buildable volume massing setback stepback sky exposure plane daylight plane angular plane height limit 3d',\n", "")],
    # the board
    'board_kind_ignored': [("    if(kind==='climate'||kind==='zoning')A3D_CLB.kind=kind;   /* __acad3dV160 */", "")],
    'verdict_word_only': [("    return '<div class=\"a3d-clb-st\"><svg viewBox=\"0 0 16 16\" style=\"color:'+S[1]+'\" aria-hidden=\"true\">'+S[2]+'</svg>'+(ok?'Complies':'Exceeds')+'</div>';", "    return '<div class=\"a3d-clb-st\">'+(ok?'Complies':'Exceeds')+'</div>';")],
    'section_not_true_scale': [("    function X(d){return ox+(d-d0)*k;}function Y(h){return B-h*k;}\n    var roleA=", "    function X(d){return ox+(d-d0)*k;}function Y(h){return B-h*k*1.4;}\n    var roleA=")],
    'section_drawn_wide': [("var z=C.zoning,nw=A3D_CLB.narrow,W=nw?360:560,Lm=nw?46:64,", "var z=C.zoning,nw=A3D_CLB.narrow,W=560,Lm=nw?46:64,")],
    'section_table_one_end': [("S.L.map(function(p,i){return [bimZnM(p[1],2),bimZnM(p[0]-S.lot.a,2),bimZnM(S.lot.b-S.R[i][0],2),bimZnM(S.R[i][0]-p[0],2)];})", "S.L.map(function(p,i){return [bimZnM(p[1],2),bimZnM(p[0]-S.lot.a,2),bimZnM(p[0]-S.lot.a,2),bimZnM(S.R[i][0]-p[0],2)];})")],
    'fig1_title_no_count': [("        'The design complies with all '+T.filter(function(r){return r.ok===true;}).length+' controls the model can check'),", "        'The design complies'),")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV160' in txt
out.write_text(txt, encoding='utf-8')
