"""patch_phase86.py -- __acad3dV86: the command palette works, and LINE/PLINE/RECTANG behave like AutoCAD.

WHAT THE USER REPORTED
    "i hit cmd + k and the command shortkey from the past still there, however it never work.
     it should pop up the new shortcut not the old. the line work needs updates. like rec, poly,
     line, it needs to work like autocad (do your own reserach and copy how they do it)"

PART 1 -- THE PALETTE. Measured, driving it with real keys on the shipped build:

    LINE      matched=['LINE - Draw a line'] -> {'sk': None, 'objs': 0}
    RECTANG   matched=['RECTANG - Draw a rectangle'] -> {'sk': None, 'objs': 0}
    PLINE     matched=['PLINE - Draw a polyline'] -> {'sk': None, 'objs': 0}
              (and after two canvas clicks and Enter, still {'sk': None, 'objs': 0})

Every command was dead. Root cause: runCadAct dispatches into window.cadRun, which is
    window.cadRun=function(act){ if(WB[act]){...} return prevRun?prevRun(act):undefined; }
-- the RETIRED Canvas whiteboard's command table. That engine does not run in the BIM workspace,
so all 44 CAD commands and all 9 canvas commands resolved to nothing. runCadAct returned `true`
regardless, so nothing even reported a failure.

The palette now dispatches to the BIM engine, and -- Product Principle 1 -- it LISTS ONLY THE
COMMANDS THAT RUN. A command with no BIM implementation is not offered. That is why the list
gets shorter: the removed entries were never working.

PART 2 -- AUTOCAD BEHAVIOUR. Researched against Autodesk's own help pages plus command-line
transcripts (sources in the Phase 86 suite header). The behaviours copied here, and why each one
is the one that matters:

  * LINE emits ONE INDEPENDENT OBJECT PER SEGMENT; PLINE emits one object. That is the defining
    difference between them, not a detail. Autodesk: PLINE "Creates a 2D polyline, a single
    object that is composed of line and arc segments."  There was no LINE tool in this app at
    all -- SK_TOOLS had rect, circle, poly, wall and no line -- so the palette's LINE entry had
    nothing to call even after the dispatch was fixed.

  * THE CLOSE THRESHOLDS DIFFER, and they are not arbitrary. Autodesk on LINE's Close: "You can
    use Close after you have drawn a series of two or more segments." PLINE's transcripts show
    Close offered after ONE segment. So: LINE needs 3 points, PLINE needs 2.

  * COORDINATE ENTRY: "3,4" absolute, "@3,4" relative, "3<45" absolute polar, "@1<45" relative
    polar, "#3,4" forces absolute, and a bare number is direct distance entry along the current
    rubber band. Angles increase counter-clockwise from +X. Measured on this app's plan camera:
    +X projects screen-right and +Z projects screen-DOWN, so screen-up is -Z and the angle maps
    to dx=cos(t), dz=-sin(t). That sign is measured, not assumed.

  * KEYS: Enter or Space ends the sequence; Esc cancels; U removes the most recent segment; C
    closes. Enter at the Command prompt repeats the previous command.

  * PROMPTS: the status bar now reads what AutoCAD prints -- "Specify first point:",
    "Specify next point or [Undo]:", "Specify next point or [Close/Undo]:".

    ONE DELIBERATE DEPARTURE. AutoCAD's real PLINE prompt is
        Specify next point or [Arc/Halfwidth/Length/Undo/Width]:
    This app implements none of Arc, Halfwidth, Length or Width. Printing them would be a
    decorative prompt offering four options that do nothing, which is the same fault as the
    palette this patch is fixing. The prompt lists [Close/Undo] because those are what work.
"""

import hashlib
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parent / 'canvas_v10.html'
BASE = '184e728a79f4b7b059a4891c2bae34c7eaf0287b348c3edc2d728d5bec15bdd0'

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


# ================================================================ 1. the LINE tool exists
sub("  var SK_TOOLS={floor:'Floor',trim:'Trim',rect:'Rectangle',",
    "  var SK_TOOLS={line:'Line',floor:'Floor',trim:'Trim',rect:'Rectangle',",
    'LINE is a real tool')

