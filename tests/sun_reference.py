"""sun_reference.py -- V171d: the sun path worked out again from the sources, for its suite.

- NOAA's Solar Calculator spreadsheet (gml.noaa.gov/grad/solcalc), column by column, in Python: the position, solar
  noon, sunrise and sunset, its refraction approximation included.
- NREL's SPA worked example (Reda and Andreas, NREL/TP-560-34302), as pvlib's tests/test_spa.py carries it.
- The dome: the owner's X = R cos(alt) sin(az), Y = R sin(alt), Z = R cos(alt) cos(az), in the app's axes (Y up,
  north on -Z, the plan turned by true north).
- The time zones by Python's own database (zoneinfo), not the browser's; a zone's standard time the lower of its
  mid-January and mid-July offsets.
- Play through the year; the half-years and the temperature's bands.
reference/research-sun-path.md."""
import datetime
import math
from zoneinfo import ZoneInfo

RAD = math.pi / 180

# NREL SPA's example (pvlib tests/test_spa.py): 2003-10-17 12:30:30 at UTC-7, Golden, Colorado
SPA = {'lat': 39.742476, 'lon': -105.1786, 'tz': -7, 'date': '2003-10-17', 'secs': 30,
       'e0': 39.872046, 'e': 39.888378, 'az': 194.340241}


def jday(date, mins, tz):
    y, m, d = (int(x) for x in date.split('-'))
    return (datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc).timestamp() / 86400 + 2440587.5) + mins / 1440 - tz / 24


def noaa(lat, lon, tz, date, mins):
    """the spreadsheet's row for a moment: minutes after local midnight at the UTC offset tz"""
    G = (jday(date, mins, tz) - 2451545) / 36525
    I = (280.46646 + G * (36000.76983 + G * 0.0003032)) % 360
    J = 357.52911 + G * (35999.05029 - 0.0001537 * G)
    K = 0.016708634 - G * (0.000042037 + 0.0000001267 * G)
    L = math.sin(J * RAD) * (1.914602 - G * (0.004817 + 0.000014 * G)) + math.sin(2 * J * RAD) * (0.019993 - 0.000101 * G) + math.sin(3 * J * RAD) * 0.000289
    M = I + L
    P = M - 0.00569 - 0.00478 * math.sin((125.04 - 1934.136 * G) * RAD)
    Q = 23 + (26 + ((21.448 - G * (46.815 + G * (0.00059 - G * 0.001813)))) / 60) / 60
    R = Q + 0.00256 * math.cos((125.04 - 1934.136 * G) * RAD)
    T = math.asin(math.sin(R * RAD) * math.sin(P * RAD)) / RAD
    U = math.tan(R * RAD / 2) ** 2
    V = 4 / RAD * (U * math.sin(2 * I * RAD) - 2 * K * math.sin(J * RAD) + 4 * K * U * math.sin(J * RAD) * math.cos(2 * I * RAD)
                   - 0.5 * U * U * math.sin(4 * I * RAD) - 1.25 * K * K * math.sin(2 * J * RAD))
    hc = math.cos(90.833 * RAD) / (math.cos(lat * RAD) * math.cos(T * RAD)) - math.tan(lat * RAD) * math.tan(T * RAD)
    W = math.acos(hc) / RAD if -1 <= hc <= 1 else None
    noon = 720 - 4 * lon - V + tz * 60
    AB = ((mins + V + 4 * lon - 60 * tz) % 1440 + 1440) % 1440
    AC = AB / 4 + 180 if AB / 4 < 0 else AB / 4 - 180
    cz = math.sin(lat * RAD) * math.sin(T * RAD) + math.cos(lat * RAD) * math.cos(T * RAD) * math.cos(AC * RAD)
    AD = math.acos(max(-1, min(1, cz))) / RAD
    AE = 90 - AD
    te = math.tan(AE * RAD)
    if AE > 85:
        AF = 0
    elif AE > 5:
        AF = 58.1 / te - 0.07 / te ** 3 + 0.000086 / te ** 5
    elif AE > -0.575:
        AF = 1735 + AE * (-518.2 + AE * (103.4 + AE * (-12.79 + AE * 0.711)))
    else:
        AF = -20.772 / te
    ca = (math.sin(lat * RAD) * math.cos(AD * RAD) - math.sin(T * RAD)) / (math.cos(lat * RAD) * math.sin(AD * RAD))
    ac = math.acos(max(-1, min(1, ca))) / RAD
    az = (ac + 180) % 360 if AC > 0 else ((540 - ac) % 360 + 360) % 360
    return {'elevation': AE + AF / 3600, 'geom': AE, 'azimuth': az, 'declination': T, 'noon': noon,
            'sunrise': None if W is None else noon - 4 * W, 'sunset': None if W is None else noon + 4 * W,
            'polar': '' if W is not None else ('night' if hc > 1 else 'day')}


