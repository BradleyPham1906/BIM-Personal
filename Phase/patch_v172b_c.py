#!/usr/bin/env python3
"""V172b, patch c: the boards become editable. reference/research-ladybug-weather-comfort.md, 13.

The new files are already in src/: js/engine/sheets/board-figures.js (the catalogue of figures, each board read
for its cards, a board's list laid out in bands), js/engine/sheets/board-edit.js (Edit: drag and size under the
drawing's Snap, Grid and Ortho, the keys, a figure's menu and options, Add a figure, boards of one's own),
css/site-analysis/boards-arranged.css, and js/engine/testing/hooks-boards.js. This patch:
- gives every card of the three boards and Ladybug's its own name ('@clim.temp' in the card's classes), and keeps
  the boards' indicators when a board is read for its figures;
- draws a board through bimBrdHtml: a board with a list of its own, or one of one's own, or Edit;
- opens, prints, presents and thumbnails a board of one's own by its id; its name in the Presentation panel;
- keeps a board's list, its figures taken off, and a board of one's own's name in the set's record;
- gives + Board a New board, and a board's menu Edit and Duplicate;
- after an undo or a redo draws the open board again; the drawing's snaps show in Edit's bar;
- Edit's dialogs carry the board's class (its colours, its charts' rules), and are not the board (bimClbEl).

Run from the repository root: python3 Phase/patch_v172b_c.py
"""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from p171 import begin, rep, done, ROOT   # noqa: E402

begin('80873f52769a7639648175e4e4bb329ba0fe095bfd450266daa9af86204fa664')   # patch b

# ---- the page: the new files in their places ----
rep('index.html', '<!-- @include css/site-analysis/boards.css -->\n',
    '<!-- @include css/site-analysis/boards.css -->\n<!-- @include css/site-analysis/boards-arranged.css -->\n')
rep('index.html', '<!-- @include js/engine/sheets/boards.js -->\n',
    '<!-- @include js/engine/sheets/boards.js -->\n<!-- @include js/engine/sheets/board-figures.js -->\n<!-- @include js/engine/sheets/board-edit.js -->\n')
rep('index.html', '<!-- @include js/engine/testing/hooks-ladybug.js -->\n',
    '<!-- @include js/engine/testing/hooks-ladybug.js -->\n<!-- @include js/engine/testing/hooks-boards.js -->\n')

# ---- Edit's dialogs are boards too (the board's colours and its charts' rules), but not the board ----
rep('js/engine/site-analysis/climate-board.js', "  function bimClbEl(){return document.querySelector('.a3d-clb:not(.a3d-ssboard)');}",
    "  function bimClbEl(){return document.querySelector('.a3d-clb:not(.a3d-ssboard):not(.a3d-clb-dlg)');}   /* __acad3dV172b: not Edit's dialog */")

# ---- the climate board: its cards named, its indicators kept, drawn through bimBrdHtml ----
CB = 'js/engine/site-analysis/climate-board.js'
rep(CB, "    var a=document.activeElement,b=bimClbEl();\n"
        "    if(a&&a!==document.body&&!(b&&b.contains(a))&&(/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)||a.isContentEditable))return false;\n"
        "    if(ev.key==='Escape'){ev.preventDefault();ev.stopImmediatePropagation();bimClbClose();return true;}\n",
    "    var a=document.activeElement,b=bimClbEl(),dl=A3D_BRD.dlg;   /* __acad3dV172b: Edit's dialogs are the board's */\n"
    "    if(a&&a!==document.body&&!(b&&b.contains(a))&&!(dl&&dl.contains(a))&&(/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)||a.isContentEditable))return false;\n"
    "    if(ev.key==='Escape'){ev.preventDefault();ev.stopImmediatePropagation();if(!bimBrdEsc())bimClbClose();return true;}   /* __acad3dV172b: a dialog, then Edit, then the board */\n")
rep(CB, "    if(b.className!==cls)b.className=cls;\n  }\n",
    "    if(b.className!==cls)b.className=cls;\n    bimBrdZoom(b);   /* __acad3dV172b: an arranged board zoomed to the main view */\n  }\n")
