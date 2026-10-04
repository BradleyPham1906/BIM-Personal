#!/usr/bin/env python3
"""build_docs.py -- the user guide, built from the repository.

  python3 tools/build_docs.py [--check]

Writes docs/*.html from:
- docs/src/*.md -- the guide's pages, in our own words (a small Markdown subset: headings, paragraphs,
  lists, tables, code, links, bold, italics; a front matter block gives each page's title and order);
- docs/data/catalog.json -- the app's own command catalogue and keys (tools/dump_catalog.py), for
  the command reference;
- canvas_v10_STATUS.md -- every phase's entry, for the release notes;
- Phase/canvas_v10.html.bak_phase*_pre -- the builds kept before each phase, for the versions page
  (tools/build_site.py publishes them at v/<version>/).

No dependencies beyond Python's standard library, so the Pages workflow can run it as it is. With
--check it writes nothing and exits 1 when docs/ is not what it would write."""
import html, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / 'docs' / 'src', ROOT / 'docs'
REPO = 'https://github.com/BradleyPham1906/BIM-Personal'
SITE = 'https://bradleypham1906.github.io/BIM-Personal/'


# ---------------------------------------------------------------- Markdown, a small subset
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', lambda m: '<code>%s</code>' % m.group(1), s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*([^*\s][^*]*)\*(?!\w)', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: '<a href="%s">%s</a>' % (html.escape(m.group(2)), m.group(1)), s)
    return s


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', s).lower()).strip('-')


