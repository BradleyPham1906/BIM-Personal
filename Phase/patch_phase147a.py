"""patch_phase147a.py -- V147: the right panel, redesigned.

After Figma's UI3: the work first, the panel quiet.
- One set of tokens (surface, line, text, muted, input, accent) for dark and light.
- Group headers in sentence case on a hairline, not uppercase boxes; one row grid (label 38%);
  one input style, 26 px high, with a focus ring; one button style; checkboxes in the accent.
- The element's type header flat, with a larger name.
- Long lists end in Show all, not "and N more".
- The panel resizes from its left edge (240 to 560 px, remembered) and minimises to a strip.
Every data attribute and group name is unchanged: what the panel does is the same."""
NAME = 'patch_phase147a.py'
BASE = 'da4c4fa7658db37b5fcf0f30a0d6466b8a08e1203a18349276b515271f524f73'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


CSS = r"""body.light-theme .a3d-ptabbtn.on{background:#fff;color:#111}
/* __acad3dV147: the right panel -- one set of tokens, one row grid, sentence case, quiet */
#a3d-right{--pp-bg:#1e2226;--pp-line:rgba(255,255,255,.075);--pp-text:#e6eaef;--pp-muted:#8f98a2;--pp-in:#16191c;--pp-inline:#353b43;--pp-hover:rgba(255,255,255,.055);--pp-acc:#4ea1ff;--pp-accbg:rgba(78,161,255,.16);background:var(--pp-bg);position:relative}
body.light-theme #a3d-right{--pp-bg:#fbfbfc;--pp-line:rgba(0,0,0,.08);--pp-text:#1f2328;--pp-muted:#687280;--pp-in:#fff;--pp-inline:#d5d9df;--pp-hover:rgba(0,0,0,.045);--pp-acc:#2f6fb8;--pp-accbg:rgba(47,111,184,.12)}
#a3d-right .a3d-palhd{background:transparent;border-bottom:1px solid var(--pp-line);font-size:13px;font-weight:600;letter-spacing:0;color:var(--pp-text);padding:11px 10px 11px 16px}
#a3d-right #a3d-propsbody{padding:2px 16px 22px}
#a3d-right .a3d-pgrp{background:transparent;border-radius:0;border-top:1px solid var(--pp-line);margin:14px 0 0;padding:12px 0 4px;font-size:12px;font-weight:600;letter-spacing:0;text-transform:none;color:var(--pp-text)}
#a3d-right .a3d-pgrp:hover{background:transparent;color:var(--pp-text)}
#a3d-right .a3d-pgcar{color:var(--pp-muted);border-radius:6px}
#a3d-right .a3d-pgrp:hover .a3d-pgcar{background:var(--pp-hover);color:var(--pp-text)}
#a3d-right .a3d-pgbody{padding:4px 0 2px}
#a3d-right .a3d-prow{grid-template-columns:minmax(0,38fr) minmax(0,62fr);gap:10px;padding:2px 0;min-height:30px}
#a3d-right .a3d-prow.ro{min-height:26px}
#a3d-right .a3d-plabel,#a3d-right .a3d-prow.ro .a3d-plabel{font-size:11.5px;color:var(--pp-muted)}
#a3d-right .a3d-pstatic,#a3d-right .a3d-prow.ro .a3d-pstatic{color:var(--pp-text);font-size:11.5px}
#a3d-right input[type=text],#a3d-right input[type=number],#a3d-right input[type=search],#a3d-right select,#a3d-right textarea{background:var(--pp-in);border:1px solid var(--pp-inline);color:var(--pp-text);border-radius:6px;min-height:26px;padding:3px 8px;font:inherit;font-size:11.5px;box-sizing:border-box;transition:border-color .12s ease,box-shadow .12s ease}
#a3d-right input:focus,#a3d-right select:focus,#a3d-right textarea:focus{outline:none;border-color:var(--pp-acc);box-shadow:0 0 0 3px var(--pp-accbg)}
#a3d-right input[type=checkbox]{accent-color:var(--pp-acc);width:14px;height:14px}
#a3d-right #a3d-propsbody button{min-height:26px;padding:0 10px;border-radius:6px;border:1px solid var(--pp-inline);background:var(--pp-hover);color:var(--pp-text);font:inherit;font-size:11.5px;cursor:pointer;transition:background .12s ease,border-color .12s ease}
#a3d-right #a3d-propsbody button:hover:not(:disabled){border-color:var(--pp-acc);background:var(--pp-accbg)}
#a3d-right #a3d-propsbody button:disabled{opacity:.45;cursor:default}
#a3d-right .a3d-ptypehd{background:transparent;border-bottom:1px solid var(--pp-line);margin:0 0 2px;padding:12px 0}
#a3d-right .a3d-ptypeic{width:32px;height:32px;border-radius:8px;background:var(--pp-hover);border-color:var(--pp-line);color:var(--pp-text)}
#a3d-right .a3d-ptypename{font-size:13px;color:var(--pp-text)}
#a3d-right .a3d-ptypesub{font-size:11px;color:var(--pp-muted)}
#a3d-right .a3d-ptabs{margin:12px 0 2px;background:var(--pp-hover)}
#a3d-right .a3d-histmore button{min-height:22px;padding:0 8px;font-size:11px}
.a3d-rgrip{position:absolute;left:-3px;top:0;bottom:0;width:7px;cursor:col-resize;z-index:6}
.a3d-rgrip:hover,.a3d-rgrip.drag{background:linear-gradient(90deg,transparent 2px,var(--pp-acc,#4ea1ff) 2px,var(--pp-acc,#4ea1ff) 4px,transparent 4px)}
.a3d-rmin{width:26px;height:26px;display:inline-grid;place-items:center;border:0;border-radius:6px;background:transparent;color:var(--pp-muted,#8f98a2);cursor:pointer;padding:0;flex:0 0 auto}
.a3d-rmin:hover{background:var(--pp-hover,rgba(255,255,255,.06));color:var(--pp-text,#fff)}
.a3d-rmin svg{width:15px;height:15px;transition:transform .15s ease}
body.a3d-rmin #a3d-right{width:42px!important;min-width:42px}
body.a3d-rmin #a3d-right #a3d-propsbody,body.a3d-rmin .a3d-rgrip{display:none}
body.a3d-rmin #a3d-right .a3d-palhd{font-size:0;justify-content:center;padding:10px 0;border-bottom:0}
body.a3d-rmin .a3d-rmin svg{transform:rotate(180deg)}"""

