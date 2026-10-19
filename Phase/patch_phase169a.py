#!/usr/bin/env python3
"""V169a: assets -- the standards and the data.

- The registry (V167) takes ten topics in a new area, Assets, each from its source (research-assets.md):
  - body.us: the mean heights of US men, women and boys of 8 (NCHS, 2015-2018);
  - body.hidh: eye height and shoulder width from height, NASA's Human Integration Design Handbook,
    Appendix B (linear in stature between its smallest and largest);
  - wheel.awmp: manual chair users' size, the Anthropometry of Wheeled Mobility Project (2010);
  - ada.space: the 2010 ADA Standards' clear floor space and turning space;
  - mutcd.walk: the MUTCD's walking speeds at signals (11th Edition with Revision 1, 4I.06);
  - ltn.cycle: LTN 1/20's upright cycle and Sheffield stands;
  - parking.bay: Manual for Streets' bay and aisles (the owner: where no rule is recorded);
  - utd.trees: tree heights and crowns by type, the medians of the Urban Tree Database's measured trees;
  - etccdi.gsl: ETCCDI's growing season;
  - app.assets: the models' own shapes where no source sizes them.
- The climate (V159) keeps the site's growing season, ETCCDI's GSL year by year from the daily means,
  for when a deciduous tree is in leaf.

Run from the repository root: python3 Phase/patch_phase169a.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '57db924464fdb7604f679c7f3c2ce3c75a7bcd8e3d496c80bcefb4baee42639a'   # V168, main at 372c9dc

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


# ---- the registry: a new area, and its unit ----
rep("'Land and green','Climate'];   /* __acad3dV168: Land and green */",
    "'Land and green','Assets','Climate'];   /* __acad3dV168: Land and green; __acad3dV169: Assets */")
rep("lanes:[' lane',' lanes'],x:['",
    "lanes:[' lane',' lanes'],days:[' day',' days'],x:['")

# ---- the ten topics ----
RECS = r'''    /* __acad3dV169: the assets' sizes -- people, a wheelchair user, cycles and stands, parking, trees -- each from its source */
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
    {id:'app.assets',title:'The assets\' own shapes',pub:'This app',kind:'assumption',area:'Assets',use:'The models\' shapes where no source sizes them',anywhere:true,
      eds:[{id:'app.assets.1',name:'The app\'s asset settings (V169)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: the seat a seated person sits on, a cycle\'s height, a Sheffield stand\'s size, a bay\'s painted line, and the crown of a mapped tree whose leaf type is not mapped (the context\'s rule since V157)',w:'research-assets.md',lv:'A'},
        v:[{n:'seat',v:0.45,u:'m',say:'the seat a seated person sits on'},{n:'bike_h',v:1.05,u:'m',say:'a cycle\'s height to its handlebars'},
          {n:'stand_w',v:0.75,u:'m',say:'a Sheffield stand\'s length'},{n:'stand_h',v:0.75,u:'m',say:'a Sheffield stand\'s height'},{n:'line',v:0.1,u:'m',say:'a bay\'s painted line, across'},
          {n:'crown',v:0.6,u:'x',say:'a mapped tree\'s crown across, of its height, where its leaf type is not mapped'}]}]},
'''
rep("    {id:'app.climate',title:'Climate readings'", RECS + "    {id:'app.climate',title:'Climate readings'")

# ---- the growing season, with the climate ----
GSL = r'''  /* __acad3dV169: the thermal growing season, ETCCDI's GSL, year by year from the daily means: from the first span of
     days above the registry's mean to the first span below it after mid-year; the median start and end kept, in days
     from 1 January (1 July in the Southern Hemisphere), for when a deciduous tree is in leaf */
  function bimClimGsl(js,lat){
    var d=js&&js.daily,T=bimStd('etccdi.gsl','t'),N=bimStd('etccdi.gsl','days'),sh=lat<0,S={},i,k,y;
    if(!d||!Array.isArray(d.time)||typeof T!=='number'||!(N>=1))return null;
    for(i=0;i<d.time.length;i++){
      var m=/^(\d{4})-(\d{2})-(\d{2})/.exec(String(d.time[i]));if(!m)continue;
      var tm=(d.temperature_2m_mean||[])[i],tx=(d.temperature_2m_max||[])[i],tn=(d.temperature_2m_min||[])[i];
      if(!bimClimNum(tm)&&bimClimNum(tx)&&bimClimNum(tn))tm=(tx+tn)/2;
      var Y=+m[1],M=+m[2],sy=(sh&&M<7)?Y-1:Y,di=Math.round((Date.UTC(Y,M-1,+m[3])-Date.UTC(sy,sh?6:0,1))/864e5);
      (S[sy]=S[sy]||[])[di]=bimClimNum(tm)?tm:null;
    }
    var st=[],en=[],ys=0;
    for(y in S){
      if(!S.hasOwnProperty(y))continue;
      var a=S[y],y0=Date.UTC(+y,sh?6:0,1),len=Math.round((Date.UTC(+y+1,sh?6:0,1)-y0)/864e5),mid=Math.round((Date.UTC(sh?+y+1:+y,sh?0:6,1)-y0)/864e5),full=true,s0=-1,e0=len,run=0;
      for(k=0;k<len;k++)if(a[k]===undefined||a[k]===null){full=false;break;}
      if(!full)continue;
      ys++;
      for(k=0;k<len;k++){run=a[k]>T?run+1:0;if(run>=N){s0=k-N+1;break;}}
      if(s0<0){st.push(len);en.push(len);continue;}   /* no season that year */
      run=0;
      for(k=Math.max(mid,s0+N);k<len;k++){run=a[k]<T?run+1:0;if(run>=N){e0=k-N+1;break;}}
      st.push(s0);en.push(e0);
    }
    if(!ys)return null;
    function med(L){L=L.slice().sort(function(p,q){return p-q;});var n=L.length;return n%2?L[(n-1)/2]:Math.round((L[n/2-1]+L[n/2])/2);}
    return {s:med(st),e:med(en),years:ys,sh:sh,std:bimStdStamp(['etccdi.gsl'])};
  }
  /* the climate's daily means to its twelve months */
'''
rep("  /* ten years of days, to the twelve months' normals */\n  function bimClimDaily(js){",
    GSL.replace("  /* the climate's daily means to its twelve months */\n", "") + "  /* ten years of days, to the twelve months' normals */\n  function bimClimDaily(js){")
rep("        C.src='ERA5 reanalysis (ECMWF), via Open-Meteo';}",
    "        C.src='ERA5 reanalysis (ECMWF), via Open-Meteo';}\n"
    "      if(R[0].ok){var G0=bimClimGsl(R[0].js,lat);if(G0)C.gsl=G0;else delete C.gsl;}   /* __acad3dV169: the growing season, for the trees */")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
