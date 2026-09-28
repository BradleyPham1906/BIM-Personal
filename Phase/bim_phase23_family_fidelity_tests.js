var STORE={};
var localStorage={
  getItem:function(k){return STORE.hasOwnProperty(k)?STORE[k]:null;},
  setItem:function(k,v){STORE[k]=String(v);}
};
var FAMILY_LIB_KEY='acad3dFamilyLibrary';
var A3D_FAMLIB=[];
var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}]};
var UNDO_STACK=[];
function pushUndo(){UNDO_STACK.push(1);}
function refreshTree(){}
function refreshHud(){}
function paint(){}
function saveSoon(){}
var TOASTS=[];
function a3dToast(m){TOASTS.push(m);}
function bimGetActiveLevel(){return A3D.levels[0];}
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

  function bimSaveFamilyLibrary(){
    try{localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify(A3D_FAMLIB));}catch(eS){console.warn('[BIM] Could not persist family library: ',eS);}
  }

  function bimFamilyLibraryAdd(fam){
    var entry={
      id:'fam-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      name:fam.name,category:fam.category||'Other',manufacturer:fam.manufacturer||'',
      mesh:bimNormalizeMeshForFamily(fam.mesh),createdAt:new Date().toISOString()
    };
    A3D_FAMLIB.push(entry);
    bimSaveFamilyLibrary();
    return entry;
  }

  function bimFamilyLibraryRemove(id){
    var idx=-1,i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id){idx=i;break;}
    if(idx<0)return false;
    A3D_FAMLIB.splice(idx,1);
    bimSaveFamilyLibrary();
    return true;
  }

  function bimFamilyLibraryGet(id){
    var i;
    for(i=0;i<A3D_FAMLIB.length;i++)if(A3D_FAMLIB[i].id===id)return A3D_FAMLIB[i];
    return null;
  }

  function bimCreateFamilyInstance(fam,posXZ,levelElev,seq){
    var meshCopy=bimCloneMesh(fam.mesh);
    return {
      id:'a3d-'+Date.now().toString(36)+'-'+seq,t:'solid',name:fam.name+'_'+seq,
      pos:[posXZ[0],levelElev,posXZ[1]],mesh:meshCopy,
      bim:{type:'familyInstance',familyId:fam.id,familyName:fam.name,category:fam.category}
    };
  }

  function bimPlaceFamilyInstance(fam,posXZ){
    pushUndo();
    A3D.counts.familyInstance=(A3D.counts.familyInstance||0)+1;
    var lvl=bimGetActiveLevel();
    var inst=bimCreateFamilyInstance(fam,posXZ,lvl.elev,A3D.counts.familyInstance);
    inst.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
    inst.layer=A3D.activeLayer;
    inst.bim.levelId=A3D.activeLevel;
    A3D.objs.push(inst);
    A3D.sel=inst.id;A3D.sel2=null;A3D.selSet=[inst.id];
    refreshTree();refreshHud();paint();saveSoon();
    a3dToast(inst.name+' placed');
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

  function meshOf(o){
    if(A3D.section&&A3D.section.cutMeshes&&A3D.section.cutMeshes.hasOwnProperty(o.id))return A3D.section.cutMeshes[o.id];
    if(o.mesh)return o.mesh;
    var key=o.t+'|'+JSON.stringify(o.prm||{});
    if(!A3D.meshes[key]){
      var tp=TYPES[o.t];
      if(!tp)return null;
      A3D.meshes[key]=tp.mk(mergePrm(o.t,o.prm));
    }
    return A3D.meshes[key];
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- 1. Add a family via the REAL embedded pipeline, verify persistence ----
var weirdMesh={v:[[10,5,20],[14,5,20],[14,5,24],[10,5,24],[10,9,20],[14,9,20],[14,9,24],[10,9,24]],f:[[0,1,2,3]]};
var doorFam=bimFamilyLibraryAdd({name:'Standard Door',category:'Doors',mesh:weirdMesh});
assert('real embedded add creates an entry with a generated id', !!doorFam.id);
assert('real embedded add normalizes the mesh (sits on Y=0)', bimMeshBounds(doorFam.mesh).mn[1]===0);
assert('real embedded add persists to localStorage immediately', STORE[FAMILY_LIB_KEY]&&STORE[FAMILY_LIB_KEY].indexOf('Standard Door')>=0);

// ---- 2. Simulate a fresh page load: reload the library from storage ----
var reloaded=bimLoadFamilyLibrary();
assert('reloading from storage recovers the saved family', reloaded.length===1&&reloaded[0].name==='Standard Door');

// ---- 3. Object-to-family via meshOf (matching how "Save as Family" actually pulls geometry) ----
var boxObj={id:'box1',t:'solid',name:'Wedge_1',mesh:weirdMesh,pos:[0,0,0]};
var pulledMesh=meshOf(boxObj);
assert('meshOf correctly resolves the geometry that Save-as-Family would capture', pulledMesh===weirdMesh);

// ---- 4. Placement: the real embedded bimPlaceFamilyInstance, full workflow ----
A3D.objs=[];
UNDO_STACK.length=0;
bimPlaceFamilyInstance(doorFam,[5,3]);
assert('placing an instance adds exactly one object to the model', A3D.objs.length===1);
assert('placing pushes exactly one undo snapshot', UNDO_STACK.length===1);
var placed=A3D.objs[0];
assert('placed instance is positioned at the clicked point and level elevation', placed.pos[0]===5&&placed.pos[1]===0&&placed.pos[2]===3);
assert('placed instance records its origin family', placed.bim.familyId===doorFam.id&&placed.bim.familyName==='Standard Door');
assert('placed instance becomes the active selection', A3D.sel===placed.id);

bimPlaceFamilyInstance(doorFam,[10,7]);
var placed2=A3D.objs[1];
assert('a second placement creates a genuinely distinct object', placed2.id!==placed.id);

// ---- 5. THE key guarantee: independence. Mutate a placed instance, verify isolation ----
placed.mesh.v[0][0]=9999;
assert('INDEPENDENCE (real embedded code): mutating a placed instance leaves the family library untouched',
  doorFam.mesh.v[0][0]!==9999);
assert('INDEPENDENCE (real embedded code): mutating one instance leaves a second instance of the same family untouched',
  placed2.mesh.v[0][0]!==9999);
doorFam.mesh.v[1][1]=7777;
assert('INDEPENDENCE (real embedded code): mutating the family definition does not retroactively affect placed instances',
  placed.mesh.v[1][1]!==7777&&placed2.mesh.v[1][1]!==7777);

// ---- 6. Remove from library: real function, real persistence update ----
var removed=bimFamilyLibraryRemove(doorFam.id);
assert('real embedded remove succeeds and returns true', removed===true);
assert('removed family no longer resolves via get', bimFamilyLibraryGet(doorFam.id)===null);
assert('already-placed instances survive a library removal (independent copies, as required)', A3D.objs.length===2);
var afterRemoveStore=JSON.parse(STORE[FAMILY_LIB_KEY]);
assert('removal is persisted to storage immediately', afterRemoveStore.length===0);

// ---- 7. Multi-part mesh merge (real embedded code) for multi-object OBJ imports ----
var partA={v:[[0,0,0],[1,0,0],[1,1,0]],f:[[0,1,2]]};
var partB={v:[[5,0,0],[6,0,0],[6,1,0]],f:[[0,1,2]]};
var merged=bimMergeMeshes([partA,partB]);
assert('real embedded merge combines vertex counts correctly', merged.v.length===6);
assert('real embedded merge correctly offsets the second part\'s face indices', JSON.stringify(merged.f[1])===JSON.stringify([3,4,5]));

// ---- 8. Corrupted storage recovers gracefully ----
STORE[FAMILY_LIB_KEY]='{not valid json, not even an array';
var recovered=bimLoadFamilyLibrary();
assert('corrupted family library storage falls back to an empty array, not a crash', Array.isArray(recovered)&&recovered.length===0);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
