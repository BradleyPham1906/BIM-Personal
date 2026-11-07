import { A3D_DOCS } from './state.js';
import { paint } from '../map/terrain-3d.js';
import { save3d, saveT, setSaveT } from './objects-save.js';
import { A3D_SPILL, A3D_STORE, bimSpillWhenIdle } from './idb-store.js';
import { bimDocsNotify, bimLoadProjectRecord, bimProjectLabel } from '../ui/project-tabs.js';
import { bimProjectRead } from './project-store.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV172f: a project open in one tab opens read-only in a second (D7, the owner's F2) =================
     docs/research/research-local-storage.md, part 13. The tab with a project on screen holds a Web Lock named for it.
     Another tab asking with ifAvailable is answered null and shows the project read-only: it can be looked at and
     changed, nothing is saved over the stored project (AutoCAD's read-only), Save to a file still works. Take over asks
     the holder over BroadcastChannel to write what it has and let go, then waits for the lock; after 1.5 s it steals
     it, and the old holder, told by an AbortError, turns read-only itself. A lock goes when its tab reloads, closes or
     crashes (11 to 62 ms, measured, e14). Where navigator.locks is missing (before Chrome 69, Firefox 96, Safari 15.4)
     there is no read-only mode: the last save wins, as before. */
  var A3D_TAB={id:null,release:null,readOnly:false,why:'',told:false,bc:null,prefix:'BIM-Personal project '};
  function bimTabLocks(){
    try{return navigator.locks&&typeof navigator.locks.request==='function'?navigator.locks:null;}catch(eL){return null;}
  }
  function bimTabRelease(){
    var r=A3D_TAB.release;A3D_TAB.release=null;A3D_TAB.id=null;
    if(r)r();
  }
  /* hold the lock of project id: onGranted(true) when this tab has it, (false) when another tab holds it */
  function bimTabHold(id,opts,onGranted){
    var L=bimTabLocks(),got=false;
    if(!L){onGranted(true);return;}
    try{
      L.request(A3D_TAB.prefix+id,opts,function(lock){
        if(A3D_TAB.id!==id)return null;   /* switched away meanwhile: let go at once */
        if(!lock){onGranted(false);return null;}
        got=true;
        return new Promise(function(res){A3D_TAB.release=res;onGranted(true);});
      }).then(null,function(e){
        if(got&&e&&e.name==='AbortError'&&A3D_TAB.id===id){A3D_TAB.release=null;bimTabReadOnly(id,'taken');}
        else if(!got&&!(e&&e.name==='AbortError'))console.warn('[BIM] The project\'s lock could not be asked for.',e);
      });
    }catch(eR){console.warn('[BIM] The project\'s lock could not be asked for.',eR);onGranted(true);}
  }
  /* the project now on screen: its lock, or read-only */
  function bimTabClaim(id){
    bimTabRelease();
    A3D_TAB.readOnly=false;A3D_TAB.told=false;
    bimTabBar();
    if(!id||A3D_STORE.mode!=='idb'||!bimTabLocks())return;
    bimTabChannel();
    A3D_TAB.id=id;
    bimTabHold(id,{ifAvailable:true},function(mine){if(!mine)bimTabReadOnly(id,'open');});
  }
  function bimTabReadOnly(id,why){
    if(A3D_DOCS.active!==id)return;
    A3D_TAB.readOnly=true;A3D_TAB.why=why;A3D_TAB.told=false;
    if(saveT){clearTimeout(saveT);setSaveT(null);}
    if(A3D_SPILL.next&&A3D_SPILL.next.id===id)A3D_SPILL.next=null;
    bimTabBar();
    if(why==='taken')a3dToast('"'+bimProjectLabel()+'" was taken over in another tab: it is read-only here');
  }
  /* save3d's answer while read-only: said once per project */
  function bimTabReadOnlyEdit(){
    if(A3D_TAB.told)return;
    A3D_TAB.told=true;
    a3dToast('Not saved: "'+bimProjectLabel()+'" is open in another tab. Use Take over to edit it here, or Save to keep a copy as a file.');
  }
  /* run fn when no other tab holds project id, else busy */
  function bimTabIfFree(id,fn,busy){
    var L=bimTabLocks();
    if(!L){fn();return;}
    try{L.request(A3D_TAB.prefix+id,{ifAvailable:true},function(lock){if(lock)fn();else busy();return null;});}
    catch(eF){console.warn('[BIM] The project\'s lock could not be asked for.',eF);fn();}
  }
  function bimTabTakeOver(){
    var id=A3D_DOCS.active,L=bimTabLocks();
    if(!A3D_TAB.readOnly||!id||!L)return false;
    bimTabPost({t:'release',id:id});
    A3D_TAB.id=id;
    var done=false,ctl=typeof AbortController==='function'?new AbortController():null;
    function granted(mine){
      if(done||!mine)return;
      done=true;
      bimProjectRead(id,function(err,st){
        if(err||!st){a3dToast('"'+bimProjectLabel()+'" could not be read from the browser\'s database: it stays read-only');return;}
        try{
          bimLoadProjectRecord(st);
          A3D_SPILL.loading=false;A3D_TAB.readOnly=false;A3D_TAB.told=false;
          bimTabBar();paint();bimDocsNotify('activate',id);
          a3dToast('You can edit "'+bimProjectLabel()+'" here now; the other tab shows it read-only');
        }catch(eL){console.warn('[BIM] The project could not be loaded after taking it over.',eL);}
      });
    }
    bimTabHold(id,ctl?{signal:ctl.signal}:{},granted);
    setTimeout(function(){
      if(done)return;
      if(ctl)ctl.abort();
      bimTabHold(id,{steal:true},granted);
    },1500);
    return true;
  }
  /* another tab asks this one to let a project go: what is waiting is written, then the lock is released */
  function bimTabMessage(ev){
    var m=ev&&ev.data;
    if(!m||m.t!=='release'||m.id!==A3D_DOCS.active||A3D_TAB.readOnly||!A3D_TAB.release)return;
    if(saveT){clearTimeout(saveT);setSaveT(null);save3d();}
    A3D_TAB.readOnly=true;A3D_TAB.why='taken';A3D_TAB.told=false;
    bimSpillWhenIdle(function(){
      var r=A3D_TAB.release;A3D_TAB.release=null;
      if(r)r();
      bimTabBar();
      a3dToast('"'+bimProjectLabel()+'" was taken over in another tab: it is read-only here');
    });
  }
  function bimTabPost(m){try{if(A3D_TAB.bc)A3D_TAB.bc.postMessage(m);}catch(eP){console.warn('[BIM] The other tabs could not be told.',eP);}}
  /* the channel is opened with the first lock, so a page without Web Locks never opens one */
  function bimTabChannel(){
    if(A3D_TAB.bc)return;
    try{
      if(typeof BroadcastChannel==='function'){A3D_TAB.bc=new BroadcastChannel('BIM-Personal');A3D_TAB.bc.onmessage=bimTabMessage;}
    }catch(eB){A3D_TAB.bc=null;}
  }
  /* the bar over the drawing while read-only */
  function bimTabBar(){
    var b=document.getElementById('a3d-ro-bar');
    if(!A3D_TAB.readOnly){if(b&&b.parentNode)b.parentNode.removeChild(b);return;}
    if(!b){
      b=document.createElement('div');b.id='a3d-ro-bar';b.setAttribute('role','status');
      b.addEventListener('click',function(ev){var t=ev.target&&ev.target.closest?ev.target.closest('[data-a3dro]'):null;if(t)bimTabTakeOver();});
      document.body.appendChild(b);
    }
    b.innerHTML='<span>'+(A3D_TAB.why==='taken'?'Taken over in another tab':'Open in another tab')+': read-only here, changes are not saved</span>'+
      '<button type="button" data-a3dro="take">Take over</button>';
  }
  /* a read-only tab shows the latest saved state when it is looked at again */
  document.addEventListener('visibilitychange',function(){
    if(document.hidden||!A3D_TAB.readOnly||A3D_STORE.mode!=='idb')return;
    var id=A3D_DOCS.active;
    bimProjectRead(id,function(err,st){
      if(err||!st||A3D_DOCS.active!==id||!A3D_TAB.readOnly)return;
      try{bimLoadProjectRecord(st);paint();bimDocsNotify('activate',id);}
      catch(eL){console.warn('[BIM] The read-only project could not be refreshed.',eL);}
    });
  });
export { A3D_TAB, bimTabClaim, bimTabIfFree, bimTabReadOnlyEdit, bimTabTakeOver };
