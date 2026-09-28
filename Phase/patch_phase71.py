"""
Phase 71 -- make the tool surface domain-scalable.

Disciplines as first-class data, computed dock rows, a command search, and a one-call registration
API so a new engineering domain costs one edit instead of four.

Anchored search-and-replace. Every anchor is asserted to occur EXACTLY ONCE before substitution.
"""
import io, sys, hashlib

PATH = 'canvas_v10.html'
EXPECT_SHA = 'f7ed79782b9ad04f903754ce6ac56fdcd235ab8fadc60fa417e4040a50a280d1'

src = io.open(PATH, encoding='utf-8').read()
raw = io.open(PATH, 'rb').read()
got = hashlib.sha256(raw).hexdigest()
if got != EXPECT_SHA:
    sys.exit('baseline sha mismatch: %s' % got)
print('baseline ok: %d bytes, %s' % (len(raw), got[:16]))

patches = []


def P(name, old, new):
    patches.append((name, old, new))


# ------------------------------------------------------------------ 1. disciplines on the tabs
P('tabs.disc.arch',
  "    {id:'arch',name:'Architecture',panels:[",
  "    {id:'arch',name:'Architecture',disc:'arch',panels:[")

P('tabs.disc.struct',
  "    {id:'struct',name:'Structure',panels:[",
  "    {id:'struct',name:'Structure',disc:'struct',panels:[")

# ------------------------------------------------------------------ 2. registration + lookups
P('code.registry',
  "  function a3drIcon(act){",
  "  /* __acad3dV71: DISCIPLINES, and the extension API that makes a new engineering domain cheap.\n"
  "\n"
  "     The scaling problem this solves, stated as it was measured. Before this phase a command\n"
  "     cost FOUR edits in four places roughly 700 lines apart -- A3DR_ICONS, a tab's panel list,\n"
  "     the a3drLabel literal, and a branch of the 60-case dispatch chain -- and the dock's rows\n"
  "     were a hardcoded [[5 ids],[4 ids]] that nine groups already filled. Adding Bridge,\n"
  "     Mechanical and MEP would have meant 12-15 groups with nowhere to put them, every tool from\n"
  "     every domain on screen at once, and four scattered edits per command.\n"
  "\n"
  "     Three changes fix that, and none of them touches the existing commands:\n"
  "       - a tab may declare a `disc`; the dock shows the ACTIVE discipline's tabs plus the\n"
  "         shared ones, the way Revit's discipline filter works. A domain is data now.\n"
  "       - dock rows are COMPUTED from the group count, so any number of groups lays out.\n"
  "       - a command registered through __a3dRegisterCommand supplies its label, icon and runner\n"
  "         in ONE call. Existing commands keep their four sites; new ones cost one.\n"
  "     The ext maps are consulted FIRST everywhere, so a registered command can also override a\n"
  "     built-in one -- which is what makes a domain plug-in able to specialise, say, Column. */\n"
  "  var A3D_DISCIPLINES=[{id:'arch',name:'Architecture'},{id:'struct',name:'Structure'}];\n"
  "  var A3D_DISC_CUR='arch';\n"
  "  var A3D_CMD_EXT={};   // id -> {label, icon, run, unimpl}\n"
  "  function a3drExt(act){return A3D_CMD_EXT[act]||null;}\n"
  "  function a3drIsUnimpl(act){\n"
  "    var e=a3drExt(act);\n"
  "    if(e&&typeof e.unimpl!=='undefined')return !!e.unimpl;\n"
  "    return !!A3DR_UNIMPL[act];\n"
  "  }\n"
  "  /* A tab belongs to the dock when it declares no discipline (shared: Drafting, Annotate,\n"
  "     Modify, View, Insert, Massing, Manage) or declares the active one. */\n"
  "  function a3drTabInDiscipline(t,disc){return !t.disc||t.disc===(disc||A3D_DISC_CUR);}\n"
  "  function a3drDockTabs(disc){\n"
  "    var out=[],i;\n"
  "    for(i=0;i<A3DR_TABS.length;i++)if(a3drTabInDiscipline(A3DR_TABS[i],disc))out.push(A3DR_TABS[i]);\n"
  "    return out;\n"
  "  }\n"
  "  /* Rows are computed, not listed. Up to five groups per row, balanced so two rows never read\n"
  "     as one long row with a stub under it; more than ten groups simply adds rows. */\n"
  "  function a3drDockRows(tabs){\n"
  "    var n=tabs.length;\n"
  "    if(n<=3)return [tabs.slice()];\n"
  "    var rows=Math.ceil(n/5),per=Math.ceil(n/rows),out=[],i;\n"
  "    for(i=0;i<n;i+=per)out.push(tabs.slice(i,i+per));\n"
  "    return out;\n"
  "  }\n"
  "  function a3drRegisterCommand(spec){\n"
  "    if(!spec||!spec.id)return false;\n"
  "    A3D_CMD_EXT[spec.id]={label:spec.label||spec.id,icon:spec.icon||'',\n"
  "      run:(typeof spec.run==='function')?spec.run:null,unimpl:!!spec.unimpl};\n"
  "    return true;\n"
  "  }\n"
  "  function a3drRegisterDiscipline(spec){\n"
  "    if(!spec||!spec.id)return false;\n"
  "    var i;\n"
  "    for(i=0;i<A3D_DISCIPLINES.length;i++)if(A3D_DISCIPLINES[i].id===spec.id)return false;\n"
  "    A3D_DISCIPLINES.push({id:spec.id,name:spec.name||spec.id});\n"
  "    return true;\n"
  "  }\n"
  "  function a3drRegisterTab(spec){\n"
  "    if(!spec||!spec.id||!spec.panels)return false;\n"
  "    var i;\n"
  "    for(i=0;i<A3DR_TABS.length;i++)if(A3DR_TABS[i].id===spec.id)return false;\n"
  "    A3DR_TABS.push({id:spec.id,name:spec.name||spec.id,disc:spec.disc||null,panels:spec.panels});\n"
  "    return true;\n"
  "  }\n"
  "  function a3drIcon(act){")

