"""falsify_phase145.py -- break the V145 build one way at a time, keeping the marker.

Each variant takes back one thing V145 does, and the V145 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the slope lines
    'fan_one_ray': [("var a1=Math.atan2(n1[1],n1[0]),da=Math.atan2(turn,dot),f=Math.max(1,Math.ceil(da/(BIM_GRADE.fanDeg*Math.PI/180)-1e-9));",
                     "var a1=Math.atan2(n1[1],n1[0]),da=Math.atan2(turn,dot),f=1;")],
    'no_edge_samples': [("      for(j=1;j<m;j++)S.push({p:[a[0]+dx*j/m,a[1]+dz*j/m],u:n1,k:1,edge:i});", "")],
    'valley_full_rate': [("if(bl>1e-9){var u=[bx/bl,bz/bl];S.push({p:b.slice(),u:u,k:u[0]*n1[0]+u[1]*n1[1],corner:(i+1)%n,valley:true});}",
                          "if(bl>1e-9){var u=[bx/bl,bz/bl];S.push({p:b.slice(),u:u,k:1,corner:(i+1)%n,valley:true});}")],
    'no_valley_stop': [("    function ok(t){var q=at(t);return bimPolyDist(q,P)>=s.k*t-1e-7&&!bimPointInPoly(q,P);}",
                        "    function ok(t){return true;}")],
    'slopes_swapped': [("var dir=h0>Z+1e-9?1:(h0<Z-1e-9?-1:0),r=dir>0?sl.cut:sl.fill;", "var dir=h0>Z+1e-9?1:(h0<Z-1e-9?-1:0),r=dir>0?sl.fill:sl.cut;")],
    'slope_ignores_k': [("    function slope(t){return Z+dir*s.k*t/r;}", "    function slope(t){return Z+dir*t/r;}")],
    'default_slope_wrong': [("var BIM_GRADE={step:2,fanDeg:15,march:0.25,reach:500,cut:2,fill:2};", "var BIM_GRADE={step:2,fanDeg:15,march:0.25,reach:500,cut:2,fill:3};")],
    # ---- the proposed surface
    'existing_points_kept': [("    for(i=0;i<tin.P.length;i++)if(used[i]&&!inside(tin.P[i]))add(", "    for(i=0;i<tin.P.length;i++)if(used[i])add(")],
    'no_slope_breaklines': [("      r.spokes.forEach(function(s){if(s.r&&!s.r.off&&s.r.t>1e-6)bls.push({name:r.pad.name+' slope',", "      r.spokes.forEach(function(s){if(false)bls.push({name:r.pad.name+' slope',")],
    'not_in_place': [("    var prev=A3D.objs.filter(function(x){return x.t==='terrain'&&x.grading&&x.grading.existing===ter.id;})[0]||null,i,j;",
                      "    var prev=null,i,j;")],
    'pads_not_kept': [("    if(prev)prev.grading.pads.forEach(function(p){var po=objById(p.id);if(bimIsPad(po)&&pads.indexOf(po)<0)pads=pads.concat([po]);});\n", "")],
    'overlaps_unchecked': [("    for(i=0;i<res.length;i++)for(j=i+1;j<res.length;j++)if(bimPolysTouch(regions[i],regions[j]))overlaps.push(", "    for(i=0;i<res.length;i++)for(j=i+1;j<res.length;j++)if(false)overlaps.push(")],
    'off_surface_allowed': [("    for(i=0;i<P.length;i++)if(idx.at(P[i][0],P[i][1])===null)return {error:o.name+' is not wholly on the existing surface'};\n", "")],
    'off_surface_uncounted': [("      if(r.kind==='edge')nOff++;\n", "")],
    'never_stale': [("    return bimGradeStamp(ter,pads)!==o.grading.stamp;", "    return false;")],
    'no_undo': [("    pushUndo();\n    var o=prev;\n", "    var o=prev;\n")],
    # ---- volumes
    'volume_unsplit': [("        var fp=bimClipHalfPlane(piece,-dx,-dz,d0),cp=bimClipHalfPlane(piece,dx,dz,-d0);", "        var fp=piece,cp=piece;")],
    'volume_swapped': [("    return {cut:cut,fill:fill,net:cut-fill,cutArea:cutA,fillArea:fillA,area:area};\n  }\n  /* Grade the pads",
                        "    return {cut:fill,fill:cut,net:fill-cut,cutArea:fillA,fillArea:cutA,area:area};\n  }\n  /* Grade the pads")],
    'volume_slivers': [("if(fp.length>=3){c=bimEarthCentroid(fp);pa_=bimPolyArea(fp);if(c&&pa_>1e-9){", "if(fp.length>=3){c=bimEarthCentroid(fp);pa_=bimPolyArea(fp);if(c&&pa_>0){")],
    'volume_bbox_only': [("        var piece=bimClipToTri([b0,b1,b2],ta,A.P);", "        var piece=[b0,b1,b2];")],
    # ---- the map, spots, arrows
    'cutfill_sign': [("        var dd=(tin.H[tr[0]]+tin.H[tr[1]]+tin.H[tr[2]])/3-he;", "        var dd=he-(tin.H[tr[0]]+tin.H[tr[1]]+tin.H[tr[2]])/3;")],
    'cutfill_for_all': [("    if(mode&&!/^(slope|elevation|aspect)$/.test(mode)&&!(mode==='cutfill'&&o.grading))return false;", "    if(mode&&!/^(slope|elevation|aspect|cutfill)$/.test(mode))return false;"),
                        ("    var e=o.grading&&objById(o.grading.existing);\n    return e?bimTerrainBands(", "    var e=o.grading?objById(o.grading.existing):o;\n    return e?bimTerrainBands(")],
    'spot_prefers_existing': [("sort(function(a,b){return (b.grading?1:0)-(a.grading?1:0);});", "sort(function(a,b){return (a.grading?1:0)-(b.grading?1:0);});")],
    'spot_ignores_selected_surface': [("    S.forEach(function(x){x.spot={surface:ter?ter.id:null};});", "    S.forEach(function(x){x.spot={surface:null};});")],
    'spot_corners_dead': [("      if(f==='gradespots'){bimGradeSpots(objById(A3D.sel));return;}", "      if(f==='gradespots'){return;}")],
    'arrows_uphill': [("var cx=(A[0]+B[0]+C[0])/3,cz=(A[1]+B[1]+C[1])/3,dx=-pl[0]/s,dz=-pl[1]/s;", "var cx=(A[0]+B[0]+C[0])/3,cz=(A[1]+B[1]+C[1])/3,dx=pl[0]/s,dz=pl[1]/s;")],
    'arrows_checkbox_dead': [("      if(f==='terrarrows'){bimSetSlopeArrows(o,inp.checked);return;}", "      if(f==='terrarrows'){return;}")],
    # ---- the app
    'existing_drawn_in_3d': [("&&bimLayerShown(o)&&!bimTerrainSuperseded(o))list.push(o);}", "&&bimLayerShown(o))list.push(o);}")],
    'existing_not_dashed': [("        var sup=!o.grading&&!!bimTerrainSuperseded(o);", "        var sup=false;")],
    'survey_check_on_proposed': [("    if(o.t==='terrain'&&o.survey&&!o.grading)h+=bimPropGroup('Survey Check',", "    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Survey Check',")],
    'no_grading_group': [("    if(o.t==='terrain'&&o.grading)h+=bimPropGroup('Grading',bimGradePropsHtml(o));            /* __acad3dV145 */\n", "")],
    'regrade_button_dead': [("      if(f==='regrade'){bimRegrade(objById(A3D.sel));return;}", "      if(f==='regrade'){return;}")],
    'pad_slopes_not_shown': [("          dims+=bimPropRow('Cut Slope (H:V)',", "          if(0)dims+=bimPropRow('Cut Slope (H:V)',")],
    'pad_slope_not_set': [("    if(v==='')delete o[key];else o[key]=n;", "    if(v==='')delete o[key];")],
    'no_card': [("    C.push({id:'grading',title:'Grading: Cut and Fill',", "    if(0)C.push({id:'grading',title:'Grading: Cut and Fill',")],
    'grade_on_proposed_ignored': [("    if(ter&&ter.grading){\n      if(!pads.length)pads=", "    if(false){\n      if(!pads.length)pads=")],
    'cutfillmap_one_way': [("    var on=!G.every(function(x){return x.tview==='cutfill';});", "    var on=true;")],
    'no_commands': [("    grade:function(){bimGradeCommand();},              /* __acad3dV145 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV145' in txt
out.write_text(txt, encoding='utf-8')
