"""patch_phase84.py -- __acad3dV84: views become the navigation.

WHAT THE USER REPORTED
    "drafting and annotation is basically 2d view which is not true. it should be a view, like
     layout view."

WHAT WAS MEASURED (probe84.py, against f8b607a9...)
    start       view=Plan            flat=True   label='Drafting & Annotation'
    3D view     view=Isometric       flat=False  label='Drafting & Annotation'   <- label lies
    Front elev  view=Front Elevation yaw=0.000 pitch=0.020
    Floor plan  view=Front Elevation yaw=0.000 pitch=0.020                       <- INERT
    Right elev  view=Right Elevation yaw=1.571 pitch=0.020
    Floor plan  view=Right Elevation yaw=1.571 pitch=0.020                       <- INERT again

    Sheets, contrary to an earlier reading, DO open: sheetOpen=True, display flex. That row is
    left alone except for being routed through the one activation path with the rest.

THE TWO FAULTS
  1. The floor-plan row read "if(!A3D.flat)toggleFlat()". An elevation is ALSO flat, so from any
     elevation the row changed the active level and left the camera looking sideways at the plan
     it had just opened. This is precisely the flat-is-not-plan confusion that V18 fixed for the
     drafting tools -- and it was never fixed here.
  2. The workspace label is a MODE name. It read "Drafting & Annotation" over an isometric 3D
     view, because it reported which tool set the user last picked from a menu rather than where
     they actually are. That is the user's complaint verbatim.

WHAT SHIPS
  A single entry point, bimActivateView(kind,id), for plan / 3d / elevation / saved / sheet.
  It restores the camera, closes whatever the previous view had open, names the active view,
  and lets the RIBBON FOLLOW THE VIEW instead of the other way round. The label then reports
  the active view's name, so the app reads as Revit does: you are always in a view.
"""

import hashlib
import pathlib
import sys

WORK = pathlib.Path(__file__).resolve().parent
SRC = WORK / 'canvas_v10.html'
BASE = 'f8b607a92c4e11b2954bc9f523d650f55cc4c1c3efbe283745b74735d9f72959'

CARET = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
         '<path d="m6 9 6 6 6-6"/></svg>')


def fail(msg):
    print('ABORT: ' + msg)
    sys.exit(1)


src = SRC.read_bytes()
have = hashlib.sha256(src).hexdigest()
if have != BASE:
    fail('baseline mismatch\n  expected %s\n  found    %s' % (BASE, have))
print('baseline ok: %s (%d bytes)' % (have[:16], len(src)))

text = src.decode('utf-8')
edits = 0


def sub(old, new, label, count=1):
    """Replace `old` exactly `count` times, asserting the count first."""
    global text, edits
    n = text.count(old)
    if n != count:
        fail('%s: expected %d occurrence(s) of the anchor, found %d' % (label, count, n))
    text = text.replace(old, new, count)
    edits += 1
    print('  edit %d ok: %s' % (edits, label))


# ---------------------------------------------------------------- 1. the V84 engine block
ANCHOR_1 = "  function bimDeleteView(id){"

