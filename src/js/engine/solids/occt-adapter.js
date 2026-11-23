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
     o.occt.brep, with a signature of the mesh it made. A mesh tool that turns, mirrors or scales the mesh evenly keeps
     it a solid: the B-rep follows the same map (V266, bimOcctShapeOf). One that stretches or rebuilds it (a plan-only
     SCALE, push and pull) leaves it a mesh, rather than a shape it no longer matches. */
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
  /* __acad3dV266: a solid whose mesh a mesh tool moved, turned, mirrored or scaled (ROTATE, MIRROR, SCALE, the gizmo)
     is still a solid: the same vertices in the same order, carried by one affine map. Its sizes still match the
     signature's, and bimOcctShapeOf finds the map and carries the B-rep with it. */
  function bimOcctSigSizes(sig){var m=/^(\d+):(\d+):/.exec(String(sig||''));return m?[+m[1],+m[2]]:null;}
  function bimOcctIsSolid(o){
    if(!(o&&o.occt&&typeof o.occt.brep==='string'&&o.mesh&&o.mesh.v))return false;
    if(o.occt.sig===bimOcctSig(o.mesh))return true;
    var n=bimOcctSigSizes(o.occt.sig);
    return !!(n&&n[0]===o.mesh.v.length&&n[1]===o.mesh.f.length&&!o.occt.lost);
  }
  /* The affine map that takes points P to points Q (q = A p + t), by least squares, and how well it fits: the largest
     distance left, and whether A is a turn, a mirror and one scale (a similarity), which a B-rep can follow; a stretch
     cannot. Pure. */
  function bimOcctFitAffine(P,Q){
    var n=Math.min(P.length,Q.length),M=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],B=[[0,0,0,0],[0,0,0,0],[0,0,0,0]],i,j,k;
    if(n<4)return null;
    for(i=0;i<n;i++){
      var p=[P[i][0],P[i][1],P[i][2],1];
      for(j=0;j<4;j++){for(k=0;k<4;k++)M[j][k]+=p[j]*p[k];for(k=0;k<3;k++)B[k][j]+=Q[i][k]*p[j];}
    }
    var X=[];
    for(k=0;k<3;k++){var x=bimOcctSolve4(M,B[k]);if(!x)return null;X.push(x);}
    var A=[[X[0][0],X[0][1],X[0][2]],[X[1][0],X[1][1],X[1][2]],[X[2][0],X[2][1],X[2][2]]],t=[X[0][3],X[1][3],X[2][3]];
    var err=0,size=0;
    for(i=0;i<n;i++){
      var d=0;
      for(k=0;k<3;k++){var q=A[k][0]*P[i][0]+A[k][1]*P[i][1]+A[k][2]*P[i][2]+t[k];d+=(q-Q[i][k])*(q-Q[i][k]);size=Math.max(size,Math.abs(Q[i][k]));}
      err=Math.max(err,Math.sqrt(d));
    }
    var det=A[0][0]*(A[1][1]*A[2][2]-A[1][2]*A[2][1])-A[0][1]*(A[1][0]*A[2][2]-A[1][2]*A[2][0])+A[0][2]*(A[1][0]*A[2][1]-A[1][1]*A[2][0]);
    var s=Math.pow(Math.abs(det),1/3),sim=s>1e-9;
    for(j=0;j<3&&sim;j++)for(k=0;k<3;k++){
      var dot=A[0][j]*A[0][k]+A[1][j]*A[1][k]+A[2][j]*A[2][k];
      if(Math.abs(dot-(j===k?s*s:0))>1e-6*Math.max(1,s*s)){sim=false;break;}
    }
    return {A:A,t:t,err:err,ok:err<=1e-6*Math.max(1,size),similar:sim,det:det,s:s};
  }
  function bimOcctSolve4(M,b){
    var a=M.map(function(r,i){return r.slice().concat([b[i]]);}),i,j,k;
    for(i=0;i<4;i++){
      var piv=i;for(j=i+1;j<4;j++)if(Math.abs(a[j][i])>Math.abs(a[piv][i]))piv=j;
      if(Math.abs(a[piv][i])<1e-12)return null;
      var tmp=a[i];a[i]=a[piv];a[piv]=tmp;
      for(j=0;j<4;j++){if(j===i)continue;var f=a[j][i]/a[i][i];for(k=i;k<5;k++)a[j][k]-=f*a[i][k];}
    }
    return [a[0][4]/a[0][0],a[1][4]/a[1][1],a[2][4]/a[2][2],a[3][4]/a[3][3]];
  }
  /* The app's map in OpenCASCADE's frame: (X, Y, Z) = (x, -z, y) is the turn Q, so A' = Q A Q^T and t' = Q t. Pure. */
  function bimOcctAffineToOcc(A,t){
    var Q=[[1,0,0],[0,0,-1],[0,1,0]],QA=[[0,0,0],[0,0,0],[0,0,0]],R=[[0,0,0],[0,0,0],[0,0,0]],i,j,k;
    for(i=0;i<3;i++)for(j=0;j<3;j++)for(k=0;k<3;k++)QA[i][j]+=Q[i][k]*A[k][j];
    for(i=0;i<3;i++)for(j=0;j<3;j++)for(k=0;k<3;k++)R[i][j]+=QA[i][k]*Q[j][k];
    return {A:R,t:[t[0],-t[2],t[1]]};
  }
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
  function bimOcctShapeOf(R,o){
    var s=R.deserializeShape(o.occt.brep);
    if(o.occt.sig===bimOcctSig(o.mesh))return s;
    /* __acad3dV266: a mesh tool moved the mesh; find its map from the mesh the B-rep makes, and follow it */
    var m0=bimOcctMesh(s),fit=(m0.v.length===o.mesh.v.length)?bimOcctFitAffine(m0.v,o.mesh.v):null;
    if(!fit||!fit.ok||!fit.similar){
      o.occt.lost=true;
      throw new Error(o.name+' was '+(fit&&fit.ok?'stretched':'reshaped')+' by a mesh tool, so it is no longer edited as a solid');
    }
    var F=bimOcctAffineToOcc(fit.A,fit.t),oc=R.getOC(),tr=new oc.gp_Trsf();
    tr.SetValues(F.A[0][0],F.A[0][1],F.A[0][2],F.t[0],F.A[1][0],F.A[1][1],F.A[1][2],F.t[1],F.A[2][0],F.A[2][1],F.A[2][2],F.t[2]);
    var bt=new oc.BRepBuilderAPI_Transform(s.wrapped,tr,true),out=R.cast(bt.Shape());
    tr.delete();bt.delete();
    o.occt={brep:out.serialize(),sig:bimOcctSig(o.mesh),v:BIM_OCCT.ver};   /* the B-rep follows; the mesh stays as the tool left it */
    return out;
  }
  /* The shape where the model shows it: a solid moved by MOVE keeps its B-rep where it was made, and its offset
     (o.pos) on top, as its mesh does; booleans between solids and STEP need them where they are. */
  function bimOcctOffsetXYZ(pos){return [pos[0]||0,-(pos[2]||0),pos[1]||0];}
  function bimOcctShapeAt(R,o,rel){
    var q=bimObjOffset(o),b=rel?bimObjOffset(rel):[0,0,0],d=bimOcctOffsetXYZ([q[0]-b[0],q[1]-b[1],q[2]-b[2]]),s=bimOcctShapeOf(R,o);
    return (d[0]||d[1]||d[2])?s.translate(d[0],d[1],d[2]):s;
  }
export {
  A3D_OCCT, bimOcctAddSolid, bimOcctDrawing, bimOcctIsSolid, bimOcctLoad, bimOcctOffsetXYZ, bimOcctPt,
  bimOcctReplace, bimOcctShapeAt, bimOcctShapeOf
};
