"""patch_phase120k.py -- V120: one stylesheet.

The CSS was five <style> elements: the base sheet in <head>, the engine's sheet after it (V120b),
and three more in <body> between the scripts -- the top bar's, the palette's and Start page's, and
the left panel's -- named acad-ribbon-css, acad-ws-css and acad-ws2-css after the modules that
first wrote them. They become one <style> in <head>, in the same order, so the cascade is the one
the five sheets had; tools/css_move_check.py compares every rule's cssText in a browser.

The rules are kept, reformatted to one per line. Their comments are rewritten: section headings in
place of the whiteboard's ("WHITEBOARD CARD + APPLE TOOLBAR", "Figma sidebar developed tabs",
"Rev component kit", five "--- from <bundle>.css ---" markers over nothing), the V62 epitaph for
a font bundle removed in V62, and the history of the dock the whiteboard owned. One rule goes with
them: .fl-help, the whiteboard's "A?" button, which V120i's rail pass stopped looking for, so no
string in the file can make it match any more."""
NAME = 'patch_phase120k.py'
BASE = '48f3cc8ef887ad751a66fc09c298f25e48e8435ad278a2a47e0708d50a249b68'
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
def css_items(css):
    """Top-level items of a stylesheet: ('comment', text) or ('rule', prelude, body) or
    ('at', prelude, [items]). Strings and comments are respected."""
    out, i, n = [], 0, len(css)
    while i < n:
        if css[i] in ' \t\n':
            i += 1; continue
        if css.startswith('/*', i):
            j = css.index('*/', i) + 2
            out.append(('comment', css[i:j])); i = j; continue
        # prelude up to '{'
        j, q = i, None
        while css[j] != '{':
            j += 1
        pre = css[i:j]
        # matching '}'
        k, depth = j, 0
        while True:
            c = css[k]
            if c in '"\'':
                k = css.index(c, k + 1)
            elif css.startswith('/*', k):
                k = css.index('*/', k) + 1
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        body = css[j + 1:k]
        if pre.strip().startswith('@'):
            out.append(('at', pre, css_items(body)))
        else:
            out.append(('rule', pre, body))
        i = k + 1
    return out


def one_line(s):
    return re.sub(r'\s*\n\s*', '', s).strip()


def norm_pre(p):
    return re.sub(r'\s+', ' ', p).strip()


def emit(items, notes, indent=''):
    """The items as text, one rule per line, a note from `notes` above the rule it is keyed to;
    the items' own comments are dropped."""
    lines = []
    for it in items:
        if it[0] == 'comment':
            continue
        pre = norm_pre(it[1])
        if pre in notes:
            lines.append(indent + notes.pop(pre))
        if it[0] == 'rule':
            lines.append(indent + pre + '{' + one_line(it[2]) + '}')
        else:
            lines.append(indent + pre + '{')
            lines.extend(emit(it[2], notes, indent + '  '))
            lines.append(indent + '}')
    return lines


def take(open_tag):
    """The body of the <style> element with this exact opening tag, removing the element."""
    global t
    c = t.count(open_tag)
    if c != 1:
        sys.exit('ABORT: %r found %d times' % (open_tag, c))
    s = t.index(open_tag)
    e = t.index('</style>', s)
    body = t[s + len(open_tag):e]
    end = e + len('</style>')
    if t[end:end + 1] == '\n':
        end += 1
    t = t[:s] + t[end:]
    return body


base = take('<style>\n  :root{')
base = '  :root{' + base
engine = take('<style id="a3d-css">\n')
ribbon = take('<style id="acad-ribbon-css">\n')
wscss = take('<style id="acad-ws-css">\n')
ws2 = take('<style id="acad-ws2-css">\n')

# .fl-help: the whiteboard's "A?" button; since V120i nothing in the file looks for it
if len(re.findall(r'(?<![\w-])fl-help(?![\w-])', t)) != 1 or base.count('.fl-help{') != 1:
    sys.exit('ABORT: .fl-help is referenced outside its own rule, or its rule is not there once')
base_items = [it for it in css_items(base) if not (it[0] == 'rule' and norm_pre(it[1]) == '.fl-help')]

