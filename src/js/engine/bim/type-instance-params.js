  // ---- __acad3dV38: Type / instance parameters -- the core BIM data model gap. In Revit a Wall
  // Type ("Generic - 300mm") governs many instances: change the type's thickness and every wall
  // of that type updates. Height and Location Line stay INSTANCE parameters because each wall can
  // legitimately differ; putting them on the type would be wrong.
  //
  // INTEGRATION CHOICE, deliberately conservative: the instance keeps its own authoritative
  // bim.thickness exactly as before, and a type edit PROPAGATES by writing the new value into
  // every instance and rebuilding it. The alternative -- resolving thickness through the type on
  // every read -- would have meant touching bimBuildWallGeometry, DXF export, schedules, offset,
  // trim and the property panel. This way none of that code changes, and walls with no typeId
  // (everything in existing saved projects) keep behaving exactly as they do today.
  var WALL_TYPE_DEFAULTS=[
    {id:'wt-gen300',name:'Generic - 300mm',params:{thickness:0.3,material:'Generic'}},
    {id:'wt-gen200',name:'Generic - 200mm',params:{thickness:0.2,material:'Generic'}},
    {id:'wt-int100',name:'Interior - 100mm Partition',params:{thickness:0.1,material:'Partition'}},
    {id:'wt-ext400',name:'Exterior - 400mm',params:{thickness:0.4,material:'Masonry'}}
  ];
  // __acad3dV38: the wall type system already existed and was well-formed (defaults, instance
  // propagation, locked/imported skipping, save-load wiring) -- it was simply wall-only. Rather
  // than build a second registry beside it, these tables extend the SAME structure to floors,
  // ceilings and columns. TYPE_CATS declares, per category, which parameters belong to the type
  // (shared by every instance) and which stay per-instance, plus how to rebuild an instance.
  var FLOOR_TYPE_DEFAULTS=[
    {id:'ft-gen200',name:'Generic - 200mm',params:{thickness:0.2,material:'Generic'}},
    {id:'ft-gen300',name:'Generic - 300mm',params:{thickness:0.3,material:'Concrete'}},
    {id:'ft-tim150',name:'Timber - 150mm Joist',params:{thickness:0.15,material:'Timber'}}
  ];
  var CEIL_TYPE_DEFAULTS=[
    {id:'ct-gen100',name:'Generic - 100mm',params:{thickness:0.1,material:'Generic'}},
    {id:'ct-acc600',name:'Acoustic Tile - 600x600',params:{thickness:0.05,material:'Acoustic'}}
  ];
  var COL_TYPE_DEFAULTS=[
    {id:'ct-300',name:'300 x 300mm',params:{width:0.3,depth:0.3,material:'Concrete'}},
    {id:'ct-400',name:'400 x 400mm',params:{width:0.4,depth:0.4,material:'Concrete'}},
    {id:'ct-200x400',name:'200 x 400mm',params:{width:0.2,depth:0.4,material:'Concrete'}},
    {id:'ct-500',name:'500 x 500mm',params:{width:0.5,depth:0.5,material:'Concrete'}},        /* __acad3dV102 */
    {id:'ct-600',name:'600 x 600mm',params:{width:0.6,depth:0.6,material:'Concrete'}},
    {id:'ct-300x600',name:'300 x 600mm',params:{width:0.3,depth:0.6,material:'Concrete'}}
  ];
  /* __acad3dV126: steel columns and concrete rounds */
  [['ct-w8x31','W8x31',{shape:'ibeam',d:8.00*0.0254,bf:8.00*0.0254,tf:0.435*0.0254,tw:0.285*0.0254},'Steel'],
   ['ct-w10x49','W10x49',{shape:'ibeam',d:10.0*0.0254,bf:10.0*0.0254,tf:0.560*0.0254,tw:0.340*0.0254},'Steel'],
   ['ct-w12x65','W12x65',{shape:'ibeam',d:12.1*0.0254,bf:12.0*0.0254,tf:0.605*0.0254,tw:0.390*0.0254},'Steel'],
   ['ct-w14x90','W14x90',{shape:'ibeam',d:14.0*0.0254,bf:14.5*0.0254,tf:0.710*0.0254,tw:0.440*0.0254},'Steel'],
   ['ct-hss6x6','HSS6x6x3/8',{shape:'hss',B:6*0.0254,H:6*0.0254,t:0.349*0.0254},'Steel'],
   ['ct-hss8x8','HSS8x8x1/2',{shape:'hss',B:8*0.0254,H:8*0.0254,t:0.465*0.0254},'Steel'],
   ['ct-hss10x10','HSS10x10x1/2',{shape:'hss',B:10*0.0254,H:10*0.0254,t:0.465*0.0254},'Steel'],
   ['ct-pipe6','Pipe 6 STD',{shape:'pipe',D:6.625*0.0254,t:0.280*0.0254},'Steel'],
   ['ct-pipe8','Pipe 8 STD',{shape:'pipe',D:8.625*0.0254,t:0.322*0.0254},'Steel'],
   ['ct-r400','Round 400mm',{shape:'circle',D:0.4},'Concrete'],
   ['ct-r500','Round 500mm',{shape:'circle',D:0.5},'Concrete'],
   ['ct-r600','Round 600mm',{shape:'circle',D:0.6},'Concrete']
  ].forEach(function(r){COL_TYPE_DEFAULTS.push(bimSectionType('column',r[0],r[1],r[2],r[3]));});
  /* __acad3dV126: a profile's extent without its outline -- this runs while the catalogues below are
     being built, before the round's segment count is set */
  function bimProfileBox(p){
    if(p.shape==='rect')return {y:p.d,z:p.b};
    if(p.shape==='circle'||p.shape==='pipe')return {y:p.D,z:p.D};
    if(p.shape==='hss')return {y:p.H,z:p.B};
    return {y:p.d,z:p.bf};
  }
  /* a profiled type: a column's width runs along its y, a beam's depth is its y */
  function bimSectionType(cat,id,name,prof,mat){
    var b=bimProfileBox(prof);
    return {id:id,name:name,params:cat==='column'?{width:b.y,depth:b.z,material:mat,profile:prof}:{width:b.z,depth:b.y,material:mat,profile:prof}};
  }
  var BIM_IN=0.0254;
  function bimW(d,bf,tf,tw){return {shape:'ibeam',d:d*BIM_IN,bf:bf*BIM_IN,tf:tf*BIM_IN,tw:tw*BIM_IN};}
  function bimIPE(d,bf,tf,tw){return {shape:'ibeam',d:d/1000,bf:bf/1000,tf:tf/1000,tw:tw/1000};}
  function bimC(d,bf,tf,tw){return {shape:'channel',d:d*BIM_IN,bf:bf*BIM_IN,tf:tf*BIM_IN,tw:tw*BIM_IN};}
  /* __acad3dV102: the structural catalogue */
  var BEAM_TYPE_DEFAULTS=[
    {id:'bt-250x450',name:'250 x 450mm',params:{width:0.25,depth:0.45,material:'Concrete'}},
    {id:'bt-300x500',name:'300 x 500mm',params:{width:0.3,depth:0.5,material:'Concrete'}},
    {id:'bt-300x600',name:'300 x 600mm',params:{width:0.3,depth:0.6,material:'Concrete'}},
    {id:'bt-400x700',name:'400 x 700mm',params:{width:0.4,depth:0.7,material:'Concrete'}}
  ];
  /* __acad3dV126: steel beams -- AISC W and C (inches), EN 10365 IPE (mm), nominal dimensions */
  [['bt-w8x31','W8x31',bimW(8.00,8.00,0.435,0.285)],['bt-w10x33','W10x33',bimW(9.73,7.96,0.435,0.290)],
   ['bt-w12x26','W12x26',bimW(12.2,6.49,0.380,0.230)],['bt-w14x30','W14x30',bimW(13.8,6.73,0.385,0.270)],
   ['bt-w16x40','W16x40',bimW(16.0,7.00,0.505,0.305)],['bt-w18x50','W18x50',bimW(18.0,7.50,0.570,0.355)],
   ['bt-w21x62','W21x62',bimW(21.0,8.24,0.615,0.400)],['bt-w24x76','W24x76',bimW(23.9,8.99,0.680,0.440)],
   ['bt-ipe200','IPE 200',bimIPE(200,100,8.5,5.6)],['bt-ipe240','IPE 240',bimIPE(240,120,9.8,6.2)],
   ['bt-ipe300','IPE 300',bimIPE(300,150,10.7,7.1)],['bt-ipe360','IPE 360',bimIPE(360,170,12.7,8.0)],
   ['bt-ipe400','IPE 400',bimIPE(400,180,13.5,8.6)],
   ['bt-c8x11','C8x11.5',bimC(8.00,2.26,0.390,0.220)],['bt-c10x15','C10x15.3',bimC(10.0,2.60,0.436,0.240)],
   ['bt-c12x21','C12x20.7',bimC(12.0,2.94,0.501,0.282)]
  ].forEach(function(r){BEAM_TYPE_DEFAULTS.push(bimSectionType('beam',r[0],r[1],r[2],'Steel'));});
  var FOOTING_TYPE_DEFAULTS=[
    {id:'ft-iso1200',name:'1200 x 1200 x 400mm',params:{width:1.2,length:1.2,thickness:0.4,material:'Concrete'}},
    {id:'ft-iso1500',name:'1500 x 1500 x 500mm',params:{width:1.5,length:1.5,thickness:0.5,material:'Concrete'}},
    {id:'ft-iso2000',name:'2000 x 2000 x 600mm',params:{width:2.0,length:2.0,thickness:0.6,material:'Concrete'}}
  ];
  var STRIP_TYPE_DEFAULTS=[
    {id:'sf-600x300',name:'600 x 300mm',params:{width:0.6,thickness:0.3,material:'Concrete'}},
    {id:'sf-800x400',name:'800 x 400mm',params:{width:0.8,thickness:0.4,material:'Concrete'}},
    {id:'sf-1000x450',name:'1000 x 450mm',params:{width:1.0,thickness:0.45,material:'Concrete'}}
  ];
  var TYPE_CATS={
    wall:   {label:'Walls',    family:'Basic Wall',         defaults:WALL_TYPE_DEFAULTS,  typeParams:['thickness']},
    floor:  {label:'Floors',   family:'Floor',              defaults:FLOOR_TYPE_DEFAULTS, typeParams:['thickness']},
    ceiling:{label:'Ceilings', family:'Compound Ceiling',   defaults:CEIL_TYPE_DEFAULTS,  typeParams:['thickness']},
    column: {label:'Columns',  family:'Rectangular Column', defaults:COL_TYPE_DEFAULTS,   typeParams:['width','depth']},
    beam:   {label:'Beams',    family:'Concrete Beam',      defaults:BEAM_TYPE_DEFAULTS,  typeParams:['width','depth']},        /* __acad3dV102 */
    footing:{label:'Isolated Footings',family:'Isolated Footing',defaults:FOOTING_TYPE_DEFAULTS,typeParams:['width','length','thickness']},
    stripfooting:{label:'Wall Foundations',family:'Wall Foundation',defaults:STRIP_TYPE_DEFAULTS,typeParams:['width','thickness']}
  };
  // __acad3dV59: Phase 51 -- graphic override data model. Per the roadmap's own phase spec, this
  // is DATA AND UI ONLY: nothing in bimBuildDXF/bimBuildSVG/bimBuildPlanViewportSVG or the live
  // Canvas2D/WebGL paint path reads any of this yet. Phase 52 (presentation render mode) is the
  // consumer. Two dictionaries per object, not one, because a technical (construction-document)
  // appearance and a presentation (client-facing) appearance are legitimately different things for
  // the same element -- e.g. a wall's cut poche is usually plain in a technical set and colored in
  // a presentation set -- and the roadmap names both explicitly.
  //
  // TWO LEVELS, deliberately not one flat registry: TYPE-level graphics live on A3D.types[cat][i]
  // .graphics (only the four TYPE_CATS categories -- wall/floor/ceiling/column -- have a type
  // system to hang this on), and INSTANCE-level overrides live on o.graphicsOverride, at the TOP
  // of the object (a sibling of o.layer/o.pos), not nested under o.bim -- because unlike thickness
  // or width, an appearance override is meaningful for ANY object this app can export (rooms,
  // dimensions, sketches, text, doors, windows, roofs, stairs), most of which have no .bim at all.
  // Resolution order, cheapest-wins: instance override > type default > a single hard-coded
  // fallback -- the same "type is shared, instance may diverge" shape the existing thickness/width
  // type params already use, extended to appearance data instead of geometry.
  var BIM_GRAPHICS_KEYS=['lineWeight','lineColor','fill','pattern','opacity','shadow','patternColor','patternScale','patternAngle'];
  /* __acad3dV63 (Phase 53): the pattern list grew from the six placeholder names Phase 51 stored
     but never drew, into the set below, and `pattern` finally renders. The two new graphics keys
     are the minimum a hatch needs to be a real drafting tool rather than a fixed decoration:
     patternColor, because a hatch is conventionally drawn lighter than the object's own outline
     (a solid poche and a 0.25 mm outline in the same colour is a black blob), and patternScale,
     because hatch density is the single most-adjusted parameter in practice -- the same physical
     pattern has to read correctly at 1:50 and at 1:200. Both are optional and default to values
     that reproduce the pre-Phase-53 look, so an existing saved project is unaffected until the
     user actually sets a pattern. */
  var BIM_HATCH_PATTERNS=['none','solid','horizontal','vertical','diagonal','diagonal-reverse','cross','dots','brick','concrete','steel'];
  /* Procedural pattern definitions. Each is a tile whose geometry is expressed in NORMALISED tile
     coordinates (0..1 on both axes), plus the tile's physical size in millimetres. Keeping the
     geometry unit-square and the size physical is what lets one definition serve both sinks
     without a second copy of the artwork: the Canvas2D renderer multiplies the tile by
     BIM_LW_TO_PX (px per mm) and the SVG writers multiply it by their own units-per-mm, exactly
     as each already does for lineWeight. `w` is the tile's width multiple (2 for a running-bond
     brick, whose tile is twice as wide as it is tall); everything else is square.

     Every primitive lies wholly inside the unit tile or runs edge-to-edge, so the pattern tiles
     seamlessly with no bleed: a lone diagonal from (0,0) to (1,1) repeats into a continuous field
     of 45-degree lines, and a centred dot repeats into a square grid, which is why those are
     written that way rather than as several parallel strokes inside one tile.

     'none' draws nothing (the pre-Phase-53 behaviour, still the default) and 'solid' is a full
     flood of patternColor, so neither carries tile geometry. */
  var BIM_PATTERN_DEFS={
    'horizontal':       {label:'Horizontal',      mm:2.5, w:1, lines:[[0,0.5,1,0.5]]},
    'vertical':         {label:'Vertical',        mm:2.5, w:1, lines:[[0.5,0,0.5,1]]},
    'diagonal':         {label:'Diagonal',        mm:2.5, w:1, lines:[[0,0,1,1]]},
    'diagonal-reverse': {label:'Diagonal (rev)',  mm:2.5, w:1, lines:[[0,1,1,0]]},
    'cross':            {label:'Crosshatch',      mm:2.5, w:1, lines:[[0,0,1,1],[0,1,1,0]]},
    'dots':             {label:'Dots',            mm:3.0, w:1, lines:[], dots:[[0.5,0.5,0.10]]},
    // Running bond: two courses per tile, so the head joints of the upper course sit at the
    // mid-point of the lower course's stretchers -- the tile is 2:1 for that reason, not for looks.
    'brick':            {label:'Brick (running bond)', mm:4.0, w:2,
                         lines:[[0,0,1,0],[0,0.5,1,0.5],[0,0,0,0.5],[0.5,0.5,0.5,1]]},
    // The conventional architectural concrete symbol: scattered aggregate with short ticks.
    // Positions are fixed, not random, so the same drawing exports byte-identically every time.
    'concrete':         {label:'Concrete',        mm:5.0, w:1,
                         lines:[[0.08,0.72,0.26,0.88],[0.62,0.14,0.82,0.30]],
                         dots:[[0.30,0.28,0.07],[0.74,0.66,0.06],[0.52,0.86,0.05]]},
    // Steel section hatch: paired close diagonals. The second line is split at the tile edge so
    // the offset copy stays inside the tile and still meets its neighbour across the seam.
    'steel':            {label:'Steel',           mm:3.0, w:1,
                         lines:[[0,0,1,1],[0,0.32,0.68,1],[0.68,0,1,0.32]]}
  };
  function bimPatternDef(name){
    return (name&&BIM_PATTERN_DEFS.hasOwnProperty(name))?BIM_PATTERN_DEFS[name]:null;
  }
  // A pattern is drawable only if it is a real fill ('solid') or has tile geometry. 'none' and
  // any unknown value answer false, so every render site can ask one question instead of
  // re-deriving the special cases.
  function bimPatternDraws(name){
    return name==='solid'||!!bimPatternDef(name);
  }
  function bimPatternLabel(name){
    if(name==='none')return 'None';
    if(name==='solid')return 'Solid fill';
    var d=bimPatternDef(name);
    return d?d.label:name;
  }
  // __acad3dV60: mm-to-px conversion for the live Canvas2D presentation renderer, chosen so the
  // UNTOUCHED default lineWeight (0.25mm) reproduces the exact 0.7px stroke the solid-face loop
  // already used before Phase 52a -- a type/instance nobody has edited looks pixel-identical.
  var BIM_LW_TO_PX=2.8;
  /* __acad3dV63 (Phase 53): the Canvas2D pattern sink. Builds one small offscreen tile per
     (pattern, colour, tile-size) combination and hands back a repeating CanvasPattern for it.

     Why a tile canvas and not a per-face stroke loop: the faces being filled are arbitrary
     projected polygons, so clipping and stroking a hatch by hand would mean a clip + N strokes
     per face per frame. createPattern does the same work in the compositor and, cached, costs one
     canvas per distinct appearance for the life of the session.

     The cache key includes the pixel tile size rather than the raw scale, so two scales that round
     to the same tile share one canvas; it cannot grow with zoom or pan because tile size depends
     only on the pattern's physical size and the user's patternScale, never on the camera.

     Honest scope note: the pattern is applied in SCREEN space, so in a plan or elevation view --
     an orthographic, uniformly-scaled projection, which is where hatch actually matters and what
     presentation mode exists for -- it reads exactly as a drafted hatch should. In a perspective
     3D view it is a screen-aligned fill rather than a surface-aligned one, i.e. it does not
     foreshorten with the face. Making it surface-aligned needs per-face UV projection, which is a
     different feature; this is recorded rather than left to be discovered. */
  var BIM_PAT_CACHE={};
  function bimPatternTile(name,color,tw,th,sc){
    var key=name+'|'+color+'|'+tw+'x'+th;
    if(BIM_PAT_CACHE[key])return BIM_PAT_CACHE[key];
    var def=bimPatternDef(name);
    if(!def)return null;
    var cv=document.createElement('canvas');
    cv.width=tw;cv.height=th;
    var c2=cv.getContext('2d');
    if(!c2)return null;
    c2.strokeStyle=color;c2.fillStyle=color;
    c2.lineCap='square';
    c2.lineWidth=Math.max(0.6,Math.min(2.2,0.18*BIM_LW_TO_PX*Math.sqrt(sc)));
    var L=def.lines||[],D=def.dots||[],i;
    for(i=0;i<L.length;i++){
      c2.beginPath();
      c2.moveTo(L[i][0]*tw,L[i][1]*th);
      c2.lineTo(L[i][2]*tw,L[i][3]*th);
      c2.stroke();
    }
    for(i=0;i<D.length;i++){
      c2.beginPath();
      c2.arc(D[i][0]*tw,D[i][1]*th,Math.max(0.7,D[i][2]*Math.min(tw,th)),0,Math.PI*2);
      c2.fill();
    }
    BIM_PAT_CACHE[key]=cv;
    return cv;
  }
  function bimPatternTileSize(name,scale){
    var def=bimPatternDef(name);
    if(!def)return null;
    var sc=(scale>0)?scale:1;
    return {w:Math.max(4,Math.round(def.mm*(def.w||1)*BIM_LW_TO_PX*sc)),
            h:Math.max(4,Math.round(def.mm*BIM_LW_TO_PX*sc)),sc:sc};
  }
  // Returns a fillStyle for the resolved graphics, or null when this appearance has no pattern to
  // draw. 'solid' short-circuits to the plain colour: a full flood needs no tile.
  function bimCanvasPatternFill(ctx,rg){
    if(!ctx||!rg||!bimPatternDraws(rg.pattern))return null;
    var col=rg.patternColor||'#555555';
    if(rg.pattern==='solid')return col;
    var sz=bimPatternTileSize(rg.pattern,rg.patternScale);
    if(!sz)return null;
    var tile=bimPatternTile(rg.pattern,col,sz.w,sz.h,sz.sc);
    if(!tile)return null;
    try{
      var pat=ctx.createPattern(tile,'repeat');
      /* __acad3dV96: the angle, through the one rotation function both sinks use. Guarded
         because setTransform and DOMMatrix are not universal; without them the pattern draws
         unrotated rather than not at all. */
      var ang=bimPatternRotation(rg.patternAngle,true);
      if(pat&&ang&&typeof pat.setTransform==='function'&&typeof DOMMatrix!=='undefined'){
        try{pat.setTransform(new DOMMatrix().rotate(ang));}
        catch(eR){console.warn('[BIM] Pattern rotation unavailable: ',eR);}
      }
      return pat;
    }
    catch(eP){console.warn('[BIM] Pattern fill unavailable: ',eP);return null;}
  }
  function bimDefaultGraphics(){
    /* __acad3dV63: patternColor/patternScale join the dict. pattern still defaults to 'none', so
       a project that has never been touched since Phase 51 resolves exactly the appearance it
       resolved before -- the two new keys only start mattering once a pattern is actually chosen. */
    /* __acad3dV96: patternAngle defaults to 0, so a project saved before this phase resolves
       the appearance it always did. */
    return {lineWeight:0.25,lineColor:'#000000',fill:'none',pattern:'none',opacity:1,shadow:false,
            patternColor:'#555555',patternScale:1,patternAngle:0};
  }
  function bimNewGraphicsSet(){
    return {technical:bimDefaultGraphics(),presentation:bimDefaultGraphics()};
  }
  /* __acad3dV96: the field checks, once. bimSanitizeGraphics and bimSanitizeGraphicsOverride
     had identical copies of this list and differed only in what an ABSENT key means -- defaults
     for a full set, inherit-from-type for an override. That difference lives in the callers; the
     validation lives here, so a new key is added in one place and the two cannot drift. */
  function bimApplyGraphicsFields(src,dst){
    if(!src||typeof src!=='object'||!dst)return dst;
    if(typeof src.lineWeight==='number'&&isFinite(src.lineWeight)&&src.lineWeight>0)dst.lineWeight=src.lineWeight;
    if(bimValidGraphicsColor(src.lineColor)&&src.lineColor!=='none')dst.lineColor=src.lineColor;
    if(bimValidGraphicsColor(src.fill))dst.fill=src.fill;
    if(typeof src.pattern==='string'&&BIM_HATCH_PATTERNS.indexOf(src.pattern)>=0)dst.pattern=src.pattern;
    if(typeof src.opacity==='number'&&isFinite(src.opacity))dst.opacity=Math.max(0,Math.min(1,src.opacity));
    if(typeof src.shadow==='boolean')dst.shadow=src.shadow;
    /* __acad3dV63: patternColor reuses the same colour validator as lineColor and, like it,
       rejects 'none' (a hatch with no colour is just 'pattern:none', which the pattern field
       already expresses). patternScale is clamped to a range that stays drawable at both ends:
       below ~0.1 the tile collapses to sub-pixel noise, above 8 it is a single line per face. */
    if(bimValidGraphicsColor(src.patternColor)&&src.patternColor!=='none')dst.patternColor=src.patternColor;
    if(typeof src.patternScale==='number'&&isFinite(src.patternScale)&&src.patternScale>0)
      dst.patternScale=Math.max(0.1,Math.min(8,src.patternScale));
    /* __acad3dV96: normalised into [0,180). A hatch line at 200 degrees is the same field of
       lines as one at 20, so storing it any other way gives two values that draw identically
       and compare unequal. */
    if(typeof src.patternAngle==='number'&&isFinite(src.patternAngle))
      dst.patternAngle=((src.patternAngle%180)+180)%180;
    return dst;
  }
  /* __acad3dV96: what rotation a sink applies for a MODEL angle. Both sinks draw with y
     increasing downward -- the SVG writers emit -y and the canvas is screen space -- so a model
     angle measured counter-clockwise from +x is applied as its negative in both. One answer for
     both, because a sign that is right in one sink and wrong in the other is invisible until
     someone exports a drawing and compares it with the screen. */
  /* __acad3dV96: does this appearance draw whatever the mode is?

     Everything the pattern library drew before this phase was a presentation-mode override, so
     every sink gated on presentation mode. A hatch is drawn geometry and is not mode-driven, so
     it carries `explicit` and the four gates ask here instead of each deciding for itself. */
  function bimPatternAlways(pres,rg){
    return !!(rg&&(pres||rg.explicit));
  }
  function bimPatternRotation(angleDeg,yDown){
    var a=(typeof angleDeg==='number'&&isFinite(angleDeg))?(((angleDeg%180)+180)%180):0;
    return yDown?-a:a;
  }
  function bimValidGraphicsColor(v){
    return typeof v==='string'&&(v==='none'||/^#[0-9a-fA-F]{6}$/.test(v));
  }
  // Sanitizes a FULL appearance dict (every key always present) -- used for type-level graphics,
  // where "missing" means "not yet migrated" and should be filled with the hard default, not left
  // absent. Tolerant of anything: undo snapshots, an older save file predating this phase, or a
  // hand-edited project JSON all hand this function whatever they have, and it always returns a
  // complete, well-typed dict rather than letting a bad value reach the (future) renderer.
  function bimSanitizeGraphics(g){
    var out=bimNewGraphicsSet();
    if(!g||typeof g!=='object')return out;
    var modes=['technical','presentation'],mi;
    for(mi=0;mi<modes.length;mi++){
      var m=modes[mi],src=g[m];
      if(!src||typeof src!=='object')continue;
      bimApplyGraphicsFields(src,out[m]);   /* __acad3dV96 */
    }
    return out;
  }
  // Sanitizes a PARTIAL override dict -- unlike bimSanitizeGraphics, an absent/invalid key here
  // means "inherit from type", never "reset to the hard default". Overrides and full appearance
  // sets have opposite absence semantics, so they get separate sanitizers on purpose rather than
  // one function trying to serve both.
  function bimSanitizeGraphicsOverride(ov){
    var out={technical:{},presentation:{}};
    if(!ov||typeof ov!=='object')return out;
    var modes=['technical','presentation'],mi;
    for(mi=0;mi<modes.length;mi++){
      var m=modes[mi],src=ov[m];
      if(!src||typeof src!=='object')continue;
      bimApplyGraphicsFields(src,out[m]);   /* __acad3dV96 */
    }
    return out;
  }
  // Resolves an object's EFFECTIVE appearance for one mode: instance override wins field-by-field
  // over the type default, which wins over the hard-coded fallback. Works for any object, typed or
  // not -- an object with no type system behind it (a room, a dimension, imported geometry) simply
  // has nothing to inherit from and resolves straight from the fallback plus its own override.
  /* __acad3dV69: assigning a card to a solid gives BOTH a plan cut pattern and a quantity takeoff
     from the same act. */
  function bimMaterialCards(){
    return A3D_MATERIAL_LIBRARY;   /* __acad3dV120 */
  }
  function bimMaterialByName(n){
    var cards=bimMaterialCards(),i;
    for(i=0;i<cards.length;i++)if(cards[i].name===n)return cards[i];
    return null;
  }
  function bimMaterialOf(o){
    return (o&&o.materialName)?bimMaterialByName(o.materialName):null;
  }
  /* A card's hatch is {angle, gap, cross}; this app's pattern engine
     takes a NAMED pattern from BIM_HATCH_PATTERNS. Mapping rather than adding a second hatch
     renderer keeps one pattern pipeline -- the one Phase 53 already tested against canvas,
     SVG and the sheet exporter. Angles are folded into [0,180) first so 225 reads as 45. */
  /* Mixes a colour toward white. Used for ONE thing: turning a material's own swatch colour into
     a poche tint light enough for its hatch to read on top of. Deriving the tint avoids a second
     colour per card that the library would have to keep in step. */
  function bimTintColor(hex,amount){
    if(typeof hex!=='string'||!/^#[0-9a-fA-F]{6}$/.test(hex))return '#dddddd';
    var i,c,out='#';
    for(i=0;i<3;i++){
      c=parseInt(hex.substr(1+i*2,2),16);
      c=Math.round(c+(255-c)*amount);
      out+=('0'+Math.max(0,Math.min(255,c)).toString(16)).slice(-2);
    }
    return out;
  }
  function bimMaterialPattern(card){
    if(!card||!card.hatch)return null;
    var h=card.hatch,a=((h.angle||0)%180+180)%180,name;
    if(h.cross)name='cross';
    else if(a<=15||a>=165)name='horizontal';
    else if(a>=75&&a<=105)name='vertical';
    else if(a<90)name='diagonal';
    else name='diagonal-reverse';
    /* patternColor is the card's colour UNCHANGED, so a material hatches in its own colour. Only
       the fill underneath is derived: a hatch with nothing behind it is invisible in a plan --
       the wall poche is gated on fill!=='none'. */
    /* __acad3dV96: the card's ANGLE is carried through rather than thrown away after being
       used to pick a tile name. Before this a 30-degree material hatch chose the 'diagonal'
       tile and then drew at 45, so the two engines disagreed about the same material -- which
       is the one thing the note above says must not happen. The four fixed names keep their
       own built-in direction, so the residual angle is what is left after that choice. */
    var baseAng=(name==='vertical')?90:((name==='diagonal')?45:((name==='diagonal-reverse')?135:0));
    return {pattern:name,patternColor:card.color||'#555555',
      fill:bimTintColor(card.color||'#555555',0.62),
      patternAngle:((a-baseAng)%180+180)%180,
      patternScale:Math.max(0.1,Math.min(8,(h.gap||8)/8))};
  }
  /* Volume is reported ONLY for a mesh that bounds a closed volume. The divergence-theorem
     figure is exact for a closed surface and MEANINGLESS for an open one, and a plausible
     wrong mass on a quantity takeoff is worse than no mass at all (Product Principle 2), so an
     unclosed or corrupt mesh returns null and the UI shows an em dash. */
  function bimObjVolume(o){
    if(!o||!o.mesh||!o.mesh.v||!o.mesh.f||!o.mesh.f.length)return null;
    var c=bimMeshClosureCheck(o.mesh);
    if(!c||!c.closed||c.corrupt)return null;
    return Math.abs(c.vol);
  }
  function bimObjMass(o){
    var card=bimMaterialOf(o),vol=bimObjVolume(o);
    if(!card||vol===null||!card.density)return null;
    return card.density*vol;
  }
  function bimSetMaterial(o,name){
    if(!o)return false;
    if(!name){delete o.materialName;return true;}
    if(!bimMaterialByName(name))return false;
    o.materialName=name;
    return true;
  }
  /* The "nobody chose a pattern" sentinel, read from bimDefaultGraphics rather than written as a
     literal so the two can never drift apart. */
  var BIM_HARD_DEFAULT_PATTERN=bimDefaultGraphics().pattern;
  var BIM_HARD_DEFAULT_FILL=bimDefaultGraphics().fill;
  var BIM_MAT_COLS=[{key:'material',label:'Material'},
    {key:'volume',label:'Volume (m\u00b3)',fmt:3},{key:'mass',label:'Mass (kg)',fmt:1}];
  function bimMatRow(o){
    return {material:o.materialName||null,volume:bimObjVolume(o),mass:bimObjMass(o)};
  }
  function bimMergeRow(base,extra){
    var k;for(k in extra)if(extra.hasOwnProperty(k))base[k]=extra[k];
    return base;
  }
  function bimResolveGraphics(o,mode){
    mode=(mode==='presentation')?'presentation':'technical';
    var out=bimDefaultGraphics();
    var cat=o&&o.bim&&(o.bim.typeCat||o.bim.type);
    if(cat&&TYPE_CATS[cat]&&o.bim.typeId){
      bimEnsureTypes();
      var t=bimFindType(cat,o.bim.typeId);
      if(t&&t.graphics&&t.graphics[mode]){
        var k;
        for(k in t.graphics[mode])if(t.graphics[mode].hasOwnProperty(k))out[k]=t.graphics[mode][k];
      }
    }
    /* __acad3dV69: an assigned material supplies the cut pattern, as it does in Revit -- where
       the pattern is a parameter OF the material, not of the type.

       It is applied here, AFTER the type, and only when nothing has expressed a preference. The
       first build of this phase applied it before the type and it never once took effect: a
       type's graphics are a FULL dict (bimNewGraphicsSet copies bimDefaultGraphics for every
       key), so t.graphics[mode].pattern is always present and always overwrote the material with
       'none'. Ordering alone cannot fix that; the gate is what fixes it. The instance override
       still runs last, so a user asking for 'none' on an object with a material gets 'none'.

       The known limit, stated rather than hidden: a type whose pattern was deliberately SET to
       'none' is indistinguishable from one that never chose, so a material will fill it in. */
    var matCard=bimMaterialOf(o),matPat=matCard?bimMaterialPattern(matCard):null;
    if(matPat&&out.pattern===BIM_HARD_DEFAULT_PATTERN){
      out.pattern=matPat.pattern;
      out.patternColor=matPat.patternColor;
      out.patternScale=matPat.patternScale;
    }
    /* The fill is gated SEPARATELY, on its own hard default. A wall poche is only emitted when
       fill!=='none' (see wallPoche), so a material that supplied a pattern but no fill would
       resolve correctly, export nothing, and read to the user as a control that does not work. */
    if(matPat&&out.fill===BIM_HARD_DEFAULT_FILL){
      out.fill=matPat.fill;
    }
    if(o&&o.graphicsOverride){
      var ovs=bimSanitizeGraphicsOverride(o.graphicsOverride);
      var k2;
      for(k2 in ovs[mode])if(ovs[mode].hasOwnProperty(k2))out[k2]=ovs[mode][k2];
    }
    return out;
  }
  // Sets (or, with value null/undefined/'', clears) one field of one object's INSTANCE override.
  // Clearing a field makes that field inherit from the type again -- it does not reset the type
  // itself, and it does not touch the object's other override fields.
  function bimSetGraphicsOverride(o,mode,key,value){
    if(!o||BIM_GRAPHICS_KEYS.indexOf(key)<0)return false;
    mode=(mode==='presentation')?'presentation':'technical';
    if(!o.graphicsOverride||typeof o.graphicsOverride!=='object')o.graphicsOverride={technical:{},presentation:{}};
    if(!o.graphicsOverride.technical)o.graphicsOverride.technical={};
    if(!o.graphicsOverride.presentation)o.graphicsOverride.presentation={};
    if(value===null||value===undefined||value===''){
      delete o.graphicsOverride[mode][key];
    }else{
      o.graphicsOverride[mode][key]=value;
    }
    return true;
  }
  // Clears every override field for one mode on one instance (a full "Reset to Type" for that
  // mode), leaving the other mode's overrides untouched.
  function bimClearGraphicsOverride(o,mode){
    if(!o)return false;
    mode=(mode==='presentation')?'presentation':'technical';
    if(!o.graphicsOverride||typeof o.graphicsOverride!=='object')o.graphicsOverride={technical:{},presentation:{}};
    o.graphicsOverride[mode]={};
    return true;
  }
  // Sets one field of one TYPE's graphics (shared by every instance of that type that has no
  // instance-level override of its own for that same field) -- the appearance analogue of editing
  // a type's thickness. No geometry rebuild is needed since this never touches mesh/centerline
  // data, unlike bimApplyTypeToInstances.
  function bimSetTypeGraphics(cat,typeId,mode,key,value){
    var t=bimFindType(cat,typeId);
    if(!t||BIM_GRAPHICS_KEYS.indexOf(key)<0)return false;
    mode=(mode==='presentation')?'presentation':'technical';
    if(!t.graphics||typeof t.graphics!=='object')t.graphics=bimNewGraphicsSet();
    t.graphics[mode][key]=value;
    return true;
  }
  function bimEnsureTypes(){
    if(!A3D.types||typeof A3D.types!=='object')A3D.types={};
    var c;
    for(c in TYPE_CATS){
      if(!TYPE_CATS.hasOwnProperty(c))continue;
      if(!Array.isArray(A3D.types[c])||!A3D.types[c].length)
        A3D.types[c]=JSON.parse(JSON.stringify(TYPE_CATS[c].defaults));
      var list=A3D.types[c],ti;
      for(ti=0;ti<list.length;ti++)list[ti].graphics=bimSanitizeGraphics(list[ti].graphics);
    }
    /* __acad3dV126: a project stored before V126 gains the section types once, by id -- its own types
       are untouched, and one it deletes later is not put back */
    if(!A3D.types.__v126){
      ['column','beam'].forEach(function(cat){
        var have={},list=A3D.types[cat],k;
        for(k=0;k<list.length;k++)have[list[k].id]=1;
        TYPE_CATS[cat].defaults.forEach(function(dt){
          if(dt.params&&dt.params.profile&&!have[dt.id]){
            var cp=JSON.parse(JSON.stringify(dt));cp.graphics=bimSanitizeGraphics(cp.graphics);list.push(cp);
          }
        });
      });
      A3D.types.__v126=1;
    }
    if(!A3D.activeWallType)A3D.activeWallType=A3D.types.wall[0].id;
    return A3D.types;
  }
  // Give an object a type if it has none (files saved before a category had types), matching an
  // existing type with the same values so N identical objects share one type rather than making N.
  function bimEnsureObjType(o){
    if(!o||!o.bim)return null;
    var cat=o.bim.type,def=TYPE_CATS[cat];
    if(!def)return null;
    bimEnsureTypes();
    if(o.bim.typeId){
      var ex=bimFindType(cat,o.bim.typeId);
      if(ex)return ex;
    }
    var list=A3D.types[cat],i,j;
    for(i=0;i<list.length;i++){
      var ok=true;
      for(j=0;j<def.typeParams.length;j++){
        var k=def.typeParams[j];
        if(Math.abs((list[i].params[k]||0)-(o.bim[k]||0))>1e-9){ok=false;break;}
      }
      if(ok){o.bim.typeId=list[i].id;o.bim.typeCat=cat;return list[i];}
    }
    var nm=def.typeParams.map(function(k){return Math.round((o.bim[k]||0)*1000);}).join(' x ')+'mm';
    var nt={id:'ty-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e5),name:nm,params:{}};
    for(j=0;j<def.typeParams.length;j++)nt.params[def.typeParams[j]]=o.bim[def.typeParams[j]];
    A3D.types[cat].push(nt);
    o.bim.typeId=nt.id;o.bim.typeCat=cat;
    return nt;
  }
  function bimRebuildInstanceForType(o,t){
    var cat=o.bim.type;
    if(cat==='wall'){
      if(!o.bim.centerline)return false;
      var r=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,t.params.thickness,o.bim.align,o.bim.closed,o.bim.bulges);
      if(r.error)return false;
      o.mesh=r.mesh;o.bim=bimCarryBim(o.bim,r.bim);   /* __acad3dV123 */
      bimAfterWallRebuild(o);   // __acad3dV51: the rebuild dropped this wall's openings; re-cut them
      return true;
    }
    if(cat==='floor'){
      if(!o.bim.profile)return false;
      var r2=bimBuildFloorGeometry(sketchCCW(o.bim.profile),o.bim.baseY,t.params.thickness);
      if(r2.error)return false;
      o.mesh=r2.mesh;o.bim.thickness=t.params.thickness;
      return true;
    }
    if(cat==='ceiling'){
      if(!o.bim.profile)return false;
      var r3=bimBuildFloorGeometry(sketchCCW(o.bim.profile),o.bim.baseY+t.params.thickness,t.params.thickness);
      if(r3.error)return false;
      o.mesh=r3.mesh;o.bim.thickness=t.params.thickness;
      return true;
    }
    if(cat==='column'){
      if(!o.bim.center)return false;
      // __acad3dV81: and through a TYPE change, for the same reason.
      var tp4=t.params.profile||null;   /* __acad3dV126 */
      var r4=bimBuildColumnGeometry(o.bim.center,o.bim.baseY,t.params.width,t.params.depth,o.bim.height,o.bim.rotation||0,tp4);
      if(r4.error)return false;
      o.mesh=r4.mesh;o.bim.width=t.params.width;o.bim.depth=t.params.depth;
      if(tp4)o.bim.section=JSON.parse(JSON.stringify(tp4));else delete o.bim.section;
      bimAfterWallRebuild(o);   /* __acad3dV102: a footing under it follows */
      return true;
    }
    if(cat==='beam'){   /* __acad3dV102 */
      if(!o.bim.p1||!o.bim.p2)return false;
      var tp5=t.params.profile||null;   /* __acad3dV126 */
      var r5=bimBuildBeamGeometry(o.bim.p1,o.bim.p2,o.bim.topY,t.params.width,t.params.depth,tp5);
      if(r5.error)return false;
      o.mesh=r5.mesh;o.bim.width=r5.bim.width;o.bim.depth=r5.bim.depth;o.bim.baseY=r5.bim.baseY;
      if(tp5)o.bim.section=JSON.parse(JSON.stringify(tp5));else delete o.bim.section;
      return true;
    }
    if(cat==='footing'||cat==='stripfooting'){   /* __acad3dV102 */
      var k2;
      for(k2 in t.params)if(t.params.hasOwnProperty(k2)&&k2!=='material')o.bim[k2]=t.params[k2];
      return bimRebuildFooting(o);
    }
    return false;
  }
  function bimApplyTypeToInstances(cat,typeId){
    var t=bimFindType(cat,typeId);
    if(!t)return {updated:0,skipped:0};
    var list=bimInstancesOfType(cat,typeId),updated=0,skipped=0,i;
    for(i=0;i<list.length;i++){
      var o=list[i];
      if(bimIsLocked(o)){skipped++;continue;}
      if(bimRebuildInstanceForType(o,t))updated++;else skipped++;
    }
    return {updated:updated,skipped:skipped};
  }
  function bimDuplicateTypeIn(cat,id,newName){
    var src=bimFindType(cat,id);
    if(!src)return null;
    var copy={id:'ty-'+Date.now().toString(36)+'-'+Math.floor(Math.random()*1e5),
      name:newName,params:JSON.parse(JSON.stringify(src.params))};
    A3D.types[cat].push(copy);
    return copy;
  }
  /* __acad3dV126: a category's types as options, grouped by material once there is more than one */
  function bimTypeOptionsHtml(cat,curId){
    var list=A3D.types[cat]||[],groups=[],by={},i;
    for(i=0;i<list.length;i++){
      var m=(list[i].params&&list[i].params.material)||'Other';
      if(!by[m]){by[m]=[];groups.push(m);}
      by[m].push(list[i]);
    }
    function opts(a){return a.map(function(x){return '<option value="'+x.id+'"'+(curId===x.id?' selected':'')+'>'+bimEsc(x.name)+'</option>';}).join('');}
    if(groups.length<2)return opts(list);
    return groups.map(function(g){return '<optgroup label="'+bimEsc(g)+'">'+opts(by[g])+'</optgroup>';}).join('');
  }
  function bimAssignTypeTo(o,cat,typeId){
    var t=bimFindType(cat,typeId);
    if(!t||!o.bim||o.bim.type!==cat)return false;
    o.bim.typeId=typeId;o.bim.typeCat=cat;
    return bimRebuildInstanceForType(o,t);
  }
  function bimFindType(cat,id){
    bimEnsureTypes();
    var list=A3D.types[cat]||[],i;
    for(i=0;i<list.length;i++)if(list[i].id===id)return list[i];
    return null;
  }
  function bimTypeNameOf(o){
    if(!o||!o.bim||!o.bim.typeId)return null;
    var t=bimFindType(o.bim.typeCat||o.bim.type||'wall',o.bim.typeId);
    return t?t.name:null;
  }
  function bimInstancesOfType(cat,id){
    return A3D.objs.filter(function(o){return o.bim&&(o.bim.typeCat||o.bim.type)===cat&&o.bim.typeId===id;});
  }
  // Propagate a type change to every instance. Locked and non-parametric (imported) walls are
  // skipped and reported rather than silently missed.
  function bimApplyWallTypeToInstances(typeId){
    var t=bimFindType('wall',typeId);
    if(!t)return {updated:0,skipped:0};
    var list=bimInstancesOfType('wall',typeId),updated=0,skipped=0,i;
    for(i=0;i<list.length;i++){
      var o=list[i];
      if(bimIsLocked(o)||!o.bim.centerline){skipped++;continue;}
      var res=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,
        t.params.thickness,o.bim.align,o.bim.closed,o.bim.bulges);
      if(res.error){skipped++;continue;}
      o.mesh=res.mesh;
      o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123 */
      bimAfterWallRebuild(o);   // __acad3dV51: re-cut this instance's openings after the rebuild
      updated++;
    }
    return {updated:updated,skipped:skipped};
  }
  function openTypeDlg(o){
    bimEnsureTypes();
    var cat=(o&&o.bim&&o.bim.type)||'wall';
    var def=TYPE_CATS[cat];
    if(!def){a3dToast('This object category has no editable types');return;}
    var t=bimEnsureObjType(o)||A3D.types[cat][0];
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    var prof=t.params&&t.params.profile;   /* __acad3dV126 */
    var paramRows=(prof?'<div class="a3d-dlgrow"><label>Section</label><span class="a3d-pstatic">'+bimEsc(BIM_PROFILE_SHAPES[prof.shape]||prof.shape)+'</span></div>':'')+
      def.typeParams.map(function(k){
      return '<div class="a3d-dlgrow"><label>'+k.charAt(0).toUpperCase()+k.slice(1)+' (m)</label>'+
        '<input type="number" step="any" min="0.001" data-typep="'+k+'" value="'+t.params[k]+'"'+
        (prof?' disabled title="Set by the section: choose another type to change it"':'')+'></div>';
    }).join('');
    /* __acad3dV59: Phase 51 type-level graphics rows. Same six fields as the instance-level
       override in the Properties palette, but written straight to t.graphics[mode][key] on OK --
       there is no "reset" concept at the type level, since the type itself IS the default an
       instance override resets back to. */
    var tGraphicsRows=['technical','presentation'].map(function(gm){
      var gg=t.graphics[gm];
      return '<div class="a3d-propnote" style="margin-top:8px">'+(gm==='technical'?'Technical':'Presentation')+' appearance</div>'+
        '<div class="a3d-dlgrow"><label>Line Weight (mm)</label><input type="number" step="0.05" min="0.05" data-tgfx="'+gm+':lineWeight" value="'+gg.lineWeight+'"></div>'+
        '<div class="a3d-dlgrow"><label>Line Color</label><input type="color" data-tgfx="'+gm+':lineColor" value="'+gg.lineColor+'"></div>'+
        '<div class="a3d-dlgrow"><label>Fill (Poch\u00e9)</label><input type="checkbox" data-tgfxfillon="'+gm+'"'+(gg.fill!=='none'?' checked':'')+
          '> <input type="color" data-tgfx="'+gm+':fill" value="'+(gg.fill!=='none'?gg.fill:'#cccccc')+'"'+(gg.fill==='none'?' disabled':'')+'></div>'+
        '<div class="a3d-dlgrow"><label>Pattern</label><select data-tgfx="'+gm+':pattern">'+BIM_HATCH_PATTERNS.map(function(p){
          return '<option value="'+p+'"'+(gg.pattern===p?' selected':'')+'>'+bimEsc(bimPatternLabel(p))+'</option>';
        }).join('')+'</select></div>'+
        // __acad3dV63: unlike the Properties palette (which re-renders on every change and so can
        // hide these when pattern is 'none'), this dialog is built once and read back on OK, so
        // the rows are always present -- a hidden input here would submit a stale value.
        '<div class="a3d-dlgrow"><label>Pattern Color</label><input type="color" data-tgfx="'+gm+':patternColor" value="'+gg.patternColor+'"></div>'+
        '<div class="a3d-dlgrow"><label>Pattern Scale</label><input type="number" step="0.1" min="0.1" max="8" data-tgfx="'+gm+':patternScale" value="'+gg.patternScale+'"></div>'+
        '<div class="a3d-dlgrow"><label>Opacity</label><input type="range" min="0" max="1" step="0.05" data-tgfx="'+gm+':opacity" value="'+gg.opacity+'"></div>'+
        '<div class="a3d-dlgrow"><label>Shadow</label><input type="checkbox" data-tgfx="'+gm+':shadow"'+(gg.shadow?' checked':'')+'></div>';
    }).join('');
    d.innerHTML='<div class="a3d-dlghd">Type Properties \u2014 '+def.label+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Family</label><span class="a3d-pstatic">'+bimEsc(def.family)+'</span></div>'+
      '<div class="a3d-dlgrow"><label>Type</label>'+
        '<select data-typesel>'+A3D.types[cat].map(function(x){
          return '<option value="'+x.id+'"'+(x.id===t.id?' selected':'')+'>'+bimEsc(x.name)+'</option>';}).join('')+'</select>'+
        '<button data-typedup title="Create an independent copy of this type">Duplicate</button></div>'+
      paramRows+
      '<div class="a3d-propnote">Type parameters are shared \u2014 changing one updates every instance of this type. Pinned instances are skipped.</div>'+
      tGraphicsRows+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);
    el.dlg=d;
    var curId=t.id;
    d.addEventListener('change',function(ev){
      var sel=ev.target&&ev.target.closest?ev.target.closest('[data-typesel]'):null;
      if(sel){
        pushUndo();
        if(bimAssignTypeTo(o,cat,sel.value)){
          if(cat==='wall')A3D.activeWallType=sel.value;
          refreshTree();paint();saveSoon();a3dToast('Type changed');
        }
        closeDlg();openTypeDlg(o);
        return;
      }
      /* __acad3dV59: Fill on/off just toggles the paired swatch's disabled state live -- the
         actual value isn't written until OK, same as every other row in this dialog. */
      var fo=ev.target&&ev.target.closest?ev.target.closest('[data-tgfxfillon]'):null;
      if(fo){
        var fom=fo.getAttribute('data-tgfxfillon');
        var sw=d.querySelector('[data-tgfx="'+fom+':fill"]');
        if(sw)sw.disabled=!fo.checked;
      }
    });
    d.addEventListener('click',function(ev){
      var dupBtn=ev.target&&ev.target.closest?ev.target.closest('[data-typedup]'):null;
      if(dupBtn){
        ev.preventDefault();
        var cur=bimFindType(cat,curId);
        var nm=window.prompt('Name for the duplicated type',(cur?cur.name:'Type')+' copy');
        if(nm===null)return;
        nm=String(nm).trim();
        if(!nm){a3dToast('Type name cannot be empty');return;}
        pushUndo();
        var cp=bimDuplicateTypeIn(cat,curId,nm);
        if(!cp){a3dToast('Could not duplicate that type');return;}
        bimAssignTypeTo(o,cat,cp.id);
        if(cat==='wall')A3D.activeWallType=cp.id;
        refreshTree();paint();saveSoon();
        a3dToast('Duplicated as "'+nm+'"');
        closeDlg();openTypeDlg(o);
        return;
      }
      var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;
      if(!b)return;
      if(b.getAttribute('data-a3dlg')!=='ok'){closeDlg();return;}
      var eb=document.getElementById('a3d-dlgerr'),i,vals={};
      for(i=0;i<def.typeParams.length;i++){
        var k=def.typeParams[i];
        var inp=d.querySelector('[data-typep="'+k+'"]');
        var v=inp?parseFloat(inp.value):NaN;
        if(!isFinite(v)||v<=0){eb.textContent=k.charAt(0).toUpperCase()+k.slice(1)+' must be a positive number';return;}
        vals[k]=v;
      }
      var tt=bimFindType(cat,curId);
      if(!tt){eb.textContent='Type no longer exists';return;}
      /* __acad3dV59: validate the graphics fields BEFORE pushUndo/mutation, same discipline as
         the geometry params above -- a bad value here should abort the whole OK, not partially
         apply thickness while leaving graphics untouched (or vice versa). */
      var gVals={technical:{},presentation:{}},gm2,gModesList=['technical','presentation'];
      for(i=0;i<gModesList.length;i++){
        gm2=gModesList[i];
        var lwInp=d.querySelector('[data-tgfx="'+gm2+':lineWeight"]');
        var lw=lwInp?parseFloat(lwInp.value):NaN;
        if(!isFinite(lw)||lw<=0){eb.textContent='Line weight must be a positive number';return;}
        gVals[gm2].lineWeight=lw;
        var lcInp=d.querySelector('[data-tgfx="'+gm2+':lineColor"]');
        gVals[gm2].lineColor=(lcInp&&bimValidGraphicsColor(lcInp.value))?lcInp.value:'#000000';
        var fillOnInp=d.querySelector('[data-tgfxfillon="'+gm2+'"]');
        var fillSwatch=d.querySelector('[data-tgfx="'+gm2+':fill"]');
        gVals[gm2].fill=(fillOnInp&&fillOnInp.checked&&fillSwatch&&bimValidGraphicsColor(fillSwatch.value))?fillSwatch.value:'none';
        var patInp=d.querySelector('[data-tgfx="'+gm2+':pattern"]');
        gVals[gm2].pattern=(patInp&&BIM_HATCH_PATTERNS.indexOf(patInp.value)>=0)?patInp.value:'none';
        // __acad3dV63: read back with the same clamping the sanitizer applies, so a value typed
        // into the dialog and a value loaded from a project file can never disagree.
        var pcInp=d.querySelector('[data-tgfx="'+gm2+':patternColor"]');
        gVals[gm2].patternColor=(pcInp&&bimValidGraphicsColor(pcInp.value)&&pcInp.value!=='none')?pcInp.value:'#555555';
        var psInp=d.querySelector('[data-tgfx="'+gm2+':patternScale"]');
        var ps=psInp?parseFloat(psInp.value):1;
        gVals[gm2].patternScale=(isFinite(ps)&&ps>0)?Math.max(0.1,Math.min(8,ps)):1;
        var opInp=d.querySelector('[data-tgfx="'+gm2+':opacity"]');
        var op=opInp?parseFloat(opInp.value):1;
        gVals[gm2].opacity=isFinite(op)?Math.max(0,Math.min(1,op)):1;
        var shInp=d.querySelector('[data-tgfx="'+gm2+':shadow"]');
        gVals[gm2].shadow=!!(shInp&&shInp.checked);
      }
      pushUndo();
      for(i=0;i<def.typeParams.length;i++)tt.params[def.typeParams[i]]=vals[def.typeParams[i]];
      for(i=0;i<gModesList.length;i++){
        gm2=gModesList[i];
        var gk;
        for(gk in gVals[gm2])if(gVals[gm2].hasOwnProperty(gk))bimSetTypeGraphics(cat,curId,gm2,gk,gVals[gm2][gk]);
      }
      var r=bimApplyTypeToInstances(cat,curId);
      closeDlg();
      refreshTree();paint();saveSoon();
      a3dToast('Type updated \u2014 '+r.updated+' instance(s) rebuilt'+(r.skipped?', '+r.skipped+' skipped':''));
    });
  }
  function bimSetWallTypeOf(o,typeId){
    var t=bimFindType('wall',typeId);
    if(!o||!o.bim||o.bim.type!=='wall'||!t)return false;
    if(bimIsLocked(o)){a3dToast(o.name+' is pinned \u2014 unpin to change its type');return false;}
    if(!o.bim.centerline){a3dToast('Imported wall has no parametric data \u2014 type cannot be applied');return false;}
    pushUndo();
    o.bim.typeId=typeId;o.bim.typeCat='wall';
    A3D.activeWallType=typeId;
    var res=bimBuildWallGeometry(o.bim.centerline,o.bim.baseY,o.bim.height,t.params.thickness,o.bim.align,o.bim.closed,o.bim.bulges);
    if(!res.error){
      o.mesh=res.mesh;o.bim=bimCarryBim(o.bim,res.bim);   /* __acad3dV123: the new type was set above */
      bimAfterWallRebuild(o);   // __acad3dV51: re-cut openings lost to the type rebuild
    }
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' \u2192 '+t.name);
    return true;
  }
  function bimRebuildWall(o,newThickness,newHeight,newAlign){
    if(!o||!o.bim||o.bim.type!=='wall')return false;
    if(!o.bim.centerline){a3dToast('This wall has no parametric data (likely imported) \u2014 thickness/height/alignment cannot be edited');return false;}
    if(bimIsLocked(o)){a3dToast(o.name+' is locked (Pin) \u2014 unlock it first to edit');return false;}
    var b=o.bim;
    var res=bimBuildWallGeometry(b.centerline,b.baseY,newHeight,newThickness,newAlign,b.closed,b.bulges);
    if(res.error){a3dToast(res.error);return false;}
    pushUndo();
    o.mesh=res.mesh;
    o.bim=bimCarryBim(b,res.bim);   /* __acad3dV123: it kept the level and dropped the type */
    bimAfterWallRebuild(o);   // __acad3dV51: re-cut openings lost to the thickness/height/align rebuild
    refreshTree();paint();saveSoon();
    a3dToast(o.name+' updated');
    return true;
  }
