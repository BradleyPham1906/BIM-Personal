#!/usr/bin/env python3
"""bim_phase150_tool_palette_browser_tests.py -- V150: the tool palette on a phone and a tablet.

Measured in the browser:
  1. A PHONE (390 x 844, touch): the dock gives way to a palette of eleven essentials, upright on
     the right edge, over the drawing; 42 px buttons; the tool in use filled; Select puts a tool
     away; Pan toggles; Delete and All tools work.
  2. DRAG: by the grip, to the middle it lies flat; to the left edge it docks upright there; kept
     through a reload; never off the drawing.
  3. FOLD: to one round button showing the tool in use; a tap opens it; the button drags.
  4. A TABLET (820 x 1180): flat at the foot of the drawing; messages and the length box above it.
  5. A COMPUTER: no palette, the dock as it was.

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, re, sys, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('  ok    ' if cond else '  FAIL  ') + msg)


CK = Checks()
STALL = 90


class Stalled(Exception):
    pass


async def within(aw, what):
    try:
        return await asyncio.wait_for(aw, STALL)
    except asyncio.TimeoutError:
        raise Stalled(what)


async def open_page(pw, vp, touch, ctx=None):
    b = await pw.chromium.launch()
    c = ctx or await b.new_context(viewport=vp, has_touch=touch, is_mobile=touch)
    p = await c.new_page()
    errs = []
    p.on('pageerror', lambda e: errs.append(str(e)))
    await within(p.goto('file://' + str(HTML)), 'goto')
    await p.wait_for_timeout(1800)

    async def safe(js, arg=None):
        try:
            return await within(p.evaluate(js, arg) if arg is not None else p.evaluate(js), 'evaluate ' + js[:50])
        except Stalled:
            raise
        except Exception as e:
            print('      (evaluate failed: %s)' % str(e)[:200])
            return None
    await safe("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();}")
    await p.wait_for_timeout(400)
    return b, c, p, safe, errs


async def drag(p, sel, to):
    r = await p.evaluate("(s)=>{var e=document.querySelector(s).getBoundingClientRect();return [e.left+e.width/2,e.top+e.height/2];}", sel)
    await p.mouse.move(r[0], r[1])
    await p.mouse.down()
    steps = 8
    for k in range(1, steps + 1):
        await p.mouse.move(r[0] + (to[0] - r[0]) * k / steps, r[1] + (to[1] - r[1]) * k / steps)
        await p.wait_for_timeout(15)
    await p.mouse.up()
    await p.wait_for_timeout(150)


CANVAS = "()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top,r.right,r.bottom];}"


async def run():
    ck = CK
    async with async_playwright() as pw:
        print("\n-- 1. a phone")
        b, c, p, safe, errs = await open_page(pw, {'width': 390, 'height': 844}, True)
        try:
            has = await safe("()=>window.__acad3dV150")
            ck(bool(has) and 'toolpalette' in has, "__acad3dV150 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 150, "the app says V150 or later (%s)" % (mv and mv.group(1)))
            T = await safe("()=>window.__a3dToolPal()") or {}
            cv = await safe(CANVAS)
            ck(T.get('shown') and T.get('tools') == ['select', 'pan', 's:line', 's:rect', 's:circle', 'bim:wall', 'bim:door', 'bim:window', 'bim:dim', 'm:del', 'more'],
               "a palette of the essentials: Select, Pan, Line, Rectangle, Circle, Wall, Door, Window, Dimension, Delete, All tools (%s)" % T.get('tools'))
            ck(await safe("()=>getComputedStyle(document.getElementById('a3d-dock')).display") == 'none', "the dock gives way to it")
            ck(T.get('orient') == 'v' and T['x'] + T['w'] <= cv[2] and T['x'] + T['w'] >= cv[2] - 20 and T['y'] >= cv[1] and T['y'] + T['h'] <= cv[3],
               "upright on the right edge, over the drawing (%s)" % {k: T.get(k) for k in ('x', 'y', 'w', 'h')})
            sz = await safe("()=>[].map.call(document.querySelectorAll('#a3d-tpal [data-tpact]'),function(b){var r=b.getBoundingClientRect();return [r.width,r.height];})") or []
            ck(sz and all(w >= 42 and h >= 42 for w, h in sz), "every button 42 px for a finger")
            look = await safe("()=>{var s=getComputedStyle(document.getElementById('a3d-tpal'));return [s.borderRadius,s.backdropFilter||s.webkitBackdropFilter,s.position];}")
            ck(look and look[0] == '24px' and 'blur' in (look[1] or '') and look[2] == 'fixed', "a frosted, rounded capsule (%s)" % look)
            ck(T.get('active') == 'select' and await safe("()=>document.querySelector('#a3d-tpal [data-tpact=\"select\"]').classList.contains('on')"), "Select is the tool in use at the start, filled")
            await p.tap('#a3d-tpal [data-tpact="bim:wall"]')
            await p.wait_for_timeout(200)
            st = await safe("()=>[window.__a3dToolPal().active,(window.__a3dState().sk||{}).tool,document.querySelector('#a3d-tpal [data-tpact=\"bim:wall\"]').getAttribute('aria-pressed'),document.querySelector('#a3d-tpal [data-tpact=\"select\"]').classList.contains('on')]")
            ck(st == ['bim:wall', 'wall', 'true', False], "Wall starts the wall tool and is filled; Select is not (%s)" % st)
            bg = await safe("()=>getComputedStyle(document.querySelector('#a3d-tpal [data-tpact=\"bim:wall\"]')).backgroundColor")
            ck(bg == 'rgb(10, 132, 255)', "filled in blue (%s)" % bg)
            await p.tap('#a3d-tpal [data-tpact="select"]')
            await p.wait_for_timeout(200)
            ck(await safe("()=>[window.__a3dToolPal().active,!!window.__a3dState().sk]") == ['select', False], "Select puts the tool away")
            await p.tap('#a3d-tpal [data-tpact="s:line"]')
            await p.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dState().sk") or {}).get('tool') == 'line', "Line draws lines")
            await p.keyboard.press('Escape')
            await p.wait_for_timeout(200)
            ck(await safe("()=>document.querySelector('#a3d-tpal [data-tpact=\"select\"]').classList.contains('on')&&!document.querySelector('#a3d-tpal [data-tpact=\"s:line\"]').classList.contains('on')"),
               "Esc ends it, and the palette's buttons follow")
            await p.tap('#a3d-tpal [data-tpact="pan"]')
            await p.wait_for_timeout(150)
            ck(await safe("()=>[window.__a3dToolPal().nav,window.__a3dToolPal().active]") == ['pan', 'pan'], "Pan turns panning on")
            await p.tap('#a3d-tpal [data-tpact="s:rect"]')
            await p.wait_for_timeout(150)
            ck(await safe("()=>[window.__a3dToolPal().nav,window.__a3dToolPal().active]") == ['orbit', 's:rect'], "a drawing tool turns it off again")
            await p.tap('#a3d-tpal [data-tpact="select"]')
            await p.tap('#a3d-tpal [data-tpact="pan"]')
            await p.tap('#a3d-tpal [data-tpact="pan"]')
            await p.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dToolPal().nav") == 'orbit', "and Pan again turns it off")
            cid = await safe("()=>{var i=window.__a3dColumnAt([0,0],0,0.4,0.4,3);window.__a3dSelectFor([i]);return i;}")
            n0 = await safe("()=>window.__a3dState().objs.length")
            await p.tap('#a3d-tpal [data-tpact="m:del"]')
            await p.wait_for_timeout(200)
            ck(await safe("()=>window.__a3dState().objs.length") == n0 - 1, "Delete deletes the selection")
            await p.tap('#a3d-tpal [data-tpact="more"]')
            await p.wait_for_timeout(300)
            pan = await safe("()=>{var q=document.getElementById('a3d-rupop');return !!q&&q.classList.contains('open')&&q.getAttribute('data-for')==='help';}")
            ck(pan, "All tools opens the panel with every tool and the search")
            await p.keyboard.press('Escape')
            await safe("()=>{var q=document.getElementById('a3d-rupop');if(q)q.classList.remove('open');}")

            print("\n-- 2. drag")
            await drag(p, '#a3d-tpal [data-tpgrip]', (195, 420))
            T = await safe("()=>window.__a3dToolPal()") or {}
            ck(T.get('orient') == 'h' and T['x'] >= cv[0] and T['x'] + T['w'] <= cv[2] and T['y'] >= cv[1] and T['y'] + T['h'] <= cv[3],
               "dragged by its grip to the middle, it lies flat, inside the drawing (%s)" % {k: T.get(k) for k in ('orient', 'x', 'y', 'w', 'h')})
            await drag(p, '#a3d-tpal [data-tpgrip]', (6, 300))
            T = await safe("()=>window.__a3dToolPal()") or {}
            ck(T.get('orient') == 'v' and T['x'] <= cv[0] + 12 and T['x'] >= cv[0], "to the left edge, it docks there upright (%s)" % {k: T.get(k) for k in ('orient', 'x', 'y')})
            ys = T.get('y')
            await drag(p, '#a3d-tpal [data-tpgrip]', (10, 5000))
            T = await safe("()=>window.__a3dToolPal()") or {}
            ck(T['y'] + T['h'] <= cv[3] and T['y'] >= cv[1], "dragged past the bottom, it stops at the drawing's edge (%s)" % T.get('y'))
            await drag(p, '#a3d-tpal [data-tpgrip]', (12, ys + 300))
            T0 = await safe("()=>window.__a3dToolPal()") or {}
            await p.wait_for_timeout(200)
            await within(p.reload(), 'reload')
            await p.wait_for_timeout(1800)
            await safe("()=>{window.__a3dEnter();window.__a3dSetPlanView&&window.__a3dSetPlanView();}")
            await p.wait_for_timeout(400)
            T1 = await safe("()=>window.__a3dToolPal()") or {}
            ck(T1.get('orient') == 'v' and abs(T1['x'] - T0['x']) <= 2 and abs(T1['y'] - T0['y']) <= 2, "where it was left is kept through a reload (%s, %s)" % (T0.get('y'), T1.get('y')))

            print("\n-- 3. fold")
            await p.tap('#a3d-tpal [data-tptoggle]')
            await p.wait_for_timeout(200)
            T = await safe("()=>window.__a3dToolPal()") or {}
            cur = await safe("()=>{var c=document.querySelector('#a3d-tpal [data-tpcur]'),r=c.getBoundingClientRect();return [r.width,r.height,c.getAttribute('data-for'),getComputedStyle(c).borderRadius];}")
            ck(T.get('min') and T['w'] <= 64 and T['h'] <= 64 and cur and cur[0] >= 44 and cur[2] == 'select' and cur[3] == '50%',
               "the chevron folds it to one round button showing the tool in use (%s, %s)" % ({k: T.get(k) for k in ('w', 'h')}, cur))
            await safe("()=>window.__a3dToolPalAct('bim:door')")
            await p.wait_for_timeout(100)
            ck(await safe("()=>document.querySelector('#a3d-tpal [data-tpcur]').getAttribute('data-for')") == 'bim:door', "folded, it shows the tool now in use: Door")
            await safe("()=>window.__a3dToolPalAct('select')")
            await drag(p, '#a3d-tpal [data-tpcur]', (300, 300))
            T = await safe("()=>window.__a3dToolPal()") or {}
            ck(T.get('min') and abs(T['x'] + T['w'] / 2 - 300) < 30, "the folded button drags, and stays folded (%s)" % {k: T.get(k) for k in ('x', 'min')})
            await p.tap('#a3d-tpal [data-tpcur]')
            await p.wait_for_timeout(200)
            T = await safe("()=>window.__a3dToolPal()") or {}
            ck(not T.get('min') and len(T.get('tools', [])) == 11 and T['w'] > 100, "a tap on it opens the palette again (%s)" % {k: T.get(k) for k in ('w', 'h')})
            await p.tap('[data-a3d="rdrawer"]')
            await p.wait_for_timeout(250)
            ck(not (await safe("()=>window.__a3dToolPal()") or {}).get('shown'), "Properties' sheet open, the palette steps aside")
            await p.tap('[data-a3d="rdrawer"]')
            await p.wait_for_timeout(250)
            ck((await safe("()=>window.__a3dToolPal()") or {}).get('shown'), "and comes back when it shuts")
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok'), "the shell audit is clean with the palette (%s)" % au.get('unclaimed'))
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "phone: the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "phone: ran to its end")
        await b.close()

        print("\n-- 4. a tablet")
        b, c, p, safe, errs = await open_page(pw, {'width': 820, 'height': 1180}, True)
        try:
            T = await safe("()=>window.__a3dToolPal()") or {}
            cv = await safe(CANVAS)
            ck(T.get('shown') and T.get('orient') == 'h' and cv[3] - (T['y'] + T['h']) <= 12 and abs((T['x'] + T['w'] / 2) - (cv[0] + cv[2]) / 2) < 3,
               "flat at the foot of the drawing, centred (%s)" % {k: T.get(k) for k in ('x', 'y', 'w', 'h')})
            await safe("()=>window.__a3dToast('V150 probe')")
            await p.wait_for_timeout(150)
            tb = await safe("()=>document.getElementById('a3d-toast').getBoundingClientRect().bottom")
            ck(tb is not None and tb <= T['y'], "a message shows above it (%s <= %s)" % (tb, T.get('y')))
            await p.tap('#a3d-tpal [data-tpact="bim:wall"]')
            await p.wait_for_timeout(200)
            tl = await safe("()=>{var e=document.querySelector('.a3d-touchlen');if(!e||getComputedStyle(e).display==='none')return null;return e.getBoundingClientRect().bottom;}")
            ck(tl is None or tl <= T['y'], "and the typed-length box (%s)" % tl)
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "tablet: the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "tablet: ran to its end")
        await b.close()

        print("\n-- 5. a computer")
        b, c, p, safe, errs = await open_page(pw, {'width': 1500, 'height': 950}, False)
        try:
            T = await safe("()=>window.__a3dToolPal()") or {}
            ck(T.get('shown') is False and await safe("()=>getComputedStyle(document.getElementById('a3d-dock')).display") != 'none', "no palette: the dock, as it was")
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "computer: the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "computer: ran to its end")
        await b.close()

    print("\n%d/%d checks passed" % (CK.n - len(CK.bad), CK.n))
    if CK.bad:
        print("RESULT: FAIL")
        for m in CK.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
