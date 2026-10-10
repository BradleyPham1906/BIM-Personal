"""patch_phase162b.py -- V162: the boards are pages of the set.

reference/research-one-analyze-boards.md. The owner: "for the report/ dashboard, it should be on the
presentation layer not its own thing". A board -- Climate and risk, Zoning and yield, Access and
people -- was a dialog over the whole app. It is a page of the presentation now, beside the sheets:
- in the Presentation panel with its thumbnail (the board as it prints, scaled), numbered in the
  set's order, dragged to move it, with + Board to add one and its own menu (present from here,
  open, print, move, remove from the set);
- opened in the main view, the panels beside it: the rail, the panel and Properties stay; Esc, a view
  or a sheet gives the main view back. It lays out by its own width, not the window's;
- in Present, as on screen, scrolled with the wheel or a finger; and in Print set, on A3 landscape
  pages of its own between the sheets. Its own Print opens it alone in a print window;
- Analyze gets the data and links to it: "Show in Presentation" puts the board in the set if it is
  not, opens it and shows its page. ACCESS, CLIMATE and ZONINGBOARD do the same.
A3D.pres keeps the boards in the set and the set's order; the sheets keep their order among
themselves (the layout tabs), and a board its place among them. It is saved, undone and kept in
History with the project."""
NAME = 'patch_phase162b.py'
BASE = '126491d8e01c16ed505e142f4b87325c1a881cbf02d546279f396a3df5ce5991'   # the output of patch_phase162a.py
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


def span(start, end, new):
    """replace from start up to and including end (both unique from start on)"""
    global t
    if t.count(start) != 1:
        sys.exit('ABORT: span start count %d: %r' % (t.count(start), start[:80]))
    i = t.index(start)
    j = t.find(end, i)
    if j < 0:
        sys.exit('ABORT: span end not found: %r' % end[:80])
    t = t[:i] + new + t[j + len(end):]


# ================= CSS =================
# a board lays out by its own width (classes set from it), not by the window's: it sits in the main
# view beside the panels, in Present on the screen, in print on the paper
rep("@media(min-width:1240px){.a3d-clb-kpis{grid-template-columns:repeat(var(--n,9),minmax(0,1fr))}}\n",
    ".a3d-clb.w-l .a3d-clb-kpis{grid-template-columns:repeat(var(--n,9),minmax(0,1fr))}   /* __acad3dV162: by the board's own width */\n")
rep("@media(max-width:760px){.a3d-zn-zt{font-size:12px}.a3d-zn-zt th,.a3d-zn-zt td{padding:6px 5px}}\n",
    ".a3d-clb.w-s .a3d-zn-zt{font-size:12px}.a3d-clb.w-s .a3d-zn-zt th,.a3d-clb.w-s .a3d-zn-zt td{padding:6px 5px}\n")
rep("@media(max-width:1100px){.a3d-acc-col{grid-column:span 6}}\n@media(max-width:760px){.a3d-acc-col{grid-column:span 12}}\n",
    ".a3d-clb.w-m .a3d-acc-col{grid-column:span 6}\n.a3d-clb.w-s .a3d-acc-col{grid-column:span 12}\n")
rep("""@media(max-width:1100px){.a3d-clb-card.s4,.a3d-clb-card.s5,.a3d-clb-card.s6,.a3d-clb-card.s7{grid-column:span 6}.a3d-clb-card.wide{grid-column:span 12}}
@media(max-width:760px){.a3d-clb-card.s4,.a3d-clb-card.s5,.a3d-clb-card.s6,.a3d-clb-card.s7{grid-column:span 12}.a3d-clb-h1{font-size:21px}
  .a3d-clb-heat{overflow-x:auto;-webkit-overflow-scrolling:touch}.a3d-clb-heat svg{min-width:880px}
  .a3d-clb-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.a3d-clb-kv{font-size:20px}.a3d-clb-btn{min-height:38px}.a3d-clb-bar .a3d-clb-hide-s{display:none}}
""", """.a3d-clb.w-m .a3d-clb-card.s4,.a3d-clb.w-m .a3d-clb-card.s5,.a3d-clb.w-m .a3d-clb-card.s6,.a3d-clb.w-m .a3d-clb-card.s7{grid-column:span 6}.a3d-clb.w-m .a3d-clb-card.wide{grid-column:span 12}
.a3d-clb.w-s .a3d-clb-card.s4,.a3d-clb.w-s .a3d-clb-card.s5,.a3d-clb.w-s .a3d-clb-card.s6,.a3d-clb.w-s .a3d-clb-card.s7{grid-column:span 12}.a3d-clb.w-s .a3d-clb-h1{font-size:21px}
.a3d-clb.w-s .a3d-clb-heat{overflow-x:auto;-webkit-overflow-scrolling:touch}.a3d-clb.w-s .a3d-clb-heat svg{min-width:880px}
.a3d-clb.w-s .a3d-clb-kpis{grid-template-columns:repeat(auto-fit,minmax(130px,1fr))}.a3d-clb.w-s .a3d-clb-kv{font-size:20px}.a3d-clb.w-s .a3d-clb-btn{min-height:38px}.a3d-clb.w-s .a3d-clb-bar .a3d-clb-hide-s{display:none}
/* __acad3dV162: a board is a page: in the main view, the panels beside it; nothing to draw with over it */
.a3d-vp>.a3d-clb{position:absolute;inset:0;z-index:700}
body.a3d-clb-open #a3d-dock,body.a3d-clb-open .a3d-tpal{display:none!important}
/* as it prints, in a print window and in its thumbnail: on paper, in the print tokens */
.a3d-clb.prt{position:static;inset:auto;z-index:auto;overflow:visible;background:#fff;color-scheme:light;
  --surf:#fff;--page:#fff;--ink:#0b0b0b;--ink2:#52514e;--muted:#6f6d68;--grid:#e1e0d9;--base:#c3c2b7;--ring:rgba(11,11,11,.14);
  --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;--s6:#008300;--s7:#6250d6;--band:rgba(11,11,11,.07);
  --w1:#86b6ef;--w2:#5598e7;--w3:#2a78d6;--w4:#1c5cab;--w5:#104281;--hn:#e7e5df}
.a3d-clb.prt .a3d-clb-bar,.a3d-clb.prt .a3d-clb-tip{display:none!important}
.a3d-clb.prt .a3d-clb-page{max-width:none}
.a3d-clb.prt .a3d-clb-card,.a3d-clb.prt .a3d-clb-kpi,.a3d-clb.prt .a3d-clb-notes{break-inside:avoid;page-break-inside:avoid}
/* in Present: the board over the black, scrolled with the wheel or a finger; the controls over it */
.a3d-slideshow .a3d-ssboard{position:absolute;inset:0;z-index:1}
.a3d-slideshow .a3d-ssboard .a3d-clb-bar{display:none}
.a3d-slideshow .a3d-ssbar,.a3d-slideshow .a3d-sshint{z-index:2}
.a3d-slideshow .a3d-ssboard .a3d-clb-page{padding-top:46px;padding-bottom:84px}
/* a unit stays whole beside its number, however narrow the tile */
.a3d-clb-ku{white-space:nowrap}
""")
rep("#a3d-shell[data-tab=\"analyze\"] .a3d-projhead{flex-shrink:0}\n",
    "#a3d-shell .a3d-projhead{flex-shrink:0}   /* __acad3dV162: a tab's long list scrolls under the project's name in every tab, not over it (Presentation's squashed it) */\n")
