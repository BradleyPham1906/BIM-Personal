"""falsify_phase161.py -- break the V161 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # who may walk where
    'motorway_walked': [("  var BIM_ACC_CLS={trunk:'a',", "  var BIM_ACC_CLS={motorway:'a',trunk:'a',")],
    'private_walked': [("    if(/^(no|private)$/.test(tg.access||'')&&!/^(yes|designated|permissive|destination)$/.test(f))return '';\n", "")],
    'foot_yes_ignored': [("    if(/^(no|private)$/.test(tg.access||'')&&!/^(yes|designated|permissive|destination)$/.test(f))return '';", "    if(/^(no|private)$/.test(tg.access||''))return '';")],
    'steps_not_slowed': [("m:e.tags.highway==='steps'?BIM_ACC_STEPS:1,lev:lev", "m:1,lev:lev")],
    'sidewalks_not_walked': [("    if(c==='p'&&/^(sidewalk|crossing|traffic_island)$/.test(tg.footway||tg.path||tg.cycleway||''))return 'w';", "    if(c==='p'&&/^(sidewalk|crossing|traffic_island)$/.test(tg.footway||tg.path||tg.cycleway||''))return '';")],
    # where the walk starts
    'bridges_seeded': [("    W.forEach(function(w){\n      if(w.lev)return;\n      var out=[w.ns[0]],j;", "    W.forEach(function(w){\n      var out=[w.ns[0]],j;")],
    'no_frontage_cuts': [("          bimAccCuts(L,ax,az,bx,bz).forEach(function(t){out.push(N.x.length);N.x.push(ax+t*(bx-ax));N.z.push(az+t*(bz-az));N.g.push(1);});\n", "")],
    'seed_cost_zero': [("      if(d0<=BIM_ACC_FRONT){seeds.push([i,d0/v]);if(d0<near)near=d0;}", "      if(d0<=BIM_ACC_FRONT){seeds.push([i,0]);if(d0<near)near=d0;}")],
    'no_exact_step': [("    if(net.L&&!net.W[net.E.w[sn.e]].lev){dl=bimAccLotDist(net.L,sn.x,sn.z);if(dl<=BIM_ACC_FRONT)t=Math.min(t,dl/BIM_ACC_SPEED);}\n", "")],
    'far_start_missing': [("    var far=!seeds.length;", "    var far=false;")],
    # the walk
    'dijkstra_no_relax': [("for(e=head[u];e>=0;e=nxt[e]){var nt=t+cost[e],w=to[e];if(nt<D[w]){D[w]=nt;push(nt,w);}}", "for(e=head[u];e>=0;e=nxt[e]){var nt=t+cost[e],w=to[e];if(nt<D[w]){D[w]=nt;}}")],
    'one_way_edges': [("      to[k]=E.a[i];cost[k]=c;nxt[k]=head[E.b[i]];head[E.b[i]]=k;k++;\n", "")],
    'peak_dropped': [("      if(c>0&&isFinite(s)&&s>1e-6&&s<c-1e-6){var f=s/c;P.push([ax+f*(bx-ax),az+f*(bz-az),ta+s]);}\n", "")],
    'runs_not_cut': [("      bimAccRuns(bimAccWayLine(net,D,wi),MAXT).forEach(function(run){", "      [bimAccWayLine(net,D,wi)].forEach(function(run){")],
    'dp_too_coarse': [("        bimAccDP(run,0.75).forEach(function(p){", "        bimAccDP(run,40).forEach(function(p){")],
    'sidewalks_drawn': [("    W.forEach(function(w,wi){\n      if(w.c==='w')return;", "    W.forEach(function(w,wi){")],
    'band_from_one_end': [("    var a=ta<=T?Math.min(len,(T-ta)/c*len):0,b=tb<=T?Math.min(len,(T-tb)/c*len):0;", "    var a=ta<=T?Math.min(len,(T-ta)/c*len):0,b=0;")],
    # places
    'park_to_centre': [("      if(kd.sub==='park')rr=bimAccParkTime(net,D,e,org);", "      if(false)rr=bimAccParkTime(net,D,e,org);")],
    'private_park_counted': [("      if(kd.k==='parks'&&/^(private|no)$/.test(e.tags.access||''))continue;\n", "")],
    'park_hole_kept': [("      if(cl&&P.length>3)area+=(L.outer?1:-1)*bimPolyArea(P);", "      if(cl&&P.length>3)area+=bimPolyArea(P);")],
    'far_places_kept': [("      if(!rr||rr.t>MAXT)continue;\n      nPl++;", "      if(!rr)continue;\n      nPl++;")],
    'counts_cumulative_wrong': [("L2.forEach(function(p){if(p.t<=5)cnt[0]++;if(p.t<=10)cnt[1]++;if(p.t<=15)cnt[2]++;cnt[3]++;});", "L2.forEach(function(p){if(p.t<=5)cnt[0]++;else if(p.t<=10)cnt[1]++;else if(p.t<=15)cnt[2]++;cnt[3]++;});")],
    # stops and lines
    'stops_not_grouped': [("      groups.forEach(function(G2){if(!g&&G2.key===kk&&dist(G2,s)<=300)g=G2;});", "")],
    'entrances_not_joined': [("if(((rail&&(G2.ms.metro||G2.ms.light||G2.ms.rail)&&dd<=300)||dd<=40)&&dd<best)", "if((dd<=40)&&dd<best)")],
    'lines_by_name': [("lab=String(e.tags.ref||e.tags.name||'')", "lab=String(e.tags.name||e.tags.ref||'')")],
    'entrance_not_rail': [("    if(tg.railway==='subway_entrance')return 'metro';", "    if(tg.railway==='subway_entrance')return 'bus';")],
    # the frontage
    'normal_flipped': [("      var nx=(sa>0?dz:-dz)/len,nz=(sa>0?-dx:dx)/len,m=Math.max(1,Math.round(len)),st=len/m;", "      var nx=(sa>0?-dz:dz)/len,nz=(sa>0?dx:-dx)/len,m=Math.max(1,Math.round(len)),st=len/m;")],
    'sidewalk_not_inferred': [("(o.side>=o.cnt*0.3?'separate':'')", "''")],
    'frontage_tied_alley_first': [("    out.sort(function(a,b){return b.len-a.len||BIM_ACC_RANK[b.c]-BIM_ACC_RANK[a.c];});", "    out.sort(function(a,b){return b.len-a.len||BIM_ACC_RANK[a.c]-BIM_ACC_RANK[b.c];});")],
    # connectivity
    'deadends_kept': [("    for(i=0;i<n;i++)if(deg[i]===1)Q.push(i);\n    while(Q.length){", "    while(Q.length){")],
    'prune_once': [("      deg[v]--;\n      if(deg[v]===1)Q.push(v);", "      deg[v]--;")],
    'divided_not_merged': [("BIM_ACC_IXR=400,BIM_ACC_IXMERGE=12,", "BIM_ACC_IXR=400,BIM_ACC_IXMERGE=1,")],
    'service_counted': [("      var w=W[E.w[e]],on=/^[aclp]$/.test(w.c)&&w.t.area!=='yes';", "      var w=W[E.w[e]],on=/^[aclps]$/.test(w.c)&&w.t.area!=='yes';")],
    'buffer_area_no_perimeter': [("    var area=(L.ring?bimPolyArea(L.ring)+bimAccPerim(L.ring)*R:0)+Math.PI*R*R,km2=area/1e6;", "    var area=(L.ring?bimPolyArea(L.ring):0)+Math.PI*R*R,km2=area/1e6;")],
    'sqmi_factor_wrong': [("sqmi:bimAccR1(pts.length/km2*2.589988)", "sqmi:bimAccR1(pts.length/km2*1.609344)")],
    'directness_mean': [("    conn.dir=rat.length>=5?bimAccR2(rat.length%2?rat[(rat.length-1)/2]:(rat[rat.length/2-1]+rat[rat.length/2])/2):null;",
                         "    conn.dir=rat.length>=5?bimAccR2(rat.reduce(function(a,b){return a+b;},0)/rat.length):null;")],
    # the people
    'moe_plus_always': [("    r=X[1]*X[1]-p*p*Y[1]*Y[1];\n    if(r<0)r=X[1]*X[1]+p*p*Y[1]*Y[1];", "    r=X[1]*X[1]+p*p*Y[1]*Y[1];")],
    'moe_no_ratio_fallback': [("    if(r<0)r=X[1]*X[1]+p*p*Y[1]*Y[1];\n    return [p,Math.sqrt(r)/Y[0]];", "    return [p,Math.sqrt(Math.abs(r))/Y[0]];")],
    'controlled_moe_unknown': [("  function bimCenM(v){var n=bimCenNum(v);return n===-555555555?0:(n===null||n<0?null:n);}", "  function bimCenM(v){var n=bimCenNum(v);return n===null||n<0?null:n;}")],
    'sentinel_kept': [("  function bimCenE(v){var n=bimCenNum(v);return n===null||n<0?null:n;}", "  function bimCenE(v){var n=bimCenNum(v);return n;}")],
    'year_no_fallback': [("      if(!r0.ok&&r0.http&&!again)return bimCenAcs(y-1,G,true);\n", "")],
    'year_last_year': [("  function bimCenYear(){var d=new Date();return d.getFullYear()-(d.getMonth()===11?1:2);}", "  function bimCenYear(){var d=new Date();return d.getFullYear()-1;}")],
    'pyramid_women_offset': [("c=bimCenE(row['B01001_'+bimCen3(i+24)+'E'])", "c=bimCenE(row['B01001_'+bimCen3(i+23)+'E'])")],
    'blocks_as_tract': [("tr=R[0].ok?bimCenIdent(R[0].js,/tract/i,/block/i):null", "tr=R[0].ok?bimCenIdent(R[0].js,/tract|block/i):null")],
    'outside_asked': [("    if(!bimCenInUS(lat,lon))return Promise.resolve({outside:true,errors:[]});\n", "")],
    # the findings and the undo
    'transit_never_opportunity': [("      if((nb&&nb.t<=5)||(nr&&nr.t<=10))cl='opportunity';", "      if(false)cl='opportunity';")],
    'arterial_frontage_fine': [("          cls:fs.some(function(f){return f.c==='a';})?'constraint':'neutral',sev:1,source:S.src,date:dt});", "          cls:'neutral',sev:1,source:S.src,date:dt});")],
    'fetch_not_undoable': [("    if(!A&&!P){a3dToast('No access or people data: '+bad.join('; '));return {error:bad.join('; ')};}\n    pushUndo();", "    if(!A&&!P){a3dToast('No access or people data: '+bad.join('; '));return {error:bad.join('; ')};}")],
    'findings_not_filled': [("      if(A&&!bimResLayers().some(function(R){return R.kind==='walk';}))bimResultLayerAdd('walk',{quiet:true});\n      bimSaFill(true);", "      if(A&&!bimResLayers().some(function(R){return R.kind==='walk';}))bimResultLayerAdd('walk',{quiet:true});")],
    'failure_wipes': [("    else bad=bad.concat(osm&&osm.msgs&&osm.msgs.length?osm.msgs:['no Overpass server answered']);", "    else{bad=bad.concat(osm&&osm.msgs&&osm.msgs.length?osm.msgs:['no Overpass server answered']);if(A3D.site)delete A3D.site.access;}")],
    # the layer
    'layer_each_fetch': [("      if(A&&!bimResLayers().some(function(R){return R.kind==='walk';}))bimResultLayerAdd('walk',{quiet:true});", "      if(A)bimResultLayerAdd('walk',{quiet:true,again:true});"),
                         ("      if(bimResLayers().some(function(x){return x.kind==='walk';})){a3dToast(", "      if(!opts.again&&bimResLayers().some(function(x){return x.kind==='walk';})){a3dToast(")],
    'layer_not_drawn': [("    if(R.kind==='walk')return bimResGone(R)?false:bimAccDrawPlan(ctx,V,W,H,op);   /* __acad3dV161 */", "    if(R.kind==='walk')return false;")],
    'layer_has_update': [("      (R.kind!=='terrain'&&R.kind!=='walk'?'<button type=\"button\" data-lyresupd=", "      (R.kind!=='terrain'?'<button type=\"button\" data-lyresupd=")],
    'layer_not_read_back': [("      if(R.kind==='walk')return R.src==='access';   /* __acad3dV161 */", "      if(R.kind==='walk')return false;")],
    # the board
    'board_kind_ignored': [("    if(kind==='climate'||kind==='zoning'||kind==='access')A3D_CLB.kind=kind;", "    if(kind==='climate'||kind==='zoning')A3D_CLB.kind=kind;")],
    'board_refresh_climate': [("      else if(a==='refresh'){if(A3D_CLB.kind==='access')bimAccFetch();else bimClimFetch();}", "      else if(a==='refresh')bimClimFetch();")],
    'map_wide_on_phone': [("    var nw=A3D_CLB.narrow,W=nw?360:760,H=nw?380:560,", "    var nw=A3D_CLB.narrow,W=760,H=nw?380:560,")],
    'no_crow_circles': [("    [400,800].forEach(function(r){var rp=bimClbF(r*F.k);", "    [].forEach(function(r){var rp=bimClbF(r*F.k);")],
    'frontage_table_gone': [("        bimClbLeg([['var(--ink2)','Arterial, collector, local (by weight)','ln'],['var(--muted)','Service road or path','ln'],['var(--s4)','Frontage'],['var(--s1)','Intersection counted']])+bimAccFrontTable(S)+",
                             "        bimClbLeg([['var(--ink2)','Arterial, collector, local (by weight)','ln'],['var(--muted)','Service road or path','ln'],['var(--s4)','Frontage'],['var(--s1)','Intersection counted']])+")],
    'commute_cycled': [("fill=\"var(--s'+(j+1)+')\" stroke=\"var(--surf)\" stroke-width=\"2\"'+", "fill=\"var(--s'+(j%4+1)+')\" stroke=\"var(--surf)\" stroke-width=\"2\"'+")],
    'pyramid_no_county': [("    if(C){\n      var pm='',pf='';", "    if(false){\n      var pm='',pf='';")],
    'no_moe_bar': [("        if(T[1]!==null)s+='<line x1=\"'+x(Math.max(lo,T[0]-T[1]))+'\"", "        if(false)s+='<line x1=\"'+x(Math.max(lo,T[0]-T[1]))+'\"")],
    'stale_unsaid': [("    if(S.lot&&S.lot.key!==bimAccLotKey(bimAccLot()))return 'The lot has changed since: refresh to walk from it.';\n", "")],
    'no_access_keywords': [("    ACCESS:'access people board walk times walkability daily needs 15-minute city amenities transit lines stops street hierarchy frontage intersection density connectivity demographics census age pyramid income households commute vehicles',   /* __acad3dV161 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV161' in txt
out.write_text(txt, encoding='utf-8')
