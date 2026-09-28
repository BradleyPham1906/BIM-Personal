function sketchCCW(pts){
  var a=0,i,j,P=pts.slice();
  for(i=0;i<P.length;i++){j=(i+1)%P.length;a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];}
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

// ---- Roof: tilted-plane mesh from footprint + pitch + slope direction ----
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
  return {v:v,f:f,topY:topY};
}

// ---- Stair: dimension math (risers/treads from total rise + target riser height) ----
function bimComputeStairDims(totalRise,targetRiserH,treadD){
  if(totalRise<=0||targetRiserH<=0)return null;
  var numSteps=Math.max(1,Math.round(totalRise/targetRiserH));
  var riserH=totalRise/numSteps;
  var totalRun=numSteps*treadD;
  return {numSteps:numSteps,riserH:riserH,treadD:treadD,totalRun:totalRun,totalRise:totalRise};
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

// ---- Roof tests ----
var footprint=[[0,0],[6,0],[6,4],[0,4]];
var flatRoof=bimBuildRoofMesh(footprint,3,0,0,0.15);
assert('flat roof (pitch=0) has all top points at the same base elevation',
  flatRoof.topY.every(function(y){return approx(y,3);}));
assert('flat roof mesh is watertight', checkWatertight(flatRoof)===0, checkWatertight(flatRoof));

var pitchedRoof=bimBuildRoofMesh(footprint,3,30,0,0.15); // slope in +X direction, 30 degree pitch
assert('pitched roof: low edge (x=0) sits at base elevation', approx(pitchedRoof.topY[0],3,1e-6));
var expectedHighY=3+6*Math.tan(30*Math.PI/180);
assert('pitched roof: high edge (x=6) rises by run*tan(pitch)', approx(pitchedRoof.topY[1],expectedHighY,1e-6),
  pitchedRoof.topY[1]+' vs '+expectedHighY);
assert('pitched roof mesh is watertight', checkWatertight(pitchedRoof)===0, checkWatertight(pitchedRoof));

var pitchedRoofZ=bimBuildRoofMesh(footprint,3,30,90,0.15); // slope in +Z direction instead
assert('rotating slope direction 90deg moves the rise to the Z-varying corners',
  approx(pitchedRoofZ.topY[0],3,1e-6)&&approx(pitchedRoofZ.topY[2],3+4*Math.tan(30*Math.PI/180),1e-6));

// non-rectangular (L-shaped) footprint still produces a valid watertight roof
var lfoot=[[0,0],[6,0],[6,2],[3,2],[3,4],[0,4]];
var lroof=bimBuildRoofMesh(lfoot,3,20,45,0.15);
assert('L-shaped footprint roof builds and is watertight', lroof&&checkWatertight(lroof)===0);

// ---- Stair tests ----
var dims1=bimComputeStairDims(3.0,0.178,0.28); // 3m total rise, ~7in target riser
assert('stair dims: riser height stays close to the target (rounds to a whole number of steps)',
  Math.abs(dims1.riserH-0.178)<0.02, dims1.riserH);
assert('stair dims: numSteps*riserH reconstructs the exact total rise', approx(dims1.numSteps*dims1.riserH,3.0));
assert('stair dims: totalRun = numSteps * treadDepth', approx(dims1.totalRun,dims1.numSteps*0.28));

var dims2=bimComputeStairDims(0.15,0.178,0.28); // tiny rise -> still at least 1 step
assert('stair dims: a tiny total rise still produces at least 1 step, not 0', dims2.numSteps>=1);

var dims3=bimComputeStairDims(0,0.178,0.28);
assert('stair dims: zero total rise is rejected (nothing to build)', dims3===null);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
