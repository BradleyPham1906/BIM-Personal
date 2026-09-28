/* bim_phase90_arcdraw_offset_prototype.js

   Two pieces of Phase 90 maths, proved before either reaches the build:

   1. TANGENT-CONTINUATION ARC. Given the direction a wall is already travelling at P and a new
      point Q, the arc that leaves P tangent to that direction and ends at Q. This is what makes
      a drawn curved wall flow instead of kinking, and it is one click per segment rather than
      two.

   2. ARC-AWARE OFFSET. A concentric offset of a circular arc subtends the SAME angle, so its
      bulge does not change at all - only the vertices move. The vertices, though, are the
      intersections of adjacent OFFSET segments, which for a line-arc or arc-arc joint needs a
      real intersection rather than the bisector the straight-only code uses. The circle-line
      intersection written here is also what arc-aware TRIM will need, so it is not throwaway.

   Conventions inherited from V88/V89: bulge = tan(sweep/4), positive = counter-clockwise; the
   segment normal points LEFT of travel, and a positive offset distance moves that way. */

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
function bimSegNormal(a,b){
  var dx=b[0]-a[0],dz=b[1]-a[1],len=Math.sqrt(dx*dx+dz*dz)||1;
  return [-dz/len,dx/len];
}

/* ---------------------------------------------------------------- 1. tangent continuation */
/* The angle between a tangent and a chord is half the arc it subtends, so the sweep is twice
   the angle from the incoming direction to the chord, and bulge = tan(sweep/4) = tan(alpha/2). */
function bimTangentBulge(dir,P,Q){
  var vx=Q[0]-P[0],vz=Q[1]-P[1];
  var vl=Math.sqrt(vx*vx+vz*vz);
  if(vl<1e-9)return null;
  var dl=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
  if(dl<1e-9)return null;
  var dx=dir[0]/dl,dz=dir[1]/dl;
  var ux=vx/vl,uz=vz/vl;
  var cross=dx*uz-dz*ux,dot=dx*ux+dz*uz;
  var alpha=Math.atan2(cross,dot);
  if(Math.abs(Math.abs(alpha)-Math.PI)<1e-6)return null;   /* doubling back: no finite arc */
  return Math.tan(alpha/2);
}
/* The direction a segment LEAVES its start point, used to chain one tangent arc to the next. */
function bimSegEndDir(A,B,bulge){
  var arc=bimBulgeArc(A,B,bulge);
  if(!arc){
    var dx=B[0]-A[0],dz=B[1]-A[1],L=Math.sqrt(dx*dx+dz*dz)||1;
    return [dx/L,dz/L];
  }
  /* tangent at the END of the arc: perpendicular to the radius, in the sweep direction */
  var rx=B[0]-arc.center[0],rz=B[1]-arc.center[1],L=Math.sqrt(rx*rx+rz*rz)||1;
  var s=arc.sweep>=0?1:-1;
  return [-s*rz/L,s*rx/L];
}

/* ---------------------------------------------------------------- 2. arc-aware offset */
function bimCircleLineIntersect(C,r,P,dir){
  var fx=P[0]-C[0],fz=P[1]-C[1];
  var a=dir[0]*dir[0]+dir[1]*dir[1];
  var b=2*(fx*dir[0]+fz*dir[1]);
  var c=fx*fx+fz*fz-r*r;
  var disc=b*b-4*a*c;
  if(disc<0)return [];
  var sq=Math.sqrt(disc);
  var t1=(-b-sq)/(2*a),t2=(-b+sq)/(2*a);
  var out=[[P[0]+dir[0]*t1,P[1]+dir[1]*t1]];
  if(Math.abs(t2-t1)>1e-12)out.push([P[0]+dir[0]*t2,P[1]+dir[1]*t2]);
  return out;
}
function bimCircleCircleIntersect(C1,r1,C2,r2){
  var dx=C2[0]-C1[0],dz=C2[1]-C1[1];
  var d=Math.sqrt(dx*dx+dz*dz);
  if(d<1e-12||d>r1+r2+1e-12||d<Math.abs(r1-r2)-1e-12)return [];
  var a=(r1*r1-r2*r2+d*d)/(2*d);
  var h2=r1*r1-a*a;
  var h=h2>0?Math.sqrt(h2):0;
  var mx=C1[0]+a*dx/d,mz=C1[1]+a*dz/d;
  if(h<1e-12)return [[mx,mz]];
  return [[mx+h*dz/d,mz-h*dx/d],[mx-h*dz/d,mz+h*dx/d]];
}
function bimNearestTo(list,ref){
  var best=null,bd=Infinity,i;
  for(i=0;i<list.length;i++){
    var d=Math.pow(list[i][0]-ref[0],2)+Math.pow(list[i][1]-ref[1],2);
    if(d<bd){bd=d;best=list[i];}
  }
  return best;
}
/* Each segment offsets on its own: a line to a parallel line, an arc to a CONCENTRIC arc whose
   radius changes by the offset distance and whose sweep - and therefore bulge - does not. */
