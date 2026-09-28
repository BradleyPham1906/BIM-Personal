"""patch_phase95b.py -- __acad3dV95: one collector, and the V22 tracer replaced by the V95 one.

The old path is DELETED rather than left beside the new one. bimCollectWallSegments,
bimBuildWallGraph and bimTraceFaces go; bimFindEnclosingWallFace now runs on the arrangement.
Two tracers would be two answers to "what encloses this point", and law 1 is explicit about
what a superseded thing that still runs costs.

Room, Floor and Ceiling inherit three fixes for free, because they all reach the tracer through
bimFindRoomBoundaryAt:

  - CROSSINGS WORK. Walls that cross mid-span without sharing a vertex now produce a node.
  - CURVES WORK. bimCollectWallSegments read o.bim.centerline raw and ignored o.bim.bulges, so
    a curved wall traced as its chord and the room it bounded had the wrong area.
  - A MOVED WALL TRACES WHERE IT IS. It never applied bimObjOffset, so a wall that had been
    moved went on bounding rooms at the position it used to occupy. That is the V75 bug, in a
    place the V75 fix did not reach.

The collector takes a source filter rather than gathering everything always: BOUNDARY wants
sketches and construction lines as well, while bimFindEnclosingWallFace means walls and must
keep meaning walls.

The two elevation tolerances are different on purpose and are named rather than inline. A
sketch's y IS the plane it was drawn on, so it matches tightly. A wall's baseY is a base
elevation that legitimately sits a floor thickness below the level datum, so it matches loosely.
They were 0.05 and 0.5 as bare literals in four places before this.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '9288d6b646f020b2700ac46e73eed924722d841d736d3cc4cc2d80bbc6f2f9e7'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

head = txt.index("  function bimCollectWallSegments(y0){")
tail = txt.index("  function bimFindEnclosingWallFace(pt,y0){")
assert head < tail, 'unexpected order'
old_block = txt[head:tail]
assert 'bimBuildWallGraph' in old_block and 'bimTraceFaces' in old_block, 'wrong span'
assert txt.count("  function bimCollectWallSegments(y0){") == 1
assert txt.count("  function bimFindEnclosingWallFace(pt,y0){") == 1

NEW_COLLECTOR = """  /* __acad3dV95: what curves are on this plan, as arrangement edges.

     One gather for every consumer. `want` selects the sources, because BOUNDARY means every
     curve while bimFindEnclosingWallFace means walls and has to keep meaning walls.

     Every source has bimObjOffset applied. The collector this replaces did not, so a wall that
     had been moved went on bounding rooms where it used to be. */
  var BIM_SKETCH_PLANE_TOL=0.05;   /* a sketch's y IS its plane, so it matches tightly */
  var BIM_LEVEL_PLANE_TOL=0.5;     /* a wall's baseY may sit a floor thickness below the datum */
  function bimPushRingEdges(out,pts,bulges,closed,ox,oz){
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
  }
"""

txt = txt[:head] + NEW_COLLECTOR + txt[tail:]

OLD_FIND = """  function bimFindEnclosingWallFace(pt,y0){
    var segments=bimCollectWallSegments(y0);
    if(segments.length<3)return null;
    var faces,graph;
    try{
      graph=bimBuildWallGraph(segments);
      faces=bimTraceFaces(graph);
    }catch(eF){
      console.warn('[BIM] Multi-wall boundary tracing failed: ',eF);
      return null;
    }
    var candidates=[],i;
    for(i=0;i<faces.length;i++){
      var f=faces[i];
      if(f.length<3)continue;
      var area=bimPolyArea(f);
      if(area<1e-6)continue;
      if(bimPolySignedArea(f)<0)continue;
      if(bimPointInPoly(pt,f))candidates.push({pts:f,area:area});
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return a.area-b.area;});
    return candidates[0];
  }"""
NEW_FIND = """  /* __acad3dV95: runs on the arrangement now. pts stays FLATTENED, because Room, Floor and
     Ceiling all read it as a plain ring and a two-vertex circle would break every one of them;
     the curve data rides alongside for callers that want it. */
  function bimFindEnclosingWallFace(pt,y0){
    var edges=bimBoundaryEdges(y0,{walls:true});
    if(edges.length<3)return null;
    var res;
    try{
      res=bimTraceBoundary(edges,pt);
    }catch(eF){
      console.warn('[BIM] Multi-wall boundary tracing failed: ',eF);
      return null;
    }
    if(!res||res.error)return null;
    if(res.area<1e-6)return null;
    var flat=bimFlattenPoly(res.pts,res.bulges,true);
    if(flat.length<3)return null;
    return {pts:flat,area:res.area,rawPts:res.pts,bulges:res.bulges,islands:!!res.islands};
  }"""
assert txt.count(OLD_FIND) == 1, 'find anchor count %d' % txt.count(OLD_FIND)
txt = txt.replace(OLD_FIND, NEW_FIND, 1)

for gone in ('bimCollectWallSegments', 'bimBuildWallGraph', 'bimTraceFaces'):
    assert gone not in txt, 'leftover reference to %s' % gone

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
