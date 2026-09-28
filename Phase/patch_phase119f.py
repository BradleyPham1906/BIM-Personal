"""patch_phase119f.py -- V119: a section is a view.

A section changes what is on screen as much as any view switch -- the camera turns sideways and the
model is cut -- and it told the record nothing. Drawn with the tool from the plan, the HUD went on
saying "Level 0 - Floor Plan" over the cut, the Project Browser marked the plan, and Properties said
the same. Exit Section put the camera back, and the record had never moved.

Now a section records itself ('Section'), remembers the view it was cut from, and Exit Section goes
back to that view, the record with the camera. The Model tab can come back to a section a sheet was
opened over (the section stays live under the sheet), so bimActivateView knows the kind.

A saved section view goes back to where the model was before it, as a drawn section does. It used to
stay at the section's own angle with the cut gone, still named Section."""
NAME = 'patch_phase119f.py'
BASE = 'ef02bc31d50eba7b6d8a4f58036527352ad724d7b039819ac6f97f60ca494778'
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
# ---- 1. its name, and the kind bimActivateView can open
rep("    return '3D View';\n  }\n",
    "    if(kind==='section')return 'Section';   /* __acad3dV119 */\n    return '3D View';\n  }\n")
rep("  /* kind: 'plan' | '3d' | 'elev' | 'saved' | 'sheet'\n"
    "     id:   level id / (none) / VIEWS preset key / saved view id / sheet id\n",
    "  /* kind: 'plan' | '3d' | 'elev' | 'saved' | 'sheet' | 'section'\n"
    "     id:   level id / (none) / VIEWS preset key / saved view id / sheet id / (none: the live section)\n")
rep("      }else if(kind==='sheet'){\n        if(!bimSheetById(id)){\n",
    r'''      }else if(kind==='section'){
        /* __acad3dV119: the live section, which a sheet opened over it leaves in place -- the Model
           tab comes back to it. There is one at a time, so it has no id. */
        if(!A3D.section){
          console.warn('[BIM] There is no open section to go back to.');
          a3dToast('That section is no longer open');
          return false;
        }
        id=null;
      }else if(kind==='sheet'){
        if(!bimSheetById(id)){
''')

# ---- 2. the tool remembers the view it was started from
rep("    var origCam={yaw:c0.yaw,pitch:c0.pitch,dist:c0.dist,tx:c0.tx,ty:c0.ty,tz:c0.tz,flat:A3D.flat,view:A3D.view};\n"
    "    if(!A3D.flat)toggleFlat();\n",
    "    var origCam={yaw:c0.yaw,pitch:c0.pitch,dist:c0.dist,tx:c0.tx,ty:c0.ty,tz:c0.tz,flat:A3D.flat,view:A3D.view,\n"
    "      record:{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};   /* __acad3dV119: the view to come back to */\n"
    "    if(!A3D.flat)toggleFlat();\n")

# ---- 3. a saved section view goes back to where the model was before it
rep("    if(A3D.section)bimExitSection();\n    var c=A3D.cam;\n    c.yaw=v.cam.yaw;",
    r'''    if(A3D.section)bimExitSection();
    var c=A3D.cam;
    /* __acad3dV119: where the model was before this view. A section view's Exit goes back there, as a
       section drawn with the tool does, the record with the camera; it used to stay at the section's
       own angle with the cut gone, still named Section. From a sheet: the model view the sheet was
       opened from, whose camera is still the model's. */
    var back={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz,flat:A3D.flat,view:A3D.view,
      record:(A3D_VIEW.kind==='sheet')?(A3D_LAST_MODEL_VIEW||{kind:'plan',id:A3D.activeLevel})
                                      :{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};
    c.yaw=v.cam.yaw;''')
rep("      var origCam={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz,flat:A3D.flat,view:A3D.view};\n"
    "      bimEnterSection(v.section.p,v.section.dir,origCam);\n",
    "      bimEnterSection(v.section.p,v.section.dir,back);   /* __acad3dV119 */\n")

# ---- 4. going in records the section; coming out goes back to the view it was cut from
rep("      prevCam:origCam,prevFlat:origCam.flat,prevView:origCam.view};\n    bimAimSectionCamera();\n",
    r'''      prevCam:origCam,prevFlat:origCam.flat,prevView:origCam.view,
      prevRecord:origCam.record||{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};   /* __acad3dV119: the view it was cut from */
    bimAimSectionCamera();
    /* __acad3dV119: a section is a view. The HUD names it, and the Project Browser and Properties stop
       naming the plan it was drawn in. Opened as part of a saved view, the saved view records itself
       when its activation finishes. */
    if(A3D_VIEW.kind!=='sheet')bimSetActiveView('section',null,null);
''')
rep("    var prev=A3D.section.prevCam,prevFlat=A3D.section.prevFlat,prevView=A3D.section.prevView;\n",
    "    var prev=A3D.section.prevCam,prevFlat=A3D.section.prevFlat,prevView=A3D.section.prevView,\n"
    "        rec=A3D.section.prevRecord;   /* __acad3dV119 */\n")
rep("    A3D.section=null;\n    refreshHud();paint();saveSoon();\n    a3dToast('Exited section view');\n",
    r'''    A3D.section=null;
    /* __acad3dV119: back to the view the section was cut from, the record with the camera. A record
       that is not a model view to go back to (a sheet, a section) gives way to the view the camera
       now shows. With a sheet on screen -- a view switch that closes the sheet ends the section before
       it records its own view -- the sheet stays the view, and the Model tab's way back, if it named
       this section, is pointed at the view the section came from. */
    if(!rec||rec.kind==='sheet'||rec.kind==='section')rec=bimViewOfCamera();
    if(A3D_VIEW.kind==='sheet'){
      if(A3D_LAST_MODEL_VIEW&&A3D_LAST_MODEL_VIEW.kind==='section')
        A3D_LAST_MODEL_VIEW={kind:rec.kind,id:rec.id,cam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz}};
      refreshHud();
    }else bimSetActiveView(rec.kind,rec.id,null);
    paint();saveSoon();
    a3dToast('Exited section view');
''')
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
