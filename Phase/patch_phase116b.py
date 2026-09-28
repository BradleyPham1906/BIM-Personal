"""patch_phase116b.py -- V116 Model and layout tabs, part 2: AutoCAD's layout tabs at the left of the
status bar -- Model, one tab per sheet, and + for a new one -- drawn from the project's sheets on every
refresh, so they cannot disagree with the Project Browser. Double-click renames, right-click offers
what AutoCAD's tab menu offers that this app really does. The status bar's PAPER / MODEL button shows
and switches which space a sheet is being worked in."""
NAME = 'patch_phase116b.py'
BASE = 'a82d2612fe304a930f8b99077a80340c33cc22cc4bf0c5af7a8239425b5c588d'
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
# ---- 1. markup and style ----------------------------------------------------------------------------------
rep("      '<span id=\"a3d-sthint\" class=\"a3d-sthint\"></span>'+\n      '<span class=\"a3d-stspring\"></span>'+\n",
    "      '<span id=\"a3d-laytabs\" class=\"a3d-laytabs\"></span>'+   /* __acad3dV116: Model and layout tabs */\n"
    "      '<span id=\"a3d-sthint\" class=\"a3d-sthint\"></span>'+\n      '<span class=\"a3d-stspring\"></span>'+\n"
    "      '<button class=\"a3d-stbtn a3d-stspace\" id=\"a3d-stspace\" title=\"Paper space or model space on this sheet (MSPACE / PSPACE)\">PAPER</button>'+\n")
rep("    '.a3d-sheetview.open{display:flex}'+\n",
    "    '.a3d-sheetview.open{display:flex}'+\n"
    "    /* __acad3dV116: the layout tabs, the space button, and the menus they open */\n"
    "    '.a3d-laytabs{display:flex;align-items:stretch;align-self:stretch;flex:0 1 auto;min-width:0;overflow:hidden;margin-left:-10px;border-right:1px solid #101214}'+\n"
    "    '.a3d-lt{flex:0 1 auto;min-width:0;max-width:180px;background:transparent;border:0;border-right:1px solid #101214;color:#a9abae;padding:0 12px;font:inherit;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'+\n"
    "    '.a3d-lt:hover{background:#2a2e33;color:#e6e8ea}'+\n"
    "    '.a3d-lt.on{background:#2e3339;color:#fff;box-shadow:inset 0 2px 0 #4ea1ff}'+\n"
    "    '.a3d-lt.a3d-ltplus{flex:0 0 auto;padding:0 10px;font-size:13px}'+\n"
    "    '.a3d-ltin{width:140px;background:#15171a;border:1px solid #4ea1ff;color:#fff;font:inherit;padding:1px 4px;margin:3px 6px;border-radius:3px}'+\n"
    "    '.a3d-stspace{display:none;font-weight:700;letter-spacing:.4px}'+\n"
    "    '.a3d-stspace.show{display:inline-flex}'+\n"
    "    '.a3d-ltmenu{position:fixed;z-index:9990;min-width:176px;background:#22262b;border:1px solid #3a4048;border-radius:5px;padding:4px;box-shadow:0 8px 24px rgba(0,0,0,.45);font:12px/1.2 \"Segoe UI\",Inter,system-ui,sans-serif}'+\n"
    "    '.a3d-ltmenu button{display:block;width:100%;text-align:left;background:transparent;border:0;color:#dfe4ea;padding:6px 10px;border-radius:3px;font:inherit;cursor:pointer}'+\n"
    "    '.a3d-ltmenu button:hover{background:#2f3540}'+\n"
    "    '.a3d-ltmenu button.a3d-ltdanger{color:#ffb4b4}'+\n"
    "    '.a3d-ltmenu hr{border:0;border-top:1px solid #353b44;margin:4px 2px}'+\n")

