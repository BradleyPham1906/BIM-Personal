function bimComputeAngularDim(vertex,p1,p2){
  var a1=Math.atan2(p1[1]-vertex[1],p1[0]-vertex[0]);
  var a2=Math.atan2(p2[1]-vertex[1],p2[0]-vertex[0]);
  var r1=Math.sqrt(Math.pow(p1[0]-vertex[0],2)+Math.pow(p1[1]-vertex[1],2));
  var r2=Math.sqrt(Math.pow(p2[0]-vertex[0],2)+Math.pow(p2[1]-vertex[1],2));
  if(r1<1e-9||r2<1e-9)return null;
  var sweep=a2-a1;
  while(sweep<=-Math.PI)sweep+=Math.PI*2;
  while(sweep>Math.PI)sweep-=Math.PI*2;
  var radius=Math.min(r1,r2)*0.6;
  return {vertex:vertex,a1:a1,a2:a2,sweep:sweep,radius:radius,degrees:Math.abs(sweep)*180/Math.PI};
}
function bimCircleFrom3Points(p1,p2,p3){
  var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
  var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
  if(Math.abs(d)<1e-9)return null; // collinear
  var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
  var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
  var r=Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2));
  return {center:[ux,uy],radius:r};
}
function bimComputeRadialDim(center,radius,anglePt,isDiameter){
  var ang=Math.atan2(anglePt[1]-center[1],anglePt[0]-center[0]);
  var edge=[center[0]+Math.cos(ang)*radius,center[1]+Math.sin(ang)*radius];
  var start=isDiameter?[center[0]-Math.cos(ang)*radius,center[1]-Math.sin(ang)*radius]:center;
  return {center:center,radius:radius,start:start,edge:edge,
    value:isDiameter?radius*2:radius,isDiameter:!!isDiameter};
}
function bimComputeLeader(anchorPt,elbowPt,textPt){
  // leader: anchor (arrow tip) -> elbow -> horizontal landing under the text
  var dir=textPt[0]>=elbowPt[0]?1:-1;
  var landing=[elbowPt[0]+dir*0.5,elbowPt[1]];
  return {anchor:anchorPt,elbow:elbowPt,landing:landing,textPt:textPt,dir:dir};
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b,e){return Math.abs(a-b)<(e||1e-6);}

// ---- Angular ----
var a90=bimComputeAngularDim([0,0],[1,0],[0,1]);
assert('perpendicular rays measure 90 degrees', a90&&approx(a90.degrees,90), a90&&a90.degrees);
var a45=bimComputeAngularDim([0,0],[1,0],[1,1]);
assert('45-degree rays measure 45 degrees', approx(a45.degrees,45), a45.degrees);
var a180=bimComputeAngularDim([0,0],[1,0],[-1,0.0001]);
assert('near-straight rays measure close to 180 degrees', a180.degrees>179&&a180.degrees<=180, a180.degrees);
var aRev=bimComputeAngularDim([0,0],[0,1],[1,0]);
assert('reversing ray order gives the same absolute angle', approx(aRev.degrees,90), aRev.degrees);
assert('sweep sign flips with ray order (direction preserved for arc drawing)', (a90.sweep>0)!==(aRev.sweep>0));
assert('degenerate ray (zero length) is rejected', bimComputeAngularDim([0,0],[0,0],[1,0])===null);
assert('arc radius is derived from the shorter ray so the arc stays inside both', a45.radius<=Math.sqrt(2)*0.6+1e-9);

// ---- Circle from 3 points ----
var c1=bimCircleFrom3Points([1,0],[0,1],[-1,0]);
assert('3 points on the unit circle recover center at origin', c1&&approx(c1.center[0],0)&&approx(c1.center[1],0), c1&&JSON.stringify(c1.center));
assert('3 points on the unit circle recover radius 1', approx(c1.radius,1), c1.radius);
var c2=bimCircleFrom3Points([5,5],[9,5],[7,7]);
assert('offset circle recovers a center on the correct axis of symmetry', approx(c2.center[0],7), c2.center[0]);
assert('collinear points are rejected (no circle exists)', bimCircleFrom3Points([0,0],[1,1],[2,2])===null);

// ---- Radial / diameter ----
var rad=bimComputeRadialDim([0,0],5,[10,0],false);
assert('radius dimension value equals the radius', approx(rad.value,5));
assert('radius leader starts at the center', approx(rad.start[0],0)&&approx(rad.start[1],0));
assert('radius leader ends exactly on the circle edge', approx(rad.edge[0],5)&&approx(rad.edge[1],0), JSON.stringify(rad.edge));
var dia=bimComputeRadialDim([0,0],5,[10,0],true);
assert('diameter dimension value is twice the radius', approx(dia.value,10));
assert('diameter line spans the full circle (start on the opposite edge)', approx(dia.start[0],-5)&&approx(dia.edge[0],5));
var radAng=bimComputeRadialDim([2,3],4,[2,99],false);
assert('radial dimension respects the chosen angle direction', approx(radAng.edge[0],2)&&approx(radAng.edge[1],7), JSON.stringify(radAng.edge));

// ---- Leader ----
var ld=bimComputeLeader([0,0],[2,2],[4,2]);
assert('leader landing extends toward the text side', ld.landing[0]>ld.elbow[0]);
assert('leader landing is horizontal from the elbow', approx(ld.landing[1],ld.elbow[1]));
var ldL=bimComputeLeader([0,0],[2,2],[-4,2]);
assert('leader landing flips direction when text is to the left', ldL.landing[0]<ldL.elbow[0]);
assert('leader preserves its anchor (arrow tip) exactly', approx(ld.anchor[0],0)&&approx(ld.anchor[1],0));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
