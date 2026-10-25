/* __acad3dV120: the shell -- the top bar, the command palette and the project tabs, and the boot
   into the BIM workspace. The engine is the next script. */
(function acadTopBar(){
  /* __acad3dV120: the top bar -- the quick-access buttons, and the host for the project tabs that
     the project section below fills. Each button runs its command through the BIM engine. */
  try{
    var QAT=[
      ['saveJson','Save','<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M5 3h11l3 3v15H5z"/><path d="M8 3v6h8V3"/><rect x="8" y="13" width="8" height="8"/></svg>'],
      ['openJson','Open','<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 6h6l2 2h10v11H3z"/><path d="M3 10h18"/></svg>'],
      '|',
      ['undo','Undo','<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M9 7H5V3"/><path d="M5 7a9 9 0 1 1 1 10"/></svg>'],
      ['redo','Redo','<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M15 7h4V3"/><path d="M19 7A9 9 0 1 0 18 17"/></svg>'],
      '|',
      ['print','Plot','<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M7 9V3h10v6"/><rect x="3" y="9" width="18" height="7" rx="1"/><path d="M7 16h10v5H7z"/></svg>']
    ];
    var dispatch=function(act){
      if(window.__a3dCmdSupported&&window.__a3dCmdSupported(act)){window.__a3dRunCmd(act);return;}
      console.warn('[BIM] No command runs the act '+act);
      if(window.__a3dToast)window.__a3dToast('That command is not available');
    };
    var shell=document.createElement('div');shell.id='acad-shell';
    var qat=document.createElement('div');qat.id='acad-qat';
    qat.innerHTML='<div class="acad-logo" title="CAD/BIM workspace">A</div>'+QAT.map(function(q){
      if(q==='|')return '<div class="acad-qsep"></div>';
      return '<button class="acad-qbtn" data-acad-act="'+q[0]+'" title="'+q[1]+'">'+q[2]+'</button>';
    }).join('')+'<div class="acad-spring"></div>';
    shell.appendChild(qat);
    var dt=document.createElement('div');dt.id='acad-doctabs';
    shell.appendChild(dt);
    shell.addEventListener('click',function(e){
      var ab=e.target.closest('[data-acad-act]');
      if(ab)dispatch(ab.getAttribute('data-acad-act'));
    });
    document.body.appendChild(shell);
    document.body.classList.add('acad-on');
  }catch(err){
    console.warn('[BIM] The top bar could not be built.',err);
    setTimeout(function(){if(window.__a3dToast)window.__a3dToast('The top bar could not be built; reload the page');},1500);
  }
})();

