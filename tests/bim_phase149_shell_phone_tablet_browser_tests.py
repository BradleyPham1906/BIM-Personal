#!/usr/bin/env python3
"""bim_phase149_shell_phone_tablet_browser_tests.py -- V149: the shell on a phone and a tablet.

Measured in the browser, on five screens:
  1. A PHONE UPRIGHT (390 x 844, touch): the rail is a tab bar along the bottom, labelled, finger
     sized; the drawing takes the whole width; the left panel is a drawer, shut at the start, opened
     by a tab and shut by the same tab, a tap beside it or Esc; More shows the rail's tools over the
     bar, and their menus open on the screen; a message clears the bar; Properties' sheet still
     opens; two fingers still zoom.
  2. A PHONE ON ITS SIDE (844 x 390) and 3. A TABLET UPRIGHT (820 x 1180): the rail down the left,
     the same drawer over the drawing, opened by the toolbar's menu button too.
  4. A TABLET ON ITS SIDE (1180 x 820) and 5. A COMPUTER (1500 x 950): as before -- the panel
     beside the drawing, the tab bar's More nowhere.
  6. THE SCREEN TURNS: a computer's window narrowed to a phone shuts the panel and widens the
     drawing; widened again, the panel is as it was.
  7. SAFE AREAS: viewport-fit=cover, and the bars padded by env(safe-area-inset-*).

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


BOX = """(s)=>{var e=document.querySelector(s);if(!e)return null;var r=e.getBoundingClientRect(),c=getComputedStyle(e);
  return {x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),r:Math.round(r.right),b:Math.round(r.bottom),d:c.display,v:c.visibility,o:+c.opacity};}"""


async def open_page(pw, vp, touch):
    b = await pw.chromium.launch()
    c = await b.new_context(viewport=vp, has_touch=touch, is_mobile=touch)
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
    await p.wait_for_timeout(300)
    return b, c, p, safe, errs


def shown(bx):
    return bool(bx) and bx['d'] != 'none' and bx['v'] != 'hidden' and bx['o'] > 0.5 and bx['w'] > 0 and bx['h'] > 0


async def run():
    ck = CK
    async with async_playwright() as pw:
        # ---------------------------------------------------------------------------------------
        print("\n-- 1. a phone, upright")
        b, c, p, safe, errs = await open_page(pw, {'width': 390, 'height': 844}, True)
        try:
            has = await safe("()=>window.__acad3dV149")
            ck(bool(has) and 'tabbar' in has and 'leftdrawer' in has, "__acad3dV149 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 149, "the app says V149 or later (%s)" % (mv and mv.group(1)))
            st = await safe("()=>window.__a3dShellTier()") or {}
            ck(st.get('tier') == 'phone' and await safe("()=>document.body.classList.contains('a3d-tier-phone')&&document.body.classList.contains('a3d-tier-overlay')"),
               "the phone layout (%s)" % st)
            ck(st.get('open') is False and not shown(await safe(BOX, '#a3d-leftpanel')), "the left panel is shut at the start")
            cv = await safe(BOX, '#a3d-canvas')
            rail = await safe(BOX, '#a3d-rail')
            acad = await safe(BOX, '#acad3d')
            ck(cv and cv['x'] == 0 and cv['w'] == 390 and st.get('leftW') == '0px', "the drawing takes the whole width: 390 px, where V148 left it 94 (%s)" % cv)
            ck(rail and rail['x'] == 0 and rail['w'] == 390 and rail['b'] == 844 and 56 <= rail['h'] <= 70, "the rail is a bar along the bottom, the screen's width (%s)" % rail)
            ck(acad and acad['b'] <= rail['y'] + 1, "and the drawing area stops above it (%d <= %d)" % (acad['b'], rail['y']))
            tabs = await safe("""()=>[].map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn,#a3d-rail .a3d-railmore'),function(e){var r=e.getBoundingClientRect();
              return {k:e.getAttribute('data-tab')||'more',w:Math.round(r.width),h:Math.round(r.height),x:Math.round(r.left),r:Math.round(r.right),lab:getComputedStyle(e,'::after').content};})""") or []
            ck([t['k'] for t in tabs] == ['layers', 'presentation', 'browser', 'assets', 'analyze', 'more'], "its tabs: Layers, Present, Browser, Assets, Analyze, and More (%s)" % [t['k'] for t in tabs])
            ck(all(t['h'] >= 44 and t['w'] >= 44 and t['x'] >= 0 and t['r'] <= 390 for t in tabs), "every tab 44 px or more, on the screen (%s)" % [(t['w'], t['h']) for t in tabs])
            ck([t['lab'] for t in tabs] == ['"Layers"', '"Present"', '"Browser"', '"Assets"', '"Analyze"', '"More"'], "each labelled under its icon (%s)" % [t['lab'] for t in tabs])
            ck(not shown(await safe(BOX, '#a3d-rail .a3d-paneltoggle')) and not shown(await safe(BOX, '.a3d-drawerbtn')),
               "the rail's panel toggle and the toolbar's menu button give way to the tabs")
            # the drawer
            await p.tap('#a3d-rail [data-tab="layers"]')
            await p.wait_for_timeout(300)
            st = await safe("()=>window.__a3dShellTier()") or {}
            lp = await safe(BOX, '#a3d-leftpanel')
            ck(st.get('open') and await safe("()=>document.getElementById('a3d-shell').getAttribute('data-tab')") == 'layers' and shown(lp) and lp['x'] >= 0 and lp['r'] <= 390 * 0.9 + 1 and lp['b'] <= rail['y'] + 1,
               "Layers opens the drawer on Layers, over the drawing, short of the screen's edge and above the bar (%s)" % lp)
            ck(await safe("()=>!!document.querySelector('#a3d-leftpanel .a3d-lyp')"), "with the layer tree in it")
            cv2 = await safe(BOX, '#a3d-canvas')
            ck(cv2 and cv2['w'] == 390 and cv2['x'] == 0, "the drawing stays where it is under it: a drawer, not a column")
            scr = await safe(BOX, '#a3d-shellscrim')
            ck(shown(scr) and scr['w'] >= 390, "a shade over the rest of the screen")
            await p.tap('#a3d-rail [data-tab="layers"]')
            await p.wait_for_timeout(300)
            ck(not (await safe("()=>window.__a3dShellTier()") or {}).get('open') and not shown(await safe(BOX, '#a3d-shellscrim')), "Layers again shuts it, shade and all")
            await p.tap('#a3d-rail [data-tab="analyze"]')
            await p.wait_for_timeout(300)
            ck((await safe("()=>window.__a3dShellTier()") or {}).get('open') and await safe("()=>!!document.querySelector('#a3d-leftpanel .a3d-analyze-wrap')"), "Analyze opens it on Analyze")
            await p.tap('#a3d-shellscrim', position={'x': 375, 'y': 420})
            await p.wait_for_timeout(300)
            ck(not (await safe("()=>window.__a3dShellTier()") or {}).get('open'), "a tap beside the drawer shuts it")
            act = await safe("()=>{var a=document.querySelector('#a3d-rail .a3d-railbtn.active');return a?getComputedStyle(a).backgroundColor:null;}")
            ck(act in ('rgba(0, 0, 0, 0)', 'transparent'), "shut, no tab looks open (%s)" % act)
            await p.tap('#a3d-rail [data-tab="browser"]')
            await p.wait_for_timeout(250)
            await p.keyboard.press('Escape')
            await p.wait_for_timeout(250)
            ck(not (await safe("()=>window.__a3dShellTier()") or {}).get('open'), "Esc shuts it")
            # More
            await p.tap('#a3d-rail [data-railmore]')
            await p.wait_for_timeout(250)
            ru = await safe("""()=>[].map.call(document.querySelectorAll('#a3d-railutil .a3d-ru'),function(e){var r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom),Math.round(r.width),Math.round(r.height)];})""") or []
            ck(len(ru) == 6 and all(r[4] >= 44 and r[5] >= 44 and r[0] >= 0 and r[2] <= 390 and r[3] <= rail['y'] for r in ru) and
               await safe("()=>document.querySelector('#a3d-rail [data-railmore]').getAttribute('aria-expanded')") == 'true',
               "More shows the rail's six tools over the bar, 44 px each, on the screen (%s)" % ru)
            await p.tap('#a3d-railutil [data-a3drumenu="zoom"]')
            await p.wait_for_timeout(300)
            pop = await safe(BOX, '#a3d-rupop')
            ck(shown(pop) and pop['x'] >= 0 and pop['r'] <= 390 and pop['b'] <= rail['y'], "Zoom's menu opens on the screen, above the bar (%s)" % pop)
            await p.tap('#a3d-canvas', position={'x': 120, 'y': 220})
            await p.wait_for_timeout(250)
            ck(not (await safe("()=>window.__a3dShellTier()") or {}).get('more') and not shown(await safe(BOX, '#a3d-railutil')), "a tap on the drawing puts More away")
            # the message, the sheet
            await safe("()=>window.__a3dToast?window.__a3dToast('V149 probe'):null")
            await safe("()=>window.__a3dRunCmd&&window.__a3dRunCmd('zoomextents')")
            await p.wait_for_timeout(200)
            tst = await safe(BOX, '#a3d-toast')
            ck(tst and tst['b'] <= rail['y'], "a message shows above the bar, not behind it (%s)" % tst)
            await p.tap('[data-a3d="rdrawer"]')
            await p.wait_for_timeout(300)
            rp = await safe(BOX, '#a3d-right')
            ck(rp and rp['d'] != 'none' and rp['w'] == 390 and rp['b'] == 844, "Props still opens Properties' sheet from the bottom (%s)" % rp)
            await p.tap('[data-a3d="rdrawer"]')
            await p.wait_for_timeout(200)
            # two fingers
            d0 = (await safe("()=>window.__a3dCamSet({})") or {}).get('dist')
            cdp = await c.new_cdp_session(p)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': 160, 'y': 400, 'id': 1}, {'x': 230, 'y': 400, 'id': 2}]})
            for k in range(1, 7):
                await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': 160 - 12 * k, 'y': 400, 'id': 1}, {'x': 230 + 12 * k, 'y': 400, 'id': 2}]})
                await p.wait_for_timeout(30)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
            await p.wait_for_timeout(150)
            d1 = (await safe("()=>window.__a3dCamSet({})") or {}).get('dist')
            ck(d0 and d1 and d1 < d0 * 0.8, "two fingers spread on the full-width drawing zoom in (%.1f -> %.1f)" % (d0 or 0, d1 or 0))
            # ---- typing on a phone (149b)
            print("\n-- 1b. typing on a phone")
            async def nomi(route):
                await route.fulfill(status=200, headers={'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                                    body='[{"lat":"51.5034","lon":"-0.1276","display_name":"10 Downing Street, London"}]')
            await c.route('https://nominatim.openstreetmap.org/**', nomi)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}")
            await p.tap('[data-a3d="rdrawer"]')
            await p.wait_for_timeout(300)
            await safe("()=>{var g=document.querySelector('#a3d-propsbody [data-a3dpgrp=\"Map\"]');if(g&&!g.nextElementSibling.offsetHeight)g.click();}")
            await p.wait_for_timeout(150)
            small = await safe("""()=>[].filter.call(document.querySelectorAll('input,select,textarea'),function(e){if(/checkbox|radio|range|color|file|hidden/.test(e.type))return false;
              return parseFloat(getComputedStyle(e).fontSize)<16;}).map(function(e){return e.getAttribute('data-propmap')||e.getAttribute('data-propmodel')||e.className||e.tagName;})""")
            n_f = await safe("()=>document.querySelectorAll('input:not([type=checkbox]):not([type=radio]),select,textarea').length")
            ck(small == [] and n_f and n_f > 10, "every one of the %d fields is 16 px, so iOS has nothing to zoom in on (%s)" % (n_f or 0, (small or [])[:5]))
            fz = await safe("()=>getComputedStyle(document.querySelector('#a3d-propsbody [data-propmap=\"addr\"]')).fontSize")
            await p.tap('#a3d-propsbody [data-propmap="addr"]')
            await p.keyboard.type('10 Downing Street, London')
            await p.keyboard.press('Enter')
            await p.wait_for_timeout(900)
            ss = await safe("()=>window.__a3dSunSettings()") or {}
            ck(fz == '16px' and abs(float(ss.get('lat') or 0) - 51.5034) < 1e-6 and abs(float(ss.get('lon') or 0) + 0.1276) < 1e-6,
               "the address typed on the phone and sent with the keyboard's Enter finds the place (%s, %s)" % (ss.get('lat'), ss.get('lon')))
            # 149c: Find after the field has been drawn again (the keyboard going changes the screen's size)
            await p.wait_for_timeout(1100)   # Nominatim's one-a-second
            await safe("()=>{var e=document.querySelector('#a3d-propsbody [data-propmap=\"addr\"]');e.value='';e.dispatchEvent(new Event('input',{bubbles:true}));}")
            await p.tap('#a3d-propsbody [data-propmap="addr"]')
            await p.keyboard.type('Paris')
            await safe("()=>document.activeElement.blur()")
            await safe("()=>window.__a3dRefreshProps()")
            kept = await safe("()=>document.querySelector('#a3d-propsbody [data-propmap=\"addr\"]').value")
            await safe("()=>window.__a3dSunSettings&&0")
            await p.tap('#a3d-propsbody [data-propmapact="find"]')
            await p.wait_for_timeout(900)
            ck(kept == 'Paris' and 'Type an address' not in (await safe("()=>(document.getElementById('a3d-toast')||{}).textContent") or ''),
               "typed, the keyboard put away and Properties drawn again: the field keeps 'Paris' and Find looks it up (%r)" % kept)
            await p.wait_for_timeout(400)
            kb = await safe("()=>window.__a3dKbFit(320)")
            sh = await safe(BOX, '#a3d-right')
            ck(kb == 320 and sh and sh['b'] == 844 - 320 and sh['y'] >= 44, "with the keyboard up (320 px), Properties sits on it, not under it (%s)" % sh)
            await safe("()=>window.__a3dKbFit(0)")
            await p.tap('[data-a3d="rdrawer"]')
            await p.wait_for_timeout(250)
            await p.tap('#a3d-rail [data-tab="layers"]')
            await p.wait_for_timeout(300)
            await safe("()=>window.__a3dKbFit(300)")
            lp = await safe(BOX, '#a3d-leftpanel')
            ck(lp and lp['b'] == 844 - 300, "and so does the drawer (%s)" % lp)
            ck(await safe("()=>window.__a3dKbFit(40)") == 0 and not await safe("()=>document.body.classList.contains('a3d-kb-up')"),
               "a browser's own bar sliding in and out (40 px) is not taken for a keyboard")
            await p.tap('#a3d-rail [data-tab="layers"]')
            await p.wait_for_timeout(250)
            # the audit with everything out
            await p.tap('#a3d-rail [data-tab="assets"]')
            await p.wait_for_timeout(200)
            await safe("()=>window.__a3dShellMore(true)")
            au = await safe("()=>window.__a3dShellAudit()") or {}
            ck(au.get('ok'), "the shell audit is clean with the drawer and More out (%s)" % au.get('unclaimed'))
            ck(not errs, "no page errors (%s)" % errs[:3])
        except Stalled as s:
            ck(False, "phone: the harness stalled at %s" % s)
        except Exception:
            traceback.print_exc()
            ck(False, "phone: ran to its end")
        await b.close()

        # ---------------------------------------------------------------------------------------
        for name, vp in (('2. a phone on its side', {'width': 844, 'height': 390}), ('3. a tablet upright', {'width': 820, 'height': 1180})):
            print("\n-- " + name)
            b, c, p, safe, errs = await open_page(pw, vp, True)
            W = vp['width']
            try:
                st = await safe("()=>window.__a3dShellTier()") or {}
                ck(st.get('tier') == 'overlay' and st.get('open') is False and st.get('leftW') == '54px', "%s: the rail and a drawer, shut at the start (%s)" % (name[3:], st))
                rail = await safe(BOX, '#a3d-rail')
                cv = await safe(BOX, '#a3d-canvas')
                ck(rail and rail['x'] == 0 and rail['w'] == 54 and rail['h'] > rail['w'], "the rail down the left (%s)" % rail)
                ck(cv and cv['x'] == 54 and cv['r'] == W, "the drawing from the rail to the edge: %d px (%s)" % (cv['w'], cv))
                ck(not shown(await safe(BOX, '#a3d-rail [data-railmore]')), "no More: the rail has room for its tools")
                btn = await safe("()=>{var r=document.querySelector('#a3d-rail .a3d-railbtn').getBoundingClientRect();return [r.width,r.height];}")
                ck(btn and btn[0] >= 44 and btn[1] >= 44, "its buttons are 44 px for a finger (%s)" % btn)
                opener = '.a3d-drawerbtn' if vp['height'] <= 500 else '#a3d-rail .a3d-paneltoggle'   # a phone on its side has the toolbar's menu button; a tablet the rail's toggle
                ck(shown(await safe(BOX, opener)), "%s is there" % ('the toolbar\'s menu button' if vp['height'] <= 500 else 'the rail\'s panel toggle'))
                await p.tap(opener)
                await p.wait_for_timeout(300)
                lp = await safe(BOX, '#a3d-leftpanel')
                cv2 = await safe(BOX, '#a3d-canvas')
                ck((await safe("()=>window.__a3dShellTier()") or {}).get('open') and shown(lp) and lp['x'] == 54 and lp['r'] <= W - 20 and cv2['x'] == 54 and cv2['w'] == cv['w'],
                   "and opens the drawer beside the rail, over the drawing, which stays put (%s)" % lp)
                await p.tap('#a3d-shellscrim', position={'x': W - 8, 'y': vp['height'] // 2})
                await p.wait_for_timeout(300)
                ck(not (await safe("()=>window.__a3dShellTier()") or {}).get('open'), "a tap beside it shuts it")
                await p.tap('#a3d-rail [data-tab="assets"]')
                await p.wait_for_timeout(250)
                ck((await safe("()=>window.__a3dShellTier()") or {}).get('open') and await safe("()=>document.getElementById('a3d-shell').getAttribute('data-tab')") == 'assets', "a rail tab opens it on that tab")
                await p.tap('#a3d-rail [data-tab="assets"]')
                await p.wait_for_timeout(250)
                ck(not (await safe("()=>window.__a3dShellTier()") or {}).get('open'), "and the same tab shuts it")
                ck(not errs, "no page errors (%s)" % errs[:3])
            except Stalled as s:
                ck(False, "%s: the harness stalled at %s" % (name, s))
            except Exception:
                traceback.print_exc()
                ck(False, "%s: ran to its end" % name)
            await b.close()

        # ---------------------------------------------------------------------------------------
        for name, vp, touch in (('4. a tablet on its side', {'width': 1180, 'height': 820}, True), ('5. a computer', {'width': 1500, 'height': 950}, False)):
            print("\n-- " + name)
            b, c, p, safe, errs = await open_page(pw, vp, touch)
            try:
                st = await safe("()=>window.__a3dShellTier()") or {}
                lp = await safe(BOX, '#a3d-leftpanel')
                cv = await safe(BOX, '#a3d-canvas')
                ck(st.get('tier') == 'desktop' and st.get('open') and st.get('leftW') == '296px' and shown(lp) and lp['x'] == 54 and cv['x'] == 296,
                   "%s: as before, the panel open beside the drawing (%s, %s)" % (name[3:], st, cv))
                ck(not shown(await safe(BOX, '#a3d-rail [data-railmore]')) and not shown(await safe(BOX, '#a3d-shellscrim')), "no More, no shade")
                fs = await safe("()=>parseFloat(getComputedStyle(document.querySelector('#a3d-propsbody input[type=text],#a3d-propsbody input[type=number]')).fontSize)")
                ck((fs >= 16) if touch else (fs < 16), "%s fields: %s px%s" % ('touch' if touch else 'mouse', fs, ', for a finger and no zoom' if touch else ', compact as before'))
                await (p.tap if touch else p.click)('#a3d-rail [data-tab="browser"]')
                await p.wait_for_timeout(250)
                ck((await safe("()=>window.__a3dShellTier()") or {}).get('open'), "the open tab's button leaves the panel open, as it always has")
                ck(await safe("()=>getComputedStyle(document.getElementById('a3d-rail')).position") == 'static', "the rail is in the page's flow")
                ck(not errs, "no page errors (%s)" % errs[:3])
                if not touch:
                    # ---------------------------------------------------------------------------
                    print("\n-- 6. the screen turns")
                    await p.set_viewport_size({'width': 390, 'height': 844})
                    await p.wait_for_timeout(400)
                    st = await safe("()=>window.__a3dShellTier()") or {}
                    cv = await safe(BOX, '#a3d-canvas')
                    ck(st.get('tier') == 'phone' and not st.get('open') and cv['x'] == 0 and cv['w'] == 390, "narrowed to a phone: the tab bar, the panel shut, the drawing full width (%s)" % st)
                    await p.set_viewport_size({'width': 820, 'height': 1180})
                    await p.wait_for_timeout(400)
                    st = await safe("()=>window.__a3dShellTier()") or {}
                    ck(st.get('tier') == 'overlay' and not st.get('open') and not await safe("()=>document.body.classList.contains('a3d-tier-phone')"), "to a tablet: the rail and a shut drawer (%s)" % st)
                    await p.set_viewport_size({'width': 1500, 'height': 950})
                    await p.wait_for_timeout(400)
                    st = await safe("()=>window.__a3dShellTier()") or {}
                    ck(st.get('tier') == 'desktop' and st.get('open') and st.get('leftW') == '296px', "widened again: the panel open, as it was (%s)" % st)
                    await p.click('#a3d-rail .a3d-paneltoggle')
                    await p.wait_for_timeout(200)
                    await p.set_viewport_size({'width': 390, 'height': 844})
                    await p.wait_for_timeout(300)
                    await p.set_viewport_size({'width': 1500, 'height': 950})
                    await p.wait_for_timeout(300)
                    st = await safe("()=>window.__a3dShellTier()") or {}
                    ck(not st.get('open') and st.get('leftW') == '54px', "a panel shut on the computer is still shut when it comes back (%s)" % st)
                    # -----------------------------------------------------------------------
                    print("\n-- 7. safe areas")
                    meta = await safe("()=>document.querySelector('meta[name=viewport]').getAttribute('content')")
                    ck(meta and 'viewport-fit=cover' in meta, "the page asks for the whole screen, notch and all (%s)" % meta)
                    rules = await safe("""()=>{var out=[];[].forEach.call(document.styleSheets,function(s){try{[].forEach.call(s.cssRules,function(r){if(r.cssText&&r.cssText.indexOf('safe-area-inset')>=0)out.push([r.selectorText,r.style.height,r.style.padding,r.style.paddingTop,r.style.bottom]);   /* the shorthand: env() leaves the longhands empty */});}catch(e){}});return out;}""") or []
                    R = {r[0]: r for r in rules}
                    bar = R.get('body.a3d-tier-phone #a3d-rail') or [None] * 5
                    ck('safe-area-inset-bottom' in (bar[1] or '') and 'safe-area-inset-bottom' in (bar[2] or '') and
                       'safe-area-inset-top' in ((R.get('body.a3d-tier-phone #acad-shell') or [None] * 5)[3] or '') and
                       'safe-area-inset-bottom' in ((R.get('body.a3d-tier-phone.a3d-railutil-open #a3d-railutil') or [None] * 5)[4] or ''),
                       "the tab bar, More and the top bar keep clear of the home bar and the notch (%d rules)" % len(rules))
            except Stalled as s:
                ck(False, "%s: the harness stalled at %s" % (name, s))
            except Exception:
                traceback.print_exc()
                ck(False, "%s: ran to its end" % name)
            await b.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        print("RESULT: FAIL")
        for m in ck.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
