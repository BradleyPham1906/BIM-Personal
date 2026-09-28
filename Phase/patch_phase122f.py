"""patch_phase122f.py -- V122: the Presentation panel, second in the left panel's stack.

The owner's stack for the left panel, V119: "1. layers ... 2. Need a presentation for doing
presentation with clients. using layout spaces, with multi pages view like a pdf viewer." V121 built
the first; this is the second, on the rail under Layers.

The panel is the presentation's page list, the thumbnail column of a PDF reader: every sheet in the
project's order, each a small picture of the page as it plots, numbered, with its name. From it:

  - Present, from the page on screen, or from the first when the model is on screen (V122d);
  - + Page, a new sheet at the end of the set, opened (the layout tabs' +);
  - Print set, every page in one print job (V122e);
  - a click on a page opens it in the Pages display (V122c), a double-click opens its layout to edit,
    a double-click on its name renames it;
  - a page is dragged to a new place in the set, or moved one place up or down from its menu.

The order is the one order the app has, A3D.sheets: the layout tabs, the Project Browser's Sheets,
the pages, Present and the printed set all read it, so moving a page moves its tab. A move is one undo
step, like a rename.

Three things are made one where they were two:
  - a sheet's rename: the layout tab did it inline in its own code; bimSheetRename is the one path,
    taken by the tab and the page alike.
  - a sheet's menu: the layout tab's items are bimSheetMenuItems, which the page's menu reads too; the
    page's adds Present from this page. Both gain the move, as Move left / Move right on a tab.
  - where a page's picture comes from: a thumbnail is the page drawn by the same renderer as the
    Pages display and Present, at twice its pixels and reduced, redrawn when the model's revision,
    the appearance, the sheet or the title block move -- and only when it is in view in the panel."""
NAME = 'patch_phase122f.py'
BASE = 'a63c75426989d1ecec74ba63c778d0577094a11a911069a1644392f5c0df1410'
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

# ---- the rail: Presentation under Layers
rep("""    assets:'<path d="m9 2 1.8 4.2L15 8l-4.2 1.8L9 14l-1.8-4.2L3 8l4.2-1.8z"/>'
""", """    /* __acad3dV122: a screen on a stand with a play mark, the Presentation tab */
    presentation:'<rect x="2.5" y="2.5" width="13" height="9.5" rx="1.5"/><path d="M7.6 5.2v4.1l3.4-2.05z"/><path d="M9 12v3.2M6.2 15.5h5.6"/>',
    assets:'<path d="m9 2 1.8 4.2L15 8l-4.2 1.8L9 14l-1.8-4.2L3 8l4.2-1.8z"/>'
""")
rep("""      bimRailIcon('layers')+'</button>'+
""", """      bimRailIcon('layers')+'</button>'+
      '<button type="button" class="a3d-railbtn" data-tab="presentation" title="Presentation" aria-label="Presentation">'+   /* __acad3dV122 */
      bimRailIcon('presentation')+'</button>'+
""")
rep("""    bimWireLayersPanel(sh.querySelector('#a3d-leftpanel'));   /* __acad3dV121 */
""", """    bimWireLayersPanel(sh.querySelector('#a3d-leftpanel'));   /* __acad3dV121 */
    bimWirePresPanel(sh.querySelector('#a3d-leftpanel'));     /* __acad3dV122 */
""")
rep("""    {sel:'.a3d-railbtn[data-tab="browser"]',why:'Project Browser tab'},
""", """    {sel:'.a3d-railbtn[data-tab="browser"]',why:'Project Browser tab'},
    /* __acad3dV122: the Presentation panel -- each driven by the V122 suite before it was claimed */
    {sel:'.a3d-railbtn[data-tab="presentation"]',why:'Presentation tab: the pages in order, to read, reorder, present and print'},
    {sel:'[data-prpact]',why:'Presentation panel action: present, a new page, print the set'},
    {sel:'[data-prpitem]',why:'a page: click to read it, double-click to edit its layout, drag to move it, right-click for its menu'},
    {sel:'[data-prpren]',why:'the name of a page being renamed'},
""")

