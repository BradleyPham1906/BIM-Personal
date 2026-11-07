"""bim_phase172d_idb_projects_browser_tests.py -- V172d: a project too large for localStorage, kept in IndexedDB.

docs/research/research-local-storage.md, the owner's decision D1 (2026-10-31), storage phase A1. localStorage holds about
5.2 million characters for the whole origin (measured), so a large model could not be saved and a project over half of
it could not be switched away from. What this suite holds the phase to:

  1. WHAT FITS STAYS WHERE IT WAS. A small project is saved whole in acad3dV1, and the database holds no copy of it.
  2. WHAT DOES NOT FIT GOES TO THE DATABASE. When localStorage refuses the record, it is written to IndexedDB
     ('BIM-Personal', store 'projects', under the project's id), and acad3dV1 holds a pointer -- the id, the name,
     the count -- once the record has committed. One toast says where it is; none says it could not be saved.
     Later saves update the database's record; the pointer stays.
  3. A RELOAD BRINGS IT BACK from the database, the pointer naming it until it arrives.
  4. SWITCHING. A project too large for its own key is parked in the database with its pointer in the key, and the
     list still names and counts it; opening it again reads it back, and the model is the one parked.
  5. DELETING a parked project deletes its database copy.
  6. NOTHING IS SAVED OVER A RECORD THAT COULD NOT BE READ. When the pointer's record is missing, the app says so,
     and edits made then never replace the pointer with the fresh project the page started with.

"Too large" is made by replacing Storage.prototype.setItem from the page after start (the V115 way), refusing any
acad3d record longer than a limit, the project list excepted; no init script touches storage (the V115 rule). The one
init script here only watches the toast.
"""
import asyncio, json, pathlib, re, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parents[2] / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v172d_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

LSK = 'acad3dV1'
PREFIX = 'acad3dDocV1:'
LIMIT = 36000          # an empty project is about 28,000 characters; twenty walls take it over
SPILLED = 'too large for quick browser storage'
NOSAVE = 'could not be saved'
UNREAD = 'could not be read'

IDB_GET = """(id)=>new Promise(function(res){
  var r;try{r=indexedDB.open('BIM-Personal');}catch(e){res({err:String(e)});return;}
  r.onupgradeneeded=function(){r.result.createObjectStore('projects');};
  r.onsuccess=function(){var db=r.result;try{var t=db.transaction('projects','readonly'),g=t.objectStore('projects').get(id);
    g.onsuccess=function(){db.close();res({rec:g.result?g.result.rec:null});};g.onerror=function(){db.close();res({err:'get'});};}
    catch(e){db.close();res({err:String(e)});}};
  r.onerror=function(){res({err:'open'});};})"""
IDB_DEL = """(id)=>new Promise(function(res){
  var r=indexedDB.open('BIM-Personal');
  r.onupgradeneeded=function(){r.result.createObjectStore('projects');};
  r.onsuccess=function(){var db=r.result,t=db.transaction('projects','readwrite');t.objectStore('projects')['delete'](id);
    t.oncomplete=function(){db.close();res(true);};t.onabort=function(){db.close();res(false);};};
  r.onerror=function(){res(false);};})"""
IDB_WIPE = """()=>new Promise(function(res){var r=indexedDB.deleteDatabase('BIM-Personal');r.onsuccess=r.onerror=r.onblocked=function(){res(true);};})"""
REFUSE = """(lim)=>{window.__v172dSet=window.__v172dSet||Storage.prototype.setItem;
  Storage.prototype.setItem=function(k,v){if(String(k).indexOf('acad3d')===0&&k!=='acad3dDocsV1'&&String(v).length>lim){
    var e=new Error('full');e.name='QuotaExceededError';throw e;}return window.__v172dSet.call(this,k,v);};}"""


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


