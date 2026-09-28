"""falsify_phase113.py -- break the V113 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the command palette, which acadWorkspaceV1 now owns end to end
    'palette_no_ctrl_k': [("      if((e.metaKey||e.ctrlKey)&&e.key&&e.key.toLowerCase()==='k'){e.preventDefault();openPal();return;}",
                           "      if(false){e.preventDefault();openPal();return;}")],
    'palette_escape_ignored': [("      if(e.key==='Escape'&&pal.classList.contains('show'))closePal();\n    });\n    document.addEventListener('pointerdown'",
                                "    });\n    document.addEventListener('pointerdown'")],
    'palette_outside_click_ignored': [("      if(!e.target.closest('#uploaded-command-palette'))closePal();", "")],
    'palette_no_focus': [("      setTimeout(function(){try{input.focus();}catch(eO){}},20);", "")],
    'palette_stale_input': [("      pal.classList.add('show');\n      input.value='';\n      draw();", "      pal.classList.add('show');\n      draw();")],
    'palette_owner_unnamed': [("    window.__wsPaletteOwner='acadWorkspaceV1';", "")],
    'palette_keeps_keyboard': [("      try{input.blur();}catch(eB){}\n      try{if(document.activeElement===input)document.body.focus();}catch(eF){}", "")],

    # ---- the material library, moved out of the deleted Precision Workbench
    'library_not_published': [("window.__WB_MATERIAL_CARDS=A3D_MATERIAL_LIBRARY;", "")],
    'library_cached_snapshot': [("  function bimMaterialCards(){\n    var c=window.__WB_MATERIAL_CARDS;\n    return (c&&c.length)?c:[];\n  }",
                                 "  var __matCache=null;\n  function bimMaterialCards(){\n    if(__matCache)return __matCache;\n    var c=window.__WB_MATERIAL_CARDS;\n    __matCache=(c&&c.length)?c.slice():[];\n    return __matCache;\n  }")],
    'library_density_changed': [("{name:'Steel',kind:'Metal',density:7900,", "{name:'Steel',kind:'Metal',density:7850,")],
    'library_hatch_lost': [("var A3D_MATERIAL_LIBRARY=[", "var A3D_MATERIAL_LIBRARY=[].concat([")],

    # ---- the left rail, which the BIM engine now builds
    'shell_not_claimed': [("    sh.setAttribute('data-a3dshell','1');", "    sh.setAttribute('data-a3dshell','0');")],
    'shell_tabs_dead': [("      if(tb)bimShellSetTab(tb.getAttribute('data-tab'));", "")],
    'shell_collapse_dead': [("      if(tg){sh.classList.toggle('collapsed');bimShellDockW();return;}", "      if(tg)return;")],
    'shell_dock_width_fixed': [("        (sh&&sh.classList.contains('collapsed'))?'54px':'296px');", "        '296px');")],
    'shell_assets_never_render': [("    try{bimCleanShell();}\n    catch(eT){console.warn('[BIM] Shell tab render failed',eT);a3dToast('That panel could not be drawn');}",
                                   "    try{}catch(eT){}")],
    'rail_icon_name_collides': [("  var A3D_SHELL_ICONS={", "  var A3D_RAIL_ICONS={"),
                                ("(A3D_SHELL_ICONS[k]||'')", "(A3D_RAIL_ICONS[k]||'')")],
    'qat_icons_removed': [("    saveJson:'<svg viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"1.7\"><path d=\"M5 3h11l3 3v15H5z\"/><path d=\"M8 3v6h8V3\"/><rect x=\"8\" y=\"13\" width=\"8\" height=\"8\"/></svg>',", "")],

    # ---- the names the app calls itself
    'title_still_canvas': [("<title>CAD/BIM workspace</title>", "<title>Enhanced Obsidian Canvas</title>")],
    'logo_still_canvas': [('<div class="acad-logo" title="CAD/BIM workspace">A</div>', '<div class="acad-logo" title="Ultimate Canvas">A</div>')],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV113' in txt
out.write_text(txt, encoding='utf-8')
