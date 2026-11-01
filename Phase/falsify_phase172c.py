"""falsify_phase172c.py -- break the V172c build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase172c_ladybug_studies_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("window.__acad3dV172c='gendaymtx,wasm,sha256,", "window.__acad3dV172c='wasm,")],   # the V172c marker
    'ground_ref_off': [("{n:'ground_ref',v:0.2,u:'ratio',say:'the ground\\'s reflectance, Ladybug", "{n:'ground_ref',v:0.25,u:'ratio',say:'the ground\\'s reflectance, Ladybug")],   # the registry's app.solar
    'offset_off': [("{n:'offset',v:0.1,u:'m',", "{n:'offset',v:0.3,u:'m',")],   # the registry's app.solar
    'rad_pin_wrong': [("var BIM_LB_RAD={f:'radiance/gendaymtx.wasm',h:'45726aea", "var BIM_LB_RAD={f:'radiance/gendaymtx.wasm',h:'45726aeb")],   # the app pins gendaymtx by the manifest's SHA-256
    # ---- 2. the rows ----
    'sun_needs_weather': [("(k==='rad'&&!src?'Choose the weather first", "(!src?'Choose the weather first")],   # with the place: ... direct sun runs without it
    # ---- 3. direct sun ----
    'bvh_left_only': [("if(H.L[id]>=0){st[sp++]=H.L[id];st[sp++]=H.R[id];continue;}", "if(H.L[id]>=0){st[sp++]=H.L[id];continue;}")],   # the floor's direct sun hours, exactly the canyon's
    'span_ignored': [("var step=bimStd('app.solar',o.span==='year'?'step_year':'step_day');", "var step=bimStd('app.solar','step_day');")],   # the year: every hour
    'numpy_not_loaded': [("if(!NP)p=p.then(function(){return PY.loadPackage('numpy').then(function(){NP=true;});});", "")],   # the first study asks for numpy and gendaymtx
    # ---- 4. radiation ----
    'north_south_swapped': [("out.push([Math.cos(e)*Math.sin(a),Math.sin(e),-Math.cos(e)*Math.cos(a)]);", "out.push([Math.cos(e)*Math.sin(a),Math.sin(e),Math.cos(e)*Math.cos(a)]);")],   # each face: ... with Ladybug's directions
    'no_ground': [("    if(ground){L=out.length;for(i=0;i<L;i++)out.push([-out[i][0],-out[i][1],-out[i][2]]);}", "")],   # each face: ... and the ground's
    'cosine_dropped': [("M[(i-a)*nv+j]=cosine?c:1;}", "M[(i-a)*nv+j]=1;}")],   # each face: the sky's patches times the cosine
    'underside_kept': [("        if(fc.n[1]<-0.99)return;   /* the underside on the ground, as V143 leaves it */\n", "")],   # the floor's underside left out
    # ---- 5. true north ----
    'north_turned_back': [("a=Math.atan2(x,y)+tn*r;", "a=Math.atan2(x,y)-tn*r;")],   # each face again, the patches turned by true north
    # ---- 6. Reinhart ----
    'density_ignored': [("pre:{fn:'sky',args:{density:o.dense?1:0,", "pre:{fn:'sky',args:{density:0,")],   # 577 patches, their 1154 directions
    # ---- 7. kept ----
    'stamp_counts_only': [("      for(j=0;j<m.v.length;j++)for(k=0;k<3;k++)h=(h*31+Math.round((m.v[j][k]||0)*1000))|0;}", "      }")],   # the box raised: out of date
    'stamp_with_date': [("    var stamp=bimResKeyFrom(bimSimStamp(),'sunhours'),t0=Date.now(),", "    var stamp=bimSimStamp(),t0=Date.now(),")],   # not out of date after its run; a new date: radiation still current
    'std_not_kept': [("ms:Date.now()-t0,src:src?src.key:null,stamp:stamp,std:bimStdStamp(['app.solar']),", "ms:Date.now()-t0,src:src?src.key:null,stamp:stamp,")],   # kept with the project: ... the standards
    # ---- 9. drawn ----
    'backfaces_drawn': [("if(flat?vdot(n,V.d)>=0:vdot(n,[eye[0]-c[0],eye[1]-c[1],eye[2]-c[2]])<=0)continue;", "if(flat?vdot(n,V.d)<0:vdot(n,[eye[0]-c[0],eye[1]-c[1],eye[2]-c[2]])>0)continue;")],   # the faces facing the eye ..., the rest culled
    'legend_under_dock': [("lx=Math.max(sr.x+12,sr.x+sr.w-lw-12),ly=Math.max(sr.y+12,sr.y+sr.h-lh-12),", "lx=W-lw-14,ly=H-lh-14,")],   # the legend inside the view's safe area
    'colours_not_ladybugs': [("var BIM_LBS_RAMP={rad:['#4b6ba9',", "var BIM_LBS_RAMP={rad:['#2c3e78',")],   # Ladybug's colours
    # ---- 10. a runtime file ----
    'gendaymtx_unchecked': [("            if(hex(h)!==RAD.h)throw new Error(RAD.f+' does not match its SHA-256');\n", "")],   # gendaymtx changed by one byte: refused, said
    # ---- 11. a phone ----
    'rows_unlisted': [("    bimLbsCards().forEach(function(c){C.push(c);});   /* __acad3dV172c: and its studies on the model */\n", "")],   # the row's buttons on a phone
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV172c' in txt
out.write_text(txt, encoding='utf-8')
