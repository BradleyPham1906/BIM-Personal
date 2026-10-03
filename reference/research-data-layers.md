# Research: data layers (V134)

The owner wants "as much open public data as possible". After the basemap (V132) and OSM context
(V133), the next layer of truth about a site is its public records: parcels, zoning and flood
zones. These are published by councils, states and agencies on GIS servers, free and keyless.

## The servers, and what V134 reads

| Kind | Recognised by | Asked as | Notes |
|---|---|---|---|
| ArcGIS REST layer (FeatureServer or MapServer) | `.../FeatureServer/<n>` or `.../MapServer/<n>` | `<url>/query?where=1=1&geometry=<w,s,e,n>&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&outSR=4326&resultRecordCount=2000&f=geojson` | Most US councils, FEMA, the Census (TIGERweb). An error arrives as `{"error":{"message":...}}` with HTTP 200, and is shown as the server's own words. `exceededTransferLimit` means more than 2000 were there. A service URL without a layer number is refused, saying to add it. |
| OGC WFS | `service=WFS` in the address, or a path ending `/wfs` | `GetFeature`, version 2.0.0, `outputFormat=application/json`, `srsName=CRS:84`, the box in `CRS:84`, `count=2000` | GeoServer, QGIS Server, many European portals. CRS:84 is longitude-first, so axis order is not a question. The address must name `typeNames` (or `typeName`). |
| GeoJSON | anything else | the file as it is, kept to features touching the area | Open-data portals (Socrata, CKAN, ArcGIS Hub downloads). |

WMS (pictures, not features) is not in V134. It needs a blended raster pass over the basemap, a
smaller and separate step. Clicking a feature, and a parcel becoming a property line, need
features.

## Presets

Each preset is a ready-made address. The owner works in Philadelphia, so:
- **FEMA National Flood Hazard Layer, flood zones (US):**
  `https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/28`. It carries `FLD_ZONE`
  (A, AE, X ...) and `ZONE_SUBTY`.
- **Philadelphia parcels (Water Department):**
  `https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/PWD_PARCELS/FeatureServer/0`.
- **Philadelphia zoning base districts:**
  `https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/Zoning_BaseDistricts/FeatureServer/0`.

None of these could be reached from the build sandbox: its proxy refuses all three hosts. The
addresses are from the publishers' open-data catalogues, so treat them as unverified until the
owner's own screen shows them. A wrong or moved address fails with the server and its HTTP status
named, and any other address can be pasted in.

## How the data is kept

- **The layers** (name, kind, address, colour, shown or not, credit) live in `A3D.site.dataLayers`,
  so adding and removing one is an undo step and goes with the project.
- **The features** (GeoJSON geometry in longitude and latitude, and their attributes, at most 2000
  a layer) live in `A3D.dataFeatures`, by layer.
  - They are saved with the project, the browser store and the project tabs, so a project opens
    offline.
  - They are kept out of the undo snapshots, so thousands of parcels do not make every undo step
    heavy. An undone layer's features stay stored and come back with a redo; Remove clears them.
- **The area** is V133's: the context radius around the property lines, or around model 0,0.

## On screen

- **Drawing.** Each shown layer is drawn on the plan in its colour: areas faintly filled and
  outlined (holes respected), lines, points.
  - The geometry is placed through V132's georeferencing, cached until the site's place or true
    north changes.
  - It is not drawn on paper, the same rule as the basemap.
- **Clicking.** A click that hits nothing in the model reads the data under it: points first, then
  lines, then the smallest area. The feature's attributes show in Properties.
  - An area can become a property line, from its outer ring, as one undo step.
- **Credits.** Each layer's credit joins the credit line while it is shown.

## Rules (from `research-open-data.md`)

- One request per press (Add, Refresh), and none until then.
- Failures are named: the server, and its HTTP status, its own error message, "does not read", or
  "could not be reached (offline, or it does not allow browser access)". Nothing is proxied.
- Longitude and latitude only: a projected answer is refused, as V132's import does.
