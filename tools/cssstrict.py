"""cssstrict.py -- which CSS rules can never match, with liveness read from where a class or an id can
actually come from.

V114c/V117e's planner kept a rule alive when its #id or .class appeared ANYWHERE outside the
stylesheets, a comment or a message included. That is why the whiteboard's stylesheet outlived the
whiteboard by seven phases: #viewport stays alive while a toast says "the viewport", .node while a
prompt says "place a node", #world while a comment says "world". Here a name is live only where it
can reach an element:

  - the static markup's class and id attributes;
  - a string literal holding an HTML fragment, from class=" or id=" to the end of the value;
  - a string literal that is nothing but names (a class list, an id, ' active', 'a3d-dock');
  - a string literal holding a selector (.name or #name), which a query or a matches() may use;
  - a regex literal, conservatively;
  - a name built at run time from a literal prefix ('a3d-'+kind), which keeps its whole prefix.

A message such as 'Point: click to place a node' is none of these, so it keeps nothing alive.
The literals come from jslex, which is checked against acorn's token stream on the same build."""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jslex
import cssdead

NAME = re.compile(r'-?[A-Za-z_][\w-]*')
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
        out.update(NAME.findall(value[a:b]))
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
        (cls if m.group(1) == 'class' else ids).update(NAME.findall(v))
    return cls, ids


def dynamic_prefixes(t):
    """A literal ending in '-' that is concatenated: 'a3d-'+kind. Its prefix keeps every name --
    except where what is concatenated is Date.now() or Math.random(): 'a3d-'+Date.now() makes an
    object's unique id, which no stylesheet can name, and it would otherwise keep every a3d- class
    in the file alive."""
    pre = set()
    for s, e, kind, v in jslex.literals(t):
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
    for s, e, kind, v, ctx in jslex.literals_ctx(t):
        if kind == 'regex':
            cls.update(NAME.findall(v)); ids.update(NAME.findall(v))
            continue
        cls.update(attr_tokens(v, 'class'))
        ids.update(attr_tokens(v, 'id'))
        one = ONE.match(v)
        if one:
            cls.add(one.group(1))
            if ctx.endswith('. id =') or re.search(r'setAttribute \( STR:id ,$', ctx) or re.search(r'[-_]', one.group(1)):
                ids.add(one.group(1))
        elif MANY.match(v) and any('-' in w for w in NAME.findall(v)):
            cls.update(NAME.findall(v))
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


def plan(t):
    """The V117 planner, with selector liveness decided per kind: a .class against the live
    classes, an #id against the live ids, a runtime-built name against its literal prefix."""
    cls, ids = live_sets(t)
    pre = dynamic_prefixes(t)

    def selector_live(sel, live, prefixes):
        for kind, tok in required_kinds(sel):
            if tok in (cls if kind == '.' else ids):
                continue
            if any(tok.startswith(p) for p in pre):
                continue
            return False
        return True
    orig = cssdead.selector_live
    cssdead.selector_live = selector_live
    try:
        return cssdead.plan(t, set())
    finally:
        cssdead.selector_live = orig


if __name__ == '__main__':
    t = open(sys.argv[1], encoding='utf-8').read()
    edits, stats = plan(t)
    print(stats)
    print('dynamic prefixes:', sorted(dynamic_prefixes(t)))
    c_, i_ = live_sets(t)
    print('live classes', len(c_), 'live ids', len(i_))

    def ln(a):
        return t.count('\n', 0, a) + 1
    tot = 0
    for s, e, r in sorted(edits):
        tot += e - s
        if '-v' in sys.argv:
            print('L%d %s' % (ln(s), (t[s:e] if r is None else ('TRIM-> ' + r))[:150].replace('\n', ' ')))
    print('chars in dead spans', tot)
