#!/usr/bin/env python3
"""bim_phase171b_workspace_browser_tests.py -- V171b: the analysis workspace.

The site analysis as a place one goes into and leaves (reference/research-analysis-workspace.md): a bar over the view,
the analyses on the left in their groups, one in focus and others ticked under it, the one analysis on the right where
Properties is while nothing is selected, the view quiet in the app's own light or dark mode. Every service is answered
in the browser by tests/traffic_fixture.py (V171's neighbourhood); the satellite map's tiles by one red square, so what
the workspace does to the map can be read back from the pixels.

  1. THE RECORDS: the marker, the version, SITEWORKSPACE and its words.
  2. BEFORE A RUN: the workspace with nothing analysed; leaving gives Analyze back.
  3. ANALYZE SITE ENDS IN IT: the site and its context, nothing in focus, in the run's one undo step; the bar, the
     list in its six groups, the overview, nothing to draw with on screen.
  4. ONE AT A TIME: a name puts its analysis in focus, drawn alone, in the list, the bar and the panel; one undo step,
     undone and done again.
  5. TICKS: drawn under the focus, in the bar's count and the key on the view, at its bottom left; unticked; the
     focus unticked.
  6. THE LOOK, DARK AND LIGHT: the ground, the context's tones, the map greyed and faded, the words, the key's colours,
     the panel's text; outside the workspace, as before.
  7. THE PANEL: the key in full, what the run said, the source, the chart where the app has one, the buttons.
  8. TRAFFIC: in focus, in its one step, playing; Pause and Stop in the panel.
  9. IN AND OUT: leaving keeps what was shown; Open from a row and from the site; a selection shows its properties;
     a second run keeps the focus.
 10. A PHONE: the view in sight, the chips with the focus in view, Details opens the panel, the key on the view.
 11. A ROW THAT FITS: Traffic's row in Analyze keeps its name in sight beside "Stop the simulation".

The harness never waits without a bound (V123).
"""
import asyncio, pathlib, re, struct, sys, traceback, zlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import traffic_fixture as FX   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
SC = 0.35
LOT = [list(p) for p in FX.LOT]
MASSES = [(20, -25, 18, 28, 31, 'use-res'), (40, -25, 18, 28, 18, 'use-off'), (30, -15, 38, 8, 4.5, 'use-ret'), (30, -35, 38, 8, 16, 'use-hot')]
GROUPS = [('site', ['frame']), ('sun', ['sun', 'shadow', 'wind']), ('see', ['views', 'noise']),
          ('ground', ['contours', 'slope', 'aspect', 'flow', 'ponds', 'flood']),
          ('move', ['streets', 'cycling', 'transit', 'walk', 'needs', 'vehicles', 'traffic']),
          ('land', ['landuse', 'figure', 'green', 'zoning'])]
LIGHT = {'bg': (0xf2, 0xf2, 0xef), 'building': '#fbfbfa', 'terrain': '#e9e8e3', 'road': '#dcdcd8'}
DARK = {'bg': (0x17, 0x19, 0x1c), 'building': '#4c525b', 'terrain': '#25292e', 'road': '#363b42'}


def red_png(n=256):
    """one red square, for every map tile"""
    raw = b''.join(b'\x00' + b'\xe0\x20\x20' * n for _ in range(n))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')


TILE = red_png()


