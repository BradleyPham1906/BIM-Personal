  /* ================= __acad3dV93: walking a distance along a curve ====================

     DIVIDE and MEASURE differ in one thing only: what decides the spacing. DIVIDE takes a
     count and splits the whole length into equal parts; MEASURE takes a distance and steps it
     off from the start until the object runs out. Everything else -- finding the point a given
     distance along geometry that may bend -- is the same operation, so it is written once.

     Measuring along the CHORD instead of the curve is the failure mode worth naming: the marks
     would bunch up at exactly the places the line bends, which is exactly where the drafter is
     looking. */
  function bimSegLengthAt(A,B,bulge){
    var arc=bimBulgeArc(A,B,bulge);
    if(arc)return Math.abs(arc.sweep)*arc.radius;
    return Math.sqrt((B[0]-A[0])*(B[0]-A[0])+(B[1]-A[1])*(B[1]-A[1]));
  }
  /* The point a distance s along the polyline, measured along the curve. null when s falls
     outside [0,total] -- deliberately not clamped, so a caller asking for a point that is not
     on the object gets nothing rather than a silently relocated one. */
  function bimPointAtLength(pts,bulges,closed,s){
    if(!pts||pts.length<2)return null;
    var total=bimBulgedLength(pts,bulges,closed);
    if(!(s>=-1e-9)||s>total+1e-9)return null;
    s=Math.max(0,Math.min(total,s));
    var n=pts.length,segs=closed?n:n-1,acc=0,i;
    for(i=0;i<segs;i++){
      var A=pts[i],B=pts[(i+1)%n],b=bimBulgeAt(bulges,i);
      var segLen=bimSegLengthAt(A,B,b);
      if(segLen<1e-12)continue;
      if(s<=acc+segLen+1e-9){
        var t=(s-acc)/segLen;
        t=Math.max(0,Math.min(1,t));
        var arc=bimBulgeArc(A,B,b);
        /* On an arc equal LENGTH is equal ANGLE, so the length fraction is the sweep
           parameter directly. That is only true because the radius is constant, and it is the
           whole reason this walk is exact rather than sampled. */
        return arc?bimArcPointAt(arc,t):[A[0]+(B[0]-A[0])*t,A[1]+(B[1]-A[1])*t];
      }
      acc+=segLen;
    }
    var last=pts[segs%n];
    return [last[0],last[1]];
  }
  /* DIVIDE: n segments means n-1 marks and neither endpoint is marked. AutoCAD's own rule, and
     the one people get wrong -- dividing into four places three points. */
  function bimDividePoints(pts,bulges,closed,n){
    if(!(n>=2)||Math.floor(n)!==n)
      return {error:'Number of segments must be a whole number of 2 or more'};
    if(n>1000)return {error:'That is more divisions than this command will place (limit 1000)'};
    var total=bimBulgedLength(pts,bulges,closed);
    if(total<1e-9)return {error:'That object has no length to divide'};
    var out=[],i,p;
    for(i=1;i<n;i++){
      p=bimPointAtLength(pts,bulges,closed,total*i/n);
      if(p)out.push(p);
    }
    return {points:out,spacing:total/n,total:total};
  }
  /* MEASURE: a mark every d from the start, and the remainder at the far end is expected. That
     leftover is REPORTED rather than swallowed, because a drafter measuring off a bar spacing
     needs to know what is left at the end. */
  function bimMeasurePoints(pts,bulges,closed,d){
    if(!isFinite(d)||d<=1e-9)return {error:'Spacing must be greater than zero'};
    var total=bimBulgedLength(pts,bulges,closed);
    if(total<1e-9)return {error:'That object has no length to measure along'};
    if(d>total)return {error:'Spacing is longer than the object'};
    if(total/d>1000)return {error:'That spacing would place more than 1000 points'};
    var out=[],s=d,p;
    while(s<=total+1e-9){
      p=bimPointAtLength(pts,bulges,closed,s);
      if(p)out.push(p);
      s+=d;
    }
    /* On a closed loop the final mark can land exactly back on the start. One point there, not
       two stacked on each other. */
    if(closed&&out.length){
      var f=bimPointAtLength(pts,bulges,closed,0),l=out[out.length-1];
      if(f&&Math.abs(f[0]-l[0])<1e-9&&Math.abs(f[1]-l[1])<1e-9)out.pop();
    }
    return {points:out,spacing:d,total:total,leftover:total-Math.floor(total/d+1e-9)*d};
  }
  /* ================= __acad3dV93: the two shapes =================

     A circle is two vertices, each with bulge 1 -- DXF's own convention, exact area, exact
     circumference, and two grips instead of twenty-four. It replaces a 24-sided polygon that
     predated arc storage and was out by 0.14 m2 on a 2 m circle. */
  function bimCircleSketch(center,radius){
    if(!center||!(radius>1e-6))return {error:'Circle radius must be greater than zero'};
    return {pts:[[center[0]-radius,center[1]],[center[0]+radius,center[1]]],
            bulges:[1,1],closed:true,center:[center[0],center[1]],radius:radius};
  }
  /* POLYGON, AutoCAD's two forms. INSCRIBED puts the VERTICES on the circle of the given
     radius; CIRCUMSCRIBED puts the EDGE MIDPOINTS on it, which makes the same radius produce
     the larger polygon. The circumscribed radius is derived from the inscribed one rather than
     asked for separately, so the two forms can never disagree about what the radius means. */
  function bimPolygonSketch(center,sides,radius,circumscribed,startAngle){
    if(!(sides>=3)||Math.floor(sides)!==sides)
      return {error:'A polygon needs a whole number of 3 or more sides'};
    if(sides>1024)return {error:'That is more sides than this command will draw (limit 1024)'};
    if(!center||!(radius>1e-6))return {error:'Polygon radius must be greater than zero'};
    var R=circumscribed?radius/Math.cos(Math.PI/sides):radius;
    var a0=(typeof startAngle==='number'&&isFinite(startAngle))?startAngle:Math.PI/2;
    var pts=[],i,a;
    for(i=0;i<sides;i++){
      a=a0+i*2*Math.PI/sides;
      pts.push([center[0]+Math.cos(a)*R,center[1]+Math.sin(a)*R]);
    }
    return {pts:pts,bulges:null,closed:true,vertexRadius:R,sides:sides,
            center:[center[0],center[1]],circumscribed:!!circumscribed};
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