# ---- the shell's render pass builds the panel on its tab
rep("""    if(shell.dataset.tab==='assets'&&!panel.querySelector('.a3d-assets')){
""", """    if(shell.dataset.tab==='presentation'&&!panel.querySelector('.a3d-pres-wrap')){   /* __acad3dV122 */
      var pbox=document.createElement('div');
      pbox.className='a3d-tabbody a3d-pres-wrap';
      pbox.innerHTML=bimPresPanelHtml();
      panel.appendChild(pbox);
      bimPresThumbsQueue();
      did=true;
    }
    if(shell.dataset.tab!=='presentation'){
      var pstale=panel.querySelector('.a3d-pres-wrap');
      if(pstale){pstale.parentNode.removeChild(pstale);A3D_PRP.edit=null;did=true;}
    }
    if(shell.dataset.tab==='assets'&&!panel.querySelector('.a3d-assets')){
""")

# ---- the list of sheets changed: the panel follows, as the layout tabs do
rep("""    /* a sheet renamed while it is open renames the view it is -- __acad3dV119: and every view's
       record is held to what it names */
    bimViewSync();
  }
""", """    /* a sheet renamed while it is open renames the view it is -- __acad3dV119: and every view's
       record is held to what it names */
    bimViewSync();
    bimPresPanelRefresh();   /* __acad3dV122: the pages are the same list */
  }
""")
rep("""      try{if(bimPagesOn())bimPagesQueue();}
""", """      try{if(bimPagesOn())bimPagesQueue();bimPresThumbsQueue();}   /* __acad3dV122: and the thumbnails */
""")

# ---- one rename
rep("""      var v=String(inp.value).trim();
      if(keep&&v&&v!==sh.name&&bimSheetById(id)){
        pushUndo();
        sh.name=v;
        refreshBrowser();bimSheetViewRefresh();saveSoon();
      }
      A3D_LT_HTML='';bimRenderLayoutTabs();
""", """      if(keep)bimSheetRename(id,inp.value);   /* __acad3dV122: the one path, the page's too */
      A3D_LT_HTML='';bimRenderLayoutTabs();
""")

