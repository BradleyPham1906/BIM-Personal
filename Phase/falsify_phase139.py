"""falsify_phase139.py -- break the V139 build one way at a time, keeping the marker.

Each variant takes back one thing V139 does, and the V139 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 139a: parts
    'query_no_parts': [("""'way["building:part"]'+b+';','relation["building:part"]["type"="multipolygon"]'+b+';');""", """'');""")],
    'part_not_a_building': [("    if(t['building:part']&&t['building:part']!=='no')return 'buildings';   /* __acad3dV139: a part */\n", "")],
    'part_flag_lost': [("      if(kind==='buildings'&&!(f.tags.building&&f.tags.building!=='no'))f.part=true;   /* __acad3dV139 */\n", "")],
    'outline_also_extruded': [("          if(!f.part&&pinfo.has[i]){nWhole++;continue;}", "          if(false){nWhole++;continue;}")],
    'low_parts_kept': [("          if(f.part&&rg.h-rg.min<0.01){lowParts++;continue;}", "")],
    'part_base_ignored': [("            try{mesh=padMesh(Pp,y0+rg.min,rg.h-rg.min);}", "            try{mesh=padMesh(Pp,y0,rg.h);}")],
    'part_top_from_base': [("            try{mesh=padMesh(Pp,y0+rg.min,rg.h-rg.min);}", "            try{mesh=padMesh(Pp,y0+rg.min,rg.h);}")],
    'min_level_ignored': [("      if(isFinite(L)&&L>0&&L<300){mn=L*BIM_CTX_LEVEL_H;from='levels';}", "      if(false){mn=L*BIM_CTX_LEVEL_H;from='levels';}")],
    'min_feet_as_metres': [("    if(m[2]&&/^(ft|feet|')$/i.test(m[2]))v*=0.3048;\n    return isFinite(v)?v:null;", "    return isFinite(v)?v:null;")],
    'pair_by_vertex': [("    return best||P[0];", "    return P[0];")],
    'pair_largest': [("            if(ar<ba){ba=ar;best={f:k,r:r};}", "            if(best===null){ba=ar;best={f:k,r:r};}")],
    'stand_own_footprint': [("        fp=o.context.standFp||o.context.footprint||[];h=null;", "        fp=o.context.footprint||[];h=null;")],
    'parts_labelled_12': [("            c.lod=f.part?'1.3':'1.2';   /* __acad3dV139 */", "            c.lod='1.2';")],
    'part_building_lost': [("                c.building={osm:pf.osm,id:pf.id,name:String(pf.tags.name||'').slice(0,60)};", "")],
    'parts_unsaid': [("      (nParts?'; '+nParts+' building part'+(nParts===1?'':'s')+' at their own heights (LOD1.3)':'')+", "")],
    # ---- 139a: LOD labels
    'lod_how_no_base': [("      return {lod:'1.3',how:'an OpenStreetMap building part, from '+(c.minHeight?", "      return {lod:'1.3',how:'an OpenStreetMap building part, from '+(false?")],
    'lod_assumed_unsaid': [("assumed:'an assumed '+BIM_CTX_DEFAULT_H+' m (OSM gives no height or levels)'", "assumed:'its height'")],
    # ---- 139a: the solid check
    'no_weld': [("      var p=m.v[i],kk=Math.round(p[0]/T.snap)+','+Math.round(p[1]/T.snap)+','+Math.round(p[2]/T.snap);", "      var p=m.v[i],kk='v'+i;")],
    'planar_no_tolerance': [("        if(dm>T.planar)bad(203);", "        if(dm>1e-9)bad(203);")],
    'planar_unchecked': [("        if(dm>T.planar)bad(203);", "")],
    'open_unchecked': [("      if(open)err[302]=open;", "")],
    'nonmanifold_unchecked': [("      else if(n>2)nonman++;", "      else if(n>2){}")],
    'orientation_unchecked': [("      else if(e.fw!==1)wrong++;", "")],
    'pieces_unchecked': [("      if(pieces>1)err[305]=pieces;", "")],
    'inside_out_unchecked': [("      if(!open&&!nonman&&!wrong&&F.length>=4&&vol<0)bad(405);", "")],
    'no_area_unchecked': [("      if(nl/2<T.area){bad(105);continue;}", "")],
    'surfaces_asked_to_close': [("    if(!o.surface){\n      if(F.length<4)bad(301);", "    if(true){\n      if(F.length<4)bad(301);")],
    'lodcheck_no_select': [("      A3D.sel=badL[0];A3D.sel2=null;A3D.selSet=[badL[0]];", "")],
    # ---- 139b: UTM
    'utm_no_scale': [("  var BIM_UTM_K0=0.9996;", "  var BIM_UTM_K0=1;")],
    'utm_south_no_false_northing': [("    return [500000+BIM_UTM_K0*S.A*x,(south?10000000:0)+BIM_UTM_K0*S.A*y];", "    return [500000+BIM_UTM_K0*S.A*x,BIM_UTM_K0*S.A*y];")],
    'utm_inverse_series_sign': [("    for(j=1;j<=3;j++)ph+=S.de[j-1]*Math.sin(2*j*chi);", "    for(j=1;j<=3;j++)ph-=S.de[j-1]*Math.sin(2*j*chi);")],
    'utm_zone_off_by_one': [("  function bimUtmZone(lon){return Math.max(1,Math.min(60,Math.floor((lon+180)/6)+1));}", "  function bimUtmZone(lon){return Math.max(1,Math.min(60,Math.floor((lon+180)/6)+2));}")],
    # ---- 139b: out
    'out_no_datum': [("w=[u[0],u[1],p[1]+(datum===null?0:datum)];", "w=[u[0],u[1],p[1]];")],
    'out_no_stand': [("      y0+=q[1];y1+=q[1];\n", "")],
    'out_roof_ground_swapped': [("    if(n[1]>0.99)return 'roof';\n    if(n[1]<-0.99)return 'ground';", "    if(n[1]>0.99)return 'ground';\n    if(n[1]<-0.99)return 'roof';")],
    'out_roof_not_turned': [("      F.push(P.slice().reverse().map(function(p){return [p[0]+q[0],y1,p[1]+q[2]];}));", "      F.push(P.map(function(p){return [p[0]+q[0],y1,p[1]+q[2]];}));")],
    'out_parts_not_children': [("      if(c&&c.buildingPart&&c.building)par={key:", "      if(false)par={key:")],
    'out_lone_part_orphan': [("      else if(c&&c.buildingPart)par={key:'osm-'+c.osm+'-'+c.id,", "      else if(false)par={key:'osm-'+c.osm+'-'+c.id,")],
    'out_no_credit': [("      a.source=c.source;a.credit=c.credit;a.osmType=c.osm;a.osmId=c.id;", "      a.source=c.source;a.osmType=c.osm;a.osmId=c.id;")],
    'out_no_lod_attrs': [("    if(L){a.lod=L.lod;a.lodMethod=L.how;}", "")],
    'out_translate_not_metres': [("    var tr=[mn[0]/1000,mn[1]/1000,mn[2]/1000];", "    var tr=[mn[0],mn[1],mn[2]];")],
    'out_no_semantics': [("{type:'Solid',lod:L.lod||'1',boundaries:[shell],semantics:{surfaces:sur,values:[vals]}}", "{type:'Solid',lod:L.lod||'1',boundaries:[shell]}")],
    # ---- 139b: in
    'in_transform_ignored': [("      var r=d.vertices[i],w=[r[0]*sc[0]+tl[0],r[1]*sc[1]+tl[1],r[2]*sc[2]+tl[2]];", "      var r=d.vertices[i],w=[r[0],r[1],r[2]];")],
    'in_utm_not_read': [("    if(epsg>32600&&epsg<=32660)utm={zone:epsg-32600,south:false};", "    if(false)utm={zone:epsg-32600,south:false};")],
    'in_heights_from_lowest': [("      var z0=(utm&&datum!==null)?datum:mn[2];", "      var z0=mn[2];")],
    'in_lowest_lod': [("        if(l>bl){bl=l;best=g;}", "        if(bl<0||l<bl){bl=l;best=g;}")],
    'in_concave_fanned': [("    if(conv)return [ring];\n", "    return [ring];\n")],
    'in_split_turned': [("      return [ring[N-1-tr[2]],ring[N-1-tr[1]],ring[N-1-tr[0]]];", "      return [ring[N-1-tr[0]],ring[N-1-tr[1]],ring[N-1-tr[2]]];")],
    'in_holes_unsaid': [("      (holes?'; '+holes+' opening'+(holes===1?'':'s')+' in faces filled':'')+", "")],
    'in_grid_unsaid': [("      (local?'; '+(epsg?'EPSG:'+epsg+' is not a grid this app converts':'it names no grid')+': placed by its centre at model 0,0, heights from its lowest point':'')+", "")],
    'in_parent_lost': [("        if(par){o.cityjson.parent=String(par).slice(0,120);", "        if(false){o.cityjson.parent=String(par).slice(0,120);")],
    'in_not_undoable': [("    pushUndo();\n    undoSuspend=true;\n    var out=[],nOk=0,nBad=0,lods={},types={};", "    undoSuspend=true;\n    var out=[],nOk=0,nBad=0,lods={},types={};")],
    'in_unchecked': [("        var chk=bimSolidCheck(o.mesh,{surface:surf});\n        if(chk.valid)nOk++;else nBad++;", "        nOk++;")],
    'in_file_not_routed': [("    }else if(ext==='cityjson'||(ext==='json'&&/\\.city\\.json$/i.test(name))){   /* __acad3dV139 */", "    }else if(false){")],
    'in_refuses_nothing': [("    if(!d||d.type!=='CityJSON'||!d.CityObjects||!d.vertices){", "    if(!d){")],
    # ---- 139c
    'no_lod_group': [("    if(bimLodOf(o))h+=bimPropGroup('LOD',bimLodHtml(o));   /* __acad3dV139 */\n", "")],
    'lod_group_no_solid': [("    if(chk)r+='<div class=\"a3d-prow a3d-svrow\" data-lodrow=\"solid\">", "    if(false)r+='<div class=\"a3d-prow a3d-svrow\" data-lodrow=\"solid\">")],
    'buttons_dead': [("    if(a==='lodcheck'){bimLodCheck();return true;}       /* __acad3dV139 */", "")],
    'export_button_dead': [("    if(a==='cjout'){bimCityJsonExport();return true;}", "")],
    'import_button_dead': [("    if(a==='cjin'){bimCityJsonPick();return true;}", "")],
    'no_commands': [("    lodcheck:function(){bimLodCheck();},              /* __acad3dV139 */\n", "")],
    'no_search_words': [("    LODCHECK:'lod level of detail validate valid solid closed watertight val3dity buildings check citygml',   /* __acad3dV139 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV139' in txt
out.write_text(txt, encoding='utf-8')
