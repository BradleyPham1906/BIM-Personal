"""patch_phase120g.py -- V120: the stylesheet rules that cannot match anything.

V114c and V117e pruned the CSS with a planner that kept a rule alive when its #id or .class
appeared anywhere outside the stylesheets -- a comment or a message included. That is how the
whiteboard's stylesheet outlived the whiteboard by seven phases: #viewport stayed alive while a
toast said "the viewport", .node while a prompt said "place a node", #world while the gizmo's
alignment mode was called 'world'. And the engine's own 277 rules were never examined at all,
because they lived in a JavaScript string until V120b.

This is the same planner with liveness read from where a class or an id can actually come from:
the markup's class and id attributes, an HTML fragment in a string from class=" or id=" to the end
of the value, a string that is only names, a selector in a string, a regex, and a name built at run
time from a literal prefix. An id additionally has to be GIVEN: an id attribute, a string assigned
to .id or passed to setAttribute('id'), or a hyphenated one-name string, the way this file names
ids. And a prefix concatenated with Date.now() or Math.random() makes an object's unique id, which
no stylesheet can name, so 'a3d-'+Date.now() no longer keeps every a3d- class alive.

Measured on this input: 145 rules and 2 at-rules that can never match, 3 selector lists with a
dead member, 18 section comments left over nothing -- the whiteboard's cards, markdown, toolbar,
swatches, hint bar and freehand layer; the FreeCAD-style toolbar and the old ribbon it hid; the
hidden ribbon's tabs, panels and dropdowns (V120c); the 2D status bar; and the engine's rules for a
title, a properties grid and a level header nothing has drawn since the Properties panel was
rebuilt. The script re-analyses its own output to a fixed point, and css_invariance.py drives both
builds through the same states and compares every element's computed style."""
NAME = 'patch_phase120g.py'
BASE = '7ede34a90edfc5cb51fe59d8eacfaaa3e2401d8f769828c99fada6120d35975b'
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
# ---- the planner: a JavaScript lexer (checked against acorn on this build), the V117 rule planner,
#      and liveness read from where a class or an id can come from

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

WORD = re.compile(r'[A-Za-z_][\w-]*')


def style_blocks(t):
    """(start, end) of the body of every <style> ELEMENT, found the way a browser finds them: one
    sequential scan in which a <script>, a <style> or an HTML comment is skipped whole once it
    opens. An earlier version searched for "<style" anywhere, and matched the words "the <style>
    block" inside a CSS comment -- a bogus block that began mid-comment inside a real one -- and two
    '<style>' strings inside JavaScript. The first double-counted fifteen keyframes; the second
    would have let a prune edit script source."""
    out, i = [], 0
    opener = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    while True:
        m = opener.search(t, i)
        if not m:
            return out
        if m.group(0) == '<!--':
            e = t.find('-->', m.end())
            if e < 0:
                raise SystemExit('ABORT: unterminated HTML comment at %d' % m.start())
            i = e + 3
            continue
        tag = m.group(1).lower()
        e = t.find('</%s>' % tag, m.end())
        if e < 0:
            raise SystemExit('ABORT: unterminated <%s> at %d' % (tag, m.start()))
        if tag == 'style':
            out.append((m.end(), e))
        i = e + len('</%s>' % tag)


def live_tokens(t, blocks, extra_prefixes):
    parts, prev = [], 0
    for s, e in blocks:
        parts.append(t[prev:s]); prev = e
    parts.append(t[prev:])
    rest = ''.join(parts)
    return set(WORD.findall(rest)), rest


def tokenize(css):
    """Yield (kind, start, end): 'comment', 'string', '{', '}', ';', 'text'."""
    i, n = 0, len(css)
    while i < n:
        c = css[i]
        if css.startswith('/*', i):
            j = css.find('*/', i + 2)
            j = n if j < 0 else j + 2
            yield ('comment', i, j); i = j
        elif c in '"\'':
            j = i + 1
            while j < n and css[j] != c:
                j += 2 if css[j] == '\\' else 1
            yield ('string', i, min(j + 1, n)); i = j + 1
        elif c in '{};':
            yield (c, i, i + 1); i += 1
        else:
            j = i
            while j < n and css[j] not in '{};"\'' and not css.startswith('/*', j):
                j += 1
            yield ('text', i, j); i = j


