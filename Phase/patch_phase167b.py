#!/usr/bin/env python3
"""V167b: the analyses read the registry -- every moved constant, and the sentences that state them.

Each constant that held a standard's or an assumption's value is replaced by an accessor that
reads it through bimStd, in the shape the code had (so BIM_CLIM_COMFORT.t0 becomes
bimClimComfort().t0), and its definition goes. The sentences that state those values are built
from the same accessors, so an override or a new edition changes the words with the number. With
the registry's values the analyses compute and say exactly what they did: the older suites pass
unchanged, which is what proves the move.

Run from the repository root: python3 Phase/patch_phase167b.py [--dry]
"""
import hashlib, pathlib, re, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'a50aeb1969eacf36d976fa20882d0e0a8969d54bbbb93d33f13c4ff470f6dbdb'   # after patch_phase167a.py
DRY = '--dry' in sys.argv

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


def js_ascii(t):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in t)


# ---- 1. the accessors, after the registry ----
ACC = r'''  /* __acad3dV167: the values the analyses read, from the registry, in the shapes their code had */
  function bimAn(n){var t=String(n);return /^(8|11|18)(\D|$)/.test(t)||/^8\d/.test(t)?'an':'a';}
  function bimStdYear(t){var E=bimStdEdition(t),m=E&&E.id?/(\d{4})/.exec(E.name||''):null;return m?m[1]:'';}
  function bimAccSpeed(){return bimStd('walk.speed','m_min');}
  function bimAccKmhText(){var v=bimAccSpeed();return bimDispNum(v*60/1000,1)+' km/h ('+bimDispNum(v,1)+' m a minute)';}
  function bimAccIxr(){return bimStd('leed.nd','radius');}
  function bimAccLeed(){return bimStdMemo('acc.leed',function(){return [[bimStd('leed.nd','case1'),'LEED ND prerequisite'],[bimStd('leed.nd','case2'),'with internal streets'],[bimStd('leed.nd','pt1'),'1 point'],[bimStd('leed.nd','pt2'),'2 points']];});}
  function bimClimWho24(){return bimStd('who.aqg','pm25_24h');}
  function bimClimWhoYear(){return bimStd('who.aqg','pm25_year');}
  function bimClimWhoIt1(){return bimStd('who.aqg','pm25_it1_year');}
  function bimClimBase(){return bimStd('app.climate','base');}
  function bimClimCalm(){return bimStd('app.climate','calm');}
  function bimClimWindBins(){return bimStdMemo('clim.bins',function(){return [bimClimCalm()].concat(bimStd('app.climate','wind_bins')||[]);});}
  function bimClimComfort(){return bimStdMemo('clim.comfort',function(){return {t0:bimStd('app.climate','comfort_t0'),t1:bimStd('app.climate','comfort_t1'),rh0:bimStd('app.climate','comfort_rh0'),rh1:bimStd('app.climate','comfort_rh1')};});}
  function bimDgCrtnMax(){return bimStd('crtn','range');}
  /* the roads by OpenStreetMap class: FHWA's class, the middle of its traffic ranges (to the nearest 10), and
     the app's speed, heavy vehicles and lanes */
  function bimDgRoads(){return bimStdMemo('dg.roads',function(){
    var F=bimStd('fhwa.fc','classes')||{},C=bimStd('app.roads','classes')||{},out={},k;
    function mid(a){return a&&a.length===2?Math.round((a[0]+a[1])/20)*10:0;}
    for(k in C)if(C.hasOwnProperty(k)){var f=F[C[k]]||{};out[k]={fc:f.name||C[k],u:mid(f.u),r:mid(f.r),v:bimStd('app.roads',k+'_v'),p:bimStd('app.roads',k+'_p'),l:bimStd('app.roads',k+'_l')};}
    return out;});}
  function bimMvXtab(){return bimStd('lts.xing2016','table');}
  function bimMvGuide(){return bimStdMemo('mv.guide',function(){return {food:bimStd('guides.walk','shops'),learn:bimStd('guides.walk','school'),parks:bimStd('guides.walk','green')};});}
  function bimMvPtalWalk(){return bimStdMemo('mv.ptalwalk',function(){var r=bimStd('tfl.ptal','walk_rail');return {bus:bimStd('tfl.ptal','walk_bus'),tram:bimStd('tfl.ptal','walk_tram'),metro:r,rail:r,light:r};});}
  function bimMvPtalK(){return bimStdMemo('mv.ptalk',function(){var r=bimStd('tfl.ptal','k_rail');return {bus:bimStd('tfl.ptal','k_bus'),tram:r,metro:r,rail:r,light:r};});}
  function bimMvPtalBands(){return bimStdMemo('mv.ptalbands',function(){return (bimStd('tfl.ptal','bands')||[]).map(function(b){return [b[0]===null?Infinity:b[0],b[1]];});});}
  /* a stop's reach: the furthest PTAL walks to it for any of its modes */
  function bimMvStopLim(s){var W=bimMvPtalWalk(),l=0;(s.m||[]).forEach(function(m){if(W[m]>l)l=W[m];});return l||W.bus;}
  var BIM_LAND_SLOPE_D=[['flat to gentle: the easiest to build on','#ffffb2'],['moderate','#fecc5c'],['moderately steep','#fd8d3c'],['steep: walls and drainage engineered','#f03b20'],['not developable without great cost','#bd0026']];
  /* the five classes: [from %, to %, name, short, what it means, colour] -- the steeper the darker */
  function bimLandSlope(){return bimStdMemo('land.slope',function(){
    var b=[0,bimStd('land.slope','b1'),bimStd('land.slope','b2'),bimStd('land.slope','b3'),bimStd('land.slope','b4'),Infinity],out=[],i;
    for(i=0;i<5;i++){var a=b[i],z=b[i+1],fa=bimDispNum(a,2),fz=bimDispNum(z,2);
      out.push([a,z,z===Infinity?'Over '+fa+'%':fa+' to '+fz+'%',z===Infinity?fa+'+':fa+'-'+fz,BIM_LAND_SLOPE_D[i][0],BIM_LAND_SLOPE_D[i][1]]);}
    return out;});}
  function bimSlopeBands(){return bimStdMemo('terrain.bands',function(){return (bimStd('terrain.slope_bands','bands')||[]).concat([Infinity]);});}
  function bimOccLoads(){return bimStd('ibc.occupant_load','table')||[];}
  /* the frame's combinations: ASCE 7's two strength combinations with the factors of the edition in force,
     and the app's service and single cases; a name is its factors, so it says what it is */
  function bimCombos(){return bimStdMemo('asce.combos',function(){
    var d1=bimStd('asce7.combos','c1_d'),d2=bimStd('asce7.combos','c2_d'),l2=bimStd('asce7.combos','c2_l'),E=bimStdEdition('asce7.combos'),ed=E&&E.name?E.name.replace(/,.*$/,''):'ASCE 7';
    return [{key:'c2',name:bimDispNum(d2,2)+'D+'+bimDispNum(l2,2)+'L',f:{D:d2,L:l2},why:'strength, '+ed+' 2.3.1 combination 2'},{key:'c1',name:bimDispNum(d1,2)+'D',f:{D:d1},why:'strength, '+ed+' 2.3.1 combination 1'},
      {key:'s',name:'D+L',f:{D:1,L:1},why:'service'},{key:'d',name:'D',f:{D:1},why:'dead load alone'},{key:'l',name:'L',f:{L:1},why:'live load alone'}];});}
  function bimCtxLevelH(){return bimStd('app.context','storey');}
  function bimCtxDefaultH(){return bimStd('app.context','building');}
  function bimCtxDeck(){return bimStd('app.context','deck');}
  function bimCtxDeckT(){return bimStd('app.context','deck_t');}
  function bimCtxPier(){return bimStd('app.context','pier');}
  function bimCtxTreeH(){return bimStd('app.context','tree');}
  function bimCtxTowerH(){return bimStd('app.context','tower');}
  function bimCtxLineH(){return bimStd('app.context','line');}
  function bimRoadW(){return bimStd('app.context','road_w')||{};}
'''
rep("  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};\n",
    js_ascii(ACC) + "  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};\n")

