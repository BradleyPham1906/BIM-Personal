"""falsify_phase107.py -- break the V107 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')
AB = "var AB=(((mins+V+4*lon-60*tz)%1440)+1440)%1440;"

VARIANTS = {
    'eqtime_sign': [(AB, "var AB=(((mins-V+4*lon-60*tz)%1440)+1440)%1440;")],
    'longitude_sign': [(AB, "var AB=(((mins+V-4*lon-60*tz)%1440)+1440)%1440;")],
    'utc_offset_ignored': [("+mins/1440-tz/24;", "+mins/1440;")],
    'no_refraction': [("return {elevation:AE+AF,", "return {elevation:AE,")],
    'azimuth_branches_swapped': [("var AH=AC>0?((ac+180)%360):(((540-ac)%360)+360)%360;", "var AH=AC>0?(((540-ac)%360)+360)%360:((ac+180)%360);")],
    'true_north_ignored': [("var a=(sun.azimuth+bimTrueNorthDeg())*Math.PI/180,e=sun.elevation*Math.PI/180;", "var a=sun.azimuth*Math.PI/180,e=sun.elevation*Math.PI/180;")],
    'shadow_toward_sun': [("return [p[0]-s[0]*h/s[1],p[2]-s[2]*h/s[1]];}", "return [p[0]+s[0]*h/s[1],p[2]+s[2]*h/s[1]];}")],
    'ground_slab_casts': [("      if(o.bim&&o.bim.type==='floor'&&top<=g+0.5)continue;\n", "")],
    'shadows_at_night': [("    if(!(sun.elevation>0)){A3D.lastShadows={night:true,", "    if(false){A3D.lastShadows={night:true,")],
    'missing_not_reported': [("    if(sun.missing){A3D.lastShadows={missing:sun.missing};return;}", "    if(sun.missing){return;}")],
    'latitude_unchecked': [("      if(v!==''&&(!isFinite(n)||n<lim[0]||n>lim[1])){a3dToast(nm+", "      if(v!==''&&!isFinite(n)){a3dToast(nm+")],
    'settings_not_undoable': [("    pushUndo();\n    A3D.site.sun=A3D.site.sun||{};", "    A3D.site.sun=A3D.site.sun||{};")],
    'properties_not_wired': [("        if(mk==='sunlat'||mk==='sunlon'||mk==='suntz'||mk==='sundate'||mk==='suntime'){bimSetSun(mk.slice(3),mv);return;}   /* __acad3dV107 */\n", "")],
    'sunpath_not_turned': [("      var rad=Math.PI/180,tn=bimTrueNorthDeg()*rad,c=A3D.cam,", "      var rad=Math.PI/180,tn=0,c=A3D.cam,")],
    'sunpath_wrong_solstice': [("[[yr+'-06-21','#ffb347','Jun 21']", "[[yr+'-07-21','#ffb347','Jun 21']")],
    'command_does_nothing': [("    sunstudy:function(){bimToggleSun();},", "    sunstudy:function(){},")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV107' in txt
out.write_text(txt, encoding='utf-8')
