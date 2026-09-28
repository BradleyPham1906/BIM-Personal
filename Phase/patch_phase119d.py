"""patch_phase119d.py -- V119: every view switch goes through the record of the active view.

V119a made the HUD name the active view from A3D_VIEW, the record bimActivateView keeps. The record
was right for everything that opened a view through bimActivateView -- and nothing else. Measured on
V118 before this patch, after one click on the status bar's 3D / 2D switch:

    camera flat:false, view 'Home'      record: plan, 'Level 0 - Floor Plan'
    Project Browser mark: the plan      Properties View row: 'Level 0 - Floor Plan'

That was already wrong in V118 (the mark and Properties read the record); the HUD made it visible.
The same mistake, found by grepping for every other path that moves the camera between views:

  - toggleFlat: the status bar's switch, the '>' key, and every drafting tool that drops a 3D view
    to the plan.
  - setView: the ViewCube's faces and its Home, the View tab's Top / Front / Right / 3D View / Home,
    and the __a3dSetView hook. setView is renamed bimAimPreset -- the camera move bimActivateView
    uses -- and setView itself now opens the preset's view through bimActivateView.
  - fitScene, with nothing to fit, called setView('home'): Fit to Model in an empty plan swung the
    camera into 3D. With nothing to fit the framing is reset and the direction kept.
  - the hidden saved-views list's Go button and the __a3dApplyView hook called bimApplyView directly.
  - __a3dFlat() with no argument read as "flat: false" and turned a plan into 3D. __a3dShellGeom
    called it that way, to ask which mode it was in. Without an argument it is now a question.

The tail of bimActivateView becomes bimSetActiveView -- the record, the saved view marked as on screen,
the ribbon tab set, and the HUD, Project Browser and Properties that read them -- and each of those
paths ends in it. The saved-view mark is set there and nowhere else in a switch: bimActivateView's
branches cleared it one by one, and the switch did not clear it at all, so after a flip away from a
saved view the Project Browser marked two views."""
NAME = 'patch_phase119d.py'
BASE = '2960d6e12477842a9db91b717693abfc913ab4f04c65f07d186066293f8913d3'
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
# ---- 1. the tail of bimActivateView becomes the one place a view switch is recorded
OLD_TAIL = r'''    A3D_VIEW={kind:kind,id:id||null,name:bimViewLabelFor(kind,id,sv)};
    /* The ribbon FOLLOWS the view. keepActive:true so a tab present in both tool sets stays
       put: the ribbon changes only when the new view makes the current tab unavailable, which
       is far less jarring than resetting to the first tab on every view change. */
    var ws=(kind==='3d'||(kind==='saved'&&sv&&!sv.flat))?'3d':'da';
    window.ACAD_WS_CUR=ws;
    try{if(window.__acadApplyWorkspace)window.__acadApplyWorkspace(ws,{keepActive:true});}
    catch(eW){console.warn('[BIM] The ribbon could not follow the view change.',eW);}
    /* refreshProps too: without it the Properties panel keeps its boot-time render, which is
       how a panel reading "View 3D" ended up sitting beside a status bar reading "View: Plan"
       in the Phase 84 visual review. */
    refreshHud();refreshBrowser();refreshProps();paint();saveSoon();
    return true;
  }
'''
NEW_TAIL = r'''    bimSetActiveView(kind,id,sv);   /* __acad3dV119: the record, and everything that reads it */
    paint();saveSoon();
    return true;
  }
  /* __acad3dV119: the record of the view on screen, and the readouts that follow it. Every view
     switch ends here -- bimActivateView, the plan / 3D switch, a section going in and coming back
     out -- because the HUD names the active view now, and a switch that went around the record left
     the HUD, the Project Browser's marks and Properties all naming the view before it. `sv`, the
     saved view, is looked up when it is not passed. */
  function bimSavedViewById(id){
    var q;
    for(q=0;q<A3D.views.length;q++)if(A3D.views[q].id===id)return A3D.views[q];
    return null;
  }
  function bimSetActiveView(kind,id,sv){
    if(kind==='saved'&&!sv)sv=bimSavedViewById(id);
    A3D_VIEW={kind:kind,id:id||null,name:bimViewLabelFor(kind,id,sv)};
    /* The saved view on screen is the record's, and nothing else's: the Project Browser marks it
       and new annotations are tagged with it, so it is set here with the record and cleared by
       every switch away from it. */
    A3D.activeViewId=(kind==='saved')?(id||null):null;
    /* The ribbon FOLLOWS the view. keepActive:true so a tab present in both tool sets stays
       put: the ribbon changes only when the new view makes the current tab unavailable, which
       is far less jarring than resetting to the first tab on every view change. */
    var ws=(kind==='3d'||(kind==='saved'&&sv&&!sv.flat))?'3d':'da';
    window.ACAD_WS_CUR=ws;
    try{if(window.__acadApplyWorkspace)window.__acadApplyWorkspace(ws,{keepActive:true});}
    catch(eW){console.warn('[BIM] The ribbon could not follow the view change.',eW);}
    /* refreshProps too: without it the Properties panel keeps its boot-time render, which is
       how a panel reading "View 3D" ended up sitting beside a status bar reading "View: Plan"
       in the Phase 84 visual review. */
    refreshHud();refreshBrowser();refreshProps();
  }
'''
rep(OLD_TAIL, NEW_TAIL)

