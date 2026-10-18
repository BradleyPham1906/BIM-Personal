"""falsify_phase166c.py -- break the V166c build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    # ---- the button ----
    'button_missing': [("      hd.appendChild(wb);\n", "")],
    'button_unwired': [("wb.addEventListener('click',function(){bimRightStep();});", "wb.addEventListener('click',function(){});")],
    'button_after_minimise': [("      hd.appendChild(wb);\n", ""), ("      hd.appendChild(b);\n", "      hd.appendChild(b);hd.appendChild(wb);\n")],
    'button_small': [(".a3d-rpwbtn{width:30px;height:30px;", ".a3d-rpwbtn{width:18px;height:18px;")],
    'button_small_touch': [(".a3d-rpwbtn{width:36px;height:36px}   /* __acad3dV166c: a finger's target, and a 12 px edge it can see */\n", "")],
    'button_white': [("cursor:pointer;padding:0;flex:0 0 auto;margin:0 2px 0 auto}", "cursor:pointer;padding:0;flex:0 0 auto;margin:0 2px 0 auto;color:#fff}")],
    'button_on_drawers': [("{.a3d-rgrip,.a3d-rpwbtn{display:none}}", "{.a3d-rgrip{display:none}}")],
    'button_while_minimised': [(",body.a3d-rmin .a3d-rpwbtn{display:none}", "{display:none}")],
    # ---- the steps, and what the screen allows ----
    'steps_no_wrap': [("    return w<mx?mx:BIM_RIGHT_MIN;\n  }\n  function bimRightStep(){", "    return mx;\n  }\n  function bimRightStep(){")],
    'steps_past_screen': [("if(BIM_RIGHT_STEPS[i]>w&&BIM_RIGHT_STEPS[i]<=mx)return BIM_RIGHT_STEPS[i];", "if(BIM_RIGHT_STEPS[i]>w)return BIM_RIGHT_STEPS[i];")],
    'screen_ignored': [("    return Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,Math.floor((window.innerWidth||0)-BIM_LEFT_RAIL-BIM_LEFT_MIN-BIM_LEFT_KEEP)));", "    return BIM_RIGHT_MAX;")],
    'drawing_not_kept': [("-BIM_LEFT_RAIL-BIM_LEFT_MIN-BIM_LEFT_KEEP)));", "-BIM_LEFT_RAIL-BIM_LEFT_MIN)));")],
    'max_against_left_now': [("-BIM_LEFT_RAIL-BIM_LEFT_MIN-BIM_LEFT_KEEP)));", "-parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w'))-BIM_LEFT_KEEP));")],
    'kept_forced': [("Math.min(bimRightMax(),p.w)):null;   /* __acad3dV166c", "Math.min(BIM_RIGHT_MAX,p.w)):null;   /* __acad3dV166c")],
    'set_unclamped': [("    else p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(bimRightMax(),w)));", "    else p.w=Math.round(Math.max(BIM_RIGHT_MIN,Math.min(BIM_RIGHT_MAX,w)));")],
    'step_not_kept': [("  function bimRightStep(){return bimRightSetWidth(bimRightNext());}", "  function bimRightStep(){var r=document.getElementById('a3d-right');r.style.width=bimRightNext()+'px';return bimRightApply();}")],
    # ---- the label ----
    'label_stale': [("    if(wb){wb.setAttribute('aria-label','Properties width '+cw+' px: '+(nx>cw?'widen to '+nx:'back to '+nx));wb.title=wb.getAttribute('aria-label');}\n", "")],
    'label_says_now': [("(nx>cw?'widen to '+nx:'back to '+nx)", "(nx>cw?'widen to '+cw:'back to '+cw)")],
    'label_no_tooltip': [("wb.title=wb.getAttribute('aria-label');}", "}")],
    # ---- the edge: a window splitter ----
    'edge_not_focusable': [("g.className='a3d-rgrip';g.tabIndex=0;", "g.className='a3d-rgrip';")],
    'edge_no_role': [("g.setAttribute('role','separator');g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-right');", "g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-right');")],
    'edge_horizontal': [("g.setAttribute('aria-orientation','vertical');g.setAttribute('aria-controls','a3d-right');", "g.setAttribute('aria-controls','a3d-right');")],
    'edge_controls_nothing': [("g.setAttribute('aria-controls','a3d-right');g.setAttribute('aria-labelledby','a3d-rpttl');", "g.setAttribute('aria-labelledby','a3d-rpttl');")],
    'edge_unnamed': [("g.setAttribute('aria-labelledby','a3d-rpttl');", "")],
    'header_name_gone': [("'<div class=\"a3d-palhd\"><span id=\"a3d-rpttl\">Properties</span></div>'", "'<div class=\"a3d-palhd\">Properties</div>'")],
    'edge_value_stale': [("    if(g){g.setAttribute('aria-valuenow',String(cw));g.setAttribute('aria-valuemin',String(BIM_RIGHT_MIN));g.setAttribute('aria-valuemax',String(mx));}\n", "")],
    'edge_valuemax_fixed': [("g.setAttribute('aria-valuemax',String(mx));}", "g.setAttribute('aria-valuemax',String(BIM_RIGHT_MAX));}")],
    'focus_unseen': [(".a3d-rgrip:hover,.a3d-rgrip.drag,.a3d-rgrip:focus-visible{", ".a3d-rgrip:hover,.a3d-rgrip.drag{")],
    # ---- its keys ----
    'keys_reversed': [("bimRightSetWidth(bimRightW()+(k==='ArrowLeft'?st:-st))", "bimRightSetWidth(bimRightW()+(k==='ArrowLeft'?-st:st))")],
    'keys_no_shift': [("bimRightSetWidth(bimRightW()+(k==='ArrowLeft'?st:-st))", "bimRightSetWidth(bimRightW()+(k==='ArrowLeft'?16:-16))")],
    'home_end_gone': [("      if(k==='Home'||k==='End'){ev.preventDefault();bimRightSetWidth(k==='Home'?BIM_RIGHT_MIN:bimRightMax());return;}\n", "")],
    'enter_ignored': [("      if(k==='Enter'){\n        ev.preventDefault();\n        bimRightToggleMin(true);\n", "      if(false){\n        ev.preventDefault();\n        bimRightToggleMin(true);\n")],
    'enter_loses_focus': [("        var mb=document.getElementById('a3d-rminbtn');if(mb)mb.focus();\n", "")],
    # ---- by any pointer ----
    'drag_mouse_only': [("    g.addEventListener('pointerdown',function(ev){\n      if(ev.button>0)return;", "    g.addEventListener('pointerdown',function(ev){\n      if(ev.button>0||ev.pointerType!=='mouse')return;")],
    'right_button_drags': [("    g.addEventListener('pointerdown',function(ev){\n      if(ev.button>0)return;\n", "    g.addEventListener('pointerdown',function(ev){\n")],
    'touch_action_default': [("cursor:col-resize;z-index:6;touch-action:none;outline:0}", "cursor:col-resize;z-index:6;outline:0}")],
    'cancel_kept': [("g.addEventListener('pointercancel',function(ev){end(ev,false);});\n    g.addEventListener('dblclick',function(){bimRightSetWidth(null);});", "g.addEventListener('pointercancel',function(ev){end(ev,true);});\n    g.addEventListener('dblclick',function(){bimRightSetWidth(null);});")],
    'drag_past_screen': [("Math.min(bimRightMax(),dr.w+dr.x-ev.clientX)", "Math.min(BIM_RIGHT_MAX,dr.w+dr.x-ev.clientX)")],
    'left_waits_for_drop': [("dr.now=w;rp.style.width=w+'px';bimShellDockW();try{", "dr.now=w;rp.style.width=w+'px';try{")],
    'left_eases_behind': [("body.a3d-rpdrag #a3d-leftpanel{transition:none}", "body.a3d-rpdrag #a3d-leftpanel{}")],
    'drag_unmarked': [("g.classList.add('drag');document.body.classList.add('a3d-rpdrag');", "g.classList.add('drag');")],
    'reset_kept': [("    if(w===null)delete p.w;   /* __acad3dV166c", "    if(w===null)p.w=280;   /* __acad3dV166c")],
    'edge_narrow_touch': [(".a3d-rgrip{left:0;width:12px;", ".a3d-rgrip{")],
    # ---- where Properties is docked ----
    'docked_wider_than_900': [("    if(window.matchMedia)return !window.matchMedia(BIM_RIGHT_SHEET_MQ).matches;\n", "    return (window.innerWidth||0)>900;\n")],
    'docked_width_only': [("var BIM_RIGHT_SHEET_MQ='(max-width:1024px),(max-height:500px)';", "var BIM_RIGHT_SHEET_MQ='(max-width:1024px)';")],
    # ---- the shell's audit ----
    'button_unclaimed': [("    {sel:'[data-rpwidth]',why:'widens Properties a step at a time: its edge, by one press'},\n", "")],
    'edge_unclaimed': [("    {sel:'.a3d-rgrip',why:'Properties\\' edge: dragged to size it, or moved from the keyboard'},   /* __acad3dV166c */\n", "")],
    'minimise_unclaimed': [("    {sel:'#a3d-rminbtn',why:'minimises Properties to a strip; on a phone or a tablet, closes its sheet or drawer'},   /* __acad3dV147, driven by its suite */\n", "")],
    'audit_misses_properties': [("    if(rpA)[].forEach.call(rpA.querySelectorAll(Q),function(e){if(!e.closest('#a3d-propsbody'))nodes.push(e);});\n", "")],
    'audit_reads_body': [("if(!e.closest('#a3d-propsbody'))nodes.push(e);", "nodes.push(e);")],
    'audit_skips_edges': [("var Q='button,[role=\"button\"],[role=\"separator\"][tabindex],a[href],input,select'", "var Q='button,[role=\"button\"],a[href],input,select'")],
    # Not variants: End to BIM_RIGHT_MAX in place of bimRightMax(), since bimRightSetWidth keeps any width
    # within what the screen allows; and Enter on the edge toggling the minimise rather than setting it,
    # since the edge is not shown while Properties is minimised, so its Enter only ever minimises.
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV166c' in txt
out.write_text(txt, encoding='utf-8')
