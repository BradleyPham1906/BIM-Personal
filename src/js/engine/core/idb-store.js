  /* ================= __acad3dV172d: the browser's database, for a project too large for localStorage =================
     reference/research-local-storage.md, phase A1. localStorage holds about 5.2 million characters for the whole
     origin (measured in Chromium, 2026-10-31), so an imported model of about 165,000 triangles could not be saved,
     and a project over half of it could not be switched away from. IndexedDB holds a share of the disk. A project
     record localStorage refuses goes to IndexedDB, and localStorage keeps a pointer in its place -- the record's id,
     name and count -- so the synchronous boot still knows which project it is and the list still names it. What
     fits stays where it was: a small project boots and switches exactly as before.
     One database named for the app (decision D10: every Pages project on the account shares the origin). ES5 and
     callbacks: the data API is events. A connection another tab's upgrade asks to close is closed (H10, measured);
     a connection the browser dropped is opened again once (idb-keyval, localForage). */
  var A3D_IDB_NAME='BIM-Personal',A3D_IDB_VERSION=1,A3D_IDB_PROJECTS='projects';
  var A3D_IDB={db:null,waiting:null};
  function bimIdbOpen(cb){
    if(A3D_IDB.db){cb(null,A3D_IDB.db);return;}
    if(A3D_IDB.waiting){A3D_IDB.waiting.push(cb);return;}
    var waiting=A3D_IDB.waiting=[cb],req;
    function finish(err,db){
      A3D_IDB.waiting=null;
      for(var i=0;i<waiting.length;i++){
        try{waiting[i](err,db);}catch(eC){console.warn('[BIM] A browser database callback failed.',eC);}
      }
    }
    try{req=window.indexedDB.open(A3D_IDB_NAME,A3D_IDB_VERSION);}
    catch(eO){finish(eO||new Error('IndexedDB is not available'),null);return;}
    req.onupgradeneeded=function(){
      var db=req.result;
      if(!db.objectStoreNames.contains(A3D_IDB_PROJECTS))db.createObjectStore(A3D_IDB_PROJECTS);
    };
    req.onsuccess=function(){
      var db=req.result;
      db.onversionchange=function(){
        db.close();
        if(A3D_IDB.db===db)A3D_IDB.db=null;
        a3dToast('A newer version of the app has updated its storage in another tab: reload this page');
      };
      db.onclose=function(){if(A3D_IDB.db===db)A3D_IDB.db=null;};
      A3D_IDB.db=db;
      finish(null,db);
    };
    req.onerror=function(){finish(req.error||new Error('The browser database could not be opened'),null);};
    req.onblocked=function(){
      console.warn('[BIM] The browser database is held open by another tab of the app.');
      a3dToast('Close the other tabs of this app so it can update its storage');
    };
  }
  /* one transaction on the projects store; done(err, value) once it has committed or failed */
  function bimIdbTx(mode,work,done,again){
    bimIdbOpen(function(err,db){
      if(err){done(err);return;}
      var tx,out={},ended=false;
      function end(e,v){if(ended)return;ended=true;done(e,v);}
      try{tx=db.transaction(A3D_IDB_PROJECTS,mode);}
      catch(eT){
        A3D_IDB.db=null;
        if(!again){bimIdbTx(mode,work,done,true);return;}
        end(eT);return;
      }
      tx.oncomplete=function(){end(null,out.v);};
      tx.onabort=function(){end(tx.error||new Error('The browser database refused the change'));};
      try{work(tx.objectStore(A3D_IDB_PROJECTS),out);}
      catch(eW){try{tx.abort();}catch(eA){}end(eW);}
    });
  }
  function bimIdbPut(key,val,done){bimIdbTx('readwrite',function(s){s.put(val,key);},done);}
  function bimIdbGet(key,done){bimIdbTx('readonly',function(s,out){var r=s.get(key);r.onsuccess=function(){out.v=r.result;};},done);}
  function bimIdbDel(key,done){bimIdbTx('readwrite',function(s){s['delete'](key);},done);}
  /* the pointer localStorage keeps in a record's place */
  function bimIsIdbPointer(st){return !!(st&&typeof st==='object'&&st.idb===1&&typeof st.docId==='string'&&!Array.isArray(st.objs));}
  function bimIdbPointer(id,rec){
    return JSON.stringify({idb:1,docId:id,titleBlock:{project:bimNameOf(rec&&rec.titleBlock)},
      count:rec&&Array.isArray(rec.objs)?rec.objs.length:0,saved:Date.now()});
  }
  /* the active project's database copy: the newest record wins, one write at a time */
  var A3D_SPILL={on:!!A3D_BOOT_IDB,loading:!!A3D_BOOT_IDB,busy:false,next:null,told:false};
  function bimSpillToast(){
    if(A3D_SPILL.told)return;
    A3D_SPILL.told=true;
    a3dToast('This project is too large for quick browser storage: it is kept in the browser\'s database. Use Save to keep a copy as a file.');
  }
  function bimSpillSave(id,s,rec){
    if(A3D_SPILL.busy){A3D_SPILL.next={id:id,s:s,rec:rec};return;}
    A3D_SPILL.busy=true;
    bimIdbPut(id,{rec:s,saved:Date.now(),v:1},function(err){
      A3D_SPILL.busy=false;
      if(err){
        if(!A3D_SAVE_FAILED){
          A3D_SAVE_FAILED=true;
          console.warn('[BIM] The project could not be saved to browser storage or to the browser\'s database.',err);
          a3dToast('This project could not be saved: browser storage is full. Use Save to keep a copy as a file.');
        }
      }else{
        /* the pointer goes in only once the record it points to has committed */
        if(A3D_DOCS.active===id){
          try{localStorage.setItem(LSK,bimIdbPointer(id,rec));}
          catch(eP){console.warn('[BIM] The pointer to the project in the browser\'s database could not be stored.',eP);}
          if(!A3D_SPILL.on){A3D_SPILL.on=true;bimSpillToast();}
          if(A3D_SAVE_FAILED){A3D_SAVE_FAILED=false;a3dToast('Saving to browser storage works again');}
        }
      }
      var n=A3D_SPILL.next;A3D_SPILL.next=null;
      if(n)bimSpillSave(n.id,n.s,n.rec);
    });
  }
  /* a parked project too large for its own key: its pointer in the key, then the record into the database. The
     pointer may go first: while it is written, acad3dV1 still holds this project, and boot drops a parked copy of
     the project acad3dV1 names (V115), so a crash between the two loses nothing. */
  function bimParkInIdb(id,s,rec,key){
    try{localStorage.setItem(key,bimIdbPointer(id,rec));}
    catch(eK){console.warn('[BIM] The pointer to a parked project could not be stored: '+id,eK);return false;}
    /* a queued save of this project is older than what is parked now, and would be written after it */
    if(A3D_SPILL.next&&A3D_SPILL.next.id===id)A3D_SPILL.next=null;
    bimIdbPut(id,{rec:s,saved:Date.now(),v:1},function(err){
      if(err){
        console.warn('[BIM] A parked project could not be written to the browser\'s database: '+id,err);
        a3dToast('"'+bimNameOf(rec&&rec.titleBlock)+'" could not be stored: browser storage is full. Open it and use Save to keep a copy as a file.');
      }
    });
    return true;
  }
  /* boot: the project on screen is in the database; nothing saves until it is read, so the fresh project the
     page started with never takes its place */
  function bimSpillBootLoad(){
    var id=A3D_BOOT_IDB;
    bimIdbGet(id,function(err,v){
      var st=null;
      if(!err&&v&&typeof v.rec==='string'){
        try{st=JSON.parse(v.rec);}catch(eJ){console.warn('[BIM] The project in the browser\'s database is not valid JSON: '+id,eJ);}
      }
      if(!st||typeof st!=='object'||A3D_DOCS.active!==id){
        if(err)console.warn('[BIM] The browser\'s database could not be read.',err);
        a3dToast('This project is kept in the browser\'s database, which could not be read: nothing is saved over it. Open a saved file or start a new project.');
        return;
      }
      try{
        bimLoadProjectRecord(st);
        A3D_SPILL.loading=false;
        var ent=bimDocEntry(id);
        if(ent){ent.name=bimProjectLabel();ent.objs=A3D.objs.length;}
        paint();
        bimDocsNotify('activate',id);
      }catch(eL){
        console.warn('[BIM] The project from the browser\'s database could not be loaded.',eL);
        a3dToast('This project is kept in the browser\'s database and could not be loaded: nothing is saved over it.');
      }
    });
  }
  if(A3D_BOOT_IDB)setTimeout(bimSpillBootLoad,0);
  /* decision D9: an autosave still waiting when the page is hidden is written then, while it can finish;
     pagehide cannot wait for the database */
  document.addEventListener('visibilitychange',function(){
    if(document.hidden&&saveT){clearTimeout(saveT);saveT=null;save3d();}
  });
