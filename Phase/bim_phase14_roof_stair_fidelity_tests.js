var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3},{id:'lvl-1',name:'Level 1',elev:3,height:3}]};
var UNDO_STACK=[];
function pushUndo(){UNDO_STACK.push(1);}
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
function closeDlg(){}
var TOASTS=[];
function a3dToast(m){TOASTS.push(m);}
function bimEsc(s){return String(s);}
  function bimBuildRoofMesh(footprint,baseY,pitchDeg,slopeDirDeg,thickness){
    var P=sketchCCW(footprint.slice());
    var n=P.length;
    if(n<3)return null;
    var rad=pitchDeg*Math.PI/180;
    var slopeRad=slopeDirDeg*Math.PI/180;
    var dirX=Math.cos(slopeRad),dirZ=Math.sin(slopeRad);
    var i,minProj=Infinity;
    for(i=0;i<n;i++){var proj=P[i][0]*dirX+P[i][1]*dirZ;if(proj<minProj)minProj=proj;}
    var topY=[];
    for(i=0;i<n;i++){var proj=P[i][0]*dirX+P[i][1]*dirZ;topY.push(baseY+(proj-minProj)*Math.tan(rad));}
    var v=[],f=[];
    for(i=0;i<n;i++)v.push([P[i][0],topY[i],P[i][1]]);
    for(i=0;i<n;i++)v.push([P[i][0],topY[i]-thickness,P[i][1]]);
    var tris=earClip(P);
    for(i=0;i<tris.length;i++)f.push([tris[i][2],tris[i][1],tris[i][0]]);
    for(i=0;i<tris.length;i++)f.push([tris[i][0]+n,tris[i][1]+n,tris[i][2]+n]);
    for(i=0;i<n;i++){var j=(i+1)%n;f.push([j,i,i+n,j+n]);}
    return {v:v,f:f};
  }

  function bimBuildRoofGeometry(footprint,baseY,pitchDeg,slopeDirDeg,thickness){
    var m;
    try{m=bimBuildRoofMesh(footprint,baseY,pitchDeg,slopeDirDeg,thickness);}
    catch(eR){console.warn('[BIM] Roof solid build failed: ',eR);return {error:'Roof build failed: '+(eR&&eR.message?eR.message:eR)};}
    if(!m||!m.f||m.f.length<4)return {error:'Roof produced an empty solid: check the source footprint'};
    return {mesh:m,bim:{type:'roof',footprint:footprint.slice(),baseY:baseY,pitch:pitchDeg,slopeDir:slopeDirDeg,thickness:thickness}};
  }

  function bimFindRoofBoundaryAt(pt,y0){
    var b=bimFindRoomBoundaryAt(pt,y0);
    if(!b)return null;
    b.roofBaseY=b.y+(b.wallHeight||0);
    return b;
  }

  function buildRoofSolid(boundary,pitchDeg,slopeDirDeg,thickness){
    var res=bimBuildRoofGeometry(boundary.pts,boundary.roofBaseY,pitchDeg,slopeDirDeg,thickness);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    A3D.counts.roof=(A3D.counts.roof||0)+1;
    res.bim.levelId=A3D.activeLevel;
    res.bim.sourceType=boundary.sourceType;
    res.bim.sourceId=boundary.sourceId;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:'#a3766a',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created ('+pitchDeg+'\u00b0 pitch)');
    return o;
  }

  function bimRebuildRoof(o,newPitch,newDir,newThickness){
    if(!o||!o.bim||o.bim.type!=='roof'||!o.bim.footprint)return false;
    var res=bimBuildRoofGeometry(o.bim.footprint,o.bim.baseY,newPitch,newDir,newThickness);
    if(res.error){a3dToast(res.error);return false;}
    pushUndo();
    res.bim.levelId=o.bim.levelId;
    res.bim.sourceType=o.bim.sourceType;
    res.bim.sourceId=o.bim.sourceId;
    o.mesh=res.mesh;
    o.bim=res.bim;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
  }

  function bimWeldMesh(rawFaces){
    var vm={},verts=[],faces=[],i,j;
    function vid(p){
      var k=p[0].toFixed(5)+','+p[1].toFixed(5)+','+p[2].toFixed(5);
      if(vm[k]===undefined){vm[k]=verts.length;verts.push(p);}
      return vm[k];
    }
    for(i=0;i<rawFaces.length;i++){
      var f=[];
      for(j=0;j<rawFaces[i].length;j++)f.push(vid(rawFaces[i][j]));
      faces.push(f);
    }
    return {v:verts,f:faces};
  }

  function bimBuildStairMesh(startXZ,dirXZ,width,baseY,numSteps,riserH,treadD){
    var nx=-dirXZ[1],nz=dirXZ[0],hw=width/2;
    function pt(run,rise,side){
      var px=startXZ[0]+dirXZ[0]*run,pz=startXZ[1]+dirXZ[1]*run;
      return [px+nx*hw*side,baseY+rise,pz+nz*hw*side];
    }
    var raw=[],i,sd;
    var maxRun=numSteps*treadD,maxRise=numSteps*riserH;
    for(sd=-1;sd<=1;sd+=2){
      for(i=0;i<numSteps;i++){
        var runA=i*treadD,runB=(i+1)*treadD,riseHere=(i+1)*riserH,risePrev=i*riserH;
        var bl=pt(runA,0,sd),br=pt(runB,0,sd),tr=pt(runB,riseHere,sd),tl=pt(runA,riseHere,sd);
        if(i===0){
          if(sd<0){raw.push([bl,br,tr]);raw.push([bl,tr,tl]);}
          else{raw.push([bl,tr,br]);raw.push([bl,tl,tr]);}
        }else{
          var ml=pt(runA,risePrev,sd);
          if(sd<0){raw.push([bl,br,tr]);raw.push([bl,tr,ml]);raw.push([ml,tr,tl]);}
          else{raw.push([bl,tr,br]);raw.push([bl,ml,tr]);raw.push([ml,tl,tr]);}
        }
      }
    }
    for(i=0;i<numSteps;i++){
      var runA3=i*treadD,runB3=(i+1)*treadD;
      raw.push([pt(runA3,0,-1),pt(runB3,0,-1),pt(runB3,0,1),pt(runA3,0,1)]);
    }
    for(i=0;i<numSteps;i++){
      var runA2=i*treadD,runB2=(i+1)*treadD,riseHere2=(i+1)*riserH,risePrev2=i*riserH;
      raw.push([pt(runA2,riseHere2,-1),pt(runB2,riseHere2,-1),pt(runB2,riseHere2,1),pt(runA2,riseHere2,1)]);
      raw.push([pt(runA2,risePrev2,-1),pt(runA2,riseHere2,-1),pt(runA2,riseHere2,1),pt(runA2,risePrev2,1)]);
    }
    raw.push([pt(maxRun,0,-1),pt(maxRun,maxRise,-1),pt(maxRun,maxRise,1),pt(maxRun,0,1)]);
    return bimWeldMesh(raw);
  }

  function bimBuildStairGeometry(startXZ,dirXZ,width,baseY,totalRise,targetRiserH,treadD){
    if(!(totalRise>0)||!(targetRiserH>0)||!(treadD>0))return {error:'Stair needs a positive rise, riser height, and tread depth'};
    var numSteps=Math.max(1,Math.round(totalRise/targetRiserH));
    var riserH=totalRise/numSteps;
    var m;
    try{m=bimBuildStairMesh(startXZ,dirXZ,width,baseY,numSteps,riserH,treadD);}
    catch(eS){console.warn('[BIM] Stair solid build failed: ',eS);return {error:'Stair build failed: '+(eS&&eS.message?eS.message:eS)};}
    if(!m||!m.f||m.f.length<4)return {error:'Stair produced an empty solid'};
    return {mesh:m,bim:{type:'stair',start:startXZ,dir:dirXZ,width:width,baseY:baseY,numSteps:numSteps,riserH:riserH,treadD:treadD,totalRise:totalRise,totalRun:numSteps*treadD}};
  }

  function buildStairSolid(startXZ,dirXZ,width,baseY,totalRise,targetRiserH,treadD,targetLvl){
    var res=bimBuildStairGeometry(startXZ,dirXZ,width,baseY,totalRise,targetRiserH,treadD);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    A3D.counts.stair=(A3D.counts.stair||0)+1;
    res.bim.levelId=A3D.activeLevel;
    res.bim.targetLevelId=targetLvl?targetLvl.id:null;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Stair_'+A3D.counts.stair,col:'#8a8f96',pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:A3D.activeLayer};
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created ('+res.bim.numSteps+' steps)');
    return o;
  }

  function bimFindRoomBoundaryAt(pt,y0){
    var candidates=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3){
        if(Math.abs(o.bim.baseY-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.bim.innerLoop))candidates.push({pts:o.bim.innerLoop.slice(),y:o.bim.baseY,sourceType:'wall',sourceId:o.id,wallHeight:o.bim.height});
      }else if(o.t==='sketch'&&o.closed!==false&&o.pts&&o.pts.length>=3){
        if(Math.abs(o.y-y0)>0.5)continue;
        if(bimPointInPoly(pt,o.pts))candidates.push({pts:o.pts.slice(),y:o.y,sourceType:'sketch',sourceId:o.id});
      }
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
    return candidates[0];
  }

  function bimPointInPoly(pt,poly){
    var x=pt[0],z=pt[1],inside=false,i,j;
    for(i=0,j=poly.length-1;i<poly.length;j=i++){
      var xi=poly[i][0],zi=poly[i][1],xj=poly[j][0],zj=poly[j][1];
      var intersect=((zi>z)!==(zj>z))&&(x<(xj-xi)*(z-zi)/(zj-zi)+xi);
      if(intersect)inside=!inside;
    }
    return inside;
  }

  function bimPolyArea(poly){
    var a=0,i,n=poly.length;
    for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
    return Math.abs(a)/2;
  }

  function bimLayerOf(o){
    var id=o.layer||A3D.activeLayer,i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].id===id)return A3D.layers[i];
    return A3D.layers[0]||null;
  }

  function bimGetActiveLevel(){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)return A3D.levels[i];
    return A3D.levels[0]||{id:'lvl-0',name:'Level 0',elev:0,height:3};
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

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

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

