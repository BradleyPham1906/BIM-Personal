"""patch_phase122c.py -- V122: the sheet view's Pages display, every sheet in one scroll like a PDF.

The owner: "Need a presentation for doing presentation with clients. using layout spaces, with multi
pages view like a pdf viewer." The layout spaces are V116's sheets; this is the multi-page view.

The sheet view has two displays now, switched at the left of its toolbar. Layout is the sheet alone,
to edit -- AutoCAD's layout tab, as it was. Pages is every sheet, in the project's order, one under
the next in one scroll, the way a PDF reader shows a document:

  - each page drawn as it plots (V121: no no-plot layer, no lock fade; V122b: in the appearance it
    prints in), at a resolution for the screen it is on (V122a: the same page at any size);
  - "Page n of N", previous and next, a page number typed to jump, and the zoom a reader expects:
    fit width, fit page, and 50 to 200 percent of the paper's own size;
  - Page Up / Page Down, Home / End and the arrows, from one table the status bar's hint and the
    shortcut sheet are both drawn from;
  - a click makes a page current, a double-click opens its layout to edit.

The view's record does not change kind: on paper the view is a sheet, and in Pages it is the page
being read. It follows the scroll, so the layout tab, the Project Browser, the HUD and Properties
all name the page on screen. A page is drawn when it comes near the screen, nearest first, one per
turn of the event loop, and again only when the model's revision (V122a), the appearance, the sheet,
the title block or the page's pixels have changed since it was drawn."""
NAME = 'patch_phase122c.py'
BASE = 'a6ec70b0415837cb4c358b620c4e7a59e320a79ef12bd9451ad1abeac7b9295c'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]

# ---- the markup: the display switch, the pages' controls, and the pages
rep("""        '<div class="a3d-sheettb">'+
          '<span id="a3d-sheetnum" class="a3d-sheetnum">Sheet</span>'+
          '<span class="a3d-sheetsp"></span>'+
""", """        '<div class="a3d-sheettb">'+
          /* __acad3dV122: the sheet alone to edit, or every sheet as pages */
          '<span class="a3d-shdisp" role="group" aria-label="Sheet display">'+
            '<button class="a3d-btn a3d-shdbtn on" data-shdisp="layout" title="This sheet alone, to edit its layout">Layout</button>'+
            '<button class="a3d-btn a3d-shdbtn" data-shdisp="pages" title="Every sheet as pages in one scroll, like a PDF">Pages</button>'+
          '</span>'+
          '<span id="a3d-sheetnum" class="a3d-sheetnum">Sheet</span>'+
          '<span class="a3d-sheetsp"></span>'+
          '<span class="a3d-pgonly a3d-pgnav">'+
            '<button class="a3d-btn" id="a3d-pgprev" title="Previous page" aria-label="Previous page">‹</button>'+
            '<input id="a3d-pgnum" class="a3d-pgnum" type="text" inputmode="numeric" aria-label="Page number" value="1">'+
            '<span id="a3d-pgof" class="a3d-pgof">of 1</span>'+
            '<button class="a3d-btn" id="a3d-pgnext" title="Next page" aria-label="Next page">›</button>'+
          '</span>'+
          '<select id="a3d-pgzoom" class="a3d-pgonly a3d-pgzoom" aria-label="Zoom"></select>'+
""")
rep("""'<button class="a3d-btn" id="a3d-sheetaddvp" """, """'<button class="a3d-btn a3d-lyonly" id="a3d-sheetaddvp" """)
rep("""'<button class="a3d-btn" id="a3d-sheetprops" """, """'<button class="a3d-btn a3d-lyonly" id="a3d-sheetprops" """)
rep("""'<button class="a3d-btn" id="a3d-sheettbedit" """, """'<button class="a3d-btn a3d-lyonly" id="a3d-sheettbedit" """)
rep("""'<button class="a3d-btn" id="a3d-sheetpng" """, """'<button class="a3d-btn a3d-lyonly" id="a3d-sheetpng" """)
rep("""'<button class="a3d-btn" id="a3d-sheetsvg" """, """'<button class="a3d-btn a3d-lyonly" id="a3d-sheetsvg" """)
rep("""'<button class="a3d-btn a3d-btn-pri" id="a3d-sheetprint" """, """'<button class="a3d-btn a3d-btn-pri a3d-lyonly" id="a3d-sheetprint" """)
rep("""        '<div class="a3d-sheetwrap"><canvas id="a3d-sheetcanvas"></canvas></div>'+
""", """        '<div class="a3d-sheetwrap"><canvas id="a3d-sheetcanvas"></canvas></div>'+
        '<div class="a3d-pageswrap" id="a3d-pageswrap"><div class="a3d-pagescol" id="a3d-pagescol"></div></div>'+   /* __acad3dV122 */
""")

