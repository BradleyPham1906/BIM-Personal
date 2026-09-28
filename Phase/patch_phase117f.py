"""patch_phase117f.py -- V117: one test for "this key belongs to the focused control", which knows a
dropdown. Found while moving Delete behind the engine's gates: the field gate the key now sits behind
did not count a <select> as a field. Measured on V116 and V117 alike: with the wall's Type dropdown
in Properties focused, ArrowDown moved the WALL a metre and left the dropdown where it was, and Delete
erased the wall. Four copies of the test existed; the sheet's had SELECT, the other three did not.
One predicate now, used by all four: a dropdown owns its plain keys -- arrows step its options,
letters find one -- and leaves Ctrl shortcuts and function keys to the app, so Ctrl+Z still undoes
the type change it just made."""
NAME = 'patch_phase117f.py'
BASE = '3be31845466b388994ef097d7ac2728ed2dc43264cd36499c4613bce0c718c0b'
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

rep("  function bimSheetKey(ev){\n"
    "    var tg=ev.target;\n"
    "    if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.tagName==='SELECT'||tg.isContentEditable))return false;\n",
    r'''  /* __acad3dV117: the one test for "this key belongs to the focused control, not to the model". There
     were four copies of it: this handler's had SELECT, the engine's key handler (twice) and the key
     claim hook did not, so with a Properties dropdown focused, ArrowDown moved the selected object a
     metre instead of stepping the dropdown, and Delete erased it. A text field owns every key -- its
     Ctrl+Z is its own text undo. A dropdown owns its plain keys -- arrows step its options, letters
     find one -- but has no use for Ctrl shortcuts or function keys, so those stay the app's, and
     Ctrl+Z still undoes the type change the dropdown just made. */
  function bimKeyForControl(ev){
    var tg=ev&&ev.target;
    if(!tg)return false;
    if(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable)return true;
    if(tg.tagName==='SELECT')return !(ev.ctrlKey||ev.metaKey||/^F\d+$/.test(ev.key));
    return false;
  }
  function bimSheetKey(ev){
    if(bimKeyForControl(ev))return false;   /* __acad3dV117 */
''')
rep("      var tg0=ev.target;\n"
    "      if(!(tg0&&(tg0.tagName==='INPUT'||tg0.tagName==='TEXTAREA'||tg0.isContentEditable))&&bimGizmoTypeKey(ev)){\n",
    "      if(!bimKeyForControl(ev)&&bimGizmoTypeKey(ev)){   /* __acad3dV117 */\n")
rep("    var tg=ev.target;\n"
    "    if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable))return;\n",
    "    if(bimKeyForControl(ev))return;   /* __acad3dV117: the one test, which knows a dropdown */\n")
rep("      var tg=ev.target;\n"
    "      if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable))return false;\n",
    "      if(bimKeyForControl(ev))return false;   /* __acad3dV117 */\n")

# no copy of the test is left anywhere in script -- the class, not the four instances
code = re.sub(r'<style\b[^>]*>.*?</style>', '', t, flags=re.S | re.I)
code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
# The gates' test is the disjunction. A dialog's "Enter in a textarea is a newline" and the level
# list's "a click on its name field is not a click on the level" are different questions, and stay.
if code.count("tagName==='INPUT'||") != 1:
    sys.exit('ABORT: a copy of the field test is left: %d' % code.count("tagName==='INPUT'||"))
uses = code.count('bimKeyForControl(ev)') - code.count('function bimKeyForControl(ev)')
if uses != 4:
    sys.exit('ABORT: bimKeyForControl is not used by all four: %d' % uses)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