// ---- 1. Roof detected from a REAL mitered closed wall, sits on top of wall height ----
var wallRes=bimBuildWallGeometry([[0,0],[6,0],[6,4],[0,4]],0,3,0.3,'center',true);
var wallObj={id:'wall-1',t:'solid',bim:wallRes.bim,mesh:wallRes.mesh,layer:'layer-0'};
A3D.objs=[wallObj];
var roofBoundary=bimFindRoofBoundaryAt([3,2],0);
assert('roof boundary detection finds the wall', !!roofBoundary);
assert('roof base elevation = wall baseY + wall height (sits ON TOP, not at floor level)',
  roofBoundary&&roofBoundary.roofBaseY===3, roofBoundary&&roofBoundary.roofBaseY);

var roof=buildRoofSolid(roofBoundary,25,0,0.15);
assert('buildRoofSolid creates a real solid object', A3D.objs.length===2&&A3D.objs[1].bim.type==='roof');
assert('roof mesh is watertight', checkWatertight(roof.mesh)===0, checkWatertight(roof.mesh));
assert('roof gets an auto-incrementing name', roof.name==='Roof_1');
assert('creating a roof pushes exactly one undo snapshot', UNDO_STACK.length===1);

// flat roof (pitch=0) sanity: all top vertices at the same Y
var flatBoundary=bimFindRoofBoundaryAt([3,2],0);
UNDO_STACK.length=0;
var flatRoof=buildRoofSolid(flatBoundary,0,0,0.15);
var topYs=flatRoof.mesh.v.filter(function(v){return v[1]>2.9;}).map(function(v){return v[1];});
assert('flat roof (pitch=0) has a uniform top elevation', topYs.every(function(y){return Math.abs(y-3)<1e-6;}));

