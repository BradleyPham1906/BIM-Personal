"""falsify_phase144.py -- break the V144 build one way at a time, keeping the marker.

Each variant takes back one thing V144 does, and the V144 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the triangles
    'own_faces_ignored': [("    if(o.faces&&o.faces.length){\n      res.tris=", "    if(false){\n      res.tris=")],
    'no_forcing': [("      cons.push([a,b]);\n      if(hasEdge(a,b))return;", "      cons.push([a,b]);\n      return;")],
    'no_split_on_points': [("      if(w>=0){force(a,w,name);force(w,b,name);return;}", "")],
    'crossings_not_split': [("      cuts[la][sa].push([ta,X[0],X[1],hX]);cuts[lb][sb].push([tb,X[0],X[1],hX]);", "")],
    'survey_codes_ignored': [("    bimSurveyBreaklines(o).forEach(function(bl){L2.push(", "    [].forEach(function(bl){L2.push(")],
    'new_vertex_height_zero': [("      var h=(p.length>2&&isFinite(p[2])&&p[2]!==null)?p[2]:bimTinHeightAt(baseTin,p[0],p[1]);", "      var h=(p.length>2&&isFinite(p[2])&&p[2]!==null)?p[2]:0;")],
    'boundary_not_clipped': [("        if(bimPointInPoly([cx,cz],bnd))keepT.push(tr);", "        keepT.push(tr);")],
    'boundary_not_forced': [("    if(bnd)L2.push({name:'boundary',", "    if(false)L2.push({name:'boundary',")],
    'outside_not_counted': [("      for(i=0;i<S.length;i++)if(!used[i])outP[i]=1;", "")],
    'cache_never_rebuilt': [("    if(!c||c.key!==key)c=BIM_TIN_CACHE[o.id]=bimTinBuild(o,key);", "    if(!c)c=BIM_TIN_CACHE[o.id]=bimTinBuild(o,key);")],
    'check_counts_trimmed': [("        if(tin.outside&&tin.outside[i]){trimmed++;continue;}   /* __acad3dV144: outside the boundary, by design */", "")],
    # ---- analysis
    'slope_not_percent': [("    return {slope:Math.sqrt(a*a+b*b)*100,aspect:az,area:Math.abs(d)/2};", "    return {slope:Math.sqrt(a*a+b*b)*10,aspect:az,area:Math.abs(d)/2};")],
    'aspect_uphill': [("    var dx=-a,dz=-b,az=", "    var dx=a,dz=b,az=")],
    'aspect_ignores_north': [("    var tn=bimTrueNorthDeg()*Math.PI/180,east=[Math.cos(tn),Math.sin(tn)]", "    var tn=0,east=[Math.cos(tn),Math.sin(tn)]")],
    'aspect_no_flat': [("      else k=pl.slope<2?0:1+Math.floor(((pl.aspect+22.5)%360)/45);", "      else k=1+Math.floor(((pl.aspect+22.5)%360)/45);")],
    'aspect_unrounded': [("      else k=pl.slope<2?0:1+Math.floor(((pl.aspect+22.5)%360)/45);", "      else k=pl.slope<2?0:1+Math.floor((pl.aspect%360)/45);")],
    'area_doubled': [("    return {slope:Math.sqrt(a*a+b*b)*100,aspect:az,area:Math.abs(d)/2};", "    return {slope:Math.sqrt(a*a+b*b)*100,aspect:az,area:Math.abs(d)};")],
    'elevation_by_vertex': [("      else if(mode==='elevation'){var hm=(tin.H[tr[0]]+tin.H[tr[1]]+tin.H[tr[2]])/3;", "      else if(mode==='elevation'){var hm=tin.H[tr[0]];")],
    # ---- LandXML
    'export_no_north_turn': [("    var dE=x*ct+z*st,dN=x*st-z*ct;", "    var dE=x,dN=-z;")],
    'export_units_ignored': [("    return {n:b.n+dN/u,e:b.e+dE/u,z:b.z+y/u,units:un};", "    return {n:b.n+dN,e:b.e+dE,z:b.z+y,units:un};")],
    'export_no_source_data': [("    if((o.breaklines&&o.breaklines.length)||(o.boundary&&o.boundary.length>=3)){\n      src+='<SourceData>';", "    if(false){\n      src+='<SourceData>';")],
    'import_invisible_kept': [("          if(f.getAttribute('i')==='1')return;", "")],
    'import_winding_kept': [("          faces.push(cr>0?[a,b,c]:[a,c,b]);", "          faces.push([a,b,c]);")],
    'import_feet_as_metres': [("    if(im){var lu=String(im.getAttribute('linearUnit')||'');un=/survey/i.test(lu)?'usft':'ft';}", "    if(im){un='m';}")],
    'import_no_base': [("        if(!base){base={n:pts[0].n,e:pts[0].e,z:0,units:un};A3D.site.surveyBase={n:base.n,e:base.e,z:0,units:un};}", "        if(!base){base={n:0,e:0,z:0,units:un};}")],
    'importcad_no_xml': [("    }else if(ext==='xml'||ext==='landxml'){   /* __acad3dV144: LandXML */", "    }else if(false){")],
    # ---- the app
    'no_props_group': [("    if(o.t==='terrain'&&o.survey)h+=bimPropGroup('Terrain Analysis',bimTerrainPropsHtml(o));   /* __acad3dV144 */\n", "")],
    'view_select_dead': [("      if(f==='terrview'){bimTerrainSetView(o,inp.value);return;}      /* __acad3dV144 */\n", "")],
    'remove_dead': [("      if(f.indexOf('terrdrop:')===0){var tdo=objById(A3D.sel);if(tdo)bimTerrainEdit(tdo,f.slice(9));return;}   /* __acad3dV144 */\n", "")],
    'not_coloured_in_plan': [("        var tb=o.tview?bimTerrainBands(tin,o.tview):null;", "        var tb=null;")],
    'no_legend': [("    if(legendFor){try{A3D.lastTerrainLegend=", "    if(false){try{A3D.lastTerrainLegend=")],
    'no_card': [("    C.push({id:'terrain',title:'Terrain: Slope, Elevation, Aspect',", "    if(0)C.push({id:'terrain',title:'Terrain: Slope, Elevation, Aspect',")],
    'view_command_selection_only': [("    if(!T.length)T=A3D.objs.filter(function(o){return o.t==='terrain'&&o.survey;});\n    if(!T.length){a3dToast('There is no terrain surface: make one with SURVEY, or import LandXML');return null;}",
                                     "    if(!T.length){a3dToast('There is no terrain surface: make one with SURVEY, or import LandXML');return null;}")],
    'breakline_not_saved': [("      ter.breaklines.push({name:o.name,pts:p,from:o.id});", "      ter.breaklines.push({name:o.name,pts:p});")],
    'no_undo_on_edit': [("    if(!o||o.t!=='terrain')return false;\n    pushUndo();\n    if(what==='breaklines')", "    if(!o||o.t!=='terrain')return false;\n    if(what==='breaklines')")],
    'no_commands': [("    slopemap:function(){bimTerrainViewCommand('slope');},\n", "")],
}


name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV144' in txt
out.write_text(txt, encoding='utf-8')
