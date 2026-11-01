"""standards_reference.py -- V167's standards registry worked out again from its sources.

What each record holds, as its source states it (reference/research-standards-registry.md says
where each was read, and at what level), with the arithmetic the app's values come from; the
constants the analyses had before V167, read from the kept build; and the rules by which the app
picks the edition in force for a place and a date, written again here so the suite can ask the app
the same question for many places and dates and compare.

Nothing here is the app's code: a value that moved into the registry wrong, an edition said to be
in force where it is not, or a level overstated is a difference the suite reports.
"""
import json, math, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEPT = ROOT / 'Phase' / 'canvas_v10.html.bak_phase167_pre'

LONDON = ['gb-lnd', 'gb-bdg', 'gb-bne', 'gb-bex', 'gb-ben', 'gb-bry', 'gb-cmd', 'gb-cry', 'gb-eal', 'gb-enf', 'gb-gre', 'gb-hck', 'gb-hmf',
          'gb-hry', 'gb-hrw', 'gb-hav', 'gb-hil', 'gb-hns', 'gb-isl', 'gb-kec', 'gb-ktt', 'gb-lbh', 'gb-lew', 'gb-mrt', 'gb-nwm', 'gb-rdb',
          'gb-ric', 'gb-swk', 'gb-stn', 'gb-twh', 'gb-wft', 'gb-wnd', 'gb-wsm']   # the City and the 32 boroughs, ISO 3166-2:GB

# ---- the sources, in numbers ----
# TfL, Assessing transport connectivity in London (2015), 2.5: walks of up to 640 m to a bus and 960 m to
# rail at 4.8 km/h; reliability 2 minutes (bus), 0.75 (rail, Tube, tram); Table 2.2 the bands.
TFL_SPEED_KMH = 4.8
TFL_SPEED = TFL_SPEED_KMH * 1000 / 60            # 80 m a minute
TFL_BUS_M, TFL_RAIL_M = 640, 960
TFL_BANDS = [[2.5, '1a'], [5, '1b'], [10, '2'], [15, '3'], [20, '4'], [25, '5'], [40, '6a'], [None, '6b']]
# FHWA, Highway Functional Classification 2023, Tables 3-5 and 3-6: AADT, rural and urban
FHWA = {'interstate': ('Interstate or motorway', (12000, 34000), (35000, 129000)),
        'freeway': ('Other freeway or expressway', (4000, 18500), (13000, 55000)),
        'opa': ('Other principal arterial', (2000, 8500), (7000, 27000)),
        'minor_art': ('Minor arterial', (1500, 6000), (3000, 14000)),
        'major_col': ('Major collector', (300, 2600), (1100, 6300)),
        'minor_col': ('Minor collector', (150, 1110), (1100, 6300)),
        'local': ('Local road', (15, 400), (80, 700))}
OSM_FC = {'motorway': 'interstate', 'trunk': 'freeway', 'primary': 'opa', 'secondary': 'minor_art', 'tertiary': 'major_col',
          'unclassified': 'minor_col', 'residential': 'local', 'living_street': 'local'}
# LEED v4 ND, Connected and Open Community: within a quarter mile (400 m); Case 1 90, Case 2 140
# intersections a square mile; the credit's Table 1: 300 to 400 one point, over 400 two
LEED = {'radius': 400, 'case1': 90, 'case2': 140, 'pt1': 300, 'pt2': 400}
# WHO global air quality guidelines (2021), Table 0.1, PM2.5 in ug/m3
WHO = {'pm25_year': 5, 'pm25_24h': 15, 'pm25_it1_year': 35, 'pm25_24h_it1': 75, 'pm25_24h_it2': 50, 'pm25_24h_it3': 37.5, 'pm25_24h_it4': 25}
# 2010 ADA Standards 403.3 and 405.2: 1:20, 1:48, 1:12
ADA = {'walk_slope': 100 / 20, 'cross_slope': 100 / 48, 'ramp_slope': 100 / 12}
# Manual for Streets 4.4.1: facilities within about 800 m; North Norfolk's guide: 800 m to a school, 400 m to green space
GUIDES = {'shops': (800, 'P'), 'school': (800, 'S'), 'green': (400, 'S')}
# LTS, Furth, Mekuria and Nixon 2016: an unsignalized crossing without a median refuge, by speed row and lanes column
XING = [[1, 2, 4], [1, 2, 4], [2, 3, 4], [3, 4, 4]]
# WHO Regional Office for Europe, Environmental Noise Guidelines for the European Region (2018), 3.1:
# road traffic below 53 dB Lden (53.3 rounded) and 45 dB Lnight
WHO_NOISE = {'road_lden': 53, 'road_lnight': 45}
# CRTN (1988), as DataKustik's documentation gives its range
CRTN_RANGE = 300
# 44 CFR 64.3(a)(1): the zones the layer groups
FEMA_GROUPS = ['floodway', 'coastal', 'sfha', 'x02', 'undetermined']