NOTES_BASE = {
    ':root': "/* ---- the page ---- */",
    'body.light-theme svg text': "/* in the light theme, SVG text is haloed in the page colour so it reads over linework */",
    '#a3d-cmdpal': "\n/* ---- the command palette (Ctrl+K) ---- */",
    '#a3d-leftpanel .a3d-tabbody': "\n/* ---- the left shell: the rail, and the panel it opens ---- */",
    '#a3d-rail .a3d-railbtn': "/* __acad3dV119: icon-only rail buttons in one quiet grey; the name is on hover */",
}
NOTES_RIBBON = {
    ':root': ("\n/* ---- the top bar: the quick-access buttons and the project tabs. --acad-ribbon-h is its\n"
              "   height, which every surface below it is positioned against: 28 + 24 px, and 22 + 22 in\n"
              "   the compact tier. ---- */"),
    '.acad-doctab.dt-doc': "/* __acad3dV115: one tab per open project, each with its own close button */",
    'body.acad-on #a3d-shell': "/* the left shell starts below the top bar */",
    '@media(max-width:720px),(max-height:500px)': "/* the compact tier: a phone, or a short landscape window */",
}
NOTES_WS = {
    'body.acad-on #a3d-cmdpal': "/* the command palette opens below the top bar */",
    '#acad-start': "\n/* ---- the Start page ---- */",
    '#acad-start .st-card.st-has-del': "/* __acad3dV115: a closed project can be deleted from here */",
}
NOTES_WS2 = {
    'body.a3d-mode #a3d-leftpanel .a3d-projhead > div:first-child':
        "\n/* ---- the left panel in the BIM workspace. Its header names the project and the site (V80). ---- */",
    'body.a3d-tree-docked #a3d-leftpanel':
        "/* __acad3dV65: the Project Browser nested in the panel is a section of it, not a panel of its\n"
        "   own, and the panel is the one scroll container */",
    'body.a3d-tree-docked #a3d-shell[data-tab="browser"] #a3d-leftpanel > .a3d-tabbody':
        "/* the rail picks which section the panel shows: the Project Browser, or the Assets library */",
    'body.a3d-tree-docked #a3d-shell[data-tab="browser"] #a3d-leftpanel':
        "/* __acad3dV66: the Project Browser keeps its own scroll regions, so a large selection cannot\n"
        "   push it off screen */",
    'body.a3d-tree-docked #a3d-leftpanel > .a3d-tree .a3d-palhd':
        "/* __acad3dV66: section headers take the panel's quiet, inset treatment, and wrap, so every\n"
        "   action button stays reachable at any panel width */",
}

# the engine's sheet keeps its own comments; its heading and one stale comment change
ENGINE_HEAD = ("/* __acad3dV120: the BIM engine's stylesheet, moved out of the JavaScript string it was built from\n"
               "   at run time. It sits after the base stylesheet and before the shell's, where the runtime\n"
               "   element sat, so the cascade is unchanged. */\n")
if engine.count(ENGINE_HEAD) != 1:
    sys.exit('ABORT: the engine sheet heading is not the one V120b wrote')
engine = engine.replace(ENGINE_HEAD, "\n/* ---- the BIM engine (__acad3dV120: until V120 a string that buildUI() injected at run time) ---- */\n")
TABLET = ("""/* Tablet tier: between the compact phone/landscape rules above and full desktop sizing. The
       ribbon and model-tree still fit without collapsing into a drawer, but the desktop ribbon's
       104px-tall button rows and the tree's fixed 268px width are noticeably cramped alongside a
       narrower viewport -- shrink them proportionally instead of leaving a dead zone between the
       two existing tiers. */""")
if engine.count(TABLET) != 1:
    sys.exit('ABORT: the tablet-tier comment is not there once')
engine = engine.replace(TABLET, "/* the tablet tier: between the compact rules above and desktop sizing, the model tree narrows\n   rather than collapsing into a drawer */")

lines = ["/* __acad3dV120: one stylesheet, in the order its five predecessors cascaded: the page, the command",
         "   palette and the left shell; the BIM engine; the top bar, the Start page and the left panel. */"]
lines += emit(base_items, NOTES_BASE)
text = '\n'.join(lines) + '\n\n' + engine.strip('\n') + '\n'
text += '\n'.join(emit(css_items(ribbon), NOTES_RIBBON) + emit(css_items(wscss), NOTES_WS) + emit(css_items(ws2), NOTES_WS2)) + '\n'
for d in (NOTES_BASE, NOTES_RIBBON, NOTES_WS, NOTES_WS2):
    if d:
        sys.exit('ABORT: a note found no rule: %r' % list(d)[:3])
rep('<title>CAD/BIM workspace</title>\n</head>\n',
    '<title>CAD/BIM workspace</title>\n<style>\n' + text + '</style>\n</head>\n')
rep("    /* __acad3dV120: the engine's rules are the <style id=\"a3d-css\"> element at the end of <head>. */\n",
    "    /* __acad3dV120: the engine's rules are in the stylesheet in <head>. */\n")


def style_elements(t):
    n, i = 0, 0
    opener = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    low = t.lower()
    while True:
        m = opener.search(t, i)
        if not m:
            return n
        if m.group(0) == '<!--':
            i = t.index('-->', m.end()) + 3
            continue
        tag = m.group(1).lower()
        n += tag == 'style'
        i = low.index('</%s>' % tag, m.end()) + len(tag) + 3


if style_elements(t) != 1:
    sys.exit('ABORT: %d style elements' % style_elements(t))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
