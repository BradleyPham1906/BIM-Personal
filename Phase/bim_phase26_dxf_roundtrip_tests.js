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

  var DXF_UNIT_SCALE={1:0.0254,2:0.3048,4:0.001,5:0.01,6:1,10:0.9144};
  var DXF_ACI={1:'#ff5555',2:'#e8d24a',3:'#5ac25a',4:'#4ac6c6',5:'#5a7fe0',6:'#c85ac0',7:'#d8d8d8',8:'#8a8a8a',9:'#bcbcbc'};
  function dxfAciToHex(idx){
    idx=parseInt(idx,10);
    if(!isFinite(idx)||idx<=0)return '#9db4c8';
    return DXF_ACI[idx]||'#9db4c8';
  }

  function dxfAllNums(items,code){
    var out=[],i;for(i=0;i<items.length;i++)if(items[i][0]===code)out.push(parseFloat(items[i][1]));
    return out;
  }

  function dxfHeaderVar(items,varname,code){
    var j;
    for(j=0;j<items.length-1;j++)if(items[j][0]===9&&items[j][1]===varname&&items[j+1][0]===code)return items[j+1][1];
    return null;
  }

  function dxfNum(items,code,def){
    var i;for(i=0;i<items.length;i++)if(items[i][0]===code)return parseFloat(items[i][1]);
    return def;
  }

  function dxfParse(text){
    var pairs=dxfTokenize(text);
    var i,rec=null,records=[];
    for(i=0;i<pairs.length;i++){
      var code=pairs[i][0],val=pairs[i][1];
      if(code===0){
        if(rec)records.push(rec);
        rec={type:val,items:[]};
        continue;
      }
      if(rec)rec.items.push([code,val]);
    }
    if(rec)records.push(rec);

    var section=null,inTable=null,insUnits=null;
    var layers={},entities=[],skipped={};
    var curPoly=null;
    var ENTITY_TYPES={LINE:1,CIRCLE:1,ARC:1,LWPOLYLINE:1,POLYLINE:1,VERTEX:1,SEQEND:1,'3DFACE':1,POINT:1};

    for(i=0;i<records.length;i++){
      var r=records[i],t=r.type;
      if(t==='SECTION'){
        section=dxfStr(r.items,2,null);
        if(section==='HEADER'){
          var iu=dxfHeaderVar(r.items,'$INSUNITS',70);
          if(iu!==null)insUnits=parseInt(iu,10);
        }
        continue;
      }
      if(t==='ENDSEC'){section=null;continue;}
      if(t==='TABLE'){inTable=dxfStr(r.items,2,null);continue;}
      if(t==='ENDTAB'){inTable=null;continue;}
      if(t==='EOF')continue;

      if(section==='TABLES'&&inTable==='LAYER'&&t==='LAYER'){
        var nm=dxfStr(r.items,2,'0');
        var col=dxfNum(r.items,62,7);
        layers[nm]={name:nm,color:dxfAciToHex(col)};
        continue;
      }
      if(section!=='ENTITIES')continue;

      var layerName=dxfStr(r.items,8,'0');
      var colOverride=dxfNum(r.items,62,null);

      if(t==='POLYLINE'){
        var flags=dxfNum(r.items,70,0);
        curPoly={type:'POLYLINE',closed:!!(flags&1),layer:layerName,color:colOverride,pts:[]};
        continue;
      }
      if(t==='VERTEX'&&curPoly){
        curPoly.pts.push([dxfNum(r.items,10,0),dxfNum(r.items,20,0)]);
        continue;
      }
      if(t==='SEQEND'){
        if(curPoly&&curPoly.pts.length>=2)entities.push(curPoly);
        curPoly=null;
        continue;
      }
      if(!ENTITY_TYPES[t]){
        skipped[t]=(skipped[t]||0)+1;
        continue;
      }
      if(t==='LINE'){
        entities.push({type:'LINE',layer:layerName,color:colOverride,
          p1:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],
          p2:[dxfNum(r.items,11,0),dxfNum(r.items,21,0),dxfNum(r.items,31,0)]});
      }else if(t==='CIRCLE'){
        entities.push({type:'CIRCLE',layer:layerName,color:colOverride,
          c:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],r:dxfNum(r.items,40,1)});
      }else if(t==='ARC'){
        entities.push({type:'ARC',layer:layerName,color:colOverride,
          c:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],r:dxfNum(r.items,40,1),
          a1:dxfNum(r.items,50,0),a2:dxfNum(r.items,51,360)});
      }else if(t==='LWPOLYLINE'){
        var flags2=dxfNum(r.items,70,0);
        var xs=dxfAllNums(r.items,10),ys=dxfAllNums(r.items,20);
        var pts=[],k;for(k=0;k<Math.min(xs.length,ys.length);k++)pts.push([xs[k],ys[k]]);
        if(pts.length>=2)entities.push({type:'LWPOLYLINE',closed:!!(flags2&1),layer:layerName,color:colOverride,pts:pts});
      }else if(t==='3DFACE'){
        entities.push({type:'3DFACE',layer:layerName,color:colOverride,pts:[
          [dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)],
          [dxfNum(r.items,11,0),dxfNum(r.items,21,0),dxfNum(r.items,31,0)],
          [dxfNum(r.items,12,0),dxfNum(r.items,22,0),dxfNum(r.items,32,0)],
          [dxfNum(r.items,13,0),dxfNum(r.items,23,0),dxfNum(r.items,33,0)]
        ]});
      }else if(t==='POINT'){
        entities.push({type:'POINT',layer:layerName,color:colOverride,
          p:[dxfNum(r.items,10,0),dxfNum(r.items,20,0),dxfNum(r.items,30,0)]});
      }
    }
    var scale=DXF_UNIT_SCALE[insUnits]||1;
    return {layers:layers,entities:entities,skipped:skipped,scale:scale,insUnits:insUnits};
  }

  function dxfStr(items,code,def){
    var i;for(i=0;i<items.length;i++)if(items[i][0]===code)return items[i][1];
    return def;
  }

  function dxfTokenize(text){
    var lines=text.split(/\r\n|\r|\n/),pairs=[],i;
    for(i=0;i+1<lines.length;i+=2){
      var codeStr=lines[i];if(codeStr===undefined)break;
      var code=parseInt(codeStr.trim(),10);
      var val=lines[i+1];if(val===undefined)val='';
      val=val.replace(/\r$/,'').trim();
      if(isNaN(code))continue;
      pairs.push([code,val]);
    }
    return pairs;
  }

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}