# every topic: kind, anywhere, catalogue; each edition: id, published, status, the adoption (place, from, to),
# its source level, and the values the app reads (name: value, unit, level when it differs from the source's)
TOPICS = {
    'tfl.ptal': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='tfl.ptal.2015', pub='2015-04-23', st='current', lv='P', adopt=[(k, '2015-04-23', None) for k in LONDON],
             v={'walk_bus': (TFL_BUS_M / TFL_SPEED, 'min'), 'walk_rail': (TFL_RAIL_M / TFL_SPEED, 'min'), 'walk_tram': (TFL_RAIL_M / TFL_SPEED, 'min', 'A'),
                'k_bus': (2, 'min'), 'k_rail': (0.75, 'min'), 'bands': (TFL_BANDS, None)})]),
    'walk.speed': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='walk.speed.1', pub='', st='current', lv='P', adopt=[('*', None, None)], v={'m_min': (TFL_SPEED, 'm/min')})]),
    'guides.walk': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='guides.walk.2007', pub='2007', st='current', lv='P', adopt=[('gb-eng', '2007', None), ('gb-wls', '2007', None)],
             v={k: (v[0], 'm', v[1]) for k, v in GUIDES.items()})]),
    'leed.nd': dict(kind='rating', anywhere=True, cat=False, eds=[
        dict(id='leed.nd.v4', pub='2018-07-02', st='current', lv='P', adopt=[('*', '2014', None)],
             v={'radius': (400, 'm'), 'case1': (90, 'per sq mi'), 'case2': (140, 'per sq mi'), 'pt1': (300, 'per sq mi'), 'pt2': (400, 'per sq mi')})]),
    'fhwa.fc': dict(kind='classification', anywhere=True, cat=False, eds=[
        dict(id='fhwa.fc.2023', pub='2023-02', st='current', lv='P', adopt=[('us', '2023-02', None)],
             v={'classes': ({k: {'name': n, 'r': list(r), 'u': list(u)} for k, (n, r, u) in FHWA.items()}, None)})]),
    'app.roads': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.roads.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),   # its values: the kept build's
    'crtn': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='crtn.1988', pub='1988', st='current', lv='S', adopt=[('gb', '1988', None)], v={'range': (CRTN_RANGE, 'm')})]),
    'who.noise': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='who.noise.2018', pub='2018', st='current', lv='P', adopt=[], v={k: (v, 'dB') for k, v in WHO_NOISE.items()})]),
    'lts.2012': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='lts.2012', pub='2012', st='current', lv='S', adopt=[('*', '2012', None)], v={})]),
    'lts.xing2016': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='lts.xing2016', pub='2016', st='current', lv='S', adopt=[('*', '2016', None)], v={'table': (XING, None)})]),
    'who.aqg': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='who.aqg.2021', pub='2021', st='current', lv='P', adopt=[('*', '2021', None)], v={k: (v, 'ug/m3') for k, v in WHO.items()})]),
    'fema.zones': dict(kind='classification', anywhere=True, cat=False, eds=[
        dict(id='fema.zones.cfr', pub='1976-10-26', st='current', lv='P', adopt=[('us', '1976-10-26', None)], v=None)]),
    'land.slope': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='land.slope.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v={'b1': (5, '%'), 'b2': (10, '%'), 'b3': (15, '%'), 'b4': (25, '%')})]),
    # AMENDED FOR V172: the site analysis tools -- Pennsylvania's site capacity calculation, Chalfont's section 440-17 as
    # read (Zoneomics' copy, a secondary source, so S), and the app's working set for constraints and opportunities
    'land.site_capacity': dict(kind='code', anywhere=True, cat=False, eds=[
        dict(id='land.site_capacity.chalfont', pub='', st='current', lv='S', adopt=[('us-pa:chalfont', None, None)],
             v={'floodplain': (1, 'ratio'), 'slope_lo': (15, '%'), 'slope_hi': (25, '%'), 'slope_a': (0.7, 'ratio'), 'slope_b': (0.85, 'ratio'),
                'forest': (0.5, 'ratio'), 'forest_with': (0.8, 'ratio'), 'pond': (1, 'ratio'), 'waters': (1, 'ratio'), 'wetland': (1, 'ratio')})]),
    'terrain.slope_bands': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='terrain.slope_bands.1', pub='', st='current', lv='P', adopt=[('*', None, None)], v={'bands': ([0, 2, 5, 8.33, 15, 25, 50], '%')})]),
    'ibc.occupant_load': dict(kind='code', anywhere=True, cat=False, eds=[
        dict(id='ibc.2021.1004.5', pub='2020-10', st='current', lv='S', adopt=[('us-pa', '2026-01-01', None)], v=None),
        dict(id='ibc.2018.1004.5', pub='2017-08', st='superseded', lv='S', adopt=[], v=None)]),
    'asce7.combos': dict(kind='code', anywhere=True, cat=False, eds=[
        dict(id='asce7.22', pub='2021-12', st='current', lv='S', adopt=[], v={'c1_d': (1.4, 'x'), 'c2_d': (1.2, 'x'), 'c2_l': (1.6, 'x')})]),
    'app.context': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.context.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    'app.climate': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.climate.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    # AMENDED FOR V172b: comfort and design days for Ladybug -- UTCI's scale and range, as utci.org's program (UTCI_a002,
    # its ReadMe: air -50 to +50 C, the radiant temperature 30 C below to 70 C above it, wind at 10 m 0.5 to 17 m/s,
    # vapour pressure under 50 hPa) and its poster's ten categories give them; ASHRAE 55-2023's PMV limits as Ladybug and
    # pythermalcomfort apply them (PPD at most 10%, still air 0.1 m/s; the standard is sold, so S); the app's comfort
    # assumptions; ASHRAE's design conditions (2025 Handbook, chapter 14, as a station's DDY carries them)
    'utci': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='utci.a002', pub='2009-10', st='current', lv='P', adopt=[('*', '2009', None)],
             v={'bands': ([-40, -27, -13, 0, 9, 26, 32, 38, 46], 'C'), 'ta_lo': (-50, 'C'), 'ta_hi': (50, 'C'), 'dtr_lo': (-30, 'C'),
                'dtr_hi': (70, 'C'), 'va_lo': (0.5, 'm/s'), 'va_hi': (17, 'm/s'), 'pa_hi': (50, 'hPa')})]),
    'ashrae.55': dict(kind='standard', anywhere=True, cat=False, eds=[
        dict(id='ashrae.55.2023', pub='2023', st='current', lv='S', adopt=[('*', '2023', None)], v={'ppd': (10, '%'), 'still': (0.1, 'm/s')})]),
    'app.comfort': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.comfort.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    'ashrae.dd': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='ashrae.dd.2025', pub='2025', st='current', lv='S', adopt=[('*', '2025', None)], v={'heating': ([99.6, 99], '%'), 'cooling': ([0.4, 1, 2], '%')})]),
    # AMENDED FOR V168: land and green -- LBCS (adopted nowhere as a rule), Spacematrix, 3-30-300 and the app's land
    # settings; their values are held to their sources by tests/land_use_reference.py in V168's suite
    'lbcs.activity': dict(kind='classification', anywhere=True, cat=False, eds=[
        dict(id='lbcs.activity.apa', pub='', st='current', lv='P', adopt=[], v=None)]),
    'spacematrix': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='spacematrix.2010', pub='2010', st='current', lv='P', adopt=[('*', '2010', None)], v={})]),
    'green.33300': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='green.33300.2024', pub='2024', st='current', lv='P', adopt=[('*', '2024', None)],
             v={'trees': (3, 'trees'), 'canopy': (30, '%'), 'walk': (300, 'm'), 'green_min': (0.5, 'ha')})]),
    # AMENDED FOR V172: the app's working set for constraints and opportunities, before app.land as the registry has it
    'app.synthesis': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.synthesis.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    'app.land': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.land.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    # AMENDED FOR V169: the assets' sizes -- people, the wheelchair user, cycles, parking, design vehicles, trees, the
    # growing season and the app's own shapes; their values are held to their sources by tests/assets_reference.py
    'body.us': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='body.us.2018', pub='2021-01', st='current', lv='P', adopt=[('us', '2021-01', None)], v=None)]),
    'body.hidh': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='body.hidh.rev1', pub='2014-06-05', st='current', lv='P', adopt=[('*', '2014', None)], v=None)]),
    'wheel.awmp': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='wheel.awmp.2010', pub='2010-12-31', st='current', lv='P', adopt=[('*', '2010', None)], v=None)]),
    'ada.space': dict(kind='code', anywhere=True, cat=False, eds=[
        dict(id='ada.space.2010', pub='2010-09-15', st='current', lv='P', adopt=[('us', '2012-03-15', None)], v=None)]),
    'mutcd.walk': dict(kind='standard', anywhere=True, cat=False, eds=[
        dict(id='mutcd.walk.11r1', pub='2025-12', st='current', lv='P', adopt=[('us', '2025-12', None)], v=None)]),
    'ltn.cycle': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='ltn.cycle.2020', pub='2020-07', st='current', lv='P', adopt=[('gb-eng', '2020-07', None)], v=None)]),
    'parking.bay': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='parking.bay.mfs2007', pub='2007', st='current', lv='P', adopt=[('gb-eng', '2007', None), ('gb-wls', '2007', None)], v=None)]),
    'utd.trees': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='utd.trees.2016', pub='2016', st='current', lv='P', adopt=[('*', '2016', None)], v=None)]),
    'etccdi.gsl': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='etccdi.gsl.27', pub='', st='current', lv='P', adopt=[('*', None, None)], v=None)]),
    'aashto.vehicles': dict(kind='standard', anywhere=True, cat=False, eds=[
        dict(id='aashto.vehicles.7', pub='2018', st='current', lv='P', adopt=[('us', None, None)], v=None)]),
    'app.assets': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.assets.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    # AMENDED FOR V171: traffic and people -- the IDM, MOBIL, the timing manual, the MUTCD's intervals, Florida's K,
    # NCHRP 255, San Diego's rates, Helbing and Molnar's walkers, SUMO's rules and the app's traffic settings; their
    # values are held to their sources by tests/traffic_reference.py in V171's suite
    'idm.car': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='idm.car.2010', pub='2010', st='current', lv='P', adopt=[('*', '2010', None)], v=None)]),
    'mobil': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='mobil.2007', pub='2007', st='current', lv='P', adopt=[('*', '2007', None)], v=None)]),
    'stm.signal': dict(kind='guideline', anywhere=True, cat=False, eds=[
        dict(id='stm.signal.2008', pub='2008-06', st='current', lv='P', adopt=[('us', '2008-06', None)], v=None)]),
    'mutcd.signal': dict(kind='standard', anywhere=True, cat=False, eds=[
        dict(id='mutcd.signal.11', pub='2023-12', st='current', lv='P', adopt=[('us', '2023-12', None)], v=None)]),
    'fdot.k': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='fdot.k.2014', pub='2014-01', st='current', lv='P', adopt=[('us-fl', '2014-01', None)], v=None)]),
    'nchrp255': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='nchrp255.1982', pub='1982-12', st='current', lv='P', adopt=[('*', '1982-12', None)], v=None)]),
    'sd.trips': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='sd.trips.2003', pub='2003-05', st='current', lv='P', adopt=[('us-ca:san diego', '2003-05', None)], v=None)]),
    'hm.walk': dict(kind='data', anywhere=True, cat=False, eds=[
        dict(id='hm.walk.1995', pub='1995', st='current', lv='S', adopt=[('*', '1995', None)], v=None)]),
    'sumo.rules': dict(kind='method', anywhere=True, cat=False, eds=[
        dict(id='sumo.rules.docs', pub='', st='current', lv='S', adopt=[('*', None, None)], v=None)]),
    'app.traffic': dict(kind='assumption', anywhere=True, cat=False, eds=[
        dict(id='app.traffic.1', pub='', st='current', lv='A', adopt=[('*', None, None)], v=None)]),
    # the catalogue: in force where they are adopted, not applied by the app yet
    'pa.ucc': dict(kind='code', anywhere=False, cat=True, eds=[dict(id='pa.ucc.2026', pub='2025-11-07', st='current', lv='P', adopt=[('us-pa', '2026-01-01', None)], v={})]),
    'ibc': dict(kind='code', anywhere=False, cat=True, eds=[dict(id='ibc.2021', pub='2020-10', st='current', lv='P', adopt=[('us-pa', '2026-01-01', None)], v={}),
                                                         dict(id='ibc.2024', pub='2023', st='current', lv='S', adopt=[], v={})]),
    'ada.2010': dict(kind='code', anywhere=False, cat=True, eds=[dict(id='ada.2010', pub='2010-09-15', st='current', lv='P', adopt=[('us', '2012-03-15', None)],
                                                                   v={k: (round(v, 2), '%') for k, v in ADA.items()})]),
    'a117.1': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='a117.1.2026', pub='2026', st='announced', lv='P', adopt=[], v={})]),
    'ashrae.90.1': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='ashrae.90.1.2025', pub='2025', st='current', lv='P', adopt=[], v={})]),
    'mutcd': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='mutcd.11r1', pub='2025-12', st='current', lv='P', adopt=[('us', '2025-12', None)], v={})]),
    'aashto.greenbook': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='aashto.greenbook.7', pub='2018', st='current', lv='P', adopt=[], v={})]),
    'penndot.dm2': dict(kind='manual', anywhere=False, cat=True, eds=[dict(id='penndot.dm2.unread', pub='', st='current', lv='U', adopt=[], v={})]),   # a search summary is not a source
    'aashto.lrfd': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='aashto.lrfd.10', pub='2024', st='current', lv='P', adopt=[], v={}),
                                                                     dict(id='aashto.lrfd.8', pub='2017', st='superseded', lv='P', adopt=[('us-pa', '2020-07-01', None)], v={})]),
    'penndot.dm4': dict(kind='manual', anywhere=False, cat=True, eds=[dict(id='penndot.dm4.2019', pub='2019-12-30', st='current', lv='P', adopt=[('us-pa', '2020-07-01', None)], v={})]),
    'asce7': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='asce7.22.cat', pub='2021-12', st='current', lv='P', adopt=[], v={})]),
    'aci318': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='aci318.unread', pub='', st='current', lv='U', adopt=[], v={})]),
    'aisc360': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='aisc360.unread', pub='', st='current', lv='U', adopt=[], v={})]),
    'faa.ac150_5300_13': dict(kind='standard', anywhere=False, cat=True, eds=[dict(id='faa.ac150_5300_13b.c1', pub='2024-08-16', st='current', lv='P', adopt=[('us', '2024-08-16', None)], v={})]),
}
# the hosts the sources are linked on
SOURCE_HOSTS = {'content.tfl.gov.uk', 'assets.publishing.service.gov.uk', 'www.gbcbrasil.org.br', 'www.fhwa.dot.gov', 'doku.datakustik.com', 'iris.who.int',
                'www.ecfr.gov', 'www.ada.gov', 'www.pacodeandbulletin.gov', 'www.asce.org', 'www.iccsafe.org', 'www.ashrae.org', 'mutcd.fhwa.dot.gov',
                'store.transportation.org', 'www.dot.state.pa.us', 'docs.penndot.pa.gov', 'www.concrete.org', 'www.aisc.org', 'www.faa.gov',
                'www.planning.org', 'doi.org',   # AMENDED FOR V168: APA's LBCS; the DOIs of Buildings and Cities and of Browning et al.
                'www.cdc.gov', 'www.nasa.gov', 'idea.ap.buffalo.edu', 'www.fs.usda.gov', 'etccdi.pacificclimate.org',   # AMENDED FOR V169: the assets' sources
                'arxiv.org', 'mtreiber.de', 'ops.fhwa.dot.gov', 'www.fdot.gov', 'onlinepubs.trb.org', 'www.sandiego.gov', 'github.com',   # AMENDED FOR V171: traffic's sources
                'www.zoneomics.com',   # AMENDED FOR V172: Chalfont's site capacity calculation, in Zoneomics' copy of the code
                'www.utci.org'}   # AMENDED FOR V172b: UTCI's program and poster


