"""bim_phase172f_idb_every_project_browser_tests.py -- V172f: every project in IndexedDB, the old keys retired, a second
tab read-only.

docs/research/research-local-storage.md, part 13 (D1, D7, D9, D10; the owner's F2). What this suite holds the phase to:

  1. THE FIRST START MOVES EVERYTHING, CHECKED. A store of older keys -- the project on screen, a parked project, a
     template, the Assets library -- is copied into the database, the index written, every older key removed; the
     model on screen is the stored one; one toast says what moved.
  2. THE JOURNAL WINS WHEN NEWER. A journal newer than the database's record (what pagehide writes when the database
     has not confirmed a save) is what the next start shows, is written into the database, and is removed.
  3. OLDER KEYS FOUND LATER. With the projects in the database, a project an older build left under the old keys is
     kept when it has anything in it and dropped when it is empty; both keys are removed.
  4. A NEWER DATABASE IS REFUSED, NOTHING SAVED OVER IT. A database at a later version than this build's: the app
     says a newer version updated the storage and writes nothing, the index included.
  5. A SECOND TAB IS READ-ONLY, WITH TAKE OVER. The tab with a project holds its lock; a second tab opening it shows
     it read-only, says so on its first edit and saves nothing; Take over gives it the lock and the latest saved
     model, and the first tab turns read-only.

Storage is seeded from a blank page of the same origin with the app closed (the V115 rule); the one init script only
watches the toast.
"""
import asyncio, json, pathlib, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent.parent / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v172f_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