def parse(css, base=0):
    """A flat list of top-level items: {'kind':'rule'|'at', 'prelude':(s,e), 'block':(s,e)|None,
    'span':(s,e)} with absolute offsets. At-rule blocks are parsed recursively on demand."""
    items, toks = [], list(tokenize(css))
    k, pstart = 0, None
    while k < len(toks):
        kind, s, e = toks[k]
        if kind in ('comment',):
            k += 1; continue
        if pstart is None and kind == 'text' and not css[s:e].strip():
            k += 1; continue
        if pstart is None:
            pstart = s
        if kind == ';':
            items.append({'kind': 'at' if css[pstart:s].strip().startswith('@') else 'junk',
                          'prelude': (base + pstart, base + s), 'block': None, 'span': (base + pstart, base + e)})
            pstart = None; k += 1; continue
        if kind == '{':
            depth, j = 1, k + 1
            while j < len(toks) and depth:
                if toks[j][0] == '{': depth += 1
                elif toks[j][0] == '}': depth -= 1
                j += 1
            bs, be = e, toks[j - 1][1]
            pre = css[pstart:s].strip()
            items.append({'kind': 'at' if pre.startswith('@') else 'rule',
                          'prelude': (base + pstart, base + s), 'block': (base + bs, base + be),
                          'span': (base + pstart, base + toks[j - 1][2])})
            pstart = None; k = j; continue
        if kind == '}':
            raise SystemExit('ABORT: unbalanced } at %d' % (base + s))
        k += 1
    return items


def at_name(prelude):
    """The at-rule's name. '@media(max-width:720px)' is legal CSS with no space before the
    parenthesis, so the name is the @-identifier, not the first whitespace-separated word -- the
    first version split on whitespace and never looked inside such a block, and its own
    fixed-point check, sharing that code, could not see the blind spot. The suite's independent
    parser found it."""
    m = re.match(r'\s*(@[A-Za-z-]+)', prelude)
    return m.group(1).lower() if m else ''


def split_top(sel):
    out, depth, cur = [], 0, ''
    for ch in sel:
        if ch in '([': depth += 1
        elif ch in ')]': depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def parse_with_comments(css, base=0):
    """parse(), plus top-level comments as their own items, in document order."""
    items = parse(css, base)
    for kind, s, e in tokenize(css):
        pass
    # comments at the top level of this block: tokens outside any item span
    spans = [it['span'] for it in items]
    out = list(items)
    depth = 0
    for kind, s, e in tokenize(css):
        if kind == '{': depth += 1
        elif kind == '}': depth -= 1
        elif kind == 'comment' and depth == 0:
            a = base + s
            if not any(sp[0] <= a < sp[1] for sp in spans):
                out.append({'kind': 'comment', 'span': (a, base + e)})
    out.sort(key=lambda it: it['span'][0])
    return out


def plan_rules(t):
    blocks = style_blocks(t)
    live, rest = live_tokens(t, blocks, None)
    pre = None
    edits, stats = [], {'dead': 0, 'partial': 0, 'keyframes': 0, 'atblocks': 0, 'comments': 0}
    kf_live = set()

    def rule_names(it):
        body = t[it['block'][0]:it['block'][1]]
        out = set()
        for n in re.findall(r'animation(?:-name)?\s*:\s*([^;}]+)', body):
            out.update(re.findall(r'[A-Za-z_][\w-]*', n))
        return out

    def level(items):
        """Returns True when everything at this level is deleted."""
        all_gone, section, sections = True, [], []
        for it in items:
            if it['kind'] == 'comment':
                sections.append(section); section = [it]
            else:
                section.append(it)
        sections.append(section)
        for sec in sections:
            head = sec[0] if sec and sec[0]['kind'] == 'comment' else None
            members = [x for x in sec if x['kind'] != 'comment']
            gone_here = True
            for it in members:
                gone = False
                if it['kind'] == 'rule':
                    sels = split_top(t[it['prelude'][0]:it['prelude'][1]])
                    alive = [x for x in sels if selector_live(x, live, pre)]
                    if not alive:
                        edits.append((it['span'][0], it['span'][1], None)); stats['dead'] += 1; gone = True
                    else:
                        kf_live.update(rule_names(it))
                        if len(alive) < len(sels):
                            edits.append((it['prelude'][0], it['prelude'][1], ','.join(alive)))
                            stats['partial'] += 1
                elif it['kind'] == 'at' and it['block']:
                    head_txt = t[it['prelude'][0]:it['prelude'][1]].strip()
                    name = at_name(head_txt)
                    if name in ('@media', '@supports'):
                        s, e = it['block']
                        n0 = len(edits)
                        if level(parse_with_comments(t[s:e], s)):
                            del edits[n0:]                     # the whole at-rule goes instead
                            edits.append((it['span'][0], it['span'][1], None)); stats['atblocks'] += 1; gone = True
                    elif name.endswith('keyframes'):
                        it['kfname'] = head_txt.split()[1]
                gone_here = gone_here and gone
                all_gone = all_gone and gone
            if head is not None:
                if members and gone_here:
                    edits.append((head['span'][0], head['span'][1], None)); stats['comments'] += 1
                else:
                    all_gone = False
        return all_gone

    tops = []
    for s, e in blocks:
        items = parse_with_comments(t[s:e], s)
        tops.append((s, e, items))
        level(items)
    # keyframes: second pass, now that every live rule's animation names are known. A keyframes
    # block is recognised from its own prelude at every depth -- an earlier draft relied on a
    # marker set during the first pass, which a nested re-parse did not carry, so keyframes inside
    # a SURVIVING @media were silently skipped. One inside an at-rule already being deleted is
    # left to go with it, so no two edits overlap.
    gone = set((a, b) for a, b, r in edits if r is None)
    def kfwalk(items):
        for it in items:
            if it['kind'] != 'at' or not it['block'] or tuple(it['span']) in gone:
                continue
            head_txt = t[it['prelude'][0]:it['prelude'][1]].strip()
            name = at_name(head_txt)
            if name.endswith('keyframes'):
                kn = head_txt.split()[1]
                if kn not in kf_live and not re.search(r'\b%s\b' % re.escape(kn), rest):
                    edits.append((it['span'][0], it['span'][1], None)); stats['keyframes'] += 1
            elif name in ('@media', '@supports'):
                a, b = it['block']; kfwalk(parse_with_comments(t[a:b], a))
    for s, e, items in tops:
        kfwalk(items)
    return edits, stats


