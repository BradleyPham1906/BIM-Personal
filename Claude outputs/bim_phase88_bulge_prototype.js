/* bim_phase88_bulge_prototype.js -- the arc math, proved before it goes into the build.
   bulge = tan(sweep/4), signed, positive = counter-clockwise. DXF group code 42. */
function bimCircleFrom3Points(p1,p2,p3){
  var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
  var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
  if(Math.abs(d)<1e-9)return null;
  var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
  var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
  return {center:[ux,uy],radius:Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2))};
}
var BULGE_EPS=1e-9;
function bimBulgeAt(bulges,i){
  if(!bulges||i<0||i>=bulges.length)return 0;
  var b=bulges[i];
  return (typeof b==='number'&&isFinite(b))?b:0;
}
function bimBulgeArc(p1,p2,b){
  if(!p1||!p2||Math.abs(b)<BULGE_EPS)return null;
  var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
  var c=Math.sqrt(dx*dx+dz*dz);
  if(c<1e-12)return null;
  var ux=dx/c,uz=dz/c;
  /* Rotate the chord direction by -90deg. For a POSITIVE (counter-clockwise) bulge the centre
     lies to the LEFT of travel, so the arc itself swells to the RIGHT: chord (0,0)-(2,0) with
     bulge +1 is the semicircle through (1,-1), not (1,1). Getting this backwards was the first
     bug this prototype caught. */
  var mx=uz,mz=-ux;
  var sag=b*c/2;                          /* sagitta, signed */
  var apex=[(p1[0]+p2[0])/2+mx*sag,(p1[1]+p2[1])/2+mz*sag];
  var cir=bimCircleFrom3Points(p1,apex,p2);
  if(!cir)return null;
  var sweep=4*Math.atan(b);
  var a1=Math.atan2(p1[1]-cir.center[1],p1[0]-cir.center[0]);
  return {center:cir.center,radius:cir.radius,a1:a1,a2:a1+sweep,sweep:sweep,apex:apex,chord:c};
}
function bimArcSegments(radius,sweep,tol){
  tol=(typeof tol==='number'&&tol>0)?tol:0.002;
  var s=Math.abs(sweep);
  if(!isFinite(radius)||radius<=tol)return 2;
  var maxStep=2*Math.acos(Math.max(-1,Math.min(1,1-tol/radius)));
  if(!isFinite(maxStep)||maxStep<1e-6)maxStep=Math.PI/64;
  return Math.max(2,Math.min(256,Math.ceil(s/maxStep)));
}
function bimBulgeSegPoints(p1,p2,b,tol){
  var arc=bimBulgeArc(p1,p2,b);
  if(!arc)return [];
  var n=bimArcSegments(arc.radius,arc.sweep,tol),out=[],k;
  for(k=1;k<n;k++){
    var a=arc.a1+arc.sweep*(k/n);
    out.push([arc.center[0]+Math.cos(a)*arc.radius,arc.center[1]+Math.sin(a)*arc.radius]);
  }
  return out;
}
function bimFlattenPoly(pts,bulges,closed,tol){
  if(!pts||pts.length<2)return pts?pts.map(function(p){return [p[0],p[1]];}):[];
  var n=pts.length,segs=closed?n:n-1,out=[],i;
  for(i=0;i<segs;i++){
    out.push([pts[i][0],pts[i][1]]);
    var mid=bimBulgeSegPoints(pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i),tol);
    for(var k=0;k<mid.length;k++)out.push(mid[k]);
  }
  if(!closed)out.push([pts[n-1][0],pts[n-1][1]]);
  return out;
}
function bimBulgeFrom3Pts(p1,pm,p2){
  var cir=bimCircleFrom3Points(p1,pm,p2);
  if(!cir)return 0;
  var a1=Math.atan2(p1[1]-cir.center[1],p1[0]-cir.center[0]);
  var am=Math.atan2(pm[1]-cir.center[1],pm[0]-cir.center[0]);
  var a2=Math.atan2(p2[1]-cir.center[1],p2[0]-cir.center[0]);
  function norm(a){while(a<0)a+=Math.PI*2;while(a>=Math.PI*2)a-=Math.PI*2;return a;}
  var dm=norm(am-a1),d2=norm(a2-a1);
  var sweep=(dm<d2)?d2:-(Math.PI*2-d2);   /* CCW if the middle point is reached first that way */
  return Math.tan(sweep/4);
}
function bimBulgedLength(pts,bulges,closed){
  if(!pts||pts.length<2)return 0;
  var n=pts.length,segs=closed?n:n-1,L=0,i;
  for(i=0;i<segs;i++){
    var a=pts[i],b=pts[(i+1)%n];
    var arc=bimBulgeArc(a,b,bimBulgeAt(bulges,i));
    if(arc)L+=Math.abs(arc.sweep)*arc.radius;
    else L+=Math.sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1]));
  }
  return L;
}
function bimBulgedArea(pts,bulges,closed){
  if(!pts||pts.length<2)return 0;
  var n=pts.length,a=0,i;
  for(i=0;i<n;i++){var j=(i+1)%n;a+=pts[i][0]*pts[j][1]-pts[j][0]*pts[i][1];}
  a/=2;
  var segs=closed?n:n-1;
  for(i=0;i<segs;i++){
    var arc=bimBulgeArc(pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i));
    if(!arc)continue;
    var th=arc.sweep;
    a+=arc.radius*arc.radius*(th-Math.sin(th))/2;
  }
  return Math.abs(a);
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}

