#!/usr/bin/env python3
"""bim_phase107_sun_shadow_browser_tests.py -- V107: sun position, shadows on the ground, sun path.

Asserted on the model against an independent source:
  1. SUN POSITION (NOAA equations) against NREL SPA, computed with pvlib 0.15.2 and written in
     below: six places and times, both hemispheres, the equator near the zenith, and the midnight
     sun at Tromso. Elevation within 0.02 deg, azimuth within 0.02 deg (0.1 near the zenith, where
     azimuth is ill-conditioned), sunrise, sunset and solar noon within one minute.
  2. SITE SETTINGS are typed into Properties -- driven -- refused out of range, undoable, kept
     through a reload; with none set, the sun study says what is missing instead of drawing.
  3. A SHADOW falls where the reference sun puts it: the top of a 3 m column at 13:00 EDT on
     2024-06-20 in Harrisburg lands 3 / tan(73.0558 deg) = 0.914 m from its base, away from the
     sun; turning True North 90 degrees turns the shadow with it. A ground slab casts nothing.
  4. AT NIGHT there is no shadow, and the study says the sun is down.
  5. THE SUN PATH peaks at 90 - |lat - 23.44| on June 21 and 90 - lat - 23.44 on December 21, marks
     the sun now, and is turned to the plan's true north.
  6. SUNSTUDY runs from the command palette, and a second run hides it all.
"""
import asyncio, math, pathlib, sys
from playwright.async_api import async_playwright

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'

# NREL SPA via pvlib.solarposition.spa_python / sun_rise_set_transit_spa (pressure 101325 Pa,
# 12 C): apparent elevation, azimuth, then sunrise, sunset, transit in local minutes.
SPA = [
    ((40.2732, -76.8867, -4, '2024-06-20', '13:00'), (73.0558, 172.6665, 337.8833, 1240.4667, 789.2833)),
    ((40.2732, -76.8867, -5, '2024-12-21', '10:30'), (22.5256, 156.2008, 446.95, 1004.9333, 725.9333)),
    ((-33.8688, 151.2093, 10, '2024-06-21', '12:00'), (32.7128, 359.1809, 420.05, 1013.7167, 716.7667)),
    ((69.6492, 18.9553, 2, '2024-06-21', '00:00'), (3.6602, 349.4467, None, None, 765.8667)),
    ((-0.1807, -78.4678, -5, '2024-03-20', '12:15'), (88.4167, 74.8602, 377.85, 1104.3667, 741.1)),
    ((40.2732, -76.8867, -5, '2024-02-11', '15:45'), (18.2077, 232.3341, 426.2667, 1057.7333, 741.7333)),
]


