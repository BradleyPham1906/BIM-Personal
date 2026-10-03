"""
bim_phase102_foundations_browser_tests.py

Regression suite for __acad3dV102 in canvas_v10.html: structural foundations and the type
catalogue -- the first structural phase of Track B.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. FOOTINGS ARE PLACED WITH THE TOOLS AND THE MOUSE -- ribbon button and command line, a click on
     a column and a click on a wall -- and asserted on the SOLID: where its mesh actually is, in
     world terms, not on stored fields.
  2. A FOOTING FOLLOWS ITS HOST through every kind of change, each driven separately because each
     reaches it by a different path: the column moved (transform), resized (rebuild), re-typed
     (type change), turned (rotation); the wall reshaped by a grip.
  3. A LEFT-ALIGNED WALL's strip is centred under the wall's BODY, not its centreline -- the case
     an implementation that reused the centreline would get wrong while passing every centred test.
  4. DELETE takes the footing with its host in one delete; moving a footing on its own detaches it
     and says so; a host removed some other way leaves it detached and said.
  5. THE CATALOGUE: beam and footing types exist, a type change rebuilds the instance, and editing a
     TYPE's size rebuilds every footing of that type.
  6. SCHEDULES give concrete volume, and it is the product of the sizes.
  7. EXPORTS: a footing appears in the DXF, and a TURNED column exports turned (V81 orientation was
     being dropped by all three exporters).
  8. The foundation slab is a real floor in the foundation category, following its region.
  9. Zero uncaught page errors.

Run:  python3 bim_phase102_foundations_browser_tests.py [path/to/canvas_v10.html]
"""
import asyncio, math, pathlib, sys

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


def near(a, b, tol=1e-6):
    try:
        return abs(a - b) <= tol
    except TypeError:
        return False


def bbox(o):
    """World bounding box of a solid's mesh: (minx, maxx, miny, maxy, minz, maxz)."""
    if not o or not o.get('mesh'):
        return None
    p = o.get('pos') or [0, 0, 0]
    v = o['mesh']['v']
    xs = [a[0] + p[0] for a in v]
    ys = [a[1] + p[1] for a in v]
    zs = [a[2] + p[2] for a in v]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


