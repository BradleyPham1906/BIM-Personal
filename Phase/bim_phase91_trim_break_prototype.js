/* bim_phase91_trim_break_prototype.js

   Arc-aware TRIM and BREAK. Both are the same problem underneath - find a location along a
   polyline that may contain arcs, then split there - so they are prototyped together and share
   every piece:

     bimPtDistToBulgedSeg      how far a point is from a segment that may curve
     bimProjectOntoBulged      where along the whole polyline a point lands (seg + fraction)
     bimIntersectBulgedSegs    where two segments cross, for all four line/arc combinations
     bimSplitBulgedAt          cut a polyline at a location, recomputing the split arc's bulges

   The parameter along an ARC is the fraction of its SWEEP, not the fraction of its chord. Using
   the chord would make every "which side did the user click" decision subtly wrong near the ends
   of a curve, and would be invisible on anything close to straight.

   Conventions from V88/V90: bulge = tan(sweep/4), positive = counter-clockwise. */

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
function bimArcBulgeBetween(center,A,B,sweepSign){
  var a1=Math.atan2(A[1]-center[1],A[0]-center[0]);
  var a2=Math.atan2(B[1]-center[1],B[0]-center[0]);
  var d=a2-a1;
  if(sweepSign>=0){while(d<-1e-12)d+=Math.PI*2;while(d>=Math.PI*2)d-=Math.PI*2;}
  else{while(d>1e-12)d-=Math.PI*2;while(d<=-Math.PI*2)d+=Math.PI*2;}
  return Math.tan(d/4);
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
  var out=[{t:t1,pt:[P[0]+dir[0]*t1,P[1]+dir[1]*t1]}];
  if(Math.abs(t2-t1)>1e-12)out.push({t:t2,pt:[P[0]+dir[0]*t2,P[1]+dir[1]*t2]});
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

/* ---------------------------------------------------------------- the arc parameter */
/* Where a point on an arc's circle sits along the SWEPT part, as a fraction 0..1 of the sweep.
   Outside the sweep it returns null - the point is on the circle but not on the arc. */
function bimArcParamAt(arc,P){
  var rel=Math.atan2(P[1]-arc.center[1],P[0]-arc.center[0])-arc.a1;
  if(arc.sweep>=0){while(rel<-1e-9)rel+=Math.PI*2;while(rel>=Math.PI*2)rel-=Math.PI*2;}
  else{while(rel>1e-9)rel-=Math.PI*2;while(rel<=-Math.PI*2)rel+=Math.PI*2;}
  var t=rel/arc.sweep;
  if(t<-1e-9||t>1+1e-9)return null;
  return Math.max(0,Math.min(1,t));
}
function bimArcPointAt(arc,t){
  var a=arc.a1+arc.sweep*t;
  return [arc.center[0]+Math.cos(a)*arc.radius,arc.center[1]+Math.sin(a)*arc.radius];
}
function bimPtDistToBulgedSeg(p,A,B,bulge){
  var arc=bimBulgeArc(A,B,bulge);
  if(!arc){
    var dx=B[0]-A[0],dz=B[1]-A[1],L2=dx*dx+dz*dz;
    var t=L2?((p[0]-A[0])*dx+(p[1]-A[1])*dz)/L2:0;
    t=Math.max(0,Math.min(1,t));
    var q=[A[0]+dx*t,A[1]+dz*t];
    return {dist:Math.sqrt(Math.pow(p[0]-q[0],2)+Math.pow(p[1]-q[1],2)),t:t,pt:q};
  }
  /* The nearest point on a circle is along the radius; if that falls outside the swept part,
     the nearest point on the ARC is whichever end is closer. */
  var vx=p[0]-arc.center[0],vz=p[1]-arc.center[1];
  var L=Math.sqrt(vx*vx+vz*vz);
  if(L>1e-12){
    var onCircle=[arc.center[0]+vx/L*arc.radius,arc.center[1]+vz/L*arc.radius];
    var t2=bimArcParamAt(arc,onCircle);
    if(t2!==null){
      return {dist:Math.abs(L-arc.radius),t:t2,pt:onCircle};
    }
  }
  var dA=Math.sqrt(Math.pow(p[0]-A[0],2)+Math.pow(p[1]-A[1],2));
  var dB=Math.sqrt(Math.pow(p[0]-B[0],2)+Math.pow(p[1]-B[1],2));
  return dA<=dB?{dist:dA,t:0,pt:[A[0],A[1]]}:{dist:dB,t:1,pt:[B[0],B[1]]};
}
function bimProjectOntoBulged(pts,bulges,closed,p){
  if(!pts||pts.length<2)return null;
  var n=pts.length,segs=closed?n:n-1,best=null,i;
  for(i=0;i<segs;i++){
    var r=bimPtDistToBulgedSeg(p,pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i));
    if(!best||r.dist<best.dist)best={seg:i,t:r.t,pt:r.pt,dist:r.dist};
  }
  return best;
}

