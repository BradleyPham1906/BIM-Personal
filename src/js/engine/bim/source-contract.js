  /* ================= __acad3dV97: the source contract =================

     The ONE reader of a boundary source. Everything built on a sketch or a closed wall -- room,
     floor, ceiling, roof, hatch -- gets its boundary from here, at creation and on every change
     after, so the two can no longer disagree about which points, which curve, or which frame.

     Returned in WORLD coordinates. A dependent converts into its own frame by subtracting its
     own offset (bimToFrame), which is the step whose absence doubled a moved room's offset. */
  function bimSourceBoundaryWorld(src){
    if(!src)return {error:'its source no longer exists'};
    var q=bimObjOffset(src),ring,pts,bulges=null,y;
    if(src.t==='sketch'&&!bimIsPoint(src)){
      if(src.closed===false)return {error:'its source sketch is no longer closed'};
      ring=bimSketchOutline(src);
      if(!ring||ring.length<3)return {error:'its source sketch has too few points'};
      pts=src.pts;bulges=bimHasBulge(src.bulges)?src.bulges.slice():null;
      y=(src.y||0)+q[1];
    }else if(src.t==='solid'&&src.bim&&src.bim.type==='wall'){
      if(!src.bim.closed||!src.bim.innerLoop||src.bim.innerLoop.length<3)
        return {error:'its source wall is no longer a closed loop'};
      ring=src.bim.innerLoop;pts=ring;
      y=(src.bim.baseY||0)+q[1];
    }else if(src.t==='room'&&src.pts&&src.pts.length>=3){
      /* a room is itself a boundary, so a hatch can be built on one and follow it -- a chain the
         graph orders correctly because a room is always visited before what depends on it */
      ring=src.pts;pts=ring;
      y=(src.y||0)+q[1];
    }else{
      return {error:'its source is not a closed boundary'};
    }
    function w(p){return [p[0]+q[0],p[1]+q[2]];}
    var outRing=ring.map(w);
    if(!(bimPolyArea(outRing)>1e-6))return {error:'its source boundary has no area'};
    return {ring:outRing,pts:pts.map(w),bulges:bulges,y:y,
            type:(src.t==='solid'?'wall':src.t),id:src.id};
  }
  /* __acad3dV99: what an object follows, in words, for Properties. One answer for every kind. */
  function bimFollowsText(o){
    if(!o)return '-';
    if(bimIsRegionDep(o)){
      var names=[],i,m,mem=o.region.members||[];
      for(i=0;i<mem.length;i++){m=objById(mem[i]);names.push(m?m.name:'(missing)');}
      return 'The region bounded by '+(names.length?names.join(', '):'nothing')+
        (o.region.open?' - NOT ENCLOSED, keeping its last shape':'');
    }
    var sid=bimGraphRoomSourceId(o);
    if(sid)return ((objById(sid)||{}).name)||'(missing)';
    return 'Nothing - it keeps its own shape';
  }
  /* World points into a dependent's own frame. */
  function bimToFrame(o,pts){
    var q=bimObjOffset(o);
    return pts.map(function(p){return [p[0]-q[0],p[1]-q[2]];});
  }
