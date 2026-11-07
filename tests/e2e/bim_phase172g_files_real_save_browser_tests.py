"""bim_phase172g_files_real_save_browser_tests.py -- V172g: files as the real save.

docs/research/research-local-storage.md, part 14 (D2, D4, D5; the owner's G1-G5). What this suite holds the phase to:

  1. THE MARKER. A fresh, empty project is not marked; an edit marks it "Not saved to a file", in the status bar and
     with a dot on its tab; the line runs Save.
  2. THE REMINDERS. At the first edit of a project never saved to a file, where the browser has not agreed to keep the
     app's storage (headless Chromium: persisted() false), one reminder, once (G1); after 30 minutes of work not in a
     file, one reminder, pauses over 2 minutes not counted (D2). The clock is moved by replacing Date.now.
  3. SAVE WITHOUT THE PICKERS (Firefox, Safari): a download of envelope version 2 with the view; Save as asks the type;
     the compressed file starts 1F 8B and is the same envelope; Save keeps the last type (G3); the marker follows.
  4. OPEN: a .gz opens in a tab of its own, "Opened from" it, not marked; a .json holding gzip bytes opens (the bytes
     decide); a version-1 file opens; a truncated .gz is refused with a message and opens nothing.
  5. SAVE WITH THE PICKERS (Chrome, Edge). Headless Chromium cannot show a picker, so the pickers are replaced by ones
     answering with real origin-private file handles (the same FileSystemFileHandle a picker gives): the first Save asks
     where; the second writes the same file without asking (the handle kept in the database); a file changed elsewhere
     is asked about, Cancel leaving it as it is and Overwrite replacing it (G4); Save as a .gz writes gzip; a close()
     that fails leaves the project marked and says the file is as it was; Open through the open picker.
  6. STORAGE REFUSED (D5): with localStorage and indexedDB.open throwing SecurityError, as WebKit does on file://, one
     true message and none of the three untrue ones; Save downloads; a second project opens in its own tab and the first
     comes back from the page's memory.
  7. A PHONE: the status bar's line inside the screen; Save as's question fits, its buttons 36 px or more.

Storage is wiped from a blank page of the same origin with the app closed (the V115 rule).
"""
import asyncio, gzip, http.server, json, pathlib, sys, tempfile, threading
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent.parent / 'canvas_v10.html'
TMP = pathlib.Path(tempfile.mkdtemp(prefix='v172g_'))
BLANK = TMP / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

WIPE = """()=>new Promise(function(res){localStorage.clear();var r=indexedDB.deleteDatabase('BIM-Personal');r.onsuccess=r.onerror=r.onblocked=function(){res(true);};})"""
TOASTS = """(function(){window.__v172gToasts=[];new MutationObserver(function(){var t=document.getElementById('a3d-toast');
  if(t&&t.textContent&&window.__v172gToasts[window.__v172gToasts.length-1]!==t.textContent)window.__v172gToasts.push(t.textContent);})
  .observe(document,{subtree:true,childList:true,characterData:true});})();"""
REFUSE = """(function(){function r(){return new DOMException('The operation is insecure.','SecurityError');}
  Object.defineProperty(window,'localStorage',{configurable:true,get:function(){throw r();}});
  if(window.indexedDB)Object.getPrototypeOf(window.indexedDB).open=function(){throw r();};})();"""


def serve():
    # origin-private files are refused to file:// pages in Chromium (part 4.4, e12), so section 5 runs over http
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            f = {'/app.html': HTML, '/blank.html': BLANK}.get(self.path.split('?')[0])
            if not f:
                self.send_response(404); self.end_headers(); return
            body = f.read_bytes()
            self.send_response(200); self.send_header('content-type', 'text/html; charset=utf-8')
            self.send_header('content-length', str(len(body))); self.end_headers(); self.wfile.write(body)

        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


