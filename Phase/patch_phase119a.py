"""patch_phase119a.py -- V119: the view dropdown goes; the HUD names the active view.

The owner: "can we do a quick clean up of this drop down since i think it is redundant." The label in
the quick-access bar ("Level 0 - Floor Plan") opened a menu of two entries, Floor Plan and 3D View --
the same two views the Project Browser lists with every other view, and the status bar's 3D / plan
switch reaches. It goes: the label, its menu, the code that built and positioned the menu, and the
two test hooks that read it (__acadBuildWsMenu, __a3dWorkspaces).

The label was also the one place that NAMED the active view, which V84 made it do after it read
"Drafting & Annotation" over an isometric view. That name is not dropped with the control: the HUD's
View readout now shows it -- "Level 0 - Floor Plan", "3D View", "Front Elevation", a saved view's own
name, a sheet's number and name -- where it showed the camera's orientation word. One readout, fed by
the one record of the active view."""
NAME = 'patch_phase119a.py'
BASE = '10456654b6e4317e111ec5d3c2e3f1796dddb8f303bd391dd349700a2f6d811f'
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
import re
# ---- the control, in the quick-access bar
rep("'<div class=\"acad-ws\">Drafting &amp; Annotation <svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\"><path d=\"m6 9 6 6 6-6\"/></svg></div><div class=\"acad-spring\"></div>'",
    "'<div class=\"acad-spring\"></div>'")

# ---- its menu, and the label writer in the workspace code
rep("  // ============ 4. WORKSPACE DROPDOWN ============\n",
    "  // ============ 4. WORKSPACES: THE BOOT INTO THE BIM SHELL ============\n"
    "  /* __acad3dV119: this section was the workspace dropdown. The dropdown is gone -- the Project\n"
    "     Browser and the status bar switch views -- and what is left here is the boot into the BIM\n"
    "     shell and the ribbon tab sets it applies. The history below is kept for why they exist. */\n")
rep("  var ACAD_WS_LABEL={da:'Drafting &amp; Annotation','3d':'3D'};\n", "")
span("    /* __acad3dV84: the label reports the ACTIVE VIEW, not the workspace. Reporting the\n",
     "    return ws;\n  }\n  window.__acadApplyWorkspace=acadApplyWorkspace;\n",
     r'''    /* __acad3dV119: the label this used to write is gone with the dropdown; the HUD names the
       active view now, from the BIM engine's own record of it. */
''', 12)
span("  /* __acad3dV75: published here, NOT inside the function body -- an assignment in the body only\n",
     "  /* __acad3dV116: section 5, the canvas-era Model / Layout strip, is gone.",
     r'''  /* __acad3dV119: the dropdown's menu is gone -- the builder, its document click handler and the
     hook that published the builder. Its two entries, Floor Plan and 3D View, are two of the views
     the Project Browser lists, and the status bar's switch reaches both. */

''', 72)
rep("  function $(s){ return document.querySelector(s); }\n", "")

# ---- the BIM engine: the label writer, its calls and its hooks
span("  /* Returns true when it actually wrote the label, false when the element is not in the DOM --\n",
     "  /* kind: 'plan' | '3d' | 'elev' | 'saved' | 'sheet'\n", "", 13)
rep("    bimSyncViewLabel();\n    /* refreshProps too:", "    /* refreshProps too:")
rep("      if(nm!==A3D_VIEW.name){A3D_VIEW.name=nm;bimSyncViewLabel();refreshHud();}\n",
    "      if(nm!==A3D_VIEW.name){A3D_VIEW.name=nm;refreshHud();}\n")
rep("  window.__a3dSyncViewLabel=bimSyncViewLabel;\n", "")
span("  /* __acad3dV73: what the workspace menu actually offers, and the hit sizes a user has to click. */\n",
     "  window.__a3dHitSizes=function(){\n",
     "  /* __acad3dV73: the hit sizes a user has to click. (__a3dWorkspaces, which read the view dropdown's\n"
     "     menu, went with the dropdown in V119.) */\n", 13)

# ---- the HUD names the active view
rep("    if(el.view)el.view.textContent=(A3D_VIEW.kind==='sheet'&&bimSheetOnScreen())?A3D_VIEW.name:A3D.view;   /* __acad3dV116: on paper the view is the sheet */\n",
    r'''    /* __acad3dV119: the View readout names the active view -- "Level 0 - Floor Plan", "3D View", an
       elevation, a saved view by its own name, a sheet by its number and name. It showed the camera's
       orientation word (Plan, Isometric) and left the name to the view dropdown's label, which V119
       removed; one record of the active view now feeds the one readout. */
    if(el.view)el.view.textContent=A3D_VIEW.name;
''')

# ---- the words that still pointed at it: a startup warning that sent the user to the workspace menu,
#      and three comments that named the dropdown or its menu as a live reader
rep("      else console.warn('[BIM] Could not enter the drafting workspace on startup; the shell is '+\n"
    "        'reachable from the workspace menu.');\n",
    "      else console.warn('[BIM] Could not enter the drafting workspace on startup; reload the page to '+\n"
    "        'try again.');   /* __acad3dV119: it sent the user to the workspace menu, which is gone */\n")
rep("  /* The name shown in the ribbon label and used to mark the active row in the Project Browser.\n"
    "     `sv` is the saved-view record, passed in rather than looked up again so a view deleted\n"
    "     mid-activation cannot produce a blank label. */\n",
    "  /* The name of a view, as the HUD and Properties' View row show it (__acad3dV119: the ribbon label\n"
    "     that showed it went with the view dropdown). `sv` is the saved-view record, passed in rather\n"
    "     than looked up again so a view deleted mid-activation cannot produce a blank label. */\n")
rep("  /* __acad3dV116: the one label for a sheet -- layout tab, sheet toolbar, view menu, Project Browser\n",
    "  /* __acad3dV116: the one label for a sheet -- layout tab, sheet toolbar, HUD, Project Browser\n")
rep("     rather than keeping a second, slightly different copy of the camera logic. They are used\n"
    "     by startup and by the view menu, where an animated camera would be wrong, so neither\n"
    "     animates. */\n",
    "     rather than keeping a second, slightly different copy of the camera logic. They are used\n"
    "     by startup, where an animated camera would be wrong, so neither animates. */\n")

# ---- nothing is left that reads or writes the control
code = re.sub(r'<style\b[^>]*>.*?</style>', '', t, flags=re.S | re.I)
code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)
code = re.sub(r'(?m)^\s*//.*$', '', code)
for dead in ('acad-ws"', "acad-ws'", '.acad-ws', 'acad-wsmenu', 'data-wsm', 'wsm-', 'buildWsMenu', '__acadBuildWsMenu',
             '__a3dWorkspaces', 'bimSyncViewLabel', '__a3dSyncViewLabel', 'ACAD_WS_LABEL'):
    if dead in code:
        sys.exit('ABORT: the view dropdown is still referenced: ' + dead)
seg = t[t.index('(function acadWs2V1(){'):]
seg = seg[:seg.index('})();')]
if re.search(r'(?<![\w.])\$\(', re.sub(r'/\*.*?\*/', '', seg, flags=re.S)):
    sys.exit('ABORT: acadWs2V1 still calls the $ helper it no longer defines')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
