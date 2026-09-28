"""patch_phase118d.py -- V118: an open dialog owns the keyboard, by one gate instead of seven checks.
V117's class, met again while probing this one. Seven of the engine's key branches each checked for
an open dialog; the nudge keys and Undo / Redo did not. Measured on V117: with the Box dialog open and
the focus off its fields, ArrowDown and PageUp moved the selected column a metre each; with the Linear
Array dialog open, Ctrl+Z undid the column's creation, and the dialog's OK then reported "unsupported
object type(s)". One gate now, right after the field test: while a dialog is open only Escape, which
closes it, and the function keys, which set drawing aids, reach past it. Six of the seven checks go;
Escape's stays, closing the dialog being what it does."""
NAME = 'patch_phase118d.py'
BASE = 'ca373924beeb66fa6bc6718c456b504b2e7f20f0650d0be3ee96378f97041e33'
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
rep("    if(bimKeyForControl(ev))return;   /* __acad3dV117: the one test, which knows a dropdown */\n",
    "    if(bimKeyForControl(ev))return;   /* __acad3dV117: the one test, which knows a dropdown */\n"
    r'''    /* __acad3dV118: an open dialog owns the keyboard. Only Escape, which closes it, and the function
       keys, which set drawing aids, reach past it. Seven branches below used to check for a dialog
       one by one and the nudge keys and Undo / Redo did not: with the focus off a dialog's fields,
       ArrowDown moved the selected object behind it a metre, and Ctrl+Z undid the object a dialog
       was about to act on. One gate, so a branch added later cannot forget it. */
    if(el.dlg&&ev.key!=='Escape'&&!/^F\d+$/.test(ev.key))return;
''')
rep("    if(A3D.sk&&BIM_COORD_TOOLS[A3D.sk.tool]&&!el.dlg){\n",
    "    if(A3D.sk&&BIM_COORD_TOOLS[A3D.sk.tool]){\n")
rep("    if((ev.ctrlKey||ev.metaKey)&&(ev.key==='d'||ev.key==='D')&&!el.dlg){\n",
    "    if((ev.ctrlKey||ev.metaKey)&&(ev.key==='d'||ev.key==='D')){\n")
rep("    if((ev.ctrlKey||ev.metaKey)&&(ev.key==='s'||ev.key==='S')&&!el.dlg){\n",
    "    if((ev.ctrlKey||ev.metaKey)&&(ev.key==='s'||ev.key==='S')){\n")
rep("    if((ev.ctrlKey||ev.metaKey)&&!ev.shiftKey&&(ev.key==='o'||ev.key==='O')&&!el.dlg){   /* __acad3dV115: OPEN */\n",
    "    if((ev.ctrlKey||ev.metaKey)&&!ev.shiftKey&&(ev.key==='o'||ev.key==='O')){   /* __acad3dV115: OPEN */\n")
rep("    if((ev.key==='Enter'||ev.key===' ')&&!A3D.sk&&!el.dlg&&!A3D.conPick&&A3D.lastCmd){\n",
    "    if((ev.key==='Enter'||ev.key===' ')&&!A3D.sk&&!A3D.conPick&&A3D.lastCmd){\n")
rep("      if(el.dlg)return;\n      try{\n        if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();",
    "      try{\n        if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();")
rep("       sheet, a field, a gizmo value or a point being typed -- and it leaves an open dialog alone,\n"
    "       as Ctrl+D does. Last before the nudge keys, where the old listener effectively ran. */\n",
    "       sheet, a field, a gizmo value or a point being typed, and an open dialog (one gate since\n"
    "       V118). Last before the nudge keys, where the old listener effectively ran. */\n")
k = t.index('  function onKey(ev){\n')
body = t[k:t.index('\n  }\n', k)]
import re
code = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
n = code.count('el.dlg')
if n != 2:   # the gate, and Escape closing the dialog
    sys.exit('ABORT: onKey should test for a dialog in two places, the gate and Escape; found %d' % n)
if body.index("if(el.dlg&&ev.key!=='Escape'") > body.index("if(A3D.sk&&BIM_COORD_TOOLS[A3D.sk.tool]){"):
    sys.exit('ABORT: the dialog gate is not ahead of the first branch that edits the model')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
