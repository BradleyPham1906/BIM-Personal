"""patch_phase120b.py -- V120: the engine's stylesheet is a stylesheet.

The engine's 277 rules lived in a JavaScript string: 338 lines of '...'+ concatenation inside
buildUI(), handed to a <style> element created at run time and appended to <head>. The file read as
CSS dressed up as code; no CSS tool could see it; and the V114/V117 prunes, which read <style>
elements, never looked inside it, which is how rules for elements deleted phases ago survived there.

It moves, character for character, into <style id="a3d-css"> at the end of <head>: the position the
runtime element occupied, after the base stylesheet and before the shell's own, so the cascade
order is unchanged. The JavaScript comments between the literals are block comments and go in as
CSS comments unchanged. The conversion is checked by the patch itself -- the concatenated string is
rebuilt from the source and compared with what goes into the element -- and by
tools/css_move_check.py in a browser: the rules the old build's runtime sheet held and the rules
the new static sheet holds are the same list, cssText for cssText."""
NAME = 'patch_phase120b.py'
BASE = '7f0b77afd677218ea440bf483417591ab0642a29da960a539e4ad5c46f55b77e'
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
HEAD_JS = "    var css=''+\n"
TAIL_JS = "    var st=document.createElement('style');\n    st.textContent=css;\n    document.head.appendChild(st);\n"
if t.count(HEAD_JS) != 1 or t.count(TAIL_JS) != 1:
    sys.exit('ABORT: the engine stylesheet anchors are not unique')
s = t.index(HEAD_JS)
e = t.index(TAIL_JS, s)
code = t[s + len("    var css="):e]


def scan(code):
    """The concatenation: string literals, '+', whitespace, block comments, and the final ';'.
    Anything else aborts -- the conversion is only exact for an expression of pure literals."""
    i, n, toks = 0, len(code), []
    while i < n:
        c = code[i]
        if c == '\n':
            toks.append(('nl', '')); i += 1
        elif c in ' \t':
            i += 1
        elif c == '+':
            i += 1
        elif c == ';':
            if code[i + 1:].strip():
                sys.exit('ABORT: text after the closing semicolon')
            return toks
        elif code.startswith('/*', i):
            j = code.index('*/', i) + 2
            toks.append(('comment', code[i:j])); i = j
        elif c == "'":
            j = i + 1
            while code[j] != "'":
                if code[j] == '\\':
                    sys.exit('ABORT: an escape in a literal; the conversion does not decode escapes')
                if code[j] == '\n':
                    sys.exit('ABORT: a newline inside a literal')
                j += 1
            toks.append(('str', code[i + 1:j])); i = j + 1
        else:
            sys.exit('ABORT: %r at %d is not part of a literal concatenation' % (c, i))
    sys.exit('ABORT: no closing semicolon')


toks = scan(code)
runtime = ''.join(v for k, v in toks if k == 'str')          # exactly what st.textContent received
lines, cur = [], ''
for k, v in toks:
    if k == 'nl':
        if cur.strip():
            lines.append(cur)
        cur = ''
    else:
        cur += v
if cur.strip():
    lines.append(cur)
css = '\n'.join(lines)
# the check: the element's text minus its comments is the string the engine used to build
stripped = re.sub(r'/\*.*?\*/', '', css, flags=re.S).replace('\n', '')
if stripped != runtime:
    sys.exit('ABORT: the static sheet would not hold the runtime string')
if len(runtime) != 26742:
    sys.exit('ABORT: runtime CSS is %d characters, measured 26742' % len(runtime))
if sum(1 for k, v in toks if k == 'str') != 279:
    sys.exit('ABORT: literal count changed')

t = t[:s] + "    /* __acad3dV120: the engine's rules are the <style id=\"a3d-css\"> element at the end of <head>. */\n" + t[e + len(TAIL_JS):]
rep('</style>\n</head>\n<body>',
    '</style>\n<style id="a3d-css">\n'
    '/* __acad3dV120: the BIM engine\'s stylesheet, moved out of the JavaScript string it was built from\n'
    '   at run time. It sits after the base stylesheet and before the shell\'s, where the runtime\n'
    '   element sat, so the cascade is unchanged. */\n' + css + '\n</style>\n</head>\n<body>')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
