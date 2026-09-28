// Revit's split for walls: THICKNESS is a TYPE parameter (all "Generic 300mm" walls are 300mm),
// while HEIGHT and LOCATION LINE are INSTANCE parameters (each wall can differ). Getting this
// split right is the whole point -- putting height on the type would be wrong.
function makeTypes(){
  return {
    wall:[
      {id:'wt-generic300',name:'Generic - 300mm',params:{thickness:0.3,material:'Concrete'}},
      {id:'wt-interior100',name:'Interior - 100mm',params:{thickness:0.1,material:'Partition'}}
    ]
  };
}
function bimFindType(types,cat,id){
  var list=types[cat]||[],i;
  for(i=0;i<list.length;i++)if(list[i].id===id)return list[i];
  return null;
}
function bimTypeParam(types,o,key,fallback){
  // instance override wins if present, else the type value, else the fallback
  if(o.bim&&o.bim.overrides&&o.bim.overrides[key]!==undefined)return o.bim.overrides[key];
  var t=bimFindType(types,o.bim.typeCat||'wall',o.bim.typeId);
  if(t&&t.params[key]!==undefined)return t.params[key];
  return fallback;
}
function bimDuplicateType(types,cat,id,newName){
  var src=bimFindType(types,cat,id);
  if(!src)return null;
  var copy={id:'wt-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e5),
    name:newName,params:JSON.parse(JSON.stringify(src.params))};
  types[cat].push(copy);
  return copy;
}
function bimSetTypeParam(types,cat,id,key,value){
  var t=bimFindType(types,cat,id);
  if(!t)return false;
  t.params[key]=value;
  return true;
}
function bimInstancesOfType(objs,cat,id){
  return objs.filter(function(o){return o.bim&&o.bim.typeCat===cat&&o.bim.typeId===id;});
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b){return Math.abs(a-b)<1e-9;}

var T=makeTypes();
var w1={id:'w1',bim:{type:'wall',typeCat:'wall',typeId:'wt-generic300',height:3,align:'center'}};
var w2={id:'w2',bim:{type:'wall',typeCat:'wall',typeId:'wt-generic300',height:2.4,align:'left'}};
var w3={id:'w3',bim:{type:'wall',typeCat:'wall',typeId:'wt-interior100',height:3,align:'center'}};
var objs=[w1,w2,w3];

// ---- resolution ----
assert('thickness resolves from the TYPE, not the instance', approx(bimTypeParam(T,w1,'thickness',0),0.3));
assert('a different type gives a different thickness', approx(bimTypeParam(T,w3,'thickness',0),0.1));
assert('type parameters other than dimensions resolve too', bimTypeParam(T,w1,'material','')==='Concrete');
assert('an unknown key falls back', bimTypeParam(T,w1,'nosuchkey','fb')==='fb');
var orphan={id:'o',bim:{type:'wall',typeCat:'wall',typeId:'missing-type'}};
assert('an object pointing at a deleted type falls back rather than crashing', approx(bimTypeParam(T,orphan,'thickness',0.2),0.2));

// ---- THE key behaviour: editing a type changes every instance of it ----
assert('two walls share the same type', bimInstancesOfType(objs,'wall','wt-generic300').length===2);
bimSetTypeParam(T,'wall','wt-generic300','thickness',0.45);
assert('PROPAGATION: editing the type changes instance 1', approx(bimTypeParam(T,w1,'thickness',0),0.45));
assert('PROPAGATION: editing the type changes instance 2 as well', approx(bimTypeParam(T,w2,'thickness',0),0.45));
assert('PROPAGATION: a wall of a DIFFERENT type is untouched', approx(bimTypeParam(T,w3,'thickness',0),0.1));

// ---- instance parameters stay independent (this is the half that must NOT propagate) ----
assert('height is an instance parameter and differs between walls of the same type',
  w1.bim.height===3 && w2.bim.height===2.4);
assert('location line is an instance parameter and differs too', w1.bim.align==='center'&&w2.bim.align==='left');

// ---- instance override beats the type ----
w2.bim.overrides={thickness:0.9};
assert('an explicit instance override wins over the type value', approx(bimTypeParam(T,w2,'thickness',0),0.9));
assert('the override does not leak to its sibling instance', approx(bimTypeParam(T,w1,'thickness',0),0.45));
delete w2.bim.overrides;

// ---- duplicating a type ----
var dup=bimDuplicateType(T,'wall','wt-generic300','Generic - 450mm');
assert('duplicating a type creates a new entry with a distinct id', dup&&dup.id!=='wt-generic300');
assert('the duplicate copies the source parameters', approx(dup.params.thickness,0.45));
bimSetTypeParam(T,'wall',dup.id,'thickness',0.6);
assert('editing the duplicate does NOT affect the original type', approx(bimFindType(T,'wall','wt-generic300').params.thickness,0.45));
assert('and does not affect walls still on the original type', approx(bimTypeParam(T,w1,'thickness',0),0.45));
w1.bim.typeId=dup.id;
assert('reassigning a wall to the new type picks up its value', approx(bimTypeParam(T,w1,'thickness',0),0.6));
assert('its former sibling stays on the old type', approx(bimTypeParam(T,w2,'thickness',0),0.45));

assert('duplicating a nonexistent type returns null, not a crash', bimDuplicateType(T,'wall','nope','X')===null);
assert('setting a parameter on a nonexistent type fails cleanly', bimSetTypeParam(T,'wall','nope','thickness',1)===false);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
