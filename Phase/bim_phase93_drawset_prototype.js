/* bim_phase93_drawset_prototype.js

   Phase 93 geometry: POLYGON, DONUT, CIRCLE-as-a-real-circle, and the arc-length walk that
   DIVIDE and MEASURE both need.

   The one piece of real maths here is bimPointAtLength: where on a polyline that may contain
   arcs is the point a given distance along it. DIVIDE places N-1 of them at equal spacing,
   MEASURE places them every d until the length runs out. Both must measure along the CURVE -
   stepping along chords would bunch the marks up wherever the line bends, which is exactly where
   a drafter is looking.

   Conventions from V88: bulge = tan(sweep/4), positive = counter-clockwise. A full circle is
   two vertices, each with bulge 1 - DXF's own convention, and the reason CIRCLE stops being a
   24-sided polygon in this phase. */

function bimCircleFrom3Points(p1,p2,p3){
  var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
  var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
  if(Math.abs(d)<1e-9)return null;
  var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
  var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
  return {center:[ux,uy],radius:Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2))};
}
var BIM_BULGE_EPS=1e-9;
function bimBulgeAt(bulges,i){
  if(!bulges||i<0||i>=bulges.length)return 0;
  var b=bulges[i];
  return (typeof b==='number'&&isFinite(b))?b:0;
}
function bimBulgeArc(p1,p2,b){
  if(!p1||!p2||!isFinite(b)||Math.abs(b)<BIM_BULGE_EPS)return null;
  var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
  var c=Math.sqrt(dx*dx+dz*dz);
  if(c<1e-12)return null;
  var ux=dx/c,uz=dz/c;
  var mx=uz,mz=-ux;
  var sag=b*c/2;
  var apex=[(p1[0]+p2[0])/2+mx*sag,(p1[1]+p2[1])/2+mz*sag];
  var cir=bimCircleFrom3Points(p1,apex,p2);
  if(!cir)return null;
  var sweep=4*Math.atan(b);
  var a1=Math.atan2(p1[1]-cir.center[1],p1[0]-cir.center[0]);
  return {center:cir.center,radius:cir.radius,a1:a1,a2:a1+sweep,sweep:sweep,apex:apex,chord:c};
}
function bimArcPointAt(arc,t){
  var a=arc.a1+arc.sweep*t;
  return [arc.center[0]+Math.cos(a)*arc.radius,arc.center[1]+Math.sin(a)*arc.radius];
}
function bimSegLength(A,B,bulge){
  var arc=bimBulgeArc(A,B,bulge);
  if(arc)return Math.abs(arc.sweep)*arc.radius;
  return Math.sqrt((B[0]-A[0])*(B[0]-A[0])+(B[1]-A[1])*(B[1]-A[1]));
}
function bimBulgedLength(pts,bulges,closed){
  if(!pts||pts.length<2)return 0;
  var n=pts.length,segs=closed?n:n-1,L=0,i;
  for(i=0;i<segs;i++)L+=bimSegLength(pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i));
  return L;
}

/* ---------------------------------------------------------------- the arc-length walk */
/* The point a distance s along the polyline, measured ALONG THE CURVE. Returns null when s is
   outside [0, total]. */
