#!/usr/bin/env python3
"""V124b: the Assets library's save, warned and toasted (the owner, 2026-10-31, decision D8 of
reference/research-local-storage.md).

bimSaveFamilyLibrary only wrote a console warning when browser storage refused the library, against the build
contract (failures warned and toasted): a SketchUp import, a block or a template added to a full store was gone
at the next reload without a word. It now toasts once per run of failures, as save3d does for the project, says
so again when a save works once more, and returns whether the library was stored.

Run from the repository root: python3 Phase/patch_v124b.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done   # noqa: E402

begin('9e07f24ce34c52a45225b03e5e2457e501fa130f86b92aa74d3e1510924b1f64')   # V172

rep('js/engine/assets/family-library.js',
    "  var FAMILY_LIB_KEY='acad3dFamilyLibrary';\n",
    "  var FAMILY_LIB_KEY='acad3dFamilyLibrary';\n"
    "  var A3D_FAMLIB_SAVE_FAILED=false;   /* __acad3dV124b: a run of failed saves is toasted once */\n")
rep('js/engine/assets/family-library.js',
    "  function bimSaveFamilyLibrary(){\n"
    "    try{localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify(A3D_FAMLIB));}catch(eS){console.warn('[BIM] Could not persist family library: ',eS);}\n"
    "  }\n",
    "  /* __acad3dV124b: a library the browser refuses is warned and toasted, as the project is (save3d) */\n"
    "  function bimSaveFamilyLibrary(){\n"
    "    try{\n"
    "      localStorage.setItem(FAMILY_LIB_KEY,JSON.stringify(A3D_FAMLIB));\n"
    "      if(A3D_FAMLIB_SAVE_FAILED){A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');}\n"
    "      return true;\n"
    "    }catch(eS){\n"
    "      console.warn('[BIM] Could not persist family library: ',eS);\n"
    "      if(!A3D_FAMLIB_SAVE_FAILED){\n"
    "        A3D_FAMLIB_SAVE_FAILED=true;\n"
    "        a3dToast('The Assets library could not be saved: browser storage is full. New assets will be lost when the page reloads; remove assets you no longer need.');\n"
    "      }\n"
    "      return false;\n"
    "    }\n"
    "  }\n")
rep('js/engine/testing/hooks-assets-structure.js',
    "  window.__acad3dV124='librarykinds,",
    "  window.__acad3dV124b='libsavetoast,libtoastonce,libsaveworksagain,libsavereturns';\n"
    "  window.__acad3dV124='librarykinds,")
done()
