# The source of the files in this folder

`occt-import-js.js` and `occt-import-js.wasm` are the npm package `occt-import-js@0.0.23` (its `dist/`), copied byte for
byte, under the GNU Lesser General Public License 2.1 (`LICENSE-occt-import-js.txt`). They are a build of Open CASCADE
Technology (`LICENSE-occt.txt`, LGPL-2.1 with the Open CASCADE exception) made with emscripten.

Their source: https://github.com/kovacsv/occt-import-js (the release tagged v0.0.23) and
https://github.com/Open-Cascade-SAS/OCCT (the library). On request to the owner of this repository, a copy of that source
is provided, as section 6 of the licence asks.

They are their own files, loaded by the app only through `src/js/engine/io/iges-io.js`, when an IGES file is imported,
and can be replaced by any build with the same interface: put its two files here under these names and update
`runtime/MANIFEST.json` (`tools/occt/build_occt_import.mjs`).
