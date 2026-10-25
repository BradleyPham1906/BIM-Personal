  // ---- __acad3dV7: Selection tools (marquee select, group move/delete, duplicate, linear array) ----
  function bimRectContains(rx1,ry1,rx2,ry2,px,py){
    var minx=Math.min(rx1,rx2),maxx=Math.max(rx1,rx2),miny=Math.min(ry1,ry2),maxy=Math.max(ry1,ry2);
    return px>=minx&&px<=maxx&&py>=miny&&py<=maxy;
  }
  function bimMarqueeTest(pts,rx1,ry1,rx2,ry2,crossing){
    if(!pts.length)return false;
    var i,allIn=true,anyIn=false;
    for(i=0;i<pts.length;i++){
      var c=bimRectContains(rx1,ry1,rx2,ry2,pts[i][0],pts[i][1]);
      if(c)anyIn=true;else allIn=false;
    }
    return crossing?anyIn:allIn;
  }
  function bimObjScreenPoints(o,V,W,H){
    /* __acad3dV75: the sketch branch dropped o.pos, so a moved sketch was marquee-selectable
       only at the rectangle it used to occupy. Rooms hit the mesh branch, have no mesh, and
       returned [] -- and bimMarqueeTest([]) is false for every rectangle, so a room could never
       be marquee-selected at all. Both are plan-point objects; both go through bimWorldPt. */
    if(o.t==='sketch'||(o.t==='room'&&o.pts))
      return o.pts.map(function(p){return toScreen(bimWorldPt(o,p,o.y),V,W,H);});
    var m=meshOf(o);
    if(!m)return [];
    return m.v.map(function(v){return toScreen([v[0]+o.pos[0],v[1]+o.pos[1],v[2]+o.pos[2]],V,W,H);});
  }
  function bimApplyMarquee(x1,y1,x2,y2){
    var crossing=x1>x2;
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var matched=[],i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(o.t==='opening')continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      var pts=bimObjScreenPoints(o,V,W,H);
      if(bimMarqueeTest(pts,x1,y1,x2,y2,crossing))matched.push(o.id);
    }
    return matched;
  }
  function drawMarqueeRect(ctx){
    if(!drag||!drag.marquee||!drag.moved)return;
    var x1=drag.x0,y1=drag.y0,x2=drag.x,y2=drag.y;
    var crossing=x1>x2;
    ctx.save();
    ctx.strokeStyle=crossing?'#5ec98a':'#4ea1ff';
    ctx.fillStyle=crossing?'rgba(94,201,138,0.10)':'rgba(78,161,255,0.10)';
    ctx.lineWidth=1.2;
    ctx.setLineDash(crossing?[4,3]:[]);
    var rx=Math.min(x1,x2),ry=Math.min(y1,y2),rw=Math.abs(x2-x1),rh=Math.abs(y2-y1);
    ctx.fillRect(rx,ry,rw,rh);
    ctx.strokeRect(rx,ry,rw,rh);
    ctx.restore();
  }
  function delSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length&&bimSelectedGrid())return bimRemoveGrid(A3D.selGrid);   /* __acad3dV98 */
    if(!ids.length){a3dToast('Nothing selected to delete');return false;}
    var lockedSkipped=0;
    var deletable=ids.filter(function(id){
      var oo=objById(id);
      if(oo&&bimIsLocked(oo)){lockedSkipped++;return false;}
      return true;
    });
    if(!deletable.length){a3dToast('Selected object(s) are locked (Pin) \u2014 unlock first to delete');return false;}
    pushUndo();
    var idSet={},i;
    for(i=0;i<deletable.length;i++)idSet[deletable[i]]=true;
    for(i=0;i<A3D.objs.length;i++){
      var oo=A3D.objs[i];
      if(oo.t==='opening'&&oo.bim&&idSet[oo.bim.hostWallId])idSet[oo.id]=true;
      if(oo.t==='roomtag'&&idSet[oo.roomId])idSet[oo.id]=true;   /* __acad3dV101 */
      if(bimIsFooting(oo)&&oo.bim.hostId&&idSet[oo.bim.hostId])idSet[oo.id]=true;   /* __acad3dV102 */
    }
    var kept=[];
    for(i=0;i<A3D.objs.length;i++){if(!idSet[A3D.objs[i].id])kept.push(A3D.objs[i]);}
    var removedCount=A3D.objs.length-kept.length;
    A3D.objs=kept;
    if(idSet[A3D.sel])A3D.sel=null;
    if(idSet[A3D.sel2])A3D.sel2=null;
    A3D.selSet=A3D.selSet.filter(function(id){return !idSet[id];});
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(removedCount+' object(s) deleted'+(lockedSkipped?' ('+lockedSkipped+' locked object(s) skipped)':''));
    return true;
  }
  function bimDuplicateObject(o,dx,dz){
    /* __acad3dV123: every copy below that is rebuilt from the original's geometry keeps the
       original's offset (pos) -- the geometry is in the original's own frame, and the frame's offset
       was thrown away, so a copy of a wall moved 10 m came out 10 m from where it should be. The
       gizmo's Ctrl-drag copies through here too. */
    var copy;
    if(o.t==='opening')return null;
    if(bimIsHatch(o)){          /* __acad3dV96 */
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pts=o.pts.map(function(p){return [p[0]+dx,p[1]+dz];});
      copy.name=o.name+' copy';
      return copy;
    }
    if(bimIsCline(o)){          /* __acad3dV94: a translation moves the root, never the angle */
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.p=[o.p[0]+dx,o.p[1]+dz];
      copy.name=o.name+' copy';
      return copy;
    }
    if(o.t==='sketch'){
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pts=o.pts.map(function(p){return [p[0]+dx,p[1]+dz];});
      copy.name=o.name+' copy';
    }else if(o.bim&&o.bim.type==='wall'){
      var newCl=o.bim.centerline.map(function(p){return [p[0]+dx,p[1]+dz];});
      /* __acad3dV89: a translation leaves every bulge exactly as it was. */
      var res=bimBuildWallGeometry(newCl,o.bim.baseY,o.bim.height,o.bim.thickness,o.bim.align,o.bim.closed,o.bim.bulges);
      if(res.error)return null;
      A3D.counts.wall=(A3D.counts.wall||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Wall_'+A3D.counts.wall,col:o.col,pos:bimObjOffset(o),mesh:res.mesh,bim:bimCarryBim(o.bim,res.bim),layer:o.layer};
    }else if(o.bim&&o.bim.type==='floor'){
      if(!o.bim.profile)return null;
      var newProf=o.bim.profile.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res2=bimBuildFloorGeometry(newProf,o.bim.baseY,o.bim.thickness);
      if(res2.error)return null;
      A3D.counts.floor=(A3D.counts.floor||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Floor_'+A3D.counts.floor,col:o.col,pos:bimObjOffset(o),mesh:res2.mesh,
        bim:bimCarryBim(o.bim,{type:'floor',profile:newProf}),layer:o.layer};
    }else if(o.bim&&o.bim.type==='column'){
      var newCenter=[o.bim.center[0]+dx,o.bim.center[1]+dz];
      // __acad3dV81: an array copy keeps the original's orientation.
      var res3=bimBuildColumnGeometry(newCenter,o.bim.baseY,o.bim.width,o.bim.depth,o.bim.height,o.bim.rotation||0,o.bim.section||null);   /* __acad3dV126 */
      if(res3.error)return null;
      A3D.counts.column=(A3D.counts.column||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Column_'+A3D.counts.column,col:o.col,pos:bimObjOffset(o),mesh:res3.mesh,
        bim:bimCarryBim(o.bim,{type:'column',center:newCenter}),layer:o.layer};
    }else if(o.t==='room'){
      A3D.counts.room=(A3D.counts.room||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'room',name:'Room_'+A3D.counts.room,col:o.col,pos:bimObjOffset(o),
        pts:o.pts.map(function(p){return [p[0]+dx,p[1]+dz];}),y:o.y,area:o.area,levelId:o.levelId,layer:o.layer,
        number:bimNextRoomNumber(o.levelId)};   /* __acad3dV101 */
      bimCopyRoomFields(o,copy);   /* __acad3dV105 */
    }else if(o.t==='dim'){
      // every dim kind stores different point fields, so offset whichever this one actually has
      // rather than assuming the linear p1/p2/d1/d2 shape (which would throw on angular/radial/leader)
      A3D.counts.dim=(A3D.counts.dim||0)+1;
      var dkD=bimDimKind(o);
      function offP(pt){return [pt[0]+dx,pt[1]+dz];}
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',col:o.col,pos:bimObjOffset(o),
        dimKind:o.dimKind,y:o.y,levelId:o.levelId,layer:o.layer,viewId:o.viewId};
      if(dkD==='linear'){
        copy.name='Dim_'+A3D.counts.dim;
        copy.p1=offP(o.p1);copy.p2=offP(o.p2);copy.d1=offP(o.d1);copy.d2=offP(o.d2);copy.length=o.length;
      }else if(dkD==='angular'){
        copy.name='Angle_'+A3D.counts.dim;
        copy.vertex=offP(o.vertex);copy.ap1=offP(o.ap1);copy.ap2=offP(o.ap2);
        copy.a1=o.a1;copy.sweep=o.sweep;copy.arcRadius=o.arcRadius;copy.degrees=o.degrees;
      }else if(dkD==='radius'||dkD==='diameter'){
        copy.name=(dkD==='diameter'?'Dia_':'Rad_')+A3D.counts.dim;
        copy.center=offP(o.center);copy.dStart=offP(o.dStart);copy.dEdge=offP(o.dEdge);
        copy.radius=o.radius;copy.value=o.value;
      }else if(dkD==='leader'){
        copy.name='Leader_'+A3D.counts.dim;
        copy.anchor=offP(o.anchor);copy.elbow=offP(o.elbow);copy.landing=offP(o.landing);
        copy.label=o.label;copy.ldir=o.ldir;
      }else{
        return null;
      }
    }else if(o.t==='text'){
      A3D.counts.text=(A3D.counts.text||0)+1;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'text',name:'Text_'+A3D.counts.text,col:o.col,pos:bimObjOffset(o),
        text:o.text,pt:[o.pt[0]+dx,o.pt[1]+dz],y:o.y,levelId:o.levelId,layer:o.layer};
    }else if(o.bim&&o.bim.type==='roof'&&o.bim.footprint){
      var newFoot=o.bim.footprint.map(function(p){return [p[0]+dx,p[1]+dz];});
      var res4=bimBuildRoofGeometry(newFoot,o.bim.baseY,o.bim.pitch,o.bim.slopeDir,o.bim.thickness,
        {style:o.bim.style||'shed',gables:o.bim.gables||[]});
      if(res4.error)return null;
      A3D.counts.roof=(A3D.counts.roof||0)+1;
      res4.bim.levelId=o.bim.levelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Roof_'+A3D.counts.roof,col:o.col,pos:bimObjOffset(o),mesh:res4.mesh,bim:res4.bim,layer:o.layer};
    }else if(o.bim&&o.bim.type==='stair'){
      // New (path-based) stairs vs legacy single-flight stairs (bim.start/bim.dir, no bim.path)
      // need different rebuild calls; dispatch on which schema this instance carries.
      var res5,newLevelId=o.bim.levelId,newTargetLevelId=o.bim.targetLevelId;
      if(o.bim.path){
        var newPath=o.bim.path.map(function(p){return [p[0]+dx,p[1]+dz];});
        res5=bimBuildStairPathGeometry(newPath,o.bim.width,o.bim.baseY,o.bim.totalRise,o.bim.riserH,o.bim.treadD,o.bim.landingLen,o.bim.railings,o.bim.railHeight);
      }else{
        var newStart=[o.bim.start[0]+dx,o.bim.start[1]+dz];
        res5=bimBuildStairGeometry(newStart,o.bim.dir,o.bim.width,o.bim.baseY,o.bim.totalRise,o.bim.riserH,o.bim.treadD);
      }
      if(res5.error)return null;
      A3D.counts.stair=(A3D.counts.stair||0)+1;
      res5.bim.levelId=newLevelId;
      res5.bim.targetLevelId=newTargetLevelId;
      copy={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Stair_'+A3D.counts.stair,col:o.col,pos:bimObjOffset(o),mesh:res5.mesh,bim:res5.bim,layer:o.layer};
    }else{
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pos=[o.pos[0]+dx,o.pos[1],o.pos[2]+dz];
      copy.name=o.name+' copy';
    }
    return copy;
  }
  function duplicateSelection(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Nothing selected to duplicate');return;}
    pushUndo();
    var newIds=[],pairs=[],i;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      var copy=bimDuplicateObject(o,1,1);
      if(copy){A3D.objs.push(copy);newIds.push(copy.id);pairs.push([o,copy]);}
    }
    if(!newIds.length){a3dToast('Nothing could be duplicated (unsupported object type)');return;}
    var cut=bimRelinkCopies(pairs,1,1,0);   /* __acad3dV124 */
    A3D.selSet=newIds;
    A3D.sel=newIds[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Duplicated '+newIds.length+' object(s)'+bimRelinkNote(cut));
  }
