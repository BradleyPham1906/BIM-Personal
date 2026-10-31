#!/usr/bin/env python3
"""V172, patch d: found by the falsification. The tool's fields were made 36 px on a touch screen by a rule of its own,
which two of the panel's rules (#a3d-right's and .a3d-sa's) already gave them: breaking it changed nothing. It goes;
what a finger needs here and nothing else gave is the tick rows, now at least 36 px tall.

Run from the repository root: python3 Phase/patch_v172_d.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('c2a00e5bac59cf379e537f602c67584c88a8bd66c5f86249f158a822edb25cb5')   # patch c, with the tools' files as they stand after the falsification's first full run

rep('css/site-analysis/workspace.css', "@media(pointer:coarse){.a3d-tl input[type=text],.a3d-tl select{min-height:36px;font-size:16px}.a3d-tl-b input[type=checkbox]{width:22px;height:22px}}\n",
    "@media(pointer:coarse){.a3d-tl-b{min-height:36px}.a3d-tl-b input[type=checkbox]{width:22px;height:22px}}   /* the fields' 36 px are the panel's own (#a3d-right, .a3d-sa) */\n")
done()
