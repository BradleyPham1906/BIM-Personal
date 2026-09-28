"""
bim_phase87_modify_toolbox_browser_tests.py

Regression suite for __acad3dV87 in canvas_v10.html: the modify toolbox, part one.

SCOPE OF THE PHASE: EXTEND, BREAK, BREAKATPOINT, LENGTHEN, CHAMFER, SCALE as real commands on
the BIM model; FILLET at radius 0; and ROTATE / ARRAYRECT / ARRAYPOLAR / ALIGN / JOIN made
reachable from the command line, which they were not.

THE AUTOCAD REFERENCE THIS WAS BUILT AGAINST:

  * EXTEND "Extends objects to meet the edges of other objects." The picked END moves, along
    its own direction, to the first boundary it meets -- forward only.
  * BREAK with two points removes the piece BETWEEN them and leaves two objects.
    BREAKATPOINT splits in place and removes nothing.
  * LENGTHEN offers DElta / Total / Percent and changes the end nearest the pick.
  * CHAMFER "Bevels the edges of objects", the two distances measured back from the corner.
  * FILLET at radius 0 produces a square corner -- the same miter Join Walls already performed.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. THE GEOMETRY IS ASSERTED ON THE POINTS, WITH ARITHMETIC THAT HAS A KNOWN ANSWER. A wall
     from (0,0) to (10,0) extended to a boundary at x=15 ends at exactly (15,0). A drawing that
     looks right is not evidence; every appearance check passed for the whole life of the V86
     dead palette.
  2. EVERY REFUSAL IS ASSERTED TOO. A modify command that silently does nothing looks the same
     as one that legitimately declined. Each geometry function is fed the case it must refuse
     (closed loop, zero distance, shortening past a vertex, parallel walls) and must return an
     {error}, not a guess.
  3. EACH COMMAND IS RUN THE WAY THE USER RUNS IT -- Ctrl+K, type, Enter -- and then the MODEL
     is read back: object count, centerline coordinates, wall thickness. Not a toast, not a
     class on a button.
  4. THE PROMPT AND THE COMMAND ARE ASSERTED TO AGREE. BREAK asks for a second point only while
     it is actually waiting for one.
  5. THE TYPED-COORDINATE CLASS BUG. bimCommitTypedPoint used to push the point onto sk.pts and
     stop, with special cases for RECTANG and CIRCLE only, so MIRROR / ROTATE / TRIM / DIM took
     a typed coordinate, showed it accepted, and did nothing. The check types a full MIRROR by
     coordinate and asserts a mirrored object exists.
  6. SCALE IS ASSERTED TO LEAVE BIM PARAMETERS ALONE. Scaling a plan by 2 doubles the centerline
     and must NOT double the wall thickness -- thickness is a type parameter, and a wall type
     reading "Generic - 300mm" that silently became 600 would be a data bug, not a drawing one.
  7. Zero uncaught page errors, and the V80 shell audit stays clean.

Run:  python3 bim_phase87_modify_toolbox_browser_tests.py [path/to/canvas_v10.html]
"""
# AMENDED FOR V120: the shell's canvas-era names were replaced -- #figma-layers-shell/-rail/-panel are
# #a3d-shell/-rail/-leftpanel, the .fl-* classes .a3d-*, #uploaded-command-palette #a3d-cmdpal, the
# Project Browser tab 'file' is 'browser', --figma-dock-w is --a3d-left-w, and the material library is
# read through window.__a3dMaterialCards() (window.__WB_MATERIAL_CARDS is gone).
import asyncio, pathlib, sys

from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

TOL = 1e-6


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


def near(a, b, tol=1e-4):
    return a is not None and b is not None and abs(a - b) <= tol


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(200)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(400)


async def dlg_ok(page, values=None):
    """Fill the open dialog's numeric fields and press OK, as a user would."""
    if values:
        for sel, val in values.items():
            await page.fill('.a3d-dlg [data-a3dp="%s"]' % sel, str(val))
            await page.wait_for_timeout(80)
    await page.click('.a3d-dlg [data-a3dlg="ok"]')
    await page.wait_for_timeout(420)