function bimPointAtLength(pts,bulges,closed,s){
  if(!pts||pts.length<2)return null;
  var total=bimBulgedLength(pts,bulges,closed);
  if(!(s>=-1e-9)||s>total+1e-9)return null;
  s=Math.max(0,Math.min(total,s));
  var n=pts.length,segs=closed?n:n-1,acc=0,i;
  for(i=0;i<segs;i++){
    var A=pts[i],B=pts[(i+1)%n],b=bimBulgeAt(bulges,i);
    var segLen=bimSegLength(A,B,b);
    if(segLen<1e-12)continue;
    if(s<=acc+segLen+1e-9){
      var t=(s-acc)/segLen;
      t=Math.max(0,Math.min(1,t));
      var arc=bimBulgeArc(A,B,b);
      /* On an arc, equal LENGTH is equal ANGLE, so the segment parameter is the length
         fraction directly - which is only true because the radius is constant. */
      return arc?bimArcPointAt(arc,t)
                :[A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t];
    }
    acc+=segLen;
  }
  var lastA=pts[segs-1],lastB=pts[segs%n];
  return [lastB[0],lastB[1]];
}
/* DIVIDE: N segments means N-1 marks, and neither endpoint is marked - AutoCAD's own rule. */
function bimDividePoints(pts,bulges,closed,n){
  if(!(n>=2)||Math.floor(n)!==n)return {error:'Number of segments must be a whole number of 2 or more'};
  if(n>1000)return {error:'That is more divisions than this command will place (limit 1000)'};
  var total=bimBulgedLength(pts,bulges,closed);
  if(total<1e-9)return {error:'That object has no length to divide'};
  var out=[],i;
  for(i=1;i<n;i++){
    var p=bimPointAtLength(pts,bulges,closed,total*i/n);
    if(p)out.push(p);
  }
  return {points:out,spacing:total/n,total:total};
}
/* MEASURE: marks every d from the START, and the leftover at the far end is expected - that is
   the difference between MEASURE and DIVIDE. */
function bimMeasurePoints(pts,bulges,closed,d){
  if(!isFinite(d)||d<=1e-9)return {error:'Spacing must be greater than zero'};
  var total=bimBulgedLength(pts,bulges,closed);
  if(total<1e-9)return {error:'That object has no length to measure along'};
  if(d>total)return {error:'Spacing is longer than the object'};
  if(total/d>1000)return {error:'That spacing would place more than 1000 points'};
  var out=[],s=d;
  while(s<=total+1e-9){
    var p=bimPointAtLength(pts,bulges,closed,s);
    if(p)out.push(p);
    s+=d;
  }
  /* A closed loop's last mark can land exactly on the start; drop it rather than stack two. */
  if(closed&&out.length){
    var f=bimPointAtLength(pts,bulges,closed,0);
    var l=out[out.length-1];
    if(f&&Math.abs(f[0]-l[0])<1e-9&&Math.abs(f[1]-l[1])<1e-9)out.pop();
  }
  return {points:out,spacing:d,total:total,leftover:total-Math.floor(total/d+1e-9)*d};
}

/* ---------------------------------------------------------------- shapes */
/* A real circle: two vertices, each bulge 1. Exact, editable, and what DXF stores. */
function bimCircleSketch(center,radius){
  if(!(radius>1e-6))return {error:'Circle radius must be greater than zero'};
  return {pts:[[center[0]-radius,center[1]],[center[0]+radius,center[1]]],bulges:[1,1],closed:true};
}
/* POLYGON, AutoCAD's two forms: INSCRIBED puts the vertices on the circle, CIRCUMSCRIBED puts
   the edge midpoints on it - so a circumscribed polygon of the same radius is larger. */
function bimPolygonSketch(center,sides,radius,circumscribed,startAngle){
  if(!(sides>=3)||Math.floor(sides)!==sides)return {error:'A polygon needs a whole number of 3 or more sides'};
  if(sides>1024)return {error:'That is more sides than this command will draw (limit 1024)'};
  if(!(radius>1e-6))return {error:'Polygon radius must be greater than zero'};
  var R=circumscribed?radius/Math.cos(Math.PI/sides):radius;
  var a0=(typeof startAngle==='number')?startAngle:Math.PI/2;
  var pts=[],i;
  for(i=0;i<sides;i++){
    var a=a0+i*2*Math.PI/sides;
    pts.push([center[0]+Math.cos(a)*R,center[1]+Math.sin(a)*R]);
  }
  return {pts:pts,bulges:null,closed:true,vertexRadius:R};
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}
function polyArea(pts,bulges,closed){
  var N=pts.length,a=0,i,j;
  for(i=0;i<N;i++){j=(i+1)%N;a+=pts[i][0]*pts[j][1]-pts[j][0]*pts[i][1];}
  a/=2;
  var segs=closed?N:N-1;
  for(i=0;i<segs;i++){
    var arc=bimBulgeArc(pts[i],pts[(i+1)%N],bimBulgeAt(bulges,i));
    if(!arc)continue;
    a+=arc.radius*arc.radius*(arc.sweep-Math.sin(arc.sweep))/2;
  }
  return Math.abs(a);
}

