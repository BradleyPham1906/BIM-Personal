import { el } from '../core/state.js';
import { bimWalkJoy } from './walk-math.js';
import { A3D_WALK, bimWalkLeave, bimWalkLookBy, bimWalkToggle } from './walk-mode.js';

  /* ================= __acad3dV203: Walkthrough W1, the controls on the page =================
     docs/work-orders/v203/SPEC.md, C-06. While walking, the view's own handlers (orbit, pick, the app's keys) are held
     back: these listeners sit in the capture phase on the view and the window and stop what they take.
     - Desktop: a click on the view locks the pointer and the mouse looks; without the lock a drag looks. W A S D or the
       arrows move, Shift runs, Space jumps (rises in Fly), C sinks, Alt held goes through walls, V third person,
       F fly, Esc (or Leave) ends the walk.
     - Phone and tablet: a joystick under the left thumb moves (bimWalkJoy), a drag anywhere else looks.
     - The bar at the top: Leave, First or Third person, Walk or Fly, Through walls; a line saying what the keys do.
     A key typed into a field (Properties) is the field's. */
  var A3D_WALKUI={on:false,bar:null,joy:null,knob:null,hint:null,joyId:null,lookId:null,lx:0,ly:0,h:{}};
  function bimWalkVp(){return el.cv&&el.cv.parentNode?el.cv.parentNode:null;}
  function bimWalkInField(ev){var t=ev.target,n=t&&t.tagName;return n==='INPUT'||n==='TEXTAREA'||n==='SELECT'||!!(t&&t.isContentEditable);}
  function bimWalkInUi(ev){return !!(ev.target&&ev.target.closest&&ev.target.closest('.a3d-walkbar,.a3d-walkjoy'));}
  function bimWalkLocked(){return document.pointerLockElement===el.cv;}
  /* the bar, the hint and the joystick, made once and shown while walking */
  function bimWalkUiBuild(){
    var U=A3D_WALKUI,vp=bimWalkVp();
    if(U.bar||!vp)return;
    U.bar=document.createElement('div');U.bar.className='a3d-walkbar';
    U.bar.innerHTML='<button type="button" data-walkact="leave">Leave</button><button type="button" data-walkact="view"></button>'+
      '<button type="button" data-walkact="mode"></button><button type="button" data-walkact="ghost">Through walls</button>';
    U.hint=document.createElement('div');U.hint.className='a3d-walkhint';
    U.joy=document.createElement('div');U.joy.className='a3d-walkjoy';U.joy.setAttribute('aria-label','Move');
    U.knob=document.createElement('div');U.knob.className='a3d-walkknob';U.joy.appendChild(U.knob);
    vp.appendChild(U.bar);vp.appendChild(U.hint);vp.appendChild(U.joy);
    U.bar.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-walkact]'):null,a;
      if(!b)return;
      ev.preventDefault();ev.stopPropagation();
      a=b.getAttribute('data-walkact');
      if(a==='leave')bimWalkLeave();else bimWalkToggle(a);
    });
  }
  /* the bar's words and states, as the walk is now */
  function bimWalkControlsTell(){
    var U=A3D_WALKUI,W=A3D_WALK,b;
    if(!U.bar)return;
    b=U.bar.querySelector('[data-walkact="view"]');if(b)b.textContent=W.view==='first'?'First person':'Third person';
    b=U.bar.querySelector('[data-walkact="mode"]');if(b)b.textContent=W.mode==='walk'?'Walk':'Fly';
    b=U.bar.querySelector('[data-walkact="ghost"]');if(b)b.classList.toggle('on',!!W.ghost);
    if(U.hint)U.hint.textContent=W.mode==='fly'?'W A S D move, Space rises, C sinks, Shift runs, F walk, V view, Esc leaves':
      'W A S D move, the mouse looks (click to hold it), Shift runs, Space jumps, Alt through walls, F fly, V view, Esc leaves';
  }
  /* the keys: held ones for the move, V and F switch, Esc leaves; the app's own shortcuts held back while walking */
  function bimWalkKeyDown(ev){
    var W=A3D_WALK,c=ev.code;
    if(!W.on||bimWalkInField(ev))return;
    if(c==='Escape'){ev.preventDefault();ev.stopPropagation();if(bimWalkLocked())return;bimWalkLeave();return;}
    ev.stopPropagation();
    if(c==='KeyV'&&!ev.repeat){ev.preventDefault();bimWalkToggle('view');return;}
    if(c==='KeyF'&&!ev.repeat){ev.preventDefault();bimWalkToggle('mode');return;}
    if(c==='AltLeft'||c==='AltRight'||c==='Space'||c.indexOf('Arrow')===0)ev.preventDefault();
    W.held[c]=true;
  }
  function bimWalkKeyUp(ev){
    var W=A3D_WALK;
    if(!W.on||bimWalkInField(ev))return;
    ev.stopPropagation();
    if(ev.code==='AltLeft'||ev.code==='AltRight')ev.preventDefault();
    delete W.held[ev.code];
  }
  /* nothing held once the page loses the keyboard */
  function bimWalkBlur(){A3D_WALK.held={};A3D_WALK.joy=null;}
  /* the pointer on the view: the joystick, a look, or the lock */
  function bimWalkPtrDown(ev){
    var U=A3D_WALKUI,r;
    if(!A3D_WALK.on||bimWalkInUi(ev)&&!(ev.target&&ev.target.closest&&ev.target.closest('.a3d-walkjoy')))return;
    ev.stopPropagation();ev.preventDefault();
    if(ev.target&&ev.target.closest&&ev.target.closest('.a3d-walkjoy')){
      U.joyId=ev.pointerId;bimWalkJoyAt(ev);
      try{U.joy.setPointerCapture(ev.pointerId);}catch(eC){}
      return;
    }
    if(ev.pointerType==='mouse'&&!bimWalkLocked()&&el.cv.requestPointerLock){
      try{r=el.cv.requestPointerLock();if(r&&r.catch)r.catch(function(){});}catch(eL){}
    }
    U.lookId=ev.pointerId;U.lx=ev.clientX;U.ly=ev.clientY;
  }
  function bimWalkPtrMove(ev){
    var U=A3D_WALKUI;
    if(!A3D_WALK.on)return;
    if(U.joyId!==null&&ev.pointerId===U.joyId){ev.preventDefault();bimWalkJoyAt(ev);return;}
    if(bimWalkLocked()){bimWalkLookBy(ev.movementX||0,ev.movementY||0);return;}
    if(U.lookId!==null&&ev.pointerId===U.lookId){
      ev.preventDefault();
      bimWalkLookBy(ev.clientX-U.lx,ev.clientY-U.ly);U.lx=ev.clientX;U.ly=ev.clientY;
    }
  }
  function bimWalkPtrUp(ev){
    var U=A3D_WALKUI;
    if(U.joyId!==null&&ev.pointerId===U.joyId){U.joyId=null;A3D_WALK.joy=null;if(U.knob)U.knob.style.transform='';}
    if(U.lookId!==null&&ev.pointerId===U.lookId)U.lookId=null;
  }
  /* the joystick from a finger: bimWalkJoy, the knob drawn where it points */
  function bimWalkJoyAt(ev){
    var U=A3D_WALKUI,r=U.joy.getBoundingClientRect(),R=r.width/2,j=bimWalkJoy(r.left+R,r.top+R,ev.clientX,ev.clientY,R,0.12);
    A3D_WALK.joy=j;
    U.knob.style.transform='translate('+Math.round(j.s*R*0.6)+'px,'+Math.round(-j.f*R*0.6)+'px)';
  }
  /* the view's own handlers held back: whatever starts on the view stops here while walking */
  function bimWalkSwallow(ev){if(A3D_WALK.on&&!bimWalkInUi(ev)){ev.stopPropagation();if(ev.cancelable)ev.preventDefault();}}
  function bimWalkControlsOn(){
    var U=A3D_WALKUI,vp=bimWalkVp(),h=U.h;
    bimWalkUiBuild();
    if(U.on||!vp)return;
    U.on=true;U.joyId=null;U.lookId=null;
    h.kd=bimWalkKeyDown;h.ku=bimWalkKeyUp;h.bl=bimWalkBlur;h.pd=bimWalkPtrDown;h.pm=bimWalkPtrMove;h.pu=bimWalkPtrUp;h.sw=bimWalkSwallow;
    window.addEventListener('keydown',h.kd,true);window.addEventListener('keyup',h.ku,true);window.addEventListener('blur',h.bl);
    vp.addEventListener('pointerdown',h.pd,true);window.addEventListener('pointermove',h.pm,true);window.addEventListener('pointerup',h.pu,true);
    window.addEventListener('pointercancel',h.pu,true);
    ['mousedown','touchstart','wheel','dblclick','contextmenu'].forEach(function(n){vp.addEventListener(n,h.sw,{capture:true,passive:false});});
    vp.classList.add('a3d-walking');
    bimWalkControlsTell();
  }
  function bimWalkControlsOff(){
    var U=A3D_WALKUI,vp=bimWalkVp(),h=U.h;
    if(!U.on)return;
    U.on=false;
    window.removeEventListener('keydown',h.kd,true);window.removeEventListener('keyup',h.ku,true);window.removeEventListener('blur',h.bl);
    window.removeEventListener('pointermove',h.pm,true);window.removeEventListener('pointerup',h.pu,true);window.removeEventListener('pointercancel',h.pu,true);
    if(vp){
      vp.removeEventListener('pointerdown',h.pd,true);
      ['mousedown','touchstart','wheel','dblclick','contextmenu'].forEach(function(n){vp.removeEventListener(n,h.sw,{capture:true,passive:false});});
      vp.classList.remove('a3d-walking');
    }
    if(bimWalkLocked()&&document.exitPointerLock)document.exitPointerLock();
    U.joyId=null;U.lookId=null;
    if(U.knob)U.knob.style.transform='';
  }
export { bimWalkControlsOff, bimWalkControlsOn, bimWalkControlsTell };
