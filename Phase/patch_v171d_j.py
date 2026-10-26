#!/usr/bin/env python3
"""V171d, patch j: what the full regression showed, and the sun's sentence.

- The sun now is a dot and its ray now, a line of two points, and V170's Motion offered a line's marching dashes and
  drawing on for it: the sun now and its angles move with the clock, Default (through the day) or Still only, as
  V170 designed for the sun now (V170's suite).
- Sun paths' sentence in Analyze says what it draws now.

Run from the repository root: python3 Phase/patch_v171d_j.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('752b807b548e943f52f8309a5c198cb97adb6a5c38b919c353cc596b96d05fd4')   # after patch i

rep('js/engine/site-analysis/motion.js', """  function bimAnimKinds(o){
    var g=o.dg.g,k=g.kind,n=(g.pts||[]).length,L=[];
    if(k==='live'||g.bands)return L;""", """  function bimAnimKinds(o){
    var g=o.dg.g,k=g.kind,n=(g.pts||[]).length,L=[];
    if(k==='live'||g.bands)return L;
    if(o.dg.a==='sun'&&(o.dg.k==='now'||o.dg.k==='angles'))return L;   /* __acad3dV171d: the sun now moves with the clock, or is still */""")
rep('js/engine/site-analysis/analysis-workspace.js',
    "    sun:'The sun\\'s path over the site on the solstices and the equinoxes, with its hours, and where it is now.',",
    "    sun:'The sun\\'s path over the site on the solstices and the equinoxes and on the day studied, with its hours; where it is now, its altitude and azimuth; and the temperature where it passes. They follow the place, the date and the time.',")
done()
