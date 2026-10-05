"""bim_phase120_canvas_cleanup_browser_tests.py -- V120: the canvas-era cleanup.

The owner, opening the file: "it look very messy and still contain some of the old canvas
configuretion in there please clean that up before we make any further progress".

What V120 took out, and what this suite holds it to:

  1. NOTHING OF THE OLD MODULES IS NAMED. No Figma, whiteboard or Canvas module, no Rev component
     kit, no Precision Workbench, no window.toast / __WB_MATERIAL_CARDS / __draftActiveTool, no
     hidden ribbon (#acad-tabs, #acad-panels, renderA3dPanels, installA3dTab, acadApplyWorkspace),
     no exit3d, no .fl-* / .uc-* / #uploaded-command-palette / --figma-dock-w, no patch_3d.py.
  2. NOTHING DEAD THAT A DERIVATION CAN FIND. Every CSS rule can match an element some code can
     create -- a class or an id counts as live only where it can come from (an attribute, a class
     list, an id assignment, a selector, a prefix a name is built from), not wherever the word
     appears. Every custom property is read. Every function declaration's name is used. Every act
     the top toolbar answers has a control that emits it, and every [data-x="v"] the code looks for
     is carried by some control.
  3. ONE STYLESHEET, TWO SCRIPTS, NO WHITESPACE DEBRIS. The CSS is one <style> in <head>; <body>
     holds the shell's script and the engine's; no line ends in blanks and no two lines in a row
     are blank.
  4. WHAT STAYED STILL WORKS, DRIVEN. The quick-access Undo and Redo undo and redo; the command
     palette opens, lists, runs and hands the keyboard back; on a sheet it refuses through the
     engine's toast; the rail switches the panel and the panel toggle moves the workspace edge; the
     dock's User Interface entry opens its menu again (V120n); the material library reaches the
     model.
  5. THE HEIGHT CONTRACT IS THE BAR'S: --a3d-top-h is 52 px (44 in the compact tier) from the first
     frame, and the workspace starts there.

The static checks share their JavaScript lexer with the V120 patches (it is checked against acorn
on the build it was written for); the CSS walk and the liveness rules here are this suite's own.
"""
import asyncio, pathlib, re, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

BANNED = [r'[Ff]igma', r'[Ww]hiteboard', r'\bCanvas\b', r'[Cc]anvas-era', r'__WB_', r'(?<![\w-])fl-[a-z]',
          r'(?<![\w-])uc-[a-z]', r'(?<![\w-])fak-', r'uploaded-command-palette', r'Rev component', r'color-fly',
          r'color-mode-', r'Svelte', r'Precision Workbench', r'__draftActiveTool', r'window\.toast\b',
          r'__acadApplyWorkspace', r'__acadRenderTab', r'renderA3dPanels', r'installA3dTab', r'removeA3dTab',
          r'__a3dIsRibbonTab', r'\bexit3d\b', r'__a3dExit\b', r'acad-tabs', r'acad-panels',
          r'(?<![\w-])acad-tab(?![\w-])', r'data-acad-tab', r'__figmaDockSyncW', r'figma-dock-w',
          r'acad-ribbon-h', r'data-fl-tab', r'data-a3dshell', r'patch_3d\.py', r'a3d_engine\.js',
          r'(?<![\w-])fc-shell', r'(?<![\w-])cad-ribbon', r'acad-status', r'#hint\b', r'#viewport\b',
          r'state\.nodes', r'state\.wires', r'__ws3Del', r'\bcadRun\b']
GONE_GLOBALS = ['toast', '__WB_MATERIAL_CARDS', '__a3dExit', '__acadApplyWorkspace', '__figmaDockSyncW',
                'renderA3dPanels', '__a3dIsRibbonTab', '__acadRenderTab', '__draftActiveTool', '__acadRibbonUI',
                '__acadWorkspaceV1', '__acadWs2V1']

# ======================================================================= the lexer (shared)
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


def literals(t):
    """Every string/template/regex literal in every script: (abs_start, abs_end, kind, value)."""
    out = []
    for s, e in script_blocks(t):
        code = t[s:e]
        for kind, a, b in lex(code):
            if kind == 'string':
                out.append((s + a, s + b, kind, decode(code[a + 1:b - 1])))
            elif kind == 'template':
                out.append((s + a, s + b, kind, code[a + 1:b - 1]))
            elif kind == 'regex':
                out.append((s + a, s + b, kind, code[a:b]))
    return out


