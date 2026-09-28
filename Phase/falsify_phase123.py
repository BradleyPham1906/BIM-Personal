"""falsify_phase123.py -- break the V123 build one way at a time, keeping the marker.

Each variant takes back one thing V123 does, or breaks one thing it built, and the V123 suite must
fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 123a: lengths in the project's unit, and what a handle takes
    'typed_len_in_metres': [("      for(i=0;i<nums.length;i++)nums[i]=nums[i]/sc;\n", "")],
    'readout_in_metres': [("    var s=bimDispLen(d);\n    if(s==='-0')s='0';\n    return s+' '+bimUnitLabel();\n",
                           "    var a=Math.abs(d);\n    if(a<0.01)return '0 m';\n    if(a<1)return (Math.round(d*1000))+' mm';\n    return (Math.round(d*1000)/1000)+' m';\n")],
    'coords_in_metres': [("      a/=sc;b/=sc;\n", "")],
    'no_comma_on_square': [("    return n>1&&!!buf&&buf.charAt(buf.length-1)!==','&&buf.split(',').length<n;\n", "    return false;\n")],
    'centre_3d_two_numbers': [("    if(k==='centre')return (r.gk?r.snapWorld:!A3D.flat)?'len3':'len2';\n", "    if(k==='centre')return 'len2';\n")],
    # ---- 123b: what a rebuild, a copy and a turn keep
    'carry_nothing': [("    if(!from||!to)return to;\n    var skip=BIM_BUILT_OPTIONAL", "    return to;\n    var skip=BIM_BUILT_OPTIONAL")],
    'wall_copy_at_origin_frame': [("t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:bimObjOffset(o),mesh:res.mesh,bim:bimCarryBim(o.bim,res.bim),layer:o.layer};",
                                   "t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:[0,0,0],mesh:res.mesh,bim:bimCarryBim(o.bim,res.bim),layer:o.layer};")],
    'column_copy_retyped': [("        bim:bimCarryBim(o.bim,{type:'column',center:newCenter}),layer:o.layer};",
                             "        bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter,rotation:o.bim.rotation||0},layer:o.layer};")],
    'floor_outline_not_turned': [("      return {kind:'floor',mesh:res2.mesh,bim:{type:'floor',profile:newProf}};", "      return {kind:'floor',mesh:res2.mesh,bim:{type:'floor'}};")],
    'pad_at_origin_frame': [("name:'Pad '+A3D.counts.pad,col:'#9db4c8',pos:bimObjOffset(s),mesh:m};", "name:'Pad '+A3D.counts.pad,col:'#9db4c8',pos:[0,0,0],mesh:m};")],
    'pocket_in_sketch_frame': [("    P=P.map(function(p){return [p[0]+sq[0],p[1]+sq[2]];});\n", "")],
    # ---- 123c: a click asks for a value and changes nothing
    'undo_on_press': [("          gd.undoPending=true;\n", "          gd.undoPending=false;pushUndo();\n")],
    'copies_on_press': [("          if(gctrl&&gcopy)gd.copyPending=true;\n",
                         "          if(gctrl&&gcopy){var mc=bimGizmoCopySelection(gd.ids);if(mc){gd.copies=mc;gd.ids=mc.ids.slice();gd.start=bimGizmoStarts(gd.ids);}}\n")],
    'click_opens_nothing': [("        bimGizmoClickValue(gizRec,ev);\n        return;\n", "        return;\n")],
    'box_no_undo_step': [("          drag=fresh;\n          pushUndo();\n          var summary=bimGizmoApplyValue(fresh,p.v,false);\n",
                          "          drag=fresh;\n          var summary=bimGizmoApplyValue(fresh,p.v,false);\n")],
    'handle_hint_missing': [("    if(A3D.gizHover&&A3D.gizHoverHint&&!drag&&A3D.gizmo)return A3D.gizHoverHint;\n", "")],
    # ---- 123d: the body drag is the gizmo's move
    'body_drag_no_undo': [("    A3D_MATERIALIZED=[];\n    pushUndo();\n    return rec;\n", "    A3D_MATERIALIZED=[];\n    return rec;\n")],
    'body_drag_no_point_snap': [("           snaps:bimGizmoSnapSetup(ids),fine:false,\n           ids:ids,start:bimGizmoStarts(ids),x0:bd.x,y0:bd.y,da:0,db:0,",
                                 "           snaps:null,fine:false,\n           ids:ids,start:bimGizmoStarts(ids),x0:bd.x,y0:bd.y,da:0,db:0,")],
    'alt_lift_refused': [("      if(!isFinite(len2)||!(len2>=A3D_GIZ.edgeOn*A3D_GIZ.edgeOn*ref)||len2<1e-4){\n", "      if(true){\n")],
    'group_drag_single': [("    if(ids.indexOf(o.id)<0)ids=[o.id];\n", "    ids=[o.id];\n")],
    # ---- 123e: taking a face
    'dblclick_dead': [("    el.cv.addEventListener('dblclick',bimFaceDblClick);   /* __acad3dV123: take a face */\n", "")],
    'gizmo_over_face': [("      !A3D.face;   /* __acad3dV123: a held face has its own arrow */", "      true;")],
    'no_edge_on_side': [("    var pick=null,pd=A3D_PUSH.edge;\n", "    var pick=null,pd=-1;\n")],
    'sketch_behind_its_solid': [("      if(!(t>0)||(best&&t>best.t+1e-4))continue;\n", "      if(!(t>0)||(best&&t>best.t-1e-4))continue;\n")],
    'sketch_over_its_floor': [("      if(best&&!best.sketch&&Math.abs(t-best.t)<=1e-4&&s.on!==best.o.id)continue;\n", "")],
    'followed_sketch_pulled': [("      if(fol.length)f.why=", "      if(false)f.why=")],
    'wall_side_pushes': [("      else f.why='A wall\\'s thickness comes from its type'+(tn?' ('+tn+')':'')+' - choose another type, or Edit Type, in Properties';\n",
                          "      else{f.ok=true;f.kind='wallTop';f.dimName='Height';f.dim=b.height;}\n")],
    'outward_by_corner_order': [("    if(bimMeshTopo(m).open)return facing;\n", "    return N.slice();\n")],
    'no_crease_rule': [("  function bimRegionSmooth(o,m,fis,N){\n", "  function bimRegionSmooth(o,m,fis,N){\n    return false;\n")],
    'tab_dead': [("    var list=bimFaceList(cur.o),at=-1,i;\n", "    return false;\n    var list=bimFaceList(cur.o),at=-1,i;\n")],
    'escape_clears_at_once': [("      if(A3D.face&&bimFaceCurrent()){bimFaceExit();ev.preventDefault();ev.stopImmediatePropagation();return;}\n", "")],
    'presspull_dead': [("    presspull:function(){bimPressPullCommand();},   /* __acad3dV123 */", "    presspull:function(){},")],
    'face_outlives_selection': [("    if(!o||A3D.sel!==F.id||(A3D.selSet&&A3D.selSet.length>1)||A3D.sk||A3D.conPick||!bimLayerShown(o)){\n",
                                 "    if(!o||A3D.sk||A3D.conPick||!bimLayerShown(o)){\n")],
    # ---- 123f: push and pull
    'push_moves_centre': [("      o.pos=[o.pos[0]+f.N[0]*dist/2,o.pos[1]+f.N[1]*dist/2,o.pos[2]+f.N[2]*dist/2];\n", "")],
    'no_level_snap': [("      for(i=0;i<A3D.levels.length;i++)out.levels.push({elev:A3D.levels[i].elev,name:A3D.levels[i].name});\n", "")],
    'no_point_snap_push': [("      if(dd<bd){bd=dd;best={d:vdot([p.P[0]-d.C0[0],p.P[1]-d.C0[1],p.P[2]-d.C0[2]],d.N),at:p.P,level:null};}\n", "")],
    'push_no_grid': [("    if(A3D_SNAP.grid&&A3D_SNAP.gridSize>0)dist=Math.round(dist/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;\n    var sn=bimPushSnap(d,xy,dist);\n",
                      "    var sn=bimPushSnap(d,xy,dist);\n")],
    'push_no_fine': [("    if(d.fine){dx*=A3D_GIZ.fine;dy*=A3D_GIZ.fine;}\n    var dist=(dx*d.sx+dy*d.sy)/d.len2;\n", "    var dist=(dx*d.sx+dy*d.sy)/d.len2;\n")],
    'escape_keeps_undo_step': [("    if(d.undoAt&&UNDO_STACK.length===d.undoAt)UNDO_STACK.pop();\n", "")],
    'push_no_range': [("    var rg=d.range||{lo:-Infinity,hi:Infinity},lim=null;\n", "    var rg={lo:-Infinity,hi:Infinity},lim=null;\n")],
    'size_box_is_distance': [("          dist=(v-now.f.dim)*(now.f.dsign||1);\n", "          dist=v;\n")],
    'sketch_pull_always_up': [("    var mesh=padMesh(P,(sk.y||0)+Math.min(0,dist),Math.abs(dist));\n", "    var mesh=padMesh(P,(sk.y||0),Math.abs(dist));\n")],
    'sketch_pushed_into_solid': [("    }else if(f.kind==='sketch'&&f.on){\n", "    }else if(false){\n"),
                                 ("    if(d.f.on&&dist<0){\n", "    if(false){\n")],
    'wall_push_drops_type': [("    o.mesh=res.mesh;\n    o.bim=bimCarryBim(b,res.bim);\n    bimPropagateFrom([o.id],'rebuild');   /* live, as a grip drag is: openings, rooms and clones follow */\n",
                              "    o.mesh=res.mesh;\n    o.bim=res.bim;\n    bimPropagateFrom([o.id],'rebuild');   /* live, as a grip drag is: openings, rooms and clones follow */\n")],
    'wall_end_backwards': [("      cl[e.i]=[cl[e.i][0]+e.N[0]*dist,cl[e.i][1]+e.N[2]*dist];\n", "      cl[e.i]=[cl[e.i][0]-e.N[0]*dist,cl[e.i][1]-e.N[2]*dist];\n")],
    'typed_push_ignores_direction': [("      if(!bimPushTo(keepSign?((rec.dist<0)?-1:1)*Math.abs(nums[0]):nums[0],true)){",
                                      "      if(!bimPushTo(Math.abs(nums[0]),true)){")],
    'wall_push_no_openings': [("    bimPropagateFrom([o.id],'rebuild');   /* live, as a grip drag is: openings, rooms and clones follow */\n", "")],
    # ---- 123g: Properties, the toolbar, the sheet
    'props_no_dimensions': [("    }else if(!o.mesh&&o.prm&&TYPES[o.t]){\n", "    }else if(false){\n")],
    'props_base_sinks': [("        if(isFinite(base0)&&isFinite(base1)){if(!o.pos)o.pos=[0,0,0];o.pos[1]+=base0-base1;}\n", "")],
    'props_scale_ignored': [("        if(pname!=='Angle'&&pname!=='Polygon')pval=pval/SCALE;\n", "")],
    'toolbar_button_dead': [("    if(act==='bim:presspull'){bimPressPullCommand();return;}   /* __acad3dV123 */\n", "")],
    'faces_sheet_hand_list': [("rows(A3D_FACE_GESTURES).concat(rows(A3D_FACE_KEYS))", "rows(A3D_FACE_GESTURES)")],
    # ---- 123h: a primitive's Base Offset is its base
    'base_offset_reads_middle': [("    cons+=bimPropLen('Base Offset',pbO!==null?pbO:((o.pos&&o.pos[1])||0),'posy');",
                                  "    cons+=bimPropLen('Base Offset',(o.pos&&o.pos[1])||0,'posy');")],
    'base_offset_sets_middle': [("        o.pos[1]=pbY!==null?o.pos[1]+(yv-pbY):yv;\n", "        o.pos[1]=yv;\n")],
    # ---- 123i: an opening's faces are the opening's
    'heads_are_top': [("        if(Math.abs(c[1]-yt)<1e-3)return 'top';\n        if(Math.abs(c[1]-yb)<1e-3)return 'bottom';\n        return 'opening';\n",
                       "        return c[1]>(yb+yt)/2?'top':'bottom';\n")],
    'jambs_are_sides': [("        if(tg&&Math.abs(N[0]*tg[0]+N[2]*tg[1])>0.7)return 'opening';\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV123' in txt
out.write_text(txt, encoding='utf-8')
