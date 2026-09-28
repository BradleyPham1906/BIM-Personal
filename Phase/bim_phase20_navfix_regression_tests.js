// Simulates the relevant state machine to verify sequencing, using the SAME logic shape as the
// real functions (toggleFlat, bimExitSection, startSectionTool, bimEnterSection).
function makeState(){
  return {cam:{yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3}, flat:false, view:'Home',
    prevCam:null, prevView:null, section:null, sk:null};
}
function toggleFlat(A3D){
  if(A3D.sk)A3D.sk=null;
  if(A3D.flat){
    A3D.flat=false;
    var c=A3D.cam;
    if(A3D.prevCam){c.yaw=A3D.prevCam.yaw;c.pitch=A3D.prevCam.pitch;}
    A3D.view=A3D.prevView||'Home';
  }else{
    A3D.prevCam={yaw:A3D.cam.yaw,pitch:A3D.cam.pitch};
    A3D.prevView=A3D.view;
    A3D.flat=true;
    A3D.cam.yaw=0;A3D.cam.pitch=1.52;
    A3D.view='Plan';
  }
}
function bimAimSectionCamera(A3D){
  var c=A3D.cam;
  c.yaw=1.23;c.pitch=0.02; // stand-in for the real section-specific aiming math
  A3D.flat=true;
  A3D.view='Section';
}
function bimExitSection(A3D){
  if(!A3D.section)return;
  var prev=A3D.section.prevCam,prevFlat=A3D.section.prevFlat,prevView=A3D.section.prevView;
  var c=A3D.cam;
  c.yaw=prev.yaw;c.pitch=prev.pitch;c.dist=prev.dist;c.tx=prev.tx;c.ty=prev.ty;c.tz=prev.tz;
  A3D.flat=prevFlat;
  A3D.view=prevView||'Home';
  A3D.section=null;
}
function bimEnterSection(A3D,P,dir,origCam){
  A3D.section={p:P,dir:dir,keepSign:1,cutMeshes:{},prevCam:origCam,prevFlat:origCam.flat,prevView:origCam.view};
  bimAimSectionCamera(A3D);
}
// ---- FIXED startSectionTool sequencing ----
function startSectionToolFixed(A3D){
  if(A3D.section)bimExitSection(A3D);
  var c=A3D.cam;
  var origCam={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz,flat:A3D.flat,view:A3D.view};
  if(!A3D.flat)toggleFlat(A3D);
  A3D.sk={tool:'section',pts:[],origCam:origCam};
}
// ---- OLD (buggy) sequencing, for comparison ----
function startSectionToolBuggy(A3D){
  if(A3D.section)bimExitSection(A3D);
  if(!A3D.flat)toggleFlat(A3D);
  A3D.sk={tool:'section',pts:[]};
}
function bimEnterSectionBuggy(A3D,P,dir){
  var c=A3D.cam;
  A3D.section={p:P,dir:dir,keepSign:1,cutMeshes:{},
    prevCam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz},prevFlat:A3D.flat,prevView:A3D.view};
  bimAimSectionCamera(A3D);
}

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

// ---- Demonstrate the OLD bug: starting from 3D perspective, entering+exiting section
// does NOT return you to the original 3D view -- it leaves you in the transient Plan view ----
var buggyState=makeState();
var origYaw=buggyState.cam.yaw, origPitch=buggyState.cam.pitch;
startSectionToolBuggy(buggyState);
bimEnterSectionBuggy(buggyState,[5,0],[0,1]);
bimExitSection(buggyState);
assert('REGRESSION PROOF: the old buggy sequencing does NOT restore the original 3D yaw/pitch after exit',
  !(approx(buggyState.cam.yaw,origYaw)&&approx(buggyState.cam.pitch,origPitch)),
  'ended at yaw='+buggyState.cam.yaw+' pitch='+buggyState.cam.pitch+', expected NOT to match original '+origYaw+','+origPitch);
assert('REGRESSION PROOF: old buggy code leaves you in flat mode with view=Plan, not your original 3D Home view',
  buggyState.flat===true && buggyState.view==='Plan');

// ---- Verify the FIX: starting from 3D perspective, entering+exiting section correctly
// returns you to the EXACT original 3D view ----
var fixedState=makeState();
var fOrigYaw=fixedState.cam.yaw, fOrigPitch=fixedState.cam.pitch, fOrigDist=fixedState.cam.dist,
    fOrigTx=fixedState.cam.tx, fOrigTy=fixedState.cam.ty, fOrigTz=fixedState.cam.tz;
startSectionToolFixed(fixedState);
assert('fixed: after starting the tool, flat mode is active for line-drawing', fixedState.flat===true);
var capturedOrigCam=fixedState.sk.origCam;
bimEnterSection(fixedState,[5,0],[0,1],capturedOrigCam);
assert('fixed: section is active with the camera aimed at the cut', fixedState.view==='Section');
bimExitSection(fixedState);
assert('FIX VERIFIED: exiting section restores the EXACT original 3D yaw', approx(fixedState.cam.yaw,fOrigYaw));
assert('FIX VERIFIED: exiting section restores the EXACT original 3D pitch', approx(fixedState.cam.pitch,fOrigPitch));
assert('FIX VERIFIED: exiting section restores the exact original camera distance/position', 
  approx(fixedState.cam.dist,fOrigDist)&&approx(fixedState.cam.tx,fOrigTx)&&approx(fixedState.cam.ty,fOrigTy)&&approx(fixedState.cam.tz,fOrigTz));
assert('FIX VERIFIED: exiting section correctly returns to non-flat (3D perspective) mode', fixedState.flat===false);
assert('FIX VERIFIED: exiting section restores the original view label (Home)', fixedState.view==='Home');

// ---- Verify the fix also works correctly when the user was ALREADY in flat/plan mode
// (not 3D perspective) before starting the section tool ----
var flatStartState=makeState();
flatStartState.flat=true;flatStartState.view='Plan';flatStartState.cam.yaw=0;flatStartState.cam.pitch=1.52;
startSectionToolFixed(flatStartState);
var capturedOrigCam2=flatStartState.sk.origCam;
assert('when already flat, origCam correctly records flat:true (not forcing a false "was 3D" assumption)', capturedOrigCam2.flat===true);
bimEnterSection(flatStartState,[5,0],[0,1],capturedOrigCam2);
bimExitSection(flatStartState);
assert('when the user started already in Plan view, exiting section returns to Plan (not forced to 3D)', 
  flatStartState.flat===true && flatStartState.view==='Plan');

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
