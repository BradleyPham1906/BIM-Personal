"""patch_phase91.py -- Phase 91 part 1: the split machinery that Trim and Break share.

Ported from Phase/bim_phase91_trim_break_prototype.js (35/35). The one difference from the
prototype: the build's bimCircleLineIntersect (V90) already returns points, so the {t,pt}
unwrapping the prototype needed is not repeated here.

The parameter along an ARC is the fraction of its SWEEP, not of its chord. Using the chord would
make every "which side did the user click" decision subtly wrong near the ends of a curve, and
would be invisible on anything close to straight.
"""
import hashlib, pathlib, sys

BASE = '466875abf4a772a78ad09b69ce4be3a22340c6b46b4a109ede21584473423bc6'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

ANCHOR = "  /* ================= __acad3dV90: drawing curves, and offsetting them =================="
assert src.count(ANCHOR) == 1, 'anchor count %d' % src.count(ANCHOR)

BLOCK = r'''  /* ================= __acad3dV91: finding a place on a curve, and cutting there ========

     TRIM and BREAK are the same problem underneath - find a location along a polyline that may
     contain arcs, then split there - so they share every piece below rather than growing two
     sets that drift.

     THE PARAMETER ALONG AN ARC IS THE FRACTION OF ITS SWEEP, not of its chord. The midpoint of
     a semicircle from (0,0) to (0,2) is (1,1); the midpoint of its chord is (0,1). Every "which
     side did the user click" decision rests on this, and taking the chord would be wrong in a
     way that is invisible on anything close to straight and badly wrong on a tight curve.
     ---------------------------------------------------------------------------------------- */
  function bimArcParamAt(arc,P){
    var rel=Math.atan2(P[1]-arc.center[1],P[0]-arc.center[0])-arc.a1;
    if(arc.sweep>=0){while(rel<-1e-9)rel+=Math.PI*2;while(rel>=Math.PI*2)rel-=Math.PI*2;}
    else{while(rel>1e-9)rel-=Math.PI*2;while(rel<=-Math.PI*2)rel+=Math.PI*2;}
    var t=rel/arc.sweep;
    if(t<-1e-9||t>1+1e-9)return null;      /* on the circle, but not on the swept part */
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
      return {dist:Math.sqrt((p[0]-q[0])*(p[0]-q[0])+(p[1]-q[1])*(p[1]-q[1])),t:t,pt:q};
    }
    /* The nearest point on a circle lies along the radius. If that falls outside the swept
       part, the nearest point on the ARC is whichever end is closer. */
    var vx=p[0]-arc.center[0],vz=p[1]-arc.center[1];
    var L=Math.sqrt(vx*vx+vz*vz);
    if(L>1e-12){
      var onCircle=[arc.center[0]+vx/L*arc.radius,arc.center[1]+vz/L*arc.radius];
      var t2=bimArcParamAt(arc,onCircle);
      if(t2!==null)return {dist:Math.abs(L-arc.radius),t:t2,pt:onCircle};
    }
    var dA=Math.sqrt((p[0]-A[0])*(p[0]-A[0])+(p[1]-A[1])*(p[1]-A[1]));
    var dB=Math.sqrt((p[0]-B[0])*(p[0]-B[0])+(p[1]-B[1])*(p[1]-B[1]));
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
  function bimSegRangeOk(A,B,bulge,P){
    var arc=bimBulgeArc(A,B,bulge);
    if(arc)return bimArcParamAt(arc,P)!==null;
    var dx=B[0]-A[0],dz=B[1]-A[1],L2=dx*dx+dz*dz;
    if(L2<1e-18)return false;
    var t=((P[0]-A[0])*dx+(P[1]-A[1])*dz)/L2;
    return t>=-1e-9&&t<=1+1e-9;
  }
  /* All four line/arc combinations, each filtered to the part actually swept - two arcs whose
     CIRCLES cross but whose swept parts do not must report nothing. */
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
      hits=bimCircleLineIntersect(arc.center,arc.radius,LA,[LB[0]-LA[0],LB[1]-LA[1]]);
    }
    var out=[];
    for(i=0;i<hits.length;i++){
      if(bimSegRangeOk(A1,B1,b1,hits[i])&&bimSegRangeOk(A2,B2,b2,hits[i]))out.push(hits[i]);
    }
    return out;
  }
  /* Splitting an ARC recomputes BOTH halves' bulges from the split point, keeping the original
     sweep direction. The two halves of a 180-degree arc are not two 180-degree arcs. */
  function bimSplitBulgedAt(pts,bulges,closed,loc){
    if(closed)return {error:'Split needs an open polyline'};
    if(!pts||pts.length<2)return {error:'Needs at least two points'};
    var n=pts.length,i;
    if(loc.seg<0||loc.seg>n-2)return {error:'Split location is outside the polyline'};
    var A=pts[loc.seg],B=pts[loc.seg+1],bl=bimBulgeAt(bulges,loc.seg);
    var arc=bimBulgeArc(A,B,bl);
    var Pt=arc?bimArcPointAt(arc,loc.t)
              :[A[0]+(B[0]-A[0])*loc.t,A[1]+(B[1]-A[1])*loc.t];
    var leftPts=[],leftB=[],rightPts=[],rightB=[];
    for(i=0;i<=loc.seg;i++)leftPts.push([pts[i][0],pts[i][1]]);
    for(i=0;i<loc.seg;i++)leftB.push(bimBulgeAt(bulges,i));
    leftPts.push([Pt[0],Pt[1]]);
    leftB.push(arc?bimArcBulgeBetween(arc.center,A,Pt,arc.sweep):0);
    rightPts.push([Pt[0],Pt[1]]);
    rightB.push(arc?bimArcBulgeBetween(arc.center,Pt,B,arc.sweep):0);
    for(i=loc.seg+1;i<n;i++){
      rightPts.push([pts[i][0],pts[i][1]]);
      if(i<n-1)rightB.push(bimBulgeAt(bulges,i));
    }
    return {a:{pts:leftPts,bulges:leftB},b:{pts:rightPts,bulges:rightB},at:Pt};
  }
  function bimTrimBulged(pts,bulges,closed,cPts,cBulges,cClosed,clickPt){
    if(closed)return {error:'Trim needs an open wall (a closed loop has no free end to remove)'};
    if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
    if(!cPts||cPts.length<2)return {error:'Cutting wall has no usable centerline'};
    var n=pts.length,cn=cPts.length,cSegs=cClosed?cn:cn-1,i,j,k,best=null;
    for(i=0;i<n-1;i++){
      for(j=0;j<cSegs;j++){
        var hits=bimIntersectBulgedSegs(pts[i],pts[i+1],bimBulgeAt(bulges,i),
                                        cPts[j],cPts[(j+1)%cn],bimBulgeAt(cBulges,j));
        for(k=0;k<hits.length;k++){
          var arc=bimBulgeArc(pts[i],pts[i+1],bimBulgeAt(bulges,i));
          var t;
          if(arc){
            t=bimArcParamAt(arc,hits[k]);
            if(t===null)continue;
          }else{
            var dx=pts[i+1][0]-pts[i][0],dz=pts[i+1][1]-pts[i][1];
            var L2=dx*dx+dz*dz;
            t=L2?((hits[k][0]-pts[i][0])*dx+(hits[k][1]-pts[i][1])*dz)/L2:0;
          }
          if(!best)best={seg:i,t:t,pt:hits[k]};
        }
      }
    }
    if(!best)return {error:'Those two walls do not cross — nothing to trim'};
    var click=bimProjectOntoBulged(pts,bulges,false,clickPt);
    if(!click)return {error:'Could not place that click on the wall'};
    var split=bimSplitBulgedAt(pts,bulges,false,{seg:best.seg,t:best.t});
    if(split.error)return {error:split.error};
    var keep=((click.seg+click.t)>(best.seg+best.t))?split.a:split.b;
    if(keep.pts.length<2)return {error:'Trim would remove the whole wall'};
    return {pts:keep.pts,bulges:keep.bulges,cutAt:best.pt};
  }
  /* Two splits. The second location is re-PROJECTED onto the piece that survived the first,
     rather than having its index arithmetic adjusted across the split - the projection already
     knows how to find a point on a polyline, and index arithmetic across a cut is where
     off-by-ones live. */
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
    if(s1.a.pts.length<2)
      return {error:'That break point is at the start of the wall — there would be nothing on that side'};
    if(s2.b.pts.length<2)
      return {error:'That break point is at the end of the wall — there would be nothing on that side'};
    return {a:s1.a,b:s2.b,cutA:lo.pt,cutB:hi.pt};
  }
'''

out = src.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
