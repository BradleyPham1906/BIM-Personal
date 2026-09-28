/* bim_phase95_boundary_prototype.js

   Phase 95: BOUNDARY. Pick a point in empty space, get the closed loop of geometry enclosing
   it, from whatever curves happen to cross there.

   THE FACE WALK ALREADY EXISTS. bimTraceFaces (V22) walks a planar graph taking the smallest
   clockwise turn at every node, and it is correct. What has never existed is the ARRANGEMENT
   in front of it: edges are put into that graph exactly as drawn, so two lines that cross
   mid-span without sharing a vertex produce no node at the crossing and the face is invisible.
   That is why room tracing has only ever worked on walls that meet end to end.

   This prototype builds the missing half:

     1. split every edge at every crossing with every other edge, arcs included;
     2. an angular key taken from the TANGENT rather than the chord, because on a curved edge
        the chord points somewhere the curve does not go;
     3. a signed area that accounts for the arcs, so the outer face is told from the inner ones
        correctly when the boundary bulges.

   The real functions are pulled out of canvas_v10.html rather than reimplemented here, so a
   passing prototype is evidence about the shipped code and not about a copy of it. */

var C = require('./core_extract.js');
var bimBulgeArc = C.bimBulgeArc, bimBulgeAt = C.bimBulgeAt, bimArcPointAt = C.bimArcPointAt,
    bimArcParamAt = C.bimArcParamAt, bimSegEndDir = C.bimSegEndDir,
    bimArcBulgeBetween = C.bimArcBulgeBetween,
    bimIntersectBulgedSegs = C.bimIntersectBulgedSegs, bimFlattenPoly = C.bimFlattenPoly,
    bimPointInPoly = C.bimPointInPoly, bimBulgedArea = C.bimBulgedArea,
    bimGraphNodeKey = C.bimGraphNodeKey, bimHasBulge = C.bimHasBulge;
var BIM_BULGE_EPS = 1e-9;

/* ---------------------------------------------------------------- signed area, with arcs */
/* bimBulgedArea returns the magnitude. The face walk needs the SIGN, because that is what
   separates the one outer face (clockwise) from the inner ones. Same formula, no Math.abs --
   so in the build bimBulgedArea becomes Math.abs of this rather than a second copy. */
function bimBulgedSignedArea(pts,bulges,closed){
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
  return a;
}

/* ---------------------------------------------------------------- edge helpers */
/* An edge is {a,b,bulge}. Its direction of travel at either end is the TANGENT, which on an
   arc is not the chord -- the whole reason the existing walk cannot be reused unchanged. */
function bimEdgeDirAt(e,atStart){
  if(!atStart)return bimSegEndDir(e.a,e.b,e.bulge);
  var d=bimSegEndDir(e.b,e.a,-e.bulge);   /* arriving at a while travelling b->a */
  return [-d[0],-d[1]];                    /* leaving a toward b is the reverse of that */
}
function bimEdgeLen(e){
  var arc=bimBulgeArc(e.a,e.b,e.bulge);
  if(arc)return Math.abs(arc.sweep)*arc.radius;
  return Math.sqrt((e.b[0]-e.a[0])*(e.b[0]-e.a[0])+(e.b[1]-e.a[1])*(e.b[1]-e.a[1]));
}
function bimEdgeParamAt(e,p){
  var arc=bimBulgeArc(e.a,e.b,e.bulge);
  if(arc)return bimArcParamAt(arc,p);
  var dx=e.b[0]-e.a[0],dz=e.b[1]-e.a[1];
  var dd=dx*dx+dz*dz;
  if(dd<1e-18)return null;
  return ((p[0]-e.a[0])*dx+(p[1]-e.a[1])*dz)/dd;
}
/* One edge cut at a list of points. An arc's pieces get their bulges recomputed about the
   SAME centre, so the pieces lie on the original circle rather than approximating it. */
