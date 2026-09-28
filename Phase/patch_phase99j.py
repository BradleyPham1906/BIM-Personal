"""patch_phase99j.py -- __acad3dV99: two defects the V99 suite found in existing code.

1. A BODY DRAG TELEPORTED the object. The single-object drag set pos to the ground point under
   the cursor, so the object's LOCAL ORIGIN jumped under the cursor. For a primitive built round
   its origin that looks right; for a sketch, line, construction line, dimension or room --
   whose points are stored in world terms with pos 0 -- a small drag threw the object across the
   plan by its distance from the origin. The group drag already moved by the delta from where it
   was grabbed; the single drag now does the same, by recording the grab offset.

2. A CONSEQUENCE TOAST WAS OVERWRITTEN by the action's own summary. The toast has one slot, so
   "Room_1 is no longer enclosed" raised during a delete was replaced, in the same instant, by
   "1 object(s) deleted" and never seen. Toasts raised in the same turn of the event loop are
   now stacked as lines of one toast (the last four), so a consequence cannot be hidden by the
   action that caused it.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '72aba1ee4e8d5a85cf130a9a93776221b4b9e113cdca43c29e33900cb7cd20b4'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""        drag.mv=hit;drag.my=hit.pos[1];drag.vert=ev.altKey;
        drag.mvObjStart=[hit.pos[0],hit.pos[1],hit.pos[2]];""",
     """        drag.mv=hit;drag.my=hit.pos[1];drag.vert=ev.altKey;
        drag.mvObjStart=[hit.pos[0],hit.pos[1],hit.pos[2]];
        /* __acad3dV99: where on the object it was grabbed, so it moves by the drag, not to it */
        var gGrab=groundPoint(xy[0],xy[1],drag.my);
        drag.mvGrab=gGrab?[gGrab[0]-hit.pos[0],gGrab[2]-hit.pos[2]]:[0,0];"""),
    ("""      var g=groundPoint(xy[0],xy[1],drag.my);
      if(g){drag.mv.pos[0]=g[0];drag.mv.pos[2]=g[2];paint();saveSoon();}""",
     """      var g=groundPoint(xy[0],xy[1],drag.my);
      if(g){   /* __acad3dV99: by the grab offset -- it used to jump its origin under the cursor */
        var gb=drag.mvGrab||[0,0];
        drag.mv.pos[0]=g[0]-gb[0];drag.mv.pos[2]=g[2]-gb[1];paint();saveSoon();
      }"""),
    ("""      tx.textContent=msg;tx.style.opacity='1';
      if(a3dToast._t)clearTimeout(a3dToast._t);""",
     """      /* __acad3dV99: toasts raised in the same turn stack, so a consequence is not hidden
         by the summary of the action that caused it */
      if(a3dToast._same&&tx.textContent){
        var lines=(tx.textContent+'\\n'+msg).split('\\n');
        tx.textContent=lines.slice(Math.max(0,lines.length-4)).join('\\n');
      }else tx.textContent=msg;
      tx.style.whiteSpace='pre-line';
      if(!a3dToast._same){a3dToast._same=true;setTimeout(function(){a3dToast._same=false;},0);}
      tx.style.opacity='1';
      if(a3dToast._t)clearTimeout(a3dToast._t);"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
