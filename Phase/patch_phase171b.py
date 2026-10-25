#!/usr/bin/env python3
"""V171b: the simulation wired in. Its files (src/js/engine/simulation/, testing/hooks-traffic.js) joined into the
build after the site analysis's panel; Traffic and people an analysis of Access (the registry's analyses, their
runner, their standards, Analyze's group and its actions, V164's card); V170's clock driving the run (Play from still
starts it, Stop gives it up, each tick steps it, fewer frames at Light) and paint() drawing it; the width a street's
kept tag; V169's design car built without its wheels on request; TRAFFIC and TRAFFICOFF; the version V171.

Run from the repository root: python3 Phase/patch_phase171b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('ab58f602ec913aded95f448696bd9de9fc191dadefdc662be8412b7b3857d63a')   # after 171a

SIM = ['traffic-network', 'traffic-demand', 'traffic-signals', 'traffic-walkers', 'traffic-sim', 'traffic-draw', 'traffic-ui']
ROOT = pathlib.Path(__file__).resolve().parent.parent
first = {f: (ROOT / 'src/js/engine/simulation' / (f + '.js')).read_text().split('\n', 1)[0][:90] for f in SIM}
hook = (ROOT / 'src/js/engine/testing/hooks-traffic.js').read_text().split('\n', 1)[0][:90]

# ---- the files in the build, in order: the simulation after the site analysis's panel, its hooks after the others ----
rep('index.html', '<!-- @include js/engine/site-analysis/panel.js -->\n',
    '<!-- @include js/engine/site-analysis/panel.js -->\n' + ''.join('<!-- @include js/engine/simulation/%s.js -->\n' % f for f in SIM))
rep('index.html', '<!-- @include js/engine/testing/hooks-legacy.js -->\n',
    '<!-- @include js/engine/testing/hooks-legacy.js -->\n<!-- @include js/engine/testing/hooks-traffic.js -->\n')
lay = ROOT / 'tools/app_layout.py'
t = lay.read_text()
a = "    ('site-analysis/panel.js', '  /* ---- the panel ---- */'),\n"
b = "    ('testing/hooks-legacy.js', '  /* __acad3dV51: opening-propagation surface for the Phase 55b tests. */'),\n"
assert t.count(a) == 1 and t.count(b) == 1
t = t.replace(a, a + ''.join('    (%r, %r),\n' % ('simulation/%s.js' % f, first[f]) for f in SIM))
t = t.replace(b, b + '    (%r, %r),\n' % ('testing/hooks-traffic.js', hook))

# ---- an analysis of Access ----
rep('js/engine/standards/registry.js', "    {id:'vehicles',name:'Vehicle access',col:'#aab3be'},\n",
    "    {id:'vehicles',name:'Vehicle access',col:'#aab3be'},\n    {id:'traffic',name:'Traffic and people',col:'#ffb454'},   /* __acad3dV171: the simulation's results */\n")
rep('js/engine/standards/registry.js', "  var BIM_DG_STD={frame:['walk.speed'],",
    "  var BIM_DG_STD={traffic:['idm.car','mobil','stm.signal','mutcd.signal','mutcd.walk','fdot.k','nchrp255','sd.trips','hm.walk','sumo.rules','app.traffic','fhwa.fc','app.roads','aashto.vehicles'],   /* __acad3dV171 */\n    frame:['walk.speed'],")
rep('js/engine/standards/registry.js', "  var BIM_DG_STD_DATA={transit:'access',", "  var BIM_DG_STD_DATA={traffic:'access',transit:'access',")
rep('js/engine/site-analysis/land-use.js', "    landuse:bimDgLanduseRun,figure:bimDgFigureRun,green:bimDgGreenRun,zoning:bimDgZoningRun};   /* __acad3dV168 */",
    "    landuse:bimDgLanduseRun,figure:bimDgFigureRun,green:bimDgGreenRun,zoning:bimDgZoningRun,   /* __acad3dV168 */\n    traffic:bimDgTrafficRun};   /* __acad3dV171 */")
rep('js/engine/analysis/analyze-tab.js', "BIM_ANZ_GROUP_OF.dgwalk='access';BIM_ANZ_GROUP_OF.dgvehicles='access';BIM_ANZ_GROUP_OF.dgneeds='people';",
    "BIM_ANZ_GROUP_OF.dgwalk='access';BIM_ANZ_GROUP_OF.dgvehicles='access';BIM_ANZ_GROUP_OF.dgneeds='people';\n  BIM_ANZ_GROUP_OF.dgtraffic='access';   /* __acad3dV171 */")
rep('js/engine/analysis/analyze-tab.js', "    else if(k.indexOf('dg:')===0)bimDgAct(k.slice(3));   /* __acad3dV164 */\n",
    "    else if(k.indexOf('dg:')===0)bimDgAct(k.slice(3));   /* __acad3dV164 */\n    else if(k.indexOf('tr:')===0)bimTrAct(k.slice(3));   /* __acad3dV171 */\n")
rep('js/engine/site-analysis/analyze-site.js', "      return {id:'dg'+A.id,title:A.name,state:", "      var card={id:'dg'+A.id,title:A.name,state:")
rep('js/engine/site-analysis/analyze-site.js',
    "          {act:'dg:reset:'+A.id,label:'Reset',off:R?'':'Not run yet',tip:'As the analysis draws it: what you changed, copied or deleted on it goes back'}]};\n",
    "          {act:'dg:reset:'+A.id,label:'Reset',off:R?'':'Not run yet',tip:'As the analysis draws it: what you changed, copied or deleted on it goes back'}]};\n"
    "      return A.id==='traffic'?bimTrCard(card):card;   /* __acad3dV171: the simulation's own part */\n")

# ---- drawn while the clock plays, under the analyses' words ----
rep('js/engine/map/terrain-3d.js', "    drawDiagrams(ctx,V,W,H,'over');    /* __acad3dV164: the site analysis's lines, symbols and words */\n",
    "    if(!capMode)bimTrDraw(ctx,V,W,H);  /* __acad3dV171: the cars and walkers, while the clock plays or holds a moment */\n"
    "    drawDiagrams(ctx,V,W,H,'over');    /* __acad3dV164: the site analysis's lines, symbols and words */\n")

# ---- V170's clock drives the run ----
M = 'js/engine/site-analysis/motion.js'
rep(M, "  function bimAnimCan(){A3D_ANIM.fr=null;return bimAnimFrame().any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk());}",
    "  function bimAnimCan(){A3D_ANIM.fr=null;return bimAnimFrame().any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk())||bimTrCanPlay();}   /* __acad3dV171: the simulation */")
rep(M, "      if(!A3D_ANIM.paused){A3D_ANIM.t=0;A3D_ANIM.playAt=0;}\n",
    "      if(!A3D_ANIM.paused){A3D_ANIM.t=0;A3D_ANIM.playAt=0;}\n      if(bimTrCanPlay()&&!A3D_TR.run)bimTrStart();   /* __acad3dV171: Play from still starts the run, warmed up */\n")
rep(M, "    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();\n    if(was)paint();",
    "    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;\n    bimAnimHalt();\n    bimTrStop();   /* __acad3dV171: Stop gives the run up */\n    if(was)paint();")
rep(M, "    if(A3D_ANIM.last)A3D_ANIM.t+=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000));   /* a slow frame moves it a tenth of a second at most, never a jump */",
    "    if(A3D_ANIM.last){var dtc=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000));A3D_ANIM.t+=dtc;bimTrAdvance(dtc);}   /* a slow frame moves it a tenth of a second at most, never a jump; __acad3dV171: the run's steps */")
rep(M, "    if(!A3D_ANIM.painted||ts-A3D_ANIM.painted>=1000/BIM_ANIM.fps-2){",
    "    if(!A3D_ANIM.painted||ts-A3D_ANIM.painted>=1000/bimTrFps()-2){   /* __acad3dV171: fewer frames at Light */")
rep(M, "    var F=bimAnimFrame(),can=F.any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk()),moving=A3D_ANIM.on||A3D_ANIM.paused,g,b,x,key;",
    "    var F=bimAnimFrame(),can=F.any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk())||bimTrCanPlay(),moving=A3D_ANIM.on||A3D_ANIM.paused,g,b,x,key;   /* __acad3dV171 */")
rep(M, "    if(!can&&moving){A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;bimAnimHalt();moving=false;}",
    "    if(!can&&moving){A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;bimAnimHalt();bimTrStop();moving=false;}")

# ---- the width a kept tag; the design car without its wheels ----
rep('js/engine/site-analysis/movement-data.js', "|shoulder(:[a-z_:]+)?)$/;", "|shoulder(:[a-z_:]+)?|width)$/;   /* __acad3dV171: width, which caps a street's lanes */")
rep('js/engine/assets/scale-assets.js', "  function bimEntVehMesh(V){\n", "  function bimEntVehMesh(V,bare){   /* __acad3dV171: bare, without its wheels (the simulation's cars) */\n")
rep('js/engine/assets/scale-assets.js', "    P.push(bimEntDisc([-xw,r,zf],r,tw),bimEntDisc([xw,r,zf],r,tw),bimEntDisc([-xw,r,zr],r,tw),bimEntDisc([xw,r,zr],r,tw));\n",
    "    if(!bare)P.push(bimEntDisc([-xw,r,zf],r,tw),bimEntDisc([xw,r,zf],r,tw),bimEntDisc([-xw,r,zr],r,tw),bimEntDisc([xw,r,zr],r,tw));\n")

# ---- the commands ----
rep('js/shell/shell.js', "    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],\n",
    "    ['TRAFFIC',['TRAFFICSIM','SIMULATETRAFFIC','PEDESTRIANS','TRAFFICON'],'traffic','Simulate traffic and people around the site: cars on the streets by the IDM with each junction\\'s own assumed signal plan, walkers on the sidewalks crossing on green, and the design\\'s own trips; it plays on the clock (Play, Pause and Stop)'],   /* __acad3dV171 */\n"
    "    ['TRAFFICOFF',['TRAFFICSTOP'],'trafficoff','Stop simulating traffic and people'],\n"
    "    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],\n")
rep('js/engine/commands/command-map.js', "    animplay:function(){bimAnimPlay();},   /* __acad3dV170 */\n",
    "    animplay:function(){bimAnimPlay();},   /* __acad3dV170 */\n    traffic:function(){bimAnzView();bimSaGoto('access');bimTrCommand(true);},   /* __acad3dV171 */\n    trafficoff:function(){bimTrCommand(false);},\n")
rep('js/engine/commands/command-catalogue.js', "  var BIM_CMD_TERMS={FILLET:", "  var BIM_CMD_TERMS={TRAFFIC:'cars pedestrians walkers simulation signals queue junction delay',FILLET:")

# ---- the settings row's look ----
rep('css/panels/properties-analyze.css', "/* __acad3dV166b: a row's settings and readings, in Analyze */\n",
    "/* __acad3dV171: the simulation's settings, as rows of buttons */\n"
    ".a3d-trset{display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin:0 0 7px}\n"
    ".a3d-trlab{flex:0 0 74px;font-size:11.5px;color:#9aa5b0}\n"
    "body.light-theme .a3d-trlab{color:#555}\n"
    "/* __acad3dV166b: a row's settings and readings, in Analyze */\n")

# ---- the version ----
rep('js/engine/ui/guide-versions.js', "  var BIM_APP_VERSION={v:'V170',date:'2026-10-24'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170 */",
    "  var BIM_APP_VERSION={v:'V171',date:'2026-10-25'};   /* __acad3dV162; __acad3dV163; __acad3dV164; __acad3dV165; __acad3dV166; __acad3dV167; __acad3dV168; __acad3dV170; __acad3dV171 */")
lay.write_text(t)
done()
