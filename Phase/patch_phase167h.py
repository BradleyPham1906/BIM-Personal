#!/usr/bin/env python3
"""V167h: no standard's value left in code -- what the suite's scan found.

The suite reads the build's source for a standard's number beside its unit outside the registry, as
the design asked (research-standards-registry.md, "Values in words"). It found seven:
- the noise layer's "For scale" row: WHO's road traffic guideline, 53 dB Lden, written in V164 with
  no record. Read at its source today (WHO Regional Office for Europe, Environmental Noise
  Guidelines for the European Region, 2018, 3.1: 53 dB Lden and 45 dB Lnight, both strong
  recommendations), it is a record, applied outside its place everywhere: guidance for the WHO
  European Region, adopted nowhere as a rule;
- the Access board's note on connectivity: LEED's 90, 140 and 300 and its quarter mile;
- the climate board's key and its comfort KPI: the comfort band, 20 to 27 degrees and 20 to 80%;
- the climate board's note: "the WHO 2021 guidelines", now the edition in force and its source;
- the relief finding (V138): the share steeper than 15%, and its classes at 5% and 15% -- the slope
  classes' edges;
- SLOPEMAP's description: the terrain's bands;
- Analyze site's context radius, raised to 300 m "for the noise and the views": at least CRTN's
  range now, so an override of the range reaches as far.

And two corrections: PennDOT's DM-2 rested on a search summary, which is not a source: it is listed
unread (U), as ACI 318 and AISC 360 are, with nothing claimed. And V167f's touch rule for the group's
buttons repeated V149's, which already makes Properties' buttons 36 px on touch: only its date field
needed it.

Run from the repository root: python3 Phase/patch_phase167h.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '2c813cc20ffd655f9b80c868bd999b85334fd556e31e6ad35a9805762c03fb0c'   # after patch_phase167g.py

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


# ---- WHO's road traffic noise guideline, a record ----
rep("    /* ---- cycling ---- */\n    {id:'lts.2012',",
    "    {id:'who.noise',title:'WHO environmental noise guidelines: road traffic',pub:'World Health Organization Regional Office for Europe',kind:'guideline',area:'Roads and noise',use:'Noise layer, for scale',anywhere:true,\n"
    "      eds:[{id:'who.noise.2018',name:'Environmental Noise Guidelines for the European Region (2018)',pub:'2018',st:'current',where:'Guidance for the WHO European Region, adopted nowhere as a rule',adopt:[],\n"
    "        src:{t:'WHO Regional Office for Europe, Environmental Noise Guidelines for the European Region',w:'3.1, road traffic noise: the two strong recommendations',u:'https://iris.who.int/handle/10665/279952',lv:'P',read:'2026-10-18'},\n"
    "        v:[{n:'road_lden',v:53,u:'dB',say:'road traffic noise, average exposure (Lden)',src:'53.3 dB rounded to 53'},{n:'road_lnight',v:45,u:'dB',say:'road traffic noise at night (Lnight)'}]}]},\n"
    "    /* ---- cycling ---- */\n    {id:'lts.2012',")
rep("    'per sq mi':[' per sq mi',' per sq mi'],", "    'per sq mi':[' per sq mi',' per sq mi'],dB:[' dB',' dB'],")
rep("['For scale','WHO advises road noise below 53 dB Lden; CRTN\\'s L10,18h reads about 2 dB above it']",
    "['For scale','WHO advises road noise below '+bimStdSay('who.noise','road_lden')+' Lden; CRTN\\'s L10,18h reads about 2 dB above it']")
rep("noise:['fhwa.fc','app.roads','crtn'],slope:", "noise:['fhwa.fc','app.roads','crtn','who.noise'],slope:")

# ---- the Access board's note on connectivity ----
rep("Connectivity after LEED ND v4 (Neighborhood Pattern and Design): 90 intersections per square mile within a quarter mile to qualify, 140 inside a project with streets of its own, points from 300.</li>'",
    "Connectivity after '+bimEsc((bimStdEdition('leed.nd')||{}).name||'LEED ND')+' (Neighborhood Pattern and Design): '+bimStd('leed.nd','case1')+' intersections per square mile within '+bimStd('leed.nd','radius')+' m to qualify, '+bimStd('leed.nd','case2')+' inside a project with streets of its own, points from '+bimStd('leed.nd','pt1')+'.</li>'")

# ---- the climate board: the comfort band, and WHO's edition ----
rep("'Of the year\\'s hours, 20\u201327 \u00b0C and 20\u201380% RH'",
    "'Of the year\\'s hours, '+bimClimUsedComfort().t0+'\u2013'+bimClimUsedComfort().t1+' \u00b0C and '+bimClimUsedComfort().rh0+'\u2013'+bimClimUsedComfort().rh1+'% RH'")
rep("['transparent','Comfort zone: 20\u201327 \u00b0C, 20\u201380% RH']",
    "['transparent','Comfort zone: '+bimClimUsedComfort().t0+'\u2013'+bimClimUsedComfort().t1+' \u00b0C, '+bimClimUsedComfort().rh0+'\u2013'+bimClimUsedComfort().rh1+'% RH']")
rep("against the <a href=\"https://www.who.int/publications/i/item/9789240034228\" target=\"_blank\" rel=\"noopener\">WHO 2021 guidelines</a>.</li>'",
    "against the <a href=\"'+bimEsc(((bimStdEdition('who.aqg')||{}).src||{}).u||'')+'\" target=\"_blank\" rel=\"noopener\">'+bimEsc((bimStdEdition('who.aqg')||{}).name||'WHO air quality guidelines')+'</a>.</li>'")

# ---- the relief finding's steep share and classes: the slope classes' edges ----
rep("    var T=tin.tris||[],out=tin.outside||{},i,a,b,c,P=tin.P,H=tin.H,area=0,sum=0,mx=0,steep=0;",
    "    var T=tin.tris||[],out=tin.outside||{},i,a,b,c,P=tin.P,H=tin.H,area=0,sum=0,mx=0,steep=0,sb3=bimStd('land.slope','b3')/100;   /* __acad3dV167h */")
rep("if(g>mx)mx=g;if(g>0.15)steep+=A;", "if(g>mx)mx=g;if(g>sb3)steep+=A;")
rep("        if(sl&&mean>=30){cl='constraint';sv=3;}else if(sl&&mean>=15){cl='constraint';sv=2;}else if(sl&&mean<5){cl='opportunity';}",
    "        if(sl&&mean>=30){cl='constraint';sv=3;}else if(sl&&mean>=bimStd('land.slope','b3')){cl='constraint';sv=2;}else if(sl&&mean<bimStd('land.slope','b1')){cl='opportunity';}   /* __acad3dV167h */")
rep("+Math.round(sl.steepShare*100)+'% of it steeper than 15%':''),",
    "+Math.round(sl.steepShare*100)+'% of it steeper than '+bimDispNum(bimStd('land.slope','b3'),2)+'%':''),")
rep("'climate.wind':['app.climate'],'risk.air':['who.aqg'],'landform.slope':['land.slope'],",
    "'climate.wind':['app.climate'],'risk.air':['who.aqg'],'landform.slope':['land.slope'],'landform.terrain':['land.slope'],")

# ---- SLOPEMAP's description ----
rep("'Colour the terrain by slope in bands (0 to 2%, 2 to 5%, 5 to 8.33% ...), with the area of each'",
    "'Colour the terrain by slope, in the bands of the standards registry (Properties > Site > Standards), with the area of each'")

# ---- the context radius: at least CRTN's range ----
rep("  var BIM_SITERUN_RADIUS=300;   /* far enough for the noise (CRTN holds to 300 m) and the views */\n",
    "  var BIM_SITERUN_RADIUS=300;   /* far enough for the views; the noise needs CRTN's range, the registry's */\n"
    "  function bimSiteRunRadius(){return Math.max(BIM_SITERUN_RADIUS,Math.ceil(bimDgCrtnMax()||0));}   /* __acad3dV167h */\n")
rep("      if(cs.radius<BIM_SITERUN_RADIUS){A3D.site.context=A3D.site.context||{};A3D.site.context.radius=BIM_SITERUN_RADIUS;wid='; the context radius is '+BIM_SITERUN_RADIUS+' m now (it was '+cs.radius+' m), for the noise and the views';}",
    "      if(cs.radius<bimSiteRunRadius()){A3D.site.context=A3D.site.context||{};A3D.site.context.radius=bimSiteRunRadius();wid='; the context radius is '+bimSiteRunRadius()+' m now (it was '+cs.radius+' m), for the noise and the views';}")
rep("'+Math.max(cs.radius,BIM_SITERUN_RADIUS)+' m around ...');", "'+Math.max(cs.radius,bimSiteRunRadius())+' m around ...');")

# ---- PennDOT's DM-2: seen only in a search summary, so not read (U), as ACI 318 and AISC 360 are ----
rep("      eds:[{id:'penndot.dm2.c11',name:'Publication 13M, Change No. 11 (March 2024), being replaced by Publication 13, Contextual Roadway Design',pub:'2024-03',st:'current',where:'Pennsylvania',adopt:[{at:'us-pa',from:'2024-03'}],\n"
    "        src:{t:'PennDOT, Publication 13M title page',w:'Change No. 11, March 2024, marked current; seen in a search summary, as PennDOT\\'s host did not answer from here',u:'https://www.dot.state.pa.us/public/pubsforms/Publications/PUB%2013M/Pub%2013M%20Title%20Page.pdf',lv:'S',read:'2026-10-18'},v:[]}]},",
    "      eds:[{id:'penndot.dm2.unread',name:'Its current change was not read: PennDOT\\'s publications host did not answer from here',pub:'',st:'current',where:'Pennsylvania',adopt:[],\n"
    "        src:{t:'Pennsylvania Department of Transportation',w:'not read: a search summary names Change No. 11 (March 2024), which is not a source',u:'https://www.dot.state.pa.us/public/pubsforms/Publications/PUB%2013M/Pub%2013M%20Title%20Page.pdf',lv:'U',read:'2026-10-18'},v:[]}]},")

# ---- on touch, Properties' buttons are 36 px already (V149's rule): the group's own rule keeps only its date ----
rep(".a3d-pgbody [data-propstdact]{min-height:36px;min-width:44px;padding:6px 10px;font-size:12.5px;margin:2px 0}.a3d-stdpick select,.a3d-pgbody [data-propstd]{min-height:36px}}",
    ".a3d-pgbody [data-propstd]{min-height:36px}}")

# ---- the marker ----
rep("drafts,sheet,packadopted,packagain';", "drafts,sheet,packadopted,packagain,whonoise,noliterals,dm2unread';")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