rep(".a3d-prpthumb canvas{display:block;width:100%;height:auto}\n",
    ".a3d-prpthumb canvas{display:block;width:100%;height:auto}\n"
    "/* __acad3dV162: a board's page: the board as it prints, laid out at 1280 px and scaled to the column */\n"
    ".a3d-prpbthumb{position:relative;overflow:hidden;aspect-ratio:420/297}\n"
    ".a3d-prpbthumb iframe{position:absolute;left:0;top:0;width:1280px;height:905px;border:0;transform-origin:0 0;pointer-events:none;background:#fff}\n"
    ".a3d-prptag{flex:0 0 auto;font-size:10px;color:#9aa5b0;border:1px solid rgba(255,255,255,.16);border-radius:4px;padding:0 4px;line-height:15px}\n"
    "body.light-theme .a3d-prptag{color:#666;border-color:rgba(0,0,0,.18)}\n")

# ================= the board in the main view =================
rep("""  var A3D_CLB={open:false,tables:false,narrow:false,kind:'climate'};   /* __acad3dV160: which board */
  window.addEventListener('resize',function(){if(A3D_CLB.open&&(window.innerWidth<760)!==A3D_CLB.narrow)bimClbOpen();});
  /* Esc shuts the board wherever the focus is, before the app's own keys see it */
  document.addEventListener('keydown',function(ev){if(A3D_CLB.open&&ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimClbClose();}},true);
""", """  var A3D_CLB={open:false,tables:false,narrow:false,kind:'climate',board:null,printFrom:null};   /* __acad3dV160: which board; __acad3dV162: its page in the set */
  window.addEventListener('resize',function(){var b=bimClbEl();if(A3D_CLB.open&&b)bimClbFit(b);});
  /* __acad3dV162: the keys on a board's page, as a sheet's page has its own. Esc gives the main view
     back; the model's keys do not reach the model behind it (the arrows and Space scroll the board);
     Ctrl, Alt and the function keys do. A field in a panel beside it keeps its keys. The app's own
     key handler asks this first; this listener is for when that one is not listening. */
  function bimClbKey(ev){
    if(!A3D_CLB.open)return false;
    var a=document.activeElement,b=bimClbEl();
    if(a&&a!==document.body&&!(b&&b.contains(a))&&(/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName)||a.isContentEditable))return false;
    if(ev.key==='Escape'){ev.preventDefault();ev.stopImmediatePropagation();bimClbClose();return true;}
    if(ev.ctrlKey||ev.metaKey||ev.altKey||/^F\d+$/.test(ev.key))return false;
    return true;
  }
  document.addEventListener('keydown',function(ev){if(ev.key==='Escape')bimClbKey(ev);},true);
  /* the main board, not Present's */
  function bimClbEl(){return document.querySelector('.a3d-clb:not(.a3d-ssboard)');}
  /* the width it lays out by: the main view's */
  function bimClbW(b){var p=b&&b.parentNode;return Math.round(p&&p!==document.body?(p.clientWidth||window.innerWidth):window.innerWidth);}
  function bimClbWidthCls(w){return (w>=1240?' w-l':'')+(w<1100?' w-m':'')+(w<760?' w-s':'');}
  function bimClbFit(b){
    if(!A3D_CLB.open||!b.parentNode)return;
    var w=bimClbW(b),cls;
    if((w<760)!==A3D_CLB.narrow){bimClbOpen();return;}   /* the figures are drawn for a phone, or not */
    cls='a3d-clb'+(A3D_CLB.tables?' tables':'')+bimClbWidthCls(w);
    if(b.className!==cls)b.className=cls;
  }
""")
span("  /* open, refresh, close; the tooltip; Esc */\n  function bimClbOpen(kind){\n",
     "  function bimClbRefresh(){if(A3D_CLB.open)bimClbOpen();}\n",
     r"""  /* open, refresh, close; the tooltip; Esc. __acad3dV162: in the main view, the panels beside it */
  function bimClbOpen(kind){
    var was=A3D_CLB.open?A3D_CLB.kind:null;
    if(kind==='climate'||kind==='zoning'||kind==='access')A3D_CLB.kind=kind;   /* __acad3dV160; __acad3dV161 */
    var host=document.querySelector('.a3d-vp')||document.body,b=bimClbEl(),w;
    if(!b){
      b=document.createElement('div');
      b.setAttribute('role','region');
      bimClbWire(b);
    }
    if(b.parentNode!==host)host.appendChild(b);
    if(!b.__clbRO&&typeof ResizeObserver!=='undefined'){
      try{b.__clbRO=new ResizeObserver(function(){bimClbFit(b);});b.__clbRO.observe(b);}
      catch(eR){console.warn('[BIM] The board cannot follow the width of the main view',eR);}
    }
    w=bimClbW(b);
    A3D_CLB.narrow=w<760;
    A3D_CLB.board=bimBoardById('board-'+A3D_CLB.kind)?'board-'+A3D_CLB.kind:null;
    b.className='a3d-clb'+(A3D_CLB.tables?' tables':'')+bimClbWidthCls(w);
    b.setAttribute('aria-label',bimBoardName(A3D_CLB.kind)+' board');
    b.innerHTML=bimClbHtml()+'<div class="a3d-clb-tip" role="tooltip" hidden></div>';
    A3D_CLB.open=true;document.body.classList.add('a3d-clb-open');
    if(was!==A3D_CLB.kind){   /* a board opened, not one redrawn: the focus and the top go to it */
      b.scrollTop=0;
      var c=b.querySelector('[data-clb="close"]');if(c)try{c.focus({preventScroll:true});}catch(eF){}
    }
    bimPresPanelRefresh();
    return true;
  }
  function bimClbClose(){
    var b=bimClbEl(),was=A3D_CLB.open;
    if(b){if(b.__clbRO){try{b.__clbRO.disconnect();}catch(eD){}}if(b.parentNode)b.parentNode.removeChild(b);}
    A3D_CLB.open=false;A3D_CLB.board=null;document.body.classList.remove('a3d-clb-open');
    if(was)bimPresPanelRefresh();
    return true;
  }
  function bimClbRefresh(){if(A3D_CLB.open)bimClbOpen();bimPresThumbsQueue();}
  /* the browser's own print (Ctrl+P) of an open board: the board alone on the paper, as before it
     was a page in the main view */
  window.addEventListener('beforeprint',function(){
    var b=bimClbEl();
    if(!A3D_CLB.open||!b||b.parentNode===document.body)return;
    A3D_CLB.printFrom=b.parentNode;document.body.appendChild(b);
    b.className='a3d-clb'+(A3D_CLB.tables?' tables':'')+' w-l';
  });
  window.addEventListener('afterprint',function(){
    var b=bimClbEl();
    if(!b||!A3D_CLB.printFrom)return;
    A3D_CLB.printFrom.appendChild(b);A3D_CLB.printFrom=null;
    bimClbFit(b);
  });
""")
rep("      else if(a==='print'){try{window.print();}catch(eP){}}\n",
    "      else if(a==='print')bimClbPrint(A3D_CLB.kind);   /* __acad3dV162: alone, in a print window, as Print set prints it */\n")

