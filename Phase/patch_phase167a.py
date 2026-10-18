#!/usr/bin/env python3
"""V167a: the standards registry -- the records, the one reader, the place, overrides, stamps, packs.

reference/research-standards-registry.md and reference/plan-v167-v170.md, V167. Every standard,
guideline and assumption the analyses apply becomes a record: a topic with its editions, each with
where and when it is in force, its source to the section and the level it was read at, and its
values in our own words. bimStd(topic, name) is the one reader. Nothing here changes what an
analysis computes yet: patch 167b moves the analyses onto the reader.

Run from the repository root: python3 Phase/patch_phase167a.py
"""
import hashlib, pathlib, re, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'b7ee1405e5248fbb833127618991763e1d0d997790b7230525e00d3d75032b7e'   # V166b, after patch_phase166f.py

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
        sys.exit('expected %d of %r, found %d' % (count, old[:80], n))
    s = s.replace(old, new)


def js_ascii(t):
    return ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in t)


# the IBC table and the road widths are taken from the build as they are, so no row is retyped
m = re.search(r"  var BIM_OCC_LOADS=\[\n(.*?)\n  \];\n", s, re.S)
if not m:
    sys.exit('BIM_OCC_LOADS not found')
OCC_ROWS = m.group(1)
if OCC_ROWS.count("',") != 36:
    sys.exit('expected 36 occupant load rows, found %d' % OCC_ROWS.count("',"))
m = re.search(r"  var BIM_ROAD_W=(\{.*?\});\n", s, re.S)
if not m:
    sys.exit('BIM_ROAD_W not found')
ROAD_W = m.group(1).replace('\n    ', '')

LONDON = ['lnd', 'bdg', 'bne', 'bex', 'ben', 'bry', 'cmd', 'cry', 'eal', 'enf', 'gre', 'hck', 'hmf', 'hry', 'hrw', 'hav',
          'hil', 'hns', 'isl', 'kec', 'ktt', 'lbh', 'lew', 'mrt', 'nwm', 'rdb', 'ric', 'swk', 'stn', 'twh', 'wft', 'wnd', 'wsm']

