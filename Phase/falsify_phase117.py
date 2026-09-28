"""falsify_phase117.py -- break the V117 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

# The Delete branch as V117 wrote it, read from the build rather than retyped, so a variant that moves
# it moves exactly what is there.
_i = base.index("    /* __acad3dV117: Delete -- and Backspace")
_j = base.index("    var o=null,i;\n", _i)
BR = base[_i:_j]
HEAD = "  function onKey(ev){\n    if(!A3D.on)return;\n"
WS4 = "  // ============ 4. WORKSPACES: THE BOOT INTO THE BIM SHELL ============\n"
FIELD = "    if(bimKeyForControl(ev))return;   /* __acad3dV117: the one test, which knows a dropdown */\n"

VARIANTS = {
    # ---- Delete erases the selection
    'delete_branch_gone': [("    if((ev.key==='Delete'||ev.key==='Backspace')&&!ev.ctrlKey&&!ev.metaKey){\n",
                            "    if(false){\n")],
    'backspace_not_delete': [("if((ev.key==='Delete'||ev.key==='Backspace')&&!ev.ctrlKey&&!ev.metaKey){",
                              "if((ev.key==='Delete')&&!ev.ctrlKey&&!ev.metaKey){")],
    'multi_selection_ignored': [("if(A3D.sel||(A3D.selSet&&A3D.selSet.length)||bimSelectedGrid())delSelection();   /* __acad3dV98's test */",
                                 "if(A3D.sel){A3D.selSet=[A3D.sel];delSelection();}")],

    # ---- and stays behind the engine's gates
    'delete_before_start_gate': [(BR, ''), (HEAD, HEAD + BR)],
    'sheet_passes_delete': [("  function bimSheetKey(ev){\n",
                             "  function bimSheetKey(ev){\n    if((ev.key==='Delete'||ev.key==='Backspace')&&!A3D.sheetSelVp)return false;\n")],
    'delete_before_field_gate': [(BR, ''), (FIELD, BR + FIELD)],
    'delete_before_typing': [(BR, ''), (FIELD, FIELD + BR)],
    # RETIRED IN V119: 'delete_ignores_dialog' anchored on the Delete branch's own dialog check, which
    # V118's one dialog gate replaced; the same break is falsify_phase118's 'dialog_gate_gone'.
    'ctrl_delete_erases': [("if((ev.key==='Delete'||ev.key==='Backspace')&&!ev.ctrlKey&&!ev.metaKey){",
                            "if((ev.key==='Delete'||ev.key==='Backspace')){")],

    # ---- a dropdown is a field, for its plain keys only
    'select_not_a_field': [("    if(tg.tagName==='SELECT')return !(ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key));\n", "")],
    'select_owns_ctrl': [("    if(tg.tagName==='SELECT')return !(ev.ctrlKey||ev.metaKey||/^F\\d+$/.test(ev.key));\n",
                          "    if(tg.tagName==='SELECT')return true;\n")],

    # ---- the wire shell stays gone
    'hook_left': [("  function closeDlg(){\n", "  window.__ws3Del=function(){return false;};\n  function closeDlg(){\n")],
    # RE-ANCHORED IN V119: these two anchored on acadWs2V1's $ helper, which went with the view
    # dropdown's menu builder, its one caller. The breaks are the same, placed after section 4's header.
    'observer_back': [(WS4,
                       WS4 +
                       "  new MutationObserver(function(){var r=document.getElementById('figma-layers-rail');"
                       "if(r&&!r.querySelector('.acad-dkbtn')){var b=document.createElement('button');b.className='acad-dkbtn';r.appendChild(b);}})"
                       ".observe(document.documentElement,{childList:true,subtree:true});\n")],
    'ws2_throws': [(WS4, WS4 + "  null.boom;\n")],

    # ---- the shell that stays still works
    # RETIRED IN V119: 'wsmenu_3d_dead' broke the workspace menu's 3D entry. The owner had the menu
    # removed; the V117 suite's section that drove it was amended to the boot, and V119's suite checks
    # that every remaining way into 3D records the view.

    # ---- stored data is kept
    'stored_dock_dropped': [("    }catch(eDp){console.warn('[BIM] Could not mark the page as the BIM workspace.',eDp);}\n",
                             "    }catch(eDp){console.warn('[BIM] Could not mark the page as the BIM workspace.',eDp);}\n"
                             "    try{localStorage.removeItem('acadDockV1');}catch(eK){}\n")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV117' in txt
out.write_text(txt, encoding='utf-8')
