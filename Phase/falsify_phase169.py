"""falsify_phase169.py -- break the V169 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase169_assets_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the standards ----
    'rec_man': [("{n:'man',v:1.753,u:'m'", "{n:'man',v:1.75,u:'m'")],   # body.us: every value as its source prints it
    'rec_eye_hi': [("{n:'eye_hi',v:0.889,u:'m'", "{n:'eye_hi',v:0.9,u:'m'")],   # body.hidh's values
    'rec_chair_height': [("{n:'height',v:1.249,u:'m'", "{n:'height',v:1.25,u:'m'")],   # wheel.awmp's values
    'rec_ada_turn': [("{n:'turn',v:1.525,u:'m'", "{n:'turn',v:1.5,u:'m'")],   # ada.space's values; 1525 mm
    'rec_cycle_len': [("{n:'length',v:1.8,u:'m',say:'a solo upright cycle", "{n:'length',v:1.9,u:'m',say:'a solo upright cycle")],   # ltn.cycle's values
    'rec_bay_w': [("{n:'width',v:2.4,u:'m',say:'a bay", "{n:'width',v:2.5,u:'m',say:'a bay")],   # parking.bay's values
    'rec_gsl_days': [("{n:'days',v:6,u:'days'", "{n:'days',v:5,u:'days'")],   # etccdi.gsl's values
    'rec_utd': [("['BDM',14,11.9,0.85]", "['BDM',14,12,0.85]")],   # the trees' table
    'rec_su_ctr': [("{n:'SU_ctr',v:11.58,u:'m'", "{n:'SU_ctr',v:11.6,u:'m'")],   # aashto.vehicles' values
    'rec_bus_unsaid': [("say:'its minimum design turning radius (Table 2-5b; Table 2-5a gives 41.6 ft, 12.68 m)'", "say:'its minimum design turning radius'")],   # the two tables differ, said
    'rec_feet_lost': [("src:'19.0 ft'", "src:'19 ft'")],   # each value carries its figure in feet
    'rec_order_lost': [("gt:'P_wb',lt:'P_r'", "lt:'P_r'")],   # radii kept in order
    'rec_utd_level': [("v:[{n:'types',t:1,lv:'S',", "v:[{n:'types',t:1,lv:'P',")],   # our medians (S)
    'rec_app_level': [("w:'research-assets.md',lv:'A'}", "w:'research-assets.md',lv:'P'}")],   # the app's own (A)
    'rec_not_anywhere': [("use:'People: their heights',anywhere:true,", "use:'People: their heights',")],   # applied anywhere and said so
    'rec_area': [("kind:'standard',area:'Assets',use:'The car, the delivery truck", "kind:'standard',area:'Highways',use:'The car, the delivery truck")],   # eleven records in the Assets area
    'rec_read_date': [("ltn-1-20.pdf',lv:'P',read:'2026-10-19'}", "ltn-1-20.pdf',lv:'P',read:'2026-10-18'}")],   # read on the day
    'rec_host': [("u:'https://www.nasa.gov/sites/default/files/atoms/files/human_integration_design_handbook_revision_1.pdf'", "u:'https://ntrs.nasa.gov/sites/default/files/atoms/files/human_integration_design_handbook_revision_1.pdf'")],   # read from its host
    'rec_adopt_dated': [("adopt:[{at:'us'}],", "adopt:[{at:'us',from:'2018'}],")],   # the United States' through 23 CFR 625.4
    'rec_where': [("where:'United States: 23 CFR 625.4 incorporates the 7th Edition for the National Highway System'", "where:'United States'")],   # 23 CFR 625.4
    # ---- 2. the library ----
    'lib_title': [("h+=grp('entourage','People, cycles, vehicles, parking and trees'", "h+=grp('entourage','People and things'")],   # the group's name
    'lib_cat': [("{k:'car',name:'Car',cat:'Vehicles',", "{k:'car',name:'Car',cat:'Parking',")],   # each under its category
    'lib_no_picture': [("mesh:b?b.mesh:{v:[],f:[]},thumb:''}", "mesh:{v:[],f:[]},thumb:''}")],   # each with its picture
    'lib_search_cat': [("if(!bimAssetMatch(q,[BIM_ENT[i].name,BIM_ENT[i].cat,'asset','people','scale','entourage']))continue;", "if(!bimAssetMatch(q,[BIM_ENT[i].name,'asset','people','scale','entourage']))continue;")],   # search 'vehicle'
    'lib_click_dead': [("if(kind==='asset')return !!bimEntPlace(key,at||bimViewCentrePlan());", "if(kind==='asset')return false;")],   # a click places a man
    'lib_no_undo': [("    a.cf=b.cf;\n    pushUndo();\n", "    a.cf=b.cf;\n")],   # undo takes the cycle away
    'lib_name': [("name:sp.name+' '+A3D.counts.asset", "name:sp.name")],   # a click places a man (Man 1)
    # ---- 3. the sizes ----
    'body_scale': [("t=(st-lo)/((hi-lo)||1)", "t=(st-lo)/((hi-lo+0.1)||1)")],   # NASA's linear scaling: the eyes
    'body_sh_swapped': [("sh=bimEntLerp(bimStd('body.hidh','sh_lo'),bimStd('body.hidh','sh_hi'),t)", "sh=bimEntLerp(bimStd('body.hidh','sh_hi'),bimStd('body.hidh','sh_lo'),t)")],   # the shoulders
    'body_out_lost': [("out:t<0||t>1", "out:false")],   # the child extrapolated
    'body_speed': [("speed:bimStd('walk.speed','m_min')/60", "speed:bimStd('walk.speed','m_min')/50")],   # walking 1.33 m/s
    'person_width': [("aw=(sh-tw)/2", "aw=(sh-tw)/3")],   # shoulders across
    'seated_top': [("top:seated?seat+sit:st", "top:seated?sit:st")],   # seated, the top of the head
    'chair_margin': [("W=bimStd('ada.space','clear_w')*0.85", "W=bimStd('ada.space','clear_w')*0.9")],   # within ADA's space less 15%
    'chair_height': [("top=bimStd('wheel.awmp','height'),", "top=bimStd('wheel.awmp','height')+0.05,")],   # as tall as the Access Board's users
    'bike_len': [("zf=L/2-r,zr=-(L/2-r)", "zf=L/2-r+0.05,zr=-(L/2-r)")],   # LTN 1/20's cycle
    'stand_top': [("bimEntBox([0,h-t/2,0],[t,t,w])", "bimEntBox([0,h,0],[t,t,w])")],   # the stand
    'bay_len': [("var W=bimStd('parking.bay','width'),L=bimStd('parking.bay','length'),lw", "var W=bimStd('parking.bay','width'),L=bimStd('parking.bay','aisle45'),lw")],   # the bay
    'veh_height_lo': [("if(c==='SU')V.hlo=g('hlo');", "if(c==='SU'){V.hlo=g('hlo');V.h=V.hlo;}")],   # the truck drawn at its largest height
    'veh_wheels_out': [("xw=W/2-tw/2", "xw=W/2")],   # the vehicles' width
    'tree_crown_v157': [("for(i=0;i<12;i++)v.push([x+ico[i][0]/g*cr,cb+ico[i][1]/g*rv,z+ico[i][2]/g*cr]);", "for(i=0;i<12;i++)v.push([x+ico[i][0]/Math.sqrt(1+g*g)*cr,cb+ico[i][1]/Math.sqrt(1+g*g)*rv,z+ico[i][2]/Math.sqrt(1+g*g)*cr]);")],   # the crown its stated spread (V157's 0.85)
    'tree_cone_open': [("    f.push([b+7,b+6,b+5,b+4,b+3,b+2,b+1,b]);\n", "")],   # a cone of nine faces
    'tree_no_fallback': [("keys=[lf+(p.cyc==='E'?'E':'D')+sz,lf+'E'+sz,lf+'D'+sz]", "keys=[lf+(p.cyc==='E'?'E':'D')+sz]")],   # a deciduous conifer: the large conifer
    'tree_crown_first': [("      return {mesh:{v:v,f:f},cf:6};\n    }\n", "      return {mesh:{v:v,f:f},cf:0};\n    }\n")],   # the trunk's faces first
    'markers_swapped': [("return {v:[[0,0,back],[0,0,front]].concat(m.v),", "return {v:[[0,0,front],[0,0,back]].concat(m.v),")],   # each facing +z
    'rebuild_unturned': [("var F=bimEntFrame(o),ca=Math.cos(F.a),sa=Math.sin(F.a);", "var F=bimEntFrame(o),ca=1,sa=0;")],   # rebuilt facing the way it faced
    'family_cat': [("bim:{type:'familyInstance',familyId:'asset:'+key,familyName:sp.name,category:sp.cat,", "bim:{type:'familyInstance',familyId:'asset:'+key,familyName:sp.name,category:'Entourage',")],   # a family instance in its category
    'colour_shared': [("Trees:'#5b8a4c',Vehicles:'#7f8fa6'}", "Trees:'#5b8a4c',Vehicles:'#5f7f9e'}")],   # each category its own colour
    # ---- 4. Properties ----
    'props_eye': [("r+=bimPropLenText('Eye height',B.eye)", "r+=bimPropLenText('Eye height',B.top)")],   # a man's rows: eyes
    'props_speed_label': [("bimPropText('Walking speed',bimStdFmt(", "bimPropText('Speed',bimStdFmt(")],   # walking 1.33 m/s
    'props_out_unsaid': [("if(B.out)r+=bimPropText('Proportions'", "if(false)r+=bimPropText('Proportions'")],   # the proportions an estimate, said
    'props_negative': [("v=parseFloat(val);if(!isFinite(v)||v<=0){a3dToast('Must be a positive number');", "v=parseFloat(val);if(!isFinite(v)){a3dToast('Must be a positive number');")],   # -1 refused
    'props_who_keeps_h': [("else{p[key]=String(val);if(key!=='pose')delete p.h;", "else{p[key]=String(val);")],   # someone else chosen: their own height goes
    'props_no_undo': [("    else if(key!=='turn'&&!/^(who|pose|leaf|cyc|size|side)$/.test(key))return false;\n    pushUndo();\n", "    else if(key!=='turn'&&!/^(who|pose|leaf|cyc|size|side)$/.test(key))return false;\n")],   # undo: back to the child's height
    'props_chair_space': [("bimDispLen(bimStd('wheel.awmp','space_w'))+' by '", "bimDispLen(bimStd('ada.space','clear_w'))+' by '")],   # 0.82 by 1.42
    'props_corner': [("r+=bimPropText(bimLenLabel('Corner'),bimDispLen(V.rov)", "r+=bimPropText(bimLenLabel('Corner'),bimDispLen(V.r)")],   # its overhang's corner, worked out
    'props_sym': [("SU:['Single-unit truck','SU-30']", "SU:['Single-unit truck','SU-9']")],   # AASHTO's SU-30
    'props_range_lost': [("+(V.c==='SU'?bimPropText(bimLenLabel('Height')", "+(false?bimPropText(bimLenLabel('Height')")],   # its height range
    'props_season_unsaid': [("if(!G)return 'all year, taken so: the site\\'s climate is not fetched (Analyze site), so its growing season is not known';", "if(!G)return 'all year';")],   # in leaf all year, said
    'props_std_lost': [("      L=['aashto.vehicles','app.assets'];\n", "      L=['app.assets'];\n")],   # the truck's standards
    # ---- 5. overrides ----
    'refit_none': [("    try{if(typeof bimEntRefit==='function')bimEntRefit();}catch(e3)", "    try{if(false)bimEntRefit();}catch(e3)")],   # the placed man resizes
    'refit_own_lost': [("if(o.asset&&o.asset.k&&o.mesh&&bimEntRebuild(o))n++;", "if(o.asset&&o.asset.k&&o.mesh){delete o.asset.p.h;if(bimEntRebuild(o))n++;}")],   # the one with his own height does not
    # ---- 6. the growing season ----
    'gsl_ge': [("for(k=0;k<len;k++){run=a[k]>T?run+1:0;", "for(k=0;k<len;k++){run=a[k]>=T?run+1:0;")],   # 5.0 C is not above 5
    'gsl_le': [("run=a[k]<T?run+1:0;if(run>=N){e0=k-N+1;break;}", "run=a[k]<=T?run+1:0;if(run>=N){e0=k-N+1;break;}")],   # 5.0 C is not below 5
    'gsl_no_mid': [("for(k=Math.max(mid,s0+N);k<len;k++)", "for(k=s0+N;k<len;k++)")],   # a cold April does not end it
    'gsl_sh_jan': [("di=Math.round((Date.UTC(Y,M-1,+m[3])-Date.UTC(sy,sh?6:0,1))/864e5);", "di=Math.round((Date.UTC(Y,M-1,+m[3])-Date.UTC(sy,0,1))/864e5);")],   # lat -35
    'gsl_missing_kept': [("for(k=0;k<len;k++)if(a[k]===undefined||a[k]===null){full=false;break;}", "")],   # a year with a missing day left out
    'gsl_no_tg': [("var tm=(d.temperature_2m_mean||[])[i],tx=(d.temperature_2m_max||[])[i],tn=(d.temperature_2m_min||[])[i];\n      if(!bimClimNum(tm)&&bimClimNum(tx)&&bimClimNum(tn))tm=(tx+tn)/2;\n      var Y=+m[1]", "var tm=(d.temperature_2m_mean||[])[i],tx=(d.temperature_2m_max||[])[i],tn=(d.temperature_2m_min||[])[i];\n      var Y=+m[1]")],   # no means: ETCCDI's TG
    'gsl_median': [("return n%2?L[(n-1)/2]:Math.round((L[n/2-1]+L[n/2])/2);", "return L[0];")],   # the median of 10 years
    'gsl_not_kept': [("if(R[0].ok){var G0=bimClimGsl(R[0].js,lat);if(G0)C.gsl=G0;else delete C.gsl;}", "if(R[0].ok){}")],   # the season kept with the site
    'gsl_unstamped': [("std:bimStdStamp(['etccdi.gsl'])}", "std:null}")],   # with the standard it used
    'gsl_noseason': [("if(s0<0){st.push(len);en.push(len);continue;}", "if(s0<0){continue;}")],   # never above 5 C
    'gsl_threshold_fixed': [("T=bimStd('etccdi.gsl','t'),N=bimStd('etccdi.gsl','days')", "T=5,N=bimStd('etccdi.gsl','days')")],   # the threshold overridden to 10 C
    # ---- 7. leaf and shadow ----
    'leaf_never_bare': [("return !!(a&&a.k==='tree'&&a.p&&a.p.cyc!=='E'&&a.cf>0&&", "return !!(false&&a.k==='tree'&&a.p&&a.p.cyc!=='E'&&a.cf>0&&")],   # bare, their trunks alone
    'leaf_evergreen_bare': [("a.k==='tree'&&a.p&&a.p.cyc!=='E'&&a.cf>0", "a.k==='tree'&&a.p&&a.cf>0")],   # the evergreen casts all of itself
    'leaf_end_inclusive': [("return d===null?true:(d>=G.s&&d<G.e);", "return d===null?true:(d>=G.s&&d<=G.e);")],   # the season's last day
    'leaf_no_climate_bare': [("function bimEntInLeaf(date){var G=bimEntSeason(),d;if(!G)return true;", "function bimEntInLeaf(date){var G=bimEntSeason(),d;if(!G)return false;")],   # with no climate, in leaf all year
    'leaf_date_ignored': [("!bimEntInLeaf(date||bimSunSettings().date)", "!bimEntInLeaf(bimSunSettings().date)")],   # each date its own leaf
    'shadow_whole': [("f:bimEntBare(o,date)?o.mesh.f.slice(0,o.asset.cf):o.mesh.f}", "f:o.mesh.f}")],   # bare, their trunks alone casting a shadow
    # ---- 8. turning ----
    'turn_wc_diameter': [("r:[bimStd('ada.space','turn')/2],what:'the turning space'", "r:[bimStd('ada.space','turn')],what:'the turning space'")],   # ADA's 1.525 m across
    'turn_side_lost': [("sd=a.p.side==='R'?-1:1", "sd=1")],   # turning right
    'turn_mirrored': [("c:[ax+q[0]+sd*fz*V.rr,az+q[2]-sd*fx*V.rr]", "c:[ax+q[0]-sd*fz*V.rr,az+q[2]+sd*fx*V.rr]")],   # to its left
    'turn_rear_axle': [("zr=-V.l/2+V.or,ax=", "zr=-V.l/2+V.of,ax=")],   # round a centre off its rear axle
    'turn_rr': [("V.rr=Math.sqrt(Math.max(0,V.ctr*V.ctr-V.wb*V.wb));", "V.rr=V.ctr;")],   # sqrt(CTR^2 - WB^2)
    'turn_rov': [("Math.pow(V.wb+V.of,2));", "Math.pow(V.wb,2));")],   # the overhang's corner
    'turn_two_radii': [("r:[V.rin,V.r,V.rov],what:'its turning path'", "r:[V.rin,V.r],what:'its turning path'")],   # out to the overhang's corner
    'turn_unturned': [("fx=Math.sin(F.a),fz=Math.cos(F.a),sd=", "fx=0,fz=1,sd=")],   # its turning centre turns with it
    'turn_hidden_shown': [("if(!a||!a.p||!a.p.turn||!o.mesh||!bimLayerShown(o))continue;", "if(!a||!a.p||!a.p.turn||!o.mesh)continue;")],   # their layer hidden
    'turn_untick_ignored': [("if(!a||!a.p||!a.p.turn||!o.mesh||", "if(!a||!a.p||!o.mesh||")],   # the bus's box unticked
    'turn_not_drawn': [("if(!capMode)bimEntDrawTurns(ctx,V,W,H);", "")],   # the five drawn on the plan
    # ---- 9. the context's trees ----
    'ctx_ratio_lost': [("cd2=bimTagMetres(f.tags.diameter_crown)||th2*bimEntCrownRatio(f.tags)", "cd2=bimTagMetres(f.tags.diameter_crown)||th2*bimStd('app.assets','crown')")],   # OSM tree 9001
    'ctx_cone_lost': [("o.mesh=bimEntTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2,lf2.type==='C').mesh;", "o.mesh=bimEntTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2,false).mesh;")],   # a cone
    'ctx_diameter_ignored': [("cd2=bimTagMetres(f.tags.diameter_crown)||", "cd2=")],   # OSM tree 9006
    'leafof_semi': [("cyc:/^(semi_)?deciduous$/.test(lc)?'D':(/^(semi_)?evergreen$/.test(lc)?'E':'')", "cyc:/^(semi_)?deciduous$/.test(lc)?'D':(/^evergreen$/.test(lc)?'E':'')")],   # broadleaved semi-evergreen
    'leafof_needle': [("type:lt==='needleleaved'?'C':", "type:lt==='coniferous'?'C':")],   # needle-leaved: a cone
    'ctx_leaf_unsaid': [("if(c.kind==='trees'&&c.leaf&&(c.leaf.type||c.leaf.cyc))r+=bimPropText('Leaf',", "if(false)r+=bimPropText('Leaf',")],   # a mapped tree's page: its leaf
    # ---- 10. a thousand trees, a reload, the numbers ----
    'place_refits_all': [("    A3D.objs.push(o);\n    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];\n    refreshTree();refreshHud();paint();saveSoon();\n    a3dToast(o.name+' placed');",
                          "    A3D.objs.push(o);bimEntRefit();\n    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];\n    refreshTree();refreshHud();paint();saveSoon();\n    a3dToast(o.name+' placed');")],   # the thousandth placed fast
    'json_heavy': [("    a.cf=b.cf;\n    pushUndo();\n", "    a.cf=b.cf;a.lib=b.mesh;\n    pushUndo();\n")],   # under 2 KB a tree
    'literal_seat': [("var W=bimStd('ada.space','clear_w')*0.85,L=bimStd('ada.space','clear_l')*0.85,s2=bimStd('wheel.awmp','seat'),", "var W=bimStd('ada.space','clear_w')*0.85,L=bimStd('ada.space','clear_l')*0.85,s2=0.495,")],   # no value written into the code
    'version_old': [("var BIM_APP_VERSION={v:'V169',date:'2026-10-19'};", "var BIM_APP_VERSION={v:'V168',date:'2026-10-19'};")],   # V169 or later
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV169' in txt
out.write_text(txt, encoding='utf-8')
