  /* ================= __acad3dV122: the Pages display =================
     The sheet view's second display: every sheet in the project's order, one under the next in one
     scroll, read-only, each drawn as it plots. The view is still a sheet -- the page being read --
     and it follows the scroll. */
  var A3D_PAGES={display:'layout',zoom:'width',els:{},pxmm:0,timer:null,raf:0,heldTop:-1,staleT:null};
  var A3D_PAGE_ZOOMS=[{v:'width',label:'Fit width'},{v:'page',label:'Fit page'},{v:50,label:'50%'},{v:75,label:'75%'},
    {v:100,label:'100%'},{v:125,label:'125%'},{v:150,label:'150%'},{v:200,label:'200%'}];
  var BIM_PX_PER_MM_100=96/25.4;   /* 100 percent: the paper at its own size, 96 screen pixels to the inch */
  var BIM_PAGE_GAP=18;             /* around the pages and between them, as the stylesheet has it */
  var BIM_PAGE_MAX_PX=8192;        /* the longest side of a page's pixels; past it a canvas may refuse */
  /* The keys of the Pages display. The handler reads this table, and so do the status bar's hint and
     the shortcut sheet: one list, so the three cannot disagree (V86). `say` is what a person reads. */
  var A3D_PAGEVIEW_KEYS=[
    {act:'next',keys:['PageDown','ArrowRight'],say:['Page Down','Right'],label:'Next page'},
    {act:'prev',keys:['PageUp','ArrowLeft'],say:['Page Up','Left'],label:'Previous page'},
    {act:'first',keys:['Home'],say:['Home'],label:'First page'},
    {act:'last',keys:['End'],say:['End'],label:'Last page'},
    {act:'down',keys:['ArrowDown'],say:['Down'],label:'Scroll down'},
    {act:'up',keys:['ArrowUp'],say:['Up'],label:'Scroll up'}
  ];
  function bimPageKeyAct(key){
    var i;
    for(i=0;i<A3D_PAGEVIEW_KEYS.length;i++)if(A3D_PAGEVIEW_KEYS[i].keys.indexOf(key)>=0)return A3D_PAGEVIEW_KEYS[i].act;
    return null;
  }
  function bimPageKeyWords(act){
    var i;
    for(i=0;i<A3D_PAGEVIEW_KEYS.length;i++)if(A3D_PAGEVIEW_KEYS[i].act===act)return A3D_PAGEVIEW_KEYS[i].say.join(' / ');
    return '';
  }
  function bimPagesKeyDo(act){
    var i=bimPagesIndex();
    if(act==='next')return bimPagesGo(i+1);
    if(act==='prev')return bimPagesGo(i-1);
    if(act==='first')return bimPagesGo(0);
    if(act==='last')return bimPagesGo(A3D.sheets.length-1);
    if(el.pageswrap&&(act==='down'||act==='up')){el.pageswrap.scrollTop+=(act==='down'?60:-60);return true;}
    return false;
  }
  function bimPagesOn(){return A3D_PAGES.display==='pages'&&bimSheetOnScreen();}
  function bimPagesIndex(){
    var i;
    for(i=0;i<A3D.sheets.length;i++)if(A3D.sheets[i].id===A3D.activeSheetId)return i;
    return 0;
  }
  function bimPageZoomOptionsHtml(){
    var h='',i;
    for(i=0;i<A3D_PAGE_ZOOMS.length;i++)
      h+='<option value="'+A3D_PAGE_ZOOMS[i].v+'">'+bimEsc(A3D_PAGE_ZOOMS[i].label)+'</option>';
    return h;
  }
  /* The one display switch. Pages leaves model space in a viewport and any viewport selected: the
     pages are read, not edited. */
  function bimPagesSetDisplay(d){
    d=(d==='pages')?'pages':'layout';
    var was=A3D_PAGES.display;
    A3D_PAGES.display=d;
    if(d==='pages'){A3D.sheetSelVp=null;A3D.sheetActiveVp=null;A3D.sheetDrag=null;}
    if(el.sheetview)el.sheetview.classList.toggle('a3d-pagesmode',d==='pages');
    bimPagesSyncBar();
    bimSheetViewRefresh();
    if(d==='pages'&&was!=='pages')bimPagesScrollTo(A3D.activeSheetId);
    bimSyncStatusHint();
    return d;
  }
  /* pixels per paper millimetre on screen: fit width fits the widest sheet, fit page the largest one
     whole, a percentage is of the paper's own size -- one scale for every page, so a smaller sheet
     reads smaller, as it is */
  function bimPagesPxPerMM(){
    var z=A3D_PAGES.zoom,wrap=el.pageswrap,mw=0,mh=0,i;
    if(typeof z==='number')return z/100*BIM_PX_PER_MM_100;
    for(i=0;i<A3D.sheets.length;i++){mw=Math.max(mw,A3D.sheets[i].w);mh=Math.max(mh,A3D.sheets[i].h);}
    if(!wrap||!mw||!mh)return SHEET_PREVIEW_PXMM;
    var k=Math.max(40,wrap.clientWidth-2*BIM_PAGE_GAP)/mw;
    if(z==='page')k=Math.min(k,Math.max(40,wrap.clientHeight-2*BIM_PAGE_GAP)/mh);
    return Math.max(0.2,k);
  }
  /* What a page's drawing depends on. The model's revision moves with every change; the appearance
     is changed without one; the sheet, the title block and the project's name are small. */
  function bimPageSig(s){
    return A3D_REV+'|'+(A3D.presentMode?'P':'T')+'|'+JSON.stringify(s)+'|'+JSON.stringify(A3D.titleBlock||{})+'|'+bimProjectLabel();
  }
  /* the scale a page is drawn at to fill cssW screen pixels on this screen (V122a) */
  function bimPageScaleFor(s,cssW){
    var d=cssW*bimDevicePixelRatio()/(s.w*SHEET_PREVIEW_PXMM);
    return Math.max(0.05,Math.min(d,BIM_PAGE_MAX_PX/(Math.max(s.w,s.h)*SHEET_PREVIEW_PXMM)));
  }
  function bimPagesLayout(){
    var col=el.pagescol,k=bimPagesPxPerMM(),seen={},i,s,e,id,W,H;
    if(!col)return;
    A3D_PAGES.pxmm=k;
    for(i=0;i<A3D.sheets.length;i++){
      s=A3D.sheets[i];seen[s.id]=1;
      e=A3D_PAGES.els[s.id];
      if(!e){
        var box=document.createElement('div');
        box.className='a3d-page';box.setAttribute('data-page',s.id);
        var cv=document.createElement('canvas');
        box.appendChild(cv);
        e=A3D_PAGES.els[s.id]={box:box,cv:cv,key:''};
      }
      W=Math.max(1,Math.round(s.w*k));H=Math.max(1,Math.round(s.h*k));
      e.box.style.width=W+'px';e.box.style.height=H+'px';
      e.box.title='Page '+(i+1)+': '+bimSheetLabel(s)+' -- double-click to edit its layout';
      e.scale=bimPageScaleFor(s,W);
      if(col.children[i]!==e.box)col.insertBefore(e.box,col.children[i]||null);
    }
    for(id in A3D_PAGES.els){
      if(!A3D_PAGES.els.hasOwnProperty(id)||seen[id])continue;
      e=A3D_PAGES.els[id];
      if(e.box.parentNode)e.box.parentNode.removeChild(e.box);
      delete A3D_PAGES.els[id];
    }
  }
  function bimPageKey(s,e){return bimPageSig(s)+'|'+e.scale.toFixed(5);}
  function bimPagesRefresh(){
    if(!el.pagescol||!bimPagesOn())return false;
    bimPagesLayout();
    bimPagesSyncBar();
    bimPagesQueue();
    return true;
  }
  function bimPagesQueue(){
    if(!A3D_PAGES.timer)A3D_PAGES.timer=setTimeout(bimPagesDrawNext,0);
  }
  /* One page per turn of the event loop, the one nearest the middle of the screen first, and only
     pages on the screen or within a screen of it. */
  function bimPagesDrawNext(){
    A3D_PAGES.timer=null;
    if(!bimPagesOn()||!el.pageswrap)return;
    var wr=el.pageswrap.getBoundingClientRect(),mid=(wr.top+wr.bottom)/2,reach=wr.height,best=null,bd=1e18,i,s,e,r,d;
    for(i=0;i<A3D.sheets.length;i++){
      s=A3D.sheets[i];e=A3D_PAGES.els[s.id];
      if(!e)continue;
      r=e.box.getBoundingClientRect();
      if(r.bottom<wr.top-reach||r.top>wr.bottom+reach)continue;
      if(e.key===bimPageKey(s,e))continue;
      d=Math.abs((r.top+r.bottom)/2-mid);
      if(d<bd){bd=d;best={s:s,e:e,n:i+1};}
    }
    if(!best)return;
    bimPageDraw(best.s,best.e,best.n);
    A3D_PAGES.timer=setTimeout(bimPagesDrawNext,0);
  }
  function bimPageDraw(s,e,n){
    var key=bimPageKey(s,e);
    try{bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,e.cv,e.scale);}
    catch(eP){
      console.warn('[BIM] Page '+n+' could not be drawn',eP);
      a3dToast('Page '+n+' could not be drawn -- see the console');
    }
    e.key=key;   /* drawn or failed, not tried again until something changes */
  }
  /* the page the reader is on: the one with the most of itself on the screen, the earlier on a tie */
  function bimPagesMostVisible(){
    var wr=el.pageswrap.getBoundingClientRect(),best=null,bv=0,i,e,r,v;
    for(i=0;i<A3D.sheets.length;i++){
      e=A3D_PAGES.els[A3D.sheets[i].id];
      if(!e)continue;
      r=e.box.getBoundingClientRect();
      v=Math.min(r.bottom,wr.bottom)-Math.max(r.top,wr.top);
      if(v>bv){bv=v;best=A3D.sheets[i].id;}
    }
    return best;
  }
  function bimPagesSetCurrent(id){
    var s=bimSheetById(id);
    if(!s)return false;
    A3D.activeSheetId=id;
    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(s);
    bimSetActiveView('sheet',id,null);   /* the record, and the tab, browser, HUD and panel that read it */
    bimPagesSyncBar();
    return true;
  }
  function bimPagesOnScroll(){
    if(A3D_PAGES.raf)return;
    A3D_PAGES.raf=requestAnimationFrame(function(){
      A3D_PAGES.raf=0;
      if(!bimPagesOn())return;
      /* a page gone to by number stays current until the reader scrolls: the last page may be too
         short to come to the top, and the one above it would otherwise take its place */
      if(A3D_PAGES.heldTop>=0&&Math.abs(el.pageswrap.scrollTop-A3D_PAGES.heldTop)<2){bimPagesQueue();return;}
      A3D_PAGES.heldTop=-1;
      var id=bimPagesMostVisible();
      if(id&&id!==A3D.activeSheetId)bimPagesSetCurrent(id);
      bimPagesQueue();
    });
  }
  function bimPagesScrollTo(id){
    var e=A3D_PAGES.els[id],wrap=el.pageswrap;
    if(!e||!wrap||!bimPagesOn())return false;
    wrap.scrollTop=Math.max(0,e.box.offsetTop-BIM_PAGE_GAP);
    A3D_PAGES.heldTop=wrap.scrollTop;
    bimPagesQueue();
    return true;
  }
  /* to a page by its place, from 0 */
  function bimPagesGo(idx){
    var n=A3D.sheets.length;
    if(!n)return false;
    idx=Math.max(0,Math.min(n-1,idx));
    var id=A3D.sheets[idx].id;
    if(id!==A3D.activeSheetId)bimPagesSetCurrent(id);
    bimPagesScrollTo(id);
    bimPagesSyncBar();
    return true;
  }
  function bimPagesZoom(z){
    var i,ok=false;
    for(i=0;i<A3D_PAGE_ZOOMS.length;i++)if(String(A3D_PAGE_ZOOMS[i].v)===String(z)){z=A3D_PAGE_ZOOMS[i].v;ok=true;break;}
    if(!ok){
      console.warn('[BIM] Not a page zoom: '+z);
      a3dToast('That zoom is not one of the choices');
      bimPagesSyncBar();
      return false;
    }
    A3D_PAGES.zoom=z;
    bimPagesRefresh();
    bimPagesScrollTo(A3D.activeSheetId);
    return true;
  }
  function bimPagesSyncBar(){
    var n=A3D.sheets.length,i=bimPagesIndex(),b,j;
    if(el.pgnum&&document.activeElement!==el.pgnum)el.pgnum.value=String(n?i+1:0);
    if(el.pgof)el.pgof.textContent='of '+n;
    if(el.pgprev)el.pgprev.disabled=(i<=0);
    if(el.pgnext)el.pgnext.disabled=(i>=n-1);
    if(el.pgzoom)el.pgzoom.value=String(A3D_PAGES.zoom);
    b=el.sheetview?el.sheetview.querySelectorAll('[data-shdisp]'):[];
    for(j=0;j<b.length;j++)b[j].classList.toggle('on',b[j].getAttribute('data-shdisp')===A3D_PAGES.display);
  }
  function bimPagesTypedNumber(){
    var n=A3D.sheets.length,v=parseInt(String(el.pgnum.value).trim(),10);
    if(!isFinite(v)||v<1||v>n){
      a3dToast('The pages run from 1 to '+n);
      el.pgnum.value=String(bimPagesIndex()+1);
      return false;
    }
    return bimPagesGo(v-1);
  }
  /* a change to the model redraws the pages on screen, once, shortly after */
  function bimPagesStale(){
    if(!A3D_PAGES||A3D_PAGES.staleT)return;   /* saveSoon can run before this file has reached A3D_PAGES */
    A3D_PAGES.staleT=setTimeout(function(){
      A3D_PAGES.staleT=null;
      try{if(bimPagesOn())bimPagesQueue();bimPresThumbsQueue();}   /* __acad3dV122: and the thumbnails */
      catch(eS){console.warn('[BIM] The pages could not be brought up to date',eS);a3dToast('The pages could not be redrawn -- see the console');}
    },250);
  }
  function bimWirePages(){
    if(!el.sheetview||el.sheetview.__a3dPagesWired)return;
    el.sheetview.__a3dPagesWired=true;
    if(el.pgzoom)el.pgzoom.innerHTML=bimPageZoomOptionsHtml();
    el.sheetview.addEventListener('click',function(ev){
      var t=ev.target,b;
      if(!t||!t.closest)return;
      try{
        if((b=t.closest('[data-shdisp]'))){bimPagesSetDisplay(b.getAttribute('data-shdisp'));return;}
        if(t.closest('#a3d-pgprev')){bimPagesGo(bimPagesIndex()-1);return;}
        if(t.closest('#a3d-pgnext')){bimPagesGo(bimPagesIndex()+1);return;}
        if((b=t.closest('[data-page]'))&&b.getAttribute('data-page')!==A3D.activeSheetId)bimPagesSetCurrent(b.getAttribute('data-page'));
      }catch(eC){console.warn('[BIM] A Pages control failed',eC);a3dToast('That did not work -- see the console');}
    });
    el.sheetview.addEventListener('dblclick',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-page]'):null;
      if(!b)return;
      bimPagesSetCurrent(b.getAttribute('data-page'));
      bimPagesSetDisplay('layout');
    });
    if(el.pgzoom)el.pgzoom.addEventListener('change',function(){bimPagesZoom(el.pgzoom.value);});
    if(el.pgnum){
      el.pgnum.addEventListener('keydown',function(ev){
        if(ev.key==='Enter'){ev.preventDefault();bimPagesTypedNumber();el.pgnum.blur();}
        else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();el.pgnum.value=String(bimPagesIndex()+1);el.pgnum.blur();}
      });
      el.pgnum.addEventListener('change',function(){bimPagesTypedNumber();});
    }
    if(el.pageswrap){
      el.pageswrap.addEventListener('scroll',bimPagesOnScroll);
      /* a fitted zoom follows the space it fits: the window, and the panel opening or closing beside it */
      var refit=function(){if(bimPagesOn()&&typeof A3D_PAGES.zoom!=='number'){bimPagesRefresh();}};
      if(typeof ResizeObserver!=='undefined'){try{new ResizeObserver(refit).observe(el.pageswrap);}catch(eR){console.warn('[BIM] The pages cannot follow the window size',eR);window.addEventListener('resize',refit);}}
      else window.addEventListener('resize',refit);
    }
  }
