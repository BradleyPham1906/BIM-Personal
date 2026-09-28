"""falsify_phase100.py -- break the V100 build one way at a time, keeping the marker."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'escape_discards': [(
        "      if(A3D.sk){bimEndSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}   /* __acad3dV100 */",
        "      if(A3D.sk){cancelSketch();ev.preventDefault();ev.stopImmediatePropagation();return;}")],
    'view_change_discards': [(
        "    if(A3D.sk)bimEndSketch();   /* __acad3dV100: a view change used to discard the drawing */",
        "    if(A3D.sk)cancelSketch();")],
    'new_command_discards': [(
        "    if(A3D.sk)bimEndSketch();   /* __acad3dV100: a new command ends the old one, keeping it */", "")],
    'section_discards': [(
        "    if(A3D.sk)bimEndSketch();   /* __acad3dV100: the one starter that skips bimEnterDraftingMode */", "")],
    'keep_every_tool': [(
        "    return !!(sk&&sk.pts&&sk.pts.length>=2&&(sk.tool==='line'||sk.tool==='poly'||sk.tool==='wall'));",
        "    return !!(sk&&sk.pts&&sk.pts.length>=2);")],
    'poly_enter_closes': [(
        "    else if(sk.tool==='poly'){if(sk.pts.length>=2)finishPoly(true);else{A3D.sk=null;paint();}}",
        "    else if(sk.tool==='poly'){if(sk.pts.length>=3)finishPoly();else{A3D.sk=null;paint();}}")],
    'poly_open_needs_three': [(
        "      if(sk.pts.length<2)return null;\n      var ob=", "      if(sk.pts.length<3)return null;\n      var ob=")],
    'close_opens': [(
        "    if(sk.pts.length<3)return null;\n    return addSketchObj(sk.pts.slice(),{bulges:sk.bulges});",
        "    if(sk.pts.length<3)return null;\n    return addSketchObj(sk.pts.slice(),{bulges:sk.bulges,closed:false});")],
    'toast_old_rule': [(
        "(tool==='poly'?'; C or click the first point to close, Enter to leave it open':'')",
        "(tool==='poly'?'; click the first point again or press Enter to close':'')")],
    'wall_interrupt_dialog': [(
        "      if(bimSketchKeepable(sk)&&sk.tool==='wall'){", "      if(false){")],
    'wall_default_thickness_drift': [(
        "    return {thk:0.3,hgt:lvl.height,align:'center'};", "    return {thk:0.25,hgt:lvl.height,align:'center'};")],
    'sketch_not_undoable': [(
        "    if(!opts.noUndo)pushUndo();   /* __acad3dV100: a drawing was never undoable */", "")],
    'line_undo_per_segment': [(
        "      o=addSketchObj([[pts[i][0],pts[i][1]],[pts[i+1][0],pts[i+1][1]]],{noUndo:true});",
        "      o=addSketchObj([[pts[i][0],pts[i][1]],[pts[i+1][0],pts[i+1][1]]]);")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV100' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
