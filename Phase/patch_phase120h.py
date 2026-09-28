"""patch_phase120h.py -- V120: custom properties nothing reads.

76 custom properties are declared in the stylesheets; 61 are never read -- no var(--name) in any
rule or string, no getPropertyValue or setProperty in the code. They are the variable bridges of
component kits that are no longer here: the "Rev component kit" (--color-mode-*, --color-fly-*,
--icon-size, --ghost-color, --option-*), the "Uploaded Figma clone" palette (--j-*), the
whiteboard's panel theme (--panel-*) and its grid and accent colours. Their declarations go; a
rule left with no declarations goes; a section comment left over nothing goes. Deleting a
declaration can leave another property unread (one bridge variable reading another), so the
script runs to a fixed point, and asserts the counts it measured."""
NAME = 'patch_phase120h.py'
BASE = 'b7e4ca1a2032d240bd1a53336b224c33b7158f1d494125686c6ba44d4f813bba'
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
def style_bodies(t):
    """(start, end) of every <style> element's body, scanning the way a browser does."""
    out, i = [], 0
    opener = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    low = t.lower()
    while True:
        m = opener.search(t, i)
        if not m:
            return out
        if m.group(0) == '<!--':
            i = t.index('-->', m.end()) + 3
            continue
        tag = m.group(1).lower()
        e = low.index('</%s>' % tag, m.end())
        if tag == 'style':
            out.append((m.end(), e))
        i = e + len(tag) + 3


def unread(t):
    """Custom properties declared in a stylesheet whose name appears nowhere but in declarations."""
    decl = {}
    for s, e in style_bodies(t):
        for m in re.finditer(r'(?<![\w-])(--[A-Za-z_][\w-]*)\s*:', t[s:e]):
            decl.setdefault(m.group(1), set()).add(s + m.start())
    out = []
    for name, ps in decl.items():
        if all(m.start() in ps for m in re.finditer(re.escape(name) + r'(?![\w-])', t)):
            out.append(name)
    return sorted(out)


def strip_decls(t, names):
    """Remove the declarations of these properties from every stylesheet; returns (t, count)."""
    n = 0
    rx = re.compile(r'[ \t]*(?<![\w-])(%s)\s*:[^;{}]*(;|(?=\}))[ \t]*(\n(?=[ \t]*[-}]))?' % '|'.join(re.escape(x) for x in names))
    for s, e in sorted(style_bodies(t), reverse=True):
        css = t[s:e]
        css2, k = rx.subn('', css)
        n += k
        t = t[:s] + css2 + t[e:]
    return t, n


def mask_comments(css):
    """The text with every comment's characters blanked, so braces inside comments are not read."""
    out, i = list(css), 0
    while True:
        a = css.find('/*', i)
        if a < 0:
            return ''.join(out)
        b = css.find('*/', a + 2)
        b = len(css) if b < 0 else b + 2
        for k in range(a, b):
            if out[k] != '\n':
                out[k] = ' '
        i = b


def empty_rule(css):
    """(start, end) of the first rule or at-rule whose block holds nothing, or None. The start is
    taken back over a comment that directly precedes it when that comment heads nothing else --
    the rule is followed by a blank line, another comment, or the end of the stylesheet."""
    m = mask_comments(css)
    i = 0
    while True:
        o = m.find('{', i)
        if o < 0:
            return None
        c = m.find('}', o)
        n = m.find('{', o + 1)
        if c >= 0 and (n < 0 or c < n) and not m[o + 1:c].strip():
            s = max(m.rfind('}', 0, o), m.rfind('{', 0, o), m.rfind(';', 0, o)) + 1
            while s < o and m[s] in ' \t\n':
                s += 1
            # the preceding comment, if one ends right before the prelude
            before = css[:s].rstrip(' \t\n')
            e = c + 1
            while e < len(css) and css[e] in ' \t':
                e += 1
            if e < len(css) and css[e] == '\n':
                e += 1
            if before.endswith('*/'):
                cs = before.rfind('/*')
                after = css[e:]
                if not after.strip() or after.lstrip(' \t').startswith('/*') or after.startswith('\n'):
                    s = cs
            # the whole line when the rule stands alone on it
            ls = s
            while ls > 0 and css[ls - 1] in ' \t':
                ls -= 1
            if ls == 0 or css[ls - 1] == '\n':
                s = ls
            return s, e
        i = o + 1


def drop_empty_rules(t):
    n = 0
    for s, e in sorted(style_bodies(t), reverse=True):
        css = t[s:e]
        while True:
            r = empty_rule(css)
            if not r:
                break
            css = css[:r[0]] + css[r[1]:]
            n += 1
        t = t[:s] + css + t[e:]
    return t, n


first = unread(t)
if len(first) != 61:
    sys.exit('ABORT: %d unread custom properties, measured 61' % len(first))
total_decls, total_rules, rounds = 0, 0, 0
while True:
    names = unread(t)
    if not names:
        break
    rounds += 1
    t, k = strip_decls(t, names)
    total_decls += k
    t, r = drop_empty_rules(t)
    total_rules += r
    if rounds > 5:
        sys.exit('ABORT: no fixed point')
print('removed %d declarations of %d+ properties and %d emptied rules in %d rounds' % (total_decls, len(first), total_rules, rounds))
if unread(t):
    sys.exit('ABORT: still unread: %r' % unread(t))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
