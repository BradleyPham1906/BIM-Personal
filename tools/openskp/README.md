# tools/openskp

The SketchUp reader the app inlines (V163), and the SketchUp files its tests open. Neither is run by
the app: `canvas_v10.html` stays one file with nothing to install. These tools exist so that what is
inlined can be made again, and checked, from openskp's own source.

| file | what it does |
|---|---|
| `build_reader.mjs` | bundles openskp's TypeScript reader (with fflate and earcut) and compiles it to ES5 syntax: `vendor/openskp/openskp_reader.es5.js` |
| `make_fixtures.mjs` | writes `tests/skp/site_kit.skp` with openskp's writer, and `site_kit.expected.json` from the same geometry |
| `package.json` | the pinned versions: esbuild, TypeScript, fflate, earcut, flatbuffers |

    git clone https://github.com/iamahsanmehmood/openskp /path/to/openskp
    git -C /path/to/openskp checkout 359d1836c9665484c193635796a54aef004babac
    cd tools/openskp && npm ci
    OPENSKP=/path/to/openskp node build_reader.mjs     # prints the reader's sha256
    OPENSKP=/path/to/openskp node make_fixtures.mjs    # prints the fixture's sha256

Both outputs are the same bytes on every run. `Phase/patch_phase163a.py` takes the reader by its
hash; a new openskp commit means a new hash there, a new phase, and the suites run again. The
licences are in `THIRD_PARTY_NOTICES.md` and in the reader's opening comment.
