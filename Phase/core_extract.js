var BIM_BULGE_EPS=1e-9;
var BIM_ARC_TOL=0.002;
var BIM_NODE_TOL=4;
  function bimPointInPoly(pt,poly){
    var x=pt[0],z=pt[1],inside=false,i,j;
    for(i=0,j=poly.length-1;i<poly.length;j=i++){
      var xi=poly[i][0],zi=poly[i][1],xj=poly[j][0],zj=poly[j][1];
      var intersect=((zi>z)!==(zj>z))&&(x<(xj-xi)*(z-zi)/(zj-zi)+xi);
      if(intersect)inside=!inside;
    }
    return inside;
  }
  function bimPolyArea(poly){
    var a=0,i,n=poly.length;
    for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
    return Math.abs(a)/2;
  }
  function bimPolySignedArea(poly){
    var a=0,i,n=poly.length;
    for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
    return a/2;
  }
  function bimGraphNodeKey(p){return p[0].toFixed(BIM_NODE_TOL)+','+p[1].toFixed(BIM_NODE_TOL);}
  function bimBuildWallGraph(segments){
    var nodes={},adj={};
    function addNode(p){
      var key=bimGraphNodeKey(p);
      if(!nodes[key]){nodes[key]=p;adj[key]=[];}
      return key;
    }
    var i;
    for(i=0;i<segments.length;i++){
      var a=addNode(segments[i][0]),b=addNode(segments[i][1]);
      if(a===b)continue;
      if(adj[a].indexOf(b)<0)adj[a].push(b);
      if(adj[b].indexOf(a)<0)adj[b].push(a);
    }
    return {nodes:nodes,adj:adj};
  }
  function bimTraceFaces(graph){
    var nodes=graph.nodes,adj=graph.adj;
    var visited={},faces=[];
    function angleOf(fromK,toK){
      var a=nodes[fromK],b=nodes[toK];
      return Math.atan2(b[1]-a[1],b[0]-a[0]);
    }
    var k;
    for(k in adj){
      if(!adj.hasOwnProperty(k))continue;
      var neighbors=adj[k],ni;
      for(ni=0;ni<neighbors.length;ni++){
        var startFrom=k,startTo=neighbors[ni];
        if(visited[startFrom+'>'+startTo])continue;
        var loop=[],curFrom=startFrom,curTo=startTo,guard=0;
        while(guard++<10000){
          visited[curFrom+'>'+curTo]=true;
          loop.push(nodes[curFrom]);
          var incomingAngle=angleOf(curTo,curFrom);
          var cand=adj[curTo],best=null,bestDelta=Infinity,ci;
          for(ci=0;ci<cand.length;ci++){
            var c=cand[ci];
            if(c===curFrom&&cand.length>1)continue;
            var outAngle=angleOf(curTo,c);
            var delta=incomingAngle-outAngle;
            while(delta<=0)delta+=Math.PI*2;
            while(delta>Math.PI*2)delta-=Math.PI*2;
            if(delta<bestDelta){bestDelta=delta;best=c;}
          }
          if(best===null)best=curFrom;
          var nextFrom=curTo,nextTo=best;
          if(nextFrom===startFrom&&nextTo===startTo)break;
          curFrom=nextFrom;curTo=nextTo;
        }
        if(loop.length>=3)faces.push(loop);
      }
    }
    return faces;
  }
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
      hits=bimCircleLineIntersect(arc.center,arc.radius,LA,[LB[0]-LA[0],LB[1]-LA[1]]);
    }
    var out=[];
    for(i=0;i<hits.length;i++){
      if(bimSegRangeOk(A1,B1,b1,hits[i])&&bimSegRangeOk(A2,B2,b2,hits[i]))out.push(hits[i]);
    }
    return out;
  }
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
  function bimSegIntersectParams(a1,a2,b1,b2){
    var d1x=a2[0]-a1[0],d1z=a2[1]-a1[1];
    var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
    var den=d1x*d2z-d1z*d2x;
    if(Math.abs(den)<1e-12)return null;
    var dx=b1[0]-a1[0],dz=b1[1]-a1[1];
    var t=(dx*d2z-dz*d2x)/den;
    var u=(dx*d1z-dz*d1x)/den;
    return {pt:[a1[0]+d1x*t,a1[1]+d1z*t],t:t,u:u};
  }
  function bimSegLengthAt(A,B,bulge){
    var arc=bimBulgeArc(A,B,bulge);
    if(arc)return Math.abs(arc.sweep)*arc.radius;
    return Math.sqrt((B[0]-A[0])*(B[0]-A[0])+(B[1]-A[1])*(B[1]-A[1]));
  }
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
  function sketchCCW(pts){
    var a=0,i,j,P=pts.slice();
    for(i=0;i<P.length;i++){
      j=(i+1)%P.length;
      a+=P[i][0]*P[j][1]-P[j][0]*P[i][1];
    }
    if(a<0)P.reverse();
    return P;
  }
  function bimClipInfinite(P,dir,isRay,box){
    if(!P||!dir||!box)return null;
    var len=Math.sqrt(dir[0]*dir[0]+dir[1]*dir[1]);
    if(!(len>1e-12))return null;
    var d=[dir[0]/len,dir[1]/len];
    var tMin=isRay?0:-Infinity,tMax=Infinity;
    var p=[-d[0],d[0],-d[1],d[1]];
    var q=[P[0]-box.minX,box.maxX-P[0],P[1]-box.minZ,box.maxZ-P[1]];
    var i,t;
    for(i=0;i<4;i++){
      if(Math.abs(p[i])<1e-12){
        /* Parallel to this pair of edges. Outside them, no value of t brings it in. */
        if(q[i]<0)return null;
        continue;
      }
      t=q[i]/p[i];
      if(p[i]<0){if(t>tMin)tMin=t;}
      else{if(t<tMax)tMax=t;}
    }
    if(tMin>tMax)return null;
    if(!isFinite(tMin)||!isFinite(tMax))return null;
    return [[P[0]+d[0]*tMin,P[1]+d[1]*tMin],[P[0]+d[0]*tMax,P[1]+d[1]*tMax]];
  }
  function bimArcSegments(radius,sweep,tol){
    tol=(typeof tol==='number'&&tol>0)?tol:BIM_ARC_TOL;
    var s=Math.abs(sweep);
    if(!isFinite(radius)||radius<=tol)return 2;
    var maxStep=2*Math.acos(Math.max(-1,Math.min(1,1-tol/radius)));
    if(!isFinite(maxStep)||maxStep<1e-6)maxStep=Math.PI/64;
    return Math.max(2,Math.min(256,Math.ceil(s/maxStep)));
  }
