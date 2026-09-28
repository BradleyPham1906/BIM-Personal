"""patch_phase98.py -- __acad3dV98: an edge remembers what drew it.

To make a room traced across several walls follow those walls, the trace has to be able to say
WHICH objects bound the region it found. Until now an arrangement edge was {a,b,bulge} and
nothing else, so the region came back as bare points with no record of where they came from.

Each edge now carries `src`, the id of the object it was collected from. It survives the
arrangement -- both pieces of a split edge keep it -- and the face walk collects the sources of
the edges it actually walked, so bimTraceBoundary returns srcIds alongside the points.

The collector's per-object test is also extracted as bimBoundaryMember, because the dependency
graph is about to need exactly the same predicate: "which objects on this plane could bound a
region". One predicate, so the graph cannot link a different set of walls than the tracer reads.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = 'ff32c72f0d0ca95f4899d0684e64b4fa0603094cfa78698c422102443b36bb48'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # --- the collector: one membership predicate, and src on every edge
    ("""  function bimPushRingEdges(out,pts,bulges,closed,ox,oz){
    var n=pts.length,segs=closed?n:n-1,i,a,b;
    for(i=0;i<segs;i++){
      a=pts[i];b=pts[(i+1)%n];
      out.push({a:[a[0]+ox,a[1]+oz],b:[b[0]+ox,b[1]+oz],bulge:bimBulgeAt(bulges,i)});
    }
  }
  function bimBoundaryEdges(y0,want){
    want=want||{walls:true,sketches:true,clines:true};
    var out=[],i,o,q,lyr,box=null,seg;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      q=bimObjOffset(o);
      if(want.sketches&&o.t==='sketch'&&!bimIsPoint(o)&&o.pts&&o.pts.length>=2&&
         Math.abs((o.y||0)+q[1]-y0)<BIM_SKETCH_PLANE_TOL){
        bimPushRingEdges(out,o.pts,o.bulges||null,o.closed!==false,q[0],q[2]);
      }else if(want.walls&&o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline&&
               o.bim.centerline.length>=2&&
               Math.abs((o.bim.baseY||0)+q[1]-y0)<=BIM_LEVEL_PLANE_TOL){
        bimPushRingEdges(out,o.bim.centerline,o.bim.bulges||null,!!o.bim.closed,q[0],q[2]);
      }else if(want.clines&&bimIsCline(o)&&
               Math.abs((o.y||0)+q[1]-y0)<BIM_SKETCH_PLANE_TOL){
        if(!box)box=bimDrawingExtent2D();
        seg=bimClineVisibleSeg(o,box);
        if(seg)out.push({a:[seg[0][0]+q[0],seg[0][1]+q[2]],
                         b:[seg[1][0]+q[0],seg[1][1]+q[2]],bulge:0});
      }
    }
    return out;
  }""",
     """  function bimPushRingEdges(out,pts,bulges,closed,ox,oz,src){
    var n=pts.length,segs=closed?n:n-1,i,a,b;
    for(i=0;i<segs;i++){
      a=pts[i];b=pts[(i+1)%n];
      out.push({a:[a[0]+ox,a[1]+oz],b:[b[0]+ox,b[1]+oz],bulge:bimBulgeAt(bulges,i),src:src||null});
    }
  }
  /* __acad3dV98: can this object bound a region on this plane? The collector and the dependency
     graph both ask this, so the graph links exactly the objects the tracer reads -- no more,
     which would re-trace needlessly, and no fewer, which would leave a room not following. */
  function bimBoundaryMember(o,y0,want){
    if(!o||!want)return null;
    var lyr=bimLayerOf(o);
    if(lyr&&lyr.visible===false)return null;
    var q=bimObjOffset(o);
    if(want.sketches&&o.t==='sketch'&&!bimIsPoint(o)&&o.pts&&o.pts.length>=2&&
       Math.abs((o.y||0)+q[1]-y0)<BIM_SKETCH_PLANE_TOL)return 'sketch';
    if(want.walls&&o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline&&
       o.bim.centerline.length>=2&&
       Math.abs((o.bim.baseY||0)+q[1]-y0)<=BIM_LEVEL_PLANE_TOL)return 'wall';
    if(want.clines&&bimIsCline(o)&&
       Math.abs((o.y||0)+q[1]-y0)<BIM_SKETCH_PLANE_TOL)return 'cline';
    return null;
  }
  function bimBoundaryEdges(y0,want){
    want=want||{walls:true,sketches:true,clines:true};
    var out=[],i,o,q,box=null,seg,kind;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      kind=bimBoundaryMember(o,y0,want);
      if(!kind)continue;
      q=bimObjOffset(o);
      if(kind==='sketch'){
        bimPushRingEdges(out,o.pts,o.bulges||null,o.closed!==false,q[0],q[2],o.id);
      }else if(kind==='wall'){
        bimPushRingEdges(out,o.bim.centerline,o.bim.bulges||null,!!o.bim.closed,q[0],q[2],o.id);
      }else{
        if(!box)box=bimDrawingExtent2D();
        seg=bimClineVisibleSeg(o,box);
        if(seg)out.push({a:[seg[0][0]+q[0],seg[0][1]+q[2]],
                         b:[seg[1][0]+q[0],seg[1][1]+q[2]],bulge:0,src:o.id});
      }
    }
    return out;
  }"""),

    # --- a split keeps the source on every piece
    ("""    for(k=0;k<kept.length;k++){
      out.push({a:prev,b:kept[k].p,
        bulge:arc?bimArcBulgeBetween(arc.center,prev,kept[k].p,sign):0});
      prev=kept[k].p;
    }
    out.push({a:prev,b:e.b,bulge:arc?bimArcBulgeBetween(arc.center,prev,e.b,sign):0});
    return out;""",
     """    for(k=0;k<kept.length;k++){
      out.push({a:prev,b:kept[k].p,
        bulge:arc?bimArcBulgeBetween(arc.center,prev,kept[k].p,sign):0,src:e.src||null});
      prev=kept[k].p;
    }
    out.push({a:prev,b:e.b,bulge:arc?bimArcBulgeBetween(arc.center,prev,e.b,sign):0,
              src:e.src||null});   /* __acad3dV98: both pieces remember what drew them */
    return out;"""),

    # --- the walk records which sources it walked
    ("""        var loopPts=[],loopB=[],h=h0,guard=0,ok=true;
        while(guard++<20000){
          seen[hid(h)]=1;
          loopPts.push(bimHalfFrom(g,h));
          loopB.push(bimHalfBulge(g,h));""",
     """        var loopPts=[],loopB=[],loopS={},h=h0,guard=0,ok=true;
        while(guard++<20000){
          seen[hid(h)]=1;
          loopPts.push(bimHalfFrom(g,h));
          loopB.push(bimHalfBulge(g,h));
          if(g.edges[h.e].src)loopS[g.edges[h.e].src]=1;   /* __acad3dV98 */"""),
    ("""        if(ok&&loopPts.length>=2)faces.push({pts:loopPts,bulges:loopB});""",
     """        if(ok&&loopPts.length>=2)faces.push({pts:loopPts,bulges:loopB,srcIds:Object.keys(loopS)});"""),

    # --- and the trace hands them back
    ("""    return {pts:hit.face.pts,bulges:hit.face.bulges,area:hit.area,
            islands:bimFaceHasIsland(g,hit),edges:arr.edges.length,faces:faces.length};""",
     """    return {pts:hit.face.pts,bulges:hit.face.bulges,area:hit.area,
            islands:bimFaceHasIsland(g,hit),edges:arr.edges.length,faces:faces.length,
            srcIds:hit.face.srcIds||[]};   /* __acad3dV98: which objects bound it */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
