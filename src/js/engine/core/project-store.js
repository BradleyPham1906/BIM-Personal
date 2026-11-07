import {
  A3D, A3D_BOOT_IDB, A3D_DOCS, A3D_DOCS_KEY, A3D_DOC_PREFIX, A3D_JOURNAL_PREFIX, LSK
} from './state.js';
import { paint } from '../map/terrain-3d.js';
import { bimProjectRecord, save3d } from './objects-save.js';
import {
  A3D_SPILL, A3D_STORE, bimIdbGet, bimIdbGetMany, bimIdbKeys, bimIdbOpen, bimIdbPut, bimIdbPutMany,
  bimIsIdbPointer
} from './idb-store.js';
import {
  bimDocEntry, bimDocsNotify, bimDocsSave, bimLoadProjectRecord, bimNameOf, bimNewDocId, bimProjectLabel
} from '../ui/project-tabs.js';
import {
  A3D_FAMLIB, A3D_FAMLIB_DIRTY, A3D_FAMLIB_LOADING, A3D_FAMLIB_RETIRE, bimSaveFamilyLibrary, setA3D_FAMLIB_IDB
} from '../assets/family-library.js';
import { bimTabClaim } from './tab-lock.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV172f: every project in the browser's database; the older keys copied, checked, retired =================
     docs/research/research-local-storage.md, part 13 (the owner's D1, D7, D9, D10; F2). At start the database is opened:
     - the projects are already in it (the index under acad3dProjectsV2): the index is reconciled with the database's
       keys, any older key found is read and kept (an older build or an old tab wrote it), and the project on screen
       is read, with its journal when that is newer;
     - they are not (a first start of this version): every project, template and the Assets library is copied from the
       older keys in one transaction, read back and compared, the index written, and only then each older key removed,
       if it still holds what was copied;
     - the browser refuses its database: projects stay in localStorage, as before V172d.
     A record the database has not yet confirmed when the page goes away is journaled to localStorage, synchronously:
     a database write started then was lost at 10 reloads in 10 without commit() and at the first write to a new
     database with it (e13, e13b); localStorage kept 10 in 10. */
  var A3D_OLD_TEMPLATE_PREFIX='acad3dTemplateV1:',A3D_OLD_LIBRARY_KEY='acad3dFamilyLibrary';

  /* ---- the journal ---- */
  function bimJournalRead(id){
    try{
      var j=JSON.parse(localStorage.getItem(A3D_JOURNAL_PREFIX+id)||'null');
      if(j&&typeof j.rec==='string'&&isFinite(j.saved))return j;
    }catch(eJ){console.warn('[BIM] A project\'s journal could not be read: '+id,eJ);}
    return null;
  }
  /* the journal wins only when it is newer than the database's record */
  function bimJournalNewer(v,j){return !!(j&&(!v||!(+v.saved>=+j.saved)));}
  function bimJournalDrop(id,saved){
    var j=bimJournalRead(id);
    if(j&&(saved==null||+j.saved<=+saved)){
      try{localStorage.removeItem(A3D_JOURNAL_PREFIX+id);}
      catch(eR){console.warn('[BIM] A project\'s journal could not be removed: '+id,eR);}
    }
  }
  /* pagehide: the record in flight and the one waiting, each under its project's own key. A record too large for what
     localStorage has left is not written: the database's commit() is then its only way */
  function bimJournalWrite(){
    if(A3D_STORE.mode!=='idb')return 0;
    var n=0;
    [A3D_SPILL.inflight,A3D_SPILL.next].forEach(function(x){
      if(!x||!x.id)return;
      try{localStorage.setItem(A3D_JOURNAL_PREFIX+x.id,JSON.stringify({id:x.id,saved:x.saved||Date.now(),rec:x.s}));n++;}
      catch(eW){console.warn('[BIM] The last change of a project could not be journaled as the page closed: '+x.id,eW);}
    });
    return n;
  }

  /* ---- one project's record: the database's, or its journal when newer ---- */
  function bimProjectRead(id,cb){
    bimIdbGet(id,function(err,v){
      var j=bimJournalRead(id),useJ=bimJournalNewer(v,j),s=null,st=null;
      if(useJ)s=j.rec;
      else if(v&&typeof v.rec==='string')s=v.rec;
      if(err&&!useJ){cb(err,null,false);return;}
      if(!useJ&&j)bimJournalDrop(id,v&&v.saved);
      if(s){try{st=JSON.parse(s);}catch(eJ){console.warn('[BIM] A stored project is not valid JSON: '+id,eJ);}}
      cb(null,st&&typeof st==='object'?st:null,useJ);
    });
  }

  /* ---- the index ---- */
  /* after a record has committed: its name, count and time in the list, written when they changed */
  function bimIndexTouch(id,rec,saved){
    if(A3D_STORE.mode!=='idb')return;
    var e=bimDocEntry(id);
    if(!e)return;
    var nm=bimNameOf(rec&&rec.titleBlock),n=rec&&Array.isArray(rec.objs)?rec.objs.length:0;
    var changed=e.name!==nm||e.objs!==n;
    e.name=nm;e.objs=n;e.saved=saved;
    if(changed)bimDocsSave();
  }
  /* a record kept from an older key has anything in it worth keeping; an older build writes an empty project under its
     keys at every start (e15 B), and that one is not kept */
  function bimRecordEmpty(r){
    if(!r||typeof r!=='object')return true;
    function n(a){return Array.isArray(a)?a.length:0;}
    var hist=r.history&&Array.isArray(r.history.commits)?r.history.commits.length:0;
    var site=r.site&&typeof r.site==='object'?Object.keys(r.site).filter(function(k){return k!=='name';}).length:0;
    var tb=r.titleBlock&&typeof r.titleBlock==='object'?['project','client','drawnBy','checkedBy'].filter(function(k){return String(r.titleBlock[k]||'').trim();}).length:0;
    var boards=r.pres&&Array.isArray(r.pres.boards)?r.pres.boards.length:0;
    return n(r.objs)+n(r.grids)+n(r.sheets)+n(r.views)+n(r.resultLayers)+n(r.classifications)+hist+site+tb+boards+
      (r.dataFeatures&&typeof r.dataFeatures==='object'?Object.keys(r.dataFeatures).length:0)+
      (n(r.levels)>1?1:0)+(n(r.layers)>1?1:0)+(n(r.buildings)>1?1:0)===0;
  }
  /* what the older keys hold, read synchronously */
  function bimLegacyScan(){
    var out={projects:[],pointers:[],templates:[],library:null,libPointer:null,list:null},keys=[],i,k,raw,st;
    try{for(i=0;i<localStorage.length;i++){k=localStorage.key(i);if(k!==null)keys.push(k);}}
    catch(eK){console.warn('[BIM] Browser storage could not be listed.',eK);return out;}
    keys.forEach(function(key){
      try{
        if(key===LSK||key.indexOf(A3D_DOC_PREFIX)===0){
          raw=localStorage.getItem(key);st=raw?JSON.parse(raw):null;
          if(!st||typeof st!=='object')return;
          var id=key===LSK?(typeof st.docId==='string'?st.docId:null):key.slice(A3D_DOC_PREFIX.length);
          if(bimIsIdbPointer(st))out.pointers.push({key:key,raw:raw,id:st.docId});
          else out.projects.push({key:key,raw:raw,st:st,id:id,active:key===LSK});
        }else if(key.indexOf(A3D_OLD_TEMPLATE_PREFIX)===0){
          out.templates.push({key:key,raw:localStorage.getItem(key),id:key.slice(A3D_OLD_TEMPLATE_PREFIX.length)});
        }else if(key===A3D_OLD_LIBRARY_KEY){
          raw=localStorage.getItem(key);st=raw?JSON.parse(raw):null;
          if(Array.isArray(st))out.library={key:key,raw:raw,arr:st};
          else if(st&&st.idb===1)out.libPointer={key:key,raw:raw};
        }else if(key===A3D_DOCS_KEY){
          out.list={key:key,raw:localStorage.getItem(key)};
        }
      }catch(eS){console.warn('[BIM] An older stored entry could not be read: '+key,eS);}
    });
    return out;
  }
  /* remove an older key only while it still holds what was copied from it */
  function bimRetire(key,raw){
    try{if(localStorage.getItem(key)===raw)localStorage.removeItem(key);}
    catch(eR){console.warn('[BIM] An older stored entry could not be removed: '+key,eR);}
  }
  function bimStoreToast(msg){a3dToast(msg);}
  function bimStoreFlushDirty(){
    if(A3D_SPILL.dirty&&!A3D_SPILL.loading){A3D_SPILL.dirty=false;save3d();}
    if(A3D_FAMLIB_DIRTY&&!A3D_FAMLIB_LOADING)bimSaveFamilyLibrary();
  }

  /* ---- the project on screen, read after start ---- */
  function bimStoreLoadActive(done){
    var id=A3D_DOCS.active;
    if(!A3D_SPILL.loading){done();return;}
    /* the index named a project its list no longer has: a fresh one is on screen, nothing to read */
    if(!A3D_BOOT_IDB||A3D_BOOT_IDB!==id){A3D_SPILL.loading=false;done();return;}
    bimProjectRead(id,function(err,st,fromJournal){
      if(err||!st||A3D_DOCS.active!==id){
        if(err)console.warn('[BIM] The browser\'s database could not be read.',err);
        bimStoreToast('This project is kept in the browser\'s database, which could not be read: nothing is saved over it. Open a saved file or start a new project.');
        done();return;
      }
      try{
        bimLoadProjectRecord(st);
        A3D_SPILL.loading=false;
        var ent=bimDocEntry(id);
        if(ent){ent.name=bimProjectLabel();ent.objs=A3D.objs.length;}
        paint();
        bimDocsNotify('activate',id);
        if(fromJournal)save3d();   /* the journal's record goes into the database, and the journal goes once it has */
      }catch(eL){
        console.warn('[BIM] The project from the browser\'s database could not be loaded.',eL);
        bimStoreToast('This project is kept in the browser\'s database and could not be loaded: nothing is saved over it.');
      }
      done();
    });
  }

  /* ---- the projects already in the database ---- */
  function bimStoreOpenV2(){
    A3D_STORE.mode='idb';A3D_SPILL.on=true;
    bimIdbKeys(function(err,keys){
      keys=err?null:(keys||[]);
      if(keys)bimStoreReconcile(keys);
      bimStoreFoundLater(keys||[],function(){
        bimStoreLoadActive(function(){
          if(keys)bimJournalSweep(keys);
          bimStoreFlushDirty();
          bimTabClaim(A3D_DOCS.active);
          bimDocsSave();
          bimDocsNotify('list',null);
        });
      });
    });
  }
  /* the index is a cache of what the database holds (V115's rule for the keys): a project the index lost is listed
     again, an entry with nothing behind it dropped -- the project on screen excepted, whose record may be its first */
  function bimStoreReconcile(keys){
    var proj=keys.filter(function(k){return typeof k==='string'&&k.indexOf('tpl:')!==0&&k.indexOf('lib:')!==0;});
    var have={},changed=false;
    A3D_DOCS.docs=A3D_DOCS.docs.filter(function(d){
      if(proj.indexOf(d.id)>=0||d.id===A3D_DOCS.active||bimJournalRead(d.id)){have[d.id]=1;return true;}
      console.warn('[BIM] A project in the list has nothing stored behind it and is dropped: '+(d.name||d.id));
      changed=true;return false;
    });
    A3D_DOCS.open=A3D_DOCS.open.filter(function(id){return have[id];});
    proj.forEach(function(k){
      if(have[k])return;
      console.warn('[BIM] A stored project was missing from the project list and is listed again: '+k);
      var e={id:k,name:'Recovered project',objs:0,saved:0};
      A3D_DOCS.docs.push(e);changed=true;
      bimIdbGet(k,function(eG,v){
        var r=null;
        try{r=v&&typeof v.rec==='string'?JSON.parse(v.rec):null;}catch(eJ){r=null;}
        if(r){e.name=bimNameOf(r.titleBlock);e.objs=Array.isArray(r.objs)?r.objs.length:0;e.saved=+v.saved||0;bimDocsSave();bimDocsNotify('list',null);}
      });
    });
    if(changed)bimDocsSave();
  }
  /* a journal left by a tab that closed: written into the database when newer, then removed */
  function bimJournalSweep(keys){
    var ks=[],i,k;
    try{for(i=0;i<localStorage.length;i++){k=localStorage.key(i);if(k&&k.indexOf(A3D_JOURNAL_PREFIX)===0)ks.push(k.slice(A3D_JOURNAL_PREFIX.length));}}
    catch(eK){return;}
    ks.forEach(function(id){
      if(id===A3D_DOCS.active)return;   /* the one on screen was read with its journal */
      bimIdbGet(id,function(err,v){
        var j=bimJournalRead(id);
        if(err||!j)return;
        if(!bimJournalNewer(v,j)){bimJournalDrop(id,v.saved);return;}
        bimIdbPut(id,{rec:j.rec,saved:j.saved,v:1},function(eP){
          if(eP){console.warn('[BIM] A journaled change could not be written to the browser\'s database: '+id,eP);return;}
          bimJournalDrop(id,j.saved);
          if(!bimDocEntry(id)){
            var r=null;try{r=JSON.parse(j.rec);}catch(eJ){}
            A3D_DOCS.docs.push({id:id,name:bimNameOf(r&&r.titleBlock),objs:r&&Array.isArray(r.objs)?r.objs.length:0,saved:j.saved});
            bimDocsSave();bimDocsNotify('list',null);
          }
        });
      });
    });
  }
  /* older keys found once the projects are in the database: written by an older build or a tab opened before the
     update. A project with anything in it is kept -- under its own id, or a new one when that id holds a different
     record -- and an empty one dropped; templates and the library's entries are added; each key removed once its copy
     has committed */
  function bimStoreFoundLater(keys,done){
    var L=bimLegacyScan(),puts={},adds=[],tplIds=[],libAdd=null,retire=[],copied=[];
    L.projects.forEach(function(p){
      if(bimRecordEmpty(p.st)){bimRetire(p.key,p.raw);return;}
      var id=p.id;
      if(!id||bimDocEntry(id)||keys.indexOf(id)>=0||puts[id]){
        id=bimNewDocId();
        if(!p.st.titleBlock||typeof p.st.titleBlock!=='object')p.st.titleBlock={project:'',client:'',drawnBy:'',checkedBy:''};
        p.st.titleBlock.project=bimNameOf(p.st.titleBlock)+' (saved by an older version)';
      }
      p.st.docId=id;
      puts[id]={rec:JSON.stringify(p.st),saved:Date.now(),v:1};
      adds.push({id:id,name:bimNameOf(p.st.titleBlock),objs:Array.isArray(p.st.objs)?p.st.objs.length:0,saved:Date.now()});
      copied.push(p);
    });
    L.pointers.forEach(function(p){retire.push(p);});   /* their records are in the database, listed by the keys */
    L.templates.forEach(function(p){
      if(keys.indexOf('tpl:'+p.id)<0)puts['tpl:'+p.id]={rec:p.raw,saved:Date.now(),v:1};
      tplIds.push(p.id);copied.push(p);
    });
    if(L.library)libAdd=L.library;
    if(L.libPointer)retire.push(L.libPointer);
    if(L.list)retire.push(L.list);
    var n=Object.keys(puts).length;
    function after(){
      retire.concat(copied).forEach(function(p){bimRetire(p.key,p.raw);});
      if(libAdd){bimLibraryAdopt(libAdd.arr,tplIds);A3D_FAMLIB_RETIRE.push(libAdd);}
      else if(tplIds.length)bimLibraryAdopt([],tplIds);
      if(adds.length){
        adds.forEach(function(a){A3D_DOCS.docs.push(a);});
        bimDocsSave();
        bimStoreToast(adds.length===1?'A project saved by an older version of the app was added: "'+adds[0].name+'"':adds.length+' projects saved by an older version of the app were added');
      }
      done();
    }
    if(!n){after();return;}
    bimIdbPutMany(puts,function(err){
      if(err){
        console.warn('[BIM] Projects saved by an older version could not be copied into the browser\'s database; they stay where they are.',err);
        copied=[];adds=[];tplIds=[];libAdd=null;
      }
      after();
    });
  }
  /* library entries from an older key, added to the library (its own entries win by id); templates whose records were
     copied are marked as kept in the database */
  function bimLibraryAdopt(arr,tplIds){
    var have={},add=[];
    A3D_FAMLIB.forEach(function(e){if(e&&e.id)have[e.id]=1;});
    (arr||[]).forEach(function(e){if(e&&e.id&&!have[e.id]){have[e.id]=1;add.push(e);}});
    Array.prototype.push.apply(A3D_FAMLIB,add);
    A3D_FAMLIB.forEach(function(e){if(e&&tplIds.indexOf(e.id)>=0)e.idb=1;});
    bimSaveFamilyLibrary();
  }

  /* ---- a first start of this version: the older keys copied, checked, retired ---- */
  function bimStoreMigrate(){
    A3D_STORE.mode='migrating';
    var L=bimLegacyScan(),puts={},now=Date.now(),retire=[],tplIds=[],nP=0,i;
    /* the project on screen from memory (what localStorage held, and any edit since); not one still to be read */
    if(!A3D_BOOT_IDB){
      var rec=bimProjectRecord();rec.docId=A3D_DOCS.active;
      puts[A3D_DOCS.active]={rec:JSON.stringify(rec),saved:now,v:1};nP++;
    }
    L.projects.forEach(function(p){
      if(p.active){retire.push(p);return;}
      if(!bimDocEntry(p.id))A3D_DOCS.docs.push({id:p.id,name:bimNameOf(p.st.titleBlock),objs:Array.isArray(p.st.objs)?p.st.objs.length:0,saved:now});
      puts[p.id]={rec:p.raw,saved:now,v:1};nP++;retire.push(p);
    });
    L.pointers.forEach(function(p){retire.push(p);});
    L.templates.forEach(function(p){puts['tpl:'+p.id]={rec:p.raw,saved:now,v:1};tplIds.push(p.id);retire.push(p);});
    if(L.library){puts['lib:family']={rec:L.library.raw,saved:now,v:1};retire.push(L.library);}
    if(L.libPointer)retire.push(L.libPointer);
    if(L.list)retire.push(L.list);
    var keys=Object.keys(puts);
    function failed(why,e){
      console.warn('[BIM] The projects could not be moved into the browser\'s database ('+why+'); they stay where they were.',e||'');
      bimStoreToast('Moving the projects into the browser\'s database did not check out ('+why+'): they stay where they were, and the move is tried again at the next start');
      A3D_STORE.mode='legacy';
      if(!A3D_BOOT_IDB)A3D_SPILL.loading=false;
      bimStoreFlushDirty();
    }
    bimIdbPutMany(puts,function(err){
      if(err){failed('the copy was refused',err);return;}
      bimIdbGetMany(keys,function(err2,got){
        if(err2){failed('the copy could not be read back',err2);return;}
        for(i=0;i<keys.length;i++){
          if(!got[keys[i]]||got[keys[i]].rec!==puts[keys[i]].rec){failed('a copy differed from what was copied: '+keys[i]);return;}
        }
        A3D_STORE.v2=true;A3D_STORE.mode='idb';A3D_SPILL.on=true;
        if(!bimDocsSave()){A3D_STORE.v2=false;failed('the index could not be written');return;}
        setA3D_FAMLIB_IDB(true);
        if(tplIds.length||!L.library&&!L.libPointer){
          A3D_FAMLIB.forEach(function(e){if(e&&tplIds.indexOf(e.id)>=0)e.idb=1;});
          if(!A3D_FAMLIB_LOADING&&(tplIds.length||A3D_FAMLIB.length))bimSaveFamilyLibrary();
        }
        retire.forEach(function(p){bimRetire(p.key,p.raw);});
        var nT=tplIds.length;
        bimStoreToast('Your projects are now kept in the browser\'s database ('+nP+' project'+(nP===1?'':'s')+
          (nT?', '+nT+' template'+(nT===1?'':'s'):'')+(L.library?', the Assets library':'')+'), each copy checked. Use Save to keep copies as files.');
        bimStoreLoadActive(function(){
          bimStoreFlushDirty();
          bimTabClaim(A3D_DOCS.active);
          bimDocsNotify('list',null);
        });
      });
    });
  }

  /* ---- start ---- */
  function bimStoreStart(){
    bimIdbOpen(function(err){
      if(err){
        if(A3D_STORE.v2){
          A3D_STORE.mode='refused';
          console.warn('[BIM] The browser\'s database that holds the projects could not be opened.',err);
          bimStoreToast(A3D_STORE.newer?
            'A newer version of the app has updated this browser\'s storage: this copy cannot open its projects and saves nothing over them. Open the newest version, or open a project file.':
            'The browser\'s database that holds your projects could not be opened: nothing is saved over them. Reload, or open a project file.');
          return;
        }
        A3D_STORE.mode='legacy';
        console.warn('[BIM] The browser refuses its database here; projects stay in its smaller storage.',err);
        if(A3D_BOOT_IDB){
          bimStoreToast('This project is kept in the browser\'s database, which could not be read: nothing is saved over it. Open a saved file or start a new project.');
          return;
        }
        bimStoreToast('This browser does not allow its database here: projects stay in its smaller storage (about 5 MB in all). Use Save to keep copies as files.');
        A3D_SPILL.loading=false;
        bimStoreFlushDirty();
        return;
      }
      if(A3D_STORE.v2)bimStoreOpenV2();else bimStoreMigrate();
    });
  }
  setTimeout(bimStoreStart,0);
export {
  bimIndexTouch, bimJournalDrop, bimJournalNewer, bimJournalWrite, bimLegacyScan, bimProjectRead,
  bimRecordEmpty, bimRetire
};
