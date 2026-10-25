  /* ================= __acad3dV97: add a vertex to a sketch ================= */
  function bimSketchSegCount(o){
    if(!o||!o.pts||o.pts.length<2)return 0;
    return (o.closed!==false)?o.pts.length:o.pts.length-1;
  }
  /* The midpoint of one segment, measured along the CURVE -- on an arc that is the sweep
     midpoint, which is where the segment actually is. */
  function bimSketchSegMid(o,seg){
    if(!o||!o.pts||!(seg>=0&&seg<bimSketchSegCount(o))||Math.floor(seg)!==seg)return null;
    var n=o.pts.length,A=o.pts[seg],B=o.pts[(seg+1)%n];
    var arc=bimBulgeArc(A,B,bimBulgeAt(o.bulges,seg));
    if(arc)return bimArcPointAt(arc,0.5);
    return [(A[0]+B[0])/2,(A[1]+B[1])/2];
  }
  function bimInsertSketchVertex(o,seg,pt){
    if(!o||o.t!=='sketch'||bimIsPoint(o)||!o.pts)return {error:'Only a sketch takes an added vertex'};
    var segs=bimSketchSegCount(o);
    if(!(seg>=0&&seg<segs)||Math.floor(seg)!==seg)return {error:'There is no such segment'};
    if(!pt||!isFinite(pt[0])||!isFinite(pt[1]))return {error:'That is not a point to insert'};
    var n=o.pts.length,A=o.pts[seg],B=o.pts[(seg+1)%n];
    var b=bimBulgeAt(o.bulges,seg),b1=0,b2=0;
    if(Math.abs(b)>BIM_BULGE_EPS){
      /* Both halves on the SAME circle, so a curve stays a curve. */
      var arc=bimBulgeArc(A,B,b);
      if(arc){
        var sg=arc.sweep>=0?1:-1;
        b1=bimArcBulgeBetween(arc.center,A,pt,sg);
        b2=bimArcBulgeBetween(arc.center,pt,B,sg);
      }
    }
    o.pts.splice(seg+1,0,[pt[0],pt[1]]);
    if(bimHasBulge(o.bulges)||Math.abs(b1)>BIM_BULGE_EPS||Math.abs(b2)>BIM_BULGE_EPS){
      var nb=[],i;
      for(i=0;i<n;i++){
        if(i===seg){nb.push(b1,b2);}
        else nb.push(bimBulgeAt(o.bulges,i));
      }
      o.bulges=nb;
    }
    /* Constraint references are indices into o.pts. Every index past the insert moves up by
       one, or the constraint would silently start holding two different points together. */
    if(o.constraints&&o.constraints.length){
      var c,k;
      for(c=0;c<o.constraints.length;c++){
        var refs=o.constraints[c].refs||[];
        for(k=0;k<refs.length;k++)if(refs[k]>seg)refs[k]++;
      }
    }
    return {idx:seg+1};
  }
  function bimDragSketchPoint(o,idx,newXZ){
    if(!o||!o.pts||idx<0||idx>=o.pts.length)return false;
    o.pts[idx]=[newXZ[0],newXZ[1]];
    return true;
  }
  function bimDragWallPoint(o,idx,newXZ){
    if(!o||!o.bim||!o.bim.centerline||idx<0||idx>=o.bim.centerline.length)return false;
    var cl=o.bim.centerline.slice();
    cl[idx]=[newXZ[0],newXZ[1]];
    var res=bimBuildWallGeometry(cl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,o.bim.bulges);
    if(res.error)return false;
    o.mesh=res.mesh;
    o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123: a grip drag dropped the wall's type */
    return true;
  }
  function bimDrawGrips(ctx,V,W,H){
    A3D.grips=[];
    if(A3D.face)return;   /* __acad3dV123: a held face is worked by its arrow alone */
    var gs=bimSelectedGrid();   /* __acad3dV98: a selected grid's two ends */
    if(gs&&!A3D.section){
      var gy=bimGetActiveLevel().elev,gk,gsp;
      for(gk=0;gk<2;gk++){
        gsp=toScreen([(gk?gs.p2:gs.p1)[0],gy,(gk?gs.p2:gs.p1)[1]],V,W,H);
        A3D.grips.push({x:gsp[0],y:gsp[1],idx:gk,objId:gs.id,kind:'grid',elev:gy});
        ctx.save();
        ctx.fillStyle=(drag&&drag.grip&&drag.kind==='grid'&&drag.idx===gk)?'#ffd479':'#4ea1ff';
        ctx.strokeStyle='#0d1117';ctx.lineWidth=1.2;
        ctx.fillRect(gsp[0]-4,gsp[1]-4,8,8);ctx.strokeRect(gsp[0]-4,gsp[1]-4,8,8);
        ctx.restore();
      }
      return;
    }
    var o=objById(A3D.sel);
    if(bimIsLocked(o))return;
    var ep=bimGetEditablePoints(o);
    if(!ep)return;
    var i,pts=ep.pts;
    var cp=(A3D.conPick&&o.id===A3D.sel)?A3D.conPick:null;
    /* __acad3dV75: THE REPORTED BUG. Grips were projected from the object's LOCAL points, so
       after a move they stayed at the object's old screen position -- and since bimPickGrip
       matches on those same stale coordinates, the stranded squares were still the live drag
       handles. elev is recorded in WORLD terms because groundPoint() un-projects the cursor
       against a world plane. */
    var wElev=bimWorldElev(o,ep.y);
    for(i=0;i<pts.length;i++){
      var sp=toScreen(bimWorldPt(o,pts[i],ep.y),V,W,H);
      A3D.grips.push({x:sp[0],y:sp[1],idx:i,objId:o.id,kind:ep.kind,elev:wElev});
      ctx.save();
      var picked=cp&&cp.picked.indexOf(i)>=0;
      ctx.fillStyle=picked?'#7ee787':((drag&&drag.grip&&drag.idx===i)?'#ffd479':'#4ea1ff');
      ctx.strokeStyle='#0d1117';
      ctx.lineWidth=1.2;
      ctx.fillRect(sp[0]-4,sp[1]-4,8,8);
      ctx.strokeRect(sp[0]-4,sp[1]-4,8,8);
      ctx.restore();
    }
    /* __acad3dV97: a midpoint grip on every segment of a sketch -- drag it to add a vertex.
       Smaller and hollow, so it reads as "insert here" and never as a vertex. Pushed AFTER the
       vertex grips, and bimPickGrip prefers the nearest, so on a very short segment a vertex
       still wins a tie. */
    if(ep.kind==='sketch'&&!bimIsPoint(o)&&!(A3D.conPick&&o.id===A3D.sel)){
      var segs=bimSketchSegCount(o),s,mp,msp;
      for(s=0;s<segs;s++){
        mp=bimSketchSegMid(o,s);
        msp=toScreen(bimWorldPt(o,mp,ep.y),V,W,H);
        A3D.grips.push({x:msp[0],y:msp[1],seg:s,mid:true,objId:o.id,kind:'sketch',elev:wElev});
        ctx.save();
        ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.2;
        ctx.fillStyle='rgba(13,17,23,0.85)';
        ctx.fillRect(msp[0]-3,msp[1]-3,6,6);
        ctx.strokeRect(msp[0]-3,msp[1]-3,6,6);
        ctx.restore();
      }
    }
  }
