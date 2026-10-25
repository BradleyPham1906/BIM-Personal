"""animation_reference.py -- V170's motions worked out again in Python, from the design
(reference/research-animation.md, section 9) and not from the app's code.

What is a fact of the world here is checked elsewhere: the sun's rise and set come from the app's
NOAA equations, which V107's suite holds to NREL's SPA; this file says what the clock does with them.

  SETTINGS        the numbers the design fixes: the frame cap, a march's speed and dashes, a wind's
                  cycle, the ripple's speed and hold, the reveal's step and fade, the sun's sweep
  AUTO            each analysis's own motion, by its element's key
  ANALYZE_ORDER   Analyze's order of the analyses (V164 to V168), the reveal's
"""
import math

SETTINGS = {
    'fps': 30,
    'march': {'speed': 28, 'dash': 6, 'gap': 14},
    'draw': {'grow': 1.6, 'hold': 1.8, 'fade': 0.6, 'rest': 0.5, 'stagger': 0.35},
    'ring': {'mps': 150, 'hold': 2.2},
    'reveal': {'step': 0.45, 'fade': 0.5},
    'sun': {'secs': 24, 'hold': 1.2, 'fill': '#5b6c8a'},
}
NAMES = {'march': 'Marching dashes', 'draw': 'Drawn on', 'ring': 'Growing ring', 'sun': 'Through the day', 'none': 'Still'}
AUTO = [['frame', 'dist:', 'ring'], ['wind', 'prevail:', 'draw'],
        ['flow', 'flow:', 'march', 'path'], ['flow', 'exit:', 'march', 'path'], ['views', 'view:', 'march', 'path'], ['vehicles', 'entry:', 'march', 'path'],
        ['walk', 'w', 'march'], ['needs', 'need:', 'march'], ['transit', 'routes', 'march', 'path'], ['transit', 'way:', 'march'], ['transit', 'catch', 'march'],
        ['sun', 'now', 'sun'], ['shadow', 'sh:', 'sun']]
ANALYZE_ORDER = ['frame', 'sun', 'shadow', 'wind', 'views', 'noise', 'contours', 'slope', 'aspect', 'flow', 'ponds', 'flood',
                 'streets', 'cycling', 'transit', 'walk', 'needs', 'vehicles', 'landuse', 'figure', 'green', 'zoning']


def mod(t, p):
    return ((t % p) + p) % p if p > 0 else 0.0


def kinds(g):
    """the motions an element's geometry can take"""
    k, n = g.get('kind'), len(g.get('pts') or [])
    if k == 'live' or g.get('bands'):
        return []
    out = []
    if (len(g.get('lines') or []) > 0) if k == 'lines' else n >= 2:
        out.append('march')
    if k not in ('segs', 'lines') and n >= 2:
        out.append('draw')
    if k not in ('segs', 'lines') and g.get('closed') and n >= 3:
        out.append('ring')
    return out


def auto(a, key):
    for row in AUTO:
        if row[0] == a and str(key).startswith(row[1]):
            return row
    return None


def motion(dg):
    """an element's motion: its own style, else its analysis's; None when still"""
    m = (dg.get('s') or {}).get('anim')
    ks = kinds(dg['g'])
    if m == 'none':
        return None
    if m and m != 'sun' and m in NAMES and m in ks:
        return m
    row = auto(dg['a'], dg['k'])
    if not row:
        return None
    if row[2] == 'sun':
        return 'sun'
    return row[2] if row[2] in ks else None


def goes_out(dg):
    row = auto(dg['a'], dg['k'])
    return not (dg.get('s') or {}).get('head') and not (row and len(row) > 3 and row[3] == 'path')


def draw_of(t, i):
    """a wind drawn on: (how far, opacity) at t, the i-th of its analysis"""
    B = SETTINGS['draw']
    per = B['grow'] + B['hold'] + B['fade'] + B['rest']
    p = mod(t - i * B['stagger'], per)
    if p < B['grow']:
        x = p / B['grow']
        return x * x * (3 - 2 * x), 1.0
    if p < B['grow'] + B['hold']:
        return 1.0, 1.0
    if p < B['grow'] + B['hold'] + B['fade']:
        return 1.0, 1 - (p - B['grow'] - B['hold']) / B['fade']
    return 0.0, 0.0


def ring_k(t, r, rings):
    """the ripple: how far the ring of radius r has grown (0 while a smaller ring carries the front)"""
    B = SETTINGS['ring']
    rmax = max(rings)
    w = mod(t, rmax / B['mps'] + B['hold']) * B['mps']
    if w >= r:
        return 1.0
    if any(w + 1e-6 < q < r - 1e-6 for q in rings):
        return 0.0
    return w / r


def reveal(t, play_at, j):
    R = SETTINGS['reveal']
    x = (t - play_at - j * R['step']) / R['fade']
    return 0.0 if x <= 0 else (1.0 if x >= 1 else x)


def hhmm(m):
    m = int(round(m)) % 1440
    return '%02d:%02d' % (m // 60, m % 60)


def sun_time(t, day):
    """the sun's time at t: day is the app's NOAA result at noon (sunrise, sunset, polar)"""
    B = SETTINGS['sun']
    if day is None or day.get('polar') == 'night':
        return None
    if day.get('polar') == 'day':
        a, b = 0, 1439
    else:
        a, b = math.ceil(day['sunrise']), math.floor(day['sunset'])
    if not b > a:
        return None
    p = mod(t, B['secs'] + B['hold'])
    return hhmm(math.floor(a + (b - a) * min(1.0, p / B['secs'])))


def tint(hexcol):
    """a solid line's moving dashes: its colour 60% toward white, or 50% toward black on a pale line"""
    if not (isinstance(hexcol, str) and len(hexcol) == 7 and hexcol[0] == '#'):
        return 'rgba(255,255,255,0.85)'
    r, g, b = int(hexcol[1:3], 16), int(hexcol[3:5], 16), int(hexcol[5:7], 16)
    pale = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 > 0.72
    to, k = (0, 0.5) if pale else (255, 0.6)

    def q(v):
        x = v + (to - v) * k
        return int(math.floor(x + 0.5))   # JavaScript's Math.round
    return 'rgb(%d,%d,%d)' % (q(r), q(g), q(b))


def dome_point(c, y, R, az, el, north):
    """a sun on the sun paths' dome, as the app draws the paths (V164): azimuth from true north"""
    a, e = math.radians(az + north), math.radians(el)
    return [c[0] + R * math.cos(e) * math.sin(a), y + R * math.sin(e), c[1] - R * math.cos(e) * math.cos(a)]
