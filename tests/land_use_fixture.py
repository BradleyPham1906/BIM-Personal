"""land_use_fixture.py -- the V168 suite's neighbourhood: V166's (tests/movement_fixture.py, its streets,
stops and walk times) with the land added to the context, each piece there to test one rule.

The site's lot is V161's, so the site's centre is at x 30, z -25 (model metres, x east, z south) and the
400 m square runs from x -170 to 230 and z -225 to 175. Every area's corners are on multiples of 5 m, and a
wood's x on even metres and its z on odd ones, so no grid cell's centre sits on an edge: the land use
grid's centres are 2.5 m off multiples of 5; the canopy's 2 m grid, from the centre less 500 m, has its
centres at odd x and even z.

What is added to V164's context (site_analysis_fixture.py):
- land use areas: a residential area with a school's grounds inside it (the smaller area wins), grass
  inside it (it takes the residential class) and a bakery (a building's own use wins); a retail area
  with a hotel (LBCS's transient living: residential) and an untagged building (the area's class); an
  industrial area with industrial=port (port before industrial: movement); a plain industrial area; a
  place of worship's grounds (assembly); a car park (movement); farmland; a brownfield over the sheds
  (no activity); grass on its own (no activity);
- homes mapped as a multipolygon round a hole (the hole says nothing);
- a supermarket over a car park mapped as an area under it, the building larger than the area: its
  own use wins all the same;
- buildings: an office with building:levels 5 and a height of 20 m (5 storeys, not 6); a kiosk 2.5 m
  tall (one storey, not none); a building of two parts, one standing on the other at 6 m with
  building:min_level 2 (its floors count, its ground does not); apartments round a courtyard (the
  courtyard is not built on);
- trees: one with diameter_crown 12; one behind East Hall (not seen); one 172 m off (beyond 100 m);
- woods and a forest, outside the square but in the neighbourhood (canopy);
- parks: a garden of 0.49 ha nearer than Mill Park (under 0.5 ha); a private park of 0.51 ha (not
  public);
- a council's zoning layer (ArcGIS): R6 west of x 40, C4 to x 150, M1 east of it, with a unique value
  renderer on ZONE and 20% transparency. store['zn'] 'nodraw' answers its description without a
  renderer, 'fail' answers it 500."""
import json, pathlib, sys
from urllib.parse import unquote

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import movement_fixture as MFX        # noqa: E402
import site_analysis_fixture as SFX   # noqa: E402
from bim_phase133_site_context_browser_tests import m2g, G, ring   # noqa: E402

SITE = (30.0, -25.0)
box = SFX.box

# areas: (id, tags, outer ring) -- in the order the context answers them, which is the app's order
AREAS = [
    (8101, {'landuse': 'residential', 'name': 'West Homes'}, box(-165, -220, -90, -100)),
    (8102, {'amenity': 'school', 'name': 'West School'}, box(-150, -200, -120, -170)),
    (8103, {'landuse': 'grass'}, box(-110, -140, -95, -110)),
    (8104, {'landuse': 'retail', 'name': 'Market Row'}, box(-85, -220, 25, -150)),
    (8105, {'landuse': 'industrial', 'industrial': 'port', 'name': 'Old Dock'}, box(100, -220, 225, -160)),
    (8106, {'landuse': 'industrial', 'name': 'Works Yard'}, box(100, -155, 160, -100)),
    (8107, {'amenity': 'school', 'name': 'East School'}, box(-165, -95, -100, -30)),
    (8108, {'amenity': 'place_of_worship', 'name': 'St Anne'}, box(-45, 100, -15, 140)),
    (8109, {'amenity': 'parking', 'name': 'Car Park C'}, box(150, 20, 190, 60)),
    (8110, {'landuse': 'farmland'}, box(150, 100, 225, 170)),
    (8111, {'landuse': 'brownfield'}, box(190, -40, 225, 0)),
    (8112, {'landuse': 'grass'}, box(-165, 120, -155, 140)),
    (8113, {'natural': 'wood', 'name': 'West Wood'}, box(-240, -95, -180, -35)),
    (8114, {'landuse': 'forest'}, box(240, 105, 300, 165)),
    (8115, {'leisure': 'park', 'name': 'Small Garden'}, box(-10, 100, 60, 170)),
    (8116, {'leisure': 'park', 'name': 'Private Green', 'access': 'private'}, box(-165, -25, -105, 60)),
    (8117, {'amenity': 'parking', 'name': 'Roof Park'}, box(-50, -130, -30, -110)),   # under Big Shop: the building's own use wins
]
# a multipolygon area: homes round a hole the land use is not said in
MP_AREAS = [(8601, {'type': 'multipolygon', 'landuse': 'residential', 'name': 'Ring Homes'}, box(100, -50, 180, 10), [box(120, -30, 160, -10)])]
SMALL_GARDEN_M2 = 70 * 70   # 0.49 ha
PRIVATE_M2 = 60 * 85         # 0.51 ha

