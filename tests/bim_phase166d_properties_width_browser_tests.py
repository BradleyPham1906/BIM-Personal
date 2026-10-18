#!/usr/bin/env python3
"""bim_phase166d_properties_width_browser_tests.py -- V166d: Properties' width by one press, and its
edge a window splitter.

V166b gave the left panel a width button beside its collapse: WCAG 2.2's 2.5.7 (Dragging Movements)
asks that what a drag does can be done by a single pointer without dragging, and 2.5.8 (Target Size)
excepts a small target when an equivalent control is 24 px. Properties' own edge (V147) had only the
drag and the minimise. Measured in the browser:
  1. THE BUTTON, in Properties' header beside the minimise: 30 px; each press widens Properties a step
     -- 240, 320, 400, 480, 560 -- and from the widest back to 240; kept, and the drawing gives up or
     takes the room; its label says where the next press goes; hidden while Properties is minimised;
     the same muted grey as the minimise on both themes; remembered across a reload.
  2. WITHIN WHAT THE SCREEN ALLOWS: the drawing keeps 320 px beside the left panel at its narrowest
     (the left panel gives way to Properties, V166b): on a 1100 px screen the steps stop at 484; the
     drag, End and a width kept on a wider screen stop there too, and the kept width comes back when
     the screen does; mid-drag the left panel gives way as Properties grows.
  3. THE EDGE FROM THE KEYBOARD, the W3C's window splitter: a focusable separator, vertical, controlling
     Properties, named by its header's "Properties", its width its value within what the screen
     allows; the splitter moves the way the arrow points, so Left widens Properties (16 px, Shift 64);
     Home and End; Enter minimises it and puts the focus on the minimise button, whose Enter brings it
     back; the model's keys are left alone while it has the focus.
  4. ANY POINTER: a mouse; a finger on a tablet on its side (CDP touch events), with a 12 px edge it
     can see and a 36 px button; a cancelled drag puts the width back.
  5. WHERE PROPERTIES IS A DRAWER OR A SHEET -- an upright tablet, a phone either way, a window 1024
     px wide or less or 500 px high or less -- no button and no edge; the code's test for "docked" is
     the stylesheet's own query and agrees with the layout at each boundary; the arrow closes the
     drawer or sheet (it shrank them to a 42 px strip where the screen was wider than 900 px) and the
     computer's width is not forced on them.
  6. THE SHELL'S AUDIT reaches Properties' chrome (not its body), counts a focusable edge as a
     control, and knows the button.

The harness never waits without a bound (V123).
"""
import asyncio, json, pathlib, re, sys, traceback
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

RAIL, LEFT_MIN, KEEP, R_MIN, R_MAX = 54, 242, 320, 240, 560


def rmax(w):
    """Properties' widest on a screen w px wide, worked out here: the drawing keeps 320 px beside the
    rail and the left panel at its narrowest."""
    return max(R_MIN, min(R_MAX, w - RAIL - LEFT_MIN - KEEP))


