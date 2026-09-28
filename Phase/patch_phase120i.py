"""patch_phase120i.py -- V120: the shell's names say what it is.

The left rail and panel, the command palette and one CSS variable still carried the names of the
modules they were copied from: #figma-layers-shell, -rail and -panel and thirteen .fl-* classes
from the "Figma sidebar" the whiteboard drew, #uploaded-command-palette and its .uc-* classes from
an "Uploaded Figma clone reference integration", and --figma-dock-w. The BIM engine has built all of
them since V113b. V113c held the rename back so that a deletion and a rename would each stay
reviewable; the deletions are done (V120a-h), so this is the rename, count for count:

  #figma-layers-shell / -rail / -panel   #a3d-shell / #a3d-rail / #a3d-leftpanel
  #uploaded-command-palette              #a3d-cmdpal, with .a3d-cmdinput/-results/-row/-key
  .fl-rail-btn, .fl-logo, .fl-collapse   .a3d-railbtn, .a3d-paneltoggle, .a3d-panelcollapse
  .fl-file-head / -title / -sub, .fl-pill  .a3d-projhead / -projtitle / -projsub, .a3d-pill
  .fl-tab-content, .fl-spacer            .a3d-tabbody, .a3d-railspacer
  --figma-dock-w                         --a3d-left-w
  the Project Browser tab 'file'         'browser' (V119 kept 'file' "until the id rename")

With it go the names nothing reads: the rail buttons' data-fl-tab (every reader uses data-tab), the
shell's data-a3dshell (it told the BIM builder from the canvas-era one, and there is one builder),
window.__figmaDockSyncW (enter3d calls bimShellDockW directly), the palette's --j-grey-300 (one
use, now its value), and the rail pass that removed the whiteboard's "A?" button on every change,
though nothing has drawn that button since the whiteboard's sidebar went."""
NAME = 'patch_phase120i.py'
BASE = 'ac70c9181c1818ca7390de404da086e967ff2d544144e77fdbe1f0136282e03f'
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
# ---- the names nothing reads, first, while they are still spelled the old way
rep(' data-fl-tab="file"', '')
rep(' data-fl-tab="assets"', '')
rep("""    var old=document.getElementById('figma-layers-shell');
    if(old&&old.getAttribute('data-a3dshell')==='1')return old;
    /* __acad3dV113c: V113b carried a docked navigator across from a shell built by the canvas-era
       module, because both builders existed for one phase. That module is deleted, so the only
       shell that can be found here is one this function built, and that returns above. The branch
       that moved the tree is removed rather than left reading as a safeguard it no longer is. */
    var sh=document.createElement('aside');
    sh.id='figma-layers-shell';
    sh.setAttribute('data-a3dshell','1');
""", """    var old=document.getElementById('figma-layers-shell');
    if(old)return old;
    var sh=document.createElement('aside');
    sh.id='figma-layers-shell';
""")
rep("""    if(old&&old.parentNode)old.parentNode.replaceChild(sh,old);
    else document.body.appendChild(sh);
""", """    document.body.appendChild(sh);
""")
rep("""  /* The name the docking code in enter3d has always called to resize the workspace behind the
     dock. It used to belong to the canvas-era module; it belongs here now. */
  window.__figmaDockSyncW=bimShellDockW;
""", '')
rep("""      if(window.__figmaDockSyncW)window.__figmaDockSyncW();
    }catch(eDock){""", """      bimShellDockW();
    }catch(eDock){""")
rep("""    /* __acad3dV85: the whiteboard shell's "A?" button is REMOVED here, not left sitting under
       the stack. It had no click handler anywhere in the file, no title, and opened nothing --
       driven with a real pointer it produced no dialog, no toast and no visible change. It was
       Figma-style set dressing in a template this app inherited. Its job, keyboard help, is now
       a real entry in the stack above. Removed on every pass rather than once, because the
       whiteboard shell re-renders its own rail and would put it back. */
    var dead=rail.querySelector('.fl-help'),did=false;
    if(dead&&dead.parentNode){dead.parentNode.removeChild(dead);did=true;}
    if(rail.querySelector('#a3d-railutil'))return did;""",
"""    if(rail.querySelector('#a3d-railutil'))return false;""")
rep("""/* Uploaded Figma clone reference integration: layers, command menu, reactions */
:root{
  --j-grey-300:#C4D3ED;
}
""", '')
rep('color:var(--j-grey-300);', 'color:#C4D3ED;')
rep("""

     The ids and class names are the canvas-era ones on purpose: about seventy CSS rules and
     V80's A3D_SHELL_CLAIMS whitelist are written against them. Renaming them is a separate and
     purely cosmetic change, and doing both at once would make neither reviewable. */""", ' */')

# ---- the Project Browser tab: 'file' -> 'browser'
rep('[data-tab="file"]', '[data-tab="browser"]', 3)
rep("    sh.setAttribute('data-tab','file');", "    sh.setAttribute('data-tab','browser');")
rep('class="fl-rail-btn active" data-tab="file"', 'class="fl-rail-btn active" data-tab="browser"')
rep("""      bimRailIcon('browser')+'</button>'+   /* __acad3dV119: icon only; the tab's id stays 'file' until the id rename */""",
    """      bimRailIcon('browser')+'</button>'+""")

# ---- the renames, token for token
RENAMES = [('figma-layers-shell', 'a3d-shell', 18), ('figma-layers-rail', 'a3d-rail', 22),
           ('figma-layers-panel', 'a3d-leftpanel', 31), ('uploaded-command-palette', 'a3d-cmdpal', 16),
           ('fl-rail-btn', 'a3d-railbtn', 14), ('fl-logo', 'a3d-paneltoggle', 8),
           ('fl-collapse', 'a3d-panelcollapse', 4), ('fl-spacer', 'a3d-railspacer', 2),
           ('fl-file-head', 'a3d-projhead', 5), ('fl-file-title', 'a3d-projtitle', 4),
           ('fl-file-sub', 'a3d-projsub', 6), ('fl-pill', 'a3d-pill', 4), ('fl-tab-content', 'a3d-tabbody', 5),
           ('uc-input', 'a3d-cmdinput', 3), ('uc-results', 'a3d-cmdresults', 2), ('uc-row', 'a3d-cmdrow', 7),
           ('uc-key', 'a3d-cmdkey', 2), ('--figma-dock-w', '--a3d-left-w', 7)]
for old, new, n in RENAMES:
    rx = re.compile(r'(?<![\w-])' + re.escape(old) + r'(?![\w-])')
    got = len(rx.findall(t))
    if got != n:
        sys.exit('ABORT: %s occurs %d times, measured %d' % (old, got, n))
    if re.search(r'(?<![\w-])' + re.escape(new) + r'(?![\w-])', t):
        sys.exit('ABORT: %s is already in use' % new)
    t = rx.sub(new, t)
left = sorted(set(re.findall(r'(?<![\w-])(?:fl|uc)-[a-z][\w-]*', t)))
if left != ['fl-help']:
    sys.exit('ABORT: canvas-era class names left: %r' % left)
for gone in ('__figmaDockSyncW', 'data-a3dshell', 'data-fl-tab', '--j-grey', "data-tab','file'", 'data-tab="file"'):
    if gone in t:
        sys.exit('ABORT: %s is still in the file' % gone)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
