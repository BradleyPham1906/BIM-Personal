"""falsify_phase171d.py -- break the V171d build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase171d_sun_path_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- 1. the records ----
    'marker_lost': [("window.__acad3dV171d='spa,dome,", "window.__acad3dV171d='dome,")],   # the V171d marker
    # ---- 2. the math ----
    'refraction_lost': [("    return {elevation:AE+AF,geomElevation:AE,", "    return {elevation:AE,geomElevation:AE,")],   # NOAA's spreadsheet ... within 1e-6
    # ---- 3. the zones ----
    'zone_one_round': [("      for(k=0;k<3;k++){   /* the instant whose local time it is", "      for(k=0;k<1;k++){   /* the instant whose local time it is")],   # fifteen offsets ... either side of its two changes
    'zone_std_max': [("    return a===null||b===null?null:Math.min(a,b);", "    return a===null||b===null?null:Math.max(a,b);")],   # standard time, the lower of mid-January's and mid-July's
    # ---- 4. the climate's offset ----
    'climate_request_day': [("{A3D.site.sun.tz=zstd!==null?zstd:C.tz;A3D.site.sun.tzAuto=true;tzSet=true;}", "{A3D.site.sun.tz=C.tz;A3D.site.sun.tzAuto=true;tzSet=true;}")],   # fetched on a summer day ... its standard time
    'zone_not_kept': [("        if(tzn)A3D.site.sun.zone=tzn;\n", "")],   # the zone kept
    'typed_not_owners': [("    if(field==='tz')delete A3D.site.sun.tzAuto;", "    if(field==='tz')A3D.site.sun.tzAuto=true;")],   # an offset typed is the owner's
    'no_dst_row': [("    loc+=bimSunZoneRows();   /* __acad3dV171d: the zone, and daylight saving */", "")],   # Properties > Site > Location: the time zone, and Daylight Saving
    # ---- 5. the dome ----
    'dome_south_north': [("    return [S.c[0]+R*Math.cos(e)*Math.sin(a),S.y+R*Math.sin(e),S.c[1]-R*Math.cos(e)*Math.cos(a)];", "    return [S.c[0]+R*Math.cos(e)*Math.sin(a),S.y+R*Math.sin(e),S.c[1]+R*Math.cos(e)*Math.cos(a)];")],   # the paths point for point
    'paths_every_15': [("    for(m=0;m<1440;m+=10){\n      sp=bimSunCalc(st.lat,st.lon,tz,dd,bimPad2(m/60)+':'+bimPad2(m%60));\n      if(!sp||!(sp.elevation>0))continue;\n      p=bimDgDome(S,R,sp);pts.push(p);",
                        "    for(m=0;m<1440;m+=15){\n      sp=bimSunCalc(st.lat,st.lon,tz,dd,bimPad2(m/60)+':'+bimPad2(m%60));\n      if(!sp||!(sp.elevation>0))continue;\n      p=bimDgDome(S,R,sp);pts.push(p);")],   # every 10 minutes the sun is up
    'owner_z_flipped': [("    return [R*Math.cos(e)*Math.sin(a),R*Math.sin(e),R*Math.cos(e)*Math.cos(a)];", "    return [R*Math.cos(e)*Math.sin(a),R*Math.sin(e),-R*Math.cos(e)*Math.cos(a)];")],   # in the owner's axes
    'angles_swapped': [("      lb:[{t:'A '+bimDispNum(now.azimuth,1)+'\\u00b0'", "      lb:[{t:'A '+bimDispNum(now.elevation,1)+'\\u00b0'")],   # its angles ... named
    'analemma_monthly': [("    for(d=0;d<366;d+=2){", "    for(d=0;d<366;d+=30){")],   # the analemma ... every second day
    'today_twice': [("    var td=st.date,same=bimSunNearDrawn(td),", "    var td=st.date,same=false,")],   # the day studied ... not drawn twice
    # ---- 6. daylight saving ----
    'dst_ignored': [("    if(z.dst){o=bimSunZoneOff(z.zone,dateStr,timeStr||'12:00');if(o!==null)return o;}", "    if(0){o=bimSunZoneOff(z.zone,dateStr,timeStr||'12:00');if(o!==null)return o;}")],   # June's hours at UTC-4
    'dst_word_lost': [("(z.dst?(std!==null&&tz>std?', daylight saving time':', standard time'):'')", "''")],   # daylight saving time ... standard time
    # ---- 7. a place tried ----
    'trial_ignored': [("    if(bimSunTrying()){st.lat=A3D_SUNX.lat;st.lon=A3D_SUNX.lon;", "    if(0){st.lat=A3D_SUNX.lat;st.lon=A3D_SUNX.lon;")],   # 60 deg north tried
    'trial_heat_drawn': [("    if(st.trial)return {quads:[],half:half,rows:[['Not drawn'", "    if(0)return {quads:[],half:half,rows:[['Not drawn'")],   # the temperature not drawn
    'no_trial_banner': [("      if(st.trial)h+='<p class=\"a3d-awp-note a3d-sun-trial\">", "      if(0)h+='<p class=\"a3d-awp-note a3d-sun-trial\">")],   # let go: the panel says it is a place tried
    'leave_keeps_trial': [("    A3D_SUNX.lat=null;A3D_SUNX.lon=null;A3D_SUNX.date=null;A3D_SUNX.time=null;   /* __acad3dV171d: a place tried ends with Analyze */\n", "")],   # leaving Analyze ends a place tried
    # ---- 8. one clock ----
    'no_sync_in_frame': [("    if(!over){try{bimDgSunSync();}", "    if(0){try{bimDgSunSync();}")],   # the date and time changed: ... follow, with no run
    'run_keeps_key': [("x.dg.info=e.info||{};delete x.dg.sk;   /* __acad3dV171d", "x.dg.info=e.info||{};   /* __acad3dV171d")],   # the paths point for point (after Analyze site again)
    'colour_lost': [("        if(JSON.stringify(old.s)===JSON.stringify(x.dg.s||{}))x.dg.s=e.s||{};", "        x.dg.s=e.s||{};")],   # a path the owner coloured keeps its colour
    'year_too_fast': [("  var BIM_ANIM_YEAR={secs:36,hold:1.2};", "  var BIM_ANIM_YEAR={secs:30,hold:1.2};")],   # Play through the year ... 36 s for the year
    'year_date_unused': [("if(A3D_ANIM.sunDate)st.date=A3D_ANIM.sunDate;", "")],   # Play through the year: the date
    'half_flipped': [("  function bimSunHalf(d){var md=String(d||'').slice(5);return md>='06-21'&&md<'12-21'?'jd':'dj';}", "  function bimSunHalf(d){var md=String(d||'').slice(5);return md>='06-21'&&md<'12-21'?'dj':'jd';}")],   # the mesh's half-year turning at the solstices
    'shadow_on_study_date': [("dt=mv?bimSunStudy().date:(L&&L.date),sun;", "dt=mv?bimSunSettings().date:(L&&L.date),sun;")],   # the model's shadow follows the date
    # ---- 9. the words ----
    'dots_not_kept': [("        A3D_DG.dotKeep.push([sp[0]-5,sp[1]-5,10,10]);\n", "")],   # no word over a labelled dot
    'hours_a_line_away': [("pri:sel?0:4,a:a,sel:sel,cap:cap,cands:bimDgBeside(sp)});", "pri:sel?0:4,a:a,sel:sel,cap:cap,cands:null});")],   # each hour's word beside its own dot
    'names_nowhere': [("    for(i=0;i<P.length;i++)C.push([P[i][0],P[i][1]-15,'center'],[P[i][0],P[i][1]+15,'center'],[P[i][0],P[i][1],'center']);", "")],   # a path's name on its path
    # ---- 10. the panel ----
    'no_formula': [("'<p class=\"a3d-awp-note a3d-sun-f\">X = R cos \\u03b1 sin A, Y = R sin \\u03b1, Z = R cos \\u03b1 cos A,", "'<p class=\"a3d-awp-note a3d-sun-f\">The point,")],   # the formula, in the owner's axes
    'time_slider_coarse': [("bimSunSliderHtml('time','Time',0,1435,5,", "bimSunSliderHtml('time','Time',0,1435,15,")],   # four sliders
    'input_commits': [("      try{bimSunSlide(k,e.value,false);}catch(eS)", "      try{bimSunSlide(k,e.value,true);}catch(eS)")],   # the time slider moving: ... no undo step
    'input_redraws': [("    paint();bimSunPanelLive();\n    return true;\n  }\n  /* Play's two ways", "    paint();bimAwRefresh();\n    return true;\n  }\n  /* Play's two ways")],   # the panel not drawn again
    'focus_lost': [("          setTimeout(function(){var s=el.propsbody.querySelector('[data-sunsl=\"'+k+'\"]');if(s&&document.activeElement!==s)s.focus();},0);\n", "")],   # the slider still in the hand
    'north_always': [("N=st.lat>=0,nm=", "N=true,nm=")],   # 33.9 deg south tried: the summer solstice is December's
    'shadow_times_height': [("sh=f&&f.noonAlt>0?10/Math.tan(f.noonAlt*Math.PI/180):null;", "sh=f&&f.noonAlt>0?10*Math.tan(f.noonAlt*Math.PI/180):null;")],   # a 10 m building's shadow
    'rise_bearing_wrong': [("f.riseAz=bimSunCalc(st.lat,st.lon,tz,dd,bimHHMM(r.sunrise)).azimuth;", "f.riseAz=bimSunCalc(st.lat,st.lon,tz,dd,bimHHMM(r.sunset)).azimuth;")],   # each with sunrise and its bearing
    'dst_button_dead': [("    if(a==='dst'){z=bimSunZone();return bimSetSun('dst',z.dst?'':'auto');}", "    if(a==='dst'){z=bimSunZone();return false;}")],   # daylight saving from the panel
    'mode_not_pressed': [("data-awact=\"sun:mode:year\" aria-pressed=\"'+y+'\">", "data-awact=\"sun:mode:year\" aria-pressed=\"false\">")],   # Play through the year chosen, pressed
    'polar_equidistant': [("  function bimSunPolarPt(a,az){var t=az*Math.PI/180,r=116*Math.tan((90-Math.max(0,a))*Math.PI/360);", "  function bimSunPolarPt(a,az){var t=az*Math.PI/180,r=116*(90-Math.max(0,a))/90;")],   # the two diagrams
    'panel_not_live': [("      if(over&&A3D_AW.on&&!cap)bimSunPanelLive();", "")],   # playing, the panel follows the clock
    'heat_key_short': [("'<div class=\"a3d-awp-key a3d-sun-heat\">'+BIM_HEAT_SHORT.map(", "'<div class=\"a3d-awp-key a3d-sun-heat\">'+BIM_HEAT_SHORT.slice(1).map(")],   # the temperature's eleven bands
    # ---- 11. the mesh ----
    'mesh_study_clock': [("        m=c*20;sp=bimSunCalc(st.lat,st.lon,C.tz,yr+'-'+rows[j]", "        m=c*20;sp=bimSunCalc(st.lat,st.lon,st.tz,yr+'-'+rows[j]")],   # its corners the sun's places by the climate's own clock
    'mesh_colour_off': [("  function bimSunHeatCol(v){var c=BIM_HEAT_COL[bimClbHeatClass(v)];", "  function bimSunHeatCol(v){var c=BIM_HEAT_COL[Math.min(10,bimClbHeatClass(v)+1)];")],   # in the board's colours
    'heat_at_study_hour': [("u=Date.UTC(+dm[1],+dm[2]-1,+dm[3],+tt[1],+tt[2])-tz*3600000+C.tz*3600000;", "u=Date.UTC(+dm[1],+dm[2]-1,+dm[3],+tt[1],+tt[2]);")],   # where the sun is now: its band's mean at the climate's hour
    # ---- 12. a phone ----
    'phone_slider_small': [("@media(pointer:coarse){.a3d-sun-slr input[type=range]{min-height:36px}}", "@media(pointer:coarse){.a3d-sun-slr input[type=range]{min-height:24px}}")],   # the sliders a finger's height
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV171d' in txt
out.write_text(txt, encoding='utf-8')
