#!/usr/bin/env python3
"""V167f: what the suite found -- every result says the values it was worked out with.

- The compass rings are the frame analysis's ('frame', not 'compass'): its run keeps the walking
  speed it used, and its row names it.
- The data fetched once and drawn from many times keep a stamp of the standards they were worked
  out with: the access data (the walking speed, LEED's radius), the site context (its sizes), the
  climate (the degree-day base, calm, the rose's bins, the comfort band) and the air quality (WHO's
  levels). A stamp may name one value of a topic ('leed.nd|radius'), so a threshold applied as it is
  drawn does not make the data out of date. Data and runs from before V167 are taken as worked out
  with the editions' own values.
- The climate and air findings and the climate board state the values the data was worked out
  with, never a value changed since; the finding's standards line says Out of date and why, and
  that Analyze site fetches it again. The views and noise rows, drawn from the site context, and the
  winds, drawn from the climate, say so too.
- WHO's four 24-hour interim targets for PM2.5 (Table 0.1) are the registry's: the air chart draws
  them from it.

Run from the repository root: python3 Phase/patch_phase167f.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'd6c1b7d7441fce4e54c79173a8f7b7d2fb555225ca9231738ab7bac78d724e08'   # after patch_phase167e.py

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


# ---- WHO's 24-hour interim targets ----
rep("          {n:'pm25_it1_year',v:35,u:'ug/m3',say:'the first interim target, annual'}]}]},",
    "          {n:'pm25_it1_year',v:35,u:'ug/m3',say:'the first interim target, annual'},\n"
    "          {n:'pm25_24h_it1',v:75,u:'ug/m3',say:'the first interim target, 24-hour'},{n:'pm25_24h_it2',v:50,u:'ug/m3',say:'the second interim target, 24-hour'},\n"
    "          {n:'pm25_24h_it3',v:37.5,u:'ug/m3',say:'the third interim target, 24-hour'},{n:'pm25_24h_it4',v:25,u:'ug/m3',say:'the fourth interim target, 24-hour'}]}]},")
rep("    [[bimClimWho24(),'WHO 24-hour guideline, '+bimClimWho24()],[25,'WHO interim target 4, 25'],[37.5,'Interim target 3, 37.5'],[50,'Interim target 2, 50'],[75,'Interim target 1, 75']].forEach(function(g,i){",
    "    var it4=bimStd('who.aqg','pm25_24h_it4'),it3=bimStd('who.aqg','pm25_24h_it3'),it2=bimStd('who.aqg','pm25_24h_it2'),it1=bimStd('who.aqg','pm25_24h_it1');   /* __acad3dV167 */\n"
    "    [[bimClimWho24(),'WHO 24-hour guideline, '+bimClimWho24()],[it4,'WHO interim target 4, '+it4],[it3,'Interim target 3, '+it3],[it2,'Interim target 2, '+it2],[it1,'Interim target 1, '+it1]].forEach(function(g,i){")

# ---- a stamp of one value; the editions' own values for what came before ----
rep("  function bimStdStamp(ts){\n"
    "    var L=[],O=bimStdS().ov||{};\n"
    "    (ts||[]).forEach(function(t){\n"
    "      var r=bimStdResolve(t),e=r&&r.ed,ov={},k;\n"
    "      for(k in O)if(O.hasOwnProperty(k)&&k.indexOf(t+'|')===0&&O[k]&&typeof O[k].v==='number')ov[k.slice(t.length+1)]=O[k].v;\n"
    "      L.push({t:t,e:e?e.id:null,how:r?r.how:'none',ov:ov,h:bimHash(bimCanon({e:e?e.id:null,v:e?e.v:null,ov:ov}))});\n"
    "    });\n"
    "    return {at:bimSaToday(),list:L};\n"
    "  }\n",
    "  /* a topic, or one value of it ('leed.nd|radius'); bare: as the editions have them, no override */\n"
    "  function bimStdStamp(ts,bare){\n"
    "    var L=[],O=bare?{}:(bimStdS().ov||{});\n"
    "    (ts||[]).forEach(function(t0){\n"
    "      var j=String(t0).indexOf('|'),t=j<0?t0:t0.slice(0,j),n=j<0?null:t0.slice(j+1),r=bimStdResolve(t),e=r&&r.ed,ov={},k;\n"
    "      for(k in O)if(O.hasOwnProperty(k)&&k.indexOf(t+'|')===0&&O[k]&&typeof O[k].v==='number'&&(n===null||k===t+'|'+n))ov[k.slice(t.length+1)]=O[k].v;\n"
    "      L.push({t:t0,e:e?e.id:null,how:r?r.how:'none',ov:ov,h:bimHash(bimCanon({e:e?e.id:null,v:e?(n===null?e.v:bimStdVal(e,n)):null,ov:ov}))});\n"
    "    });\n"
    "    return {at:bimSaToday(),list:L};\n"
    "  }\n"
    "  /* what a result kept, or for one from before V167 the editions' own values */\n"
    "  function bimStdDataStamp(st,ts){return st&&Array.isArray(st.list)?st:bimStdStamp(ts,true);}\n"
    "  function bimStdTopicOf(t){t=String(t);var j=t.indexOf('|');return j<0?t:t.slice(0,j);}\n"
    "  /* the value of the edition in force, an override set aside */\n"
    "  function bimStdOwn(t,n){var r=bimStdResolve(t),x=r&&r.ed?bimStdVal(r.ed,n):null;return x?x.v:undefined;}\n")
rep("      var R=bimStdRec(c.t),nm=R?R.title:c.t,bits=[];",
    "      var R=bimStdRec(bimStdTopicOf(c.t)),nm=R?R.title:c.t,bits=[];")

# ---- the data and what they are worked out with ----
rep("  var BIM_DG_STD={compass:['walk.speed'],",
    "  var BIM_DG_STD={frame:['walk.speed'],")
rep("  var BIM_DG_STD_DATA={transit:'access',walk:'access',needs:'access'};\n",
    "  var BIM_DG_STD_DATA={transit:'access',walk:'access',needs:'access',views:'context',noise:'context',wind:'climate'};\n"
    "  /* the data fetched once and drawn from many times: the standards each is worked out with, the topics a\n"
    "     row names for it, and its stamp */\n"
    "  var BIM_STD_DATA={\n"
    "    access:{ts:['walk.speed','leed.nd|radius'],say:['walk.speed'],name:'the access data',of:function(){var S=A3D.site&&A3D.site.access;return S?{st:S.std}:null;}},\n"
    "    context:{ts:['app.context'],say:['app.context'],name:'the site context',of:function(){var c=A3D.site&&A3D.site.context&&A3D.site.context.last;return c?{st:c.std}:null;}},\n"
    "    climate:{ts:['app.climate'],say:['app.climate'],name:'the climate data',of:function(){var C=A3D.site&&A3D.site.climate;return C&&(C.normals||C.hourly)?{st:C.std}:null;}},\n"
    "    air:{ts:['who.aqg|pm25_24h','who.aqg|pm25_year','who.aqg|pm25_it1_year'],say:['who.aqg'],name:'the air quality data',of:function(){var Q=A3D.site&&A3D.site.risk&&A3D.site.risk.air;return Q?{st:Q.std}:null;}}};\n"
    "  /* the standards a kind of data was worked out with that are not what they are now; only, the topics that matter */\n"
    "  function bimStdDataChanged(kind,only){\n"
    "    var K=BIM_STD_DATA[kind],d=K&&K.of(),ch;\n"
    "    if(!d)return [];\n"
    "    ch=bimStdChanged(bimStdDataStamp(d.st,K.ts));\n"
    "    return only?ch.filter(function(c){return only.indexOf(bimStdTopicOf(c.t))>=0;}):ch;\n"
    "  }\n")
rep("    var R=bimDgState().runs[a],out={run:[],data:[]},S;\n"
    "    if(!R)return out;\n"
    "    out.run=bimStdChanged(R.std);\n"
    "    if(BIM_DG_STD_DATA[a]==='access'){S=A3D.site&&A3D.site.access;if(S&&S.std)out.data=bimStdChanged(S.std);}\n"
    "    return out;\n",
    "    var R=bimDgState().runs[a],k=BIM_DG_STD_DATA[a]||null,out={run:[],data:[],kind:k};\n"
    "    if(!R)return out;\n"
    "    out.run=bimStdChanged(bimStdDataStamp(R.std,BIM_DG_STD[a]||[]));\n"
    "    if(k)out.data=bimStdDataChanged(k,BIM_STD_DATA[k].say);\n"
    "    return out;\n")
rep("    var T=(BIM_DG_STD[a]||[]).concat(BIM_DG_STD_DATA[a]==='access'?['walk.speed']:[]);\n",
    "    var k=BIM_DG_STD_DATA[a],T=(BIM_DG_STD[a]||[]).slice();\n"
    "    if(k)BIM_STD_DATA[k].say.forEach(function(t){if(T.indexOf(t)<0)T.push(t);});\n")
rep("  function bimSaStdText(f){var T=f&&BIM_SA_STD[f.auto];return T?'Standards: '+T.map(bimStdUsedText).join('; '):'';}\n",
    "  /* the data each finding is worked out from */\n"
    "  var BIM_SA_STD_DATA={'access.transit':'access','access.walk':'access','access.connectivity':'access','people.daily':'access','climate.comfort':'climate',\n"
    "    'climate.degreedays':'climate','climate.wind':'climate','risk.air':'air','location.built':'context'};\n"
    "  function bimSaStdText(f){\n"
    "    var T=f&&BIM_SA_STD[f.auto],k=f&&BIM_SA_STD_DATA[f.auto],s,ch;\n"
    "    if(!T)return '';\n"
    "    s='Standards: '+T.map(bimStdUsedText).join('; ');\n"
    "    ch=k?bimStdDataChanged(k,T):[];\n"
    "    if(ch.length)s+='. Out of date: '+bimStdChangedText(ch)+' since '+BIM_STD_DATA[k].name+' was fetched: Analyze site again';\n"
    "    return s;\n"
    "  }\n")
rep("+(SC.data.length?bimStdChangedText(SC.data)+' since the access data was fetched: Analyze site again':'');",
    "+(SC.data.length?bimStdChangedText(SC.data)+' since '+BIM_STD_DATA[SC.kind].name+' was fetched: Analyze site again':'');")
rep("    return {speed:v,std:bimStdStamp(['walk.speed']),bands:",
    "    return {speed:v,std:bimStdStamp(BIM_STD_DATA.access.ts),bands:")
rep(",std:bimStdStamp(['app.context'])};   /* __acad3dV167: std */",
    ",std:bimStdStamp(BIM_STD_DATA.context.ts)};   /* __acad3dV167: std */")

# ---- the climate and the air keep the values they were worked out with ----
rep("      if(Hh)C.hourly=Hh;\n",
    "      if(Hh)C.hourly=Hh;\n"
    "      /* __acad3dV167: the values they were worked out with, and their stamp */\n"
    "      if(D)D.used={base:bimClimBase()};\n"
    "      if(Hh)Hh.used={calm:bimClimCalm(),comfort:JSON.parse(JSON.stringify(bimClimComfort()))};\n"
    "      if(D||Hh)C.std=bimStdStamp(BIM_STD_DATA.climate.ts);\n")
rep("      if(Q){K.air=Q;K.airSrc='CAMS (Copernicus), via Open-Meteo';}",
    "      if(Q){Q.used={who24:bimClimWho24()};Q.std=bimStdStamp(BIM_STD_DATA.air.ts);K.air=Q;K.airSrc='CAMS (Copernicus), via Open-Meteo';}   /* __acad3dV167: used, std */")
rep("  function bimClimFmt(v,d){",
    "  /* __acad3dV167: the values the climate and the air were worked out with, for what states them */\n"
    "  function bimClimUsedBase(){var N=A3D.site&&A3D.site.climate&&A3D.site.climate.normals;return N&&N.used&&typeof N.used.base==='number'?N.used.base:bimStdOwn('app.climate','base');}\n"
    "  function bimClimUsedComfort(){var H=A3D.site&&A3D.site.climate&&A3D.site.climate.hourly;return H&&H.used&&H.used.comfort?H.used.comfort:\n"
    "    {t0:bimStdOwn('app.climate','comfort_t0'),t1:bimStdOwn('app.climate','comfort_t1'),rh0:bimStdOwn('app.climate','comfort_rh0'),rh1:bimStdOwn('app.climate','comfort_rh1')};}\n"
    "  function bimClimUsedCalm(){var H=A3D.site&&A3D.site.climate&&A3D.site.climate.hourly;return H&&H.used&&typeof H.used.calm==='number'?H.used.calm:(H&&H.wind&&Array.isArray(H.wind.bins)?H.wind.bins[0]:bimStdOwn('app.climate','calm'));}\n"
    "  function bimClimUsedBins(){var H=A3D.site&&A3D.site.climate&&A3D.site.climate.hourly;return H&&H.wind&&Array.isArray(H.wind.bins)?H.wind.bins:bimClimWindBins();}\n"
    "  function bimClimUsedWho24(){var Q=A3D.site&&A3D.site.risk&&A3D.site.risk.air;return Q&&Q.used&&typeof Q.used.who24==='number'?Q.used.who24:bimStdOwn('who.aqg','pm25_24h');}\n"
    "  function bimClimFmt(v,d){")

# the findings and the board: from bimClimAuto to the board's end
a = s.index("  function bimClimAuto(){")
b = s.index("  function bimClbOpen(kind){")
seg = s[a:b]
for old, new, n in (('bimClimBase()', 'bimClimUsedBase()', 4), ('bimClimComfort()', 'bimClimUsedComfort()', 11),
                    ('bimClimWho24()', 'bimClimUsedWho24()', 7), ('bimClimCalm()', 'bimClimUsedCalm()', 1),
                    ('bimClimWindBins()', 'bimClimUsedBins()', 1)):
    if seg.count(old) != n:
        sys.exit('the findings and the board: expected %d of %s, found %d' % (n, old, seg.count(old)))
    seg = seg.replace(old, new)
s = s[:a] + seg + s[b:]

# ---- a standards change works the findings out again from the data kept, in the same undo step ----
rep("  function bimStdDone(){\n"
    "    try{refreshProps();}",
    "  /* the findings made from the data are worked out again with the standards as they are now: no fetch,\n"
    "     the data's own values where it was worked out with them, and said Out of date where it was */\n"
    "  function bimStdRefill(){\n"
    "    var s=A3D.site&&A3D.site.analysis,A,by={},n=0;\n"
    "    if(!s||!Array.isArray(s.findings)||!s.findings.some(function(x){return x&&x.auto;}))return 0;\n"
    "    A=bimSaAuto();A.forEach(function(a){by[a.auto]=a;});\n"
    "    s.findings.forEach(function(f){var a=f&&f.auto&&by[f.auto];if(!a)return;\n"
    "      if(f.value!==a.value||f.title!==a.title)n++;\n"
    "      f.title=a.title;f.value=a.value;f.source=a.source;f.date=a.date;f.cls=bimSaPair(BIM_SA_CLS,a.cls)?a.cls:'neutral';f.sev=a.sev||1;});\n"
    "    if(typeof bimSaRefresh==='function')bimSaRefresh(true);\n"
    "    return n;\n"
    "  }\n"
    "  function bimStdDone(){\n"
    "    try{bimStdRefill();}catch(e0){console.warn('[BIM] The findings could not be worked out again after a standards change',e0);}\n"
    "    try{refreshProps();}")

# ---- on a touch screen the group's buttons, its edition list and its date are finger-sized ----
rep("  @media (pointer:coarse){.a3d-stdov input[type=number],.a3d-stdov input[type=text]{min-height:36px;font-size:16px}}",
    "  @media (pointer:coarse){.a3d-stdov input[type=number],.a3d-stdov input[type=text]{min-height:36px;font-size:16px}\n"
    "    .a3d-pgbody [data-propstdact]{min-height:36px;min-width:44px;padding:6px 10px;font-size:12.5px;margin:2px 0}.a3d-stdpick select,.a3d-pgbody [data-propstd]{min-height:36px}}")

# ---- the hooks and the marker ----
rep("  window.__a3dDgStdChanged=function(a){return bimDgStdChanged(a);};\n",
    "  window.__a3dDgStdChanged=function(a){return bimDgStdChanged(a);};\n"
    "  window.__a3dStdDataChanged=function(k,only){return bimStdDataChanged(k,only||null);};\n")
rep("standardsgroup,standardscommand,valuesinwords';", "standardsgroup,standardscommand,valuesinwords,datastamps,usedvalues,valuestamps,framestd,refill,touchsizes';")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
