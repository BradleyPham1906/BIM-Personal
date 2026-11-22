import { A3D } from '../core/state.js';
import { pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { paint } from '../map/terrain-3d.js';
import { fitScene } from '../ui/tool-palette.js';
import { refreshHud, saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV270: IGES import, through occt-import-js =================
     The owner's approval, 2026-11-22: "Yes". occt-import-js 0.0.23 (LGPL-2.1) is OpenCASCADE's IGES reader as
     WebAssembly, pinned at runtime/occt-import/<ver>/ as its own unchanged files (tools/occt/build_occt_import.mjs) and
     loaded only when an IGES file is imported. This file is the only one that calls it.
     The reader triangulates what it reads; the app takes it in metres (the file's own unit converted by OpenCASCADE),
     turned from IGES's Z up to the app's y up ((X, Y, Z) to (x, y, z) = (X, Z, -Y)), as one mesh object, its faces
     kept apart as the file has them. A closed one becomes a true solid with MESHTOSOLID (V271), which welds them.
     The conversion is pure, tested with the pinned reader in Node on an IGES file of our own
     (docs/research/experiments/v270-iges). */
  var BIM_IGES={ver:'0.0.23',dir:'occt-import/0.0.23/',file:'occt-import-js.js',sri:'sha256-P7RM4R0AYR+bPzxXddUg66tIkwwfCCebexMW8F8NM3k='};
  var A3D_IGES={load:null,st:'',err:''};
  function bimIgesLoad(){
    var R=A3D_IGES;
    if(R.load)return R.load;
    var p=String(window.location&&window.location.protocol||''),src=[],i=0;
    if(p!=='http:'&&p!=='https:')src.push({b:'runtime/',sri:false});
    src.push({b:String(bimLbBase()),sri:true});
    R.st='loading';
    R.load=new Promise(function(res,rej){
      function start(base){
        window.occtimportjs({locateFile:function(f){return new URL(base+BIM_IGES.dir+f,document.baseURI).href;}}).then(res,function(e){rej(e);});
      }
      if(typeof window.occtimportjs==='function'){start(src[src.length-1].b);return;}
      function next(){
        if(i>=src.length){rej(new Error('the IGES reader could not be loaded from '+src.map(function(s){return s.b+BIM_IGES.dir;}).join(' or ')));return;}
        var s=src[i++],tag=document.createElement('script');
        tag.src=s.b+BIM_IGES.dir+BIM_IGES.file;
        if(s.sri){tag.integrity=BIM_IGES.sri;tag.crossOrigin='anonymous';}
        tag.onload=function(){if(typeof window.occtimportjs==='function')start(s.b);else next();};
        tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
        document.head.appendChild(tag);
      }
      next();
    }).then(function(M){R.st='ready';return M;},function(e){R.st='failed';R.err=String(e&&e.message||e);R.load=null;throw e;});
    return R.load;
  }
  /* The reader's result as one app mesh {v, f}, its colour, and the number of faces it had. Pure. */
  function bimIgesMesh(res){
    var v=[],f=[],col=null,i,k;
    if(!res||!res.success||!res.meshes)return null;
    for(i=0;i<res.meshes.length;i++){
      var m=res.meshes[i],P=m.attributes&&m.attributes.position&&m.attributes.position.array,I=m.index&&m.index.array,base=v.length;
      if(!P||!I)continue;
      for(k=0;k+2<P.length;k+=3)v.push([P[k],P[k+2],-P[k+1]]);
      for(k=0;k+2<I.length;k+=3)f.push([base+I[k],base+I[k+1],base+I[k+2]]);
      if(!col&&m.color&&m.color.length>=3)col='#'+[0,1,2].map(function(j){var c=Math.max(0,Math.min(255,Math.round(m.color[j]*255)));return (c<16?'0':'')+c.toString(16);}).join('');
    }
    return f.length?{mesh:{v:v,f:f},col:col,parts:res.meshes.length}:null;
  }
  function bimImportIGES(buf,name){
    if(A3D_IGES.st!=='ready')a3dToast('IGES: loading the reader (about 7.6 MB, the first time only)...');
    return bimIgesLoad().then(function(M){
      var res,r;
      try{res=M.ReadIgesFile(new Uint8Array(buf),{linearUnit:'meter',linearDeflectionType:'bounding_box_ratio',linearDeflection:0.001});}
      catch(e){console.warn('[BIM] IGES read failed:',e);a3dToast('IGES import failed: the file could not be read');return null;}
      r=bimIgesMesh(res);
      if(!r){a3dToast('IGES import: no surfaces in '+name);return null;}
      pushUndo();
      A3D.counts.solid=(A3D.counts.solid||0)+1;
      var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:String(name||'IGES').replace(/\.[^.]+$/,'').slice(0,60),
        col:r.col||'#b9c7d6',pos:[0,0,0],mesh:r.mesh,layer:A3D.activeLayer};
      A3D.objs.push(o);
      A3D.sel=o.id;A3D.sel2=null;A3D.selSet=[o.id];
      refreshTree();refreshHud();fitScene();paint();saveSoon();
      a3dToast('IGES import: '+name+' ('+r.parts+' surface(s), '+r.mesh.f.length+' triangles). MESHTOSOLID makes a closed one a true solid');
      return o;
    },function(e){a3dToast('IGES: '+(e&&e.message||e));return null;});
  }
export { bimImportIGES };
