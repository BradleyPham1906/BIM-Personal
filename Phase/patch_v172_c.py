#!/usr/bin/env python3
"""V172, patch c: found in the first screenshot. A criterion's tick, name and unit ran together ("Slope%"): the label
was not a flex row. Now it is, its unit in brackets (panel.js). The restricted grey is half seen on the plan, so the
map shows through it (tools.js); the transform's words write a percentage without a space (suitability.js).

Run from the repository root: python3 Phase/patch_v172_c.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('58195f57e6da2ccf1ad829de36687c52ad50329c66773b6c74d45543cb1709ed')   # patch b, with the tools' files as they stood after the first screenshot

rep('css/site-analysis/workspace.css', ".a3d-tl-b{flex-direction:row;align-items:center;gap:8px;flex-wrap:wrap}\n",
    ".a3d-tl-b{display:flex;flex-direction:row;align-items:center;gap:8px;flex-wrap:wrap}\n")
done()
