"""patch_phase122d.py -- V122: Present -- the pages full screen, one at a time, for a client.

The owner: "Need a presentation for doing presentation with clients." Present shows the pages in the
project's order on black, each drawn as it plots and fitted to the screen, from the page on screen
(or the one it is started from) onwards:

  - the browser's full screen is asked for; where it is refused -- a page opened inside a frame, a
    browser set not to allow it -- the pages fill the window instead, and the presenter is told on
    the presentation itself, since the app's messages sit underneath it;
  - Right, Down, Page Down, Space, Enter or N for the next page; Left, Up, Page Up, Backspace or P for
    the one before; Home and End; Escape to end -- from one table (A3D_SHOW_KEYS) that the handler,
    the hint on screen and the shortcut sheet are all drawn from;
  - a click for the next page and the wheel either way, one page a turn of the wheel;
  - a bar with the same steps and the page count, for a mouse or a finger, that shows while the mouse
    moves and gets out of the way when it stops, with the cursor;
  - every key belongs to the presentation while it runs: nothing typed during it reaches the model.
    The browser keeps its own chords (full screen, the developer tools).

Ending it goes back to where it was started, on paper to the page last shown. The next page is drawn
ahead while the current one is on screen, so a step does not wait for a render.

The shortcut sheet gains the Pages display's keys (V122c) and these, as two groups drawn from their
tables; its rows of alternatives are written with a slash, not the plus of a chord."""
NAME = 'patch_phase122d.py'
BASE = '50c1c4f13291bc1c018cb99de18a54727bce336487a56fabe1b0f2eced6deb95'
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

# ---- the Present button, on paper in either display
rep("""          '<button class="a3d-btn a3d-btn-pri a3d-lyonly" id="a3d-sheetprint" title="Print sheet (vector)">Print</button>'+
""", """          '<button class="a3d-btn a3d-btn-pri a3d-lyonly" id="a3d-sheetprint" title="Print sheet (vector)">Print</button>'+
          '<button class="a3d-btn a3d-btn-pri" id="a3d-sheetpresent" title="Present the pages full screen, one at a time, from this one">Present</button>'+   /* __acad3dV122 */
""")
rep("""    el.pgnum=root.querySelector('#a3d-pgnum');el.pgof=root.querySelector('#a3d-pgof');el.pgzoom=root.querySelector('#a3d-pgzoom');
""", """    el.pgnum=root.querySelector('#a3d-pgnum');el.pgof=root.querySelector('#a3d-pgof');el.pgzoom=root.querySelector('#a3d-pgzoom');
    var sheetPresentBtn=root.querySelector('#a3d-sheetpresent');
    if(sheetPresentBtn)sheetPresentBtn.addEventListener('click',function(){bimSlideshowStart(A3D.activeSheetId);});
""")

# ---- the styles
rep(""".a3d-page canvas{display:block;width:100%;height:100%}
""", """.a3d-page canvas{display:block;width:100%;height:100%}
/* __acad3dV122: Present */
.a3d-slideshow{position:fixed;inset:0;z-index:100000;background:#000;display:none;align-items:center;justify-content:center;user-select:none;-webkit-user-select:none}
.a3d-slideshow.open{display:flex}
.a3d-slideshow.idle{cursor:none}
.a3d-sscv{display:block;background:#fff}
.a3d-ssbar{position:absolute;left:50%;bottom:22px;transform:translateX(-50%);display:flex;align-items:center;gap:4px;padding:5px 7px;border-radius:10px;background:rgba(28,31,36,.92);color:#e6e8ea;font:13px/1 system-ui,sans-serif;transition:opacity .25s}
.a3d-ssbar button{background:transparent;border:0;color:#e6e8ea;font:inherit;padding:7px 11px;border-radius:6px;cursor:pointer}
.a3d-ssbar button:hover{background:rgba(255,255,255,.12)}
.a3d-ssbar button:disabled{opacity:.3;cursor:default;background:transparent}
.a3d-sspos{min-width:58px;text-align:center;font-variant-numeric:tabular-nums}
.a3d-sshint{position:absolute;left:50%;top:16px;transform:translateX(-50%);max-width:90vw;text-align:center;color:rgba(255,255,255,.72);font:12px/1.4 system-ui,sans-serif;transition:opacity .4s}
.a3d-slideshow.idle .a3d-ssbar,.a3d-slideshow.idle .a3d-sshint{opacity:0;pointer-events:none}
""")