# ---- 2. the definitions go ----
rep("  var BIM_ACC_SPEED=80,BIM_ACC_BANDS=[5,10,15],BIM_ACC_MAXT=20,BIM_ACC_FRONT=30,BIM_ACC_STEPS=2,BIM_ACC_IXR=400,BIM_ACC_IXMERGE=12,BIM_ACC_CUT=5;",
    "  var BIM_ACC_BANDS=[5,10,15],BIM_ACC_MAXT=20,BIM_ACC_FRONT=30,BIM_ACC_STEPS=2,BIM_ACC_IXMERGE=12,BIM_ACC_CUT=5;   /* __acad3dV167: the walking speed and LEED's radius are in the registry */")
rep("  var BIM_ACC_LEED=[[90,'LEED ND prerequisite'],[140,'with internal streets'],[300,'1 point'],[400,'2 points']];\n",
    "  /* __acad3dV167: the thresholds are the registry's (leed.nd): bimAccLeed */\n")
rep("  var BIM_CLIM_YEARS=10,BIM_CLIM_BASE=18,BIM_CLIM_CALM=0.5,BIM_CLIM_WIND_BINS=[0.5,2,4,6,8];",
    "  var BIM_CLIM_YEARS=10;   /* __acad3dV167: the base, the calm and the bins are the registry's (app.climate) */")
