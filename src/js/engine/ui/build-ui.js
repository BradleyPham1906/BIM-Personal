  // ---- __acad3dV20: UI panel visibility dropdown, matching the "show/hide panels" convention
  // from Revit's User Interface button / AutoCAD's palette toggles. Deliberately does NOT let
  // the toolbar itself be hidden (that's where the toggle control lives) -- same
  // restriction Revit's own dropdown has. Preferences persist separately from project data
  // (a user preference, not model content) so they survive across different projects. ----
  /* __acad3dV67: the 'snappill' KEY is kept although the pill is gone, so a user who had
     already hidden the snap toggles keeps them hidden -- the saved preference is about the
     controls, not about the element that used to host them. Only the target and label move. */
  var UI_PANEL_MAP={sidebar:'.a3d-tree',snappill:'#a3d-snapgrp',navpill:'#a3d-navgrp',hud:'.a3d-hud'};
  var UI_PANEL_PREF_KEY='acad3dUIPrefs';
  function bimLoadUIPanelPrefs(){
    try{
      var raw=localStorage.getItem(UI_PANEL_PREF_KEY);
      if(raw)return JSON.parse(raw)||{};
    }catch(eL){}
    return {};
  }
  function bimSaveUIPanelPrefs(prefs){
    try{localStorage.setItem(UI_PANEL_PREF_KEY,JSON.stringify(prefs));}catch(eS){}
  }
  function bimSetUIPanelVisible(key,visible){
    var sel=UI_PANEL_MAP[key];
    if(!sel)return;
    var els=document.querySelectorAll(sel),i;
    for(i=0;i<els.length;i++)els[i].classList.toggle('a3d-hide-panel',!visible);
    var prefs=bimLoadUIPanelPrefs();
    prefs[key]=visible;
    bimSaveUIPanelPrefs(prefs);
  }
  function bimApplyUIPanelPrefs(root){
    var prefs=bimLoadUIPanelPrefs(),key;
    for(key in UI_PANEL_MAP){
      if(!UI_PANEL_MAP.hasOwnProperty(key)||!prefs.hasOwnProperty(key))continue;
      var visible=prefs[key],sel=UI_PANEL_MAP[key];
      var els=root.querySelectorAll(sel),i;
      for(i=0;i<els.length;i++)els[i].classList.toggle('a3d-hide-panel',!visible);
      var cb=root.querySelector('[data-a3dui="'+key+'"]');
      if(cb)cb.checked=visible;
    }
  }
  function buildUI(){
    if(A3D.built)return;
    A3D.built=true;
    /* __acad3dV120: the engine's rules are in the stylesheet in <head>. */
    var root=document.createElement('div');
    root.id='acad3d';
    root.innerHTML=''+
    '<div class="a3d-tb">'+
      '<button class="a3d-btn a3d-drawerbtn" data-a3d="drawer" title="Show panel">\u2630</button>'+
      '<button class="a3d-btn a3d-rdrawerbtn" data-a3d="rdrawer" title="Show properties">Props</button>'+
      '<input type="file" id="a3d-filein" accept=".dxf,.ifc,.obj,.stl,.skp,.json,.geojson,.kml,.cityjson,.xml,.landxml" style="display:none">'+
      '<input type="file" id="a3d-projin" accept=".json" style="display:none">'+   /* __acad3dV115 */
      '<span class="a3d-hud">View: <b id="a3d-view">Home</b><span id="a3d-count">0 objects</span></span>'+
      '<span class="a3d-uiwrap">'+
        '<div id="a3d-uimenu" class="a3d-uimenu">'+
          '<label><input type="checkbox" data-a3dui="sidebar" checked> Model Browser</label>'+
          '<label><input type="checkbox" data-a3dui="snappill" checked> Snap Toggles</label>'+
          '<label><input type="checkbox" data-a3dui="navpill" checked> Navigation Pill</label>'+
          '<label><input type="checkbox" data-a3dui="hud" checked> View HUD</label>'+
        '</div>'+
      '</span>'+
      '</div>'+
      '<div class="a3d-body">'+
      '<div class="a3d-tree">'+
        /* __acad3dV68: Properties is wrapped so the header and body move to the right panel as
           ONE node. They were siblings of the Project Browser's header, so moving them apart
           would have meant two appendChild calls and two chances to leave the palette half
           split if one of them threw. */
        '<div id="a3d-propssec">'+
          '<div class="a3d-palhd"><span id="a3d-rpttl">Properties</span></div>'+   /* __acad3dV166d: the name its edge takes */
          '<div id="a3d-propsbody" class="a3d-propsbody"></div>'+
        '</div>'+
        '<div class="a3d-palhd a3d-palhd2">Project Browser'+
          '<span class="a3d-palbtns">'+
            '<button class="a3d-palbtn" id="a3d-viewsave" title="Save current camera as a named view">+View</button>'+
            '<button class="a3d-palbtn" id="a3d-sheetadd" title="New Sheet">+Sht</button>'+
            '<button class="a3d-palbtn" id="a3d-lvladd" title="Add Level">+Lvl</button>'+
            '<button class="a3d-palbtn" id="a3d-bldadd" title="Add Building">+Bldg</button>'+
            '<button class="a3d-palbtn" id="a3d-famsave" title="Save selection as a Family">+Fam</button>'+
            '<button class="a3d-palbtn" id="a3d-famimport" title="Import OBJ/STL as a Family">Imp</button>'+
          '</span>'+
        '</div>'+
        '<input type="file" id="a3d-famfilein" accept=".obj,.stl,.skp" style="display:none">'+
        '<div class="a3d-bsearch"><input type="text" id="a3d-bsearch" placeholder="Search"></div>'+
        '<div id="a3d-browser" class="a3d-browser"></div>'+
        '<div id="a3d-schedwrap" class="a3d-schedwrap">'+
          '<div class="a3d-palhd a3d-palhd2"><span id="a3d-schedtitle">Schedule</span>'+
            '<span class="a3d-palbtns">'+
              '<button class="a3d-palbtn" id="a3d-schedcsv" title="Export as CSV">CSV</button>'+
              '<button class="a3d-palbtn" id="a3d-schedclose" title="Close">\u00d7</button>'+
            '</span></div>'+
          /* __acad3dV74: options are generated from SCHEDULE_DEFS by bimSyncScheduleCats, so a
             registered schedule cannot be listed in the browser and then fail to open here. */
          '<select id="a3d-schedcat" style="display:none"></select>'+
          '<div id="a3d-schedbody" class="a3d-schedbody"></div>'+
        '</div>'+
        '<div id="a3d-rows" style="display:none"></div>'+
        '<div id="a3d-lvlrows" style="display:none"></div>'+
        '<div id="a3d-viewrows" style="display:none"></div>'+
      '</div>'+
      '<div class="a3d-vp"><canvas id="a3d-gpucanvas"></canvas><canvas id="a3d-glcanvas"></canvas><canvas id="a3d-canvas"></canvas>'+
      '<div id="a3d-sheetview" class="a3d-sheetview">'+
        '<div class="a3d-sheettb">'+
          /* __acad3dV122: the sheet alone to edit, or every sheet as pages */
          '<span class="a3d-shdisp" role="group" aria-label="Sheet display">'+
            '<button class="a3d-btn a3d-shdbtn on" data-shdisp="layout" title="This sheet alone, to edit its layout">Layout</button>'+
            '<button class="a3d-btn a3d-shdbtn" data-shdisp="pages" title="Every sheet as pages in one scroll, like a PDF">Pages</button>'+
          '</span>'+
          '<span id="a3d-sheetnum" class="a3d-sheetnum">Sheet</span>'+
          '<span class="a3d-sheetsp"></span>'+
          '<span class="a3d-pgonly a3d-pgnav">'+
            '<button class="a3d-btn" id="a3d-pgprev" title="Previous page" aria-label="Previous page">\u2039</button>'+
            '<input id="a3d-pgnum" class="a3d-pgnum" type="text" inputmode="numeric" aria-label="Page number" value="1">'+
            '<span id="a3d-pgof" class="a3d-pgof">of 1</span>'+
            '<button class="a3d-btn" id="a3d-pgnext" title="Next page" aria-label="Next page">\u203a</button>'+
          '</span>'+
          '<select id="a3d-pgzoom" class="a3d-pgonly a3d-pgzoom" aria-label="Zoom"></select>'+
          '<button class="a3d-btn a3d-pgonly" id="a3d-pgprint" title="Print every page in one go -- Save as PDF in the print dialog makes the client\'s PDF">Print set</button>'+   /* __acad3dV122 */
          '<button class="a3d-btn a3d-lyonly" id="a3d-sheetaddvp" title="Add a viewport referencing an existing view or schedule">+ Viewport</button>'+
          '<button class="a3d-btn a3d-lyonly" id="a3d-sheetprops" title="Sheet properties">Sheet Setup</button>'+
          '<button class="a3d-btn a3d-lyonly" id="a3d-sheettbedit" title="Edit title block info">Title Block</button>'+
          '<button class="a3d-btn a3d-lyonly" id="a3d-sheetpng" title="Export sheet as PNG">Export PNG</button>'+
          '<button class="a3d-btn a3d-lyonly" id="a3d-sheetsvg" title="Export sheet as vector SVG">Export SVG</button>'+
          '<button class="a3d-btn a3d-btn-pri a3d-lyonly" id="a3d-sheetprint" title="Print sheet (vector)">Print</button>'+
          '<button class="a3d-btn a3d-btn-pri" id="a3d-sheetpresent" title="Present the pages full screen, one at a time, from this one">Present</button>'+   /* __acad3dV122 */
          '<button class="a3d-btn" id="a3d-sheetclose" title="Close (back to model)">× Close</button>'+
        '</div>'+
        '<div class="a3d-sheetwrap"><canvas id="a3d-sheetcanvas"></canvas></div>'+
        '<div class="a3d-pageswrap" id="a3d-pageswrap"><div class="a3d-pagescol" id="a3d-pagescol"></div></div>'+   /* __acad3dV122 */
      '</div>'+
      '<div id="a3d-touchlen" class="a3d-touchlen">'+
        '<span class="a3d-tl-hint">Drag to place the first point</span>'+
        '<input type="text" inputmode="decimal" id="a3d-touchlen-input" placeholder="length">'+
        '<button class="a3d-tl-set" id="a3d-touchlen-set">Set</button>'+
      '</div>'+
      /* __acad3dV67: the floating snap pill moved into the status bar. Two surfaces carrying
         the same three A3D_SNAP toggles would be duplicate controls.
         __acad3dV109: the navigation pill followed it, on the owner's call -- pan, orbit, the
         2D/3D switch and Tech/Pres sit in the bar beside SNAP, ORTHO and GRID, and nothing
         floats over the drawing. */
      '<div id="a3d-mapattr" class="a3d-mapattr" hidden></div>'+   /* __acad3dV132: the map's credit */
      '<div id="a3d-dock"></div>'+
      '</div>'+
      '<div id="a3d-right"></div>'+
    '</div>'+
    '<div class="a3d-status" id="a3d-statusbar">'+
      '<span id="a3d-laytabs" class="a3d-laytabs"></span>'+   /* __acad3dV116: Model and layout tabs */
      '<span id="a3d-sthint" class="a3d-sthint"></span>'+
      '<span class="a3d-stspring"></span>'+
      '<button class="a3d-stbtn a3d-stspace" id="a3d-stspace" title="Paper space or model space on this sheet (MSPACE / PSPACE)">PAPER</button>'+
      '<label class="a3d-stlvl" title="Active level -- new walls, floors and sketches are placed here">'+
        'Level <select id="a3d-stlevel"></select></label>'+
      '<span id="a3d-stcoords" class="a3d-stcoords" title="Cursor position on the active level plane">\u2014</span>'+
      '<span id="a3d-snapgrp">'+
        '<button class="a3d-stbtn" data-a3dsnap="point" title="Object snap (F3)">'+PILL_SNAP+'<span>SNAP</span></button>'+
        '<button class="a3d-stbtn" data-a3dsnap="ortho" title="Ortho lock (F8)">'+PILL_ORTHO+'<span>ORTHO</span></button>'+
        '<button class="a3d-stbtn" data-a3dsnap="grid" title="Grid snap (F9)">'+PILL_GRID+'<span>GRID</span></button>'+
      '</span>'+
      '<span id="a3d-navgrp">'+   /* __acad3dV109: the view controls, beside the drawing aids */
        '<button class="a3d-stbtn" data-a3dnav="pan" title="Pan">'+PILL_PAN+'<span>PAN</span></button>'+
        '<button class="a3d-stbtn on" data-a3dnav="orbit" title="Orbit">'+PILL_ORBIT+'<span>ORBIT</span></button>'+
        '<button class="a3d-stbtn a3d-stview" id="a3d-flip" data-a3dnav="flip" title="Go to 2D (Shift + &gt;)">2D</button>'+
        '<button class="a3d-stbtn a3d-stview" id="a3d-present" data-a3dnav="present" title="Toggle Presentation appearance (graphic overrides from Phase 51)">Tech</button>'+
      '</span>'+
      '<span id="a3d-animgrp" hidden>'+   /* __acad3dV170: the site analysis in motion */
        '<button class="a3d-stbtn" id="a3d-animplay" data-a3danim="play" aria-pressed="false" aria-label="Play" title="Play the site analysis in motion">'+PILL_PLAY+'<span>PLAY</span></button>'+
        '<button class="a3d-stbtn" id="a3d-animstop" data-a3danim="stop" aria-label="Stop" title="Stop: the still drawing" hidden>'+PILL_STOP+'<span>STOP</span></button>'+
      '</span>'+
    '</div>';
    document.body.appendChild(root);
    el.root=root;
    el.cv=root.querySelector('#a3d-canvas');
    el.ctx=el.cv.getContext('2d');
    el.view=root.querySelector('#a3d-view');
    el.count=root.querySelector('#a3d-count');
    el.rows=root.querySelector('#a3d-rows');
    root.querySelector('.a3d-tb').addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3d]'):null;
      if(!b)return;
      var act=b.getAttribute('data-a3d');
      if(act==='drawer'){if(bimShellOverlay()){bimShellDrawer();return;}var tr=root.querySelector('.a3d-tree');if(tr)tr.classList.toggle('open');}   /* __acad3dV149: the left drawer */
      if(act==='rdrawer'){var rp=document.getElementById('a3d-right');if(rp)rp.classList.toggle('open');}
    });
    document.addEventListener('click',function(ev){
      var um2=root.querySelector('#a3d-uimenu');
      if(!um2||!um2.classList.contains('open'))return;
      if(ev.target&&ev.target.closest&&(ev.target.closest('#a3d-uimenu')||ev.target.closest('[data-a3dr="bim:uipanels"]')))return;   /* __acad3dV120 */
      um2.classList.remove('open');
    });
    var uimenuEl=root.querySelector('#a3d-uimenu');
    if(uimenuEl)uimenuEl.addEventListener('change',function(ev){
      var cb=ev.target&&ev.target.closest?ev.target.closest('[data-a3dui]'):null;
      if(!cb)return;
      bimSetUIPanelVisible(cb.getAttribute('data-a3dui'),cb.checked);
    });
    bimApplyUIPanelPrefs(root);
    /* __acad3dV115: Open reads project files only, each into a tab of its own */
    var projInEl=root.querySelector('#a3d-projin');
    if(projInEl)projInEl.addEventListener('change',function(ev){
      var files=ev.target.files,i;
      if(!files||!files.length)return;
      for(i=0;i<files.length;i++)bimOpenProjectFileObj(files[i]);
    });
    var fileInEl=root.querySelector('#a3d-filein');
    if(fileInEl)fileInEl.addEventListener('change',function(ev){
      var files=ev.target.files,i;
      if(!files||!files.length)return;
      for(i=0;i<files.length;i++)bimHandleImportFile(files[i]);
    });
    el.rows.addEventListener('click',function(ev){
      var r=ev.target&&ev.target.closest?ev.target.closest('.a3d-row'):null;
      if(!r)return;
      var rwo=objById(r.getAttribute('data-a3did')),rww=rwo?bimLayerPickRefusal(rwo):'';   /* __acad3dV121 */
      if(rww){a3dToast(rww);return;}
      A3D.sel=r.getAttribute('data-a3did');
      A3D.selSet=A3D.sel?[A3D.sel]:[];
      var trOpen=root.querySelector('.a3d-tree.open');
      if(trOpen)trOpen.classList.remove('open');
      refreshTree();paint();
    });
    el.lvlrows=root.querySelector('#a3d-lvlrows');
    var lvladdBtn=root.querySelector('#a3d-lvladd');
    if(lvladdBtn)lvladdBtn.addEventListener('click',function(ev){ev.stopPropagation();addLevel();});
    var bldaddBtn=root.querySelector('#a3d-bldadd');
    if(bldaddBtn)bldaddBtn.addEventListener('click',function(ev){ev.stopPropagation();addBuilding();});
    el.lvlrows.addEventListener('click',function(ev){
      var gdel=ev.target&&ev.target.closest?ev.target.closest('[data-griddel]'):null;
      if(gdel){bimRemoveGrid(gdel.getAttribute('data-griddel'));ev.stopPropagation();return;}
      var bdel=ev.target&&ev.target.closest?ev.target.closest('[data-blddel]'):null;
      if(bdel){removeBuilding(bdel.getAttribute('data-blddel'));ev.stopPropagation();return;}
      var del=ev.target&&ev.target.closest?ev.target.closest('[data-lvldel]'):null;
      if(del){removeLevel(del.getAttribute('data-lvldel'));ev.stopPropagation();return;}
      if(ev.target&&ev.target.tagName==='INPUT')return;
      var row=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlvl]'):null;
      if(row){setActiveLevel(row.getAttribute('data-a3dlvl'));return;}
      var grow=ev.target&&ev.target.closest?ev.target.closest('[data-a3dgrid]'):null;   /* __acad3dV98 */
      if(grow){bimSelectGrid(grow.getAttribute('data-a3dgrid'));return;}
      var brow=ev.target&&ev.target.closest?ev.target.closest('[data-a3dbldg]'):null;
      if(brow)setActiveBuilding(brow.getAttribute('data-a3dbldg'));
    });
    el.lvlrows.addEventListener('change',function(ev){
      var siteInp=ev.target&&ev.target.closest?ev.target.closest('[data-sitef]'):null;
      if(siteInp){updateSite(siteInp.getAttribute('data-sitef'),siteInp.value);return;}
      var bldInp=ev.target&&ev.target.closest?ev.target.closest('[data-bldf]'):null;
      if(bldInp){updateBuilding(bldInp.getAttribute('data-bldid'),bldInp.getAttribute('data-bldf'),bldInp.value);return;}
      var inp=ev.target&&ev.target.closest?ev.target.closest('[data-lvlf]'):null;
      if(!inp)return;
      updateLevel(inp.getAttribute('data-lvlid'),inp.getAttribute('data-lvlf'),inp.value);
    });
    var treetabsEl=root.querySelector('.a3d-treetabs');
    if(treetabsEl)treetabsEl.addEventListener('click',function(ev){
      var b2=ev.target&&ev.target.closest?ev.target.closest('[data-a3dpane]'):null;
      if(!b2)return;
      var name=b2.getAttribute('data-a3dpane');
      var tabs=root.querySelectorAll('.a3d-treetab'),panes=root.querySelectorAll('.a3d-pane'),ii;
      for(ii=0;ii<tabs.length;ii++)tabs[ii].classList.remove('on');
      b2.classList.add('on');
      for(ii=0;ii<panes.length;ii++)panes[ii].classList.toggle('on',panes[ii].getAttribute('data-a3dpanebody')===name);
    });
    el.schedbody=root.querySelector('#a3d-schedbody');
    el.schedcat=root.querySelector('#a3d-schedcat');
    bimSyncScheduleCats();
    if(el.schedcat)el.schedcat.addEventListener('change',function(){refreshSchedule();});
    var schedCsvBtn=root.querySelector('#a3d-schedcsv');
    if(schedCsvBtn)schedCsvBtn.addEventListener('click',function(ev){ev.stopPropagation();bimExportScheduleCSV();});
    el.browser=root.querySelector('#a3d-browser');
    el.schedwrap=root.querySelector('#a3d-schedwrap');
    el.schedtitle=root.querySelector('#a3d-schedtitle');
    if(el.browser)el.browser.addEventListener('click',function(ev){
      var t=ev.target,cl=function(sel){return t&&t.closest?t.closest(sel):null;};
      var g=cl('[data-a3dbgrp]');
      // toggle buttons must win over the row/group click they sit inside
      var b;
      if((b=cl('[data-a3dbviewdel]'))){ev.stopPropagation();bimDeleteView(b.getAttribute('data-a3dbviewdel'));return;}
      if((b=cl('[data-a3dbsheetdel]'))){
        ev.stopPropagation();
        var shId=b.getAttribute('data-a3dbsheetdel'),shObj=bimSheetById(shId);
        if(shObj)bimConfirmDeleteSheet(shId);   /* __acad3dV116: the one delete path */
        return;
      }
      if((b=cl('[data-a3dbfamdel]'))){
        ev.stopPropagation();
        var fid=b.getAttribute('data-a3dbfamdel'),fam=bimFamilyLibraryGet(fid);
        if(fam&&confirm('Remove "'+fam.name+'" from the Family Library? Placed instances are unaffected.')){
          bimFamilyLibraryRemove(fid);refreshBrowser();a3dToast('Removed from Family Library');
        }
        return;
      }
      if(g){bimBrowserToggle(g.getAttribute('data-a3dbgrp'));return;}
      /* __acad3dV84: every one of these rows opens a VIEW, so every one goes through the
         single activation path. The floor-plan row used to read "if(!A3D.flat)toggleFlat()",
         which is inert whenever the CURRENT view is also flat -- from any elevation it changed
         the level and left the camera looking sideways at the plan it had just opened. */
      if((b=cl('[data-a3dbplan]'))){bimActivateView('plan',b.getAttribute('data-a3dbplan'));return;}
      if((b=cl('[data-a3dbview3d]'))){bimActivateView('3d');return;}
      if((b=cl('[data-a3dbviewpreset]'))){bimActivateView('elev',b.getAttribute('data-a3dbviewpreset'));return;}
      if((b=cl('[data-a3dbviewgo]'))){bimActivateView('saved',b.getAttribute('data-a3dbviewgo'));return;}
      if((b=cl('[data-a3dbsheetgo]'))){bimActivateView('sheet',b.getAttribute('data-a3dbsheetgo'));return;}
      if((b=cl('[data-a3dbsched]'))){
        var k=b.getAttribute('data-a3dbsched');
        if(el.schedcat){el.schedcat.value=k;}
        if(el.schedwrap)el.schedwrap.classList.add('open');
        if(el.schedtitle&&SCHEDULE_DEFS[k])el.schedtitle.textContent=SCHEDULE_DEFS[k].label;
        refreshSchedule();refreshBrowser();
        return;
      }
      if((b=cl('[data-a3dbfam]'))){startFamilyPlaceTool(b.getAttribute('data-a3dbfam'));return;}
      if((b=cl('[data-a3dbclass]'))){
        var clsId=b.getAttribute('data-a3dbclass');
        var matches=A3D.objs.filter(function(o){return o.classId===clsId;});
        if(!matches.length){a3dToast('No objects use this classification');return;}
        bimSelectByRule(matches);   /* __acad3dV121: as SELECT ALL, by the layers */
        return;
      }
    });
    var schedCloseBtn=root.querySelector('#a3d-schedclose');
    if(schedCloseBtn)schedCloseBtn.addEventListener('click',function(ev){
      ev.stopPropagation();
      if(el.schedwrap)el.schedwrap.classList.remove('open');
    });
    el.sheetview=root.querySelector('#a3d-sheetview');
    el.sheetcv=root.querySelector('#a3d-sheetcanvas');
    el.sheetnum=root.querySelector('#a3d-sheetnum');
    /* __acad3dV122: the Pages display */
    el.pageswrap=root.querySelector('#a3d-pageswrap');el.pagescol=root.querySelector('#a3d-pagescol');
    el.pgprev=root.querySelector('#a3d-pgprev');el.pgnext=root.querySelector('#a3d-pgnext');
    el.pgnum=root.querySelector('#a3d-pgnum');el.pgof=root.querySelector('#a3d-pgof');el.pgzoom=root.querySelector('#a3d-pgzoom');
    var pgPrintBtn=root.querySelector('#a3d-pgprint');
    if(pgPrintBtn)pgPrintBtn.addEventListener('click',function(){bimPrintSet();});   /* __acad3dV122 */
    var sheetPresentBtn=root.querySelector('#a3d-sheetpresent');
    if(sheetPresentBtn)sheetPresentBtn.addEventListener('click',function(){bimSlideshowStart(A3D.activeSheetId);});
    bimWirePages();
    var sheetAddBtn=root.querySelector('#a3d-sheetadd');
    if(sheetAddBtn)sheetAddBtn.addEventListener('click',function(ev){ev.stopPropagation();bimOpenNewSheetDlg();});
    var sheetAddVpBtn=root.querySelector('#a3d-sheetaddvp');
    if(sheetAddVpBtn)sheetAddVpBtn.addEventListener('click',function(){bimOpenAddViewportDlg();});
    var sheetPropsBtn=root.querySelector('#a3d-sheetprops');
    if(sheetPropsBtn)sheetPropsBtn.addEventListener('click',function(){bimOpenSheetPropsDlg();});
    var sheetTbEditBtn=root.querySelector('#a3d-sheettbedit');
    if(sheetTbEditBtn)sheetTbEditBtn.addEventListener('click',function(){bimOpenTitleBlockDlg();});
    var sheetPngBtn=root.querySelector('#a3d-sheetpng');
    if(sheetPngBtn)sheetPngBtn.addEventListener('click',function(){bimExportSheetPNG();});
    var sheetSvgBtn=root.querySelector('#a3d-sheetsvg');
    if(sheetSvgBtn)sheetSvgBtn.addEventListener('click',function(){bimExportSheetSVG();});
    var sheetPrintBtn=root.querySelector('#a3d-sheetprint');
    if(sheetPrintBtn)sheetPrintBtn.addEventListener('click',function(){bimPrintSheet();});
    var sheetCloseBtn2=root.querySelector('#a3d-sheetclose');
    if(sheetCloseBtn2)sheetCloseBtn2.addEventListener('click',function(){bimShowModel();});   /* __acad3dV116: the Model tab's path */
    if(el.sheetcv){
      el.sheetcv.addEventListener('mousedown',bimSheetPointerDown);
      el.sheetcv.addEventListener('mousemove',bimSheetPointerMove);
      window.addEventListener('mouseup',bimSheetPointerUp);
      el.sheetcv.addEventListener('dblclick',bimSheetDblClick);
      el.sheetcv.addEventListener('wheel',bimSheetWheel,{passive:false});   /* __acad3dV116 */
      el.sheetcv.addEventListener('contextmenu',bimSheetContextMenu);
      el.sheetcv.addEventListener('touchstart',bimSheetPointerDown,{passive:false});
      el.sheetcv.addEventListener('touchmove',bimSheetPointerMove,{passive:false});
      el.sheetcv.addEventListener('touchend',bimSheetPointerUp);
    }
    var famSaveBtn=root.querySelector('#a3d-famsave');
    if(famSaveBtn)famSaveBtn.addEventListener('click',function(ev){ev.stopPropagation();openSaveAsFamilyDlg();});
    var famImportBtn=root.querySelector('#a3d-famimport');
    var famFileIn=root.querySelector('#a3d-famfilein');
    if(famImportBtn&&famFileIn)famImportBtn.addEventListener('click',function(ev){ev.stopPropagation();famFileIn.value='';famFileIn.click();});
    if(famFileIn)famFileIn.addEventListener('change',function(ev){
      var files=ev.target.files;
      if(files&&files.length)bimImportFamilyFile(files[0]);
    });
    refreshFamilyPanel();
    el.viewrows=root.querySelector('#a3d-viewrows');
    var viewSaveBtn=root.querySelector('#a3d-viewsave');
    if(viewSaveBtn)viewSaveBtn.addEventListener('click',function(ev){ev.stopPropagation();bimSaveCurrentView();});
    if(el.viewrows)el.viewrows.addEventListener('click',function(ev){
      var goBtn=ev.target&&ev.target.closest?ev.target.closest('[data-viewgo]'):null;
      if(goBtn){ev.stopPropagation();bimActivateView('saved',goBtn.getAttribute('data-viewgo'));return;}   /* __acad3dV119 */
      var delBtn=ev.target&&ev.target.closest?ev.target.closest('[data-viewdel]'):null;
      if(delBtn){ev.stopPropagation();bimDeleteView(delBtn.getAttribute('data-viewdel'));}
    });
    if(el.viewrows)el.viewrows.addEventListener('change',function(ev){
      if(ev.target&&ev.target.id==='a3d-lvlfilter-cb')bimToggleLevelFilter();
    });
    refreshViews();
    var bsearch=root.querySelector('#a3d-bsearch');
    if(bsearch)bsearch.addEventListener('input',function(){A3D.browserFilter=bsearch.value.trim().toLowerCase();refreshBrowser();});
    el.propsbody=root.querySelector('#a3d-propsbody');
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var g=ev.target&&ev.target.closest?ev.target.closest('[data-a3dpgrp]'):null;
      if(g){bimPropGroupToggle(g.getAttribute('data-a3dpgrp'));return;}
      var cd=ev.target&&ev.target.closest?ev.target.closest('[data-concondel]'):null;
      if(cd){
        var co=objById(A3D.sel);
        if(co)bimDeleteSketchConstraint(co,cd.getAttribute('data-concondel'));
        refreshProps();
        return;
      }
      /* __acad3dV50: clicking a related element in the Dependencies group selects it, so the
         parametric graph can be walked from the palette. */
      var ds=ev.target&&ev.target.closest?ev.target.closest('[data-propsel]'):null;
      if(ds){
        var selId=ds.getAttribute('data-propsel'),selObj=objById(selId);
        if(!selObj){a3dToast('That element no longer exists');refreshProps();return;}
        var dsw=bimLayerPickRefusal(selObj);   /* __acad3dV121 */
        if(dsw){a3dToast(dsw);return;}
        A3D.sel=selObj.id;A3D.sel2=null;A3D.selSet=[selObj.id];
        refreshTree();refreshHud();refreshProps();paint();
        a3dToast('Selected '+selObj.name);
        return;
      }
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-propf]'):null;
      if(!b||b.tagName!=='BUTTON')return;
      var f=b.getAttribute('data-propf');
      if(f==='apply'){refreshProps();paint();a3dToast('Applied');return;}
      if(f==='edittype'){
        var eo=objById(A3D.sel);
        if(eo&&eo.bim&&TYPE_CATS[eo.bim.type])openTypeDlg(eo);
        else a3dToast('This object has no editable type');
        return;
      }
      if(f==='editclass'){openClassificationDlg();return;}
      if(f.indexOf('terrdrop:')===0){var tdo=objById(A3D.sel);if(tdo)bimTerrainEdit(tdo,f.slice(9));return;}   /* __acad3dV144 */
      if(f==='terrlandxml'){var tlo=objById(A3D.sel);if(tlo)bimLandXmlExport([tlo.id]);return;}
      if(f==='regrade'){bimRegrade(objById(A3D.sel));return;}   /* __acad3dV145 */
      if(f==='gradespots'){bimGradeSpots(objById(A3D.sel));return;}
      if(f==='syncclones'){
        var so=objById(A3D.sel);
        if(so)syncLinkedClones(so.id);
        return;
      }
    });
    /* __acad3dV59: graphics-override reset buttons live inside the Graphics prop rows but are
       plain <button data-propgfxreset> elements, not <input data-propf>, so they need their own
       click delegate rather than reusing the generic [data-propf] one above. */
    /* __acad3dV146: the History group's buttons, and Enter in its message */
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var hb=ev.target&&ev.target.closest?ev.target.closest('[data-histact]'):null;
      if(!hb||hb.disabled)return;
      bimHistAct(hb.getAttribute('data-histact'),ev);
    });
    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histmsg'))A3D_HIST_MSG=ev.target.value;
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brname'))A3D_BR_NEW=ev.target.value;   /* __acad3dV151 */
    });
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){   /* __acad3dV151: switch branch */
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-histbranch'))bimHistSwitchUI(ev.target.value);
      if(ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brmergefrom')){A3D_BR_PICK=ev.target.value;if(A3D_BR_DEL){A3D_BR_DEL='';refreshProps();}}   /* kept through a redraw; another picked: ask again */
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'&&ev.target&&ev.target.hasAttribute&&ev.target.hasAttribute('data-brname')){ev.preventDefault();ev.stopPropagation();bimHistBranchAct('branch');return;}   /* __acad3dV151 */
      if(ev.key!=='Enter'||!ev.target||!ev.target.hasAttribute||!ev.target.hasAttribute('data-histmsg'))return;
      ev.preventDefault();ev.stopPropagation();
      bimHistDoCommit(ev.target.value);
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var rb=ev.target&&ev.target.closest?ev.target.closest('[data-propgfxreset]'):null;
      if(!rb)return;
      var ro=objById(A3D.sel);
      if(!ro)return;
      var rparts=rb.getAttribute('data-propgfxreset').split(':');
      pushUndo();
      bimSetGraphicsOverride(ro,rparts[0],rparts[1],null);
      refreshProps();saveSoon();
    });
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var inp=ev.target&&ev.target.closest?ev.target.closest('[data-propf]'):null;
      if(!inp)return;
      var o=objById(A3D.sel);
      if(!o)return;
      var f=inp.getAttribute('data-propf');
      if(f==='terrint'){bimSetTerrainInterval(o,inp.value);return;}   /* __acad3dV108 */
      if(f==='terrview'){bimTerrainSetView(o,inp.value);return;}      /* __acad3dV144 */
      if(f==='cutslope'||f==='fillslope'){bimSetPadSlope(o,f,inp.value);return;}   /* __acad3dV145 */
      if(f==='terrarrows'){bimSetSlopeArrows(o,inp.checked);return;}
      if(f==='gradeelev'){bimSetGradeElev(o,inp.value);return;}      /* __acad3dV108 */
      /* __acad3dV77: a length field SHOWS and ACCEPTS the project's display units. Converting
         back to metres here, once, before any branch below reads inp.value, means every
         existing branch keeps reading a plain metres figure and none of them has to know that
         display units exist. A parallel handler for length fields would have been the obvious
         alternative and would have duplicated twenty branches of validation and rebuild logic,
         which is how the two copies drift apart. */
      if(inp.getAttribute('data-proplen')){
        var lenM=bimLenInputToMetres(inp.value);
        if(lenM===null){
          console.warn('[BIM] Unreadable length typed into '+f+': '+inp.value);
          a3dToast('Must be a number');refreshProps();return;
        }
        inp={value:String(lenM),checked:inp.checked};
      }
      if(f.indexOf('asset:')===0&&o.asset){bimEntPropSet(o,f.slice(6),inp.value,inp.checked);return;}   /* __acad3dV169 */
      if(f==='name'){
        pushUndo();
        o.name=String(inp.value||'').slice(0,60)||o.name;
        refreshTree();paint();saveSoon();   /* __acad3dV101: labels and tags read the name */
      }else if(f==='layer'){
        bimObjSetLayer(o.id,inp.value);   /* __acad3dV121 */
      }else if(f==='posy'){
        var yv=parseFloat(inp.value);
        if(!isFinite(yv)){a3dToast('Must be a number');refreshProps();return;}
        var pbY=bimPrimBase(o);   /* __acad3dV123: a primitive's row sets its base */
        pushUndo();
        if(!o.pos)o.pos=[0,0,0];
        o.pos[1]=pbY!==null?o.pos[1]+(yv-pbY):yv;
        paint();saveSoon();
      }else if(f==='locked'){
        bimSetLocked(o,inp.checked);
        refreshProps();
      }else if(f==='thickness'||f==='height'){
        var v=parseFloat(inp.value);
        if(!isFinite(v)||v<=0){a3dToast('Must be a positive number');refreshProps();return;}
        bimRebuildWall(o,f==='thickness'?v:o.bim.thickness,f==='height'?v:o.bim.height,o.bim.align);
      }else if(f==='align'){
        bimRebuildWall(o,o.bim.thickness,o.bim.height,inp.value);
      }else if(f==='nw'||f==='nh'){
        var nv=parseFloat(inp.value);
        if(!isFinite(nv)||nv<0){a3dToast('Must be a number');refreshProps();return;}
        pushUndo();
        if(f==='nw')o.w=Math.max(8,nv);else o.h=Math.max(0,nv);
        refreshProps();paint();saveSoon();
        return;
      }else if(f==='ntitle'||f==='nbody'||f==='ncells'){
        pushUndo();
        if(f==='ntitle')o.title=String(inp.value||'').slice(0,80);
        else if(f==='nbody')o.body=String(inp.value||'').slice(0,600);
        // the round trip of the readable form shown in the field back to the stored one
        else o.cells=String(inp.value||'').split('|').map(function(r2){
               return r2.split('\u2192').map(function(c){return c.trim();}).join('\t');
             }).join('\n');
        refreshTree();paint();saveSoon();
        return;
      }else if(f==='nfill'||f==='nstroke'){
        pushUndo();
        if(!o.style)o.style={};
        if(f==='nfill')o.style.fill=inp.value;else o.style.stroke=inp.value;
        paint();saveSoon();
        return;
      }else if(f==='crot'){
        var cr=parseFloat(inp.value);
        if(!isFinite(cr)){a3dToast('Rotation must be a number');refreshProps();return;}
        pushUndo();
        var crRes=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,o.bim.width,o.bim.depth,
          o.bim.height,cr*Math.PI/180,o.bim.section||null);   /* __acad3dV126 */
        if(crRes.error){a3dToast(crRes.error);refreshProps();return;}
        o.mesh=crRes.mesh;o.bim.rotation=cr*Math.PI/180;
        bimPropagateFrom([o.id],'rebuild');
        refreshTree();refreshProps();paint();saveSoon();
        return;
      }else if(f==='fthickness'){
        var fv=parseFloat(inp.value);
        if(!isFinite(fv)||fv<=0){a3dToast('Must be a positive number');refreshProps();return;}
        bimRebuildFloor(o,fv,o.bim.material);
      }else if(f==='fmaterial'){
        bimRebuildFloor(o,o.bim.thickness,inp.value);
      }else if(f==='cwidth'||f==='cdepth'||f==='cheight'){
        var cv=parseFloat(inp.value);
        if(!isFinite(cv)||cv<=0){a3dToast('Must be a positive number');refreshProps();return;}
        bimRebuildColumn(o,f==='cwidth'?cv:o.bim.width,f==='cdepth'?cv:o.bim.depth,f==='cheight'?cv:o.bim.height);
      }else if(f==='rpitch'||f==='rdir'||f==='rthick'){
        var rv=parseFloat(inp.value);
        if(!isFinite(rv)){a3dToast('Must be a number');refreshProps();return;}
        if(f==='rthick'&&rv<=0){a3dToast('Thickness must be positive');refreshProps();return;}
        if(f==='rpitch'&&(rv<0||rv>=90)){a3dToast('Pitch must be between 0 and 90 degrees');refreshProps();return;}
        bimRebuildRoof(o,f==='rpitch'?rv:o.bim.pitch,f==='rdir'?rv:o.bim.slopeDir,f==='rthick'?rv:o.bim.thickness);
      }else if(f==='rstyle'){
        if(inp.value==='gable'&&!(o.bim.gables&&o.bim.gables.length)){
          a3dToast('This roof has no gable ends recorded; redraw it to pick them');refreshProps();return;
        }
        bimRebuildRoof(o,o.bim.pitch,o.bim.slopeDir,o.bim.thickness,inp.value);
      }else if(f==='walltype'){
        bimSetWallTypeOf(o,inp.value);
      }else if(f==='objtype'){   /* __acad3dV102 */
        if(!o.bim||!TYPE_CATS[o.bim.type]){a3dToast('This object has no type');return;}
        pushUndo();
        if(bimAssignTypeTo(o,o.bim.type,inp.value)){
          A3D.meshes={};refreshTree();paint();saveSoon();
          a3dToast(o.name+' is now '+(bimTypeNameOf(o)||'the selected type'));
        }else{
          a3dToast('That type could not be applied to '+o.name+' - see the console');
          console.warn('[BIM] Type change failed for '+o.name,inp.value);
        }
      }else if(f==='classid'){
        setObjectClassification(o.id,inp.value||null);
        a3dToast(inp.value?'Classification assigned':'Classification cleared');
      }else if(f==='leadertext'){
        var lv2=inp.value.trim();
        if(!lv2){a3dToast('Leader text cannot be empty');refreshProps();return;}
        pushUndo();o.label=lv2;paint();saveSoon();
      }else if(f==='textcontent'){
        var txtv=inp.value;
        if(!txtv||!txtv.trim()){a3dToast('Text cannot be empty');refreshProps();return;}
        pushUndo();
        o.text=txtv.trim();
        paint();saveSoon();
      }else if(f.indexOf('prm:')===0){
        /* __acad3dV123: the Dimensions rows above call this again. A length arrives in metres (the
           data-proplen conversion at the top) and is kept in the parameter's own unit, SCALE. */
        var pname=f.slice(4);
        var newPrm={},pk,pval=parseFloat(inp.value);
        if(!isFinite(pval)){a3dToast('Must be a number');refreshProps();return;}
        if(pname!=='Angle'&&pname!=='Polygon')pval=pval/SCALE;
        for(pk in o.prm)if(o.prm.hasOwnProperty(pk))newPrm[pk]=o.prm[pk];
        newPrm[pname]=pval;
        var merged=mergePrm(o.t,newPrm);
        var verr=validatePrm(o.t,merged);
        if(verr){a3dToast(verr);refreshProps();return;}
        var base0=meshMinY(meshOf(o));
        pushUndo();
        o.prm=merged;
        /* the base stays where it stood: the mesh is centred on the position, so a taller box sank
           below its level by half the change -- pulling the top keeps the base too */
        var base1=meshMinY(meshOf(o));
        if(isFinite(base0)&&isFinite(base1)){if(!o.pos)o.pos=[0,0,0];o.pos[1]+=base0-base1;}
        refreshTree();refreshProps();paint();saveSoon();
      }
    });
    /* __acad3dV59: graphics-override inputs (data-propgfx="mode:key") and the Fill on/off checkbox
       (data-propgfxfillon="mode") get their own change delegate, parallel to the [data-propf] one
       above, because their key isn't a flat field name -- it's a mode+key pair that needs a small
       amount of per-type parsing (number/color/select/range/checkbox) the generic handler doesn't do. */
    /* __acad3dV98: the selected grid's fields. */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var gi=ev.target&&ev.target.closest?ev.target.closest('[data-gridf]'):null;
      if(!gi)return;
      var gg=bimSelectedGrid();
      if(!gg)return;
      try{
        var gf=gi.getAttribute('data-gridf');
        if(gf==='name'){if(!bimRenameGrid(gg.id,gi.value))refreshProps();return;}
        var v=bimLenInputToMetres(gi.value);
        if(v===null){a3dToast('Grid ends must be numbers');refreshProps();return;}
        var np1=gg.p1.slice(),np2=gg.p2.slice();
        if(gf==='x1')np1[0]=v;else if(gf==='y1')np1[1]=v;
        else if(gf==='x2')np2[0]=v;else if(gf==='y2')np2[1]=v;
        else return;
        if(!bimSetGridEnds(gg.id,np1,np2))refreshProps();
      }catch(eGP){
        console.warn('[BIM] Grid property edit failed',eGP);
        a3dToast('That grid could not be edited - see the console');
      }
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var ga=ev.target&&ev.target.closest?ev.target.closest('[data-gridact]'):null;
      if(!ga)return;
      var gg=bimSelectedGrid();
      if(gg&&ga.getAttribute('data-gridact')==='delete')bimRemoveGrid(gg.id);
    });
    /* __acad3dV164: a site analysis element's appearance, Reset and Run again */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimDgPropChange(ev);}catch(eDC){console.warn('[BIM] Site analysis element edit failed',eDC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimDgPropClick(ev);}catch(eDK){console.warn('[BIM] Site analysis element action failed',eDK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV125: the Structural and Analysis pages */
    if(el.propsbody){el.propsbody.addEventListener('input',bimLoadDraftInput,true);el.propsbody.addEventListener('change',bimLoadDraftInput,true);}
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimStructPropChange(ev);}catch(eSP){console.warn('[BIM] Analysis setting failed',eSP);a3dToast('That setting could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimStructPropClick(ev);}catch(eSC){console.warn('[BIM] Load edit failed',eSC);a3dToast('That load could not be changed - see the console');}
    });
    /* __acad3dV131: the Usage page and the usages */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimUsagePropChange(ev);}catch(eUC){console.warn('[BIM] Usage edit failed',eUC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimUsagePropClick(ev);}catch(eUK){console.warn('[BIM] Usage edit failed',eUK);a3dToast('That could not be changed - see the console');}
    });
    /* __acad3dV141: Properties' tabs */
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimPropTabClick(ev);}catch(eTB){console.warn('[BIM] Properties tab',eTB);}
    });
    /* __acad3dV138: the survey check */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimSurveyPropChange(ev);}catch(eSC){console.warn('[BIM] Survey check failed',eSC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimSurveyPropClick(ev);}catch(eSK){console.warn('[BIM] Survey report failed',eSK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV136: the lens */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimLensPropChange(ev);}catch(eLC){console.warn('[BIM] Colour by failed',eLC);a3dToast('That could not be changed - see the console');}
    });
    /* __acad3dV135: find open data */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimFindPropChange(ev);}catch(eFC){console.warn('[BIM] Find data setting failed',eFC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimFindPropClick(ev);}catch(eFK){console.warn('[BIM] Find data action failed',eFK);a3dToast('That did not work - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      var q=ev.target&&ev.target.closest?ev.target.closest('[data-propfind="q"]'):null;
      if(!q||ev.key!=='Enter')return;
      ev.preventDefault();ev.stopPropagation();
      bimFindSearch(q.value);
    });
    /* __acad3dV167: the Standards group */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimStdPropChange(ev);}catch(eSC){console.warn('[BIM] Standards setting failed',eSC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){   /* __acad3dV167g: the drafts, as typed */
      var f=ev.target&&ev.target.closest?ev.target.closest('[data-propstd]'):null,k=f&&f.getAttribute('data-propstd');
      if(k&&BIM_STD_DRAFT_KEYS[k])A3D_STD_UI.draft[k]=f.value;
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimStdPropClick(ev);}catch(eSK){console.warn('[BIM] Standards action failed',eSK);a3dToast('That did not work - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      var f=ev.target&&ev.target.closest?ev.target.closest('[data-propstd="ovv"],[data-propstd="ovwhy"]'):null;
      if(!f||ev.key!=='Enter'||!A3D_STD_UI.edit)return;
      ev.preventDefault();ev.stopPropagation();
      try{var j=A3D_STD_UI.edit.indexOf('|');if(bimStdOverride(A3D_STD_UI.edit.slice(0,j),A3D_STD_UI.edit.slice(j+1),bimStdPropVal('ovv'),bimStdPropVal('ovwhy'))){A3D_STD_UI.edit=null;bimStdDraftClear(['ovv','ovwhy']);}refreshProps();}
      catch(eSE){console.warn('[BIM] The override could not be saved',eSE);a3dToast('The override could not be saved - see the console');}
    });
    /* __acad3dV134: the Data Layers group and a data feature */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimDataPropChange(ev);}catch(eDC){console.warn('[BIM] Data layer setting failed',eDC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimDataPropClick(ev);}catch(eDK){console.warn('[BIM] Data layer action failed',eDK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV133: the Site Context group */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimCtxPropChange(ev);}catch(eXC){console.warn('[BIM] Context setting failed',eXC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimCtxPropClick(ev);}catch(eXK){console.warn('[BIM] Context action failed',eXK);a3dToast('That did not work - see the console');}
    });
    /* __acad3dV132: the Map group */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimMapPropChange(ev);}catch(eMC){console.warn('[BIM] Map setting failed',eMC);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimMapPropClick(ev);}catch(eMK){console.warn('[BIM] Map action failed',eMK);a3dToast('That did not work - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('input',function(ev){   /* __acad3dV149c: kept as typed */
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;
      if(a)A3D_MAP_DRAFT=a.value;
    });
    if(el.propsbody)el.propsbody.addEventListener('keydown',function(ev){
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-propmap="addr"]'):null;
      if(!a||(ev.key!=='Enter'&&ev.keyCode!==13))return;
      ev.preventDefault();ev.stopPropagation();
      bimMapFind(a.value);
    });
    /* __acad3dV127: the Alignment and Profile pages */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      try{bimAlignPropChange(ev);}catch(eAL){console.warn('[BIM] Alignment edit failed',eAL);a3dToast('That could not be changed - see the console');}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      try{bimAlignPropClick(ev);}catch(eAC){console.warn('[BIM] Alignment edit failed',eAC);a3dToast('That could not be changed - see the console');}
    });
    /* __acad3dV103: setbacks, per side or all at once */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var si=ev.target&&ev.target.closest?ev.target.closest('[data-propsetback]'):null;
      if(!si)return;
      var po=objById(A3D.sel);
      if(!bimIsProperty(po))return;
      var sv=parseFloat(si.value);
      if(!isFinite(sv)||sv<0){a3dToast('A setback is a distance of 0 or more');refreshProps();return;}
      pushUndo();
      var sk_=si.getAttribute('data-propsetback'),k_;
      if(!po.setbacks||po.setbacks.length!==po.legs.length)po.setbacks=po.legs.map(function(){return 0;});
      if(sk_==='all'){for(k_=0;k_<po.setbacks.length;k_++)po.setbacks[k_]=sv;}
      else po.setbacks[parseInt(sk_,10)]=sv;
      refreshProps();paint();saveSoon();
      var sg=bimPropertyGeometry(po);
      if(sg.setback&&sg.setback.error)a3dToast(po.name+': '+sg.setback.error);
      else{var vv=bimSetbackViolations(po);if(vv.list.length)a3dToast(vv.list.length+' element(s) outside the setback: '+vv.list.map(function(v){return v.name;}).join(', '));}
    });
    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){
      var pa=ev.target&&ev.target.closest?ev.target.closest('[data-propact="propedit"]'):null;
      if(!pa)return;
      var po=objById(A3D.sel);
      if(bimIsProperty(po))openPropertyDlg(po);
    });
    /* __acad3dV101: a tag's own switch */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var ti=ev.target&&ev.target.closest?ev.target.closest('[data-tagf]'):null;
      if(!ti)return;
      var tg=objById(A3D.sel);
      if(!tg||tg.t!=='roomtag')return;
      pushUndo();
      tg.showArea=!!ti.checked;
      paint();saveSoon();
    });
    /* __acad3dV101: room fields. A field shown on a TAG edits the tag's room. */
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      var ri=ev.target&&ev.target.closest?ev.target.closest('[data-roomf]'):null;
      if(!ri)return;
      var so=objById(A3D.sel),room=so&&so.t==='room'?so:(so&&so.roomId?objById(so.roomId):null);
      if(!room){a3dToast('That room no longer exists');refreshProps();return;}
      try{bimSetRoomField(room,ri.getAttribute('data-roomf'),ri.value);}
      catch(eRF){
        console.warn('[BIM] Room field edit failed',eRF);
        a3dToast('That room field could not be changed - see the console');
      }
      /* __acad3dV118: V105 deferred the rebuild to a timer here and refocused the field a Tab or Enter
         had been aimed at, because the rebuild used to destroy the field the browser was about to
         focus. The rebuild keeps its elements now, and the panel's last change delegate shows the
         model after every edit. */
    });
    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){
      /* __acad3dV73: the no-selection model fields. Handled BEFORE the objById guard, because
         these are the one set of inspector controls that exist precisely when nothing is
         selected -- the old early return made them inert. */
      var mp=ev.target&&ev.target.closest?ev.target.closest('[data-propmodel]'):null;
      if(mp){
        var mk=mp.getAttribute('data-propmodel'),mv=mp.value;
        if(mk==='truenorth'){bimSetTrueNorth(mv);return;}   /* __acad3dV103 */
        if(mk==='sunlat'||mk==='sunlon'||mk==='suntz'||mk==='sundate'||mk==='suntime'){bimSetSun(mk.slice(3),mv);return;}   /* __acad3dV107 */
        if(mk==='project'){A3D.titleBlock.project=mv;}
        else if(mk==='client'){A3D.titleBlock.client=mv;}
        else if(mk==='site'){updateSite('name',mv);}
        else if(mk==='level'){setActiveLevel(mv);}
        else if(mk==='layer'){setActiveLayer(mv);}
        else if(mk==='present'){A3D.presentMode=(mv==='1');bimSyncPresentPill();}
        /* __acad3dV80: the left shell's file card names the project and the site, so these
           two fields are the ones that change it. Nothing here mutates the panel's own DOM,
           which is what the cleanup observer watches, so the card has to be told. */
        try{bimCleanShell();}catch(eS2){console.warn('[BIM] The left panel could not be redrawn',eS2);}   /* __acad3dV121: said nothing */
        refreshProps();paint();saveSoon();
        return;
      }
      var go=objById(A3D.sel);
      if(!go)return;
      /* __acad3dV69: material assignment. refreshProps AND paint: the material supplies the
         plan cut pattern, so the drawing changes with the palette and a repaint is not
         optional here the way it is for a purely informational field. */
      var mSel=ev.target&&ev.target.closest?ev.target.closest('[data-propmat]'):null;
      if(mSel){
        pushUndo();
        if(!bimSetMaterial(go,mSel.value)){
          a3dToast('That material is not in the library');refreshProps();return;
        }
        a3dToast(mSel.value?('Material set to '+mSel.value):'Material cleared');
        refreshProps();paint();saveSoon();
        return;
      }
      var fillOn=ev.target&&ev.target.closest?ev.target.closest('[data-propgfxfillon]'):null;
      if(fillOn){
        var fom=fillOn.getAttribute('data-propgfxfillon');
        pushUndo();
        if(fillOn.checked){
          var swatch=el.propsbody.querySelector('[data-propgfx="'+fom+':fill"]');
          bimSetGraphicsOverride(go,fom,'fill',(swatch&&swatch.value)||'#cccccc');
        }else{
          bimSetGraphicsOverride(go,fom,'fill','none');
        }
        refreshProps();saveSoon();
        return;
      }
      var gi=ev.target&&ev.target.closest?ev.target.closest('[data-propgfx]'):null;
      if(!gi)return;
      var gparts=gi.getAttribute('data-propgfx').split(':'),gmode=gparts[0],gkey=gparts[1],gval;
      if(gkey==='lineWeight'){
        gval=parseFloat(gi.value);
        if(!isFinite(gval)||gval<=0){a3dToast('Line weight must be a positive number');refreshProps();return;}
      }else if(gkey==='patternScale'){
        // __acad3dV63: clamped rather than rejected -- 0.1..8 is the range that still renders a
        // recognisable tile, and silently pinning an out-of-range entry is friendlier here than
        // discarding the edit, since the field is a density dial rather than a measured value.
        gval=parseFloat(gi.value);
        if(!isFinite(gval)||gval<=0){a3dToast('Pattern scale must be a positive number');refreshProps();return;}
        gval=Math.max(0.1,Math.min(8,gval));
      }else if(gkey==='opacity'){
        gval=parseFloat(gi.value);
        if(!isFinite(gval)){a3dToast('Opacity must be a number');refreshProps();return;}
        gval=Math.max(0,Math.min(1,gval));
      }else if(gkey==='shadow'){
        gval=!!gi.checked;
      }else{
        gval=gi.value;
      }
      pushUndo();
      bimSetGraphicsOverride(go,gmode,gkey,gval);
      refreshProps();saveSoon();
    });
    /* __acad3dV118: whatever a field's change did -- applied, refused, or refused without saying so --
       the panel ends showing the model. Registered after every other change handler on the panel, so
       it runs last. A refused Type change on a pinned wall used to leave the dropdown showing a type
       the wall does not have, because that one branch did not refresh; now no branch has to. */
    if(el.propsbody)el.propsbody.addEventListener('change',function(){
      try{refreshProps();}
      catch(eRP){console.warn('[BIM] Properties could not be refreshed after an edit.',eRP);a3dToast('Properties could not be refreshed - see the console');}
    });
    el.pill=root.querySelector('#a3d-navgrp');   /* __acad3dV109: the view buttons now live in the status bar */
    el.flip=root.querySelector('#a3d-flip');
    el.present=root.querySelector('#a3d-present');
    bimSyncPresentPill();
    el.touchLen=root.querySelector('#a3d-touchlen');
    el.touchLenInput=root.querySelector('#a3d-touchlen-input');
    var touchLenSetBtn=root.querySelector('#a3d-touchlen-set');
    if(touchLenSetBtn)touchLenSetBtn.addEventListener('click',function(ev){ev.preventDefault();bimSubmitTouchLen();});
    if(el.touchLenInput)el.touchLenInput.addEventListener('keydown',function(ev){
      if(ev.key==='Enter'){ev.preventDefault();bimSubmitTouchLen();}
      ev.stopPropagation();
    });
    if(el.pill)el.pill.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dnav]'):null;
      if(!b)return;
      var a=b.getAttribute('data-a3dnav');
      if(a==='flip')toggleFlat();
      else if(a==='present'){A3D.presentMode=!A3D.presentMode;bimSyncPresentPill();paint();}
      else setNav(a);
    });
    var animGrp=root.querySelector('#a3d-animgrp');   /* __acad3dV170: Play, Pause and Stop */
    if(animGrp)animGrp.addEventListener('click',function(ev){
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3danim]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3danim')==='stop')bimAnimStop();else bimAnimPlay();
    });
    /* __acad3dV116: the layout tabs and the space button */
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
    el.stcoords=root.querySelector('#a3d-stcoords');
    el.stlevel=root.querySelector('#a3d-stlevel');
    if(el.stlevel)el.stlevel.addEventListener('change',function(){
      setActiveLevel(el.stlevel.value);
    });
    el.snappill=root.querySelector('#a3d-snapgrp');
    if(el.snappill)el.snappill.addEventListener('click',function(ev){
      var b3=ev.target&&ev.target.closest?ev.target.closest('[data-a3dsnap]'):null;
      if(!b3)return;
      var s=b3.getAttribute('data-a3dsnap');
      if(s==='point')A3D_SNAP.point=!A3D_SNAP.point;
      else if(s==='ortho')A3D_SNAP.ortho=!A3D_SNAP.ortho;
      else if(s==='grid')A3D_SNAP.grid=!A3D_SNAP.grid;
      syncSnapPill();
      paint();
    });
    el.cv.addEventListener('mousedown',onDown);
    el.cv.addEventListener('mousemove',onHover);
    /* __acad3dV67: onHover only runs while a sketch is active (it returns early on !A3D.sk),
       so the coordinate read-out needs its own listener or it would be blank except while
       drawing -- which is the one time the on-canvas length label already tells you. */
    el.cv.addEventListener('mousemove',bimStatusHover);
    el.cv.addEventListener('mouseleave',bimStatusHoverOut);
    /* __acad3dV111: the cursor has left the drawing, so nothing is under it */
    el.cv.addEventListener('mouseleave',function(){
      if(A3D.gizHover===null||A3D.gizHover===undefined)return;
      A3D.gizHover=null;A3D.gizHoverName=null;A3D.gizHoverHint=null;   /* __acad3dV123 */
      bimSyncStatusHint();
      paint();
    });
    el.cv.addEventListener('dblclick',bimFaceDblClick);   /* __acad3dV123: take a face */
    window.addEventListener('mousemove',onMove);
    window.addEventListener('mouseup',onUp);
    el.cv.addEventListener('wheel',onWheel,{passive:false});
    el.cv.addEventListener('contextmenu',function(ev){ev.preventDefault();});
    /* __acad3dV110: the gizmo menu closes on any press outside it (Escape: see onKey) */
    document.addEventListener('mousedown',function(ev){
      if(!document.getElementById('a3d-gizmenu'))return;
      if(ev.target&&ev.target.closest&&ev.target.closest('#a3d-gizmenu'))return;
      bimCloseGizmoMenu();
    },true);
    el.cv.addEventListener('touchstart',onTouchStart,{passive:false});
    window.addEventListener('touchmove',onTouchMove,{passive:false});
    window.addEventListener('touchend',onTouchEnd,{passive:false});
    window.addEventListener('touchcancel',onTouchEnd,{passive:false});
    window.addEventListener('keydown',onKey,true);
    window.addEventListener('resize',function(){if(A3D.on)size();});
  }
  function bimSyncGlCanvasSize(){
    var g=document.getElementById('a3d-glcanvas');
    if(g&&el.cv){if(g.width!==el.cv.width)g.width=el.cv.width;if(g.height!==el.cv.height)g.height=el.cv.height;}
  }
