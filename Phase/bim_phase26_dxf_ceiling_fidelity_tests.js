var A3D={objs:[],layers:[{id:'L1',name:'A-WALL'}],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'L1',sel:null,sel2:null,selSet:[],levels:[{id:'lvl-0',name:'L0',elev:0,height:3}]};
function pushUndo(){} function a3dToast(){} function paint(){} function saveSoon(){}
function refreshTree(){} function refreshHud(){} function bimGetActiveLevel(){return A3D.levels[0];}
  var DXF_UNIT_SCALE={1:0.0254,2:0.3048,4:0.001,5:0.01,6:1,10:0.9144};

  var DXF_ACI={1:'#ff5555',2:'#e8d24a',3:'#5ac25a',4:'#4ac6c6',5:'#5a7fe0',6:'#c85ac0',7:'#d8d8d8',8:'#8a8a8a',9:'#bcbcbc'};

  function bimDxfPair(code,val){return code+'\r\n'+val+'\r\n';}

  function bimDxfLayerName(raw){
    return String(raw||'0').replace(/[<>\/\\":;?*|=`,]/g,'_').replace(/\s+/g,'_').slice(0,255)||'0';
  }

  function bimBuildDXF(){
    var P=bimDxfPair,out='',layers=A3D.layers,i;
    out+=P(0,'SECTION')+P(2,'HEADER')+P(9,'$INSUNITS')+P(70,6)+P(0,'ENDSEC');
    out+=P(0,'SECTION')+P(2,'TABLES')+P(0,'TABLE')+P(2,'LAYER')+P(70,layers.length+1);
    out+=P(0,'LAYER')+P(2,'0')+P(70,0)+P(62,7)+P(6,'CONTINUOUS');
    for(i=0;i<layers.length;i++)out+=P(0,'LAYER')+P(2,bimDxfLayerName(layers[i].name))+P(70,0)+P(62,7)+P(6,'CONTINUOUS');
    out+=P(0,'ENDTAB')+P(0,'ENDSEC')+P(0,'SECTION')+P(2,'ENTITIES');
    var stats={lwpolyline:0,line:0,text:0,skipped:0};
    function layerOf(o){
      var k;
      for(k=0;k<layers.length;k++)if(layers[k].id===o.layer)return bimDxfLayerName(layers[k].name);
      return '0';
    }
    function poly(pts,closed,lay){
      out+=P(0,'LWPOLYLINE')+P(8,lay)+P(100,'AcDbEntity')+P(100,'AcDbPolyline')+P(90,pts.length)+P(70,closed?1:0);
      var q;
      for(q=0;q<pts.length;q++)out+=P(10,pts[q][0].toFixed(6))+P(20,pts[q][1].toFixed(6));
      stats.lwpolyline++;
    }
    function line(a,b,lay){
      out+=P(0,'LINE')+P(8,lay)+P(10,a[0].toFixed(6))+P(20,a[1].toFixed(6))+P(30,'0.0')+P(11,b[0].toFixed(6))+P(21,b[1].toFixed(6))+P(31,'0.0');
      stats.line++;
    }
    function text(pt,str,h,lay){
      out+=P(0,'TEXT')+P(8,lay)+P(10,pt[0].toFixed(6))+P(20,pt[1].toFixed(6))+P(30,'0.0')+P(40,h.toFixed(4))+P(1,String(str).replace(/[\r\n]+/g,' '));
      stats.text++;
    }
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],lay=layerOf(o),b=o.bim;
      if(b&&b.type==='wall'&&b.centerline){
        poly(b.centerline,!!b.closed,lay);
        if(b.innerLoop)poly(b.innerLoop,true,lay);
        if(b.outerLoop)poly(b.outerLoop,true,lay);
      }else if(o.t==='room'){
        poly(o.pts,true,lay);
        var cx=0,cz=0,r;
        for(r=0;r<o.pts.length;r++){cx+=o.pts[r][0];cz+=o.pts[r][1];}
        text([cx/o.pts.length,cz/o.pts.length],o.name+' '+o.area.toFixed(2)+'m2',0.25,lay);
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(o.pts,o.closed!==false,lay);
      }else if(o.t==='dim'){
        line(o.d1,o.d2,lay);line(o.p1,o.d1,lay);line(o.p2,o.d2,lay);
        text([(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2],o.length.toFixed(2),0.2,lay);
      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay);
      }else if(b&&(b.type==='floor'||b.type==='ceiling'||b.type==='roof')&&(b.profile||b.footprint)){
        poly(b.profile||b.footprint,true,lay);
      }else if(b&&b.type==='column'&&b.center){
        var c=b.center,hw=b.width/2,hd=b.depth/2;
        poly([[c[0]-hw,c[1]-hd],[c[0]+hw,c[1]-hd],[c[0]+hw,c[1]+hd],[c[0]-hw,c[1]+hd]],true,lay);
      }else{
        stats.skipped++;
      }
    }
    out+=P(0,'ENDSEC')+P(0,'EOF');
    return {text:out,stats:stats};
  }

  function bimBuildFloorGeometry(profPts,y,thickness){
    var m;
    try{m=padMesh(profPts,y-thickness,thickness);}
    catch(eF){console.warn('[BIM] Floor solid build failed: ',eF);return {error:'Floor build failed: '+(eF&&eF.message?eF.message:eF)};}
    if(!m||!m.f||m.f.length<4)return {error:'Floor produced an empty solid: check the source profile'};
    return {mesh:m};
  }

  function buildCeilingSolid(boundary,heightAbove,thickness){
    var lvl=bimGetActiveLevel();
    var ceilY=boundary.y+heightAbove;
    var res=bimBuildFloorGeometry(sketchCCW(boundary.pts),ceilY+thickness,thickness);
    if(res.error){a3dToast(res.error.replace('Floor','Ceiling'));return null;}
    pushUndo();
    A3D.counts.ceiling=(A3D.counts.ceiling||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Ceiling_'+A3D.counts.ceiling,col:'#b8bfc7',pos:[0,0,0],mesh:res.mesh,
      bim:{type:'ceiling',thickness:thickness,heightAbove:heightAbove,levelId:lvl.id,baseY:ceilY,profile:sketchCCW(boundary.pts)},layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }

  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }

  function earClip(P){
    var idx=[],i,n=P.length,tris=[],guard=0;
    for(i=0;i<n;i++)idx.push(i);
    function cross2(o,a2,b2){return (a2[0]-o[0])*(b2[1]-o[1])-(a2[1]-o[1])*(b2[0]-o[0]);}
    function inTri(p,a2,b2,c2){
      var d1=cross2(p,a2,b2),d2=cross2(p,b2,c2),d3=cross2(p,c2,a2);
      var neg=(d1<0)||(d2<0)||(d3<0),pos=(d1>0)||(d2>0)||(d3>0);
      return !(neg&&pos);
    }
    while(idx.length>3&&guard++<3000){
      var cut=false;
      for(i=0;i<idx.length;i++){
        var i0=idx[(i+idx.length-1)%idx.length],i1=idx[i],i2=idx[(i+1)%idx.length];
        if(cross2(P[i0],P[i1],P[i2])<=1e-9)continue;
        var ok=true,k;
        for(k=0;k<idx.length;k++){
          var ix=idx[k];
          if(ix===i0||ix===i1||ix===i2)continue;
          if(inTri(P[ix],P[i0],P[i1],P[i2])){ok=false;break;}
        }
        if(!ok)continue;
        tris.push([i0,i1,i2]);
        idx.splice(i,1);
        cut=true;
        break;
      }
      if(!cut)break;
    }
    if(idx.length===3)tris.push([idx[0],idx[1],idx[2]]);
    return tris;
  }

  function padMesh(P,y0,h){
    var n=P.length,v=[],f=[],i,j;
    for(i=0;i<n;i++)v.push([P[i][0],y0,P[i][1]]);
    for(i=0;i<n;i++)v.push([P[i][0],y0+h,P[i][1]]);
    var tris=earClip(P);
    for(i=0;i<tris.length;i++)f.push([tris[i][0],tris[i][1],tris[i][2]]);
    for(i=0;i<tris.length;i++)f.push([tris[i][2]+n,tris[i][1]+n,tris[i][0]+n]);
    for(i=0;i<n;i++){
      j=(i+1)%n;
      f.push([j,i,i+n,j+n]);
    }
    return {v:v,f:f};
  }

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

