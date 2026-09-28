#!/usr/bin/env python3
"""bim_phase117_wire_shell_retired_browser_tests.py -- V117: the rest of the 2D wire shell is gone, and
the Delete key, which was riding on it, is the BIM engine's own.

  1. THE WIRE SHELL IS GONE. Its hooks are undefined, its dock, rail buttons and marquee are never in
     the document -- not at boot and not after the view changes that its MutationObserver used to
     answer -- and both of the shell's surviving scripts ran to the end without an exception.
  2. DELETE ERASES THE SELECTION, and Backspace with it -- one object, several at once, undone in
     one step. Asserted on the model: the ids are gone from it, then back.
  3. DELETE STAYS BEHIND THE ENGINE'S GATES. The old path ran after the engine's handler had
     returned, so it leaked past every gate; two leaks were measured on V116 and are driven here: the
     Start page and an open dialog. The others are driven because the move could break them: a field,
     a point being typed, a sheet, and Ctrl. And a DROPDOWN is a field: its plain keys step it -- on
     V116 ArrowDown on the wall's Type dropdown moved the wall a metre -- while Ctrl+Z stays the app's.
  4. THE SHELL THAT STAYS STILL WORKS: the view menu the same script builds switches the model view.
  5. STORED DATA IS KEPT. The whiteboard's blocks and dock state ('acadBlocksV1', 'acadDockV1') are
     not the app's to delete; they are byte-identical after a session and a reload.
     AMENDED FOR V121b: the owner has since made that call ("i want to clear them up"), and the app
     removes both at start with the rest of the old canvas's entries; this section now asserts that,
     and that the app's own saved model is untouched by it.
  6. No page errors.
"""
# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys, tempfile
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
BLANK = pathlib.Path(tempfile.mkdtemp(prefix='v117_')) / 'blank.html'
BLANK.write_text('<!doctype html><title>blank</title>', encoding='utf-8')

GONE_HOOKS = ['__ws3Del', '__wsState', '__wsPick', '__wsHitTest', '__ws2Marq', '__ws3Fixes', '__ws4Layers']
GONE_DOM = '#acad-dock,#acad-dockpanel,.acad-dkbtn,#ws2-marq,#selbox'
KEPT = {'acadBlocksV1': '[{"name":"KEEP-B","wires":[{"a":[0,0],"b":[1,0]}]}]',
        'acadDockV1': '{"open":"props","w":256,"note":"kept by V117"}'}


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


