  /* ================= __acad3dV101: room data =================
     The fields a tag and a schedule read. They live on the room only. */
  var BIM_ROOM_FIELDS=[
    {k:'number',label:'Number',grp:'id'},
    {k:'dept',label:'Department',grp:'id'},
    {k:'occupancy',label:'Occupancy',grp:'id'},
    {k:'loadFactor',label:'Load Factor (m²/person)',grp:'id'},   /* __acad3dV105: blank = the IBC default for the Occupancy */
    {k:'finishFloor',label:'Floor Finish',grp:'fin'},
    {k:'finishWall',label:'Wall Finish',grp:'fin'},
    {k:'finishCeiling',label:'Ceiling Finish',grp:'fin'},
    {k:'finishBase',label:'Base Finish',grp:'fin'},
    {k:'comments',label:'Comments',grp:'id'}
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
  /* __acad3dV167: the table is the registry's (ibc.occupant_load), its edition the one in force for the site: bimOccLoads */
  var BIM_FT2_M2=0.09290304;
  function bimOccKey(s){return String(s==null?'':s).replace(/\s+/g,' ').replace(/^ | $/g,'').toLowerCase();}
  /* The table row a room's Occupancy names, case and spacing ignored. Any other text is the
     owner's own occupancy: it has no default, and the schedule says so by leaving it blank. */
  function bimOccLoadRow(occ){
    var k=bimOccKey(occ),i,r;
    if(!k)return null;
    for(i=0;i<bimOccLoads().length;i++){
      r=bimOccLoads()[i];
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
  /* __acad3dV105: the Properties side of occupant load. All of it reads the two functions the
     schedule reads, so the panel and the schedule cannot disagree. */
  function bimRoomLoadFactorHint(o){
    var row=bimOccLoadRow(o&&o.occupancy);
    return row?(row.m2.toFixed(2)+' IBC default ('+row.ft2+' sq ft '+row.basis+')'):'none: pick an IBC Occupancy or type a factor';
  }
  function bimRoomOccupantsText(o){
    var f=bimRoomLoadFactor(o),n=bimRoomOccupants(o);
    if(!f)return 'no load factor';
    return (n===null?'-':String(n))+' at '+f.m2.toFixed(2)+' m²/person'+(f.basis?' '+f.basis:'')+' ('+f.src+')';
  }
  function bimOccDatalist(){
    var h='<datalist id="bimOccList">',i;
    for(i=0;i<bimOccLoads().length;i++)h+='<option value="'+bimEsc(bimOccLoads()[i][0])+'">'+bimOccLoads()[i][1]+' sq ft '+bimOccLoads()[i][2]+'</option>';
    return h+'</datalist>';
  }
  function bimRoomField(o,k){return (o&&o[k]!==undefined&&o[k]!==null)?String(o[k]):'';}