# ================= Analyze links to the board in the set =================
rep("""data-saact="climboard">Open the board</button>""",
    """data-saact="climboard" title="The board is a page of the set: it opens here and presents and prints with the sheets">Show in Presentation</button>""", 2)
rep("""data-saact="znboard">Open the board</button>""",
    """data-saact="znboard" title="The board is a page of the set: it opens here and presents and prints with the sheets">Show in Presentation</button>""")
rep("""data-saact="accboard">Open the board</button>""",
    """data-saact="accboard" title="The board is a page of the set: it opens here and presents and prints with the sheets">Show in Presentation</button>""", 2)
rep("    if(c==='climboard')return bimClbOpen('climate');\n", "    if(c==='climboard')return bimBoardShow('climate');   /* __acad3dV162: a page of the set */\n")
rep("    if(c==='znboard')return bimClbOpen('zoning');\n", "    if(c==='znboard')return bimBoardShow('zoning');\n")
rep("    if(c==='accboard')return bimClbOpen('access');\n", "    if(c==='accboard')return bimBoardShow('access');\n")
rep("    climate:function(){bimClbOpen('climate');},\n", "    climate:function(){bimBoardShow('climate');},                     /* __acad3dV162: the board's page in the set */\n")
rep("    zoningboard:function(){bimClbOpen('zoning');},", "    zoningboard:function(){bimBoardShow('zoning');},")
rep("    access:function(){bimClbOpen('access');},\n", "    access:function(){bimBoardShow('access');},\n")
rep("  function bimZnDone(){refreshTree();refreshLayers();refreshProps();paint();saveSoon();bimSaRefresh(true);if(A3D_CLB.open&&A3D_CLB.kind==='zoning')bimClbOpen('zoning');}",
    "  function bimZnDone(){refreshTree();refreshLayers();refreshProps();paint();saveSoon();bimSaRefresh(true);if(A3D_CLB.open&&A3D_CLB.kind==='zoning')bimClbOpen('zoning');bimPresThumbsQueue();}")

# ================= the set, kept with the project =================
rep("      A3D.resultLayers=bimResValid(st&&st.resultLayers);   /* __acad3dV148: its result layers, or none */\n",
    "      A3D.resultLayers=bimResValid(st&&st.resultLayers);   /* __acad3dV148: its result layers, or none */\n"
    "      A3D.pres=bimPresValid(st&&st.pres);   /* __acad3dV162: its boards in the set, and the set's order */\n")
rep("resultLayers:A3D.resultLayers||[]});   /* __acad3dV148 */",
    "resultLayers:A3D.resultLayers||[],pres:A3D.pres||null});   /* __acad3dV148; __acad3dV162 */")
rep("resultLayers:A3D.resultLayers||[]}});", "resultLayers:A3D.resultLayers||[],pres:A3D.pres||null}});")
rep("resultLayers:A3D.resultLayers||[]};   /* __acad3dV146, __acad3dV148 */",
    "resultLayers:A3D.resultLayers||[],pres:A3D.pres||null};   /* __acad3dV146, __acad3dV148; __acad3dV162 */")
rep("    if(Array.isArray(st.resultLayers))A3D.resultLayers=st.resultLayers;   /* __acad3dV148: a version from History has none, and keeps today's */\n",
    "    if(Array.isArray(st.resultLayers))A3D.resultLayers=st.resultLayers;   /* __acad3dV148: a version from History has none, and keeps today's */\n"
    "    A3D.pres=bimPresValid(st.pres);   /* __acad3dV162: the set as it was */\n")
rep("    refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();bimSheetViewRefresh();paint();\n    undoSuspend=false;",
    "    refreshTree();refreshHud();refreshLevels();refreshLayers();refreshViews();bimSheetViewRefresh();paint();\n    bimPresPanelRefresh();   /* __acad3dV162 */\n    undoSuspend=false;")

rep("    if(bimStartShowing())return;\n    if(bimSheetOnScreen()&&bimSheetKey(ev))return;   /* __acad3dV116 */\n",
    "    if(bimStartShowing())return;\n    if(bimClbKey(ev))return;   /* __acad3dV162: a board's page owns the keys, as a sheet's does */\n    if(bimSheetOnScreen()&&bimSheetKey(ev))return;   /* __acad3dV116 */\n")

# ================= a view, or a sheet, gives the main view back =================
rep("    var anim=(opts.anim!==false),sv=null,q;\n",
    "    var anim=(opts.anim!==false),sv=null,q;\n    if(A3D_CLB.open)bimClbClose();   /* __acad3dV162: a board's page gives the main view back */\n")

