"""patch_phase120c.py -- V120: the hidden ribbon.

The top of the window was built as an AutoCAD-style ribbon: a quick-access bar, a tab strip, a
panel row and the project tabs. Since V70 the BIM workspace hid the tab strip and the panel row on
entry, because the floating tool dock replaced them, and nothing has shown them since. They were
still built and kept current:

  - the shell's own ribbon definition, whose Insert tab offered the whiteboard's Card, Sticky,
    Group, Table, Chart, Board, Image and Upload and whose Arrange tab ordered whiteboard nodes,
    rendered into the hidden panel row at startup;
  - a timer that every 350 ms asked window.__draftActiveTool, which nothing has defined since the
    whiteboard went in V113c, which tool to highlight in that hidden row;
  - the engine's copy of every BIM tab (installA3dTab, renderA3dPanels, the tab click handler and
    the panel dropdowns), re-rendered into the hidden row on every tab switch;
  - the workspace tab sets (acadApplyWorkspace), which showed and hid buttons in the hidden strip
    on every view change, and a migration for a 'canvas' workspace value that nothing can store.

All of that goes. What stays is what is on screen: the quick-access bar and the project tabs. The
height contract --acad-ribbon-h was 182 px (28 bar + 26 tabs + 104 panels + 24 project tabs) with
body.a3d-mode overriding it to 52 once the workspace was entered; it is 52 px from the start now
(44 in the compact tier), the value every surface has actually been positioned against. The tool
dock's failure message no longer promises a ribbon to fall back on: it points to the command
palette, which runs every command without the dock."""
NAME = 'patch_phase120c.py'
BASE = 'f00b05e24715b4ea7a18465cde33fa76b579fe3a46879e6b03e20d4a4e91904a'
import re
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    """Non-ASCII in inserted text becomes a \\uXXXX escape, by code rather than by care (V103)."""
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


def after_line(head, new):
    """Insert new text after the whole line that starts with head (head must be unique)."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: %d occurrences, expected 1: %r' % (c, head[:90]))
    e = t.index('\n', t.index(head)) + 1
    t = t[:e] + esc(new) + t[e:]


def span(head, tail, new, lines):
    """Replace from the start of head up to (not including) the first tail after it. The span may
    hold non-ASCII that cannot be retyped, so it is found by its ends; head must be unique, and the
    number of lines removed must be exactly what was measured, so a tail that matched somewhere
    unexpected cannot quietly take the wrong amount."""
    global t
    c = t.count(head)
    if c != 1:
        sys.exit('ABORT: span head %d occurrences, expected 1: %r' % (c, head[:90]))
    s = t.index(head)
    e = t.find(tail, s + len(head))
    if e < 0:
        sys.exit('ABORT: span tail not found after head: %r' % tail[:90])
    got = t[s:e].count('\n')
    if got != lines:
        sys.exit('ABORT: span covers %d lines, expected %d: %r' % (got, lines, head[:60]))
    t = t[:s] + esc(new) + t[e:]
# ---- 1. the top bar: the quick-access buttons and the project tab host
TB_HEAD = '(function acadRibbonUI(){'
s = t.index(TB_HEAD)
e = t.index('\n</script>', s)
old = t[s:e]
icons = {}
for k in ('saveJson', 'openJson', 'undo', 'redo', 'print'):
    m = re.findall(r"\n    %s:'(<svg[^']*</svg>)'" % k, old)
    if len(m) != 1:
        sys.exit('ABORT: icon %s found %d times' % (k, len(m)))
    icons[k] = m[0]
for gone in ('card', 'sticky', 'table', 'chart', 'board', 'image', 'upload'):
    if len(re.findall(r"\n    %s:'<svg" % gone, old)) != 1:
        sys.exit('ABORT: whiteboard icon %s not found once' % gone)
if old.count('var TABS=[') != 1 or old.count('window.__draftActiveTool') != 2:
    sys.exit('ABORT: the ribbon definition or the timer is not where it was measured')
new = """(function acadTopBar(){
  /* __acad3dV120: the top bar -- the quick-access buttons, and the host for the project tabs that
     the project section below fills. Each button runs its command through the BIM engine. */
  try{
    var QAT=[
      ['saveJson','Save','""" + icons['saveJson'] + """'],
      ['openJson','Open','""" + icons['openJson'] + """'],
      '|',
      ['undo','Undo','""" + icons['undo'] + """'],
      ['redo','Redo','""" + icons['redo'] + """'],
      '|',
      ['print','Plot','""" + icons['print'] + """']
    ];
    var dispatch=function(act){
      if(window.__a3dCmdSupported&&window.__a3dCmdSupported(act)){window.__a3dRunCmd(act);return;}
      console.warn('[BIM] No command runs the act '+act);
      if(window.__a3dToast)window.__a3dToast('That command is not available');
    };
    var shell=document.createElement('div');shell.id='acad-shell';
    var qat=document.createElement('div');qat.id='acad-qat';
    qat.innerHTML='<div class="acad-logo" title="CAD/BIM workspace">A</div>'+QAT.map(function(q){
      if(q==='|')return '<div class="acad-qsep"></div>';
      return '<button class="acad-qbtn" data-acad-act="'+q[0]+'" title="'+q[1]+'">'+q[2]+'</button>';
    }).join('')+'<div class="acad-spring"></div>';
    shell.appendChild(qat);
    var dt=document.createElement('div');dt.id='acad-doctabs';
    shell.appendChild(dt);
    shell.addEventListener('click',function(e){
      var ab=e.target.closest('[data-acad-act]');
      if(ab)dispatch(ab.getAttribute('data-acad-act'));
    });
    document.body.appendChild(shell);
    document.body.classList.add('acad-on');
  }catch(err){
    console.warn('[BIM] The top bar could not be built.',err);
    setTimeout(function(){if(window.__a3dToast)window.__a3dToast('The top bar could not be built; reload the page');},1500);
  }
})();"""
t = t[:s] + new + t[e:]

# ---- 2. the height contract: the bar and the project tabs, from the start
rep(':root{--acad-ribbon-h:182px}', ':root{--acad-ribbon-h:52px}')
rep('  :root{--acad-ribbon-h:136px}\n', '  :root{--acad-ribbon-h:44px}\n')
rep('  :root{--acad-ribbon-h:160px}\n', '')
rep('body.a3d-mode{--acad-ribbon-h:52px}\n@media(max-width:720px),(max-height:500px){\n  /* compact tier: 22 QAT + 22 doctabs */\n  body.a3d-mode{--acad-ribbon-h:44px}\n}\n@media(min-width:721px) and (max-width:1024px) and (min-height:501px){\n  /* tablet tier keeps the desktop QAT and doctab heights */\n  body.a3d-mode{--acad-ribbon-h:52px}\n}\n', '')

# ---- 3. the engine's copy of the ribbon
rep("""  function chunk3(arr){
    var out=[],i;
    for(i=0;i<arr.length;i+=3)out.push(arr.slice(i,i+3));
    return out;
  }
  var A3DR_ACTIVE_TAB='arch';
  function a3drTabById(id){
    var i;
    for(i=0;i<A3DR_TABS.length;i++)if(A3DR_TABS[i].id===id)return A3DR_TABS[i];
    return A3DR_TABS[0];
  }
