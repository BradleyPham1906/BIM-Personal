"""geolibre_portals.py -- turn GeoLibre's US open-data portal catalogs into V135's BIM_DATA_PORTALS.

GeoLibre (https://github.com/opengeos/GeoLibre, MIT licence, (c) 2026 Qiusheng Wu) lists US federal,
state and local open-data portals in packages/plugins/src/plugins/us-{federal,state,local}-gis-catalogs.ts.
This reads those three files and prints one JavaScript array, ES5, for canvas_v10.html:

  [[group, [[name, host, siteId, orgId, socrata], ...]], ...]

  group    "Federal: <department>", "<State>: state" or "<State>: cities and counties"
  host     the portal's home (an ArcGIS Hub site, an ArcGIS Online organisation, or a Socrata domain)
  siteId   the Hub site item, whose catalog groups scope a search ('' when there is none)
  orgId    the ArcGIS organisation, the fallback scope ('' for Socrata)
  socrata  1 when the portal is Socrata, searched through the Socrata Discovery API

Usage: python3 tools/geolibre_portals.py <geolibre checkout> > portals.js
"""
import json, re, sys, pathlib

D = pathlib.Path(sys.argv[1]) / 'packages/plugins/src/plugins'
S = r'"((?:[^"\\]|\\.)*)"'


def entries(body):
    out = []
    # helper calls: hub(name, host, site, org) / socrata(name, domain) / org(name, urlKey, orgId)
    for m in re.finditer(r'\b(hub|socrata|org)\(\s*' + S + r'(?:\s*,\s*' + S + r')?(?:\s*,\s*' + S + r')?(?:\s*,\s*' + S + r')?\s*,?\s*\)', body):
        k, a = m.group(1), [m.group(i) for i in range(2, 6)]
        if k == 'hub':
            out.append((m.start(), [a[0], a[1], a[2], a[3], 0]))
        elif k == 'socrata':
            out.append((m.start(), [a[0], a[1], '', '', 1]))
        else:
            out.append((m.start(), [a[0], a[1] + '.maps.arcgis.com', '', a[2], 0]))
    # object literals: { name, url, siteId?, orgId?, socrataDomain? }
    for m in re.finditer(r'\{\s*name:\s*' + S + r'(.*?)\}', body, re.S):
        f = dict(re.findall(r'(\w+):\s*' + S, m.group(2)))
        host = re.sub(r'^https://', '', f.get('url', '')).rstrip('/')
        if f.get('socrataDomain'):
            out.append((m.start(), [m.group(1), f['socrataDomain'], '', '', 1]))
        elif host:
            out.append((m.start(), [m.group(1), host, f.get('siteId', ''), f.get('orgId', ''), 0]))
    return [e for _, e in sorted(out)]


def sets(fname, fn, label):
    t = (D / fname).read_text()
    t = t[t.index('export const'):]
    starts = [m for m in re.finditer(r'\b' + fn + r'\(\s*' + S + r'\s*,\s*' + S + r'\s*,\s*\[', t)]
    res = []
    for i, m in enumerate(starts):
        body = t[m.end():starts[i + 1].start() if i + 1 < len(starts) else len(t)]
        es = entries(body)
        if es:
            res.append((label(m.group(2)), es))
    return res


groups = sets('us-federal-gis-catalogs.ts', 'department', lambda n: 'Federal: ' + n)
st = sets('us-state-gis-catalogs.ts', 'state', lambda n: n + ': state')
lo = sets('us-local-gis-catalogs.ts', 'state', lambda n: n + ': cities and counties')
# each state's portals sit next to its cities and counties
names = sorted(set(g.split(':')[0] for g, _ in st + lo))
by = dict(st + lo)
for n in names:
    for g in (n + ': state', n + ': cities and counties'):
        if g in by:
            groups.append((g, by[g]))
for g, es in groups:
    for e in es:
        assert re.match(r'^[a-z0-9.\-]+$', e[1]), e
        assert e[2] == '' or re.match(r'^[0-9a-f]{32}$', e[2]), e
        assert e[3] == '' or re.match(r'^[0-9A-Za-z]{16}$', e[3]), e
        assert e[4] or e[2] or e[3], e
n = sum(len(es) for _, es in groups)
sys.stderr.write('%d groups, %d portals\n' % (len(groups), n))
print(json.dumps([[g, es] for g, es in groups], ensure_ascii=True, separators=(',', ':')))
