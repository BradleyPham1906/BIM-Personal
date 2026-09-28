"""jslex.py -- a small JavaScript lexer: enough to find every comment, string, template and regex
literal in the build's scripts. It is checked against acorn's token stream on the build it is
used on (tools/lexcheck.js), because a lexer that misreads one regex reads every string after it
wrong."""
import re

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
