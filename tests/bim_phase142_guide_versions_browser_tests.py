#!/usr/bin/env python3
"""bim_phase142_guide_versions_browser_tests.py -- V142: the user guide, and versions.

The owner: documentation "like AutoCAD and Rhinoceros on their websites", and versioning. The
guide must not drift from the app, so this suite holds it to the build:

  1. THE APP KNOWS ITS VERSION: Properties > Project > Statistics says it, with links to its release
     notes and the guide; DOCS and RELEASENOTES open them; F1 in the command search opens the
     highlighted command's entry.
  2. THE GUIDE IS CURRENT: docs/data/catalog.json is the build's own catalogue and keys;
     tools/build_docs.py --check passes.
  3. THE GUIDE IS TRUE: every command a page names runs in this build; every link inside the guide
     reaches a page and an anchor that exist; every command has its entry; the notes have every
     phase, newest first, this version included; the versions page lists every kept build.
  4. THE SITE: tools/build_site.py gives the app, the guide and each older build at v/<version>/.
  5. THE PAGES: open with no errors, no outside scripts, the filter works, and a phone-width page does
     not scroll sideways.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, subprocess, sys, tempfile, traceback, filecmp
from html.parser import HTMLParser
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / 'canvas_v10.html'
DOCS = ROOT / 'docs'
sys.path.insert(0, str(ROOT / 'tools'))
import build_docs  # noqa: E402


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 60


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.scripts = set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a' and a.get('href'):
            self.hrefs.append(a['href'])
        if tag == 'script' and a.get('src'):
            self.scripts.append(a['src'])


def parse(p):
    L = Links()
    L.feed(p.read_text(encoding='utf-8'))
    return L


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        await ctx.add_init_script("window.__opened=[];window.open=function(u){window.__opened.push(String(u));return null;};")
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None):
            try:
                return await within(page.evaluate(js, arg) if arg is not None else page.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>window.__acad3dV142")
        ck(bool(has) and 'f1help' in has, "__acad3dV142 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def opened():
            return await safe("()=>window.__opened.slice()") or []

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the app knows its version")
            ver = await safe("()=>window.__a3dVersion()") or {}
            ck(ver.get('v') == 'V142' and re.match(r'^\d{4}-\d{2}-\d{2}$', ver.get('date', '')), "the app says it is V142, with a date (%s)" % ver)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('project');window.__a3dRefreshProps();}")
            await page.wait_for_timeout(100)
            row = await safe("""()=>{var a=document.querySelector('#a3d-propsbody [data-docslink="notes"]'),g=document.querySelector('#a3d-propsbody [data-docslink="guide"]');
              return a&&g?{notes:a.getAttribute('href'),text:a.textContent,guide:g.getAttribute('href'),vis:a.getBoundingClientRect().height>0,
                grp:a.closest('.a3d-pgbody').previousElementSibling.getAttribute('data-a3dpgrp')}:null;}""")
            ck(row and row['notes'] == 'docs/changelog.html#v142' and row['guide'] == 'docs/index.html' and row['text'].startswith('V142, ') and row['vis'] and row['grp'] == 'Statistics',
               "Statistics, on the Project tab, shows the version linked to its notes, and the guide (%s)" % row)
            ck((HTML.parent / 'docs' / 'changelog.html').exists() and (HTML.parent / 'docs' / 'index.html').exists() or (DOCS / 'index.html').exists(),
               "the links reach files beside the app")
            await safe("()=>window.__a3dRunCmd('docs')")
            await safe("()=>window.__a3dRunCmd('releasenotes')")
            o = await opened()
            ck(o[-2:] == ['docs/index.html', 'docs/changelog.html#v142'] and 'Opening the user guide' in await toast(), "DOCS opens the guide; RELEASENOTES this version's notes (%s)" % o[-2:])
            # F1 in the command search
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type('cityjsonout')
            await page.wait_for_timeout(200)
            top = await safe("()=>{var r=document.querySelector('#a3d-cmdpal .a3d-cmdrow.active .a3d-cmdname');return r?r.textContent:null;}")
            await page.keyboard.press('F1')
            await page.wait_for_timeout(150)
            o = await opened()
            shown = await safe("()=>document.getElementById('a3d-cmdpal').classList.contains('show')")
            ck(top and 'CITYJSONOUT' in top and o[-1] == 'docs/commands.html#cmd-CITYJSONOUT' and shown is False,
               "F1 on CITYJSONOUT in the command search opens its entry and closes the search (%s)" % o[-1:])
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(150)
            await page.keyboard.type('?undo')
            await page.wait_for_timeout(200)
            await page.keyboard.press('F1')
            await page.wait_for_timeout(150)
            ck((await opened())[-1] == 'docs/index.html', "F1 on a keyboard shortcut opens the guide")
            for q_, n_ in (('help', 'DOCS'), ('changelog', 'RELEASENOTES'), ('manual', 'DOCS')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the guide is current")
            cat = json.loads((DOCS / 'data' / 'catalog.json').read_text(encoding='utf-8'))
            live = await safe("""()=>window.__a3dCommandCatalog().map(function(c){return [c.id,c.name,(c.aliases||[]).join(','),c.desc||'',(c.where||[]).join(';'),window.__a3dDocsAnchor(c.id)];}).sort()""") or []
            mine = sorted([[c['id'], c['name'], ','.join(c['aliases']), c['desc'], ';'.join(c['where']), c['anchor']] for c in cat['commands']])
            ck(live and live == mine, "docs/data/catalog.json is this build's catalogue, entry for entry (%d; rerun tools/dump_catalog.py if not)" % len(live))
            keys = await safe("()=>window.__a3dShortcuts().map(function(g){return [g.grp,g.rows.map(function(r){return r.label;})];})")
            ck(keys == [[g['grp'], [r['label'] for r in g['rows']]] for g in cat['shortcuts']] and cat['version'] == ver, "and its keyboard shortcuts and version")
            pr = subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_docs.py'), '--check'], capture_output=True, text=True, timeout=120)
            ck(pr.returncode == 0, "tools/build_docs.py --check: docs/ is what the sources make (%s)" % (pr.stdout + pr.stderr).strip()[-200:])

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the guide is true")
            names = set()
            for c in cat['commands']:
                names.add(c['name'])
                names.update(a.upper() for a in c['aliases'])
            bad = []
            for f in sorted((DOCS / 'src').glob('*.md')):
                for m in re.findall(r'`([A-Z][A-Z0-9]{1,})`', f.read_text(encoding='utf-8')):
                    if m not in names:
                        bad.append('%s: %s' % (f.name, m))
            ck(not bad, "every command a page names runs in this build (%s)" % bad[:6])
            pages = {p.name: parse(p) for p in DOCS.glob('*.html')}
            broken = []
            for n, L in pages.items():
                for h in L.hrefs:
                    if re.match(r'^(https?:|mailto:)', h):
                        continue
                    f, _, anc = h.partition('#')
                    if f.startswith('../'):
                        tgt = (DOCS / f).resolve()
                        if f.startswith('../v/'):
                            continue   # the older builds exist on the site; checked in section 4
                        if not tgt.exists() and f != '../index.html':
                            broken.append('%s -> %s' % (n, h))
                        continue
                    tp = pages.get(f or n)
                    if tp is None or (anc and anc not in tp.ids):
                        broken.append('%s -> %s' % (n, h))
            ck(not broken, "every link inside the guide reaches a page and an anchor that exist (%s)" % broken[:6])
            cmdp = pages['commands.html']
            miss = [c['anchor'] for c in cat['commands'] if c['anchor'] not in cmdp.ids]
            ck(not miss and len(set(c['anchor'] for c in cat['commands'])) == len(cat['commands']), "every command has its own entry in the reference (%s)" % miss[:5])
            ents = build_docs.changelog((ROOT / 'canvas_v10_STATUS.md').read_text(encoding='utf-8'))
            vs = [e['v'] for e in ents]
            ck(vs and vs[0] == 'V142' and 'v142' in pages['changelog.html'].ids, "the release notes open with this version, V142 (%s)" % vs[:3])
            nums = [int(re.match(r'V(\d+)', v).group(1)) for v in vs]
            ck(all(a >= b for a, b in zip(nums, nums[1:])) and len(vs) >= 55, "newest first, %d entries" % len(vs))
            want = set(range(87, 143)) - set(nums)
            ck(not want, "a note for every phase from V87 (%s missing)" % sorted(want))
            kept = build_docs.kept_versions()
            ck(len(kept) >= 55 and all(lab.lower() in ''.join(pages['versions.html'].hrefs) for lab, _ in kept) and kept[-1][0] == 'V141',
               "the versions page lists every kept build, the newest V141 (%d)" % len(kept))
            labs = [lab for lab, _ in kept]
            ck(len(labs) == len(set(labs)), "each version once")
            for lab, p in kept:
                n = re.search(r'bak_phase(\d+)', p.name).group(1)
                if int(re.match(r'V(\d+)', lab).group(1)) > int(n):
                    ck(False, "%s is not older than the phase it was kept before (%s)" % (lab, p.name))
                    break
            else:
                ck(True, "every kept build is named for a version older than the phase it was kept before")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. the site")
            tmp = pathlib.Path(tempfile.mkdtemp()) / '_site'
            pr = subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_site.py'), str(tmp)], capture_output=True, text=True, timeout=300)
            ck(pr.returncode == 0, "tools/build_site.py builds the site (%s)" % pr.stdout.strip())
            ck(filecmp.cmp(tmp / 'index.html', ROOT / 'canvas_v10.html', shallow=False) and filecmp.cmp(tmp / 'canvas_v10.html', ROOT / 'canvas_v10.html', shallow=False),
               "the site opens the newest app")
            ck(sorted(p.name for p in (tmp / 'docs').glob('*.html')) == sorted(pages) and (tmp / '.nojekyll').exists(), "with every guide page")
            okv = all(filecmp.cmp(tmp / 'v' / lab.lower() / 'index.html', p, shallow=False) for lab, p in kept)
            ck(okv and len(list((tmp / 'v').iterdir())) == len(kept), "and every older build at v/<version>/, as it was")
            wf = (ROOT / '.github' / 'workflows' / 'pages.yml').read_text()
            ck('python3 tools/build_docs.py --check' in wf and 'python3 tools/build_site.py _site' in wf, "the Pages workflow checks the guide and builds the site with them")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. the pages")
            dp = await ctx.new_page()
            derrs = []
            dp.on('pageerror', lambda e: derrs.append(str(e)))
            ext = []
            dp.on('request', lambda r: ext.append(r.url) if not r.url.startswith(('file:', 'data:')) else None)
            for n in sorted(pages):
                await within(dp.goto('file://' + str(DOCS / n)), 'goto ' + n)
            ck(not derrs and not ext and not any(L.scripts for L in pages.values()), "every page opens with no errors and asks no server for anything (%s %s)" % (derrs[:2], ext[:2]))
            await within(dp.goto('file://' + str(DOCS / 'commands.html')), 'goto commands')
            await dp.fill('#f', 'cityjson')
            await dp.wait_for_timeout(100)
            vis = await dp.evaluate("()=>[[].filter.call(document.querySelectorAll('.cmd'),function(c){return c.offsetParent!==null;}).map(function(c){return c.id;}),"
                                    "[].filter.call(document.querySelectorAll('.grpw'),function(s){return s.offsetParent!==null;}).length,document.getElementById('n').textContent]")
            ck(sorted(vis[0]) == ['cmd-CITYJSONIN', 'cmd-CITYJSONOUT'] and vis[1] == 1 and vis[2] == '2 of %d commands' % len(cat['commands']),
               "the reference's filter: 'cityjson' leaves its two commands, under one heading (%s)" % vis)
            await dp.set_viewport_size({'width': 390, 'height': 800})
            sw = []
            for n in ('index.html', 'bim.html', 'commands.html', 'changelog.html', 'versions.html'):
                await within(dp.goto('file://' + str(DOCS / n)), 'goto ' + n)
                sw.append(await dp.evaluate("()=>document.documentElement.scrollWidth<=window.innerWidth+1"))
            ck(all(sw), "at phone width no page scrolls sideways (%s)" % sw)
            ck(not errs, "no page errors in the app (%s)" % errs[:3])
        except Stalled as e:
            ck(False, "the harness stalled at: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
