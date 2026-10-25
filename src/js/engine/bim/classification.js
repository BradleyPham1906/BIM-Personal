  /* ---------- Phase 47: Classification system ----------
     A lightweight, original classification-code registry: each entry is just a code and a
     description, and any object can optionally carry a classId referencing one. Unlike a
     level or building, a classification is not structurally load-bearing, so deleting one
     that is in use is never blocked -- instead every object referencing it has its classId
     cleared and the user is told how many were affected, following the file's established
     "fail gracefully, warn, never corrupt" pattern rather than the level/building "block if
     no heir" pattern. ---------- */
  function bimFindClassification(id){
    var i;for(i=0;i<A3D.classifications.length;i++)if(A3D.classifications[i].id===id)return A3D.classifications[i];
    return null;
  }
  function bimClassificationInUseCount(id){
    var i,n=0;for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].classId===id)n++;
    return n;
  }
  function addClassification(code,description){
    code=String(code==null?'':code).trim();
    if(!code){a3dToast('Classification code cannot be empty');return null;}
    var i;
    for(i=0;i<A3D.classifications.length;i++){
      if(A3D.classifications[i].code.toLowerCase()===code.toLowerCase()){
        a3dToast('A classification with code "'+code+'" already exists');return null;
      }
    }
    pushUndo();
    var c={id:'cls-'+Date.now().toString(36)+'-'+(A3D.seq++),code:code,description:String(description==null?'':description).trim()};
    A3D.classifications.push(c);
    saveSoon();
    return c;
  }
  function updateClassification(id,field,val){
    var c=bimFindClassification(id);
    if(!c)return;
    if(field==='code'){
      var nc=String(val==null?'':val).trim();
      if(!nc){a3dToast('Classification code cannot be empty');return;}
      pushUndo();c.code=nc;
    }else if(field==='description'){
      pushUndo();c.description=String(val==null?'':val).trim();
    }else return;
    saveSoon();
  }
  function removeClassification(id){
    var c=bimFindClassification(id);
    if(!c)return;
    pushUndo();
    var cleared=0,i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].classId===id){A3D.objs[i].classId=null;cleared++;}
    var idx=-1;
    for(i=0;i<A3D.classifications.length;i++)if(A3D.classifications[i].id===id){idx=i;break;}
    if(idx>=0)A3D.classifications.splice(idx,1);
    refreshTree();refreshProps();saveSoon();
    if(cleared)a3dToast(c.code+' deleted — cleared from '+cleared+' object'+(cleared===1?'':'s'));
    else a3dToast(c.code+' deleted');
  }
  function setObjectClassification(objId,classId){
    var o=objById(objId);
    if(!o)return false;
    pushUndo();
    o.classId=classId||null;
    refreshTree();saveSoon();
    return true;
  }
  function openClassificationDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    function rowsHtml(){
      if(!A3D.classifications.length)return '<div class="a3d-propnote">No classifications yet. Add one below.</div>';
      return A3D.classifications.map(function(c){
        var n=bimClassificationInUseCount(c.id);
        return '<div class="a3d-dlgrow">'+
          '<input type="text" data-clsf="code" data-clsid="'+c.id+'" value="'+bimEsc(c.code)+'" style="max-width:100px" title="Code">'+
          '<input type="text" data-clsf="description" data-clsid="'+c.id+'" value="'+bimEsc(c.description)+'" placeholder="Description" style="flex:1 1 auto" title="Description">'+
          '<span class="a3d-pstatic" title="Objects using this classification">'+n+'</span>'+
          '<button data-clsdel="'+c.id+'" title="Delete">×</button></div>';
      }).join('');
    }
    d.innerHTML='<div class="a3d-dlghd">Manage Classifications</div><div class="a3d-dlgbody">'+
      '<div id="a3d-clsrows">'+rowsHtml()+'</div>'+
      '<div class="a3d-dlgrow"><label>New Code</label><input type="text" id="a3d-clsnewcode" placeholder="e.g. 03 30 00"></div>'+
      '<div class="a3d-dlgrow"><label>Description</label><input type="text" id="a3d-clsnewdesc" placeholder="e.g. Cast-in-Place Concrete"></div>'+
      '<div class="a3d-dlgrow"><label></label><button id="a3d-clsadd">Add Classification</button></div>'+
      '<div class="a3d-propnote">Codes are yours to define — Uniformat, MasterFormat, or a scheme of your own.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Close</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function reopen(){closeDlg();openClassificationDlg();refreshProps();}
    d.addEventListener('click',function(ev){
      var addBtn=ev.target&&ev.target.closest?ev.target.closest('#a3d-clsadd'):null;
      if(addBtn){
        var codeI=d.querySelector('#a3d-clsnewcode'),descI=d.querySelector('#a3d-clsnewdesc');
        var made=addClassification(codeI.value,descI.value);
        if(made)reopen();
        return;
      }
      var del=ev.target&&ev.target.closest?ev.target.closest('[data-clsdel]'):null;
      if(del){removeClassification(del.getAttribute('data-clsdel'));reopen();return;}
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(b)closeDlg();
    });
    d.addEventListener('change',function(ev){
      var inp=ev.target&&ev.target.closest?ev.target.closest('[data-clsf]'):null;
      if(!inp)return;
      updateClassification(inp.getAttribute('data-clsid'),inp.getAttribute('data-clsf'),inp.value);
    });
    d.addEventListener('keydown',function(ev){if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  function refreshLevels(){
    bimSyncStatusLevel();
    if(el.browser)refreshBrowser();
    if(!el.lvlrows)return;
    bimEnsureBuildings();
    var h='',i,j;
    h+='<div class="a3d-lvlrow a3d-siterow" style="background:#20242a;cursor:default">'+
      '<span class="a3d-lvlnm" style="opacity:.7">Site</span>'+
      '<input type="text" data-sitef="name" value="'+bimEsc(A3D.site.name)+'" title="Site name" style="flex:1 1 auto">'+
      '</div>';
    for(i=0;i<A3D.buildings.length;i++){
      var bd=A3D.buildings[i];
      h+='<div class="a3d-lvlrow a3d-bldrow'+(A3D.activeBuilding===bd.id?' active':'')+'" data-a3dbldg="'+bd.id+'">'+
        '<input type="text" class="a3d-bldnm" data-bldf="name" data-bldid="'+bd.id+'" value="'+bimEsc(bd.name)+'" title="Building name">'+
        '<button class="a3d-lvldel" data-blddel="'+bd.id+'" title="Delete building">\u00d7</button></div>';
      for(j=0;j<A3D.levels.length;j++){
        var lv=A3D.levels[j];
        if(lv.buildingId!==bd.id)continue;
        h+='<div class="a3d-lvlrow a3d-lvlsub'+(A3D.activeLevel===lv.id?' active':'')+'" data-a3dlvl="'+lv.id+'">'+
          '<span class="a3d-lvlnm" title="'+bimEsc(lv.name)+'">'+bimEsc(lv.name)+'</span>'+
          '<input type="number" step="any" data-lvlf="elev" data-lvlid="'+lv.id+'" value="'+lv.elev+'" title="Elevation">'+
          '<input type="number" step="any" min="0.1" data-lvlf="height" data-lvlid="'+lv.id+'" value="'+lv.height+'" title="Level height">'+
          '<button class="a3d-lvldel" data-lvldel="'+lv.id+'" title="Delete level">\u00d7</button></div>';
      }
    }
    h+='<div class="a3d-lvlrow" style="background:#20242a;cursor:default">'+
      '<span class="a3d-lvlnm" style="opacity:.7">Grids ('+A3D.grids.length+')</span></div>';
    for(i=0;i<A3D.grids.length;i++){
      var gd=A3D.grids[i];
      h+='<div class="a3d-lvlrow'+(A3D.selGrid===gd.id&&!A3D.sel?' active':'')+'" data-a3dgrid="'+gd.id+'">'+   /* __acad3dV98 */
        '<span class="a3d-lvlnm" title="Grid '+bimEsc(gd.name)+'">Grid '+bimEsc(gd.name)+'</span>'+
        '<button class="a3d-lvldel" data-griddel="'+gd.id+'" title="Delete grid">\u00d7</button></div>';
    }
    bimRenderInto(el.lvlrows,h);   /* __acad3dV118 */
  }
