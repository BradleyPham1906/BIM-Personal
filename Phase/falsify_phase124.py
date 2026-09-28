"""falsify_phase124.py -- break the V124 build one way at a time, keeping the marker.

Each variant takes back one thing V124 does, or breaks one thing it built, and the V124 suite must
fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 124a: the store
    'no_starter_set': [("  var A3D_ASSET_BUILTINS=A3D_ASSET_STARTER.map(function(s){", "  var A3D_ASSET_BUILTINS=[].map(function(s){")],
    'no_mesh_thumbnail': [("        if(faces.length<4000)g.stroke();\n      }\n      return c.toDataURL('image/png');",
                           "        if(faces.length<4000)g.stroke();\n      }\n      return '';")],
    'thumb_not_kept': [("    if(th&&!e.builtin)bimSaveFamilyLibrary();\n", "")],
    'old_entry_not_model': [("    return (k==='block'||k==='template')?k:'model';", "    return k;")],
    'template_key_left': [("      try{localStorage.removeItem(A3D_TEMPLATE_PREFIX+id);}", "      try{}")],
    'browser_lists_everything': [("libModels=bimLibEntries('model');", "libModels=A3D_FAMLIB.slice();")],
    # ---- 124b: import
    'import_in_metres': [("    var f=bimImportUnitScale(unit);", "    var f=1;")],
    'z_up_ignored': [("return zUp?[p[0]*f,p[2]*f,-p[1]*f]:", "return false?[p[0]*f,p[2]*f,-p[1]*f]:")],
    'guess_always_metres': [("    if(!(E>0)||!isFinite(E))return 'm';", "    return 'm';")],
    'size_not_live': [("    uI.addEventListener('change',show);yI.addEventListener('change',show);", "")],
    'unit_not_kept': [("    if(fam.unit)entry.unit=fam.unit;", "")],
    # ---- 124c: blocks and the selection model
    'model_first_only': [("    var m=bimSelectionMesh(selIds);", "    var m=bimSelectionMesh([o.id]);")],
    'block_keeps_tags': [("    return !o||o.t==='opening'||o.t==='roomtag';", "    return !o;")],
    'block_no_level_shift': [("      bimShiftObjectY(c,dY);\n", "")],
    'block_level_not_set': [("      if(c.bim&&c.bim.levelId!==undefined)c.bim.levelId=lvl.id;\n      if(c.levelId!==undefined)c.levelId=lvl.id;\n", "")],
    # ---- 124h: a copy follows what it was copied with, never the original's sources
    'links_read_from_copy': [("        var v=bimLinkGet(from,path);\n", "        var v=bimLinkGet(c,path);\n")],
    'keeps_outside_link': [("        }else{bimLinkSet(c,path,null);cut++;}", "        }else{cut++;}")],
    'region_seed_not_moved': [("          rg.seed=[rg.seed[0]+q0[0]-q1[0]+dx,rg.seed[1]+q0[2]-q1[2]+dz];\n", "")],
    'region_kept_without_members': [("        }else{\n          if(c.region)c.region=null;\n          cut++;\n        }", "        }else{\n          cut++;\n        }")],
    'duplicate_not_relinked': [("    var cut=bimRelinkCopies(pairs,1,1,0);   /* __acad3dV124 */", "    var cut=0;")],
    'block_no_undo': [("    pushUndo();\n    var mark=UNDO_STACK[UNDO_STACK.length-1];", "    var mark=null;")],
    'block_base_at_origin': [("    if(b)base=[(b.mn[0]+b.mx[0])/2,(b.mn[2]+b.mx[2])/2];", "    if(b)base=[0,0];")],
    # ---- 124d: templates
    'template_keeps_its_name': [("    rec.titleBlock.project=bimNextProjectName();\n    var id=bimDocsAdd(rec,'create');\n    if(id)a3dToast('New project '",
                                 "    var id=bimDocsAdd(rec,'create');\n    if(id)a3dToast('New project '")],
    'template_replaces_project': [("    var id=bimDocsAdd(rec,'create');\n    if(id)a3dToast('New project '",
                                   "    bimLoadProjectRecord(rec);var id=A3D_DOCS.active;\n    if(id)a3dToast('New project '")],
    # ---- 124e: the panel
    'click_at_origin': [("      bimPlaceFamilyInstance(fam,at||bimViewCentrePlan());", "      bimPlaceFamilyInstance(fam,at||[0,0]);")],
    'search_loses_focus': [("      if(nI){nI.focus();try{nI.setSelectionRange(s0,s1);}catch(eS){}}", "")],
    'search_ignored': [("    if(!q)return true;\n    return words.join(' ').toLowerCase().indexOf(q)>=0;", "    return true;")],
    'fold_dead': [("A3D_ASSETS_UI.closed[gid]=!A3D_ASSETS_UI.closed[gid];refreshAssets();", "refreshAssets();")],
    'remove_without_asking': [("    if(!confirm('Remove \"'+e.name+'\" from the library? '+what))return false;\n", "")],
    'starter_removable': [("        (e.builtin?'':'<button type=\"button\" class=\"a3d-asdel\"", "        (false?'':'<button type=\"button\" class=\"a3d-asdel\"")],
    'material_click_silent': [("      if(!o||o.t!=='solid'){a3dToast(drop?'Drop a material on a solid':'Select a solid, or drag the material onto one');return false;}",
                               "      if(!o||o.t!=='solid'){return false;}")],
    # ---- 124f: drag and drop
    'drop_at_view_centre': [("    return bimAssetAction(spec,{pt:pt,obj:obj});", "    return bimAssetAction(spec);")],
    'drop_not_snapped': [("      var sn=bimSnapPoint([cx,cy],g,{tool:'familyplace',pts:[],y:y0,on:null});\n      pt=[sn[0],sn[1]];",
                          "      pt=[g[0],g[2]];")],
    'drop_anywhere': [("    return (tg&&el.cv&&tg===el.cv)?el.cv:null;", "    return el.cv;")],
    'press_is_a_drag': [("      if(dx*dx+dy*dy<=cl*cl)return;", "      if(dx*dx+dy*dy<=0)return;")],
    'release_click_places': [("        if(A3D_ASDRAG_EAT)return;   /* __acad3dV124: the click sent with the release that ended a drag */\n", "")],
    'escape_ignored': [("    if(ev.key==='Escape'&&bimAssetDragCancel()){a3dToast('Nothing placed');ev.preventDefault();ev.stopImmediatePropagation();return;}\n", "")],
    'no_card': [("      document.body.appendChild(g);\n      d.ghost=g;", "      d.ghost=g;")],
    'drop_on_selection': [("    if(kind==='material'||kind==='pattern'||kind==='walltype')obj=pick(cx,cy)||null;\n", "")],
    # ---- 124g: commands, toolbar, claims
    'insert_command_missing': [("    ['INSERT',['I','DDINSERT'],'blockinsert','Insert a block: drag it from the library onto the drawing'],\n", "")],
    'block_command_dead': [("    blockmake:function(){openSaveBlockDlg();},", "    blockmake:function(){},")],
    'component_toast_only': [("    if(act==='bim:component'){bimOpenLibraryAt('families');return;}", "    if(act==='bim:component'){a3dToast('Place a family from the Project Browser > Families');return;}")],
    'action_unclaimed': [("    {sel:'[data-a3dasact]',why:", "    {sel:'[data-a3dasactX]',why:")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV124' in txt
out.write_text(txt, encoding='utf-8')