# ---- the constants before V167, from the kept build ----
def _js(lit):
    """a JavaScript literal of numbers, strings, arrays and objects with bare keys, to Python"""
    t = lit.replace('Infinity', 'null')
    t = re.sub(r"'((?:[^'\\]|\\.)*)'", lambda m: json.dumps(m.group(1).replace("\\'", "'")), t)
    t = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:', r'\1"\2":', t)
    return json.loads(t)


def kept():
    """{name: value} for every constant V167 moved into the registry, as the build before it had them"""
    s = KEPT.read_text(encoding='utf-8')
    out = {}

    def one(name, src):
        m = re.search(r'\bvar (?:[A-Za-z0-9_]+=[^,;]+,)*?' + name + r'=', src) or re.search(r'[,\s]' + name + r'=', src)
        if not m:
            raise ValueError('no ' + name + ' in the kept build')
        i = m.end()
        if src[i] not in '[{':
            return _js(re.match(r'[-0-9.]+', src[i:]).group(0))
        depth, q, j = 0, None, i
        while True:   # the literal to its matching bracket, quotes respected
            c = src[j]
            if q:
                if c == '\\':
                    j += 1
                elif c == q:
                    q = None
            elif c in '\'"':
                q = c
            elif c in '[{':
                depth += 1
            elif c in ']}':
                depth -= 1
                if depth == 0:
                    return _js(src[i:j + 1])
            j += 1
    for n in ('BIM_ACC_SPEED', 'BIM_ACC_IXR', 'BIM_ACC_LEED', 'BIM_CLIM_BASE', 'BIM_CLIM_CALM', 'BIM_CLIM_WIND_BINS', 'BIM_CLIM_WHO24', 'BIM_CLIM_WHO_YEAR',
              'BIM_CLIM_COMFORT', 'BIM_DG_CRTN_MAX', 'BIM_DG_ROADS', 'BIM_MV_XTAB', 'BIM_MV_GUIDE', 'BIM_MV_PTAL_WALK', 'BIM_MV_PTAL_K', 'BIM_MV_PTAL',
              'BIM_LAND_SLOPE', 'BIM_SLOPE_BANDS', 'BIM_CTX_LEVEL_H', 'BIM_CTX_DEFAULT_H', 'BIM_CTX_DECK', 'BIM_CTX_DECK_T', 'BIM_CTX_PIER',
              'BIM_CTX_TREE_H', 'BIM_CTX_TOWER_H', 'BIM_CTX_LINE_H', 'BIM_ROAD_W', 'BIM_OCC_LOADS', 'BIM_COMBOS'):
        out[n] = one(n, s)
    # the speed of a street with none mapped, by class, and WHO's first interim target (a status edge)
    m = re.search(r"return \{v:rc\?rc\.v:\(base==='service'\?(\d+):\(base==='track'\?(\d+):(\d+)\)\),src:'assumed'\};", s)
    out['SPEED_ELSE'] = [int(m.group(1)), int(m.group(2)), int(m.group(3))]
    m = re.search(r'if\(mean>(\d+)\)st=\'critical\';', s)
    out['WHO_IT1'] = int(m.group(1))
    m = re.search(r"\[\[BIM_CLIM_WHO24,'WHO 24-hour guideline, '\+BIM_CLIM_WHO24\],\[([\d.]+),'WHO interim target 4, [\d.]+'\],\[([\d.]+),'Interim target 3, [\d.]+'\],"
                  r"\[([\d.]+),'Interim target 2, [\d.]+'\],\[([\d.]+),'Interim target 1, [\d.]+'\]\]", s)
    out['WHO_IT24'] = [float(m.group(i)) for i in (1, 2, 3, 4)] if m else None
    m = re.search(r"WHO advises road noise below (\d+) dB Lden", s)
    out['WHO_NOISE'] = int(m.group(1))
    return out


