"""patch_phase117c.py -- V117 the rest of the 2D wire shell, part 3: the Delete key moves into the BIM
engine. The engine's Delete was never its own: the whiteboard shell's section 6 listened for Delete on
the document and called window.__ws3Del, and the engine wrapped that function to erase its selection.
Deleting section 6 alone takes the key with it -- measured, the V101 and V102 suites fail -- and the
detour ran outside every one of the engine's key gates, so two leaks were measured on the V116 build:
with the Start page showing, Delete erased the selection of the project behind it; with a dialog open
and the focus off its fields, Backspace erased the object the dialog sat over. The key now lives in
the engine's own handler, behind those gates, and both hooks go."""
NAME = 'patch_phase117c.py'
BASE = '247c1a3e83705817ad3e7ba43efd9a1c9930352d0ee05f7146568d2a0c3d60d5'
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
import re

# ---- 1. the whiteboard shell's Delete listener -------------------------------------------------------------
span("  // ============ 6. DELETE KEY FOR CAD SHAPES ============\n", "  }catch(err){ window.__ws2Err=String(err&&err.stack||err); }\n",
     r'''  /* __acad3dV117: section 6, a Delete-key listener over whiteboard wires, is gone. It read the
     whiteboard's state object, deleted in V113c, and the BIM engine's own Delete rode on it: the
     engine wrapped the window.__ws3Del this listener called. The key is the engine's now, in its own
     handler. */

''', 31)

# ---- 2. the engine's wrapper of it ---------------------------------------------------------------------------
rep("  var prevDel=window.__ws3Del;\n"
    "  window.__ws3Del=function(){\n"
    "    if(A3D.on){\n"
    "      if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();   /* __acad3dV98 */\n"
    "      return true;\n"
    "    }\n"
    "    return prevDel?prevDel():false;\n"
    "  };\n", "")

# ---- 3. the key, in the engine's own handler, behind its gates ------------------------------------------------
rep("    var o=null,i;\n"
    "    if(A3D.sel)for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===A3D.sel)o=A3D.objs[i];\n"
    "    if(!o)return;\n"
    "    var nudged=bimNudgeObject(o,ev.key);\n",
    r'''    /* __acad3dV117: Delete -- and Backspace, the delete key of a Mac keyboard -- erases the selection.
       It used to arrive here the long way round: the whiteboard shell's document listener called
       window.__ws3Del, which this engine wrapped. That ran after this handler had returned, outside
       every gate above, and two leaks were measured: with the Start page showing, Delete erased the
       selection of the project behind it; with a dialog open and the focus off its fields, Backspace
       erased the object the dialog sat over. Here it sits behind the gates -- the Start page, a
       sheet, a field, a gizmo value or a point being typed -- and it leaves an open dialog alone,
       as Ctrl+D does. Last before the nudge keys, where the old listener effectively ran. */
    if((ev.key==='Delete'||ev.key==='Backspace')&&!ev.ctrlKey&&!ev.metaKey){
      if(el.dlg)return;
      try{
        if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();   /* __acad3dV98's test */
      }catch(eDel){console.warn('[BIM] Delete failed.',eDel);a3dToast('Could not delete the selection');}
      ev.preventDefault();ev.stopImmediatePropagation();return;
    }
    var o=null,i;
    if(A3D.sel)for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].id===A3D.sel)o=A3D.objs[i];
    if(!o)return;
    var nudged=bimNudgeObject(o,ev.key);
''')

# ---- the checks: code only, since the comments that say what went name it on purpose -------------------------
code = re.sub(r'<style\b[^>]*>.*?</style>', '', t, flags=re.S | re.I)
code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
if '__ws3Del' in code:
    sys.exit('ABORT: something still calls or defines __ws3Del')
seg = t[t.index('(function acadWs2V1(){'):]
seg = seg[:seg.index('})();')]
seg = re.sub(r'/\*.*?\*/', '', seg, flags=re.S)
seg = re.sub(r'(?m)^\s*//.*$', '', seg)
for dead in ('state.', 'deleteSelected', 'renderAll', "addEventListener('keydown'"):
    if dead in seg:
        sys.exit('ABORT: acadWs2V1 still has ' + dead)
k = t.index('  function onKey(ev){\n')
body = t[k:t.index('\n  }\n', k)]
g = [body.index(x) for x in ("if(bimStartShowing())return;", "if(bimSheetOnScreen()&&bimSheetKey(ev))return;",
                             "if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable))return;",
                             "if((ev.key==='Delete'||ev.key==='Backspace')&&!ev.ctrlKey&&!ev.metaKey){")]
if g != sorted(g):
    sys.exit('ABORT: the Delete branch is not behind the Start, sheet and field gates: %r' % g)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