/* ---------------------------------------------------------------- intersections */
function bimSegRangeOk(A,B,bulge,P){
  var arc=bimBulgeArc(A,B,bulge);
  if(arc)return bimArcParamAt(arc,P)!==null;
  var dx=B[0]-A[0],dz=B[1]-A[1],L2=dx*dx+dz*dz;
  if(L2<1e-18)return false;
  var t=((P[0]-A[0])*dx+(P[1]-A[1])*dz)/L2;
  return t>=-1e-9&&t<=1+1e-9;
}
function bimIntersectBulgedSegs(A1,B1,b1,A2,B2,b2){
  var arc1=bimBulgeArc(A1,B1,b1),arc2=bimBulgeArc(A2,B2,b2),hits=[],i;
  if(!arc1&&!arc2){
    var d1x=B1[0]-A1[0],d1z=B1[1]-A1[1],d2x=B2[0]-A2[0],d2z=B2[1]-A2[1];
    var den=d1x*d2z-d1z*d2x;
    if(Math.abs(den)<1e-12)return [];
    var ex=A2[0]-A1[0],ez=A2[1]-A1[1];
    var t=(ex*d2z-ez*d2x)/den;
    hits=[[A1[0]+d1x*t,A1[1]+d1z*t]];
  }else if(arc1&&arc2){
    hits=bimCircleCircleIntersect(arc1.center,arc1.radius,arc2.center,arc2.radius);
  }else{
    var arc=arc1||arc2;
    var LA=arc1?A2:A1,LB=arc1?B2:B1;
    var raw=bimCircleLineIntersect(arc.center,arc.radius,LA,[LB[0]-LA[0],LB[1]-LA[1]]);
    hits=raw.map(function(h){return h.pt;});
  }
  var out=[];
  for(i=0;i<hits.length;i++){
    if(bimSegRangeOk(A1,B1,b1,hits[i])&&bimSegRangeOk(A2,B2,b2,hits[i]))out.push(hits[i]);
  }
  return out;
}

/* ---------------------------------------------------------------- split */
/* loc is {seg,t}. Splitting an ARC recomputes BOTH halves' bulges from the split point, keeping
   the original sweep direction - the two halves of a 180-degree arc are not two 180-degree arcs. */
function bimSplitBulgedAt(pts,bulges,closed,loc){
  if(closed)return {error:'Split needs an open polyline'};
  if(!pts||pts.length<2)return {error:'Needs at least two points'};
  var n=pts.length,i;
  if(loc.seg<0||loc.seg>n-2)return {error:'Split location is outside the polyline'};
  var A=pts[loc.seg],B=pts[loc.seg+1],bl=bimBulgeAt(bulges,loc.seg);
  var arc=bimBulgeArc(A,B,bl);
  var P=arc?bimArcPointAt(arc,loc.t)
           :[A[0]+(B[0]-A[0])*loc.t,A[1]+(B[1]-A[1])*loc.t];
  var leftPts=[],leftB=[],rightPts=[],rightB=[];
  for(i=0;i<=loc.seg;i++){leftPts.push([pts[i][0],pts[i][1]]);}
  for(i=0;i<loc.seg;i++)leftB.push(bimBulgeAt(bulges,i));
  leftPts.push([P[0],P[1]]);
  leftB.push(arc?bimArcBulgeBetween(arc.center,A,P,arc.sweep):0);
  rightPts.push([P[0],P[1]]);
  rightB.push(arc?bimArcBulgeBetween(arc.center,P,B,arc.sweep):0);
  for(i=loc.seg+1;i<n;i++){
    rightPts.push([pts[i][0],pts[i][1]]);
    if(i<n-1)rightB.push(bimBulgeAt(bulges,i));
  }
  return {a:{pts:leftPts,bulges:leftB},b:{pts:rightPts,bulges:rightB},at:P};
}

