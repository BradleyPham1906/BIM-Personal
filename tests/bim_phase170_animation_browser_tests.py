#!/usr/bin/env python3
"""bim_phase170_animation_browser_tests.py -- V170: the site analysis in motion, and Save image with the model.

Every service is answered inside the browser by tests/site_analysis_fixture.py (V164's), so the analyses are
the ones V164 to V168 draw. What the clock should do is worked out again in tests/animation_reference.py from
the design; what reaches the screen is read back from the canvas's own pixels.

  1. BEFORE PLAY: the marker and the version; the settings and each analysis's motion as the design says;
     nothing to play before a run; PLAY in the command search; the buttons once a run has drawn.
  2. PLAY, PAUSE, STOP: the clock in real time and the frame cap; Pause keeps the moment, Play goes on from
     it; Stop gives the still drawing back, pixel for pixel, and the project is untouched; a hidden page
     stops the clock; the device asking for reduced motion pauses it; opening still; nothing left to move.
  3. MARCHING DASHES: each element's motion and way against the reference; the dashes move on the canvas,
     and stand when the elements are set still; the moving dashes' colour.
  4. WINDS DRAWN ON: how far and how clear, one after another; on the canvas, the tip not there yet, then there,
     then gone; the words when it is whole.
  5. RINGS AND REVEALS: the ripple against the reference, and on the canvas; the analyses coming in one after
     another, from still only.
  6. THE SUN THROUGH THE DAY: the sweep against the app's NOAA sunrise and sunset; polar day and night; no place;
     the moving sun on the dome; one shadow, on the side away from the sun, morning and afternoon; the sun study
     in plan; the project's time unchanged.
  7. MOTION IN PROPERTIES: the choices each shape can take; a change, one undo step; refused; Default; kept by a
     run.
  8. SAVE IMAGE: the model in it (WebGL here; headless Chromium has no WebGPU, said); the file; the moment; the
     CPU drawing.
  9. STILL ON PAPER: a sheet drawn the same whatever the clock.
 10. A PHONE, A TABLET, A COMPUTER.
 11. A RELOAD: a project with its analyses, left playing, opens still.

The harness never waits without a bound (V123).
"""
import asyncio, base64, json, math, pathlib, re, struct, sys, traceback, zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import site_analysis_fixture as FX   # noqa: E402
import animation_reference as R   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
TOWER = [-12, -10, 12, 10, 24]


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