NO_PICKERS = "()=>{window.showSaveFilePicker=undefined;window.showOpenFilePicker=undefined;}"
# pickers answering with origin-private file handles; __v172gFail wraps the handle so that close() fails
FAKE_PICKERS = """()=>{
  var P=window.__v172gPick={save:0,open:0,saveName:'House.acad3d.json',openName:null,fail:false,lastSave:null};
  function opfs(n){return navigator.storage.getDirectory().then(function(d){return d.getFileHandle(n,{create:true});});}
  function failing(h){return {kind:'file',name:h.name,getFile:function(){return h.getFile();},
    queryPermission:function(){return Promise.resolve('granted');},requestPermission:function(){return Promise.resolve('granted');},
    createWritable:function(){return h.createWritable().then(function(w){return {write:function(b){return w.write(b);},
      close:function(){return w.abort().then(function(){throw new DOMException('Blocked by Safe Browsing.','AbortError');});},
      abort:function(){return Promise.resolve();}};});}};}
  window.showSaveFilePicker=function(o){P.save++;P.lastSave=JSON.parse(JSON.stringify(o||{}));
    return opfs(P.saveName).then(function(h){return P.fail?failing(h):h;});};
  window.showOpenFilePicker=function(o){P.open++;return opfs(P.openName).then(function(h){return [h];});};
}"""
OPFS_READ = """(n)=>navigator.storage.getDirectory().then(function(d){return d.getFileHandle(n);}).then(function(h){return h.getFile();})
  .then(function(f){return f.arrayBuffer();}).then(function(b){return Array.prototype.slice.call(new Uint8Array(b));})"""
OPFS_WRITE = """(a)=>navigator.storage.getDirectory().then(function(d){return d.getFileHandle(a.n,{create:true});})
  .then(function(h){return h.createWritable().then(function(w){return w.write(new Uint8Array(a.b)).then(function(){return w.close();});});})"""


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
    ck('__acad3dV172g' in t, 'the V172g marker is present')
    if not ck.bad:
        try:
            await drive(ck)
        except Exception as e:
            ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:200]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


