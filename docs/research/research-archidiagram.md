# Research: Archi Diagram, animated site analysis (2026-10-19)

The owner (2026-10-19): "this app has the site analysis tool that match my intention:
https://archidiagram.com/ it allows the analysis layer to be animated. take a look at their build and
capabilities."

Read here on 2026-10-19, from its own hosts: the site's pages as text, and the web app's page and
JavaScript bundles as text (never run). Archi Diagram is closed, commercial software by Febhouse
(Nam Nguyen); as with Giraffe (`research-giraffe.md`), ideas only: nothing of its code, symbols,
templates or text is taken. Third-party screenshots are not kept.

## 1. What it is

| Fact | Source | Level |
|---|---|---|
| An educational site and four tools by Febhouse: three SketchUp extensions (Sun Diagram, Dynamic Symbols, Shadow Slice) and a web app; Canva templates with animated symbols | https://archidiagram.com/ and its pages | P |
| The web app: an address in, then a satellite map at 1:1, 3D context buildings, terrain and contours, a sun path and shadows (time zone and daylight saving worked out), wind arrows from climate data, a library of animated symbols dragged onto the site, light and dark themes, touch on an iPad; images up to 5K, PDFs and MP4 video; cloud saves and share links; glTF/GLB models imported (Pro) | https://archidiagram.com/web-app/ | P |
| Express Mode: one click from an address to a solar and wind diagram | the same | P |
| Its tutorial for a dynamic site analysis: location, contours and distance rings, the sun path sized to a radius up to 1500 m, a massing model imported as GLB, motion symbols placed (they animate on placement; turned off while editing for speed), colours and line weights by style, a plan image laid on the terrain, export of stills, batches and MP4 | https://archidiagram.com/dynamic-site-analysis-diagram/ | P |
| Dynamic Symbols (SketchUp): swap a symbol's shape or colour keeping its position, size and rotation; animation by three SketchUp scenes exported as a video; uses: circulation and pedestrian flows, ventilation streams, zoning markers, section annotations, reels | https://archidiagram.com/dynamic-symbols/ | P |
| Sun Diagram (SketchUp): a 3D sun path from the model's location or coordinates, daylight saving, real-time time sliders, a HUD with place, date, time and UTC, batch-exported shadow sequences (4K and 9:16), diagram styles | https://archidiagram.com/sun-diagram/ | P |
| Shadow Slice (SketchUp): walls and roofs cut away from the camera but kept solid to the sun, for interior daylight in perspective sections | https://archidiagram.com/shadow-slice/ | P |
| Prices: free tiers; the web app's free tier limits symbols to 15 and the sun path's months; Pro plugins $12 a year or $29 for life | the pages above | P |

## 2. How the web app is built (its bundles read as text)

| Fact | Where | Level |
|---|---|---|
| React, three.js through react-three-fiber, a Vite (rolldown) build; instanced meshes | `app.archidiagram.com/assets/index-*.js`, `Studio-*.js` | P |
| Satellite images and terrain from Mapbox (a token, Mapbox's terrain-rgb); context buildings from the Overpass API; wind, temperature and humidity from Open-Meteo's ERA5 archive (hourly, a year); cloud saves and sign-in by Supabase; an AI help desk (Dify, Google Gemini); payments by Lemon Squeezy | the bundles' URLs and credits | P |
| Video: frames at 30 a second, the animation's clock set to each frame's time before it is drawn, encoded by the browser's hardware encoder (WebCodecs) into MP4 with mp4-muxer; where that fails, the canvas recorded by MediaRecorder (MP4, else WebM VP9) at 35 Mbit/s; PDFs by jsPDF | `Studio-*.js` | P |
| How a symbol moves: a flow line's dashes march along it (the dash offset moves with time and the symbol's speed); a symbol draws itself on and off in a loop, by a clip in its shader: most grow from their centre, arrows and wind wipe along their direction; the loop reveals over 40% of it, holds to 50%, erases to 90%, then rests | `Studio-*.js` | P |

Its data choices differ from the owner's rule: Mapbox needs a key (this app uses OpenStreetMap's and
Esri's keyless tiles, and AWS Terrain Tiles). Open-Meteo's ERA5 archive is the source this app's
climate already reads (V159).

## 3. Against this app

| Archi Diagram | This app |
|---|---|
| Address to context, terrain, contours | Analyze site (V164), the context (V133, V157), the ground and contours (V165) |
| Sun path, shadows on chosen dates, DST | The sun path on a dome and the shadows on three dates (V164), sun hours (V143); the time zone from the climate |
| Wind arrows from climate data | Winds by season and the strongest (V164), wind roses (V159) |
| Distance rings, compass | V164's compass and rings |
| Symbol library, dragged, recoloured | The diagram engine's live, editable elements (V164); no free symbol library yet |
| **Animated symbols and flows** | **None: every analysis is drawn still** |
| **The sun and shadows moving through a day** | **Shadows for a time set by hand** |
| **MP4 video, batch stills** | **Sheets and boards print (V122, V162); no video** |
| Plan image on the terrain | Image notes; the basemap (V132) |
| GLB import | Later: model import (glTF) |
| Light and dark, iPad | Light and dark, phone, tablet and computer (V147 to V150) |
| Cloud saves and share links | Local, saved with the project; Hub H4 later |

The gap is motion: the analysis layers this app already works out (walk times, transit catchments,
winds, flow lines, the sun, traffic and pedestrians in V170) drawn moving, and exported as video.

## 4. What an animation phase would take (a sketch for the owner's decision)

- **One clock** for every animated layer: the wall clock while working, a frame clock while exporting, so
  each video frame is exact (as Archi Diagram does), paused when the page is hidden.
- **Motion on the analyses already drawn**, from the diagram engine's elements: marching dashes along
  flow lines, walk routes and transit lines; winds as arrows drawn on along their direction and as
  streamlines; walk-time rings growing outward; the sun moving along its path with the shadows; the
  analysis layers revealed one after another. Each element's motion a style setting (on, speed), so
  the still drawing stays exactly as it is.
- **Video export** with the browser's own encoder: WebCodecs where it is, its MP4 container written by
  the app (a small ISO base media file writer, no dependency), MediaRecorder where it is not; and batch
  stills. Light by design, with the frame budget the simulation (V170) sets.
- **V170's traffic and pedestrians** would draw with the same clock and export with the same video.

## 5. Still open

- The web app's knowledge base was not read (behind its app); its symbol library's full list is not
  needed.
- The MP4 writer: read at their sources on 2026-10-19, mp4-muxer (Vanilagy) is MIT but deprecated, its
  README pointing to Mediabunny, which is MPL-2.0 (file-level copyleft) and 10.9 MB unpacked
  (https://github.com/Vanilagy/mp4-muxer, https://github.com/Vanilagy/mediabunny, npm's registry).
  Neither fits the one-file, no-dependency build well; a container writer of the app's own is the
  plan, against ISO/IEC 14496-12's box structure (sold; its free copies and open readers to be read
  at the phase's research).