rep("""body.light-theme .a3d-ptabbtn.on{background:#fff;color:#111}""", CSS)

UI = r"""  /* __acad3dV147: the right panel's width and its minimised state, remembered */
  var BIM_RIGHT_KEY='acad3dRightPanel',BIM_RIGHT_MIN=240,BIM_RIGHT_MAX=560;
  function bimRightPrefs(){try{var v=JSON.parse(localStorage.getItem(BIM_RIGHT_KEY)||'null');return v&&typeof v==='object'?v:{};}catch(eR){return {};}}
  function bimRightSave(p){try{localStorage.setItem(BIM_RIGHT_KEY,JSON.stringify(p));}catch(eW){}}
  function bimRightDesktop(){return (window.innerWidth||0)>900;}
  function bimRightApply(){
    var rp=document.getElementById('a3d-right'),p=bimRightPrefs();
    if(!rp)return null;
    document.body.classList.toggle('a3d-rmin',!!p.min);
    var w=isFinite(p.w)?Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,p.w)):null;
    rp.style.width=(w&&bimRightDesktop()&&!p.min)?w+'px':'';
    var b=document.getElementById('a3d-rminbtn');
    if(b){b.setAttribute('aria-pressed',p.min?'true':'false');b.title=p.min?'Show the Properties panel':'Minimise the Properties panel';}
    return {w:rp.getBoundingClientRect().width,min:!!p.min};
  }
  function bimRightSetWidth(w){
    var p=bimRightPrefs();p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,w)));bimRightSave(p);
    var r=bimRightApply();try{size();paint();}catch(eS){}
    return r;
  }
  function bimRightToggleMin(on){
    var p=bimRightPrefs();p.min=on===undefined?!p.min:!!on;bimRightSave(p);
    var r=bimRightApply();try{size();paint();}catch(eS){}
    return r;
  }
  function bimRightWire(rp,sec){
    if(!rp||rp.querySelector('.a3d-rgrip'))return;
    var g=document.createElement('div');g.className='a3d-rgrip';g.title='Drag to resize';g.setAttribute('aria-hidden','true');
    rp.insertBefore(g,rp.firstChild);
    var hd=sec&&sec.querySelector('.a3d-palhd');
    if(hd&&!document.getElementById('a3d-rminbtn')){
      var b=document.createElement('button');b.type='button';b.id='a3d-rminbtn';b.className='a3d-rmin';b.setAttribute('aria-label','Minimise the Properties panel');
      b.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 6l6 6-6 6"/></svg>';
      b.addEventListener('click',function(){bimRightToggleMin();});
      hd.appendChild(b);
    }
    g.addEventListener('mousedown',function(ev){
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
    window.addEventListener('resize',function(){bimRightApply();});
    bimRightApply();
  }
"""

