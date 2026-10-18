"""patch_phase166f.py -- V166b: the left panel's width by one press, as well as by its edge.

  WCAG 2.2's 2.5.7 (Dragging Movements) asks that what a drag does can be done by a single pointer
  without dragging, and its 2.5.8 (Target Size, Minimum) excepts a small target when an equivalent
  control meets 24 by 24 px. The edge is 6 px (12 px for a finger); this button, 30 px, beside the
  panel's collapse, widens the panel a step at a time -- 242, 320, 400, 480, 560 within what the
  screen allows -- and from the widest back to 242. A computer's, as the edge is.
  The collapse beside it was white on the light theme's white header; it is the button's grey now.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '0d4eef927fd6d35ae7e2a1c92c76b13c545ba2ccec95adeb29e8e65f85590c4d'   # after patch_phase166e.py

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')
assert 'function bimLeftWire(sh){' in txt, 'run patch_phase166e.py first'


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- the button, beside the collapse ----
rep("""      '<button type="button" class="a3d-panelcollapse" data-toggle title="Collapse the panel">\\u2039</button></div>'+""",
    """      '<div class="a3d-projbtns"><button type="button" class="a3d-lpwbtn" data-lpwidth="1">'+   /* __acad3dV166b: the width, by one press */
      '<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M2.5 9h13M5.5 6 2.5 9l3 3M12.5 6l3 3-3 3"/></svg></button>'+
      '<button type="button" class="a3d-panelcollapse" data-toggle title="Collapse the panel">\\u2039</button></div></div>'+""")
rep("""      var mo=ev.target&&ev.target.closest?ev.target.closest('[data-railmore]'):null;   /* __acad3dV149 */
      if(mo){bimShellMore();return;}
""", """      var mo=ev.target&&ev.target.closest?ev.target.closest('[data-railmore]'):null;   /* __acad3dV149 */
      if(mo){bimShellMore();return;}
      if(ev.target&&ev.target.closest&&ev.target.closest('[data-lpwidth]')){bimLeftStep();return;}   /* __acad3dV166b */
""")
rep(""".a3d-panelcollapse:hover{background:rgba(255,255,255,.08)}
""", """.a3d-panelcollapse:hover{background:rgba(255,255,255,.08)}
/* __acad3dV166b: the panel's width, by one press; a computer's, as its edge is */
.a3d-projbtns{display:flex;align-items:center;gap:2px}
.a3d-lpwbtn{width:30px;height:30px;border:0;border-radius:8px;background:transparent;color:#9aa3ad;cursor:pointer;display:grid;place-items:center;padding:0}
.a3d-lpwbtn:hover{background:rgba(255,255,255,.08);color:#fff}
.a3d-lpwbtn svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
body.a3d-tier-overlay .a3d-lpwbtn{display:none}
body.light-theme .a3d-lpwbtn{color:#6b7280}
body.light-theme .a3d-lpwbtn:hover{background:rgba(0,0,0,.06);color:#111}
/* and the collapse beside it, white on the light theme's white header until now */
body.light-theme .a3d-panelcollapse{color:#6b7280}
body.light-theme .a3d-panelcollapse:hover{background:rgba(0,0,0,.06);color:#111}
@media(pointer:coarse){.a3d-lpwbtn{width:36px;height:36px}}
""")
# ---- the steps; the button says where it goes ----
rep("""  function bimLeftState(){""", """  /* the next width up, within what the screen allows; from the widest, back to the narrowest */
  var BIM_LEFT_STEPS=[242,320,400,480,560];
  function bimLeftNext(){
    var w=bimLeftW(),mx=bimLeftMax(),i;
    for(i=0;i<BIM_LEFT_STEPS.length;i++)if(BIM_LEFT_STEPS[i]>w&&BIM_LEFT_STEPS[i]<=mx)return BIM_LEFT_STEPS[i];
    return w<mx?mx:BIM_LEFT_MIN;
  }
  function bimLeftStep(){return bimLeftSetWidth(bimLeftNext());}
  function bimLeftState(){""")
rep("""      if(g){g.setAttribute('aria-valuenow',String(w));g.setAttribute('aria-valuemin',String(BIM_LEFT_MIN));g.setAttribute('aria-valuemax',String(bimLeftMax()));}
""", """      if(g){g.setAttribute('aria-valuenow',String(w));g.setAttribute('aria-valuemin',String(BIM_LEFT_MIN));g.setAttribute('aria-valuemax',String(bimLeftMax()));}
      var b=document.querySelector('#a3d-leftpanel [data-lpwidth]'),nx=bimLeftNext();
      if(b){b.setAttribute('aria-label','Panel width '+w+' px: '+(nx>w?'widen to '+nx:'back to '+nx));b.title=b.getAttribute('aria-label');}
""")
rep("""      grip:!!(g&&getComputedStyle(g).display!=='none'),tier:A3D_SHELL_TIER,""", """      grip:!!(g&&getComputedStyle(g).display!=='none'),next:bimLeftNext(),tier:A3D_SHELL_TIER,""")
# the shell's audit knows it
rep("""    {sel:'.a3d-panelcollapse',why:'collapses the rail'},
""", """    {sel:'.a3d-panelcollapse',why:'collapses the rail'},
    {sel:'[data-lpwidth]',why:'widens the panel a step at a time: its edge, by one press'},   /* __acad3dV166b */
""")
rep("""leftresize,leftremembered,leftreset,leftkeys,leftclamp,leftdesktop';""", """leftresize,leftremembered,leftreset,leftkeys,leftclamp,leftdesktop,leftstep';""")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('patch_phase166f applied:', hashlib.sha256(out).hexdigest(), len(out))
