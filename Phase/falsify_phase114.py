"""falsify_phase114.py -- break the V114 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

TAB_LINE = """      escHtml(bimProjectName())+'</button>';
    if(html!==lastTabHtml){dt.innerHTML=html;lastTabHtml=html;}"""
FIRST_STYLE = '<style>\n'

VARIANTS = {
    # ---- the stylesheet guard: each of these puts back something that can never match
    'dead_rule_left': [(FIRST_STYLE, '<style>\n.whiteboard-leftover-panel{color:red}\n')],
    'dead_rule_in_media_nospace': [(FIRST_STYLE, '<style>\n@media(max-width:600px){.whiteboard-leftover-panel{color:red}}\n')],
    'dead_rule_in_selector_list': [(FIRST_STYLE, '<style>\n.whiteboard-leftover-panel .x,.whiteboard-leftover-card{color:red}\n')],
    'dead_keyframes_left': [(FIRST_STYLE, '<style>\n@keyframes wbGhostFade{from{opacity:0}to{opacity:1}}\n')],

    # ---- the project tab
    'plus_tab_back': [(TAB_LINE, """      escHtml(bimProjectName())+'</button><button class="acad-doctab acad-plus" data-dt="plus">+</button>';
    if(html!==lastTabHtml){dt.innerHTML=html;lastTabHtml=html;}""")],
    'tab_name_static': [("""      escHtml(bimProjectName())+'</button>';""", """      'Drawing1</button>';""")],
    'tab_never_refreshed': [("    if(document.getElementById('acad-doctabs')){renderDocTabs();setInterval(renderDocTabs,1000);return;}",
                             "    if(document.getElementById('acad-doctabs')){renderDocTabs();return;}")],
    'start_tab_active_wrong': [("""    var html='<button class="acad-doctab'+(startShown()?' active':'')+'" data-dt="start">Start</button>'+""",
                                """    var html='<button class="acad-doctab'+(startShown()?'':' active')+'" data-dt="start">Start</button>'+""")],

    # ---- the Start screen
    'start_counts_nothing': [("    try{return window.__a3dObjects?window.__a3dObjects().length:0;}",
                              "    try{return 0;}")],
    'start_offers_new_drawing': [("""      '<button data-st="continue">Continue</button>'+""",
                                  """      '<button data-st="new">New Drawing</button><button data-st="continue">Continue</button>'+""")],
    'continue_leaves_start_up': [("""    hideStart();
  });
  /* The tab carries the project's name""", """  });
  /* The tab carries the project's name""")],
    'open_does_not_open': [("      if(fi){ hideStart(); fi.value=''; fi.click(); }", "      if(fi){ hideStart(); }")],

    # ---- the toast
    'shell_toast_silent': [("  if(window.__a3dToast)return window.__a3dToast(m);", "  if(false)return window.__a3dToast(m);")],
    'engine_toast_unpublished': [("  window.__a3dToast=function(m){return a3dToast(m);};", "")],

    # ---- user data
    'drawings_deleted': [("  var lastTabHtml='';", "  try{localStorage.removeItem('acadDrawingsV1');}catch(eR){}\n  var lastTabHtml='';")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) >= 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV114' in txt
out.write_text(txt, encoding='utf-8')