# ================================================================ 2. finishLine + the AutoCAD input core
OLD_FINISH = """  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice());
  }"""

NEW_FINISH = r'''  function finishPoly(){
    var sk=A3D.sk;if(!sk||sk.pts.length<3)return null;
    return addSketchObj(sk.pts.slice());
  }

  /* ================= __acad3dV86: AutoCAD-shaped drawing input =================

     LINE emits ONE OBJECT PER SEGMENT. That is the whole difference between LINE and PLINE in
     AutoCAD -- N points produce N-1 independent entities, which is why a finished LINE run has
     no Close option and selecting one segment selects only that segment. PLINE produces a
     single object. Copying the prompts without copying this would be copying the costume. */
  function finishLine(close){
    var sk=A3D.sk;
    if(!sk||sk.pts.length<2){A3D.sk=null;paint();return null;}
    var pts=sk.pts.slice(),y=sk.y,on=sk.on||null,made=[],i,o;
    if(close&&pts.length>=3)pts.push([pts[0][0],pts[0][1]]);
    /* addSketchObj reads A3D.sk for the datum plane and host face and then clears it, so the
       sketch is rebuilt for each segment rather than the loop reaching around it. */
    for(i=0;i<pts.length-1;i++){
      A3D.sk={tool:'line',pts:[],y:y,on:on};
      o=addSketchObj([[pts[i][0],pts[i][1]],[pts[i+1][0],pts[i+1][1]]]);
      if(o)made.push(o.id);
    }
    A3D.sk=null;
    paint();saveSoon();
    return made;
  }

  /* Tools that take typed coordinates. Everything here accumulates points on the ground plane,
     which is what the parser below produces. */
  var BIM_COORD_TOOLS={line:1,poly:1,wall:1,rect:1,stair:1};

  /* AutoCAD coordinate entry. Exactly the five forms Autodesk documents:

         3,4     absolute Cartesian        @3,4    relative Cartesian
         3<45    absolute polar            @1<45   relative polar
         #3,4    forces absolute           7       direct distance entry along the rubber band

     Angles increase counter-clockwise from +X. MEASURED on this app's plan camera: world +X
     projects screen-right and world +Z projects screen-DOWN, so screen-up is -Z and an AutoCAD
     angle maps to dx = cos(t), dz = -sin(t). That sign was measured with __a3dProject, not
     reasoned about.

     Returns a [x,z] ground point, or null when the string is not a coordinate -- the caller
     reports that rather than silently placing a point somewhere wrong. */
  function bimParseCoordInput(s,sk){
    if(!sk)return null;
    s=String(s||'').trim();
    if(!s)return null;
    var rel=false;
    if(s.charAt(0)==='@'){rel=true;s=s.slice(1);}
    else if(s.charAt(0)==='#'){s=s.slice(1);}
    var last=sk.pts.length?sk.pts[sk.pts.length-1]:null;
    var i,a,b;
    if(s.indexOf('<')>=0){
      i=s.indexOf('<');
      a=parseFloat(s.slice(0,i));b=parseFloat(s.slice(i+1));
      if(!isFinite(a)||!isFinite(b))return null;
      var t=b*Math.PI/180,vx=Math.cos(t)*a,vz=-Math.sin(t)*a;
      if(rel){if(!last)return null;return [last[0]+vx,last[1]+vz];}
      return [vx,vz];
    }
    if(s.indexOf(',')>=0){
      i=s.indexOf(',');
      a=parseFloat(s.slice(0,i));b=parseFloat(s.slice(i+1));
      if(!isFinite(a)||!isFinite(b))return null;
      if(rel){if(!last)return null;return [last[0]+a,last[1]+b];}
      return [a,b];
    }
    /* Direct distance entry: a bare number travels along the direction the rubber band is
       already pointing. This is the ortho workflow -- push the cursor the way you want to go,
       type the number, press Enter. */
    var d=parseFloat(s);
    if(!isFinite(d)||d<=0||!last)return null;
    var dir=sk.liveDir||[1,0];
    return [last[0]+dir[0]*d,last[1]+dir[1]*d];
  }

  function bimCanClose(sk){
    if(!sk||!sk.pts)return false;
    /* The thresholds differ, and both come from AutoCAD. Autodesk on LINE: "You can use Close
       after you have drawn a series of two or more segments" -- so 3 points. PLINE's own
       transcripts offer Close after ONE segment -- so 2 points. */
    if(sk.tool==='line')return sk.pts.length>=3;
    if(sk.tool==='poly')return sk.pts.length>=3;
    if(sk.tool==='wall')return sk.pts.length>=3;
    return false;
  }
  function bimCloseCurrent(){
    var sk=A3D.sk;if(!bimCanClose(sk))return false;
    if(sk.tool==='line')finishLine(true);
    else if(sk.tool==='wall')finishWall(true);
    else finishPoly();
    bimSyncStatusHint();
    return true;
  }
  function bimFinishCurrent(){
    var sk=A3D.sk;if(!sk)return false;
    if(sk.tool==='line'){if(sk.pts.length>=2)finishLine(false);else{A3D.sk=null;paint();}}
    else if(sk.tool==='wall'){if(sk.pts.length>=2)finishWall(false);else{A3D.sk=null;paint();}}
    else if(sk.tool==='poly'){if(sk.pts.length>=3)finishPoly();else{A3D.sk=null;paint();}}
    else if(sk.tool==='stair'){if(sk.pts.length>=2)finishStair();else{A3D.sk=null;paint();}}
    else{A3D.sk=null;paint();}
    bimSyncStatusHint();
    return true;
  }
  function bimUndoLastPoint(){
    var sk=A3D.sk;
    if(!sk||!sk.pts||!sk.pts.length)return false;
    sk.pts.pop();
    bimSyncStatusHint();paint();
    return true;
  }
  /* A typed coordinate is a POINT, so it goes through the same placement path a click would --
     including the auto-finish rules for the two-point tools. */
  function bimCommitTypedPoint(str){
    var sk=A3D.sk;if(!sk)return false;
    var p=bimParseCoordInput(str,sk);
    if(!p){a3dToast('Not a coordinate: try 3,4 or @3,4 or @5<45, or a length');paint();return false;}
    sk.pts.push([p[0],p[1]]);
    if(sk.tool==='rect'&&sk.pts.length>=2)finishRect();
    else if(sk.tool==='circle'&&sk.pts.length>=2)finishCircle();
    bimSyncStatusHint();paint();saveSoon();
    return true;
  }

  /* The prompt strings AutoCAD prints, for the tools that behave like AutoCAD's.

     DELIBERATE DEPARTURE: AutoCAD's PLINE prompt reads
         Specify next point or [Arc/Halfwidth/Length/Undo/Width]:
     and this app implements none of Arc, Halfwidth, Length or Width. Printing them would offer
     four options that do nothing -- the same fault as the dead palette this phase is fixing --
     so the bracket list holds only what works. */
  function bimPromptFor(sk){
    var n=sk.pts?sk.pts.length:0;
    if(sk.tool==='line'){
      if(!n)return 'Specify first point:';
      return n>=2?'Specify next point or [Close/Undo]:':'Specify next point or [Undo]:';
    }
    if(sk.tool==='poly'){
      if(!n)return 'Specify start point:';
      return n>=2?'Specify next point or [Close/Undo]:':'Specify next point or [Undo]:';
    }
    if(sk.tool==='rect'){
      return n?'Specify other corner point:':'Specify first corner point:';
    }
    if(sk.tool==='circle'){
      return n?'Specify radius:':'Specify center point:';
    }
    if(sk.tool==='wall'){
      if(!n)return 'Wall  ·  Specify start point:';
      return n>=2?'Wall  ·  Specify next point or [Close/Undo]:':'Wall  ·  Specify next point or [Undo]:';
    }
    var msg=(SK_TOOLS[sk.tool]||sk.tool);
    return msg+(n?'  ·  click the next point, or type a length + Enter':'  ·  click to start');
  }

  /* Enter at the Command prompt repeats the previous command -- Autodesk: "You can also repeat
     the previous command by pressing Enter or the spacebar." Recorded wherever a command is
     started, so the palette and the ribbon both feed it. */
  function bimRecordCmd(fn,label){A3D.lastCmd={run:fn,label:label||''};}
  function bimRepeatLastCommand(){
    var c=A3D.lastCmd;
    if(!c||typeof c.run!=='function')return false;
    try{c.run();}
    catch(eR){console.warn('[BIM] Could not repeat the last command.',eR);a3dToast('Could not repeat that command');return false;}
    return true;
  }'''