rep("  var BIM_CLIM_WHO24=15,BIM_CLIM_WHO_YEAR=5,BIM_CLIM_COMFORT={t0:20,t1:27,rh0:20,rh1:80};\n",
    "  /* __acad3dV167: WHO's levels (who.aqg) and the comfort band (app.climate) are the registry's */\n")
rep("  var BIM_DG_CRTN_MAX=300,BIM_DG_LAMBDA=0.686,BIM_DG_STEP=15;",
    "  var BIM_DG_LAMBDA=0.686,BIM_DG_STEP=15;   /* __acad3dV167: CRTN's range is the registry's (crtn) */")
m = re.search(r"  var BIM_DG_ROADS=\{\n.*?\n    living_street:\{fc:'Local road',u:390,r:210,v:20,p:1,l:1\}\};\n", s, re.S)
if not m:
    sys.exit('BIM_DG_ROADS not found')
s = s[:m.start()] + "  /* __acad3dV167: the classes, their traffic and the app's speeds, heavy vehicles and lanes are the registry's (fhwa.fc, app.roads): bimDgRoads */\n" + s[m.end():]
rep("  var BIM_MV_XTAB=[[1,2,4],[1,2,4],[2,3,4],[3,4,4]];\n", "  /* __acad3dV167: the table is the registry's (lts.xing2016): bimMvXtab */\n")
rep("  /* the design guides' walks: 400 m to green space, 800 m to shops and a primary school */\n  var BIM_MV_GUIDE={food:800,learn:800,parks:400};\n",
    "  /* the design guides' walks to green space, shops and a primary school: the registry's (guides.walk), bimMvGuide */\n")
rep("  var BIM_MV_PTAL_WALK={bus:8,tram:12,metro:12,rail:12,light:12},BIM_MV_PTAL_K={bus:2,tram:0.75,metro:0.75,rail:0.75,light:0.75};\n"
    "  var BIM_MV_PTAL=[[2.5,'1a'],[5,'1b'],[10,'2'],[15,'3'],[20,'4'],[25,'5'],[40,'6a'],[Infinity,'6b']];\n",
    "  /* __acad3dV167: the walks, the allowances and the bands are the registry's (tfl.ptal): bimMvPtalWalk, bimMvPtalK, bimMvPtalBands */\n")
m = re.search(r"  /\* the five classes: \[from %, to %, name, short, what it means, colour\] -- the steeper the darker \*/\n  var BIM_LAND_SLOPE=\[.*?\]\];\n", s, re.S)
if not m:
    sys.exit('BIM_LAND_SLOPE not found')