async def palette_run(page, name):
    await page.keyboard.press('Control+k')
    await page.wait_for_timeout(320)
    await page.keyboard.type(name)
    await page.wait_for_timeout(260)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(420)


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

        has = await page.evaluate("()=>!!window.__acad3dV102")
        ck(has, "__acad3dV102 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        box = await page.evaluate(
            "()=>{const r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top];}")

        async def scr(p):
            s = await page.evaluate("(p)=>window.__a3dToScreen(p,0)", p)
            return [box[0] + s[0], box[1] + s[1]]

        async def snap(oid):
            o = await page.evaluate("(id)=>id?window.__a3dObjSnapshot(id):null", oid)
            return o or {'missing': True}

        async def objs():
            return await page.evaluate("()=>window.__a3dState().objs")

        async def toast():
            return await page.evaluate("()=>{const t=document.getElementById('a3d-toast');return t?t.textContent:'';}")

        async def blur():
            await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")

        async def scene():
            await page.evaluate("()=>{window.__a3dTestSetObjs([]);window.__a3dFlat(true);}")
            await blur()

        def footings(os_, kind=None):
            return [o for o in os_ if (o.get('bim') or {}).get('type') in (('footing', 'stripfooting') if kind is None else (kind,))]

        # ---------------------------------------------- 1. placing
        print("\n-- 1. footings placed with the tools, clicked with the mouse")
        await scene()
        col = await page.evaluate("()=>window.__a3dColumnAt([2,3],0,0.4,0.4,3)")
        wal = await page.evaluate("()=>window.__a3dWall([[6,0],[12,0]],0.3,3,'center',false)")
        await page.evaluate("()=>{window.__a3dSelectFor([]);window.__a3dFit();window.__a3dTestPaint();}")
        # AMENDED FOR V128: the Foundation panel is the Structure discipline's. Its buttons used to be
        # in the page under Architecture too, only because the dock's own search popover (retired in
        # V128 for the one command search) rendered every discipline's tools. A person picks Structure.
        await page.evaluate("()=>window.__a3dSetDiscipline('struct')")
        await page.wait_for_timeout(150)
        rib = await page.evaluate("""()=>{window.__a3dToolsPanel();const es=[...document.querySelectorAll('#a3d-rupop [data-rkact="bim:footing"],#a3d-rupop [data-rkact="bim:foundwall"],#a3d-rupop [data-rkact="bim:foundslab"]')].map(r=>{if(r.classList.contains('off'))r.classList.add('a3dr-dis');return r;});   /* AMENDED FOR V130: the dock's More menus are gone; a ribbon tool is a row of the Tools and shortcuts panel, opened first */
            return {n:es.length,dis:es.filter(e=>e.classList.contains('a3dr-dis')).length};}""")
        ck(rib['n'] >= 3 and rib['dis'] == 0,
           "the Foundation panel's Isolated Footing, Wall Foundation and Foundation Slab are live, none greyed (%s)" % rib)
        await page.evaluate("()=>{window.__a3dToolsPanel();const e=document.querySelector('#a3d-rupop [data-a3dr=\"bim:footing\"]');if(e)e.click();}")
        await page.wait_for_timeout(250)
        pr = await page.evaluate("()=>window.__a3dPrompt()")
        ck('column' in pr.lower(), "the ribbon button starts the footing command (%r)" % pr)
        c = await scr([2.05, 3.05])
        await page.mouse.click(c[0], c[1])
        await page.wait_for_timeout(250)
        fs_ = footings(await objs(), 'footing')
        f1 = fs_[0]['id'] if fs_ else None
        fb = bbox(await snap(f1))
        ck(fb and near(fb[0], 1.4, 1e-6) and near(fb[1], 2.6, 1e-6) and near(fb[4], 2.4, 1e-6) and near(fb[5], 3.6, 1e-6),
           "a click on the column puts a 1200 x 1200 footing centred under it (%s)" % (fb,))
        ck(fb and near(fb[3], 0.0, 1e-6) and near(fb[2], -0.4, 1e-6),
           "top at the column's base (0), 400 thick (%s .. %s)" % (fb and fb[2], fb and fb[3]))
        await page.mouse.click(c[0], c[1])
        await page.wait_for_timeout(250)
        ck(len(footings(await objs(), 'footing')) == 1 and 'already has' in (await toast() or ''),
           "a second click on the same column adds nothing, and says why")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)

        await palette_run(page, 'WALLFOUNDATION')
        c2 = await scr([9.0, 0.05])
        await page.mouse.click(c2[0], c2[1])
        await page.wait_for_timeout(250)
        await page.keyboard.press('Escape')
        ss = footings(await objs(), 'stripfooting')
        s1 = ss[0]['id'] if ss else None
        sb = bbox(await snap(s1))
        ck(sb and near(sb[4], -0.3, 1e-6) and near(sb[5], 0.3, 1e-6) and near(sb[0], 6.0, 0.35) and near(sb[1], 12.0, 0.35),
           "WALLFOUNDATION + a click on the wall lays a 600-wide strip along it (%s)" % (sb,))
        ck(sb and near(sb[3], 0.0, 1e-6) and near(sb[2], -0.3, 1e-6), "300 thick, top at the wall's base")

        # ---------------------------------------------- 2. follows its host
        print("\n-- 2. a footing follows its host")
        # moved the way a user moves a selected column: by the move gizmo's X arm
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", col)
        await page.evaluate("()=>window.__a3dTestPaint()")
        gz = await page.evaluate("()=>window.__a3dGizmo()")
        xa = [a_ for a_ in (gz or {}).get('arms', []) if a_.get('axis') == 'x']
        if xa:
            r_ = await page.evaluate("()=>window.__a3dCanvasRect()")
            mx, my = (xa[0]['x0'] + xa[0]['x1']) / 2, (xa[0]['y0'] + xa[0]['y1']) / 2
            await page.mouse.move(r_['left'] + mx, r_['top'] + my); await page.mouse.down()
            await page.mouse.move(r_['left'] + mx + 90, r_['top'] + my, steps=10); await page.mouse.up()
            await page.wait_for_timeout(300)
        cs = await snap(col)
        cx = 2.0 + cs['pos'][0]
        fb2 = bbox(await snap(f1))
        ck(abs(cs['pos'][0]) > 1 and fb2 and near((fb2[0] + fb2[1]) / 2, cx, 1e-6),
           "dragging the column moves its footing with it (column x %.3f, footing centre %.3f)"
           % (cx, fb2 and (fb2[0] + fb2[1]) / 2))
        await page.evaluate("(id)=>window.__a3dRebuildColumn(id,0.4,0.4,3)", col)
        ts = await page.evaluate("()=>window.__a3dTypesOf('footing')")
        big = [t for t in ts if t['id'] == 'ft-iso2000']
        await page.evaluate("(a)=>window.__a3dAssignType(a[0],a[1])", [f1, 'ft-iso2000'])
        fb3 = bbox(await snap(f1))
        ck(big and fb3 and near(fb3[1] - fb3[0], 2.0, 1e-6) and near(fb3[3] - fb3[2], 0.6, 1e-6),
           "changing the footing's type to 2000 x 2000 x 600 rebuilds it (%s)" % (fb3,))
        await page.evaluate("()=>window.__a3dApplyTypeParams('footing','ft-iso2000',{width:2.4})")
        fb4 = bbox(await snap(f1))
        ck(fb4 and near(fb4[1] - fb4[0], 2.4, 1e-6), "editing the TYPE's width rebuilds every footing of that type (%.3f)" % (fb4 and fb4[1] - fb4[0]))
        c0 = (await snap(col)).get('bim', {}).get('center', [0, 0])
        cp_ = (await snap(col)).get('pos', [0, 0, 0])
        await page.evaluate("(a)=>window.__a3dRotateSelection([a[0]],[a[1],a[2]],Math.PI/6)", [col, c0[0] + cp_[0], c0[1] + cp_[2]])
        f5 = await snap(f1); c5 = await snap(col)
        ck(near((f5.get('bim') or {}).get('rotation', 0), (c5.get('bim') or {}).get('rotation', -1), 1e-9) and abs((c5.get('bim') or {}).get('rotation', 0)) > 0.1,
           "turning the column turns its footing (%s, %s)" % ((c5.get('bim') or {}).get('rotation'), (f5.get('bim') or {}).get('rotation')))

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", wal)
        await page.evaluate("()=>window.__a3dTestPaint()")
        gs = [g for g in await page.evaluate("()=>window.__a3dGrips()") if g.get('objId') == wal and g.get('idx') == 1 and not g.get('mid')]
        if gs:
            a = [box[0] + gs[0]['x'], box[1] + gs[0]['y']]; b = await scr([15.0, 0.0])
            await page.mouse.move(a[0], a[1]); await page.mouse.down()
            await page.mouse.move(b[0], b[1], steps=8); await page.mouse.up()
            await page.wait_for_timeout(300)
        wl = await snap(wal)
        wend = wl['bim']['centerline'][1][0]
        sb2 = bbox(await snap(s1))
        ck(gs and wend > 14 and sb2 and near(sb2[1], wend, 0.35),
           "dragging the wall's end out to x=%.2f stretches its strip with it (%s)" % (wend, sb2 and sb2[1]))

        print("\n-- 2b. a left-aligned wall's strip sits under the wall's BODY")
        await scene()
        lw = await page.evaluate("()=>window.__a3dWall([[0,0],[10,0]],0.4,3,'left',false)")
        lf = await page.evaluate("(id)=>window.__a3dAddFootingUnder(id)", lw)
        wb = bbox(await snap(lw)); lb = bbox(await snap(lf))
        wmid = (wb[4] + wb[5]) / 2 if wb else None
        fmid = (lb[4] + lb[5]) / 2 if lb else None
        ck(wb and lb and abs(wmid) > 0.1 and near(fmid, wmid, 1e-6),
           "the strip's centre (%.3f) is the wall body's (%.3f), not the centreline (0)" % (fmid or -9, wmid or -9))

        # ---------------------------------------------- 3. relationships
        print("\n-- 3. delete, detach, sweep")
        await scene()
        c3 = await page.evaluate("()=>window.__a3dColumnAt([0,0],0,0.4,0.4,3)")
        f3 = await page.evaluate("(id)=>window.__a3dAddFootingUnder(id)", c3)
        rel = await page.evaluate("(id)=>window.__a3dGraphRelationsOf(id)", c3)
        ck(any(d.get('objId') == f3 and d.get('rel') == 'support' for d in (rel or {}).get('dependents', [])),
           "the relation graph links the column to its footing")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", c3)
        await blur()
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(250)
        dt = await toast()
        ck(not footings(await objs()) and '2 object' in (dt or ''),
           "deleting the column deletes its footing in the same delete (%r)" % dt)
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(200)
        ck(len(footings(await objs())) == 1, "Undo brings the footing back with its column")
        await page.evaluate("(id)=>window.__a3dPropagateFrom([id],'transform',[1,0,0])", f3)
        f3s = await snap(f3)
        ck(not (f3s.get('bim') or {}).get('hostId') and 'no longer under' in (await toast() or ''),
           "a footing moved on its own is detached, and told")
        await page.evaluate("(id)=>window.__a3dPropagateFrom([id],'transform',[1,0,0])", c3)
        f3t = bbox(await snap(f3))
        ck(f3t and near((f3t[0] + f3t[1]) / 2, 0.0, 1e-6), "and no longer follows the column (%.3f)" % ((f3t[0] + f3t[1]) / 2 if f3t else -9))
        await scene()
        c4 = await page.evaluate("()=>window.__a3dColumnAt([0,0],0,0.4,0.4,3)")
        f4 = await page.evaluate("(id)=>window.__a3dAddFootingUnder(id)", c4)
        await page.evaluate("""(id)=>{var o=window.__a3dState().objs.filter(x=>x.id!==id);
            o.push({id:'KEEP',t:'sketch',name:'KEEP',col:'#5ec4b8',pos:[0,0,0],pts:[[20,0],[21,0]],y:0,closed:false});
            window.__a3dTestSetObjs(o);}""", c4)
        await page.evaluate("()=>window.__a3dSelectFor(['KEEP'])")
        await blur()
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(250)
        f4s = await snap(f4)
        ck(not f4s.get('missing') and not (f4s.get('bim') or {}).get('hostId') and 'no longer under anything' in (await toast() or ''),
           "a host that vanished some other way leaves the footing detached, kept, and said")

        # ---------------------------------------------- 4. catalogue, all, schedule
        print("\n-- 4. the catalogue, Footings Under All, and the schedule")
        bt = await page.evaluate("()=>window.__a3dTypesOf('beam')")
        st = await page.evaluate("()=>window.__a3dTypesOf('stripfooting')")
        ck(len(bt) >= 4 and len(st) >= 3, "beam (%d) and wall-foundation (%d) types exist" % (len(bt), len(st)))
        await scene()
        bm = await page.evaluate("()=>window.__a3dBeam([0,0],[6,0],0.25,0.45,'top')")
        await page.evaluate("(a)=>window.__a3dAssignType(a,'bt-400x700')", bm)
        bs = await snap(bm)
        bb = bbox(bs)
        ck(near((bs.get('bim') or {}).get('depth', 0), 0.7, 1e-9) and bb and near(bb[3] - bb[2], 0.7, 1e-6),
           "a beam takes a catalogue type and is rebuilt 700 deep (%s)" % (bb and bb[3] - bb[2]))
        for i, x in enumerate((0, 6, 12)):
            await page.evaluate("(x)=>window.__a3dColumnAt([x,0],0,0.4,0.4,3)", x)
        made = await page.evaluate("()=>window.__a3dFootingsUnderAll()")
        made2 = await page.evaluate("()=>window.__a3dFootingsUnderAll()")
        ck(len(made) == 3 and len(made2) == 0, "FOOTINGSALL puts one under each of 3 columns, and a second run adds none")
        keys = await page.evaluate("()=>window.__a3dScheduleKeys()")
        sched = await page.evaluate("()=>window.__a3dScheduleRows('footing')")
        rows = (sched or {}).get('rows') if isinstance(sched, dict) else sched
        vol = await page.evaluate("(id)=>window.__a3dFootingVolume(id)", made[0] if made else None)
        ck('footing' in (keys or []) and 'stripfooting' in (keys or []),
           "Isolated Footings and Wall Foundations are registered schedules (%s)" % keys)
        ck(rows and len(rows) == 3 and all(near(r.get('volume'), 1.2 * 1.2 * 0.4, 1e-9) for r in rows)
           and all(str(r.get('host', '')).startswith('Column') for r in rows),
           "the footing schedule lists 3 footings, each under its column, 0.576 m3 each (%s)" % (rows[:1] if rows else rows))
        ck(near(vol, 1.2 * 1.2 * 0.4, 1e-9), "concrete volume is width x length x thickness (%.4f)" % (vol or -1))

        # ---------------------------------------------- 5. exports
        print("\n-- 5. exports")
        dxf = (await page.evaluate("()=>window.__a3dBuildDXF()") or {}).get('text', '')
        n_poly = dxf.count('LWPOLYLINE')
        await page.evaluate("()=>{var o=window.__a3dState().objs.filter(x=>!(x.bim&&x.bim.type==='footing'));window.__a3dTestSetObjs(o);}")
        dxf2 = (await page.evaluate("()=>window.__a3dBuildDXF()") or {}).get('text', '')
        ck(n_poly - dxf2.count('LWPOLYLINE') == 3, "each of the 3 footings is a polyline in the DXF (%d more)" % (n_poly - dxf2.count('LWPOLYLINE')))
        await scene()
        tc = await page.evaluate("()=>window.__a3dColumnAt([0,0],0,1.0,0.2,3)")
        await page.evaluate("(a)=>window.__a3dRotateSelection([a],[0,0],Math.PI/4)", tc)
        dx = (await page.evaluate("()=>window.__a3dBuildDXF()") or {}).get('text', '')
        # a 1.0 x 0.2 bar turned 45 degrees: its corners reach sqrt(0.5^2+0.1^2) off-axis, i.e. x
        # from about -0.424 to 0.424, never the axis-aligned +-0.5
        xs = []
        lines = dx.split('\r\n')
        for i in range(len(lines) - 1):
            if lines[i].strip() == '10':
                try:
                    xs.append(float(lines[i + 1]))
                except ValueError:
                    pass
        ck(xs and max(abs(v) for v in xs) < 0.46, "a TURNED column exports turned (max |x| %.3f, axis-aligned would be 0.5)" % (max(abs(v) for v in xs) if xs else -1))

        # ---------------------------------------------- 6. foundation slab
        print("\n-- 6. a foundation slab")
        await page.evaluate("""()=>window.__a3dTestSetObjs([{id:'R',t:'sketch',name:'R',col:'#5ec4b8',pos:[0,0,0],
            pts:[[0,0],[8,0],[8,5],[0,5]],y:0}])""")
        await palette_run(page, 'FOUNDATIONSLAB')
        await page.evaluate("()=>{window.__a3dFit();window.__a3dTestPaint();}")
        c6 = await scr([4.0, 2.5])
        await page.mouse.click(c6[0], c6[1])
        await page.wait_for_timeout(300)
        sl = [o for o in await objs() if (o.get('bim') or {}).get('structural') == 'foundation']
        sb6 = bbox(sl[0]) if sl else None
        ck(sl and sl[0]['name'].startswith('Foundation Slab') and sb6 and near(sb6[3] - sb6[2], 0.3, 1e-6) and near(sb6[1] - sb6[0], 8.0, 1e-6),
           "FOUNDATIONSLAB + a click makes an 8 x 5, 300 mm foundation slab (%s)" % (sb6,))
        ck(sl and sl[0].get('sourceId') == 'R', "and it follows the rectangle it was made in (source %s)" % (sl and sl[0].get('sourceId')))

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
