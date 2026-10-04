"""falsify_phase143.py -- break the V143 build one way at a time, keeping the marker.

Each variant takes back one thing V143 does, and the V143 suite must fail on every one of them.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- sun hours
    'sunhours_no_shadows': [("      for(i=0;i<list.length;i++)each(list[i],function(p){return bimShadowPoint(p,s,g);},shade,stamp);\n", "")],
    'sunhours_roof_counted': [("    for(k=0;k<N;k++){if(roof[k])continue;nG++;", "    for(k=0;k<N;k++){nG++;")],
    'sunhours_half_steps': [("      for(k=0;k<N;k++)if(shade[k]!==stamp)lit[k]+=step/60;", "      for(k=0;k<N;k++)if(shade[k]!==stamp)lit[k]+=step/120;")],
    'sunhours_low_sun_dropped': [("      if(s&&s.elevation>0)out.push({m:m,sun:s});", "      if(s&&s.elevation>5)out.push({m:m,sun:s});")],
    # ---- solar
    'solar_no_airmass_power': [("Math.pow(0.7,Math.pow(bimSolarAirMass(el),0.678))", "Math.pow(0.7,bimSolarAirMass(el))")],
    'solar_sky_not_tilted': [("var beam=0,sky=0,seen=0,i,s,c,o,sv=(1+fc.n[1])/2;", "var beam=0,sky=0,seen=0,i,s,c,o,sv=1;")],
    'solar_no_shading': [("      if(!noShade&&bimRayBlocked(o,s.v,occ))continue;", "")],
    'solar_cosine_ignored': [("      beam+=s.dni*c*s.w;seen++;", "      beam+=s.dni*s.w;seen++;")],
    'solar_month_unweighted': [("w:dm[mo]*0.5});", "w:15});")],
    'solar_box_only': [("      for(k=0;k<occ[i].tris.length;k++)if(bimRayTri(o,d,occ[i].tris[k]))return true;", "      return true;")],
    'solar_selection_nothing': [("    return T.length?T:A3D.objs.filter(solid);", "    return ids&&ids.length?T:A3D.objs.filter(solid);")],
    'solar_not_saved': [("          if(o)o.solar={roof:", "          if(false)o.solar={roof:")],
    'solar_not_in_lens': [("      if(o.solar.roof!==null)out['Solar on roof (kWh/m2 a year)']=o.solar.roof;\n", "")],
    # ---- rain
    'rain_no_fill': [("        F[nk]=Math.max(H[nk],F[c]+eps*DL[d]);", "        F[nk]=H[nk];")],
    'rain_d8_uphill': [("        var sl=(F[k]-F[q])/(DL[d]*cell);if(sl>bs+1e-12&&F[k]-H[k]<1e-3){bs=sl;best=d;}", "        var sl=(F[q]-F[k])/(DL[d]*cell);if(sl>bs+1e-12&&F[k]-H[k]<1e-3){bs=sl;best=d;}")],
    'rain_no_accumulation': [("      if(ok[t2])acc[t2]+=acc[k];", "")],
    'rain_ponds_unjoined': [("          if(ok[v]&&!pid[v]&&F[v]-H[v]>=pmin){pid[v]=ponds.length+1;stack.push(v);}}", "          }")],
    'rain_volume_no_area': [("pool.volume+=dd*cell*cell;", "pool.volume+=dd;")],
    # ---- the tab and the commands
    'no_sim_section': [("      '<div class=\"a3d-anzhead a3d-anzsimhd\"><span class=\"a3d-anzttl0\">Simulation</span></div>'+\n", "")],
    'never_stale': [("  function bimSimStale(r){return !!(r&&r.stamp!==bimSimStamp());}", "  function bimSimStale(r){return false;}")],
    'clear_keeps_solar': [("    if(!which||which==='solar')A3D.objs.forEach(function(o){if(o.solar){delete o.solar;n++;}});\n", "")],
    'colour_button_dead': [("    else if(k==='solar:colour'){bimLensSet('prop','Solar on roof (kWh/m2 a year)');}", "    else if(k==='solar:colour'){}")],
    'not_drawn': [("    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */\n", "")],
    'no_commands': [("    sunhours:function(){bimSunHoursCommand();},                   /* __acad3dV143 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV143' in txt
out.write_text(txt, encoding='utf-8')
