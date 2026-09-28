"""
bim_phase101_room_tags_browser_tests.py

Regression suite for __acad3dV101 in canvas_v10.html: rooms carry their data, and room tags
show it.

THE OWNER'S DIRECTION (V100): go further -- structural, room tagging, site analysis, all three
interleaved, rooms first.

WHY EACH CHECK IS THE ONE THAT WOULD CATCH A REGRESSION:

  1. ROOMS ARE MADE WITH THE ROOM TOOL AND THE MOUSE and numbered on creation, per level.
  2. TAG ROOM IS DRIVEN FROM THE COMMAND PALETTE AND THE RIBBON, and clicked into rooms with the
     mouse. The ribbon button was greyed as unimplemented before this phase; a button that works
     but still looks dead would pass every engine check.
  3. A TAG NEVER DISAGREES WITH ITS ROOM: renaming or renumbering the room -- through the room's
     Properties AND through the tag's -- changes what the tag says. Asserted on the tag's text,
     which is read from the room, not stored.
  4. THE ROOM'S OWN LABEL STEPS ASIDE when tagged: asserted by recording what the canvas actually
     writes, so a room tagged in plan does not say its name twice.
  5. RELATIONSHIPS: the graph links room -> tag; moving the room moves the tag by the same amount;
     deleting the room deletes its tags; Undo brings both back; a tag orphaned any other way is
     swept, and said.
  6. TAG ALL tags exactly the untagged rooms, once.
  7. SCHEDULE AND EXPORT read the same data: the room schedule has the number and department; the
     DXF has the tag's text and no second label under it.
  8. THE LABEL POINT IS INSIDE an L-shaped room.
  9. Persistence across a reload, and zero uncaught page errors.

Run:  python3 bim_phase101_room_tags_browser_tests.py [path/to/canvas_v10.html]
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


def near(a, b, tol=1e-6):
    try:
        return abs(a - b) <= tol
    except TypeError:
        return False


def sk(i, pts, closed=True):
    o = {'id': i, 't': 'sketch', 'name': i, 'col': '#5ec4b8', 'pos': [0, 0, 0], 'pts': pts, 'y': 0}
    if not closed:
        o['closed'] = False
    return o


def inside(pt, poly):
    x, z = pt
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, zi = poly[i]
        xj, zj = poly[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi:
            c = not c
        j = i
    return c


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

        has = await page.evaluate("()=>!!window.__acad3dV101")
        ck(has, "__acad3dV101 marker is present")
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
            return o or {'missing': True, 'pts': [[0, 0]], 'pos': [0, 0, 0]}

        async def objs(t=None):
            os_ = await page.evaluate("()=>window.__a3dState().objs")
            return [o for o in os_ if t is None or o.get('t') == t]

        async def toast():
            return await page.evaluate("()=>{const t=document.getElementById('a3d-toast');return t?t.textContent:'';}")

        async def click_at(p, dx=0, dy=0):
            s = await scr(p)
            await page.mouse.click(s[0] + dx, s[1] + dy)
            await page.wait_for_timeout(200)

        async def sel():
            return (await page.evaluate("()=>window.__a3dState()")).get('sel')

        async def scene(o):
            await page.evaluate("(o)=>window.__a3dTestSetObjs(o)", o)
            await page.evaluate("()=>{window.__a3dFlat(true);window.__a3dFit();window.__a3dTestPaint();}")
            await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
            await page.wait_for_timeout(200)

        # --------------------------------------------- 1. rooms, numbered
        print("\n-- 1. rooms made with the Room tool are numbered per level")
        await scene([sk('R', [[0, 0], [10, 0], [10, 6], [0, 6]]), sk('D', [[5, -1], [5, 7]], closed=False)])
        await palette_run(page, 'Room')
        await click_at([2.5, 3.0])
        await palette_run(page, 'Room')
        await click_at([7.5, 3.0])
        await page.keyboard.press('Escape')
        rooms = await objs('room')
        rooms.sort(key=lambda r: r['pts'][0][0] if r['pts'] else 0)
        nums = sorted(str(r.get('number')) for r in rooms)
        ck(len(rooms) == 2 and nums == ['101', '102'],
           "two rooms on the first level are numbered 101 and 102 (%s)" % nums)
        left = [r for r in rooms if max(p[0] for p in r['pts']) <= 5.01]
        right = [r for r in rooms if min(p[0] for p in r['pts']) >= 4.99]
        A = left[0]['id'] if left else None
        B = right[0]['id'] if right else None
        ck(A and B, "one room on each side of the dividing line")

        # --------------------------------------------- 2. tagging
        print("\n-- 2. Tag Room from the palette and the ribbon, clicked with the mouse")
        await palette_run(page, 'ROOMTAG')
        pr = await page.evaluate("()=>window.__a3dPrompt()")
        ck('tag' in pr.lower(), "ROOMTAG starts the tag command (%r)" % pr)
        await click_at([2.5, 4.0])
        await click_at([7.5, 4.0])
        tags = await objs('roomtag')
        ck(len(tags) == 2 and sorted(t['roomId'] for t in tags) == sorted([A, B]),
           "two clicks tag the two rooms, one each (%d)" % len(tags))
        ck('tag' in (await page.evaluate("()=>window.__a3dPrompt()")).lower(),
           "and the command stays live for the next room")
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(200)
        ck(len(await objs('roomtag')) == 2 and await page.evaluate("()=>window.__a3dPrompt()") == 'Ready',
           "Escape ends it and adds nothing")
        tA = ([t['id'] for t in tags if t['roomId'] == A] or [None])[0]
        tB = ([t['id'] for t in tags if t['roomId'] == B] or [None])[0]
        rib = await page.evaluate("""()=>{const es=[...document.querySelectorAll('[data-a3dr="bim:tagroom"]')];
            return {n:es.length,dis:es.filter(e=>e.classList.contains('a3dr-dis')).length};}""")
        ck(rib['n'] >= 1 and rib['dis'] == 0,
           "the ribbon's Tag Room button is no longer greyed as unimplemented (%s)" % rib)
        await page.evaluate("()=>{const e=document.querySelector('[data-a3dr=\"bim:tagroom\"]');if(e)e.click();}")
        await page.wait_for_timeout(250)
        pr2 = await page.evaluate("()=>window.__a3dPrompt()")
        ck('tag' in pr2.lower(), "and pressing it starts the tag command (%r)" % pr2)
        await page.keyboard.press('Escape')
        await page.wait_for_timeout(150)

        # --------------------------------------------- 3. the tag reads its room
        print("\n-- 3. a tag never disagrees with its room")
        t0 = await page.evaluate("(id)=>window.__a3dRoomTagText(id)", tA)
        ck(t0 and t0.startswith('101 '), "the tag reads the room's number and name (%r)" % t0)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", A)
        await page.evaluate("()=>window.__a3dRefreshProps&&window.__a3dRefreshProps()")
        await page.evaluate("()=>window.__a3dTestPaint()")
        ok_nm = await page.query_selector('[data-propf="name"]')
        if ok_nm:
            await page.fill('[data-propf="name"]', 'Kitchen')
            await page.dispatch_event('[data-propf="name"]', 'change')
            await page.wait_for_timeout(200)
        ok_num = await page.query_selector('[data-roomf="number"]')
        if ok_num:
            await page.fill('[data-roomf="number"]', '110')
            await page.dispatch_event('[data-roomf="number"]', 'change')
            await page.wait_for_timeout(200)
        t1 = await page.evaluate("(id)=>window.__a3dRoomTagText(id)", tA)
        ck(ok_nm and ok_num and t1 == '110 Kitchen',
           "renaming and renumbering the ROOM in Properties changes its tag (%r)" % t1)
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", tB)
        await page.evaluate("()=>window.__a3dRefreshProps&&window.__a3dRefreshProps()")
        via = await page.query_selector('[data-roomf="name"]')
        if via:
            await page.fill('[data-roomf="name"]', 'Dining')
            await page.dispatch_event('[data-roomf="name"]', 'change')
            await page.wait_for_timeout(200)
        rB = await snap(B)
        ck(via and rB.get('name') == 'Dining',
           "renaming through the TAG's Properties renames the room (%s)" % rB.get('name'))
        if await page.query_selector('[data-roomf="number"]'):
            await page.fill('[data-roomf="number"]', '110')
            await page.dispatch_event('[data-roomf="number"]', 'change')
            await page.wait_for_timeout(150)
        tt = await toast()
        ck('also used' in (tt or ''), "a duplicate room number is allowed but SAID (%r)" % tt)
        await page.evaluate("(id)=>window.__a3dSetRoomField(id,'number','102')", B)

        print("\n-- 3b. the room's own label steps aside while it is tagged")
        drawn = await page.evaluate("""()=>{
            const seen=[];const f=CanvasRenderingContext2D.prototype.fillText;
            CanvasRenderingContext2D.prototype.fillText=function(t,x,y){seen.push(String(t));return f.apply(this,arguments);};
            window.__a3dSelectFor([]);window.__a3dTestPaint();
            CanvasRenderingContext2D.prototype.fillText=f;return seen;}""")
        ck(drawn.count('Kitchen') == 1 and not any(s.startswith('110  Kitchen') for s in drawn),
           "'Kitchen' is written once on the canvas -- by its tag, not also by the room (%d)"
           % drawn.count('Kitchen'))

        # --------------------------------------------- 4. pick and grip
        print("\n-- 4. the tag is picked where it is drawn, and moved by its grip")
        tg = await snap(tA)
        await page.evaluate("()=>{window.__a3dSelectFor([]);window.__a3dTestPaint();}")
        await click_at(tg['pt'])
        ck(await sel() == tA, "a click on the tag inside the room selects the TAG, not the room")
        await page.evaluate("()=>window.__a3dTestPaint()")
        gs = [g for g in await page.evaluate("()=>window.__a3dGrips()") if g.get('objId') == tA]
        if gs:
            a = [box[0] + gs[0]['x'], box[1] + gs[0]['y']]
            b = await scr([2.0, 1.5])
            await page.mouse.move(a[0], a[1]); await page.mouse.down()
            await page.mouse.move(b[0], b[1], steps=8); await page.mouse.up()
            await page.wait_for_timeout(200)
        tg2 = await snap(tA)
        ck(len(gs) == 1 and near(tg2['pt'][0], 2.0, 0.08) and near(tg2['pt'][1], 1.5, 0.08),
           "its one grip moves it to (2, 1.5) (%s)" % tg2['pt'])

        # --------------------------------------------- 5. relationships
        print("\n-- 5. the tag depends on its room")
        rel = await page.evaluate("(id)=>window.__a3dGraphRelationsOf(id)", A)
        ck(any(d.get('objId') == tA and d.get('rel') == 'tag' for d in (rel or {}).get('dependents', [])),
           "the relation graph links the room to its tag")
        await scene([sk('Q', [[0, 0], [4, 0], [4, 3], [0, 3]])])
        q = await page.evaluate("()=>window.__a3dCreateRoomAt([2,1.5],0)")
        qt = await page.evaluate("()=>window.__a3dTagRoomAt([1,1])")
        await page.evaluate("()=>window.__a3dFit()")
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", q)
        await page.evaluate("()=>window.__a3dTestPaint()")
        a = await scr([3.0, 2.2]); b = await scr([8.0, 2.2])
        await page.mouse.move(a[0], a[1]); await page.mouse.down()
        await page.mouse.move(b[0], b[1], steps=10); await page.mouse.up()
        await page.wait_for_timeout(300)
        qs = await snap(q); qts = await snap(qt)
        ck(abs(qs['pos'][0]) > 1 and near(qts['pos'][0], qs['pos'][0], 1e-9) and near(qts['pos'][2], qs['pos'][2], 1e-9),
           "moving the room moves its tag by the same amount (room %.3f, tag %.3f)" % (qs['pos'][0], qts['pos'][0]))
        await page.evaluate("(id)=>window.__a3dSelectFor([id])", q)
        await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(250)
        dt = await toast()
        ck(not await objs('room') and not await objs('roomtag') and '2 object' in (dt or '') and 'removed' not in (dt or ''),
           "deleting the room deletes its tag WITH it -- one delete of 2 objects, not a later sweep (%r)" % dt)
        await page.evaluate("()=>window.__a3dUndo()")
        await page.wait_for_timeout(200)
        ck(len(await objs('room')) == 1 and len(await objs('roomtag')) == 1, "Undo brings both back")
        await page.evaluate("""()=>{var o=window.__a3dState().objs.filter(x=>x.t!=='room');
            window.__a3dTestSetObjs(o.concat([{id:'KEEP',t:'sketch',name:'KEEP',col:'#5ec4b8',pos:[0,0,0],pts:[[20,0],[21,0]],y:0,closed:false}]));}""")
        # the room is gone but its tag is not; the next real edit (deleting KEEP) saves
        await page.evaluate("()=>window.__a3dSelectFor(['KEEP'])")
        await page.evaluate("()=>document.activeElement&&document.activeElement.blur()")
        await page.keyboard.press('Delete')
        await page.wait_for_timeout(250)
        ck(not await objs('roomtag') and 'room tag' in (await toast() or ''),
           "a tag whose room vanished some other way is swept on the next save, and said (%r)" % await toast())

        # --------------------------------------------- 6. tag all
        print("\n-- 6. Tag All tags exactly the untagged rooms")
        await scene([sk('R', [[0, 0], [12, 0], [12, 4], [0, 4]]), sk('D1', [[4, -1], [4, 5]], closed=False),
                     sk('D2', [[8, -1], [8, 5]], closed=False)])
        for x in (2, 6, 10):
            await page.evaluate("(x)=>window.__a3dCreateRoomAt([x,2],0)", x)
        await page.evaluate("()=>window.__a3dTagRoomAt([2,2])")
        made = await page.evaluate("()=>window.__a3dTagAllRooms()")
        tags = await objs('roomtag')
        ck(len(made) == 2 and len(tags) == 3 and len(set(t['roomId'] for t in tags)) == 3,
           "with one room tagged, Tag All adds 2 tags, one per remaining room (%d, %d)" % (len(made), len(tags)))
        made2 = await page.evaluate("()=>window.__a3dTagAllRooms()")
        ck(len(made2) == 0 and 'already tagged' in (await toast() or ''), "a second Tag All adds none and says why")
        inside_ok = True
        for t in tags:
            r = await snap(t['roomId'])
            inside_ok = inside_ok and inside(t['pt'], r['pts'])
        ck(inside_ok, "every tag Tag All placed is inside its room")

        # --------------------------------------------- 7. schedule, export
        print("\n-- 7. the schedule and the DXF read the same data")
        rid = tags[0]['roomId'] if tags else None
        await page.evaluate("(id)=>window.__a3dSetRoomField(id,'dept','Kitchens')", rid)
        sched = await page.evaluate("()=>window.__a3dRoomSchedule()")
        row = [s for s in sched if s.get('dept') == 'Kitchens']
        ck(len(sched) == 3 and row and row[0].get('number'),
           "the room schedule carries the number and the department (%s)" % (row[0] if row else None))
        dxf = (await page.evaluate("()=>window.__a3dBuildDXF()") or {}).get('text')
        rname = str((await snap(rid)).get('name'))
        rnum = str((await snap(rid)).get('number'))
        ck(isinstance(dxf, str) and dxf.count(rnum + ' ' + rname) == 1,
           "the DXF has the tag's text '%s %s' and no second label for that room" % (rnum, rname))

        # --------------------------------------------- 8. L room
        print("\n-- 8. the label point of an L-shaped room is inside it")
        L = [[0, 0], [8, 0], [8, 2], [2, 2], [2, 8], [0, 8]]
        await scene([sk('L', L)])
        lr = await page.evaluate("()=>window.__a3dCreateRoomAt([1,1],0)")
        lp = await page.evaluate("(id)=>window.__a3dRoomLabelPoint(id)", lr)
        avg = [sum(p[0] for p in L) / 6, sum(p[1] for p in L) / 6]
        ck(lp and inside(lp, L) and not inside(avg, L),
           "the label goes inside the L (%s), where the vertex average %s would not" % (lp, avg))

        # --------------------------------------------- 9. persistence
        print("\n-- 9. numbers and tags survive a reload")
        await scene([sk('P', [[0, 0], [5, 0], [5, 4], [0, 4]])])
        pr_ = await page.evaluate("()=>window.__a3dCreateRoomAt([2,2],0)")
        pt_ = await page.evaluate("()=>window.__a3dTagRoomAt([2,2])")
        await page.evaluate("(id)=>window.__a3dSetRoomField(id,'occupancy','Office')", pr_)
        await page.wait_for_timeout(700)
        await page.reload()
        await page.wait_for_timeout(2300)
        rp = await snap(pr_)
        tp = await snap(pt_)
        ck(rp.get('number') == '101' and rp.get('occupancy') == 'Office' and tp.get('roomId') == pr_,
           "the room keeps its number and occupancy, and the tag still points at it")

        ck(not errs, "no uncaught page errors (%s)" % errs[:3])
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.failed), ck.n))
    print("RESULT: " + ("PASS" if not ck.failed else "FAIL"))
    return 0 if not ck.failed else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
