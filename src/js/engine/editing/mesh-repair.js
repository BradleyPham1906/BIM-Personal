import { A3D } from '../core/state.js';
import { UNDO_STACK, pushUndo } from '../drawing/plan-mode-sketch.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimOcctReplace } from '../solids/occt-adapter.js';
import { bimOcctRun } from '../solids/occt-tools.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV271: FreeCAD's Mesh workbench: repair, and a mesh made a solid =================
     MESHREPAIR (FreeCAD's Mesh "Analyze and repair"): on the selected meshes, points closer than a tolerance welded
     into one, faces that collapse (two corners the same, or no area) dropped, repeated faces dropped, the faces turned
     to agree with their neighbours and then outward (a positive volume), and what is left open reported: its
     boundary edges, as holes. MESHTOSOLID (FreeCAD's Part "Shape from mesh", then "Convert to solid"): a closed mesh
     sewn into an OpenCASCADE solid, so the solid tools (V264 to V266) and STEP work on it. The repair is pure, tested
     without a page; the solid uses OpenCASCADE's sewing through replicad's makeSolid. */
  /* Weld points within tol (by a grid of tol cells, the neighbours checked), faces re-indexed. Pure. */
  function bimMeshWeld(mesh,tol){
    tol=tol>0?tol:1e-6;
    var grid={},map=[],V=[],i,k;
    function key(a,b,c){return a+','+b+','+c;}
    for(i=0;i<mesh.v.length;i++){
      var p=mesh.v[i],g=[Math.floor(p[0]/tol),Math.floor(p[1]/tol),Math.floor(p[2]/tol)],hit=-1,dx,dy,dz;
      for(dx=-1;dx<=1&&hit<0;dx++)for(dy=-1;dy<=1&&hit<0;dy++)for(dz=-1;dz<=1&&hit<0;dz++){
        var L=grid[key(g[0]+dx,g[1]+dy,g[2]+dz)];
        if(L)for(k=0;k<L.length;k++){var q=V[L[k]];if(Math.abs(q[0]-p[0])<=tol&&Math.abs(q[1]-p[1])<=tol&&Math.abs(q[2]-p[2])<=tol){hit=L[k];break;}}
      }
      if(hit<0){hit=V.length;V.push([p[0],p[1],p[2]]);var kk=key(g[0],g[1],g[2]);(grid[kk]||(grid[kk]=[])).push(hit);}
      map.push(hit);
    }
    return {v:V,f:mesh.f.map(function(fc){return fc.map(function(j){return map[j];});}),merged:mesh.v.length-V.length};
  }
  function bimMeshTriArea(a,b,c){
    var u=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],w=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];
    var x=u[1]*w[2]-u[2]*w[1],y=u[2]*w[0]-u[0]*w[2],z=u[0]*w[1]-u[1]*w[0];
    return Math.sqrt(x*x+y*y+z*z)/2;
  }
  /* Faces as triangles, the collapsed and repeated ones dropped. Pure. */
  function bimMeshCleanFaces(mesh,minArea){
    var out=[],seen={},degen=0,dup=0,i,j;
    for(i=0;i<mesh.f.length;i++){
      var fc=mesh.f[i];
      for(j=2;j<fc.length;j++){
        var t=[fc[0],fc[j-1],fc[j]];
        if(t[0]===t[1]||t[1]===t[2]||t[0]===t[2]||bimMeshTriArea(mesh.v[t[0]],mesh.v[t[1]],mesh.v[t[2]])<=(minArea||1e-12)){degen++;continue;}
        var k=t.slice().sort(function(a,b){return a-b;}).join(',');
        if(seen[k]){dup++;continue;}
        seen[k]=1;out.push(t);
      }
    }
    return {f:out,degenerate:degen,duplicates:dup};
  }
  /* Each edge's faces: {"a,b": [face indices]} with a < b. Pure. */
  function bimMeshEdges(f){
    var E={},i,j;
    for(i=0;i<f.length;i++)for(j=0;j<3;j++){var a=f[i][j],b=f[i][(j+1)%3],k=a<b?a+','+b:b+','+a;(E[k]||(E[k]=[])).push(i);}
    return E;
  }
  /* The faces turned to agree with their neighbours (each shared edge run opposite ways), part by part, then each
     closed part turned outward (positive signed volume). Returns the faces and how many were turned. Pure. */
  function bimMeshOrient(v,f){
    var F=f.map(function(t){return t.slice();}),E=bimMeshEdges(F),done=new Array(F.length),turned=0,i;
    function has(t,a,b){return (t[0]===a&&t[1]===b)||(t[1]===a&&t[2]===b)||(t[2]===a&&t[0]===b);}
    for(i=0;i<F.length;i++){
      if(done[i])continue;
      var part=[i],q=[i];done[i]=true;
      while(q.length){
        var c=q.pop(),t=F[c],j;
        for(j=0;j<3;j++){
          var a=t[j],b=t[(j+1)%3],L=E[a<b?a+','+b:b+','+a],m;
          for(m=0;m<L.length;m++){
            var n=L[m];if(done[n])continue;
            if(has(F[n],a,b)){F[n].reverse();turned++;}   /* the neighbour runs the edge the same way: turn it */
            done[n]=true;q.push(n);part.push(n);
          }
        }
      }
      var vol=0;
      part.forEach(function(k){var A=v[F[k][0]],B=v[F[k][1]],C=v[F[k][2]];
        vol+=(A[0]*(B[1]*C[2]-B[2]*C[1])-A[1]*(B[0]*C[2]-B[2]*C[0])+A[2]*(B[0]*C[1]-B[1]*C[0]))/6;});
      if(vol<0){part.forEach(function(k){F[k].reverse();});turned+=part.length;}
    }
    return {f:F,turned:turned};
  }
  /* The whole repair, and its report. Pure. */
  function bimMeshRepair(mesh,tol){
    var w=bimMeshWeld(mesh,tol),c=bimMeshCleanFaces(w),o=bimMeshOrient(w.v,c.f),E=bimMeshEdges(o.f),open=0,nonManifold=0,k;
    for(k in E){if(E[k].length===1)open++;else if(E[k].length>2)nonManifold++;}
    /* the points no face uses, dropped */
    var used={},V=[],map={},i;
    o.f.forEach(function(t){used[t[0]]=used[t[1]]=used[t[2]]=1;});
    for(i=0;i<w.v.length;i++)if(used[i]){map[i]=V.length;V.push(w.v[i]);}
    return {mesh:{v:V,f:o.f.map(function(t){return [map[t[0]],map[t[1]],map[t[2]]];})},
      report:{merged:w.merged,degenerate:c.degenerate,duplicates:c.duplicates,turned:o.turned,openEdges:open,nonManifold:nonManifold,closed:!open&&!nonManifold}};
  }
  function bimMeshSel(){
    var ids=(A3D.selSet&&A3D.selSet.length)?A3D.selSet.slice():(A3D.sel?[A3D.sel]:[]);
    return ids.map(objById).filter(function(o){return o&&o.mesh&&o.mesh.f&&o.mesh.f.length&&!o.bim;});
  }
  function bimMeshRepairCommand(){
    var L=bimMeshSel(),i,msg=[];
    if(!L.length){a3dToast('MESHREPAIR: select meshes (an STL, OBJ or SketchUp import, a solid)');return null;}
    pushUndo();
    for(i=0;i<L.length;i++){
      var r=bimMeshRepair(L[i].mesh,1e-6),R=r.report;
      L[i].mesh=r.mesh;if(L[i].occt)delete L[i].occt;
      msg.push(L[i].name+': '+R.merged+' points welded, '+(R.degenerate+R.duplicates)+' faces dropped, '+R.turned+' turned; '+
        (R.closed?'closed':(R.openEdges+' open edges'+(R.nonManifold?', '+R.nonManifold+' shared by 3 or more faces':''))));
    }
    A3D.meshes={};
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast(msg.join(' | '));
    return msg;
  }
  /* A closed mesh sewn into a solid (its points where the mesh has them, the offset kept by pos). */
  function bimMeshToSolidShape(R,mesh){
    var faces=[],i;
    for(i=0;i<mesh.f.length;i++){
      var t=mesh.f[i];
      faces.push(R.makePolygon([0,1,2].map(function(j){var p=mesh.v[t[j]];return [p[0],-p[2],p[1]];})));   /* app to OpenCASCADE */
    }
    return R.makeSolid(faces);
  }
  function bimMeshToSolidCommand(){
    var L=bimMeshSel();
    if(!L.length){a3dToast('MESHTOSOLID: select closed meshes');return null;}
    return bimOcctRun('MESHTOSOLID',function(R){
      var n=0,bad=[],i;
      pushUndo();
      for(i=0;i<L.length;i++){
        var r=bimMeshRepair(L[i].mesh,1e-6);
        if(!r.report.closed){bad.push(L[i].name+' ('+r.report.openEdges+' open edges)');continue;}
        if(r.mesh.f.length>20000){bad.push(L[i].name+' (over 20,000 faces)');continue;}
        var s=bimMeshToSolidShape(R,r.mesh);
        if(bimOcctReplace(L[i],s))n++;
      }
      if(!n)UNDO_STACK.pop();
      refreshTree();paint();saveSoon();
      a3dToast('MESHTOSOLID: '+n+' solid(s)'+(bad.length?'; not closed or too large: '+bad.join(', '):''));
      return n;
    });
  }
export { bimMeshRepairCommand, bimMeshToSolidCommand };
