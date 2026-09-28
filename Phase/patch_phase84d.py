"""patch_phase84d.py -- a third leftover, found in visual review.

Screenshot 01_floor_plan.png shows the ribbon label reading "Level 0 - Floor Plan" and the status
bar reading "View: Plan", while the Properties panel three inches to the right reads "View  3D".

Two causes, both the same family as the rest of this phase:

  1. bimPropText('View', A3D.flat?'Plan':'3D') is the flat-is-not-plan confusion a third time.
     An elevation and a section are both flat, so both of them reported "Plan" in the Properties
     panel. It now reports the ACTIVE VIEW'S NAME, which is the thing the user is actually in.
  2. Nothing re-rendered the Properties panel on a view change, so even a correct readout would
     have been stale until something else happened to refresh it. That is what the screenshot
     caught: the panel was showing its boot-time render.

The standing instruction from the user is the reason both are fixed here rather than noted:
"you need to make sure we dont have any left over and they gotta work in the new version".
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = 'ae86d722bfb95fc7bad4639544e15e0230a37fd58642b3a0f92b684306fcff16'

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


# ------------------------------------------------------------------ 1. report the view, not the plane
OLD_ROW = "    vrows+=bimPropText('View',A3D.flat?'Plan':'3D');"
NEW_ROW = """    /* __acad3dV84: "A3D.flat ? 'Plan' : '3D'" is the flat-is-not-plan confusion a third
       time -- an elevation and a section are flat too, and both of them reported "Plan" here.
       The active view is what the user is in, so the active view is what this says. */
    vrows+=bimPropText('View',(typeof A3D_VIEW!=='undefined'&&A3D_VIEW&&A3D_VIEW.name)
      ?A3D_VIEW.name:(A3D.flat?'Plan':'3D'));"""
sub(OLD_ROW, NEW_ROW, 'the Properties View row names the active view')

# ------------------------------------------------------------------ 2. refresh it on a view change
OLD_TAIL = """    bimSyncViewLabel();
    refreshHud();refreshBrowser();paint();saveSoon();
    return true;
  }"""
NEW_TAIL = """    bimSyncViewLabel();
    /* refreshProps too: without it the Properties panel keeps its boot-time render, which is
       how a panel reading "View 3D" ended up sitting beside a status bar reading "View: Plan"
       in the Phase 84 visual review. */
    refreshHud();refreshBrowser();refreshProps();paint();saveSoon();
    return true;
  }"""
sub(OLD_TAIL, NEW_TAIL, 'a view change re-renders the Properties panel')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