console.log('-- a circle is a circle, not a 24-sided polygon');
var c=bimCircleSketch([3,4],2);
ck(c.pts.length===2&&c.bulges[0]===1&&c.bulges[1]===1,
   'two vertices, both bulge 1 -> '+JSON.stringify(c.pts)+' '+JSON.stringify(c.bulges));
ck(near(bimBulgedLength(c.pts,c.bulges,true),2*Math.PI*2,1e-9),
   'circumference is exactly 2*pi*r -> '+bimBulgedLength(c.pts,c.bulges,true).toFixed(9));
ck(near(polyArea(c.pts,c.bulges,true),Math.PI*4,1e-9),
   'and the area is exactly pi*r^2 -> '+polyArea(c.pts,c.bulges,true).toFixed(9));
/* what the OLD 24-gon gave, for contrast */
var poly24=[],k;
for(k=0;k<24;k++){var an=k/24*Math.PI*2;poly24.push([3+Math.cos(an)*2,4+Math.sin(an)*2]);}
var err24=Math.abs(polyArea(poly24,null,true)-Math.PI*4);
ck(err24>0.02,'the 24-gon it replaces was out by '+err24.toFixed(4)+' m2 on a 2m circle');
ck(!!bimCircleSketch([0,0],0).error,'a zero radius is refused');

console.log('\n-- POLYGON, inscribed and circumscribed');
var hex=bimPolygonSketch([0,0],6,1,false);
ck(hex.pts.length===6,'a hexagon has six vertices');
ck(hex.pts.every(function(p){return near(Math.sqrt(p[0]*p[0]+p[1]*p[1]),1,1e-9);}),
   'inscribed: every VERTEX sits on the circle of the given radius');
ck(near(polyArea(hex.pts,null,true),6*(Math.sqrt(3)/4),1e-9),
   'and its area is the textbook 6*(sqrt3/4)*r^2 -> '+polyArea(hex.pts,null,true).toFixed(9));
var hexC=bimPolygonSketch([0,0],6,1,true);
var apo=[];
for(k=0;k<6;k++){
  var A=hexC.pts[k],B=hexC.pts[(k+1)%6];
  apo.push(Math.sqrt(Math.pow((A[0]+B[0])/2,2)+Math.pow((A[1]+B[1])/2,2)));
}
ck(apo.every(function(v){return near(v,1,1e-9);}),
   'circumscribed: every EDGE MIDPOINT sits on it instead -> '+apo[0].toFixed(9));
ck(polyArea(hexC.pts,null,true)>polyArea(hex.pts,null,true),
   'so the circumscribed polygon is the larger of the two ('
   +polyArea(hexC.pts,null,true).toFixed(4)+' > '+polyArea(hex.pts,null,true).toFixed(4)+')');
var tri=bimPolygonSketch([0,0],3,2,false);
ck(near(polyArea(tri.pts,null,true),3*Math.sqrt(3)/4*4,1e-9),
   'a triangle of radius 2 has area 3*sqrt3/4*r^2 -> '+polyArea(tri.pts,null,true).toFixed(9));
ck(!!bimPolygonSketch([0,0],2,1,false).error,'two sides is refused');
ck(!!bimPolygonSketch([0,0],6.5,1,false).error,'a fractional side count is refused');

