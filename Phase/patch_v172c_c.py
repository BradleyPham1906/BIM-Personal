#!/usr/bin/env python3
"""V172c, patch c: what the first browser check of the studies asked of the build (2026-11-01).
- The legend went under the floating dock at the view's bottom right: it is now placed in the view's safe area
  (bimSafeViewRect, as the colour-by legend is), at its bottom right.
- numpy's version was kept as none: the versions are read when the worker starts, before the first study loads
  numpy. The study's answer now carries the versions read after it, and the kept result and the runtime take them.
Run from the repository root: python3 Phase/patch_v172c_c.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('d84a7107fb507e6c1c1c93714f269b322f4d8b2302aaa42a6600da70c8553649')   # patch b

S = 'js/engine/ladybug/studies.js'
rep(S, "      var lw=196,lh=72,lx=W-lw-14,ly=H-lh-14,",
    "      var sr=bimSafeViewRect(),lw=196,lh=72,lx=Math.max(sr.x+12,sr.x+sr.w-lw-12),ly=Math.max(sr.y+12,sr.y+sr.h-lh-12),")
rep(S, "      var D=bimLbData(),r=bimLbsPack(G,ans.values);\n",
    "      var D=bimLbData(),r=bimLbsPack(G,ans.values),ver;\n"
    "      if(ans.versions){try{ver=JSON.parse(ans.versions);if(ver&&typeof ver==='object')A3D_LB.versions=ver;}catch(eV){console.warn('[BIM] Ladybug versions',eV);}}\n")
rep('js/engine/ladybug/runtime.js',
    "        say({t:'done',id:m.id,r:JSON.stringify({pre:pre,values:vals,dirs:V.length,ms:{first:t1-t0,rays:rays,all:Date.now()-t0}})});\n",
    "        say({t:'done',id:m.id,r:JSON.stringify({pre:pre,values:vals,dirs:V.length,ms:{first:t1-t0,rays:rays,all:Date.now()-t0},\n"
    "          versions:String(PY.runPython('import bim_ladybug\\nbim_ladybug.versions()'))})});\n")
done()
