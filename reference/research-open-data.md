# Research: open public data for building on real sites (V132 to V134)

The owner: "i just want free stuff", then "i want to be able to access as much open public data as
possible since i saw a lot of apps able to do that to build BIM easy".

Every source below is free. None needs an API key, except where a row says so. The points come from
search summaries and the providers' published terms; check each provider's current terms when its
phase starts.

## The catalogue

| Data | Source | Licence and terms | Into the app as |
|---|---|---|---|
| Street map | OpenStreetMap standard tiles, `tile.openstreetmap.org/{z}/{x}/{y}.png` | ODbL data. Light use only: show "© OpenStreetMap contributors", send a proper Referer, cache tiles, never bulk-download | A basemap under the plan and the 3D ground |
| Satellite | Esri World Imagery (`server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}`) | No key. Attribution "Esri, Maxar, Earthstar Geographics". Terms favour non-commercial use | A basemap style, labelled as such |
| US imagery and topo | USGS National Map | Public domain | A basemap style for US sites |
| Address search | Nominatim (OSM) | One request per second, with attribution; no search-as-you-type | Sets the site's latitude and longitude |
| Neighbouring buildings | OSM via the Overpass API | ODbL. `height` or `building:levels` where tagged | Context massing on a locked Context layer |
| Roads, water, parks, trees | OSM via Overpass | ODbL | Context linework and areas |
| Terrain | AWS Terrain Tiles (Terrarium; SRTM, GMTED, national DEMs) | Free, no key; attribution per source | A TIN for V108's terrain, so contours and earthwork work at once |
| More footprints | Microsoft Global ML Building Footprints; Overture Maps buildings | ODbL / CDLA Permissive 2.0 | Bulk files, imported where OSM is thin |
| Parcels, zoning, flood, heritage | Public ArcGIS REST, WMS and WFS servers: councils, FEMA's flood map (NFHL), state planning portals | Varies by publisher, usually open with attribution | Data layers by URL, with presets; a parcel becomes a property line |
| Climate and sun | NASA POWER (API, no key); EPW files (climate.onebuilding.org) | Open | Feeds the sun and shadow, later solar and energy |
| Your own files | GeoJSON, KML/KMZ, CSV of points; DXF and IFC already | Yours | Local and offline |

## The phases

- **V132 The map.**
  - Street and satellite basemaps.
  - Address search.
  - Georeferencing from the latitude, longitude and true north the project already stores.
  - A cached tile store, and an attribution footer.
- **V133 Site context in one click.**
  - From the site's extent, fetch OSM buildings, roads, water and trees (Overpass), and the terrain
    (AWS Terrain Tiles).
  - Neighbours come in as massing at their OSM height, or levels × 3 m. The terrain becomes a TIN.
- **V134 Data layers.**
  - A Data section with the catalogue's presets, plus any ArcGIS REST, WMS, WFS or GeoJSON URL.
  - Click a feature to read it. A parcel becomes a property line. Layers stay live.

## Ground rules

- **Offline-first.** The network is used only when the person asks for it.
- **Saved with the project.** Fetched data is cached and saved in the project, so a project opens
  offline.
- **Attribution travels.** Every source's licence and attribution go with its data, into sheets
  and exports too.
- **No silent proxy.** A server that does not allow browser access (no CORS headers) is reported
  by name. It is never quietly routed through a proxy.
- **If the app is ever sold or heavily used,** OSM's and Esri's tile terms stop fitting. Move to
  OpenFreeMap (free vector tiles) or a provider with a key. The tile URL is a setting.

## Sources

- [OSM tile usage policy](https://operations.osmfoundation.org/policies/tiles/), [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)
- [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)
- [AWS Terrain Tiles / OpenFreeMap terrain](https://geodataviewer.com/datasets/dem/openfreemap-terrain/)
- [Microsoft Global ML Building Footprints](https://github.com/microsoft/GlobalMLBuildingFootprints), [Microsoft building footprint data (OSM wiki)](https://wiki.openstreetmap.org/wiki/Microsoft_Building_Footprint_Data)
- [Overture Maps](https://overturemaps.org/)
- [NASA POWER](https://power.larc.nasa.gov/), [climate.onebuilding.org](https://climate.onebuilding.org/)