BLOCK = r'''  /* ================= __acad3dV167: the standards registry =================
     reference/research-standards-registry.md. Every standard, guideline and assumption an analysis
     applies is a record here, never a number in its code: a topic, and its editions. An edition says
     where and when it is in force (adopt: a place key, from, to), its source to the section and the
     level it was read at (P at its source, S from a dependable secondary one with the gap said, U not
     yet verified, A the app's own assumption), and its values in our own words -- numbers and facts,
     never a standard's text. Place keys: '*' international, 'us', 'us-pa' (ISO 3166-2, lower case),
     a district ('gb-wsm'), a city ('us-pa:philadelphia').
     bimStd(topic, name) is the one reader: the value of the edition in force for the site's place and
     the project's date, or the project's override. A topic with no edition in force for the place is
     still applied when it is marked anywhere, and says so (how: 'outside'): the owner's choice of
     2026-10-18. Reading never writes to the project; the first change makes A3D.site.std. */
  var BIM_STD_LONDON=[__LONDON__];
  function bimStdAt(keys,from,to){return keys.map(function(k){var a={at:k};if(from)a.from=from;if(to)a.to=to;return a;});}
  var BIM_STD=[
    /* ---- transit and walking ---- */
    {id:'tfl.ptal',title:'Public Transport Accessibility Level (PTAL)',pub:'Transport for London',kind:'method',area:'Transit and walking',use:'Transit layer, its finding and the walk catchments',anywhere:true,
      eds:[{id:'tfl.ptal.2015',name:'Assessing transport connectivity in London (2015)',pub:'2015-04-23',st:'current',where:'Greater London',adopt:bimStdAt(BIM_STD_LONDON,'2015-04-23'),
        src:{t:'Transport for London, Assessing transport connectivity in London',w:'section 2.5, the calculation of PTAL, and Table 2.2',u:'https://content.tfl.gov.uk/connectivity-assessment-guide.pdf',lv:'P',read:'2026-10-18'},method:'ptal.2015',
        v:[{n:'walk_bus',v:8,u:'min',say:'the walk to a bus stop',src:'up to 640 m, about eight minutes'},
          {n:'walk_rail',v:12,u:'min',say:'the walk to a rail, Tube or DLR station',src:'up to 960 m, 12 minutes'},
          {n:'walk_tram',v:12,u:'min',say:'the walk to a tram stop',src:'not given by the guide: taken as rail\'s',lv:'A'},
          {n:'k_bus',v:2,u:'min',say:'the reliability allowance for buses',src:'two minutes'},
          {n:'k_rail',v:0.75,u:'min',say:'the reliability allowance for rail, Tube and tram',src:'0.75 minutes'},
          {n:'bands',t:1,v:[[2.5,'1a'],[5,'1b'],[10,'2'],[15,'3'],[20,'4'],[25,'5'],[40,'6a'],[null,'6b']],say:'the access index\'s bands, each up to the value',src:'Table 2.2: 0.01 to 2.50 is 1a, up to 40.01 and over 6b'}]}]},
    {id:'walk.speed',title:'Walking speed',pub:'This app',kind:'assumption',area:'Transit and walking',use:'Walk times, the transit catchments, the compass rings',anywhere:true,
      eds:[{id:'walk.speed.1',name:'The app\'s walking speed, TfL\'s figure',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app, taking Transport for London\'s figure from Assessing transport connectivity in London (2015)',w:'section 2.5: a walking speed of 4.8 km/h',u:'https://content.tfl.gov.uk/connectivity-assessment-guide.pdf',lv:'P',read:'2026-10-18'},
        v:[{n:'m_min',v:80,u:'m/min',say:'the walking speed',src:'4.8 km/h'}]}]},
    {id:'guides.walk',title:'Walking distances to daily needs',pub:'UK planning guidance',kind:'guideline',area:'Transit and walking',use:'Daily needs layer',anywhere:true,
      eds:[{id:'guides.walk.2007',name:'Manual for Streets (2007), with the North Norfolk Design Guide',pub:'2007',st:'current',where:'England and Wales',adopt:[{at:'gb-eng',from:'2007'},{at:'gb-wls',from:'2007'}],
        src:{t:'Department for Transport, Manual for Streets (2007); North Norfolk District Council, Design Guide, movement and connectivity',w:'Manual for Streets 4.4.1; the guide\'s walking distances (its page has since moved)',u:'https://assets.publishing.service.gov.uk/media/5a7e0035ed915d74e6223743/pdfmanforstreets.pdf',lv:'P',read:'2026-10-18'},
        v:[{n:'shops',v:800,u:'m',say:'the walk to shops',src:'Manual for Streets 4.4.1: facilities within about 800 m, a 10-minute walk',lv:'P'},
          {n:'school',v:800,u:'m',say:'the walk to a primary school',src:'the North Norfolk Design Guide: about 800 m',lv:'S'},
          {n:'green',v:400,u:'m',say:'the walk to local green space',src:'the North Norfolk Design Guide: about 400 m, a 5-minute walk',lv:'S'}]}]},
    {id:'leed.nd',title:'LEED for Neighborhood Development: connectivity',pub:'U.S. Green Building Council',kind:'rating',area:'Transit and walking',use:'Access board and its finding',anywhere:true,
      eds:[{id:'leed.nd.v4',name:'LEED v4 for Neighborhood Development (updated 2 July 2018)',pub:'2018-07-02',st:'current',where:'Projects seeking LEED, anywhere',adopt:[{at:'*',from:'2014'}],
        src:{t:'U.S. Green Building Council, LEED v4 for Neighborhood Development',w:'Connected and Open Community: the prerequisite\'s Cases 1 and 2, and the credit\'s Table 1',u:'https://www.gbcbrasil.org.br/wp-content/uploads/2019/08/LEED_v4_ND.pdf',lv:'P',read:'2026-10-18'},
        v:[{n:'radius',v:400,u:'m',say:'the distance from the project counted',src:'a quarter mile, 400 m'},
          {n:'case1',v:90,u:'per sq mi',say:'the prerequisite, around a project with no streets of its own',src:'Case 1: 90 intersections a square mile within 400 m'},
          {n:'case2',v:140,u:'per sq mi',say:'the prerequisite, inside a project with its own streets',src:'Case 2: 140 intersections a square mile'},
          {n:'pt1',v:300,u:'per sq mi',say:'the credit\'s first point',src:'Table 1: 300 to 400, 1 point'},
          {n:'pt2',v:400,u:'per sq mi',say:'the credit\'s second point',src:'Table 1: over 400, 2 points'}]}]},
    /* ---- roads and noise ---- */
    {id:'fhwa.fc',title:'Highway functional classification: traffic by class',pub:'Federal Highway Administration',kind:'classification',area:'Roads and noise',use:'Noise layer; the street hierarchy\'s classes',anywhere:true,
      eds:[{id:'fhwa.fc.2023',name:'Highway Functional Classification: Concepts, Criteria and Procedures, 2023 Edition',pub:'2023-02',st:'current',where:'United States',adopt:[{at:'us',from:'2023-02'}],
        src:{t:'FHWA, Highway Functional Classification: Concepts, Criteria and Procedures, 2023 Edition (February 2023)',w:'Tables 3-5 and 3-6: AADT ranges by class, from 2011 HPMS data',u:'https://www.fhwa.dot.gov/planning/processes/statewide/related/hwy-functional-classification-2023.pdf',lv:'P',read:'2026-10-18'},method:'fc.midpoint',
        v:[{n:'classes',t:1,say:'the typical daily traffic (AADT) of each class, rural and urban: the noise analysis takes the middle of each range, to the nearest 10',
          v:{interstate:{name:'Interstate or motorway',r:[12000,34000],u:[35000,129000]},freeway:{name:'Other freeway or expressway',r:[4000,18500],u:[13000,55000]},
            opa:{name:'Other principal arterial',r:[2000,8500],u:[7000,27000]},minor_art:{name:'Minor arterial',r:[1500,6000],u:[3000,14000]},
            major_col:{name:'Major collector',r:[300,2600],u:[1100,6300]},minor_col:{name:'Minor collector',r:[150,1110],u:[1100,6300]},local:{name:'Local road',r:[15,400],u:[80,700]}}}]}]},
    {id:'app.roads',title:'Roads where OpenStreetMap does not say',pub:'This app',kind:'assumption',area:'Roads and noise',use:'Noise; cycling stress\'s speeds and lanes',anywhere:true,
      eds:[{id:'app.roads.1',name:'The app\'s road classes (V164)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: OpenStreetMap\'s highway classes read as FHWA\'s, each with a speed, a share of heavy vehicles and lanes',w:'research-site-analysis-in-model.md, section 1',lv:'A'},
        v:[{n:'classes',t:1,v:{motorway:'interstate',trunk:'freeway',primary:'opa',secondary:'minor_art',tertiary:'major_col',unclassified:'minor_col',residential:'local',living_street:'local'},say:'OpenStreetMap\'s classes as FHWA\'s'},
          {n:'motorway_v',v:100,u:'km/h',say:'a motorway\'s speed'},{n:'motorway_p',v:15,u:'%',say:'a motorway\'s heavy vehicles'},{n:'motorway_l',v:4,u:'lanes',say:'a motorway\'s lanes'},
          {n:'trunk_v',v:90,u:'km/h',say:'a trunk road\'s speed'},{n:'trunk_p',v:10,u:'%',say:'a trunk road\'s heavy vehicles'},{n:'trunk_l',v:4,u:'lanes',say:'a trunk road\'s lanes'},
          {n:'primary_v',v:60,u:'km/h',say:'a primary road\'s speed'},{n:'primary_p',v:8,u:'%',say:'a primary road\'s heavy vehicles'},{n:'primary_l',v:2,u:'lanes',say:'a primary road\'s lanes'},
          {n:'secondary_v',v:50,u:'km/h',say:'a secondary road\'s speed'},{n:'secondary_p',v:5,u:'%',say:'a secondary road\'s heavy vehicles'},{n:'secondary_l',v:2,u:'lanes',say:'a secondary road\'s lanes'},
          {n:'tertiary_v',v:50,u:'km/h',say:'a tertiary road\'s speed'},{n:'tertiary_p',v:3,u:'%',say:'a tertiary road\'s heavy vehicles'},{n:'tertiary_l',v:2,u:'lanes',say:'a tertiary road\'s lanes'},
          {n:'unclassified_v',v:40,u:'km/h',say:'an unclassified road\'s speed'},{n:'unclassified_p',v:2,u:'%',say:'an unclassified road\'s heavy vehicles'},{n:'unclassified_l',v:2,u:'lanes',say:'an unclassified road\'s lanes'},
          {n:'residential_v',v:40,u:'km/h',say:'a residential street\'s speed'},{n:'residential_p',v:2,u:'%',say:'a residential street\'s heavy vehicles'},{n:'residential_l',v:2,u:'lanes',say:'a residential street\'s lanes'},
          {n:'living_street_v',v:20,u:'km/h',say:'a living street\'s speed'},{n:'living_street_p',v:1,u:'%',say:'a living street\'s heavy vehicles'},{n:'living_street_l',v:1,u:'lanes',say:'a living street\'s lanes'},
          {n:'service_v',v:20,u:'km/h',say:'a service road\'s speed'},{n:'track_v',v:30,u:'km/h',say:'a track\'s speed'},{n:'other_v',v:40,u:'km/h',say:'any other street\'s speed'}]}]},
    {id:'crtn',title:'Calculation of Road Traffic Noise (CRTN)',pub:'Department of Transport and Welsh Office',kind:'method',area:'Roads and noise',use:'Noise layer',anywhere:true,
      eds:[{id:'crtn.1988',name:'Calculation of Road Traffic Noise (1988)',pub:'1988',st:'current',where:'United Kingdom',adopt:[{at:'gb',from:'1988'}],
        src:{t:'Department of Transport and Welsh Office, Calculation of Road Traffic Noise, HMSO, 1988',w:'its range, as DataKustik\'s CadnaA documentation gives it: the memorandum\'s own text could not be read from here',u:'https://doku.datakustik.com/CadnaA/en/Str_CRTN.html',lv:'S',read:'2026-10-17'},method:'crtn.1988',
        v:[{n:'range',v:300,u:'m',say:'how far from a road the method holds'}]}]},
    /* ---- cycling ---- */
    {id:'lts.2012',title:'Level of traffic stress (cycling)',pub:'Mekuria, Furth and Nixon',kind:'method',area:'Cycling',use:'Cycling layer and its finding',anywhere:true,
      eds:[{id:'lts.2012',name:'Low-Stress Bicycling and Network Connectivity, MTI report 11-19 (2012)',pub:'2012',st:'current',where:'A research method, used anywhere',adopt:[{at:'*',from:'2012'}],
        src:{t:'Mekuria, Furth and Nixon, Low-Stress Bicycling and Network Connectivity, Mineta Transportation Institute report 11-19',w:'the criteria tables, as Princeton\'s reproduction gives them; the report could not be read from here',lv:'S',read:'2026-10-17'},method:'lts.2012',v:[]}]},
    {id:'lts.xing2016',title:'Crossing an unsignalized street (cycling stress)',pub:'Furth, Mekuria and Nixon',kind:'method',area:'Cycling',use:'Cycling layer',anywhere:true,
      eds:[{id:'lts.xing2016',name:'Network connectivity for low-stress bicycling (2016)',pub:'2016',st:'current',where:'A research method, used anywhere',adopt:[{at:'*',from:'2016'}],
        src:{t:'Furth, Mekuria and Nixon, Network connectivity for low-stress bicycling, Transportation Research Record 2587 (2016)',w:'the table for a crossing without a median refuge, as Princeton\'s reproduction gives it',lv:'S',read:'2026-10-17'},
        v:[{n:'table',t:1,v:[[1,2,4],[1,2,4],[2,3,4],[3,4,4]],say:'the level by the crossed street\'s speed (up to 25 mph, 30, 35, 40 and over) and lanes (up to 3, 4 to 5, 6 or more)'}]}]},
    /* ---- air ---- */
    {id:'who.aqg',title:'WHO air quality guidelines: fine particulate matter (PM2.5)',pub:'World Health Organization',kind:'guideline',area:'Air',use:'Air quality finding and board',anywhere:true,
      eds:[{id:'who.aqg.2021',name:'WHO global air quality guidelines (2021)',pub:'2021',st:'current',where:'International',adopt:[{at:'*',from:'2021'}],
        src:{t:'WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide',w:'Table 0.1, the recommended AQG levels and interim targets',u:'https://iris.who.int/handle/10665/345329',lv:'P',read:'2026-10-18'},
        v:[{n:'pm25_year',v:5,u:'ug/m3',say:'the annual guideline level'},
          {n:'pm25_24h',v:15,u:'ug/m3',say:'the 24-hour guideline level',src:'the 99th percentile: three to four days a year over it'},
          {n:'pm25_it1_year',v:35,u:'ug/m3',say:'the first interim target, annual'}]}]},
    /* ---- flood and ground ---- */
    {id:'fema.zones',title:'Flood zones',pub:'Federal Emergency Management Agency',kind:'classification',area:'Flood and ground',use:'Flood zones layer and its finding',anywhere:true,
      eds:[{id:'fema.zones.cfr',name:'44 CFR 64.3, the flood insurance rate map\'s zone symbols',pub:'1976-10-26',st:'current',where:'United States',adopt:[{at:'us',from:'1976-10-26'}],
        src:{t:'Code of Federal Regulations, title 44, section 64.3 (eCFR, current to 2026-10-01)',w:'(a)(1), the zone symbols',u:'https://www.ecfr.gov/current/title-44/section-64.3',lv:'P',read:'2026-10-18'},method:'fema.nfhl.1',
        v:[{n:'groups',t:1,say:'how the layer groups FEMA\'s zones',v:{floodway:'the regulatory floodway, from the NFHL\'s zone subtype',coastal:'V, VE, V1-30 and VO: special flood hazard with velocity',
          sfha:'A, AE, A1-30, AH, AO, A99 and AR: special flood hazard',x02:'B, or X with the 0.2% subtype: moderate flood hazard',undetermined:'D: possible but undetermined flood hazard'}}]}]},
    {id:'land.slope',title:'Slope classes for development',pub:'This app',kind:'assumption',area:'Flood and ground',use:'Slope layer and its finding',anywhere:true,
      eds:[{id:'land.slope.1',name:'The app\'s working set (V165)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: a working set from planning practice, 15% and 25% the decision points; the bands vary by place',w:'research-site-analysis-in-model.md, section 2',lv:'A'},
        v:[{n:'b1',v:5,u:'%',say:'flat to gentle, up to'},{n:'b2',v:10,u:'%',say:'moderate, up to'},{n:'b3',v:15,u:'%',say:'moderately steep, up to'},{n:'b4',v:25,u:'%',say:'steep, up to'}]}]},
    {id:'terrain.slope_bands',title:'Slope bands on terrain',pub:'This app',kind:'assumption',area:'Flood and ground',use:'Terrain coloured by slope (V144)',anywhere:true,
      eds:[{id:'terrain.slope_bands.1',name:'The app\'s bands (V144), three at the 2010 ADA Standards\' limits',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app; 5% and 8.33% are the 2010 ADA Standards\' 1:20 walking slope and 1:12 ramp slope, 2% their 1:48 cross slope rounded',w:'ADA Standards 403.3 and 405.2',u:'https://www.ada.gov/law-and-regs/design-standards/2010-stds/',lv:'P',read:'2026-10-18'},
        v:[{n:'bands',t:1,v:[0,2,5,8.33,15,25,50],u:'%',say:'the band edges'}]}]},
    /* ---- buildings and structure ---- */
    {id:'ibc.occupant_load',title:'Occupant load factors',pub:'International Code Council',kind:'code',area:'Buildings',use:'Rooms\' occupant loads and the area plans',anywhere:true,
      eds:[{id:'ibc.2021.1004.5',name:'International Building Code 2021, Table 1004.5',pub:'2020-10',st:'current',where:'Pennsylvania (the Uniform Construction Code)',adopt:[{at:'us-pa',from:'2026-01-01'}],
          src:{t:'International Building Code 2021, Table 1004.5, maximum floor area allowances per occupant; adopted in Pennsylvania by 34 Pa. Code 403.21',w:'the table as V105 read it (the same in 2018 and 2021); the adoption in 34 Pa. Code 403.21, effective 1 January 2026',u:'https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/034/chapter403/s403.21.html',lv:'S',read:'2026-10-18'},
          v:[{n:'table',t:1,u:'sq ft',say:'square feet per occupant, gross or net, by use',v:__OCC__}]},
        {id:'ibc.2018.1004.5',name:'International Building Code 2018, Table 1004.5',pub:'2017-08',st:'superseded',where:'As adopted',adopt:[],
          src:{t:'International Building Code 2018, Table 1004.5',w:'the table as V105 read it (the same as 2021\'s)',lv:'S',read:'2026-10-10'},
          v:[{n:'table',t:1,u:'sq ft',say:'square feet per occupant, gross or net, by use',v:__OCC__}]}]},
    {id:'asce7.combos',title:'Load combinations, strength design',pub:'American Society of Civil Engineers',kind:'code',area:'Structure',use:'Frame analysis',anywhere:true,
      eds:[{id:'asce7.22',name:'ASCE/SEI 7-22, section 2.3.1, combinations 1 and 2',pub:'2021-12',st:'current',where:'Adoption by place not recorded',adopt:[],
        src:{t:'ASCE/SEI 7-22, Minimum Design Loads and Associated Criteria for Buildings and Other Structures',w:'2.3.1, combinations 1 and 2, as V125 recorded them; the sold text is not read here, ASCE\'s page names 7-22 the current edition',u:'https://www.asce.org/publications-and-news/asce-7',lv:'S',read:'2026-10-18'},
        v:[{n:'c1_d',v:1.4,u:'x',say:'combination 1, dead load'},{n:'c2_d',v:1.2,u:'x',say:'combination 2, dead load'},{n:'c2_l',v:1.6,u:'x',say:'combination 2, live load'}]}]},
    /* ---- the app's assumptions, where data is missing ---- */
    {id:'app.context',title:'Site context where OpenStreetMap does not say',pub:'This app',kind:'assumption',area:'Site context',use:'Context buildings, trees, power, bridges and roads; applied at the next fetch',anywhere:true,
      eds:[{id:'app.context.1',name:'The app\'s context sizes (V133, V157)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: the sizes it gives what OpenStreetMap maps without them',w:'research-site-context.md',lv:'A'},
        v:[{n:'storey',v:3,u:'m',say:'a storey\'s height'},{n:'building',v:6,u:'m',say:'a building\'s height where neither its height nor its levels are mapped'},
          {n:'tree',v:8,u:'m',say:'a tree\'s height where none is mapped'},{n:'tower',v:25,u:'m',say:'a power tower\'s height'},{n:'line',v:20,u:'m',say:'the height a power line hangs at'},
          {n:'deck',v:6,u:'m',say:'a bridge deck\'s height for each layer'},{n:'deck_t',v:0.8,u:'m',say:'a bridge deck\'s thickness'},{n:'pier',v:30,u:'m',say:'the spacing of a bridge\'s piers'},
          {n:'road_w',t:1,u:'m',say:'a road\'s width by class, where neither its width nor its lanes are mapped',v:__ROADW__}]}]},
    {id:'app.climate',title:'Climate readings',pub:'This app',kind:'assumption',area:'Climate',use:'The climate board, the wind rose and its finding',anywhere:true,
      eds:[{id:'app.climate.1',name:'The app\'s climate settings (V159)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: a degree-day base, a calm threshold and the rose\'s speed bins, and a comfort band',w:'research-climate-risk-presentation.md',lv:'A'},
        v:[{n:'base',v:18,u:'C',say:'the degree-day base temperature'},{n:'calm',v:0.5,u:'m/s',say:'calm: the wind below this speed'},
          {n:'wind_bins',t:1,u:'m/s',v:[2,4,6,8],say:'the wind rose\'s speed bins above calm'},
          {n:'comfort_t0',v:20,u:'C',say:'the comfort band\'s lowest temperature'},{n:'comfort_t1',v:27,u:'C',say:'the comfort band\'s highest temperature'},
          {n:'comfort_rh0',v:20,u:'%',say:'the comfort band\'s lowest humidity'},{n:'comfort_rh1',v:80,u:'%',say:'the comfort band\'s highest humidity'}]}]},
    /* ---- the catalogue for a US and Pennsylvania site: in force there, not applied by the app yet ---- */
    {id:'pa.ucc',title:'Pennsylvania Uniform Construction Code',pub:'Pennsylvania Department of Labor and Industry',kind:'code',area:'Buildings',cat:true,access:'free to read',
      eds:[{id:'pa.ucc.2026',name:'The 2021 I-Codes (IBC, IRC, IECC, IMC, IFGC, IEBC; the IFC as they reference it), with Pennsylvania\'s changes',pub:'2025-11-07',st:'current',where:'Pennsylvania',adopt:[{at:'us-pa',from:'2026-01-01'}],
        src:{t:'34 Pa. Code 403.21, as amended 7 November 2025 (55 Pa.B. 7701), effective 1 January 2026',w:'403.21(a)',u:'https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/034/chapter403/s403.21.html',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'ibc',title:'International Building Code',pub:'International Code Council',kind:'code',area:'Buildings',cat:true,access:'free to read, not to copy',
      eds:[{id:'ibc.2021',name:'International Building Code 2021',pub:'2020-10',st:'current',where:'Pennsylvania',adopt:[{at:'us-pa',from:'2026-01-01'}],
          src:{t:'34 Pa. Code 403.21(a)(1)',w:'its adoption in Pennsylvania',u:'https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/034/chapter403/s403.21.html',lv:'P',read:'2026-10-18'},v:[]},
        {id:'ibc.2024',name:'International Building Code 2024, ICC\'s current model code',pub:'2023',st:'current',where:'As adopted',adopt:[],
          src:{t:'International Code Council, on A117.1-2026 being for the 2027 I-Codes',w:'the 2024 edition being the current one is inferred from that; codes.iccsafe.org refuses scripts here',u:'https://www.iccsafe.org/building-safety-journal/bsj-dives/a117-1-2026-the-international-code-council-to-release-major-updates-to-the-nations-leading-accessibility-standard/',lv:'S',read:'2026-10-18'},v:[]}]},
    {id:'ada.2010',title:'2010 ADA Standards for Accessible Design',pub:'U.S. Department of Justice',kind:'code',area:'Accessibility',cat:true,access:'free',
      eds:[{id:'ada.2010',name:'2010 ADA Standards for Accessible Design',pub:'2010-09-15',st:'current',where:'United States',adopt:[{at:'us',from:'2012-03-15'}],
        src:{t:'U.S. Department of Justice, 2010 ADA Standards for Accessible Design',w:'403.3 (walking surfaces 1:20, cross slope 1:48), 405.2 (ramps 1:12), and the rest',u:'https://www.ada.gov/law-and-regs/design-standards/2010-stds/',lv:'P',read:'2026-10-18'},
        v:[{n:'walk_slope',v:5,u:'%',say:'the steepest running slope of a walking surface (1:20)'},{n:'cross_slope',v:2.08,u:'%',say:'the steepest cross slope (1:48)'},{n:'ramp_slope',v:8.33,u:'%',say:'the steepest ramp run (1:12)'}]}]},
    {id:'a117.1',title:'ICC A117.1, Accessible and Usable Buildings and Facilities',pub:'International Code Council',kind:'standard',area:'Accessibility',cat:true,access:'sold',
      eds:[{id:'a117.1.2026',name:'ICC A117.1-2026, for the 2027 I-Codes (announced for fall 2026)',pub:'2026',st:'announced',where:'As adopted',adopt:[],
        src:{t:'International Code Council, Building Safety Journal, on A117.1-2026',w:'its release in fall 2026 and its reference by the 2027 I-Codes',u:'https://www.iccsafe.org/building-safety-journal/bsj-dives/a117-1-2026-the-international-code-council-to-release-major-updates-to-the-nations-leading-accessibility-standard/',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'ashrae.90.1',title:'ASHRAE/IES Standard 90.1, energy standard for buildings except low-rise residential',pub:'ASHRAE',kind:'standard',area:'Energy',cat:true,access:'sold; a read-only copy online',
      eds:[{id:'ashrae.90.1.2025',name:'Standard 90.1-2025',pub:'2025',st:'current',where:'As adopted',adopt:[],
        src:{t:'ASHRAE, read-only versions of its standards',w:'the list names 90.1-2025',u:'https://www.ashrae.org/technical-resources/standards-and-guidelines/read-only-versions-of-ashrae-standards',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'mutcd',title:'Manual on Uniform Traffic Control Devices (MUTCD)',pub:'Federal Highway Administration',kind:'standard',area:'Highways',cat:true,access:'free',
      eds:[{id:'mutcd.11r1',name:'MUTCD 11th Edition (December 2023), with Revision 1 (December 2025)',pub:'2025-12',st:'current',where:'United States',adopt:[{at:'us',from:'2025-12'}],
        src:{t:'FHWA, MUTCD 11th Edition',w:'the 11th Edition with Revision 1, dated December 2025, is the current version',u:'https://mutcd.fhwa.dot.gov/kno_11th_Edition.htm',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'aashto.greenbook',title:'A Policy on Geometric Design of Highways and Streets (the Green Book)',pub:'AASHTO',kind:'standard',area:'Highways',cat:true,access:'sold',
      eds:[{id:'aashto.greenbook.7',name:'A Policy on Geometric Design of Highways and Streets, 7th Edition',pub:'2018',st:'current',where:'As adopted',adopt:[],
        src:{t:'AASHTO Store, its publications list',w:'names the 7th Edition',u:'https://store.transportation.org/',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'penndot.dm2',title:'Design Manual Part 2, Highway Design (Publication 13M)',pub:'Pennsylvania Department of Transportation',kind:'manual',area:'Highways',cat:true,access:'free',
      eds:[{id:'penndot.dm2.c11',name:'Publication 13M, Change No. 11 (March 2024), being replaced by Publication 13, Contextual Roadway Design',pub:'2024-03',st:'current',where:'Pennsylvania',adopt:[{at:'us-pa',from:'2024-03'}],
        src:{t:'PennDOT, Publication 13M title page',w:'Change No. 11, March 2024, marked current; seen in a search summary, as PennDOT\'s host did not answer from here',u:'https://www.dot.state.pa.us/public/pubsforms/Publications/PUB%2013M/Pub%2013M%20Title%20Page.pdf',lv:'S',read:'2026-10-18'},v:[]}]},
    {id:'aashto.lrfd',title:'AASHTO LRFD Bridge Design Specifications',pub:'AASHTO',kind:'standard',area:'Bridges',cat:true,access:'sold',
      eds:[{id:'aashto.lrfd.10',name:'AASHTO LRFD Bridge Design Specifications, 10th Edition',pub:'2024',st:'current',where:'As adopted',adopt:[],
          src:{t:'AASHTO Store, its featured publications',w:'names the 10th Edition',u:'https://store.transportation.org/',lv:'P',read:'2026-10-18'},v:[]},
        {id:'aashto.lrfd.8',name:'AASHTO LRFD Bridge Design Specifications, 8th Edition (2017), as DM-4 adopts it',pub:'2017',st:'superseded',where:'Pennsylvania, through DM-4',adopt:[{at:'us-pa',from:'2020-07-01'}],
          src:{t:'PennDOT, Design Manual Part 4, December 2019 Edition',w:'adopts and modifies the 8th Edition (2017), for projects with TS&L approval after 30 June 2020',u:'https://docs.penndot.pa.gov/Public/Bureaus/Bridge/DM-4/DM-4_Archive.pdf',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'penndot.dm4',title:'Design Manual Part 4, Structures (DM-4, Publication 15M)',pub:'Pennsylvania Department of Transportation',kind:'manual',area:'Bridges',cat:true,access:'free',
      eds:[{id:'penndot.dm4.2019',name:'DM-4, December 2019 Edition, with its strike-off letters to 483-25-01',pub:'2019-12-30',st:'current',where:'Pennsylvania',adopt:[{at:'us-pa',from:'2020-07-01'}],
        src:{t:'PennDOT Bureau of Bridge, DM-4 archive',w:'the December 2019 Edition, effective for projects with TS&L approval after 30 June 2020; its annotated version updated 8 August 2025',u:'https://docs.penndot.pa.gov/Public/Bureaus/Bridge/DM-4/DM-4_Archive.pdf',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'asce7',title:'ASCE/SEI 7, Minimum Design Loads and Associated Criteria for Buildings and Other Structures',pub:'American Society of Civil Engineers',kind:'standard',area:'Structure',cat:true,access:'sold',
      eds:[{id:'asce7.22.cat',name:'ASCE/SEI 7-22, with Supplements 1 to 3',pub:'2021-12',st:'current',where:'As adopted',adopt:[],
        src:{t:'ASCE, its ASCE 7 page',w:'names ASCE/SEI 7-22 and its three supplements',u:'https://www.asce.org/publications-and-news/asce-7',lv:'P',read:'2026-10-18'},v:[]}]},
    {id:'aci318',title:'ACI 318, Building Code Requirements for Structural Concrete',pub:'American Concrete Institute',kind:'standard',area:'Structure',cat:true,access:'sold',
      eds:[{id:'aci318.unread',name:'Its current edition was not read: concrete.org did not answer from here',pub:'',st:'current',where:'As adopted',adopt:[],
        src:{t:'American Concrete Institute',w:'not read',u:'https://www.concrete.org/',lv:'U',read:'2026-10-18'},v:[]}]},
    {id:'aisc360',title:'AISC 360, Specification for Structural Steel Buildings',pub:'American Institute of Steel Construction',kind:'standard',area:'Structure',cat:true,access:'free to download',
      eds:[{id:'aisc360.unread',name:'Its current edition was not read: aisc.org refuses scripts here',pub:'',st:'current',where:'As adopted',adopt:[],
        src:{t:'American Institute of Steel Construction',w:'not read',u:'https://www.aisc.org/publications/steel-standards/',lv:'U',read:'2026-10-18'},v:[]}]},
    {id:'faa.ac150_5300_13',title:'FAA Advisory Circular 150/5300-13, Airport Design',pub:'Federal Aviation Administration',kind:'standard',area:'Aviation',cat:true,access:'free',
      eds:[{id:'faa.ac150_5300_13b.c1',name:'AC 150/5300-13B, Airport Design, Change 1 (16 August 2024)',pub:'2024-08-16',st:'current',where:'United States',adopt:[{at:'us',from:'2024-08-16'}],
        src:{t:'FAA, the advisory circular\'s document page',w:'number 150/5300-13B, Change 1, status active, issued 2024-08-16',u:'https://www.faa.gov/airports/resources/advisory_circulars/index.cfm/go/document.current/documentNumber/150_5300-13',lv:'P',read:'2026-10-18'},v:[]}]}];
  var BIM_STD_LV={P:'read at its source',S:'from a dependable secondary source, the gap said',U:'not yet verified',A:'the app\'s own assumption'};
  var BIM_STD_HOW={adopted:'in force here',international:'international',chosen:'chosen for this project',outside:'applied outside its place',assumption:'the app\'s assumption',none:'none in force'};
  var BIM_STD_UNIT={min:[' minute',' minutes'],m:[' m',' m'],'m/min':[' m a minute',' m a minute'],'km/h':[' km/h',' km/h'],'%':['%','%'],'ug/m3':[' \u00b5g/m\u00b3',' \u00b5g/m\u00b3'],
    'per sq mi':[' per sq mi',' per sq mi'],C:['\u00b0C','\u00b0C'],'m/s':[' m/s',' m/s'],lanes:[' lane',' lanes'],x:['\u00d7','\u00d7'],'sq ft':[' sq ft',' sq ft']};
  var BIM_STD_EMPTY={place:null,date:'',ov:{},pick:{},packs:[]};
  var A3D_STD={obj:null,rev:-1,sig:'',at:0,cache:{},recs:null,by:{},memo:{},warned:{},gen:0};
  /* what the project holds: A3D.site.std, or nothing changed yet */
  function bimStdS(){var s=A3D.site&&A3D.site.std;return (s&&typeof s==='object')?s:BIM_STD_EMPTY;}
  function bimStdW(){
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    var s=A3D.site.std;
    if(!s||typeof s!=='object')s=A3D.site.std={};
    if(!s.ov||typeof s.ov!=='object')s.ov={};
    if(!s.pick||typeof s.pick!=='object')s.pick={};
    if(!Array.isArray(s.packs))s.packs=[];
    if(typeof s.date!=='string')s.date='';
    return s;
  }
  function bimStdTouch(){var s=bimStdW();s.rev=(s.rev||0)+1;A3D_STD.at=0;}
  function bimStdDate(){var d=bimStdS().date;return /^\d{4}-\d{2}-\d{2}$/.test(String(d||''))?d:bimSaToday();}
  /* the resolutions are kept until the project's standards, its place or the date change */
  function bimStdCacheOk(){
    var s=bimStdS(),now=Date.now(),g;
    if(A3D_STD.obj===s&&A3D_STD.rev===(s.rev||0)&&now-A3D_STD.at<60000)return;
    g=(s.rev||0)+'|'+bimStdDate();
    A3D_STD.at=now;
    if(A3D_STD.obj!==s||A3D_STD.sig!==g){A3D_STD.obj=s;A3D_STD.sig=g;A3D_STD.cache={};A3D_STD.recs=null;A3D_STD.memo={};A3D_STD.gen++;}
    A3D_STD.rev=s.rev||0;
  }
  function bimStdMemo(k,fn){bimStdCacheOk();var M=A3D_STD.memo;if(!M.hasOwnProperty(k))M[k]=fn();return M[k];}
  function bimStdCopy(o){var c={},k;for(k in o)if(o.hasOwnProperty(k))c[k]=o[k];return c;}
  /* the records, with the editions and topics of the project's packs */
  function bimStdRecs(){
    bimStdCacheOk();
    if(A3D_STD.recs)return A3D_STD.recs;
    var by={},out=[];
    BIM_STD.forEach(function(r){var c=bimStdCopy(r);c.eds=r.eds.slice();by[r.id]=c;out.push(c);});
    (bimStdS().packs||[]).forEach(function(p){(p&&Array.isArray(p.topics)?p.topics:[]).forEach(function(t){
      var c=by[t.id];
      if(!c){c={id:t.id,title:t.title,pub:t.pub,kind:t.kind||'standard',area:t.area||'From standards packs',cat:true,access:t.access||'',eds:[],fromPack:p.sha};by[t.id]=c;out.push(c);}
      (t.eds||[]).forEach(function(e){var x=bimStdCopy(e);x.pack=p.sha;x.packName=p.name;c.eds.push(x);});
    });});
    A3D_STD.recs=out;A3D_STD.by=by;
    return out;
  }
  function bimStdRec(t){bimStdRecs();return A3D_STD.by.hasOwnProperty(t)?A3D_STD.by[t]:null;}
  /* ---- the site's place: from the address search, or set by hand ---- */
  function bimStdPlace(){var p=bimStdS().place;return p&&typeof p==='object'&&p.cc?p:null;}
  function bimStdPlaceName(p){
    p=p||bimStdPlace();
    if(!p)return 'no place set';
    var a=[];
    if(p.city)a.push(p.city);
    if(p.d8n&&p.d8n!==p.city)a.push(p.d8n);
    if(p.rn)a.push(p.rn);
    a.push(p.ccn||String(p.cc).toUpperCase());
    return a.join(', ');
  }
  /* most specific first: the city, its districts, the region, the country, then international */
  function bimStdPath(){
    var p=bimStdPlace(),P=[];
    if(p){
      if(p.city)P.push({k:(p.r||p.cc)+':'+String(p.city).toLowerCase(),lv:'city',name:p.city});
      if(p.d8)P.push({k:p.d8,lv:'district',name:p.d8n||p.d8.toUpperCase()});
      if(p.d6)P.push({k:p.d6,lv:'district',name:p.d6n||p.d6.toUpperCase()});
      if(p.r)P.push({k:p.r,lv:'region',name:p.rn||p.r.toUpperCase()});
      P.push({k:p.cc,lv:'country',name:p.ccn||p.cc.toUpperCase()});
    }
    P.push({k:'*',lv:'international',name:'International'});
    return P;
  }
  function bimStdCode(v,re){v=String(v==null?'':v).replace(/^\s+|\s+$/g,'').toLowerCase();return re.test(v)?v:'';}
  function bimStdTxt(v,n){return String(v==null?'':v).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,n||80);}
  /* p: {cc, r, d6, d8, city, ccn, rn, d6n, d8n}; null clears the place. One undo step. */
  function bimStdSetPlace(p,src,quiet){
    var q=null;
    if(p){
      var cc=bimStdCode(p.cc,/^[a-z]{2}$/);
      if(!cc){a3dToast('A country is two letters, as ISO 3166 gives them: US, GB, DE');return false;}
      q={cc:cc,src:src==='search'?'search':'hand',at:bimSaToday()};
      var r=bimStdCode(p.r,/^[a-z]{2}-[a-z0-9]{1,3}$/),d6=bimStdCode(p.d6,/^[a-z]{2}-[a-z0-9]{1,3}$/),d8=bimStdCode(p.d8,/^[a-z]{2}-[a-z0-9]{1,3}$/);
      if(p.r&&!r){a3dToast('A region is its ISO 3166-2 code: US-PA, GB-ENG, DE-BY');return false;}
      if(r&&r.slice(0,2)!==cc){a3dToast('The region '+r.toUpperCase()+' is not in '+cc.toUpperCase());return false;}
      if(r)q.r=r;if(d6)q.d6=d6;if(d8)q.d8=d8;
      ['city','ccn','rn','d6n','d8n'].forEach(function(k){var t=bimStdTxt(p[k]);if(t)q[k]=t;});
      var st=A3D.site&&A3D.site.sun;
      if(src==='search'&&st&&isFinite(st.lat)&&isFinite(st.lon)){q.lat=st.lat;q.lon=st.lon;}
    }
    if(!quiet)pushUndo();
    var S=bimStdW();S.place=q;bimStdTouch();
    if(!quiet){bimStdDone();a3dToast(q?'The site is in '+bimStdPlaceName(q)+': the standards in force there apply':'The site\'s place is cleared: no place\'s editions apply, and every standard says so');}
    return true;
  }
  /* Nominatim's addressdetails: country_code, ISO3166-2-lvl4 (a state, a region), lvl6 and lvl8
     (districts: a county, a London borough), the city or town */
  function bimStdPlaceFromAddress(a){
    if(!a||typeof a!=='object'||!a.country_code)return false;
    return bimStdSetPlace({cc:a.country_code,r:a['ISO3166-2-lvl4'],d6:a['ISO3166-2-lvl6'],d8:a['ISO3166-2-lvl8'],
      city:a.city||a.town||a.village||a.municipality||'',ccn:a.country,rn:a.state,d6n:a.county||a.state_district,d8n:a.city_district||a.borough||a.city},'search',true);
  }
  /* the site moved far from where its place was found */
  function bimStdPlaceMoved(){
    var p=bimStdPlace(),st=A3D.site&&A3D.site.sun;
    if(!p||p.src!=='search'||!isFinite(p.lat)||!st||!isFinite(st.lat))return false;
    return Math.abs(st.lat-p.lat)>0.05||Math.abs(st.lon-p.lon)>0.05;
  }
  function bimStdSetDate(d){
    d=String(d==null?'':d).replace(/\s+/g,'');
    if(d&&!/^\d{4}-\d{2}-\d{2}$/.test(d)){a3dToast('A date is YYYY-MM-DD; blank is today');return false;}
    pushUndo();bimStdW().date=d;bimStdTouch();bimStdDone();
    a3dToast(d?'Standards in force on '+d:'Standards in force today');
    return true;
  }
  /* ---- the edition in force ---- */
  function bimStdInForce(a,d){return (!a.from||String(a.from)<=d)&&(!a.to||d<String(a.to));}
  function bimStdResolve(t){
    bimStdCacheOk();
    var C=A3D_STD.cache;
    if(C.hasOwnProperty(t))return C[t];
    var rec=bimStdRec(t);
    if(!rec)return null;
    var S=bimStdS(),d=bimStdDate(),path=bimStdPath(),eds=rec.eds||[],r=null,i,j,best;
    if(S.pick&&S.pick[t])for(i=0;i<eds.length;i++)if(eds[i].id===S.pick[t]){r={ed:eds[i],how:'chosen',at:null};break;}
    for(i=0;!r&&i<path.length;i++){
      best=null;
      for(j=0;j<eds.length;j++)(eds[j].adopt||[]).forEach(function(a){
        if(a&&a.at===path[i].k&&bimStdInForce(a,d)&&(!best||String(a.from||'')>String(best.a.from||'')))best={e:eds[j],a:a};
      });
      if(best)r={ed:best.e,how:rec.kind==='assumption'?'assumption':(path[i].k==='*'?'international':'adopted'),at:path[i],a:best.a};
    }
    if(!r&&rec.anywhere&&eds.length){
      best=null;
      for(j=0;j<eds.length;j++)if(!eds[j].pub||String(eds[j].pub)<=d){if(!best||String(eds[j].pub||'')>String(best.pub||''))best=eds[j];}
      if(!best){best=eds[0];for(j=1;j<eds.length;j++)if(String(eds[j].pub||'')<String(best.pub||''))best=eds[j];}
      r={ed:best,how:'outside',at:null,why:bimStdPlace()?'no edition is recorded in force for '+bimStdPlaceName()+' on '+d:'the site\'s place is not set'};
    }
    if(!r)r={ed:null,how:'none',at:null,why:bimStdPlace()?'none is recorded in force for '+bimStdPlaceName()+' on '+d:'the site\'s place is not set'};
    C[t]=r;
    return r;
  }
  function bimStdVal(ed,n){var V=(ed&&ed.v)||[],i;for(i=0;i<V.length;i++)if(V[i].n===n)return V[i];return null;}
  function bimStdOvKey(t,n){return t+'|'+n;}
  function bimStdOvOf(t,n){var O=bimStdS().ov,o=O&&O[bimStdOvKey(t,n)];return o&&typeof o.v==='number'&&isFinite(o.v)?o:null;}
  /* THE reader: the project's override, or the value of the edition in force */
  function bimStd(t,n){
    var o=bimStdOvOf(t,n),r,x;
    if(o)return o.v;
    r=bimStdResolve(t);x=r&&r.ed?bimStdVal(r.ed,n):null;
    if(!x){
      var w=t+'|'+n;
      if(!A3D_STD.warned[w]){A3D_STD.warned[w]=1;console.warn('[BIM] The standards registry has no '+n+' in '+t+(r&&r.ed?' ('+r.ed.id+')':''));}
      return undefined;
    }
    return x.v;
  }
  function bimStdFmt(v,u){
    var U=BIM_STD_UNIT[u]||[' '+(u||''),' '+(u||'')],n=typeof v==='number'?bimDispNum(v,Math.abs(v-Math.round(v))<1e-9?0:(Math.abs(v*10-Math.round(v*10))<1e-9?1:2)):String(v);
    return n+(v===1?U[0]:U[1]);
  }
  /* the value in words, with its unit: every sentence that states a standard's number builds it here */
  function bimStdSay(t,n){var r=bimStdResolve(t),x=r&&r.ed?bimStdVal(r.ed,n):null,v=bimStd(t,n);return v===undefined?'':bimStdFmt(v,x?x.u:'');}
  function bimStdEdition(t){
    var rec=bimStdRec(t),r=bimStdResolve(t);
    if(!rec||!r)return null;
    var e=r.ed,O=bimStdS().ov||{},ov=[],k;
    for(k in O)if(O.hasOwnProperty(k)&&k.indexOf(t+'|')===0&&O[k]&&typeof O[k].v==='number')ov.push(k.slice(t.length+1));
    return {topic:t,title:rec.title,pub:rec.pub,kind:rec.kind,id:e?e.id:null,name:e?e.name:null,how:r.how,at:r.at?r.at.name:null,atKey:r.at?r.at.k:null,why:r.why||'',
      lv:e&&e.src?e.src.lv:null,src:e?e.src:null,where:e?e.where:'',pack:e?e.pack||null:null,ov:ov};
  }
  /* the edition in force, in words: what a result that used it says */
  function bimStdUsedText(t){
    var E=bimStdEdition(t);
    if(!E||!E.id)return E?E.title+': none in force ('+E.why+')':'';
    var s=E.title+': '+E.name;
    if(E.how==='outside')s+=', applied outside its place ('+(E.where||'its own place')+'; '+E.why+')';
    else if(E.how==='chosen')s+=', chosen for this project';
    if(E.ov.length)s+='; overridden: '+E.ov.map(function(n){var o=bimStdOvOf(t,n),x=bimStdVal(bimStdResolve(t).ed,n);return (x&&x.say?x.say:n)+' '+bimStdFmt(o.v,x?x.u:'')+' ('+o.why+')';}).join('; ');
    return s;
  }
  /* ---- provenance: what a result keeps of the standards it used ---- */
  function bimStdStamp(ts){
    var L=[],O=bimStdS().ov||{};
    (ts||[]).forEach(function(t){
      var r=bimStdResolve(t),e=r&&r.ed,ov={},k;
      for(k in O)if(O.hasOwnProperty(k)&&k.indexOf(t+'|')===0&&O[k]&&typeof O[k].v==='number')ov[k.slice(t.length+1)]=O[k].v;
      L.push({t:t,e:e?e.id:null,how:r?r.how:'none',ov:ov,h:bimHash(bimCanon({e:e?e.id:null,v:e?e.v:null,ov:ov}))});
    });
    return {at:bimSaToday(),list:L};
  }
  /* the topics whose edition, values or overrides are not what the result used */
  function bimStdChanged(st){
    if(!st||!Array.isArray(st.list))return [];
    var now=bimStdStamp(st.list.map(function(x){return x.t;})),out=[];
    st.list.forEach(function(x,i){var y=now.list[i];if(y&&y.h!==x.h)out.push({t:x.t,was:x,now:y});});
    return out;
  }
  function bimStdChangedText(ch){
    return ch.map(function(c){
      var R=bimStdRec(c.t),nm=R?R.title:c.t,bits=[];
      if(c.was.e!==c.now.e)bits.push('the edition is now '+(c.now.e||'none'));
      var ks={},k;
      for(k in c.was.ov)ks[k]=1;for(k in c.now.ov)ks[k]=1;
      for(k in ks)if(c.was.ov[k]!==c.now.ov[k])bits.push(k+(c.now.ov.hasOwnProperty(k)?' overridden':' back to the standard'));
      if(!bits.length)bits.push('its values have changed');
      return nm+': '+bits.join(', ');
    }).join('; ');
  }
  /* ---- the project's overrides, each with its reason ---- */
  function bimStdDone(){
    try{refreshProps();}catch(e1){console.warn('[BIM] Properties could not be drawn after a standards change',e1);}
    try{bimAnalyzeRefresh(true);}catch(e2){console.warn('[BIM] Analyze could not be refreshed after a standards change',e2);}
    paint();saveSoon();
  }
  function bimStdOverride(t,n,v,why){
    var rec=bimStdRec(t),r=bimStdResolve(t),x=r&&r.ed?bimStdVal(r.ed,n):null,num=typeof v==='number'?v:parseFloat(String(v==null?'':v).replace(',','.'));
    why=bimStdTxt(why,200);
    if(!rec||!x){a3dToast('There is no '+n+' in '+(rec?rec.title:t)+' to override');return false;}
    if(rec.cat){a3dToast(rec.title+' is not applied by the app yet: there is nothing to override');return false;}
    if(x.t){a3dToast((x.say||n)+' is a table: change it with a standards pack');return false;}
    if(!isFinite(num)){a3dToast('Type a number for '+(x.say||n));return false;}
    if(x.u!=='C'&&(x.u==='%'?num<0:num<=0)){a3dToast((x.say||n)+' must be '+(x.u==='%'?'zero or more':'more than zero'));return false;}
    if(!why){a3dToast('Say why '+(x.say||n)+' is overridden: the reason shows on every result that uses it');return false;}
    pushUndo();
    bimStdW().ov[bimStdOvKey(t,n)]={v:num,why:why,at:bimSaToday()};
    bimStdTouch();bimStdDone();
    a3dToast(rec.title+': '+(x.say||n)+' is '+bimStdFmt(num,x.u)+' in this project (overridden; the standard has '+bimStdFmt(x.v,x.u)+')');
    return true;
  }
  function bimStdClear(t,n){
    var S=bimStdS(),k=bimStdOvKey(t,n),rec=bimStdRec(t);
    if(!S.ov||!S.ov.hasOwnProperty(k)){a3dToast('That value is not overridden');return false;}
    pushUndo();delete bimStdW().ov[k];bimStdTouch();bimStdDone();
    a3dToast((rec?rec.title+': ':'')+n+' is the standard\'s again');
    return true;
  }
  /* an edition chosen for the project, or null for the one in force by place and date */
  function bimStdPick(t,id){
    var rec=bimStdRec(t),i,ok=!id;
    if(!rec){a3dToast('No standard '+t);return false;}
    for(i=0;id&&i<rec.eds.length;i++)if(rec.eds[i].id===id)ok=true;
    if(!ok){a3dToast(rec.title+' has no edition '+id);return false;}
    pushUndo();var S=bimStdW();if(id)S.pick[t]=id;else delete S.pick[t];bimStdTouch();bimStdDone();
    return true;
  }
  /* ---- standards packs: files that add editions and topics, kept with the project ---- */
  function bimSha256(str){
    var K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    var H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19],B=[],i,j,c,c2;
    str=String(str);
    for(i=0;i<str.length;i++){
      c=str.charCodeAt(i);
      if(c>=0xd800&&c<0xdc00&&i+1<str.length){c2=str.charCodeAt(i+1);if(c2>=0xdc00&&c2<0xe000){c=0x10000+((c-0xd800)<<10)+(c2-0xdc00);i++;}}
      if(c<0x80)B.push(c);
      else if(c<0x800)B.push(0xc0|(c>>6),0x80|(c&63));
      else if(c<0x10000)B.push(0xe0|(c>>12),0x80|((c>>6)&63),0x80|(c&63));
      else B.push(0xf0|(c>>18),0x80|((c>>12)&63),0x80|((c>>6)&63),0x80|(c&63));
    }
    var bits=B.length*8;
    B.push(0x80);
    while(B.length%64!==56)B.push(0);
    var hi=Math.floor(bits/0x100000000),lo=bits>>>0;
    B.push((hi>>>24)&255,(hi>>>16)&255,(hi>>>8)&255,hi&255,(lo>>>24)&255,(lo>>>16)&255,(lo>>>8)&255,lo&255);
    var W=new Array(64);
    function rr(x,n){return (x>>>n)|(x<<(32-n));}
    for(i=0;i<B.length;i+=64){
      for(j=0;j<16;j++)W[j]=(B[i+4*j]<<24)|(B[i+4*j+1]<<16)|(B[i+4*j+2]<<8)|B[i+4*j+3];
      for(j=16;j<64;j++){
        var s0=rr(W[j-15],7)^rr(W[j-15],18)^(W[j-15]>>>3),s1=rr(W[j-2],17)^rr(W[j-2],19)^(W[j-2]>>>10);
        W[j]=(W[j-16]+s0+W[j-7]+s1)|0;
      }
      var a=H[0],b=H[1],cc=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
      for(j=0;j<64;j++){
        var S1=rr(e,6)^rr(e,11)^rr(e,25),ch=(e&f)^(~e&g),t1=(h+S1+ch+K[j]+W[j])|0,S0=rr(a,2)^rr(a,13)^rr(a,22),mj=(a&b)^(a&cc)^(b&cc),t2=(S0+mj)|0;
        h=g;g=f;f=e;e=(d+t1)|0;d=cc;cc=b;b=a;a=(t1+t2)|0;
      }
      H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+cc)|0;H[3]=(H[3]+d)|0;H[4]=(H[4]+e)|0;H[5]=(H[5]+f)|0;H[6]=(H[6]+g)|0;H[7]=(H[7]+h)|0;
    }
    return H.map(bimHex8).join('');
  }
  var BIM_STD_PACK_MAX=1048576;
  function bimStdOkId(v){return typeof v==='string'&&/^[a-z0-9][a-z0-9._-]{1,59}$/.test(v);}
  function bimStdOkDate(v){return v===undefined||v===''||(typeof v==='string'&&/^\d{4}(-\d{2}(-\d{2})?)?$/.test(v));}
  function bimStdOkKey(v){return v==='*'||(typeof v==='string'&&/^[a-z]{2}(-[a-z0-9]{1,3})?(:[^:]{1,80})?$/.test(v));}
  /* a pack's text read, checked and normalised; {pack, sha} or {err} */
  function bimStdPackParse(text){
    text=String(text==null?'':text);
    if(text.length>BIM_STD_PACK_MAX)return {err:'The pack is larger than 1 MB'};
    var P;
    try{P=JSON.parse(text);}catch(e){return {err:'The file is not JSON: '+String(e&&e.message||e)};}
    if(!P||P.format!=='bim-standards-pack')return {err:'This is not a standards pack: its format is not bim-standards-pack'};
    if(P.version!==1)return {err:'A pack of version '+P.version+': this app reads version 1'};
    var pub=bimStdTxt(P.publisher,120),name=bimStdTxt(P.name,120);
    if(!pub)return {err:'The pack names no publisher'};
    if(!name)return {err:'The pack has no name'};
    if(!Array.isArray(P.topics)||!P.topics.length)return {err:'The pack has no topics'};
    var have={},out=[],i,j,k;
    bimStdRecs().forEach(function(r){r.eds.forEach(function(e){have[e.id]=r.id;});});
    for(i=0;i<P.topics.length;i++){
      var T=P.topics[i],rec;
      if(!T||!bimStdOkId(T.id))return {err:'Topic '+(i+1)+' has no id of lower-case letters, digits, dots and dashes'};
      rec=bimStdRec(T.id);
      if(!Array.isArray(T.eds)||!T.eds.length)return {err:T.id+' has no editions'};
      var t2={id:T.id,title:bimStdTxt(T.title||(rec&&rec.title)||T.id,160),pub:bimStdTxt(T.pub||(rec&&rec.pub)||pub,120),kind:bimStdTxt(T.kind||'standard',20),area:bimStdTxt(T.area||'',60),access:bimStdTxt(T.access||'',60),eds:[]};
      if(!rec&&!t2.title)return {err:T.id+' has no title'};
      for(j=0;j<T.eds.length;j++){
        var E=T.eds[j];
        if(!E||!bimStdOkId(E.id))return {err:T.id+': edition '+(j+1)+' has no id'};
        if(have.hasOwnProperty(E.id))return {err:T.id+': the edition '+E.id+' is already in the registry; a revision is a new edition'};
        if(!bimStdOkDate(E.pub))return {err:E.id+': its date is not YYYY, YYYY-MM or YYYY-MM-DD'};
        var ad=[],V=[];
        if(!Array.isArray(E.adopt))return {err:E.id+' says nothing of where it is in force (adopt)'};
        for(k=0;k<E.adopt.length;k++){
          var A=E.adopt[k];
          if(!A||!bimStdOkKey(A.at)||!bimStdOkDate(A.from)||!bimStdOkDate(A.to))return {err:E.id+': adoption '+(k+1)+' is not a place key with from and to dates'};
          var a2={at:A.at};if(A.from)a2.from=A.from;if(A.to)a2.to=A.to;ad.push(a2);
        }
        var src=E.src&&typeof E.src==='object'?E.src:{},lv=/^[PSUA]$/.test(String(src.lv||''))?src.lv:'U';
        (Array.isArray(E.v)?E.v:[]).forEach(function(x){
          if(!x||typeof x.n!=='string'||!/^[a-z0-9_]{1,40}$/.test(x.n))return;
          var y={n:x.n,v:x.v,u:bimStdTxt(x.u,20),say:bimStdTxt(x.say,160)};
          if(x.t)y.t=1;
          V.push(y);
        });
        /* an edition of a topic the app applies must carry every value the app reads, of the same kind */
        if(rec&&!rec.cat){
          var B0=rec.eds[0];
          for(k=0;k<(B0.v||[]).length;k++){
            var need=B0.v[k],got=bimStdVal({v:V},need.n);
            if(!got)return {err:E.id+' lacks '+need.n+' ('+(need.say||need.n)+'), which the app reads'};
            if(need.t?(got.v===null||typeof got.v!=='object'):(typeof got.v!=='number'||!isFinite(got.v)))return {err:E.id+': '+need.n+' must be '+(need.t?'a table':'a number')};
            if(!got.u)got.u=need.u;if(!got.say)got.say=need.say;if(need.t)got.t=1;
          }
        }
        t2.eds.push({id:E.id,name:bimStdTxt(E.name||E.id,160),pub:E.pub||'',st:/^(current|superseded|announced|draft)$/.test(String(E.st||''))?E.st:'current',where:bimStdTxt(E.where||'',120),adopt:ad,
          src:{t:bimStdTxt(src.t,240),w:bimStdTxt(src.w,240),u:/^https:\/\/[^\s"<>]{3,400}$/.test(String(src.u||''))?src.u:'',lv:lv,read:bimStdOkDate(src.read)?String(src.read||''):''},method:bimStdTxt(E.method||'',40),v:V});
        have[E.id]=T.id;
      }
      out.push(t2);
    }
    return {pack:{name:name,pub:pub,date:bimStdOkDate(P.date)?String(P.date||''):'',topics:out},sha:bimSha256(text)};
  }
  /* what a pack would change, before it applies: each topic's edition in force, and its values */
  function bimStdPackDiff(text){
    var R=bimStdPackParse(text);
    if(R.err)return {ok:false,err:R.err};
    var S=bimStdS(),ts=R.pack.topics.map(function(t){return t.id;}),was={},now={},i;
    if((S.packs||[]).some(function(p){return p.sha===R.sha;}))return {ok:false,err:'This pack is already applied to the project',sha:R.sha};
    ts.forEach(function(t){var r=bimStdResolve(t);was[t]=r?{ed:r.ed,how:r.how}:null;});
    if(!A3D.site||typeof A3D.site!=='object')return {ok:false,err:'The project has no site'};
    var held=A3D.site.std,trial=bimStdCopy(S);
    trial.packs=(S.packs||[]).concat([{sha:R.sha,name:R.pack.name,pub:R.pack.pub,topics:R.pack.topics}]);trial.rev=(S.rev||0)+0.5;
    A3D.site.std=trial;A3D_STD.at=0;
    try{ts.forEach(function(t){var r=bimStdResolve(t);now[t]=r?{ed:r.ed,how:r.how}:null;});}
    finally{A3D.site.std=held;A3D_STD.at=0;}
    var out=R.pack.topics.map(function(t){
      var a=was[t.id],b=now[t.id],ch=[];
      if(a&&a.ed&&b&&b.ed&&a.ed.id!==b.ed.id)(b.ed.v||[]).forEach(function(x){var y=bimStdVal(a.ed,x.n);if(!y||JSON.stringify(y.v)!==JSON.stringify(x.v))ch.push({n:x.n,say:x.say||'',from:y?y.v:null,to:x.v,u:x.u||''});});
      return {t:t.id,title:t.title,adds:t.eds.map(function(e){return e.name;}),before:a&&a.ed?a.ed.id:null,beforeHow:a?a.how:null,after:b&&b.ed?b.ed.id:null,afterHow:b?b.how:null,changes:ch,applied:!!(bimStdRec(t.id)&&!bimStdRec(t.id).cat)};
    });
    return {ok:true,sha:R.sha,name:R.pack.name,pub:R.pack.pub,date:R.pack.date,topics:out,signed:false};
  }
  function bimStdPackApply(text){
    var D=bimStdPackDiff(text),R;
    if(!D.ok){a3dToast('The pack was not applied: '+D.err);return D;}
    R=bimStdPackParse(text);
    pushUndo();
    bimStdW().packs.push({sha:R.sha,name:R.pack.name,pub:R.pack.pub,date:R.pack.date,at:bimSaToday(),topics:R.pack.topics});
    bimStdTouch();bimStdDone();
    a3dToast('The pack '+R.pack.name+' ('+R.pack.pub+', unsigned) is applied: '+D.topics.length+' topic'+(D.topics.length===1?'':'s')+'. Its SHA-256: '+R.sha.slice(0,16)+'...');
    return D;
  }
  function bimStdPackRemove(sha){
    var S=bimStdS(),n=(S.packs||[]).length;
    if(!(S.packs||[]).some(function(p){return p.sha===sha;})){a3dToast('No pack '+String(sha).slice(0,16)+' in this project');return false;}
    pushUndo();var W=bimStdW();W.packs=W.packs.filter(function(p){return p.sha!==sha;});
    Object.keys(W.pick).forEach(function(t){var r=bimStdRec(t);if(!r||!r.eds.some(function(e){return e.id===W.pick[t]&&e.pack!==sha;}))delete W.pick[t];});
    bimStdTouch();bimStdDone();
    a3dToast('The pack is removed ('+(n-W.packs.length)+')');
    return true;
  }
'''

