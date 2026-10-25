  // ---- __acad3dV32: Offset and Align for BIM objects, against BIM geometry.
  // SIGN CONVENTION for Offset: for a CCW-wound closed ring the segment normals point inward,
  // so a POSITIVE distance offsets inward (shrinks) and a negative one outward. The dialog spells
  // this out rather than leaving the user to discover it.
  function bimOffsetPoints(pts,dist,closed){
    if(!pts||pts.length<2)return null;
    if(Math.abs(dist)<1e-9)return null;
    return bimOffsetRing(pts,dist,!!closed);
  }
  function bimObjBounds2D(o){
    var pts=null,i;
    if(o.bim&&o.bim.type==='wall'&&o.bim.centerline)pts=o.bim.centerline;
    else if(o.bim&&o.bim.profile)pts=o.bim.profile;
    else if(o.bim&&o.bim.footprint)pts=o.bim.footprint;
    else if(bimIsHatch(o))pts=bimHatchOutline(o);    /* __acad3dV96 */
    else if(bimIsCline(o))pts=[o.p];                 /* __acad3dV94: the root, the one
       definite point on a line that has no ends. Without it Align silently did nothing to a
       construction line, and the extent guard that keeps one out of its own drawing extent was
       unreachable. */
    else if(o.t==='sketch')pts=bimSketchOutline(o);   /* __acad3dV93 */
    else if(o.t==='room')pts=o.pts;
    else if(o.bim&&o.bim.center)pts=[o.bim.center];
    else if(o.t==='text'||o.t==='roomtag')pts=[o.pt];   /* __acad3dV101 */
    else if(bimIsAlignment(o))pts=bimAlignExtentPts(o);   /* __acad3dV127 */
    else if(bimIsProperty(o)){   /* __acad3dV103: world points, so the offset below is taken off */
      var pq=bimObjOffset(o);
      pts=bimPropertyGeometry(o).ring.map(function(p){return [p[0]-pq[0],p[1]-pq[2]];});
    }
    if(pts&&pts.length){
      var ox=(o.pos&&o.pos[0])||0,oz=(o.pos&&o.pos[2])||0;
      var mnx=Infinity,mxx=-Infinity,mnz=Infinity,mxz=-Infinity;
      for(i=0;i<pts.length;i++){
        var x=pts[i][0]+ox,z=pts[i][1]+oz;
        if(x<mnx)mnx=x;if(x>mxx)mxx=x;if(z<mnz)mnz=z;if(z>mxz)mxz=z;
      }
      return {minX:mnx,maxX:mxx,minZ:mnz,maxZ:mxz};
    }
    var m=meshOf(o);
    if(m&&m.v&&m.v.length){
      var ox2=(o.pos&&o.pos[0])||0,oz2=(o.pos&&o.pos[2])||0;
      var a=Infinity,b=-Infinity,c=Infinity,d=-Infinity;
      for(i=0;i<m.v.length;i++){
        var vx=m.v[i][0]+ox2,vz=m.v[i][2]+oz2;
        if(vx<a)a=vx;if(vx>b)b=vx;if(vz<c)c=vz;if(vz>d)d=vz;
      }
      return {minX:a,maxX:b,minZ:c,maxZ:d};
    }
    return null;
  }
  function bimOffsetObject(o,dist){
    if(o.bim&&o.bim.type==='wall'){
      if(!o.bim.centerline)return {error:'Imported wall has no editable centerline'};
      /* __acad3dV90: a curved wall offsets to CONCENTRIC arcs. The V89 refusal that stood here
         was waiting for exactly this and is gone rather than bypassed. */
      var ncl,nbulge=null;
      if(bimHasBulge(o.bim.bulges)){
        var ob=bimOffsetBulged(o.bim.centerline,o.bim.bulges,o.bim.closed,dist);
        if(ob.error)return {error:'Offset: '+ob.error};
        ncl=ob.pts;nbulge=ob.bulges;
      }else{
        ncl=bimOffsetPoints(o.bim.centerline,dist,o.bim.closed);
      }
      if(!ncl)return {error:'Offset distance cannot be zero'};
      var res=bimBuildWallGeometry(ncl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,nbulge);
      if(res.error)return {error:res.error};
      A3D.counts.wall=(A3D.counts.wall||0)+1;
      res.bim.levelId=o.bim.levelId;
      return {obj:{id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,
        col:o.col,pos:[0,0,0],mesh:res.mesh,bim:res.bim,layer:o.layer}};
    }
    if(bimIsPoint(o))return {error:'Offset: a point has no side to offset to'};   /* __acad3dV93 */
    if(o.t==='sketch'){
      /* __acad3dV90: same treatment for a sketch that carries arcs. */
      var npts,nb=null;
      if(bimHasBulge(o.bulges)){
        var sb=bimOffsetBulged(o.pts,o.bulges,o.closed!==false,dist);
        if(sb.error)return {error:'Offset: '+sb.error};
        npts=sb.pts;nb=sb.bulges;
      }else{
        npts=bimOffsetPoints(o.pts,dist,o.closed!==false);
      }
      if(!npts)return {error:'Offset distance cannot be zero'};
      var so={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'sketch',name:(o.name||'Sketch')+' offset',
        col:o.col,pos:[0,0,0],pts:npts,y:o.y,closed:o.closed,layer:o.layer};
      if(bimHasBulge(nb))so.bulges=nb.slice();
      return {obj:so};
    }
    return {error:'Offset works on walls and sketches (selected object is a '+(o.t||'?')+')'};
  }
  // ---- __acad3dV33: Trim for BIM walls. AutoCAD semantics: pick the cutting wall, then click
  // the portion of another wall to remove. Distinct from Join Walls, which pulls two free ENDS
  // together at a corner -- Trim cuts a wall that already CROSSES another and discards the
  // clicked side. Requires the intersection to land inside both segments, so a cutter that
  // merely points at the wall without reaching it is refused rather than extending anything.