function bimSplitEdge(e,cuts){
  var arc=bimBulgeArc(e.a,e.b,e.bulge);
  var items=[],i,t;
  for(i=0;i<cuts.length;i++){
    t=bimEdgeParamAt(e,cuts[i]);
    if(t===null||!isFinite(t))continue;
    if(t<=1e-9||t>=1-1e-9)continue;        /* an endpoint is already a node */
    items.push({t:t,p:[cuts[i][0],cuts[i][1]]});
  }
  if(!items.length)return [e];
  items.sort(function(x,y){return x.t-y.t;});
  var kept=[],k;
  for(k=0;k<items.length;k++)
    if(!kept.length||items[k].t-kept[kept.length-1].t>1e-9)kept.push(items[k]);
  var out=[],prev=e.a,sign=arc?(arc.sweep>=0?1:-1):0;
  for(k=0;k<kept.length;k++){
    out.push({a:prev,b:kept[k].p,
      bulge:arc?bimArcBulgeBetween(arc.center,prev,kept[k].p,sign):0});
    prev=kept[k].p;
  }
  out.push({a:prev,b:e.b,bulge:arc?bimArcBulgeBetween(arc.center,prev,e.b,sign):0});
  return out;
}
/* The arrangement: every edge cut at every crossing with every other edge. */
function bimArrangeEdges(edges,limit){
  limit=limit||400;
  if(edges.length>limit)
    return {error:'Too much geometry to trace here ('+edges.length+' edges, limit '+limit+')'};
  var cuts=[],i,j,k,hits;
  for(i=0;i<edges.length;i++)cuts.push([]);
  for(i=0;i<edges.length;i++)for(j=i+1;j<edges.length;j++){
    hits=bimIntersectBulgedSegs(edges[i].a,edges[i].b,edges[i].bulge,
                                edges[j].a,edges[j].b,edges[j].bulge);
    for(k=0;k<hits.length;k++){cuts[i].push(hits[k]);cuts[j].push(hits[k]);}
  }
  var out=[],pieces;
  for(i=0;i<edges.length;i++){
    pieces=bimSplitEdge(edges[i],cuts[i]);
    for(k=0;k<pieces.length;k++)
      if(bimEdgeLen(pieces[k])>1e-7)out.push(pieces[k]);
  }
  return {edges:out};
}

/* ---------------------------------------------------------------- the walk */
function bimBuildEdgeGraph(edges){
  var nodes={},adj={},i,ka,kb;
  function put(k,p){if(!nodes[k])nodes[k]=[p[0],p[1]];if(!adj[k])adj[k]=[];}
  for(i=0;i<edges.length;i++){
    ka=bimGraphNodeKey(edges[i].a);kb=bimGraphNodeKey(edges[i].b);
    if(ka===kb)continue;
    put(ka,edges[i].a);put(kb,edges[i].b);
    adj[ka].push({e:i,forward:true,to:kb});
    adj[kb].push({e:i,forward:false,to:ka});
  }
  return {nodes:nodes,adj:adj,edges:edges};
}
function bimHalfArriveDir(g,h){
  var e=g.edges[h.e];
  return h.forward?bimEdgeDirAt(e,false):[-bimEdgeDirAt(e,true)[0],-bimEdgeDirAt(e,true)[1]];
}
function bimHalfLeaveDir(g,h){
  var e=g.edges[h.e];
  return h.forward?bimEdgeDirAt(e,true):[-bimEdgeDirAt(e,false)[0],-bimEdgeDirAt(e,false)[1]];
}
function bimHalfFrom(g,h){var e=g.edges[h.e];return h.forward?e.a:e.b;}
function bimHalfTo(g,h){var e=g.edges[h.e];return h.forward?e.b:e.a;}
function bimHalfBulge(g,h){var e=g.edges[h.e];return h.forward?e.bulge:-e.bulge;}

/* Trace every face. At each node the next half-edge is the smallest positive clockwise turn
   from the reversed arrival direction -- the same rule bimTraceFaces already uses, with the
   angles taken from tangents instead of chords. */
