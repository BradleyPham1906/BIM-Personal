#!/usr/bin/env python3
"""V171b, c: the context's terrain is drawn by its own renderers (WebGL, WebGPU and the canvas), which read its colour
themselves; in the workspace they take the mode's quiet tone. Run from the repository root: python3 Phase/patch_v171b_c.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('da581fd88faf7cab92407c14afa168c5efd19d0b02ee5f2fdc5150dd2e6dc611')   # after 171b b
rep('js/engine/map/terrain-3d.js',
    "      col=bimHexToRgb(sel?'#4ea1ff':(o.col||'#b08559'));\n",
    "      col=bimHexToRgb(sel?'#4ea1ff':(bimAwCtxCol(o)||o.col||'#b08559'));   /* __acad3dV171b */\n")
rep('js/engine/map/terrain-3d.js',
    "polys.push({o:o,pts:pts,z:zs/3,n:n,col:o.col||'#b08559',",
    "polys.push({o:o,pts:pts,z:zs/3,n:n,col:bimAwCtxCol(o)||o.col||'#b08559',")
rep('js/engine/render/webgpu.js',
    "          col=bimHexToRgb(sel?'#4ea1ff':(o.col||'#b08559'));\n",
    "          col=bimHexToRgb(sel?'#4ea1ff':(bimAwCtxCol(o)||o.col||'#b08559'));   /* __acad3dV171b */\n")
done()