s = s[:m.start()] + "  /* __acad3dV167: the slope classes are the registry's (land.slope): bimLandSlope */\n" + s[m.end():]
rep("  var BIM_SLOPE_BANDS=[0,2,5,8.33,15,25,50,Infinity];\n", "  /* __acad3dV167: the band edges are the registry's (terrain.slope_bands): bimSlopeBands */\n")
m = re.search(r"  var BIM_OCC_LOADS=\[\n.*?\n  \];\n", s, re.S)
if not m:
    sys.exit('BIM_OCC_LOADS not found')
s = s[:m.start()] + "  /* __acad3dV167: the table is the registry's (ibc.occupant_load), its edition the one in force for the site: bimOccLoads */\n" + s[m.end():]
m = re.search(r"  var BIM_COMBOS=\[\n.*?\n  \];\n", s, re.S)
if not m:
    sys.exit('BIM_COMBOS not found')
s = s[:m.start()] + "  /* __acad3dV167: the combinations are the registry's (asce7.combos): bimCombos */\n" + s[m.end():]
rep("  var BIM_CTX_LEVEL_H=3,BIM_CTX_DEFAULT_H=6,BIM_CTX_MAX_FEATURES=5000,BIM_CTX_GRID=25,BIM_CTX_TZ=15;",
    "  var BIM_CTX_MAX_FEATURES=5000,BIM_CTX_GRID=25,BIM_CTX_TZ=15;   /* __acad3dV167: a storey's and a building's height are the registry's (app.context) */")
rep("  var BIM_CTX_DECK=6,BIM_CTX_DECK_T=0.8,BIM_CTX_PIER=30,BIM_CTX_TREE_H=8,BIM_CTX_TREE_STEP=8,BIM_CTX_TOWER_H=25,BIM_CTX_LINE_H=20,BIM_CTX_TREES_MAX=3000;",
    "  var BIM_CTX_TREE_STEP=8,BIM_CTX_TREES_MAX=3000;   /* __acad3dV167: the decks, piers, trees, towers and lines are the registry's (app.context) */")
m = re.search(r"  var BIM_ROAD_W=\{.*?\};\n", s, re.S)
if not m:
    sys.exit('BIM_ROAD_W not found')
s = s[:m.start()] + "  /* __acad3dV167: the widths are the registry's (app.context): bimRoadW */\n" + s[m.end():]

# ---- 3. every read of them reads the accessor ----
TOK = [('BIM_ACC_SPEED', 'bimAccSpeed()', 13), ('BIM_ACC_IXR', 'bimAccIxr()', 1), ('BIM_ACC_LEED', 'bimAccLeed()', 2),
       ('BIM_CLIM_WHO24', 'bimClimWho24()', 9), ('BIM_CLIM_WHO_YEAR', 'bimClimWhoYear()', 2), ('BIM_CLIM_BASE', 'bimClimBase()', 6),
       ('BIM_CLIM_CALM', 'bimClimCalm()', 2), ('BIM_CLIM_WIND_BINS', 'bimClimWindBins()', 4), ('BIM_CLIM_COMFORT', 'bimClimComfort()', 16),
       ('BIM_DG_CRTN_MAX', 'bimDgCrtnMax()', 5), ('BIM_DG_ROADS', 'bimDgRoads()', 3), ('BIM_MV_XTAB', 'bimMvXtab()', 1),
       ('BIM_MV_GUIDE', 'bimMvGuide()', 1), ('BIM_MV_PTAL_WALK', 'bimMvPtalWalk()', 1), ('BIM_MV_PTAL_K', 'bimMvPtalK()', 1),
       ('BIM_MV_PTAL', 'bimMvPtalBands()', 3), ('BIM_LAND_SLOPE', 'bimLandSlope()', 11), ('BIM_SLOPE_BANDS', 'bimSlopeBands()', 6),
       ('BIM_OCC_LOADS', 'bimOccLoads()', 7), ('BIM_COMBOS', 'bimCombos()', 7), ('BIM_CTX_LEVEL_H', 'bimCtxLevelH()', 7),
       ('BIM_CTX_DEFAULT_H', 'bimCtxDefaultH()', 3), ('BIM_CTX_DECK', 'bimCtxDeck()', 1), ('BIM_CTX_DECK_T', 'bimCtxDeckT()', 2),
       ('BIM_CTX_PIER', 'bimCtxPier()', 4), ('BIM_CTX_TREE_H', 'bimCtxTreeH()', 1), ('BIM_CTX_TOWER_H', 'bimCtxTowerH()', 1),
       ('BIM_CTX_LINE_H', 'bimCtxLineH()', 1), ('BIM_ROAD_W', 'bimRoadW()', 1)]