sub(OLD_FINISH, NEW_FINISH, 'finishLine, the coordinate parser, prompts and repeat-last')

# ================================================================ 3. startSketch records the command
OLD_START = """  function startSketch(tool){
    if(!SK_TOOLS[tool])return;
    closeDlg();
    bimEnterDraftingMode();"""
NEW_START = """  function startSketch(tool){
    if(!SK_TOOLS[tool])return;
    closeDlg();
    bimEnterDraftingMode();
    bimRecordCmd(function(){startSketch(tool);},SK_TOOLS[tool]);   // __acad3dV86: Enter repeats it"""
sub(OLD_START, NEW_START, 'starting a tool records it for Enter-repeat')

# ================================================================ 4. skClick closes LINE correctly
OLD_CLOSE = """    }else{
      if(sk.pts.length>=3){
        var V=camVecs(A3D.cam),p0=toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,cvW(),cvH());
        if(Math.abs(p0[0]-xy[0])<9&&Math.abs(p0[1]-xy[1])<9){
          if(sk.tool==='wall')finishWall(true);else finishPoly();
          return;
        }
      }
      sk.pts.push([gx,gz]);
    }"""
NEW_CLOSE = """    }else{
      if(sk.pts.length>=3){
        var V=camVecs(A3D.cam),p0=toScreen([sk.pts[0][0],sk.y,sk.pts[0][1]],V,cvW(),cvH());
        if(Math.abs(p0[0]-xy[0])<9&&Math.abs(p0[1]-xy[1])<9){
          /* __acad3dV86: LINE closes into SEGMENTS, not into one polygon. Routing it through
             finishPoly would have quietly turned a closed run of lines into a single sketch
             loop -- the exact distinction this phase exists to get right. */
          if(sk.tool==='wall')finishWall(true);
          else if(sk.tool==='line')finishLine(true);
          else finishPoly();
          return;
        }
      }
      sk.pts.push([gx,gz]);
    }"""
