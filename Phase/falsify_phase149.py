"""falsify_phase149.py -- break the V149 build one way at a time, keeping the marker.
Variant names are lower case: the runner reads no other (V126)."""
import pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
base = SRC.read_text(encoding='utf-8')

VARIANTS = {
    'no_phone_tier': [("    if(mm('(max-width:720px) and (orientation:portrait)').matches)return 'phone';\n", "")],
    'no_overlay_tier': [("    if(mm('(max-width:720px),(max-height:500px)').matches||mm('(min-width:721px) and (max-width:1024px) and (orientation:portrait)').matches)return 'overlay';\n", "")],
    'enter_opens': [("      if(shellEl&&shellEl.classList.contains('collapsed')&&!bimShellOverlay()){", "      if(shellEl&&shellEl.classList.contains('collapsed')){")],
    'tier_no_shut': [("A3D_SHELL_DESK_SHUT=sh.classList.contains('collapsed');sh.classList.add('collapsed');}", "A3D_SHELL_DESK_SHUT=sh.classList.contains('collapsed');}")],
    'desktop_not_restored': [("      else if(tr==='desktop'&&was!==null)sh.classList.toggle('collapsed',A3D_SHELL_DESK_SHUT);\n", "")],
    'desktop_shut_forgotten': [("sh.classList.toggle('collapsed',A3D_SHELL_DESK_SHUT);", "sh.classList.remove('collapsed');")],
    'drawing_not_widened': [("        A3D_SHELL_TIER==='phone'?'0px':A3D_SHELL_TIER==='overlay'?'54px':   /* __acad3dV149: a drawer leaves the drawing where it is */\n", "")],
    'bar_on_the_left': [("body.a3d-tier-phone #a3d-rail{position:fixed;left:0;right:0;bottom:0;top:auto;width:auto;", "body.a3d-tier-phone #a3d-rail{position:fixed;left:0;bottom:0;top:auto;")],
    'no_labels': [("content:attr(data-short);font:500 10.5px/1", "content:none;font:500 10.5px/1")],
    'tabs_small': [("body.a3d-tier-phone #a3d-rail .a3d-railbtn,body.a3d-tier-phone #a3d-rail .a3d-railmore{flex:1 1 0;max-width:76px;width:auto;height:50px;",
                    "body.a3d-tier-phone #a3d-rail .a3d-railbtn,body.a3d-tier-phone #a3d-rail .a3d-railmore{flex:0 0 auto;max-width:76px;width:34px;height:34px;")],
    'rail_touch_small': [("@media(pointer:coarse){body.a3d-tier-overlay #a3d-rail .a3d-railbtn,body.a3d-tier-overlay #a3d-rail .a3d-paneltoggle{min-width:44px;min-height:44px}}", "")],
    'drawing_under_bar': [("body.a3d-tier-phone #acad3d{bottom:calc(58px + env(safe-area-inset-bottom,0px))}\n", "")],
    'drawer_full_width': [("body.a3d-tier-phone #a3d-leftpanel{left:0;bottom:calc(58px + env(safe-area-inset-bottom,0px));width:min(360px,88vw);",
                           "body.a3d-tier-phone #a3d-leftpanel{left:0;bottom:calc(58px + env(safe-area-inset-bottom,0px));width:100vw;")],
    'drawer_covers_bar': [("body.a3d-tier-phone #a3d-leftpanel{left:0;bottom:calc(58px + env(safe-area-inset-bottom,0px));", "body.a3d-tier-phone #a3d-leftpanel{left:0;bottom:0;")],
    'drawer_a_column': [("body.a3d-tier-overlay #a3d-leftpanel{position:fixed;z-index:3;top:var(--a3d-top-h);bottom:0;left:54px;", "body.a3d-tier-overlay #a3d-leftpanel{z-index:3;")],
    'shut_drawer_shown': [("transform:translateX(-104%);opacity:0;visibility:hidden;pointer-events:none}", "transform:none;opacity:1}")],
    'no_scrim': [("body.a3d-tier-overlay #a3d-shell:not(.collapsed) #a3d-shellscrim{display:block;", "body.a3d-tier-overlay #a3d-shell:not(.collapsed) #a3d-shellscrimx{display:block;")],
    'tab_no_toggle': [("        if(bimShellOverlay()&&!sh.classList.contains('collapsed')&&sh.getAttribute('data-tab')===tb.getAttribute('data-tab')){bimShellDrawer(false);return;}\n", "")],
    'esc_ignored': [("      if(ev.key!=='Escape'||!bimShellOverlay()||sh.classList.contains('collapsed'))return;", "      if(ev.key!=='Esc'||!bimShellOverlay()||sh.classList.contains('collapsed'))return;")],
    'more_dead': [("      if(mo){bimShellMore();return;}", "      if(mo){return;}")],
    'more_stays': [("      if(x&&x.closest&&(x.closest('#a3d-rail')||x.closest('#a3d-rupop')))return;\n      bimShellMore(false);", "      return;")],
    'more_hidden': [("body.a3d-tier-phone.a3d-railutil-open #a3d-railutil{display:flex;", "body.a3d-tier-phone.a3d-railutil-open #a3d-railutilx{display:flex;")],
    'more_on_desktop': [(".a3d-railmore{display:none}\n", ".a3d-railmore{display:grid;width:34px;height:34px}\n")],
    'burger_old': [("if(act==='drawer'){if(bimShellOverlay()){bimShellDrawer();return;}var tr=", "if(act==='drawer'){var tr=")],
    'burger_on_phone': [("body.a3d-tier-phone .a3d-drawerbtn{display:none!important}\n", "")],
    'toast_behind_bar': [("body.a3d-tier-phone #a3d-toast{bottom:calc(74px + env(safe-area-inset-bottom,0px))!important}\n", "")],
    'tab_lit_when_shut': [("body.a3d-tier-phone #a3d-shell.collapsed #a3d-rail .a3d-railbtn.active{color:#9aa3ad;background:transparent}", "")],
    'no_viewport_fit': [('content="width=device-width, initial-scale=1, viewport-fit=cover"', 'content="width=device-width, initial-scale=1"')],
    'no_safe_bottom': [("height:calc(58px + env(safe-area-inset-bottom,0px));flex-direction:row;", "height:58px;flex-direction:row;"),
                       ("padding:4px max(6px,env(safe-area-inset-right,0px)) env(safe-area-inset-bottom,0px) max(6px,env(safe-area-inset-left,0px));", "padding:4px 6px 0;")],
    'no_safe_top': [("body.a3d-tier-phone #acad-shell{padding-top:env(safe-area-inset-top,0px);", "body.a3d-tier-phone #acad-shell{")],
    'audit_unclaimed': [("    {sel:'[data-railmore]',why:'on a phone, shows the rail\\'s tools over the tab bar'},   /* __acad3dV149 */\n", "")],
    'no_resize': [("    window.addEventListener('resize',function(){bimShellApplyTier();});\n", "")],
}

name = sys.argv[1]
out = pathlib.Path(sys.argv[2])
txt = base
for old, new in VARIANTS[name]:
    assert txt.count(old) == 1, 'variant %s anchor count %d: %r' % (name, txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
assert '__acad3dV149' in txt
out.write_text(txt, encoding='utf-8')
