"""bim_phase172e_idb_library_templates_browser_tests.py -- V172e: the Assets library and templates in IndexedDB; the
browser asked to keep the app's storage at the first Save.

reference/research-local-storage.md, the owner's decisions D1 (phase A) and D3 (2026-10-31). What this suite holds
the phase to:

  1. WHAT FITS STAYS WHERE IT WAS. A small library is saved whole in acad3dFamilyLibrary; the database has no copy.
  2. A LIBRARY LOCALSTORAGE REFUSES goes to the database ('BIM-Personal', 'projects', key 'lib:family'), its pointer
     in its key once the copy has committed; no toast says it could not be saved. A reload reads it back.
  3. A TEMPLATE LOCALSTORAGE REFUSES is kept in the database under 'tpl:<id>', its library entry marked; using it
     reads it back into a new project with the template's model; removing it removes its copy.
  4. A TEMPLATE BOTH REFUSE is said so, and its entry is not left in the library.
  5. D3: the browser is asked to keep the app's storage at the first Save, not on load, and only once.

Storage is made to refuse by replacing Storage.prototype.setItem (and, in 4, IndexedDB's open and transaction) from
the page after start (the V115 way); no init script touches storage. The one init script watches the toast.
"""
import asyncio, json, pathlib, re, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v172e_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

LIB = 'acad3dFamilyLibrary'
TPL = 'acad3dTemplateV1:'
MESH = "{v:[0,0,0, 1,0,0, 0,1,0],f:[0,1,2]}"

IDB_GET = """(id)=>new Promise(function(res){
  var r;try{r=indexedDB.open('BIM-Personal',1);}catch(e){res({err:String(e)});return;}
  r.onupgradeneeded=function(){r.result.createObjectStore('projects');};
  r.onsuccess=function(){var db=r.result;try{var t=db.transaction('projects','readonly'),g=t.objectStore('projects').get(id);
    g.onsuccess=function(){db.close();res({rec:g.result?g.result.rec:null});};g.onerror=function(){db.close();res({err:'get'});};}
    catch(e){db.close();res({err:String(e)});}};
  r.onerror=function(){res({err:'open'});};})"""
IDB_WIPE = """()=>new Promise(function(res){var r=indexedDB.deleteDatabase('BIM-Personal');r.onsuccess=r.onerror=r.onblocked=function(){res(true);};})"""
REFUSE = """(prefix)=>{window.__v172eSet=window.__v172eSet||Storage.prototype.setItem;
  Storage.prototype.setItem=function(k,v){if(String(k).indexOf(prefix)===0&&String(v).indexOf('"idb":1')<0){
    var e=new Error('full');e.name='QuotaExceededError';throw e;}return window.__v172eSet.call(this,k,v);};}"""
RESTORE = "()=>{if(window.__v172eSet)Storage.prototype.setItem=window.__v172eSet;}"
IDB_REFUSE = """()=>{window.__v172eOpen=IDBFactory.prototype.open;window.__v172eTx=IDBDatabase.prototype.transaction;
  IDBFactory.prototype.open=function(){var e=new Error('full');e.name='QuotaExceededError';throw e;};
  IDBDatabase.prototype.transaction=function(){var e=new Error('full');e.name='QuotaExceededError';throw e;};}"""
