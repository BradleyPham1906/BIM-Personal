"""falsify_phase147.py -- break the V147 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_tokens': [("#a3d-right{--pp-bg:#1e2226;", "#a3d-right{--pp-bgx:#1e2226;")],
    'light_not_redefined': [("body.light-theme #a3d-right{--pp-bg:#fbfbfc;", "body.light-theme #a3d-rightx{--pp-bg:#fbfbfc;")],
    'uppercase_headers': [("letter-spacing:0;text-transform:none;color:var(--pp-text)}", "letter-spacing:0;text-transform:uppercase;color:var(--pp-text)}")],
    'header_boxed': [("#a3d-right .a3d-pgrp{background:transparent;border-radius:0;border-top:1px solid var(--pp-line);", "#a3d-right .a3d-pgrp{background:#262b31;border-radius:0;border-top:0;")],
    'grid_overflows': [("grid-template-columns:minmax(0,38fr) minmax(0,62fr);gap:10px;", "grid-template-columns:38% 62%;gap:10px;")],
    'inputs_uneven': [("border-radius:6px;min-height:26px;padding:3px 8px;font:inherit;font-size:11.5px;box-sizing:border-box;", "border-radius:6px;padding:3px 8px;font:inherit;font-size:11.5px;box-sizing:border-box;")],
    'buttons_square': [("#a3d-right #a3d-propsbody button{min-height:26px;padding:0 10px;border-radius:6px;", "#a3d-right #a3d-propsbody button{min-height:26px;padding:0 10px;border-radius:2px;")],
    'type_name_small': [("#a3d-right .a3d-ptypename{font-size:13px;", "#a3d-right .a3d-ptypename{font-size:11.5px;")],
    'unclamped': [("var p=bimRightPrefs();p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,w)));bimRightSave(p);", "var p=bimRightPrefs();p.w=Math.round(w);bimRightSave(p);"),
                  ("var w=isFinite(p.w)?Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,p.w)):null;", "var w=isFinite(p.w)?p.w:null;")],
    'width_not_saved': [("  function bimRightSave(p){try{localStorage.setItem(BIM_RIGHT_KEY,JSON.stringify(p));}catch(eW){}}", "  function bimRightSave(p){A3D_RIGHT_MEM=p;}\n  var A3D_RIGHT_MEM={};"),
                        ("  function bimRightPrefs(){try{var v=JSON.parse(localStorage.getItem(BIM_RIGHT_KEY)||'null');return v&&typeof v==='object'?v:{};}catch(eR){return {};}}", "  function bimRightPrefs(){return JSON.parse(JSON.stringify(A3D_RIGHT_MEM));}")],
    # RETIRED IN V147: the drawing follows the panel through bimObserveViewport's ResizeObserver,
    # so the explicit size() after a width change is belt and braces; removing it changes nothing.
    #   [("    var r=bimRightApply();try{size();paint();}catch(eS){}\n    return r; ...", "... without size()")],
    'drag_dead': [("      function mv(e){var w=Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,w0+(x0-e.clientX)));", "      function mv(e){var w=w0;")],
    'drag_backwards': [("w0+(x0-e.clientX)", "w0-(x0-e.clientX)")],
    'no_reset': [("    g.addEventListener('dblclick',function(){var p=bimRightPrefs();delete p.w;", "    g.addEventListener('dblclick',function(){var p=bimRightPrefs();")],
    'minimise_dead': [("      b.addEventListener('click',function(){bimRightToggleMin();});", "      b.addEventListener('click',function(){});")],
    'minimise_body_shown': [("body.a3d-rmin #a3d-right #a3d-propsbody,body.a3d-rmin .a3d-rgrip{display:none}", "body.a3d-rmin .a3d-rgrip{display:none}")],
    'minimise_button_text': [("b.innerHTML='<svg viewBox=", "b.innerHTML='Hide<svg viewBox=")],
    'narrow_forced': [("rp.style.width=(w&&bimRightDesktop()&&!p.min)?w+'px':'';", "rp.style.width=(w&&!p.min)?w+'px':'';")],
    'no_show_all': [("'<div class=\"a3d-histmore\"><button type=\"button\" data-histact=\"all\">Show all '+d.length+'</button></div>'", "'<div class=\"a3d-histmore\">and '+(d.length-max)+' more</div>'")],
    'show_all_dead': [("    if(k==='all'){A3D_HIST_ALL=true;refreshProps();return true;}   /* __acad3dV147 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV147' in txt
out.write_text(txt, encoding='utf-8')
