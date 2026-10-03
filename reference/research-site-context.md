# Research: site context in one click (V133)

The owner wants "as much open public data as possible" to build on real sites, and the map "just
like how giraffe do". Giraffe, TestFit and Forma all start a project the same way: draw or find the
site, and the buildings, roads and ground around it arrive with it. V133 does that from free
sources only.

## Sources

| What | Source | Terms |
|---|---|---|
| Buildings, roads, water, parks and woods, trees | OpenStreetMap through the Overpass API (`overpass-api.de/api/interpreter`) | ODbL: show "© OpenStreetMap contributors". Overpass asks for fewer than 10,000 requests a day and allows browser access (CORS). One request per press is far inside that. The server is a setting, so a mirror can take over. |
| Ground heights | AWS Terrain Tiles, Terrarium encoding (`s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`) | Free, no key. Mapzen built them from SRTM, GMTED2010, ETOPO1, USGS 3DEP (NED) and other national models. Credit "Terrain Tiles: Mapzen, AWS" and the sources. |

Checked from this machine (2026-10-03):
- **Terrarium answers with `Access-Control-Allow-Origin: *`.** It also exposes
  `x-amz-meta-x-imagery-sources`, the sources of each tile, such as `srtm/N27E086.tif`, which V133
  keeps with the terrain.
- **The decoding is `elevation = R·256 + G + B/256 − 32768` metres.** Checked on the tile under
  Everest at zoom 12: 8,753 m at the summit pixel. SRTM at about 30 m a pixel smooths the
  8,849 m peak.
- **Overpass could not be reached from this sandbox,** whose proxy refuses it. Its CORS support
  and response format are from its documentation, and the suite answers it with a recorded-shape
  fixture.

## What comes in, and as what

- **Buildings** (`building=*` ways and multipolygon relations).
  - Each becomes a solid extruded from its footprint, pinned, on a *Context buildings* layer.
  - Height comes from `height` (metres, or feet when marked `ft` or `'`). Failing that, from
    `building:levels` × 3 m. Failing both, 6 m, and the building says its height was assumed.
  - A multipolygon's outer ring is extruded. Its courtyards are filled, and it says so.
  - They stand on the lowest level, on the same flat ground as the basemap. The terrain's height
    under each is kept on it, for a later 3D ground.
- **Roads** (`highway=*`) become their centrelines, as open sketches on *Context roads*, with
  their tags (name, lanes, width).
- **Water** (`natural=water`, `water=*`, `waterway=*`): areas become closed sketches, holes
  marked, and rivers and streams become lines, on *Context water*.
- **Green** (`leisure=park`, `landuse=grass|forest|meadow|recreation_ground|village_green`,
  `natural=wood|scrub|grassland`) becomes closed sketches on *Context green*.
- **Trees** (`natural=tree` nodes) become points on *Context trees*.
- **Terrain** becomes a V108 surface, a TIN with its contours and earthwork.
  - It is sampled on a grid of at most 25 × 25 points across the area, by bilinear interpolation
    of the tile pixels.
  - The elevation at model y 0 is the survey base's, when V108 set one. Otherwise it is the
    ground's at model 0,0, kept on the site so the next fetch lands on the same datum.

The layers sit under one *Context* layer, so one switch hides them all. Every object keeps its
source, credit, OSM type, id and tags. Properties shows them, and GeoJSON export writes them with
the credit.

## The area

A square around the site, its half-size the *Context radius* (150 m by default, 50 to 1,000 m),
plus half the property line's extent when there is one:
- centred on the property line(s), when there are any;
- otherwise on model 0,0.

It is turned to longitude and latitude through V132's georeferencing, so true north is honoured.

## Rules (from `research-open-data.md`)

- **One request per press, and nothing until asked.** A second press while one runs is refused.
- **Saved with the project.** Context is ordinary objects, so the project opens offline.
- **A fresh fetch replaces the context of the kinds it fetches,** in one undo step with the new
  data. Remove Context takes all of it away.
- **A failure is named.** Busy (HTTP 429 or 504), unreachable (offline, or no browser access), or
  a bad answer: each source reports its own. What did come is still placed.

## Not in V133

- Terrain in 3D, and the map draped on it. V108's surfaces are plan-only, and the buildings stay
  on the flat ground under the flat basemap.
- Building parts (`building:part`), roof shapes, and courtyards cut out.
- Microsoft and Overture footprints (bulk files, a later import).

## Sources

- [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API), [Overpass QL](https://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_QL), [Key:height](https://wiki.openstreetmap.org/wiki/Key:height), [Key:building:levels](https://wiki.openstreetmap.org/wiki/Key:building:levels)
- [Terrain Tiles on AWS](https://registry.opendata.aws/terrain-tiles/), [tilezen/joerd: formats and data sources](https://github.com/tilezen/joerd/blob/master/docs/formats.md)
