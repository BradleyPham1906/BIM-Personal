/* bim_phase92_grow_end_prototype.js

   EXTEND and LENGTHEN on a polyline whose end segment may be an arc. They are the same operation
   twice - grow the end - and differ only in what decides how far:

     LENGTHEN  by a length the user gives (delta / total / percent)
     EXTEND    to the first place the end meets a boundary

   ON AN ARC, GROWING MEANS CHANGING THE SWEEP. The centre and the radius stay exactly where they
   are; the endpoint travels along its own circle. Moving the endpoint any other way - along the
   chord, along the tangent - changes the radius, which is not lengthening an arc, it is
   replacing it with a different one.

   The two ends are not symmetric: growing the END advances past the last vertex in the sweep
   direction, growing the START retreats before the first vertex, against it. Both recompute the
   whole segment's bulge afterwards.

   Conventions from V88: bulge = tan(sweep/4), positive = counter-clockwise. */

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
function bimCircleLineIntersect(C,r,P,dir){
  var fx=P[0]-C[0],fz=P[1]-C[1];
  var a=dir[0]*dir[0]+dir[1]*dir[1];
  if(a<1e-18)return [];
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
function bimArcParamAt(arc,P){
  var rel=Math.atan2(P[1]-arc.center[1],P[0]-arc.center[0])-arc.a1;
  if(arc.sweep>=0){while(rel<-1e-9)rel+=Math.PI*2;while(rel>=Math.PI*2)rel-=Math.PI*2;}
  else{while(rel>1e-9)rel-=Math.PI*2;while(rel<=-Math.PI*2)rel+=Math.PI*2;}
  var t=rel/arc.sweep;
  if(t<-1e-9||t>1+1e-9)return null;
  return Math.max(0,Math.min(1,t));
}
function bimSegRangeOk(A,B,bulge,P){
  var arc=bimBulgeArc(A,B,bulge);
  if(arc)return bimArcParamAt(arc,P)!==null;
  var dx=B[0]-A[0],dz=B[1]-A[1],L2=dx*dx+dz*dz;
  if(L2<1e-18)return false;
  var t=((P[0]-A[0])*dx+(P[1]-A[1])*dz)/L2;
  return t>=-1e-9&&t<=1+1e-9;
}
function bimBulgedLength(pts,bulges,closed){
  if(!pts||pts.length<2)return 0;
  var n=pts.length,segs=closed?n:n-1,L=0,i;
  for(i=0;i<segs;i++){
    var a=pts[i],b=pts[(i+1)%n];
    var arc=bimBulgeArc(a,b,bimBulgeAt(bulges,i));
    if(arc)L+=Math.abs(arc.sweep)*arc.radius;
    else L+=Math.sqrt(Math.pow(b[0]-a[0],2)+Math.pow(b[1]-a[1],2));
  }
  return L;
}
function bimNearestEndIndex(pts,p){
  var n=pts.length;
  var d0=Math.pow(pts[0][0]-p[0],2)+Math.pow(pts[0][1]-p[1],2);
  var d1=Math.pow(pts[n-1][0]-p[0],2)+Math.pow(pts[n-1][1]-p[1],2);
  return d0<=d1?0:n-1;
}

/* ---------------------------------------------------------------- the shared operation */
/* The segment that touches the chosen end, and which way "growing" goes along it. */
function bimEndSegment(pts,bulges,endIdx){
  var n=pts.length;
  if(endIdx!==0&&endIdx!==n-1)return null;
  var segIdx=endIdx===0?0:n-2;
  if(segIdx<0)return null;
  return {segIdx:segIdx,atStart:endIdx===0,
          A:pts[segIdx],B:pts[segIdx+1],bulge:bimBulgeAt(bulges,segIdx),
          arc:bimBulgeArc(pts[segIdx],pts[segIdx+1],bimBulgeAt(bulges,segIdx))};
}
/* Grow (delta>0) or shrink (delta<0) the chosen end by an ARC LENGTH along its own segment.
   Returns the new pts/bulges, or an {error} naming what it refuses. */
function bimGrowEnd(pts,bulges,endIdx,delta){
  var n=pts.length;
  var seg=bimEndSegment(pts,bulges,endIdx);
  if(!seg)return {error:'That is not a free end'};
  var out=pts.map(function(p){return [p[0],p[1]];});
  var ob=[];
  var i;for(i=0;i<Math.max(0,n-1);i++)ob.push(bimBulgeAt(bulges,i));
  if(!seg.arc){
    /* straight: the endpoint slides along the segment's own direction */
    var far=seg.atStart?seg.B:seg.A;
    var near=seg.atStart?seg.A:seg.B;
    var dx=near[0]-far[0],dz=near[1]-far[1];
    var L=Math.sqrt(dx*dx+dz*dz);
    if(L<1e-9)return {error:'The end segment has zero length'};
    if(delta<0&&(-delta)>=L-1e-9)
      return {error:'That would shorten the end segment past its other end - use Break or Trim'};
    out[endIdx]=[near[0]+dx/L*delta,near[1]+dz/L*delta];
    return {pts:out,bulges:ob};
  }
  /* arc: the SWEEP changes, the centre and radius do not */
  var arc=seg.arc;
  var dTheta=delta/arc.radius;
  var sign=arc.sweep>=0?1:-1;
  var newSweep=arc.sweep+sign*dTheta;
  if(Math.abs(newSweep)<=1e-9)
    return {error:'That would shrink the arc away entirely'};
  if(sign*newSweep<0)
    return {error:'That would shorten the arc past its other end - use Break or Trim'};
  if(Math.abs(newSweep)>=Math.PI*2-1e-9)
    return {error:'That would take the arc past a full circle'};
  var newEndAngle,newStartAngle;
  if(seg.atStart){
    /* growing the START retreats BEFORE the first vertex, against the sweep */
    newStartAngle=arc.a1-sign*dTheta;
    out[endIdx]=[arc.center[0]+Math.cos(newStartAngle)*arc.radius,
                 arc.center[1]+Math.sin(newStartAngle)*arc.radius];
  }else{
    newEndAngle=arc.a2+sign*dTheta;
    out[endIdx]=[arc.center[0]+Math.cos(newEndAngle)*arc.radius,
                 arc.center[1]+Math.sin(newEndAngle)*arc.radius];
  }
  ob[seg.segIdx]=Math.tan(newSweep/4);
  return {pts:out,bulges:ob,sweep:newSweep};
}
function bimLengthenBulged(pts,bulges,closed,mode,value,clickPt){
  if(closed)return {error:'Lengthen needs an open wall'};
  if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
  if(!isFinite(value))return {error:'Lengthen value must be a number'};
  var L=bimBulgedLength(pts,bulges,false);
  var target;
  if(mode==='total')target=value;
  else if(mode==='percent')target=L*value/100;
  else target=L+value;
  if(!isFinite(target)||target<=1e-6)return {error:'That would leave the wall with no length'};
  var endIdx=bimNearestEndIndex(pts,clickPt);
  var r=bimGrowEnd(pts,bulges,endIdx,target-L);
  if(r.error)return r;
  return {pts:r.pts,bulges:r.bulges,length:target,delta:target-L,endIdx:endIdx};
}
/* EXTEND: how far the end must grow to reach the boundary. On an arc that is an ANGLE swept
   forward from the end, not a distance along a ray. */
function bimExtendBulged(pts,bulges,closed,bPts,bBulges,bClosed,clickPt){
  if(closed)return {error:'Extend needs an open wall (a closed loop has no free end)'};
  if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
  if(!bPts||bPts.length<2)return {error:'Boundary wall has no usable centerline'};
  var endIdx=bimNearestEndIndex(pts,clickPt);
  var seg=bimEndSegment(pts,bulges,endIdx);
  if(!seg)return {error:'That is not a free end'};
  var bn=bPts.length,bSegs=bClosed?bn:bn-1,i,best=null;
  if(!seg.arc){
    var near=pts[endIdx],far=seg.atStart?seg.B:seg.A;
    var dx=near[0]-far[0],dz=near[1]-far[1];
    var L=Math.sqrt(dx*dx+dz*dz);
    if(L<1e-9)return {error:'The end segment has zero length'};
    var D=[dx/L,dz/L];
    for(i=0;i<bSegs;i++){
      var bA=bPts[i],bB=bPts[(i+1)%bn],bb=bimBulgeAt(bBulges,i);
      var barc=bimBulgeArc(bA,bB,bb);
      var hits=barc?bimCircleLineIntersect(barc.center,barc.radius,near,D)
                   :(function(){
                       var d2x=bB[0]-bA[0],d2z=bB[1]-bA[1];
                       var den=D[0]*d2z-D[1]*d2x;
                       if(Math.abs(den)<1e-12)return [];
                       var ex=bA[0]-near[0],ez=bA[1]-near[1];
                       var t=(ex*d2z-ez*d2x)/den;
                       return [[near[0]+D[0]*t,near[1]+D[1]*t]];
                     })();
      var k;
      for(k=0;k<hits.length;k++){
        var t2=(hits[k][0]-near[0])*D[0]+(hits[k][1]-near[1])*D[1];
        if(t2<1e-9)continue;
        if(!bimSegRangeOk(bA,bB,bb,hits[k]))continue;
        if(!best||t2<best.d)best={d:t2,pt:hits[k]};
      }
    }
    if(!best)return {error:'That end does not reach the boundary when extended'};
    var outS=pts.map(function(p){return [p[0],p[1]];});
    var obS=[];for(i=0;i<pts.length-1;i++)obS.push(bimBulgeAt(bulges,i));
    outS[endIdx]=[best.pt[0],best.pt[1]];
    return {pts:outS,bulges:obS,atPt:best.pt,added:best.d};
  }
  /* arc end: candidates are where the boundary meets this arc's CIRCLE, ranked by the angle
     swept forward from the end - the smallest positive turn wins. */
  var arc=seg.arc;
  var sign=arc.sweep>=0?1:-1;
  var fromAngle=seg.atStart?arc.a1:arc.a2;
  var growSign=seg.atStart?-sign:sign;
  for(i=0;i<bSegs;i++){
    var cA=bPts[i],cB=bPts[(i+1)%bn],cb=bimBulgeAt(bBulges,i);
    var carc=bimBulgeArc(cA,cB,cb);
    var chits=carc?bimCircleCircleIntersect(arc.center,arc.radius,carc.center,carc.radius)
                  :bimCircleLineIntersect(arc.center,arc.radius,cA,[cB[0]-cA[0],cB[1]-cA[1]]);
    var j;
    for(j=0;j<chits.length;j++){
      if(!bimSegRangeOk(cA,cB,cb,chits[j]))continue;
      var ang=Math.atan2(chits[j][1]-arc.center[1],chits[j][0]-arc.center[0]);
      var turn=(ang-fromAngle)*growSign;
      while(turn<=1e-9)turn+=Math.PI*2;
      while(turn>Math.PI*2)turn-=Math.PI*2;
      /* growing all the way round to the arc's own other end is not an extension */
      if(Math.abs(arc.sweep)+turn>=Math.PI*2-1e-9)continue;
      if(!best||turn<best.turn)best={turn:turn,pt:chits[j]};
    }
  }
  if(!best)return {error:'That end does not reach the boundary when extended'};
  var grown=bimGrowEnd(pts,bulges,endIdx,best.turn*arc.radius);
  if(grown.error)return grown;
  return {pts:grown.pts,bulges:grown.bulges,atPt:best.pt,added:best.turn*arc.radius};
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}

var Q=Math.tan(Math.PI/2/4);            /* quarter-circle bulge */
console.log('-- growing an arc end changes the SWEEP, not the radius');
/* CCW quarter circle radius 2 about the origin: (2,0) -> (0,2). */
var g=bimGrowEnd([[2,0],[0,2]],[Q,0],1,Math.PI);   /* add a quarter's worth of arc: pi/2*2 = pi */
ck(!g.error,'the END grows ('+(g.error||'ok')+')');
var ga=bimBulgeArc(g.pts[0],g.pts[1],g.bulges[0]);
ck(near(ga.radius,2,1e-9)&&near(ga.center[0],0,1e-9)&&near(ga.center[1],0,1e-9),
   'same centre and radius -> c='+ga.center+' r='+ga.radius);
ck(near(Math.abs(ga.sweep),Math.PI,1e-9),'and the sweep doubled to 180 degrees -> '+(ga.sweep*180/Math.PI).toFixed(4));
ck(near(g.pts[1][0],-2,1e-9)&&near(g.pts[1][1],0,1e-9),'the end landed at (-2,0) -> '+g.pts[1]);
ck(near(bimBulgedLength(g.pts,g.bulges,false),2*Math.PI,1e-9),
   'measuring 2pi, exactly pi more than it did -> '+bimBulgedLength(g.pts,g.bulges,false).toFixed(6));

var gs=bimGrowEnd([[2,0],[0,2]],[Q,0],0,Math.PI);
ck(!gs.error,'the START grows too ('+(gs.error||'ok')+')');
var gsa=bimBulgeArc(gs.pts[0],gs.pts[1],gs.bulges[0]);
ck(near(gsa.radius,2,1e-9)&&near(gsa.center[0],0,1e-9)&&near(gsa.center[1],0,1e-9),
   'on the same circle -> c='+gsa.center+' r='+gsa.radius);
ck(near(gs.pts[0][0],0,1e-9)&&near(gs.pts[0][1],-2,1e-9),
   'retreating the other way, to (0,-2) -> '+gs.pts[0]);
ck(near(gs.pts[1][0],0,1e-9)&&near(gs.pts[1][1],2,1e-9),'and the far end did not move -> '+gs.pts[1]);

var sh=bimGrowEnd([[2,0],[0,2]],[Q,0],1,-Math.PI/2);
var sha=bimBulgeArc(sh.pts[0],sh.pts[1],sh.bulges[0]);
ck(!sh.error&&near(sha.radius,2,1e-9)&&near(Math.abs(sha.sweep),Math.PI/4,1e-9),
   'a negative delta shrinks the sweep to 45 degrees, radius unchanged -> '+(sha.sweep*180/Math.PI).toFixed(4));

ck(!!bimGrowEnd([[2,0],[0,2]],[Q,0],1,-Math.PI).error,
   'shrinking past the other end is refused -> '+bimGrowEnd([[2,0],[0,2]],[Q,0],1,-Math.PI).error);
ck(!!bimGrowEnd([[2,0],[0,2]],[Q,0],1,100).error,
   'and growing past a full circle is refused -> '+bimGrowEnd([[2,0],[0,2]],[Q,0],1,100).error);

console.log('\n-- a straight end still slides along itself');
var st=bimGrowEnd([[0,0],[10,0]],null,1,2.5);
ck(near(st.pts[1][0],12.5)&&near(st.pts[0][0],0),'the end moves to x=12.5 -> '+JSON.stringify(st.pts));
var st0=bimGrowEnd([[0,0],[10,0]],null,0,2.5);
ck(near(st0.pts[0][0],-2.5),'and the start to x=-2.5 -> '+JSON.stringify(st0.pts));
ck(!!bimGrowEnd([[0,0],[5,0],[10,0]],null,1,-7).error,'shortening past the previous vertex is refused');

console.log('\n-- LENGTHEN on a curve');
var lt=bimLengthenBulged([[2,0],[0,2]],[Q,0],false,'total',2*Math.PI,[0.1,2.1]);
ck(!lt.error&&near(bimBulgedLength(lt.pts,lt.bulges,false),2*Math.PI,1e-9),
   'total 2pi on a quarter circle gives exactly 2pi -> '+bimBulgedLength(lt.pts,lt.bulges,false).toFixed(6));
var lta=bimBulgeArc(lt.pts[0],lt.pts[1],lt.bulges[0]);
ck(near(lta.radius,2,1e-9),'still radius 2 - lengthening an arc does not resize it -> '+lta.radius);
var lp=bimLengthenBulged([[2,0],[0,2]],[Q,0],false,'percent',200,[0.1,2.1]);
ck(!lp.error&&near(bimBulgedLength(lp.pts,lp.bulges,false),Math.PI*2,1e-9),
   'percent 200 doubles pi to 2pi -> '+bimBulgedLength(lp.pts,lp.bulges,false).toFixed(6));
var ld=bimLengthenBulged([[2,0],[0,2]],[Q,0],false,'delta',-Math.PI/2,[0.1,2.1]);
ck(!ld.error&&near(bimBulgedLength(ld.pts,ld.bulges,false),Math.PI/2,1e-9),
   'delta -pi/2 shortens pi to pi/2 -> '+bimBulgedLength(ld.pts,ld.bulges,false).toFixed(6));
var lstraight=bimLengthenBulged([[0,0],[10,0]],null,false,'delta',2.5,[9.9,0]);
ck(near(lstraight.pts[1][0],12.5),'and a straight wall behaves exactly as it did -> '+lstraight.pts[1]);

console.log('\n-- EXTEND on a curve');
/* Quarter circle (2,0)->(0,2) CCW about the origin, extended forward to the x-axis at (-2,0). */
var ex=bimExtendBulged([[2,0],[0,2]],[Q,0],false,[[-5,0],[5,0]],null,false,[0.1,2.1]);
ck(!ex.error,'extend runs on an arc end ('+(ex.error||'ok')+')');
ck(ex.atPt&&near(ex.atPt[0],-2,1e-9)&&near(ex.atPt[1],0,1e-9),
   'reaching the boundary at (-2,0), the FIRST crossing going forward -> '+ex.atPt);
var exa=bimBulgeArc(ex.pts[0],ex.pts[1],ex.bulges[0]);
ck(near(exa.radius,2,1e-9)&&near(Math.abs(exa.sweep),Math.PI,1e-9),
   'making a semicircle of the same radius -> r='+exa.radius+' sweep='+(exa.sweep*180/Math.PI).toFixed(2));
ck(near(ex.added,Math.PI,1e-9),'and reporting pi of arc added -> '+ex.added.toFixed(6));

var exMiss=bimExtendBulged([[2,0],[0,2]],[Q,0],false,[[6,-5],[6,5]],null,false,[0.1,2.1]);
ck(!!exMiss.error,'a boundary the circle never reaches is refused -> '+exMiss.error);
var exStraight=bimExtendBulged([[0,0],[10,0]],null,false,[[15,-5],[15,5]],null,false,[9.5,0]);
ck(!exStraight.error&&near(exStraight.pts[1][0],15)&&near(exStraight.added,5),
   'and a straight wall extends exactly as it did -> '+JSON.stringify(exStraight.pts));
var exBack=bimExtendBulged([[0,0],[10,0]],null,false,[[15,-5],[15,5]],null,false,[0.5,0]);
ck(!!exBack.error,'picking the end facing away from the boundary is still refused');

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
process.exit(bad.length?1:0);