def comments(t):
    """Every JS comment in every script: (abs_start, abs_end)."""
    out = []
    for s, e in script_blocks(t):
        code = t[s:e]
        for kind, a, b in lex(code):
            if kind == 'comment':
                out.append((s + a, s + b))
    return out


def literals_ctx(t, k=4):
    """Like literals(), with the text of the k significant tokens before each literal, joined by
    single spaces: '. id =' before the literal in el.id='x'."""
    out = []
    for s, e in script_blocks(t):
        code = t[s:e]
        prev = []
        for kind, a, b in lex(code):
            if kind == 'comment':
                continue
            if kind in ('string', 'template', 'regex'):
                v = decode(code[a + 1:b - 1]) if kind == 'string' else (code[a + 1:b - 1] if kind == 'template' else code[a:b])
                out.append((s + a, s + b, kind, v, ' '.join(prev[-k:])))
                prev.append(code[a:b] if kind != 'string' else 'STR:' + decode(code[a + 1:b - 1]))
            else:
                prev.append(code[a:b])
            if len(prev) > 16:
                prev = prev[-8:]
    return out


# ======================================================================= the file, statically
def elements(t):
    """[(tag, open_start, body_start, body_end)] of every <script> and <style> ELEMENT, found the
    way a browser finds them: one scan, a comment or an element skipped whole once it opens."""
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
        out.append((tag, m.start(), m.end(), e))
        i = e + len(tag) + 3


NAMETOK = re.compile(r'-?[A-Za-z_][\w-]*')


def live_names(t):
    """(classes, ids) an element can carry, read from where they can come from."""
    cls, ids = set(), set()
    # the markup outside scripts, styles and comments
    rest, prev = [], 0
    for tag, a, b, e in elements(t):
        rest.append(t[prev:a]); prev = e
    rest.append(t[prev:])
    html = re.sub(r'<!--.*?-->', '', ''.join(rest), flags=re.S)
    for m in re.finditer(r'\b(class|id)\s*=\s*"([^"]*)"', html):
        (cls if m.group(1) == 'class' else ids).update(NAMETOK.findall(m.group(2)))
    for s, e, kind, v, ctx in literals_ctx(t):
        if kind == 'regex':
            cls.update(NAMETOK.findall(v)); ids.update(NAMETOK.findall(v)); continue
        for m in re.finditer(r'\b(class|id)\s*=\s*(["\']?)', v):
            q, a = m.group(2), m.end()
            b = (v.find(q, a) if q else a + re.match(r'[^\s>]*', v[a:]).end())
            b = len(v) if b < 0 else b
            (cls if m.group(1) == 'class' else ids).update(NAMETOK.findall(v[a:b]))
        words = NAMETOK.findall(v)
        if re.fullmatch(r'\s*-?[A-Za-z_][\w-]*\s*', v):
            cls.add(words[0])
            if ctx.endswith('. id =') or re.search(r'[-_]', words[0]):
                ids.add(words[0])
        elif re.fullmatch(r'\s*-?[A-Za-z_][\w-]*(?:\s+-?[A-Za-z_][\w-]*)+\s*', v) and any('-' in w for w in words):
            cls.update(words)
        cls.update(re.findall(r'\.(-?[A-Za-z_][\w-]*)', v))
    pre = set()
    for s, e, kind, v, ctx in literals_ctx(t):
        m = re.search(r'(-?[A-Za-z_][\w-]*-)\Z', v) if kind == 'string' else None
        after = t[e:e + 60].lstrip()
        if m and after.startswith('+') and not re.match(r'\+\s*(Date\.now|Math\.)', after):
            pre.add(m.group(1))
    return cls, ids, pre


def css_rules(css):
    """Every style rule's selector list, at any depth of @media / @supports: [(start, selector)]."""
    css = re.sub(r'/\*.*?\*/', lambda m: ' ' * len(m.group(0)), css, flags=re.S)
    out, stack, i, start = [], [], 0, 0
    while i < len(css):
        c = css[i]
        if c in '"\'':
            i = css.index(c, i + 1) + 1; continue
        if c == '{':
            pre = css[start:i].strip()
            if pre.startswith('@'):
                stack.append('at' if re.match(r'@(media|supports)\b', pre) else 'skip')
            else:
                stack.append('rule')
                if 'skip' not in stack[:-1]:
                    out.append((start, pre))
            start = i + 1
        elif c == '}':
            stack.pop(); start = i + 1
        elif c == ';' and (not stack or stack[-1] == 'at'):
            start = i + 1
        i += 1
    return out