def steps_from(w, mx):
    """The widths a run of presses goes through from w, by the rule V166b set for the left panel."""
    out = []
    for _ in range(7):
        nx = next((s for s in (240, 320, 400, 480, 560) if s > w and s <= mx), None)
        w = nx if nx is not None else (mx if w < mx else R_MIN)
        out.append(w)
    return out


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


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1500, 'height': 950})
        page = await ctx.new_page()
        errs, warns = [], []
        page.on('pageerror', lambda e: errs.append(str(e)))
        page.on('console', lambda m: warns.append(m.text) if m.type == 'warning' and '[BIM]' in m.text else None)
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None, pg=None):
            p = pg or page
            try:
                return await within(p.evaluate(js, arg) if arg is not None else p.evaluate(js), 'evaluate ' + js[:50])
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        has = await safe("()=>window.__acad3dV166d")
        ck(bool(has) and 'rightstep' in has and 'rightedgekeys' in has and 'rightdocked' in has and 'auditproperties' in has,
           "__acad3dV166d marker is present (%s)" % (has or '')[:60])
        if not has:
            print("\n%d/%d checks passed\nRESULT: FAIL" % (ck.n - len(ck.bad), ck.n))
            await browser.close()
            return 1

        async def rp(pg=None):
            return await safe("()=>window.__a3dRightPanel()", pg=pg) or {}

        async def geo(pg=None):
            # Properties, its edge, its button, the drawing between the panels, and what is kept; the left
            # panel's width eases over 0.18 s, so it is read once that has settled (V84)
            try:
                await (pg or page).wait_for_function("()=>{var p=document.getElementById('a3d-leftpanel');return !p||!p.getAnimations||p.getAnimations().length===0;}", timeout=4000)
            except Exception:
                print('      (the left panel was still moving after 4 s)')
            return await safe("""()=>{var r=document.getElementById('a3d-right'),rr=r.getBoundingClientRect(),a=document.getElementById('acad3d').getBoundingClientRect(),
              g=r.querySelector('.a3d-rgrip'),gr=g?g.getBoundingClientRect():{left:0,right:0,width:0},b=r.querySelector('[data-rpwidth]'),br=b?b.getBoundingClientRect():{left:0,right:0,width:0,height:0},
              m=document.getElementById('a3d-rminbtn'),mr=m?m.getBoundingClientRect():{left:0},c=document.querySelector('#a3d-viewport canvas')||document.querySelector('#acad3d canvas'),
              lp=document.getElementById('a3d-leftpanel');
              return {w:Math.round(rr.width),rl:Math.round(rr.left),draw:Math.round(rr.left-a.left),al:Math.round(a.left),lw:lp?Math.round(lp.getBoundingClientRect().width):null,
                cw:c?Math.round(c.getBoundingClientRect().width):null,store:localStorage.getItem('acad3dRightPanel'),
                gl:gr.left,gw:gr.width,gd:g?getComputedStyle(g).display:null,now:g?g.getAttribute('aria-valuenow'):null,vmin:g?g.getAttribute('aria-valuemin'):null,vmax:g?g.getAttribute('aria-valuemax'):null,
                bd:b?getComputedStyle(b).display:null,bw:Math.round(br.width),bh:Math.round(br.height),bl:br.left,br:br.right,ml:mr.left,
                label:b?b.getAttribute('aria-label'):null,title:b?b.title:null,min:document.body.classList.contains('a3d-rmin'),pos:getComputedStyle(r).position,rd:getComputedStyle(r).display};}""", pg=pg) or {}

        def kept(g):
            # the width kept in this browser, from Properties' own record
            try:
                return json.loads(g.get('store') or '{}').get('w')
            except ValueError:
                return 'unreadable'

        async def press(pg=None, n=1):
            p = pg or page
            for _ in range(n):
                await safe("()=>{var b=document.querySelector('#a3d-right [data-rpwidth]');if(b)b.click();}", pg=p)
                await p.wait_for_timeout(250)

        try:
            # ---------------------------------------------------------------------------------
            print("\n-- 1. the button, on a computer")
            await safe("()=>{window.__a3dRightSetWidth(null);window.__a3dSetLeftWidth(null);}")
            await page.wait_for_timeout(250)
            g0 = await geo()
            hdr = await safe("""()=>{var h=document.querySelector('#a3d-right .a3d-palhd'),k=[].map.call(h.children,function(e){return e.id||e.getAttribute('data-rpwidth')&&'width'||e.tagName;});
              return {kids:k,text:h.textContent.trim(),tag:(document.querySelector('#a3d-right [data-rpwidth]')||{}).tagName,type:(document.querySelector('#a3d-right [data-rpwidth]')||{}).type};}""") or {}
            ck(hdr.get('kids') == ['a3d-rpttl', 'width', 'a3d-rminbtn'] and hdr.get('text') == 'Properties' and hdr.get('tag') == 'BUTTON' and hdr.get('type') == 'button',
               "a button in Properties' header, after its name and just before the minimise; the header still says Properties (%s)" % hdr)
            ck(g0.get('bw') == 30 and g0.get('bh') == 30 and g0.get('bd') != 'none' and 0 <= g0.get('ml', 0) - g0.get('br', 0) <= 4,
               "30 by 30 px, beside the minimise (%s)" % [g0.get('bw'), g0.get('bh'), g0.get('br'), g0.get('ml')])
            ck(g0.get('w') == 280 and kept(g0) is None, "Properties starts at its 280 px, nothing kept (%s, %s)" % (g0.get('w'), g0.get('store')))
            seen = [g0]
            for k in range(6):
                await press()
                seen.append(await geo())
            ws = [s.get('w') for s in seen]
            ck(ws == [280] + steps_from(280, rmax(1500))[:6] and ws == [280, 320, 400, 480, 560, 240, 320],
               "each press widens it a step, 320, 400, 480, 560, then back to 240 and on (%s)" % ws)
            ck([kept(s) for s in seen[1:]] == ws[1:], "each width is kept (%s)" % [kept(s) for s in seen[1:]])
            dd = [seen[i - 1]['cw'] - seen[i]['cw'] if seen[i - 1].get('cw') and seen[i].get('cw') else None for i in range(1, len(seen))]
            ck(dd == [ws[i] - ws[i - 1] for i in range(1, len(ws))], "the drawing gives up and takes back the room, px for px (%s)" % dd)
            labs = [s.get('label') for s in seen]
            want = ['Properties width %d px: %s' % (ws[i], ('widen to %d' if ws[i + 1] > ws[i] else 'back to %d') % ws[i + 1]) for i in range(len(ws) - 1)]
            ck(labs[:-1] == want and all(s.get('title') == s.get('label') for s in seen),
               "its label says where the next press goes, and its tooltip says the same (%r ... %r)" % (labs[0], labs[4]))
            ck([s.get('now') for s in seen] == [str(w) for w in ws], "the edge's value follows each press (%s)" % [s.get('now') for s in seen])
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            g1 = await geo()
            ck(g1.get('w') == 320 and g1.get('label') == 'Properties width 320 px: widen to 400', "after a reload it is 320 px, and says so (%s)" % [g1.get('w'), g1.get('label')])
            await safe("()=>window.__a3dRightToggleMin(true)")
            await page.wait_for_timeout(200)
            g2 = await geo()
            await safe("()=>window.__a3dRightToggleMin(false)")
            await page.wait_for_timeout(200)
            g3 = await geo()
            ck(g2.get('min') is True and g2.get('bd') == 'none' and g2.get('gd') == 'none' and g3.get('bd') != 'none' and g3.get('w') == 320,
               "minimised, the button goes with the edge; shown again, both are back at 320 (%s)" % [g2.get('bd'), g3.get('bd'), g3.get('w')])
            hc = await safe("""()=>{var f=function(){var h=document.querySelector('#a3d-right .a3d-palhd');return [getComputedStyle(document.querySelector('#a3d-right [data-rpwidth]')).color,
              getComputedStyle(document.getElementById('a3d-rminbtn')).color,getComputedStyle(document.getElementById('a3d-right')).backgroundColor];};
              var d=f();document.body.classList.add('light-theme');var l=f();document.body.classList.remove('light-theme');return [d,l];}""") or [[], []]
            ck(len(hc[0]) == 3 and hc[0][0] == hc[0][1] == 'rgb(143, 152, 162)' and len(hc[1]) == 3 and hc[1][0] == hc[1][1] == 'rgb(104, 114, 128)' and hc[1][2] != hc[1][0],
               "the minimise's muted grey on both themes, never white on the light theme's white (%s)" % hc)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. within what the screen allows")
            await safe("()=>{window.__a3dRightSetWidth(560);window.__a3dSetLeftWidth(null);}")
            await page.wait_for_timeout(200)
            await page.set_viewport_size({'width': 1100, 'height': 900})
            await page.wait_for_timeout(500)
            s1, gk = await rp(), await geo()
            ck(s1.get('max') == rmax(1100) == 484 and gk.get('w') == 484 and s1.get('kept') == 560 and gk.get('draw') == KEEP and gk.get('vmax') == '484',
               "on a 1100 px screen Properties stops at 484, the drawing keeping 320 beside the left panel; the 560 kept (%s)" % [s1.get('max'), gk.get('w'), s1.get('kept'), gk.get('draw')])
            await page.set_viewport_size({'width': 1500, 'height': 950})
            await page.wait_for_timeout(500)
            ck((await geo()).get('w') == 560, "back on the wide screen it is 560 again")
            await page.set_viewport_size({'width': 1100, 'height': 900})
            await page.wait_for_timeout(500)
            await safe("()=>window.__a3dRightSetWidth(null)")
            await page.wait_for_timeout(200)
            sq = []
            for k in range(5):
                await press()
                g = await geo()
                sq.append((g.get('w'), g.get('draw')))
            ck([w for w, d in sq] == steps_from(280, 484)[:5] == [320, 400, 480, 484, 240] and min(d for w, d in sq) >= KEEP and sq[3][1] == KEEP,
               "the presses go 320, 400, 480, then 484 and back to 240; the drawing never under 320 (%s)" % sq)
            await safe("()=>window.__a3dRightSetWidth(480)")
            await page.wait_for_timeout(200)
            ck((await geo()).get('label') == 'Properties width 480 px: widen to 484', "at 480 it says the next press goes to 484 (%s)" % (await geo()).get('label'))
            # the left panel gives way to Properties, and the drawing keeps 320 as Properties grows
            await safe("()=>{window.__a3dRightSetWidth(240);window.__a3dSetLeftWidth(560);}")
            await page.wait_for_timeout(250)
            gL = await geo()
            ck(gL.get('lw') == 1100 - RAIL - 240 - KEEP and gL.get('draw') == KEEP, "Properties at 240, the left panel takes the room up to the drawing's 320 (%s)" % [gL.get('lw'), gL.get('draw')])
            mid = await safe("""()=>{var g=document.querySelector('#a3d-right .a3d-rgrip'),r=g.getBoundingClientRect(),x=r.left+r.width/2,y=400,a=document.getElementById('acad3d');
              var ev=function(t,dx){g.dispatchEvent(new PointerEvent(t,{pointerId:21,pointerType:'mouse',button:0,buttons:1,isPrimary:true,clientX:x+dx,clientY:y,bubbles:true,cancelable:true}));};
              var m=function(){var p=document.getElementById('a3d-right').getBoundingClientRect();return [Math.round(p.width),Math.round(p.left-a.getBoundingClientRect().left),
                Math.round(document.getElementById('a3d-leftpanel').getBoundingClientRect().width),document.body.classList.contains('a3d-rpdrag')];};
              ev('pointerdown',0);ev('pointermove',-100);var m1=m();ev('pointermove',-900);var m2=m();ev('pointerup',-900);return [m1,m2,m()];}""") or [[], [], []]
            await page.wait_for_timeout(250)
            ck(len(mid) == 3 and mid[0][:3] == [340, KEEP, 1100 - RAIL - 340 - KEEP] and mid[0][3] is True,
               "mid-drag the left panel gives way as Properties grows, at once, not easing behind it; the drawing at 320 (%s)" % mid[:1])
            ck(len(mid) == 3 and mid[1][:3] == [484, KEEP, LEFT_MIN] and mid[2][:3] == [484, KEEP, LEFT_MIN] and mid[2][3] is False and (await rp()).get('kept') == 484,
               "dragged far left it stops at 484, the left panel at its 242; let go, it is kept (%s)" % mid[1:])
            await safe("()=>{window.__a3dRightSetWidth(300);document.getElementById('a3d-shell').querySelector('.a3d-panelcollapse').click();}")
            await page.wait_for_timeout(400)
            await safe("()=>document.querySelector('#a3d-right .a3d-rgrip').focus()")
            await page.keyboard.press('End')
            await page.wait_for_timeout(150)
            sc = await geo()
            await page.keyboard.press('ArrowLeft')
            await page.wait_for_timeout(150)
            sk = await geo()
            ck(sk.get('w') == 484 and kept(sk) == 484, "a key past the widest is refused: 484, and 484 kept (%s, %s)" % (sk.get('w'), kept(sk)))
            await safe("()=>document.querySelector('#a3d-rail .a3d-paneltoggle').click()")
            await page.wait_for_timeout(450)
            so = await geo()
            ck(sc.get('w') == 484 and sc.get('al') == RAIL and so.get('w') == 484 and so.get('draw') == KEEP and so.get('lw') == LEFT_MIN,
               "with the left panel shut End still stops at 484, so the drawing keeps 320 when it opens again (%s)" % [sc.get('w'), so.get('draw'), so.get('lw')])
            await safe("()=>{window.__a3dSetLeftWidth(null);window.__a3dRightSetWidth(null);}")
            await page.set_viewport_size({'width': 1500, 'height': 950})
            await page.wait_for_timeout(500)

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the edge from the keyboard")
            ed = await safe("""()=>{var g=document.querySelector('#a3d-right .a3d-rgrip'),n=document.getElementById(g.getAttribute('aria-labelledby')||'-');
              return {role:g.getAttribute('role'),or:g.getAttribute('aria-orientation'),ctl:g.getAttribute('aria-controls'),name:n?n.textContent:null,tab:g.tabIndex,
                hid:g.getAttribute('aria-hidden'),now:g.getAttribute('aria-valuenow'),min:g.getAttribute('aria-valuemin'),max:g.getAttribute('aria-valuemax')};}""") or {}
            ck(ed.get('role') == 'separator' and ed.get('or') == 'vertical' and ed.get('ctl') == 'a3d-right' and ed.get('name') == 'Properties' and ed.get('tab') == 0 and ed.get('hid') is None,
               "the edge is a focusable vertical separator controlling Properties, named Properties (%s)" % ed)
            ck([ed.get('now'), ed.get('min'), ed.get('max')] == ['280', '240', str(rmax(1500))], "its value is the width, from 240 to what the screen allows (%s)" % [ed.get('now'), ed.get('min'), ed.get('max')])
            cid = await safe("()=>{window.__a3dColumnAt([20,20],0,0.4,0.4,3);var s=window.__a3dState().objs;var id=s[s.length-1].id;window.__a3dSelectFor([id]);return id;}")
            pos0 = (await safe("(i)=>window.__a3dObjSnapshot(i)", cid) or {}).get('pos')
            await safe("()=>document.querySelector('#a3d-right .a3d-rgrip').focus()")
            x0 = (await geo()).get('gl')
            kw = []
            for key in ('ArrowLeft', 'Shift+ArrowLeft', 'ArrowRight'):
                await page.keyboard.press(key)
                await page.wait_for_timeout(80)
                kw.append((await geo()).get('w'))
            x1 = (await geo()).get('gl')
            ck(kw == [296, 360, 344] and x0 is not None and x1 is not None and abs((x0 - x1) - 64) < 0.6,
               "Left widens it 16 px, Shift+Left 64, Right narrows it 16: the edge moves the way the arrow points (%s, moved %s px left)" % (kw, None if x0 is None or x1 is None else x0 - x1))
            await page.keyboard.press('Home')
            await page.wait_for_timeout(80)
            h1 = (await geo()).get('w')
            await page.keyboard.press('End')
            await page.wait_for_timeout(80)
            h2 = await geo()
            ck(h1 == 240 and h2.get('w') == rmax(1500) and h2.get('now') == str(rmax(1500)), "Home the narrowest, End the widest the screen allows (%s, %s)" % (h1, h2.get('w')))
            fv = await safe("()=>{var g=document.querySelector('#a3d-right .a3d-rgrip');return [document.activeElement===g,g.matches(':focus-visible'),getComputedStyle(g).backgroundImage.indexOf('gradient')>=0];}") or []
            ck(fv == [True, True, True], "focused from the keyboard, the edge shows it (%s)" % fv)
            await page.keyboard.press('ArrowLeft')
            await page.keyboard.press('ArrowUp')
            await page.keyboard.press('d')
            await page.wait_for_timeout(150)
            pos1 = (await safe("(i)=>window.__a3dObjSnapshot(i)", cid) or {}).get('pos')
            pal = await safe("()=>{var p=document.getElementById('a3d-cmdpal');return !!(p&&p.classList.contains('show'));}")
            ck(pos0 and pos1 == pos0 and pal is False and await safe("()=>document.activeElement.className") == 'a3d-rgrip',
               "the keys are the edge's: the selected column does not move, a letter opens no search (%s, %s)" % (pos0, pos1))
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(250)
            en = await safe("()=>[document.body.classList.contains('a3d-rmin'),Math.round(document.getElementById('a3d-right').getBoundingClientRect().width),document.activeElement&&document.activeElement.id,getComputedStyle(document.querySelector('#a3d-right .a3d-rgrip')).display,JSON.parse(localStorage.getItem('acad3dRightPanel')||'{}').min]") or []
            ck(en == [True, 42, 'a3d-rminbtn', 'none', True], "Enter minimises it to its strip, the edge goes, the focus is on the minimise button (%s)" % en)
            await page.keyboard.press('Enter')
            await page.wait_for_timeout(250)
            ex = await geo()
            ck(ex.get('min') is False and ex.get('w') == rmax(1500) and ex.get('gd') != 'none' and ex.get('bd') != 'none',
               "Enter on the minimise button brings it back at its width, with its edge and its button (%s)" % [ex.get('min'), ex.get('w')])
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRightSetWidth(null);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. any pointer")
            await page.wait_for_timeout(200)
            gm = await geo()
            y, sx = 420, gm.get('rl', 0) + 2   # inside the panel: it clips the edge's 3 px outside it
            await page.mouse.move(sx, y)
            await page.mouse.down()
            await page.mouse.move(sx - 40, y, steps=4)
            dragging = await safe("()=>document.body.classList.contains('a3d-rpdrag')")
            await page.mouse.move(sx - 60, y, steps=4)
            await page.mouse.up()
            await page.wait_for_timeout(200)
            gm2 = await geo()
            ck(dragging is True and gm2.get('w') == 340 and kept(gm2) == 340 and await safe("()=>document.body.classList.contains('a3d-rpdrag')") is False,
               "a mouse drags the edge 60 px left: 340 px, kept (%s, %s)" % (gm2.get('w'), gm2.get('store')))
            cx = await safe("""()=>{var g=document.querySelector('#a3d-right .a3d-rgrip'),r=g.getBoundingClientRect(),x=r.left+r.width/2,y=300;
              var ev=function(t,dx){g.dispatchEvent(new PointerEvent(t,{pointerId:7,pointerType:'touch',isPrimary:true,clientX:x+dx,clientY:y,bubbles:true,cancelable:true}));};
              ev('pointerdown',0);ev('pointermove',-60);var m=Math.round(document.getElementById('a3d-right').getBoundingClientRect().width);ev('pointercancel',-60);return m;}""")
            await page.wait_for_timeout(200)
            gc = await geo()
            ck(cx == 400 and gc.get('w') == 340 and kept(gc) == 340, "a drag follows the pointer, and a cancelled one puts the width back (%s, %s)" % (cx, gc.get('w')))
            await page.mouse.dblclick(gc.get('rl', 0) + 2, y)
            await page.wait_for_timeout(200)
            gd = await geo()
            ck(gd.get('w') == 280 and kept(gd) is None, "a double click on the edge puts it back to 280 and forgets the width (%s)" % gd.get('store'))
            rb = await safe("""()=>{var g=document.querySelector('#a3d-right .a3d-rgrip'),r=g.getBoundingClientRect(),x=r.left+r.width/2,y=300;
              var ev=function(t,dx){g.dispatchEvent(new PointerEvent(t,{pointerId:9,pointerType:'mouse',button:2,buttons:2,isPrimary:true,clientX:x+dx,clientY:y,bubbles:true,cancelable:true}));};
              ev('pointerdown',0);ev('pointermove',-80);var m=[Math.round(document.getElementById('a3d-right').getBoundingClientRect().width),document.body.classList.contains('a3d-rpdrag')];ev('pointerup',-80);return m;}""")
            await page.wait_for_timeout(200)
            ck(rb == [280, False] and kept(await geo()) is None, "the right button does not drag it (%s)" % rb)

            c2 = await browser.new_context(viewport={'width': 1180, 'height': 820}, has_touch=True, is_mobile=True)
            p2 = await c2.new_page()
            p2.on('pageerror', lambda e: errs.append(str(e)))
            await within(p2.goto('file://' + str(HTML)), 'goto tablet on its side')
            await p2.wait_for_timeout(2300)
            t0 = await geo(p2)
            ck(t0.get('pos') not in ('absolute', 'fixed') and t0.get('gd') != 'none' and t0.get('gw') == 12 and 0 <= t0.get('gl', -9) - t0.get('rl', 0) <= 1.5 and t0.get('bw') == 36 and t0.get('bh') == 36,
               "a tablet on its side: Properties docked, a 12 px edge inside it (past its 1 px border) and a 36 px button (%s)" % [t0.get('pos'), t0.get('gd'), t0.get('gw'), t0.get('gl'), t0.get('rl'), t0.get('bw'), t0.get('bh')])
            ln = await safe("()=>getComputedStyle(document.querySelector('#a3d-right .a3d-rgrip')).backgroundImage", pg=p2) or ''
            ck('gradient' in ln, "the edge shows itself without a hover (%s)" % ln[:60])
            cdp = await c2.new_cdp_session(p2)

            async def touch(kind, xx, yy):
                pts = [] if kind == 'touchEnd' else [{'x': xx, 'y': yy, 'id': 1}]
                await cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': pts})

            bx = t0.get('gl', 0) + 6
            await touch('touchStart', bx, 500)
            for k in range(1, 7):
                await touch('touchMove', bx - k * 20, 500)
            await touch('touchEnd', 0, 0)
            await p2.wait_for_timeout(300)
            t1 = await geo(p2)
            ck(t1.get('w') == 400 and kept(t1) == 400, "a finger drags it 120 px wider, kept (%s)" % t1.get('w'))
            bb = await safe("()=>{var r=document.querySelector('#a3d-right [data-rpwidth]').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}", pg=p2) or [0, 0]
            await p2.touchscreen.tap(bb[0], bb[1])
            await p2.wait_for_timeout(300)
            t2 = await geo(p2)
            ck(t2.get('w') == 480 and t2.get('label') == 'Properties width 480 px: widen to %d' % rmax(1180),
               "a tap on the button takes it to the next step, 480 (%s, %r)" % (t2.get('w'), t2.get('label')))
            await c2.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 5. where Properties is a drawer or a sheet")
            mr = await safe("""()=>{var out=[];[].forEach.call(document.styleSheets,function(s){var rs;try{rs=s.cssRules;}catch(e){return;}
              [].forEach.call(rs,function(r){if(r.type!==4)return;[].forEach.call(r.cssRules,function(q){if(q.selectorText&&q.selectorText.indexOf('.a3d-rpwbtn')>=0&&q.style.display==='none'&&q.selectorText.indexOf('.a3d-rgrip')>=0)out.push(r.conditionText||r.media.mediaText);});});});return out;}""") or []
            mq = (await rp()).get('mq') or ''
            ck(len(mr) == 1 and re.sub(r'\s', '', mr[0]) == re.sub(r'\s', '', mq) and mq,
               "one rule hides the edge and the button, and its query is the code's own (%s, %s)" % (mr, mq))
            await safe("()=>window.__a3dRightSetWidth(400)")
            sizes = ((1500, 950), (1025, 700), (1024, 700), (1300, 501), (1300, 500), (1000, 800), (932, 430), (844, 390), (820, 1180), (390, 844), (1180, 820))
            agree, rows = True, []
            for (vw, vh) in sizes:
                await page.set_viewport_size({'width': vw, 'height': vh})
                await page.wait_for_timeout(250)
                await safe("()=>{var r=document.getElementById('a3d-right');if(getComputedStyle(r).position==='absolute'||getComputedStyle(r).position==='fixed')r.classList.add('open');}")
                await page.wait_for_timeout(120)
                s, g = await rp(), await geo()
                docked = g.get('pos') not in ('absolute', 'fixed')
                want = vw > 1024 and vh > 500
                ok = (s.get('docked') is docked is want and (g.get('bd') != 'none') is want and (g.get('gd') != 'none') is want
                      and (g.get('w') == 400 if want else g.get('w') != 400))
                if not ok:
                    rows.append((vw, vh, docked, s.get('docked'), g.get('bd'), g.get('gd'), g.get('w')))
                agree = agree and ok
                await safe("()=>document.getElementById('a3d-right').classList.remove('open')")
            ck(agree, "docked, button and edge only over 1024 px wide and 500 high, the code agreeing with the layout at %d sizes; the 400 kept is not forced on a drawer or a sheet (%s)"
               % (len(sizes), rows[:3] or 'all agree'))
            await page.set_viewport_size({'width': 1500, 'height': 950})
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dRightSetWidth(null)")
            for nm, vw, vh, tch in (('a window 1000 by 800', 1000, 800, False), ('a phone on its side wider than 900', 932, 430, True), ('a short window', 1280, 480, False),
                                    ('an upright tablet', 820, 1180, True), ('a phone', 390, 844, True)):
                c3 = await browser.new_context(viewport={'width': vw, 'height': vh}, has_touch=tch, is_mobile=tch and vw < 700)
                p3 = await c3.new_page()
                p3.on('pageerror', lambda e: errs.append(str(e)))
                await within(p3.goto('file://' + str(HTML)), 'goto ' + nm)
                await p3.wait_for_timeout(2300)
                await p3.evaluate("()=>{window.__a3dColumnAt([10,10],0,0.4,0.4,3);var s=window.__a3dState().objs;window.__a3dSelectFor([s[s.length-1].id]);window.__a3dRefreshProps();}")
                await p3.evaluate("()=>{var b=document.querySelector('.a3d-rdrawerbtn');if(b&&getComputedStyle(b).display!=='none')b.click();else document.getElementById('a3d-right').classList.add('open');}")
                await p3.wait_for_timeout(300)
                o = await geo(p3)
                await p3.evaluate("()=>document.getElementById('a3d-rminbtn').click()")
                await p3.wait_for_timeout(300)
                c = await geo(p3)
                ck(o.get('rd') != 'none' and o.get('pos') in ('absolute', 'fixed') and o.get('bd') == 'none' and o.get('gd') == 'none'
                   and c.get('rd') == 'none' and c.get('min') is False and (c.get('store') or '{}').find('"min":true') < 0,
                   "%s: Properties opens as a drawer or sheet with no button and no edge, and its arrow closes it rather than minimise it (%s)"
                   % (nm, [o.get('pos'), o.get('bd'), o.get('gd'), c.get('rd'), c.get('min'), c.get('w')]))
                await c3.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the shell's audit")
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok') is True and not au.get('unclaimed'), "the shell's audit knows the button, the edge and the minimise (%s)" % au.get('unclaimed'))
            inj = await safe("""()=>{var h=document.querySelector('#a3d-right .a3d-palhd'),b=document.createElement('button'),s=document.createElement('div'),f=document.createElement('button');
              b.textContent='Stray';b.className='a3d-stray1';h.appendChild(b);var a1=window.__a3dShellAudit();b.remove();
              s.setAttribute('role','separator');s.tabIndex=0;s.className='a3d-stray2';s.style.cssText='display:block;width:6px;height:20px';h.appendChild(s);var a2=window.__a3dShellAudit();s.remove();
              f.textContent='Field';f.className='a3d-stray3';document.getElementById('a3d-propsbody').appendChild(f);var a3=window.__a3dShellAudit();f.remove();
              var cls=function(a){return (a.unclaimed||[]).map(function(u){return u.cls;});};return [a1.ok,cls(a1),a2.ok,cls(a2),a3.ok,cls(a3)];}""") or []
            ck(len(inj) == 6 and inj[0] is False and 'a3d-stray1' in inj[1], "it reaches Properties' header: a stray button there is reported (%s)" % inj[:2])
            ck(len(inj) == 6 and inj[2] is False and 'a3d-stray2' in inj[3], "a focusable edge counts as a control: a stray one is reported (%s)" % inj[2:4])
            ck(len(inj) == 6 and inj[4] is True and not inj[5], "Properties' body is not the shell's: a button there is left to its own phase (%s)" % inj[4:])

            ck(not errs, "no page errors (%s)" % errs[:3])
            ck(not warns, "nothing went wrong quietly: no [BIM] warnings (%s)" % warns[:3])
        except Stalled as e:
            ck(False, "the harness stalled at: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite ran to its end")
        await browser.close()
    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    print("RESULT: " + ("PASS" if not ck.bad else "FAIL"))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