# the constants V167 moved into the registry: none is left in the build
MOVED = ['BIM_ACC_SPEED', 'BIM_ACC_IXR', 'BIM_ACC_LEED', 'BIM_CLIM_BASE', 'BIM_CLIM_CALM', 'BIM_CLIM_WIND_BINS', 'BIM_CLIM_WHO24', 'BIM_CLIM_WHO_YEAR',
         'BIM_CLIM_COMFORT', 'BIM_DG_CRTN_MAX', 'BIM_DG_ROADS', 'BIM_MV_XTAB', 'BIM_MV_GUIDE', 'BIM_MV_PTAL_WALK', 'BIM_MV_PTAL_K', 'BIM_MV_PTAL',
         'BIM_LAND_SLOPE', 'BIM_SLOPE_BANDS', 'BIM_OCC_LOADS', 'BIM_COMBOS', 'BIM_CTX_LEVEL_H', 'BIM_CTX_DEFAULT_H', 'BIM_CTX_DECK', 'BIM_CTX_DECK_T',
         'BIM_CTX_PIER', 'BIM_CTX_TREE_H', 'BIM_CTX_TOWER_H', 'BIM_CTX_LINE_H', 'BIM_ROAD_W']
# a standard's number beside its unit, as the build before V167 wrote them, and as a sentence might again
PHRASES = [(r'\b80 ?m a minute', 'the walking speed'), (r'4\.8 ?km/h', 'the walking speed in km/h'), (r'\b(8|12)-minute walk', "PTAL's walks"),
           (r'\b8 minutes to a bus|station within 12', "PTAL's walks"), (r"LEED ND[^'\n]{0,60}?\b(90|140|300|400)\b", "LEED's thresholds"),
           (r'per square mile within a quarter mile', "LEED's radius"), (r'below 53 dB', "WHO's road noise"), (r'45 dB Lnight', "WHO's night noise"),
           (r'WHO (19|20)\d\d (24-hour|guidelines)', "WHO's edition"), (r'interim target \d, \d', "WHO's interim targets"), (r'base 18\b', 'the degree-day base'),
           (u'20\u201327 \u00b0C', 'the comfort band'), (r'\(0 to 2%, 2 to 5%', "the terrain's bands"), (r'steeper than 15%', 'the slope classes'),
           (r'under 5%|at 15% or more', 'the slope classes'), (r'CRTN holds to 300', "CRTN's range"), (r'mean>35\b', "WHO's first interim target")]