# ---- the styles
rep(""".a3d-sheetwrap{flex:1 1 auto;overflow:auto;display:flex;align-items:flex-start;justify-content:center;padding:18px}
""", """.a3d-sheetwrap{flex:1 1 auto;overflow:auto;display:flex;align-items:flex-start;justify-content:center;padding:18px}
/* __acad3dV122: the Pages display -- every sheet in one scroll, the way a PDF reader shows a document */
.a3d-sheettb{flex-wrap:wrap;row-gap:6px}   /* a narrow window gives the bar a second row, not two-line buttons */
.a3d-sheettb .a3d-btn{white-space:nowrap}
.a3d-shdisp{display:inline-flex;flex:0 0 auto;margin-right:4px}
.a3d-shdisp .a3d-btn{border-radius:0}
.a3d-shdisp .a3d-btn:first-child{border-radius:4px 0 0 4px}
.a3d-shdisp .a3d-btn:last-child{border-radius:0 4px 4px 0;margin-left:-1px}
.a3d-shdisp .a3d-btn.on{background:#2f5d8a;border-color:#3f75a8;color:#fff}
.a3d-sheetview .a3d-pgonly{display:none}
.a3d-sheetview.a3d-pagesmode .a3d-pgonly{display:inline-flex}
.a3d-sheetview.a3d-pagesmode select.a3d-pgonly{display:inline-block}
.a3d-sheetview.a3d-pagesmode .a3d-lyonly{display:none}
.a3d-sheetview.a3d-pagesmode .a3d-sheetwrap{display:none}
.a3d-pgnav{align-items:center;gap:4px}
.a3d-pgnav .a3d-btn{padding:3px 9px}
.a3d-pgnav .a3d-btn:disabled{opacity:.35;cursor:default}
.a3d-pgnum{width:38px;background:#15171a;border:1px solid #3a4048;border-radius:4px;color:#e6e8ea;font:inherit;font-size:12px;text-align:center;padding:3px 2px}
.a3d-pgof{color:#a9abae;font-size:12px;white-space:nowrap;margin-right:2px}
.a3d-pgzoom{background:#2a2f35;border:1px solid #3a4048;color:#c8ced6;border-radius:4px;font-size:12px;padding:3px 4px}
.a3d-pageswrap{display:none;position:relative;flex:1 1 auto;overflow-x:auto;overflow-y:scroll;padding:18px}
.a3d-sheetview.a3d-pagesmode .a3d-pageswrap{display:block}
.a3d-page{margin:0 auto 18px;background:#fff;box-shadow:0 6px 24px rgba(0,0,0,.5);cursor:default}
.a3d-page:last-child{margin-bottom:0}
.a3d-page canvas{display:block;width:100%;height:100%}
""")

# ---- the model's revision tells the pages
rep("""    A3D_REV++;   /* __acad3dV122 */
    if(saveT)clearTimeout(saveT);
""", """    A3D_REV++;   /* __acad3dV122 */
    bimPagesStale();
    if(saveT)clearTimeout(saveT);
""")
rep("""  function bimSyncPresentPill(){
    if(!el.present)return;
""", """  function bimSyncPresentPill(){
    bimPagesStale();   /* __acad3dV122: every change of appearance passes here, and a page is drawn in it */
    if(!el.present)return;
""")

# ---- the status bar's hint on the pages
rep("""    if(bimSheetOnScreen()){   /* __acad3dV116 */
      if(A3D.sheetActiveVp){
""", """    if(bimSheetOnScreen()){   /* __acad3dV116 */
      if(A3D_PAGES.display==='pages')   /* __acad3dV122: from the table the keys are read from */
        return 'Pages: scroll, or '+bimPageKeyWords('next')+' and '+bimPageKeyWords('prev')+' to turn a page; double-click a page to edit its layout';
      if(A3D.sheetActiveVp){
""")

# ---- the sheet view draws the page it shows, or the pages
rep("""    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(sheet);   /* __acad3dV116 */
    bimRenderLayoutTabs();
    bimRenderSheet(sheet,SHEET_PREVIEW_PXMM);
  }
""", """    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(sheet);   /* __acad3dV116 */
    bimRenderLayoutTabs();
    if(A3D_PAGES.display==='pages'){bimPagesRefresh();return;}   /* __acad3dV122 */
    bimRenderSheet(sheet,SHEET_PREVIEW_PXMM);
  }
""")
rep("""    A3D.activeSheetId=id;A3D.sheetSelVp=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */
    if(el.sheetview)el.sheetview.classList.add('open');
    refreshBrowser();bimSheetViewRefresh();
  }
""", """    A3D.activeSheetId=id;A3D.sheetSelVp=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */
    if(el.sheetview)el.sheetview.classList.add('open');
    refreshBrowser();bimSheetViewRefresh();
    if(A3D_PAGES.display==='pages')bimPagesScrollTo(id);   /* __acad3dV122: the sheet opened is the page shown */
  }
""")
rep("""        var wasOn=(A3D.activeSheetId===id&&bimSheetOnScreen());   /* __acad3dV116 */
        if(A3D.activeSheetId===id)A3D.activeSheetId=A3D.sheets.length?A3D.sheets[0].id:null;
        if(wasOn)bimShowModel();
""", """        var wasOn=(A3D.activeSheetId===id&&bimSheetOnScreen());   /* __acad3dV116 */
        /* __acad3dV122: in Pages the reader stays in the document, on the page that took its place */
        var inPages=wasOn&&A3D_PAGES.display==='pages'&&A3D.sheets.length>0;
        if(A3D.activeSheetId===id)A3D.activeSheetId=A3D.sheets.length?A3D.sheets[inPages?Math.min(i,A3D.sheets.length-1):0].id:null;
        if(inPages)bimSetActiveView('sheet',A3D.activeSheetId,null);
        else if(wasOn)bimShowModel();
""")

