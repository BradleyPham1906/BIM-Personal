  /* ---------- Phase 42: level-as-datum integrity ----------
     A BIM level is a datum, not a label. Everything hosted on it must follow it when
     its elevation moves, and nothing may be left pointing at a level that no longer
     exists. Before this, editing an elevation silently desynchronised the datum from
     its geometry, and deleting a level orphaned every element hosted on it (they kept
     a dangling levelId, so the level filter hid them permanently and schedules showed
     a blank level). Both are handled here. ---------- */
  function bimObjectsOnLevel(levelId){
    var out=[],i;
    if(!levelId)return out;
    for(i=0;i<A3D.objs.length;i++)if(bimObjectLevelId(A3D.objs[i])===levelId)out.push(A3D.objs[i]);
    return out;
  }
  function bimShiftObjectY(o,dY){
    /* Shifts every Y-bearing field of one object. Solids carry both a vertex buffer and
       a bim.baseY that must stay in lockstep; annotations, rooms and sketches carry a
       single planar y. Anything else is left untouched rather than guessed at. */
    var i;
    if(!o||!isFinite(dY)||dY===0)return false;
    if(o.mesh&&o.mesh.v&&o.mesh.v.length){
      for(i=0;i<o.mesh.v.length;i++){
        if(o.mesh.v[i]&&typeof o.mesh.v[i][1]==='number')o.mesh.v[i][1]+=dY;
      }
    }
    if(o.bim&&typeof o.bim.baseY==='number')o.bim.baseY+=dY;
    if(typeof o.y==='number')o.y+=dY;
    return true;
  }
  function bimShiftLevelContents(levelId,dY){
    var list=bimObjectsOnLevel(levelId),i,n=0,shiftedIds=[];
    if(!isFinite(dY)||dY===0)return 0;
    for(i=0;i<list.length;i++)if(bimShiftObjectY(list[i],dY)){n++;shiftedIds.push(list[i].id);}
    if(n){
      A3D.meshes={};
      /* __acad3dV55: the Y-shift above is baked directly into each object's own geometry (see
         bimShiftObjectY), not carried as a .pos offset, so a wall and a room/clone built on it
         that are BOTH on this level already stay in lockstep without any further help --
         bimGraphPropagate skips every node passed in as a start, so this call is a no-op for
         them. It matters for the less common case where a room or clone's OWN level differs
         from its source's: there, only one side of the relationship just moved, which
         legitimately breaks it unless the source is part of this same shiftedIds batch
         (bimPropagateFrom's relationship-aware detach), and for any opening whose host wall is
         on this level, translating its Y-independent 2D center bookkeeping by [0,dY,0] is a
         harmless no-op. */
      bimPropagateFrom(shiftedIds,'transform',[0,dY,0]);
    }
    return n;
  }
  function bimNearestLevelTo(elev,excludeId,preferBuildingId){
    var best=null,bestD=Infinity,i;
    if(preferBuildingId){
      for(i=0;i<A3D.levels.length;i++){
        var lvB=A3D.levels[i];
        if(lvB.id===excludeId||lvB.buildingId!==preferBuildingId)continue;
        var dB=Math.abs((lvB.elev||0)-elev);
        if(dB<bestD){bestD=dB;best=lvB;}
      }
      if(best)return best;
      bestD=Infinity;
    }
    for(i=0;i<A3D.levels.length;i++){
      var lv=A3D.levels[i];
      if(lv.id===excludeId)continue;
      var d=Math.abs((lv.elev||0)-elev);
      if(d<bestD){bestD=d;best=lv;}
    }
    return best;
  }
  function updateLevel(id,field,val){
    var lvl=null,i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id)lvl=A3D.levels[i];
    if(!lvl)return;
    if(field==='dl'||field==='ll'){   /* __acad3dV106: a floor load on this level, kPa; blank clears it */
      var ls=String(val==null?'':val).replace(/^\s+|\s+$/g,''),lq=parseFloat(ls);
      if(ls!==''&&(!isFinite(lq)||lq<0)){a3dToast('A floor load is a number of kPa, 0 or more');refreshProps();return;}
      if(ls===''?lvl[field]==null:lvl[field]===lq)return;
      pushUndo();
      if(ls==='')delete lvl[field];else lvl[field]=lq;
      refreshProps();paint();saveSoon();
      a3dToast(lvl.name+': '+(field==='dl'?'dead':'live')+' load '+(ls===''?'cleared':lq+' kPa'));
      return;
    }
    pushUndo();
    if(field==='height')lvl.height=clampLevelHeight(val);
    else if(field==='elev'){
      var prev=lvl.elev||0;
      lvl.elev=clampLevelElev(val);
      var dY=lvl.elev-prev;
      if(dY){
        var moved=0;
        try{moved=bimShiftLevelContents(id,dY);}
        catch(eS){console.warn('[BIM] Level elevation propagation failed, datum reverted.',eS);lvl.elev=prev;a3dToast('Could not move elements with the level - change reverted');refreshLevels();return;}
        if(moved)a3dToast(lvl.name+' moved to '+lvl.elev+' - '+moved+' element'+(moved===1?'':'s')+' followed');
      }
    }
    if(A3D.activeLevel===id)bimSyncActiveGlobal();
    refreshTree();refreshLevels();refreshHud();paint();
    saveSoon();
  }
  function removeLevel(id){
    if(A3D.levels.length<=1){a3dToast('At least one BIM level must remain');return;}
    var doomed=null,i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id)doomed=A3D.levels[i];
    if(!doomed)return;
    var hosted=bimObjectsOnLevel(id);
    var heir=bimNearestLevelTo(doomed.elev||0,id,doomed.buildingId);
    if(!heir){a3dToast('No surviving level to receive the elements');return;}
    pushUndo();
    /* Re-host before removing the datum, so no object is ever left pointing at a level
       that is not in A3D.levels. Geometry is moved with the re-host so the elements stay
       correctly seated on their new datum instead of floating at the old elevation. */
    var dY=(heir.elev||0)-(doomed.elev||0),adopted=0;
    for(i=0;i<hosted.length;i++){
      var o=hosted[i];
      try{
        bimShiftObjectY(o,dY);
        if(o.bim&&o.bim.levelId)o.bim.levelId=heir.id;
        if(o.levelId)o.levelId=heir.id;
        adopted++;
      }catch(eA){console.warn('[BIM] Could not re-host element on level delete: '+(o&&o.name),eA);}
    }
    if(adopted)A3D.meshes={};
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id){A3D.levels.splice(i,1);break;}
    if(A3D.activeLevel===id){A3D.activeLevel=heir.id;}
    bimSyncActiveGlobal();
    refreshTree();refreshLevels();refreshHud();paint();
    saveSoon();
    if(adopted)a3dToast(doomed.name+' deleted - '+adopted+' element'+(adopted===1?'':'s')+' re-hosted on '+heir.name);
    else a3dToast(doomed.name+' deleted');
  }