function bimTraceEdgeFaces(g){
  var faces=[],seen={},k,key;
  var keys=Object.keys(g.adj);
  function hid(h){return h.e+(h.forward?'f':'r');}
  for(k=0;k<keys.length;k++){
    var start=g.adj[keys[k]],s;
    for(s=0;s<start.length;s++){
      var h0=start[s];
      if(seen[hid(h0)])continue;
      var loopPts=[],loopB=[],h=h0,guard=0,ok=true;
      while(guard++<20000){
        seen[hid(h)]=1;
        loopPts.push(bimHalfFrom(g,h));
        loopB.push(bimHalfBulge(g,h));
        var atKey=bimGraphNodeKey(bimHalfTo(g,h));
        var inDir=bimHalfArriveDir(g,h);
        var back=Math.atan2(-inDir[1],-inDir[0]);
        var cands=g.adj[atKey]||[],best=null,bestAng=Infinity,c;
        for(c=0;c<cands.length;c++){
          var cand=cands[c];
          if(cand.e===h.e&&cand.forward!==h.forward)continue;   /* the way we came */
          var od=bimHalfLeaveDir(g,cand);
          var ang=back-Math.atan2(od[1],od[0]);
          while(ang<=1e-12)ang+=Math.PI*2;
          while(ang>Math.PI*2)ang-=Math.PI*2;
          if(ang<bestAng){bestAng=ang;best=cand;}
        }
        if(!best){                       /* dead end: go back the way we came */
          for(c=0;c<cands.length;c++)
            if(cands[c].e===h.e&&cands[c].forward!==h.forward){best=cands[c];break;}
        }
        if(!best){ok=false;break;}
        h=best;
        if(hid(h)===hid(h0))break;
      }
      if(ok&&loopPts.length>=2)faces.push({pts:loopPts,bulges:loopB});
    }
  }
  return faces;
}

/* The face containing a point: counter-clockwise (so not the one outer face), containing it,
   smallest first -- the same selection bimFindEnclosingWallFace already makes. */
function bimFaceContaining(faces,pt){
  var best=null,i;
  for(i=0;i<faces.length;i++){
    var f=faces[i];
    var sa=bimBulgedSignedArea(f.pts,f.bulges,true);
    if(sa<=1e-9)continue;                        /* clockwise: that is the outer face */
    var flat=bimFlattenPoly(f.pts,f.bulges,true);
    if(flat.length<3)continue;
    if(!bimPointInPoly(pt,flat))continue;
    if(!best||sa<best.area)best={face:f,area:sa,flat:flat};
  }
  return best;
}
/* Anything of the arrangement strictly inside the traced loop is an island. A polyline cannot
   carry a hole, so this is reported rather than silently dropped from the area. */
function bimFaceHasIsland(g,hit){
  var keys=Object.keys(g.nodes),i,on={};
  for(i=0;i<hit.face.pts.length;i++)on[bimGraphNodeKey(hit.face.pts[i])]=1;
  for(i=0;i<keys.length;i++){
    if(on[keys[i]])continue;
    if(bimPointInPoly(g.nodes[keys[i]],hit.flat))return true;
  }
  return false;
}
function bimTraceBoundary(edges,pt){
  var arr=bimArrangeEdges(edges);
  if(arr.error)return {error:arr.error};
  if(!arr.edges.length)return {error:'There is no geometry here to trace a boundary from'};
  var g=bimBuildEdgeGraph(arr.edges);
  var faces=bimTraceEdgeFaces(g);
  var hit=bimFaceContaining(faces,pt);
  if(!hit)return {error:'That point is not inside a closed region'};
  return {pts:hit.face.pts,bulges:hit.face.bulges,area:hit.area,
          islands:bimFaceHasIsland(g,hit),edges:arr.edges.length,faces:faces.length};
}

