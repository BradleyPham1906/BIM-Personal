#!/usr/bin/env python3
"""bim_phase159_climate_risk_browser_tests.py -- V159: Site analysis SA2, climate and risk, and the board.

The four free services are answered inside the browser by tests/climate_fixture.py, in their own
answer shapes. Every number the app works out is worked out again here, independently, from the
same fixture.

  1. ANALYZE HOLDS SITE ANALYSIS: no Site tab on the rail; the switch; remembered; the commands.
  2. THE REQUESTS: ten full years daily, the last full year hourly, 92 days of PM2.5, M4.5+ in 100 km.
  3. THE NUMBERS: monthly normals and percentiles, degree days, solar, the Koppen zone (with known
     climates), the wind roses, comfort and the psychrometric density, PM2.5, earthquakes.
  4. FINDINGS: nine, each with its source and date, classed by its reference; one undo step.
  5. FAILURES: a source down is named and the rest kept; all down changes nothing; busy; no place.
  6. THE BOARD: header, indicators with states, nine figures with titles, sources and tables,
     hover, Esc, the theme, print, the phone; a reload keeps it all, offline.

The harness never waits without a bound (V123).
"""
import asyncio, datetime, json, math, pathlib, re, sys, traceback

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bim_phase133_site_context_browser_tests import Checks, Stalled, within, near   # noqa: E402
import climate_fixture as FX   # noqa: E402
from playwright.async_api import async_playwright   # noqa: E402

HTML = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else \
    pathlib.Path(__file__).resolve().parent.parent / 'canvas_v10.html'
CK = Checks()
Y1 = datetime.date.today().year - 1
Y0 = Y1 - 9
HOSTS = ('https://archive-api.open-meteo.com/**', 'https://air-quality-api.open-meteo.com/**', 'https://earthquake.usgs.gov/**')


# ---------------- the reference, worked out here ----------------
def pct(a, p):
    s = sorted(a)
    r = (len(s) - 1) * p
    lo, hi = math.floor(r), math.ceil(r)
    return s[lo] + (s[hi] - s[lo]) * (r - lo)


def ref_normals():
    d = FX.daily(Y0, Y1)['daily']
    M = [{'tx': [], 'tn': [], 'tm': [], 'p': {}, 'w': {}, 'sw': [], 'h': {}, 'c': {}} for _ in range(12)]
    for i, t in enumerate(d['time']):
        y, m = int(t[:4]), int(t[5:7]) - 1
        K = M[m]
        tx, tn, tm, p, sw = d['temperature_2m_max'][i], d['temperature_2m_min'][i], d['temperature_2m_mean'][i], d['precipitation_sum'][i], d['shortwave_radiation_sum'][i]
        K['tx'].append(tx); K['tn'].append(tn); K['tm'].append(tm)
        K['p'][y] = K['p'].get(y, 0) + p
        K['w'][y] = K['w'].get(y, 0) + (1 if p >= 1 else 0)
        K['sw'].append(sw / 3.6)
        mn = (tx + tn) / 2
        K['h'][y] = K['h'].get(y, 0) + max(0, 18 - mn)
        K['c'][y] = K['c'].get(y, 0) + max(0, mn - 18)
    out = []
    for K in M:
        avg = lambda a: sum(a) / len(a)
        yv = lambda o: sum(o.values()) / len(o)
        out.append({'tx': avg(K['tx']), 'tn': avg(K['tn']), 'tm': avg(K['tm']), 'tx90': pct(K['tx'], 0.9), 'tn10': pct(K['tn'], 0.1),
                    'p': yv(K['p']), 'wet': yv(K['w']), 'sw': avg(K['sw']), 'hdd': yv(K['h']), 'cdd': yv(K['c'])})
    return out


def ref_koppen(T, P, lat):
    MAT = sum(T) / 12; MAP = sum(P); Tc = min(T); Th = max(T); n10 = sum(1 for t in T if t >= 10)
    summ = [3, 4, 5, 6, 7, 8] if lat >= 0 else [9, 10, 11, 0, 1, 2]
    wint = [9, 10, 11, 0, 1, 2] if lat >= 0 else [3, 4, 5, 6, 7, 8]
    Ps = sum(P[j] for j in summ); Pw = sum(P[j] for j in wint)
    Psdry = min(P[j] for j in summ); Pswet = max(P[j] for j in summ); Pwdry = min(P[j] for j in wint); Pwwet = max(P[j] for j in wint)
    Pth = 2 * MAT if Pw >= 0.7 * MAP else (2 * MAT + 28 if Ps >= 0.7 * MAP else 2 * MAT + 14)
    if Th <= 10:
        return 'ET' if Th > 0 else 'EF'
    if MAP < 10 * Pth:
        return 'B' + ('W' if MAP < 5 * Pth else 'S') + ('h' if MAT >= 18 else 'k')
    if Tc >= 18:
        return 'Af' if min(P) >= 60 else ('Am' if min(P) >= 100 - MAP / 25 else ('As' if Psdry < Pwdry else 'Aw'))
    g = 'C' if Tc > 0 else 'D'
    s2 = 's' if (Psdry < 40 and Psdry < Pwwet / 3) else ('w' if Pwdry < Pswet / 10 else 'f')
    t3 = 'a' if Th >= 22 else ('b' if n10 >= 4 else ('d' if (g == 'D' and Tc < -38) else 'c'))
    return g + s2 + t3