def near(c, want, tol=6):
    return c is not None and all(abs(c[i] - want[i]) <= tol for i in range(3))


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def page_for(vp, mobile=False):
            ctx = await browser.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=2 if mobile else 1)
            ST = {'tr': ()}
            for h in FX.HOSTS:
                await ctx.route(h, FX.route_handler(ST))
            await ctx.route('https://server.arcgisonline.com/**', lambda r: r.fulfill(status=200, body=TILE, headers={'Content-Type': 'image/png', 'Access-Control-Allow-Origin': '*'}))
            for h in ('https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**'):
                await ctx.route(h, lambda r: r.abort())
            pg = await ctx.new_page()
            pg.errs = []
            pg.on('pageerror', lambda e: pg.errs.append(str(e)))
            return ctx, pg

        ctx, page = await page_for({'width': 1440, 'height': 900})
        errs = page.errs

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def aw(pg=None):
            return await safe("()=>window.__a3dAw()", pg=pg) or {}

        async def design(pg=None):
            pg = pg or page
            await safe("""(a)=>{var o=window.__a3dState().objs.filter(function(x){return x.t!=='property'&&x.id!=='LOT'&&x.t!=='box';});
              o.push({id:'LOT',t:'sketch',name:'Lot',col:'#5ec4b8',pos:[0,0,0],pts:a,y:0,closed:true,layer:'layer-0'});
              window.__a3dTestSetObjs(o);window.__a3dPropertyFromSketch('LOT');}""", LOT, pg=pg)
            for (x, z, w, d, h, u) in MASSES:
                bid = await safe("(a)=>window.__a3dAdd('box',{Length:a[0],Width:a[1],Height:a[2]}).id", [w / SC, d / SC, h / SC], pg=pg)
                await safe("(a)=>{var L=window.__a3dState().objs;L.forEach(function(o){if(o.id===a[0])o.pos=[a[1],a[2],a[3]];});window.__a3dTestSetObjs(L);}", [bid, x, h / 2, z], pg=pg)
                await safe("(a)=>window.__a3dUsageAssign([a[0]],a[1])", [bid, u], pg=pg)

        async def analyse(pg=None):
            pg = pg or page
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(300)
            if await safe("()=>!!document.querySelector('[data-saaddr]')", pg=pg):
                await pg.fill('[data-saaddr]', '1 Market Street')
                await pg.press('[data-saaddr]', 'Enter')
            else:
                await safe("()=>document.querySelector('[data-saact=\"analyze\"],.a3d-awl [data-anzact=\"aw:analyze\"]').click()", pg=pg)
            for _ in range(240):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await pg.wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def click(sel, pg=None):
            return await safe("(s)=>{var b=document.querySelector(s);if(!b)return false;b.click();return true;}", sel, pg=pg)

        async def text(sel, pg=None):
            return await safe("(s)=>{var e=document.querySelector(s);return e?e.textContent.replace(/\\s+/g,' ').trim():null;}", sel, pg=pg)

        async def shown_layers(pg=None):
            """the analyses whose layer, and those above it, are on"""
            return set((await aw(pg)).get('shown', []))

        async def px(x, y, pg=None):
            """the view's pixel at (x, y) of the drawing canvas, the model and the overlay composed (Save image's copy)"""
            return await safe("""(a)=>new Promise(function(res){var r=window.__a3dViewportImage(),c=document.getElementById('a3d-canvas'),s=c.width/c.getBoundingClientRect().width,im=new Image();
              im.onload=function(){var k=document.createElement('canvas');k.width=im.width;k.height=im.height;var g=k.getContext('2d');g.drawImage(im,0,0);
                res(Array.prototype.slice.call(g.getImageData(Math.round(a[0]*s),Math.round(a[1]*s),1,1).data));};im.onerror=function(){res(null);};im.src=r.url;})""", [x, y], pg=pg)

        async def view_box(pg=None):
            return await safe("()=>{var r=document.getElementById('a3d-canvas').getBoundingClientRect();return [r.left,r.top,r.width,r.height];}", pg=pg)

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV171b") or ''
            ck(all(w in mk for w in ('workspace', 'focus', 'ticks', 'look', 'ctxtones', 'mapgrey', 'phone', 'rowfit')), "the V171b marker (%s)" % mk)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 171, "the app says V171 or later: a sub-phase keeps its phase's number, as V166b did (%s)" % (mv and mv.group(1)))
            cat = await safe("()=>window.__a3dCommandCatalog().filter(function(c){return c.name==='SITEWORKSPACE';})") or []
            ck(len(cat) == 1 and 'ANALYSISWORKSPACE' in (cat[0].get('aliases') or []), "SITEWORKSPACE is a command, ANALYSISWORKSPACE its alias (%s)" % cat[:1])
            found = [x['name'] for x in (await safe("()=>window.__a3dCommandSearch('archimap',5)") or [])]
            ck('SITEWORKSPACE' in found[:3], "searching 'archimap' finds it (%s)" % found[:3])
            gr = await safe("()=>window.__a3dAwGroups()") or []
            ck([(g['id'], g['an']) for g in gr] == GROUPS, "the analyses in six groups, each of the 23 once, in Analyze's order (%s)" % [g['id'] for g in gr])
            alln = await safe("()=>window.__a3dAw().run.length+0")
            ck(sum(len(a) for _, a in GROUPS) == 23 and alln == 0, "23 analyses; none run yet (%s)" % alln)

            # ---------------------------------------------------------------------------------
            print("\n-- 2. Before a run")
            await safe("()=>window.__a3dRunCmd('siteworkspace')")
            await page.wait_for_timeout(300)
            a0 = await aw()
            ck(a0.get('on') is True and a0.get('now') is None, "SITEWORKSPACE opens it, nothing in focus (%s)" % {k: a0.get(k) for k in ('on', 'now')})
            ck(await safe("()=>!!document.querySelector('.a3d-analyze-wrap .a3d-awl')&&!document.querySelector('.a3d-analyze-wrap [data-anzcard]')"),
               "the left panel is the workspace's list, not Analyze's rows")
            emp = await text('.a3d-awl-empty')
            ck(emp and 'Analyze site' in emp, "with nothing analysed the list says how to start (%s)" % emp)
            ov = await text('[data-awpanel="overview"] .a3d-awp-ttl')
            ck(ov == 'Overview' and await text('#a3d-rpttl') == 'Analysis', "the panel is the overview, and Properties' title says Analysis (%s)" % ov)
            ck(await text('#a3d-awbar [data-awbart]') == 'Overview', "the bar names it")
            ck(await click('#a3d-awbar [data-awact="leave"]') and (await aw()).get('on') is False, "the bar's cross leaves")
            ck(await safe("()=>!document.getElementById('a3d-awbar')&&!!document.querySelector('.a3d-analyze-wrap [data-anzcard]')") and await text('#a3d-rpttl') == 'Properties',
               "out of it: the bar gone, Analyze's rows back, Properties' title back")

            # ---------------------------------------------------------------------------------
            print("\n-- 3. Analyze site ends in it")
            await design()
            u0 = await safe("()=>window.__a3dUndoDepth()")
            st = await analyse()
            a1 = await aw()
            ck(len(a1.get('run', [])) == 23 and a1.get('on') is True and a1.get('now') is None and a1.get('shown') == [],
               "Analyze site ends in the workspace: all 23 run, none in focus, none drawn: the site and its context (%s)" % {k: a1.get(k) for k in ('on', 'now', 'shown')})
            ck(await safe("()=>window.__a3dUndoDepth()") == (u0 or 0) + 1, "inside the run's one undo step")
            lys = await safe("()=>window.__a3dLayers()") or []
            D = await safe("()=>window.__a3dDgState()") or {}
            root = next((l for l in lys if l['id'] == D.get('layers', {}).get('root')), None)
            ck(root and root.get('visible') is not False, "the Site analysis layer stays on: its analyses' own are off")
            nrow = await safe("()=>document.querySelectorAll('.a3d-awl [data-awrow]').length")
            ngrp = await safe("()=>[].map.call(document.querySelectorAll('.a3d-awl [data-awgrp]'),function(g){return g.getAttribute('data-awgrp');})")
            ck(nrow == 23 and ngrp == [g for g, _ in GROUPS], "the list: 23 rows in the six groups (%s, %s)" % (nrow, ngrp))
            ck(await safe("()=>[].every.call(document.querySelectorAll('.a3d-awl .a3d-awl-tick'),function(t){return !t.checked;})"), "none ticked")
            stp = await safe("()=>document.querySelectorAll('[data-awpanel=\"overview\"] .a3d-awp-steps li').length")
            ck(stp and stp >= 6, "the overview lists what the run fetched (%s steps)" % stp)
            dock = await safe("()=>{var d=document.getElementById('a3d-dock');return d?getComputedStyle(d).display:'none';}")
            ck(dock == 'none', "nothing to draw with on screen while it is open (the dock: %s)" % dock)
            ck(await safe("()=>window.__a3dDgLegend()") is None, "nothing drawn, no key on the view")

            # ---------------------------------------------------------------------------------
            print("\n-- 4. One at a time")
            u1 = await safe("()=>window.__a3dUndoDepth()")
            ck(await click('.a3d-awl [data-awrow="sun"] .a3d-awl-nm'), "a name pressed")
            await page.wait_for_timeout(200)
            a2 = await aw()
            ck(a2.get('now') == 'sun' and a2.get('shown') == ['sun'], "Sun paths in focus, drawn alone (%s)" % a2.get('shown'))
            ck(await safe("()=>window.__a3dUndoDepth()") == (u1 or 0) + 1, "one undo step")
            ck(await safe("()=>{var r=document.querySelector('.a3d-awl [data-awrow=\"sun\"]');return r.classList.contains('focus')&&r.querySelector('.a3d-awl-tick').checked&&r.querySelector('.a3d-awl-nm').getAttribute('aria-pressed')==='true';}"),
               "its row: in focus, ticked, pressed")
            ck(await text('#a3d-awbar [data-awbart]') == 'Sun paths' and await text('[data-awpanel="sun"] .a3d-awp-ttl') == 'Sun paths',
               "the bar and the panel name it")
            await click('.a3d-awl [data-awrow="wind"] .a3d-awl-nm')
            await page.wait_for_timeout(150)
            a3 = await aw()
            ck(a3.get('now') == 'wind' and a3.get('shown') == ['wind'], "another name: it alone, the first gone (%s)" % a3.get('shown'))
            await safe("()=>window.__a3dRunCmd('undo')")
            await page.wait_for_timeout(150)
            a4 = await aw()
            bt = await text('#a3d-awbar [data-awbart]')
            lr = await safe("()=>{var r=document.querySelector('.a3d-awl .a3d-awl-row.focus');return r?r.getAttribute('data-awrow'):null;}")
            ck(a4.get('now') == 'sun' and a4.get('shown') == ['sun'] and bt == 'Sun paths' and lr == 'sun',
               "undone: Sun paths again, in the layers, the list and the bar (%s)" % [a4.get('now'), a4.get('shown'), bt, lr])
            await safe("()=>window.__a3dRunCmd('redo')")
            await page.wait_for_timeout(150)
            ck((await aw()).get('now') == 'wind', "done again: Winds")
            await click('.a3d-awl-ov')
            await page.wait_for_timeout(150)
            ck((await aw()).get('shown') == [] and await text('#a3d-awbar [data-awbart]') == 'Overview', "Overview: none in focus, none drawn")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. Ticks")
            await safe("()=>window.__a3dSetPlanView()")
            await safe("()=>window.__a3dCamSet({tx:20,tz:-10,dist:420})")
            await click('.a3d-awl [data-awrow="noise"] .a3d-awl-nm')
            await click('.a3d-awl [data-awrow="streets"] .a3d-awl-tick')
            await page.wait_for_timeout(250)
            a5 = await aw()
            ck(a5.get('now') == 'noise' and set(a5.get('shown', [])) == {'noise', 'streets'} and a5.get('add') == ['streets'],
               "a tick draws Street hierarchy under Noise (%s)" % a5.get('shown'))
            ck((await text('#a3d-awbar .a3d-awbar-n') or '').replace(' ', '') == '+1', "the bar counts it")
            ck(await safe("()=>document.querySelector('.a3d-awl [data-awrow=\"streets\"]').classList.contains('add')"), "its row marked as drawn with the focus")
            lg = await safe("()=>window.__a3dDgLegend()") or {}
            vb = await view_box() or [0, 0, 1, 1]
            titles = [b['title'] for b in lg.get('blocks', [])]
            box = lg.get('box') or [0, 0, 0, 0]
            ck(sorted(titles) == ['Noise', 'Street hierarchy'], "the key on the view: the two drawn, and only them (%s)" % titles)
            ck(box[0] <= 24 and box[1] + box[3] >= vb[3] - 24, "at the view's bottom left (%s in %s)" % ([round(v) for v in box], [round(v) for v in vb]))
            await click('.a3d-awl [data-awrow="streets"] .a3d-awl-tick')
            await page.wait_for_timeout(150)
            ck((await aw()).get('shown') == ['noise'], "unticked: gone")
            await click('.a3d-awl [data-awrow="noise"] .a3d-awl-tick')
            await page.wait_for_timeout(150)
            a6 = await aw()
            ck(a6.get('now') is None and a6.get('shown') == [], "the focus unticked: none in focus (%s)" % a6)

            # ---------------------------------------------------------------------------------
            print("\n-- 6. The look, dark and light")
            await safe("()=>window.__a3dAwFocus('sun')")
            await safe("()=>window.__a3dSet3DView()")
            await safe("()=>window.__a3dCamSet({tx:30,tz:-20,dist:420})")
            await page.wait_for_timeout(300)
            vb = await view_box()
            sky = [vb[2] * 0.5, 30]
            ids = await safe("""()=>{var O=window.__a3dState().objs,f=function(k){var o=O.filter(function(x){return x.context&&x.context.kind===k;})[0];return o?o.id:null;};
              return {b:f('buildings'),t:f('terrain'),r:f('roads'),own:O.filter(function(x){return x.usage;})[0].id};}""") or {}
            for mode, L in (('dark', DARK), ('light', LIGHT)):
                await safe("(m)=>{document.body.classList.toggle('light-theme',m==='light');window.__a3dRefreshAll&&window.__a3dRefreshAll();}", mode)
                await safe("()=>window.__a3dCamSet({dist:421})")
                await page.wait_for_timeout(300)
                a7 = await aw()
                c = await px(sky[0], sky[1])
                ck(a7.get('look') == mode and near(c, L['bg']), "%s mode: the view's ground is the mode's (%s, %s)" % (mode, a7.get('bg'), c))
                g = await px(vb[2] * 0.6, vb[3] - 30)
                ck(g and abs(g[0] - g[2]) <= 12 and abs(g[0] - g[1]) <= 12, "%s mode: the terrain near the camera in its quiet tone, not brown, no map draped on it (%s)" % (mode, g))
                cols = {k: await safe("(i)=>window.__a3dAwCtxCol(i)", ids.get(k)) for k in ('b', 't', 'r', 'own')}
                ck(cols == {'b': L['building'], 't': L['terrain'], 'r': L['road'], 'own': None},
                   "%s mode: the context's buildings, terrain and roads in the mode's tones; the design keeps its own colours (%s)" % (mode, cols))
                mvl = await safe("()=>window.__a3dAwMvLight()")
                ck(mvl is (mode == 'light'), "%s mode: the streets' analyses and the cars take the mode's colours, not the map's (%s)" % (mode, mvl))
                ink = await safe("()=>window.__a3dAwInk('#ffb347')")
                ck((ink != '#ffb347') if mode == 'light' else (ink == '#ffb347'), "%s mode: a light word's colour %s (%s)" % (mode, 'darkened to be read on paper' if mode == 'light' else 'kept', ink))
                tc = await safe("()=>getComputedStyle(document.querySelector('.a3d-awp-ttl')).color")
                ck((tc == 'rgb(31, 35, 40)') if mode == 'light' else (tc != 'rgb(31, 35, 40)'), "%s mode: the panel's title in the mode's ink (%s)" % (mode, tc))
                kb = await safe("()=>getComputedStyle(document.querySelector('.a3d-awbar-row')).backgroundColor")
                ck(('255, 255, 255' in (kb or '')) == (mode == 'light'), "%s mode: the bar in the mode's colours (%s)" % (mode, kb))
            # the context's roads are sketches: their lines too
            await safe("()=>window.__a3dSetPlanView()")
            await safe("()=>window.__a3dCamSet({tx:20,tz:-10,dist:420})")
            await page.wait_for_timeout(800)
            rp = await safe("()=>window.__a3dToScreen([-100,0])")
            road_in = await px(rp[0], rp[1])
            ck(near(road_in, (0xdc, 0xdc, 0xd8), 4), "light mode, in plan: Market Street's line in the road tone (%s)" % road_in)
            mp = await safe("()=>window.__a3dToScreen([0,-100])")
            map_in = await px(mp[0], mp[1])
            bc = await safe("""()=>{var o=window.__a3dState().objs.filter(function(x){return x.context&&x.context.kind==='buildings'&&x.mesh&&x.mesh.v;})[0],v=o.mesh.v,x=0,z=0;
              v.forEach(function(p){x+=p[0];z+=p[2];});return window.__a3dToScreen([o.pos[0]+x/v.length,o.pos[2]+z/v.length],60);}""")
            b_in = await px(bc[0], bc[1])
            # the map: one red square everywhere, greyed and faded in the workspace
            await safe("()=>window.__a3dCamSet({tx:20,tz:-10,dist:3000})")
            await page.wait_for_timeout(1500)
            far = [vb[2] - 30, vb[3] - 60]
            m_in = await px(far[0], far[1])
            ck(m_in and abs(m_in[0] - m_in[1]) <= 4 and abs(m_in[1] - m_in[2]) <= 4 and m_in[0] > 150,
               "the map in the workspace: grey, and faded toward the light ground (%s)" % m_in)
            await safe("()=>window.__a3dAwLeave()")
            await safe("()=>window.__a3dCamSet({dist:3001})")
            await page.wait_for_timeout(600)
            m_out = await px(far[0], far[1])
            ck(m_out and m_out[0] > m_out[1] + 60, "out of it, the map as it is (%s)" % m_out)
            await safe("()=>window.__a3dCamSet({tx:20,tz:-10,dist:420})")
            await page.wait_for_timeout(800)
            road_out = await px(rp[0], rp[1])
            map_out = await px(mp[0], mp[1])
            b_out = await px(bc[0], bc[1])
            ck(b_in and b_out and sum(b_in[:3]) >= sum(b_out[:3]) + 45 and min(b_in[:3]) >= 200,
               "a context building drawn in the light mode's tone in the workspace, the app's own out of it (%s, %s)" % (b_in, b_out))
            ck(road_out and not near(road_out, (0xdc, 0xdc, 0xd8), 30) and map_in and map_out and map_out[0] > map_out[1] + 60 and abs(map_in[0] - map_in[1]) <= 4,
               "out of it the road's line and the map near the site as they were (%s, %s; in it %s)" % (road_out, map_out, map_in))
            await safe("()=>window.__a3dSet3DView()")
            await safe("()=>window.__a3dCamSet({tx:30,tz:-20,dist:420})")
            await page.wait_for_timeout(800)
            g_out = await px(vb[2] * 0.6, vb[3] - 30)
            ck(g_out and g_out[0] - g_out[2] > 40, "out of it the terrain as it is (%s)" % g_out)
            outl = await aw()
            ck(outl.get('look') is None and outl.get('bg') == '#1d2024' and await safe("(i)=>window.__a3dAwCtxCol(i)", ids.get('b')) is None,
               "out of it the view's ground and the context's colours are the app's own (%s)" % outl.get('bg'))
            await safe("()=>document.body.classList.remove('light-theme')")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. The panel")
            await safe("()=>window.__a3dAwFocus('wind')")
            await page.wait_for_timeout(200)
            run = (D.get('runs') or {}) if D else {}
            D = await safe("()=>window.__a3dDgState()") or {}
            keys = await safe("()=>[].map.call(document.querySelectorAll('[data-awpanel=\"wind\"] .a3d-awp-keyi'),function(e){return e.textContent;})") or []
            ck(keys == [r['name'] for r in D['runs']['wind']['legend']], "its key in full, every row the run gave (%s)" % keys)
            ck(await safe("()=>!!document.querySelector('[data-awpanel=\"wind\"] .a3d-awp-chart svg')"), "the winds' rose, the climate's own chart")
            src = await safe("()=>document.querySelector('[data-awpanel=\"wind\"]').textContent")
            ck(D['runs']['wind'].get('source') and D['runs']['wind']['source'] in (src or ''), "the source the run named (%s)" % D['runs']['wind'].get('source'))
            ck('From the' in (src or '') and 'm/s' in (src or ''), "the rose's caption: the prevailing direction and the mean speed")
            await safe("()=>window.__a3dAwFocus('sun')")
            await page.wait_for_timeout(150)
            ck(await safe("()=>!!document.querySelector('[data-awpanel=\"sun\"] .a3d-awp-chart svg')") and 'midsummer' in (await text('[data-awpanel="sun"] .a3d-awp-cap') or ''),
               "the sun's paths drawn looking up, and their caption")
            ab = await text('[data-awpanel="sun"] .a3d-awp-about')
            ck(ab and 'solstices' in ab, "what it shows, in a sentence (%s)" % ab)
            n0 = await safe("()=>window.__a3dDgDiagsCount?window.__a3dDgDiagsCount('sun'):window.__a3dState().objs.filter(function(o){return o.t==='diag'&&o.dg.a==='sun';}).length")
            ck(await click('[data-awpanel="sun"] [data-awact="dg:select:sun"]') and await safe("()=>window.__a3dSelSetLen?window.__a3dSelSetLen():window.__a3dAwSel().length") == n0,
               "Select selects its elements (%s)" % n0)
            await safe("()=>window.__a3dSelectFor([])")
            await safe("()=>window.__a3dRefreshProps&&window.__a3dRefreshProps()")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. Traffic")
            u2 = await safe("()=>window.__a3dUndoDepth()")
            await safe("()=>window.__a3dRunCmd('traffic')")
            await page.wait_for_timeout(600)
            a8 = await aw()
            an = await safe("()=>window.__a3dAnim()") or {}
            ck(a8.get('on') is True and a8.get('now') == 'traffic' and a8.get('shown') == ['traffic'] and an.get('on') is True,
               "TRAFFIC: Traffic and people in focus in the workspace, alone, and playing (%s)" % a8.get('shown'))
            ck(await safe("()=>window.__a3dUndoDepth()") == (u2 or 0) + 1, "in the command's one undo step")
            ck(await safe("()=>!!document.querySelector('[data-awpanel=\"traffic\"] [data-anzact=\"tr:peak:am\"]')"), "its settings in the panel")
            await click('[data-awpanel="traffic"] [data-awact="anim:play"]')
            await page.wait_for_timeout(150)
            ck((await safe("()=>window.__a3dAnim()") or {}).get('paused') is True, "Pause in the panel keeps the moment")
            await click('[data-awpanel="traffic"] [data-awact="anim:stop"]')
            await page.wait_for_timeout(150)
            an2 = await safe("()=>window.__a3dAnim()") or {}
            ck(an2.get('on') is False and an2.get('paused') is False, "Stop gives the drawing back")
            await click('[data-awpanel="traffic"] [data-anzact="tr:speed:4"]')
            ck((await safe("()=>window.__a3dTrSettings()") or {}).get('speed') == 4, "the speed set in the panel")
            await safe("()=>window.__a3dRunCmd('trafficoff')")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. In and out")
            await safe("()=>window.__a3dAwFocus('views')")
            await safe("()=>window.__a3dAwTick('green')")
            await click('.a3d-awl-back')
            await page.wait_for_timeout(200)
            ck((await aw()).get('on') is False and await shown_layers() == {'views', 'green'}, "the list's back button leaves; what was shown stays shown")
            ck(await safe("()=>!!document.querySelector('.a3d-analyze-wrap [data-anzact=\"aw:open:\"]')"), "Analyze's site part offers Open the site analysis")
            ck(await safe("()=>{var b=document.querySelector('[data-anzcard=\"dgnoise\"] [data-anzact=\"aw:open:noise\"]');if(!b)return false;b.click();return true;}"), "a row's Open pressed")
            await page.wait_for_timeout(200)
            a9 = await aw()
            ck(a9.get('on') is True and a9.get('now') == 'noise', "Open: the workspace, that analysis in focus (%s)" % a9.get('now'))
            dg = await safe("()=>window.__a3dState().objs.filter(function(o){return o.t==='diag'&&o.dg.a==='noise';})[0].id")
            await safe("(i)=>{window.__a3dSelectFor([i]);window.__a3dRefreshProps&&window.__a3dRefreshProps();}", dg)
            await safe("()=>window.__a3dCamSet({dist:420})")
            await page.wait_for_timeout(150)
            ck(await text('#a3d-rpttl') == 'Properties' and not await safe("()=>!!document.querySelector('#a3d-propsbody [data-awpanel]')"), "an element selected: its properties, as anywhere")
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps&&window.__a3dRefreshProps();}")
            await safe("()=>window.__a3dCamSet({dist:421})")
            await page.wait_for_timeout(150)
            ck(await text('#a3d-rpttl') == 'Analysis' and await safe("()=>!!document.querySelector('#a3d-propsbody [data-awpanel=\"noise\"]')"), "nothing selected: the analysis again")
            await safe("()=>window.__a3dAwTick('streets')")
            ck(await click('.a3d-awl [data-anzact="aw:analyze"]') and (await safe("()=>window.__a3dSiteRunState()") or {}).get('busy') is True,
               "the list's Analyze again runs it")
            for _ in range(240):
                if not (await safe("()=>window.__a3dSiteRunState()") or {}).get('busy'):
                    break
                await page.wait_for_timeout(250)
            a10 = await aw()
            ck(a10.get('now') == 'noise' and set(a10.get('shown', [])) == {'noise', 'green', 'streets'}, "Analyze site again, from the list, keeps the focus and the ticks (%s)" % a10.get('shown'))

            # ---------------------------------------------------------------------------------
            print("\n-- 10. A phone")
            pc, pp = await page_for({'width': 390, 'height': 844}, mobile=True)
            await within(pp.goto('file://' + str(HTML)), 'goto phone')
            await pp.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()", pg=pp)
            await design(pp)
            await analyse(pp)
            await safe("()=>window.__a3dAwFocus('needs')", pg=pp)
            await pp.wait_for_timeout(400)
            ph = await safe("""()=>{var sh=document.getElementById('a3d-shell'),b=document.getElementById('a3d-awbar'),ch=b&&b.querySelector('.a3d-awchips'),on=ch&&ch.querySelector('.a3d-awchip.on'),
              cv=document.getElementById('a3d-canvas').getBoundingClientRect(),br=b?b.getBoundingClientRect():null,cr=ch?ch.getBoundingClientRect():null,orr=on?on.getBoundingClientRect():null;
              return {tier:document.body.classList.contains('a3d-tier-phone'),collapsed:sh.classList.contains('collapsed'),cv:[cv.width,cv.height],bar:br?[br.left,br.right]:null,
                chips:ch?getComputedStyle(ch).display:null,onIn:!!(orr&&cr&&orr.left>=cr.left-1&&orr.right<=cr.right+1),onText:on?on.textContent:null};}""", pg=pp) or {}
            ck(ph.get('tier') and ph.get('collapsed') and ph.get('cv', [0, 0])[1] > 400, "a phone: the drawer closed, the view in sight (%s)" % ph)
            ck(ph.get('chips') == 'flex' and ph.get('onText') == 'Daily needs' and ph.get('onIn'), "the analyses as chips under the bar, the one in focus in view (%s)" % ph.get('onText'))
            ck(ph.get('bar') and ph['bar'][1] <= 390 and ph['bar'][0] >= 0, "the bar within the screen (%s)" % ph.get('bar'))
            ck(await click('#a3d-awbar [data-awact="panel"]', pg=pp) and await safe("()=>document.getElementById('a3d-right').classList.contains('open')&&!!document.querySelector('#a3d-propsbody [data-awpanel=\"needs\"]')", pg=pp),
               "Details opens the panel, the analysis in it")
            await click('#a3d-awbar [data-awact="panel"]', pg=pp)
            await click('#a3d-awbar .a3d-awchip[data-awact="focus:transit"]', pg=pp)
            await pp.wait_for_timeout(300)
            ck((await aw(pp)).get('now') == 'transit', "a chip puts its analysis in focus")
            lgp = await safe("()=>window.__a3dDgLegend()", pg=pp) or {}
            ck([b['title'] for b in lgp.get('blocks', [])] == ['Transit'], "the key of the one in focus on a phone's view (%s)" % [b['title'] for b in lgp.get('blocks', [])])
            ck(not pp.errs, "the phone: zero uncaught page errors (%s)" % (pp.errs[:2] or 'none'))
            await pc.close()

            # ---------------------------------------------------------------------------------
            print("\n-- 11. A row that fits")
            await safe("()=>window.__a3dAwLeave()")
            await safe("()=>window.__a3dTrAct('sim:on')")
            await page.wait_for_timeout(300)
            await safe("()=>window.__a3dAwLeave()")
            await safe("()=>window.__a3dAnzView(true)")
            await safe("()=>window.__a3dSaGoto('access')")
            await page.wait_for_timeout(300)
            wt = await safe("()=>{var t=document.querySelector('[data-anzcard=\"dgtraffic\"] .a3d-anzttl'),b=document.querySelector('[data-anzcard=\"dgtraffic\"] .a3d-anzhd>.a3d-anzbtn');return t&&b?[t.getBoundingClientRect().width,b.textContent]:null;}")
            ck(wt and wt[0] >= 60 and 'Stop' in wt[1], "Traffic's row keeps its name in sight beside \"%s\" (%s px)" % (wt and wt[1], wt and round(wt[0])))
            await safe("()=>window.__a3dRunCmd('trafficoff')")

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
