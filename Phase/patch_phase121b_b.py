"""patch_phase121b_b.py -- V121b: the interface theme, under the app's own name, put back at start.

The eighth canvas-era entry is canvas-theme. The Appearance menu (V83) writes Light or Dark under it,
"the same key the app's own theme button has always used, so the two agree" -- the whiteboard's
theme button, which also read the key back at start. V114 took the whiteboard's start-up out, and
nothing has read the key since: a light interface has gone dark again on every reload, while the
menu went on saving the choice.

The theme is kept as acad3dTheme now, one of the app's own names, written by the menu and read at
every start. A value still under canvas-theme is carried over once -- the owner's last choice is not
lost -- and the old name removed. A theme that cannot be saved says so instead of failing silently."""
NAME = 'patch_phase121b_b.py'
BASE = '7a719814488cd5fd9e002d148db44debc8c1cf00150adf9b915e9aed710118a5'
import re
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
rep("  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();\n", r"""  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();
  /* __acad3dV121b: the interface theme, the Appearance menu's Light or Dark, kept under the app's own
     name and put back at every start. The menu wrote 'canvas-theme', which nothing has read since
     V114 took the old canvas's start-up out; a value still there is carried over once and the old
     name removed. */
  var A3D_THEME_KEY='acad3dTheme';
  function bimThemeStore(light){
    try{localStorage.setItem(A3D_THEME_KEY,light?'light':'dark');}
    catch(eT){console.warn('[BIM] The interface theme could not be saved to browser storage.',eT);a3dToast('The interface theme could not be saved in this browser');}
  }
  function bimThemeRestore(){
    var v=null,old=null;
    try{
      v=localStorage.getItem(A3D_THEME_KEY);
      old=localStorage.getItem('canvas-theme');
      if(old!==null){
        if(v===null&&(old==='light'||old==='dark')){v=old;localStorage.setItem(A3D_THEME_KEY,v);}
        localStorage.removeItem('canvas-theme');
      }
    }catch(eR){console.warn('[BIM] The interface theme could not be read from browser storage.',eR);}
    if(v==='light'||v==='dark')document.body.classList.toggle('light-theme',v==='light');
    return v;
  }
  var A3D_THEME_AT_START=bimThemeRestore();
""")
rep("""        document.body.classList.toggle('light-theme',light);
        // the same key the app's own theme button has always used, so the two agree
        try{localStorage.setItem('canvas-theme',light?'light':'dark');}catch(eL){}
""", """        document.body.classList.toggle('light-theme',light);
        bimThemeStore(light);   /* __acad3dV121b: under the app's own name, and read back at every start */
""")
rep("  window.__a3dCanvasCleared=function(){return {removed:A3D_CANVAS_CLEARED.slice(),names:A3D_CANVAS_KEYS.slice()};};\n",
    "  window.__a3dCanvasCleared=function(){return {removed:A3D_CANVAS_CLEARED.slice(),names:A3D_CANVAS_KEYS.slice()};};\n"
    "  window.__a3dThemeAtStart=function(){return A3D_THEME_AT_START;};   /* __acad3dV121b */\n")

code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
if len(re.findall(r"setItem\('canvas-theme'", code)):
    sys.exit('ABORT: the theme is still written under the old name')
if code.count("'canvas-theme'") != 2:
    sys.exit('ABORT: the old theme name is used besides the carry-over (%d)' % code.count("'canvas-theme'"))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