class Checks:
    def __init__(self):
        self.n, self.bad = 0, []

    def __call__(self, cond, msg):
        self.n += 1
        if not cond:
            self.bad.append(msg)
        print(('ok    ' if cond else 'FAIL  ') + msg)


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def adiff(a, b):
    return abs((a - b + 180) % 360 - 180)


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

        async def safe(js, arg=None):
            try:
                return await (page.evaluate(js, arg) if arg is not None else page.evaluate(js))
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:140])
                return None

        async def blur():
            await safe("()=>{if(document.activeElement)document.activeElement.blur();}")

        async def model_props():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dRefreshProps();}")
            await page.wait_for_timeout(80)

        async def set_field(key, v):
            await model_props()
            try:
                loc = page.locator('input[data-propmodel="%s"]' % key)
                await loc.fill(v, timeout=3000)
                await loc.press('Enter', timeout=3000)
                await page.wait_for_timeout(150)
            except Exception as e:
                print('      (driving %s failed: %s)' % (key, str(e)[:120]))

        async def paint():
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dTestPaint();}")

        print('\n-- 1. NOAA against NREL SPA')
        ok_el, ok_az, ok_t = True, True, True
        for (lat, lon, tz, d, t), (el, az, rise, sset, noon) in SPA:
            r = (await safe("(a)=>window.__a3dSunCalc(a[0],a[1],a[2],a[3],a[4])", [lat, lon, tz, d, t])) or {}
            if not (num(r.get('elevation')) and abs(r['elevation'] - el) <= 0.02):
                ok_el = False
                print('      el %s %s: %s vs %s' % (d, t, r.get('elevation'), el))
            if not (num(r.get('azimuth')) and adiff(r['azimuth'], az) <= (0.1 if el > 85 else 0.02)):
                ok_az = False
                print('      az %s %s: %s vs %s' % (d, t, r.get('azimuth'), az))
            for key, ref in (('sunrise', rise), ('sunset', sset), ('noon', noon)):
                got = r.get(key)
                if (ref is None and got is not None) or (ref is not None and not (num(got) and abs(got - ref) <= 1.0)):
                    ok_t = False
                    print('      %s %s %s: %s vs %s' % (key, d, t, got, ref))
        ck(ok_el, 'elevation within 0.02 deg of SPA at all six')
        ck(ok_az, 'azimuth within 0.02 deg of SPA (0.1 near the zenith)')
        ck(ok_t, 'sunrise, sunset and solar noon within a minute; none at Tromso in June')
        tro = (await safe("()=>window.__a3dSunCalc(69.6492,18.9553,2,'2024-06-21','00:00')")) or {}
        ck(tro.get('polar') == 'day' and tro.get('elevation', 0) > 0, 'the midnight sun is up at midnight and reported as polar day')

        print('\n-- 2. site settings in Properties')
        col = await safe("()=>window.__a3dColumnAt([10,10],0,0.4,0.4,3)")
        await safe("()=>{window.__a3dFit();window.__a3dFlat(true);}")   # fit an EMPTY model goes to the 3D home view
        await blur()
        await palette_run(page, 'SUNSTUDY')
        await paint()
        info = (await safe("()=>window.__a3dShadowInfo()")) or {}
        ck(info.get('missing') == ['latitude', 'longitude', 'UTC offset'], 'with no site set, the study names what is missing and draws nothing (%s)' % info)
        for key, v in (('sunlat', '40.2732'), ('sunlon', '-76.8867'), ('suntz', '-4'), ('sundate', '2024-06-20'), ('suntime', '13:00')):
            await set_field(key, v)
        st = (await safe("()=>window.__a3dSunSettings()")) or {}
        ck(st.get('lat') == 40.2732 and st.get('lon') == -76.8867 and st.get('tz') == -4 and st.get('date') == '2024-06-20' and st.get('time') == '13:00',
           'latitude, longitude, UTC offset, date and time typed into Properties are on the site (%s)' % st)
        await set_field('sunlat', '95')
        ck(((await safe("()=>window.__a3dSunSettings()")) or {}).get('lat') == 40.2732, 'a latitude of 95 is refused')
        await set_field('suntime', '14:00')
        await blur()
        await safe("()=>window.__a3dUndo()")
        ck(((await safe("()=>window.__a3dSunSettings()")) or {}).get('time') == '13:00', 'a settings change is one undo step')
        await model_props()
        txt = await safe("()=>document.body.innerText")
        ck(txt is not None and 'altitude 73.1, azimuth 172.7 deg' in txt, 'Properties states the sun: altitude 73.1, azimuth 172.7')

        print('\n-- 3. the shadow')
        await paint()
        info = (await safe("()=>window.__a3dShadowInfo()")) or {}
        ck(num(info.get('elevation')) and abs(info['elevation'] - 73.0558) <= 0.02 and info.get('triangles', 0) > 0 and info.get('casters') == 1,
           'shadows drawn for the one solid at the reference sun (%s)' % {k: info.get(k) for k in ('elevation', 'casters', 'triangles')})
        L = 3 / math.tan(math.radians(73.0558))

        async def tip():
            pts = (await safe("(i)=>window.__a3dShadowPoints(i)", col)) or []
            top = [p for p in pts if abs(p['y'] - 3) < 1e-6]
            if len(top) < 4:
                return None
            return (sum(p['x'] for p in top) / len(top) - 10, sum(p['z'] for p in top) / len(top) - 10)

        t0 = await tip()
        phi = math.radians(172.6665)
        want = (-L * math.sin(phi), L * math.cos(phi))
        ck(t0 is not None and abs(t0[0] - want[0]) < 0.01 and abs(t0[1] - want[1]) < 0.01,
           'the column top lands %.3f m away from the sun: (%.3f, %.3f), want (%.3f, %.3f)' % (L, (t0 or (0, 0))[0], (t0 or (0, 0))[1], want[0], want[1]))
        await safe("()=>window.__a3dSetTrueNorth(90)")
        t1 = await tip()
        phi = math.radians(172.6665 + 90)
        want = (-L * math.sin(phi), L * math.cos(phi))
        ck(t1 is not None and abs(t1[0] - want[0]) < 0.01 and abs(t1[1] - want[1]) < 0.01, 'with True North at 90 deg the shadow turns 90 deg with it')
        await paint()
        sp = (await safe("()=>window.__a3dSunPath()")) or {}
        n90 = sp.get('north') or [0, 0]
        await safe("()=>window.__a3dSetTrueNorth(0)")
        await safe("(o)=>window.__a3dFloorAt(o,0,0.2)", [[5, 5], [15, 5], [15, 15], [5, 15]])
        await paint()
        info = (await safe("()=>window.__a3dShadowInfo()")) or {}
        ck(info.get('casters') == 1, 'a ground slab under the column neither casts nor hides (%s casters)' % info.get('casters'))

        print('\n-- 4. the sun path')
        sp = (await safe("()=>window.__a3dSunPath()")) or {}
        paths = {p['date']: p for p in sp.get('paths') or []}
        jun, dec, mar = paths.get('2024-06-21', {}), paths.get('2024-12-21', {}), paths.get('2024-03-20', {})
        ck(num(jun.get('max')) and abs(jun['max'] - (90 - (40.2732 - 23.44))) < 0.15, 'June 21 peaks at 90 - (lat - 23.44) = 73.17 (%s)' % jun.get('max'))
        ck(num(dec.get('max')) and abs(dec['max'] - (90 - 40.2732 - 23.44)) < 0.15, 'December 21 peaks at 90 - lat - 23.44 = 26.29 (%s)' % dec.get('max'))
        ck(num(mar.get('max')) and abs(mar['max'] - (90 - 40.2732)) < 0.5, 'the March equinox peaks near 90 - lat = 49.73 (%s)' % mar.get('max'))
        now = (await safe("()=>window.__a3dSunNow()")) or {}
        ck(sp.get('sun') is not None and abs(sp['sun'][0] - now.get('azimuth', 0)) < 1e-9 and abs(sp['sun'][1] - now.get('elevation', 0)) < 1e-9, 'it marks the sun now')
        n0 = sp.get('north') or [0, 0]
        ck(abs(n0[0]) < 1e-6 and abs(n0[1] + 1) < 1e-6 and abs(n90[0] - 1) < 1e-6 and abs(n90[1]) < 1e-6,
           'its north is up with True North at 0, and to the right with True North at 90 (%s, %s)' % (n0, n90))
        box = sp.get('box') or [0, 0, 0, 0]
        cr = (await safe("()=>{var q=window.__a3dCanvasRect();return [q.width||q.w,q.height||q.h];}")) or [0, 0]
        ck(box[2] > 0 and box[0] >= 0 and box[1] >= 0 and box[0] + box[2] <= cr[0] and box[1] + box[3] <= cr[1], 'the diagram sits inside the canvas (%s)' % box)

        print('\n-- 5. night, reload, off')
        await set_field('suntime', '23:30')
        await blur()
        await paint()
        info = (await safe("()=>window.__a3dShadowInfo()")) or {}
        ck(info.get('night') is True and not info.get('triangles'), 'at 23:30 the sun is down and nothing is drawn')
        await set_field('suntime', '13:00')
        await blur()
        await page.wait_for_timeout(1500)
        await page.reload()
        await page.wait_for_timeout(2300)
        st = (await safe("()=>window.__a3dSunSettings()")) or {}
        ck(st.get('lat') == 40.2732 and st.get('tz') == -4 and st.get('time') == '13:00', 'the site settings survive a reload')
        await safe("()=>window.__a3dFlat(true)")
        await blur()
        await palette_run(page, 'SUNSTUDY')
        await paint()
        on = (await safe("()=>window.__a3dShadowInfo()")) or {}
        await palette_run(page, 'SUNSTUDY')
        await paint()
        ck(on.get('triangles', 0) > 0 and (await safe("()=>window.__a3dShadowInfo()")) is None and (await safe("()=>window.__a3dSunPath()")) is None,
           'SUNSTUDY from the palette shows the study, and run again hides it')
        ck(not errs, 'no uncaught page errors (%s)' % errs[:2])
        await browser.close()
    print('\n%d/%d checks passed' % (ck.n - len(ck.bad), ck.n))
    print('RESULT: ' + ('PASS' if not ck.bad else 'FAIL'))
    return 0 if not ck.bad else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
