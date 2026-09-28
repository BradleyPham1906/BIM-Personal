/* bim_phase94_cline_prototype.js

   Phase 94 geometry: XLINE and RAY -- construction lines that have no endpoints.

   Three pieces of real maths:

   1. CLIPPING. An infinite line cannot be stored as two points, so every renderer has to be
      handed the piece of it that is visible right now. Liang-Barsky, parametric, with the
      parameter range being the only difference between an XLINE (-inf, +inf) and a RAY
      [0, +inf). Writing it slope-first is the classic mistake: a vertical construction line is
      the single most common one a drafter draws, and it is exactly the case a slope has no
      value for.

   2. INTERSECTION WITH FINITE GEOMETRY. The whole point of a construction line is snapping to
      where it crosses something. The line is unbounded, the thing it crosses is not, so the
      two parameters are tested against different ranges -- and getting that backwards produces
      snap points floating in space beyond the end of a wall.

   3. INTERSECTION WITH AN ARC, which is a circle test plus a sweep test. A crossing on the
      circle but not on the swept part of the arc is not a crossing.
*/

var BIM_BULGE_EPS=1e-9;
function bimCircleFrom3Points(p1,p2,p3){
  var ax=p1[0],ay=p1[1],bx=p2[0],by=p2[1],cx=p3[0],cy=p3[1];
  var d=2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by));
  if(Math.abs(d)<1e-9)return null;
  var ux=((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d;
  var uy=((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d;
  return {center:[ux,uy],radius:Math.sqrt(Math.pow(ax-ux,2)+Math.pow(ay-uy,2))};
}
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
function bimPointOnSweptArc(arc,p,tol){
  if(!arc)return false;
  tol=(typeof tol==='number'&&tol>0)?tol:1e-9;
  var d=Math.sqrt((p[0]-arc.center[0])*(p[0]-arc.center[0])+(p[1]-arc.center[1])*(p[1]-arc.center[1]));
  if(Math.abs(d-arc.radius)>tol)return false;
  var rel=Math.atan2(p[1]-arc.center[1],p[0]-arc.center[0])-arc.a1;
  if(arc.sweep>=0){
    while(rel<-1e-12)rel+=Math.PI*2;
    while(rel>=Math.PI*2)rel-=Math.PI*2;
    return rel<=arc.sweep+1e-9;
  }
  while(rel>1e-12)rel-=Math.PI*2;
  while(rel<=-Math.PI*2)rel+=Math.PI*2;
  return rel>=arc.sweep-1e-9;
}

/* ----------------------------------------------------------------- 1. the clipper */
/* Liang-Barsky against an axis-aligned rectangle. tMin/tMax start at the parameter range the
   entity actually has, which is the ONLY difference between an XLINE and a RAY. No slope is
   ever formed, so a vertical line is not a special case -- it is the p=0 branch that every
   other direction also takes for one of its two axes. */
function bimClipInfinite(P,dir,isRay,box){
  var len=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
  if(!(len>1e-12))return null;
  var d=[dir[0]/len,dir[1]/len];
  var tMin=isRay?0:-Infinity, tMax=Infinity;
  var p=[-d[0],d[0],-d[1],d[1]];
  var q=[P[0]-box.minX, box.maxX-P[0], P[1]-box.minZ, box.maxZ-P[1]];
  var i;
  for(i=0;i<4;i++){
    if(Math.abs(p[i])<1e-12){
      /* Parallel to this pair of edges: outside them means the line never enters the box at
         all, and no value of t can rescue it. */
      if(q[i]<0)return null;
      continue;
    }
    var t=q[i]/p[i];
    if(p[i]<0){ if(t>tMin)tMin=t; }
    else       { if(t<tMax)tMax=t; }
  }
  if(tMin>tMax)return null;
  if(!isFinite(tMin)||!isFinite(tMax))return null;
  return [[P[0]+d[0]*tMin,P[1]+d[1]*tMin],[P[0]+d[0]*tMax,P[1]+d[1]*tMax]];
}

/* ------------------------------------------------- 2. crossing a finite straight segment */
/* t is the parameter on the INFINITE line and is bounded only for a ray; u is the parameter
   on the SEGMENT and is always bounded to [0,1]. Two different ranges, and swapping them is
   what puts a snap point out past the end of a wall. */
function bimClineSegIntersect(P,dir,isRay,A,B){
  var rx=dir[0],rz=dir[1];
  var sx=B[0]-A[0],sz=B[1]-A[1];
  var den=rx*sz-rz*sx;
  if(Math.abs(den)<1e-12)return null;          /* parallel, or a zero-length segment */
  var qpx=A[0]-P[0],qpz=A[1]-P[1];
  var t=(qpx*sz-qpz*sx)/den;
  var u=(qpx*rz-qpz*rx)/den;
  if(u<-1e-9||u>1+1e-9)return null;            /* past an end of the finite segment */
  if(isRay&&t<-1e-9)return null;               /* behind the ray's start */
  return [P[0]+rx*t,P[1]+rz*t];
}

/* ----------------------------------------------------- 3. crossing a bulged arc segment */
function bimClineCircleHits(P,dir,isRay,C,r){
  var a=dir[0]*dir[0]+dir[1]*dir[1];
  if(a<1e-18)return [];
  var fx=P[0]-C[0],fz=P[1]-C[1];
  var b=2*(fx*dir[0]+fz*dir[1]);
  var c=fx*fx+fz*fz-r*r;
  var disc=b*b-4*a*c;
  if(disc<-1e-12)return [];
  var sq=Math.sqrt(Math.max(0,disc));
  var ts=[(-b-sq)/(2*a)];
  if(sq>1e-9)ts.push((-b+sq)/(2*a));
  var out=[],i;
  for(i=0;i<ts.length;i++){
    if(isRay&&ts[i]<-1e-9)continue;
    out.push([P[0]+dir[0]*ts[i],P[1]+dir[1]*ts[i]]);
  }
  return out;
}
function bimClineArcIntersect(P,dir,isRay,A,B,bulge){
  var arc=bimBulgeArc(A,B,bulge);
  if(!arc)return bimClineSegIntersect(P,dir,isRay,A,B)?[bimClineSegIntersect(P,dir,isRay,A,B)]:[];
  var hits=bimClineCircleHits(P,dir,isRay,arc.center,arc.radius);
  var out=[],i;
  for(i=0;i<hits.length;i++)
    if(bimPointOnSweptArc(arc,hits[i],1e-7))out.push(hits[i]);
  return out;
}
/* Every crossing between one construction line and one polyline that may carry arcs. */
function bimClineCrossings(P,dir,isRay,pts,bulges,closed){
  if(!pts||pts.length<2)return [];
  var n=pts.length,segs=closed?n:n-1,out=[],i,k,h;
  for(i=0;i<segs;i++){
    var b=bimBulgeAt(bulges,i);
    if(Math.abs(b)<BIM_BULGE_EPS){
      h=bimClineSegIntersect(P,dir,isRay,pts[i],pts[(i+1)%n]);
      if(h)out.push(h);
    }else{
      var hs=bimClineArcIntersect(P,dir,isRay,pts[i],pts[(i+1)%n],b);
      for(k=0;k<hs.length;k++)out.push(hs[k]);
    }
  }
  return out;
}

/* --------------------------------------------------------------- 4. the construction modes */
/* AutoCAD's XLINE offers Hor/Ver/Ang. The DIRECTION is what each mode produces, and it is the
   only thing they differ in -- so one function answers all three and the prompt can derive its
   bracket list from the same table the keys consult. */
var BIM_CLINE_MODES={
  two:   {key:'',  label:'',           needsSecond:true },
  hor:   {key:'H', label:'Horizontal', needsSecond:false, dir:[1,0]},
  ver:   {key:'V', label:'Vertical',   needsSecond:false, dir:[0,1]},
  ang:   {key:'A', label:'Angle',      needsSecond:true }
};
function bimClineDir(mode,root,second,angleDeg){
  var m=BIM_CLINE_MODES[mode];
  if(!m)return null;
  if(m.dir)return [m.dir[0],m.dir[1]];
  if(mode==='ang'){
    if(typeof angleDeg==='number'&&isFinite(angleDeg)){
      var a=angleDeg*Math.PI/180;
      return [Math.cos(a),Math.sin(a)];
    }
    return null;
  }
  if(!second)return null;
  var dx=second[0]-root[0],dz=second[1]-root[1];
  if(Math.sqrt(dx*dx+dz*dz)<1e-9)return null;
  return [dx,dz];
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}
function pt(p){return p?('('+p[0].toFixed(4)+','+p[1].toFixed(4)+')'):'null';}
var BOX={minX:-10,maxX:10,minZ:-10,maxZ:10};

console.log('-- clipping an XLINE to the view');
var c=bimClipInfinite([0,0],[1,1],false,BOX);
ck(c&&near(Math.min(c[0][0],c[1][0]),-10)&&near(Math.max(c[0][0],c[1][0]),10),
   'a 45 degree line through the origin spans the box corner to corner -> '+pt(c[0])+' '+pt(c[1]));
var v=bimClipInfinite([3,0],[0,1],false,BOX);
ck(v&&near(v[0][0],3)&&near(v[1][0],3)&&near(Math.min(v[0][1],v[1][1]),-10)&&near(Math.max(v[0][1],v[1][1]),10),
   'a VERTICAL line clips without ever forming a slope -> '+pt(v[0])+' '+pt(v[1]));
var h=bimClipInfinite([0,-4],[1,0],false,BOX);
ck(h&&near(h[0][1],-4)&&near(h[1][1],-4)&&near(Math.min(h[0][0],h[1][0]),-10),
   'and a HORIZONTAL one likewise -> '+pt(h[0])+' '+pt(h[1]));
ck(bimClipInfinite([0,40],[1,0],false,BOX)===null,
   'a line that misses the box entirely clips to nothing, not to a zero-length stub');
var edge=bimClipInfinite([0,10],[1,0],false,BOX);
ck(edge&&near(edge[0][1],10),'a line lying exactly along the top edge still clips -> '+pt(edge[0]));
ck(bimClipInfinite([0,0],[0,0],false,BOX)===null,'a zero direction is refused');

console.log('\n-- a RAY is the same clip with one end of the range moved');
var r1=bimClipInfinite([0,0],[1,0],true,BOX);
ck(r1&&near(r1[0][0],0)&&near(r1[1][0],10),
   'a ray from the origin along +x starts AT the origin, not at the box edge -> '+pt(r1[0])+' '+pt(r1[1]));
var rx=bimClipInfinite([0,0],[1,0],false,BOX);
ck(rx&&near(rx[0][0],-10),'while the XLINE through the same point runs both ways -> '+pt(rx[0]));
ck(bimClipInfinite([20,0],[1,0],true,BOX)===null,
   'a ray starting outside the box and pointing away clips to nothing');
var rin=bimClipInfinite([20,0],[-1,0],true,BOX);
ck(rin&&near(rin[0][0],10)&&near(rin[1][0],-10),
   'but one pointing back INTO it clips to the crossing, not to its origin -> '+pt(rin[0])+' '+pt(rin[1]));

console.log('\n-- crossing a finite segment');
var s=bimClineSegIntersect([0,0],[0,1],false,[-5,3],[5,3]);
ck(s&&near(s[0],0)&&near(s[1],3),'a vertical xline crosses a horizontal wall at (0,3) -> '+pt(s));
ck(bimClineSegIntersect([0,0],[0,1],false,[2,3],[8,3])===null,
   'and does NOT cross a wall that stops short of it -- the segment parameter is bounded');
ck(bimClineSegIntersect([0,0],[1,0],false,[-5,3],[5,3])===null,'a parallel wall gives no crossing');
var behind=bimClineSegIntersect([0,0],[0,1],true,[-5,-3],[5,-3]);
ck(behind===null,'a RAY does not cross what is behind it');
var ahead=bimClineSegIntersect([0,0],[0,1],true,[-5,3],[5,3]);
ck(ahead&&near(ahead[1],3),'but does cross what is ahead -> '+pt(ahead));
var far=bimClineSegIntersect([0,0],[0,1],false,[-5,-3],[5,-3]);
ck(far&&near(far[1],-3),'while the XLINE crosses both -> '+pt(far));

console.log('\n-- crossing an arc');
/* FIRST establish which half of the circle the bulge actually sweeps, rather than assuming it.
   The V88 convention is that a positive bulge puts the centre LEFT of travel and swells the arc
   RIGHT, and getting it backwards is the single most expensive mistake in this codebase -- it
   cost V88 a day. So the test asks the arc where its apex is and builds every case from that
   answer, instead of writing a number down and hoping. */
var B1=1;
var UP=bimBulgeArc([2,0],[-2,0],B1);      /* travel -x, bulge +1 */
ck(UP&&near(UP.center[0],0)&&near(UP.center[1],0)&&near(UP.radius,2),
   '(2,0)->(-2,0) bulge 1 is a semicircle of radius 2 about the origin -> c='+pt(UP.center));
ck(UP&&near(UP.apex[0],0)&&near(UP.apex[1],2),
   'and it sweeps through (0,2), NOT (0,-2) -- stated by the arc, not assumed -> '+pt(UP.apex));
var DOWN=bimBulgeArc([-2,0],[2,0],B1);
ck(DOWN&&near(DOWN.apex[1],-2),'reversing the chord sweeps the other half -> '+pt(DOWN.apex));

var arcHits=bimClineArcIntersect([0,-5],[0,1],false,[2,0],[-2,0],B1);
ck(arcHits.length===1&&near(arcHits[0][0],0)&&near(arcHits[0][1],2),
   'a vertical xline through the centre meets the SWEPT half once, at its apex -> '+
   arcHits.map(pt).join(' '));
var other=bimClineArcIntersect([0,-5],[0,1],false,[-2,0],[2,0],B1);
ck(other.length===1&&near(other[0][1],-2),
   'the other half of the SAME circle is met at (0,-2) instead -- the sweep decides, not the '+
   'circle -> '+other.map(pt).join(' '));
var twice=bimClineArcIntersect([0,1],[1,0],false,[2,0],[-2,0],B1);
ck(twice.length===2,'a chord line crosses one arc twice -> '+twice.map(pt).join(' '));
ck(twice.length===2&&twice.every(function(p){return near(Math.sqrt(p[0]*p[0]+p[1]*p[1]),2,1e-9);}),
   'and both crossings are exactly on the circle');
var tangent=bimClineArcIntersect([0,2],[1,0],false,[2,0],[-2,0],B1);
ck(tangent.length===1&&near(tangent[0][0],0)&&near(tangent[0][1],2),
   'a tangent line touches once, not twice -> '+tangent.map(pt).join(' '));
ck(bimClineArcIntersect([0,9],[1,0],false,[2,0],[-2,0],B1).length===0,
   'a line clear of the circle meets it not at all');

console.log('\n-- crossings against a whole polyline');
var box4=[[0,0],[10,0],[10,10],[0,10]];
var cr=bimClineCrossings([5,-5],[0,1],false,box4,null,true);
ck(cr.length===2,'a vertical xline through a closed square crosses it twice -> '+cr.map(pt).join(' '));
/* The closing edge of this square is the one at x=0, so the line that proves closure matters
   has to be the HORIZONTAL one. A vertical line at x=5 crosses the top and bottom either way
   and would report "2" whether the loop closed or not -- a check that cannot fail. */
var crH=bimClineCrossings([-5,5],[1,0],false,box4,null,true);
ck(crH.length===2,'a horizontal xline through the CLOSED square crosses it twice -> '+
   crH.map(pt).join(' '));
var crOpen=bimClineCrossings([-5,5],[1,0],false,box4,null,false);
ck(crOpen.length===1&&near(crOpen[0][0],10),
   'the same square left OPEN is crossed once -- the closing edge is gone -> '+
   crOpen.map(pt).join(' '));
var crRay=bimClineCrossings([5,5],[0,1],true,box4,null,true);
ck(crRay.length===1&&near(crRay[0][1],10),
   'a ray from inside the square leaves through one side only -> '+crRay.map(pt).join(' '));
/* a circle stored the V93 way: two vertices, both bulge 1 */
var circPts=[[-2,0],[2,0]],circB=[1,1];
var crCirc=bimClineCrossings([-9,0.5],[1,0],false,circPts,circB,true);
ck(crCirc.length===2,'and a V93 two-vertex circle is crossed twice -> '+crCirc.map(pt).join(' '));
ck(crCirc.length===2&&crCirc.every(function(p){return near(Math.sqrt(p[0]*p[0]+p[1]*p[1]),2,1e-7);}),
   'both on the circle of radius 2');

console.log('\n-- the construction modes');
ck(bimClineDir('hor',[3,4])[0]===1&&bimClineDir('hor',[3,4])[1]===0,'H gives a horizontal direction');
ck(bimClineDir('ver',[3,4])[0]===0&&bimClineDir('ver',[3,4])[1]===1,'V gives a vertical one');
var d30=bimClineDir('ang',[0,0],null,30);
ck(d30&&near(d30[0],Math.cos(Math.PI/6))&&near(d30[1],Math.sin(Math.PI/6)),
   'A 30 gives 30 degrees from +x -> '+pt(d30));
var d2=bimClineDir('two',[0,0],[3,4]);
ck(d2&&near(d2[0],3)&&near(d2[1],4),'and two points give the direction between them -> '+pt(d2));
ck(bimClineDir('two',[1,1],[1,1])===null,'two identical points define no direction');
ck(bimClineDir('ang',[0,0],null,null)===null,'Angle with no angle defines none either');
/* the bracket list a prompt would print, derived from the same table the keys consult */
var offered=Object.keys(BIM_CLINE_MODES).filter(function(k){return BIM_CLINE_MODES[k].key;})
  .map(function(k){return BIM_CLINE_MODES[k].label;});
ck(offered.length===3&&offered.indexOf('Horizontal')>=0&&offered.indexOf('Bisect')<0,
   'the offered modes are derived, and Bisect is not among them because it is not built -> ['+
   offered.join('/')+']');

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