rep(CB, "  function bimClbCard(cls,no,title,dek,body,src){\n"
        "    return '<figure class=\"a3d-clb-card '+(Array.isArray(cls)?cls.join(' '):cls)+'\" data-fig=\"'+no+'\"><figcaption>",
    "  function bimClbCard(cls,no,title,dek,body,src){\n"
    "    var C=Array.isArray(cls)?cls.slice():[cls],id='',i;   /* __acad3dV172b: '@name' among the classes names the figure */\n"
    "    for(i=C.length-1;i>=0;i--)if(String(C[i]).charAt(0)==='@'){id=String(C[i]).slice(1);C.splice(i,1);}\n"
    "    if(id)bimFigCapCard(id,C,title,dek,body,src);\n"
    "    return '<figure class=\"a3d-clb-card '+C.join(' ')+'\" data-fig=\"'+no+'\"'+(id?' data-figid=\"'+id+'\"':'')+'><figcaption>")
for old, new in [
        ("cards.push(bimClbCard(['s7','wide'],fig,title,'Monthly mean", "cards.push(bimClbCard(['s7','wide','@clim.temp'],fig,title,'Monthly mean"),
        ("cards.push(bimClbCard('s5',fig,'Prevailing wind from the '", "cards.push(bimClbCard(['s5','@clim.wind'],fig,'Prevailing wind from the '"),
        ("cards.push(bimClbCard(['s12','wide'],fig,'In '+Hh.year+' the air was", "cards.push(bimClbCard(['s12','wide','@clim.heat'],fig,'In '+Hh.year+' the air was"),
        ("cards.push(bimClbCard('s4',fig,'The sun climbs to '", "cards.push(bimClbCard(['s4','@clim.sun'],fig,'The sun climbs to '"),
        ("cards.push(bimClbCard('s4',fig,(a.hdd>2*a.cdd?", "cards.push(bimClbCard(['s4','@clim.dd'],fig,(a.hdd>2*a.cdd?"),
        ("cards.push(bimClbCard('s4',fig,bimClimInt(a.sw)+' kWh/m", "cards.push(bimClbCard(['s4','@clim.solar'],fig,bimClimInt(a.sw)+' kWh/m"),
        ("cards.push(bimClbCard('s6',fig,bimClbNum(Hh.comfort.inside,0)+'% of hours are comfortable outdoors", "cards.push(bimClbCard(['s6','@clim.psy'],fig,bimClbNum(Hh.comfort.inside,0)+'% of hours are comfortable outdoors"),
        ("cards.push(bimClbCard('s6',fig,E.count?(", "cards.push(bimClbCard(['s6','@risk.quake'],fig,E.count?("),
        ("cards.push(bimClbCard(['s12','wide'],fig,'PM2.5 averaged '", "cards.push(bimClbCard(['s12','wide','@risk.air'],fig,'PM2.5 averaged '")]:
    rep(CB, old, new)
rep(CB, "    h+='<section class=\"a3d-clb-kpis\" aria-label=\"Indicators\"",
    "    bimFigCapKpis('clim.kpis',kp);   /* __acad3dV172b */\n    h+='<section class=\"a3d-clb-kpis\" aria-label=\"Indicators\"")
rep(CB, "if(c){fig++;lbAny=true;cards.push(c.replace('<figure class=\"a3d-clb-card','<figure data-figid=\"'+F[0]+'\" class=\"a3d-clb-card'));}});",
    "if(c){fig++;lbAny=true;cards.push(c);}});")
rep(CB, "  function bimClbHtml(){\n",
    "  function bimClbHtml(){\n    if(!A3D_CLB.raw)return bimBrdHtml();   /* __acad3dV172b: a board's own list, a board of one's own, Edit; then each board as ever */\n")
rep(CB, "    var was=A3D_CLB.open?A3D_CLB.kind:null;\n"
        "    if(kind==='climate'||kind==='zoning'||kind==='access')A3D_CLB.kind=kind;   /* __acad3dV160; __acad3dV161 */\n",
    "    var was=A3D_CLB.open?bimClbWhich():null;   /* __acad3dV172b: a board of one's own is opened by its id */\n"
    "    if(kind==='climate'||kind==='zoning'||kind==='access'){A3D_CLB.kind=kind;A3D_CLB.cid=null;}   /* __acad3dV160; __acad3dV161 */\n"
    "    else if(kind&&bimBoardById(kind)&&bimBoardById(kind).kind==='custom'){A3D_CLB.kind='custom';A3D_CLB.cid=kind;}\n"
    "    if(was!==bimClbWhich()){A3D_CLB.edit=false;bimBrdDlgClose();}\n")
