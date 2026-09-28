"""patch_phase87.py -- Phase 87 part 1: the modify toolbox geometry core.

Pure polyline operations (extend, break, lengthen, chamfer, scale-point) inserted ahead of
startTrimTool, beside the trim/offset helpers they sit next to conceptually.

Baseline: canvas_v10.html at c0a7dd... (the V86 build).
"""
import hashlib, pathlib, sys

BASE = 'c0a7ddade2dc0a764f3a00b248614669c7fc61b516b3dcb60cef163158d4cff9'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

ANCHOR = "  function startTrimTool(){"
assert src.count(ANCHOR) == 1, 'anchor count %d' % src.count(ANCHOR)

BLOCK = r'''  /* ================= __acad3dV87: the modify toolbox, part one =========================

     Pure polyline operations. Each takes point arrays and returns point arrays or an {error};
     none of them touch the model or the DOM, so the browser suite asserts on the GEOMETRY that
     comes out rather than on what the screen looks like afterwards. That is the V86 lesson
     applied before the bug rather than after it.

     WHAT IS DELIBERATELY NOT HERE: a radius FILLET. A rounded corner is an ARC, and this file
     has no arc storage yet -- Phase 88 decides between a bulge factor per vertex and a
     segment-type array, and four drawing tools depend on that answer. A chord-approximated arc
     written here would be geometry the real arc storage then disagrees with, which is precisely
     the leftover Standing Law 1 is about. So FILLET runs at radius 0 -- the corner case, which
     is AutoCAD's own behaviour when the radius is 0 -- and says so in the toast. CHAMFER is
     straight geometry, needs no arcs, and is implemented in full below.

     AutoCAD reference this was built against:
       EXTEND  "Extends objects to meet the edges of other objects." The picked END is the one
               that moves, and it moves along its own direction until it meets the boundary.
       BREAK   two points: the piece BETWEEN them is removed, leaving two objects.
       BREAKATPOINT  one point: split in place with nothing removed.
       LENGTHEN  DElta / Total / Percent, applied at the end nearest the pick.
       CHAMFER "Bevels the edges of objects", two distances measured back from the corner.
     ---------------------------------------------------------------------------------------- */
  function bimRaySegIntersect(P,D,b1,b2){
    var d2x=b2[0]-b1[0],d2z=b2[1]-b1[1];
    var den=D[0]*d2z-D[1]*d2x;
    if(Math.abs(den)<1e-12)return null;
    var dx=b1[0]-P[0],dz=b1[1]-P[1];
    var t=(dx*d2z-dz*d2x)/den;
    var u=(dx*D[1]-dz*D[0])/den;
    return {t:t,u:u,pt:[P[0]+D[0]*t,P[1]+D[1]*t]};
  }
  function bimDedupePts(arr){
    if(!arr||!arr.length)return [];
    var out=[arr[0]],i;
    for(i=1;i<arr.length;i++){
      var pv=out[out.length-1];
      if(Math.abs(pv[0]-arr[i][0])>1e-6||Math.abs(pv[1]-arr[i][1])>1e-6)out.push(arr[i]);
    }
    return out;
  }
  function bimPolyLength(pts,closed){
    if(!pts||pts.length<2)return 0;
    var n=pts.length,segs=closed?n:n-1,L=0,i;
    for(i=0;i<segs;i++){
      var a=pts[i],b=pts[(i+1)%n];
      L+=Math.sqrt((b[0]-a[0])*(b[0]-a[0])+(b[1]-a[1])*(b[1]-a[1]));
    }
    return L;
  }
  function bimProjectOntoPolyline(pts,closed,p){
    if(!pts||pts.length<2)return null;
    var n=pts.length,segs=closed?n:n-1,best=null,i;
    for(i=0;i<segs;i++){
      var a=pts[i],b=pts[(i+1)%n];
      var dx=b[0]-a[0],dz=b[1]-a[1],L2=dx*dx+dz*dz;
      var t=L2?((p[0]-a[0])*dx+(p[1]-a[1])*dz)/L2:0;
      t=Math.max(0,Math.min(1,t));
      var q=[a[0]+dx*t,a[1]+dz*t];
      var d=Math.sqrt((p[0]-q[0])*(p[0]-q[0])+(p[1]-q[1])*(p[1]-q[1]));
      if(!best||d<best.dist)best={seg:i,t:t,pt:q,dist:d};
    }
    return best;
  }
  /* Which free end the user meant, by proximity to the pick -- the same rule AutoCAD uses for
     EXTEND and LENGTHEN, and the reason both commands take a click rather than a dialog field. */
  function bimNearestEndIndex(pts,p){
    var n=pts.length;
    var d0=(pts[0][0]-p[0])*(pts[0][0]-p[0])+(pts[0][1]-p[1])*(pts[0][1]-p[1]);
    var d1=(pts[n-1][0]-p[0])*(pts[n-1][0]-p[0])+(pts[n-1][1]-p[1])*(pts[n-1][1]-p[1]);
    return d0<=d1?0:n-1;
  }
  function bimExtendPolyline(pts,closed,bPts,bClosed,clickPt){
    if(closed)return {error:'Extend needs an open wall (a closed loop has no free end)'};
    if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
    if(!bPts||bPts.length<2)return {error:'Boundary wall has no usable centerline'};
    var n=pts.length;
    var endIdx=bimNearestEndIndex(pts,clickPt);
    var nb=endIdx===0?1:n-2;
    var end=pts[endIdx],neigh=pts[nb];
    var dx=end[0]-neigh[0],dz=end[1]-neigh[1];
    var segLen=Math.sqrt(dx*dx+dz*dz);
    if(segLen<1e-9)return {error:'The end segment has zero length'};
    var D=[dx/segLen,dz/segLen];
    var bn=bPts.length,bsegs=bClosed?bn:bn-1,best=null,i;
    for(i=0;i<bsegs;i++){
      var r=bimRaySegIntersect(end,D,bPts[i],bPts[(i+1)%bn]);
      if(!r)continue;
      if(r.t<1e-9)continue;                       /* forward only: EXTEND never runs backwards */
      if(r.u<-1e-9||r.u>1+1e-9)continue;          /* and the boundary must really be there */
      if(!best||r.t<best.t)best=r;
    }
    if(!best)return {error:'That end does not reach the boundary when extended'};
    var out=pts.map(function(p){return [p[0],p[1]];});
    out[endIdx]=[best.pt[0],best.pt[1]];
    return {pts:out,atPt:[best.pt[0],best.pt[1]],endIdx:endIdx,added:best.t};
  }
  function bimBreakPolyline(pts,closed,p1,p2){
    if(closed)return {error:'Break needs an open wall (breaking a closed loop is not supported)'};
    if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
    var a=bimProjectOntoPolyline(pts,false,p1);
    var b=p2?bimProjectOntoPolyline(pts,false,p2):a;
    if(!a||!b)return {error:'Break point is not on the wall'};
    var lo=(a.seg+a.t)<=(b.seg+b.t)?a:b;
    var hi=(a.seg+a.t)<=(b.seg+b.t)?b:a;
    var n=pts.length,k,left=[],right=[];
    for(k=0;k<=lo.seg;k++)left.push([pts[k][0],pts[k][1]]);
    left.push([lo.pt[0],lo.pt[1]]);
    right.push([hi.pt[0],hi.pt[1]]);
    for(k=hi.seg+1;k<n;k++)right.push([pts[k][0],pts[k][1]]);
    left=bimDedupePts(left);right=bimDedupePts(right);
    if(left.length<2)return {error:'That break point is at the start of the wall - there would be nothing on that side'};
    if(right.length<2)return {error:'That break point is at the end of the wall - there would be nothing on that side'};
    return {a:left,b:right,cutA:[lo.pt[0],lo.pt[1]],cutB:[hi.pt[0],hi.pt[1]],
            removed:bimPolyLength(pts,false)-bimPolyLength(left,false)-bimPolyLength(right,false)};
  }
  function bimLengthenPolyline(pts,closed,mode,value,clickPt){
    if(closed)return {error:'Lengthen needs an open wall'};
    if(!pts||pts.length<2)return {error:'Wall has no usable centerline'};
    if(!isFinite(value))return {error:'Lengthen value must be a number'};
    var L=bimPolyLength(pts,false);
    var target;
    if(mode==='total')target=value;
    else if(mode==='percent')target=L*value/100;
    else target=L+value;
    if(!isFinite(target)||target<=1e-6)return {error:'That would leave the wall with no length'};
    var n=pts.length;
    var endIdx=bimNearestEndIndex(pts,clickPt);
    var nb=endIdx===0?1:n-2;
    var end=pts[endIdx],neigh=pts[nb];
    var dx=end[0]-neigh[0],dz=end[1]-neigh[1];
    var segLen=Math.sqrt(dx*dx+dz*dz);
    if(segLen<1e-9)return {error:'The end segment has zero length'};
    var change=target-L;
    /* Shortening past the previous vertex would silently eat a vertex and change the wall's
       shape, not its length. Refused with the command that does do that, rather than guessed. */
    if(change<0&&(-change)>=segLen-1e-9)
      return {error:'Lengthen cannot shorten past the next vertex - use Break or Trim for that'};
    var D=[dx/segLen,dz/segLen];
    var out=pts.map(function(p){return [p[0],p[1]];});
    out[endIdx]=[end[0]+D[0]*change,end[1]+D[1]*change];
    return {pts:out,length:target,delta:change,endIdx:endIdx};
  }
  function bimChamferPolylines(clA,closedA,clB,closedB,d1,d2){
    if(closedA||closedB)return {error:'Chamfer needs two open walls'};
    if(!clA||clA.length<2||!clB||clB.length<2)return {error:'Both walls need a usable centerline'};
    if(!isFinite(d1)||!isFinite(d2)||d1<=0||d2<=0)
      return {error:'Both chamfer distances must be greater than zero (a zero-distance chamfer IS the corner case - run Fillet)'};
    var endsA=[0,clA.length-1],endsB=[0,clB.length-1],best=null,ia,ib;
    for(ia=0;ia<2;ia++)for(ib=0;ib<2;ib++){
      var pa=clA[endsA[ia]],pb=clB[endsB[ib]];
      var d=(pa[0]-pb[0])*(pa[0]-pb[0])+(pa[1]-pb[1])*(pa[1]-pb[1]);
      if(!best||d<best.d)best={d:d,ai:endsA[ia],bi:endsB[ib]};
    }
    var aNb=best.ai===0?1:clA.length-2,bNb=best.bi===0?1:clB.length-2;
    var ip=bimLineLineIntersect(clA[aNb],clA[best.ai],clB[bNb],clB[best.bi]);
    if(!ip)return {error:'Those two walls are parallel - there is no corner to chamfer'};
    function backFrom(corner,neigh,dist,label){
      var vx=neigh[0]-corner[0],vz=neigh[1]-corner[1];
      var L=Math.sqrt(vx*vx+vz*vz);
      if(L<1e-9)return {error:'The wall '+label+' has zero length at the corner'};
      if(dist>=L)return {error:'Chamfer distance '+label+' is longer than the wall it cuts back ('+L.toFixed(3)+' m available)'};
      return {pt:[corner[0]+vx/L*dist,corner[1]+vz/L*dist]};
    }
    var ra=backFrom(ip,clA[aNb],d1,'on the first wall');
    if(ra.error)return {error:ra.error};
    var rb=backFrom(ip,clB[bNb],d2,'on the second wall');
    if(rb.error)return {error:rb.error};
    var outA=clA.map(function(p){return [p[0],p[1]];});
    var outB=clB.map(function(p){return [p[0],p[1]];});
    outA[best.ai]=[ra.pt[0],ra.pt[1]];
    outB[best.bi]=[rb.pt[0],rb.pt[1]];
    return {a:outA,b:outB,chamfer:[[ra.pt[0],ra.pt[1]],[rb.pt[0],rb.pt[1]]],corner:[ip[0],ip[1]]};
  }
  function bimScalePoint(p,base,k){
    return [base[0]+(p[0]-base[0])*k,base[1]+(p[1]-base[1])*k];
  }
'''

out = src.replace(ANCHOR, BLOCK + ANCHOR, 1)
assert out != src
b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