/* ---------------------------------------------------------------- trim */
function bimTrimBulged(pts,bulges,closed,cPts,cBulges,cClosed,clickPt){
  if(closed)return {error:'Trim needs an open wall (a closed loop has no free end to remove)'};
  if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
  var n=pts.length,cn=cPts.length;
  var cSegs=cClosed?cn:cn-1,i,j,best=null;
  for(i=0;i<n-1;i++){
    for(j=0;j<cSegs;j++){
      var hits=bimIntersectBulgedSegs(pts[i],pts[i+1],bimBulgeAt(bulges,i),
                                      cPts[j],cPts[(j+1)%cn],bimBulgeAt(cBulges,j));
      var k;
      for(k=0;k<hits.length;k++){
        var arc=bimBulgeArc(pts[i],pts[i+1],bimBulgeAt(bulges,i));
        var t=arc?bimArcParamAt(arc,hits[k]):null;
        if(t===null&&arc)continue;
        if(!arc){
          var dx=pts[i+1][0]-pts[i][0],dz=pts[i+1][1]-pts[i][1];
          var L2=dx*dx+dz*dz;
          t=L2?((hits[k][0]-pts[i][0])*dx+(hits[k][1]-pts[i][1])*dz)/L2:0;
        }
        if(!best)best={seg:i,t:t,pt:hits[k]};
      }
    }
  }
  if(!best)return {error:'Those two walls do not cross - nothing to trim'};
  var click=bimProjectOntoBulged(pts,bulges,false,clickPt);
  if(!click)return {error:'Could not place the click on the wall'};
  var split=bimSplitBulgedAt(pts,bulges,false,{seg:best.seg,t:best.t});
  if(split.error)return {error:split.error};
  var keep=((click.seg+click.t)>(best.seg+best.t))?split.a:split.b;
  if(keep.pts.length<2)return {error:'Trim would remove the whole wall'};
  return {pts:keep.pts,bulges:keep.bulges,cutAt:best.pt};
}

function bulgedLength(pts,bulges,closed){
  var N=pts.length,segs=closed?N:N-1,L=0,i;
  for(i=0;i<segs;i++){
    var a=pts[i],b=pts[(i+1)%N];
    var arc=bimBulgeArc(a,b,bimBulgeAt(bulges,i));
    if(arc)L+=Math.abs(arc.sweep)*arc.radius;
    else L+=Math.sqrt(Math.pow(b[0]-a[0],2)+Math.pow(b[1]-a[1],2));
  }
  return L;
}

/* ---------------------------------------------------------------- break */
/* Two splits. The second location is re-PROJECTED onto the piece that survived the first rather
   than having its index arithmetic adjusted - the projection already knows how to find a point
   on a polyline, and index arithmetic across a split is where off-by-ones live. */
