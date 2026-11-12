import { A3D } from '../core/state.js';
import { pushUndo, setUndoSuspend } from '../drawing/plan-mode-sketch.js';
import { clampLevelElev } from '../bim/levels-walls-floors.js';
import { refreshLevels } from '../bim/classification.js';
import { bimLayerById } from '../layers/layer-rules.js';
import { refreshLayers } from '../layers/analysis-data-rows.js';
import { bimPropGroup, bimPropText } from '../properties/palette.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { bimImportIFC } from './import-ifc.js';
import { bimSkpLayer } from './sketchup-import.js';
import { bimGltfFeatureEdges, bimGltfWeld } from './gltf.js';
import { bimHandleImportFile } from './import-entry.js';
import { paint } from '../map/terrain-3d.js';
import { fitScene } from '../ui/tool-palette.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast } from '../bim/csg-booleans.js';

/* __acad3dV196: full IFC import, through BimCraft's IFC engine (cc-ifc, Apache-2.0) and Manifold (Apache-2.0), a
   pinned runtime loaded only when an IFC file is opened (runtime/cc-ifc/<rev>/, tools/ifc/build_ifc.mjs). Every
   element with geometry comes in as one locked solid, in its own colour, with its openings cut, on a layer for its
   IFC class under a layer named after the file; its GlobalId, storey and property sets are kept for Properties; the
   storeys become levels. When the runtime cannot be loaded the walls-and-slabs reader (import-ifc.js) is used.
   docs/research/research-ifc-engine.md. */
  var BIM_IFC={rev:'cfbd948',file:'cc-ifc/cfbd948/bim-ifc.min.js',wasm:'cc-ifc/cfbd948/manifold.wasm',
    sri:'sha256-66V2QHHfq3vjlzKTpyK0LYY98Hc7UqzSbY7eT0gbG5c=',
    maxTris:1500000,warnTris:300000,maxSets:40,maxProps:80,maxText:200};
  var A3D_IFC={load:null,st:'',err:'',B:null,M:null};
  /* where the runtime is looked for: beside the page when it is opened as a file, then the site (as V194's three.js) */
  function bimIfcSources(protocol,base){
    var p=String(protocol||''),out=[];
    if(p!=='http:'&&p!=='https:')out.push({u:'runtime/'+BIM_IFC.file,sri:false,base:'runtime/'});
    out.push({u:String(base)+BIM_IFC.file,sri:true,base:String(base)});
    return out;
  }
  /* the engine, asked for once: a promise of {B, M} (M null when Manifold's wasm could not be had: no openings cut) */
  function bimIfcLoad(){
    var R=A3D_IFC;
    if(R.load)return R.load;
    var src=bimIfcSources(window.location&&window.location.protocol,bimLbBase()),i=0,from='';
    R.st='loading';R.err='';
    R.load=new Promise(function(res,rej){
      if(window.BIMIFC&&window.BIMIFC.IfcAPI){from=src[src.length-1].base;res(window.BIMIFC);return;}
      function next(){
        if(i>=src.length){rej(new Error('the IFC engine could not be loaded from '+src.map(function(s){return s.u;}).join(' or ')));return;}
        var s=src[i++],tag=document.createElement('script');
        tag.src=s.u;
        if(s.sri){tag.integrity=BIM_IFC.sri;tag.crossOrigin='anonymous';}
        tag.onload=function(){if(window.BIMIFC&&window.BIMIFC.IfcAPI){from=s.base;res(window.BIMIFC);}else next();};
        tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
        document.head.appendChild(tag);
      }
      next();
    }).then(function(B){
      R.B=B;
      /* Manifold's wasm beside the bundle; from a file:// page the browser refuses it, and the site's copy is tried */
      var bases=[from].concat(from!==String(bimLbBase())?[String(bimLbBase())]:[]),k=0;
      function tryM(){
        if(k>=bases.length)return Promise.resolve(null);
        var b=bases[k++];
        return Promise.resolve().then(function(){
          return B.Manifold({locateFile:function(f){return /\.wasm$/.test(f)?b+BIM_IFC.wasm:f;}});
        }).then(function(M){M.setup();return M;},function(e){console.warn('[BIM] IFC: Manifold from '+b+' failed: '+(e&&e.message||e));return tryM();});
      }
      return tryM().then(function(M){R.M=M;R.st='ready';return R;});
    },function(e){R.st='failed';R.err=String(e&&e.message||e);R.load=null;throw e;});
    return R.load;
  }
  function bimIfcHex(c){
    if(!c)return '#b8b8b0';
    return '#'+[c.x,c.y,c.z].map(function(x){var h=Math.max(0,Math.min(255,Math.round((+x||0)*255))).toString(16);return h.length<2?'0'+h:h;}).join('');
  }
  function bimIfcVal(v){
    if(v==null)return '';
    if(typeof v==='object'&&v.value!==undefined)v=v.value;
    if(typeof v==='number')return String(Math.abs(v)>=1e-4||v===0?+v.toPrecision(6):v);
    if(typeof v==='boolean')return v?'Yes':'No';
    if(Array.isArray(v))return v.map(bimIfcVal).join(', ');
    return String(v);
  }
  function bimIfcText(v){return bimIfcVal(v).replace(/\s+/g,' ').slice(0,BIM_IFC.maxText);}
  /* every element's meshes, in metres with +Y up, as parts: [{id, type, guid, name, col, opacity, mesh}], each element
     one welded mesh (all its pieces), in the colour that covers most of it; at most maxTris triangles */
  function bimIfcMeshParts(api,mid,maxTris){
    var parts=[],tris=0,cut=0,skipped=0;
    maxTris=maxTris||BIM_IFC.maxTris;
    api.StreamAllMeshes(mid,function(mesh){
      var g=mesh.geometries,n=g.size(),pos=[],idx=[],cols={},best='',bestN=-1,op=0,opN=0,i,k,base,count=0;
      for(i=0;i<n;i++){
        var pg=g.get(i),geo=api.GetGeometry(mid,pg.geometryExpressID),
          v=api.GetVertexArray(geo.GetVertexData(),geo.GetVertexDataSize()),ix=api.GetIndexArray(geo.GetIndexData(),geo.GetIndexDataSize()),
          m=pg.flatTransformation,t=ix.length/3,hex=bimIfcHex(pg.color),a=pg.color&&isFinite(pg.color.w)?+pg.color.w:1;
        if(geo.delete)geo.delete();
        if(!t)continue;
        base=pos.length/3;
        for(k=0;k<v.length;k+=6){
          var x=v[k],y=v[k+1],z=v[k+2];
          pos.push(m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]);
        }
        for(k=0;k<ix.length;k++)idx.push(base+ix[k]);
        cols[hex]=(cols[hex]||0)+t;
        if(a>=0.99&&cols[hex]>bestN){best=hex;bestN=cols[hex];}
        op+=a*t;opN+=t;count+=t;
      }
      if(!count){skipped++;return;}
      if(tris+count>maxTris){cut+=count;return;}
      var mm=bimGltfWeld(pos,idx);
      if(!mm.f.length){skipped++;return;}
      mm.fe=bimGltfFeatureEdges(mm);
      if(!best)for(var h in cols)if(cols.hasOwnProperty(h)&&cols[h]>bestN){best=h;bestN=cols[h];}
      tris+=mm.f.length;
      var L=api.GetLine(mid,mesh.expressID)||{};
      parts.push({id:mesh.expressID,type:api.GetNameFromTypeCode(api.GetLineType(mid,mesh.expressID))||'IfcProduct',
        guid:bimIfcText(L.GlobalId),name:bimIfcText(L.Name),col:best,opacity:opN?Math.max(0.05,Math.min(1,op/opN)):1,mesh:mm});
    });
    return {parts:parts,tris:tris,cut:cut,skipped:skipped};
  }
  /* the storeys, as levels: [{id, name, elev}] (metres, in the model's frame) */
  function bimIfcStoreys(api,mid,B){
    var ids=api.GetLineIDsWithType(mid,B.IFCBUILDINGSTOREY),out=[],i,u=1,C=api.GetCoordinationMatrix(mid);
    try{u=api.geometry(mid).g.lengthUnit||1;}catch(eU){u=1;}
    for(i=0;i<ids.size();i++){
      var L=api.GetLine(mid,ids.get(i))||{},e=L.Elevation&&L.Elevation.value;
      out.push({id:ids.get(i),name:bimIfcText(L.Name)||('Storey '+(i+1)),elev:typeof e==='number'?e*u+(C[13]||0):null});
    }
    return out;
  }
  /* element id -> the storey (or other spatial element) that holds it */
  function bimIfcContainers(tree){
    var map={};
    (function walk(n,holder){
      if(!n)return;
      var t=String(n.type||'').toUpperCase(),here=(t==='IFCBUILDINGSTOREY'||t==='IFCSPACE'&&!holder)?n.expressID:holder;
      if(n.expressID!=null&&holder!=null&&map[n.expressID]==null)map[n.expressID]=holder;
      (n.children||[]).forEach(function(c){walk(c,here);});
    })(tree,null);
    return map;
  }
  /* a property set or quantity set line as {name, rows: [[name, value]]} */
  function bimIfcSet(L){
    if(!L)return null;
    var list=L.HasProperties||L.Quantities||[],rows=[],i,q,k,val;
    for(i=0;i<list.length&&rows.length<BIM_IFC.maxProps;i++){
      q=list[i];if(!q||!q.Name)continue;
      val='';
      for(k in q)if(q.hasOwnProperty(k)&&/Value$/.test(k)&&q[k]!=null){val=bimIfcText(q[k]);break;}
      if(!val&&q.EnumerationValues)val=bimIfcText(q.EnumerationValues);
      if(!val&&q.ListValues)val=bimIfcText(q.ListValues);
      rows.push([bimIfcText(q.Name),val]);
    }
    return {name:bimIfcText(L.Name)||'Properties',rows:rows};
  }
  function bimIfcPsets(api,mid,id){
    return api.properties.getPropertySets(mid,id,true).then(function(list){
      var out=[],i,s;
      for(i=0;i<list.length&&out.length<BIM_IFC.maxSets;i++){s=bimIfcSet(list[i]);if(s&&s.rows.length)out.push(s);}
      return out;
    },function(){return [];});
  }
  /* the file read: {parts, storeys, holder, tris, cut, skipped, notes, booleans, schema} (async, for the property sets) */
  function bimIfcRead(R,bytes){
    var api=new R.B.IfcAPI();
    return api.Init({manifold:R.M||false}).then(function(){
      var mid=api.OpenModel(bytes,{COORDINATE_TO_ORIGIN:true});
      if(mid<0)throw new Error('not a readable IFC file (ISO 10303-21)');
      var S=bimIfcMeshParts(api,mid,BIM_IFC.maxTris),st=bimIfcStoreys(api,mid,R.B),notes=[];
      try{api.notes(mid).forEach(function(n,why){notes.push(why+' ('+n+')');});}catch(eN){notes=[];}
      return api.properties.getSpatialStructure(mid,false).then(function(tree){
        var holder=bimIfcContainers(tree),i=0;
        function more(){
          if(i>=S.parts.length)return Promise.resolve();
          var q=S.parts[i++];
          return bimIfcPsets(api,mid,q.id).then(function(ps){q.psets=ps;return more();});
        }
        return more().then(function(){
          var schema='';try{schema=api.GetModelSchema(mid);}catch(eS){schema='';}
          api.CloseModel(mid);
          return {parts:S.parts,storeys:st,holder:holder,tris:S.tris,cut:S.cut,skipped:S.skipped,notes:notes,booleans:!!api.booleans,schema:schema};
        });
      });
    });
  }
  /* IfcWallStandardCase -> IfcWall: the class an element's layer is named after */
  function bimIfcClass(t){return String(t||'IfcProduct').replace(/StandardCase$|ElementedCase$/,'');}
  var BIM_IFC_KIND={IfcWall:'wall',IfcSlab:'floor'};
  function bimIfcImportBuffer(buf,filename){
    var name=String(filename||'model.ifc'),stem=name.replace(/^.*[\\\/]/,'').replace(/\.ifc$/i,'')||'IFC',t0=Date.now();
    var bytes=buf instanceof Uint8Array?buf:new Uint8Array(buf);
    return bimIfcLoad().then(function(R){return bimIfcRead(R,bytes);}).then(function(D){
      if(!D.parts.length)throw new Error('no elements with geometry in '+name);
      var made=[],ids=[],byClass={},names={},levels=0,i;
      for(i=0;i<D.storeys.length;i++)names[D.storeys[i].id]=D.storeys[i].name;
      pushUndo();
      setUndoSuspend(true);
      var was=A3D.activeLayer;
      try{
        var fl=bimSkpLayer(stem,'#c7bfae',null,made).ly;
        if(!fl)throw new Error('the layer '+stem+' could not be made');
        for(i=0;i<D.storeys.length;i++){
          var s=D.storeys[i],ln=s.name+' (IFC)';
          if(s.elev==null||A3D.levels.some(function(l){return l.name===ln;}))continue;
          A3D.levels.push({id:'lvl-'+Date.now().toString(36)+'-'+(A3D.seq++),name:ln,elev:clampLevelElev(s.elev),height:3});
          levels++;
        }
        for(i=0;i<D.parts.length;i++){
          var q=D.parts[i],cls=bimIfcClass(q.type),glass=q.opacity<0.99,key=cls+(glass?'|g':'');
          if(!byClass[key]){
            var cl=bimSkpLayer(cls,q.col,fl.id,made);
            if(glass){
              var pct=Math.max(5,Math.min(90,Math.round((1-q.opacity)*20)*5)),sl=bimSkpLayer(cls+' - see-through',q.col,(cl.ly||fl).id,made);
              if(sl.fresh)sl.ly.transparency=pct;
              byClass[key]=sl.ly||cl.ly||fl;
            }else byClass[key]=cl.ly||fl;
          }
          var hold=D.holder[q.id],bim={type:BIM_IFC_KIND[cls]||'ifc',imported:true,ifcType:q.type,guid:q.guid,
            storey:hold!=null&&names[hold]?names[hold]:'',file:name.slice(0,120),psets:q.psets||[]};
          var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:(q.name||cls+' '+q.id).slice(0,80),col:q.col,
            pos:[0,0,0],mesh:q.mesh,layer:byClass[key].id,locked:true,bim:bim};
          A3D.objs.push(o);ids.push(o.id);
        }
      }finally{setUndoSuspend(false);}
      if(bimLayerById(was))A3D.activeLayer=was;
      refreshTree();refreshLevels();refreshLayers();refreshProps();fitScene();paint();saveSoon();
      return {ids:ids,layers:made,levels:levels,triangles:D.tris,cut:D.cut,skipped:D.skipped,notes:D.notes,booleans:D.booleans,ms:Date.now()-t0,
        text:'IFC'+(D.schema?' ('+D.schema+')':'')+': '+ids.length+' element'+(ids.length===1?'':'s')+' from '+name+', '+levels+' level'+(levels===1?'':'s')+
          ', on the '+stem+' layer by class'+
          (D.booleans?'':'; openings not cut (the geometry library could not be loaded)')+
          (D.cut?'; stopped at '+BIM_IFC.maxTris+' triangles, the rest left out':'')+
          (D.tris>BIM_IFC.warnTris?'; a large model: the project file grows with it':'')+
          (D.notes.length?'; not drawn: '+D.notes.slice(0,2).join('; '):'')};
    });
  }
  /* Import's .ifc: the full reader, or the walls-and-slabs one when the runtime cannot be had */
  function bimImportIFCFull(buf,filename){
    var name=String(filename||'model.ifc');
    a3dToast('Reading '+name+' (the first time loads the IFC engine)...');
    return bimIfcImportBuffer(buf,name).then(function(r){a3dToast(r.text);return r;},function(e){
      var s=String(e&&e.message||e);
      console.warn('[BIM] IFC import: '+s,e);
      if(A3D_IFC.st==='failed'){
        a3dToast('The IFC engine could not be loaded, so only walls and slabs are read');
        var text='';
        try{text=new TextDecoder('utf-8').decode(buf);}catch(eD){text='';}
        if(text)bimImportIFC(text,name);
        return {error:s,fallback:true};
      }
      a3dToast('IFC import failed: '+s);
      return {error:s};
    });
  }
  /* Properties: the IFC rows of an imported element (class, GlobalId, storey, then each property set as a group) */
  function bimIfcPropsHtml(o){
    var b=o&&o.bim;
    if(!b||!b.ifcType||!b.guid)return '';
    var h='',rows=bimPropText('IFC Class',b.ifcType)+bimPropText('GlobalId',b.guid)+(b.storey?bimPropText('Storey',b.storey):'')+
      (b.file?bimPropText('File',b.file):'');
    h+=bimPropGroup('IFC',rows);
    (b.psets||[]).forEach(function(s){
      h+=bimPropGroup(s.name,s.rows.map(function(r){return bimPropText(r[0],r[1]);}).join(''));
    });
    return h;
  }
  function bimIfcPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.ifc';
    inp.onchange=function(){var f=inp.files&&inp.files[0];if(f)bimHandleImportFile(f);};
    inp.click();
    return true;
  }
export {
  BIM_IFC, bimIfcClass, bimIfcContainers, bimIfcHex, bimIfcImportBuffer, bimIfcMeshParts, bimIfcPick,
  bimIfcPropsHtml, bimIfcRead, bimIfcSet, bimIfcSources, bimIfcStoreys, bimIfcVal, bimImportIFCFull
};