# ---- every key is the presentation's while it runs
rep("""  function onKey(ev){
    if(!A3D.on)return;
""", """  function onKey(ev){
    if(!A3D.on)return;
    if(A3D_SLIDESHOW.on){bimSlideshowKey(ev);return;}   /* __acad3dV122: nothing typed reaches the model */
""")

# ---- the shortcut sheet: the two tables as two groups, alternatives with a slash
rep("""    for(i=0;i<A3D_KEYS.length;i++){
      g=A3D_KEYS[i];
""", """    var groups=bimShortcutGroups();   /* __acad3dV122 */
    for(i=0;i<groups.length;i++){
      g=groups[i];
""")
rep("""          if(k)h+='<span class="a3d-rkplus">+</span>';
""", """          if(k)h+='<span class="a3d-rkplus">'+(r.alt?'/':'+')+'</span>';   /* __acad3dV122: a slash between alternatives */
""")
rep("""  function bimShortcutsHtml(){
""", """  /* __acad3dV122: the sheet's groups -- A3D_KEYS, and the keys of the Pages display and of Present,
     read from the tables their handlers read. A row of alternatives (`alt`) is any one of its keys.
     They carry no `k`: the V85 suite presses keys with nothing open, and these work on the pages or
     in a presentation, where the V122 suite presses them. */
  function bimShortcutGroups(){
    function rows(tbl){
      return tbl.map(function(r){return {keys:r.say.slice(),k:null,alt:true,label:r.label};});
    }
    return A3D_KEYS.concat([{grp:'Pages',rows:rows(A3D_PAGEVIEW_KEYS)},{grp:'Presenting',rows:rows(A3D_SHOW_KEYS)}]);
  }
  function bimShortcutsHtml(){
""")
rep("""  window.__a3dShortcuts=function(){return JSON.parse(JSON.stringify(A3D_KEYS));};
""", """  window.__a3dShortcuts=function(){return JSON.parse(JSON.stringify(bimShortcutGroups()));};   /* __acad3dV122 */
""")