var arc=bimBulgeArc([0,0],[2,0],1);          /* half circle, CCW */
ck(near(arc.radius,1)&&near(arc.center[0],1)&&near(arc.center[1],0),
   'bulge 1 on a chord of 2 is a semicircle r=1 centred at (1,0) -> r='+arc.radius+' c='+arc.center);
ck(near(arc.sweep,Math.PI),'and sweeps +pi (CCW) -> '+arc.sweep);
ck(near(arc.apex[1],-1),'a positive (CCW) bulge swells BELOW a left-to-right chord -> '+arc.apex);
var arcN=bimBulgeArc([0,0],[2,0],-1);
ck(near(arcN.sweep,-Math.PI)&&near(arcN.apex[1],1),'a negative bulge swells the other way -> '+arcN.apex);
ck(bimBulgeArc([0,0],[2,0],0)===null,'bulge 0 is a straight segment (null arc)');

var q=bimBulgeArc([1,0],[0,1],Math.tan(Math.PI/2/4));   /* quarter circle, CCW about the origin */
ck(near(q.radius,1,1e-9)&&near(q.center[0],0,1e-9)&&near(q.center[1],0,1e-9),
   'quarter-circle bulge gives r=1 at the origin -> r='+q.radius+' c='+q.center);
ck(near(q.sweep,Math.PI/2,1e-9),'and sweeps +90deg -> '+(q.sweep*180/Math.PI).toFixed(4));
/* THE CHECK THAT SETTLES ORIENTATION WITHOUT ARGUING ABOUT IT: the arc a bulge describes has to
   end where the chord ends. A flipped perpendicular passes every radius test and fails this. */
function arcEndsAt(p1,p2,b){
  var a=bimBulgeArc(p1,p2,b);
  if(!a)return false;
  var e=[a.center[0]+Math.cos(a.a2)*a.radius,a.center[1]+Math.sin(a.a2)*a.radius];
  return near(e[0],p2[0],1e-9)&&near(e[1],p2[1],1e-9);
}
ck(arcEndsAt([0,0],[2,0],1),'the swept arc ENDS at p2 (semicircle, +1)');
ck(arcEndsAt([0,0],[2,0],-1),'the swept arc ends at p2 (semicircle, -1)');
ck(arcEndsAt([1,0],[0,1],Math.tan(Math.PI/8)),'the swept arc ends at p2 (quarter circle)');
ck(arcEndsAt([3,-2],[-1,5],0.37),'the swept arc ends at p2 (arbitrary chord and bulge)');

/* a full circle is two vertices, both bulge 1 -- the DXF convention */
ck(near(bimBulgedArea([[-1,0],[1,0]],[1,1],true),Math.PI,1e-9),
   'two vertices with bulge 1 each enclose pi (unit circle) -> '+bimBulgedArea([[-1,0],[1,0]],[1,1],true));
ck(near(bimBulgedLength([[-1,0],[1,0]],[1,1],true),2*Math.PI,1e-9),
   'and measure 2pi round -> '+bimBulgedLength([[-1,0],[1,0]],[1,1],true));

ck(near(bimBulgedLength([[0,0],[2,0]],[1],false),Math.PI,1e-9),
   'a half-circle chord of 2 measures pi, not 2 -> '+bimBulgedLength([[0,0],[2,0]],[1],false));
ck(near(bimBulgedLength([[0,0],[3,0],[3,4]],null,false),7),
   'with no bulges the length is the straight polyline -> '+bimBulgedLength([[0,0],[3,0],[3,4]],null,false));
