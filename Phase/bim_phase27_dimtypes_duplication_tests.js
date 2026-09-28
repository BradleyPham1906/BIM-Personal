var A3D={objs:[],counts:{},seq:1,layers:[],activeLayer:'L1',activeLevel:'lvl-0',activeViewId:null};
function bimBuildWallGeometry(){return {error:'n/a'};}
function bimBuildFloorGeometry(){return {error:'n/a'};}
function bimBuildColumnGeometry(){return {error:'n/a'};}
  function bimDimKind(o){return (o&&o.dimKind)||'linear';}

  function bimDuplicateObject(o,dx,dz){
    var copy;
    if(o.t==='opening')return null;
    if(o.t==='sketch'){
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pts=o.pts.map(function(p){return [p[0]+dx,p[1]+dz];});
      copy.name=o.name+' copy';
    }else if(o.bim&&o.bim.type==='wall'){
      var newCl=o.bim.centerline.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);
      if(res.error)return null;
      A3D.counts.wall=(A3D.counts.wall||0)+1;
      res.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:o.layer};
    }else if(o.bim&&o.bim.type==='floor'){
      if(!o.bim.profile)return null;
      var newProf=o.bim.profile.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res2=bimBuildFloorGeometry(newProf,o.bim.baseY,o.bim.thickness);
      if(res2.error)return null;
      A3D.counts.floor=(A3D.counts.floor||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Floor_'+A3D.counts.floor,col:o.col,pos:[0,0,0],mesh:res2.mesh,
        bim:{type:'floor',thickness:o.bim.thickness,material:o.bim.material,levelId:o.bim.levelId,baseY:o.bim.baseY,profile:newProf},layer:o.layer};
    }else if(o.bim&&o.bim.type==='column'){
      var newCenter=[o.bim.center[0]+dx,o.bim.center[1]+dz];
      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height);
      if(res3.error)return null;
      A3D.counts.column=(A3D.counts.column||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Column_'+A3D.counts.column,col:o.col,pos:[0,0,0],mesh:res3.mesh,
        bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter},layer:o.layer};
    }else if(o.t==='room'){
      A3D.counts.room=(A3D.counts.room||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:o.col,pos:[0,0,0],
        pts:o.pts.map(function(p){return [p[0]+dx,p[1]+dz];}),y:o.y,area:o.area,levelId:o.levelId,
        sourceType:o.sourceType,sourceId:o.sourceId,layer:o.layer};
    }else if(o.t==='dim'){
      // every dim kind stores different point fields, so offset whichever this one actually has
      // rather than assuming the linear p1/p2/d1/d2 shape (which would throw on angular/radial/leader)
      A3D.counts.dim=(A3D.counts.dim||0)+1;
      var dkD=bimDimKind(o);
      function offP(pt){return [pt[0]+dx,pt[1]+dz];}
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',col:o.col,pos:[0,0,0],
        dimKind:o.dimKind,y:o.y,levelId:o.levelId,layer:o.layer,viewId:o.viewId};
      if(dkD==='linear'){
        copy.name='Dim_'+A3D.counts.dim;
        copy.p1=offP(o.p1);copy.p2=offP(o.p2);copy.d1=offP(o.d1);copy.d2=offP(o.d2);copy.length=o.length;
      }else if(dkD==='angular'){
        copy.name='Angle_'+A3D.counts.dim;
        copy.vertex=offP(o.vertex);copy.ap1=offP(o.ap1);copy.ap2=offP(o.ap2);
        copy.a1=o.a1;copy.sweep=o.sweep;copy.arcRadius=o.arcRadius;copy.degrees=o.degrees;
      }else if(dkD==='radius'||dkD==='diameter'){
        copy.name=(dkD==='diameter'?'Dia_':'Rad_')+A3D.counts.dim;
        copy.center=offP(o.center);copy.dStart=offP(o.dStart);copy.dEdge=offP(o.dEdge);
        copy.radius=o.radius;copy.value=o.value;
      }else if(dkD==='leader'){
        copy.name='Leader_'+A3D.counts.dim;
        copy.anchor=offP(o.anchor);copy.elbow=offP(o.elbow);copy.landing=offP(o.landing);
        copy.label=o.label;copy.ldir=o.ldir;
      }else{
        return null;
      }
    }else if(o.t==='text'){
      A3D.counts.text=(A3D.counts.text||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'text',name:'Text_'+A3D.counts.text,col:o.col,pos:[0,0,0],
        text:o.text,pt:[o.pt[0]+dx,o.pt[1]+dz],y:o.y,levelId:o.levelId,layer:o.layer};
    }else if(o.bim&&o.bim.type==='roof'&&o.bim.footprint){
      var newFoot=o.bim.footprint.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res4=bimBuildRoofGeometry(newFoot,o.bim.baseY,o.bim.pitch,o.bim.slopeDir,o.bim.thickness);
      if(res4.error)return null;
      A3D.counts.roof=(A3D.counts.roof||0)+1;
      res4.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:o.col,pos:[0,0,0],mesh:res4.mesh,bim:res4.bim,layer:o.layer};
    }else if(o.bim&&o.bim.type==='stair'){
      var newStart=[o.bim.start[0]+dx,o.bim.start[1]+dz];
      var res5=bimBuildStairGeometry(newStart,o.bim.dir,o.bim.width,o.bim.baseY,o.bim.totalRise,o.bim.riserH,o.bim.treadD);
      if(res5.error)return null;
      A3D.counts.stair=(A3D.counts.stair||0)+1;
      res5.bim.levelId=o.bim.levelId;
      res5.bim.targetLevelId=o.bim.targetLevelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Stair_'+A3D.counts.stair,col:o.col,pos:[0,0,0],mesh:res5.mesh,bim:res5.bim,layer:o.layer};
    }else{
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pos=[o.pos[0]+dx,o.pos[1],o.pos[2]+dz];
      copy.name=o.name+' copy';
    }
    return copy;
  }

  function bimComputeTransformedGeometry(o,transformPt){
    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};
    if(o.t==='room')return {kind:'room',pts:o.pts.map(transformPt),y:o.y,area:o.area};
    if(o.t==='text')return {kind:'text',pt:transformPt(o.pt),y:o.y,text:o.text};
    if(o.t==='dim'){
      if(bimDimKind(o)!=='linear')return {error:'Only linear dimensions support Mirror/Rotate for now \u2014 angular/radial/leader dims store angles that need extra handling'};
      var np1=transformPt(o.p1),np2=transformPt(o.p2),nd1=transformPt(o.d1),nd2=transformPt(o.d2);
      return {kind:'dim',p1:np1,p2:np2,d1:nd1,d2:nd2,length:o.length,y:o.y};
    }
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      var newCl=o.bim.centerline.map(transformPt);
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed);
      if(res.error)return {error:res.error};
      return {kind:'wall',mesh:res.mesh,bim:res.bim};
    }
    if(o.bim&&o.bim.type==='floor'){
      if(!o.bim.profile)return {error:'Imported floor has no editable profile'};
      var newProf=o.bim.profile.map(transformPt);
      var res2=bimBuildFloorGeometry(newProf,o.bim.baseY,o.bim.thickness);
      if(res2.error)return {error:res2.error};
      return {kind:'floor',mesh:res2.mesh,bim:res2.bim};
    }
    if(o.bim&&o.bim.type==='column'){
      var newCenter=transformPt(o.bim.center);
      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height);
      if(res3.error)return {error:res3.error};
      return {kind:'column',mesh:res3.mesh,bim:{type:'column',width:o.bim.width,depth:o.bim.depth,height:o.bim.height,baseY:o.bim.baseY,levelId:o.bim.levelId,center:newCenter}};
    }
    if(o.bim&&(o.bim.type==='roof'||o.bim.type==='stair')){
      return {error:'Roof and Stair do not support Mirror/Rotate yet (their direction/slope parameters need extra handling) \u2014 redraw instead'};
    }
    if(o.t==='opening'){
      return {error:'Openings move with their host wall and cannot be transformed independently'};
    }
    if(o.mesh){
      var newV=o.mesh.v.map(function(v3){var p2=transformPt([v3[0],v3[2]]);return [p2[0],v3[1],p2[1]];});
      return {kind:'mesh',mesh:{v:newV,f:o.mesh.f}};
    }
    if(o.pos){
      var npz=transformPt([o.pos[0],o.pos[2]]);
      return {kind:'pos',pos:[npz[0],o.pos[1],npz[1]]};
    }
    return {error:'This object type cannot be transformed'};
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

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

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b){return Math.abs(a-b)<1e-9;}

