#!/usr/bin/env python3
"""V171b, e: the terrain drapes the map over itself with shaders of its own, which neither grey nor fade it as the
workspace's map is; in the workspace the terrain is drawn plain, in its quiet tone, and the map lies faded and grey
around it. Run from the repository root: python3 Phase/patch_v171b_e.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('664a96a1c997a6de9c50bf662cae97df47da785a910bb2acc113fe579bfb80d5')   # after 171b d and the workspace's own fixes
rep('js/engine/map/terrain-3d.js',
    "      if(plan.tiles.length&&rec.ext){\n",
    "      if(plan.tiles.length&&rec.ext&&!bimAwLook()){   /* __acad3dV171b: in the workspace, plain */\n")
rep('js/engine/render/webgpu.js',
    "          if(plan.tiles.length&&D.ext){\n",
    "          if(plan.tiles.length&&D.ext&&!bimAwLook()){   /* __acad3dV171b: in the workspace, plain */\n")
done()
