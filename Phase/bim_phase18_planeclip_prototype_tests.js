function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function vadd(a,b){return [a[0]+b[0],a[1]+b[1],a[2]+b[2]];}
function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
function vlerp(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t];}

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
function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
  if(a<0)P.reverse();
  return P;
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

// ---- The new algorithm ----
var CLIP_EPS=1e-7;
function bimClipTriangle(A,B,C,dA,dB,dC){
  var pts=[A,B,C],ds=[dA,dB,dC];
  var keep=[ds[0]>=-CLIP_EPS,ds[1]>=-CLIP_EPS,ds[2]>=-CLIP_EPS];
  var numKeep=(keep[0]?1:0)+(keep[1]?1:0)+(keep[2]?1:0);
  if(numKeep===3)return {kept:[[A,B,C]],cutEdge:null};
  if(numKeep===0)return {kept:[],cutEdge:null};
  var outPts=[],intersections=[],i;
  for(i=0;i<3;i++){
    var j=(i+1)%3;
    var pi=pts[i],pj=pts[j],di=ds[i],dj=ds[j];
    if(keep[i])outPts.push(pi);
    if(keep[i]!==keep[j]){
      var t=di/(di-dj);
      var ip=vlerp(pi,pj,t);
      outPts.push(ip);
      intersections.push(ip);
    }
  }
  var tris=[];
  for(i=1;i<outPts.length-1;i++)tris.push([outPts[0],outPts[i],outPts[i+1]]);
  var cutEdge=(intersections.length===2)?[intersections[0],intersections[1]]:null;
  return {kept:tris,cutEdge:cutEdge};
}
function bimChainEdgesToLoops(edges){
  function keyOf(p){return p[0].toFixed(4)+','+p[1].toFixed(4)+','+p[2].toFixed(4);}
  function edgeKey(a,b){return a<b?a+'|'+b:b+'|'+a;}
  var pointByKey={},adj={},i;
  for(i=0;i<edges.length;i++){
    var k1=keyOf(edges[i][0]),k2=keyOf(edges[i][1]);
    if(k1===k2)continue; // degenerate zero-length edge, skip
    pointByKey[k1]=edges[i][0];pointByKey[k2]=edges[i][1];
    if(!adj[k1])adj[k1]=[];
    if(!adj[k2])adj[k2]=[];
    adj[k1].push(k2);
    adj[k2].push(k1);
  }
  var usedEdge={},loops=[];
  var allKeys=Object.keys(adj);
  var ki;
  for(ki=0;ki<allKeys.length;ki++){
    var startKey=allKeys[ki];
    var neighbors=adj[startKey],ni;
    for(ni=0;ni<neighbors.length;ni++){
      var ek=edgeKey(startKey,neighbors[ni]);
      if(usedEdge[ek])continue;
      var loop=[startKey];
      var current=startKey,next=neighbors[ni];
      usedEdge[edgeKey(current,next)]=true;
      var guard=0;
      while(next!==startKey&&guard++<10000){
        loop.push(next);
        var nextNeighbors=adj[next],found=null,nj;
        for(nj=0;nj<nextNeighbors.length;nj++){
          var ek2=edgeKey(next,nextNeighbors[nj]);
          if(!usedEdge[ek2]){found=nextNeighbors[nj];usedEdge[ek2]=true;break;}
        }
        if(found===null)break;
        current=next;next=found;
      }
      if(next===startKey&&loop.length>=3)loops.push(loop.map(function(k){return pointByKey[k];}));
    }
  }
  return loops;
}
function bimCapLoop(loop3D,normal){
  if(loop3D.length<3)return [];
  var n=normal;
  var arbitrary=Math.abs(n[0])<0.9?[1,0,0]:[0,1,0];
  var u=vnorm(vcross(arbitrary,n));
  var v=vcross(n,u);
  var pts2D=loop3D.map(function(p){return [vdot(p,u),vdot(p,v)];});
  var area=0,i;
  for(i=0;i<pts2D.length;i++){var j=(i+1)%pts2D.length;area+=pts2D[i][0]*pts2D[j][1]-pts2D[j][0]*pts2D[i][1];}
  var pts3=loop3D.slice(),pts2=pts2D.slice();
  if(area<0){pts3.reverse();pts2.reverse();}
  var tris=earClip(pts2);
  var out=[];
  for(i=0;i<tris.length;i++)out.push([pts3[tris[i][0]],pts3[tris[i][1]],pts3[tris[i][2]]]);
  return out;
}
function bimClipMeshToPlane(mesh,planeP,planeN){
  var kept=[],cutEdges=[],i,j;
  for(i=0;i<mesh.f.length;i++){
    var fc=mesh.f[i];
    var faceTris=[];
    for(j=2;j<fc.length;j++)faceTris.push([fc[0],fc[j-1],fc[j]]);
    var t;
    for(t=0;t<faceTris.length;t++){
      var tri=faceTris[t];
      var A=mesh.v[tri[0]],B=mesh.v[tri[1]],C=mesh.v[tri[2]];
      var dA=vdot(vsub(A,planeP),planeN),dB=vdot(vsub(B,planeP),planeN),dC=vdot(vsub(C,planeP),planeN);
      var res=bimClipTriangle(A,B,C,dA,dB,dC);
      kept=kept.concat(res.kept);
      if(res.cutEdge)cutEdges.push(res.cutEdge);
    }
  }
  var loops=bimChainEdgesToLoops(cutEdges);
  var capTris=[];
  for(i=0;i<loops.length;i++)capTris=capTris.concat(bimCapLoop(loops[i],planeN));
  return bimWeldMesh(kept.concat(capTris));
}