# ================= the set: the boards in it, and its order =================
BOARDS = r"""  /* ================= __acad3dV162: the boards are pages of the set =================
     reference/research-one-analyze-boards.md. A board is a page of the presentation beside the
     sheets: in the Presentation panel with its thumbnail, in the main view, in Present and in Print
     set. Analyze fetches the data and links to it. A3D.pres keeps the boards in the set and the
     set's order; the sheets keep their order among themselves (the layout tabs), and a board its
     place among them. */
  /* a function, not a list: a project is read from storage early in the boot, before a list here
     would have been made */
  function bimBoards(){return [['climate','Climate and risk'],['zoning','Zoning and yield'],['access','Access and people']];}
  function bimBoardName(kind){var B=bimBoards(),i;for(i=0;i<B.length;i++)if(B[i][0]===kind)return B[i][1];return '';}
  /* the record as saved: one board of each kind, an order of ids */
  function bimPresValid(p){
    var out={boards:[],order:[]},seen={};
    if(p&&typeof p==='object'){
      if(Array.isArray(p.boards))p.boards.forEach(function(b){
        if(b&&typeof b==='object'&&bimBoardName(b.kind)&&!seen[b.kind]){seen[b.kind]=1;out.boards.push({id:'board-'+b.kind,kind:b.kind});}
      });
      if(Array.isArray(p.order))out.order=p.order.filter(function(x){return typeof x==='string';});
    }
    return out;
  }
  function bimPresData(){
    if(!A3D.pres||typeof A3D.pres!=='object'||!Array.isArray(A3D.pres.boards)||!Array.isArray(A3D.pres.order))A3D.pres=bimPresValid(A3D.pres);
    return A3D.pres;
  }
  function bimBoardById(id){var B=bimPresData().boards,i;for(i=0;i<B.length;i++)if(B[i].id===id)return B[i];return null;}
  /* the set in its order, [{t:'sheet',id,s} or {t:'board',id,b}]: each place the order gives a sheet
     is filled by the sheets in their own order; a sheet the order does not have yet comes last */
  function bimPresSeq(){
    var P=bimPresData(),B={},S={},used={},out=[],sh=A3D.sheets,i,id,k=0;
    P.boards.forEach(function(b){B[b.id]=b;});
    sh.forEach(function(s){S[s.id]=1;});
    for(i=0;i<P.order.length;i++){
      id=P.order[i];
      if(used[id])continue;
      if(B[id]){used[id]=1;out.push({t:'board',id:id,b:B[id]});}
      else if(S[id]){used[id]=1;out.push(null);}
    }
    for(i=0;i<out.length;i++)if(out[i]===null){out[i]={t:'sheet',id:sh[k].id,s:sh[k]};k++;}
    for(;k<sh.length;k++)out.push({t:'sheet',id:sh[k].id,s:sh[k]});
    P.boards.forEach(function(b){if(!used[b.id])out.push({t:'board',id:b.id,b:b});});
    return out;
  }
  function bimPresIndex(id){var Q=bimPresSeq(),i;for(i=0;i<Q.length;i++)if(Q[i].id===id)return i;return -1;}
  /* a new order for the set, as its ids: the sheets take the order they have in it. One undo step. */
  function bimPresSetOrder(Q){
    var S={},ord;
    A3D.sheets.forEach(function(s){S[s.id]=s;});
    ord=Q.filter(function(id){return S[id];}).map(function(id){return S[id];});
    if(ord.length!==A3D.sheets.length){console.warn('[BIM] A new order for the set left a sheet out; nothing was moved');return false;}
    pushUndo();
    A3D.sheets.length=0;ord.forEach(function(s){A3D.sheets.push(s);});
    bimPresData().order=Q.slice();
    refreshBrowser();bimSheetViewRefresh();saveSoon();bimPresPanelRefresh();
    return true;
  }
  /* dropped on a page, above or below its middle; with no board in the set, a sheet's move as ever */
  function bimPresMoveNear(id,targetId,after){
    if(!bimPresData().boards.length)return bimSheetMoveNear(id,targetId,after);
    var Q=bimPresSeq().map(function(e){return e.id;}),from=Q.indexOf(id),to=Q.indexOf(targetId);
    if(from<0||to<0)return false;
    if(after)to++;
    if(from<to)to--;
    if(to===from)return true;
    Q.splice(to,0,Q.splice(from,1)[0]);
    return bimPresSetOrder(Q);
  }
  /* a page one place earlier (-1) or later (+1) in the set */
  function bimPresStep(id,d){
    var Q=bimPresSeq().map(function(e){return e.id;}),i=Q.indexOf(id),j=i+d;
    if(i<0||j<0||j>=Q.length)return false;
    if(!bimPresData().boards.length)return bimSheetMove(id,j);
    Q.splice(j,0,Q.splice(i,1)[0]);
    return bimPresSetOrder(Q);
  }
  /* a board into the set, as its last page: one undo step; one of each kind */
  function bimBoardAdd(kind){
    if(!bimBoardName(kind)){a3dToast('There is no such board');return null;}
    var id='board-'+kind,P;
    if(bimBoardById(id))return id;
    pushUndo();
    P=bimPresData();
    P.order=bimPresSeq().map(function(e){return e.id;});
    P.boards.push({id:id,kind:kind});
    P.order.push(id);
    saveSoon();bimPresPanelRefresh();
    return id;
  }
  /* out of the set: one undo step. Its data stays in Analyze. */
  function bimBoardRemove(id){
    var b=bimBoardById(id),P;
    if(!b)return false;
    pushUndo();
    P=bimPresData();
    P.order=bimPresSeq().map(function(e){return e.id;}).filter(function(x){return x!==id;});
    P.boards=P.boards.filter(function(x){return x.id!==id;});
    if(A3D_CLB.open&&A3D_CLB.kind===b.kind)bimClbClose();
    saveSoon();bimPresPanelRefresh();
    a3dToast(bimBoardName(b.kind)+' is out of the set; its data stays in Analyze');
    return true;
  }
  /* a board's page in the main view, the panels beside it; on a phone or a tablet the drawer makes
     way for it */
  function bimPresOpenBoard(id){
    var b=bimBoardById(id);
    if(!b){a3dToast('That board is no longer in the set');return false;}
    bimClbOpen(b.kind);
    if(bimShellOverlay())bimShellDrawer(false);
    return true;
  }
  /* from Analyze, or a command: the board in the set if it is not, open, and its page shown in
     Presentation */
  function bimBoardShow(kind){
    if(!bimBoardName(kind)){a3dToast('There is no such board');return false;}
    var had=!!bimBoardById('board-'+kind),id=bimBoardAdd(kind);
    if(!id)return false;
    bimShellSetTab('presentation');
    if(!bimPresOpenBoard(id))return false;
    if(!had)a3dToast(bimBoardName(kind)+' is page '+(bimPresIndex(id)+1)+' of the set, in Presentation: it presents and prints with the sheets');
    return true;
  }
  function bimBoardMenu(btn){
    var r=btn.getBoundingClientRect();
    bimLtMenuOpen(r.left,r.bottom+4,bimBoards().map(function(x){return [x[1]+(bimBoardById('board-'+x[0])?' (in the set)':''),x[0]];}),function(k){bimBoardShow(k);});
    return true;
  }
  function bimBoardMenuItems(id){
    var i=bimPresIndex(id),n=bimPresSeq().length,it=[['Present from this page','present'],'-',['Open','open'],['Print…','print']];
    if(i>0||i<n-1)it.push('-');
    if(i>0)it.push(['Move up','earlier']);
    if(i>=0&&i<n-1)it.push(['Move down','later']);
    it.push('-',['Remove from the set','remove',true]);
    return it;
  }
  function bimBoardMenuDo(a,id){
    var b=bimBoardById(id);
    if(!b)return false;
    if(a==='present')return bimSlideshowStart(id);
    if(a==='open')return bimPresOpenBoard(id);
    if(a==='print')return bimClbPrint(b.kind);
    if(a==='earlier'||a==='later')return bimPresStep(id,a==='earlier'?-1:1);
    if(a==='remove')return bimBoardRemove(id);
    return false;
  }
  /* a board's markup for a kind, drawn for a phone or not, whatever is open */
  function bimBoardHtmlFor(kind,narrow){
    var k=A3D_CLB.kind,n=A3D_CLB.narrow,h;
    A3D_CLB.kind=kind;A3D_CLB.narrow=!!narrow;
    try{h=bimClbHtml();}finally{A3D_CLB.kind=k;A3D_CLB.narrow=n;}
    return h;
  }
  /* as it prints: wide, on paper */
  function bimBoardPrintHtml(kind){return '<div class="a3d-clb prt w-l">'+bimBoardHtmlFor(kind,false)+'</div>';}
  /* the boards' own style rules, out of this page's style sheet, for a print window or a thumbnail */
  var A3D_CLB_CSS='';
  function bimClbCss(){
    if(A3D_CLB_CSS)return A3D_CLB_CSS;
    var re=/a3d-(clb|acc-|zn-)/,out=[],i;
    function take(L){
      var s='',k,r,inner;
      for(k=0;k<L.length;k++){
        r=L[k];
        if(typeof r.selectorText==='string'){if(re.test(r.selectorText))s+=r.cssText;}
        else if(r.cssRules&&r.cssRules.length){inner=take(r.cssRules);if(inner)s+=r.cssText.slice(0,r.cssText.indexOf('{'))+'{'+inner+'}';}
      }
      return s;
    }
    for(i=0;i<document.styleSheets.length;i++){
      try{out.push(take(document.styleSheets[i].cssRules||[]));}
      catch(eC){console.warn('[BIM] A style sheet could not be read for the boards',eC);}
    }
    A3D_CLB_CSS=out.join('');
    return A3D_CLB_CSS;
  }
  /* a board alone, in a print window: A3 landscape, as Print set prints it */
  function bimClbPrint(kind){
    if(!bimBoardName(kind))kind=A3D_CLB.kind;
    var w=window.open('','_blank');
    if(!w){a3dToast('The print window was blocked -- allow pop-ups for this page and try again');return false;}
    try{
      w.document.write('<html><head><title>'+bimEsc(bimProjectLabel()+' - '+bimBoardName(kind))+'</title><style>'+bimClbCss()+
        '@page{size:420mm 297mm;margin:10mm}body{margin:0;background:#fff}</style></head><body>'+bimBoardPrintHtml(kind)+
        '<script>window.onload=function(){window.focus();window.print();};<\/script></body></html>');
      w.document.close();
    }catch(eW){console.warn('[BIM] The board could not be put in the print window',eW);a3dToast('The board could not be printed -- see the console');return false;}
    a3dToast('Printing '+bimBoardName(kind)+' -- Save as PDF in the print dialog makes a PDF');
    return true;
  }
  /* a board's thumbnail: the board as it prints, written into its frame when the model has moved
     and the board's markup with it */
  function bimPresBoardThumb(b,doc,key){
    try{
      var T=A3D_PRP.bthumbs[b.id];
      if(!T||T.key!==key)T=A3D_PRP.bthumbs[b.id]={key:key,html:bimBoardPrintHtml(b.kind)};
      if(doc.__prpHtml!==T.html){
        doc.open();
        doc.write('<!doctype html><html><head><meta charset="utf-8"><style>'+bimClbCss()+
          'html,body{margin:0;overflow:hidden;background:#fff}.a3d-clb.prt .a3d-clb-page{padding:28px 32px}</style></head><body>'+T.html+'</body></html>');
        doc.close();
        doc.__prpHtml=T.html;
      }
    }catch(eT){
      console.warn('[BIM] The thumbnail of the '+bimBoardName(b.kind)+' board could not be drawn',eT);
      a3dToast('A board thumbnail could not be drawn -- see the console');
    }
    doc.__prpKey=key;   /* drawn or failed, not tried again until the model moves */
  }
"""
rep("  /* ================= __acad3dV122: the Presentation panel =================\n",
    BOARDS + "  /* ================= __acad3dV122: the Presentation panel =================\n")
