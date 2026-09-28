"""patch_phase119c.py -- V119: delete the CSS that can never match an element, now that the view
dropdown is gone: the label's rules, its menu's, and the Start page's rule that hid the label.

patch_phase114c.py's derivation again, unchanged but for the name, the baseline and the counts: a
selector is dead when it requires an #id or .class that nothing outside the stylesheets writes. The
counts are the ones measured on this patch's input, and the output must re-analyse to nothing dead.
"""
NAME = 'patch_phase119c.py'
BASE = '7140d6949ecc8e05e3691fcd361f2985fa1dab7ea3c21d4ebd712ebf897cb1b7'
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
import re, sys

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


def dynamic_prefixes(rest):
    """String literals that end in '-' and are concatenated or interpolated: 'fl-'+x, `a3d-${k}`.
    Any CSS token with such a prefix is treated as live, because it may be built at run time."""
    pre = set()
    for m in re.finditer(r"""['"]([A-Za-z_][\w-]*-)['"]\s*\+""", rest):
        pre.add(m.group(1))
    for m in re.finditer(r"""\+\s*['"]([A-Za-z_][\w-]*-)['"]""", rest):
        pre.add(m.group(1))
    for m in re.finditer(r"""([A-Za-z_][\w-]*-)\$\{""", rest):
        pre.add(m.group(1))
    return pre


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


def required(sel):
    """The #ids and .classes a selector requires to match."""
    s, depth, out = '', 0, ''
    for ch in sel:
        if ch in '([':
            depth += 1; continue
        if ch in ')]':
            depth -= 1; continue
        if depth == 0:
            out += ch
    return re.findall(r'[.#]([A-Za-z_][\w-]*)', out)


def selector_live(sel, live, prefixes):
    for tok in required(sel):
        if tok in live:
            continue
        if any(tok.startswith(p) for p in prefixes):
            continue
        return False
    return True


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


def plan(t):
    blocks = style_blocks(t)
    live, rest = live_tokens(t, blocks, None)
    pre = dynamic_prefixes(rest)
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


edits, stats = plan(t)
DEAD, PARTIAL, KEYFRAMES = 13, 0, 0   # measured by the stand-alone analyzer on this patch's input (the 119b output)
WANT = {'dead': DEAD, 'partial': PARTIAL, 'keyframes': KEYFRAMES}
for k, v in WANT.items():
    if stats[k] != v:
        sys.exit('ABORT: %s is %d, measured %d -- the input is not the file this was written against'
                 % (k, stats[k], v))
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

# A <style> element left with nothing in it goes too, unless live script reaches it by id.
for m in list(re.finditer(r'<style\b([^>]*)>(.*?)</style>\n?', t, re.S))[::-1]:
    if m.group(2).strip():
        continue
    sid = re.search(r'id="([^"]+)"', m.group(1))
    if sid and re.search(r'\b%s\b' % re.escape(sid.group(1)), t[:m.start()] + t[m.end():]):
        continue
    t = t[:m.start()] + t[m.end():]
    stats['emptied'] = stats.get('emptied', 0) + 1

# The fixed point: the output must re-analyse to nothing dead.
again, st2 = plan(t)
if st2['dead'] or st2['partial'] or st2['keyframes']:
    sys.exit('ABORT: the pruned file still analyses as dead: %r' % st2)
print('pruned', stats)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
