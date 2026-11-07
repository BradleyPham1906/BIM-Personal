import { A3D_BOOT_IDB, A3D_BOOT_V2 } from './state.js';
import { A3D_SAVE_FAILED, save3d, saveT, setA3D_SAVE_FAILED, setSaveT } from './objects-save.js';
import { bimIndexTouch, bimJournalDrop } from './project-store.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV172d: the browser's database, for a project too large for localStorage =================
     docs/research/research-local-storage.md, phase A1. localStorage holds about 5.2 million characters for the whole
     origin (measured in Chromium, 2026-10-31), so an imported model of about 165,000 triangles could not be saved,
     and a project over half of it could not be switched away from. IndexedDB holds a share of the disk. A project
     record localStorage refuses goes to IndexedDB, and localStorage keeps a pointer in its place -- the record's id,
     name and count -- so the synchronous boot still knows which project it is and the list still names it. What
     fits stays where it was: a small project boots and switches exactly as before.
     One database named for the app (decision D10: every Pages project on the account shares the origin). ES5 and
     callbacks: the data API is events. A connection another tab's upgrade asks to close is closed (H10, measured);
     a connection the browser dropped is opened again once (idb-keyval, localForage). */
  var A3D_IDB_NAME='BIM-Personal',A3D_IDB_VERSION=2,A3D_IDB_PROJECTS='projects';
  /* __acad3dV172f: version 2 is the schema version (D10). Its store is version 1's, unchanged; the number keeps V172d and
     V172e copies -- an old tab, a file opened from disk -- out: they open version 1, are refused (VersionError) and save
     nothing over a pointer they cannot read (measured, e15 C). A later version refuses this one the same way, and this
     one says so. The store's mode: 'boot' until the database answers, then 'idb' (every project in it), 'migrating'
     while the older keys are copied, 'legacy' (the browser refuses its database: localStorage as before V172d), or
     'refused' (the projects are in a database this copy cannot open: nothing is saved over them). */
  var A3D_STORE={mode:'boot',v2:!!A3D_BOOT_V2,newer:false};
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
    req.onerror=function(){
      if(req.error&&req.error.name==='VersionError')A3D_STORE.newer=true;   /* __acad3dV172f */
      finish(req.error||new Error('The browser database could not be opened'),null);
    };
    req.onblocked=function(){
      console.warn('[BIM] The browser database is held open by another tab of the app.');
      a3dToast('Close the other tabs of this app so it can update its storage');
    };
  }
  /* one transaction on the projects store; done(err, value) once it has committed or failed -- always after the
     call has returned (__acad3dV172e: a refusal at once answered inside the call) */
  function bimIdbTx(mode,work,done,again,strict){
    bimIdbOpen(function(err,db){
      if(err){setTimeout(function(){done(err);},0);return;}
      var tx,out={},ended=false;
      function end(e,v){if(ended)return;ended=true;setTimeout(function(){done(e,v);},0);}
      try{tx=strict?db.transaction(A3D_IDB_PROJECTS,mode,{durability:'strict'}):db.transaction(A3D_IDB_PROJECTS,mode);}
      catch(eT){
        A3D_IDB.db=null;
        if(!again){bimIdbTx(mode,work,done,true,strict);return;}
        end(eT);return;
      }
      tx.oncomplete=function(){end(null,out.v);};
      tx.onabort=function(){end(tx.error||new Error('The browser database refused the change'));};
      try{
        work(tx.objectStore(A3D_IDB_PROJECTS),out);
        /* __acad3dV172f: committed at once, not when the results have been handled: a write started as the page goes
           away was lost at every reload without it, and kept with it (e13, e13b; IndexedDB 3.0, auto-commit) */
        if(mode==='readwrite'&&typeof tx.commit==='function')tx.commit();
      }
      catch(eW){try{tx.abort();}catch(eA){}end(eW);}
    });
  }
  function bimIdbPut(key,val,done){bimIdbTx('readwrite',function(s){s.put(val,key);},done);}
  function bimIdbGet(key,done){bimIdbTx('readonly',function(s,out){var r=s.get(key);r.onsuccess=function(){out.v=r.result;};},done);}
  function bimIdbDel(key,done){bimIdbTx('readwrite',function(s){s['delete'](key);},done);}
  /* __acad3dV172f: every key in the store; several values in one transaction, read or written (the migration's copy is
     written with durability 'strict', the case Chrome names for it) */
  function bimIdbKeys(done){bimIdbTx('readonly',function(s,out){var r=s.getAllKeys();r.onsuccess=function(){out.v=r.result||[];};},done);}
  function bimIdbGetMany(keys,done){
    bimIdbTx('readonly',function(s,out){
      out.v={};
      keys.forEach(function(k){var r=s.get(k);r.onsuccess=function(){out.v[k]=r.result;};});
    },done);
  }
  function bimIdbPutMany(map,done){
    bimIdbTx('readwrite',function(s){var k;for(k in map)if(map.hasOwnProperty(k))s.put(map[k],k);},done,false,true);
  }
  /* a V172d pointer: what acad3dV1 or a parked key held in place of a record the database kept */
  function bimIsIdbPointer(st){return !!(st&&typeof st==='object'&&st.idb===1&&typeof st.docId==='string'&&!Array.isArray(st.objs));}
  /* the projects' database copies: one write at a time, the newest of each waiting; the record in flight and the one
     waiting are what the pagehide journal keeps (core/project-store.js) */
  var A3D_SPILL={on:false,loading:!!A3D_BOOT_IDB,busy:false,next:null,inflight:null,dirty:false,idle:[],failed:{}};
  function bimSpillSave(id,s,rec){
    if(A3D_SPILL.busy){
      /* a waiting write of another project is written first, so no project's last state is dropped */
      if(A3D_SPILL.next&&A3D_SPILL.next.id!==id){var w=A3D_SPILL.next;A3D_SPILL.next=null;A3D_SPILL.idle.unshift(function(){bimSpillSave(w.id,w.s,w.rec);});}
      A3D_SPILL.next={id:id,s:s,rec:rec,saved:Date.now()};
      return;
    }
    A3D_SPILL.busy=true;
    var saved=Date.now();
    A3D_SPILL.inflight={id:id,s:s,saved:saved};
    bimIdbPut(id,{rec:s,saved:saved,v:1},function(err){
      A3D_SPILL.busy=false;A3D_SPILL.inflight=null;
      /* a record the database refused stays here for the session: reopening the project reads it first, the journal
         keeps it at pagehide, and the next save of the project tries again */
      if(err)A3D_SPILL.failed[id]={id:id,s:s,saved:saved};else delete A3D_SPILL.failed[id];
      if(err){
        if(!A3D_SAVE_FAILED){
          setA3D_SAVE_FAILED(true);
          console.warn('[BIM] The project could not be saved to the browser\'s database.',err);
          a3dToast('This project could not be saved: browser storage is full. Use Save to keep a copy as a file.');
        }
      }else{
        bimJournalDrop(id,Infinity);   /* only the tab holding the project writes its journal: confirmed, it goes */
        bimIndexTouch(id,rec,saved);
        if(A3D_SAVE_FAILED){setA3D_SAVE_FAILED(false);a3dToast('Saving to browser storage works again');}
      }
      var n=A3D_SPILL.next;A3D_SPILL.next=null;
      if(n){bimSpillSave(n.id,n.s,n.rec);return;}
      var q=A3D_SPILL.idle.splice(0,A3D_SPILL.idle.length),i;
      for(i=0;i<q.length;i++){try{q[i]();}catch(eQ){console.warn('[BIM] A step waiting on the database failed.',eQ);}}
    });
  }
  /* run fn once every write sent so far has been answered */
  function bimSpillWhenIdle(fn){if(!A3D_SPILL.busy&&!A3D_SPILL.next)fn();else A3D_SPILL.idle.push(fn);}
  /* decision D9: an autosave still waiting when the page is hidden is written then, while it can finish;
     pagehide cannot wait for the database */
  document.addEventListener('visibilitychange',function(){
    if(document.hidden&&saveT){clearTimeout(saveT);setSaveT(null);save3d();}
  });
export {
  A3D_SPILL, A3D_STORE, bimIdbDel, bimIdbGet, bimIdbGetMany, bimIdbKeys, bimIdbOpen, bimIdbPut, bimIdbPutMany,
  bimIsIdbPointer, bimSpillSave, bimSpillWhenIdle
};