V84 = r'''  /* ================= __acad3dV84: a view is where you are, not a mode you picked ============

     Before this, "Drafting & Annotation" and "3D" were MODES chosen from a menu, and the label
     at the top of the ribbon reported the mode. It therefore read "Drafting & Annotation" while
     the camera sat in an isometric 3D view, which is what the user reported. Revit has no such
     concept: the Project Browser lists views, you open one, and the ribbon follows.

     Everything that opens a view now goes through bimActivateView. That matters beyond tidiness:
     the floor-plan row in the browser used to read "if(!A3D.flat)toggleFlat()", and an elevation
     is ALSO flat, so opening a floor plan from any elevation changed the level and left the
     camera looking sideways at it -- measured, twice, before this patch. One activation path is
     what stops a per-row fix from leaving the next row broken. */
  var A3D_VIEW={kind:'plan',id:null,name:'Floor Plan'};

  /* The name shown in the ribbon label and used to mark the active row in the Project Browser.
     `sv` is the saved-view record, passed in rather than looked up again so a view deleted
     mid-activation cannot produce a blank label. */
  function bimViewLabelFor(kind,id,sv){
    var i;
    if(kind==='plan'){
      for(i=0;i<A3D.levels.length;i++)
        if(A3D.levels[i].id===id)return A3D.levels[i].name+' - Floor Plan';
      return 'Floor Plan';
    }
    if(kind==='elev')return (VIEWS[id]&&VIEWS[id].label)||'Elevation';
    if(kind==='sheet'){
      var sh=bimSheetById(id);
      return sh?(sh.number+' - '+sh.name):'Sheet';
    }
    if(kind==='saved')return (sv&&sv.name)||'View';
    return '3D View';
  }

  /* Returns true when it actually wrote the label, false when the element is not in the DOM --
     acadApplyWorkspace uses that answer to fall back to the old workspace name rather than
     leaving the user with no label at all. */
  function bimSyncViewLabel(){
    var lab=document.querySelector('#acad-shell .acad-ws');
    if(!lab)return false;
    lab.innerHTML=bimEsc(A3D_VIEW.name)+' '+
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'+
      '<path d="m6 9 6 6 6-6"/></svg>';
    lab.setAttribute('title','Active view: '+A3D_VIEW.name+' -- click to switch view');
    return true;
  }

  /* kind: 'plan' | '3d' | 'elev' | 'saved' | 'sheet'
     id:   level id / (none) / VIEWS preset key / saved view id / sheet id

     Returns true only when the view is actually open. Every failure path warns on the console
     AND toasts, and leaves the previous view exactly as it was -- a view switch that half
     happens is worse than one that declines. */
  function bimActivateView(kind,id,opts){
    opts=opts||{};
    var anim=(opts.anim!==false),sv=null,q;
    try{
      /* Leaving a sheet is not optional: the paper canvas covers the model canvas, so any view
         that is not a sheet must close it first or the user opens a view they cannot see. */
      if(kind!=='sheet')bimCloseSheetView();
      if(kind==='plan'){
        if(A3D.section)bimExitSection();
        if(id)setActiveLevel(id);
        id=A3D.activeLevel;
        setView('top',anim);
        /* setView would name this 'Top (Plan)'. The HUD and the status bar have said 'Plan'
           since V18 and other code reads that string, so keep it. */
        A3D.view='Plan';
        A3D.activeViewId=null;
      }else if(kind==='3d'){
        if(A3D.section)bimExitSection();
        setView('iso',anim);
        A3D.activeViewId=null;
      }else if(kind==='elev'){
        if(!VIEWS[id]||!VIEWS[id].ortho){
          console.warn('[BIM] Unknown elevation preset: '+id);
          a3dToast('That elevation view is not defined');
          return false;
        }
        if(A3D.section)bimExitSection();
        setView(id,anim);
        A3D.activeViewId=null;
      }else if(kind==='saved'){
        if(!bimApplyView(id))return false;
        for(q=0;q<A3D.views.length;q++)if(A3D.views[q].id===id){sv=A3D.views[q];break;}
        if(!sv){
          console.warn('[BIM] Saved view vanished during activation: '+id);
          return false;
        }
      }else if(kind==='sheet'){
        if(!bimSheetById(id)){
          console.warn('[BIM] Unknown sheet: '+id);
          a3dToast('Sheet not found');
          return false;
        }
        bimOpenSheetView(id);
      }else{
        console.warn('[BIM] Unknown view kind: '+kind);
        a3dToast('Unknown view type');
        return false;
      }
    }catch(eV){
      console.warn('[BIM] Could not activate the view; the previous view is unchanged.',eV);
      a3dToast('Could not open that view');
      return false;
    }
    A3D_VIEW={kind:kind,id:id||null,name:bimViewLabelFor(kind,id,sv)};
    /* The ribbon FOLLOWS the view. keepActive:true so a tab present in both tool sets stays
       put: the ribbon changes only when the new view makes the current tab unavailable, which
       is far less jarring than resetting to the first tab on every view change. */
    var ws=(kind==='3d'||(kind==='saved'&&sv&&!sv.flat))?'3d':'da';
    window.ACAD_WS_CUR=ws;
    try{if(window.__acadApplyWorkspace)window.__acadApplyWorkspace(ws,{keepActive:true});}
    catch(eW){console.warn('[BIM] The ribbon could not follow the view change.',eW);}
    bimSyncViewLabel();
    refreshHud();refreshBrowser();paint();saveSoon();
    return true;
  }
'''

sub(ANCHOR_1, V84 + ANCHOR_1, 'insert the V84 view-activation engine')

