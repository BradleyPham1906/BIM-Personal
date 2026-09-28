var A3D={cam:{yaw:0,pitch:0.6,dist:20,tx:0,ty:0,tz:0},objs:[],flat:false};
function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function vnorm(a){var l=Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])||1;return [a[0]/l,a[1]/l,a[2]/l];}
var el={cv:{width:800,height:600}};

  var A3D_SNAP={point:true,grid:false,gridSize:0.5,ortho:false,pxThreshold:12};

  function toScreen(p,V,W,H){
    var x=p[0]-V.eye[0],y=p[1]-V.eye[1],z=p[2]-V.eye[2];
    var xc=x*V.r[0]+y*V.r[1]+z*V.r[2];
    var yc=x*V.u[0]+y*V.u[1]+z*V.u[2];
    var zc=x*V.d[0]+y*V.d[1]+z*V.d[2];
    if(A3D.flat){
      var k=H*1.2/Math.max(A3D.cam.dist,0.5);
      return [W/2+xc*k,H/2-yc*k,Math.max(-zc,0.5)];
    }
    var w=-zc;if(w<0.5)w=0.5;
    var f=H*1.2;
    return [W/2+xc*f/w,H/2-yc*f/w,w];
  }

  function camVecs(c){
    var cy=Math.cos(c.yaw),sy=Math.sin(c.yaw),cp=Math.cos(c.pitch),sp=Math.sin(c.pitch);
    var d=[cp*sy,sp,cp*cy];
    var r=vnorm(vcross([0,1,0],d));
    var u=vcross(d,r);
    return {d:d,r:r,u:u,eye:[c.tx+d[0]*c.dist,c.ty+d[1]*c.dist,c.tz+d[2]*c.dist]};
  }

  function bimSnapCandidates(y0){
    var pts=[],i,o,j;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t==='sketch'&&Math.abs(o.y-y0)<0.05){
        for(j=0;j<o.pts.length;j++)pts.push(o.pts[j]);
      }else if(o.t==='solid'&&o.bim&&o.bim.centerline&&Math.abs((o.bim.baseY||0)-y0)<0.05){
        for(j=0;j<o.bim.centerline.length;j++)pts.push(o.bim.centerline[j]);
      }
    }
    return pts;
  }

  function bimSnapPoint(xy,gRaw,sk){
    var px=gRaw[0],pz=gRaw[2],snapped=false;
    if(A3D_SNAP.point){
      var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height;
      var cands=bimSnapCandidates(sk.y),k;
      for(k=0;k<sk.pts.length;k++)cands.push(sk.pts[k]);
      var best=null,bestD=A3D_SNAP.pxThreshold;
      for(k=0;k<cands.length;k++){
        var c=cands[k];
        var sp=toScreen([c[0],sk.y,c[1]],V,W,H);
        var dx=sp[0]-xy[0],dy=sp[1]-xy[1],d=Math.sqrt(dx*dx+dy*dy);
        if(d<bestD){bestD=d;best=c;}
      }
      if(best){px=best[0];pz=best[1];snapped=true;}
    }
    if(!snapped&&A3D_SNAP.grid&&A3D_SNAP.gridSize>0){
      px=Math.round(px/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;
      pz=Math.round(pz/A3D_SNAP.gridSize)*A3D_SNAP.gridSize;
    }
    if(A3D_SNAP.ortho&&sk.pts.length&&!snapped){
      var last=sk.pts[sk.pts.length-1];
      var ddx=px-last[0],ddz=pz-last[1];
      if(Math.abs(ddx)>=Math.abs(ddz))pz=last[1];else px=last[0];
    }
    return [px,pz,snapped];
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

var V=camVecs(A3D.cam),W=el.cv.width,H=el.cv.height;

// Existing sketch with one point at world (3,2) on plane y=0
A3D.objs=[{t:'sketch',y:0,pts:[[3,2]]}];

var sk={y:0,pts:[]};

// Case 1: raw ground point is essentially AT the existing sketch point -> should snap
var g1=[3,0,2]; // groundPoint format [x,y,z]
var xyAtPoint=toScreen([3,0,2],V,W,H);
var r1=bimSnapPoint([xyAtPoint[0],xyAtPoint[1]], g1, sk);
assert('cursor exactly on an existing point snaps to it', r1[0]===3 && r1[1]===2 && r1[2]===true, JSON.stringify(r1));

// Case 2: raw ground point is far away (20,20) on screen, candidate at (3,2) should NOT be within threshold
var gFar=[20,0,20];
var xyFar=toScreen([20,0,20],V,W,H);
var r2=bimSnapPoint([xyFar[0],xyFar[1]], gFar, sk);
assert('cursor far from any existing point does not snap', r2[2]===false, JSON.stringify(r2));
assert('unsnapped point passes through the raw ground coordinates', r2[0]===20 && r2[1]===20, JSON.stringify(r2));

// Case 3: grid snap engages when point-snap is off and no candidate nearby
A3D_SNAP.point=false;A3D_SNAP.grid=true;A3D_SNAP.gridSize=0.5;
var r3=bimSnapPoint([xyFar[0],xyFar[1]], [20.23,0,19.61], sk);
assert('grid snap rounds to nearest 0.5 when point-snap is disabled', r3[0]===20&&r3[1]===19.5, JSON.stringify(r3));
A3D_SNAP.point=true;A3D_SNAP.grid=false;

// Case 4: ortho lock constrains relative to the last committed point in the in-progress path
A3D_SNAP.ortho=true;
var sk2={y:0,pts:[[0,0]]};
var rOrtho=bimSnapPoint([9999,9999],[5,0,0.4],sk2); // far off-screen xy so no point-snap triggers; raw g is what matters here
assert('ortho constrains a mostly-horizontal move to pure horizontal', rOrtho[1]===0, JSON.stringify(rOrtho));
A3D_SNAP.ortho=false;

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
