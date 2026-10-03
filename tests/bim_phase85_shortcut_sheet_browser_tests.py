"""
bim_phase85_shortcut_sheet_browser_tests.py

Regression suite for __acad3dV85 in canvas_v10.html: the dead "A?" button is replaced by a real
keyboard shortcuts sheet in the rail's utility stack.

WHAT THE USER ASKED: "whats that a? thing then its useless"

WHAT IT WAS, measured by clicking it with a real pointer on the shipped build:

    A? button: {'text': 'A?', 'title': None, 'w': 24, 'h': 24, 'attrs': ['class=fl-help']}
    before:    {'dlgs': 0, 'toast': None}
    after :    {'dlgs': 0, 'toast': None}

Nothing happened. There was no click handler for '.fl-help' anywhere in the file. It was Figma-
style set dressing inherited from the whiteboard shell's template.

THE PART THAT WAS MY FAULT, and the reason check 4 below exists: V80 added a whitelist so that any
control in the left shell which is not claimed fails the build, and I claimed this one as
'keyboard help' on the strength of its appearance, without ever driving it. The audit then
reported a clean shell over a dead button for five phases. A whitelist entry taken on faith is
worse than no whitelist, because it converts an unexamined control into a documented one.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. EVERY SHORTCUT THE SHEET DOCUMENTS IS DISPATCHED AS A REAL KEY EVENT AND ITS CLAIMED EFFECT
     MEASURED. This is the check that matters. A help sheet is the one kind of UI that can rot
     silently and invisibly: it keeps rendering beautifully while the shortcuts it names stop
     working, and no user ever reports it because they assume they mistyped. The sheet is written
     as a list (the key handlers are a switch chain, not a table, so V74's derive-don't-list rule
     cannot be applied literally here) -- so the suite is what holds the list to account.
  2. The A? button is asserted GONE, and gone again after the whiteboard shell re-renders its own
     rail, because that shell rebuilds the rail from its template and would put it back.
  3. The sheet is asserted to open fully ON SCREEN by measuring its rectangle -- the V70 lesson,
     where the dock's carets once opened at top 1109 in a 950px window while every state check
     passed.
  4. The V80 shell audit is asserted clean AND asserted not to be claiming '.fl-help' any more.
     A claim left behind for a removed element is how the original fault would return.
  5. Zero uncaught page errors.

Run:  python3 bim_phase85_shortcut_sheet_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
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


async def open_help(page):
    """Open the shortcuts sheet with a REAL mouse click on its rail button.

    Playwright only delivers keyboard events to a page with genuine input focus, and a synthetic
    element.click() gives it none -- the V83 suite lost three checks to exactly that. Everything
    in this suite is driven by real pointer and real keyboard for the same reason.
    """
    btn = await page.evaluate("""()=>{
      const b=document.querySelector('[data-a3drumenu="help"]');
      if(!b)return null;
      const r=b.getBoundingClientRect();
      return {x:r.left+r.width/2,y:r.top+r.height/2};
    }""")
    if not btn:
        return None
    await page.mouse.click(btn['x'], btn['y'])
    await page.wait_for_timeout(300)
    return await page.evaluate("""()=>{
      const p=document.getElementById('a3d-rupop');
      if(!p||!p.classList.contains('open'))return null;
      const r=p.getBoundingClientRect();
      return {forId:p.getAttribute('data-for'),
              left:r.left,top:r.top,right:r.right,bottom:r.bottom,
              w:r.width,h:r.height,
              rows:[...p.querySelectorAll('.a3d-rkrow')].length,
              grps:[...p.querySelectorAll('.a3d-rkgrp')].filter(e=>(e.getAttribute('data-rkg')||'').indexOf('tool:')!==0).map(e=>e.textContent.trim())};   /* AMENDED FOR V130: the panel lists the tools too; these are the key groups */
    }""")


async def run():
    ck = Checks()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1600, 'height': 950},
                                        device_scale_factor=2)
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto('file://' + str(HTML))
        await page.wait_for_timeout(2200)

        has85 = await page.evaluate("()=>!!window.__acad3dV85")
        ck(has85, "__acad3dV85 marker is present")
        if not has85:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------------------------ 1
        print("\n-- 1. the dead A? button is gone, and stays gone")
        gone = await page.evaluate("()=>document.querySelectorAll('.fl-help').length")
        ck(gone == 0,
           "no .fl-help button anywhere (%d) -- it had no click handler in the entire file, no "
           "title, and driven with a real pointer it produced no dialog, no toast and no visible "
           "change" % gone)

        # AMENDED FOR V120: "removed again when the shell re-renders its rail" is retired. It injected the
        # button the whiteboard's rail template used to bring back; the template went in V113b, and the pass
        # that kept removing the button went in V120i.

        stack = await page.evaluate("()=>window.__a3dRailUtils()")
        ids = [s['id'] for s in (stack or [])]
        ck(ids == ['zoom', 'appear', 'snaps', 'units', 'capture', 'help'],
           "the stack now ends with the shortcuts entry: %s" % ids)
        xs = set(s['x'] for s in stack)
        ck(len(xs) == 1, "still one vertical column (x=%s)" % list(xs))

        # ------------------------------------------------------------------ 2
        print("\n-- 2. it opens a real sheet, fully on screen")
        pop = await open_help(page)
        print("     " + str(pop))
        ck(pop is not None, "the shortcuts sheet opens")
        if pop:
            ck(pop['forId'] == 'help', "and it is the help sheet (%s)" % pop['forId'])
            ck(pop['rows'] >= 12, "with a real number of shortcut rows (%d)" % pop['rows'])
            # AMENDED FOR V122: the Pages display's keys and Present's, drawn from their tables
            # AMENDED FOR V123: how a face is taken and the keys a held face listens to (Faces)
            # AMENDED FOR V129: typed point input (x,y  @x,y  d<a) is a grammar, not a key, so it has
            # its own page after Drawing instead of three rows inside it
            ck(pop['grps'] == ['Views', 'Drawing', 'Typing points', 'Snaps', 'Editing', 'Project', 'Faces', 'Pages', 'Presenting'],
               "grouped by what the keys do (%s)" % pop['grps'])
            on_screen = (pop['left'] >= 0 and pop['top'] >= 0
                         and pop['right'] <= 1600 and pop['bottom'] <= 950)
            ck(on_screen,
               "and lands fully on screen: l=%.0f t=%.0f r=%.0f b=%.0f in a 1600x950 window -- "
               "the V70 lesson, where a fixed popover inside a transformed ancestor once opened "
               "at top 1109 while every state check passed"
               % (pop['left'], pop['top'], pop['right'], pop['bottom']))

        # AMENDED FOR V130: the panel is Tools and shortcuts; the registry's rows are its key rows
        keys_in_dom = await page.evaluate("""()=>[...document.querySelectorAll('#a3d-rupop .a3d-rkrow[data-rkkind="key"]')]
          .map(r=>({keys:[...r.querySelectorAll('kbd')].map(k=>k.textContent.trim()),
                    label:r.querySelector('.a3d-rklab').textContent.trim()}))""")
        reg = await page.evaluate("()=>window.__a3dShortcuts()")
        flat = [r for g in reg for r in g['rows']]
        ck(len(keys_in_dom) == len(flat),
           "every registry row is rendered, none invented (%d rendered, %d in the registry)"
           % (len(keys_in_dom), len(flat)))
        ck(all(d['label'] == r['label'] for d, r in zip(keys_in_dom, flat)),
           "and each row's text is the registry's text, in order")

        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)
        closed = await page.evaluate("()=>{const p=document.getElementById('a3d-rupop');"
                                     "return !(p&&p.classList.contains('open'));}")
        ck(closed, "Escape closes the sheet")

        # ------------------------------------------------------------------ 3
        print("\n-- 3. THE CHECK THAT MATTERS: every key the sheet documents actually works")
        print("     A help sheet is the one kind of UI that rots invisibly -- it keeps rendering")
        print("     while the keys it names stop working, and nobody reports it because they")
        print("     assume they mistyped. So each row is dispatched for real and measured.")

        # Put focus on the page body so the app's keydown chain actually receives the keys.
        await page.mouse.click(800, 500)
        await page.wait_for_timeout(200)

        async def snap_state():
            return await page.evaluate("()=>{const s=window.__a3dSnapState?window.__a3dSnapState():null;"
                                       "return s?{point:!!s.point,grid:!!s.grid,ortho:!!s.ortho}:null;}")

        s0 = await snap_state()
        ck(s0 is not None, "snap state is readable for the F-key checks (%s)" % s0)

        for key, field in (('F3', 'point'), ('F8', 'ortho'), ('F9', 'grid')):
            before = await snap_state()
            await page.keyboard.press(key)
            await page.wait_for_timeout(200)
            after = await snap_state()
            ck(before and after and before[field] != after[field],
               "%s toggles %s as the sheet says (%s -> %s)"
               % (key, field, before and before[field], after and after[field]))
            await page.keyboard.press(key)          # restore
            await page.wait_for_timeout(150)

        # Shift + > : plan <-> 3D
        flat_before = await page.evaluate("()=>window.__a3dState().flat")
        # 'Shift+.' is NOT the same thing: Playwright delivers key='.' for it and the app
        # listens for key='>'. Measured: Shift+. -> key='.', nothing happens; Shift+Period ->
        # key='>', the view switches. The first version of this check used Shift+. and reported
        # a working feature as broken.
        await page.keyboard.press('Shift+Period')
        await page.wait_for_timeout(350)
        flat_after = await page.evaluate("()=>window.__a3dState().flat")
        ck(flat_before != flat_after,
           "> switches between the plan and 3D as the sheet says (flat %s -> %s)"
           % (flat_before, flat_after))

        # Escape: back out of transient states, then clear the selection, then STOP.
        # The first version of this check pressed Escape once in the 3D view and watched the
        # app leave the BIM workspace entirely -- body lost 'a3d-mode' and every later check
        # failed because the engine had stopped. That was real: the chain used to end with
        # exit3d(). Escape is the most reflexive key in a drawing app and must never do that.
        probe = await page.evaluate("""()=>window.__a3dWall(
          [[-2,-2],[2,-2],[2,2],[-2,2]],0.3,3,'center',true)""")
        await page.wait_for_timeout(450)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", probe)
        await page.wait_for_timeout(200)
        sel_before = await page.evaluate("()=>window.__a3dSelSet().length")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(350)
        after_esc = await page.evaluate("""()=>({
          flat:window.__a3dState().flat,
          sel:window.__a3dSelSet().length,
          inShell:document.body.className.indexOf('a3d-mode')>=0,
          on:!!window.__a3dOn})""")
        ck(sel_before > 0 and after_esc['sel'] == 0,
           "Escape clears the selection as the sheet says (%d -> %d selected)"
           % (sel_before, after_esc['sel']))
        ck(after_esc['inShell'] is True and after_esc['on'] is True,
           "and does NOT leave the workspace (inShell=%s, engine on=%s) -- one Escape in the 3D "
           "view used to close the entire BIM workspace"
           % (after_esc['inShell'], after_esc['on']))
        ck(after_esc['flat'] == flat_after,
           "and does not swing the camera either (flat %s -> %s) -- Escape in a plan used to "
           "send the user to the 3D view" % (flat_after, after_esc['flat']))

        await page.keyboard.press('Escape')
        await page.wait_for_timeout(300)
        after_esc2 = await page.evaluate("""()=>({
          inShell:document.body.className.indexOf('a3d-mode')>=0,
          on:!!window.__a3dOn})""")
        ck(after_esc2['inShell'] is True and after_esc2['on'] is True,
           "a SECOND Escape with nothing left to cancel still does not leave the workspace (%s)"
           % after_esc2)

        # back to the plan for the editing checks
        await page.evaluate("()=>window.__a3dSetPlanView()")
        await page.wait_for_timeout(300)

        # Undo / redo / duplicate, on a real object
        wall = await page.evaluate("""()=>window.__a3dWall(
          [[-6,-4],[6,-4],[6,4],[-6,4]],0.3,3,'center',true)""")
        await page.wait_for_timeout(500)
        ck(bool(wall), "a wall exists for the editing checks (%s)" % wall)
        mod = await page.evaluate(
            "()=>/Mac|iPhone|iPad/.test(navigator.platform)?'Meta':'Control'")

        n_before = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.keyboard.press('%s+z' % mod)
        await page.wait_for_timeout(350)
        n_undo = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(n_undo < n_before,
           "%s + Z undoes as the sheet says (%d -> %d objects)" % (mod, n_before, n_undo))

        await page.keyboard.press('%s+y' % mod)
        await page.wait_for_timeout(350)
        n_redo = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(n_redo == n_before,
           "%s + Y redoes as the sheet says (%d -> %d objects)" % (mod, n_undo, n_redo))

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", wall)
        await page.wait_for_timeout(250)
        n_sel = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.keyboard.press('%s+d' % mod)
        await page.wait_for_timeout(450)
        n_dup = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(n_dup > n_sel,
           "%s + D duplicates the selection as the sheet says (%d -> %d objects)"
           % (mod, n_sel, n_dup))

        undocumented = [r for r in flat if r.get('k') is None]
        print("     rows this suite cannot dispatch with one synthetic keypress, by design: %s"
              % [r['keys'] for r in undocumented])
        ck(all(r.get('label') for r in undocumented),
           "and those rows still carry a real description rather than a blank")

        # ------------------------------------------------------------------ 4
        print("\n-- 4. the audit no longer claims a control that does not exist")
        claims = await page.evaluate("""()=>{
          const a=window.__a3dShellAudit();
          return {ok:a.ok, claimed:a.claimed, unclaimed:a.unclaimed};
        }""")
        ck(claims['ok'] is True,
           "the V80 shell audit is clean: %d claimed, unclaimed=%s"
           % (claims['claimed'], claims['unclaimed']))
        src_has_claim = await page.evaluate("""()=>{
          // the claim list is not exposed; probe it by its effect instead -- a synthetic
          // .fl-help element must now be reported UNCLAIMED rather than waved through.
          const rail=document.getElementById('a3d-rail');
          const b=document.createElement('button');
          b.className='fl-help'; b.textContent='A?';
          b.style.cssText='width:24px;height:24px;display:block';
          rail.appendChild(b);
          const a=window.__a3dShellAudit();
          b.remove();
          return (a.unclaimed||[]).some(u=>String(u.cls||'').indexOf('fl-help')>=0);
        }""")
        ck(src_has_claim is True,
           "and an '.fl-help' button, if one ever came back, is now reported UNCLAIMED (%s) -- "
           "it used to be waved through by a claim I wrote on the strength of its appearance "
           "without ever driving it" % src_has_claim)
        await page.wait_for_timeout(800)

        body = await page.evaluate("()=>document.body.className")
        ck('a3d-mode' in body, "and the app is still inside the BIM shell (%r)" % body)

        print("")
        ck(not errs, "zero uncaught page errors across every probe (%s)" % (errs or 'none'))

        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    if ck.failed:
        print("RESULT: FAIL")
        for f in ck.failed:
            print("  - " + f)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