var lin={t:'dim',name:'Dim_1',p1:[0,0],p2:[6,0],d1:[0,-1],d2:[6,-1],length:6,y:0,layer:'L1'};
var ang={t:'dim',dimKind:'angular',name:'Angle_1',vertex:[0,0],ap1:[1,0],ap2:[0,1],a1:0,sweep:1.5707963,arcRadius:0.6,degrees:90,y:0,layer:'L1'};
var rad={t:'dim',dimKind:'radius',name:'Rad_1',center:[0,0],dStart:[0,0],dEdge:[5,0],radius:5,value:5,y:0,layer:'L1'};
var ld={t:'dim',dimKind:'leader',name:'Leader_1',anchor:[0,0],elbow:[2,2],landing:[2.5,2],label:'Note',ldir:1,y:0,layer:'L1'};

var dl=bimDuplicateObject(lin,3,4);
assert('linear dim still duplicates correctly (unchanged behavior)', dl&&approx(dl.p1[0],3)&&approx(dl.d2[1],3), dl&&JSON.stringify([dl.p1,dl.d2]));

var da=null,errA=null;
try{da=bimDuplicateObject(ang,3,4);}catch(e){errA=e;}
assert('duplicating an ANGULAR dim no longer throws', !errA, errA&&errA.message);
assert('duplicated angular dim offsets its vertex and rays', da&&approx(da.vertex[0],3)&&approx(da.ap1[0],4)&&approx(da.ap2[1],5));
assert('duplicated angular dim preserves the measured angle', da&&da.degrees===90);

