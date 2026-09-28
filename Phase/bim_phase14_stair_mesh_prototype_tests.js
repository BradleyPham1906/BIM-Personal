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
  // cap triangulation per strip, WITH the intermediate vertex at the previous step's height on the
  // left edge -- this is what makes the cap edges line up exactly with the riser-quad edges below,
  // instead of leaving a T-junction where one side has a vertex the other doesn't.
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

var numSteps=17,riserH=3.0/17,treadD=0.28;
var mesh1=bimBuildStairMesh([0,0],[1,0],1.0,0,numSteps,riserH,treadD);
assert('17-step stair is watertight', checkWatertight(mesh1)===0, checkWatertight(mesh1));

var i,minY=Infinity,maxY=-Infinity,minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity;
for(i=0;i<mesh1.v.length;i++){
  var p=mesh1.v[i];
  if(p[1]<minY)minY=p[1];if(p[1]>maxY)maxY=p[1];
  if(p[0]<minX)minX=p[0];if(p[0]>maxX)maxX=p[0];
  if(p[2]<minZ)minZ=p[2];if(p[2]>maxZ)maxZ=p[2];
}
assert('spans exact vertical rise', Math.abs(minY-0)<1e-9&&Math.abs(maxY-numSteps*riserH)<1e-9, minY+'..'+maxY);
assert('spans exact horizontal run', Math.abs(minX-0)<1e-9&&Math.abs(maxX-numSteps*treadD)<1e-9, minX+'..'+maxX);
assert('spans exact width', Math.abs((maxZ-minZ)-1.0)<1e-9);

var mesh2=bimBuildStairMesh([5,5],[0,1],1.2,2,10,0.18,0.28);
assert('offset start + different direction still watertight', checkWatertight(mesh2)===0, checkWatertight(mesh2));

var diagDir=[Math.SQRT1_2,Math.SQRT1_2];
var mesh3=bimBuildStairMesh([0,0],diagDir,1.0,0,8,0.18,0.28);
assert('diagonal travel direction still watertight', checkWatertight(mesh3)===0, checkWatertight(mesh3));

var mesh4=bimBuildStairMesh([0,0],[1,0],1.0,0,1,0.18,0.28);
assert('single-step edge case still watertight', checkWatertight(mesh4)===0, checkWatertight(mesh4));

var mesh5=bimBuildStairMesh([0,0],[1,0],1.0,0,40,0.15,0.25);
assert('a large 40-step stair (stress test) is watertight', checkWatertight(mesh5)===0, checkWatertight(mesh5));

var mesh6=bimBuildStairMesh([0,0],[1,0],2.5,0,12,0.17,0.29);
assert('a wider stair (2.5m) is watertight', checkWatertight(mesh6)===0, checkWatertight(mesh6));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