def needs(sel):
    flat, depth = '', 0
    for ch in sel:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        elif depth == 0:
            flat += ch
    return re.findall(r'([.#])(-?[A-Za-z_][\w-]*)', flat)


def split_top(sel):
    out, depth, cur = [], 0, ''
    for ch in sel:
        depth += ch in '(['
        depth -= ch in ')]'
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    return [x.strip() for x in out + [cur] if x.strip()]


def dead_rules(t):
    cls, ids, pre = live_names(t)
    dead = []
    for tag, a, b, e in elements(t):
        if tag != 'style':
            continue
        for s, sel in css_rules(t[b:e]):
            ok = False
            for one in split_top(sel):
                if all(n in (cls if k == '.' else ids) or any(n.startswith(p) for p in pre) for k, n in needs(one)):
                    ok = True
                    break
            if not ok:
                dead.append(sel[:70])
    return dead


def unread_properties(t):
    decl = {}
    for tag, a, b, e in elements(t):
        if tag == 'style':
            for m in re.finditer(r'(?<![\w-])(--[A-Za-z_][\w-]*)\s*:', t[b:e]):
                decl.setdefault(m.group(1), set()).add(b + m.start())
    return sorted(n for n, ps in decl.items()
                  if all(m.start() in ps for m in re.finditer(re.escape(n) + r'(?![\w-])', t)))


def unused_functions(t):
    words, decls = {}, []
    for tag, a, b, e in elements(t):
        if tag != 'script':
            continue
        code = t[b:e]
        toks = [(k, x, y) for k, x, y in lex(code) if k != 'comment']
        for i, (k, x, y) in enumerate(toks):
            txt = code[x:y]
            for w in re.findall(r'[A-Za-z_$][\w$]*', jslex_value(k, txt)):
                words.setdefault(w, []).append(b + x)
            if k == 'word' and txt == 'function' and i + 2 < len(toks) and toks[i + 1][0] == 'word' \
                    and code[toks[i + 2][1]:toks[i + 2][2]] == '(':
                prev = code[toks[i - 1][1]:toks[i - 1][2]] if i else ';'
                if prev[-1] in '=(,:?[!&|+-*/%<>~^' or prev in ('return', 'typeof', 'new', 'void', 'in', 'case'):
                    continue
                j, d = i + 2, 0
                while True:                      # the parameter list
                    s_ = code[toks[j][1]:toks[j][2]]
                    if s_ == '(':
                        d += 1
                    elif s_ == ')':
                        d -= 1
                        if d == 0:
                            break
                    j += 1
                j += 1
                d = 0
                while True:                      # the body
                    s_ = code[toks[j][1]:toks[j][2]]
                    if s_ == '{':
                        d += 1
                    elif s_ == '}':
                        d -= 1
                        if d == 0:
                            break
                    j += 1
                decls.append((code[toks[i + 1][1]:toks[i + 1][2]], b + x, b + toks[j][2]))
    rest, prev = [], 0
    for tag, a, b, e in elements(t):
        rest.append(t[prev:a]); prev = e
    rest.append(t[prev:])
    markup = ''.join(rest)
    return sorted(n for n, s, e in decls
                  if not [p for p in words.get(n, []) if not (s <= p < e)] and not re.search(r'\b%s\b' % re.escape(n), markup))


def jslex_value(kind, txt):
    return decode(txt[1:-1]) if kind == 'string' else txt


def toolbar_acts(t):
    """(acts the top toolbar's handler answers, acts a control in the file emits)."""
    m = re.search(r"root\.querySelector\('\.a3d-tb'\)\.addEventListener\('click',function\(ev\)\{(.*?)\n    \}\);", t, re.S)
    handled = sorted(set(re.findall(r"act==='([a-z0-9]+)'", m.group(1)))) if m else None
    typed = bool(m and re.search(r'TYPES\[act\]', m.group(1)))
    emitted = sorted(set(re.findall(r'(?<!\[)data-a3d="([a-z0-9]+)"', t)))   # [data-a3d="x"] is a query, not a control
    return handled, typed, emitted


