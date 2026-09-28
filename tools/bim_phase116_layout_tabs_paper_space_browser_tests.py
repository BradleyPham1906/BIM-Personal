#!/usr/bin/env python3
"""bim_phase116_layout_tabs_paper_space_browser_tests.py -- V116: AutoCAD's Model and layout tabs, and
paper space with model space through a viewport, over the BIM engine's sheets.

  1. THE CANVAS-ERA STRIP IS GONE. It kept its own "layouts" per whiteboard drawing and was never on
     screen; its element, its paper overlay and its storage writes are gone.
  2. THE TABS ARE THE SHEETS. Model, one tab per sheet in the project's own order and labels, and +.
     + adds a landscape sheet with a number no sheet has, and opens it.
  3. EVERY WAY OFF A SHEET RETURNS TO THE MODEL VIEW IT CAME FROM -- the Model tab, Close, deleting
     the sheet, undoing its creation -- with the camera exactly as it was. Before V116 three of these
     left the view state saying Sheet over a model on screen.
  4. EVERY WAY ONTO A SHEET IS A VIEW -- the tab, the New Sheet dialog, the ribbon's Sheet command,
     the test hook. Two of these used to open the paper and leave the view state saying Plan.
  5. RENAME AND THE TAB MENU work, are undoable, and one label follows everywhere.
  6. MODEL SPACE THROUGH A VIEWPORT. Double-click in, drag to pan, wheel through standard scales,
     Escape / double-click outside / PAPER to come back. Asserted as geometry: the model point under
     the cursor stays under it through a zoom, and under the pointer through a pan; a fitted viewport
     keeps its centre when it takes a fixed scale; the pan reaches the SVG a sheet prints from.
  7. NOTHING REACHES THE MODEL BEHIND THE PAPER: keys, commands and the tool dock's acts.
  8. EACH PROJECT KEEPS ITS OWN MODEL VIEW behind its sheets.
  9. EXPORTS ARE THE PAPER, without the working highlight.
"""
import asyncio, io, json, pathlib, re, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

STD = [1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 1250, 2000, 2500, 5000]


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