def png_size(raw):
    return struct.unpack('>II', raw[16:24]) if raw[:8] == b'\x89PNG\r\n\x1a\n' else None


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
        ST = {}
        for h in FX.HOSTS:
            await ctx.route(h, FX.route_handler(ST))
        for h in BLOCKERS:
            await ctx.route(h, lambda r: r.abort())
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def toast(pg=None):
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}", pg=pg) or ''

        async def anim(pg=None):
            return await safe("()=>window.__a3dAnim()", pg=pg) or {}

        async def at(t, play_at=0, pg=None):
            return await safe("(a)=>window.__a3dAnimAt(a[0],a[1])", [t, play_at], pg=pg) or {}

        async def diags(a=None, pg=None):
            L = (await safe("()=>window.__a3dState().objs", pg=pg)) or []
            return [o for o in L if o.get('t') == 'diag' and (a is None or o['dg']['a'] == a)]

        async def by_key(a, k):
            for o in await diags(a):
                if o['dg']['k'] == k:
                    return o
            return None

        async def overlay(pg=None):
            return await safe("()=>document.getElementById('a3d-canvas').toDataURL('image/png')", pg=pg)

        async def ink(x, y, r=3, pg=None):
            """the overlay's strongest alpha in a small square about a point, in CSS pixels"""
            return await safe("""(a)=>{var c=document.getElementById('a3d-canvas'),s=c.width/c.getBoundingClientRect().width,x=Math.round(a[0]*s),y=Math.round(a[1]*s),r=Math.max(1,Math.round(a[2]*s));
              var d=c.getContext('2d').getImageData(x-r,y-r,2*r+1,2*r+1).data,m=0,i;for(i=3;i<d.length;i+=4)if(d[i]>m)m=d[i];return m;}""", [x, y, r], pg=pg)

        async def px(x, y, pg=None):
            return await safe("""(a)=>{var c=document.getElementById('a3d-canvas'),s=c.width/c.getBoundingClientRect().width;return Array.prototype.slice.call(c.getContext('2d').getImageData(Math.round(a[0]*s),Math.round(a[1]*s),1,1).data);}""", [x, y], pg=pg)

        async def scr(p, pg=None):
            return await safe("(p)=>window.__a3dDgToScreen(p)", p, pg=pg)

        async def only(keep, pg=None):
            """the Site analysis's layers shown: these analyses only"""
            return await safe("""(keep)=>{var D=window.__a3dDgState(),k,n=0;for(k in D.layers)if(D.layers.hasOwnProperty(k)&&k!=='root'){
              var v=keep.indexOf(k)>=0||keep.some(function(a){return k.indexOf(a+':')===0;});window.__a3dLayerSet(D.layers[k],'visible',v);n++;}
              window.__a3dLayerSet(D.layers.root,'visible',true);return n;}""", keep, pg=pg)

        async def tower(pg=None):
            await safe("""(a)=>{var x0=a[0],z0=a[1],x1=a[2],z1=a[3],h=a[4];return window.__a3dPushTestObj({id:'TOWER',t:'solid',name:'Tower',pos:[0,0,0],layer:'layer-0',
              mesh:{v:[[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1],[x0,h,z0],[x1,h,z0],[x1,h,z1],[x0,h,z1]],f:[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}});}""", TOWER, pg=pg)

        async def analyze(pg=None):
            pg = pg or page
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(300)
            await pg.fill('[data-saaddr]', '1 Market Street')
            await pg.press('[data-saaddr]', 'Enter')
            for _ in range(240):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await pg.wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def btn(pg=None):
            return await safe("""()=>{var g=document.getElementById('a3d-animgrp'),b=document.getElementById('a3d-animplay'),x=document.getElementById('a3d-animstop');
              return g&&b?{shown:!g.hidden&&g.offsetParent!==null,text:b.textContent,pressed:b.getAttribute('aria-pressed'),label:b.getAttribute('aria-label'),title:b.title,
              stop:!!x&&!x.hidden&&x.offsetParent!==null,on:b.classList.contains('on')}:null;}""", pg=pg) or {}

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")
            await tower()

            # ---------------------------------------------------------------------------------
            print("\n-- 1. Before Play")
            mk = await safe("()=>window.__acad3dV170") or ''
            ck(all(w in mk for w in ('clock', 'play', 'pause', 'stop', 'march', 'drawon', 'rings', 'reveal', 'sun', 'shadowday', 'motionstyle', 'reducedmotion', 'hidden', 'saveimage3d', 'command')),
               "the V170 marker (%s)" % mk)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 170, "the app says V170 or later (%s)" % (mv and mv.group(1)))
            st = await safe("()=>window.__a3dAnimSettings()") or {}
            ck(st.get('anim') == R.SETTINGS, "the clock's settings are the design's: %s" % st.get('anim'))
            ck(st.get('names') == R.NAMES and st.get('auto') == R.AUTO, "the motions' names, and each analysis's own motion by its elements' keys, as the design lists them")
            a0 = await anim()
            ck(a0.get('on') is False and a0.get('paused') is False and a0.get('t') == 0 and a0.get('live') is False and a0.get('raf') is False, "the app opens still: no clock running (%s)" % {k: a0.get(k) for k in ('on', 'paused', 't', 'live', 'raf')})
            b0 = await btn()
            ck(b0 and b0['shown'] is False, "with nothing to move, no Play in the status bar")
            ok = await safe("()=>window.__a3dAnimPlay(true)")
            ck(ok is False and 'Nothing to play' in await toast() and (await anim()).get('on') is False, "Play with nothing to move says so and does nothing")
            found = [x['name'] for x in (await safe("()=>window.__a3dCommandSearch('animate',5)") or [])]
            ck('PLAY' in found[:3], "searching 'animate' finds PLAY (%s)" % found)
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return c.name==='PLAY';})[0]") or {}
            ck(set(['ANIMATE', 'PAUSE', 'MOTION']).issubset(set(cat.get('aliases') or [])) and 'Stop' in (cat.get('desc') or ''), "PLAY's aliases and its description (%s)" % cat.get('aliases'))
            fin = await analyze()
            S = {s['id']: s['state'] for s in fin.get('steps', [])}
            ck(S.get('draw') == 'ok', "the fixture's run draws the analyses (%s)" % S)
            await safe("()=>{window.__a3dAnzView(false);window.__a3dSelectFor([]);window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:520});}")
            await page.wait_for_timeout(400)
            b1 = await btn()
            ck(b1.get('shown') is True and b1.get('text') == 'PLAY' and b1.get('pressed') == 'false' and b1.get('label') == 'Play' and b1.get('stop') is False,
               "a run drawn: PLAY in the status bar, not pressed, named for screen readers, no Stop yet (%s)" % b1)
            ck(await safe("()=>{var g=document.getElementById('a3d-animgrp');return !!g.closest('#a3d-statusbar')&&g.previousElementSibling&&g.previousElementSibling.id==='a3d-navgrp';}") is True,
               "beside the view's own buttons, after them; nothing floats over the drawing (V109)")
            DG = await diags()
            bad = [(o['dg']['a'], o['dg']['k']) for o in DG if (await safe("(id)=>window.__a3dAnimOf(id).motion", o['id'])) != R.motion(o['dg'])]
            ck(not bad and len(DG) > 150, "each of the %d elements has the motion the design gives its analysis and shape (%s)" % (len(DG), bad[:5]))
            got = {}
            for o in DG:
                m = R.motion(o['dg'])
                if m:
                    got.setdefault(m, set()).add(o['dg']['a'])
            ck(got.get('march', set()) >= {'flow', 'views', 'walk', 'needs', 'transit'} and got.get('draw') == {'wind'} and got.get('ring') == {'frame'} and got.get('sun') == {'sun', 'shadow'},
               "marching: flows, views, walks, daily needs, transit; drawn on: the winds; rings: the distances; the sun and the shadows through the day (%s)" % {k: sorted(v) for k, v in got.items()})
            still0 = await overlay()
            u0 = await safe("()=>window.__a3dUndoDepth()")
            objs0 = json.dumps(await safe("()=>window.__a3dState().objs"), sort_keys=True)
            sun0 = await safe("()=>window.__a3dSunSettings()")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. Play, Pause, Stop")
            await safe("()=>document.getElementById('a3d-animplay').click()")
            t0 = await safe("()=>performance.now()")
            b2 = await btn()
            ck(b2.get('text') == 'PAUSE' and b2.get('pressed') == 'true' and b2.get('label') == 'Pause' and b2.get('on') is True and b2.get('stop') is True,
               "Play pressed: it reads PAUSE, pressed, and Stop beside it (%s)" % b2)
            await page.wait_for_timeout(1600)
            a2 = await anim()
            el = ((await safe("()=>performance.now()")) - t0) / 1000
            ck(a2.get('on') is True and a2.get('raf') is True and 0.5 * el <= a2.get('t', 0) <= el + 0.05,
               "the clock runs in real time: %.2f s of play in %.2f s (never ahead; a slow frame moves it a tenth of a second at most)" % (a2.get('t', 0), el))
            ck(3 <= a2.get('frames', 0) <= R.SETTINGS['fps'] * el + 2, "frames drawn: %d in %.2f s, never more than %d a second" % (a2.get('frames', 0), el, R.SETTINGS['fps']))
            ck(re.match(r'^Pause, keeping this moment \(the sun at \d\d:\d\d\)$', b2.get('title') or (await btn()).get('title') or '') is not None or 'Pause, keeping this moment' in (await btn()).get('title', ''),
               "its title says Pause keeps the moment, with the sun's time")
            tk = await safe("()=>{var a=[],i;for(i=0;i<=60;i++)a.push(1000+i*1000/60);return window.__a3dAnimTicks(a);}") or {}
            ck(tk.get('frames') in (30, 31) and near(tk.get('dt'), 1.0, 1e-9),
               "fed a second of frames at 60 a second: %s drawn (the cap is %d), and the clock a second on (%s)" % (tk.get('frames'), R.SETTINGS['fps'], tk.get('dt')))
            tg = await safe("()=>window.__a3dAnimTicks([5000,5016,5516,5532])") or {}
            ck(near(tg.get('dt'), 0.016 + 0.1 + 0.016, 1e-9), "a half-second gap between frames moves the clock a tenth of a second, not half (%s)" % tg.get('dt'))
            await safe("()=>window.__a3dAnimPlay(true)")
            await page.wait_for_timeout(300)
            praf = await safe("()=>{var a=window.__a3dAnim().raf;document.getElementById('a3d-animplay').click();return [a,window.__a3dAnim().raf];}")
            ck(praf == [True, False], "Pause cancels the frame already asked for, at once, in the same task (%s)" % praf)
            p1 = await anim()
            await page.wait_for_timeout(500)
            p2 = await anim()
            b3 = await btn()
            ck(p1.get('paused') is True and p1.get('on') is False and p2.get('t') == p1.get('t') and p2.get('frames') == p1.get('frames') and p2.get('raf') is False,
               "Pause: the clock and the frames stand still (t %.3f, %d frames)" % (p1.get('t', 0), p1.get('frames', 0)))
            ck(b3.get('text') == 'PLAY' and b3.get('title') == 'Play on from this moment' and b3.get('stop') is True and p2.get('live') is True,
               "paused: PLAY again, 'Play on from this moment', Stop still there, the moment still drawn")
            await safe("()=>document.getElementById('a3d-animplay').click()")
            await page.wait_for_timeout(400)
            p3 = await anim()
            ck(p3.get('t', 0) > p1.get('t', 0) and p3.get('playAt') == p1.get('playAt'), "Play again goes on from the moment, without bringing the layers in again (playAt %s)" % p3.get('playAt'))
            rs = await safe("()=>{window.__a3dAnimAt(5,1);window.__a3dAnimPlay(true);var a=window.__a3dAnim();window.__a3dAnimPlay(false);return [a.on,a.t,a.playAt];}")
            ck(rs == [True, 5, 1], "and exactly: paused at 5 s, the layers brought in at 1 s, Play goes on at 5 s with them in (%s)" % rs)
            await safe("()=>window.__a3dAnimPlay(true)")
            await page.wait_for_timeout(300)
            hraf = await safe("()=>{var a=window.__a3dAnim().raf;Object.defineProperty(document,'hidden',{configurable:true,get:function(){return true;}});document.dispatchEvent(new Event('visibilitychange'));return [a,window.__a3dAnim().raf];}")
            ck(hraf == [True, False], "the page hidden: the frame already asked for is cancelled at once (%s)" % hraf)
            h1 = await anim()
            await page.wait_for_timeout(500)
            h2 = await anim()
            ck(h1.get('raf') is False and h2.get('frames') == h1.get('frames') and h2.get('t') == h1.get('t') and h2.get('on') is True,
               "the page hidden: the clock waits, still playing")
            await safe("()=>{Object.defineProperty(document,'hidden',{configurable:true,get:function(){return false;}});document.dispatchEvent(new Event('visibilitychange'));}")
            await page.wait_for_timeout(400)
            h3 = await anim()
            ck(h3.get('raf') is True and h3.get('frames', 0) > h2.get('frames', 0) and 0 < h3.get('t', 0) - h2.get('t', 0) <= 0.55,
               "shown again: it goes on from where it waited, no jump (%.3f s on)" % (h3.get('t', 0) - h2.get('t', 0)))
            await page.emulate_media(reduced_motion='reduce')
            await page.wait_for_timeout(200)
            r1 = await anim()
            ck(r1.get('on') is False and r1.get('paused') is True and 'reduced motion' in await toast(), "the device asking for reduced motion while it plays: paused, and said")
            await page.emulate_media(reduced_motion='no-preference')
            await safe("()=>document.getElementById('a3d-animstop').click()")
            s1 = await anim()
            ck(s1.get('t') == 0 and s1.get('on') is False and s1.get('paused') is False and s1.get('live') is False and (await btn()).get('stop') is False,
               "Stop: the clock at nothing, still, and Stop gone")
            ck(await overlay() == still0, "and the drawing is the still one again, pixel for pixel")
            ck(await safe("()=>window.__a3dUndoDepth()") == u0 and json.dumps(await safe("()=>window.__a3dState().objs"), sort_keys=True) == objs0 and await safe("()=>window.__a3dSunSettings()") == sun0,
               "Play, Pause and Stop left the project as it was: no undo step, the elements and the sun's date and time unchanged")
            await safe("()=>{var b=document.getElementById('a3d-animplay');b.focus();}")
            await page.keyboard.press('Enter')
            k1 = await anim()
            await page.keyboard.press('Space')
            k2 = await anim()
            ck(k1.get('on') is True and k2.get('on') is False and k2.get('paused') is True, "the keyboard: Enter plays, Space pauses, on the focused button")
            await safe("()=>window.__a3dAnimPlay(true)")
            await only([])
            await page.wait_for_timeout(300)
            n1 = await anim()
            ck(n1.get('on') is False and n1.get('paused') is False and n1.get('t') == 0 and (await btn()).get('shown') is False,
               "every analysis hidden while it plays: nothing left to move, still, and the buttons gone")
            await only([a for a in R.ANALYZE_ORDER])
            await page.wait_for_timeout(200)
            ck((await btn()).get('shown') is True and (await anim()).get('on') is False, "shown again: PLAY, still")
            p2c = await browser.new_context(viewport={'width': 1200, 'height': 800}, reduced_motion='reduce')
            p2p = await p2c.new_page()
            await within(p2p.goto('file://' + str(HTML)), 'goto reduced')
            await p2p.wait_for_timeout(2000)
            ck((await anim(p2p)).get('on') is False and (await anim(p2p)).get('live') is False, "a device asking for reduced motion: the app opens still, as always")
            await p2c.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Marching dashes")
            c = await safe("()=>window.__a3dAnimCentre()") or [0, 0]
            site = await safe("()=>window.__a3dDgSite()") or {}
            ck(near(c[0], site['c'][0]) and near(c[1], site['c'][1]), "a march away from the site goes from the site's centre (%s)" % c)
            wrong, n_out, n_path = [], 0, 0
            for o in DG:
                dg = o['dg']
                if R.motion(dg) != 'march':
                    continue
                info = await safe("(id)=>window.__a3dAnimOf(id)", o['id']) or {}
                if info.get('out') != R.goes_out(dg):
                    wrong.append(('way', dg['a'], dg['k']))
                    continue
                if not R.goes_out(dg):
                    n_path += 1
                    continue
                n_out += 1
                way = await safe("(id)=>window.__a3dAnimWay(id)", o['id'])
                q = o.get('pos') or [0, 0, 0]

                def far(p):
                    return (p[0] + q[0] - c[0]) ** 2 + (p[2] + q[2] - c[1]) ** 2
                g = dg['g']
                if g['kind'] == 'segs':
                    P = g['pts']
                    exp = []
                    for i in range(0, len(P) - 1, 2):
                        exp += [i + 1, i] if far(P[i]) > far(P[i + 1]) else [i, i + 1]
                    if way != exp:
                        wrong.append(('segs', dg['a'], dg['k']))
                elif g['kind'] == 'lines':
                    exp = [list(range(len(L)))[::-1] if far(L[0]) > far(L[-1]) else list(range(len(L))) for L in g['lines']]
                    if way != exp:
                        wrong.append(('lines', dg['a'], dg['k']))
                else:
                    P = g['pts']
                    exp = list(range(len(P)))
                    if far(P[0]) > far(P[-1]):
                        exp.reverse()
                    if way != exp:
                        wrong.append(('line', dg['a'], dg['k']))
            ck(not wrong and n_out >= 8 and n_path >= 8,
               "each march runs its way: %d away from the site, each line, pair and polyline turned as the reference turns it; %d as drawn (%s)" % (n_out, n_path, wrong[:4]))
            # the fixture's routes all have an arrowhead, and none of its polylines marches by its analysis (falsify's second run)
            fl = next((o for o in DG if o['dg']['a'] == 'flow' and o['dg']['k'].startswith('flow:') and (o['dg'].get('s') or {}).get('head')), None)
            nh = json.loads(json.dumps(fl or {'dg': {'s': {}}}))
            nh['id'] = 'T170-NOHEAD'
            nh['dg']['s'].pop('head', None)
            out_nh = await safe("""(o)=>{window.__a3dPushTestObj(o);var r=window.__a3dAnimOf(o.id);window.__a3dDel(o.id);
              return r?r.out:'none';}""", nh)
            ck(fl is not None and R.goes_out(nh['dg']) is False and out_nh is False,
               "a route without its arrowhead still marches as drawn: its analysis says so (%s)" % out_nh)
            wrong_l, n_l, n_turned, n_kept = [], 0, 0, 0
            for o in DG:
                dg, g = o['dg'], o['dg']['g']
                if g['kind'] != 'lines' or g.get('closed') or R.auto(dg['a'], dg['k']) or (dg.get('s') or {}).get('head'):
                    continue
                q = o.get('pos') or [0, 0, 0]

                def far(p):
                    return (p[0] + q[0] - c[0]) ** 2 + (p[2] + q[2] - c[1]) ** 2
                exp = [list(range(len(L)))[::-1] if far(L[0]) > far(L[-1]) else list(range(len(L))) for L in g['lines']]
                ok_set = await safe("(id)=>window.__a3dDgSet(id,'anim','march')", o['id'])
                info = await safe("(id)=>window.__a3dAnimOf(id)", o['id']) or {}
                way = await safe("(id)=>window.__a3dAnimWay(id)", o['id'])
                await safe("(id)=>window.__a3dDgSet(id,'anim','')", o['id'])
                if not (ok_set is True and info.get('motion') == 'march' and info.get('out') is True and way == exp):
                    wrong_l.append((dg['a'], dg['k'], ok_set, info.get('out')))
                n_l += 1
                n_turned += sum(1 for e in exp if len(e) > 1 and e[0] > e[-1])
                n_kept += sum(1 for e in exp if len(e) > 1 and e[0] < e[-1])
                if n_l >= 4 and n_turned >= 3 and n_kept >= 3:
                    break
            ck(not wrong_l and n_turned >= 3 and n_kept >= 3,
               "polylines set to march go away from the site, each line turned or kept on its own: %d elements, %d lines turned, %d kept (%s)" % (n_l, n_turned, n_kept, wrong_l[:3]))
            cols = ['#3b8fd9', '#f2f5f8', '#8fd694', '#d95926', '#000000', '#ffffff', '#9fb7d4', 'red']
            tt = [await safe("(h)=>window.__a3dAnimTint(h)", h) for h in cols]
            ck(tt == [R.tint(h) for h in cols], "a solid line's moving dashes: lighter on a dark line, darker on a pale one (%s)" % tt)
            await only(['walk', 'needs'])
            await safe("()=>window.__a3dCamSet({tx:0,tz:0,dist:520})")
            f1 = await at(5.0, -10)
            im1 = await overlay()
            await at(5.25, -10)
            im2 = await overlay()
            ck(im1 != im2, "the walks and the ways to daily needs: the drawing moves between 5.00 and 5.25 s")
            W = [o for o in DG if o['dg']['a'] in ('walk', 'needs')]
            for o in W:
                await safe("(id)=>window.__a3dDgSet(id,'anim','none')", o['id'])
            await at(5.0, -10)
            im3 = await overlay()
            await at(5.25, -10)
            im4 = await overlay()
            ck(im3 == im4, "each set still in its Motion: the same at both moments")
            await safe("()=>window.__a3dAnimStop()")
            im5 = await overlay()
            ck(im5 == im3, "and drawn as the still drawing is")
            for o in W:
                await safe("(id)=>window.__a3dDgSet(id,'anim','')", o['id'])

            # ---------------------------------------------------------------------------------
            print("\n-- 4. Winds drawn on")
            WD = sorted([o for o in await diags('wind') if R.motion(o['dg']) == 'draw'], key=lambda o: o['id'])
            ck(len(WD) == 2, "two prevailing winds drawn on (%d)" % len(WD))
            await only(['wind'])
            bad = []
            for t in (0.0, 0.4, 0.8, 1.2, 1.6, 2.5, 3.5, 3.6, 3.9, 4.3, 4.6, 5.0, 9.3):
                await at(t, -10)
                for o in WD:
                    d = (await safe("(id)=>window.__a3dAnimOf(id)", o['id']) or {}).get('draw') or {}
                    idx = (await anim()).get('fr', {}).get('idx', {}).get(o['id'])
                    f, a = R.draw_of(t, idx if idx is not None else -1)
                    if not (near(d.get('f'), f, 1e-9) and near(d.get('a'), a, 1e-9)):
                        bad.append((t, o['dg']['k'], d, (f, a)))
            fr_idx = (await anim()).get('fr', {}).get('idx', {})
            idxs = sorted(fr_idx.get(o['id']) for o in WD)
            ck(not bad and idxs == [0, 1], "how far each is drawn and how clear, at thirteen moments, the second %.2f s after the first (%s)" % (R.SETTINGS['draw']['stagger'], bad[:3]))
            w0 = WD[0]
            P = w0['dg']['g']['pts']
            tail = [(P[0][k] + P[-1][k]) / 2 for k in range(3)]
            tip = P[len(P) // 2]
            near_tip = [tail[k] + (tip[k] - tail[k]) * 0.85 for k in range(3)]
            near_tail = [tail[k] + (tip[k] - tail[k]) * 0.12 for k in range(3)]
            st_tip, st_tail = await scr(near_tip), await scr(near_tail)
            i0 = (await anim()).get('fr', {}).get('idx', {}).get(w0['id']) or 0
            T = lambda p: p + i0 * R.SETTINGS['draw']['stagger']
            await at(T(0.6), -10)
            g_tip, g_tail = await ink(st_tip[0], st_tip[1], 2), await ink(st_tail[0], st_tail[1], 2)
            await at(T(2.5), -10)
            h_tip = await ink(st_tip[0], st_tip[1], 2)
            await at(T(4.6), -10)
            r_tip, r_tail = await ink(st_tip[0], st_tip[1], 2), await ink(st_tail[0], st_tail[1], 2)
            ck(g_tail is not None and r_tail is not None and g_tail > r_tail + 60 and g_tip == r_tip and h_tip > r_tip + 60,
               "on the canvas, against the moment it rests: growing, its tail drawn and its tip not yet; held, the tip there (tail %s/%s, tip %s/%s/%s)" % (g_tail, r_tail, g_tip, h_tip, r_tip))
            await at(T(0.6), -10)
            lb_g = await safe("()=>window.__a3dDgLabelBoxes().length")
            await at(T(2.5), -10)
            lb_h = await safe("()=>window.__a3dDgLabelBoxes().length")
            ck(lb_h is not None and lb_g is not None and lb_h > lb_g, "its words come when it is whole (%s words growing, %s held)" % (lb_g, lb_h))

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Rings and reveals")
            await only(['frame'])
            RG = sorted([o for o in await diags('frame') if R.motion(o['dg']) == 'ring'], key=lambda o: o['dg']['k'])
            radii = []
            for o in RG:
                rr = (await safe("(id)=>window.__a3dAnimOf(id)", o['id']) or {}).get('ring') or {}
                radii.append(rr.get('r'))
            ck(len(RG) == 3 and all(near(r, d, 1e-6) for r, d in zip(sorted(radii), [100, 200, 300])), "three distance rings, 100, 200 and 300 m (%s)" % radii)
            bad = []
            rings = sorted(radii)
            for t in (0.0, 0.2, 0.5, 0.66, 1.0, 1.3, 1.9, 2.0, 3.0, 4.1, 4.2, 4.5, 8.9):
                await at(t, -10)
                for o, r in zip(RG, radii):
                    k = (await safe("(id)=>window.__a3dAnimOf(id)", o['id']) or {}).get('k')
                    if not near(k, R.ring_k(t, r, rings), 1e-9):
                        bad.append((t, o['dg']['k'], k, R.ring_k(t, r, rings)))
            ck(not bad, "the ripple: each ring's growth at thirteen moments, the front carried by the smallest ring not yet reached (%s)" % bad[:3])
            o100 = [o for o, r in zip(RG, radii) if near(r, 100, 1e-6)][0]
            P = o100['dg']['g']['pts']
            Cc = [sum(p[0] for p in P) / len(P), sum(p[2] for p in P) / len(P)]
            p45 = P[len(P) // 8]
            half = [Cc[0] + (p45[0] - Cc[0]) * 0.5, p45[1], Cc[1] + (p45[2] - Cc[1]) * 0.5]
            s_half, s_full = await scr(half), await scr(p45)
            await at(50 / R.SETTINGS['ring']['mps'], -10)
            a_half, a_full = await ink(s_half[0], s_half[1], 4), await ink(s_full[0], s_full[1], 4)
            await at(150 / R.SETTINGS['ring']['mps'], -10)
            b_half, b_full = await ink(s_half[0], s_half[1], 4), await ink(s_full[0], s_full[1], 4)
            ck(a_half > b_half + 60 and b_full > a_full + 30, "on the canvas: the 100 m ring at 50 m first, then at 100 m (ink at 50 m %s then %s; at 100 m %s then %s)" % (a_half, b_half, a_full, b_full))
            lb_a = [b for b in (await safe("()=>window.__a3dDgLabelBoxes()") or [])]
            await at(0.33, -10)
            lb_b = [b for b in (await safe("()=>window.__a3dDgLabelBoxes()") or [])]
            ck(len(lb_b) < len(lb_a), "a ring's words wait until it is whole (%d words, then %d)" % (len(lb_b), len(lb_a)))
            await only([a for a in R.ANALYZE_ORDER if a != 'noise'])
            await page.wait_for_timeout(100)
            shown = [a for a in R.ANALYZE_ORDER if a != 'noise' and any(o['dg']['a'] == a for o in DG)]
            vis = await safe("""()=>{var D=window.__a3dDgState(),L=window.__a3dLayers?window.__a3dLayers():[],out=[],k;
              function shown(id){var l=L.filter(function(x){return x.id===id;})[0];return !!l&&l.visible!==false;}
              for(k in D.layers)if(D.layers.hasOwnProperty(k)&&k!=='root'&&k.indexOf(':')<0&&shown(D.layers[k]))out.push(k);return out;}""") or []
            a5 = await at(1.0, 0)
            order = a5.get('fr', {}).get('order', {})
            exp = [a for a in R.ANALYZE_ORDER if a in order]
            ck(sorted(order.values()) == list(range(len(order))) and sorted(order, key=lambda k: order[k]) == shown and 'noise' not in order,
               "the layers come in in Analyze's order, one after another, the shown ones only: noise hidden takes no turn (%s)" % sorted(order, key=lambda k: order[k]))
            bad = []
            for t in (0.0, 0.3, 0.5, 0.9, 1.4, 2.2, 3.0, 6.0):
                await at(t, 0)
                for a, j in order.items():
                    v = (await safe("(a)=>{var o=window.__a3dDgList(a)[0];return o?window.__a3dAnimOf(o.id).reveal:null;}", a))
                    if not near(v, R.reveal(t, 0, j), 1e-9):
                        bad.append((t, a, v, R.reveal(t, 0, j)))
            ck(not bad, "each layer's share at eight moments, against the reference (%s)" % bad[:3])
            await only(['frame'])
            await at(0.0, 0)
            z0 = await ink(s_full[0], s_full[1], 4)
            await at(3.9, 0)
            z1 = await ink(s_full[0], s_full[1], 4)
            ck(z1 > z0 + 30, "on the canvas: the 100 m ring not there at the first moment, there once the compass is in (%s, %s)" % (z0, z1))
            await only(R.ANALYZE_ORDER)
            pa = await safe("()=>{window.__a3dAnimAt(7,3);window.__a3dAnimStop();window.__a3dAnimPlay(true);var a=window.__a3dAnim();window.__a3dAnimPlay(false);return [a.t,a.playAt];}")
            ck(pa == [0, 0], "Play from still starts the clock and the reveal again at nothing (%s)" % pa)
            await safe("()=>window.__a3dAnimStop()")

            # ---------------------------------------------------------------------------------
            print("\n-- 6. The sun through the day")
            ss = await safe("()=>window.__a3dSunSettings()") or {}
            day = await safe("(s)=>window.__a3dSunCalc(s.lat,s.lon,s.tz,s.date,'12:00')", ss) or {}
            ck(isinstance(ss.get('lat'), (int, float)) and day.get('sunrise') is not None, "the fixture's place and the study's day: %s, %s, UTC%+g; sunrise %s, sunset %s" % (ss.get('lat'), ss.get('date'), ss.get('tz', 0), R.hhmm(day.get('sunrise', 0)), R.hhmm(day.get('sunset', 0))))
            bad = []
            for t in (0.0, 0.5, 6.0, 12.0, 18.0, 23.99, 24.0, 24.6, 25.19, 25.2, 31.0):
                got = await safe("(t)=>window.__a3dAnimSunTime(t)", t)
                if got != R.sun_time(t, day):
                    bad.append((t, got, R.sun_time(t, day)))
            ck(not bad, "the sun's time from sunrise to sunset in %d s, held %.1f s at sunset, then again, against the reference at eleven moments (%s)" % (R.SETTINGS['sun']['secs'], R.SETTINGS['sun']['hold'], bad[:3]))
            async def sun_field(k, v):
                return await safe("""(a)=>{var b=document.getElementById('a3d-propsbody'),i=document.createElement('input');i.setAttribute('data-propmodel',a[0]);i.value=a[1];
                  b.appendChild(i);i.dispatchEvent(new Event('change',{bubbles:true}));if(i.parentNode)i.parentNode.removeChild(i);return window.__a3dSunSettings();}""", [k, v])
            yr = ss['date'][:4]
            await sun_field('sunlat', '80')
            await sun_field('sundate', yr + '-12-21')
            dn = await safe("(s)=>window.__a3dSunCalc(s.lat,s.lon,s.tz,s.date,'12:00')", await safe("()=>window.__a3dSunSettings()")) or {}
            n_t = await safe("()=>window.__a3dAnimSunTime(5)")
            await sun_field('sundate', yr + '-06-21')
            dd = await safe("(s)=>window.__a3dSunCalc(s.lat,s.lon,s.tz,s.date,'12:00')", await safe("()=>window.__a3dSunSettings()")) or {}
            d_t = [await safe("(t)=>window.__a3dAnimSunTime(t)", t) for t in (0, 12, 24)]
            ck(dn.get('polar') == 'night' and n_t is None and dd.get('polar') == 'day' and d_t == [R.sun_time(t, dd) for t in (0, 12, 24)] == ['00:00', '11:59', '23:59'],
               "80 degrees north: no sun to move in the polar night; under the midnight sun, the whole day (%s)" % d_t)
            await sun_field('sunlat', '')
            ck(await safe("()=>window.__a3dAnimSunTime(5)") is None, "with no latitude, no sun to move")
            await sun_field('sunlat', str(ss['lat']))
            await sun_field('sundate', ss['date'])
            ck(await safe("()=>window.__a3dSunSettings()") == ss, "the place and the day put back")
            await only(['sun'])
            tm = (14 * 60 - math.ceil(day['sunrise'])) / (math.floor(day['sunset']) - math.ceil(day['sunrise'])) * R.SETTINGS['sun']['secs']
            a6 = await at(tm, -10)
            sn = await safe("()=>window.__a3dSunNow()") or {}
            ck(a6.get('sunTime') == '14:00' and (sn.get('settings') or {}).get('time') == '14:00' and (await safe("()=>window.__a3dSunSettings()")).get('time') == ss['time'],
               "while it plays the sun is the clock's (14:00 here); the study's time stays %s" % ss['time'])
            dome = ((await safe("()=>window.__a3dDgState()")) or {}).get('runs', {}).get('sun', {}).get('dome') or {}
            ck(dome.get('R') == site.get('Rc') and dome.get('c') == site.get('c'), "the sun paths keep their dome: the site's centre and radius (%s)" % dome)
            dp = R.dome_point(dome.get('c', [0, 0]), dome.get('y', 0), dome.get('R', 1), sn.get('azimuth', 0), sn.get('elevation', 0), a6.get('north', 0))
            sp = await scr(dp)
            sa = (a6.get('fr') or {}).get('sunAt')
            ck(sa and sp and abs(sa[0] - sp[0]) < 0.01 and abs(sa[1] - sp[1]) < 0.01, "the sun moving drawn on the dome where its 14:00 lies (%s, %s)" % (sa, sp and sp[:2]))
            nw = await by_key('sun', 'now')
            hh = [h for h in (await safe("()=>window.__a3dDgHits()") or []) if h['id'] == nw['id']]
            await safe("()=>window.__a3dAnimStop()")
            hs = [h for h in (await safe("()=>window.__a3dDgHits()") or []) if h['id'] == nw['id']]
            ck(hh and not hh[0]['boxes'] and hs and hs[0]['boxes'], "the sun now gives way to it, and comes back with Stop")
            ok_sides = []
            for hm in (8 * 60 + 30, 16 * 60):
                tt = (hm - math.ceil(day['sunrise'])) / (math.floor(day['sunset']) - math.ceil(day['sunrise'])) * R.SETTINGS['sun']['secs']
                a7 = await at(tt, -10)
                sc = await safe("(s)=>window.__a3dSunCalc(s.lat,s.lon,s.tz,s.date,'%s')" % R.hhmm(hm), ss) or {}
                az, el = math.radians(sc['azimuth'] + a7.get('north', 0)), math.radians(sc['elevation'])
                u = [-math.cos(el) * math.sin(az), math.cos(el) * math.cos(az)]
                L = math.hypot(*u)
                u = [u[0] / L, u[1] / L]
                await only([])
                dd_ = None
                for dist in range(18, 41, 2):
                    for lat in (0, 4, -4, 7, -7):
                        v = [-u[1] * lat, u[0] * lat]
                        pi, pa = await scr([dist * u[0] + v[0], 0, dist * u[1] + v[1]]), await scr([-dist * u[0] + v[0], 0, -dist * u[1] + v[1]])
                        if await ink(pi[0], pi[1], 1) == 0 and await ink(pa[0], pa[1], 1) == 0:
                            dd_ = (pi, pa)
                            break
                    if dd_:
                        break
                await only(['shadow'])
                a7 = await at(tt, -10)
                into, away = dd_ if dd_ else (pi, pa)
                ai, aa = await ink(into[0], into[1], 1), await ink(away[0], away[1], 1)
                ok_sides.append((R.hhmm(hm), a7.get('sunTime'), ai, aa, a7.get('fr', {}).get('shadowDone')))
            fop = ((await diags('shadow'))[0]['dg']['s'] or {}).get('fop', 0.4)
            ck(all(s[1] == s[0] and abs(s[2] - round(255 * fop)) <= 2 and s[3] == 0 and s[4] for s in ok_sides),
               "one shadow, the model's, on the side away from the sun at 08:30 and at 16:00, at one shadow's opacity, %.2f (%s)" % (fop, ok_sides))
            await only(R.ANALYZE_ORDER)
            await safe("()=>window.__a3dRunCmd('sunstudy')")
            await at(tm, -10)
            si, sp7 = await safe("()=>window.__a3dShadowInfo()") or {}, await safe("()=>window.__a3dSunPath()") or {}
            sn = await safe("()=>window.__a3dSunNow()") or {}
            ck(near(si.get('azimuth'), sn.get('azimuth'), 1e-9) and sp7.get('sun') and near(sp7['sun'][0], sn.get('azimuth'), 1e-9),
               "the sun study in plan follows the same clock: its shadows and its sun at 14:00")
            await safe("()=>window.__a3dAnimStop()")
            si = await safe("()=>window.__a3dShadowInfo()") or {}
            ck(near(si.get('azimuth'), day.get('azimuth'), 1e-9), "and back at the study's own time with Stop")
            await only([])
            await page.wait_for_timeout(150)
            ck((await btn()).get('shown') is True, "with the sun study on in plan, Play is there even with every analysis hidden")
            await safe("()=>window.__a3dRunCmd('sunstudy')")
            await only(R.ANALYZE_ORDER)
            await at(tm, -10)
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();window.__a3dSetPropTab&&window.__a3dSetPropTab('site');}")
            ptxt = await safe("()=>document.getElementById('a3d-propsbody').innerText") or ''
            ck(('altitude %.1f' % day['elevation']) in ptxt, "Properties shows the study's own sun, not the clock's")
            await safe("()=>window.__a3dAnimStop()")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. Motion in Properties")

            async def motion_opts(o):
                await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", o['id'])
                await page.wait_for_timeout(100)
                return await safe("""()=>{var s=document.querySelector('#a3d-propsbody select[data-dgf="anim"]');if(!s)return null;
                  return {v:[].map.call(s.options,function(x){return x.value;}),t:[].map.call(s.options,function(x){return x.text;}),sel:s.value,
                  label:(s.closest('.a3d-prow')||s.parentNode.parentNode).innerText.split('\\n')[0]};}""")
            w5 = await by_key('walk', 'w5')
            wa = WD[0]
            nw = await by_key('sun', 'now')
            shd = [o for o in await diags('shadow')][0]
            slope = [o for o in await diags('slope')]
            st1 = [o for o in await diags('streets') if R.auto('streets', o['dg']['k']) is None and 'march' in R.kinds(o['dg']['g'])][0]
            oo = [await motion_opts(x) for x in (w5, wa, nw, shd, st1)]
            ck(oo[0] and oo[0]['v'] == ['', 'none', 'march'] and oo[0]['t'] == ['Default (marching dashes)', 'Still', 'Marching dashes'] and oo[0]['sel'] == '',
               "a walk's streets: Default (marching dashes), Still, Marching dashes (%s)" % (oo[0] and oo[0]['t']))
            ck(oo[1] and oo[1]['v'] == ['', 'none', 'march', 'draw', 'ring'] and oo[1]['t'][0] == 'Default (drawn on)', "a wind's arrow, a closed shape: every motion (%s)" % (oo[1] and oo[1]['t']))
            ck(oo[2] and oo[2]['v'] == ['', 'none'] and oo[2]['t'] == ['Default (through the day)', 'Still'] and oo[3] and oo[3]['v'] == ['', 'none'],
               "the sun now and a shadow: through the day, or still")
            ck(oo[4] and oo[4]['v'] == ['', 'none', 'march'] and oo[4]['t'][0] == 'Default (still)', "a street of the hierarchy, still by default, can march")
            if slope:
                ck(await motion_opts(slope[0]) is None, "a slope class, a band, has no Motion")
            await safe("()=>window.__a3dTestClearUndo()")
            u1 = await safe("()=>window.__a3dUndoDepth()")
            await safe("(id)=>{window.__a3dSelectFor([id]);window.__a3dRefreshProps();}", w5['id'])
            await safe("()=>{var e=document.querySelector('#a3d-propsbody select[data-dgf=\"anim\"]');e.value='none';e.dispatchEvent(new Event('change',{bubbles:true}));}")
            w5b = await by_key('walk', 'w5')
            ck(w5b['dg']['s'].get('anim') == 'none' and await safe("()=>window.__a3dUndoDepth()") == u1 + 1 and (await safe("(id)=>window.__a3dAnimOf(id).motion", w5['id'])) is None,
               "Still chosen: the element's style, one undo step, and it no longer moves")
            ck(await safe("()=>/Changed by you/.test(document.getElementById('a3d-propsbody').innerText)") is True, "its status: changed by you")
            ck(await safe("(id)=>window.__a3dDgSet(id,'anim','none')", w5['id']) is True and await safe("()=>window.__a3dUndoDepth()") == u1 + 1, "the same again: no second step")
            ck(await safe("(id)=>window.__a3dDgSet(id,'anim','ring')", w5['id']) is False and await safe("(id)=>window.__a3dDgSet(id,'anim','spin')", w5['id']) is False
               and await safe("()=>window.__a3dUndoDepth()") == u1 + 1, "a motion its shape cannot take, or none at all, refused with no step")
            await safe("()=>window.__a3dUndo()")
            ck('anim' not in (await by_key('walk', 'w5'))['dg']['s'], "undone: its own again")
            await safe("(id)=>window.__a3dDgSet(id,'anim','march')", st1['id'])
            ck((await safe("(id)=>window.__a3dAnimOf(id)", st1['id']) or {}).get('motion') == 'march' and (await safe("(id)=>window.__a3dAnimOf(id)", st1['id']) or {}).get('out') is True,
               "a street set marching marches, away from the site")
            await safe("(id)=>window.__a3dDgSet(id,'anim','')", st1['id'])
            ck('anim' not in (await by_key('streets', st1['dg']['k']))['dg']['s'], "Default takes the setting away")
            w10 = await by_key('walk', 'w10')
            await safe("(id)=>window.__a3dDgSet(id,'anim','none')", w10['id'])
            await safe("()=>window.__a3dDgRun('walk')")
            ck((await by_key('walk', 'w10'))['dg']['s'].get('anim') == 'none', "the analysis run again keeps the owner's choice, as it keeps any change of style")
            await safe("(id)=>window.__a3dDgReset(id)", w10['id'])
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Save image")
            await only([])
            await safe("()=>{window.__a3dSetPlanView();window.__a3dCamSet({tx:0,tz:0,dist:160});}")
            await page.wait_for_timeout(200)
            tw = await scr([5, 24, 3])
            corner = [12, 12]
            img = await safe("""(a)=>new Promise(function(res){var r=window.__a3dViewportImage(),c=document.getElementById('a3d-canvas'),s=c.width/c.getBoundingClientRect().width,im=new Image();
              im.onload=function(){var k=document.createElement('canvas');k.width=im.width;k.height=im.height;var g=k.getContext('2d');g.drawImage(im,0,0);
                function P(p){return Array.prototype.slice.call(g.getImageData(Math.round(p[0]*s),Math.round(p[1]*s),1,1).data);}
                function O(p){return Array.prototype.slice.call(c.getContext('2d').getImageData(Math.round(p[0]*s),Math.round(p[1]*s),1,1).data);}
                res({engine:r.engine,w:r.w,h:r.h,cw:c.width,ch:c.height,tower:P(a[0]),corner:P(a[1]),otower:O(a[0]),ocorner:O(a[1])});};im.src=r.url;})""", [tw[:2], corner]) or {}
            ck(img.get('engine') == 'webgl' and img.get('w') == img.get('cw') and img.get('h') == img.get('ch'),
               "Save image here copies WebGL's canvas (headless Chromium has no WebGPU; the copy from its canvas is the same), at the view's size (%s)" % img.get('engine'))
            ck(img.get('otower', [0, 0, 0, 1])[3] == 0 and img.get('tower', [0, 0, 0, 0])[3] == 255 and img.get('tower')[:3] != img.get('corner', [0, 0, 0])[:3],
               "where the model is the overlay is clear, and the image holds the model: opaque, not the background (%s, %s)" % (img.get('tower'), img.get('corner')))
            ck(img.get('corner', [0, 0, 0, 0])[3] == 255, "the background too, not a hole")
            async with page.expect_download(timeout=20000) as dl:
                await safe("()=>{var b=document.querySelector('#a3d-railutil [data-a3druact=\"capture\"]');if(b)b.click();else window.__a3dRunCmd('SAVEIMAGE');}")
            d = await dl.value
            raw = pathlib.Path(await d.path()).read_bytes()
            ck(d.suggested_filename.endswith('.png') and png_size(raw) == (img.get('w'), img.get('h')), "the rail's Save image downloads it: %s, %s" % (d.suggested_filename, png_size(raw)))
            fpx = await safe("""(a)=>new Promise(function(res){var im=new Image(),c=document.getElementById('a3d-canvas'),s=c.width/c.getBoundingClientRect().width;im.onload=function(){var k=document.createElement('canvas');k.width=im.width;k.height=im.height;
              var g=k.getContext('2d');g.drawImage(im,0,0);res(Array.prototype.slice.call(g.getImageData(Math.round(a[1][0]*s),Math.round(a[1][1]*s),1,1).data));};im.src='data:image/png;base64,'+a[0];})""",
                             [base64.b64encode(raw).decode('ascii'), tw[:2]])
            ck(fpx == img.get('tower'), "and the file holds the model where the view shows it (%s)" % fpx)
            await only(R.ANALYZE_ORDER)
            await at(3.0, -10)
            i1 = (await safe("()=>window.__a3dViewportImage()") or {}).get('url')
            await at(9.5, -10)
            i2 = (await safe("()=>window.__a3dViewportImage()") or {}).get('url')
            ck(i1 and i2 and i1 != i2, "paused at two moments, two images: the motion as it stands")
            await safe("()=>window.__a3dAnimStop()")
            await safe("()=>{window.__a3dTestForceCpu(true);}")
            await safe("()=>window.__a3dCamSet({dist:161})")
            cp = await safe("()=>{var r=window.__a3dViewportImage();return {engine:r.engine,same:r.url===document.getElementById('a3d-canvas').toDataURL('image/png')};}") or {}
            await safe("()=>{window.__a3dTestForceCpu(false);window.__a3dCamSet({dist:160});}")
            ck(cp.get('engine') == '2d' and cp.get('same') is True, "drawn on the CPU, the image is the view's own canvas, as before (%s)" % cp)

            # ---------------------------------------------------------------------------------
            print("\n-- 9. Still on paper")
            sh = await safe("""()=>{var s=window.__a3dAddSheet('A-170','Motion','ANSI-B-L');var opts=window.__a3dSheetSourceOptions?window.__a3dSheetSourceOptions():[];
              var plan=opts.filter(function(o){return o.kind==='plan';})[0];var vp=plan?window.__a3dAddViewport(s,'plan',plan.refId||plan.id,'fit',100):null;window.__a3dOpenSheetView(s);return {s:s,vp:vp};}""") or {}
            await at(0.4, 0)
            pA = await safe("()=>window.__a3dRenderSheetPNG(2)")
            await at(6.3, -10)
            pB = await safe("()=>window.__a3dRenderSheetPNG(2)")
            await safe("()=>window.__a3dAnimStop()")
            pC = await safe("()=>window.__a3dRenderSheetPNG(2)")
            ck(sh.get('vp') and pA and pA == pB == pC, "a sheet with the plan on it is drawn the same at any moment of the clock, and as when still")
            ck(await safe("()=>{var g=document.getElementById('a3d-animgrp');return getComputedStyle(g).display;}") == 'none', "and on the sheet there is no Play")
            await safe("()=>window.__a3dCloseSheetView()")

            # ---------------------------------------------------------------------------------
            print("\n-- 10. A phone, a tablet, a computer")
            for (vw, vh, name) in ((390, 844, 'a phone'), (820, 1180, 'a tablet held upright'), (1440, 900, 'a computer')):
                await page.set_viewport_size({'width': vw, 'height': vh})
                await page.wait_for_timeout(500)
                lay = await safe("""()=>{var b=document.getElementById('a3d-animplay'),l=document.querySelector('.a3d-stlvl'),r=b.getBoundingClientRect(),lr=l?l.getBoundingClientRect():null,sp=b.querySelector('span');
                  var sn=document.querySelector('#a3d-snapgrp .a3d-stbtn');return {left:r.left,right:r.right,w:r.width,h:r.height,snapH:sn?sn.getBoundingClientRect().height:null,lvl:lr?lr.left:null,span:sp?getComputedStyle(sp).display:null,cap:l?getComputedStyle(l).fontSize:null,label:b.getAttribute('aria-label'),vw:window.innerWidth};}""") or {}
                if vw <= 1024:
                    ck(lay.get('left', -1) >= 0 and lay.get('right', 1e9) <= vw and lay.get('left', 0) < (lay.get('lvl') or 0) and lay.get('span') == 'none' and lay.get('label') == 'Play' and lay.get('h') == lay.get('snapH') and (vw > 720 or lay.get('h', 0) >= 32),
                       "%s: Play first in the bar, on the screen, an icon as large as the bar's own buttons (a thumb's on a phone), named for screen readers (%s)" % (name, lay))
                    ck(lay.get('cap') == '0px', "%s: the level's caption gives it its room (the selector says the level)" % name)
                    await only([])
                    await page.wait_for_timeout(200)
                    ck(await safe("()=>getComputedStyle(document.querySelector('.a3d-stlvl')).fontSize") != '0px', "%s, nothing to play: the caption back" % name)
                    await only(R.ANALYZE_ORDER)
                    await page.wait_for_timeout(200)
                else:
                    ck(lay.get('left', -1) >= 0 and lay.get('right', 1e9) <= vw and lay.get('span') != 'none', "%s: PLAY in the bar, on the screen, with its word (%s)" % (name, lay))

            # ---------------------------------------------------------------------------------
            # ---------------------------------------------------------------------------------
            print("\n-- 11. A reload")
            await safe("()=>window.__a3dAnimPlay(true)")
            await page.wait_for_timeout(300)
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2500)
            await safe("()=>window.__a3dEnter&&window.__a3dEnter()")
            await page.wait_for_timeout(500)
            rl = await anim()
            nd = len(await diags())
            ck(nd == len(DG) and rl.get('on') is False and rl.get('paused') is False and rl.get('live') is False and rl.get('t') == 0 and (await btn()).get('text') == 'PLAY',
               "the project reloaded with its %d analysis elements, left playing: it opens still, PLAY ready (%s)" % (nd, {k: rl.get(k) for k in ('on', 'paused', 'live', 't')}))

            # ---------------------------------------------------------------------------------
            print("")
            ck(not errs, "zero uncaught page errors (%s)" % (errs[:3] or 'none'))
        except Stalled as e:
            ck(False, "STALLED: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the suite raised")
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        print("RESULT: FAIL")
        for m in ck.bad:
            print("   - " + m)
        return 1
    print("RESULT: PASS")
    return 0


sys.exit(asyncio.run(run()))