def unmatched_attribute_selectors(t):
    """[data-x="v"] selectors in the code whose value no control carries: an attribute written in
    markup (data-x="v" outside brackets), set with setAttribute, or built at run time (data-x="'+...)."""
    queried, emitted, built = {}, set(), set()
    for s, e, kind, v, ctx in literals_ctx(t):
        if kind != 'string':
            continue
        for m in re.finditer(r'\[data-([a-z0-9-]+)=\\?["\']([^"\'\\\]]+)\\?["\']\]', v):
            queried.setdefault((m.group(1), m.group(2)), t.count('\n', 0, s) + 1)
        for m in re.finditer(r'(?<![\[\w-])data-([a-z0-9-]+)="([^"]*)"', v):
            emitted.add((m.group(1), m.group(2)))
        for m in re.finditer(r'(?<![\[\w-])data-([a-z0-9-]+)="\Z', v):
            built.add(m.group(1))
        m = re.search(r"setAttribute \( STR:data-([a-z0-9-]+) ,$", ctx)
        if m:
            emitted.add((m.group(1), v))
    return sorted('data-%s="%s" (line %d)' % (a, v, ln) for (a, v), ln in queried.items()
                  if (a, v) not in emitted and a not in built)


def static_checks(ck, t):
    print('\n-- 1. nothing of the old modules is named')
    hits = [(p, t.count('\n', 0, m.start()) + 1) for p in BANNED for m in [re.search(p, t)] if m]
    ck(not hits, 'none of %d canvas-era names appears anywhere in the file (%s)' % (len(BANNED), hits[:4]))

    print('\n-- 2. nothing dead that a derivation can find')
    dead = dead_rules(t)
    ck(not dead, 'every CSS rule can match an element some code can create (%d cannot: %s)' % (len(dead), dead[:3]))
    un = unread_properties(t)
    ck(not un, 'every custom property is read (%d unread: %s)' % (len(un), un[:4]))
    uf = unused_functions(t)
    ck(not uf, 'every function declaration is used (%d unused: %s)' % (len(uf), uf[:4]))
    handled, typed, emitted = toolbar_acts(t)
    ck(handled is not None and handled == emitted and not typed,
       'the top toolbar answers exactly the acts its controls emit (answers %s, emitted %s%s)'
       % (handled, emitted, ', plus every primitive type' if typed else ''))
    um = unmatched_attribute_selectors(t)
    ck(not um, 'every attribute selector in the code names a value some control carries (%s)' % um[:3])
    lib = [m.start() for m in re.finditer(r'\bA3D_MATERIAL_LIBRARY\b', t)]
    reader = re.search(r'function bimMaterialCards\(\)\{\s*return A3D_MATERIAL_LIBRARY;', t)
    ck(len(lib) == 2 and t.count('var A3D_MATERIAL_LIBRARY=') == 1 and reader is not None,
       'the material library is declared once and read only through bimMaterialCards() (%d mentions)' % len(lib))
    guards = re.findall(r'if\(window\.__acad\w+\)\s*return;', t)
    ck(not guards, 'no shell module guards against being injected twice (%s)' % guards[:2])
    silent = [m.group(0)[:60] for m in re.finditer(r'catch\(\w+\)\{\s*window\.__\w+Err=[^}]*\}', t) if 'console.warn' not in m.group(0)]
    ck(not silent, 'no catch only records an error where nothing reads it (%s)' % silent[:2])

    print('\n-- 3. one stylesheet, two scripts, no whitespace debris')
    els = elements(t)
    styles = [x for x in els if x[0] == 'style']
    scripts = [x for x in els if x[0] == 'script']
    head_end = t.index('</head>')
    ck(len(styles) == 1 and styles[0][1] < head_end, 'one <style>, in <head> (%d style elements)' % len(styles))
    ck(len(scripts) == 2 and all(x[1] > head_end for x in scripts),
       'two <script> elements in <body>: the shell and the engine (%d)' % len(scripts))
    lines = t.split('\n')
    trailing = [i + 1 for i, l in enumerate(lines) if l != l.rstrip(' \t')]
    ck(not trailing, 'no line ends in blanks (%s)' % trailing[:5])
    runs = [i + 1 for i in range(1, len(lines)) if not lines[i].strip() and not lines[i - 1].strip()]
    ck(not runs, 'no two blank lines in a row (%s)' % runs[:5])


