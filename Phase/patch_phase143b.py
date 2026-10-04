"""patch_phase143b.py -- V143: Simulation in the Analyze tab.

- A Simulation section under the analyses: Sun Hours, Solar, Rain on Terrain -- each saying what
  it shows (and when the model has changed since), with Run, Clear and its settings; a legend for
  the sun hours; Colour By solar.
- A building's LOD group shows its solar result.
- Commands: SUNHOURS, SOLAR, RAINFLOW, SIMCLEAR. The marker."""
NAME = 'patch_phase143b.py'
BASE = '73b52ef2536b2145a844e754a3ab23349a0d6a1bd48f8ce458247bfe2dbb1147'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""  function bimAnzCard(id,title,status,acts,state){
    return '<div class="a3d-anzcard" data-anzcard="'+id+'"><div class="a3d-anzhd"><span class="a3d-anzttl">'+bimEsc(title)+'</span>'+
      (state?'<span class="a3d-anzstate a3d-anzstate-'+state+'">'+(state==='on'?'On':state==='warn'?'Check':state==='fail'?'Problems':'Off')+'</span>':'')+'</div>'+
      '<div class="a3d-anzst">'+bimEsc(status)+'</div><div class="a3d-anzacts">'""",
    """  function bimAnzCard(id,title,status,acts,state,extra){
    return '<div class="a3d-anzcard" data-anzcard="'+id+'"><div class="a3d-anzhd"><span class="a3d-anzttl">'+bimEsc(title)+'</span>'+
      (state?'<span class="a3d-anzstate a3d-anzstate-'+state+'">'+(state==='on'?'On':state==='warn'?'Check':state==='fail'?'Problems':state==='stale'?'Out of date':state==='busy'?'Running':'Off')+'</span>':'')+'</div>'+
      '<div class="a3d-anzst">'+bimEsc(status)+'</div>'+(extra||'')+'<div class="a3d-anzacts">'""")
rep("""      acts:[{act:'open:Statistics',label:'Open'}]});
    return C;
  }""", """      acts:[{act:'open:Statistics',label:'Open'}]});
    /* __acad3dV143: the simulations */
    var miss=bimSunNow().missing,ms=miss?'Set the site '+miss.join(', ')+' first (Site: Location)':'',sh=A3D_SIM.sun,so=A3D_SIM.solar,ra=A3D_SIM.rain;
    var nSol=bimSolarTargets(null).length,ter=bimRainTerrain(null);
    C.push({id:'sunhours',sim:true,title:'Sun Hours',state:sh?(bimSimStale(sh)?'stale':'on'):'off',
      status:ms||(sh?'Ground in direct sun on '+sh.date+': '+bimDispNum(sh.min,1)+' to '+bimDispNum(sh.max,1)+' h of '+bimDispNum(sh.day,1)+' h; '+Math.round(sh.sixPlus*100)+'% has 6 h or more'+(bimSimStale(sh)?' (the model or the date has changed since)':''):
        'Hours of direct sun on the ground through the site\\'s date, every 15 minutes'),
      extra:sh?'<div class="a3d-anzleg"><span>'+bimDispNum(0,0)+' h</span><span class="a3d-anzramp">'+BIM_SIM_RAMP.map(function(c){return '<i style="background:'+c+'"></i>';}).join('')+'</span><span>'+bimDispNum(sh.day,1)+' h</span></div>':'',
      acts:[{act:'sunhours:run',label:sh?'Run Again':'Run',pri:true,off:ms},{act:'sim:clear:sun',label:'Clear',off:sh?'':'Not run'},{act:'open:Location',label:'Date'}]});
    C.push({id:'solar',sim:true,title:'Solar on Roofs and Facades',state:A3D_SIM.busy==='solar'?'busy':so?(bimSimStale(so)?'stale':'on'):'off',
      status:ms||(A3D_SIM.busy==='solar'?'Running ...':so?so.count+' solid'+(so.count===1?'':'s')+(so.roofMean!==null?': roofs '+Math.round(so.roofMean)+' kWh/m\\u00b2 a year on average':'')+
        ' (clear sky, no clouds'+(so.shaded?', shaded by the others':'')+')'+(bimSimStale(so)?'; the model has changed since':''):
        (nSol?'A clear-sky year of sun on the faces of '+nSol+' solid'+(nSol===1?'':'s')+' (the selection, if any)':'No buildings or solids yet')),
      acts:[{act:'solar:run',label:so?'Run Again':'Run',pri:true,off:ms||(nSol?'':'No buildings or solids yet')||(A3D_SIM.busy?'Running':'')},
        {act:'solar:colour',label:'Colour By',off:so?'':'Run it first'},{act:'sim:clear:solar',label:'Clear',off:so?'':'Not run'}]});
    C.push({id:'rain',sim:true,title:'Rain on Terrain',state:ra?(bimSimStale(ra)?'stale':'on'):'off',
      status:ra?ra.name+': '+ra.ponds.length+' pond'+(ra.ponds.length===1?'':'s')+(ra.ponds.length?', '+bimDispNum(ra.pondVolume,1)+' m\\u00b3 held, the deepest '+bimDispNum(ra.ponds[0].depth,2)+' m':'')+
        '; flow lines where '+bimDispNum(ra.threshold*ra.cell*ra.cell,0)+' m\\u00b2 or more drains'+(bimSimStale(ra)?' (the surface has changed since)':''):
        (ter?'Where rain runs and ponds on '+ter.name:'No terrain yet: make one with SURVEY, or get the site context'),
      acts:[{act:'rain:run',label:ra?'Run Again':'Run',pri:true,off:ter?'':'No terrain yet'},{act:'sim:clear:rain',label:'Clear',off:ra?'':'Not run'}]});
    return C;
  }""")
rep("""    return '<div class="a3d-anz"><div class="a3d-anzhead"><span class="a3d-anzttl0">Analyze</span><span class="a3d-anzcount">'+C.length+' analyses</span></div>'+
      '<div class="a3d-anzlist">'+C.map(function(c){return bimAnzCard(c.id,c.title,c.status,c.acts,c.state);}).join('')+'</div></div>';""",
    """    var A=C.filter(function(c){return !c.sim;}),S=C.filter(function(c){return c.sim;});   /* __acad3dV143 */
    return '<div class="a3d-anz"><div class="a3d-anzhead"><span class="a3d-anzttl0">Analyze</span><span class="a3d-anzcount">'+A.length+' analyses, '+S.length+' simulations</span></div>'+
      '<div class="a3d-anzlist">'+A.map(function(c){return bimAnzCard(c.id,c.title,c.status,c.acts,c.state);}).join('')+'</div>'+
      '<div class="a3d-anzhead a3d-anzsimhd"><span class="a3d-anzttl0">Simulation</span></div>'+
      '<div class="a3d-anzlist">'+S.map(function(c){return bimAnzCard(c.id,c.title,c.status,c.acts,c.state,c.extra);}).join('')+'</div></div>';""")
rep("""    else if(k==='lod:cityjson')bimCityJsonExport();
    else return false;""", """    else if(k==='lod:cityjson')bimCityJsonExport();
    else if(k==='sunhours:run')bimSunHoursCommand();   /* __acad3dV143 */
    else if(k==='solar:run'){bimSolarCommand();bimAnalyzeRefresh();return true;}
    else if(k==='solar:colour'){bimLensSet('prop','Solar on roof (kWh/m2 a year)');}
    else if(k==='rain:run')bimRainCommand(null);
    else if(k.indexOf('sim:clear:')===0)bimSimClear(k.slice(10));
    else return false;""")
# a building's solar, in its LOD group
rep("""    if(c&&c.building)r+=bimPropText('Building',(c.building.name||'unnamed')+' ('+c.building.osm+' '+c.building.id+')');""",
    """    if(c&&c.building)r+=bimPropText('Building',(c.building.name||'unnamed')+' ('+c.building.osm+' '+c.building.id+')');
    if(o.solar)r+=bimPropText('Solar',(o.solar.roof!==null?'roof '+o.solar.roof+' kWh/m\\u00b2 a year ('+o.solar.roofKwh+' kWh)':'no roof')+   /* __acad3dV143 */
      (o.solar.facade!==null?', facades '+o.solar.facade+' kWh/m\\u00b2 a year':'')+'; clear sky, '+o.solar.computed);""")
rep("""    ['DOCS',['GUIDE','MANUAL','USERGUIDE'],'docs',""", """    ['SUNHOURS',['SUNLIGHTHOURS','DAYLIGHTHOURS'],'sunhours','Hours of direct sun on the ground through the site\\'s date, drawn over the plan'],   /* __acad3dV143 */
    ['SOLAR',['SOLARRADIATION','INSOLATION','IRRADIATION'],'solar','A clear-sky year of sun on the roofs and facades: kWh/m2 on each building, shaded by the others'],
    ['RAINFLOW',['RAIN','DRAINAGE','PONDING','RUNOFF'],'rainflow','Where rain runs and ponds on the terrain: flow lines and ponds over the plan'],
    ['SIMCLEAR',['CLEARSIM'],'simclear','Clear the simulations from the drawing'],
    ['DOCS',['GUIDE','MANUAL','USERGUIDE'],'docs',""")
rep("""    docs:function(){bimDocsOpen('index.html');},                  /* __acad3dV142 */""", """    docs:function(){bimDocsOpen('index.html');},                  /* __acad3dV142 */
    sunhours:function(){bimSunHoursCommand();},                   /* __acad3dV143 */
    solar:function(){bimSolarCommand();},
    rainflow:function(){bimRainCommand(null);},
    simclear:function(){var n=bimSimClear();a3dToast(n?'Simulations cleared':'No simulation to clear');},""")
rep("""    DOCS:'help documentation manual guide tutorial learn how reference f1',   /* __acad3dV142 */""",
    """    DOCS:'help documentation manual guide tutorial learn how reference f1',   /* __acad3dV142 */
    SUNHOURS:'sun hours sunlight shadow study daylight right to light overshadowing simulation',   /* __acad3dV143 */
    SOLAR:'solar radiation irradiance energy photovoltaic pv roof potential kwh sun simulation',
    RAINFLOW:'rain water flow runoff drainage ponding flooding watershed terrain simulation',
    SIMCLEAR:'clear simulation remove results',""")
rep(""".a3d-lodtag{""", """.a3d-anzsimhd{margin-top:16px}
.a3d-anzleg{display:flex;align-items:center;gap:6px;font-size:11px;color:#9aa5b0;margin:0 0 7px}
.a3d-anzramp{display:flex;flex:1;height:8px;border-radius:3px;overflow:hidden}.a3d-anzramp i{flex:1}
.a3d-anzstate-stale{background:rgba(255,183,77,.18);color:#ffb74d}.a3d-anzstate-busy{background:rgba(110,160,255,.18);color:#8fb4ff}
.a3d-lodtag{""")
rep("""  var BIM_APP_VERSION={v:'V142',date:'2026-10-04'};""", """  var BIM_APP_VERSION={v:'V143',date:'2026-10-04'};   /* __acad3dV143 */""")
rep("""  window.__acad3dV142='""", """  window.__acad3dV143='sunhours,solarclearsky,solarshading,solarlens,rainfill,rainponds,rainflowlines,simcards,simcommands,simstale';
  window.__acad3dV142='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
