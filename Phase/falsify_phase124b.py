"""falsify_phase124b.py -- break the V124b build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126). Each names, in its comment, the check
of tests/bim_phase124b_library_save_toast_browser_tests.py that should catch it."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'silent_again': [("        a3dToast('The Assets library could not be saved: browser storage is full. New assets will be lost when the page reloads; remove assets you no longer need.');\n", "")],   # the toast says the Assets library could not be saved
    'no_warning': [("      console.warn('[BIM] Could not persist family library: ',eS);\n      if(!A3D_FAMLIB_SAVE_FAILED){", "      if(!A3D_FAMLIB_SAVE_FAILED){")],   # the console has the [BIM] warning
    'toast_every_time': [("        A3D_FAMLIB_SAVE_FAILED=true;\n", "")],   # no toast for the second failure
    'no_works_again': [("      if(A3D_FAMLIB_SAVE_FAILED){A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');}\n", "")],   # the toast says saving the library works again
    'works_again_always': [("      if(A3D_FAMLIB_SAVE_FAILED){A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');}\n", "      A3D_FAMLIB_SAVE_FAILED=false;a3dToast('Saving the Assets library works again');\n")],   # and no library toast was raised
    'vague_message': [("New assets will be lost when the page reloads; remove assets you no longer need.", "Try again later.")],   # and that new assets will be lost at a reload
    'no_return': [("      return true;\n    }catch(eS){", "    }catch(eS){")],   # it returns whether the library was stored
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV124b' in txt
out.write_text(txt, encoding='utf-8')
