#!/usr/bin/env python3
"""V171b, d: the movement analyses and the traffic pick their light or dark colours by the map's style, which is the
ground under them outside the workspace; in it the ground is the mode's, so they follow the mode.
Run from the repository root: python3 Phase/patch_v171b_d.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('ff4633d36008c8b51f1a1cd07df97f4378b4449bd07f23220c993cebd81271b2')   # after 171b c
rep('js/engine/site-analysis/movement-analyses.js',
    "  function bimMvLight(){var s=bimMapSettings().style;return s==='street'||s==='custom';}\n",
    "  function bimMvLight(){var L=bimAwLook();if(L)return L.light;var s=bimMapSettings().style;return s==='street'||s==='custom';}   /* __acad3dV171b: the workspace's ground is the mode's */\n")
done()
