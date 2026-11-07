"""assets_reference.py -- V169: the assets' sizes, worked out again in Python from their sources.

Every value is the one its source prints (reference/research-assets.md names each, what was read, and
its level); each is checked against the unit the source states it in where that differs from the app's
metres. The derivations are written from the method each source gives, not from the app's code:
NASA's linear scaling for a body, ETCCDI's GSL for the growing season, AASHTO's geometry for a turn.
"""
import datetime, math

FT, INCH = 0.3048, 0.0254

# ---- the registry's values, as their sources print them ----
TOPICS = {
    'body.us': {'man': 1.753, 'woman': 1.613, 'child': 1.321},                         # NCHS 2021, Tables 7, 9, 11 (cm)
    'body.hidh': {'st_lo': 1.486, 'st_hi': 1.946, 'sit_lo': 0.777, 'sit_hi': 1.013,     # NASA HIDH Rev1, App. B Tables 1a, 1b
                  'eye_lo': 0.665, 'eye_hi': 0.889, 'sh_lo': 0.378, 'sh_hi': 0.561},
    'wheel.awmp': {'height': 1.249, 'seat': 0.495, 'eye': 1.152, 'space_w': 0.82, 'space_l': 1.42},   # IDeA, AWMP 2010
    'ada.space': {'clear_w': 0.76, 'clear_l': 1.22, 'turn': 1.525},                    # 2010 ADA Standards 305.3, 304.3.1
    'mutcd.walk': {'clear': 1.067, 'slow': 0.914},                                      # MUTCD 11th with Rev. 1, 4I.06
    'ltn.cycle': {'length': 1.8, 'width': 0.65, 'wheel': 0.7, 'turn_out': 1.65, 'turn_in': 0.85, 'gap': 1.2,
                  'gap_min': 1, 'bay': 2, 'aisle': 3, 'wall': 0.6, 'front': 1},          # LTN 1/20, Tables 5-1, 11-2
    'parking.bay': {'width': 2.4, 'length': 4.8, 'aisle90': 6, 'aisle60': 4.2, 'aisle45': 3.6},   # Manual for Streets 8.3
    'etccdi.gsl': {'t': 5, 'days': 6},                                                   # ETCCDI's 27 indices, GSL
    'aashto.vehicles': {                                                                 # Green Book 7th, Tables 2-4b, 2-5b
        'P_l': 5.79, 'P_w': 2.13, 'P_h': 1.3, 'P_of': 0.91, 'P_or': 1.52, 'P_wb': 3.35, 'P_r': 7.26, 'P_ctr': 6.4, 'P_rin': 4.39,
        'SU_l': 9.14, 'SU_w': 2.44, 'SU_h': 4.11, 'SU_hlo': 3.35, 'SU_of': 1.22, 'SU_or': 1.83, 'SU_wb': 6.1, 'SU_r': 12.73,
        'SU_ctr': 11.58, 'SU_rin': 8.64,
        'BUS_l': 12.19, 'BUS_w': 2.59, 'BUS_h': 3.2, 'BUS_of': 2.13, 'BUS_or': 2.44, 'BUS_wb': 7.62, 'BUS_r': 12.8,
        'BUS_ctr': 11.52, 'BUS_rin': 7.45},
    'app.assets': {'seat': 0.45, 'bike_h': 1.05, 'stand_w': 0.75, 'stand_h': 0.75, 'line': 0.1, 'wheel_p': 0.65,
                   'wheel_hv': 1, 'crown': 0.6},                                         # the app's own (V169)
}
# the Urban Tree Database: type, height (m), crown across (m), crown over height -- the medians of the trees at or
# above their type's median trunk diameter, worked out from TS3_Raw_tree_data.csv (research-assets.md, 4)
UTD = [['BDS', 8.2, 8.7, 1.07], ['BDM', 14, 11.9, 0.85], ['BDL', 20, 15.9, 0.81], ['BES', 8.5, 8, 0.96], ['BEM', 11.5, 11.3, 0.98],
       ['BEL', 16, 15.1, 0.98], ['CES', 7, 6, 0.87], ['CEM', 12.5, 8.5, 0.74], ['CEL', 20, 10.7, 0.57]]
LEVELS = {'body.us': 'P', 'body.hidh': 'P', 'wheel.awmp': 'P', 'ada.space': 'P', 'mutcd.walk': 'P', 'ltn.cycle': 'P',
          'parking.bay': 'P', 'utd.trees': 'P', 'etccdi.gsl': 'P', 'aashto.vehicles': 'P', 'app.assets': 'A'}
