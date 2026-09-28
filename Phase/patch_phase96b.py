"""patch_phase96b.py -- __acad3dV96: the hatch object.

A hatch is a closed region with a pattern. It stores its own pattern fields rather than using
graphicsOverride, for one reason: graphicsOverride is per-MODE, and a hatch is explicit drawn
geometry that must look the same in Technical and Presentation alike. Every pattern the library
has drawn until now has been a presentation-mode appearance override, gated on
A3D.presentMode in all three sinks; a hatch cannot inherit that gate.

The fields still go through bimApplyGraphicsFields, so a hatch's pattern, colour, scale and
angle are validated and clamped by exactly the code that validates an override's. One
appearance contract, two ways of reaching it.

The boundary carries bulges, so a hatch traced round a curved region is bounded by the curve.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '90f784ae5f6b6712bfd36534564ab4d572d83bb0e20bcb530b2b8857d8416241'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # ---- the entity and its appearance
    ("""  /* ================= __acad3dV94: construction lines =================""",
     """  /* ================= __acad3dV96: the hatch object =================

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
    A3D.objs.push(o);
    return o;
  }
  /* ================= __acad3dV94: construction lines ================="""),

    # ---- viewport: hatch draws UNDER the linework, as AutoCAD's does
    ("""  /* __acad3dV94: construction geometry, drawn under the model the way grids are, dashed so
     it never reads as a wall. */
  function drawClines(ctx,V,W,H){""",
     """  /* __acad3dV96: hatch, drawn under the linework. This is the one pattern sink that is NOT
     gated on presentation mode, because a hatch is geometry the drafter placed rather than an
     appearance the mode chose. */
  function drawHatches(ctx,V,W,H){
    var i,o,ring,sp,k,rg,fill;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsHatch(o))continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(!bimObjectVisibleOnLevel(o))continue;
      ring=bimHatchOutline(o);
      if(ring.length<3)continue;
      var q=bimObjOffset(o);
      sp=[];
      for(k=0;k<ring.length;k++)
        sp.push(toScreen([ring[k][0]+q[0],(o.y||0)+q[1],ring[k][1]+q[2]],V,W,H));
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(sp[0][0],sp[0][1]);
      for(k=1;k<sp.length;k++)ctx.lineTo(sp[k][0],sp[k][1]);
      ctx.closePath();
      rg=bimHatchGraphics(o);
      if(rg.fill&&rg.fill!=='none'){ctx.fillStyle=rg.fill;ctx.fill();}
      fill=bimCanvasPatternFill(ctx,rg);
      if(fill){ctx.fillStyle=fill;ctx.fill();}
      /* The boundary is drawn only while selected. AutoCAD's hatch has no visible edge of its
         own -- the edge belongs to whatever bounded it -- and drawing one would put a line in
         the drawing that is not in the model. */
      if(o.id===A3D.sel){
        ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.4;
        ctx.setLineDash([6,4]);ctx.stroke();ctx.setLineDash([]);
      }
      ctx.restore();
    }
  }
  /* __acad3dV94: construction geometry, drawn under the model the way grids are, dashed so
     it never reads as a wall. */
  function drawClines(ctx,V,W,H){"""),

    ("""    drawGrids(ctx,V,W,H);
    drawClines(ctx,V,W,H);         /* __acad3dV94: construction geometry, under the model */""",
     """    drawGrids(ctx,V,W,H);
    drawHatches(ctx,V,W,H);        /* __acad3dV96: under the linework, as AutoCAD draws it */
    drawClines(ctx,V,W,H);         /* __acad3dV94: construction geometry, under the model */"""),

    # ---- picking: inside the region, smallest first, below the linework
    ("""    return best||bimPickCline(x,y)||bimPickRoom(x,y)||bimPickDim(x,y)||bimPickText(x,y);""",
     """    return best||bimPickCline(x,y)||bimPickRoom(x,y)||bimPickHatch(x,y)||bimPickDim(x,y)||bimPickText(x,y);"""),

    ("""  function bimPickRoom(x,y){""",
     """  /* __acad3dV96: a hatch is picked by clicking INSIDE it, like a room, and it is tested
     after rooms so a room label is never swallowed by a hatch lying under it. */
  function bimPickHatch(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var candidates=[],i,o,k;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsHatch(o))continue;
      var lyr=bimLayerOf(o);
      if(lyr&&(lyr.visible===false||lyr.locked))continue;
      var ring=bimHatchOutline(o);
      if(ring.length<3)continue;
      var sp=[];
      for(k=0;k<ring.length;k++)sp.push(toScreen(bimWorldPt(o,ring[k],o.y),V,W,H));
      if(bimPointInPoly([x,y],sp))candidates.push({o:o,area:bimPolyArea(sp)});
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return a.area-b.area;});
    return candidates[0].o;
  }
  function bimPickRoom(x,y){"""),

    # ---- bounds, so Align and the drawing extent see it
    ("""    else if(bimIsCline(o))pts=[o.p];                 /* __acad3dV94: the root, the one""",
     """    else if(bimIsHatch(o))pts=bimHatchOutline(o);    /* __acad3dV96 */
    else if(bimIsCline(o))pts=[o.p];                 /* __acad3dV94: the root, the one"""),

    # ---- copy translates the ring
    ("""    if(bimIsCline(o)){          /* __acad3dV94: a translation moves the root, never the angle */""",
     """    if(bimIsHatch(o)){          /* __acad3dV96 */
      copy=JSON.parse(JSON.stringify(o));
      copy.id='a3d-'+Date.now().toString(36)+'-'+(A3D.seq++);
      copy.pts=o.pts.map(function(p){return [p[0]+dx,p[1]+dz];});
      copy.name=o.name+' copy';
      return copy;
    }
    if(bimIsCline(o)){          /* __acad3dV94: a translation moves the root, never the angle */"""),

    # ---- properties and the schedule label
    ("""    }else if(bimIsCline(o)){                    /* __acad3dV94 */""",
     """    }else if(bimIsHatch(o)){                    /* __acad3dV96 */
      dims+=bimPropText('Pattern',bimPatternLabel(o.pattern));
      dims+=bimPropText('Angle',(o.patternAngle||0).toFixed(1)+' deg');
      dims+=bimPropText('Scale',(o.patternScale||1).toFixed(2));
      dims+=bimPropText('Area',bimHatchArea(o).toFixed(3)+' m2');
      dims+=bimPropText('Boundary points',o.pts.length);
    }else if(bimIsCline(o)){                    /* __acad3dV94 */"""),

    ("""    if(bimIsCline(o))return 'Lines : Construction Lines';   /* __acad3dV94 */""",
     """    if(bimIsHatch(o))return 'Patterns : Hatches';           /* __acad3dV96 */
    if(bimIsCline(o))return 'Lines : Construction Lines';   /* __acad3dV94 */"""),

    # ---- the three export sinks
    ("""      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        /* R12 ASCII has no XLINE or RAY entity (both arrived in R13), so what goes out is the
           clipped LINE. Stated here rather than silently approximated. */""",
     """      }else if(bimIsHatch(o)){                  /* __acad3dV96 */
        /* R12 ASCII has no HATCH entity either -- it arrived in R13, and R12 drawings carry
           hatching as exploded lines. This export writes the BOUNDARY as a closed polyline and
           nothing else, which is true rather than approximate: the region is there, the
           pattern is not. Generating the pattern as clipped LINE entities is real work and is
           its own phase. */
        poly(o.pts,true,lay,o.bulges||null);
        stats.hatch=(stats.hatch||0)+1;
      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        /* R12 ASCII has no XLINE or RAY entity (both arrived in R13), so what goes out is the
           clipped LINE. Stated here rather than silently approximated. */"""),

    ("""      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var svCL=bimClineVisibleSeg(o,null);""",
     """      }else if(bimIsHatch(o)){                  /* __acad3dV96: rg is the hatch's OWN
        appearance, passed whatever the mode is, because a hatch is geometry and not a
        presentation override. forFill true is what turns the pattern overlay on. */
        poly(bimHatchOutline(o),true,lay,o.id,bimHatchGraphics(o),true);
      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var svCL=bimClineVisibleSeg(o,null);"""),

    ("""      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var shCL=bimClineVisibleSeg(o,null);""",
     """      }else if(bimIsHatch(o)){                  /* __acad3dV96 */
        poly(bimHatchOutline(o),true,o.id,o.y,bimHatchGraphics(o),true);
      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var shCL=bimClineVisibleSeg(o,null);"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
