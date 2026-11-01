  /* ================= __acad3dV122: Present -- the pages full screen, one at a time =================
     For a client. The pages in the project's order, each drawn as it plots, fitted to the screen on
     black. Named the slideshow in the code: "presentation" there already means the Presentation
     appearance (A3D.presentMode). */
  var A3D_SLIDESHOW={on:false,idx:0,el:null,cv:null,from:null,fs:false,idleT:null,wheelAt:0,ahead:null,msg:'',scale:0};
  var BIM_SHOW_IDLE_MS=2500,BIM_SHOW_WHEEL_MS=350;
  var A3D_SHOW_KEYS=[
    {act:'next',keys:['ArrowRight','ArrowDown','PageDown',' ','Enter','n','N'],say:['Right','Down','Page Down','Space','Enter','N'],label:'Next page'},
    {act:'prev',keys:['ArrowLeft','ArrowUp','PageUp','Backspace','p','P'],say:['Left','Up','Page Up','Backspace','P'],label:'Previous page'},
    {act:'first',keys:['Home'],say:['Home'],label:'First page'},
    {act:'last',keys:['End'],say:['End'],label:'Last page'},
    {act:'end',keys:['Escape'],say:['Esc'],label:'End the presentation'}
  ];
  function bimShowSay(act,n){
    var i;
    for(i=0;i<A3D_SHOW_KEYS.length;i++)if(A3D_SHOW_KEYS[i].act===act)return A3D_SHOW_KEYS[i].say.slice(0,n||99).join(', ');
    return '';
  }
  function bimSlideshowHint(){
    return bimShowSay('next',4)+' or a click for the next page; '+bimShowSay('prev',3)+' for the one before; '+bimShowSay('end',1)+' to end';
  }
  function bimSlideshowEl(){
    if(A3D_SLIDESHOW.el&&document.body.contains(A3D_SLIDESHOW.el))return A3D_SLIDESHOW.el;
    var ov=document.createElement('div');
    ov.id='a3d-slideshow';ov.className='a3d-slideshow';
    ov.setAttribute('role','dialog');ov.setAttribute('aria-label','Presentation');
    ov.innerHTML='<canvas class="a3d-sscv"></canvas>'+
      '<div class="a3d-sshint"></div>'+
      '<div class="a3d-ssbar">'+
        '<button type="button" data-ssact="prev" title="Previous page" aria-label="Previous page">\u2039</button>'+
        '<span class="a3d-sspos">1 / 1</span>'+
        '<button type="button" data-ssact="next" title="Next page" aria-label="Next page">\u203a</button>'+
        '<button type="button" data-ssact="end" title="End the presentation (Esc)" aria-label="End the presentation">End</button>'+
      '</div>';
    document.body.appendChild(ov);
    A3D_SLIDESHOW.el=ov;A3D_SLIDESHOW.cv=ov.querySelector('.a3d-sscv');
    ov.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-ssact]'):null;
      try{
        if(b){if(!b.disabled)bimSlideshowAct(b.getAttribute('data-ssact'));}
        else if(!(ev.target.closest&&ev.target.closest('.a3d-ssbar')))bimSlideshowAct('next');
      }catch(eC){console.warn('[BIM] A presentation step failed',eC);a3dToast('That step failed -- see the console');}
    });
    ov.addEventListener('wheel',function(ev){
      var bd=ev.target&&ev.target.closest?ev.target.closest('.a3d-ssboard'):null;   /* __acad3dV162: a board scrolls, to its end */
      if(bd&&ev.deltaY&&(ev.deltaY>0?bd.scrollTop+bd.clientHeight<bd.scrollHeight-1:bd.scrollTop>0))return;
      ev.preventDefault();
      var now=Date.now();
      if(now-A3D_SLIDESHOW.wheelAt<BIM_SHOW_WHEEL_MS||!ev.deltaY)return;
      A3D_SLIDESHOW.wheelAt=now;
      bimSlideshowAct(ev.deltaY>0?'next':'prev');
    },{passive:false});
    ov.addEventListener('mousemove',bimSlideshowWake);
    ov.addEventListener('contextmenu',function(ev){ev.preventDefault();});   /* no browser menu over a client's page */
    return ov;
  }
  /* the controls and the cursor show while the mouse moves, and go when it rests */
  function bimSlideshowWake(){
    var ov=A3D_SLIDESHOW.el;
    if(!ov||!A3D_SLIDESHOW.on)return;
    ov.classList.remove('idle');
    if(A3D_SLIDESHOW.idleT)clearTimeout(A3D_SLIDESHOW.idleT);
    A3D_SLIDESHOW.idleT=setTimeout(function(){A3D_SLIDESHOW.idleT=null;if(A3D_SLIDESHOW.on)ov.classList.add('idle');},BIM_SHOW_IDLE_MS);
  }
  function bimSlideshowStart(fromId){
    if(A3D_SLIDESHOW.on)return true;
    var Q=bimPresSeq(),idx=0,i,ov;   /* __acad3dV162: the set, boards and all */
    if(!Q.length){a3dToast('There are no pages to present yet: every sheet is a page');return false;}
    for(i=0;i<Q.length;i++)if(Q[i].id===fromId){idx=i;break;}
    try{ov=bimSlideshowEl();}
    catch(eE){console.warn('[BIM] The presentation could not be set up',eE);a3dToast('The presentation could not start -- see the console');return false;}
    A3D_SLIDESHOW.on=true;A3D_SLIDESHOW.idx=idx;A3D_SLIDESHOW.ahead=null;A3D_SLIDESHOW.msg='';
    A3D_SLIDESHOW.from={kind:A3D_VIEW.kind,id:A3D_VIEW.id,board:A3D_CLB.open?A3D_CLB.kind:null};
    if(A3D_CLB.open)bimClbClose();   /* one board on the screen: Present's */
    ov.classList.add('open');
    bimSlideshowFullscreen(ov);
    bimSlideshowShow();
    bimSlideshowWake();
    return true;
  }
  function bimSlideshowFullscreen(ov){
    A3D_SLIDESHOW.fs=false;
    var rq=ov.requestFullscreen||ov.webkitRequestFullscreen,p;
    if(!rq){bimSlideshowNoFs(null);return;}
    try{
      p=rq.call(ov);
      if(p&&typeof p.then==='function')p.then(function(){if(A3D_SLIDESHOW.on){A3D_SLIDESHOW.fs=true;bimSlideshowShow();}},bimSlideshowNoFs);
      else A3D_SLIDESHOW.fs=true;
    }catch(eF){bimSlideshowNoFs(eF);}
  }
  function bimSlideshowNoFs(e){
    if(!A3D_SLIDESHOW.on)return;
    console.warn('[BIM] Full screen was not granted; the presentation fills the window instead',e);
    A3D_SLIDESHOW.msg='Full screen was not allowed here, so the pages fill the window. ';
    a3dToast('Full screen was not allowed here, so the presentation fills the window');
    bimSlideshowBar();
  }
  function bimSlideshowBar(){
    var ov=A3D_SLIDESHOW.el,n=bimPresSeq().length,i=A3D_SLIDESHOW.idx;
    if(!ov)return;
    ov.querySelector('.a3d-sspos').textContent=(i+1)+' / '+n;
    ov.querySelector('[data-ssact="prev"]').disabled=(i<=0);
    ov.querySelector('[data-ssact="next"]').disabled=(i>=n-1);
    ov.querySelector('.a3d-sshint').textContent=A3D_SLIDESHOW.msg+bimSlideshowHint();
  }
  /* the page on screen: fitted with a small margin, drawn for this screen, the next one drawn ahead */
  function bimSlideshowShow(){
    if(!A3D_SLIDESHOW.on)return;
    var Q=bimPresSeq(),n=Q.length;
    if(!n){bimSlideshowEnd();return;}
    if(A3D_SLIDESHOW.idx>n-1)A3D_SLIDESHOW.idx=n-1;
    var e=Q[A3D_SLIDESHOW.idx];
    if(e.t==='board'){bimSlideshowBoard(e);bimSlideshowBar();bimSlideshowAhead(A3D_SLIDESHOW.idx+1);return;}   /* __acad3dV162 */
    bimSlideshowBoard(null);
    var s=e.s,ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv;
    var vw=ov.clientWidth||window.innerWidth,vh=ov.clientHeight||window.innerHeight,m=Math.round(Math.min(vw,vh)*0.03);
    var k=Math.max(0.05,Math.min((vw-2*m)/s.w,(vh-2*m)/s.h));
    var W=Math.max(1,Math.round(s.w*k)),H=Math.max(1,Math.round(s.h*k)),sc=bimPageScaleFor(s,W);
    var key=bimPageSig(s)+'|'+sc.toFixed(5),a=A3D_SLIDESHOW.ahead;
    cv.style.width=W+'px';cv.style.height=H+'px';
    try{
      if(a&&a.id===s.id&&a.key===key){
        cv.width=a.cv.width;cv.height=a.cv.height;
        cv.getContext('2d').drawImage(a.cv,0,0);
      }else bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,cv,sc);
    }catch(eS){
      console.warn('[BIM] Page '+(A3D_SLIDESHOW.idx+1)+' could not be drawn for the presentation',eS);
      a3dToast('Page '+(A3D_SLIDESHOW.idx+1)+' could not be drawn -- see the console');
    }
    cv.setAttribute('data-sspage',s.id);cv.setAttribute('data-sskey',key);
    A3D_SLIDESHOW.scale=sc;
    bimSlideshowBar();
    bimSlideshowAhead(A3D_SLIDESHOW.idx+1);
  }
  /* __acad3dV162: a board's page in Present: the board as on screen, over the black, scrolled with the
     wheel or a finger; the canvas stands aside */
  function bimSlideshowBoard(e){
    var ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv,bd=ov?ov.querySelector('.a3d-ssboard'):null,w,sig;
    if(!ov)return;
    if(!e){if(bd)bd.parentNode.removeChild(bd);cv.style.display='';return;}
    cv.style.display='none';
    cv.setAttribute('data-sspage',e.id);cv.removeAttribute('data-sskey');
    if(!bd){bd=document.createElement('div');bd.setAttribute('role','document');ov.insertBefore(bd,cv.nextSibling);bimClbWire(bd);}
    w=ov.clientWidth||window.innerWidth;
    bd.className='a3d-clb a3d-ssboard'+bimClbWidthCls(w);
    bd.setAttribute('data-sspage',e.id);
    bd.setAttribute('aria-label',bimBoardLabel(e.b)+' board');
    sig=e.b.id+'|'+A3D_REV+'|'+(w<760);   /* __acad3dV172b: a board of one's own by its id */
    if(bd.getAttribute('data-sssig')!==sig){
      bd.innerHTML=bimBoardHtmlFor(bimBoardKey(e.b),w<760)+'<div class="a3d-clb-tip" role="tooltip" hidden></div>';
      bd.setAttribute('data-sssig',sig);bd.scrollTop=0;
    }
    bimBrdZoom(bd);   /* __acad3dV172b */
    A3D_SLIDESHOW.scale=0;
  }
  function bimSlideshowAhead(i){
    setTimeout(function(){
      var Q=bimPresSeq();
      if(!A3D_SLIDESHOW.on||i>=Q.length||Q[i].t!=='sheet')return;   /* __acad3dV162: a board is not drawn ahead */
      var s=Q[i].s,ov=A3D_SLIDESHOW.el,vw=ov.clientWidth||window.innerWidth,vh=ov.clientHeight||window.innerHeight;
      var m=Math.round(Math.min(vw,vh)*0.03),k=Math.max(0.05,Math.min((vw-2*m)/s.w,(vh-2*m)/s.h));
      var W=Math.max(1,Math.round(s.w*k)),sc=bimPageScaleFor(s,W),key=bimPageSig(s)+'|'+sc.toFixed(5);
      if(A3D_SLIDESHOW.ahead&&A3D_SLIDESHOW.ahead.id===s.id&&A3D_SLIDESHOW.ahead.key===key)return;
      try{
        var c=document.createElement('canvas');
        bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,c,sc);
        A3D_SLIDESHOW.ahead={id:s.id,key:key,cv:c};
      }catch(eA){console.warn('[BIM] The next page could not be drawn ahead; it will be drawn when it is shown',eA);}
    },60);
  }
  function bimSlideshowGo(i){
    if(!A3D_SLIDESHOW.on)return false;
    var n=bimPresSeq().length;
    i=Math.max(0,Math.min(n-1,i));
    if(i!==A3D_SLIDESHOW.idx){A3D_SLIDESHOW.idx=i;bimSlideshowShow();}
    else bimSlideshowBar();
    return true;
  }
  function bimSlideshowAct(act){
    var i=A3D_SLIDESHOW.idx;
    if(act==='next')return bimSlideshowGo(i+1);
    if(act==='prev')return bimSlideshowGo(i-1);
    if(act==='first')return bimSlideshowGo(0);
    if(act==='last')return bimSlideshowGo(bimPresSeq().length-1);
    if(act==='end')return bimSlideshowEnd();
    return false;
  }
  function bimSlideshowKey(ev){
    var act=null,i;
    for(i=0;i<A3D_SHOW_KEYS.length;i++)if(A3D_SHOW_KEYS[i].keys.indexOf(ev.key)>=0){act=A3D_SHOW_KEYS[i].act;break;}
    ev.stopImmediatePropagation();
    /* the browser keeps its chords and function keys -- full screen, the developer tools */
    if(ev.ctrlKey||ev.metaKey||ev.altKey||/^F\d+$/.test(ev.key))return true;
    ev.preventDefault();
    if(act)bimSlideshowAct(act);
    return true;
  }
  /* back where it was started; on paper, to the page last shown */
  function bimSlideshowEnd(){
    if(!A3D_SLIDESHOW.on)return false;
    var e=bimPresSeq()[A3D_SLIDESHOW.idx]||null,s=e&&e.t==='sheet'?e.s:null,from=A3D_SLIDESHOW.from||{},ov=A3D_SLIDESHOW.el;
    bimSlideshowBoard(null);
    A3D_SLIDESHOW.on=false;A3D_SLIDESHOW.ahead=null;
    if(A3D_SLIDESHOW.idleT){clearTimeout(A3D_SLIDESHOW.idleT);A3D_SLIDESHOW.idleT=null;}
    if(ov)ov.classList.remove('open','idle');
    var fsEl=document.fullscreenElement||document.webkitFullscreenElement;
    if(A3D_SLIDESHOW.fs&&fsEl){
      try{var x=(document.exitFullscreen||document.webkitExitFullscreen).call(document);if(x&&x.catch)x.catch(function(eX){console.warn('[BIM] Full screen could not be left',eX);});}
      catch(eX){console.warn('[BIM] Full screen could not be left',eX);a3dToast('Full screen could not be left -- press Esc');}
    }
    A3D_SLIDESHOW.fs=false;
    if(e&&e.t==='board'){bimClbOpen(bimBoardKey(e.b));return true;}   /* __acad3dV162: back on the board last shown */
    if(s&&from.board){bimActivateView('sheet',s.id);return true;}   /* started on a board: to the sheet last shown */
    if(s&&from.kind==='sheet'&&bimSheetOnScreen()){
      if(A3D_PAGES.display==='pages'){if(s.id!==A3D.activeSheetId)bimPagesSetCurrent(s.id);bimPagesScrollTo(s.id);}
      else if(s.id!==A3D.activeSheetId)bimActivateView('sheet',s.id);
    }
    return true;
  }
  /* the browser's own Esc leaves full screen without a key reaching the page: that ends it too */
  function bimSlideshowFsChange(){
    var fsEl=document.fullscreenElement||document.webkitFullscreenElement;
    if(!A3D_SLIDESHOW.on)return;
    if(A3D_SLIDESHOW.fs&&!fsEl){A3D_SLIDESHOW.fs=false;bimSlideshowEnd();return;}
    bimSlideshowShow();
  }
  document.addEventListener('fullscreenchange',bimSlideshowFsChange);
  document.addEventListener('webkitfullscreenchange',bimSlideshowFsChange);
  window.addEventListener('resize',function(){if(A3D_SLIDESHOW.on)bimSlideshowShow();});
  function bimOpenSheetView(id){
    var sheet=bimSheetById(id);
    if(!sheet){a3dToast('Sheet not found');return;}
    A3D.activeSheetId=id;A3D.sheetSelVp=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */
    if(el.sheetview)el.sheetview.classList.add('open');
    refreshBrowser();bimSheetViewRefresh();
    if(A3D_PAGES.display==='pages')bimPagesScrollTo(id);   /* __acad3dV122: the sheet opened is the page shown */
  }
  /* __acad3dV116: the Model tab. Back to the view the sheet was opened from, with its camera; a view
     that no longer exists falls back to the plan of the active level. */
  function bimSheetOnScreen(){return !!(el.sheetview&&el.sheetview.classList.contains('open'));}
  function bimShowModel(){
    if(A3D_VIEW.kind!=='sheet'&&!bimSheetOnScreen())return true;
    var m=A3D_LAST_MODEL_VIEW||{kind:'plan',id:A3D.activeLevel,cam:null};
    var ok=bimActivateView(m.kind,m.id,{anim:false});
    if(!ok)ok=bimActivateView('plan',A3D.activeLevel,{anim:false});
    if(ok&&m.cam){
      A3D.cam={yaw:m.cam.yaw,pitch:m.cam.pitch,dist:m.cam.dist,tx:m.cam.tx,ty:m.cam.ty,tz:m.cam.tz};
      paint();
    }
    return ok;
  }
  function bimCloseSheetView(){
    if(el.sheetview)el.sheetview.classList.remove('open');
    A3D.sheetSelVp=null;A3D.sheetDrag=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */
    bimRenderLayoutTabs();
  }
  function bimSheetEvtToMM(ev,cv){
    var t=(ev.touches&&ev.touches.length)?ev.touches[0]:((ev.changedTouches&&ev.changedTouches.length)?ev.changedTouches[0]:ev);
    var rect=cv.getBoundingClientRect();
    var scaleX=cv.width/rect.width,scaleY=cv.height/rect.height;
    var cx=(t.clientX-rect.left)*scaleX,cy=(t.clientY-rect.top)*scaleY;
    return [cx/SHEET_PREVIEW_PXMM,cy/SHEET_PREVIEW_PXMM];
  }
  function bimSheetHitTest(sheet,mm){
    var i;
    for(i=sheet.viewports.length-1;i>=0;i--){
      var vp=sheet.viewports[i];
      var hx=vp.x+vp.w,hy=vp.y+vp.h;
      if(Math.abs(mm[0]-hx)<4&&Math.abs(mm[1]-hy)<4)return {vp:vp,handle:true};
      if(mm[0]>=vp.x&&mm[0]<=vp.x+vp.w&&mm[1]>=vp.y&&mm[1]<=vp.y+vp.h)return {vp:vp,handle:false};
    }
    return null;
  }
