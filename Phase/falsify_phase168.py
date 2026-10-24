"""falsify_phase168.py -- break the V168 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase168_land_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the standards ----
    'rec_lbcs_colour': [("[3000,'Industrial, manufacturing, and waste-related','A020F0']", "[3000,'Industrial, manufacturing, and waste-related','A0F020']")],   # LBCS's families
    'rec_lbcs_adopted': [("where:'A model classification for planning in the United States, adopted nowhere as a rule',adopt:[],", "where:'A model classification for planning in the United States, adopted nowhere as a rule',adopt:[{at:'*'}],")],   # outside its place
    'rec_trees': [("v:[{n:'trees',v:3,u:'trees'", "v:[{n:'trees',v:4,u:'trees'")],   # 3-30-300's values
    'rec_green_min': [("{n:'green_min',v:0.5,u:'ha'", "{n:'green_min',v:1,u:'ha'")],   # 3-30-300's values
    'rec_hood': [("v:[{n:'hood',v:500,u:'m'", "v:[{n:'hood',v:400,u:'m'")],   # the app's land settings
    'rec_mix_n': [("{n:'mix_n',v:8,u:'families'", "{n:'mix_n',v:9,u:'families'")],   # the app's land settings
    'rec_land_level': [("w:'research-site-analysis-in-model.md, section 6',lv:'A'},\n        v:[{n:'hood'", "w:'research-site-analysis-in-model.md, section 6',lv:'P'},\n        v:[{n:'hood'")],   # the app's own assumption (A)
    'xw_hotel': [("'tourism=hotel':1000,", "'tourism=hotel':2000,")],   # the crosswalk in the registry; the hotel's cell
    'xw_port': [("'industrial=port':5000,", "'industrial=port':3000,")],   # the port's cell
    'area_missing': [("'Site context','Land and green','Assets','Climate'];", "'Site context','Assets','Climate'];")],   # Properties, Site, Standards; RE-ANCHORED IN V169
    'unit_ha': [("ha:[' ha',' ha'],trees:", "ha:[' hectare',' hectares'],trees:")],   # the new units in words
    # ---- 2. the context ----
    'query_no_amenity': [("'way[\"amenity\"~\"^('+BIM_CTX_LAND_AREAS.amenity+')$\"]'+b+';',", "")],   # the grounds of amenities
    'query_old_landuse': [("'education|institutional|civic_admin|religious|churchyard|cemetery|military|garages|landfill|brownfield|greenfield|farmland|field|farmyard|orchard|vineyard|allotments|plant_nursery|greenhouse_horticulture|aquaculture|quarry|port|school|flowerbed';",
                           "'education';")],   # every land use value
    'kind_amenity_none': [("    if(['amenity','leisure','tourism'].some(function(k2){return t[k2]&&new RegExp('^('+BIM_CTX_LAND_AREAS[k2]+')$').test(t[k2]);}))return 'landuse';", "")],   # a school's grounds land use
    'holes_dropped': [("c.holes=f.inner.map(function(r){return r.map(function(p){return [p[0],p[1]];});});}", "}")],   # Court House keeps its courtyard
    # ---- 3. the crosswalk ----
    'bkeys_building_first': [("  var BIM_LD_BKEYS=['amenity','shop','office','tourism','leisure','social_facility','building',", "  var BIM_LD_BKEYS=['building','amenity','shop','office','tourism','leisure','social_facility',")],   # a building's amenity before its shop; the hotel
    'akeys_landuse_first': [("  var BIM_LD_AKEYS=['industrial','amenity','leisure','tourism','aeroway','landuse',", "  var BIM_LD_AKEYS=['landuse','industrial','amenity','leisure','tourism','aeroway',")],   # the port before industrial
    'no_values_skipped': [("      if(v===undefined||v===null||v===''||v==='no')continue;\n      v=String(v);\n      if(T.hasOwnProperty(k+'='+v))", "      if(v===undefined||v===null||v==='')continue;\n      v=String(v);\n      if(T.hasOwnProperty(k+'='+v))")],   # shop=no
    'wildcard_ignored': [("      if(T.hasOwnProperty(k+'=*'))return {c:+T[k+'=*'],tag:k+'='+v,weak:false};\n", "")],   # shop=* : the bakery
    # ---- 4. land use ----
    'weak_ignored': [("return {c:+T[k+'='+v],tag:k+'='+v,weak:W.indexOf(k+'='+v)>=0};", "return {c:+T[k+'='+v],tag:k+'='+v,weak:false};")],   # grass in homes
    'largest_wins': [("r=tier*1e12+area,ii,jj;", "r=tier*1e12-area,ii,jj;")],   # a school in homes
    'building_not_first': [("lay(b.cls.c,0,b.area,function(x,z){if(!bimPointInPoly([x,z],b.fp))", "lay(b.cls.c,1,b.area,function(x,z){if(!bimPointInPoly([x,z],b.fp))")],   # the supermarket over the car park
    'courtyard_used': [("lay(b.cls.c,0,b.area,function(x,z){if(!bimPointInPoly([x,z],b.fp))return false;for(var h=0;h<b.holes.length;h++)if(bimPointInPoly([x,z],b.holes[h]))return false;return true;}",
                        "lay(b.cls.c,0,b.area,function(x,z){return bimPointInPoly([x,z],b.fp);}")],   # the courtyard's cell
    'area_holes_ignored': [("    if(!inn)return false;\n    for(i=0;i<a.holes.length;i++)if(bimPointInPoly([x,z],a.holes[i]))return false;\n    return true;", "    return inn;")],   # homes round a hole
    'mix_with_none': [("else if(c===9000)none++;else{cnt[c]=(cnt[c]||0)+1;n++;}", "else{cnt[c]=(cnt[c]||0)+1;n++;}")],   # every cell's family; H
    'mix_n_present': [("sh.forEach(function(x){H-=x.p*Math.log(x.p);});\n    return {sh:sh,n:n,tot:tot,none:none,un:un,H:H,N:N,ix:(N>=2&&n)?H/Math.log(N):null};",
                       "sh.forEach(function(x){H-=x.p*Math.log(x.p);});N=sh.length;\n    return {sh:sh,n:n,tot:tot,none:none,un:un,H:H,N:N,ix:(N>=2&&n)?H/Math.log(N):null};")],   # the mix over 4 families
    'dark_as_light': [("function bimLdCol(c){var F=bimLdFam(c);return bimMvLight()?F.lt:F.dk;}", "function bimLdCol(c){var F=bimLdFam(c);return F.lt;}")],   # the dark plan's steps
    'no_outline': [("        s:{stroke:C.o,w:1,fop:0.55},lb:a.area>=BIM_LD_LABEL?", "        s:{w:1,fop:0.55},lb:a.area>=BIM_LD_LABEL?")],   # every area outlined
    'labels_all': [("lb:a.area>=BIM_LD_LABEL?[{t:F.short,", "lb:a.area>=0?[{t:F.short,")],   # named when 2000 m2 or more
    'tex_unset': [("bands:[{lv:a.cls.weak?-1e12:-a.area,col:C.f,rings:rings,tex:F.tex||null,ink:C.i||null}]", "bands:[{lv:a.cls.weak?-1e12:-a.area,col:C.f,rings:rings,ink:C.i||null}]")],   # the textures
    'tex_not_drawn': [("      if(T[i].tex){var tp=bimDgTex(c2,T[i].tex,T[i].ink);if(tp){c2.fillStyle=tp;c2.fill(T[i].eo?'evenodd':'nonzero');}}", "")],   # the hatch on the plan
    'tex_css_missing': [("      if(r.tex)st+=';'+bimDgTexCss(r.tex,r.ink);", "")],   # the row's key
    'key_eight': [("rows:(R.legend||[]).slice(0,9),", "rows:(R.legend||[]).slice(0,8),")],   # the key on the view: nine
    'lids_not_filled': [("        if(s.fillOver&&g.closed&&lp.length>2){", "        if(false){")],   # Office Five filled dark
    'lid_on_ground': [("lines:L.map(function(b){return R3(b.fp,y+b.h);})", "lines:L.map(function(b){return R3(b.fp,y);})")],   # a lid at its height
    'buildings_no_use': [("    B.forEach(function(b){if(b.cls&&b.ground&&bimLdMeets([b.fp],W))(G[b.cls.c]||(G[b.cls.c]=[])).push(b);});", "")],   # the buildings with a use
    # ---- 5. figure-ground ----
    'levels_ignored': [("if(isFinite(lv)&&lv>0&&lv<300){sn=", "if(false){sn=")],   # Office Five's storeys
    'storeys_none': [("else{sn=Math.max(1,Math.floor((h-mn)/st+1e-9));from='height';}", "else{sn=Math.max(0,Math.floor((h-mn)/st+1e-9));from='height';}")],   # the kiosk
    'min_level_ignored': [("sn=Math.max(0,lv-(isFinite(ml)&&ml>0?ml:0));from='levels';", "sn=lv;from='levels';")],   # Part House's parts
    'part_on_ground': [("B.push({id:o.id,name:o.name,t:t,fp:fp,holes:holes,ground:!(mn>0),", "B.push({id:o.id,name:o.name,t:t,fp:fp,holes:holes,ground:true,")],   # Part House's parts
    'courtyard_built': [("var ar=bimPolyArea(fp);holes.forEach(function(r){ar-=bimPolyArea(r);});", "var ar=bimPolyArea(fp);")],   # Court House 2700 m2
    'unclipped': [("    var R=bimLdClip(b.fp,x0,z0,x1,z1),a=R.length>=3?bimPolyArea(R):0;", "    var R=b.fp,a=bimLdMeets([b.fp],{x0:x0,z0:z0,x1:x1,z1:z1})?bimPolyArea(R):0;")],   # the cells
    'osr_inverted': [("osr:fsi>0?(1-gsi)/fsi:null,", "osr:gsi>0?(1-fsi)/gsi:null,")],   # Spacematrix for the square
    'l_over_land': [("l:gf>0?fa/gf:null,n:n};", "l:gf>0?fa/A:null,n:n};")],   # Spacematrix for the square
    'grain_parts_twice': [("      if(!seen[b.whole]){seen[b.whole]=1;n++;}", "      n++;")],   # the grain: Part House once
    'yards_unsaid': [("yards:!!(c.courtyards&&!c.holes)});", "yards:false});")],   # a building fetched before V168
    'type_claimed': [("rw.push(['Spacematrix\\'s type','not given: the bounds of its types are in the book, which was not read']);", "rw.push(['Spacematrix\\'s type','mid-rise block']);")],   # not given
    # ---- 6. green and trees ----
    'canopy_unclipped': [("      if(re&&(x<re.x0||x>re.x1||z<re.z0||z>re.z1))continue;\n      cnt++;", "      cnt++;")],   # the canopy, cut to the context
    'canopy_no_woods': [("    woods.forEach(function(a){\n      var b=bimLdBox(a.outer),I=span(b[0],b[2],gx0)", "    [].forEach(function(a){\n      var b=bimLdBox(a.outer),I=span(b[0],b[2],gx0)")],   # the canopy
    'canopy_coarse': [("    var R=bimStd('app.land','hood'),rc=BIM_LD_RCC,re=bimLdReach()", "    var R=bimStd('app.land','hood'),rc=BIM_LD_RC,re=bimLdReach()")],   # the canopy's 2 m grid
    'canopy_crown_diameter': [("T.push({id:o.id,x:o.pts[0][0]+q[0],z:o.pts[0][1]+q[2],r:Math.max(0.5,(+c.crown||h*0.6)/2),", "T.push({id:o.id,x:o.pts[0][0]+q[0],z:o.pts[0][1]+q[2],r:Math.max(0.5,(+c.crown||h*0.6)),")],   # the canopy
    'seen_shown_only': [("iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(true),see)", "iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(),see)")],   # trees seen, their layer hidden
    'seen_far': [("iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(true),see)", "iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(true),400)")],   # the tree 172 m off
    'seen_through': [("iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(true),see)", "iv=bimDgIsovist(S,S.y+1.6,bimDgObstacles(true).filter(function(b){return b.kind==='t';}),see)")],   # the tree behind East Hall
    'private_counted': [("t.landuse==='village_green')&&!/^(private|no)$/.test(String(t.access||''));})", "t.landuse==='village_green');})")],   # the private park left out
    'small_counted': [("a.big=a.area>=m2-0.001;", "a.big=true;")],   # Small Garden under 0.5 ha
    'edge_strict': [("a.big=a.area>=m2-0.001;", "a.big=a.area>=m2;")],   # the garden counts at 0.49 ha
    'walk_crow': [("if(d<=r&&d<bd){bd=d;bt=p[2]+u*(p[5]-p[2]);}", "if(d<=r&&d<bd){bd=d;bt=0;}")],   # the walks along the streets
    'walk_vertices_only': [("      if(bt!==null)take(bt*v+bd,[x,z]);", "")],   # the walks along the streets
    'walk_minutes': [("if(bt!==null)take(bt*v+bd,[x,z]);", "if(bt!==null)take(bt+bd,[x,z]);")],   # the walks in metres
    'ok3_strict': [("ok3:seen.n>=bimStd('green.33300','trees')", "ok3:seen.n>bimStd('green.33300','trees')")],   # the edge: as many asked as seen
    'ok30_inverted': [("ok30:can.share!==null&&can.share*100>=bimStd('green.33300','canopy')", "ok30:can.share!==null&&can.share*100<=bimStd('green.33300','canopy')")],   # 3-30-300
    'ok300_always': [("ok300:!!best&&best.d<=bimStd('green.33300','walk')", "ok300:!!best")],   # the walk overridden to 200 m
    # ---- 7. zoning around ----
    'zn_no_transparency': [("var a=(c.length>3?+c[3]:255)/255*(1-(+tr||0)/100);", "var a=(c.length>3?+c[3]:255)/255;")],   # its renderer read
    'zn_null_outline': [("o:(sy.outline&&sy.outline.style!=='esriSLSNull')?bimZnRgba(sy.outline.color,tr):null", "o:sy.outline?bimZnRgba(sy.outline.color,tr):null")],   # its renderer read
    'zn_hatch_filled': [("{f:(sy.type==='esriSFS'&&(!sy.style||sy.style==='esriSFSSolid'))?bimZnRgba(sy.color,tr):null,", "{f:bimZnRgba(sy.color,tr),")],   # its renderer read
    'zn_no_default': [("      if(ds)out.def=[String(r.defaultLabel||'Other').slice(0,80),ds.f,ds.o];\n", "")],   # its renderer read
    'zn_strict': [("for(i=0;i<D.v.length;i++)if(D.v[i][0]==key)return", "for(i=0;i<D.v.length;i++)if(D.v[i][0]===key&&typeof D.v[i][0]===typeof p[D.f[0]])return")],   # a number matched loosely
    'zn_field2_ignored': [("out.f=[r.field1,r.field2,r.field3].filter(", "out.f=[r.field1].filter(")],   # two fields joined
    'zn_asked_each_run': [("var L=bimDataList().filter(function(x){return x&&x.kind==='arcgis'&&!x.drawing;}).slice(0,3);", "var L=bimDataList().filter(function(x){return x&&x.kind==='arcgis';}).slice(0,3);")],   # asked once
    'zn_never_asked': [("      return Promise.all([pc,pk,pl]).then(function(){return bimZnDrawingFetch();}).then(function(){", "      return Promise.all([pc,pk,pl]).then(function(){return 0;}).then(function(){")],   # its renderer read
    'zn_failure_silent': [("          a3dToast(x.name+': its own colours could not be read ('+bimCtxErr(bimMapHost(u),e)+'); its districts are drawn in the app\\'s');\n", "")],   # the failure named
    'zn_lot_lost': [("      if(inn&&!lot)lot=val;", "")],   # the site in R6
    'zn_shares_whole': [("ft.rings.forEach(function(r){var Q=bimLdClip(r.pts,W.x0,W.z0,W.x1,W.z1);if(Q.length>=3)aw+=(r.hole?-1:1)*bimPolyArea(Q);});", "ft.rings.forEach(function(r){aw+=(r.hole?-1:1)*bimPolyArea(r.pts);});")],   # the shares
    'zn_lot_not_heavier': [("s:{stroke:x.sy&&x.sy.o?x.sy.o:(light?'#4b5563':'#c8ccd0'),w:x.inn?2.2:1.1,", "s:{stroke:x.sy&&x.sy.o?x.sy.o:(light?'#4b5563':'#c8ccd0'),w:1.1,")],   # R6 heavier
    'zn_none_full': [("w:x.inn?2.2:1.1,fop:Z.D?0.6:0.18},", "w:x.inn?2.2:1.1,fop:0.6},")],   # a layer with no renderer
    # ---- 8. findings and rows ----
    'finding_landuse_lost': [("        A.push({auto:'location.landuse',cat:'location',title:'Land use mix',", "        A.push({auto:'location.landuse_',cat:'location',title:'Land use mix',")],   # the land use finding
    'finding_33300_cat': [("        A.push({auto:'ecology.33300',cat:'ecology',title:'3-30-300',", "        A.push({auto:'ecology.33300',cat:'location',title:'3-30-300',")],   # the 3-30-300 finding
    'finding_zoning_lost': [("      if(Z&&Z.order.length)A.push({auto:'legal.zoningaround',", "      if(false)A.push({auto:'legal.zoningaround',")],   # the zoning around
    'finding_std_lost': [("'ecology.33300':['green.33300','app.land'],'legal.zoningaround':['app.land']};", "'legal.zoningaround':['app.land']};")],   # each finding names its standards
    'run_unstamped': [("green:['green.33300','app.land'],zoning:['app.land']};", "zoning:['app.land']};")],   # the green layer out of date
    'row_misplaced': [("BIM_ANZ_GROUP_OF.dggreen='ecology';", "BIM_ANZ_GROUP_OF.dggreen='location';")],   # the rows in their categories
    'landuse_shown': [("    {id:'landuse',name:'Land use',col:'#eda100',hidden:true},", "    {id:'landuse',name:'Land use',col:'#eda100'},")],   # start hidden
    'version_old': [("var BIM_APP_VERSION={v:'V169',date:'2026-10-19'};", "var BIM_APP_VERSION={v:'V167',date:'2026-10-18'};")],   # V168 or later; RE-ANCHORED IN V169
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV168' in txt
out.write_text(txt, encoding='utf-8')
