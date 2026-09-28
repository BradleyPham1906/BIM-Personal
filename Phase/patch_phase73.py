"""
Phase 73 -- Canvas retired as a workspace, model properties in the inspector, bigger hit targets.

Anchored search-and-replace. Every anchor is asserted to match an EXACT expected count.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = '8c48c07bf371a1704e7f5fa0d43e1bda9f3180906c743077d77eb9ca3cfb538d'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new, count=1):
    patches.append((name, old, new, count))


# =============================================================== A. bigger hit targets
P('css.dockbtn',
  "    '.a3d-dbtn{width:30px;height:28px;display:flex;align-items:center;justify-content:center;",
  "    '.a3d-dbtn{width:34px;height:32px;display:flex;align-items:center;justify-content:center;")

P('css.dockicon',
  "    '.a3d-dbtn svg{width:16px;height:16px}'+",
  "    '.a3d-dbtn svg{width:18px;height:18px}'+")

P('css.dockcaret',
  "    '.a3d-dcar{width:13px;height:28px;background:transparent;border:0;color:#8d9196;font-size:8px;"
  "cursor:pointer;padding:0;line-height:1;font-family:inherit;flex:0 0 auto}'+\n"
  "    '.a3d-dcar:hover{color:#fff}'+",
  "    /* __acad3dV73: the caret was a 13x28 sliver -- a 13px-wide target is below every hit-size\n"
  "       guideline there is, and it is the control a user reaches for most, because it is the way\n"
  "       into the rest of a group's tools. Widened to 22px with a visible hover plate so it reads\n"
  "       as a button rather than as decoration on the one beside it. */\n"
  "    '.a3d-dcar{width:22px;height:32px;background:transparent;border:1px solid transparent;"
  "border-radius:5px;color:#9aa3ad;font-size:10px;"
  "cursor:pointer;padding:0;line-height:1;font-family:inherit;flex:0 0 auto}'+\n"
  "    '.a3d-dcar:hover{color:#fff;background:#2f353c}'+")

P('css.pgcar',
  "    '.a3d-pgcar{color:#7d8590;font-size:9px}'+",
  "    /* __acad3dV73: the property-group caret. 9px is unreadable and its parent header row was\n"
  "       the only hit target; the caret now has its own 22px box inside that row. */\n"
  "    '.a3d-pgcar{color:#9aa3ad;font-size:12px;width:22px;height:22px;display:inline-flex;"
  "align-items:center;justify-content:center;border-radius:4px;margin:-4px -4px -4px 0}'+\n"
  "    '.a3d-pgrp:hover .a3d-pgcar{color:#fff;background:#2f353c}'+")

P('css.palbtn',
  "    '.a3d-palbtn{background:#2f353c;border:1px solid #3a4048;color:#aeb6bf;border-radius:3px;"
  "font-size:9.5px;padding:2px 5px;cursor:pointer;font-family:inherit}'+",
  "    '.a3d-palbtn{background:#2f353c;border:1px solid #3a4048;color:#aeb6bf;border-radius:4px;"
  "font-size:11px;padding:4px 8px;cursor:pointer;font-family:inherit}'+\n"
  "    '.a3d-palbtn:hover{background:#3a4149;color:#fff}'+")

# =============================================================== B. Canvas retired
P('ws.tabs',
  "  var ACAD_WS_TABS={\n"
  "    canvas:['insert','cvarrange','view','output'],\n"
  "    da:",
  "  /* __acad3dV73: CANVAS IS RETIRED AS A WORKSPACE.\n"
  "\n"
  "     Drafting & Annotation and 3D have run the same BIM engine since the workspaces were split --\n"
  "     they differ only in camera mode. Canvas ran the whiteboard engine on its own data model\n"
  "     (state.nodes / state.wires) with its own panels, and after V64-V72 unified the shell around\n"
  "     the BIM engine it was the last surface that did not belong to the rest of the app. Worse,\n"
  "     the app BOOTED into it: the workspace label read \"Drafting & Annotation\" while the screen\n"
  "     showed the Canvas board, because the startup path applied the workspace's ribbon tabs\n"
  "     without ever entering the BIM shell.\n"
  "\n"
  "     What is removed is the WORKSPACE, not the code. The whiteboard module still supplies two\n"
  "     things the unified shell depends on: the file dock and rail that host the BIM navigator\n"
  "     since V65, and the shared material card library (window.__WB_MATERIAL_CARDS, V69). Ripping\n"
  "     the module out would take both with it; removing it from the workspace list is the change\n"
  "     that was actually asked for. */\n"
  "  var ACAD_WS_TABS={\n"
  "    da:")

P('ws.label',
  "  var ACAD_WS_LABEL={canvas:'Canvas',da:'Drafting &amp; Annotation','3d':'3D'};",
  "  var ACAD_WS_LABEL={da:'Drafting &amp; Annotation','3d':'3D'};\n"
  "  /* A session that last ran before this phase can have 'canvas' persisted as its workspace.\n"
  "     It is migrated rather than rejected, so an existing user lands in Drafting & Annotation\n"
  "     instead of a workspace that no longer exists. */\n"
  "  if(window.ACAD_WS_CUR==='canvas')window.ACAD_WS_CUR='da';")

P('ws.menu.row',
  "    m.innerHTML=row('canvas','Canvas','Board')+row('da','Drafting &amp; Annotation','')+row('3d','3D','Part');\n"
  "    m.querySelector('[data-wsm=\"canvas\"]').addEventListener('click',function(){\n"
  "      m.classList.remove('show');\n"
  "      window.ACAD_WS_CUR='canvas';\n"
  "      try{ if(window.__a3dOn&&window.__a3dExit) window.__a3dExit(); }catch(e){}\n"
  "      acadApplyWorkspace('canvas');\n"
  "      try{window.toast&&toast('Workspace: Canvas');}catch(e){}\n"
  "    });\n",
  "    m.innerHTML=row('da','Drafting &amp; Annotation','Plan')+row('3d','3D','Model');\n")

P('ws.boot',
  "  setTimeout(function(){try{acadApplyWorkspace(window.ACAD_WS_CUR||'da');}catch(eS){}},60);",
  "  /* __acad3dV73: boot INTO the drafting workspace, not just into its ribbon tabs. Before this,\n"
  "     startup applied the tab set for 'da' and stopped, so the first thing on screen was the\n"
  "     Canvas board under a label that said Drafting & Annotation. __a3dEnter may not be defined\n"
  "     at 60ms, so this retries briefly and gives up quietly rather than throwing on a slow load --\n"
  "     the workspace tabs are applied either way. */\n"
  "  function acadBootWorkspace(tries){\n"
  "    var ws=window.ACAD_WS_CUR||'da';\n"
  "    if(ws==='canvas')ws='da';\n"
  "    try{acadApplyWorkspace(ws);}catch(eS){}\n"
  "    if(typeof window.__a3dEnter!=='function'){\n"
  "      if(tries>0)setTimeout(function(){acadBootWorkspace(tries-1);},120);\n"
  "      else console.warn('[BIM] Could not enter the drafting workspace on startup; the shell is '+\n"
  "        'reachable from the workspace menu.');\n"
  "      return;\n"
  "    }\n"
  "    try{\n"
  "      window.__a3dEnter();\n"
  "      if(ws==='3d'){if(window.__a3dSet3DView)window.__a3dSet3DView();}\n"
  "      else if(window.__a3dSetPlanView)window.__a3dSetPlanView();\n"
  "      window.ACAD_WS_CUR=ws;\n"
  "    }catch(eB){console.warn('[BIM] Startup entry into the drafting workspace failed.',eB);}\n"
  "  }\n"
  "  setTimeout(function(){acadBootWorkspace(25);},60);")

# =============================================================== C. model properties
P('props.model',
  "    var o=objById(A3D.sel);\n"
  "    if(!o){\n"
  "      el.propsbody.innerHTML='<div class=\"a3d-propempty\">No object selected.<br>Click an object in the view, or pick one from the Project Browser.</div>';\n"
  "      return;\n"
  "    }",
  "    var o=objById(A3D.sel);\n"
  "    if(!o){\n"
  "      /* __acad3dV73: with nothing selected the inspector describes the MODEL, the way the\n"
  "         reference tool does. \"No object selected\" wastes the panel exactly when a user is\n"
  "         orienting themselves. Every field below is backed by state that already exists and is\n"
  "         already persisted -- no new settings were invented to fill the space. */\n"
  "      el.propsbody.innerHTML=bimModelPropsHtml();\n"
  "      return;\n"
  "    }")

P('code.modelprops',
  "  function refreshProps(){",
  "  /* __acad3dV73: the no-selection inspector. Project and Site are editable and write to the\n"
  "     title block and site record that the sheet title block already prints. Level, Layer and\n"
  "     Appearance are the three switches that change what the drawing shows, and each one already\n"
  "     had a control elsewhere -- gathering them here does not add state, it stops a user hunting\n"
  "     for them. Statistics are counted from the model, never stored. */\n"
  "  function bimModelPropsHtml(){\n"
  "    var h='',i,lv,ly;\n"
  "    bimEnsureBuildings();\n"
  "    var rows='';\n"
  "    rows+=bimPropRow('Project','<input type=\"text\" data-propmodel=\"project\" value=\"'+\n"
  "      bimEsc(A3D.titleBlock.project||'')+'\" placeholder=\"Untitled project\">');\n"
  "    rows+=bimPropRow('Client','<input type=\"text\" data-propmodel=\"client\" value=\"'+\n"
  "      bimEsc(A3D.titleBlock.client||'')+'\">');\n"
  "    rows+=bimPropRow('Site','<input type=\"text\" data-propmodel=\"site\" value=\"'+\n"
  "      bimEsc(A3D.site.name||'')+'\">');\n"
  "    h+=bimPropGroup('Identity Data',rows);\n"
  "\n"
  "    var vrows='',lvlOpts='';\n"
  "    for(i=0;i<A3D.levels.length;i++){\n"
  "      lv=A3D.levels[i];\n"
  "      lvlOpts+='<option value=\"'+bimEsc(lv.id)+'\"'+(lv.id===A3D.activeLevel?' selected':'')+'>'+\n"
  "        bimEsc(lv.name)+'</option>';\n"
  "    }\n"
  "    vrows+=bimPropRow('Active Level','<select data-propmodel=\"level\">'+lvlOpts+'</select>');\n"
  "    var lyrOpts='';\n"
  "    for(i=0;i<A3D.layers.length;i++){\n"
  "      ly=A3D.layers[i];\n"
  "      lyrOpts+='<option value=\"'+bimEsc(ly.id)+'\"'+(ly.id===A3D.activeLayer?' selected':'')+'>'+\n"
  "        bimEsc(ly.name)+'</option>';\n"
  "    }\n"
  "    vrows+=bimPropRow('Active Layer','<select data-propmodel=\"layer\">'+lyrOpts+'</select>');\n"
  "    vrows+=bimPropRow('Appearance','<select data-propmodel=\"present\">'+\n"
  "      '<option value=\"0\"'+(A3D.presentMode?'':' selected')+'>Technical</option>'+\n"
  "      '<option value=\"1\"'+(A3D.presentMode?' selected':'')+'>Presentation</option></select>');\n"
  "    /* Read-only and honest: the engine works in metres throughout and there is no unit\n"
  "       conversion layer, so this states the fact rather than offering a switch that would not\n"
  "       convert anything. */\n"
  "    vrows+=bimPropText('Units','Meters');\n"
  "    vrows+=bimPropText('View',A3D.flat?'Plan':'3D');\n"
  "    h+=bimPropGroup('View',vrows);\n"
  "\n"
  "    var nRooms=0,nWalls=0,nOpen=0;\n"
  "    for(i=0;i<A3D.objs.length;i++){\n"
  "      var ob=A3D.objs[i];\n"
  "      if(ob.t==='room')nRooms++;\n"
  "      else if(ob.t==='opening')nOpen++;\n"
  "      else if(ob.bim&&ob.bim.type==='wall')nWalls++;\n"
  "    }\n"
  "    var srows='';\n"
  "    srows+=bimPropText('Objects',A3D.objs.length);\n"
  "    srows+=bimPropText('Walls',nWalls);\n"
  "    srows+=bimPropText('Openings',nOpen);\n"
  "    srows+=bimPropText('Rooms',nRooms);\n"
  "    srows+=bimPropText('Levels',A3D.levels.length);\n"
  "    srows+=bimPropText('Layers',A3D.layers.length);\n"
  "    srows+=bimPropText('Sheets',A3D.sheets.length);\n"
  "    h+=bimPropGroup('Statistics',srows);\n"
  "    return h;\n"
  "  }\n"
  "  function refreshProps(){")

P('props.model.change',
  "      var go=objById(A3D.sel);\n"
  "      if(!go)return;\n"
  "      /* __acad3dV69: material assignment.",
  "      /* __acad3dV73: the no-selection model fields. Handled BEFORE the objById guard, because\n"
  "         these are the one set of inspector controls that exist precisely when nothing is\n"
  "         selected -- the old early return made them inert. */\n"
  "      var mp=ev.target&&ev.target.closest?ev.target.closest('[data-propmodel]'):null;\n"
  "      if(mp){\n"
  "        var mk=mp.getAttribute('data-propmodel'),mv=mp.value;\n"
  "        if(mk==='project'){A3D.titleBlock.project=mv;}\n"
  "        else if(mk==='client'){A3D.titleBlock.client=mv;}\n"
  "        else if(mk==='site'){updateSite('name',mv);}\n"
  "        else if(mk==='level'){setActiveLevel(mv);}\n"
  "        else if(mk==='layer'){setActiveLayer(mv);}\n"
  "        else if(mk==='present'){A3D.presentMode=(mv==='1');bimSyncPresentPill();}\n"
  "        refreshProps();paint();saveSoon();\n"
  "        return;\n"
  "      }\n"
  "      var go=objById(A3D.sel);\n"
  "      if(!go)return;\n"
  "      /* __acad3dV69: material assignment.")

# =============================================================== apply
out = src
for name, old, new, count in patches:
    n = out.count(old)
    if n != count:
        sys.exit('ANCHOR %s matched %d times (need exactly %d)' % (name, n, count))
    out = out.replace(old, new)
    print('  applied %-22s x%d' % (name, count))

assert "canvas:['insert'" not in out, 'the canvas workspace tab set survives'
assert "data-wsm=\"canvas\"" not in out, 'the canvas menu row survives'
assert 'bimModelPropsHtml' in out
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
