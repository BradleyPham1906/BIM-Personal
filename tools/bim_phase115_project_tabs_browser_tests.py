#!/usr/bin/env python3
"""bim_phase115_project_tabs_browser_tests.py -- V115: several projects open side by side, the way
AutoCAD's file tabs and Revit's open projects work, with a Start page you can actually see.

  1. AN EXISTING USER LOSES NOTHING. A store written before V115 (one project in acad3dV1, no list)
     boots into one tab holding that project, and the record is tagged with its project's id.
  2. EACH TAB IS ITS OWN PROJECT. + makes a new one; its model starts empty; switching tabs swaps
     the whole model, and nothing of one project survives into another -- asserted on the objects
     and levels, not on a label.
  3. EACH PROJECT HAS ITS OWN UNDO. Undo in one tab never reaches into another, and a tab you come
     back to still has its history.
  4. STORAGE HOLDS EVERY PROJECT IN EXACTLY ONE PLACE. The one on screen in acad3dV1, every other
     in its own key; checked after each switch rather than trusted.
  5. THE DOCUMENT COMMANDS WORK. The quick-access bar's Save, Undo and Redo did nothing before this
     phase; NEW, CLOSE and the rest run from the command palette.
  6. OPEN OPENS, IT DOES NOT REPLACE. A project file opens in a tab of its own, with no confirm(),
     named from the file when its title block has no name; a DXF given to Open is refused.
  7. CLOSE, REOPEN, DELETE. Closing a tab moves to its neighbour; a closed project waits on Start;
     deleting asks first and a cancel keeps it.
  8. FAILURES ARE LOUD AND LEAVE NOTHING HALF-DONE. A damaged project, a full store during a switch,
     and a failed autosave each say so, and the project on screen stays whole.
  9. THE START PAGE IS SEEN. It is what is on top, over the drawing area and the dock, and while it
     shows no key or command reaches the project hidden behind it.
 10. BOOT REPAIRS WHAT A CRASH LEAVES. A copy left by an interrupted switch is dropped, a stored
     project the list lost is listed again, and a list entry with nothing stored is dropped.
"""
import asyncio, json, pathlib, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v115_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


LEGACY = {'objs': [], 'titleBlock': {'project': 'Legacy Tower', 'client': '', 'drawnBy': '', 'checkedBy': ''},
          'levels': [{'id': 'lvl-0', 'name': 'Ground', 'elev': 0, 'height': 3.5, 'buildingId': 'bldg-0'}],
          'activeLevel': 'lvl-0'}


async def main():
    ck = Checks()
    t = HTML.read_text(encoding='utf-8')
    ck('__acad3dV115' in t, 'the V115 marker is present')
    if ck.bad:
        print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
        print('RESULT: FAIL')
        sys.exit(1)

    try:
        await drive(ck)
    except Exception as e:
        ck(False, 'the suite ran to the end (stopped by %s: %s)' % (type(e).__name__, str(e).splitlines()[0][:160]))
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    sys.exit(1 if ck.bad else 0)


