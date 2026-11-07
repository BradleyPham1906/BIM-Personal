import { A3D, A3D_DOCS, A3D_NO_STORAGE } from '../core/state.js';
import { bimTriggerDownload } from '../annotation/annotation-pick.js';
import {
  A3D_PERSIST, bimAskPersist, bimBuildProjectEnvelope, bimFileStem, bimImportProjectFile, bimOpenProjectPicker
} from './project-file.js';
import { A3D_REV } from '../core/objects-save.js';
import { A3D_STORE, bimIdbDel, bimIdbGet, bimIdbPut } from '../core/idb-store.js';
import { bimDocEntry, bimDocName, bimDocsSave } from '../ui/project-tabs.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV172g: files as the real save =================
     docs/research/research-local-storage.md, part 14 (D2, D4, D5; the owner's G1-G5, 2026-11-07). The browser keeps a
     working copy; the file is the save. Each project's entry in the index says whether it is in a file: the file's name,
     how it got there (saved, opened, downloaded), its type, when, the file's own time where the browser tells it, and
     whether the project has changed since. Every edit passes saveSoon(), which tells bimFileTouch().
     Save, in Chrome and Edge (the File System Access pickers), writes to the project's own file again: permission asked
     within the click, the writable opened first (draw.io's order: the click's activation lasts 5 s), the file's time
     checked against the last save (a change made elsewhere is asked about, G4), the envelope written, and the project
     counted as saved only when close() resolves -- until then the file on disk is the old one (the standard; Chromium's
     .crswap). Elsewhere, a download. Save as offers the plain file first and the compressed one second (G3); the
     compressed file is made in a worker (G2: 2-13 ms of stall against 108-566 ms on the main thread, e17). */
  var A3D_FILE={busy:false,last:{},quietUntil:0,persisted:null,worker:null,workerFailed:false,jobs:{},job:0};
  var A3D_FILE_REMIND_MS=30*60*1000;   /* D2: the owner's 30 minutes of work not in a file */
  var A3D_FILE_GAP_MS=2*60*1000;       /* a pause longer than this between edits is not counted as work */
  var A3D_FILE_PICKER_ID='acad3d-projects';   /* the pickers remember this folder (letters, digits, - and _, at most 32) */
  /* picker types: each extension at most 16 characters with its dot (e16, the WICG report 84-90) */
  var A3D_FILE_TYPE_JSON={description:'Project file',accept:{'application/json':['.acad3d.json']}};
  var A3D_FILE_TYPE_GZ={description:'Compressed project file',accept:{'application/gzip':['.acad3d.json.gz']}};
  var A3D_FILE_HANDLE_PREFIX='lib:file:';   /* in the projects store; keys under lib: are not projects to V172f's reconcile either */

  function bimFilePickers(){
    return typeof window.showSaveFilePicker==='function'&&typeof window.showOpenFilePicker==='function';
  }
  function bimFileTypeOf(name){return /\.gz$/i.test(String(name||''))?'gz':'json';}
  function bimFileEntryNow(){return bimDocEntry(A3D_DOCS.active);}

  /* ---- the marker ---- */
  /* a project is "in a file" when its entry names one and it has not changed since; a project never saved to a file is
     marked once it holds anything */
  function bimFileState(e,objs){
    if(!e)return {kind:'none',text:''};
    if(e.fileName){
      if(e.unsaved)return {kind:'changed',text:'Changes not saved to '+e.fileName};
      var t=e.fileAt?new Date(e.fileAt):null,hm=t?(' at '+('0'+t.getHours()).slice(-2)+':'+('0'+t.getMinutes()).slice(-2)):'';
      return {kind:'saved',text:(e.fileVia==='opened'?'Opened from ':e.fileVia==='downloaded'?'Downloaded as ':'Saved to ')+e.fileName+hm};
    }
    if(e.unsaved||objs>0)return {kind:'unsaved',text:'Not saved to a file'};
    return {kind:'none',text:''};
  }
  function bimFileStatus(){
    var b=document.getElementById('a3d-stfile');
    if(!b||!A3D_FILE)return;
    var e=bimFileEntryNow(),s=bimFileState(e,A3D.objs.length);
    if(A3D_NO_STORAGE&&s.kind==='none'&&e)s={kind:'unsaved',text:'Not saved to a file'};
    b.hidden=(s.kind==='none');
    b.textContent=s.text;
    b.setAttribute('data-state',s.kind);
    b.title=s.kind==='saved'?'Save again (Ctrl+S)':'Save this project to a file (Ctrl+S)';
  }
  /* every edit: the project changed since its file; 30 minutes of such work, a reminder, then again after 30 more (D2);
     at the first edit of a project never saved to a file, where the browser has not agreed to keep the app's storage,
     one reminder (G1). The index is written only when the state changes, not at every edit. */
  function bimFileTouch(){
    if(!A3D_FILE)return;   /* an edit made while the engine is still starting, before this file's own code has run */
    var e=bimFileEntryNow(),now=Date.now(),id=A3D_DOCS.active,changed=false;
    if(!e||now<A3D_FILE.quietUntil)return;
    if(!e.unsaved){e.unsaved=1;e.work=0;e.told=0;changed=true;}
    var last=A3D_FILE.last[id]||0;
    if(last&&now-last<A3D_FILE_GAP_MS)e.work=(e.work||0)+(now-last);
    A3D_FILE.last[id]=now;
    if((e.work||0)-(e.told||0)>=A3D_FILE_REMIND_MS){
      e.told=e.work;changed=true;
      a3dToast('"'+bimDocName(id)+'" has 30 minutes of work not saved to a file. Use Save (Ctrl+S) to keep it.');
    }
    if(changed)bimDocsSave();
    if(!e.fileName&&!e.warned)bimFileFirstSave(id);
    bimFileStatus();
  }
  function bimFilePersisted(cb){
    if(A3D_PERSIST.granted===true)A3D_FILE.persisted=true;
    if(A3D_FILE.persisted!==null){cb(A3D_FILE.persisted);return;}
    try{
      if(!navigator.storage||typeof navigator.storage.persisted!=='function'){A3D_FILE.persisted=false;cb(false);return;}
      navigator.storage.persisted().then(function(p){A3D_FILE.persisted=!!p;cb(!!p);},function(err){
        console.warn('[BIM] The browser could not say whether it keeps this app\'s storage.',err);
        A3D_FILE.persisted=false;cb(false);
      });
    }catch(eP){console.warn('[BIM] The browser could not say whether it keeps this app\'s storage.',eP);A3D_FILE.persisted=false;cb(false);}
  }
  /* G1: Safari tabs and every private window never have persisted storage, so this covers both without guessing the
     browser (a private window cannot be told dependably: part 14, H37) */
  function bimFileFirstSave(id){
    if(A3D_NO_STORAGE)return;   /* that state has its own message (D5) */
    bimFilePersisted(function(p){
      var e=bimDocEntry(id);
      if(p||!e||e.warned||e.fileName)return;
      e.warned=1;bimDocsSave();
      a3dToast('This browser may clear its copy of your projects. Use Save (Ctrl+S) to keep "'+bimDocName(id)+'" as a file.');
    });
  }
  function bimFileMark(id,name,via,type,mod,rev){
    var e=bimDocEntry(id);
    if(!e)return;
    e.fileName=name;e.fileVia=via;e.fileType=type;e.fileAt=Date.now();
    if(typeof mod==='number')e.fileMod=mod;else delete e.fileMod;
    /* an edit made while the file was being written is not in it */
    if(rev===null||id!==A3D_DOCS.active||rev===A3D_REV){e.unsaved=0;e.work=0;e.told=0;A3D_FILE.last[id]=0;}
    bimDocsSave();
    bimFileStatus();
  }

  /* ---- the handles, kept beside the projects in the browser's database ---- */
  function bimFileHandleGet(id,cb){
    if(A3D_STORE.mode!=='idb'){cb(null);return;}
    bimIdbGet(A3D_FILE_HANDLE_PREFIX+id,function(err,v){
      if(err){console.warn('[BIM] The project\'s file could not be looked up.',err);cb(null);return;}
      cb(v&&typeof v.createWritable==='function'?v:null);
    });
  }
  function bimFileHandlePut(id,h){
    if(A3D_STORE.mode!=='idb')return;
    bimIdbPut(A3D_FILE_HANDLE_PREFIX+id,h,function(err){
      if(err){
        console.warn('[BIM] The project\'s file could not be remembered.',err);
        a3dToast('The browser could not remember this project\'s file: Save will ask where to save next time');
      }
    });
  }
  function bimFileHandleDrop(id){
    if(A3D_STORE.mode!=='idb')return;
    bimIdbDel(A3D_FILE_HANDLE_PREFIX+id,function(err){if(err)console.warn('[BIM] A project\'s file link could not be removed.',err);});
  }

  /* ---- the file's bytes ---- */
  var A3D_GZ_WORKER_SRC='self.onmessage=function(e){var d=e.data;function bad(x){self.postMessage({id:d.id,error:String(x&&x.message||x)});}'+
    'try{new Response(new Blob([new TextEncoder().encode(d.text)]).stream().pipeThrough(new CompressionStream("gzip"))).arrayBuffer()'+
    '.then(function(b){self.postMessage({id:d.id,buf:b},[b]);},bad);}catch(x){bad(x);}};';
  function bimGzipMain(text){
    return new Response(new Blob([new TextEncoder().encode(text)]).stream().pipeThrough(new CompressionStream('gzip')))
      .arrayBuffer().then(function(b){return new Uint8Array(b);});
  }
  function bimGzipWorker(){
    if(A3D_FILE.worker||A3D_FILE.workerFailed)return A3D_FILE.worker;
    try{
      var w=new Worker(URL.createObjectURL(new Blob([A3D_GZ_WORKER_SRC],{type:'text/javascript'})));
      w.onmessage=function(ev){
        var d=ev.data,j=A3D_FILE.jobs[d.id];
        if(!j)return;
        delete A3D_FILE.jobs[d.id];
        if(d.error)j.no(new Error(d.error));else j.ok(new Uint8Array(d.buf));
      };
      w.onerror=function(ev){
        console.warn('[BIM] The compression worker stopped; files are compressed on the page instead.',ev&&ev.message);
        A3D_FILE.workerFailed=true;A3D_FILE.worker=null;
        var k,jobs=A3D_FILE.jobs;A3D_FILE.jobs={};
        for(k in jobs)if(jobs.hasOwnProperty(k))bimGzipMain(jobs[k].text).then(jobs[k].ok,jobs[k].no);
      };
      A3D_FILE.worker=w;
    }catch(eW){
      console.warn('[BIM] A compression worker could not be made; files are compressed on the page instead.',eW);
      A3D_FILE.workerFailed=true;
    }
    return A3D_FILE.worker;
  }
  /* G2: in a worker, the page's own thread only where a worker cannot be made */
  function bimGzip(text){
    if(typeof CompressionStream!=='function')return Promise.reject(new Error('this browser cannot write compressed files; save as .acad3d.json'));
    var w=bimGzipWorker();
    if(!w)return bimGzipMain(text);
    return new Promise(function(ok,no){
      var id=++A3D_FILE.job;
      A3D_FILE.jobs[id]={ok:ok,no:no,text:text};
      w.postMessage({id:id,text:text});
    });
  }
  /* a damaged file is refused whole: truncation, trailing bytes and a second member are errors (part 14, H35) */
  function bimGunzip(u8){
    if(typeof DecompressionStream!=='function')return Promise.reject(new Error('this browser cannot read compressed files'));
    return new Response(new Blob([u8]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
  }
  function bimFileBytes(type){
    var json=bimBuildProjectEnvelope();
    if(type!=='gz')return Promise.resolve(new Blob([json],{type:'application/json'}));
    return bimGzip(json).then(function(u8){return new Blob([u8],{type:'application/gzip'});});
  }
  function bimFileName(type){return bimFileStem()+(type==='gz'?'.acad3d.json.gz':'.acad3d.json');}

  /* ---- a small question: the buttons it offers, the answer to cb ('cancel' on Escape or outside) ---- */
  function bimFileAsk(title,text,buttons,cb){
    var old=document.getElementById('a3d-filedlg');
    if(old&&old.parentNode)old.parentNode.removeChild(old);
    var d=document.createElement('div'),h='',i;
    d.id='a3d-filedlg';d.className='a3d-filedlg';
    d.setAttribute('role','dialog');d.setAttribute('aria-modal','true');d.setAttribute('aria-labelledby','a3d-filedlg-t');
    for(i=0;i<buttons.length;i++)h+='<button class="a3d-btn'+(buttons[i].pri?' a3d-btn-pri':'')+'" data-a3dfd="'+buttons[i].k+'">'+buttons[i].label+'</button>';
    d.innerHTML='<div class="a3d-filedlg-box"><div class="a3d-filedlg-t" id="a3d-filedlg-t"></div><div class="a3d-filedlg-x"></div>'+
      '<div class="a3d-filedlg-ft">'+h+'</div></div>';
    d.querySelector('.a3d-filedlg-t').textContent=title;
    d.querySelector('.a3d-filedlg-x').textContent=text;
    var done=false;
    function end(k){
      if(done)return;done=true;
      document.removeEventListener('keydown',key,true);
      if(d.parentNode)d.parentNode.removeChild(d);
      cb(k);
    }
    function key(ev){if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();end('cancel');}}
    d.addEventListener('click',function(ev){
      var b=ev.target.closest&&ev.target.closest('[data-a3dfd]');
      if(b){end(b.getAttribute('data-a3dfd'));return;}
      if(ev.target===d)end('cancel');
    });
    document.addEventListener('keydown',key,true);
    document.body.appendChild(d);
    var first=d.querySelector('.a3d-btn-pri')||d.querySelector('button');
    if(first)first.focus();
  }

  /* ---- Save and Save as ---- */
  function bimFileSave(asNew){
    if(A3D_FILE.busy){a3dToast('A save to a file is already under way');return false;}
    var e=bimFileEntryNow();
    if(!e){a3dToast('Open a project to save it');return false;}
    if(bimFilePickers()){bimFileSavePicked(A3D_DOCS.active,!!asNew);return true;}
    if(asNew){
      bimFileAsk('Save as','Save "'+bimDocName(A3D_DOCS.active)+'" as a plain project file, or compressed to about a third of the size.',
        [{k:'json',label:'Project file (.acad3d.json)',pri:true},{k:'gz',label:'Compressed (.acad3d.json.gz)'},{k:'cancel',label:'Cancel'}],
        function(k){if(k==='json'||k==='gz')bimFileDownload(A3D_DOCS.active,k);});
      return true;
    }
    bimFileDownload(A3D_DOCS.active,e.fileType||'json');
    return true;
  }
  /* where there is no save picker: a download, as before V172g; a browser cannot say where it went */
  function bimFileDownload(id,type){
    var rev=A3D_REV,name=bimFileName(type);
    A3D_FILE.busy=true;
    bimFileBytes(type).then(function(blob){
      A3D_FILE.busy=false;
      bimTriggerDownload(blob,name,type==='gz'?'application/gzip':'application/json');
      bimFileMark(id,name,'downloaded',type,null,rev);
      a3dToast('Project saved as '+name+' ('+A3D.objs.length+' object(s))');
      bimAskPersist();
    },function(err){
      A3D_FILE.busy=false;
      console.warn('[BIM] The project file could not be made.',err);
      a3dToast('The project file could not be made: '+(err&&err.message?err.message:err));
    });
  }
  function bimFileSavePicked(id,asNew){
    A3D_FILE.busy=true;
    function free(){A3D_FILE.busy=false;}
    function failed(what,err){
      free();
      console.warn('[BIM] '+what,err);
      a3dToast(what+': '+(err&&err.message?err.message:err));
    }
    function pick(){
      var t=(bimDocEntry(id)||{}).fileType==='gz'?'gz':'json';
      try{
        window.showSaveFilePicker({id:A3D_FILE_PICKER_ID,suggestedName:bimFileName(t),types:[A3D_FILE_TYPE_JSON,A3D_FILE_TYPE_GZ]})
          .then(function(h){write(h,true);},function(err){
            if(err&&err.name==='AbortError'){free();return;}
            if(err&&err.name==='SecurityError'){free();a3dToast('The browser asked for a fresh click: use Save as again');return;}
            failed('The save dialog could not be opened',err);
          });
      }catch(eS){failed('The save dialog could not be opened',eS);}
    }
    function write(h,isNew){
      var type=bimFileTypeOf(h.name),rev=A3D_REV,w=null;
      h.createWritable().then(function(ws){w=ws;rev=A3D_REV;return bimFileBytes(type);})
        .then(function(blob){return w.write(blob);})
        .then(function(){return w.close();})
        .then(function(){w=null;return h.getFile();})
        .then(function(f){
          free();
          if(isNew)bimFileHandlePut(id,h);
          bimFileMark(id,h.name,'saved',type,f.lastModified,rev);
          a3dToast('Saved to '+h.name+' ('+A3D.objs.length+' object(s))');
          bimAskPersist();
        },function(err){
          if(w){try{w.abort()['catch'](function(){});}catch(eA){console.warn('[BIM] An unfinished write could not be abandoned.',eA);}}
          free();
          console.warn('[BIM] The project could not be saved to '+h.name,err);
          a3dToast('Not saved to '+h.name+': '+(err&&err.message?err.message:err)+'. The file on disk is as it was.');
        });
    }
    function check(h){
      var e=bimDocEntry(id);
      h.getFile().then(function(f){
        if(e&&typeof e.fileMod==='number'&&f.lastModified!==e.fileMod){
          free();
          /* G4: the file was changed elsewhere since this project was last saved to it */
          bimFileAsk('The file has changed',h.name+' was changed outside this app after it was last saved here. Saving now replaces those changes.',
            [{k:'over',label:'Overwrite',pri:true},{k:'as',label:'Save as…'},{k:'cancel',label:'Cancel'}],
            function(k){
              if(k==='over'){A3D_FILE.busy=true;write(h,false);}
              else if(k==='as'){A3D_FILE.busy=true;pick();}
            });
          return;
        }
        write(h,false);
      },function(err){
        console.warn('[BIM] The project\'s file can no longer be found.',err);
        bimFileHandleDrop(id);
        a3dToast(h.name+' can no longer be found: choose where to save');
        pick();
      });
    }
    if(asNew){pick();return;}
    bimFileHandleGet(id,function(h){
      if(!h){pick();return;}
      var q;
      try{q=h.queryPermission({mode:'readwrite'});}catch(eQ){q=Promise.resolve('prompt');}
      q.then(function(s){return s==='granted'?s:h.requestPermission({mode:'readwrite'});})
        .then(function(s){
          if(s==='granted'){check(h);return;}
          a3dToast('Permission to write '+h.name+' was not given: choose where to save');
          pick();
        },function(err){
          console.warn('[BIM] Permission to write the project\'s file could not be asked.',err);
          pick();
        });
    });
  }

  /* ---- Open ---- */
  function bimFileOpen(){
    if(!bimFilePickers())return bimOpenProjectPicker();
    try{
      window.showOpenFilePicker({id:A3D_FILE_PICKER_ID,multiple:true,
        types:[{description:'Project file',accept:{'application/json':['.json'],'application/gzip':['.gz']}}]})
        .then(function(hs){
          hs.forEach(function(h){
            h.getFile().then(function(f){bimFileRead(f,h);},function(err){
              console.warn('[BIM] A project file could not be read: '+h.name,err);
              a3dToast('Failed to read '+h.name);
            });
          });
        },function(err){
          if(err&&err.name==='AbortError')return;
          console.warn('[BIM] The open dialog could not be shown; the file input is used instead.',err);
          bimOpenProjectPicker();
        });
    }catch(eO){
      console.warn('[BIM] The open dialog could not be shown; the file input is used instead.',eO);
      bimOpenProjectPicker();
    }
    return true;
  }
  /* a file is compressed when its first two bytes are 1F 8B (RFC 1952), whatever its name (D4) */
  function bimFileRead(file,handle){
    var name=file.name||'project.acad3d.json';
    var reader=new FileReader();
    reader.onerror=function(){console.warn('[BIM] A project file could not be read: '+name,reader.error);a3dToast('Failed to read '+name);};
    reader.onload=function(){
      var u8=new Uint8Array(reader.result),gz=u8.length>1&&u8[0]===0x1f&&u8[1]===0x8b;
      var text=gz?bimGunzip(u8):Promise.resolve(new TextDecoder('utf-8').decode(u8));
      text.then(function(t){
        var id=bimImportProjectFile(t,name);
        if(!id)return;
        A3D_FILE.quietUntil=Date.now()+600;
        if(handle)bimFileHandlePut(id,handle);
        bimFileMark(id,name,'opened',gz?'gz':'json',handle?file.lastModified:null,null);
      },function(err){
        console.warn('[BIM] A compressed project file could not be read: '+name,err);
        a3dToast(name+' is damaged or incomplete and was not opened: '+(err&&err.message?err.message:err));
      })['catch'](function(eI){
        console.warn('[BIM] Opening a project file crashed:',eI);
        a3dToast('Opening '+name+' failed: '+(eI&&eI.message?eI.message:eI));
      });
    };
    reader.readAsArrayBuffer(file);
  }

  /* opening, creating or switching a project is not an edit to it */
  window.addEventListener('a3ddocs',function(ev){
    var k=ev&&ev.detail?ev.detail.kind:'';
    if(k==='activate'||k==='open'||k==='create')A3D_FILE.quietUntil=Date.now()+600;
    if(k==='remove'&&ev.detail.id)bimFileHandleDrop(ev.detail.id);
    setTimeout(bimFileStatus,0);
  });
  /* the line is shown once the status bar is built */
  (function bimFileStatusBoot(n){
    if(document.getElementById('a3d-stfile')){bimFileStatus();return;}
    if(n<80)setTimeout(function(){bimFileStatusBoot(n+1);},250);
  })(0);
  /* the status bar's line runs Save, as draw.io's "Unsaved changes. Click here to save." does */
  document.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('#a3d-stfile');
    if(b){ev.preventDefault();bimFileSave(false);}
  });
export {
  bimFileDownload, bimFileOpen, bimFilePickers, bimFileRead, bimFileSave, bimFileState, bimFileTouch, bimGzip
};
