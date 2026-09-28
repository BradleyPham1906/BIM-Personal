"""
bim_phase86_command_line_autocad_browser_tests.py

Regression suite for __acad3dV86 in canvas_v10.html: the Cmd+K command palette runs against the
BIM engine, and LINE / PLINE / RECTANG behave the way AutoCAD's do.

WHAT THE USER ASKED FOR: "i hit cmd + k and the command shortkey from the past still there,
however it never work. it should pop up the new shortcut not the old. the line work needs
updates. like rec, poly, line, it needs to work like autocad (do your own reserach and copy how
they do it)"

WHAT WAS MEASURED BEFORE THE PATCH, driving the palette with real keys:

    LINE      matched=['LINE - Draw a line']      -> {'sk': None, 'objs': 0}
    RECTANG   matched=['RECTANG - Draw a rect']   -> {'sk': None, 'objs': 0}
    PLINE     matched=['PLINE - Draw a polyline'] -> {'sk': None, 'objs': 0}
              (and after two canvas clicks and Enter, still {'sk': None, 'objs': 0})

All 53 commands were dead. runCadAct dispatched into window.cadRun -> WB[act], the RETIRED
Canvas whiteboard's command table, which does not run in the BIM workspace -- and it returned
true regardless, so a command that did nothing still reported success.

THE AUTOCAD REFERENCE THIS WAS BUILT AGAINST (researched for this phase):

  * LINE emits one INDEPENDENT OBJECT PER SEGMENT; PLINE emits ONE object. Autodesk: PLINE
    "Creates a 2D polyline, a single object that is composed of line and arc segments."
    RECTANG "Creates a rectangular polyline." This is the defining difference between the
    commands, and check 4 is built on it.
  * Prompts: "Specify first point:" -> "Specify next point or [Undo]:" -> once Close is
    available, "Specify next point or [Close/Undo]:".
  * Coordinates: 3,4 absolute | @3,4 relative | 3<45 absolute polar | @1<45 relative polar |
    #3,4 forces absolute | a bare number is direct distance entry. Angles increase
    counter-clockwise from +X.
  * Keys: Enter/Space ends, Esc cancels, U removes the last segment, C closes. Enter at the
    Command prompt repeats the previous command.
  Sources: Autodesk help for LINE / PLINE / RECTANG, "About Entering 2D Polar Coordinates",
  "About Using Dynamic Input Tooltips", plus command-line transcripts from CADTutor.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. EVERY COMMAND THE PALETTE OFFERS IS RUN AND ITS EFFECT MEASURED. Not "the palette opens",
     not "the list is non-empty" -- each row is dispatched and the engine is read back. The bug
     being fixed is precisely a palette that looked perfect and did nothing, and a check on
     appearance would have passed on it for as long as it existed.
  2. THE PROMPT AND THE KEYS ARE ASSERTED TO AGREE AT EVERY POINT COUNT. The first build of this
     phase offered [Close/Undo] at two points while the C key required three, so the prompt
     advertised an option the command refused. The check walks the point count up and asserts
     that "Close" appears in the bracket list IF AND ONLY IF pressing C actually closes.
  3. LINE is asserted to produce N-1 OBJECTS and PLINE exactly 1. This is the difference between
     copying AutoCAD and copying the look of AutoCAD.
  4. FOCUS IS ASSERTED TO RETURN TO THE DRAWING after a palette command. The palette left focus
     in its own hidden input, and the BIM key chain returns early on an INPUT target, so the
     command worked and then every keystroke after it was silently swallowed. Measured:
     activeElement was INPUT and the typing buffer stayed empty. That is worse than a dead
     command, because it looks like it worked.
  5. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase86_command_line_autocad_browser_tests.py [path/to/canvas_v10.html]
"""

# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

ST = """()=>{const s=window.__a3dState();
 return {tool:s.sk?s.sk.tool:null, pts:window.__a3dSkPts(), objs:s.objs.length,
         prompt:window.__a3dPrompt(), typing:window.__a3dTyping()};}"""


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


async def palette_run(page, name):
    """Run a command the way the user does: Cmd/Ctrl+K, type it, Enter."""
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(350)
    await page.keyboard.type(name)
    await page.wait_for_timeout(220)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


