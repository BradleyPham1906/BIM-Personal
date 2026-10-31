"""falsify_phase172.py -- break the V172 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase172_site_tools_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("window.__acad3dV172='grid,extent,", "window.__acad3dV172='extent,")],   # the V172 marker
    'synth_record_value': [("{n:'near_art',v:30,u:'m',say:'near an arterial road, within'}", "{n:'near_art',v:35,u:'m',say:'near an arterial road, within'}")],   # the constraints map's distances ... a registry record
    'chalfont_ratio_off': [("{n:'slope_a',v:0.7,u:'ratio',say:'steep slopes of the lower class'}", "{n:'slope_a',v:0.75,u:'ratio',say:'steep slopes of the lower class'}")],   # Chalfont's open space ratios ... as read
    # ---- 2. the grid ----
    'margin_short': [("  var BIM_TL_MARGIN=100,BIM_TL_MAXCELLS=250000,", "  var BIM_TL_MARGIN=90,BIM_TL_MAXCELLS=250000,")],   # the extent: the lot and 100 m around it
    'never_coarser': [("    while(Math.ceil((x1-x0)/cell-1e-6)*Math.ceil((z1-z0)/cell-1e-6)>BIM_TL_MAXCELLS)cell*=2;", "")],   # a lot too large ... cells of 2 m
    'noise_counts': [("    nx=Math.ceil((x1-x0)/cell-1e-6);nz=Math.ceil((z1-z0)/cell-1e-6);", "    nx=Math.ceil((x1-x0)/cell);nz=Math.ceil((z1-z0)/cell);")],   # a lot too large ... (the float noise's row)
    'fill_shifted': [("        i0=Math.max(0,Math.ceil((X[k]-G.x0)/G.cell-0.5));", "        i0=Math.max(0,Math.ceil((X[k]-G.x0)/G.cell));")],   # a ring's cells, even-odd by the centres
    'fill_nonzero': [("      for(k=0;k+1<X.length;k+=2){", "      for(k=0;k+1<X.length;k+=1){")],   # a concave ring: its notch left out
    'stroke_wide': [("    for(j=j0;j<=j1;j++)for(i=i0;i<=i1;i++)if(bimTlSegDist(bimTlCx(G,i),bimTlCz(G,j),a,b)<=h+1e-9)m[j*G.nx+i]=v;",
                     "    for(j=j0;j<=j1;j++)for(i=i0;i<=i1;i++)if(bimTlSegDist(bimTlCx(G,i),bimTlCz(G,j),a,b)<=h*1.5+1e-9)m[j*G.nx+i]=v;")],   # a line's cells: within half a cell of it
    'alphabet_quote': [("for(c=33;c<=126;c++)if(c!==34&&c!==92)s+=String.fromCharCode(c);", "for(c=33;c<=126;c++)if(c!==92)s+=String.fromCharCode(c);")],   # the codes kept: ... no quote
    # ---- 3. the distance transform ----
    'dt_no_pop': [("      while(s<=z[k]){k--;s=((f[q]+q*q)-(f[v[k]]+v[k]*v[k]))/(2*q-2*v[k]);}", "      if(s<=z[k]){k--;s=((f[q]+q*q)-(f[v[k]]+v[k]*v[k]))/(2*q-2*v[k]);}")],   # Algorithm 1 along a line
    'dt_rows_only': [("    for(i=0;i<nx;i++){for(j=0;j<nz;j++)f[j]=D[j*nx+i];bimTlDt1(f,nz,d,v,z);for(j=0;j<nz;j++)D[j*nx+i]=d[j];}\n", "")],   # the grid's distances from the streets, exact
    'dt_cells': [("    for(i=0;i<N;i++)D[i]=Math.sqrt(D[i])*G.cell;", "    for(i=0;i<N;i++)D[i]=Math.sqrt(D[i]);")],   # a lot too large ... distances still in metres
    'big_infinite': [("BIM_TL_BIG=1e10;", "BIM_TL_BIG=Infinity;")],   # Algorithm 1 along a line (no source in a stretch)
    # ---- 4. buffer ----
    'buffer_strict': [("lv[k]=D&&D[k]<=P.dist+1e-9&&(P.side==='full'||!m[k])?0:-1;", "lv[k]=D&&D[k]<P.dist-1e-9&&(P.side==='full'||!m[k])?0:-1;")],   # around the streets, 7.5 m
    'buffer_outside_keeps': [("lv[k]=D&&D[k]<=P.dist+1e-9&&(P.side==='full'||!m[k])?0:-1;", "lv[k]=D&&D[k]<=P.dist+1e-9?0:-1;")],   # Outside an area: ... not the lot
    'buffer_inside_from_area': [("out=new Uint8Array(G.n);for(k=0;k<G.n;k++)out[k]=m[k]?0:1;D=bimTlDistance(G,out);", "out=new Uint8Array(G.n);for(k=0;k<G.n;k++)out[k]=m[k]?0:1;D=bimTlDistance(G,m);")],   # Inside an area: the band
    'side_unchecked': [("if(s&&s.kind!=='area'&&P.side!=='full')E.side='Outside or Inside is for an area layer';", "")],   # its checks: Outside for a line
    'num_min_inclusive': [("if(mn!==undefined&&mn!==null&&(p.gt?!(v>mn):!(v>=mn)))", "if(mn!==undefined&&mn!==null&&!(v>=mn))")],   # its checks: ... 0 m
    'num_max_off': [("        else if(mx!==undefined&&mx!==null&&!(v<=mx))", "        else if(0)")],   # its checks: ... beyond the margin
    'required_off': [("        if(v===null||v===undefined){if(p.req)E[p.id]='Required';return;}\n        if(!isFinite(v)){E[p.id]='Type a number';return;}",
                      "        if(v===null||v===undefined){return;}\n        if(!isFinite(v)){E[p.id]='Type a number';return;}")],   # its checks: ... empty
    'error_still_runs': [("    if(C.err){if(!opts.quiet)a3dToast(t.name+' cannot run: '+C.first);return {error:C.first,E:C.E};}", "    if(0){return {error:C.first,E:C.E};}")],   # a tool with an error does not run
    # ---- 5. distance ----
    'max_ignored': [("      for(k=0;k<G.n;k++)V[k]=P.max!==null&&D[k]>P.max+1e-9?NaN:D[k];", "      for(k=0;k<G.n;k++)V[k]=D[k];")],   # with a maximum of 25 m, no value beyond it
    'levels_few': [("  var BIM_TL_LEVELS=91;", "  var BIM_TL_LEVELS=31;")],   # each cell's distance, kept to its level of 91
    'distance_stats_extent': [("      for(k=0;k<G.n;k++)if(L[k]&&isFinite(V[k])){n++;sum+=V[k];", "      for(k=0;k<G.n;k++)if(isFinite(V[k])){n++;sum+=V[k];")],   # the lot's nearest, mean and farthest
    # ---- 6. slope classes ----
    'resample_nearest': [("q=[j0*D.nx+i0,j0*D.nx+i0+1,(j0+1)*D.nx+i0,(j0+1)*D.nx+i0+1];w=[(1-fx)*(1-fz),fx*(1-fz),(1-fx)*fz,fx*fz];s=0;t=0;",
                          "q=[j0*D.nx+i0,j0*D.nx+i0+1,(j0+1)*D.nx+i0,(j0+1)*D.nx+i0+1];w=[1,0,0,0];s=0;t=0;")],   # the ground's slope on the grid: between the 5 m grid's points
    'class_by_lower': [("        for(i=0;i<C.length-1;i++)if(s.v[k]<C[i][1])break;\n        lv[k]=i;if(L[k]){cnt[i]++;tot++;}", "        for(i=0;i<C.length-1;i++)if(s.v[k]<C[i][0])break;\n        lv[k]=i;if(L[k]){cnt[i]++;tot++;}")],   # each cell in the registry's class
    'slope_stats_extent': [("        lv[k]=i;if(L[k]){cnt[i]++;tot++;}", "        lv[k]=i;cnt[i]++;tot++;")],   # the lot's area in each class
    # ---- 7. exclusions ----
    'excl_last_reason': [("      for(k=0;k<G.n;k++)for(i=0;i<BIM_TL_EXCL.length;i++)if(masks[i]&&masks[i][k]){lv[k]=i;if(L[k])cnt[i]++;break;}", "      for(k=0;k<G.n;k++)for(i=0;i<BIM_TL_EXCL.length;i++)if(masks[i]&&masks[i][k]){lv[k]=i;if(L[k])cnt[i]++;}")],   # each cell its first reason
    'excl_steep_off': [("for(k=0;k<G.n;k++)st[k]=isFinite(s.v[k])&&s.v[k]>=P.steepAt-1e-9?1:0;", "for(k=0;k<G.n;k++)st[k]=isFinite(s.v[k])&&s.v[k]>=P.steepAt+5?1:0;")],   # ... then slopes from 25%
    'excl_missing_error': [("var s=bimTlSourceOf(G,x[1]);if(s.why)W[x[0]]=s.why+': nothing is excluded for it';", "var s=bimTlSourceOf(G,x[1]);if(s.why)E[x[0]]=s.why+': nothing is excluded for it';")],   # the wetlands not fetched: a warning, not an error
    'excl_buffer_ignored': [("      if(P.buffer){var B=bimTlRunOut(P.buffer,G);", "      if(0){var B=bimTlRunOut(P.buffer,G);")],   # ... and a buffer from History
    'excl_none_allowed': [("if(!P.outside&&!P.setbacks&&!P.flood&&!P.wetlands&&!P.steep&&!P.buildings&&!P.buffer)E._='Tick at least one reason, or pick a buffer';", "")],   # nothing ticked: refused
    # ---- 8. suitability ----
    'small_is_large': [("    if(how==='small')return 1/(1+Math.pow(Math.max(0,x)/mid,spread));", "    if(how==='small')return 1/(1+Math.pow(Math.max(0,x)/mid,-spread));")],   # the transforms against QGIS's formulas
    'near_peak_ends': [("    if(o.how==='near'&&mid>=T.lo&&mid<=T.hi)T.fmax=bimTlFn('near',mid,mid,sp);\n", "")],   # the transforms ... near
    'linear_one_way': [("    var down=o.how==='linear'&&o.dir==='down';", "    var down=false;")],   # the transforms ... linear either way
    'not_clamped': [("var xx=Math.max(T.lo,Math.min(T.hi,x)),f=bimTlFn(o.how,xx,mid,sp)", "var xx=x,f=bimTlFn(o.how,xx,mid,sp)")],   # the transforms (values beyond the thresholds)
    'break_lower': [("      T.f=function(x){var i=0;while(i<T.breaks.length&&x>=T.breaks[i])i++;return T.vals[i];};", "      T.f=function(x){var i=0;while(i<T.breaks.length&&x>T.breaks[i])i++;return T.vals[i];};")],   # classes (at a break, the class above)
    'cats_reversed': [("T.vals.push(Math.round((sc[1]-i*(sc[1]-sc[0])/(nc-1))*100)/100);", "T.vals.push(Math.round((sc[0]+i*(sc[1]-sc[0])/(nc-1))*100)/100);")],   # categories ... the first class best
    'flat_top': [("    if(T.flat){T.f=function(){return (sc[0]+sc[1])/2;};return T;}", "    if(T.flat){T.f=function(){return sc[1];};return T;}")],   # a criterion the same everywhere adds the scale's middle
    'pct_not_rescaled': [("        if(rg&&rg[1]>rg[0])for(k=0;k<G.n;k++){if(isFinite(S[k]))S[k]=sc[0]+(S[k]-rg[0])/(rg[1]-rg[0])*(sc[1]-sc[0]);}", "        if(0)for(k=0;k<G.n;k++){}")],   # by percent ... rescaled to 1 to 5
    'pct_sum_unchecked': [("else if(P.weightBy==='pct'&&!E._&&Math.abs(sum-100)>1e-6)E._=", "else if(0)E._=")],   # percentages that do not add to 100: refused
    'weights_ignored': [("s+=(P.weightBy==='pct'?U[j].w/100:U[j].w)*t;", "s+=t;")],   # by multiplier: 2 x slope ...
    'restricted_as_none': [("      if(rest)for(k=0;k<G.n;k++)if(rest[k]>=0)lv[k]=BIM_TL_LEVELS;\n", "")],   # the restricted cells kept as restricted, not no value
    'nodata_scored': [("var x=U[j].V[k];if(!isFinite(x)){ok=false;break;}", "var x=U[j].V[k];if(!isFinite(x)){continue;}")],   # a cell where a criterion has no value ... has none
    'restrict_default_none': [("{id:'restrict',label:'Restricted cells from',t:'run',of:'exclude',def:function(){return bimTlLast('exclude');}}", "{id:'restrict',label:'Restricted cells from',t:'run',of:'exclude',def:''}")],   # its defaults: the latest Exclusions run restricts
    'missing_layer_on': [("var s=bimTlSourceOf(G,c.src),D={on:!!c.on&&!s.why,", "var s=bimTlSourceOf(G,c.src),D={on:!!c.on,")],   # its defaults: ... a criterion whose layer is missing is off
    'crit_breaks_fall': [("          for(var i=1;i<b.length;i++)if(!(b[i]>b[i-1])){E[key]=c.name+': the breaks must rise';return;}\n", "")],   # a criterion's checks: breaks that fall
    # ---- 9. locate ----
    'grow_diagonal': [("      nb=[i>0?k-1:-1,i<G.nx-1?k+1:-1,j>0?k-G.nx:-1,j<G.nz-1?k+G.nx:-1];", "      nb=[i>0?k-1:-1,i<G.nx-1?k+1:-1,j>0?k-G.nx:-1,j<G.nz-1?k+G.nx:-1,i<G.nx-1&&j<G.nz-1?k+G.nx+1:-1];")],   # grown by the best neighbour sharing a side
    'seeds_one': [("    for(i=0;i<C.length&&S.length<24;i++){", "    for(i=0;i<C.length&&S.length<1;i++){")],   # its mean the best of the seeds
    'locate_worst': [("if(r&&(!best||r.mean>best.mean+1e-12)){best=r;best.seed=i;}", "if(r&&(!best||r.mean<best.mean-1e-12)){best=r;best.seed=i;}")],   # the region ... the reference's own
    'locate_anywhere': [("ok[k]=v!==null&&(P.within!=='lot'||!G.lot||G.lot[k])?1:0;", "ok[k]=v!==null?1:0;")],   # within the lot, the region stays on it
    'locate_area_unchecked': [("      if(bimTlArea(I.n,G)<P.area-1e-9)E.area='Only '+bimTlAreaText(bimTlArea(I.n,G))+' can be used there';\n", "")],   # an area larger than can be used: refused
    # ---- 10. buildable area ----
    'cap_last_resource': [("      for(i=0;i<has.length;i++)if(has[i]&&r[i]>bv+1e-12){bv=r[i];best=i;}", "      for(i=0;i<has.length;i++)if(has[i]){bv=r[i];best=i;}")],   # each lot cell's resource: the highest ratio
    'cap_forest_with_off': [("      if(has[6]&&other){has[5]=true;has[6]=false;}\n", "")],   # forest with another resource ... at its own ratio
    'cap_less_ignored': [("base=Math.max(0,tot-(P.less||0))", "base=tot")],   # Chalfont's form: base
    'cap_units_rounded': [("String(Math.floor(net/BIM_TL_ACRE*P.density+1e-9))", "String(Math.round(net/BIM_TL_ACRE*P.density))")],   # units at 13 an acre not rounded up
    'cap_upper_from_lower': [("sl&&isFinite(sl.v[k])&&sl.v[k]>=hi-1e-9,sl&&isFinite(sl.v[k])&&sl.v[k]>=lo-1e-9&&sl.v[k]<hi-1e-9", "sl&&isFinite(sl.v[k])&&sl.v[k]>=lo-1e-9,sl&&isFinite(sl.v[k])&&sl.v[k]>=lo-1e-9&&sl.v[k]<hi-1e-9")],   # overlaps ... the lower steep class
    'cap_ratio_literal': [("{id:'flood',name:'Floodplain',r:function(){return bimStd('land.site_capacity','floodplain');}", "{id:'flood',name:'Floodplain',r:function(){return 1;}")],   # an override of the floodplain's ratio changes the calculation
    'cap_wetlands_skipped': [("we=mask('wetlands','Wetlands');", "we=null;")],   # each lot cell's resource (the wetland)
    'nwi_point': [("geometryType:'esriGeometryEnvelope',\n      inSR:4326,outSR:4326", "geometryType:'esriGeometryPoint',\n      inSR:4326,outSR:4326")],   # Get wetlands asks ... over the extent
    'nwi_us_inverted': [("    if(!bimLandUS(org)){T.wetlands={outside:true", "    if(bimLandUS(org)){T.wetlands={outside:true")],   # Get wetlands ... one wetland back
    # ---- 11. constraints and opportunities ----
    'synth_last_first': [("        for(i=0;i<ms.length;i++)if(ms[i]&&ms[i][k]){lv[k]=i;cnt[i]++;break;}", "        for(i=ms.length-1;i>=0;i--)if(ms[i]&&ms[i][k]){lv[k]=i;cnt[i]++;break;}")],   # each cell's first constraint, else its first opportunity
    'synth_noise_literal': [("na=bimStd('app.synthesis','near_art')", "na=50")],   # on the lot, each cell's first constraint (near an arterial)
    'synth_setbacks_lost': [("      var sb=G.lot?bimTlSetbackMask(G,W):null;", "      var sb=null;")],   # the zoning's setbacks a constraint once they are recorded
    'setbacks_need_height': [("    try{var P=bimZnProperty(),zz=bimZn(),L=P?bimZnLegs(P,zz.frontLeg,zz.legRoles):null;", "    try{var P=bimZnProperty(),zz=bimZn(),L=P&&!bimZnCalc().error?bimZnLegs(P,zz.frontLeg,zz.legRoles):null;")],   # the zoning's setbacks ... (no height limit)
    # ---- 12. the pane ----
    'field_not_rechecked': [("{bimTlSetField(k,e.type==='checkbox'?e.checked:e.value);if(bimAwOwns())bimAwRender(true);}", "{bimTlSetField(k,e.type==='checkbox'?e.checked:e.value);}")],   # a field typed is checked at once
    'run_not_held': [("bimAwBtn('tl:run:'+t.id,'Run',true,C.err?C.first:'')", "bimAwBtn('tl:run:'+t.id,'Run',true,'')")],   # ... Run held with why
    'field_not_kept': [("      S[p.id]=v;\n    }\n    saveSoon();", "    }\n    saveSoon();")],   # a good value is kept as the tool's parameter
    'overwrite_off': [("    for(i=0;i<Ls.length;i++)if(Ls[i].kind==='tool'&&Ls[i].sig===sig){R=Ls[i];break;}", "")],   # Run again ...: the same layer overwritten
    'open_not_restoring': [("    bimTlState().params[t.id]=bimTlCopy(h.params);saveSoon();\n", "")],   # Open from History sets the tool's parameters
    'reset_dead': [("    if(c==='reset'){var T=bimTlState();delete T.params[v];", "    if(c==='reset'){var T=bimTlState();")],   # Reset parameters: the defaults again
    'forget_dead': [("    T.history.splice(i,1);saveSoon();", "    saveSoon();")],   # Remove takes a run from History
    'run_no_undo': [("    pushUndo();\n    T=bimTlState();\n    h={id:'tlh-'", "    T=bimTlState();\n    h={id:'tlh-'")],   # undo takes the run and its layer back: one step
    'history_unlisted': [("(H.length?'<div class=\"a3d-tl-hist\">'+H.map(function(x){return bimTlHistRow(x,true);}).join('')+'</div>'", "(H.length?'<div class=\"a3d-tl-hist\">'+H.slice(0,3).map(function(x){return bimTlHistRow(x,true);}).join('')+'</div>'")],   # History lists every run
    # ---- 13. layers ----
    'others_stay_shown': [("      bimResLayers().forEach(function(L){if(L.kind==='tool')L.visible=L.id===R.id;});\n", "")],   # a run's output is shown alone
    'layer_not_drawn': [("    if(R.kind==='tool'){var im=bimTlDataOk(d)?bimTlImage(R):null;if(!im)return false;", "    if(R.kind==='tool'){return false;")],   # drawn on the plan
    'layer_dropped_on_load': [("      if(R.kind==='tool')return bimTlDataOk(R.data);   /* __acad3dV172 */", "      if(R.kind==='tool')return false;")],   # a reload keeps ... the layers
    'stale_never': [("  function bimTlStale(R){return !!(R&&R.kind==='tool'&&R.data&&R.data.gkey!==bimTlGrid().key);}", "  function bimTlStale(R){return false;}")],   # the lot moved: the layer is out of date
    'update_no_rerun': [("    if(R.kind==='tool')return bimTlLayerRerun(R);   /* __acad3dV172: its run again, with the same parameters */\n", "")],   # Update in Layers runs its tool again
    'hide_dead': [("    if(c==='show'){R=bimResById(v);if(!R)return false;return bimResultLayerSet(v,'visible',R.visible===false);}", "    if(c==='show'){return false;}")],   # Hide in the panel hides it
    # ---- 14. the search and the commands ----
    'search_tools_unread': [("bimTlCards().forEach(function(x){C[x.id]=x;});}   /* __acad3dV172: the tools' rows */", "}   /* __acad3dV172: the tools' rows */")],   # the search finds Suitability
    'command_wrong_tool': [("tlsuit:function(){bimTlCommand('suit');}", "tlsuit:function(){bimTlCommand('locate');}")],   # each command opens its tool
    # ---- 16. a phone ----
    'phone_ticks_small': [("@media(pointer:coarse){.a3d-tl-b{min-height:36px}", "@media(pointer:coarse){.a3d-tl-b{min-height:20px}")],   # its fields and its ticks a finger's height
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV172' in txt
out.write_text(txt, encoding='utf-8')