rep("  var A3D_PRP={thumbs:{},timer:null,edit:null,drag:null};\n",
    "  var A3D_PRP={thumbs:{},timer:null,edit:null,drag:null,bthumbs:{}};   /* __acad3dV162: the boards' thumbnails too */\n")

# ---- the panel: sheets and boards, in the set's order ----
span("  function bimPresPanelHtml(){\n", "    return h+'</div></div>';\n  }\n",
     r"""  function bimPresPanelHtml(){
    var Q=bimPresSeq(),n=Q.length,cur=A3D_CLB.open&&A3D_CLB.board?A3D_CLB.board:(bimSheetOnScreen()?A3D.activeSheetId:null),i,e,s,d,lab,h;   /* __acad3dV162 */
    h='<div class="a3d-prp"><div class="a3d-prphd"><span class="a3d-prpttl">Presentation</span>'+
      '<span class="a3d-prpcount">'+n+' page'+(n===1?'':'s')+'</span></div>'+
      '<div class="a3d-prpbar">'+
      '<button type="button" class="a3d-prpbtn pri" data-prpact="present"'+(n?'':' disabled')+
        ' title="'+(n?'Present the pages full screen, one at a time':'No pages to present yet')+'">Present</button>'+
      '<button type="button" class="a3d-prpbtn" data-prpact="new" title="A new sheet, the last page of the set">+ Page</button>'+
      '<button type="button" class="a3d-prpbtn" data-prpact="board" title="A board of the site analysis -- climate and risk, zoning and yield, access and people -- as a page of the set" aria-haspopup="menu">+ Board</button>'+
      '<button type="button" class="a3d-prpbtn" data-prpact="print"'+(n?'':' disabled')+
        ' title="'+(n?'Print every page in one go -- Save as PDF in the print dialog makes a PDF':'No pages to print yet')+'">Print set</button>'+
      '</div><div class="a3d-prplist" data-prplist="1">';
    if(!n)h+='<div class="a3d-prpempty">No pages yet. Every sheet is a page, in the order of the layout tabs; + Page makes the first. + Board adds a board of the site analysis.</div>';
    for(i=0;i<n;i++){
      e=Q[i];
      if(e.t==='board'){
        lab=bimBoardName(e.b.kind);
        h+='<div class="a3d-prpitem a3d-prpbrd'+(e.id===cur?' cur':'')+'" data-prpitem="'+bimEsc(e.id)+'" draggable="true" title="Page '+(i+1)+': the '+bimEsc(lab)+
          ' board -- click to open it, drag to move it, right-click for more">'+
          '<div class="a3d-prpthumb a3d-prpbthumb"><iframe data-prpbframe="'+bimEsc(e.id)+'" tabindex="-1" aria-hidden="true" title=""></iframe></div>'+
          '<div class="a3d-prpcap"><span class="a3d-prpno">'+(i+1)+'</span><span class="a3d-prpname">'+bimEsc(lab)+'</span><span class="a3d-prptag">Board</span></div></div>';
        continue;
      }
      s=e.s;d=bimPresThumbDims(s);lab=bimSheetLabel(s);
      h+='<div class="a3d-prpitem'+(s.id===cur?' cur':'')+'" data-prpitem="'+bimEsc(s.id)+'" draggable="true" title="Page '+(i+1)+': '+bimEsc(lab)+
        ' -- click to read it, double-click to edit its layout, drag to move it, right-click for more">'+
        '<div class="a3d-prpthumb"><canvas data-prpthumb="'+bimEsc(s.id)+'" width="'+d.W+'" height="'+d.H+'"></canvas></div>'+
        '<div class="a3d-prpcap"><span class="a3d-prpno">'+(i+1)+'</span>'+
        (A3D_PRP.edit===s.id?'<input type="text" class="a3d-prpren" data-prpren="'+bimEsc(s.id)+'" value="'+bimEsc(s.name||'')+'" aria-label="Sheet name">':
          '<span class="a3d-prpname" data-prpname="'+bimEsc(s.id)+'">'+bimEsc(lab)+'</span>')+
        '</div></div>';
    }
    return h+'</div></div>';
  }
""")
# the boards' frames, after the sheets' canvases, one per turn
rep("""      bimPresThumbDraw(s,cv,key);
      A3D_PRP.timer=setTimeout(bimPresThumbNext,0);
      return;
    }
  }
""", """      bimPresThumbDraw(s,cv,key);
      A3D_PRP.timer=setTimeout(bimPresThumbNext,0);
      return;
    }
    /* __acad3dV162: the boards' frames, scaled to the column, written when the model has moved */
    var F=host.querySelectorAll('iframe[data-prpbframe]'),fr,doc,b,k;
    for(id in A3D_PRP.bthumbs)if(A3D_PRP.bthumbs.hasOwnProperty(id)&&!bimBoardById(id))delete A3D_PRP.bthumbs[id];
    for(i=0;i<F.length;i++){
      fr=F[i];b=bimBoardById(fr.getAttribute('data-prpbframe'));
      if(!b)continue;
      k=(fr.parentNode.clientWidth||BIM_THUMB_CSS_W)/1280;
      fr.style.transform='scale('+k.toFixed(5)+')';
      if(!fr.__prpWired){fr.__prpWired=1;fr.addEventListener('load',bimPresThumbsQueue);}   /* a frame that loaded afresh is written again */
      doc=fr.contentDocument;
      key='brd|'+A3D_REV;
      if(!doc||doc.__prpKey===key)continue;
      r=fr.parentNode.getBoundingClientRect();
      if(r.bottom<pr.top-pr.height||r.top>pr.bottom+pr.height)continue;
      bimPresBoardThumb(b,doc,key);
      A3D_PRP.timer=setTimeout(bimPresThumbNext,0);
      return;
    }
  }
""")
rep("""  function bimPresOpenPage(id){
    if(!bimSheetById(id)){a3dToast('That page is no longer in the project');return false;}
""", """  function bimPresOpenPage(id){
    if(bimBoardById(id))return bimPresOpenBoard(id);   /* __acad3dV162 */
    if(!bimSheetById(id)){a3dToast('That page is no longer in the project');return false;}
    if(A3D_CLB.open)bimClbClose();
""")
rep("""  function bimPresAct(a){
    if(a==='present')return bimSlideshowStart(bimSheetOnScreen()?A3D.activeSheetId:(A3D.sheets[0]&&A3D.sheets[0].id));
""", """  function bimPresAct(a,btn){
    var Q;
    if(a==='present'){   /* __acad3dV162: from the page on screen, a board's or a sheet's, or the first */
      Q=bimPresSeq();
      return bimSlideshowStart(A3D_CLB.open&&A3D_CLB.board?A3D_CLB.board:(bimSheetOnScreen()?A3D.activeSheetId:(Q[0]&&Q[0].id)));
    }
    if(a==='board')return btn?bimBoardMenu(btn):false;
""")
rep("        if((b=t.closest('[data-prpact]'))){if(!b.disabled)bimPresAct(b.getAttribute('data-prpact'));return;}\n",
    "        if((b=t.closest('[data-prpact]'))){if(!b.disabled)bimPresAct(b.getAttribute('data-prpact'),b);return;}\n")
