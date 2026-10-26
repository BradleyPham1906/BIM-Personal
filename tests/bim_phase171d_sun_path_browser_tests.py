#!/usr/bin/env python3
"""bim_phase171d_sun_path_browser_tests.py -- V171d: the sun path, one clock.

The owner: the sun path, its animation and the shadows should agree through the hours and the dates; the math checked
against NOAA's algorithm and the dome by X = R cos(alt) sin(az), Y = R sin(alt), Z = R cos(alt) cos(az); sliders for
latitude, longitude, date and time; a mesh on the dome coloured by the temperature; the solstices and the equinoxes
on the right, with diagrams. Every service is answered in the browser by tests/site_analysis_fixture.py (V164's), its
climate fetched on a summer day (UTC-4 for New York); what the app should draw is worked out again in
tests/sun_reference.py from the sources.

  1. THE RECORDS: the marker, the version, the hooks.
  2. THE MATH: the app's sun against NOAA's spreadsheet in Python at 192 moments, and against NREL SPA's example.
  3. THE ZONES: the offsets against Python's own time zone database, daylight saving's change included; standard time.
  4. THE CLIMATE'S OFFSET: fetched in summer, the site keeps the zone and its standard time; an offset typed is kept.
  5. THE DOME: the paths, their hours, the day studied, the sun now and its angles, the analemma, against the
     reference point for point; the formula in the owner's axes.
  6. DAYLIGHT SAVING: Off, standard time all year; Auto, each date's own offset, the hours moving with it; undone.
  7. A PLACE TRIED: the drawing follows it, nothing saved, no undo step; back; it ends with Analyze.
  8. ONE CLOCK: a date changed, the sun's elements follow without a run; Play through the year, the date, the sun,
     the day's path and the half-year's mesh; the shadow longer in December; through the day as V170; Stop.
  9. THE WORDS: each hour beside its own dot; no word over a labelled dot; a path's name on its path.
 10. THE PANEL: the sun now, the formula, the sliders (moving without an undo step, let go with one), Back, daylight
     saving, Play's two ways, the turning points by hemisphere, the two diagrams, following the clock.
 11. THE MESH: its cells and colours against the reference's bands from the climate's own hours.
 12. A PHONE: the panel in the sheet, the sliders a finger's height, nothing spilling.

The harness never waits without a bound (V123).
"""
import asyncio, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within   # noqa: E402
import site_analysis_fixture as FX   # noqa: E402
import animation_reference as AR   # noqa: E402
import sun_reference as R   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
BLOCKERS = ('https://server.arcgisonline.com/**', 'https://tile.openstreetmap.org/**', 'https://*.tile.openstreetmap.org/**')
TOWER = [-12, -10, 12, 10, 24]
KEYS = ['path:06-21', 'path:03-20', 'path:12-21', 'today', 'now', 'angles', 'analemma', 'heat']
ZONES = [('America/New_York', '2026-01-15', '12:00'), ('America/New_York', '2026-07-15', '12:00'), ('America/New_York', '2026-03-08', '01:30'),
         ('America/New_York', '2026-03-08', '03:30'), ('America/New_York', '2026-11-01', '00:30'), ('America/New_York', '2026-11-01', '03:00'),
         ('Australia/Sydney', '2026-01-15', '12:00'), ('Australia/Sydney', '2026-07-15', '12:00'), ('Asia/Kolkata', '2026-06-01', '12:00'),
         ('America/St_Johns', '2026-07-01', '12:00'), ('Pacific/Chatham', '2026-01-15', '12:00'), ('America/Phoenix', '2026-07-15', '12:00'),
         ('Europe/Dublin', '2026-07-15', '12:00'), ('Europe/Dublin', '2026-01-15', '12:00'), ('Asia/Ho_Chi_Minh', '2026-07-15', '12:00')]
PLACES = [(40, -75, -5), (-33.87, 151.21, 10), (51.5, -0.12, 0), (1.29, 103.85, 8), (64.1, -21.9, 0), (-54.8, -68.3, -3), (35.68, 139.69, 9), (21.03, 105.85, 7)]
DATES = ['2026-01-05', '2026-03-20', '2026-06-21', '2026-10-26']
TIMES = ['06:10', '09:00', '11:45', '12:00', '15:30', '18:20']


def near(a, b, tol=1e-6):
    return a is not None and b is not None and abs(a - b) <= tol


def adiff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def dist(p, q):
    return math.sqrt(sum((p[i] - q[i]) ** 2 for i in range(len(p))))


def disp(v, dp):
    """the app's bimDispNum: fixed, its trailing zeros dropped"""
    s = ('%.' + str(dp) + 'f') % v
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return '0' if s in ('', '-', '-0') else s


def mins(t):
    h, m = t.split(':')[:2]
    return int(h) * 60 + int(m)


def polar_pt(el, az):
    r = 116 * math.tan((90 - max(0, el)) * math.pi / 360)
    return [150 + r * math.sin(az * math.pi / 180), 150 - r * math.cos(az * math.pi / 180)]


def words_date(d):
    M = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    y, m, dd = d.split('-')
    return '%d %s %s' % (int(dd), M[int(m) - 1], y)


def box_gap(b, p):
    """how far a point lies from a box [x, y, w, h]"""
    dx = max(b[0] - p[0], 0, p[0] - (b[0] + b[2]))
    dy = max(b[1] - p[1], 0, p[1] - (b[1] + b[3]))
    return math.sqrt(dx * dx + dy * dy)


def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


