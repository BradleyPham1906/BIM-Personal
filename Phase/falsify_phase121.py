"""falsify_phase121.py -- break the V121 build one way at a time, keeping the marker.

Each variant takes back one thing V121 does, or breaks one thing it built, and the V121 suite must
fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the questions and the rules
    'site_reads_flag': [("      if(!bimLayerShown(o))continue;   /* __acad3dV121: a hidden layer's corners were snap targets */\n",
                         "      var lyr=bimLayerOf(o);if(lyr&&lyr.visible===false)continue;\n")],
    'off_not_selectable': [("    return !s.frozen&&!s.locked;\n", "    return s.on&&!s.frozen&&!s.locked;\n")],
    'frozen_selectable': [("    return !s.frozen&&!s.locked;\n", "    return !s.locked;\n")],
    'current_freezable': [("      if(field==='frozen'&&v&&cur&&bimLayerUnder(cur,ly.id))\n", "      if(false)\n")],
    'frozen_current': [("    if(bimLayerEff(ly).frozen)return bimLayerRefuse('A frozen layer cannot be current: thaw it first');\n", "")],
    'name_case_sensitive': [("      if(A3D.layers[i].id!==exceptId&&String(A3D.layers[i].name).toLowerCase()===n)return A3D.layers[i];\n",
                             "      if(A3D.layers[i].id!==exceptId&&String(A3D.layers[i].name)===n)return A3D.layers[i];\n")],
    'delete_with_objects': [("    if(n)return bimLayerRefuse(ly.name+' holds '+n+' object'+(n===1?'':'s')+': move '+(n===1?'it':'them')+' to another layer first');\n", "")],
    'delete_first_layer': [("    if(ly===A3D.layers[0])return bimLayerRefuse(", "    if(false)return bimLayerRefuse(")],
    'transparency_unbounded': [("      if(!isFinite(v)||v<0||v>90)return bimLayerRefuse('Transparency is 0 to 90');\n",
                                "      if(!isFinite(v)||v<0)return bimLayerRefuse('Transparency is 0 to 90');\n")],
    'sub_not_inherit': [("    var s={on:true,frozen:false,locked:false,plot:true},ch=bimLayerChain(ly),i;\n",
                         "    var s={on:true,frozen:false,locked:false,plot:true},ch=[ly],i;\n")],
    'change_not_undoable': [("    if(was===v)return true;\n    pushUndo();\n    ly[field]=v;\n", "    if(was===v)return true;\n    ly[field]=v;\n")],
    'new_ignores_from': [("    var src=opts.from?bimLayerById(opts.from):par;\n", "    var src=par;\n")],
    # ---- the look
    'no_lock_fade': [("  var BIM_LOCK_FADE=50;\n", "  var BIM_LOCK_FADE=0;\n")],
    'dash_in_inches': [("  var BIM_LT_SCREEN_PXMM=24/25.4;\n", "  var BIM_LT_SCREEN_PXMM=24;\n")],
    'default_width_changed': [("    return d?base:Math.max(0.6,mm*6.4);\n", "    return d?1:Math.max(0.6,mm*6.4);\n")],
    'sketch_width_fixed': [("    ctx.lineWidth=look?look.width:1.6;\n", "    ctx.lineWidth=1.6;\n")],
    'wall_opaque': [("      var la=bimLayerAlpha(o);\n      A3D.lastGlAlpha[o.id]=la;\n", "      var la=1;\n      A3D.lastGlAlpha[o.id]=la;\n")],
    # ---- selecting
    'marquee_ignores_layers': [("      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */\n      var pts=bimObjScreenPoints(o,V,W,H);\n",
                                "      var pts=bimObjScreenPoints(o,V,W,H);\n")],
    'classification_takes_all': [("        bimSelectByRule(matches);   /* __acad3dV121: as SELECT ALL, by the layers */\n",
                                  "        window.__a3dSelectFor(matches.map(function(o){return o.id;}));refreshTree();paint();\n")],
    'lock_keeps_selection': [("    bimLayerDropUnpickable();\n    refreshLayers();refreshTree();paint();saveSoon();\n",
                              "    refreshLayers();refreshTree();paint();saveSoon();\n")],
    'locked_current_selected': [("    if(bimLayerDropUnselectable()){refreshTree();refreshProps();paint();}   /* __acad3dV121 */\n", "")],
    'checkmodel_selects_locked': [("        if(ckw){a3dToast(ckw);return;}\n", "")],
    'dependency_selects_locked': [("        if(dsw){a3dToast(dsw);return;}\n", "")],
    # ---- the panel and the manager
    'panel_on_dead': [("        if((b=t.closest('[data-lyon]'))){l=bimLayerById(b.getAttribute('data-lyon'));if(l)bimLayerSet(l.id,'visible',l.visible===false);return;}\n",
                       "        if((b=t.closest('[data-lyon]'))){return;}\n")],
    'rename_escape_keeps': [("      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimLyEndEdit(t,true);}\n",
                             "      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimLyEndEdit(t,false);}\n")],
    'drag_object_dead': [("        if(v.indexOf('obj:')===0){if(tgt)bimObjSetLayer(v.slice(4),tgt);}\n", "        if(v.indexOf('obj:')===0){}\n")],
    'search_without_parents': [("    function hit(s){return String(s).toLowerCase().indexOf(f)>=0;}\n",
                                "    function hit(s){return String(s).toLowerCase().indexOf(f)===0;}\n")],
    'layer_command_dead': [("    layers:function(){bimLayerManagerOpen();},   /* __acad3dV121: LAYER, listed since V86 and never run */\n", "")],
    'layer_refused_on_sheet': [("    newSheet:1,modelTab:1,mspace:1,pspace:1,shortcuts:1,layers:1};", "    newSheet:1,modelTab:1,mspace:1,pspace:1,shortcuts:1};")],
    'refused_cell_shows_refused': [("      catch(eF){console.warn('[BIM] A layer field could not be set',eF);a3dToast('That layer change could not be made');}\n      bimLayerManagerRefresh();\n",
                                    "      catch(eF){console.warn('[BIM] A layer field could not be set',eF);a3dToast('That layer change could not be made');}\n")],
    'no_plot_column': [("<th>Lock</th><th>Plot</th>", "<th>Lock</th>")],
    'active_layer_hand_list': [("    vrows+=bimPropRow('Active Layer','<select data-propmodel=\"layer\">'+bimLayerOptionsHtml(A3D.activeLayer)+'</select>');\n",
                                "    var lyo='';A3D.layers.forEach(function(q){lyo+='<option value=\"'+q.id+'\"'+(q.id===A3D.activeLayer?' selected':'')+'>'+bimEsc(q.name)+'</option>';});\n"
                                "    vrows+=bimPropRow('Active Layer','<select data-propmodel=\"layer\">'+lyo+'</select>');\n")],
    # ---- plots and the DXF
    'svg_not_a_plot': [("    return bimWithPlotPass(mode==='presentation',function(){return bimBuildSVGDrawing(mode);});\n",
                        "    return bimBuildSVGDrawing(mode);\n")],
    'noplot_plotted': [("    return s.on&&!s.frozen&&(s.plot||!A3D_PLOT.on);\n", "    return s.on&&!s.frozen;\n")],
    'plot_fades_lock': [("    if(A3D_PLOT.on)return A3D_PLOT.pres?a:1;\n", "")],
    'sheet_at_screen_scale': [("    var pm=(A3D.sheetCapture&&A3D_PLOT.pxmm>0)?A3D_PLOT.pxmm:0,d=(mm===null||mm===undefined||!isFinite(mm));\n",
                               "    var pm=0,d=(mm===null||mm===undefined||!isFinite(mm));\n")],
    'dxf_layers_white': [("    out=P(0,'LAYER')+P(2,bimDxfLayerName(l.name))+P(70,(s.frozen?1:0)|(s.locked?4:0))+P(62,s.on?aci:-aci);\n",
                          "    out=P(0,'LAYER')+P(2,bimDxfLayerName(l.name))+P(70,0)+P(62,7);\n")],
    'dxf_import_ignores_state': [("    if(dl.off)ly.visible=false;\n", "")],
    # ---- data
    'older_layers_rewritten': [("    if(!cur||!first)return 0;\n    for(i=0;i<A3D.layers.length;i++)ids[A3D.layers[i].id]=1;\n",
                                "    if(!cur||!first)return 0;\n    A3D.layers.forEach(function(l){if(l.frozen===undefined)l.frozen=false;});\n"
                                "    for(i=0;i<A3D.layers.length;i++)ids[A3D.layers[i].id]=1;\n")],
    'new_fields_not_stored': [("activeLevel:A3D.activeLevel,layers:A3D.layers,activeLayer:A3D.activeLayer,types:A3D.types",
                               "activeLevel:A3D.activeLevel,layers:A3D.layers.map(function(l){return {id:l.id,name:l.name,color:l.color,visible:l.visible,locked:l.locked};}),activeLayer:A3D.activeLayer,types:A3D.types")],
    'emoji_lock_back': [("(bimIsLocked(o)?'<span class=\"a3d-lockicon\" title=\"Locked (Pin)\">'+BIM_LOCK_ON+'</span>':'')",
                         "(bimIsLocked(o)?'<span class=\"a3d-lockicon\" title=\"Locked (Pin)\">\\ud83d\\udd12</span>':'')")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV121' in txt
out.write_text(txt, encoding='utf-8')
