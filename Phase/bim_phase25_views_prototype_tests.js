// ---- Saved views ----
function bimCaptureView(A3D,name){
  var c=A3D.cam;
  return {
    id:'view-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
    name:name,
    cam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz},
    flat:A3D.flat,
    viewLabel:A3D.view,
    levelId:A3D.activeLevel,
    levelFilter:!!A3D.levelFilter,
    section:A3D.section?{p:A3D.section.p,dir:A3D.section.dir,keepSign:A3D.section.keepSign}:null
  };
}
function bimApplyView(A3D,v){
  if(!v)return false;
  var c=A3D.cam;
  c.yaw=v.cam.yaw;c.pitch=v.cam.pitch;c.dist=v.cam.dist;
  c.tx=v.cam.tx;c.ty=v.cam.ty;c.tz=v.cam.tz;
  A3D.flat=v.flat;
  A3D.view=v.viewLabel||'Custom';
  if(v.levelId)A3D.activeLevel=v.levelId;
  A3D.levelFilter=!!v.levelFilter;
  A3D.activeViewId=v.id;
  return true;
}

// ---- View-specific annotation visibility ----
function bimAnnotationVisible(o,activeViewId){
  // An annotation with no viewId was created before view-scoping existed (or deliberately
  // global) and shows everywhere. One tagged to a view shows only in that view.
  if(!o.viewId)return true;
  return o.viewId===activeViewId;
}

// ---- Level-based filtering ----
function bimObjectLevelId(o){
  if(o.bim&&o.bim.levelId)return o.bim.levelId;
  if(o.levelId)return o.levelId;
  return null;
}
function bimObjectVisibleOnLevel(o,activeLevel,filterOn){
  if(!filterOn)return true;
  var lv=bimObjectLevelId(o);
  if(!lv)return true; // objects with no level assignment (primitives, imports) always show
  return lv===activeLevel;
}

var PASS=0,FAIL=0;
function assert(n,c,d){if(c){PASS++;console.log('PASS  '+n);}else{FAIL++;console.log('FAIL  '+n+(d?' -- '+d:''));}}
function approx(a,b){return Math.abs(a-b)<1e-9;}

// ---- Saved view capture/restore ----
var A3D={cam:{yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3},flat:false,view:'Home',
  activeLevel:'lvl-0',levelFilter:false,section:null,activeViewId:null};
var v1=bimCaptureView(A3D,'My 3D View');
assert('captured view stores a name and generated id', v1.name==='My 3D View'&&!!v1.id);
assert('captured view records the full camera state', approx(v1.cam.yaw,-0.7)&&approx(v1.cam.tx,1)&&approx(v1.cam.dist,20));
assert('captured view records flat/perspective mode', v1.flat===false);
assert('captured view records the active level', v1.levelId==='lvl-0');
assert('captured view records no section when none is active', v1.section===null);

// change everything, then restore
A3D.cam={yaw:0,pitch:1.52,dist:99,tx:0,ty:0,tz:0};
A3D.flat=true;A3D.view='Plan';A3D.activeLevel='lvl-9';A3D.levelFilter=true;
bimApplyView(A3D,v1);
assert('restoring a view returns the exact camera', approx(A3D.cam.yaw,-0.7)&&approx(A3D.cam.dist,20)&&approx(A3D.cam.tx,1));
assert('restoring a view returns the flat/perspective mode', A3D.flat===false);
assert('restoring a view returns the active level', A3D.activeLevel==='lvl-0');
assert('restoring a view returns the level-filter setting', A3D.levelFilter===false);
assert('restoring a view marks it active', A3D.activeViewId===v1.id);

// section-aware capture
A3D.section={p:[5,0],dir:[0,1],keepSign:1,cutMeshes:{}};
var v2=bimCaptureView(A3D,'Section A');
assert('a view captured while a section is active records the cut plane', v2.section&&v2.section.p[0]===5&&v2.section.keepSign===1);
assert('captured section does NOT store the heavy cut-mesh cache (recomputed on restore)', v2.section.cutMeshes===undefined);

// ---- View-specific annotations ----
var globalDim={id:'d1',t:'dim'};
var viewDim={id:'d2',t:'dim',viewId:'view-A'};
assert('an annotation with no viewId is visible in any view (backward compatible)', bimAnnotationVisible(globalDim,'view-A')===true&&bimAnnotationVisible(globalDim,null)===true);
assert('a view-scoped annotation IS visible in its own view', bimAnnotationVisible(viewDim,'view-A')===true);
assert('a view-scoped annotation is NOT visible in a different view', bimAnnotationVisible(viewDim,'view-B')===false);
assert('a view-scoped annotation is NOT visible when no view is active', bimAnnotationVisible(viewDim,null)===false);

// ---- Level filtering ----
var wallL0={id:'w1',t:'solid',bim:{type:'wall',levelId:'lvl-0'}};
var wallL1={id:'w2',t:'solid',bim:{type:'wall',levelId:'lvl-1'}};
var roomL1={id:'r1',t:'room',levelId:'lvl-1'};
var boxNoLevel={id:'b1',t:'box'};
assert('filter OFF: everything visible regardless of level', 
  bimObjectVisibleOnLevel(wallL0,'lvl-0',false)&&bimObjectVisibleOnLevel(wallL1,'lvl-0',false));
assert('filter ON: object on the active level is visible', bimObjectVisibleOnLevel(wallL0,'lvl-0',true)===true);
assert('filter ON: object on a different level is hidden', bimObjectVisibleOnLevel(wallL1,'lvl-0',true)===false);
assert('filter ON: room objects use their own levelId field (not bim.levelId)', bimObjectVisibleOnLevel(roomL1,'lvl-1',true)===true&&bimObjectVisibleOnLevel(roomL1,'lvl-0',true)===false);
assert('filter ON: objects with NO level assignment stay visible (primitives/imports never vanish)', bimObjectVisibleOnLevel(boxNoLevel,'lvl-0',true)===true);

console.log('');console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
