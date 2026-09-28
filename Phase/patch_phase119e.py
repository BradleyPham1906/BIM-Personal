"""patch_phase119e.py -- V119: the view's name follows what it names.

A3D_VIEW.name was written once, when a view was opened, and the HUD shows it. Anything that changed
what it named afterwards left the HUD naming something else:

  - the active level switched from the status bar or from Properties while a plan is open -- the plan
    is the active level's, and the Project Browser's mark moved to the new level while the HUD kept
    "Level 0 - Floor Plan"; the same for a level deleted while its plan is open (the next level
    becomes active) and for an undo that puts the active level back;
  - a saved view deleted while it is on screen, or undone away.

V116 handled one case of this -- a sheet renamed while open -- by re-deriving the sheet's name on
every refresh of the layout tabs. That is generalized to every view: bimViewSync re-derives the
record from what it names on every refresh of the lists those names live in, and a saved view that is
no longer there stops being the record -- it falls back to the view the camera is showing
(bimViewOfCamera), which moves nothing.

Three more writers of the saved-view mark go, leaving bimSetActiveView the one. Saving a view made
it the active saved view without recording it, so the Project Browser marked the new view and the HUD
named the old one; saving records it. Deleting the open view cleared the mark and left the record
naming it; the sync lets go of it. Undo restored the mark from its snapshot -- an undo is a model
change, not a navigation, and restoring the mark could mark a view that is not on screen -- so the
mark leaves the undo snapshot.

bimCameraIsPlan is the one test for "the camera is a plan": flat, no section, looking straight down.
A flat camera cannot orbit (a drag pans it), so a flat camera looks down, up, or along an elevation
preset -- which is what lets bimViewOfCamera name one."""
NAME = 'patch_phase119e.py'
BASE = '27d0903b7b8a86fc2a40242a451ee00de4d00e6f7c568ef3a5c0607662f656a8'
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
# ---- 1. the one test for a plan, the view a camera shows, and the record kept in step with its source
rep("    refreshHud();refreshBrowser();refreshProps();\n  }\n  function bimDeleteView(id){\n",
    r'''    refreshHud();refreshBrowser();refreshProps();
  }
  /* __acad3dV119: the camera is a plan -- flat, looking straight down, and not a section. "Flat" alone
     is not the test: an elevation is flat, and so is a section. */
  function bimCameraIsPlan(){
    return !!(A3D.flat&&!A3D.section&&A3D.cam.pitch>1.4);
  }
  /* __acad3dV119: the view the camera shows, for when no record names it. A flat camera cannot orbit
     (a drag pans it), so a flat camera that is not a plan looks straight up or along one of the
     elevation presets, and the nearest preset is the one it was set to. */
  function bimViewOfCamera(){
    var c=A3D.cam,k,d,dy,best=null,bd=1e9;
    if(A3D.section)return {kind:'section',id:null};
    if(!A3D.flat)return {kind:'3d',id:null};
    if(bimCameraIsPlan())return {kind:'plan',id:A3D.activeLevel};
    for(k in VIEWS){
      if(!VIEWS.hasOwnProperty(k)||!VIEWS[k].ortho||k==='top')continue;
      dy=c.yaw-VIEWS[k].yaw;
      d=Math.abs(Math.atan2(Math.sin(dy),Math.cos(dy)))+Math.abs(c.pitch-VIEWS[k].pitch);
      if(d<bd){bd=d;best=k;}
    }
    return {kind:'elev',id:best};
  }
  /* __acad3dV119: the record is re-derived from what it names on every refresh of the lists those
     names live in (the layout tabs, and so the Project Browser, which draws them first), because the
     HUD shows it. The plan is the active level's, so a level switched from the status bar or from
     Properties, deleted while its plan is open, or put back by an undo switches the plan with it. A
     saved view that is no longer there -- deleted while open, or undone away -- stops being the
     record, and the view the camera shows takes its place; nothing moves. V116 did this for a
     sheet's name, and a renamed sheet still renames its view here. */
  function bimViewSync(){
    var k=A3D_VIEW.kind,id=A3D_VIEW.id,f;
    if(k==='saved'&&!bimSavedViewById(id)){
      f=bimViewOfCamera();
      bimSetActiveView(f.kind,f.id,null);
      return;
    }
    if(k==='plan')id=A3D.activeLevel;
    var nm=bimViewLabelFor(k,id,null);
    if(id===A3D_VIEW.id&&nm===A3D_VIEW.name)return;
    A3D_VIEW={kind:k,id:id||null,name:nm};
    refreshHud();refreshProps();
  }
  function bimDeleteView(id){
''')

# ---- 2. a saved view's name is looked up when the view is not passed in
rep("    if(kind==='saved')return (sv&&sv.name)||'View';\n",
    "    if(kind==='saved'){\n      if(!sv)sv=bimSavedViewById(id);   /* __acad3dV119: the sync names views it did not open */\n"
    "      return (sv&&sv.name)||'View';\n    }\n")

# ---- 3. V116's sheet-name sync becomes every view's
rep("    /* a sheet renamed while it is open renames the view it is */\n"
    "    if(A3D_VIEW.kind==='sheet'){\n"
    "      var nm=bimViewLabelFor('sheet',A3D_VIEW.id);\n"
    "      if(nm!==A3D_VIEW.name){A3D_VIEW.name=nm;refreshHud();}\n"
    "    }\n",
    "    /* a sheet renamed while it is open renames the view it is -- __acad3dV119: and every view's\n"
    "       record is held to what it names */\n"
    "    bimViewSync();\n")

# ---- 4. saving a view records it; deleting or undoing it away is the sync's
rep("    A3D.activeViewId=v.id;\n    refreshViews();paint();saveSoon();\n",
    "    bimSetActiveView('saved',v.id,v);   /* __acad3dV119: the saved view is the one on screen, and named so */\n"
    "    refreshViews();paint();saveSoon();\n")
rep("        if(A3D.activeViewId===id)A3D.activeViewId=null;\n",
    "        /* __acad3dV119: the record lets go of it in bimViewSync, which refreshViews reaches */\n")

# ---- 5. an undo is a model change, not a navigation
rep("    return JSON.stringify({objs:A3D.objs,levels:A3D.levels,grids:A3D.grids,layers:A3D.layers,counts:A3D.counts,"
    "activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer,views:A3D.views,activeViewId:A3D.activeViewId,levelFilter:",
    "    return JSON.stringify({objs:A3D.objs,levels:A3D.levels,grids:A3D.grids,layers:A3D.layers,counts:A3D.counts,"
    "activeLevel:A3D.activeLevel,activeLayer:A3D.activeLayer,views:A3D.views,levelFilter:")
rep("    A3D.activeViewId=st.activeViewId||null;\n",
    "    /* __acad3dV119: the saved-view mark is not restored -- it follows the view on screen, which an\n"
    "       undo does not change; a saved view the undo removed is let go of by bimViewSync */\n")

# ---- the saved-view mark has one writer: bimSetActiveView. Besides it only the stored-state load
#      (which the boot's or the project's activation then overwrites) and the sheet capture's set and
#      restore around an off-screen render.
code = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
writers = re.findall(r'A3D\.activeViewId=(?!=)', code)
if len(writers) != 4:
    sys.exit('ABORT: A3D.activeViewId has %d writers, expected 4' % len(writers))
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
