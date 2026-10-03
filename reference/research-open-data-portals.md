# Research: finding open data (V135)

The owner pointed at GeoLibre (geolibre.app, github.com/opengeos/GeoLibre) and asked to "copy and
paste" it in. This note records what was taken, what was not, and why.

## GeoLibre, and why it cannot be pasted in

- **What it is:** a free, open-source GIS by Qiusheng Wu (opengeos), MIT licence. It runs on the
  desktop (Tauri), in the browser and inside Jupyter.
- **How it is built:** an npm monorepo of about 2,000 TypeScript files.
  - React for the interface, Zustand for the state, MapLibre GL for the map.
  - DuckDB-WASM to read files, a Python sidecar for processing, and a build step.
- **This app** is one ES5 HTML file with its own WebGL renderer and no build. GeoLibre's code
  cannot run in it as it is: pasting it in would mean replacing the renderer the BIM tools draw
  with.
- **What does carry over** is code written against plain web APIs, and data. The MIT licence allows
  both, with the copyright notice kept.

## What V135 takes from GeoLibre (commit 4ec853f)

| GeoLibre file | What it holds | In V135 |
|---|---|---|
| `packages/plugins/src/plugins/us-federal-gis-catalogs.ts` | 24 federal portals by department (USGS, FEMA, NOAA, Census, EPA ...) | `BIM_DATA_PORTALS`, the federal groups |
| `us-state-gis-catalogs.ts` | 68 state GIS portals, every state | one group per state |
| `us-local-gis-catalogs.ts` | 146 city and county portals (ArcGIS Hub or Socrata) | one group per state's cities and counties |
| `arcgis-hub-api.ts` | ArcGIS Online item search, Hub site catalog groups, service layers | `bimHubSearchUrl`, `bimHubGroups`, `bimFindAdd` |
| `socrata-api.ts` | Socrata Discovery API search, spatial datasets only | `bimSocrataSearchUrl`, `bimSocrataItem` |

`tools/geolibre_portals.py` reads the three catalog files and writes
`Phase/geolibre_portals_phase135.json`, which patch 135a embeds. Run it again on a newer GeoLibre
checkout to refresh the list. GeoLibre's `npm run check:gis-portals` is how its authors find dead
portals.

## How a search works

- **An ArcGIS Hub portal** (most cities and states).
  - The Hub site's item (`/sharing/rest/content/items/<site>/data`) names the groups its catalog
    is made of: under `catalogV2.scopes.item.filters[].predicates[].group` on current sites, or
    `catalog.groups` on older ones. These are read once per site, and kept for the session.
  - Then one search goes to `https://www.arcgis.com/sharing/rest/search`:
    - the words, with Lucene syntax dropped;
    - the types read here (Feature Service, Map Service, GeoJson);
    - the groups, or the organisation (`orgid:`) when the site cannot be read or has none;
    - `access:public`;
    - the site's box (`bbox`), when Near the site only is ticked.
- **A Socrata portal** (Chicago, Los Angeles, New York and others).
  - `https://api.us.socrata.com/api/catalog/v1`, scoped by `search_context` and `domains`.
  - Its tables are read in batches of 100, and only datasets with a geometry column are kept. It
    reads up to five batches, until it has 20.
  - A dataset's addresses are built from the portal's own host, never taken from the answer.
- **More results** continues where the search stopped (Hub's `nextStart`, Socrata's offset).

## What a result becomes

Every result is added as a V134 data layer, credited to its portal:
- **A layer** (`.../FeatureServer/3`, `.../MapServer/28`): as it is.
- **A whole service:** its `?f=json` lists its layers.
  - Group layers and imagery are left out.
  - With one feature layer, that one is added.
  - With several, they are listed under the result to add one by one. GeoLibre adds only the
    first.
- **A GeoJSON item:** its data (`/sharing/rest/content/items/<id>/data`), kept to the area.
- **A Socrata dataset:** a new data-layer kind, `socrata`.
  - It is asked for the site's box only: `$where=within_box(<geometry column>, north, west,
    south, east)` and `$limit=2000`.
  - A dataset whose geometry column is not a plain name is asked for its first 2000, kept to the
    area.

## Which portal

- **A first guess from the site's address,** the one Find (V132) keeps from Nominatim.
  - Its city or county portal when one is named in it (Philadelphia).
  - Else its state's (Harrisburg, Pennsylvania: PennShare).
  - Outside the US, none.
- **Then the last one picked,** remembered in the browser.

## Not taken, and why

- **MapLibre GL, vector tiles, 3D Tiles and the photorealistic city meshes.**
  - The first three need GeoLibre's map engine.
  - Google's and Cesium's photorealistic 3D Tiles need an API key and billing.
- **DuckDB, GeoParquet, Shapefiles, the Python sidecar, processing tools:** a build, WASM and a
  server.
- **Colour by attribute, with a legend:** next, as the lens (V136), drawn in this app's renderer.

## Checked from the sandbox

None of the portals, nor arcgis.com or the Socrata API, can be reached from the build sandbox (its
proxy refuses them). The request shapes follow GeoLibre's code, which its web build uses from the
browser, so both APIs answer with CORS. The suite answers every request with a routed fixture of
the same shape.
