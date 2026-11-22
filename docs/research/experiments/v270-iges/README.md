# V270 experiment: an IGES box of our own

`gen_iges_cube.mjs W D H` writes an IGES 5.3 file of a box (six untrimmed bilinear entity-128 surfaces, metres) in
the specification's fixed-column layout, so that the IGES reader is tested without committing a third-party drawing.

Result (2026-11-22, after the owner's approval of occt-import-js 0.0.23): OpenCASCADE's reader loads all six entities
of `gen_iges_cube.mjs 2 1 3` (`tests/fixtures/iges/box-2x1x3.igs`), as faces spanning 0..2, 0..1, 0..3 m; asked for
millimetres it gives 0..2000, 0..1000, 0..3000, so the file's unit (M) is read. Welded, the faces close to 6 m3.
