"""patch_phase101.py -- __acad3dV101: rooms carry the data a room tag shows.

First phase of the room track (owner, V100: "throw the structural stuff in. room tagging? site
analysis?" -- all three, interleaved, rooms first).

A room had a name and an area. A room in a drawing set has a NUMBER, a name, a department, an
occupancy and its finishes, and every one of those is read by a tag and a schedule. This adds
the data, with one rule for each:

  * Number is assigned on creation, per level, the way offices number rooms: 101, 102 ... on the
    first level, 201 ... on the second. A duplicate number is allowed (renumbering passes go
    through duplicates) but it is SAID.
  * The fields live on the room and nowhere else. Tags and schedules read them live, so editing
    the room edits every tag at once and a tag can never disagree with its room.
  * Properties shows them in Identity Data and a Finishes group; the schedule gains the columns.
  * The plan label puts the number in front of the name, and is placed at a point INSIDE the
    room -- it was placed at the average of the vertices, which lies outside an L-shaped room.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = 'd53fb23231ebc1a5be35ad37b79727765d78519d2a46625e967dd3ceacbd20f4'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # --- numbering, and assignment on creation
    ("""  function bimCreateRoom(boundary){
    pushUndo();""",
     """  /* ================= __acad3dV101: room data =================
     The fields a tag and a schedule read. They live on the room only. */
  var BIM_ROOM_FIELDS=[
    {k:'number',label:'Number',grp:'id'},
    {k:'dept',label:'Department',grp:'id'},
    {k:'occupancy',label:'Occupancy',grp:'id'},
    {k:'finishFloor',label:'Floor Finish',grp:'fin'},
    {k:'finishWall',label:'Wall Finish',grp:'fin'},
    {k:'finishCeiling',label:'Ceiling Finish',grp:'fin'},
    {k:'finishBase',label:'Base Finish',grp:'fin'},
    {k:'comments',label:'Comments',grp:'id'}
  ];
  function bimRoomField(o,k){return (o&&o[k]!==undefined&&o[k]!==null)?String(o[k]):'';}
  /* 101, 102 ... on the first level, 201 ... on the second: the next free number in that
     level's hundred. Past 99 rooms on a level, one past the highest number anywhere. */
  function bimNextRoomNumber(levelId){
    var li=0,i,base,top=0,n,any=0;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId){li=i;break;}
    base=(li+1)*100;
    for(i=0;i<A3D.objs.length;i++){
      if(A3D.objs[i].t!=='room')continue;
      n=parseInt(A3D.objs[i].number,10);
      if(!isFinite(n))continue;
      if(n>any)any=n;
      if(n>base&&n<base+100&&n>top)top=n;
    }
    if(!top)return String(base+1);
    if(top<base+99)return String(top+1);
    return String(any+1);
  }
  /* Other rooms already using this number. */
  function bimRoomsWithNumber(num,exceptId){
    var out=[],i;
    if(!num)return out;
    for(i=0;i<A3D.objs.length;i++){
      var r=A3D.objs[i];
      if(r.t==='room'&&r.id!==exceptId&&String(r.number||'')===String(num))out.push(r);
    }
    return out;
  }
  /* Set one room field, with undo, and say when a number is already taken. */
  function bimSetRoomField(room,k,val){
    var f=null,i;
    for(i=0;i<BIM_ROOM_FIELDS.length;i++)if(BIM_ROOM_FIELDS[i].k===k)f=BIM_ROOM_FIELDS[i];
    if(!room||room.t!=='room'||!f){a3dToast('That room field does not exist');return false;}
    val=String(val===undefined||val===null?'':val).replace(/^\\s+|\\s+$/g,'').slice(0,80);
    if(bimRoomField(room,k)===val)return true;
    pushUndo();
    room[k]=val;
    if(k==='number'&&val){
      var dup=bimRoomsWithNumber(val,room.id);
      if(dup.length)a3dToast('Number '+val+' is also used by '+dup.map(function(r){return r.name;}).join(', '));
    }
    refreshTree();paint();saveSoon();
    return true;
  }
  function bimCreateRoom(boundary){
    pushUndo();"""),
    ("""    if(boundary.region)o.region=bimCloneRegion(boundary.region);   /* __acad3dV99 */
    A3D.objs.push(o);""",
     """    if(boundary.region)o.region=bimCloneRegion(boundary.region);   /* __acad3dV99 */
    o.number=bimNextRoomNumber(o.levelId);   /* __acad3dV101 */
    A3D.objs.push(o);"""),
    ("""    a3dToast(o.name+' created \\u2014 '+o.area.toFixed(2)+' m\\u00b2');
    return o;
  }
  function startRoomTool(){""",
     """    a3dToast(o.name+' ('+o.number+') created \\u2014 '+o.area.toFixed(2)+' m\\u00b2');
    return o;
  }
  function startRoomTool(){"""),

    # --- Properties
    ("""    h+=bimPropGroup('Identity Data',idd);""",
     """    var finRows='';   /* __acad3dV101: the room's own data, from the one field list */
    if(o.t==='room'){
      var rfi;
      for(rfi=0;rfi<BIM_ROOM_FIELDS.length;rfi++){
        var rf=BIM_ROOM_FIELDS[rfi];
        var rrow=bimPropRow(rf.label,'<input type="text" data-roomf="'+rf.k+'" value="'+bimEsc(bimRoomField(o,rf.k))+'">');
        if(rf.grp==='fin')finRows+=rrow;else idd+=rrow;
      }
    }
    h+=bimPropGroup('Identity Data',idd);
    if(finRows)h+=bimPropGroup('Finishes',finRows);"""),
    ("""    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      /* __acad3dV73: the no-selection model fields.""",
     """    /* __acad3dV101: room fields. A field shown on a TAG edits the tag's room. */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var ri=ev.target&&ev.target.closest?ev.target.closest('[data-roomf]'):null;
      if(!ri)return;
      var so=objById(A3D.sel),room=so&&so.t==='room'?so:(so&&so.roomId?objById(so.roomId):null);
      if(!room){a3dToast('That room no longer exists');refreshProps();return;}
      try{bimSetRoomField(room,ri.getAttribute('data-roomf'),ri.value);}
      catch(eRF){
        console.warn('[BIM] Room field edit failed',eRF);
        a3dToast('That room field could not be changed - see the console');
      }
      refreshProps();
    });
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      /* __acad3dV73: the no-selection model fields."""),
    # a renamed room is repainted: its label (and tags) read the name
    ("""      if(f==='name'){
        pushUndo();
        o.name=String(inp.value||'').slice(0,60)||o.name;
        refreshTree();saveSoon();""",
     """      if(f==='name'){
        pushUndo();
        o.name=String(inp.value||'').slice(0,60)||o.name;
        refreshTree();paint();saveSoon();   /* __acad3dV101: labels and tags read the name */"""),

    # --- schedule
    ("""      return {name:o.name,area:o.area,level:bimLevelName(o.levelId),source:o.sourceType||'-'};""",
     """      return {number:bimRoomField(o,'number'),name:o.name,area:o.area,level:bimLevelName(o.levelId),
              dept:bimRoomField(o,'dept'),occupancy:bimRoomField(o,'occupancy'),
              finishFloor:bimRoomField(o,'finishFloor'),finishWall:bimRoomField(o,'finishWall'),
              finishCeiling:bimRoomField(o,'finishCeiling'),source:o.sourceType||'-'};   /* __acad3dV101 */"""),
    ("""    room:{label:'Rooms',build:bimBuildRoomSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'area',label:'Area (m\\u00b2)',fmt:2},{key:'source',label:'Source'}]},""",
     """    room:{label:'Rooms',build:bimBuildRoomSchedule,cols:[{key:'number',label:'Number'},{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'area',label:'Area (m\\u00b2)',fmt:2},{key:'dept',label:'Department'},{key:'occupancy',label:'Occupancy'},{key:'finishFloor',label:'Floor'},{key:'finishWall',label:'Wall'},{key:'finishCeiling',label:'Ceiling'},{key:'source',label:'Source'}]},"""),

    # --- plan label: number, and a point inside the room
    ("""      var cp=toScreen([cx,y0,cz],V,W,H);
      var line1=o.name,line2=o.area.toFixed(2)+' m\\u00b2'+""",
     """      /* __acad3dV101: at a point INSIDE the room -- the vertex average lies outside an L */
      var inW=bimInteriorPoint(o.pts.map(function(p){return [p[0]+ox,p[1]+oz];}));
      if(inW){cx=inW[0];cz=inW[1];}
      var cp=toScreen([cx,y0,cz],V,W,H);
      var line1=(o.number?o.number+'  ':'')+o.name,line2=o.area.toFixed(2)+' m\\u00b2'+"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
