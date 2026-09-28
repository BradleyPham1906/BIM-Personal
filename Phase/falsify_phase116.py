"""falsify_phase116.py -- break the V116 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the tabs are the sheets
    'strip_not_derived': [("    for(i=0;i<A3D.sheets.length;i++){\n      s=A3D.sheets[i];\n      h+='<button class=\"a3d-lt'",
                           "    for(i=0;i<0;i++){\n      s=A3D.sheets[i];\n      h+='<button class=\"a3d-lt'")],
    'next_number_repeats': [("    return 'A'+(max+1);\n", "    return 'A'+(101+A3D.sheets.length);\n")],
    'portrait_new_sheet': [("  var SHEET_NEW_SIZE='ANSI-B-L';", "  var SHEET_NEW_SIZE='ANSI-B';")],

    # ---- every way off a sheet returns to the model view it came from
    'model_tab_no_camera': [("    if(ok&&m.cam){\n", "    if(false){\n")],
    'close_bypasses_model': [("addEventListener('click',function(){bimShowModel();});", "addEventListener('click',function(){bimCloseSheetView();});")],
    'delete_leaves_sheet_view': [("        if(wasOn)bimShowModel();\n", "")],
    'undo_leaves_sheet_view': [("      if(bimSheetOnScreen()||A3D_VIEW.kind==='sheet')bimShowModel();\n      else el.sheetview.classList.remove('open');\n",
                                "      el.sheetview.classList.remove('open');\n")],

    # ---- every way onto a sheet is a view
    'dialog_bypass': [("      bimActivateView('sheet',s.id);   /* __acad3dV116: through the view path", "      bimOpenSheetView(s.id);   /* __acad3dV116: through the view path")],
    'ribbon_bypass': [("if(A3D.sheets.length){bimActivateView('sheet',A3D.activeSheetId&&", "if(A3D.sheets.length){bimOpenSheetView(A3D.activeSheetId&&")],
    'hook_bypass': [("  window.__a3dOpenSheetView=function(id){return bimActivateView('sheet',id);};", "  window.__a3dOpenSheetView=bimOpenSheetView;")],

    # ---- rename, the tab menu, Sheet Setup
    'hud_not_following': [("bimSyncViewLabel();refreshHud();}\n", "bimSyncViewLabel();}\n")],
    'rename_not_undoable': [("        pushUndo();\n        sh.name=v;\n", "        sh.name=v;\n")],
    'escape_rename_commits': [("      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();finish(false);}", "      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();finish(true);}")],
    'tab_delete_no_confirm': [("      else if(a==='del')bimConfirmDeleteSheet(id);\n", "      else if(a==='del')bimDeleteSheet(id);\n")],
    'setup_half_applied': [("      if(sizeI.value==='Custom'&&(!isFinite(cw)||cw<10||!isFinite(ch)||ch<10)){document.getElementById('a3d-dlgerr').textContent='Custom size must be at least 10mm';return;}\n      pushUndo();\n      sheet.number=num;sheet.name=name||'Untitled';sheet.sizeKey=sizeI.value;\n",
                            "      pushUndo();\n      sheet.number=num;sheet.name=name||'Untitled';sheet.sizeKey=sizeI.value;\n      if(sizeI.value==='Custom'&&(!isFinite(cw)||cw<10||!isFinite(ch)||ch<10)){document.getElementById('a3d-dlgerr').textContent='Custom size must be at least 10mm';return;}\n")],

    # ---- model space through a viewport
    'dblclick_opens_props': [("    if(hit&&hit.vp.kind!=='schedule'){bimSetModelSpace(hit.vp.id);return;}\n", "")],
    'schedule_activates': [("    if(hit&&hit.vp.kind!=='schedule'){bimSetModelSpace(hit.vp.id);return;}\n", "    if(hit){bimSetModelSpace(hit.vp.id);return;}\n")],
    'fit_center_lost': [("    vp.pan=bimSheetVpFitPan(vp)||[0,0];\n    vp.scaleMode='ratio';vp.scaleDenom=d;\n", "    vp.pan=[0,0];\n    vp.scaleMode='ratio';vp.scaleDenom=d;\n")],
    'fit_scale_too_tight': [("if(SHEET_SCALES[i].denom>=want-1e-6){d=SHEET_SCALES[i].denom;break;}", "if(SHEET_SCALES[i].denom>=want/2){d=SHEET_SCALES[i].denom;break;}")],
    'zoom_not_about_cursor': [("      vp.pan=[vp.pan[0]+ox*(d1-d2)/1000,vp.pan[1]-oy*(d1-d2)/1000];\n", "")],
    'pan_sign_flipped': [("      vp.pan=[pd.orig[0]-dx*mPerMM,pd.orig[1]+dy*mPerMM];\n", "      vp.pan=[pd.orig[0]+dx*mPerMM,pd.orig[1]-dy*mPerMM];\n")],
    'pan_undo_per_move': [("      if(!pd.orig){\n        if(Math.abs(dx)<0.3&&Math.abs(dy)<0.3)return;   /* a click is not a pan */\n        pushUndo();\n",
                           "      pushUndo();\n      if(!pd.orig){\n        if(Math.abs(dx)<0.3&&Math.abs(dy)<0.3)return;   /* a click is not a pan */\n")],
    'pan_not_in_svg': [("    var cam=bimSheetSolveCamera(src,wMM,hMM,1,vp.scaleMode,vp.scaleDenom,vp.pan);", "    var cam=bimSheetSolveCamera(src,wMM,hMM,1,vp.scaleMode,vp.scaleDenom);")],
    'escape_keeps_mspace': [("      if(A3D.sheetActiveVp)bimSetPaperSpace();\n      else if(A3D.sheetSelVp){A3D.sheetSelVp=null;bimSheetViewRefresh();}\n",
                             "      if(A3D.sheetSelVp){A3D.sheetSelVp=null;bimSheetViewRefresh();}\n")],
    'space_button_dead': [("    if(spBtn)spBtn.addEventListener('click',function(){", "    if(false)spBtn.addEventListener('click',function(){")],
    'scale_list_short': [("    {label:'1:1',denom:1},{label:'1:2',denom:2},{label:'1:5',denom:5},{label:'1:10',denom:10},\n", ""),
                         ("{label:'1:500',denom:500},{label:'1:1000',denom:1000},\n    {label:'1:1250',denom:1250},{label:'1:2000',denom:2000},{label:'1:2500',denom:2500},{label:'1:5000',denom:5000}\n",
                          "{label:'1:500',denom:500}\n")],
    'custom_scale_replaced': [("    if(vp.scaleMode==='ratio'&&!listed&&isFinite(vp.scaleDenom))sopts=", "    if(false)sopts=")],

    'added_vp_at_origin': [("vp.scaleDenom=parseInt(scaleI.value,10)||100;vp.pan=bimSheetVpFitPan(vp)||[0,0];}   /* __acad3dV116: opens on the model */",
                            "vp.scaleDenom=parseInt(scaleI.value,10)||100;}   /* __acad3dV116: opens on the model */")],
    'props_fit_jumps': [("if(wasFit)vp.pan=bimSheetVpFitPan(vp)||[0,0];}", "}")],

    # ---- nothing reaches the model behind the paper
    'keys_reach_model': [("    if(bimSheetOnScreen()&&bimSheetKey(ev))return;   /* __acad3dV116 */\n", "")],
    'cmds_reach_model': [("    if(bimSheetOnScreen()&&!BIM_SHEET_CMDS[act]){a3dToast('That works on the model: go to the Model tab first');return false;}\n", "")],
    'acts_reach_model': [("    if(bimSheetOnScreen()&&!BIM_SHEET_ACTS[act]){a3dToast('That works on the model: go to the Model tab first');return;}   /* __acad3dV116 */\n", "")],
    'dock_stays': [("    '.a3d-sheetview.open~#a3d-dock{display:none}'+", "    ''+")],

    # ---- per project, and exports
    'last_model_global': [("    A3D_LAST_MODEL_VIEW=(rt&&rt.lastModel)||null;   /* __acad3dV116", "    void 0;   /* __acad3dV116")],
    'export_decorated': [("      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM,true);   /* __acad3dV116 */\n      var dataURL=cv.toDataURL('image/png');\n      var a=",
                          "      var cv=bimRenderSheet(sheet,SHEET_EXPORT_PXMM,false);   /* __acad3dV116 */\n      var dataURL=cv.toDataURL('image/png');\n      var a=")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV116' in txt
out.write_text(txt, encoding='utf-8')
