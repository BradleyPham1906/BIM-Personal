"""patch_phase85c.py -- Escape stops backing out of the application.

FOUND BY the Phase 85 suite, which pressed Escape once in the 3D view to demonstrate the row the
shortcuts sheet documents, and then watched every later check fail:

    body className after one Escape:  'cad-ribbon-on fc-on acad-on'   <- 'a3d-mode' is gone

One Escape, from the 3D view, with no dialog and no sketch open, LEFT THE ENTIRE BIM WORKSPACE.
The undo and duplicate checks that followed then reported nothing happening, because the engine
was no longer running.

The old tail of the chain was:

    if(A3D.flat){toggleFlat();...return;}      // in a PLAN, Escape sent you to the 3D VIEW
    exit3d();...return;                        // in 3D, Escape closed the workspace

Both of those made sense when this was a mode you were "in" and Escape meant "get me out of it."
V84 retired that model: views are the navigation now, and there is nothing sensible for Escape to
back out TO. Escape is also the single most reflexive key in any drawing application -- the user
presses it to cancel whatever they are doing -- and in this app that reflex closed their
workspace, or silently swung the camera from the plan into 3D.

Escape now walks the transient states and then STOPS: rail popover, zoom window, dialog,
constraint pick, sketch, section, clear the selection, nothing. The last step is deliberate rather
than empty -- clearing the selection is what Escape does in Revit and in AutoCAD, and it gives the
key an honest final meaning instead of a cliff.

No existing suite asserted the old behaviour; V83's suite asserts the popover and zoom-window
steps, which are untouched.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = 'b614f0e10455d555c1b25d007be776bb28bb71d2b47cc42a0602a78641fe1c83'

src = SRC.read_bytes()
have = hashlib.sha256(src).hexdigest()
if have != BASE:
    print('ABORT: baseline mismatch\n  expected %s\n  found    %s' % (BASE, have))
    sys.exit(1)
print('baseline ok: %s (%d bytes)' % (have[:16], len(src)))

text = src.decode('utf-8')
edits = 0


def sub(old, new, label, count=1):
    global text, edits
    n = text.count(old)
    if n != count:
        print('ABORT: %s: expected %d occurrence(s), found %d' % (label, count, n))
        sys.exit(1)
    text = text.replace(old, new, count)
    edits += 1
    print('  edit %d ok: %s' % (edits, label))


OLD_TAIL = """      if(A3D.section){bimExitSection();ev.preventDefault();ev.stopImmediatePropagation();return;}
      if(A3D.flat){toggleFlat();ev.preventDefault();ev.stopImmediatePropagation();return;}
      exit3d();ev.preventDefault();ev.stopImmediatePropagation();return;
    }"""

NEW_TAIL = """      if(A3D.section){bimExitSection();ev.preventDefault();ev.stopImmediatePropagation();return;}
      /* __acad3dV85: the chain STOPS here. It used to end:

             if(A3D.flat){toggleFlat();...}   // in a plan, Escape swung the camera into 3D
             exit3d();                        // in 3D, Escape closed the whole workspace

         Measured: one Escape in the 3D view with nothing open left the BIM workspace entirely --
         body lost 'a3d-mode' and the engine stopped. Both steps made sense while this was a MODE
         you were in and Escape meant "get me out of it". V84 retired that model: views are the
         navigation, and there is nothing sensible left to back out TO. Escape is also the most
         reflexive key in any drawing application, and that reflex should never close the
         workspace.

         Clearing the selection is the honest last step rather than an empty one -- it is what
         Escape does in Revit and in AutoCAD. Past that, Escape does nothing and says nothing. */
      if(A3D.sel||A3D.sel2||(A3D.selSet&&A3D.selSet.length)){
        A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
        refreshTree();refreshProps();paint();
        ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      return;
    }"""

sub(OLD_TAIL, NEW_TAIL, 'Escape backs out of states, never out of the workspace')

# the sheet must describe what the chain now does
OLD_LAB = ("      {keys:['Esc'],k:'Escape',label:'Back out one step: menu, zoom window, dialog, "
           "sketch, section, plan'}")
NEW_LAB = ("      {keys:['Esc'],k:'Escape',label:'Back out one step: menu, zoom window, dialog, "
           "sketch, section, then clear the selection'}")
sub(OLD_LAB, NEW_LAB, 'the sheet describes the chain it actually has')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
