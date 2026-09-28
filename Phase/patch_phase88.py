"""patch_phase88.py -- Phase 88 part 1: arc storage.

THE DECISION PIPELINE ASKED FOR, made here: bulge factor per vertex, not a segment-type array.

Ported verbatim from bim_phase88_bulge_prototype.js (29/29), which caught the one sign error in
the perpendicular before any of this reached the build.
"""
import hashlib, pathlib, sys

BASE = '26e32d355a3496910022126f43f8caa95b0cd45bd03653a6a8e116dbcd12bc2b'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

ANCHOR = "  /* ================= __acad3dV87: the modify toolbox, part one ========================="
assert src.count(ANCHOR) == 1, 'anchor count %d' % src.count(ANCHOR)

BLOCK = r'''  /* ================= __acad3dV88: arc storage =========================================

     PIPELINE put one decision ahead of this whole phase -- bulge factor per vertex, or a
     segment-type array - because ARC, ELLIPSE, SPLINE, DONUT and the radius FILLET all rest on
     it. Decided here, with the reasoning, so it is not re-litigated later:

     BULGE FACTOR PER VERTEX. A polyline optionally carries a `bulges` array parallel to `pts`;
     bulges[i] describes the segment from pts[i] to pts[i+1] (wrapping when closed). 0, absent,
     or no array at all means straight, which is exactly the data every polyline in this file
     holds today.

     Why, in the order the reasons actually weighed:

     1. IT DEGRADES GRACEFULLY, AND THAT DECIDES IT. Eighteen places in this file read a sketch
        `pts` array, and many more read wall centerlines and floor profiles: offset, trim,
        extend, chamfer, break, lengthen, area, snaps, grips, constraints, DXF, SVG, sheets,
        schedules, picking, rendering. With a bulge array, every one of them keeps working
        untouched and sees the chord - which is what it draws and computes today, so nothing
        regresses on the day the array is introduced. Each is then taught the curve one at a
        time, by calling bimFlattenPoly. A segment-type array changes the SHAPE of the data, so
        every one of those readers is silently wrong the moment the first arc is stored: the
        V84 "flat means plan view" lesson multiplied by eighteen.
     2. IT IS THE FORMAT THIS FILE ALREADY WRITES. Bulge is DXF group code 42 on LWPOLYLINE.
        Today bimImportDXF TESSELLATES an incoming ARC into chords and bimBuildDXF emits no 42
        at all, so an arc that enters this app is destroyed and can never leave as an arc.
        Bulge storage makes the round trip exact with no translation layer in between.
     3. THE MATH IS CLOSED-FORM AND SMALL - everything below derives from (p1, p2, bulge).
     4. IT COSTS NOTHING IN FUTURE EXPRESSIVENESS. Bulge cannot describe a spline or a true
        ellipse - but neither can a segment-type array without carrying control points, so those
        are separate entity types either way. The segment-type array does not save that work; it
        only front-loads a migration.

     Convention: bulge = tan(sweep/4), signed, POSITIVE = COUNTER-CLOCKWISE, which is DXF's own.
     A full circle is two vertices each with bulge 1, also DXF's convention.

     ONE SIGN, PROVED RATHER THAN ARGUED: for a positive (counter-clockwise) bulge the centre
     lies to the LEFT of travel, so the arc swells to the RIGHT - chord (0,0)-(2,0) with bulge
     +1 is the semicircle through (1,-1), NOT (1,1). The prototype had it backwards, and the
     check that caught it is neither a radius nor a centre comparison but "the swept arc must
     END where the chord ends", which a flipped perpendicular fails and everything else passes.
     ---------------------------------------------------------------------------------------- */
  var BIM_BULGE_EPS=1e-9;
  var BIM_ARC_TOL=0.002;        /* max chord-to-arc departure when flattening, in metres */
  function bimBulgeAt(bulges,i){
    if(!bulges||i<0||i>=bulges.length)return 0;
    var b=bulges[i];
    return (typeof b==='number'&&isFinite(b))?b:0;
  }
  function bimHasBulge(bulges){
    if(!bulges||!bulges.length)return false;
    var i;
    for(i=0;i<bulges.length;i++)if(Math.abs(bimBulgeAt(bulges,i))>BIM_BULGE_EPS)return true;
    return false;
  }
  function bimBulgeArc(p1,p2,b){
    if(!p1||!p2||!isFinite(b)||Math.abs(b)<BIM_BULGE_EPS)return null;
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    var c=Math.sqrt(dx*dx+dz*dz);
    if(c<1e-12)return null;
    var ux=dx/c,uz=dz/c;
    var mx=uz,mz=-ux;                     /* chord direction rotated -90deg; see the note above */
    var sag=b*c/2;
    var apex=[(p1[0]+p2[0])/2+mx*sag,(p1[1]+p2[1])/2+mz*sag];
    var cir=bimCircleFrom3Points(p1,apex,p2);
    if(!cir)return null;
    var sweep=4*Math.atan(b);
    var a1=Math.atan2(p1[1]-cir.center[1],p1[0]-cir.center[0]);
    return {center:cir.center,radius:cir.radius,a1:a1,a2:a1+sweep,sweep:sweep,apex:apex,chord:c};
  }
  /* Segment count from a chord TOLERANCE rather than a fixed number, so a 40 m arc is not drawn
     with the same eight chords as a 200 mm one. Derived from the geometry it describes. */
  function bimArcSegments(radius,sweep,tol){
    tol=(typeof tol==='number'&&tol>0)?tol:BIM_ARC_TOL;
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
  /* THE one place a curve becomes points. Every consumer that needs the real shape calls this;
     none of them tessellate for themselves, so none of them can disagree about how. */
  function bimFlattenPoly(pts,bulges,closed,tol){
    if(!pts||pts.length<2)return pts?pts.map(function(p){return [p[0],p[1]];}):[];
    if(!bimHasBulge(bulges))return pts.map(function(p){return [p[0],p[1]];});
    var n=pts.length,segs=closed?n:n-1,out=[],i,k;
    for(i=0;i<segs;i++){
      out.push([pts[i][0],pts[i][1]]);
      var mid=bimBulgeSegPoints(pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i),tol);
      for(k=0;k<mid.length;k++)out.push(mid[k]);
    }
    if(!closed)out.push([pts[n-1][0],pts[n-1][1]]);
    return out;
  }
  function bimFlattenSketch(o,tol){
    if(!o||!o.pts)return null;
    return bimFlattenPoly(o.pts,o.bulges,o.closed!==false,tol);
  }
  function bimBulgeFrom3Pts(p1,pm,p2){
    var cir=bimCircleFrom3Points(p1,pm,p2);
    if(!cir)return 0;
    var a1=Math.atan2(p1[1]-cir.center[1],p1[0]-cir.center[0]);
    var am=Math.atan2(pm[1]-cir.center[1],pm[0]-cir.center[0]);
    var a2=Math.atan2(p2[1]-cir.center[1],p2[0]-cir.center[0]);
    function norm(a){while(a<0)a+=Math.PI*2;while(a>=Math.PI*2)a-=Math.PI*2;return a;}
    var dm=norm(am-a1),d2=norm(a2-a1);
    var sweep=(dm<d2)?d2:-(Math.PI*2-d2);
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
  /* Shoelace over the vertices plus one circular-segment correction per arc. Checked against the
     case with a known answer: two vertices, both bulge 1, enclose exactly pi for a unit circle. */
  function bimBulgedArea(pts,bulges,closed){
    if(!pts||pts.length<2)return 0;
    var n=pts.length,a=0,i,j;
    for(i=0;i<n;i++){j=(i+1)%n;a+=pts[i][0]*pts[j][1]-pts[j][0]*pts[i][1];}
    a/=2;
    var segs=closed?n:n-1;
    for(i=0;i<segs;i++){
      var arc=bimBulgeArc(pts[i],pts[(i+1)%n],bimBulgeAt(bulges,i));
      if(!arc)continue;
      a+=arc.radius*arc.radius*(arc.sweep-Math.sin(arc.sweep))/2;
    }
    return Math.abs(a);
  }
  /* Is a point on the SWEPT part of an arc (not merely on its circle)? Exact - an angle test,
     not a walk along sampled points. */
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
'''

out = src.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