# buildings: (id, tags, outer, inner rings)
BUILDINGS = [
    (8201, {'building': 'hotel', 'tourism': 'hotel', 'name': 'Rest Inn', 'height': '15'}, box(-60, -200, -40, -170), []),
    (8202, {'building': 'yes', 'shop': 'bakery', 'name': 'Bakery', 'height': '6'}, box(-130, -130, -115, -115), []),
    (8203, {'building': 'yes', 'name': 'Plain Store', 'height': '7'}, box(0, -200, 20, -180), []),
    (8204, {'building': 'office', 'building:levels': '5', 'height': '20', 'name': 'Office Five'}, box(110, -90, 140, -60), []),
    (8205, {'building': 'kiosk', 'height': '2.5', 'name': 'Kiosk'}, box(-5, -140, 5, -130), []),
    (8206, {'building': 'supermarket', 'name': 'Big Shop', 'height': '8'}, box(-60, -140, -10, -100), []),   # larger than the car park mapped under it
]
PART_HOUSE = (8301, {'building': 'yes', 'name': 'Part House', 'height': '15'}, box(-20, 60, 20, 90))
PARTS = [
    (8302, {'building:part': 'yes', 'height': '12', 'building:levels': '4'}, box(-20, 60, 0, 90)),
    (8303, {'building:part': 'yes', 'height': '15', 'min_height': '6', 'building:levels': '5', 'building:min_level': '2'}, box(0, 60, 20, 90)),
]
COURT = (8401, {'type': 'multipolygon', 'building': 'apartments', 'building:levels': '6', 'height': '20', 'name': 'Court House'},
         box(60, 100, 120, 160), [box(75, 115, 105, 145)])

TREES = [
    (8501, {'natural': 'tree', 'height': '10', 'diameter_crown': '12'}, -40, 20),
    (8502, {'natural': 'tree', 'height': '8'}, 95, 0),        # behind East Hall from the site
    (8503, {'natural': 'tree', 'height': '8'}, -120, 60),     # 172 m off
]

# the council's zoning layer
ZN_URL = 'https://gis.example-council.gov/arcgis/rest/services/Planning/Zoning/FeatureServer/0'
ZN_HOST = 'https://gis.example-council.gov/**'
DISTRICTS = [('R6', box(-400, -400, 40, 400), 2.0), ('C4', box(40, -400, 150, 400), 3.4), ('M1', box(150, -400, 400, 400), 2.0)]
RENDERER = {'type': 'uniqueValue', 'field1': 'ZONE', 'fieldDelimiter': ', ',
            'defaultSymbol': {'type': 'esriSFS', 'style': 'esriSFSSolid', 'color': [200, 200, 200, 255], 'outline': {'type': 'esriSLS', 'style': 'esriSLSSolid', 'color': [110, 110, 110, 255], 'width': 0.4}},
            'defaultLabel': 'Other',
            'uniqueValueInfos': [
                {'value': 'R6', 'label': 'Residence R6', 'symbol': {'type': 'esriSFS', 'style': 'esriSFSSolid', 'color': [255, 255, 0, 255], 'outline': {'type': 'esriSLS', 'style': 'esriSLSSolid', 'color': [120, 120, 0, 255], 'width': 0.4}}},
                {'value': 'C4', 'label': 'Commercial C4', 'symbol': {'type': 'esriSFS', 'style': 'esriSFSSolid', 'color': [255, 0, 0, 204], 'outline': {'type': 'esriSLS', 'style': 'esriSLSNull'}}},
                {'value': 'M1', 'label': 'Manufacturing M1', 'symbol': {'type': 'esriSFS', 'style': 'esriSFSDiagonalCross', 'color': [160, 32, 240, 255], 'outline': {'type': 'esriSLS', 'style': 'esriSLSSolid', 'color': [80, 16, 120, 255], 'width': 0.4}}}]}