""", '')
span('  function renderA3dPanels(tabId){', "  document.addEventListener('click',function(ev){\n    var t=ev.target;", '', 129)
rep("""    var tab=t.closest('[data-acad-tab="a3dtools"]');
    if(tab&&A3D.on){
      var tabs=document.querySelectorAll('#acad-tabs .acad-tab'),i;
      for(i=0;i<tabs.length;i++)tabs[i].classList.remove('active');
      tab.classList.add('active');
      renderA3dPanels();
      return;
    }
""", '')
rep('    installA3dTab();\n', '')
rep('    removeA3dTab();\n', '')
rep("""    /* The ribbon FOLLOWS the view. keepActive:true so a tab present in both tool sets stays
       put: the ribbon changes only when the new view makes the current tab unavailable, which
       is far less jarring than resetting to the first tab on every view change. */
    var ws=(kind==='3d'||(kind==='saved'&&sv&&!sv.flat))?'3d':'da';
    window.ACAD_WS_CUR=ws;
    try{if(window.__acadApplyWorkspace)window.__acadApplyWorkspace(ws,{keepActive:true});}
    catch(eW){console.warn('[BIM] The ribbon could not follow the view change.',eW);}
""", """    /* __acad3dV120: 'da' for a plan, a section or a sheet, '3d' for a 3D view -- what a project tab
       falls back to when it opens with no view of its own. */
    window.ACAD_WS_CUR=(kind==='3d'||(kind==='saved'&&sv&&!sv.flat))?'3d':'da';
""")
rep("""console.warn('[BIM] Could not build the tool dock; the ribbon stays as the tool surface.',eDock2);document.body.classList.add('a3d-dock-failed');a3dToast('Tool dock unavailable -- using the ribbon');}""",
    """console.warn('[BIM] Could not build the tool dock.',eDock2);a3dToast('The tool dock could not be built; the command palette (Ctrl+K) still runs every command');}   /* __acad3dV120 */""")

# ---- 4. the boot: what is left of the workspace section
WS2_HEAD = '(function acadWs2V1(){'
s = t.index(WS2_HEAD)
e = t.index('\n</script>', s)
if t[s:e].count('function acadApplyWorkspace(ws,opts){') != 1 or t[s:e].count("window.ACAD_WS_CUR==='canvas'") != 1:
    sys.exit('ABORT: the workspace section is not the one measured')
t = t[:s] + """(function acadBoot(){
  /* __acad3dV120: the boot into the BIM workspace. The engine publishes window.__a3dEnter when it
     has loaded; this waits for it, for about three seconds at most, then opens the plan view. */
  function boot(tries){
    if(typeof window.__a3dEnter!=='function'){
      if(tries>0)setTimeout(function(){boot(tries-1);},120);
      else console.warn('[BIM] The BIM workspace did not load; reload the page to try again.');
      return;
    }
    try{
      window.ACAD_WS_CUR='da';
      window.__a3dEnter();
      if(window.__a3dSetPlanView)window.__a3dSetPlanView();
    }catch(eB){
      console.warn('[BIM] Startup entry into the drafting workspace failed.',eB);
      if(window.__a3dToast)window.__a3dToast('The workspace could not start; reload the page');
    }
  }
  setTimeout(function(){boot(25);},60);
})();""" + t[e:]

for gone in ('renderA3dPanels', '__a3dIsRibbonTab', 'installA3dTab', 'removeA3dTab', '__acadApplyWorkspace',
             '__acadRenderTab', '__draftActiveTool', 'bimBindRibbonDropdowns', 'A3DR_ACTIVE_TAB', 'a3d-dock-failed'):
    if gone in t:
        sys.exit('ABORT: %s is still referenced' % gone)
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
