"""patch_phase121b_a.py -- V121b: the old canvas's saved data, cleared from the browser.

The owner, on V120's note that the browser may still hold the old canvas's saved data: "No i want to
clear them up". The whiteboard this file grew from kept seven entries in browser storage, found in
every build from V87 to V113c (the oldest kept, and the last with its code):

  obsidian-canvas-enhanced-v6   the whiteboard's board (its own key, LS_KEY)
  obsidian-canvas-enhanced-v5   the board of the version before it, which v6 read to carry over
  acadDrawingsV1                the 2D wire shell's drawings (DKEY)
  acadLayoutsV1                 its layouts (LKEY)
  acadBlocksV1                  its blocks
  acadDockV1                    its dock
  canvas-grid                   the whiteboard's grid setting

Nothing has read any of them since V113c and V117 took that code out; V114 and V117 left them where
they were because deleting a user's stored data was the owner's call, and the owner has made it.

The engine removes exactly these names at every start and says how many it removed. It removes
nothing by pattern: a page opened from disk shares its storage with every other page opened from
disk, so another file's data must not be caught by a rule written for this one. The app's own keys
-- acad3dV1, acad3dDocsV1, acad3dDocV1:<id>, acad3dFamilyLibrary, acad3dUIPrefs -- are not in the list.
The eighth canvas-era entry, canvas-theme, is still written by the Appearance menu: V121b_b gives it
the app's own name and carries its value over."""
NAME = 'patch_phase121b_a.py'
BASE = 'ebf05f4299201eddb765fd7460a4f32edf7bfb1b15a4cfa4f37de5bae86dc336'
import re
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
rep("  var A3D_DOCS=bimDocsBoot();\n  var A3D_DOC_RT={};\n", r"""  var A3D_DOCS=bimDocsBoot();
  var A3D_DOC_RT={};
  /* ================= __acad3dV121b: the old canvas's saved data, cleared =================
     The old canvas this file grew from kept its board, its predecessor's board, and the 2D wire
     shell's drawings, layouts, blocks, dock and grid in browser storage under these names. Nothing
     has read them since V113c and V117 took that code out, and the owner asked for them to go.
     Exactly these names are removed, at every start (an old copy of the file opened in the same
     browser writes them again): a page opened from disk shares its storage with every other page
     opened from disk, so nothing is removed by pattern, and the app's own keys are never here. */
  var A3D_CANVAS_KEYS=['obsidian-canvas-enhanced-v6','obsidian-canvas-enhanced-v5','acadDrawingsV1',
    'acadLayoutsV1','acadBlocksV1','acadDockV1','canvas-grid'];
  function bimClearCanvasStorage(){
    var gone=[],i,k;
    for(i=0;i<A3D_CANVAS_KEYS.length;i++){
      k=A3D_CANVAS_KEYS[i];
      try{
        if(localStorage.getItem(k)!==null){localStorage.removeItem(k);gone.push(k);}
      }catch(eC){
        console.warn('[BIM] The old canvas entry '+k+' could not be removed from browser storage.',eC);
        a3dToast('Some of the old canvas\'s saved data could not be removed from this browser');
        return gone;
      }
    }
    if(gone.length)a3dToast('Removed the old canvas\'s saved data from this browser ('+gone.length+' entr'+(gone.length===1?'y':'ies')+')');
    return gone;
  }
  var A3D_CANVAS_CLEARED=bimClearCanvasStorage();
""")
rep("  window.__a3dLayers=function(){return JSON.parse(JSON.stringify(A3D.layers));};\n",
    "  window.__a3dLayers=function(){return JSON.parse(JSON.stringify(A3D.layers));};\n"
    "  /* __acad3dV121b: what this start removed, and the names it removes */\n"
    "  window.__a3dCanvasCleared=function(){return {removed:A3D_CANVAS_CLEARED.slice(),names:A3D_CANVAS_KEYS.slice()};};\n")

# ---- each name is removed here and nowhere else reads or writes it
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
for k in ('obsidian-canvas-enhanced-v6', 'obsidian-canvas-enhanced-v5', 'acadDrawingsV1', 'acadLayoutsV1',
          'acadBlocksV1', 'acadDockV1', 'canvas-grid'):
    if code.count("'" + k + "'") != 1 or code.count(k) != 1:
        sys.exit('ABORT: %s is named somewhere besides the list that removes it' % k)
for k in ('acad3dV1', 'acad3dDocsV1', 'acad3dFamilyLibrary', 'acad3dUIPrefs'):
    m = re.search(r"var A3D_CANVAS_KEYS=\[([^\]]*)\]", code)
    if not m or k in m.group(1):
        sys.exit('ABORT: an app key is in the removal list')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
