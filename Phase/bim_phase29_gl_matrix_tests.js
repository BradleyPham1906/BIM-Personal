// ---- existing CPU projection, copied verbatim from canvas_v10.html ----
function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
function camVecs(c){
  var cy=Math.cos(c.yaw),sy=Math.sin(c.yaw),cp=Math.cos(c.pitch),sp=Math.sin(c.pitch);
  var d=[cp*sy,sp,cp*cy];
  var r=vnorm(vcross([0,1,0],d));
  var u=vcross(d,r);
  return {d:d,r:r,u:u,eye:[c.tx+d[0]*c.dist,c.ty+d[1]*c.dist,c.tz+d[2]*c.dist]};
}
function toScreen(p,V,W,H,flat,camDist){
  var x=p[0]-V.eye[0],y=p[1]-V.eye[1],z=p[2]-V.eye[2];
  var xc=x*V.r[0]+y*V.r[1]+z*V.r[2];
  var yc=x*V.u[0]+y*V.u[1]+z*V.u[2];
  var zc=x*V.d[0]+y*V.d[1]+z*V.d[2];
  if(flat){
    var k=H*1.2/Math.max(camDist,0.5);
    return [W/2+xc*k,H/2-yc*k,Math.max(-zc,0.5)];
  }
  var w=-zc;if(w<0.5)w=0.5;
  var f=H*1.2;
  return [W/2+xc*f/w,H/2-yc*f/w,w];
}

// ---- NEW: matrices for WebGL, derived to match the above exactly ----
// column-major 4x4, as WebGL expects
function bimGlViewMatrix(V){
  var r=V.r,u=V.u,d=V.d,e=V.eye;
  return [
    r[0], u[0], d[0], 0,
    r[1], u[1], d[1], 0,
    r[2], u[2], d[2], 0,
    -vdot(r,e), -vdot(u,e), -vdot(d,e), 1
  ];
}
function bimGlProjMatrix(W,H,flat,camDist,near,far){
  near=near||0.5; far=far||4000;
  if(flat){
    // orthographic: screenX = W/2 + xc*k  ->  ndcX = xc*k/(W/2)
    var k=H*1.2/Math.max(camDist,0.5);
    var sx=k/(W/2), sy=k/(H/2);
    return [
      sx,0,0,0,
      0,sy,0,0,
      0,0,-2/(far-near),0,
      0,0,-(far+near)/(far-near),1
    ];
  }
  // perspective: screenX = W/2 + xc*f/w where w=-zc, f=H*1.2
  // ndcX = xc*f/(w*(W/2)) -> clip.x = xc * f/(W/2), clip.w = -zc
  var f=H*1.2;
  var px=f/(W/2), py=f/(H/2);
  return [
    px,0,0,0,
    0,py,0,0,
    0,0,-(far+near)/(far-near),-1,
    0,0,-2*far*near/(far-near),0
  ];
}
function mat4mulVec(m,v){ // column-major m * vec4 v
  return [
    m[0]*v[0]+m[4]*v[1]+m[8]*v[2]+m[12]*v[3],
    m[1]*v[0]+m[5]*v[1]+m[9]*v[2]+m[13]*v[3],
    m[2]*v[0]+m[6]*v[1]+m[10]*v[2]+m[14]*v[3],
    m[3]*v[0]+m[7]*v[1]+m[11]*v[2]+m[15]*v[3]
  ];
}
function glToScreen(p,viewM,projM,W,H){
  var vv=mat4mulVec(viewM,[p[0],p[1],p[2],1]);
  var cc=mat4mulVec(projM,vv);
  if(Math.abs(cc[3])<1e-9)return null;
  var ndcx=cc[0]/cc[3], ndcy=cc[1]/cc[3];
  return [W/2+ndcx*(W/2), H/2-ndcy*(H/2), cc[3]];
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}

var W=1400,H=800;
var cams=[
  {yaw:-0.7,pitch:0.42,dist:20,tx:0,ty:0,tz:0},
  {yaw:1.9,pitch:0.15,dist:45,tx:3,ty:1,tz:-7},
  {yaw:0,pitch:1.52,dist:30,tx:0,ty:0,tz:0}
];
var pts=[[0,0,0],[5,3,-2],[-8,0.5,12],[100,20,-60],[0.2,0.1,0.3]];

console.log('--- PERSPECTIVE: GPU matrices must reproduce toScreen exactly ---');
var maxErr=0;
cams.forEach(function(c,ci){
  var V=camVecs(c);
  var viewM=bimGlViewMatrix(V), projM=bimGlProjMatrix(W,H,false,c.dist);
  pts.forEach(function(p,pi){
    var a=toScreen(p,V,W,H,false,c.dist);
    var b=glToScreen(p,viewM,projM,W,H);
    if(!b)return;
    // toScreen clamps w to 0.5; skip points behind the camera where clamping diverges
    var raw=vdot([p[0]-V.eye[0],p[1]-V.eye[1],p[2]-V.eye[2]],V.d);
    if(-raw<0.5)return;
    var e=Math.max(Math.abs(a[0]-b[0]),Math.abs(a[1]-b[1]));
    if(e>maxErr)maxErr=e;
  });
});
assert('perspective GPU projection matches CPU toScreen to sub-pixel accuracy', maxErr<0.001, 'max err='+maxErr+'px');

console.log('--- ORTHOGRAPHIC (plan/elevation mode) ---');
var maxErrO=0;
cams.forEach(function(c){
  var V=camVecs(c);
  var viewM=bimGlViewMatrix(V), projM=bimGlProjMatrix(W,H,true,c.dist);
  pts.forEach(function(p){
    var a=toScreen(p,V,W,H,true,c.dist);
    var b=glToScreen(p,viewM,projM,W,H);
    if(!b)return;
    var e=Math.max(Math.abs(a[0]-b[0]),Math.abs(a[1]-b[1]));
    if(e>maxErrO)maxErrO=e;
  });
});
assert('orthographic GPU projection matches CPU toScreen to sub-pixel accuracy', maxErrO<0.001, 'max err='+maxErrO+'px');

console.log('--- depth ordering sanity (GPU depth buffer needs monotonic z) ---');
var V0=camVecs(cams[0]);
var vm=bimGlViewMatrix(V0), pm=bimGlProjMatrix(W,H,false,cams[0].dist);
function ndcZ(p){
  var vv=mat4mulVec(vm,[p[0],p[1],p[2],1]);
  var cc=mat4mulVec(pm,vv);
  return cc[2]/cc[3];
}
var near=[V0.eye[0]-V0.d[0]*2, V0.eye[1]-V0.d[1]*2, V0.eye[2]-V0.d[2]*2];
var far=[V0.eye[0]-V0.d[0]*50, V0.eye[1]-V0.d[1]*50, V0.eye[2]-V0.d[2]*50];
var zn=ndcZ(near), zf=ndcZ(far);
assert('nearer geometry gets a smaller NDC depth than farther geometry', zn<zf, 'near='+zn.toFixed(4)+' far='+zf.toFixed(4));
assert('NDC depth stays within the valid [-1,1] clip range', zn>=-1.01&&zf<=1.01, zn+'..'+zf);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
