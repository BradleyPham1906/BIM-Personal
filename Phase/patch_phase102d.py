"""patch_phase102d.py -- __acad3dV102: footings in the plan exports, and turned columns too.

A footing had no 2D footprint, so DXF, SVG and the sheet export skipped it. Adding it found the
same fault one level up: all three exporters drew a COLUMN's footprint axis-aligned, ignoring the
orientation V81 gave columns -- a column turned 30 degrees exported square to the axes. The
rectangle is now built by one function, bimRectFootprint, which the column builder, the footing
builder and all three exporters use (law 3), so the plan, the model and every export agree.

A footing records its plan footprint when it is built (a pad's turned rectangle; a strip's two
edges, from the same offsets the wall builder uses), and the exporters draw that.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '887d32a778d6f1962aff695e44bcfee7ae511db6ef9a5e8f882bff53125cb1d6'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

QUAD = "[[c[0]-hw,c[1]-hd],[c[0]+hw,c[1]-hd],[c[0]+hw,c[1]+hd],[c[0]-hw,c[1]+hd]]"
assert txt.count(QUAD) == 3
txt = txt.replace(QUAD, "bimRectFootprint(c,b.width,b.depth,b.rotation||0)")

EDITS = [
    ("""  function bimBuildColumnGeometry(center,y0,w,dep,h,rot){
    var hw=w/2,hd=dep/2;
    var quad=[[-hw,-hd],[hw,-hd],[hw,hd],[-hw,hd]];
    var th=rot||0,cs=Math.cos(th),sn=Math.sin(th),qi;
    for(qi=0;qi<quad.length;qi++){
      var qx=quad[qi][0],qz=quad[qi][1];
      quad[qi]=[center[0]+qx*cs-qz*sn,center[1]+qx*sn+qz*cs];
    }
    var mesh;""",
     """  /* __acad3dV102: the one turned rectangle -- column and footing builders and every exporter */
  function bimRectFootprint(center,w,dep,rot){
    var hw=w/2,hd=dep/2;
    var quad=[[-hw,-hd],[hw,-hd],[hw,hd],[-hw,hd]];
    var th=rot||0,cs=Math.cos(th),sn=Math.sin(th),qi;
    for(qi=0;qi<quad.length;qi++){
      var qx=quad[qi][0],qz=quad[qi][1];
      quad[qi]=[center[0]+qx*cs-qz*sn,center[1]+qx*sn+qz*cs];
    }
    return quad;
  }
  function bimBuildColumnGeometry(center,y0,w,dep,h,rot){
    var quad=bimRectFootprint(center,w,dep,rot);
    var mesh;"""),
    ("""      return {mesh:res.mesh,set:{center:[c[0],c[1]],topY:top,baseY:top-b.thickness,rotation:rot}};""",
     """      return {mesh:res.mesh,set:{center:[c[0],c[1]],topY:top,baseY:top-b.thickness,rotation:rot,
              plan:[bimRectFootprint(c,b.width,b.length,rot)]}};"""),
    ("""    if(res.error)return res;
    return {mesh:res.mesh,set:{centerline:cl.map(function(p){return [p[0],p[1]];}),bulges:bul,closed:closed,""",
     """    if(res.error)return res;
    var flat=bimHasBulge(bul)?bimFlattenPoly(cl,bul,closed):cl;
    var ra=bimOffsetRing(flat,hw+off,closed),rb=bimOffsetRing(flat,-(hw-off),closed);
    var plan=closed?[ra,rb]:[ra.concat(rb.slice().reverse())];
    return {mesh:res.mesh,set:{plan:plan,centerline:cl.map(function(p){return [p[0],p[1]];}),bulges:bul,closed:closed,"""),
    ("""        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,lay);
      }else{
        stats.skipped++;""",
     """        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,lay);
      }else if(bimIsFooting(o)&&b.plan){   /* __acad3dV102 */
        var fpi;
        for(fpi=0;fpi<b.plan.length;fpi++)poly(b.plan[fpi],true,lay);
      }else{
        stats.skipped++;"""),
    ("""        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,lay,o.id,rg,true);
      }else{
        stats.skipped++;""",
     """        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,lay,o.id,rg,true);
      }else if(bimIsFooting(o)&&b.plan){   /* __acad3dV102 */
        var fps;
        for(fps=0;fps<b.plan.length;fps++)poly(b.plan[fps],true,lay,o.id,rg,true);
      }else{
        stats.skipped++;"""),
    ("""        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,o.id,b.baseY,rg,true);
      }
    }""",
     """        poly(bimRectFootprint(c,b.width,b.depth,b.rotation||0),true,o.id,b.baseY,rg,true);
      }else if(bimIsFooting(o)&&b.plan){   /* __acad3dV102 */
        var fpv;
        for(fpv=0;fpv<b.plan.length;fpv++)poly(b.plan[fpv],true,o.id,b.baseY,rg,true);
      }
    }"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