async def reset_model(page):
    await page.evaluate("()=>{window.__a3dTestSetObjs([]);}")
    await page.wait_for_timeout(120)


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

        has87 = await page.evaluate("()=>!!window.__acad3dV87")
        ck(has87, "__acad3dV87 marker is present")
        if not has87:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        # ---------------------------------------------------------------- 1. geometry core
        print("\n-- 1. the geometry core, on answers that can be computed by hand")

        # V92 replaced the straight-only bimExtendPolyline with the bulged one and deleted it,
        # so these drive __a3dExtendBulged -- the function the app runs. Claims unchanged.
        r = await page.evaluate("""()=>window.__a3dExtendBulged(
            [[0,0],[10,0]],null,false,[[15,-5],[15,5]],null,false,[9.5,0])""")
        ck(r.get('pts') and near(r['pts'][1][0], 15) and near(r['pts'][1][1], 0),
           "EXTEND (0,0)-(10,0) to the line x=15 lands the end on (15,0) -> %s" % (r.get('pts') or r))
        ck(near(r.get('added'), 5), "and reports 5.0 m added (%s)" % r.get('added'))
        ck(near(r['pts'][0][0], 0) and near(r['pts'][0][1], 0),
           "and the far end is untouched")

        r = await page.evaluate("""()=>window.__a3dExtendBulged(
            [[0,0],[10,0]],null,false,[[15,-5],[15,5]],null,false,[0.5,0])""")
        ck('error' in r, "EXTEND picked at the OTHER end refuses - the boundary is behind it (%s)"
           % r.get('error'))

        r = await page.evaluate("""()=>window.__a3dExtendBulged(
            [[0,0],[10,0],[10,10],[0,10]],null,true,[[15,-5],[15,5]],null,false,[9.5,0])""")
        ck('error' in r, "EXTEND refuses a closed loop (%s)" % r.get('error'))

        # V91 replaced the straight-only bimBreakPolyline with the bulged one and DELETED it, so
        # these checks now drive __a3dBreakBulged -- the function the app actually runs. The
        # claims are unchanged; testing a function nothing calls is a false assurance, which the
        # V85 lesson rates as worse than no check at all.
        r = await page.evaluate("""()=>window.__a3dBreakBulged(
            [[0,0],[10,0]],null,false,[3,0],[7,0])""")
        ok = (r.get('a') and r.get('b')
              and near(r['a']['pts'][1][0], 3) and near(r['b']['pts'][0][0], 7)
              and len(r['a']['pts']) == 2 and len(r['b']['pts']) == 2)
        ck(ok, "BREAK (0,0)-(10,0) at x=3 and x=7 gives 0-3 and 7-10 -> %s | %s"
           % (r['a']['pts'] if r.get('a') else None, r['b']['pts'] if r.get('b') else None))
        removed = await page.evaluate("""(r)=>10
            -window.__a3dBulgedLength(r.a.pts,r.a.bulges,false)
            -window.__a3dBulgedLength(r.b.pts,r.b.bulges,false)""", r) if ok else None
        ck(removed is not None and near(removed, 4),
           "and the two pieces account for 4.0 m less than the original (%s)" % removed)

        r = await page.evaluate("""()=>window.__a3dBreakBulged(
            [[0,0],[10,0]],null,false,[4,0],null)""")
        ck(r.get('a') and near(r['a']['pts'][1][0], 4) and near(r['b']['pts'][0][0], 4),
           "BREAKATPOINT at x=4 splits in place -> %s | %s"
           % (r['a']['pts'] if r.get('a') else None, r['b']['pts'] if r.get('b') else None))
        kept = await page.evaluate("""(r)=>window.__a3dBulgedLength(r.a.pts,r.a.bulges,false)
            +window.__a3dBulgedLength(r.b.pts,r.b.bulges,false)""", r) if r.get('a') else None
        ck(kept is not None and near(kept, 10), "removing nothing: the halves still measure 10 (%s)" % kept)

        r = await page.evaluate("""()=>window.__a3dBreakBulged(
            [[0,0],[10,0]],null,false,[0,0],null)""")
        ck('error' in r, "BREAK at the very start refuses rather than making a zero-length wall (%s)"
           % r.get('error'))

        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[10,0]],null,false,'delta',2.5,[9.9,0])""")
        ck(r.get('pts') and near(r['pts'][1][0], 12.5) and near(r.get('length'), 12.5),
           "LENGTHEN delta +2.5 at the far end -> end at x=12.5 (%s)" % (r.get('pts') or r))
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[10,0]],null,false,'total',4,[9.9,0])""")
        ck(r.get('pts') and near(r['pts'][1][0], 4), "LENGTHEN total 4 -> end at x=4")
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[10,0]],null,false,'percent',150,[9.9,0])""")
        ck(r.get('pts') and near(r['pts'][1][0], 15), "LENGTHEN percent 150 -> end at x=15")
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[10,0]],null,false,'delta',2.5,[0.1,0])""")
        ck(r.get('pts') and near(r['pts'][0][0], -2.5),
           "LENGTHEN picked at the START moves the START (-2.5) (%s)" % (r.get('pts') or r))
        r = await page.evaluate("""()=>window.__a3dLengthenBulged(
            [[0,0],[5,0],[10,0]],null,false,'delta',-7,[9.9,0])""")
        ck('error' in r,
           "LENGTHEN refuses to shorten past the previous vertex instead of eating it (%s)"
           % r.get('error'))

        r = await page.evaluate("""()=>window.__a3dChamferPolylines(
            [[0,0],[10,0]],false,[[10,0],[10,10]],false,2,3)""")
        ok = (r.get('chamfer')
              and near(r['chamfer'][0][0], 8) and near(r['chamfer'][0][1], 0)
              and near(r['chamfer'][1][0], 10) and near(r['chamfer'][1][1], 3))
        ck(ok, "CHAMFER 2 and 3 on a right-angle corner cuts to (8,0) and (10,3) -> %s"
           % (r.get('chamfer') or r))
        ck(r.get('a') and near(r['a'][1][0], 8) and r.get('b') and near(r['b'][0][1], 3),
           "and both walls are pulled back to the chamfer ends")
        r = await page.evaluate("""()=>window.__a3dChamferPolylines(
            [[0,0],[10,0]],false,[[0,5],[10,5]],false,2,2)""")
        ck('error' in r, "CHAMFER refuses parallel walls (%s)" % r.get('error'))
        r = await page.evaluate("""()=>window.__a3dChamferPolylines(
            [[0,0],[10,0]],false,[[10,0],[10,10]],false,0,2)""")
        ck('error' in r, "CHAMFER refuses a zero distance and names Fillet (%s)" % r.get('error'))
        r = await page.evaluate("""()=>window.__a3dChamferPolylines(
            [[0,0],[10,0]],false,[[10,0],[10,10]],false,40,2)""")
        ck('error' in r, "CHAMFER refuses a distance longer than the wall (%s)" % r.get('error'))

        p = await page.evaluate("()=>window.__a3dScalePoint([4,6],[2,2],3)")
        ck(near(p[0], 8) and near(p[1], 14), "SCALE point (4,6) about (2,2) by 3 -> (8,14) %s" % p)

        L = await page.evaluate("()=>window.__a3dPolyLength([[0,0],[3,0],[3,4]],false)")
        ck(near(L, 7), "polyline length 3+4 = 7 (%s)" % L)

        # ---------------------------------------------------------------- 2. palette offers them
        print("\n-- 2. every Phase 87 command is offered by the command line and supported")
        acts = ['extend', 'break', 'breakat', 'lengthen', 'chamfer', 'fillet', 'scale',
                'rotate', 'arrayRect', 'arrayPolar', 'align', 'join']
        sup = await page.evaluate(
            "(acts)=>{const o={};acts.forEach(a=>{o[a]=!!window.__a3dCmdSupported(a);});return o;}",
            acts)
        ck(all(sup.values()), "every new act is supported (%s)"
           % [k for k, v in sup.items() if not v])

        await page.keyboard.press('Control+k')
        await page.wait_for_timeout(350)
        await page.keyboard.type('EXTEND')
        await page.wait_for_timeout(250)
        rows = await page.evaluate(
            "()=>[...document.querySelectorAll('.a3d-cmdrow')].map(r=>r.textContent.trim())")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        ck(any(r.startswith('EXTEND') for r in rows),
           "typing EXTEND offers the EXTEND row (%s)" % rows[:3])

        for name in ('BREAK', 'LENGTHEN', 'CHAMFER', 'SCALE', 'ROTATE', 'JOIN'):
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(280)
            await page.keyboard.type(name)
            await page.wait_for_timeout(200)
            rows = await page.evaluate(
                "()=>[...document.querySelectorAll('.a3d-cmdrow')].map(r=>r.textContent.trim())")
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(180)
            ck(any(r.split(' ')[0] == name or r.startswith(name) for r in rows),
               "typing %s offers it (%s)" % (name, rows[:2] or 'nothing'))

        # ---------------------------------------------------------------- 3. EXTEND end to end
        print("\n-- 3. EXTEND, driven through the command line, measured on the model")
        await reset_model(page)
        target = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        bound = await page.evaluate("()=>window.__a3dWall([[15,-5],[15,5]],0.3,3,'center',false)")
        await page.wait_for_timeout(300)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", bound)
        await palette_run(page, 'EXTEND')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'extend',
           "EXTEND from the command line starts the extend pick (%s)"
           % (st['sk'] and st['sk']['tool']))
        prompt = await page.evaluate("()=>window.__a3dPrompt()")
        ck('Extend' in prompt, "and the command line prompts for the end to extend (%r)" % prompt)
        await page.evaluate("()=>window.__a3dPlacePoint(9.5,0)")
        await page.wait_for_timeout(400)
        cl = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", target)
        ck(near(cl[1][0], 15) and near(cl[1][1], 0),
           "the wall now ends at the boundary, (15,0) -> %s" % cl)
        thick = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.thickness", target)
        ck(near(thick, 0.3), "and it is still the same wall: thickness 0.3 (%s)" % thick)

        # ---------------------------------------------------------------- 4. BREAK end to end
        print("\n-- 4. BREAK, and the prompt that has to agree with it")
        await reset_model(page)
        w = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", w)
        await palette_run(page, 'BREAK')
        p0 = await page.evaluate("()=>window.__a3dPrompt()")
        ck('first' in p0.lower(), "BREAK asks for the FIRST point first (%r)" % p0)
        await page.evaluate("()=>window.__a3dPlacePoint(3,0)")
        await page.wait_for_timeout(200)
        p1 = await page.evaluate("()=>window.__a3dPrompt()")
        ck('second' in p1.lower(),
           "and asks for the SECOND only while it is waiting for one (%r)" % p1)
        n_before = await page.evaluate("()=>window.__a3dState().objs.length")
        await page.evaluate("()=>window.__a3dPlacePoint(7,0)")
        await page.wait_for_timeout(450)
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['objs'].__len__() == n_before + 1,
           "one wall became two objects (%d -> %d)" % (n_before, len(st['objs'])))
        walls = [o for o in st['objs'] if o.get('bim') and o['bim'].get('type') == 'wall']
        cls = sorted([w2['bim']['centerline'] for w2 in walls], key=lambda c: c[0][0])
        ck(len(cls) == 2 and near(cls[0][1][0], 3) and near(cls[1][0][0], 7),
           "and the piece between x=3 and x=7 is gone -> %s" % cls)
        ck(all(near(w2['bim']['thickness'], 0.3) for w2 in walls),
           "both pieces keep the source wall's thickness")
        p_after = await page.evaluate("()=>window.__a3dPrompt()")
        ck('second' not in p_after.lower(),
           "and the prompt stops asking for a second point once it has acted (%r)" % p_after)

        print("\n   BREAKATPOINT splits without removing anything")
        await reset_model(page)
        w = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", w)
        await palette_run(page, 'BREAKATPOINT')
        await page.evaluate("()=>window.__a3dPlacePoint(4,0)")
        await page.wait_for_timeout(420)
        st = await page.evaluate("()=>window.__a3dState()")
        walls = [o for o in st['objs'] if o.get('bim') and o['bim'].get('type') == 'wall']
        total = sum(abs(w2['bim']['centerline'][-1][0] - w2['bim']['centerline'][0][0])
                    for w2 in walls)
        ck(len(walls) == 2 and near(total, 10),
           "two walls, total length still 10 -> %d walls, %.4f" % (len(walls), total))

        # ---------------------------------------------------------------- 5. LENGTHEN
        print("\n-- 5. LENGTHEN through its dialog")
        await reset_model(page)
        w = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", w)
        await palette_run(page, 'LENGTHEN')
        await page.evaluate("()=>window.__a3dPlacePoint(9.8,0)")
        await page.wait_for_timeout(350)
        has_dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        ck(has_dlg, "clicking the end opens the Lengthen dialog")
        await dlg_ok(page, {'v': 5})
        cl = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", w)
        ck(near(cl[1][0], 15), "delta +5 puts the picked end at x=15 -> %s" % cl)

        # ---------------------------------------------------------------- 6. CHAMFER
        print("\n-- 6. CHAMFER builds the bevel as a real wall")
        await reset_model(page)
        a = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        b = await page.evaluate("()=>window.__a3dWall([[10,0],[10,10]],0.3,3,'center',false)")
        await page.wait_for_timeout(300)
        await page.evaluate("([x,y])=>window.__a3dSelectPair(x,y)", [a, b])
        n_before = await page.evaluate("()=>window.__a3dState().objs.length")
        await palette_run(page, 'CHAMFER')
        has_dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        ck(has_dlg, "CHAMFER from the command line opens its dialog")
        await dlg_ok(page, {'d1': 2, 'd2': 3})
        st = await page.evaluate("()=>window.__a3dState()")
        ck(len(st['objs']) == n_before + 1,
           "a third wall exists for the bevel (%d -> %d)" % (n_before, len(st['objs'])))
        ca = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", a)
        cb = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", b)
        ck(near(ca[1][0], 8) and near(cb[0][1], 3),
           "and both walls are cut back to (8,0) and (10,3) -> %s %s" % (ca, cb))
        bevel = [o for o in st['objs']
                 if o.get('bim') and o['bim'].get('type') == 'wall'
                 and o['id'] not in (a, b)]
        ck(len(bevel) == 1 and near(bevel[0]['bim']['thickness'], 0.3),
           "the bevel inherits the source wall's thickness (%s)"
           % (bevel[0]['bim']['thickness'] if bevel else None))

        # ---------------------------------------------------------------- 7. SCALE
        print("\n-- 7. SCALE moves geometry and leaves BIM parameters alone")
        await reset_model(page)
        w = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", w)
        await palette_run(page, 'SCALE')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'scale', "SCALE starts a base-point pick")
        await page.evaluate("()=>window.__a3dPlacePoint(0,0)")
        await page.wait_for_timeout(350)
        await dlg_ok(page, {'k': 2})
        snap = await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", w)
        cl = snap['bim']['centerline']
        ck(near(cl[1][0], 20) and near(cl[0][0], 0),
           "scale 2 about (0,0) doubles the centerline -> %s" % cl)
        ck(near(snap['bim']['thickness'], 0.3),
           "and the wall thickness is UNCHANGED at 0.3 (%s) - it is a type parameter, not geometry"
           % snap['bim']['thickness'])
        ck(near(snap['bim']['height'], 3),
           "and the height is unchanged at 3 (%s)" % snap['bim']['height'])

        # ---------------------------------------------------------------- 8. FILLET r0
        print("\n-- 8. FILLET at radius 0 is the square corner, and says so")
        await reset_model(page)
        a = await page.evaluate("()=>window.__a3dWall([[0,0],[8,0]],0.3,3,'center',false)")
        b = await page.evaluate("()=>window.__a3dWall([[10,2],[10,10]],0.3,3,'center',false)")
        await page.wait_for_timeout(300)
        await page.evaluate("([x,y])=>window.__a3dSelectPair(x,y)", [a, b])
        await palette_run(page, 'FILLET')
        # V89 gave FILLET a radius, so it now asks for one the way AutoCAD does. The CLAIM this
        # check makes is unchanged -- radius 0 is the square corner -- but the command has to be
        # driven through its dialog to make it. Amended here rather than weakened, because a
        # check that stopped completing the command would pass on a FILLET that did nothing.
        ck(await page.evaluate("()=>!!document.querySelector('.a3d-dlg')"),
           "FILLET asks for a radius (V89)")
        await dlg_ok(page, {'r': 0})
        ca = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", a)
        cb = await page.evaluate("(id)=>window.__a3dObjSnapshot(id).bim.centerline", b)
        ck(near(ca[1][0], 10) and near(ca[1][1], 0) and near(cb[0][0], 10) and near(cb[0][1], 0),
           "both ends meet at the corner (10,0) -> %s %s" % (ca, cb))

        # ---------------------------------------------------------------- 9. typed coordinates
        print("\n-- 9. the typed-coordinate class bug: a typed point has to ACT, not just land")
        await reset_model(page)
        w = await page.evaluate("()=>window.__a3dWall([[1,1],[4,1]],0.3,3,'center',false)")
        await page.wait_for_timeout(250)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", w)
        n_before = await page.evaluate("()=>window.__a3dState().objs.length")
        await palette_run(page, 'MIRROR')
        st = await page.evaluate("()=>window.__a3dState()")
        ck(st['sk'] and st['sk']['tool'] == 'mirror', "MIRROR starts its two-point pick")
        ok1 = await page.evaluate("()=>window.__a3dTypedPoint('0,-5')")
        ok2 = await page.evaluate("()=>window.__a3dTypedPoint('0,5')")
        await page.wait_for_timeout(450)
        n_after = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(ok1 and ok2, "both coordinates parse and are accepted")
        ck(n_after == n_before + 1,
           "and the mirror actually ran from typed coordinates alone (%d -> %d)"
           % (n_before, n_after))
        st = await page.evaluate("()=>window.__a3dState()")
        cls = [o['bim']['centerline'] for o in st['objs']
               if o.get('bim') and o['bim'].get('type') == 'wall']
        copy = [c for c in cls if c[0][0] < 0]
        # (1,1)-(4,1) reflected in the line x=0 is (-1,1)-(-4,1): every x negated, z untouched.
        ck(len(copy) == 1
           and near(copy[0][0][0], -1) and near(copy[0][0][1], 1)
           and near(copy[0][1][0], -4) and near(copy[0][1][1], 1),
           "the copy is the reflection in x=0, (-1,1)-(-4,1) -> %s" % cls)

        print("   and a typed coordinate still completes the two-point drawing tools")
        await reset_model(page)
        await palette_run(page, 'RECTANG')
        await page.evaluate("()=>window.__a3dTypedPoint('0,0')")
        await page.evaluate("()=>window.__a3dTypedPoint('4,3')")
        await page.wait_for_timeout(400)
        n = await page.evaluate("()=>window.__a3dState().objs.length")
        ck(n >= 1, "RECTANG from two typed coordinates made an object (%d)" % n)
        sk_after = await page.evaluate("()=>window.__a3dState().sk")
        ck(sk_after is None, "and the tool finished rather than collecting a third point")

        # ---------------------------------------------------------------- 10. refusals in the app
        print("\n-- 10. the commands refuse cleanly when their preconditions are not met")
        await reset_model(page)
        await page.evaluate("()=>window.__a3dSelectFor([])")
        ran = await page.evaluate("()=>window.__a3dRunCmd('extend')")
        st = await page.evaluate("()=>window.__a3dState()")
        ck(ran and (st['sk'] is None),
           "EXTEND with no boundary selected does not start a pick it cannot finish")
        ran = await page.evaluate("()=>window.__a3dRunCmd('chamfer')")
        has_dlg = await page.evaluate("()=>!!document.querySelector('.a3d-dlg')")
        ck(ran and not has_dlg, "CHAMFER with no pair selected opens no dialog")

        # ---------------------------------------------------------------- 11. hygiene
        print("\n-- 11. hygiene")
        audit = await page.evaluate("()=>window.__a3dShellAudit()")
        bad = [k for k, v in (audit or {}).items()
               if isinstance(v, list) and v] if isinstance(audit, dict) else []
        ck(not bad, "V80 shell audit is clean (%s)" % (bad or 'clean'))
        ck(not errs, "no uncaught page errors (%s)" % (errs[:3] or 'none'))

        passed = ck.n - len(ck.failed)
        print("\n%d/%d checks passed" % (passed, ck.n))
        print("RESULT: %s" % ('PASS' if not ck.failed else 'FAIL'))
        if ck.failed:
            print("FAILURES:")
            for f in ck.failed:
                print("  - " + f)
        await browser.close()
        return 1 if ck.failed else 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
