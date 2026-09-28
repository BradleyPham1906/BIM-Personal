"""patch_phase123c.py -- V123: click a handle and type; a click changes nothing.

Rhino's gumball: "click an arrow to type the moving distance, an arc to type the rotation angle, a
scale handle to type a scale factor." The gizmo only took a number during a drag. Now a click on
any handle -- a press that travels less than A3D_GIZ.click pixels -- opens a value box at the cursor
naming what it takes ("Move X", "Move X, Y", "Rotate Z", "Scale X", in the project's unit): Enter
applies it as one undo step through the path a drag ends by, Escape or a click elsewhere closes it
with nothing changed. The box is one component, bimValueBox, which V123's faces use too.

Two faults went with it, both found by clicking a handle on V122:

1. A plain click on a handle added an undo step that changed nothing: pushUndo ran on the press.
2. Ctrl+click on a move handle left a copy of the selection exactly on top of it -- invisible, and
   in the model: the copies were made on the press, and a press that never moved kept them.

Nothing happens on a press now. The undo step, and with Ctrl the copies, are made by the first
movement past the click distance (bimGizmoStartMoving), so the drag that follows is exactly the drag
there was, and a click is a click. The hover names a handle as V111 did; the status bar now says
what it does -- the drag, the click, and the modifiers its press reads -- from one function."""
NAME = 'patch_phase123c.py'
BASE = '742b6c98469386f85567f9ae01314339d3dfb7c9ee7681b3990d909559352a63'
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

# 1. the value box's look, beside the gizmo menu's
rep("""#a3d-gizmenu .a3d-gizmenu-sep{height:1px;background:#3a4048;margin:4px 2px}
""", """#a3d-gizmenu .a3d-gizmenu-sep{height:1px;background:#3a4048;margin:4px 2px}
#a3d-valbox{position:fixed;z-index:10070;display:flex;align-items:center;gap:6px;flex-wrap:wrap;max-width:300px;background:#22262b;border:1px solid #4ea1ff;border-radius:6px;padding:6px 8px;box-shadow:0 8px 24px rgba(0,0,0,.45);font:12px "Segoe UI",Inter,system-ui,sans-serif;color:#dfe4ea}
#a3d-valbox label{font-weight:600;white-space:nowrap}
#a3d-valbox input{width:104px;background:#15181c;border:1px solid #3a4048;border-radius:4px;color:#fff;padding:3px 6px;font:inherit}
#a3d-valbox .u{color:#8b949e}
#a3d-valbox .h{flex-basis:100%;color:#8b949e;font-size:11px}
#a3d-valbox .e{flex-basis:100%;color:#ff8a80;font-size:11px}
#a3d-valbox .e:empty{display:none}
""")

# 2. how far a press may travel and still be a click
rep("""               snapSrc:24,snapTgt:400,fine:0.25};           /* __acad3dV112 */""",
    """               snapSrc:24,snapTgt:400,fine:0.25,            /* __acad3dV112 */
               click:3,                                     /* __acad3dV123: a press that travels no further is a click, */
               clickWait:280};                              /* and its value box waits out a double-click */""")

# 3. the typed read-out's words come from what the handle takes
rep("""  function bimGizmoTypeLabel(dr){
    if(dr.rot)return 'ROTATE Z';
    if(dr.gk==='tilt')return 'ROTATE '+(dr.lab||'');
    if(dr.gk==='scale')return 'SCALE'+(dr.uniform?'':' '+bimGizAxis(dr.axis).lab);
    if(dr.gk==='axis')return bimGizAxis(dr.axis).lab;
    return 'MOVE';
  }""", """  /* __acad3dV123: the words of the value being typed, from the one function that names what a handle
     takes -- the value box a click opens says the same thing */
  function bimGizmoTypeLabel(dr){
    return bimGizmoValueLabel(dr).toUpperCase();
  }""")