def envelope_of(raw):
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return json.loads(raw.decode('utf-8'))


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def new_page(refuse=False, viewport=None, touch=False):
            ctx = await browser.new_context(viewport=viewport or {'width': 1500, 'height': 950}, accept_downloads=True,
                                            has_touch=touch, is_mobile=touch)
            await ctx.add_init_script(TOASTS)
            if refuse:
                await ctx.add_init_script(REFUSE)
            pg = await ctx.new_page()
            pg.set_default_timeout(8000)
            pg.errs = []
            pg.on('pageerror', lambda e: pg.errs.append(str(e)[:200]))
            return ctx, pg

        async def safe(pg, js, arg=None):
            try:
                return await asyncio.wait_for(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 15)
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def open_app(pg, wipe=True, base=None):
            if wipe:
                await pg.goto(base + '/blank.html' if base else 'file://' + str(BLANK))
                await safe(pg, WIPE)
            await pg.goto(base + '/app.html' if base else 'file://' + str(HTML))
            for _ in range(80):
                st = await safe(pg, "()=>window.__a3dStore?window.__a3dStore().mode:null")
                if st in ('idb', 'legacy', 'refused'):
                    break
                await pg.wait_for_timeout(100)
            await pg.wait_for_timeout(900)

        async def toasts(pg):
            return await safe(pg, "()=>window.__v172gToasts") or []

        async def fstate(pg):
            return await safe(pg, "()=>window.__a3dFileState()") or {}

        async def bar(pg):
            return await safe(pg, "()=>{var b=document.getElementById('a3d-stfile');return b?{hidden:b.hidden,text:b.textContent,state:b.getAttribute('data-state')}:null;}") or {}

        async def dot(pg):
            return await safe(pg, "()=>!!document.querySelector('#acad-doctabs .acad-doctab.active .dt-dot')")

        async def edit(pg, n=1):
            await safe(pg, "(n)=>{for(var i=0;i<n;i++)window.__a3dAddPoint(i,0,i);}", n)
            # the point hook does not call saveSoon, as every real edit does; setting the title block to itself does
            await safe(pg, "()=>window.__a3dTitleBlockSet(window.__a3dTitleBlockGet())")
            await pg.wait_for_timeout(400)

        async def download(pg, js):
            try:
                async with pg.expect_download(timeout=6000) as d:
                    await safe(pg, js)
                dl = await d.value
                return dl.suggested_filename, pathlib.Path(await dl.path()).read_bytes()
            except Exception as e:
                print('      (no download: %s)' % str(e)[:120])
                return None, None

        # ------------------------------------------------------------------------------------------
        print('\n-- 1. the marker')
        ctx, page = await new_page()
        await open_app(page)
        await safe(page, NO_PICKERS)
        b0 = await bar(page)
        ck(b0.get('hidden') is True and (await fstate(page)).get('state', {}).get('kind') == 'none',
           'a fresh, empty project is not marked (%s)' % b0)
        await edit(page, 2)
        b1 = await bar(page)
        ck(b1.get('hidden') is False and b1.get('text') == 'Not saved to a file' and b1.get('state') == 'unsaved',
           'an edit marks it in the status bar (%s)' % b1)
        await page.wait_for_timeout(1200)   # the tabs are drawn again within a second
        ck(await dot(page), 'and with a dot on its tab')
        name, raw = None, None
        try:
            async with page.expect_download(timeout=6000) as d:
                await page.click('#a3d-stfile')
            dl = await d.value
            name, raw = dl.suggested_filename, pathlib.Path(await dl.path()).read_bytes()
        except Exception as e:
            print('      (no download: %s)' % str(e)[:120])
        ck(name == 'Untitled project.acad3d.json', 'the line runs Save (%s)' % name)

        # ------------------------------------------------------------------------------------------
        print('\n-- 2. the reminders')
        await open_app(page)
        await safe(page, NO_PICKERS)
        await edit(page)
        await edit(page)
        first = [x for x in await toasts(page) if 'may clear its copy' in x]
        ck(len(first) == 1 and 'Use Save (Ctrl+S)' in first[0],
           'the first edit where persisted() is false gives one reminder, once (%s)' % first)
        await safe(page, "()=>{var real=Date.now;window.__v172gOff=0;Date.now=function(){return real()+window.__v172gOff;};}")
        for i in range(31):
            await safe(page, "()=>{window.__v172gOff+=60000;window.__a3dTitleBlockSet(window.__a3dTitleBlockGet());}")
        await page.wait_for_timeout(400)
        thirty = [x for x in await toasts(page) if '30 minutes of work' in x]
        ck(len(thirty) == 1, 'after 30 minutes of work not in a file, one reminder (%d)' % len(thirty))
        # the watcher drops a toast that repeats the one before it: start the count afresh
        await safe(page, "()=>{window.__v172gToasts=[];var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")
        await safe(page, "()=>{window.__v172gOff+=10*60000;window.__a3dTitleBlockSet(window.__a3dTitleBlockGet());}")
        for i in range(25):
            await safe(page, "()=>{window.__v172gOff+=60000;window.__a3dTitleBlockSet(window.__a3dTitleBlockGet());}")
        await page.wait_for_timeout(300)
        n2 = len([x for x in await toasts(page) if '30 minutes of work' in x])
        ck(n2 == 0, 'a 10-minute pause is not counted: 25 more minutes of work give no second reminder yet (%d)' % n2)
        for i in range(6):
            await safe(page, "()=>{window.__v172gOff+=60000;window.__a3dTitleBlockSet(window.__a3dTitleBlockGet());}")
        await page.wait_for_timeout(300)
        n3 = len([x for x in await toasts(page) if '30 minutes of work' in x])
        ck(n3 == 1, 'after 30 more minutes of work, the second reminder (%d)' % n3)

        # ------------------------------------------------------------------------------------------
        print('\n-- 3. Save without the pickers')
        await open_app(page)
        await safe(page, NO_PICKERS)
        await edit(page, 3)
        cam = await safe(page, "()=>{var e=JSON.parse(window.__a3dProjectEnvelope());return e.data.cam;}")
        name, raw = await download(page, "()=>window.__a3dFileSave(false)")
        env = envelope_of(raw) if raw else {}
        ck(name == 'Untitled project.acad3d.json' and env.get('formatVersion') == 2 and env.get('app') == 'acad3d-project',
           'Save downloads envelope version 2 (%s, v%s)' % (name, env.get('formatVersion')))
        ck(env.get('data', {}).get('cam') == cam and isinstance(env.get('data', {}).get('seq'), int) and 'docId' not in env.get('data', {}),
           'with the view and the id counter, without the browser\'s id')
        ck(len(env.get('data', {}).get('objs', [])) == 3, 'holding the three objects')
        b = await bar(page)
        ck(b.get('state') == 'saved' and b.get('text', '').startswith('Downloaded as Untitled project.acad3d.json'),
           'the line says it was downloaded (%s)' % b.get('text'))
        await page.wait_for_timeout(1200)
        ck(not await dot(page), 'and the tab\'s dot is gone')
        await edit(page)
        ck((await bar(page)).get('text') == 'Changes not saved to Untitled project.acad3d.json', 'an edit after it: changes not saved to it')
        await safe(page, "()=>{window.__v172gAs=window.__a3dFileSave(true);}")
        await page.wait_for_timeout(200)
        btns = await safe(page, "()=>Array.prototype.map.call(document.querySelectorAll('#a3d-filedlg [data-a3dfd]'),function(b){return b.getAttribute('data-a3dfd');})") or []
        ck(btns == ['json', 'gz', 'cancel'], 'Save as asks the type, plain first (%s)' % btns)
        try:
            async with page.expect_download(timeout=6000) as d:
                await page.click('#a3d-filedlg [data-a3dfd="gz"]')
            dl = await d.value
            name, raw = dl.suggested_filename, pathlib.Path(await dl.path()).read_bytes()
        except Exception as e:
            name, raw = None, None
            print('      (no download: %s)' % str(e)[:120])
        ck(name == 'Untitled project.acad3d.json.gz' and raw and raw[:2] == b'\x1f\x8b',
           'the compressed file is named for it and starts 1F 8B (%s)' % name)
        genv = envelope_of(raw) if raw else {}
        ck(genv.get('formatVersion') == 2 and len(genv.get('data', {}).get('objs', [])) == 4, 'and is the same envelope, four objects')
        ck(raw is not None and len(raw) < len(json.dumps(genv)), 'and is smaller than the plain file')
        await edit(page)
        name2, raw2 = await download(page, "()=>window.__a3dFileSave(false)")
        ck(name2 == 'Untitled project.acad3d.json.gz' and raw2 and raw2[:2] == b'\x1f\x8b', 'Save keeps the last type (%s)' % name2)
        gzfile = raw2

        # ------------------------------------------------------------------------------------------
        print('\n-- 4. Open')
        n_tabs = len(await safe(page, "()=>window.__a3dDocs.open()") or [])
        p1 = TMP / 'Pier.acad3d.json.gz'
        p1.write_bytes(gzfile)
        await page.set_input_files('#a3d-projin', str(p1))
        await page.wait_for_timeout(1200)
        st = await fstate(page)
        ck(len(await safe(page, "()=>window.__a3dDocs.open()") or []) == n_tabs + 1 and len(await safe(page, "()=>window.__a3dObjects()") or []) == 5,
           'a .gz opens in a tab of its own with its five objects')
        ck((st.get('entry') or {}).get('fileName') == 'Pier.acad3d.json.gz' and st.get('state', {}).get('kind') == 'saved'
           and (await bar(page)).get('text', '').startswith('Opened from Pier.acad3d.json.gz'), 'opened from it, not marked (%s)' % st.get('state'))
        p2 = TMP / 'Disguised.json'
        p2.write_bytes(gzfile)
        await page.set_input_files('#a3d-projin', str(p2))
        await page.wait_for_timeout(1200)
        ck((await fstate(page)).get('entry', {}).get('fileName') == 'Disguised.json' and len(await safe(page, "()=>window.__a3dObjects()") or []) == 5,
           'a .json holding gzip bytes opens: the bytes decide')
        p3 = TMP / 'Old.acad3d.json'
        p3.write_text(json.dumps({'app': 'acad3d-project', 'formatVersion': 1, 'savedAt': '2026-01-01T00:00:00Z',
                                  'data': {'objs': genv['data']['objs'][:1], 'titleBlock': {'project': 'Old one', 'client': '', 'drawnBy': '', 'checkedBy': ''}}}), encoding='utf-8')
        await page.set_input_files('#a3d-projin', str(p3))
        await page.wait_for_timeout(1200)
        ck(len(await safe(page, "()=>window.__a3dObjects()") or []) == 1 and not [x for x in await toasts(page) if 'newer version' in x],
           'a version-1 file opens without a warning')
        n_before = len(await safe(page, "()=>window.__a3dDocs.open()") or [])
        p4 = TMP / 'Broken.acad3d.json.gz'
        p4.write_bytes(gzfile[:-10])
        await page.set_input_files('#a3d-projin', str(p4))
        await page.wait_for_timeout(1200)
        bad = [x for x in await toasts(page) if 'Broken.acad3d.json.gz is damaged or incomplete' in x]
        ck(bad and len(await safe(page, "()=>window.__a3dDocs.open()") or []) == n_before,
           'a truncated .gz is refused with a message and opens nothing (%s)' % bad[:1])
        ck(not page.errs, 'no page errors so far (%s)' % page.errs[:2])
        await ctx.close()

        # ------------------------------------------------------------------------------------------
        print('\n-- 5. Save with the pickers')
        srv = serve()
        # a file handle read back from IndexedDB closes the browser in an off-the-record context (part 4.6, e12):
        # this section runs in a persistent profile, as a user's browser does
        ctx = await pw.chromium.launch_persistent_context(str(TMP / 'profile'), viewport={'width': 1500, 'height': 950}, accept_downloads=True)
        await ctx.add_init_script(TOASTS)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        page.set_default_timeout(8000)
        page.errs = []
        page.on('pageerror', lambda e: page.errs.append(str(e)[:200]))
        await open_app(page, base='http://127.0.0.1:%d' % srv.server_address[1])
        await safe(page, FAKE_PICKERS)
        await edit(page, 2)
        await safe(page, "()=>window.__a3dFileSave(false)")
        await page.wait_for_timeout(1200)
        pick = await safe(page, "()=>window.__v172gPick") or {}
        raw = bytes(await safe(page, OPFS_READ, 'House.acad3d.json') or [])
        env = envelope_of(raw) if raw else {}
        ck(pick.get('save') == 1 and env.get('formatVersion') == 2 and len(env.get('data', {}).get('objs', [])) == 2,
           'the first Save asks where and writes envelope version 2 there (%s pickers)' % pick.get('save'))
        so = pick.get('lastSave') or {}
        ck(so.get('id') == 'acad3d-projects' and so.get('suggestedName') == 'Untitled project.acad3d.json'
           and [list(x['accept'].values())[0][0] for x in so.get('types', [])] == ['.acad3d.json', '.acad3d.json.gz'],
           'the save picker: the folder id, the name, plain then compressed (%s)' % so)
        b = await bar(page)
        ck(b.get('state') == 'saved' and b.get('text', '').startswith('Saved to House.acad3d.json'), 'the line says where (%s)' % b.get('text'))
        stored = await safe(page, "()=>new Promise(function(r){var q=indexedDB.open('BIM-Personal');q.onsuccess=function(){var db=q.result,"
                                  "g=db.transaction('projects').objectStore('projects').getAllKeys();g.onsuccess=function(){db.close();r(g.result);};};})") or []
        ck(any(str(k).startswith('lib:file:') for k in stored), 'the file\'s handle is kept in the database (%s)' % [k for k in stored if str(k).startswith('lib:')])
        await edit(page)
        await safe(page, "()=>window.__a3dFileSave(false)")
        await page.wait_for_timeout(1200)
        pick = await safe(page, "()=>window.__v172gPick") or {}
        env = envelope_of(bytes(await safe(page, OPFS_READ, 'House.acad3d.json') or []))
        ck(pick.get('save') == 1 and len(env.get('data', {}).get('objs', [])) == 3,
           'the second Save writes the same file without asking (%s pickers, %d objects)' % (pick.get('save'), len(env.get('data', {}).get('objs', []))))
        await page.wait_for_timeout(50)
        await safe(page, OPFS_WRITE, {'n': 'House.acad3d.json', 'b': list(b'{"changed":"elsewhere"}')})
        await edit(page)
        await safe(page, "()=>window.__a3dFileSave(false)")
        await page.wait_for_timeout(800)
        title = await safe(page, "()=>{var t=document.querySelector('#a3d-filedlg .a3d-filedlg-t');return t?t.textContent:null;}")
        btns = await safe(page, "()=>Array.prototype.map.call(document.querySelectorAll('#a3d-filedlg [data-a3dfd]'),function(b){return b.getAttribute('data-a3dfd');})") or []
        ck(title == 'The file has changed' and btns == ['over', 'as', 'cancel'], 'a file changed elsewhere is asked about (%s, %s)' % (title, btns))
        await page.click('#a3d-filedlg [data-a3dfd="cancel"]')
        await page.wait_for_timeout(500)
        raw = bytes(await safe(page, OPFS_READ, 'House.acad3d.json') or [])
        ck(raw == b'{"changed":"elsewhere"}' and (await bar(page)).get('state') == 'changed', 'Cancel leaves the file as it is, the project marked')
        await safe(page, "()=>window.__a3dFileSave(false)")
        await page.wait_for_timeout(800)
        await page.click('#a3d-filedlg [data-a3dfd="over"]')
        await page.wait_for_timeout(1200)
        env = envelope_of(bytes(await safe(page, OPFS_READ, 'House.acad3d.json') or []))
        ck(env.get('formatVersion') == 2 and len(env.get('data', {}).get('objs', [])) == 4 and (await bar(page)).get('state') == 'saved',
           'Overwrite replaces it with the project')
        await safe(page, "()=>{window.__v172gPick.saveName='House.acad3d.json.gz';}")
        await safe(page, "()=>window.__a3dFileSave(true)")
        await page.wait_for_timeout(1500)
        raw = bytes(await safe(page, OPFS_READ, 'House.acad3d.json.gz') or [])
        ck(raw[:2] == b'\x1f\x8b' and envelope_of(raw).get('formatVersion') == 2 and (await fstate(page)).get('entry', {}).get('fileType') == 'gz',
           'Save as a .gz writes gzip, made in the worker, and the project now saves as gzip')
        await edit(page)
        await safe(page, "()=>{window.__v172gPick.saveName='Fail.acad3d.json';window.__v172gPick.fail=true;}")
        await safe(page, "()=>window.__a3dFileSave(true)")
        await page.wait_for_timeout(1200)
        fail = [x for x in await toasts(page) if x.startswith('Not saved to Fail.acad3d.json') and 'The file on disk is as it was' in x]
        b = await bar(page)
        ck(fail and b.get('state') == 'changed' and 'House.acad3d.json.gz' in b.get('text', ''),
           'a close() that fails: the project stays marked, the file said to be as it was (%s)' % (fail[:1] or b))
        await safe(page, "()=>{window.__v172gPick.fail=false;window.__v172gPick.openName='House.acad3d.json.gz';}")
        n_tabs = len(await safe(page, "()=>window.__a3dDocs.open()") or [])
        await safe(page, "()=>window.__a3dFileOpen()")
        await page.wait_for_timeout(1500)
        st = await fstate(page)
        ck(len(await safe(page, "()=>window.__a3dDocs.open()") or []) == n_tabs + 1 and (st.get('entry') or {}).get('fileName') == 'House.acad3d.json.gz'
           and (st.get('entry') or {}).get('fileVia') == 'opened', 'Open through the open picker opens the .gz in a tab of its own')
        ck(not page.errs, 'no page errors with the pickers (%s)' % page.errs[:2])
        await ctx.close()
        srv.shutdown()

        # ------------------------------------------------------------------------------------------
        print('\n-- 6. storage refused (D5)')
        ctx, page = await new_page(refuse=True)
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(3500)
        await safe(page, NO_PICKERS)
        tt = await toasts(page)
        ck((await fstate(page)).get('noStorage') is True and any('keeps nothing for a page opened from a file' in x for x in tt),
           'one true message: the project lives only in its file')
        untrue = [x for x in tt if 'could not be removed' in x or 'about 5 MB' in x or 'storage is full' in x]
        await edit(page, 2)
        untrue += [x for x in await toasts(page) if 'storage is full' in x]
        ck(not untrue, 'none of the three untrue messages (%s)' % untrue[:2])
        ck((await bar(page)).get('text') == 'Not saved to a file', 'the marker is on')
        name, raw = await download(page, "()=>window.__a3dFileSave(false)")
        ck(name == 'Untitled project.acad3d.json' and envelope_of(raw).get('formatVersion') == 2, 'Save downloads the file')
        first_id = await safe(page, "()=>window.__a3dDocs.active()")
        await page.set_input_files('#a3d-projin', str(p3))
        await page.wait_for_timeout(1200)
        ck(len(await safe(page, "()=>window.__a3dDocs.open()") or []) == 2 and len(await safe(page, "()=>window.__a3dObjects()") or []) == 1,
           'a second project opens in a tab of its own')
        await safe(page, "(id)=>window.__a3dDocs.activate(id)", first_id)
        await page.wait_for_timeout(800)
        ck(len(await safe(page, "()=>window.__a3dObjects()") or []) == 2, 'and the first comes back from the page\'s memory with its two objects')
        ck(not page.errs, 'no page errors with storage refused (%s)' % page.errs[:2])
        await ctx.close()

        # ------------------------------------------------------------------------------------------
        print('\n-- 7. a phone')
        ctx, page = await new_page(viewport={'width': 390, 'height': 844}, touch=True)
        await open_app(page)
        await safe(page, NO_PICKERS)
        await edit(page)
        box = await safe(page, "()=>{var b=document.getElementById('a3d-stfile');if(!b||b.hidden)return null;var r=b.getBoundingClientRect();return {l:r.left,r:r.right,w:r.width,vis:getComputedStyle(b).display!=='none'};}")
        ck(box is None or (box['l'] >= 0 and box['r'] <= 390), 'the status bar\'s line stays inside the screen (%s)' % box)
        await safe(page, "()=>{window.__a3dFileSave(true);}")
        await page.wait_for_timeout(300)
        dlg = await safe(page, "()=>{var b=document.querySelector('#a3d-filedlg .a3d-filedlg-box');if(!b)return null;var r=b.getBoundingClientRect();"
                               "var h=Array.prototype.map.call(document.querySelectorAll('#a3d-filedlg .a3d-btn'),function(x){return x.getBoundingClientRect().height;});"
                               "return {l:r.left,r:r.right,minH:Math.min.apply(null,h)};}")
        ck(dlg and dlg['l'] >= 0 and dlg['r'] <= 390 and dlg['minH'] >= 36, 'Save as\'s question fits, its buttons 36 px or more (%s)' % dlg)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        ck(not await safe(page, "()=>!!document.getElementById('a3d-filedlg')"), 'Escape closes it')
        ck(not page.errs, 'no page errors on a phone (%s)' % page.errs[:2])
        await ctx.close()
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