BLOCK = BLOCK.replace('__LONDON__', ','.join("'gb-%s'" % c for c in LONDON))
BLOCK = BLOCK.replace('__OCC__', '[\n' + OCC_ROWS + ']')
BLOCK = BLOCK.replace('__ROADW__', ROAD_W)
BLOCK = js_ascii(BLOCK)

rep("  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};\n",
    BLOCK + "  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};\n")

# the address search asks for the address's parts, and the place found becomes the site's place
rep("  var BIM_GEOCODE_URL='https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=';",
    "  var BIM_GEOCODE_URL='https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&addressdetails=1&q=';   /* __acad3dV167: addressdetails, for the place */")
rep("      try{bimMapPlace(lat,lon,nm);}",
    "      try{bimMapPlace(lat,lon,nm,hit.address);}   /* __acad3dV167 */")
rep("  function bimMapPlace(lat,lon,name){",
    "  function bimMapPlace(lat,lon,name,addr){")
rep("    if(name)A3D.site.address=name;\n    A3D.site.map=A3D.site.map||{};",
    "    if(name)A3D.site.address=name;\n"
    "    /* __acad3dV167: the place found is the site's place, for the standards in force there (one undo step with the move) */\n"
    "    if(addr&&typeof addr==='object'&&addr.country_code){try{bimStdPlaceFromAddress(addr);}catch(eSt){console.warn('[BIM] The site\\'s place could not be kept',eSt);}}\n"
    "    A3D.site.map=A3D.site.map||{};")