# ---------------------------------------------------------------- 2. the ribbon label
OLD_LAB = """    var lab=document.querySelector('.acad-ws');
    if(lab)lab.innerHTML=ACAD_WS_LABEL[ws]+' <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>';
    return ws;"""

NEW_LAB = """    /* __acad3dV84: the label reports the ACTIVE VIEW, not the workspace. Reporting the
       workspace is what made it read "Drafting & Annotation" over an isometric 3D view. The
       old workspace name is kept as the fallback for the window between first paint and the
       BIM engine publishing its hook, and for any build where that engine failed to load --
       a wrong label is bad, no label at all is worse. */
    var lab=document.querySelector('.acad-ws');
    if(lab){
      var named=false;
      try{if(window.__a3dSyncViewLabel)named=!!window.__a3dSyncViewLabel();}
      catch(eL){console.warn('[BIM] View label sync failed; showing the workspace name.',eL);}
      if(!named)lab.innerHTML=ACAD_WS_LABEL[ws]+' <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>';
    }
    return ws;"""

sub(OLD_LAB, NEW_LAB, 'ribbon label reports the active view')

# ---------------------------------------------------------------- 3. the workspace menu is a view menu
OLD_ROWS = """    m.innerHTML=row('da','Drafting &amp; Annotation','Plan')+row('3d','3D','Model');"""
NEW_ROWS = """    /* __acad3dV84: these are VIEWS now, named as views. The keys stay 'da' and '3d' because
       they still select the ribbon tool set; what changed is that picking one opens the
       matching view rather than putting the app into a mode. */
    m.innerHTML=row('da','Floor Plan','Drafting &amp; Annotation tools')+
                row('3d','3D View','Modelling tools');"""
sub(OLD_ROWS, NEW_ROWS, 'workspace menu rows are named as views')

# ---------------------------------------------------------------- 4. the Project Browser delegate
OLD_DELEG = """      if((b=cl('[data-a3dbplan]'))){setActiveLevel(b.getAttribute('data-a3dbplan'));if(!A3D.flat)toggleFlat();refreshBrowser();return;}
      if((b=cl('[data-a3dbview3d]'))){setView('iso');refreshBrowser();return;}
      if((b=cl('[data-a3dbviewpreset]'))){setView(b.getAttribute('data-a3dbviewpreset'));refreshBrowser();return;}
      if((b=cl('[data-a3dbviewgo]'))){bimApplyView(b.getAttribute('data-a3dbviewgo'));return;}
      if((b=cl('[data-a3dbsheetgo]'))){bimOpenSheetView(b.getAttribute('data-a3dbsheetgo'));return;}"""

NEW_DELEG = """      /* __acad3dV84: every one of these rows opens a VIEW, so every one goes through the
         single activation path. The floor-plan row used to read "if(!A3D.flat)toggleFlat()",
         which is inert whenever the CURRENT view is also flat -- from any elevation it changed
         the level and left the camera looking sideways at the plan it had just opened. */
      if((b=cl('[data-a3dbplan]'))){bimActivateView('plan',b.getAttribute('data-a3dbplan'));return;}
      if((b=cl('[data-a3dbview3d]'))){bimActivateView('3d');return;}
      if((b=cl('[data-a3dbviewpreset]'))){bimActivateView('elev',b.getAttribute('data-a3dbviewpreset'));return;}
      if((b=cl('[data-a3dbviewgo]'))){bimActivateView('saved',b.getAttribute('data-a3dbviewgo'));return;}
      if((b=cl('[data-a3dbsheetgo]'))){bimActivateView('sheet',b.getAttribute('data-a3dbsheetgo'));return;}"""

sub(OLD_DELEG, NEW_DELEG, 'Project Browser rows route through bimActivateView')

# ---------------------------------------------------------------- 5. active-row highlighting
OLD_PLAN_SEL = """          h+=bimBrowserLeaf(lv.name,{data:'data-a3dbplan="'+lv.id+'"',sel:(A3D.activeLevel===lv.id&&A3D.flat),
            ico:'\\u25a6',title:'Plan view at elevation '+lv.elev},2);"""
NEW_PLAN_SEL = """          /* __acad3dV84: the old test was "&&A3D.flat", and an elevation is flat too, so the
             floor plan row sat highlighted while the user was looking at an elevation. The
             active VIEW is what decides which row is the active row. */
          h+=bimBrowserLeaf(lv.name,{data:'data-a3dbplan="'+lv.id+'"',
            sel:(A3D_VIEW.kind==='plan'&&A3D.activeLevel===lv.id),
            ico:'\\u25a6',title:'Plan view at elevation '+lv.elev},2);"""