async def run():
    ck = CK
    FX.UTC_OFFSET = -14400   # the climate fetched on a summer day: Open-Meteo's offset is the request day's (research 5)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()

        async def page_for(vp, mobile=False):
            ctx = await browser.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=2 if mobile else 1)
            ST = {}
            for h in FX.HOSTS:
                await ctx.route(h, FX.route_handler(ST))
            for h in BLOCKERS:
                await ctx.route(h, lambda r: r.abort())
            pg = await ctx.new_page()
            pg.errs = []
            pg.on('pageerror', lambda e: pg.errs.append(str(e)))
            return ctx, pg

        ctx, page = await page_for({'width': 1440, 'height': 900})

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def state(pg=None):
            return await safe("()=>window.__a3dState()", pg=pg) or {}

        async def sun_els(pg=None):
            L = (await state(pg)).get('objs') or []
            return [o for o in L if o.get('t') == 'diag' and o['dg']['a'] == 'sun']

        async def el(k, pg=None):
            for o in await sun_els(pg):
                if o['dg']['k'] == k:
                    return o
            return None

        async def text(sel, pg=None):
            return await safe("(s)=>{var e=document.querySelector(s);return e?e.textContent.replace(/\\s+/g,' ').trim():null;}", sel, pg=pg)

        async def texts(sel, pg=None):
            return await safe("(s)=>[].map.call(document.querySelectorAll(s),function(e){return e.textContent.replace(/\\s+/g,' ').trim();})", sel, pg=pg) or []

        async def click(sel, pg=None):
            return await safe("(s)=>{var b=document.querySelector(s);if(!b)return false;b.click();return true;}", sel, pg=pg)

        async def undo_depth(pg=None):
            return await safe("()=>window.__a3dUndoDepth()", pg=pg)

        async def settings(pg=None):
            return await safe("()=>window.__a3dSunSettings()", pg=pg) or {}

        async def site(pg=None):
            return await safe("()=>window.__a3dSite()", pg=pg) or {}

        async def site_sun(pg=None):
            return (await site(pg)).get('sun') or {}

        async def paint(pg=None):
            await safe("()=>{window.__a3dRefreshProps&&window.__a3dRefreshProps();window.__a3dCamSet({});}", pg=pg)   # the app's own frame: its sync, not the suite's
            await (pg or page).wait_for_timeout(120)

        async def cam(c, pg=None):
            await safe("(c)=>window.__a3dCamSet(c)", c, pg=pg)
            await (pg or page).wait_for_timeout(250)

        async def only(keep, pg=None):
            return await safe("""(keep)=>{var D=window.__a3dDgState(),k,n=0;for(k in D.layers)if(D.layers.hasOwnProperty(k)&&k!=='root'){
              var v=keep.indexOf(k)>=0||keep.some(function(a){return k.indexOf(a+':')===0;});window.__a3dLayerSet(D.layers[k],'visible',v);n++;}
              window.__a3dLayerSet(D.layers.root,'visible',true);return n;}""", keep, pg=pg)

        async def analyze(pg=None):
            pg = pg or page
            await safe("()=>window.__a3dAnzView(true)", pg=pg)
            await pg.wait_for_timeout(300)
            if await safe("()=>!!document.querySelector('[data-saaddr]')", pg=pg):
                await pg.fill('[data-saaddr]', '1 Market Street')
                await pg.press('[data-saaddr]', 'Enter')
            else:
                await click('[data-saact="analyze"]', pg=pg)
            for _ in range(240):
                s = await safe("()=>window.__a3dSiteRunState()", pg=pg) or {}
                if not s.get('busy'):
                    return s
                await pg.wait_for_timeout(250)
            raise Stalled('the run did not end')

        async def ref_path(lat, lon, tz, date, pg=None):
            d = ((await safe("()=>window.__a3dDgState()", pg=pg)) or {}).get('runs', {}).get('sun', {}).get('dome') or {}
            north = await safe("()=>window.__a3dSite().trueNorth||0", pg=pg) or 0
            return R.day_path(lat, lon, tz, date, d.get('c', [0, 0]), d.get('y', 0), d.get('R', 30), north), d, north

        def same_pts(A, B, tol=1e-6):
            return len(A) == len(B) and all(dist(a, b) <= tol for a, b in zip(A, B))

        try:
            await within(page.goto('file://' + str(HTML)), 'goto')
            await page.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. The records")
            mk = await safe("()=>window.__acad3dV171d") or ''
            ck(all(w in mk for w in ('spa', 'dome', 'zone', 'dst', 'trial', 'yearplay', 'sync', 'heat', 'labels', 'panel', 'sliders', 'turning')), "the V171d marker (%s)" % mk)
            ck(bool(await safe("()=>window.__acad3dV171c")) and bool(await safe("()=>window.__acad3dV170")), "V171c's and V170's markers kept")
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and mv.group(1) == '171', "the version stays V171, a sub-phase's (V171b's rule)")
            ck(await safe("()=>['__a3dSunZoneOff','__a3dSunTzAt','__a3dSunStudy','__a3dSunSlide','__a3dSunVals','__a3dSunWords','__a3dAnimSunDate'].every(function(k){return typeof window[k]==='function';})"),
               "the suite's hooks")

            # ---------------------------------------------------------------------------------
            print("\n-- 2. The math")
            worst = [0, 0, None]
            for (la, lo, tz) in PLACES:
                for d in DATES:
                    for t in TIMES:
                        a = await safe("(a)=>window.__a3dSunCalc(a[0],a[1],a[2],a[3],a[4])", [la, lo, tz, d, t])
                        r = R.noaa(la, lo, tz, d, mins(t))
                        e = abs(a['elevation'] - r['elevation']) if a else 99
                        z = adiff(a['azimuth'], r['azimuth']) if a else 99
                        if e > worst[0] or z > worst[1]:
                            worst = [max(e, worst[0]), max(z, worst[1]), (la, lo, d, t)]
            ck(worst[0] < 1e-6 and worst[1] < 1e-6, "NOAA's spreadsheet, column by column in Python, at 8 places, 4 dates and 6 times: the app's altitude and azimuth within 1e-6 deg (%.2g, %.2g)" % (worst[0], worst[1]))
            a0 = await safe("(a)=>window.__a3dSunCalc(a[0],a[1],a[2],a[3],'12:30')", [R.SPA['lat'], R.SPA['lon'], R.SPA['tz'], R.SPA['date']])
            a1 = await safe("(a)=>window.__a3dSunCalc(a[0],a[1],a[2],a[3],'12:31')", [R.SPA['lat'], R.SPA['lon'], R.SPA['tz'], R.SPA['date']])
            g = (a0['geomElevation'] + a1['geomElevation']) / 2
            e = (a0['elevation'] + a1['elevation']) / 2
            z = (a0['azimuth'] + a1['azimuth']) / 2
            ck(abs(g - R.SPA['e0']) < 0.0005 and abs(e - R.SPA['e']) < 0.005 and abs(z - R.SPA['az']) < 0.005,
               "NREL SPA's example, 12:30:30: altitude %.5f against %.5f (no refraction), %.4f against %.4f, azimuth %.4f against %.4f" % (g, R.SPA['e0'], e, R.SPA['e'], z, R.SPA['az']))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. The zones")
            bad = []
            for (zn, d, t) in ZONES:
                got = await safe("(a)=>window.__a3dSunZoneOff(a[0],a[1],a[2])", [zn, d, t])
                if got is None or abs(got - R.zone_off(zn, d, t)) > 1e-9:
                    bad.append((zn, d, t, got, R.zone_off(zn, d, t)))
            ck(not bad, "fifteen offsets against Python's own time zone database, New York either side of its two changes, half and three-quarter hours (%s)" % bad[:2])
            ck(await safe("()=>window.__a3dSunZoneOff('Nope/Zone','2026-01-15','12:00')") is None, "a zone the browser does not know: none")
            sb = [(zn, await safe("(a)=>window.__a3dSunZoneStd(a[0],2026)", [zn]), R.zone_std(zn, 2026)) for zn in ('America/New_York', 'Australia/Sydney', 'Europe/Dublin', 'America/St_Johns', 'Asia/Kolkata')]
            ck(all(near(x[1], x[2], 1e-9) for x in sb), "standard time, the lower of mid-January's and mid-July's (%s)" % sb)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. The climate's offset")
            await safe("""(a)=>{var x0=a[0],z0=a[1],x1=a[2],z1=a[3],h=a[4];return window.__a3dPushTestObj({id:'TOWER',t:'solid',name:'Tower',pos:[0,0,0],layer:'layer-0',
              mesh:{v:[[x0,0,z0],[x1,0,z0],[x1,0,z1],[x0,0,z1],[x0,h,z0],[x1,h,z0],[x1,h,z1],[x0,h,z1]],f:[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]}});}""", TOWER)
            await analyze()
            ss = await site_sun()
            C = (await site()).get('climate') or {}
            ck(C.get('tz') == -4 and ss.get('zone') == 'America/New_York' and ss.get('tz') == -5 and ss.get('tzAuto') is True,
               "fetched on a summer day (UTC-4 for every hour, as Open-Meteo answers): the zone kept and its standard time, UTC-5 (%s, %s)" % (C.get('tz'), {k: ss.get(k) for k in ('tz', 'zone', 'tzAuto')}))
            z0 = await safe("()=>window.__a3dSunZone()") or {}
            ck(z0.get('zone') == 'America/New_York' and z0.get('dst') is False, "daylight saving Off at first: standard time all year, as Ladybug draws (%s)" % z0)
            await safe("()=>{window.__a3dAwLeave();window.__a3dSelectFor&&window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(200)
            loc = await safe("""()=>{var s=document.querySelector('[data-propmodel="sundst"]');var t=[].filter.call(document.querySelectorAll('#a3d-propsbody .a3d-prop-row,#a3d-propsbody [class*="row"]'),function(r){return /Time Zone/.test(r.textContent);})[0];
              return {sel:!!s,val:s?s.value:null,opts:s?[].map.call(s.options,function(o){return o.value;}):[],zone:t?t.textContent:''};}""") or {}
            ck(loc.get('sel') and loc.get('val') == '' and loc.get('opts') == ['', 'auto'] and 'America/New_York' in loc.get('zone', ''),
               "Properties > Site > Location: the time zone, and Daylight Saving, Off or Auto (%s)" % loc)
            u0 = await undo_depth()
            await safe("()=>window.__a3dSetSun('tz','-6')")
            ck((await site_sun()).get('tz') == -6 and 'tzAuto' not in (await site_sun()), "an offset typed is the owner's")
            await analyze()
            ck((await site_sun()).get('tz') == -6, "and Analyze site again keeps it")
            await safe("()=>window.__a3dSetSun('tz','-5')")
            await safe("()=>window.__a3dAwFocus('sun')")
            await only(['sun'])
            await paint()

            # ---------------------------------------------------------------------------------
            print("\n-- 5. The dome")
            E = await sun_els()
            ck([o['dg']['k'] for o in E] == KEYS, "the sun's elements: three paths, the day studied, the sun now, its angles, the analemma, the temperature (%s)" % [o['dg']['k'] for o in E])
            st = await settings()
            YR = st['date'][:4]
            okp, D, north = [], None, 0
            for md in ('06-21', '03-20', '12-21'):
                (pts, marks), D, north = await ref_path(40, -75, -5, YR + '-' + md)
                o = await el('path:' + md)
                okp.append(same_pts(o['dg']['g']['pts'], pts) and [m['t'] for m in o['dg']['g']['marks']] == ['%dh' % h for h, _ in marks] and
                           all(dist(m['p'], p) < 1e-6 for m, (_, p) in zip(o['dg']['g']['marks'], marks)))
            ck(all(okp), "the solstices' and the equinox's paths point for point, every 10 minutes the sun is up, a dot an hour (%s)" % okp)
            ck(all(abs(dist(p, [D['c'][0], D['y'], D['c'][1]]) - D['R']) < 1e-9 for o in E[:3] for p in o['dg']['g']['pts']), "each point R from the site's centre (R %s m)" % D.get('R'))
            o = await el('path:06-21')
            rows = {r[0]: r[1] for r in o['dg']['info']['rows']}
            r6 = R.noaa(40, -75, -5, YR + '-06-21', 720)
            ck(rows.get('Sunrise', '').startswith(R.hhmm(r6['sunrise'])) and 'UTC−5, America/New_York' in rows.get('Clock', ''), "its sunrise, and its clock (%s)" % rows)
            nw = await el('now')
            rn = R.noaa(40, -75, -5, st['date'], mins(st['time']))
            q = R.dome(D['c'], D['y'], D['R'], rn['azimuth'], rn['elevation'], north)
            ck(nw['dg']['sym'] and dist(nw['dg']['sym']['p'], q) < 1e-6 and dist(nw['dg']['g']['pts'][1], q) < 1e-6, "the sun now on the dome, its ray from the centre")
            vals = await safe("()=>window.__a3dSunVals()") or {}
            ox = R.owner_xyz(D['R'], rn['azimuth'], rn['elevation'])
            ck(vals.get('xyz') == 'X %s, Y %s, Z %s m' % (disp(ox[0], 2), disp(ox[1], 2), disp(ox[2], 2)), "in the owner's axes, X = R cos(alt) sin(az), Y = R sin(alt), Z = R cos(alt) cos(az): %s" % vals.get('xyz'))
            an = await el('angles')
            lbs = [l['t'] for l in an['dg']['lb']]
            ck(len(an['dg']['g']['lines']) == 5 and lbs == ['A %s°' % disp(rn['azimuth'], 1), 'α %s°' % disp(rn['elevation'], 1)],
               "its angles: north, the bearing, the drop, the azimuth's arc and the altitude's, named (%s)" % lbs)
            al = await el('analemma')
            n_ref = sum(1 for d in range(0, 366, 2) if R.noaa(40, -75, -5, (R.datetime.date(int(YR), 1, 1) + R.datetime.timedelta(days=d)).isoformat(), mins(st['time']))['elevation'] > 0
                        and (R.datetime.date(int(YR), 1, 1) + R.datetime.timedelta(days=d)).year == int(YR))
            ck(sum(len(L) for L in al['dg']['g']['lines']) == n_ref, "the analemma: the sun at %s every second day, %d points" % (st['time'], n_ref))
            td = await el('today')
            ck(td and td['dg']['g']['pts'] == [] and R.near_drawn(st['date']), "the day studied, %s, is the June solstice's: not drawn twice" % st['date'])

            # ---------------------------------------------------------------------------------
            print("\n-- 6. Daylight saving")
            u1 = await undo_depth()
            await safe("""()=>{var s=document.querySelector('[data-propmodel="sundst"]');window.__a3dAwLeave();window.__a3dRefreshProps();}""")
            await page.wait_for_timeout(150)
            await safe("""()=>{var s=document.querySelector('[data-propmodel="sundst"]');s.value='auto';s.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(150)
            await paint()
            ck((await site_sun()).get('dst') == 'auto' and await undo_depth() == u1 + 1, "Auto from Properties: one undo step")
            ok6 = []
            for md, tz in (('06-21', -4), ('12-21', -5)):
                (pts, marks), D, north = await ref_path(40, -75, R.zone_off('America/New_York', YR + '-' + md), YR + '-' + md)
                o = await el('path:' + md)
                ok6.append(tz == R.zone_off('America/New_York', YR + '-' + md) and all(dist(m['p'], p) < 1e-6 for m, (_, p) in zip(o['dg']['g']['marks'], marks)) and
                           ('daylight saving time' if tz == -4 else 'standard time') in json.dumps(o['dg']['info'], ensure_ascii=False))
            ck(all(ok6), "June's hours at UTC-4, daylight saving time; December's at UTC-5, standard time; without a run (%s)" % ok6)
            await safe("()=>window.__a3dSetSun('date','" + YR + "-07-15')")
            await paint()
            nw = await el('now')
            rn = R.noaa(40, -75, -4, YR + '-07-15', 720)
            ck(dist(nw['dg']['sym']['p'], R.dome(D['c'], D['y'], D['R'], rn['azimuth'], rn['elevation'], north)) < 1e-6, "the sun at 12:00 on 15 July by daylight saving time")
            await safe("()=>window.__a3dUndo()")
            await safe("()=>window.__a3dUndo()")
            await paint()
            (pts, marks), D, north = await ref_path(40, -75, -5, YR + '-06-21')
            o = await el('path:06-21')
            ck('dst' not in (await site_sun()) and all(dist(m['p'], p) < 1e-6 for m, (_, p) in zip(o['dg']['g']['marks'], marks)), "undone: Off, June's hours by standard time again")

            # ---------------------------------------------------------------------------------
            print("\n-- 7. A place tried")
            await safe("()=>window.__a3dAwFocus('sun')")
            u2 = await undo_depth()
            sv0 = json.dumps(await site_sun(), sort_keys=True)
            await safe("()=>window.__a3dSunSlide('lat','60',false)")
            await paint()
            (pts, marks), D, north = await ref_path(60, -75, -5, YR + '-06-21')
            o = await el('path:06-21')
            stt = await safe("()=>window.__a3dSunStudy()") or {}
            ck(stt.get('lat') == 60 and stt.get('trial') is True and same_pts(o['dg']['g']['pts'], pts), "60 deg north tried: June's path follows it, point for point")
            ck(json.dumps(await site_sun(), sort_keys=True) == sv0 and await undo_depth() == u2, "nothing saved, no undo step")
            ck((await el('heat'))['dg']['g']['quads'] == [] and 'site' in json.dumps((await el('heat'))['dg']['info']), "the temperature not drawn: the climate is the site's")
            await safe("()=>window.__a3dSunSlide('lat','60',true)")
            await page.wait_for_timeout(150)
            ck('Trying 60' in (await text('.a3d-sun-trial') or ''), "let go: the panel says it is a place tried")
            await click('[data-awact="sun:back"]')
            await paint()
            (pts, marks), D, north = await ref_path(40, -75, -5, YR + '-06-21')
            ck(same_pts((await el('path:06-21'))['dg']['g']['pts'], pts) and not await safe("()=>!!document.querySelector('.a3d-sun-trial')") and len((await el('heat'))['dg']['g']['quads']) > 0,
               "Back to the site's place: its paths and its temperature again")
            await safe("()=>window.__a3dSunSlide('lon','10',true)")
            await safe("()=>window.__a3dAwLeave()")
            x = await safe("()=>window.__a3dSunX()") or {}
            ck(x.get('lat') is None and x.get('lon') is None, "leaving Analyze ends a place tried")
            await safe("()=>window.__a3dAwFocus('sun')")

            # ---------------------------------------------------------------------------------
            print("\n-- 8. One clock")
            run0 = ((await safe("()=>window.__a3dDgState()")) or {}).get('runs', {}).get('sun', {}).get('date')
            u3 = await undo_depth()
            await safe("()=>window.__a3dSetSun('date','" + YR + "-10-26')")
            await safe("()=>window.__a3dSetSun('time','15:30')")
            await paint()
            (pts, marks), D, north = await ref_path(40, -75, -5, YR + '-10-26')
            td = await el('today')
            nw = await el('now')
            rn = R.noaa(40, -75, -5, YR + '-10-26', 930)
            ck(same_pts(td['dg']['g']['pts'], pts) and dist(nw['dg']['sym']['p'], R.dome(D['c'], D['y'], D['R'], rn['azimuth'], rn['elevation'], north)) < 1e-6 and nw['dg']['lb'][0]['t'] == '15:30',
               "the date and time changed: the day's own path and the sun follow, with no run (%s)" % run0)
            ck(await undo_depth() == u3 + 2 and ((await safe("()=>window.__a3dDgState()")) or {}).get('runs', {}).get('sun', {}).get('date') == run0, "the two changes the only undo steps")
            # an element the owner coloured keeps its colour and follows
            dj = await el('path:12-21')
            await safe("(id)=>window.__a3dDgSet(id,'stroke','#00ff00')", dj['id'])
            await safe("()=>window.__a3dSunSlide('lat','45',false)")
            await paint()
            (pts, marks), D, north = await ref_path(45, -75, -5, YR + '-12-21')
            dj2 = await el('path:12-21')
            ck(dj2['dg']['s'].get('stroke') == '#00ff00' and same_pts(dj2['dg']['g']['pts'], pts), "a path the owner coloured keeps its colour and follows the sun")
            await safe("()=>window.__a3dSunBack()")
            # through the year
            await safe("()=>window.__a3dSunModeSet('year')")
            yb = []
            for t in (0, 5, 16.96, 18, 30, 35.95, 36.6):
                a = await safe("(t)=>window.__a3dAnimAt(t,0)", t) or {}
                stt = await safe("()=>window.__a3dSunStudy()") or {}
                want = R.year_date(t, int(YR))
                rn = R.noaa(40, -75, -5, want, 930)
                nw = await el('now')
                td = await el('today')
                ht = await el('heat')
                hrow = {r[0]: r[1] for r in ht['dg']['info']['rows']}
                (pts, _), D, north = await ref_path(40, -75, -5, want)
                good = (stt.get('date') == want and stt.get('time') == '15:30' and a.get('sunTime') == '15:30' and
                        (nw['dg']['sym'] is None if rn['elevation'] <= 0 else dist(nw['dg']['sym']['p'], R.dome(D['c'], D['y'], D['R'], rn['azimuth'], rn['elevation'], north)) < 1e-6) and
                        (td['dg']['g']['pts'] == [] if R.near_drawn(want) else same_pts(td['dg']['g']['pts'], pts)) and
                        hrow.get('Half-year', '').startswith('21 June' if R.half(want) == 'jd' else '21 December'))
                if not good:
                    yb.append((t, stt.get('date'), want))
            ck(not yb, "Play through the year: the date a day a step, 36 s for the year, held at its end; the sun at 15:30, the day's path, the mesh's half-year turning at the solstices (%s)" % yb[:2])
            # the shadow follows the date: longer in December than in June
            await only(['shadow'])
            await cam({'yaw': 0, 'pitch': 1.52, 'dist': 160, 'tx': 0, 'ty': 0, 'tz': 0})
            await safe("()=>window.__a3dSetSun('time','12:00')")

            async def shade(t):
                await safe("(t)=>window.__a3dAnimAt(t,0)", t)
                await page.wait_for_timeout(150)
                return await safe("""()=>{var c=document.getElementById('a3d-canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,n=0,i;for(i=3;i<d.length;i+=16)if(d[i]>40)n++;return n;}""")
            sj, sd = await shade(16.96), await shade(34.93)
            ck(sj and sd and sd > sj * 1.6, "the model's shadow follows the date: at noon on %s it covers %s px, on %s %s px" % (R.year_date(16.96, int(YR)), sj, R.year_date(34.93, int(YR)), sd))
            await safe("()=>window.__a3dSunModeSet('day')")
            day = await safe("()=>window.__a3dSunCalc(40,-75,-5,'%s-10-26','12:00')" % YR)
            dt = []
            for t in (0, 6, 12, 24.5):
                a = await safe("(t)=>window.__a3dAnimAt(t,0)", t) or {}
                stt = await safe("()=>window.__a3dSunStudy()") or {}
                if a.get('sunTime') != AR.sun_time(t, day) or stt.get('date') != YR + '-10-26':
                    dt.append((t, a.get('sunTime'), AR.sun_time(t, day)))
            ck(not dt, "through the day as V170: sunrise to sunset of the day studied (%s)" % dt[:2])
            await safe("()=>window.__a3dAnimStop()")
            await only(['sun'])
            await paint()
            a = await safe("()=>window.__a3dAnim()") or {}
            nw = await el('now')
            rn = R.noaa(40, -75, -5, YR + '-10-26', 720)
            ck(not a.get('on') and not a.get('paused') and dist(nw['dg']['sym']['p'], R.dome(D['c'], D['y'], D['R'], rn['azimuth'], rn['elevation'], north)) < 1e-6,
               "Stop: the sun back at the study's own moment")

            # ---------------------------------------------------------------------------------
            print("\n-- 9. The words")
            await safe("()=>window.__a3dSetSun('date','" + YR + "-06-21')")
            far = []
            named = set()
            for view in ({'yaw': 0.5, 'pitch': 0.45, 'dist': 120, 'tx': 0, 'ty': 8, 'tz': 0}, {'yaw': 0, 'pitch': 1.52, 'dist': 120, 'tx': 0, 'ty': 0, 'tz': 0}):
                await cam(view)
                await paint()
                W = await safe("()=>window.__a3dSunWords()") or []
                dots = await safe("()=>window.__a3dSunDots()") or {}
                ids = {o['id']: o['dg']['k'] for o in await sun_els()}
                keep = [[p[0] - 5, p[1] - 5, 10, 10] for i, k in ids.items() if k.startswith('path:') or k == 'today' for p in dots.get(i, [])]   # the labelled dots, from what was drawn
                for w in W:
                    if w['id'] not in ids:
                        continue
                    if re.match(r'^\d+h$', w['t']):
                        gap = min([box_gap(w['b'], p) for p in dots.get(w['id'], [])] or [99])
                        if gap > 14:
                            far.append((view['pitch'], w['t'], round(gap, 1)))
                    if w['t'] in ('21 June', '20 Mar, 22 Sep', '21 December'):
                        named.add(w['t'])
                over = [w['t'] for w in W for k in keep if overlap(w['b'], k)]
                ck(not over, "no word over a labelled dot (%s, %d words): %s" % ('plan' if view['pitch'] > 1 else '3D', len(W), over[:3]))
            ck(not far, "each hour's word beside its own dot, never a line away, in 3D and in plan (%s)" % far[:3])
            ck(named, "a path's name on its path where there is room between its hours (%s)" % sorted(named))

            # ---------------------------------------------------------------------------------
            print("\n-- 10. The panel")
            await safe("()=>window.__a3dAwFocus('sun')")
            await page.wait_for_timeout(200)
            st = await settings()
            rn = R.noaa(40, -75, -5, st['date'], mins(st['time']))
            rowv = await safe("()=>{var o={};[].forEach.call(document.querySelectorAll('[data-sunv]'),function(e){o[e.getAttribute('data-sunv')]=e.textContent;});return o;}") or {}
            ck(rowv.get('place') == '40° N, 75° W' and rowv.get('day') == words_date(st['date']) and rowv.get('time') == st['time'] + ' (UTC−5, America/New_York)' and
               rowv.get('alt') == disp(rn['elevation'], 2) + '°' and rowv.get('az') == disp(rn['azimuth'], 2) + '° from true north',
               "the sun now: the place, the day, the time with its offset and zone, the altitude and azimuth (%s)" % {k: rowv.get(k) for k in ('time', 'alt', 'az')})
            ck('X = R cos α sin A, Y = R sin α, Z = R cos α cos A' in (await text('.a3d-sun-f') or ''), "the formula, in the owner's axes")
            sl = await safe("()=>[].map.call(document.querySelectorAll('[data-sunsl]'),function(s){return [s.getAttribute('data-sunsl'),s.min,s.max,s.step,s.value];})") or []
            ck([s[0] for s in sl] == ['lat', 'lon', 'date', 'time'] and sl[0][1:4] == ['-89.9', '89.9', '0.1'] and sl[3][1:] == ['0', '1435', '5', str(mins(st['time']))],
               "four sliders: latitude, longitude, date and time (%s)" % sl)
            u4 = await undo_depth()
            mv = await safe("""()=>{var s=document.querySelector('[data-sunsl="time"]');document.querySelector('[data-sunpanel]').setAttribute('data-t171d','1');
              s.value='840';s.dispatchEvent(new Event('input',{bubbles:true}));return 1;}""")
            await page.wait_for_timeout(250)
            # a redraw (the panel's morph) would drop the mark it does not write
            mv = await safe("""()=>({same:document.querySelector('[data-sunpanel]').getAttribute('data-t171d')==='1',out:document.querySelector('[data-sunout="time"]').textContent,
              row:document.querySelector('[data-sunv="time"]').textContent})""") or {}
            ck(mv.get('same') and mv.get('out') == '14:00' and mv.get('row', '').startswith('14:00') and (await safe("()=>window.__a3dSunStudy()") or {}).get('time') == '14:00'
               and (await settings()).get('time') == st['time'] and await undo_depth() == u4, "the time slider moving: the sun and the numbers follow, the panel not drawn again, no undo step (%s)" % mv)
            await safe("""()=>{var s=document.querySelector('[data-sunsl="time"]');s.focus();s.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(200)
            ck((await settings()).get('time') == '14:00' and await undo_depth() == u4 + 1 and await safe("()=>document.activeElement&&document.activeElement.getAttribute('data-sunsl')") == 'time',
               "let go: the study's time, one undo step, the slider still in the hand")
            await safe("""()=>{var s=document.querySelector('[data-sunsl="date"]');s.value='80';s.dispatchEvent(new Event('input',{bubbles:true}));s.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(200)
            ck((await settings()).get('date') == YR + '-03-21' and await undo_depth() == u4 + 2, "the date slider: the 80th day, 21 March")
            await safe("""()=>{var s=document.querySelector('[data-sunsl="lat"]');s.value='-33.9';s.dispatchEvent(new Event('input',{bubbles:true}));s.dispatchEvent(new Event('change',{bubbles:true}));}""")
            await page.wait_for_timeout(200)
            tp = await safe("()=>[].map.call(document.querySelectorAll('[data-sunturn]'),function(c){return [c.getAttribute('data-sunturn'),c.querySelector('b').textContent];})") or []
            ck(tp == [['12-21', 'Summer solstice'], ['03-20', 'Equinoxes'], ['06-21', 'Winter solstice']] and await undo_depth() == u4 + 2,
               "33.9 deg south tried: the summer solstice is December's, first; no undo step (%s)" % tp)
            await click('[data-awact="sun:back"]')
            await page.wait_for_timeout(150)
            tp = await safe("""()=>[].map.call(document.querySelectorAll('[data-sunturn]'),function(c){var o={k:c.getAttribute('data-sunturn'),n:c.querySelector('b').textContent};
              [].forEach.call(c.querySelectorAll('.a3d-awp-r'),function(r){o[r.querySelector('span').textContent]=r.querySelector('b').textContent;});return o;})""") or []
            okt = []
            for c in tp:
                f = R.noaa(40, -75, -5, YR + '-' + c['k'], 720)
                hi = R.noaa(40, -75, -5, YR + '-' + c['k'], round(f['noon']))
                sh = 10 / math.tan(hi['elevation'] * math.pi / 180)
                rz = R.noaa(40, -75, -5, YR + '-' + c['k'], round(f['sunrise']))['azimuth']
                okt.append(c.get('Sunrise') == '%s at %s°' % (R.hhmm(f['sunrise']), disp(rz, 0)) and c.get('Noon', '').startswith(disp(hi['elevation'], 1) + '° up') and
                           c.get('A 10 m building') == 'casts %s m at noon' % disp(sh, 1))
            ck([c['n'] for c in tp] == ['Summer solstice', 'Equinoxes', 'Winter solstice'] and all(okt), "back north: the summer solstice, the equinoxes, the winter solstice, each with sunrise and its bearing, noon, a 10 m building's shadow (%s)" % okt)
            u5 = await undo_depth()
            await click('[data-awact="sun:dst"]')
            await page.wait_for_timeout(150)
            p1 = await safe("()=>document.querySelector('[data-awact=\"sun:dst\"]').getAttribute('aria-pressed')")
            await click('[data-awact="sun:dst"]')
            await page.wait_for_timeout(150)
            ck(p1 == 'true' and await undo_depth() == u5 + 2 and 'dst' not in (await site_sun()), "daylight saving from the panel: Auto, then Off, one undo step each")
            await click('[data-awact="sun:mode:year"]')
            await page.wait_for_timeout(150)
            md = await safe("()=>[].map.call(document.querySelectorAll('[data-awact^=\"sun:mode:\"]'),function(b){return b.getAttribute('aria-pressed');})")
            ck(await safe("()=>window.__a3dSunMode()") == 'year' and md == ['false', 'true'], "Play through the year chosen, pressed (%s)" % md)
            st = await settings()
            pv = await safe("()=>{var c=document.querySelector('[data-sunnow=\"polar\"]'),h=document.querySelector('[data-sunnow=\"height\"]');return [+c.getAttribute('cx'),+c.getAttribute('cy'),+h.getAttribute('cx'),+h.getAttribute('cy')];}") or [0, 0, 0, 0]
            rn = R.noaa(40, -75, -5, st['date'], mins(st['time']))
            pp = polar_pt(rn['elevation'], rn['azimuth'])
            ck(abs(pv[0] - pp[0]) < 0.11 and abs(pv[1] - pp[1]) < 0.11 and abs(pv[2] - (34 + 258 * mins(st['time']) / 1440)) < 0.11 and abs(pv[3] - (146 - 136 * rn['elevation'] / 90)) < 0.11,
               "the two diagrams: the sun now on the sky dome in plan and on the day's height (%s)" % pv)
            await safe("(t)=>window.__a3dAnimAt(t,0)", 30)
            await page.wait_for_timeout(150)
            want = R.year_date(30, int(YR))
            lv = await safe("()=>({day:document.querySelector('[data-sunv=\"day\"]').textContent,poly:[].map.call(document.querySelectorAll('[data-sunpolar] [data-sunday]'),function(p){return p.getAttribute('data-sunday');})})") or {}
            ck(lv.get('day') == words_date(want) and (want in lv.get('poly', []) or R.near_drawn(want)), "playing, the panel follows the clock: %s, its path in the diagram (%s)" % (want, lv))
            await safe("()=>window.__a3dAnimStop()")
            await safe("()=>window.__a3dSunModeSet('day')")
            ck(len(await texts('.a3d-sun-heat .a3d-awp-keyi')) == 11, "the temperature's eleven bands, as the climate board's")

            # ---------------------------------------------------------------------------------
            print("\n-- 11. The mesh")
            await paint()
            C = (await site())['climate']
            Hh = C['hourly']
            st = await settings()
            hf = R.half(st['date'])
            rows = R.ROWS[hf]
            band = R.heat_bands(Hh['heat'], Hh['start'], rows)
            ht = await el('heat')
            Q = ht['dg']['g']['quads']
            (pts, _), D, north = await ref_path(40, -75, -5, st['date'])
            V = []
            for j in range(len(rows)):
                V.append([])
                for c in range(73):
                    s = R.noaa(40, -75, C['tz'], YR + '-' + rows[j], c * 20)
                    V[j].append(R.dome(D['c'], D['y'], D['R'], s['azimuth'], s['elevation'], north) if s['elevation'] > 0 else None)
            ref = {}
            for j in range(len(rows) - 1):
                for c in range(72):
                    v = band[j][c // 3]
                    if V[j][c] and V[j][c + 1] and V[j + 1][c + 1] and V[j + 1][c] and v is not None:
                        ref[(j, c // 3, c % 3)] = (R.heat_col(v), [V[j][c], V[j][c + 1], V[j + 1][c + 1], V[j + 1][c]], v)
            got = {(q['r'], q['h'], q['k']): q for q in Q}
            bad = [k for k in ref if k not in got or got[k]['c'] != ref[k][0] or abs(got[k]['v'] - ref[k][2]) > 0.0501 or
                   any(dist(a, b) > 2e-3 for a, b in zip(got[k]['p'], ref[k][1]))]
            ck(len(Q) == len(ref) and not bad, "the half-year %s: %d cells of 20 minutes by a month, each its band's mean at its hour, in the board's colours, its corners the sun's places by the climate's own clock (%s)" %
               (hf, len(ref), bad[:3]))
            h_at = await safe("()=>window.__a3dSunHeatAt()")
            # the moment's band and hour in the climate's clock (UTC-4 here), the study at UTC-5
            hh = (mins(st['time']) // 60 + int(C['tz'] - (-5))) % 24
            md5 = st['date'][5:]
            jj = [j for j in range(len(rows) - 1) if (rows[j] <= md5 < rows[j + 1]) if rows[j] < rows[j + 1]] or [j for j in range(len(rows) - 1) if rows[j] > rows[j + 1] and (md5 >= rows[j] or md5 < rows[j + 1])]
            ck(h_at and jj and h_at.get('h') == hh and abs(h_at.get('v') - band[jj[0]][hh]) < 1e-9, "where the sun is now: its band's mean at the climate's hour %s (an hour on from the study's standard time): %s" % (hh, h_at and round(h_at.get('v'), 2)))

            # ---------------------------------------------------------------------------------
            print("\n-- 12. A phone")
            ctx2, pg2 = await page_for({'width': 390, 'height': 844}, mobile=True)
            await within(pg2.goto('file://' + str(HTML)), 'goto')
            await pg2.wait_for_timeout(2300)
            await safe("()=>window.__a3dEnter()", pg=pg2)
            await analyze(pg2)
            await safe("()=>window.__a3dAwFocus('sun')", pg=pg2)
            await click('#a3d-awbar [data-awact="panel"]', pg=pg2)
            await pg2.wait_for_timeout(300)
            ph = await safe("""()=>{var b=document.getElementById('a3d-propsbody'),s=[].map.call(document.querySelectorAll('[data-sunsl]'),function(e){return Math.round(e.getBoundingClientRect().height);});
              return {sl:s,spill:b?b.scrollWidth-b.clientWidth:-1,panel:!!document.querySelector('[data-sunpanel]')};}""", pg=pg2) or {}
            ck(ph.get('panel') and len(ph.get('sl', [])) == 4 and min(ph['sl']) >= 36 and ph.get('spill', 1) <= 0, "the sun's panel in the sheet, its sliders a finger's height, nothing spilling (%s)" % ph)
            ck(not pg2.errs, "no page errors on the phone (%s)" % pg2.errs[:2])
            await ctx2.close()

            ck(not page.errs, "no page errors (%s)" % page.errs[:3])
        except Stalled as s:
            ck(False, 'the suite stalled: %s' % s)
        except Exception:
            traceback.print_exc()
            ck(False, 'the suite raised')
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
