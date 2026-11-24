

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
function bimAstFitBox(min,max,size){
  var e=[max[0]-min[0],max[1]-min[1],max[2]-min[2]];var l=e[0];if(e[1]>l)l=e[1];if(e[2]>l)l=e[2];
  var s;if(size>0&&l>0)s=size/l;else s=1;
  var m0=-(min[0]+max[0])*s/2,m1=-min[1]*s,m2=-(min[2]+max[2])*s/2;if(m0===0)m0=0;if(m1===0)m1=0;if(m2===0)m2=0;
  var s0=e[0]*s,s1=e[1]*s,s2=e[2]*s;return{scale:s,move:[m0,m1,m2],size:[s0,s1,s2]}
}
function bimAstCheck(s,b,l){
  if(s===null||typeof s!=='object'||Array.isArray(s))return['not a glTF file'];
  var m=[],t=200000,bc=20971520;
  if(l!==undefined){
    if(l.triangles!==undefined)t=l.triangles;
    if(l.bytes!==undefined)bc=l.bytes;
  }
  if(s.triangles!==undefined&&s.triangles>t)m.push(s.triangles+' triangles, over '+t);
  if(b!==undefined&&b>bc){
    var f=function(n){var s=n.toFixed(1);return s.endsWith('.0')?s.slice(0,-2):s;};
    m.push(f(b/1048576)+' MB, over '+f(bc/1048576)+' MB');
  }
  return m;
}
function bimAstCredit(e){
  if(e===null||typeof e!=='object'||Array.isArray(e))return'not a glTF file';
  if(!e.title)return'"Untitled"';
  var r='"'+e.title+'"';
  if(e.author){r=r+' by '+e.author}
  if(e.license){r=r+', '+e.license}
  if(e.source){r=r+' ('+e.source+')'}
  return r;
}
