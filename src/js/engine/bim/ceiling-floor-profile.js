  // Ceiling: same geometry as Floor but extruded UPWARD from a height offset below the level
  // above, rather than downward from the level datum. Reuses bimBuildFloorGeometry entirely.
  function startCeilingTool(){
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'ceiling',pts:[],y:lvl.elev,on:null};
    a3dToast('Ceiling: click inside an enclosed wall loop or closed sketch on '+lvl.name);
    paint();
  }
  function openCeilingDlg(boundary){
    closeDlg();
    var lvl=bimGetActiveLevel();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Ceiling parameters</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Height above level</label><input type="number" step="any" min="0.1" data-a3dp="h" value="'+(lvl.height||3)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Thickness</label><input type="number" step="any" min="0.01" data-a3dp="t" value="0.1"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var hI=d.querySelector('[data-a3dp="h"]'),tI=d.querySelector('[data-a3dp="t"]');
    function submit(){
      var h=parseFloat(hI.value),t=parseFloat(tI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(h)||h<=0){eb.textContent='Height must be a positive number';return;}
      if(!isFinite(t)||t<=0){eb.textContent='Thickness must be a positive number';return;}
      closeDlg();
      buildCeilingSolid(boundary,h,t);
    }
    d.addEventListener('click',function(ev){var bt=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!bt)return;if(bt.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    hI.focus();hI.select();
  }
  function buildCeilingSolid(boundary,heightAbove,thickness){
    var lvl=bimGetActiveLevel();
    var ceilY=boundary.y+heightAbove;
    var res=bimBuildFloorGeometry(sketchCCW(boundary.pts),ceilY+thickness,thickness);
    if(res.error){a3dToast(res.error.replace('Floor','Ceiling'));return null;}
    pushUndo();
    A3D.counts.ceiling=(A3D.counts.ceiling||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Ceiling_'+A3D.counts.ceiling,col:'#b8bfc7',pos:[0,0,0],mesh:res.mesh,
      bim:{type:'ceiling',thickness:thickness,heightAbove:heightAbove,levelId:lvl.id,baseY:ceilY,profile:sketchCCW(boundary.pts)},layer:A3D.activeLayer};
    if(boundary.sourceId&&(boundary.sourceType==='sketch'||boundary.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=boundary.sourceId;o.sourceType=boundary.sourceType;
    }else if(boundary.region){   /* __acad3dV99 */
      o.region=bimCloneRegion(boundary.region);o.sourceType=boundary.sourceType;o.sourceId=null;
    }
    bimEnsureObjType(o);
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created');
    return o;
  }
  function bimBuildFloorGeometry(profPts,y,thickness){
    var m;
    try{m=padMesh(profPts,y-thickness,thickness);}
    catch(eF){console.warn('[BIM] Floor solid build failed: ',eF);return {error:'Floor build failed: '+(eF&&eF.message?eF.message:eF)};}
    if(!m||!m.f||m.f.length<4)return {error:'Floor produced an empty solid: check the source profile'};
    return {mesh:m};
  }
  /* __acad3dV99: the profile a floor is built from, from a traced boundary. */
  function bimFloorProfileFrom(b){
    return {pts:sketchCCW(b.pts),y:b.y,sourceType:b.sourceType,sourceId:b.sourceId,
            region:b.region?bimCloneRegion(b.region):null};
  }
  function buildFloorSolid(prof,thickness,material,lvl){
    var res=bimBuildFloorGeometry(prof.pts,prof.y,thickness);
    if(res.error){a3dToast(res.error);return null;}
    pushUndo();
    A3D.counts.floor=(A3D.counts.floor||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:'Floor_'+A3D.counts.floor,col:'#9aa79a',pos:[0,0,0],mesh:res.mesh,
      bim:{type:'floor',thickness:thickness,material:material,levelId:lvl.id,baseY:prof.y,profile:prof.pts.slice()}};
    if(prof.sourceId&&(prof.sourceType==='sketch'||prof.sourceType==='wall')){   /* __acad3dV97 */
      o.sourceId=prof.sourceId;o.sourceType=prof.sourceType;
    }else if(prof.region){   /* __acad3dV99 */
      o.region=bimCloneRegion(prof.region);o.sourceType=prof.sourceType;o.sourceId=null;
    }
    A3D.objs.push(o);
    A3D.sel=o.id;A3D.sel2=null;
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(o.name+' created ('+material+')');
    return o;
  }
  function bimRebuildFloor(o,newThickness,newMaterial){
    if(!o||!o.bim||o.bim.type!=='floor'||!o.bim.profile)return false;
    var res=bimBuildFloorGeometry(o.bim.profile,o.bim.baseY,newThickness);
    if(res.error){a3dToast(res.error);return false;}
    pushUndo();
    o.mesh=res.mesh;
    o.bim.thickness=newThickness;
    o.bim.material=newMaterial;
    bimAfterWallRebuild(o);   // __acad3dV53: sync any linked clone of this floor
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
  }