var layers=[{id:'L1',name:'A-WALL'}];
var objs=[
  {id:'w1',t:'solid',layer:'L1',bim:{type:'wall',centerline:[[0,0],[6,0],[6,4],[0,4]],closed:true}},
  {id:'t1',t:'text',layer:'L1',text:'Kitchen',pt:[3,2]},
  {id:'r1',t:'room',layer:'L1',name:'Room_1',pts:[[0,0],[6,0],[6,4],[0,4]],area:24}
];
var exported=bimBuildDXF(objs,layers).text;

var parsed=null,err=null;
try{parsed=dxfParse(exported);}catch(e){err=e;}
assert('the app\'s OWN DXF parser accepts our exported DXF without throwing', !err, err&&err.message);
assert('round-trip parse produced a result', !!parsed);

assert('round-trip recovers our exported layer name', Object.keys(parsed.layers).indexOf('A-WALL')>=0);
assert('round-trip preserves the declared unit ($INSUNITS=6, metres)', parsed.insUnits===6, parsed.insUnits);

var ents=parsed.entities||[];
assert('round-trip recovers a non-zero entity count', ents.length>0, 'n='+ents.length);

var polys=ents.filter(function(e){return e.type==='LWPOLYLINE';});
assert('round-trip recovers polylines (wall centerline + room outline)', polys.length>=2, 'polys='+polys.length);
var wall=polys[0];
assert('recovered polyline has the original 4 vertices', wall.pts.length===4, wall.pts.length);
assert('recovered polyline is marked closed', wall.closed===true);
assert('recovered vertex coordinates match the original exactly',
  wall.pts[1][0]===6&&wall.pts[2][1]===4, JSON.stringify(wall.pts));
assert('recovered entity carries the correct layer assignment', wall.layer==='A-WALL', wall.layer);

// NOTE: our exporter emits standard DXF TEXT entities, but this app's own DXF *importer* has
// never supported TEXT (it handles LINE/CIRCLE/ARC/LWPOLYLINE/POLYLINE/3DFACE/POINT only,
// documented from the start). So TEXT correctly appears in the file for other CAD apps to read,
// but round-trips back into this app as a skipped entity rather than an object. Asserting the
// real behavior rather than pretending otherwise.
var texts=ents.filter(function(e){return e.type==='TEXT';});
assert('TEXT is correctly absent from re-imported entities (importer does not support TEXT, by design)', texts.length===0, 'texts='+texts.length);
assert('but TEXT entities ARE present in the exported file itself (readable by other CAD apps)', exported.indexOf('Kitchen')>=0&&exported.indexOf('Room_1')>=0);
assert('the importer counts unsupported TEXT as skipped rather than silently losing it', parsed.skipped&&parsed.skipped.TEXT>0, JSON.stringify(parsed.skipped));

// sanitized layer name survives the round trip
var exported2=bimBuildDXF([{id:'w',t:'sketch',layer:'LX',pts:[[0,0],[1,1]],closed:false}],[{id:'LX',name:'Bad/Name:Here'}]).text;
var parsed2=dxfParse(exported2);
assert('a sanitized layer name round-trips intact', Object.keys(parsed2.layers).indexOf('Bad_Name_Here')>=0, JSON.stringify(Object.keys(parsed2.layers)));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
