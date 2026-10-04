"""falsify_phase150.py -- break the V150 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_palette': [("body.a3d-tier-overlay.a3d-mode .a3d-tpal{display:flex}", "")],
    'palette_on_computer': [("body.a3d-tier-overlay.a3d-mode .a3d-tpal{display:flex}", ".a3d-tpal{display:flex!important}")],
    'covers_sheet': [("body.a3d-tier-overlay.a3d-mode:has(#a3d-right.open) .a3d-tpal{display:none}\n", "")],
    'dock_stays': [("body.a3d-tier-overlay #a3d-dock{display:none!important}\n", "")],
    'no_door': [("    {id:'bim:door',label:'Door',", "    {id:'bim:doorx',label:'Door',")],
    'small_buttons': [(".a3d-tpb{width:42px;height:42px;flex:0 0 42px;", ".a3d-tpb{width:30px;height:30px;flex:0 0 30px;")],
    'not_frosted': [("-webkit-backdrop-filter:saturate(180%) blur(22px);backdrop-filter:saturate(180%) blur(22px);", "")],
    'no_active_fill': [(".a3d-tpb.on{background:#0a84ff;color:#fff}", ".a3d-tpbx.on{background:#0a84ff;color:#fff}")],
    'active_not_followed': [("    document.addEventListener('pointerup',later,true);\n    document.addEventListener('keyup',later,true);\n    document.addEventListener('click',later,true);\n", "")],
    'select_keeps_tool': [("      if(A3D.sk){try{document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true,cancelable:true}));}catch(eE){}if(A3D.sk)cancelSketch();}\n", "")],
    'pan_one_way': [("      setNav(A3D.navMode==='pan'?'orbit':'pan');", "      setNav('pan');")],
    'pan_sticks': [("    }else{\n      if(A3D.navMode==='pan')setNav('orbit');\n      bimRunAct(id);", "    }else{\n      bimRunAct(id);")],
    'more_shut_at_once': [("      setTimeout(bimOpenToolsPanel,0);", "      bimOpenToolsPanel();")],
    'no_drag': [("      p.style.left=Math.round(ev.clientX-d.dx)+'px';p.style.top=Math.round(ev.clientY-d.dy)+'px';", "")],
    'no_edge_dock': [("    if(cx<A.l+edge)s={side:'l'};else if(cx>A.r-edge)s={side:'r'};else s={side:null};", "    s={side:null};")],
    'edge_by_middle': [("        bimTPalDrop(ev.clientX<A.l+edge?A.l:ev.clientX>A.r-edge?A.r:r.left+r.width/2,r.top+r.height/2);", "        bimTPalDrop(r.left+r.width/2,r.top+r.height/2);")],
    # RETIRED IN V150: the kept spot is a fraction of the drawing area, clamped to 0..1 when dropped,
    # so the clamp in bimTPalPlace cannot be reached by a drag.
    #   'xunclamped_retired': [("    x=Math.max(A.l+m,Math.min(A.r-w-m,x));y=Math.max(A.t+m,Math.min(A.b-h-m,y));\n", "")],
    'not_kept': [("  function bimTPalSave(p){try{localStorage.setItem(BIM_TPAL_KEY,JSON.stringify(p));}catch(eS){}}", "  function bimTPalSave(p){}")],
    'no_fold': [("      if(ev.target.closest('[data-tptoggle]'))bimTPalFold(true);", "")],
    'fold_shows_select': [("    if(cur&&cur.getAttribute('data-for')!==a){", "    if(cur&&!cur.getAttribute('data-for')){a='select';")],
    'folded_tap_dead': [("      else if(ev.target.closest&&ev.target.closest('[data-tpcur]'))bimTPalFold(false);   /* a tap on the folded button opens it */\n", "")],
    'folded_not_round': [(".a3d-tpcur{display:none;width:50px;height:50px;border-radius:50%;", ".a3d-tpcur{display:none;width:50px;height:50px;border-radius:4px;")],
    'phone_flat_default': [("    if(!s)s=k==='phone'?{side:'r',fy:0.42}:{side:null,fx:0.5,fy:1};", "    if(!s)s={side:null,fx:0.5,fy:1};")],
    'toast_behind': [("body.a3d-tier-overlay:not(.a3d-tier-phone) #a3d-toast{bottom:146px!important}\n", "")],
    # RETIRED IN V150: the shell audit reads the shell, and the palette is the page's, not the shell's.
    #   'xaudit_retired': [("    {sel:'[data-tpact]',why:'the palette: a tool, Select, Pan or every tool'},   /* __acad3dV150 */\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV150' in txt
out.write_text(txt, encoding='utf-8')
