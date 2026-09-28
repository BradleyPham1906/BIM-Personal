"""patch_phase119b.py -- V119: the left rail, in the clean style of the owner's reference (Rayon).

Icons only, in one quiet grey, with the panel's name on hover; the open panel is marked by a soft
rounded square rather than a blue slab, and the utility stack below takes the same mark. The tab that
was labelled "File" is the Project Browser -- that is what it opens -- and says so, with a tree icon.
Every rail button keeps an accessible name, now from aria-label and title rather than a caption."""
NAME = 'patch_phase119b.py'
BASE = 'b11016ab2d0561016631806d02ac7e449a2286746d3e127f09f5b2de6eea86c0'
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
rep("#figma-layers-rail .fl-rail-btn{width:40px;height:46px;border:0;border-radius:9px;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;font-size:9.5px;font-weight:850;cursor:pointer;line-height:1}",
    "/* __acad3dV119: icon-only rail buttons in one quiet grey; the name is on hover */"
    "#figma-layers-rail .fl-rail-btn{width:36px;height:36px;border:0;border-radius:8px;background:transparent;display:grid;place-items:center;cursor:pointer;color:#9aa3ad}")
rep("#figma-layers-rail .fl-rail-btn svg{width:17px;height:17px;stroke:currentColor;fill:none;stroke-width:1.8}",
    "#figma-layers-rail .fl-rail-btn svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.6}")
rep("#figma-layers-rail .fl-rail-btn:hover{background:rgba(255,255,255,.08)}",
    "#figma-layers-rail .fl-rail-btn:hover{background:rgba(255,255,255,.08);color:#fff}")
rep("#figma-layers-rail .fl-rail-btn.active{background:#2c477d;color:#e4efff}",
    "#figma-layers-rail .fl-rail-btn.active{background:rgba(255,255,255,.12);color:#fff}")
rep("body.light-theme #figma-layers-rail button{color:#222}",
    "body.light-theme #figma-layers-rail button{color:#222}"
    "body.light-theme #figma-layers-rail .fl-rail-btn{color:#6b7280}"
    "body.light-theme #figma-layers-rail .fl-rail-btn:hover{background:rgba(0,0,0,.06);color:#111}"
    "body.light-theme #figma-layers-rail .fl-rail-btn.active{background:rgba(0,0,0,.09);color:#111}")
rep(".a3d-ru.on{background:#2c477d;color:#e4efff}",
    ".a3d-ru.on{background:rgba(255,255,255,.12);color:#fff}")

rep("    file:'<path d=\"M5 2.5h5l3 3V15H5z\"/><path d=\"M10 2.5v3h3\"/>',\n",
    "    /* __acad3dV119: the Project Browser's icon is a tree -- what the panel is -- not a page */\n"
    "    browser:'<rect x=\"2.5\" y=\"2.5\" width=\"5\" height=\"3.5\" rx=\"1\"/><rect x=\"9.5\" y=\"7.2\" width=\"6\" height=\"3.2\" rx=\"1\"/>"
    "<rect x=\"9.5\" y=\"12.3\" width=\"6\" height=\"3.2\" rx=\"1\"/><path d=\"M5 6v7.9h4.5M5 8.8h4.5\"/>',\n")
rep("      '<button type=\"button\" class=\"fl-rail-btn active\" data-tab=\"file\" data-fl-tab=\"file\" title=\"Project Browser\">'+\n"
    "      bimRailIcon('file')+'<span>File</span></button>'+\n",
    "      '<button type=\"button\" class=\"fl-rail-btn active\" data-tab=\"file\" data-fl-tab=\"file\" title=\"Project Browser\" aria-label=\"Project Browser\">'+\n"
    "      bimRailIcon('browser')+'</button>'+   /* __acad3dV119: icon only; the tab's id stays 'file' until the id rename */\n")
rep("      '<button type=\"button\" class=\"fl-rail-btn\" data-tab=\"assets\" data-fl-tab=\"assets\" title=\"Families, materials, wall types and patterns\">'+\n"
    "      bimRailIcon('assets')+'<span>Assets</span></button>'+\n",
    "      '<button type=\"button\" class=\"fl-rail-btn\" data-tab=\"assets\" data-fl-tab=\"assets\" title=\"Assets\" aria-label=\"Assets\">'+\n"
    "      bimRailIcon('assets')+'</button>'+\n")
rep("    {sel:'.fl-rail-btn[data-tab=\"file\"]',why:'File tab: the BIM Project Browser'},\n",
    "    {sel:'.fl-rail-btn[data-tab=\"file\"]',why:'Project Browser tab'},\n")
rep("#figma-layers-rail .fl-logo:hover{background:rgba(255,255,255,.08)}",
    "#figma-layers-rail .fl-logo{color:#9aa3ad}#figma-layers-rail .fl-logo svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.6}"
    "#figma-layers-rail .fl-logo:hover{background:rgba(255,255,255,.08);color:#fff}"
    "body.light-theme #figma-layers-rail .fl-logo{color:#6b7280}body.light-theme #figma-layers-rail .fl-logo:hover{background:rgba(0,0,0,.06);color:#111}")
rep("    logo:'<circle cx=\"7\" cy=\"4\" r=\"2.2\"/><circle cx=\"13\" cy=\"4\" r=\"2.2\"/><circle cx=\"7\" cy=\"10\" r=\"2.2\"/><circle cx=\"13\" cy=\"10\" r=\"2.2\"/><circle cx=\"7\" cy=\"16\" r=\"2.2\"/>',\n",
    "    /* __acad3dV119: the top button shows and hides the panel, and now looks like it: a sidebar */\n"
    "    panel:'<rect x=\"2.5\" y=\"3\" width=\"13\" height=\"12\" rx=\"2\"/><path d=\"M7 3v12\"/>',\n")
rep("title=\"Collapse the panel\">'+bimRailIcon('logo')+'</button>'",
    "title=\"Show or hide the panel\" aria-label=\"Show or hide the panel\">'+bimRailIcon('panel')+'</button>'")
if "bimRailIcon('logo')" in t:
    sys.exit('ABORT: the old dot icon is still used')
if "bimRailIcon('file')" in t:
    sys.exit('ABORT: the old page icon is still used')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
