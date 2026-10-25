  /* ================= __acad3dV162: the boards are pages of the set =================
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