rep("        if((it=t.closest('[data-prpitem]')))bimPresEditLayout(it.getAttribute('data-prpitem'));\n",
    "        if((it=t.closest('[data-prpitem]'))){if(bimBoardById(it.getAttribute('data-prpitem')))bimPresOpenBoard(it.getAttribute('data-prpitem'));else bimPresEditLayout(it.getAttribute('data-prpitem'));}\n")
rep("      bimSheetMenu(ev,it.getAttribute('data-prpitem'),'pages');\n",
    "      var bid=it.getAttribute('data-prpitem');   /* __acad3dV162: a board's page has its own menu */\n"
    "      if(bimBoardById(bid)){bimLtMenuOpen(ev.clientX,ev.clientY,bimBoardMenuItems(bid),function(a){bimBoardMenuDo(a,bid);});return;}\n"
    "      bimSheetMenu(ev,it.getAttribute('data-prpitem'),'pages');\n")
rep("      try{bimSheetMoveNear(id,it.getAttribute('data-prpitem'),ev.clientY>r.top+r.height/2);}\n",
    "      try{bimPresMoveNear(id,it.getAttribute('data-prpitem'),ev.clientY>r.top+r.height/2);}   /* __acad3dV162: in the set, boards and all */\n")
rep("    var i=bimSheetIndex(id),n=A3D.sheets.length,pg=(where==='pages'),it=[];\n",
    "    var pg=(where==='pages'),i=pg?bimPresIndex(id):bimSheetIndex(id),n=pg?bimPresSeq().length:A3D.sheets.length,it=[];   /* __acad3dV162: a page's place is in the set */\n")
rep("    if(a==='earlier'||a==='later')return bimSheetMove(id,bimSheetIndex(id)+(a==='earlier'?-1:1));\n",
    "    if(a==='earlier'||a==='later')return where==='pages'?bimPresStep(id,a==='earlier'?-1:1):bimSheetMove(id,bimSheetIndex(id)+(a==='earlier'?-1:1));\n")

