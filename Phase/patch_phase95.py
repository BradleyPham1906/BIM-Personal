"""patch_phase95.py -- __acad3dV95 geometry core: the planar arrangement.

One concern: the maths. No entity, no tool, no rendering.

THE FACE WALK ALREADY EXISTS. bimTraceFaces (V22) walks a planar graph taking the smallest
clockwise turn at every node and it is correct. What has never existed is the ARRANGEMENT in
front of it: edges go into that graph exactly as drawn, so two lines that cross mid-span
without sharing a vertex produce no node at the crossing, and the region they bound is
invisible. That is why room tracing has only ever worked on walls meeting end to end.

Three things this adds, and each is a thing the old path gets wrong rather than merely lacks:

  bimArrangeEdges     every edge cut at every crossing with every other edge, arcs included.
                      An arc's pieces get their bulges recomputed about the SAME centre, so
                      they lie on the original circle instead of approximating it.

  bimEdgeDirAt        the angular key taken from the TANGENT. The V22 walk sorts by the chord,
                      which on a curved edge points somewhere the curve does not go, so the
                      turn it picks at a node where an arc meets a line can be the wrong one.

  bimBulgedSignedArea the sign is what separates the single outer face (clockwise) from the
                      inner ones. bimBulgedArea returned only the magnitude, so it now derives
                      from this rather than being a second copy of the same formula.

Islands are reported rather than dropped. A polyline cannot carry a hole, so a face with
something inside it has an area the polyline would misstate, and saying so beats being quietly
wrong by the area of the island.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'af6fe9c580d66a7537c85bae2721907a24a9e6bbd57a57e924c21e6d3ba85121'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

# --- 1. bimBulgedArea derives from a signed version rather than repeating the formula
OLD_AREA = """  function bimBulgedArea(pts,bulges,closed){
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
  }"""
NEW_AREA = """  /* __acad3dV95: the SIGN is what tells the one outer face of an arrangement from the inner
     ones, and the magnitude is what every schedule wants. One formula, two callers, so they
     cannot drift. */
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
  function bimBulgedArea(pts,bulges,closed){
    return Math.abs(bimBulgedSignedArea(pts,bulges,closed));
  }"""
assert txt.count(OLD_AREA) == 1, 'area anchor count %d' % txt.count(OLD_AREA)
txt = txt.replace(OLD_AREA, NEW_AREA, 1)

# --- 2. the arrangement and the arc-aware walk, after the V94 block
ANCHOR = """  /* ================= __acad3dV93: walking a distance along a curve ===================="""
NEW = """  /* ================= __acad3dV95: the planar arrangement =================

     An edge is {a,b,bulge}: one straight segment or one arc. Everything below works on those,
     so a wall, a sketch and a construction line are the same thing once collected. */
  var BIM_ARRANGE_LIMIT=400;
  /* The direction of travel at either end of an edge. On an arc this is the TANGENT, and it is
     the reason the V22 walk could not simply be reused: sorting turns by the chord picks the
     wrong edge wherever an arc meets a line at a node. */
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
    var dx=e.b[0]-e.a[0],dz=e.b[1]-e.a[1],dd=dx*dx+dz*dz;
    if(dd<1e-18)return null;
    return ((p[0]-e.a[0])*dx+(p[1]-e.a[1])*dz)/dd;
  }
  /* One edge cut at a list of points. An arc's pieces are rebuilt about the SAME centre, so
     they sit on the original circle rather than approximating it. */
  function bimSplitEdge(e,cuts){
    var arc=bimBulgeArc(e.a,e.b,e.bulge);
    var items=[],i,t,k;
    for(i=0;i<cuts.length;i++){
      t=bimEdgeParamAt(e,cuts[i]);
      if(t===null||!isFinite(t))continue;
      if(t<=1e-9||t>=1-1e-9)continue;      /* an endpoint is already a node */
      items.push({t:t,p:[cuts[i][0],cuts[i][1]]});
    }
    if(!items.length)return [e];
    items.sort(function(x,y){return x.t-y.t;});
    var kept=[];
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
  function bimArrangeEdges(edges,limit){
    limit=limit||BIM_ARRANGE_LIMIT;
    if(!edges||!edges.length)return {edges:[]};
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
      for(k=0;k<pieces.length;k++)if(bimEdgeLen(pieces[k])>1e-7)out.push(pieces[k]);
    }
    return {edges:out};
  }
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
  function bimHalfFrom(g,h){var e=g.edges[h.e];return h.forward?e.a:e.b;}
  function bimHalfTo(g,h){var e=g.edges[h.e];return h.forward?e.b:e.a;}
  function bimHalfBulge(g,h){var e=g.edges[h.e];return h.forward?e.bulge:-e.bulge;}
  function bimHalfArriveDir(g,h){
    var e=g.edges[h.e],d;
    if(h.forward)return bimEdgeDirAt(e,false);
    d=bimEdgeDirAt(e,true);return [-d[0],-d[1]];
  }
  function bimHalfLeaveDir(g,h){
    var e=g.edges[h.e],d;
    if(h.forward)return bimEdgeDirAt(e,true);
    d=bimEdgeDirAt(e,false);return [-d[0],-d[1]];
  }
  /* Every face of the arrangement, each traced once. Same rule as the V22 walk -- the smallest
     positive clockwise turn from the reversed arrival direction -- with the angles taken from
     tangents. A dead-end edge is traversed in and back out, and the two traversals cancel in
     the shoelace, so a spur inside a region does not change its area. */
  function bimTraceEdgeFaces(g){
    var faces=[],seen={},k,keys=Object.keys(g.adj);
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
          var cands=g.adj[atKey]||[],best=null,bestAng=Infinity,c,cand,od,ang;
          for(c=0;c<cands.length;c++){
            cand=cands[c];
            if(cand.e===h.e&&cand.forward!==h.forward)continue;   /* the way we came */
            od=bimHalfLeaveDir(g,cand);
            ang=back-Math.atan2(od[1],od[0]);
            while(ang<=1e-12)ang+=Math.PI*2;
            while(ang>Math.PI*2)ang-=Math.PI*2;
            if(ang<bestAng){bestAng=ang;best=cand;}
          }
          if(!best){        /* a dead end: the only way on is back the way we came */
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
  /* Counter-clockwise (so never the single outer face), containing the point, smallest first --
     the same selection bimFindEnclosingWallFace has always made. */
  function bimFaceContaining(faces,pt){
    var best=null,i,f,sa,flat;
    for(i=0;i<faces.length;i++){
      f=faces[i];
      sa=bimBulgedSignedArea(f.pts,f.bulges,true);
      if(sa<=1e-9)continue;
      flat=bimFlattenPoly(f.pts,f.bulges,true);
      if(flat.length<3)continue;
      if(!bimPointInPoly(pt,flat))continue;
      if(!best||sa<best.area)best={face:f,area:sa,flat:flat};
    }
    return best;
  }
  /* Anything of the arrangement strictly inside the traced loop is an island. A polyline cannot
     carry a hole, so this is SAID rather than left out of the area in silence. */
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
    var g,faces;
    try{
      g=bimBuildEdgeGraph(arr.edges);
      faces=bimTraceEdgeFaces(g);
    }catch(eT){
      console.warn('[BIM] Boundary tracing failed',eT);
      return {error:'That boundary could not be traced'};
    }
    var hit=bimFaceContaining(faces,pt);
    if(!hit)return {error:'That point is not inside a closed region'};
    return {pts:hit.face.pts,bulges:hit.face.bulges,area:hit.area,
            islands:bimFaceHasIsland(g,hit),edges:arr.edges.length,faces:faces.length};
  }
""" + ANCHOR

assert txt.count(ANCHOR) == 1, 'anchor count %d' % txt.count(ANCHOR)
txt = txt.replace(ANCHOR, NEW, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
