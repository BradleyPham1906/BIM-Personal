import { bimLbBase } from '../ladybug/runtime.js';
import { bimGltfFeatureEdges, bimGltfWeld } from './gltf.js';
import {
  bimToeClassName, bimToeLook, bimToeMesh, bimToePartsLook, bimToeRaw, bimToeSets, bimToeTree, bimToeUnit,
  bimToeVal
} from './ifc-review.js';
import { bimRvLoad } from '../render/rendered-view.js';

/* ================= __acad3dV206: That Open Engine, loaded on demand =================
   docs/research/research-thatopen.md (the owner's decisions, 2026-11-13) and research-thatopen-gap/. That Open
   (@thatopen/components 3.6.0, components-front 3.6.1, fragments 3.6.1, MIT) and web-ifc 0.0.81 (MPL-2.0) are three
   files in runtime/thatopen/<ver>/, pinned by size and SHA-256 in runtime/MANIFEST.json and built by tools/thatopen,
   fetched only when an IFC file is opened or the Review view is asked for: from the page's folder over http(s), and
   for a copy on a disk first from a runtime folder beside it, then from the Pages address. They run on the app's own
   three.js (render/rendered-view.js loads it), never a second copy.
   Two things make it work from file:// (e01, e02): web-ifc's wasm is carried in a script and handed to web-ifc by a
   fetch wrapper that answers only its address, and the fragments worker is made a classic worker by the library's own
   toClassicWorker(). This file is the only meeting point with the library: its loader, and the reader that turns an
   IFC file into the import's data (the same shape as io/ifc-full.js's bimIfcRead). */
var BIM_TOE={ver:'3.6.0',dir:'thatopen/3.6.0/',wasmUrl:'https://bim-webifc.invalid/web-ifc.wasm',
  files:[
    {f:'bim-webifc.min.js',g:'BIMWEBIFC',sri:'sha256-jPwIk5HMlzhh1FxocntXSeMsiGlayJLI4wkNciONruc='},
    {f:'bim-webifc-wasm.js',g:'BIMWEBIFC_WASM',sri:'sha256-zDTtyg+u6dPpEVwZIqLuin3WgBA0eBNNuw7fEZPUzzw='},
    {f:'bim-thatopen.min.js',g:'BIMTOE',sri:'sha256-UEvSoAA2gbCXb+E+apFIwyqFZSPZNw9UJzLb+DTNKz0='}],
  maxTris:1500000,chunk:400,
  /* as V196: spaces are rooms, not solids (web-ifc and cc-ifc leave them out too); the facility parts are added */
  skip:{IFCSPACE:1,IFCOPENINGELEMENT:1,IFCOPENINGSTANDARDCASE:1},
  addClasses:['IFCSPATIALZONE','IFCROADPART','IFCBRIDGEPART','IFCRAILWAYPART','IFCMARINEPART','IFCFACILITYPARTCOMMON']};
var A3D_TOE={load:null,st:'',err:'',L:null};
/* where each file is asked for, in order: beside the page from a disk, then the runtime's address (with its hash) */
function bimToeSources(protocol,base,file){
  var p=String(protocol||''),out=[];
  if(p!=='http:'&&p!=='https:')out.push({u:'runtime/'+BIM_TOE.dir+file.f,sri:false});
  out.push({u:String(base)+BIM_TOE.dir+file.f,sri:true});
  return out;
}
function bimToeScript(file){
  if(window[file.g])return Promise.resolve(window[file.g]);
  var src=bimToeSources(window.location&&window.location.protocol,bimLbBase(),file),i=0;
  return new Promise(function(res,rej){
    function next(){
      if(i>=src.length){rej(new Error(file.f+' could not be loaded from '+src.map(function(s){return s.u;}).join(' or ')));return;}
      var s=src[i++],tag=document.createElement('script');
      tag.src=s.u;
      if(s.sri){tag.integrity=file.sri;tag.crossOrigin='anonymous';}
      tag.onload=function(){if(window[file.g])res(window[file.g]);else next();};
      tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
      document.head.appendChild(tag);
    }
    next();
  });
}
/* web-ifc asks for its wasm by fetch; the wrapper answers that one address from the script's base64 and passes every
   other request on unchanged */
