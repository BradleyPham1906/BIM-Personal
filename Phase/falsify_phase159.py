"""falsify_phase159.py -- break the V159 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # Analyze holds Site analysis
    'no_view_switch': [("      '<button type=\"button\" role=\"tab\" class=\"a3d-anzviewbtn\" data-anzview=\"site\" aria-selected=\"'+(v==='site')+'\">Site analysis</button></div>';", "      '</div>';")],
    'view_not_remembered': [("    try{localStorage.setItem('acad3dAnzView',v);}catch(eS){}", "")],
    'site_command_old_tab': [("    siteanalysis:function(){bimAnzView('site');},", "    siteanalysis:function(){bimShellSetTab('analyze');},")],
    # the requests and the numbers
    'nine_years': [("var BIM_CLIM_YEARS=10,", "var BIM_CLIM_YEARS=9,")],
    'wind_in_kmh': [("wind_speed_unit:'ms',", "")],
    'mj_not_converted': [("if(bimClimNum(sw))K.sw.push(sw/3.6);", "if(bimClimNum(sw))K.sw.push(sw);")],
    'percentile_95': [("tx90:bimClimPct(K2.tx,0.9)", "tx90:bimClimPct(K2.tx,0.95)")],
    'base_15_5': [("BIM_CLIM_BASE=18,", "BIM_CLIM_BASE=15.5,")],
    'koppen_not_polar_first': [("    if(Th<=10)c=Th>0?'ET':'EF';   /* polar first: a cold ice cap is not a desert */\n    else if(MAP<10*Pth)", "    if(MAP<10*Pth)")],
    'koppen_a_at_24': [("var t3=Th>=22?'a':", "var t3=Th>=24?'a':")],
    'calm_ignored': [("BIM_CLIM_CALM=0.5,", "BIM_CLIM_CALM=0,")],
    'sector_floor': [("var sec=Math.round(((wd%360)+360)%360/22.5)%16", "var sec=Math.floor(((wd%360)+360)%360/22.5)%16")],
    'comfort_rh_ignored': [("t<=BIM_CLIM_COMFORT.t1&&rh>=BIM_CLIM_COMFORT.rh0&&rh<=BIM_CLIM_COMFORT.rh1)inC++;", "t<=BIM_CLIM_COMFORT.t1)inC++;")],
    'pressure_wrong': [("return 1000*0.622*pv/(101325-pv);", "return 1000*0.622*pv/(90000-pv);")],
    'who_25': [("BIM_CLIM_WHO24=15,", "BIM_CLIM_WHO24=25,")],
    'quakes_by_distance': [("E.sort(function(a,b){return b.m-a.m||a.km-b.km;});", "E.sort(function(a,b){return a.km-b.km;});")],
    'quake_m5_anywhere': [("(e.m>=6)||(e.m>=5&&e.km<=50))?2:1", "(e.m>=6)||(e.m>=5))?2:1")],
    # findings, undo, failures
    'findings_not_filled': [("      A3D.site.risk=K;\n      bimSaFill(true);", "      A3D.site.risk=K;")],
    'apply_not_undoable': [("    if(!D&&!Hh&&!Q&&!E){a3dToast('No climate or risk data: '+bad.join('; '));return {error:bad.join('; ')};}\n    pushUndo();", "    if(!D&&!Hh&&!Q&&!E){a3dToast('No climate or risk data: '+bad.join('; '));return {error:bad.join('; ')};}")],
    'failure_wipes_air': [("      if(Q){K.air=Q;K.airSrc='CAMS (Copernicus), via Open-Meteo';}", "      K.air=Q;K.airSrc='CAMS (Copernicus), via Open-Meteo';")],
    'all_down_applies': [("    if(!D&&!Hh&&!Q&&!E){a3dToast('No climate or risk data: '+bad.join('; '));return {error:bad.join('; ')};}", "")],
    'busy_ignored': [("    if(A3D_CLIM.busy){a3dToast('The climate and risk data are already on their way');return null;}", "")],
    # the board
    'state_colour_only': [("    return '<div class=\"a3d-clb-st\"><svg viewBox=\"0 0 16 16\" style=\"color:'+S[1]+'\" aria-hidden=\"true\">'+S[2]+'</svg>'+S[0]+'</div>';", "    return '<div class=\"a3d-clb-st\" style=\"color:'+S[1]+'\">\\u25cf</div>';")],
    'tables_never': [(".a3d-clb.tables .a3d-clb-table{display:table}", "")],
    'heat_not_merged': [("        if(d<days&&k===k0){run++;continue;}", "")],
    'no_direct_label': [("'<text class=\"lb\" x=\"'+bimClbF(x(ih))+'\" y=\"'+bimClbF(y(M[ih].tx)-9)+'\" text-anchor=\"middle\">'+bimClbNum(M[ih].tx)+'°</text>';", "'';")],
    'esc_dead': [("  document.addEventListener('keydown',function(ev){if(A3D_CLB.open&&ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimClbClose();}},true);", "")],
    'print_shows_app': [("  body.a3d-clb-open>*:not(.a3d-clb){display:none!important}\n", "")],
    'phone_not_narrow': [("    A3D_CLB.narrow=window.innerWidth<760;", "    A3D_CLB.narrow=false;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV159' in txt
out.write_text(txt, encoding='utf-8')