TRANSPARENCY = 20


def context():
    """V164's context and the land, as Overpass answers it"""
    base = SFX.context()

    def way(i, tags, pts):
        return {'type': 'way', 'id': i, 'tags': tags, 'geometry': G(ring(pts))}
    E = list(base['elements'])
    for i, t, pts in AREAS:
        E.append(way(i, t, pts))
    for i, t, outer, inner in MP_AREAS:
        E.append({'type': 'relation', 'id': i, 'tags': t, 'members':
                  [{'type': 'way', 'ref': i * 10, 'role': 'outer', 'geometry': G(ring(outer))}] +
                  [{'type': 'way', 'ref': i * 10 + 1 + k, 'role': 'inner', 'geometry': G(ring(r))} for k, r in enumerate(inner)]})
    for i, t, pts, inner in BUILDINGS:
        E.append(way(i, t, pts))
    E.append(way(PART_HOUSE[0], PART_HOUSE[1], PART_HOUSE[2]))
    for i, t, pts in PARTS:
        E.append(way(i, t, pts))
    i, t, outer, inner = COURT
    E.append({'type': 'relation', 'id': i, 'tags': t, 'members':
              [{'type': 'way', 'ref': i * 10, 'role': 'outer', 'geometry': G(ring(outer))}] +
              [{'type': 'way', 'ref': i * 10 + 1 + k, 'role': 'inner', 'geometry': G(ring(r))} for k, r in enumerate(inner)]})
    for i, t, x, z in TREES:
        lon, lat = m2g(x, z)
        E.append({'type': 'node', 'id': i, 'lat': lat, 'lon': lon, 'tags': t})
    return {'version': 0.6, 'generator': 'Overpass API (fixture)', 'elements': E}


def districts_geojson():
    F = []
    for k, (zn, pts, far) in enumerate(DISTRICTS):
        F.append({'type': 'Feature', 'id': k + 1, 'properties': {'OBJECTID': k + 1, 'ZONE': zn, 'FAR': far},
                  'geometry': {'type': 'Polygon', 'coordinates': [[list(m2g(p[0], p[1])) for p in ring(pts)]]}})
    return {'type': 'FeatureCollection', 'features': F}


def layer_json(mode):
    js = {'currentVersion': 11.1, 'id': 0, 'name': 'Zoning', 'type': 'Feature Layer', 'geometryType': 'esriGeometryPolygon'}
    if mode != 'nodraw':
        js['drawingInfo'] = {'renderer': RENDERER, 'transparency': TRANSPARENCY, 'labelingInfo': None}
    return js


def route_handler(store):
    """V166's handler, the context answered with the land; the council's layer answered too"""
    base = MFX.route_handler(store)

    async def handle(route):
        u = route.request.url
        if '/api/interpreter' in u and '["building"]' in unquote(u):
            store.setdefault('hits', []).append(('ctx', u))
            await route.fulfill(status=200, body=json.dumps(context()), headers=SFX.HDR)
            return
        if 'gis.example-council.gov' in u:
            store.setdefault('hits', []).append(('zn', u))
            mode = store.get('zn')
            if '/query' in u:
                await route.fulfill(status=200, body=json.dumps(districts_geojson()), headers=SFX.HDR)
            elif mode == 'fail':
                await route.fulfill(status=500, body='error', headers=SFX.HDR)
            else:
                await route.fulfill(status=200, body=json.dumps(layer_json(mode)), headers=SFX.HDR)
            return
        await base(route)
    return handle


HOSTS = MFX.HOSTS + (ZN_HOST,)