for name, acc, n in TOK:
    pat = re.compile(r'\b%s\b' % re.escape(name))
    found = len(pat.findall(s))
    if DRY:
        print('%-20s %d (expected %d)' % (name, found, n))
        continue
    if found != n:
        sys.exit('%s: expected %d reads, found %d' % (name, n, found))
    s = pat.sub(acc, s)
if DRY:
    sys.exit(0)

# ---- 4. the sentences that state the values ----
# the compass rings: minutes on foot at the walking speed
rep("rows:[['On foot','about '+Math.max(1,Math.round(d/80))+' min, at 80 m a minute, as the crow flies']]",
    "rows:[['On foot','about '+Math.max(1,Math.round(d/bimAccSpeed()))+' min, at '+bimDispNum(bimAccSpeed(),1)+' m a minute, as the crow flies']]")
# transit: PTAL's walks, its stops' reach, its legend and its method, from the record
rep("    var c8=bimMvWalkBand(A,0,8,y-0.02),c12=bimMvWalkBand(A,8,12,y-0.02);\n"
    "    if(c8.length)E.push({k:'catch8',name:'Within an 8-minute walk',g:{kind:'segs',pts:c8},s:{stroke:light?'#5d7fa8':'#9fb7d4',w:2.4,op:0.75},\n"
    "      info:{title:'The streets within an 8-minute walk: PTAL\\'s reach to a bus stop',rows:[['Speed','4.8 km/h (80 m a minute)']],method:'The walk times along the streets (V161)',source:A.src}});\n"
    "    if(c12.length)E.push({k:'catch12',name:'8 to 12 minutes\\' walk',g:{kind:'segs',pts:c12},s:{stroke:light?'#5d7fa8':'#9fb7d4',w:1.2,dash:[4,3],op:0.7},\n"
    "      info:{title:'The streets 8 to 12 minutes\\' walk away: PTAL\\'s reach to a station',rows:[['Speed','4.8 km/h (80 m a minute)']],method:'The walk times along the streets (V161)',source:A.src}});\n",
    "    var PW=bimMvPtalWalk(),wb=PW.bus,wr=PW.rail,c8=bimMvWalkBand(A,0,wb,y-0.02),c12=bimMvWalkBand(A,wb,wr,y-0.02);   /* __acad3dV167: PTAL's walks, the registry's */\n"
    "    if(c8.length)E.push({k:'catch8',name:'Within '+bimAn(wb)+' '+bimDispNum(wb,2)+'-minute walk',g:{kind:'segs',pts:c8},s:{stroke:light?'#5d7fa8':'#9fb7d4',w:2.4,op:0.75},\n"
    "      info:{title:'The streets within '+bimAn(wb)+' '+bimDispNum(wb,2)+'-minute walk: PTAL\\'s reach to a bus stop',rows:[['Speed',bimAccKmhText()]],method:'The walk times along the streets (V161)',source:A.src}});\n"
    "    if(c12.length)E.push({k:'catch12',name:bimDispNum(wb,2)+' to '+bimDispNum(wr,2)+' minutes\\' walk',g:{kind:'segs',pts:c12},s:{stroke:light?'#5d7fa8':'#9fb7d4',w:1.2,dash:[4,3],op:0.7},\n"
    "      info:{title:'The streets '+bimDispNum(wb,2)+' to '+bimDispNum(wr,2)+' minutes\\' walk away: PTAL\\'s reach to a station',rows:[['Speed',bimAccKmhText()]],method:'The walk times along the streets (V161)',source:A.src}});\n")
