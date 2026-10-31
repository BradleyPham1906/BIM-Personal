  /* ================= __acad3dV128: one catalogue of every command ================= */
  /* A ribbon action that IS a typed command: one entry, the command's, with the ribbon place added */
  var BIM_ACT_CMD={'bim:wall':'wall','s:poly':'poly','s:rect':'rect','s:circle':'circle','bim:arc':'arc','bim:floor':'floorTool',
    'bim:room':'room','bim:tagroom':'roomtag','bim:tagallrooms':'roomtagall','bim:footing':'footing','bim:foundwall':'wallfoundation',
    'bim:foundslab':'foundslab','bim:property':'propertyline','bim:propshape':'propertyshape','bim:truenorth':'truenorth',
    'bim:alignment':'alignment','bim:usage':'usage','bim:usages':'usages','bim:map':'map','bim:findaddress':'findaddress',
    'bim:geoimport':'geoimport','bim:context':'context','bim:datalayers':'datalayers','m:exportgeojson':'geoexport','bim:roof':'roofTool','bim:stair':'stairTool','bim:dim':'bimDims','bim:text':'text',
    'bim:section':'sectionTool','bim:ceiling':'ceilingTool','bim:offset':'offset','bim:trim':'trim','bim:align':'align',
    'bim:leader':'leader','bim:beam':'beamTool','bim:analyze':'analyze','bim:grid':'gridline','bim:column':'columnTool',
    'bim:door':'doorTool','bim:window':'windowTool','v:fit':'zoomFit','m:del':'del','m:dup':'duplicate','m:array':'arrayRect',
    'm:saveproj':'saveJson','m:openproj':'openJson','bim:mirror':'mirror','bim:rotate':'rotate','bim:polararray':'arrayPolar',
    'bim:mergewalls':'join','bim:extend':'extend','bim:fillet':'fillet','bim:chamfer':'chamfer','bim:lengthen':'lengthen',
    'bim:scale':'scale','bim:presspull':'presspull','m:desel':'selNone','bim:layers':'layers','bim:sheet':'newSheet'};
  /* ribbon actions left out of the search: each only says to use the Project Browser */
  var BIM_ACT_HIDE={'bim:levels':1};
  /* a ribbon-only tool's name, where its label alone would be ambiguous or not a command's name */
  var BIM_ACT_NAMES={'v:top':'VIEWTOP','v:front':'VIEWFRONT','v:right':'VIEWRIGHT','v:iso':'VIEW3D','v:home':'VIEWHOME',
    'm:exportpng':'EXPORTPNG','m:exportpdf':'EXPORTPDF','m:exportdxf':'EXPORTDXF','m:exportsvg':'EXPORTSVG',
    'm:exitsection':'SECTIONEXIT','m:flipsection':'SECTIONFLIP','b:union':'UNION','b:cut':'SUBTRACT','b:isect':'INTERSECT',
    'bim:dimang':'DIMANGULAR','bim:dimrad':'DIMRADIUS','bim:dimdia':'DIMDIAMETER','bim:famimport':'FAMILYLOAD',
    'bim:famsave':'FAMILYSAVE','bim:component':'COMPONENT','bim:level':'LEVEL','bim:saveview':'SAVEVIEW',
    'bim:uipanels':'USERINTERFACE','bim:classification':'CLASSIFY','bim:checkmodel':'CHECKMODEL','bim:importcad':'IMPORTCAD',
    'bim:linkifc':'LINKIFC','bim:joinwalls':'JOINWALLS','bim:clonelinked':'CLONELINKED','bim:syncclones':'SYNCCLONES',
    'bim:titleblock':'TITLEBLOCK','bim:break':'BREAK',
    /* the sketch constraints by AutoCAD's names: GC geometric, DC dimensional */
    'con:coincident':'GCCOINCIDENT','con:horizontal':'GCHORIZONTAL','con:vertical':'GCVERTICAL','con:parallel':'GCPARALLEL',
    'con:perpendicular':'GCPERPENDICULAR','con:equal':'GCEQUAL','con:pointonline':'GCPOINTONLINE','con:midpoint':'GCMIDPOINT',
    'con:symmetric_pt':'GCSYMMETRICPOINT','con:symmetric_line':'GCSYMMETRICLINE','con:distance':'DCDISTANCE','con:angle':'DCANGLE'};
  /* what a ribbon-only tool does, where its button's label alone does not say */
  var BIM_ACT_DESC={'bim:joinwalls':'Join two walls at their corner','bim:component':'Place a model from the library',
    'bim:famsave':'Save the selection to the library as a model','bim:famimport':'Load an OBJ or STL model into the library',
    'bim:level':'Add a level','v:top':'Look at the model from above','v:front':'Look at the model from the front',
    'v:right':'Look at the model from the right','v:iso':'The default 3D view','v:home':'The home 3D view',
    'con:coincident':'Make two sketch points meet','con:horizontal':'Make a sketch line horizontal','con:vertical':'Make a sketch line vertical',
    'con:parallel':'Make two sketch lines parallel','con:perpendicular':'Make two sketch lines perpendicular',
    'con:equal':'Make two sketch lines the same length','con:distance':'Fix the distance between two sketch points',
    'con:angle':'Fix the angle between two sketch lines','con:pointonline':'Keep a sketch point on a line',
    'con:midpoint':'Keep a sketch point at the middle of a line','con:symmetric_pt':'Make two sketch points symmetric about a point',
    'con:symmetric_line':'Make two sketch points symmetric about a line','bim:dimang':'Angular dimension',
    'bim:dimrad':'Radius dimension','bim:dimdia':'Diameter dimension','bim:saveview':'Save the current view to the Project Browser',
    'bim:linkifc':'Link an IFC file','bim:importcad':'Import a CAD file','m:exitsection':'Leave the section view',
    'm:flipsection':'Look at the section from the other side','bim:titleblock':'Edit the title block the sheets share',
    'bim:uipanels':'Show or hide the interface panels','bim:clonelinked':'Make a linked clone of the selection',
    'bim:syncclones':'Update the linked clones from their source','b:union':'Join the selected solids into one',
    'b:cut':'Cut one solid out of another','b:isect':'Keep only where the selected solids overlap',
    'p:pad':'Extrude the selected sketch into a solid','p:pocket':'Cut the selected sketch into a solid',
    'box':'Place a box','cyl':'Place a cylinder','sphere':'Place a sphere','cone':'Place a cone','torus':'Place a torus',
    'tube':'Place a tube','prism':'Place a prism','wedge':'Place a wedge','ellipsoid':'Place an ellipsoid',
    'bim:classification':'Manage the classification systems','bim:checkmodel':'Check the model for problems',
    'm:exportpng':'Export the view as a PNG image','m:exportpdf':'Export the plan as a PDF',
    'm:exportdxf':'Export the drawing as a DXF file','m:exportsvg':'Export the drawing as an SVG file'};
  /* AutoCAD's synonyms: the words a person might search for a command by, beyond its name */
  var BIM_CMD_TERMS={SITETOOLS:'geoprocessing pane history arcgis analysis tools runs',BUFFER:'around within distance zone setback dissolve',   /* __acad3dV172 */
    DISTANCEFROM:'euclidean straight line nearest proximity',SLOPECLASSES:'reclassify steep gentle gradient',EXCLUSIONS:'restricted constraints mask nodata',
    SUITABILITY:'weighted overlay criteria transform weight multicriteria siting',LOCATE:'regions best site footprint where to build',
    CONSTRAINTSMAP:'constraints opportunities synthesis site analysis plan',BUILDABLE:'site capacity net buildable resource protection density impervious acres',
    SITEWORKSPACE:'analyses focus legend key workspace archimap forma diagram',TRAFFIC:'cars pedestrians walkers simulation signals queue junction delay',FILLET:'round rounded corner radius',CHAMFER:'bevel corner',ERASE:'delete remove',COPY:'duplicate clone',
    OFFSET:'parallel',TRIM:'cut clip shorten',EXTEND:'stretch longer',MIRROR:'flip reflect',ARRAYRECT:'grid pattern repeat rows columns',
    ARRAYPOLAR:'circular radial repeat',DIST:'distance length measure',DIMLINEAR:'dimension measure',MTEXT:'label note annotation words',
    TEXT:'label note annotation words',HATCH:'fill pattern poche',LAYER:'layers visibility',ZOOM:'fit extents all',UNDO:'back revert',
    REDO:'again forward',ROTATE:'turn spin angle',SCALE:'resize size bigger smaller',PLOT:'print pdf paper',SAVE:'export file download',
    OPEN:'load file import project',NEW:'project file blank',RECTANG:'box square',CIRCLE:'round',PLINE:'polyline path lines',
    LINE:'segment',SELECTALL:'everything select',CLEAR:'deselect none',ANALYZE:'structural frame solve stiffness forces moments deflection',
    USAGE:'program use department gross floor area gfa gba nsa net saleable lettable yield efficiency residential office retail',   /* __acad3dV131 */
    USAGES:'program library gross net area ratios efficiency formulas parameters units',
    MAP:'basemap satellite imagery aerial photo street openstreetmap osm tiles background giraffe',   /* __acad3dV132 */
    FINDADDRESS:'geocode location search place latitude longitude site where nominatim',
    GEOIMPORT:'geojson kml gis parcels lots boundaries import site data google earth',
    GEOEXPORT:'geojson gis export longitude latitude',
    ZONING:'zoning zone district regulation regulations planning code far fsr floor area ratio floor space ratio height limit setbacks stepback coverage permitted uses legal',   /* __acad3dV160 */
    ENVELOPE:'zoning envelope buildable volume massing setback stepback sky exposure plane daylight plane angular plane height limit 3d',
    ZONINGBOARD:'yield feasibility zoning analysis table gfa gross floor area units parking capacity envelope section board',
    CLIMATE:'climate weather temperature rain rainfall precipitation wind rose sun path degree days heating cooling solar radiation humidity psychrometric comfort koppen air quality pollution pm2.5 earthquake seismic risk board dashboard charts',   /* __acad3dV159 */
    CLIMATEGET:'climate weather data temperature rain wind air quality earthquake fetch download era5 open-meteo usgs',
    ACCESS:'access people board walk times walkability daily needs 15-minute city amenities transit lines stops street hierarchy frontage intersection density connectivity demographics census age pyramid income households commute vehicles',   /* __acad3dV161 */
    ACCESSGET:'access walk walking walkability transit bus stop train station subway metro tram ferry streets frontage census demographics population acs openstreetmap overpass fetch get data',   /* __acad3dV161 */
    WALKTIMES:'walk times walk shed walkshed isochrone isochrones service area network 5 10 15 minutes pedestrian catchment layer plan',
    CONTEXT:'neighbours neighbors surrounding buildings osm openstreetmap overpass roads streets water rivers parks trees terrain elevation contours ground giraffe railway railways train tram subway bridges tunnels airport runway power pylons land use infrastructure',   /* __acad3dV133; __acad3dV157 */
    CONTEXTREMOVE:'delete clear neighbours context',
    ANALYZESITE:'site analysis analyze run one click diagrams sun path shadows wind rose views isovist noise compass distance rings layers climate context fill findings contours slope aspect terrain ground drainage flow catchment watershed ponds flood floodplain fema street hierarchy streets roads cycling bicycle bike stress lts transit bus rail ptal walk walking times daily needs vehicle access driveway entry parking car park',   /* __acad3dV164; __acad3dV165; __acad3dV166 */
    DOCS:'help documentation manual guide tutorial learn how reference f1',   /* __acad3dV142 */
    SUNHOURS:'sun hours sunlight shadow study daylight right to light overshadowing simulation',   /* __acad3dV143 */
    SOLAR:'solar radiation irradiance energy photovoltaic pv roof potential kwh sun simulation',
    RAINFLOW:'rain water flow runoff drainage ponding flooding watershed terrain simulation',
    SIMCLEAR:'clear simulation remove results',
    RELEASENOTES:'version changelog release notes history what is new updates',
    ANALYSES:'analysis analyses analyze dashboard results checks studies simulation sun shadow structure areas survey',   /* __acad3dV141 */
    LODCHECK:'lod level of detail validate valid solid closed watertight val3dity buildings check citygml',   /* __acad3dV139 */
    CITYJSONOUT:'cityjson citygml 3d city model export buildings lod utm 3dbag',
    CITYJSONIN:'cityjson citygml 3d city model import buildings lod 3dbag',
    SKPIN:'sketchup skp trimble import open model components groups tags materials 3d warehouse',   /* __acad3dV163 */
    BREAKLINE:'breakline terrain tin ridge ditch kerb curb edge constraint surface',   /* __acad3dV144 */
    GRADE:'grading pad daylight slope cut fill embankment batter earthwork proposed surface site',   /* __acad3dV145 */
    COMMIT:'commit version save checkpoint snapshot git history revision',   /* __acad3dV146 */
    HISTORY:'history versions revisions changes log diff restore git timeline',
    CUTFILL:'cut fill volume earthwork quantities excavation embankment surface comparison tin',
    CUTFILLMAP:'cut fill map depth colour earthwork heat',
    SPOTELEV:'spot elevation height level label point grade',
    SLOPEARROWS:'slope arrows drainage direction fall flow percent grade',
    TERRAINBOUNDARY:'terrain tin surface boundary trim clip outer limit',
    SLOPEMAP:'slope analysis gradient grade percent steepness terrain bands',
    ELEVATIONMAP:'elevation height bands terrain hypsometric tint colour',
    ASPECTMAP:'aspect orientation facing direction north south terrain slope',
    TERRAINANALYSISOFF:'terrain analysis colour off clear',
    LANDXMLOUT:'landxml civil 3d export tin surface survey xml',
    LANDXMLIN:'landxml civil 3d import tin surface survey xml',
    DATALAYERS:'gis arcgis wfs geojson parcels lots zoning flood fema council open data layers attributes lookup',   /* __acad3dV134 */
    FINDDATA:'search catalog portal hub socrata city county state federal datasets browse discover',   /* __acad3dV135 */
    ANALYZEOFF:'hide analysis',LOAD:'force kn',SUPPORT:'fixed pinned boundary base',ALIGNMENT:'road route centerline centreline chainage highway',
    STATION:'chainage offset',PROFILEVIEW:'vertical profile grade',SURVEY:'terrain topography topo tin contours ground',SURVEYCHECK:'verify validate qa qc quality accuracy rmse bust blunder control benchmark check shots report',
    PROPERTYLINE:'parcel lot boundary site',GRIDLINE:'axis grid line',ROOM:'space area',SECTIONTOOL:'cut elevation',SECTION:'cut elevation',
    BLOCK:'group symbol save',INSERT:'place block',ASSETS:'library models blocks templates content',PRESSPULL:'extrude push pull face',
    SUNSTUDY:'sun shadow daylight',TRIBAREA:'tributary load area',AREAPLAN:'gross area',FOOTING:'foundation pad',WALLFOUNDATION:'strip footing',
    FOUNDATIONSLAB:'mat raft slab',COLUMN:'post pillar',BEAM:'girder joist',FLOOR:'slab deck',JOIN:'merge walls',OSNAP:'snap object',
    ORTHO:'orthogonal perpendicular',GRID:'snap grid',SHORTCUTS:'keyboard keys help hotkeys',LAYOUT:'sheet paper',PSPACE:'paper sheet',
    MSPACE:'model viewport',GIZMO:'transform move handles',BOUNDARY:'region outline',DIVIDE:'split equal points',MEASURE:'spacing points',
    ALIGN:'line up',BREAKATPOINT:'split',EXPORTPDF:'print save pdf',EXPORTPNG:'image picture screenshot',EXPORTDXF:'cad autocad',
    EXPORTSVG:'vector image',UNION:'boolean add merge combine',SUBTRACT:'boolean difference cut minus',INTERSECT:'boolean common',
    VIEW3D:'isometric iso 3d',VIEWTOP:'plan top',BOX:'cube block',CYLINDER:'tube pipe round',COMPONENT:'family furniture place',
    LEVEL:'storey story floor elevation',SAVEVIEW:'camera bookmark',ROOMTAG:'label tag room',ROOMCOLOR:'color fill scheme department',COLOURBY:'color colour lens legend scheme theme thematic height usage heatmap',
    WINDOW:'opening glazing',DOOR:'opening entrance',ROOF:'pitch slope',STAIR:'stairs steps',CEILING:'soffit'};
  var BIM_CMD_USE_KEY='acad3dCmdUsage';
  /* the chord each command answers to, from A3D_KEYS -- the shortcut sheet's own table */
  function bimCmdKeyMap(){
    var m={},g,r;
    for(g=0;g<A3D_KEYS.length;g++)for(r=0;r<A3D_KEYS[g].rows.length;r++){
      var row=A3D_KEYS[g].rows[r];
      if(row.cmd&&!m[row.cmd])m[row.cmd]=row.keys.slice();
    }
    return m;
  }
  function bimCmdCatalog(){
    var reg=window.__wsRegistry||[],keys=bimCmdKeyMap(),out=[],byCad={},byName={},i,c,it;
    for(i=0;i<reg.length;i++){
      c=reg[i];
      if(!BIM_CMD_MAP[c.cad])continue;   /* only commands that run (V86) */
      it={id:'cmd:'+c.name,name:c.name,aliases:c.aliases.slice(),desc:c.desc,cad:c.cad,act:null,where:[],
        keys:keys[c.name]||null,terms:BIM_CMD_TERMS[c.name]||''};
      out.push(it);(byCad[c.cad]=byCad[c.cad]||[]).push(it);byName[c.name]=it;
    }
    var all=a3drAllCommands();
    for(i=0;i<all.length;i++){
      var a=all[i].act,where=all[i].tab.name+' \u203a '+all[i].panel,cad=BIM_ACT_CMD[a],lbl,nm;
      if(BIM_ACT_HIDE[a]||a3drIsUnimpl(a))continue;
      lbl=a3drLabel(a);nm=BIM_ACT_NAMES[a]||String(lbl).toUpperCase().replace(/[^A-Z0-9]+/g,'');
      var same=(cad&&byCad[cad])||(byName[nm]?[byName[nm]]:null);
      if(same){same.forEach(function(x){if(x.where.indexOf(where)<0)x.where.push(where);if(!x.act)x.ribbon=a;});continue;}
      it={id:'act:'+a,name:nm,aliases:[],desc:BIM_ACT_DESC[a]||lbl,cad:null,act:a,where:[where],keys:null,terms:(BIM_CMD_TERMS[nm]||'')+' '+lbl};
      out.push(it);byName[nm]=it;
    }
    return out;
  }
  function bimCmdWords(s){return String(s||'').toLowerCase().split(/[^a-z0-9]+/).filter(function(w){return !!w;});}
  function bimKeyNorm(s){return String(s||'').toLowerCase().replace(/\s+/g,'').replace(/cmd|ctrl|control|meta|\u2318/g,'mod');}
  /* within one edit: a letter changed, added, dropped, or two swapped */
  function bimEditWithin1(a,b){
    if(a===b)return true;
    var la=a.length,lb=b.length,i=0;
    if(Math.abs(la-lb)>1)return false;
    while(i<la&&i<lb&&a.charAt(i)===b.charAt(i))i++;
    if(la===lb){
      if(a.slice(i+1)===b.slice(i+1))return true;
      return i+1<la&&a.charAt(i)===b.charAt(i+1)&&a.charAt(i+1)===b.charAt(i)&&a.slice(i+2)===b.slice(i+2);
    }
    return la>lb?a.slice(i+1)===b.slice(i):a.slice(i)===b.slice(i+1);
  }
  /* the letters of t, in order, in s: their positions, or null */
  function bimSubseq(s,t){
    var out=[],j=0,i;
    for(i=0;i<s.length&&j<t.length;i++)if(s.charAt(i)===t.charAt(j)){out.push(i);j++;}
    return j===t.length?out:null;
  }
  function bimRange(a,n){var o=[],i;for(i=0;i<n;i++)o.push(a+i);return o;}
  /* How well one typed word matches an entry: a tier (lower is better) and, when it matched the
     name, which letters of the name matched. -1: no match. */
  function bimCmdTier(it,t){
    var nm=it.name.toLowerCase(),i,k;
    if(nm===t)return {tier:0,hl:bimRange(0,nm.length)};
    for(i=0;i<it.aliases.length;i++)if(it.aliases[i].toLowerCase()===t)return {tier:1};
    if(it.keys&&(/\+/.test(t)||/^f\d+$/.test(t)||t==='delete')){
      var kn=bimKeyNorm(it.keys.join('+')),tn=bimKeyNorm(t);
      if(kn===tn)return {tier:1.5};
    }
    if(nm.indexOf(t)===0)return {tier:2,hl:bimRange(0,t.length)};
    for(i=0;i<it.aliases.length;i++)if(it.aliases[i].toLowerCase().indexOf(t)===0)return {tier:3};
    k=nm.indexOf(t);
    if(k>0)return {tier:4,hl:bimRange(k,t.length)};
    var words=bimCmdWords(it.desc+' '+it.terms+' '+(it.keys?it.keys.join(' '):''));
    for(i=0;i<words.length;i++)if(words[i].indexOf(t)===0)return {tier:5};
    if(t.length>=2&&nm.charAt(0)===t.charAt(0)){var sq=bimSubseq(nm,t);if(sq)return {tier:6,hl:sq};}   /* an abbreviation: from the first letter */
    var ww=bimCmdWords(it.where.join(' '));
    for(i=0;i<ww.length;i++)if(ww[i].indexOf(t)===0)return {tier:7};
    if(t.length>=4){
      if(bimEditWithin1(t,nm))return {tier:8,typo:true};
      for(i=0;i<it.aliases.length;i++)if(bimEditWithin1(t,it.aliases[i].toLowerCase()))return {tier:8,typo:true};
      for(i=0;i<words.length;i++)if(words[i].length>=4&&bimEditWithin1(t,words[i]))return {tier:8,typo:true};
    }
    return {tier:-1};
  }
  function bimCmdUsage(){
    try{var u=JSON.parse(localStorage.getItem(BIM_CMD_USE_KEY)||'{}');return (u&&typeof u==='object')?u:{};}
    catch(eU){console.warn('[BIM] The command history could not be read; it starts again',eU);return {};}
  }
  function bimCmdUsed(id){
    var u=bimCmdUsage(),r=u[id]||{n:0,t:0},mx=0,k;
    for(k in u)if(u.hasOwnProperty(k)&&u[k].t>mx)mx=u[k].t;
    r.n++;r.t=Math.max(Date.now(),mx+1);u[id]=r;
    try{localStorage.setItem(BIM_CMD_USE_KEY,JSON.stringify(u));}
    catch(eS){console.warn('[BIM] The command history could not be saved',eS);}
  }
  /* why an entry cannot run where the user is now, or '' */
  function bimCmdOff(it){
    if(bimStartShowing())return (it.cad&&BIM_START_CMDS[it.cad])?'':'open a project first';
    if(bimSheetOnScreen())return (it.cad?BIM_SHEET_CMDS[it.cad]:BIM_SHEET_ACTS[it.act])?'':'works on the model, not a sheet';
    return '';
  }
  function bimCmdPublic(it,extra){
    var o={id:it.id,name:it.name,aliases:it.aliases.slice(),desc:it.desc,kind:it.cad?'cmd':'act',cad:it.cad,act:it.act||it.ribbon||null,
      where:it.where.slice(),keys:it.keys?it.keys.slice():null,off:bimCmdOff(it)};
    if(extra)for(var k in extra)if(extra.hasOwnProperty(k))o[k]=extra[k];
    return o;
  }
  /* The search. Every word typed must match; entries are ordered by how well, then by use. */
  function bimCmdSearch(q,limit){
    var cat=bimCmdCatalog(),use=bimCmdUsage(),s=String(q||'').trim().toLowerCase().replace(/^>\s*/,'');
    var toks=s?s.split(/\s+/):[],res=[],i,j;
    for(i=0;i<cat.length;i++){
      var it=cat[i],sum=0,hl=null,typo=false,ok=true;
      for(j=0;j<toks.length;j++){
        var r=bimCmdTier(it,toks[j]);
        if(r.tier<0){ok=false;break;}
        sum+=r.tier;if(r.hl&&!hl)hl=r.hl;if(r.typo)typo=true;
      }
      if(!ok)continue;
      var u=use[it.id];
      res.push({it:it,s:sum,n:toks.length&&u?u.n:0,i:i,hl:hl,typo:typo});
    }
    /* a typo is offered only when nothing matched as typed (VS Code's "similar commands") */
    var direct=res.filter(function(r){return !r.typo;});
    if(direct.length)res=direct;
    res.sort(function(a,b){return (a.s-b.s)||(b.n-a.n)||(a.i-b.i);});
    if(limit>0)res=res.slice(0,limit);
    return res.map(function(r){return bimCmdPublic(r.it,{hl:r.hl,typo:r.typo});});
  }
  function bimCmdRecent(k){
    var cat=bimCmdCatalog(),use=bimCmdUsage(),by={},ids=[],i,id;
    for(i=0;i<cat.length;i++)by[cat[i].id]=cat[i];
    for(id in use)if(use.hasOwnProperty(id)&&by[id])ids.push(id);
    ids.sort(function(a,b){return use[b].t-use[a].t;});
    return ids.slice(0,k||5).map(function(x){return bimCmdPublic(by[x],{recent:true});});
  }
  /* run an entry as its button or its typed name would, and remember that it was used */
  function bimCmdRun(id){
    var cat=bimCmdCatalog(),it=null,i,ran;
    for(i=0;i<cat.length;i++)if(cat[i].id===id){it=cat[i];break;}
    if(!it){a3dToast('That command is not available');return false;}
    if(it.cad)ran=!!(window.__a3dRunCmd&&window.__a3dRunCmd(it.cad));
    else{
      ran=bimRunAct(it.act)!==false;
      if(ran)bimRecordCmd(function(){bimRunAct(it.act);},it.act);   /* Enter repeats it, as it repeats a typed command */
    }
    if(ran)bimCmdUsed(it.id);
    return ran;
  }
  /* __acad3dV128: the command a ribbon action answers to when typed: "  . type WALL or WA" */
  function bimActHint(act,cat){
    var cad=BIM_ACT_CMD[act],i,it;
    for(i=0;i<cat.length;i++){
      it=cat[i];
      if((cad&&it.cad===cad)||it.act===act||it.ribbon===act)return '  \u00b7  type '+it.name+(it.aliases.length?' or '+it.aliases[0]:'');
    }
    return '';
  }
