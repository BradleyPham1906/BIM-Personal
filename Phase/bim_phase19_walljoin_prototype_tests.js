function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
  if(a<0)P.reverse();
  return P;
}
function bimSegNormal(a,b){
  var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
  return [-dz/len,dx/len];
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
    return {error:'Wall build failed: '+(eW&&eW.message?eW.message:eW)};
  }
  if(!nm||!nm.f||nm.f.length<4)return {error:'Wall produced an empty solid'};
  var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
  if(closed){bim.innerLoop=innerRing;bim.outerLoop=outerRing;}
  return {mesh:nm,bim:bim};
}

// ---- Wall Join: the new logic being tested ----
function bimLineLineIntersect(a1,a2,b1,b2){
  var d1x=a2[0]-a1[0],d1z=a2[1]-a1[1];
  var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
  var denom=d1x*d2z-d1z*d2x;
  if(Math.abs(denom)<1e-9)return null;
  var dx=b1[0]-a1[0],dz=b1[1]-a1[1];
  var t=(dx*d2z-dz*d2x)/denom;
  return [a1[0]+d1x*t,a1[1]+d1z*t];
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

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}
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

// ---- Test 1: two walls that overlap slightly at an L-corner should trim to meet exactly ----
var wallResA=bimBuildWallGeometry([[0,0],[6,0.3]],0,3,0.3,'center',false); // slightly off, ending near (6,0.3)
var wallResB=bimBuildWallGeometry([[6.2,0.3],[6.2,5]],0,3,0.3,'center',false); // starts slightly off from wallA's end
var wallA={id:'wA',t:'solid',bim:wallResA.bim,mesh:wallResA.mesh,pos:[0,0,0]};
var wallB={id:'wB',t:'solid',bim:wallResB.bim,mesh:wallResB.mesh,pos:[0,0,0]};
var joinRes=bimJoinWalls(wallA,wallB);
assert('join succeeds for two open walls with a gap at their corner', !joinRes.error, JSON.stringify(joinRes.error));
assert('joined wall A mesh is watertight', checkWatertight(joinRes.meshA)===0, checkWatertight(joinRes.meshA));
assert('joined wall B mesh is watertight', checkWatertight(joinRes.meshB)===0, checkWatertight(joinRes.meshB));
assert('wall A\'s centerline endpoint now exactly matches wall B\'s centerline endpoint (true corner join)',
  approx(joinRes.bimA.centerline[joinRes.bimA.centerline.length-1][0],joinRes.bimB.centerline[0][0])&&
  approx(joinRes.bimA.centerline[joinRes.bimA.centerline.length-1][1],joinRes.bimB.centerline[0][1]));

// ---- Test 2: a clean T-junction (one wall's endpoint touching the middle of another) should NOT
// use this join (join is specifically for end-to-end corners); test that a proper corner case
// (walls ending near each other, not a T) is correctly identified and joined ----
var wallResC=bimBuildWallGeometry([[0,0],[5,0]],0,3,0.25,'center',false);
var wallResD=bimBuildWallGeometry([[5.1,-0.1],[5.1,4]],0,3,0.25,'center',false);
var wallC={id:'wC',t:'solid',bim:wallResC.bim,mesh:wallResC.mesh,pos:[0,0,0]};
var wallD={id:'wD',t:'solid',bim:wallResD.bim,mesh:wallResD.mesh,pos:[0,0,0]};
var joinRes2=bimJoinWalls(wallC,wallD);
assert('a second, differently-shaped corner join also succeeds cleanly', !joinRes2.error);
assert('join point is a real, finite coordinate', isFinite(joinRes2.joinPoint[0])&&isFinite(joinRes2.joinPoint[1]));

// ---- Test 3: closed walls cannot be joined (join is for open wall-chain corners only) ----
var closedWallRes=bimBuildWallGeometry([[0,0],[4,0],[4,4],[0,4]],0,3,0.3,'center',true);
var closedWall={id:'wClosed',t:'solid',bim:closedWallRes.bim,mesh:closedWallRes.mesh,pos:[0,0,0]};
var openWallRes=bimBuildWallGeometry([[10,10],[15,10]],0,3,0.3,'center',false);
var openWall={id:'wOpen',t:'solid',bim:openWallRes.bim,mesh:openWallRes.mesh,pos:[0,0,0]};
var joinRes3=bimJoinWalls(closedWall,openWall);
assert('joining a closed wall loop is correctly rejected (join only applies to open wall chains)', !!joinRes3.error);

// ---- Test 4: parallel walls (no corner possible) are correctly rejected, not crashed ----
var wallResE=bimBuildWallGeometry([[0,0],[5,0]],0,3,0.25,'center',false);
var wallResF=bimBuildWallGeometry([[0,2],[5,2]],0,3,0.25,'center',false);
var wallE={id:'wE',t:'solid',bim:wallResE.bim,mesh:wallResE.mesh,pos:[0,0,0]};
var wallF={id:'wF',t:'solid',bim:wallResF.bim,mesh:wallResF.mesh,pos:[0,0,0]};
var joinRes4=bimJoinWalls(wallE,wallF);
assert('parallel walls (cannot form a corner) are rejected with a clear error, not crashed', !!joinRes4.error);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