A3D.objs=[
  {id:'w1',t:'solid',layer:'L1',bim:{type:'wall',centerline:[[0,0],[6,0],[6,4],[0,4]],closed:true}},
  {id:'r1',t:'room',layer:'L1',name:'Room_1',pts:[[0,0],[6,0],[6,4],[0,4]],area:24},
  {id:'o1',t:'opening',layer:'L1',bim:{type:'door'}}
];
var res=bimBuildDXF();
assert('real embedded exporter produces polylines', res.stats.lwpolyline>=2, res.stats.lwpolyline);
assert('real embedded exporter counts openings as skipped (no 2D footprint)', res.stats.skipped===1);
var p=dxfParse(res.text);
assert('real embedded exporter output parses with the real embedded importer', !!p&&!!p.entities);
assert('round-trip recovers the wall polyline with exact coordinates',
  p.entities.some(function(e){return e.type==='LWPOLYLINE'&&e.pts.length===4&&e.pts[1][0]===6;}));
assert('round-trip preserves layer assignment', p.entities[0].layer==='A-WALL', p.entities[0].layer);
assert('round-trip preserves metre units', p.insUnits===6);

// Ceiling via real embedded code
A3D.objs=[];
var c=buildCeilingSolid({pts:[[0,0],[6,0],[6,4],[0,4]],y:0},3,0.1);
assert('real buildCeilingSolid creates a ceiling object', !!c&&c.bim.type==='ceiling');
assert('ceiling sits at the requested height above the level (3.0)', c.bim.baseY===3);
assert('ceiling records its thickness and height offset', c.bim.thickness===0.1&&c.bim.heightAbove===3);
assert('ceiling mesh is real geometry', c.mesh&&c.mesh.f.length>=4);
var ys=c.mesh.v.map(function(v){return v[1];});
assert('ceiling geometry spans the correct vertical band (3.0 to 3.1)',
  Math.abs(Math.min.apply(null,ys)-3)<1e-6&&Math.abs(Math.max.apply(null,ys)-3.1)<1e-6, Math.min.apply(null,ys)+'..'+Math.max.apply(null,ys));

// ceiling exports its footprint to DXF
A3D.objs=[c];
var res2=bimBuildDXF();
assert('ceiling footprint is included in DXF export', res2.stats.lwpolyline===1&&res2.stats.skipped===0);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
