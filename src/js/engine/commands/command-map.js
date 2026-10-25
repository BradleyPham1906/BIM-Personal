  /* ================= __acad3dV86: the command palette runs against the BIM engine =========

     Every entry here was driven before it was listed. A command with no BIM implementation is
     NOT in this table and therefore is not offered by the palette -- that is the point. */
  /* __acad3dV115: PLOT plots what is on screen, as AutoCAD's does: the open sheet goes to the print
     dialog as vector, and model space goes to PDF -- AutoCAD's default plotter is a PDF writer too. */
  function bimPlot(){
    if(el.sheetview&&el.sheetview.classList.contains('open')&&bimSheetById(A3D.activeSheetId)){bimPrintSheet();return;}
    bimExportPDF();
  }
  /* __acad3dV115: the only commands that make sense with no project current */
  var BIM_START_CMDS={newProject:1,openJson:1};
  var BIM_SHEET_CMDS={saveJson:1,openJson:1,newProject:1,closeProject:1,undo:1,redo:1,print:1,   /* __acad3dV116 */
    newSheet:1,modelTab:1,mspace:1,pspace:1,shortcuts:1,layers:1};   /* __acad3dV121: LAYER works on a sheet, as AutoCAD's does */
  var BIM_SHEET_ACTS={'bim:sheet':1,'bim:titleblock':1,'bim:projinfo':1,'bim:uipanels':1,'m:saveproj':1,'m:openproj':1};
  var BIM_CMD_MAP={
    line:function(){startSketch('line');},
    poly:function(){startSketch('poly');},
    rect:function(){startSketch('rect');},
    circle:function(){startSketch('circle');},
    text:function(){startTextTool();},
    leader:function(){startLeaderTool();},
    bimDims:function(){startDimTool();},
    measure:function(){startDimTool();},
    trim:function(){startTrimTool();},
    /* __acad3dV87: rotate, arrayRect and arrayPolar, reachable from the command line. A working
       tool that no command can start is the same leftover as a control that no longer does
       anything. */
    arc:function(){startArcTool();},          /* __acad3dV88 */
    polygon:function(){openPolygonDlg();},    /* __acad3dV93 */
    /* __acad3dV95: the BIM toolset, reachable from the command line. */
    room:function(){startRoomTool();},
    roomtag:function(){startRoomTagTool();},          /* __acad3dV101 */
    roomtagall:function(){bimTagAllRooms();},         /* __acad3dV101 */
    colourby:function(){bimLensCommand();},          /* __acad3dV136 */
    roomcolor:function(){bimCycleRoomScheme();},       /* __acad3dV105 */
    tribarea:function(){bimToggleTrib();},             /* __acad3dV106 */
    areaplan:function(){bimToggleAreaPlan();},        /* __acad3dV105b */
    sunstudy:function(){bimToggleSun();},             /* __acad3dV107 */
    survey:function(){openSurveyDlg();},              /* __acad3dV108 */
    surveycheck:function(){bimSurveyCheckCommand();},  /* __acad3dV138 */
    breakline:function(){bimBreaklineCommand();},      /* __acad3dV144 */
    grade:function(){bimGradeCommand();},              /* __acad3dV145 */
    commit:function(){bimHistCommitCommand();},        /* __acad3dV146 */
    history:function(){bimHistReveal(false);},
    branch:function(){bimHistReveal(false);setTimeout(function(){var i=document.querySelector('#a3d-propsbody [data-brname]');if(i)i.focus();},0);},   /* __acad3dV151 */
    merge:function(){bimHistReveal(false);if(bimHistBranches().length<2)a3dToast('There is one branch: start another with BRANCH');},
    comparebranches:function(){A3D_BR_CMP=true;bimHistReveal(false);},
    graphics:function(){bimGraphicsCommand();},   /* __acad3dV153 */
    benchmark:function(){bimBenchmark();},   /* __acad3dV155 */
    cutfill:function(){bimCutFillCommand();},
    cutfillmap:function(){bimCutFillMapCommand();},
    spotelev:function(){bimSpotCommand();},
    slopearrows:function(){bimSlopeArrowsCommand();},
    terrainboundary:function(){bimBoundaryCommand();},
    slopemap:function(){bimTerrainViewCommand('slope');},
    elevationmap:function(){bimTerrainViewCommand('elevation');},
    aspectmap:function(){bimTerrainViewCommand('aspect');},
    terrainviewoff:function(){bimTerrainViewCommand('');},
    landxmlout:function(){bimLandXmlExport(null);},
    landxmlin:function(){bimLandXmlPick();},
    footing:function(){startFootingTool('column');},  /* __acad3dV102 */
    footingall:function(){bimFootingsUnderAllColumns();},
    wallfoundation:function(){startFootingTool('wall');},
    foundslab:function(){startFoundationSlabTool();},
    propertyline:function(){openPropertyDlg(null);},                                   /* __acad3dV103 */
    propertyshape:function(){bimPropertyFromSketch(objById(A3D.sel));},
    propertyedit:function(){var o=objById(A3D.sel);if(bimIsProperty(o))openPropertyDlg(o);else a3dToast('Select a property line to edit');},
    truenorth:function(){openTrueNorthDlg();},
    floorTool:function(){startFloorTool();},
    ceilingTool:function(){startCeilingTool();},
    roofTool:function(){startRoofTool();},
    stairTool:function(){startStairTool();},
    columnTool:function(){startColumnTool();},
    beamTool:function(){startBeamTool();},
    doorTool:function(){startDoorTool();},
    windowTool:function(){startWindowTool();},
    gridline:function(){startGridTool();},
    sectionTool:function(){startSectionTool();},
    hatch:function(){bimOpenHatchDlg('new');},     /* __acad3dV96 */
    hatchedit:function(){bimOpenHatchDlg('edit');},/* __acad3dV96 */
    boundary:function(){startBoundaryTool();},/* __acad3dV95 */
    xline:function(){startClineTool(false);}, /* __acad3dV94 */
    ray:function(){startClineTool(true);},    /* __acad3dV94 */
    pointTool:function(){startPointTool();},  /* __acad3dV93 */
    divide:function(){bimOpenSpacingDlg('divide');},     /* __acad3dV93 */
    measurePts:function(){bimOpenSpacingDlg('measure');},/* __acad3dV93 */
    wall:function(){startWallTool();},        /* __acad3dV90: built in V5, unreachable until now */
    extend:function(){startExtendTool();},
    'break':function(){startBreakTool(false);},
    breakat:function(){startBreakTool(true);},
    lengthen:function(){startLengthenTool();},
    chamfer:function(){startChamferTool();},
    fillet:function(){applyFilletCorner();},
    scale:function(){startScaleTool();},
    gizmo:function(){bimGizmoCommand();},     /* __acad3dV110 */
    presspull:function(){bimPressPullCommand();},   /* __acad3dV123 */
    blockmake:function(){openSaveBlockDlg();},                   /* __acad3dV124 */
    analyze:function(){bimAnalyzeCommand();},                    /* __acad3dV125 */
    analyses:function(){bimAnalyzeCommandTab();},                 /* __acad3dV141 */
    docs:function(){bimDocsOpen('index.html');},                  /* __acad3dV142 */
    sunhours:function(){bimSunHoursCommand();},                   /* __acad3dV143 */
    solar:function(){bimSolarCommand();},
    rainflow:function(){bimRainCommand(null);},
    simclear:function(){var n=bimSimClear();a3dToast(n?'Simulations cleared':'No simulation to clear');},
    releasenotes:function(){bimDocsOpen('changelog.html',BIM_APP_VERSION.v.toLowerCase());},
    alignment:function(){bimAlignmentCommand();},
    usage:function(){bimUsageCommand();},                        /* __acad3dV131 */
    usages:function(){bimUsageLibraryCommand();},
    map:function(){bimMapCommand();},                            /* __acad3dV132 */
    findaddress:function(){openFindAddressDlg();},
    standards:function(){bimStdCommand();},                      /* __acad3dV167 */
    geoimport:function(){bimGeoImportPick();},
    geoexport:function(){bimGeoExport();},
    context:function(){bimCtxFetch();},                          /* __acad3dV133 */
    siteanalysis:function(){bimAnzView();},                      /* __acad3dV158; __acad3dV162: Analyze is one list */
    analyzesite:function(){bimAnzView();bimSiteAnalyze('');},   /* __acad3dV164 */
    animplay:function(){bimAnimPlay();},   /* __acad3dV170 */
    traffic:function(){bimAnzView();bimSaGoto('access');bimTrCommand(true);},   /* __acad3dV171 */
    trafficoff:function(){bimTrCommand(false);},
    climate:function(){bimBoardShow('climate');},                     /* __acad3dV162: the board's page in the set */
    zoning:function(){A3D_ZN.edit=true;bimSaGoto('legal');bimSaRefresh(true);},   /* __acad3dV160; __acad3dV162: in Legal */
    envelope:function(){bimZnBuild();},
    zoningboard:function(){bimBoardShow('zoning');},                           /* __acad3dV159 */
    climateget:function(){bimClimFetch();},                      /* __acad3dV159 */
    accessget:function(){bimAccFetch();},                        /* __acad3dV161 */
    access:function(){bimBoardShow('access');},
    walktimes:function(){bimResultLayerAdd('walk');},
    contextremove:function(){bimCtxRemove();},
    lodcheck:function(){bimLodCheck();},              /* __acad3dV139 */
    cityjsonout:function(){bimCityJsonExport();},
    cityjsonin:function(){bimCityJsonPick();},
    skpin:function(){bimSkpPick();},                  /* __acad3dV163 */
    finddata:function(){bimFindCommand();},                      /* __acad3dV135 */
    datalayers:function(){bimDataCommand();},                    /* __acad3dV134 */                /* __acad3dV127 */
    profileview:function(){bimStartProfileViewTool();},
    stationoffset:function(){bimStartStationTool();},
    analyzeoff:function(){bimAnalyzeOff();},
    structsupport:function(){bimStructFocus('support');},
    structload:function(){bimStructFocus('load');},
    blockinsert:function(){bimOpenLibraryAt('blocks');},
    assets:function(){bimOpenLibraryAt(null);},
    rotate:function(){startRotateTool();},
    arrayRect:function(){openArrayDlg();},
    arrayPolar:function(){startPolarArrayTool();},
    align:function(){openAlignDlg();},
    join:function(){applyMergeWalls();},
    mirror:function(){startMirrorTool();},
    offset:function(){openOffsetDlg();},
    duplicate:function(){duplicateSelection();},
    del:function(){delSelection();},
    zoomFit:function(){fitScene();},
    layers:function(){bimLayerManagerOpen();},   /* __acad3dV121: LAYER, listed since V86 and never run */
    selAll:function(){bimSelectByRule(A3D.objs);},   /* __acad3dV121: AutoCAD's ALL -- frozen and locked layers left out */
    selNone:function(){
      A3D.sel=null;A3D.sel2=null;A3D.selSet=[];
      refreshTree();refreshProps();paint();
    },
    bimSnap:function(){bimSetSnap({point:!A3D_SNAP.point});bimSyncSnapPill();paint();
      a3dToast('Object snap '+(A3D_SNAP.point?'on':'off'));},
    bimOrtho:function(){bimSetSnap({ortho:!A3D_SNAP.ortho});bimSyncSnapPill();paint();
      a3dToast('Ortho '+(A3D_SNAP.ortho?'on':'off'));},
    grid:function(){bimSetSnap({grid:!A3D_SNAP.grid});bimSyncSnapPill();paint();
      a3dToast('Grid snap '+(A3D_SNAP.grid?'on':'off'));},
    /* __acad3dV115: the document commands, which the quick-access bar's Save, Open, Undo, Redo and
       Plot run. */
    saveJson:function(){bimExportProjectFile();},
    newSheet:function(){bimLayoutNew();},          /* __acad3dV116: LAYOUT */
    modelTab:function(){bimShowModel();},          /* __acad3dV116: MODEL */
    mspace:function(){bimSetModelSpace(null);},    /* __acad3dV116: MSPACE */
    pspace:function(){if(!bimSetPaperSpace()&&!bimSheetOnScreen())a3dToast('PSPACE works on a sheet: open one from the layout tabs');},   /* __acad3dV116 */
    openJson:function(){bimOpenProjectPicker();},
    newProject:function(){bimDocsCreate();},
    closeProject:function(){bimDocsClose(A3D_DOCS.active);},
    undo:function(){doUndo();},
    redo:function(){doRedo();},
    print:function(){bimPlot();},
    /* Opens the V85 sheet through its own rail button, so there is one shortcuts sheet with one
       renderer rather than a second copy that could drift from the first. */
    shortcuts:function(){
      bimOpenToolsPanel();   /* __acad3dV130: the panel; already open, it stays open (the one guard is there) */
    }
  };
  window.__a3dCmdSupported=function(act){return !!BIM_CMD_MAP[act];};
