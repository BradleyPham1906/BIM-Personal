"""patch_phase94g.py -- __acad3dV94: the letters V, H and N never reached the drawing.

Found while driving XLINE's mode keys: pressing V or H did nothing, while A worked.

A guard from the retired Canvas shell -- "Capture before the old single-key shortcut listener.
Plain letters are now always typing-safe." -- is registered on window in the CAPTURE phase at
load, long before the BIM engine's own key handler, and calls stopImmediatePropagation on plain
v, h and n. So in the drafting workspace those three letters have never reached the drawing at
all. It was right for Canvas, where V meant "select tool"; it is wrong for a CAD workspace where
H and V mean Horizontal and Vertical.

The file already makes exactly this exemption for z, y and d ("The 3D/BIM workspace owns its own
undo stack and duplicate command while it is on screen"), so the shape of the fix is settled.
What is NOT acceptable is a second hand-written list of letters the drafting engine cares about:
that list would drift from the handlers the moment a phase adds a key. So the gate ASKS the
engine, through one predicate, and the engine answers from the same table its own handler
dispatches on.

That table is the second half of this patch. The in-sketch letter handlers were five separate
if-statements repeating their own conditions; they are now one ordered list of {test, run},
which onKey dispatches through and which __a3dWantsKey queries. A key the drawing will consume
and a key the gate lets through cannot disagree, because there is one answer to both questions.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '2e74c1a10833bb627292740201fd17ea8d0768b5e5d2d627b09dbbffcca38c6e'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD_HANDLERS = """        /* __acad3dV94: XLINE's construction modes, claimed before any other tool's letters so
           the match is explicit rather than a consequence of branch order. */
        if(A3D.sk.tool==='xline'&&!ev.ctrlKey&&!ev.metaKey&&bimClineCanSetMode(A3D.sk)){
          var clMode=bimClineModeForKey(ev.key);
          if(clMode){
            bimSetClineMode(A3D.sk,clMode);
            ev.preventDefault();ev.stopImmediatePropagation();return;
          }
        }
        if((ev.key==='u'||ev.key==='U')&&!ev.ctrlKey&&!ev.metaKey&&A3D.sk.pts.length){
          bimUndoLastPoint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        /* __acad3dV90: A switches to arc segments, L back to straight - PLINE's own keys. */
        if((ev.key==='a'||ev.key==='A')&&!ev.ctrlKey&&!ev.metaKey&&bimCanArc(A3D.sk)&&!A3D.sk.arcMode){
          bimSetArcMode(A3D.sk,true);ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if((ev.key==='l'||ev.key==='L')&&!ev.ctrlKey&&!ev.metaKey&&A3D.sk.arcMode){
          bimSetArcMode(A3D.sk,false);ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if((ev.key==='c'||ev.key==='C')&&!ev.ctrlKey&&!ev.metaKey&&bimCanClose(A3D.sk)){
          bimCloseCurrent();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Enter'||ev.key===' '){
          bimFinishCurrent();ev.preventDefault();ev.stopImmediatePropagation();return;
        }"""

NEW_HANDLERS = """        /* __acad3dV94: one ordered table instead of five if-statements that each restated
           their own condition. onKey dispatches through it and __a3dWantsKey queries it, so
           "will the drawing consume this letter" has exactly one answer. */
        var skHit=bimSketchKeyFor(A3D.sk,ev);
        if(skHit){
          skHit.run(A3D.sk,ev);
          ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Enter'||ev.key===' '){
          bimFinishCurrent();ev.preventDefault();ev.stopImmediatePropagation();return;
        }"""

assert txt.count(OLD_HANDLERS) == 1, 'handler anchor count %d' % txt.count(OLD_HANDLERS)
txt = txt.replace(OLD_HANDLERS, NEW_HANDLERS, 1)

# the table itself, beside the predicates it consults
OLD_TBL = """  function bimPromptOpts(sk){"""
NEW_TBL = """  /* __acad3dV94: the letters a point-taking tool claims, in the order they are tried. Each
     entry's test is the SAME predicate the prompt's bracket list is built from, so a key and
     the prompt that advertises it cannot drift apart -- and the Canvas-era shortcut gate can
     ask this table rather than keeping a list of its own. */
  var BIM_SKETCH_KEYS=[
    {name:'clineMode',
     test:function(sk,ev){
       return sk.tool==='xline'&&bimClineCanSetMode(sk)&&!!bimClineModeForKey(ev.key);},
     run:function(sk,ev){bimSetClineMode(sk,bimClineModeForKey(ev.key));}},
    {name:'undo',
     test:function(sk,ev){return (ev.key==='u'||ev.key==='U')&&!!(sk.pts&&sk.pts.length);},
     run:function(){bimUndoLastPoint();}},
    /* __acad3dV90: A switches to arc segments, L back to straight - PLINE's own keys. */
    {name:'arcOn',
     test:function(sk,ev){return (ev.key==='a'||ev.key==='A')&&bimCanArc(sk)&&!sk.arcMode;},
     run:function(sk){bimSetArcMode(sk,true);}},
    {name:'arcOff',
     test:function(sk,ev){return (ev.key==='l'||ev.key==='L')&&!!sk.arcMode;},
     run:function(sk){bimSetArcMode(sk,false);}},
    {name:'close',
     test:function(sk,ev){return (ev.key==='c'||ev.key==='C')&&bimCanClose(sk);},
     run:function(){bimCloseCurrent();}}
  ];
  function bimSketchKeyFor(sk,ev){
    if(!sk||!ev||ev.ctrlKey||ev.metaKey)return null;
    if(!BIM_COORD_TOOLS[sk.tool])return null;
    var i;
    for(i=0;i<BIM_SKETCH_KEYS.length;i++)
      if(BIM_SKETCH_KEYS[i].test(sk,ev))return BIM_SKETCH_KEYS[i];
    return null;
  }
  function bimPromptOpts(sk){"""
assert txt.count(OLD_TBL) == 1, 'table anchor count %d' % txt.count(OLD_TBL)
txt = txt.replace(OLD_TBL, NEW_TBL, 1)

# the predicate the Canvas-era gate consults
OLD_EXP = """  /* __acad3dV94 */
  window.__a3dClipInfinite=bimClipInfinite;"""
NEW_EXP = """  /* __acad3dV94: asked by the Canvas-era shortcut gate before it swallows a plain letter.
     True only when the drawing will actually consume it, so a letter the drafting engine does
     not want is still swallowed exactly as it was. */
  window.__a3dWantsKey=function(ev){
    try{
      if(!A3D.on||!ev)return false;
      var tg=ev.target;
      if(tg&&(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable))return false;
      if(el.dlg||A3D_TYPING.active)return false;
      return !!(A3D.sk&&bimSketchKeyFor(A3D.sk,ev));
    }catch(eW){console.warn('[BIM] Key claim check failed',eW);return false;}
  };
  window.__a3dSketchKeyNames=function(){
    return BIM_SKETCH_KEYS.map(function(k){return k.name;});
  };
  /* __acad3dV94 */
  window.__a3dClipInfinite=bimClipInfinite;"""
assert txt.count(OLD_EXP) == 1, 'export anchor count %d' % txt.count(OLD_EXP)
txt = txt.replace(OLD_EXP, NEW_EXP, 1)

# the gate itself: ask, do not keep a list
OLD_GATE = """    if(runShortcut(e)){e.stopImmediatePropagation();return;}
    if(['v','h','n'].includes(k) && !mod){e.stopImmediatePropagation();return;}
  },true);"""
NEW_GATE = """    if(runShortcut(e)){e.stopImmediatePropagation();return;}
    if(['v','h','n'].includes(k) && !mod){
      /* __acad3dV94: this guard is registered in the CAPTURE phase at load, ahead of the BIM
         engine's own key handler, so for as long as it has existed the letters V, H and N have
         never reached the drafting workspace at all -- and in a CAD workspace H and V mean
         Horizontal and Vertical. The same exemption this file already makes for z, y and d,
         except that the decision is DELEGATED rather than duplicated: the drawing is asked
         whether it wants the key, so this gate never needs a list of its own to keep in step. */
      try{ if(window.__a3dOn&&window.__a3dWantsKey&&window.__a3dWantsKey(e))return; }catch(err3){}
      e.stopImmediatePropagation();return;
    }
  },true);"""
assert txt.count(OLD_GATE) == 1, 'gate anchor count %d' % txt.count(OLD_GATE)
txt = txt.replace(OLD_GATE, NEW_GATE, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
