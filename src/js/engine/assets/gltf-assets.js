

  /* ================= __acad3dV207: glTF models in Assets, and valdrada's credited models, the pure part =================
     docs/research/research-notion-gltf-assets.md and docs/work-orders/v207/SPEC.md. A glTF's counts from its JSON, a model
     seated on the origin, the limits that ask first, the credit line. Each function is a work order, added below as it is
     built; none uses another file's names. */
function bimAstGltfStats(g){
  if(g===null)return null;if(typeof g!=='object')return null;
  var m=0,p=0,t=0,mat=0,tex=0,ext;
  if(g.accessors!==undefined){
    if(g.extensionsUsed!==undefined){
      var a=[];for(var i=0;i<g.extensionsUsed.length;i++)a[a.length]=g.extensionsUsed[i];ext=a.sort()
    }
  }
  if(g.meshes!==undefined){
    for(var r=0;r<g.meshes.length;r++){
      m++;var mg=g.meshes[r];
      if(mg.primitives!==undefined){
        for(var k=0;k<mg.primitives.length;k++){
          p++;var pr=mg.primitives[k];var mo=pr.mode;
          if(mo===4||mo===undefined){
            var co;if(pr.indices!==undefined){var ai=pr.indices;if(g.accessors[ai]!==undefined)co=g.accessors[ai].count;else co=0}else{var pa=pr.attributes?pr.attributes.POSITION:undefined;if(pa!==undefined){if(g.accessors[pa]!==undefined)co=g.accessors[pa].count;else co=0}else co=0;}t+=Math.floor(co/3)
          }
        }
      }
    }
  }
  if(g.materials!==undefined)mat=g.materials.length;
  if(g.textures!==undefined)tex=g.textures.length;
  return{meshes:m,primitives:p,triangles:t,materials:mat,textures:tex,extensions:ext}
}
