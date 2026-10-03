# Research: the map (V132)

The owner wants the map "just like how giraffe do", with free sources only ("i just want free
stuff"). This note sets out what V132 builds on, and what it leaves for V133 and V134. The sources
and their terms are catalogued in `research-open-data.md`.

## What Giraffe does, and what V132 keeps

- **The map comes first.** Giraffe opens on a map. You search an address, and the project sits on
  the imagery or street map, so the site's context is under everything you draw.
  - V132 keeps that: a basemap under the plan and under the 3D ground, and an address search.
  - V132 drops one thing: the map is **off** until someone turns it on, so the app stays offline
    until asked.
- **Styles.** Street, satellite, and the owner's own tiles.
  - V132 has street (OpenStreetMap), satellite (Esri World Imagery), and a custom tile URL with its
    own credit. The custom URL covers USGS, a council's tiles, or a paid provider, with no code
    change.
- **GeoJSON in and out.** Giraffe's apps, and its SDK, speak GeoJSON.
  - V132 imports GeoJSON and KML as site data, and exports the model's plan as GeoJSON. This is
    the format V134's data layers and a later app SDK will use.

## Georeferencing

- **The latitude and longitude the project already stores are model 0,0.** These are the V107
  sun settings. It is the same convention as the V108 survey base point, which is the survey
  coordinate that sits at model 0,0.
- **True north (V103) turns the model on the map.** A true azimuth `az` points along model
  `x = sin(az+tn), z = -cos(az+tn)`. A model point `(x, z)` is therefore this far east and north
  of the origin:

  ```
  E = x cos tn + z sin tn
  N = x sin tn - z cos tn
  ```

  The inverse is:

  ```
  x = E cos tn + N sin tn
  z = E sin tn - N cos tn
  ```
- **Metres to degrees use the WGS84 ellipsoid's radii at the site's latitude.** A sphere would
  be up to 0.7% off north-south, about 70 cm across a 100 m site.
  - The meridian radius `M = a(1-e²)/(1-e² sin²φ)^1.5` gives `Δlat = N/M`.
  - The prime-vertical radius `Nr = a/√(1-e² sin²φ)` gives `Δlon = E/(Nr cos φ)`.
  - `a = 6378137`, `e² = 0.00669437999014`.
  - Over a site, a few kilometres at most, the error of this local tangent plane is millimetres.
- **Tiles are Web Mercator (EPSG:3857), on the slippy-map tile scheme:**

  ```
  x = (lon+180)/360 · 2^z
  y = (1 - ln(tan φ + sec φ)/π)/2 · 2^z
  ```

  The inverse is `φ = atan(sinh(π(1-2y/2^z)))`. A tile's four corners are placed on the model
  through the inverse above, so the tiles turn with true north.

## Which tiles

- **Zoom.** It comes from the view's metres per pixel, `mpp = dist/(1.2·H)`, which holds exactly
  in plan and at the target in 3D:

  ```
  z = round(log2(156543.034 · cos φ / mpp))
  ```

  It is clamped to 1 to 19, and lowered one step at a time while the view would need more than 80
  tiles.
- **Extent.**
  - In plan, the four screen corners on the ground.
  - In 3D, a 7×7 grid of screen points on the ground. Points past three camera distances from the
    target are pulled in to that distance, so a view toward the horizon does not ask for the
    world.
- **Loading.**
  - At most 12 tile requests are in flight at once, nearest the centre first.
  - About 400 tiles are kept in memory, and the least recently drawn go first.
  - While a tile loads, its parent (up to four levels up) is drawn stretched, so panning shows
    a blurred map rather than holes.
- **Failures are said, not hidden.**
  - A tile is requested with `crossOrigin = "anonymous"`. A server that sends no CORS header
    therefore fails to load, rather than tainting the canvas.
  - The credit line names the host and how many tiles did not load ("offline, or the server does
    not allow browser access").
  - Nothing is proxied.

## Drawing

- **WebGL.** One textured quad per tile on the lowest level's plane, just below it.
  - It is drawn first and without writing depth, so every solid draws over it.
  - Opacity mixes the tile toward the background colour in the shader, with no blending state.
  - The same view and projection matrices as the solids are used, so the map and the model
    cannot drift apart.
- **2D canvas** (the presentation appearance and the fallback renderer). In plan only, each tile
  is drawn with an affine transform from three of its corners. In 3D the 2D renderer draws no map.
- **Never on paper.** Sheets, PNG, PDF, SVG and DXF leave the basemap out in V132. A plot with the
  basemap would have to carry its credit, and that is better done once the data layers (V134) need
  the same thing.

## Address search: Nominatim

- `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=…`
- Nominatim's policy allows one request a second, no autocomplete, and attribution. So there is
  one request per Find, and a second Find within a second is refused with the reason.
- The first result's latitude and longitude become the site's, so model 0,0 is that place, and
  the street map comes on if the map was off. The address found is kept on the site.

## GeoJSON and KML

- **Import (GEOIMPORT, `.geojson`, `.json`, `.kml`).**
  - Polygons become closed sketches, one per ring, holes included. Lines become open sketches,
    and points become points.
  - Everything goes on a "Site data" layer. Each feature's properties are kept on the object and
    shown in a Site Data group in Properties.
  - Coordinates must be longitude and latitude (WGS84, RFC 7946). A file in a projected system, or
    one whose `crs` names something else, is refused with that reason, not placed wrongly.
  - With no site latitude and longitude yet, the data's centre becomes the site's.
  - KMZ (zipped) is refused with the reason: unzip it first.
- **Export (GEOEXPORT).** These go out:
  - rooms, floors, roofs and ceilings, columns, property lines, masses (the footprint, sliced at
    the first floor), and closed sketches, as polygons;
  - walls (centreline) and open sketches as lines;
  - points as points.

  Each carries its name, kind, layer, level, usage and area. Coordinates are rounded to 8 decimals,
  about 1 mm. Imported site data goes back out with the properties it came with.

## Sources

- [Slippy map tilenames (OSM wiki)](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames)
- [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/), [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)
- [RFC 7946 GeoJSON](https://datatracker.ietf.org/doc/html/rfc7946), [OGC KML 2.2](https://www.ogc.org/standard/kml/)
- [WGS84 (NGA TR8350.2)](https://earth-info.nga.mil/), for the ellipsoid constants
- Giraffe: `research-giraffe.md`
