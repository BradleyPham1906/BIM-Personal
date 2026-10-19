#!/usr/bin/env python3
"""V168a: land -- the standards and the data.

- The registry (V167) takes four topics, in a new area, Land and green:
  - LBCS's activity dimension (APA): the nine families and their colours, read in APA's workbook;
  - Spacematrix (Berghauser Pont and Haupt): the measures, as Buildings and Cities' box defines them;
  - 3-30-300, as Browning et al. (2024) measure it: 3 trees seen, 30% canopy, 300 m to a public green
    space of at least 0.5 ha;
  - the app's land settings: the owner's 500 m neighbourhood and 8 families (2026-10-18), the 400 m
    square and its 100 m cells, how far a tree seen counts, and the crosswalk from OpenStreetMap's tags
    to LBCS's activities, checked against LBCS's descriptions.
- The context asks for the land use the crosswalk reads: OpenStreetMap's land use values beyond the six
  V157 drew, and the areas of amenities, leisure and tourism (a school's grounds, a car park, a pitch, a
  hotel's). A building keeps its courtyards' outlines, for the ground it covers.

Run from the repository root: python3 Phase/patch_phase168a.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = 'c53d8e035c1ba9f8c85a09777e50c5c0d98bf6dc1f5dd8914d0c418db83959a8'   # V166d, main at 065bfec

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


# ---- the registry: four topics in Land and green ----
XW = (
    "'landuse=residential':1000,'building=house':1000,'building=apartments':1000,'building=residential':1000,'building=detached':1000,'building=semidetached_house':1000,"
    "'building=terrace':1000,'building=bungalow':1000,'building=dormitory':1000,'building=hotel':1000,'tourism=hotel':1000,'tourism=motel':1000,'tourism=guest_house':1000,"
    "'tourism=hostel':1000,'amenity=nursing_home':1000,'social_facility=group_home':1000,\n"
    "            'landuse=commercial':2000,'landuse=retail':2000,'shop=*':2000,'office=*':2000,'building=commercial':2000,'building=retail':2000,'building=office':2000,"
    "'building=supermarket':2000,'building=kiosk':2000,'amenity=restaurant':2000,'amenity=cafe':2000,'amenity=fast_food':2000,'amenity=pub':2000,'amenity=bar':2000,"
    "'amenity=bank':2000,'amenity=marketplace':2000,\n"
    "            'landuse=industrial':3000,'landuse=construction':3000,'landuse=landfill':3000,'building=industrial':3000,'building=warehouse':3000,'building=factory':3000,"
    "'man_made=works':3000,'man_made=wastewater_plant':3000,'amenity=recycling':3000,\n"
    "            'landuse=education':4000,'landuse=institutional':4000,'landuse=civic_admin':4000,'landuse=cemetery':4000,'landuse=military':4000,'landuse=school':4000,"
    "'amenity=school':4000,'amenity=university':4000,'amenity=college':4000,'amenity=kindergarten':4000,'amenity=hospital':4000,'amenity=clinic':4000,'amenity=doctors':4000,"
    "'amenity=library':4000,'amenity=police':4000,'amenity=fire_station':4000,'amenity=courthouse':4000,'amenity=post_office':4000,'amenity=prison':4000,'amenity=grave_yard':4000,"
    "'building=school':4000,'building=university':4000,'building=college':4000,'building=kindergarten':4000,'building=hospital':4000,'building=civic':4000,"
    "'building=government':4000,'building=public':4000,'power=substation':4000,\n"
    "            'landuse=railway':5000,'landuse=garages':5000,'amenity=parking':5000,'building=garage':5000,'building=garages':5000,'building=parking':5000,"
    "'industrial=port':5000,'landuse=port':5000,'aeroway=aerodrome':5000,'aeroway=apron':5000,\n"
    "            'amenity=bus_station':6000,'building=train_station':6000,'building=transportation':6000,'aeroway=terminal':6000,'leisure=stadium':6000,'building=stadium':6000,"
    "'amenity=theatre':6000,'amenity=cinema':6000,'amenity=arts_centre':6000,'amenity=community_centre':6000,'amenity=place_of_worship':6000,'amenity=townhall':6000,"
    "'landuse=religious':6000,'landuse=churchyard':6000,'building=church':6000,'building=cathedral':6000,'building=chapel':6000,'building=mosque':6000,"
    "'building=synagogue':6000,'building=temple':6000,'tourism=museum':6000,'tourism=gallery':6000,'tourism=zoo':6000,'tourism=aquarium':6000,\n"
    "            'leisure=park':7000,'leisure=playground':7000,'leisure=pitch':7000,'leisure=sports_centre':7000,'leisure=golf_course':7000,'leisure=garden':7000,"
    "'leisure=track':7000,'leisure=marina':7000,'landuse=recreation_ground':7000,'landuse=village_green':7000,'tourism=theme_park':7000,'tourism=camp_site':7000,\n"
    "            'landuse=farmland':8000,'landuse=field':8000,'landuse=farmyard':8000,'landuse=orchard':8000,'landuse=vineyard':8000,'landuse=allotments':8000,"
    "'landuse=plant_nursery':8000,'landuse=greenhouse_horticulture':8000,'landuse=aquaculture':8000,'landuse=meadow':8000,'landuse=forest':8000,'landuse=quarry':8000,\n"
    "            'natural=wood':9000,'natural=scrub':9000,'natural=grassland':9000,'landuse=brownfield':9000,'landuse=greenfield':9000,'landuse=grass':9000,'landuse=flowerbed':9000"
)
rep("    {id:'app.climate',title:'Climate readings'",
    "    /* ---- __acad3dV168: land use, form and green ---- */\n"
    "    {id:'lbcs.activity',title:'Land-Based Classification Standards (LBCS): activity',pub:'American Planning Association',kind:'classification',area:'Land and green',use:'Land use layer, its key and its finding',anywhere:true,\n"
    "      eds:[{id:'lbcs.activity.apa',name:'LBCS Activity Dimension, with APA\\'s colour workbook',pub:'',st:'current',where:'A model classification for planning in the United States, adopted nowhere as a rule',adopt:[],\n"
    "        src:{t:'American Planning Association, LBCS Activity Dimension with Descriptions, and its workbook of colours for every dimension (LBCSColorForAllDimensions.xls)',w:'the nine top-level activities, one colour each (the workbook\\'s hex and RGB strings, which agree; its separate Green and Blue columns are swapped), and the descriptions the crosswalk is checked against',u:'https://www.planning.org/lbcs/standards/activity/',lv:'P',read:'2026-10-18'},\n"
    "        v:[{n:'families',t:1,say:'the top-level activities, each with its colour',v:[[1000,'Residential activities','FFFF00'],[2000,'Shopping, business, or trade','FF0000'],[3000,'Industrial, manufacturing, and waste-related','A020F0'],\n"
    "          [4000,'Social, institutional, or infrastructure-related','0000FF'],[5000,'Travel or movement','BEBEBE'],[6000,'Mass assembly of people','2F4F4F'],[7000,'Leisure','90EE90'],\n"
    "          [8000,'Natural resources-related','228B22'],[9000,'No human activity or unclassifiable','FFFFFF']]}]}]},\n"
    "    {id:'spacematrix',title:'Spacematrix: density and form',pub:'Berghauser Pont and Haupt',kind:'method',area:'Land and green',use:'Figure-ground layer and the density finding',anywhere:true,\n"
    "      eds:[{id:'spacematrix.2010',name:'Spacematrix: Space, Density and Urban Form (2010)',pub:'2010',st:'current',where:'A research method, used anywhere',adopt:[{at:'*',from:'2010'}],\n"
    "        src:{t:'Godoy-Shimizu, Steadman and Evans, Density and morphology: from the building scale to the city scale, Buildings and Cities 2(1), 2021 (CC BY 4.0), its box of Spacemate\\'s definitions; with Berghauser Pont, Measuring urban form',w:'FSI the floor area over the land, GSI the ground floor over the land, FSI over GSI the storeys; FSI, GSI and N the main measures; OSR as (1 - GSI) / FSI from papers citing the book (S), the book itself not read',u:'https://doi.org/10.5334/bc.83',lv:'P',read:'2026-10-18'},method:'spacematrix.2010',v:[]}]},\n"
    "    {id:'green.33300',title:'The 3-30-300 rule for trees and green space',pub:'Konijnendijk; measured by Browning et al.',kind:'guideline',area:'Land and green',use:'Green and trees layer and the 3-30-300 finding',anywhere:true,\n"
    "      eds:[{id:'green.33300.2024',name:'Measuring the 3-30-300 rule (Browning et al., 2024), after Konijnendijk (2023)',pub:'2024',st:'current',where:'A rule of thumb, used anywhere',adopt:[{at:'*',from:'2024'}],\n"
    "        src:{t:'Browning et al., Measuring the 3-30-300 rule to help cities meet nature access thresholds, Science of the Total Environment 907, 167739 (2024), the author manuscript in full',w:'the rule as the paper states it, the green space public and at least 0.5 ha, within 300 m by the network; no radius given for the neighbourhood',u:'https://doi.org/10.1016/j.scitotenv.2023.167739',lv:'P',read:'2026-10-18'},\n"
    "        v:[{n:'trees',v:3,u:'trees',say:'the trees seen from home, work or school, at least'},{n:'canopy',v:30,u:'%',say:'the tree canopy of the neighbourhood, at least'},\n"
    "          {n:'walk',v:300,u:'m',say:'the walk to the nearest public green space, at most'},{n:'green_min',v:0.5,u:'ha',say:'the smallest public green space counted'}]}]},\n"
    "    {id:'app.land',title:'Land use, form and green around the site',pub:'This app',kind:'assumption',area:'Land and green',use:'Land use, figure-ground and green layers and their findings',anywhere:true,\n"
    "      eds:[{id:'app.land.1',name:'The app\\'s land settings (V168), with the owner\\'s choices of 2026-10-18',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],\n"
    "        src:{t:'This app: the neighbourhood for the canopy (neither Konijnendijk nor Browning et al. fix one), the families the mix is counted over, the square and its cells, how far a tree seen counts, and the crosswalk from OpenStreetMap\\'s tags to LBCS\\'s activities, checked against LBCS\\'s descriptions',w:'research-site-analysis-in-model.md, section 6',lv:'A'},\n"
    "        v:[{n:'hood',v:500,u:'m',say:'the neighbourhood\\'s radius for the canopy'},{n:'mix_n',v:8,u:'families',say:'the land use families the mix is counted over'},\n"
    "          {n:'window',v:400,u:'m',say:'the square the land use and form are measured in, across',gt:'cell'},{n:'cell',v:100,u:'m',say:'its cells, across',lt:'window'},\n"
    "          {n:'see',v:100,u:'m',say:'how far from the site a tree seen is counted'},\n"
    "          {n:'xw',t:1,say:'OpenStreetMap\\'s tags as LBCS\\'s activities; grass and flowerbeds take the class of what they lie in',v:{weak:['landuse=grass','landuse=flowerbed'],tags:{\n"
    "            " + XW + "}}}]}]},\n"
    "    {id:'app.climate',title:'Climate readings'")
rep("  var BIM_STD_AREAS=['Transit and walking','Roads and noise','Cycling','Air','Flood and ground','Buildings','Structure','Site context','Climate'];",
    "  var BIM_STD_AREAS=['Transit and walking','Roads and noise','Cycling','Air','Flood and ground','Buildings','Structure','Site context','Land and green','Climate'];   /* __acad3dV168: Land and green */")
rep("'per sq mi':[' per sq mi',' per sq mi'],dB:[' dB',' dB'],",
    "'per sq mi':[' per sq mi',' per sq mi'],dB:[' dB',' dB'],ha:[' ha',' ha'],trees:[' tree',' trees'],families:[' family',' families'],")

# ---- the context: the land use the crosswalk reads ----
rep("  var BIM_CTX_LANDUSE='residential|commercial|retail|industrial|railway|construction';",
    "  var BIM_CTX_LANDUSE='residential|commercial|retail|industrial|railway|construction|'+   /* __acad3dV168: what LBCS's crosswalk reads */\n"
    "    'education|institutional|civic_admin|religious|churchyard|cemetery|military|garages|landfill|brownfield|greenfield|farmland|field|farmyard|orchard|vineyard|allotments|plant_nursery|greenhouse_horticulture|aquaculture|quarry|port|school|flowerbed';\n"
    "  /* __acad3dV168: the areas of amenities, leisure and tourism, land use too: a school's grounds, a car park, a pitch */\n"
    "  var BIM_CTX_LAND_AREAS={amenity:'school|university|college|kindergarten|hospital|clinic|place_of_worship|townhall|library|fire_station|police|courthouse|prison|grave_yard|marketplace|theatre|cinema|arts_centre|community_centre|parking|bus_station|nursing_home',\n"
    "    leisure:'playground|pitch|sports_centre|stadium|golf_course|garden|track|marina',tourism:'hotel|motel|museum|gallery|zoo|aquarium|theme_park|camp_site'};")
rep("    if(k.landuse)q.push('way[\"landuse\"~\"^('+BIM_CTX_LANDUSE+')$\"]'+b+';','relation[\"landuse\"~\"^('+BIM_CTX_LANDUSE+')$\"][\"type\"=\"multipolygon\"]'+b+';');",
    "    if(k.landuse)q.push('way[\"landuse\"~\"^('+BIM_CTX_LANDUSE+')$\"]'+b+';','relation[\"landuse\"~\"^('+BIM_CTX_LANDUSE+')$\"][\"type\"=\"multipolygon\"]'+b+';',\n"
    "      'way[\"amenity\"~\"^('+BIM_CTX_LAND_AREAS.amenity+')$\"]'+b+';','way[\"leisure\"~\"^('+BIM_CTX_LAND_AREAS.leisure+')$\"]'+b+';','way[\"tourism\"~\"^('+BIM_CTX_LAND_AREAS.tourism+')$\"]'+b+';');   /* __acad3dV168 */")
rep("    if(t.landuse&&new RegExp('^('+BIM_CTX_LANDUSE+')$').test(t.landuse))return 'landuse';   /* __acad3dV157 */",
    "    if(t.landuse&&new RegExp('^('+BIM_CTX_LANDUSE+')$').test(t.landuse))return 'landuse';   /* __acad3dV157 */\n"
    "    if(['amenity','leisure','tourism'].some(function(k2){return t[k2]&&new RegExp('^('+BIM_CTX_LAND_AREAS[k2]+')$').test(t[k2]);}))return 'landuse';   /* __acad3dV168: an amenity's, a pitch's, a hotel's grounds */")
rep("            if(f.inner.length){c.courtyards=f.inner.length;yards+=f.inner.length;}",
    "            if(f.inner.length){c.courtyards=f.inner.length;yards+=f.inner.length;c.holes=f.inner.map(function(r){return r.map(function(p){return [p[0],p[1]];});});}   /* __acad3dV168: the courtyards' outlines, for the ground covered */")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