async def main():
    ck = Checks()
    ck('__acad3dV117' in HTML.read_text(encoding='utf-8'), 'the V117 marker is present')
    if not ck.bad:
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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))
        page.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        async def ready():
            try:
                await page.wait_for_function("()=>!!window.__a3dColumnAt&&!!window.__a3dSheetSpace&&"
                                             "!!document.querySelector('#acad-doctabs [data-dt=\"doc\"]')", timeout=20000)
            except Exception as e:
                print('      (the workspace did not come up: %s)' % str(e)[:100])
            await page.wait_for_timeout(500)

        async def ids():
            return (await safe("()=>window.__a3dState().objs.map(function(o){return o.id;})")) or []

        async def column(x):
            return await safe("(x)=>window.__a3dColumnAt([x,0],0,0.4,0.4,3)", x)

        async def select(*oid):
            await safe("(a)=>window.__a3dSelectFor(a)", list(oid))

        async def blur():
            await safe("()=>{if(document.activeElement&&document.activeElement.blur)document.activeElement.blur();}")

        async def press(key):
            await page.keyboard.press(key)
            await page.wait_for_timeout(200)

        async def gone_dom():
            return await safe("(q)=>document.querySelectorAll(q).length", GONE_DOM)

        # the stored whiteboard data is written while the app is closed, from a blank page on the
        # same file:// origin -- never from an init script, which on file:// cuts storage off
        await page.goto('file://' + str(BLANK))
        await safe("(kv)=>{localStorage.clear();Object.keys(kv).forEach(function(k){localStorage.setItem(k,kv[k]);});}", KEPT)
        await page.goto('file://' + str(HTML))
        await ready()
        await page.mouse.click(800, 450)
        boot = await safe("()=>[window.__a3dActiveView().kind,document.body.classList.contains('a3d-mode')]")

        # -------------------------------------------------------------------------------------------
        print('\n-- 1. the wire shell is gone')
        hooks = await safe("(names)=>names.filter(function(n){return typeof window[n]!=='undefined';})", GONE_HOOKS)
        ck(hooks == [], 'none of the wire shell\'s hooks is defined (%s)' % hooks)
        errv = await safe("()=>[typeof window.__wsErr,typeof window.__ws2Err,!!window.__a3dOn]")   # AMENDED FOR V120: the boot is what shows the last section ran
        ck(errv == ['undefined', 'undefined', True], 'both of the shell\'s scripts ran to the end without an exception (%s)' % errv)
        ck((await gone_dom()) == 0, 'no dock, dock panel, rail button, marquee or selection box is in the document at boot')
        await safe("()=>{window.__a3dSet3DView();}")
        await page.wait_for_timeout(300)
        await safe("()=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"assets\"]');b&&b.click();}")
        await page.wait_for_timeout(300)
        await safe("()=>{var b=document.querySelector('#a3d-rail .a3d-railbtn[data-tab=\"browser\"]');b&&b.click();}")
        await safe("()=>{window.__a3dSetPlanView();}")
        await page.wait_for_timeout(300)
        ck((await gone_dom()) == 0, 'and none after the view and the side panel change -- the changes the shell\'s observer answered')

        # -------------------------------------------------------------------------------------------
        print('\n-- 2. Delete erases the selection')
        c1 = await column(0)
        await select(c1)
        await blur()
        await press('Delete')
        ck(c1 not in await ids(), 'Delete erases the selected object from the model')
        c2 = await column(2)
        await select(c2)
        await blur()
        await press('Backspace')
        ck(c2 not in await ids(), 'Backspace, the delete key of a Mac keyboard, does too')
        await press('Control+z')
        ck(c2 in await ids(), 'and Ctrl+Z brings it back')
        a, b = await column(4), await column(6)
        await select(a, b)
        await blur()
        await press('Delete')
        now = await ids()
        ck(a not in now and b not in now, 'a selection of two is erased by one Delete')
        await press('Control+z')
        now = await ids()
        ck(a in now and b in now, 'and one Ctrl+Z brings both back')
        await safe("()=>window.__a3dSelectFor([])")
        n0 = len(await ids())
        await press('Delete')
        ck(len(await ids()) == n0, 'with nothing selected, Delete erases nothing (%d -> %d)' % (n0, len(await ids())))

        # -------------------------------------------------------------------------------------------
        print('\n-- 3. Delete stays behind the engine\'s gates')
        c3 = await column(8)
        await select(c3)
        await page.click('#acad-doctabs [data-dt="start"]')
        await page.wait_for_timeout(250)
        await blur()
        shown = await safe("()=>document.getElementById('acad-start').classList.contains('show')")
        await press('Delete')
        ck(shown and c3 in await ids(),
           'with the Start page showing, Delete does not reach the project behind it (V116 erased it)')
        await page.click('#acad-doctabs [data-dt="doc"]')
        await page.wait_for_timeout(300)
        await select(c3)
        await blur()
        await press('Delete')
        ck(c3 not in await ids(), 'back on the project, the same Delete erases it')

        c4 = await column(10)
        await select(c4)
        await safe("()=>window.__a3dOpenDlg('box')")
        hd = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');if(!d)return null;var r=d.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];}")
        if hd:
            await page.mouse.click(hd[0], hd[1])
            await page.wait_for_timeout(100)
        focus = await safe("()=>document.activeElement.tagName")
        await press('Backspace')
        ck(hd and focus == 'BODY' and c4 in await ids() and await safe("()=>!!document.querySelector('.a3d-dlg')"),
           'with a dialog open and the focus off its fields, Backspace leaves the object behind it (V116 erased it) (%s)' % focus)
        await press('Escape')
        await blur()
        await press('Delete')
        ck(c4 not in await ids(), 'with the dialog closed, Delete erases it')

        c5 = await column(12)
        await select(c5)
        await press('Control+k')
        await page.wait_for_timeout(250)
        await page.keyboard.type('ab')
        await press('Backspace')
        field = await safe("()=>{var i=document.querySelector('#a3d-cmdpal input');return i?[i.value,document.activeElement===i]:null;}")
        ck(field == ['a', True] and c5 in await ids(),
           'Backspace in a field edits the field and leaves the model alone (%s)' % field)
        await press('Escape')
        await blur()

        await select(c5)
        await press('Control+Delete')
        ck(c5 in await ids(), 'Ctrl+Delete is not Delete')

        await select(c5)
        await press('Control+k')
        await page.wait_for_timeout(250)
        await page.keyboard.type('LINE')
        await page.wait_for_timeout(150)
        await press('Enter')
        await page.wait_for_timeout(200)
        sk = await safe("()=>{var s=window.__a3dState();return [s.sk&&s.sk.tool,s.sel];}")
        await page.keyboard.type('5')
        await page.wait_for_timeout(100)
        t1 = await safe("()=>window.__a3dTyping()")
        await press('Backspace')
        t2 = await safe("()=>window.__a3dTyping()")
        ck(sk == ['line', c5] and t1 == {'active': True, 'buf': '5'} and t2 == {'active': False, 'buf': ''} and c5 in await ids(),
           'while a point is being typed, Backspace edits the number, with the object still selected and still there (%s %s %s)' % (sk, t1, t2))
        await press('Escape')

        sid = await safe("()=>window.__a3dAddSheet('A117','Delete gate','ANSI-B-L')")
        await select(c5)
        await safe("(id)=>window.__a3dOpenSheetView(id)", sid)
        await page.wait_for_timeout(300)
        await blur()
        on = await safe("()=>[window.__a3dSheetIsOpen(),window.__a3dSheetSelectedVp()]")
        await press('Delete')
        ck(on == [True, None] and c5 in await ids(), 'on a sheet, Delete does not reach the model behind the paper (%s)' % on)
        await safe("()=>window.__a3dCloseSheetView()")
        await page.wait_for_timeout(300)
        await select(c5)
        await blur()
        await press('Delete')
        ck(c5 not in await ids(), 'and on the Model tab it erases the object')

        # a dropdown is a field too: its plain keys are its own, its Ctrl shortcuts are the app's
        w = await safe("()=>window.__a3dWall([[0,4],[6,4]],0.3,3,'center',false)")

        async def wall():
            return await safe("(id)=>{var o=window.__a3dState().objs.filter(function(x){return x.id===id;})[0];"
                              "return o?[o.pos,o.bim&&o.bim.typeId]:null;}", w)

        async def focus_type():
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", w)
            await page.wait_for_timeout(150)
            return await safe("()=>{var s=document.querySelector('#a3d-propsbody select[data-propf=\"walltype\"]');"
                              "if(!s)return null;s.focus();return [document.activeElement===s,s.value,s.options[1]&&s.options[1].value];}")

        w0 = await wall()
        fs = await focus_type()
        await press('ArrowDown')
        w1 = await wall()
        ck(fs and fs[0] and w0 and w1 and w1[0] == w0[0] and w1[1] == fs[2] and w1[1] != w0[1],
           'with the wall\'s Type dropdown focused, ArrowDown steps the dropdown -- the wall takes the next type '
           'and does not move (V116 moved it a metre) (%s -> %s)' % (w0, w1))
        fs2 = await focus_type()
        await press('Delete')
        ck(fs2 and fs2[0] and w in await ids(), 'and Delete there does not erase the wall')
        fs3 = await focus_type()
        await press('Control+z')
        w2 = await wall()
        ck(fs3 and fs3[0] and w2 and w0 and w2[1] == w0[1] and w2[0] == w0[0],
           'but Ctrl+Z there is still the app\'s: the type change is undone (%s)' % (w2,))
        await blur()

        # -------------------------------------------------------------------------------------------
        print('\n-- 4. the shell that stays still works')

        # AMENDED FOR V119: the view menu this section drove was the owner's to remove, and V119 removed it.
        # What the same script still does is boot the app into the BIM shell, in the plan view.
        ck(boot == ['plan', True], 'the script that is left booted the app into the BIM shell, in the plan view (%s)' % boot)

        # -------------------------------------------------------------------------------------------
        print('\n-- 5. stored data: the whiteboard\'s is cleared at the owner\'s request (V121b), the app\'s is kept')
        await page.wait_for_timeout(1200)   # past the save debounce
        await page.reload()
        await ready()
        got = await safe("(ks)=>ks.map(function(k){return localStorage.getItem(k);})", list(KEPT))
        own = await safe("()=>localStorage.getItem('acad3dV1')!==null")
        ck(got == [None, None] and own is True,
           'the whiteboard\'s stored blocks and dock state are gone after a start, and the app\'s own model is still stored (%s, %s)' % (got, own))

        # -------------------------------------------------------------------------------------------
        print('\n-- 6. errors')
        ck(errs == [], 'no page errors (%s)' % errs[:3])
        await browser.close()


asyncio.run(main())