console.log('\n-- walking a given distance along the curve');
var line=[[0,0],[10,0]];
ck(near(bimPointAtLength(line,null,false,2.5)[0],2.5),'2.5 along a straight 10 is x=2.5');
ck(near(bimPointAtLength(line,null,false,0)[0],0),'0 is the start');
ck(near(bimPointAtLength(line,null,false,10)[0],10),'and 10 is the end');
ck(bimPointAtLength(line,null,false,11)===null,'past the end is null, not clamped silently');
/* CCW semicircle (0,0)->(0,2) through (1,1): length pi, so pi/2 along is the apex (1,1) */
var semi=[[0,0],[0,2]],semiB=[1,0];
var half=bimPointAtLength(semi,semiB,false,Math.PI/2);
ck(near(half[0],1,1e-9)&&near(half[1],1,1e-9),
   'half way along a semicircle by LENGTH is (1,1) -> '+half);
/* the same fraction along the CHORD would be (0,1) - the distinction that matters */
ck(!(near(half[0],0,1e-9)&&near(half[1],1,1e-9)),'not the chord midpoint (0,1)');
var quarter=bimPointAtLength(semi,semiB,false,Math.PI/4);
ck(near(Math.sqrt(Math.pow(quarter[0],2)+Math.pow(quarter[1]-1,2)),1,1e-9),
   'and every walked point is exactly on the arc');

console.log('\n-- DIVIDE');
var d4=bimDividePoints(line,null,false,4);
ck(!d4.error&&d4.points.length===3,'dividing into 4 places 3 marks, not 4 or 5 -> '+d4.points.length);
ck(d4.points.map(function(p){return p[0];}).every(function(x,i){return near(x,2.5*(i+1));}),
   'at 2.5, 5 and 7.5 -> '+JSON.stringify(d4.points.map(function(p){return p[0];})));
var dArc=bimDividePoints(semi,semiB,false,2);
ck(dArc.points.length===1&&near(dArc.points[0][0],1,1e-9)&&near(dArc.points[0][1],1,1e-9),
   'dividing the semicircle in two marks the apex, not the chord middle -> '+dArc.points[0]);
var dArc4=bimDividePoints(semi,semiB,false,4);
var gaps=[];
for(k=0;k<dArc4.points.length;k++){
  var ang=Math.atan2(dArc4.points[k][1]-1,dArc4.points[k][0]-0);
  gaps.push(ang);
}
ck(dArc4.points.length===3&&near(gaps[1]-gaps[0],gaps[2]-gaps[1],1e-9),
   'four divisions of an arc are equally spaced in ANGLE as well as length');
ck(!!bimDividePoints(line,null,false,1).error,'one division is refused');
ck(!!bimDividePoints(line,null,false,2.5).error,'a fractional count is refused');

console.log('\n-- MEASURE');
var m3=bimMeasurePoints(line,null,false,3);
ck(!m3.error&&m3.points.length===3,'spacing 3 on a length of 10 places 3 marks -> '+m3.points.length);
ck(m3.points.map(function(p){return p[0];}).every(function(x,i){return near(x,3*(i+1));}),
   'at 3, 6 and 9, leaving 1 over -> '+JSON.stringify(m3.points.map(function(p){return p[0];})));
ck(near(m3.leftover,1,1e-9),'and the leftover is reported, not hidden -> '+m3.leftover.toFixed(6));
var mArc=bimMeasurePoints(semi,semiB,false,Math.PI/4);
ck(mArc.points.length===4,'measuring a semicircle every quarter-turn places 4 -> '+mArc.points.length);
ck(mArc.points.every(function(p){return near(Math.sqrt(p[0]*p[0]+Math.pow(p[1]-1,2)),1,1e-9);}),
   'all of them on the arc');
ck(!!bimMeasurePoints(line,null,false,0).error,'zero spacing is refused');
ck(!!bimMeasurePoints(line,null,false,50).error,'spacing longer than the object is refused');
var circ=bimCircleSketch([0,0],1);
var mCirc=bimMeasurePoints(circ.pts,circ.bulges,true,Math.PI/2);
ck(mCirc.points.length===3,
   'measuring a unit circle every quarter-circumference places 3, not 4 stacked on the start -> '
   +mCirc.points.length);

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
process.exit(bad.length?1:0);
