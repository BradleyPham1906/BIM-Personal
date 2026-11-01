  /* ================= __acad3dV167: the standards registry =================
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
  var BIM_STD_LONDON=['gb-lnd','gb-bdg','gb-bne','gb-bex','gb-ben','gb-bry','gb-cmd','gb-cry','gb-eal','gb-enf','gb-gre','gb-hck','gb-hmf','gb-hry','gb-hrw','gb-hav','gb-hil','gb-hns','gb-isl','gb-kec','gb-ktt','gb-lbh','gb-lew','gb-mrt','gb-nwm','gb-rdb','gb-ric','gb-swk','gb-stn','gb-twh','gb-wft','gb-wnd','gb-wsm'];
  function bimStdAt(keys,from,to){return keys.map(function(k){var a={at:k};if(from)a.from=from;if(to)a.to=to;return a;});}
  var BIM_STD=[
    /* ---- transit and walking ---- */
    {id:'tfl.ptal',title:'Public Transport Accessibility Level (PTAL)',pub:'Transport for London',kind:'method',area:'Transit and walking',use:'Transit layer, its finding and the walk catchments',anywhere:true,
      eds:[{id:'tfl.ptal.2015',name:'Assessing transport connectivity in London (2015)',pub:'2015-04-23',st:'current',where:'Greater London',adopt:bimStdAt(BIM_STD_LONDON,'2015-04-23'),
        src:{t:'Transport for London, Assessing transport connectivity in London',w:'section 2.5, the calculation of PTAL, and Table 2.2',u:'https://content.tfl.gov.uk/connectivity-assessment-guide.pdf',lv:'P',read:'2026-10-18'},method:'ptal.2015',
        v:[{n:'walk_bus',v:8,u:'min',say:'the walk to a bus stop',src:'up to 640 m, about eight minutes',lt:'walk_rail'},
          {n:'walk_rail',v:12,u:'min',say:'the walk to a rail, Tube or DLR station',src:'up to 960 m, 12 minutes',gt:'walk_bus'},
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
    {id:'who.noise',title:'WHO environmental noise guidelines: road traffic',pub:'World Health Organization Regional Office for Europe',kind:'guideline',area:'Roads and noise',use:'Noise layer, for scale',anywhere:true,
      eds:[{id:'who.noise.2018',name:'Environmental Noise Guidelines for the European Region (2018)',pub:'2018',st:'current',where:'Guidance for the WHO European Region, adopted nowhere as a rule',adopt:[],
        src:{t:'WHO Regional Office for Europe, Environmental Noise Guidelines for the European Region',w:'3.1, road traffic noise: the two strong recommendations',u:'https://iris.who.int/handle/10665/279952',lv:'P',read:'2026-10-18'},
        v:[{n:'road_lden',v:53,u:'dB',say:'road traffic noise, average exposure (Lden)',src:'53.3 dB rounded to 53'},{n:'road_lnight',v:45,u:'dB',say:'road traffic noise at night (Lnight)'}]}]},
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
          {n:'pm25_it1_year',v:35,u:'ug/m3',say:'the first interim target, annual'},
          {n:'pm25_24h_it1',v:75,u:'ug/m3',say:'the first interim target, 24-hour'},{n:'pm25_24h_it2',v:50,u:'ug/m3',say:'the second interim target, 24-hour'},
          {n:'pm25_24h_it3',v:37.5,u:'ug/m3',say:'the third interim target, 24-hour'},{n:'pm25_24h_it4',v:25,u:'ug/m3',say:'the fourth interim target, 24-hour'}]}]},
    /* ---- flood and ground ---- */
    {id:'fema.zones',title:'Flood zones',pub:'Federal Emergency Management Agency',kind:'classification',area:'Flood and ground',use:'Flood zones layer and its finding',anywhere:true,
      eds:[{id:'fema.zones.cfr',name:'44 CFR 64.3, the flood insurance rate map\'s zone symbols',pub:'1976-10-26',st:'current',where:'United States',adopt:[{at:'us',from:'1976-10-26'}],
        src:{t:'Code of Federal Regulations, title 44, section 64.3 (eCFR, current to 2026-10-01)',w:'(a)(1), the zone symbols',u:'https://www.ecfr.gov/current/title-44/section-64.3',lv:'P',read:'2026-10-18'},method:'fema.nfhl.1',
        v:[{n:'groups',t:1,say:'how the layer groups FEMA\'s zones',v:{floodway:'the regulatory floodway, from the NFHL\'s zone subtype',coastal:'V, VE, V1-30 and VO: special flood hazard with velocity',
          sfha:'A, AE, A1-30, AH, AO, A99 and AR: special flood hazard',x02:'B, or X with the 0.2% subtype: moderate flood hazard',undetermined:'D: possible but undetermined flood hazard'}}]}]},
    {id:'land.slope',title:'Slope classes for development',pub:'This app',kind:'assumption',area:'Flood and ground',use:'Slope layer and its finding',anywhere:true,
      eds:[{id:'land.slope.1',name:'The app\'s working set (V165)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: a working set from planning practice, 15% and 25% the decision points; the bands vary by place',w:'research-site-analysis-in-model.md, section 2',lv:'A'},
        v:[{n:'b1',v:5,u:'%',say:'flat to gentle, up to',lt:'b2'},{n:'b2',v:10,u:'%',say:'moderate, up to',gt:'b1',lt:'b3'},{n:'b3',v:15,u:'%',say:'moderately steep, up to',gt:'b2',lt:'b4'},{n:'b4',v:25,u:'%',say:'steep, up to',gt:'b3'}]}]},
    /* __acad3dV172: Buildable area, Pennsylvania's site capacity calculation, the owner's choice (2026-10-27) */
    {id:'land.site_capacity',title:'Site capacity: the open space ratios of resource protection land',pub:'Chalfont Borough, Pennsylvania',kind:'code',area:'Flood and ground',use:'Buildable area (the site analysis tools)',anywhere:true,
      eds:[{id:'land.site_capacity.chalfont',name:'Chalfont Borough Zoning, section 440-17, site capacity calculations',pub:'',st:'current',where:'Chalfont, Pennsylvania',adopt:[{at:'us-pa:chalfont'}],
        src:{t:'Chalfont Borough Code, Chapter 440 Zoning, section 440-17 Site capacity calculations, B, the resources and their open space ratios; read in Zoneomics\' copy of the code, not the borough\'s own',w:'section 440-17 B',u:'https://www.zoneomics.com/code/chalfont-PA/chapter_5',lv:'S',read:'2026-10-27'},
        v:[{n:'floodplain',v:1,u:'ratio',say:'floodplains'},{n:'slope_lo',v:15,u:'%',say:'the lower class of steep slopes from',lt:'slope_hi'},{n:'slope_hi',v:25,u:'%',say:'the upper class of steep slopes from',gt:'slope_lo'},
          {n:'slope_a',v:0.7,u:'ratio',say:'steep slopes of the lower class'},{n:'slope_b',v:0.85,u:'ratio',say:'steep slopes of the upper class'},
          {n:'forest',v:0.5,u:'ratio',say:'forested areas with no other resource'},{n:'forest_with',v:0.8,u:'ratio',say:'forested areas with another resource'},
          {n:'pond',v:1,u:'ratio',say:'ponds'},{n:'waters',v:1,u:'ratio',say:'waters of the Commonwealth'},{n:'wetland',v:1,u:'ratio',say:'wetlands'}]}]},
    {id:'terrain.slope_bands',title:'Slope bands on terrain',pub:'This app',kind:'assumption',area:'Flood and ground',use:'Terrain coloured by slope (V144)',anywhere:true,
      eds:[{id:'terrain.slope_bands.1',name:'The app\'s bands (V144), three at the 2010 ADA Standards\' limits',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app; 5% and 8.33% are the 2010 ADA Standards\' 1:20 walking slope and 1:12 ramp slope, 2% their 1:48 cross slope rounded',w:'ADA Standards 403.3 and 405.2',u:'https://www.ada.gov/law-and-regs/design-standards/2010-stds/',lv:'P',read:'2026-10-18'},
        v:[{n:'bands',t:1,v:[0,2,5,8.33,15,25,50],u:'%',say:'the band edges'}]}]},
    /* ---- buildings and structure ---- */
    {id:'ibc.occupant_load',title:'Occupant load factors',pub:'International Code Council',kind:'code',area:'Buildings',use:'Rooms\' occupant loads and the area plans',anywhere:true,
      eds:[{id:'ibc.2021.1004.5',name:'International Building Code 2021, Table 1004.5',pub:'2020-10',st:'current',where:'Pennsylvania (the Uniform Construction Code)',adopt:[{at:'us-pa',from:'2026-01-01'}],
          src:{t:'International Building Code 2021, Table 1004.5, maximum floor area allowances per occupant; adopted in Pennsylvania by 34 Pa. Code 403.21',w:'the table as V105 read it (the same in 2018 and 2021); the adoption in 34 Pa. Code 403.21, effective 1 January 2026',u:'https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/034/chapter403/s403.21.html',lv:'S',read:'2026-10-18'},
          v:[{n:'table',t:1,u:'sq ft',say:'square feet per occupant, gross or net, by use',v:[
    ['Accessory storage areas, mechanical equipment room',300,'gross'],
    ['Agricultural building',300,'gross'],
    ['Aircraft hangars',500,'gross'],
    ['Airport terminal - baggage claim',20,'gross'],
    ['Airport terminal - baggage handling',300,'gross'],
    ['Airport terminal - concourse',100,'gross'],
    ['Airport terminal - waiting areas',15,'gross'],
    ['Assembly - exhibit gallery and museum',30,'net'],
    ['Assembly - gaming floors',11,'gross'],
    ['Assembly without fixed seats - concentrated',7,'net'],
    ['Assembly without fixed seats - standing space',5,'net'],
    ['Assembly without fixed seats - unconcentrated',15,'net'],
    ['Business areas',150,'gross'],
    ['Courtrooms - other than fixed seating areas',40,'net'],
    ['Day care',35,'net'],
    ['Dormitories',50,'gross'],
    ['Educational - classroom area',20,'net'],
    ['Educational - shops and other vocational room areas',50,'net'],
    ['Exercise rooms',50,'gross'],
    ['Group H-5 fabrication and manufacturing areas',200,'gross'],
    ['Industrial areas',100,'gross'],
    ['Institutional - inpatient treatment areas',240,'gross'],
    ['Institutional - outpatient areas',100,'gross'],
    ['Institutional - sleeping areas',120,'gross'],
    ['Kitchens, commercial',200,'gross'],
    ['Library - reading rooms',50,'net'],
    ['Library - stack area',100,'gross'],
    ['Locker rooms',50,'gross'],
    ['Mercantile',60,'gross'],
    ['Mercantile - storage, stock, shipping areas',300,'gross'],
    ['Parking garages',200,'gross'],
    ['Residential',200,'gross'],
    ['Skating rinks, swimming pools - decks',15,'gross'],
    ['Skating rinks, swimming pools - rink and pool',50,'gross'],
    ['Stages and platforms',15,'net'],
    ['Warehouses',500,'gross']]}]},
        {id:'ibc.2018.1004.5',name:'International Building Code 2018, Table 1004.5',pub:'2017-08',st:'superseded',where:'As adopted',adopt:[],
          src:{t:'International Building Code 2018, Table 1004.5',w:'the table as V105 read it (the same as 2021\'s)',lv:'S',read:'2026-10-10'},
          v:[{n:'table',t:1,u:'sq ft',say:'square feet per occupant, gross or net, by use',v:[
    ['Accessory storage areas, mechanical equipment room',300,'gross'],
    ['Agricultural building',300,'gross'],
    ['Aircraft hangars',500,'gross'],
    ['Airport terminal - baggage claim',20,'gross'],
    ['Airport terminal - baggage handling',300,'gross'],
    ['Airport terminal - concourse',100,'gross'],
    ['Airport terminal - waiting areas',15,'gross'],
    ['Assembly - exhibit gallery and museum',30,'net'],
    ['Assembly - gaming floors',11,'gross'],
    ['Assembly without fixed seats - concentrated',7,'net'],
    ['Assembly without fixed seats - standing space',5,'net'],
    ['Assembly without fixed seats - unconcentrated',15,'net'],
    ['Business areas',150,'gross'],
    ['Courtrooms - other than fixed seating areas',40,'net'],
    ['Day care',35,'net'],
    ['Dormitories',50,'gross'],
    ['Educational - classroom area',20,'net'],
    ['Educational - shops and other vocational room areas',50,'net'],
    ['Exercise rooms',50,'gross'],
    ['Group H-5 fabrication and manufacturing areas',200,'gross'],
    ['Industrial areas',100,'gross'],
    ['Institutional - inpatient treatment areas',240,'gross'],
    ['Institutional - outpatient areas',100,'gross'],
    ['Institutional - sleeping areas',120,'gross'],
    ['Kitchens, commercial',200,'gross'],
    ['Library - reading rooms',50,'net'],
    ['Library - stack area',100,'gross'],
    ['Locker rooms',50,'gross'],
    ['Mercantile',60,'gross'],
    ['Mercantile - storage, stock, shipping areas',300,'gross'],
    ['Parking garages',200,'gross'],
    ['Residential',200,'gross'],
    ['Skating rinks, swimming pools - decks',15,'gross'],
    ['Skating rinks, swimming pools - rink and pool',50,'gross'],
    ['Stages and platforms',15,'net'],
    ['Warehouses',500,'gross']]}]}]},
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
          {n:'road_w',t:1,u:'m',say:'a road\'s width by class, where neither its width nor its lanes are mapped',v:{motorway:14,motorway_link:7,trunk:12,trunk_link:7,primary:11,primary_link:6,secondary:9,secondary_link:6,tertiary:8,tertiary_link:6,residential:7,unclassified:6,living_street:6,service:4,pedestrian:6,track:3,footway:2,path:1.5,cycleway:2,steps:2,bridleway:2,corridor:2}}]}]},
    /* ---- __acad3dV168: land use, form and green ---- */
    {id:'lbcs.activity',title:'Land-Based Classification Standards (LBCS): activity',pub:'American Planning Association',kind:'classification',area:'Land and green',use:'Land use layer, its key and its finding',anywhere:true,
      eds:[{id:'lbcs.activity.apa',name:'LBCS Activity Dimension, with APA\'s colour workbook',pub:'',st:'current',where:'A model classification for planning in the United States, adopted nowhere as a rule',adopt:[],
        src:{t:'American Planning Association, LBCS Activity Dimension with Descriptions, and its workbook of colours for every dimension (LBCSColorForAllDimensions.xls)',w:'the nine top-level activities, one colour each (the workbook\'s hex and RGB strings, which agree; its separate Green and Blue columns are swapped), and the descriptions the crosswalk is checked against',u:'https://www.planning.org/lbcs/standards/activity/',lv:'P',read:'2026-10-18'},
        v:[{n:'families',t:1,say:'the top-level activities, each with its colour',v:[[1000,'Residential activities','FFFF00'],[2000,'Shopping, business, or trade','FF0000'],[3000,'Industrial, manufacturing, and waste-related','A020F0'],
          [4000,'Social, institutional, or infrastructure-related','0000FF'],[5000,'Travel or movement','BEBEBE'],[6000,'Mass assembly of people','2F4F4F'],[7000,'Leisure','90EE90'],
          [8000,'Natural resources-related','228B22'],[9000,'No human activity or unclassifiable','FFFFFF']]}]}]},
    {id:'spacematrix',title:'Spacematrix: density and form',pub:'Berghauser Pont and Haupt',kind:'method',area:'Land and green',use:'Figure-ground layer and the density finding',anywhere:true,
      eds:[{id:'spacematrix.2010',name:'Spacematrix: Space, Density and Urban Form (2010)',pub:'2010',st:'current',where:'A research method, used anywhere',adopt:[{at:'*',from:'2010'}],
        src:{t:'Godoy-Shimizu, Steadman and Evans, Density and morphology: from the building scale to the city scale, Buildings and Cities 2(1), 2021 (CC BY 4.0), its box of Spacemate\'s definitions; with Berghauser Pont, Measuring urban form',w:'FSI the floor area over the land, GSI the ground floor over the land, FSI over GSI the storeys; FSI, GSI and N the main measures; OSR as (1 - GSI) / FSI from papers citing the book (S), the book itself not read',u:'https://doi.org/10.5334/bc.83',lv:'P',read:'2026-10-18'},method:'spacematrix.2010',v:[]}]},
    {id:'green.33300',title:'The 3-30-300 rule for trees and green space',pub:'Konijnendijk; measured by Browning et al.',kind:'guideline',area:'Land and green',use:'Green and trees layer and the 3-30-300 finding',anywhere:true,
      eds:[{id:'green.33300.2024',name:'Measuring the 3-30-300 rule (Browning et al., 2024), after Konijnendijk (2023)',pub:'2024',st:'current',where:'A rule of thumb, used anywhere',adopt:[{at:'*',from:'2024'}],
        src:{t:'Browning et al., Measuring the 3-30-300 rule to help cities meet nature access thresholds, Science of the Total Environment 907, 167739 (2024), the author manuscript in full',w:'the rule as the paper states it, the green space public and at least 0.5 ha, within 300 m by the network; no radius given for the neighbourhood',u:'https://doi.org/10.1016/j.scitotenv.2023.167739',lv:'P',read:'2026-10-18'},
        v:[{n:'trees',v:3,u:'trees',say:'the trees seen from home, work or school, at least'},{n:'canopy',v:30,u:'%',say:'the tree canopy of the neighbourhood, at least'},
          {n:'walk',v:300,u:'m',say:'the walk to the nearest public green space, at most'},{n:'green_min',v:0.5,u:'ha',say:'the smallest public green space counted'}]}]},
    /* __acad3dV172: Constraints and opportunities, the app's working set */
    {id:'app.synthesis',title:'Constraints and opportunities: the distances and hours',pub:'This app',kind:'assumption',area:'Land and green',use:'Constraints and opportunities (the site analysis tools)',anywhere:true,
      eds:[{id:'app.synthesis.1',name:'The app\'s working set (V172)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: a working set for the summary plan, not a standard; set each to the place\'s own rule where it has one',w:'research-site-analysis-tools.md, sections 3 and 5',lv:'A'},
        v:[{n:'near_art',v:30,u:'m',say:'near an arterial road, within'},{n:'front',v:10,u:'m',say:'street frontage, within'},
          {n:'sunny',v:6,u:'h',say:'sunny, from'},{n:'shade',v:2,u:'h',say:'overshadowed, under'},{n:'green',v:15,u:'m',say:'near trees and woods, within'}]}]},
    {id:'app.land',title:'Land use, form and green around the site',pub:'This app',kind:'assumption',area:'Land and green',use:'Land use, figure-ground and green layers and their findings',anywhere:true,
      eds:[{id:'app.land.1',name:'The app\'s land settings (V168), with the owner\'s choices of 2026-10-18',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: the neighbourhood for the canopy (neither Konijnendijk nor Browning et al. fix one), the families the mix is counted over, the square and its cells, how far a tree seen counts, and the crosswalk from OpenStreetMap\'s tags to LBCS\'s activities, checked against LBCS\'s descriptions',w:'research-site-analysis-in-model.md, section 6',lv:'A'},
        v:[{n:'hood',v:500,u:'m',say:'the neighbourhood\'s radius for the canopy'},{n:'mix_n',v:8,u:'families',say:'the land use families the mix is counted over'},
          {n:'window',v:400,u:'m',say:'the square the land use and form are measured in, across',gt:'cell'},{n:'cell',v:100,u:'m',say:'its cells, across',lt:'window'},
          {n:'see',v:100,u:'m',say:'how far from the site a tree seen is counted'},
          {n:'xw',t:1,say:'OpenStreetMap\'s tags as LBCS\'s activities; grass and flowerbeds take the class of what they lie in',v:{weak:['landuse=grass','landuse=flowerbed'],tags:{
            'landuse=residential':1000,'building=house':1000,'building=apartments':1000,'building=residential':1000,'building=detached':1000,'building=semidetached_house':1000,'building=terrace':1000,'building=bungalow':1000,'building=dormitory':1000,'building=hotel':1000,'tourism=hotel':1000,'tourism=motel':1000,'tourism=guest_house':1000,'tourism=hostel':1000,'amenity=nursing_home':1000,'social_facility=group_home':1000,
            'landuse=commercial':2000,'landuse=retail':2000,'shop=*':2000,'office=*':2000,'building=commercial':2000,'building=retail':2000,'building=office':2000,'building=supermarket':2000,'building=kiosk':2000,'amenity=restaurant':2000,'amenity=cafe':2000,'amenity=fast_food':2000,'amenity=pub':2000,'amenity=bar':2000,'amenity=bank':2000,'amenity=marketplace':2000,
            'landuse=industrial':3000,'landuse=construction':3000,'landuse=landfill':3000,'building=industrial':3000,'building=warehouse':3000,'building=factory':3000,'man_made=works':3000,'man_made=wastewater_plant':3000,'amenity=recycling':3000,
            'landuse=education':4000,'landuse=institutional':4000,'landuse=civic_admin':4000,'landuse=cemetery':4000,'landuse=military':4000,'landuse=school':4000,'amenity=school':4000,'amenity=university':4000,'amenity=college':4000,'amenity=kindergarten':4000,'amenity=hospital':4000,'amenity=clinic':4000,'amenity=doctors':4000,'amenity=library':4000,'amenity=police':4000,'amenity=fire_station':4000,'amenity=courthouse':4000,'amenity=post_office':4000,'amenity=prison':4000,'amenity=grave_yard':4000,'building=school':4000,'building=university':4000,'building=college':4000,'building=kindergarten':4000,'building=hospital':4000,'building=civic':4000,'building=government':4000,'building=public':4000,'power=substation':4000,
            'landuse=railway':5000,'landuse=garages':5000,'amenity=parking':5000,'building=garage':5000,'building=garages':5000,'building=parking':5000,'industrial=port':5000,'landuse=port':5000,'aeroway=aerodrome':5000,'aeroway=apron':5000,
            'amenity=bus_station':6000,'building=train_station':6000,'building=transportation':6000,'aeroway=terminal':6000,'leisure=stadium':6000,'building=stadium':6000,'amenity=theatre':6000,'amenity=cinema':6000,'amenity=arts_centre':6000,'amenity=community_centre':6000,'amenity=place_of_worship':6000,'amenity=townhall':6000,'landuse=religious':6000,'landuse=churchyard':6000,'building=church':6000,'building=cathedral':6000,'building=chapel':6000,'building=mosque':6000,'building=synagogue':6000,'building=temple':6000,'tourism=museum':6000,'tourism=gallery':6000,'tourism=zoo':6000,'tourism=aquarium':6000,
            'leisure=park':7000,'leisure=playground':7000,'leisure=pitch':7000,'leisure=sports_centre':7000,'leisure=golf_course':7000,'leisure=garden':7000,'leisure=track':7000,'leisure=marina':7000,'landuse=recreation_ground':7000,'landuse=village_green':7000,'tourism=theme_park':7000,'tourism=camp_site':7000,
            'landuse=farmland':8000,'landuse=field':8000,'landuse=farmyard':8000,'landuse=orchard':8000,'landuse=vineyard':8000,'landuse=allotments':8000,'landuse=plant_nursery':8000,'landuse=greenhouse_horticulture':8000,'landuse=aquaculture':8000,'landuse=meadow':8000,'landuse=forest':8000,'landuse=quarry':8000,
            'natural=wood':9000,'natural=scrub':9000,'natural=grassland':9000,'landuse=brownfield':9000,'landuse=greenfield':9000,'landuse=grass':9000,'landuse=flowerbed':9000}}}]}]},
    /* __acad3dV169: the assets' sizes -- people, a wheelchair user, cycles and stands, parking, trees -- each from its source */
    {id:'body.us',title:'Body size: height',pub:'U.S. National Center for Health Statistics',kind:'data',area:'Assets',use:'People: their heights',anywhere:true,
      eds:[{id:'body.us.2018',name:'Anthropometric reference data, United States, 2015-2018 (NCHS, 2021)',pub:'2021-01',st:'current',where:'United States',adopt:[{at:'us',from:'2021-01'}],
        src:{t:'Fryar, Carroll, Gu, Afful and Ogden, Anthropometric reference data for children and adults: United States, 2015-2018, NCHS Vital and Health Statistics 3(46), January 2021',w:'Tables 7, 9 and 11: the mean height of men and of women aged 20 and over, and of boys aged 8',u:'https://www.cdc.gov/nchs/data/series/sr_03/sr03-046-508.pdf',lv:'P',read:'2026-10-19'},
        v:[{n:'man',v:1.753,u:'m',say:'the mean height of a man (20 and over)',src:'175.3 cm'},{n:'woman',v:1.613,u:'m',say:'the mean height of a woman (20 and over)',src:'161.3 cm'},
          {n:'child',v:1.321,u:'m',say:'the mean height of a boy of 8',src:'132.1 cm'}]}]},
    {id:'body.hidh',title:'Body proportions by height',pub:'NASA',kind:'method',area:'Assets',use:'People: their eye height and shoulder width from their height',anywhere:true,
      eds:[{id:'body.hidh.rev1',name:'Human Integration Design Handbook, Revision 1 (2014), Appendix B',pub:'2014-06-05',st:'current',where:'A method, used anywhere',adopt:[{at:'*',from:'2014'}],
        src:{t:'NASA, Human Integration Design Handbook, NASA/SP-2010-3407/REV1 (2014)',w:'Appendix B, Tables 1a and 1b: stature, sitting height, eye height sitting and bideltoid breadth for the smallest (1st percentile female) and the largest (99th percentile male); 4.2.2: linear regressions on stature from the 1988 ANSUR survey, a military population, projected to 2015',u:'https://www.nasa.gov/sites/default/files/atoms/files/human_integration_design_handbook_revision_1.pdf',lv:'P',read:'2026-10-19'},
        v:[{n:'st_lo',v:1.486,u:'m',say:'the smallest stature',lt:'st_hi'},{n:'st_hi',v:1.946,u:'m',say:'the largest stature',gt:'st_lo'},
          {n:'sit_lo',v:0.777,u:'m',say:'the smallest sitting height'},{n:'sit_hi',v:1.013,u:'m',say:'the largest sitting height'},
          {n:'eye_lo',v:0.665,u:'m',say:'the smallest eye height, sitting'},{n:'eye_hi',v:0.889,u:'m',say:'the largest eye height, sitting'},
          {n:'sh_lo',v:0.378,u:'m',say:'the narrowest shoulders (bideltoid breadth)'},{n:'sh_hi',v:0.561,u:'m',say:'the widest shoulders (bideltoid breadth)'}]}]},
    {id:'wheel.awmp',title:'Wheelchair users: size',pub:'IDeA Center, University at Buffalo, for the U.S. Access Board',kind:'data',area:'Assets',use:'The wheelchair user',anywhere:true,
      eds:[{id:'wheel.awmp.2010',name:'Anthropometry of Wheeled Mobility Project, final report (2010)',pub:'2010-12-31',st:'current',where:'A measured sample, used anywhere',adopt:[{at:'*',from:'2010'}],
        src:{t:'Steinfeld, Paquet, D\'Souza, Joseph and Maisel, Anthropometry of Wheeled Mobility Project, final report for the U.S. Access Board, IDeA Center, University at Buffalo (2010)',w:'Appendix Two, Tables 1 and 2, and pages 86 and 87: manual chair users\' occupied height and seat height, the space that holds 95% of them; the eye height of all device users (the manual chair row is not legible in the text)',u:'https://idea.ap.buffalo.edu/wp-content/uploads/sites/110/2020/01/AnthropometryofWheeledMobilityProject_FinalReport.pdf',lv:'P',read:'2026-10-19'},
        v:[{n:'height',v:1.249,u:'m',say:'a manual chair user\'s occupied height (mean)'},{n:'seat',v:0.495,u:'m',say:'the occupied seat height (mean)'},
          {n:'eye',v:1.152,u:'m',say:'the eye height (mean, all device users)'},{n:'space_w',v:0.82,u:'m',say:'the width that holds 95% of manual chair users'},{n:'space_l',v:1.42,u:'m',say:'the length that holds 95% of them'}]}]},
    {id:'ada.space',title:'Wheelchair space',pub:'U.S. Department of Justice',kind:'code',area:'Assets',use:'The wheelchair user\'s clear floor space and turning space',anywhere:true,
      eds:[{id:'ada.space.2010',name:'2010 ADA Standards for Accessible Design, 304.3.1 and 305.3',pub:'2010-09-15',st:'current',where:'United States',adopt:[{at:'us',from:'2012-03-15'}],
        src:{t:'U.S. Department of Justice, 2010 ADA Standards for Accessible Design',w:'304.3.1: a turning space 60 inches (1525 mm) across; 305.3: a clear floor space 30 inches (760 mm) by 48 inches (1220 mm) at least',u:'https://www.ada.gov/assets/pdfs/2010-design-standards.pdf',lv:'P',read:'2026-10-19'},
        v:[{n:'clear_w',v:0.76,u:'m',say:'the clear floor space\'s width'},{n:'clear_l',v:1.22,u:'m',say:'its length'},{n:'turn',v:1.525,u:'m',say:'the turning space, across'}]}]},
    {id:'mutcd.walk',title:'Walking speeds at signals',pub:'Federal Highway Administration',kind:'standard',area:'Assets',use:'The wheelchair user\'s speed',anywhere:true,
      eds:[{id:'mutcd.walk.11r1',name:'MUTCD 11th Edition with Revision 1 (December 2025), 4I.06',pub:'2025-12',st:'current',where:'United States',adopt:[{at:'us',from:'2025-12'}],
        src:{t:'FHWA, Manual on Uniform Traffic Control Devices, 11th Edition with Revision 1',w:'4I.06 paragraph 07: the clearance at 3.5 feet per second; paragraph 14: the walk and the clearance at 3 feet per second; paragraph 10: slower where people who use wheelchairs routinely cross',u:'https://mutcd.fhwa.dot.gov/kno_11th_Editionr1.htm',lv:'P',read:'2026-10-19'},
        v:[{n:'clear',v:1.067,u:'m/s',say:'the walking speed for the clearance time',src:'3.5 ft/s'},{n:'slow',v:0.914,u:'m/s',say:'the slower walking speed',src:'3 ft/s',lt:'clear'}]}]},
    {id:'ltn.cycle',title:'Cycles and cycle parking',pub:'UK Department for Transport',kind:'guideline',area:'Assets',use:'The cycle and the cycle stand',anywhere:true,
      eds:[{id:'ltn.cycle.2020',name:'Cycle Infrastructure Design, LTN 1/20 (July 2020)',pub:'2020-07',st:'current',where:'England',adopt:[{at:'gb-eng',from:'2020-07'}],
        src:{t:'Department for Transport, Cycle Infrastructure Design, Local Transport Note 1/20',w:'Table 5-1: the solo upright cycle; 11.4.6 and Table 11-2: banks of Sheffield stands',u:'https://assets.publishing.service.gov.uk/media/5ffa1f96d3bf7f65d9e35825/cycle-infrastructure-design-ltn-1-20.pdf',lv:'P',read:'2026-10-19'},
        v:[{n:'length',v:1.8,u:'m',say:'a solo upright cycle\'s length'},{n:'width',v:0.65,u:'m',say:'its width'},{n:'wheel',v:0.7,u:'m',say:'a typical wheel\'s diameter'},
          {n:'turn_out',v:1.65,u:'m',say:'its smallest turning circle, outer radius'},{n:'turn_in',v:0.85,u:'m',say:'and inner radius',lt:'turn_out'},
          {n:'gap',v:1.2,u:'m',say:'the spacing between stands, recommended'},{n:'gap_min',v:1,u:'m',say:'the spacing between stands, at least',lt:'gap'},{n:'bay',v:2,u:'m',say:'the length of a cycle parked on a stand'},
          {n:'aisle',v:3,u:'m',say:'the access aisle\'s width'},{n:'wall',v:0.6,u:'m',say:'a stand\'s clearance to a wall'},{n:'front',v:1,u:'m',say:'the clear space in front of a stand'}]}]},
    {id:'parking.bay',title:'Parking bays',pub:'UK Department for Transport',kind:'guideline',area:'Assets',use:'The parking bay',anywhere:true,
      eds:[{id:'parking.bay.mfs2007',name:'Manual for Streets (2007), 8.3',pub:'2007',st:'current',where:'England and Wales; elsewhere where no rule is recorded (the owner, 2026-10-19)',adopt:[{at:'gb-eng',from:'2007'},{at:'gb-wls',from:'2007'}],
        src:{t:'Department for Transport, Manual for Streets (2007)',w:'8.3.58: an off-street bay at least 4.8 m long by 2.4 m wide; 8.3.51: the width to reach a 2.4 m bay, by its angle',u:'https://assets.publishing.service.gov.uk/media/5a7e0035ed915d74e6223743/pdfmanforstreets.pdf',lv:'P',read:'2026-10-19'},
        v:[{n:'width',v:2.4,u:'m',say:'a bay\'s width'},{n:'length',v:4.8,u:'m',say:'a bay\'s length'},{n:'aisle90',v:6,u:'m',say:'the aisle to reach it at 90 degrees'},{n:'aisle60',v:4.2,u:'m',say:'the aisle at 60 degrees'},{n:'aisle45',v:3.6,u:'m',say:'the aisle at 45 degrees'}]}]},
    {id:'utd.trees',title:'Tree sizes',pub:'USDA Forest Service',kind:'data',area:'Assets',use:'Trees: their height and crown by type',anywhere:true,
      eds:[{id:'utd.trees.2016',name:'Urban Tree Database (McPherson, van Doorn and Peper, 2016), its measured trees',pub:'2016',st:'current',where:'A measured US sample, used anywhere',adopt:[{at:'*',from:'2016'}],
        src:{t:'McPherson, van Doorn and Peper, Urban Tree Database, Forest Service Research Data Archive RDS-2016-0005',w:'TS3_Raw_tree_data.csv: 14,487 street and park trees in 17 US cities; the medians of the trees at or above their type\'s median trunk diameter, worked out here (research-assets.md, 4)',u:'https://www.fs.usda.gov/rds/archive/catalog/RDS-2016-0005',lv:'P',read:'2026-10-19'},
        v:[{n:'types',t:1,lv:'S',say:'by type (broadleaf B or conifer C; deciduous D or evergreen E; small, medium or large): the height and the crown across, in m, and the crown over the height',
          v:[['BDS',8.2,8.7,1.07],['BDM',14,11.9,0.85],['BDL',20,15.9,0.81],['BES',8.5,8,0.96],['BEM',11.5,11.3,0.98],['BEL',16,15.1,0.98],['CES',7,6,0.87],['CEM',12.5,8.5,0.74],['CEL',20,10.7,0.57]]}]}]},
    {id:'etccdi.gsl',title:'Growing season',pub:'ETCCDI, the Expert Team on Climate Change Detection and Indices',kind:'method',area:'Assets',use:'When a deciduous tree is in leaf',anywhere:true,
      eds:[{id:'etccdi.gsl.27',name:'The 27 core climate indices: GSL, growing season length',pub:'',st:'current',where:'A method, used anywhere',adopt:[{at:'*'}],
        src:{t:'ETCCDI, the definitions of the 27 core indices',w:'GSL: from the first span of at least 6 days with a daily mean above 5 C to the first span after 1 July (1 January in the Southern Hemisphere) of 6 days below 5 C',u:'https://etccdi.pacificclimate.org/list_27_indices.shtml',lv:'P',read:'2026-10-19'},
        v:[{n:'t',v:5,u:'C',say:'the daily mean the season is counted above'},{n:'days',v:6,u:'days',say:'the span that starts and ends it'}]}]},
    {id:'aashto.vehicles',title:'Design vehicles',pub:'AASHTO',kind:'standard',area:'Assets',use:'The car, the delivery truck and the city bus, and their turning paths',anywhere:true,
      eds:[{id:'aashto.vehicles.7',name:'A Policy on Geometric Design of Highways and Streets, 7th Edition (2018), Tables 2-4b and 2-5b',pub:'2018',st:'current',where:'United States: 23 CFR 625.4 incorporates the 7th Edition for the National Highway System',adopt:[{at:'us'}],
        src:{t:'AASHTO, A Policy on Geometric Design of Highways and Streets (the Green Book), 7th Edition (2018), the owner\'s copy',w:'Table 2-4b: the design vehicles\' dimensions in metres (2-4a in feet); Table 2-5b: their minimum turning radii (2-5a in feet); 2.8.2: the turning path bounded by the outer trace of the front overhang and the path of the inner rear wheel',u:'https://store.transportation.org/',lv:'P',read:'2026-10-19'},
        v:[{n:'P_l',v:5.79,u:'m',say:'the passenger car\'s length',src:'19.0 ft'},{n:'P_w',v:2.13,u:'m',say:'its width',src:'7.0 ft'},{n:'P_h',v:1.3,u:'m',say:'its height',src:'4.3 ft'},
          {n:'P_of',v:0.91,u:'m',say:'its front overhang',src:'3.0 ft'},{n:'P_or',v:1.52,u:'m',say:'its rear overhang',src:'5.0 ft'},{n:'P_wb',v:3.35,u:'m',say:'its wheelbase',src:'11.0 ft'},
          {n:'P_r',v:7.26,u:'m',say:'its minimum design turning radius',src:'23.8 ft'},{n:'P_ctr',v:6.4,u:'m',say:'its centreline turning radius',src:'21.0 ft',gt:'P_wb',lt:'P_r'},{n:'P_rin',v:4.39,u:'m',say:'its minimum inside radius',src:'14.4 ft',lt:'P_ctr'},
          {n:'SU_l',v:9.14,u:'m',say:'the single-unit truck\'s (SU-30) length',src:'30.0 ft'},{n:'SU_w',v:2.44,u:'m',say:'its width',src:'8.0 ft'},{n:'SU_h',v:4.11,u:'m',say:'its height, the largest',src:'13.5 ft'},
          {n:'SU_hlo',v:3.35,u:'m',say:'its height, the smallest',src:'11.0 ft',lt:'SU_h'},{n:'SU_of',v:1.22,u:'m',say:'its front overhang',src:'4.0 ft'},{n:'SU_or',v:1.83,u:'m',say:'its rear overhang',src:'6.0 ft'},
          {n:'SU_wb',v:6.1,u:'m',say:'its wheelbase',src:'20.0 ft'},{n:'SU_r',v:12.73,u:'m',say:'its minimum design turning radius',src:'41.8 ft'},{n:'SU_ctr',v:11.58,u:'m',say:'its centreline turning radius',src:'38.0 ft',gt:'SU_wb',lt:'SU_r'},
          {n:'SU_rin',v:8.64,u:'m',say:'its minimum inside radius',src:'28.4 ft',lt:'SU_ctr'},
          {n:'BUS_l',v:12.19,u:'m',say:'the city transit bus\'s length',src:'40.0 ft'},{n:'BUS_w',v:2.59,u:'m',say:'its width',src:'8.5 ft'},{n:'BUS_h',v:3.2,u:'m',say:'its height',src:'10.5 ft'},
          {n:'BUS_of',v:2.13,u:'m',say:'its front overhang',src:'7.0 ft'},{n:'BUS_or',v:2.44,u:'m',say:'its rear overhang',src:'8.0 ft'},{n:'BUS_wb',v:7.62,u:'m',say:'its wheelbase',src:'25.0 ft'},
          {n:'BUS_r',v:12.8,u:'m',say:'its minimum design turning radius (Table 2-5b; Table 2-5a gives 41.6 ft, 12.68 m)',src:'12.80 m'},{n:'BUS_ctr',v:11.52,u:'m',say:'its centreline turning radius',src:'37.8 ft',gt:'BUS_wb',lt:'BUS_r'},
          {n:'BUS_rin',v:7.45,u:'m',say:'its minimum inside radius',src:'24.5 ft',lt:'BUS_ctr'}]}]},
    {id:'app.assets',title:'The assets\' own shapes',pub:'This app',kind:'assumption',area:'Assets',use:'The models\' shapes where no source sizes them',anywhere:true,
      eds:[{id:'app.assets.1',name:'The app\'s asset settings (V169)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: the seat a seated person sits on, a cycle\'s height, a Sheffield stand\'s size, a bay\'s painted line, a vehicle\'s wheels, and the crown of a mapped tree whose leaf type is not mapped (the context\'s rule since V157)',w:'research-assets.md',lv:'A'},
        v:[{n:'seat',v:0.45,u:'m',say:'the seat a seated person sits on'},{n:'bike_h',v:1.05,u:'m',say:'a cycle\'s height to its handlebars'},
          {n:'stand_w',v:0.75,u:'m',say:'a Sheffield stand\'s length'},{n:'stand_h',v:0.75,u:'m',say:'a Sheffield stand\'s height'},{n:'line',v:0.1,u:'m',say:'a bay\'s painted line, across'},
          {n:'wheel_p',v:0.65,u:'m',say:'a car\'s wheel, across'},{n:'wheel_hv',v:1,u:'m',say:'a truck\'s or a bus\'s wheel, across'},
          {n:'crown',v:0.6,u:'x',say:'a mapped tree\'s crown across, of its height, where its leaf type is not mapped'}]}]},
    /* ---- __acad3dV171: traffic and people around the site (research-traffic.md) ---- */
    {id:'idm.car',title:'Car following: the Intelligent Driver Model',pub:'Kesting, Treiber and Helbing',kind:'method',area:'Traffic',use:'Traffic and people: how each car follows the one ahead',anywhere:true,
      eds:[{id:'idm.car.2010',name:'The enhanced IDM\'s paper (2010), Table 1: a car',pub:'2010',st:'current',where:'A model, used anywhere',adopt:[{at:'*',from:'2010'}],
        src:{t:'Kesting, Treiber and Helbing, Enhanced intelligent driver model to access the impact of driving strategies on traffic capacity, Phil. Trans. R. Soc. A 368 (2010); the authors\' version, arXiv 0912.3613',w:'section 2(a), equations 2.1 and 2.2, and Table 1: a car; Treiber, The Intelligent-Driver Model and its Variants (traffic-simulation.de): the free road and the step',u:'https://arxiv.org/abs/0912.3613',lv:'P',read:'2026-10-24'},
        v:[{n:'T',v:1.5,u:'s',say:'the time gap a driver keeps'},{n:'s0',v:2,u:'m',say:'the gap kept standing'},{n:'a',v:1.4,u:'m/s2',say:'the acceleration'},
          {n:'b',v:2,u:'m/s2',say:'the comfortable deceleration'},{n:'delta',v:4,u:'',say:'the acceleration exponent'},
          {n:'free',v:1000,u:'m',say:'the gap ahead of a car with nothing ahead',src:'Treiber: a free road is a gap of 1000 m'},
          {n:'step_max',v:0.5,u:'s',say:'the longest step giving the same result',src:'Treiber: any step below 0.5 s gives essentially the same'}]}]},
    {id:'mobil',title:'Lane changes: MOBIL',pub:'Kesting, Treiber and Helbing',kind:'method',area:'Traffic',use:'Traffic and people: a car changing lanes on a street with two or more each way',anywhere:true,
      eds:[{id:'mobil.2007',name:'MOBIL: General Lane-Changing Model for Car-Following Models (2007)',pub:'2007',st:'current',where:'A model, used anywhere',adopt:[{at:'*',from:'2007'}],
        src:{t:'Kesting, Treiber and Helbing, MOBIL: General Lane-Changing Model for Car-Following Models, Transportation Research Record 1999 (2007); the authors\' manuscript',w:'sections 2.1 and 2.2, the symmetric incentive (equation 3), and Table 1',u:'https://mtreiber.de/publications/MOBIL_TRB.pdf',lv:'P',read:'2026-10-25'},
        v:[{n:'p',v:1,u:'',say:'the politeness factor',src:'Table 1: 0 to 1; at 1 the ideal MOBIL, with no free parameter'},
          {n:'thr',v:0.1,u:'m/s2',say:'the changing threshold'},{n:'bsafe',v:4,u:'m/s2',say:'the most a new follower may have to brake'}]}]},
    {id:'stm.signal',title:'Signal timing',pub:'Federal Highway Administration',kind:'guideline',area:'Traffic',use:'Traffic and people: each signal\'s cycle, greens and change intervals',anywhere:true,
      eds:[{id:'stm.signal.2008',name:'Traffic Signal Timing Manual (FHWA-HOP-08-024, 2008)',pub:'2008-06',st:'current',where:'Guidance for the United States',adopt:[{at:'us',from:'2008-06'}],
        src:{t:'FHWA, Traffic Signal Timing Manual (FHWA-HOP-08-024, June 2008)',w:'3.3: the saturation flow and lost time; 5.3: Equation 5-2 (Kell and Fullerton) and Table 5-3; 6.4: Equation 6-1 (Webster), the least and the preferred most cycle',u:'https://ops.fhwa.dot.gov/publications/fhwahop08024/',lv:'P',read:'2026-10-25'},
        v:[{n:'sat',v:1900,u:'pc/h/ln',say:'the ideal saturation flow',src:'3.3.2: typically assumed 1,900 passenger cars an hour a lane'},
          {n:'lost',v:4,u:'s',say:'the lost time a phase',src:'3.3.3: the HCM\'s default, start-up and clearance lost time'},
          {n:'webster',t:1,v:[1.5,5],say:'Webster\'s optimum cycle, (1.5 L + 5) / (1 - Y)',src:'Equation 6-1'},
          {n:'cycle_min',v:60,u:'s',say:'the least cycle',src:'6.4: the minimum suggested for use',lt:'cycle_max'},
          {n:'cycle_max',v:120,u:'s',say:'the longest cycle, for a four-legged junction',src:'6.4: preferred not to exceed 120 seconds',gt:'cycle_min'},
          {n:'kf_t',v:1,u:'s',say:'the driver\'s reaction to the yellow',src:'Equation 5-2\'s t, 1.0 s often cited'},
          {n:'kf_a',v:3.048,u:'m/s2',say:'the deceleration at the yellow',src:'10 ft/s2'},
          {n:'kf_lv',v:6.096,u:'m',say:'a vehicle\'s length, for the red clearance',src:'20 ft'},
          {n:'min_green',t:1,u:'s',v:{fast:10,major:7,minor:4,local:2},say:'the least green by the approach\'s class: a major arterial over 40 mph, a major arterial, a minor arterial, a collector or local street',src:'Table 5-3\'s lower values'},
          {n:'fast',v:64.37,u:'km/h',say:'a major arterial\'s speed above which its least green is the longer one',src:'40 mph'}]}]},
    {id:'mutcd.signal',title:'Signal intervals',pub:'Federal Highway Administration',kind:'standard',area:'Traffic',use:'Traffic and people: the yellow, the red clearance and WALK',anywhere:true,
      eds:[{id:'mutcd.signal.11',name:'MUTCD 11th Edition (December 2023), 4F.17 and 4I.06',pub:'2023-12',st:'current',where:'United States',adopt:[{at:'us',from:'2023-12'}],
        src:{t:'FHWA, Manual on Uniform Traffic Control Devices, 11th Edition (December 2023)',w:'4F.17: a yellow of 3 to 6 s, a red clearance of at most 6 s; 4I.06: WALK at least 7 s, the clearance at 3.5 ft/s (mutcd.walk)',u:'https://mutcd.fhwa.dot.gov/',lv:'P',read:'2026-10-24'},
        v:[{n:'yel_min',v:3,u:'s',say:'the shortest yellow',lt:'yel_max'},{n:'yel_max',v:6,u:'s',say:'the longest yellow',gt:'yel_min'},
          {n:'red_max',v:6,u:'s',say:'the longest red clearance'},{n:'walk',v:7,u:'s',say:'WALK, at least'}]}]},
    {id:'fdot.k',title:'The peak hour\'s share of the day\'s traffic (K)',pub:'Florida Department of Transportation',kind:'data',area:'Traffic',use:'Traffic and people: each street\'s traffic in the peak hour',anywhere:true,
      eds:[{id:'fdot.k.2014',name:'Project Traffic Forecasting Handbook (January 2014), Figure 2.4',pub:'2014-01',st:'current',where:'Florida',adopt:[{at:'us-fl',from:'2014-01'}],
        src:{t:'Florida Department of Transportation, Project Traffic Forecasting Handbook (January 2014)',w:'2.6.2.1 and Figure 2.4: the standard K factors',u:'https://www.fdot.gov/docs/default-source/statistics/trafficdata/PTF.pdf',lv:'P',read:'2026-10-24'},
        v:[{n:'k',v:9,u:'%',say:'the share of the day\'s traffic in the weekday peak hour, on urban arterials',src:'Figure 2.4: arterials and highways, urbanized and urban areas, 9.0%'}]}]},
    {id:'nchrp255',title:'Turns at a junction from the streets\' traffic',pub:'Transportation Research Board',kind:'method',area:'Traffic',use:'Traffic and people: which way a car turns',anywhere:true,
      eds:[{id:'nchrp255.1982',name:'NCHRP Report 255 (1982), chapter 8',pub:'1982-12',st:'current',where:'A method, used anywhere',adopt:[{at:'*',from:'1982-12'}],
        src:{t:'Pedersen and Samdahl, NCHRP Report 255, Highway Traffic Data for Urbanized Area Project Planning and Design (TRB, December 1982)',w:'chapter 8, pages 110 to 118: a first guess of the turns, the matrix balanced by rows and columns to the streets\' volumes',u:'https://onlinepubs.trb.org/Onlinepubs/nchrp/nchrp_rpt_255.pdf',lv:'P',read:'2026-10-24'},
        v:[{n:'iter',v:10,u:'',say:'the balancing\'s rounds',src:'six to ten: the most'}]}]},
    {id:'sd.trips',title:'Trips a site makes',pub:'City of San Diego',kind:'data',area:'Traffic',use:'Traffic and people: the design\'s own trips in the peak hour',anywhere:true,
      eds:[{id:'sd.trips.2003',name:'Trip Generation Manual (revised May 2003), Table 1',pub:'2003-05',st:'current',where:'San Diego',adopt:[{at:'us-ca:san diego',from:'2003-05'}],
        src:{t:'City of San Diego, Trip Generation Manual (revised May 2003)',w:'Table 1, the driveway vehicle trip rates with the AM and PM peak hours\' shares and in:out splits: the residential, office, retail and lodging rows',u:'https://www.sandiego.gov/sites/default/files/legacy/planning/documents/pdf/trans/tripmanual.pdf',lv:'P',read:'2026-10-25'},
        v:[{n:'table',t:1,say:'a weekday\'s trips by use, and the peak hours\' shares (percent) with their in:out',
            v:{mdu_lo:{name:'Multiple dwelling units, under 20 an acre',rate:8,per:'du',am:[8,2,8],pm:[10,7,3]},
              mdu_hi:{name:'Multiple dwelling units, over 20 an acre',rate:6,per:'du',am:[8,2,8],pm:[9,7,3]},
              office:{name:'Commercial office',ln:[0.756,3.95],per:'ksf',am:[13,9,1],pm:[14,2,8]},
              retail:{name:'Specialty retail centre or strip commercial',rate:40,per:'ksf',am:[3,6,4],pm:[9,5,5]},
              hotel:{name:'Hotel',rate:10,per:'room',am:[6,6,4],pm:[8,6,4]}}},
          {n:'dense',v:20,u:'du/acre',say:'the density above which a dwelling makes fewer trips'}]}]},
    {id:'hm.walk',title:'Walking speeds of a crowd',pub:'Helbing and Molnar',kind:'data',area:'Traffic',use:'Traffic and people: each walker\'s own speed',anywhere:true,
      eds:[{id:'hm.walk.1995',name:'Social force model for pedestrian dynamics (1995), the simulations\' values',pub:'1995',st:'current',where:'A measured sample, used anywhere',adopt:[{at:'*',from:'1995'}],
        src:{t:'Helbing and Molnar, Social force model for pedestrian dynamics, Phys. Rev. E 51, 4282 (1995); the authors\' version, arXiv cond-mat/9805244',w:'section III: desired speeds Gaussian, mean 1.34 m/s and spread 0.26 m/s (citing Henderson\'s measurements, not read), each capped at 1.3 times its own',u:'https://arxiv.org/abs/cond-mat/9805244',lv:'S',read:'2026-10-24'},
        v:[{n:'mean',v:1.34,u:'m/s',say:'the mean desired walking speed'},{n:'sd',v:0.26,u:'m/s',say:'its spread (standard deviation)'},{n:'cap',v:1.3,u:'x',say:'the most a walker goes, of its own speed'}]}]},
    {id:'sumo.rules',title:'Junctions and walkers in a simulation',pub:'Eclipse SUMO',kind:'method',area:'Traffic',use:'Traffic and people: giving way, and the walkers\' stripes',anywhere:true,
      eds:[{id:'sumo.rules.docs',name:'Eclipse SUMO\'s documentation (read October 2026)',pub:'',st:'current',where:'A simulator\'s rules, used anywhere',adopt:[{at:'*'}],
        src:{t:'Eclipse SUMO\'s documentation: Simulation/Intersections, Networks/PlainXML (right of way), the junction model parameters, Simulation/Pedestrians (striping)',w:'a minor road keeps a time gap of at least 1 s to a priority car not yet in the junction (jmTimegapMinor); right of way from the ways in: the two sharing the highest priority (then speed and lanes), or the one alone with the way in most nearly opposite it; on amber a car far away slows and one near goes; walkers in stripes of 0.65 m',u:'https://github.com/eclipse-sumo/sumo',lv:'S',read:'2026-10-24'},
        v:[{n:'gap',v:1,u:'s',say:'the time gap a minor road keeps to a priority car'},{n:'stripe',v:0.65,u:'m',say:'a walker\'s stripe across a sidewalk'}]}]},
    {id:'app.traffic',title:'The traffic simulation\'s own settings',pub:'This app',kind:'assumption',area:'Traffic',use:'Traffic and people: what no source gives',anywhere:true,
      eds:[{id:'app.traffic.1',name:'The app\'s traffic settings (V171)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: the reach of the simulation, a lane\'s width as the site context draws it, how near a signal is to its junction, the step, the warm-up and the tallies, how far ahead a car sees, what a crossing costs a walker choosing a way, a left turn, the sidewalks\' and crossings\' places, the queue\'s and the crossings\' tests, a car\'s people, and the usages read as San Diego\'s uses',w:'research-traffic.md, section 8',lv:'A'},
        v:[{n:'radius',v:300,u:'m',say:'the streets simulated, from the lot'},{n:'lane_w',v:3.3,u:'m',say:'a lane\'s width'},
          {n:'sig_r',v:30,u:'m',say:'how near a mapped signal is to the junction it controls'},{n:'step',v:0.2,u:'s',say:'the simulation\'s step'},
          {n:'warm',v:300,u:'s',say:'the warm-up before the tallies start'},{n:'bin',v:10,u:'s',say:'the tallies\' bins'},
          {n:'sw_off',v:1.5,u:'m',say:'a sidewalk\'s line beyond the roadway\'s edge'},{n:'cw',v:2,u:'m',say:'a crossing behind the corner'},
          {n:'y_max',v:0.95,u:'',say:'the junction\'s demand over its capacity at which the cycle is the longest'},
          {n:'walk_gap',v:2,u:'s',say:'the time a car must be away for a walker to cross where no signal is'},
          {n:'look',v:100,u:'m',say:'how far ahead a car sees the next street\'s stop line'},
          {n:'x_sig',v:30,u:'s',say:'a signalled crossing\'s wait, as a walker weighs it choosing a way: half the shortest cycle'},
          {n:'x_lane',v:10,u:'s',say:'each lane crossed where nothing signals it, as a walker weighs it choosing a way'},
          {n:'left',v:30,u:'deg',say:'a turn this sharp to the left or sharper waits for the oncoming'},
          {n:'queue_v',v:2,u:'m/s',say:'a car slower than this is standing in a queue'},{n:'queue_r',v:100,u:'m',say:'the street before the lot\'s entry counted for its queue'},
          {n:'occ',v:1,u:'',say:'the people a car brings'},
          {n:'uses',t:1,v:{'use-res':'mdu','use-off':'office','use-ret':'retail','use-hot':'hotel'},say:'the usages read as San Diego\'s uses: Residential as multiple dwelling units, Office as commercial office, Retail as strip commercial, Hotel as hotel'}]}]},
    {id:'app.climate',title:'Climate readings',pub:'This app',kind:'assumption',area:'Climate',use:'The climate board, the wind rose and its finding',anywhere:true,
      eds:[{id:'app.climate.1',name:'The app\'s climate settings (V159)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: a degree-day base, a calm threshold and the rose\'s speed bins, and a comfort band',w:'research-climate-risk-presentation.md',lv:'A'},
        v:[{n:'base',v:18,u:'C',say:'the degree-day base temperature'},{n:'calm',v:0.5,u:'m/s',say:'calm: the wind below this speed'},
          {n:'wind_bins',t:1,u:'m/s',v:[2,4,6,8],say:'the wind rose\'s speed bins above calm'},
          {n:'comfort_t0',v:20,u:'C',say:'the comfort band\'s lowest temperature',lt:'comfort_t1'},{n:'comfort_t1',v:27,u:'C',say:'the comfort band\'s highest temperature',gt:'comfort_t0'},
          {n:'comfort_rh0',v:20,u:'%',say:'the comfort band\'s lowest humidity',lt:'comfort_rh1'},{n:'comfort_rh1',v:80,u:'%',say:'the comfort band\'s highest humidity',gt:'comfort_rh0'}]}]},
    /* ---- __acad3dV172b: comfort and design days, for Ladybug's analyses ---- */
    {id:'utci',title:'Universal Thermal Climate Index (UTCI): its stress scale and range',pub:'ISB Commission 6 and COST Action 730',kind:'method',area:'Climate',use:'Ladybug\'s outdoor comfort (UTCI): its figure and its row in Analyze',anywhere:true,
      eds:[{id:'utci.a002',name:'UTCI_a002 (Br\u00f6de, October 2009), its ten stress categories',pub:'2009-10',st:'current',where:'International',adopt:[{at:'*',from:'2009'}],
        src:{t:'utci.org: the UTCI program code (UTCI_a002, its ReadMe and Fortran) and the poster Calculating UTCI Equivalent Temperatures (2009)',w:'the ReadMe\'s range of validity; the poster\'s assessment scale',u:'https://www.utci.org/',lv:'P',read:'2026-10-31'},
        v:[{n:'bands',t:1,u:'C',v:[-40,-27,-13,0,9,26,32,38,46],say:'the bounds of the ten stress categories, from extreme cold stress below the first to extreme heat stress above the last'},
          {n:'ta_lo',v:-50,u:'C',say:'the coldest air in the formula\'s range',lt:'ta_hi'},{n:'ta_hi',v:50,u:'C',say:'the warmest air in its range',gt:'ta_lo'},
          {n:'dtr_lo',v:-30,u:'C',say:'the radiant temperature, at most this far below the air\'s',lt:'dtr_hi'},{n:'dtr_hi',v:70,u:'C',say:'the radiant temperature, at most this far above the air\'s',gt:'dtr_lo'},
          {n:'va_lo',v:0.5,u:'m/s',say:'the lowest wind at 10 m in its range: still air is taken as this',lt:'va_hi'},{n:'va_hi',v:17,u:'m/s',say:'the strongest wind at 10 m in its range',gt:'va_lo'},
          {n:'pa_hi',v:50,u:'hPa',say:'the most water vapour pressure in its range'}]}]},
    {id:'ashrae.55',title:'Thermal environmental conditions for human occupancy: PMV comfort',pub:'ASHRAE',kind:'standard',area:'Climate',use:'Ladybug\'s psychrometric chart: its comfort zone',anywhere:true,
      eds:[{id:'ashrae.55.2023',name:'ANSI/ASHRAE Standard 55-2023',pub:'2023',st:'current',where:'International practice',adopt:[{at:'*',from:'2023'}],
        src:{t:'ASHRAE 55-2023 (sold, and its publisher refuses scripts), as Ladybug\'s PMVParameter and pythermalcomfort 4.8.0 apply it',w:'the PMV method: PMV within plus or minus 0.5, at most 10% dissatisfied; the cooling effect of moving air above still air',u:'https://github.com/ladybug-tools/ladybug-comfort',lv:'S',read:'2026-10-31'},
        v:[{n:'ppd',v:10,u:'%',say:'the most people dissatisfied in the comfort zone (PMV within plus or minus 0.5)'},
          {n:'still',v:0.1,u:'m/s',say:'still air: at or below it the air\'s speed cools no one'}]}]},
    {id:'app.comfort',title:'Comfort assumptions',pub:'This app',kind:'assumption',area:'Climate',use:'Ladybug\'s psychrometric chart and its passive strategies, and UTCI in the sun',anywhere:true,
      eds:[{id:'app.comfort.1',name:'The app\'s comfort assumptions (V172b): Ladybug\'s own defaults',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app (the owner\'s choices of 2026-10-31), taking the defaults of Ladybug Tools\' LB PMV Polygon, LB Passive Strategy Parameters and LB Outdoor Solar MRT',w:'research-ladybug-weather-comfort.md, sections 4 and 10',u:'https://github.com/ladybug-tools/ladybug-grasshopper',lv:'A'},
        v:[{n:'clo',t:1,u:'clo',v:[0.5,1.0],say:'the clothing whose comfort zones are merged: summer and winter'},
          {n:'met',v:1.1,u:'met',say:'the activity: seated, light office work'},
          {n:'day_above',v:12,u:'C',say:'mass and night ventilation: the warmest day above the comfort zone it can still cool'},
          {n:'night_below',v:3,u:'C',say:'mass and night ventilation: how far below the comfort zone\'s warmest the night must fall'},
          {n:'fan',v:1,u:'m/s',say:'occupant fans: the air speed they make'},
          {n:'balance',v:12.8,u:'C',say:'capture internal heat: the building\'s balance temperature'},
          {n:'solar_cap',v:50,u:'W/m2',say:'passive solar heating: the sun on the window that warms the building by one degree'},
          {n:'time_const',v:8,u:'h',say:'the hours a building holds its coolness, or its sun\'s heat'},
          {n:'body_exp',v:1,u:'ratio',say:'UTCI in the sun: the share of the body in the sun'},
          {n:'sky_exp',v:1,u:'ratio',say:'UTCI in the sun: the share of the sky in view'},
          {n:'ground_ref',v:0.25,u:'ratio',say:'UTCI in the sun: the ground\'s reflectance'}]}]},
    {id:'ashrae.dd',title:'Climatic design conditions',pub:'ASHRAE',kind:'data',area:'Climate',use:'Ladybug\'s design days',anywhere:true,
      eds:[{id:'ashrae.dd.2025',name:'ASHRAE Handbook -- Fundamentals 2025, chapter 14',pub:'2025',st:'current',where:'International',adopt:[{at:'*',from:'2025'}],
        src:{t:'ASHRAE Handbook -- Fundamentals 2025, chapter 14, Climatic Design Information (sold): the values a station\'s DDY and EPW carry, as Ladybug reads them',w:'the design days: heating at 99.6% and 99% of the year\'s hours, cooling at 0.4%, 1% and 2%',u:'https://www.ashrae.org/',lv:'S',read:'2026-10-31'},
        v:[{n:'heating',t:1,u:'%',v:[99.6,99],say:'the heating design conditions: the share of the year\'s hours warmer than each'},
          {n:'cooling',t:1,u:'%',v:[0.4,1,2],say:'the cooling design conditions: the share of the year\'s hours warmer than each'}]}]},
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
      eds:[{id:'penndot.dm2.unread',name:'Its current change was not read: PennDOT\'s publications host did not answer from here',pub:'',st:'current',where:'Pennsylvania',adopt:[],
        src:{t:'Pennsylvania Department of Transportation',w:'not read: a search summary names Change No. 11 (March 2024), which is not a source',u:'https://www.dot.state.pa.us/public/pubsforms/Publications/PUB%2013M/Pub%2013M%20Title%20Page.pdf',lv:'U',read:'2026-10-18'},v:[]}]},
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
    'per sq mi':[' per sq mi',' per sq mi'],dB:[' dB',' dB'],ha:[' ha',' ha'],trees:[' tree',' trees'],families:[' family',' families'],C:['\u00b0C','\u00b0C'],'m/s':[' m/s',' m/s'],lanes:[' lane',' lanes'],days:[' day',' days'],x:['\u00d7','\u00d7'],'sq ft':[' sq ft',' sq ft'],
    s:[' s',' s'],'m/s2':[' m/s\u00b2',' m/s\u00b2'],'pc/h/ln':[' an hour a lane',' an hour a lane'],'du/acre':[' an acre',' an acre'],deg:['\u00b0','\u00b0'],ratio:['',''],h:[' h',' h'],hPa:[' hPa',' hPa'],'W/m2':[' W/m\u00b2',' W/m\u00b2'],clo:[' clo',' clo'],met:[' met',' met']};   /* __acad3dV172b */   /* __acad3dV172: a ratio, hours */   /* __acad3dV171 */
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
      if(best)r={ed:best.e,how:rec.kind==='assumption'&&!best.e.pack?'assumption':(path[i].k==='*'?'international':'adopted'),at:path[i],a:best.a};   /* __acad3dV167g: a pack's edition is adopted */
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
  /* a topic, or one value of it ('leed.nd|radius'); bare: as the editions have them, no override */
  function bimStdStamp(ts,bare){
    var L=[],O=bare?{}:(bimStdS().ov||{});
    (ts||[]).forEach(function(t0){
      var j=String(t0).indexOf('|'),t=j<0?t0:t0.slice(0,j),n=j<0?null:t0.slice(j+1),r=bimStdResolve(t),e=r&&r.ed,ov={},k;
      for(k in O)if(O.hasOwnProperty(k)&&k.indexOf(t+'|')===0&&O[k]&&typeof O[k].v==='number'&&(n===null||k===t+'|'+n))ov[k.slice(t.length+1)]=O[k].v;
      L.push({t:t0,e:e?e.id:null,how:r?r.how:'none',ov:ov,h:bimHash(bimCanon({e:e?e.id:null,v:e?(n===null?e.v:bimStdVal(e,n)):null,ov:ov}))});
    });
    return {at:bimSaToday(),list:L};
  }
  /* what a result kept, or for one from before V167 the editions' own values */
  function bimStdDataStamp(st,ts){return st&&Array.isArray(st.list)?st:bimStdStamp(ts,true);}
  function bimStdTopicOf(t){t=String(t);var j=t.indexOf('|');return j<0?t:t.slice(0,j);}
  /* the value of the edition in force, an override set aside */
  function bimStdOwn(t,n){var r=bimStdResolve(t),x=r&&r.ed?bimStdVal(r.ed,n):null;return x?x.v:undefined;}
  /* the topics whose edition, values or overrides are not what the result used */
  function bimStdChanged(st){
    if(!st||!Array.isArray(st.list))return [];
    var now=bimStdStamp(st.list.map(function(x){return x.t;})),out=[];
    st.list.forEach(function(x,i){var y=now.list[i];if(y&&y.h!==x.h)out.push({t:x.t,was:x,now:y});});
    return out;
  }
  function bimStdChangedText(ch){
    return ch.map(function(c){
      var R=bimStdRec(bimStdTopicOf(c.t)),nm=R?R.title:c.t,bits=[];
      if(c.was.e!==c.now.e)bits.push('the edition is now '+(c.now.e||'none'));
      var ks={},k;
      for(k in c.was.ov)ks[k]=1;for(k in c.now.ov)ks[k]=1;
      for(k in ks)if(c.was.ov[k]!==c.now.ov[k])bits.push(k+(c.now.ov.hasOwnProperty(k)?' overridden':' back to the standard'));
      if(!bits.length)bits.push('its values have changed');
      return nm+': '+bits.join(', ');
    }).join('; ');
  }
  /* ---- the project's overrides, each with its reason ---- */
  /* the findings made from the data are worked out again with the standards as they are now: no fetch,
     the data's own values where it was worked out with them, and said Out of date where it was */
  function bimStdRefill(){
    var s=A3D.site&&A3D.site.analysis,A,by={},n=0;
    if(!s||!Array.isArray(s.findings)||!s.findings.some(function(x){return x&&x.auto;}))return 0;
    A=bimSaAuto();A.forEach(function(a){by[a.auto]=a;});
    s.findings.forEach(function(f){var a=f&&f.auto&&by[f.auto];if(!a)return;
      if(f.value!==a.value||f.title!==a.title)n++;
      f.title=a.title;f.value=a.value;f.source=a.source;f.date=a.date;f.cls=bimSaPair(BIM_SA_CLS,a.cls)?a.cls:'neutral';f.sev=a.sev||1;});
    if(typeof bimSaRefresh==='function')bimSaRefresh(true);
    return n;
  }
  function bimStdDone(){
    try{bimStdRefill();}catch(e0){console.warn('[BIM] The findings could not be worked out again after a standards change',e0);}
    try{if(typeof bimEntRefit==='function')bimEntRefit();}catch(e3){console.warn('[BIM] The assets could not be built again after a standards change',e3);a3dToast('The assets could not be resized to the standards - see the console');}
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
    if(x.gt&&!(num>bimStd(t,x.gt))){a3dToast((x.say||n)+' must be more than '+bimStdFmt(bimStd(t,x.gt),x.u)+' ('+x.gt+')');return false;}
    if(x.lt&&!(num<bimStd(t,x.lt))){a3dToast((x.say||n)+' must be less than '+bimStdFmt(bimStd(t,x.lt),x.u)+' ('+x.lt+')');return false;}
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
    var t0=String(text==null?'':text),S=bimStdS(),sh=t0.length<=BIM_STD_PACK_MAX?bimSha256(t0):'';
    /* __acad3dV167g: the same file again is said as such, before its editions are found in the registry already */
    if(sh&&(S.packs||[]).some(function(p){return p.sha===sh;}))return {ok:false,err:'This pack is already applied to the project',sha:sh};
    var R=bimStdPackParse(text);
    if(R.err)return {ok:false,err:R.err};
    var ts=R.pack.topics.map(function(t){return t.id;}),was={},now={},i;
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
  /* __acad3dV167: the values the analyses read, from the registry, in the shapes their code had */
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
  /* __acad3dV167: the standards each analysis drawn in the model uses, and the data it is drawn from */
  var BIM_DG_STD={traffic:['idm.car','mobil','stm.signal','mutcd.signal','mutcd.walk','fdot.k','nchrp255','sd.trips','hm.walk','sumo.rules','app.traffic','fhwa.fc','app.roads','aashto.vehicles'],   /* __acad3dV171 */
    frame:['walk.speed'],noise:['fhwa.fc','app.roads','crtn','who.noise'],slope:['land.slope'],flood:['fema.zones'],streets:['fhwa.fc','app.roads'],
    cycling:['lts.2012','lts.xing2016','app.roads'],transit:['tfl.ptal'],needs:['guides.walk'],
    landuse:['lbcs.activity','app.land'],figure:['spacematrix','app.land','app.context'],green:['green.33300','app.land'],zoning:['app.land']};   /* __acad3dV168 */
  var BIM_DG_STD_DATA={traffic:'access',transit:'access',walk:'access',needs:'access',views:'context',noise:'context',wind:'climate',landuse:'context',figure:'context',green:'context'};
  /* the data fetched once and drawn from many times: the standards each is worked out with, the topics a
     row names for it, and its stamp */
  var BIM_STD_DATA={
    access:{ts:['walk.speed','leed.nd|radius'],say:['walk.speed'],name:'the access data',of:function(){var S=A3D.site&&A3D.site.access;return S?{st:S.std}:null;}},
    context:{ts:['app.context'],say:['app.context'],name:'the site context',of:function(){var c=A3D.site&&A3D.site.context&&A3D.site.context.last;return c?{st:c.std}:null;}},
    climate:{ts:['app.climate'],say:['app.climate'],name:'the climate data',of:function(){var C=A3D.site&&A3D.site.climate;return C&&(C.normals||C.hourly)?{st:C.std}:null;}},
    air:{ts:['who.aqg|pm25_24h','who.aqg|pm25_year','who.aqg|pm25_it1_year'],say:['who.aqg'],name:'the air quality data',of:function(){var Q=A3D.site&&A3D.site.risk&&A3D.site.risk.air;return Q?{st:Q.std}:null;}}};
  /* the standards a kind of data was worked out with that are not what they are now; only, the topics that matter */
  function bimStdDataChanged(kind,only){
    var K=BIM_STD_DATA[kind],d=K&&K.of(),ch;
    if(!d)return [];
    ch=bimStdChanged(bimStdDataStamp(d.st,K.ts));
    return only?ch.filter(function(c){return only.indexOf(bimStdTopicOf(c.t))>=0;}):ch;
  }
  /* and each finding */
  var BIM_SA_STD={'access.cycling':['lts.2012','lts.xing2016','app.roads'],'access.transit':['tfl.ptal','walk.speed'],'access.walk':['walk.speed'],
    'access.connectivity':['leed.nd'],'people.daily':['walk.speed'],'climate.comfort':['app.climate'],'climate.degreedays':['app.climate'],
    'climate.wind':['app.climate'],'risk.air':['who.aqg'],'landform.slope':['land.slope'],'landform.terrain':['land.slope'],'water.fema':['fema.zones'],'location.built':['app.context'],
    'location.landuse':['lbcs.activity','app.land'],'location.density':['spacematrix','app.land','app.context'],'ecology.33300':['green.33300','app.land'],'legal.zoningaround':['app.land']};   /* __acad3dV168 */
  /* what changed in the standards an analysis used: its own run's, and the data it is drawn from */
  function bimDgStdChanged(a){
    var R=bimDgState().runs[a],k=BIM_DG_STD_DATA[a]||null,out={run:[],data:[],kind:k};
    if(!R)return out;
    out.run=bimStdChanged(bimStdDataStamp(R.std,BIM_DG_STD[a]||[]));
    if(k)out.data=bimStdDataChanged(k,BIM_STD_DATA[k].say);
    return out;
  }
  function bimDgStdText(a){
    var k=BIM_DG_STD_DATA[a],T=(BIM_DG_STD[a]||[]).slice();
    if(k)BIM_STD_DATA[k].say.forEach(function(t){if(T.indexOf(t)<0)T.push(t);});
    return T.length?'Standards: '+T.map(bimStdUsedText).join('; '):'';
  }
  /* the data each finding is worked out from */
  var BIM_SA_STD_DATA={'access.transit':'access','access.walk':'access','access.connectivity':'access','people.daily':'access','climate.comfort':'climate',
    'climate.degreedays':'climate','climate.wind':'climate','risk.air':'air','location.built':'context','location.landuse':'context','location.density':'context','ecology.33300':'context'};
  function bimSaStdText(f){
    var T=f&&BIM_SA_STD[f.auto],k=f&&BIM_SA_STD_DATA[f.auto],s,ch;
    if(!T)return '';
    s='Standards: '+T.map(bimStdUsedText).join('; ');
    ch=k?bimStdDataChanged(k,T):[];
    if(ch.length)s+='. Out of date: '+bimStdChangedText(ch)+' since '+BIM_STD_DATA[k].name+' was fetched: Analyze site again';
    return s;
  }
  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};
  var BIM_DG_AN=[
    {id:'frame',name:'Compass and distance',col:'#c9d3dd'},
    {id:'sun',name:'Sun paths',col:'#ffb347'},
    {id:'shadow',name:'Shadows',col:'#7c8db0'},
    {id:'wind',name:'Winds',col:'#7fd3e6'},
    {id:'views',name:'Views',col:'#8fd694'},
    {id:'noise',name:'Noise',col:'#f08a24'},
    /* __acad3dV165: land and water; slope and aspect cover the ground, so they start hidden */
    {id:'contours',name:'Contours',col:'#b98a4e'},
    {id:'slope',name:'Slope',col:'#fd8d3c',hidden:true},
    {id:'aspect',name:'Aspect',col:'#fc8d59',hidden:true},
    {id:'flow',name:'Water flow',col:'#3b8fd9'},
    {id:'ponds',name:'Ponds',col:'#3f7fcf'},
    {id:'flood',name:'Flood zones',col:'#3d85d8'},
    /* __acad3dV166: movement; cycling and walk times colour the streets the hierarchy does, so they start hidden */
    {id:'streets',name:'Street hierarchy',col:'#e99d4c'},
    {id:'cycling',name:'Cycling stress',col:'#3987e5',hidden:true},
    {id:'transit',name:'Transit',col:'#d95926'},
    {id:'walk',name:'Walk times',col:'#5598e7',hidden:true},
    {id:'needs',name:'Daily needs',col:'#199e70'},
    {id:'vehicles',name:'Vehicle access',col:'#aab3be'},
    {id:'traffic',name:'Traffic and people',col:'#ffb454',hidden:true},   /* __acad3dV171: the simulation's results */
    /* __acad3dV168: land; land use, the figure-ground and the zoning cover the ground, so they start hidden */
    {id:'landuse',name:'Land use',col:'#eda100',hidden:true},
    {id:'figure',name:'Figure-ground',col:'#6b7280',hidden:true},
    {id:'green',name:'Green and trees',col:'#3fae5f'},
    {id:'zoning',name:'Zoning around',col:'#e0b85e',hidden:true}];
  function bimDgAn(id){var i;for(i=0;i<BIM_DG_AN.length;i++)if(BIM_DG_AN[i].id===id)return BIM_DG_AN[i];return null;}
  function bimIsDiag(o){return !!(o&&o.t==='diag'&&o.dg&&o.dg.g);}
  function bimDgState(){
    A3D.site=A3D.site||{};
    var D=A3D.site.diag;
    if(!D||typeof D!=='object')D=A3D.site.diag={};
    if(!D.runs||typeof D.runs!=='object')D.runs={};
    if(!D.layers||typeof D.layers!=='object')D.layers={};
    return D;
  }
  function bimDgCore(dg){return JSON.stringify({g:dg.g,s:dg.s||{},lb:dg.lb||[],sym:dg.sym||null});}
  /* changed by the owner: moved, or not as the analysis drew it */
  function bimDgEdited(o){
    var q=o.pos||[0,0,0];
    return !!(q[0]||q[1]||q[2])||!o.dg.gen||bimDgCore(o.dg)!==o.dg.gen;
  }
  function bimDgW(o,p){var q=bimObjOffset(o);return [p[0]+q[0],(p[1]||0)+q[1],p[2]+q[2]];}
  function bimDgDiags(a){return A3D.objs.filter(function(x){return bimIsDiag(x)&&(!a||x.dg.a===a);});}
