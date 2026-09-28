var A3D_TOUCH_AIM_OFFSET=46;
var BIM_IS_TOUCH=true;
var A3D={sk:null};
var el={touchLen:{style:{display:'none'},querySelector:function(sel){return this._hint;},_hint:{textContent:''}},touchLenInput:{value:''}};
var TOASTS=[];
function a3dToast(msg){TOASTS.push(msg);}
var COMMITTED=[];
function bimCommitTypedLength(len){COMMITTED.push(len);}

  function bimTouchFakeEvent(t,opts){
    opts=opts||{};
    var y=t.clientY-(opts.aim?A3D_TOUCH_AIM_OFFSET:0);
    return {clientX:t.clientX,clientY:y,button:0,ctrlKey:!!opts.ctrlKey,metaKey:false,shiftKey:!!opts.shiftKey,altKey:false,preventDefault:function(){}};
  }

  function bimTouchDist(a,b){var tdx=b.clientX-a.clientX,tdy=b.clientY-a.clientY;return Math.sqrt(tdx*tdx+tdy*tdy);}

  function bimTouchMid(a,b){return [(a.clientX+b.clientX)/2,(a.clientY+b.clientY)/2];}

  function bimSyncTouchLenInput(){
    if(!el.touchLen)return;
    var show=BIM_IS_TOUCH&&!!A3D.sk&&(A3D.sk.tool==='poly'||A3D.sk.tool==='wall');
    el.touchLen.style.display=show?'flex':'none';
    if(show){
      var hint=el.touchLen.querySelector('.a3d-tl-hint');
      if(hint)hint.textContent=A3D.sk.pts.length?('Next length (dir set by drag)'):'Drag to place the first point';
    }
  }

  function bimSubmitTouchLen(){
    if(!el.touchLenInput)return;
    var v=parseFloat(el.touchLenInput.value);
    el.touchLenInput.value='';
    if(!isFinite(v)||v<=0){a3dToast('Enter a positive length');return;}
    bimCommitTypedLength(v);
  }

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?' -- '+detail:''));}}

var t={clientX:100,clientY:500};
var evPlain=bimTouchFakeEvent(t,{});
assert('fake event without aim: Y unchanged', evPlain.clientY===500);
assert('fake event without aim: X unchanged', evPlain.clientX===100);
var evAim=bimTouchFakeEvent(t,{aim:true});
assert('fake event WITH aim: Y shifted up by the offset', evAim.clientY===500-46);
assert('fake event WITH aim: X still unchanged', evAim.clientX===100);
assert('fake event carries button:0 (never triggers pan/secondary paths)', evPlain.button===0);
var evCtrl=bimTouchFakeEvent(t,{ctrlKey:true});
assert('fake event correctly threads ctrlKey for marquee synthesis', evCtrl.ctrlKey===true && evPlain.ctrlKey===false);
assert('fake event has a callable no-op preventDefault (real onDown/onMove/onUp call it)', typeof evPlain.preventDefault==='function');

assert('bimTouchDist: 3-4-5 triangle', Math.abs(bimTouchDist({clientX:0,clientY:0},{clientX:3,clientY:4})-5)<1e-9);
assert('bimTouchMid: simple average', JSON.stringify(bimTouchMid({clientX:0,clientY:0},{clientX:10,clientY:20}))===JSON.stringify([5,10]));

A3D.sk=null;
bimSyncTouchLenInput();
assert('touch-len overlay hidden when not sketching', el.touchLen.style.display==='none');

A3D.sk={tool:'wall',pts:[]};
bimSyncTouchLenInput();
assert('touch-len overlay shown while wall-sketching', el.touchLen.style.display==='flex');
assert('hint text prompts to place the first point when no points yet', el.touchLen.querySelector().textContent.indexOf('first point')>=0, el.touchLen.querySelector().textContent);

A3D.sk={tool:'wall',pts:[[0,0]]};
bimSyncTouchLenInput();
assert('hint text switches to "next length" once a point exists', el.touchLen.querySelector().textContent.toLowerCase().indexOf('length')>=0, el.touchLen.querySelector().textContent);

A3D.sk={tool:'rect'};
bimSyncTouchLenInput();
assert('touch-len overlay hidden for non poly/wall sketch tools (e.g. rect)', el.touchLen.style.display==='none');

COMMITTED.length=0;TOASTS.length=0;
el.touchLenInput.value='abc';
bimSubmitTouchLen();
assert('non-numeric input is rejected, nothing committed', COMMITTED.length===0);
assert('non-numeric input produces a toast message', TOASTS.length===1);

COMMITTED.length=0;TOASTS.length=0;
el.touchLenInput.value='-3';
bimSubmitTouchLen();
assert('negative length is rejected, nothing committed', COMMITTED.length===0);

COMMITTED.length=0;TOASTS.length=0;
el.touchLenInput.value='2.75';
bimSubmitTouchLen();
assert('valid positive length is committed with the correct value', COMMITTED.length===1 && COMMITTED[0]===2.75);
assert('input field is cleared after a successful submit', el.touchLenInput.value==='');

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
