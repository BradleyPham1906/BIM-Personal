  /* ================= __acad3dV96: the hatch object =================

     A closed region plus a pattern. Unlike every pattern this library has drawn so far, a hatch
     is not a presentation-mode appearance override -- it is drawn geometry, and it renders in
     Technical mode too. */
  function bimIsHatch(o){
    return !!(o&&o.t==='hatch'&&o.pts&&o.pts.length>=2);
  }
  /* The appearance a hatch resolves to. Built from the hard defaults and then filtered through
     bimApplyGraphicsFields, so a hatch's pattern, colour, scale and angle are validated and
     clamped by exactly the code that validates an object's graphics override. */
  function bimHatchGraphics(o){
    var g=bimDefaultGraphics();
    g.explicit=true;   /* __acad3dV96: drawn geometry, not a presentation-mode appearance */
    if(!o)return g;
    bimApplyGraphicsFields({pattern:o.pattern,patternColor:o.patternColor,
      patternScale:o.patternScale,patternAngle:o.patternAngle,
      fill:o.fill,opacity:o.opacity,lineColor:o.lineColor},g);
    return g;
  }
  function bimHatchOutline(o){
    if(!o||!o.pts)return [];
    return bimFlattenPoly(o.pts,o.bulges||null,true);
  }
  function bimHatchArea(o){
    if(!o||!o.pts)return 0;
    return bimBulgedArea(o.pts,o.bulges||null,true);
  }
  function bimAddHatch(pts,bulges,y,opts){
    opts=opts||{};
    if(!pts||pts.length<2)return null;
    A3D.counts.hatch=(A3D.counts.hatch||0)+1;
    var o={
      id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),
      t:'hatch',name:'Hatch '+A3D.counts.hatch,col:'#8fb3c4',
      pos:[0,0,0],pts:pts.map(function(p){return [p[0],p[1]];}),
      y:(typeof y==='number')?y:bimGetActiveLevel().elev,
      layer:(opts.layer===undefined?A3D.activeLayer:opts.layer),
      pattern:opts.pattern||'diagonal',
      patternColor:opts.patternColor||'#555555',
      patternScale:(opts.patternScale>0)?opts.patternScale:1,
      patternAngle:(typeof opts.patternAngle==='number'&&isFinite(opts.patternAngle))?
        (((opts.patternAngle%180)+180)%180):0
    };
    if(bimHasBulge(bulges))o.bulges=bulges.slice();
    if(opts.sourceId){o.sourceId=opts.sourceId;o.sourceType=opts.sourceType||null;}   /* __acad3dV97 */
    A3D.objs.push(o);
    return o;
  }