rep(CB, "    A3D_CLB.board=bimBoardById('board-'+A3D_CLB.kind)?'board-'+A3D_CLB.kind:null;\n",
    "    A3D_CLB.board=A3D_CLB.kind==='custom'?(bimBoardById(A3D_CLB.cid)?A3D_CLB.cid:null):(bimBoardById('board-'+A3D_CLB.kind)?'board-'+A3D_CLB.kind:null);   /* __acad3dV172b */\n")
rep(CB, "    b.setAttribute('aria-label',bimBoardName(A3D_CLB.kind)+' board');\n"
        "    b.innerHTML=bimClbHtml()+'<div class=\"a3d-clb-tip\" role=\"tooltip\" hidden></div>';\n",
    "    b.setAttribute('aria-label',bimClbLabel()+' board');   /* __acad3dV172b */\n"
    "    b.innerHTML=bimClbHtml()+'<div class=\"a3d-clb-tip\" role=\"tooltip\" hidden></div>';\n"
    "    bimBrdZoom(b);\n")
rep(CB, "    if(was!==A3D_CLB.kind){   /* a board opened, not one redrawn: the focus and the top go to it */",
    "    if(was!==bimClbWhich()){   /* a board opened, not one redrawn: the focus and the top go to it */")
rep(CB, "    A3D_CLB.open=false;A3D_CLB.board=null;document.body.classList.remove('a3d-clb-open');\n",
    "    A3D_CLB.open=false;A3D_CLB.board=null;document.body.classList.remove('a3d-clb-open');\n"
    "    A3D_CLB.edit=false;A3D_BRD.drag=null;bimBrdDlgClose();   /* __acad3dV172b */\n")
rep(CB, "      else if(a==='print')bimClbPrint(A3D_CLB.kind);", "      else if(a==='print')bimClbPrint(bimClbWhich());")
rep(CB, "    b.addEventListener('focusout',function(){bimClbTipHide(b);});\n",
    "    b.addEventListener('focusout',function(){bimClbTipHide(b);});\n    bimBrdWire(b);   /* __acad3dV172b: Edit */\n")

# ---- the zoning board ----
ZN = 'js/engine/site-analysis/zoning-envelope.js'
for old, new in [
        ("cards.push(bimClbCard(['s7','wide'],fig,!has?'The zoning analysis: '", "cards.push(bimClbCard(['s7','wide','@zn.table'],fig,!has?'The zoning analysis: '"),
        ("cards.push(bimClbCard('s5',fig,'The envelope rises to '", "cards.push(bimClbCard(['s5','@zn.secA'],fig,'The envelope rises to '"),
        ("cards.push(bimClbCard('s4',fig,Sb.lot&&Sb.L.length?'Side to side", "cards.push(bimClbCard(['s4','@zn.secB'],fig,Sb.lot&&Sb.L.length?'Side to side"),
        ("cards.push(bimClbCard('s4',fig,'Each side\\'s rule: '", "cards.push(bimClbCard(['s4','@zn.rules'],fig,'Each side\\'s rule: '"),
        ("cards.push(bimClbCard('s4',fig,bimClimInt(C.fpArea)+' m", "cards.push(bimClbCard(['s4','@zn.plan'],fig,bimClimInt(C.fpArea)+' m"),
        ("cards.push(bimClbCard('s6',fig,C.plates.length+' storeys fit under the envelope", "cards.push(bimClbCard(['s6','@zn.plates'],fig,C.plates.length+' storeys fit under the envelope"),
        ("cards.push(bimClbCard(['s6','wide'],fig,'The '+C.governs+' governs: '", "cards.push(bimClbCard(['s6','wide','@zn.yield'],fig,'The '+C.governs+' governs: '")]:
    rep(ZN, old, new)
rep(ZN, "    var h=bar+head+'<section class=\"a3d-clb-kpis\" aria-label=\"Indicators\"",
    "    bimFigCapKpis('zn.kpis',kp);   /* __acad3dV172b */\n    var h=bar+head+'<section class=\"a3d-clb-kpis\" aria-label=\"Indicators\"")
rep(ZN, "if(A3D_CLB.open&&A3D_CLB.kind==='zoning')bimClbOpen('zoning');",
    "if(A3D_CLB.open&&A3D_CLB.kind==='zoning')bimClbOpen('zoning');else if(A3D_CLB.open&&bimBrdRec()&&bimBrdRec().figs)bimClbOpen();")

