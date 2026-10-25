  /* ================= __acad3dV124: blocks =================
     A block is object RECORDS, not a mesh, so what comes back is what went in: a wall with its
     type, a room, a sketch. Inserted through bimDuplicateObject, the one way this app copies. */
  /* The links an object can hold to another, read and rewritten here and nowhere else in a block. */
  var A3D_BLOCK_LINKS=[['sourceId'],['linkSourceId'],['roomId'],['on'],['bim','sourceId'],['bim','hostWallId'],['bim','hostId']];
  /* what a block cannot carry: an opening is cut into its wall when the wall is built, a room tag is
     made for its room */
  function bimBlockSkips(o){
    return !o||o.t==='opening'||o.t==='roomtag';
  }
  function bimBlockLevelElev(o){
    var lid=bimObjectLevelId(o),i;
    if(lid)for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===lid)return A3D.levels[i].elev;
    return null;
  }
  /* The block a selection makes: the records it can carry, deep-copied, its base point (the centre
     of the selection in plan) and the elevation of the level it came from. */
  function bimBlockFromIds(ids){
    var recs=[],skipped=0,i,y0=null;
    for(i=0;i<ids.length;i++){
      var o=objById(ids[i]);
      if(!o)continue;
      if(bimBlockSkips(o)){skipped++;continue;}
      recs.push(JSON.parse(JSON.stringify(o)));
      if(y0===null)y0=bimBlockLevelElev(o);
    }
    if(!recs.length)return {recs:[],skipped:skipped};
    var b=bimWorldBounds(recs.map(function(r){return r.id;})),base;
    if(b)base=[(b.mn[0]+b.mx[0])/2,(b.mn[2]+b.mx[2])/2];
    else{
      var L=bimRecsPlanLines(recs),sx=0,sz=0,n=0,j,k;
      for(j=0;j<L.length;j++)for(k=0;k<L[j].length;k++){sx+=L[j][k][0];sz+=L[j][k][1];n++;}
      base=n?[sx/n,sz/n]:[0,0];
    }
    if(y0===null)y0=b?b.mn[1]:bimGetActiveLevel().elev;
    return {recs:recs,skipped:skipped,base:base,y0:y0};
  }
  function bimBlockSave(name,ids){
    var blk=bimBlockFromIds(ids||[]);
    if(!blk.recs.length)return null;
    var entry={id:'blk-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),kind:'block',
      name:name,category:'Blocks',manufacturer:'',recs:blk.recs,base:blk.base,y0:blk.y0,
      count:blk.recs.length,createdAt:new Date().toISOString()};
    entry.thumb=bimRecsThumb(entry.recs);
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
  function openSaveBlockDlg(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    if(!ids.length){a3dToast('Select the objects to make a block of first');return;}
    var blk=bimBlockFromIds(ids);
    if(!blk.recs.length){a3dToast('None of the selected objects can be saved in a block (openings and room tags go with their wall and room)');return;}
    var first=objById(ids[0]);
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Save as Block</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(first?first.name+' block':'Block')+'" maxlength="60"></div>'+
      '<div class="a3d-propnote">'+blk.recs.length+' object(s). The base point is the centre of the selection: an insert puts it where you drop or click.'+
      (blk.skipped?' '+blk.skipped+' opening(s) or room tag(s) are not included: they go with their wall and room.':'')+'</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">Save</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var nI=d.querySelector('[data-a3dp="name"]');
    function submit(){
      var name=nI.value.trim();
      var eb=document.getElementById('a3d-dlgerr');
      if(!name){eb.textContent='Enter a name';return;}
      closeDlg();
      var e=null;
      try{e=bimBlockSave(name,ids);}
      catch(eB){console.warn('[BIM] The block could not be saved.',eB);}
      if(!e){a3dToast('The block could not be saved');return;}
      refreshFamilyPanel();
      a3dToast('Saved block "'+e.name+'" ('+e.count+' object(s)) to the library');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  /* __acad3dV124: every copy made by translation is relinked here. pairs is [[original, copy], ...]
     for ONE copy operation; (dx, dz) is how far it moved in plan, dY how far up. Each link is read
     from the ORIGINAL -- a copy path decides what it carries, and a link it dropped or kept by
     accident must not decide what the copy follows. A link to an object copied in the same
     operation points at that object's copy; any other link is dropped. Returns how many were
     dropped. */
  function bimRelinkCopies(pairs,dx,dz,dY){
    var map={},cut=0,i,j;
    dx=dx||0;dz=dz||0;dY=dY||0;
    for(i=0;i<pairs.length;i++)map[pairs[i][0].id]=pairs[i][1].id;
    for(i=0;i<pairs.length;i++){
      var from=pairs[i][0],c=pairs[i][1];
      for(j=0;j<A3D_BLOCK_LINKS.length;j++){
        var path=A3D_BLOCK_LINKS[j];
        if(path.length===2&&!c[path[0]])continue;
        var v=bimLinkGet(from,path);
        if(v===undefined||v===null||v===''){
          /* nothing to carry -- and nothing the copy may keep of its own */
          if(bimLinkGet(c,path))bimLinkSet(c,path,null);
          continue;
        }
        if(map[v]){
          bimLinkSet(c,path,map[v]);
          /* a source carries its kind beside it */
          if(path[path.length-1]==='sourceId')bimLinkSet(c,path.slice(0,-1).concat(['sourceType']),bimLinkGet(from,path.slice(0,-1).concat(['sourceType'])));
        }else{bimLinkSet(c,path,null);cut++;}
      }
      /* a traced region: its seed and the shapes that bound it */
      if(bimIsRegionDep(from)){
        var mem=[],k,ms=from.region.members||[];
        for(k=0;k<ms.length;k++)if(map[ms[k]])mem.push(map[ms[k]]);
        if(mem.length){
          var q0=bimObjOffset(from),q1=bimObjOffset(c),rg=bimCloneRegion(from.region);
          rg.seed=[rg.seed[0]+q0[0]-q1[0]+dx,rg.seed[1]+q0[2]-q1[2]+dz];
          rg.y=(rg.y||0)+q0[1]-q1[1]+dY;
          rg.members=mem;rg.sig='';
          c.region=rg;
        }else{
          if(c.region)c.region=null;
          cut++;
        }
      }else if(c.region){
        c.region=null;
      }
    }
    return cut;
  }
  function bimRelinkNote(cut){
    return cut?'; '+cut+' link(s) to shapes that were not copied with them were not kept -- the copies are shapes of their own':'';
  }
  function bimLinkGet(o,path){
    return path.length===1?o[path[0]]:(o[path[0]]?o[path[0]][path[1]]:undefined);
  }
  function bimLinkSet(o,path,v){
    if(path.length===1)o[path[0]]=v;else if(o[path[0]])o[path[0]][path[1]]=v;
  }
  /* Insert a block with its base point at pt ([x, z] on the active level). Returns the new ids, or
     null when nothing could be made. One undo step. */
  function bimInsertBlock(entry,pt){
    if(!entry||bimAssetKind(entry)!=='block'||!entry.recs||!entry.recs.length){a3dToast('That block has nothing in it');return null;}
    var lvl=bimGetActiveLevel(),dx=pt[0]-entry.base[0],dz=pt[1]-entry.base[1];
    var dY=lvl.elev-(isFinite(entry.y0)?entry.y0:lvl.elev);
    pushUndo();
    var mark=UNDO_STACK[UNDO_STACK.length-1];
    var made=[],from=[],map={},failed=0,i,j;
    for(i=0;i<entry.recs.length;i++){
      var r=JSON.parse(JSON.stringify(entry.recs[i])),c=null;
      try{c=bimDuplicateObject(r,dx,dz);}
      catch(eD){console.warn('[BIM] A block member could not be copied: '+(r&&r.name),eD);c=null;}
      if(!c){failed++;continue;}
      map[r.id]=c.id;
      from.push(r);
      bimShiftObjectY(c,dY);
      if(c.bim&&c.bim.levelId!==undefined)c.bim.levelId=lvl.id;
      if(c.levelId!==undefined)c.levelId=lvl.id;
      if(!c.layer||!bimLayerById(c.layer))c.layer=A3D.activeLayer;
      made.push(c);
    }
    /* the links, read from the SAVED records (bimRelinkCopies) */
    var cut=bimRelinkCopies(made.map(function(c,k){return [from[k],c];}),dx,dz,dY);
    if(!made.length){
      /* nothing was made, so the step this pushed would undo nothing */
      if(!undoSuspend&&UNDO_STACK.length&&UNDO_STACK[UNDO_STACK.length-1]===mark)UNDO_STACK.pop();
      a3dToast('Nothing in "'+entry.name+'" could be inserted');return null;
    }
    for(i=0;i<made.length;i++)A3D.objs.push(made[i]);
    A3D.meshes={};
    var ids=made.map(function(o){return o.id;});
    A3D.selSet=ids.slice();A3D.sel=ids[0];A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast('Inserted "'+entry.name+'" ('+made.length+' object(s))'+
      (failed?', '+failed+' could not be copied':'')+
      (cut?'; '+cut+' link(s) to objects outside the block were not kept':''));
    return ids;
  }
  function startFamilyPlaceTool(famId){
    var fam=bimFamilyLibraryGet(famId);
    if(!fam){a3dToast('Family not found (it may have been deleted)');return;}
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'familyplace',pts:[],y:lvl.elev,on:null,placeFamId:famId};
    a3dToast('Click to place '+fam.name);
    paint();
  }
  function bimPlaceFamilyInstance(fam,posXZ){
    pushUndo();
    A3D.counts.familyInstance=(A3D.counts.familyInstance||0)+1;
    var lvl=bimGetActiveLevel();
    var inst=bimCreateFamilyInstance(fam,posXZ,lvl.elev,A3D.counts.familyInstance);
    inst.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
    inst.layer=A3D.activeLayer;
    inst.bim.levelId=A3D.activeLevel;
    A3D.objs.push(inst);
    A3D.sel=inst.id;A3D.sel2=null;A3D.selSet=[inst.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(inst.name+' placed');
  }
  function refreshFamilyPanel(){
    /* __acad3dV124: the library shows in the Project Browser's Families and in the Assets tab.
       The list this also wrote into #a3d-famrows, an element that was never shown, is gone. */
    if(el.browser)refreshBrowser();
    refreshAssets();
  }
