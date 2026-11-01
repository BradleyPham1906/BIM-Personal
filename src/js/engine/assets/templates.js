  /* ================= __acad3dV124: templates -- a starting project =================
     The record goes under its own key before the entry is added, so a full store adds nothing. */
  function bimTemplateSave(name){
    var rec=JSON.parse(JSON.stringify(bimProjectRecord()));
    delete rec.docId;
    var id='tpl-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6);
    /* __acad3dV172e: a template localStorage refuses is kept in the browser's database; the entry goes again if the
       database refuses it too */
    var s=JSON.stringify(rec),inIdb=false;
    try{localStorage.setItem(A3D_TEMPLATE_PREFIX+id,s);}
    catch(eS){
      console.warn('[BIM] The template does not fit in browser storage; it goes to the browser\'s database.',eS);
      inIdb=true;
    }
    var entry={id:id,kind:'template',name:name,category:'Templates',manufacturer:'',
      count:Array.isArray(rec.objs)?rec.objs.length:0,
      levels:Array.isArray(rec.levels)?rec.levels.length:0,
      sheets:Array.isArray(rec.sheets)?rec.sheets.length:0,
      createdAt:new Date().toISOString()};
    entry.thumb=bimRecsThumb(rec.objs||[]);
    if(inIdb){
      entry.idb=1;
      bimIdbPut('tpl:'+id,{rec:s,saved:Date.now(),v:1},function(err){
        if(!err)return;
        console.warn('[BIM] The template could not be stored.',err);
        var i;for(i=A3D_FAMLIB.length-1;i>=0;i--)if(A3D_FAMLIB[i].id===id)A3D_FAMLIB.splice(i,1);
        bimSaveFamilyLibrary();
        try{refreshFamilyPanel();}catch(eR){console.warn('[BIM] The Assets panel could not be refreshed.',eR);}
        a3dToast('The template could not be saved: browser storage is full');
      });
    }
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
  /* A new project tab that starts as a copy of the template. Returns the new project's id. */
  function bimTemplateUse(entry){
    if(!entry||bimAssetKind(entry)!=='template')return null;
    /* __acad3dV172e: a template kept in the browser's database is read first; the project follows */
    if(entry.idb){
      bimIdbGet('tpl:'+entry.id,function(err,v){
        var r=null;
        if(!err&&v&&typeof v.rec==='string'){try{r=JSON.parse(v.rec);}catch(eJ){r=null;}}
        if(!r||typeof r!=='object'){
          if(err)console.warn('[BIM] The browser\'s database could not be read.',err);
          a3dToast('"'+entry.name+'" could not be used: its stored project could not be read');
          return;
        }
        bimTemplateStart(entry,r);
      });
      return true;
    }
    var raw=null,rec=null;
    try{raw=localStorage.getItem(A3D_TEMPLATE_PREFIX+entry.id);}
    catch(eG){console.warn('[BIM] Browser storage could not be read.',eG);}
    if(raw==null){a3dToast('The project stored for "'+entry.name+'" is no longer in this browser\'s storage');return null;}
    try{rec=JSON.parse(raw);}catch(eP){console.warn('[BIM] A stored template is not valid JSON: '+entry.id,eP);rec=null;}
    if(!rec||typeof rec!=='object'){a3dToast('"'+entry.name+'" could not be used: its stored project is damaged');return null;}
    return bimTemplateStart(entry,rec);
  }
  function bimTemplateStart(entry,rec){
    if(!rec.titleBlock||typeof rec.titleBlock!=='object')rec.titleBlock={project:'',client:'',drawnBy:'',checkedBy:''};
    rec.titleBlock.project=bimNextProjectName();
    var id=bimDocsAdd(rec,'create');
    if(id)a3dToast('New project '+rec.titleBlock.project+' from the template "'+entry.name+'"');
    return id;
  }
  function openSaveTemplateDlg(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Save as Template</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(bimProjectLabel()+' template')+'" maxlength="60"></div>'+
      '<div class="a3d-propnote">Keeps this whole project -- its levels, grids, layers, types, views, sheets, title block and '+
      A3D.objs.length+' object(s) -- as the start of new projects. A project made from it is a copy: the template does not change.</div>'+
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
      var e=bimTemplateSave(name);
      if(!e)return;
      refreshFamilyPanel();
      a3dToast('Saved template "'+e.name+'" to the library');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    nI.focus();nI.select();
  }
  function bimNameFromFile(filename){
    var n=String(filename||'').replace(/^.*[\\\/]/,'').replace(/\.acad3d\.json$/i,'').replace(/\.json$/i,'').trim();
    return n||'Opened project';
  }
  function bimDocsOpenData(data,filename){
    if(!data.titleBlock||typeof data.titleBlock!=='object')data.titleBlock={project:'',client:'',drawnBy:'',checkedBy:''};
    if(!String(data.titleBlock.project||'').trim())data.titleBlock.project=bimNameFromFile(filename);
    return bimDocsAdd(data,'open');
  }
  function bimDocsClose(id){
    var at=A3D_DOCS.open.indexOf(id);
    if(at<0)return false;
    if(id===A3D_DOCS.active){
      var next=A3D_DOCS.open[at+1]||A3D_DOCS.open[at-1]||null;
      if(next){
        if(!bimDocsActivate(next))return false;
      }else{
        /* the last tab: the project stays loaded behind the Start page, as the one a reload finds */
        try{if(A3D.sk)bimEndSketch();}
        catch(eE){console.warn('[BIM] The running command could not be ended before closing.',eE);}
        closeDlg();
        if(saveT){clearTimeout(saveT);saveT=null;}
        save3d();
      }
    }
    A3D_DOCS.open.splice(A3D_DOCS.open.indexOf(id),1);
    bimDocsSave();
    bimDocsNotify('close',id);
    return true;
  }
  function bimDocsRemove(id){
    var ent=bimDocEntry(id);
    if(!ent)return false;
    if(A3D_DOCS.open.indexOf(id)>=0){a3dToast('Close "'+bimDocName(id)+'" before deleting it');return false;}
    if(id===A3D_DOCS.active){a3dToast('Open another project before deleting "'+bimDocName(id)+'"');return false;}
    try{localStorage.removeItem(A3D_DOC_PREFIX+id);}
    catch(eX){console.warn('[BIM] A stored project could not be deleted.',eX);a3dToast('The project could not be deleted');return false;}
    bimIdbDel(id,function(eD){if(eD)console.warn('[BIM] A project\'s copy in the browser\'s database could not be removed: '+id,eD);});   /* __acad3dV172d */
    A3D_DOCS.docs=A3D_DOCS.docs.filter(function(e){return e.id!==id;});
    delete A3D_DOC_RT[id];
    bimDocsSave();
    bimDocsNotify('remove',id);
    a3dToast('Deleted "'+(ent.name||'Untitled project')+'"');
    return true;
  }
