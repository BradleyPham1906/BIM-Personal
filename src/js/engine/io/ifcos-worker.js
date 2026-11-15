import { A3D } from '../core/state.js';
import { meshOf } from '../core/mesh-primitives.js';
import { bimFileStem } from './project-file.js';
import { bimLayerById, bimLayerShown } from '../layers/layer-rules.js';
import { BIM_LB_PYODIDE, bimLbBase } from '../ladybug/runtime.js';
import { BIM_IFC_SAVE } from './ifc-save.js';
import { BIM_IFCOS_PY } from './ifcos-py.js';
import { bimProjectLabel } from '../ui/project-tabs.js';
import { a3dToast } from '../bim/csg-booleans.js';

/* ================= __acad3dV177: IfcOpenShell in a worker, and Save as IFC =================
   docs/research/research-ifcopenshell-app.md. IfcOpenShell 0.8.5's WebAssembly wheel, unchanged, run by the app's
   Pyodide in a Web Worker of its own, made the first time a model is saved as IFC: the app opens as fast as before
   and never waits on it. The wheel contains GPL code (CGAL), so it stays a separate program (the owner's D1): its
   own files under runtime/ifcos/ (runtime/MANIFEST.json, their NOTICE), fetched only here, reached only by this
   worker's messages; none of it is joined into the app. The worker checks each wheel's SHA-256 before unpacking
   it, then writes the app's adapter (src/py/bim_ifcos.py, embedded as BIM_IFCOS_PY) beside them. The model goes in
   as plain data (io/ifc-save.js) and the file's text comes back. */
  var BIM_IFCOS={dir:'ifcos/0.8.5/',mb:16,wheels:[
    {f:'six-1.17.0-py2.py3-none-any.whl',h:'bc830cfdc71a224b6d0e4337183a87ea53f21b6623deca5771ee3bc866fd8da2'},
    {f:'python_dateutil-2.9.0.post0-py2.py3-none-any.whl',h:'1fe3a0346ef21bc85b295227256d6aed72aa8116178b019fc5ae5d57fbd213cf'},
    {f:'typing_extensions-4.15.0-py3-none-any.whl',h:'42190f892f6219350c50e107954f57cb6196acac818fece4a7d21689c94f71de'},
    {f:'shapely-2.0.7-cp313-cp313-pyemscripten_2025_0_wasm32.whl',h:'586daa7290c2d309f9e8d14589d4aa940b1d84502defb3adecc23e17897e476d'},
    {f:'isodate-0.7.2-py3-none-any.whl',h:'28009937d8031054830160fce6d409ed342816b543597cece116d966c6d99e15'},
    {f:'lark-1.3.1-py3-none-any.whl',h:'c629b661023a014c37da873b4ff58a817398d12635d3bbb2c5a03be7fe5d1e12'},
    {f:'ifcopenshell-0.8.5-cp313-cp313-pyodide_2025_0_wasm32.whl',h:'fbebb7a7144277be213d156ed9b77de30de1d92b0b2b0c815e4a07555bfb929c'}]};
  var BIM_IFCOS_BOOT_MS=240000,BIM_IFCOS_RUN_MS=300000;
  var A3D_IFCOS={w:null,st:'idle',err:'',seq:0,pend:{},boot:null,version:'',ms:null};
  /* the worker's whole program: it is made from this function's own text, so it reads nothing of the engine's */
  function bimIfcosWorkerMain(){
    var PY=null;
    function hex(buf){var a=new Uint8Array(buf),s='',i;for(i=0;i<a.length;i++)s+=('0'+a[i].toString(16)).slice(-2);return s;}
    function say(m){self.postMessage(m);}
    function boot(m){
      var t0=Date.now(),B=m.base;
      if(!(self.crypto&&self.crypto.subtle)){say({t:'fail',s:'This page cannot check IfcOpenShell\'s files (no secure context)'});return;}
      try{importScripts(B+m.pyodide+'pyodide.js');}catch(x){say({t:'fail',s:'The Python runtime could not be loaded from '+B+' ('+(x&&x.message||x)+')'});return;}
      if(typeof self.loadPyodide!=='function'){say({t:'fail',s:'The Python runtime at '+B+' did not start'});return;}
      self.loadPyodide({indexURL:B+m.pyodide}).then(function(py){
        PY=py;
        return py.loadPackage('numpy');
      }).then(function(){
        return Promise.all(m.wheels.map(function(w){
          return fetch(B+m.dir+w.f).then(function(r){if(!r.ok)throw new Error(w.f+': HTTP '+r.status);return r.arrayBuffer();})
            .then(function(buf){return self.crypto.subtle.digest('SHA-256',buf).then(function(h){
              if(hex(h)!==w.h)throw new Error(w.f+' does not match its SHA-256');
              return buf;});});
        }));
      }).then(function(bufs){
        var sp=PY.runPython('import site\nsite.getsitepackages()[0]');
        bufs.forEach(function(buf){PY.unpackArchive(buf,'wheel',{extractDir:sp});});
        PY.FS.writeFile(sp+'/bim_ifcos.py',m.py);
        var v=PY.runPython('import bim_ifcos, importlib.metadata\nimportlib.metadata.version("ifcopenshell")');
        say({t:'ready',ms:Date.now()-t0,version:String(v)});
      }).then(null,function(x){say({t:'fail',s:String(x&&x.message||x)});});
    }
    /* one call: the adapter's function by name, its arguments as JSON, its answer as JSON; and, when asked, a file
       it wrote read back as text and removed */
    function run(m){
      var r,text=null;
      try{
        if(!/^bim_ifcos_[a-z_]+$/.test(String(m.fn)))throw new Error('not an adapter function: '+m.fn);
        PY.globals.set('_bim_args',m.args);
        r=String(PY.runPython('import json, bim_ifcos\njson.dumps(getattr(bim_ifcos, "'+m.fn+'")(*json.loads(_bim_args)))'));
        if(m.read){
          try{text=PY.FS.readFile(m.read,{encoding:'utf8'});PY.FS.unlink(m.read);}catch(eR){text=null;}
        }
        say({t:'done',id:m.id,r:r,text:text});
      }catch(x){say({t:'err',id:m.id,s:String(x&&x.message||x)});}
    }
    self.onmessage=function(e){var m=e.data||{};if(m.t==='boot')boot(m);else if(m.t==='run'&&PY)run(m);};
  }
  /* the worker ended, and every call waiting on it told why; the next call starts a fresh one */
  function bimIfcosStop(s){
    var k,P=A3D_IFCOS.pend;
    try{if(A3D_IFCOS.w)A3D_IFCOS.w.terminate();}catch(eT){}
    A3D_IFCOS.w=null;A3D_IFCOS.boot=null;A3D_IFCOS.pend={};
    for(k in P)if(P.hasOwnProperty(k)){clearTimeout(P[k].timer);P[k].rej(new Error(s));}
    A3D_IFCOS.st='failed';A3D_IFCOS.err=s;
    console.warn('[BIM] IfcOpenShell: '+s);
  }
  function bimIfcosOnMessage(e){
    var m=e.data||{},p=A3D_IFCOS.pend[m.id];
    if(!p)return;
    clearTimeout(p.timer);delete A3D_IFCOS.pend[m.id];
    if(m.t==='done')p.res({r:m.r,text:m.text});else p.rej(new Error(m.s||'IfcOpenShell failed'));
  }
  /* IfcOpenShell, started once; a promise of it */
  function bimIfcosStart(){
    var w,s;
    if(A3D_IFCOS.boot)return A3D_IFCOS.boot;
    if(typeof Worker!=='function'||typeof Blob!=='function'||!window.URL||!URL.createObjectURL||typeof WebAssembly!=='object'){
      s='This browser cannot run IfcOpenShell: it has no Web Workers or no WebAssembly';
      A3D_IFCOS.st='failed';A3D_IFCOS.err=s;console.warn('[BIM] IfcOpenShell: '+s);
      return Promise.reject(new Error(s));
    }
    try{w=new Worker(URL.createObjectURL(new Blob(['('+bimIfcosWorkerMain.toString()+')();'],{type:'text/javascript'})));}
    catch(eW){
      s='The IfcOpenShell worker could not be made ('+eW+')';
      A3D_IFCOS.st='failed';A3D_IFCOS.err=s;console.warn('[BIM] IfcOpenShell: '+s);
      return Promise.reject(new Error(s));
    }
    A3D_IFCOS.w=w;A3D_IFCOS.st='loading';A3D_IFCOS.err='';
    A3D_IFCOS.boot=new Promise(function(res,rej){
      var timer=setTimeout(function(){var t='IfcOpenShell did not load in '+Math.round(BIM_IFCOS_BOOT_MS/1000)+' s from '+bimLbBase();bimIfcosStop(t);rej(new Error(t));},BIM_IFCOS_BOOT_MS);
      w.onmessage=function(e){
        var m=e.data||{};
        if(m.t==='ready'){
          clearTimeout(timer);
          A3D_IFCOS.st='ready';A3D_IFCOS.version=String(m.version||'');A3D_IFCOS.ms=m.ms;
          w.onmessage=bimIfcosOnMessage;
          res(true);
        }else if(m.t==='fail'){clearTimeout(timer);bimIfcosStop(String(m.s||'IfcOpenShell failed to start'));rej(new Error(A3D_IFCOS.err));}
      };
      w.onerror=function(e){clearTimeout(timer);var t='The IfcOpenShell worker failed ('+(e&&e.message||'no message')+')';bimIfcosStop(t);rej(new Error(t));};
      w.postMessage({t:'boot',base:bimLbBase(),pyodide:'pyodide/'+BIM_LB_PYODIDE+'/',dir:BIM_IFCOS.dir,wheels:BIM_IFCOS.wheels,py:BIM_IFCOS_PY});
    });
    return A3D_IFCOS.boot;
  }
  /* one call into the adapter: its function's name and its arguments (a list); read names a file the function
     wrote, to be handed back as text. A promise of {r: the answer's object, text} */
  function bimIfcosCall(fn,args,read){
    return bimIfcosStart().then(function(){
      return new Promise(function(res,rej){
        var id=++A3D_IFCOS.seq;
        A3D_IFCOS.pend[id]={res:res,rej:rej,timer:setTimeout(function(){
          delete A3D_IFCOS.pend[id];rej(new Error('IfcOpenShell\'s '+fn+' did not finish in '+Math.round(BIM_IFCOS_RUN_MS/1000)+' s'));},BIM_IFCOS_RUN_MS)};
        A3D_IFCOS.w.postMessage({t:'run',id:id,fn:fn,args:JSON.stringify(args||[]),read:read||null});
      });
    }).then(function(A){
      var r;
      try{r=JSON.parse(A.r);}catch(eP){throw new Error('IfcOpenShell\'s '+fn+' answered something unreadable');}
      return {r:r,text:A.text};
    });
  }
  /* what is saved: every element shown that has a shape, and the doors' and windows' markers; with its mesh and
     its layer's name */
  function bimIfcExportEntries(){
    var out=[],i,o,m,ly;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimLayerShown(o))continue;
      m=o.t==='opening'?null:meshOf(o);
      if(o.t!=='opening'&&!(m&&m.f&&m.f.length&&m.v&&m.v.length))continue;
      ly=bimLayerById(o.layer);
      out.push({o:o,mesh:m,layer:ly?String(ly.name):''});
    }
    return out;
  }
  /* the model as an IFC file's text; a promise of {text, written, left, summary, ms}: left is what was not written,
     [{id, why}], from the app's side and from IfcOpenShell's */
  function bimIfcExportText(){
    var E=bimIfcExportEntries(),R,t0=Date.now();
    if(typeof BIM_IFC_SAVE.model!=='function')return Promise.reject(new Error('this build cannot write IFC yet'));
    if(!E.length)return Promise.reject(new Error('There is nothing shown to export'));
    R=BIM_IFC_SAVE.model(bimProjectLabel(),A3D.levels,E);
    return bimIfcosCall('bim_ifcos_export',[R.model,'/tmp/model.ifc'],'/tmp/model.ifc').then(function(A){
      if(!A.r||A.r.error)throw new Error('IfcOpenShell could not write the file ('+((A.r&&A.r.error)||'no answer')+')');
      if(!A.text)throw new Error('IfcOpenShell wrote no file');
      return {text:A.text,written:A.r.written,left:R.left.concat(A.r.skipped||[]),summary:A.r.summary,ms:Date.now()-t0};
    });
  }
  /* File, Export, IFC */
  function bimIfcExport(){
    a3dToast(A3D_IFCOS.st==='ready'?'Writing the model as IFC...':'Writing the model as IFC (the first time loads IfcOpenShell, about '+BIM_IFCOS.mb+' MB)...');
    return bimIfcExportText().then(function(R){
      var a=document.createElement('a'),url=URL.createObjectURL(new Blob([R.text],{type:'application/x-step'})),i;
      a.href=url;a.download=bimFileStem()+'.ifc';
      document.body.appendChild(a);a.click();document.body.removeChild(a);
      setTimeout(function(){URL.revokeObjectURL(url);},4000);
      for(i=0;i<R.left.length;i++)console.warn('[BIM] IFC export: '+R.left[i].id+' was not written: '+R.left[i].why);
      a3dToast('Saved '+a.download+': '+R.written+' element'+(R.written===1?'':'s')+', '+Math.max(1,Math.round(R.text.length/1024))+' KB'+
        (R.left.length?'; '+R.left.length+' not written (the console lists them)':''));
      return R;
    },function(e){
      var s=String(e&&e.message||e);
      console.warn('[BIM] IFC export failed: '+s,e);
      a3dToast('IFC export failed: '+s);
      return {error:s};
    });
  }
export { A3D_IFCOS, bimIfcExport, bimIfcExportText };
