"""falsify_phase96.py -- break the V96 build eleven ways, keeping the marker.

Each variant breaks one thing the suite claims to measure. Each must make the suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. the y-down sign is lost, so the screen and the export disagree about which way a hatch runs.
    'rotation_sign_lost': [(
        "    return yDown?-a:a;",
        "    return a;")],
    # 2. the angle is stored, shown, and never applied on canvas.
    'canvas_ignores_angle': [(
        "      var ang=bimPatternRotation(rg.patternAngle,true);",
        "      var ang=0;")],
    # 3. the SVG pattern definition drops the transform.
    'svg_ignores_angle': [(
        "    var xf=rot?(' patternTransform=\"rotate('+rot.toFixed(4)+')\"'):'';",
        "    var xf='';")],
    # 4. the angle leaves the pattern's identity, so every angle shares the first definition.
    'angle_not_interned': [(
        "        var key=rg.pattern+'|'+col+'|'+sc+'|'+ang;",
        "        var key=rg.pattern+'|'+col+'|'+sc;")],
    # 5. the hatch goes back to being a presentation-mode appearance.
    'hatch_present_only': [(
        "    g.explicit=true;   /* __acad3dV96: drawn geometry, not a presentation-mode appearance */",
        "    g.explicit=false;")],
    # 6. the angle stops being normalised, so 200 and 20 compare unequal and draw the same.
    'angle_not_normalised': [(
        "    if(typeof src.patternAngle==='number'&&isFinite(src.patternAngle))\n"
        "      dst.patternAngle=((src.patternAngle%180)+180)%180;",
        "    if(typeof src.patternAngle==='number'&&isFinite(src.patternAngle))\n"
        "      dst.patternAngle=src.patternAngle;")],
    # 7. the shared field validator stops carrying patternAngle at all.
    'validator_drops_angle': [(
        "    if(typeof src.patternAngle==='number'&&isFinite(src.patternAngle))",
        "    if(false&&typeof src.patternAngle==='number'&&isFinite(src.patternAngle))")],
    # 8. HATCH goes back to being unreachable in the BIM workspace.
    'hatch_unreachable': [(
        "    hatch:function(){bimOpenHatchDlg('new');},     /* __acad3dV96 */",
        "    hatchXX:function(){bimOpenHatchDlg('new');},")],
    # 9. HATCHEDIT writes hatch fields onto whatever is selected, hatch or not.
    'hatchedit_no_guard': [(
        "    if(!bimIsHatch(o)){a3dToast('Hatchedit: select a hatch first');return null;}",
        "    if(!o){return null;}")],
    # 10. a hatch traced round a curve loses the curve.
    'hatch_drops_bulges': [(
        "        (((opts.patternAngle%180)+180)%180):0\n    };\n    if(bimHasBulge(bulges))o.bulges=bulges.slice();",
        "        (((opts.patternAngle%180)+180)%180):0\n    };\n    if(false)o.bulges=bulges.slice();")],
    # 11. the DXF stops reporting that a hatch went out as a bare boundary.
    'dxf_hatch_silent': [(
        "        poly(o.pts,true,lay,o.bulges||null);\n        stats.hatch=(stats.hatch||0)+1;",
        "        stats.hatch=(stats.hatch||0)+1;")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV96' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
