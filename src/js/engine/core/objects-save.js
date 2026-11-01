  function add3d(t,prm){
    var tp=TYPES[t];if(!tp)return null;
    var p=mergePrm(t,prm);
    if(validatePrm(t,p))return null;
    pushUndo();
    A3D.counts[t]=(A3D.counts[t]||0)+1;
    var k=A3D.objs.length;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:t,name:tp.n+' '+A3D.counts[t],prm:p,
      pos:[-6+(k%3)*6,0,-6+Math.floor(k/3)*6]
    };
    o.pos[1]=-meshMinY(meshOf(o));
    A3D.objs.push(o);
    A3D.sel=o.id;
    refreshTree();refreshHud();paint();saveSoon();
    return o;
  }
  function del3d(id){
    if(!id)return false;
    var i;
    for(i=A3D.objs.length-1;i>=0;i--){
      if(A3D.objs[i].id===id){
        pushUndo();
        A3D.objs.splice(i,1);
        if(A3D.sel===id)A3D.sel=null;
        if(A3D.sel2===id)A3D.sel2=null;
        refreshTree();refreshHud();paint();saveSoon();
        return true;
      }
    }
    return false;
  }
  var saveT=null;
  /* __acad3dV122: the model's revision, moved by every change (saveSoon). What draws a page -- the
     pages, their thumbnails, the slideshow -- keeps the revision it drew at and draws again only when
     this has moved. */
  var A3D_REV=0;
  /* __acad3dV115: the one list of what a project is. save3d wrote it inline; the project tabs
     need the same list to park a project in its own key and to know what a fresh project is,
     and two copies of one field list are two lists that will eventually disagree. */
  function bimProjectRecord(){
    return {objs:A3D.objs,cam:A3D.cam,seq:A3D.seq,counts:A3D.counts,levels:A3D.levels,grids:A3D.grids,activeLevel:A3D.activeLevel,layers:A3D.layers,activeLayer:A3D.activeLayer,types:A3D.types,activeWallType:A3D.activeWallType,views:A3D.views,activeViewId:A3D.activeViewId,levelFilter:A3D.levelFilter,sheets:A3D.sheets,titleBlock:A3D.titleBlock,buildings:A3D.buildings,activeBuilding:A3D.activeBuilding,site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications,dataFeatures:A3D.dataFeatures||{},history:A3D.history||null,resultLayers:A3D.resultLayers||[],pres:A3D.pres||null};   /* __acad3dV146, __acad3dV148; __acad3dV162 */
  }
  /* __acad3dV115: a save that failed went into an empty catch, so a full browser store lost every
     later edit without a word. It says so now -- once per run of failures, not once per edit. */
  var A3D_SAVE_FAILED=false;
  /* __acad3dV172d: a record localStorage refuses goes to the browser's database (core/idb-store.js), and stays
     there while it is the project on screen; nothing saves while that record is still being read */
  function save3d(){
    if(A3D_SPILL&&A3D_SPILL.loading)return;
    var rec=bimProjectRecord();
    rec.docId=A3D_DOCS.active;
    var s=JSON.stringify(rec);
    if(!(A3D_SPILL&&A3D_SPILL.on)){
      try{
        localStorage.setItem(LSK,s);
        if(A3D_SAVE_FAILED){A3D_SAVE_FAILED=false;a3dToast('Saving to browser storage works again');}
        return;
      }catch(e1){
        console.warn('[BIM] The project does not fit in browser storage; it goes to the browser\'s database.',e1);
      }
    }
    bimSpillSave(rec.docId,s,rec);
  }