P('code.icon.ext',
  "  function a3drIcon(act){\n"
  "    if(act.indexOf('b:')===0)return A3DR_ICONS[act.slice(2)]||'';",
  "  function a3drIcon(act){\n"
  "    var xi=a3drExt(act);\n"
  "    if(xi&&xi.icon)return xi.icon;\n"
  "    if(act.indexOf('b:')===0)return A3DR_ICONS[act.slice(2)]||'';")

P('code.label.ext',
  "  function a3drLabel(act){\n"
  "    var L=",
  "  function a3drLabel(act){\n"
  "    var xl=a3drExt(act);\n"
  "    if(xl&&xl.label)return xl.label;\n"
  "    var L=")

# ------------------------------------------------------------------ 3. dispatch consults ext first
P('dispatch.ext',
  "    var b=t.closest('[data-a3dr]');\n"
  "    if(!b||!A3D.on)return;\n"
  "    var act=b.getAttribute('data-a3dr');",
  "    var b=t.closest('[data-a3dr]');\n"
  "    if(!b||!A3D.on)return;\n"
  "    var act=b.getAttribute('data-a3dr');\n"
  "    /* __acad3dV71: registered commands run first, so a domain pack does not have to reach into\n"
  "       the 60-branch chain below -- and can deliberately override a built-in for its domain. */\n"
  "    var xr=a3drExt(act);\n"
  "    if(xr){\n"
  "      if(xr.unimpl){a3dToast(a3drLabel(act)+' is not implemented yet');return;}\n"
  "      if(xr.run){xr.run(act);return;}\n"
  "    }")

# ------------------------------------------------------------------ 4. dock builds from disciplines
P('dock.rows',
  "  var A3D_DOCK_ROWS=[['arch','struct','a3ddraft','a3dannotate','a3dmodify'],\n"
  "                     ['a3dinsert','a3dview','a3dmassing','a3dmanage']];\n",
  "")

