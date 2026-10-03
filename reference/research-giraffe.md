# Research: Giraffe (giraffe.build), and what this app takes from it

The owner: "I just discover this app called giraffe that is kinda similar to what we are doing. can
you take a look at their design, docs or even if there's any open code".

Giraffe's help centre, docs site and the reviews could not be opened from the build environment,
so most points come from search summaries of the pages under Sources. The SDK's type declarations
were read from the published npm package itself, and are marked [src].

## What it is

- **A browser app for the earliest stage of a project:** site, massing, then yield and money. It is
  built for developers, architects and planners.
- **Map-first, not model-first.** TRXL's spotlight calls it "a map, a pencil and a calculator" in
  one place. You draw on a live map whose GIS data layers come straight from map servers;
  right-clicking any geometry queries its metadata.
- **Simple geometry.** Shapes are GeoJSON outlines, extruded and stacked into floors. There are no
  walls, doors or sections, which is where this app (model-first CAD/BIM) differs.

## Its concepts

- **Usages.** A named set of assumptions you assign to a geometry, such as Residential or
  Commercial. It brings in its colour and area efficiencies (GBA→GFA, GBA→NSA), and also parking
  rates, hard costs, sale price, rent and yield. Areas are tracked by usage, and Height overrides
  the floor-to-floor and level count.
- **Raw and baked sections.** What you draw is a raw section. The engine "bakes" it into stacked
  sections: floors with a base height, a height and a stack order [src].
- **Calculations and the analytics data model.** These are live numbers over the properties.
- **Lenses.** Colour the model by a property, plus a **lens table**: a bottom strip of the
  selection's numbers, whose height the layout tracks [src].
- **Flows.** Small node graphs attached to a geometry from its Properties panel.
  - A new flow starts with one "read feature" node and one "write feature" node.
  - Prebuilt ones are offered as **Quick Transforms**.
  - Flows can be imported from another project.
- **Scenarios** (`visibleScenarios` [src]) and saved **views** (`views`, called Vistas).
- **Layers** with folders, lock, transparency and an active layer. A layer tree [src].
- **Paper:** a presentation app, built on Giraffe's own app store.
- **Apps:** iframes inside Giraffe, talking to it over postMessage.
- **Layout:** a left bar, a right bar and the lens table. The right bar is Properties. Drawing tools
  are few: grid snaps, typed dimensions and layers.

## The open part: the app SDK [src]

The app itself is closed. Its only public code is the SDK for embedded apps:
- **Packages:** `@gi-nx/iframe-sdk` 0.0.15 and `@gi-nx/iframe-sdk-react` 0.0.10 on npm. No license
  is declared, so ideas can be taken but not code.
- **State.** `giraffeState.get(key)` returns a **read-only** snapshot. `addListener(keys, fn)`
  subscribes to changes. The keys include:
  - `selected`, `lensSelection`;
  - `projects`, `rawSections`, `bakedSections`;
  - `flows`, `blocks`, `layerTree`, `projectLayers`;
  - `views`, `visibleScenarios`;
  - `mapView`, `mapContent`;
  - `uiLayout` (bar widths and the lens table's height);
  - `contextMenuClick`, `workspace`.

  Geometry keys come back as GeoJSON FeatureCollections.
- **Commands.** `rpc.invoke(name, args)` calls into Giraffe, for example `setTiles`. The changelog
  mentions `evaluateFeatures`, which resolves stacking in one call.
- **Types.** The package that defines them, `@gi-nx/gi-types`, is not public.

From Giraffe's own help article "The Giraffe Javascript SDK", pasted by the owner (the page cannot
be opened from the build environment):

- **One set of functions, two ways in:**
  - **The Iframe Post-message SDK** is for an app the customer deploys and owns, whose UI appears
    inside Giraffe in an iframe on the **right** of the screen. It combines Giraffe's features with
    the customer's own APIs, data or workflows.
  - **The Console JS SDK** is for the same functions typed in the browser console. It is meant for
    one-off automations (for example: import a CSV of points, join them to cadastre boundaries,
    save them as projects), advanced GIS work, and prototyping an algorithm before it becomes an
    app.
- **What an app can do.** It reads and writes geometries, layers and UI state (for example the
  current selection). It uses Giraffe's authentication and hosting.
- **The data is GeoJSON,** chosen because "simple formats like this drive automation and
  interesting analysis".
- **What came before:**
  - a pub/sub API, still used to drive Giraffe live from Grasshopper;
  - a first JavaScript SDK that customers built apps with;
  - Bit and webpack module federation, which they tried.

  All of these needed "significant technical setup", so they went with plain postMessage instead.

**For this app:** the engine already has the console half. Its `window.__a3d…` hooks are what
every suite drives, and `__a3dRegisterCommand`, `__a3dRegisterDiscipline` and `__a3dRegisterTab`
are an extension API. An app SDK, then, is mostly three things:
- choosing and documenting a stable subset of those functions;
- giving the model a plain export format: plan outlines and extrusions as GeoJSON-like features,
  plus the BIM properties;
- adding a postMessage bridge to the same function table, for an iframe app docked in the right
  panel.

That is Giraffe's "same set of functions, two ways in", and it keeps the plugin route free of
build tooling.

## What this app takes

The owner chose all four, ahead of the MEP runs:

1. **V131 Usages and live areas.** A usage on rooms and masses carries a colour and GBA→GFA→NSA
   efficiencies. It is edited in Properties, with a live area table for the selection. It builds on
   rooms, Areas by Level and the schedules.
2. **V132 A colour-by-property lens.** Colour by usage, level, type or any property, with a legend,
   under Appearance.
3. **V133 Design scenarios.** Options within one project, switched between and compared by their
   numbers.
4. **Later: Flows and an app SDK.**
   - Per-object node graphs.
   - A documented plugin API: read-only state snapshots with listeners, plus named commands over
     postMessage. The engine's `__a3dRegisterCommand`, `__a3dRegisterDiscipline` and
     `__a3dRegisterTab` already point that way.

It also confirms V130's direction: few tools on screen, and the work done in Properties.

## Sources

- [Giraffe](https://www.giraffe.build/), [Giraffe for architects](https://www.giraffe.build/architects/), [plugins and data packs](https://www.giraffe.build/plugins/)
- [Help: calculations overview](https://help.giraffe.build/en/articles/12334672-calculations-overview)
- [Help: built-in properties](https://help.giraffe.build/en/articles/11818694-built-in-properties)
- [Help: the analytics data model](https://help.giraffe.build/en/articles/11511677-the-analytics-data-model)
- [Help: create a new flow](https://help.giraffe.build/en/articles/12117613-create-a-new-flow)
- [Help: layer types](https://help.giraffe.build/en/articles/11814863-layer-types)
- [Help: build your first app](https://help.giraffe.build/en/articles/12525764-build-your-first-app)
- [Giraffe changelog](https://changelog.giraffe.build/)
- [TRXL: Giraffe feature spotlight](https://www.trxl.co/feature-spotlight-giraffe/)
- [Architosh: ToolTalk, Giraffe](https://architosh.com/2025/09/tooltalk-giraffe-reimagines-urban-design-and-development/)
- [npm: @gi-nx/iframe-sdk](https://www.npmjs.com/package/@gi-nx/iframe-sdk), [SDK docs](https://gi-docs.web.app/)
- Giraffe help: "The Giraffe Javascript SDK" ([help centre](https://help.giraffe.build/)), text pasted by the owner