# ---- 2. drawing the strip ---------------------------------------------------------------------------------------
rep("  function refreshBrowser(){\n    if(!el.browser)return;\n",
    r'''  /* ================= __acad3dV116: Model and layout tabs =================
     AutoCAD's tabs at the left of the status bar: Model, then one tab per sheet, then + for a new
     one. Drawn from A3D.sheets on every refresh -- the same list the Project Browser's Sheets group
     reads -- so the two cannot disagree. The canvas-era strip this replaces kept its own list of
     "layouts" in localStorage and drew whiteboard wires on them; it was never shown in this app. */
  var A3D_LT_EDITING=false,A3D_LT_HTML='';
  function bimLayoutTabsHtml(){
    var onSheet=bimSheetOnScreen(),i,s;
    var h='<button class="a3d-lt'+(onSheet?'':' on')+'" data-lt="model" title="Model space">Model</button>';
    for(i=0;i<A3D.sheets.length;i++){
      s=A3D.sheets[i];
      h+='<button class="a3d-lt'+(onSheet&&s.id===A3D.activeSheetId?' on':'')+'" data-lt="sheet" data-ltsheet="'+bimEsc(s.id)+'" '+
        'title="'+bimEsc(bimSheetLabel(s))+' -- double-click to rename, right-click for more">'+bimEsc(bimSheetLabel(s))+'</button>';
    }
    return h+'<button class="a3d-lt a3d-ltplus" data-lt="new" title="New sheet">+</button>';
  }
  function bimRenderLayoutTabs(){
    var box=document.getElementById('a3d-laytabs');
    if(box&&!A3D_LT_EDITING){
      var h=bimLayoutTabsHtml();
      if(h!==A3D_LT_HTML||box.innerHTML===''){box.innerHTML=h;A3D_LT_HTML=h;}
    }
    var sp=document.getElementById('a3d-stspace');
    if(sp){
      var onSheet=bimSheetOnScreen();
      sp.classList.toggle('show',onSheet);
      sp.textContent=A3D.sheetActiveVp?'MODEL':'PAPER';
      sp.classList.toggle('on',!!A3D.sheetActiveVp);
    }
    /* a sheet renamed while it is open renames the view it is */
    if(A3D_VIEW.kind==='sheet'){
      var nm=bimViewLabelFor('sheet',A3D_VIEW.id);
      if(nm!==A3D_VIEW.name){A3D_VIEW.name=nm;bimSyncViewLabel();refreshHud();}
    }
  }
  function bimLayoutNew(){
    var s=bimAddSheet(bimNextSheetNumber(),'Untitled','ANSI-B');
    if(!s)return null;
    bimActivateView('sheet',s.id);
    a3dToast('New sheet '+bimSheetLabel(s));
    return s.id;
  }
  function bimLayoutRename(id){
    var sh=bimSheetById(id),box=document.getElementById('a3d-laytabs');
    if(!sh||!box)return false;
    var tab=box.querySelector('[data-ltsheet="'+id+'"]');
    if(!tab)return false;
    A3D_LT_EDITING=true;
    var inp=document.createElement('input');
    inp.className='a3d-ltin';inp.value=sh.name||'';inp.setAttribute('data-ltrename',id);
    tab.style.display='none';tab.parentNode.insertBefore(inp,tab);   /* an input may not sit inside a button */
    var done=false;
    function finish(keep){
      if(done)return;done=true;
      A3D_LT_EDITING=false;
      var v=String(inp.value).trim();
      if(keep&&v&&v!==sh.name&&bimSheetById(id)){
        pushUndo();
        sh.name=v;
        refreshBrowser();bimSheetViewRefresh();saveSoon();
      }
      A3D_LT_HTML='';bimRenderLayoutTabs();
    }
    inp.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();finish(true);}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();finish(false);}
    });
    inp.addEventListener('blur',function(){finish(true);});
    inp.addEventListener('click',function(ev){ev.stopPropagation();});
    inp.focus();inp.select();
    return true;
  }
  function bimLtMenuClose(){
    var m=document.getElementById('a3d-ltmenu');
    if(m&&m.parentNode)m.parentNode.removeChild(m);
  }
  /* items: [label, act, danger] or '-' for a rule */
  function bimLtMenuOpen(x,y,items,handler){
    bimLtMenuClose();
    var m=document.createElement('div'),h='',i;
    m.id='a3d-ltmenu';m.className='a3d-ltmenu';
    for(i=0;i<items.length;i++){
      if(items[i]==='-'){h+='<hr>';continue;}
      h+='<button data-ltm="'+items[i][1]+'"'+(items[i][2]?' class="a3d-ltdanger"':'')+'>'+bimEsc(items[i][0])+'</button>';
    }
    m.innerHTML=h;
    document.body.appendChild(m);
    var r=m.getBoundingClientRect();
    m.style.left=Math.max(4,Math.min(x,window.innerWidth-r.width-4))+'px';
    m.style.top=Math.max(4,Math.min(y,window.innerHeight-r.height-4))+'px';
    m.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-ltm]'):null;
      if(!b)return;
      bimLtMenuClose();
      try{handler(b.getAttribute('data-ltm'));}
      catch(eM){console.warn('[BIM] A layout menu action failed',eM);a3dToast('That did not work: '+(eM&&eM.message?eM.message:eM));}
    });
    return m;
  }
  function bimLayoutTabMenu(ev,tab){
    var kind=tab.getAttribute('data-lt'),id=tab.getAttribute('data-ltsheet');
    if(kind!=='sheet'){
      bimLtMenuOpen(ev.clientX,ev.clientY,[['New sheet','new']],function(a){if(a==='new')bimLayoutNew();});
      return;
    }
    bimLtMenuOpen(ev.clientX,ev.clientY,[['New sheet','new'],['Rename','rename'],['Delete','del',true],'-',
      ['Sheet setup…','setup'],['Plot…','plot']],function(a){
      if(a==='new')bimLayoutNew();
      else if(a==='rename')bimLayoutRename(id);
      else if(a==='del')bimConfirmDeleteSheet(id);
      else if(a==='setup'){if(bimActivateView('sheet',id))bimOpenSheetPropsDlg();}
      else if(a==='plot'){if(bimActivateView('sheet',id))bimPrintSheet();}
    });
  }
  function refreshBrowser(){
    bimRenderLayoutTabs();   /* __acad3dV116 */
    if(!el.browser)return;
''')
rep("  function bimSyncStatusBar(){\n    bimSyncStatusHint();\n    bimSyncStatusLevel();\n  }\n",
    "  function bimSyncStatusBar(){\n    bimSyncStatusHint();\n    bimSyncStatusLevel();\n    bimRenderLayoutTabs();   /* __acad3dV116 */\n  }\n")
