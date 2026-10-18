"""patch_phase166g.py -- V166c: Properties' width by one press, and its edge a window splitter.

  the button   in Properties' header, beside its minimise, 30 px (36 for a finger): each press widens
               Properties a step -- 240, 320, 400, 480, 560 within what the screen allows -- and from
               the widest goes back to 240; its label says where the next press goes. WCAG 2.2's 2.5.7
               single-pointer way, and 2.5.8's equivalent control for the 7 px edge. Hidden where
               Properties is a drawer or a sheet, and while it is minimised.
  the screen   Properties' widest keeps the drawing 320 px beside the left panel at its narrowest: the
               left panel gives way to Properties (V166b), never below its 242 px
  the edge     the W3C's window splitter: a focusable separator named by the header's "Properties", its
               width as its value; Left widens Properties (the splitter moves left), Right narrows it,
               16 px (Shift, 64); Home and End; Enter minimises it, the focus on the minimise button,
               whose Enter brings it back. Pointer events: a mouse, a pen or a finger (it took mousedown
               alone, so a finger could not move it); a cancelled drag puts the width back.
  where        docked by the stylesheet's own query, over 1024 px wide and over 500 high. V147's code
               said wider than 900, so the arrow shrank a drawer (901 to 1024 px wide) or a sheet (a
               phone on its side wider than 900, any window 500 px high or less) to a 42 px strip
  the audit    reaches Properties' chrome (its header, its edge, the phone's grab bar; not its body),
               and counts an edge that takes the focus as a control
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = 'b7ee1405e5248fbb833127618991763e1d0d997790b7230525e00d3d75032b7e'   # V166b, after patch_phase166f.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimLeftStep(){' in txt, 'run patch_phase166f.py first'
NA0 = sum(1 for c in txt if ord(c) > 127)


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- the header's name, which the edge takes ----
rep(r"""'<div class="a3d-palhd">Properties</div>'+""",
    r"""'<div class="a3d-palhd"><span id="a3d-rpttl">Properties</span></div>'+   /* __acad3dV166c: the name its edge takes */""")

# ---- the stylesheet ----
rep(r""".a3d-rgrip{position:absolute;left:-3px;top:0;bottom:0;width:7px;cursor:col-resize;z-index:6}
.a3d-rgrip:hover,.a3d-rgrip.drag{background:linear-gradient(90deg,transparent 2px,var(--pp-acc,#4ea1ff) 2px,var(--pp-acc,#4ea1ff) 4px,transparent 4px)}
""", r""".a3d-rgrip{position:absolute;left:-3px;top:0;bottom:0;width:7px;cursor:col-resize;z-index:6;touch-action:none;outline:0}   /* __acad3dV166c: a finger's too, and focusable */
.a3d-rgrip:hover,.a3d-rgrip.drag,.a3d-rgrip:focus-visible{background:linear-gradient(90deg,transparent 2px,var(--pp-acc,#4ea1ff) 2px,var(--pp-acc,#4ea1ff) 4px,transparent 4px)}
body.a3d-rpdrag,body.a3d-rpdrag *{cursor:col-resize!important;user-select:none;-webkit-user-select:none}
body.a3d-rpdrag #a3d-leftpanel{transition:none}   /* it gives way as Properties is dragged, in step with the drawing's edge */
/* __acad3dV166c: Properties' width, by one press, beside its minimise; a docked panel's, as its edge is */
.a3d-rpwbtn{width:30px;height:30px;display:inline-grid;place-items:center;border:0;border-radius:6px;background:transparent;color:var(--pp-muted,#8f98a2);cursor:pointer;padding:0;flex:0 0 auto;margin:0 2px 0 auto}
.a3d-rpwbtn:hover{background:var(--pp-hover,rgba(255,255,255,.06));color:var(--pp-text,#fff)}
.a3d-rpwbtn svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
""")
rep(r"""body.a3d-rmin #a3d-right #a3d-propsbody,body.a3d-rmin .a3d-rgrip{display:none}""",
    r"""body.a3d-rmin #a3d-right #a3d-propsbody,body.a3d-rmin .a3d-rgrip,body.a3d-rmin .a3d-rpwbtn{display:none}""")
rep(r"""@media(max-width:1024px),(max-height:500px){.a3d-rgrip{display:none}}""",
    r"""@media(max-width:1024px),(max-height:500px){.a3d-rgrip,.a3d-rpwbtn{display:none}}   /* __acad3dV166c: BIM_RIGHT_SHEET_MQ, the code's own */""")
rep(r""".a3d-rmin{width:36px;height:36px}
""", r""".a3d-rmin{width:36px;height:36px}
.a3d-rpwbtn{width:36px;height:36px}   /* __acad3dV166c: a finger's target, and a 12 px edge it can see */
.a3d-rgrip{left:0;width:12px;background:linear-gradient(90deg,transparent 2px,rgba(255,255,255,.16) 2px,rgba(255,255,255,.16) 4px,transparent 4px)}
.a3d-rgrip.drag{background:linear-gradient(90deg,transparent 2px,var(--pp-acc,#4ea1ff) 2px,var(--pp-acc,#4ea1ff) 5px,transparent 5px)}
body.light-theme .a3d-rgrip:not(.drag):not(:focus-visible){background:linear-gradient(90deg,transparent 2px,rgba(0,0,0,.14) 2px,rgba(0,0,0,.14) 4px,transparent 4px)}
""")

# ---- where it is docked; its widest; the steps ----
rep(r"""  function bimRightDesktop(){return (window.innerWidth||0)>900;}
""", r"""  /* __acad3dV166c: docked beside the drawing where the stylesheet docks it, over 1024 px wide and over
     500 px high; below that Properties is a drawer or a sheet. The same query as the rule that hides
     its edge and its width button, so the code and the stylesheet cannot disagree: V147's "wider than
     900" let the arrow shrink a drawer, or a sheet on a phone on its side, to a 42 px strip */
  var BIM_RIGHT_SHEET_MQ='(max-width:1024px),(max-height:500px)';
  function bimRightDesktop(){
    if(window.matchMedia)return !window.matchMedia(BIM_RIGHT_SHEET_MQ).matches;
    return (window.innerWidth||0)>1024&&(window.innerHeight||0)>500;
  }
  /* the widest Properties may be now: the drawing keeps BIM_LEFT_KEEP px beside the left panel at its
     narrowest, since the left panel gives way to Properties (V166b) but never below BIM_LEFT_MIN */
  function bimRightMax(){
    return Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,Math.floor((window.innerWidth||0)-BIM_LEFT_RAIL-BIM_LEFT_MIN-BIM_LEFT_KEEP)));
  }
  /* the width on screen, and the next step up within what the screen allows; from the widest, back to
     the narrowest -- V166b's rule for the left panel */
  var BIM_RIGHT_STEPS=[BIM_RIGHT_MIN,320,400,480,BIM_RIGHT_MAX];
  function bimRightW(){var rp=document.getElementById('a3d-right');return rp?Math.round(rp.getBoundingClientRect().width):0;}
  function bimRightNext(){
    var w=bimRightW(),mx=bimRightMax(),i;
    for(i=0;i<BIM_RIGHT_STEPS.length;i++)if(BIM_RIGHT_STEPS[i]>w&&BIM_RIGHT_STEPS[i]<=mx)return BIM_RIGHT_STEPS[i];
    return w<mx?mx:BIM_RIGHT_MIN;
  }
  function bimRightStep(){return bimRightSetWidth(bimRightNext());}
""")
rep(r"""    var w=isFinite(p.w)?Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,p.w)):null;
    rp.style.width=(w&&bimRightDesktop()&&!p.min)?w+'px':'';
    var b=document.getElementById('a3d-rminbtn');
    if(b){b.setAttribute('aria-pressed',p.min?'true':'false');b.title=p.min?'Show the Properties panel':'Minimise the Properties panel';}
    bimShellDockW();   /* __acad3dV166b: the left panel keeps the drawing its room */
    return {w:rp.getBoundingClientRect().width,min:!!p.min};
""", r"""    var w=isFinite(p.w)?Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),p.w)):null;   /* __acad3dV166c: within what the screen allows now; the one kept stays */
    rp.style.width=(w&&bimRightDesktop()&&!p.min)?w+'px':'';
    var b=document.getElementById('a3d-rminbtn');
    if(b){b.setAttribute('aria-pressed',p.min?'true':'false');b.title=p.min?'Show the Properties panel':'Minimise the Properties panel';}
    bimShellDockW();   /* __acad3dV166b: the left panel keeps the drawing its room */
    /* __acad3dV166c: the edge's value and range, and where the button's next press goes */
    var cw=bimRightW(),mx=bimRightMax(),nx=bimRightNext(),g=rp.querySelector('.a3d-rgrip'),wb=rp.querySelector('[data-rpwidth]');
    if(g){g.setAttribute('aria-valuenow',String(cw));g.setAttribute('aria-valuemin',String(BIM_RIGHT_MIN));g.setAttribute('aria-valuemax',String(mx));}
    if(wb){wb.setAttribute('aria-label','Properties width '+cw+' px: '+(nx>cw?'widen to '+nx:'back to '+nx));wb.title=wb.getAttribute('aria-label');}
    return {w:rp.getBoundingClientRect().width,min:!!p.min,kept:typeof p.w==='number'?p.w:null,max:mx,next:nx,docked:bimRightDesktop(),mq:BIM_RIGHT_SHEET_MQ,
      grip:!!(g&&getComputedStyle(g).display!=='none'),button:!!(wb&&getComputedStyle(wb).display!=='none')};
""")
rep(r"""    var p=bimRightPrefs();p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,w)));bimRightSave(p);
""", r"""    var p=bimRightPrefs();
    if(w===null)delete p.w;   /* __acad3dV166c: null forgets it, as the edge's double click does */
    else p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),w)));
    bimRightSave(p);
""")

# ---- the edge: a window splitter, by any pointer and from the keyboard ----
rep(r"""    var g=document.createElement('div');g.className='a3d-rgrip';g.title='Drag to resize';g.setAttribute('aria-hidden','true');
    rp.insertBefore(g,rp.firstChild);
""", r"""    /* __acad3dV166c: the edge is the W3C's window splitter -- a focusable separator named by the
       header's "Properties", its width as its value */
    var g=document.createElement('div');g.className='a3d-rgrip';g.tabIndex=0;g.title='Drag to resize; double-click to put it back';
    g.setAttribute('role','separator');g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-right');g.setAttribute('aria-labelledby','a3d-rpttl');
    rp.insertBefore(g,rp.firstChild);
""")
rep(r"""    if(hd&&!document.getElementById('a3d-rminbtn')){
      var b=document.createElement('button');b.type='button';b.id='a3d-rminbtn';""",
    r"""    if(hd&&!document.getElementById('a3d-rminbtn')){
      var wb=document.createElement('button');wb.type='button';wb.className='a3d-rpwbtn';wb.setAttribute('data-rpwidth','1');   /* __acad3dV166c: the width, by one press */
      wb.innerHTML='<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M2.5 9h13M5.5 6 2.5 9l3 3M12.5 6l3 3-3 3"/></svg>';
      wb.addEventListener('click',function(){bimRightStep();});
      hd.appendChild(wb);
      var b=document.createElement('button');b.type='button';b.id='a3d-rminbtn';""")
rep(r"""    g.addEventListener('mousedown',function(ev){
      if(!bimRightDesktop())return;
      ev.preventDefault();
      var x0=ev.clientX,w0=rp.getBoundingClientRect().width;
      g.classList.add('drag');document.body.style.cursor='col-resize';
      function mv(e){var w=Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,w0+(x0-e.clientX)));rp.style.width=w+'px';try{size();paint();}catch(eS){}}
      function up(e){
        document.removeEventListener('mousemove',mv);document.removeEventListener('mouseup',up);
        g.classList.remove('drag');document.body.style.cursor='';
        bimRightSetWidth(rp.getBoundingClientRect().width);
      }
      document.addEventListener('mousemove',mv);document.addEventListener('mouseup',up);
    });
    g.addEventListener('dblclick',function(){var p=bimRightPrefs();delete p.w;bimRightSave(p);bimRightApply();try{size();paint();}catch(eS){}});
""", r"""    /* __acad3dV166c: dragged by a mouse, a pen or a finger (pointer events: it took mousedown alone, so a
       finger could not move it), within what the screen allows, the left panel giving way as it goes;
       a cancelled drag puts the width back. The edge is shown only where Properties is docked. */
    var dr=null;
    g.addEventListener('pointerdown',function(ev){
      if(ev.button>0)return;
      ev.preventDefault();
      dr={x:ev.clientX,w:bimRightW(),id:ev.pointerId,now:null};
      try{g.setPointerCapture(ev.pointerId);}catch(eC){}
      g.classList.add('drag');document.body.classList.add('a3d-rpdrag');
    });
    g.addEventListener('pointermove',function(ev){
      if(!dr||ev.pointerId!==dr.id)return;
      var w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),dr.w+dr.x-ev.clientX)));
      if(w===dr.now)return;
      dr.now=w;rp.style.width=w+'px';bimShellDockW();try{size();paint();}catch(eS){}
    });
    function end(ev,keep){
      if(!dr||ev.pointerId!==dr.id)return;
      var w=dr.now;dr=null;
      g.classList.remove('drag');document.body.classList.remove('a3d-rpdrag');
      if(keep&&w!==null)bimRightSetWidth(w);
      else{bimRightApply();try{size();paint();}catch(eS){}}
    }
    g.addEventListener('pointerup',function(ev){end(ev,true);});
    g.addEventListener('pointercancel',function(ev){end(ev,false);});
    g.addEventListener('dblclick',function(){bimRightSetWidth(null);});
    /* the keys: the splitter moves the way the arrow points, so Left widens Properties, which is to its
       right; Home and End the narrowest and the widest; Enter minimises it, the focus going to the
       minimise button, whose Enter brings it back. A focused separator keeps its keys from the model (V166b). */
    g.addEventListener('keydown',function(ev){
      var k=ev.key,st=ev.shiftKey?64:16;
      if(k==='ArrowLeft'||k==='ArrowRight'){ev.preventDefault();bimRightSetWidth(bimRightW()+(k==='ArrowLeft'?st:-st));return;}
      if(k==='Home'||k==='End'){ev.preventDefault();bimRightSetWidth(k==='Home'?BIM_RIGHT_MIN:bimRightMax());return;}
      if(k==='Enter'){
        ev.preventDefault();
        bimRightToggleMin(true);
        var mb=document.getElementById('a3d-rminbtn');if(mb)mb.focus();
      }
    });
""")

# ---- the shell's audit reaches Properties' chrome, and knows its controls ----
rep(r"""    var nodes=shell.querySelectorAll('button,[role="button"],a[href],input,select');
""", r"""    /* __acad3dV166c: an edge that takes the focus is a control too; and Properties' own chrome -- its
       header, its edge, the phone's grab bar -- sits outside the shell. Its body (the fields of what is
       selected) is not the shell's. */
    var Q='button,[role="button"],[role="separator"][tabindex],a[href],input,select',rpA=document.getElementById('a3d-right');
    var nodes=[].slice.call(shell.querySelectorAll(Q));
    if(rpA)[].forEach.call(rpA.querySelectorAll(Q),function(e){if(!e.closest('#a3d-propsbody'))nodes.push(e);});
""")
rep(r"""    {sel:'[data-lpwidth]',why:'widens the panel a step at a time: its edge, by one press'},   /* __acad3dV166b */
""", r"""    {sel:'[data-lpwidth]',why:'widens the panel a step at a time: its edge, by one press'},   /* __acad3dV166b */
    {sel:'#a3d-lgrip',why:'the left panel\'s edge: dragged to size it, or moved from the keyboard'},   /* __acad3dV166c: driven by the V166b suite */
    {sel:'.a3d-rgrip',why:'Properties\' edge: dragged to size it, or moved from the keyboard'},   /* __acad3dV166c */
    {sel:'[data-rpwidth]',why:'widens Properties a step at a time: its edge, by one press'},
    {sel:'#a3d-rminbtn',why:'minimises Properties to a strip; on a phone or a tablet, closes its sheet or drawer'},   /* __acad3dV147, driven by its suite */
    {sel:'.a3d-rsheetbar',why:'on a phone, raises or lowers the Properties sheet'},
""")

# ---- the marker ----
rep(r"""  window.__acad3dV166b='""", r"""  window.__acad3dV166c='rightstep,rightsteplabel,rightstepscreen,rightstephidden,rightedgekeys,rightedgepointer,rightdocked,auditproperties';
  window.__acad3dV166b='""")

out = txt.encode('utf-8')
assert sum(1 for c in txt if ord(c) > 127) == NA0, 'the patch put non-ASCII characters into the build'
SRC.write_bytes(out)
print('patch_phase166g applied:', hashlib.sha256(out).hexdigest(), len(raw), '->', len(out))