def tidy(t, s, e):
    """Widen a deletion to the whole line when the item is alone on it."""
    a = s
    while a > 0 and t[a - 1] in ' \t':
        a -= 1
    if a == 0 or t[a - 1] == '\n':
        b = e
        while b < len(t) and t[b] in ' \t':
            b += 1
        if b < len(t) and t[b] == '\n':
            return a, b + 1
    return s, e



TOKNAME = re.compile(r'-?[A-Za-z_][\w-]*')
ONE = re.compile(r'\s*(-?[A-Za-z_][\w-]*)\s*\Z')
MANY = re.compile(r'\s*-?[A-Za-z_][\w-]*(?:\s+-?[A-Za-z_][\w-]*)+\s*\Z')
ATTR = re.compile(r'\b(class|id)\s*=\s*(["\']?)')
SELCLS = re.compile(r'\.(-?[A-Za-z_][\w-]*)')


def attr_tokens(value, which):
    out = set()
    for m in ATTR.finditer(value):
        if m.group(1) != which:
            continue
        q, a = m.group(2), m.end()
        if q:
            b = value.find(q, a)
            b = len(value) if b < 0 else b
        else:
            b = a + re.match(r'[^\s>]*', value[a:]).end()
        out.update(TOKNAME.findall(value[a:b]))
    return out


def markup_tokens(t):
    """(classes, ids) from the class and id attributes of the markup outside scripts, styles and
    comments."""
    cls, ids, prev, rest = set(), set(), 0, []
    opener = re.compile(r'<!--|<(script|style)\b[^>]*>', re.I)
    low = t.lower()
    i = 0
    while True:
        m = opener.search(t, i)
        if not m:
            break
        rest.append(t[prev:m.start()])
        if m.group(0) == '<!--':
            i = prev = t.index('-->', m.end()) + 3
            continue
        tag = m.group(1).lower()
        e = low.index('</%s>' % tag, m.end())
        i = prev = e + len(tag) + 3
    rest.append(t[prev:])
    html = ''.join(rest)
    for m in re.finditer(r'\b(class|id)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', html):
        v = m.group(2) if m.group(2) is not None else m.group(3)
        (cls if m.group(1) == 'class' else ids).update(TOKNAME.findall(v))
    return cls, ids


def dynamic_prefixes(t):
    """A literal ending in '-' that is concatenated: 'a3d-'+kind. Its prefix keeps every name --
    except where what is concatenated is Date.now() or Math.random(): 'a3d-'+Date.now() makes an
    object's unique id, which no stylesheet can name, and it would otherwise keep every a3d- class
    in the file alive."""
    pre = set()
    for s, e, kind, v in literals(t):
        if kind != 'string':
            continue
        m = re.search(r'(-?[A-Za-z_][\w-]*-)\Z', v)
        after = t[e:e + 60].lstrip()
        if m and after.startswith('+') and not re.match(r'\+\s*(Date\.now|Math\.)', after):
            pre.add(m.group(1))
    return pre


