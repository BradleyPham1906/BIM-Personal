var A3D={cam:{yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3},flat:false,view:'Home',prevCam:null,prevView:null,
  section:null,sk:null,sel:null,sel2:null,selSet:[],objs:[],levels:[{id:'lvl-0',name:'Level 0',elev:0,height:3}],activeLevel:'lvl-0'};
var el={flip:{textContent:'',setAttribute:function(){}},root:{classList:{add:function(){},remove:function(){},toggle:function(){}}}};
function refreshHud(){}
function paint(){}
function saveSoon(){}
function refreshTree(){}
function a3dToast(){}
function cancelSketch(){A3D.sk=null;}
function bimComputeSectionCuts(){return {};}
function bimGetActiveLevel(){return A3D.levels[0];}
function closeDlg(){}
function fitScene(){}
  function toggleFlat(){
    if(A3D.sk)cancelSketch();
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
    if(el.flip){
      el.flip.textContent=A3D.flat?'3D':'2D';
      el.flip.setAttribute('title',A3D.flat?'Go to 3D (Shift + >)':'Go to 2D (Shift + >)');
    }
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    refreshHud();paint();saveSoon();
  }

  function bimEnterDraftingMode(){
    if(A3D.section)bimExitSection();
    if(!A3D.flat)toggleFlat();
  }

  function startSectionTool(){
    closeDlg();
    if(A3D.section)bimExitSection();
    var c0=A3D.cam;
    var origCam={yaw:c0.yaw,pitch:c0.pitch,dist:c0.dist,tx:c0.tx,ty:c0.ty,tz:c0.tz,flat:A3D.flat,view:A3D.view};
    if(!A3D.flat)toggleFlat();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'section',pts:[],y:lvl.elev,on:null,origCam:origCam};
    a3dToast('Section: click the start point, then click again to draw the cut line');
    paint();
  }

  function bimEnterSection(P,dir,origCam){
    var keepSign=1;
    var cuts=bimComputeSectionCuts(P,dir,keepSign);
    A3D.section={p:P,dir:dir,keepSign:keepSign,cutMeshes:cuts,
      prevCam:origCam,prevFlat:origCam.flat,prevView:origCam.view};
    bimAimSectionCamera();
    A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
    refreshTree();paint();saveSoon();
    a3dToast('Section view active \u2014 use Flip Section to see the other side, Exit Section to return');
  }

  function bimExitSection(){
    if(!A3D.section)return;
    var prev=A3D.section.prevCam,prevFlat=A3D.section.prevFlat,prevView=A3D.section.prevView;
    var c=A3D.cam;
    c.yaw=prev.yaw;c.pitch=prev.pitch;c.dist=prev.dist;c.tx=prev.tx;c.ty=prev.ty;c.tz=prev.tz;
    A3D.flat=prevFlat;
    A3D.view=prevView||'Home';
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (Shift + >)':'Go to 2D (Shift + >)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    A3D.section=null;
    refreshHud();paint();saveSoon();
    a3dToast('Exited section view');
  }

  function bimAimSectionCamera(){
    if(!A3D.section)return;
    var perp=[-A3D.section.dir[1],A3D.section.dir[0]];
    var viewDirX=-perp[0]*A3D.section.keepSign,viewDirZ=-perp[1]*A3D.section.keepSign;
    var yaw=Math.atan2(viewDirX,viewDirZ);
    var c=A3D.cam;
    c.yaw=yaw;c.pitch=0.02;
    A3D.flat=true;
    if(el.flip){el.flip.textContent='3D';el.flip.setAttribute('title','Go to 3D (Shift + >)');}
    if(el.root)el.root.classList.add('flat');
    fitScene();
    A3D.view='Section';
    refreshHud();
  }

  function bimFlipSection(){
    if(!A3D.section){a3dToast('No active section to flip');return;}
    A3D.section.keepSign=-A3D.section.keepSign;
    A3D.section.cutMeshes=bimComputeSectionCuts(A3D.section.p,A3D.section.dir,A3D.section.keepSign);
    bimAimSectionCamera();
    paint();saveSoon();
  }

  function startRoomTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'room',pts:[],y:lvl.elev,on:null};
    a3dToast('Room: click inside an enclosed wall loop or closed sketch on '+lvl.name);
    paint();
  }

  function startDimTool(){
    closeDlg();
    bimEnterDraftingMode();
    var lvl=bimGetActiveLevel();
    A3D.sk={tool:'dim',pts:[],y:lvl.elev,on:null};
    a3dToast('Dimension: click first point, second point, then a third point to set the offset side');
    paint();
  }

  var A3DR_PANELS=[
    {t:'BIM',small:['bim:wall','bim:door','bim:window','bim:floor','bim:room','bim:roof','bim:stair','bim:column']},
    {t:'Annotate',small:['bim:dim','bim:text','bim:section']},
    {t:'Sketch',small:['s:rect','s:circle','s:poly']},
    {t:'PartDesign',small:['p:pad','p:pocket']},
    {t:'Solids',small:['b:union','b:cut','b:isect']},
    {t:'Primitives',small:['box','cyl','sphere','cone','torus','tube','prism','wedge','ellipsoid']},
    {t:'View',small:['v:home','v:fit','v:top','v:front','v:right','v:iso']},
    {t:'Modify',small:['m:del','m:desel','m:dup','m:array']},
    {t:'Export',small:['m:exportpng','m:exportpdf']},
    {t:'Section',small:['m:exitsection','m:flipsection']},
    {t:'Precision',small:['bim:mirror','bim:rotate','bim:polararray','bim:joinwalls']}
  ];

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}
function approx(a,b,eps){return Math.abs(a-b)<(eps||1e-6);}

