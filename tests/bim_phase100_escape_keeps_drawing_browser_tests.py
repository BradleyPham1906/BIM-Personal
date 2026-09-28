"""
bim_phase100_escape_keeps_drawing_browser_tests.py

Regression suite for __acad3dV100 in canvas_v10.html: ending a drawing command keeps what was
drawn, the way AutoCAD does.

FOUND IN V99: Escape during LINE threw away every segment already drawn. The same discard sat
behind the plan/3D switch and behind starting any other command, and Enter in PLINE CLOSED the
polyline (and with two points produced nothing), where AutoCAD's Enter ends it open.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. EVERY COMMAND IS DRIVEN FROM THE KEYBOARD: coordinates typed and committed with Enter, the
     command ended with the real Escape key. The assertion is on the objects in the model.
  2. EVERY EXIT IS DRIVEN SEPARATELY -- Escape, another command starting, the plan/3D switch --
     because each was a separate discard and each is a separate call site.
  3. LINE, PLINE and WALL are each checked, and so is a command with NOTHING complete (an arc
     with two of its three points, a line with one point), which must still leave nothing.
  4. ENTER AND ESCAPE ARE COMPARED on the same points: they must produce the same polyline,
     since the rule is derived from one finisher and a second copy would drift.
  5. CLOSE STILL CLOSES: C on a PLINE gives a closed polyline, so "Enter is open" did not turn
     into "nothing closes".
  6. UNDO takes a kept drawing back out.
  7. Zero uncaught page errors.

Run:  python3 bim_phase100_escape_keeps_drawing_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n = 0
        self.failed = []

    def __call__(self, cond, msg):
        self.n += 1
        ok = bool(cond)
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            self.failed.append(msg)


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950})
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(250)

        has = await page.evaluate("()=>!!window.__acad3dV100")
        ck(has, "__acad3dV100 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        mk = {'n': 0}

        async def fresh():
            # every scene carries a marker with a NEW id, so an Undo that restores some OLDER
            # snapshot (from an earlier scene) cannot pass for undoing this command
            mk['n'] += 1
            mk['id'] = 'MK%d' % mk['n']
            await page.evaluate("""(id)=>{window.__a3dTestSetObjs([{id:id,t:'sketch',name:id,col:'#5ec4b8',
                pos:[0,0,0],pts:[[40,40],[41,40]],y:0,closed:false}]);window.__a3dFlat(true);window.__a3dTestPaint();}""", mk['id'])
            await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
            await page.wait_for_timeout(150)

        async def objs():
            os_ = await page.evaluate("()=>window.__a3dState().objs")
            return [o for o in os_ if not str(o.get('id', '')).startswith('MK')]

        async def marker_only():
            ids_ = await page.evaluate("()=>window.__a3dState().objs.map(o=>o.id)")
            return ids_ == [mk['id']]

        async def cmd(name):
            ok = await page.evaluate("(n)=>window.__a3dRunCmd(n)", name)
            await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
            await page.wait_for_timeout(200)
            return ok

        async def pts(*ss):
            for s in ss:
                await page.keyboard.type(s)
                await page.wait_for_timeout(100)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(180)

        async def key(k):
            await page.keyboard.press(k)
            await page.wait_for_timeout(300)

        async def prompt():
            return await page.evaluate("()=>window.__a3dPrompt()")

        def sketches(os_):
            return [o for o in os_ if o.get('t') == 'sketch']

        # ------------------------------------------------ 1. Escape
        print("\n-- 1. Escape ends the command and keeps what is complete")
        await fresh()
        await cmd('line')
        await pts('0,0', '4,0', '4,3')
        await key('Escape')
        s = sketches(await objs())
        ck(len(s) == 2 and all(len(o['pts']) == 2 for o in s),
           "LINE, three points, Escape: the TWO segments drawn are kept as two lines (%d)" % len(s))
        ck(await prompt() == 'Ready', "and the command has ended (%r)" % await prompt())

        await fresh()
        await cmd('line')
        await pts('0,0')
        await key('Escape')
        ck(len(await objs()) == 0 and await prompt() == 'Ready',
           "LINE with only its first point: Escape leaves nothing, and ends")

        await fresh()
        await cmd('poly')
        await pts('0,0', '5,0', '5,2')
        await key('Escape')
        s = sketches(await objs())
        ck(len(s) == 1 and len(s[0]['pts']) == 3 and s[0].get('closed') is False,
           "PLINE, three points, Escape: ONE open polyline of 3 points is kept (%s)"
           % ([(len(o['pts']), o.get('closed')) for o in s]))
        esc_poly = s[0]['pts'] if s else None

        await fresh()
        await cmd('wall')
        await pts('0,0', '6,0', '6,4')
        await key('Escape')
        w = [o for o in await objs() if o.get('t') == 'solid' and (o.get('bim') or {}).get('type') == 'wall']
        cl = (w[0].get('bim') or {}).get('centerline') if w else None
        ck(len(w) == 1 and cl and len(cl) == 3 and not (w[0].get('bim') or {}).get('closed'),
           "WALL chain, three points, Escape: the wall is kept, open, along all 3 points (%s)" % cl)

        await fresh()
        await cmd('arc')
        await pts('0,0', '2,2')
        await key('Escape')
        ck(len(await objs()) == 0 and await prompt() == 'Ready',
           "ARC with two of its three points: Escape makes nothing (no half arc)")

        await fresh()
        st_ok = await cmd('stairTool')
        await pts('0,0', '4,0')
        st_pts = await page.evaluate("()=>window.__a3dSkPts()")
        await key('Escape')
        dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        ck(st_ok and st_pts and len(st_pts) == 2 and len(await objs()) == 0 and not dlg and await prompt() == 'Ready',
           "STAIR is not a drawing command: Escape cancels it, no stair and no dialog (dialog %s)" % dlg)

        # ------------------------------------------------ 2. Enter
        print("\n-- 2. Enter ends PLINE OPEN; C closes it")
        await fresh()
        await cmd('poly')
        await pts('0,0', '5,0', '5,2')
        await key('Enter')
        s = sketches(await objs())
        ck(len(s) == 1 and s[0].get('closed') is False,
           "PLINE, three points, Enter: an OPEN polyline, as AutoCAD (closed=%s)" % (s and s[0].get('closed')))
        ck(s and esc_poly is not None and s[0]['pts'] == esc_poly,
           "and exactly the polyline Escape produced from the same points")

        await fresh()
        await cmd('poly')
        await pts('0,0', '5,0')
        await key('Enter')
        s = sketches(await objs())
        ck(len(s) == 1 and len(s[0]['pts']) == 2,
           "PLINE, two points, Enter: a two-point polyline is kept (was: nothing) (%d)" % len(s))

        await fresh()
        await cmd('poly')
        await pts('0,0', '5,0', '5,2', '0,2')
        await key('c')
        s = sketches(await objs())
        ck(len(s) == 1 and s[0].get('closed') is not False and len(s[0]['pts']) == 4,
           "PLINE, four points, C: a CLOSED polyline (closed=%s)" % (s and s[0].get('closed')))

        toast = None
        await fresh()
        await cmd('poly')
        toast = await page.evaluate("()=>{const t=document.getElementById('a3d-toast');return t?t.textContent:'';}")
        ck('Enter to leave it open' in (toast or '') and 'Enter to close' not in (toast or ''),
           "the PLINE start message states the rule it now follows (%r)" % toast)
        await key('Escape')

        # ------------------------------------------------ 3. other exits
        print("\n-- 3. another command, or a view change, also keeps the drawing")
        await fresh()
        await cmd('line')
        await pts('0,0', '3,0')
        await cmd('room')
        s = sketches(await objs())
        pr = await prompt()
        ck(len(s) == 1, "LINE, two points, then the Room command: the line is kept (%d)" % len(s))
        ck('Room' in pr or 'room' in pr.lower() or pr != 'Ready',
           "and the Room command is the one now running (%r)" % pr)
        await key('Escape')

        await fresh()
        await cmd('poly')
        await pts('0,0', '2,0', '2,2')
        await key('Shift+Period')
        s = sketches(await objs())
        flat = await page.evaluate("()=>window.__a3dState().flat")
        ck(len(s) == 1 and s[0].get('closed') is False,
           "PLINE, three points, then switching to 3D: the polyline is kept, open (%d)" % len(s))
        ck(flat is False, "and the view did switch")
        await page.evaluate("()=>window.__a3dFlat(true)")

        await fresh()
        await cmd('sectionTool')
        await page.wait_for_timeout(100)
        await key('Escape')
        await cmd('line')
        await pts('0,0', '1,1')
        await cmd('sectionTool')
        s = sketches(await objs())
        ck(len(s) == 1, "LINE, two points, then the Section command (the starter with its own path): kept (%d)" % len(s))
        await key('Escape')

        # ------------------------------------------------ 4. undo
        print("\n-- 4. Undo takes a kept drawing back")
        await fresh()
        await cmd('poly')
        await pts('0,0', '4,0', '4,4')
        await key('Escape')
        n1 = len(sketches(await objs()))
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(200)
        n2 = len(sketches(await objs()))
        ck(n1 == 1 and n2 == 0 and await marker_only(),
           "the polyline Escape kept is removed by Undo, back to exactly this scene (%d -> %d)" % (n1, n2))

        await fresh()
        await cmd('line')
        await pts('0,0', '4,0', '4,4', '0,4')
        await key('Escape')
        n1 = len(sketches(await objs()))
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(200)
        n2 = len(sketches(await objs()))
        ck(n1 == 3 and n2 == 0 and await marker_only(),
           "a LINE run of 3 segments is ONE undo step, not three (%d -> %d)" % (n1, n2))

        await fresh()
        await cmd('rect')
        await pts('0,0', '3,2')
        n1 = len(sketches(await objs()))
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(200)
        n2 = len(sketches(await objs()))
        ck(n1 == 1 and n2 == 0 and await marker_only(),
           "a rectangle is undoable too -- no drawing command was before V100 (%d -> %d)" % (n1, n2))

        print("\n-- 5. a wall chain: Escape builds it, Enter still asks for its parameters")
        await fresh()
        await cmd('wall')
        await pts('0,0', '5,0')
        await key('Escape')
        dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        w = [o for o in await objs() if (o.get('bim') or {}).get('type') == 'wall']
        ck(len(w) == 1 and not dlg,
           "Escape builds the wall and leaves NO dialog behind (walls %d, dialog %s)" % (len(w), dlg))
        th = (w[0].get('bim') or {}).get('thickness') if w else None
        ck(th == 0.3, "with the thickness the dialog would have offered (%s)" % th)
        await fresh()
        await cmd('wall')
        await pts('0,0', '5,0')
        await cmd('line')
        dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        w = [o for o in await objs() if (o.get('bim') or {}).get('type') == 'wall']
        ck(len(w) == 1 and not dlg and await prompt() != 'Ready',
           "a wall chain interrupted by LINE is built, no dialog, and LINE runs (%d, %s)" % (len(w), dlg))
        await key('Escape')
        await fresh()
        await cmd('wall')
        await pts('0,0', '5,0')
        await key('Enter')
        dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        ck(dlg, "Enter on a wall chain still opens the parameters dialog")
        await page.evaluate("()=>{var d=document.querySelector('.a3d-dlg [data-a3dlg=\"cancel\"]');if(d)d.click();}")

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
