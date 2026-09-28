var A3D={objs:[],layers:[{id:'L1',name:'A-ANNO'}],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'L1',
  activeViewId:null,sel:null,sel2:null,selSet:[],levels:[{id:'lvl-0',name:'L0',elev:0,height:3}]};
var UNDO=[];
function pushUndo(){UNDO.push(1);}
function a3dToast(){} function paint(){} function saveSoon(){}
function refreshTree(){} function refreshHud(){}
  var DXF_UNIT_SCALE={1:0.0254,2:0.3048,4:0.001,5:0.01,6:1,10:0.9144};

  var DXF_ACI={1:'#ff5555',2:'#e8d24a',3:'#5ac25a',4:'#4ac6c6',5:'#5a7fe0',6:'#c85ac0',7:'#d8d8d8',8:'#8a8a8a',9:'#bcbcbc'};

  function bimDimKind(o){return (o&&o.dimKind)||'linear';}

  function bimComputeAngularDim(vertex,p1,p2){
    var a1=Math.atan2(p1[1]-vertex[1],p1[0]-vertex[0]);
    var a2=Math.atan2(p2[1]-vertex[1],p2[0]-vertex[0]);
    var r1=Math.sqrt(Math.pow(p1[0]-vertex[0],2)+Math.pow(p1[1]-vertex[1],2));
    var r2=Math.sqrt(Math.pow(p2[0]-vertex[0],2)+Math.pow(p2[1]-vertex[1],2));
    if(r1<1e-9||r2<1e-9)return null;
    var sweep=a2-a1;
    while(sweep<=-Math.PI)sweep+=Math.PI*2;
    while(sweep>Math.PI)sweep-=Math.PI*2;
    return {vertex:vertex,a1:a1,a2:a2,sweep:sweep,radius:Math.min(r1,r2)*0.6,degrees:Math.abs(sweep)*180/Math.PI};
  }

  function bimCircleFrom3Points(p1,p2,p3){
    var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
    var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
    if(Math.abs(d)<1e-9)return null;
    var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
    var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
    return {center:[ux,uy],radius:Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2))};
  }

  function bimComputeRadialDim(center,radius,anglePt,isDiameter){
    var ang=Math.atan2(anglePt[1]-center[1],anglePt[0]-center[0]);
    var edge=[center[0]+Math.cos(ang)*radius,center[1]+Math.sin(ang)*radius];
    var start=isDiameter?[center[0]-Math.cos(ang)*radius,center[1]-Math.sin(ang)*radius]:center;
    return {center:center,radius:radius,start:start,edge:edge,value:isDiameter?radius*2:radius,isDiameter:!!isDiameter};
  }

  function bimComputeLeader(anchorPt,elbowPt,textPt){
    var dir=textPt[0]>=elbowPt[0]?1:-1;
    return {anchor:anchorPt,elbow:elbowPt,landing:[elbowPt[0]+dir*0.5,elbowPt[1]],textPt:textPt,dir:dir};
  }

  function bimNewDimBase(){
    A3D.counts.dim=(A3D.counts.dim||0)+1;
    var lvl=bimGetActiveLevel();
    return {id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',col:'#dfe4ea',pos:[0,0,0],
      y:lvl.elev,levelId:A3D.activeLevel,layer:A3D.activeLayer,viewId:A3D.activeViewId};
  }

  function bimCreateAngularDim(vertex,p1,p2){
    var r=bimComputeAngularDim(vertex,p1,p2);
    if(!r){a3dToast('Angle rays cannot be zero-length');return null;}
    pushUndo();
    var o=bimNewDimBase();
    o.dimKind='angular';o.name='Angle_'+A3D.counts.dim;
    o.vertex=vertex;o.ap1=p1;o.ap2=p2;o.a1=r.a1;o.sweep=r.sweep;o.arcRadius=r.radius;o.degrees=r.degrees;
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' \u2014 '+r.degrees.toFixed(1)+'\u00b0');
    return o;
  }

  function bimCreateRadialDim(p1,p2,p3,isDiameter){
    var circ=bimCircleFrom3Points(p1,p2,p3);
    if(!circ){a3dToast('Those three points are collinear \u2014 no circle through them');return null;}
    var r=bimComputeRadialDim(circ.center,circ.radius,p3,isDiameter);
    pushUndo();
    var o=bimNewDimBase();
    o.dimKind=isDiameter?'diameter':'radius';
    o.name=(isDiameter?'Dia_':'Rad_')+A3D.counts.dim;
    o.center=circ.center;o.radius=circ.radius;o.dStart=r.start;o.dEdge=r.edge;o.value=r.value;
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' \u2014 '+r.value.toFixed(2)+' m');
    return o;
  }

  function bimCreateLeader(anchorPt,elbowPt,textPt,label){
    var r=bimComputeLeader(anchorPt,elbowPt,textPt);
    pushUndo();
    var o=bimNewDimBase();
    o.dimKind='leader';o.name='Leader_'+A3D.counts.dim;
    o.anchor=r.anchor;o.elbow=r.elbow;o.landing=r.landing;o.label=label;o.ldir=r.dir;
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }

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
      }else if(o.t==='dim'&&bimDimKind(o)==='linear'){
        line(o.d1,o.d2,lay);line(o.p1,o.d1,lay);line(o.p2,o.d2,lay);
        text([(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2],o.length.toFixed(2),0.2,lay);
      }else if(o.t==='dim'&&bimDimKind(o)==='angular'){
        line(o.vertex,o.ap1,lay);line(o.vertex,o.ap2,lay);
        var arcPts=[],ai;
        for(ai=0;ai<=16;ai++){
          var aa=o.a1+o.sweep*(ai/16);
          arcPts.push([o.vertex[0]+Math.cos(aa)*o.arcRadius,o.vertex[1]+Math.sin(aa)*o.arcRadius]);
        }
        poly(arcPts,false,lay);
        var midA=o.a1+o.sweep/2;
        text([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25],o.degrees.toFixed(1)+'deg',0.2,lay);
      }else if(o.t==='dim'&&(bimDimKind(o)==='radius'||bimDimKind(o)==='diameter')){
        var cPts=[],ci2;
        for(ci2=0;ci2<=32;ci2++){
          var cc=(ci2/32)*Math.PI*2;
          cPts.push([o.center[0]+Math.cos(cc)*o.radius,o.center[1]+Math.sin(cc)*o.radius]);
        }
        poly(cPts,true,lay);
        line(o.dStart,o.dEdge,lay);
        text([(o.dStart[0]+o.dEdge[0])/2,(o.dStart[1]+o.dEdge[1])/2],(bimDimKind(o)==='diameter'?'D':'R')+o.value.toFixed(2),0.2,lay);
      }else if(o.t==='dim'&&bimDimKind(o)==='leader'){
        poly([o.anchor,o.elbow,o.landing],false,lay);
        text(o.landing,o.label||'',0.2,lay);
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

  function bimGetActiveLevel(){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)return A3D.levels[i];
    return A3D.levels[0]||{id:'lvl-0',name:'Level 0',elev:0,height:3};
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
function approx(a,b,e){return Math.abs(a-b)<(e||1e-6);}

// backward compat: existing linear dims have no dimKind
assert('a pre-existing linear dim (no dimKind) reads as linear', bimDimKind({t:'dim'})==='linear');
assert('bimDimKind on null is safe', bimDimKind(null)==='linear');

// angular via real embedded create
UNDO.length=0;
var ang=bimCreateAngularDim([0,0],[1,0],[0,1]);
assert('real bimCreateAngularDim creates an object', !!ang&&ang.t==='dim');
assert('angular dim tagged with dimKind', ang.dimKind==='angular');
assert('angular dim measures 90 degrees', approx(ang.degrees,90), ang.degrees);
assert('angular dim pushes one undo', UNDO.length===1);
assert('angular dim inherits standard dim plumbing (layer/level/view fields)',
  ang.layer==='L1'&&ang.levelId==='lvl-0'&&ang.hasOwnProperty('viewId'));
var angBad=bimCreateAngularDim([0,0],[0,0],[1,0]);
assert('degenerate angular dim rejected, no object created', angBad===null);

// radius / diameter
var rad=bimCreateRadialDim([1,0],[0,1],[-1,0],false);
assert('real bimCreateRadialDim builds a radius dim from 3 points', !!rad&&rad.dimKind==='radius');
assert('recovered radius is 1 for unit-circle points', approx(rad.radius,1), rad.radius);
assert('radius value equals the radius', approx(rad.value,1));
var dia=bimCreateRadialDim([1,0],[0,1],[-1,0],true);
assert('diameter dim value is twice the radius', approx(dia.value,2), dia.value);
assert('diameter dim tagged correctly', dia.dimKind==='diameter');
var collinear=bimCreateRadialDim([0,0],[1,1],[2,2],false);
assert('collinear points rejected for radial dim', collinear===null);

// leader
var ld=bimCreateLeader([0,0],[2,2],[4,2],'Note here');
assert('real bimCreateLeader creates a leader', !!ld&&ld.dimKind==='leader');
assert('leader stores its label text', ld.label==='Note here');
assert('leader landing points toward the text side', ld.landing[0]>ld.elbow[0]);

// names are distinct per kind
assert('each kind gets a distinct name prefix',
  ang.name.indexOf('Angle_')===0&&rad.name.indexOf('Rad_')===0&&dia.name.indexOf('Dia_')===0&&ld.name.indexOf('Leader_')===0,
  [ang.name,rad.name,dia.name,ld.name].join(','));

// DXF export handles all new kinds, and round-trips through the real parser
var res=bimBuildDXF();
assert('DXF export emits geometry for all 4 new dim objects (none skipped)', res.stats.skipped===0, 'skipped='+res.stats.skipped);
assert('DXF export emits polylines for angular arc / circles / leader', res.stats.lwpolyline>=4, res.stats.lwpolyline);
assert('DXF export emits the angular value as text', res.text.indexOf('90.0deg')>=0);
assert('DXF export emits radius/diameter prefixes', res.text.indexOf('R1.00')>=0&&res.text.indexOf('D2.00')>=0);
assert('DXF export emits the leader label', res.text.indexOf('Note here')>=0);
var parsed=dxfParse(res.text);
assert('new dim types round-trip through the app\'s own DXF parser without throwing', !!parsed&&!!parsed.entities);
assert('round-trip recovers a non-zero entity count', parsed.entities.length>0, parsed.entities.length);

// a linear dim still exports through the original path unchanged
A3D.objs=[{id:'d0',t:'dim',layer:'L1',p1:[0,0],p2:[6,0],d1:[0,-1],d2:[6,-1],length:6}];
var res2=bimBuildDXF();
assert('legacy linear dim still exports via the original path', res2.stats.line===3&&res2.stats.skipped===0, JSON.stringify(res2.stats));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
