# cc-ifc, BimCraft's IFC engine (V196)

`ifc/` is `app/ifc/` of https://github.com/getcadcraft/bimcraft at commit
`cfbd948949cdb2a4712bd94b1a1985306d8d60d2`, copied unchanged, with that repository's `LICENSE` (Apache License 2.0),
`NOTICE` and `PROVENANCE.md`. Copyright 2026 The Data Design Group, Inc. Its names (CadCraft, BimCraft) are their
trademarks and are not used for this app (NOTICE; Apache-2.0 section 6).

It reads IFC2x3, IFC4 and IFC4.3 files into web-ifc's `IfcAPI` calls, and makes each element's geometry. Openings and
other booleans use Manifold (Apache-2.0), from npm `manifold-3d@3.5.4`.

`tools/ifc/build_ifc.mjs` bundles these files and Manifold's loader, unchanged, into one classic script,
`runtime/cc-ifc/cfbd948/bim-ifc.min.js` (global `BIMIFC`), with Manifold's WebAssembly beside it. The engine loads it
only when an IFC file is opened (`engine/io/ifc-full.js`). Why this engine: `docs/research/research-ifc-engine.md`.

Never edit these files by hand; to move to a newer revision, replace `ifc/` from upstream, rebuild, and rerun
`docs/research/experiments/v196-ifc/run.mjs`.