# ---- the access board ----
AC = 'js/engine/site-analysis/access-board.js'
for old, new in [
        ("f1=bimClbCard('s7',++fig,'A 10-minute walk reaches '", "f1=bimClbCard(['s7','@acc.walk'],++fig,'A 10-minute walk reaches '"),
        ("f2=bimClbCard('s5',++fig,w10+' of '+S.places.length+' daily needs", "f2=bimClbCard(['s5','@acc.needs'],++fig,w10+' of '+S.places.length+' daily needs"),
        ("f3=bimClbCard('s7',++fig,!S.lot.ring?", "f3=bimClbCard(['s7','@acc.streets'],++fig,!S.lot.ring?"),
        ("f4=bimClbCard('s5',++fig,(nb2?", "f4=bimClbCard(['s5','@acc.stops'],++fig,(nb2?"),
        ("f5=bimClbCard('s5',++fig,bimClimFmt(C2.dens,0)", "f5=bimClbCard(['s5','@acc.conn'],++fig,bimClimFmt(C2.dens,0)"),
        ("f6=bimClbCard('s7',++fig,big?", "f6=bimClbCard(['s7','@ppl.compare'],++fig,big?"),
        ("col+=bimClbCard('s5',++fig,BIM_ACC_COMMUTE[bj][0]", "col+=bimClbCard(['s5','@ppl.commute'],++fig,BIM_ACC_COMMUTE[bj][0]"),
        ("col+=bimClbCard('s5',++fig,bimClimFmt(gs(PT,grp[gi]),0)", "col+=bimClbCard(['s5','@ppl.pyramid'],++fig,bimClimFmt(gs(PT,grp[gi]),0)")]:
    rep(AC, old, new)
rep(AC, "    if(ka.length)h+='<div class=\"a3d-acc-kh\">Access and circulation</div>",
    "    bimFigCapKpis('acc.kpis',ka);bimFigCapKpis('ppl.kpis',kq);   /* __acad3dV172b */\n    if(ka.length)h+='<div class=\"a3d-acc-kh\">Access and circulation</div>")

# ---- Ladybug's figures, named ----
LB = 'js/engine/ladybug/figures.js'
rep(LB, "return bimClbCard(['s12','wide'],no,title,dek,body,", "return bimClbCard(['s12','wide','@lb.utci'],no,title,dek,body,")
rep(LB, "return bimClbCard('s7',no,title,dek,body,", "return bimClbCard(['s7','@lb.psych'],no,title,dek,body,")
rep(LB, "return bimClbCard('s5',no,title,'Share of the hours from each direction", "return bimClbCard(['s5','@lb.wind'],no,title,'Share of the hours from each direction")
rep(LB, "return bimClbCard('s5',no,title,'The conditions a building", "return bimClbCard(['s5','@lb.dd'],no,title,'The conditions a building")
rep(LB, "if(c){fig++;cards.push(c.replace('<figure class=\"a3d-clb-card','<figure data-figid=\"'+F[0]+'\" class=\"a3d-clb-card'));}});",
    "if(c){fig++;cards.push(c);}});")

# ---- the set: the record, the menus, a board of one's own by its id ----
BD = 'js/engine/sheets/boards.js'
rep(BD, "        if(b&&typeof b==='object'&&bimBoardName(b.kind)&&!seen[b.kind]){seen[b.kind]=1;out.boards.push({id:'board-'+b.kind,kind:b.kind});}\n",
    "        if(b&&typeof b==='object'&&bimBoardName(b.kind)&&!seen[b.kind]){seen[b.kind]=1;out.boards.push(bimBrdKeep({id:'board-'+b.kind,kind:b.kind},b));}   /* __acad3dV172b: its list, if it has one */\n"
    "        else if(b&&typeof b==='object'&&b.kind==='custom'&&typeof b.id==='string'&&/^board-c\\d{1,6}$/.test(b.id)&&!seen[b.id]){seen[b.id]=1;out.boards.push(bimBrdKeep({id:b.id,kind:'custom'},b));}   /* a board of one's own */\n")
