#!/usr/bin/env python3
"""V172c, patch e: what V172c's suite found (2026-11-01).
- bimSimStamp (V143), the model's shape that says a result is out of date, counted each mesh's vertices and its
  position, not where the vertices are: a box raised from 10 m to 12 m kept its stamp, and Solar, Sun hours and
  Ladybug's studies each said they were current. Each mesh's coordinates now go into the hash (to the millimetre),
  in the same "hash:north:settings" form bimResKeyFrom reads. Found by the suite's "the box raised: out of date".
Run from the repository root: python3 Phase/patch_v172c_e.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('2b293487ea11c6157113923ed221da7da2305f96361004a16c4ea45b21d4e7cc')   # patch d
rep('js/engine/analysis/simulation.js',
    "    var h=0;for(i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;\n"
    "    return h+':'+(bimTrueNorthDeg())+':'+JSON.stringify(bimSunSettings());\n",
    "    var h=0,j,k;for(i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;\n"
    "    /* __acad3dV172c: where the vertices are, not only how many: a mesh reshaped with the same count changed nothing above */\n"
    "    for(i=0;i<A3D.objs.length;i++){m=A3D.objs[i].mesh;if(!m||!m.v)continue;\n"
    "      for(j=0;j<m.v.length;j++)for(k=0;k<3;k++)h=(h*31+Math.round((m.v[j][k]||0)*1000))|0;}\n"
    "    return h+':'+(bimTrueNorthDeg())+':'+JSON.stringify(bimSunSettings());\n")
done()
