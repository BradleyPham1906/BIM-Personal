  /* ================= __acad3dV116: Model and layout tabs =================
     AutoCAD's tabs at the left of the status bar: Model, then one tab per sheet, then + for a new
     one. Drawn from A3D.sheets on every refresh -- the same list the Project Browser's Sheets group
     reads -- so the two cannot disagree. */
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
    var bar=document.getElementById('a3d-statusbar');
    if(bar)bar.classList.toggle('a3d-onsheet',bimSheetOnScreen());   /* the model's aids step aside on paper */
    var sp=document.getElementById('a3d-stspace');
    if(sp){
      var onSheet=bimSheetOnScreen();
      sp.classList.toggle('show',onSheet);
      sp.textContent=A3D.sheetActiveVp?'MODEL':'PAPER';
      sp.classList.toggle('on',!!A3D.sheetActiveVp);
    }
    /* a sheet renamed while it is open renames the view it is -- __acad3dV119: and every view's
       record is held to what it names */
    bimViewSync();
    bimPresPanelRefresh();   /* __acad3dV122: the pages are the same list */
  }
  function bimLayoutNew(){
    var s=bimAddSheet(bimNextSheetNumber(),'Untitled',SHEET_NEW_SIZE);
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
      if(keep)bimSheetRename(id,inp.value);   /* __acad3dV122: the one path, the page's too */
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
    bimSheetMenu(ev,id,'tabs');   /* __acad3dV122: the items the page's menu reads too */
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
    var pg=(where==='pages'),i=pg?bimPresIndex(id):bimSheetIndex(id),n=pg?bimPresSeq().length:A3D.sheets.length,it=[];   /* __acad3dV162: a page's place is in the set */
    if(pg)it.push(['Present from this page','present'],'-');
    it.push(['New sheet','new'],['Rename','rename'],['Delete','del',true],'-');
    if(i>0)it.push([pg?'Move up':'Move left','earlier']);
    if(i>=0&&i<n-1)it.push([pg?'Move down':'Move right','later']);
    if(n>1)it.push('-');
    it.push(['Sheet setup\u2026','setup'],['Plot\u2026','plot']);
    return it;
  }
  function bimSheetMenu(ev,id,where){
    bimLtMenuOpen(ev.clientX,ev.clientY,bimSheetMenuItems(id,where),function(a){bimSheetMenuDo(a,id,where);});
  }
  function bimSheetMenuDo(a,id,where){
    if(a==='new')return bimLayoutNew();
    if(a==='rename')return (where==='pages')?bimPresRename(id):bimLayoutRename(id);
    if(a==='del')return bimConfirmDeleteSheet(id);
    if(a==='earlier'||a==='later')return where==='pages'?bimPresStep(id,a==='earlier'?-1:1):bimSheetMove(id,bimSheetIndex(id)+(a==='earlier'?-1:1));
    if(a==='setup'){if(bimActivateView('sheet',id))bimOpenSheetPropsDlg();return true;}
    if(a==='plot'){if(bimActivateView('sheet',id))bimPrintSheet();return true;}
    if(a==='present')return bimSlideshowStart(id);
    return false;
  }
