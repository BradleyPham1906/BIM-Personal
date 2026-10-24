# Third-party notices

## GeoLibre

`canvas_v10.html` (V135, find open data) contains the US open-data portal list and the ArcGIS Hub
and Socrata search logic from GeoLibre, ported to ES5. The sources are
`packages/plugins/src/plugins/us-{federal,state,local}-gis-catalogs.ts`, `arcgis-hub-api.ts` and
`socrata-api.ts` at commit 4ec853f of https://github.com/opengeos/GeoLibre.

    MIT License

    Copyright (c) 2026 Qiusheng Wu

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## openskp

`canvas_v10.html` (V163, open SketchUp files) contains the TypeScript reader of openskp, at commit
359d1836c9665484c193635796a54aef004babac of https://github.com/iamahsanmehmood/openskp: the code that
reads a `.skp` file (`parseSkp`, `buildScene`, `buildInstancedScene`, `SkpParseError` and what they
use). It is bundled with the two packages below and compiled to ES5 syntax, unchanged otherwise, by
`tools/openskp/build_reader.mjs`; the result is `vendor/openskp/openskp_reader.es5.js`. The test
files in `tests/skp/` are written by openskp's own writer (`tools/openskp/make_fixtures.mjs`), which
the app does not contain.

    MIT License

    Copyright (c) 2024-2026 Ahsan Mehmood

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## fflate

Bundled into the SketchUp reader above (it opens the ZIP that SketchUp 2021 and later save):
fflate 0.8.3, https://github.com/101arrowz/fflate.

    MIT License

    Copyright (c) 2026 Arjun Barrett

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

## earcut

Bundled into the SketchUp reader above (it splits SketchUp's faces into triangles): earcut 3.2.4,
https://github.com/mapbox/earcut.

    ISC License

    Copyright (c) 2026, Mapbox

    Permission to use, copy, modify, and/or distribute this software for any purpose
    with or without fee is hereby granted, provided that the above copyright notice
    and this permission notice appear in all copies.

    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
    REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
    INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
    OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
    TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
    THIS SOFTWARE.


## OpenBridge UI asset intake (not yet integrated into canvas_v10.html)

OpenBridge webcomponents, Ocean Industries Concept Lab (OICL).
Pinned commit: `eb2013003cbb323ded47674576e5b273df0a2566` (`2.0.0-next.9`).
Source: https://github.com/Ocean-Industries-Concept-Lab/openbridge-webcomponents/blob/eb2013003cbb323ded47674576e5b273df0a2566/LICENSE.TXT

The pinned LICENSE.TXT and package metadata directly license this snapshot under
Apache-2.0. The original license (including its copyright appendix) is preserved
verbatim at `vendor/openbridge/LICENSE.TXT`. Do not substitute a newer upstream
revision without reviewing its license: the reviewed newer revision starts under
AGPL-3.0-only and offers Apache-2.0 after a per-version 180-day delay.

Modifications: extracted 17 static SVGs from TypeScript wrappers (geometry unchanged);
added an ES5 lookup/accessibility adapter; selected and scoped theme/sizing tokens.
Original wrappers and palette CSS are preserved as source references only, never executed
or loaded by the production app. Per-file provenance and checksums: `vendor/openbridge/manifest.json`.
Some upstream names identify Google-derived icons; preserve these names and source attribution.
No Figma files, fonts, logos or maritime certification claims are included.
