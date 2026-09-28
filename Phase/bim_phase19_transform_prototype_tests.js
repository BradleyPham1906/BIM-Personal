// (reuse the same wall-building stack from the join test, abbreviated here via require-free copy)
function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
  if(a<0)P.reverse();
  return P;
}
function bimSegNormal(a,b){var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;return [-dz/len,dx/len];}
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
function bimBuildWallRibbonMesh(outer,inner,y0,height,closed){
  var n=outer.length;if(n!==inner.length||n<2)return null;
  var v=[],f=[],i;var segCount=closed?n:n-1;
  for(i=0;i<n;i++)v.push([outer[i][0],y0,outer[i][1]]);
  for(i=0;i<n;i++)v.push([outer[i][0],y0+height,outer[i][1]]);
  for(i=0;i<n;i++)v.push([inner[i][0],y0,inner[i][1]]);
  for(i=0;i<n;i++)v.push([inner[i][0],y0+height,inner[i][1]]);
  var OB=0,OT=n,IB=2*n,IT=3*n;
  for(i=0;i<segCount;i++){
    var j=(i+1)%n;
    f.push([OB+j,OB+i,OT+i,OT+j]);f.push([IB+i,IB+j,IT+j,IT+i]);
    f.push([OT+i,OT+j,IT+j,IT+i]);f.push([OB+j,OB+i,IB+i,IB+j]);
  }
  if(!closed){f.push([OB+0,IB+0,IT+0,OT+0]);var last=n-1;f.push([IB+last,OB+last,OT+last,IT+last]);}
  return {v:v,f:f};
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
  }catch(eW){return {error:'Wall build failed'};}
  if(!nm||!nm.f||nm.f.length<4)return {error:'Wall produced an empty solid'};
  var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
  if(closed){bim.innerLoop=innerRing;bim.outerLoop=outerRing;}
  return {mesh:nm,bim:bim};
}
function earClip(P){
  var idx=[],i,n=P.length,tris=[],guard=0;
  for(i=0;i<n;i++)idx.push(i);
  function cross2(o,a2,b2){return (a2[0]-o[0])*(b2[1]-o[1])-(a2[1]-o[1])*(b2[0]-o[0]);}
  function inTri(p,a2,b2,c2){var d1=cross2(p,a2,b2),d2=cross2(p,b2,c2),d3=cross2(p,c2,a2);var neg=(d1<0)||(d2<0)||(d3<0),pos=(d1>0)||(d2>0)||(d3>0);return !(neg&&pos);}
  while(idx.length>3&&guard++<3000){
    var cut=false;
    for(i=0;i<idx.length;i++){
      var i0=idx[(i+idx.length-1)%idx.length],i1=idx[i],i2=idx[(i+1)%idx.length];
      if(cross2(P[i0],P[i1],P[i2])<=1e-9)continue;
      var ok=true,k;
      for(k=0;k<idx.length;k++){var ix=idx[k];if(ix===i0||ix===i1||ix===i2)continue;if(inTri(P[ix],P[i0],P[i1],P[i2])){ok=false;break;}}
      if(!ok)continue;
      tris.push([i0,i1,i2]);idx.splice(i,1);cut=true;break;
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
  for(i=0;i<n;i++){j=(i+1)%n;f.push([j,i,i+n,j+n]);}
  return {v:v,f:f};
}
function bimBuildFloorGeometry(profPts,y,thickness){
  var P=sketchCCW(profPts);
  if(P.length<3)return {error:'Floor needs at least 3 points'};
  var m;
  try{m=padMesh(P,y-thickness,thickness);}catch(e){return {error:'Floor build failed'};}
  return {mesh:m,bim:{type:'floor',thickness:thickness,baseY:y,profile:profPts.slice()}};
}

// ---- Generic transform helpers being tested ----
function bimMirrorPoint(pt,P1,P2){
  var dx=P2[0]-P1[0],dz=P2[1]-P1[1];var len=Math.sqrt(dx*dx+dz*dz)||1e-9;
  var ux=dx/len,uz=dz/len;var vx=pt[0]-P1[0],vz=pt[1]-P1[1];
  var proj=vx*ux+vz*uz;var perpX=vx-proj*ux,perpZ=vz-proj*uz;
  return [P1[0]+proj*ux-perpX,P1[1]+proj*uz-perpZ];
}
function bimRotatePoint(pt,center,angleRad){
  var vx=pt[0]-center[0],vz=pt[1]-center[1];
  var c=Math.cos(angleRad),s=Math.sin(angleRad);
  return [center[0]+vx*c-vz*s,center[1]+vx*s+vz*c];
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
  if(o.mesh){
    // generic mesh-vertex transform (booleans, imports) -- transform every vertex directly,
    // which correctly handles asymmetric shapes (unlike a pos-only transform)
    var newV=o.mesh.v.map(function(v3){var p2=transformPt([v3[0],v3[2]]);return [p2[0],v3[1],p2[1]];});
    return {kind:'mesh',mesh:{v:newV,f:o.mesh.f}};
  }
  if(o.pos){
    var np=transformPt([o.pos[0],o.pos[2]]);
    return {kind:'pos',pos:[np[0],o.pos[1],np[1]]};
  }
  return {error:'This object type cannot be transformed'};
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}
function checkWatertight(mesh){
  var edgeCount={},i,j;
  for(i=0;i<mesh.f.length;i++){var fc=mesh.f[i];for(j=0;j<fc.length;j++){var a=fc[j],b=fc[(j+1)%fc.length];var k=a<b?a+'_'+b:b+'_'+a;edgeCount[k]=(edgeCount[k]||0)+1;}}
  var bad=0,k2;for(k2 in edgeCount)if(edgeCount[k2]!==2)bad++;
  return bad;
}

// ---- 1. Mirror a wall across a vertical axis ----
var wallRes=bimBuildWallGeometry([[0,0],[6,0],[6,4],[0,4]],0,3,0.3,'center',true);
var wallObj={id:'w1',t:'solid',bim:wallRes.bim,mesh:wallRes.mesh,pos:[0,0,0]};
var mirrorFn=function(p){return bimMirrorPoint(p,[10,0],[10,1]);}; // mirror across the vertical line X=10
var mirrored=bimComputeTransformedGeometry(wallObj,mirrorFn);
assert('mirroring a wall succeeds', !mirrored.error, JSON.stringify(mirrored.error));
assert('mirrored wall mesh is watertight', checkWatertight(mirrored.mesh)===0, checkWatertight(mirrored.mesh));
assert('mirrored wall centerline is correctly reflected (X=0 becomes X=20)', approx(mirrored.bim.centerline[0][0],20));
assert('mirrored wall preserves thickness/height/align', mirrored.bim.thickness===0.3&&mirrored.bim.height===3&&mirrored.bim.align==='center');

// ---- 2. Rotate a room 90 degrees around its own centroid ----
var roomObj={id:'r1',t:'room',pts:[[0,0],[4,0],[4,2],[0,2]],y:0,area:8};
var rotateFn=function(p){return bimRotatePoint(p,[2,1],Math.PI/2);};
var rotated=bimComputeTransformedGeometry(roomObj,rotateFn);
assert('rotating a room succeeds and preserves its area (rigid transform)', rotated.area===8);
assert('rotated room has the same point count', rotated.pts.length===4);

// ---- 3. Rotate a generic mesh (boolean/import standin) -- verifies asymmetric shapes rotate correctly, not just translate ----
var wedgeStandin={id:'wedge1',t:'solid',pos:[0,0,0],mesh:{v:[[0,0,0],[4,0,0],[0,0,2],[0,3,0]],f:[[0,1,2],[0,3,1],[0,2,3],[1,3,2]]}};
var rot90=function(p){return bimRotatePoint(p,[0,0],Math.PI/2);};
var rotatedWedge=bimComputeTransformedGeometry(wedgeStandin,rot90);
assert('rotating a mesh-based (asymmetric) object transforms EVERY vertex, not just position',
  approx(rotatedWedge.mesh.v[1][0],0)&&approx(rotatedWedge.mesh.v[1][2],4), JSON.stringify(rotatedWedge.mesh.v[1]));
assert('rotating a mesh-based object leaves the Y (height) coordinate untouched', rotatedWedge.mesh.v[3][1]===3);

// ---- 4. A primitive (pos-only) transforms its position correctly ----
var boxObj={id:'b1',t:'box',pos:[5,0,5],prm:{}};
var mirroredBox=bimComputeTransformedGeometry(boxObj,function(p){return bimMirrorPoint(p,[0,0],[0,1]);});
assert('mirroring a primitive transforms its position across the given axis', approx(mirroredBox.pos[0],-5)&&approx(mirroredBox.pos[2],5));

// ---- 5. Imported wall without centerline is correctly rejected, not crashed ----
var importedWall={id:'iw1',t:'solid',bim:{type:'wall',imported:true},mesh:{v:[],f:[]},pos:[0,0,0]};
var res5=bimComputeTransformedGeometry(importedWall,mirrorFn);
assert('transforming an imported wall without parametric data is rejected cleanly', !!res5.error);

// ---- 6. Text and Dimension transform correctly ----
var textObj={id:'t1',t:'text',text:'Kitchen',pt:[3,3],y:0};
var rotatedText=bimComputeTransformedGeometry(textObj,rot90);
assert('rotating a text label transforms its anchor point', approx(rotatedText.pt[0],-3)&&approx(rotatedText.pt[1],3), JSON.stringify(rotatedText.pt));

var dimObj={id:'d1',t:'dim',p1:[0,0],p2:[4,0],d1:[0,1],d2:[4,1],length:4,y:0};
var rotatedDim=bimComputeTransformedGeometry(dimObj,rot90);
assert('rotating a dimension preserves its measured length (rigid transform)', rotatedDim.length===4);
assert('rotating a dimension correctly transforms both measured points', approx(rotatedDim.p2[0],0)&&approx(rotatedDim.p2[1],4));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
