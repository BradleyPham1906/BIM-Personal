"""patch_phase120f.py -- V120: code nothing can reach.

Three kinds, each found by derivation rather than by reading:

  - function declarations whose name appears nowhere else in the file: not called, not referenced,
    not named in a string, not in the markup. The finder is scope-blind on purpose -- a name used
    anywhere keeps every declaration of it -- so it can only err towards keeping. Twelve, measured
    (bimRebuildBeam, bimDuplicateWallType, openWallTypeDlg, bimIsRoomTag, three segment and ray
    intersectors, among them), and the script re-runs the finder on its own output until it finds
    none: deleting a function can orphan the only one it called;
  - the top toolbar's click handler answered ten acts, and only two controls in the file carry
    data-a3d (drawer, rdrawer). The other eight branches -- fit, undo, redo, import, saveproj,
    del, uipanels and any primitive type -- were written for toolbar buttons that later phases
    moved to the ribbon and the dock; nothing has emitted them since. (uipanels was the User
    Interface menu's own button; V120n makes the menu's other opener, the dock's, work again);
  - A3D_DEAD_SHELL, V80's list of whiteboard panel blocks (.fl-pages, .fl-layers,
    .fl-bottom-actions, .fak-root) that bimCleanShell removed on every change to the left panel.
    Nothing has built those blocks since the whiteboard's sidebar went in V113b, so the pass
    searched for them on every mutation and never found one."""
NAME = 'patch_phase120f.py'
BASE = '98c4e26a8466f131ca9ce5678327e9f5dac53a91f0130b605020ad04a12ea775'
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
# ---- the finder: a JavaScript lexer checked against acorn on this build, and a scope-blind
#      search for declarations whose name is mentioned nowhere else

_PUNCT_BEFORE_REGEX = set('(,=:[!&|?{};+-*%<>~^')
_KW_BEFORE_REGEX = {'return', 'typeof', 'case', 'do', 'else', 'in', 'instanceof', 'new', 'delete',
                    'void', 'throw', 'yield', 'await'}
_WORDCH = re.compile(r'[A-Za-z0-9_$]')


def decode(body):
    """The value of a string literal's body (between the quotes)."""
    out, i, n = [], 0, len(body)
    while i < n:
        c = body[i]
        if c != '\\':
            out.append(c); i += 1; continue
        i += 1
        if i >= n:
            break
        c = body[i]
        simple = {'n': '\n', 't': '\t', 'r': '\r', 'b': '\b', 'f': '\f', 'v': '\v', '0': '\0'}
        if c in simple and not (c == '0' and i + 1 < n and body[i + 1].isdigit()):
            out.append(simple[c]); i += 1
        elif c == 'u':
            if i + 1 < n and body[i + 1] == '{':
                j = body.index('}', i)
                out.append(chr(int(body[i + 2:j], 16))); i = j + 1
            else:
                out.append(chr(int(body[i + 1:i + 5], 16))); i += 5
        elif c == 'x':
            out.append(chr(int(body[i + 1:i + 3], 16))); i += 3
        elif c == '\r':
            i += 2 if body[i:i + 2] == '\r\n' else 1
        elif c in '\n  ':
            i += 1
        else:
            out.append(c); i += 1
    s = ''.join(out)
    # a surrogate pair written as two \\u escapes is one character, as it is to the browser
    return s.encode('utf-16', 'surrogatepass').decode('utf-16') if re.search('[\ud800-\udfff]', s) else s


