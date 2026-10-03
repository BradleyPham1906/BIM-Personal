"""falsify_phase136.py -- break the V136 build one way at a time, keeping the marker.

Each variant takes back one thing V136 does, and the V136 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 136a: values
    'usage_own_colour_ignored': [("return u?{v:'u:'+u.id,name:u.name,col:u.color}:null;}", "return u?{v:'u:'+u.id,name:u.name}:null;}")],
    'level_name_order': [("for(k=0;k<A3D.levels.length;k++)if(A3D.levels[k].id===o.level)return {v:'l:'+k,name:A3D.levels[k].name,order:k};",
                          "for(k=0;k<A3D.levels.length;k++)if(A3D.levels[k].id===o.level)return {v:'l:'+k,name:A3D.levels[k].name};")],
    'type_unnamed': [("return k?{v:'t:'+k,name:(TYPES[k]&&TYPES[k].n)||", "return k?{v:'t:'+k,name:")],
    'layer_ignored': [("    if(st.by==='layer'){ly=bimLayerById(o.layer);return ly?{v:'y:'+ly.id,name:ly.name}:null;}\n", "")],
    'material_ignored': [("    if(st.by==='material')return o.materialName?{v:'m:'+o.materialName,name:o.materialName}:null;\n", "")],
    'context_height_ignored': [("    if(o.context&&typeof o.context.height==='number'&&isFinite(o.context.height))return o.context.height;\n", "")],
    'tags_ignored': [("    if(o.context&&o.context.tags)take(o.context.tags);\n", "")],
    'geo_props_ignored': [("    if(o.geo&&o.geo.props)take(o.geo.props);\n", "")],
    'numbers_as_words': [("      if(typeof v==='number'||(/^-?\\d+(\\.\\d+)?$/.test(String(v))&&isFinite(parseFloat(v))))return {num:parseFloat(v),raw:String(v)};\n", "")],
    'keys_unsorted': [("    out.sort(function(a,b){return cnt[b]-cnt[a]||(a<b?-1:(a>b?1:0));});", "")],
    # ---- 136a: scale
    'categories_unsorted': [("      var p=A.name.toLowerCase(),q=B.name.toLowerCase();return p<q?-1:(p>q?1:0);", "      return 0;")],
    'ramp_reversed': [("    for(i=0;i<BIM_LENS_RAMP.length;i++)bins.push({lo:lo+step*i,hi:i===BIM_LENS_RAMP.length-1?hi:lo+step*(i+1),col:BIM_LENS_RAMP[i],n:0});",
                       "    for(i=0;i<BIM_LENS_RAMP.length;i++)bins.push({lo:lo+step*i,hi:i===BIM_LENS_RAMP.length-1?hi:lo+step*(i+1),col:BIM_LENS_RAMP[BIM_LENS_RAMP.length-1-i],n:0});")],
    'top_value_dropped': [("      i=Math.min(sc.bins.length-1,Math.max(0,Math.floor((x.num-sc.lo)/(sc.hi-sc.lo)*sc.bins.length)));",
                           "      i=Math.max(0,Math.floor((x.num-sc.lo)/(sc.hi-sc.lo)*sc.bins.length));")],
    'no_value_coloured': [("        else{cur.col[ids[i]]=BIM_LENS_NONE;cur.none++;}", "        else{cur.col[ids[i]]=null;cur.none++;}")],
    'prop_without_name_colours': [("    if(st.by&&!(st.by==='prop'&&!st.prop)){", "    if(st.by){")],
    # ---- 136a: where it shows
    'not_in_gl': [("col=bimHexToRgb(bimLensCol(o)||o.col||(TYPES[o.t]||{}).c||'#7f9db8');", "col=bimHexToRgb(o.col||(TYPES[o.t]||{}).c||'#7f9db8');")],
    'presentation_wins': [("      var baseFill=pl.lens?pl.col:((rg&&rg.fill!=='none')?rg.fill:pl.col);", "      var baseFill=(rg&&rg.fill!=='none')?rg.fill:pl.col;")],
    'not_in_2d': [("      var lcol=bimLensCol(ob),col=lcol||ob.col||", "      var lcol=null,col=ob.col||")],
    'stale_per_paint': [("    A3D_LENS.cur=null;   /* __acad3dV136: the lens is worked out once per paint */\n", "")],
    'lens_not_undoable': [("    pushUndo();\n    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};\n    A3D.site.lens=",
                           "    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};\n    A3D.site.lens=")],
    'lens_not_kept': [("    var l=A3D.site&&A3D.site.lens;", "    var l=A3D_LENS.mem;")],
    # ---- 136a: legend
    'no_legend': [("    drawLensLegend(ctx,V,W,H);         /* __acad3dV136: the lens's and the data layers' legend, below it */\n", "")],
    'legend_on_paper': [("    A3D.lastLensLegend=null;\n    if(A3D.sheetCapture||A3D_PLOT.on)return;", "    A3D.lastLensLegend=null;")],
    'legend_no_none_row': [("    if(none)r.push({col:BIM_LENS_NONE,name:'no value',n:none});\n", "")],
    'legend_empty_bins': [("      for(i=0;i<sc.bins.length;i++)if(sc.bins[i].n)r.push(", "      for(i=0;i<sc.bins.length;i++)r.push(")],
    'legend_no_data_layers': [("      if(rows.length)blocks.push({title:L[i].name+': '+L[i].by,rows:rows});", "")],
    # ---- 136a: data layers
    'data_lens_ignored': [("        if(ds){fc=bimDataFeatCol(L[i],ds,f.fi);ctx.strokeStyle=fc;ctx.fillStyle=fc;}", "")],
    'data_attr_unchecked': [("if(v&&bimDataAttrKeys(id).indexOf(v)<0){a3dToast(L.name+' has no attribute '+v);refreshProps();return false;}", "")],
    'opacity_ignored': [("      ctx.globalAlpha=(sel?Math.min(1,fa*2.1):fa)*op;ctx.fill('evenodd');ctx.globalAlpha=op;ctx.stroke();",
                         "      ctx.globalAlpha=(sel?Math.min(1,fa*2.1):fa);ctx.fill('evenodd');ctx.globalAlpha=1;ctx.stroke();")],
    'opacity_unclamped': [("v=Math.max(0.1,Math.min(1,v>1?v/100:v));", "v=v>1?v/100:v;")],
    'opacity_nan_kept': [("v=parseFloat(val);if(!isFinite(v)){a3dToast('Opacity is a percentage, 10 to 100');refreshProps();return false;}", "v=parseFloat(val)||0.5;")],
    'data_numbers_as_words': [("      if(typeof v==='number'||(/^-?\\d+(\\.\\d+)?$/.test(String(v))&&isFinite(parseFloat(v))))vals.push({num:parseFloat(v)});\n      else vals.push",
                               "      vals.push")],
    # ---- 136b
    'no_lens_row': [("    vrows+=bimLensHtml();   /* __acad3dV136: the lens */\n", "")],
    'no_prop_row': [("    if(st.by==='prop'){\n      keys=bimLensPropKeys();", "    if(false){\n      keys=bimLensPropKeys();")],
    'no_data_lens_row': [("      r+=bimDataLensRow(L[i]);   /* __acad3dV136 */\n", "")],
    'data_by_not_wired': [("    if(b[0]==='by')return bimDataSet(b[1],'by',f.value);             /* __acad3dV136 */\n", "")],
    'lens_select_not_wired': [("    if(k==='by'){bimLensSet(f.value,f.value==='prop'?st.prop:'');return true;}", "    if(k==='by'){return true;}")],
    'no_command': [("    colourby:function(){bimLensCommand();},          /* __acad3dV136 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV136' in txt
out.write_text(txt, encoding='utf-8')