async def main():
    ck = Checks()
    ck('__acad3dV116' in HTML.read_text(encoding='utf-8'), 'the V116 marker is present')
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
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950}, accept_downloads=True)
        page = await ctx.new_page()
        page.set_default_timeout(6000)
        errs, dialogs = [], []
        answer = {'accept': False}
        page.on('pageerror', lambda e: errs.append(str(e)[:160]))

        async def on_dialog(d):
            dialogs.append(d.message)
            await (d.accept() if answer['accept'] else d.dismiss())
        page.on('dialog', lambda d: asyncio.ensure_future(on_dialog(d)))
        ev = page.evaluate

        async def safe(js, arg=None):
            try:
                return await (ev(js, arg) if arg is not None else ev(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:160])
                return None

        async def ready():
            try:
                await page.wait_for_function("()=>!!window.__a3dSheetSpace&&!!document.querySelector('#a3d-laytabs [data-lt]')", timeout=20000)
            except Exception as e:
                print('      (the workspace did not come up: %s)' % str(e)[:100])
            await page.wait_for_timeout(500)

        async def tabs():
            return (await safe("()=>Array.prototype.map.call(document.querySelectorAll('#a3d-laytabs [data-lt]'),function(b){"
                               "return [b.getAttribute('data-lt'),b.textContent,b.classList.contains('on'),b.getAttribute('data-ltsheet')];})")) or []

        async def space():
            return (await safe("()=>window.__a3dSheetSpace()")) or {}

        async def sheets():
            return (await safe("()=>window.__a3dSheets()")) or []

        async def cam():
            return await safe("()=>window.__a3dState().cam")

        def same_cam(a, b):
            return bool(a and b) and all(near(a[k], b[k], 1e-9) for k in ('yaw', 'pitch', 'dist', 'tx', 'ty', 'tz'))

        async def toast():
            return (await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}")) or ''

        async def clear_toast():
            await safe("()=>{var t=document.getElementById('a3d-toast');if(t)t.textContent='';}")

        async def menu_items():
            return await safe("()=>{var m=document.getElementById('a3d-ltmenu');return m?Array.prototype.map.call(m.querySelectorAll('button'),function(b){return b.textContent;}):null;}")

        # A pointer lands on whole CSS pixels, so every position is rounded to one and the millimetres
        # are read back from that pixel the way the app reads them -- not from the millimetres asked for.
        async def geom():
            return await safe("""()=>{var c=document.getElementById('a3d-sheetcanvas');var r=c.getBoundingClientRect();
                return {x:r.x,y:r.y,k:c.width/r.width,ky:c.height/r.height};}""")

        async def mm_to_px(mx, my):
            g = await geom()
            return round(g['x'] + mx * 3 / g['k']), round(g['y'] + my * 3 / g['ky']), g['k']

        async def px_to_mm(px, py):
            g = await geom()
            return (px - g['x']) * g['k'] / 3, (py - g['y']) * g['ky'] / 3

        async def label_everywhere():
            # AMENDED FOR V119: the view dropdown whose label was the third place is gone; the HUD carries its name
            return await safe("""()=>{
                return {header:(document.getElementById('a3d-sheetnum')||{}).textContent,hud:(document.getElementById('a3d-view')||{}).textContent};}""")

        await page.goto('file://' + str(HTML))
        await ready()
        await page.mouse.click(800, 450)

        # -------------------------------------------------------------------------------------------
        print('\n-- 1. the canvas-era strip is gone')
        gone = await safe("()=>[!!document.getElementById('acad-mltabs'),!!document.getElementById('acad-layout'),"
                          "localStorage.getItem('acadLayoutsV1')===null,typeof window.__ws2Space]")
        ck(gone == [False, False, True, 'undefined'],
           'no canvas-era strip, no paper overlay, nothing written to its storage key, no hook (%s)' % gone)
        tb = await tabs()
        ck([x[0] for x in tb] == ['model', 'new'] and tb[0][2] is True,
           'with no sheets the tabs are Model, active, and + (%s)' % tb)

        # -------------------------------------------------------------------------------------------
        print('\n-- 2. + adds a landscape sheet with a number no sheet has, and opens it')
        await safe("()=>{window.__a3dWall([[0,0],[8,0]],0.3,null,'center',false);window.__a3dWall([[8,0],[8,6]],0.3,null,'center',false);"
                   "window.__a3dWall([[8,6],[0,6]],0.3,null,'center',false);window.__a3dWall([[0,6],[0,0]],0.3,null,'center',false);}")
        wall = await safe("()=>window.__a3dObjects()[0].id")
        await safe("()=>{window.__a3dSetPlanView();}")
        await page.wait_for_timeout(300)
        cam0 = await cam()
        await page.click('#a3d-laytabs [data-lt="new"]')
        await page.wait_for_timeout(400)
        tb = await tabs()
        sp = await space()
        sh = await sheets()
        ck([x[0] for x in tb] == ['model', 'sheet', 'new'] and tb[1][1] == 'A101 - Untitled' and tb[1][2] and not tb[0][2],
           'a sheet tab, A101 - Untitled, is added and active (%s)' % [x[1] for x in tb])
        ck(sp.get('onSheet') and sp.get('view') == 'sheet' and sp.get('viewName') == 'A101 - Untitled',
           'and the sheet is the view on screen, by the view state and not only by the paper (%s)' % sp)
        ck(len(sh) == 1 and sh[0]['w'] > sh[0]['h'], 'a drawing sheet is landscape (%s x %s mm)' % (sh[0]['w'], sh[0]['h']) if sh else 'no sheet')
        lab = await label_everywhere()
        ck(lab and lab['header'] == 'A101 - Untitled' and lab['hud'] == 'A101 - Untitled',
           'the sheet toolbar and the HUD both name it (%s)' % lab)
        a101 = sp.get('sheet')
        await page.click('#a3d-laytabs [data-lt="new"]')
        await page.wait_for_timeout(300)
        answer['accept'] = True
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % a101, button='right')
        await page.click('#a3d-ltmenu [data-ltm="del"]')
        await page.wait_for_timeout(300)
        answer['accept'] = False
        await page.click('#a3d-laytabs [data-lt="new"]')
        await page.wait_for_timeout(300)
        nums = [s['number'] for s in await sheets()]
        ck(nums == ['A102', 'A103'], 'after deleting A101, + makes A103 -- it used to make A102 again (%s)' % nums)
        tb = await tabs()
        ck([x[1] for x in tb[1:-1]] == [s['number'] + ' - ' + s['name'] for s in await sheets()],
           'the tabs are the sheets, in their order and with their labels (%s)' % [x[1] for x in tb])

        # -------------------------------------------------------------------------------------------
        print('\n-- 3. every way off a sheet goes back to the model view it came from')
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(300)
        sp = await space()
        ck(not sp.get('onSheet') and sp.get('view') == 'plan' and same_cam(cam0, await cam()),
           'the Model tab: plan again, the paper gone, the camera exactly as it was (%s)' % sp.get('view'))
        a103 = (await sheets())[1]['id']
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % a103)
        await page.wait_for_timeout(250)
        await page.click('#a3d-sheetclose')
        await page.wait_for_timeout(250)
        sp = await space()
        ck(not sp.get('onSheet') and sp.get('view') == 'plan' and same_cam(cam0, await cam()),
           "the sheet toolbar's Close: the same -- it used to leave the view state saying Sheet (%s)" % sp.get('view'))
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % a103)
        await page.wait_for_timeout(250)
        answer['accept'] = True
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % a103, button='right')
        await page.click('#a3d-ltmenu [data-ltm="del"]')
        await page.wait_for_timeout(300)
        answer['accept'] = False
        sp = await space()
        ck(not sp.get('onSheet') and sp.get('view') == 'plan' and len(await sheets()) == 1,
           'deleting the sheet on screen: back to the model view (%s)' % sp.get('view'))
        await page.click('#a3d-laytabs [data-lt="new"]')
        await page.wait_for_timeout(300)
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(400)
        sp = await space()
        ck(not sp.get('onSheet') and sp.get('view') == 'plan' and len(await sheets()) == 1 and len(await tabs()) == 3,
           'undoing the sheet on screen: its tab goes and the model comes back (%s, %d sheets)' % (sp.get('view'), len(await sheets())))

        await safe("()=>{window.__a3dSet3DView();}")
        await page.wait_for_timeout(400)
        iso = await cam()
        await page.mouse.move(430, 160)
        await page.mouse.down()
        await page.mouse.move(520, 200, steps=6)
        await page.mouse.up()
        await page.wait_for_timeout(250)
        cam3 = await cam()
        a102 = (await sheets())[0]['id']
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % a102)
        await page.wait_for_timeout(250)
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(300)
        sp = await space()
        ck(iso and cam3 and not near(iso['yaw'], cam3['yaw'], 1e-3) and sp.get('view') == '3d' and same_cam(cam3, await cam()),
           'from an orbited 3D view, the Model tab brings the orbit back -- not the iso preset the view would reset to (%s)' % sp.get('view'))
        await safe("()=>{window.__a3dSetPlanView();}")
        await page.wait_for_timeout(250)

        # -------------------------------------------------------------------------------------------
        print('\n-- 4. every way onto a sheet is a view')
        await page.click('#a3d-sheetadd')
        await page.wait_for_timeout(250)
        await safe("()=>{var d=document.querySelector('.a3d-dlg');d.querySelector('[data-a3dp=\"num\"]').value='S-201';"
                   "d.querySelector('[data-a3dp=\"name\"]').value='Sections';d.querySelector('[data-a3dlg=\"ok\"]').click();}")
        await page.wait_for_timeout(300)
        sp = await space()
        s201 = [s['id'] for s in await sheets() if s['number'] == 'S-201']
        ck(s201 and sp.get('view') == 'sheet' and sp.get('viewId') == s201[0] and sp.get('viewName') == 'S-201 - Sections',
           'the New Sheet dialog opens its sheet as the view -- it used to leave the view state saying Plan (%s)' % sp.get('view'))
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(250)
        await safe("()=>{var b=document.createElement('button');b.setAttribute('data-a3dr','bim:sheet');document.body.appendChild(b);b.click();b.remove();}")
        await page.wait_for_timeout(250)
        sp = await space()
        ck(sp.get('onSheet') and sp.get('view') == 'sheet', "the ribbon's Sheet command, likewise (%s)" % sp.get('view'))
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(250)
        await safe("(id)=>window.__a3dOpenSheetView(id)", s201[0] if s201 else '')
        sp = await space()
        ck(sp.get('onSheet') and sp.get('view') == 'sheet', 'and the test hook, which went around the view path too (%s)' % sp.get('view'))

        # -------------------------------------------------------------------------------------------
        print('\n-- 5. rename by double-click, and the tab menu')
        await page.dblclick('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(150)
        await page.keyboard.press('Control+a')
        await page.keyboard.type('Wall Sections')
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(300)
        nm = [s['name'] for s in await sheets() if s['id'] == s201[0]]
        tb = await tabs()
        lab = await label_everywhere()
        ck(nm == ['Wall Sections'] and any(x[1] == 'S-201 - Wall Sections' and x[2] for x in tb) and lab and
           lab['header'] == 'S-201 - Wall Sections' and lab['hud'] == 'S-201 - Wall Sections',
           'double-click renames it, and the tab, sheet toolbar and HUD all follow (%s / %s)' % (nm, lab))
        await page.dblclick('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(150)
        await page.keyboard.type('Scrap')
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)
        nm = [s['name'] for s in await sheets() if s['id'] == s201[0]]
        ck(nm == ['Wall Sections'] and (await space()).get('onSheet'), 'Escape cancels a rename and nothing else (%s)' % nm)
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(300)
        nm = [s['name'] for s in await sheets() if s['id'] == s201[0]]
        ck(nm == ['Sections'], 'a rename is one undo step (%s)' % nm)
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0], button='right')
        items = await menu_items()
        # AMENDED FOR V122: the tab and the Presentation panel's page read one menu, which moves a sheet
        # in the set -- this tab is the last of two, so it moves left only
        ck(items == ['New sheet', 'Rename', 'Delete', 'Move left', 'Sheet setup…', 'Plot…'],
           "a sheet tab's menu offers what AutoCAD's does that this app really does (%s)" % items)
        answer['accept'] = False
        n_dialogs = len(dialogs)
        await page.click('#a3d-ltmenu [data-ltm="del"]')
        await page.wait_for_timeout(250)
        ck(len(dialogs) == n_dialogs + 1 and 'S-201 - Sections' in dialogs[-1] and len(await sheets()) == 2,
           'Delete asks, naming the sheet, and Cancel keeps it (%s)' % (dialogs[-1:] if dialogs else None))
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0], button='right')
        await page.click('#a3d-ltmenu [data-ltm="setup"]')
        await page.wait_for_timeout(250)
        hd = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');return d?d.textContent:null;}")
        ud0 = await safe("()=>window.__a3dDocs.undoDepth().undo")
        await safe("""()=>{var d=document.querySelector('.a3d-dlg');d.querySelector('[data-a3dp="name"]').value='Changed';
            var s=d.querySelector('[data-a3dp="size"]');s.value='Custom';s.dispatchEvent(new Event('change'));
            d.querySelector('[data-a3dp="cw"]').value='5';d.querySelector('[data-a3dlg="ok"]').click();}""")
        await page.wait_for_timeout(200)
        err = await safe("()=>{var e=document.getElementById('a3d-dlgerr');return e?e.textContent:null;}")
        nm = [s['name'] for s in await sheets() if s['id'] == s201[0]]
        ud1 = await safe("()=>window.__a3dDocs.undoDepth().undo")
        ck(hd == 'Sheet Setup' and err and '10mm' in err and nm == ['Sections'] and ud0 == ud1,
           'Sheet setup from the menu; a bad custom size is refused with nothing changed and no undo step spent (%s, %s)' % (err, nm))
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg=\"cancel\"]');if(b)b.click();}")
        await page.click('#a3d-laytabs [data-lt="model"]', button='right')
        ck((await menu_items()) == ['New sheet'], "the Model tab's menu has only New sheet")
        await page.keyboard.press('Escape')
        await page.mouse.click(700, 300)

        # -------------------------------------------------------------------------------------------
        print('\n-- 6. model space through a viewport')
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(250)
        lvl = await safe("()=>window.__a3dActiveLevel().id")
        vp = await safe("(a)=>window.__a3dAddViewport(a[0],'plan',a[1],'fit')", [s201[0], lvl])
        # a schedule viewport beside it, clear of the plan viewport
        sch = await safe("""(a)=>{var o=window.__a3dSheetSourceOptions().filter(function(x){return x.kind==='schedule';})[0];
            var id=window.__a3dAddViewport(a[0],'schedule',o.refId,'fit');window.__a3dSetViewportRect(a[0],id,160,20,100,60);return id;}""", [s201[0]])
        await page.wait_for_timeout(200)
        vcx, vcy, s = await mm_to_px(20 + 60, 20 + 45)
        fitcam = await safe("(a)=>window.__a3dSheetVpCamera(a[0],a[1],1)", [s201[0], vp])
        await page.mouse.dblclick(vcx, vcy)
        await page.wait_for_timeout(250)
        sp = await space()
        btn = await safe("()=>{var b=document.getElementById('a3d-stspace');return [b.textContent,getComputedStyle(b).display!=='none'];}")
        hint = await safe("()=>document.getElementById('a3d-sthint').textContent")
        ck(sp.get('activeVp') == vp and btn == ['MODEL', True] and 'Model space' in (hint or ''),
           'double-click a viewport: model space in it, the status bar says MODEL (%s, %s)' % (sp.get('activeVp') == vp, btn))
        await page.mouse.move(vcx, vcy)
        await page.mouse.wheel(0, 120)
        await page.wait_for_timeout(250)
        sp = await space()
        rcam = await safe("(a)=>window.__a3dSheetVpCamera(a[0],a[1],1)", [s201[0], vp])
        d0 = sp.get('vp', {}).get('scaleDenom')
        fit_denom = 1000.0 / (1.2 * 90 / fitcam['dist']) if fitcam else None
        conv = STD[STD.index(d0) - 1] if d0 in STD and STD.index(d0) > 0 else None
        m0x, m0y = await px_to_mm(vcx, vcy)
        o0x, o0y = m0x - (20 + 60), m0y - (20 + 45)
        pv = sp.get('vp', {}).get('pan') or [0, 0]
        pconv = [pv[0] - o0x * ((conv or 0) - (d0 or 0)) / 1000, pv[1] + o0y * ((conv or 0) - (d0 or 0)) / 1000]
        ccam = await safe("""(a)=>{var s=window.__a3dSheets().filter(function(x){return x.id===a[0];})[0];
            var v=s.viewports.filter(function(x){return x.id===a[1];})[0];var src=window.__a3dResolveViewportSource(v);
            return window.__a3dSheetSolveCamera(src,120,90,1,'ratio',a[2],a[3]);}""", [s201[0], vp, conv, pconv])
        ck(sp.get('vp', {}).get('scaleMode') == 'ratio' and conv and fit_denom and conv >= fit_denom and
           STD[STD.index(conv) - 1] < fit_denom and ccam and near(fitcam['tx'], ccam['tx'], 1e-9) and near(fitcam['tz'], ccam['tz'], 1e-9),
           'a fitted viewport takes the smallest standard scale that still shows what the fit showed, at the fit\'s centre, '
           'before the wheel steps out from it (fit 1:%.1f -> 1:%s -> 1:%s)' % (fit_denom or 0, conv, d0))
        pan1 = sp['vp']['pan']
        cx2, cy2, s = await mm_to_px(20 + 90, 20 + 30)       # about 30 mm right and 15 mm up of the centre
        await page.mouse.move(cx2, cy2)
        await page.mouse.wheel(0, -120)
        await page.wait_for_timeout(250)
        v2 = (await space()).get('vp', {})
        mx2, my2 = await px_to_mm(cx2, cy2)
        ox, oy = mx2 - (20 + 60), my2 - (20 + 45)
        d1, d2, pan2 = d0, v2.get('scaleDenom'), v2.get('pan')
        ck(d2 == STD[STD.index(d1) - 1], 'the wheel steps to the next standard scale (1:%s -> 1:%s)' % (d1, d2))
        ck(pan2 and near(pan1[0] + ox * d1 / 1000, pan2[0] + ox * d2 / 1000, 1e-6) and near(pan1[1] - oy * d1 / 1000, pan2[1] - oy * d2 / 1000, 1e-6),
           'and the model point under the cursor stays under the cursor (%s -> %s)' % (pan1, pan2))
        svg_before = await safe("(a)=>window.__a3dBuildPlanViewportSVG(a[0],a[1],'technical').svg", [s201[0], vp])
        ud0 = await safe("()=>window.__a3dDocs.undoDepth().undo")
        sx, sy, k = await mm_to_px(20 + 50, 20 + 40)
        ex, ey = sx + round(12 * 3 / k), sy + round(8 * 3 / k)
        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(ex, ey, steps=6)
        await page.mouse.up()
        await page.wait_for_timeout(250)
        v3 = (await space()).get('vp', {})
        pan3 = v3.get('pan')
        smm, emm = await px_to_mm(sx, sy), await px_to_mm(ex, ey)
        ddx, ddy = emm[0] - smm[0], emm[1] - smm[1]
        ck(pan3 and near(pan3[0], pan2[0] - ddx * d2 / 1000, 1e-9) and near(pan3[1], pan2[1] + ddy * d2 / 1000, 1e-9),
           'a drag pans: the model point under the pointer stays under it (%s -> %s)' % (pan2, pan3))
        ud1 = await safe("()=>window.__a3dDocs.undoDepth().undo")
        ck(ud1 == ud0 + 1, 'one drag is one undo step (%s -> %s)' % (ud0, ud1))
        svg_after = await safe("(a)=>window.__a3dBuildPlanViewportSVG(a[0],a[1],'technical').svg", [s201[0], vp])
        m0 = re.search(r'd="M([-\d.]+),([-\d.]+)', svg_before or '')
        m1 = re.search(r'd="M([-\d.]+),([-\d.]+)', svg_after or '')
        ck(m0 and m1 and near(float(m1.group(1)) - float(m0.group(1)), ddx, 0.002) and near(float(m1.group(2)) - float(m0.group(2)), ddy, 0.002),
           'and the pan reaches the SVG the sheet prints from: the drawing moved exactly as far as the pointer (%.3f, %.3f mm; %s -> %s)'
           % (ddx, ddy, m0 and m0.groups(), m1 and m1.groups()))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        sp = await space()
        btn = await safe("()=>document.getElementById('a3d-stspace').textContent")
        ck(sp.get('activeVp') is None and sp.get('onSheet') and btn == 'PAPER', 'Escape: paper space, on the same sheet (%s)' % btn)
        await page.click('#a3d-stspace')
        await page.wait_for_timeout(200)
        ck((await space()).get('activeVp') == vp, "the status bar's PAPER button goes into the sheet's model viewport")
        px, py, s = await mm_to_px(300, 200)
        await page.mouse.dblclick(px, py)
        await page.wait_for_timeout(200)
        ck((await space()).get('activeVp') is None, 'double-click on the paper outside the viewport: paper space again')
        scx, scy, s = await mm_to_px(160 + 50, 20 + 30)
        await page.mouse.dblclick(scx, scy)
        await page.wait_for_timeout(250)
        hd = await safe("()=>{var d=document.querySelector('.a3d-dlg .a3d-dlghd');return d?d.textContent:null;}")
        ck(sch and (await space()).get('activeVp') is None and hd and hd.startswith('Viewport'),
           'a schedule has no model to work in: its double-click opens its properties (%s)' % hd)
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg=\"cancel\"]');if(b)b.click();}")
        await page.wait_for_timeout(150)
        await page.mouse.click(vcx, vcy, button='right')
        await page.wait_for_timeout(150)
        items = await menu_items()
        ck(items == ['Work in this viewport', 'Viewport properties\u2026', 'Delete viewport'],
           "a viewport's right-click menu: work in it, its properties, delete it (%s)" % items)
        await page.click('#a3d-ltmenu [data-ltm="props"]')
        await page.wait_for_timeout(200)
        opts = await safe("()=>Array.prototype.map.call(document.querySelectorAll('.a3d-dlg [data-a3dp=\"scale\"] option'),function(o){return o.textContent;})")
        ck(opts and '1:1000' in opts and '1:2500' in opts and '1:25' in opts,
           'its scales run from detail to site -- the list used to stop at 1:500 (%s)' % (opts and len(opts)))
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg=\"cancel\"]');if(b)b.click();}")
        cvp = await safe("""(a)=>{var id=window.__a3dAddViewport(a[0],'plan',a[1],'ratio',300);window.__a3dSetViewportRect(a[0],id,160,90,100,60);return id;}""", [s201[0], lvl])
        await page.wait_for_timeout(200)
        cx3, cy3, k = await mm_to_px(160 + 50, 90 + 30)
        await page.mouse.click(cx3, cy3, button='right')
        await page.click('#a3d-ltmenu [data-ltm="props"]')
        await page.wait_for_timeout(200)
        selopt = await safe("()=>{var s=document.querySelector('.a3d-dlg [data-a3dp=\"scale\"]');return s?s.options[s.selectedIndex].textContent:null;}")
        await safe("()=>{var b=document.querySelector('.a3d-dlg [data-a3dlg=\"ok\"]');if(b)b.click();}")
        await page.wait_for_timeout(200)
        kept = await safe("""(a)=>window.__a3dSheets().filter(function(x){return x.id===a[0];})[0].viewports.filter(function(v){return v.id===a[1];})[0].scaleDenom""", [s201[0], cvp])
        ck(selopt == '1:300' and kept == 300,
           'a scale not in the list is shown as it is, and OK keeps it -- OK used to set the first scale listed (%s, 1:%s)' % (selopt, kept))
        await safe("(a)=>window.__a3dDeleteViewport(a[0],a[1])", [s201[0], cvp])
        await page.wait_for_timeout(150)
        # a fixed scale opens on the model: through + Viewport, and through Properties from Fit
        fit_vs_ratio = """(a)=>{var s=window.__a3dSheets().filter(function(x){return x.id===a[0];})[0];
            var v=s.viewports.filter(function(x){return x.id===a[1];})[0];var src=window.__a3dResolveViewportSource(v);
            var f=window.__a3dSheetSolveCamera(src,v.w,v.h,1,'fit',v.scaleDenom),r=window.__a3dSheetVpCamera(a[0],a[1],1);
            return {mode:v.scaleMode,denom:v.scaleDenom,ft:[f.tx,f.tz],rt:[r.tx,r.tz]};}"""
        await page.click('#a3d-sheetaddvp')
        await page.wait_for_timeout(200)
        await safe("()=>{document.querySelector('.a3d-dlg [data-a3dlg=\"ok\"]').click();}")
        await page.wait_for_timeout(250)
        avp = await safe("(id)=>{var s=window.__a3dSheets().filter(function(x){return x.id===id;})[0];return s.viewports[s.viewports.length-1].id;}", s201[0])
        fr = await safe(fit_vs_ratio, [s201[0], avp])
        ck(fr and fr['mode'] == 'ratio' and fr['denom'] == 100 and near(fr['ft'][0], fr['rt'][0], 1e-9) and near(fr['ft'][1], fr['rt'][1], 1e-9),
           'a viewport added at 1:100 opens on the model, where a fit would centre it -- it used to look at the model origin (%s)' % fr)
        await safe("(a)=>window.__a3dDeleteViewport(a[0],a[1])", [s201[0], avp])
        fvp = await safe("""(a)=>{var id=window.__a3dAddViewport(a[0],'plan',a[1],'fit');window.__a3dSetViewportRect(a[0],id,280,110,100,70);return id;}""", [s201[0], lvl])
        await page.wait_for_timeout(200)
        fx, fy, k = await mm_to_px(280 + 50, 110 + 35)
        await page.mouse.click(fx, fy, button='right')
        await page.click('#a3d-ltmenu [data-ltm="props"]')
        await page.wait_for_timeout(200)
        await safe("()=>{var d=document.querySelector('.a3d-dlg');d.querySelector('[data-a3dp=\"scale\"]').value='200';d.querySelector('[data-a3dlg=\"ok\"]').click();}")
        await page.wait_for_timeout(250)
        fr = await safe(fit_vs_ratio, [s201[0], fvp])
        ck(fr and fr['mode'] == 'ratio' and fr['denom'] == 200 and near(fr['ft'][0], fr['rt'][0], 1e-9) and near(fr['ft'][1], fr['rt'][1], 1e-9),
           'a fitted viewport set to 1:200 in its properties keeps looking where the fit looked (%s)' % fr)
        await safe("(a)=>window.__a3dDeleteViewport(a[0],a[1])", [s201[0], fvp])
        await page.wait_for_timeout(150)

        # -------------------------------------------------------------------------------------------
        print('\n-- 7. nothing reaches the model behind the paper')
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(200)
        await safe("(id)=>window.__a3dSelectFor([id])", wall)
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(250)
        n0 = await safe("()=>window.__a3dObjects().length")
        await page.mouse.click(1400, 300)
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(200)
        ck((await safe("()=>window.__a3dObjects().length")) == n0,
           'Delete on a sheet does not delete the wall still selected in the model behind it (%s objects)' % n0)
        vx, vy, s = await mm_to_px(20 + 20, 20 + 20)
        await page.mouse.click(vx, vy)
        await page.wait_for_timeout(150)
        sel = (await space()).get('selVp')
        nvp = await safe("(id)=>window.__a3dSheets().filter(function(x){return x.id===id;})[0].viewports.length", s201[0])
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(200)
        nvp2 = await safe("(id)=>window.__a3dSheets().filter(function(x){return x.id===id;})[0].viewports.length", s201[0])
        ck(sel == vp and nvp2 == nvp - 1, 'but it deletes the viewport selected on the paper (%s -> %s)' % (nvp, nvp2))
        await page.keyboard.press('Control+z')
        await page.wait_for_timeout(250)
        nvp3 = await safe("(id)=>window.__a3dSheets().filter(function(x){return x.id===id;})[0].viewports.length", s201[0])
        ck(nvp3 == nvp, 'and Ctrl+Z on the sheet brings it back (%s)' % nvp3)
        await clear_toast()
        ran = await safe("()=>window.__a3dRunCmd('wall')")
        sk = await safe("()=>window.__a3dState().sk")
        tt = await toast()
        ck(ran is False and sk is None and 'Model tab' in tt, 'a model command on a sheet is refused and says where it works (%r)' % tt)
        await clear_toast()
        await safe("()=>{var b=document.createElement('button');b.setAttribute('data-a3dr','bim:wall');document.body.appendChild(b);b.click();b.remove();}")
        await page.wait_for_timeout(150)
        ck((await safe("()=>window.__a3dState().sk")) is None and 'Model tab' in (await toast()),
           'so is a tool from the ribbon or the dock')
        vis = await safe("""()=>{function v(s){var e=document.querySelector(s);return !!e&&getComputedStyle(e).display!=='none';}
            return {dock:v('#a3d-dock'),snaps:v('#a3d-snapgrp'),space:v('#a3d-stspace')};}""")
        ck(vis == {'dock': False, 'snaps': False, 'space': True},
           "on paper the model's tool dock and drawing aids step aside, and the space button shows (%s)" % vis)
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(250)
        vis = await safe("""()=>{function v(s){var e=document.querySelector(s);return !!e&&getComputedStyle(e).display!=='none';}
            return {dock:v('#a3d-dock'),snaps:v('#a3d-snapgrp'),space:v('#a3d-stspace')};}""")
        ck(vis == {'dock': True, 'snaps': True, 'space': False}, 'and come back in the model (%s)' % vis)

        # -------------------------------------------------------------------------------------------
        print('\n-- 8. each project keeps its own model view behind its sheets')
        await safe("()=>{window.__a3dSetPlanView();}")
        await page.mouse.move(800, 450)
        await page.mouse.wheel(0, 360)
        await page.wait_for_timeout(300)
        camA = await cam()
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(250)
        await page.click('#acad-doctabs [data-dt="new"]')
        await page.wait_for_timeout(500)
        await safe("()=>{window.__a3dSet3DView();}")
        await page.wait_for_timeout(300)
        a_id = (await safe("()=>window.__a3dDocs.open()"))[0]
        await page.click('#acad-doctabs [data-doc="%s"] .dt-name' % a_id)
        await page.wait_for_timeout(500)
        sp = await space()
        ck(sp.get('onSheet') and sp.get('viewId') == s201[0], 'back in the first project, its sheet is still the view (%s)' % sp.get('viewName'))
        await page.click('#a3d-laytabs [data-lt="model"]')
        await page.wait_for_timeout(300)
        sp = await space()
        ck(sp.get('view') == 'plan' and same_cam(camA, await cam()),
           "and its Model tab returns to its own plan and camera, not the other project's 3D view (%s)" % sp.get('view'))

        # -------------------------------------------------------------------------------------------
        print('\n-- 9. exports are the paper, without the working highlight')
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(250)
        vcx, vcy, s = await mm_to_px(20 + 60, 20 + 45)
        await page.mouse.dblclick(vcx, vcy)
        await page.wait_for_timeout(200)
        dl = None
        try:
            async with page.expect_download(timeout=5000) as d:
                await page.click('#a3d-sheetpng')
            dl = await d.value
        except Exception as e:
            print('      (no download: %s)' % str(e)[:80])
        px_border = px_out = None
        if dl:
            from PIL import Image
            im = Image.open(await dl.path()).convert('RGB')
            px_border = im.getpixel((int((20 + 60) * 6), int(20 * 6 + 2)))
            px_out = im.getpixel((int((20 + 120 + 30) * 6), int((20 + 30) * 6)))
        ck((await space()).get('activeVp') == vp and px_border is not None and px_border != (47, 127, 224) and px_out == (255, 255, 255),
           'in model space the exported PNG has no blue frame and no dimmed paper (%s, %s)' % (px_border, px_out))

        # -------------------------------------------------------------------------------------------
        print('\n-- 10. the command line')
        await page.keyboard.press('Escape')

        async def cmd(name):
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(120)
            await page.keyboard.type(name)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(350)
        await cmd('MODEL')
        ck(not (await space()).get('onSheet'), 'MODEL goes to the Model tab')
        n_sh = len(await sheets())
        await cmd('LAYOUT')
        sp = await space()
        ck(len(await sheets()) == n_sh + 1 and sp.get('onSheet') and sp.get('view') == 'sheet', 'LAYOUT adds a sheet and opens it')
        await page.click('#a3d-laytabs [data-ltsheet="%s"]' % s201[0])
        await page.wait_for_timeout(250)
        await cmd('MS')
        ck((await space()).get('activeVp') == vp, 'MS works in the viewport')
        await cmd('PS')
        ck((await space()).get('activeVp') is None, 'PS comes back to paper')

        # -------------------------------------------------------------------------------------------
        print('\n-- 11. what a viewport is set to survives a reload')
        vpstate = (await safe("(id)=>window.__a3dSheets().filter(function(x){return x.id===id;})[0].viewports.filter(function(v){return v.kind==='plan';})[0]", s201[0])) or {}
        await page.wait_for_timeout(500)
        await page.reload()
        await ready()
        after = (await safe("(id)=>{var s=window.__a3dSheets().filter(function(x){return x.id===id;})[0];return s?s.viewports.filter(function(v){return v.kind==='plan';})[0]:null;}", s201[0])) or {}
        ck(after.get('scaleDenom') == vpstate.get('scaleDenom') and after.get('pan') and vpstate.get('pan') and
           near(after['pan'][0], vpstate['pan'][0], 1e-9) and near(after['pan'][1], vpstate['pan'][1], 1e-9),
           'its pan and scale are part of the sheet, stored with the project (%s / %s)' % (after.get('pan'), after.get('scaleDenom')))

        ck(not errs, 'no page errors (%s)' % errs[:3])
        await browser.close()


asyncio.run(main())