# the hooks
HOOKS = r'''  /* __acad3dV167: the standards registry */
  window.__a3dStd=function(t,n){return bimStd(t,n);};
  window.__a3dStdSay=function(t,n){return bimStdSay(t,n);};
  window.__a3dStdEdition=function(t){return bimStdEdition(t);};
  window.__a3dStdUsed=function(t){return bimStdUsedText(t);};
  window.__a3dStdStamp=function(ts){return bimStdStamp(ts);};
  window.__a3dStdChanged=function(st){return bimStdChanged(st);};
  window.__a3dStdRecords=function(){return JSON.parse(JSON.stringify(bimStdRecs().map(function(r){return {id:r.id,title:r.title,pub:r.pub,kind:r.kind,area:r.area,cat:!!r.cat,anywhere:!!r.anywhere,
    eds:r.eds.map(function(e){return {id:e.id,name:e.name,pub:e.pub,st:e.st,where:e.where,adopt:e.adopt,src:e.src,method:e.method||'',pack:e.pack||null,v:e.v};})};})));};
  window.__a3dStdPath=function(){return bimStdPath();};
  window.__a3dStdPlace=function(){var p=bimStdPlace();return p?JSON.parse(JSON.stringify(p)):null;};
  window.__a3dStdSetPlace=function(p,src){return bimStdSetPlace(p,src||'hand');};
  window.__a3dStdPlaceFromAddress=function(a){pushUndo();var ok=bimStdPlaceFromAddress(a);bimStdDone();return ok;};
  window.__a3dStdSetDate=function(d){return bimStdSetDate(d);};
  window.__a3dStdOverride=function(t,n,v,why){return bimStdOverride(t,n,v,why);};
  window.__a3dStdClear=function(t,n){return bimStdClear(t,n);};
  window.__a3dStdPick=function(t,id){return bimStdPick(t,id||null);};
  window.__a3dStdPackDiff=function(text){return bimStdPackDiff(text);};
  window.__a3dStdPackApply=function(text){return bimStdPackApply(text);};
  window.__a3dStdPackRemove=function(sha){return bimStdPackRemove(sha);};
  window.__a3dStdState=function(){var s=A3D.site&&A3D.site.std;return s?JSON.parse(JSON.stringify(s)):null;};
  window.__a3dSha256=function(t){return bimSha256(t);};
'''
rep("  window.__acad3dV166b=", js_ascii(HOOKS) + "  window.__acad3dV166b=")