def lex(code):
    """Yield (kind, start, end) with kind in comment, string, template, regex, word, num, punct."""
    i, n = 0, len(code)
    prev = None          # (kind, text) of the previous significant token
    while i < n:
        c = code[i]
        if c in ' \t\r\n ﻿  ':
            i += 1; continue
        if code.startswith('//', i):
            j = code.find('\n', i)
            j = n if j < 0 else j
            yield ('comment', i, j); i = j; continue
        if code.startswith('/*', i):
            j = code.find('*/', i + 2)
            j = n if j < 0 else j + 2
            yield ('comment', i, j); i = j; continue
        if c in '"\'':
            j = i + 1
            while j < n and code[j] != c:
                j += 2 if code[j] == '\\' else 1
            yield ('string', i, j + 1); prev = ('string', ''); i = j + 1; continue
        if c == '`':
            j = i + 1
            depth = 0
            while j < n:
                if code[j] == '\\':
                    j += 2; continue
                if code[j] == '`' and depth == 0:
                    break
                if code.startswith('${', j):
                    depth += 1; j += 2; continue
                if code[j] == '}' and depth:
                    depth -= 1
                j += 1
            yield ('template', i, j + 1); prev = ('template', ''); i = j + 1; continue
        if c == '/':
            is_regex = prev is None or (prev[0] == 'punct' and prev[1][-1] in _PUNCT_BEFORE_REGEX) or \
                (prev[0] == 'word' and prev[1] in _KW_BEFORE_REGEX)
            if is_regex:
                j, cls = i + 1, False
                while j < n:
                    ch = code[j]
                    if ch == '\\':
                        j += 2; continue
                    if ch == '[':
                        cls = True
                    elif ch == ']':
                        cls = False
                    elif ch == '/' and not cls:
                        break
                    elif ch == '\n':
                        raise ValueError('unterminated regex at %d' % i)
                    j += 1
                j += 1
                while j < n and _WORDCH.match(code[j]):
                    j += 1
                yield ('regex', i, j); prev = ('regex', ''); i = j; continue
        if _WORDCH.match(c):
            j = i
            while j < n and (_WORDCH.match(code[j]) or (code[j] == '.' and c.isdigit())):
                j += 1
            kind = 'num' if c.isdigit() else 'word'
            yield (kind, i, j); prev = (kind, code[i:j]); i = j; continue
        if c == '.' and i + 1 < n and code[i + 1].isdigit():
            j = i + 1
            while j < n and _WORDCH.match(code[j]):
                j += 1
            yield ('num', i, j); prev = ('num', code[i:j]); i = j; continue
        # punctuation: the longest operators first matter only for '/' handling via prev
        m = re.match(r'>>>=|===|!==|\*\*=|<<=|>>=|>>>|\.\.\.|=>|==|!=|<=|>=|&&|\|\||\?\?|\+\+|--|[-+*/%&|^]=|<<|>>|\*\*|.', code[i:i + 4], re.S)
        tok = m.group(0)
        yield ('punct', i, i + len(tok))
        # ')' and ']' end an expression; '++'/'--' are ambiguous and treated as ending one
        prev = ('punct', tok) if tok not in (')', ']', '}', '++', '--') else ('end', tok)
        i += len(tok)


def script_blocks(t):
    """(start, end) of the body of every <script> element, found the way a browser finds them."""
    out, i = [], 0
    opener = re.compile(r'<!--|<(script|style)\b([^>]*)>', re.I)
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
        if tag == 'script':
            out.append((m.end(), e))
        i = e + len(tag) + 3



WORD = re.compile(r'[A-Za-z_$][\w$]*')
EXPR_BEFORE = set('=(,:?[!&|+-*/%<>~^')


def declarations(t):
    """[(name, start, end)] of function DECLARATIONS (statement position), end after the '}'."""
    out = []
    for s, e in script_blocks(t):
        code = t[s:e]
        toks = [(k, a, b) for k, a, b in lex(code) if k != 'comment']
        for i, (k, a, b) in enumerate(toks):
            if k != 'word' or code[a:b] != 'function':
                continue
            if i + 2 >= len(toks) or toks[i + 1][0] != 'word' or code[toks[i + 2][1]:toks[i + 2][2]] != '(':
                continue
            prev = code[toks[i - 1][1]:toks[i - 1][2]] if i else ';'
            if prev and (prev[-1] in EXPR_BEFORE or prev in ('return', 'typeof', 'new', 'void', 'in', 'case')):
                continue
            j, depth = i + 2, 0
            while True:           # to the parameter list's close, then the body's braces
                x = code[toks[j][1]:toks[j][2]]
                if x == '(':
                    depth += 1
                elif x == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            j += 1
            if code[toks[j][1]:toks[j][2]] != '{':
                continue
            depth = 0
            while True:
                x = code[toks[j][1]:toks[j][2]]
                if x == '{':
                    depth += 1
                elif x == '}':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            out.append((code[toks[i + 1][1]:toks[i + 1][2]], s + a, s + toks[j][2]))
    return out