# ---- one menu
rep("""    bimLtMenuOpen(ev.clientX,ev.clientY,[['New sheet','new'],['Rename','rename'],['Delete','del',true],'-',
      ['Sheet setup\\u2026','setup'],['Plot\\u2026','plot']],function(a){
      if(a==='new')bimLayoutNew();
      else if(a==='rename')bimLayoutRename(id);
      else if(a==='del')bimConfirmDeleteSheet(id);
      else if(a==='setup'){if(bimActivateView('sheet',id))bimOpenSheetPropsDlg();}
      else if(a==='plot'){if(bimActivateView('sheet',id))bimPrintSheet();}
    });
  }
""", """    bimSheetMenu(ev,id,'tabs');   /* __acad3dV122: the items the page's menu reads too */
  }
  /* ================= __acad3dV122: a sheet's order, name and menu, one of each =================
     A3D.sheets is the one order: the layout tabs, the Project Browser's Sheets, the pages, Present
     and the printed set all read it. */
  function bimSheetIndex(id){
    var i;
    for(i=0;i<A3D.sheets.length;i++)if(A3D.sheets[i].id===id)return i;
    return -1;
  }
  /* to a place in the order, from 0. One undo step. */
  function bimSheetMove(id,to){
    var i=bimSheetIndex(id),n=A3D.sheets.length;
    if(i<0){a3dToast('That sheet is no longer in the project');return false;}
    if(!isFinite(+to)){console.warn('[BIM] Not a place in the set of sheets: '+to);a3dToast('That is not a place in the set');return false;}
    to=Math.max(0,Math.min(n-1,Math.round(+to)));
    if(to===i)return true;
    pushUndo();
    A3D.sheets.splice(to,0,A3D.sheets.splice(i,1)[0]);
    refreshBrowser();bimSheetViewRefresh();saveSoon();
    return true;
  }
  /* dropped on a page, above or below its middle */
  function bimSheetMoveNear(id,targetId,after){
    var from=bimSheetIndex(id),to=bimSheetIndex(targetId);
    if(from<0||to<0)return false;
    if(after)to++;
    if(from<to)to--;
    return bimSheetMove(id,to);
  }
  /* a sheet's name, from its layout tab or its page. One undo step; an empty name, or the same one,
     changes nothing. */
  function bimSheetRename(id,v){
    var sh=bimSheetById(id);
    v=String(v==null?'':v).trim();
    if(!sh||!v||v===sh.name)return false;
    pushUndo();
    sh.name=v;
    refreshBrowser();bimSheetViewRefresh();saveSoon();
    return true;
  }
  /* the menu of a sheet: 'tabs' for a layout tab, 'pages' for a page in the Presentation panel */
  function bimSheetMenuItems(id,where){
    var i=bimSheetIndex(id),n=A3D.sheets.length,pg=(where==='pages'),it=[];
    if(pg)it.push(['Present from this page','present'],'-');
    it.push(['New sheet','new'],['Rename','rename'],['Delete','del',true],'-');
    if(i>0)it.push([pg?'Move up':'Move left','earlier']);
    if(i>=0&&i<n-1)it.push([pg?'Move down':'Move right','later']);
    if(n>1)it.push('-');
    it.push(['Sheet setup\\u2026','setup'],['Plot\\u2026','plot']);
    return it;
  }
  function bimSheetMenu(ev,id,where){
    bimLtMenuOpen(ev.clientX,ev.clientY,bimSheetMenuItems(id,where),function(a){bimSheetMenuDo(a,id,where);});
  }
  function bimSheetMenuDo(a,id,where){
    if(a==='new')return bimLayoutNew();
    if(a==='rename')return (where==='pages')?bimPresRename(id):bimLayoutRename(id);
    if(a==='del')return bimConfirmDeleteSheet(id);
    if(a==='earlier'||a==='later')return bimSheetMove(id,bimSheetIndex(id)+(a==='earlier'?-1:1));
    if(a==='setup'){if(bimActivateView('sheet',id))bimOpenSheetPropsDlg();return true;}
    if(a==='plot'){if(bimActivateView('sheet',id))bimPrintSheet();return true;}
    if(a==='present')return bimSlideshowStart(id);
    return false;
  }
  /* ================= __acad3dV122: the Presentation panel =================
     The presentation's pages, the thumbnail column of a PDF reader. A thumbnail is the page as it
     plots, drawn by the renderer the pages and Present use, at twice its pixels and reduced. */
  var A3D_PRP={thumbs:{},timer:null,edit:null,drag:null};
  var BIM_THUMB_CSS_W=206;   /* the panel's width less its padding */
  function bimPresThumbDims(s){
    var W=Math.max(1,Math.round(BIM_THUMB_CSS_W*bimDevicePixelRatio()));
    return {W:W,H:Math.max(1,Math.round(W*s.h/s.w))};
  }
  function bimPresPanelHtml(){
    var n=A3D.sheets.length,cur=bimSheetOnScreen()?A3D.activeSheetId:null,i,s,d,lab,h;
    h='<div class="a3d-prp"><div class="a3d-prphd"><span class="a3d-prpttl">Presentation</span>'+
      '<span class="a3d-prpcount">'+n+' page'+(n===1?'':'s')+'</span></div>'+
      '<div class="a3d-prpbar">'+
      '<button type="button" class="a3d-prpbtn pri" data-prpact="present"'+(n?'':' disabled')+
        ' title="'+(n?'Present the pages full screen, one at a time':'No pages to present yet')+'">Present</button>'+
      '<button type="button" class="a3d-prpbtn" data-prpact="new" title="A new sheet, the last page of the set">+ Page</button>'+
      '<button type="button" class="a3d-prpbtn" data-prpact="print"'+(n?'':' disabled')+
        ' title="'+(n?'Print every page in one go -- Save as PDF in the print dialog makes a PDF':'No pages to print yet')+'">Print set</button>'+
      '</div><div class="a3d-prplist" data-prplist="1">';
    if(!n)h+='<div class="a3d-prpempty">No pages yet. Every sheet is a page, in the order of the layout tabs; + Page makes the first.</div>';
    for(i=0;i<n;i++){
      s=A3D.sheets[i];d=bimPresThumbDims(s);lab=bimSheetLabel(s);
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
  function bimPresHost(){return document.querySelector('#a3d-leftpanel .a3d-pres-wrap');}
  function bimPresPanelRefresh(){
    var host=bimPresHost();
    if(!host||A3D_PRP.edit)return false;   /* not under a name being typed; it refreshes when that ends */
    bimRenderInto(host,bimPresPanelHtml());
    bimPresThumbsQueue();
    return true;
  }
  function bimPresThumbsQueue(){
    if(!A3D_PRP.timer)A3D_PRP.timer=setTimeout(bimPresThumbNext,0);
  }
  /* A thumbnail already drawn at this key goes back in at once; one that is not is drawn, one per
     turn of the event loop, and only for pages in view in the panel or within a panel's height. */
  function bimPresThumbNext(){
    A3D_PRP.timer=null;
    var host=bimPresHost(),panel=document.getElementById('a3d-leftpanel');
    if(!host||!panel)return;
    var pr=panel.getBoundingClientRect(),cvs=host.querySelectorAll('canvas[data-prpthumb]'),i,cv,s,key,t,r,id,live={};
    for(i=0;i<A3D.sheets.length;i++)live[A3D.sheets[i].id]=1;
    for(id in A3D_PRP.thumbs)if(A3D_PRP.thumbs.hasOwnProperty(id)&&!live[id])delete A3D_PRP.thumbs[id];
    for(i=0;i<cvs.length;i++){
      cv=cvs[i];s=bimSheetById(cv.getAttribute('data-prpthumb'));
      if(!s)continue;
      key=bimPageSig(s)+'|'+cv.width+'x'+cv.height;
      if(cv.__prpKey===key)continue;
      t=A3D_PRP.thumbs[s.id];
      if(t&&t.key===key){bimThumbBlit(cv,t.cv);cv.__prpKey=key;continue;}
      r=cv.getBoundingClientRect();
      if(r.bottom<pr.top-pr.height||r.top>pr.bottom+pr.height)continue;
      bimPresThumbDraw(s,cv,key);
      A3D_PRP.timer=setTimeout(bimPresThumbNext,0);
      return;
    }
  }
  function bimThumbBlit(dst,src){
    var x=dst.getContext('2d');
    x.setTransform(1,0,0,1,0,0);x.clearRect(0,0,dst.width,dst.height);
    x.drawImage(src,0,0,dst.width,dst.height);
  }
  function bimPresThumbDraw(s,cv,key){
    try{
      var big=document.createElement('canvas'),c=document.createElement('canvas'),x;
      bimRenderSheet(s,SHEET_PREVIEW_PXMM,true,big,cv.width*2/(s.w*SHEET_PREVIEW_PXMM));
      c.width=cv.width;c.height=cv.height;
      x=c.getContext('2d');x.imageSmoothingEnabled=true;x.imageSmoothingQuality='high';
      x.drawImage(big,0,0,c.width,c.height);
      A3D_PRP.thumbs[s.id]={key:key,cv:c};
      bimThumbBlit(cv,c);
    }catch(eT){
      console.warn('[BIM] The thumbnail of '+bimSheetLabel(s)+' could not be drawn',eT);
      a3dToast('A page thumbnail could not be drawn -- see the console');
    }
    cv.__prpKey=key;   /* drawn or failed, not tried again until something changes */
  }
  /* a page opened from the panel is read in the Pages display: on paper already, it is scrolled to */
  function bimPresOpenPage(id){
    if(!bimSheetById(id)){a3dToast('That page is no longer in the project');return false;}
    if(bimSheetOnScreen()&&A3D_PAGES.display==='pages'){
      if(id!==A3D.activeSheetId)bimPagesSetCurrent(id);
      return bimPagesScrollTo(id);
    }
    bimPagesSetDisplay('pages');
    return bimActivateView('sheet',id);
  }
  function bimPresEditLayout(id){
    if(!bimSheetById(id))return false;
    bimPagesSetDisplay('layout');
    return bimActivateView('sheet',id);
  }
  function bimPresAct(a){
    if(a==='present')return bimSlideshowStart(bimSheetOnScreen()?A3D.activeSheetId:(A3D.sheets[0]&&A3D.sheets[0].id));
    if(a==='new')return bimLayoutNew();
    if(a==='print')return bimPrintSet();
    return false;
  }
  function bimPresRename(id){
    var host=bimPresHost(),inp;
    if(!host||!bimSheetById(id))return false;
    A3D_PRP.edit=id;
    bimRenderInto(host,bimPresPanelHtml());
    inp=host.querySelector('[data-prpren]');
    if(inp){try{inp.focus();inp.select();}catch(eF){console.warn('[BIM] The page name field could not take the focus',eF);}}
    return !!inp;
  }
  function bimPresEndRename(inp,cancel){
    var id=inp.getAttribute('data-prpren');
    if(A3D_PRP.edit!==id)return;
    A3D_PRP.edit=null;
    if(!cancel)bimSheetRename(id,inp.value);
    bimPresPanelRefresh();
  }
  function bimPresDropMark(it,after){
    var host=bimPresHost(),old,i;
    if(host){
      old=host.querySelectorAll('.a3d-dropbefore,.a3d-dropafter');
      for(i=0;i<old.length;i++)old[i].classList.remove('a3d-dropbefore','a3d-dropafter');
    }
    if(it)it.classList.add(after?'a3d-dropafter':'a3d-dropbefore');
  }
  function bimWirePresPanel(panel){
    if(!panel||panel.getAttribute('data-prpwired'))return;
    panel.setAttribute('data-prpwired','1');
    function inPrp(t){return !!(t&&t.closest&&t.closest('.a3d-prp'));}
    panel.addEventListener('click',function(ev){
      var t=ev.target,b;
      if(!inPrp(t))return;
      try{
        if((b=t.closest('[data-prpact]'))){if(!b.disabled)bimPresAct(b.getAttribute('data-prpact'));return;}
        if(t.closest('input'))return;
        if((b=t.closest('[data-prpitem]')))bimPresOpenPage(b.getAttribute('data-prpitem'));
      }catch(eP){console.warn('[BIM] A Presentation panel action failed',eP);a3dToast('That did not work -- see the console');}
    });
    panel.addEventListener('dblclick',function(ev){
      var t=ev.target,n,it;
      if(!inPrp(t)||t.closest('input'))return;
      try{
        if((n=t.closest('[data-prpname]'))){bimPresRename(n.getAttribute('data-prpname'));return;}
        if((it=t.closest('[data-prpitem]')))bimPresEditLayout(it.getAttribute('data-prpitem'));
      }catch(eD){console.warn('[BIM] A Presentation panel action failed',eD);a3dToast('That did not work -- see the console');}
    });
    panel.addEventListener('contextmenu',function(ev){
      var it=inPrp(ev.target)?ev.target.closest('[data-prpitem]'):null;
      if(!it)return;
      ev.preventDefault();
      bimSheetMenu(ev,it.getAttribute('data-prpitem'),'pages');
    });
    panel.addEventListener('keydown',function(ev){
      var t=ev.target;
      if(!inPrp(t)||!t.hasAttribute('data-prpren'))return;
      if(ev.key==='Enter'){ev.preventDefault();bimPresEndRename(t,false);}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimPresEndRename(t,true);}
    });
    panel.addEventListener('focusout',function(ev){
      var t=ev.target;
      if(t&&t.hasAttribute&&t.hasAttribute('data-prpren'))bimPresEndRename(t,false);
    });
    panel.addEventListener('dragstart',function(ev){
      var it=inPrp(ev.target)?ev.target.closest('[data-prpitem]'):null;
      if(!it)return;
      A3D_PRP.drag=it.getAttribute('data-prpitem');
      try{ev.dataTransfer.setData('text/plain','a3dpage:'+A3D_PRP.drag);ev.dataTransfer.effectAllowed='move';}
      catch(eD){console.warn('[BIM] The page drag could not carry its data',eD);}
    });
    panel.addEventListener('dragover',function(ev){
      if(!A3D_PRP.drag)return;
      var it=inPrp(ev.target)?ev.target.closest('[data-prpitem]'):null;
      if(!it)return;
      ev.preventDefault();
      try{ev.dataTransfer.dropEffect='move';}catch(eO){console.warn('[BIM] The page drag could not show a move',eO);}
      var r=it.getBoundingClientRect();
      bimPresDropMark(it,ev.clientY>r.top+r.height/2);
    });
    panel.addEventListener('drop',function(ev){
      if(!A3D_PRP.drag)return;
      var id=A3D_PRP.drag,it=inPrp(ev.target)?ev.target.closest('[data-prpitem]'):null,r;
      ev.preventDefault();
      A3D_PRP.drag=null;bimPresDropMark(null);
      if(!it)return;
      r=it.getBoundingClientRect();
      try{bimSheetMoveNear(id,it.getAttribute('data-prpitem'),ev.clientY>r.top+r.height/2);}
      catch(eM){console.warn('[BIM] The page could not be moved',eM);a3dToast('The page could not be moved -- see the console');}
    });
    panel.addEventListener('dragend',function(){A3D_PRP.drag=null;bimPresDropMark(null);});
    panel.addEventListener('scroll',function(){if(bimPresHost())bimPresThumbsQueue();});
  }
""")