(function acadWorkspaceV1(){
  try{

  // ============ SHARED COMMAND REGISTRY (palette == command line) ============
  var CADCMDS=[
    ['LINE',['L'],'line','Draw a line'],['PLINE',['PL','POLYLINE','POLY'],'poly','Draw a polyline'],
    ['WALL',['WA'],'wall','Draw a wall (A for arc segments)'],
    ['RECTANG',['REC','RECT','RECTANGLE'],'rect','Draw a rectangle'],['CIRCLE',['C'],'circle','Draw a circle'],
    ['ARC',['A'],'arc','Draw a 3-point arc'],['ELLIPSE',['EL'],'ellipse','Draw an ellipse'],
    ['POLYGON',['POL'],'polygon','Draw a polygon'],['SKETCH',['DRAW'],'draw','Freehand sketch'],
    ['MTEXT',['T','MT'],'text','Text box'],['TEXT',['DT'],'text','Text box'],
    ['SPLINE',['SPL'],'spline','Spline through fit points'],
    ['ROOM',['RM'],'room','Make a room from an enclosed region'],
    ['ROOMTAG',['RT','TAGROOM'],'roomtag','Tag a room with its number and name'],
    ['TAGALLROOMS',['TAGALL'],'roomtagall','Tag every untagged room on the active level'],
    ['COLOURBY',['COLORBY','LENS'],'colourby','Colour the model by usage, level, type, layer, material, height or any property, with a legend'],   /* __acad3dV136 */
    ['ROOMCOLOR',['COLORFILL','ROOMCOLOUR'],'roomcolor','Fill rooms by Department, then by Occupancy, then off'],   /* __acad3dV105 */
    ['TRIBAREA',['TRIBUTARY','TRIB'],'tribarea','Show or hide the tributary area each column carries on this level'],   /* __acad3dV106 */
    ['AREAPLAN',['AREA','GROSSAREA','AP'],'areaplan','Show or hide the gross area inside the exterior walls on this level'],   /* __acad3dV105b */
    ['SUNSTUDY',['SHADOWS','SUNPATH'],'sunstudy','Show or hide the shadows on the ground and the sun path, for the site date and time'],   /* __acad3dV107 */
    ['COMMIT',['CHECKPOINT','SAVEVERSION'],'commit','Keep this state of the model as a version, with a message: what changed, element by element'],   /* __acad3dV146 */
    ['HISTORY',['VERSIONS','VERSIONHISTORY'],'history','The model\'s versions: what changed in each, element by element, and Restore'],
    ['BRANCH',['NEWBRANCH','DESIGNOPTION','OPTION'],'branch','Start a design option: a branch of the history, switched to and compared with the others'],   /* __acad3dV151 */
    ['BENCHMARK',['BENCH','FRAMETIME','SPEEDTEST'],'benchmark','Time this device drawing 5,000 and 20,000 elements, with WebGPU and with WebGL; the model is put back as it was'],   /* __acad3dV155 */
    ['GRAPHICS',['RENDERER','WEBGPU','WEBGL'],'graphics','Draw 3D with WebGPU where the browser has it, or always with WebGL in this browser'],   /* __acad3dV153 */
    ['MERGE',['MERGEBRANCH'],'merge','Merge another branch into this one, element by element, with conflicts shown side by side'],
    ['COMPAREBRANCHES',['COMPAREOPTIONS','OPTIONS'],'comparebranches','Each branch\'s numbers side by side: walls, rooms, areas, cut and fill'],
    ['GRADE',['GRADING','DAYLIGHT','GRADEPADS'],'grade','Grade the pads onto the ground: cut and fill slopes run out to the daylight line, into a proposed surface'],   /* __acad3dV145 */
    ['CUTFILL',['VOLUMES','TINVOLUME','SURFACEVOLUME'],'cutfill','Cut and fill between two surfaces (the existing one first), or of every proposed surface against its existing one'],
    ['CUTFILLMAP',['CUTFILLCOLOUR','CUTFILLCOLOR'],'cutfillmap','Colour the proposed surface by how deep it cuts or fills'],
    ['SPOTELEV',['SPOT','SPOTELEVATION','SPOTHEIGHT'],'spotelev','Label the selected points with the height of the surface under them'],
    ['SLOPEARROWS',['ARROWS','FLOWARROWS'],'slopearrows','Show or hide arrows down the slope of the terrain, with its percentage'],
    ['BREAKLINE',['BRK','BREAKLINES'],'breakline','Hold the selected polylines in the terrain surface as breaklines: the triangles follow them'],   /* __acad3dV144 */
    ['TERRAINBOUNDARY',['TINBOUNDARY','SURFACEBOUNDARY'],'terrainboundary','Trim the terrain surface to the selected closed polyline'],
    ['SLOPEMAP',['SLOPE','SLOPEANALYSIS','GRADEANALYSIS'],'slopemap','Colour the terrain by slope, in the bands of the standards registry (Properties > Site > Standards), with the area of each'],
    ['ELEVATIONMAP',['ELEVATIONBANDS','HYPSOMETRIC'],'elevationmap','Colour the terrain by elevation, in seven bands, with the area of each'],
    ['ASPECTMAP',['ASPECT','ASPECTANALYSIS'],'aspectmap','Colour the terrain by the way it faces: north, north-east, east ...'],
    ['TERRAINANALYSISOFF',['TERRAINOFF'],'terrainviewoff','Stop colouring the terrain'],
    ['LANDXMLOUT',['EXPORTLANDXML','LANDXML'],'landxmlout','Export the terrain surfaces as LandXML 1.2: points, triangles, breaklines and boundary, in the survey\'s own coordinates'],
    ['LANDXMLIN',['IMPORTLANDXML'],'landxmlin','Import the TIN surfaces of a LandXML file, keeping their own triangles'],
    ['SURVEYCHECK',['VERIFYSURVEY','QA'],'surveycheck','Check a survey surface: every line read, duplicates, the surface through every point, bust shots, check shots, control points, and the public terrain'],   /* __acad3dV138 */
    ['SURVEY',['TOPO','SURFACE'],'survey','Make a terrain surface from survey points: contours, and cut and fill against building pads'],   /* __acad3dV108 */
    ['FOOTING',['FTG'],'footing','Isolated footing under a column'],
    ['FOOTINGSALL',[],'footingall','Footings under every column on the active level'],
    ['WALLFOUNDATION',['WF'],'wallfoundation','Strip footing under a wall'],
    ['FOUNDATIONSLAB',['FS'],'foundslab','Foundation slab in an enclosed region'],
    ['PROPERTYLINE',['PROP'],'propertyline','Property line from bearings and distances'],
    ['PROPERTYFROMSHAPE',['PROPSH'],'propertyshape','Property line from the selected closed shape'],
    ['PROPERTYEDIT',['PROPED'],'propertyedit','Edit the legs of the selected property line'],
    ['TRUENORTH',['TN'],'truenorth','Set the angle from project north to true north'],
    ['FLOOR',['FL','SLAB'],'floorTool','Place a floor slab in a closed region'],
    ['CEILING',['CEIL'],'ceilingTool','Place a ceiling in a closed region'],
    ['ROOF',['RF'],'roofTool','Place a roof over a closed region'],
    ['STAIR',['STAIRS'],'stairTool','Draw a stair run'],
    ['COLUMN',['COL'],'columnTool','Place a column'],
    ['BEAM',['BM'],'beamTool','Draw a beam between two points'],
    ['DOOR',['DR'],'doorTool','Place a door in a wall'],
    ['WINDOW',['WIN'],'windowTool','Place a window in a wall'],
    ['GRIDLINE',['GL'],'gridline','Draw a structural gridline'],
    ['SECTION',['SEC'],'sectionTool','Cut a section through the model'],
    ['GIZMO',['GZ'],'gizmo','Show the transform gizmo, or set its alignment'],
    ['PRESSPULL',['PP','PUSHPULL'],'presspull','Push or pull a face: click the face, then drag its arrow or type'],   /* __acad3dV123 */
    ['HATCHEDIT',['HE'],'hatchedit','Change a hatch pattern, angle or scale'],
    ['BOUNDARY',['BO','BPOLY'],'boundary','Trace the closed region around a picked point'],
    ['XLINE',['XL'],'xline','Construction line, infinite both ways'],
    ['RAY',[],'ray','Construction ray, infinite one way'],
    ['MLINE',['ML'],'mline','Multiline'],['DONUT',['DO'],'donut','Donut'],
    ['POINT',['PO'],'pointTool','Point'],['HATCH',['H','BH'],'hatch','Hatch closed region'],
    ['LEADER',['LE','QLEADER'],'leader','Leader balloon'],['TRIM',['TR'],'trim','Trim to intersection'],
    ['EXTEND',['EX'],'extend','Extend to boundary'],['FILLET',['F'],'fillet','Fillet two walls (radius 0)'],
    ['CHAMFER',['CHA'],'chamfer','Chamfer a corner between two walls'],['EXPLODE',['X'],'explode','Explode into segments'],
    ['MOVE',['M'],'moveTool','Move selection'],['COPY',['CO','CP'],'duplicate','Copy selection'],
    ['BREAK',['BR'],'break','Break a wall between two points'],
    ['BREAKATPOINT',['BRP','BREAKAT'],'breakat','Split a wall at one point'],
    ['LENGTHEN',['LEN'],'lengthen','Change a wall length at one end'],
    ['JOIN',['J'],'join','Join two colinear walls into one'],
    ['ALIGN',['AL'],'align','Align objects to the first selected'],
    ['ARRAYRECT',['AR','ARRAY','ARRAYCLASSIC'],'arrayRect','Rectangular array'],
    ['ARRAYPOLAR',['ARP'],'arrayPolar','Polar array'],
    ['ROTATE',['RO'],'rotate','Rotate about a base point'],['ROTATECCW',['RCC'],'rotCCW','Rotate 90 CCW'],
    ['ROTATE0',['RZ'],'rot0','Reset rotation'],['SCALE',['SC','SCU'],'scale','Scale about a base point'],
    ['SCALEDOWN',['SCD'],'scaleDown','Scale to 80%'],['MIRROR',['MI'],'mirror','Mirrored copy'],
    ['OFFSET',['O'],'offset','Parallel copy'],['ERASE',['E','DEL'],'del','Delete selection'],
    /* __acad3dV93: MEASURE was an alias of DIST. In AutoCAD they are different commands --
       DIST reports a distance, MEASURE steps points off along an object -- so the alias made
       the real command unreachable by its own name. */
    ['DIST',['DI'],'measure','Measure distance'],
    ['DIVIDE',['DIV'],'divide','Place points dividing an object into equal parts'],
    ['MEASURE',['ME'],'measurePts','Place points at a set spacing along an object'],['DIMLINEAR',['DLI','DIM'],'bimDims','Linear dimension'],
    ['LAYER',['LA','LAYERS'],'layers','Layer Properties Manager'],['OSNAP',['OS'],'bimSnap','Toggle object snap'],
    ['ORTHO',[],'bimOrtho','Toggle ortho mode'],['GRID',[],'grid','Toggle grid'],
    ['ZOOM',['Z','ZE','FIT'],'zoomFit','Zoom to fit'],['ZOOMIN',['ZI'],'zoomIn','Zoom in'],
    ['ZOOMOUT',['ZO'],'zoomOut','Zoom out'],['ZOOM100',['Z1'],'view100','Zoom to 100%'],
    ['SELECTALL',['SA','ALL'],'selAll','Select every object'],['CLEAR',[],'selNone','Clear selection'],
    ['SHORTCUTS',['KEYS','HELP','?'],'shortcuts','Keyboard shortcuts'],
    /* __acad3dV115: the document commands, last so the palette's opening list is unchanged */
    ['NEW',['QNEW'],'newProject','Start a new project in a tab of its own'],
    ['OPEN',[],'openJson','Open a project file in a tab of its own'],
    ['CLOSE',[],'closeProject','Close this project\'s tab'],
    ['SAVE',['QSAVE','SAVEAS'],'saveJson','Save this project as a file'],
    ['PLOT',['PRINT'],'print','Plot the open sheet, or model space to PDF'],
    ['UNDO',['U'],'undo','Undo the last change'],
    ['REDO',[],'redo','Redo what was undone'],
    /* __acad3dV116: the layout commands */
    ['LAYOUT',['NEWSHEET'],'newSheet','New sheet, opened on its own layout tab'],
    ['MODEL',[],'modelTab','Back to the Model tab'],
    ['MSPACE',['MS'],'mspace','Work in the model through a viewport on this sheet'],
    ['PSPACE',['PS'],'pspace','Back to paper space on this sheet'],
    /* __acad3dV124: the library */
    ['BLOCK',['B','BMAKE'],'blockmake','Save the selection to the library as a block'],
    /* __acad3dV125: the frame analysis -- a display turned on and off, as Rhino's analysis modes are */
    ['ANALYZE',['ANALYSE','AN'],'analyze','Solve the frame and show its forces and deflection over the model'],
    ['SUNHOURS',['SUNLIGHTHOURS','DAYLIGHTHOURS'],'sunhours','Hours of direct sun on the ground through the site\'s date, drawn over the plan'],   /* __acad3dV143 */
    ['SOLAR',['SOLARRADIATION','INSOLATION','IRRADIATION'],'solar','A clear-sky year of sun on the roofs and facades: kWh/m2 on each building, shaded by the others'],
    ['RAINFLOW',['RAIN','DRAINAGE','PONDING','RUNOFF'],'rainflow','Where rain runs and ponds on the terrain: flow lines and ponds over the plan'],
    ['SIMCLEAR',['CLEARSIM'],'simclear','Clear the simulations from the drawing'],
    ['DOCS',['GUIDE','MANUAL','USERGUIDE'],'docs','Open the user guide: getting started, every topic, and the command reference'],   /* __acad3dV142 */
    ['RELEASENOTES',['VERSION','WHATSNEW'],'releasenotes','What changed in this version, and every version before it'],
    ['ANALYSES',['ANALYZEPANEL','ANALYSISPANEL'],'analyses','The Analyze tab: every analysis, what it shows now, and its settings'],   /* __acad3dV141 */
    ['ANALYZEOFF',['ANALYSEOFF'],'analyzeoff','Turn the analysis display off'],
    ['SUPPORT',['SUP'],'structsupport','Set how the selected column\'s base is held (Properties)'],
    ['LOAD',['LD'],'structload','Add a load to the selected beam or column (Properties)'],
    /* __acad3dV127: the alignment */
    ['ALIGNMENT',['ALIGN_CREATE','ALN'],'alignment','Make the selected open polyline an alignment: its vertices become the PIs'],
    ['PROFILEVIEW',['PV'],'profileview','Place the selected alignment\'s profile view where you click'],
    ['STATION',['STA','STAOFF'],'stationoffset','Read the station and offset of points along the selected alignment'],
    /* __acad3dV131: usages */
    ['USAGE',['US'],'usage','Give the selected rooms, floors or masses a usage (Residential, Office...); with none selected, the usages'],
    ['USAGES',['USES','PROGRAM'],'usages','The usages: each one\'s colour, area ratios, floor-to-floor height, parameters and formulas'],
    /* __acad3dV132: the map */
    ['MAP',['BASEMAP'],'map','The basemap under the drawing: off, street map, satellite, your own tiles -- each run the next'],
    ['FINDADDRESS',['ADDRESS','GEOCODE'],'findaddress','Find an address on OpenStreetMap and put the site there: model 0,0'],
    ['STANDARDS',['STANDARDSREGISTRY','CODES','STDS'],'standards','Standards: the editions in force for the site\'s place and date, their sources, overrides with a reason, the codes in force there, and standards packs, in Properties, Site'],   /* __acad3dV167 */
    ['GEOIMPORT',['IMPORTGEOJSON','KML','GEOJSON'],'geoimport','Import GeoJSON or KML as site data, placed by longitude and latitude'],
    /* __acad3dV133: site context */
    ['CONTEXT',['SITECONTEXT','OSM'],'context','Get the buildings, roads, bridges, tunnels, railways, airports, power lines, land use, water, green, trees and terrain around the site, from OpenStreetMap and AWS Terrain Tiles'],   /* __acad3dV158: V157's kinds named */
    ['SITEANALYSIS',['SA','SITEAN','SITEPROCESS'],'siteanalysis','Site analysis, in the Analyze tab: Analyze site, the ten categories, the analyses drawn in the model and the findings with their sources'],   /* __acad3dV158; __acad3dV159 */
    ['ZONING',['ZONINGSUMMARY','ZONINGANALYSIS','ZONE'],'zoning','The site\'s zoning: district, uses, FAR, height, setbacks by side, steps and angular planes, coverage, parking (Site analysis)'],   /* __acad3dV160 */
    ['ENVELOPE',['ZONINGENVELOPE','BUILDABLEENVELOPE','ENV'],'envelope','Build the zoning envelope in 3D from the zoning record and the property, and flag massing outside it'],
    ['ZONINGBOARD',['YIELD','YIELDSTUDY','FEASIBILITY'],'zoningboard','The Zoning and yield board: the zoning analysis table, sections, the rules by side, the plan, floor plates, the yield'],
    ['CLIMATE',['CLIMATEBOARD','CLIMATEANALYSIS','WINDROSE','PSYCHROMETRIC','DEGREEDAYS','SEISMIC','AIRQUALITY'],'climate','The Climate and risk board: temperature, rain, hourly heat map, wind rose, sun path, degree days, solar, psychrometric comfort, air quality, earthquakes'],
    ['ACCESS',['ACCESSBOARD','PEOPLEBOARD','WALKABILITY','DEMOGRAPHICS'],'access','The Access and people board: the walk-time map, daily needs, transit, the street hierarchy and frontage, connectivity, and the census tract against its county and state'],   /* __acad3dV161 */
    ['ACCESSGET',['GETACCESS','CENSUSGET','WALKABILITYDATA'],'accessget','Get walk times to daily needs and transit, the streets the lot fronts, connectivity, and the census tract\'s people, from OpenStreetMap and the US Census (free, no key)'],   /* __acad3dV161 */
    ['WALKTIMES',['WALKSHED','ISOCHRONES','SERVICEAREA'],'walktimes','Draw the walk times (5, 10 and 15 minutes along the streets from the lot) on the plan, as a layer under Analysis'],
    ['CLIMATEGET',['GETCLIMATE','WEATHERDATA','CLIMATEDATA'],'climateget','Get the site\'s climate (ten years of ERA5), air quality (PM2.5) and earthquakes within 100 km, from free open sources'],   /* __acad3dV159 */
    ['ANALYZESITE',['SITEANALYZE','RUNSITEANALYSIS','SAFILL','SITEANALYSISFILL','SAFROMMODEL'],'analyzesite','Analyze site: get what is around the site from free open data and draw each analysis in the model -- compass, sun paths, shadows, winds, views, noise, contours, slope, aspect, water flow, ponds, flood zones, street hierarchy, cycling stress, transit, walk times, daily needs, vehicle access -- on Layers, Site analysis; one undo step'],   /* __acad3dV164; __acad3dV165; __acad3dV166 */
    ['CONTEXTREMOVE',['CONTEXTCLEAR'],'contextremove','Remove the site context'],
    /* __acad3dV139: LOD and CityJSON */
    ['LODCHECK',['CHECKSOLIDS','VALIDATESOLIDS','VAL3DITY'],'lodcheck','Check every building: its LOD, and whether it is a valid solid (closed, outward, flat faces, one piece)'],
    ['CITYJSONOUT',['EXPORTCITYJSON','CITYJSON'],'cityjsonout','Export the buildings as CityJSON 2.0, in the site\'s UTM zone'],
    ['CITYJSONIN',['IMPORTCITYJSON'],'cityjsonin','Import a CityJSON file\'s buildings, placed by their UTM coordinates'],
    ['SKPIN',['IMPORTSKP','SKETCHUP'],'skpin','Open a SketchUp file: its faces as solids, its tags as layers, its components as blocks'],   /* __acad3dV163 */
    /* __acad3dV134: data layers */
    ['FINDDATA',['OPENDATA','PORTAL'],'finddata','Find open data: search a US city, county, state or federal portal and add what it holds as a data layer'],   /* __acad3dV135 */
    ['DATALAYERS',['DATA','PARCELS','ZONING','FLOOD'],'datalayers','Parcels, zoning, flood zones: ArcGIS, WFS or GeoJSON data around the site, drawn on the plan and read by a click'],
    ['GEOEXPORT',['EXPORTGEOJSON'],'geoexport','Export the plan as GeoJSON, in longitude and latitude'],
    ['INSERT',['I','DDINSERT'],'blockinsert','Insert a block: drag it from the library onto the drawing'],
    ['ASSETS',['ADCENTER','CONTENT','TOOLPALETTES'],'assets','Open the Assets library of models, blocks and templates']
  ];
  /* __acad3dV86: a command runs through the BIM engine and reports whether it ran, so a command
     that did nothing cannot report success (V120: the engine is the only thing it can run on). */
  function runCadAct(act){
    if(!window.__a3dOn||!window.__a3dRunCmd){
      console.warn('[BIM] A command was asked for before the BIM workspace was on: '+act);
      return false;
    }
    try{ return !!window.__a3dRunCmd(act); }
    catch(e){ console.warn('[BIM] Palette command failed: '+act,e); return false; }
  }
  var REGISTRY=[];
  CADCMDS.forEach(function(c){ REGISTRY.push({name:c[0],aliases:c[1],desc:c[3],cad:c[2]}); });

  /* __acad3dV128: the command search. The engine owns the catalogue (every command and every ribbon
     tool, window.__a3dCommandSearch) and runs an entry (window.__a3dCommandRun); this draws it. */
  window.__wsRegistry=REGISTRY;
  function buildPalette(){
    var pal=document.createElement('div'); pal.id='a3d-cmdpal';
    pal.setAttribute('role','dialog'); pal.setAttribute('aria-label','Command search');
    pal.innerHTML='<div class="a3d-cmdinput"><span aria-hidden="true">&gt;_</span><input placeholder="Search commands, tools and shortcuts \u2014 or type a command: L, WA, TRIM" aria-label="Search commands, tools and shortcuts" role="combobox" aria-expanded="true" aria-controls="a3d-cmdlist" aria-autocomplete="list" autocomplete="off" spellcheck="false"></div>'+
      '<div class="a3d-cmdresults" id="a3d-cmdlist" role="listbox" aria-label="Commands"></div>'+
      '<div class="a3d-cmdfoot"><span><kbd>\u2191</kbd><kbd>\u2193</kbd> or <kbd>Tab</kbd> choose</span><span><kbd>Enter</kbd> run</span>'+
      '<span><kbd>?</kbd> keyboard shortcuts</span><span><kbd>Esc</kbd> close</span><span class="a3d-cmdcount"></span></div>';
    document.body.appendChild(pal);
    var input=pal.querySelector('input'), results=pal.querySelector('.a3d-cmdresults'), count=pal.querySelector('.a3d-cmdcount');
    var rows=[], active=0;
    function escH(s){return String(s==null?'':s).replace(/[&<>"]/g,function(ch){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch];});}
    function nameHtml(c){
      var n=c.name,on={},h='',i;
      if(!c.hl||!c.hl.length)return escH(n);
      for(i=0;i<c.hl.length;i++)on[c.hl[i]]=1;
      for(i=0;i<n.length;i++)h+=on[i]?'<b class="a3d-cmdhl">'+escH(n.charAt(i))+'</b>':escH(n.charAt(i));
      return h;
    }
    function kbdHtml(k,alt){
      return (k&&k.length)?'<span class="a3d-cmdkbd">'+k.map(function(x){return '<kbd>'+escH(x)+'</kbd>';}).join(alt?'<i>/</i>':'<i>+</i>')+'</span>':'';
    }
    function rowHtml(c,i){
      var meta='';
      if(c.off)meta+='<span class="a3d-cmdoff">'+escH(c.off)+'</span>';
      else if(c.where&&c.where.length)meta+='<span class="a3d-cmdwhere" title="On the ribbon: '+escH(c.where.join('; '))+'">'+escH(c.where[0])+(c.where.length>1?' +'+(c.where.length-1):'')+'</span>';
      if(c.aliases&&c.aliases.length)meta+='<span class="a3d-cmdkey" title="Also typed as '+escH(c.aliases.join(', '))+'">'+escH(c.aliases[0])+'</span>';
      meta+=kbdHtml(c.keys);
      return '<div class="a3d-cmdrow'+(c.off?' a3d-cmdrowoff':'')+'" role="option" id="a3d-cmdopt-'+i+'" aria-selected="false" data-idx="'+i+'">'+
        '<span class="a3d-cmdmain"><span class="a3d-cmdname">'+nameHtml(c)+'</span><span class="a3d-cmddesc"> \u2014 '+escH(c.desc)+'</span></span>'+
        '<span class="a3d-cmdmeta">'+meta+'</span></div>';
    }
    /* ? -- the keyboard shortcuts, searched by what they do or by the key itself */
    function keyRows(q){
      var g=window.__a3dShortcuts?window.__a3dShortcuts():[],out=[],norm=function(s){return String(s).toLowerCase().replace(/cmd|ctrl|control|meta|\u2318/g,'mod');};
      var words=norm(q).split(/\s+/).filter(function(w){return !!w;});
      g.forEach(function(grp){grp.rows.forEach(function(r){
        var hay=norm(r.keys.join(' ')+' '+r.keys.join('+')+' '+r.label+' '+grp.grp);
        if(words.every(function(w){return hay.indexOf(w)>=0;}))out.push({kind:'key',keys:r.keys,alt:!!r.alt,desc:r.label,grp:grp.grp,cmd:r.cmd||null});
      });});
      return out;
    }
    function keyRowHtml(c,i){
      return '<div class="a3d-cmdrow a3d-cmdkeyrow" role="option" id="a3d-cmdopt-'+i+'" aria-selected="false" data-idx="'+i+'">'+
        '<span class="a3d-cmdmain"><span class="a3d-cmdname">'+kbdHtml(c.keys,c.alt)+'</span><span class="a3d-cmddesc"> \u2014 '+escH(c.desc)+'</span></span>'+
        '<span class="a3d-cmdmeta"><span class="a3d-cmdwhere">'+escH(c.grp)+'</span>'+(c.cmd?'<span class="a3d-cmdkey">'+escH(c.cmd)+'</span>':'')+'</span></div>';
    }
    function draw(){
      var q=input.value.trim(),h='',i;
      if(q.charAt(0)==='?'){
        rows=keyRows(q.slice(1).trim());
        if(rows.length)h+='<div class="a3d-cmdhd">Keyboard shortcuts</div>';
        for(i=0;i<rows.length;i++)h+=keyRowHtml(rows[i],i);
        count.textContent=rows.length+' shortcut'+(rows.length===1?'':'s');
        if(!rows.length)h='<div class="a3d-cmdrow a3d-cmdnone">No matching shortcut</div>';
      }else{
        var res=window.__a3dCommandSearch?window.__a3dCommandSearch(q,q?80:0):[];
        var rec=(!q&&window.__a3dCommandRecent)?window.__a3dCommandRecent(5):[],seen={},typoAt=-1;
        rec.forEach(function(c){seen[c.id]=1;});
        var rest=res.filter(function(c){return !seen[c.id];});
        rows=rec.concat(rest);
        for(i=0;i<rows.length;i++){
          if(i===0&&rec.length)h+='<div class="a3d-cmdhd">Recently used</div>';
          if(i===rec.length&&rec.length)h+='<div class="a3d-cmdhd">All commands</div>';
          if(rows[i].typo&&typoAt<0){typoAt=i;h+='<div class="a3d-cmdhd">Did you mean</div>';}
          h+=rowHtml(rows[i],i);
        }
        count.textContent=q?(res.length+' match'+(res.length===1?'':'es')):(res.length+' commands');
        if(!rows.length)h='<div class="a3d-cmdrow a3d-cmdnone">No matching command \u2014 try fewer letters, or ? for the keyboard shortcuts</div>';
      }
      results.innerHTML=h;
      active=0;
      highlight();
    }
    function highlight(){
      var els=results.querySelectorAll('.a3d-cmdrow[data-idx]'),i,cur=null;
      for(i=0;i<els.length;i++){
        var on=(+els[i].getAttribute('data-idx')===active);
        els[i].classList.toggle('active',on);els[i].setAttribute('aria-selected',on?'true':'false');
        if(on)cur=els[i];
      }
      if(cur){input.setAttribute('aria-activedescendant',cur.id);try{cur.scrollIntoView({block:'nearest'});}catch(eS){}}
      else input.removeAttribute('aria-activedescendant');
    }
    /* __acad3dV86: hand the keyboard back to the drawing.

       The BIM key chain begins "if the event target is an INPUT, return", so leaving focus in
       the palette's hidden input meant every keystroke AFTER a command was swallowed: the tool
       started, and then typing a coordinate, pressing C to close or pressing Escape to cancel
       all did nothing at all. Measured: activeElement was INPUT and the typing buffer stayed
       empty. A command line that keeps the keyboard after it runs is not a command line. */
    function closePal(){
      pal.classList.remove('show');
      try{input.blur();}catch(eB){}
      try{if(document.activeElement===input)document.body.focus();}catch(eF){}
    }
    function runIdx(i){
      var c=rows[i]; if(!c) return;
      closePal();
      if(c.kind==='key'){
        if(c.cmd&&window.__a3dCommandRun){if(!window.__a3dCommandRun('cmd:'+c.cmd)&&window.__a3dToast)window.__a3dToast(c.cmd+' is not available here');}
        else if(window.__a3dToast)window.__a3dToast('Press '+c.keys.join(c.alt?' or ':'+')+' on the drawing: '+c.desc);
        return;
      }
      /* A command that cannot run says so, instead of closing the palette over nothing. */
      var ok=window.__a3dCommandRun?window.__a3dCommandRun(c.id):runCadAct(c.cad);
      if(!ok&&window.__a3dToast)window.__a3dToast(c.name+' is not available here'+(c.off?': '+c.off:''));   /* __acad3dV120 */
    }
    input.addEventListener('input',draw);
    input.addEventListener('keydown',function(e){
      var n=rows.length;
      if(e.key==='ArrowDown'){active=Math.min(n-1,active+1);highlight();e.preventDefault();}
      else if(e.key==='ArrowUp'){active=Math.max(0,active-1);highlight();e.preventDefault();}
      else if(e.key==='Tab'){if(n){active=(active+(e.shiftKey?n-1:1))%n;highlight();}e.preventDefault();}   /* AutoCAD: Tab cycles */
      else if(e.key==='Enter'){runIdx(active);e.preventDefault();e.stopPropagation();}
      else if(e.key==='F1'){   /* __acad3dV142: the highlighted command's page in the guide */
        var hc=rows[active];e.preventDefault();e.stopPropagation();
        if(hc&&hc.kind!=='key'&&window.__a3dDocsOpen){closePal();window.__a3dDocsOpen('commands.html',hc.id);}
        else if(window.__a3dDocsOpen){closePal();window.__a3dDocsOpen('index.html');}
      }
      else if(e.key==='Escape'){closePal();}
    });
    results.addEventListener('pointerdown',function(e){
      var row=e.target.closest('.a3d-cmdrow'); if(!row||row.dataset.idx===undefined) return;
      e.preventDefault(); e.stopPropagation();
      runIdx(+row.dataset.idx);
    });
    draw();
    /* __acad3dV113: Ctrl+K opens the palette; Escape, or a pointer outside it, closes it.
       window.openPalette and window.closePalette are what the suites drive. */
    function openPal(initial){
      pal.classList.add('show');
      input.value=(typeof initial==='string')?initial:'';
      draw();
      /* the caret goes in at once, so the letters typed after the first land in the search too */
      try{input.focus();input.setSelectionRange(input.value.length,input.value.length);}catch(eO){}
      setTimeout(function(){try{if(pal.classList.contains('show')&&document.activeElement!==input)input.focus();}catch(eO2){}},20);
    }
    window.openPalette=openPal;
    window.closePalette=closePal;
    document.addEventListener('keydown',function(e){
      if((e.metaKey||e.ctrlKey)&&e.key&&e.key.toLowerCase()==='k'){e.preventDefault();openPal();return;}
      if(e.key==='Escape'&&pal.classList.contains('show')){closePal();return;}
      /* __acad3dV128: AutoCAD's command line takes a letter typed on the drawing. The engine's
         key chain has already run (window, capture) and has not claimed the key; the engine says
         whether anything else is listening for it -- a tool, a dialog, a held face -- and only
         when nothing is does the letter open the search. */
      if(!pal.classList.contains('show')&&!e.defaultPrevented&&!e.isComposing&&window.__a3dTypeAnywhere&&window.__a3dTypeAnywhere(e)){
        /* __acad3dV129: ? is the keyboard shortcuts panel (Linear's and GitHub's key) */
        if(e.key==='?'&&window.__a3dRunCmd){e.preventDefault();window.__a3dRunCmd('shortcuts');return;}
        e.preventDefault();openPal(e.key);
      }
    });
    document.addEventListener('pointerdown',function(e){
      if(!pal.classList.contains('show'))return;
      if(!e.target.closest('#a3d-cmdpal'))closePal();
    },true);
    window.__wsPaletteCount=REGISTRY.length;
    window.__wsPaletteOwner='acadWorkspaceV1';
  }
  buildPalette();

  // ============ PROJECT TABS + START SCREEN ============
  /* __acad3dV115: AutoCAD's file tabs. Start, then one tab per open project, then +. Each project
     tab is its own model with its own undo history; x closes it, and a closed project waits on the
     Start page until it is opened again or deleted there. The list belongs to the BIM engine
     (window.__a3dDocs); this section only draws it and passes clicks on. */
  function docsApi(){ return window.__a3dDocs||null; }
  function escHtml(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function startShown(){ var s=document.getElementById('acad-start'); return !!(s&&s.classList.contains('show')); }
  function docCount(n){ return n+' object'+(n===1?'':'s'); }
  function docWhen(ms){
    if(!ms) return '';
    try{ return new Date(ms).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'}); }
    catch(eW){ return ''; }
  }
  var lastTabHtml='';
  function renderDocTabs(){
    var dt=document.getElementById('acad-doctabs'); if(!dt) return;
    var api=docsApi(), list=api?api.list():[], open=api?api.open():[], act=api?api.active():null, byId={}, i, d;
    for(i=0;i<list.length;i++) byId[list[i].id]=list[i];
    var onStart=startShown()||!act;
    var html='<button class="acad-doctab'+(onStart?' active':'')+'" data-dt="start">Start</button>';
    for(i=0;i<open.length;i++){
      d=byId[open[i]]; if(!d) continue;
      html+='<button class="acad-doctab dt-doc'+(!onStart&&d.id===act?' active':'')+'" data-dt="doc" data-doc="'+escHtml(d.id)+'" title="'+escHtml(d.name)+' \u2014 '+docCount(d.objs)+'">'+
        '<span class="dt-name">'+escHtml(d.name)+'</span>'+
        '<span class="dt-x" data-dtx="'+escHtml(d.id)+'" title="Close '+escHtml(d.name)+'">\u00d7</span></button>';
    }
    html+='<button class="acad-doctab acad-plus" data-dt="new" title="New project">+</button>';
    if(html!==lastTabHtml){ dt.innerHTML=html; lastTabHtml=html; }
  }
  function buildStart(){
    var s=document.getElementById('acad-start');
    if(!s){ s=document.createElement('div'); s.id='acad-start'; document.body.appendChild(s); }
    var api=docsApi(), list=api?api.list():[], open=api?api.open():[], ordered=[], cards='', i, j, d, meta;
    /* the open projects in tab order, then the closed ones, most recently used first */
    for(i=0;i<open.length;i++) for(j=0;j<list.length;j++) if(list[j].id===open[i]) ordered.push(list[j]);
    list.filter(function(x){ return !x.open; })
        .sort(function(a,b){ return ((b.loaded?1:0)-(a.loaded?1:0))||(b.saved-a.saved); })
        .forEach(function(x){ ordered.push(x); });
    for(i=0;i<ordered.length;i++){
      d=ordered[i];
      meta=docCount(d.objs)+' \u00b7 '+(d.open?'open':(d.loaded?'last open':(docWhen(d.saved)?'closed '+docWhen(d.saved):'closed')));
      var del=!d.open&&!d.loaded;
      cards+='<div class="st-card'+(del?' st-has-del':'')+'" data-st="doc" data-doc="'+escHtml(d.id)+'">'+
        '<div class="st-name">'+escHtml(d.name)+'</div><div class="st-meta">'+meta+'</div>'+
        (del?'<button class="st-del" data-st="del" data-doc="'+escHtml(d.id)+'" title="Delete '+escHtml(d.name)+' from this browser">Delete</button>':'')+
        '</div>';
    }
    s.innerHTML='<div class="st-wrap"><h1>Start</h1>'+
      '<div class="st-sub">CAD/BIM workspace \u2014 drafting, modelling and documentation</div>'+
      '<div class="st-cols"><div class="st-left">'+
      '<button data-st="new">New project</button>'+
      '<button class="st-sec" data-st="open">Open project file\u2026</button>'+
      '</div><div class="st-right"><div class="st-sect">Projects</div><div class="st-grid">'+
      (cards||'<div class="st-empty">No projects yet</div>')+
      '</div></div></div></div>';
  }
  function showStart(){ buildStart(); document.getElementById('acad-start').classList.add('show'); document.body.classList.add('acad-startpage'); renderDocTabs(); }
  function hideStart(){
    var api=docsApi();
    if(api&&!api.active()){ showStart(); return; }   /* with no project open, Start is all there is */
    var s=document.getElementById('acad-start'); if(s) s.classList.remove('show');
    document.body.classList.remove('acad-startpage');
    renderDocTabs();
  }
  function docAct(fn,arg){
    var api=docsApi();
    if(!api){
      console.warn('[BIM] The project list is not ready yet');
      if(window.__a3dToast)window.__a3dToast('The workspace is still loading; try again in a moment');   /* __acad3dV120 */
      return false;
    }
    try{ return api[fn](arg); }
    catch(eD){
      console.warn('[BIM] Project '+fn+' failed',eD);
      if(window.__a3dToast)window.__a3dToast('That did not work: '+(eD&&eD.message?eD.message:eD));   /* __acad3dV120 */
      return false;
    }
  }
  /* the engine says what changed; opening a project takes the Start page away, and losing the last
     open one brings it back */
  window.addEventListener('a3ddocs',function(e){
    var k=e&&e.detail?e.detail.kind:'';
    if(k==='activate'||k==='create'||k==='open') hideStart();
    else if(startShown()) buildStart();
    var api=docsApi();
    if(api&&!api.active()) showStart();
    renderDocTabs();
  });
  document.addEventListener('click',function(e){
    var x=e.target.closest&&e.target.closest('#acad-doctabs [data-dtx]');
    if(x){
      e.preventDefault(); e.stopPropagation();
      var was=startShown();
      docAct('close',x.getAttribute('data-dtx'));
      if(was) showStart();
      return;
    }
    var t=e.target.closest&&e.target.closest('#acad-doctabs [data-dt]');
    if(t){
      var k=t.getAttribute('data-dt');
      if(k==='start') showStart();
      else if(k==='new') docAct('create');
      else if(docAct('activate',t.getAttribute('data-doc'))) hideStart();
      return;
    }
    var st=e.target.closest&&e.target.closest('#acad-start [data-st]');
    if(!st) return;
    var a=st.getAttribute('data-st'), id=st.getAttribute('data-doc');
    if(a==='new') docAct('create');
    else if(a==='open'){
      if(!window.__a3dRunCmd||!window.__a3dRunCmd('openJson')){
        console.warn('[BIM] The project file picker could not be opened');
        if(window.__a3dToast)window.__a3dToast('The workspace is still loading; try Open again in a moment');   /* __acad3dV120 */
      }
    }
    else if(a==='del'){
      var card=st.closest('.st-card'), nmEl=card?card.querySelector('.st-name'):null;
      var nm=nmEl?nmEl.textContent:'this project';
      if(window.confirm('Delete "'+nm+'" from this browser? This cannot be undone.')) docAct('remove',id);
    }
    else if(a==='doc'&&docAct('activate',id)) hideStart();
  });
  /* The tab carries the project's name, which is edited elsewhere (Properties, the title block).
     A one-second look is cheap and cannot miss an edit path; the DOM is only touched when a label
     actually changed. */
  var dtBoot=0;
  (function bootTabs(){
    if(document.getElementById('acad-doctabs')&&docsApi()){
      renderDocTabs();
      if(!docsApi().active()) showStart();
      setInterval(renderDocTabs,1000);
      return;
    }
    if(++dtBoot<60) setTimeout(bootTabs,250);
    else console.warn('[BIM] The document tabs never found the project list');
  })();
  }catch(err){
    window.__wsErr=String(err&&err.stack||err);
    console.warn('[BIM] The command palette and the project tabs could not be set up.',err);   /* __acad3dV120 */
    setTimeout(function(){if(window.__a3dToast)window.__a3dToast('The command palette could not be set up; reload the page');},1500);
  }
})();

(function acadBoot(){
  /* __acad3dV120: the boot into the BIM workspace. The engine publishes window.__a3dEnter when it
     has loaded; this waits for it, for about three seconds at most, then opens the plan view. */
  function boot(tries){
    if(typeof window.__a3dEnter!=='function'){
      if(tries>0)setTimeout(function(){boot(tries-1);},120);
      else{
        console.warn('[BIM] The BIM workspace did not load; reload the page to try again.');
        document.body.insertAdjacentHTML('beforeend','<div style="position:fixed;left:50%;top:40%;transform:translateX(-50%);padding:14px 18px;background:#2a2f35;color:#e6eef6;border:1px solid #c0504d;border-radius:6px;font:13px sans-serif;z-index:99999">The workspace did not load. Reload the page to try again.</div>');
      }
      return;
    }
    try{
      window.ACAD_WS_CUR='da';
      window.__a3dEnter();
      if(window.__a3dSetPlanView)window.__a3dSetPlanView();
    }catch(eB){
      console.warn('[BIM] Startup entry into the drafting workspace failed.',eB);
      if(window.__a3dToast)window.__a3dToast('The workspace could not start; reload the page');
    }
  }
  setTimeout(function(){boot(25);},60);
})();
