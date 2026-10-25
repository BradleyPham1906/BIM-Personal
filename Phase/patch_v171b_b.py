#!/usr/bin/env python3
"""V171b, b: the context's roads, rail and water are sketches, drawn in their layer's colour; in the workspace they take
the mode's quiet tone as the context's solids do. Run from the repository root: python3 Phase/patch_v171b_b.py"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('13d4b2e28e42ba5dd7579942a4b42a226c7c4b316a28a97c388199aa935472e3')   # after 171b a and the workspace's own fixes
rep('js/engine/drawing/drawing-input.js',
    "      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':lk.color,(o.closed!==false),false,bimObjOffset(o),o.bulges,lk);\n    }\n",
    "      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':(bimAwCtxCol(o)||lk.color),(o.closed!==false),false,bimObjOffset(o),o.bulges,lk);   /* __acad3dV171b */\n    }\n")
done()