# ================= Present: the set, boards and all =================
rep("""    ov.addEventListener('wheel',function(ev){
      ev.preventDefault();
""", """    ov.addEventListener('wheel',function(ev){
      var bd=ev.target&&ev.target.closest?ev.target.closest('.a3d-ssboard'):null;   /* __acad3dV162: a board scrolls, to its end */
      if(bd&&ev.deltaY&&(ev.deltaY>0?bd.scrollTop+bd.clientHeight<bd.scrollHeight-1:bd.scrollTop>0))return;
      ev.preventDefault();
""")
rep("""    if(!A3D.sheets.length){a3dToast('There are no pages to present yet: every sheet is a page');return false;}
    var idx=0,i,ov;
    for(i=0;i<A3D.sheets.length;i++)if(A3D.sheets[i].id===fromId){idx=i;break;}
""", """    var Q=bimPresSeq(),idx=0,i,ov;   /* __acad3dV162: the set, boards and all */
    if(!Q.length){a3dToast('There are no pages to present yet: every sheet is a page');return false;}
    for(i=0;i<Q.length;i++)if(Q[i].id===fromId){idx=i;break;}
""")
rep("""    A3D_SLIDESHOW.from={kind:A3D_VIEW.kind,id:A3D_VIEW.id};
""", """    A3D_SLIDESHOW.from={kind:A3D_VIEW.kind,id:A3D_VIEW.id,board:A3D_CLB.open?A3D_CLB.kind:null};
    if(A3D_CLB.open)bimClbClose();   /* one board on the screen: Present's */
""")
rep("""    var ov=A3D_SLIDESHOW.el,n=A3D.sheets.length,i=A3D_SLIDESHOW.idx;
    if(!ov)return;
""", """    var ov=A3D_SLIDESHOW.el,n=bimPresSeq().length,i=A3D_SLIDESHOW.idx;
    if(!ov)return;
""")
rep("""    var n=A3D.sheets.length;
    if(!n){bimSlideshowEnd();return;}
    if(A3D_SLIDESHOW.idx>n-1)A3D_SLIDESHOW.idx=n-1;
    var s=A3D.sheets[A3D_SLIDESHOW.idx],ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv;
""", """    var Q=bimPresSeq(),n=Q.length;
    if(!n){bimSlideshowEnd();return;}
    if(A3D_SLIDESHOW.idx>n-1)A3D_SLIDESHOW.idx=n-1;
    var e=Q[A3D_SLIDESHOW.idx];
    if(e.t==='board'){bimSlideshowBoard(e);bimSlideshowBar();bimSlideshowAhead(A3D_SLIDESHOW.idx+1);return;}   /* __acad3dV162 */
    bimSlideshowBoard(null);
    var s=e.s,ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv;
""")
rep("""  function bimSlideshowAhead(i){
    setTimeout(function(){
      if(!A3D_SLIDESHOW.on||i>=A3D.sheets.length)return;
      var s=A3D.sheets[i],ov=A3D_SLIDESHOW.el,vw=ov.clientWidth||window.innerWidth,vh=ov.clientHeight||window.innerHeight;
""", """  /* __acad3dV162: a board's page in Present: the board as on screen, over the black, scrolled with the
     wheel or a finger; the canvas stands aside */
  function bimSlideshowBoard(e){
    var ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv,bd=ov?ov.querySelector('.a3d-ssboard'):null,w,sig;
    if(!ov)return;
    if(!e){if(bd)bd.parentNode.removeChild(bd);cv.style.display='';return;}
    cv.style.display='none';
    cv.setAttribute('data-sspage',e.id);cv.removeAttribute('data-sskey');
    if(!bd){bd=document.createElement('div');bd.setAttribute('role','document');ov.insertBefore(bd,cv.nextSibling);bimClbWire(bd);}
    w=ov.clientWidth||window.innerWidth;
    bd.className='a3d-clb a3d-ssboard'+bimClbWidthCls(w);
    bd.setAttribute('data-sspage',e.id);
    bd.setAttribute('aria-label',bimBoardName(e.b.kind)+' board');
    sig=e.b.kind+'|'+A3D_REV+'|'+(w<760);
    if(bd.getAttribute('data-sssig')!==sig){
      bd.innerHTML=bimBoardHtmlFor(e.b.kind,w<760)+'<div class="a3d-clb-tip" role="tooltip" hidden></div>';
      bd.setAttribute('data-sssig',sig);bd.scrollTop=0;
    }
    A3D_SLIDESHOW.scale=0;
  }
  function bimSlideshowAhead(i){
    setTimeout(function(){
      var Q=bimPresSeq();
      if(!A3D_SLIDESHOW.on||i>=Q.length||Q[i].t!=='sheet')return;   /* __acad3dV162: a board is not drawn ahead */
      var s=Q[i].s,ov=A3D_SLIDESHOW.el,vw=ov.clientWidth||window.innerWidth,vh=ov.clientHeight||window.innerHeight;
""")
rep("""    if(!A3D_SLIDESHOW.on)return false;
    var n=A3D.sheets.length;
    i=Math.max(0,Math.min(n-1,i));
""", """    if(!A3D_SLIDESHOW.on)return false;
    var n=bimPresSeq().length;
    i=Math.max(0,Math.min(n-1,i));
""")
rep("    if(act==='last')return bimSlideshowGo(A3D.sheets.length-1);\n",
    "    if(act==='last')return bimSlideshowGo(bimPresSeq().length-1);\n")
rep("""    if(!A3D_SLIDESHOW.on)return false;
    var s=A3D.sheets[A3D_SLIDESHOW.idx],from=A3D_SLIDESHOW.from||{},ov=A3D_SLIDESHOW.el;
""", """    if(!A3D_SLIDESHOW.on)return false;
    var e=bimPresSeq()[A3D_SLIDESHOW.idx]||null,s=e&&e.t==='sheet'?e.s:null,from=A3D_SLIDESHOW.from||{},ov=A3D_SLIDESHOW.el;
    bimSlideshowBoard(null);
""")
rep("""    A3D_SLIDESHOW.fs=false;
    if(s&&from.kind==='sheet'&&bimSheetOnScreen()){
""", """    A3D_SLIDESHOW.fs=false;
    if(e&&e.t==='board'){bimClbOpen(e.b.kind);return true;}   /* __acad3dV162: back on the board last shown */
    if(s&&from.board){bimActivateView('sheet',s.id);return true;}   /* started on a board: to the sheet last shown */
    if(s&&from.kind==='sheet'&&bimSheetOnScreen()){
""")

# ================= Print set: the set, boards and all =================
span("  function bimPrintSetHtml(){\n", "    return {html:html,bad:bad,n:n};\n  }\n",
     r"""  function bimPrintSetHtml(){
    var Q=bimPresSeq(),n=Q.length,mode=A3D.presentMode?'presentation':'technical',sizes={},css='',body='',bad=[],lost=[],i,e,s,nm,svg,cv,first=true,brd=false;   /* __acad3dV162 */
    for(i=0;i<n;i++){
      e=Q[i];
      if(e.t==='board'){   /* __acad3dV162: a board on A3 landscape pages of its own, as it prints alone */
        if(!brd){brd=true;css+='@page a3dbrd{size:420mm 297mm;margin:10mm}';}
        try{body+='<div class="a3dbrd" data-page="'+bimEsc(e.id)+'" style="page:a3dbrd">'+bimBoardPrintHtml(e.b.kind)+'</div>';}
        catch(eB){
          console.warn('[BIM] Page '+(i+1)+', the '+bimBoardName(e.b.kind)+' board, could not be put together',eB);
          lost.push(i+1);
          body+='<div class="a3dbrd" data-page="'+bimEsc(e.id)+'"><div class="a3dpgerr">Page '+(i+1)+' ('+bimEsc(bimBoardName(e.b.kind))+') could not be drawn</div></div>';
        }
        continue;
      }
      s=e.s;
      nm='a3dsz'+String(s.w.toFixed(1)+'x'+s.h.toFixed(1)).replace(/[^0-9x]/g,'_');
      if(!sizes[nm]){
        sizes[nm]=1;
        if(first)css+='@page{size:'+s.w+'mm '+s.h+'mm;margin:0}';
        css+='@page '+nm+'{size:'+s.w+'mm '+s.h+'mm;margin:0}';
      }
      first=false;
      try{svg=bimBuildSheetSVG(s,mode);}
      catch(eS){
        console.warn('[BIM] Page '+(i+1)+' could not be built as a vector drawing; it is printed from its image',eS);
        bad.push(i+1);
        try{
          cv=bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,document.createElement('canvas'),SHEET_EXPORT_PXMM/SHEET_PREVIEW_PXMM);
          svg='<img alt="" src="'+cv.toDataURL('image/png')+'">';
        }catch(eR){
          console.warn('[BIM] Page '+(i+1)+' could not be drawn at all',eR);
          svg='<div class="a3dpgerr">Page '+(i+1)+' ('+bimEsc(bimSheetLabel(s))+') could not be drawn</div>';
        }
      }
      body+='<div class="a3dpg" data-page="'+bimEsc(s.id)+'" style="page:'+nm+';width:'+s.w+'mm;height:'+s.h+'mm">'+svg+'</div>';
    }
    if(brd)css+=bimClbCss()+'.a3dbrd{break-after:page;page-break-after:always}.a3dbrd:last-child{break-after:auto;page-break-after:auto}';
    var html='<html><head><title>'+bimEsc(bimProjectLabel())+' - '+n+' page'+(n===1?'':'s')+'</title><style>'+css+
      'body{margin:0}.a3dpg{break-after:page;page-break-after:always;overflow:hidden}.a3dpg:last-child{break-after:auto;page-break-after:auto}'+
      '.a3dpg svg,.a3dpg img{width:100%;height:100%;display:block}.a3dpgerr{padding:20mm;font:14pt sans-serif;color:#c33}'+
      '</style></head><body>'+body+'<script>window.onload=function(){window.focus();window.print();};<\/script></body></html>';
    return {html:html,bad:bad,lost:lost,n:n};
  }
""")
rep("    if(!A3D.sheets.length){a3dToast('There are no pages to print yet: every sheet is a page');return false;}\n",
    "    if(!bimPresSeq().length){a3dToast('There are no pages to print yet: every sheet is a page');return false;}   /* __acad3dV162: a board is one too */\n")
