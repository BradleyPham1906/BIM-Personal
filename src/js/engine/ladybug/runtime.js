  /* ================= __acad3dV172b: Ladybug Tools in a worker =================
     reference/research-ladybug-weather-comfort.md. Ladybug Tools' own Python, unchanged, run by Pyodide 0.29.5
     (MPL-2.0) in a Web Worker made on first use: the app opens as fast as before and the drawing never waits on a
     calculation. The runtime is committed under runtime/ (runtime/MANIFEST.json) and served with the site: the
     multi-file app loads it from its own address, the one-file copy and the older versions kept under v/ from the
     Pages address. The worker checks each wheel's SHA-256 before unpacking it, then writes the app's adapter
     (bim_ladybug, src/py/) beside them. The zero-dependency contract's one written exception: these analyses, on
     demand. Pyodide 0.29.5, not 314: 314's loader refuses a classic worker, and only a classic worker can be driven
     by ES5 code. */
  var BIM_LB_PYODIDE='0.29.5';
  var BIM_LB_PAGES='https://bradleypham1906.github.io/BIM-Personal/runtime/';
  /* the four wheels, as runtime/MANIFEST.json pins them */
  var BIM_LB_WHEELS=[
    {f:'ladybug_geometry-1.35.7-py3-none-any.whl',h:'fd73bddbf611f6d523677dd855db0184191b882aba06c353e7032bf245c89139'},
    {f:'ladybug_core-0.44.63-py3-none-any.whl',h:'21d67827869f5f8d6dc726f452aa9186689f448d87bb7c83aae466d7905e9556'},
    {f:'ladybug_comfort-0.19.13-py3-none-any.whl',h:'227e246d0689cb6a7c25fd34169c84c154bcf7f244042b508bf86de35abb62e8'},
    {f:'click-8.3.3-py3-none-any.whl',h:'a2bf429bb3033c89fa4936ffb35d5cb471e3719e1f3c8a7c3fff0b8314305613'}];
  var BIM_LB_BOOT_MS=180000,BIM_LB_RUN_MS=180000;
  var A3D_LB={w:null,st:'idle',err:'',seq:0,pend:{},boot:null,versions:null,pyodide:null,base:null,ms:null,src:null};
  /* where the runtime is: the page's own folder over http(s); the Pages address from a file:// copy or an older
     version kept under v/ */
  function bimLbBase(){
    if(A3D_LB.base)return A3D_LB.base;
    var L=window.location,p=String(L&&L.protocol||''),path=String(L&&L.pathname||'');
    if(p!=='http:'&&p!=='https:')return BIM_LB_PAGES;
    if(/\/v\/[^\/]+\/[^\/]*$/.test(path))return BIM_LB_PAGES;
    return String(L.href).replace(/[?#].*$/,'').replace(/[^\/]*$/,'')+'runtime/';
  }
  /* the worker's whole program: it is made from this function's own text, so it reads nothing of the engine's */
  function bimLbWorkerMain(){
    var PY=null;
    function hex(buf){var a=new Uint8Array(buf),s='',i;for(i=0;i<a.length;i++)s+=('0'+a[i].toString(16)).slice(-2);return s;}
    function say(m){self.postMessage(m);}
    function boot(m){
      var t0=Date.now(),B=m.base;
      if(!(self.crypto&&self.crypto.subtle)){say({t:'fail',s:'This page cannot check the runtime\'s files (no secure context)'});return;}
      try{importScripts(B+m.dir+'pyodide.js');}catch(x){say({t:'fail',s:'The runtime could not be loaded from '+B+' ('+(x&&x.message||x)+')'});return;}
      if(typeof self.loadPyodide!=='function'){say({t:'fail',s:'The runtime at '+B+' did not start'});return;}
      self.loadPyodide({indexURL:B+m.dir}).then(function(py){
        PY=py;
        var sp=py.runPython('import site\nsite.getsitepackages()[0]');
        return Promise.all(m.wheels.map(function(w){
          return fetch(B+'wheels/'+w.f).then(function(r){if(!r.ok)throw new Error(w.f+': HTTP '+r.status);return r.arrayBuffer();})
            .then(function(buf){return self.crypto.subtle.digest('SHA-256',buf).then(function(h){
              if(hex(h)!==w.h)throw new Error(w.f+' does not match its SHA-256');
              return buf;});});
        })).then(function(bufs){
          bufs.forEach(function(buf){py.unpackArchive(buf,'wheel',{extractDir:sp});});
          py.FS.writeFile(sp+'/bim_ladybug.py',m.py);
          var v=py.runPython('import bim_ladybug\nbim_ladybug.versions()');
          say({t:'ready',ms:Date.now()-t0,versions:String(v),pyodide:py.version});
        });
      }).then(null,function(x){say({t:'fail',s:String(x&&x.message||x)});});
    }
    function run(m){
      try{
        (m.files||[]).forEach(function(f){PY.FS.writeFile(f.path,f.data);});
        PY.globals.set('_bim_req',m.req);
        say({t:'done',id:m.id,r:String(PY.runPython('import bim_ladybug\nbim_ladybug.handle(_bim_req)'))});
      }catch(x){say({t:'err',id:m.id,s:String(x&&x.message||x)});}
    }
    self.onmessage=function(e){var m=e.data||{};if(m.t==='boot')boot(m);else if(m.t==='run'&&PY)run(m);};
  }
  function bimLbFail(s){
    A3D_LB.st='failed';A3D_LB.err=s;
    console.warn('[BIM] Ladybug: '+s);
    return Promise.reject(new Error(s));
  }
  /* the worker ended, and every call waiting on it told why; the next call starts a fresh one */
  function bimLbStop(s){
    var k,P=A3D_LB.pend;
    try{if(A3D_LB.w)A3D_LB.w.terminate();}catch(eT){}
    A3D_LB.w=null;A3D_LB.boot=null;A3D_LB.src=null;A3D_LB.pend={};
    for(k in P)if(P.hasOwnProperty(k)){clearTimeout(P[k].timer);P[k].rej(new Error(s));}
    A3D_LB.st='failed';A3D_LB.err=s;
    console.warn('[BIM] Ladybug: '+s);
  }
  function bimLbOnMessage(e){
    var m=e.data||{},p=A3D_LB.pend[m.id];
    if(!p)return;
    clearTimeout(p.timer);delete A3D_LB.pend[m.id];
    if(m.t==='done')p.res(m.r);else p.rej(new Error(m.s||'The analysis failed'));
  }
  /* the runtime, started once; a promise of it */
  function bimLbStart(){
    if(A3D_LB.boot)return A3D_LB.boot;
    if(typeof Worker!=='function'||typeof Blob!=='function'||!window.URL||!URL.createObjectURL)
      return bimLbFail('This browser cannot run the Ladybug analyses: it has no Web Workers');
    if(typeof WebAssembly!=='object')return bimLbFail('This browser cannot run the Ladybug analyses: it has no WebAssembly');
    var w;
    try{w=new Worker(URL.createObjectURL(new Blob(['('+bimLbWorkerMain.toString()+')();'],{type:'text/javascript'})));}
    catch(eW){return bimLbFail('The Ladybug worker could not be made ('+eW+')');}
    A3D_LB.w=w;A3D_LB.st='loading';A3D_LB.err='';
    A3D_LB.boot=new Promise(function(res,rej){
      var timer=setTimeout(function(){var s='The Ladybug runtime did not load in '+Math.round(BIM_LB_BOOT_MS/1000)+' s from '+bimLbBase();bimLbStop(s);rej(new Error(s));},BIM_LB_BOOT_MS);
      w.onmessage=function(e){
        var m=e.data||{};
        if(m.t==='ready'){
          clearTimeout(timer);
          var v={};try{v=JSON.parse(m.versions)||{};}catch(eV){}
          A3D_LB.st='ready';A3D_LB.versions=v;A3D_LB.pyodide=String(m.pyodide||'');A3D_LB.ms=m.ms;
          w.onmessage=bimLbOnMessage;
          res(true);
        }else if(m.t==='fail'){clearTimeout(timer);bimLbStop(String(m.s||'The Ladybug runtime failed'));rej(new Error(A3D_LB.err));}
      };
      w.onerror=function(e){clearTimeout(timer);var s='The Ladybug worker failed ('+(e&&e.message||'no message')+')';bimLbStop(s);rej(new Error(s));};
      w.postMessage({t:'boot',base:bimLbBase(),dir:'pyodide/'+BIM_LB_PYODIDE+'/',wheels:BIM_LB_WHEELS,py:BIM_LB_PY});
    });
    return A3D_LB.boot;
  }
  /* one call into the adapter: fn and its arguments, and files written into the worker first ({path, data});
     the answer's object, or a rejection with its cause */
  function bimLbCall(fn,args,files){
    return bimLbStart().then(function(){
      return new Promise(function(res,rej){
        var id=++A3D_LB.seq;
        A3D_LB.pend[id]={res:res,rej:rej,timer:setTimeout(function(){
          delete A3D_LB.pend[id];rej(new Error('The Ladybug '+fn+' did not finish in '+Math.round(BIM_LB_RUN_MS/1000)+' s'));},BIM_LB_RUN_MS)};
        A3D_LB.w.postMessage({t:'run',id:id,req:JSON.stringify({fn:fn,args:args||{}}),files:files||[]});
      });
    }).then(function(txt){
      var r;
      try{r=JSON.parse(txt);}catch(eP){throw new Error('The Ladybug '+fn+' answered something unreadable');}
      if(r&&r.error){if(r.trace)console.warn('[BIM] Ladybug '+fn+':\n'+r.trace);throw new Error(r.error);}
      return r;
    });
  }
  /* the runtime's state in words, for a panel */
  function bimLbStateText(){
    if(A3D_LB.st==='ready')return 'Ladybug Tools ready (Pyodide '+A3D_LB.pyodide+', ladybug-core '+((A3D_LB.versions||{})['ladybug-core']||'')+')';
    if(A3D_LB.st==='loading')return 'Loading Ladybug Tools (about 13 MB, once)';
    if(A3D_LB.st==='failed')return 'Ladybug Tools could not start: '+A3D_LB.err;
    return 'Ladybug Tools loads when an analysis is first run (about 13 MB, once)';
  }
