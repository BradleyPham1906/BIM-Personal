"""patch_phase94d.py -- __acad3dV94: drawing a line that has no ends.

Four consumers, one clipper. The viewport, the DXF, the SVG and the sheet all call
bimClineVisibleSeg against the same derived drawing extent, so no two can disagree about where
a construction line appears to stop.

Two things stated rather than assumed:

  - The extent is DERIVED from the drawing (bimDrawingExtent2D), not a constant. A construction
    line drawn across a 3 m room and one drawn across a 400 m bridge both run visibly past the
    geometry, and neither needs a number someone chose once.
  - R12 ASCII DXF has no XLINE or RAY entity -- they arrived in R13. So the export writes the
    CLIPPED LINE, which is what R12 can carry. Writing a group code the format does not define
    would produce a file that opens and is quietly wrong.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '75da56e35726685c4e8f51422f67bb71e5e16ac2aac904c0a6a7af5f78da3917'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

EDITS = [
    # ---- viewport
    ("""  function drawSketches(ctx,V,W,H){""",
     """  /* __acad3dV94: construction geometry, drawn under the model the way grids are, dashed so
     it never reads as a wall. */
  function drawClines(ctx,V,W,H){
    var box=null,i,o,seg,a,b,q;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsCline(o))continue;
      var lyr=bimLayerOf(o);
      if(lyr&&lyr.visible===false)continue;
      if(!bimObjectVisibleOnLevel(o))continue;
      if(!box)box=bimDrawingExtent2D();
      seg=bimClineVisibleSeg(o,box);
      if(!seg)continue;
      q=bimObjOffset(o);
      a=toScreen([seg[0][0]+q[0],(o.y||0)+q[1],seg[0][1]+q[2]],V,W,H);
      b=toScreen([seg[1][0]+q[0],(o.y||0)+q[1],seg[1][1]+q[2]],V,W,H);
      ctx.save();
      ctx.setLineDash([9,5]);
      ctx.strokeStyle=(o.id===A3D.sel)?'#4ea1ff':(o.col||'#8a7fd0');
      ctx.lineWidth=1.1;
      ctx.beginPath();ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1]);ctx.stroke();
      ctx.setLineDash([]);
      /* The ROOT is marked, because on an xline it is the only point that means anything and
         it is the one a drafter snaps back to. */
      var rp=toScreen([o.p[0]+q[0],(o.y||0)+q[1],o.p[1]+q[2]],V,W,H);
      ctx.fillStyle=(o.id===A3D.sel)?'#4ea1ff':(o.col||'#8a7fd0');
      ctx.fillRect(rp[0]-2.5,rp[1]-2.5,5,5);
      ctx.restore();
    }
  }
  function drawSketches(ctx,V,W,H){"""),

    ("""    drawGrids(ctx,V,W,H);
    drawSketches(ctx,V,W,H);""",
     """    drawGrids(ctx,V,W,H);
    drawClines(ctx,V,W,H);         /* __acad3dV94: construction geometry, under the model */
    drawSketches(ctx,V,W,H);"""),

    # ---- DXF
    ("""      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var dxPM=bimPointMarkerSegs(o.pts[0]),dxPK;
        for(dxPK=0;dxPK<dxPM.length;dxPK++)line(dxPM[dxPK][0],dxPM[dxPK][1],lay);""",
     """      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        /* R12 ASCII has no XLINE or RAY entity (both arrived in R13), so what goes out is the
           clipped LINE. Stated here rather than silently approximated. */
        var dxCL=bimClineVisibleSeg(o,null);
        if(dxCL)line(dxCL[0],dxCL[1],lay);
      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var dxPM=bimPointMarkerSegs(o.pts[0]),dxPK;
        for(dxPK=0;dxPK<dxPM.length;dxPK++)line(dxPM[dxPK][0],dxPM[dxPK][1],lay);"""),

    # ---- SVG export
    ("""      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var svPM=bimPointMarkerSegs(o.pts[0]),svPK;
        for(svPK=0;svPK<svPM.length;svPK++)line(svPM[svPK][0],svPM[svPK][1],lay,o.id,rg);""",
     """      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var svCL=bimClineVisibleSeg(o,null);
        if(svCL)line(svCL[0],svCL[1],lay,o.id,rg);
      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var svPM=bimPointMarkerSegs(o.pts[0]),svPK;
        for(svPK=0;svPK<svPM.length;svPK++)line(svPM[svPK][0],svPM[svPK][1],lay,o.id,rg);"""),

    # ---- sheet viewport SVG
    ("""      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var shPM=bimPointMarkerSegs(o.pts[0]),shPK;
        for(shPK=0;shPK<shPM.length;shPK++)ln(shPM[shPK][0],shPM[shPK][1],o.id,o.y,rg);""",
     """      }else if(bimIsCline(o)){                  /* __acad3dV94 */
        var shCL=bimClineVisibleSeg(o,null);
        if(shCL)ln(shCL[0],shCL[1],o.id,o.y,rg);
      }else if(bimIsPoint(o)){                  /* __acad3dV93 */
        var shPM=bimPointMarkerSegs(o.pts[0]),shPK;
        for(shPK=0;shPK<shPM.length;shPK++)ln(shPM[shPK][0],shPM[shPK][1],o.id,o.y,rg);"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:64])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
