#!/usr/bin/env python3
"""V172b, patch d: Ladybug's standards in the registry, and its rows in Analyze. reference/research-ladybug-weather-comfort.md, 5 and 9.

- The registry (V167) gets four topics in Climate, after app.climate: UTCI's scale and range (utci.org's program and
  poster, P), ASHRAE 55-2023's PMV limits as Ladybug and pythermalcomfort apply them (S: the standard is sold), the
  app's comfort assumptions (Ladybug's own defaults, A), and ASHRAE's design conditions as a station's DDY carries them.
- The analyses read them: bimLbParams passes them to the adapter (src/py/bim_ladybug.py, embedded again: limits and still air for UTCI,
  PPD and still air for PMV, the strategy parameters checked as Ladybug's component checks them), and each result keeps
  the standards it used (bimStdStamp), out of date when they change. The figures say what each run used.
- js/engine/ladybug/panel.js (new): Climate's rows in Analyze -- Weather for Ladybug, then the four analyses, each with
  its numbers, Run, Show on the board and Add to a board.

Run from the repository root: python3 Phase/patch_v172b_d.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

begin('e94f7d4dd223d9516f1a6eb6f0e112cfcc6c04824ba86ef06db1373de5fa003e')   # patch c

# the adapter (src/py/bim_ladybug.py, edited: UTCI's limits and still air, PMV's PPD and still air, the strategy
# parameters checked) written again into js/engine/ladybug/adapter-py.js, as tools/embed_py.py writes it
import subprocess   # noqa: E402
subprocess.check_call([sys.executable, str(ROOT / 'tools' / 'embed_py.py')])

rep('index.html', '<!-- @include js/engine/ladybug/figures.js -->\n',
    '<!-- @include js/engine/ladybug/figures.js -->\n<!-- @include js/engine/ladybug/panel.js -->\n')

# ---- the registry ----
RG = 'js/engine/standards/registry.js'
rep(RG, "ratio:['',''],h:[' h',' h']};",
    "ratio:['',''],h:[' h',' h'],hPa:[' hPa',' hPa'],'W/m2':[' W/m\\u00b2',' W/m\\u00b2'],clo:[' clo',' clo'],met:[' met',' met']};   /* __acad3dV172b */")
rep(RG, "    /* ---- the catalogue for a US and Pennsylvania site: in force there, not applied by the app yet ---- */\n",
    "    /* ---- __acad3dV172b: comfort and design days, for Ladybug's analyses ---- */\n"
    "    {id:'utci',title:'Universal Thermal Climate Index (UTCI): its stress scale and range',pub:'ISB Commission 6 and COST Action 730',kind:'method',area:'Climate',use:'Ladybug\\'s outdoor comfort (UTCI): its figure and its row in Analyze',anywhere:true,\n"
    "      eds:[{id:'utci.a002',name:'UTCI_a002 (Br\\u00f6de, October 2009), its ten stress categories',pub:'2009-10',st:'current',where:'International',adopt:[{at:'*',from:'2009'}],\n"
    "        src:{t:'utci.org: the UTCI program code (UTCI_a002, its ReadMe and Fortran) and the poster Calculating UTCI Equivalent Temperatures (2009)',w:'the ReadMe\\'s range of validity; the poster\\'s assessment scale',u:'https://www.utci.org/',lv:'P',read:'2026-10-31'},\n"
    "        v:[{n:'bands',t:1,u:'C',v:[-40,-27,-13,0,9,26,32,38,46],say:'the bounds of the ten stress categories, from extreme cold stress below the first to extreme heat stress above the last'},\n"
    "          {n:'ta_lo',v:-50,u:'C',say:'the coldest air in the formula\\'s range',lt:'ta_hi'},{n:'ta_hi',v:50,u:'C',say:'the warmest air in its range',gt:'ta_lo'},\n"
    "          {n:'dtr_lo',v:-30,u:'C',say:'the radiant temperature, at most this far below the air\\'s',lt:'dtr_hi'},{n:'dtr_hi',v:70,u:'C',say:'the radiant temperature, at most this far above the air\\'s',gt:'dtr_lo'},\n"
    "          {n:'va_lo',v:0.5,u:'m/s',say:'the lowest wind at 10 m in its range: still air is taken as this',lt:'va_hi'},{n:'va_hi',v:17,u:'m/s',say:'the strongest wind at 10 m in its range',gt:'va_lo'},\n"
    "          {n:'pa_hi',v:50,u:'hPa',say:'the most water vapour pressure in its range'}]}]},\n"
    "    {id:'ashrae.55',title:'Thermal environmental conditions for human occupancy: PMV comfort',pub:'ASHRAE',kind:'standard',area:'Climate',use:'Ladybug\\'s psychrometric chart: its comfort zone',anywhere:true,\n"
    "      eds:[{id:'ashrae.55.2023',name:'ANSI/ASHRAE Standard 55-2023',pub:'2023',st:'current',where:'International practice',adopt:[{at:'*',from:'2023'}],\n"
    "        src:{t:'ASHRAE 55-2023 (sold, and its publisher refuses scripts), as Ladybug\\'s PMVParameter and pythermalcomfort 4.8.0 apply it',w:'the PMV method: PMV within plus or minus 0.5, at most 10% dissatisfied; the cooling effect of moving air above still air',u:'https://github.com/ladybug-tools/ladybug-comfort',lv:'S',read:'2026-10-31'},\n"
    "        v:[{n:'ppd',v:10,u:'%',say:'the most people dissatisfied in the comfort zone (PMV within plus or minus 0.5)'},\n"
    "          {n:'still',v:0.1,u:'m/s',say:'still air: at or below it the air\\'s speed cools no one'}]}]},\n"
    "    {id:'app.comfort',title:'Comfort assumptions',pub:'This app',kind:'assumption',area:'Climate',use:'Ladybug\\'s psychrometric chart and its passive strategies, and UTCI in the sun',anywhere:true,\n"
    "      eds:[{id:'app.comfort.1',name:'The app\\'s comfort assumptions (V172b): Ladybug\\'s own defaults',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],\n"
    "        src:{t:'This app (the owner\\'s choices of 2026-10-31), taking the defaults of Ladybug Tools\\' LB PMV Polygon, LB Passive Strategy Parameters and LB Outdoor Solar MRT',w:'research-ladybug-weather-comfort.md, sections 4 and 10',u:'https://github.com/ladybug-tools/ladybug-grasshopper',lv:'A'},\n"
    "        v:[{n:'clo',t:1,u:'clo',v:[0.5,1.0],say:'the clothing whose comfort zones are merged: summer and winter'},\n"
    "          {n:'met',v:1.1,u:'met',say:'the activity: seated, light office work'},\n"
    "          {n:'day_above',v:12,u:'C',say:'mass and night ventilation: the warmest day above the comfort zone it can still cool'},\n"
    "          {n:'night_below',v:3,u:'C',say:'mass and night ventilation: how far below the comfort zone\\'s warmest the night must fall'},\n"
    "          {n:'fan',v:1,u:'m/s',say:'occupant fans: the air speed they make'},\n"
    "          {n:'balance',v:12.8,u:'C',say:'capture internal heat: the building\\'s balance temperature'},\n"
    "          {n:'solar_cap',v:50,u:'W/m2',say:'passive solar heating: the sun on the window that warms the building by one degree'},\n"
    "          {n:'time_const',v:8,u:'h',say:'the hours a building holds its coolness, or its sun\\'s heat'},\n"
    "          {n:'body_exp',v:1,u:'ratio',say:'UTCI in the sun: the share of the body in the sun'},\n"
    "          {n:'sky_exp',v:1,u:'ratio',say:'UTCI in the sun: the share of the sky in view'},\n"
    "          {n:'ground_ref',v:0.25,u:'ratio',say:'UTCI in the sun: the ground\\'s reflectance'}]}]},\n"
    "    {id:'ashrae.dd',title:'Climatic design conditions',pub:'ASHRAE',kind:'data',area:'Climate',use:'Ladybug\\'s design days',anywhere:true,\n"
    "      eds:[{id:'ashrae.dd.2025',name:'ASHRAE Handbook -- Fundamentals 2025, chapter 14',pub:'2025',st:'current',where:'International',adopt:[{at:'*',from:'2025'}],\n"
    "        src:{t:'ASHRAE Handbook -- Fundamentals 2025, chapter 14, Climatic Design Information (sold): the values a station\\'s DDY and EPW carry, as Ladybug reads them',w:'the design days: heating at 99.6% and 99% of the year\\'s hours, cooling at 0.4%, 1% and 2%',u:'https://www.ashrae.org/',lv:'S',read:'2026-10-31'},\n"
    "        v:[{n:'heating',t:1,u:'%',v:[99.6,99],say:'the heating design conditions: the share of the year\\'s hours warmer than each'},\n"
    "          {n:'cooling',t:1,u:'%',v:[0.4,1,2],say:'the cooling design conditions: the share of the year\\'s hours warmer than each'}]}]},\n"
    "    /* ---- the catalogue for a US and Pennsylvania site: in force there, not applied by the app yet ---- */\n")

# ---- the analyses read them, and keep what they used ----
AN = 'js/engine/ladybug/analyses.js'
rep(AN, "  var A3D_LBRUN={busy:null};\n",
    "  var A3D_LBRUN={busy:null};\n"
    "  /* the standards each applies (the registry, V167): kept with its result, and out of date when they change */\n"
    "  var BIM_LB_STD={utci:['utci','app.comfort'],psych:['ashrae.55','app.comfort'],wind:['app.climate'],dd:['ashrae.dd']};\n")
rep(AN, "  function bimLbParams(kind){\n"
        "    if(kind==='utci')return {conditions:['sun_wind','shade_wind','sun_still','shade_still']};\n"
        "    if(kind==='psych')return {clo:[0.5,1.0],met:[1.1,1.1],merge:true};\n",
    "  function bimLbParams(kind){\n"
    "    function c(n){return bimStd('app.comfort',n);}\n"
    "    function u(n){return bimStd('utci',n);}\n"
    "    if(kind==='utci')return {conditions:['sun_wind','shade_wind','sun_still','shade_still'],fract_body_exp:c('body_exp'),sky_exposure:c('sky_exp'),ground_ref:c('ground_ref'),\n"
    "      limits:{ta:[u('ta_lo'),u('ta_hi')],dtr:[u('dtr_lo'),u('dtr_hi')],va:[u('va_lo'),u('va_hi')],pa:u('pa_hi')},still:u('va_lo')};\n"
    "    if(kind==='psych'){var clo=(c('clo')||[]).slice(),met=c('met');\n"
    "      return {clo:clo,met:clo.map(function(){return met;}),merge:true,strategy_par:[c('day_above'),c('night_below'),c('fan'),c('balance'),c('solar_cap'),c('time_const')],\n"
    "        ppd:bimStd('ashrae.55','ppd'),still:bimStd('ashrae.55','still')};}\n")
rep(AN, "        D[kind]={r:r,params:P,at:bimSaToday(),src:src.key,ms:Date.now()-t0,\n",
    "        D[kind]={r:r,params:P,at:bimSaToday(),src:src.key,ms:Date.now()-t0,std:bimStdStamp(BIM_LB_STD[kind]||[]),\n")
rep(AN, "  /* a kept result, if it is one and of the source the project names */\n",
    "  /* the standards a kept result used that are not what they are now */\n"
    "  function bimLbStdChanged(kind){var L=A3D.site&&A3D.site.ladybug,R=L&&L[kind];return R&&R.std?bimStdChanged(R.std):[];}\n"
    "  /* a kept result, if it is one and of the source the project names */\n")

# ---- the figures say what each run used ----
FG = 'js/engine/ladybug/figures.js'
rep(FG, "  var BIM_UTCI_RANGE=['below \u221240 \u00b0C','\u221240 to \u221227 \u00b0C','\u221227 to \u221213 \u00b0C','\u221213 to 0 \u00b0C','0 to 9 \u00b0C','9 to 26 \u00b0C','26 to 32 \u00b0C','32 to 38 \u00b0C','38 to 46 \u00b0C','above 46 \u00b0C'];\n",
    "  /* the ten categories' ranges, from the registry's scale (topic 'utci') */\n"
    "  function bimLbUtciRange(){\n"
    "    var b=bimStd('utci','bands')||[],out=[],i;\n"
    "    function f(v){return (v<0?'\\u2212':'')+Math.abs(v);}\n"
    "    if(b.length!==9)return [];\n"
    "    out.push('below '+f(b[0])+' \\u00b0C');\n"
    "    for(i=1;i<9;i++)out.push(f(b[i-1])+' to '+f(b[i])+' \\u00b0C');\n"
    "    out.push('above '+f(b[8])+' \\u00b0C');\n"
    "    return out;\n"
    "  }\n")
rep(FG, "      bimClbLeg(BIM_UTCI_NAMES.map(function(n,k){return [BIM_UTCI_COL[k],n+' ('+BIM_UTCI_RANGE[k]+')'];}))+",
    "      bimClbLeg(BIM_UTCI_NAMES.map(function(n,k){var rg=bimLbUtciRange();return [BIM_UTCI_COL[k],n+(rg[k]?' ('+rg[k]+')':'')];}))+")
rep(FG, "bimLbSrcLine(R)+'; UTCI by Br\u00f6de et al. (UTCI_a002, 2009); the sun by SolarCal (ASHRAE 55); still air is UTCI\\'s 0.5 m/s');",
    "bimLbSrcLine(R)+'; UTCI by '+((bimStdEdition('utci')||{}).name||'UTCI_a002')+'; the sun by SolarCal (ASHRAE 55); still air at '+bimStdFmt(R.r.still!==undefined?R.r.still:bimStd('utci','va_lo'),'m/s'));")
rep(FG, "the PMV comfort zone for '+P.clo.join(' and ')+' clo at '+P.met[0]+' met (PPD 10% or less), and the zones",
    "the PMV comfort zone for '+P.clo.join(' and ')+' clo at '+P.met[0]+' met (PPD '+bimStdFmt(P.ppd!==undefined?P.ppd:bimStd('ashrae.55','ppd'),'%')+' or less), and the zones")
rep(FG, "bimLbSrcLine(R)+'; PMV by Fanger (ASHRAE 55), the strategies",
    "bimLbSrcLine(R)+'; PMV by Fanger ('+((bimStdEdition('ashrae.55')||{}).name||'ASHRAE 55')+'), the strategies")
rep(FG, "    var title='Design days: '+bimClbNum(h.db)+' \u00b0C for heating (99.6%), '+bimClbNum(c.db)+' \u00b0C for cooling (0.4%) with '",
    "    var hp=(bimStd('ashrae.dd','heating')||[])[0],cp=(bimStd('ashrae.dd','cooling')||[])[0];   /* __acad3dV172b: the registry's percentiles */\n"
    "    var title='Design days: '+bimClbNum(h.db)+' \u00b0C for heating ('+hp+'%), '+bimClbNum(c.db)+' \u00b0C for cooling ('+cp+'%) with '")
rep(FG, "bimClbLeg([['var(--s1)','Heating 99.6%','ln'],['var(--s2)','Cooling 0.4%','ln']])",
    "bimClbLeg([['var(--s1)','Heating '+hp+'%','ln'],['var(--s2)','Cooling '+cp+'%','ln']])")
rep(FG, "      bimLbSrcLine(R)+'; ASHRAE Handbook, Fundamentals, chapter 14 (climatic design information)');",
    "      bimLbSrcLine(R)+'; '+((bimStdEdition('ashrae.dd')||{}).name||'ASHRAE Handbook -- Fundamentals')+' (climatic design information)');")

# ---- Analyze: Ladybug's rows in Climate, and their buttons ----
AT = 'js/engine/analysis/analyze-tab.js'
rep(AT, "    C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});   /* __acad3dV148 */\n",
    "    bimLbCards().forEach(function(c){C.push(c);});   /* __acad3dV172b: Ladybug's rows, in Climate */\n"
    "    C.forEach(function(c){c.group=BIM_ANZ_GROUP_OF[c.id]||'model';});   /* __acad3dV148 */\n")
rep(AT, "    else if(k.indexOf('tr:')===0)bimTrAct(k.slice(3));   /* __acad3dV171 */\n",
    "    else if(k.indexOf('tr:')===0)bimTrAct(k.slice(3));   /* __acad3dV171 */\n"
    "    else if(k.indexOf('lb:')===0)return bimLbAct(k.slice(3));   /* __acad3dV172b: Ladybug's rows refresh as their work ends */\n")

# ---- the suite's hooks, and the marker ----
HL = 'js/engine/testing/hooks-ladybug.js'
rep(HL, "keys,catalogue,options,custom,duplicate';", "keys,catalogue,options,custom,duplicate,registry,stdstamp,analyze';")
rep(HL, "  window.__a3dLbOmZone=function(off){return bimLbOmZone(off);};\n",
    "  window.__a3dLbOmZone=function(off){return bimLbOmZone(off);};\n"
    "  window.__a3dLbParams=function(kind){return bimLbParams(kind);};\n"
    "  window.__a3dLbStdChanged=function(kind){return bimLbStdChanged(kind);};\n"
    "  window.__a3dLbCards=function(){return JSON.parse(JSON.stringify(bimLbCards()));};\n"
    "  window.__a3dLbAct=function(a){return bimLbAct(a);};\n"
    "  window.__a3dLbAddTo=function(kind,id){return bimLbAddTo(kind,id);};\n"
    "  window.__a3dLbUtciRange=function(){return bimLbUtciRange();};\n")

LAY = ROOT / 'tools' / 'app_layout.py'
s = LAY.read_text(encoding='utf-8')
a = "    ('ladybug/figures.js', '  /* ================= __acad3dV172b: the Ladybug analyses as board figures ================='),\n"
assert s.count(a) == 1
s = s.replace(a, a + "    ('ladybug/panel.js', '  /* ================= __acad3dV172b: Ladybug in the analysis workspace ================='),\n")
LAY.write_text(s, encoding='utf-8')
done()
