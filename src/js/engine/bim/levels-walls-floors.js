  // ---- __acad3dV5: BIM Level Manager + Parametric Wall + Structural Floor ----
  function clampLevelHeight(h){
    h=Number(h);
    if(!isFinite(h))return 3;
    if(h<0.1)h=0.1;
    if(h>100)h=100;
    return h;
  }
  function clampLevelElev(e){
    e=Number(e);
    if(!isFinite(e))return 0;
    if(e<-1000)e=-1000;
    if(e>1000)e=1000;
    return e;
  }
  function bimGetActiveLevel(){
    var i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===A3D.activeLevel)return A3D.levels[i];
    return A3D.levels[0]||{id:'lvl-0',name:'Level 0',elev:0,height:3};
  }
  function bimSyncActiveGlobal(){
    window.activeBIMLevel=bimGetActiveLevel();
  }
  function setActiveLevel(id){
    var lvl=null,i;
    for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id)lvl=A3D.levels[i];
    if(!lvl)return;
    A3D.activeLevel=id;
    bimSyncActiveGlobal();
    refreshLevels();
    paint();
    saveSoon();
    a3dToast('Active level: '+lvl.name+' (elevation '+lvl.elev+')');
  }
  function addLevel(){
    var top=0,i,inBldg=0;
    for(i=0;i<A3D.levels.length;i++){
      if(A3D.levels[i].buildingId!==A3D.activeBuilding)continue;
      inBldg++;
      var t=A3D.levels[i].elev+A3D.levels[i].height;if(t>top)top=t;
    }
    pushUndo();
    var lvl={id:'lvl-'+Date.now().toString(36)+'-'+(A3D.seq++),name:'Level '+inBldg,elev:top,height:3,buildingId:A3D.activeBuilding};
    A3D.levels.push(lvl);
    A3D.activeLevel=lvl.id;
    bimSyncActiveGlobal();
    refreshLevels();
    saveSoon();
    a3dToast(lvl.name+' added at elevation '+top);
  }
