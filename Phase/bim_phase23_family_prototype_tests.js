function bimMeshBounds(mesh){
  var mn=[Infinity,Infinity,Infinity],mx=[-Infinity,-Infinity,-Infinity],i,k;
  for(i=0;i<mesh.v.length;i++)for(k=0;k<3;k++){
    if(mesh.v[i][k]<mn[k])mn[k]=mesh.v[i][k];
    if(mesh.v[i][k]>mx[k])mx[k]=mesh.v[i][k];
  }
  return {mn:mn,mx:mx};
}
function bimNormalizeMeshForFamily(mesh){
  // shift so XZ is centered at the origin and Y sits on 0 (its local "ground"), so placement
  // via a single click-point + level elevation behaves predictably regardless of the source
  // geometry's original, possibly arbitrary, coordinate origin.
  if(!mesh||!mesh.v||!mesh.v.length)return {v:[],f:mesh?mesh.f:[]};
  var b=bimMeshBounds(mesh);
  var cx=(b.mn[0]+b.mx[0])/2,cz=(b.mn[2]+b.mx[2])/2,baseY=b.mn[1];
  var newV=mesh.v.map(function(v3){return [v3[0]-cx,v3[1]-baseY,v3[2]-cz];});
  return {v:newV,f:mesh.f,size:[b.mx[0]-b.mn[0],b.mx[1]-b.mn[1],b.mx[2]-b.mn[2]]};
}
function bimCloneMesh(mesh){
  return {v:mesh.v.map(function(p){return [p[0],p[1],p[2]];}),f:mesh.f.map(function(fc){return fc.slice();})};
}
function bimFamilyLibraryAdd(library,fam){
  var entry={
    id:'fam-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
    name:fam.name,
    category:fam.category||'Other',
    manufacturer:fam.manufacturer||'',
    mesh:bimNormalizeMeshForFamily(fam.mesh),
    createdAt:new Date().toISOString()
  };
  library.push(entry);
  return entry;
}
function bimFamilyLibraryRemove(library,id){
  var idx=-1,i;
  for(i=0;i<library.length;i++)if(library[i].id===id){idx=i;break;}
  if(idx<0)return false;
  library.splice(idx,1);
  return true;
}
function bimFamilyLibraryByCategory(library){
  var out={},i;
  for(i=0;i<library.length;i++){
    var cat=library[i].category;
    if(!out[cat])out[cat]=[];
    out[cat].push(library[i]);
  }
  return out;
}
function bimCreateFamilyInstance(fam,posXZ,levelElev,seq){
  var meshCopy=bimCloneMesh(fam.mesh);
  return {
    id:'a3d-'+Date.now().toString(36)+'-'+seq,
    t:'solid',
    name:fam.name+'_'+seq,
    pos:[posXZ[0],levelElev,posXZ[1]],
    mesh:meshCopy,
    bim:{type:'familyInstance',familyId:fam.id,familyName:fam.name,category:fam.category}
  };
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- Mesh normalization: an off-center, floating mesh gets recentered correctly ----
var weirdMesh={v:[[10,5,20],[14,5,20],[14,5,24],[10,5,24],[10,9,20],[14,9,20],[14,9,24],[10,9,24]],f:[[0,1,2,3]]};
var normalized=bimNormalizeMeshForFamily(weirdMesh);
var nb=bimMeshBounds(normalized);
assert('normalized mesh is centered on X (min/max symmetric around 0)', approx(nb.mn[0],-2)&&approx(nb.mx[0],2), JSON.stringify(nb));
assert('normalized mesh is centered on Z', approx(nb.mn[2],-2)&&approx(nb.mx[2],2));
assert('normalized mesh sits exactly on Y=0 (its base, not floating or embedded)', approx(nb.mn[1],0), nb.mn[1]);
assert('normalized mesh preserves its original height', approx(nb.mx[1],4));
assert('normalization returns the original size for reference/thumbnail use', approx(normalized.size[0],4)&&approx(normalized.size[1],4)&&approx(normalized.size[2],4));

// ---- Family library CRUD ----
var library=[];
var doorFam=bimFamilyLibraryAdd(library,{name:'Standard Door',category:'Doors',mesh:weirdMesh});
assert('adding a family stores it with a generated id', !!doorFam.id);
assert('added family is normalized on the way in', bimMeshBounds(doorFam.mesh).mn[1]===0);
assert('library now contains exactly one entry', library.length===1);

var winFam=bimFamilyLibraryAdd(library,{name:'Standard Window',category:'Windows',mesh:weirdMesh});
var chairFam=bimFamilyLibraryAdd(library,{name:'Office Chair',category:'Furniture',mesh:weirdMesh});
var byCategory=bimFamilyLibraryByCategory(library);
assert('categorization groups families correctly', byCategory['Doors'].length===1&&byCategory['Windows'].length===1&&byCategory['Furniture'].length===1);

var removed=bimFamilyLibraryRemove(library,winFam.id);
assert('removing a family by id succeeds', removed===true);
assert('library shrinks after removal', library.length===2);
assert('removing an already-removed/nonexistent id fails gracefully, not a crash', bimFamilyLibraryRemove(library,winFam.id)===false);

// ---- Instance creation: THE key requirement -- independent copies, not linked ----
var instance1=bimCreateFamilyInstance(doorFam,[5,3],0,1);
var instance2=bimCreateFamilyInstance(doorFam,[10,7],0,2);
assert('two instances of the same family get distinct ids', instance1.id!==instance2.id);
assert('instance position is placed at the clicked point + level elevation', instance1.pos[0]===5&&instance1.pos[1]===0&&instance1.pos[2]===3);
assert('instance mesh is a genuine independent copy (different array reference from the family\'s stored mesh)',
  instance1.mesh.v!==doorFam.mesh.v && instance2.mesh.v!==doorFam.mesh.v);

// mutate one instance's mesh directly -- the family definition and the OTHER instance must be unaffected
instance1.mesh.v[0][0]=9999;
assert('INDEPENDENCE VERIFIED: mutating one placed instance does not affect the family library definition',
  doorFam.mesh.v[0][0]!==9999);
assert('INDEPENDENCE VERIFIED: mutating one placed instance does not affect a DIFFERENT instance of the same family',
  instance2.mesh.v[0][0]!==9999);

// mutate the family definition itself -- already-placed instances must be unaffected (matches "independent copies" choice)
doorFam.mesh.v[1][1]=8888;
assert('INDEPENDENCE VERIFIED: editing the family library entry does not retroactively affect already-placed instances',
  instance1.mesh.v[1][1]!==8888 && instance2.mesh.v[1][1]!==8888);

// ---- bim metadata correctly identifies the instance's origin family ----
assert('placed instance records which family it came from', instance1.bim.familyId===doorFam.id&&instance1.bim.familyName==='Standard Door');
assert('placed instance records its category (for schedules/filtering later)', instance1.bim.category==='Doors');

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
