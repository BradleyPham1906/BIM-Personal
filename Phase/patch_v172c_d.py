#!/usr/bin/env python3
"""V172c, patch d: what the suite needs to hold the studies to a sum of its own.
- src/py/bim_ladybug.py: sky_values, the kept sky's patches (direct and diffuse) as Ladybug holds them, so the suite
  can work out a lone box's faces from Ladybug's own patch directions and compare them face by face. Embedded here.
Run from the repository root: python3 Phase/patch_v172c_d.py
"""
import pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, done, ROOT   # noqa: E402

begin('234e52fe52faa7f7e812ba8557d3ec7057b1e9471553ca710e31948b822dd53b')   # patch c
subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_py.py')], check=True)
done()