def hhmm(m):
    m = int(round(m)) % 1440
    return '%02d:%02d' % (m // 60, m % 60)


def dome(c, y, R, az, el, north):
    a = (az + north) * RAD
    e = el * RAD
    return [c[0] + R * math.cos(e) * math.sin(a), y + R * math.sin(e), c[1] - R * math.cos(e) * math.cos(a)]


def owner_xyz(R, az, el):
    """the owner's axes: Y up, Z to true north"""
    return [R * math.cos(el * RAD) * math.sin(az * RAD), R * math.sin(el * RAD), R * math.cos(el * RAD) * math.cos(az * RAD)]


def zone_off(zone, date, time='12:00'):
    y, m, d = (int(x) for x in date.split('-'))
    hh, mm = (int(x) for x in time.split(':')[:2])
    return datetime.datetime(y, m, d, hh, mm, tzinfo=ZoneInfo(zone)).utcoffset().total_seconds() / 3600


def zone_std(zone, year):
    return min(zone_off(zone, '%d-01-15' % year), zone_off(zone, '%d-07-15' % year))


def day_path(lat, lon, tz, date, c, y, R, north):
    """every 10 minutes the sun is up, as the dome's points; the hours' marks"""
    pts, marks = [], []
    for m in range(0, 1440, 10):
        s = noaa(lat, lon, tz, date, m)
        if s['elevation'] > 0:
            p = dome(c, y, R, s['azimuth'], s['elevation'], north)
            pts.append(p)
            if m % 60 == 0:
                marks.append((m // 60, p))
    return pts, marks


YEAR = {'secs': 36, 'hold': 1.2}


def year_days(y):
    return 366 if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0 else 365


def year_date(t, y):
    """Play through the year: the date at t seconds of the clock"""
    n = year_days(y)
    p = t % (YEAR['secs'] + YEAR['hold'])
    d = min(n - 1, math.floor(n * min(1, p / YEAR['secs'])))
    return (datetime.date(y, 1, 1) + datetime.timedelta(days=d)).isoformat()


def near_drawn(date):
    """within three days of a solstice or an equinox: the drawn path stands for the day"""
    y = int(date[:4])
    d = datetime.date.fromisoformat(date)
    return any(abs((d - datetime.date(y, int(md[:2]), int(md[3:]))).days) <= 3 for md in ('06-21', '03-20', '12-21'))


ROWS = {'dj': ['12-21', '01-21', '02-21', '03-21', '04-21', '05-21', '06-21'],
        'jd': ['06-21', '07-21', '08-21', '09-21', '10-21', '11-21', '12-21']}


def half(date):
    md = date[5:]
    return 'jd' if '06-21' <= md < '12-21' else 'dj'


def heat_bands(heat, start, rows):
    """the mean at each hour over each band's days, the series' own days from its first"""
    Y = int(start[:4])
    n = len(heat) // 24

    def day_of(md):
        return (datetime.date(Y, int(md[:2]), int(md[3:])) - datetime.date(Y, 1, 1)).days
    out = []
    for j in range(len(rows) - 1):
        a, b = day_of(rows[j]), day_of(rows[j + 1])
        days = list(range(a, min(b, n))) if b > a else list(range(a, n)) + list(range(0, min(b, n)))
        mean = []
        for h in range(24):
            v = [heat[d * 24 + h] for d in days if heat[d * 24 + h] is not None]
            mean.append(sum(v) / len(v) if v else None)
        out.append(mean)
    return out


HEAT_EDGES = [-10, 0, 8, 14, 20, 24, 27, 30, 33, 36]
HEAT_COL = ['#104281', '#1c5cab', '#2a78d6', '#6da7ec', '#b7d3f6', '#c2c0b8', '#f6c2bd', '#ec8f86', '#e34948', '#b8302f', '#7d1f1f']


def heat_col(v):
    for k, e in enumerate(HEAT_EDGES):
        if v < e:
            return HEAT_COL[k]
    return HEAT_COL[-1]