function bimToeWasmShim(b64){
  if(window.fetch&&window.fetch.bimToeShim)return;
  var bin=atob(b64),bytes=new Uint8Array(bin.length),i,f0=window.fetch;
  for(i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
  var shim=function(u){
    var s=String(u&&u.url||u);
    if(s===BIM_TOE.wasmUrl)return Promise.resolve(new Response(bytes.slice(0),{headers:{'Content-Type':'application/wasm'}}));
    return f0.apply(this,arguments);
  };
  shim.bimToeShim=true;
  window.fetch=shim;
}
/* the library, asked for once: a promise of {T, OBC, OBF, FRAGS, W, worker} */
function bimToeLoad(){
  var R=A3D_TOE;
  if(R.load)return R.load;
  R.st='loading';R.err='';
  R.load=bimRvLoad().then(function(T){
    var k=0;
    function next(){return k<BIM_TOE.files.length?bimToeScript(BIM_TOE.files[k++]).then(next):Promise.resolve();}
    return next().then(function(){
      bimToeWasmShim(window.BIMWEBIFC_WASM);
      var E=window.BIMTOE;
      return E.FRAGS.FragmentsModels.getWorker().then(function(u){return E.FRAGS.toClassicWorker(u);}).then(function(w){
        R.L={T:T,OBC:E.OBC,OBF:E.OBF,FRAGS:E.FRAGS,W:window.BIMWEBIFC,worker:w};
        R.st='ready';
        return R.L;
      });
    });
  }).then(null,function(e){R.st='failed';R.err=String(e&&e.message||e);R.load=null;throw e;});
  return R.load;
}
/* a That Open session: components with a fragments manager on the classic worker, and an IFC loader that never fetches
   (its wasm comes through the shim). Each caller disposes its own (components.dispose()) */
function bimToeSession(L){
  var c=new L.OBC.Components(),fm=c.get(L.OBC.FragmentsManager),ld=c.get(L.OBC.IfcLoader);
  fm.init(L.worker,{classicWorker:true});
  return ld.setup({autoSetWasm:false,wasm:{path:BIM_TOE.wasmUrl.replace(/[^\/]*$/,''),absolute:true}}).then(function(){
    return {c:c,fm:fm,loader:ld};
  });
}
/* the importer as the app wants it: IFC4.3's facility parts and spatial zones, which carry geometry cc-ifc draws and
   That Open's list leaves out (e03, the road); and, for the import (raw true), each storey's Elevation left as the file
   has it. That Open's default replaces it by the storey's absolute height already in metres, which the import's own
   unit factor would then scale again: the second reader found millimetre files' levels collapsed to within 12 mm */
function bimToeImporterSetup(imp,raw){
  var W=window.BIMWEBIFC,k;
  for(k=0;k<BIM_TOE.addClasses.length;k++)if(W&&typeof W[BIM_TOE.addClasses[k]]==='number')imp.classes.elements.add(W[BIM_TOE.addClasses[k]]);
  if(raw)imp.replaceStoreyElevation=false;
  return imp;
}
/* the ids that pass, in chunks, through an async call of the model's, and the results joined */
function bimToeChunks(ids,fn){
  var out=[],i=0;
  function next(){
    if(i>=ids.length)return Promise.resolve(out);
    var part=ids.slice(i,i+BIM_TOE.chunk);i+=BIM_TOE.chunk;
    return Promise.resolve(fn(part)).then(function(r){out=out.concat(r||[]);return next();});
  }
  return next();
}
/* the IFC file read through That Open, as io/ifc-full.js's bimIfcRead gives it: {parts: [{id, type, guid, name, col,
   opacity, mesh, psets}], storeys: [{id, name, elev}], holder, tris, cut, skipped, notes, booleans, schema, coord}.
   Meshes in metres, +Y up, moved near the origin as web-ifc's COORDINATE_TO_ORIGIN does; coord's translation is the
   shift from the file's frame, as cc-ifc's coordination matrix (e02: equal to it in meaning, by measurement) */
function bimToeRead(bytes,text){
  var S=null,model=null,T0=Date.now(),ms={};
  return bimToeLoad().then(function(L){return bimToeSession(L);}).then(function(s){
    S=s;
    return S.loader.load(bytes,false,'bim-import',{instanceCallback:function(imp){bimToeImporterSetup(imp,true);}});
  }).then(function(m){
    model=m;ms.convert=Date.now()-T0;
    return Promise.all([model.getItemsWithGeometry(),model.getSpatialStructure(),model.getCoordinates(),
      model.getMetadata().then(null,function(){return {};})]);
  }).then(function(r){
    var items=r[0],tree=bimToeTree(r[1]),base=r[2]||[0,0,0],meta=r[3]||{},ids=[],k=0;
    function ids1(){
      if(k>=items.length)return Promise.resolve();
      return Promise.resolve(items[k++].getLocalId()).then(function(id){if(id!=null)ids.push(id);return ids1();});
    }
    return ids1().then(function(){
      var unit=bimToeUnit(text),D={parts:[],storeys:[],holder:tree.holder,tris:0,cut:0,skipped:0,notes:[],booleans:true,
        schema:String(meta.schema||''),coord:[1,0,0,0,0,1,0,0,0,0,1,0,+base[0]||0,+base[1]||0,+base[2]||0,1]};
      return Promise.all([
        bimToeChunks(ids,function(p){return model.getItemsData(p,{attributesDefault:true,relations:{IsDefinedBy:{attributes:true,relations:true}}});}),
        model.getItemsMaterialDefinition(ids),
        tree.storeys.length?model.getItemsData(tree.storeys,{attributesDefault:true}):Promise.resolve([])
      ]).then(function(q){
        var data=q[0],look=bimToeLook(q[1]),byId={},i;ms.data=Date.now()-T0-ms.convert;
        for(i=0;i<data.length;i++)if(data[i]&&bimToeRaw(data[i]._localId)!=null)byId[bimToeRaw(data[i]._localId)]=data[i];
        for(i=0;i<q[2].length;i++){
          var sd=q[2][i],e=sd&&sd.Elevation&&sd.Elevation.value;
          D.storeys.push({id:+bimToeRaw(sd._localId),name:bimToeVal(sd.Name)||('Storey '+(i+1)),
            elev:typeof e==='number'?e*unit+(+base[1]||0):null});
        }
        ids=ids.filter(function(id){var c=bimToeVal((byId[id]||{})._category)||tree.cats[id]||'';return !BIM_TOE.skip[String(c).toUpperCase()];});
        var j=0;
        function geo(){
          if(j>=ids.length)return Promise.resolve();
          var part=ids.slice(j,j+BIM_TOE.chunk);j+=BIM_TOE.chunk;
          var G,own={},sampleMat={},mats={};
          return model.getItemsGeometry(part).then(function(G0){
            G=G0;
            /* each part to its element by its own localId (the list's order only where a part has none) */
            var g,q,m2,sids=[];
            for(g=0;g<(G||[]).length;g++)for(q=0;q<(G[g]||[]).length;q++){
              m2=G[g][q];var key=m2&&m2.localId!=null?m2.localId:part[g];
              (own[key]||(own[key]=[])).push(m2);
              if(m2&&m2.sampleId!=null)sids.push(m2.sampleId);
            }
            /* each part's material, for the colour by cc-ifc's rule (bimToePartsLook) */
            return sids.length?model.getSamples(sids).then(function(S1){
              var mids=[];
              S1.forEach(function(v,k){sampleMat[k]=v.material;mids.push(v.material);});
              return model.getMaterials(mids);
            }).then(function(M){M.forEach(function(v,k){mats[k]=v;});},function(eM){console.warn('[BIM] That Open: the parts\' materials could not be read; colours from the items\' definitions',eM);}):null;
          }).then(function(){
            for(var g=0;g<part.length;g++){
              var id=part[g],it=byId[id]||{},cls=bimToeVal(it._category)||tree.cats[id]||'IFCPRODUCT';
              var lk=bimToePartsLook(own[id]||[],sampleMat,mats)||look[id]||{col:'#b8b8b0',opacity:1};
              var raw=bimToeMesh(own[id]||[]),t=raw.idx.length/3;
              if(!t){D.skipped++;continue;}
              if(D.tris+t>BIM_TOE.maxTris){D.cut+=t;continue;}
              var mm=bimGltfWeld(raw.pos,raw.idx);
              if(!mm.f.length){D.skipped++;continue;}
              mm.fe=bimGltfFeatureEdges(mm);
              D.tris+=mm.f.length;
              D.parts.push({id:id,type:bimToeClassName(cls,bimToeClassLists()),guid:bimToeVal(it._guid),name:bimToeVal(it.Name),
                col:lk.col,opacity:Math.max(0.05,Math.min(1,lk.opacity)),mesh:mm,psets:bimToeSets(it)});
            }
            return geo();
          });
        }
        return geo().then(function(){ms.geometry=Date.now()-T0-ms.convert-ms.data;D.ms=ms;return D;});
      });
    });
  }).then(function(D){
    var t1=Date.now();
    if(S)try{S.c.dispose();}catch(eX){console.warn('[BIM] That Open: the reading session could not be closed',eX);}
    if(D.ms){D.ms.dispose=Date.now()-t1;D.ms.read=Date.now()-T0;}
    return D;
  },function(e){
    if(S)try{S.c.dispose();}catch(eX){}
    throw e;
  });
}
/* the class names web-ifc's schemas know, once, for bimToeClassName */
function bimToeClassLists(){
  if(A3D_TOE.names)return A3D_TOE.names;
  var W=window.BIMWEBIFC||{},out=[],ns=['IFC4X3','IFC4','IFC2X3'],i,k,L;
  for(i=0;i<ns.length;i++){L=[];if(W[ns[i]])for(k in W[ns[i]])if(/^Ifc[A-Z]/.test(k)&&!/(Enum|Select)$/.test(k))L.push(k);out.push(L);}
  A3D_TOE.names=out;
  return out;
}
export { A3D_TOE, BIM_TOE, bimToeClassLists, bimToeImporterSetup, bimToeLoad, bimToeRead };
