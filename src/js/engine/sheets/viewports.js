  /* ================= __acad3dV116: model space through a viewport =================
     AutoCAD's MSPACE and Revit's Activate View. Double-click a viewport and it becomes a window onto
     the model: a drag pans it, the wheel steps through the standard scales about the cursor, and the
     rest of the sheet recedes. Double-click outside it, Escape or PAPER returns to paper space. The
     viewport keeps its pan and scale, so every output shows what was set here. */
  function bimSheetVp(sheet,id){
    var i;
    if(!sheet||!id)return null;
    for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===id)return sheet.viewports[i];
    return null;
  }
  function bimSheetInVp(vp,mm){return mm[0]>=vp.x&&mm[0]<=vp.x+vp.w&&mm[1]>=vp.y&&mm[1]<=vp.y+vp.h;}
  function bimNextScale(d,dir){
    var i;
    if(dir<0){for(i=SHEET_SCALES.length-1;i>=0;i--)if(SHEET_SCALES[i].denom<d-1e-9)return SHEET_SCALES[i].denom;return d;}
    for(i=0;i<SHEET_SCALES.length;i++)if(SHEET_SCALES[i].denom>d+1e-9)return SHEET_SCALES[i].denom;
    return d;
  }
  /* A fitted viewport has no fixed scale or centre to pan from. The first pan or zoom gives it both:
     the smallest standard scale that still shows everything the fit showed, centred where the fit
     was -- read back from the fit's own camera, so this cannot drift from how 'fit' frames. */
  /* __acad3dV116: where a fit would centre this viewport, as a pan -- read back from the fit's own
     camera, so a fixed scale opens on the model the same way the first pan or zoom keeps it. */
  function bimSheetVpFitPan(vp){
    var src=bimResolveViewportSource(vp);
    if(src.error||!src.cam)return null;
    var cam=bimSheetSolveCamera(src,vp.w,vp.h,1,'fit',vp.scaleDenom);
    var V=camVecs({yaw:src.cam.yaw,pitch:src.cam.pitch,dist:1,tx:src.cam.tx,ty:src.cam.ty,tz:src.cam.tz});
    var dx=cam.tx-src.cam.tx,dy=cam.ty-src.cam.ty,dz=cam.tz-src.cam.tz;
    return [dx*V.r[0]+dy*V.r[1]+dz*V.r[2],dx*V.u[0]+dy*V.u[1]+dz*V.u[2]];
  }
  function bimSheetVpToRatio(vp){
    if(vp.scaleMode==='ratio'){
      if(!vp.pan||!isFinite(vp.pan[0])||!isFinite(vp.pan[1]))vp.pan=[0,0];
      return true;
    }
    var src=bimResolveViewportSource(vp);
    if(src.error||!src.cam)return false;
    var cam=bimSheetSolveCamera(src,vp.w,vp.h,1,'fit',vp.scaleDenom);
    var mmPerM=1.2*vp.h/Math.max(cam.dist,1e-9),want=1000/Math.max(mmPerM,1e-9),d=SHEET_SCALES[SHEET_SCALES.length-1].denom,i;
    for(i=0;i<SHEET_SCALES.length;i++)if(SHEET_SCALES[i].denom>=want-1e-6){d=SHEET_SCALES[i].denom;break;}
    vp.pan=bimSheetVpFitPan(vp)||[0,0];
    vp.scaleMode='ratio';vp.scaleDenom=d;
    return true;
  }
  function bimSetModelSpace(id){
    if(!bimSheetOnScreen()){a3dToast('MSPACE works on a sheet: open one from the layout tabs');return false;}
    var sheet=bimSheetById(A3D.activeSheetId),vp=null,i;
    if(!sheet)return false;
    vp=bimSheetVp(sheet,id)||bimSheetVp(sheet,A3D.sheetSelVp);
    if(!vp)for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].kind!=='schedule'){vp=sheet.viewports[i];break;}
    if(!vp){a3dToast('This sheet has no viewport onto the model: add one with + Viewport');return false;}
    if(vp.kind==='schedule'){a3dToast('A schedule has no model to work in');return false;}
    var src=bimResolveViewportSource(vp);
    if(src.error){a3dToast('That viewport cannot be worked in: '+src.error);return false;}
    A3D.sheetActiveVp=vp.id;A3D.sheetSelVp=null;A3D.sheetDrag=null;
    bimSheetViewRefresh();bimSyncStatusHint();
    return true;
  }
  function bimSetPaperSpace(){
    if(!A3D.sheetActiveVp)return false;
    A3D.sheetActiveVp=null;A3D.sheetDrag=null;
    bimSheetViewRefresh();bimSyncStatusHint();
    return true;
  }
  function bimDeleteSheetViewport(id){
    var sheet=bimSheetById(A3D.activeSheetId),vp=bimSheetVp(sheet,id);
    if(!vp)return false;
    pushUndo();
    sheet.viewports.splice(sheet.viewports.indexOf(vp),1);
    if(A3D.sheetSelVp===id)A3D.sheetSelVp=null;
    if(A3D.sheetActiveVp===id)A3D.sheetActiveVp=null;
    bimSheetViewRefresh();bimSyncStatusHint();saveSoon();
    a3dToast('Viewport deleted');
    return true;
  }
  var A3D_VP_WHEEL_T=0;
  function bimSheetWheel(ev){
    if(!A3D.sheetActiveVp||!el.sheetcv)return;
    var sheet=bimSheetById(A3D.activeSheetId),vp=bimSheetVp(sheet,A3D.sheetActiveVp);
    if(!vp)return;
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    if(!bimSheetInVp(vp,mm)||!ev.deltaY)return;
    ev.preventDefault();
    var dir=ev.deltaY<0?-1:1;
    if(vp.scaleMode==='ratio'&&bimNextScale(vp.scaleDenom,dir)===vp.scaleDenom)return;
    var now=Date.now();
    if(now-A3D_VP_WHEEL_T>600)pushUndo();   /* one undo step for a run of wheel notches */
    A3D_VP_WHEEL_T=now;
    if(!bimSheetVpToRatio(vp))return;
    var d1=vp.scaleDenom,d2=bimNextScale(d1,dir);
    if(d2!==d1){
      /* the model point under the cursor stays under the cursor */
      var ox=mm[0]-(vp.x+vp.w/2),oy=mm[1]-(vp.y+vp.h/2);
      vp.pan=[vp.pan[0]+ox*(d1-d2)/1000,vp.pan[1]-oy*(d1-d2)/1000];
      vp.scaleDenom=d2;
    }
    bimSheetViewRefresh();saveSoon();
  }
  function bimSheetContextMenu(ev){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet||!el.sheetcv)return;
    ev.preventDefault();
    var mm=bimSheetEvtToMM(ev,el.sheetcv),hit=bimSheetHitTest(sheet,mm),items=[];
    if(hit){
      if(!A3D.sheetActiveVp){A3D.sheetSelVp=hit.vp.id;bimSheetViewRefresh();}
      if(hit.vp.kind!=='schedule')items.push(A3D.sheetActiveVp===hit.vp.id?['Paper space','pspace']:['Work in this viewport','mspace']);
      items.push(['Viewport properties\u2026','props']);
      items.push(['Delete viewport','del',true]);
    }else if(A3D.sheetActiveVp){
      items.push(['Paper space','pspace']);
    }else{
      items.push(['Add viewport\u2026','add']);
      items.push(['Sheet setup\u2026','setup']);
    }
    bimLtMenuOpen(ev.clientX,ev.clientY,items,function(a){
      if(a==='mspace')bimSetModelSpace(hit.vp.id);
      else if(a==='pspace')bimSetPaperSpace();
      else if(a==='props')bimOpenViewportPropsDlg(hit.vp.id);
      else if(a==='del')bimDeleteSheetViewport(hit.vp.id);
      else if(a==='add')bimOpenAddViewportDlg();
      else if(a==='setup')bimOpenSheetPropsDlg();
    });
  }
  /* On a sheet the paper is what is on screen. A key that would start a tool or edit a model object
     would act on something the user cannot see, so only these reach past the paper: Escape (out of
     the viewport, then the selection), Delete (the selected viewport), the Ctrl shortcuts (undo,
     redo, save, open) and the function keys. */
  /* __acad3dV117: the one test for "this key belongs to the focused control, not to the model". There
     were four copies of it: this handler's had SELECT, the engine's key handler (twice) and the key
     claim hook did not, so with a Properties dropdown focused, ArrowDown moved the selected object a
     metre instead of stepping the dropdown, and Delete erased it. A text field owns every key -- its
     Ctrl+Z is its own text undo. A dropdown owns its plain keys -- arrows step its options, letters
     find one -- but has no use for Ctrl shortcuts or function keys, so those stay the app's, and
     Ctrl+Z still undoes the type change the dropdown just made. */
  function bimKeyForControl(ev){
    var tg=ev&&ev.target;
    if(!tg)return false;
    if(tg.tagName==='INPUT'||tg.tagName==='TEXTAREA'||tg.isContentEditable)return true;
    if(tg.tagName==='SELECT')return !(ev.ctrlKey||ev.metaKey||/^F\d+$/.test(ev.key));
    if(tg.getAttribute&&tg.getAttribute('role')==='separator'&&tg.tabIndex>=0)return !(ev.ctrlKey||ev.metaKey||/^F\d+$/.test(ev.key));   /* __acad3dV166b */
    return false;
  }
  function bimSheetKey(ev){
    if(bimKeyForControl(ev))return false;   /* __acad3dV117 */
    if(el.dlg||ev.ctrlKey||ev.metaKey||/^F\d+$/.test(ev.key))return false;
    if(A3D_PAGES.display==='pages'){   /* __acad3dV122: the pages' keys, from their table */
      var pact=bimPageKeyAct(ev.key);
      if(pact)bimPagesKeyDo(pact);
      ev.preventDefault();ev.stopImmediatePropagation();
      return true;
    }
    if(ev.key==='Escape'){
      if(A3D.sheetActiveVp)bimSetPaperSpace();
      else if(A3D.sheetSelVp){A3D.sheetSelVp=null;bimSheetViewRefresh();}
    }else if((ev.key==='Delete'||ev.key==='Backspace')&&!A3D.sheetActiveVp&&A3D.sheetSelVp){
      bimDeleteSheetViewport(A3D.sheetSelVp);
    }
    ev.preventDefault();ev.stopImmediatePropagation();
    return true;
  }
  function bimSheetPointerDown(ev){
    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet||!el.sheetcv)return;
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    if(A3D.sheetActiveVp){   /* __acad3dV116: a drag inside the viewport pans; nothing on the paper can be picked */
      var avp=bimSheetVp(sheet,A3D.sheetActiveVp);
      if(avp&&bimSheetInVp(avp,mm)&&!ev.button){
        ev.preventDefault();
        A3D.sheetDrag={mode:'pan',vpId:avp.id,startMM:mm,orig:null};
      }
      return;
    }
    if(ev.button)return;   /* __acad3dV116: a right-click opens the menu; it does not start a move */
    var hit=bimSheetHitTest(sheet,mm);
    if(hit){
      ev.preventDefault();
      A3D.sheetSelVp=hit.vp.id;
      pushUndo();
      A3D.sheetDrag={mode:hit.handle?'resize':'move',vpId:hit.vp.id,startMM:mm,
        orig:{x:hit.vp.x,y:hit.vp.y,w:hit.vp.w,h:hit.vp.h}};
    }else{
      A3D.sheetSelVp=null;
    }
    bimSheetViewRefresh();
  }
  function bimSheetPointerMove(ev){
    if(!A3D.sheetDrag||!el.sheetcv)return;
    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet){A3D.sheetDrag=null;return;}
    var vp=null,i;for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===A3D.sheetDrag.vpId){vp=sheet.viewports[i];break;}
    if(!vp){A3D.sheetDrag=null;return;}
    ev.preventDefault();
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    var dx=mm[0]-A3D.sheetDrag.startMM[0],dy=mm[1]-A3D.sheetDrag.startMM[1];
    if(A3D.sheetDrag.mode==='pan'){   /* __acad3dV116 */
      var pd=A3D.sheetDrag;
      if(!pd.orig){
        if(Math.abs(dx)<0.3&&Math.abs(dy)<0.3)return;   /* a click is not a pan */
        pushUndo();
        if(!bimSheetVpToRatio(vp)){A3D.sheetDrag=null;return;}
        pd.orig=[vp.pan[0],vp.pan[1]];
      }
      var mPerMM=vp.scaleDenom/1000;
      vp.pan=[pd.orig[0]-dx*mPerMM,pd.orig[1]+dy*mPerMM];
      bimSheetViewRefresh();
      return;
    }
    var o=A3D.sheetDrag.orig;
    if(A3D.sheetDrag.mode==='move'){
      vp.x=Math.max(0,Math.min(sheet.w-o.w,o.x+dx));
      vp.y=Math.max(0,Math.min(sheet.h-o.h,o.y+dy));
    }else{
      vp.w=Math.max(15,Math.min(sheet.w-o.x,o.w+dx));
      vp.h=Math.max(15,Math.min(sheet.h-o.y,o.h+dy));
    }
    bimSheetViewRefresh();
  }
  function bimSheetPointerUp(){
    if(A3D.sheetDrag){A3D.sheetDrag=null;saveSoon();}
  }
  function bimSheetDblClick(ev){
    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet||!el.sheetcv)return;
    var mm=bimSheetEvtToMM(ev,el.sheetcv);
    var hit=bimSheetHitTest(sheet,mm);
    /* __acad3dV116: double-click is the way into a viewport and back out, in AutoCAD and in Revit
       alike. It used to open the properties dialog, which is on the right-click menu now. A schedule
       has no model to work in, so its double-click still opens its properties. */
    if(hit&&hit.vp.kind!=='schedule'){bimSetModelSpace(hit.vp.id);return;}
    if(hit){bimOpenViewportPropsDlg(hit.vp.id);return;}
    bimSetPaperSpace();
  }
  function bimOpenNewSheetDlg(){
    closeDlg();
    var opts='',k;
    for(k in SHEET_SIZES)if(SHEET_SIZES.hasOwnProperty(k))opts+='<option value="'+k+'"'+(k===SHEET_NEW_SIZE?' selected':'')+'>'+SHEET_SIZES[k].label+'</option>';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">New Sheet</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Number</label><input type="text" data-a3dp="num" value="'+bimEsc(bimNextSheetNumber())+'"></div>'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="Untitled"></div>'+
      '<div class="a3d-dlgrow"><label>Size</label><select data-a3dp="size">'+opts+'</select></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var numI=d.querySelector('[data-a3dp="num"]'),nameI=d.querySelector('[data-a3dp="name"]'),sizeI=d.querySelector('[data-a3dp="size"]');
    function submit(){
      var num=numI.value.trim(),name=nameI.value.trim();
      if(!num){document.getElementById('a3d-dlgerr').textContent='Sheet number cannot be empty';return;}
      closeDlg();
      var s=bimAddSheet(num,name||'Untitled',sizeI.value);
      bimActivateView('sheet',s.id);   /* __acad3dV116: through the view path, so the view state says Sheet */
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    numI.focus();numI.select();
  }
  function bimOpenSheetPropsDlg(){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet){a3dToast('No sheet open');return;}
    closeDlg();
    var opts='',k;
    for(k in SHEET_SIZES)if(SHEET_SIZES.hasOwnProperty(k))opts+='<option value="'+k+'"'+(k===sheet.sizeKey?' selected':'')+'>'+SHEET_SIZES[k].label+'</option>';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Sheet Setup</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Number</label><input type="text" data-a3dp="num" value="'+bimEsc(sheet.number)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Name</label><input type="text" data-a3dp="name" value="'+bimEsc(sheet.name)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Size</label><select data-a3dp="size">'+opts+'</select></div>'+
      '<div class="a3d-dlgrow" id="a3d-sheetcustomrow" style="display:'+(sheet.sizeKey==='Custom'?'':'none')+'"><label>W x H (mm)</label>'+
        '<span><input type="number" step="any" min="10" data-a3dp="cw" value="'+sheet.w+'" style="width:48px"> x '+
        '<input type="number" step="any" min="10" data-a3dp="ch" value="'+sheet.h+'" style="width:48px"></span></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="del" style="margin-right:auto;color:#e08080">Delete Sheet</button><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var numI=d.querySelector('[data-a3dp="num"]'),nameI=d.querySelector('[data-a3dp="name"]'),sizeI=d.querySelector('[data-a3dp="size"]');
    var cwI=d.querySelector('[data-a3dp="cw"]'),chI=d.querySelector('[data-a3dp="ch"]'),custRow=d.querySelector('#a3d-sheetcustomrow');
    sizeI.addEventListener('change',function(){custRow.style.display=(sizeI.value==='Custom')?'':'none';});
    function submit(){
      var num=numI.value.trim(),name=nameI.value.trim();
      if(!num){document.getElementById('a3d-dlgerr').textContent='Sheet number cannot be empty';return;}
      /* __acad3dV116: a bad custom size used to be found after the undo step was taken and the number,
         name and size key were already changed -- half a Sheet Setup, kept. Checked first now. */
      var cw=parseFloat(cwI.value),ch=parseFloat(chI.value);
      if(sizeI.value==='Custom'&&(!isFinite(cw)||cw<10||!isFinite(ch)||ch<10)){document.getElementById('a3d-dlgerr').textContent='Custom size must be at least 10mm';return;}
      pushUndo();
      sheet.number=num;sheet.name=name||'Untitled';sheet.sizeKey=sizeI.value;
      if(sizeI.value==='Custom'){sheet.w=cw;sheet.h=ch;}
      else{sheet.w=SHEET_SIZES[sizeI.value].w;sheet.h=SHEET_SIZES[sizeI.value].h;}
      closeDlg();
      refreshBrowser();bimSheetViewRefresh();saveSoon();
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      var act=b.getAttribute('data-a3dlg');
      if(act==='ok')submit();
      else if(act==='del'){closeDlg();bimConfirmDeleteSheet(sheet.id);}   /* __acad3dV116: the one delete path */
      else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    numI.focus();numI.select();
  }
  function bimOpenAddViewportDlg(){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet){a3dToast('Open or create a sheet first');return;}
    closeDlg();
    var sources=bimSheetSourceOptions();
    if(!sources.length){a3dToast('Nothing to place yet -- add a level, view, section or schedule first');return;}
    var opts='',i;
    for(i=0;i<sources.length;i++)opts+='<option value="'+i+'">'+bimEsc(sources[i].label)+'</option>';
    var sopts='';
    for(i=0;i<SHEET_SCALES.length;i++)sopts+='<option value="'+SHEET_SCALES[i].denom+'"'+(SHEET_SCALES[i].denom===100?' selected':'')+'>'+SHEET_SCALES[i].label+'</option>';
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Add Viewport</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Source</label><select data-a3dp="src">'+opts+'</select></div>'+
      '<div class="a3d-dlgrow"><label>Scale</label><select data-a3dp="scale">'+sopts+'<option value="fit">Fit to viewport</option></select></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var srcI=d.querySelector('[data-a3dp="src"]'),scaleI=d.querySelector('[data-a3dp="scale"]');
    function submit(){
      var src=sources[parseInt(srcI.value,10)];
      if(!src){document.getElementById('a3d-dlgerr').textContent='Pick a source';return;}
      closeDlg();
      pushUndo();
      var vp=bimNewViewport(src.kind,src.refId,src.label);
      if(scaleI.value==='fit'){vp.scaleMode='fit';}
      else{vp.scaleMode='ratio';vp.scaleDenom=parseInt(scaleI.value,10)||100;vp.pan=bimSheetVpFitPan(vp)||[0,0];}   /* __acad3dV116: opens on the model */
      var maxX=Math.max(10,sheet.w-vp.w-10),maxY=Math.max(10,sheet.h-vp.h-10);
      vp.x=Math.min(maxX,10+sheet.viewports.length*8);vp.y=Math.min(maxY,10+sheet.viewports.length*8);
      sheet.viewports.push(vp);
      A3D.sheetSelVp=vp.id;
      bimSheetViewRefresh();saveSoon();
      a3dToast('Viewport added: '+src.label);
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
  }
  function bimOpenViewportPropsDlg(vpId){
    var sheet=bimSheetById(A3D.activeSheetId);if(!sheet)return;
    var vp=null,i;for(i=0;i<sheet.viewports.length;i++)if(sheet.viewports[i].id===vpId){vp=sheet.viewports[i];break;}
    if(!vp)return;
    closeDlg();
    var sopts='';
    var listed=false;
    for(i=0;i<SHEET_SCALES.length;i++){if(SHEET_SCALES[i].denom===vp.scaleDenom)listed=true;sopts+='<option value="'+SHEET_SCALES[i].denom+'"'+(vp.scaleMode==='ratio'&&SHEET_SCALES[i].denom===vp.scaleDenom?' selected':'')+'>'+SHEET_SCALES[i].label+'</option>';}
    /* __acad3dV116: a scale not in the list is shown as it is; OK used to set the first one listed */
    if(vp.scaleMode==='ratio'&&!listed&&isFinite(vp.scaleDenom))sopts='<option value="'+vp.scaleDenom+'" selected>1:'+vp.scaleDenom+'</option>'+sopts;
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Viewport: '+bimEsc(vp.label)+'</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Scale</label><select data-a3dp="scale">'+sopts+'<option value="fit"'+(vp.scaleMode==='fit'?' selected':'')+'>Fit to viewport</option></select></div>'+
      '<div class="a3d-dlgrow"><label>X (mm)</label><input type="number" step="any" data-a3dp="x" value="'+vp.x.toFixed(1)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Y (mm)</label><input type="number" step="any" data-a3dp="y" value="'+vp.y.toFixed(1)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Width (mm)</label><input type="number" step="any" min="15" data-a3dp="w" value="'+vp.w.toFixed(1)+'"></div>'+
      '<div class="a3d-dlgrow"><label>Height (mm)</label><input type="number" step="any" min="15" data-a3dp="h" value="'+vp.h.toFixed(1)+'"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="del" style="margin-right:auto;color:#e08080">Delete</button><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var scaleI=d.querySelector('[data-a3dp="scale"]'),xI=d.querySelector('[data-a3dp="x"]'),yI=d.querySelector('[data-a3dp="y"]'),
        wI=d.querySelector('[data-a3dp="w"]'),hI=d.querySelector('[data-a3dp="h"]');
    function submit(){
      var x=parseFloat(xI.value),y=parseFloat(yI.value),w=parseFloat(wI.value),h=parseFloat(hI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(x)||!isFinite(y)){eb.textContent='X/Y must be numbers';return;}
      if(!isFinite(w)||w<15||!isFinite(h)||h<15){eb.textContent='Width/Height must be at least 15mm';return;}
      pushUndo();
      vp.x=x;vp.y=y;vp.w=w;vp.h=h;
      var wasFit=(vp.scaleMode!=='ratio');
      if(scaleI.value==='fit')vp.scaleMode='fit';
      else{vp.scaleMode='ratio';vp.scaleDenom=parseInt(scaleI.value,10)||100;if(wasFit)vp.pan=bimSheetVpFitPan(vp)||[0,0];}   /* __acad3dV116: keeps where the fit looked */
      closeDlg();
      bimSheetViewRefresh();saveSoon();
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      var act=b.getAttribute('data-a3dlg');
      if(act==='ok')submit();
      else if(act==='del'){
        closeDlg();
        bimDeleteSheetViewport(vp.id);   /* __acad3dV116: the one delete path */
      }else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
    xI.focus();
  }
  function bimOpenTitleBlockDlg(){
    closeDlg();
    var tb=A3D.titleBlock||{project:'',client:'',drawnBy:'',checkedBy:''};
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Title Block Info</div>'+
      '<div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Project</label><input type="text" data-a3dp="project" value="'+bimEsc(tb.project||'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Client</label><input type="text" data-a3dp="client" value="'+bimEsc(tb.client||'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Drawn by</label><input type="text" data-a3dp="drawnBy" value="'+bimEsc(tb.drawnBy||'')+'"></div>'+
      '<div class="a3d-dlgrow"><label>Checked by</label><input type="text" data-a3dp="checkedBy" value="'+bimEsc(tb.checkedBy||'')+'"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      A3D.titleBlock={
        project:d.querySelector('[data-a3dp="project"]').value,
        client:d.querySelector('[data-a3dp="client"]').value,
        drawnBy:d.querySelector('[data-a3dp="drawnBy"]').value,
        checkedBy:d.querySelector('[data-a3dp="checkedBy"]').value
      };
      closeDlg();
      bimSheetViewRefresh();saveSoon();
    }
    d.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();
    });
    d.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}
      else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}
    });
  }
  function bimExportSheetPNG(){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet){a3dToast('No sheet open');return;}
    try{
      /* __acad3dV122: the layout's page at twice its pixels -- the same image size as before, with the
         title block, the labels and the text in the viewports the size they are on the sheet */
      var cv=bimRenderSheet(sheet,SHEET_PREVIEW_PXMM,true,null,SHEET_EXPORT_PXMM/SHEET_PREVIEW_PXMM);
      var dataURL=cv.toDataURL('image/png');
      var a=document.createElement('a');
      a.href=dataURL;a.download=bimFileStem()+'-'+(sheet.number||'sheet')+'.png';
      document.body.appendChild(a);a.click();document.body.removeChild(a);
      bimSheetViewRefresh();
      a3dToast('Exported '+bimFileStem()+'-'+(sheet.number||'sheet')+'.png');
    }catch(eP){
      console.warn('[BIM] Sheet PNG export failed: ',eP);
      a3dToast('Sheet export failed: '+(eP&&eP.message?eP.message:eP));
    }
  }
  /* __acad3dV57: real vector sheet printing/export, Phase 50b. 'plan' viewports get a true
     vector rebuild (bimBuildPlanViewportSVG) by re-deriving the exact plan-camera projection
     bimSheetSolveCamera/camVecs/toScreen already use (yaw is always 0 for a plan viewport, which
     lets the eye-to-target math cancel exactly rather than approximately -- see header comment
     above bimPrintSheet's replacement for the derivation). Elevation/saved-view/schedule
     viewports still rasterize (true 3D silhouette or tabular layout is a separate, larger
     feature) and are embedded as <image> elements inside the same vector page. Door/window
     opening cuts are still not drawn into wall outlines here -- a pre-existing, shared limitation
     with bimBuildDXF/bimBuildSVG (Phase 50), not a regression. */
  function bimBuildPlanViewportSVG(vp,src,xMM,yMM,wMM,hMM,mode){
    var pres=(mode==='presentation');
    var cam=bimSheetSolveCamera(src,wMM,hMM,1,vp.scaleMode,vp.scaleDenom,vp.pan);   /* __acad3dV116 */
    var cp=Math.cos(cam.pitch),sp=Math.sin(cam.pitch);
    var k=hMM*1.2/Math.max(cam.dist,0.5);
    function projPt(wx,wz,wy){
      var y=(wy==null||!isFinite(wy))?cam.ty:wy;
      var xc=wx-cam.tx;
      var yc=cp*(y-cam.ty)-sp*(wz-cam.tz);
      return [xMM+wMM/2+xc*k,yMM+hMM/2-yc*k];
    }
    var parts=[],strokeW=0.18,drew=false;
    var EX=[0,0,0];   /* __acad3dV104: the current object's offset, applied at projection */
    var projLocal=projPt;
    projPt=function(wx,wz,wy){
      return projLocal(wx+EX[0],wz+EX[2],(wy==null||!isFinite(wy))?wy:wy+EX[1]);
    };
    /* __acad3dV63: same under-the-model room ordering as bimBuildSVG -- see the comment there for
       why an opaque room fill drawn last is wrong. Room output is diverted into its own list and
       concatenated in FRONT at the end, and only when pres is on, so a technical viewport
       fragment is emitted in exactly the order it always was. */
    var roomParts=[],curRoom=false;
    function emit(str){(pres&&curRoom?roomParts:parts).push(str);}
    // This whole function already works in sheet-page millimetres, so a resolved lineWeight (also
    // mm, per bimDefaultGraphics) maps directly to stroke-width -- no diag-relative calibration
    // needed here, unlike bimBuildSVG's "fit to content" model-space viewBox.
    function styleAttrs(rg,fillOn){
      if(!bimPatternAlways(pres,rg))return {fill:'none',extra:''};   /* __acad3dV96 */
      var fillVal=(fillOn&&rg.fill!=='none')?rg.fill:'none';
      var extra=' stroke="'+rg.lineColor+'" stroke-width="'+Math.max(0.02,rg.lineWeight).toFixed(3)+'"'+(rg.opacity!==1?' opacity="'+rg.opacity+'"':'');
      return {fill:fillVal,extra:extra};
    }
    /* __acad3dV63: this builder is already in sheet-page millimetres, so units-per-mm is literally
       1 -- the same reason its lineWeight needs no calibration while bimBuildSVG's does. Getting
       these two the wrong way round is the one mistake that would still let every other check
       pass while printing hatch at the wrong density, so it is spelled out rather than inlined.
       The id prefix carries a global sequence number because a single sheet export concatenates
       several viewport fragments into one SVG document, and two fragments must never define
       different <pattern> elements under the same id. */
    var patReg=bimPatternRegistry(1,true,'a3dvpat'+(BIM_PAT_SVG_SEQ++)+'_');
    function patternOverlay(rg,objId,d,extraAttrs){
      if(!bimPatternAlways(pres,rg))return;   /* __acad3dV96 */
      var pf=patReg.resolve(rg);
      if(!pf)return;
      var op=(rg.opacity!==1)?' opacity="'+rg.opacity+'"':'';
      emit('<path'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+' data-pattern="'+bimEscXml(rg.pattern)+'"'+
                 op+(extraAttrs||'')+' d="'+d+'" fill="'+pf+'" stroke="none"/>');
    }
    function poly(pts,closed,objId,wy,rg,forFill,lk){   /* __acad3dV121: lk, the object drawn By Layer */
      if(!pts||pts.length<2)return;
      var q,d='';
      for(q=0;q<pts.length;q++){var p=projPt(pts[q][0],pts[q][1],wy);d+=(q?'L':'M')+p[0].toFixed(3)+','+p[1].toFixed(3)+' ';}
      if(closed)d+='Z';
      var st=styleAttrs(rg,forFill);
      emit('<path'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+(lk?bimLookPlotAttrs(lk,1,pres):'')+' d="'+d.trim()+'" fill="'+st.fill+'"/>');
      if(forFill&&closed)patternOverlay(rg,objId,d.trim(),'');
      drew=true;
    }
    // Wall poche: same evenodd outer-minus-inner ring technique as bimBuildSVG, and the same
    // exclusion for opening-broken walls (disjoint runs, not a closed ring -- see that function's
    // comment for the full reasoning).
    function poche(outer,inner,objId,wy,rg){
      if(!outer||outer.length<3||!inner||inner.length<3)return;
      var q,d='';
      for(q=0;q<outer.length;q++){var p=projPt(outer[q][0],outer[q][1],wy);d+=(q?'L':'M')+p[0].toFixed(3)+','+p[1].toFixed(3)+' ';}
      d+='Z ';
      for(q=0;q<inner.length;q++){var p2=projPt(inner[q][0],inner[q][1],wy);d+=(q?'L':'M')+p2[0].toFixed(3)+','+p2[1].toFixed(3)+' ';}
      d+='Z';
      var st=styleAttrs(rg,true);
      emit('<path'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+' fill-rule="evenodd" d="'+d.trim()+'" fill="'+st.fill+'"/>');
      patternOverlay(rg,objId,d.trim(),' fill-rule="evenodd"');
      drew=true;
    }
    function ln(a,b,objId,wy,rg,lk){
      var pa=projPt(a[0],a[1],wy),pb=projPt(b[0],b[1],wy);
      var st=styleAttrs(rg,false);
      emit('<line'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+st.extra+(lk?bimLookPlotAttrs(lk,1,pres):'')+' x1="'+pa[0].toFixed(3)+'" y1="'+pa[1].toFixed(3)+'" x2="'+pb[0].toFixed(3)+'" y2="'+pb[1].toFixed(3)+'"/>');
      drew=true;
    }
    function txt(pt,str,fsMM,objId,wy,rg){
      var p=projPt(pt[0],pt[1],wy);
      var fillColor=(pres&&rg)?rg.lineColor:'#000000';
      var opAttr=(pres&&rg&&rg.opacity!==1)?' opacity="'+rg.opacity+'"':'';
      emit('<text'+(objId?' data-obj="'+bimEscXml(objId)+'"':'')+opAttr+' x="'+p[0].toFixed(3)+'" y="'+p[1].toFixed(3)+'" font-size="'+fsMM.toFixed(3)+'" stroke="none" fill="'+fillColor+'">'+bimEscXml(str)+'</text>');
      drew=true;
    }
    var i;
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i];
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(src.levelFilter){
        var olv=bimObjectLevelId(o);
        if(olv&&olv!==src.levelId)continue;
      }
      var b=o.bim;
      EX=bimExportOffset(o);   /* __acad3dV104 */
      var rg=pres?bimResolveGraphics(o,'presentation'):null;
      if(b&&b.type==='wall'&&b.centerline){
        poly(b.centerline,!!b.closed,o.id,b.baseY,rg,false);
        if(b.innerLoop&&b.outerLoop){
          var brkP=bimWallOpeningBreaks(o);
          // Same "brkP is always truthy, even with no openings" caveat as bimBuildSVG above --
          // poche is only geometrically valid when the break result is really just the whole loop.
          var noOpeningsP=brkP&&brkP.outerClosed&&brkP.innerClosed&&brkP.outerRuns.length===1&&
            brkP.innerRuns.length===1&&!brkP.jambs.length&&!brkP.glaze.length;
          if(pres&&rg&&rg.fill!=='none'&&noOpeningsP){
            poche(b.outerLoop,b.innerLoop,o.id,b.baseY,rg);
          }else if(brkP){
            var bpi;
            for(bpi=0;bpi<brkP.outerRuns.length;bpi++)poly(brkP.outerRuns[bpi],brkP.outerClosed,o.id,b.baseY,rg,false);
            for(bpi=0;bpi<brkP.innerRuns.length;bpi++)poly(brkP.innerRuns[bpi],brkP.innerClosed,o.id,b.baseY,rg,false);
            for(bpi=0;bpi<brkP.jambs.length;bpi++)ln(brkP.jambs[bpi][0],brkP.jambs[bpi][1],brkP.jambs[bpi][2],b.baseY,rg);
            for(bpi=0;bpi<brkP.glaze.length;bpi++)ln(brkP.glaze[bpi][0],brkP.glaze[bpi][1],brkP.glaze[bpi][2],b.baseY,rg);
          }else{
            poly(b.innerLoop,true,o.id,b.baseY,rg,false);
            poly(b.outerLoop,true,o.id,b.baseY,rg,false);
          }
        }
      }else if(o.t==='room'){
        // Fill under the model (curRoom), label back on top with everything else -- see the
        // emit()/roomParts note above.
        curRoom=true;
        poly(o.pts,true,o.id,o.y,bimRoomSchemeGraphics(o,rg,pres),true);   /* __acad3dV105 */
        curRoom=false;
        if(!bimRoomTagged(o.id))txt(bimRoomLabelPoint(o),bimRoomLabelText(o),3.0,o.id,o.y,rg);   /* __acad3dV101 */
      }else if(bimIsHatch(o)){                  /* __acad3dV96 */
        poly(bimHatchOutline(o),true,o.id,o.y,bimHatchGraphics(o),true);
      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var shCL=bimClineVisibleSeg(o,null);
        if(shCL)ln(shCL[0],shCL[1],o.id,o.y,rg);
      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var shPM=bimPointMarkerSegs(o.pts[0]),shPK;
        for(shPK=0;shPK<shPM.length;shPK++)ln(shPM[shPK][0],shPM[shPK][1],o.id,o.y,bimLookPlotGraphics(o,rg),o);   /* __acad3dV121 */
      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,o.id,o.y,bimLookPlotGraphics(o,rg),false,o);   /* __acad3dV88; V121 By Layer */
      }else if(o.t==='dim'&&bimDimKind(o)==='linear'){
        ln(o.d1,o.d2,o.id,null,rg);ln(o.p1,o.d1,o.id,null,rg);ln(o.p2,o.d2,o.id,null,rg);
        txt([(o.d1[0]+o.d2[0])/2,(o.d1[1]+o.d2[1])/2],o.length.toFixed(2),2.4,o.id,null,rg);
      }else if(o.t==='dim'&&bimDimKind(o)==='angular'){
        ln(o.vertex,o.ap1,o.id,null,rg);ln(o.vertex,o.ap2,o.id,null,rg);
        var arcPts=[],ai;
        for(ai=0;ai<=16;ai++){
          var aa=o.a1+o.sweep*(ai/16);
          arcPts.push([o.vertex[0]+Math.cos(aa)*o.arcRadius,o.vertex[1]+Math.sin(aa)*o.arcRadius]);
        }
        poly(arcPts,false,o.id,null,rg,false);
        var midA=o.a1+o.sweep/2;
        txt([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25],o.degrees.toFixed(1)+'deg',2.4,o.id,null,rg);
      }else if(o.t==='dim'&&(bimDimKind(o)==='radius'||bimDimKind(o)==='diameter')){
        var cPts=[],ci2;
        for(ci2=0;ci2<=32;ci2++){
          var cc=(ci2/32)*Math.PI*2;
          cPts.push([o.center[0]+Math.cos(cc)*o.radius,o.center[1]+Math.sin(cc)*o.radius]);
        }
        poly(cPts,true,o.id,null,rg,false);
        ln(o.dStart,o.dEdge,o.id,null,rg);
        txt([(o.dStart[0]+o.dEdge[0])/2,(o.dStart[1]+o.dEdge[1])/2],(bimDimKind(o)==='diameter'?'D':'R')+o.value.toFixed(2),2.4,o.id,null,rg);
      }else if(o.t==='dim'&&bimDimKind(o)==='leader'){
        poly([o.anchor,o.elbow,o.landing],false,o.id,null,rg,false);
        txt(o.landing,o.label||'',2.4,o.id,null,rg);
      }else if(bimIsAlignment(o)){   /* __acad3dV127 */
        var axV=bimAlignExport(o),alV;
        poly(axV.pts,false,o.id,null,rg,false);
        for(alV=0;alV<axV.labels.length;alV++)txt(axV.labels[alV].p,axV.labels[alV].t,2.4,o.id,null,rg);
      }else if(bimIsProperty(o)){   /* __acad3dV103 */
        var pgV=bimPropertyGeometry(o),lkv;
        poly(pgV.ring,true,o.id,null,rg,false);
        for(lkv=0;lkv<o.legs.length&&lkv+1<pgV.pts.length;lkv++)
          txt([(pgV.pts[lkv][0]+pgV.pts[lkv+1][0])/2,(pgV.pts[lkv][1]+pgV.pts[lkv+1][1])/2],
              bimFormatBearing(o.legs[lkv].az)+' '+o.legs[lkv].d.toFixed(2),2.4,o.id,null,rg);
      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))txt(o.pt,bimRoomTagText(o),3.0,o.id,o.y,rg);
      }else if(o.t==='text'){
        txt(o.pt,o.text,3.0,o.id,o.y,rg);
      }else if(b&&(b.type==='floor'||b.type==='ceiling'||b.type==='roof')&&(b.profile||b.footprint)){
        poly(b.profile||b.footprint,true,o.id,b.baseY,rg,true);
      }else if(b&&b.type==='column'&&b.center){
        var c=b.center,hw=b.width/2,hd=b.depth/2;
        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,o.id,b.baseY,rg,true);
      }else if(bimIsFooting(o)&&b.plan){   /* __acad3dV102 */
        var fpv;
        for(fpv=0;fpv<b.plan.length;fpv++)poly(b.plan[fpv],true,o.id,b.baseY,rg,true);
      }
    }
    // __acad3dV63: patReg.defs() is the empty string in technical mode and whenever nothing on
    // this viewport carries a pattern, so an unhatched viewport's fragment is byte-identical to
    // its pre-Phase-53 output.
    return {svg:'<g fill="none" stroke="#000000" stroke-width="'+strokeW.toFixed(3)+'">'+patReg.defs()+
      roomParts.join('')+parts.join('')+'</g>',drew:drew};
  }
  // Raster fallback embed for viewport kinds the vector path does not cover (elevation/view/
  // schedule) or a 'plan' viewport whose vector build threw -- keeps current appearance exactly,
  // just re-hosted as an <image> inside the vector sheet page instead of the whole sheet being one.
  function bimRasterImageEmbed(src,vp,xMM,yMM,wMM,hMM){
    var pxPerMM=SHEET_EXPORT_PXMM;
    var destW=Math.max(1,wMM*pxPerMM),destH=Math.max(1,hMM*pxPerMM);
    try{
      var img=bimRenderSourceToCanvas(src,destW,destH,pxPerMM,vp.scaleMode,vp.scaleDenom,vp.pan);
      var durl=img.toDataURL('image/png');
      return '<image x="'+xMM.toFixed(3)+'" y="'+yMM.toFixed(3)+'" width="'+wMM.toFixed(3)+'" height="'+hMM.toFixed(3)+'" href="'+durl+'" xlink:href="'+durl+'" preserveAspectRatio="none"/>';
    }catch(eR){
      console.warn('[BIM] Sheet viewport raster embed failed: ',eR);
      return '<rect x="'+xMM.toFixed(3)+'" y="'+yMM.toFixed(3)+'" width="'+wMM.toFixed(3)+'" height="'+hMM.toFixed(3)+'" fill="#f4f4f4"/>';
    }
  }
  function bimBuildScheduleImageEmbed(vp,xMM,yMM,wMM,hMM){
    var pxPerMM=SHEET_EXPORT_PXMM;
    var destW=Math.max(1,Math.round(wMM*pxPerMM)),destH=Math.max(1,Math.round(hMM*pxPerMM));
    try{
      var scratch=bimGetScratchCanvas(destW,destH);
      var sctx=scratch.getContext('2d');
      sctx.clearRect(0,0,destW,destH);
      bimDrawScheduleViewport(sctx,vp,0,0,destW,destH);
      var durl=scratch.toDataURL('image/png');
      return '<image x="'+xMM.toFixed(3)+'" y="'+yMM.toFixed(3)+'" width="'+wMM.toFixed(3)+'" height="'+hMM.toFixed(3)+'" href="'+durl+'" xlink:href="'+durl+'" preserveAspectRatio="none"/>';
    }catch(eS){
      console.warn('[BIM] Sheet schedule embed failed: ',eS);
      return '<rect x="'+xMM.toFixed(3)+'" y="'+yMM.toFixed(3)+'" width="'+wMM.toFixed(3)+'" height="'+hMM.toFixed(3)+'" fill="#f4f4f4"/>';
    }
  }
  // Direct mm-unit translation of bimDrawTitleBlock -- that function already computes everything
  // in mm before multiplying by pxPerMM, so no pixel concept needs re-deriving here.
  function bimBuildTitleBlockSVG(sheet){
    var tbWmm=Math.min(90,sheet.w*0.42), tbHmm=Math.min(28,sheet.h*0.22);
    var x=sheet.w-tbWmm, y=sheet.h-tbHmm, w=tbWmm, h=tbHmm;
    var tb=A3D.titleBlock||{};
    var rowH=h/4,ri,parts=[];
    parts.push('<rect x="'+x.toFixed(3)+'" y="'+y.toFixed(3)+'" width="'+w.toFixed(3)+'" height="'+h.toFixed(3)+'" fill="#ffffff" stroke="#222222" stroke-width="0.35"/>');
    for(ri=1;ri<4;ri++){
      var ly=y+rowH*ri;
      parts.push('<line x1="'+x.toFixed(3)+'" y1="'+ly.toFixed(3)+'" x2="'+(x+w).toFixed(3)+'" y2="'+ly.toFixed(3)+'" stroke="#999999" stroke-width="0.15"/>');
    }
    var vx=x+w*0.62;
    parts.push('<line x1="'+vx.toFixed(3)+'" y1="'+(y+rowH*2).toFixed(3)+'" x2="'+vx.toFixed(3)+'" y2="'+(y+h).toFixed(3)+'" stroke="#999999" stroke-width="0.15"/>');
    function t(tx,ty,str,fs,bold,anchor){
      parts.push('<text x="'+tx.toFixed(3)+'" y="'+ty.toFixed(3)+'" font-size="'+fs+'" '+(bold?'font-weight="bold" ':'')+'text-anchor="'+(anchor||'start')+'" dominant-baseline="middle" fill="#222222">'+bimEscXml(str)+'</text>');
    }
    t(x+1.4,y+rowH*0.5,bimProjectLabel(),3.2,true);   /* __acad3dV115 */
    t(x+1.4,y+rowH*1.5,'Drawn by: '+(tb.drawnBy||'-')+'   Checked by: '+(tb.checkedBy||'-'),2.6,false);
    t(x+1.4,y+rowH*2.5,tb.client||'',2.6,false);
    t(vx+1.4,y+rowH*2.5,new Date().toLocaleDateString(),2.6,false);
    t(x+1.4,y+rowH*3.5-2.0,'Sheet Name',3.0,false);
    t(x+1.4,y+rowH*3.5+1.6,sheet.name||'Untitled',3.8,false);
    t(x+w-1.4,y+rowH*3,sheet.number||'',5.4,true,'end');
    return parts.join('');
  }
  // Builds one full sheet page as a single vector SVG: real vector geometry for 'plan' viewports,
  // raster <image> embeds for every other kind (or a 'plan' viewport that failed to resolve or
  // build), a vector title block, and vector borders/labels for every viewport regardless of kind.
  function bimBuildSheetSVG(sheet,mode){   /* __acad3dV121: a sheet's SVG and its print are plots */
    return bimWithPlotPass(mode==='presentation',function(){return bimBuildSheetSVGDrawing(sheet,mode);});
  }
  function bimBuildSheetSVGDrawing(sheet,mode){
    var W=sheet.w,H=sheet.h,defs=[],body=[],i;
    for(i=0;i<sheet.viewports.length;i++){
      var vp=sheet.viewports[i];
      var xMM=vp.x,yMM=vp.y,wMM=vp.w,hMM=vp.h;
      var clipId='a3dvpclip'+i;
      defs.push('<clipPath id="'+clipId+'"><rect x="'+xMM.toFixed(3)+'" y="'+yMM.toFixed(3)+'" width="'+wMM.toFixed(3)+'" height="'+hMM.toFixed(3)+'"/></clipPath>');
      var errMsg=null,inner='';
      if(vp.kind==='schedule'){
        inner=bimBuildScheduleImageEmbed(vp,xMM,yMM,wMM,hMM);
      }else{
        var src=bimResolveViewportSource(vp);
        if(src.error){
          errMsg=src.error;
        }else if(vp.kind==='plan'){
          try{
            inner=bimBuildPlanViewportSVG(vp,src,xMM,yMM,wMM,hMM,mode).svg;
          }catch(ePV){
            console.warn('[BIM] Vector plan viewport failed, falling back to raster: ',ePV);
            inner=bimRasterImageEmbed(src,vp,xMM,yMM,wMM,hMM);
          }
        }else{
          inner=bimRasterImageEmbed(src,vp,xMM,yMM,wMM,hMM);
        }
      }
      if(errMsg){
        console.warn('[BIM] Sheet viewport '+vp.id+' could not be resolved: '+errMsg);
        inner='<rect x="'+xMM.toFixed(3)+'" y="'+yMM.toFixed(3)+'" width="'+wMM.toFixed(3)+'" height="'+hMM.toFixed(3)+'" fill="#f4f4f4"/>'+
          '<text x="'+(xMM+wMM/2).toFixed(3)+'" y="'+(yMM+hMM/2).toFixed(3)+'" font-size="3.2" text-anchor="middle" dominant-baseline="middle" fill="#cc3333">'+bimEscXml(errMsg)+'</text>';
      }
      body.push('<g clip-path="url(#'+clipId+')">'+inner+'</g>');
      body.push('<rect x="'+(xMM+0.15).toFixed(3)+'" y="'+(yMM+0.15).toFixed(3)+'" width="'+Math.max(0,wMM-0.3).toFixed(3)+'" height="'+Math.max(0,hMM-0.3).toFixed(3)+'" fill="none" stroke="#888888" stroke-width="0.3"/>');
      var scaleTxt=vp.kind==='schedule'?'':(vp.scaleMode==='ratio'?(' — 1 : '+vp.scaleDenom):' — Fit');
      var lbl=(vp.label||'')+scaleTxt;
      body.push('<text x="'+(xMM+0.8).toFixed(3)+'" y="'+(yMM+hMM+2.6).toFixed(3)+'" font-size="3.0" font-weight="bold" fill="#222222">'+bimEscXml(lbl)+'</text>');
    }
    body.push(bimBuildTitleBlockSVG(sheet));
    return '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 '+W+' '+H+'" width="'+W+'mm" height="'+H+'mm" font-family="system-ui,sans-serif">\n'+
      '<defs>'+defs.join('')+'</defs>\n'+
      '<rect x="0" y="0" width="'+W+'" height="'+H+'" fill="#ffffff"/>\n'+
      '<rect x="0.4" y="0.4" width="'+(W-0.8)+'" height="'+(H-0.8)+'" fill="none" stroke="#333333" stroke-width="0.5"/>\n'+
      body.join('\n')+'\n</svg>\n';
  }
  function bimExportSheetSVG(){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet){a3dToast('No sheet open');return;}
    try{
      var svg=bimBuildSheetSVG(sheet,A3D.presentMode?'presentation':'technical');
      bimTriggerDownload(svg,bimFileStem()+'-'+(sheet.number||'sheet')+'.svg','image/svg+xml');
      a3dToast('Exported '+bimFileStem()+'-'+(sheet.number||'sheet')+'.svg (vector plan viewports; other kinds embedded as images)');
    }catch(eS){
      console.warn('[BIM] Sheet SVG export failed: ',eS);
      a3dToast('Sheet SVG export failed: '+(eS&&eS.message?eS.message:eS));
    }
  }
  // Fail-safe fallback to the previous PNG-embed print path -- kept verbatim (minus the function
  // name) so a vector-build failure degrades to exactly what shipped before this phase rather than
  // leaving Print non-functional.
  function bimPrintSheetRasterFallback(sheet){
    try{
      /* __acad3dV122: the layout's page at twice its pixels -- the same image size as before, with the
         title block, the labels and the text in the viewports the size they are on the sheet */
      var cv=bimRenderSheet(sheet,SHEET_PREVIEW_PXMM,true,null,SHEET_EXPORT_PXMM/SHEET_PREVIEW_PXMM);
      var dataURL=cv.toDataURL('image/png');
      bimSheetViewRefresh();
      var w=window.open('','_blank');
      if(!w){a3dToast('Could not open print window (popup blocked?)');return;}
      w.document.write('<html><head><title>'+bimEsc(bimSheetLabel(sheet))+'</title>'+
        '<style>@page{size:'+sheet.w+'mm '+sheet.h+'mm;margin:0} body{margin:0} img{width:'+sheet.w+'mm;height:'+sheet.h+'mm;display:block}</style>'+
        '</head><body><img src="'+dataURL+'" onload="window.focus();window.print();"></body></html>');
      w.document.close();
    }catch(eD2){
      console.warn('[BIM] Print sheet raster fallback also failed: ',eD2);
      a3dToast('Print failed: '+(eD2&&eD2.message?eD2.message:eD2));
    }
  }
  /* __acad3dV122: every page in the project's order, one print job -- the print dialog's Save as PDF
     makes the document a client is sent. Each page is the vector sheet on paper of its own size: a
     named @page per size (the first size is also the plain @page, for a browser without named
     pages). A page whose vector build fails goes in as its image, and the presenter is told. */
  function bimPrintSetHtml(){
    var Q=bimPresSeq(),n=Q.length,mode=A3D.presentMode?'presentation':'technical',sizes={},css='',body='',bad=[],lost=[],i,e,s,nm,svg,cv,first=true,brd=false;   /* __acad3dV162 */
    for(i=0;i<n;i++){
      e=Q[i];
      if(e.t==='board'){   /* __acad3dV162: a board on A3 landscape pages of its own, as it prints alone */
        if(!brd){brd=true;css+='@page a3dbrd{size:420mm 297mm;margin:10mm}';}
        try{body+='<div class="a3dbrd" data-page="'+bimEsc(e.id)+'" style="page:a3dbrd">'+bimBoardPrintHtml(bimBoardKey(e.b))+'</div>';}
        catch(eB){
          console.warn('[BIM] Page '+(i+1)+', the '+bimBoardLabel(e.b)+' board, could not be put together',eB);
          lost.push(i+1);
          body+='<div class="a3dbrd" data-page="'+bimEsc(e.id)+'"><div class="a3dpgerr">Page '+(i+1)+' ('+bimEsc(bimBoardLabel(e.b))+') could not be drawn</div></div>';
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
  function bimPrintSet(){
    if(!bimPresSeq().length){a3dToast('There are no pages to print yet: every sheet is a page');return false;}   /* __acad3dV162: a board is one too */
    var r;
    try{r=bimPrintSetHtml();}
    catch(eB){console.warn('[BIM] The set could not be put together for printing',eB);a3dToast('The set could not be printed -- see the console');return false;}
    var w=window.open('','_blank');
    if(!w){a3dToast('The print window was blocked -- allow pop-ups for this page and try again');return false;}
    try{w.document.write(r.html);w.document.close();}
    catch(eW){console.warn('[BIM] The print window could not be written',eW);a3dToast('The set could not be printed -- see the console');return false;}
    if(r.lost&&r.lost.length)a3dToast('Page'+(r.lost.length>1?'s ':' ')+r.lost.join(', ')+' could not be drawn -- see the console');   /* __acad3dV162 */
    else if(r.bad.length)a3dToast('Page'+(r.bad.length>1?'s ':' ')+r.bad.join(', ')+' printed from '+(r.bad.length>1?'their images':'its image')+': the vector drawing failed -- see the console');
    else a3dToast('Printing '+r.n+' page'+(r.n===1?'':'s')+' -- Save as PDF in the print dialog makes a PDF');
    return true;
  }
  function bimPrintSheet(){
    var sheet=bimSheetById(A3D.activeSheetId);
    if(!sheet){a3dToast('No sheet open');return;}
    try{
      var svg=bimBuildSheetSVG(sheet,A3D.presentMode?'presentation':'technical');
      var w=window.open('','_blank');
      if(!w){a3dToast('Could not open print window (popup blocked?)');return;}
      w.document.write('<html><head><title>'+bimEsc(bimSheetLabel(sheet))+'</title>'+
        '<style>@page{size:'+sheet.w+'mm '+sheet.h+'mm;margin:0} body{margin:0} svg{width:'+sheet.w+'mm;height:'+sheet.h+'mm;display:block}</style>'+
        '</head><body>'+svg+'<script>window.onload=function(){window.focus();window.print();};<\/script></body></html>');
      w.document.close();
    }catch(eD){
      console.warn('[BIM] Vector print build failed, falling back to raster: ',eD);
      a3dToast('Vector print failed, using raster fallback: '+(eD&&eD.message?eD.message:eD));
      bimPrintSheetRasterFallback(sheet);
    }
  }