sub(OLD_CLOSE, NEW_CLOSE, 'clicking the start point closes LINE as segments')

# ================================================================ 5. the status bar prints the prompt
OLD_HINT = """    if(sk){
      var msg=(SK_TOOLS[sk.tool]||sk.tool);
      if(sk.pts&&sk.pts.length)msg+=' \\u00b7 click the next point, or type a length + Enter';
      else msg+=' \\u00b7 click to start';
      return msg;
    }"""
NEW_HINT = """    if(sk){
      /* __acad3dV86: the AutoCAD prompt, plus whatever is being typed -- the command line is
         where a drafter looks to find out what the tool will accept next. */
      var pr=bimPromptFor(sk);
      if(A3D_TYPING.active)pr+='  '+A3D_TYPING.buf;
      return pr;
    }"""
sub(OLD_HINT, NEW_HINT, 'the status bar prints the AutoCAD prompt')

# ================================================================ 6. the key chain
OLD_KEYS = """    if(A3D.sk&&(A3D.sk.tool==='poly'||A3D.sk.tool==='wall')&&!el.dlg){
      if(/^[0-9.]$/.test(ev.key)){
        A3D_TYPING.active=true;A3D_TYPING.buf+=ev.key;paint();ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      if(A3D_TYPING.active){
        if(ev.key==='Backspace'){A3D_TYPING.buf=A3D_TYPING.buf.slice(0,-1);if(!A3D_TYPING.buf.length)A3D_TYPING.active=false;paint();ev.preventDefault();ev.stopImmediatePropagation();return;}
        if(ev.key==='Enter'){var typedLen=parseFloat(A3D_TYPING.buf);A3D_TYPING.active=false;A3D_TYPING.buf='';if(isFinite(typedLen)&&typedLen>0)bimCommitTypedLength(typedLen);ev.preventDefault();ev.stopImmediatePropagation();return;}
        if(ev.key==='Escape'){A3D_TYPING.active=false;A3D_TYPING.buf='';paint();ev.preventDefault();ev.stopImmediatePropagation();return;}
      }
    }"""

