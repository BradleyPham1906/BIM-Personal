"""falsify_phase120.py -- break the V120 build one way at a time, keeping the marker.

Each variant puts back one kind of thing the cleanup took out, or breaks one thing it kept, and the
V120 suite must fail on every one of them."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

CSS_END = ("body.a3d-tree-docked #a3d-leftpanel > .a3d-tree .a3d-palhd .a3d-palbtns{flex-wrap:wrap;flex:1 1 100%;"
           "justify-content:flex-start;}\n</style>")
LIBFN = "  function bimMaterialCards(){\n    return A3D_MATERIAL_LIBRARY;   /* __acad3dV120 */\n  }"
TOPBAR_DT = "    var dt=document.createElement('div');dt.id='acad-doctabs';\n    shell.appendChild(dt);"
RDRAWER = "      if(act==='rdrawer'){var rp=document.getElementById('a3d-right');if(rp)rp.classList.toggle('open');}\n    });"

VARIANTS = {
    # ---- the stylesheet: a rule nothing can match, a property nothing reads, a second sheet
    'dead_css_rule': [(CSS_END, CSS_END.replace('\n</style>', '\n.node .content{overflow:auto}\n</style>'))],
    'unread_property': [(":root{--bg:#191919;--text:#ffffff;}", ":root{--bg:#191919;--text:#ffffff;--j-green:#56FFA6;}")],
    'second_stylesheet': [("</script>\n\n</body>", "</script>\n\n<style>.a3d-hud{color:inherit}</style>\n</body>")],
    'runtime_sheet_back': [("    var root=document.createElement('div');\n    root.id='acad3d';",
                            "    var st=document.createElement('style');st.textContent='#acad3d{outline:0}';document.head.appendChild(st);\n"
                            "    var root=document.createElement('div');\n    root.id='acad3d';")],
    # ---- names of the old modules
    'figma_comment': [(":root{--bg:#191919;--text:#ffffff;}", "/* Final robust Figma sidebar panels */\n:root{--bg:#191919;--text:#ffffff;}")],
    'toast_shim_back': [("(function acadWorkspaceV1(){\n  try{",
                         "window.toast=function(m){if(window.__a3dToast)window.__a3dToast(m);};\n(function acadWorkspaceV1(){\n  try{")],
    'module_guard_back': [("(function acadWorkspaceV1(){\n  try{",
                           "(function acadWorkspaceV1(){\n  if(window.__acadWorkspaceV1) return; window.__acadWorkspaceV1=true;\n  try{")],
    'hidden_tab_strip_back': [(TOPBAR_DT, "    var tb=document.createElement('div');tb.id='acad-tabs';tb.style.display='none';\n"
                                          "    shell.appendChild(tb);\n" + TOPBAR_DT)],
    # ---- dead code a derivation finds
    'dead_function': [(LIBFN, LIBFN + "\n  function bimDedupePts(arr){return arr?arr.slice():[];}")],
    'dead_toolbar_branch': [(RDRAWER, RDRAWER.replace("\n    });", "\n      else if(act==='fit')fitScene();\n    });"))],
    'library_second_reader': [(LIBFN, LIBFN + "\n  var A3D_MATERIAL_COPY=A3D_MATERIAL_LIBRARY.slice();")],
    'silent_catch': [("  console.warn('[BIM] The engine failed to load.',e);   /* __acad3dV120 */\n", "")],
    'unmatched_selector': [("ev.target.closest('[data-a3dr=\"bim:uipanels\"]')", "ev.target.closest('[data-a3d=\"uipanels\"]')")],
    # ---- whitespace
    'blank_run': [("  var LSK='acad3dV1';\n", "  var LSK='acad3dV1';\n\n\n")],
    'trailing_blank': [("  var LSK='acad3dV1';\n", "  var LSK='acad3dV1';   \n")],
    # ---- what stayed, broken
    'qat_dead': [("      if(ab)dispatch(ab.getAttribute('data-acad-act'));", "      if(ab)return;")],
    'palette_rows_renamed': [("return '<div class=\"a3d-cmdrow'+(i===0?' active':'')", "return '<div class=\"a3d-cmdline'+(i===0?' active':'')")],
    'palette_key_dead': [("      if((e.metaKey||e.ctrlKey)&&e.key&&e.key.toLowerCase()==='k'){e.preventDefault();openPal();return;}", "")],
    'edge_not_synced': [("      document.documentElement.style.setProperty('--a3d-left-w',",
                         "      document.documentElement.style.setProperty('--a3d-left-width',")],
    'boot_does_not_enter': [("      window.ACAD_WS_CUR='da';\n      window.__a3dEnter();\n", "      window.ACAD_WS_CUR='da';\n")],
    'ribbon_height_back': [(":root{--a3d-top-h:52px}", ":root{--a3d-top-h:182px}")],
    'uimenu_offscreen': [(".a3d-uimenu{display:none;position:absolute;top:100%;right:0;", ".a3d-uimenu{display:none;position:absolute;top:100%;left:0;")],
    'material_library_empty': [(LIBFN, LIBFN.replace("return A3D_MATERIAL_LIBRARY;", "return A3D_MATERIAL_LIBRARY.slice(0,0);"))],
    'rail_tab_old_id': [("    sh.setAttribute('data-tab','browser');", "    sh.setAttribute('data-tab','file');")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV120' in txt
out.write_text(txt, encoding='utf-8')