# 4. the click, the first movement, the value box, and what a handle does
rep("""  /* Escape: the objects go back exactly where the press found them, and the gesture is over. */""",
"""  /* __acad3dV123: what a handle takes, in words: the value box's label, and in capitals the read-out
     of a value typed during a drag. From a picked handle or from a drag record. */
  function bimGizmoValueLabel(r){
    var k=r.gk||r.kind,kind=bimGizmoValueKind(r);
    if(r.rot)return 'Rotate Z';
    if(k==='tilt')return 'Rotate '+(r.lab||bimGizRingLab(r.arc||r.ring));
    if(k==='scale')return r.uniform?'Scale evenly':('Scale '+bimGizAxis(r.axis).lab);
    if(k==='uniform')return 'Scale evenly';
    if(k==='axis')return 'Move '+bimGizAxis(r.axis).lab;
    if(k==='plane'&&r.labA)return 'Move '+r.labA+', '+r.labB;
    if(k==='plane'&&r.plane&&r.plane.a)return 'Move '+bimGizAxis(r.plane.a).lab+', '+bimGizAxis(r.plane.b).lab;
    if(kind==='len3')return 'Move X, Y, Z';
    if(kind==='len2')return 'Move X, Y';
    return 'Move';
  }
  /* __acad3dV123: WHAT A HANDLE DOES, as the status bar says it while the cursor is on it: the drag,
     the click, and the modifiers its press reads -- the copy rule in onDown (Ctrl on a move handle),
     Shift and Alt in bimGizmoBegin, ORTHO's steps on a ring. The V123 suite drives each claim. */
  function bimGizmoHandleHint(h){
    if(!h)return '';
    var k=h.kind,kind=bimGizmoValueKind(h),what,mods;
    var ask=kind==='deg'?'an angle':(kind==='factor'?'a factor':(bimGizmoValueCount(kind)>1?'the distances':'a distance'));
    if(h.rot||k==='tilt'){what='drag to turn';mods='F8 turns in 15-degree steps, Shift is fine';}
    else if(k==='scale'){what='drag to stretch';mods='Shift scales evenly';}
    else if(k==='uniform'){what='drag to scale evenly';mods='';}
    else if(k==='centre'){what=A3D.flat?'drag to move in the plan':'drag to move across the screen';
      mods='Ctrl+drag copies, Alt+drag moves the pivot, Shift is fine';}
    else{what='drag to move';mods='Ctrl+drag copies, Shift is fine';}
    var nm=bimGizmoHandleName(h);
    return nm.charAt(0).toUpperCase()+nm.slice(1)+': '+what+', click to type '+ask+(mods?'; '+mods:'');
  }
  /* __acad3dV123: the first movement of a gizmo drag -- the moment it stops being a click. The undo
     step is taken here, and a Ctrl drag makes its copies here and carries on with them, exactly as
     V112's did from the press. */
  function bimGizmoStartMoving(d){
    if(d.undoPending){pushUndo();d.undoPending=false;}
    if(d.copyPending){
      d.copyPending=false;
      var made=bimGizmoCopySelection(d.ids);
      if(made){
        d.copies=made;
        d.ids=made.ids.slice();
        d.start=bimGizmoStarts(d.ids);
        d.snaps=bimGizmoSnapSetup(d.ids);
      }
    }
  }
  /* __acad3dV123: A CLICK ON A HANDLE -- Rhino's gumball. The box asks for what the handle takes; Enter
     applies it through a drag begun then, so its snapshots are of the model as it is, and ends it on
     the path every drag ends by, as one undo step. A Ctrl+click does nothing, as in Revit, and the
     pivot is only ever dragged. */
  var A3D_CLICKBOX_T=null;
  function bimGizmoClickValue(rec,ev){
    paint();
    if(!rec||rec.copyPending||!rec.hit)return false;
    var kind=bimGizmoValueKind(rec);
    if(!kind)return false;
    var hit=rec.hit,xy=rec.xy0.slice(),mods=rec.mods||{},cx=ev.clientX,cy=ev.clientY;
    /* opened once a double-click can no longer be under way: the second click of one takes a face
       (V123) and must not find a box in its way. Nothing opens over a drag begun meanwhile. */
    if(A3D_CLICKBOX_T)clearTimeout(A3D_CLICKBOX_T);
    A3D_CLICKBOX_T=setTimeout(function(){
      A3D_CLICKBOX_T=null;
      if(drag)return;
      bimValueBox({x:cx,y:cy,label:bimGizmoValueLabel(rec),
        unit:bimGizmoUnitSuffix(kind).replace(/^ /,''),value:'',
        hint:bimGizmoValueCount(kind)>1?'Numbers separated by commas; Enter to apply, Esc to cancel':'Enter to apply, Esc to cancel',
        submit:function(text){
          var now=bimGizmoIds(),was=(hit.giz&&hit.giz.ids)||[],i;
          if(now.length!==was.length)return 'The selection has changed - click the handle again';
          for(i=0;i<now.length;i++)if(was.indexOf(now[i])<0)return 'The selection has changed - click the handle again';
          var p=bimGizmoParseValue(kind,text);
          if(p.error)return p.error;
          A3D_MATERIALIZED=[];
          var fresh=bimGizmoBegin(hit,xy,mods);
          if(!fresh)return 'That handle cannot take a value now - see the message';
          drag=fresh;
          pushUndo();
          var summary=bimGizmoApplyValue(fresh,p.v,false);
          drag=null;
          bimGizmoEndDrag(summary);
          return null;
        }});
    },A3D_GIZ.clickWait);
    return true;
  }
  /* __acad3dV123: THE VALUE BOX -- Rhino's "click the handle and type", Revit's temporary dimension. One
     field beside the cursor, named for what it takes, in the project's unit. submit returns a message
     to show, or null when the value was applied; Escape, a click elsewhere or anything that takes
     the focus closes it with nothing changed. Keys typed in it are the value's: the app's shortcuts
     leave a focused field alone (bimKeyForControl). */
  var A3D_VALBOX=null;
  function bimValueBox(o){
    bimCloseValueBox();
    var host=el.root||document.body;
    var d=document.createElement('div');
    d.id='a3d-valbox';
    d.innerHTML='<label>'+bimEsc(o.label)+'</label><input type="text" spellcheck="false" autocomplete="off" aria-label="'+bimEsc(o.label)+'">'+
      (o.unit?'<span class="u">'+bimEsc(o.unit)+'</span>':'')+
      (o.hint?'<div class="h">'+bimEsc(o.hint)+'</div>':'')+'<div class="e"></div>';
    host.appendChild(d);
    var inp=d.querySelector('input'),er=d.querySelector('.e'),done=false;
    inp.value=(o.value===undefined||o.value===null)?'':String(o.value);
    var vw=window.innerWidth||1200,vh=window.innerHeight||800,w=d.offsetWidth||240,hh=d.offsetHeight||44;
    d.style.left=Math.max(4,Math.min((o.x||0)+14,vw-w-4))+'px';
    d.style.top=Math.max(4,Math.min((o.y||0)+14,vh-hh-4))+'px';
    function close(){
      if(done)return;
      done=true;
      if(d.parentNode)d.parentNode.removeChild(d);
      if(A3D_VALBOX&&A3D_VALBOX.el===d)A3D_VALBOX=null;
      if(o.onClose){try{o.onClose();}catch(eC){console.warn('[BIM] Value box close',eC);}}
      paint();bimSyncStatusHint();
    }
    inp.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){
        ev.preventDefault();ev.stopPropagation();
        var r;
        try{r=o.submit(inp.value);}
        catch(eV){console.warn('[BIM] The typed value could not be applied',eV);r='That value could not be applied - see the console';}
        if(r){er.textContent=r;inp.select();return;}
        close();
      }else if(ev.key==='Escape'){
        ev.preventDefault();ev.stopPropagation();close();
      }
    });
    inp.addEventListener('blur',function(){setTimeout(close,0);});
    A3D_VALBOX={el:d,close:close,label:o.label,input:inp,err:er};
    inp.focus();
    if(inp.value)inp.setSelectionRange(inp.value.length,inp.value.length);
    return d;
  }
  function bimCloseValueBox(){if(A3D_VALBOX)A3D_VALBOX.close();}
  /* Escape: the objects go back exactly where the press found them, and the gesture is over. */""")