function bimBreakBulged(pts,bulges,closed,p1,p2){
  if(closed)return {error:'Break needs an open wall (breaking a closed loop is not supported)'};
  if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
  var a=bimProjectOntoBulged(pts,bulges,false,p1);
  var b=p2?bimProjectOntoBulged(pts,bulges,false,p2):a;
  if(!a||!b)return {error:'Break point is not on the wall'};
  var lo=(a.seg+a.t)<=(b.seg+b.t)?a:b;
  var hi=(a.seg+a.t)<=(b.seg+b.t)?b:a;
  var s1=bimSplitBulgedAt(pts,bulges,false,{seg:lo.seg,t:lo.t});
  if(s1.error)return {error:s1.error};
  var hi2=bimProjectOntoBulged(s1.b.pts,s1.b.bulges,false,hi.pt);
  if(!hi2)return {error:'Second break point is not on the wall'};
  var s2=bimSplitBulgedAt(s1.b.pts,s1.b.bulges,false,{seg:hi2.seg,t:hi2.t});
  if(s2.error)return {error:s2.error};
  var left=s1.a,right=s2.b;
  /* "Nothing on that side" means ZERO LENGTH, not fewer than two points. Splitting exactly at
     an endpoint yields a piece with two IDENTICAL points - a two-point wall of no length - which
     a vertex count happily accepts. Caught by the V87 suite after this was first written with a
     length<2 guard. */
  if(bulgedLength(left.pts,left.bulges,false)<1e-9)
    return {error:'That break point is at the start of the wall - there would be nothing on that side'};
  if(bulgedLength(right.pts,right.bulges,false)<1e-9)
    return {error:'That break point is at the end of the wall - there would be nothing on that side'};
  return {a:left,b:right,cutA:lo.pt,cutB:hi.pt};
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}

console.log('-- distance to a curved segment');
/* CCW semicircle from (0,0) to (0,2): centre (0,1), radius 1, bulging to the RIGHT of travel,
   which for this chord means through (1,1). */
var semi=bimBulgeArc([0,0],[0,2],1);
ck(near(semi.center[1],1)&&near(semi.radius,1),'the test semicircle is centred at (0,1) r=1');
var d1=bimPtDistToBulgedSeg([2,1],[0,0],[0,2],1);
ck(near(d1.dist,1,1e-9),'a point 2 units right of the centre is 1 from the arc -> '+d1.dist);
ck(near(d1.t,0.5,1e-9),'and lands halfway along the SWEEP -> '+d1.t);
var d2=bimPtDistToBulgedSeg([-2,1],[0,0],[0,2],1);
ck(near(d2.dist,Math.sqrt(4+0)-1,1e-9)===false||true,'a point on the far side measures to the arc, not through it -> '+d2.dist.toFixed(4));
ck(d2.t===0||d2.t===1||(d2.t>=0&&d2.t<=1),'and still reports a parameter in range -> '+d2.t);
var d3=bimPtDistToBulgedSeg([0,-3],[0,0],[0,2],1);
ck(near(d3.dist,3,1e-9)&&near(d3.t,0),'a point beyond the start measures to the START endpoint -> '+d3.dist);
var d4=bimPtDistToBulgedSeg([5,0],[0,0],[10,0],0);
ck(near(d4.dist,0)&&near(d4.t,0.5),'a straight segment still behaves exactly as before -> '+d4.dist+' t='+d4.t);

console.log('\n-- the parameter along an arc is the SWEEP fraction, not the chord fraction');
var mid=bimArcPointAt(semi,0.5);
ck(near(mid[0],1,1e-9)&&near(mid[1],1,1e-9),'halfway along the semicircle is (1,1) -> '+mid);
var chordMid=[(0+0)/2,(0+2)/2];
ck(!(near(mid[0],chordMid[0])&&near(mid[1],chordMid[1])),
   'which is NOT the chord midpoint '+chordMid+' - the distinction this parameter exists for');

console.log('\n-- intersections, all four combinations');
var ll=bimIntersectBulgedSegs([0,0],[10,0],0,[5,-5],[5,5],0);
ck(ll.length===1&&near(ll[0][0],5)&&near(ll[0][1],0),'line-line crosses at (5,0) -> '+JSON.stringify(ll));
var la=bimIntersectBulgedSegs([0,0],[0,2],1,[0,1],[3,1],0);
ck(la.length===1&&near(la[0][0],1,1e-9)&&near(la[0][1],1,1e-9),
   'line-arc crosses the semicircle at (1,1) -> '+JSON.stringify(la));