# ---- 2. the plan / 3D switch records the view it switched to
rep("    if(el.root)el.root.classList.toggle('flat',A3D.flat);\n    refreshHud();paint();saveSoon();\n  }\n",
    r'''    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    /* __acad3dV119: the switch is a view switch like any other, and records one. The status bar's
       3D / 2D, the '>' key and every drafting tool that drops a 3D view to the plan went around the
       record, so the HUD went on naming the view before -- as the Project Browser's mark and the
       Properties View row had since V84. A saved view is left, as any view switch leaves it. On a
       sheet the switch turns the model's camera behind the paper, and the sheet is still the view. */
    if(A3D_VIEW.kind!=='sheet')bimSetActiveView(A3D.flat?'plan':'3d',A3D.flat?A3D.activeLevel:null,null);
    else refreshHud();
    paint();saveSoon();
  }
''')

# ---- 3. a preset is a view: setView opens it through bimActivateView; the camera move is bimAimPreset
rep("  function setView(name,anim){\n    var v=VIEWS[name];if(!v)return;\n",
    r'''  /* __acad3dV119: a preset is a view, and opens as one. The ViewCube's faces and its Home, the View
     tab's Top / Front / Right / 3D View / Home and the __a3dSetView hook all moved the camera below
     directly, so none of them told the record: after a click on the cube's Front face the HUD, the
     Project Browser and Properties went on naming the plan. They open the view through the one
     activation path now -- which also leaves a section behind, as every other view switch does.
     Top is the floor plan of the active level; Home and Isometric are the 3D view, Home framed
     afresh; the other faces are elevations. */
  function setView(name,anim){
    var v=VIEWS[name],o={anim:anim!==false};
    if(!v)return false;
    if(name==='top')return bimActivateView('plan',null,o);
    if(!v.ortho){o.home=(name==='home');return bimActivateView('3d',null,o);}
    return bimActivateView('elev',name,o);
  }
  /* The camera move itself, which bimActivateView makes for a plan, the 3D view and an elevation. */
  function bimAimPreset(name,anim){
    var v=VIEWS[name];if(!v)return;
''')
rep("        setView('top',anim);\n        /* setView would name this 'Top (Plan)'. The HUD and the status bar have said 'Plan'\n"
    "           since V18 and other code reads that string, so keep it. */\n        A3D.view='Plan';\n        A3D.activeViewId=null;\n",
    "        bimAimPreset('top',anim);\n        /* bimAimPreset would name this 'Top (Plan)'. The camera's word has been 'Plan' since V18\n"
    "           and other code reads that string, so keep it. */\n        A3D.view='Plan';\n")
rep("        setView('iso',anim);\n        A3D.activeViewId=null;\n",
    "        bimAimPreset(opts.home?'home':'iso',anim);   /* __acad3dV119: Home is the 3D view, framed afresh */\n")
rep("        setView(id,anim);\n        A3D.activeViewId=null;\n", "        bimAimPreset(id,anim);\n")

# ---- 4. Fit to Model with nothing to fit keeps the view
rep("  function fitScene(){\n",
    r'''  /* __acad3dV119: with nothing to fit, the framing goes back to the default and the direction stays --
     an empty plan is still a plan. fitScene used to open the Home view here, a switch to 3D: Fit to
     Model in an empty plan swung the camera into 3D, and a section aimed at an empty model turned
     into a 3D view. */
  function bimFrameNothing(){
    var c=A3D.cam;
    c.dist=DEFCAM.dist;c.tx=DEFCAM.tx;c.ty=DEFCAM.ty;c.tz=DEFCAM.tz;
    paint();saveSoon();
  }
  function fitScene(){
''')
rep("    if(!A3D.objs.length){setView('home');return;}\n", "")   # no objects is no bounds: one test, below
rep("    if(!bb){setView('home');return;}\n", "    if(!bb){bimFrameNothing();return;}\n")

# ---- 5. the saved view paths that called bimApplyView directly; and it no longer marks the view
#      itself -- bimSetActiveView does, when the activation finishes
rep("    A3D.levelFilter=!!v.levelFilter;\n    A3D.activeViewId=v.id;\n", "    A3D.levelFilter=!!v.levelFilter;\n")
rep("      if(goBtn){ev.stopPropagation();bimApplyView(goBtn.getAttribute('data-viewgo'));return;}\n",
    "      if(goBtn){ev.stopPropagation();bimActivateView('saved',goBtn.getAttribute('data-viewgo'));return;}   /* __acad3dV119 */\n")
rep("  window.__a3dApplyView=bimApplyView;\n",
    "  window.__a3dApplyView=function(id){return bimActivateView('saved',id);};   /* __acad3dV119: through the record */\n")

# ---- 6. a question changes nothing
rep("  window.__a3dFlat=function(on){\n    if(!!on!==A3D.flat)toggleFlat();\n",
    r'''  window.__a3dFlat=function(on){
    /* __acad3dV119: with no argument this is a question, and a question changes nothing. It read as
       "flat: false" and turned a plan into 3D -- which __a3dShellGeom did on every call, to find out
       which mode it was in. */
    if(on!==undefined&&!!on!==A3D.flat)toggleFlat();
''')

# ---- nothing moves the camera between views around the record
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
calls = re.findall(r'(?<![\w.])setView\(', code)
defs = re.findall(r'function setView\(', code)
if len(calls) != len(defs) + 5:
    sys.exit('ABORT: setView is called %d times, expected 5 (the cube x2, the ribbon x2, the hook)' % (len(calls) - len(defs)))
if len(re.findall(r'(?<![\w.])bimApplyView\(', code)) != 2:
    sys.exit('ABORT: bimApplyView is reached other than through bimActivateView')
if len(re.findall(r'(?<![\w.])bimAimPreset\(', code)) != 4:
    sys.exit('ABORT: bimAimPreset is used other than by bimActivateView')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