for name in ['__a3dStd', '__a3dStdSay', '__a3dStdEdition', '__a3dStdUsed', '__a3dStdStamp', '__a3dStdChanged', '__a3dStdRecords',
             '__a3dStdPath', '__a3dStdPlace', '__a3dStdSetPlace', '__a3dStdPlaceFromAddress', '__a3dStdSetDate', '__a3dStdOverride',
             '__a3dStdClear', '__a3dStdPick', '__a3dStdPackDiff', '__a3dStdPackApply', '__a3dStdPackRemove', '__a3dStdState', '__a3dSha256']:
    n = s.count('window.%s=' % name)
    if n != 1:
        sys.exit('window.%s= defined %d times' % (name, n))
for fn in ['bimStd', 'bimStdSay', 'bimStdEdition', 'bimStdStamp', 'bimStdChanged', 'bimSha256', 'bimStdResolve', 'bimStdPath']:
    n = len(re.findall(r'function %s\(' % fn, s))
    if n != 1:
        sys.exit('function %s defined %d times' % (fn, n))

out = s.encode('utf-8')
added = [l for l in s.splitlines() if '__acad3dV167' in l or 'bimStd' in l]
for l in added:
    if any(ord(c) > 127 for c in l):
        sys.exit('non-ASCII in a new line: %r' % l[:80])
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