P('dock.unimpl.primary',
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
  "    }",
  "        if(!a3drIsUnimpl(a)&&out.indexOf(a)<0)out.push(a);\n"
  "      }\n"
  "    }\n"
  "    for(i=0;i<tab.panels.length&&out.length<3;i++){\n"
  "      p=tab.panels[i];\n"
  "      if(!p.small)continue;\n"
  "      for(j=0;j<p.small.length&&out.length<3;j++){\n"
  "        a=p.small[j];\n"
  "        if(!a3drIsUnimpl(a)&&out.indexOf(a)<0)out.push(a);\n"
  "      }\n"
  "    }")

P('dock.build',
  "    var h='<div class=\"a3d-dockbody\">',pops='',r,g,tab,prim,i,grps,gi,ai,act;\n"
  "    for(r=0;r<A3D_DOCK_ROWS.length;r++){\n"
  "      h+='<div class=\"a3d-dockrow\">';\n"
  "      for(g=0;g<A3D_DOCK_ROWS[r].length;g++){\n"
  "        tab=a3drTabById(A3D_DOCK_ROWS[r][g]);\n"
  "        prim=a3drTabPrimary(tab);",
  "    var rows=a3drDockRows(a3drDockTabs(A3D_DISC_CUR));\n"
  "    var h='<div class=\"a3d-dockbody\">',pops='',r,g,tab,prim,i,grps,gi,ai,act;\n"
  "    /* The discipline group leads the dock: it is what decides which of the others are here. */\n"
  "    h+='<div class=\"a3d-dockrow a3d-dockhead\">'+\n"
  "      '<div class=\"a3d-dockgrp\" data-dockgrp=\"__disc\">'+\n"
  "      '<select id=\"a3d-discsel\" class=\"a3d-discsel\" title=\"Discipline -- which domain toolset the dock shows\">'+\n"
  "      (function(){var o='',d;for(d=0;d<A3D_DISCIPLINES.length;d++)\n"
  "        o+='<option value=\"'+bimEsc(A3D_DISCIPLINES[d].id)+'\"'+\n"
  "          (A3D_DISCIPLINES[d].id===A3D_DISC_CUR?' selected':'')+'>'+\n"
  "          bimEsc(A3D_DISCIPLINES[d].name)+'</option>';return o;})()+\n"
  "      '</select>'+\n"
  "      '<button class=\"a3d-dbtn\" id=\"a3d-dsearch\" title=\"Find a command (every discipline)\">'+\n"
  "      A3DR_SEARCH_ICON+'</button>'+\n"
  "      '</div></div>';\n"
  "    for(r=0;r<rows.length;r++){\n"
  "      h+='<div class=\"a3d-dockrow\">';\n"
  "      for(g=0;g<rows[r].length;g++){\n"
  "        tab=rows[r][g];\n"
  "        prim=a3drTabPrimary(tab);")

P('dock.build.sep',
  "        if(g<A3D_DOCK_ROWS[r].length-1)h+='<div class=\"a3d-dsep\"></div>';",
  "        if(g<rows[r].length-1)h+='<div class=\"a3d-dsep\"></div>';")

P('dock.build.pop.unimpl',
  "            pops+='<div class=\"a3d-dockitem'+(A3DR_UNIMPL[act]?' a3dr-dis':'')+'\" data-a3dr=\"'+act+'\"'+\n"
  "              (A3DR_UNIMPL[act]?' title=\"Not implemented yet\"':'')+'>'+a3drIcon(act)+\n"
  "              bimEsc(a3drLabel(act))+'</div>';",
  "            pops+='<div class=\"a3d-dockitem'+(a3drIsUnimpl(act)?' a3dr-dis':'')+'\" data-a3dr=\"'+act+'\"'+\n"
  "              (a3drIsUnimpl(act)?' title=\"Not implemented yet\"':'')+'>'+a3drIcon(act)+\n"
  "              bimEsc(a3drLabel(act))+'</div>';")

P('dock.build.search',
  "    host.innerHTML=h+'</div>'+pops;\n"
  "    return true;",
  "    /* __acad3dV71: the command search. At a hundred commands an icon grid still works; at three\n"
  "       hundred it does not, and no amount of grouping saves it. Search spans EVERY discipline,\n"
  "       not just the active one, so filtering the dock by domain never puts a tool out of reach --\n"
  "       which is what lets the discipline filter be aggressive. */\n"
  "    pops+='<div class=\"a3d-dockpop a3d-searchpop\" data-dockpop=\"__search\">'+\n"
  "      '<input type=\"text\" id=\"a3d-dsearchin\" placeholder=\"Find a command\">'+\n"
  "      '<div id=\"a3d-dsearchres\"></div></div>';\n"
  "    host.innerHTML=h+'</div>'+pops;\n"
  "    bimRenderDockSearch('');\n"
  "    return true;")