function bimOffsetSegment(A,B,bulge,dist){
  var arc=bimBulgeArc(A,B,bulge);
  if(!arc){
    var nrm=bimSegNormal(A,B);
    return {kind:'line',A:[A[0]+nrm[0]*dist,A[1]+nrm[1]*dist],
                        B:[B[0]+nrm[0]*dist,B[1]+nrm[1]*dist],dir:[B[0]-A[0],B[1]-A[1]],bulge:0};
  }
  /* For a counter-clockwise arc the centre is to the LEFT of travel, which is the direction a
     positive offset moves, so the radius SHRINKS. Clockwise, it grows. */
  var s=arc.sweep>=0?1:-1;
  var nr=arc.radius-s*dist;
  if(nr<=1e-6)return {error:'Offset distance is larger than the arc radius'};
  var k=nr/arc.radius;
  function radial(P){
    return [arc.center[0]+(P[0]-arc.center[0])*k,arc.center[1]+(P[1]-arc.center[1])*k];
  }
  return {kind:'arc',A:radial(A),B:radial(B),center:arc.center,radius:nr,bulge:bulge};
}
function bimJoinOffsetSegments(s1,s2,ref){
  if(s1.kind==='line'&&s2.kind==='line'){
    var d1=s1.dir,d2=s2.dir;
    var den=d1[0]*d2[1]-d1[1]*d2[0];
    if(Math.abs(den)<1e-12)return s1.B;            /* parallel: the ends already coincide */
    var ex=s2.A[0]-s1.A[0],ez=s2.A[1]-s1.A[1];
    var t=(ex*d2[1]-ez*d2[0])/den;
    return [s1.A[0]+d1[0]*t,s1.A[1]+d1[1]*t];
  }
  if(s1.kind==='arc'&&s2.kind==='arc'){
    var hits=bimCircleCircleIntersect(s1.center,s1.radius,s2.center,s2.radius);
    return hits.length?bimNearestTo(hits,ref):s1.B;
  }
  var line=(s1.kind==='line')?s1:s2,arc=(s1.kind==='line')?s2:s1;
  var hits2=bimCircleLineIntersect(arc.center,arc.radius,line.A,line.dir);
  return hits2.length?bimNearestTo(hits2,ref):s1.B;
}
/* THE CORRECTION THE PROTOTYPE EARNED: "a concentric arc keeps its bulge" is true of the
   SEGMENT, but not of the stored bulge once the vertices move. At a tangent joint the offset
   vertex is the radial projection of the original, the sweep is unchanged, and the bulge really
   does carry over. At a KINK the vertex is where the offset line crosses the offset circle,
   which is somewhere else on that circle, so the arc now spans a different angle. The bulge has
   to be recomputed from the endpoints that actually ended up there - keeping the original value
   silently produces an arc that is no longer concentric with the one it came from. */
