var A3D={objs:[],counts:{},seq:1,activeLevel:'lvl-0',activeLayer:'layer-0',sel:null,sel2:null,selSet:[],meshes:{},
  layers:[{id:'layer-0',name:'Model',color:'#7f9db8',visible:true,locked:false}],
  levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}]};
var UNDO_STACK=[],REDO_STACK=[],UNDO_MAX=50,undoSuspend=false;
function refreshTree(){}
function refreshHud(){}
function refreshLevels(){}
function refreshLayers(){}
function paint(){}
function saveSoon(){}
function fitScene(){}
function bimSyncActiveGlobal(){}
var TOASTS=[];
function a3dToast(m){TOASTS.push(m);}
function pushUndo(){if(undoSuspend)return;UNDO_STACK.push(bimSnapshotState());if(UNDO_STACK.length>UNDO_MAX)UNDO_STACK.shift();REDO_STACK.length=0;}
var CONFIRM_RESPONSE=true;
function confirm(msg){return CONFIRM_RESPONSE;}
  function bimSnapshotState(){
    return JSON.stringify({objs:A3D.objs,levels:A3D.levels,layers:A3D.layers,counts:A3D.counts,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer});
  }

  function bimRestoreState(json){
    var st;
    try{st=JSON.parse(json);}catch(eR){console.warn('[BIM] Corrupted undo snapshot, ignoring.',eR);return false;}
    undoSuspend=true;
    A3D.objs=st.objs||[];
    A3D.levels=(st.levels&&st.levels.length)?st.levels:A3D.levels;
    A3D.layers=(st.layers&&st.layers.length)?st.layers:A3D.layers;
    A3D.counts=st.counts||A3D.counts;
    A3D.activeLevel=st.activeLevel||A3D.activeLevel;
    A3D.activeLayer=st.activeLayer||A3D.activeLayer;
    A3D.sel=null;A3D.sel2=null;A3D.meshes={};
    bimSyncActiveGlobal();
    refreshTree();refreshHud();refreshLevels();refreshLayers();paint();
    undoSuspend=false;
    return true;
  }

  function bimBuildProjectEnvelope(){
    return JSON.stringify({app:'acad3d-project',formatVersion:1,savedAt:new Date().toISOString(),
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

  function bimExportProjectFile(){
    try{
      var json=bimBuildProjectEnvelope();
      bimTriggerDownload(json,'project.acad3d.json','application/json');
      a3dToast('Project saved ('+A3D.objs.length+' object(s))');
    }catch(eS){console.warn('[BIM] Project export failed: ',eS);a3dToast('Project export failed: '+(eS&&eS.message?eS.message:eS));}
  }

  function bimImportProjectFile(text,filename){
    var res=bimParseProjectEnvelope(text);
    if(res.error){a3dToast(filename+': '+res.error);return false;}
    if(!A3D.objs.length||confirm('Loading "'+filename+'" will replace the current model ('+A3D.objs.length+' object(s)). Continue?')){
      pushUndo();
      var ok=bimRestoreState(JSON.stringify(res.data));
      if(ok){
        saveSoon();
        var msg='Project loaded: '+(res.data.objs?res.data.objs.length:0)+' object(s) from '+filename;
        if(res.warn)msg+=' \u2014 '+res.warn;
        a3dToast(msg);
        fitScene();
      }else{
        a3dToast('Failed to load project data from '+filename);
      }
      return ok;
    }
    return false;
  }

  function objById(id){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===id)return A3D.objs[i];
    return null;
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

A3D.objs=[
  {id:'wall-1',t:'solid',name:'Wall_1',bim:{type:'wall',thickness:0.3,height:3,align:'center',baseY:0,closed:true,centerline:[[0,0],[6,0],[6,4],[0,4]]},pos:[0,0,0],mesh:{v:[[0,0,0]],f:[[0,0,0]]},layer:'layer-0'},
  {id:'room-1',t:'room',name:'Room_1',pts:[[0,0],[6,0],[6,4],[0,4]],y:0,area:24,pos:[0,0,0],levelId:'lvl-0',layer:'layer-0'},
  {id:'text-1',t:'text',name:'Text_1',text:'Living Room',pt:[3,2],y:0,pos:[0,0,0],layer:'layer-0'}
];
A3D.counts={wall:1,room:1,text:1};

var envelope=bimBuildProjectEnvelope();
var envParsed=JSON.parse(envelope);
assert('saved envelope has the correct app identifier', envParsed.app==='acad3d-project');
assert('saved envelope has a format version', envParsed.formatVersion===1);
assert('saved envelope includes a savedAt timestamp', typeof envParsed.savedAt==='string' && envParsed.savedAt.length>0);
assert('saved envelope contains all 3 objects', envParsed.data.objs.length===3);
assert('saved envelope preserves the naming counters', JSON.stringify(envParsed.data.counts)===JSON.stringify({wall:1,room:1,text:1}));

var savedModel=JSON.stringify(A3D.objs);
A3D.objs=[{id:'unrelated',t:'box'}];
A3D.counts={};
A3D.sel='unrelated';

var loadRes=bimImportProjectFile(envelope,'myproject.acad3d.json');
assert('project load reports success', loadRes===true);
assert('loaded model exactly matches what was saved', JSON.stringify(A3D.objs)===savedModel);
assert('loaded counts exactly match what was saved', JSON.stringify(A3D.counts)===JSON.stringify({wall:1,room:1,text:1}));
assert('stale selection from before the load is cleared', A3D.sel===null);
assert('loading a project pushes exactly one undo snapshot (reversible via Ctrl+Z)', UNDO_STACK.length===1);

var restoreOk=bimRestoreState(UNDO_STACK.pop());
assert('undoing a project load restores the prior model', restoreOk===true && A3D.objs.length===1 && A3D.objs[0].id==='unrelated');

var r1=bimImportProjectFile('{not valid json', 'bad.json');
assert('malformed JSON is rejected, not crashed', r1===false);

var r2=bimImportProjectFile(JSON.stringify({some:'random',objs:[1,2,3]}), 'random.json');
assert('a random JSON file (even with an objs-like key) is rejected as not a recognized project', r2===false);

var r3=bimImportProjectFile(JSON.stringify({app:'other-app',data:{objs:[]}}), 'foreign.json');
assert('a project file from a different app identifier is rejected', r3===false);

A3D.objs=[{id:'keepme',t:'box'}];
CONFIRM_RESPONSE=false;
var r4=bimImportProjectFile(envelope,'declined.json');
assert('declining the confirmation prompt does not load the project', r4===false);
assert('model is untouched after declining', A3D.objs.length===1 && A3D.objs[0].id==='keepme');
CONFIRM_RESPONSE=true;

A3D.objs=[];
var confirmCalls=0;
var realConfirm=confirm;
confirm=function(msg){confirmCalls++;return true;};
bimImportProjectFile(envelope,'intoempty.json');
assert('loading into an empty model does not prompt for confirmation (nothing would be lost)', confirmCalls===0);
confirm=realConfirm;

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