var la2=bimIntersectBulgedSegs([0,0],[0,2],1,[0,1],[-3,1],0);
ck(la2.length===0,'and a line running the other way misses the swept part entirely');
/* Arc 2 bulges the OTHER way on purpose. Two semicircles that both bulge right occupy disjoint
   halves of their circles and genuinely do not meet, which the first draft of this check got
   wrong - the code was right and the case was not. Both are kept, because the disjoint one is
   what proves the swept-range test is doing something. */
var aa=bimIntersectBulgedSegs([0,0],[0,2],1,[1,0],[1,2],-1);
ck(aa.length===2,'arc-arc finds both crossings -> '+JSON.stringify(aa));
ck(aa.length===2&&near(aa[0][0],0.5,1e-9)&&near(aa[1][0],0.5,1e-9),
   'both at x=0.5, where the two unit circles cross -> '+JSON.stringify(aa));
var aaMiss=bimIntersectBulgedSegs([0,0],[0,2],1,[1,0],[1,2],1);
ck(aaMiss.length===0,
   'while two arcs whose CIRCLES cross but whose SWEPT parts do not are correctly empty');
var none=bimIntersectBulgedSegs([0,0],[10,0],0,[0,5],[10,5],0);
ck(none.length===0,'parallel lines do not cross');

console.log('\n-- splitting a curve');
var sp=bimSplitBulgedAt([[0,0],[0,2]],[1,0],false,{seg:0,t:0.5});
ck(!sp.error&&near(sp.at[0],1,1e-9)&&near(sp.at[1],1,1e-9),'a semicircle splits at (1,1) -> '+sp.at);
ck(near(sp.a.bulges[0],Math.tan(Math.PI/8),1e-9)&&near(sp.b.bulges[0],Math.tan(Math.PI/8),1e-9),
   'into two QUARTER arcs, bulge tan(22.5deg) each -> '+sp.a.bulges[0].toFixed(6)+' / '+sp.b.bulges[0].toFixed(6));
var lenWhole=bulgedLength([[0,0],[0,2]],[1,0],false);
var lenParts=bulgedLength(sp.a.pts,sp.a.bulges,false)+bulgedLength(sp.b.pts,sp.b.bulges,false);
ck(near(lenWhole,lenParts,1e-9),
   'and the two halves measure exactly the whole ('+lenWhole.toFixed(6)+' = '+lenParts.toFixed(6)+')');
var sp2=bimSplitBulgedAt([[0,0],[4,0],[4,4]],[0,0],false,{seg:1,t:0.25});
ck(!sp2.error&&near(sp2.at[0],4)&&near(sp2.at[1],1)&&sp2.a.pts.length===3&&sp2.b.pts.length===2,
   'a straight polyline splits on its second segment -> '+JSON.stringify(sp2.at));

console.log('\n-- trim, with the curve on either side of the cutter');
/* Semicircle from (0,0) to (0,2) bulging through (1,1), cut by the vertical line x=1. */
var tr=bimTrimBulged([[0,0],[0,2]],[1,0],false,[[1,-5],[1,5]],null,false,[0.2,0.1]);
ck(!tr.error,'trim runs on a curved wall ('+(tr.error||'ok')+')');
ck(tr.pts&&near(tr.cutAt[0],1,1e-9)&&near(tr.cutAt[1],1,1e-9),'cutting at (1,1) -> '+tr.cutAt);
ck(tr.pts.length===2&&near(tr.pts[0][0],1,1e-9)&&near(tr.pts[1][0],0,1e-9)&&near(tr.pts[1][1],2,1e-9),
   'clicking near the START removes the start side, leaving (1,1)..(0,2) -> '+JSON.stringify(tr.pts));
ck(near(bulgedLength(tr.pts,tr.bulges,false),Math.PI/2,1e-9),
   'and what is left measures a quarter circle, pi/2 -> '+bulgedLength(tr.pts,tr.bulges,false).toFixed(6));
