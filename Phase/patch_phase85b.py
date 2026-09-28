"""patch_phase85b.py -- two things the Phase 85 suite caught.

1. THE A? BUTTON WOULD HAVE COME BACK. bimWatchShell observes only '#figma-layers-panel', with
   subtree:false. A mutation in the RAIL -- which is a sibling of the panel, not a child --
   never fires the observer, so the cleanup pass that removes the dead button never ran on the
   one element it was added to remove. The suite injected a .fl-help button into the rail and
   measured it still sitting there 900ms later. The observer now watches the rail as well.

   This is the V80 pattern finally applied to the half of the shell it had never covered: the
   panel was watched because that is where the retired Canvas blocks lived, and the rail was
   simply never in scope.

2. "Shift + >" IS THE WRONG NAME FOR THE KEY. The handler tests ev.key === '>', with no shiftKey
   check. Measured with real key events:

       Shift+.       -> key='.'  shift=true   flat stayed True   (nothing happened)
       Shift+Period  -> key='>'  shift=true   flat True -> False (worked)
       '>'           -> key='>'  shift=false  flat False -> True (worked)

   The key is '>'. On a US keyboard producing it happens to involve Shift, but "Shift + >" reads
   as Shift AND '>', which is a different chord and is not what the app listens for. Five places
   in the file said "Shift + >"; they now say ">", and so does the new shortcuts sheet, so the
   tooltip and the sheet cannot disagree about the same key.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = '67709a7056cf644545a673d83cf731bd74ef798b969ffd123673303d32d163ae'

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


# ------------------------------------------------------------------ 1. watch the rail too
OLD_OBS = """    A3D_SHELL_OBS.observe(panel,{childList:true,subtree:false});"""
NEW_OBS = """    A3D_SHELL_OBS.observe(panel,{childList:true,subtree:false});
    /* __acad3dV85: the RAIL is watched too. It is a SIBLING of the panel, not a child, so a
       rail re-render never fired this observer -- which meant the cleanup pass that removes the
       dead "A?" button never ran on the one element it exists to remove. Measured: inject a
       .fl-help button into the rail and it was still there 900ms later. The panel was watched
       because that is where the retired Canvas blocks lived; the rail was simply never in
       scope. */
    var railEl=document.getElementById('figma-layers-rail');
    if(railEl)A3D_SHELL_OBS.observe(railEl,{childList:true,subtree:false});"""
sub(OLD_OBS, NEW_OBS, 'the shell observer watches the rail as well')

# ------------------------------------------------------------------ 2. name the key correctly
OLD_ROW = "      {keys:['Shift','>'],k:'>',label:'Switch between the plan and 3D'},"
NEW_ROW = """      /* The handler tests ev.key === '>' and does not look at shiftKey. Producing '>' on a
         US keyboard involves Shift, but "Shift + >" reads as Shift AND '>', which is a
         different chord and is not what the app listens for. Measured: Playwright's 'Shift+.'
         delivers key='.' and does nothing; 'Shift+Period' delivers key='>' and works. */
      {keys:['>'],k:'>',label:'Switch between the plan and 3D'},"""
sub(OLD_ROW, NEW_ROW, 'the sheet names the key as > rather than Shift + >')

# 10 occurrences across 5 lines -- each line carries the 2D and the 3D wording of one tooltip.
# The first count here said 5 because `grep -c` counts LINES, not occurrences.
n = text.count('Shift + >')
if n != 10:
    print('ABORT: expected 10 "Shift + >" labels, found %d' % n)
    sys.exit(1)
text = text.replace('Shift + >', '>', 10)
edits += 1
print('  edit %d ok: all 10 tooltip labels agree with the sheet (Shift + > -> >)' % edits)

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
