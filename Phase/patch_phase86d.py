"""patch_phase86d.py -- keep the shortcuts sheet honest about V86, and let the palette open it.

TWO LOOSE ENDS from V86, both of the "no leftovers, and they have to work in the new version"
kind the user has asked for repeatedly.

1. THE V85 SHORTCUTS SHEET STILL DESCRIBES THE OLD INPUT MODEL. It says "Type an exact length
   while drawing", which was the whole of the old grammar -- V86 replaced it with AutoCAD's five
   coordinate forms and added U. A help sheet that describes the previous version is the exact
   failure V85 built its suite to prevent, arriving one phase later from the other direction: the
   keys changed, not the sheet.

2. THE USER'S SENTENCE IS GENUINELY AMBIGUOUS. "i hit cmd + k and the command shortkey from the
   past still there, however it never work. it should pop up the new shortcut not the old."
   Read one way that is the dead command list (what V86 fixed). Read another way it is a request
   for Cmd+K to reach the new keyboard-shortcuts sheet. Rather than guess between them, SHORTCUTS
   becomes a command in the palette, so both readings are satisfied and neither costs the other
   anything.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = '0a251526f0c201944842463253fe607f93225399fafaf0ba7474cd1e6cf5e64a'

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


# ------------------------------------------------------------------ 1. the sheet tells the truth
OLD_ROWS = """    {grp:'Drawing',rows:[
      {keys:['Enter'],k:null,label:'Finish the current wall, polyline or stair'},
      {keys:['C'],k:null,label:'Close the current wall or polyline path'},
      {keys:['0-9'],k:null,label:'Type an exact length while drawing, then Enter to commit it'},
      {keys:['Arrows'],k:null,label:'Nudge the selected object'}
    ]},"""
NEW_ROWS = """    /* __acad3dV86: rewritten for the AutoCAD input model. The previous rows described a
       grammar that accepted a bare length and nothing else, which is what the tools took
       before this phase. A help sheet describing the previous version is the same fault V85
       built its suite to catch, arriving from the other direction: the keys changed, not the
       sheet. */
    {grp:'Drawing',rows:[
      {keys:['Enter'],k:null,label:'Finish the current line, polyline, wall or stair'},
      {keys:['C'],k:null,label:'Close the path (from three points on)'},
      {keys:['U'],k:null,label:'Undo the last point'},
      {keys:['x,y'],k:null,label:'Absolute point. @x,y is relative to the last point; # forces absolute'},
      {keys:['d<a'],k:null,label:'Polar point: distance, then angle. @5<45 is relative'},
      {keys:['0-9'],k:null,label:'A bare length draws that far along the current direction'},
      {keys:['Arrows'],k:null,label:'Nudge the selected object'}
    ]},"""
sub(OLD_ROWS, NEW_ROWS, 'the shortcuts sheet describes the AutoCAD grammar')

OLD_VIEWS = "      {keys:['Esc'],k:'Escape',label:'Back out one step: menu, zoom window, dialog, sketch, section, then clear the selection'}"
NEW_VIEWS = ("      {keys:['Esc'],k:'Escape',label:'Back out one step: menu, zoom window, dialog, sketch, section, then clear the selection'},\n"
             "      {keys:['Enter'],k:null,label:'With nothing running, repeats the last command'}")
sub(OLD_VIEWS, NEW_VIEWS, 'the sheet documents Enter-repeat')

# ------------------------------------------------------------------ 2. SHORTCUTS is a command
OLD_CMD = "    ['SELECTALL',['SA','ALL'],'selAll','Select every object'],['CLEAR',[],'selNone','Clear selection']"
NEW_CMD = ("    ['SELECTALL',['SA','ALL'],'selAll','Select every object'],['CLEAR',[],'selNone','Clear selection'],\n"
           "    ['SHORTCUTS',['KEYS','HELP','?'],'shortcuts','Keyboard shortcuts']")
sub(OLD_CMD, NEW_CMD, 'SHORTCUTS is a command in the palette')

OLD_MAP = """    grid:function(){bimSetSnap({grid:!A3D_SNAP.grid});bimSyncSnapPill();paint();
      a3dToast('Grid snap '+(A3D_SNAP.grid?'on':'off'));}
  };"""
NEW_MAP = """    grid:function(){bimSetSnap({grid:!A3D_SNAP.grid});bimSyncSnapPill();paint();
      a3dToast('Grid snap '+(A3D_SNAP.grid?'on':'off'));},
    /* Opens the V85 sheet through its own rail button, so there is one shortcuts sheet with one
       renderer rather than a second copy that could drift from the first. */
    shortcuts:function(){
      var b=document.querySelector('[data-a3drumenu="help"]');
      if(!b){a3dToast('The shortcuts sheet is not available here');return;}
      b.click();
    }
  };"""
sub(OLD_MAP, NEW_MAP, 'the SHORTCUTS command opens the V85 sheet')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
