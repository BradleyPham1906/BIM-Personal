"""falsify_phase163.py -- break the V163 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the reader ----
    'reader_missing': [("var OpenSkp=(function(){", "var OpenSkpGone=(function(){")],
    'reader_in_engine': [("return OpenSkp;\n})();\n</script>\n\n<script>\n/* The BIM engine", "return OpenSkp;\n})();\n/* The BIM engine")],
    'licence_dropped': [("   Permission to use, copy, modify, and/or distribute this software for any purpose", "   Use freely")],
    # ---- the objects ----
    'backs_kept': [("      for(i=0;i<drop.length;i++)keep[drop[i][0]][drop[i][1]]=false;", "")],
    'back_wrong_side': [("      if(co===fb&&ce!==fb)drop=O;\n      else if(ce===fb&&co!==fb)drop=E;", "      if(co===fb&&ce!==fb)drop=E;\n      else if(ce===fb&&co!==fb)drop=O;")],
    'no_weld': [("      var key=X+','+Y+','+Z;\n", "      var key=n+':'+X+','+Y+','+Z;\n")],
    'mirror_inside_out': [("      f.push(det<0?[a,c,b]:[a,b,c]);", "      f.push([a,b,c]);")],
    'matrix_order': [("for(c=0;c<4;c++)for(r=0;r<4;r++){s=0;for(k=0;k<4;k++)s+=a[k*4+r]*b[c*4+k];o[c*4+r]=s;}",
                      "for(c=0;c<4;c++)for(r=0;r<4;r++){s=0;for(k=0;k<4;k++)s+=b[k*4+r]*a[c*4+k];o[c*4+r]=s;}")],
    'no_world_transform': [("      var M=isRoot?BIM_SKP_ID:bimSkpMul(W,n.matrix||BIM_SKP_ID),pth=", "      var M=isRoot?BIM_SKP_ID:(n.matrix||BIM_SKP_ID),pth=")],
    'unlocked': [("mesh:q.mesh,layer:ly.id,locked:true,", "mesh:q.mesh,layer:ly.id,locked:false,")],
    'unpainted_in_tag_colour': [("col:mn?bimSkpHex(L):BIM_SKP_DEFAULT,", "col:bimSkpHex(L),")],
    'brackets_kept': [("function bimSkpMatShown(n){return String(n||'').replace(/^\\[(.*)\\]$/,'$1');}", "function bimSkpMatShown(n){return String(n||'');}")],
    'material_unnamed': [("      return String(m.name||'');\n    }\n    return '';", "      return '';\n    }\n    return '';")],
    'undo_per_layer': [("      pushUndo();\n      undoSuspend=true;\n      try{\n        var fl=bimSkpLayer(", "      pushUndo();\n      try{\n        var fl=bimSkpLayer(")],
    # ---- the layers ----
    'tags_flat': [("bimSkpLayer(stem+' - '+tg,info.color,fl.id,made)", "bimSkpLayer(stem+' - '+tg,info.color,null,made)")],
    'hidden_tag_on': [("if(got.fresh&&info.hidden){got.ly.visible=false;hiddenTags++;}", "if(got.fresh&&info.hidden){hiddenTags++;}")],
    'tag_colour_lost': [("bimSkpLayer(stem+' - '+tg,info.color,fl.id,made)", "bimSkpLayer(stem+' - '+tg,'#888888',fl.id,made)")],
    'glass_opaque': [("          if(q.opacity<1&&ly.visible!==false){", "          if(false){")],
    'glass_not_under_tag': [("bimSkpLayer(ly.name+' - '+pct+'% see-through',ly.color,ly.id,made)", "bimSkpLayer(ly.name+' - '+pct+'% see-through',ly.color,fl.id,made)")],
    'transparency_inverted': [("pct=Math.max(5,Math.min(90,Math.round((1-q.opacity)*20)*5))", "pct=Math.max(5,Math.min(90,Math.round(q.opacity*20)*5))")],
    'current_layer_taken': [("    var ly=bimLayerNew({name:n,color:color,parent:parentId||null});", "    var ly=bimLayerNew({name:n,color:color,parent:parentId||null,current:true});"),
                            ("      if(bimLayerById(was))A3D.activeLayer=was;\n    }\n    /* the components", "    }\n    /* the components")],
    'own_layer_taken': [("    while(ex&&(ex.parent||null)!==(parentId||null)){", "    while(false){")],
    'reopen_new_layers': [("    if(ex)return {ly:ex,fresh:false};", "    if(ex&&false)return {ly:ex,fresh:false};")],
    # ---- the blocks ----
    'group_is_block': [("    return !!m&&!(defNames&&defNames.hasOwnProperty(m[1]));", "    return false;")],
    'make_unique_lost': [("    return !!m&&!(defNames&&defNames.hasOwnProperty(m[1]));", "    return !!m;")],
    'english_only': [("    var m=/^([^#]+)#\\d+$/.exec(String(n||''));", "    var m=/^((?:Group|Component)\\d*)#\\d+$/.exec(String(n||''));")],
    'blocks_world_frame': [("        var M=top?BIM_SKP_ID:bimSkpMul(W,n.matrix||BIM_SKP_ID),c;", "        var M=top?(n.matrix||BIM_SKP_ID):bimSkpMul(W,n.matrix||BIM_SKP_ID),c;")],
    'blocks_without_insides': [("        for(c=0;c<(n.children||[]).length;c++)inner(n.children[c],M,false);", "")],
    'blocks_doubled': [("          if(bimAssetKind(ex)==='block'&&ex.category==='SketchUp'&&ex.source===entry.source&&ex.name===entry.name)A3D_FAMLIB.splice(d,1);", "")],
    'blocks_not_saved': [("      if(kept.length){bimSaveFamilyLibrary();refreshFamilyPanel();}", "      if(kept.length){refreshFamilyPanel();}")],
    'blocks_locked': [("          return {id:'skp-'+k,t:'solid',name:q.name,col:q.col,pos:[0,0,0],mesh:q.mesh,layer:lid,", "          return {id:'skp-'+k,t:'solid',name:q.name,col:q.col,pos:[0,0,0],mesh:q.mesh,layer:lid,locked:true,")],
    'blocks_only_places': [("    if(!opt.blocksOnly&&S.parts.length){", "    if(S.parts.length){")],
    'block_limit_ignored': [("        if(B.tris>BIM_SKP.blockTris){big++;continue;}", "")],
    'room_ignored': [("        if(chars+sz>BIM_SKP.blockChars){room++;continue;}", "")],
    'one_block_plural': [("(kept.length===1?' kept as a block':'s kept as blocks')", "(kept.length===1?' kept as blocks':'s kept as blocks')")],
    # ---- what goes wrong ----
    'tri_limit_ignored': [("        if(count&&tris+keep[j].length>BIM_SKP.maxTris){trunc=true;return made;}", "")],
    'read_error_vague': [("return {error:'Could not read '+name+' as a SketchUp file: '+bimSkpWhy(eR)};", "return {error:'Import failed'};")],
    'empty_not_said': [("    if(!buf||!(buf.byteLength>0))return {error:name+' is empty'};", "")],
    'no_reader_crash': [("    return (typeof OpenSkp!=='undefined'&&OpenSkp&&typeof OpenSkp.buildInstancedScene==='function'&&typeof OpenSkp.parseSkp==='function')?OpenSkp:null;",
                         "    return OpenSkp;")],
    'version_guessed': [("name:v>=13?'SketchUp '+(2000+v):", "name:v>=13?'SketchUp '+v:")],
    # ---- the ways in ----
    'filein_no_skp': [('accept=".dxf,.ifc,.obj,.stl,.skp,.json,', 'accept=".dxf,.ifc,.obj,.stl,.json,')],
    'import_route_missing': [("    }else if(ext==='skp'){   /* __acad3dV163: SketchUp */\n      reader.onload=function(ev){bimImportSKP(ev.target.result,name);};\n      reader.readAsArrayBuffer(file);\n", "")],
    'toast_errors_only': [("      a3dToast(r.error||r.text);\n    },30);", "      if(r.error)a3dToast(r.error);\n    },30);")],
    'skpin_missing': [("    ['SKPIN',['IMPORTSKP','SKETCHUP'],'skpin','Open a SketchUp file: its faces as solids, its tags as layers, its components as blocks'],   /* __acad3dV163 */\n", "")],
    'skpin_unsearchable': [("    SKPIN:'sketchup skp trimble import open model components groups tags materials 3d warehouse',   /* __acad3dV163 */\n", "")],
    'famfile_no_skp': [('<input type="file" id="a3d-famfilein" accept=".obj,.stl,.skp"', '<input type="file" id="a3d-famfilein" accept=".obj,.stl"')],
    'family_import_places': [("      reader.onload=function(ev){bimImportSKP(ev.target.result,name,{blocksOnly:true});};", "      reader.onload=function(ev){bimImportSKP(ev.target.result,name);};")],
    'assets_meta_plain': [("(blocks[i].category==='SketchUp'?'SketchUp, ':'')+", "")],
    'assets_search_name_only': [("[blocks[i].name||'',blocks[i].category||'',blocks[i].source||'','block']", "[blocks[i].name||'','block']")],
    'assets_tip_old': [("Import an OBJ or STL model into the library, or a SketchUp file\\'s components as blocks", "Import an OBJ or STL model into the library")],
    # ---- properties ----
    'props_missing': [("    if(o.skp)h+=bimPropGroup('SketchUp',bimSkpPropsHtml(o));   /* __acad3dV163 */\n", "")],
    'props_texture_unsaid': [("    if(s.texture)r+=bimPropText('Texture',s.texture+', drawn in the colour SketchUp keeps with it');\n", "")],
    'props_inside_unsaid': [("    if(s.path&&s.path.length>1)r+=bimPropText('Inside',s.path.slice(0,-1).join(' / '));\n", "")],
    # RETIRED IN V164: 'version_old' -- anchored on V163's version; V164's script checks the version now.
    # 'version_old': [("  var BIM_APP_VERSION={v:'V163',date:'2026-10-10'};", "  var BIM_APP_VERSION={v:'V162',date:'2026-10-10'};")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV163' in txt
out.write_text(txt, encoding='utf-8')