rep("    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(sheet);   /* __acad3dV116 */\n",
    "    if(el.sheetnum)el.sheetnum.textContent=bimSheetLabel(sheet);   /* __acad3dV116 */\n    bimRenderLayoutTabs();\n")
rep("  function bimCloseSheetView(){\n    if(el.sheetview)el.sheetview.classList.remove('open');\n    A3D.sheetSelVp=null;A3D.sheetDrag=null;\n  }\n",
    "  function bimCloseSheetView(){\n    if(el.sheetview)el.sheetview.classList.remove('open');\n    A3D.sheetSelVp=null;A3D.sheetDrag=null;A3D.sheetActiveVp=null;   /* __acad3dV116 */\n    bimRenderLayoutTabs();\n  }\n")

# ---- 3. wiring ------------------------------------------------------------------------------------------------
rep("    el.sthint=root.querySelector('#a3d-sthint');\n",
    r'''    /* __acad3dV116: the layout tabs and the space button */
    var ltBox=root.querySelector('#a3d-laytabs');
    if(ltBox){
      ltBox.addEventListener('click',function(ev){
        var tab=ev.target&&ev.target.closest?ev.target.closest('[data-lt]'):null;
        if(!tab||A3D_LT_EDITING)return;
        var k=tab.getAttribute('data-lt');
        if(k==='model')bimShowModel();
        else if(k==='new')bimLayoutNew();
        else if(k==='sheet')bimActivateView('sheet',tab.getAttribute('data-ltsheet'));
      });
      ltBox.addEventListener('dblclick',function(ev){
        var tab=ev.target&&ev.target.closest?ev.target.closest('[data-lt="sheet"]'):null;
        if(tab&&!A3D_LT_EDITING){ev.preventDefault();bimLayoutRename(tab.getAttribute('data-ltsheet'));}
      });
      ltBox.addEventListener('contextmenu',function(ev){
        var tab=ev.target&&ev.target.closest?ev.target.closest('[data-lt]'):null;
        if(!tab)return;
        ev.preventDefault();
        bimLayoutTabMenu(ev,tab);
      });
    }
    var spBtn=root.querySelector('#a3d-stspace');
    if(spBtn)spBtn.addEventListener('click',function(){
      if(A3D.sheetActiveVp)bimSetPaperSpace();else bimSetModelSpace(null);
    });
    document.addEventListener('pointerdown',function(ev){
      var m=document.getElementById('a3d-ltmenu');
      if(m&&!(ev.target&&ev.target.closest&&ev.target.closest('#a3d-ltmenu')))bimLtMenuClose();
    },true);
    el.sthint=root.querySelector('#a3d-sthint');
''')

