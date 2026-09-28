"""falsify_phase109.py -- break the V109 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'group_not_created': [("      '<span id=\"a3d-navgrp\">'+   /* __acad3dV109", "      '<span id=\"a3d-navgrpX\">'+   /* __acad3dV109")],
    'handler_on_old_pill': [("    el.pill=root.querySelector('#a3d-navgrp');", "    el.pill=root.querySelector('#a3d-pill');")],
    'panel_map_stale': [("navpill:'#a3d-navgrp'", "navpill:'#a3d-pill'")],
    'hide_rule_stale': [("#a3d-snapgrp.a3d-hide-panel,#a3d-navgrp.a3d-hide-panel{display:none}", "#a3d-snapgrp.a3d-hide-panel{display:none}")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV109' in txt
out.write_text(txt, encoding='utf-8')
