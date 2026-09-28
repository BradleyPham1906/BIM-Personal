var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}]};
var UNDO_STACK=[];
function pushUndo(){UNDO_STACK.push(1);}
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
function closeDlg(){}
var TOASTS=[];
function a3dToast(m){TOASTS.push(m);}
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

  function bimMirrorPoint(pt,P1,P2){
    var dx=P2[0]-P1[0],dz=P2[1]-P1[1];
    var len=Math.sqrt(dx*dx+dz*dz)||1e-9;
    var ux=dx/len,uz=dz/len;
    var vx=pt[0]-P1[0],vz=pt[1]-P1[1];
    var proj=vx*ux+vz*uz;
    var perpX=vx-proj*ux,perpZ=vz-proj*uz;
    return [P1[0]+proj*ux-perpX,P1[1]+proj*uz-perpZ];
  }

  function bimRotatePoint(pt,center,angleRad){
    var vx=pt[0]-center[0],vz=pt[1]-center[1];
    var c=Math.cos(angleRad),s=Math.sin(angleRad);
    return [center[0]+vx*c-vz*s,center[1]+vx*s+vz*c];
  }

  function bimLineLineIntersect(a1,a2,b1,b2){
    var d1x=a2[0]-a1[0],d1z=a2[1]-a1[1];
    var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
    var denom=d1x*d2z-d1z*d2x;
    if(Math.abs(denom)<1e-9)return null;
    var dx=b1[0]-a1[0],dz=b1[1]-a1[1];
    var t=(dx*d2z-dz*d2x)/denom;
    return [a1[0]+d1x*t,a1[1]+d1z*t];
  }

  function bimComputeTransformedGeometry(o,transformPt){
    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};
    if(o.t==='room')return {kind:'room',pts:o.pts.map(transformPt),y:o.y,area:o.area};
    if(o.t==='text')return {kind:'text',pt:transformPt(o.pt),y:o.y,text:o.text};
    if(o.t==='dim'){
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

  function bimMirrorObject(o,P1,P2){
    var transformPt=function(p){return bimMirrorPoint(p,P1,P2);};
    var g=bimComputeTransformedGeometry(o,transformPt);
    if(g.error)return g;
    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:[0,0,0],col:o.col,layer:o.layer};
    if(g.kind==='sketch'){copy.t='sketch';copy.pts=g.pts;copy.y=g.y;copy.closed=o.closed;A3D.counts.sketch=(A3D.counts.sketch||0)+1;copy.name=(o.name||'Sketch')+' mirror';}
    else if(g.kind==='room'){A3D.counts.room=(A3D.counts.room||0)+1;copy.t='room';copy.name='Room_'+A3D.counts.room;copy.pts=g.pts;copy.y=g.y;copy.area=g.area;copy.levelId=o.levelId;copy.sourceType=o.sourceType;copy.sourceId=o.sourceId;}
    else if(g.kind==='text'){A3D.counts.text=(A3D.counts.text||0)+1;copy.t='text';copy.name='Text_'+A3D.counts.text;copy.text=g.text;copy.pt=g.pt;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='dim'){A3D.counts.dim=(A3D.counts.dim||0)+1;copy.t='dim';copy.name='Dim_'+A3D.counts.dim;copy.p1=g.p1;copy.p2=g.p2;copy.d1=g.d1;copy.d2=g.d2;copy.length=g.length;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='wall'){A3D.counts.wall=(A3D.counts.wall||0)+1;copy.t='solid';copy.name='Wall_'+A3D.counts.wall;copy.mesh=g.mesh;copy.bim=g.bim;copy.bim.levelId=o.bim.levelId;}
    else if(g.kind==='floor'){A3D.counts.floor=(A3D.counts.floor||0)+1;copy.t='solid';copy.name='Floor_'+A3D.counts.floor;copy.mesh=g.mesh;copy.bim=g.bim;copy.bim.levelId=o.bim.levelId;}
    else if(g.kind==='column'){A3D.counts.column=(A3D.counts.column||0)+1;copy.t='solid';copy.name='Column_'+A3D.counts.column;copy.mesh=g.mesh;copy.bim=g.bim;}
    else if(g.kind==='mesh'){copy.t=o.t;copy.name=o.name+' mirror';copy.mesh=g.mesh;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' mirror';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    return copy;
  }

  function bimMirrorSelection(ids,P1,P2){
    pushUndo();
    var newIds=[],i,failCount=0;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var copy=bimMirrorObject(o,P1,P2);
      if(copy&&!copy.error){A3D.objs.push(copy);newIds.push(copy.id);}
      else failCount++;
    }
    if(!newIds.length){a3dToast('Mirror failed: unsupported object type(s)');return;}
    A3D.selSet=newIds;A3D.sel=newIds[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Mirrored '+newIds.length+' object(s)'+(failCount?' ('+failCount+' skipped)':''));
  }

  function bimRotateObjectInPlace(o,center,angleRad){
    var transformPt=function(p){return bimRotatePoint(p,center,angleRad);};
    var g=bimComputeTransformedGeometry(o,transformPt);
    if(g.error)return false;
    if(g.kind==='sketch'){o.pts=g.pts;}
    else if(g.kind==='room'){o.pts=g.pts;}
    else if(g.kind==='text'){o.pt=g.pt;}
    else if(g.kind==='dim'){o.p1=g.p1;o.p2=g.p2;o.d1=g.d1;o.d2=g.d2;}
    else if(g.kind==='wall'||g.kind==='floor'||g.kind==='column'){o.mesh=g.mesh;o.bim=Object.assign(o.bim,g.bim);}
    else if(g.kind==='mesh'){o.mesh=g.mesh;}
    else if(g.kind==='pos'){o.pos=g.pos;}
    return true;
  }

  function bimRotateSelection(ids,center,angleRad){
    var lockedIds=ids.filter(function(id){var oo=objById(id);return oo&&bimIsLocked(oo);});
    var rotatable=ids.filter(function(id){var oo=objById(id);return oo&&!bimIsLocked(oo);});
    if(!rotatable.length){a3dToast('Selected object(s) are locked \u2014 unlock to rotate');return;}
    pushUndo();
    var ok=0,fail=0,i;
    for(i=0;i<rotatable.length;i++){
      var o=objById(rotatable[i]);
      if(!o)continue;
      if(bimRotateObjectInPlace(o,center,angleRad))ok++;else fail++;
    }
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Rotated '+ok+' object(s)'+(fail?' ('+fail+' skipped)':'')+(lockedIds.length?' ('+lockedIds.length+' locked, skipped)':''));
  }

  function bimBuildPolarArray(ids,center,n,totalAngleRad){
    pushUndo();
    var newIds=[],i,k,fail=0;
    var stepAngle=totalAngleRad/n;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      for(k=1;k<n;k++){
        var ang=stepAngle*k;
        var transformPt=function(p){return bimRotatePoint(p,center,ang);};
        var g=bimComputeTransformedGeometry(o,transformPt);
        if(g.error){fail++;continue;}
        var built=bimBuildArrayCopyFromGeometry(o,g);
        if(built){A3D.objs.push(built);newIds.push(built.id);}else fail++;
      }
    }
    if(!newIds.length){a3dToast('Array failed: unsupported object type(s)');return;}
    A3D.selSet=ids.concat(newIds);
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Polar array created '+newIds.length+' cop'+(newIds.length===1?'y':'ies')+(fail?' ('+fail+' skipped)':''));
  }

  function bimBuildArrayCopyFromGeometry(o,g){
    var copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),pos:[0,0,0],col:o.col,layer:o.layer};
    if(g.kind==='sketch'){copy.t='sketch';copy.pts=g.pts;copy.y=g.y;copy.closed=o.closed;copy.name=(o.name||'Sketch')+' copy';}
    else if(g.kind==='room'){A3D.counts.room=(A3D.counts.room||0)+1;copy.t='room';copy.name='Room_'+A3D.counts.room;copy.pts=g.pts;copy.y=g.y;copy.area=g.area;copy.levelId=o.levelId;copy.sourceType=o.sourceType;copy.sourceId=o.sourceId;}
    else if(g.kind==='text'){A3D.counts.text=(A3D.counts.text||0)+1;copy.t='text';copy.name='Text_'+A3D.counts.text;copy.text=g.text;copy.pt=g.pt;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='dim'){A3D.counts.dim=(A3D.counts.dim||0)+1;copy.t='dim';copy.name='Dim_'+A3D.counts.dim;copy.p1=g.p1;copy.p2=g.p2;copy.d1=g.d1;copy.d2=g.d2;copy.length=g.length;copy.y=g.y;copy.levelId=o.levelId;}
    else if(g.kind==='wall'){A3D.counts.wall=(A3D.counts.wall||0)+1;copy.t='solid';copy.name='Wall_'+A3D.counts.wall;copy.mesh=g.mesh;copy.bim=g.bim;copy.bim.levelId=o.bim.levelId;}
    else if(g.kind==='floor'){A3D.counts.floor=(A3D.counts.floor||0)+1;copy.t='solid';copy.name='Floor_'+A3D.counts.floor;copy.mesh=g.mesh;copy.bim=g.bim;copy.bim.levelId=o.bim.levelId;}
    else if(g.kind==='column'){A3D.counts.column=(A3D.counts.column||0)+1;copy.t='solid';copy.name='Column_'+A3D.counts.column;copy.mesh=g.mesh;copy.bim=g.bim;}
    else if(g.kind==='mesh'){copy.t=o.t;copy.name=o.name+' copy';copy.mesh=g.mesh;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' copy';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}
    else return null;
    return copy;
  }

  function bimFindClosestWallEndpoints(wallA,wallB){
    var clA=wallA.bim.centerline,clB=wallB.bim.centerline;
    if(wallA.bim.closed||wallB.bim.closed)return null;
    if(clA.length<2||clB.length<2)return null;
    var endsA=[{idx:0,pt:clA[0]},{idx:clA.length-1,pt:clA[clA.length-1]}];
    var endsB=[{idx:0,pt:clB[0]},{idx:clB.length-1,pt:clB[clB.length-1]}];
    var best=null,bestDist=Infinity,ea,eb;
    for(ea=0;ea<2;ea++)for(eb=0;eb<2;eb++){
      var dx=endsA[ea].pt[0]-endsB[eb].pt[0],dz=endsA[ea].pt[1]-endsB[eb].pt[1];
      var d=Math.sqrt(dx*dx+dz*dz);
      if(d<bestDist){bestDist=d;best={a:endsA[ea],b:endsB[eb],dist:d};}
    }
    return best;
  }

  function bimJoinWalls(wallA,wallB){
    if(!wallA.bim||wallA.bim.type!=='wall'||!wallA.bim.centerline)return {error:'First object is not an editable wall'};
    if(!wallB.bim||wallB.bim.type!=='wall'||!wallB.bim.centerline)return {error:'Second object is not an editable wall'};
    var ends=bimFindClosestWallEndpoints(wallA,wallB);
    if(!ends)return {error:'Both walls must be open (non-closed) polylines to join'};
    var clA=wallA.bim.centerline.slice(),clB=wallB.bim.centerline.slice();
    var aNeighborIdx=ends.a.idx===0?1:ends.a.idx-1;
    var bNeighborIdx=ends.b.idx===0?1:ends.b.idx-1;
    var aNeighbor=clA[aNeighborIdx],aEnd=clA[ends.a.idx];
    var bNeighbor=clB[bNeighborIdx],bEnd=clB[ends.b.idx];
    var ip=bimLineLineIntersect(aNeighbor,aEnd,bNeighbor,bEnd);
    if(!ip)return {error:'Wall directions are parallel; cannot compute a corner intersection'};
    clA[ends.a.idx]=ip;
    clB[ends.b.idx]=ip;
    var resA=bimBuildWallGeometry(clA,wallA.bim.baseY,wallA.bim.height,wallA.bim.thickness,wallA.bim.align,false);
    var resB=bimBuildWallGeometry(clB,wallB.bim.baseY,wallB.bim.height,wallB.bim.thickness,wallB.bim.align,false);
    if(resA.error)return {error:'Wall A: '+resA.error};
    if(resB.error)return {error:'Wall B: '+resB.error};
    return {meshA:resA.mesh,bimA:resA.bim,meshB:resB.mesh,bimB:resB.bim,joinPoint:ip};
  }

  function applyWallJoin(){
    var a=objById(A3D.sel),b=objById(A3D.sel2);
    if(!a||!b||a===b){a3dToast('Join Walls needs two walls: click the first, Ctrl+click the second');return;}
    if(bimIsLocked(a)||bimIsLocked(b)){a3dToast('One of the selected walls is locked \u2014 unlock to join');return;}
    var res=bimJoinWalls(a,b);
    if(res.error){a3dToast('Join failed: '+res.error);return;}
    pushUndo();
    a.mesh=res.meshA;a.bim=res.bimA;
    b.mesh=res.meshB;b.bim=res.bimB;
    refreshTree();paint();saveSoon();
    a3dToast('Walls joined at their corner');
  }

  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed){
    var off=bimAlignOffsets(thickness,align);
    var cleanPts=[pts[0]],i;
    for(i=1;i<pts.length;i++){
      var prevp=cleanPts[cleanPts.length-1],curp=pts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }
    if(closed&&cleanPts.length>1){
      var firstp=cleanPts[0],lastp=cleanPts[cleanPts.length-1];
      if(Math.abs(firstp[0]-lastp[0])<1e-6&&Math.abs(firstp[1]-lastp[1])<1e-6)cleanPts.pop();
    }
    if(cleanPts.length<2)return {error:'Wall needs at least 2 distinct points'};
    var basePts=closed?sketchCCW(cleanPts):cleanPts;
    var innerRing,outerRing,nm;
    try{
      innerRing=bimOffsetRing(basePts,off.dLeft,!!closed);
      outerRing=bimOffsetRing(basePts,-off.dRight,!!closed);
      nm=bimBuildWallRibbonMesh(outerRing,innerRing,y0,height,!!closed);
    }catch(eW){
      console.warn('[BIM] Wall solid build failed: ',eW);
      return {error:'Wall build failed: '+(eW&&eW.message?eW.message:eW)};
    }
    if(!nm||!nm.f||nm.f.length<4)return {error:'Wall produced an empty solid: check the centerline points'};
    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
    if(closed){
      bim.innerLoop=innerRing;
      bim.outerLoop=outerRing;
    }
    return {mesh:nm,bim:bim};
  }

  function bimBuildFloorGeometry(profPts,y,thickness){
    var m;
    try{m=padMesh(profPts,y-thickness,thickness);}
    catch(eF){console.warn('[BIM] Floor solid build failed: ',eF);return {error:'Floor build failed: '+(eF&&eF.message?eF.message:eF)};}
    if(!m||!m.f||m.f.length<4)return {error:'Floor produced an empty solid: check the source profile'};
    return {mesh:m};
  }

  function bimBuildColumnGeometry(center,y0,w,dep,h){
    var hw=w/2,hd=dep/2;
    var quad=[[center[0]-hw,center[1]-hd],[center[0]+hw,center[1]-hd],[center[0]+hw,center[1]+hd],[center[0]-hw,center[1]+hd]];
    var mesh;
    try{mesh=padMesh(sketchCCW(quad),y0,h);}
    catch(eC){return {error:'Column build failed: '+(eC&&eC.message?eC.message:eC)};}
    if(!mesh||!mesh.f||mesh.f.length<4)return {error:'Column produced an empty solid'};
    return {mesh:mesh};
  }

  function bimIsLocked(o){return !!(o&&o.locked);}

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

  function bimOffsetRing(pts,dist,closed){
    var n=pts.length,out=[],i;
    for(i=0;i<n;i++){
      if(!closed&&(i===0||i===n-1)){
        var a=i===0?pts[0]:pts[n-2],b=i===0?pts[1]:pts[n-1];
        var nrm=bimSegNormal(a,b);
        out.push([pts[i][0]+nrm[0]*dist,pts[i][1]+nrm[1]*dist]);
        continue;
      }
      var prev=pts[(i-1+n)%n],cur=pts[i],next=pts[(i+1)%n];
      var n1=bimSegNormal(prev,cur),n2=bimSegNormal(cur,next);
      var mx=n1[0]+n2[0],mz=n1[1]+n2[1];
      var mlen=Math.sqrt(mx*mx+mz*mz)||1;mx/=mlen;mz/=mlen;
      var cosH=(n1[0]*mx+n1[1]*mz);
      var scale=cosH>0.15?1/cosH:1;scale=Math.min(scale,4);
      out.push([cur[0]+mx*dist*scale,cur[1]+mz*dist*scale]);
    }
    return out;
  }

  function bimAlignOffsets(thickness,align){
    if(align==='left')return {dLeft:0,dRight:thickness};
    if(align==='right')return {dLeft:thickness,dRight:0};
    return {dLeft:thickness/2,dRight:thickness/2};
  }

  function bimSegNormal(a,b){
    var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
    return [-dz/len,dx/len];
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

  function bimBuildWallRibbonMesh(outer,inner,y0,height,closed){
    var n=outer.length;
    if(n!==inner.length||n<2)return null;
    var v=[],f=[],i;
    var segCount=closed?n:n-1;
    for(i=0;i<n;i++)v.push([outer[i][0],y0,outer[i][1]]);
    for(i=0;i<n;i++)v.push([outer[i][0],y0+height,outer[i][1]]);
    for(i=0;i<n;i++)v.push([inner[i][0],y0,inner[i][1]]);
    for(i=0;i<n;i++)v.push([inner[i][0],y0+height,inner[i][1]]);
    var OB=0,OT=n,IB=2*n,IT=3*n;
    for(i=0;i<segCount;i++){
      var j=(i+1)%n;
      f.push([OB+j,OB+i,OT+i,OT+j]);
      f.push([IB+i,IB+j,IT+j,IT+i]);
      f.push([OT+i,OT+j,IT+j,IT+i]);
      f.push([OB+j,OB+i,IB+i,IB+j]);
    }
    if(!closed){
      f.push([OB+0,IB+0,IT+0,OT+0]);
      var last=n-1;
      f.push([IB+last,OB+last,OT+last,IT+last]);
    }
    return {v:v,f:f};
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function checkWatertight(mesh){
  var edgeCount={},i,j;
  for(i=0;i<mesh.f.length;i++){
    var fc=mesh.f[i];
    for(j=0;j<fc.length;j++){
      var a=fc[j],b=fc[(j+1)%fc.length];
      var k=a<b?a+'_'+b:b+'_'+a;
      edgeCount[k]=(edgeCount[k]||0)+1;
    }
  }
  var bad=0,k2;
  for(k2 in edgeCount)if(edgeCount[k2]!==2)bad++;
  return bad;
}

var wallRes=bimBuildWallGeometry([[0,0],[6,0],[6,4],[0,4]],0,3,0.3,'center',true);
var wallObj={id:'w1',t:'solid',name:'Wall_1',bim:wallRes.bim,mesh:wallRes.mesh,pos:[0,0,0],layer:'layer-0'};
A3D.objs=[wallObj];
A3D.selSet=['w1'];
UNDO_STACK.length=0;
bimMirrorSelection(['w1'],[10,0],[10,1]);
assert('mirror creates a new object, leaving the original untouched', A3D.objs.length===2);
assert('mirror pushes exactly one undo snapshot for the whole operation', UNDO_STACK.length===1);
var mirroredWall=A3D.objs[1];
assert('mirrored wall mesh is watertight', checkWatertight(mirroredWall.mesh)===0, checkWatertight(mirroredWall.mesh));
assert('mirrored wall got a new distinct id', mirroredWall.id!==wallObj.id);
assert('original wall object is completely unchanged', A3D.objs[0].bim.centerline[0][0]===wallRes.bim.centerline[0][0]);

var roomObj={id:'r1',t:'room',name:'Room_1',pts:[[0,0],[4,0],[4,2],[0,2]],y:0,area:8,pos:[0,0,0],layer:'layer-0'};
A3D.objs=[roomObj];
UNDO_STACK.length=0;
bimRotateSelection(['r1'],[2,1],Math.PI/2);
assert('rotate modifies the object in place (no new object created)', A3D.objs.length===1);
assert('rotate pushes exactly one undo snapshot', UNDO_STACK.length===1);
assert('rotated room preserves its area (rigid transform)', A3D.objs[0].area===8);

var lockedRoom={id:'r2',t:'room',name:'Room_2',pts:[[0,0],[2,0],[2,2],[0,2]],y:0,area:4,pos:[0,0,0],locked:true,layer:'layer-0'};
A3D.objs=[lockedRoom];
TOASTS.length=0;UNDO_STACK.length=0;
bimRotateSelection(['r2'],[1,1],Math.PI/4);
assert('rotating a locked-only selection is refused, no undo pushed', UNDO_STACK.length===0);
assert('locked-object rotation attempt produces an explanatory toast', TOASTS.some(function(t){return t.indexOf('locked')>=0;}));

var colRes=bimBuildColumnGeometry([2,0],0,0.4,0.4,3);
assert('setup: column geometry builds correctly (harness dependency check)', !colRes.error, JSON.stringify(colRes.error));
var colObj={id:'c1',t:'solid',name:'Column_1',
  bim:{type:'column',width:0.4,depth:0.4,height:3,baseY:0,levelId:'lvl-0',center:[2,0]},
  mesh:colRes.mesh,pos:[0,0,0],layer:'layer-0'};
A3D.objs=[colObj];
UNDO_STACK.length=0;
bimBuildPolarArray(['c1'],[0,0],4,2*Math.PI);
assert('polar array creates exactly 3 new copies (4 total - 1 original)', A3D.objs.length===4);
assert('polar array pushes exactly one undo snapshot for the whole array', UNDO_STACK.length===1);
var allWatertight=A3D.objs.every(function(o){return o.mesh&&checkWatertight(o.mesh)===0;});
assert('every column in the polar array is watertight', allWatertight);
var centers=A3D.objs.map(function(o){return o.bim.center;});
var found90=centers.some(function(c){return Math.abs(c[0]-0)<1e-6&&Math.abs(c[1]-2)<1e-6;});
assert('one of the array copies is at the mathematically correct 90-degree position', found90, JSON.stringify(centers));

var wA=bimBuildWallGeometry([[0,0],[6,0.3]],0,3,0.3,'center',false);
var wB=bimBuildWallGeometry([[6.2,0.3],[6.2,5]],0,3,0.3,'center',false);
var wallObjA={id:'wa',t:'solid',name:'Wall_A',bim:wA.bim,mesh:wA.mesh,pos:[0,0,0],layer:'layer-0'};
var wallObjB={id:'wb',t:'solid',name:'Wall_B',bim:wB.bim,mesh:wB.mesh,pos:[0,0,0],layer:'layer-0'};
A3D.objs=[wallObjA,wallObjB];
A3D.sel='wa';A3D.sel2='wb';
UNDO_STACK.length=0;
applyWallJoin();
assert('applyWallJoin (the real UI entry point) succeeds', UNDO_STACK.length===1);
var endA=wallObjA.bim.centerline[wallObjA.bim.centerline.length-1];
var startB=wallObjB.bim.centerline[0];
assert('after joining, wall A\'s end and wall B\'s start are EXACTLY the same point',
  Math.abs(endA[0]-startB[0])<1e-9&&Math.abs(endA[1]-startB[1])<1e-9, JSON.stringify([endA,startB]));
assert('joined wall A is watertight', checkWatertight(wallObjA.mesh)===0);
assert('joined wall B is watertight', checkWatertight(wallObjB.mesh)===0);

TOASTS.length=0;
A3D.sel='wa';A3D.sel2=null;
applyWallJoin();
assert('joining with only one wall selected is refused with a clear message', TOASTS.some(function(t){return t.indexOf('two walls')>=0;}));

wallObjA.locked=true;
TOASTS.length=0;
A3D.sel='wa';A3D.sel2='wb';
applyWallJoin();
assert('joining is refused if either wall is locked', TOASTS.some(function(t){return t.indexOf('locked')>=0;}));
wallObjA.locked=false;

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
