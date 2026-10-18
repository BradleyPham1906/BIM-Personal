#!/usr/bin/env python3
"""V167c: provenance -- every result keeps the standards it used, and says Out of date when they change.

- An analysis drawn in the model keeps a stamp of its topics (the edition, its values, the
  overrides) with its run; its Analyze row turns Out of date when any of them is not what it used,
  and says which and why, and every row names the standards it uses.
- The access data keeps the walking speed its walk times were worked out with, and the context
  the sizes it gave what OpenStreetMap left unsized: the analyses drawn from them say when Analyze
  site has to fetch again.
- A finding names the standards behind it, with an edition applied outside its place or a value
  overridden said so.

Run from the repository root: python3 Phase/patch_phase167c.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'c6305837648eb498a8460e7e35e42350d0536c9f94adb2aeab81f7530147b0b3'   # after patch_phase167b.py

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


# ---- the topics each analysis and each finding uses ----
BLOCK = r'''  /* __acad3dV167: the standards each analysis drawn in the model uses, and the data it is drawn from */
  var BIM_DG_STD={compass:['walk.speed'],noise:['fhwa.fc','app.roads','crtn'],slope:['land.slope'],flood:['fema.zones'],streets:['fhwa.fc','app.roads'],
    cycling:['lts.2012','lts.xing2016','app.roads'],transit:['tfl.ptal'],needs:['guides.walk']};
  var BIM_DG_STD_DATA={transit:'access',walk:'access',needs:'access'};
  /* and each finding */
  var BIM_SA_STD={'access.cycling':['lts.2012','lts.xing2016','app.roads'],'access.transit':['tfl.ptal','walk.speed'],'access.walk':['walk.speed'],
    'access.connectivity':['leed.nd'],'people.daily':['walk.speed'],'climate.comfort':['app.climate'],'climate.degreedays':['app.climate'],
    'climate.wind':['app.climate'],'risk.air':['who.aqg'],'landform.slope':['land.slope'],'water.fema':['fema.zones'],'location.built':['app.context']};
  /* what changed in the standards an analysis used: its own run's, and the data it is drawn from */
  function bimDgStdChanged(a){
    var R=bimDgState().runs[a],out={run:[],data:[]},S;
    if(!R)return out;
    out.run=bimStdChanged(R.std);
    if(BIM_DG_STD_DATA[a]==='access'){S=A3D.site&&A3D.site.access;if(S&&S.std)out.data=bimStdChanged(S.std);}
    return out;
  }
  function bimDgStdText(a){
    var T=(BIM_DG_STD[a]||[]).concat(BIM_DG_STD_DATA[a]==='access'?['walk.speed']:[]);
    return T.length?'Standards: '+T.map(bimStdUsedText).join('; '):'';
  }
  function bimSaStdText(f){var T=f&&BIM_SA_STD[f.auto];return T?'Standards: '+T.map(bimStdUsedText).join('; '):'';}
'''
rep("  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};\n",
    BLOCK + "  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};\n")

# a run keeps its stamp
rep("    D.runs[a]={keys:keys,gone:Object.keys(gone).filter(function(kk){return keys.indexOf(kk)>=0;}),date:bimSaToday(),\n"
    "      legend:run&&run.legend?run.legend:[],note:run&&run.note?run.note:'',source:run&&run.source?run.source:''};",
    "    D.runs[a]={keys:keys,gone:Object.keys(gone).filter(function(kk){return keys.indexOf(kk)>=0;}),date:bimSaToday(),\n"
    "      legend:run&&run.legend?run.legend:[],note:run&&run.note?run.note:'',source:run&&run.source?run.source:'',\n"
    "      std:bimStdStamp(BIM_DG_STD[a]||[])};   /* __acad3dV167: the standards it used */")

# the row: Out of date when they changed, and the standards named
rep("      var st=!R?'Not run yet: Analyze site draws it':(L.length?bimSaN(L.length,'element')+' on Site analysis - '+A.name+(ed?', '+ed+' changed by you':'')+', '+R.date:(R.note||'Nothing to draw'));\n"
    "      return {id:'dg'+A.id,title:A.name,state:!R?null:(L.length?(on?'on':'off'):'warn'),status:st,\n"
    "        extra:R?bimDgLegendHtml(R.legend)+(R.note&&L.length?'<div class=\"a3d-sacap\">'+bimEsc(R.note)+'</div>':'')+(R.source?'<div class=\"a3d-sacap\">Source: '+bimEsc(R.source)+'</div>':''):'',",
    "      var st=!R?'Not run yet: Analyze site draws it':(L.length?bimSaN(L.length,'element')+' on Site analysis - '+A.name+(ed?', '+ed+' changed by you':'')+', '+R.date:(R.note||'Nothing to draw'));\n"
    "      /* __acad3dV167: Out of date when a standard it used changed: an edition, a value, an override */\n"
    "      var SC=R?bimDgStdChanged(A.id):{run:[],data:[]},stale=!!(SC.run.length||SC.data.length),sx=bimDgStdText(A.id);\n"
    "      if(stale)st+='. Out of date: '+(SC.run.length?bimStdChangedText(SC.run)+' since it ran: Run again':'')+(SC.run.length&&SC.data.length?'; ':'')+(SC.data.length?bimStdChangedText(SC.data)+' since the access data was fetched: Analyze site again':'');\n"
    "      return {id:'dg'+A.id,title:A.name,state:!R?null:(stale?'stale':(L.length?(on?'on':'off'):'warn')),status:st,\n"
    "        extra:R?bimDgLegendHtml(R.legend)+(R.note&&L.length?'<div class=\"a3d-sacap\">'+bimEsc(R.note)+'</div>':'')+(R.source?'<div class=\"a3d-sacap\">Source: '+bimEsc(R.source)+'</div>':'')+\n"
    "          (sx?'<div class=\"a3d-sacap a3d-sastd\" data-dgstd=\"'+A.id+'\">'+bimEsc(sx)+'</div>':''):'',")

# a finding names its standards
rep("      bimEsc(f.source||'no source given')+' \\u00b7 '+bimEsc(f.date)+'</div></div>';\n  }",
    "      bimEsc(f.source||'no source given')+' \\u00b7 '+bimEsc(f.date)+'</div>'+\n"
    "      (bimSaStdText(f)?'<div class=\"a3d-safstd\" data-safstd=\"'+bimEsc(f.auto)+'\">'+bimEsc(bimSaStdText(f))+'</div>':'')+'</div>';   /* __acad3dV167 */\n  }")

# the access data keeps the walking speed it used; the context the sizes it gave
rep("    return {speed:v,bands:BIM_ACC_BANDS.slice(),maxT:MAXT,front:BIM_ACC_FRONT,",
    "    return {speed:v,std:bimStdStamp(['walk.speed']),bands:BIM_ACC_BANDS.slice(),maxT:MAXT,front:BIM_ACC_FRONT,   /* __acad3dV167: std */")
rep("      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc,server:osm&&osm.ok?bimMapHost(osm.server):null};",
    "      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc,server:osm&&osm.ok?bimMapHost(osm.server):null,std:bimStdStamp(['app.context'])};   /* __acad3dV167: std */")

# the finding's standards line, small
rep(".a3d-safm{", ".a3d-safstd{font-size:10.5px;line-height:1.4;color:#8a96a3;margin-top:3px}\n  .a3d-safm{")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
