var A3D={objs:[],levels:[{id:'lvl-0',name:'Level 0'},{id:'lvl-1',name:'Level 1'}]};
var el={};
function a3dToast(){}
  function bimWallLength(centerline,closed){
    if(!centerline||centerline.length<2)return 0;
    var len=0,n=centerline.length,i;
    var segCount=closed?n:n-1;
    for(i=0;i<segCount;i++){
      var a=centerline[i],b=centerline[(i+1)%n];
      var dx=b[0]-a[0],dz=b[1]-a[1];
      len+=Math.sqrt(dx*dx+dz*dz);
    }
    return len;
  }

  function bimLevelName(levelId){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId)return A3D.levels[i].name;
    return '-';
  }

  function bimBuildRoomSchedule(){
    return A3D.objs.filter(function(o){return o.t==='room';}).map(function(o){
      return {name:o.name,area:o.area,level:bimLevelName(o.levelId),source:o.sourceType||'-'};
    });
  }

  function bimBuildDoorSchedule(){
    return A3D.objs.filter(function(o){return o.t==='opening'&&o.bim&&o.bim.type==='door';}).map(function(o){
      var host=objById(o.bim.hostWallId);
      return {name:o.name,width:o.bim.width,height:o.bim.height,hostWall:host?host.name:'(host wall missing)'};
    });
  }

  function bimBuildWindowSchedule(){
    return A3D.objs.filter(function(o){return o.t==='opening'&&o.bim&&o.bim.type==='window';}).map(function(o){
      var host=objById(o.bim.hostWallId);
      return {name:o.name,width:o.bim.width,height:o.bim.height,sillHeight:o.bim.sillHeight,hostWall:host?host.name:'(host wall missing)'};
    });
  }

  function bimBuildWallSchedule(){
    return A3D.objs.filter(function(o){return o.t==='solid'&&o.bim&&o.bim.type==='wall';}).map(function(o){
      var hasCenterline=!!(o.bim.centerline);
      var length=hasCenterline?bimWallLength(o.bim.centerline,o.bim.closed):null;
      return {
        name:o.name,
        length:length,
        thickness:hasCenterline?o.bim.thickness:null,
        height:hasCenterline?o.bim.height:null,
        area:(length!==null&&o.bim.height)?length*o.bim.height:null,
        level:bimLevelName(o.bim.levelId),
        imported:!!o.bim.imported
      };
    });
  }

  function bimBuildColumnSchedule(){
    return A3D.objs.filter(function(o){return o.t==='solid'&&o.bim&&o.bim.type==='column';}).map(function(o){
      return {name:o.name,width:o.bim.width,depth:o.bim.depth,height:o.bim.height,level:bimLevelName(o.bim.levelId)};
    });
  }

  function bimFmtScheduleValue(v,fmt){
    if(v===null||v===undefined)return '\u2014';
    if(fmt&&typeof v==='number')return v.toFixed(fmt);
    return String(v);
  }

  function bimScheduleToCSV(rows,columns){
    function esc(v){
      if(v===null||v===undefined)return '';
      var s=String(v);
      if(s.indexOf(',')>=0||s.indexOf('"')>=0||s.indexOf('\n')>=0)return '"'+s.replace(/"/g,'""')+'"';
      return s;
    }
    var lines=[columns.map(function(c){return esc(c.label);}).join(',')],i;
    for(i=0;i<rows.length;i++)lines.push(columns.map(function(c){return esc(rows[i][c.key]);}).join(','));
    return lines.join('\r\n');
  }

  function refreshSchedule(){
    if(!el.schedbody)return;
    var cat=el.schedcat?el.schedcat.value:'room';
    var def=SCHEDULE_DEFS[cat];
    if(!def){el.schedbody.innerHTML='';return;}
    var rows=def.build();
    if(!rows.length){el.schedbody.innerHTML='<div class="a3d-propnote">No '+def.label.toLowerCase()+' in the model yet.</div>';return;}
    var h='<table class="a3d-schedtbl"><thead><tr>';
    var i,j;
    for(j=0;j<def.cols.length;j++)h+='<th>'+def.cols[j].label+'</th>';
    h+='</tr></thead><tbody>';
    for(i=0;i<rows.length;i++){
      h+='<tr>';
      for(j=0;j<def.cols.length;j++)h+='<td>'+bimFmtScheduleValue(rows[i][def.cols[j].key],def.cols[j].fmt)+'</td>';
      h+='</tr>';
    }
    h+='</tbody></table><div class="a3d-propnote">'+rows.length+' '+def.label.toLowerCase()+'</div>';
    el.schedbody.innerHTML=h;
  }

  function bimExportScheduleCSV(){
    var cat=el.schedcat?el.schedcat.value:'room';
    var def=SCHEDULE_DEFS[cat];
    if(!def)return;
    var rows=def.build();
    if(!rows.length){a3dToast('No '+def.label.toLowerCase()+' to export');return;}
    var csv=bimScheduleToCSV(rows,def.cols);
    bimTriggerDownload(csv,def.label.toLowerCase()+'_schedule.csv','text/csv');
    a3dToast('Exported '+def.label.toLowerCase()+'_schedule.csv ('+rows.length+' rows)');
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

  function bimTriggerDownload(bytes,filename,mime){
    var blob=new Blob([bytes],{type:mime});
    var url=URL.createObjectURL(blob);
    var a=document.createElement('a');
    a.href=url;a.download=filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function(){URL.revokeObjectURL(url);},1000);
  }

  var SCHEDULE_DEFS={
    room:{label:'Rooms',build:bimBuildRoomSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'area',label:'Area (m\u00b2)',fmt:2},{key:'source',label:'Source'}]},
    door:{label:'Doors',build:bimBuildDoorSchedule,cols:[{key:'name',label:'Name'},{key:'hostWall',label:'Host Wall'},{key:'width',label:'Width (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2}]},
    window:{label:'Windows',build:bimBuildWindowSchedule,cols:[{key:'name',label:'Name'},{key:'hostWall',label:'Host Wall'},{key:'width',label:'Width (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2},{key:'sillHeight',label:'Sill (m)',fmt:2}]},
    wall:{label:'Walls',build:bimBuildWallSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'length',label:'Length (m)',fmt:2},{key:'thickness',label:'Thickness (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2},{key:'area',label:'Area (m\u00b2)',fmt:2}]},
    column:{label:'Columns',build:bimBuildColumnSchedule,cols:[{key:'name',label:'Name'},{key:'level',label:'Level'},{key:'width',label:'Width (m)',fmt:2},{key:'depth',label:'Depth (m)',fmt:2},{key:'height',label:'Height (m)',fmt:2}]}
  };

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- Build a realistic mixed model and verify every schedule against the REAL embedded code ----
A3D.objs=[
  {id:'wall1',t:'solid',name:'Wall_1',bim:{type:'wall',centerline:[[0,0],[6,0],[6,4],[0,4]],closed:true,thickness:0.3,height:3,levelId:'lvl-0'}},
  {id:'wall2',t:'solid',name:'IFCWall_1',bim:{type:'wall',imported:true}},
  {id:'room1',t:'room',name:'Room_1',area:20.79,levelId:'lvl-0',sourceType:'wall'},
  {id:'door1',t:'opening',name:'Door_1',bim:{type:'door',hostWallId:'wall1',width:0.9,height:2.1}},
  {id:'win1',t:'opening',name:'Window_1',bim:{type:'window',hostWallId:'wall1',width:1.2,height:1.0,sillHeight:0.9}},
  {id:'col1',t:'solid',name:'Column_1',bim:{type:'column',width:0.4,depth:0.4,height:3,levelId:'lvl-0'}}
];

var roomSched=SCHEDULE_DEFS.room.build();
assert('real embedded room schedule finds the room', roomSched.length===1);
assert('real embedded room schedule resolves level name', roomSched[0].level==='Level 0');
assert('real embedded room schedule preserves exact area', roomSched[0].area===20.79);

var doorSched=SCHEDULE_DEFS.door.build();
assert('real embedded door schedule finds the door and resolves its host wall via objById', doorSched.length===1&&doorSched[0].hostWall==='Wall_1');

var winSched=SCHEDULE_DEFS.window.build();
assert('real embedded window schedule finds the window with sill height', winSched.length===1&&winSched[0].sillHeight===0.9);

var wallSched=SCHEDULE_DEFS.wall.build();
assert('real embedded wall schedule finds both walls (native + imported)', wallSched.length===2);
var nativeWall=wallSched.filter(function(w){return w.name==='Wall_1';})[0];
assert('real embedded wall schedule computes correct PERIMETER length for a closed wall (6+4+6+4=20)', approx(nativeWall.length,20), nativeWall.length);
assert('real embedded wall schedule computes correct area (perimeter x height)', approx(nativeWall.area,60));
var importedWall=wallSched.filter(function(w){return w.name==='IFCWall_1';})[0];
assert('imported wall without centerline shows null length via the real code, not a crash', importedWall.length===null);

var colSched=SCHEDULE_DEFS.column.build();
assert('real embedded column schedule finds the column', colSched.length===1&&colSched[0].width===0.4);

// ---- Verify refreshSchedule (the real UI-facing function) renders a table without crashing,
// and gracefully handles the "no elements yet" case ----
el.schedbody={innerHTML:''};
el.schedcat={value:'room'};
refreshSchedule();
assert('refreshSchedule (real function) populates the table body with real HTML', el.schedbody.innerHTML.indexOf('Room_1')>=0);
assert('rendered table includes the formatted area value', el.schedbody.innerHTML.indexOf('20.79')>=0);

el.schedcat={value:'door'};
refreshSchedule();
assert('switching category via the real function correctly re-renders for doors', el.schedbody.innerHTML.indexOf('Door_1')>=0 && el.schedbody.innerHTML.indexOf('Room_1')===-1);

A3D.objs=[];
el.schedcat={value:'room'};
refreshSchedule();
assert('empty model shows a graceful "no rooms" message rather than a broken/empty table', el.schedbody.innerHTML.indexOf('No rooms')>=0, el.schedbody.innerHTML);

// ---- CSV export via the real embedded pipeline ----
A3D.objs=[
  {id:'room1',t:'room',name:'Room_1',area:24.5,levelId:'lvl-0',sourceType:'wall'},
  {id:'room2',t:'room',name:'Room, "Special"',area:12,levelId:'lvl-1',sourceType:'sketch'}
];
var realCsv=bimScheduleToCSV(SCHEDULE_DEFS.room.build(),SCHEDULE_DEFS.room.cols);
assert('real CSV export header matches the schedule column labels', realCsv.split('\r\n')[0]==='Name,Level,Area (m\u00b2),Source');
assert('real CSV export correctly quotes a name containing a comma and quote', realCsv.indexOf('"Room, ""Special"""')>=0, realCsv);
assert('real CSV export includes both rooms', realCsv.split('\r\n').length===3);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