# 5. the press, the first movement, the release
rep("""      if(gz&&(!gctrl||gcopy)){
        bimCloseGizmoMenu();
        A3D_MATERIALIZED=[];
        var made=null,ghit=gz;
        if(gctrl&&gcopy){
          pushUndo();
          made=bimGizmoCopySelection(gz.giz.ids);
          if(made){paint();ghit=bimPickGizmo(xy[0],xy[1])||gz;}
        }
        var gd=bimGizmoBegin(ghit,xy,ev);
        if(gd){
          if(made)gd.copies=made;else pushUndo();
          drag=gd;
          paint();
        }else if(made){bimGizmoDropCopies(made);paint();}
        ev.preventDefault();
        return;
      }""", """      if(gz&&(!gctrl||gcopy)){
        bimCloseGizmoMenu();
        A3D_MATERIALIZED=[];
        var gd=bimGizmoBegin(gz,xy,ev);
        if(gd){
          /* __acad3dV123: nothing happens on the press. The undo step and, with Ctrl, the copies are
             made by the first movement (bimGizmoStartMoving): a click opens the handle's value box
             and changes nothing. On V122 a click added an empty undo step, and a Ctrl+click left a
             copy of the selection on top of it. */
          gd.undoPending=true;
          if(gctrl&&gcopy)gd.copyPending=true;
          gd.hit=gz;gd.xy0=xy.slice();gd.mods={shiftKey:!!ev.shiftKey};
          drag=gd;
          paint();
        }
        ev.preventDefault();
        return;
      }""")