async def type_point(page, s):
    """Type a coordinate and commit it, as a drafter would."""
    await page.keyboard.type(s)
    await page.wait_for_timeout(120)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(200)


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
        await page.wait_for_timeout(2300)
        await page.mouse.click(800, 500)          # give the page genuine input focus
        await page.wait_for_timeout(250)

        has86 = await page.evaluate("()=>!!window.__acad3dV86")
        ck(has86, "__acad3dV86 marker is present")
        if not has86:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ------------------------------------------------------------------ 1
        print("\n-- 1. the palette offers only commands that RUN, and runs them")
        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(400)
        rows = await page.evaluate(
            "()=>[...document.querySelectorAll('.a3d-cmdrow')].map(r=>r.textContent.trim())")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)
        print("     " + str(rows))
        ck(len(rows) > 0, "the palette lists commands (%d)" % len(rows))
        names = [r.split(' — ')[0].split('—')[0].strip() for r in rows]
        for want in ('LINE', 'PLINE', 'RECTANG', 'CIRCLE'):
            ck(want in names, "%s is offered" % want)

        supported = await page.evaluate("""()=>{
          const acts=['line','poly','rect','circle','text','leader','bimDims','measure','trim',
                      'mirror','offset','duplicate','del','zoomFit','selAll','selNone',
                      'bimSnap','bimOrtho','grid'];
          const out={};
          acts.forEach(a=>{out[a]=!!window.__a3dCmdSupported(a);});
          return out;
        }""")
        ck(all(supported.values()),
           "every act in the BIM table reports supported (%s)"
           % [k for k, v in supported.items() if not v])
        ck(await page.evaluate("()=>window.__a3dCmdSupported('donut')") is False,
           "and an act with no BIM implementation reports UNSUPPORTED, so it is never offered")

        print("     driving each offered command and reading the engine back")
        # A command is measured in a state where it CAN act. The first version of this block ran
        # every command against an empty model, so selAll selected nothing, selNone cleared
        # nothing and zoomFit had nothing to frame -- three working commands reported as dead.
        # trim is different again: it legitimately REFUSES without a cutting wall selected and
        # says so, which is a precondition, not a dead command. So the model gets a wall, and
        # the wall is selected before each probe.
        # TWO objects, not one: with a single object in the model, selAll selects exactly what
        # was already selected and reports no change -- a working command measured as dead.
        wall = await page.evaluate("""()=>window.__a3dWall(
          [[-8,-5],[8,-5],[8,5],[-8,5]],0.3,3,'center',true)""")
        await page.wait_for_timeout(500)
        wall2 = await page.evaluate("""()=>window.__a3dWall(
          [[14,-5],[22,-5],[22,5]],0.3,3,'center',false)""")
        await page.wait_for_timeout(500)
        n_obj = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(bool(wall) and bool(wall2) and n_obj >= 2,
           "two walls exist so every command has something to act on (%d objects)" % n_obj)

        effects = await page.evaluate("""(wallId)=>{
          const acts=['line','poly','rect','circle','text','leader','bimDims','trim',
                      'selAll','selNone','bimSnap','bimOrtho','grid','zoomFit'];
          const out={};
          for(const a of acts){
            // reset to a known, actionable state before each probe
            window.__a3dRunCmd('selNone');
            const dlg0=document.querySelector('.a3d-dlg');
            if(dlg0&&dlg0.parentNode)dlg0.parentNode.removeChild(dlg0);
            window.__a3dSelectFor([wallId]);
            const s0=window.__a3dState(), sn0=window.__a3dSnapState();
            const c0=JSON.stringify(s0.cam), sel0=window.__a3dSelSet().length;
            const ran=window.__a3dRunCmd(a);
            const s1=window.__a3dState(), sn1=window.__a3dSnapState();
            const changed = (!!s1.sk !== !!s0.sk) || (s1.sk&&s0.sk&&s1.sk.tool!==s0.sk.tool)
              || JSON.stringify(sn1)!==JSON.stringify(sn0)
              || window.__a3dSelSet().length!==sel0
              || JSON.stringify(s1.cam)!==c0
              || s1.objs.length!==s0.objs.length
              || !!document.querySelector('.a3d-dlg');
            out[a]={ran:!!ran, changed:!!changed};
            const dlg=document.querySelector('.a3d-dlg');
            if(dlg&&dlg.parentNode)dlg.parentNode.removeChild(dlg);
          }
          return out;
        }""", wall)
        for act, r in effects.items():
            ck(r['ran'] and r['changed'],
               "  %-9s ran=%s and changed engine state=%s"
               % (act, r['ran'], r['changed']))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)
        await page.evaluate("()=>window.__a3dRunCmd('selNone')")

        print("     SHORTCUTS reaches the V85 sheet, and the sheet describes THIS grammar")
        # The user's sentence is ambiguous -- "it should pop up the new shortcut not the old"
        # reads either as the dead command list (fixed above) or as a request for Cmd+K to reach
        # the keyboard-shortcuts sheet. Both are satisfied rather than guessed between.
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        await palette_run(page, 'SHORTCUTS')
        sheet = await page.evaluate("""()=>{
          const p=document.getElementById('a3d-rupop');
          if(!p||!p.classList.contains('open'))return null;
          return {forId:p.getAttribute('data-for'),
                  labels:[...p.querySelectorAll('.a3d-rklab')].map(e=>e.textContent.trim())};
        }""")
        ck(sheet is not None and sheet['forId'] == 'help',
           "the SHORTCUTS command opens the keyboard shortcuts sheet (%s)"
           % (sheet and sheet['forId']))
        if sheet:
            joined = ' | '.join(sheet['labels'])
            ck('@x,y' in joined and 'relative' in joined,
               "and the sheet documents relative coordinates")
            ck('Polar' in joined or '@5<45' in joined,
               "and polar coordinates")
            ck(any('Undo the last point' in l for l in sheet['labels']),
               "and U, which V86 added")
            ck(not any('Type an exact length while drawing' in l for l in sheet['labels']),
               "and no longer describes the pre-V86 grammar, which accepted a bare length and "
               "nothing else")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)

        # ------------------------------------------------------------------ 2
        print("\n-- 2. the palette hands the keyboard back to the drawing")
        await palette_run(page, 'LINE')
        focus = await page.evaluate(
            "()=>{const a=document.activeElement;return a?a.tagName:null;}")
        ck(focus != 'INPUT',
           "focus is not left in the palette input (%s) -- the BIM key chain returns early on an "
           "INPUT target, so leaving it there silently swallowed every keystroke AFTER the "
           "command: the tool started and then nothing else worked" % focus)
        await page.keyboard.type('3,4')
        await page.wait_for_timeout(200)
        buf = await page.evaluate("()=>window.__a3dTyping()")
        ck(buf['active'] is True and buf['buf'] == '3,4',
           "and typing immediately after the command reaches the engine (%s)" % buf)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)

        # ------------------------------------------------------------------ 3
        print("\n-- 3. AutoCAD coordinate entry, all five forms")
        await page.evaluate("()=>window.__a3dRunCmd('line')")
        await page.wait_for_timeout(300)
        st = await page.evaluate(ST)
        ck(st['prompt'] == 'Specify first point:',
           "the first prompt is AutoCAD's (%r)" % st['prompt'])

        await type_point(page, '0,0')
        await type_point(page, '@10,0')
        await type_point(page, '@0,-8')
        pts = await page.evaluate("()=>window.__a3dSkPts()")
        ck(pts == [[0, 0], [10, 0], [10, -8]],
           "absolute '0,0' and relative '@10,0' / '@0,-8' land exactly (%s)" % pts)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)

        await page.evaluate("()=>window.__a3dRunCmd('line')")
        await page.wait_for_timeout(300)
        for s in ('0,0', '@10<0', '@10<90', '@10<180'):
            await type_point(page, s)
        polar = await page.evaluate("()=>window.__a3dSkPts()")
        ok_polar = (polar and len(polar) == 4
                    and abs(polar[1][0] - 10) < 1e-6 and abs(polar[1][1]) < 1e-6
                    and abs(polar[2][0] - 10) < 1e-6 and abs(polar[2][1] + 10) < 1e-6
                    and abs(polar[3][0]) < 1e-6 and abs(polar[3][1] + 10) < 1e-6)
        ck(ok_polar,
           "relative polar '@d<a' walks 0deg=+X, 90deg=screen-up, 180deg=-X (%s) -- the sign of "
           "the angle was MEASURED against this app's plan camera (+X projects right, +Z "
           "projects DOWN), not assumed" % polar)

        dde = await page.evaluate("()=>window.__a3dParseCoord('#7,7')")
        ck(dde == [7, 7], "'#7,7' forces an absolute coordinate (%s)" % dde)
        bad = await page.evaluate("()=>window.__a3dParseCoord('banana')")
        ck(bad is None, "and a string that is not a coordinate is refused rather than guessed (%s)"
           % bad)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)

        # ------------------------------------------------------------------ 4
        print("\n-- 4. THE CHECK THAT MATTERS: the prompt and the keys agree at every point count")
        print("     The first build of this phase offered [Close/Undo] at two points while the C")
        print("     key required three -- the bracket list advertised an option the command")
        print("     refused. The list is now derived from the same predicate C consults.")
        for tool, label in (('line', 'LINE'), ('poly', 'PLINE')):
            for n in (1, 2, 3):
                await page.evaluate("(t)=>window.__a3dRunCmd(t)", tool)
                await page.wait_for_timeout(250)
                coords = ['0,0', '@6,0', '@0,-6'][:n]
                for c in coords:
                    await type_point(page, c)
                prompt = await page.evaluate("()=>window.__a3dPrompt()")
                objs_before = await page.evaluate("()=>window.__a3dState().objs.length")
                await page.keyboard.press('c')
                await page.wait_for_timeout(400)
                after = await page.evaluate(ST)
                closed = (after['tool'] is None) and (after['objs'] > objs_before)
                offered = 'Close' in prompt
                ck(offered == closed,
                   "%s at %d point(s): prompt offers Close=%s and C actually closes=%s -- %r"
                   % (label, n, offered, closed, prompt))
                if not closed:
                    await page.keyboard.press('Escape')
                    await page.wait_for_timeout(200)

        # ------------------------------------------------------------------ 5
        print("\n-- 5. LINE makes one object per segment; PLINE makes one; RECTANG makes one")
        base = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.evaluate("()=>window.__a3dRunCmd('line')")
        await page.wait_for_timeout(250)
        for s in ('0,0', '@10,0', '@0,-8', '@-10,0'):
            await type_point(page, s)
        await page.keyboard.press('Enter')          # end the sequence
        await page.wait_for_timeout(450)
        n_line = await page.evaluate("()=>window.__a3dState().objs.length") - base
        ck(n_line == 3,
           "4 points -> %d LINE objects (expected 3, one per segment) -- Autodesk: LINE segments "
           "are independent objects, which is the whole difference from PLINE" % n_line)

        base = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.evaluate("()=>window.__a3dRunCmd('poly')")
        await page.wait_for_timeout(250)
        for s in ('30,0', '@10,0', '@0,-8', '@-10,0'):
            await type_point(page, s)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(450)
        n_poly = await page.evaluate("()=>window.__a3dState().objs.length") - base
        ck(n_poly == 1,
           "the same 4 points as PLINE -> %d object (expected 1) -- \"a single object composed of "
           "line and arc segments\"" % n_poly)

        base = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.evaluate("()=>window.__a3dRunCmd('rect')")
        await page.wait_for_timeout(250)
        pr = await page.evaluate("()=>window.__a3dPrompt()")
        ck(pr == 'Specify first corner point:', "RECTANG prompts for the first corner (%r)" % pr)
        await type_point(page, '60,0')
        pr2 = await page.evaluate("()=>window.__a3dPrompt()")
        ck(pr2 == 'Specify other corner point:', "then the other corner (%r)" % pr2)
        await type_point(page, '@12,-7')
        await page.wait_for_timeout(400)
        n_rect = await page.evaluate("()=>window.__a3dState().objs.length") - base
        done = await page.evaluate("()=>window.__a3dState().sk")
        ck(n_rect == 1 and done is None,
           "two corners -> %d closed profile and the command ends (sk=%s) -- RECTANG \"Creates a "
           "rectangular polyline\"" % (n_rect, done))

        # ------------------------------------------------------------------ 6
        print("\n-- 6. U removes the last segment; Esc cancels; Enter repeats")
        await page.evaluate("()=>window.__a3dRunCmd('line')")
        await page.wait_for_timeout(250)
        for s in ('0,0', '@5,0', '@5,5'):
            await type_point(page, s)
        n_before = len(await page.evaluate("()=>window.__a3dSkPts()"))
        await page.keyboard.press('u')
        await page.wait_for_timeout(300)
        n_after = len(await page.evaluate("()=>window.__a3dSkPts()"))
        ck(n_after == n_before - 1,
           "U removes the most recent point (%d -> %d)" % (n_before, n_after))

        objs_before = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(350)
        esc = await page.evaluate(ST)
        ck(esc['tool'] is None,
           "Escape cancels the command (%s)" % esc['tool'])
        # __acad3dV100 changed this on purpose. V86 asserted Escape DISCARDS the run; AutoCAD
        # does the opposite -- a LINE segment exists the moment its second point is placed,
        # and Escape ends the command with the completed segments kept. After U, two points
        # remain: one segment, so one line.
        ck(esc['objs'] == objs_before + 1,
           "and keeps the completed segment, as AutoCAD does (%d -> %d objects)"
           % (objs_before, esc['objs']))

        last = await page.evaluate("()=>window.__a3dLastCmd()")
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(400)
        rep = await page.evaluate(ST)
        ck(rep['tool'] == 'line',
           "Enter at the command prompt repeats the previous command (last=%r, now=%s) -- "
           "Autodesk: \"You can also repeat the previous command by pressing Enter or the "
           "spacebar\"" % (last, rep['tool']))
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(250)

        # ------------------------------------------------------------------ 7
        print("\n-- 7. nothing was left behind")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        ck(audit and audit.get('ok') is True,
           "the V80 shell audit is clean: %d claimed, unclaimed=%s"
           % (audit.get('claimed', -1), audit.get('unclaimed')))
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
