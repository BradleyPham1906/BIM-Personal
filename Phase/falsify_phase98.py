"""falsify_phase98.py -- break the V98 build one way at a time, keeping the marker.

Each variant breaks one thing the annotation/grid suite claims to measure. Each must make the
suite FAIL.
"""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # 1. annotations picked last again: a room swallows the label inside it.
    'annot_picked_last': [(
        "    var an=bimPickAnnotation(x,y);\n    if(an)return an;\n", "")],
    # 2. only linear dimensions pickable, as before.
    'linear_only': [(
        "      if(o.t!==t||!bimAnnotDrawable(o))continue;",
        "      if(o.t!==t||!bimAnnotDrawable(o))continue;\n      if(t==='dim'&&bimDimKind(o)!=='linear')continue;")],
    # 3. labels are not part of the pick shape.
    'no_label_boxes': [(
        "      if(x>=b[0]&&x<=b[2]&&y>=b[1]&&y<=b[3])return 0;", "")],
    # 4. pick ignores view scoping, which draw honours.
    'pick_ignores_view': [(
        "    if(!bimAnnotationVisible(o))return false;\n    if(!bimObjectVisibleOnLevel(o))return false;\n    return true;",
        "    return true;")],
    # 5. annotations have no grips.
    'no_annot_grips': [(
        "    if(ap)return {pts:ap,y:o.y||0,kind:'annot'};", "")],
    # 6. a point drag on a linear dim forgets the offset.
    'linear_drops_offset': [(
        "          p3=[a[0]+(-dz/len)*off,a[1]+(dx/len)*off];",
        "          p3=[a[0],a[1]];")],
    # 7. the grip drag never reaches annotations.
    'annot_drag_unwired': [(
        "          bimDragAnnotPoint(o,drag.idx,[snapped[0],snapped[1]]);", "")],
    # 8. the angular grip moves the point but does not re-measure.
    'angular_not_remeasured': [(
        "        o.a1=r.a1;o.sweep=r.sweep;o.arcRadius=r.radius;o.degrees=r.degrees;",
        "        o.a1=r.a1;o.sweep=r.sweep;o.arcRadius=r.radius;")],
    # 9. the radius text grip changes the radius instead of swinging round it.
    'radius_grip_changes_radius': [(
        "          r=bimComputeRadialDim(o.center,o.radius,p,isD);",
        "          r=bimComputeRadialDim(o.center,Math.sqrt((p[0]-o.center[0])*(p[0]-o.center[0])+(p[1]-o.center[1])*(p[1]-o.center[1])),p,isD);")],
    # 10. the leader landing does not follow the elbow.
    'leader_landing_stays': [(
        "        o.anchor=r.anchor;o.elbow=r.elbow;o.landing=r.landing;o.ldir=r.dir;",
        "        o.anchor=r.anchor;o.elbow=r.elbow;o.ldir=r.dir;")],
    # 11. a click never selects a grid.
    'grid_click_dead': [(
        "      A3D.selGrid=gpk?gpk.id:null;", "      A3D.selGrid=null;")],
    # 12. grids get no grips.
    'grid_no_grips': [(
        "        A3D.grips.push({x:gsp[0],y:gsp[1],idx:gk,objId:gs.id,kind:'grid',elev:gy});", "")],
    # 13. the grid grip drag writes nothing.
    'grid_grip_inert': [(
        "            if(drag.idx)gg.p2=[snapped[0],snapped[1]];else gg.p1=[snapped[0],snapped[1]];", "")],
    # 14. the grid body drag moves only one end.
    'grid_body_one_end': [(
        "        gmG.p1=[gm.p1[0]+mdx,gm.p1[1]+mdz];gmG.p2=[gm.p2[0]+mdx,gm.p2[1]+mdz];",
        "        gmG.p1=[gm.p1[0]+mdx,gm.p1[1]+mdz];")],
    # 15. duplicate grid names accepted.
    'grid_dup_names': [(
        "        a3dToast('Grid '+name+' already exists - grid names must be unique');return false;",
        "        break;")],
    # 16. Delete ignores a selected grid.
    'grid_delete_dead': [(
        "    if(!ids.length&&bimSelectedGrid())return bimRemoveGrid(A3D.selGrid);   /* __acad3dV98 */", "")],
    # 17. Escape leaves the grid selected.
    'grid_escape_dead': [(
        "        A3D.sel=null;A3D.sel2=null;A3D.selSet=[];A3D.selGrid=null;   /* __acad3dV98 */",
        "        A3D.sel=null;A3D.sel2=null;A3D.selSet=[];")],
    # 18. the Levels-panel row does not select.
    'grid_row_dead': [(
        "      if(grow){bimSelectGrid(grow.getAttribute('data-a3dgrid'));return;}", "")],
    # 19. grids picked BEFORE the model: a sketch on a grid loses the click.
    'grid_before_model': [(
        "    var o=pick(xy[0],xy[1]);\n    if(ev.ctrlKey||ev.metaKey){\n      if(o&&o.id!==A3D.sel)A3D.sel2=(A3D.sel2===o.id)?null:o.id;",
        "    var o=bimPickGrid(xy[0],xy[1])?null:pick(xy[0],xy[1]);\n    if(ev.ctrlKey||ev.metaKey){\n      if(o&&o.id!==A3D.sel)A3D.sel2=(A3D.sel2===o.id)?null:o.id;")],
    # 20. the grid properties panel is never shown.
    'grid_props_dead': [(
        "    if(gP){el.propsbody.innerHTML=bimGridPropsHtml(gP);return;}", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d' % (name, txt.count(old))
    txt = txt.replace(old, new, 1)
assert '__acad3dV98' in txt
out.write_text(txt, encoding='utf-8')
print('wrote %s' % out)
