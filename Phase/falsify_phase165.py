"""falsify_phase165.py -- break the V165 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the engine: rings, groups, lines, the pick, the key ----
    'rings_nonzero': [("c2.fill(T[i].eo?'evenodd':'nonzero');", "c2.fill('nonzero');")],
    'bands_one_group': [("    for(i=0;i<order.length;i++)bimDgDrawBandGroup(ctx,V,W,H,G[order[i]]);\n", "    bimDgDrawBandGroup(ctx,V,W,H,L);\n")],
    'fill_not_followed': [("col:(B.rings&&s.fill)?s.fill:B.col", "col:B.col")],
    'seam_unstroked': [("if(T[i].eo){c2.strokeStyle=T[i].col;", "if(false){c2.strokeStyle=T[i].col;")],
    'band_unpicked': [("      var bpk=(o||gpk)?null:bimPickBand(xy[0],xy[1]);\n", "      var bpk=null;\n")],
    'band_over_model': [("    var o=pick(xy[0],xy[1]);\n    if(ev.ctrlKey||ev.metaKey){", "    var o=bimPickBand(xy[0],xy[1])||pick(xy[0],xy[1]);\n    if(ev.ctrlKey||ev.metaKey){")],
    'band_pick_bottom_first': [("    for(i=order.length-1;i>=0;i--){\n      var T=G[order[i]].slice()", "    for(i=0;i<order.length;i++){\n      var T=G[order[i]].slice()")],
    'band_pick_hidden': [("      if(!gb||!gb.length||!bimLayerShown(o)||!bimLayerPickable(o))continue;", "      if(!gb||!gb.length)continue;")],
    'selected_band_unlit': [("    if(sel&&g.bands){   /* __acad3dV165", "    if(false&&sel&&g.bands){   /* __acad3dV165")],
    'lines_unpicked': [("        for(i=0;i+1<lp.length;i++)if(lp[i][2]>0.5&&lp[i+1][2]>0.5)hit.segs.push([lp[i][0],lp[i][1],lp[i+1][0],lp[i+1][1]]);\n", "")],
    'lines_undrawn': [("        if(s.stroke){bimDgPath(ctx,lp,g.closed);", "        if(false){bimDgPath(ctx,lp,g.closed);")],
    'turn_skips_rings': [("if(B.rings)B.rings=B.rings.map(function(Rg){return Rg.map(P);});", "")],
    'turn_skips_lines': [("    if(g.lines)g.lines=g.lines.map(function(Ln){return Ln.map(P);});\n", "")],
    'bounds_skip_rings': [("(B.rings||[]).forEach(function(Rg){Rg.forEach(function(p){P.push(p);});});", "")],
    'bounds_skip_lines': [("    (g.lines||[]).forEach(function(Ln){Ln.forEach(function(p){P.push(p);});});\n", "")],
    'cover_shown': [("'root',!!A.hidden);", "'root',false);")],
    'legend_overflows': [("      while(LY.h>avail&&LY.nb>1)LY=lay(false,LY.nb-1);\n", "")],
    'legend_blocks_before_sources': [("      if(LY.h>avail)LY=lay(false,blocks.length);\n", "")],
    'legend_more_unsaid': [("        if(nb<blocks.length){ctx.font='10px sans-serif';mt=", "        if(false){ctx.font='10px sans-serif';mt=")],
    # ---- the ground ----
    'cell_ten': [("BIM_LAND_HALF=150,BIM_LAND_CELL=5,", "BIM_LAND_HALF=150,BIM_LAND_CELL=10,")],
    'metres_rounded': [("if(isFinite(ev)){h.push(Math.round(ev*100));got++;}", "if(isFinite(ev)){h.push(Math.round(ev)*100);got++;}")],
    'datum_ignored': [("D.H[i]=d.h[i]/100-dat;D.ok[i]=1;", "D.H[i]=d.h[i]/100;D.ok[i]=1;")],
    'datum_unset': [("      A3D.site.terrainBase=Math.round(b0*100)/100;dat=A3D.site.terrainBase;\n", "      dat=0;\n")],
    'own_surface_ignored': [("      if(!own&&bimTinIndexOf(o).at(S.c[0],S.c[1])!==null)own=o;\n", "")],
    'moved_site_read': [("org&&d.org&&Math.abs(d.org.lat-org.lat)<1e-9&&Math.abs(d.org.lon-org.lon)<1e-9&&", "")],
    'context_before_tiles': [("if(own)from='own';else if(fresh)from='tiles';else if(ct)from='context';else return null;",
                              "if(own)from='own';else if(ct)from='context';else if(fresh)from='tiles';else return null;")],
    'cache_unkeyed': [("    if(A3D_LAND.key===key&&A3D_LAND.D)return A3D_LAND.D;\n", "    if(A3D_LAND.D)return A3D_LAND.D;\n")],
    # ---- slope, aspect, marching squares, contours ----
    'horn_unweighted': [("var dx=((cc+2*f+ii)-(a+2*d+g))/(8*c),dz=((g+2*hh+ii)-(a+2*b+cc))/(8*c);", "var dx=((cc+f+ii)-(a+d+g))/(6*c),dz=((g+hh+ii)-(a+b+cc))/(6*c);")],
    'edge_zero': [("function h(i2,j2,e){if(i2<0||j2<0||i2>=nx||j2>=nz)return e;", "function h(i2,j2,e){if(i2<0||j2<0||i2>=nx||j2>=nz)return 0;")],
    'never_flat': [("as[k]=sl[k]<BIM_LAND_FLAT?-1:", "as[k]=false?-1:")],
    'aspect_upslope': [("Math.atan2(-dx*ex-dz*ez,-dx*nxv-dz*nzv)", "Math.atan2(dx*ex+dz*ez,dx*nxv+dz*nzv)")],
    'slope_site_everywhere': [("      if(M[k]){sc[i]++;stot++;sum+=hn.slope[k];if(hn.slope[k]>mx){mx=hn.slope[k];mxk=k;}}\n",
                               "      {sc[i]++;stot++;sum+=hn.slope[k];if(hn.slope[k]>mx){mx=hn.slope[k];mxk=k;}}\n")],
    'warm_north': [("var az=d8*45,eq=lat<0?0:180,", "var az=d8*45,eq=180,")],
    'site_mask_wide': [("?bimPointInPoly([x,z],S.ring):d2<=S.r*S.r)", "?bimPointInPoly([x,z],S.ring):d2<=4*S.r*S.r)")],
    'saddle_fixed': [("up=(a+b+c+d)/4>=lev;", "up=false;")],
    'closed_loops_open': [("for(s=0;s<segs.length;s++)if(!used[s]){var rg=walk(s,segs[s][0]);if(o)rg.pop();out.push(rg);}",
                           "for(s=0;s<segs.length;s++)if(!used[s]){var rg=walk(s,segs[s][0]);rg.pop();out.push(rg);}")],
    'rings_simplified': [("r=bimLandDP(r,D.cell*0.002,true);", "r=bimLandDP(r,D.cell*0.12,true);")],
    'contours_from_model_zero': [("var base=D.datum||0,st=bimLandStep(D,base)", "var base=0,st=bimLandStep(D,base)")],
    'index_every_fourth': [("idx=Math.round(k)%5===0", "idx=Math.round(k)%4===0")],
    'contour_label_unit': [("lb:idx&&best?[{t:ht.replace(/ m$/,''),", "lb:idx&&best?[{t:ht,")],
    'contours_one_colour': [("var col=bimLandHypso((y-st.lo)/span),", "var col=bimLandHypso(0),")],
    # ---- water ----
    'pf_flat_traps': [("F[nk]=Math.max(H[nk],F[cc]+BIM_LAND_EPS*DL[d]);", "F[nk]=Math.max(H[nk],F[cc]);")],
    'd8_diagonal_short': [("var s2=(F[k]-F[q])/(DL[d]*c);", "var s2=(F[k]-F[q])/c;")],
    'acc_lowest_first': [("var byF=ord.slice().sort(function(p,q2){return F[q2]-F[p]||q2-p;});", "var byF=ord.slice();")],
    'streams_from_more': [("if(ok[k]&&acc[k]>=BIM_LAND_STREAM)stream[k]=1;", "if(ok[k]&&acc[k]>=2*BIM_LAND_STREAM)stream[k]=1;")],
    'order_counts_every_join': [("cnt[k]>=2?mxo[k]+1:mxo[k]", "mxo[k]+1")],
    'width_flat': [("w:W[o-1],head:true", "w:W[0],head:true")],
    'catchments_all': [("return Y.outCells[o]>=BIM_LAND_CATCH*tot;", "return Y.outCells[o]>=1;")],
    'divides_with_small': [("if(i+1<nx&&D.ok[k+1]&&(b=Y.lab[k+1])!==a&&big[b])", "if(i+1<nx&&D.ok[k+1]&&(b=Y.lab[k+1])!==a)")],
    'divides_undashed': [("s:{stroke:'#8fa9c4',w:1.1,dash:[6,4],op:0.85}", "s:{stroke:'#8fa9c4',w:1.1,op:0.85}")],
    'upstream_site_only': [("    while(st.length){k=st.pop();for(u=Y.head[k];u>=0;u=Y.nxt[u])if(!U[u]){U[u]=1;st.push(u);}}\n", "")],
    'exits_unordered': [("    E.sort(function(a,b){return Y.acc[b]-Y.acc[a]||a-b;});\n", "")],
    'exit_reversed': [("dn=BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(bimLandAz(e[0]-P[0][0],e[2]-P[0][2]))]];",
                       "dn=BIM_LAND_DIRNAME[BIM_LAND_DIRS[bimLandDir8(bimLandAz(P[0][0]-e[0],P[0][2]-e[2]))]];")],
    'ponds_one_cm': [("if(!ok[k]||pid[k]||F[k]-H[k]<BIM_LAND_POND)continue;", "if(!ok[k]||pid[k]||F[k]-H[k]<0.01)continue;"),
                     ("if(ok[v]&&!pid[v]&&F[v]-H[v]>=BIM_LAND_POND){", "if(ok[v]&&!pid[v]&&F[v]-H[v]>=0.01){")],
    'ponds_any_size': [("if(pool.area>=BIM_LAND_POND_AREA)ponds.push(pool);", "ponds.push(pool);")],
    'pond_volume_unscaled': [("pool.volume+=dd*a2;", "pool.volume+=dd;")],
    # ---- flood zones ----
    'floodway_as_1pct': [("    if(/FLOODWAY/.test(st))return 'floodway';\n", "")],
    'coastal_as_1pct': [("return /^V/.test(z)?'coastal':'sfha';", "return 'sfha';")],
    'shaded_x_dropped': [("    if((z==='X'&&/0\\.2|1 PCT/.test(st))||z==='B')return 'x02';\n", "")],
    'minimal_x_drawn': [("    if(z==='D')return 'undetermined';\n    return null;", "    if(z==='D')return 'undetermined';\n    return 'x02';")],
    'bfe_none_shown': [("if(!isFinite(v)||v<=-9000)return null;", "if(!isFinite(v))return null;")],
    'bfe_feet_as_metres': [("m=ft?v*0.3048:v,", "m=v,")],
    'fema_everywhere': [("var pf=(bimLandUS(a.org)?bimLandFloodFetch(a,date):", "var pf=(true?bimLandFloodFetch(a,date):")],
    'zones_uncut': [("var r=bimLandClip(pos.map(function(q){return bimGeoToModel(q[0],q[1]);}),box);", "var r=pos.map(function(q){return bimGeoToModel(q[0],q[1]);});")],
    'site_zone_first_found': [("&&BIM_LAND_ZORDER.indexOf(zc)<rank){", "&&!out.site){")],
    'zones_lost_when_down': [("if(out.flood&&!(out.flood.error&&LD.flood&&LD.flood.features))LD.flood=out.flood;", "if(out.flood)LD.flood=out.flood;")],
    'zone_label_no_bfe': [("+(bfe?', BFE '+bfe.short:''),p:y3(lp,0.1)", "+'',p:y3(lp,0.1)")],
    'shaded_x_unsaid': [("(zc==='x02'?' (0.2%)':'')", "''")],
    # ---- findings, the step, Analyze ----
    'steep_uncounted': [("if(hn.slope[k]>=15)steep++;", "")],
    'drainage_upstream_unsaid': [("parts.push(nu?bimLandHa(nu*a2)+' around drains onto it':'nothing around drains onto it');", "parts.push('nothing around drains onto it');")],
    'floodway_not_red': [("cls:zc==='floodway'?'redflag':(zc?'constraint':'neutral')", "cls:zc?'constraint':'neutral'")],
    'land_findings_dropped': [(".concat(bimLandAuto());", ";")],
    'land_step_missing': [("['context','Context'],['land','Ground and water'],", "['context','Context'],")],
    'drawn_before_land': [("return Promise.all([pc,pk,pl]).then(function(){", "return Promise.all([pc,pk]).then(function(){")],
    'cards_ungrouped': [("  BIM_ANZ_GROUP_OF.dgflow='water';BIM_ANZ_GROUP_OF.dgponds='water';BIM_ANZ_GROUP_OF.dgflood='water';\n", "")],
    'version_old': [("  var BIM_APP_VERSION={v:'V165',date:'2026-10-11'};", "  var BIM_APP_VERSION={v:'V164',date:'2026-10-11'};")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV165' in txt
out.write_text(txt, encoding='utf-8')
