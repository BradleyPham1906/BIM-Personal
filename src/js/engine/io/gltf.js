import { A3D } from '../core/state.js';
import { TYPES, meshOf } from '../core/mesh-primitives.js';
import { pushUndo, setUndoSuspend } from '../drawing/plan-mode-sketch.js';
import { bimFileStem } from './project-file.js';
import { bimLayerAlpha, bimLayerById, bimLayerShown } from '../layers/layer-rules.js';
import { refreshLayers } from '../layers/analysis-data-rows.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { bimSkpLayer } from './sketchup-import.js';
import { bimHandleImportFile } from './import-entry.js';
import { BIM_RV_VER, bimRvLoad } from '../render/rendered-view.js';
import { paint } from '../map/terrain-3d.js';
import { fitScene } from '../ui/tool-palette.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { A3D_FAMLIB, bimAssetKind, bimMergeMeshes, bimSaveFamilyLibrary } from '../assets/family-library.js';
import { bimMeshThumb } from '../assets/scale-assets.js';
import { refreshFamilyPanel } from '../assets/blocks.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV195: glTF and GLB, in and out =================
     docs/research/research-gltf.md. glTF 2.0 (Khronos) is the format models move between programs in: furniture,
     trees, cars and people from model libraries, and the model out to Blender, SketchUp, a headset. It is read and
     written by three.js's own GLTFLoader and GLTFExporter, in the pinned runtime the rendered view already loads
     (runtime/three, V194), with its Draco loader and meshopt decoder for compressed files (the owner, 2026-11-12).
     glTF is metres, +Y up and right-handed, as this engine is (the glTF 2.0 specification, 3.4), so no axis or
     unit is changed either way.

     In: every mesh's triangles where the file places them, welded by position, gathered by material (one solid each,
     in its colour; see-through ones on a sub-layer at their transparency, as V163's SketchUp import does), locked, on
     a layer named after the file; and the whole file kept in Assets as a block when small enough (the owner: the
     model and Assets). Each solid keeps its outline only: the edges where the surface folds or ends, not every
     triangle's (mesh.fe, read by the shaded view's two engines). Textures are not drawn: a part takes its material's
     colour.

     Out: each element shown, one mesh each, named by its name and id, under a node for its layer, in its colour and
     its layer's transparency, as one .glb. */
  var BIM_GLTF={maxTris:300000,warnTris:100000,blockTris:20000,weld:1e-5,crease:20,KTX:'KHR_texture_basisu'};
  /* triangles as glTF gives them (positions, three numbers a corner; index, or none for a plain list) welded by
     position: {v, f}, the corners that land on one point made one, triangles of no area left out */
  function bimGltfWeld(pos,index,q){
    q=q||BIM_GLTF.weld;
    var v=[],f=[],key={},map=[],n=pos.length/3,i,k,x,y,z,a,b,c,t;
    for(i=0;i<n;i++){
      x=pos[i*3];y=pos[i*3+1];z=pos[i*3+2];
      k=Math.round(x/q)+','+Math.round(y/q)+','+Math.round(z/q);
      if(!key.hasOwnProperty(k)){key[k]=v.length;v.push([x,y,z]);}
      map[i]=key[k];
    }
    t=index?index.length:n;
    for(i=0;i+2<t;i+=3){
      a=map[index?index[i]:i];b=map[index?index[i+1]:i+1];c=map[index?index[i+2]:i+2];
      if(a===b||b===c||a===c)continue;
      f.push([a,b,c]);
    }
    return {v:v,f:f};
  }
  /* a triangle's unit normal, or null for one of no area */
  function bimGltfNormal(m,t){
    var A=m.v[t[0]],B=m.v[t[1]],C=m.v[t[2]],
      ux=B[0]-A[0],uy=B[1]-A[1],uz=B[2]-A[2],wx=C[0]-A[0],wy=C[1]-A[1],wz=C[2]-A[2],
      x=uy*wz-uz*wy,y=uz*wx-ux*wz,z=ux*wy-uy*wx,l=Math.sqrt(x*x+y*y+z*z);
    return l>1e-12?[x/l,y/l,z/l]:null;
  }
  /* the edges worth drawing: where the surface ends (an edge of one triangle) or folds by more than deg degrees
     between its two triangles, or meets more than two; [[a, b]] by vertex */
  function bimGltfFeatureEdges(m,deg){
    var cos=Math.cos((deg==null?BIM_GLTF.crease:deg)*Math.PI/180),E={},out=[],i,j,a,b,k,e,n,N=[];
    for(i=0;i<m.f.length;i++)N.push(bimGltfNormal(m,m.f[i]));
    for(i=0;i<m.f.length;i++)for(j=0;j<3;j++){
      a=m.f[i][j];b=m.f[i][(j+1)%3];k=a<b?a+'_'+b:b+'_'+a;
      (E[k]||(E[k]={a:Math.min(a,b),b:Math.max(a,b),t:[]})).t.push(i);
    }
    for(k in E)if(E.hasOwnProperty(k)){
      e=E[k];
      if(e.t.length!==2){out.push([e.a,e.b]);continue;}
      n=[N[e.t[0]],N[e.t[1]]];
      if(!n[0]||!n[1]){out.push([e.a,e.b]);continue;}
      /* a fold either way: the two faces may be wound alike or not */
      if(Math.abs(n[0][0]*n[1][0]+n[0][1]*n[1][1]+n[0][2]*n[1][2])<cos)out.push([e.a,e.b]);
    }
    return out;
  }
  /* a colour (0 to 1, sRGB) as #rrggbb */
  function bimGltfHex(r,g,b){
    return '#'+[r,g,b].map(function(x){var h=Math.max(0,Math.min(255,Math.round(x*255))).toString(16);return h.length<2?'0'+h:h;}).join('');
  }
  /* the meshes of a loaded glTF scene (three.js objects) gathered by material: [{key, name, col, opacity, pos, index}],
     each a list of world positions; at most maxTris triangles, the rest counted as left out */
  function bimGltfGather(T,root,maxTris){
    var by={},order=[],tris=0,cut=0,c=new T.Color(),p=new T.Vector3();
    root.updateMatrixWorld(true);
    root.traverse(function(o){
      if(!o.isMesh||!o.geometry||!o.geometry.attributes||!o.geometry.attributes.position)return;
      var g=o.geometry,P=g.attributes.position,I=g.index,mats=Array.isArray(o.material)?o.material:[o.material],
        groups=(g.groups&&g.groups.length)?g.groups:[{start:0,count:I?I.count:P.count,materialIndex:0}],gi,s,k,m,key,G,idx;
      for(gi=0;gi<groups.length;gi++){
        s=groups[gi];m=mats[s.materialIndex||0]||mats[0]||{};
        if(m.color)c.copy(m.color);else c.setRGB(0.62,0.71,0.78);
        var rgb=c.getRGB?c.getRGB(new T.Color(),T.SRGBColorSpace):c;   /* the colour as the file gives it, sRGB */
        var hex=bimGltfHex(rgb.r,rgb.g,rgb.b),op=m.transparent?Math.max(0.05,Math.min(1,m.opacity==null?1:m.opacity)):1;
        key=hex+'|'+Math.round(op*20);
        G=by[key];
        if(!G){G=by[key]={key:key,name:String(m.name||'').slice(0,60),col:hex,opacity:op,pos:[]};order.push(G);}
        if(!G.name&&m.name)G.name=String(m.name).slice(0,60);
        var n=Math.floor(s.count/3);
        if(maxTris&&tris+n>maxTris){cut+=n;continue;}
        tris+=n;
        for(k=0;k<n*3;k++){
          idx=I?I.getX(s.start+k):s.start+k;
          p.fromBufferAttribute(P,idx).applyMatrix4(o.matrixWorld);
          G.pos.push(p.x,p.y,p.z);
        }
      }
    });
    return {parts:order,tris:tris,cut:cut};
  }
  /* a loaded scene as the parts the model takes: [{name, col, opacity, mesh}] (welded, its outline named), with the
     triangles kept and those left out over the limit */
  function bimGltfParts(T,root){
    var S=bimGltfGather(T,root,BIM_GLTF.maxTris),parts=[],i,G,m,tri=0;
    for(i=0;i<S.parts.length;i++){
      G=S.parts[i];
      m=bimGltfWeld(G.pos,null);
      if(!m.f.length)continue;
      m.fe=bimGltfFeatureEdges(m);
      tri+=m.f.length;
      parts.push({name:G.name||('Material '+(parts.length+1)),col:G.col,opacity:G.opacity,mesh:m});
    }
    return {parts:parts,tris:tri,cut:S.cut};
  }
  /* the loader, with the decoders for compressed files */
  function bimGltfLoader(T){
    var L=new T.GLTFLoader(),D=new T.DRACOLoader();
    D.setDecoderPath(bimLbBase()+'three/'+BIM_RV_VER+'/draco/');
    L.setDRACOLoader(D);
    L.setMeshoptDecoder(T.MeshoptDecoder);
    return {L:L,D:D};
  }
  /* why a file could not be read, in words */
  function bimGltfWhy(e,name){
    var s=String(e&&e.message||e||'');
    if(s.indexOf(BIM_GLTF.KTX)>=0)return name+' uses KTX2 textures (KHR_texture_basisu), which are not read yet: export it without them';
    if(/Unknown extension|extensionsRequired|not supported/i.test(s))return name+' needs a glTF extension this app does not read ('+s.slice(0,120)+')';
    if(/Failed to fetch|Failed to load buffer|404|NetworkError/i.test(s))return name+' refers to files beside it (a .bin or images): open it as one .glb, or a .gltf with everything embedded';
    if(/draco/i.test(s))return name+' is Draco-compressed and its decoder could not be loaded ('+s.slice(0,100)+')';
    return name+' could not be read as glTF: '+s.slice(0,160);
  }
  /* a buffer read as glTF; a promise of the result in words, or a rejection with its cause */
  function bimGltfImportBuffer(buf,filename){
    var name=String(filename||'model.glb'),stem=name.replace(/^.*[\\\/]/,'').replace(/\.(glb|gltf)$/i,'')||'glTF',t0=Date.now();
    return bimRvLoad().then(function(T){
      return new Promise(function(res,rej){
        var LD=bimGltfLoader(T);
        try{LD.L.parse(buf,'',function(g){LD.D.dispose();res({T:T,g:g});},function(e){LD.D.dispose();rej(new Error(bimGltfWhy(e,name)));});}
        catch(eP){LD.D.dispose();rej(new Error(bimGltfWhy(eP,name)));}
      });
    }).then(function(R){
      var S=bimGltfParts(R.T,R.g.scene),parts=S.parts,tri=S.tris,i,made=[],ids=[],layers={};
      if(!parts.length)throw new Error('No faces in '+name+' to bring in');
      pushUndo();
      setUndoSuspend(true);
      var was=A3D.activeLayer;
      try{
        var fl=bimSkpLayer(stem,'#9db4c8',null,made).ly;
        if(!fl)throw new Error('the layer '+stem+' could not be made');
        for(i=0;i<parts.length;i++){
          var q=parts[i],ly=fl;
          if(q.opacity<1){
            var pct=Math.max(5,Math.min(90,Math.round((1-q.opacity)*20)*5)),k=String(pct);
            if(!layers[k]){var st=bimSkpLayer(fl.name+' - '+pct+'% see-through',fl.color,fl.id,made);if(st.fresh)st.ly.transparency=pct;layers[k]=st.ly||fl;}
            ly=layers[k];
          }
          var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:q.name,col:q.col,pos:[0,0,0],mesh:q.mesh,layer:ly.id,locked:true,
            gltf:{file:name.slice(0,120),material:q.name,triangles:q.mesh.f.length,opacity:q.opacity}};
          A3D.objs.push(o);ids.push(o.id);
        }
      }finally{setUndoSuspend(false);}
      if(bimLayerById(was))A3D.activeLayer=was;
      /* the whole file in Assets, as one block, when small enough to keep */
      var kept=false;
      if(tri<=BIM_GLTF.blockTris){
        var recs=parts.map(function(q,k){return {id:'gltf-'+k,t:'solid',name:q.name,col:q.col,pos:[0,0,0],mesh:q.mesh,layer:null,gltf:{file:name.slice(0,120),material:q.name,triangles:q.mesh.f.length,opacity:q.opacity}};});
        var entry={id:'blk-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),kind:'block',name:stem.slice(0,60),category:'glTF',
          manufacturer:'',source:name.slice(0,120),recs:recs,base:[0,0],y0:0,count:recs.length,createdAt:new Date().toISOString()};
        try{entry.thumb=bimMeshThumb(bimMergeMeshes(recs.map(function(r){return r.mesh;})));}catch(eT){entry.thumb='';}
        for(var d=A3D_FAMLIB.length-1;d>=0;d--){
          var ex=A3D_FAMLIB[d];
          if(bimAssetKind(ex)==='block'&&ex.category==='glTF'&&ex.source===entry.source)A3D_FAMLIB.splice(d,1);
        }
        A3D_FAMLIB.push(entry);kept=true;
        bimSaveFamilyLibrary();refreshFamilyPanel();
      }
      refreshTree();refreshLayers();refreshProps();fitScene();paint();saveSoon();
      return {ids:ids,layers:made,triangles:tri,cut:S.cut,block:kept,ms:Date.now()-t0,
        text:'glTF: '+ids.length+' object'+(ids.length===1?'':'s')+' from '+name+' ('+tri+' triangles) on the '+stem+' layer'+
          (kept?', kept in Assets as a block':'')+
          (S.cut?'; stopped at '+BIM_GLTF.maxTris+' triangles, '+S.cut+' left out':'')+
          (tri>BIM_GLTF.warnTris?'; a large model: the project file grows with it':'')};
    });
  }
  function bimImportGLTF(buf,filename){
    var name=String(filename||'model.glb');
    a3dToast('Reading '+name+' (the first time loads the 3D library)...');
    return bimGltfImportBuffer(buf,name).then(function(r){a3dToast(r.text);return r;},function(e){
      var s=String(e&&e.message||e);
      console.warn('[BIM] glTF import: '+s,e);
      a3dToast('glTF import failed: '+s);
      return {error:s};
    });
  }
  function bimGltfPick(){
    var inp=document.createElement('input');
    inp.type='file';inp.accept='.glb,.gltf';
    inp.onchange=function(){var f=inp.files&&inp.files[0];if(f)bimHandleImportFile(f);};
    inp.click();
    return true;
  }
  /* ---- out ---- */
  /* the elements shown, as [{o, mesh, col, alpha}]: what a glTF of the model holds */
  function bimGltfElements(){
    var out=[],i,o,m;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];m=meshOf(o);
      if(!m||!m.f||!m.f.length||!m.v||!m.v.length)continue;
      if(!bimLayerShown(o))continue;
      out.push({o:o,mesh:m,col:o.col||((TYPES[o.t]||{}).c)||'#7f9db8',alpha:bimLayerAlpha(o)});
    }
    return out;
  }
  /* an element's triangles as positions (world metres) and an index: faces of more than three corners as fans,
     as the shaded view draws them */
  function bimGltfArrays(m,off){
    var pos=new Float32Array(m.v.length*3),idx=[],i,j,f;
    for(i=0;i<m.v.length;i++){pos[i*3]=m.v[i][0]+off[0];pos[i*3+1]=m.v[i][1]+off[1];pos[i*3+2]=m.v[i][2]+off[2];}
    for(i=0;i<m.f.length;i++){f=m.f[i];if(f.length<3)continue;for(j=2;j<f.length;j++)idx.push(f[0],f[j-1],f[j]);}
    return {pos:pos,index:idx};
  }
  /* the model as a three.js scene: a node for each layer, a mesh for each element */
  function bimGltfScene(T){
    var S=new T.Scene(),L=bimGltfElements(),nodes={},mats={},i,e,A,g,ly,node,key,mesh;
    S.name=bimFileStem();
    for(i=0;i<L.length;i++){
      e=L[i];A=bimGltfArrays(e.mesh,e.o.pos||[0,0,0]);
      if(!A.index.length)continue;
      g=new T.BufferGeometry();
      g.setAttribute('position',new T.BufferAttribute(A.pos,3));
      g.setIndex(A.index);
      g.computeVertexNormals();
      ly=bimLayerById(e.o.layer)||{id:'none',name:'No layer'};
      node=nodes[ly.id];
      if(!node){node=nodes[ly.id]=new T.Group();node.name=String(ly.name);node.userData={layer:ly.id};S.add(node);}
      key=e.col+'|'+Math.round(e.alpha*100);
      if(!mats[key]){
        mats[key]=new T.MeshStandardMaterial({color:new T.Color(e.col),roughness:0.8,metalness:0,side:T.DoubleSide,transparent:e.alpha<1,opacity:e.alpha});
        mats[key].name=e.col+(e.alpha<1?' '+Math.round(e.alpha*100)+'%':'');
      }
      mesh=new T.Mesh(g,mats[key]);
      mesh.name=String(e.o.name||e.o.id);
      mesh.userData={id:e.o.id,type:(e.o.bim&&e.o.bim.type)||e.o.t,layer:ly.name};
      node.add(mesh);
    }
    return {scene:S,count:L.length};
  }
  /* the model as a .glb; a promise of {bytes, count} */
  function bimGltfExportBytes(){
    return bimRvLoad().then(function(T){
      var R=bimGltfScene(T);
      if(!R.count)throw new Error('There is nothing shown to export');
      return new Promise(function(res,rej){
        new T.GLTFExporter().parse(R.scene,function(b){res({bytes:b,count:R.count});},function(e){rej(e);},{binary:true,onlyVisible:true});
      });
    });
  }
  function bimGltfExport(){
    a3dToast('Writing the model as glTF (the first time loads the 3D library)...');
    return bimGltfExportBytes().then(function(R){
      var a=document.createElement('a'),url=URL.createObjectURL(new Blob([R.bytes],{type:'model/gltf-binary'}));
      a.href=url;a.download=bimFileStem()+'.glb';
      document.body.appendChild(a);a.click();document.body.removeChild(a);
      setTimeout(function(){URL.revokeObjectURL(url);},4000);
      a3dToast('Saved '+a.download+': '+R.count+' element'+(R.count===1?'':'s')+', '+Math.round(R.bytes.byteLength/1024)+' KB');
      return R;
    },function(e){
      var s=String(e&&e.message||e);
      console.warn('[BIM] glTF export failed: '+s,e);
      a3dToast('glTF export failed: '+s);
      return {error:s};
    });
  }
export {
  BIM_GLTF, bimGltfArrays, bimGltfElements, bimGltfExport, bimGltfExportBytes, bimGltfFeatureEdges,
  bimGltfGather, bimGltfHex, bimGltfImportBuffer, bimGltfParts, bimGltfPick, bimGltfWeld, bimGltfWhy,
  bimImportGLTF
};