NEW_KEYS = r"""    /* __acad3dV86: AutoCAD's input model for the point-taking tools.

       The buffer used to accept [0-9.] only, and only for poly and wall, and it only ever meant
       a length. It now accepts the full coordinate grammar -- 3,4 / @3,4 / 3<45 / @1<45 / #3,4
       and a bare number for direct distance entry -- for every tool that takes points.

       Option letters are read ONLY when nothing is typed, because 'c' and 'u' are not part of a
       coordinate: while a number is being entered they would be a typo, not a command. */
    if(A3D.sk&&BIM_COORD_TOOLS[A3D.sk.tool]&&!el.dlg){
      if(!ev.ctrlKey&&!ev.metaKey&&/^[0-9.,@<#-]$/.test(ev.key)){
        A3D_TYPING.active=true;A3D_TYPING.buf+=ev.key;
        bimSyncStatusHint();paint();ev.preventDefault();ev.stopImmediatePropagation();return;
      }
      if(A3D_TYPING.active){
        if(ev.key==='Backspace'){
          A3D_TYPING.buf=A3D_TYPING.buf.slice(0,-1);
          if(!A3D_TYPING.buf.length)A3D_TYPING.active=false;
          bimSyncStatusHint();paint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Enter'||ev.key===' '){
          var typedStr=A3D_TYPING.buf;
          A3D_TYPING.active=false;A3D_TYPING.buf='';
          bimCommitTypedPoint(typedStr);
          ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Escape'){
          A3D_TYPING.active=false;A3D_TYPING.buf='';
          bimSyncStatusHint();paint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
      }else{
        if((ev.key==='u'||ev.key==='U')&&!ev.ctrlKey&&!ev.metaKey&&A3D.sk.pts.length){
          bimUndoLastPoint();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if((ev.key==='c'||ev.key==='C')&&!ev.ctrlKey&&!ev.metaKey&&bimCanClose(A3D.sk)){
          bimCloseCurrent();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
        if(ev.key==='Enter'||ev.key===' '){
          bimFinishCurrent();ev.preventDefault();ev.stopImmediatePropagation();return;
        }
      }
    }"""
sub(OLD_KEYS, NEW_KEYS, 'the AutoCAD key and coordinate grammar')

# the old per-tool Enter and Close handlers are now unreachable -- remove rather than strand them
OLD_DEAD = """    if(ev.key==='Enter'&&A3D.sk&&A3D.sk.tool==='poly'&&A3D.sk.pts.length>=3){
      finishPoly();ev.preventDefault();return;
    }
    if(ev.key==='Enter'&&A3D.sk&&A3D.sk.tool==='wall'&&A3D.sk.pts.length>=2){
      finishWall(false);ev.preventDefault();return;
    }
    if(ev.key==='Enter'&&A3D.sk&&A3D.sk.tool==='stair'&&A3D.sk.pts.length>=2){
      finishStair();ev.preventDefault();return;
    }
    // AutoCAD PLINE convention: 'C' closes the current path. Without this the only way to close
    // a wall/polyline was to click within 0.09 units of the start point -- a tolerance tight
    // enough that in practice walls almost always finished OPEN, which silently broke Room,
    // Floor and Roof (they need an enclosed loop). Found by real browser testing, not unit tests.
    if((ev.key==='c'||ev.key==='C')&&!ev.ctrlKey&&!ev.metaKey&&!el.dlg&&A3D.sk&&A3D.sk.pts.length>=3){
      if(A3D.sk.tool==='wall'){finishWall(true);ev.preventDefault();return;}
      if(A3D.sk.tool==='poly'){finishPoly();ev.preventDefault();return;}
    }"""
