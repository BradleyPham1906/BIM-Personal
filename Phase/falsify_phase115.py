"""falsify_phase115.py -- break the V115 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the Start page is seen
    'start_under_drawing': [("top:var(--acad-ribbon-h);bottom:0;background:#20232a;z-index:9550;",
                             "top:var(--acad-ribbon-h);bottom:0;background:#20232a;z-index:9300;")],
    'start_leaves_dock': [("#acad-start{position:fixed;left:0;right:0;", "#acad-start{position:fixed;left:var(--figma-dock-w,0px);right:0;")],
    'ws_menu_visible': [("body.acad-startpage #acad-qat .acad-ws{visibility:hidden}\n", "")],
    'start_keys_leak': [("    if(bimStartShowing())return;\n", "")],
    'start_cmds_leak': [("    if(bimStartShowing()&&!BIM_START_CMDS[act]){a3dToast('Open a project to use that command');return false;}\n", "")],

    # ---- each tab is its own project
    'no_reset_before_load': [("    for(k in d)if(d.hasOwnProperty(k))A3D[k]=d[k];\n    bimApplyStoredState(st);\n",
                              "    bimApplyStoredState(st);\n")],
    'undo_shared': [("      UNDO_STACK=rt?rt.undo:[];REDO_STACK=rt?rt.redo:[];\n", "")],
    'names_repeat': [("    for(n=1;n<100000;n++)if(!used[('project'+n)])return 'Project'+n;\n", "    return 'Project1';\n")],
    'new_tab_not_opened': [("      return null;\n    }\n    A3D_DOCS.open.push(id);\n", "      return null;\n    }\n")],
    'close_no_neighbour': [("      var next=A3D_DOCS.open[at+1]||A3D_DOCS.open[at-1]||null;\n", "      var next=null;\n")],

    # ---- storage holds every project in exactly one place
    'park_not_written': [("    try{localStorage.setItem(A3D_DOC_PREFIX+cur,sA);}\n", "    try{void sA;}\n")],
    'opened_copy_kept': [("    if(fromKey){\n      try{localStorage.removeItem(fromKey);}\n", "    if(false){\n      try{localStorage.removeItem(fromKey);}\n")],
    'docid_untagged': [("    rec.docId=A3D_DOCS.active;\n", "")],
    'stale_copy_kept': [("        try{localStorage.removeItem(A3D_DOC_PREFIX+act);}\n", "        try{}\n")],
    'orphan_forgotten': [("      docs.push(bimDocMetaFromStore(keys[i]));\n", "      continue;\n")],
    'ghost_kept': [("      if(e.id===act||keys.indexOf(e.id)>=0)return true;\n", "      return true;\n")],

    'pagehide_flush_missing': [("  window.addEventListener('pagehide',function(){\n    if(saveT){clearTimeout(saveT);saveT=null;save3d();}\n  });\n", "")],

    # ---- failures are loud and leave nothing half-done
    'rollback_missing': [("        localStorage.setItem(LSK,sA);\n        localStorage.removeItem(A3D_DOC_PREFIX+cur);\n", "")],
    'quota_half_done': [("    catch(e1){console.warn('[BIM] The current project could not be parked in its own key.',e1);a3dToast(full);return false;}\n",
                         "    catch(e1){console.warn('[BIM] The current project could not be parked in its own key.',e1);a3dToast(full);}\n")],
    'save_silent': [("      if(!A3D_SAVE_FAILED){\n        A3D_SAVE_FAILED=true;\n", "      if(false){\n        A3D_SAVE_FAILED=true;\n")],
    'delete_without_confirm': [("      if(window.confirm('Delete \"'+nm+'\" from this browser? This cannot be undone.')) docAct('remove',id);\n",
                                "      docAct('remove',id);\n")],

    # ---- the document commands and files
    'qat_dead': [("    if(window.__a3dCmdSupported&&window.__a3dCmdSupported(act)){window.__a3dRunCmd(act);return;}\n", "")],
    'download_unnamed': [("    return s.slice(0,80)||'project';\n", "    return 'project';\n")],
    'dxf_through_open': [("    if(ext!=='json'){\n      a3dToast(name+' is not a project file.", "    if(false){\n      a3dToast(name+' is not a project file.")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV115' in txt
out.write_text(txt, encoding='utf-8')
