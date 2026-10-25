  /* ---------- Phase 46: Building / Site hierarchy ----------
     A single project can hold more than one building (a campus, a duplex, an addition
     modeled beside the existing structure), and every level belongs to exactly one of
     them. Site is a single project-wide record (name only, for now) that sits above the
     buildings. Mirrors the level system's own invariants: bimEnsureBuildings() is the
     migration/backfill guard (called after every state restore, same as bimEnsureTypes),
     and removeBuilding() re-hosts orphaned levels onto a surviving building rather than
     ever leaving a level pointing at a building id that no longer exists. ---------- */
  function bimEnsureBuildings(){
    if(!Array.isArray(A3D.buildings)||!A3D.buildings.length)
      A3D.buildings=[{id:'bldg-0',name:'Building 1'}];
    if(!A3D.site||typeof A3D.site!=='object'||typeof A3D.site.name!=='string')
      A3D.site={name:'Site'};
    var i,valid={},firstId=A3D.buildings[0].id;
    for(i=0;i<A3D.buildings.length;i++)valid[A3D.buildings[i].id]=true;
    for(i=0;i<A3D.levels.length;i++){
      if(!A3D.levels[i].buildingId||!valid[A3D.levels[i].buildingId])A3D.levels[i].buildingId=firstId;
    }
    if(!A3D.activeBuilding||!valid[A3D.activeBuilding])A3D.activeBuilding=firstId;
    return A3D.buildings;
  }
  function setActiveBuilding(id){
    var b=null,i;
    for(i=0;i<A3D.buildings.length;i++)if(A3D.buildings[i].id===id)b=A3D.buildings[i];
    if(!b)return;
    A3D.activeBuilding=id;
    var curLvl=bimGetActiveLevel();
    if(!curLvl||curLvl.buildingId!==id){
      var lv=null;
      for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].buildingId===id){lv=A3D.levels[i];break;}
      if(lv){A3D.activeLevel=lv.id;bimSyncActiveGlobal();}
    }
    refreshLevels();
    paint();
    saveSoon();
    a3dToast('Active building: '+b.name);
  }
  function addBuilding(){
    pushUndo();
    var b={id:'bldg-'+Date.now().toString(36)+'-'+(A3D.seq++),name:'Building '+(A3D.buildings.length+1)};
    A3D.buildings.push(b);
    A3D.activeBuilding=b.id;
    var lvl={id:'lvl-'+Date.now().toString(36)+'-'+(A3D.seq++),name:'Level 0',elev:0,height:3,buildingId:b.id};
    A3D.levels.push(lvl);
    A3D.activeLevel=lvl.id;
    bimSyncActiveGlobal();
    refreshLevels();
    saveSoon();
    a3dToast(b.name+' added');
  }
  function updateBuilding(id,field,val){
    var b=null,i;
    for(i=0;i<A3D.buildings.length;i++)if(A3D.buildings[i].id===id)b=A3D.buildings[i];
    if(!b)return;
    if(field==='name'){
      var nm=String(val==null?'':val).trim();
      if(!nm)return;
      pushUndo();
      b.name=nm;
      refreshLevels();refreshTree();
      saveSoon();
    }
  }
  function removeBuilding(id){
    if(A3D.buildings.length<=1){a3dToast('At least one building must remain');return;}
    var doomed=null,i;
    for(i=0;i<A3D.buildings.length;i++)if(A3D.buildings[i].id===id)doomed=A3D.buildings[i];
    if(!doomed)return;
    var heir=null;
    for(i=0;i<A3D.buildings.length;i++)if(A3D.buildings[i].id!==id){heir=A3D.buildings[i];break;}
    if(!heir){a3dToast('No surviving building to receive the levels');return;}
    pushUndo();
    var moved=0;
    for(i=0;i<A3D.levels.length;i++){
      if(A3D.levels[i].buildingId===id){A3D.levels[i].buildingId=heir.id;moved++;}
    }
    for(i=0;i<A3D.buildings.length;i++)if(A3D.buildings[i].id===id){A3D.buildings.splice(i,1);break;}
    if(A3D.activeBuilding===id)A3D.activeBuilding=heir.id;
    bimEnsureBuildings();
    refreshLevels();refreshTree();
    saveSoon();
    if(moved)a3dToast(doomed.name+' deleted - '+moved+' level'+(moved===1?'':'s')+' re-hosted on '+heir.name);
    else a3dToast(doomed.name+' deleted');
  }
  function updateSite(field,val){
    if(field!=='name')return;
    var nm=String(val==null?'':val).trim();
    if(!nm)return;
    pushUndo();
    A3D.site.name=nm;
    saveSoon();
  }