function bimArcBulgeBetween(center,A,B,sweepSign){
  var a1=Math.atan2(A[1]-center[1],A[0]-center[0]);
  var a2=Math.atan2(B[1]-center[1],B[0]-center[0]);
  var d=a2-a1;
  if(sweepSign>=0){while(d<-1e-12)d+=Math.PI*2;while(d>=Math.PI*2)d-=Math.PI*2;}
  else{while(d>1e-12)d-=Math.PI*2;while(d<=-Math.PI*2)d+=Math.PI*2;}
  return Math.tan(d/4);
}
function bimOffsetBulged(pts,bulges,closed,dist){
  if(!pts||pts.length<2)return {error:'Needs at least two points'};
  if(!isFinite(dist)||Math.abs(dist)<1e-9)return {error:'Offset distance cannot be zero'};
  var n=pts.length,segCount=closed?n:n-1,segs=[],i;
  for(i=0;i<segCount;i++){
    var s=bimOffsetSegment(pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i),dist);
    if(s.error)return {error:s.error};
    segs.push(s);
  }
  var outPts=[],outBulges=[];
  for(i=0;i<n;i++){
    var incoming=closed?segs[(i-1+n)%n]:(i>0?segs[i-1]:null);
    var outgoing=closed?segs[i%segCount]:(i<segCount?segs[i]:null);
    if(!incoming){outPts.push(outgoing.A);continue;}
    if(!outgoing){outPts.push(incoming.B);continue;}
    outPts.push(bimJoinOffsetSegments(incoming,outgoing,pts[i]));
  }
  for(i=0;i<segCount;i++){
    var sg=segs[i];
    if(sg.kind!=='arc'){outBulges.push(0);continue;}
    outBulges.push(bimArcBulgeBetween(sg.center,outPts[i],outPts[(i+1)%n],sg.bulge));
  }
  if(!closed)outBulges.push(0);
  return {pts:outPts,bulges:outBulges};
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}

console.log('-- tangent continuation');
var tb=bimTangentBulge([1,0],[0,0],[0,2]);
ck(near(tb,1,1e-12),'travelling +x at the origin and ending at (0,2) is a CCW semicircle, bulge +1 -> '+tb);
var tarc=bimBulgeArc([0,0],[0,2],tb);
ck(near(tarc.center[0],0,1e-9)&&near(tarc.center[1],1,1e-9)&&near(tarc.radius,1,1e-9),
   'centred at (0,1) with radius 1 -> c='+tarc.center+' r='+tarc.radius);
/* TANGENCY AT THE START is the whole point of this form: the arc must LEAVE along the incoming
   direction, or the wall kinks at the joint it was supposed to smooth. */
function startDir(arc){
  var rx=0-arc.center[0],rz=0-arc.center[1];   /* at P=(0,0) for these cases */
  var L=Math.sqrt(rx*rx+rz*rz)||1;
  var s=arc.sweep>=0?1:-1;
  return [-s*rz/L,s*rx/L];
}
var sd=startDir(tarc);
ck(near(sd[0],1,1e-9)&&near(sd[1],0,1e-9),'and it leaves along +x, tangent to the incoming run -> '+sd);
var tb2=bimTangentBulge([1,0],[0,0],[0,-2]);
ck(tb2<0&&near(tb2,-1,1e-12),'turning the other way gives the opposite sign -> '+tb2);
var tb3=bimTangentBulge([1,0],[0,0],[5,0.0001]);
ck(Math.abs(tb3)<1e-4,'a nearly straight continuation gives a nearly zero bulge -> '+tb3);
ck(bimTangentBulge([1,0],[0,0],[-3,0])===null,'doubling straight back is refused, not turned into an infinite arc');
ck(bimTangentBulge([1,0],[0,0],[0,0])===null,'and a zero-length segment is refused');

console.log('\n-- the end direction that chains one arc to the next');
var ed=bimSegEndDir([0,0],[0,2],1);
ck(near(ed[0],-1,1e-9)&&near(ed[1],0,1e-9),
   'a CCW semicircle from (0,0) to (0,2) arrives travelling -x -> '+ed);
