# V270 experiment: an IGES box of our own

`gen_iges_cube.mjs W D H` writes an IGES 5.3 file of a box (six untrimmed bilinear entity-128 surfaces, metres) in
the specification's fixed-column layout, so that an IGES reader can be tested without committing a third-party drawing.

Status (2026-11-22): written, not yet read by any IGES reader. The candidate reader, occt-import-js 0.0.23
(LGPL-2.1, OpenCASCADE's IGES reader as WebAssembly, 7.6 MB), is not vendored: it needs the owner's approval under
the third-party rule before it is run or shipped. Until then the app imports STEP (V264) but not IGES.
