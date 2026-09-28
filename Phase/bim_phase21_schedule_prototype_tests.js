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
function bimLevelName(A3D,levelId){
  var i;
  for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===levelId)return A3D.levels[i].name;
  return '-';
}
function bimBuildRoomSchedule(A3D){
  return A3D.objs.filter(function(o){return o.t==='room';}).map(function(o){
    return {name:o.name,area:o.area,level:bimLevelName(A3D,o.levelId),source:o.sourceType||'-'};
  });
}
function bimBuildDoorSchedule(A3D){
  return A3D.objs.filter(function(o){return o.t==='opening'&&o.bim&&o.bim.type==='door';}).map(function(o){
    var host=A3D.objs.filter(function(x){return x.id===o.bim.hostWallId;})[0];
    return {name:o.name,width:o.bim.width,height:o.bim.height,hostWall:host?host.name:'(host wall missing)'};
  });
}
function bimBuildWindowSchedule(A3D){
  return A3D.objs.filter(function(o){return o.t==='opening'&&o.bim&&o.bim.type==='window';}).map(function(o){
    var host=A3D.objs.filter(function(x){return x.id===o.bim.hostWallId;})[0];
    return {name:o.name,width:o.bim.width,height:o.bim.height,sillHeight:o.bim.sillHeight,hostWall:host?host.name:'(host wall missing)'};
  });
}
function bimBuildWallSchedule(A3D){
  return A3D.objs.filter(function(o){return o.t==='solid'&&o.bim&&o.bim.type==='wall';}).map(function(o){
    var hasCenterline=!!(o.bim.centerline);
    var length=hasCenterline?bimWallLength(o.bim.centerline,o.bim.closed):null;
    return {
      name:o.name,
      length:length,
      thickness:hasCenterline?o.bim.thickness:null,
      height:hasCenterline?o.bim.height:null,
      area:(length!==null&&o.bim.height)?length*o.bim.height:null,
      level:bimLevelName(A3D,o.bim.levelId),
      imported:!!o.bim.imported
    };
  });
}
function bimBuildColumnSchedule(A3D){
  return A3D.objs.filter(function(o){return o.t==='solid'&&o.bim&&o.bim.type==='column';}).map(function(o){
    return {name:o.name,width:o.bim.width,depth:o.bim.depth,height:o.bim.height,level:bimLevelName(A3D,o.bim.levelId)};
  });
}
function bimScheduleToCSV(rows,columns){
  function esc(v){
    if(v===null||v===undefined)return '';
    var s=String(v);
    if(s.indexOf(',')>=0||s.indexOf('"')>=0||s.indexOf('\n')>=0)return '"'+s.replace(/"/g,'""')+'"';
    return s;
  }
  var lines=[columns.map(function(c){return esc(c.label);}).join(',')];
  var i;
  for(i=0;i<rows.length;i++){
    lines.push(columns.map(function(c){return esc(rows[i][c.key]);}).join(','));
  }
  return lines.join('\r\n');
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- Wall length ----
assert('open wall (straight line) length is correct', approx(bimWallLength([[0,0],[6,0]],false),6));
assert('open L-shaped wall length sums both segments', approx(bimWallLength([[0,0],[6,0],[6,4]],false),10));
assert('closed rectangular wall length includes the wrap-around segment (perimeter)', approx(bimWallLength([[0,0],[6,0],[6,4],[0,4]],true),20));
assert('wall with missing centerline returns 0, not a crash', bimWallLength(null,false)===0);
assert('wall with a single point returns 0', bimWallLength([[0,0]],false)===0);

// ---- Room schedule ----
var A3D={levels:[{id:'lvl-0',name:'Level 0'},{id:'lvl-1',name:'Level 1'}],objs:[
  {id:'r1',t:'room',name:'Room_1',area:24.5,levelId:'lvl-0',sourceType:'wall'},
  {id:'r2',t:'room',name:'Room_2',area:12.1,levelId:'lvl-1',sourceType:'sketch'},
  {id:'w0',t:'solid',bim:{type:'wall'}} // should NOT appear in the room schedule
]};
var roomSched=bimBuildRoomSchedule(A3D);
assert('room schedule includes exactly the room objects, nothing else', roomSched.length===2);
assert('room schedule resolves the level id to a readable name', roomSched[0].level==='Level 0');
assert('room schedule preserves the exact area value', roomSched[1].area===12.1);

// ---- Door/Window schedule ----
var A3D2={levels:[{id:'lvl-0',name:'Level 0'}],objs:[
  {id:'wallX',t:'solid',name:'Wall_1',bim:{type:'wall'}},
  {id:'d1',t:'opening',name:'Door_1',bim:{type:'door',hostWallId:'wallX',width:0.9,height:2.1}},
  {id:'win1',t:'opening',name:'Window_1',bim:{type:'window',hostWallId:'wallX',width:1.2,height:1.0,sillHeight:0.9}},
  {id:'d2',t:'opening',name:'Door_2',bim:{type:'door',hostWallId:'missing-wall',width:0.8,height:2.0}}
]};
var doorSched=bimBuildDoorSchedule(A3D2);
assert('door schedule includes only door-type openings', doorSched.length===2);
assert('door schedule correctly resolves the host wall name', doorSched[0].hostWall==='Wall_1');
assert('door schedule handles a missing/deleted host wall gracefully, not crashed', doorSched[1].hostWall==='(host wall missing)');
var winSched=bimBuildWindowSchedule(A3D2);
assert('window schedule includes only window-type openings', winSched.length===1);
assert('window schedule includes sill height (a field doors don\'t have)', winSched[0].sillHeight===0.9);

// ---- Wall schedule ----
var A3D3={levels:[{id:'lvl-0',name:'Level 0'}],objs:[
  {id:'w1',t:'solid',name:'Wall_1',bim:{type:'wall',centerline:[[0,0],[6,0]],closed:false,thickness:0.3,height:3,levelId:'lvl-0'}},
  {id:'w2',t:'solid',name:'IFCWall_1',bim:{type:'wall',imported:true}} // no centerline (unrecovered import)
]};
var wallSched=bimBuildWallSchedule(A3D3);
assert('wall schedule includes both native and imported walls', wallSched.length===2);
assert('native wall gets a computed length', approx(wallSched[0].length,6));
assert('native wall gets a computed area (length x height)', approx(wallSched[0].area,18));
assert('imported wall without centerline shows null length rather than crashing or showing 0 misleadingly', wallSched[1].length===null);
assert('imported wall is flagged as imported for the schedule to display distinctly', wallSched[1].imported===true);

// ---- Column schedule ----
var A3D4={levels:[{id:'lvl-0',name:'Level 0'}],objs:[
  {id:'c1',t:'solid',name:'Column_1',bim:{type:'column',width:0.4,depth:0.4,height:3,levelId:'lvl-0'}}
]};
var colSched=bimBuildColumnSchedule(A3D4);
assert('column schedule includes the column with correct dimensions', colSched.length===1&&colSched[0].width===0.4);

// ---- CSV export ----
var csvRows=[{name:'Room_1',area:24.5},{name:'Room, "Big"',area:12}];
var csvCols=[{key:'name',label:'Name'},{key:'area',label:'Area'}];
var csv=bimScheduleToCSV(csvRows,csvCols);
assert('CSV header row matches column labels', csv.split('\r\n')[0]==='Name,Area');
assert('CSV correctly quotes/escapes a value containing a comma and quote', csv.indexOf('"Room, ""Big"""')>=0, csv);
assert('CSV plain numeric values are not quoted', csv.split('\r\n')[1].indexOf('24.5')>=0 && csv.split('\r\n')[1].indexOf('"24.5"')===-1);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
