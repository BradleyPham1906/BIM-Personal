"""patch_phase92.py -- Phase 92 part 1: growing the end of a curve.

EXTEND and LENGTHEN are the same operation twice - grow the end - differing only in what decides
how far. Ported from Phase/bim_phase92_grow_end_prototype.js (27/27).

ON AN ARC, GROWING MEANS CHANGING THE SWEEP. The centre and radius stay exactly where they are
and the endpoint travels along its own circle. Moving it any other way - along the chord, along
the tangent - changes the radius, which is not lengthening an arc but replacing it with a
different one.
"""
import hashlib, pathlib, sys

BASE = 'c4046875164e355be4df3f66363d842116ac70a9ee59310ce4f902657e834a69'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

ANCHOR = "  /* ================= __acad3dV91: finding a place on a curve, and cutting there ========"
assert src.count(ANCHOR) == 1, 'anchor count %d' % src.count(ANCHOR)

BLOCK = r'''  /* ================= __acad3dV92: growing the end of a curve ===========================

     EXTEND and LENGTHEN are one operation twice. Both grow (or shrink) a free end; they differ
     only in what decides how far - a length the user gives, or the first place the end meets a
     boundary. So both go through bimGrowEnd.

     ON AN ARC, GROWING MEANS CHANGING THE SWEEP. The centre and the radius do not move; the
     endpoint travels along its own circle. Sliding the endpoint along the chord or the tangent
     instead would change the radius, which is not a longer arc, it is a different one.

     THE TWO ENDS ARE NOT SYMMETRIC. Growing the END advances past the last vertex in the sweep
     direction; growing the START retreats before the first vertex, against it. Getting that
     backwards moves the wrong end and looks, on a symmetric test case, like nothing at all.
     ---------------------------------------------------------------------------------------- */
  function bimEndSegment(pts,bulges,endIdx){
    var n=pts.length;
    if(endIdx!==0&&endIdx!==n-1)return null;
    var segIdx=endIdx===0?0:n-2;
    if(segIdx<0)return null;
    return {segIdx:segIdx,atStart:endIdx===0,
            A:pts[segIdx],B:pts[segIdx+1],bulge:bimBulgeAt(bulges,segIdx),
            arc:bimBulgeArc(pts[segIdx],pts[segIdx+1],bimBulgeAt(bulges,segIdx))};
  }
  function bimGrowEnd(pts,bulges,endIdx,delta){
    var n=pts.length;
    var seg=bimEndSegment(pts,bulges,endIdx);
    if(!seg)return {error:'That is not a free end'};
    var out=pts.map(function(p){return [p[0],p[1]];});
    var ob=[],i;
    for(i=0;i<Math.max(0,n-1);i++)ob.push(bimBulgeAt(bulges,i));
    if(!seg.arc){
      var far=seg.atStart?seg.B:seg.A;
      var nearP=seg.atStart?seg.A:seg.B;
      var dx=nearP[0]-far[0],dz=nearP[1]-far[1];
      var L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-9)return {error:'The end segment has zero length'};
      if(delta<0&&(-delta)>=L-1e-9)
        return {error:'Lengthen cannot shorten past the next vertex — use Break or Trim for that'};
      out[endIdx]=[nearP[0]+dx/L*delta,nearP[1]+dz/L*delta];
      return {pts:out,bulges:ob};
    }
    var arc=seg.arc;
    var dTheta=delta/arc.radius;
    var sign=arc.sweep>=0?1:-1;
    var newSweep=arc.sweep+sign*dTheta;
    if(Math.abs(newSweep)<=1e-9)return {error:'That would shrink the arc away entirely'};
    if(sign*newSweep<0)
      return {error:'That would shorten the arc past its other end — use Break or Trim for that'};
    if(Math.abs(newSweep)>=Math.PI*2-1e-9)
      return {error:'That would take the arc past a full circle'};
    var ang=seg.atStart?(arc.a1-sign*dTheta):(arc.a2+sign*dTheta);
    out[endIdx]=[arc.center[0]+Math.cos(ang)*arc.radius,arc.center[1]+Math.sin(ang)*arc.radius];
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
  /* EXTEND on an arc end ranks candidates by the ANGLE swept forward from the end, not by
     distance along a ray: the nearest crossing in space can be behind you on the circle. */
  function bimExtendBulged(pts,bulges,closed,bPts,bBulges,bClosed,clickPt){
    if(closed)return {error:'Extend needs an open wall (a closed loop has no free end)'};
    if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
    if(!bPts||bPts.length<2)return {error:'Boundary wall has no usable centerline'};
    var endIdx=bimNearestEndIndex(pts,clickPt);
    var seg=bimEndSegment(pts,bulges,endIdx);
    if(!seg)return {error:'That is not a free end'};
    var bn=bPts.length,bSegs=bClosed?bn:bn-1,best=null,i,k;
    if(!seg.arc){
      var nearP=pts[endIdx],far=seg.atStart?seg.B:seg.A;
      var dx=nearP[0]-far[0],dz=nearP[1]-far[1];
      var L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-9)return {error:'The end segment has zero length'};
      var D=[dx/L,dz/L];
      for(i=0;i<bSegs;i++){
        var bA=bPts[i],bB=bPts[(i+1)%bn],bb=bimBulgeAt(bBulges,i);
        var barc=bimBulgeArc(bA,bB,bb),hits;
        if(barc){
          hits=bimCircleLineIntersect(barc.center,barc.radius,nearP,D);
        }else{
          var d2x=bB[0]-bA[0],d2z=bB[1]-bA[1];
          var den=D[0]*d2z-D[1]*d2x;
          if(Math.abs(den)<1e-12)continue;
          var ex=bA[0]-nearP[0],ez=bA[1]-nearP[1];
          var tt=(ex*d2z-ez*d2x)/den;
          hits=[[nearP[0]+D[0]*tt,nearP[1]+D[1]*tt]];
        }
        for(k=0;k<hits.length;k++){
          var t2=(hits[k][0]-nearP[0])*D[0]+(hits[k][1]-nearP[1])*D[1];
          if(t2<1e-9)continue;                       /* forward only */
          if(!bimSegRangeOk(bA,bB,bb,hits[k]))continue;
          if(!best||t2<best.d)best={d:t2,pt:hits[k]};
        }
      }
      if(!best)return {error:'That end does not reach the boundary when extended'};
      var outS=pts.map(function(p){return [p[0],p[1]];});
      var obS=[];
      for(i=0;i<pts.length-1;i++)obS.push(bimBulgeAt(bulges,i));
      outS[endIdx]=[best.pt[0],best.pt[1]];
      return {pts:outS,bulges:obS,atPt:best.pt,added:best.d};
    }
    var arc=seg.arc;
    var sign=arc.sweep>=0?1:-1;
    var fromAngle=seg.atStart?arc.a1:arc.a2;
    var growSign=seg.atStart?-sign:sign;
    for(i=0;i<bSegs;i++){
      var cA=bPts[i],cB=bPts[(i+1)%bn],cb=bimBulgeAt(bBulges,i);
      var carc=bimBulgeArc(cA,cB,cb);
      var chits=carc?bimCircleCircleIntersect(arc.center,arc.radius,carc.center,carc.radius)
                    :bimCircleLineIntersect(arc.center,arc.radius,cA,[cB[0]-cA[0],cB[1]-cA[1]]);
      for(k=0;k<chits.length;k++){
        if(!bimSegRangeOk(cA,cB,cb,chits[k]))continue;
        var angH=Math.atan2(chits[k][1]-arc.center[1],chits[k][0]-arc.center[0]);
        var turn=(angH-fromAngle)*growSign;
        while(turn<=1e-9)turn+=Math.PI*2;
        while(turn>Math.PI*2)turn-=Math.PI*2;
        /* coming all the way round to the arc's own other end is not an extension */
        if(Math.abs(arc.sweep)+turn>=Math.PI*2-1e-9)continue;
        if(!best||turn<best.turn)best={turn:turn,pt:chits[k]};
      }
    }
    if(!best)return {error:'That end does not reach the boundary when extended'};
    var grown=bimGrowEnd(pts,bulges,endIdx,best.turn*arc.radius);
    if(grown.error)return grown;
    return {pts:grown.pts,bulges:grown.bulges,atPt:best.pt,added:best.turn*arc.radius};
  }
'''

out = src.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
