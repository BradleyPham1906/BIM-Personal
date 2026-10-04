"""patch_phase149a.py -- V149: the shell on a phone and a tablet.

Three layouts, chosen from the screen (re-chosen when it turns or is resized):
- A phone held upright (up to 720 px wide, portrait): the rail is a tab bar along the bottom,
  with a label under each icon and More for the rail's tools (zoom, appearance, snaps, units,
  save image, shortcuts). The left panel is a drawer over the drawing, closed at the start: a tab
  opens it on that tab, the same tab or a tap beside it closes it. The drawing takes the whole
  width.
- A tablet held upright, and a phone on its side: the rail stays down the left, and the panel is
  the same drawer over the drawing, closed at the start; the drawing starts at the rail.
- A computer, and a tablet on its side: as before, the panel beside the drawing.
- The screen's safe areas (a notch, the home bar) are kept clear: viewport-fit=cover, and the top
  bar and the tab bar padded by env(safe-area-inset-*).
- The toolbar's menu button opens and closes the drawer (it opened a tree drawer the shell
  retired in V67), and on a phone gives way to the tab bar."""
NAME = 'patch_phase149a.py'
BASE = 'ffde091c9c18a002bc08518f5f5acdf22d8680859918ff8cdc8bf1222de7d525'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep('<meta name="viewport" content="width=device-width, initial-scale=1" />',
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />')

CSS = r"""
.a3d-tabbody{display:flex;flex-direction:column;min-height:0;flex:1;min-width:242px}
/* __acad3dV149: the shell on a phone and a tablet. body.a3d-tier-overlay: the panel is a drawer
   over the drawing (a tablet upright, a phone either way); body.a3d-tier-phone: and the rail is a
   tab bar along the bottom (a phone upright). */
#a3d-shellscrim{display:none}
.a3d-railmore{display:none}
body.a3d-tier-overlay #a3d-shell{z-index:9640}
body.a3d-tier-overlay #a3d-rail{position:relative;z-index:2}
body.a3d-tier-overlay #a3d-leftpanel{position:fixed;z-index:3;top:var(--a3d-top-h);bottom:0;left:54px;width:min(340px,calc(100vw - 54px - 24px));height:auto;box-shadow:14px 0 40px rgba(0,0,0,.45);transition:transform .18s ease,opacity .16s ease}
body.a3d-tier-overlay #a3d-shell.collapsed #a3d-leftpanel{width:min(340px,calc(100vw - 54px - 24px));transform:translateX(-104%);opacity:0;visibility:hidden;pointer-events:none}
body.a3d-tier-overlay #a3d-shell:not(.collapsed) #a3d-shellscrim{display:block;position:fixed;inset:0;z-index:1;background:rgba(0,0,0,.38);pointer-events:auto}
body.a3d-tier-phone{--a3d-top-h:calc(44px + env(safe-area-inset-top,0px))}
body.a3d-tier-phone #acad-shell{padding-top:env(safe-area-inset-top,0px);padding-left:env(safe-area-inset-left,0px);padding-right:env(safe-area-inset-right,0px)}
body.a3d-tier-phone #acad3d{bottom:calc(58px + env(safe-area-inset-bottom,0px))}
body.a3d-tier-phone #a3d-rail{position:fixed;left:0;right:0;bottom:0;top:auto;width:auto;height:calc(58px + env(safe-area-inset-bottom,0px));flex-direction:row;align-items:flex-start;justify-content:space-around;gap:0;padding:4px max(6px,env(safe-area-inset-right,0px)) env(safe-area-inset-bottom,0px) max(6px,env(safe-area-inset-left,0px));border-right:0;border-top:1px solid rgba(255,255,255,.1);box-sizing:border-box}
body.a3d-tier-phone #a3d-rail .a3d-paneltoggle,body.a3d-tier-phone #a3d-rail .a3d-railspacer{display:none}
body.a3d-tier-phone #a3d-rail .a3d-railbtn,body.a3d-tier-phone #a3d-rail .a3d-railmore{flex:1 1 0;max-width:76px;width:auto;height:50px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;border:0;border-radius:10px;background:transparent;color:#9aa3ad;cursor:pointer;padding:0}
body.a3d-tier-phone #a3d-rail .a3d-railbtn::after,body.a3d-tier-phone #a3d-rail .a3d-railmore::after{content:attr(data-short);font:500 10.5px/1 Inter,system-ui,sans-serif;letter-spacing:0}
body.a3d-tier-phone #a3d-rail .a3d-railbtn svg,body.a3d-tier-phone #a3d-rail .a3d-railmore svg{width:21px;height:21px;stroke:currentColor;fill:none;stroke-width:1.6}
body.a3d-tier-phone #a3d-rail .a3d-railbtn.active,body.a3d-tier-phone #a3d-rail .a3d-railmore.on{color:#fff;background:rgba(255,255,255,.08)}
body.a3d-tier-phone #a3d-shell.collapsed #a3d-rail .a3d-railbtn.active{color:#9aa3ad;background:transparent}   /* shut: no tab is the one showing */
body.a3d-tier-phone #a3d-railutil{display:none}
body.a3d-tier-phone.a3d-railutil-open #a3d-railutil{display:flex;flex-direction:column;gap:4px;position:fixed;right:max(8px,env(safe-area-inset-right,0px));bottom:calc(66px + env(safe-area-inset-bottom,0px));padding:6px;background:#262626;border:1px solid rgba(255,255,255,.12);border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.5)}
body.a3d-tier-phone.a3d-railutil-open #a3d-railutil .a3d-ru{width:44px;height:44px}
body.a3d-tier-phone #a3d-leftpanel{left:0;bottom:calc(58px + env(safe-area-inset-bottom,0px));width:min(360px,88vw);border-radius:0 14px 0 0}
body.a3d-tier-phone #a3d-shell.collapsed #a3d-leftpanel{width:min(360px,88vw)}
body.a3d-tier-phone .a3d-drawerbtn{display:none!important}
body.a3d-tier-phone #a3d-toast{bottom:calc(74px + env(safe-area-inset-bottom,0px))!important}
body.light-theme.a3d-tier-phone #a3d-railutil{background:#f6f6f4;border-color:rgba(0,0,0,.12)}
body.light-theme.a3d-tier-phone #a3d-rail .a3d-railbtn.active,body.light-theme.a3d-tier-phone #a3d-rail .a3d-railmore.on{color:#111;background:rgba(0,0,0,.07)}
@media(pointer:coarse){body.a3d-tier-overlay #a3d-rail .a3d-railbtn,body.a3d-tier-overlay #a3d-rail .a3d-paneltoggle{min-width:44px;min-height:44px}}"""
rep("""
.a3d-tabbody{display:flex;flex-direction:column;min-height:0;flex:1;min-width:242px}""", CSS)

# ---- the rail's markup: a short name for the tab bar, a More button, the scrim
for tab, short in (('layers', 'Layers'), ('presentation', 'Present'), ('assets', 'Assets'), ('analyze', 'Analyze')):
    rep("""'<button type="button" class="a3d-railbtn" data-tab="%s" title=""" % tab,
        """'<button type="button" class="a3d-railbtn" data-tab="%s" data-short="%s" title=""" % (tab, short))
rep("""'<button type="button" class="a3d-railbtn active" data-tab="browser" title=""",
    """'<button type="button" class="a3d-railbtn active" data-tab="browser" data-short="Browser" title=""")
rep("""      '<div class="a3d-railspacer"></div>'+
      '</nav>'+""", """      '<div class="a3d-railspacer"></div>'+
      '<button type="button" class="a3d-railmore" data-railmore="1" data-short="More" title="More: zoom, appearance, snaps, units, save image, shortcuts" aria-label="More" aria-expanded="false">'+   /* __acad3dV149 */
      '<svg viewBox="0 0 18 18"><circle cx="4" cy="9" r="1.3"/><circle cx="9" cy="9" r="1.3"/><circle cx="14" cy="9" r="1.3"/></svg></button>'+
      '</nav>'+
      '<div id="a3d-shellscrim" data-toggle="1" aria-hidden="true"></div>'+""")

# ---- the tiers
rep("""  function bimShellDockW(){
    try{
      var sh=document.getElementById('a3d-shell');
      document.documentElement.style.setProperty('--a3d-left-w',
        (sh&&sh.classList.contains('collapsed'))?'54px':'296px');""", """  /* __acad3dV149: which layout the screen gets -- 'phone' (upright, up to 720 px: a tab bar and a
     drawer), 'overlay' (a tablet upright, a phone on its side: the rail and a drawer), 'desktop' */
  var A3D_SHELL_TIER=null,A3D_SHELL_DESK_SHUT=false;
  function bimShellTier(){
    var mm=window.matchMedia;
    if(!mm)return 'desktop';
    if(mm('(max-width:720px) and (orientation:portrait)').matches)return 'phone';
    if(mm('(max-width:720px),(max-height:500px)').matches||mm('(min-width:721px) and (max-width:1024px) and (orientation:portrait)').matches)return 'overlay';
    return 'desktop';
  }
  function bimShellOverlay(){return A3D_SHELL_TIER==='phone'||A3D_SHELL_TIER==='overlay';}
  /* the layout for the screen now: on the way into a drawer layout the panel closes, and on the way
     back it opens as it was */
  function bimShellApplyTier(){
    var sh=document.getElementById('a3d-shell'),tr=bimShellTier(),was=A3D_SHELL_TIER,b=document.body;
    if(!sh||!b)return tr;
    if(tr!==was){
      if(tr!=='desktop'&&(was==='desktop'||was===null)){A3D_SHELL_DESK_SHUT=sh.classList.contains('collapsed');sh.classList.add('collapsed');}
      else if(tr==='desktop'&&was!==null)sh.classList.toggle('collapsed',A3D_SHELL_DESK_SHUT);
      A3D_SHELL_TIER=tr;
      b.classList.toggle('a3d-tier-phone',tr==='phone');
      b.classList.toggle('a3d-tier-overlay',tr!=='desktop');
      if(tr!=='phone')bimShellMore(false);
    }
    bimShellDockW();
    return tr;
  }
  /* the drawer: open on a tab, or shut; on a computer the panel's own toggle */
  function bimShellDrawer(open,tab){
    var sh=document.getElementById('a3d-shell');
    if(!sh)return false;
    if(open===undefined)open=sh.classList.contains('collapsed');
    if(open){bimShellSetTab(tab||sh.getAttribute('data-tab')||'browser');}
    else{sh.classList.add('collapsed');bimShellDockW();}
    bimShellMore(false);
    return !sh.classList.contains('collapsed');
  }
  /* the phone's More: the rail's tools, over the tab bar */
  function bimShellMore(on){
    var b=document.body,m=document.querySelector('#a3d-rail [data-railmore]');
    if(!b)return false;
    if(on===undefined)on=!b.classList.contains('a3d-railutil-open');
    on=!!on&&A3D_SHELL_TIER==='phone';
    b.classList.toggle('a3d-railutil-open',on);
    if(m){m.classList.toggle('on',on);m.setAttribute('aria-expanded',String(on));}
    return on;
  }
  function bimShellDockW(){
    try{
      var sh=document.getElementById('a3d-shell');
      document.documentElement.style.setProperty('--a3d-left-w',
        A3D_SHELL_TIER==='phone'?'0px':A3D_SHELL_TIER==='overlay'?'54px':   /* __acad3dV149: a drawer leaves the drawing where it is */
        (sh&&sh.classList.contains('collapsed'))?'54px':'296px');""")

rep("""    sh.addEventListener('click',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-toggle]'):null;
      if(tg){sh.classList.toggle('collapsed');bimShellDockW();return;}
      var tb=ev.target&&ev.target.closest?ev.target.closest('.a3d-railbtn[data-tab]'):null;
      if(tb)bimShellSetTab(tb.getAttribute('data-tab'));
    });""", """    sh.addEventListener('click',function(ev){
      var mo=ev.target&&ev.target.closest?ev.target.closest('[data-railmore]'):null;   /* __acad3dV149 */
      if(mo){bimShellMore();return;}
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-toggle]'):null;
      if(tg){sh.classList.toggle('collapsed');bimShellDockW();bimShellMore(false);return;}
      var tb=ev.target&&ev.target.closest?ev.target.closest('.a3d-railbtn[data-tab]'):null;
      if(tb){
        /* __acad3dV149: in a drawer layout the open tab's button shuts the drawer */
        if(bimShellOverlay()&&!sh.classList.contains('collapsed')&&sh.getAttribute('data-tab')===tb.getAttribute('data-tab')){bimShellDrawer(false);return;}
        bimShellSetTab(tb.getAttribute('data-tab'));
        bimShellMore(false);
      }
    });
    /* __acad3dV149: the layout follows the screen; More shuts when something else is touched; Esc
       shuts an open drawer */
    window.addEventListener('resize',function(){bimShellApplyTier();});
    document.addEventListener('pointerdown',function(ev){
      if(!document.body.classList.contains('a3d-railutil-open'))return;
      var x=ev.target;
      if(x&&x.closest&&(x.closest('#a3d-rail')||x.closest('#a3d-rupop')))return;
      bimShellMore(false);
    },true);
    document.addEventListener('keydown',function(ev){
      if(ev.key!=='Escape'||!bimShellOverlay()||sh.classList.contains('collapsed'))return;
      var a=document.activeElement;
      if(a&&(a.tagName==='INPUT'||a.tagName==='TEXTAREA'||a.tagName==='SELECT'))return;
      bimShellDrawer(false);
    });""")
rep("""    bimWirePresPanel(sh.querySelector('#a3d-leftpanel'));     /* __acad3dV122 */
    bimShellDockW();""", """    bimWirePresPanel(sh.querySelector('#a3d-leftpanel'));     /* __acad3dV122 */
    bimShellApplyTier();   /* __acad3dV149: the layout for this screen, and the dock's width */""")

rep("""      if(act==='drawer'){var tr=root.querySelector('.a3d-tree');if(tr)tr.classList.toggle('open');}""",
    """      if(act==='drawer'){if(bimShellOverlay()){bimShellDrawer();return;}var tr=root.querySelector('.a3d-tree');if(tr)tr.classList.toggle('open');}   /* __acad3dV149: the left drawer */""")

rep("""    {sel:'.a3d-panelcollapse',why:'collapses the rail'},""", """    {sel:'.a3d-panelcollapse',why:'collapses the rail'},
    {sel:'[data-railmore]',why:'on a phone, shows the rail\\'s tools over the tab bar'},   /* __acad3dV149 */""")

rep("""      if(shellEl&&shellEl.classList.contains('collapsed')){
        // the panel hosts the BIM navigator, so it opens on entry
        shellEl.classList.remove('collapsed');
      }""", """      if(shellEl&&shellEl.classList.contains('collapsed')&&!bimShellOverlay()){   /* __acad3dV149: a drawer stays shut */
        // the panel hosts the BIM navigator, so it opens on entry
        shellEl.classList.remove('collapsed');
      }""")

rep("""  var BIM_APP_VERSION={v:'V148',date:'2026-10-04'};   /* __acad3dV148 */""",
    """  var BIM_APP_VERSION={v:'V149',date:'2026-10-04'};   /* __acad3dV149 */""")
rep("""  window.__acad3dV148='anzlist,""", """  /* __acad3dV149: the shell on a phone and a tablet */
  window.__a3dShellTier=function(){return {tier:A3D_SHELL_TIER,computed:bimShellTier(),open:!document.getElementById('a3d-shell').classList.contains('collapsed'),
    more:document.body.classList.contains('a3d-railutil-open'),leftW:getComputedStyle(document.documentElement).getPropertyValue('--a3d-left-w').trim()};};
  window.__a3dShellDrawer=function(open,tab){return bimShellDrawer(open,tab);};
  window.__a3dShellMore=function(on){return bimShellMore(on);};
  window.__a3dShellApplyTier=function(){return bimShellApplyTier();};
  window.__acad3dV149='tierphone,tieroverlay,tabbar,tablabels,railmore,leftdrawer,drawerclosed,drawerscrim,tabtoggles,escshuts,fullwidth,safeareas,viewportfit,burgerdrawer,toastclear,tierfollows';
  window.__acad3dV148='anzlist,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
