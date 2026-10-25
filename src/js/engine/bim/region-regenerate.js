  /* ================= __acad3dV99: regenerate regions whose plane changed ================= */
  var A3D_REGEN_BUSY=false;
  function bimRegenerateRegions(){
    if(A3D_REGEN_BUSY||!A3D.objs||!A3D.objs.length)return 0;
    A3D_REGEN_BUSY=true;
    var changed=[],ctx=null,i,o,sid,planes={},key,want,y,edges,sig,b,ip,cut=0,adopted=0;
    try{
      for(i=0;i<A3D.objs.length;i++){
        o=A3D.objs[i];
        /* a single source that no longer exists */
        sid=bimGraphRoomSourceId(o);
        if(sid&&!bimIsRegionDep(o)&&!objById(sid)){
          if(bimCutSource(o,'its source was deleted'))cut++;
          continue;
        }
        /* an older build's multi-wall room: adopt it without changing its shape */
        if(o.t==='room'&&!bimIsRegionDep(o)&&o.sourceType==='wallgroup'&&o.pts&&o.pts.length>=3){
          var q0=bimObjOffset(o),cur=o.pts.map(function(p){return [p[0]+q0[0],p[1]+q0[2]];});
          ip=bimInteriorPoint(cur);
          if(ip){
            var yw=(o.y||0)+q0[1],tr=bimRegionTraceAt(ip,yw,BIM_REGION_WANT.walls);
            o.region={seed:[ip[0]-q0[0],ip[1]-q0[2]],y:o.y||0,want:'walls',
                      members:tr.error?[]:tr.srcIds.slice(),sig:tr.sig||'',open:false};
            adopted++;
          }
          continue;
        }
        if(!bimIsRegionDep(o))continue;
        want=(o.region.want==='walls')?'walls':'all';
        y=bimRegionPlaneY(o);
        key=want+'@'+y.toFixed(4);
        if(!planes[key]){
          edges=bimBoundaryEdges(y,BIM_REGION_WANT[want]);
          planes[key]=bimEdgesSig(edges);
        }
        sig=planes[key];
        if(o.region.sig===sig)continue;
        if(!ctx)ctx={reason:'rebuild',delta:null,recut:0,failed:0,recutWalls:{},wallsRebaked:{},
                     roomsUpdated:0,roomsFailed:0,clonesUpdated:0,clonesFailed:0,openingsShifted:0};
        if(o.t==='room')b=bimRemeasureRoomFromSource(o,ctx);
        else b=bimFollowSource(o,ctx);
        /* whatever happened, this plane state has now been seen */
        if(bimIsRegionDep(o))o.region.sig=sig;
        changed.push(bimGraphObjKey(o.id));
      }
      if(changed.length)bimGraphPropagate(changed,bimGraphVisit,ctx);
    }catch(eRG){
      console.warn('[BIM] Region regeneration failed; regions keep their last shapes.',eRG);
      a3dToast('Some rooms or hatches could not be updated - see the console');
    }
    A3D_REGEN_BUSY=false;
    if(changed.length||cut){
      A3D.meshes={};
      try{refreshTree();paint();}catch(eRP){console.warn('[BIM] Repaint after region update failed',eRP);}
    }
    return changed.length+cut+adopted;
  }
  /* __acad3dV121: every object is on a layer. An object without one is adopted by the current layer
     -- the layer it was made on, since every maker calls saveSoon at once -- and one whose layer no
     longer exists by the first layer, which is what bimLayerOf reads it as. Nine makers never gave
     an object a layer, and a missing layer read as the CURRENT one: every wall followed whichever
     layer was current, out of sight when it was off and out of reach when it was locked. */
  function bimAdoptLayers(){
    var ids={},i,o,n=0,cur=bimLayerById(A3D.activeLayer)||A3D.layers[0],first=A3D.layers[0];
    if(!cur||!first)return 0;
    for(i=0;i<A3D.layers.length;i++)ids[A3D.layers[i].id]=1;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(typeof o.layer!=='string'||!o.layer){o.layer=cur.id;n++;}
      else if(!ids[o.layer]){o.layer=first.id;n++;}
    }
    return n;
  }
  function saveSoon(){
    bimAdoptLayers();   /* __acad3dV121 */
    if(bimLayerDropUnselectable()){refreshTree();refreshProps();paint();}   /* __acad3dV121 */
    /* __acad3dV99: every model mutation passes through here, so this is where a change to
       WHICH shapes bound a region is noticed. */
    bimSweepOrphanTags();   /* __acad3dV101 */
    bimSweepFootingHosts(); /* __acad3dV102 */
    bimRegenerateRegions();
    A3D_REV++;   /* __acad3dV122 */
    bimPagesStale();
    if(saveT)clearTimeout(saveT);
    saveT=setTimeout(save3d,300);
  }
  function refreshHud(){
    /* __acad3dV119: the View readout names the active view -- "Level 0 - Floor Plan", "3D View", an
       elevation, a saved view by its own name, a sheet by its number and name. It showed the camera's
       orientation word (Plan, Isometric) and left the name to the view dropdown's label, which V119
       removed; one record of the active view now feeds the one readout. */
    if(el.view)el.view.textContent=A3D_VIEW.name;
    if(el.count)el.count.textContent=A3D.objs.length+' object'+(A3D.objs.length===1?'':'s');
  }