// ==== TESTS ====
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
function meshBounds(mesh){
  var mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9],i,k;
  for(i=0;i<mesh.v.length;i++)for(k=0;k<3;k++){
    if(mesh.v[i][k]<mn[k])mn[k]=mesh.v[i][k];
    if(mesh.v[i][k]>mx[k])mx[k]=mesh.v[i][k];
  }
  return {mn:mn,mx:mx};
}

// ---- Test 1: the EXACT case that broke CSG intersect -- a 10x10x4 box cut at x=5 ----
var box=padMesh(sketchCCW([[0,0],[10,0],[10,10],[0,10]]),0,4);
var clipped=bimClipMeshToPlane(box,[5,0,0],[-1,0,0]); // normal points -X, keeping x<=5
assert('clipped box is watertight (the exact case that failed with CSG)', checkWatertight(clipped)===0, checkWatertight(clipped));
var b1=meshBounds(clipped);
assert('clipped box has correct X range [0,5]', Math.abs(b1.mn[0]-0)<1e-6&&Math.abs(b1.mx[0]-5)<1e-6, JSON.stringify(b1));
assert('clipped box keeps full Y range [0,4]', Math.abs(b1.mn[1]-0)<1e-6&&Math.abs(b1.mx[1]-4)<1e-6);
assert('clipped box keeps full Z range [0,10]', Math.abs(b1.mn[2]-0)<1e-6&&Math.abs(b1.mx[2]-10)<1e-6);

// opposite side
var clipped2=bimClipMeshToPlane(box,[5,0,0],[1,0,0]); // keeping x>=5
assert('opposite-side clip is also watertight', checkWatertight(clipped2)===0, checkWatertight(clipped2));
var b2=meshBounds(clipped2);
assert('opposite-side clip has correct X range [5,10]', Math.abs(b2.mn[0]-5)<1e-6&&Math.abs(b2.mx[0]-10)<1e-6);