rep("""  /* ================= __acad3dV138: verify the survey ================= */""",
    UI + """  /* ================= __acad3dV138: verify the survey ================= */""")
rep("""        rightPane.appendChild(propsSec);
        document.body.classList.add('a3d-props-right');
      }""", """        rightPane.appendChild(propsSec);
        document.body.classList.add('a3d-props-right');
      }
      try{bimRightWire(rightPane,propsSec);}catch(eRw){console.warn('[BIM] The Properties panel could not be made resizable.',eRw);}   /* __acad3dV147 */""")

# long lists: Show all
rep("""  var A3D_HIST_OPEN={},A3D_HIST_MSG='';""", """  var A3D_HIST_OPEN={},A3D_HIST_MSG='',A3D_HIST_ALL=false;   /* __acad3dV147: Show all */""")
rep("""    }).join('')+(d.length>max?'<div class="a3d-histmore">and '+(d.length-max)+' more</div>':'');
  }""", """    }).join('')+(d.length>max?'<div class="a3d-histmore"><button type="button" data-histact="all">Show all '+d.length+'</button></div>':'');
  }""")
rep("""      r+='<div class="a3d-histchg" data-histchanges>'+bimHistListHtml(d,20)+'</div>';""",
    """      r+='<div class="a3d-histchg" data-histchanges>'+bimHistListHtml(d,A3D_HIST_ALL?d.length:12)+'</div>';""")
rep("""    if(k.indexOf('show:')===0){""", """    if(k==='all'){A3D_HIST_ALL=true;refreshProps();return true;}   /* __acad3dV147 */
    if(k.indexOf('show:')===0){""")
rep("""    if(r.error){a3dToast(r.error);return r;}
    A3D_HIST_MSG='';""", """    if(r.error){a3dToast(r.error);return r;}
    A3D_HIST_MSG='';A3D_HIST_ALL=false;""")

rep("""  window.__a3dTerrainLegend=function(){""", """  window.__a3dRightPanel=function(){var r=bimRightApply();return r;};   /* __acad3dV147 */
  window.__a3dRightSetWidth=function(w){return bimRightSetWidth(w);};
  window.__a3dRightToggleMin=function(on){return bimRightToggleMin(on);};
  window.__a3dTerrainLegend=function(){""")
rep("""  var BIM_APP_VERSION={v:'V146',date:'2026-10-04'};   /* __acad3dV146 */""", """  var BIM_APP_VERSION={v:'V147',date:'2026-10-04'};   /* __acad3dV147 */""")
rep("""  window.__acad3dV146='""", """  window.__acad3dV147='paneltokens,sentencecase,rowgrid,inputstyle,buttonstyle,typeheader,showall,resizable,minimise,lightdark';
  window.__acad3dV146='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