# ---- the keys: in Pages they turn pages
rep("""    if(el.dlg||ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key))return false;
    if(ev.key==='Escape'){
      if(A3D.sheetActiveVp)bimSetPaperSpace();
""", """    if(el.dlg||ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key))return false;
    if(A3D_PAGES.display==='pages'){   /* __acad3dV122: the pages' keys, from their table */
      var pact=bimPageKeyAct(ev.key);
      if(pact)bimPagesKeyDo(pact);
      ev.preventDefault();ev.stopImmediatePropagation();
      return true;
    }
    if(ev.key==='Escape'){
      if(A3D.sheetActiveVp)bimSetPaperSpace();
""")

# ---- the engine of the Pages display
rep("""  function bimOpenSheetView(id){
""", """  /* ================= __acad3dV122: the Pages display =================
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
      try{if(bimPagesOn())bimPagesQueue();}
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
  function bimOpenSheetView(id){
""")

# ---- the elements, found once
rep("""    el.sheetnum=root.querySelector('#a3d-sheetnum');
""", """    el.sheetnum=root.querySelector('#a3d-sheetnum');
    /* __acad3dV122: the Pages display */
    el.pageswrap=root.querySelector('#a3d-pageswrap');el.pagescol=root.querySelector('#a3d-pagescol');
    el.pgprev=root.querySelector('#a3d-pgprev');el.pgnext=root.querySelector('#a3d-pgnext');
    el.pgnum=root.querySelector('#a3d-pgnum');el.pgof=root.querySelector('#a3d-pgof');el.pgzoom=root.querySelector('#a3d-pgzoom');
    bimWirePages();
""")

# ---- the hooks
rep("""  window.__a3dActiveSheetId=function(){return A3D.activeSheetId;};
""", """  window.__a3dActiveSheetId=function(){return A3D.activeSheetId;};
  /* __acad3dV122: the Pages display, as the engine holds it */
  window.__a3dPages=function(){
    var pages=A3D.sheets.map(function(s){
      var e=A3D_PAGES.els[s.id];
      return {id:s.id,label:bimSheetLabel(s),el:!!e,cssW:e?e.box.offsetWidth:0,cssH:e?e.box.offsetHeight:0,
        devW:e?e.cv.width:0,devH:e?e.cv.height:0,scale:e?e.scale:0,drawn:!!(e&&e.key&&e.key===bimPageKey(s,e))};
    });
    var dom=el.pagescol?Array.prototype.map.call(el.pagescol.children,function(b){return b.getAttribute('data-page');}):[];
    return {display:A3D_PAGES.display,on:bimPagesOn(),zoom:A3D_PAGES.zoom,pxmm:A3D_PAGES.pxmm,cur:A3D.activeSheetId,dom:dom,
      index:bimPagesIndex(),rev:A3D_REV,pages:pages,scrollTop:el.pageswrap?el.pageswrap.scrollTop:0,
      view:{kind:A3D_VIEW.kind,id:A3D_VIEW.id,name:A3D_VIEW.name},hint:bimStatusHintText(),
      keys:A3D_PAGEVIEW_KEYS.map(function(k){return {act:k.act,keys:k.keys.slice(),say:k.say.slice(),label:k.label};}),
      zooms:A3D_PAGE_ZOOMS.map(function(z){return z.v;})};
  };
  window.__a3dPagesDisplay=function(d){return bimPagesSetDisplay(d);};
  window.__a3dPagesGo=function(i){return bimPagesGo(i);};
  window.__a3dPagesZoom=function(z){return bimPagesZoom(z);};
  /* the pixels of a page drawn afresh at a scale, to set beside the page on screen */
  window.__a3dPageFresh=function(id,scale){
    var s=bimSheetById(id);if(!s)return null;
    var cv=document.createElement('canvas');
    bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,cv,scale);
    return cv.toDataURL('image/png');
  };
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
