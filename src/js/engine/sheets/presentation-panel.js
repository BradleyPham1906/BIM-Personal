  /* ================= __acad3dV122: the Presentation panel =================
     The presentation's pages, the thumbnail column of a PDF reader. A thumbnail is the page as it
     plots, drawn by the renderer the pages and Present use, at twice its pixels and reduced. */
  var A3D_PRP={thumbs:{},timer:null,edit:null,drag:null,bthumbs:{}};   /* __acad3dV162: the boards' thumbnails too */
  var BIM_THUMB_CSS_W=206;   /* the panel's width less its padding */
  function bimPresThumbDims(s){
    var W=Math.max(1,Math.round(BIM_THUMB_CSS_W*bimDevicePixelRatio()));
    return {W:W,H:Math.max(1,Math.round(W*s.h/s.w))};
  }
  function bimPresPanelHtml(){
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
    if(bimBoardById(id))return bimPresOpenBoard(id);   /* __acad3dV162 */
    if(!bimSheetById(id)){a3dToast('That page is no longer in the project');return false;}
    if(A3D_CLB.open)bimClbClose();
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
  function bimPresAct(a,btn){
    var Q;
    if(a==='present'){   /* __acad3dV162: from the page on screen, a board's or a sheet's, or the first */
      Q=bimPresSeq();
      return bimSlideshowStart(A3D_CLB.open&&A3D_CLB.board?A3D_CLB.board:(bimSheetOnScreen()?A3D.activeSheetId:(Q[0]&&Q[0].id)));
    }
    if(a==='board')return btn?bimBoardMenu(btn):false;
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
        if((b=t.closest('[data-prpact]'))){if(!b.disabled)bimPresAct(b.getAttribute('data-prpact'),b);return;}
        if(t.closest('input'))return;
        if((b=t.closest('[data-prpitem]')))bimPresOpenPage(b.getAttribute('data-prpitem'));
      }catch(eP){console.warn('[BIM] A Presentation panel action failed',eP);a3dToast('That did not work -- see the console');}
    });
    panel.addEventListener('dblclick',function(ev){
      var t=ev.target,n,it;
      if(!inPrp(t)||t.closest('input'))return;
      try{
        if((n=t.closest('[data-prpname]'))){bimPresRename(n.getAttribute('data-prpname'));return;}
        if((it=t.closest('[data-prpitem]'))){if(bimBoardById(it.getAttribute('data-prpitem')))bimPresOpenBoard(it.getAttribute('data-prpitem'));else bimPresEditLayout(it.getAttribute('data-prpitem'));}
      }catch(eD){console.warn('[BIM] A Presentation panel action failed',eD);a3dToast('That did not work -- see the console');}
    });
    panel.addEventListener('contextmenu',function(ev){
      var it=inPrp(ev.target)?ev.target.closest('[data-prpitem]'):null;
      if(!it)return;
      ev.preventDefault();
      var bid=it.getAttribute('data-prpitem');   /* __acad3dV162: a board's page has its own menu */
      if(bimBoardById(bid)){bimLtMenuOpen(ev.clientX,ev.clientY,bimBoardMenuItems(bid),function(a){bimBoardMenuDo(a,bid);});return;}
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
      try{bimPresMoveNear(id,it.getAttribute('data-prpitem'),ev.clientY>r.top+r.height/2);}   /* __acad3dV162: in the set, boards and all */
      catch(eM){console.warn('[BIM] The page could not be moved',eM);a3dToast('The page could not be moved -- see the console');}
    });
    panel.addEventListener('dragend',function(){A3D_PRP.drag=null;bimPresDropMark(null);});
    panel.addEventListener('scroll',function(){if(bimPresHost())bimPresThumbsQueue();});
  }
  function refreshBrowser(){
    bimRenderLayoutTabs();   /* __acad3dV116 */
    if(!el.browser)return;
    var h='',i,O=A3D_BROWSER_OPEN;

    // ---- Views ----
    h+=bimBrowserGroup('views','Views',null,0);
    if(O.views){
      h+=bimBrowserGroup('floorplans','Floor Plans',A3D.levels.length,1);
      if(O.floorplans){
        for(i=0;i<A3D.levels.length;i++){
          var lv=A3D.levels[i];
          /* __acad3dV84: the old test was "&&A3D.flat", and an elevation is flat too, so the
             floor plan row sat highlighted while the user was looking at an elevation. The
             active VIEW is what decides which row is the active row. */
          h+=bimBrowserLeaf(lv.name,{data:'data-a3dbplan="'+lv.id+'"',
            sel:(A3D_VIEW.kind==='plan'&&A3D.activeLevel===lv.id),
            ico:'\u25a6',title:'Plan view at elevation '+lv.elev},2);
        }
      }
      var v3=A3D.views.filter(function(v){return !v.flat&&!v.section;});
      h+=bimBrowserGroup('view3d','3D Views',v3.length,1);
      if(O.view3d){
        h+=bimBrowserLeaf('{3D}',{data:'data-a3dbview3d="iso"',sel:(A3D_VIEW.kind==='3d'),
          ico:'\u25c8',title:'Default isometric view'},2);
        for(i=0;i<v3.length;i++)
          h+=bimBrowserLeaf(v3[i].name,{data:'data-a3dbviewgo="'+v3[i].id+'"',sel:(A3D.activeViewId===v3[i].id),ico:'\u25c8'},2,
            '<button class="a3d-bdel" data-a3dbviewdel="'+v3[i].id+'" title="Delete view">\u00d7</button>');
      }
      /* __acad3dV84: a saved view whose camera is FLAT and which is not a section matched
         neither of the groups above -- 3D Views filters it out for being flat, Sections for not
         being a section -- so a view saved from a plan or an elevation landed in the palette
         list and nowhere in the Project Browser at all. Measured on the shipped build: save a
         view at boot, get zero browser rows. */
      var v2=A3D.views.filter(function(v){return !!v.flat&&!v.section;});
      h+=bimBrowserGroup('views2d','2D Views',v2.length,1);
      if(O.views2d){
        if(!v2.length)h+='<div class="a3d-bempty" style="padding-left:30px">none yet</div>';
        for(i=0;i<v2.length;i++)
          h+=bimBrowserLeaf(v2[i].name,{data:'data-a3dbviewgo="'+v2[i].id+'"',
            sel:(A3D.activeViewId===v2[i].id),ico:'\u25b1'},2,
            '<button class="a3d-bdel" data-a3dbviewdel="'+v2[i].id+'" title="Delete view">\u00d7</button>');
      }
      h+=bimBrowserGroup('elevations','Elevations',4,1);
      if(O.elevations){
        ['front','back','left','right'].forEach(function(k){
          h+=bimBrowserLeaf(VIEWS[k].label,{data:'data-a3dbviewpreset="'+k+'"',
            sel:(A3D_VIEW.kind==='elev'&&A3D_VIEW.id===k),ico:'\u25b1'},2);
        });
      }
      var vs=A3D.views.filter(function(v){return !!v.section;});
      h+=bimBrowserGroup('sections','Sections',vs.length,1);
      if(O.sections){
        if(!vs.length)h+='<div class="a3d-bempty" style="padding-left:30px">none yet</div>';
        for(i=0;i<vs.length;i++)
          h+=bimBrowserLeaf(vs[i].name,{data:'data-a3dbviewgo="'+vs[i].id+'"',sel:(A3D.activeViewId===vs[i].id),ico:'\u2702'},2,
            '<button class="a3d-bdel" data-a3dbviewdel="'+vs[i].id+'" title="Delete view">\u00d7</button>');
      }
    }

    // ---- Schedules ----
    /* __acad3dV74: derived, not listed. The literal this replaced omitted 'beam', which made a
       working schedule unreachable for as long as it existed. */
    var schedKeys=bimScheduleKeys();
    h+=bimBrowserGroup('schedules','Schedules/Quantities',schedKeys.length,0);
    if(O.schedules){
      schedKeys.forEach(function(k){
        var def=SCHEDULE_DEFS[k];
        if(!def)return;
        var n=0;
        try{n=def.build().length;}catch(eS){n=0;}
        h+=bimBrowserLeaf(def.label+' ('+n+')',{data:'data-a3dbsched="'+k+'"',
          sel:(el.schedcat&&el.schedcat.value===k),ico:'\u2261'},1);
      });
    }

    // ---- Sheets ----
    h+=bimBrowserGroup('sheets','Sheets',A3D.sheets.length,0);
    if(O.sheets){
      if(!A3D.sheets.length)h+='<div class="a3d-bempty" style="padding-left:18px">none yet -- use +Sht above</div>';
      for(i=0;i<A3D.sheets.length;i++){
        var sh=A3D.sheets[i];
        h+=bimBrowserLeaf(bimSheetLabel(sh),{data:'data-a3dbsheetgo="'+sh.id+'"',   /* __acad3dV116 */
          sel:(A3D.activeSheetId===sh.id&&el.sheetview&&el.sheetview.classList.contains('open')),ico:'\u25a4'},1,
          '<button class="a3d-bdel" data-a3dbsheetdel="'+sh.id+'" title="Delete sheet">\u00d7</button>');
      }
    }

    // ---- Families ----
    var byCat={},libModels=bimLibEntries('model');   /* __acad3dV124: blocks and templates are not families */
    for(i=0;i<libModels.length;i++){
      var f=libModels[i];
      if(!byCat[f.category])byCat[f.category]=[];
      byCat[f.category].push(f);
    }
    h+=bimBrowserGroup('families','Families',libModels.length,0);
    if(O.families){
      var cats=Object.keys(byCat).sort();
      if(!cats.length)h+='<div class="a3d-bempty" style="padding-left:18px">none loaded</div>';
      cats.forEach(function(c){
        h+='<div class="a3d-bsub" style="padding-left:18px">'+bimEsc(c)+'</div>';
        byCat[c].forEach(function(f){
          h+=bimBrowserLeaf(f.name,{data:'data-a3dbfam="'+f.id+'"',ico:'\u25a3',title:'Click to place an instance'},2,
            '<button class="a3d-bdel" data-a3dbfamdel="'+f.id+'" title="Remove from library">\u00d7</button>');
        });
      });
    }

    // ---- Classifications (Phase 47) ----
    h+=bimBrowserGroup('classifications','Classifications',A3D.classifications.length,0);
    if(O.classifications){
      if(!A3D.classifications.length)h+='<div class="a3d-bempty" style="padding-left:18px">none yet -- use Manage &gt; Classifications</div>';
      for(i=0;i<A3D.classifications.length;i++){
        var cl=A3D.classifications[i];
        var cn=bimClassificationInUseCount(cl.id);
        h+=bimBrowserLeaf(cl.code+(cl.description?' — '+cl.description:'')+' ('+cn+')',
          {data:'data-a3dbclass="'+cl.id+'"',ico:'▢',title:'Select all objects with this classification'},1);
      }
    }

    /* __acad3dV121: the Layers and Model groups moved to the Layers panel, where the model is the
       layers' contents */
    el.browser.innerHTML=h;
  }
  function refreshTree(){
    bimSyncStatusHint();
    /* __acad3dV80: the left shell's file card names the PROJECT, and a rename changes no DOM
       inside the panel -- so the MutationObserver that drives the cleanup never fires for it.
       Re-running the pass here is what makes the card follow the project rather than only
       being right on first paint. Cheap: the pass compares before it writes. */
    try{bimCleanShell();}catch(eS){console.warn('[BIM] The left panel could not be redrawn',eS);}   /* __acad3dV121: said nothing */
    bimLayersPanelRefresh();   /* __acad3dV121: the objects on each layer, and which are selected */
    if(!el.rows)return;
    var h='',i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],c=o.col||(TYPES[o.t]||{}).c||'#7f9db8';
      h+='<div class="a3d-row'+((A3D.sel===o.id||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0))?' sel':(A3D.sel2===o.id?' sel2':''))+'" data-a3did="'+o.id+'">'+
        '<span class="a3d-dot" style="background:'+c+'"></span>'+
        '<span class="a3d-nm">'+o.name+'</span>'+
        (bimIsLocked(o)?'<span class="a3d-lockicon" title="Locked (Pin)">'+BIM_LOCK_ON+'</span>':'')   /* __acad3dV121: not an emoji */+
        '<span class="a3d-ty">'+o.t+'</span></div>';
    }
    el.rows.innerHTML=h;
    refreshProps();
    refreshSchedule();
    refreshBrowser();
  }
  var drag=null;
  function cvXY(ev){
    var r=el.cv.getBoundingClientRect();
    return [ev.clientX-r.left,ev.clientY-r.top];
  }
  function onDown(ev){
    var xy=cvXY(ev);
    if(A3D.conPick&&ev.button===0){
      var gripC=bimPickGrip(xy[0],xy[1]);
      if(gripC&&gripC.kind==='sketch'&&gripC.objId===A3D.sel&&A3D.conPick.picked.indexOf(gripC.idx)<0){
        A3D.conPick.picked.push(gripC.idx);
        if(A3D.conPick.picked.length>=A3D.conPick.need){bimFinishConstraintPick();}
        else{a3dToast(bimSketchConstraintLabel(A3D.conPick.type)+': click point '+(A3D.conPick.picked.length+1)+' of '+A3D.conPick.need);paint();}
      }else{
        a3dToast('Click a point on the selected sketch (Escape to cancel)');
      }
      ev.preventDefault();
      return;
    }
    /* __acad3dV83: a zoom window owns the pointer completely while it is armed -- it is a modal
       view operation, and letting a selection or a gizmo drag start underneath it would make the
       rectangle mean two things at once. */
    if(A3D.zoomWindow&&ev.button===0){
      drag={zwin:true,x0:xy[0],y0:xy[1],x:xy[0],y:xy[1],moved:false};
      ev.preventDefault();
      return;
    }
    /* __acad3dV123: PRESSPULL's click takes a face; Ctrl+Shift+click takes one at any time (Rhino's
       sub-object pick). Off every face the click is what it always was. */
    if(ev.button===0&&!A3D.sk&&!A3D.conPick&&(A3D.facePick||((ev.ctrlKey||ev.metaKey)&&ev.shiftKey))){
      var fpk=bimFacePickAt(xy[0],xy[1]);
      if(fpk){bimFaceEnter(fpk);drag=bimPushPress(xy,ev,true);ev.preventDefault();return;}
      if(A3D.facePick){
        A3D.facePick=false;bimSyncStatusHint();
        a3dToast('No face there - PRESSPULL ended');
        ev.preventDefault();return;
      }
    }
    /* __acad3dV123: a held face: its arrow or the face itself is pushed; another face of the same
       object is taken and pushed; anywhere else lets the face go and the press goes on as ever */
    if(ev.button===0&&!A3D.sk&&!A3D.conPick&&A3D.face){
      var fcd=bimFaceCurrent();
      if(fcd){
        var fhit=bimFaceHitAt(xy[0],xy[1]);
        if(!fhit){
          var fo=bimFacePickAt(xy[0],xy[1]);
          if(fo&&fo.o.id===fcd.o.id){bimFaceEnter(fo);fhit='face';}
        }
        if(fhit){drag=bimPushPress(xy,ev,false);paint();ev.preventDefault();return;}
        bimFaceExit();
      }
    }
    /* __acad3dV97: GRIPS FIRST, then the gizmo. A grip is an 8-pixel point target the user
       aims at on purpose; a gizmo arm is a long band that can be grabbed anywhere along it. On
       a symmetric shape an edge's midpoint grip sits exactly on an arm, so gizmo-first turned
       "add a vertex here" into "move the whole shape". The gizmo still wins over the body and
       over other objects, which is what V76 put it first for. */
    if(!A3D.sk&&ev.button===0){
      var grip=bimPickGrip(xy[0],xy[1]);
      if(grip&&grip.mid){
        /* __acad3dV97: insert, then become an ordinary vertex drag on the new point, so the new
           vertex snaps, obeys constraints and propagates exactly as any other vertex does. */
        /* The press only ARMS the insert. No drag, no vertex: a click that goes up where it
           went down must leave the sketch exactly as it was. */
        drag={grip:true,objId:grip.objId,idx:-1,kind:'sketch',elev:grip.elev,moved:false,
              pendingMid:{seg:grip.seg}};
        ev.preventDefault();
        return;
      }
      if(grip){
        pushUndo();
        drag={grip:true,objId:grip.objId,idx:grip.idx,kind:grip.kind,elev:grip.elev,moved:false};
        ev.preventDefault();
        return;
      }
    }
    /* __acad3dV76: the gizmo is tested before the body drag. Its arms reach outside the
       object, so testing it later would let whatever lies under an arm win the click -- and
       the arm is the thing the user aimed at. (Grips now come first; see __acad3dV97 above.) */
    if(!A3D.sk&&ev.button===0){
      var gz=bimPickGizmo(xy[0],xy[1]);
      /* __acad3dV110/V112: on a handle, the modifiers belong to the handle -- Shift is precision
         (and an even scale on a scale box), Alt on the centre moves the pivot, and Ctrl leaves a
         copy behind and drags the new one, which is how Revit copies. Off a handle they mean what
         they always did: pan, and add to the selection. */
      var gctrl=(ev.ctrlKey||ev.metaKey);
      var gcopy=gz&&(gz.kind==='axis'||gz.kind==='plane'||gz.kind==='centre')&&!ev.altKey;
      if(gz&&(!gctrl||gcopy)){
        bimCloseGizmoMenu();
        A3D_MATERIALIZED=[];
        var gd=bimGizmoBegin(gz,xy,ev);
        if(gd){
          /* __acad3dV123: nothing happens on the press. The undo step and, with Ctrl, the copies are
             made by the first movement (bimGizmoStartMoving): a click opens the handle's value box
             and changes nothing. On V122 a click added an empty undo step, and a Ctrl+click left a
             copy of the selection on top of it. */
          gd.undoPending=true;
          if(gctrl&&gcopy)gd.copyPending=true;
          gd.hit=gz;gd.xy0=xy.slice();gd.mods={shiftKey:!!ev.shiftKey};
          drag=gd;
          paint();
        }
        ev.preventDefault();
        return;
      }
    }
    if(A3D.sk&&ev.button===0&&!ev.shiftKey&&!ev.ctrlKey&&!ev.metaKey){drag={sk:true,moved:false,pan:false};skClick(xy);ev.preventDefault();return;}
    if(!A3D.sk&&ev.button===0&&(ev.ctrlKey||ev.metaKey)){
      var hitEmpty=pick(xy[0],xy[1]);
      if(!hitEmpty){
        drag={marquee:true,x0:xy[0],y0:xy[1],x:xy[0],y:xy[1],moved:false};
        ev.preventDefault();
        return;
      }
    }
    var forcePan=(A3D.flat&&A3D.navMode==='pan')||A3D.flat&&false;
    drag={x0:xy[0],y0:xy[1],x:xy[0],y:xy[1],moved:false,pan:(ev.button===1||ev.button===2||ev.shiftKey||forcePan||(A3D.navMode==='pan'&&ev.button===0))};
    /* __acad3dV110: a right-press on a gizmo handle still pans if it drags; released where it
       went down, it opens the gizmo menu instead (onUp). */
    if(ev.button===2&&!A3D.sk&&bimPickGizmo(xy[0],xy[1]))drag.gizMenu={x:ev.clientX,y:ev.clientY};
    if(!drag.pan&&!ev.ctrlKey&&!ev.metaKey){
      var hit=pick(xy[0],xy[1]);
      if(hit&&hit.id===A3D.sel&&bimIsLocked(hit)&&!(A3D.selSet&&A3D.selSet.length>1)){
        a3dToast(hit.name+' is locked (Pin) \u2014 unlock it in Properties to move it');
      }else if(hit&&!bimIsLocked(hit)&&(hit.id===A3D.sel||(A3D.selSet&&A3D.selSet.length>1&&A3D.selSet.indexOf(hit.id)>=0))){
        /* __acad3dV123: armed here; its first movement makes it the gizmo's move (bimBodyDragStart).
           It still moves by the drag and not to it (V99): the plane goes through the point grabbed. */
        drag.body={id:hit.id,x:xy[0],y:xy[1],vert:!!ev.altKey};
      }
      /* __acad3dV98: pressing on the SELECTED grid drags it. The undo snapshot is taken on
         the first real movement, so a click that selects nothing new adds no undo step. */
      if(!hit){
        var sgD=bimSelectedGrid(),gpD=sgD?bimPickGrid(xy[0],xy[1]):null;
        if(gpD&&gpD.id===sgD.id){
          var gy0=bimGetActiveLevel().elev,gO=groundPoint(xy[0],xy[1],gy0);
          if(gO)drag.gridMv={id:gpD.id,y:gy0,o:[gO[0],gO[2]],p1:gpD.p1.slice(),p2:gpD.p2.slice(),undo:false};
        }
      }
    }
    ev.preventDefault();
  }
  function onMove(ev){
    if(!drag)return;
    var xy=cvXY(ev),dx=xy[0]-drag.x,dy=xy[1]-drag.y;
    drag.x=xy[0];drag.y=xy[1];
    if(drag.marquee){
      if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>2||Math.abs(xy[1]-drag.y0)>2))drag.moved=true;
      paint();
      return;
    }
    if(drag.zwin){
      if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>2||Math.abs(xy[1]-drag.y0)>2))drag.moved=true;
      paint();
      return;
    }
    if(drag.pp){   /* __acad3dV123 */
      if(!drag.moved){
        if(Math.abs(xy[0]-drag.x0)<=A3D_GIZ.click&&Math.abs(xy[1]-drag.y0)<=A3D_GIZ.click)return;
        drag.moved=true;
        if(!bimPushBegin(drag,true)){drag=null;paint();return;}
      }
      bimPushApply(xy);
      return;
    }
    if(drag.rot||drag.giz){
      /* __acad3dV123: a press that has not travelled A3D_GIZ.click pixels is still a click, and a
         click changes nothing. The first real movement takes the undo step and makes any copies;
         the drag then runs from where it was pressed, so nothing jumps. */
      if(!drag.moved){
        if(Math.abs(xy[0]-drag.x0)<=A3D_GIZ.click&&Math.abs(xy[1]-drag.y0)<=A3D_GIZ.click)return;
        drag.moved=true;
        bimGizmoStartMoving(drag);
      }
      if(drag.rot)bimGizmoApplyRotate(xy);else bimGizmoApply(xy);
      return;
    }
    if(drag.grip){
      if(drag.pendingMid){   /* __acad3dV97: the drag moved, so now the vertex is added */
        var pmo=objById(drag.objId);
        /* the snapshot BEFORE the insert, so undo restores the shape as it was */
        if(pmo)pushUndo();
        var pins=pmo?bimInsertSketchVertex(pmo,drag.pendingMid.seg,bimSketchSegMid(pmo,drag.pendingMid.seg))
                    :{error:'That sketch no longer exists'};
        drag.pendingMid=null;
        if(pins.error){a3dToast('Add vertex: '+pins.error);drag=null;paint();return;}
        drag.idx=pins.idx;
        refreshProps();
      }
      var g0=groundPoint(xy[0],xy[1],drag.elev);
      if(!g0)return;
      var fakeSk={y:drag.elev,pts:[]};
      var snapped=bimSnapPoint(xy,g0,fakeSk);
      if(drag.kind==='grid'){   /* __acad3dV98: grids are world datums -- no object offset */
        var gg=bimGridById(drag.objId);
        if(gg){
          var other=drag.idx?gg.p1:gg.p2;
          var gdx=snapped[0]-other[0],gdz=snapped[1]-other[1];
          if(Math.sqrt(gdx*gdx+gdz*gdz)>=1e-6){
            if(drag.idx)gg.p2=[snapped[0],snapped[1]];else gg.p1=[snapped[0],snapped[1]];
            drag.moved=true;
          }
          paint();saveSoon();
        }
        return;
      }
      var o=objById(drag.objId);
      if(o){
        /* __acad3dV75: snapped is a WORLD plan point (groundPoint + snap both work in world) and
           the point arrays it is about to be written into are LOCAL. On an object with a
           non-zero pos, writing it straight through teleported the point by -pos on the first
           drag after a move. Subtract the offset here, at the single boundary where a cursor
           position becomes stored geometry. */
        var q=bimObjOffset(o);
        snapped=[snapped[0]-q[0],snapped[1]-q[2],snapped[2]];
        if(drag.kind==='sketch'){
          bimDragSketchPoint(o,drag.idx,[snapped[0],snapped[1]]);
          if(o.constraints&&o.constraints.length)bimResolveSketch(o,drag.idx,{silent:true});
          bimPropagateFrom([o.id],'rebuild');   // __acad3dV52: live -- any room sourced from this sketch follows it
        }
        else if(drag.kind==='wall'){
          bimDragWallPoint(o,drag.idx,[snapped[0],snapped[1]]);
          bimPropagateFrom([o.id],'rebuild');   // __acad3dV52: live -- openings/rooms depending on this wall follow it
        }
        else if(drag.kind==='annot'){   /* __acad3dV98 */
          bimDragAnnotPoint(o,drag.idx,[snapped[0],snapped[1]]);
        }
        paint();saveSoon();
      }
      return;
    }
    if(!drag.moved&&(Math.abs(xy[0]-drag.x0)>3||Math.abs(xy[1]-drag.y0)>3))drag.moved=true;
    if(!drag.moved)return;
    if(drag.gridMv){   /* __acad3dV98 */
      var gm=drag.gridMv,gmG=bimGridById(gm.id),gN=groundPoint(xy[0],xy[1],gm.y);
      if(gmG&&gN){
        if(!gm.undo){pushUndo();gm.undo=true;}
        var mdx=gN[0]-gm.o[0],mdz=gN[2]-gm.o[1];
        gmG.p1=[gm.p1[0]+mdx,gm.p1[1]+mdz];gmG.p2=[gm.p2[0]+mdx,gm.p2[1]+mdz];
        paint();saveSoon();
      }
      return;
    }
    if(drag.body){   /* __acad3dV123: from here on the gizmo's move */
      var bodyRec=bimBodyDragStart(drag.body);
      if(!bodyRec){drag=null;paint();return;}
      drag=bodyRec;
      bimGizmoApply(xy);
      return;
    }
    var c=A3D.cam;
    if(drag.pan){
      var V=camVecs(c),k=c.dist*0.0018;
      c.tx-=(V.r[0]*dx-V.u[0]*dy)*k;
      c.ty-=(V.r[1]*dx-V.u[1]*dy)*k;
      c.tz-=(V.r[2]*dx-V.u[2]*dy)*k;
    }else{
      if(A3D.flat){drag.pan=true;var k2=c.dist*0.0018;var R2=camVecs(c);c.tx-=(R2.r[0]*dx-R2.u[0]*dy)*k2;c.ty-=(R2.r[1]*dx-R2.u[1]*dy)*k2;c.tz-=(R2.r[2]*dx-R2.u[2]*dy)*k2;paint();return;}
      c.yaw-=dx*0.0075;
      c.pitch+=dy*0.0075;
      if(c.pitch>1.52)c.pitch=1.52;
      if(c.pitch<-1.52)c.pitch=-1.52;
      A3D.view='Custom';refreshHud();
    }
    paint();saveSoon();
  }
  function onUp(ev){
    if(!drag)return;
    var wasSk=drag.sk,moved=drag.moved,pan=drag.pan,wasGrip=drag.grip,wasMarquee=drag.marquee;
    var wasGridMv=drag.gridMv;   /* __acad3dV98 */
    var mx0=drag.x0,my0=drag.y0,mx1=drag.x,my1=drag.y;
    /* __acad3dV76: the gizmo follows the same deferred-propagation rule the body drag uses --
       .pos tracks live for responsiveness, and the dependency graph is walked ONCE, here, with
       the gesture's total delta. */
    var wasGiz=drag.giz,gizIds=drag.ids,gizKind=drag.gk,gizVec=drag.gizVec;   /* __acad3dV110 */
    var gizRec=(drag.giz||drag.rot)?drag:null;                                  /* __acad3dV123 */
    var ppRec=drag.pp?drag:null;
    var gizFactor=drag.factor,gizTilt=drag.tiltAngle,gizFailed=drag.gizFailed,gizMenu=drag.gizMenu;
    var wasRot=drag.rot,rotAngle=drag.rotAngle,rotFailed=drag.rotFailed;
    var wasZwin=drag.zwin,zw=[drag.x0,drag.y0,drag.x,drag.y],zwMoved=drag.moved;
    drag=null;
    if(wasZwin){
      bimCancelZoomWindow();
      if(zwMoved)bimApplyZoomWindow(zw[0],zw[1],zw[2],zw[3]);
      else a3dToast('Zoom window cancelled');
      return;
    }
    if(ppRec){   /* __acad3dV123: a push ends; a click on a held face asks for its value */
      if(moved&&ppRec.f)bimPushEnd(ppRec);
      else if(!moved&&!ppRec.entry)bimFaceClickValue(ppRec);
      else paint();
      return;
    }
    if(wasRot||wasGiz){
      if(!moved&&gizRec){   /* __acad3dV123: a click on a handle asks for a value; nothing has changed */
        bimGizmoClickValue(gizRec,ev);
        return;
      }
      /* __acad3dV112: one end-of-drag path, so a drag finished with the mouse and a drag finished
         by typing an exact value settle identically. */
      bimGizmoEndDrag({rot:wasRot,gk:gizKind,ids:gizIds,vec:gizVec,factor:gizFactor,tilt:gizTilt,
                       failed:gizFailed,angle:rotAngle,rotFailed:rotFailed});
      return;
    }
    if(wasGrip){refreshTree();paint();saveSoon();return;}
    if(wasGridMv&&moved){refreshProps();paint();saveSoon();return;}   /* __acad3dV98 */
    if(wasMarquee){
      if(moved){
        var matched=bimApplyMarquee(mx0,my0,mx1,my1);
        A3D.selSet=matched;
        A3D.sel=matched.length?matched[0]:null;
        A3D.sel2=null;
        a3dToast(matched.length+' object(s) selected');
      }else{
        A3D.selSet=[];A3D.sel=null;A3D.sel2=null;
      }
      refreshTree();paint();
      return;
    }
    /* __acad3dV55 deferred a body drag's propagation to one walk with the gesture's total delta.
       __acad3dV123: a body drag is the gizmo's move, and the gizmo's end path (above) is that walk. */
    if(gizMenu&&!moved){bimOpenGizmoMenu(gizMenu.x,gizMenu.y);return;}   /* __acad3dV110 */
    if(wasSk||moved||pan)return;
    var xy=cvXY(ev);
    if(inRect(xy[0],xy[1],A3D.homeRect)){setView('home');return;}
    var ch=cubeHit(xy[0],xy[1]);
    if(ch){setView(ch);return;}
    var o=pick(xy[0],xy[1]);
    if(ev.ctrlKey||ev.metaKey){
      if(o&&o.id!==A3D.sel)A3D.sel2=(A3D.sel2===o.id)?null:o.id;
    }else{
      A3D.sel=o?o.id:null;
      A3D.selSet=o?[o.id]:[];
      if(!o)A3D.sel2=null;
      if(A3D.sel2===A3D.sel)A3D.sel2=null;
      /* __acad3dV98: grids are drawn beneath the model, so they are picked after it */
      var gpk=o?null:bimPickGrid(xy[0],xy[1]);
      A3D.selGrid=gpk?gpk.id:null;
      if(gpk)refreshLevels();
      /* __acad3dV165: under the grids, a band of the site analysis, by its inside */
      var bpk=(o||gpk)?null:bimPickBand(xy[0],xy[1]);
      if(bpk){o=bpk;A3D.sel=o.id;A3D.selSet=[o.id];}
      /* __acad3dV134: under them all, the data layers */
      A3D_DATA.sel=(o||gpk)?null:bimDataPick(xy[0],xy[1]);
      if(!o)refreshProps();
    }
    refreshTree();paint();
  }
  /* __acad3dV133e: how near and how far the view may go -- a door handle to the whole town */
  var BIM_ZOOM_MIN=0.5,BIM_ZOOM_MAX=200000;
  function bimZoomClamp(d){return d<BIM_ZOOM_MIN?BIM_ZOOM_MIN:(d>BIM_ZOOM_MAX?BIM_ZOOM_MAX:d);}
  /* zoom by a factor about a screen point: the ground under it stays under it, as in AutoCAD and Revit */
  function bimZoomAbout(f,sx,sy){
    var c=A3D.cam,y0=c.ty,p0=(sx==null)?null:groundPoint(sx,sy,y0),p1;
    c.dist=bimZoomClamp(c.dist*f);
    if(p0){
      p1=groundPoint(sx,sy,y0);
      if(p1){c.tx+=p0[0]-p1[0];c.tz+=p0[2]-p1[2];}
    }
    return c.dist;
  }
  function onWheel(ev){
    var xy=cvXY(ev);
    bimZoomAbout(Math.pow(1.0015,ev.deltaY),xy[0],xy[1]);
    ev.preventDefault();paint();saveSoon();
  }
