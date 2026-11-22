import { A3D } from '../core/state.js';
import { bimObjOffset } from '../drawing/plan-mode-sketch.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { BIM_BULGE_EPS, bimBulgeAt, bimBulgedSignedArea } from '../drawing/arc-storage.js';

  /* ================= __acad3dV264: OpenCASCADE, through replicad (the owner's approval, 2026-11-22: "Yes go ahead") =================
     FreeCAD's own geometry kernel, for what FreeCAD's Part and PartDesign do and this app's meshes cannot: true solids,
     fillets and chamfers on their edges, shells, revolves, lofts, STEP. docs/research/research-occt-library.md.

     The runtime is runtime/occt/<ver>/ (tools/occt/build_occt.mjs): bim-replicad.min.js (replicad, MIT; global
     BIMREPLICAD) and the OpenCASCADE build it drives, replicad_single.js and .wasm (LGPL-2.1, their own unchanged files),
     fetched only the first time a solid tool is used. This file is the only one that calls them.

     The plan is the app's x and z with y up; OpenCASCADE's is X, Y with Z up. (x, y, z) goes to (X, Y, Z) = (x, -z, y),
     a turn rather than a reflection, so faces keep their winding; a bulge changes sign with the plan's north-up flip, as
     the DXF writer's does (export-mappings.js). A solid keeps its OpenCASCADE shape as replicad's serialized text in
     o.occt.brep, with a signature of the mesh it made; a mesh tool that changes the mesh afterwards (rotate, scale,
     push and pull) leaves the signature behind, and the solid is then no longer edited as a B-rep, rather than from a
     shape it no longer matches. */
  var BIM_OCCT={ver:'1.2.1',dir:'occt/1.2.1/',lib:'bim-replicad.min.js',loader:'replicad_single.js',wasm:'replicad_single.wasm',
    sri:'sha256-hpbD1EWm6C2UdV5h1R+k5GlTKeXiUht9ADDHuoZNr18=',mesh:{tolerance:0.005,angularTolerance:10}};
  var A3D_OCCT={load:null,st:'',err:'',R:null};
  /* ---------- pure: the plan to OpenCASCADE and back ---------- */
  function bimOcctPt(p){return [p[0],-p[1]];}
  /* A closed outline (the app's points and bulges) in OpenCASCADE's plane, counter-clockwise. The turn to (X, Y) mirrors
     the plan, so the points are taken there with their bulges negated; an outline that then runs clockwise is walked
     the other way (points reversed, bulges reversed and negated). A clockwise face extrudes into a solid turned inside
     out, whose volume still reads positive but whose booleans come out wrong: two overlapping boxes fused to the sum
     of their volumes (found by V264's browser check). */
  function bimOcctOutline(pts,bulges){
    var n=pts.length,P=pts.map(bimOcctPt),B=[],i;
    for(i=0;i<n;i++)B.push(-bimBulgeAt(bulges,i));
    if(bimBulgedSignedArea(P,B,true)<0){
      var P2=[],B2=[];
      for(i=0;i<n;i++)P2.push(P[(n-i)%n]);
      for(i=0;i<n;i++)B2.push(-B[(n-1-i+n)%n]);
      P=P2;B=B2;
    }
    return {pts:P,bulges:B};
  }
  /* The outline drawn with replicad's pen. */
  function bimOcctDrawing(R,pts,bulges){
    var n=pts.length,i,b,d,O;
    if(n<2)return null;
    O=bimOcctOutline(pts,bulges);
    d=R.draw(O.pts[0]);
    for(i=0;i<n;i++){
      var q=O.pts[(i+1)%n];b=O.bulges[i];
      if(i===n-1){
        if(Math.abs(b)>BIM_BULGE_EPS)d=d.bulgeArcTo(q,b);
        break;
      }
      d=Math.abs(b)>BIM_BULGE_EPS?d.bulgeArcTo(q,b):d.lineTo(q);
    }
    return d.close();
  }
  /* replicad's mesh as the app's: vertices (X, Y, Z) to (x, y, z) = (X, Z, -Y), triangles as faces. */
  function bimOcctMeshToApp(m){
    var v=[],f=[],i;
    for(i=0;i+2<m.vertices.length;i+=3)v.push([m.vertices[i],m.vertices[i+2],-m.vertices[i+1]]);
    for(i=0;i+2<m.triangles.length;i+=3)f.push([m.triangles[i],m.triangles[i+1],m.triangles[i+2]]);
    return {v:v,f:f};
  }
  /* A mesh's signature: its sizes and a coarse sum of its coordinates, enough to tell that a mesh tool changed it. */
  function bimOcctSig(mesh){
    var s=0,i;
    for(i=0;i<mesh.v.length;i++)s+=mesh.v[i][0]*1.3+mesh.v[i][1]*1.7+mesh.v[i][2]*1.9;
    return mesh.v.length+':'+mesh.f.length+':'+s.toFixed(4);
  }
  function bimOcctIsSolid(o){return !!(o&&o.occt&&typeof o.occt.brep==='string'&&o.mesh&&o.occt.sig===bimOcctSig(o.mesh));}
  /* ---------- loading ---------- */
  function bimOcctBases(){
    var p=String(window.location&&window.location.protocol||''),out=[];
    if(p!=='http:'&&p!=='https:')out.push({b:'runtime/',sri:false});
    out.push({b:String(bimLbBase()),sri:true});
    return out;
  }
  function bimOcctScript(u,sri){
    return new Promise(function(res,rej){
      var t=document.createElement('script');
      t.src=u;if(sri){t.integrity=BIM_OCCT.sri;t.crossOrigin='anonymous';}
      t.onload=function(){res();};
      t.onerror=function(){if(t.parentNode)t.parentNode.removeChild(t);rej(new Error('could not load '+u));};
      document.head.appendChild(t);
    });
  }
  /* The OpenCASCADE loader is an ES module (it finds its wasm by import.meta.url); a dynamic import made through the
     Function constructor keeps this file's own code ES5. */
  var bimOcctImport=null;
  function bimOcctModule(u){
    if(!bimOcctImport)bimOcctImport=new Function('u','return import(u);');
    return bimOcctImport(u);
  }
  function bimOcctLoad(){
    var S=A3D_OCCT;
    if(S.load)return S.load;
    var bases=bimOcctBases(),k=0;
    S.st='loading';
    function attempt(){
      if(k>=bases.length)return Promise.reject(new Error('the solid modeller could not be loaded from '+bases.map(function(x){return x.b+BIM_OCCT.dir;}).join(' or ')));
      var B=bases[k++],dir=B.b+BIM_OCCT.dir;
      var lib=window.BIMREPLICAD?Promise.resolve():bimOcctScript(dir+BIM_OCCT.lib,B.sri);
      return lib.then(function(){return bimOcctModule(new URL(dir+BIM_OCCT.loader,document.baseURI).href);})
        .then(function(mod){return mod.default({locateFile:function(){return new URL(dir+BIM_OCCT.wasm,document.baseURI).href;}});})
        .then(function(oc){window.BIMREPLICAD.setOC(oc);S.R=window.BIMREPLICAD;S.st='ready';return S.R;},
          function(e){console.warn('[BIM] OpenCASCADE from '+dir+' failed: '+(e&&e.message||e));return attempt();});
    }
    S.load=attempt().catch(function(e){S.st='failed';S.err=String(e&&e.message||e);S.load=null;throw e;});
    return S.load;
  }
  /* ---------- solids in the model ---------- */
  function bimOcctMesh(shape){return bimOcctMeshToApp(shape.mesh(BIM_OCCT.mesh));}
  /* A new solid object from an OpenCASCADE shape, on the active layer. */
  function bimOcctAddSolid(shape,name){
    var mesh=bimOcctMesh(shape);
    if(!mesh.f.length)return null;
    A3D.counts.solid=(A3D.counts.solid||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',name:(name||'Solid')+' '+A3D.counts.solid,col:'#b9c7d6',
      pos:[0,0,0],mesh:mesh,layer:A3D.activeLayer,occt:{brep:shape.serialize(),sig:bimOcctSig(mesh),v:BIM_OCCT.ver}};
    A3D.objs.push(o);
    return o;
  }
  /* An existing solid given a new shape (a fillet, a shell): its mesh and its B-rep together. */
  function bimOcctReplace(o,shape){
    var mesh=bimOcctMesh(shape);
    if(!mesh.f.length)return false;
    o.mesh=mesh;o.occt={brep:shape.serialize(),sig:bimOcctSig(mesh),v:BIM_OCCT.ver};
    A3D.meshes={};
    return true;
  }
  function bimOcctShapeOf(R,o){return R.deserializeShape(o.occt.brep);}
  /* The shape where the model shows it: a solid moved by MOVE keeps its B-rep where it was made, and its offset
     (o.pos) on top, as its mesh does; booleans between solids and STEP need them where they are. */
  function bimOcctOffsetXYZ(pos){return [pos[0]||0,-(pos[2]||0),pos[1]||0];}
  function bimOcctShapeAt(R,o,rel){
    var q=bimObjOffset(o),b=rel?bimObjOffset(rel):[0,0,0],d=bimOcctOffsetXYZ([q[0]-b[0],q[1]-b[1],q[2]-b[2]]),s=bimOcctShapeOf(R,o);
    return (d[0]||d[1]||d[2])?s.translate(d[0],d[1],d[2]):s;
  }
export {
  A3D_OCCT, bimOcctAddSolid, bimOcctDrawing, bimOcctIsSolid, bimOcctLoad, bimOcctPt, bimOcctReplace,
  bimOcctShapeAt, bimOcctShapeOf
};