rep(BD, "    if(A3D_CLB.open&&A3D_CLB.kind===b.kind)bimClbClose();\n    saveSoon();bimPresPanelRefresh();\n"
        "    a3dToast(bimBoardName(b.kind)+' is out of the set; its data stays in Analyze');\n",
    "    if(A3D_CLB.open&&(b.kind==='custom'?A3D_CLB.cid===b.id:A3D_CLB.kind===b.kind))bimClbClose();   /* __acad3dV172b */\n    saveSoon();bimPresPanelRefresh();\n"
    "    a3dToast(b.kind==='custom'?bimBoardLabel(b)+' is deleted; Ctrl+Z brings it back':bimBoardName(b.kind)+' is out of the set; its data stays in Analyze');\n")
rep(BD, "    bimClbOpen(b.kind);\n", "    bimClbOpen(bimBoardKey(b));   /* __acad3dV172b */\n")
rep(BD, "    bimLtMenuOpen(r.left,r.bottom+4,bimBoards().map(function(x){return [x[1]+(bimBoardById('board-'+x[0])?' (in the set)':''),x[0]];}),function(k){bimBoardShow(k);});\n",
    "    bimLtMenuOpen(r.left,r.bottom+4,bimBoards().map(function(x){return [x[1]+(bimBoardById('board-'+x[0])?' (in the set)':''),x[0]];}).concat(['-',['New board','new']]),   /* __acad3dV172b: a board of one's own */\n"
    "      function(k){if(k==='new')bimBrdNewUi();else bimBoardShow(k);});\n")
rep(BD, "    var i=bimPresIndex(id),n=bimPresSeq().length,it=[['Present from this page','present'],'-',['Open','open'],['Print…','print']];\n",
    "    var i=bimPresIndex(id),n=bimPresSeq().length,b=bimBoardById(id),c=!!(b&&b.kind==='custom'),it=[['Present from this page','present'],'-',['Open','open'],['Edit','edit'],['Print…','print']];   /* __acad3dV172b: Edit, Duplicate */\n")
rep(BD, "    it.push('-',['Remove from the set','remove',true]);\n",
    "    it.push('-',[c?'Duplicate':'Duplicate as a new board','dup'],'-',[c?'Delete the board':'Remove from the set','remove',true]);\n")
rep(BD, "    if(a==='print')return bimClbPrint(b.kind);\n",
    "    if(a==='edit')return bimPresOpenBoard(id)&&bimBrdEdit(true);   /* __acad3dV172b */\n    if(a==='dup')return !!bimBrdDupBoard(id);\n"
    "    if(a==='print')return bimClbPrint(bimBoardKey(b));\n")
rep(BD, "    var k=A3D_CLB.kind,n=A3D_CLB.narrow,h;\n    A3D_CLB.kind=kind;A3D_CLB.narrow=!!narrow;\n"
        "    try{h=bimClbHtml();}finally{A3D_CLB.kind=k;A3D_CLB.narrow=n;}\n",
    "    var k=A3D_CLB.kind,n=A3D_CLB.narrow,c=A3D_CLB.cid,o=A3D_CLB.other,B=bimBoardById(kind),h;   /* __acad3dV172b: a board of one's own by its id; nothing of Edit */\n"
    "    if(B&&B.kind==='custom'){A3D_CLB.kind='custom';A3D_CLB.cid=B.id;}else A3D_CLB.kind=kind;\n"
    "    A3D_CLB.narrow=!!narrow;A3D_CLB.other=true;\n"
    "    try{h=bimClbHtml();}finally{A3D_CLB.kind=k;A3D_CLB.narrow=n;A3D_CLB.cid=c;A3D_CLB.other=o;}\n")
rep(BD, "    if(!bimBoardName(kind))kind=A3D_CLB.kind;\n", "    if(!bimBoardName(kind)&&!bimBoardById(kind))kind=bimClbWhich();   /* __acad3dV172b */\n")
rep(BD, "bimEsc(bimProjectLabel()+' - '+bimBoardName(kind))", "bimEsc(bimProjectLabel()+' - '+bimBoardKeyLabel(kind))")
rep(BD, "    a3dToast('Printing '+bimBoardName(kind)+' -- Save as PDF", "    a3dToast('Printing '+bimBoardKeyLabel(kind)+' -- Save as PDF")
rep(BD, "T=A3D_PRP.bthumbs[b.id]={key:key,html:bimBoardPrintHtml(b.kind)};", "T=A3D_PRP.bthumbs[b.id]={key:key,html:bimBoardPrintHtml(bimBoardKey(b))};")
rep(BD, ".a3d-clb.prt .a3d-clb-page{padding:28px 32px}</style>", ".a3d-clb.prt .a3d-clb-page{padding:28px 32px}.a3d-clb.prt .a3d-clb-arr{zoom:.86364}</style>")
rep(BD, "      console.warn('[BIM] The thumbnail of the '+bimBoardName(b.kind)+' board could not be drawn',eT);",
    "      console.warn('[BIM] The thumbnail of the '+bimBoardLabel(b)+' board could not be drawn',eT);")