WIPE = """()=>new Promise(function(res){localStorage.clear();var r=indexedDB.deleteDatabase('BIM-Personal');r.onsuccess=r.onerror=r.onblocked=function(){res(true);};})"""
TB = {'project': '', 'client': '', 'drawnBy': '', 'checkedBy': ''}
TOASTS = """(function(){window.__v172fToasts=[];new MutationObserver(function(){var t=document.getElementById('a3d-toast');
  if(t&&t.textContent&&window.__v172fToasts[window.__v172fToasts.length-1]!==t.textContent)window.__v172fToasts.push(t.textContent);})
  .observe(document,{subtree:true,childList:true,characterData:true});})();"""


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV172f' in t, 'the V172f marker is present')
    if not ck.bad:
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:200]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        await ctx.add_init_script(TOASTS)
        page = await ctx.new_page()
        page.set_default_timeout(8000)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))

        async def safe(js, arg=None, pg=None):
            try:
                p = pg or page
                return await asyncio.wait_for(p.evaluate(js, arg) if arg is not None else p.evaluate(js), 12)
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def open_app(pg=None):
            p = pg or page
            await p.goto('file://' + str(HTML))
            for _ in range(80):
                st = await safe("()=>window.__a3dStore?window.__a3dStore().mode:null", pg=p)
                if st in ('idb', 'legacy', 'refused'):
                    break
                await p.wait_for_timeout(100)
            await p.wait_for_timeout(900)

        async def blank(pg=None):
            await (pg or page).goto('file://' + str(BLANK))

        async def stored(key, pg=None):
            v = await safe("(k)=>window.__a3dStoredGet(k)", key, pg=pg)
            return v.get('rec') if v else None

        async def keys(pg=None):
            return await safe("()=>{var o=[],i;for(i=0;i<localStorage.length;i++)o.push(localStorage.key(i));return o.sort();}", pg=pg) or []

        async def toasts(pg=None):
            return await safe("()=>window.__v172fToasts", pg=pg) or []

        async def objs(pg=None):
            return await safe("()=>window.__a3dObjects().map(function(o){return o.id;})", pg=pg) or []

        # ------------------------------------------------------------------------------------------
        print('\n-- 1. the first start moves everything, checked')
        await blank()
        await safe(WIPE)
        rec = {'docId': 'doc-on-screen', 'objs': [{'id': 'w-legacy-1', 't': 'wall', 'prm': {}, 'pos': [0, 0, 0]}],
               'titleBlock': dict(TB, project='Old Tower')}
        parked = {'objs': [{'id': 'w-parked-1', 't': 'wall', 'prm': {}, 'pos': [0, 0, 0]}], 'titleBlock': dict(TB, project='Parked Pier')}
        lst = {'v': 1, 'active': 'doc-on-screen', 'open': ['doc-on-screen'],
               'docs': [{'id': 'doc-on-screen', 'name': 'Old Tower', 'objs': 1, 'saved': 1}, {'id': 'doc-parked', 'name': 'Parked Pier', 'objs': 1, 'saved': 1}]}
        lib = [{'id': 'fam-old-1', 'kind': 'model', 'name': 'Old bench', 'category': 'Site', 'mesh': {'v': [], 'f': []}},
               {'id': 'tpl-old-1', 'kind': 'template', 'name': 'Old template', 'category': 'Templates', 'count': 0}]
        await safe("""(a)=>{localStorage.setItem('acad3dV1',a.rec);localStorage.setItem('acad3dDocV1:doc-parked',a.parked);
            localStorage.setItem('acad3dDocsV1',a.lst);localStorage.setItem('acad3dFamilyLibrary',a.lib);
            localStorage.setItem('acad3dTemplateV1:tpl-old-1','{"objs":[]}');localStorage.setItem('acad3dTheme','light');}""",
                   {'rec': json.dumps(rec), 'parked': json.dumps(parked), 'lst': json.dumps(lst), 'lib': json.dumps(lib)})
        await open_app()
        st = await safe("()=>window.__a3dStore()") or {}
        ck(st.get('mode') == 'idb' and st.get('v2') is True, 'the store is in the database (%s)' % st)
        r1, r2 = await stored('doc-on-screen'), await stored('doc-parked')
        ck(r1 and 'w-legacy-1' in r1 and r2 and 'w-parked-1' in r2, 'the project on screen and the parked one are in the database under their ids')
        ck(await stored('tpl:tpl-old-1') == '{"objs":[]}' and 'fam-old-1' in (await stored('lib:family') or ''),
           'the template and the library are too')
        ks = await keys()
        ck(ks == ['acad3dProjectsV2', 'acad3dTheme'], 'every older key is removed; the index and the preferences stay (%s)' % ks)
        ck('w-legacy-1' in await objs(), 'the model on screen is the stored one')
        tt = [x for x in await toasts() if 'now kept in the browser' in x]
        ck(len(tt) == 1 and '2 projects' in tt[0] and '1 template' in tt[0] and 'Assets library' in tt[0], 'one toast says what moved (%s)' % tt)
        names = [d['name'] for d in (await safe("()=>window.__a3dDocs.list()") or [])]
        ck(sorted(names) == ['Old Tower', 'Parked Pier'], 'the list names both (%s)' % names)
        await safe("(id)=>window.__a3dDocs.activate(id)", 'doc-parked')
        await page.wait_for_timeout(800)
        ck('w-parked-1' in await objs(), 'the parked project opens from the database')

        # ------------------------------------------------------------------------------------------
        print('\n-- 2. the journal wins when newer')
        cur = await safe("()=>window.__a3dDocs.active()")
        base = await stored(cur)
        await blank()
        jr = json.loads(base)
        jr['objs'].append({'id': 'w-journal-1', 't': 'wall', 'prm': {}, 'pos': [0, 0, 0]})
        await safe("(a)=>localStorage.setItem('acad3dJournalV2:'+a.id,JSON.stringify({id:a.id,saved:Date.now()+60000,rec:a.rec}))",
                   {'id': cur, 'rec': json.dumps(jr)})
        await open_app()
        await page.wait_for_timeout(600)
        ck('w-journal-1' in await objs(), 'the next start shows the journal\'s model')
        ck('w-journal-1' in (await stored(cur) or ''), 'it is written into the database')
        ck('acad3dJournalV2:' + cur not in await keys(), 'and the journal is removed')
        older = json.loads(base)
        await blank()
        await safe("(a)=>localStorage.setItem('acad3dJournalV2:'+a.id,JSON.stringify({id:a.id,saved:1,rec:a.rec}))",
                   {'id': cur, 'rec': json.dumps(older)})
        await open_app()
        ck('w-journal-1' in await objs() and 'acad3dJournalV2:' + cur not in await keys(),
           'a journal older than the record loses and is removed')

        # ------------------------------------------------------------------------------------------
        print('\n-- 3. older keys found later')
        await blank()
        await safe("""()=>{localStorage.setItem('acad3dV1',JSON.stringify({objs:[],titleBlock:{project:'',client:'',drawnBy:'',checkedBy:''}}));
            localStorage.setItem('acad3dDocV1:doc-later',JSON.stringify({objs:[{id:'w-later-1',t:'wall',prm:{},pos:[0,0,0]}],
              titleBlock:{project:'Later Hall',client:'',drawnBy:'',checkedBy:''}}));}""")
        await open_app()
        await page.wait_for_timeout(500)
        names = [d['name'] for d in (await safe("()=>window.__a3dDocs.list()") or [])]
        ks = await keys()
        ck('Later Hall' in names and 'w-later-1' in (await stored('doc-later') or ''), 'a project with something in it is kept (%s)' % names)
        ck('Untitled project' not in names, 'the empty one is dropped (%s)' % names)
        ck('acad3dV1' not in ks and 'acad3dDocV1:doc-later' not in ks, 'and both keys are removed (%s)' % ks)

        # ------------------------------------------------------------------------------------------
        print('\n-- 4. a newer database is refused, nothing saved over it')
        ix_before = await safe("()=>localStorage.getItem('acad3dProjectsV2')")
        await blank()
        await safe("""()=>new Promise(function(res){var r=indexedDB.open('BIM-Personal',3);r.onupgradeneeded=function(){};
            r.onsuccess=function(){r.result.close();res(true);};r.onerror=function(){res(false);};})""")
        await open_app()
        st = await safe("()=>window.__a3dStore()") or {}
        tt = [x for x in await toasts() if 'newer version' in x]
        ck(st.get('mode') == 'refused' and st.get('newer') is True and tt, 'the app says a newer version updated the storage (%s, %s)' % (st, tt[:1]))
        await safe("()=>window.__a3dWall([[0,9],[3,9]],0.2,3,'center',false)")
        await page.wait_for_timeout(700)
        ck(await safe("()=>localStorage.getItem('acad3dProjectsV2')") == ix_before, 'an edit then writes nothing, the index included')
        await blank()
        await safe(WIPE)

        # ------------------------------------------------------------------------------------------
        print('\n-- 5. a second tab is read-only, with Take over')
        await open_app()
        w0 = await safe("()=>window.__a3dWall([[0,0],[4,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(700)
        pid = await safe("()=>window.__a3dDocs.active()")
        t1 = await safe("()=>window.__a3dTab()") or {}
        ck(t1.get('held') is True and t1.get('readOnly') is False and t1.get('id') == pid, 'the first tab holds its project\'s lock (%s)' % t1)
        p2 = await ctx.new_page()
        p2.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await open_app(p2)
        t2 = await safe("()=>window.__a3dTab()", pg=p2) or {}
        bar = await safe("()=>{var b=document.getElementById('a3d-ro-bar');if(!b)return null;var r=b.getBoundingClientRect();"
                         "var e=document.elementFromPoint(r.x+r.width-30,r.y+r.height/2);return {text:b.textContent,top:!!(e&&b.contains(e))};}", pg=p2)
        ck(await safe("()=>window.__a3dDocs.active()", pg=p2) == pid and t2.get('readOnly') is True,
           'a second tab opening it shows it read-only (%s)' % t2)
        ck(bar and 'read-only' in bar['text'] and bar['top'], 'the bar says so and its button is what the pointer reaches (%s)' % bar)
        before = await stored(pid)
        await safe("()=>window.__a3dWall([[0,5],[4,5]],0.3,3,'center',false)", pg=p2)
        await p2.wait_for_timeout(800)
        tt = [x for x in await toasts(p2) if 'Not saved' in x]
        ck(tt and await stored(pid) == before, 'its first edit says it is not saved, and nothing is written (%s)' % tt[:1])
        w1 = await safe("()=>window.__a3dWall([[0,9],[4,9]],0.3,3,'center',false)")
        await page.wait_for_timeout(700)
        await p2.click('#a3d-ro-bar [data-a3dro="take"]')
        for _ in range(40):
            if not (await safe("()=>window.__a3dTab().readOnly", pg=p2)):
                break
            await p2.wait_for_timeout(100)
        await p2.wait_for_timeout(500)
        ids2 = await objs(p2)
        ck((await safe("()=>window.__a3dTab()", pg=p2) or {}).get('held') is True and w0 in ids2 and w1 in ids2,
           'Take over gives the second tab the lock and the latest saved model, the first tab\'s last edit included')
        t1b = await safe("()=>window.__a3dTab()") or {}
        ck(t1b.get('readOnly') is True and t1b.get('held') is False, 'and the first tab turns read-only (%s)' % t1b)
        w2 = await safe("()=>window.__a3dWall([[0,12],[4,12]],0.3,3,'center',false)", pg=p2)
        await p2.wait_for_timeout(800)
        ck(w2 and w2 in (await stored(pid) or ''), 'the second tab\'s edits are saved now')
        await p2.close()
        await page.wait_for_timeout(300)
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