def md(text):
    """Markdown to HTML: headings (with ids), paragraphs, nested lists, tables, fenced code."""
    lines, out, i = text.split('\n'), [], 0
    toc = []

    def flush_list(items):
        # items: [(indent, ordered, text)] -> nested <ul>/<ol>
        res, stack = [], []
        for ind, ordered, txt in items:
            while stack and stack[-1][0] > ind:
                res.append('</li></%s>' % stack.pop()[1])
            if not stack or stack[-1][0] < ind:
                tag = 'ol' if ordered else 'ul'
                res.append('<%s>' % tag)
                stack.append((ind, tag))
            else:
                res.append('</li>')
            res.append('<li>' + inline(txt))
        while stack:
            res.append('</li></%s>' % stack.pop()[1])
        return ''.join(res)
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith('```'):
            j = i + 1
            while j < len(lines) and not lines[j].startswith('```'):
                j += 1
            out.append('<pre><code>%s</code></pre>' % html.escape('\n'.join(lines[i + 1:j])))
            i = j + 1
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', ln)
        if m:
            lv, tx = len(m.group(1)), inline(m.group(2))
            sid = slug(m.group(2))
            if lv == 2:
                toc.append((sid, tx))
            out.append('<h%d id="%s">%s</h%d>' % (lv, sid, tx, lv))
            i += 1
            continue
        if ln.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.match(r'^:?-+:?$', c) for c in r)]
            out.append('<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (
                ''.join('<th>%s</th>' % inline(c) for c in head),
                ''.join('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c) for c in r) for r in body)))
            continue
        if re.match(r'^\s*([-*]|\d+\.)\s+', ln):
            items = []
            while i < len(lines) and (re.match(r'^\s*([-*]|\d+\.)\s+', lines[i]) or (lines[i].startswith('  ') and lines[i].strip() and items)):
                mm = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)$', lines[i])
                if mm:
                    items.append((len(mm.group(1)), mm.group(2)[0].isdigit(), mm.group(3)))
                else:
                    ind, o, tx = items[-1]
                    items[-1] = (ind, o, tx + ' ' + lines[i].strip())
                i += 1
            out.append(flush_list(items))
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,4}\s|\s*\||```|\s*([-*]|\d+\.)\s)', lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append('<p>%s</p>' % inline(' '.join(para)))
    return '\n'.join(out), toc


def front(text):
    meta = {}
    if text.startswith('---\n'):
        end = text.index('\n---\n', 4)
        for ln in text[4:end].split('\n'):
            if ':' in ln:
                k, v = ln.split(':', 1)
                meta[k.strip()] = v.strip()
        text = text[end + 5:]
    return meta, text


# ---------------------------------------------------------------- the page
CSS = """
:root{--bg:#ffffff;--fg:#1d2329;--mut:#5b6670;--line:#e3e7eb;--side:#f6f7f9;--acc:#2f6fd6;--code:#f1f3f5}
@media (prefers-color-scheme:dark){:root{--bg:#16191d;--fg:#e4e8ec;--mut:#9aa5b0;--line:#2c3238;--side:#1d2126;--acc:#6ea0ff;--code:#22272d}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 Inter,system-ui,-apple-system,Segoe UI,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
.wrap{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}
nav.side{background:var(--side);border-right:1px solid var(--line);padding:18px 16px;position:sticky;top:0;height:100vh;overflow:auto}
nav.side .brand{font-weight:700;font-size:16px;margin-bottom:2px}
nav.side .ver{color:var(--mut);font-size:12px;margin-bottom:14px}
nav.side a{display:block;padding:4px 8px;border-radius:6px;color:var(--fg);font-size:14px}
nav.side a.on{background:rgba(47,111,214,.12);color:var(--acc);font-weight:600}
nav.side .sep{border-top:1px solid var(--line);margin:10px 0}
main{padding:28px 40px 60px;max-width:900px}
h1{font-size:28px;margin:0 0 14px}h2{font-size:20px;margin:30px 0 8px;padding-top:6px;border-top:1px solid var(--line)}h3{font-size:16px;margin:20px 0 6px}
code{background:var(--code);padding:1px 5px;border-radius:4px;font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--code);padding:12px;border-radius:8px;overflow:auto}pre code{padding:0}
table{border-collapse:collapse;width:100%;margin:10px 0 16px;font-size:14px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}th{background:var(--side)}
ul,ol{padding-left:22px}li{margin:3px 0}
.toc{font-size:13px;color:var(--mut);margin:-4px 0 18px}.toc a{margin-right:12px}
.cmd{border:1px solid var(--line);border-radius:9px;padding:10px 14px;margin:10px 0}
.cmd h3{margin:0 0 4px;font-size:16px}.cmd .al{color:var(--mut);font-size:13px}.cmd .wh{color:var(--mut);font-size:13px}
.cmd:target{border-color:var(--acc);box-shadow:0 0 0 2px rgba(47,111,214,.25)}
.filter{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg);font:inherit;margin:6px 0 10px}
.rel{border-left:3px solid var(--line);padding:2px 0 2px 14px;margin:14px 0}.rel:target{border-left-color:var(--acc)}
.rel h3{margin:0}.rel p{margin:4px 0;color:var(--fg)}
footer{color:var(--mut);font-size:12px;margin-top:40px;border-top:1px solid var(--line);padding-top:10px}
@media (max-width:760px){.wrap{display:block}nav.side{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}main{padding:18px 16px 40px}}
"""


def page(title, body, pages, cur, version, toc=None, script=''):
    nav = ''.join('<a href="%s"%s>%s</a>' % (p['file'], ' class="on"' if p['file'] == cur else '', html.escape(p['title'])) for p in pages)
    nav += '<div class="sep"></div>' + ''.join('<a href="%s"%s>%s</a>' % (f, ' class="on"' if f == cur else '', t) for f, t in (
        ('commands.html', 'Command reference'), ('changelog.html', 'Release notes'), ('versions.html', 'Versions')))
    nav += '<div class="sep"></div><a href="../index.html">Open the app</a><a href="%s">Source on GitHub</a>' % REPO
    tocs = '<div class="toc">%s</div>' % ''.join('<a href="#%s">%s</a>' % (a, t) for a, t in toc) if toc and len(toc) > 2 else ''
    h1 = re.search(r'<h1[^>]*>.*?</h1>', body)
    if h1 and tocs:
        body = body.replace(h1.group(0), h1.group(0) + tocs, 1)
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>%s - BIM Personal guide</title><style>%s</style></head><body><div class="wrap">'
            '<nav class="side"><div class="brand">BIM Personal</div><div class="ver">User guide for %s, %s</div>%s</nav>'
            '<main>%s<footer>Guide for %s (%s). Built from the repository by tools/build_docs.py.</footer></main></div>%s</body></html>\n') % (
        html.escape(title), CSS, version['v'], version['date'], nav, body, version['v'], version['date'], script)


# ---------------------------------------------------------------- the generated pages
def commands_page(cat):
    groups = {}
    for c in cat['commands']:
        key = c['where'][0].split(' › ')[0] if c['where'] else 'In the command search'
        groups.setdefault(key, []).append(c)
    order = sorted(groups, key=lambda k: (k == 'In the command search', k))
    b = ['<h1 id="command-reference">Command reference</h1>',
         '<p>Every command and ribbon tool in this version, from the same catalogue the command search uses. '
         'In the app, type a name or an alias (<strong>Ctrl K</strong>, or just start typing on the drawing), and press '
         '<strong>F1</strong> on a highlighted command to come back to its entry here.</p>',
         '<input class="filter" type="search" id="f" placeholder="Filter: a name, an alias or a word" aria-label="Filter the commands">',
         '<p id="n" class="toc"></p>']
    for g in order:
        b.append('<section class="grpw"><h2 id="%s" class="grp">%s</h2>' % (slug(g), html.escape(g)))
        for c in sorted(groups[g], key=lambda c: c['name']):
            al = ', '.join(c['aliases'])
            b.append('<div class="cmd" id="%s" data-s="%s"><h3>%s</h3>%s<div>%s</div>%s%s</div>' % (
                html.escape(c['anchor']), html.escape((c['name'] + ' ' + al + ' ' + c['desc']).lower()), html.escape(c['name']),
                '<div class="al">Aliases: %s</div>' % html.escape(al) if al else '', inline(c['desc']),
                '<div class="wh">On the ribbon: %s</div>' % html.escape('; '.join(c['where'])) if c['where'] else '',
                '<div class="wh">Keys: %s</div>' % html.escape(' '.join(c['keys']) if isinstance(c['keys'], list) else str(c['keys'])) if c['keys'] else ''))
        b.append('</section>')
    b.append('<h2 id="keyboard-shortcuts">Keyboard shortcuts</h2>')
    for g in cat['shortcuts']:
        b.append('<h3 id="keys-%s">%s</h3><table><thead><tr><th>Keys</th><th>What it does</th></tr></thead><tbody>%s</tbody></table>' % (
            slug(g['grp']), html.escape(g['grp']), ''.join('<tr><td><code>%s</code></td><td>%s%s</td></tr>' % (
                html.escape((' or ' if r['alt'] else ' + ').join(r['keys'])), html.escape(r['label']), (' (%s)' % html.escape(r['cmd'])) if r.get('cmd') else '')
                for r in g['rows'])))
    script = ('<script>(function(){var f=document.getElementById("f"),n=document.getElementById("n"),C=document.querySelectorAll(".cmd");'
              'function go(){var q=f.value.toLowerCase().replace(/^\\s+|\\s+$/g,""),k=0,i;for(i=0;i<C.length;i++){var on=!q||C[i].getAttribute("data-s").indexOf(q)>=0;'
              'C[i].style.display=on?"":"none";if(on)k++;}var S=document.querySelectorAll(".grpw");for(i=0;i<S.length;i++){var v=0,c=S[i].querySelectorAll(".cmd"),j;'
              'for(j=0;j<c.length;j++)if(c[j].style.display!=="none")v++;S[i].style.display=v?"":"none";}n.textContent=k+" of "+C.length+" commands";}'
              'f.addEventListener("input",go);go();})();</script>')
    return '\n'.join(b), script


STATUS_HEAD = re.compile(r'^## (?:Phase (?P<p>[0-9a-z ]+?)(?: and [0-9a-z]+)?(?:, part \d+)? \((?P<v>V[0-9a-z]+)(?:, V[0-9a-z]+)*\)(?:, part \d+)?|Session (?P<d>\d{4}-\d{2}-\d{2}): (?P<t2>.*?) \(__acad3d(?P<v2>V[0-9a-z]+)\))(?: - (?P<t>.*))?$')


def changelog(status_text):
    entries, lines = [], status_text.split('\n')
    for i, ln in enumerate(lines):
        m = STATUS_HEAD.match(ln)
        if not m:
            continue
        v = m.group('v') or m.group('v2')
        title = (m.group('t') or m.group('t2') or '').strip()
        para, j = [], i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        while j < len(lines) and lines[j].strip() and not lines[j].startswith('#'):
            para.append(lines[j].strip())
            j += 1
        summary = ' '.join(para)
        if len(summary) > 420:
            summary = summary[:420].rsplit(' ', 1)[0] + ' ...'
        ids = []
        for x in re.findall(r'\bV(\d+[a-z]?)\b', ln):
            if 'v' + x not in ids:
                ids.append('v' + x)
        entries.append({'v': v, 'title': title, 'summary': summary, 'date': m.group('d'), 'ids': ids})
    def key(e):
        mm = re.match(r'V(\d+)([a-z]?)', e['v'])
        return (int(mm.group(1)), mm.group(2))
    entries.sort(key=key, reverse=True)
    return entries


def changelog_page(entries):
    b = ['<h1 id="release-notes">Release notes</h1>',
         '<p>Newest first. Each version is a phase of work, verified before it ships (its own test suite, every older suite, and deliberately broken builds the suite must catch). '
         'The full engineering log, with the bugs found and the tests, is <a href="%s/blob/main/canvas_v10_STATUS.md">canvas_v10_STATUS.md</a>.</p>' % REPO]
    for e in entries:
        b.append('<div class="rel" id="%s">%s<h3>%s - %s</h3>%s<p>%s</p></div>' % (
            e['v'].lower(), ''.join('<span id="%s"></span>' % i for i in e['ids'] if i != e['v'].lower()), html.escape(e['v']), inline(e['title']), '<div class="toc">%s</div>' % e['date'] if e['date'] else '', inline(e['summary'])))
    b.append('<p>Earlier versions (V1 to V86) are recorded in the engineering log above.</p>')
    return '\n'.join(b)


MARK = re.compile(r'__acad3dV(\d+)([a-z]?)(?![a-z0-9])')   # a phase's marker, in code or in its comments


def kept_versions():
    """[(label, backup path)]: each build kept before a phase, named by the newest marker in it."""
    out = {}
    for p in sorted((ROOT / 'Phase').glob('canvas_v10.html.bak_phase*_pre')):
        t = p.read_text(encoding='utf-8', errors='replace')
        ms = [(int(a), b) for a, b in MARK.findall(t)]
        if not ms:
            continue
        n, s = max(ms)
        out['V%d%s' % (n, s)] = p
    return sorted(out.items(), key=lambda kv: (int(re.match(r'V(\d+)', kv[0]).group(1)), kv[0]))


def versions_page(version, kept, entries):
    ids = set(i for e in entries for i in e['ids'])

    def notes(lab):
        a = lab.lower()
        if a not in ids:
            a = re.match(r'v\d+', a).group(0)
        return '<a href="changelog.html#%s">notes</a>' % a if a in ids else 'in the engineering log'
    b = ['<h1 id="versions">Versions</h1>',
         '<p>The site always opens the newest version, <strong>%s</strong> (%s). Every version below is kept on the site as it was, '
         'so a project or a screenshot can be checked against the build it was made with. They are the builds kept in the repository before each phase.</p>' % (version['v'], version['date']),
         '<table><thead><tr><th>Version</th><th>Open it</th><th>Release notes</th></tr></thead><tbody>',
         '<tr><td><strong>%s</strong> (newest)</td><td><a href="../index.html">the app</a></td><td><a href="changelog.html#%s">notes</a></td></tr>' % (version['v'], version['v'].lower())]
    for lab, _ in reversed(kept):
        b.append('<tr><td>%s</td><td><a href="../v/%s/index.html">v/%s/</a></td><td>%s</td></tr>' % (lab, lab.lower(), lab.lower(), notes(lab)))
    b.append('</tbody></table><p>The older builds open on the website; in a copy of the repository, open the files in <code>Phase/</code> instead.</p>')
    return '\n'.join(b)


# ---------------------------------------------------------------- build
def build():
    cat = json.loads((OUT / 'data' / 'catalog.json').read_text(encoding='utf-8'))
    version = cat['version']
    srcs = []
    for f in sorted(SRC.glob('*.md')):
        meta, text = front(f.read_text(encoding='utf-8'))
        srcs.append({'file': f.stem + '.html', 'title': meta.get('title', f.stem), 'order': int(meta.get('order', 99)), 'text': text})
    srcs.sort(key=lambda p: (p['order'], p['file']))
    files = {}
    for p in srcs:
        body, toc = md(p['text'])
        files[p['file']] = page(p['title'], body, srcs, p['file'], version, toc)
    body, script = commands_page(cat)
    files['commands.html'] = page('Command reference', body, srcs, 'commands.html', version, script=script)
    entries = changelog((ROOT / 'canvas_v10_STATUS.md').read_text(encoding='utf-8'))
    files['changelog.html'] = page('Release notes', changelog_page(entries), srcs, 'changelog.html', version)
    files['versions.html'] = page('Versions', versions_page(version, kept_versions(), entries), srcs, 'versions.html', version)
    return files


def main():
    files = build()
    stale = [n for n, t in files.items() if not (OUT / n).exists() or (OUT / n).read_text(encoding='utf-8') != t]
    gone = [p.name for p in OUT.glob('*.html') if p.name not in files]
    if '--check' in sys.argv:
        if stale or gone:
            print('docs/ is out of date: %s' % ', '.join(stale + gone))
            sys.exit(1)
        print('docs/ is current: %d pages' % len(files))
        return
    for n, t in files.items():
        (OUT / n).write_text(t, encoding='utf-8')
    for n in gone:
        (OUT / n).unlink()
    print('wrote %d pages to docs/ (%d changed)' % (len(files), len(stale)))


if __name__ == '__main__':
    main()