# ------------------------------------------------------------------ 5. search index + render
P('code.search',
  "  function bimCloseDockPops(){",
  "  var A3DR_SEARCH_ICON=ric('<circle cx=\"11\" cy=\"11\" r=\"6\"/><path d=\"M16 16l4 4\"/>');\n"
  "  /* Every action in every tab, with the tab and panel it came from so a result can say where it\n"
  "     lives. Rebuilt per query rather than cached: A3DR_TABS is extensible at runtime through\n"
  "     a3drRegisterTab, and a stale index is a tool that cannot be found. */\n"
  "  function a3drAllCommands(){\n"
  "    var out=[],seen={},i,j,k,t,p,a;\n"
  "    for(i=0;i<A3DR_TABS.length;i++){\n"
  "      t=A3DR_TABS[i];\n"
  "      for(j=0;j<t.panels.length;j++){\n"
  "        p=t.panels[j];\n"
  "        if(p.big)for(k=0;k<p.big.length;k++){\n"
  "          a=a3drActOf(p.big[k]);\n"
  "          if(!seen[a]){seen[a]=1;out.push({act:a,tab:t,panel:p.t});}\n"
  "          if(p.big[k].menu){var m;for(m=0;m<p.big[k].menu.length;m++){\n"
  "            a=p.big[k].menu[m][0];\n"
  "            if(!seen[a]){seen[a]=1;out.push({act:a,tab:t,panel:p.t});}\n"
  "          }}\n"
  "        }\n"
  "        if(p.small)for(k=0;k<p.small.length;k++){\n"
  "          a=p.small[k];\n"
  "          if(!seen[a]){seen[a]=1;out.push({act:a,tab:t,panel:p.t});}\n"
  "        }\n"
  "      }\n"
  "    }\n"
  "    return out;\n"
  "  }\n"
  "  function bimRenderDockSearch(q){\n"
  "    var res=document.getElementById('a3d-dsearchres');\n"
  "    if(!res)return 0;\n"
  "    var all=a3drAllCommands(),needle=String(q||'').trim().toLowerCase(),h='',n=0,i,c,lbl;\n"
  "    for(i=0;i<all.length;i++){\n"
  "      c=all[i];lbl=a3drLabel(c.act);\n"
  "      if(needle&&(lbl+' '+c.tab.name+' '+c.panel).toLowerCase().indexOf(needle)<0)continue;\n"
  "      n++;\n"
  "      if(n>40)continue;\n"
  "      h+='<div class=\"a3d-dockitem'+(a3drIsUnimpl(c.act)?' a3dr-dis':'')+'\" data-a3dr=\"'+c.act+'\">'+\n"
  "        a3drIcon(c.act)+'<span>'+bimEsc(lbl)+'</span>'+\n"
  "        '<span class=\"a3d-dockwhere\">'+bimEsc(c.tab.name)+'</span></div>';\n"
  "    }\n"
  "    if(!n)h='<div class=\"a3d-dockpoph\">No command matches</div>';\n"
  "    else if(n>40)h+='<div class=\"a3d-dockpoph\">'+(n-40)+' more -- keep typing</div>';\n"
  "    res.innerHTML=h;\n"
  "    return n;\n"
  "  }\n"
  "  function bimCloseDockPops(){")

