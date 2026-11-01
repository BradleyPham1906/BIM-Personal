#!/usr/bin/env python3
"""V172b, patch a: the Ladybug engine joins the build. reference/research-ladybug-weather-comfort.md.

The new files are already in src/ (js/engine/ladybug/: adapter-py.js, written by tools/embed_py.py from src/py/
bim_ladybug.py; runtime.js; sources.js; analyses.js; and testing/hooks-ladybug.js). This patch lists them in the page,
after the site analysis tools and after their hooks, and gives tools/app_layout.py their rows.

Run from the repository root: python3 Phase/patch_v172b_a.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

begin('9e07f24ce34c52a45225b03e5e2457e501fa130f86b92aa74d3e1510924b1f64')   # V172 as merged

rep('index.html', '<!-- @include js/engine/site-tools/panel.js -->\n',
    '<!-- @include js/engine/site-tools/panel.js -->\n'
    '<!-- @include js/engine/ladybug/adapter-py.js -->\n'
    '<!-- @include js/engine/ladybug/runtime.js -->\n'
    '<!-- @include js/engine/ladybug/sources.js -->\n'
    '<!-- @include js/engine/ladybug/analyses.js -->\n')
rep('index.html', '<!-- @include js/engine/testing/hooks-tools.js -->\n',
    '<!-- @include js/engine/testing/hooks-tools.js -->\n'
    '<!-- @include js/engine/testing/hooks-ladybug.js -->\n')

LAY = ROOT / 'tools' / 'app_layout.py'
s = LAY.read_text(encoding='utf-8')
a1 = "    ('site-tools/panel.js', '  /* ================= __acad3dV172: the site analysis tools in the analysis workspace ================='),\n"
a2 = "    ('testing/hooks-tools.js', '  /* __acad3dV172: the site analysis tools, for the suite */'),\n"
assert s.count(a1) == 1 and s.count(a2) == 1, 'app_layout.py anchors'
s = s.replace(a1, a1 +
    "    ('ladybug/adapter-py.js', \"  /* ================= __acad3dV172b: the Ladybug adapter's Python, as text =================\"),\n"
    "    ('ladybug/runtime.js', '  /* ================= __acad3dV172b: Ladybug Tools in a worker ================='),\n"
    "    ('ladybug/sources.js', '  /* ================= __acad3dV172b: the weather Ladybug reads ================='),\n"
    "    ('ladybug/analyses.js', '  /* ================= __acad3dV172b: the analyses, run and kept ================='),\n")
s = s.replace(a2, a2 + "    ('testing/hooks-ladybug.js', '  /* __acad3dV172b: the Ladybug analyses, for the suite */'),\n")
LAY.write_text(s, encoding='utf-8')
done()