# ======================================================================= the running app
class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV120' in t, 'the V120 marker is present')
    if not ck.bad:
        try:
            static_checks(ck, t)
        except Exception as e:
            ck(False, 'the static checks ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e)[:160]))
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:160]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs, warns = [], []
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        page.on('console', lambda m: warns.append(m.text[:160]) if m.type == 'warning' and m.text.startswith('[BIM]') else None)
        page.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        early = []

        def on_dcl():
            early.append(1)
        await page.add_init_script("""document.addEventListener('DOMContentLoaded',function(){
            window.__v120early={sheets:document.styleSheets.length,
              engineRule:[].some.call(document.styleSheets[0]?document.styleSheets[0].cssRules:[],function(r){return r.selectorText==='#acad3d';})};});""")
        await page.goto('file://' + str(HTML))
        on = False
        for _ in range(40):
            on = await safe("()=>!!window.__a3dOn")
            if on:
                break
            await page.wait_for_timeout(100)
        await page.wait_for_timeout(600)

        print('\n-- 4. the app boots into the workspace, and the old shell is not in it')
        ck(on is True, 'the boot enters the BIM workspace (%s)' % on)
        gone = await safe("(names)=>names.filter(function(n){return typeof window[n]!=='undefined';})", GONE_GLOBALS)
        ck(gone == [], 'none of the old globals is defined (%s)' % gone)
        dom = await safe("""()=>({old:['#acad-tabs','#acad-panels','.acad-tab','#viewport','#fc-shell','#cad-ribbon','#acad-status',
                                    '#uploaded-command-palette','#figma-layers-shell','.fl-help'].filter(function(s){return document.querySelector(s);}),
              bar:[].map.call(document.getElementById('acad-shell').children,function(e){return e.id;}),
              qat:[].map.call(document.querySelectorAll('#acad-qat .acad-qbtn'),function(b){return [b.getAttribute('data-acad-act'),b.title,!!b.querySelector('svg')];}),
              early:window.__v120early||null,
              sheets:document.styleSheets.length})""")
        ck(dom and dom['old'] == [], 'no element of the old shell is in the document (%s)' % (dom and dom['old']))
        ck(dom and dom['bar'] == ['acad-qat', 'acad-doctabs'], 'the top bar is the quick-access buttons and the project tabs (%s)' % (dom and dom['bar']))
        ck(dom and [q[:2] for q in dom['qat']] == [['saveJson', 'Save'], ['openJson', 'Open'], ['undo', 'Undo'], ['redo', 'Redo'], ['print', 'Plot']]
           and all(q[2] for q in dom['qat']),
           'five quick-access buttons, each with its icon (%s)' % (dom and [q[1] for q in dom['qat']]))
        ck(dom and dom['early'] and dom['early']['sheets'] == 1 and dom['early']['engineRule'] is True and dom['sheets'] == 1,
           "the engine's rules are in the one stylesheet before any script runs, and nothing adds another (%s, then %s)"
           % (dom and dom['early'], dom and dom['sheets']))

        print('\n-- 5. the height contract is the bar\'s')
        h = await safe("()=>[getComputedStyle(document.documentElement).getPropertyValue('--a3d-top-h').trim(),"
                       "Math.round(document.getElementById('acad3d').getBoundingClientRect().top),"
                       "Math.round(document.getElementById('acad-shell').getBoundingClientRect().height)]")
        ck(h == ['52px', 52, 52], '--a3d-top-h is 52px, the workspace starts there, and the bar is that tall (%s)' % h)

        print('\n-- 6. the quick-access Undo and Redo, clicked')
        n0 = await safe("()=>{window.__a3dTestSetObjs([]);return window.__a3dState().objs.length;}")
        await safe("()=>window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false)")
        n1 = await safe("()=>window.__a3dState().objs.length")
        await page.click('#acad-qat [data-acad-act="undo"]')
        await page.wait_for_timeout(300)
        n2 = await safe("()=>window.__a3dState().objs.length")
        await page.click('#acad-qat [data-acad-act="redo"]')
        await page.wait_for_timeout(300)
        n3 = await safe("()=>window.__a3dState().objs.length")
        ck([n0, n1, n2, n3] == [0, 1, 0, 1], 'Undo takes the wall away and Redo brings it back (%s)' % [n0, n1, n2, n3])

        print('\n-- 7. the command palette, driven from the keyboard')
        await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
        await page.mouse.click(800, 500)
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(300)
        pal = await safe("()=>({open:document.getElementById('a3d-cmdpal').classList.contains('show'),"
                         "focus:document.activeElement===document.querySelector('#a3d-cmdpal input')})")
        await page.keyboard.type('WALL')
        await page.wait_for_timeout(200)
        rows = await safe("()=>[].map.call(document.querySelectorAll('#a3d-cmdpal .a3d-cmdrow'),function(r){return r.textContent.trim();})")
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(400)
        after = await safe("()=>({open:document.getElementById('a3d-cmdpal').classList.contains('show'),"
                           "tool:window.__a3dActiveSketchTool(),input:document.activeElement&&document.activeElement.tagName})")
        ck(pal and pal['open'] and pal['focus'], 'Ctrl+K opens the palette with the keyboard in it (%s)' % pal)
        ck(rows and rows[0].startswith('WALL'), 'typing WALL puts the WALL command first (%s)' % (rows and rows[:2]))
        ck(after and not after['open'] and after['tool'] == 'wall' and after['input'] != 'INPUT',
           'Enter runs it: the palette closes, the wall tool is armed, the keyboard is back on the drawing (%s)' % after)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)

        print('\n-- 8. on a sheet the palette refuses, through the engine\'s toast')
        await safe("()=>{var id=window.__a3dAddSheet('A900','Cleanup probe','ANSI-B-L');window.__a3dOpenSheetView(id);"
                   "var t=document.getElementById('a3d-toast');if(t)t.textContent='';"
                   "if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")
        await page.wait_for_timeout(300)
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(250)
        await page.keyboard.type('WALL')
        await page.wait_for_timeout(150)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(400)
        toast = await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:null;}")
        ck(toast is not None and 'not available' in toast, "the refusal is said on screen (%r)" % toast)
        await safe("()=>{var b=document.querySelector('.a3d-lytab[data-lt=\"model\"],[data-lt=\"model\"]');if(b)b.click();else window.__a3dSetPlanView();}")
        await page.wait_for_timeout(300)
        await safe("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(200)

        print('\n-- 9. the left shell: the rail switches the panel, the toggle moves the workspace edge')
        rail = await safe("()=>[].map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn'),function(b){return [b.getAttribute('data-tab'),b.getAttribute('aria-label')];})")
        ck(rail == [['layers', 'Layers'], ['presentation', 'Presentation'], ['browser', 'Project Browser'], ['assets', 'Assets'], ['analyze', 'Analyze']],   # AMENDED FOR V141; FOR V159: Site analysis inside Analyze
           'the rail buttons, Layers (V121), Presentation (V122), Project Browser and Assets -- AMENDED FOR V122 (%s)' % rail)
        first = await safe("()=>[document.getElementById('a3d-shell').getAttribute('data-tab'),"
                           "[].map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn.active'),function(b){return b.getAttribute('data-tab');})]")
        ck(first == ['browser', ['browser']], 'the panel opens on the Project Browser, and its button is the one marked (%s)' % first)
        await page.click('#a3d-rail .a3d-railbtn[data-tab="assets"]')
        await page.wait_for_timeout(350)
        a = await safe("()=>({tab:document.getElementById('a3d-shell').getAttribute('data-tab'),"
                       "rows:document.querySelectorAll('#a3d-leftpanel [data-a3dassets]').length,"
                       "tree:getComputedStyle(document.querySelector('#a3d-leftpanel > .a3d-tree')).display})")
        await page.click('#a3d-rail .a3d-railbtn[data-tab="browser"]')
        await page.wait_for_timeout(350)
        b = await safe("()=>({tab:document.getElementById('a3d-shell').getAttribute('data-tab'),"
                       "assets:document.querySelectorAll('#a3d-leftpanel .a3d-assets-wrap').length,"
                       "tree:getComputedStyle(document.querySelector('#a3d-leftpanel > .a3d-tree')).display})")
        ck(a and a['tab'] == 'assets' and a['rows'] > 0 and a['tree'] == 'none', 'Assets shows the libraries and hides the tree (%s)' % a)
        ck(b and b['tab'] == 'browser' and b['assets'] == 0 and b['tree'] != 'none', 'Project Browser brings the tree back, no assets left behind (%s)' % b)
        edge = "()=>[getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim(),Math.round(document.getElementById('acad3d').getBoundingClientRect().left)]"
        await page.click('#a3d-rail .a3d-paneltoggle')
        await page.wait_for_timeout(450)
        c1 = await safe(edge)
        await page.click('#a3d-rail .a3d-paneltoggle')
        await page.wait_for_timeout(450)
        c2 = await safe(edge)
        ck(c1 == ['54px', 54] and c2 == ['296px', 296], 'collapsing and reopening the panel moves the workspace edge with it (%s / %s)' % (c1, c2))

        print('\n-- 10. the User Interface menu, from the tool dock (V120n)')
        # AMENDED FOR V130: the dock's More menus are gone; the View group's tools are in the Tools and
        # shortcuts panel, opened on that group
        await page.evaluate("()=>window.__a3dDockOpenGroup('a3dview')")
        await page.wait_for_timeout(300)
        await page.click('#a3d-rupop [data-a3dr="bim:uipanels"]')
        await page.wait_for_timeout(300)
        um = await safe("()=>{var m=document.getElementById('a3d-uimenu'),r=m.getBoundingClientRect();"
                        "return {open:m.classList.contains('open'),inside:r.left>=0&&r.right<=window.innerWidth&&r.bottom<=window.innerHeight&&r.width>0};}")
        ck(um and um['open'] and um['inside'], "the dock's User Interface entry opens the menu, inside the window (%s)" % um)
        await page.click('#a3d-uimenu [data-a3dui="hud"]')
        await page.wait_for_timeout(250)
        hud1 = await safe("()=>getComputedStyle(document.querySelector('.a3d-hud')).display")
        await page.click('#a3d-uimenu [data-a3dui="hud"]')
        await page.wait_for_timeout(250)
        hud2 = await safe("()=>getComputedStyle(document.querySelector('.a3d-hud')).display")
        ck(hud1 == 'none' and hud2 != 'none', 'its View HUD box hides the HUD and shows it again (%s -> %s)' % (hud1, hud2))
        await page.mouse.click(900, 600)
        await page.wait_for_timeout(250)
        um2 = await safe("()=>document.getElementById('a3d-uimenu').classList.contains('open')")
        ck(um2 is False, 'and a click outside closes it (%s)' % um2)
        await safe("()=>window.__a3dSetPlanView()")

        print('\n-- 11. the material library reaches the model')
        got = await safe("""()=>{window.__a3dTestSetObjs([]);var id=window.__a3dWall([[0,0],[4,0]],0.3,3,'center',false);
            window.__a3dSetMaterial(id,'Steel');return {mat:window.__a3dMaterialOf(id),vol:window.__a3dObjVolume(id),mass:window.__a3dObjMass(id)};}""")
        ck(got and got['mat'] == 'Steel' and got['vol'] > 0 and abs(got['mass'] - got['vol'] * 7900) < 1e-6,
           "a wall made of Steel weighs its volume times Steel's 7900 kg/m3 (%s)" % got)

        print('\n-- 12. the compact tier')
        await page.set_viewport_size({'width': 700, 'height': 900})
        await page.wait_for_timeout(600)
        hc = await safe("()=>[getComputedStyle(document.documentElement).getPropertyValue('--a3d-top-h').trim(),"
                        "Math.round(document.getElementById('acad3d').getBoundingClientRect().top)]")
        ck(hc == ['44px', 44], 'at phone width the bar is 44px and the workspace starts there (%s)' % hc)
        await page.click('[data-a3d="rdrawer"]')
        await page.wait_for_timeout(300)
        rd = await safe("()=>document.getElementById('a3d-right').classList.contains('open')")
        ck(rd is True, 'the inspector button opens the inspector drawer (%s)' % rd)

        print('\n-- 13. errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        ck(warns == [], 'no [BIM] warnings (%s)' % warns[:3])
        await browser.close()


asyncio.run(main())