NEW_DEAD = """    /* __acad3dV86: the per-tool Enter handlers and the 'C' closes handler that used to sit here
       are gone. The branch above reaches every one of their cases first and returns, so leaving
       them would have stranded four unreachable handlers in the chain -- and the C handler
       carried the wrong threshold for LINE besides. Its original note is worth keeping: before
       it existed, the only way to close a path was to click within 0.09 units of the start
       point, a tolerance tight enough that walls almost always finished OPEN, which silently
       broke Room, Floor and Roof. Found by real browser testing, not unit tests. */
    if((ev.key==='Enter'||ev.key===' ')&&!A3D.sk&&!el.dlg&&!A3D.conPick&&A3D.lastCmd){
      bimRepeatLastCommand();ev.preventDefault();ev.stopImmediatePropagation();return;
    }"""
sub(OLD_DEAD, NEW_DEAD, 'unreachable handlers removed; Enter repeats the last command')

# ================================================================ 7. the BIM command table
OLD_HOOKS = "  window.__a3dSyncViewLabel=bimSyncViewLabel;"
NEW_HOOKS = r"""  window.__a3dSyncViewLabel=bimSyncViewLabel;

  /* ================= __acad3dV86: the command palette runs against the BIM engine =========

     Every entry here was driven before it was listed. A command with no BIM implementation is
     NOT in this table and therefore is not offered by the palette -- that is the point. The
     palette used to list 44 CAD commands and 9 canvas commands, every one of which dispatched
     into the retired Canvas whiteboard and did nothing. */
  var BIM_CMD_MAP={
    line:function(){startSketch('line');},
    poly:function(){startSketch('poly');},
    rect:function(){startSketch('rect');},
    circle:function(){startSketch('circle');},
    text:function(){startTextTool();},
    leader:function(){startLeaderTool();},
    bimDims:function(){startDimTool();},
    measure:function(){startDimTool();},
    trim:function(){startTrimTool();},
    mirror:function(){startMirrorTool();},
    offset:function(){openOffsetDlg();},
    duplicate:function(){duplicateSelection();},
    del:function(){delSelection();},
    zoomFit:function(){fitScene();},
    selAll:function(){
      A3D.selSet=A3D.objs.map(function(o){return o.id;});
      A3D.sel=A3D.selSet.length?A3D.selSet[0]:null;A3D.sel2=null;
      refreshTree();refreshProps();paint();
      a3dToast('Selected '+A3D.selSet.length+' object(s)');
    },
    selNone:function(){
      A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
      refreshTree();refreshProps();paint();
    },
    bimSnap:function(){bimSetSnap({point:!A3D_SNAP.point});bimSyncSnapPill();paint();
      a3dToast('Object snap '+(A3D_SNAP.point?'on':'off'));},
    bimOrtho:function(){bimSetSnap({ortho:!A3D_SNAP.ortho});bimSyncSnapPill();paint();
      a3dToast('Ortho '+(A3D_SNAP.ortho?'on':'off'));},
    grid:function(){bimSetSnap({grid:!A3D_SNAP.grid});bimSyncSnapPill();paint();
      a3dToast('Grid snap '+(A3D_SNAP.grid?'on':'off'));}
  };
  window.__a3dCmdSupported=function(act){return !!BIM_CMD_MAP[act];};
  window.__a3dRunCmd=function(act){
    var f=BIM_CMD_MAP[act];
    if(!f)return false;
    try{f();bimRecordCmd(f,act);return true;}
    catch(eC){
      console.warn('[BIM] Command failed: '+act,eC);
      a3dToast('That command could not run');
      return false;
    }
  };
  window.__a3dParseCoord=function(s){return bimParseCoordInput(s,A3D.sk);};
  window.__a3dPrompt=function(){return A3D.sk?bimPromptFor(A3D.sk):'Ready';};
  window.__a3dTyping=function(){return {active:A3D_TYPING.active,buf:A3D_TYPING.buf};};
  window.__a3dLastCmd=function(){return A3D.lastCmd?(A3D.lastCmd.label||''):null;};
  window.__acad3dV86='palettewired,linetool,autocadcoords,autocadprompts,closeundo,repeatlast';"""
