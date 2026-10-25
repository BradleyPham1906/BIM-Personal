  /* ================= __acad3dV99: region dependents =================

     o.region = {seed:[x,z], y, want:'all'|'walls', members:[ids], sig, open}

     seed and y are in the dependent's OWN frame, like its points, so moving the dependent moves
     the place it is traced from. members are the objects whose edges the last trace walked --
     what the dependency graph links it to. sig is the signature of the whole plane at the last
     trace. open is true while the region is no longer enclosed; the dependent then keeps its
     last shape and says so once. want is 'all' for everything made from V99 on; a room saved
     by an older build as 'wallgroup' is adopted with 'walls', so re-tracing it cannot pick up
     sketches it never used to see. */
  var BIM_REGION_WANT={all:{walls:true,sketches:true,clines:true},walls:{walls:true}};
  function bimIsRegionDep(o){
    return !!(o&&o.region&&o.region.seed&&o.region.seed.length===2&&
              isFinite(o.region.seed[0])&&isFinite(o.region.seed[1]));
  }
  function bimRegionWant(o){
    return BIM_REGION_WANT[(o&&o.region&&o.region.want==='walls')?'walls':'all'];
  }
  function bimRegionPlaneY(o){return (o.region.y||0)+bimObjOffset(o)[1];}
  function bimRegionSeedWorld(o){
    var q=bimObjOffset(o);
    return [o.region.seed[0]+q[0],o.region.seed[1]+q[2]];
  }
  function bimCloneRegion(r){
    if(!r||!r.seed)return null;
    return {seed:[r.seed[0],r.seed[1]],y:r.y||0,want:r.want==='walls'?'walls':'all',
            members:(r.members||[]).slice(),sig:r.sig||'',open:!!r.open};
  }
  /* A signature of every edge on a plane. Two planes with the same signature trace the same
     faces, so a dependent whose recorded signature still matches needs no re-trace. */
  function bimEdgesSig(edges){
    var h=2166136261,i,s,k;
    function mix(str){
      for(k=0;k<str.length;k++){h^=str.charCodeAt(k);h=(h*16777619)>>>0;}
    }
    for(i=0;i<edges.length;i++){
      s=edges[i].a[0].toFixed(6)+','+edges[i].a[1].toFixed(6)+','+edges[i].b[0].toFixed(6)+','+
        edges[i].b[1].toFixed(6)+','+(edges[i].bulge||0).toFixed(6)+','+(edges[i].src||'')+';';
      mix(s);
    }
    return edges.length+':'+h.toString(36);
  }
  /* A point strictly inside a polygon. The centroid when it is inside; otherwise the middle of
     the widest interior span of a horizontal scan line, tried at several heights -- an L-shaped
     or U-shaped room has its centroid outside itself. */
  function bimInteriorPoint(poly){
    if(!poly||poly.length<3)return null;
    var n=poly.length,i,cx=0,cz=0,minz=Infinity,maxz=-Infinity;
    for(i=0;i<n;i++){cx+=poly[i][0];cz+=poly[i][1];
      if(poly[i][1]<minz)minz=poly[i][1];if(poly[i][1]>maxz)maxz=poly[i][1];}
    cx/=n;cz/=n;
    if(bimPointInPoly([cx,cz],poly))return [cx,cz];
    var fr=[0.5,0.37,0.63,0.25,0.75,0.13,0.87],f,z,xs,j,a,b,best=null,bw=0;
    for(f=0;f<fr.length;f++){
      z=minz+(maxz-minz)*fr[f];
      xs=[];
      for(i=0,j=n-1;i<n;j=i++){
        a=poly[i];b=poly[j];
        if((a[1]>z)!==(b[1]>z))xs.push(a[0]+(z-a[1])*(b[0]-a[0])/(b[1]-a[1]));
      }
      xs.sort(function(p,q){return p-q;});
      for(i=0;i+1<xs.length;i+=2){
        if(xs[i+1]-xs[i]>bw&&bimPointInPoly([(xs[i]+xs[i+1])/2,z],poly)){
          bw=xs[i+1]-xs[i];best=[(xs[i]+xs[i+1])/2,z];
        }
      }
      if(best)return best;
    }
    return null;
  }
  /* Trace the region containing pt on plane y, from the shapes `want` selects. WORLD in and out. */
  function bimRegionTraceAt(pt,y,want){
    var edges=bimBoundaryEdges(y,want||BIM_REGION_WANT.all),sig=bimEdgesSig(edges),res,flat;
    if(edges.length<2)return {error:'there is nothing on this plan to bound it',sig:sig};
    try{res=bimTraceBoundary(edges,pt);}
    catch(eR){
      console.warn('[BIM] Region trace failed',eR);
      return {error:'its boundary could not be traced',sig:sig};
    }
    if(!res||res.error)return {error:(res&&res.error)||'it is not inside a closed region',sig:sig};
    flat=bimFlattenPoly(res.pts,res.bulges,true);
    if(!flat||flat.length<3||!(res.area>1e-6))return {error:'its region has no area',sig:sig};
    return {ring:flat,pts:res.pts,bulges:bimHasBulge(res.bulges)?res.bulges.slice():null,y:y,
            srcs:res.srcs?res.srcs.slice():null,   /* __acad3dV105b */
            srcIds:(res.srcIds||[]).slice(),islands:!!res.islands,sig:sig,type:'region'};
  }
  /* The dependent's current boundary in WORLD plan coordinates -- what it looks like now. */
  function bimDependentRingWorld(o){
    var q=bimObjOffset(o),ring=null;
    if(o.t==='room')ring=o.pts;
    else if(bimIsHatch(o))ring=bimFlattenPoly(o.pts,o.bulges||null,true);
    else if(o.bim&&(o.bim.type==='floor'||o.bim.type==='ceiling'))ring=o.bim.profile;
    else if(o.bim&&o.bim.type==='roof')ring=o.bim.footprint;
    if(!ring||ring.length<3)return null;
    return ring.map(function(p){return [p[0]+q[0],p[1]+q[2]];});
  }
  /* A region dependent's boundary now. From its seed first; when the seed no longer lands in a
     region (a wall was dragged over it), from a point inside the shape it has now. */
  function bimRegionBoundaryWorld(o){
    if(!bimIsRegionDep(o))return {error:'it has no region to trace'};
    var y=bimRegionPlaneY(o),want=bimRegionWant(o);
    var r=bimRegionTraceAt(bimRegionSeedWorld(o),y,want);
    if(!r.error)return r;
    var cur=bimDependentRingWorld(o),ip=cur?bimInteriorPoint(cur):null,r2;
    if(ip){
      r2=bimRegionTraceAt(ip,y,want);
      if(!r2.error)return r2;
    }
    return {error:'it is no longer enclosed',unenclosed:true,sig:r.sig};
  }
  /* Record what a successful trace found: its members and the plane signature. The seed stays
     where the user put it unless it is no longer inside the region found (then a point inside
     the new shape, so the next trace does not start from a point on an edge). */
  function bimRegionRecord(o,b){
    var q=bimObjOffset(o),i,allWalls=b.srcIds.length>0,m,ip;
    o.region.members=b.srcIds.slice();
    o.region.sig=b.sig;
    o.region.open=false;
    if(!bimPointInPoly(bimRegionSeedWorld(o),b.ring)){
      ip=bimInteriorPoint(b.ring);
      if(ip)o.region.seed=[ip[0]-q[0],ip[1]-q[2]];
    }
    for(i=0;i<b.srcIds.length;i++){
      m=objById(b.srcIds[i]);
      if(!(m&&m.t==='solid'&&m.bim&&m.bim.type==='wall')){allWalls=false;break;}
    }
    o.sourceType=allWalls?'wallgroup':'region';o.sourceId=null;
    if(o.bim&&o.bim.type==='roof'){o.bim.sourceType=o.sourceType;o.bim.sourceId=null;}
  }
  /* The region is no longer closed: keep the last shape, say so ONCE, and remember the plane
     signature so the same open plane is not re-traced on every save. */
  function bimRegionNoteOpen(o,b,ctx){
    if(!o.region.open){
      o.region.open=true;
      console.warn('[BIM] '+o.name+' is no longer enclosed; it keeps its last shape.');
      a3dToast(o.name+' is no longer enclosed - it keeps its last shape until its boundary is closed again');
    }
    if(b&&b.sig)o.region.sig=b.sig;
    if(ctx)ctx.regionsOpen=(ctx.regionsOpen||0)+1;
    return false;
  }
  function bimRemeasureRoomFromSource(room,ctx){
    if(!room||room.t!=='room')return false;
    if(bimIsRegionDep(room)){   /* __acad3dV99 */
      var rb=bimRegionBoundaryWorld(room);
      if(rb.error){
        if(rb.unenclosed)return bimRegionNoteOpen(room,rb,ctx);
        console.warn('[BIM] '+room.name+': '+rb.error+'; its boundary was NOT updated.');
        if(ctx){ctx.roomsFailed++;ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;}
        return false;
      }
      var rq=bimObjOffset(room);
      room.pts=bimToFrame(room,bimRoomFaceRing(rb)||rb.ring);   /* __acad3dV105b */
      room.y=rb.y-rq[1];
      room.area=bimPolyArea(room.pts);
      bimRegionRecord(room,rb);
      if(ctx){ctx.roomsUpdated++;ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;}
      return true;
    }
    var st=room.sourceType,sid=room.sourceId;
    if(!sid||(st!=='wall'&&st!=='sketch'))return false;
    /* __acad3dV97: through the source contract. The version this replaces read raw src.pts,
       so a curved sketch was re-measured as chords, and a two-vertex circle failed outright;
       and it wrote WORLD points into a room that is drawn with its own pos added. */
    var b=bimSourceBoundaryWorld(objById(sid));
    if(b.error){
      console.warn('[BIM] '+room.name+': '+b.error+'; its boundary was NOT updated.');
      if(ctx){ctx.roomsFailed++;ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;}
      return false;
    }
    var q=bimObjOffset(room);
    room.pts=bimToFrame(room,b.ring);
    room.y=b.y-q[1];
    room.area=bimPolyArea(room.pts);
    if(ctx){ctx.roomsUpdated++;ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;}
    return true;
  }
  /* __acad3dV97: rebuild a hatch, floor, ceiling or roof from its source's CURRENT boundary.
     Reads the boundary through the source contract and writes it in the dependent's own frame,
     so a dependent that has been moved together with its source does not get its offset twice.
     A failure leaves the object exactly as it was and says why -- never half-rebuilt. */
  function bimFollowSource(o,ctx){
    var sid=bimGraphRoomSourceId(o),isReg=bimIsRegionDep(o);   /* __acad3dV99 */
    if(!sid&&!isReg)return false;
    if(o.t==='room')return bimRemeasureRoomFromSource(o,ctx);
    var b=isReg?bimRegionBoundaryWorld(o):bimSourceBoundaryWorld(objById(sid));
    function fail(msg){
      console.warn('[BIM] '+o.name+': '+msg+'; it was NOT updated.');
      if(ctx)ctx.dependentsFailed=(ctx.dependentsFailed||0)+1;
      return false;
    }
    if(b.error){
      if(isReg&&b.unenclosed)return bimRegionNoteOpen(o,b,ctx);
      return fail(b.error);
    }
    var q=bimObjOffset(o),res,prof;
    try{
      if(bimIsHatch(o)){
        o.pts=bimToFrame(o,b.pts);
        if(b.bulges)o.bulges=b.bulges.slice();else delete o.bulges;
        o.y=b.y-q[1];
      }else if(o.t==='solid'&&o.bim&&o.bim.type==='floor'){
        prof=sketchCCW(bimToFrame(o,b.ring));
        res=bimBuildFloorGeometry(prof,o.bim.baseY,o.bim.thickness);
        if(res.error)return fail(res.error);
        o.mesh=res.mesh;o.bim.profile=prof;
      }else if(o.t==='solid'&&o.bim&&o.bim.type==='ceiling'){
        prof=sketchCCW(bimToFrame(o,b.ring));
        res=bimBuildFloorGeometry(prof,o.bim.baseY+o.bim.thickness,o.bim.thickness);
        if(res.error)return fail(res.error);
        o.mesh=res.mesh;o.bim.profile=prof;
      }else if(o.t==='solid'&&o.bim&&o.bim.type==='roof'){
        var fp=bimToFrame(o,b.ring);
        /* Gable choices are edge INDICES, so they only survive a change that kept the edge
           count; otherwise they would name edges that are no longer the same edges. */
        var keepG=(o.bim.footprint&&o.bim.footprint.length===fp.length)?(o.bim.gables||[]):[];
        res=bimBuildRoofGeometry(fp,o.bim.baseY,o.bim.pitch,o.bim.slopeDir,o.bim.thickness,
          {style:o.bim.style||'shed',gables:keepG});
        if(res.error)return fail(res.error);
        var k,old=o.bim;
        for(k in res.bim)if(res.bim.hasOwnProperty(k))old[k]=res.bim[k];
        o.mesh=res.mesh;
      }else{
        return fail('this kind of object does not know how to follow a boundary');
      }
    }catch(eF){
      console.warn('[BIM] Following a source failed for '+o.name,eF);
      return fail('its rebuild raised an error');
    }
    if(isReg)bimRegionRecord(o,b);   /* __acad3dV99 */
    A3D.meshes={};
    if(ctx)ctx.dependentsUpdated=(ctx.dependentsUpdated||0)+1;
    return true;
  }
  function bimGraphVisit(node,g,ctx){
    var o=node.obj;
    if(!o)return;
    /* __acad3dV101: a tag keeps its offset from a room that was MOVED -- only then. A room that
       re-traced because a wall moved has not been moved, and its tag stays put. */
    /* __acad3dV102: a footing re-derives from its host whatever happened to it -- moved,
       resized, turned or reshaped all change where the footing must be. */
    if(bimIsFooting(o)){
      if(o.bim.hostId)bimRebuildFooting(o,ctx);
      return;
    }
    if(o.t==='roomtag'){
      if(ctx&&ctx.reason==='transform'&&ctx.delta&&ctx.movedIds&&
         ctx.movedIds.indexOf(o.roomId)>=0&&ctx.movedIds.indexOf(o.id)<0){
        if(!o.pos)o.pos=[0,0,0];
        o.pos[0]+=ctx.delta[0];o.pos[2]+=ctx.delta[2];
      }
      return;
    }
    if(o.t==='opening'&&o.bim&&o.bim.hostWallId){
      if(ctx&&ctx.reason==='transform'){
        /* __acad3dV55: a host wall's own .pos moving does NOT touch its centerline -- the whole
           mesh (hole included) moves rigidly at render time, and any future re-cut still looks
           up this opening in the wall's ORIGINAL, unchanged centerline space -- so the plain
           "translations carry their holes with them" rule from below still applies and there is
           nothing to do. The one case where this opening's bookkeeping genuinely goes stale is
           when the host wall is itself a linked CLONE whose centerline was just REALLY rebaked
           (not just .pos-shifted) by the clone branch below, earlier in this same pass -- there,
           translating bim.center by the same delta keeps it valid for a later Trim/Join/rebuild;
           anywhere else, translating it would move it OFF the wall's actual centerline and cause
           a later re-cut to silently drop this opening instead. */
        if(ctx.delta&&ctx.wallsRebaked&&ctx.wallsRebaked[o.bim.hostWallId]&&Array.isArray(o.bim.center)){
          o.bim.center=[o.bim.center[0]+ctx.delta[0],o.bim.center[1]+ctx.delta[2]];
          ctx.openingsShifted++;
        }
        return;
      }
      if(!ctx||ctx.reason!=='rebuild')return;      // translations carry their holes with them
      var wall=objById(o.bim.hostWallId);
      if(!wall)return;
      if(ctx.recutWalls[wall.id])return;           // one pass per wall cuts all of its openings
      ctx.recutWalls[wall.id]=true;
      bimReapplyOpeningsToWall(wall,ctx);
      return;
    }
    if(o.t==='room'){
      // Unlike an opening, a room has no "translations carry their holes with them" exception:
      // its boundary must match whatever the source's CURRENT shape/position is either way, so
      // this re-measures regardless of ctx.reason. bimRemeasureRoomFromSource itself owns the
      // fail-safe rules that decide whether an update is even possible.
      bimRemeasureRoomFromSource(o,ctx);
      return;
    }
    /* __acad3dV97: every other boundary-derived object follows its source the same way.
       __acad3dV99: and so does one bounded by a region. */
    if(bimGraphRoomSourceId(o)||bimIsRegionDep(o)){
      bimFollowSource(o,ctx);
      return;
    }
    if(o.linkSourceId){
      // __acad3dV53: a linked clone tracks its source at a fixed relative offset, so -- like a
      // room, and unlike an opening -- it must follow regardless of ctx.reason: a pure
      // reposition of the source should carry the clone along exactly as much as a parametric
      // rebuild should.
      var syncedOk=bimSyncOneClone(o,ctx);
      // __acad3dV55: this clone's centerline was just genuinely rebaked (not merely .pos-shifted)
      // -- record it so the opening branch above can tell a resynced-clone host apart from a
      // plain .pos-moved one, further down in this same topological pass (a clone is always
      // visited before anything hosted on it, since the host/link edges make it a dependency).
      if(syncedOk&&o.bim&&o.bim.type==='wall'){if(!ctx.wallsRebaked)ctx.wallsRebaked={};ctx.wallsRebaked[o.id]=true;}
      return;
    }
  }
  /* Single entry point for "this element changed, update everything downstream of it".
     reason: 'rebuild' when the element's geometry was regenerated from parameters, 'transform'
     when it was only moved (delta is the [dx,dy,dz] the objIds moved by, in world units --
     used to translate opening bookkeeping that rides along with its host wall's .pos rather
     than being re-cut; see bimGraphVisit's opening branch). Returns a small report so callers
     can tell the user what happened. */
  function bimPropagateFrom(objIds,reason,delta){
    var ctx={reason:reason||'rebuild',delta:delta||null,recut:0,failed:0,recutWalls:{},wallsRebaked:{},roomsUpdated:0,roomsFailed:0,clonesUpdated:0,clonesFailed:0,openingsShifted:0};
    var keys=[],i,regionOrigins=[];   /* __acad3dV99 */
    ctx.movedIds=objIds.slice();      /* __acad3dV101 */
    for(i=0;i<objIds.length;i++){
      keys.push(bimGraphObjKey(objIds[i]));
      // __acad3dV53/55: the object propagated FROM was just directly edited (a rebuild dialog,
      // Join/Merge/Trim, Rotate-in-place, a live grip-drag, or an Align/nudge/drag-move all
      // operate on their own origin object(s) directly). If that origin was itself a linked
      // clone or a room built on a source, it has now diverged from being a pure derived
      // copy/measurement of its source -- UNLESS that same source is ALSO part of this very
      // batch (a group-drag, or a level-elevation shift, can legitimately carry a wall and the
      // room/clone built on it together, in lockstep, without actually breaking the
      // relationship). Only sever the link/source when it is NOT also in objIds -- this keeps
      // every existing single-object call site (55b/55c/55d) behaving exactly as before, since
      // a lone id can never self-reference this way.
      var origin=objById(objIds[i]);
      if(origin&&origin.linkSourceId&&objIds.indexOf(origin.linkSourceId)<0){origin.linkSourceId=null;origin.linkOffset=null;}
      /* __acad3dV97: general, and no longer silent. This was rooms only, and nulled the id
         without a word, so the user could not tell a room had stopped following its sketch. */
      var oSrc=origin?bimGraphRoomSourceId(origin):null;
      if(oSrc&&objIds.indexOf(oSrc)<0)bimCutSource(origin,'moved on its own');
      /* __acad3dV99: a region dependent that was itself edited. A room re-bounds where it now
         is. Anything else re-derives only when every one of its members moved with it, and is
         otherwise detached. Re-derived HERE because the propagation below skips the nodes it
         starts from, and it must happen before anything built on it is visited. */
      /* __acad3dV102: a footing moved without its host becomes its own, and says so */
      if(origin&&bimIsFooting(origin)&&origin.bim.hostId&&objIds.indexOf(origin.bim.hostId)<0){
        var fh=objById(origin.bim.hostId);
        origin.bim.hostId=null;
        a3dToast(origin.name+' is no longer under '+((fh&&fh.name)||'its host')+' (moved on its own) - it stays where it is');
      }
      if(origin&&bimIsRegionDep(origin)){
        var allIn=true,mi,mem=origin.region.members||[];
        for(mi=0;mi<mem.length;mi++)if(objIds.indexOf(mem[mi])<0){allIn=false;break;}
        if(origin.t==='room'||allIn)regionOrigins.push(origin);
        else bimCutSource(origin,'moved on its own');
      }
    }
    for(i=0;i<regionOrigins.length;i++)bimFollowSource(regionOrigins[i],ctx);
    var r=bimGraphPropagate(keys,bimGraphVisit,ctx);
    if(ctx.recut||ctx.failed)A3D.meshes={};
    return {ok:r.ok,recut:ctx.recut,failed:ctx.failed,roomsUpdated:ctx.roomsUpdated,roomsFailed:ctx.roomsFailed,clonesUpdated:ctx.clonesUpdated,clonesFailed:ctx.clonesFailed,openingsShifted:ctx.openingsShifted,visited:r.visited,cycle:r.cycle};
  }
  /* Wraps a solid-geometry rebuild so everything downstream of it follows: the openings cut
     into a wall survive the rebuild, any room sourced from a wall re-measures, and
     (__acad3dV53) any linked clone of the rebuilt object re-syncs. Named for walls, since that
     is where it started and where openings/rooms apply, but every path that replaces ANY
     solid's mesh (wall, floor, or column) from its parameters goes through here now -- the
     opening/room counters are simply always zero for a floor or column, since neither can
     host an opening or source a room. */
  function bimAfterWallRebuild(wall){
    if(!wall)return null;
    var rep=bimPropagateFrom([wall.id],'rebuild');
    if(rep.recut)a3dToast(rep.recut+' opening'+(rep.recut===1?'':'s')+' re-cut into '+wall.name);
    if(rep.roomsUpdated)a3dToast(rep.roomsUpdated+' room'+(rep.roomsUpdated===1?'':'s')+' re-measured');
    if(rep.clonesUpdated)a3dToast(rep.clonesUpdated+' linked clone'+(rep.clonesUpdated===1?'':'s')+' synced');
    if(rep.failed)a3dToast(rep.failed+' opening'+(rep.failed===1?'':'s')+' could not be re-cut - see console, or undo');
    if(rep.roomsFailed)a3dToast(rep.roomsFailed+' room'+(rep.roomsFailed===1?'':'s')+' could not be re-measured - see console, or undo');
    if(rep.clonesFailed)a3dToast(rep.clonesFailed+' linked clone'+(rep.clonesFailed===1?'':'s')+' could not be synced - see console, or undo');
    return rep;
  }
  /* __acad3dV52: same idea as bimAfterWallRebuild, for the OTHER kind of room source. A sketch
     never hosts openings, so this only ever needs to report on rooms. */
  function bimAfterSketchEdit(sketch){
    if(!sketch)return null;
    var rep=bimPropagateFrom([sketch.id],'rebuild');
    if(rep.roomsUpdated)a3dToast(rep.roomsUpdated+' room'+(rep.roomsUpdated===1?'':'s')+' re-measured');
    if(rep.roomsFailed)a3dToast(rep.roomsFailed+' room'+(rep.roomsFailed===1?'':'s')+' could not be re-measured - see console, or undo');
    return rep;
  }
  function openCloneLinkedDlg(){
    var id=A3D.sel;
    if(!id){a3dToast('Select an object to clone');return;}
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Linked Clone</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Offset X (m)</label><input type="number" step="any" data-a3dp="dx" value="0"></div>'+
      '<div class="a3d-dlgrow"><label>Offset Y / Elev (m)</label><input type="number" step="any" data-a3dp="dy" value="0"></div>'+
      '<div class="a3d-dlgrow"><label>Offset Z (m)</label><input type="number" step="any" data-a3dp="dz" value="0"></div>'+
      '<div class="a3d-propnote">The clone follows this object automatically whenever it changes; Sync Clones re-applies it immediately if you do not want to wait for the next edit.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var dx=parseFloat(d.querySelector('[data-a3dp="dx"]').value)||0;
      var dy=parseFloat(d.querySelector('[data-a3dp="dy"]').value)||0;
      var dz=parseFloat(d.querySelector('[data-a3dp="dz"]').value)||0;
      closeDlg();
      cloneLinked(id,dx,dy,dz);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  function applySyncClones(){
    var id=A3D.sel;
    if(!id){a3dToast('Select the source object to sync its clones');return;}
    syncLinkedClones(id);
  }