def scan(text):
    """(constants left, phrases left) in a build's source, outside the registry and its comments"""
    a, b = text.find('  var BIM_STD=['), text.find('  var BIM_STD_LV=')
    body = re.sub(r'/\*.*?\*/', '', text[:a] + text[b:] if a >= 0 and b > a else text, flags=re.S)
    return ([n for n in MOVED if re.search(r'\b%s\b' % n, body)], [(w, len(re.findall(p, body))) for p, w in PHRASES if re.search(p, body)])


def fc_mid(a):
    """the middle of an AADT range to the nearest 10, as Math.round rounds it"""
    return int(math.floor((a[0] + a[1]) / 20 + 0.5)) * 10


# ---- the edition in force ----
def path(place):
    """most specific first: the city, the districts, the region, the country, then international"""
    P = []
    if place:
        if place.get('city'):
            P.append((place.get('r') or place['cc']) + ':' + place['city'].lower())
        for k in ('d8', 'd6', 'r'):
            if place.get(k):
                P.append(place[k])
        P.append(place['cc'])
    P.append('*')
    return P


def in_force(a, d):
    _, f, t = a
    return (not f or f <= d) and (not t or d < t)


def resolve(tid, place, d, pick=None):
    """(edition id, how, place key) for the topic, as the registry's rules give it"""
    T = TOPICS[tid]
    if pick:
        for e in T['eds']:
            if e['id'] == pick:
                return e['id'], 'chosen', None
    for k in path(place):
        best = None
        for e in T['eds']:
            for a in e['adopt']:
                if a[0] == k and in_force(a, d) and (best is None or (a[1] or '') > (best[1][1] or '')):
                    best = (e, a)
        if best:
            return best[0]['id'], ('assumption' if T['kind'] == 'assumption' else ('international' if k == '*' else 'adopted')), k
    if T['anywhere'] and T['eds']:
        ok = [e for e in T['eds'] if not e['pub'] or e['pub'] <= d]
        if ok:
            b = ok[0]
            for e in ok[1:]:
                if (e['pub'] or '') > (b['pub'] or ''):
                    b = e
        else:
            b = min(T['eds'], key=lambda e: e['pub'] or '')
        return b['id'], 'outside', None
    return None, 'none', None


