"""patch_phase90.py -- Phase 90 part 1: tangent-arc continuation and arc-aware offset geometry.

Ported verbatim from Phase/bim_phase90_arcdraw_offset_prototype.js (22/22), which earned one
correction the build would otherwise have shipped: a concentric offset keeps an arc's bulge only
while its endpoints move RADIALLY. At a kink the offset vertex is where the offset line crosses
the offset circle, which is somewhere else on that circle, so the arc spans a different angle and
the bulge has to be recomputed from the endpoints that actually ended up there.
"""
import hashlib, pathlib, sys

BASE = 'c685b2b3bdd2b4d11c816dfebe04cb6e97a31b8b8dd92de6c9f3327b98290e92'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

ANCHOR = "  /* ================= __acad3dV87: the modify toolbox, part one ========================="
assert src.count(ANCHOR) == 1, 'anchor count %d' % src.count(ANCHOR)

BLOCK = r'''  /* ================= __acad3dV90: drawing curves, and offsetting them ==================

     TANGENT CONTINUATION. The angle between a tangent and a chord is half the arc it subtends,
     so an arc leaving P along direction d and ending at Q sweeps twice the angle from d to the
     chord: bulge = tan(alpha/2). One click per arc segment instead of two, and the arc leaves
     the previous segment smoothly - which is the whole reason to draw a curved wall this way
     rather than with three points.

     ARC-AWARE OFFSET. A concentric offset of a circular arc subtends the same angle, so the
     SEGMENT keeps its bulge; what moves are the vertices, and a vertex is where two adjacent
     OFFSET segments meet. For line-line that is the existing mitre. For line-arc and arc-arc it
     is a real intersection, which is why the circle-line and circle-circle helpers are here -
     and they are what arc-aware TRIM will need too, so they are not written for one caller.

     THE CORRECTION THE PROTOTYPE EARNED: "a concentric arc keeps its bulge" holds for the
     segment, not for the stored bulge once the vertices move. At a TANGENT joint the offset
     vertex is the radial projection of the original, the sweep is unchanged and the bulge does
     carry over. At a KINK the vertex lands elsewhere on the offset circle, the arc spans a
     different angle, and keeping the original bulge silently produces an arc that is no longer
     concentric with the one it came from. Every offset arc's bulge is recomputed below from the
     endpoints it actually ended up with.
     ---------------------------------------------------------------------------------------- */
  function bimTangentBulge(dir,P,Q){
    if(!dir||!P||!Q)return null;
    var vx=Q[0]-P[0],vz=Q[1]-P[1];
    var vl=Math.sqrt(vx*vx+vz*vz);
    if(vl<1e-9)return null;
    var dl=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
    if(dl<1e-9)return null;
    var dx=dir[0]/dl,dz=dir[1]/dl;
    var ux=vx/vl,uz=vz/vl;
    var alpha=Math.atan2(dx*uz-dz*ux,dx*ux+dz*uz);
    /* Doubling straight back has no finite arc through it - tan(pi/2) is not an answer. */
    if(Math.abs(Math.abs(alpha)-Math.PI)<1e-6)return null;
    return Math.tan(alpha/2);
  }
  /* The direction a segment ARRIVES travelling, which is what the next tangent arc continues. */
  function bimSegEndDir(A,B,bulge){
    var arc=bimBulgeArc(A,B,bulge);
    if(!arc){
      var dx=B[0]-A[0],dz=B[1]-A[1],L=Math.sqrt(dx*dx+dz*dz)||1;
      return [dx/L,dz/L];
    }
    var rx=B[0]-arc.center[0],rz=B[1]-arc.center[1],L2=Math.sqrt(rx*rx+rz*rz)||1;
    var s=arc.sweep>=0?1:-1;
    return [-s*rz/L2,s*rx/L2];
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
  function bimNearestTo(list,ref){
    var best=null,bd=Infinity,i;
    for(i=0;i<list.length;i++){
      var d=(list[i][0]-ref[0])*(list[i][0]-ref[0])+(list[i][1]-ref[1])*(list[i][1]-ref[1]);
      if(d<bd){bd=d;best=list[i];}
    }
    return best;
  }
  function bimArcBulgeBetween(center,A,B,sweepSign){
    var a1=Math.atan2(A[1]-center[1],A[0]-center[0]);
    var a2=Math.atan2(B[1]-center[1],B[0]-center[0]);
    var d=a2-a1;
    if(sweepSign>=0){while(d<-1e-12)d+=Math.PI*2;while(d>=Math.PI*2)d-=Math.PI*2;}
    else{while(d>1e-12)d-=Math.PI*2;while(d<=-Math.PI*2)d+=Math.PI*2;}
    return Math.tan(d/4);
  }
  function bimOffsetSegment(A,B,bulge,dist){
    var arc=bimBulgeArc(A,B,bulge);
    if(!arc){
      var nrm=bimSegNormal(A,B);
      return {kind:'line',A:[A[0]+nrm[0]*dist,A[1]+nrm[1]*dist],
              B:[B[0]+nrm[0]*dist,B[1]+nrm[1]*dist],dir:[B[0]-A[0],B[1]-A[1]],bulge:0};
    }
    /* For a counter-clockwise arc the centre is to the LEFT of travel, which is the way a
       positive offset moves, so the radius SHRINKS. Clockwise, it grows. */
    var s=arc.sweep>=0?1:-1;
    var nr=arc.radius-s*dist;
    if(nr<=1e-6)return {error:'Offset distance is larger than the arc radius'};
    var k=nr/arc.radius;
    function radial(Pt){
      return [arc.center[0]+(Pt[0]-arc.center[0])*k,arc.center[1]+(Pt[1]-arc.center[1])*k];
    }
    return {kind:'arc',A:radial(A),B:radial(B),center:arc.center,radius:nr,bulge:bulge};
  }
  function bimJoinOffsetSegments(s1,s2,ref){
    if(s1.kind==='line'&&s2.kind==='line'){
      var d1=s1.dir,d2=s2.dir;
      var den=d1[0]*d2[1]-d1[1]*d2[0];
      if(Math.abs(den)<1e-12)return s1.B;
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
'''

out = src.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
