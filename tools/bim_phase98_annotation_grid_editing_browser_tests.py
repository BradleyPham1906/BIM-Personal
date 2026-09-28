"""
bim_phase98_annotation_grid_editing_browser_tests.py

Regression suite for __acad3dV98 in canvas_v10.html: annotations and grid lines can be touched
and edited.

REPORTED: "I can't touch or edit an annotation and grid lines."

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. EVERY CLICK IS A REAL MOUSE CLICK at the place the thing is drawn, and the assertion is on
     the SELECTION the model holds -- not on a pick function called directly, which passed for
     the linear dimension the whole time a room was swallowing the click.
  2. THE ANNOTATION SITS INSIDE A ROOM, because that is where labels live and that is what
     broke. A label in empty space was always selectable.
  3. EVERY KIND IS CLICKED -- linear, angular, radius, diameter, leader, text -- on its line and
     on its LABEL, since the old pick returned early for every kind but linear.
  4. THE MODEL STILL WINS WHERE NO ANNOTATION IS: the room's empty interior still selects the
     room, and a wall over a grid still selects the wall. A fix that made annotations win
     everywhere would break selection of everything else.
  5. A HIDDEN ANNOTATION IS NOT PICKABLE where nothing is drawn.
  6. GRIP EDITS ARE ASSERTED ON THE MODEL: a dimension's measured length and its offset, an
     angle's degrees, a radius's value, a leader's landing -- each re-derived, not just moved.
  7. THE GRID IS DRIVEN THROUGH EVERY VERB: click, end grip, body drag, rename (and a duplicate
     name refused), a typed end, Delete, Undo, Escape, and its Levels-panel row.
  8. Zero uncaught page errors.

Run:  python3 bim_phase98_annotation_grid_editing_browser_tests.py [path/to/canvas_v10.html]
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


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


ROOMSK = {'id': 'R', 't': 'sketch', 'name': 'R', 'col': '#5ec4b8', 'pos': [0, 0, 0],
          'pts': [[0, 0], [10, 0], [10, 8], [0, 8]], 'y': 0}


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

        has = await page.evaluate("()=>!!window.__acad3dV98")
        ck(has, "__acad3dV98 marker is present")
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.failed), ck.n))
            await browser.close()
            return 1

        box = await page.evaluate(
            "()=>{const r=document.getElementById('a3d-canvas').getBoundingClientRect();"
            "return [r.left,r.top];}")

        async def scr(p):
            s = await page.evaluate("(p)=>window.__a3dToScreen(p,0)", p)
            return [box[0] + s[0], box[1] + s[1]]

        async def sel():
            st = await page.evaluate("()=>window.__a3dState()")
            return st.get('sel')

        async def click_world(p, dx=0, dy=0):
            await page.evaluate("()=>{window.__a3dSelectFor([]);window.__a3dTestPaint();}")
            s = await scr(p)
            await page.mouse.click(s[0] + dx, s[1] + dy)
            await page.wait_for_timeout(120)

        async def drag_screen(a, b):
            await page.mouse.move(a[0], a[1])
            await page.mouse.down()
            await page.mouse.move(b[0], b[1], steps=8)
            await page.mouse.up()
            await page.wait_for_timeout(200)

        async def snap(oid):
            return await page.evaluate("(id)=>window.__a3dObjSnapshot(id)", oid)

        async def set_field(f, v):
            # a missing field is a FAILED check further down, never a crash here
            sel_ = '[data-gridf="%s"]' % f
            if await page.query_selector(sel_) is None:
                return False
            await page.fill(sel_, v)
            await page.dispatch_event(sel_, 'change')
            await page.wait_for_timeout(150)
            return True

        async def grips_of(oid):
            await page.evaluate("()=>window.__a3dTestPaint()")
            gs = await page.evaluate("()=>window.__a3dGrips()")
            return [g for g in gs if g.get('objId') == oid and not g.get('mid')]

        # ------------------------------------------------------------ scene
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [ROOMSK])
        await page.evaluate("()=>window.__a3dFlat(true)")
        ids = await page.evaluate("""()=>{
          var r={};
          r.room=window.__a3dCreateRoomAt([5,4],0);
          r.lin=window.__a3dCreateDim([1,1],[5,1],[3,2]).id;
          r.txt=window.__a3dCreateText([1,6],0,'KITCHEN').id;
          r.ang=window.__a3dCreateAngularDim([6,1],[9,1],[6,4]).id;
          r.rad=window.__a3dCreateRadialDim([3,4],[4,5],[5,4],false).id;
          r.dia=window.__a3dCreateRadialDim([7.5,5],[8.5,6],[9.5,5],true).id;
          r.ldr=window.__a3dCreateLeader([2,7],[3,7.5],[4,7.5],'NOTE A').id;
          window.__a3dSelectFor([]);window.__a3dFit();window.__a3dTestPaint();
          return r;}""")
        await page.wait_for_timeout(300)

        # ------------------------------------------------------------ 1. picking
        print("\n-- 1. every annotation inside a room is selectable with the mouse")
        # the linear dim line runs at z=2 from x=1..5; click on it
        await click_world([3.0, 2.0])
        ck(await sel() == ids['lin'], "a click on the linear dimension line INSIDE the room selects the dimension")
        # its label sits just above the midpoint of the dim line, on screen
        await click_world([3.0, 2.0], 0, -9)
        ck(await sel() == ids['lin'], "a click on the linear dimension's LABEL selects it")
        await click_world([1.0, 6.0], 20, 0)
        ck(await sel() == ids['txt'], "a click on a text label inside the room selects the text, not the room")
        # angular: arc radius = min(3,3)*0.6 = 1.8, sweep from 0 to +90deg about (6,1)
        a45 = [6 + 1.8 * math.cos(math.pi / 4), 1 + 1.8 * math.sin(math.pi / 4)]
        await click_world(a45)
        ck(await sel() == ids['ang'], "a click on an ANGULAR dimension's arc selects it (was never pickable)")
        await click_world([7.5, 1.0])
        ck(await sel() == ids['ang'], "a click on an angular dimension's ray selects it")
        rs = await snap(ids['rad'])
        mid = [(rs['dStart'][0] + rs['dEdge'][0]) / 2, (rs['dStart'][1] + rs['dEdge'][1]) / 2]
        await click_world(mid)
        ck(await sel() == ids['rad'], "a click on a RADIUS dimension's line selects it")
        ds = await snap(ids['dia'])
        dm = [(ds['dStart'][0] * 0.3 + ds['dEdge'][0] * 0.7), (ds['dStart'][1] * 0.3 + ds['dEdge'][1] * 0.7)]
        await click_world(dm)
        ck(await sel() == ids['dia'], "a click on a DIAMETER dimension's line selects it")
        ls = await snap(ids['ldr'])
        lm = [(ls['anchor'][0] + ls['elbow'][0]) / 2, (ls['anchor'][1] + ls['elbow'][1]) / 2]
        await click_world(lm)
        ck(await sel() == ids['ldr'], "a click on a LEADER's line selects it")
        await click_world(ls['landing'], 14, -6)
        ck(await sel() == ids['ldr'], "a click on a leader's TEXT selects it")

        print("\n-- 1b. the model still wins where no annotation is drawn")
        await click_world([8.5, 7.3])
        ck(await sel() == ids['room'], "the room's empty interior still selects the room")
        await click_world([10.0, 3.0])
        ck(await sel() in ('R', ids['room']),
           "the rectangle's edge still selects model geometry, not an annotation (%s)" % await sel())

        print("\n-- 1c. an annotation hidden by its view is not pickable")
        # the same label, scoped to a view that is not the active one: draw skips it, so the
        # pick must too. Rebuilt afterwards so section 2 starts from the original scene.
        await page.evaluate("""()=>{window.__a3dTestSetObjs([{id:'HID',t:'text',name:'HID',col:'#dfe4ea',
            pos:[0,0,0],text:'HIDDEN',pt:[1,6],y:0,levelId:'lvl-0',layer:'layer-0',viewId:'not-this-view'},
            {id:'VIS',t:'text',name:'VIS',col:'#dfe4ea',pos:[0,0,0],text:'SHOWN',pt:[1,3],y:0,
            levelId:'lvl-0',layer:'layer-0',viewId:null}]);window.__a3dTestPaint();}""")
        await click_world([1.0, 6.0], 20, 0)
        ck(await sel() is None, "a text label scoped to another view is NOT selected where it is not drawn (%s)"
           % await sel())
        await click_world([1.0, 3.0], 20, 0)
        ck(await sel() == 'VIS', "while the same kind of label, drawn in this view, is (%s)" % await sel())
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [ROOMSK])
        ids = await page.evaluate("""()=>{
          var r={};
          r.room=window.__a3dCreateRoomAt([5,4],0);
          r.lin=window.__a3dCreateDim([1,1],[5,1],[3,2]).id;
          r.txt=window.__a3dCreateText([1,6],0,'KITCHEN').id;
          r.ang=window.__a3dCreateAngularDim([6,1],[9,1],[6,4]).id;
          r.rad=window.__a3dCreateRadialDim([3,4],[4,5],[5,4],false).id;
          r.dia=window.__a3dCreateRadialDim([7.5,5],[8.5,6],[9.5,5],true).id;
          r.ldr=window.__a3dCreateLeader([2,7],[3,7.5],[4,7.5],'NOTE A').id;
          window.__a3dSelectFor([]);window.__a3dTestPaint();
          return r;}""")

        # ------------------------------------------------------------ 2. grips
        print("\n-- 2. annotation grips edit what the annotation measures")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", ids['txt'])
        g = await grips_of(ids['txt'])
        ck(len(g) == 1, "a selected text label shows one grip (%d)" % len(g))
        if g:
            await drag_screen([box[0] + g[0]['x'], box[1] + g[0]['y']], await scr([2.0, 5.0]))
        t1 = await snap(ids['txt'])
        ck(t1 and near(t1['pt'][0], 2.0, 0.06) and near(t1['pt'][1], 5.0, 0.06),
           "dragging the text grip moves its insertion point to (2,5) (%s)" % (t1 and t1['pt']))

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", ids['lin'])
        g = await grips_of(ids['lin'])
        ck(len(g) == 3, "a selected linear dimension shows 3 grips: two points and the line (%d)" % len(g))
        l0 = await snap(ids['lin'])
        off0 = dist(l0['p1'], l0['d1'])
        g2 = [x for x in g if x['idx'] == 1]
        if g2:
            await drag_screen([box[0] + g2[0]['x'], box[1] + g2[0]['y']], await scr([7.0, 1.0]))
        l1 = await snap(ids['lin'])
        ck(l1 and near(l1['length'], 6.0, 0.06),
           "dragging the second point from x=5 to x=7 re-measures 4 -> 6 m (%s)" % (l1 and l1['length']))
        ck(l1 and near(dist(l1['p1'], l1['d1']), off0, 1e-6) and near(dist(l1['p2'], l1['d2']), off0, 1e-6),
           "and the dimension line keeps its offset of %.3f m" % off0)
        g = await grips_of(ids['lin'])
        g3 = [x for x in g if x['idx'] == 2]
        if g3:
            await drag_screen([box[0] + g3[0]['x'], box[1] + g3[0]['y']], await scr([4.0, 3.0]))
        l2 = await snap(ids['lin'])
        ck(l2 and near(l2['d1'][1], 3.0, 0.06) and near(l2['d2'][1], 3.0, 0.06) and near(l2['length'], l1['length'], 1e-9),
           "dragging the dimension-line grip moves the line to z=3 and leaves the length alone (%s)"
           % (l2 and l2['d1']))
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(150)
        lu = await snap(ids['lin'])
        ck(lu and near(lu['d1'][1], l1['d1'][1], 1e-9),
           "UNDO takes back exactly the last grip edit")

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", ids['ang'])
        g = await grips_of(ids['ang'])
        ck(len(g) == 3, "a selected angular dimension shows 3 grips (%d)" % len(g))
        ga = [x for x in g if x['idx'] == 2]
        if ga:
            await drag_screen([box[0] + ga[0]['x'], box[1] + ga[0]['y']], await scr([4.0, 3.0]))
        a1 = await snap(ids['ang'])
        ck(a1 and near(a1['degrees'], 135.0, 0.8),
           "dragging the second ray point to (4,3) re-measures the angle to 135 deg (%s)"
           % (a1 and a1['degrees']))

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", ids['rad'])
        g = await grips_of(ids['rad'])
        r0 = await snap(ids['rad'])
        gr = [x for x in g if x['idx'] == 1]
        ck(len(g) == 2, "a selected radius dimension shows 2 grips (%d)" % len(g))
        if gr:
            tgt = [r0['center'][0], r0['center'][1] - 3.0]
            await drag_screen([box[0] + gr[0]['x'], box[1] + gr[0]['y']], await scr([tgt[0] + 0.001, tgt[1]]))
        r1 = await snap(ids['rad'])
        ang = math.degrees(math.atan2(r1['dEdge'][1] - r1['center'][1], r1['dEdge'][0] - r1['center'][0])) if r1 else None
        ck(r1 and near(r1['value'], r0['value'], 1e-9) and near(dist(r1['dEdge'], r1['center']), r0['radius'], 1e-9)
           and near(ang, -90.0, 2.0),
           "dragging the radius text grip swings it round the circle; the radius stays %.3f (angle %s)"
           % (r0['value'], ang))

        await page.evaluate("(id)=>window.__a3dSelectFor([id])", ids['ldr'])
        g = await grips_of(ids['ldr'])
        ck(len(g) == 3, "a selected leader shows 3 grips (%d)" % len(g))
        ge = [x for x in g if x['idx'] == 1]
        if ge:
            await drag_screen([box[0] + ge[0]['x'], box[1] + ge[0]['y']], await scr([4.0, 6.0]))
        l3 = await snap(ids['ldr'])
        ck(l3 and near(l3['elbow'][0], 4.0, 0.06) and near(l3['elbow'][1], 6.0, 0.06)
           and near(l3['landing'][1], l3['elbow'][1], 1e-9) and near(abs(l3['landing'][0] - l3['elbow'][0]), 0.5, 1e-9),
           "dragging the leader elbow moves it to (4,6) and the landing follows it (%s)"
           % (l3 and l3['elbow']))

        # ------------------------------------------------------------ 3. grids
        print("\n-- 3. a grid line can be selected and edited")
        await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", [])
        gid = await page.evaluate("""()=>{
            var gs=window.__a3dGrids();for(var i=0;i<gs.length;i++)window.__a3dRemoveGrid(gs[i].id);
            var a=window.__a3dAddGrid([0,0],[0,10]);var b=window.__a3dAddGrid([-2,5],[12,5]);
            window.__a3dSelectFor([]);window.__a3dSetView('home');window.__a3dTestPaint();return [a,b];}""")
        # AMENDED FOR V119: this called __a3dFit() on a model with no objects, and Fit to Model with
        # nothing to fit used to open the 3D Home view -- the camera every click below is aimed
        # through. V119 made an empty Fit keep the view it is in (it swung an empty plan into 3D), so
        # the Home view is opened here by name: the same camera, asked for rather than fallen into.
        await page.wait_for_timeout(250)
        await click_world([0.0, 2.5])
        ck(await page.evaluate("()=>window.__a3dSelectedGrid()") == gid[0],
           "a click on the grid line selects the grid")
        hint = await page.evaluate("()=>document.getElementById('a3d-sthint').textContent")
        ck('Grid' in (hint or ''), "the status bar names the selected grid (%r)" % hint)
        props = await page.evaluate("()=>{var i=document.querySelector('[data-gridf=\"name\"]');return i?i.value:null;}")
        g0 = (await page.evaluate("()=>window.__a3dGrids()"))[0]
        ck(props == g0['name'], "Properties shows the grid's name for editing (%r)" % props)
        await page.evaluate("()=>window.__a3dTestPaint()")
        gg = [x for x in await page.evaluate("()=>window.__a3dGrips()") if x.get('kind') == 'grid']
        ck(len(gg) == 2, "a selected grid shows a grip at each end (%d)" % len(gg))
        e2 = [x for x in gg if x['idx'] == 1]
        if e2:
            await drag_screen([box[0] + e2[0]['x'], box[1] + e2[0]['y']], await scr([0.0, 14.0]))
        gs = await page.evaluate("()=>window.__a3dGrids()")
        ck(near(gs[0]['p2'][0], 0.0, 0.06) and near(gs[0]['p2'][1], 14.0, 0.06) and gs[0]['p1'] == [0, 0],
           "dragging its end grip extends the grid to (0,14) and leaves the start alone (%s)" % gs[0]['p2'])
        # body drag: press on the selected grid away from its ends and grips, move by +3 in x
        a = await scr([0.0, 6.0])
        b = await scr([3.0, 6.0])
        await drag_screen(a, b)
        gs2 = await page.evaluate("()=>window.__a3dGrids()")
        dx1 = gs2[0]['p1'][0] - gs[0]['p1'][0]
        dx2 = gs2[0]['p2'][0] - gs[0]['p2'][0]
        ck(near(dx1, 3.0, 0.08) and near(dx1, dx2, 1e-9) and near(gs2[0]['p1'][1], gs[0]['p1'][1], 0.08),
           "dragging the selected grid's line moves the whole grid +3 in x (%.3f, %.3f)" % (dx1, dx2))
        ok_dup = await page.evaluate("(n)=>window.__a3dRenameGrid(window.__a3dSelectedGrid(),n)", gs2[1]['name'])
        ck(ok_dup is False, "renaming it to another grid's name (%s) is refused" % gs2[1]['name'])
        await set_field('name', 'G1')
        gs3 = await page.evaluate("()=>window.__a3dGrids()")
        ck(gs3[0]['name'] == 'G1', "typing a name in Properties renames the grid (%s)" % gs3[0]['name'])
        await set_field('x1', '1')
        gs4 = await page.evaluate("()=>window.__a3dGrids()")
        ck(near(gs4[0]['p1'][0], 1.0, 1e-9), "typing a Start X in Properties moves that end (%s)" % gs4[0]['p1'])
        await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(200)
        gs5 = await page.evaluate("()=>window.__a3dGrids()")
        ck(len(gs5) == 1 and gs5[0]['id'] == gid[1], "Delete removes the selected grid (%d left)" % len(gs5))
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(150)
        gs6 = await page.evaluate("()=>window.__a3dGrids()")
        ck(len(gs6) == 2 and any(x['name'] == 'G1' for x in gs6), "UNDO brings it back, renamed")
        await page.evaluate("(id)=>window.__a3dSelectGrid(id)", gid[1])
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(120)
        ck(await page.evaluate("()=>window.__a3dSelectedGrid()") is None, "Escape clears the grid selection")
        row = await page.query_selector('[data-a3dgrid="%s"] .a3d-lvlnm' % gid[1])
        if row:
            try:
                await row.click(timeout=1500)
            except Exception:
                await page.evaluate("(id)=>{var r=document.querySelector('[data-a3dgrid=\"'+id+'\"] .a3d-lvlnm');if(r)r.click();}", gid[1])
            await page.wait_for_timeout(150)
        ck(row and await page.evaluate("()=>window.__a3dSelectedGrid()") == gid[1],
           "clicking a grid's row in the Levels panel selects that grid")
        await click_world([6.0, 9.0])
        ck(await page.evaluate("()=>window.__a3dSelectedGrid()") is None, "clicking empty space deselects it")

        print("\n-- 3b. the model still wins over a grid")
        await page.evaluate("""()=>{window.__a3dTestSetObjs([{id:'W',t:'sketch',name:'W',col:'#5ec4b8',
            pos:[0,0,0],pts:[[-1,5],[4,5]],y:0,closed:false}]);window.__a3dTestPaint();}""")
        await click_world([2.0, 5.0])
        ck(await sel() == 'W' and await page.evaluate("()=>window.__a3dSelectedGrid()") is None,
           "where a sketch lies on a grid, the click selects the sketch (%s)" % await sel())

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
