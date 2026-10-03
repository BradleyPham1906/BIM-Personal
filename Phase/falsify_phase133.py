"""falsify_phase133.py -- break the V133 build one way at a time, keeping the marker.

Each variant takes back one thing V133 does, and the V133 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 133a: the area and the query
    'area_no_radius': [("h=(n?Math.max(x1-x0,z1-z0)/2:0)+st.radius;", "h=(n?Math.max(x1-x0,z1-z0)/2:0)+150;")],
    'area_ignores_property': [("    var cx=n?(x0+x1)/2:0,cz=n?(z0+z1)/2:0,", "    var cx=0,cz=0,")],
    'area_two_corners': [("    for(i=0;i<4;i++){\n      q=bimModelToGeo(C[i][0],C[i][1],org);", "    for(i=0;i<4;i+=2){\n      q=bimModelToGeo(C[i][0],C[i][1],org);")],
    'no_trees_query': [("    if(k.trees)q.push('node[\"natural\"=\"tree\"]'+b+';');\n", "")],
    'kinds_ignored': [("    if(k.roads)q.push('way[\"highway\"]'+b+';');", "    q.push('way[\"highway\"]'+b+';');")],
    'overpass_setting_ignored': [("    var pOsm=q?fetch(st.overpass,", "    var pOsm=q?fetch(BIM_OVERPASS_URL,")],
    # ---- 133a: reading OSM
    'feet_as_metres': [("      if(m[2]&&/^(ft|feet|')$/i.test(m[2]))v*=0.3048;\n", "")],
    'levels_ignored': [("    if(isFinite(L)&&L>0&&L<300)return {h:L*BIM_CTX_LEVEL_H,from:'levels'};\n", "")],
    'zero_height_kept': [("      if(v>0&&v<1000)return {h:v,from:'height'};", "      return {h:v,from:'height'};")],
    'rings_not_joined': [("      while(!same(r[0],r[r.length-1])&&grew){", "      while(false){")],
    'open_chain_kept': [("      if(r.length>=4&&same(r[0],r[r.length-1]))rings.push(r);", "      if(r.length>=2)rings.push(r);")],
    'inner_as_outer': [("        bimOsmRings(el.members,'inner').forEach(function(r){f.inner.push(", "        bimOsmRings(el.members,'inner').forEach(function(r){f.outer.push(")],
    'trees_dropped': [("    if(el.type==='node')return t.natural==='tree'?'trees':'';", "    if(el.type==='node')return '';")],
    # ---- 133a: the ground
    'decode_off_by_one': [("e[i]=d[i*4]*256+d[i*4+1]+d[i*4+2]/256-32768;", "e[i]=d[i*4]*256+d[i*4+1]+d[i*4+2]/256-32767;")],
    'decode_no_fraction': [("e[i]=d[i*4]*256+d[i*4+1]+d[i*4+2]/256-32768;", "e[i]=d[i*4]*256+d[i*4+1]-32768;")],
    'nearest_not_bilinear': [("    return (px(ix,iy)*(1-fx)+px(ix+1,iy)*fx)*(1-fy)+(px(ix,iy+1)*(1-fx)+px(ix+1,iy+1)*fx)*fy;",
                              "    return px(Math.round(gx),Math.round(gy));")],
    'zoom_14': [("    for(z=BIM_CTX_TZ;z>1;z--){", "    for(z=14;z>1;z--){")],
    'grid_coarse': [("        var pts=[],N=BIM_CTX_GRID,", "        var pts=[],N=10,")],
    'datum_not_kept': [("if(isFinite(e0)){base=Math.round(e0*100)/100;A3D.site.terrainBase=base;}", "if(isFinite(e0)){base=Math.round(e0*100)/100;}")],
    'survey_base_ignored': [("    if(b&&isFinite(b.z))return b.z*(BIM_SURVEY_UNITS[b.units]||1);\n", "")],
    'sources_dropped': [("        String(s).split(/\\s*,\\s*/).forEach(function(v){if(v)src[v]=1;});\n", "")],
    # ---- 133a: placing
    'no_replace': [("      A3D.objs=A3D.objs.filter(function(x){return !(x.context&&repl[x.context.kind]);});\n", "")],
    'replace_all_kinds': [("    if(feats)for(i=0;i<5;i++)if(k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;", "    if(feats)for(i=0;i<6;i++)repl[BIM_CTX_KINDS[i]]=1;")],
    'fetch_not_undoable': [("    var selWas=A3D.sel,setWas=(A3D.selSet||[]).slice();\n    pushUndo();", "    var selWas=A3D.sel,setWas=(A3D.selSet||[]).slice();")],
    'not_pinned': [("x.col=BIM_CTX_COL[kind];x.locked=true;n[kind]++;", "x.col=BIM_CTX_COL[kind];n[kind]++;")],
    'layers_flat': [("ly=bimLayerByName('Context '+k)||bimLayerNew({name:'Context '+k,color:BIM_CTX_COL[k],parent:par.id});",
                     "ly=bimLayerByName('Context '+k)||bimLayerNew({name:'Context '+k,color:BIM_CTX_COL[k]});")],
    'selection_left': [("    A3D.sel=objById(selWas)?selWas:null;A3D.sel2=null;\n", "")],
    'ground_not_recorded': [("            c.ground=ground([cx/Pp.length,cz/Pp.length]);\n", "")],
    'courtyards_uncounted': [("            if(f.inner.length){c.courtyards=f.inner.length;yards+=f.inner.length;}\n", "")],
    'assumed_unsaid': [("            if(hh.from==='assumed')assumed++;\n", "")],
    # ---- 133a: failures
    'failures_unnamed': [("      else bad.push(bimCtxErr(bimMapHost(st.overpass),osm.err));\n", "")],
    'busy_not_guarded': [("    if(A3D_CTX.busy){a3dToast('The site context is already on its way');return null;}\n", "")],
    'busy_stuck': [("      A3D_CTX.busy=false;\n      try{return bimCtxApply(a,st,r[0],r[1]);}", "      try{return bimCtxApply(a,st,r[0],r[1]);}")],
    'nothing_still_steps': [("    if(!feats&&!terOk){a3dToast('No site context: '+bad.join('; '));return {error:bad.join('; ')};}", "")],
    'junk_accepted': [("        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}\n        if(!js||!js.elements)throw {bad:true};",
                       "        try{js=JSON.parse(tx);}catch(eJ){js={elements:[]};}")],
    'busy_generic': [("    if(e&&(e.http===429||e.http===504))return host+' is busy (HTTP '+e.http+'): try again in a minute';\n", "")],
    # ---- 133a: credits, usages, export
    'credit_missing': [("    if(cc)h=h?h+' \\u00b7 '+cc:cc;\n", "")],
    'osm_credit_twice': [("cc=bimCtxCreditHtml(h.indexOf('OpenStreetMap contributors')>=0);", "cc=bimCtxCreditHtml(false);")],
    'context_is_mass': [("    if(o.context)return '';   /* __acad3dV133: a neighbour is not the project's */\n", "")],
    'export_no_footprint': [("      }else if(o.context&&o.context.footprint){   /* __acad3dV133 */", "      }else if(false){")],
    'export_no_credit': [("pr.source=o.context.source;pr.credit=o.context.credit;", "pr.source=o.context.source;")],
    # ---- 133a: settings, remove
    'radius_unbounded': [("      if(!isFinite(v)||v<50||v>1000){a3dToast('The context radius is from 50 to 1000 m');", "      if(!isFinite(v)){a3dToast('The context radius is from 50 to 1000 m');")],
    'overpass_unchecked': [("      if(!/^https?:\\/\\/[^\\s\\/]+\\/\\S*$/i.test(nv)){a3dToast('An Overpass server is a web address", "      if(false){a3dToast('An Overpass server is a web address")],
    'remove_not_undoable': [("    if(!n){a3dToast('There is no site context to remove');return 0;}\n    pushUndo();", "    if(!n){a3dToast('There is no site context to remove');return 0;}")],
    # ---- 133b
    'no_site_context_group': [("    h+=bimPropGroup('Site Context',bimCtxModelHtml());   /* __acad3dV133 */\n", "")],
    'no_context_page': [("    if(o.context)h+=bimCtxPropsHtml(o);                 /* __acad3dV133 */\n", "")],
    'checkbox_value': [("    bimCtxSet(k,k.indexOf('kind:')===0?f.checked:f.value);", "    bimCtxSet(k,f.value);")],
    'context_not_on_ribbon': [("'bim:map','bim:findaddress','bim:geoimport','bim:context',", "'bim:map','bim:findaddress','bim:geoimport',")],
    'no_context_terms': [("    CONTEXT:'neighbours neighbors surrounding buildings osm openstreetmap overpass roads streets water rivers parks trees terrain elevation contours ground giraffe',   /* __acad3dV133 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV133' in txt
out.write_text(txt, encoding='utf-8')