def live_sets(t):
    """(classes, ids) that some element can carry.

    A class is live from a class attribute, from any literal that is one name (' active',
    'open'), from a literal that is several names at least one of which is hyphenated (a class
    list: 'st-card st-has-del' -- 'the viewport' is a message, not a list), from a selector in a
    literal (.name, for a query), and from any regex. An id is live only where an element is
    GIVEN it: an id attribute, a literal assigned to .id or passed to setAttribute('id'), or a
    one-name literal that is hyphenated or underscored the way this file names ids (so that an
    id kept in a table and assigned from it still counts). 'world', the gizmo's alignment mode,
    does not make #world an element."""
    cls, ids = markup_tokens(t)
    for s, e, kind, v, ctx in literals_ctx(t):
        if kind == 'regex':
            cls.update(TOKNAME.findall(v)); ids.update(TOKNAME.findall(v))
            continue
        cls.update(attr_tokens(v, 'class'))
        ids.update(attr_tokens(v, 'id'))
        one = ONE.match(v)
        if one:
            cls.add(one.group(1))
            if ctx.endswith('. id =') or re.search(r'setAttribute \( STR:id ,$', ctx) or re.search(r'[-_]', one.group(1)):
                ids.add(one.group(1))
        elif MANY.match(v) and any('-' in w for w in TOKNAME.findall(v)):
            cls.update(TOKNAME.findall(v))
        cls.update(SELCLS.findall(v))
    return cls, ids


def required_kinds(sel):
    """[('.', name) | ('#', name)] a selector requires, outside :not() and attribute brackets."""
    out, depth = '', 0
    for ch in sel:
        if ch in '([':
            depth += 1; continue
        if ch in ')]':
            depth -= 1; continue
        if depth == 0:
            out += ch
    return re.findall(r'([.#])(-?[A-Za-z_][\w-]*)', out)



CLS, IDS, PRE = set(), set(), set()


def selector_live(sel, live, prefixes):
    """A .class against the live classes, an #id against the live ids, a runtime-built name against
    its literal prefix."""
    for kind, tok in required_kinds(sel):
        if tok in (CLS if kind == '.' else IDS):
            continue
        if any(tok.startswith(p) for p in PRE):
            continue
        return False
    return True


def plan(t):
    global CLS, IDS, PRE
    CLS, IDS = live_sets(t)
    PRE = dynamic_prefixes(t)
    return plan_rules(t)


def tidy(t, s, e):
    """Widen a deletion to the whole line when the item is alone on it."""
    a = s
    while a > 0 and t[a - 1] in ' \t':
        a -= 1
    if a == 0 or t[a - 1] == '\n':
        b = e
        while b < len(t) and t[b] in ' \t':
            b += 1
        if b < len(t) and t[b] == '\n':
            return a, b + 1
    return s, e


edits, stats = plan(t)
WANT = {'dead': 145, 'partial': 3, 'keyframes': 0, 'atblocks': 2, 'comments': 18}
for k, v in WANT.items():
    if stats[k] != v:
        sys.exit('ABORT: %s is %d, measured %d -- the input is not the file this was written against' % (k, stats[k], v))
edits.sort(key=lambda x: x[0], reverse=True)
last = len(t) + 1
for s, e, rep_ in edits:
    if e > last:
        sys.exit('ABORT: overlapping edits at %d' % s)
    if rep_ is None:
        s, e = tidy(t, s, e)
        t = t[:s] + t[e:]
    else:
        t = t[:s] + rep_ + t[e:]
    last = s

# a <style> element left with nothing but whitespace and comments goes too, unless script reaches it by id
emptied = 0
for m in list(re.finditer(r'<style\b([^>]*)>(.*?)</style>\n?', t, re.S))[::-1]:
    if re.sub(r'/\*.*?\*/', '', m.group(2), flags=re.S).strip():
        continue
    sid = re.search(r'id="([^"]+)"', m.group(1))
    if sid and re.search(r'\b%s\b' % re.escape(sid.group(1)), t[:m.start()] + t[m.end():]):
        continue
    t = t[:m.start()] + t[m.end():]
    emptied += 1
print('pruned', stats, 'emptied style elements', emptied)

again, st2 = plan(t)
if st2['dead'] or st2['partial'] or st2['keyframes'] or st2['atblocks']:
    sys.exit('ABORT: the pruned file still analyses as dead: %r' % st2)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