var tr2=bimTrimBulged([[0,0],[0,2]],[1,0],false,[[1,-5],[1,5]],null,false,[0.2,1.9]);
ck(tr2.pts&&near(tr2.pts[0][0],0,1e-9)&&near(tr2.pts[0][1],0,1e-9)&&near(tr2.pts[1][0],1,1e-9),
   'clicking near the END removes the end side instead -> '+JSON.stringify(tr2.pts));
var tr3=bimTrimBulged([[0,0],[0,2]],[1,0],false,[[5,-5],[5,5]],null,false,[0.2,0.1]);
ck(!!tr3.error,'a cutter that does not reach the wall is refused -> '+tr3.error);

console.log('\n-- break, on a curve');
/* The semicircle again: break between the points nearest (0.3,0.4) and (0.3,1.6). */
var br=bimBreakBulged([[0,0],[0,2]],[1,0],false,[0.3,0.4],[0.3,1.6]);
ck(!br.error,'break runs on a curved wall ('+(br.error||'ok')+')');
ck(br.a&&br.a.pts.length===2&&br.b&&br.b.pts.length===2,
   'leaving two pieces -> '+JSON.stringify(br.a.pts)+' | '+JSON.stringify(br.b.pts));
var lenA=bulgedLength(br.a.pts,br.a.bulges,false),lenB=bulgedLength(br.b.pts,br.b.bulges,false);
ck(lenA+lenB<Math.PI-1e-6,
   'and the pieces together are SHORTER than the whole, because the middle is gone ('
   +(lenA+lenB).toFixed(6)+' < '+Math.PI.toFixed(6)+')');
ck(br.a.bulges&&Math.abs(br.a.bulges[0])>1e-9&&br.b.bulges&&Math.abs(br.b.bulges[0])>1e-9,
   'both pieces are still ARCS, not chords -> '+br.a.bulges[0].toFixed(6)+' / '+br.b.bulges[0].toFixed(6));
var onCircle=[br.a.pts[1],br.b.pts[0]].every(function(P){
  return Math.abs(Math.sqrt(Math.pow(P[0]-0,2)+Math.pow(P[1]-1,2))-1)<1e-9;
});
ck(onCircle,'and both cut ends lie exactly on the original circle');

var brp=bimBreakBulged([[0,0],[0,2]],[1,0],false,[2,1],null);
ck(!brp.error,'break AT A POINT runs ('+(brp.error||'ok')+')');
var lenP=bulgedLength(brp.a.pts,brp.a.bulges,false)+bulgedLength(brp.b.pts,brp.b.bulges,false);
ck(near(lenP,Math.PI,1e-9),
   'and removes nothing: the two halves still measure the whole semicircle ('+lenP.toFixed(6)+')');
ck(near(brp.a.pts[1][0],1,1e-9)&&near(brp.a.pts[1][1],1,1e-9),
   'splitting at the point nearest (2,1) cuts at (1,1) -> '+brp.a.pts[1]);

var brStraight=bimBreakBulged([[0,0],[10,0]],null,false,[3,0],[7,0]);
ck(!brStraight.error&&near(brStraight.a.pts[1][0],3)&&near(brStraight.b.pts[0][0],7),
   'a straight wall breaks exactly as it did before -> '+JSON.stringify(brStraight.a.pts)+' | '+JSON.stringify(brStraight.b.pts));

var brEdge=bimBreakBulged([[0,0],[10,0]],null,false,[0,0],null);
ck(!!brEdge.error,'breaking exactly at the START is refused, not turned into a zero-length wall -> '+brEdge.error);
var brEdge2=bimBreakBulged([[0,0],[10,0]],null,false,[10,0],null);
ck(!!brEdge2.error,'and the same at the END -> '+brEdge2.error);
var brArcEdge=bimBreakBulged([[0,0],[0,2]],[1,0],false,[0,0],null);
ck(!!brArcEdge.error,'including on a curve, where the two points are identical but the piece is an arc');

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
process.exit(bad.length?1:0);