A3D.cam={yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3};
A3D.flat=false;A3D.view='Home';A3D.section=null;A3D.sk=null;
var origYaw=A3D.cam.yaw,origPitch=A3D.cam.pitch,origDist=A3D.cam.dist,origTx=A3D.cam.tx,origTy=A3D.cam.ty,origTz=A3D.cam.tz;

startSectionTool();
assert('starting the section tool switches to flat/plan mode for line-drawing', A3D.flat===true);
assert('sk carries the correctly-captured original camera state', !!A3D.sk&&!!A3D.sk.origCam);
assert('origCam captured the TRUE original yaw/pitch, not the plan-view camera',
  approx(A3D.sk.origCam.yaw,origYaw)&&approx(A3D.sk.origCam.pitch,origPitch));
assert('origCam correctly records that the user was NOT in flat mode originally', A3D.sk.origCam.flat===false);

var capturedOrigCam=A3D.sk.origCam;
bimEnterSection([5,0],[0,1],capturedOrigCam);
assert('section becomes active', !!A3D.section);
assert('section view is aimed (camera changed from the plan view)', A3D.view==='Section');

bimExitSection();
assert('FIX CONFIRMED: exiting section restores the EXACT original yaw', approx(A3D.cam.yaw,origYaw), A3D.cam.yaw+' vs '+origYaw);
assert('FIX CONFIRMED: exiting section restores the EXACT original pitch', approx(A3D.cam.pitch,origPitch));
assert('FIX CONFIRMED: exiting section restores the exact original camera position',
  approx(A3D.cam.dist,origDist)&&approx(A3D.cam.tx,origTx)&&approx(A3D.cam.ty,origTy)&&approx(A3D.cam.tz,origTz));
assert('FIX CONFIRMED: exiting section returns to 3D perspective (not stuck in flat/plan)', A3D.flat===false);
assert('FIX CONFIRMED: exiting section restores the original view label', A3D.view==='Home');

A3D.cam={yaw:-0.7,pitch:0.42,dist:20,tx:1,ty:2,tz:3};
A3D.flat=false;A3D.view='Home';A3D.section=null;A3D.sk=null;
startSectionTool();
bimEnterSection([5,0],[0,1],A3D.sk.origCam);
assert('setup: section is active before testing the interaction', !!A3D.section);
startRoomTool();
assert('starting Room while a section was active correctly exits the section first (not left stuck in a vertical section-camera orientation)', A3D.section===null);
assert('after auto-exiting section, drafting mode (flat) is still correctly active for Room placement', A3D.flat===true);
assert('the camera is no longer aimed at the section cut (Section view label cleared)', A3D.view!=='Section');

var bimPanel=A3DR_PANELS.filter(function(p){return p.t==='BIM';})[0];
var annotatePanel=A3DR_PANELS.filter(function(p){return p.t==='Annotate';})[0];
assert('a dedicated Annotate panel now exists, separate from BIM', !!annotatePanel);
assert('BIM panel contains only modeling tools (Wall/Door/Window/Floor/Room/Roof/Stair/Column)',
  bimPanel.small.indexOf('bim:wall')>=0 && bimPanel.small.indexOf('bim:dim')===-1 && bimPanel.small.indexOf('bim:text')===-1);
assert('Annotate panel contains Dimension, Text, and Section (documentation/measurement tools)',
  annotatePanel.small.indexOf('bim:dim')>=0 && annotatePanel.small.indexOf('bim:text')>=0 && annotatePanel.small.indexOf('bim:section')>=0);

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