var dr=null,errR=null;
try{dr=bimDuplicateObject(rad,3,4);}catch(e){errR=e;}
assert('duplicating a RADIUS dim no longer throws', !errR, errR&&errR.message);
assert('duplicated radius dim offsets center and edge, preserves radius', dr&&approx(dr.center[0],3)&&approx(dr.dEdge[0],8)&&dr.radius===5);

var dd=null,errL=null;
try{dd=bimDuplicateObject(ld,3,4);}catch(e){errL=e;}
assert('duplicating a LEADER no longer throws', !errL, errL&&errL.message);
assert('duplicated leader offsets all points and keeps its text', dd&&approx(dd.anchor[0],3)&&approx(dd.elbow[1],6)&&dd.label==='Note');

assert('duplicated non-linear dims keep their dimKind', da.dimKind==='angular'&&dr.dimKind==='radius'&&dd.dimKind==='leader');

// transform path declines non-linear rather than corrupting
var tLin=bimComputeTransformedGeometry(lin,function(p){return [p[0]+1,p[1]+1];});
assert('mirror/rotate still works on linear dims', tLin&&tLin.kind==='dim');
var tAng=bimComputeTransformedGeometry(ang,function(p){return [p[0]+1,p[1]+1];});
assert('mirror/rotate declines non-linear dims with a clear message instead of corrupting them', tAng&&!!tAng.error, JSON.stringify(tAng));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