rep("      var rail=s.m.some(function(m){return /^(metro|rail|light|tram)$/.test(m);}),lim=rail?12:8;",
    "      var rail=s.m.some(function(m){return /^(metro|rail|light|tram)$/.test(m);}),lim=bimMvStopLim(s);")
rep("          ['Within PTAL\\'s reach',(rail?'12':'8')+' minutes for '+(rail?'rail, metro, light rail and tram':'a bus')]]",
    "          ['Within PTAL\\'s reach',bimDispNum(lim,2)+' minutes for '+(rail?'rail, metro, light rail and tram':'a bus')]]")
rep("    if(c8.length)leg.push({name:'Within 8 minutes',short:'8 min',col:light?'#5d7fa8':'#9fb7d4',kind:'line'});\n"
    "    if(c12.length)leg.push({name:'8 to 12 minutes',short:'12 min',col:light?'#5d7fa8':'#9fb7d4',kind:'dash'});\n",
    "    if(c8.length)leg.push({name:'Within '+bimDispNum(wb,2)+' minutes',short:bimDispNum(wb,2)+' min',col:light?'#5d7fa8':'#9fb7d4',kind:'line'});\n"
    "    if(c12.length)leg.push({name:bimDispNum(wb,2)+' to '+bimDispNum(wr,2)+' minutes',short:bimDispNum(wr,2)+' min',col:light?'#5d7fa8':'#9fb7d4',kind:'dash'});\n")
rep("title='No bus stop within 8 minutes or station within 12: PTAL 0';",
    "title='No bus stop within '+bimDispNum(wb,2)+' minutes or station within '+bimDispNum(wr,2)+': PTAL 0';")
rep("        method:'TfL\\'s PTAL: the walk at 4.8 km/h (8 minutes to a bus, 12 to rail), half the headway, and 2 minutes (bus) or 0.75 (rail) for reliability make the access time; 30 over it the doorstep frequency; per mode the best in full and the rest at half. Headways from OpenStreetMap\\'s interval',",
    "        method:'TfL\\'s PTAL: the walk at '+bimDispNum(bimAccSpeed()*60/1000,1)+' km/h ('+bimDispNum(wb,2)+' minutes to a bus, '+bimDispNum(wr,2)+' to rail), half the headway, and '+bimDispNum(bimMvPtalK().bus,2)+' minutes (bus) or '+bimDispNum(bimMvPtalK().rail,2)+' (rail) for reliability make the access time; 30 over it the doorstep frequency; per mode the best in full and the rest at half. Headways from OpenStreetMap\\'s interval',")
rep("    if(!P.lines.length)return 'No bus stop within 8 minutes or station within 12: PTAL 0 by TfL\\'s method.';",
    "    if(!P.lines.length)return 'No bus stop within '+bimDispNum(bimMvPtalWalk().bus,2)+' minutes or station within '+bimDispNum(bimMvPtalWalk().rail,2)+': PTAL 0 by TfL\\'s method.';")
# PTAL's band of the index, from its bands
rep("  function bimMvPtalBand(ai){var i;if(!(ai>0))return '0';for(i=0;i<bimMvPtalBands().length;i++)if(ai<=bimMvPtalBands()[i][0])return bimMvPtalBands()[i][1];return '6b';}",
    "  function bimMvPtalBand(ai){var B=bimMvPtalBands(),i;if(!(ai>0))return '0';for(i=0;i<B.length;i++)if(ai<=B[i][0])return B[i][1];return B.length?B[B.length-1][1]:'6b';}")
# a street's speed where none is mapped: the app's, by class
rep("    return {v:rc?rc.v:(base==='service'?20:(base==='track'?30:40)),src:'assumed'};",
    "    return {v:rc?rc.v:bimStd('app.roads',base==='service'?'service_v':(base==='track'?'track_v':'other_v')),src:'assumed'};")
# noise: CRTN's range in its method
rep("the distance to a point 4 m up, to 300 m; behind the first building",
    "the distance to a point 4 m up, to '+bimDispNum(bimDgCrtnMax(),0)+' m; behind the first building")
