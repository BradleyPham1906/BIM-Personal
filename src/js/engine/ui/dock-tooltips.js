  /* ================= __acad3dV129: the dock's tooltips and its names ================= */
  var A3DR_MORE_ICON=ric('<circle cx="6" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="18" cy="12" r="1.3"/>');
  function bimDockLabelsOn(){var p=bimLoadUIPanelPrefs();return p.dockLabels!==false;}
  function bimSetDockLabels(on){
    var p=bimLoadUIPanelPrefs();p.dockLabels=!!on;bimSaveUIPanelPrefs(p);
    bimBuildDock();
    a3dToast(on?'Tool names are shown on the dock':'The dock shows icons only; hover a tool for its name');
  }
  /* what a tooltip says: the tool's name, its keys, what to type for it, what it does, where it is */
  function bimDockTipData(spec){
    if(spec==='__search')return {name:'Search tools and commands',keys:[A3D_MODKEY,'K'],desc:'Or just start typing a command on the drawing',type:[],where:''};
    if(spec==='__all')return {name:'All tools and shortcuts',keys:['?'],desc:'Every tool and key: search, filter, sort, and pin tools to the dock',type:[],where:''};   /* __acad3dV130 */
    var cat=bimCmdCatalog(),cad=BIM_ACT_CMD[spec],it=null,i;
    for(i=0;i<cat.length;i++)if((cad&&cat[i].cad===cad)||cat[i].act===spec||cat[i].ribbon===spec){it=cat[i];break;}
    if(a3drIsUnimpl(spec))return {name:a3drLabel(spec),keys:null,desc:'Not built yet',type:[],where:'',off:true};
    if(!it)return {name:a3drLabel(spec),keys:null,desc:'',type:[],where:''};
    return {name:a3drLabel(spec),keys:it.keys,desc:it.desc,type:[it.name].concat(it.aliases.slice(0,1)),where:it.where[0]||''};
  }
  function bimDockTipHtml(spec){
    var d=bimDockTipData(spec),h='<div class="a3d-tiphd"><strong>'+bimEsc(d.name)+'</strong>',k;
    if(d.keys){h+='<span class="a3d-tipkeys">';for(k=0;k<d.keys.length;k++)h+=(k?'<i>+</i>':'')+'<kbd>'+bimEsc(d.keys[k])+'</kbd>';h+='</span>';}
    h+='</div>';
    if(d.type.length)h+='<div class="a3d-tiptype">Type '+d.type.map(function(x){return '<b>'+bimEsc(x)+'</b>';}).join(' or ')+'</div>';
    if(d.desc)h+='<div class="a3d-tipdesc'+(d.off?' off':'')+'">'+bimEsc(d.desc)+'</div>';
    if(d.where)h+='<div class="a3d-tipwhere">'+bimEsc(d.where)+'</div>';
    return h;
  }
  var A3D_TIP={el:null,timer:null,at:null};
  function bimTipHide(){
    if(A3D_TIP.timer){clearTimeout(A3D_TIP.timer);A3D_TIP.timer=null;}
    if(A3D_TIP.el)A3D_TIP.el.classList.remove('show');
    if(A3D_TIP.at){A3D_TIP.at.removeAttribute('aria-describedby');A3D_TIP.at=null;}
  }
  function bimTipShow(target){
    var spec=target&&target.getAttribute('data-a3dtip');
    if(!spec||!document.body.contains(target))return;
    var el=A3D_TIP.el;
    if(!el){el=A3D_TIP.el=document.createElement('div');el.id='a3d-tip';el.setAttribute('role','tooltip');document.body.appendChild(el);}
    el.innerHTML=bimDockTipHtml(spec);
    el.classList.add('show');
    var r=target.getBoundingClientRect(),w=el.offsetWidth,hh=el.offsetHeight;
    var left=Math.max(8,Math.min(window.innerWidth-w-8,r.left+r.width/2-w/2)),top=r.top-hh-10;
    if(top<8)top=r.bottom+10;
    el.style.left=Math.round(left)+'px';el.style.top=Math.round(top)+'px';
    target.setAttribute('aria-describedby','a3d-tip');A3D_TIP.at=target;
  }
  /* after a short pause on hover (so a pointer passing over does not flash them), at once on focus */
  function bimBindDockTips(host){
    if(host.getAttribute('data-tips'))return;
    host.setAttribute('data-tips','1');
    host.addEventListener('mouseover',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-a3dtip]'):null;
      if(!tg||tg===A3D_TIP.at)return;
      bimTipHide();
      A3D_TIP.timer=setTimeout(function(){A3D_TIP.timer=null;bimTipShow(tg);},350);
    });
    host.addEventListener('mouseout',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-a3dtip]'):null;
      if(tg&&!(ev.relatedTarget&&tg.contains(ev.relatedTarget)))bimTipHide();
    });
    host.addEventListener('focusin',function(ev){
      var tg=ev.target&&ev.target.closest?ev.target.closest('[data-a3dtip]'):null;
      bimTipHide();if(tg&&tg.matches(':focus-visible'))bimTipShow(tg);
    });
    host.addEventListener('focusout',bimTipHide);
    host.addEventListener('pointerdown',bimTipHide,true);
    host.addEventListener('keydown',function(ev){if(ev.key==='Escape')bimTipHide();});
    window.addEventListener('scroll',bimTipHide,true);
  }
  var A3DR_ALL_ICON=ric('<rect x="4" y="4" width="6" height="6" rx="1"/><rect x="14" y="4" width="6" height="6" rx="1"/><rect x="4" y="14" width="6" height="6" rx="1"/><rect x="14" y="14" width="6" height="6" rx="1"/>');   /* __acad3dV130 */
  var A3DR_PIN_ICON=ric('<path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z"/>');
  var A3DR_SEARCH_ICON=ric('<circle cx="11" cy="11" r="6"/><path d="M16 16l4 4"/>');
  /* Every action in every tab, with the tab and panel it came from so a result can say where it
     lives. Rebuilt per query rather than cached: A3DR_TABS is extensible at runtime through
     a3drRegisterTab, and a stale index is a tool that cannot be found. */
  function a3drAllCommands(){
    var out=[],seen={},i,j,k,t,p,a;
    for(i=0;i<A3DR_TABS.length;i++){
      t=A3DR_TABS[i];
      for(j=0;j<t.panels.length;j++){
        p=t.panels[j];
        if(p.big)for(k=0;k<p.big.length;k++){
          a=a3drActOf(p.big[k]);
          if(!seen[a]){seen[a]=1;out.push({act:a,tab:t,panel:p.t});}
          if(p.big[k].menu){var m;for(m=0;m<p.big[k].menu.length;m++){
            a=p.big[k].menu[m][0];
            if(!seen[a]){seen[a]=1;out.push({act:a,tab:t,panel:p.t});}
          }}
        }
        if(p.small)for(k=0;k<p.small.length;k++){
          a=p.small[k];
          if(!seen[a]){seen[a]=1;out.push({act:a,tab:t,panel:p.t});}
        }
      }
    }
    return out;
  }
  var A3D_DOCK_BOUND=false;
  function bimBindDock(){
    if(A3D_DOCK_BOUND)return;
    var host=document.getElementById('a3d-dock');
    if(!host)return;
    A3D_DOCK_BOUND=true;
    host.addEventListener('click',function(ev){
      /* __acad3dV130: All tools opens the panel */
      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-dall')){ev.stopPropagation();bimOpenToolsPanel();return;}
      /* __acad3dV128: the magnifier opens THE command search, not a second one */
      var sbtn=ev.target&&ev.target.closest?ev.target.closest('#a3d-dsearch'):null;
      if(sbtn){
        ev.stopPropagation();
        if(window.openPalette)window.openPalette();
        return;
      }
      /* Any other click inside the dock is a command; the document dispatcher runs it. */
    });
    host.addEventListener('change',function(ev){
      if(ev.target&&ev.target.id==='a3d-discsel'){
        A3D_DISC_CUR=ev.target.value;
        bimBuildDock();
        a3dToast('Discipline: '+ev.target.options[ev.target.selectedIndex].text);
      }
    });
  }
  document.addEventListener('click',function(ev){
    var t=ev.target;
    if(!t||!t.closest)return;
    var b=t.closest('[data-a3dr]');
    if(!b||!A3D.on)return;
    var ra=b.getAttribute('data-a3dr');
    if(bimRunAct(ra)!==false&&(b.closest('#a3d-dock')||b.closest('#a3d-rupop')))bimActUsed(ra);   /* __acad3dV130 */
  });
  /* __acad3dV128: a ribbon action, run as its button runs it -- by a click, or from the command
     search. false when it was refused or is not a command; anything else ran. */
  function bimRunAct(act){
    if(bimSheetOnScreen()&&!BIM_SHEET_ACTS[act]){a3dToast('That works on the model: go to the Model tab first');return false;}   /* __acad3dV116 */
    /* __acad3dV71: registered commands run first, so a domain pack does not have to reach into
       the 60-branch chain below -- and can deliberately override a built-in for its domain. */
    var xr=a3drExt(act);
    if(xr){
      if(xr.unimpl){a3dToast(a3drLabel(act)+' is not implemented yet');return false;}
      if(xr.run){xr.run(act);return;}
    }
    if(act.indexOf('s:')===0){startSketch(act.slice(2));return;}
    if(act.indexOf('con:')===0){startConstraintTool(act.slice(4));return;}
    if(act==='p:pad'){openPadDlg('pad');return;}
    if(act==='p:pocket'){openPadDlg('pocket');return;}
    if(act==='bim:wall'){startWallTool();return;}
    if(act==='bim:floor'){startFloorTool();return;}
    if(act==='bim:room'){startRoomTool();return;}
    if(act==='bim:tagroom'){startRoomTagTool();return;}       /* __acad3dV101 */
    if(act==='bim:footing'){startFootingTool('column');return;}  /* __acad3dV102 */
    if(act==='bim:foundwall'){startFootingTool('wall');return;}
    if(act==='bim:foundslab'){startFoundationSlabTool();return;}
    if(act==='bim:property'){openPropertyDlg(null);return;}              /* __acad3dV103 */
    if(act==='bim:propshape'){bimPropertyFromSketch(objById(A3D.sel));return;}
    if(act==='bim:truenorth'){openTrueNorthDlg();return;}
    if(act==='bim:alignment'){bimAlignmentCommand();return;}
    if(act==='bim:usage'){bimUsageCommand();return;}                    /* __acad3dV131 */
    if(act==='bim:usages'){bimUsageLibraryCommand();return;}
    if(act==='bim:map'){bimMapCommand();return;}                         /* __acad3dV132 */
    if(act==='bim:findaddress'){openFindAddressDlg();return;}
    if(act==='bim:geoimport'){bimGeoImportPick();return;}
    if(act==='m:exportgeojson'){bimGeoExport();return;}
    if(act==='bim:context'){bimCtxFetch();return;}                      /* __acad3dV133 */
    if(act==='bim:datalayers'){bimDataCommand();return;}                /* __acad3dV134 */            /* __acad3dV127 */
    if(act==='bim:tagallrooms'){bimTagAllRooms();return;}     /* __acad3dV101 */
    if(act==='bim:roof'){startRoofTool();return;}
    if(act==='bim:stair'){startStairTool();return;}
    if(act==='bim:dim'){startDimTool();return;}
    if(act==='bim:text'){startTextTool();return;}
    if(act==='bim:section'){startSectionTool();return;}
    if(act==='bim:ceiling'){startCeilingTool();return;}
    if(act==='bim:offset'){openOffsetDlg();return;}
    if(act==='bim:trim'){startTrimTool();return;}
    if(act==='bim:align'){openAlignDlg();return;}
    if(act==='bim:mergewalls'){applyMergeWalls();return;}
    if(act==='bim:checkmodel'){openCheckModelDlg();return;}
    if(act==='bim:clonelinked'){openCloneLinkedDlg();return;}
    if(act==='bim:syncclones'){applySyncClones();return;}
    if(A3DR_UNIMPL[act]){a3dToast(a3drLabel(act)+' is not implemented yet');return false;}
    if(act==='bim:component'){bimOpenLibraryAt('families');return;}   /* __acad3dV124 */
    if(act==='bim:famsave'){openSaveAsFamilyDlg();return;}
    if(act==='bim:famimport'){var ffi=document.getElementById('a3d-famfilein');if(ffi){ffi.value='';ffi.click();}return;}
    if(act==='bim:linkifc'||act==='bim:importcad'){var fi2=document.getElementById('a3d-filein');if(fi2){fi2.value='';fi2.click();}return;}
    if(act==='bim:saveview'){bimSaveCurrentView();return;}
    if(act==='bim:sheet'){if(A3D.sheets.length){bimActivateView('sheet',A3D.activeSheetId&&bimSheetById(A3D.activeSheetId)?A3D.activeSheetId:A3D.sheets[0].id);}else{bimOpenNewSheetDlg();}return;}   /* __acad3dV116 */
    if(act==='bim:titleblock'){bimOpenTitleBlockDlg();return;}
    if(act==='bim:level'){if(typeof openAddLevelDlg==='function')openAddLevelDlg();else a3dToast('Add a level from the Project Browser');return;}
    if(act==='bim:layers'||act==='bim:levels'){a3dToast('Manage these in the Project Browser');return;}
    if(act==='bim:classification'){openClassificationDlg();return;}
    if(act==='bim:uipanels'){var um=document.getElementById('a3d-uimenu');if(um)um.classList.toggle('open');return;}
    if(act==='bim:dimang'){startAngularDimTool();return;}
    if(act==='bim:dimrad'){startRadialDimTool(false);return;}
    if(act==='bim:dimdia'){startRadialDimTool(true);return;}
    if(act==='bim:leader'){startLeaderTool();return;}
    if(act==='bim:beam'){startBeamTool();return;}
    if(act==='bim:analyze'){bimAnalyzeCommand();return;}   /* __acad3dV125 */
    if(act==='bim:grid'){startGridTool();return;}
    if(act==='bim:column'){startColumnTool();return;}
    if(act==='bim:door'){startDoorTool();return;}
    if(act==='bim:window'){startWindowTool();return;}
    if(act==='v:fit'){fitScene();return;}
    if(act==='v:iso'){setView('iso');return;}
    if(act.indexOf('v:')===0){setView(act.slice(2));return;}
    if(act.indexOf('b:')===0){doBool(act.slice(2));return;}
    if(act==='m:del'){delSelection();return;}
    if(act==='m:dup'){duplicateSelection();return;}
    if(act==='m:array'){openArrayDlg();return;}
    if(act==='m:exportpng'){bimExportPNG();return;}
    if(act==='m:exportpdf'){bimExportPDF();return;}
    if(act==='m:exportdxf'){bimExportDXF();return;}
    if(act==='m:exportsvg'){bimExportSVG();return;}
    if(act==='m:saveproj'){bimExportProjectFile();return;}
    if(act==='m:openproj'){bimOpenProjectPicker();return;}   /* __acad3dV115: opens in a tab of its own */
    if(act==='m:exitsection'){bimExitSection();return;}
    if(act==='m:flipsection'){bimFlipSection();return;}
    if(act==='bim:mirror'){startMirrorTool();return;}
    if(act==='bim:rotate'){startRotateTool();return;}
    if(act==='bim:polararray'){startPolarArrayTool();return;}
    if(act==='bim:joinwalls'){applyWallJoin();return;}
    if(act==='bim:extend'){startExtendTool();return;}
    if(act==='bim:arc'){startArcTool();return;}
    if(act==='bim:fillet'){applyFilletCorner();return;}
    if(act==='bim:chamfer'){startChamferTool();return;}
    if(act==='bim:break'){startBreakTool(false);return;}
    if(act==='bim:lengthen'){startLengthenTool();return;}
    if(act==='bim:scale'){startScaleTool();return;}
    if(act==='bim:presspull'){bimPressPullCommand();return;}   /* __acad3dV123 */
    if(act==='m:desel'){A3D.sel=null;A3D.sel2=null;A3D.selSet=[];refreshTree();paint();return;}
    if(TYPES[act]){openDlg(act);return;}
    return false;
  }

