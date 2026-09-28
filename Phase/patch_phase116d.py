"""patch_phase116d.py -- V116 Model and layout tabs, part 4: the shell. The canvas-era Model / Layout
strip is deleted with its paper overlay and styles: it kept its own list of "layouts" per whiteboard
drawing, drew whiteboard wires on them through a state object that no longer exists, and the BIM
engine hid it on entry, so it was never on screen. The Start page thumbnails it shared helpers with
go too -- they looked for cards the Start page stopped drawing in V114, under a MutationObserver on the
whole document. LAYOUT, MODEL, MSPACE and PSPACE join the command line."""
NAME = 'patch_phase116d.py'
BASE = '697fb68e4f9a93c09febd926779dca469e10bcf97e56b01b3b01ad8f5a06ec3e'
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

span("/* Start screen previews */\n", "/* Workspace dropdown */\n", "", 2)
span("/* Model / Layout tabs strip */\n", "</style>\n<script>\n(function acadWs2V1(){\n", "", 15)
span("  // ============ 3. START SCREEN PREVIEWS ============\n", "  // ============ 4. WORKSPACE DROPDOWN ============\n",
     r'''  /* __acad3dV116: section 3, the Start page's wire thumbnails, is gone. It looked for cards the Start
     page stopped drawing in V114, under a MutationObserver on the whole document. */
''', 49)
span("  // ============ 5. MODEL / LAYOUT TABS + PAPER SPACE ============\n", "  // ============ 6. DELETE KEY FOR CAD SHAPES ============\n",
     r'''  /* __acad3dV116: section 5, the canvas-era Model / Layout strip, is gone. It kept its own list of
     "layouts" per whiteboard drawing in localStorage ('acadLayoutsV1', left where it is, unread) and
     drew whiteboard wires on them, and the BIM engine hid it on entry -- it was never on screen. The
     layout tabs are the BIM engine's now, drawn from the project's sheets in the status bar. */
''', 87)
rep("  var BIM_2D_CHROME_IDS=['acad-status','acad-mltabs'];\n",
    "  var BIM_2D_CHROME_IDS=['acad-status'];   /* __acad3dV116: the canvas-era layout strip's id went with the strip */\n")
for dead in ('acad-mltabs', 'acad-layout', 'drawWiresToCanvas', 'addStartThumbs', '__ws2Space', 'st-thumb', 'al-paper', 'ml-plus'):
    if dead in t:
        sys.exit('ABORT: a leftover of the canvas-era strip is still referenced: ' + dead)

rep("    ['REDO',[],'redo','Redo what was undone']\n  ];\n",
    "    ['REDO',[],'redo','Redo what was undone'],\n"
    "    /* __acad3dV116: the layout commands */\n"
    "    ['LAYOUT',['NEWSHEET'],'newSheet','New sheet, opened on its own layout tab'],\n"
    "    ['MODEL',[],'modelTab','Back to the Model tab'],\n"
    "    ['MSPACE',['MS'],'mspace','Work in the model through a viewport on this sheet'],\n"
    "    ['PSPACE',['PS'],'pspace','Back to paper space on this sheet']\n  ];\n")
seg = t[t.index('  var CADCMDS=['):]
seg = seg[:seg.index('\n  ];\n')]
keys = []
for n, al in re.findall(r"\['([A-Z0-9?]+)',\[([^\]]*)\],'", seg):
    keys.append(n)
    keys += re.findall(r"'([^']+)'", al)
if len(keys) != len(set(keys)) or len(keys) != 206 + 7:
    sys.exit('ABORT: command names and aliases are not unique (%d, %d distinct)' % (len(keys), len(set(keys))))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