# air: WHO's edition and its first interim target
rep("    if(mean>35)st='critical';",
    "    if(mean>bimClimWhoIt1())st='critical';")
rep("against the WHO 2021 24-hour guideline of '",
    "against the WHO '+bimStdYear('who.aqg')+' 24-hour guideline of '")
# LEED ND: its thresholds, in the chart, the sentence and the finding; over 400 is its second point
rep("      '<rect x=\"'+x(90)+'\" y=\"'+y0+'\" width=\"'+bimClbF(x(mx)-x(90))+'\" height=\"24\" fill=\"var(--band)\"/>'+\n"
    "      '<rect x=\"'+x(300)+'\" y=\"'+y0+'\" width=\"'+bimClbF(x(mx)-x(300))+'\" height=\"24\" fill=\"var(--band)\"/>';",
    "      '<rect x=\"'+x(bimStd('leed.nd','case1'))+'\" y=\"'+y0+'\" width=\"'+bimClbF(x(mx)-x(bimStd('leed.nd','case1')))+'\" height=\"24\" fill=\"var(--band)\"/>'+\n"
    "      '<rect x=\"'+x(bimStd('leed.nd','pt1'))+'\" y=\"'+y0+'\" width=\"'+bimClbF(x(mx)-x(bimStd('leed.nd','pt1')))+'\" height=\"24\" fill=\"var(--band)\"/>';")
rep("      var C2=S.conn,lv=C2.sqmi>=400?'above LEED ND\\'s top threshold':(C2.sqmi>=300?'earns LEED ND\\'s connectivity point':(C2.sqmi>=90?'meets LEED ND\\'s prerequisite':'below LEED ND\\'s prerequisite of 90 per square mile'));",
    "      var C2=S.conn,L1=bimStd('leed.nd','case1'),lv=C2.sqmi>bimStd('leed.nd','pt2')?'above LEED ND\\'s top threshold':(C2.sqmi>=bimStd('leed.nd','pt1')?'earns LEED ND\\'s connectivity point':(C2.sqmi>=L1?'meets LEED ND\\'s prerequisite':'below LEED ND\\'s prerequisite of '+L1+' per square mile'));")
rep("+' per sq mi within '+C.r+' m; LEED ND asks 90',C.sqmi>=140?'good':(C.sqmi>=90?'warning':'serious')));",
    "+' per sq mi within '+C.r+' m; LEED ND asks '+bimStd('leed.nd','case1'),C.sqmi>=bimStd('leed.nd','case2')?'good':(C.sqmi>=bimStd('leed.nd','case1')?'warning':'serious')));")
rep("        (C.sqmi>=90?'at or above':'below')+' LEED ND\\'s 90 per square mile'",
    "        (C.sqmi>=bimStd('leed.nd','case1')?'at or above':'below')+' LEED ND\\'s '+bimStd('leed.nd','case1')+' per square mile'")
rep("        cls:C.sqmi>=300?'opportunity':(C.sqmi>=90?'neutral':'constraint'),",
    "        cls:C.sqmi>=bimStd('leed.nd','pt1')?'opportunity':(C.sqmi>=bimStd('leed.nd','case1')?'neutral':'constraint'),")
# the ground: the slope finding's gentle and steep shares are the classes' own edges
rep("if(hn.slope[k]<5)flat++;if(hn.slope[k]>=15)steep++;}",
    "if(hn.slope[k]<sb1)flat++;if(hn.slope[k]>=sb3)steep++;}")
rep("      var hn=bimLandHornOf(D),M=bimLandSiteMask(D,S),Y=bimLandHydroOf(D),n=0,sum=0,mx=0,flat=0,steep=0,k,a2=D.cell*D.cell;",
    "      var hn=bimLandHornOf(D),M=bimLandSiteMask(D,S),Y=bimLandHydroOf(D),n=0,sum=0,mx=0,flat=0,steep=0,k,a2=D.cell*D.cell,sb1=bimStd('land.slope','b1'),sb3=bimStd('land.slope','b3');   /* __acad3dV167 */")
