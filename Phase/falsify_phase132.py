"""falsify_phase132.py -- break the V132 build one way at a time, keeping the marker.

Each variant takes back one thing V132 does, and the V132 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 132a: georeferencing
    'tn_ignored': [("    var t=bimTrueNorthDeg()*BIM_D2R,c=Math.cos(t),s=Math.sin(t),R=bimGeoRadii(org.lat);\n    var E=x*c+z*s,N=x*s-z*c;",
                    "    var t=0,c=Math.cos(t),s=Math.sin(t),R=bimGeoRadii(org.lat);\n    var E=x*c+z*s,N=x*s-z*c;")],
    'sphere_not_ellipsoid': [("return {M:BIM_WGS84_A*(1-BIM_WGS84_E2)/Math.pow(w,1.5),N:BIM_WGS84_A/Math.sqrt(w)};", "return {M:BIM_WGS84_A,N:BIM_WGS84_A};")],
    'north_flipped': [("    var E=x*c+z*s,N=x*s-z*c;", "    var E=x*c+z*s,N=x*s+z*c;")],
    'lon_not_scaled': [("return [org.lon+E/(R.N*Math.cos(org.lat*BIM_D2R))/BIM_D2R,", "return [org.lon+E/R.N/BIM_D2R,")],
    # ---- 132a: which tiles
    'zoom_off_by_one': [("    z=Math.max(1,Math.min(maxz,z));\n    for(;;){", "    z=Math.max(1,Math.min(maxz,z+1));\n    for(;;){")],
    'no_tile_cap': [("      if((x1-x0+1)*(y1-y0+1)<=BIM_MAP_MAXT||z<=1)break;", "      break;")],
    'no_horizon_clamp': [("        if(d>R)p=[tg[0]+dx*R/d,g,tg[2]+dz*R/d];\n", "")],
    'side_drawn': [("    if(!pts.length){r.reason='side';return r;}", "")],
    'not_nearest_first': [("    T.sort(function(a,b){return a.k-b.k;});\n", "")],
    'on_by_default': [("    return {style:BIM_MAP_STYLES[m.style]?m.style:'off',", "    return {style:BIM_MAP_STYLES[m.style]?m.style:'street',")],
    # ---- 132a: the store
    'no_inflight_cap': [("    if(!ask||A3D_MAP.inflight>=BIM_MAP_INFLIGHT)return null;", "    if(!ask)return null;")],
    'no_parent_fallback': [("    for(d=1;d<=4&&t.z-d>=0;d++){", "    for(d=1;d<=0;d++){")],
    'no_eviction': [("    if(A3D_MAP.n<=BIM_MAP_CACHE)return;", "    return;")],
    'no_cors_request': [("    e.img.crossOrigin='anonymous';\n", "")],
    'failures_kept': [("    if(field==='style'||field==='url')bimMapForgetFailures();\n", "")],
    # ---- 132a: drawing
    'no_2d_map': [("      if(!glOn)bimMapDraw2D(ctx,V,W,H);", "")],
    'map_on_paper': [("  function bimMapDraw2D(ctx,V,W,H){\n    if(A3D_PLOT.on)return;", "  function bimMapDraw2D(ctx,V,W,H){")],
    'opacity_ignored': [("      gl.uniform1f(P.alpha,plan.opacity);", "      gl.uniform1f(P.alpha,1.0);")],
    # ---- 132a: the credit line, settings
    'failures_unnamed': [("    if(bad.length)h+=' <span class=\"a3d-mapwarn\">'+bimEsc(bad.join('; '))+'</span>';\n", "")],
    'no_credit_link': [("    h=(st.style!=='custom'&&sd.link)?", "    h=false?")],
    'sheet_shows_credit': [(".a3d-sheetview.open~#a3d-mapattr{display:none}\n", "")],
    'opacity_unbounded': [("if(!isFinite(v)||v<10||v>100){a3dToast('The map opacity is from 10 to 100%');", "if(!isFinite(v)){a3dToast('The map opacity is from 10 to 100%');")],
    'url_unchecked': [("      if(nv&&(!/^https?:\\/\\/[^\\s\\/]+\\/\\S*$/i.test(nv)||nv.indexOf('{z}')<0||nv.indexOf('{x}')<0||nv.indexOf('{y}')<0)){", "      if(false){")],
    'setting_not_undoable': [("    if(st[field]===nv)return true;\n    pushUndo();", "    if(st[field]===nv)return true;")],
    # ---- 132b: the address
    'find_unthrottled': [("    if(A3D_MAP.lastFind&&now-A3D_MAP.lastFind<1000){a3dToast('One search a second: Nominatim asks for no more');return null;}\n", "")],
    'find_not_undoable': [("  function bimMapPlace(lat,lon,name){\n    pushUndo();", "  function bimMapPlace(lat,lon,name){")],
    'find_keeps_map_off': [("    if(!BIM_MAP_STYLES[A3D.site.map.style])A3D.site.map.style='street';\n", "")],
    'find_keeps_view': [("    A3D.cam.tx=0;A3D.cam.tz=0;\n", "")],
    'enter_does_nothing': [("      if(!a||ev.key!=='Enter')return;", "      return;")],
    'map_group_missing': [("    h+=bimPropGroup('Map',bimMapPropsHtml());   /* __acad3dV132 */\n", "")],
    # ---- 132b: site data in
    'projected_placed': [("          if(Math.abs(pt[k][0])>180||Math.abs(pt[k][1])>90){", "          if(false){")],
    'crs_ignored': [("    if(crs&&!/(CRS84|4326)$/i.test(String(crs)))", "    if(false)")],
    'closing_kept': [("          if(pt.length>1&&a0[0]===aN[0]&&a0[1]===aN[1])pt.pop();\n", "")],
    'holes_dropped': [("    function ring(r,i){P.push({kind:'ring',pts:r,hole:i>0});}", "    function ring(r,i){if(!i)P.push({kind:'ring',pts:r,hole:false});}")],
    'props_dropped': [("        o.geo={source:name.slice(0,120),props:pr};", "        o.geo={source:name.slice(0,120),props:{}};")],
    'no_site_from_data': [("        A3D.site.sun.lat=Math.round((la0+la1)/2*1e7)/1e7;\n        A3D.site.sun.lon=Math.round((lo0+lo1)/2*1e7)/1e7;\n",
                           "        A3D.site.sun.lat=0;\n        A3D.site.sun.lon=0;\n")],
    'import_not_undoable': [("    pushUndo();\n    undoSuspend=true;\n    try{\n      if(!org){", "    undoSuspend=true;\n    try{\n      if(!org){")],
    'current_layer_moved': [("      if(bimLayerById(was))A3D.activeLayer=was;\n      for(i=0;i<parts.length;i++){", "      for(i=0;i<parts.length;i++){")],
    'kml_no_extdata': [("      all(pm,'Data').forEach(function(d){props[d.getAttribute('name')||'value']=txt(d,'value');});\n", "")],
    'geo_props_not_shown': [("    if(o.geo)h+=bimGeoPropsHtml(o);                     /* __acad3dV132 */\n", "")],
    # ---- 132b: the plan out
    'export_offset_dropped': [("    function ring(pts,off){var r=pts.map(function(p){return P(p[0]+off[0],p[1]+off[2]);});", "    function ring(pts,off){var r=pts.map(function(p){return P(p[0],p[1]);});")],
    'export_unclosed': [("if(r.length)r.push(r[0].slice());return r;}", "return r;}")],
    'mass_not_exported': [("      }else if(bimUsageTarget(o)==='mass'){", "      }else if(false){")],
    'export_without_place': [("    if(!org)return {error:'Set the site latitude and longitude first, or find an address: they put model 0,0 on the earth'};\n", "")],
    'site_props_not_exported': [("      if(o.geo&&o.geo.props)for(k in o.geo.props)if(o.geo.props.hasOwnProperty(k))pr[k]=o.geo.props[k];\n", "")],
    # ---- 132b: commands
    'map_cmd_no_custom': [("    do{i=(i+1)%BIM_MAP_ORDER.length;nx=BIM_MAP_ORDER[i];}while(nx==='custom'&&!st.url);", "    do{i=(i+1)%BIM_MAP_ORDER.length;nx=BIM_MAP_ORDER[i];}while(nx==='custom');")],
    'not_on_ribbon': [("{t:'Site',small:['bim:map','bim:findaddress','bim:geoimport',", "{t:'Site',small:[")],
    'no_search_terms': [("    MAP:'basemap satellite imagery aerial photo street openstreetmap osm tiles background giraffe',   /* __acad3dV132 */\n", "")],
    'filein_no_geojson': [('accept=".dxf,.ifc,.obj,.stl,.json,.geojson,.kml"', 'accept=".dxf,.ifc,.obj,.stl,.json"')],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV132' in txt
out.write_text(txt, encoding='utf-8')