HOSTS = {'body.us': 'www.cdc.gov', 'body.hidh': 'www.nasa.gov', 'wheel.awmp': 'idea.ap.buffalo.edu', 'ada.space': 'www.ada.gov',
         'mutcd.walk': 'mutcd.fhwa.dot.gov', 'ltn.cycle': 'assets.publishing.service.gov.uk', 'parking.bay': 'assets.publishing.service.gov.uk',
         'utd.trees': 'www.fs.usda.gov', 'etccdi.gsl': 'etccdi.pacificclimate.org', 'aashto.vehicles': 'store.transportation.org'}

# ---- the values in the units their sources print them ----
IN_SOURCE = {
    ('body.us', 'man'): 175.3 / 100, ('body.us', 'woman'): 161.3 / 100, ('body.us', 'child'): 132.1 / 100,
    ('ada.space', 'clear_w'): 760 / 1000.0, ('ada.space', 'clear_l'): 1220 / 1000.0, ('ada.space', 'turn'): 1525 / 1000.0,
    ('mutcd.walk', 'clear'): 3.5 * FT, ('mutcd.walk', 'slow'): 3 * FT,
}
# Table 2-4a and 2-5a, in feet; the metric tables agree within their rounding (0.02 m), but for the city bus's minimum
# design turning radius: 41.6 ft is 12.68 m, Table 2-5b prints 12.80 m. The app keeps 2-5b, and says so.
GB_FEET = {'P_l': 19.0, 'P_w': 7.0, 'P_h': 4.3, 'P_of': 3.0, 'P_or': 5.0, 'P_wb': 11.0, 'P_r': 23.8, 'P_ctr': 21.0, 'P_rin': 14.4,
           'SU_l': 30.0, 'SU_w': 8.0, 'SU_h': 13.5, 'SU_hlo': 11.0, 'SU_of': 4.0, 'SU_or': 6.0, 'SU_wb': 20.0, 'SU_r': 41.8,
           'SU_ctr': 38.0, 'SU_rin': 28.4,
           'BUS_l': 40.0, 'BUS_w': 8.5, 'BUS_h': 10.5, 'BUS_of': 7.0, 'BUS_or': 8.0, 'BUS_wb': 25.0, 'BUS_r': 41.6,
           'BUS_ctr': 37.8, 'BUS_rin': 24.5}
GB_DIFFER = {'BUS_r'}


def v(t, n):
    return TOPICS[t][n]


def lerp(a, b, t):
    return a + (b - a) * t


# ---- people: NASA's dimensions linear in stature between its smallest and largest ----
def body(who='woman', pose='standing', h=None):
    st = h if h and h > 0 else v('body.us', 'child' if who == 'child' else ('man' if who == 'man' else 'woman'))
    H = TOPICS['body.hidh']
    t = (st - H['st_lo']) / (H['st_hi'] - H['st_lo'])
    sit = lerp(H['sit_lo'], H['sit_hi'], t)
    es = lerp(H['eye_lo'], H['eye_hi'], t)
    sh = lerp(H['sh_lo'], H['sh_hi'], t)
    head = sit - es                       # the top of the head to the eyes, the same standing or seated
    seated = pose == 'seated'
    seat = v('app.assets', 'seat') if seated else 0
    return {'st': st, 't': t, 'sh': sh, 'head': head, 'eye': seat + es if seated else st - head,
            'top': seat + sit if seated else st, 'out': t < 0 or t > 1, 'speed': 80 / 60.0}


# ---- trees: their type's sizes ----
def tree_type(leaf='B', cyc='D', size='M'):
    lf = 'C' if leaf == 'C' else 'B'
    sz = size if size in ('S', 'M', 'L') else 'M'
    for key in (lf + ('E' if cyc == 'E' else 'D') + sz, lf + 'E' + sz, lf + 'D' + sz):
        for row in UTD:
            if row[0] == key:
                return {'key': key, 'h': row[1], 'cd': row[2], 'r': row[3]}
    return None


def leaf_of(tags):
    lt, lc = str(tags.get('leaf_type', '')), str(tags.get('leaf_cycle', ''))
    return {'type': 'C' if lt == 'needleleaved' else ('B' if lt == 'broadleaved' else ''),
            'cyc': 'D' if lc in ('deciduous', 'semi_deciduous') else ('E' if lc in ('evergreen', 'semi_evergreen') else '')}


def crown_ratio(tags):
    L = leaf_of(tags)
    if not L['type']:
        return v('app.assets', 'crown')
    T = tree_type(L['type'], L['cyc'] or ('E' if L['type'] == 'C' else 'D'), 'M')
    return T['r']