ck(near(bimBulgedArea([[0,0],[4,0],[4,4],[0,4]],null,true),16),
   'and the area is the plain shoelace -> '+bimBulgedArea([[0,0],[4,0],[4,4],[0,4]],null,true));

var b3=bimBulgeFrom3Pts([0,0],[1,1],[2,0]);
ck(near(b3,-1,1e-9),'3-point arc (0,0)-(1,1)-(2,0) turns clockwise, so bulge -1 -> '+b3);
var b3n=bimBulgeFrom3Pts([0,0],[1,-1],[2,0]);
ck(near(b3n,1,1e-9),'and through (1,-1) it is bulge +1 -> '+b3n);
/* THE ROUND TRIP, which is what ARC actually depends on: the bulge derived from three points
   must describe an arc that passes through the middle one. This is the single check that keeps
   bimBulgeFrom3Pts and bimBulgeArc from disagreeing about orientation. */
/* Exact, not sampled. The first version of this walked the arc in 400 steps and asked whether
   any sample landed within 2mm of the middle point -- on a 4.6m arc the samples are 11mm apart,
   so it reported a failure that was entirely its own resolution. A test whose tolerance is
   tighter than its own sampling measures the test. */
function onSweptArc(a,p){
  var d=Math.sqrt(Math.pow(p[0]-a.center[0],2)+Math.pow(p[1]-a.center[1],2));
  if(Math.abs(d-a.radius)>1e-9)return false;
  var rel=Math.atan2(p[1]-a.center[1],p[0]-a.center[0])-a.a1;
  if(a.sweep>=0){while(rel<-1e-12)rel+=Math.PI*2;while(rel>=Math.PI*2)rel-=Math.PI*2;
    return rel<=a.sweep+1e-9;}
  while(rel>1e-12)rel-=Math.PI*2;while(rel<=-Math.PI*2)rel+=Math.PI*2;
  return rel>=a.sweep-1e-9;
}
function roundTrip(p1,pm,p2){
  var b=bimBulgeFrom3Pts(p1,pm,p2);
  var a=bimBulgeArc(p1,p2,b);
  return !!a&&onSweptArc(a,pm);
}
ck(roundTrip([0,0],[1,1],[2,0]),'round trip: 3 points -> bulge -> arc passes through the middle point (up)');
ck(roundTrip([0,0],[1,-1],[2,0]),'round trip: same, mirrored (down)');
ck(roundTrip([0,0],[0.3,1.4],[2,0]),'round trip: an off-centre middle point');
ck(roundTrip([5,5],[2,9],[-4,4]),'round trip: a major arc');
var b3c=bimBulgeFrom3Pts([0,0],[1,0.0001],[2,0]);
ck(Math.abs(b3c)<0.01,'a nearly straight 3-point arc gives a near-zero bulge -> '+b3c);
ck(bimBulgeFrom3Pts([0,0],[1,0],[2,0])===0,'exactly colinear gives 0 (no circle)');

var flat=bimFlattenPoly([[0,0],[2,0]],[1],false);
var maxErr=0;
for(var i=0;i<flat.length;i++){
  var d=Math.sqrt(Math.pow(flat[i][0]-1,2)+Math.pow(flat[i][1],2));
  maxErr=Math.max(maxErr,Math.abs(d-1));
}
ck(maxErr<1e-9,'every flattened point lies on the arc (max radial error '+maxErr.toExponential(2)+')');
ck(flat.length>=2&&near(flat[0][0],0)&&near(flat[flat.length-1][0],2),
   'flatten keeps the real endpoints -> '+flat.length+' points');
var chordErr=0;
for(var k=0;k+1<flat.length;k++){
  var mx=(flat[k][0]+flat[k+1][0])/2,my=(flat[k][1]+flat[k+1][1])/2;
  chordErr=Math.max(chordErr,Math.abs(1-Math.sqrt(Math.pow(mx-1,2)+Math.pow(my,2))));
}
ck(chordErr<=0.002+1e-9,'and no chord departs from the arc by more than the 2mm tolerance -> '+chordErr.toFixed(6));
var coarse=bimFlattenPoly([[0,0],[200,0]],[1],false);
var fine=bimFlattenPoly([[0,0],[0.2,0]],[1],false);
ck(coarse.length>fine.length,'a bigger arc gets more segments than a small one ('+coarse.length+' vs '+fine.length+')');
ck(bimFlattenPoly([[0,0],[3,0],[3,4]],null,false).length===3,
   'a polyline with no bulges flattens to itself, unchanged');

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
process.exit(bad.length?1:0);
