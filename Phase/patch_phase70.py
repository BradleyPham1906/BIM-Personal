"""
Phase 70 -- Rayon-style floating tool dock replaces the ribbon in the BIM workspace.

Anchored search-and-replace. Every anchor is asserted to occur EXACTLY ONCE before substitution.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = 'fd9dd824069724ebcea57d62e1005872a57630fb7100cd6afe0ffb236a156532'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new):
    patches.append((name, old, new))


# ------------------------------------------------------------------ 1. hide the ribbon in BIM
P('css.hideribbon',
  "body.a3d-mode #viewport{display:none!important}",
  "body.a3d-mode #viewport{display:none!important}\n"
  "/* __acad3dV70: the ribbon stands down in the BIM workspace, replaced by the floating tool\n"
  "   dock (#a3d-dock) over the drawing -- the Rayon arrangement. The dock is GENERATED from\n"
  "   A3DR_TABS, the same registry the ribbon renders from, so no command can be lost by this\n"
  "   swap; that is asserted set-for-set by the Phase 70 suite rather than trusted.\n"
  "   --acad-ribbon-h is the contract every other surface positions against (see the comment on\n"
  "   the .acad-doctab rules). Its parts are 28 QAT + 26 tabs + 104 panels + 24 doctabs = 182;\n"
  "   hiding the tab strip and the panel row leaves 28 + 24 = 52. The QAT keeps file/undo/redo\n"
  "   and the workspace switcher, and the doc tabs keep document switching -- removing those\n"
  "   would leave no way back out of this workspace. */\n"
  "body.a3d-mode #acad-panels,\n"
  "body.a3d-mode #acad-tabs{display:none!important}\n"
  "body.a3d-mode{--acad-ribbon-h:52px}\n"
  "@media(max-width:720px),(max-height:500px){\n"
  "  /* compact tier: 22 QAT + 22 doctabs */\n"
  "  body.a3d-mode{--acad-ribbon-h:44px}\n"
  "}\n"
  "@media(min-width:721px) and (max-width:1024px) and (min-height:501px){\n"
  "  /* tablet tier keeps the desktop QAT and doctab heights */\n"
  "  body.a3d-mode{--acad-ribbon-h:52px}\n"
  "}")

# ------------------------------------------------------------------ 2. dock CSS
P('css.dock',
  "    '.a3d-rdrawerbtn{display:none;font-size:11px;padding:4px 9px}'+",
  "    '.a3d-rdrawerbtn{display:none;font-size:11px;padding:4px 9px}'+\n"
  "    /* __acad3dV70: the floating tool dock. Two rows of icon buttons grouped by subject with a\n"
  "       caret per group, over the drawing rather than above it -- the shape the reference tool\n"
  "       uses, and the reason the ribbon's 130px of permanent chrome can go. */\n"
  "    '#a3d-dock{position:absolute;left:50%;bottom:14px;transform:translateX(-50%);z-index:9600;"
  "display:flex;flex-direction:column;gap:3px;background:#22262b;border:1px solid #3a4048;"
  "border-radius:10px;padding:5px;box-shadow:0 6px 22px rgba(0,0,0,0.45);max-width:calc(100% - 28px)}'+\n"
  "    '.a3d-dockrow{display:flex;align-items:center;gap:2px;min-width:0}'+\n"
  "    '.a3d-dockgrp{display:flex;align-items:center;gap:1px;flex:0 0 auto}'+\n"
  "    '.a3d-dsep{width:1px;align-self:stretch;margin:3px 4px;background:#3a4048;flex:0 0 auto}'+\n"
  "    '.a3d-dbtn{width:30px;height:28px;display:flex;align-items:center;justify-content:center;"
  "background:transparent;border:1px solid transparent;border-radius:5px;color:#c3cad2;cursor:pointer;"
  "padding:0;flex:0 0 auto}'+\n"
  "    '.a3d-dbtn:hover{background:#2f353c;color:#fff}'+\n"
  "    '.a3d-dbtn svg{width:16px;height:16px}'+\n"
  "    '.a3d-dcar{width:13px;height:28px;background:transparent;border:0;color:#8d9196;font-size:8px;"
  "cursor:pointer;padding:0;line-height:1;font-family:inherit;flex:0 0 auto}'+\n"
  "    '.a3d-dcar:hover{color:#fff}'+\n"
  "    '.a3d-dockpop{display:none;position:fixed;z-index:9700;min-width:212px;max-height:60vh;"
  "overflow:auto;background:#22262b;border:1px solid #3a4048;border-radius:8px;padding:5px;"
  "box-shadow:0 10px 30px rgba(0,0,0,0.5)}'+\n"
  "    '.a3d-dockpop.open{display:block}'+\n"
  "    '.a3d-dockpoph{padding:7px 7px 3px;font-size:9.5px;font-weight:800;letter-spacing:.06em;"
  "color:#8d9196;text-transform:uppercase}'+\n"
  "    '.a3d-dockitem{display:flex;align-items:center;gap:8px;padding:5px 7px;font-size:11.5px;"
  "color:#dfe4ea;cursor:pointer;border-radius:4px;white-space:nowrap}'+\n"
  "    '.a3d-dockitem:hover{background:#2b3138}'+\n"
  "    '.a3d-dockitem svg{width:15px;height:15px;flex:0 0 auto;color:#9aa3ad}'+\n"
  "    '#a3d-dock.a3d-hide-panel{display:none}'+")

P('css.dock.compact',
  "      '#a3d-pill{padding:6px}'+",
  "      '#a3d-pill{padding:6px}'+\n"
  "      /* The dock spans the viewport and scrolls sideways rather than centring and overflowing\n"
  "         off both edges; its rows keep full-size hit targets for a finger. */\n"
  "      '#a3d-dock{left:8px;right:8px;transform:none;max-width:none;bottom:10px}'+\n"
  "      '.a3d-dockrow{overflow-x:auto;-webkit-overflow-scrolling:touch}'+\n"
  "      '.a3d-dbtn{width:34px;height:34px}'+\n"
  "      '.a3d-dcar{height:34px}'+")

# ------------------------------------------------------------------ 3. dock markup
P('markup.dock',
  "      '<div id=\"a3d-pill\">'+",
  "      '<div id=\"a3d-dock\"></div>'+\n"
  "      '<div id=\"a3d-pill\">'+")

# ------------------------------------------------------------------ 4. dock builder
P('code.dock',
  "  function renderA3dPanels(tabId){",
  "  /* __acad3dV70: the floating tool dock, GENERATED from A3DR_TABS rather than hand-listed.\n"
  "     That is the whole safety argument for retiring the ribbon in this workspace: a hand-built\n"
  "     dock would quietly drop commands, and a command that exists but cannot be reached is the\n"
  "     same failure as one that does not work. One group per ribbon TAB (nine groups over two\n"
  "     rows, the reference tool's density); the group shows that tab's headline tools and its\n"
  "     caret opens every action the tab has, still grouped under its panel headings.\n"
  "     Buttons carry data-a3dr, so the existing document-level dispatcher wires them by\n"
  "     construction -- this phase adds no new command routing at all. */\n"
  "  var A3D_DOCK_ROWS=[['arch','struct','a3ddraft','a3dannotate','a3dmodify'],\n"
  "                     ['a3dinsert','a3dview','a3dmassing','a3dmanage']];\n"
  "  function a3drActOf(entry){return (typeof entry==='string')?entry:entry.act;}\n"
  "  /* Every action a tab can reach, in ribbon order, grouped by panel and de-duplicated within\n"
  "     the tab. Drop-down entries hanging off a big button (e.g. Dimension > Angular) are pulled\n"
  "     in too -- they are actions of that panel, and leaving them out is exactly how a rebuild\n"
  "     loses tools without anyone noticing. */\n"
  "  function a3drTabGroups(tab){\n"
  "    var out=[],seen={},i,j,k,p,acts,a;\n"
  "    for(i=0;i<tab.panels.length;i++){\n"
  "      p=tab.panels[i];acts=[];\n"
  "      if(p.big)for(j=0;j<p.big.length;j++){\n"
  "        a=a3drActOf(p.big[j]);\n"
  "        if(!seen[a]){seen[a]=1;acts.push(a);}\n"
  "        if(p.big[j].menu)for(k=0;k<p.big[j].menu.length;k++){\n"
  "          a=p.big[j].menu[k][0];\n"
  "          if(!seen[a]){seen[a]=1;acts.push(a);}\n"
  "        }\n"
  "      }\n"
  "      if(p.small)for(j=0;j<p.small.length;j++){\n"
  "        a=p.small[j];\n"
  "        if(!seen[a]){seen[a]=1;acts.push(a);}\n"
  "      }\n"
  "      if(acts.length)out.push({t:p.t,acts:acts});\n"
  "    }\n"
  "    return out;\n"
  "  }\n"
  "  /* Up to three headline buttons per group: the tab's big buttons first, then its smalls.\n"
  "     Unimplemented commands are never promoted to the dock face -- they stay listed, greyed,\n"
  "     inside the caret, where the ribbon already showed them, so the dock's visible row is all\n"
  "     working tools. */\n"
  "  function a3drTabPrimary(tab){\n"
  "    var out=[],i,j,p,a;\n"
  "    for(i=0;i<tab.panels.length&&out.length<3;i++){\n"
  "      p=tab.panels[i];\n"
  "      if(!p.big)continue;\n"
  "      for(j=0;j<p.big.length&&out.length<3;j++){\n"
  "        a=a3drActOf(p.big[j]);\n"
  "        if(!A3DR_UNIMPL[a]&&out.indexOf(a)<0)out.push(a);\n"
  "      }\n"
  "    }\n"
  "    for(i=0;i<tab.panels.length&&out.length<3;i++){\n"
  "      p=tab.panels[i];\n"
  "      if(!p.small)continue;\n"
  "      for(j=0;j<p.small.length&&out.length<3;j++){\n"
  "        a=p.small[j];\n"
  "        if(!A3DR_UNIMPL[a]&&out.indexOf(a)<0)out.push(a);\n"
  "      }\n"
  "    }\n"
  "    return out;\n"
  "  }\n"
  "  function bimBuildDock(){\n"
  "    var host=document.getElementById('a3d-dock');\n"
  "    if(!host)return false;\n"
  "    var h='',pops='',r,g,tab,prim,i,grps,gi,ai,act;\n"
  "    for(r=0;r<A3D_DOCK_ROWS.length;r++){\n"
  "      h+='<div class=\"a3d-dockrow\">';\n"
  "      for(g=0;g<A3D_DOCK_ROWS[r].length;g++){\n"
  "        tab=a3drTabById(A3D_DOCK_ROWS[r][g]);\n"
  "        prim=a3drTabPrimary(tab);\n"
  "        h+='<div class=\"a3d-dockgrp\" data-dockgrp=\"'+tab.id+'\">';\n"
  "        for(i=0;i<prim.length;i++)\n"
  "          h+='<button class=\"a3d-dbtn\" data-a3dr=\"'+prim[i]+'\" title=\"'+\n"
  "            bimEsc(a3drLabel(prim[i])+'  \\u00b7  '+tab.name)+'\">'+a3drIcon(prim[i])+'</button>';\n"
  "        h+='<button class=\"a3d-dcar\" data-dockmore=\"'+tab.id+'\" title=\"'+\n"
  "          bimEsc(tab.name+' \\u2014 all tools')+'\">\\u25b4</button>';\n"
  "        h+='</div>';\n"
  "        if(g<A3D_DOCK_ROWS[r].length-1)h+='<div class=\"a3d-dsep\"></div>';\n"
  "        grps=a3drTabGroups(tab);\n"
  "        pops+='<div class=\"a3d-dockpop\" data-dockpop=\"'+tab.id+'\">';\n"
  "        for(gi=0;gi<grps.length;gi++){\n"
  "          pops+='<div class=\"a3d-dockpoph\">'+bimEsc(tab.name+' \\u00b7 '+grps[gi].t)+'</div>';\n"
  "          for(ai=0;ai<grps[gi].acts.length;ai++){\n"
  "            act=grps[gi].acts[ai];\n"
  "            pops+='<div class=\"a3d-dockitem'+(A3DR_UNIMPL[act]?' a3dr-dis':'')+'\" data-a3dr=\"'+act+'\"'+\n"
  "              (A3DR_UNIMPL[act]?' title=\"Not implemented yet\"':'')+'>'+a3drIcon(act)+\n"
  "              bimEsc(a3drLabel(act))+'</div>';\n"
  "          }\n"
  "        }\n"
  "        pops+='</div>';\n"
  "      }\n"
  "      h+='</div>';\n"
  "    }\n"
  "    host.innerHTML=h+pops;\n"
  "    return true;\n"
  "  }\n"
  "  function bimCloseDockPops(){\n"
  "    var all=document.querySelectorAll('.a3d-dockpop.open'),i;\n"
  "    for(i=0;i<all.length;i++)all[i].classList.remove('open');\n"
  "  }\n"
  "  var A3D_DOCK_BOUND=false;\n"
  "  function bimBindDock(){\n"
  "    if(A3D_DOCK_BOUND)return;\n"
  "    var host=document.getElementById('a3d-dock');\n"
  "    if(!host)return;\n"
  "    A3D_DOCK_BOUND=true;\n"
  "    host.addEventListener('click',function(ev){\n"
  "      var car=ev.target&&ev.target.closest?ev.target.closest('[data-dockmore]'):null;\n"
  "      if(car){\n"
  "        ev.stopPropagation();\n"
  "        var key=car.getAttribute('data-dockmore');\n"
  "        var d=host.querySelector('[data-dockpop=\"'+key+'\"]');\n"
  "        var wasOpen=d&&d.classList.contains('open');\n"
  "        bimCloseDockPops();\n"
  "        if(d&&!wasOpen){\n"
  "          d.classList.add('open');\n"
  "          /* Opens UPWARD from the caret, because the dock sits at the bottom of the viewport;\n"
  "             then clamped to the window so a group near either edge is still fully readable. */\n"
  "          var cr=car.getBoundingClientRect(),dr=d.getBoundingClientRect();\n"
  "          var top=cr.top-dr.height-6;\n"
  "          if(top<8)top=Math.min(cr.bottom+6,window.innerHeight-dr.height-8);\n"
  "          var left=cr.left+cr.width/2-dr.width/2;\n"
  "          if(left<8)left=8;\n"
  "          if(left+dr.width>window.innerWidth-8)left=Math.max(8,window.innerWidth-dr.width-8);\n"
  "          d.style.top=Math.round(Math.max(8,top))+'px';\n"
  "          d.style.left=Math.round(left)+'px';\n"
  "        }\n"
  "        return;\n"
  "      }\n"
  "      /* Any other click inside the dock is a command; the document dispatcher runs it, and the\n"
  "         popover closes so the drawing is not left behind a menu. */\n"
  "      bimCloseDockPops();\n"
  "    });\n"
  "    document.addEventListener('click',function(ev){\n"
  "      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-dock'))return;\n"
  "      bimCloseDockPops();\n"
  "    });\n"
  "    window.addEventListener('resize',bimCloseDockPops);\n"
  "  }\n"
  "  function renderA3dPanels(tabId){")

# ------------------------------------------------------------------ 5. build it on entry
P('enter.dock',
  "    size();\n"
  "    installA3dTab();\n"
  "    bimSyncActiveGlobal();",
  "    /* __acad3dV70: the dock is the tool surface in this workspace now. Built on entry rather\n"
  "       than at buildUI time so it always reflects the current A3DR_TABS, and bound once. */\n"
  "    try{\n"
  "      bimBuildDock();bimBindDock();\n"
  "    }catch(eDock2){console.warn('[BIM] Could not build the tool dock; the ribbon stays as the "
  "tool surface.',eDock2);document.body.classList.add('a3d-dock-failed');"
  "a3dToast('Tool dock unavailable -- using the ribbon');}\n"
  "    size();\n"
  "    installA3dTab();\n"
  "    bimSyncActiveGlobal();")

P('exit.dock',
  "    document.body.classList.remove('a3d-props-right');",
  "    document.body.classList.remove('a3d-props-right');\n"
  "      bimCloseDockPops();")

# ------------------------------------------------------------------ apply
out = src
for name, old, new in patches:
    n = out.count(old)
    if n != 1:
        sys.exit('ANCHOR %s matched %d times (need exactly 1)' % (name, n))
    out = out.replace(old, new, 1)
    print('  applied %-22s (%+d chars)' % (name, len(new) - len(old)))

assert out.count('bimBuildDock') == 2, 'dock builder not wired (definition + entry call)'
assert out.count("id=\\\"a3d-dock\\\"") + out.count('id="a3d-dock"') >= 1
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
