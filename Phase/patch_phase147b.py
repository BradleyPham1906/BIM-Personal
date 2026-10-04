"""patch_phase147b.py -- V147: the right panel on a phone, a tablet and a computer.

- Phone (the compact tier, up to 720 px wide or 500 px high): Properties is a bottom sheet, the
  width of the screen, 62% of its height, with a grab bar that raises it to 92% and back.
- Tablet (721-1024 px): a 340 px drawer from the right.
- A touch screen (pointer: coarse) of any size: inputs and buttons 36 px, rows 40 px, group
  headers easy to tap.
- The resize edge is a computer's only; on a phone or tablet the panel's arrow closes the sheet
  or drawer instead of minimising it."""
NAME = 'patch_phase147b.py'
BASE = '69aa59e5b9eb29c674b668151f06c3d8096ab78918ab8ffeceed0ad5499aea60'
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


CSS = r"""body.a3d-rmin .a3d-rmin svg{transform:rotate(180deg)}
/* __acad3dV147: a phone, a tablet, a finger */
.a3d-rsheetbar{display:none}
@media(max-width:1024px),(max-height:500px){.a3d-rgrip{display:none}}
@media(pointer:coarse){
#a3d-right input[type=text],#a3d-right input[type=number],#a3d-right input[type=search],#a3d-right select,#a3d-right textarea{min-height:36px;font-size:13px}
#a3d-right #a3d-propsbody button{min-height:36px;font-size:13px;padding:0 12px}
#a3d-right .a3d-prow{min-height:40px}
#a3d-right .a3d-plabel,#a3d-right .a3d-pstatic{font-size:12.5px}
#a3d-right .a3d-pgrp{padding:15px 0 9px;font-size:13px}
#a3d-right .a3d-pgcar{width:32px;height:32px}
#a3d-right input[type=checkbox]{width:20px;height:20px}
.a3d-rmin{width:36px;height:36px}
}
@media(min-width:721px) and (max-width:1024px) and (min-height:501px){
body.a3d-props-right #a3d-right{width:340px;max-width:85vw}
}
@media(max-width:720px),(max-height:500px){
body.a3d-props-right #a3d-right{position:fixed;z-index:9700;top:auto;left:0;right:0;bottom:0;width:auto;max-width:none;height:62vh;border-radius:14px 14px 0 0;border-left:0;box-shadow:0 -10px 30px rgba(0,0,0,.5);transition:height .18s ease}
body.a3d-props-right #a3d-right.a3d-rtall{height:92vh}
body.a3d-props-right #a3d-right .a3d-rsheetbar{display:flex;justify-content:center;align-items:center;height:22px;flex:0 0 auto;cursor:pointer;touch-action:none}
body.a3d-props-right #a3d-right .a3d-rsheetbar i{display:block;width:40px;height:5px;border-radius:3px;background:var(--pp-muted,#8f98a2);opacity:.6}
body.a3d-props-right #a3d-right .a3d-palhd{padding-top:4px}
}"""

rep("""body.a3d-rmin .a3d-rmin svg{transform:rotate(180deg)}""", CSS)
rep("""    document.body.classList.toggle('a3d-rmin',!!p.min);""",
    """    document.body.classList.toggle('a3d-rmin',!!p.min&&bimRightDesktop());   /* minimised is a computer's; a phone or tablet closes the panel */""")
rep("""      b.addEventListener('click',function(){bimRightToggleMin();});""",
    """      b.addEventListener('click',function(){
        if(!bimRightDesktop()){rp.classList.remove('open');rp.classList.remove('a3d-rtall');return;}   /* the sheet or drawer closes */
        bimRightToggleMin();
      });""")
rep("""    var g=document.createElement('div');g.className='a3d-rgrip';g.title='Drag to resize';g.setAttribute('aria-hidden','true');
    rp.insertBefore(g,rp.firstChild);""", """    var g=document.createElement('div');g.className='a3d-rgrip';g.title='Drag to resize';g.setAttribute('aria-hidden','true');
    rp.insertBefore(g,rp.firstChild);
    /* the phone's sheet: a grab bar that raises it and lowers it */
    var sb=document.createElement('div');sb.className='a3d-rsheetbar';sb.setAttribute('role','button');sb.setAttribute('aria-label','Raise or lower Properties');sb.innerHTML='<i></i>';
    sb.addEventListener('click',function(){rp.classList.toggle('a3d-rtall');});
    rp.insertBefore(sb,sec||null);""")
rep("""  window.__acad3dV147='paneltokens,""", """  window.__acad3dV147='phonesheet,tabletdrawer,touchtargets,paneltokens,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
