#!/usr/bin/env python3
"""patch_phase105a.py -- V105 occupant load. IBC Table 1004.5 defaults kept as published (sq ft per
occupant, gross or net) with the m2 value derived; a room Load Factor the owner sets; the room
schedule gains factor, basis, source and occupant load. Room copy derives its fields from
BIM_ROOM_FIELDS: the V101 hand list had dropped Comments and would have dropped Load Factor."""
NAME = 'patch_phase105a.py'
BASE = '425072d54c06b93680f1013bea9729261310efec02bbc9af98f43cb53e2d55c0'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)
rep(r"""    {k:'occupancy',label:'Occupancy',grp:'id'},
""", r"""    {k:'occupancy',label:'Occupancy',grp:'id'},
    {k:'loadFactor',label:'Load Factor (m²/person)',grp:'id'},   /* __acad3dV105: blank = the IBC default for the Occupancy */
""")
rep(r"""    {k:'comments',label:'Comments',grp:'id'}
  ];
""", r"""    {k:'comments',label:'Comments',grp:'id'}
  ];
  /* __acad3dV105: a copied room takes every field above except its number, derived from the list
     rather than written out -- the V101 hand list had already dropped Comments. */
  function bimCopyRoomFields(src,dst){
    var i,k;
    for(i=0;i<BIM_ROOM_FIELDS.length;i++){k=BIM_ROOM_FIELDS[i].k;if(k!=='number'&&src[k]!==undefined)dst[k]=src[k];}
    return dst;
  }
  /* ================= __acad3dV105: occupant load =================
     Defaults from IBC Table 1004.5, "Maximum floor area allowances per occupant" (2018 and 2021
     editions), labelled as defaults wherever they show. The table publishes square feet per
     occupant and that is the number kept; the m2 figure is derived from it (1 sq ft =
     0.09290304 m2), never typed in beside it. Gross or net is the table's own. A room's own Load
     Factor overrides the default: the factor is the owner's to set. Rows the table sends
     elsewhere -- fixed seating (1004.6), concentrated business use (1004.8), malls (402.8.2),
     bowling lanes -- are not an area rate and are not here.
     A gross factor is applied to the ROOM's own area; a gross floor area plan is Phase 105b. */
  var BIM_OCC_LOADS=[
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
    ['Warehouses',500,'gross']
  ];
  var BIM_FT2_M2=0.09290304;
  function bimOccKey(s){return String(s==null?'':s).replace(/\s+/g,' ').replace(/^ | $/g,'').toLowerCase();}
  /* The table row a room's Occupancy names, case and spacing ignored. Any other text is the
     owner's own occupancy: it has no default, and the schedule says so by leaving it blank. */
  function bimOccLoadRow(occ){
    var k=bimOccKey(occ),i,r;
    if(!k)return null;
    for(i=0;i<BIM_OCC_LOADS.length;i++){
      r=BIM_OCC_LOADS[i];
      if(bimOccKey(r[0])===k)return {name:r[0],ft2:r[1],m2:r[1]*BIM_FT2_M2,basis:r[2]};
    }
    return null;
  }
  /* The factor a room is computed with, in m2 per person: its own Load Factor when the owner has
     set one, else the IBC default for its Occupancy, else none. */
  function bimRoomLoadFactor(o){
    if(!o||o.t!=='room')return null;
    var own=parseFloat(o.loadFactor),row=bimOccLoadRow(o.occupancy);
    if(isFinite(own)&&own>0)return {m2:own,basis:'',src:'Set'};
    if(row)return {m2:row.m2,basis:row.basis,src:'IBC 1004.5'};
    return null;
  }
  /* Occupant load = area / factor, rounded UP to a whole person -- the usual convention; the table
     gives the rate, not the rounding. The 1e-9 stops an exact multiple rounding up on floating-
     point noise: a 1.1 x 3 m room drawn at x = 60 measures 3.3000000000000114 m2, and at 1.1
     m2/person that is 3.00000000000001 -- 3 people, not 4. No factor, no load: null, shown blank, never 0,
     because 0 is a claim that the room holds nobody. */
  function bimRoomOccupants(o){
    var f=bimRoomLoadFactor(o);
    if(!f||!(o.area>0))return null;
    return Math.ceil(o.area/f.m2-1e-9);
  }
""")
rep(r"""        number:bimNextRoomNumber(o.levelId),dept:o.dept,occupancy:o.occupancy,finishFloor:o.finishFloor,
        finishWall:o.finishWall,finishCeiling:o.finishCeiling,finishBase:o.finishBase};   /* __acad3dV101 */
""", r"""        number:bimNextRoomNumber(o.levelId)};   /* __acad3dV101 */
      bimCopyRoomFields(o,copy);   /* __acad3dV105 */
""")
rep(r"""    return A3D.objs.filter(function(o){return o.t==='room';}).map(function(o){
      return {number:bimRoomField(o,'number'),""", r"""    return A3D.objs.filter(function(o){return o.t==='room';}).map(function(o){
      var lf=bimRoomLoadFactor(o),occ=bimRoomOccupants(o);   /* __acad3dV105 */
      return {number:bimRoomField(o,'number'),""")
rep(r"""dept:bimRoomField(o,'dept'),occupancy:bimRoomField(o,'occupancy'),
""", r"""dept:bimRoomField(o,'dept'),occupancy:bimRoomField(o,'occupancy'),
              loadFactor:lf?lf.m2:'',loadBasis:lf?lf.basis:'',loadSrc:lf?lf.src:'',occupants:occ===null?'':occ,
""")
rep(r"""{key:'occupancy',label:'Occupancy'},""", r"""{key:'occupancy',label:'Occupancy'},{key:'loadFactor',label:'Load Factor (m²/person)',fmt:2},{key:'loadBasis',label:'Basis'},{key:'loadSrc',label:'Factor Source'},{key:'occupants',label:'Occupant Load'},""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