def static_checks(ck, t):
    code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    print('\n-- 0. the file')
    ck("var A3D_IDB_NAME='BIM-Personal'" in code, "one database, named for the app ('BIM-Personal')")
    ck(re.search(r"db\.onversionchange=function\(\)\{\s*db\.close\(\);", code) is not None,
       "a connection another tab's upgrade asks for is closed")
    m = re.search(r"function bimSpillSave\(id,s,rec\)\{(.*?)\n  \}\n", code, flags=re.S)
    body = m.group(1) if m else ''
    put = body.find('bimIdbPut(')
    # AMENDED FOR V172f: the pointer in acad3dV1 is gone; the index is touched once the record has committed
    idx = body.find('bimIndexTouch(')
    ck(put >= 0 and idx > put and 'if(err){' in body[put:idx],
       'the index is updated in the callback, after the record has committed, and not on an error')
    m2 = re.search(r"function save3d\(\)\{(.*?)\n  \}\n", code, flags=re.S)
    ck(m2 is not None and 'if((A3D_SPILL&&A3D_SPILL.loading)' in m2.group(1) and 'A3D_SPILL.dirty=true;return;' in m2.group(1),
       'save3d writes nothing while the record on screen is still being read, and saves it after')
    ck("document.addEventListener('visibilitychange'" in code and 'if(document.hidden&&saveT)' in code,
       'a waiting autosave is written when the page is hidden (D9)')


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV172d' in t, 'the V172d marker is present')
    if not ck.bad:
        try:
            static_checks(ck, t)
        except Exception as e:
            ck(False, 'the static checks ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e)[:160]))
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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(8000)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await page.add_init_script("""(function(){window.__v172dToasts=[];
            new MutationObserver(function(){var t=document.getElementById('a3d-toast');
              if(t&&t.textContent&&window.__v172dToasts[window.__v172dToasts.length-1]!==t.textContent)window.__v172dToasts.push(t.textContent);})
            .observe(document,{subtree:true,childList:true,characterData:true});})();""")
        ev = page.evaluate

        async def safe(js, arg=None):
            # bounded: page.evaluate waits on a promise without a limit, and a database request that never
            # answers would hang the suite (falsification, park_fails)
            try:
                return await asyncio.wait_for(ev(js, arg) if arg is not None else ev(js), 12)
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def open_app(wait_loaded=True):
            await page.goto('file://' + str(HTML))
            for _ in range(80):
                ok = await safe("()=>!!(window.__a3dOn&&window.__a3dDocs&&window.__a3dSpill)")
                if ok and (not wait_loaded or not (await safe("()=>window.__a3dSpill().loading"))):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(500)

        async def toasts_with(s):
            return [x for x in (await safe("()=>window.__v172dToasts") or []) if s in x]

        async def clear_toasts():
            await safe("()=>{window.__v172dToasts=[];var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")

        async def ls(key):
            return await safe("(k)=>localStorage.getItem(k)", key)

        async def ls_json(key):
            raw = await ls(key)
            try:
                return json.loads(raw) if raw else None
            except Exception:
                return None

        async def walls(n, x0=0):
            return await safe("""(a)=>{var ids=[],i;for(i=0;i<a.n;i++)ids.push(window.__a3dWall([[a.x0+i*5,0],[a.x0+i*5+4,0]],0.3,3,'center',false));return ids;}""",
                              {'n': n, 'x0': x0}) or []

        async def obj_ids():
            return await safe("()=>window.__a3dObjects().map(function(o){return o.id;})") or []

        async def active():
            return await safe("()=>window.__a3dDocs.active()")

        async def idb_rec(id_):
            r = await safe(IDB_GET, id_) or {}
            return r.get('rec')

        # ------------------------------------------------------------------------------------------
        # AMENDED FOR V172f: every project is kept in the database, small or large; the checks that a small one stayed
        # in acad3dV1 and a large one left a pointer there assert what V172f lifted, and became the checks below
        print('\n-- 1. a small project is kept in the database')
        await page.goto('file://' + str(BLANK))
        await safe("()=>localStorage.clear()")
        await safe(IDB_WIPE)
        await open_app()
        a_id = await active()
        w1 = await walls(2)
        await page.wait_for_timeout(900)
        r0 = await idb_rec(a_id)
        ck(r0 and w1 and w1[0] in r0, 'a small project is saved whole in the database, under its id')
        ck(await ls(LSK) is None, 'and acad3dV1 holds nothing')
        ix = await ls_json('acad3dProjectsV2') or {}
        ck(ix.get('active') == a_id and any(d.get('id') == a_id for d in ix.get('docs', [])), 'the index lists it, on screen (%s)' % str(ix)[:100])

        print('\n-- 2. a large project is kept the same way')
        await safe(REFUSE, LIMIT)
        await clear_toasts()
        w2 = await walls(20, 20)
        await page.wait_for_timeout(1500)
        ix = await ls_json('acad3dProjectsV2') or {}
        ent = [d for d in ix.get('docs', []) if d.get('id') == a_id]
        ck(ent and ent[0].get('objs', 0) >= 22, 'the index counts its objects (%s)' % (ent[0].get('objs') if ent else None))
        r = await idb_rec(a_id)
        ck(r and len(r) > LIMIT and all(w in r for w in w1 + w2), 'the database holds the whole record under the project\'s id (%s chars)' % (len(r) if r else None))
        ck(not await toasts_with(SPILLED), 'no toast about where it is kept: every project is kept there')
        ck(not await toasts_with(NOSAVE), 'and none says it could not be saved')
        ck((await safe("()=>window.__a3dSpill().on")) is True, 'the project is marked as kept in the database')
        await clear_toasts()
        w3 = await walls(1, 200)
        await page.wait_for_timeout(1200)
        r = await idb_rec(a_id)
        ptr2 = await ls_json(LSK)
        ck(r and w3 and w3[0] in r, 'a later edit updates the database\'s record')
        ck(ptr2 is None, 'and acad3dV1 stays empty')
        ck(not await toasts_with(SPILLED), 'without a second toast')

        print('\n-- 3. a reload brings it back from the database')
        await open_app()
        ids = await obj_ids()
        ck(all(w in ids for w in w1 + w2 + w3), 'the 23 walls are back after a reload (%d objects)' % len(ids))
        sp = await safe("()=>window.__a3dSpill()") or {}
        ck(sp.get('on') is True and sp.get('loading') is False, 'kept in the database, and read (%s)' % sp)
        ck(await active() == a_id, 'the same project is on screen')

        print('\n-- 4. switching: parked in the database, and opened again from it')
        await safe(REFUSE, LIMIT)
        b_id = await safe("()=>window.__a3dDocs.create()")
        await page.wait_for_timeout(1200)
        parked = await ls_json(PREFIX + a_id)
        ck(b_id and await active() == b_id, 'a new project opens (%s)' % b_id)
        ck(parked is None, 'no parked key is written for the project left')
        r = await idb_rec(a_id)
        ck(r and all(w in r for w in w1 + w2 + w3), 'its record is in the database')
        ck(await idb_rec(b_id) is not None, 'and so is the new project\'s')
        ck(await ls(LSK) is None, 'acad3dV1 stays empty')
        lst = await safe("()=>window.__a3dDocs.list()") or []
        ent = [d for d in lst if d['id'] == a_id]
        ck(ent and ent[0]['objs'] >= 23, 'the list counts the parked project (%s)' % (ent[0]['objs'] if ent else None))
        bw = await walls(1, 400)
        await page.wait_for_timeout(600)
        # the index lost: the database's keys list the projects again, named and counted from their records
        await page.goto('file://' + str(BLANK))
        await safe("()=>localStorage.removeItem('acad3dProjectsV2')")
        await open_app()
        await page.wait_for_timeout(800)
        lst = await safe("()=>window.__a3dDocs.list()") or []
        ent = [d for d in lst if d['id'] == a_id]
        ck(ent and ent[0]['objs'] >= 23, 'a list rebuilt from the database\'s keys counts it from its record (%s)' % (ent[0]['objs'] if ent else None))
        ck(any(d['id'] == b_id for d in lst), 'and lists the other project too')
        await safe(REFUSE, LIMIT)
        await clear_toasts()
        ok = await safe("(id)=>window.__a3dDocs.activate(id)", a_id)
        for _ in range(40):
            if await active() == a_id and len(await obj_ids()) >= 23:
                break
            await page.wait_for_timeout(100)
        await page.wait_for_timeout(1200)
        ids = await obj_ids()
        ck(ok and await active() == a_id and all(w in ids for w in w1 + w2 + w3), 'opening it again reads the parked model back (%d objects)' % len(ids))
        ck(bw and bw[0] not in ids, 'and none of the other project\'s')
        ck(await ls(PREFIX + a_id) is None and await ls(LSK) is None, 'no older key is written for either')
        await safe("(id)=>window.__a3dDocs.activate(id)", b_id)
        await page.wait_for_timeout(1200)
        await safe("(id)=>window.__a3dDocs.activate(id)", a_id)
        for _ in range(40):
            if await active() == a_id and len(await obj_ids()) >= 23:
                break
            await page.wait_for_timeout(100)
        await page.wait_for_timeout(800)
        ck(await active() == a_id and len(await obj_ids()) >= 23, 'opened a second time, it is read back again')

        print('\n-- 5. deleting a parked project deletes its database copy')
        await safe("(id)=>window.__a3dDocs.activate(id)", b_id)
        await page.wait_for_timeout(1200)
        await safe("(id)=>window.__a3dDocs.close(id)", a_id)
        gone = await safe("(id)=>window.__a3dDocs.remove(id)", a_id)
        await page.wait_for_timeout(800)
        ck(gone is True and await idb_rec(a_id) is None, 'the database no longer holds the deleted project')
        ck(await ls(PREFIX + a_id) is None, 'nor does its key')

        print('\n-- 6. nothing is saved over a record that could not be read')
        await safe(REFUSE, LIMIT)
        await walls(22, 600)
        await page.wait_for_timeout(1500)
        ck(await idb_rec(b_id) is not None and await active() == b_id, 'the second project is on screen, kept in the database')
        await page.goto('file://' + str(BLANK))
        await safe(IDB_DEL, b_id)
        await clear_toasts()
        await open_app(wait_loaded=False)
        await page.wait_for_timeout(800)
        ck(len(await toasts_with(UNREAD)) == 1, 'the app says the record could not be read (%s)' % (await safe("()=>window.__v172dToasts")))
        await walls(1, 900)
        await page.wait_for_timeout(1200)
        ix5 = await ls_json('acad3dProjectsV2') or {}
        ck(ix5.get('active') == b_id and await idb_rec(b_id) is None,
           'an edit made then writes nothing over it: the index still names it, and no empty record replaces it (%s)' % str(ix5)[:80])
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
