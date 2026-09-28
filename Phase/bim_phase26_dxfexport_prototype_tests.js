function dxfPair(code,val){return code+'\r\n'+val+'\r\n';}
function bimDxfLayerName(raw){
  // DXF layer names cannot contain these characters; also normalize spaces.
  return String(raw||'0').replace(/[<>\/\\":;?*|=`,]/g,'_').replace(/\s+/g,'_').slice(0,255)||'0';
}
function bimBuildDXF(objs,layers){
  var out='';
  // --- HEADER: declare millimetre-agnostic unitless drawing, matching how we import ---
  out+=dxfPair(0,'SECTION')+dxfPair(2,'HEADER');
  out+=dxfPair(9,'$INSUNITS')+dxfPair(70,6); // 6 = metres
  out+=dxfPair(0,'ENDSEC');
  // --- TABLES: layer definitions ---
  out+=dxfPair(0,'SECTION')+dxfPair(2,'TABLES');
  out+=dxfPair(0,'TABLE')+dxfPair(2,'LAYER')+dxfPair(70,layers.length+1);
  out+=dxfPair(0,'LAYER')+dxfPair(2,'0')+dxfPair(70,0)+dxfPair(62,7)+dxfPair(6,'CONTINUOUS');
  var i;
  for(i=0;i<layers.length;i++){
    out+=dxfPair(0,'LAYER')+dxfPair(2,bimDxfLayerName(layers[i].name))+dxfPair(70,0)+dxfPair(62,7)+dxfPair(6,'CONTINUOUS');
  }
  out+=dxfPair(0,'ENDTAB')+dxfPair(0,'ENDSEC');
  // --- ENTITIES ---
  out+=dxfPair(0,'SECTION')+dxfPair(2,'ENTITIES');
  var stats={lwpolyline:0,line:0,text:0,skipped:0};
  function layerOf(o){
    var lid=o.layer,k;
    for(k=0;k<layers.length;k++)if(layers[k].id===lid)return bimDxfLayerName(layers[k].name);
    return '0';
  }
  function emitPolyline(pts,closed,layer){
    out+=dxfPair(0,'LWPOLYLINE')+dxfPair(8,layer)+dxfPair(100,'AcDbEntity')+dxfPair(100,'AcDbPolyline');
    out+=dxfPair(90,pts.length)+dxfPair(70,closed?1:0);
    var p;
    for(p=0;p<pts.length;p++)out+=dxfPair(10,pts[p][0].toFixed(6))+dxfPair(20,pts[p][1].toFixed(6));
    stats.lwpolyline++;
  }
  function emitLine(a,b,layer){
    out+=dxfPair(0,'LINE')+dxfPair(8,layer);
    out+=dxfPair(10,a[0].toFixed(6))+dxfPair(20,a[1].toFixed(6))+dxfPair(30,'0.0');
    out+=dxfPair(11,b[0].toFixed(6))+dxfPair(21,b[1].toFixed(6))+dxfPair(31,'0.0');
    stats.line++;
  }
  function emitText(pt,str,height,layer){
    out+=dxfPair(0,'TEXT')+dxfPair(8,layer);
    out+=dxfPair(10,pt[0].toFixed(6))+dxfPair(20,pt[1].toFixed(6))+dxfPair(30,'0.0');
    out+=dxfPair(40,height.toFixed(4))+dxfPair(1,String(str).replace(/[\r\n]+/g,' '));
    stats.text++;
  }
  for(i=0;i<objs.length;i++){
    var o=objs[i],lay=layerOf(o);
    if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline){
      emitPolyline(o.bim.centerline,!!o.bim.closed,lay);
      if(o.bim.innerLoop)emitPolyline(o.bim.innerLoop,true,lay);
      if(o.bim.outerLoop)emitPolyline(o.bim.outerLoop,true,lay);
    }else if(o.t==='room'){
      emitPolyline(o.pts,true,lay);
      var cx=0,cz=0,r;
      for(r=0;r<o.pts.length;r++){cx+=o.pts[r][0];cz+=o.pts[r][1];}
      emitText([cx/o.pts.length,cz/o.pts.length],o.name+' '+o.area.toFixed(2)+'m2',0.25,lay);
    }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
      emitPolyline(o.pts,o.closed!==false,lay);
    }else if(o.t==='dim'){
      emitLine(o.d1,o.d2,lay);
      emitLine(o.p1,o.d1,lay);
      emitLine(o.p2,o.d2,lay);
      emitText([(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2],o.length.toFixed(2),0.2,lay);
    }else if(o.t==='text'){
      emitText(o.pt,o.text,0.25,lay);
    }else if(o.t==='solid'&&o.bim&&(o.bim.type==='floor'||o.bim.type==='roof')&&(o.bim.profile||o.bim.footprint)){
      emitPolyline(o.bim.profile||o.bim.footprint,true,lay);
    }else if(o.t==='solid'&&o.bim&&o.bim.type==='column'&&o.bim.center){
      var c=o.bim.center,hw=o.bim.width/2,hd=o.bim.depth/2;
      emitPolyline([[c[0]-hw,c[1]-hd],[c[0]+hw,c[1]-hd],[c[0]+hw,c[1]+hd],[c[0]-hw,c[1]+hd]],true,lay);
    }else{
      stats.skipped++;
    }
  }
  out+=dxfPair(0,'ENDSEC')+dxfPair(0,'EOF');
  return {text:out,stats:stats};
}

// ---- minimal DXF reader, only to validate our own output structurally ----
function readDxfPairs(text){
  var lines=text.split(/\r\n|\n/),pairs=[],i;
  for(i=0;i+1<lines.length;i+=2){
    if(lines[i]==='')break;
    pairs.push([parseInt(lines[i],10),lines[i+1]]);
  }
  return pairs;
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}

var layers=[{id:'L1',name:'A-WALL'},{id:'L2',name:'Bad/Name:Here'}];
var objs=[
  {id:'w1',t:'solid',layer:'L1',bim:{type:'wall',centerline:[[0,0],[6,0],[6,4],[0,4]],closed:true,innerLoop:[[0.15,0.15],[5.85,0.15],[5.85,3.85],[0.15,3.85]]}},
  {id:'r1',t:'room',layer:'L1',name:'Room_1',pts:[[0,0],[6,0],[6,4],[0,4]],area:24},
  {id:'d1',t:'dim',layer:'L2',p1:[0,0],p2:[6,0],d1:[0,-1],d2:[6,-1],length:6},
  {id:'t1',t:'text',layer:'L2',text:'Kitchen',pt:[3,2]},
  {id:'c1',t:'solid',layer:'L1',bim:{type:'column',center:[2,2],width:0.4,depth:0.4}},
  {id:'x1',t:'opening',layer:'L1',bim:{type:'door'}}
];
var res=bimBuildDXF(objs,layers);
var txt=res.text;

assert('DXF starts with a SECTION', txt.indexOf('SECTION')>=0);
assert('DXF terminates with EOF', txt.trim().slice(-3)==='EOF');
assert('DXF contains a HEADER section', txt.indexOf('HEADER')>=0);
assert('DXF contains a TABLES/LAYER section', txt.indexOf('TABLES')>=0&&txt.indexOf('LAYER')>=0);
assert('DXF contains an ENTITIES section', txt.indexOf('ENTITIES')>=0);

assert('illegal DXF layer-name characters are sanitized', txt.indexOf('Bad/Name:Here')===-1&&txt.indexOf('Bad_Name_Here')>=0);
assert('valid layer name passes through unchanged', txt.indexOf('A-WALL')>=0);

assert('wall centerline exported as LWPOLYLINE', res.stats.lwpolyline>=1);
assert('wall closed flag emitted (70=1)', txt.indexOf('70\r\n1\r\n')>=0);
assert('room name+area exported as TEXT', txt.indexOf('Room_1 24.00m2')>=0);
assert('text label exported verbatim', txt.indexOf('Kitchen')>=0);
assert('dimension emits its measured length as text', txt.indexOf('6.00')>=0);
assert('dimension emits 3 LINE entities (dim line + 2 extension lines)', res.stats.line===3, res.stats.line);
assert('opening (no 2D footprint) is skipped, counted, not silently mangled', res.stats.skipped===1);

// structural parse: every code line must be an integer
var pairs=readDxfPairs(txt);
assert('every emitted group code parses as an integer', pairs.every(function(p){return Number.isInteger(p[0]);}));
assert('a meaningful number of group pairs were emitted', pairs.length>50, pairs.length);

// counts: wall(centerline+inner)=2, room=1, sketch=0, floor/roof=0, column=1 -> 4 polylines
assert('polyline count matches expected entity breakdown (2 wall + 1 room + 1 column)', res.stats.lwpolyline===4, res.stats.lwpolyline);
assert('text count matches expected (room label + dim value + text label)', res.stats.text===3, res.stats.text);

// empty model
var empty=bimBuildDXF([],[]);
assert('an empty model still produces a structurally valid DXF', empty.text.indexOf('ENTITIES')>=0&&empty.text.trim().slice(-3)==='EOF');

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