// ---- Test 2: the wall standin case (previously also found broken under CSG) ----
var wall=padMesh(sketchCCW([[0,-0.15],[6,-0.15],[6,0.15],[0,0.15]]),0,3);
var wallClipped=bimClipMeshToPlane(wall,[3,0,0],[0,0,-1]); // cut along Z at z=3... wait wall runs along X, cut plane should be perpendicular to X
// correct: wall runs along X (0 to 6), cut it at x=3, keep normal pointing -X
var wallClipped2=bimClipMeshToPlane(wall,[3,0,0],[-1,0,0]);
assert('wall clip is watertight', checkWatertight(wallClipped2)===0, checkWatertight(wallClipped2));
var bw=meshBounds(wallClipped2);
assert('wall clip preserves full thickness (Z range -0.15..0.15)', Math.abs(bw.mn[2]-(-0.15))<1e-6&&Math.abs(bw.mx[2]-0.15)<1e-6, JSON.stringify(bw));
assert('wall clip correctly bounds X to [0,3]', Math.abs(bw.mn[0]-0)<1e-6&&Math.abs(bw.mx[0]-3)<1e-6);

// ---- Test 3: object entirely on the kept side survives whole; entirely removed side vanishes ----
var smallInside=padMesh(sketchCCW([[6,4],[8,4],[8,6],[6,6]]),0,3);
var clippedInside=bimClipMeshToPlane(smallInside,[5,0,0],[1,0,0]); // keep x>=5, object is x:[6,8], fully inside
assert('object entirely on kept side survives essentially whole', checkWatertight(clippedInside)===0 && clippedInside.f.length>0);

var smallOutside=padMesh(sketchCCW([[-5,4],[-3,4],[-3,6],[-5,6]]),0,3);
var clippedOutside=bimClipMeshToPlane(smallOutside,[5,0,0],[1,0,0]); // keep x>=5, object is x:[-5,-3], fully outside
assert('object entirely on removed side produces an empty (not crashed) result', clippedOutside.f.length===0, clippedOutside.f.length);

// ---- Test 4: stress test with many steps (reusing the stair mesh from earlier work) ----
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
var stair=bimBuildStairMesh([0,0],[1,0],1.0,0,17,3.0/17,0.28);
var stairClipped=bimClipMeshToPlane(stair,[2.4,0,0],[-1,0,0]); // cut partway through the stair run
assert('clipping a complex stair mesh (many faces) is watertight', checkWatertight(stairClipped)===0, checkWatertight(stairClipped));
assert('clipped stair produces real, non-empty geometry', stairClipped.f.length>0);

// ---- Test 5: clip a mesh that ends up with TWO disjoint pieces at the cut plane (multi-loop case) ----
// two separate boxes, both straddling the cut plane, should each get their own cap loop
var boxLeftPart=padMesh(sketchCCW([[0,0],[6,0],[6,2],[0,2]]),0,3);
var boxRightPart=padMesh(sketchCCW([[0,8],[6,8],[6,10],[0,10]]),0,3);
var combined={v:boxLeftPart.v.concat(boxRightPart.v),
  f:boxLeftPart.f.concat(boxRightPart.f.map(function(fc){return fc.map(function(idx){return idx+boxLeftPart.v.length;});}))};
var multiClipped=bimClipMeshToPlane(combined,[3,0,0],[-1,0,0]);
assert('multi-piece mesh (two disjoint boxes both straddling the cut) clips watertight', checkWatertight(multiClipped)===0, checkWatertight(multiClipped));

// ---- Test 6: plane entirely misses the mesh (no intersection) -- must not crash, either keep-all or empty ----
var farBox=padMesh(sketchCCW([[20,20],[22,20],[22,22],[20,22]]),0,3);
var missedKeep=bimClipMeshToPlane(farBox,[5,0,0],[1,0,0]); // plane at x=5, box is entirely at x>5 (kept side)
assert('a plane that misses the mesh entirely (mesh fully on kept side) returns it watertight and whole', checkWatertight(missedKeep)===0 && missedKeep.f.length===box.f.length===false || missedKeep.f.length>0);
var missedDiscard=bimClipMeshToPlane(farBox,[100,0,0],[1,0,0]); // plane far beyond, box entirely on discard side
assert('a plane where the mesh is entirely discarded produces an empty result, no crash', missedDiscard.f.length===0);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