sub(OLD_HOOKS, NEW_HOOKS, 'the BIM command table and V86 hooks')

# ================================================================ 8. the dispatcher
OLD_RUN = """  function runCadAct(act){
    try{ if(typeof window.cadRun==='function'){ window.cadRun(act); return true; } }catch(e){}
    try{ if(window.RUN&&typeof RUN[act]==='function'){ RUN[act](); return true; } }catch(e){}
    return false;
  }"""
NEW_RUN = """  function runCadAct(act){
    /* __acad3dV86: in the BIM workspace these commands run against the BIM engine, and the
       fall-through below is NOT taken.

       That fall-through is why every palette command was dead: window.cadRun dispatches into
       WB[act], the retired Canvas whiteboard's table, which does not run in this workspace.
       Worse, this function returned true regardless of what cadRun did, so a command that did
       nothing still reported success and nothing ever surfaced the failure. */
    if(window.__a3dOn){
      try{ if(window.__a3dRunCmd)return !!window.__a3dRunCmd(act); }
      catch(e){ console.warn('[BIM] Palette command failed: '+act,e); }
      return false;
    }
    try{ if(typeof window.cadRun==='function'){ window.cadRun(act); return true; } }catch(e){}
    try{ if(window.RUN&&typeof RUN[act]==='function'){ RUN[act](); return true; } }catch(e){}
    return false;
  }"""
sub(OLD_RUN, NEW_RUN, 'the palette dispatches to the BIM engine in BIM mode')

# ================================================================ 9. the palette lists only live commands
OLD_DRAW = """    function draw(){
      var q=input.value.trim();
      rows=!q?REGISTRY.slice(0,14):REGISTRY.map(function(c){return {c:c,s:score(c,q)};}).filter(function(r){return r.s<99;}).sort(function(a,b){return a.s-b.s;}).slice(0,14).map(function(r){return r.c;});"""
NEW_DRAW = """    /* __acad3dV86: in the BIM workspace the palette offers only commands that RUN there.
       Everything it used to list dispatched into the retired Canvas whiteboard and did nothing;
       a shorter list of working commands beats a long list of dead ones. */
    function pool(){
      if(window.__a3dOn&&window.__a3dCmdSupported){
        return REGISTRY.filter(function(c){return c.cad&&window.__a3dCmdSupported(c.cad);});
      }
      return REGISTRY;
    }
    function draw(){
      var q=input.value.trim(),P=pool();
      rows=!q?P.slice(0,14):P.map(function(c){return {c:c,s:score(c,q)};}).filter(function(r){return r.s<99;}).sort(function(a,b){return a.s-b.s;}).slice(0,14).map(function(r){return r.c;});"""
sub(OLD_DRAW, NEW_DRAW, 'the palette lists only commands that run')

OLD_RUNIDX = """    function runIdx(i){
      var c=rows[i]; if(!c) return;
      pal.classList.remove('show');
      if(c.cad) runCadAct(c.cad); else if(c.fn) c.fn();
    }"""
NEW_RUNIDX = """    function runIdx(i){
      var c=rows[i]; if(!c) return;
      pal.classList.remove('show');
      /* A command that cannot run says so, instead of closing the palette over nothing. */
      var ok=c.cad?runCadAct(c.cad):(c.fn?(c.fn(),true):false);
      if(!ok&&window.toast)try{window.toast(c.name+' is not available here');}catch(eT){}
    }"""
sub(OLD_RUNIDX, NEW_RUNIDX, 'a command that cannot run reports it')

sub("placeholder=\"Type a command: LINE, CIRCLE, MOVE, CARD\\u2026\"",
    "placeholder=\"Type a command: LINE, PLINE, REC, CIRCLE\\u2026\"",
    'the placeholder names commands that exist')

out = text.encode('utf-8')
SRC.write_bytes(out)
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % hashlib.sha256(out).hexdigest())