# ---- Present, Print set, the Presentation panel ----
PR = 'js/engine/sheets/present.js'
rep(PR, "    bd.setAttribute('aria-label',bimBoardName(e.b.kind)+' board');\n    sig=e.b.kind+'|'+A3D_REV+'|'+(w<760);\n",
    "    bd.setAttribute('aria-label',bimBoardLabel(e.b)+' board');\n    sig=e.b.id+'|'+A3D_REV+'|'+(w<760);   /* __acad3dV172b: a board of one's own by its id */\n")
rep(PR, "      bd.innerHTML=bimBoardHtmlFor(e.b.kind,w<760)+", "      bd.innerHTML=bimBoardHtmlFor(bimBoardKey(e.b),w<760)+")
rep(PR, "    A3D_SLIDESHOW.scale=0;\n  }\n  function bimSlideshowAhead",
    "    bimBrdZoom(bd);   /* __acad3dV172b */\n    A3D_SLIDESHOW.scale=0;\n  }\n  function bimSlideshowAhead")
rep(PR, "    if(e&&e.t==='board'){bimClbOpen(e.b.kind);return true;}", "    if(e&&e.t==='board'){bimClbOpen(bimBoardKey(e.b));return true;}")
VP = 'js/engine/sheets/viewports.js'
rep(VP, "bimBoardPrintHtml(e.b.kind)", "bimBoardPrintHtml(bimBoardKey(e.b))")
rep(VP, "bimBoardName(e.b.kind)", "bimBoardLabel(e.b)", 2)
rep('js/engine/sheets/presentation-panel.js', "        lab=bimBoardName(e.b.kind);\n", "        lab=bimBoardLabel(e.b);   /* __acad3dV172b */\n")

# ---- undo, and the drawing's snaps ----
PM = 'js/engine/drawing/plan-mode-sketch.js'
rep(PM, "    bimPresPanelRefresh();   /* __acad3dV162 */\n    undoSuspend=false;",
    "    bimPresPanelRefresh();   /* __acad3dV162 */\n    bimBrdRestored();   /* __acad3dV172b: the open board, as the record now is */\n    undoSuspend=false;")
rep(PM, "  function syncSnapPill(){\n    bimSyncStatusHint();\n",
    "  function syncSnapPill(){\n    bimSyncStatusHint();\n    bimBrdSnapSync();   /* __acad3dV172b: a board's Edit shows the same three */\n")

# ---- the marker ----
rep('js/engine/testing/hooks-ladybug.js', "strategies5,windrose,designdays,kept';",
    "strategies5,windrose,designdays,kept,figids,arranged,bands,zoom,edit,snaps,keys,catalogue,options,custom,duplicate';")

LAY = ROOT / 'tools' / 'app_layout.py'
s = LAY.read_text(encoding='utf-8')
a1 = "    ('site-analysis/boards.css', '/* __acad3dV158: the Site analysis tab */'),\n"
a2 = "    ('sheets/boards.js', '  /* ================= __acad3dV162: the boards are pages of the set ================='),\n"
a3 = "    ('testing/hooks-ladybug.js', '  /* __acad3dV172b: the Ladybug analyses, for the suite */'),\n"
assert s.count(a1) == 1 and s.count(a2) == 1 and s.count(a3) == 1, 'app_layout.py anchors'
s = s.replace(a1, a1 + "    ('site-analysis/boards-arranged.css', \"/* ================= __acad3dV172b: a board's figures, arranged; Edit =================\"),\n")
s = s.replace(a2, a2 +
    "    ('sheets/board-figures.js', \"  /* ================= __acad3dV172b: a board's figures, arranged =================\"),\n"
    "    ('sheets/board-edit.js', '  /* ================= __acad3dV172b: Edit, on a board ================='),\n")
s = s.replace(a3, a3 + "    ('testing/hooks-boards.js', \"  /* __acad3dV172b: a board's figures and Edit, for the suite */\"),\n")
LAY.write_text(s, encoding='utf-8')
done()