# ---- the presentation itself
rep("""  function bimOpenSheetView(id){
""", """  /* ================= __acad3dV122: Present -- the pages full screen, one at a time =================
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
        '<button type="button" data-ssact="prev" title="Previous page" aria-label="Previous page">‹</button>'+
        '<span class="a3d-sspos">1 / 1</span>'+
        '<button type="button" data-ssact="next" title="Next page" aria-label="Next page">›</button>'+
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
    if(!A3D.sheets.length){a3dToast('There are no pages to present yet: every sheet is a page');return false;}
    var idx=0,i,ov;
    for(i=0;i<A3D.sheets.length;i++)if(A3D.sheets[i].id===fromId){idx=i;break;}
    try{ov=bimSlideshowEl();}
    catch(eE){console.warn('[BIM] The presentation could not be set up',eE);a3dToast('The presentation could not start -- see the console');return false;}
    A3D_SLIDESHOW.on=true;A3D_SLIDESHOW.idx=idx;A3D_SLIDESHOW.ahead=null;A3D_SLIDESHOW.msg='';
    A3D_SLIDESHOW.from={kind:A3D_VIEW.kind,id:A3D_VIEW.id};
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
    var ov=A3D_SLIDESHOW.el,n=A3D.sheets.length,i=A3D_SLIDESHOW.idx;
    if(!ov)return;
    ov.querySelector('.a3d-sspos').textContent=(i+1)+' / '+n;
    ov.querySelector('[data-ssact="prev"]').disabled=(i<=0);
    ov.querySelector('[data-ssact="next"]').disabled=(i>=n-1);
    ov.querySelector('.a3d-sshint').textContent=A3D_SLIDESHOW.msg+bimSlideshowHint();
  }
  /* the page on screen: fitted with a small margin, drawn for this screen, the next one drawn ahead */
  function bimSlideshowShow(){
    if(!A3D_SLIDESHOW.on)return;
    var n=A3D.sheets.length;
    if(!n){bimSlideshowEnd();return;}
    if(A3D_SLIDESHOW.idx>n-1)A3D_SLIDESHOW.idx=n-1;
    var s=A3D.sheets[A3D_SLIDESHOW.idx],ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv;
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
  function bimSlideshowAhead(i){
    setTimeout(function(){
      if(!A3D_SLIDESHOW.on||i>=A3D.sheets.length)return;
      var s=A3D.sheets[i],ov=A3D_SLIDESHOW.el,vw=ov.clientWidth||window.innerWidth,vh=ov.clientHeight||window.innerHeight;
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
    var n=A3D.sheets.length;
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
    if(act==='last')return bimSlideshowGo(A3D.sheets.length-1);
    if(act==='end')return bimSlideshowEnd();
    return false;
  }
  function bimSlideshowKey(ev){
    var act=null,i;
    for(i=0;i<A3D_SHOW_KEYS.length;i++)if(A3D_SHOW_KEYS[i].keys.indexOf(ev.key)>=0){act=A3D_SHOW_KEYS[i].act;break;}
    ev.stopImmediatePropagation();
    /* the browser keeps its chords and function keys -- full screen, the developer tools */
    if(ev.ctrlKey||ev.metaKey||ev.altKey||/^F\\d+$/.test(ev.key))return true;
    ev.preventDefault();
    if(act)bimSlideshowAct(act);
    return true;
  }
  /* back where it was started; on paper, to the page last shown */
  function bimSlideshowEnd(){
    if(!A3D_SLIDESHOW.on)return false;
    var s=A3D.sheets[A3D_SLIDESHOW.idx],from=A3D_SLIDESHOW.from||{},ov=A3D_SLIDESHOW.el;
    A3D_SLIDESHOW.on=false;A3D_SLIDESHOW.ahead=null;
    if(A3D_SLIDESHOW.idleT){clearTimeout(A3D_SLIDESHOW.idleT);A3D_SLIDESHOW.idleT=null;}
    if(ov)ov.classList.remove('open','idle');
    var fsEl=document.fullscreenElement||document.webkitFullscreenElement;
    if(A3D_SLIDESHOW.fs&&fsEl){
      try{var x=(document.exitFullscreen||document.webkitExitFullscreen).call(document);if(x&&x.catch)x.catch(function(eX){console.warn('[BIM] Full screen could not be left',eX);});}
      catch(eX){console.warn('[BIM] Full screen could not be left',eX);a3dToast('Full screen could not be left -- press Esc');}
    }
    A3D_SLIDESHOW.fs=false;
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
""")

# ---- the hooks
rep("""  window.__a3dPagesDisplay=function(d){return bimPagesSetDisplay(d);};
""", """  window.__a3dPagesDisplay=function(d){return bimPagesSetDisplay(d);};
  /* __acad3dV122: Present, as the engine holds it */
  window.__a3dSlideshow=function(){
    var ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv,s=A3D.sheets[A3D_SLIDESHOW.idx]||null;
    return {on:A3D_SLIDESHOW.on,idx:A3D_SLIDESHOW.idx,id:s?s.id:null,n:A3D.sheets.length,fs:A3D_SLIDESHOW.fs,
      fsEl:!!(document.fullscreenElement||document.webkitFullscreenElement),open:!!(ov&&ov.classList.contains('open')),
      idle:!!(ov&&ov.classList.contains('idle')),cssW:cv?cv.offsetWidth:0,cssH:cv?cv.offsetHeight:0,devW:cv?cv.width:0,devH:cv?cv.height:0,
      shown:cv?cv.getAttribute('data-sspage'):null,drawnKey:cv?cv.getAttribute('data-sskey'):null,scale:A3D_SLIDESHOW.scale,
      key:s?bimPageSig(s):null,pos:ov?ov.querySelector('.a3d-sspos').textContent:'',hint:ov?ov.querySelector('.a3d-sshint').textContent:'',
      ahead:A3D_SLIDESHOW.ahead?A3D_SLIDESHOW.ahead.id:null,
      keys:A3D_SHOW_KEYS.map(function(k){return {act:k.act,keys:k.keys.slice(),say:k.say.slice(),label:k.label};})};
  };
  window.__a3dSlideshowStart=function(id){return bimSlideshowStart(id);};
  window.__a3dSlideshowEnd=function(){return bimSlideshowEnd();};
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