module.exports={bimArcSegments:bimArcSegments,bimPointInPoly:bimPointInPoly,bimPolyArea:bimPolyArea,bimPolySignedArea:bimPolySignedArea,bimGraphNodeKey:bimGraphNodeKey,bimBuildWallGraph:bimBuildWallGraph,bimTraceFaces:bimTraceFaces,bimCircleFrom3Points:bimCircleFrom3Points,bimBulgeAt:bimBulgeAt,bimHasBulge:bimHasBulge,bimBulgeArc:bimBulgeArc,bimBulgeSegPoints:bimBulgeSegPoints,bimFlattenPoly:bimFlattenPoly,bimBulgedLength:bimBulgedLength,bimBulgedArea:bimBulgedArea,bimPointOnSweptArc:bimPointOnSweptArc,bimArcParamAt:bimArcParamAt,bimArcPointAt:bimArcPointAt,bimPtDistToBulgedSeg:bimPtDistToBulgedSeg,bimSegRangeOk:bimSegRangeOk,bimIntersectBulgedSegs:bimIntersectBulgedSegs,bimSegEndDir:bimSegEndDir,bimCircleLineIntersect:bimCircleLineIntersect,bimCircleCircleIntersect:bimCircleCircleIntersect,bimNearestTo:bimNearestTo,bimArcBulgeBetween:bimArcBulgeBetween,bimSegIntersectParams:bimSegIntersectParams,bimSegLengthAt:bimSegLengthAt,bimPointAtLength:bimPointAtLength,sketchCCW:sketchCCW,bimClipInfinite:bimClipInfinite};
