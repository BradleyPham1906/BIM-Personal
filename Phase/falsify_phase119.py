"""falsify_phase119.py -- break the V119 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

SPRING = "'<div class=\"acad-spring\"></div>'"
FLIP = ("    if(A3D_VIEW.kind!=='sheet')bimSetActiveView(A3D.flat?'plan':'3d',A3D.flat?A3D.activeLevel:null,null);\n"
        "    else refreshHud();\n")
SETVIEW = ("    var v=VIEWS[name],o={anim:anim!==false};\n"
           "    if(!v)return false;\n"
           "    if(name==='top')return bimActivateView('plan',null,o);\n"
           "    if(!v.ortho){o.home=(name==='home');return bimActivateView('3d',null,o);}\n"
           "    return bimActivateView('elev',name,o);\n")
TOO = "   /* __acad3dV119: an elevation is flat too */\n"
DRAFT = "    else if(!bimCameraIsPlan())bimActivateView('plan',null,{anim:false});" + TOO
PLAN_ONLY = "    if(!bimCameraIsPlan())return;   /* __acad3dV119: flat is not plan -- an elevation is flat */\n"
NORTH_CLEAR = "    A3D.lastNorth=null;   /* __acad3dV119: what the hook reports is what this frame drew */\n"

VARIANTS = {
    # ---- 119a: the dropdown is gone and the HUD names the view
    'dropdown_back': [("'<div class=\"acad-spring\"></div>'",
                       "'<div class=\"acad-ws\">Drafting &amp; Annotation</div><div class=\"acad-spring\"></div>'")],
    'menu_hook_back': [("  window.__a3dHitSizes=function(){\n",
                        "  window.__a3dWorkspaces=function(){return [];};\n  window.__a3dHitSizes=function(){\n")],
    'hud_camera_word': [("    if(el.view)el.view.textContent=A3D_VIEW.name;\n", "    if(el.view)el.view.textContent=A3D.view;\n")],

    # ---- 119b: the rail
    'rail_caption': [("      bimRailIcon('browser')+'</button>'+", "      bimRailIcon('browser')+'<span>Project Browser</span></button>'+")],
    'rail_no_aria': [('title="Assets" aria-label="Assets"', 'title="Assets"')],
    'rail_no_icon': [("      bimRailIcon('assets')+'</button>'+", "      '</button>'+")],
    'rail_two_marked': [("      btns[i].classList.toggle('active',btns[i].getAttribute('data-tab')===t);\n",
                         "      btns[i].classList.add('active');\n")],
    'rail_top_dead': [("      if(tg){sh.classList.toggle('collapsed');bimShellDockW();return;}\n", "      if(tg){return;}\n")],

    # ---- 119d: every view switch records the view
    'flip_no_record': [(FLIP, "    refreshHud();\n")],
    'preset_camera_only': [(SETVIEW, "    if(!VIEWS[name])return false;\n    bimAimPreset(name,anim);\n    return true;\n")],
    'home_not_framed': [("        bimAimPreset(opts.home?'home':'iso',anim);", "        bimAimPreset('iso',anim);")],
    'fit_goes_home': [("    if(!bb){bimFrameNothing();return;}\n", "    if(!bb){setView('home');return;}\n")],
    'fit_keeps_zoom': [("    c.dist=DEFCAM.dist;c.tx=DEFCAM.tx;c.ty=DEFCAM.ty;c.tz=DEFCAM.tz;\n    paint();saveSoon();\n", "    paint();saveSoon();\n")],
    'go_button_direct': [("bimActivateView('saved',goBtn.getAttribute('data-viewgo'))", "bimApplyView(goBtn.getAttribute('data-viewgo'))")],
    'apply_hook_direct': [("  window.__a3dApplyView=function(id){return bimActivateView('saved',id);};", "  window.__a3dApplyView=bimApplyView;")],
    'flat_query_toggles': [("    if(on!==undefined&&!!on!==A3D.flat)toggleFlat();\n", "    if(!!on!==A3D.flat)toggleFlat();\n")],
    'mark_not_set': [("    A3D.activeViewId=(kind==='saved')?(id||null):null;\n", "")],

    # ---- 119e: the name follows what it names
    'plan_not_synced': [("    if(k==='plan')id=A3D.activeLevel;\n", "")],
    'sync_not_called': [("    bimViewSync();\n", "")],
    'vanished_kept': [("    if(k==='saved'&&!bimSavedViewById(id)){\n", "    if(false){\n")],
    'camera_view_is_3d': [("    if(A3D.section)return {kind:'section',id:null};\n    if(!A3D.flat)return {kind:'3d',id:null};\n",
                           "    return {kind:'3d',id:null};\n")],
    'camera_view_first_preset': [("      if(d<bd){bd=d;best=k;}\n", "      if(!best)best=k;\n")],
    'save_not_recorded': [("    bimSetActiveView('saved',v.id,v);   /* __acad3dV119: the saved view is the one on screen, and named so */\n",
                           "    A3D.activeViewId=v.id;\n")],
    'undo_restores_mark': [("views:A3D.views,levelFilter:A3D.levelFilter,types:A3D.types,activeWallType:A3D.activeWallType,sheets:A3D.sheets,titleBlock:A3D.titleBlock,buildings:A3D.buildings,activeBuilding:A3D.activeBuilding,site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications});\n  }\n  function pushUndo(){",
                            "views:A3D.views,activeViewId:A3D.activeViewId,levelFilter:A3D.levelFilter,types:A3D.types,activeWallType:A3D.activeWallType,sheets:A3D.sheets,titleBlock:A3D.titleBlock,buildings:A3D.buildings,activeBuilding:A3D.activeBuilding,site:A3D.site,roomScheme:A3D.roomScheme||'',classifications:A3D.classifications});\n  }\n  function pushUndo(){"),
                           ("    A3D.views=st.views||[];\n", "    A3D.views=st.views||[];\n    A3D.activeViewId=st.activeViewId||null;\n")],

    # ---- 119f: a section is a view
    'section_not_recorded': [("    if(A3D_VIEW.kind!=='sheet')bimSetActiveView('section',null,null);\n", "")],
    'section_label': [("    if(kind==='section')return 'Section';   /* __acad3dV119 */\n", "")],
    'exit_not_restoring': [("    }else bimSetActiveView(rec.kind,rec.id,null);\n", "    }else refreshHud();\n")],
    'tool_no_record': [(",\n      record:{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};   /* __acad3dV119: the view to come back to */\n", "};\n")],
    'saved_section_stays': [("      bimEnterSection(v.section.p,v.section.dir,back);   /* __acad3dV119 */\n",
                             "      bimEnterSection(v.section.p,v.section.dir,{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz,flat:A3D.flat,view:A3D.view});\n")],
    'no_section_kind': [("      }else if(kind==='section'){\n", "      }else if(kind==='no-section'){\n")],
    'model_tab_not_repointed': [("      if(A3D_LAST_MODEL_VIEW&&A3D_LAST_MODEL_VIEW.kind==='section')\n", "      if(false)\n")],
    'bad_record_kept': [("    if(!rec||rec.kind==='sheet'||rec.kind==='section')rec=bimViewOfCamera();\n", "    if(!rec)rec=bimViewOfCamera();\n")],

    # ---- 119g: one test for a plan
    'plan_ignores_pitch': [("    return !!(A3D.flat&&!A3D.section&&A3D.cam.pitch>1.4);\n", "    return !!(A3D.flat&&!A3D.section);\n")],
    'draft_flat_is_plan': [(DRAFT + "  }\n", "  }\n")],
    'section_tool_flat_is_plan': [(DRAFT + "    var lvl=bimGetActiveLevel();\n", "    var lvl=bimGetActiveLevel();\n")],
    'terrain_in_elev': [("    A3D.lastTerrainDrawn=null;\n" + PLAN_ONLY, "    A3D.lastTerrainDrawn=null;\n    if(!A3D.flat||A3D.section)return;\n")],
    'north_in_elev': [(NORTH_CLEAR + PLAN_ONLY, NORTH_CLEAR + "    if(!A3D.flat||A3D.section)return;\n")],
    'north_not_cleared': [(NORTH_CLEAR, "")],
    'shadows_in_elev': [("    if(!A3D.showSun||!bimCameraIsPlan())return;   /* __acad3dV119 */\n", "    if(!A3D.showSun||!A3D.flat||A3D.section)return;\n")],
    'sunpath_in_elev': [("    if(!A3D.showSun||!bimCameraIsPlan()||A3D.sheetCapture)return;   /* __acad3dV119 */\n",
                         "    if(!A3D.showSun||!A3D.flat||A3D.section||A3D.sheetCapture)return;\n")],
    'sun_toast_flat': [("    else if(!bimCameraIsPlan())a3dToast('Sun study on:", "    else if(!A3D.flat)a3dToast('Sun study on:")],

    # ---- 119h: the cube is clickable only where it is drawn
    'cube_stale': [("      else{A3D.cubePolys=[];A3D.homeRect=null;}   /* __acad3dV119: not drawn, not clickable */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV119' in txt
out.write_text(txt, encoding='utf-8')
