import { save3d, saveT, setSaveT } from './objects-save.js';
import { A3D_SPILL, bimSpillWhenIdle } from './idb-store.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV172h: installable and offline =================
     docs/research/research-local-storage.md, part 15 (option C; the owner's Q1-Q7, 2026-11-08). The Pages site's page
     carries <meta name="a3d-sw" content="sw.js"> (tools/build_pwa.py writes it there only), so the one-file build, a
     file:// copy (no service worker there, part 4.4) and a build kept under v/ never register one.
     - The first time the worker takes over, "Ready to work offline", once in this browser.
     - A new build found while a page is open waits (H44: nothing but closing every tab of the old build lets it in).
       A bar says a new version is ready, with Reload and Later. Reload asks every open tab of the app whether it has
       work not yet in the browser's database (Q1, Q4: skipWaiting takes every tab at once, H45), and tells the worker to
       take over only when none has; each tab then writes what is waiting and reloads once. */
  var A3D_SW={reg:null,hadCtl:false,reloading:false,asking:false,later:false,bc:null,q:0,answers:null,tries:0};
  var A3D_SW_READY_KEY='acad3dOfflineReadyV1';
  var A3D_SW_CHANNEL='BIM-Personal offline';
  var A3D_SW_ASK_MS=400,A3D_SW_RETRY_MS=1000,A3D_SW_TRIES=8;

  /* should this page register the worker: the site's page, over https (or http on this machine), not under v/ */
  function bimSwWanted(loc,meta,hasSw){
    if(!meta||!hasSw||!loc)return false;
    var p=String(loc.protocol||''),h=String(loc.hostname||'');
    if(p!=='https:'&&!(p==='http:'&&/^(localhost|127\.0\.0\.1|\[::1\])$/.test(h)))return false;
    return !/\/v\/[^\/]+\//.test(String(loc.pathname||''));
  }
  /* work not yet in the browser's database (the owner's Q1): a save waiting for its debounce, or a record waiting,
     being written, or not yet confirmed */
  function bimSwUnsavedOf(pending,spill){
    return !!(pending||(spill&&(spill.dirty||spill.inflight||spill.next||spill.busy)));
  }
  function bimSwUnsaved(){return bimSwUnsavedOf(saveT,A3D_SPILL);}
  /* the tabs' answers: true when any has unsaved work */
  function bimSwAnyUnsaved(answers){
    for(var k in answers)if(answers.hasOwnProperty(k)&&answers[k])return true;
    return false;
  }

  function bimSwStart(){
    var meta=document.querySelector('meta[name="a3d-sw"]'),sw=navigator.serviceWorker;
    if(!bimSwWanted(window.location,meta,!!sw))return;
    A3D_SW.hadCtl=!!sw.controller;
    bimSwChannel();
    sw.addEventListener('controllerchange',bimSwControllerChange);
    try{
      sw.register(meta.getAttribute('content')||'sw.js').then(function(reg){
        A3D_SW.reg=reg;
        if(reg.waiting&&A3D_SW.hadCtl)bimSwBar(true);
        reg.addEventListener('updatefound',function(){
          var w=reg.installing;
          if(!w)return;
          w.addEventListener('statechange',function(){
            if(w.state==='installed'&&navigator.serviceWorker.controller)bimSwBar(true);
          });
        });
      },function(e){
        console.warn('[BIM] The app could not be set up to work offline.',e);
        a3dToast('This browser could not set the app up to work offline: it works online as before');
      });
    }catch(eR){
      console.warn('[BIM] The app could not be set up to work offline.',eR);
      a3dToast('This browser could not set the app up to work offline: it works online as before');
    }
  }
  /* a worker took over: the first one (nothing was in control) says the app works offline; a new build reloads */
  function bimSwControllerChange(){
    if(!A3D_SW.hadCtl){
      A3D_SW.hadCtl=true;
      var told=false;
      try{told=!!window.localStorage.getItem(A3D_SW_READY_KEY);}catch(eG){told=true;}
      if(!told){
        try{window.localStorage.setItem(A3D_SW_READY_KEY,'1');}catch(eS){}
        a3dToast('Ready to work offline: this app now opens without a connection');
      }
      return;
    }
    if(A3D_SW.reloading)return;
    A3D_SW.reloading=true;
    if(saveT){clearTimeout(saveT);setSaveT(null);save3d();}
    bimSpillWhenIdle(function(){window.location.reload();});
  }

  /* ---- the tabs, asked ---- */
  function bimSwChannel(){
    if(A3D_SW.bc)return;
    try{
      if(typeof BroadcastChannel!=='function')return;
      A3D_SW.bc=new BroadcastChannel(A3D_SW_CHANNEL);
      A3D_SW.bc.onmessage=function(ev){
        var m=ev&&ev.data;
        if(!m)return;
        if(m.t==='ask')A3D_SW.bc.postMessage({t:'answer',q:m.q,from:bimSwTabId(),unsaved:bimSwUnsaved()});
        else if(m.t==='answer'&&A3D_SW.answers&&m.q===A3D_SW.q)A3D_SW.answers[m.from]=!!m.unsaved;
      };
    }catch(eB){A3D_SW.bc=null;console.warn('[BIM] The other tabs could not be asked.',eB);}
  }
  function bimSwTabId(){
    if(!A3D_SW.tab)A3D_SW.tab=String(Date.now())+'-'+String(Math.random()).slice(2,8);
    return A3D_SW.tab;
  }
  /* Reload: every tab asked; the new build let in only when none has unsaved work, else asked again a moment later */
  function bimSwApply(){
    var reg=A3D_SW.reg;
    if(!reg||!reg.waiting){bimSwBar(false);return;}
    if(A3D_SW.asking)return;
    A3D_SW.asking=true;
    if(saveT){clearTimeout(saveT);setSaveT(null);save3d();}
    A3D_SW.q++;
    A3D_SW.answers={};
    A3D_SW.answers[bimSwTabId()]=false;
    try{if(A3D_SW.bc)A3D_SW.bc.postMessage({t:'ask',q:A3D_SW.q});}
    catch(eP){console.warn('[BIM] The other tabs could not be asked.',eP);}
    setTimeout(function(){
      A3D_SW.answers[bimSwTabId()]=bimSwUnsaved();
      var busy=bimSwAnyUnsaved(A3D_SW.answers);
      A3D_SW.answers=null;A3D_SW.asking=false;
      if(!busy){
        A3D_SW.tries=0;
        try{reg.waiting.postMessage({t:'skip'});}
        catch(eS){console.warn('[BIM] The new version could not be started.',eS);a3dToast('The new version could not be started: close every tab of the app and open it again');}
        return;
      }
      if(++A3D_SW.tries<A3D_SW_TRIES){
        bimSwBar(true,'Saving changes in an open tab before the new version starts...');
        setTimeout(bimSwApply,A3D_SW_RETRY_MS);
        return;
      }
      A3D_SW.tries=0;
      bimSwBar(true);
      a3dToast('A tab of the app still has changes being saved: Reload again once it has finished');
    },A3D_SW_ASK_MS);
  }

  /* ---- the bar ---- */
  function bimSwBar(show,text){
    var b=document.getElementById('a3d-sw-bar');
    if(!show||A3D_SW.later){if(b&&b.parentNode)b.parentNode.removeChild(b);return;}
    if(!b){
      b=document.createElement('div');b.id='a3d-sw-bar';b.setAttribute('role','status');
      b.addEventListener('click',function(ev){
        var t=ev.target&&ev.target.closest?ev.target.closest('[data-a3dsw]'):null;
        if(!t)return;
        if(t.getAttribute('data-a3dsw')==='later'){A3D_SW.later=true;bimSwBar(false);}
        else bimSwApply();
      });
      document.body.appendChild(b);
    }
    b.innerHTML='<span>'+(text||'A new version of the app is ready')+'</span>'+
      '<button type="button" data-a3dsw="reload">Reload</button>'+
      '<button type="button" data-a3dsw="later" class="a3d-sw-later">Later</button>';
  }

  try{
    if(document.readyState==='complete')bimSwStart();
    else window.addEventListener('load',bimSwStart);
  }catch(eStart){console.warn('[BIM] The offline set-up did not start.',eStart);}
export { A3D_SW, bimSwAnyUnsaved, bimSwApply, bimSwUnsaved, bimSwUnsavedOf, bimSwWanted };