rep("""    if(drag.rot){
      if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>1||Math.abs(xy[1]-drag.y0)>1))drag.moved=true;
      bimGizmoApplyRotate(xy);
      return;
    }
    if(drag.giz){
      if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>1||Math.abs(xy[1]-drag.y0)>1))drag.moved=true;
      bimGizmoApply(xy);
      return;
    }""", """    if(drag.rot||drag.giz){
      /* __acad3dV123: a press that has not travelled A3D_GIZ.click pixels is still a click, and a
         click changes nothing. The first real movement takes the undo step and makes any copies;
         the drag then runs from where it was pressed, so nothing jumps. */
      if(!drag.moved){
        if(Math.abs(xy[0]-drag.x0)<=A3D_GIZ.click&&Math.abs(xy[1]-drag.y0)<=A3D_GIZ.click)return;
        drag.moved=true;
        bimGizmoStartMoving(drag);
      }
      if(drag.rot)bimGizmoApplyRotate(xy);else bimGizmoApply(xy);
      return;
    }""")
rep("""    var wasGiz=drag.giz,gizIds=drag.ids,gizKind=drag.gk,gizVec=drag.gizVec;   /* __acad3dV110 */""",
    """    var wasGiz=drag.giz,gizIds=drag.ids,gizKind=drag.gk,gizVec=drag.gizVec;   /* __acad3dV110 */
    var gizRec=(drag.giz||drag.rot)?drag:null;                                  /* __acad3dV123 */""")
rep("""    if(wasRot||wasGiz){
      /* __acad3dV112: one end-of-drag path, so a drag finished with the mouse and a drag finished
         by typing an exact value settle identically. */""", """    if(wasRot||wasGiz){
      if(!moved&&gizRec){   /* __acad3dV123: a click on a handle asks for a value; nothing has changed */
        bimGizmoClickValue(gizRec,ev);
        return;
      }
      /* __acad3dV112: one end-of-drag path, so a drag finished with the mouse and a drag finished
         by typing an exact value settle identically. */""")

# 6. the status bar says what the handle under the cursor does
rep("""      if(hk!==A3D.gizHover){
        A3D.gizHover=hk;
        A3D.gizHoverName=hh?bimGizmoHandleName(hh).replace(/^the /,'').toUpperCase():null;
        paint();
      }""", """      if(hk!==A3D.gizHover){
        A3D.gizHover=hk;
        A3D.gizHoverName=hh?bimGizmoHandleName(hh).replace(/^the /,'').toUpperCase():null;
        A3D.gizHoverHint=hh?bimGizmoHandleHint(hh):null;   /* __acad3dV123 */
        bimSyncStatusHint();
        paint();
      }""")
rep("""    n=(A3D.selSet&&A3D.selSet.length)||0;
    if(n>1)return n+' objects selected';""", """    /* __acad3dV123: the handle under the cursor, and what it does -- set by onHover, cleared the
       moment the cursor leaves it */
    if(A3D.gizHover&&A3D.gizHoverHint&&!drag&&A3D.gizmo)return A3D.gizHoverHint;
    n=(A3D.selSet&&A3D.selSet.length)||0;
    if(n>1)return n+' objects selected';""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
