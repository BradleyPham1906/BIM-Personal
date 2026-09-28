"""falsify_phase105b.py -- break the V105b build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the inset itself
    'inset_half_thickness': [("        ins=bimWallInsetAt(rings,mid,nrm);\n        if(ins===null||!isFinite(ins))ins=0;",
                              "        ins=(rings&&rings.thickness)?rings.thickness/2:0;")],
    'inset_zero': [("        ins=bimWallInsetAt(rings,mid,nrm);", "        ins=0;bimWallInsetAt(rings,mid,nrm);")],
    'inset_wrong_side': [("      nrm=[dir[1]*side,-dir[0]*side];", "      nrm=[-dir[1]*side,dir[0]*side];")],
    'inset_side_ignored': [("      nrm=[dir[1]*side,-dir[0]*side];", "      nrm=[dir[1],-dir[0]];")],
    'inset_takes_near_face': [("    return ta>tb?ta:tb;", "    return ta>tb?tb:ta;")],
    'inset_ray_takes_first': [("      if(best===null||t>best)best=t;", "      if(best===null||t<best)best=t;")],
    'inset_no_thickness_limit': [("    var lim=(rings.thickness>0?rings.thickness:0)+1e-6;", "    var lim=1e9;")],
    'inset_ray_infinite_segments': [("      if(u<-1e-9||u>1+1e-9)continue;\n", "")],
    'faces_from_raw_centerline': [("    var base=bimWallBasePts(o.bim.centerline,o.bim.bulges||null,!!o.bim.closed);\n    if(base.error)return null;",
                                   "    var base={pts:o.bim.centerline};")],
    'faces_drop_world_offset': [("    function world(r){var out=[],k;for(k=0;k<r.length;k++)out.push([r[k][0]+q[0],r[k][1]+q[2]]);return out;}",
                                 "    function world(r){var out=[],k;for(k=0;k<r.length;k++)out.push([r[k][0],r[k][1]]);return out;}")],

    # ---- which faces are counted
    'counts_inner_faces_too': [("      if(bimBulgedSignedArea(faces[i].pts,faces[i].bulges,true)>=-BIM_AREA_EPS)continue;", "      if(false)continue;")],
    'counts_ccw_faces_only': [("      if(bimBulgedSignedArea(faces[i].pts,faces[i].bulges,true)>=-BIM_AREA_EPS)continue;",
                               "      if(bimBulgedSignedArea(faces[i].pts,faces[i].bulges,true)<=BIM_AREA_EPS)continue;")],
    'islands_counted_twice': [("      for(j=0;j<keep.length&&!inside;j++)if(bimRingInsideRing(rings[i].pts,keep[j].pts))inside=true;", "      inside=false;")],
    'containment_by_area_only': [("      for(j=0;j<keep.length&&!inside;j++)if(bimRingInsideRing(rings[i].pts,keep[j].pts))inside=true;",
                                  "      for(j=0;j<keep.length&&!inside;j++)if(rings[i].area<=keep[j].area)inside=true;")],
    'spurs_kept': [("    var st=bimStripSpurs(fpts,fbulges,fsrcs);", "    var st={pts:fpts,bulges:fbulges||[],srcs:fsrcs||[]};")],
    'spur_drops_wrong_pair': [("      d2=(d1+1)%n;np=[];nb=[];ns=[];", "      d1=(d1+1)%n;d2=(d1+1)%n;np=[];nb=[];ns=[];")],
    'two_edge_face_rejected': [("    if(st.pts.length<2)return null;", "    if(st.pts.length<3)return null;")],
    'two_edge_level_rejected': [("    if(edges.length<2)return {rings:[],level:lv};", "    if(edges.length<3)return {rings:[],level:lv};")],
    'curves_as_chords': [("        flat=bimFlattenPoly([a,b],[bl,0],false);", "        flat=[a,b];")],
    'miter_skipped': [("      if(hit&&isFinite(hit[0])&&isFinite(hit[1])&&dd<=cap)ring.push(hit);", "      if(false)ring.push(hit);")],

    # ---- net, efficiency, occupant load
    'net_counts_every_level': [("      if(o.t!=='room'||o.levelId!==levelId)continue;", "      if(o.t!=='room')continue;")],
    'occupants_per_room': [("      groups[key].area+=area;", "      groups[key].area+=Math.ceil(area/lf.m2-1e-9)*lf.m2;")],
    'occupants_one_bucket': [("      key=lf.m2+'|'+(lf.basis||'');", "      key='all';")],
    'occupants_not_rounded_up': [("    for(k in groups)if(groups.hasOwnProperty(k))tot+=Math.ceil(groups[k].area/groups[k].m2-1e-9);",
                                  "    for(k in groups)if(groups.hasOwnProperty(k))tot+=Math.round(groups[k].area/groups[k].m2);")],
    'gross_basis_ignored': [("      if(lf.basis&&String(lf.basis).toLowerCase().indexOf('gross')>=0){area=rooms[i].area*scale;grossUsed=true;}",
                             "      if(false){area=rooms[i].area*scale;grossUsed=true;}")],
    'gross_basis_silent': [("    else if(grossUsed&&scale!==1)notes.push('gross factors apportioned at '+scale.toFixed(2)+'x room area');", "")],
    'missing_factor_silent': [("    if(noFactor)notes.push(noFactor+' room'+(noFactor===1?'':'s')+' with no load factor');", "")],
    'empty_level_reports_zero': [("    out.gross=out.rings.length?g:null;", "    out.gross=g;")],
    'efficiency_inverted': [("    if(out.gross!==null&&out.gross>BIM_AREA_EPS)out.efficiency=out.net/out.gross*100;",
                             "    if(out.gross!==null&&out.gross>BIM_AREA_EPS)out.efficiency=out.gross/out.net*100;")],

    # ---- the room path
    'room_back_to_centerlines': [("              roomPts:bimRoomFaceRing(reg),   /* __acad3dV105b: what a ROOM measures here */\n", "")],
    'room_remeasure_centerlines': [("      room.pts=bimToFrame(room,bimRoomFaceRing(rb)||rb.ring);   /* __acad3dV105b */",
                                    "      room.pts=bimToFrame(room,rb.ring);")],
    'room_per_edge_src_dropped': [("            srcs:hit.face.srcs||null,   /* __acad3dV105b: which object bounds EACH edge */\n", "")],

    # ---- the schedule, the overlay and the command
    'schedule_unregistered': [("    arealevel:{label:'Areas by Level',build:bimBuildAreaSchedule,", "    xarealevel:{label:'Areas by Level',build:bimBuildAreaSchedule,")],
    'schedule_row_per_room': [("    for(i=0;i<A3D.levels.length;i++){\n      a=bimLevelAreas(A3D.levels[i].id);",
                               "    for(i=0;i<1;i++){\n      a=bimLevelAreas(A3D.levels[i].id);")],
    'overlay_never_records': [("      A3D.lastAreaDrawn={levelId:a.levelId,rings:a.rings.length,gross:a.gross,net:a.net,",
                               "      A3D.lastAreaDrawn=A3D.showArea?null:{levelId:a.levelId,rings:a.rings.length,gross:a.gross,net:a.net,")],
    'overlay_not_painted': [("    drawAreaPlan(ctx,V,W,H);           /* __acad3dV105b */\n", "")],
    'command_not_dispatched': [("    areaplan:function(){bimToggleAreaPlan();},        /* __acad3dV105b */",
                                "    areaplan:function(){},        /* __acad3dV105b */")],
    'command_does_not_toggle_off': [("    A3D.showArea=!A3D.showArea;", "    A3D.showArea=true;")],
    'overlay_net_from_elsewhere': [("      A3D.lastAreaDrawn={levelId:a.levelId,rings:a.rings.length,gross:a.gross,net:a.net,",
                                    "      A3D.lastAreaDrawn={levelId:a.levelId,rings:a.rings.length,gross:a.gross,net:a.gross,")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV105b' in txt
out.write_text(txt, encoding='utf-8')
