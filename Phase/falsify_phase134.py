"""falsify_phase134.py -- break the V134 build one way at a time, keeping the marker.

Each variant takes back one thing V134 does, and the V134 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 134a: addresses and requests
    'service_without_layer_accepted': [("    if(/\\/(FeatureServer|MapServer)\\/?(\\?.*)?$/i.test(u))return {error:", "    if(false)return {error:")],
    'wfs_without_typenames': [("      if(!/[?&]typenames?=[^&]+/i.test(u))return {error:", "      if(false)return {error:")],
    'box_wrong_order': [("    var b=[a.w,a.s,a.e,a.n].map(", "    var b=[a.s,a.w,a.n,a.e].map(")],
    'arcgis_esri_json': [("&resultRecordCount='+BIM_DATA_MAX+'&f=geojson';", "&resultRecordCount='+BIM_DATA_MAX+'&f=json';")],
    'wfs_epsg4326': [("&srsName=CRS%3A84&bbox='", "&srsName=EPSG%3A4326&bbox='")],
    'not_fetched_on_add': [("    if(bimCtxArea())bimDataFetch(lyr.id);", "    if(false)bimDataFetch(lyr.id);")],
    'duplicate_allowed': [("    for(i=0;i<L.length;i++)if(L[i].url===u){a3dToast('That layer is here already: '+L[i].name);return null;}\n", "")],
    'add_not_undoable': [("    pushUndo();\n    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};\n    if(!Array.isArray(A3D.site.dataLayers))A3D.site.dataLayers=[];\n    lyr=",
                          "    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};\n    if(!Array.isArray(A3D.site.dataLayers))A3D.site.dataLayers=[];\n    lyr=")],
    # ---- 134a: answers
    'no_area_filter': [("      if(bb[2]<a.w||bb[0]>a.e||bb[3]<a.s||bb[1]>a.n)continue;   /* not in the area */\n", "")],
    'arcgis_error_unread': [("    if(js&&js.error&&!js.type)return {error:'said: '+String(js.error.message||js.error.code||'an error').slice(0,160)};\n", "")],
    'projected_accepted': [("if(Math.abs(pt[k][0])>180||Math.abs(pt[k][1])>90)return {error:'answered in a projected grid", "if(false)return {error:'answered in a projected grid")],
    'more_ignored': [("more:!!(js&&(js.exceededTransferLimit||(js.properties&&js.properties.exceededTransferLimit)))||i<r.features.length};", "more:false};")],
    # ---- 134a: kept
    'features_not_saved': [("roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{}};", "roomScheme:A3D.roomScheme||'',classifications:A3D.classifications};")],
    'features_dropped_on_load': [("        A3D.site.dataLayers.forEach(function(L){if(L&&Array.isArray(st.dataFeatures[L.id]))A3D.dataFeatures[L.id]=st.dataFeatures[L.id];});",
                                  "        A3D.site.dataLayers.forEach(function(L){});")],
    'remove_drops_features': [("    /* its features stay stored, so an undo brings the layer back whole; a load drops orphans */\n", "    if(A3D.dataFeatures)delete A3D.dataFeatures[id];\n")],
    # ---- 134a: drawn and read
    'holes_filled': [("ctx.globalAlpha=sel?0.34:0.16;ctx.fill('evenodd');", "ctx.globalAlpha=sel?0.34:0.16;ctx.fill();")],
    'hidden_drawn': [("      if(!L[i].visible)continue;\n      c=bimDataModel(L[i]);\n      if(!c)continue;\n      ctx.save();", "      c=bimDataModel(L[i]);\n      if(!c)continue;\n      ctx.save();")],
    'hidden_picked': [("        if(!L[i].visible)continue;\n        c=bimDataModel(L[i]);\n        if(!c)continue;\n        for(j=c.feats.length-1", "        c=bimDataModel(L[i]);\n        if(!c)continue;\n        for(j=c.feats.length-1")],
    'points_not_first': [("          if(pass===0){", "          if(pass===9){")],
    'largest_area': [("if(inside%2===1&&f.area<bestA){bestA=f.area;", "if(inside%2===1&&-f.area<bestA){bestA=-f.area;")],
    'courtyard_picked': [("            if(inside%2===1&&f.area<bestA)", "            if(inside>=1&&f.area<bestA)")],
    'on_paper': [("    A3D.lastDataDrawn=0;\n    if(A3D.sheetCapture||A3D_PLOT.on)return;", "    A3D.lastDataDrawn=0;")],
    'click_not_wired': [("      A3D_DATA.sel=(o||gpk)?null:bimDataPick(xy[0],xy[1]);", "      A3D_DATA.sel=null;")],
    # ---- 134a: property line, credit
    'property_from_any_ring': [("    f.rings.forEach(function(r){if(!r.hole&&(!outer||bimPolyArea(r.pts)>bimPolyArea(outer)))outer=r.pts;});", "    f.rings.forEach(function(r){outer=r.pts;});")],
    'property_not_undoable': [("    pushUndo();\n    pr=bimNewProperty(outer[0],legs);", "    pr=bimNewProperty(outer[0],legs);")],
    'credit_missing': [("    if(dcr)h=h?h+' \\u00b7 '+dcr:dcr;\n", "")],
    'hidden_credited': [("    for(i=0;i<L.length;i++)if(L[i].visible&&bimDataFeats(L[i].id).length&&", "    for(i=0;i<L.length;i++)if(bimDataFeats(L[i].id).length&&")],
    # ---- 134b
    'no_feature_page': [("    h+=bimDataFeatureHtml();   /* __acad3dV134: the data clicked on the plan, first */\n", "")],
    'no_group': [("    h+=bimPropGroup('Data Layers',bimDataModelHtml());   /* __acad3dV134 */\n", "")],
    'checkbox_ignored': [("    if(b[0]==='vis')return bimDataSet(b[1],'visible',f.checked);", "    if(b[0]==='vis')return bimDataSet(b[1],'visible',f.value);")],
    'preset_ignored': [("      if(p)bimDataAdd(p.url,p.name,p.color,p.credit);", "      if(false)bimDataAdd(p.url,p.name,p.color,p.credit);")],
    'not_on_ribbon': [("'bim:geoimport','bim:context','bim:datalayers',", "'bim:geoimport','bim:context',")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV134' in txt
out.write_text(txt, encoding='utf-8')