rep("+bimLandPct(flat,n)+' under 5%'+(steep?', '+bimLandPct(steep,n)+' at 15% or more':''),",
    "+bimLandPct(flat,n)+' under '+bimDispNum(sb1,2)+'%'+(steep?', '+bimLandPct(steep,n)+' at '+bimDispNum(sb3,2)+'% or more':''),")
# the frame: a combination found by its key too, so a name made of new factors still finds its case
rep("    for(i=0;i<bimCombos().length;i++)if(bimCombos()[i].name===name)return bimCombos()[i];\n    return null;",
    "    var C=bimCombos();\n    for(i=0;i<C.length;i++)if(C[i].name===name||C[i].key===name)return C[i];\n    return null;")

# ---- 5. the slope classes, the comfort band and the ordered values keep their order ----
rep("        v:[{n:'b1',v:5,u:'%',say:'flat to gentle, up to'},{n:'b2',v:10,u:'%',say:'moderate, up to'},{n:'b3',v:15,u:'%',say:'moderately steep, up to'},{n:'b4',v:25,u:'%',say:'steep, up to'}]}]},",
    "        v:[{n:'b1',v:5,u:'%',say:'flat to gentle, up to',lt:'b2'},{n:'b2',v:10,u:'%',say:'moderate, up to',gt:'b1',lt:'b3'},{n:'b3',v:15,u:'%',say:'moderately steep, up to',gt:'b2',lt:'b4'},{n:'b4',v:25,u:'%',say:'steep, up to',gt:'b3'}]}]},")
rep("          {n:'comfort_t0',v:20,u:'C',say:'the comfort band\\'s lowest temperature'},{n:'comfort_t1',v:27,u:'C',say:'the comfort band\\'s highest temperature'},\n"
    "          {n:'comfort_rh0',v:20,u:'%',say:'the comfort band\\'s lowest humidity'},{n:'comfort_rh1',v:80,u:'%',say:'the comfort band\\'s highest humidity'}]}]},",
    "          {n:'comfort_t0',v:20,u:'C',say:'the comfort band\\'s lowest temperature',lt:'comfort_t1'},{n:'comfort_t1',v:27,u:'C',say:'the comfort band\\'s highest temperature',gt:'comfort_t0'},\n"
    "          {n:'comfort_rh0',v:20,u:'%',say:'the comfort band\\'s lowest humidity',lt:'comfort_rh1'},{n:'comfort_rh1',v:80,u:'%',say:'the comfort band\\'s highest humidity',gt:'comfort_rh0'}]}]},")
rep("{n:'walk_bus',v:8,u:'min',say:'the walk to a bus stop',src:'up to 640 m, about eight minutes'},",
    "{n:'walk_bus',v:8,u:'min',say:'the walk to a bus stop',src:'up to 640 m, about eight minutes',lt:'walk_rail'},")
rep("{n:'walk_rail',v:12,u:'min',say:'the walk to a rail, Tube or DLR station',src:'up to 960 m, 12 minutes'},",
    "{n:'walk_rail',v:12,u:'min',say:'the walk to a rail, Tube or DLR station',src:'up to 960 m, 12 minutes',gt:'walk_bus'},")
rep("    if(!why){a3dToast('Say why '+(x.say||n)+' is overridden: the reason shows on every result that uses it');return false;}",
    "    if(x.gt&&!(num>bimStd(t,x.gt))){a3dToast((x.say||n)+' must be more than '+bimStdFmt(bimStd(t,x.gt),x.u)+' ('+x.gt+')');return false;}\n"
    "    if(x.lt&&!(num<bimStd(t,x.lt))){a3dToast((x.say||n)+' must be less than '+bimStdFmt(bimStd(t,x.lt),x.u)+' ('+x.lt+')');return false;}\n"
    "    if(!why){a3dToast('Say why '+(x.say||n)+' is overridden: the reason shows on every result that uses it');return false;}")

for name, acc, n in TOK:
    if re.search(r'\b%s\b' % re.escape(name), s):
        sys.exit('%s is still read somewhere' % name)

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