# places to ask about: (name, place) -- as the address search gives them, ISO 3166-2 lower case
PLACES = [
    ('no place', None),
    ('Westminster, London', {'cc': 'gb', 'r': 'gb-eng', 'd8': 'gb-wsm', 'city': 'City of Westminster'}),
    ('Camden, London', {'cc': 'gb', 'r': 'gb-eng', 'd8': 'gb-cmd', 'city': 'London'}),
    ('Leeds, England', {'cc': 'gb', 'r': 'gb-eng', 'd8': 'gb-lds', 'city': 'Leeds'}),
    ('Cardiff, Wales', {'cc': 'gb', 'r': 'gb-wls', 'd8': 'gb-crf', 'city': 'Cardiff'}),
    ('Edinburgh, Scotland', {'cc': 'gb', 'r': 'gb-sct', 'd8': 'gb-edh', 'city': 'Edinburgh'}),
    ('Philadelphia, Pennsylvania', {'cc': 'us', 'r': 'us-pa', 'city': 'Philadelphia'}),
    ('Pittsburgh, Pennsylvania', {'cc': 'us', 'r': 'us-pa', 'city': 'Pittsburgh'}),
    ('New York, New York', {'cc': 'us', 'r': 'us-ny', 'city': 'New York'}),
    ('Munich, Bavaria', {'cc': 'de', 'r': 'de-by', 'city': 'Munich'}),
]
# Nominatim's answers, their address parts as the search gives them (read 2026-10-17 for Trafalgar Square,
# 1401 John F. Kennedy Boulevard and Market Square, Pittsburgh)
NOM_WESTMINSTER = {'square': 'Trafalgar Square', 'quarter': 'Westminster', 'suburb': 'Covent Garden', 'city': 'City of Westminster', 'ISO3166-2-lvl8': 'GB-WSM',
                   'state': 'England', 'ISO3166-2-lvl4': 'GB-ENG', 'postcode': 'WC2', 'country': 'United Kingdom', 'country_code': 'gb'}
NOM_PHILADELPHIA = {'house_number': '1401', 'road': 'John F. Kennedy Boulevard', 'suburb': 'Center City', 'city': 'Philadelphia', 'county': 'Philadelphia County',
                    'state': 'Pennsylvania', 'ISO3166-2-lvl4': 'US-PA', 'postcode': '19102', 'country': 'United States', 'country_code': 'us'}
NOM_PITTSBURGH = {'road': 'Market Square', 'neighbourhood': 'Fifth & Forbes', 'quarter': 'Downtown', 'city': 'Pittsburgh', 'county': 'Allegheny County',
                  'state': 'Pennsylvania', 'ISO3166-2-lvl4': 'US-PA', 'postcode': '15262', 'country': 'United States', 'country_code': 'us'}
DATES = ['2010-06-01', '2014-06-01', '2020-06-30', '2020-07-01', '2024-02-29', '2024-03-01', '2025-12-31', '2026-01-01', '2026-10-18']
