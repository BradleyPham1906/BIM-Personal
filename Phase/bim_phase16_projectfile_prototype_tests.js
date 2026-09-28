function bimSnapshotState(A3D){
  return JSON.stringify({objs:A3D.objs,levels:A3D.levels,layers:A3D.layers,counts:A3D.counts,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer});
}
function bimRestoreState(A3D,json){
  var st;
  try{st=JSON.parse(json);}catch(eR){return false;}
  A3D.objs=st.objs||[];
  A3D.levels=(st.levels&&st.levels.length)?st.levels:A3D.levels;
  A3D.layers=(st.layers&&st.layers.length)?st.layers:A3D.layers;
  A3D.counts=st.counts||A3D.counts;
  A3D.activeLevel=st.activeLevel||A3D.activeLevel;
  A3D.activeLayer=st.activeLayer||A3D.activeLayer;
  A3D.sel=null;A3D.sel2=null;
  return true;
}
function bimBuildProjectEnvelope(A3D){
  return JSON.stringify({app:'acad3d-project',formatVersion:1,savedAt:'2026-01-01T00:00:00.000Z',
    data:{objs:A3D.objs,levels:A3D.levels,layers:A3D.layers,counts:A3D.counts,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer}});
}
function bimParseProjectEnvelope(text){
  var parsed;
  try{parsed=JSON.parse(text);}catch(eP){return {error:'not valid JSON'};}
  if(!parsed||typeof parsed!=='object')return {error:'not a recognized project file'};
  if(parsed.app!=='acad3d-project'||!parsed.data)return {error:'not a recognized project file'};
  var warn=null;
  if(parsed.formatVersion>1)warn='this project file is from a newer version, some data may not load correctly';
  return {data:parsed.data,warn:warn};
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

// ---- Round trip: save then load produces an identical model ----
var A3D={objs:[{id:'w1',t:'solid',bim:{type:'wall'}},{id:'r1',t:'room',pts:[[0,0],[4,0],[4,3],[0,3]],area:12}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}],
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  counts:{wall:1,room:1},activeLevel:'lvl-0',activeLayer:'layer-0',sel:'w1',sel2:null};

var envelope=bimBuildProjectEnvelope(A3D);
var parsed=bimParseProjectEnvelope(envelope);
assert('envelope round-trips without error', !parsed.error, parsed.error);
assert('no version warning for a same-version file', parsed.warn===null);

// simulate loading into a FRESH (different) state
var A3D2={objs:[],levels:[],layers:[],counts:{},activeLevel:null,activeLayer:null,sel:'stale-selection',sel2:'stale2'};
var ok=bimRestoreState(A3D2,JSON.stringify(parsed.data));
assert('restore succeeds', ok===true);
assert('objects round-trip exactly', JSON.stringify(A3D2.objs)===JSON.stringify(A3D.objs));
assert('levels round-trip exactly', JSON.stringify(A3D2.levels)===JSON.stringify(A3D.levels));
assert('layers round-trip exactly', JSON.stringify(A3D2.layers)===JSON.stringify(A3D.layers));
assert('counts round-trip exactly (fixes a latent gap: undo/redo did not used to preserve these)', JSON.stringify(A3D2.counts)===JSON.stringify(A3D.counts));
assert('activeLevel/activeLayer round-trip', A3D2.activeLevel==='lvl-0'&&A3D2.activeLayer==='layer-0');
assert('stale selection is cleared on load (selecting an object from a discarded model would be a real bug)', A3D2.sel===null&&A3D2.sel2===null);

// ---- Rejection cases: must not silently corrupt the model on bad input ----
var badJson=bimParseProjectEnvelope('{this is not valid json');
assert('malformed JSON is rejected with a clear error, not a crash', !!badJson.error);

var randomJson=bimParseProjectEnvelope(JSON.stringify({foo:'bar',objs:[1,2,3]}));
assert('a random unrelated JSON file (even one with an "objs" key) is rejected, not silently loaded', !!randomJson.error);

var otherApp=bimParseProjectEnvelope(JSON.stringify({app:'some-other-app',data:{objs:[]}}));
assert('a project file from a different app is rejected', !!otherApp.error);

var futureVersion=bimParseProjectEnvelope(JSON.stringify({app:'acad3d-project',formatVersion:99,data:{objs:[]}}));
assert('a future format version loads but produces a warning rather than silently failing', !futureVersion.error && !!futureVersion.warn);

var missingData=bimParseProjectEnvelope(JSON.stringify({app:'acad3d-project',formatVersion:1}));
assert('a project envelope with no data payload is rejected', !!missingData.error);

// ---- Loading into a model with EXISTING content must fully replace it, not merge ----
var A3D3={objs:[{id:'old1',t:'box'},{id:'old2',t:'box'}],levels:[{id:'old-lvl'}],layers:[{id:'old-layer'}],counts:{box:2},activeLevel:'old-lvl',activeLayer:'old-layer'};
bimRestoreState(A3D3,JSON.stringify(parsed.data));
assert('loading a project fully replaces existing objects (no merge/duplication)', A3D3.objs.length===2 && A3D3.objs[0].id==='w1');
assert('old objects are gone entirely after load', A3D3.objs.every(function(o){return o.id!=='old1'&&o.id!=='old2';}));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