var ed2=bimSegEndDir([0,0],[4,0],0);
ck(near(ed2[0],1,1e-9),'and a straight segment arrives along itself -> '+ed2);

console.log('\n-- arc-aware offset');
/* Quarter circle, CCW, radius 2, centred at the origin: (2,0) -> (0,2). */
var qb=Math.tan(Math.PI/2/4);
var off=bimOffsetBulged([[2,0],[0,2]],[qb,0],false,0.5);
ck(!off.error,'a single arc offsets ('+(off.error||'ok')+')');
ck(near(off.bulges[0],qb,1e-12),'THE BULGE IS UNCHANGED - a concentric arc subtends the same angle -> '+off.bulges[0]);
var oarc=bimBulgeArc(off.pts[0],off.pts[1],off.bulges[0]);
ck(near(oarc.radius,1.5,1e-9),'and the offset arc has radius 1.5, exactly 0.5 less -> '+oarc.radius);
ck(near(oarc.center[0],0,1e-9)&&near(oarc.center[1],0,1e-9),
   'sharing the original centre, which is what makes it concentric -> '+oarc.center);
var offOut=bimOffsetBulged([[2,0],[0,2]],[qb,0],false,-0.5);
var oarc2=bimBulgeArc(offOut.pts[0],offOut.pts[1],offOut.bulges[0]);
ck(near(oarc2.radius,2.5,1e-9),'a negative distance offsets outward to 2.5 -> '+oarc2.radius);
ck(!!bimOffsetBulged([[2,0],[0,2]],[qb,0],false,3).error,
   'offsetting inward by more than the radius is refused, not flipped');

console.log('\n-- offset still agrees with the straight case');
var so=bimOffsetBulged([[0,0],[10,0]],null,false,1);
ck(near(so.pts[0][1],1)&&near(so.pts[1][1],1),
   'a straight segment offsets to the LEFT of travel by 1 -> '+so.pts[0]+' '+so.pts[1]);
var corner=bimOffsetBulged([[0,0],[10,0],[10,10]],null,false,1);
ck(near(corner.pts[1][0],9)&&near(corner.pts[1][1],1),
   'and a right-angle corner mitres to (9,1) -> '+corner.pts[1]);

console.log('\n-- a line meeting an arc');
/* Straight run in along +x to (0,0), then the CCW semicircle up to (0,2): tangent joint. */
var mixed=bimOffsetBulged([[-4,0],[0,0],[0,2]],[0,1],false,0.5);
ck(!mixed.error,'a line-then-arc polyline offsets ('+(mixed.error||'ok')+')');
ck(near(mixed.pts[1][1],0.5,1e-9),
   'at a TANGENT joint the shared vertex moves straight along the common normal -> '+mixed.pts[1]);
var marc=bimBulgeArc(mixed.pts[1],mixed.pts[2],mixed.bulges[1]);
ck(near(marc.center[0],0,1e-9)&&near(marc.center[1],1,1e-9)&&near(marc.radius,0.5,1e-9),
   'and the offset arc stays concentric with the original -> c='+marc.center+' r='+marc.radius);

/* A KINK between a line and an arc: the vertex is a real circle-line intersection, and the
   bisector the straight-only code uses would put it somewhere else. */
var kink=bimOffsetBulged([[-4,-3],[0,0],[0,2]],[0,1],false,0.5);
var karc=bimBulgeArc(kink.pts[1],kink.pts[2],kink.bulges[1]);
ck(!kink.error&&near(karc.radius,0.5,1e-9)&&near(karc.center[1],1,1e-9),
   'at a KINK the offset arc is still exactly concentric -> r='+karc.radius+' c='+karc.center);
var onCircle=Math.abs(Math.sqrt(Math.pow(kink.pts[1][0]-0,2)+Math.pow(kink.pts[1][1]-1,2))-0.5);
ck(onCircle<1e-9,
   'and the shared vertex lies exactly ON the offset arc, so the two meet (error '+onCircle.toExponential(2)+')');

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
process.exit(bad.length?1:0);
