#!/usr/bin/env python3
"""V171a: the standards the traffic simulation reads, as records of a new area, Traffic (research-traffic.md 1 to 4
and 7): the IDM's car, MOBIL, the FHWA signal timing manual, the MUTCD's intervals, Florida's K, NCHRP 255's
balancing, San Diego's trip rates, Helbing and Molnar's walking speeds, SUMO's junction and walker rules, and the
app's own traffic settings. The units they need; the area in its place.

Run from the repository root: python3 Phase/patch_phase171a.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('993d632ab2273093d57432af765193d86a03d9c63603b8d73214893fec189029')   # V170

REC = r"""    /* ---- __acad3dV171: traffic and people around the site (research-traffic.md) ---- */
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
        src:{t:'Eclipse SUMO\'s documentation: Simulation/Intersections, Networks/PlainXML (right of way), the junction model parameters, Simulation/Pedestrians (striping)',w:'a minor road keeps a time gap of at least 1 s to a priority car not yet in the junction (jmTimegapMinor); right of way to the two approaches ranked highest by priority, speed and lanes; on amber a car far away slows and one near goes; walkers in stripes of 0.65 m',u:'https://github.com/eclipse-sumo/sumo',lv:'S',read:'2026-10-24'},
        v:[{n:'gap',v:1,u:'s',say:'the time gap a minor road keeps to a priority car'},{n:'stripe',v:0.65,u:'m',say:'a walker\'s stripe across a sidewalk'}]}]},
    {id:'app.traffic',title:'The traffic simulation\'s own settings',pub:'This app',kind:'assumption',area:'Traffic',use:'Traffic and people: what no source gives',anywhere:true,
      eds:[{id:'app.traffic.1',name:'The app\'s traffic settings (V171)',pub:'',st:'current',where:'Anywhere',adopt:[{at:'*'}],
        src:{t:'This app: the reach of the simulation, a lane\'s width as the site context draws it, how near a signal is to its junction, the step, the warm-up and the tallies, the sidewalks\' and crossings\' places, the queue\'s and the crossings\' tests, a car\'s people, and the usages read as San Diego\'s uses',w:'research-traffic.md, section 8',lv:'A'},
        v:[{n:'radius',v:300,u:'m',say:'the streets simulated, from the lot'},{n:'lane_w',v:3.3,u:'m',say:'a lane\'s width'},
          {n:'sig_r',v:30,u:'m',say:'how near a mapped signal is to the junction it controls'},{n:'step',v:0.2,u:'s',say:'the simulation\'s step'},
          {n:'warm',v:300,u:'s',say:'the warm-up before the tallies start'},{n:'bin',v:10,u:'s',say:'the tallies\' bins'},
          {n:'sw_off',v:1.5,u:'m',say:'a sidewalk\'s line beyond the roadway\'s edge'},{n:'cw',v:2,u:'m',say:'a crossing behind the corner'},
          {n:'y_max',v:0.95,u:'',say:'the junction\'s demand over its capacity at which the cycle is the longest'},
          {n:'walk_gap',v:2,u:'s',say:'the time a car must be away for a walker to cross where no signal is'},
          {n:'queue_v',v:2,u:'m/s',say:'a car slower than this is standing in a queue'},{n:'queue_r',v:100,u:'m',say:'the street before the lot\'s entry counted for its queue'},
          {n:'occ',v:1,u:'',say:'the people a car brings'},
          {n:'uses',t:1,v:{'use-res':'mdu','use-off':'office','use-ret':'retail','use-hot':'hotel'},say:'the usages read as San Diego\'s uses: Residential as multiple dwelling units, Office as commercial office, Retail as strip commercial, Hotel as hotel'}]}]},
"""
rep('js/engine/standards/registry.js', "    {id:'app.climate',title:'Climate readings',", REC + "    {id:'app.climate',title:'Climate readings',")
rep('js/engine/standards/registry.js', "x:['\\u00d7','\\u00d7'],'sq ft':[' sq ft',' sq ft']};",
    "x:['\\u00d7','\\u00d7'],'sq ft':[' sq ft',' sq ft'],\n    s:[' s',' s'],'m/s2':[' m/s\\u00b2',' m/s\\u00b2'],'pc/h/ln':[' an hour a lane',' an hour a lane'],'du/acre':[' an acre',' an acre']};   /* __acad3dV171 */")
rep('js/engine/properties/site-standards.js', "'Land and green','Assets','Climate'];", "'Land and green','Assets','Traffic','Climate'];")
rep('js/engine/properties/site-standards.js', "/* __acad3dV168: Land and green; __acad3", "/* __acad3dV171: Traffic; __acad3dV168: Land and green; __acad3")
done()
