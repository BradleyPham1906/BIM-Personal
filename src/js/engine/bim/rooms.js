  // ---- __acad3dV10: Room/Space tool. Click inside an enclosed wall loop or closed sketch; the tool
  // auto-detects the boundary (smallest enclosing region, so a closet nested inside a larger room picks
  // correctly) and creates a Room object with a live area tag. Snapshot at creation time, like Floor --
  // does not stay live-linked if the source wall is edited afterward. ----
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
  // ---- __acad3dV22: multi-wall-loop boundary detection. The original detection only matched a
  // SINGLE closed wall object's innerLoop (or a closed sketch), so a room enclosed by several
  // separate wall segments meeting at corners -- the normal way people actually draw plans --
  // was never detected. This adds planar-graph face tracing as a fallback: collect every visible
  // wall's centerline segments at this elevation, weld coincident endpoints into a graph, then
  // walk directed half-edges always taking the most-clockwise turn, which enumerates every face
  // of the arrangement exactly once. Interior faces trace CCW (positive signed area); the
  // arrangement's outer boundary traces CW, so skipping negative-area faces avoids matching the
  // infinite exterior region (which technically contains every click point). ----
  var BIM_NODE_TOL=4;
  function bimGraphNodeKey(p){return p[0].toFixed(BIM_NODE_TOL)+','+p[1].toFixed(BIM_NODE_TOL);}
  function bimPolySignedArea(poly){
    var a=0,i,n=poly.length;
    for(i=0;i<n;i++){var j=(i+1)%n;a+=poly[i][0]*poly[j][1]-poly[j][0]*poly[i][1];}
    return a/2;
  }
  /* __acad3dV95: what curves are on this plan, as arrangement edges.

     One gather for every consumer. `want` selects the sources, because BOUNDARY means every
     curve while bimFindEnclosingWallFace means walls and has to keep meaning walls.

     Every source has bimObjOffset applied. The collector this replaces did not, so a wall that
     had been moved went on bounding rooms where it used to be. */
  var BIM_SKETCH_PLANE_TOL=0.05;   /* a sketch's y IS its plane, so it matches tightly */
  var BIM_LEVEL_PLANE_TOL=0.5;     /* a wall's baseY may sit a floor thickness below the datum */
  function bimPushRingEdges(out,pts,bulges,closed,ox,oz,src){
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
    if(!bimLayerShown(o))return null;   /* __acad3dV121 */
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
  }
  /* __acad3dV95: runs on the arrangement now. pts stays FLATTENED, because Room, Floor and
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
  }
  function bimFindRoomBoundaryAt(pt,y0){
    var candidates=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      /* __acad3dV97: through the source contract, in WORLD coordinates. This tested the click
         against a moved sketch's or wall's LOCAL points, so a sketch that had been moved could
         not be picked where it was drawn. */
      var isWall=(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.closed&&o.bim.innerLoop&&o.bim.innerLoop.length>=3);
      var isSk=(o.t==='sketch'&&!bimIsPoint(o)&&o.closed!==false&&o.pts&&o.pts.length>=2);
      if(!isWall&&!isSk)continue;
      var sb=bimSourceBoundaryWorld(o);
      if(sb.error)continue;
      if(Math.abs(sb.y-y0)>0.5)continue;
      if(!bimPointInPoly(pt,sb.ring))continue;
      if(isWall)candidates.push({pts:sb.ring.slice(),y:sb.y,sourceType:'wall',sourceId:o.id,wallHeight:o.bim.height});
      else candidates.push({pts:sb.ring.slice(),y:sb.y,sourceType:'sketch',sourceId:o.id});
    }
    if(candidates.length)candidates.sort(function(a,b){return bimPolyArea(a.pts)-bimPolyArea(b.pts);});
    /* __acad3dV99: the region under the click, from EVERY shape on the plan. A single closed
       source still wins when the region is that shape and nothing else -- it then follows that
       one object exactly as it did in V97 (a closed wall keeps its inner face). */
    var reg;
    try{reg=bimRegionTraceAt(pt,y0,BIM_REGION_WANT.all);}
    catch(eRg){console.warn('[BIM] Region trace for a room failed',eRg);reg={error:'trace failed'};}
    if(candidates.length&&(reg.error||(reg.srcIds.length===1&&reg.srcIds[0]===candidates[0].sourceId)))
      return candidates[0];
    if(!reg.error){
      var wh=0,j,wo,allW=reg.srcIds.length>0;
      for(j=0;j<reg.srcIds.length;j++){
        wo=objById(reg.srcIds[j]);
        if(wo&&wo.t==='solid'&&wo.bim&&wo.bim.type==='wall'){if(!wh&&wo.bim.height)wh=wo.bim.height;}
        else allW=false;
      }
      return {pts:reg.ring,y:y0,sourceType:allW?'wallgroup':'region',sourceId:null,wallHeight:wh,
              roomPts:bimRoomFaceRing(reg),   /* __acad3dV105b: what a ROOM measures here */
              rawPts:reg.pts,bulges:reg.bulges,islands:reg.islands,
              region:{seed:[pt[0],pt[1]],y:y0,want:'all',members:reg.srcIds.slice(),sig:reg.sig,open:false}};
    }
    if(candidates.length)return candidates[0];
    return null;
  }
