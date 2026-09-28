"""deadfuncs.py -- function declarations whose name is mentioned nowhere else: not as an identifier,
not inside a string, not in the markup. Scope-blind on purpose (a name used anywhere keeps every
declaration of it), so it can only err towards keeping. Uses jslex, checked against acorn."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jslex

WORD = re.compile(r'[A-Za-z_$][\w$]*')
EXPR_BEFORE = set('=(,:?[!&|+-*/%<>~^')


def declarations(t):
    """[(name, start, end)] of function DECLARATIONS (statement position), end after the '}'."""
    out = []
    for s, e in jslex.script_blocks(t):
        code = t[s:e]
        toks = [(k, a, b) for k, a, b in jslex.lex(code) if k != 'comment']
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
    for s, e in jslex.script_blocks(t):
        code = t[s:e]
        for k, a, b in jslex.lex(code):
            if k == 'comment':
                continue
            txt = code[a:b]
            if k == 'string':
                txt = jslex.decode(txt[1:-1])
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


if __name__ == '__main__':
    t = open(sys.argv[1], encoding='utf-8').read()
    d = declarations(t)
    print('declarations', len(d))
    for name, s, e in dead(t):
        print('DEAD L%d %s (%d chars)' % (t.count('\n', 0, s) + 1, name, e - s))
