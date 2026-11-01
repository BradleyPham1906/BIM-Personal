  // ---- __acad3dV21: Family Library. Persists SEPARATELY from project data (its own localStorage
  // key, like UI prefs) since a family library is reusable content meant to survive across
  // different projects, not something that should live inside or reset with any one project
  // file. Placed instances are deliberately INDEPENDENT copies (per explicit product decision) --
  // editing a library entry later never retroactively changes anything already placed. ----
  var FAMILY_LIB_KEY='acad3dFamilyLibrary';
  var A3D_FAMLIB_SAVE_FAILED=false;   /* __acad3dV124b: a run of failed saves is toasted once */
  var FAMILY_CATEGORIES=['Doors','Windows','Furniture','Fixtures','Structural','Other'];
  var A3D_FAMLIB=bimLoadFamilyLibrary();
  function bimMeshBounds(mesh){
    var mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity],i,k;
    for(i=0;i<mesh.v.length;i++)for(k=0;k<3;k++){
      if(mesh.v[i][k]<mn[k])mn[k]=mesh.v[i][k];
      if(mesh.v[i][k]>mx[k])mx[k]=mesh.v[i][k];
    }
    return {mn:mn,mx:mx};
  }
  function bimNormalizeMeshForFamily(mesh){
    if(!mesh||!mesh.v||!mesh.v.length)return {v:[],f:mesh?mesh.f:[]};
    var b=bimMeshBounds(mesh);
    var cx=(b.mn[0]+b.mx[0])/2,cz=(b.mn[2]+b.mx[2])/2,baseY=b.mn[1];
    var newV=mesh.v.map(function(v3){return [v3[0]-cx,v3[1]-baseY,v3[2]-cz];});
    return {v:newV,f:mesh.f,size:[b.mx[0]-b.mn[0],b.mx[1]-b.mn[1],b.mx[2]-b.mn[2]]};
  }
  function bimCloneMesh(mesh){
    return {v:mesh.v.map(function(p){return [p[0],p[1],p[2]];}),f:mesh.f.map(function(fc){return fc.slice();})};
  }
  function bimMergeMeshes(meshes){
    var v=[],f=[],offset=0,i,j;
    for(i=0;i<meshes.length;i++){
      var m=meshes[i];
      for(j=0;j<m.v.length;j++)v.push(m.v[j]);
      for(j=0;j<m.f.length;j++)f.push(m.f[j].map(function(idx){return idx+offset;}));
      offset+=m.v.length;
    }
    return {v:v,f:f};
  }
  function bimLoadFamilyLibrary(){
    try{
      var raw=localStorage.getItem(FAMILY_LIB_KEY);
      if(raw){var parsed=JSON.parse(raw);if(Array.isArray(parsed))return parsed;}
    }catch(eL){console.warn('[BIM] Corrupted family library, starting empty.',eL);}
    return [];
  }
  /* __acad3dV124b: a library the browser refuses is warned and toasted, as the project is (save3d) */
  function bimSaveFamilyLibrary(){
    try{
      localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify(A3D_FAMLIB));
      if(A3D_FAMLIB_SAVE_FAILED){A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');}
      return true;
    }catch(eS){
      console.warn('[BIM] Could not persist family library: ',eS);
      if(!A3D_FAMLIB_SAVE_FAILED){
        A3D_FAMLIB_SAVE_FAILED=true;
        a3dToast('The Assets library could not be saved: browser storage is full. New assets will be lost when the page reloads; remove assets you no longer need.');
      }
      return false;
    }
  }
  function bimFamilyLibraryAdd(fam){
    var entry={
      id:'fam-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      kind:'model',   /* __acad3dV124 */
      name:fam.name,category:fam.category||'Other',manufacturer:fam.manufacturer||'',
      mesh:bimNormalizeMeshForFamily(fam.mesh),createdAt:new Date().toISOString()
    };
    /* __acad3dV124: the unit and the file an imported model came from, and its thumbnail */
    if(fam.unit)entry.unit=fam.unit;
    if(fam.source)entry.source=fam.source;
    entry.thumb=bimMeshThumb(entry.mesh);
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }
  function bimFamilyLibraryRemove(id){
    var idx=-1,i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id){idx=i;break;}
    if(idx<0)return false;
    /* __acad3dV124: a template's project is stored under its own key, and goes with it */
    if(bimAssetKind(A3D_FAMLIB[idx])==='template'){
      try{localStorage.removeItem(A3D_TEMPLATE_PREFIX+id);}
      catch(eR){console.warn('[BIM] A template\'s stored project could not be removed.',eR);}
    }
    A3D_FAMLIB.splice(idx,1);
    bimSaveFamilyLibrary();
    return true;
  }
  function bimFamilyLibraryGet(id){
    var i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id)return A3D_FAMLIB[i];
    /* __acad3dV124: the starter set resolves through the same lookup, so every placement path
       takes it unchanged */
    for(i=0;i<A3D_ASSET_BUILTINS.length;i++)if(A3D_ASSET_BUILTINS[i].id===id)return A3D_ASSET_BUILTINS[i];
    return null;
  }
  /* ================= __acad3dV124: the Assets library =================
     One store, three kinds: a MODEL is a mesh placed as an independent instance (every entry
     written before V124 is one), a BLOCK is a set of object records inserted as independent copies,
     a TEMPLATE is a starting project. The kind is read here and nowhere else, so an entry without
     one is a model and nothing already stored has to be rewritten. */
  var A3D_TEMPLATE_PREFIX='acad3dTemplateV1:';
  function bimAssetKind(e){
    var k=e&&e.kind;
    return (k==='block'||k==='template')?k:'model';
  }
  /* the user's entries of one kind, in the library's own order */
  function bimLibEntries(kind){
    var out=[],i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(bimAssetKind(A3D_FAMLIB[i])===kind)out.push(A3D_FAMLIB[i]);
    return out;
  }
  /* A mesh made of parts, each a box [cx,cy,cz,lx,ly,lz] or a cylinder {cyl:[cx,cy,cz,r,h]}, with
     its centre given in metres and its base on y=0 once it is normalised. */
  function bimAsmMesh(parts){
    var meshes=[],i,j;
    for(i=0;i<parts.length;i++){
      var p=parts[i],m,c;
      if(p.cyl){m=mkCylP(p.cyl[3],p.cyl[4],360,20);c=[p.cyl[0],p.cyl[1],p.cyl[2]];}
      else{m=mkBoxP(p[3],p[4],p[5]);c=[p[0],p[1],p[2]];}
      var mv=[];
      for(j=0;j<m.v.length;j++)mv.push([m.v[j][0]+c[0],m.v[j][1]+c[1],m.v[j][2]+c[2]]);
      meshes.push({v:mv,f:m.f});
    }
    return bimMergeMeshes(meshes);
  }
  /* The starter set: real sizes, in metres. Front is +Z. */
  var A3D_ASSET_STARTER=[
    {k:'chair',name:'Chair',cat:'Furniture',parts:[[-0.2,0.225,0.2,0.04,0.45,0.04],[0.2,0.225,0.2,0.04,0.45,0.04],
      [-0.2,0.225,-0.2,0.04,0.45,0.04],[0.2,0.225,-0.2,0.04,0.45,0.04],[0,0.47,0,0.45,0.05,0.45],
      [0,0.72,-0.205,0.45,0.45,0.04]]},
    {k:'table',name:'Dining table',cat:'Furniture',parts:[[0,0.73,0,1.6,0.04,0.9],[-0.74,0.355,-0.39,0.06,0.71,0.06],
      [0.74,0.355,-0.39,0.06,0.71,0.06],[-0.74,0.355,0.39,0.06,0.71,0.06],[0.74,0.355,0.39,0.06,0.71,0.06]]},
    {k:'desk',name:'Desk',cat:'Furniture',parts:[[0,0.73,0,1.4,0.04,0.7],[-0.68,0.355,0,0.04,0.71,0.66],
      [0.68,0.355,0,0.04,0.71,0.66],[0,0.45,-0.3,1.32,0.4,0.02]]},
    {k:'bed',name:'Double bed',cat:'Furniture',parts:[[0,0.175,0.03,1.6,0.35,2.04],[0,0.45,0.05,1.5,0.2,1.95],
      [0,0.45,-1.02,1.6,0.9,0.06]]},
    {k:'sofa',name:'Sofa',cat:'Furniture',parts:[[0,0.2,0.05,1.6,0.4,0.8],[0,0.625,-0.35,2.0,0.45,0.2],
      [-0.9,0.325,0.05,0.2,0.65,0.8],[0.9,0.325,0.05,0.2,0.65,0.8]]},
    {k:'cabinet',name:'Base cabinet',cat:'Furniture',parts:[[0,0.43,0,0.6,0.86,0.58],[0,0.88,0.01,0.62,0.04,0.6]]},
    {k:'wc',name:'WC',cat:'Fixtures',parts:[{cyl:[0,0.2,0.12,0.19,0.4]},[0,0.575,-0.17,0.4,0.35,0.18]]},
    {k:'basin',name:'Basin',cat:'Fixtures',parts:[{cyl:[0,0.35,0,0.08,0.7]},[0,0.78,0.05,0.55,0.16,0.45]]},
    {k:'bath',name:'Bathtub',cat:'Fixtures',parts:[[0,0.275,0,1.7,0.55,0.75]]}
  ];
  var A3D_ASSET_BUILTINS=A3D_ASSET_STARTER.map(function(s){
    return {id:'builtin:'+s.k,kind:'model',builtin:true,name:s.name,category:s.cat,manufacturer:'',
      mesh:bimNormalizeMeshForFamily(bimAsmMesh(s.parts)),thumb:''};
  });