def hum_ratio(T, RH):
    pv = RH / 100 * 610.94 * math.exp(17.625 * T / (T + 243.04))
    return 1000 * 0.622 * pv / (101325 - pv)


def ref_hourly():
    h = FX.hourly(Y1)['hourly']
    n = len(h['time'])
    bins = [0.5, 2, 4, 6, 8]
    c = [[0] * 5 for _ in range(16)]
    calm = tot = 0
    inside = cold = hot = 0
    psy = {}
    for i in range(n):
        ws, wd, t, rh = h['wind_speed_10m'][i], h['wind_direction_10m'][i], h['temperature_2m'][i], h['relative_humidity_2m'][i]
        tot += 1
        sec = int(math.floor((wd % 360) / 22.5 + 0.5)) % 16
        if ws < 0.5:
            calm += 1
        else:
            b = max(k for k in range(5) if ws >= bins[k])
            c[sec][b] += 1
        if 20 <= t <= 27 and 20 <= rh <= 80:
            inside += 1
        elif t < 20:
            cold += 1
        else:
            hot += 1
        key = '%d|%d' % (math.floor(t), math.floor(hum_ratio(t, rh)))
        psy[key] = psy.get(key, 0) + 1
    share = [100 * sum(r) / tot for r in c]
    prev = max(range(16), key=lambda k: share[k])
    return {'n': n, 'calm': 100 * calm / tot, 'share': share, 'prev': prev, 'inside': 100 * inside / tot,
            'cold': 100 * cold / tot, 'hot': 100 * hot / tot, 'psy': psy, 'mean': sum(h['wind_speed_10m']) / n,
            'heat': [int(math.floor(v + 0.5)) for v in h['temperature_2m']]}   # as JavaScript rounds


def ref_air():
    h = FX.air()['hourly']
    by = {}
    for t, v in zip(h['time'], h['pm2_5']):
        by.setdefault(t[:10], []).append(v)
    days = [(d, sum(v) / len(v)) for d, v in by.items() if len(v) >= 12]
    vals = [round(v, 1) for _, v in days]
    return {'n': len(days), 'mean': sum(vals) / len(vals), 'over': sum(1 for v in vals if v > 15), 'max': max(vals)}


KNOWN = [   # monthly mean temperature, rainfall, latitude -> Koppen
    ('Singapore', [26.5, 27.1, 27.5, 27.9, 28.3, 28.3, 27.9, 27.9, 27.6, 27.6, 27.0, 26.5], [234, 115, 170, 154, 171, 140, 155, 172, 160, 159, 251, 274], 1.3, 'Af'),
    ('Phoenix', [13.5, 15.3, 18.6, 22.4, 27.5, 32.6, 34.9, 34.2, 31.5, 25.0, 17.8, 12.9], [23, 24, 23, 7, 3, 1, 27, 25, 17, 15, 17, 22], 33.4, 'BWh'),
    ('London', [5.2, 5.3, 7.6, 9.9, 13.3, 16.5, 18.7, 18.5, 15.7, 12.0, 8.0, 5.5], [55, 41, 42, 44, 49, 45, 45, 50, 49, 69, 59, 55], 51.5, 'Cfb'),
    ('Rome', [7.6, 8.7, 11.4, 14.1, 18.4, 22.5, 25.4, 25.5, 21.9, 17.5, 12.2, 8.7], [67, 73, 58, 81, 53, 34, 19, 37, 73, 113, 115, 81], 41.9, 'Csa'),
    ('Moscow', [-6.2, -5.9, -0.8, 6.9, 13.2, 17.0, 19.2, 17.0, 11.3, 5.6, -0.4, -4.4], [53, 44, 39, 37, 61, 78, 84, 78, 66, 70, 52, 51], 55.8, 'Dfb'),
    ('Sydney', [23.5, 23.4, 22.1, 19.5, 16.6, 14.2, 13.4, 14.5, 17.0, 18.9, 20.4, 22.1], [92, 130, 117, 115, 98, 131, 69, 79, 61, 74, 83, 77], -33.9, 'Cfa'),
    ('Ice', [-30, -32, -31, -28, -22, -15, -10, -12, -18, -24, -28, -30], [5] * 12, -78.0, 'EF'),
]


