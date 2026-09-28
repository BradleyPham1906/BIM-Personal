var A3D={cam:{yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3},flat:false,view:'Home',objs:[],levels:[{id:'lvl-0',name:'L0'}],
  layers:[],counts:{},activeLevel:'lvl-0',activeLayer:'layer-0',views:[],activeViewId:null,levelFilter:false,
  section:null,sel:null,sel2:null,meshes:{}};
var el={};var undoSuspend=false;
function pushUndo(){} function a3dToast(){} function paint(){} function saveSoon(){} function refreshViews(){}
function refreshTree(){} function refreshHud(){} function refreshLevels(){} function refreshLayers(){}
function bimSyncActiveGlobal(){} function bimExitSection(){A3D.section=null;}
function bimEnterSection(p,d,o){A3D.section={p:p,dir:d,keepSign:1,cutMeshes:{}};}
function bimFlipSection(){if(A3D.section)A3D.section.keepSign=-A3D.section.keepSign;}
  function bimCaptureView(name){
    var c=A3D.cam;
    return {
      id:'view-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      name:name,
      cam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz},
      flat:A3D.flat,viewLabel:A3D.view,levelId:A3D.activeLevel,levelFilter:!!A3D.levelFilter,
      section:A3D.section?{p:A3D.section.p,dir:A3D.section.dir,keepSign:A3D.section.keepSign}:null
    };
  }

  function bimApplyView(id){
    var v=null,i;
    for(i=0;i<A3D.views.length;i++)if(A3D.views[i].id===id){v=A3D.views[i];break;}
    if(!v){a3dToast('View not found');return false;}
    if(A3D.section)bimExitSection();
    var c=A3D.cam;
    c.yaw=v.cam.yaw;c.pitch=v.cam.pitch;c.dist=v.cam.dist;
    c.tx=v.cam.tx;c.ty=v.cam.ty;c.tz=v.cam.tz;
    A3D.flat=!!v.flat;
    A3D.view=v.viewLabel||'Custom';
    if(v.levelId)A3D.activeLevel=v.levelId;
    A3D.levelFilter=!!v.levelFilter;
    A3D.activeViewId=v.id;
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (Shift + >)':'Go to 2D (Shift + >)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    if(v.section){
      var origCam={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz,flat:A3D.flat,view:A3D.view};
      bimEnterSection(v.section.p,v.section.dir,origCam);
      if(v.section.keepSign===-1)bimFlipSection();
    }
    bimSyncActiveGlobal();
    refreshViews();refreshLevels();refreshTree();refreshHud();paint();saveSoon();
    a3dToast('View: '+v.name);
    return true;
  }

  function bimDeleteView(id){
    var i;
    for(i=0;i<A3D.views.length;i++){
      if(A3D.views[i].id===id){
        pushUndo();
        A3D.views.splice(i,1);
        if(A3D.activeViewId===id)A3D.activeViewId=null;
        refreshViews();paint();saveSoon();
        a3dToast('View deleted');
        return true;
      }
    }
    return false;
  }

  function bimAnnotationVisible(o){
    if(!o.viewId)return true;
    return o.viewId===A3D.activeViewId;
  }

  function bimObjectLevelId(o){
    if(o.bim&&o.bim.levelId)return o.bim.levelId;
    if(o.levelId)return o.levelId;
    return null;
  }

  function bimObjectVisibleOnLevel(o){
    if(!A3D.levelFilter)return true;
    var lv=bimObjectLevelId(o);
    if(!lv)return true;
    return lv===A3D.activeLevel;
  }

  function bimToggleLevelFilter(){
    A3D.levelFilter=!A3D.levelFilter;
    refreshViews();refreshHud();paint();saveSoon();
    a3dToast(A3D.levelFilter?'Showing active level only':'Showing all levels');
  }

  function bimSnapshotState(){
    return JSON.stringify({objs:A3D.objs,levels:A3D.levels,layers:A3D.layers,counts:A3D.counts,activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer,views:A3D.views,activeViewId:A3D.activeViewId,levelFilter:A3D.levelFilter});
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
    A3D.views=st.views||[];
    A3D.activeViewId=st.activeViewId||null;
    A3D.levelFilter=!!st.levelFilter;
    A3D.sel=null;A3D.sel2=null;A3D.meshes={};
    bimSyncActiveGlobal();
    refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();paint();
    undoSuspend=false;
    return true;
  }

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b){return Math.abs(a-b)<1e-9;}

// capture + apply via REAL embedded code
var v=bimCaptureView('Test 3D');
A3D.views.push(v);
A3D.cam={yaw:0,pitch:1.52,dist:99,tx:9,ty:9,tz:9};A3D.flat=true;A3D.activeLevel='lvl-9';A3D.levelFilter=true;
bimApplyView(v.id);
assert('real bimApplyView restores exact camera', approx(A3D.cam.yaw,-0.7)&&approx(A3D.cam.dist,20)&&approx(A3D.cam.tx,1));
assert('real bimApplyView restores flat mode', A3D.flat===false);
assert('real bimApplyView restores active level', A3D.activeLevel==='lvl-0');
assert('real bimApplyView restores level filter state', A3D.levelFilter===false);
assert('applied view becomes active', A3D.activeViewId===v.id);

// section round-trip
A3D.section={p:[5,0],dir:[0,1],keepSign:1,cutMeshes:{heavy:'data'}};
var vs=bimCaptureView('Sec');
assert('captured section stores only the cut plane, not the mesh cache', vs.section&&vs.section.cutMeshes===undefined);
A3D.views.push(vs);
A3D.section=null;
bimApplyView(vs.id);
assert('applying a section view re-enters the section', !!A3D.section&&A3D.section.p[0]===5);

// annotation visibility
A3D.activeViewId='view-A';
assert('untagged annotation visible in any view', bimAnnotationVisible({t:'dim'})===true);
assert('view-tagged annotation visible in its own view', bimAnnotationVisible({t:'dim',viewId:'view-A'})===true);
assert('view-tagged annotation hidden in another view', bimAnnotationVisible({t:'dim',viewId:'view-B'})===false);

// level filtering
A3D.levelFilter=false;A3D.activeLevel='lvl-0';
assert('filter off: other-level object visible', bimObjectVisibleOnLevel({bim:{levelId:'lvl-1'}})===true);
A3D.levelFilter=true;
assert('filter on: active-level object visible', bimObjectVisibleOnLevel({bim:{levelId:'lvl-0'}})===true);
assert('filter on: other-level object hidden', bimObjectVisibleOnLevel({bim:{levelId:'lvl-1'}})===false);
assert('filter on: room uses its own levelId field', bimObjectVisibleOnLevel({t:'room',levelId:'lvl-0'})===true);
assert('filter on: unassigned object stays visible', bimObjectVisibleOnLevel({t:'box'})===true);

// delete
var n0=A3D.views.length;
bimDeleteView(v.id);
assert('real bimDeleteView removes the view', A3D.views.length===n0-1);

// persistence through snapshot/restore (project save + undo path)
A3D.views=[bimCaptureView('Persisted')];A3D.activeViewId=A3D.views[0].id;A3D.levelFilter=true;
var snap=bimSnapshotState();
A3D.views=[];A3D.activeViewId=null;A3D.levelFilter=false;
bimRestoreState(snap);
assert('views survive snapshot/restore (project save + undo)', A3D.views.length===1&&A3D.views[0].name==='Persisted');
assert('activeViewId survives snapshot/restore', A3D.activeViewId===A3D.views[0].id);
assert('levelFilter survives snapshot/restore', A3D.levelFilter===true);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
