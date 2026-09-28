// Which parameters belong to the TYPE (shared by every instance) vs the INSTANCE.
// This split is the whole point: in Revit, changing a Wall Type's thickness changes every wall
// of that type at once, while height/offset stay per-wall.
var TYPE_PARAM_DEFS={
  wall:   {family:'Basic Wall',        typeParams:['thickness'],      instanceParams:['height','align','baseY']},
  floor:  {family:'Floor',             typeParams:['thickness'],      instanceParams:['baseY']},
  ceiling:{family:'Compound Ceiling',  typeParams:['thickness'],      instanceParams:['heightAbove','baseY']},
  column: {family:'Rectangular Column',typeParams:['width','depth'],  instanceParams:['height','baseY']}
};

function bimCreateType(reg,cat,name,params){
  var def=TYPE_PARAM_DEFS[cat];
  if(!def)return {error:'No type definition for category "'+cat+'"'};
  var id='typ-'+cat+'-'+(reg._seq=(reg._seq||0)+1);
  var p={},i;
  for(i=0;i<def.typeParams.length;i++){
    var k=def.typeParams[i];
    if(params[k]===undefined)return {error:'Type parameter "'+k+'" is required for '+cat};
    p[k]=params[k];
  }
  reg[id]={id:id,category:cat,family:def.family,name:name,params:p};
  return {type:reg[id]};
}
function bimFindTypeByParams(reg,cat,params){
  var def=TYPE_PARAM_DEFS[cat],k;
  if(!def)return null;
  for(k in reg){
    if(k==='_seq'||!reg.hasOwnProperty(k))continue;
    var t=reg[k];
    if(t.category!==cat)continue;
    var match=true,i;
    for(i=0;i<def.typeParams.length;i++){
      var pk=def.typeParams[i];
      if(Math.abs((t.params[pk]||0)-(params[pk]||0))>1e-9){match=false;break;}
    }
    if(match)return t;
  }
  return null;
}
function bimTypesForCategory(reg,cat){
  var out=[],k;
  for(k in reg){
    if(k==='_seq'||!reg.hasOwnProperty(k))continue;
    if(reg[k].category===cat)out.push(reg[k]);
  }
  out.sort(function(a,b){return a.name<b.name?-1:1;});
  return out;
}
function bimDuplicateType(reg,typeId,newName){
  var src=reg[typeId];
  if(!src)return {error:'Type not found'};
  var copy={},k;
  for(k in src.params)copy[k]=src.params[k];
  return bimCreateType(reg,src.category,newName,copy);
}
// Setting a TYPE parameter must update every instance of that type -- that is the behaviour
// that distinguishes a type system from editing objects one at a time.
function bimSetTypeParam(reg,objs,typeId,key,value,rebuildFn){
  var t=reg[typeId];
  if(!t)return {error:'Type not found'};
  var def=TYPE_PARAM_DEFS[t.category];
  if(def.typeParams.indexOf(key)<0)return {error:'"'+key+'" is an instance parameter, not a type parameter'};
  if(!isFinite(value)||value<=0)return {error:'Value must be a positive number'};
  t.params[key]=value;
  var changed=0,i;
  for(i=0;i<objs.length;i++){
    var o=objs[i];
    if(!o.bim||o.bim.typeId!==typeId)continue;
    o.bim[key]=value;
    if(rebuildFn)rebuildFn(o);
    changed++;
  }
  return {changed:changed};
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b){return Math.abs(a-b)<1e-9;}

var reg={};
var r1=bimCreateType(reg,'wall','Generic 200mm',{thickness:0.2});
assert('creating a wall type succeeds', !r1.error&&!!r1.type.id, JSON.stringify(r1.error));
assert('type records its Revit family name', r1.type.family==='Basic Wall');
assert('type holds only its type parameters', JSON.stringify(Object.keys(r1.type.params))==='["thickness"]');

var r2=bimCreateType(reg,'wall','Exterior 300mm',{thickness:0.3});
assert('a second type of the same category can exist', r2.type.id!==r1.type.id);
assert('two wall types are listed for the category', bimTypesForCategory(reg,'wall').length===2);
assert('creating a type without its required parameter is refused', !!bimCreateType(reg,'wall','Missing',{}).error);
assert('an unknown category is refused', !!bimCreateType(reg,'nonsense','X',{}).error);

var rebuilt=[];
function fakeRebuild(o){rebuilt.push(o.id);}
var objs=[
  {id:'w1',bim:{type:'wall',typeId:r1.type.id,thickness:0.2,height:3}},
  {id:'w2',bim:{type:'wall',typeId:r1.type.id,thickness:0.2,height:2.4}},
  {id:'w3',bim:{type:'wall',typeId:r2.type.id,thickness:0.3,height:3}}
];

rebuilt.length=0;
var res=bimSetTypeParam(reg,objs,r1.type.id,'thickness',0.25,fakeRebuild);
assert('setting a type parameter reports how many instances changed', res.changed===2, JSON.stringify(res));
assert('BOTH instances of that type got the new thickness', approx(objs[0].bim.thickness,0.25)&&approx(objs[1].bim.thickness,0.25));
assert('an instance of a DIFFERENT type is untouched', approx(objs[2].bim.thickness,0.3));
assert('only the affected instances were rebuilt', rebuilt.length===2&&rebuilt.indexOf('w3')<0, JSON.stringify(rebuilt));
assert('the type itself records the new value', approx(reg[r1.type.id].params.thickness,0.25));
assert('instance heights were NOT flattened by the type change', approx(objs[0].bim.height,3)&&approx(objs[1].bim.height,2.4));
assert('setting an INSTANCE parameter through the type system is refused', !!bimSetTypeParam(reg,objs,r1.type.id,'height',5,fakeRebuild).error);

var dup=bimDuplicateType(reg,r1.type.id,'Generic 250mm copy');
assert('duplicating a type succeeds', !dup.error);
assert('the duplicate carries the same parameter values', approx(dup.type.params.thickness,0.25));
assert('the duplicate is a genuinely separate type', dup.type.id!==r1.type.id);
bimSetTypeParam(reg,objs,dup.type.id,'thickness',0.4,fakeRebuild);
assert('editing the duplicate does NOT affect the original type', approx(reg[r1.type.id].params.thickness,0.25));
assert('editing the duplicate does not affect the original type\'s instances', approx(objs[0].bim.thickness,0.25));

var found=bimFindTypeByParams(reg,'wall',{thickness:0.3});
assert('a wall drawn at an existing thickness matches the existing type', found&&found.id===r2.type.id, found&&found.name);
assert('an unmatched thickness returns null so a new type can be made', bimFindTypeByParams(reg,'wall',{thickness:0.999})===null);

var c1=bimCreateType(reg,'column','300x300',{width:0.3,depth:0.3});
assert('a multi-parameter type (column w+d) is created', !c1.error&&approx(c1.type.params.width,0.3));
var cobjs=[{id:'c1',bim:{type:'column',typeId:c1.type.id,width:0.3,depth:0.3,height:3}}];
bimSetTypeParam(reg,cobjs,c1.type.id,'width',0.45,fakeRebuild);
assert('changing one of several type params updates instances', approx(cobjs[0].bim.width,0.45));
assert('the other type param is left alone', approx(cobjs[0].bim.depth,0.3));

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
