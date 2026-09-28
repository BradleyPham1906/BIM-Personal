// Standalone DXF parser prototype, to be embedded verbatim (renamed with bim/dxf prefixes) in canvas_v10.html.
// Handles: LAYER table (name + ACI color), LINE, CIRCLE, ARC, LWPOLYLINE, POLYLINE/VERTEX/SEQEND, 3DFACE, POINT.
// Explicitly NOT handled (reported as skipped): INSERT (block references), splines, dimensions, text, hatches.

var DXF_ACI={1:'#ff5555',2:'#e8d24a',3:'#5ac25a',4:'#4ac6c6',5:'#5a7fe0',6:'#c85ac0',7:'#d8d8d8',8:'#8a8a8a',9:'#bcbcbc'};
function dxfAciToHex(idx){
  idx=parseInt(idx,10);
  if(!isFinite(idx)||idx<=0)return '#9db4c8';
  return DXF_ACI[idx]||'#9db4c8';
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
function dxfNum(items,code,def){
  var i;for(i=0;i<items.length;i++)if(items[i][0]===code)return parseFloat(items[i][1]);
  return def;
}
function dxfAllNums(items,code){
  var out=[],i;for(i=0;i<items.length;i++)if(items[i][0]===code)out.push(parseFloat(items[i][1]));
  return out;
}
function dxfStr(items,code,def){
  var i;for(i=0;i<items.length;i++)if(items[i][0]===code)return items[i][1];
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

  var section=null,inTable=null;
  var layers={},entities=[],skipped={};
  var curPoly=null;
  var ENTITY_TYPES={LINE:1,CIRCLE:1,ARC:1,LWPOLYLINE:1,POLYLINE:1,VERTEX:1,SEQEND:1,'3DFACE':1,POINT:1};

  for(i=0;i<records.length;i++){
    var r=records[i],t=r.type;
    if(t==='SECTION'){section=dxfStr(r.items,2,null);continue;}
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
  return {layers:layers,entities:entities,skipped:skipped};
}

// ---- TEST: synthetic DXF sample covering LAYER table + all supported entity types + one unsupported (INSERT) ----
var sample = [
'0','SECTION',
'2','TABLES',
'0','TABLE',
'2','LAYER',
'0','LAYER','2','WALLS','62','1',
'0','LAYER','2','FURNITURE','62','3',
'0','ENDTAB',
'0','ENDSEC',
'0','SECTION',
'2','ENTITIES',
'0','LINE','8','WALLS','10','0','20','0','30','0','11','10','21','0','31','0',
'0','CIRCLE','8','FURNITURE','10','5','20','5','30','0','40','2',
'0','ARC','8','WALLS','10','0','20','0','30','0','40','3','50','0','51','90',
'0','LWPOLYLINE','8','WALLS','70','1','90','4','10','0','20','0','10','6','20','0','10','6','20','4','10','0','20','4',
'0','POLYLINE','8','WALLS','70','1',
'0','VERTEX','8','WALLS','10','0','20','0','30','0',
'0','VERTEX','8','WALLS','10','3','20','0','30','0',
'0','VERTEX','8','WALLS','10','3','20','3','30','0',
'0','SEQEND',
'0','3DFACE','8','FURNITURE','10','0','20','0','30','1','11','1','21','0','31','1','12','1','22','1','32','1','13','0','23','1','33','1',
'0','POINT','8','WALLS','10','1','20','1','30','0',
'0','INSERT','8','FURNITURE','2','CHAIR_BLOCK','10','2','20','2','30','0',
'0','ENDSEC',
'0','EOF'
].join('\n');

var res=dxfParse(sample);
console.log('Layers parsed:', JSON.stringify(res.layers));
console.log('Entity count:', res.entities.length, res.entities.map(function(e){return e.type;}));
console.log('Skipped (unsupported):', JSON.stringify(res.skipped));

var PASS=0,FAIL=0;
function assert(name,cond){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name);}}
assert('parses 2 layers with correct names', Object.keys(res.layers).length===2 && res.layers.WALLS && res.layers.FURNITURE);
assert('WALLS layer color maps ACI 1 -> red-ish hex', res.layers.WALLS.color===dxfAciToHex(1));
assert('parses LINE with correct endpoints', res.entities.some(function(e){return e.type==='LINE'&&e.p2[0]===10;}));
assert('parses CIRCLE with correct radius', res.entities.some(function(e){return e.type==='CIRCLE'&&e.r===2;}));
assert('parses ARC with correct angles', res.entities.some(function(e){return e.type==='ARC'&&e.a2===90;}));
assert('parses closed LWPOLYLINE with 4 vertices', res.entities.some(function(e){return e.type==='LWPOLYLINE'&&e.pts.length===4&&e.closed;}));
assert('parses legacy POLYLINE/VERTEX/SEQEND into one entity with 3 pts', res.entities.some(function(e){return e.type==='POLYLINE'&&e.pts.length===3;}));
assert('parses 3DFACE with 4 corner points', res.entities.some(function(e){return e.type==='3DFACE'&&e.pts.length===4;}));
assert('parses POINT', res.entities.some(function(e){return e.type==='POINT';}));
assert('INSERT correctly reported as skipped (unsupported)', res.skipped.INSERT===1);
console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');

// ---- Extra test: HEADER section $INSUNITS extraction (uses same 0-code record grouping) ----
function dxfHeaderVar(items,varname,code){
  var j;
  for(j=0;j<items.length-1;j++){
    if(items[j][0]===9&&items[j][1]===varname&&items[j+1][0]===code)return items[j+1][1];
  }
  return null;
}
var headerSample=[
  '0','SECTION','2','HEADER',
  '9','$ACADVER','1','AC1015',
  '9','$INSUNITS','70','4',
  '9','$EXTMIN','10','0','20','0','30','0',
  '0','ENDSEC',
  '0','SECTION','2','ENTITIES','0','LINE','8','0','10','0','20','0','30','0','11','1','21','0','31','0','0','ENDSEC','0','EOF'
].join('\n');
var pairs2=dxfTokenize(headerSample);
var rec2=null,records2=[],j2;
for(j2=0;j2<pairs2.length;j2++){
  var code2=pairs2[j2][0],val2=pairs2[j2][1];
  if(code2===0){ if(rec2)records2.push(rec2); rec2={type:val2,items:[]}; continue; }
  if(rec2)rec2.items.push([code2,val2]);
}
if(rec2)records2.push(rec2);
var headerRec=records2[0];
console.log('First record type (expect SECTION):', headerRec.type);
console.log('INSUNITS raw value (expect "4" = millimeters):', dxfHeaderVar(headerRec.items,'$INSUNITS',70));
var PASS2=(dxfHeaderVar(headerRec.items,'$INSUNITS',70)==='4')?1:0;
console.log(PASS2?'PASS  header $INSUNITS extraction':'FAIL  header $INSUNITS extraction');
console.log('');
console.log('GRAND TOTAL: '+(PASS+PASS2)+' passed, '+(FAIL+(1-PASS2))+' failed');
process.exit((FAIL>0||PASS2!==1)?1:0);