IDB_RESTORE = "()=>{IDBFactory.prototype.open=window.__v172eOpen;IDBDatabase.prototype.transaction=window.__v172eTx;}"


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
    m = re.search(r"function bimSaveFamilyLibrary\(\)\{(.*?)\n  \}\n", code, flags=re.S)
    body = m.group(1) if m else ''
    put = body.find("bimIdbPut('lib:family'")
    ptr = body.find("localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify({idb:1")
    ck(put >= 0 and ptr > put and 'if(err){failed(err);return;}' in body[put:ptr],
       'the library\'s pointer is written after its copy has committed, and not on an error')
    ck('if(A3D_FAMLIB_LOADING){A3D_FAMLIB_DIRTY=true;return null;}' in body, 'nothing saves over the library while it is read')
    ck('arr.concat(added)' in code, 'what is added while it is read is kept after what was stored')
    tx = re.search(r"function bimIdbTx\(mode,work,done,again\)\{(.*?)\n  \}\n", code, flags=re.S)
    ck(tx is not None and 'if(err){setTimeout(function(){done(err);},0);return;}' in tx.group(1)
       and 'ended=true;setTimeout(function(){done(e,v);},0);' in tx.group(1),
       'every database answer comes after the call has returned, a refusal at once too')
    calls = [mm.start() for mm in re.finditer(r'bimAskPersist\(\);', code)]
    ex = re.search(r"function bimExportProjectFile\(\)\{(.*?)\n  \}\n", code, flags=re.S)
    ck(len(calls) == 1 and ex and 'bimAskPersist();' in ex.group(1), 'persist() is asked from Save alone (D3)')


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV172e' in t, 'the V172e marker is present')
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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        page.set_default_timeout(8000)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await page.add_init_script("""(function(){window.__v172eToasts=[];
            new MutationObserver(function(){var t=document.getElementById('a3d-toast');
              if(t&&t.textContent&&window.__v172eToasts[window.__v172eToasts.length-1]!==t.textContent)window.__v172eToasts.push(t.textContent);})
            .observe(document,{subtree:true,childList:true,characterData:true});})();""")
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await asyncio.wait_for(ev(js, arg) if arg is not None else ev(js), 12)
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def open_app():
            await page.goto('file://' + str(HTML))
            for _ in range(80):
                if await safe("()=>!!(window.__a3dOn&&window.__a3dLibStore&&!window.__a3dLibStore().loading)"):
                    break
                await page.wait_for_timeout(100)
            await page.wait_for_timeout(500)

        async def toasts_with(s):
            return [x for x in (await safe("()=>window.__v172eToasts") or []) if s in x]

        async def clear_toasts():
            await safe("()=>{window.__v172eToasts=[];var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")

        async def ls_json(key):
            raw = await safe("(k)=>localStorage.getItem(k)", key)
            try:
                return json.loads(raw) if raw else None
            except Exception:
                return None

        async def idb_rec(key):
            return (await safe(IDB_GET, key) or {}).get('rec')

        async def add(name):
            return await safe("(n)=>{var e=window.__a3dFamilyAdd({name:n,category:'Site',mesh:" + MESH + "});return e?e.id:null;}", name)

        async def lib_ids():
            return await safe("()=>window.__a3dLibrary().filter(function(r){return !r.builtin;}).map(function(r){return r.id;})") or []

        # ------------------------------------------------------------------------------------------
        print('\n-- 1. what fits stays where it was')
        await page.goto('file://' + str(BLANK))
        await safe("()=>localStorage.clear()")
        await safe(IDB_WIPE)
        await open_app()
        ck((await safe("()=>window.__a3dPersist().asked")) is False, 'the browser is not asked to keep storage on load (D3)')
        a = await add('V172e first')
        await page.wait_for_timeout(400)
        stored = await ls_json(LIB)
        ck(isinstance(stored, list) and a in [e.get('id') for e in stored], 'a small library is saved whole in its key')
        ck(await idb_rec('lib:family') is None, 'and the database has no copy of it')

        print('\n-- 2. a library localStorage refuses goes to the database')
        await safe(REFUSE, LIB)
        await clear_toasts()
        b = await add('V172e second')
        await page.wait_for_timeout(900)
        ptr = await ls_json(LIB)
        ck(isinstance(ptr, dict) and ptr.get('idb') == 1 and ptr.get('count', 0) >= 2, 'its key holds a pointer (%s)' % (str(ptr)[:80]))
        r = await idb_rec('lib:family')
        ck(r and a in r and b in r, 'the database holds the whole library')
        ck(not await toasts_with('could not be saved'), 'no toast says it could not be saved')
        ck((await safe("()=>window.__a3dLibStore().idb")) is True, 'the library is marked as kept in the database')
        c = await add('V172e third')
        await page.wait_for_timeout(900)
        r = await idb_rec('lib:family')
        ck(r and c in r, 'a later add updates the database\'s copy')
        await safe(RESTORE)
        await open_app()
        ids = await lib_ids()
        ck(all(x in ids for x in (a, b, c)), 'a reload reads the library back from the database (%d entries)' % len(ids))
        ck((await safe("()=>window.__a3dLibStore()")) == {'idb': True, 'loading': False, 'dirty': False}, 'and it is read, kept in the database')

        print('\n-- 3. a template localStorage refuses is kept in the database')
        w = await safe("()=>window.__a3dWall([[0,0],[6,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(500)
        await safe(REFUSE, TPL)
        await clear_toasts()
        tid = await safe("()=>window.__a3dTemplateSave('V172e big template')")
        await page.wait_for_timeout(900)
        await safe(RESTORE)
        ck(tid is not None, 'the template is saved (%s)' % tid)
        ck(await safe("(k)=>localStorage.getItem(k)", TPL + (tid or '')) is None, 'not in localStorage')
        tr = await idb_rec('tpl:' + (tid or ''))
        ck(tr and w in tr, 'but in the database under its own key, with the model')
        ck(not await toasts_with('could not be saved'), 'with no toast that it failed')
        n_docs = len(await safe("()=>window.__a3dDocs.list()") or [])
        used = await safe("(id)=>window.__a3dTemplateUse(id)", tid)
        for _ in range(40):
            if len(await safe("()=>window.__a3dDocs.list()") or []) > n_docs:
                break
            await page.wait_for_timeout(100)
        await page.wait_for_timeout(800)
        objs = await safe("()=>window.__a3dObjects().map(function(o){return o.id;})") or []
        ck(used and len(await safe("()=>window.__a3dDocs.list()") or []) == n_docs + 1 and w in objs,
           'using it opens a new project with the template\'s model (%d objects)' % len(objs))
        await safe("(id)=>window.__a3dFamilyRemove(id)", tid)
        await page.wait_for_timeout(600)
        ck(await idb_rec('tpl:' + tid) is None, 'removing it removes its copy from the database')

        print('\n-- 4. a template both refuse is said so, and its entry goes')
        await safe(REFUSE, TPL)
        await safe(IDB_REFUSE)
        await clear_toasts()
        n_lib = len(await lib_ids())
        bad = await safe("()=>window.__a3dTemplateSave('V172e refused template')")
        await page.wait_for_timeout(900)
        await safe(IDB_RESTORE)
        await safe(RESTORE)
        ck(await toasts_with('template could not be saved'), 'the toast says the template could not be saved (%s)' % (await safe("()=>window.__v172eToasts")))
        ids = await lib_ids()
        ck(bad not in ids and len(ids) == n_lib, 'and its entry is not left in the library (%s, %s, %d to %d)' % (bad, bad in ids, n_lib, len(ids)))

        print('\n-- 5. D3: asked at the first Save, once')
        await safe("()=>window.__a3dExportProject()")
        await page.wait_for_timeout(600)
        p1 = await safe("()=>window.__a3dPersist()") or {}
        ck(p1.get('asked') is True and p1.get('granted') in (True, False), 'the first Save asks, and the answer is kept (%s)' % p1)
        await safe("()=>{window.__v172eAsks=0;var o=navigator.storage.persist;navigator.storage.persist=function(){window.__v172eAsks++;return o.call(navigator.storage);};}")
        await safe("()=>window.__a3dExportProject()")
        await page.wait_for_timeout(600)
        ck((await safe("()=>window.__v172eAsks")) == 0, 'a second Save does not ask again')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
