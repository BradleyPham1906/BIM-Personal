#!/usr/bin/env python3
"""bim_phase146_history_browser_tests.py -- V146: history by element (the Hub's H1).

  1. THE STORE: canonical JSON does not depend on key order; the 128-bit hash is recomputed here in
     Python, bit for bit (the app multiplies 32-bit integers without Math.imul).
  2. COMMIT: the first version holds every element; nothing to commit is refused; after a move, a
     delete, a new object, a renamed site and a new level, the changes are exactly those five, each
     said field by field; only the changed elements are stored again.
  3. RESTORE: the model comes back as it was, the history untouched; undo takes it back again.
  4. AN ELEMENT'S OWN HISTORY, the History group (Enter commits, Changes, Restore, Discard), the
     commands, and the reload.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 90
M = 0xffffffff


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


def py_hash(s):
    out = ''
    for seed in (0, 0x9e3779b9):
        h1, h2 = (0xdeadbeef ^ seed) & M, (0x41c6ce57 ^ seed) & M
        for ch in s:
            c = ord(ch)
            h1 = ((h1 ^ c) * 2654435761) & M
            h2 = ((h2 ^ c) * 1597334677) & M
        h1 = (((h1 ^ (h1 >> 16)) * 2246822507) & M) ^ (((h2 ^ (h2 >> 13)) * 3266489909) & M)
        h2 = (((h2 ^ (h2 >> 16)) * 2246822507) & M) ^ (((h1 ^ (h1 >> 13)) * 3266489909) & M)
        out += '%08x%08x' % (h2, h1)
    return out


def py_canon(v):
    if isinstance(v, dict):
        return '{' + ','.join(json.dumps(k) + ':' + py_canon(v[k]) for k in sorted(v)) + '}'
    if isinstance(v, list):
        return '[' + ','.join(py_canon(x) for x in v) + ']'
    return json.dumps(v)


PARTS = 10


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
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

        has = await safe("()=>window.__acad3dV146")
        ck(bool(has) and 'blobstore' in has and 'restore' in has, "__acad3dV146 marker is present (%s)" % has)
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1
        mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
        ck(mv and int(mv.group(1)) >= 146, "the app says V146 or later (%s)" % (mv and mv.group(1)))

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def hist():
            return await safe("()=>window.__a3dHistory()") or {}

        async def changes():
            return await safe("()=>window.__a3dHistChanges()") or []

        async def objs():
            return await safe("()=>window.__a3dState().objs") or []

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the store")
            c1 = await safe("()=>window.__a3dCanon({b:1,a:[1,{d:2,c:3}],z:null,u:undefined})")
            c2 = await safe("()=>window.__a3dCanon({z:null,a:[1,{c:3,d:2}],b:1})")
            ck(c1 == c2 == '{"a":[1,{"c":3,"d":2}],"b":1,"z":null}', "canonical JSON: the same content in any key order, undefined left out (%s)" % c1)
            samples = ['', 'a', 'wall', 'Wall 12 height 3.2', py_canon({'id': 'a3d-1', 'pos': [1, 0, 2], 'name': 'Sketch 1'}), 'x' * 5000]
            hs = await safe("(a)=>a.map(function(s){return window.__a3dHash(s);})", samples) or []
            ck(hs == [py_hash(s) for s in samples], "the 128-bit hash agrees with Python, bit for bit, on %d strings" % len(samples))
            ck(len(set(hs)) == len(hs) and all(len(h) == 32 for h in hs), "distinct strings, distinct 32-hex-digit hashes")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. commit")
            n0 = len(await objs())
            A = await safe("()=>window.__a3dSketch('poly',[[0,0],[4,0],[4,3]])")
            B = await safe("()=>window.__a3dSketch('poly',[[10,0],[14,0],[14,3]])")
            C = await safe("()=>window.__a3dSketch('poly',[[20,0],[24,0],[24,3]])")
            ch = await changes()
            ck(len(ch) == n0 + 3 + PARTS and all(x['kind'] == 'added' for x in ch), "before any version, every element is new: %d objects and %d project parts" % (n0 + 3, PARTS))
            r = await safe("()=>window.__a3dHistCommit('First layout')") or {}
            H = await hist()
            ck(r.get('msg') == 'First layout' and r['stats'] == {'added': n0 + 3 + PARTS, 'changed': 0, 'removed': 0} and len(H['commits']) == 1 and H['head'] == r['id'],
               "COMMIT: the first version holds them all (%s)" % r.get('stats'))
            b1 = H['size']['blobs']
            tree = H['commits'][0]['tree']
            ck(len(tree) == n0 + 3 + PARTS + 1 and b1 == len({h for k, h in tree}) < len(tree),
               "each content stored once: %d elements, %d stored (empty parts share one)" % (len(tree), b1))
            ck(await changes() == [], "after it, nothing has changed")
            r = await safe("()=>window.__a3dHistCommit('again')") or {}
            ck('Nothing has changed since "First layout"' in r.get('error', ''), "a version with no change is refused (%s)" % r.get('error'))
            await safe("(a)=>window.__a3dSetPos(a,1,0,2)", A)
            await safe("(b)=>window.__a3dDel(b)", B)
            D = await safe("()=>window.__a3dSketch('poly',[[30,0],[34,0],[34,3]])")
            await safe("()=>window.__a3dSetSite('North Lot')")
            await safe("()=>window.__a3dAddLevel()")
            ch = {x['key']: x for x in await changes()}
            ck(set(ch) == {'o:' + A, 'o:' + B, 'o:' + D, '@site', '@levels'}, "five changes, exactly: the moved, the deleted, the new, the site and the levels (%s)" % sorted(ch))
            ck(ch['o:' + A]['kind'] == 'changed' and any(p['text'] == 'moved by 1, 0, 2' for p in ch['o:' + A]['props']), "the moved one says 'moved by 1, 0, 2'")
            ck(ch['o:' + B]['kind'] == 'removed' and ch['o:' + D]['kind'] == 'added', "the deleted one removed, the new one added")
            ck(any(p['text'] == 'name: "Site" → "North Lot"' for p in ch['@site']['props']), "the site, field by field: name: \"Site\" → \"North Lot\"")
            ck(ch['@levels']['label'] == 'Levels' and any(p['text'].endswith(' added') for p in ch['@levels']['props']), "the levels, by id: a level added (%s)" % [p['text'] for p in ch['@levels']['props']])
            r2 = await safe("()=>window.__a3dHistCommit('Moved, removed, added')") or {}
            ck(r2.get('stats') == {'added': 1, 'changed': 3, 'removed': 1}, "the second version: 1 added, 3 changed, 1 removed (%s)" % r2.get('stats'))
            H = await hist()
            ck(H['size']['blobs'] == b1 + 4 + 1, "only what changed is stored again: 4 elements and the bookkeeping (%d to %d)" % (b1, H['size']['blobs']))
            cd = await safe("(i)=>window.__a3dHistCommitDiff(i)", r2['id']) or []
            ck(sorted((x['key'], x['kind']) for x in cd) == sorted((k, v['kind']) for k, v in ch.items()), "the version's own changes are the same five")
            ck(H['commits'][1]['parent'] == H['commits'][0]['id'], "each version names the one before it")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. restore")
            first = H['commits'][0]['id']
            nlev = len((await safe("()=>window.__a3dState()"))['objs'])
            r = await safe("(i)=>window.__a3dHistRestore(i)", first) or {}
            O = {o['id']: o for o in await objs()}
            site = await safe("()=>window.__a3dSite()")
            ck(A in O and B in O and C in O and D not in O and O[A].get('pos') in (None, [0, 0, 0]) and site['name'] == 'Site',
               "Restore 'First layout': the deleted one back, the new one gone, the moved one where it was, the site's name")
            ck(len((await hist())['commits']) == 2, "the history is not rewritten")
            ch = {x['key']: x['kind'] for x in await changes()}
            ck(ch == {'o:' + A: 'changed', 'o:' + B: 'added', 'o:' + D: 'removed', '@site': 'changed', '@levels': 'changed'}, "against the latest, the restore shows as the five changes undone")
            await safe("()=>window.__a3dUndo()")
            O = {o['id']: o for o in await objs()}
            ck(D in O and B not in O and await changes() == [], "undo takes the restore back: the latest version again")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. an element's history, the History group, the commands, the reload")
            L = await safe("(a)=>window.__a3dHistOf(a)", A) or []
            ck([x['kind'] for x in L] == ['changed', 'added'] and L[0]['msg'] == 'Moved, removed, added' and any(p['text'] == 'moved by 1, 0, 2' for p in L[0]['props']),
               "an element's own history: added in the first version, moved in the second")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps();}", A)
            await page.wait_for_timeout(80)
            hb = await safe("()=>document.getElementById('a3d-propsbody').innerHTML") or ''
            ck('data-histobj' in hb and 'Moved, removed, added' in hb, "its Properties have a History group")
            await safe("()=>window.__a3dRunCmd('history')")
            await page.wait_for_timeout(120)
            st = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-histstate]');return e?[e.getAttribute('data-histstate'),e.textContent]:null;}")
            dis = await safe("()=>{var b=document.querySelector('#a3d-propsbody [data-histact=\"commit\"]');return b?b.disabled:null;}")
            ck(st and st[0] == 'clean' and 'No changes since "Moved, removed, added"' in st[1] and dis is True, "HISTORY: the History group, clean, Commit disabled (%s)" % st)
            await safe("(c)=>window.__a3dSetPos(c,0,0,5)", C)
            await safe("()=>window.__a3dRunCmd('commit')")
            await page.wait_for_timeout(150)
            foc = await safe("()=>{var a=document.activeElement;return !!(a&&a.hasAttribute&&a.hasAttribute('data-histmsg'));}")
            ck(foc, "COMMIT with a change waiting puts the cursor in the message")
            await page.keyboard.type('Third: C raised')
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(150)
            H = await hist()
            ck(len(H['commits']) == 3 and H['commits'][-1]['msg'] == 'Third: C raised' and 'Committed "Third: C raised"' in await toast(), "Enter commits it, with its message")
            top = await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-histc]');return e?[e.getAttribute('data-histc'),e.textContent]:null;}")
            ck(top and top[0] == H['head'] and 'latest' in top[1], "newest first, marked latest")
            await page.click('#a3d-propsbody [data-histact="show:%s"]' % H['head'])
            await page.wait_for_timeout(100)
            rows = await safe("()=>[].map.call(document.querySelectorAll('#a3d-propsbody [data-histc] [data-histkey]'),function(e){return e.getAttribute('data-histkey')+'|'+e.textContent;})") or []
            ck(len(rows) == 1 and rows[0].startswith('o:' + C) and 'moved by 0, 0, 5' in rows[0], "Changes opens it: C moved by 0, 0, 5 (%s)" % rows)
            await safe("(c)=>window.__a3dSetPos(c,9,9,9)", C)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(80)
            await page.click('#a3d-propsbody [data-histact="discard"]')
            await page.wait_for_timeout(120)
            O = {o['id']: o for o in await objs()}
            ck(O[C]['pos'] == [0, 0, 5] and await changes() == [], "Discard Changes: back to the latest version")
            await page.click('#a3d-propsbody [data-histact="restore:%s"]' % first)
            await page.wait_for_timeout(120)
            ck(D not in {o['id'] for o in await objs()} and 'Restored "First layout"' in await toast(), "Restore on a version, from the group")
            await safe("()=>window.__a3dUndo()")
            # a field deep inside an element, and the Commit button with a typed message
            await safe("()=>{var o={id:'t-nest',t:'sketch',name:'Nested',pts:[[50,0],[52,0],[52,2]],closed:true,pos:[0,0,0],y:0,layer:'layer-0',meta:{kind:'x',size:{w:1,h:2}}};window.__TN=o;window.__a3dPushTestObj(o);}")
            await safe("()=>window.__a3dHistCommit('Nested added')")
            await safe("()=>{window.__TN.meta.size.w=3;}")
            ch = {x['key']: x for x in await changes()}
            ck(list(ch) == ['o:t-nest'] and [p['text'] for p in ch['o:t-nest']['props']] == ['meta.size.w: 1 → 3'],
               "a field deep inside an element is named by its path: meta.size.w: 1 → 3 (%s)" % [p['text'] for x in ch.values() for p in x.get('props', [])])
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(80)
            await page.fill('#a3d-propsbody [data-histmsg]', 'Widened the nested one')
            await page.click('#a3d-propsbody [data-histact="commit"]')
            await page.wait_for_timeout(120)
            ck((await hist())['commits'][-1]['msg'] == 'Widened the nested one', "the Commit button takes the typed message")
            H = await hist()
            await safe("()=>window.__a3dRunCmd('commit')")
            ck('Nothing has changed since "Widened the nested one"' in await toast(), "COMMIT with nothing changed says so")
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return c.name==='COMMIT'||c.name==='HISTORY';}).map(function(c){return c.name;})") or []
            ck(sorted(cat) == ['COMMIT', 'HISTORY'], "COMMIT and HISTORY are in the catalogue")
            for q_, n_ in (('checkpoint', 'COMMIT'), ('version history', 'HISTORY'), ('revisions', 'HISTORY')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,5)", q_) or [])]
                ck(n_ in nm[:3], "searching %r finds %s (%s)" % (q_, n_, nm))
            ids = [c['id'] for c in H['commits']]
            await page.wait_for_timeout(700)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            H2 = await hist()
            ck([c['id'] for c in H2['commits']] == ids and H2['head'] == ids[-1] and await changes() == [], "after a reload the history is all there, and nothing is uncommitted")
            r = await safe("(i)=>window.__a3dHistRestore(i)", first) or {}
            ck(r.get('msg') == 'First layout' and B in {o['id'] for o in await objs()}, "and a version restores from it")
            ck(not errs, "no page errors (%s)" % errs[:3])
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