rep("    if(r.bad.length)a3dToast(",
    "    if(r.lost&&r.lost.length)a3dToast('Page'+(r.lost.length>1?'s ':' ')+r.lost.join(', ')+' could not be drawn -- see the console');   /* __acad3dV162 */\n    else if(r.bad.length)a3dToast(")

# ================= hooks =================
rep("""      items.push({id:id,no:no?no.textContent:null,name:nm?nm.textContent:null,cur:it.classList.contains('cur'),w:cv?cv.width:0,h:cv?cv.height:0,
        drawn:!!(cv&&s&&cv.__prpKey===bimPageSig(s)+'|'+cv.width+'x'+cv.height)});
    });
    return {open:!!host,count:A3D.sheets.length,items:items,edit:A3D_PRP.edit,""",
    """      var fr=it.querySelector('iframe[data-prpbframe]'),bd=bimBoardById(id),fd=fr&&fr.contentDocument;   /* __acad3dV162: a board's page */
      items.push({id:id,no:no?no.textContent:null,name:nm?nm.textContent:null,cur:it.classList.contains('cur'),w:cv?cv.width:0,h:cv?cv.height:0,
        drawn:bd?!!(fd&&fd.__prpKey==='brd|'+A3D_REV&&fd.querySelector('.a3d-clb.prt')):!!(cv&&s&&cv.__prpKey===bimPageSig(s)+'|'+cv.width+'x'+cv.height),
        board:bd?bd.kind:null,scale:fr?fr.style.transform:null,thumbTitle:fd&&fd.querySelector('.a3d-clb-h1')?fd.querySelector('.a3d-clb-h1').textContent:null});
    });
    return {open:!!host,count:bimPresSeq().length,items:items,edit:A3D_PRP.edit,""")
rep("""    var ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv,s=A3D.sheets[A3D_SLIDESHOW.idx]||null;
    return {on:A3D_SLIDESHOW.on,idx:A3D_SLIDESHOW.idx,id:s?s.id:null,n:A3D.sheets.length,fs:A3D_SLIDESHOW.fs,""",
    """    var ov=A3D_SLIDESHOW.el,cv=A3D_SLIDESHOW.cv,Q=bimPresSeq(),e=Q[A3D_SLIDESHOW.idx]||null,s=e&&e.t==='sheet'?e.s:null,bd=ov?ov.querySelector('.a3d-ssboard'):null;   /* __acad3dV162 */
    return {on:A3D_SLIDESHOW.on,idx:A3D_SLIDESHOW.idx,id:e?e.id:null,n:Q.length,fs:A3D_SLIDESHOW.fs,board:e&&e.t==='board'?e.b.kind:null,
      boardShown:bd?bd.getAttribute('data-sspage'):null,boardTitle:bd&&bd.querySelector('.a3d-clb-h1')?bd.querySelector('.a3d-clb-h1').textContent:null,
      canvasShown:!!(cv&&cv.style.display!=='none'),""")
rep("  window.__a3dSlideshowStart=function(id){return bimSlideshowStart(id);};\n",
    "  window.__a3dSlideshowStart=function(id){return bimSlideshowStart(id);};\n"
    "  /* __acad3dV162: the boards as pages of the set */\n"
    "  window.__a3dPresSeq=function(){return bimPresSeq().map(function(e){return {id:e.id,t:e.t,kind:e.t==='board'?e.b.kind:null};});};\n"
    "  window.__a3dPresRecord=function(){return JSON.parse(JSON.stringify(bimPresData()));};\n"
    "  window.__a3dBoardAdd=function(k){return bimBoardAdd(k);};\n"
    "  window.__a3dBoardRemove=function(id){return bimBoardRemove(id);};\n"
    "  window.__a3dBoardShow=function(k){return bimBoardShow(k);};\n"
    "  window.__a3dPresOpen=function(id){return bimPresOpenPage(id);};\n"
    "  window.__a3dPresMoveNear=function(id,t,after){return bimPresMoveNear(id,t,!!after);};\n"
    "  window.__a3dPresStep=function(id,d){return bimPresStep(id,d);};\n"
    "  window.__a3dBoardMenuItems=function(id){return bimBoardMenuItems(id).map(function(x){return x==='-'?'-':x[0];});};\n"
    "  window.__a3dBoardMenuDo=function(a,id){return bimBoardMenuDo(a,id);};\n"
    "  window.__a3dBoardPrintHtml=function(k){return bimBoardPrintHtml(k);};\n"
    "  window.__a3dPrintSetHtml=function(){return bimPrintSetHtml();};\n"
    "  window.__a3dClbCss=function(){return bimClbCss();};\n"
    "  window.__a3dClbState=function(){var b=bimClbEl();return {open:A3D_CLB.open,kind:A3D_CLB.kind,board:A3D_CLB.board,narrow:A3D_CLB.narrow,"
    "inView:!!(b&&b.parentNode&&b.parentNode.classList&&b.parentNode.classList.contains('a3d-vp')),cls:b?b.className:null,w:b?bimClbW(b):0};};\n")

rep("  window.__acad3dV161='accessfetch,", "  window.__acad3dV162='oneanalyze,categories,modelgroup,onesearch,heldrefresh,boardpages,boardorder,boardthumbs,boardinview,boardwidth,boardpresent,boardprint,printset';\n  window.__acad3dV161='accessfetch,")

# ================= version =================
rep("  var BIM_APP_VERSION={v:'V161',date:'2026-10-10'};   /* __acad3dV161 */\n",
    "  var BIM_APP_VERSION={v:'V162',date:'2026-10-10'};   /* __acad3dV162 */\n")

if t.count('__acad3dV162') < 40:
    sys.exit('ABORT: markers %d' % t.count('__acad3dV162'))
P.write_bytes(t.encode('utf-8'))
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(t.encode('utf-8')), hashlib.sha256(t.encode('utf-8')).hexdigest()))