def mentions(t):
    """{name: [positions]} of every word outside comments: identifiers, words in literals, markup."""
    pos = {}
    covered = []
    for s, e in script_blocks(t):
        code = t[s:e]
        for k, a, b in lex(code):
            if k == 'comment':
                continue
            txt = code[a:b]
            if k == 'string':
                txt = decode(txt[1:-1])
            for m in WORD.finditer(txt):
                pos.setdefault(m.group(0), []).append(s + a)
        covered.append((s, e))
    # markup outside scripts (styles included: harmless)
    prev = 0
    for s, e in covered:
        for m in WORD.finditer(t[prev:s]):
            pos.setdefault(m.group(0), []).append(prev + m.start())
        prev = e
    for m in WORD.finditer(t[prev:]):
        pos.setdefault(m.group(0), []).append(prev + m.start())
    return pos


def dead(t):
    decl = declarations(t)
    pos = mentions(t)
    out = []
    for name, s, e in decl:
        others = [p for p in pos.get(name, []) if not (s <= p < e)]
        if not others:
            out.append((name, s, e))
    return out




def tidy_lines(t, s, e):
    """Widen [s, e) to whole lines when the declaration stands alone on them."""
    a = s
    while a > 0 and t[a - 1] in ' \t':
        a -= 1
    b = e
    while b < len(t) and t[b] in ' \t':
        b += 1
    if (a == 0 or t[a - 1] == '\n') and b < len(t) and t[b] == '\n':
        return a, b + 1
    return s, e


WANT = ['bimGetActiveBuilding', 'bimRebuildBeam', 'bimWallSegQuad', 'bimDuplicateWallType', 'openWallTypeDlg',
        'bimIsRoomTag', 'bimGizPolyDist', 'bimGizStrokePoly', 'bimSegIntersectParams', 'bimPtSegDist2D',
        'bimRaySegIntersect', 'bimDedupePts']
first = dead(t)
if [n for n, s, e in first] != WANT:
    sys.exit('ABORT: the dead functions are %r, measured %r' % ([n for n, s, e in first], WANT))
removed, rounds = [], 0
while True:
    d = dead(t)
    if not d:
        break
    rounds += 1
    for name, s, e in sorted(d, key=lambda x: -x[1]):
        a, b = tidy_lines(t, s, e)
        t = t[:a] + t[b:]
        removed.append(name)
    if rounds > 5:
        sys.exit('ABORT: no fixed point after five rounds')
print('removed %d functions in %d rounds: %s' % (len(removed), rounds, ', '.join(removed)))

# ---- the top toolbar's acts: only two are emitted. A data-a3d="X" inside a [..] selector is a query,
#      not a control -- the V120 suite found that the first version of this count took one for the other
emitted = sorted(set(re.findall(r'(?<!\[)data-a3d="([a-z0-9]+)"', t)))
if emitted != ['drawer', 'rdrawer']:
    sys.exit('ABORT: the toolbar emits %r' % emitted)
rep("""      if(act==='rdrawer'){var rp=document.getElementById('a3d-right');if(rp)rp.classList.toggle('open');}
      else if(act==='fit')fitScene();
      else if(act==='undo')doUndo();
      else if(act==='redo')doRedo();
      else if(act==='import'){var fi=root.querySelector('#a3d-filein');if(fi){fi.value='';fi.click();}}
      else if(act==='saveproj'){bimExportProjectFile();}
      else if(act==='del'){delSelection();}
      else if(act==='uipanels'){var um=root.querySelector('#a3d-uimenu');if(um)um.classList.toggle('open');ev.stopPropagation();}
      else if(TYPES[act])openDlg(act);
    });""",
"""      if(act==='rdrawer'){var rp=document.getElementById('a3d-right');if(rp)rp.classList.toggle('open');}
    });""")

# ---- the whiteboard panel blocks the shell pass looked for
span('  /* ================= __acad3dV80: the left shell belongs to the BIM app =================',
     '  /* Every control that IS live in the left shell',
     '  /* ================= __acad3dV80: the left shell belongs to the BIM app ================= */\n', 25)
rep("""    var did=false,i;
    for(i=0;i<A3D_DEAD_SHELL.length;i++){
      var dead=panel.querySelectorAll(A3D_DEAD_SHELL[i]),k;
      for(k=0;k<dead.length;k++){dead[k].parentNode.removeChild(dead[k]);did=true;}
    }
""", """    var did=false;
""")
if 'A3D_DEAD_SHELL' in t:
    sys.exit('ABORT: A3D_DEAD_SHELL is still referenced')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
