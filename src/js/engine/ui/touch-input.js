  // ---- __acad3dV8: Touch input (single-finger nav/select/move, long-press marquee, two-finger pinch/pan, touch-aim sketch placement) ----
  var BIM_IS_TOUCH=(('ontouchstart' in window)||(navigator.maxTouchPoints>0));
  var A3D_TOUCH_AIM_OFFSET=46;
  var A3D_TOUCH_TAP_THRESH=8;
  var A3D_TOUCH_LONGPRESS_MS=480;
  var A3D_TOUCH=null;
  function bimTouchFakeEvent(t,opts){
    opts=opts||{};
    var y=t.clientY-(opts.aim?A3D_TOUCH_AIM_OFFSET:0);
    return {clientX:t.clientX,clientY:y,button:0,ctrlKey:!!opts.ctrlKey,metaKey:false,shiftKey:!!opts.shiftKey,altKey:false,preventDefault:function(){}};
  }
  function bimTouchDist(a,b){var tdx=b.clientX-a.clientX,tdy=b.clientY-a.clientY;return Math.sqrt(tdx*tdx+tdy*tdy);}
  function bimTouchMid(a,b){return [(a.clientX+b.clientX)/2,(a.clientY+b.clientY)/2];}
  function onTouchStart(ev){
    if(!A3D.on)return;
    if(ev.touches.length===1){
      var t=ev.touches[0];
      if(A3D.sk){
        A3D_TOUCH={mode:'aim',t0:t};
        onHover(bimTouchFakeEvent(t,{aim:true}));
        ev.preventDefault();
        return;
      }
      A3D_TOUCH={mode:'pending',t0:t,x0:t.clientX,y0:t.clientY};
      A3D_TOUCH.timer=setTimeout(function(){
        if(A3D_TOUCH&&A3D_TOUCH.mode==='pending'){
          A3D_TOUCH.mode='marquee';
          onDown(bimTouchFakeEvent(A3D_TOUCH.t0,{ctrlKey:true}));
          if(navigator.vibrate)navigator.vibrate(12);
          a3dToast('Box-select: drag, lift to apply');
        }
      },A3D_TOUCH_LONGPRESS_MS);
      ev.preventDefault();
    }else if(ev.touches.length===2){
      if(A3D_TOUCH&&A3D_TOUCH.timer)clearTimeout(A3D_TOUCH.timer);
      if(A3D_TOUCH&&(A3D_TOUCH.mode==='single'||A3D_TOUCH.mode==='marquee')){
        onUp(bimTouchFakeEvent(ev.touches[0],{}));
      }
      var d0=bimTouchDist(ev.touches[0],ev.touches[1]),m0=bimTouchMid(ev.touches[0],ev.touches[1]);
      var cc=A3D.cam;
      A3D_TOUCH={mode:'pinch',d0:d0,mid0:m0,camStart:{dist:cc.dist,tx:cc.tx,ty:cc.ty,tz:cc.tz}};
      ev.preventDefault();
    }
  }
  function onTouchMove(ev){
    if(!A3D.on||!A3D_TOUCH)return;
    if(A3D_TOUCH.mode==='aim'){
      onHover(bimTouchFakeEvent(ev.touches[0],{aim:true}));
      ev.preventDefault();
      return;
    }
    if(A3D_TOUCH.mode==='pending'){
      var tp=ev.touches[0];
      var pdx=tp.clientX-A3D_TOUCH.x0,pdy=tp.clientY-A3D_TOUCH.y0;
      if(Math.abs(pdx)>A3D_TOUCH_TAP_THRESH||Math.abs(pdy)>A3D_TOUCH_TAP_THRESH){
        clearTimeout(A3D_TOUCH.timer);
        A3D_TOUCH.mode='single';
        onDown(bimTouchFakeEvent(A3D_TOUCH.t0,{}));
        onMove(bimTouchFakeEvent(tp,{}));
      }
      ev.preventDefault();
      return;
    }
    if(A3D_TOUCH.mode==='single'||A3D_TOUCH.mode==='marquee'){
      onMove(bimTouchFakeEvent(ev.touches[0],{}));
      ev.preventDefault();
      return;
    }
    if(A3D_TOUCH.mode==='pinch'&&ev.touches.length===2){
      var d1=bimTouchDist(ev.touches[0],ev.touches[1]),m1=bimTouchMid(ev.touches[0],ev.touches[1]);
      var c2=A3D.cam,scale=A3D_TOUCH.d0/Math.max(d1,1);
      c2.dist=A3D_TOUCH.camStart.dist*scale;
      c2.dist=bimZoomClamp(c2.dist);   /* __acad3dV133e */
      var V2=camVecs(c2),k2=c2.dist*0.0018,dxp=m1[0]-A3D_TOUCH.mid0[0],dyp=m1[1]-A3D_TOUCH.mid0[1];
      c2.tx=A3D_TOUCH.camStart.tx-(V2.r[0]*dxp-V2.u[0]*dyp)*k2;
      c2.ty=A3D_TOUCH.camStart.ty-(V2.r[1]*dxp-V2.u[1]*dyp)*k2;
      c2.tz=A3D_TOUCH.camStart.tz-(V2.r[2]*dxp-V2.u[2]*dyp)*k2;
      paint();saveSoon();
      ev.preventDefault();
    }
  }
  function onTouchEnd(ev){
    if(!A3D.on||!A3D_TOUCH)return;
    if(A3D_TOUCH.timer)clearTimeout(A3D_TOUCH.timer);
    if(A3D_TOUCH.mode==='aim'){
      var te=ev.changedTouches[0];
      onDown(bimTouchFakeEvent(te,{aim:true}));
      onUp(bimTouchFakeEvent(te,{aim:true}));
    }else if(A3D_TOUCH.mode==='pending'){
      onDown(bimTouchFakeEvent(A3D_TOUCH.t0,{}));
      onUp(bimTouchFakeEvent(A3D_TOUCH.t0,{}));
    }else if(A3D_TOUCH.mode==='single'||A3D_TOUCH.mode==='marquee'){
      var lt=(ev.changedTouches&&ev.changedTouches[0])?ev.changedTouches[0]:A3D_TOUCH.t0;
      onUp(bimTouchFakeEvent(lt,{ctrlKey:A3D_TOUCH.mode==='marquee'}));
    }else if(A3D_TOUCH.mode==='pinch'){
      if(ev.touches.length===1){
        var rem=ev.touches[0];
        A3D_TOUCH={mode:'single',t0:rem};
        onDown(bimTouchFakeEvent(rem,{}));
        ev.preventDefault();
        return;
      }
    }
    if(ev.touches.length===0)A3D_TOUCH=null;
    ev.preventDefault();
  }
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
  function onKey(ev){
    if(!A3D.on)return;
    /* __acad3dV124: a drag from the library is the innermost thing Escape can end */
    if(ev.key==='Escape'&&bimAssetDragCancel()){a3dToast('Nothing placed');ev.preventDefault();ev.stopImmediatePropagation();return;}
    if(A3D_SLIDESHOW.on){bimSlideshowKey(ev);return;}   /* __acad3dV122: nothing typed reaches the model */
    /* __acad3dV115: the Start page covers the project behind it; a key typed there is not for it */
    if(bimStartShowing())return;
    if(bimClbKey(ev))return;   /* __acad3dV162: a board's page owns the keys, as a sheet's does */
    if(bimSheetOnScreen()&&bimSheetKey(ev))return;   /* __acad3dV116 */
    /* __acad3dV112: a gizmo drag is listening. Digits build an exact value, Enter applies it,
       Escape puts everything back -- and the key is consumed here, before anything else in the
       app can read it as a command. */
    if(bimTypingDrag()){   /* __acad3dV123: a push listens as a gizmo drag does */
      if(!bimKeyForControl(ev)&&bimGizmoTypeKey(ev)){   /* __acad3dV117 */
        ev.preventDefault();ev.stopImmediatePropagation();
        return;
      }
    }
    /* __acad3dV110: Escape with the gizmo menu open closes the menu and does nothing else. It is
       caught here, in the app's own window-capture handler, because a listener anywhere later in
       the event's path runs after this one has already cleared the selection. */
    if(ev.key==='Escape'&&document.getElementById('a3d-gizmenu')){
      bimCloseGizmoMenu();
      ev.preventDefault();ev.stopImmediatePropagation();
      return;
    }
    if(bimKeyForControl(ev))return;   /* __acad3dV117: the one test, which knows a dropdown */
    /* __acad3dV118: an open dialog owns the keyboard. Only Escape, which closes it, and the function
       keys, which set drawing aids, reach past it. Seven branches below used to check for a dialog
       one by one and the nudge keys and Undo / Redo did not: with the focus off a dialog's fields,
       ArrowDown moved the selected object behind it a metre, and Ctrl+Z undid the object a dialog
       was about to act on. One gate, so a branch added later cannot forget it. */
    if(el.dlg&&ev.key!=='Escape'&&!/^F\d+$/.test(ev.key))return;
    /* __acad3dV123: a held face's keys, from A3D_FACE_KEYS (Escape is in the chain below) */
    if(A3D.face&&!drag&&!ev.ctrlKey&&!ev.metaKey&&!ev.altKey&&ev.key!=='Escape'){
      var fkey=bimFaceKeyFor(ev);
      if(fkey&&bimFaceCurrent()){bimFaceKeyRun(fkey,ev);ev.preventDefault();ev.stopImmediatePropagation();return;}
    }
    /* __acad3dV86: AutoCAD's input model for the point-taking tools.

       The buffer used to accept [0-9.] only, and only for poly and wall, and it only ever meant
       a length. It now accepts the full coordinate grammar -- 3,4 / @3,4 / 3<45 / @1<45 / #3,4
       and a bare number for direct distance entry -- for every tool that takes points.

       Option letters are read ONLY when nothing is typed, because 'c' and 'u' are not part of a
       coordinate: while a number is being entered they would be a typo, not a command. */
    if(A3D.sk&&BIM_COORD_TOOLS[A3D.sk.tool]){
      if(!ev.ctrlKey&&!ev.metaKey&&/^[0-9.,@<#-]$/.test(ev.key)){
        A3D_TYPING.active=true;A3D_TYPING.buf+=ev.key;
        bimSyncStatusHint();paint();ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      if(A3D_TYPING.active){
        if(ev.key==='Backspace'){
          A3D_TYPING.buf=A3D_TYPING.buf.slice(0,-1);
          if(!A3D_TYPING.buf.length)A3D_TYPING.active=false;
          bimSyncStatusHint();paint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Enter'||ev.key===' '){
          var typedStr=A3D_TYPING.buf;
          A3D_TYPING.active=false;A3D_TYPING.buf='';
          bimCommitTypedPoint(typedStr);
          ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Escape'){
          A3D_TYPING.active=false;A3D_TYPING.buf='';
          bimSyncStatusHint();paint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
      }else{
        /* __acad3dV94: one ordered table instead of five if-statements that each restated
           their own condition. onKey dispatches through it and __a3dWantsKey queries it, so
           "will the drawing consume this letter" has exactly one answer. */
        var skHit=bimSketchKeyFor(A3D.sk,ev);
        if(skHit){
          skHit.run(A3D.sk,ev);
          ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Enter'||ev.key===' '){
          bimFinishCurrent();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
      }
    }
    if(ev.key==='F8'){A3D_SNAP.ortho=!A3D_SNAP.ortho;a3dToast('Ortho '+(A3D_SNAP.ortho?'on':'off')+' (F8)');syncSnapPill();paint();ev.preventDefault();return;}
    if(ev.key==='F3'){A3D_SNAP.point=!A3D_SNAP.point;a3dToast('Object snap '+(A3D_SNAP.point?'on':'off')+' (F3)');syncSnapPill();paint();ev.preventDefault();return;}
    if(ev.key==='F9'){A3D_SNAP.grid=!A3D_SNAP.grid;a3dToast('Grid snap '+(A3D_SNAP.grid?'on':'off')+' (F9)');syncSnapPill();paint();ev.preventDefault();return;}
    if((ev.ctrlKey||ev.metaKey)&&!ev.shiftKey&&(ev.key==='z'||ev.key==='Z')){
      doUndo();ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    if((ev.ctrlKey||ev.metaKey)&&((ev.key==='y'||ev.key==='Y')||(ev.shiftKey&&(ev.key==='z'||ev.key==='Z')))){
      doRedo();ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    if((ev.ctrlKey||ev.metaKey)&&(ev.key==='d'||ev.key==='D')){
      duplicateSelection();ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    if((ev.ctrlKey||ev.metaKey)&&(ev.key==='s'||ev.key==='S')){
      bimExportProjectFile();ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    if((ev.ctrlKey||ev.metaKey)&&!ev.shiftKey&&(ev.key==='o'||ev.key==='O')){   /* __acad3dV115: OPEN */
      bimOpenProjectPicker();ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    if(ev.key==='Escape'){
      /* __acad3dV83: the rail's own transient layers come FIRST in this chain.

         Escape walks outwards -- dialog, constraint pick, sketch, section, selection. A rail
         menu and an armed zoom window are the innermost things, so they back out first.

         Put HERE rather than in a listener of its own: a separate handler cannot win, since
         this one is registered at load and calls stopImmediatePropagation. Same-phase
         listeners run in registration order, so any later handler is simply never reached --
         which is exactly what happened to the first attempt. */
      var ruPop=document.getElementById('a3d-rupop');
      if(ruPop&&ruPop.classList.contains('open')){
        bimCloseRailPop();ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      if(A3D.zoomWindow){
        bimCancelZoomWindow();a3dToast('Zoom window cancelled');
        ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      if(el.dlg){closeDlg();ev.preventDefault();ev.stopImmediatePropagation();return;}
      if(A3D.conPick){cancelConstraintPick();ev.preventDefault();ev.stopImmediatePropagation();return;}
      if(A3D.sk){bimEndSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}   /* __acad3dV100 */
      /* __acad3dV123: PRESSPULL waiting for its click, then a held face -- inner to the selection */
      if(A3D.facePick){A3D.facePick=false;bimSyncStatusHint();a3dToast('PRESSPULL cancelled');ev.preventDefault();ev.stopImmediatePropagation();return;}
      if(A3D.face&&bimFaceCurrent()){bimFaceExit();ev.preventDefault();ev.stopImmediatePropagation();return;}
      if(A3D.section){bimExitSection();ev.preventDefault();ev.stopImmediatePropagation();return;}
      /* __acad3dV85: the chain STOPS here. Views are the navigation, so there is nothing to back
         out TO, and the most reflexive key in a drawing application should never close the
         workspace. Clearing the selection is the last step -- what Escape does in Revit and in
         AutoCAD. Past that, Escape does nothing and says nothing. */
      if(A3D.sel||A3D.sel2||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid()){
        A3D.sel=null;A3D.sel2=null;A3D.selSet=[];A3D.selGrid=null;   /* __acad3dV98 */
        refreshLevels();refreshTree();refreshProps();paint();
        ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      return;
    }
    if(ev.key==='>'){
      toggleFlat();ev.preventDefault();return;
    }
    /* __acad3dV86: the per-tool Enter handlers and the 'C' closes handler that used to sit here
       are gone. The branch above reaches every one of their cases first and returns, so leaving
       them would have stranded four unreachable handlers in the chain -- and the C handler
       carried the wrong threshold for LINE besides. Its original note is worth keeping: before
       it existed, the only way to close a path was to click within 0.09 units of the start
       point, a tolerance tight enough that walls almost always finished OPEN, which silently
       broke Room, Floor and Roof. Found by real browser testing, not unit tests. */
    if((ev.key==='Enter'||ev.key===' ')&&!A3D.sk&&!A3D.conPick&&A3D.lastCmd){
      bimRepeatLastCommand();ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    /* __acad3dV117: Delete -- and Backspace, the delete key of a Mac keyboard -- erases the selection.
       It sits behind the gates -- the Start page, a sheet, a field, a gizmo value or a point being
       typed, and an open dialog (one gate since V118) -- so Delete cannot erase the selection of
       the project behind the Start page, or the object a dialog sits over. Last before the nudge
       keys. */
    if((ev.key==='Delete'||ev.key==='Backspace')&&!ev.ctrlKey&&!ev.metaKey){
      try{
        if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();   /* __acad3dV98's test */
      }catch(eDel){console.warn('[BIM] Delete failed.',eDel);a3dToast('Could not delete the selection');}
      ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    var o=null,i;
    if(A3D.sel)for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===A3D.sel)o=A3D.objs[i];
    if(!o)return;
    var nudged=bimNudgeObject(o,ev.key);
    if(nudged){ev.preventDefault();paint();saveSoon();}
  }

  function closeDlg(){
    if(el.dlg&&el.dlg.parentNode)el.dlg.parentNode.removeChild(el.dlg);
    el.dlg=null;
  }
  function openDlg(t){
    var tp=TYPES[t];if(!tp||!el.root)return;
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var h='<div class="a3d-dlghd">'+tp.n+' parameters</div><div class="a3d-dlgbody">',i;
    for(i=0;i<tp.prm.length;i++){
      h+='<div class="a3d-dlgrow"><label>'+tp.prm[i][0]+'</label>'+
        '<input type="number" step="any" data-a3dp="'+tp.prm[i][0]+'" value="'+tp.prm[i][1]+'"></div>';
    }
    h+='<div id="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft">'+
      '<button class="a3d-btn" data-a3dlg="cancel">Cancel</button>'+
      '<button class="a3d-btn a3d-btn-pri" data-a3dlg="ok">OK</button></div>';
    d.innerHTML=h;
    el.root.appendChild(d);
    el.dlg=d;
    function submit(){
      var ins=d.querySelectorAll('[data-a3dp]'),given={},j;
      for(j=0;j<ins.length;j++)given[ins[j].getAttribute('data-a3dp')]=ins[j].value;
      var p=mergePrm(t,given);
      var err=validatePrm(t,p);
      var eb=d.querySelector('#a3d-dlgerr');
      if(err){if(eb)eb.textContent=err;return;}
      closeDlg();
      add3d(t,p);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      var act=b.getAttribute('data-a3dlg');
      if(act==='ok')submit();
      else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    var f=d.querySelector('input');
    if(f){f.focus();try{f.select();}catch(e2){}}
  }

  function ric(inner){
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4">'+inner+'</svg>';
  }
  var A3DR_ICONS={
    box:ric('<path d="M4 8l8-4 8 4v8l-8 4-8-4z"/><path d="M4 8l8 4 8-4M12 12v8"/>'),
    cyl:ric('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v12M19 6v12"/><ellipse cx="12" cy="18" rx="7" ry="3"/>'),
    sphere:ric('<circle cx="12" cy="12" r="8"/><ellipse cx="12" cy="12" rx="8" ry="3"/>'),
    cone:ric('<path d="M12 4l7 14M12 4L5 18"/><ellipse cx="12" cy="18" rx="7" ry="2.6"/>'),
    torus:ric('<ellipse cx="12" cy="12" rx="9" ry="5.5"/><ellipse cx="12" cy="12" rx="3.5" ry="1.8"/>'),
    tube:ric('<ellipse cx="12" cy="6" rx="7" ry="3"/><ellipse cx="12" cy="6" rx="3" ry="1.3"/><path d="M5 6v12M19 6v12"/><ellipse cx="12" cy="18" rx="7" ry="3"/>'),
    prism:ric('<path d="M7 5h10l3 5-3 9H7l-3-9z"/><path d="M4 10h16"/>'),
    wedge:ric('<path d="M4 18h16l-4-12H8z"/><path d="M8 6l-4 12M16 6l4 12"/>'),
    ellipsoid:ric('<ellipse cx="12" cy="12" rx="9" ry="5"/><ellipse cx="12" cy="12" rx="4" ry="5"/>'),
    vhome:ric('<path d="M4 11l8-7 8 7"/><path d="M6 10v9h12v-9"/>'),
    vfit:ric('<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/><rect x="9" y="9" width="6" height="6"/>'),
    vtop:ric('<rect x="5" y="5" width="14" height="14"/><path d="M12 2v3M9 3l3-1 3 1"/>'),
    vfront:ric('<rect x="5" y="8" width="14" height="11"/><path d="M5 8l3-4h8l3 4"/>'),
    vright:ric('<rect x="8" y="5" width="11" height="14"/><path d="M8 5L4 8v8l4 3"/>'),
    viso:ric('<path d="M12 3l8 5v8l-8 5-8-5V8z"/><path d="M12 3v18M4 8l8 5 8-5"/>'),
    del:ric('<path d="M5 7h14M9 7V5h6v2M8 7l1 13h6l1-13"/>'),
    desel:ric('<rect x="4" y="4" width="16" height="16" stroke-dasharray="3 2"/><path d="M8 12h8"/>'),
    dup:ric('<rect x="4" y="4" width="12" height="12"/><rect x="9" y="9" width="12" height="12"/>'),
    array:ric('<rect x="3" y="3" width="6" height="6"/><rect x="10" y="3" width="6" height="6"/><rect x="17" y="3" width="4" height="6"/><rect x="3" y="15" width="6" height="6"/>'),
    union:ric('<circle cx="9.5" cy="12" r="6"/><circle cx="14.5" cy="12" r="6"/>'),
    cut:ric('<circle cx="9.5" cy="12" r="6"/><circle cx="14.5" cy="12" r="6" stroke-dasharray="2 2"/>'),
    isect:ric('<circle cx="9.5" cy="12" r="6" stroke-dasharray="2 2"/><circle cx="14.5" cy="12" r="6" stroke-dasharray="2 2"/><path d="M12 9v6"/>'),
    's:rect':ric('<rect x="5" y="7" width="14" height="10" rx="1"/>'),
    's:circle':ric('<circle cx="12" cy="12" r="6.5"/>'),
    's:poly':ric('<path d="M5 16l4-8 5 4 5-6"/><circle cx="5" cy="16" r="1.3"/><circle cx="9" cy="8" r="1.3"/><circle cx="14" cy="12" r="1.3"/><circle cx="19" cy="6" r="1.3"/>'),
    'p:pad':ric('<rect x="6" y="12" width="12" height="7"/><path d="M12 12V4M9 7l3-3 3 3"/>'),
    'p:pocket':ric('<rect x="5" y="6" width="14" height="13"/><path d="M9 6v6h6V6"/>'),
    'con:coincident':ric('<circle cx="9" cy="12" r="4"/><circle cx="15" cy="12" r="4" stroke-dasharray="2 2"/>'),
    'con:horizontal':ric('<path d="M4 12h16"/><circle cx="4" cy="12" r="1.6"/><circle cx="20" cy="12" r="1.6"/>'),
    'con:vertical':ric('<path d="M12 4v16"/><circle cx="12" cy="4" r="1.6"/><circle cx="12" cy="20" r="1.6"/>'),
    'con:parallel':ric('<path d="M5 8l6-4M5 8l14 3M5 16l6-4M5 16l14 3"/>'),
    'con:perpendicular':ric('<path d="M5 5v14h14"/><rect x="5" y="14" width="5" height="5"/>'),
    'con:equal':ric('<path d="M4 9h7M4 15h7"/><path d="M13 9h7M13 15h7"/>'),
    'con:distance':ric('<path d="M5 8v8M19 8v8"/><path d="M5 12h14"/><path d="M16 9l3 3-3 3M8 9l-3 3 3 3"/>'),
    'con:angle':ric('<path d="M4 18h16M4 18L16 6"/><path d="M9 18a5 5 0 0 1 1.5-3.5" stroke-dasharray="2 2"/>'),
    'con:pointonline':ric('<path d="M4 12h16"/><circle cx="13" cy="12" r="2.2"/>'),
    'con:midpoint':ric('<path d="M4 12h16"/><circle cx="12" cy="12" r="2.2"/><path d="M4 9v6M20 9v6" stroke-dasharray="2 2"/>'),
    'con:symmetric_pt':ric('<circle cx="5" cy="12" r="2"/><circle cx="19" cy="12" r="2"/><circle cx="12" cy="12" r="1.2"/><path d="M5 12h14" stroke-dasharray="2 2"/>'),
    'con:symmetric_line':ric('<path d="M12 4v16" stroke-dasharray="2 2"/><circle cx="6" cy="12" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 12h12"/>'),
    'bim:wall':ric('<rect x="3" y="9" width="18" height="6"/><path d="M3 9l4-4M8 9l4-4M13 9l4-4M18 9l3-3"/>'),
    'bim:floor':ric('<rect x="4" y="6" width="16" height="12"/><path d="M4 10h16M4 14h16M9.3 6v12M14.6 6v12"/>'),
    'bim:column':ric('<rect x="8" y="4" width="8" height="16"/><path d="M6 4h12M6 20h12"/>'),
    'bim:door':ric('<path d="M5 21V4h11v17"/><path d="M5 21h13"/><path d="M13 12.5v0.1"/><path d="M5 4l11 3v14"/>'),
    'bim:window':ric('<rect x="4" y="4" width="16" height="16"/><path d="M12 4v16M4 12h16"/>'),
    'bim:room':ric('<rect x="4" y="4" width="16" height="16" stroke-dasharray="3 2"/><path d="M9 12l2 2 4-4" stroke-dasharray="0"/>'),
    'bim:roof':ric('<path d="M2 12L12 4l10 8"/><path d="M4 12v8h16v-8"/>'),
    'bim:stair':ric('<path d="M3 20h4v-4h4v-4h4v-4h4V4"/>'),
    'bim:dim':ric('<path d="M3 8v8M21 8v8M3 12h18"/><path d="M6 9l-3 3 3 3M18 9l3 3-3 3"/>'),
    'bim:text':ric('<path d="M5 5h14M12 5v14"/>'),
    'bim:dimang':ric('<path d="M4 20h16"/><path d="M4 20L16 6"/><path d="M9 20a7 7 0 0 0 1.6-4.4" fill="none"/>'),
    'bim:dimrad':ric('<circle cx="12" cy="12" r="8"/><path d="M12 12l6-4"/>'),
    'bim:dimdia':ric('<circle cx="12" cy="12" r="8"/><path d="M6 15l12-6"/>'),
    'bim:leader':ric('<path d="M4 20l6-6 10-2"/><path d="M4 20l4-1M4 20l1-4"/>'),
    'bim:component':ric('<rect x="4" y="9" width="16" height="11" rx="1"/><path d="M4 9l8-5 8 5"/><path d="M9 20v-6h6v6"/>'),
    'bim:famsave':ric('<path d="M5 4h11l3 3v13H5z"/><path d="M8 4v6h7V4"/><rect x="8" y="13" width="8" height="7"/>'),
    'bim:famimport':ric('<path d="M4 15v4h16v-4"/><path d="M12 4v10"/><path d="M8 10l4 4 4-4"/>'),
    'bim:level':ric('<path d="M3 12h18"/><rect x="15" y="8" width="6" height="8"/><circle cx="4" cy="12" r="1.4"/>'),
    'bim:levels':ric('<path d="M3 7h18M3 12h18M3 17h18"/>'),
    'bim:grid':ric('<path d="M4 4v16M12 4v16M20 4v16M4 4h16M4 12h16M4 20h16"/>'),
    'bim:tagroom':ric('<path d="M4 4h9l7 7-9 9-7-7z"/><circle cx="9" cy="9" r="1.6"/>'),
    'bim:tagallrooms':ric('<path d="M3 6h7l5 5-7 7-5-5z"/><path d="M11 4h5l5 5-5 5"/>'),   /* __acad3dV101 */
    'bim:tagcat':ric('<path d="M3 6h8l6 6-6 6H3z"/><path d="M17 6h4v12h-4"/>'),
    'bim:beam':ric('<rect x="2" y="10" width="20" height="4"/><path d="M2 10V7M22 10V7M2 14v3M22 14v3"/>'),
    'bim:truss':ric('<path d="M2 18h20L17 8H7z"/><path d="M7 8l5 10 5-10"/>'),
    'bim:brace':ric('<path d="M4 4v16M20 4v16"/><path d="M4 4l16 16"/>'),
    'bim:foundwall':ric('<rect x="3" y="14" width="18" height="6"/><rect x="7" y="5" width="10" height="9"/>'),
    'bim:foundslab':ric('<rect x="2" y="12" width="20" height="7"/><path d="M6 12V8M18 12V8"/>'),
    'bim:property':ric('<path d="M3 17L8 4l13 5-4 11z" stroke-dasharray="5 2 1.5 2"/>'),   /* __acad3dV103 */
    'bim:propshape':ric('<rect x="4" y="5" width="15" height="13" stroke-dasharray="5 2 1.5 2"/><path d="M8 11h7"/>'),
    'bim:map':ric('<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2z"/><path d="M9 4v14M15 6v14"/>'),   /* __acad3dV132 */
    'bim:findaddress':ric('<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>'),
    'bim:geoimport':ric('<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>'),
    exportgeojson:ric('<path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5"/><circle cx="12" cy="15" r="3.6"/><path d="M8.4 15h7.2M12 11.4c1.2 1.2 1.2 6 0 7.2"/>'),
    'bim:datalayers':ric('<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12l9 5 9-5"/><path d="M3 16l9 5 9-5"/>'),   /* __acad3dV134 */
    'bim:context':ric('<path d="M3 21h18"/><rect x="4" y="11" width="5" height="10"/><rect x="10" y="5" width="6" height="16"/><rect x="17" y="13" width="4" height="8"/><path d="M12 9h2M12 13h2"/>'),   /* __acad3dV133 */
    'bim:usage':ric('<rect x="5" y="4" width="14" height="5" rx="1"/><rect x="5" y="10" width="14" height="5" rx="1"/><rect x="5" y="16" width="14" height="4" rx="1"/><path d="M8 6.5h4M8 12.5h7"/>'),   /* __acad3dV131 */
    'bim:usages':ric('<rect x="4" y="4" width="5" height="5" rx="1"/><path d="M12 6.5h8"/><rect x="4" y="10" width="5" height="5" rx="1"/><path d="M12 12.5h8"/><rect x="4" y="16" width="5" height="4" rx="1"/><path d="M12 18h8"/>'),
    'bim:alignment':ric('<path d="M3 19c5 0 5-7 9-7s4-7 9-7" stroke-dasharray="6 2 1.5 2"/><path d="M6 17.5l1 2M11 13l1.6 1.4M16 7.2l.6 1.8"/>'),   /* __acad3dV127 */
    'bim:truenorth':ric('<circle cx="12" cy="12" r="8"/><path d="M12 5l3 9-3-2-3 2z"/>'),
    'bim:analyze':ric('<path d="M3 20h18"/><path d="M6 20V9M18 20V9M4 9h16"/><path d="M8 13q4 5 8 0" stroke-dasharray="2 2"/>'),   /* __acad3dV125 */
    'bim:footing':ric('<rect x="4" y="15" width="16" height="5"/><rect x="10" y="4" width="4" height="11"/>'),   /* __acad3dV102 */
    'bim:rebar':ric('<path d="M4 8h16M4 16h16"/><path d="M8 4v16M16 4v16"/>'),
    'bim:linkifc':ric('<path d="M10 13a4 4 0 0 0 6 .6l2-2a4 4 0 0 0-5.6-5.6l-1 1"/><path d="M14 11a4 4 0 0 0-6-.6l-2 2a4 4 0 0 0 5.6 5.6l1-1"/>'),
    'bim:linkcad':ric('<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M7 15l4-6 3 4 2-2 2 4"/>'),
    'bim:importcad':ric('<path d="M4 15v4h16v-4"/><path d="M12 4v10M8 10l4 4 4-4"/><rect x="3" y="2" width="18" height="3"/>'),
    'bim:saveview':ric('<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M8 5v6h8V5"/><circle cx="12" cy="15" r="2"/>'),
    'bim:sheet':ric('<rect x="4" y="3" width="16" height="18"/><path d="M7 7h10M7 11h10M14 15h3M14 18h3"/>'),
    'bim:titleblock':ric('<rect x="3" y="4" width="18" height="16"/><path d="M3 15h18M14 15v5M3 15V4"/>'),
    'bim:uipanels':ric('<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M9 4v16M3 9h6"/>'),
    'bim:trim':ric('<circle cx="6" cy="6" r="2.4"/><circle cx="6" cy="18" r="2.4"/><path d="M8 7.5L20 17M8 16.5L20 7"/>'),
    'bim:offset':ric('<rect x="3" y="6" width="12" height="12"/><path d="M8 3h13v13" stroke-dasharray="3 2"/>'),
    'bim:align':ric('<path d="M3 3v18"/><rect x="7" y="5" width="9" height="4"/><rect x="7" y="14" width="13" height="4"/>'),
    'bim:layers':ric('<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>'),
    'bim:units':ric('<path d="M3 9h18M3 15h18"/><path d="M7 9V6M12 9V5M17 9V6"/>'),
    'bim:classification':ric('<path d="M4 4h7v7H4z"/><path d="M13 4h7v7h-7z"/><path d="M4 13h7v7H4z"/><path d="M13 13h7v7h-7z"/>'),
    'bim:mergewalls':ric('<path d="M4 6h8M4 18h8"/><path d="M12 6l8 6-8 6"/>'),
    'bim:checkmodel':ric('<path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/>'),
    'bim:clonelinked':ric('<rect x="4" y="4" width="10" height="10"/><rect x="11" y="11" width="10" height="10"/>'),
    'bim:syncclones':ric('<path d="M4 12a8 8 0 0 1 14-5"/><path d="M20 12a8 8 0 0 1-14 5"/><path d="M18 3v5h-5"/><path d="M6 21v-5h5"/>'),
    'bim:projinfo':ric('<circle cx="12" cy="12" r="9"/><path d="M12 11v6"/><circle cx="12" cy="7.5" r="1"/>'),
    'bim:purge':ric('<path d="M5 7h14M9 7V5h6v2M8 7l1 13h6l1-13"/><path d="M10 11v6M14 11v6"/>'),
    'bim:ceiling':ric('<path d="M3 7h18"/><path d="M6 7v4M10 7v4M14 7v4M18 7v4"/><path d="M3 4h18"/>'),
    saveproj:ric('<path d="M5 4h11l3 3v13H5z"/><path d="M8 4v6h7V4"/><rect x="8" y="13" width="8" height="7"/>'),
    openproj:ric('<path d="M3 7h6l2 2h10v10H3z"/>'),
    exportdxf:ric('<path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5"/><path d="M9 12l6 6M15 12l-6 6"/>'),
    exportsvg:ric('<path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5"/><path d="M8 17c1.5-5 5-4.5 6-9"/><circle cx="8" cy="17" r="1.1"/><circle cx="14" cy="8" r="1.1"/>'),
    'bim:section':ric('<path d="M4 4v16M4 4l16 4M4 20l16-4"/><path d="M15 6l4 12"/>'),
    exitsection:ric('<path d="M6 18L18 6M6 6l12 12"/>'),
    flipsection:ric('<path d="M4 12h16"/><path d="M15 7l5 5-5 5M9 7L4 12l5 5"/>'),
    'bim:mirror':ric('<path d="M12 3v18" stroke-dasharray="3 2"/><path d="M4 6l5 6-5 6M20 6l-5 6 5 6"/>'),
    'bim:rotate':ric('<path d="M4 12a8 8 0 1 1 3 6.2"/><path d="M3 15l1 4 4-1"/>'),
    'bim:polararray':ric('<circle cx="12" cy="12" r="1.6"/><circle cx="12" cy="4" r="1.6"/><circle cx="18.9" cy="8" r="1.6"/><circle cx="18.9" cy="16" r="1.6"/><circle cx="12" cy="20" r="1.6"/><circle cx="5.1" cy="16" r="1.6"/><circle cx="5.1" cy="8" r="1.6"/>'),
    'bim:joinwalls':ric('<path d="M4 4v9a7 7 0 0 0 7 7h9"/><path d="M14 17l6 3M20 20l-3-6"/>'),
    'bim:extend':ric('<path d="M3 12h11"/><path d="M11 8l4 4-4 4"/><path d="M19 4v16"/>'),
    'bim:arc':ric('<path d="M4 19a15 15 0 0 1 16-14"/><circle cx="4" cy="19" r="1.4"/><circle cx="20" cy="5" r="1.4"/>'),
    'bim:fillet':ric('<path d="M4 20V10a6 6 0 0 1 6-6h10"/>'),
    'bim:chamfer':ric('<path d="M4 20v-8l8-8h8"/>'),
    'bim:break':ric('<path d="M3 12h6M15 12h6"/><path d="M11 7l-2 10M13 7l-2 10"/>'),
    'bim:lengthen':ric('<path d="M3 12h14"/><path d="M13 8l4 4-4 4"/><path d="M3 7v10"/>'),
    'bim:scale':ric('<rect x="3" y="12" width="9" height="9"/><path d="M12 12L21 3"/><path d="M15 3h6v6"/>'),
    'bim:presspull':ric('<path d="M4 15l8-4 8 4-8 4z"/><path d="M4 15v3l8 4 8-4v-3"/><path d="M12 11V2M9 5l3-3 3 3"/>'),   /* __acad3dV123 */
    exportpng:ric('<rect x="3" y="3" width="18" height="14" rx="1"/><path d="M3 13l5-5 4 4 4-4 5 5"/><circle cx="8" cy="8" r="1.5"/>'),
    exportpdf:ric('<path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5"/><path d="M8.5 13.5h1.2c.7 0 1.3.6 1.3 1.3s-.6 1.3-1.3 1.3H8.5v-2.6z"/>')
  };