// ---- 2. Roof editing via Properties-panel path (bimRebuildRoof) ----
UNDO_STACK.length=0;
var rebuildOk=bimRebuildRoof(roof,35,90,0.2);
assert('bimRebuildRoof (Properties panel path) succeeds and regenerates a watertight mesh',
  rebuildOk===true&&checkWatertight(roof.mesh)===0);
assert('bimRebuildRoof updates the stored pitch/direction/thickness', roof.bim.pitch===35&&roof.bim.slopeDir===90&&roof.bim.thickness===0.2);

// ---- 3. Roof duplication offsets the footprint and rebuilds real geometry ----
var roofDup=bimDuplicateObject(roof,5,0);
assert('duplicating a roof produces a distinct real object with a rebuilt mesh', roofDup&&roofDup.id!==roof.id&&checkWatertight(roofDup.mesh)===0);
assert('duplicated roof footprint is offset by (5,0)', roofDup.bim.footprint[0][0]===roof.bim.footprint[0][0]+5);

// ---- 4. Stair build end to end, correct rise/run derivation ----
UNDO_STACK.length=0;
var stair=buildStairSolid([0,0],[1,0],1.1,0,3.0,0.178,0.28,A3D.levels[1]);
assert('buildStairSolid creates a real solid object', stair&&stair.bim.type==='stair');
assert('stair mesh is watertight (real embedded pipeline, not just the prototype)', checkWatertight(stair.mesh)===0, checkWatertight(stair.mesh));
assert('stair total rise exactly matches level difference (3.0)', Math.abs(stair.bim.totalRise-3.0)<1e-9);
assert('stair riser height stays close to the 0.178 target', Math.abs(stair.bim.riserH-0.178)<0.02);
assert('stair records its target level id', stair.bim.targetLevelId==='lvl-1');
assert('creating a stair pushes exactly one undo snapshot', UNDO_STACK.length===1);

// ---- 5. Stair duplication offsets the start point and rebuilds ----
var stairDup=bimDuplicateObject(stair,3,3);
assert('duplicating a stair produces a distinct watertight object', stairDup&&stairDup.id!==stair.id&&checkWatertight(stairDup.mesh)===0);
assert('duplicated stair start point is offset by (3,3)', stairDup.bim.start[0]===stair.bim.start[0]+3&&stairDup.bim.start[1]===stair.bim.start[1]+3);
assert('duplicated stair keeps the same direction/rise/step config', stairDup.bim.numSteps===stair.bim.numSteps);

// ---- 6. Error handling: degenerate stair rejected cleanly, not crashed ----
var badStair=bimBuildStairGeometry([0,0],[1,0],1.0,0,0,0.178,0.28);
assert('zero total rise is rejected with an error, not a crash', !!badStair.error);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
