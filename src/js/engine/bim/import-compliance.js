  // ---- __acad3dV11: BIM import compliance -- object lock/pin, and recovering full parametric
  // wall data (centerline/thickness/align) from a simple rectangular imported profile so an
  // imported IFC wall becomes a genuine editable/hostable wall, not just an inert mesh. ----
  function bimTryRecoverWallFromRectProfile(profXZ,baseY,height){
    if(!profXZ||profXZ.length!==4)return null;
    var P=sketchCCW(profXZ.slice());
    var i,edges=[];
    for(i=0;i<4;i++){
      var a=P[i],b=P[(i+1)%4];
      var dx=b[0]-a[0],dz=b[1]-a[1];
      edges.push({a:a,b:b,len:Math.sqrt(dx*dx+dz*dz),dx:dx,dz:dz});
    }
    var e0=edges[0],e1=edges[1],e2=edges[2],e3=edges[3];
    function closeLen(x,y){return Math.abs(x-y)<Math.max(0.02,0.02*Math.max(x,y));}
    if(!closeLen(e0.len,e2.len)||!closeLen(e1.len,e3.len))return null;
    function perp(u,v){var cosA=(u.dx*v.dx+u.dz*v.dz)/((u.len*v.len)||1);return Math.abs(cosA)<0.06;}
    if(!perp(e0,e1)||!perp(e1,e2))return null;
    var longEdges,shortEdges;
    if(e0.len>=e1.len){longEdges=[e0,e2];shortEdges=[e1,e3];}
    else{longEdges=[e1,e3];shortEdges=[e0,e2];}
    var thickness=shortEdges[0].len;
    if(thickness<1e-4)return null;
    var c1=[(shortEdges[0].a[0]+shortEdges[0].b[0])/2,(shortEdges[0].a[1]+shortEdges[0].b[1])/2];
    var c2=[(shortEdges[1].a[0]+shortEdges[1].b[0])/2,(shortEdges[1].a[1]+shortEdges[1].b[1])/2];
    var runLen=Math.sqrt(Math.pow(c2[0]-c1[0],2)+Math.pow(c2[1]-c1[1],2));
    if(runLen<1e-3)return null;
    return {centerline:[c1,c2],thickness:thickness,align:'center',closed:false,baseY:baseY,height:height};
  }
  function bimIsLocked(o){return !!(o&&o.locked);}
  function bimSetLocked(o,val){
    if(!o)return false;
    pushUndo();
    o.locked=!!val;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+(val?' locked (Pin)':' unlocked'));
    return true;
  }
  /* __acad3dV89: the centerline may now carry bulges (the V88 storage), so a wall can curve.

     HOW: flatten the centerline FIRST, then run the existing clean / CCW / offset / miter /
     ribbon code over the flattened points. One ribbon builder, not a second curved one that
     could drift from it.

     WHAT IS STORED is the ORIGINAL pts and bulges, never the flattened copy. Storing the
     flattened version would re-tessellate an already tessellated centerline on every rebuild -
     a type change, an opening, a height edit - and the wall would coarsen a little each time it
     was touched, with no single moment where anything looked wrong.

     Flattening before sketchCCW also avoids a real trap: reversing a point list that carries
     bulges requires reversing AND NEGATING them, because reversing the vertex order reverses
     the sense of every arc. Flattened points carry no such baggage. */
  /* __acad3dV105b: the points a wall's body is actually built from -- flattened when it carries
     bulges, de-duplicated, and wound CCW when it closes. Lifted out of bimBuildWallGeometry so
     that the area plan can rebuild a wall's two faces from the SAME ring the solid was built
     from. Two copies of these lines would disagree the first time either one changed, and the
     disagreement would show up as a gross area that quietly misses a wall thickness. */
  function bimWallBasePts(pts,bulges,closed){
    if(!pts||pts.length<2)return {error:'Wall needs at least 2 distinct points'};
    var geomPts=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;
    var cleanPts=[geomPts[0]],i,prevp,curp;
    for(i=1;i<geomPts.length;i++){
      prevp=cleanPts[cleanPts.length-1];curp=geomPts[i];
      if(Math.abs(prevp[0]-curp[0])>1e-6||Math.abs(prevp[1]-curp[1])>1e-6)cleanPts.push(curp);
    }
    if(closed&&cleanPts.length>1){
      var firstp=cleanPts[0],lastp=cleanPts[cleanPts.length-1];
      if(Math.abs(firstp[0]-lastp[0])<1e-6&&Math.abs(firstp[1]-lastp[1])<1e-6)cleanPts.pop();
    }
    if(cleanPts.length<2)return {error:'Wall needs at least 2 distinct points'};
    return {pts:closed?sketchCCW(cleanPts):cleanPts};
  }
  /* Both faces of a wall's body, in WORLD plan coordinates. */
  function bimWallFaceRings(o){
    if(!o||o.t!=='solid'||!o.bim||o.bim.type!=='wall'||!o.bim.centerline)return null;
    var base=bimWallBasePts(o.bim.centerline,o.bim.bulges||null,!!o.bim.closed);
    if(base.error)return null;
    var off=bimAlignOffsets(o.bim.thickness,o.bim.align),q=bimObjOffset(o),ra,rb;
    try{
      ra=bimOffsetRing(base.pts,off.dLeft,!!o.bim.closed);
      rb=bimOffsetRing(base.pts,-off.dRight,!!o.bim.closed);
    }catch(eFR){console.warn('[BIM] Wall face rings failed: ',eFR);return null;}
    function world(r){var out=[],k;for(k=0;k<r.length;k++)out.push([r[k][0]+q[0],r[k][1]+q[2]]);return out;}
    return {a:world(ra),b:world(rb),closed:!!o.bim.closed,thickness:o.bim.thickness};
  }
  /* The far crossing of the ray p + t*n with a polyline, for t in [0, lim].

     This replaces a nearest-point-on-the-ring lookup, which answered the right number for a
     straight wall and had no defensible answer at all when the nearest part of the ring belonged
     to a different run of the same wall. A ray asks the question the caller actually has: how
     deep is this body in this direction. lim is the wall's own thickness, and it is what stops
     the ray reaching the FAR side of a closed wall and reporting the width of the building as a
     wall inset. */
  function bimRayPolyDepth(poly,closed,p,n,lim){
    if(!poly||poly.length<2)return null;
    var best=null,m=poly.length,segs=closed?m:m-1,i,a,b,ex,ez,wx,wz,D,t,u;
    for(i=0;i<segs;i++){
      a=poly[i];b=poly[(i+1)%m];
      ex=b[0]-a[0];ez=b[1]-a[1];
      D=ex*n[1]-n[0]*ez;
      if(Math.abs(D)<1e-12)continue;
      wx=a[0]-p[0];wz=a[1]-p[1];
      t=(ex*wz-wx*ez)/D;
      u=(n[0]*wz-wx*n[1])/D;
      if(u<-1e-9||u>1+1e-9)continue;
      if(t<-1e-9||t>lim)continue;
      if(best===null||t>best)best=t;
    }
    return best;
  }
  /* How deep a wall's body reaches from the point p in the direction n. Measured off the BUILT
     faces instead of assumed from 'align', so a left- or right-aligned wall insets by its whole
     thickness on the side its body is on and by nothing on the other -- and so that no sign
     convention is copied out of bimOffsetRing, where a later change to it would not be noticed. */
  function bimWallInsetAt(rings,p,n){
    if(!rings)return null;
    var lim=(rings.thickness>0?rings.thickness:0)+1e-6;
    var ta=bimRayPolyDepth(rings.a,rings.closed,p,n,lim);
    var tb=bimRayPolyDepth(rings.b,rings.closed,p,n,lim);
    if(ta===null)return tb;
    if(tb===null)return ta;
    return ta>tb?ta:tb;
  }
  function bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges){
    var off=bimAlignOffsets(thickness,align);
    var base=bimWallBasePts(pts,bulges,closed);
    if(base.error)return {error:base.error};
    var basePts=base.pts;
    var innerRing,outerRing,nm;
    try{
      innerRing=bimOffsetRing(basePts,off.dLeft,!!closed);
      outerRing=bimOffsetRing(basePts,-off.dRight,!!closed);
      nm=bimBuildWallRibbonMesh(outerRing,innerRing,y0,height,!!closed);
    }catch(eW){
      console.warn('[BIM] Wall solid build failed: ',eW);
      return {error:'Wall build failed: '+(eW&&eW.message?eW.message:eW)};
    }
    if(!nm||!nm.f||nm.f.length<4)return {error:'Wall produced an empty solid: check the centerline points'};
    var bim={type:'wall',thickness:thickness,height:height,align:align,baseY:y0,closed:!!closed,centerline:pts.slice()};
    if(bimHasBulge(bulges))bim.bulges=bulges.slice();   /* __acad3dV89 */
    if(closed){
      bim.innerLoop=innerRing;
      bim.outerLoop=outerRing;
    }
    return {mesh:nm,bim:bim};
  }
  /* __acad3dV123: WHAT A REBUILD OWNS. An element's record is its geometry and everything else about
     it -- its type, its level, whatever a later phase adds. A rebuild makes the geometry again; it
     must not decide what else survives. Before V123 every rebuild, copy and transform carried the
     fields its author remembered: Properties' Height, a grip drag, Join and Trim dropped a wall's
     type, every copy of a wall had none, copies of floors and columns had theirs re-guessed from
     their sizes, and a turned floor kept the outline it had before the turn. bimCarryBim copies every
     field of the old record the new one does not set -- except the geometry a wall build writes
     only sometimes (its arcs, its loops), which would outlive the shape it described. Declared
     here, beside the build that writes them. */
  var BIM_BUILT_OPTIONAL={wall:['bulges','innerLoop','outerLoop']};
  function bimCarryBim(from,to){
    if(!from||!to)return to;
    var skip=BIM_BUILT_OPTIONAL[to.type||from.type]||[],k,v;
    for(k in from){
      if(!from.hasOwnProperty(k)||to.hasOwnProperty(k)||skip.indexOf(k)>=0)continue;
      v=from[k];
      to[k]=(v&&typeof v==='object')?JSON.parse(JSON.stringify(v)):v;
    }
    return to;
  }
  function buildWallSolid(pts,y0,height,thickness,align,closed,bulges){
    var res=bimBuildWallGeometry(pts,y0,height,thickness,align,closed,bulges);
    if(res.error){a3dToast(res.error);paint();return null;}
    pushUndo();
    A3D.counts.wall=(A3D.counts.wall||0)+1;
    res.bim.levelId=A3D.activeLevel;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:'#c7bfae',pos:[0,0,0],mesh:res.mesh,bim:res.bim};
    bimEnsureTypes();
    o.bim.typeId=A3D.activeWallType;o.bim.typeCat='wall';
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
