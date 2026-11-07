"""climate_fixture.py -- a made-up but realistic climate, air and earthquake record for the suites.

Shaped exactly as Open-Meteo's archive and air-quality answers and the USGS GeoJSON feed, so the app
reads it as it would the real services. Deterministic: the same numbers every run (a fixed seed),
and simple enough that a suite can work out what the app should find."""
import datetime, json, math, random


def daily(y0, y1, seed=7):
    """y0..y1 inclusive: a 40 N continental climate (cold winters, hot humid summers)"""
    rnd = random.Random(seed)
    t, tx, tn, tm, p, sw = [], [], [], [], [], []
    d = datetime.date(y0, 1, 1)
    while d.year <= y1:
        doy = d.timetuple().tm_yday
        mean = 12.5 + 12.5 * math.sin(2 * math.pi * (doy - 110) / 365.25) + rnd.gauss(0, 2.2)
        rng = 9.5 + rnd.gauss(0, 1.5)
        t.append(d.isoformat())
        tx.append(round(mean + rng / 2, 1))
        tn.append(round(mean - rng / 2, 1))
        tm.append(round(mean, 1))
        wet = rnd.random() < (0.30 + 0.06 * math.sin(2 * math.pi * (doy - 120) / 365.25))
        p.append(round(rnd.expovariate(1 / 8.5), 1) if wet else 0.0)
        sw.append(round(max(1.0, 15 + 11 * math.sin(2 * math.pi * (doy - 80) / 365.25) + rnd.gauss(0, 3)), 2))
        d += datetime.timedelta(days=1)
    return {'latitude': 40.0, 'longitude': -75.0, 'timezone': 'America/New_York',
            'daily_units': {'temperature_2m_max': '°C', 'precipitation_sum': 'mm', 'shortwave_radiation_sum': 'MJ/m²'},
            'daily': {'time': t, 'temperature_2m_max': tx, 'temperature_2m_min': tn, 'temperature_2m_mean': tm,
                      'precipitation_sum': p, 'shortwave_radiation_sum': sw}}


DIRS_W = [(292.5, 0.30), (315, 0.18), (270, 0.14), (225, 0.12), (180, 0.10), (45, 0.08), (90, 0.08)]


def hourly(year, seed=11):
    rnd = random.Random(seed)
    t, T, RH, WS, WD = [], [], [], [], []
    d = datetime.datetime(year, 1, 1)
    while d.year == year:
        doy = d.timetuple().tm_yday
        base = 12.5 + 12.5 * math.sin(2 * math.pi * (doy - 110) / 365.25)
        temp = base + 5 * math.sin(2 * math.pi * (d.hour - 9) / 24) + rnd.gauss(0, 1.2)
        rh = max(15, min(100, 70 - 2.2 * (temp - base) + 8 * math.sin(2 * math.pi * (doy - 150) / 365.25) + rnd.gauss(0, 6)))
        r, acc = rnd.random(), 0
        summer = 150 <= doy <= 240
        for deg, share in DIRS_W:
            acc += share
            if r <= acc:
                break
        if summer and rnd.random() < 0.45:
            deg = 202.5   # summer: the SSW sea breeze
        ws = max(0, rnd.gammavariate(2.2, 1.7) + (0.8 if not summer else -0.4))
        if rnd.random() < 0.05:
            ws = rnd.random() * 0.4
        t.append(d.strftime('%Y-%m-%dT%H:%M'))
        T.append(round(temp, 1))
        RH.append(round(rh))
        WS.append(round(ws, 2))
        WD.append(round((deg + rnd.gauss(0, 8)) % 360))
        d += datetime.timedelta(hours=1)
    return {'latitude': 40.0, 'longitude': -75.0, 'timezone': 'America/New_York',
            'hourly': {'time': t, 'temperature_2m': T, 'relative_humidity_2m': RH, 'wind_speed_10m': WS, 'wind_direction_10m': WD}}


def air(days=92, seed=5, end=None):
    rnd = random.Random(seed)
    end = end or datetime.date.today()
    start = end - datetime.timedelta(days=days - 1)
    t, v = [], []
    d = datetime.datetime(start.year, start.month, start.day)
    while d.date() <= end:
        k = (d.date() - start).days
        level = 8 + 6 * math.sin(k / 9.0) + (14 if 40 <= k <= 45 else 0)   # a smoggy week
        t.append(d.strftime('%Y-%m-%dT%H:%M'))
        v.append(round(max(0.5, level + rnd.gauss(0, 2.5)), 1))
        d += datetime.timedelta(hours=1)
    return {'latitude': 40.0, 'longitude': -75.0, 'hourly': {'time': t, 'pm2_5': v}}


def quakes(lat=40.0, lon=-75.0):
    def at(km, az):
        r = 6371.0088
        la, lo, b = math.radians(lat), math.radians(lon), math.radians(az)
        la2 = math.asin(math.sin(la) * math.cos(km / r) + math.cos(la) * math.sin(km / r) * math.cos(b))
        lo2 = lo + math.atan2(math.sin(b) * math.sin(km / r) * math.cos(la), math.cos(km / r) - math.sin(la) * math.sin(la2))
        return [round(math.degrees(lo2), 5), round(math.degrees(la2), 5)]
    E = [(5.8, 1994, 62, 45, 8.0, 'Northern Sample Valley'), (4.9, 2011, 31, 200, 5.1, 'South of the Sample Hills'),
         (4.6, 1988, 85, 300, 11.0, 'Western Sample Range'), (4.5, 2003, 18, 110, 3.3, 'Near the site')]
    F = []
    for m, y, km, az, dep, place in E:
        ms = int(datetime.datetime(y, 6, 1).replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)
        F.append({'type': 'Feature', 'properties': {'mag': m, 'place': place, 'time': ms}, 'geometry': {'type': 'Point', 'coordinates': at(km, az) + [dep]}})
    return {'type': 'FeatureCollection', 'metadata': {'count': len(F)}, 'features': F}


def route_handler(store):
    """a Playwright context route handler answering the four services; store['hits'] records the urls"""
    async def handle(route):
        u = route.request.url
        store.setdefault('hits', []).append(u)
        mode = store.get('mode', {})
        if 'air-quality-api.open-meteo.com' in u:
            key, body = 'aq', air()
        elif 'earthquake.usgs.gov' in u:
            key, body = 'eq', quakes()
        elif 'hourly=' in u:
            key, body = 'hourly', hourly(int(u.split('start_date=')[1][:4]))
        else:
            y0 = int(u.split('start_date=')[1][:4]); y1 = int(u.split('end_date=')[1][:4])
            key, body = 'daily', daily(y0, y1)
        if mode.get(key) == 'abort':
            await route.abort('internetdisconnected')
            return
        if mode.get(key) == '429':
            await route.fulfill(status=429, body='busy', headers={'Access-Control-Allow-Origin': '*'})
            return
        await route.fulfill(status=200, body=json.dumps(body), headers={'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'})
    return handle