# ---- vehicles: AASHTO's geometry of the sharpest turn ----
VEH = {'car': 'P', 'truck': 'SU', 'bus': 'BUS'}


def vehicle(code):
    g = lambda n: v('aashto.vehicles', code + '_' + n)
    V = {k: g(k) for k in ('l', 'w', 'h', 'of', 'or', 'wb', 'r', 'ctr', 'rin')}
    V['rr'] = math.sqrt(V['ctr'] ** 2 - V['wb'] ** 2)              # the rear axle's middle from the turn's centre
    V['rov'] = math.hypot(V['rr'] + V['w'] / 2, V['wb'] + V['of'])  # the front overhang's outer corner
    V['d'] = v('app.assets', 'wheel_p' if code == 'P' else 'wheel_hv')
    return V


def turn_centre(code, x, z, heading=0.0, side='L'):
    """a vehicle placed at x, z facing heading (0 along +z): its turn's centre. Left of a driver facing +z is +x
    (project north is -z, so +z faces south and its left is east)"""
    V = vehicle(code)
    fx, fz = math.sin(heading), math.cos(heading)
    zr = -V['l'] / 2 + V['or']
    ax, az = x + fx * zr, z + fz * zr
    sd = -1 if side == 'R' else 1
    return [ax + sd * fz * V['rr'], az - sd * fx * V['rr']]


# ---- the growing season: ETCCDI's GSL, year by year ----
def gsl_years(daily, lat):
    """from each full year's daily means: (start, end) in days from 1 January (1 July in the Southern Hemisphere);
    the start the first day of the first span of at least 6 days above 5 C, the end the first day of the first span
    after mid-year of 6 days below 5 C; no season, (len, len); no end, the year's length"""
    T, N, sh = v('etccdi.gsl', 't'), v('etccdi.gsl', 'days'), lat < 0
    d = daily['daily']
    years = {}
    for i, s in enumerate(d['time']):
        Y, M, D = int(s[:4]), int(s[5:7]), int(s[8:10])
        sy = Y - 1 if (sh and M < 7) else Y
        o = (datetime.date(Y, M, D) - datetime.date(sy, 7 if sh else 1, 1)).days
        tm = d.get('temperature_2m_mean', [None] * len(d['time']))[i]
        if tm is None and d['temperature_2m_max'][i] is not None and d['temperature_2m_min'][i] is not None:
            tm = (d['temperature_2m_max'][i] + d['temperature_2m_min'][i]) / 2
        years.setdefault(sy, {})[o] = tm
    out = []
    for y in sorted(years):
        a = years[y]
        y0 = datetime.date(y, 7 if sh else 1, 1)
        y1 = datetime.date(y + 1, 7 if sh else 1, 1)
        n = (y1 - y0).days
        mid = (datetime.date(y + 1 if sh else y, 1 if sh else 7, 1) - y0).days
        if any(a.get(k) is None for k in range(n)):
            continue
        s0, run = None, 0
        for k in range(n):
            run = run + 1 if a[k] > T else 0
            if run >= N:
                s0 = k - N + 1
                break
        if s0 is None:
            out.append((n, n))
            continue
        e0, run = n, 0
        for k in range(max(mid, s0 + N), n):
            run = run + 1 if a[k] < T else 0
            if run >= N:
                e0 = k - N + 1
                break
        out.append((s0, e0))
    return out


def median(L):
    L = sorted(L)
    n = len(L)
    if not n:
        return None
    return L[(n - 1) // 2] if n % 2 else int(math.floor((L[n // 2 - 1] + L[n // 2]) / 2.0 + 0.5))


def gsl(daily, lat):
    Y = gsl_years(daily, lat)
    if not Y:
        return None
    return {'s': median([a for a, b in Y]), 'e': median([b for a, b in Y]), 'years': len(Y), 'sh': lat < 0}


def doy(date, sh):
    Y, M, D = int(date[:4]), int(date[5:7]), int(date[8:10])
    sy = Y - 1 if (sh and M < 7) else Y
    return (datetime.date(Y, M, D) - datetime.date(sy, 7 if sh else 1, 1)).days


def in_leaf(G, date):
    if not G:
        return True
    d = doy(date, G['sh'])
    return G['s'] <= d < G['e']


def day_name(d, sh):
    t = datetime.date(2025, 7 if sh else 1, 1) + datetime.timedelta(days=d)
    return '%d %s' % (t.day, t.strftime('%B'))