/* ------------------------------------------------------------------ checks */
var n=0,bad=[];
function ck(c,m){n++;console.log((c?'  PASS  ':'  FAIL  ')+m);if(!c)bad.push(m);}
function near(a,b,t){return Math.abs(a-b)<=(t||1e-9);}
function seg(ax,az,bx,bz,bg){return {a:[ax,az],b:[bx,bz],bulge:bg||0};}
function ring(pts,bulges){
  var out=[],i,n2=pts.length;
  for(i=0;i<n2;i++)out.push({a:pts[i],b:pts[(i+1)%n2],bulge:bimBulgeAt(bulges,i)});
  return out;
}

console.log('-- the tangent, which is what the chord is not');
var semi={a:[2,0],b:[-2,0],bulge:1};
var d0=bimEdgeDirAt(semi,true),d1=bimEdgeDirAt(semi,false);
ck(near(d0[0],0)&&near(d0[1],1),
   'leaving (2,0) on a CCW semicircle heads +z, not along the chord -> ['+d0+']');
ck(near(d1[0],0)&&near(d1[1],-1),'and arrives at (-2,0) heading -z -> ['+d1+']');

console.log('\n-- splitting an edge keeps its pieces on the original circle');
var halves=bimSplitEdge(semi,[[0,2]]);
ck(halves.length===2,'a semicircle cut at its apex gives two pieces');
var h0=bimBulgeArc(halves[0].a,halves[0].b,halves[0].bulge);
ck(h0&&near(h0.radius,2,1e-9)&&near(h0.center[0],0,1e-9)&&near(h0.center[1],0,1e-9),
   'each on the SAME circle, centre and radius unmoved -> c=['+(h0?h0.center:'')+'] r='+(h0?h0.radius.toFixed(6):''));
ck(near(Math.abs(h0.sweep),Math.PI/2,1e-9),
   'and each sweeping a quarter turn -> '+(h0?(h0.sweep*180/Math.PI).toFixed(4):'')+' deg');

console.log('\n-- the case the existing tracer cannot do: lines that merely cross');
var grid=[seg(-5,0,5,0),seg(-5,1,5,1),seg(0,-5,0,5),seg(1,-5,1,5)];
var g0=bimBuildEdgeGraph(grid);
ck(Object.keys(g0.nodes).length===8,
   'unarranged, four crossing lines share NO node at any crossing -> '+
   Object.keys(g0.nodes).length+' nodes, all of them endpoints');
var r=bimTraceBoundary(grid,[0.5,0.5]);
ck(!r.error&&near(r.area,1,1e-9),
   'arranged, the point in the middle finds the unit square -> area '+
   (r.error||r.area.toFixed(9)));
ck(!r.error&&r.pts.length===4,'with four corners -> '+(r.error?'-':r.pts.length));
ck(!r.error&&!r.islands,'and no islands');
var open=bimTraceBoundary(grid,[3,0.5]);
ck(!!open.error,'a point in a region that is NOT closed is refused -> '+open.error);

console.log('\n-- a circle cut by a chord: both pieces, by exact area');
var circ=ring([[-2,0],[2,0]],[1,1]);
ck(near(bimBulgedArea([[-2,0],[2,0]],[1,1],true),Math.PI*4,1e-9),
   'the circle itself is pi*r^2 to start with');
var chord=[seg(-5,1,5,1)];
var withChord=circ.concat(chord);
/* chord at z=1 on r=2: half-angle acos(1/2)=pi/3, so the minor cap subtends 2pi/3 */
var theta=2*Math.PI/3;
var capArea=4/2*(theta-Math.sin(theta));
var minor=bimTraceBoundary(withChord,[0,1.5]);
ck(!minor.error&&near(minor.area,capArea,1e-7),
   'the minor segment is r^2/2*(theta-sin theta) -> '+
   (minor.error||minor.area.toFixed(9))+' vs '+capArea.toFixed(9));
