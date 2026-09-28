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

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- Mirror point ----
var m1=bimMirrorPoint([3,5],[0,0],[1,0]); // mirror across the X axis (line Z=0)
assert('mirror across the X axis flips Z, keeps X', approx(m1[0],3)&&approx(m1[1],-5), JSON.stringify(m1));
var m2=bimMirrorPoint([3,5],[0,0],[0,1]); // mirror across the Z axis (line X=0)
assert('mirror across the Z axis flips X, keeps Z', approx(m2[0],-3)&&approx(m2[1],5), JSON.stringify(m2));
var m3=bimMirrorPoint([2,2],[0,0],[1,1]); // mirror across the diagonal Y=X line
assert('mirroring a point ON the diagonal mirror line stays put', approx(m3[0],2)&&approx(m3[1],2));
var m4=bimMirrorPoint([0,2],[0,0],[1,1]);
assert('mirror across the diagonal swaps coordinates', approx(m4[0],2)&&approx(m4[1],0), JSON.stringify(m4));
var m5=bimMirrorPoint([5,5],[0,0],[1,0]);
var m6=bimMirrorPoint(m5,[0,0],[1,0]);
assert('mirroring twice across the same line returns the original point', approx(m6[0],5)&&approx(m6[1],5));

// ---- Rotate point ----
var r1=bimRotatePoint([1,0],[0,0],Math.PI/2); // rotate 90deg CCW around origin
assert('rotating (1,0) by 90deg around origin gives (0,1)', approx(r1[0],0)&&approx(r1[1],1), JSON.stringify(r1));
var r2=bimRotatePoint([1,0],[0,0],Math.PI); // 180deg
assert('rotating by 180deg gives (-1,0)', approx(r2[0],-1)&&approx(r2[1],0), JSON.stringify(r2));
var r3=bimRotatePoint([5,5],[5,5],Math.PI/3); // rotating a point AROUND ITSELF never moves
assert('rotating a point around itself (zero radius) never moves', approx(r3[0],5)&&approx(r3[1],5));
var r4=bimRotatePoint([3,0],[1,0],Math.PI); // rotate around an off-origin center
assert('rotating 180deg around an off-center point reflects through that center', approx(r4[0],-1)&&approx(r4[1],0), JSON.stringify(r4));
var r5=bimRotatePoint([2,0],[0,0],0);
assert('rotating by zero angle leaves the point unchanged', approx(r5[0],2)&&approx(r5[1],0));

// ---- Line-line intersection ----
var i1=bimLineLineIntersect([0,0],[10,0],[5,-5],[5,5]); // horizontal line meets vertical line at (5,0)
assert('perpendicular lines intersect at the expected point', approx(i1[0],5)&&approx(i1[1],0), JSON.stringify(i1));
var i2=bimLineLineIntersect([0,0],[1,0],[0,1],[1,1]); // parallel lines never meet
assert('parallel lines return null (no intersection)', i2===null);
var i3=bimLineLineIntersect([0,0],[10,10],[0,10],[10,0]); // diagonal X, meet at center
assert('diagonal lines intersect at their crossing point', approx(i3[0],5)&&approx(i3[1],5), JSON.stringify(i3));
// intersection works even when the actual crossing point is OUTSIDE both segments' extents
// (needed for wall trim/extend, where walls often need extending beyond their drawn endpoints)
var i4=bimLineLineIntersect([0,0],[1,0],[5,-1],[5,1]);
assert('intersection correctly extrapolates beyond the segment extents (needed for wall extend)', approx(i4[0],5)&&approx(i4[1],0));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