sub(OLD_PLAN_SEL, NEW_PLAN_SEL, 'floor plan row highlights only in a plan view')

OLD_3D_SEL = """        h+=bimBrowserLeaf('{3D}',{data:'data-a3dbview3d="iso"',ico:'\\u25c8',title:'Default isometric view'},2);"""
NEW_3D_SEL = """        h+=bimBrowserLeaf('{3D}',{data:'data-a3dbview3d="iso"',sel:(A3D_VIEW.kind==='3d'),
          ico:'\\u25c8',title:'Default isometric view'},2);"""
sub(OLD_3D_SEL, NEW_3D_SEL, 'the {3D} row highlights in the 3D view')

OLD_EL_SEL = """          h+=bimBrowserLeaf(VIEWS[k].label,{data:'data-a3dbviewpreset="'+k+'"',ico:'\\u25b1'},2);"""
NEW_EL_SEL = """          h+=bimBrowserLeaf(VIEWS[k].label,{data:'data-a3dbviewpreset="'+k+'"',
            sel:(A3D_VIEW.kind==='elev'&&A3D_VIEW.id===k),ico:'\\u25b1'},2);"""
sub(OLD_EL_SEL, NEW_EL_SEL, 'the active elevation row highlights')

# ---------------------------------------------------------------- 6. plan / 3D hooks go through the path
OLD_HOOKS = """  window.__a3dSetPlanView=function(){
    try{
      if(A3D.section)bimExitSection();
      if(!A3D.flat)toggleFlat();
      setView('top',false);
      A3D.flat=true;A3D.view='Plan';
      if(el.root)el.root.classList.add('flat');
      refreshHud();paint();
    }catch(e){console.warn('[BIM] plan view switch failed',e);}
  };
  window.__a3dSet3DView=function(){
    try{
      if(A3D.flat)toggleFlat();
      setView('iso',false);
      refreshHud();paint();
    }catch(e){console.warn('[BIM] 3D view switch failed',e);}
  };"""

NEW_HOOKS = """  /* __acad3dV84: both of these open a view, so both go through the one activation path
     rather than keeping a second, slightly different copy of the camera logic. They are used
     by startup and by the view menu, where an animated camera would be wrong, so neither
     animates. */
  window.__a3dSetPlanView=function(){
    if(!bimActivateView('plan',A3D.activeLevel,{anim:false}))
      console.warn('[BIM] plan view switch failed');
  };
  window.__a3dSet3DView=function(){
    if(!bimActivateView('3d',null,{anim:false}))
      console.warn('[BIM] 3D view switch failed');
  };
  window.__a3dActiveView=function(){
    return {kind:A3D_VIEW.kind,id:A3D_VIEW.id,name:A3D_VIEW.name};
  };
  window.__a3dOpenView=function(kind,id,opts){return bimActivateView(kind,id,opts);};
  window.__a3dSyncViewLabel=bimSyncViewLabel;
  window.__acad3dV84='viewactivation,planisnotflat,viewfollowsribbon,viewlabel,browserviewrows';"""

sub(OLD_HOOKS, NEW_HOOKS, 'plan/3D hooks delegate to the activation path, plus V84 hooks')

# ---------------------------------------------------------------- 7. state exposes the level and the view
OLD_STATE = ("sk:A3D.sk?{tool:A3D.sk.tool,y:A3D.sk.y,on:A3D.sk.on,pts:A3D.sk.pts.length}:null,"
             "sheets:A3D.sheets}));")
NEW_STATE = ("sk:A3D.sk?{tool:A3D.sk.tool,y:A3D.sk.y,on:A3D.sk.on,pts:A3D.sk.pts.length}:null,"
             "sheets:A3D.sheets,activeLevel:A3D.activeLevel,activeViewId:A3D.activeViewId,"
             "viewKind:A3D_VIEW.kind,viewName:A3D_VIEW.name}));")
sub(OLD_STATE, NEW_STATE, 'state exposes activeLevel and the active view')

out = text.encode('utf-8')
SRC.write_bytes(out)
new = hashlib.sha256(out).hexdigest()
print('\n%d edits applied' % edits)
print('bytes : %d -> %d (%+d)' % (len(src), len(out), len(out) - len(src)))
print('sha256: %s' % new)