# ------------------------------------------------------------------ 6. bind search + discipline
P('bind.search',
  "      /* Any other click inside the dock is a command; the document dispatcher runs it, and the\n"
  "         popover closes so the drawing is not left behind a menu. */\n"
  "      bimCloseDockPops();",
  "      var sbtn=ev.target&&ev.target.closest?ev.target.closest('#a3d-dsearch'):null;\n"
  "      if(sbtn){\n"
  "        ev.stopPropagation();\n"
  "        var sp=host.querySelector('[data-dockpop=\"__search\"]');\n"
  "        var sOpen=sp&&sp.classList.contains('open');\n"
  "        bimCloseDockPops();\n"
  "        if(sp&&!sOpen){\n"
  "          sp.classList.add('open');\n"
  "          var sr=sbtn.getBoundingClientRect(),spr=sp.getBoundingClientRect();\n"
  "          var stop=sr.top-spr.height-6;\n"
  "          if(stop<8)stop=Math.min(sr.bottom+6,window.innerHeight-spr.height-8);\n"
  "          var sleft=sr.left+sr.width/2-spr.width/2;\n"
  "          if(sleft<8)sleft=8;\n"
  "          if(sleft+spr.width>window.innerWidth-8)sleft=Math.max(8,window.innerWidth-spr.width-8);\n"
  "          sp.style.top=Math.round(Math.max(8,stop))+'px';\n"
  "          sp.style.left=Math.round(sleft)+'px';\n"
  "          var si=document.getElementById('a3d-dsearchin');\n"
  "          if(si){si.value='';bimRenderDockSearch('');si.focus();}\n"
  "        }\n"
  "        return;\n"
  "      }\n"
  "      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-dsearchin'))return;\n"
  "      /* Any other click inside the dock is a command; the document dispatcher runs it, and the\n"
  "         popover closes so the drawing is not left behind a menu. */\n"
  "      bimCloseDockPops();")

P('bind.input',
  "    window.addEventListener('resize',bimCloseDockPops);",
  "    host.addEventListener('input',function(ev){\n"
  "      if(ev.target&&ev.target.id==='a3d-dsearchin')bimRenderDockSearch(ev.target.value);\n"
  "    });\n"
  "    host.addEventListener('change',function(ev){\n"
  "      if(ev.target&&ev.target.id==='a3d-discsel'){\n"
  "        A3D_DISC_CUR=ev.target.value;\n"
  "        bimBuildDock();\n"
  "        a3dToast('Discipline: '+ev.target.options[ev.target.selectedIndex].text);\n"
  "      }\n"
  "    });\n"
  "    window.addEventListener('resize',bimCloseDockPops);")

# ------------------------------------------------------------------ 7. CSS
P('css.search',
  "    '.a3d-dockitem svg{width:15px;height:15px;flex:0 0 auto;color:#9aa3ad}'+",
  "    '.a3d-dockitem svg{width:15px;height:15px;flex:0 0 auto;color:#9aa3ad}'+\n"
  "    '.a3d-dockhead{padding-bottom:2px;border-bottom:1px solid #30353c;margin-bottom:2px}'+\n"
  "    '.a3d-discsel{background:#1c2024;border:1px solid #3a4048;color:#dfe4ea;border-radius:5px;"
  "font-size:11px;padding:3px 6px;font-family:inherit;max-width:150px}'+\n"
  "    '.a3d-searchpop{min-width:290px;padding:7px}'+\n"
  "    '#a3d-dsearchin{width:100%;box-sizing:border-box;background:#1c2024;border:1px solid #3a4048;"
  "color:#dfe4ea;border-radius:5px;padding:6px 8px;font-size:12px;font-family:inherit;margin-bottom:5px}'+\n"
  "    '#a3d-dsearchres{max-height:46vh;overflow:auto}'+\n"
  "    '.a3d-dockwhere{margin-left:auto;padding-left:12px;color:#7f858c;font-size:10px}'+")

# ------------------------------------------------------------------ apply
out = src
for name, old, new in patches:
    n = out.count(old)
    if n != 1:
        sys.exit('ANCHOR %s matched %d times (need exactly 1)' % (name, n))
    out = out.replace(old, new, 1)
    print('  applied %-22s (%+d chars)' % (name, len(new) - len(old)))

assert 'A3D_DOCK_ROWS' not in out, 'the hardcoded row layout survives'
assert out.count('a3drRegisterCommand') >= 1
io.open(PATH, 'w', encoding='utf-8').write(out)
nraw = io.open(PATH, 'rb').read()
print('\nwrote %d bytes (%+d)' % (len(nraw), len(nraw) - len(raw)))
print('sha256 %s' % hashlib.sha256(nraw).hexdigest())
