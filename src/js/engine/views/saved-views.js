  // ---- __acad3dV23: Saved views + view-specific annotations + level filtering ----
  // Saved views capture camera/mode/level/section (the section's cut PLANE only -- the cut-mesh
  // cache is recomputed on restore rather than stored, since it's large and derivable).
  // Annotations created while a view is active are tagged with that view's id and only render
  // there; annotations with no viewId (created before this existed, or with no active view)
  // stay global -- that fallback is what keeps every existing model working unchanged.
  function bimCaptureView(name){
    var c=A3D.cam;
    return {
      id:'view-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e6),
      name:name,
      cam:{yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz},
      flat:A3D.flat,viewLabel:A3D.view,levelId:A3D.activeLevel,levelFilter:!!A3D.levelFilter,
      section:A3D.section?{p:A3D.section.p,dir:A3D.section.dir,keepSign:A3D.section.keepSign}:null
    };
  }
  function bimSaveCurrentView(){
    var name=window.prompt('Name this view','View '+(A3D.views.length+1));
    if(name===null)return;
    name=String(name).trim();
    if(!name){a3dToast('View name cannot be empty');return;}
    pushUndo();
    var v=bimCaptureView(name);
    A3D.views.push(v);
    bimSetActiveView('saved',v.id,v);   /* __acad3dV119: the saved view is the one on screen, and named so */
    refreshViews();paint();saveSoon();
    a3dToast('Saved view "'+name+'"');
  }
  function bimApplyView(id){
    var v=null,i;
    for(i=0;i<A3D.views.length;i++)if(A3D.views[i].id===id){v=A3D.views[i];break;}
    if(!v){a3dToast('View not found');return false;}
    if(A3D.section)bimExitSection();
    var c=A3D.cam;
    /* __acad3dV119: where the model was before this view. A section view's Exit goes back there, as a
       section drawn with the tool does, the record with the camera; it used to stay at the section's
       own angle with the cut gone, still named Section. From a sheet: the model view the sheet was
       opened from, whose camera is still the model's. */
    var back={yaw:c.yaw,pitch:c.pitch,dist:c.dist,tx:c.tx,ty:c.ty,tz:c.tz,flat:A3D.flat,view:A3D.view,
      record:(A3D_VIEW.kind==='sheet')?(A3D_LAST_MODEL_VIEW||{kind:'plan',id:A3D.activeLevel})
                                      :{kind:A3D_VIEW.kind,id:A3D_VIEW.id}};
    c.yaw=v.cam.yaw;c.pitch=v.cam.pitch;c.dist=v.cam.dist;
    c.tx=v.cam.tx;c.ty=v.cam.ty;c.tz=v.cam.tz;
    A3D.flat=!!v.flat;
    A3D.view=v.viewLabel||'Custom';
    if(v.levelId)A3D.activeLevel=v.levelId;
    A3D.levelFilter=!!v.levelFilter;
    if(el.flip){el.flip.textContent=A3D.flat?'3D':'2D';el.flip.setAttribute('title',A3D.flat?'Go to 3D (>)':'Go to 2D (>)');}
    if(el.root)el.root.classList.toggle('flat',A3D.flat);
    if(v.section){
      bimEnterSection(v.section.p,v.section.dir,back);   /* __acad3dV119 */
      if(v.section.keepSign===-1)bimFlipSection();
    }
    bimSyncActiveGlobal();
    refreshViews();refreshLevels();refreshTree();refreshHud();paint();saveSoon();
    a3dToast('View: '+v.name);
    return true;
  }
  /* ================= __acad3dV84: a view is where you are, not a mode you picked ============

     Revit's model: the Project Browser lists views, and you open one. There are no modes.

     Everything that opens a view now goes through bimActivateView. That matters beyond tidiness:
     the floor-plan row in the browser used to read "if(!A3D.flat)toggleFlat()", and an elevation
     is ALSO flat, so opening a floor plan from any elevation changed the level and left the
     camera looking sideways at it -- measured, twice, before this patch. One activation path is
     what stops a per-row fix from leaving the next row broken. */
  var A3D_VIEW={kind:'plan',id:null,name:'Floor Plan'};
  /* __acad3dV116: where the model was when a sheet was opened -- the view and its camera -- so the
     Model tab goes back to exactly that, the way AutoCAD's does. Per project: the project tabs keep
     it with the rest of a project's runtime state. */
  var A3D_LAST_MODEL_VIEW=null;

  /* The name of a view, as the HUD and Properties' View row show it. `sv` is the saved-view record,
     passed in rather than looked up again so a view deleted mid-activation cannot produce a blank
     label. */
  function bimViewLabelFor(kind,id,sv){
    var i;
    if(kind==='plan'){
      for(i=0;i<A3D.levels.length;i++)
        if(A3D.levels[i].id===id)return A3D.levels[i].name+' - Floor Plan';
      return 'Floor Plan';
    }
    if(kind==='elev')return (VIEWS[id]&&VIEWS[id].label)||'Elevation';
    if(kind==='sheet'){
      var sh=bimSheetById(id);
      return bimSheetLabel(sh);   /* __acad3dV116 */
    }
    if(kind==='saved'){
      if(!sv)sv=bimSavedViewById(id);   /* __acad3dV119: the sync names views it did not open */
      return (sv&&sv.name)||'View';
    }
    if(kind==='section')return 'Section';   /* __acad3dV119 */
    return '3D View';
  }

  /* kind: 'plan' | '3d' | 'elev' | 'saved' | 'sheet' | 'section'
     id:   level id / (none) / VIEWS preset key / saved view id / sheet id / (none: the live section)

     Returns true only when the view is actually open. Every failure path warns on the console
     AND toasts, and leaves the previous view exactly as it was -- a view switch that half
     happens is worse than one that declines. */
  function bimActivateView(kind,id,opts){
    opts=opts||{};
    var anim=(opts.anim!==false),sv=null,q;
    if(A3D_CLB.open)bimClbClose();   /* __acad3dV162: a board's page gives the main view back */
    try{
      /* Leaving a sheet is not optional: the paper canvas covers the model canvas, so any view
         that is not a sheet must close it first or the user opens a view they cannot see. */
      if(kind==='sheet'&&A3D_VIEW.kind!=='sheet'){   /* __acad3dV116 */
        A3D_LAST_MODEL_VIEW={kind:A3D_VIEW.kind,id:A3D_VIEW.id,
          cam:{yaw:A3D.cam.yaw,pitch:A3D.cam.pitch,dist:A3D.cam.dist,tx:A3D.cam.tx,ty:A3D.cam.ty,tz:A3D.cam.tz}};
      }
      if(kind!=='sheet')bimCloseSheetView();
      if(kind==='plan'){
        if(A3D.section)bimExitSection();
        if(id)setActiveLevel(id);
        id=A3D.activeLevel;
        bimAimPreset('top',anim);
        /* bimAimPreset would name this 'Top (Plan)'. The camera's word has been 'Plan' since V18
           and other code reads that string, so keep it. */
        A3D.view='Plan';
      }else if(kind==='3d'){
        if(A3D.section)bimExitSection();
        bimAimPreset(opts.home?'home':'iso',anim);   /* __acad3dV119: Home is the 3D view, framed afresh */
      }else if(kind==='elev'){
        if(!VIEWS[id]||!VIEWS[id].ortho){
          console.warn('[BIM] Unknown elevation preset: '+id);
          a3dToast('That elevation view is not defined');
          return false;
        }
        if(A3D.section)bimExitSection();
        bimAimPreset(id,anim);
      }else if(kind==='saved'){
        if(!bimApplyView(id))return false;
        for(q=0;q<A3D.views.length;q++)if(A3D.views[q].id===id){sv=A3D.views[q];break;}
        if(!sv){
          console.warn('[BIM] Saved view vanished during activation: '+id);
          return false;
        }
      }else if(kind==='section'){
        /* __acad3dV119: the live section, which a sheet opened over it leaves in place -- the Model
           tab comes back to it. There is one at a time, so it has no id. */
        if(!A3D.section){
          console.warn('[BIM] There is no open section to go back to.');
          a3dToast('That section is no longer open');
          return false;
        }
        id=null;
      }else if(kind==='sheet'){
        if(!bimSheetById(id)){
          console.warn('[BIM] Unknown sheet: '+id);
          a3dToast('Sheet not found');
          return false;
        }
        bimOpenSheetView(id);
      }else{
        console.warn('[BIM] Unknown view kind: '+kind);
        a3dToast('Unknown view type');
        return false;
      }
    }catch(eV){
      console.warn('[BIM] Could not activate the view; the previous view is unchanged.',eV);
      a3dToast('Could not open that view');
      return false;
    }
    bimSetActiveView(kind,id,sv);   /* __acad3dV119: the record, and everything that reads it */
    paint();saveSoon();
    return true;
  }
  /* __acad3dV119: the record of the view on screen, and the readouts that follow it. Every view
     switch ends here -- bimActivateView, the plan / 3D switch, a section going in and coming back
     out -- because the HUD names the active view now, and a switch that went around the record left
     the HUD, the Project Browser's marks and Properties all naming the view before it. `sv`, the
     saved view, is looked up when it is not passed. */
  function bimSavedViewById(id){
    var q;
    for(q=0;q<A3D.views.length;q++)if(A3D.views[q].id===id)return A3D.views[q];
    return null;
  }
  function bimSetActiveView(kind,id,sv){
    if(kind==='saved'&&!sv)sv=bimSavedViewById(id);
    A3D_VIEW={kind:kind,id:id||null,name:bimViewLabelFor(kind,id,sv)};
    /* The saved view on screen is the record's, and nothing else's: the Project Browser marks it
       and new annotations are tagged with it, so it is set here with the record and cleared by
       every switch away from it. */
    A3D.activeViewId=(kind==='saved')?(id||null):null;
    /* __acad3dV120: 'da' for a plan, a section or a sheet, '3d' for a 3D view -- what a project tab
       falls back to when it opens with no view of its own. */
    window.ACAD_WS_CUR=(kind==='3d'||(kind==='saved'&&sv&&!sv.flat))?'3d':'da';
    /* refreshProps too: without it the Properties panel keeps its boot-time render, which is
       how a panel reading "View 3D" ended up sitting beside a status bar reading "View: Plan"
       in the Phase 84 visual review. */
    refreshHud();refreshBrowser();refreshProps();
  }
  /* __acad3dV119: the camera is a plan -- flat, looking straight down, and not a section. "Flat" alone
     is not the test: an elevation is flat, and so is a section. */
  function bimCameraIsPlan(){
    return !!(A3D.flat&&!A3D.section&&A3D.cam.pitch>1.4);
  }
  /* __acad3dV119: the view the camera shows, for when no record names it. A flat camera cannot orbit
     (a drag pans it), so a flat camera that is not a plan looks straight up or along one of the
     elevation presets, and the nearest preset is the one it was set to. */
  function bimViewOfCamera(){
    var c=A3D.cam,k,d,dy,best=null,bd=1e9;
    if(A3D.section)return {kind:'section',id:null};
    if(!A3D.flat)return {kind:'3d',id:null};
    if(bimCameraIsPlan())return {kind:'plan',id:A3D.activeLevel};
    for(k in VIEWS){
      if(!VIEWS.hasOwnProperty(k)||!VIEWS[k].ortho||k==='top')continue;
      dy=c.yaw-VIEWS[k].yaw;
      d=Math.abs(Math.atan2(Math.sin(dy),Math.cos(dy)))+Math.abs(c.pitch-VIEWS[k].pitch);
      if(d<bd){bd=d;best=k;}
    }
    return {kind:'elev',id:best};
  }
  /* __acad3dV119: the record is re-derived from what it names on every refresh of the lists those
     names live in (the layout tabs, and so the Project Browser, which draws them first), because the
     HUD shows it. The plan is the active level's, so a level switched from the status bar or from
     Properties, deleted while its plan is open, or put back by an undo switches the plan with it. A
     saved view that is no longer there -- deleted while open, or undone away -- stops being the
     record, and the view the camera shows takes its place; nothing moves. V116 did this for a
     sheet's name, and a renamed sheet still renames its view here. */
  function bimViewSync(){
    var k=A3D_VIEW.kind,id=A3D_VIEW.id,f;
    if(k==='saved'&&!bimSavedViewById(id)){
      f=bimViewOfCamera();
      bimSetActiveView(f.kind,f.id,null);
      return;
    }
    if(k==='plan')id=A3D.activeLevel;
    var nm=bimViewLabelFor(k,id,null);
    if(id===A3D_VIEW.id&&nm===A3D_VIEW.name)return;
    A3D_VIEW={kind:k,id:id||null,name:nm};
    refreshHud();refreshProps();
  }
  function bimDeleteView(id){
    var i;
    for(i=0;i<A3D.views.length;i++){
      if(A3D.views[i].id===id){
        pushUndo();
        A3D.views.splice(i,1);
        /* __acad3dV119: the record lets go of it in bimViewSync, which refreshViews reaches */
        refreshViews();paint();saveSoon();
        a3dToast('View deleted');
        return true;
      }
    }
    return false;
  }
  function bimAnnotationVisible(o){
    if(!o.viewId)return true;
    return o.viewId===A3D.activeViewId;
  }
  function bimObjectLevelId(o){
    if(o.bim&&o.bim.levelId)return o.bim.levelId;
    if(o.levelId)return o.levelId;
    return null;
  }
  function bimObjectVisibleOnLevel(o){
    if(!A3D.levelFilter)return true;
    var lv=bimObjectLevelId(o);
    if(!lv)return true;
    return lv===A3D.activeLevel;
  }
  function bimToggleLevelFilter(){
    A3D.levelFilter=!A3D.levelFilter;
    refreshViews();refreshHud();paint();saveSoon();
    a3dToast(A3D.levelFilter?'Showing active level only':'Showing all levels');
  }
  function refreshViews(){
    if(el.browser)refreshBrowser();
    if(!el.viewrows)return;
    var h='';
    h+='<label class="a3d-lvlfilter"><input type="checkbox" id="a3d-lvlfilter-cb"'+(A3D.levelFilter?' checked':'')+'> Active level only</label>';
    if(!A3D.views.length){
      h+='<div class="a3d-propnote">No saved views yet. Set up a camera angle and click Save View.</div>';
    }else{
      var i;
      for(i=0;i<A3D.views.length;i++){
        var v=A3D.views[i];
        var tag=v.section?'Section':(v.flat?'2D':'3D');
        h+='<div class="a3d-famrow'+(A3D.activeViewId===v.id?' sel':'')+'" data-viewid="'+v.id+'">'+
          '<div class="a3d-famcat">'+tag+'</div>'+
          '<div class="a3d-famname">'+bimEsc(v.name)+'</div>'+
          '<button class="a3d-famplace" data-viewgo="'+v.id+'" title="Go to this view">Go</button>'+
          '<button class="a3d-famdel" data-viewdel="'+v.id+'" title="Delete view">\u00d7</button>'+
        '</div>';
      }
    }
    bimRenderInto(el.viewrows,h);   /* __acad3dV118 */
  }

