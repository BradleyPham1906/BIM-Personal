# The source of the OpenCASCADE build in this folder

`replicad_single.js` and `replicad_single.wasm` are the npm package `replicad-opencascadejs@1.2.1` (its `dist/`), copied
byte for byte, under the GNU Lesser General Public License 2.1 (`OCCT-LICENSE`). They are a build of Open CASCADE Technology
(https://dev.opencascade.org, LGPL-2.1 with the Open CASCADE exception) made with the opencascade.js tool chain.

Their source: https://github.com/sgenoud/replicad (`packages/replicad-opencascadejs`, the build configuration, at the release
tagged for 1.2.1), https://github.com/donalffons/opencascade.js (the tool chain) and https://github.com/Open-Cascade-SAS/OCCT
(the library). On request to the owner of this repository, a copy of that source is provided, as section 6 of the licence asks.

They are their own files, loaded by the app only through `src/js/engine/solids/occt-adapter.js`, and can be replaced by any build
with the same interface: put its two files here under these names and update `runtime/MANIFEST.json` (`tools/occt/build_occt.mjs`).
