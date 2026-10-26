#!/usr/bin/env python3
"""V171d, patch e: the words placed, each with its element, kept with the frame's label boxes (A3D_DG.labelWords), and
the hooks that read them and every element's dots: the suite checks each hour's word beside its own dot and no word
over a labelled dot.

Run from the repository root: python3 Phase/patch_v171d_e.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('d3a2fcbbdf9c1c04a58646c5f684d47626a39216399f9a61e962ba311b90fed8')   # after patch d

ML = 'js/engine/site-analysis/model-layers.js'
rep(ML, "    A3D_DG.labelBoxes=[];\n", "    A3D_DG.labelBoxes=[];A3D_DG.labelWords=[];   /* __acad3dV171d: each word with its element */\n")
rep(ML, "      q.hit.boxes.push(bx);A3D_DG.labelBoxes.push(bx);",
    "      q.hit.boxes.push(bx);A3D_DG.labelBoxes.push(bx);A3D_DG.labelWords.push({t:q.t,b:bx,id:q.hit.id});")
rep('js/engine/testing/hooks-sun.js', "  window.__a3dSunLabels=function(){",
    "  window.__a3dSunWords=function(){return JSON.parse(JSON.stringify(A3D_DG.labelWords||[]));};\n"
    "  window.__a3dSunDots=function(){var o={};A3D_DG.hits.forEach(function(h){o[h.id]=h.dots.map(function(d){return d.slice();});});return o;};\n"
    "  window.__a3dSunLabels=function(){")
done()
