#!/usr/bin/env python3
"""V172c, patch b: the guide and the version. reference/research-ladybug-sun-radiation.md.
- docs/src/site.md: Sun and radiation on the model (Ladybug), after Weather and comfort (Ladybug).
- The version: V172 still (a sub-phase keeps its number, as V171b to V171d and V172b did), of 2026-11-01, its
  marker noted. Then tools/build_docs.py writes the guide again (its versions page lists the build kept before V172c).
Run from the repository root: python3 Phase/patch_v172c_b.py
"""
import pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

begin('abae28ed41437882737652a484bd30fc4027e13cb59abb2b0a2fb43e7cb4250f')   # patch a

rep('js/engine/ui/guide-versions.js', "__acad3dV171; __acad3dV172; __acad3dV172b */",
    "__acad3dV171; __acad3dV172; __acad3dV172b; __acad3dV172c */")

DOC = ROOT / 'docs' / 'src' / 'site.md'
s = DOC.read_text(encoding='utf-8')
a = """change one and each result that used it says it is out of date.

## Zoning and yield
"""
assert s.count(a) == 1, 'site.md anchor'
s = s.replace(a, """change one and each result that used it says it is out of date.

### Sun and radiation on the model (Ladybug)

Two more rows under 5. Climate put Ladybug's own studies on the model's faces, beside **Solar** and **Sun
hours**, which stay as they are:
- **Incident radiation (Ladybug):** the kWh/m² each face receives over the weather's year, from the sun
  and the sky, by Ladybug's sky matrix and its radiation study. It needs the weather (Weather for
  Ladybug). The sky is cut into patches: **Tregenza**'s 145, Ladybug's default, or **Reinhart**'s 577,
  finer, with four times the rays. The coarse sky reads about 4% high in a deep courtyard; the fine one
  agrees with the exact view.
- **Direct sun hours (Ladybug):** the hours each face sees the sun, by Ladybug's sun path and its direct
  sun study, on **the day studied** (the site's date, in the sun panel; every quarter hour) or over **the
  year** (every hour). It needs the site's place, not the weather.

Each studies the selected solids, or every solid when none is selected, one value a face. Every solid
shown casts shade, the studied ones included. Each face's point is moved 10 cm off the face first, as
Ladybug's components do. There are no reflections, as in Ladybug, and the ground is a hemisphere that
reflects 20% of the sky.

**Show on the model** draws the study as Ladybug does: the faces in its legend's colours (its own
palettes, the range from the study's lowest to its highest value), the other solids in grey, the legend
at the bottom right. **Clear** removes the result; each run is one undo step. A result is out of date
when the model, its north, the site's place, the weather or a setting changes, and says which.

The sky's matrix is Radiance's own `gendaymtx`, the program Ladybug runs on a desktop, built for the
browser from its C as it is (the release 6.0P1a), and checked by its SHA-256 before use; numpy, which
the studies' sums use, is Pyodide's own. Both load at the first study, about 3 MB more. The rays are the
app's, in the same worker, as Ladybug's components use their CAD program's own; a model of 20,000 faces
takes a few seconds. The reflectance, the offset and the steps an hour are in Standards, under Climate.

## Zoning and yield
""")
DOC.write_text(s, encoding='utf-8')
done()
subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_docs.py')], check=True)