async def drive(ck):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        # No init script touches localStorage. Measured in V115: on a file:// page, an init script that
        # reads localStorage at document start leaves the page's storage cut off from the browser in
        # about half of all runs -- every write stays in the page and a reload finds nothing (4 runs
        # of 8 lost, 0 of 8 without the init script). The store written before V115 is set up by
        # hand instead: clear, write the old record, reload.
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs, dialogs = [], []
        answer = {'accept': False}
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))

        async def on_dialog(d):
            dialogs.append(d.message)
            if answer['accept']:
                await d.accept()
            else:
                await d.dismiss()
        page.on('dialog', lambda d: asyncio.ensure_future(on_dialog(d)))
        ev = page.evaluate

        async def ready():
            try:
                await page.wait_for_function("()=>!!window.__a3dDocs&&!!window.__a3dObjects&&"
                                             "document.querySelectorAll('#acad-doctabs button').length>0&&"
                                             "(!!window.__a3dDocs.active()||!!document.getElementById('acad-start'))", timeout=20000)
            except Exception as e:
                print('      (the workspace did not come up: %s)' % str(e)[:100])
            await page.wait_for_timeout(400)

        await page.goto('file://' + str(HTML))
        await ready()

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        async def tabs():
            return (await safe("()=>Array.prototype.map.call(document.querySelectorAll('#acad-doctabs button'),"
                               "function(b){var n=b.querySelector('.dt-name');return [b.getAttribute('data-dt'),(n||b).textContent.trim(),"
                               "b.classList.contains('active'),b.getAttribute('data-doc')];})")) or []

        async def docs():
            return (await safe("()=>window.__a3dDocs.list()")) or []

        async def objs():
            return await safe("()=>window.__a3dObjects().length")

        async def toast():
            return (await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}")) or ''

        async def clear_toast():
            await safe("()=>{var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")
            await page.wait_for_timeout(30)

        async def click_tab(doc_id):
            await page.click('#acad-doctabs [data-doc="%s"] .dt-name' % doc_id)
            await page.wait_for_timeout(450)

        async def active_id():
            return await safe("()=>window.__a3dDocs.active()")

        async def storage_places():
            """Where each project is stored: the one in acad3dV1, and every acad3dDocV1: key."""
            return await safe("""()=>{var o={slot:null,keys:[]};
                try{o.slot=JSON.parse(localStorage.getItem('acad3dV1')||'{}').docId||null;}catch(e){}
                for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);
                  if(k.indexOf('acad3dDocV1:')===0)o.keys.push(k.slice(12));}
                o.keys.sort();return o;}""")

        async def one_place(label):
            await page.wait_for_timeout(450)     # the autosave that follows a switch
            pl = await storage_places()
            ds = await docs()
            act = [d['id'] for d in ds if d['loaded']]
            others = sorted(d['id'] for d in ds if not d['loaded'])
            ck(pl is not None and len(act) == 1 and pl['slot'] == act[0] and act[0] not in pl['keys'] and pl['keys'] == others,
               '%s: every project is stored in exactly one place -- the one on screen in acad3dV1, each other in its own key (%s)'
               % (label, pl))

        async def start_state():
            return await safe("""()=>{var s=document.getElementById('acad-start');if(!s)return null;
                var r=s.getBoundingClientRect(),e=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2),
                    d=document.elementFromPoint(30,420),hv=document.getElementById('a3d-view'),hr=hv&&hv.getBoundingClientRect(),
                    he=hr&&document.elementFromPoint(hr.x+hr.width/2,hr.y+hr.height/2);
                return {shown:s.classList.contains('show'),onTop:!!(e&&e.closest('#acad-start')),
                        overDock:!!(d&&d.closest('#acad-start')),wsHidden:!!(he&&he.closest('#acad-start')),
                        cards:Array.prototype.map.call(s.querySelectorAll('.st-card'),function(c){
                          return {id:c.getAttribute('data-doc'),name:c.querySelector('.st-name').textContent,
                                  meta:c.querySelector('.st-meta').textContent,del:!!c.querySelector('.st-del')};})};}""")

        # ---------------------------------------------------------------------------------------
        # the old store is written while the app is closed -- from a blank page on the same file://
        # origin -- so nothing the app still has pending can land on top of it
        await page.goto('file://' + str(BLANK))
        await safe("(rec)=>{localStorage.clear();localStorage.setItem('acad3dV1',rec);}", json.dumps(LEGACY))
        await page.goto('file://' + str(HTML))
        await ready()
        print('\n-- 1. a store written before V115 boots into one tab and loses nothing')
        tb = await tabs()
        ds = await docs()
        ck([x[0] for x in tb] == ['start', 'doc', 'new'] and tb[1][1] == 'Legacy Tower' and tb[1][2] is True,
           'one tab, named from the stored title block, active (%s)' % tb)
        lv = await safe("()=>window.__a3dLevels().map(function(l){return l.name;})")
        ck(len(ds) == 1 and ds[0]['loaded'] and lv == ['Ground'],
           'the project list has that one project, and its model is the stored one -- level "Ground" (%s / %s)' % (len(ds), lv))
        idx = await safe("()=>JSON.parse(localStorage.getItem('acad3dDocsV1')||'null')")
        ck(idx is not None and idx.get('open') == [ds[0]['id']] and idx.get('active') == ds[0]['id'],
           'the list is written, with that project open and on screen (%s)' % idx)
        legacy = ds[0]['id'] if ds else None
        await safe("()=>{window.__a3dWall([[0,0],[4,0]],0.3,null,'center',false);}")
        await page.wait_for_timeout(500)
        pl = await storage_places()
        ck(pl is not None and pl['slot'] == legacy,
           'the next save tags acad3dV1 with the project it holds, so boot never has to guess (%s)' % pl)
        await page.click('#acad-qat [data-acad-act="undo"]')
        await page.wait_for_timeout(450)

        # ---------------------------------------------------------------------------------------
        print('\n-- 2. + makes a separate project, and switching swaps the whole model')
        await page.click('#acad-doctabs [data-dt="new"]')
        await page.wait_for_timeout(500)
        tb = await tabs()
        ck([x[0] for x in tb] == ['start', 'doc', 'doc', 'new'] and tb[2][1] == 'Project1' and tb[2][2] is True and tb[1][2] is False,
           'a second tab, Project1, is active and the first is still open (%s)' % tb)
        p1 = tb[2][3] if len(tb) == 4 else None
        lv = await safe("()=>window.__a3dLevels().map(function(l){return l.name;})")
        ck((await objs()) == 0 and lv == ['Level 0'],
           'its model is a fresh one: no objects, the default level -- nothing of Legacy Tower came along (%s)' % lv)
        ck((await safe("()=>window.__a3dTitleBlockGet().project")) == 'Project1',
           'its name is in its own title block, so tab, sheets and Properties show one name')
        await one_place('after +')
        await safe("()=>{window.__a3dWall([[0,0],[6,0]],0.3,null,'center',false);window.__a3dWall([[6,0],[6,4]],0.3,null,'center',false);}")
        ck((await objs()) == 2, 'two walls drawn in Project1')
        await click_tab(legacy)
        lv = await safe("()=>window.__a3dLevels().map(function(l){return l.name;})")
        ck((await objs()) == 0 and lv == ['Ground'] and (await active_id()) == legacy,
           'clicking Legacy Tower\'s tab brings back its model -- no walls, level "Ground" -- and none of Project1 leaks in (%s)' % lv)
        await one_place('after switching back')
        await click_tab(p1)
        ck((await objs()) == 2 and (await safe("()=>window.__a3dLevels()[0].name")) == 'Level 0',
           'and Project1 comes back with its two walls')

        # ---------------------------------------------------------------------------------------
        print('\n-- 3. each project has its own undo history')
        ud = await safe("()=>window.__a3dDocs.undoDepth()")
        ck(ud and ud['undo'] == 2, 'Project1 has two steps to undo (%s)' % ud)
        await click_tab(legacy)
        ud2 = await safe("()=>window.__a3dDocs.undoDepth()")
        await page.mouse.click(800, 450)
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(250)
        ck(ud2 and ud2['undo'] == 0 and ud2['redo'] == 1 and (await objs()) == 0,
           "Legacy Tower's history is its own: nothing to undo, one step to redo, and Ctrl+Z there changes nothing (%s)" % ud2)
        await click_tab(p1)
        ud3 = await safe("()=>window.__a3dDocs.undoDepth()")
        ck((await objs()) == 2 and ud3 and ud3['undo'] == 2,
           "and it did not reach into Project1: two walls, two steps to undo (%s)" % ud3)
        await page.click('#acad-qat [data-acad-act="undo"]')
        await page.wait_for_timeout(250)
        ck((await objs()) == 1, "the quick-access bar's Undo works, in Project1's own history (it did nothing before V115)")
        await page.click('#acad-qat [data-acad-act="redo"]')
        await page.wait_for_timeout(250)
        ck((await objs()) == 2, "and its Redo puts the wall back")

        # ---------------------------------------------------------------------------------------
        print('\n-- 4. the document commands')
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(150)
        await page.keyboard.type('NEW')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(500)
        tb = await tabs()
        ck(len(tb) == 5 and tb[3][1] == 'Project2' and tb[3][2] is True,
           'NEW on the command line opens Project2 -- a name no other project has (%s)' % [x[1] for x in tb])
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(150)
        await page.keyboard.type('CLOSE')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(500)
        tb = await tabs()
        ck([x[1] for x in tb] == ['Start', 'Legacy Tower', 'Project1', '+'] and tb[2][2] is True,
           'CLOSE closes it and the neighbour tab takes over (%s)' % [x[1] for x in tb])
        dl = None
        try:
            async with page.expect_download(timeout=4000) as d:
                await page.click('#acad-qat [data-acad-act="saveJson"]')
            dl = await d.value
        except Exception as e:
            print('      (no download: %s)' % str(e)[:80])
        body = None
        if dl:
            try:
                body = json.loads(pathlib.Path(await dl.path()).read_text(encoding='utf-8'))
            except Exception as e:
                print('      (download unreadable: %s)' % str(e)[:80])
        ck(dl is not None and dl.suggested_filename == 'Project1.acad3d.json',
           "the quick-access bar's Save downloads the project, named after it (%s)" % (dl.suggested_filename if dl else None))
        ck(body is not None and body.get('app') == 'acad3d-project' and len(body['data']['objs']) == 2,
           'and the file is a project file holding its two walls')

        # ---------------------------------------------------------------------------------------
        print('\n-- 5. Open opens a project in a tab of its own; it does not replace one')
        env = json.loads(await safe("()=>window.__a3dProjectEnvelope()"))
        env['data']['titleBlock']['project'] = ''
        payload = json.dumps(env).encode('utf-8')
        await page.click('#acad-doctabs [data-dt="start"]')
        await page.wait_for_timeout(250)
        st0 = await start_state()
        ck(st0 and st0['shown'] and st0['onTop'],
           'the Start tab shows the Start page on top of the drawing area, with projects still open behind it (%s)'
           % (st0 and {k: st0[k] for k in ('shown', 'onTop')}))
        n_dialogs = len(dialogs)
        chooser = None
        try:
            async with page.expect_file_chooser(timeout=3000) as fc:
                await page.click('#acad-start [data-st="open"]')
            chooser = await fc.value
            await chooser.set_files(files=[{'name': 'Bridge Deck.acad3d.json', 'mimeType': 'application/json', 'buffer': payload}])
        except Exception as e:
            print('      (file chooser failed: %s)' % str(e)[:100])
        await page.wait_for_timeout(700)
        tb = await tabs()
        st = await start_state()
        ck([x[1] for x in tb] == ['Start', 'Legacy Tower', 'Project1', 'Bridge Deck', '+'] and tb[3][2] is True,
           'the file opens as a new tab, named from the file because its title block had no name (%s)' % [x[1] for x in tb])
        ck((await objs()) == 2 and st and st['shown'] is False and len(dialogs) == n_dialogs,
           'with its two walls, the Start page gone, and no confirm() asked -- nothing was being replaced')
        await click_tab(p1)
        ck((await objs()) == 2, 'and Project1 is still there in its own tab, untouched')
        await clear_toast()
        try:
            async with page.expect_file_chooser(timeout=3000) as fc:
                await page.keyboard.press('Control+o')
            ch2 = await fc.value
            await ch2.set_files(files=[{'name': 'site.dxf', 'mimeType': 'application/dxf', 'buffer': b'0\nEOF\n'}])
        except Exception as e:
            print('      (Ctrl+O chooser failed: %s)' % str(e)[:100])
        await page.wait_for_timeout(500)
        tt = await toast()
        ck('not a project file' in tt and len(await tabs()) == 5 and (await objs()) == 2,
           'Ctrl+O is OPEN, and a DXF given to it is refused, not imported into the open project (%r)' % tt)
        bridge = tb[3][3] if len(tb) == 5 else None

        # ---------------------------------------------------------------------------------------
        print('\n-- 6. close, reopen from Start, and the history comes back with it')
        await page.click('#acad-doctabs [data-dtx="%s"]' % p1)
        await page.wait_for_timeout(500)
        tb = await tabs()
        ck([x[1] for x in tb] == ['Start', 'Legacy Tower', 'Bridge Deck', '+'] and (await active_id()) == bridge,
           "closing the active tab moves to its neighbour on the right (%s)" % [x[1] for x in tb])
        await one_place('after closing a tab')
        await page.click('#acad-doctabs [data-dt="start"]')
        await page.wait_for_timeout(300)
        st = await start_state()
        card = [c for c in (st['cards'] if st else []) if c['id'] == p1]
        ck(len(card) == 1 and 'closed' in card[0]['meta'] and card[0]['del'] is True and '2 objects' in card[0]['meta'],
           'the closed project waits on Start: 2 objects, closed, with a Delete button (%s)' % card)
        await page.click('#acad-start .st-card[data-doc="%s"] .st-name' % p1)
        await page.wait_for_timeout(500)
        tb = await tabs()
        ud = await safe("()=>window.__a3dDocs.undoDepth()")
        ck(tb[-2][1] == 'Project1' and tb[-2][2] is True and (await objs()) == 2 and ud and ud['undo'] == 2,
           'its card reopens it as the active tab, with its walls and its undo history (%s, %s)' % ([x[1] for x in tb], ud))

        # ---------------------------------------------------------------------------------------
        print('\n-- 7. failures say so and leave the project on screen whole')
        await page.click('#acad-doctabs [data-dtx="%s"]' % bridge)
        await page.wait_for_timeout(450)
        await safe("(id)=>localStorage.setItem('acad3dDocV1:'+id,'{\"objs\":\"damaged\"}')", bridge)
        await page.click('#acad-doctabs [data-dt="start"]')
        await page.wait_for_timeout(250)
        await clear_toast()
        await page.click('#acad-start .st-card[data-doc="%s"] .st-name' % bridge)
        await page.wait_for_timeout(500)
        tt = await toast()
        pl = await storage_places()
        ck('damaged' in tt and (await active_id()) == p1 and (await objs()) == 2 and pl and pl['slot'] == p1 and bridge in pl['keys'],
           'a damaged project says so, and Project1 stays on screen and in acad3dV1, the damaged one kept for inspection (%r)' % tt)
        await safe("(id)=>localStorage.setItem('acad3dDocV1:'+id,JSON.stringify({objs:[],titleBlock:{project:'Bridge Deck',client:'',drawnBy:'',checkedBy:''}}))", bridge)
        await page.click('#acad-doctabs [data-doc="%s"] .dt-name' % p1)
        await page.wait_for_timeout(300)
        n_docs = len(await docs())
        await safe("""()=>{window.__realSet=Storage.prototype.setItem;
            Storage.prototype.setItem=function(k,v){if(String(k).indexOf('acad3dDocV1:')===0){var e=new Error('full');e.name='QuotaExceededError';throw e;}
              return window.__realSet.call(this,k,v);};}""")
        await clear_toast()
        await page.click('#acad-doctabs [data-dt="new"]')
        await page.wait_for_timeout(500)
        tt = await toast()
        await safe("()=>{Storage.prototype.setItem=window.__realSet;}")
        ck('not enough browser storage' in tt and (await active_id()) == p1 and (await objs()) == 2 and len(await docs()) == n_docs,
           'a full store during a switch says so, and nothing moves: same project, same list (%r)' % tt)
        await safe("""()=>{Storage.prototype.setItem=function(k,v){if(k==='acad3dV1'){var e=new Error('full');e.name='QuotaExceededError';throw e;}
              return window.__realSet.call(this,k,v);};}""")
        await clear_toast()
        await safe("()=>{window.__a3dWall([[0,6],[3,6]],0.2,null,'center',false);}")
        await page.wait_for_timeout(600)
        tt = await toast()
        await safe("()=>{Storage.prototype.setItem=window.__realSet;}")
        ck('could not be saved' in tt,
           'an autosave that fails says so -- it went into an empty catch before (%r)' % tt)
        await clear_toast()
        await safe("()=>{window.__a3dWall([[0,8],[3,8]],0.2,null,'center',false);}")
        await page.wait_for_timeout(600)
        tt = await toast()
        ck('works again' in tt, 'and says so again when saving recovers (%r)' % tt)
        await page.click('#acad-qat [data-acad-act="undo"]')
        await page.click('#acad-qat [data-acad-act="undo"]')
        await page.wait_for_timeout(500)

        # ---------------------------------------------------------------------------------------
        print('\n-- 8. with every tab closed, Start is all there is, and it is seen')
        for d in await docs():
            if d['open']:
                await page.click('#acad-doctabs [data-dtx="%s"]' % d['id'])
                await page.wait_for_timeout(450)
        tb = await tabs()
        st = await start_state()
        ck([x[0] for x in tb] == ['start', 'new'] and tb[0][2] is True,
           'no project tabs, and the Start tab is active (%s)' % tb)
        ck(st and st['shown'] and st['onTop'] and st['overDock'],
           'the Start page is what is on top -- over the drawing area and over the dock (%s)' % st)
        # AMENDED FOR V119: the view menu is gone; the readout that names a project's view is the HUD now
        ck(st and st['wsHidden'] is True, 'and the HUD, which names the view of a project on screen, is under it')
        loaded = [d for d in await docs() if d['loaded']][0]
        n0, u0 = await objs(), await safe("()=>window.__a3dDocs.undoDepth().undo")
        await page.mouse.click(800, 600)
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(200)
        await clear_toast()
        await page.click('#acad-qat [data-acad-act="undo"]')
        await page.wait_for_timeout(250)
        tt = await toast()
        ck((await objs()) == n0 and (await safe("()=>window.__a3dDocs.undoDepth().undo")) == u0 and 'Open a project' in tt,
           'neither Ctrl+Z nor Undo reaches the project hidden behind Start; Undo says why (%r)' % tt)
        card = [c for c in st['cards'] if c['id'] == loaded['id']]
        ck(len(card) == 1 and 'last open' in card[0]['meta'] and card[0]['del'] is False,
           'the project still loaded behind Start is listed as last open and cannot be deleted from under itself (%s)' % card)
        await page.reload()
        await ready()
        tb = await tabs()
        st = await start_state()
        ck([x[0] for x in tb] == ['start', 'new'] and st and st['shown'] and st['onTop'] and len(st['cards']) == 4,
           'a reload comes back the same way: Start, no tabs, all four projects listed -- closing is not deleting (%s)'
           % (st and [c['name'] for c in st['cards']]))

        # ---------------------------------------------------------------------------------------
        print('\n-- 9. deleting a project asks first')
        answer['accept'] = False
        await page.click('#acad-start .st-card[data-doc="%s"] .st-del' % bridge)
        await page.wait_for_timeout(300)
        still = await safe("(id)=>localStorage.getItem('acad3dDocV1:'+id)!==null", bridge)
        ck(dialogs and 'Bridge Deck' in dialogs[-1] and still is True and any(d['id'] == bridge for d in await docs()),
           'Delete asks, naming the project, and Cancel keeps it (%s)' % (dialogs[-1:] if dialogs else None))
        answer['accept'] = True
        await page.click('#acad-start .st-card[data-doc="%s"] .st-del' % bridge)
        await page.wait_for_timeout(300)
        answer['accept'] = False
        gone = await safe("(id)=>localStorage.getItem('acad3dDocV1:'+id)===null", bridge)
        st = await start_state()
        ck(gone is True and not any(d['id'] == bridge for d in await docs()) and not any(c['id'] == bridge for c in st['cards']),
           'OK deletes it: its stored data, its list entry and its card')

        # ---------------------------------------------------------------------------------------
        print('\n-- 10. what boot finds: the last edit, and repairs for what a crash leaves')
        await page.click('#acad-start .st-card[data-doc="%s"] .st-name' % p1)
        await page.wait_for_timeout(700)
        cur = await active_id()
        await safe("()=>{window.__a3dWall([[0,10],[5,10]],0.2,null,'center',false);}")
        await page.reload()
        await ready()
        ck((await objs()) == 3 and (await active_id()) == cur,
           'a wall drawn and reloaded inside the autosave\'s 300 ms wait is still there -- it was lost every time before')
        await page.wait_for_timeout(500)
        await page.goto('file://' + str(BLANK))   # what a crash leaves, written while the app is closed
        await safe("""(cur)=>{localStorage.setItem('acad3dDocV1:'+cur,localStorage.getItem('acad3dV1'));
            localStorage.setItem('acad3dDocV1:doc-orphan-1',JSON.stringify({objs:[],titleBlock:{project:'Orphan Hall',client:'',drawnBy:'',checkedBy:''}}));
            var ix=JSON.parse(localStorage.getItem('acad3dDocsV1'));ix.docs.push({id:'doc-ghost-1',name:'Ghost',objs:0,saved:0});
            localStorage.setItem('acad3dDocsV1',JSON.stringify(ix));}""", cur)
        await page.goto('file://' + str(HTML))
        await ready()
        names = [d['name'] for d in await docs()]
        stale = await safe("(id)=>localStorage.getItem('acad3dDocV1:'+id)", cur)
        ck(stale is None and (await active_id()) == cur and (await objs()) == 3,
           'the copy an interrupted switch leaves is dropped at boot, and the project on screen is whole')
        ck('Orphan Hall' in names, 'a stored project the list lost is listed again (%s)' % names)
        ck('Ghost' not in names, 'and a list entry with nothing stored behind it is dropped (%s)' % names)

        ck(not errs, 'no page errors (%s)' % errs[:3])
        await browser.close()


asyncio.run(main())
