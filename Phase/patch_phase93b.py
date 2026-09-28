"""patch_phase93b.py -- __acad3dV93: the viewport draws the CURVE.

Found while making CIRCLE a real circle. drawSketchPath is the main viewport's sketch
renderer and it was handed o.pts raw -- no flattening -- so every committed arc sketch since
V88 has drawn in the viewport as its CHORD. The V90 rubber band flattened and the committed
object did not, which is the interface disagreeing with the model in the one place a drafter
looks first, and it is why a two-vertex circle would otherwise have appeared as a line.

The fix takes bulges into the function so the path is built from the flattened curve while the
grips stay on the real vertices. There is no second flattener: it calls bimFlattenPoly, the
same one the DXF, SVG and sheet emitters call.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '9163712d6fd5c269818cd5b5d873b38cdce62fd78fde7a267b3614bb0572e3de'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD_FN = """  function drawSketchPath(ctx,V,W,H,pts,y0,col,closed,prog,off){
    if(!pts||pts.length<1)return;
    var i,p,sp=[],q=off||[0,0,0];
    for(i=0;i<pts.length;i++){
      p=toScreen([pts[i][0]+q[0],(y0||0)+q[1],pts[i][1]+q[2]],V,W,H);sp.push(p);
    }
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(sp[0][0],sp[0][1]);
    for(i=1;i<sp.length;i++)ctx.lineTo(sp[i][0],sp[i][1]);
    if(closed){
      ctx.closePath();
      ctx.fillStyle='rgba(94,196,184,0.10)';
      ctx.fill();
    }
    if(prog)ctx.setLineDash([5,4]);
    ctx.strokeStyle=col;
    ctx.lineWidth=1.6;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle=col;
    for(i=0;i<sp.length;i++)ctx.fillRect(sp[i][0]-2.5,sp[i][1]-2.5,5,5);
    ctx.restore();
  }"""

NEW_FN = """  /* __acad3dV93: bulges is the arc data, and the PATH is built from the flattened curve while
     the GRIPS stay on the stored vertices. Before this the viewport drew o.pts raw, so a
     committed arc appeared as its chord while the rubber band that produced it appeared
     curved. Same flattener as every other consumer -- bimFlattenPoly -- so the viewport cannot
     drift from the DXF, the SVG or the sheet. */
  function drawSketchPath(ctx,V,W,H,pts,y0,col,closed,prog,off,bulges){
    if(!pts||pts.length<1)return;
    var i,p,sp=[],gp=[],q=off||[0,0,0],y=(y0||0)+q[1];
    var path=bimHasBulge(bulges)?bimFlattenPoly(pts,bulges,!!closed):pts;
    for(i=0;i<path.length;i++){
      p=toScreen([path[i][0]+q[0],y,path[i][1]+q[2]],V,W,H);sp.push(p);
    }
    for(i=0;i<pts.length;i++){
      p=toScreen([pts[i][0]+q[0],y,pts[i][1]+q[2]],V,W,H);gp.push(p);
    }
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(sp[0][0],sp[0][1]);
    for(i=1;i<sp.length;i++)ctx.lineTo(sp[i][0],sp[i][1]);
    if(closed){
      ctx.closePath();
      ctx.fillStyle='rgba(94,196,184,0.10)';
      ctx.fill();
    }
    if(prog)ctx.setLineDash([5,4]);
    ctx.strokeStyle=col;
    ctx.lineWidth=1.6;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle=col;
    for(i=0;i<gp.length;i++)ctx.fillRect(gp[i][0]-2.5,gp[i][1]-2.5,5,5);
    ctx.restore();
  }"""

OLD_CALL = """      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':'#5ec4b8',(o.closed!==false),false,bimObjOffset(o));"""
NEW_CALL = """      drawSketchPath(ctx,V,W,H,o.pts,o.y,(o.id===A3D.sel)?'#4ea1ff':'#5ec4b8',(o.closed!==false),false,bimObjOffset(o),o.bulges);"""

OLD_PREV = """    if(A3D.sk&&A3D.sk.pts.length)drawSketchPath(ctx,V,W,H,
      bimFlattenPoly(A3D.sk.pts,A3D.sk.bulges,false),A3D.sk.y,'#ffd479',false,true);"""
NEW_PREV = """    if(A3D.sk&&A3D.sk.pts.length)drawSketchPath(ctx,V,W,H,
      A3D.sk.pts,A3D.sk.y,'#ffd479',false,true,null,A3D.sk.bulges);"""

for old, new in ((OLD_FN, NEW_FN), (OLD_CALL, NEW_CALL), (OLD_PREV, NEW_PREV)):
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:60])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