# ---- the styles
rep(""".a3d-lylist{display:flex;flex-direction:column;min-height:48px;padding-bottom:24px}
""", """.a3d-lylist{display:flex;flex-direction:column;min-height:48px;padding-bottom:24px}
/* __acad3dV122: the Presentation panel, the Layers panel's type and spacing */
.a3d-prp{display:flex;flex-direction:column;min-height:0;padding:6px 6px 14px;font:12px/1.3 Inter,system-ui,sans-serif;color:#c9d1d9}
.a3d-prphd{display:flex;align-items:center;justify-content:space-between;padding:4px 4px 6px}
.a3d-prpttl{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#aeb8c2}
.a3d-prpcount{font-size:11px;color:#8b939c}
.a3d-prpbar{display:flex;flex-wrap:wrap;gap:5px;padding:0 4px 10px}
.a3d-prpbtn{background:#2a2f35;border:1px solid #3a4048;color:#c8ced6;border-radius:6px;padding:5px 10px;font:inherit;cursor:pointer}
.a3d-prpbtn:hover{background:#343a41}
.a3d-prpbtn.pri{background:#2f5d8a;border-color:#3f75a8;color:#fff}
.a3d-prpbtn:disabled{opacity:.4;cursor:default}
.a3d-prplist{display:flex;flex-direction:column;gap:4px;padding:0 4px 20px}
.a3d-prpitem{padding:6px;border-radius:8px;border:1px solid transparent;cursor:pointer}
.a3d-prpitem:hover{background:rgba(255,255,255,.05)}
.a3d-prpitem.cur{border-color:#4ea1ff;background:rgba(78,161,255,.08)}
.a3d-prpitem.a3d-dropbefore{box-shadow:0 -3px 0 #4ea1ff}
.a3d-prpitem.a3d-dropafter{box-shadow:0 3px 0 #4ea1ff}
.a3d-prpthumb{background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.45);line-height:0}
.a3d-prpthumb canvas{display:block;width:100%;height:auto}
.a3d-prpcap{display:flex;align-items:center;gap:6px;padding:6px 1px 0;min-width:0}
.a3d-prpno{flex:0 0 auto;min-width:18px;height:18px;padding:0 4px;border-radius:5px;background:#3a4048;color:#fff;font-size:10px;font-weight:700;display:inline-flex;align-items:center;justify-content:center}
.a3d-prpname{flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.a3d-prpren{flex:1 1 auto;min-width:0;background:#15171a;border:1px solid #4ea1ff;border-radius:4px;color:#fff;font:inherit;padding:2px 5px}
.a3d-prpempty{padding:6px 4px;color:#8b939c;line-height:1.45}
""")
rep("""body.light-theme .a3d-lyb:hover,body.light-theme .a3d-lyi:hover{background:rgba(0,0,0,.07);color:#111}
""", """body.light-theme .a3d-lyb:hover,body.light-theme .a3d-lyi:hover{background:rgba(0,0,0,.07);color:#111}
/* __acad3dV122 */
body.light-theme .a3d-prp{color:#2b2f33}
body.light-theme .a3d-prpttl{color:#555}
body.light-theme .a3d-prpbtn{background:#f3f4f6;border-color:#d1d5db;color:#222}
body.light-theme .a3d-prpbtn:hover{background:#e5e7eb}
body.light-theme .a3d-prpbtn.pri{background:#2f6fb8;border-color:#2f6fb8;color:#fff}
body.light-theme .a3d-prpitem:hover{background:rgba(0,0,0,.05)}
body.light-theme .a3d-prpitem.cur{background:rgba(47,111,184,.08)}
body.light-theme .a3d-prpno{background:#e5e7eb;color:#111}
body.light-theme .a3d-prpren{background:#fff;color:#111}
""")

