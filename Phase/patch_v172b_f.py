#!/usr/bin/env python3
"""V172b, patch f: what the full regression asked of the build. reference/research-ladybug-weather-comfort.md.

- A figure shown as a table, or as its chart and its table, carries the class its rule names, written out whole
  ('o-table', 'o-both'), not put together from 'o-' and its option: V114 holds every rule of the stylesheet to a
  class some code writes, and reads the code for the names it writes. The option is 'table' or 'both' or none
  (bimBrdOpts), so the board draws as before.

Run from the repository root: python3 Phase/patch_v172b_f.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('8e68d4c9610df4321e921df8f3d600f5b582d0b3d9b639958e5eea634aab5e37')   # patch e

rep('js/engine/sheets/board-figures.js', "(o.show?' o-'+o.show:'')", "(o.show==='table'?' o-table':o.show==='both'?' o-both':'')", 2)
done()