# ---- 4. commands -----------------------------------------------------------------------------------------------
rep("    saveJson:function(){bimExportProjectFile();},\n",
    "    saveJson:function(){bimExportProjectFile();},\n"
    "    newSheet:function(){bimLayoutNew();},          /* __acad3dV116: LAYOUT */\n"
    "    modelTab:function(){bimShowModel();},          /* __acad3dV116: MODEL */\n"
    "    mspace:function(){bimSetModelSpace(null);},    /* __acad3dV116: MSPACE */\n"
    "    pspace:function(){if(!bimSetPaperSpace()&&!bimSheetOnScreen())a3dToast('PSPACE works on a sheet: open one from the layout tabs');},   /* __acad3dV116 */\n")

# ---- 5. the HUD names the sheet on screen, and sheets come in landscape too ------------------------------------------
rep("  function refreshHud(){\n    if(el.view)el.view.textContent=A3D.view;\n",
    "  function refreshHud(){\n"
    "    if(el.view)el.view.textContent=(A3D_VIEW.kind==='sheet'&&bimSheetOnScreen())?A3D_VIEW.name:A3D.view;   /* __acad3dV116: on paper the view is the sheet */\n")
rep("    'ANSI-B':{label:'ANSI B / Tabloid (11x17 in)',w:279.4,h:431.8},\n",
    "    'ANSI-B':{label:'ANSI B / Tabloid (11x17 in)',w:279.4,h:431.8},\n"
    "    /* __acad3dV116: every size here was portrait, and drawing sheets are landscape -- the way an\n"
    "       AutoCAD page setup and a Revit title block lay them out. The portrait sizes stay for the\n"
    "       sheets already made with them. */\n"
    "    'ANSI-B-L':{label:'ANSI B landscape (17x11 in)',w:431.8,h:279.4},\n"
    "    'ANSI-D-L':{label:'ANSI D landscape (36x24 in)',w:914.4,h:609.6},\n"
    "    'A3-L':{label:'A3 landscape (420x297 mm)',w:420,h:297},\n"
    "    'A1-L':{label:'A1 landscape (841x594 mm)',w:841,h:594},\n")
rep("  var SHEET_SCALES=[\n",
    "  var SHEET_NEW_SIZE='ANSI-B-L';   /* __acad3dV116: what + and New Sheet start from */\n  var SHEET_SCALES=[\n")
rep("(k==='ANSI-B'?' selected':'')", "(k===SHEET_NEW_SIZE?' selected':'')")
rep("    var s=bimAddSheet(bimNextSheetNumber(),'Untitled','ANSI-B');\n",
    "    var s=bimAddSheet(bimNextSheetNumber(),'Untitled',SHEET_NEW_SIZE);\n")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
