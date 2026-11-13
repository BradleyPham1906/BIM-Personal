(function(){
function b64(s){var b=atob(s),u=new Uint8Array(b.length);for(var i=0;i<b.length;i++)u[i]=b.charCodeAt(i);return u;}
window.RUN=async function(mode){
  var out={mode:mode,proto:location.protocol,coi:!!window.crossOriginIsolated,files:{}};
  var T=window.TOE,FR=T.FRAGS;
  if(/shim/.test(mode)){var of=window.fetch;window.fetch=function(u,o){var s=String(u&&u.url||u);if(/web-ifc\.wasm$/.test(s))return Promise.resolve(new Response(b64(window.WEBIFC_WASM_B64),{headers:{'Content-Type':'application/wasm'}}));return of.apply(this,arguments);};}
  try{
    var wurl=await FR.FragmentsModels.getWorker();if(/classic/.test(mode))wurl=await FR.toClassicWorker(wurl); out.worker=wurl.slice(0,5);
    var fm=new FR.FragmentsModels(wurl,/classic/.test(mode)?{classicWorker:true}:undefined);
    for(var name in window.IFCS){
      var r={},t0=performance.now();
      try{
        var imp=new FR.IfcImporter(); imp.wasm={path:'./',absolute:false};
        console.log("convert "+name);var frag=await imp.process({bytes:b64(window.IFCS[name])});
        r.convertMs=Math.round(performance.now()-t0); r.fragBytes=frag.byteLength;
        console.log("converted "+frag.byteLength);var t1=performance.now(); var model=await fm.load(frag,{modelId:name});
        console.log("loaded");r.loadMs=Math.round(performance.now()-t1);
        var ids=await model.getItemsIdsWithGeometry(); r.itemsWithGeometry=ids.length;
        var cats=await model.getCategories(); r.categories=cats.length;
      }catch(e){r.error=String(e&&e.message||e).slice(0,200);}
      out.files[name]=r;
    }
  }catch(e){out.error=String(e&&e.message||e).slice(0,300);}
  return out;
};})();