var major=bimTraceBoundary(withChord,[0,-1]);
ck(!major.error&&near(major.area,Math.PI*4-capArea,1e-7),
   'and the major segment is the rest of the circle -> '+
   (major.error||major.area.toFixed(9))+' vs '+(Math.PI*4-capArea).toFixed(9));
ck(!minor.error&&bimHasBulge(minor.bulges),
   'the curved edge stayed CURVED in the result -> bulges '+
   (minor.error?'-':JSON.stringify(minor.bulges.map(function(b){return +b.toFixed(6);}))));
if(!minor.error){
  var chordOnly=bimBulgedArea(minor.pts,null,true);
  ck(Math.abs(chordOnly-minor.area)>0.2,
     'drop the bulge and the region has no area at all, which is what makes this exact -> '+
     chordOnly.toFixed(6)+' vs '+minor.area.toFixed(6));
}

console.log('\n-- a spur poking into the region: the walk must come back out of it');
/* The classic face-walk failure. A dead-end edge inside a face has to be traversed in and out
   again, and the loop that results visits it twice. The area must be unchanged, because the
   two traversals cancel in the shoelace -- if they do not, the walk took a wrong turn. */
var spur=[seg(-5,0,5,0),seg(-5,1,5,1),seg(0,-5,0,5),seg(1,-5,1,5),seg(0.5,0,0.5,0.4)];
var sp=bimTraceBoundary(spur,[0.8,0.8]);
ck(!sp.error&&near(sp.area,1,1e-9),
   'the unit square still measures 1 with a spur inside it -> '+(sp.error||sp.area.toFixed(9)));
ck(!sp.error&&sp.pts.length>4,
   'and the loop visits the spur rather than stepping over it -> '+
   (sp.error?'-':sp.pts.length)+' points');

console.log('\n-- islands are reported, not quietly left out of the area');
var outer=ring([[0,0],[10,0],[10,10],[0,10]]);
var inner=ring([[3,3],[7,3],[7,7],[3,7]]);
var withIsland=bimTraceBoundary(outer.concat(inner),[1,1]);
ck(!withIsland.error&&withIsland.islands===true,
   'a point between two nested squares reports an island -> '+
   (withIsland.error||withIsland.islands));
var noIsland=bimTraceBoundary(outer.concat(inner),[5,5]);
ck(!noIsland.error&&noIsland.islands===false&&near(noIsland.area,16,1e-9),
   'a point inside the inner square does not -> area '+
   (noIsland.error||noIsland.area.toFixed(6))+', islands '+(noIsland.error||noIsland.islands));

console.log('\n-- refusals');
ck(!!bimTraceBoundary([],[0,0]).error,'no geometry at all is refused');
ck(!!bimTraceBoundary([seg(0,0,5,0)],[1,1]).error,'a single line encloses nothing');
var big=[];for(var q=0;q<420;q++)big.push(seg(q,-1,q,1));
ck(!!bimTraceBoundary(big,[0,0]).error,
   'and too much geometry is refused rather than hung on -> '+bimTraceBoundary(big,[0,0]).error);

console.log('\n-- the signed area is the same magnitude the build already reports');
var sq=[[0,0],[4,0],[4,3],[0,3]];
ck(near(Math.abs(bimBulgedSignedArea(sq,null,true)),bimBulgedArea(sq,null,true),1e-12),
   'CCW square: |signed| equals bimBulgedArea -> '+bimBulgedSignedArea(sq,null,true).toFixed(6));
var sqCW=sq.slice().reverse();
ck(bimBulgedSignedArea(sqCW,null,true)<0&&
   near(Math.abs(bimBulgedSignedArea(sqCW,null,true)),bimBulgedArea(sqCW,null,true),1e-12),
   'reversed it goes negative while the magnitude is unchanged -> '+
   bimBulgedSignedArea(sqCW,null,true).toFixed(6));

console.log('\n'+(n-bad.length)+'/'+n+' checks passed');
console.log('RESULT: '+(bad.length?'FAIL':'PASS'));
