"""falsify_phase112.py -- break the V112 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'snap_never': [("    if(!A3D_SNAP.point||!sn)return null;", "    if(true)return null;")],
    'snap_ignores_freedom': [("      for(k=0;k<dirs.length;k++){\n        var d=dirs[k],a=want[0]*d[0]+want[1]*d[1]+want[2]*d[2];\n        cand[0]+=d[0]*a;cand[1]+=d[1]*a;cand[2]+=d[2]*a;\n      }", "      cand=[want[0],want[1],want[2]];")],
    'snap_takes_worst': [("      if(pull+res<bestD){bestD=pull+res;best={v:cand,at:land,tgt:t};}", "      if(pull+res>=bestD||!best){bestD=pull+res;best={v:cand,at:land,tgt:t};}")],
    'snap_to_itself': [("      var c=bimSnapCandidates(elevs[i],ids);", "      var c=bimSnapCandidates(elevs[i]);")],
    'snap_no_pull_limit': [("      if(pull>px)continue;                                // the cursor is not near it yet", "      if(pull>px*40)continue;")],
    'snap_marker_missing': [("    var sn=bimGizmoSnapVec(v,[drag.dir]);\n    drag.snapAt=sn?sn.at:null;", "    var sn=bimGizmoSnapVec(v,[drag.dir]);\n    drag.snapAt=null;")],
    'plane_snap_off': [("    var sn=bimGizmoSnapVec(v,[drag.a,drag.b]);\n    drag.snapAt=sn?sn.at:null;\n    if(sn){\n      v=sn.v;\n      drag.da=vdot(v,drag.a);drag.db=vdot(v,drag.b);\n    }", "    drag.snapAt=null;")],
    'typed_enter_ignored': [("    if(k==='Enter'&&A3D_GIZ_TYPE.active)return bimGizmoTypedCommit();", "    if(false)return bimGizmoTypedCommit();")],
    'typed_digits_ignored': [("      A3D_GIZ_TYPE.active=true;A3D_GIZ_TYPE.buf+=k;paint();return true;", "      return false;")],
    'typed_sign_from_number': [("      var sgn=(d.gizDist<0)?-1:1;", "      var sgn=1;")],
    'typed_angle_sense': [("      bimGizmoRotateTo(-v*Math.PI/180);", "      bimGizmoRotateTo(v*Math.PI/180);")],
    'typed_no_propagation': [("    drag=null;\n    bimGizmoEndDrag(summary);\n    return true;", "    drag=null;\n    refreshTree();paint();saveSoon();\n    return true;")],
    'backspace_not_claimed': [("    return /^[0-9]$/.test(k)||k==='.'||k==='-'||k==='Backspace'||k==='Enter';", "    return /^[0-9]$/.test(k)||k==='.'||k==='-'||k==='Enter';")],
    'backspace_gate_not_delegated': [("      /* __acad3dV112: and the same question here, in the second gate */\n      try{ if(window.__a3dOn&&window.__a3dWantsKey&&window.__a3dWantsKey(e)) return; }catch(err7){}\n", "")],
    'escape_behind_modifiers': [("    if(k==='Escape'){bimGizmoCancelDrag();return true;}\n    if(ev.ctrlKey||ev.metaKey||ev.altKey)return false;", "    if(ev.ctrlKey||ev.metaKey||ev.altKey)return false;\n    if(k==='Escape'){bimGizmoCancelDrag();return true;}")],
    'escape_no_restore': [("    if(d.snap)bimGizmoRestoreObjs(d.ids,d.snap);\n    else if(d.start){", "    if(false)bimGizmoRestoreObjs(d.ids,d.snap);\n    else if(false){")],
    'escape_keeps_copies': [("    if(d.copies)bimGizmoDropCopies(d.copies);                    /* __acad3dV112 */", "    /* __acad3dV112 */")],
    'escape_loses_pivot': [("    if(d.gk==='pivot')A3D.gizPivot=d.pivot0;                     /* __acad3dV112 */", "    /* __acad3dV112 */")],
    'ctrl_drags_originals': [("          if(made){paint();ghit=bimPickGizmo(xy[0],xy[1])||gz;}", "          if(made){paint();}")],
    'ctrl_copy_not_undoable': [("          pushUndo();\n          made=bimGizmoCopySelection(gz.giz.ids);", "          made=bimGizmoCopySelection(gz.giz.ids);\n          pushUndo();")],
    'shift_not_fine': [("    if(drag.fine){dx*=A3D_GIZ.fine;dy*=A3D_GIZ.fine;}   /* __acad3dV112 */", "    /* __acad3dV112 */")],
    'fine_factor_wrong': [("snapSrc:24,snapTgt:400,fine:0.25};", "snapSrc:24,snapTgt:400,fine:0.5};")],
    'pivot_not_used': [("    if(A3D.gizPivot&&ids&&ids.length)return A3D.gizPivot.slice();", "    if(false)return A3D.gizPivot.slice();")],
    'alt_moves_model': [("    if(hit.kind==='centre'&&ev&&ev.altKey)return bimGizmoBeginPivot(hit,xy);   /* __acad3dV112 */", "    /* __acad3dV112 */")],
    'pivot_menu_always': [('    if(A3D.gizPivot)h+=\'<button type="button" data-a3dgiz="pivot">Reset Pivot</button>\';   /* __acad3dV112 */', '    h+=\'<button type="button" data-a3dgiz="pivot">Reset Pivot</button>\';   /* __acad3dV112 */')],
    'pivot_reset_noop': [("      A3D.gizPivot=null;\n      a3dToast('Pivot back at the middle of the selection');", "      a3dToast('Pivot back at the middle of the selection');")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV112' in txt
out.write_text(txt, encoding='utf-8')