# ---- the hooks
rep("""  window.__a3dPagesDisplay=function(d){return bimPagesSetDisplay(d);};
""", """  window.__a3dPagesDisplay=function(d){return bimPagesSetDisplay(d);};
  /* __acad3dV122: the Presentation panel as it is on screen, and the order */
  window.__a3dPresPanel=function(){
    var host=bimPresHost(),items=[];
    if(host)Array.prototype.forEach.call(host.querySelectorAll('[data-prpitem]'),function(it){
      var id=it.getAttribute('data-prpitem'),cv=it.querySelector('canvas[data-prpthumb]'),s=bimSheetById(id),nm=it.querySelector('.a3d-prpname'),no=it.querySelector('.a3d-prpno');
      items.push({id:id,no:no?no.textContent:null,name:nm?nm.textContent:null,cur:it.classList.contains('cur'),w:cv?cv.width:0,h:cv?cv.height:0,
        drawn:!!(cv&&s&&cv.__prpKey===bimPageSig(s)+'|'+cv.width+'x'+cv.height)});
    });
    return {open:!!host,count:A3D.sheets.length,items:items,edit:A3D_PRP.edit,
      head:host?(host.querySelector('.a3d-prpcount')||{}).textContent:null,cached:Object.keys(A3D_PRP.thumbs).length};
  };
  window.__a3dSheetMove=function(id,to){return bimSheetMove(id,to);};
  window.__a3dSheetMenuItems=function(id,where){return bimSheetMenuItems(id,where).map(function(x){return x==='-'?'-':x[0];});};
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