async def run():
    ck = CK
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        ctx = await browser.new_context(viewport={'width': 1440, 'height': 900})
        ST = {}
        for h in HOSTS:
            await ctx.route(h, FX.route_handler(ST))
        page = await ctx.new_page()
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await within(page.goto('file://' + str(HTML)), 'goto')
        await page.wait_for_timeout(2300)

        async def safe(js, arg=None, pg=None):
            pg = pg or page
            try:
                return await within(pg.evaluate(js, arg) if arg is not None else pg.evaluate(js), 'evaluate ' + js[:60].replace('\n', ' '))
            except Stalled:
                raise
            except Exception as e:
                print('      (evaluate failed: %s)' % str(e)[:200])
                return None

        async def toast():
            return await safe("()=>{var t=document.getElementById('a3d-toast');return t?t.textContent:'';}") or ''

        async def set_site(lat, lon, tz='-5', pg=None):
            await safe("()=>{window.__a3dSelectFor([]);window.__a3dSetPropTab('site');window.__a3dRefreshProps();}", pg=pg)
            for k, v in (('sunlat', lat), ('sunlon', lon), ('suntz', tz)):
                await safe("""(a)=>{var L=document.querySelectorAll('#a3d-propsbody input'),e=null,i;for(i=0;i<L.length;i++)if(L[i].getAttribute('data-propmodel')===a[0])e=L[i];
                  if(!e)return false;e.value=a[1];e.dispatchEvent(new Event('change',{bubbles:true}));return true;}""", [k, v], pg=pg)
                await (pg or page).wait_for_timeout(80)

        async def clim():
            return await safe("()=>window.__a3dClim()") or {}

        async def fnd(key):
            for f in ((await safe("()=>window.__a3dSa()")) or {}).get('findings', []):
                if f.get('auto') == key:
                    return f
            return None

        try:
            has = await safe("()=>window.__acad3dV159")
            ck(bool(has) and 'windrose' in has and 'board' in has, "__acad3dV159 marker is present (%s)" % has)
            mv = re.search(r"var BIM_APP_VERSION=\{v:'V(\d+)'", HTML.read_text(encoding='utf-8'))
            ck(mv and int(mv.group(1)) >= 159, "the app says V159 or later (%s)" % (mv and mv.group(1)))
            if not has:
                raise Stalled('no V159')
            await safe("()=>{window.__a3dEnter();window.__a3dTestSetObjs([]);}")

            # ---------------------------------------------------------------------------------
            print("\n-- 1. Analyze holds Site analysis")
            tabs = await safe("()=>[].map.call(document.querySelectorAll('#a3d-rail .a3d-railbtn[data-tab]'),function(b){return b.getAttribute('data-tab');})")
            ck(tabs == ['layers', 'presentation', 'browser', 'assets', 'analyze'], "no Site tab on the rail: Site analysis is in Analyze (%s)" % tabs)
            await safe("()=>window.__a3dAnzView('analyses')")
            await page.wait_for_timeout(150)
            sw = await safe("""()=>{var w=document.querySelector('.a3d-analyze-wrap');if(!w)return null;
              return [].map.call(w.querySelectorAll('[data-anzview]'),function(b){return [b.getAttribute('data-anzview'),b.textContent,b.getAttribute('aria-selected')];});}""")
            ck(sw == [['analyses', 'Analyses', 'true'], ['site', 'Site analysis', 'false']], "Analyze opens with the switch: Analyses | Site analysis (%s)" % sw)
            await safe("()=>document.querySelector('.a3d-analyze-wrap [data-anzview=\"site\"]').click()")
            await page.wait_for_timeout(150)
            ck(await safe("()=>!!document.querySelector('.a3d-sa-wrap')&&!document.querySelector('.a3d-analyze-wrap')&&document.getElementById('a3d-shell').dataset.tab==='analyze'"),
               "pressed: the Site analysis view, still the Analyze tab")
            ck(await safe("()=>document.querySelector('.a3d-sa-wrap [data-anzview=\"site\"]').getAttribute('aria-selected')") == 'true', "with the switch on it")
            await safe("()=>document.querySelector('.a3d-sa-wrap [data-anzview=\"analyses\"]').click()")
            await page.wait_for_timeout(150)
            ck(await safe("()=>!!document.querySelector('.a3d-analyze-wrap [data-anzcard]')"), "and back to the analyses")
            await safe("()=>window.__a3dRunCmd('siteanalysis')")
            await page.wait_for_timeout(150)
            ck(await safe("()=>window.__a3dAnzView()") == 'site' and await safe("()=>!!document.querySelector('.a3d-sa-wrap')"), "SITEANALYSIS opens Analyze on Site analysis")
            ck('Get climate and risk' in (await safe("()=>document.querySelector('.a3d-sa-wrap').innerHTML") or ''), "where Climate and risk waits to be fetched")
            for q, want in (('climate', 'CLIMATE'), ('wind rose', 'CLIMATE'), ('weather data', 'CLIMATEGET'), ('earthquake', 'CLIMATE')):
                nm = [x['name'] for x in (await safe("(q)=>window.__a3dCommandSearch(q,6)", q) or [])]
                ck(want in nm[:3], "searching %r finds %s (%s)" % (q, want, nm[:4]))

            # ---------------------------------------------------------------------------------
            print("\n-- 2. the requests")
            r = await safe("()=>Promise.resolve(window.__a3dClimFetch())")
            ck(r is None and 'Set the site latitude and longitude first' in await toast() and not ST.get('hits'), "no place: refused, saying why, nothing asked")
            U = await safe("()=>window.__a3dClimUrls(40,-75)") or {}
            ck('start_date=%d-01-01' % Y0 in U.get('daily', '') and 'end_date=%d-12-31' % Y1 in U.get('daily', '') and 'temperature_2m_max' in U['daily'] and 'shortwave_radiation_sum' in U['daily'],
               "daily: the ten full years %d to %d, high, low, mean, rain, sun" % (Y0, Y1))
            ck('start_date=%d-01-01' % Y1 in U.get('hourly', '') and 'wind_speed_unit=ms' in U['hourly'] and 'relative_humidity_2m' in U['hourly'], "hourly: the last full year, in m/s, with humidity")
            ck('past_days=92' in U.get('aq', '') and 'pm2_5' in U['aq'], "air: 92 days of PM2.5")
            ck('maxradiuskm=100' in U.get('eq', '') and 'minmagnitude=4.5' in U['eq'] and 'starttime=1976-01-01' in U['eq'] and 'format=geojson' in U['eq'], "earthquakes: M4.5+ within 100 km since 1976")
            ck(all('key' not in u.lower() for u in U.values()), "no key in any of them")
            await set_site('40', '-75')
            r = await safe("()=>Promise.resolve(window.__a3dClimFetch())") or {}
            ck(r.get('climate') and r.get('hourly') and r.get('air') and r.get('quakes') == 4 and r.get('errors') == [], "one press: the climate, a year of hours, air quality, 4 earthquakes (%s)" % r)
            ck(len(ST.get('hits', [])) == 4, "four requests, one to each (%s)" % len(ST.get('hits', [])))

            # ---------------------------------------------------------------------------------
            print("\n-- 3. the numbers")
            C = (await clim()).get('climate') or {}
            K = (await clim()).get('risk') or {}
            N = C.get('normals') or {}
            RN = ref_normals()
            M = N.get('months') or []
            worst = {}
            for k in ('tx', 'tn', 'tm', 'tx90', 'tn10', 'p', 'wet', 'hdd', 'cdd'):
                worst[k] = max(abs(M[i][k] - RN[i][k]) for i in range(12)) if len(M) == 12 else 99
            ck(len(M) == 12 and all(v <= 0.051 for v in worst.values()), "the twelve months match, to the tenth: highs, lows, means, percentiles, rain, wet days, degree days (%s)" %
               {k: round(v, 3) for k, v in worst.items()})
            ck(len(M) == 12 and max(abs(M[i]['sw'] - RN[i]['sw']) for i in range(12)) <= 0.0051, "solar in kWh/m2 a day (MJ / 3.6), to the hundredth")
            DIM = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            A = N.get('annual') or {}
            ck(A and A['p'] == round(sum(round(m['p'], 1) for m in M)) and A['hdd'] == round(sum(m['hdd'] for m in M)) and A['cdd'] == round(sum(m['cdd'] for m in M)) and
               A['sw'] == round(sum(M[i]['sw'] * DIM[i] for i in range(12))), "the year: rain, degree days and solar summed from the months (%s)" % {k: A.get(k) for k in ('p', 'hdd', 'cdd', 'sw')})
            ck(N.get('years') == 10 and C.get('period') == [Y0, Y1], "ten years, %d to %d" % (Y0, Y1))
            kp = C.get('koppen') or {}
            ck(kp.get('code') == ref_koppen([m['tm'] for m in M], [m['p'] for m in M], 40) and kp.get('name'), "the fixture's climate zone: %s, %s" % (kp.get('code'), kp.get('name')))
            for name, T, P, lat, want in KNOWN:
                got = (await safe("(a)=>window.__a3dKoppen(a[0],a[1],a[2])", [T, P, lat]) or {}).get('code')
                ck(got == want == ref_koppen(T, P, lat), "Köppen: %s is %s (%s)" % (name, want, got))
            for T, RH, lo, hi in ((20, 50, 7.2, 7.4), (30, 60, 15.9, 16.3), (0, 100, 3.7, 3.85)):
                w = await safe("(a)=>window.__a3dHumRatio(a[0],a[1])", [T, RH])
                ck(w is not None and lo <= w <= hi, "humidity ratio at %d °C, %d%%: %.2f g/kg (ASHRAE %.1f to %.1f)" % (T, RH, w or -1, lo, hi))
            Hh = C.get('hourly') or {}
            RH_ = ref_hourly()
            ck(Hh.get('year') == Y1 and Hh.get('heat') == RH_['heat'], "the heat map: all %d hours of %d, in whole degrees" % (RH_['n'], Y1))
            Wy = (Hh.get('wind') or {}).get('year') or {}
            tot = sum(sum(r) for r in Wy.get('pct', [])) + Wy.get('calm', 0)
            ck(Wy and abs(tot - 100) < 0.2, "the rose: every hour once, the sectors and calm adding to 100%% (%.2f)" % tot)
            ck(Wy and Wy['prev'] == RH_['prev'] and abs(Wy['calm'] - RH_['calm']) < 0.06 and abs(Wy['mean'] - RH_['mean']) < 0.06,
               "prevailing from the %s, calm %.1f%%, mean %.1f m/s, as worked out here" % (['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'][RH_['prev']], RH_['calm'], RH_['mean']))
            ck(Wy and all(abs(sum(Wy['pct'][k]) - RH_['share'][k]) < 0.06 for k in range(16)), "each sector's share, as worked out here")
            ck((Hh.get('wind') or {}).get('summer', {}).get('prev') == 9 and (Hh.get('wind') or {}).get('winter', {}).get('prev') == 13,
               "summer from the SSW (the sea breeze in the fixture), winter from the WNW")
            cf = Hh.get('comfort') or {}
            ck(cf and abs(cf['inside'] - RH_['inside']) < 0.06 and abs(cf['cold'] - RH_['cold']) < 0.06 and abs(cf['hot'] - RH_['hot']) < 0.06,
               "comfort: %.1f%% inside, %.1f%% too cool, %.1f%% too hot or humid" % (RH_['inside'], RH_['cold'], RH_['hot']))
            ck(Hh.get('psy') == RH_['psy'], "the psychrometric density: every hour in its 1 °C by 1 g/kg cell (%d cells)" % len(RH_['psy']))
            Q = K.get('air') or {}
            RA = ref_air()
            ck(Q and len(Q['days']) == RA['n'] and abs(Q['mean'] - RA['mean']) < 0.06 and Q['over'] == RA['over'] and Q['max']['v'] == RA['max'],
               "PM2.5: %d daily means, %.1f on average, %d days above 15, at most %.1f" % (RA['n'], RA['mean'], RA['over'], RA['max']))
            ck(Q.get('status') == ('serious' if RA['mean'] > 15 else 'warning'), "its state: %s (a mean above 5, days above 15)" % Q.get('status'))
            E = K.get('quakes') or {}
            ev = E.get('events') or []
            ck([e['m'] for e in ev] == [5.8, 4.9, 4.6, 4.5] and [round(e['km']) for e in ev] == [62, 31, 85, 18] and [e['az'] for e in ev] == [45, 200, 300, 110],
               "the earthquakes, the largest first, by distance and direction: %s" % [(e['m'], e['km'], e['az']) for e in ev])
            ck(E.get('status') == 'warning' and E.get('max', {}).get('t') == '1994-06-01', "its state: watch (none of M6, none of M5 within 50 km)")
            sz = len(json.dumps(C)) + len(json.dumps(K))
            ck(sz < 120000, "kept small enough to save with the project: %d bytes" % sz)

            # ---------------------------------------------------------------------------------
            print("\n-- 4. findings")
            keys = ['climate.koppen', 'climate.temp', 'climate.rain', 'climate.degreedays', 'climate.solar', 'climate.wind', 'climate.comfort', 'risk.air', 'risk.seismic']
            F = [await fnd(k) for k in keys]
            ck(all(F) and all(f['source'] and re.match(r'^\d{4}-\d{2}-\d{2}$', f['date']) for f in F), "nine findings, each with its source and date")
            ck(all(f['cat'] == ('risk' if k.startswith('risk') else 'climate') for f, k in zip(F, keys)), "under Climate and Environmental risk")
            ck(F[0]['value'].startswith(kp.get('code', '?') + ': ') and 'Beck et al. 2018' in F[0]['source'], "the zone, its rules named")
            ck(F[3]['value'].startswith('%s heating and %s cooling degree days' % ('{:,}'.format(A['hdd']), '{:,}'.format(A['cdd']))), "degree days (%s)" % F[3]['value'])
            ck(F[7]['cls'] == 'constraint' and 'WHO' in F[7]['value'] and 'CAMS' in F[7]['source'], "air: a constraint, against WHO, credited to CAMS")
            ck(F[8]['cls'] == 'constraint' and F[8]['sev'] == 1 and 'M5.8 (1994), 62 km NE' in F[8]['value'] and F[8]['source'] == 'USGS earthquake catalogue',
               "earthquakes: a low constraint, the largest named (%s)" % F[8]['value'])
            await safe("()=>window.__a3dUndo()")
            cc = await clim()
            ck(cc.get('climate') is None and cc.get('risk') is None and await fnd('climate.temp') is None, "one undo takes the climate, the risks and their findings back")
            ss = await safe("()=>window.__a3dSunSettings()") or {}
            ck(ss.get('lat') == 40 and ss.get('tz') == -5, "and only them: the latitude and UTC offset set before stay (%s, %s)" % (ss.get('lat'), ss.get('tz')))
            await safe("()=>window.__a3dRedo()")
            ck((await clim()).get('climate') and await fnd('risk.air'), "redo returns them")

            # ---------------------------------------------------------------------------------
            print("\n-- 5. failures")
            ST['mode'] = {'aq': 'abort'}
            ST['hits'] = []
            r = await safe("()=>Promise.resolve(window.__a3dClimFetch())") or {}
            ck(r.get('climate') and r.get('air') is False and any('air-quality-api.open-meteo.com' in e for e in r.get('errors', [])), "air quality down: named by its host, the rest kept (%s)" % r.get('errors'))
            ck('Not available: air-quality-api.open-meteo.com' in await toast(), "and said")
            ck((await clim()).get('risk', {}).get('air'), "the earlier air quality is kept, not wiped")
            ST['mode'] = {'daily': '429', 'hourly': 'abort', 'aq': 'abort', 'eq': 'abort'}
            before = await clim()
            r = await safe("()=>Promise.resolve(window.__a3dClimFetch())") or {}
            ck(r.get('error') and 'busy (HTTP 429)' in r['error'] and await clim() == before, "all down: nothing changes, and each failure is named (%s)" % (r.get('error') or '')[:90])
            ST['mode'] = {}
            await safe("()=>{window.__a3dClimFetch();}")
            r2 = await safe("()=>window.__a3dClimFetch()")
            ck(r2 is None and 'already on their way' in await toast(), "a second press while one runs: refused")
            for _ in range(60):
                if not await safe("()=>window.__a3dClimBusy()"):
                    break
                await page.wait_for_timeout(100)

            # ---------------------------------------------------------------------------------
            print("\n-- 6. the board")
            await safe("()=>window.__a3dAnzView('site')")
            await page.wait_for_timeout(150)
            await safe("()=>document.querySelector('.a3d-sa-wrap [data-saact=\"climboard\"]').click()")
            await page.wait_for_timeout(300)
            B = await safe("""()=>{var b=document.querySelector('.a3d-clb');if(!b)return null;
              return {h1:b.querySelector('.a3d-clb-h1').textContent,sub:b.querySelector('.a3d-clb-sub').textContent,
                kpis:[].map.call(b.querySelectorAll('.a3d-clb-kpi'),function(k){return [k.querySelector('.a3d-clb-kl').textContent,k.querySelector('.a3d-clb-kv').textContent,!!k.querySelector('.a3d-clb-st')];}),
                figs:[].map.call(b.querySelectorAll('.a3d-clb-card'),function(c){return {no:c.getAttribute('data-fig'),t:c.querySelector('.a3d-clb-h2').textContent,svg:c.querySelectorAll('svg').length,
                  src:!!c.querySelector('.a3d-clb-src'),tbl:!!c.querySelector('.a3d-clb-table')};}),
                notes:!!b.querySelector('.a3d-clb-notes'),dialog:b.getAttribute('role'),open:document.body.classList.contains('a3d-clb-open')};}""") or {}
            ck(B.get('dialog') == 'dialog' and B.get('open') and B['h1'].endswith(': climate and risk'), "the board opens from Site analysis, a dialog over the app")
            ck(kp.get('code', '?') in B.get('sub', '') and '%d–%d' % (Y0, Y1) in B['sub'] and '40.0000° N, 75.0000° W' in B['sub'], "its header: the place, the zone, the period")
            labels = [k[0] for k in B.get('kpis', [])]
            ck(labels == ['Climate zone', 'Mean temperature', 'Rainfall', 'Prevailing wind', 'Degree days', 'Solar energy', 'Outdoor comfort', 'PM2.5', 'Earthquakes'],
               "nine indicators, in reading order (%s)" % labels)
            ck([k[2] for k in B['kpis']] == [False] * 7 + [True, True], "a state (icon and word) only where a reference exists: PM2.5 and earthquakes")
            st = await safe("()=>[].map.call(document.querySelectorAll('.a3d-clb-kpi .a3d-clb-st'),function(s){return [s.textContent,!!s.querySelector('svg')];})")
            ck(st == [['Watch', True], ['Watch', True]], "each state an icon and a word, never colour alone (%s)" % st)
            figs = B.get('figs', [])
            ck([f['no'] for f in figs] == [str(i) for i in range(1, 10)] and all(f['svg'] >= 1 and f['src'] and f['tbl'] for f in figs),
               "nine figures, numbered, each with its chart, its source and a table")
            ck(all(re.search(r'\d', f['t']) for f in figs), "every figure's title states a finding, with its number")
            ck(figs and figs[0]['svg'] == 2 and figs[1]['svg'] == 3, "Fig. 1 temperature and rain as two charts sharing the months (no second y-axis); Fig. 2 the year's rose and two seasons")
            ix = max(range(12), key=lambda i: M[i]['tx'])
            lab = await safe("()=>[].map.call(document.querySelectorAll('.a3d-clb-card[data-fig=\"1\"] svg .lb'),function(t){return t.textContent;})") or []
            ck(('%.1f°' % M[ix]['tx']) in lab, "the warmest month's high labelled directly (%s)" % lab)
            nrect = await safe("()=>document.querySelector('.a3d-clb-card[data-fig=\"3\"] svg').querySelectorAll('rect').length")
            ck(nrect and nrect < 8760 / 2, "the heat map's runs merged: %s rectangles, not 8,760" % nrect)
            ck(await safe("()=>getComputedStyle(document.querySelector('.a3d-clb-table')).display") == 'none', "tables hidden until asked")
            await safe("()=>document.querySelector('[data-clb=\"tables\"]').click()")
            ck(await safe("()=>getComputedStyle(document.querySelector('.a3d-clb-table')).display") == 'table' and
               await safe("()=>document.querySelector('[data-clb=\"tables\"]').getAttribute('aria-pressed')") == 'true', "Tables: every chart's numbers as a table")
            rows = await safe("()=>document.querySelectorAll('.a3d-clb-card[data-fig=\"1\"] .a3d-clb-table tbody tr').length")
            ck(rows == 12, "Fig. 1's table: twelve months")
            await safe("()=>document.querySelector('[data-clb=\"tables\"]').click()")
            box = await safe("()=>{var e=document.querySelectorAll('.a3d-clb-card[data-fig=\"1\"] svg')[1].querySelectorAll('path.mk')[6];e.scrollIntoView({block:'center'});var r=e.getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2];}")
            await page.mouse.move(box[0], box[1])
            await page.wait_for_timeout(120)
            tip = await safe("()=>{var t=document.querySelector('.a3d-clb-tip');return t.hidden?null:t.textContent;}")
            ck(tip and tip.startswith('July') and ('%d mm' % round(M[6]['p'])) in tip, "hover a rain bar: July and its millimetres (%s)" % tip)
            box = await safe("()=>{var s=document.querySelector('.a3d-clb-card[data-fig=\"3\"] svg');s.scrollIntoView({block:'center'});var r=s.getBoundingClientRect();return [r.left,r.top,r.width,r.height];}")
            L, T0, W, H = 46, 8, 1200, 268
            days = len(RH_['heat']) // 24
            cw = (W - 10 - L) / days
            ch = (H - 24 - T0) / 24
            d, hh = 191, 15
            px = box[0] + (L + (d + 0.5) * cw) * box[2] / W
            py = box[1] + (T0 + (hh + 0.5) * ch) * box[3] / H
            await page.mouse.move(px, py)
            await page.wait_for_timeout(120)
            tip = await safe("()=>{var t=document.querySelector('.a3d-clb-tip');return t.hidden?null:t.textContent;}") or ''
            dd = datetime.date(Y1, 1, 1) + datetime.timedelta(days=d)
            ck(tip.startswith('%d %s, 15:00' % (dd.day, dd.strftime('%B'))) and ('%d °C' % RH_['heat'][d * 24 + hh]) in tip,
               "hover the heat map: the day, the hour, its temperature and band (%s)" % tip)
            surf = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--surf').trim()")
            await safe("()=>document.body.classList.add('light-theme')")
            surf2 = await safe("()=>getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--surf').trim()")
            await safe("()=>document.body.classList.remove('light-theme')")
            ck(surf == '#1a1a19' and surf2 == '#fcfcfb', "it follows the theme: dark %s, light %s" % (surf, surf2))
            await page.emulate_media(media='print')
            pr = await safe("""()=>({bar:getComputedStyle(document.querySelector('.a3d-clb-bar')).display,pos:getComputedStyle(document.querySelector('.a3d-clb')).position,
              shell:getComputedStyle(document.getElementById('a3d-shell')).display,surf:getComputedStyle(document.querySelector('.a3d-clb')).getPropertyValue('--surf').trim()})""") or {}
            await page.emulate_media(media='screen')
            ck(pr.get('bar') == 'none' and pr.get('pos') == 'static' and pr.get('shell') == 'none' and pr.get('surf') == '#fff', "in print: the board alone, on white, without its bar (%s)" % pr)
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(100)
            ck(await safe("()=>!document.querySelector('.a3d-clb')&&!document.body.classList.contains('a3d-clb-open')"), "Esc closes it")
            await safe("()=>window.__a3dRunCmd('climate')")
            ck(await safe("()=>!!document.querySelector('.a3d-clb .a3d-clb-kpi')"), "CLIMATE opens it")
            await safe("()=>window.__a3dClbClose()")
            # a reload, offline
            before = await clim()
            await page.wait_for_timeout(700)
            ST['mode'] = {'daily': 'abort', 'hourly': 'abort', 'aq': 'abort', 'eq': 'abort'}
            await within(page.reload(), 'reload')
            await page.wait_for_timeout(2300)
            ck(await clim() == before, "a reload keeps it all")
            ck(await safe("()=>window.__a3dAnzView()") == 'site', "and Analyze opens on the view last chosen, Site analysis")
            await safe("()=>window.__a3dClbOpen()")
            ck(await safe("()=>document.querySelectorAll('.a3d-clb-card').length") == 9, "and the board opens offline, all nine figures")
            ck(not errs, "no page errors (%s)" % errs[:3])
            await ctx.close()

            # a phone
            ctx2 = await browser.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
            ST2 = {}
            for h in HOSTS:
                await ctx2.route(h, FX.route_handler(ST2))
            p2 = await ctx2.new_page()
            await within(p2.goto('file://' + str(HTML)), 'goto')
            await p2.wait_for_timeout(1800)
            await safe("()=>window.__a3dEnter()", pg=p2)
            await set_site('40', '-75', pg=p2)
            await safe("()=>Promise.resolve(window.__a3dClimFetch())", pg=p2)
            await safe("()=>window.__a3dClbOpen()", pg=p2)
            await p2.wait_for_timeout(300)
            g = await safe("""()=>{var b=document.querySelector('.a3d-clb'),k=document.querySelectorAll('.a3d-clb-kpi');
              return {sw:b.scrollWidth,cw:b.clientWidth,k0:k[0].getBoundingClientRect().top,k1:k[1].getBoundingClientRect().top,k2:k[2].getBoundingClientRect().top,
                vb:document.querySelector('.a3d-clb-card[data-fig="1"] svg').getAttribute('viewBox'),
                heat:getComputedStyle(document.querySelector('.a3d-clb-heat')).overflowX,btn:document.querySelector('[data-clb="close"]').getBoundingClientRect().height};}""", pg=p2) or {}
            ck(g and g['sw'] <= g['cw'] + 1, "on a phone: nothing scrolls sideways (%s)" % g)
            ck(g and g['k0'] == g['k1'] and g['k2'] > g['k1'], "indicators two to a row")
            ck(g and g['vb'] == '0 0 360 220', "charts drawn for the phone's width, so their text stays readable (%s)" % g.get('vb'))
            ck(g and g['heat'] == 'auto' and g['btn'] >= 38, "the year's heat map swipes; touch-sized buttons")
            await ctx2.close()
        except Stalled as e:
            ck(False, "the harness stalled: %s" % e)
        except Exception:
            traceback.print_exc()
            ck(False, "the harness raised")
        await browser.close()

    print("\n%d/%d checks passed" % (ck.n - len(ck.bad), ck.n))
    if ck.bad:
        for b in ck.bad:
            print("  FAILED: " + b)
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(run()))
