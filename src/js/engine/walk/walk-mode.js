import { A3D } from '../core/state.js';
import { meshOf } from '../core/mesh-primitives.js';
import { bimTerrainSuperseded } from '../terrain/grading.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimPropRow } from '../properties/palette.js';
import { bimStd } from '../standards/registry.js';
import { refreshProps } from '../site-analysis/panel.js';
import { bimLbBase } from '../ladybug/runtime.js';
import { bimSceneExtra } from '../render/gpu-batches.js';
import { bimRvTerrainArrays, bimRvTerrainItem } from '../render/rendered-scene.js';
import { paint } from '../map/terrain-3d.js';
import {
  bimWalkCamFirst, bimWalkCamThird, bimWalkCapsule, bimWalkKeys, bimWalkLook, bimWalkMove, bimWalkStepUp
} from './walk-math.js';
import {
  bimWalkPhys, bimWalkPhysChar, bimWalkPhysFree, bimWalkPhysRay, bimWalkPhysStep, bimWalkPhysSync
} from './walk-physics.js';
import { bimWalkControlsOff, bimWalkControlsOn, bimWalkControlsTell } from './walk-controls.js';
import { bimShadowGround } from '../site/shadows.js';
import { bimEntBody, bimEntChairMesh, bimEntPersonMesh } from '../assets/scale-assets.js';
import { A3D_VIEW, bimObjectVisibleOnLevel } from '../views/saved-views.js';
import { a3dToast } from '../bim/csg-booleans.js';

  /* ================= __acad3dV203: Walkthrough W1, the walk =================
     docs/research/research-walkthrough.md (the owner's D1 to D7, 2026-11-14) and docs/work-orders/v203/SPEC.md, C-05.
     WALK puts the user into the model as a person, in whatever visual style the view is in: Jolt (runtime/jolt, loaded
     here the first time, as the rendered view loads three.js) holds them to the floor, stops them at walls and lets them
     climb what a code stair allows (walk-physics.js); walk-math.js turns the keys, the joystick and the look into a
     move and a camera; the camera is the app's own A3D.cam, so every view draws the walk. Third person draws a V169
     figure at the feet, as an object of the scene only (bimSceneExtra), never of the model. Leave puts the camera back.
     The model's triangles are each element's own (meshOf, the terrain's surface), shown ones only, kept by the
     physics under the element's id and rebuilt when one changes: the figure is never among them. */
  var BIM_WALK_VER='1.1.1',BIM_WALK_FILE='jolt/'+BIM_WALK_VER+'/bim-jolt.min.js';
  var BIM_WALK_SRI='sha256-CjWGOkdK71XTljPaSyhFcvbvhquB8CSdVPyjW5yaMf0=';   /* the file's SHA-256, as runtime/MANIFEST.json pins it */
  var BIM_WALK_KEY='acad3dWalkV1';
  var BIM_WALK_LOOK=0.0025,BIM_WALK_BOOM=3,BIM_WALK_SYNC_MS=400;   /* radians a pixel; the third person's boom, m; how often edits are looked for */
  var BIM_WALK_WHO={adult:'Mean adult',man:'Man',woman:'Woman',child:'Child',own:'Own height',chair:'Wheelchair user'};
  var A3D_WALK={on:false,mode:'walk',view:'first',ghost:false,yaw:0,pitch:0,p:[0,0,0],cap:null,B:null,R:null,saved:null,
    held:{},joy:null,last:0,raf:0,J:null,load:null,st:'idle',err:'',phys:null,seen:{},syncAt:0,jump:false,set:null,moved:0};

  /* Walk's settings, this browser's: who walks, and their own height */
  function bimWalkSettings(){
    if(A3D_WALK.set)return A3D_WALK.set;
    var s={who:'adult',h:1.7},r=null;
    try{r=JSON.parse(localStorage.getItem(BIM_WALK_KEY)||'null');}catch(eS){r=null;}
    if(r&&typeof r==='object'){
      if(BIM_WALK_WHO.hasOwnProperty(r.who))s.who=r.who;
      if(typeof r.h==='number'&&r.h>=0.8&&r.h<=2.3)s.h=r.h;
    }
    A3D_WALK.set=s;
    return s;
  }
  function bimWalkSetting(k,v){
    var s=bimWalkSettings(),n;
    if(k==='who'&&BIM_WALK_WHO.hasOwnProperty(v))s.who=v;
    else if(k==='h'){n=parseFloat(v);if(!(n>=0.8&&n<=2.3)){a3dToast('A height between 0.8 m and 2.3 m');refreshProps();return false;}s.h=n;}
    else return false;
    try{localStorage.setItem(BIM_WALK_KEY,JSON.stringify(s));}
    catch(eS){console.warn('[BIM] Walk\'s settings could not be kept in this browser',eS);}
    if(A3D_WALK.on)bimWalkRebody();
    refreshProps();
    return true;
  }
  /* the walker's body: {top, eye, sh, chair, speed, person} from the registry; the mean adult halfway between the
     registry's man and woman */
  function bimWalkBody(s){
    var P,man,wo;
    if(s.who==='chair')return {top:bimStd('wheel.awmp','height'),eye:bimStd('wheel.awmp','eye'),sh:bimStd('ada.space','clear_w')*0.85,
      chair:true,speed:bimStd('walk.speed','m_min')/60,person:null};
    if(s.who==='adult'){man=bimEntBody({who:'man'});wo=bimEntBody({who:'woman'});P=bimEntBody({h:(man.st+wo.st)/2});}
    else if(s.who==='own')P=bimEntBody({h:s.h});
    else P=bimEntBody({who:s.who});
    return {top:P.top,eye:P.eye,sh:P.sh,chair:false,speed:P.speed,person:P};
  }
  /* the rules: the step a code stair allows, the walker's slope, the wheelchair user's slope (the ADA's where the
     site is in the United States, 1:12 elsewhere), running */
  function bimWalkRules(){
    var rs=bimStd('ada.2010','ramp_slope'),run=bimStd('walk.rules','run');
    return {stepUp:bimWalkStepUp(bimStd('stair.riser','riser'),bimStd('stair.riser','var')),slopeDeg:bimStd('walk.rules','slope'),
      chairSlope:(typeof rs==='number'&&rs>0)?rs/100:1/12,run:(typeof run==='number'&&run>0)?run:2};
  }
  /* where Jolt is asked for, in order, as the rendered view asks for three.js */
  function bimWalkSources(protocol,base){
    var p=String(protocol||''),out=[];
    if(p!=='http:'&&p!=='https:')out.push({u:'runtime/'+BIM_WALK_FILE,sri:false});
    out.push({u:String(base)+BIM_WALK_FILE,sri:true});
    return out;
  }
  /* Jolt, loaded and started once: a promise of it */
  function bimWalkLoad(){
    var W=A3D_WALK;
    if(W.load)return W.load;
    var src=bimWalkSources(window.location&&window.location.protocol,bimLbBase()),i=0;
    W.st='loading';W.err='';
    W.load=new Promise(function(res,rej){
      if(window.BIMJOLT&&window.BIMJOLT.default){res(window.BIMJOLT);return;}
      function next(){
        if(i>=src.length){rej(new Error('Jolt could not be loaded from '+src.map(function(s){return s.u;}).join(' or ')));return;}
        var s=src[i++],tag=document.createElement('script');
        tag.src=s.u;
        if(s.sri){tag.integrity=BIM_WALK_SRI;tag.crossOrigin='anonymous';}
        tag.onload=function(){if(window.BIMJOLT&&window.BIMJOLT.default)res(window.BIMJOLT);else next();};
        tag.onerror=function(){if(tag.parentNode)tag.parentNode.removeChild(tag);next();};
        document.head.appendChild(tag);
      }
      next();
    }).then(function(M){return M.default();}).then(function(J){W.J=J;W.st='ready';return J;},
      function(e){W.st='failed';W.err=String(e&&e.message||e);W.load=null;throw e;});
    return W.load;
  }
  /* an element's triangles in the world, nine numbers a triangle, its faces fanned as the shaded view fans them */
  function bimWalkTris(o){
    var m=meshOf(o),n=0,i,j,f,a,b,c,p=o.pos||[0,0,0],out,k=0;
    if(!m||!m.f)return null;
    for(i=0;i<m.f.length;i++)if(m.f[i].length>=3)n+=m.f[i].length-2;
    if(!n)return null;
    out=new Float32Array(n*9);
    for(i=0;i<m.f.length;i++){
      f=m.f[i];if(f.length<3)continue;a=m.v[f[0]];
      for(j=2;j<f.length;j++){
        b=m.v[f[j-1]];c=m.v[f[j]];
        out[k++]=a[0]+p[0];out[k++]=a[1]+p[1];out[k++]=a[2]+p[2];
        out[k++]=b[0]+p[0];out[k++]=b[1]+p[1];out[k++]=b[2]+p[2];
        out[k++]=c[0]+p[0];out[k++]=c[1]+p[1];out[k++]=c[2]+p[2];
      }
    }
    return out;
  }
  /* the shown elements, each with a signature that changes when its mesh, its place or its showing does */
  function bimWalkItems(){
    var W=A3D_WALK,items=[],i,o,m,s,t,p;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimLayerShown(o)||!bimObjectVisibleOnLevel(o))continue;
      if(o.t==='terrain'){
        if(!o.survey||bimTerrainSuperseded(o))continue;
        t=bimRvTerrainItem(o);
        if(t)items.push({key:o.id,sig:'t'+t.sig,o:o,ter:t});
        continue;
      }
      m=meshOf(o);
      if(!m||!m.f||!m.f.length)continue;
      p=o.pos||[0,0,0];s=W.seen[o.id];
      if(!s||s.m!==m||s.x!==p[0]||s.y!==p[1]||s.z!==p[2])s=W.seen[o.id]={m:m,x:p[0],y:p[1],z:p[2],n:(s?s.n+1:1)};
      items.push({key:o.id,sig:'m'+s.n,o:o});
    }
    return items;
  }
  /* the physics brought up to date with the model: on entering, and every so often while walking (an edit, a layer) */
  function bimWalkSyncModel(){
    var W=A3D_WALK;
    if(!W.phys)return false;
    return bimWalkPhysSync(W.phys,bimWalkItems(),function(it){return it.ter?bimRvTerrainArrays(it.ter).op.pos:bimWalkTris(it.o);});
  }
  /* the ground where nothing is: the shadows' ground (the active level's floor), else 0 */
  function bimWalkGround(){var g=0;try{g=bimShadowGround();}catch(eG){g=0;}return isFinite(g)?g:0;}
  /* where the walker starts: on the first floor below the view's focus; on the ground there when there is none; never
     inside a solid: when something stands within the walker's height over that spot, on top of the highest surface */
  function bimWalkStart(cap){
    var P=A3D_WALK.phys,c=A3D.cam,x=c.tx||0,z=c.tz||0,y0=(c.ty||0)+0.5,d,y,up,top;
    d=bimWalkPhysRay(P,[x,y0,z],[0,-1,0],500);
    y=isFinite(d)?y0-d:bimWalkGround();
    up=bimWalkPhysRay(P,[x,y+0.02,z],[0,1,0],cap.h);
    if(isFinite(up)){
      top=bimWalkPhysRay(P,[x,y+1000,z],[0,-1,0],2000);
      if(isFinite(top))y=y+1000-top;
    }
    return [x,y+0.01,z];
  }
  /* WALK: in or out */
  function bimWalkCommand(){
    if(A3D_WALK.on){bimWalkLeave();return Promise.resolve(false);}
    return bimWalkEnter();
  }
  function bimWalkEnter(){
    var W=A3D_WALK;
    if(W.on)return Promise.resolve(true);
    if(!A3D.on){a3dToast('Open the model first');return Promise.resolve(false);}
    if(A3D_VIEW.kind==='sheet'){a3dToast('Walk is in the model: open the Model tab first');return Promise.resolve(false);}
    if(W.st!=='ready')a3dToast('Walk: loading the physics (about 4 MB, once)');
    return bimWalkLoad().then(function(J){
      if(W.on)return true;
      var s=bimWalkSettings(),c=A3D.cam;
      W.B=bimWalkBody(s);W.R=bimWalkRules();W.cap=bimWalkCapsule(W.B,W.R);
      W.phys=bimWalkPhys(J);W.seen={};
      bimWalkSyncModel();
      W.saved={cam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz},flat:!!A3D.flat};
      A3D.flat=false;
      W.p=bimWalkStart(W.cap);
      bimWalkPhysChar(W.phys,W.cap,W.p);
      W.yaw=c.yaw;W.pitch=0;W.mode='walk';W.view='first';W.ghost=false;W.held={};W.joy=null;W.last=0;W.jump=false;
      W.syncAt=performance.now()+BIM_WALK_SYNC_MS;W.moved=performance.now();
      W.on=true;
      bimWalkControlsOn();
      bimWalkCam();
      W.raf=requestAnimationFrame(bimWalkFrame);
      refreshProps();
      a3dToast('Walk: W A S D to move, the mouse to look; V third person, F fly, Alt through walls, Esc to leave');
      return true;
    },function(e){
      console.warn('[BIM] Walk: '+String(e&&e.message||e),e);
      a3dToast('Walk could not start: '+String(e&&e.message||e));
      return false;
    });
  }
  /* out of the walk: the camera back where it was, everything Jolt holds given back */
  function bimWalkLeave(){
    var W=A3D_WALK,k;
    if(!W.on)return false;
    W.on=false;
    if(W.raf){cancelAnimationFrame(W.raf);W.raf=0;}
    bimWalkControlsOff();
    bimSceneExtra([]);
    if(W.phys){try{bimWalkPhysFree(W.phys);}catch(eF){console.warn('[BIM] Walk: the physics could not be freed',eF);}W.phys=null;}
    W.seen={};
    if(W.saved){for(k in W.saved.cam)if(W.saved.cam.hasOwnProperty(k))A3D.cam[k]=W.saved.cam[k];A3D.flat=W.saved.flat;W.saved=null;}
    paint();refreshProps();
    return true;
  }
  /* the walker's body changed in Properties while walking: a new capsule where they stand */
  function bimWalkRebody(){
    var W=A3D_WALK;
    if(!W.on||!W.phys)return;
    W.B=bimWalkBody(bimWalkSettings());W.cap=bimWalkCapsule(W.B,W.R);
    bimWalkPhysChar(W.phys,W.cap,W.p);
    bimWalkCam();
  }
  /* the camera from the walker: their eyes, or behind and above them on a boom that stops short of a wall */
  function bimWalkCam(){
    var W=A3D_WALK,c,e,d,hit;
    if(W.view==='third'){
      e=[W.p[0],W.p[1]+W.cap.eye,W.p[2]];
      d=[Math.cos(W.pitch)*Math.sin(W.yaw),Math.sin(W.pitch),Math.cos(W.pitch)*Math.cos(W.yaw)];
      hit=bimWalkPhysRay(W.phys,e,d,BIM_WALK_BOOM+0.5);
      c=bimWalkCamThird(W.p,W.cap.eye,W.yaw,W.pitch,BIM_WALK_BOOM,hit);
    }else c=bimWalkCamFirst(W.p,W.cap.eye,W.yaw,W.pitch);
    A3D.cam.tx=c.tx;A3D.cam.ty=c.ty;A3D.cam.tz=c.tz;A3D.cam.yaw=c.yaw;A3D.cam.pitch=c.pitch;A3D.cam.dist=c.dist;
    bimWalkFigure();
  }
  /* the figure at the feet, turned to the walk, in third person only: an object of the scene, not of the model */
  function bimWalkFigure(){
    var W=A3D_WALK,m,cy,sy;
    if(W.view!=='third'){bimSceneExtra([]);return;}
    if(!W.fig||W.fig.B!==W.B){m=W.B.chair?bimEntChairMesh():bimEntPersonMesh(W.B.person);W.fig={B:W.B,src:m};}
    /* the figure faces +z (its marker runs back to front along +z); walking forward is [-sin(yaw), 0, -cos(yaw)],
       so it is turned by the yaw and half a turn: +z goes to [sin(a), 0, cos(a)] turned by a */
    cy=Math.cos(W.yaw+Math.PI);sy=Math.sin(W.yaw+Math.PI);
    if(W.fig.yaw!==W.yaw){
      W.fig.mesh={v:W.fig.src.v.map(function(q){return [q[0]*cy+q[2]*sy,q[1],-q[0]*sy+q[2]*cy];}),f:W.fig.src.f};
      W.fig.yaw=W.yaw;
    }
    bimSceneExtra([{id:'a3d-walker',t:'solid',name:'Walker',col:'#c99a6e',pos:[W.p[0],W.p[1],W.p[2]],mesh:W.fig.mesh}]);
  }
  /* one frame: the controls to a move, the move to the physics, the walker to the camera, the view drawn */
  function bimWalkFrame(t){
    var W=A3D_WALK,dt,inp,v,mode,r,sp,moving;
    W.raf=0;
    if(!W.on)return;
    try{
      dt=W.last?Math.min(0.05,Math.max(0,(t-W.last)/1000)):1/60;W.last=t;
      if(performance.now()>=W.syncAt){bimWalkSyncModel();W.syncAt=performance.now()+BIM_WALK_SYNC_MS;}
      inp=bimWalkKeys(W.held,W.joy);
      sp=W.B.speed*(inp.run?W.R.run/2:1);   /* bimWalkMove doubles a run; the registry's factor is kept */
      mode=(inp.ghost||W.ghost)?'ghost':W.mode;
      v=bimWalkMove(inp,W.yaw,sp,mode!=='walk');
      if(mode==='walk'&&inp.up>0)W.jump=true;
      r=bimWalkPhysStep(W.phys,v,dt,mode,W.jump&&!W.B.chair);
      W.jump=false;
      moving=inp.f||inp.s||inp.up||!r||Math.abs(r.p[0]-W.p[0])+Math.abs(r.p[1]-W.p[1])+Math.abs(r.p[2]-W.p[2])>1e-5;
      if(r)W.p=r.p;
      if(moving)W.moved=performance.now();
      if(W.p[1]<bimWalkGround()-200){W.p=bimWalkStart(W.cap);bimWalkPhysChar(W.phys,W.cap,W.p);a3dToast('Walk: fallen off the model, back on the floor');}
      bimWalkCam();
      paint();
    }catch(eW){
      console.warn('[BIM] Walk stopped',eW);
      a3dToast('Walk stopped: '+String(eW&&eW.message||eW));
      bimWalkLeave();
      return;
    }
    W.raf=requestAnimationFrame(bimWalkFrame);
  }
  /* the switches: first or third person (V), walk or fly (F), through walls (the ghost button; Alt while held) */
  function bimWalkToggle(what){
    var W=A3D_WALK;
    if(!W.on)return false;
    if(what==='view')W.view=W.view==='first'?'third':'first';
    else if(what==='mode'){W.mode=W.mode==='walk'?'fly':'walk';if(W.mode==='walk')W.pitch=Math.max(-1.2,Math.min(1.2,W.pitch));}
    else if(what==='ghost')W.ghost=!W.ghost;
    else return false;
    bimWalkCam();bimWalkControlsTell();paint();
    return true;
  }
  /* the look, from the mouse or a finger */
  function bimWalkLookBy(dx,dy){
    var W=A3D_WALK,l;
    if(!W.on)return;
    l=bimWalkLook({yaw:W.yaw,pitch:W.pitch},dx,dy,BIM_WALK_LOOK);
    W.yaw=l.yaw;W.pitch=l.pitch;W.moved=performance.now();
  }
  /* Properties > View: who walks */
  function bimWalkProp(mk,mv){
    if(mk==='walkwho')return bimWalkSetting('who',mv);
    if(mk==='walkh')return bimWalkSetting('h',mv);
    return false;
  }
  function bimWalkPropsHtml(){
    var s=bimWalkSettings(),o='',k,h;
    for(k in BIM_WALK_WHO)if(BIM_WALK_WHO.hasOwnProperty(k))o+='<option value="'+k+'"'+(s.who===k?' selected':'')+'>'+bimEsc(BIM_WALK_WHO[k])+'</option>';
    h=bimPropRow('Walker','<select data-propmodel="walkwho">'+o+'</select>');
    if(s.who==='own')h+=bimPropRow('Walker height (m)','<input type="number" step="0.01" min="0.8" max="2.3" data-propmodel="walkh" value="'+s.h+'">');
    return h;
  }
export {
  A3D_WALK, bimWalkCam, bimWalkCommand, bimWalkEnter, bimWalkLeave, bimWalkLookBy, bimWalkProp,
  bimWalkPropsHtml, bimWalkToggle
};
