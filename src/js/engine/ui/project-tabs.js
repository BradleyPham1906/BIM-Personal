  /* ================= __acad3dV115: projects side by side =================
     AutoCAD's file tabs and Revit's open projects: several projects open at once, each its own
     model with its own undo history, one on screen. What is on screen is always the project in
     'acad3dV1'. Switching parks it in its own key, then loads the next one into 'acad3dV1', and
     only then removes the next one's own copy -- so at every instant each project is stored in
     at least one place, and when it is briefly in two, 'acad3dV1' (written last) is the one boot
     keeps. The list in 'acad3dDocsV1' is a cache of what is stored: boot re-derives it from the
     keys, so a stored project the list lost is listed again rather than orphaned. */
  /* the one derivation of a project's name, from its title block: the tab, the Start page, the
     dock, the sheets and every download name all go through it */
  function bimNameOf(tb){
    var p=tb&&tb.project;
    p=String(p==null?'':p).trim();
    return p||'Untitled project';
  }
  function bimProjectLabel(){return bimNameOf(A3D.titleBlock);}
  function bimNewDocId(){
    return 'doc-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e9).toString(36);
  }
  function bimDocEntry(id){
    var i;
    for(i=0;i<A3D_DOCS.docs.length;i++)if(A3D_DOCS.docs[i].id===id)return A3D_DOCS.docs[i];
    return null;
  }
  function bimDocName(id){
    if(id===A3D_DOCS.active)return bimProjectLabel();
    var d=bimDocEntry(id);
    return (d&&d.name)||'Untitled project';
  }
  function bimDocMetaFromStore(id){
    var meta={id:id,name:'Damaged project',objs:0,saved:0};
    try{
      var st=JSON.parse(localStorage.getItem(A3D_DOC_PREFIX+id)||'null');
      if(st&&typeof st==='object'){
        meta.name=bimNameOf(st.titleBlock);
        meta.objs=Array.isArray(st.objs)?st.objs.length:0;
      }
    }catch(eM){console.warn('[BIM] A stored project could not be read: '+id,eM);}
    return meta;
  }
  function bimDocsBoot(){
    var idx=null,keys=[],seen={},docs=[],open=[],i,j,k,d,act=null,fresh=false;
    try{idx=JSON.parse(localStorage.getItem(A3D_DOCS_KEY)||'null');}
    catch(eI){console.warn('[BIM] The project list is damaged; it is rebuilt from the stored projects.',eI);idx=null;}
    if(!idx||typeof idx!=='object'||!Array.isArray(idx.docs)){idx={v:1,active:null,open:[],docs:[]};fresh=true;}
    try{
      for(i=0;i<localStorage.length;i++){
        k=localStorage.key(i);
        if(k&&k.indexOf(A3D_DOC_PREFIX)===0)keys.push(k.slice(A3D_DOC_PREFIX.length));
      }
    }catch(eK){console.warn('[BIM] Browser storage could not be listed.',eK);}
    for(i=0;i<idx.docs.length;i++){
      d=idx.docs[i];
      if(!d||typeof d.id!=='string'||!d.id||seen[d.id])continue;
      seen[d.id]=1;
      docs.push({id:d.id,name:typeof d.name==='string'?d.name:'',objs:isFinite(d.objs)?+d.objs:0,saved:isFinite(d.saved)?+d.saved:0});
    }
    for(i=0;i<keys.length;i++){
      if(seen[keys[i]])continue;
      seen[keys[i]]=1;
      docs.push(bimDocMetaFromStore(keys[i]));
      console.warn('[BIM] A stored project was missing from the project list and is listed again: '+keys[i]);
    }
    /* which project is on screen: the one 'acad3dV1' says it is */
    if(A3D_BOOT_DOC){
      act=A3D_BOOT_DOC;
      if(keys.indexOf(act)>=0){
        /* a switch stopped after parking this project and before the next one took its place;
           'acad3dV1' is written after the parked copy, so the parked copy is the stale one */
        try{localStorage.removeItem(A3D_DOC_PREFIX+act);}
        catch(eR){console.warn('[BIM] A stale copy of the open project could not be removed.',eR);}
        keys.splice(keys.indexOf(act),1);
      }
    }else if(idx.active&&seen[idx.active]&&keys.indexOf(idx.active)<0){
      act=idx.active;   /* saved by a build that did not tag the record */
    }else{
      act=bimNewDocId();   /* first run: the project already here becomes the first tab */
    }
    if(!seen[act]){seen[act]=1;docs.push({id:act,name:bimProjectLabel(),objs:A3D.objs.length,saved:Date.now()});}
    docs=docs.filter(function(e){
      if(e.id===act||keys.indexOf(e.id)>=0)return true;
      console.warn('[BIM] A project in the list has nothing stored behind it and is dropped: '+(e.name||e.id));
      return false;
    });
    if(fresh)open=[act];
    else if(Array.isArray(idx.open)){
      for(i=0;i<idx.open.length;i++){
        k=idx.open[i];
        if(typeof k!=='string'||open.indexOf(k)>=0)continue;
        for(j=0;j<docs.length;j++)if(docs[j].id===k){open.push(k);break;}
      }
      /* the project on screen can only be closed when it is the last one, so with any tab open
         it is one of them */
      if(open.length&&open.indexOf(act)<0)open.push(act);
    }
    var res={v:1,active:act,open:open,docs:docs};
    try{localStorage.setItem(A3D_DOCS_KEY,JSON.stringify(res));}
    catch(eW){console.warn('[BIM] The project list could not be saved.',eW);}
    return res;
  }
  /* an autosave waits 300 ms for the edits after it, and an edit made in that window was lost when
     the page closed or reloaded -- measured: a wall drawn just before a reload, gone 8 times in 8.
     pagehide is the last moment the page can still write. */
  window.addEventListener('pagehide',function(){
    if(saveT){clearTimeout(saveT);saveT=null;save3d();}
  });
  function bimDocsSave(){
    try{localStorage.setItem(A3D_DOCS_KEY,JSON.stringify(A3D_DOCS));return true;}
    catch(eD){
      console.warn('[BIM] The project list could not be saved.',eD);
      a3dToast('The list of projects could not be saved: browser storage is full');
      return false;
    }
  }
  function bimDocsNotify(kind,id){
    try{window.dispatchEvent(new CustomEvent('a3ddocs',{detail:{kind:kind,id:id}}));}
    catch(eN){console.warn('[BIM] The document tabs could not be told about a change.',eN);}
  }
  /* The Start page is a document of its own, as it is in AutoCAD: while it shows, no project is
     the current one, so keys and commands have nothing to act on. */
  function bimStartShowing(){
    var s=document.getElementById('acad-start');
    return !!(s&&s.classList.contains('show'));
  }
  /* Opening a project is booting into it: a fresh project, then what was stored, through the
     same validation boot uses. Nothing of the previous project can survive a field the next one
     does not carry, because every field is reset first. */
  function bimLoadProjectRecord(st){
    var d=JSON.parse(A3D_PROJECT_DEFAULTS),k;
    for(k in d)if(d.hasOwnProperty(k))A3D[k]=d[k];
    bimApplyStoredState(st);
    undoSuspend=true;
    try{
      bimEnsureTypes();
      bimEnsureBuildings();
      A3D.sel=null;A3D.sel2=null;A3D.selSet=[];A3D.meshes={};
      A3D.activeSheetId=null;A3D.sheetSelVp=null;A3D.sheetDrag=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */
      bimSyncActiveGlobal();
      refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();refreshBrowser();refreshProps();
      bimSyncStatusBar();
    }finally{undoSuspend=false;}
  }
  function bimDocsSwap(toId,stB,fromKey){
    var cur=A3D_DOCS.active;
    if(toId===cur)return true;
    try{if(A3D.sk)bimEndSketch();}
    catch(eE){console.warn('[BIM] The running command could not be ended before switching projects.',eE);}
    closeDlg();
    bimCloseSheetView();
    if(A3D.section){
      try{bimExitSection();}
      catch(eX){console.warn('[BIM] The section view could not be closed before switching projects.',eX);}
    }
    var recA=bimProjectRecord();recA.docId=cur;
    var sA=JSON.stringify(recA);
    stB.docId=toId;
    var sB=JSON.stringify(stB);
    var full='There is not enough browser storage to switch projects. Use Save to keep this project as a file, then delete projects you no longer need from Start.';
    try{localStorage.setItem(A3D_DOC_PREFIX+cur,sA);}
    catch(e1){console.warn('[BIM] The current project could not be parked in its own key.',e1);a3dToast(full);return false;}
    try{localStorage.setItem(LSK,sB);}
    catch(e2){
      try{localStorage.removeItem(A3D_DOC_PREFIX+cur);}
      catch(e3){console.warn('[BIM] A parked copy could not be removed after a failed switch.',e3);}
      console.warn('[BIM] The next project could not be written to the active slot.',e2);
      a3dToast(full);
      return false;
    }
    var stash={undo:UNDO_STACK,redo:REDO_STACK,view:{kind:A3D_VIEW.kind,id:A3D_VIEW.id},lastModel:A3D_LAST_MODEL_VIEW,   /* __acad3dV116 */
      cam:{yaw:A3D.cam.yaw,pitch:A3D.cam.pitch,dist:A3D.cam.dist,tx:A3D.cam.tx,ty:A3D.cam.ty,tz:A3D.cam.tz}};
    var nameA=bimProjectLabel(),countA=A3D.objs.length;
    var rt=A3D_DOC_RT[toId]||null;
    try{
      UNDO_STACK=rt?rt.undo:[];REDO_STACK=rt?rt.redo:[];
      A3D_TYPING.active=false;A3D_TYPING.buf='';
      bimLoadProjectRecord(stB);
    }catch(eL){
      console.warn('[BIM] The project could not be loaded; the previous one is put back.',eL);
      try{
        localStorage.setItem(LSK,sA);
        localStorage.removeItem(A3D_DOC_PREFIX+cur);
      }catch(eP){console.warn('[BIM] Browser storage could not be put back after a failed switch.',eP);}
      UNDO_STACK=stash.undo;REDO_STACK=stash.redo;
      try{bimLoadProjectRecord(JSON.parse(sA));}
      catch(eA){console.warn('[BIM] The previous project could not be reloaded.',eA);}
      a3dToast('"'+bimDocName(toId)+'" could not be opened: its stored data is damaged');
      return false;
    }
    if(fromKey){
      try{localStorage.removeItem(fromKey);}
      catch(e4){console.warn('[BIM] The opened project\'s parked copy could not be removed.',e4);}
    }
    var entA=bimDocEntry(cur);
    if(entA){entA.name=nameA;entA.objs=countA;entA.saved=Date.now();}
    A3D_DOC_RT[cur]=stash;
    A3D_DOCS.active=toId;
    var shown=false;
    if(rt&&rt.view){
      shown=bimActivateView(rt.view.kind,rt.view.id,{anim:false});
      if(shown&&rt.view.kind!=='sheet'){A3D.cam=rt.cam;paint();}
    }
    if(!shown)bimActivateView(window.ACAD_WS_CUR==='3d'?'3d':'plan',A3D.activeLevel,{anim:false});
    A3D_LAST_MODEL_VIEW=(rt&&rt.lastModel)||null;   /* __acad3dV116: after the activation, which would record the other project's */
    bimDocsSave();
    return true;
  }
  function bimDocsActivate(id){
    var ent=bimDocEntry(id);
    if(!ent){console.warn('[BIM] Unknown project: '+id);a3dToast('That project is not in the list');return false;}
    if(id!==A3D_DOCS.active){
      var nm=ent.name||'Untitled project',raw=null,st=null;
      try{raw=localStorage.getItem(A3D_DOC_PREFIX+id);}
      catch(eG){console.warn('[BIM] Browser storage could not be read.',eG);}
      if(raw==null){a3dToast('"'+nm+'" is no longer in this browser\'s storage');return false;}
      try{st=JSON.parse(raw);}
      catch(eP){console.warn('[BIM] A stored project is not valid JSON: '+id,eP);st=null;}
      if(!st||typeof st!=='object'){a3dToast('"'+nm+'" could not be opened: its stored data is damaged');return false;}
      if(!bimDocsSwap(id,st,A3D_DOC_PREFIX+id))return false;
    }
    if(A3D_DOCS.open.indexOf(id)<0)A3D_DOCS.open.push(id);
    bimDocsSave();
    bimDocsNotify('activate',id);
    return true;
  }
  function bimNextProjectName(){
    var used={},i,n;
    for(i=0;i<A3D_DOCS.docs.length;i++)used[bimDocName(A3D_DOCS.docs[i].id).toLowerCase()]=1;
    for(n=1;n<100000;n++)if(!used[('project'+n)])return 'Project'+n;
    return 'Project';
  }
  function bimDocsAdd(rec,kind){
    var id=bimNewDocId();
    A3D_DOCS.docs.push({id:id,name:bimNameOf(rec.titleBlock),
      objs:Array.isArray(rec.objs)?rec.objs.length:0,saved:Date.now()});
    if(!bimDocsSwap(id,rec,null)){
      A3D_DOCS.docs=A3D_DOCS.docs.filter(function(e){return e.id!==id;});
      return null;
    }
    A3D_DOCS.open.push(id);
    bimDocsSave();
    bimDocsNotify(kind,id);
    return id;
  }
  function bimDocsCreate(){
    var rec=JSON.parse(A3D_PROJECT_DEFAULTS);
    rec.titleBlock.project=bimNextProjectName();
    var id=bimDocsAdd(rec,'create');
    if(id)a3dToast('New project: '+rec.titleBlock.project);
    return id;
  }
