"""patch_phase88c.py -- Phase 88 part 3: the DXF round trip.

Export writes group code 42 per vertex; import reads it, and an incoming ARC entity becomes a
two-vertex bulged polyline instead of a fan of chords. An arc can now leave this app and come
back as the same arc.
"""
import hashlib, pathlib, sys

BASE = 'f567e5a1efdf3ead2a423baaa8617c5a3af4fd3cb9093bc4c9bb11b3c76d6f2a'
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')

src = P.read_text(encoding='utf-8')
h0 = hashlib.sha256(src.encode('utf-8')).hexdigest()
assert h0 == BASE, 'baseline hash mismatch: %s' % h0
b0 = len(src.encode('utf-8'))

reps = []

# ---- 1. export: emit the bulge -----------------------------------------------------------
reps.append(("""    function poly(pts,closed,lay){
      out+=P(0,'LWPOLYLINE')+P(8,lay)+P(100,'AcDbEntity')+P(100,'AcDbPolyline')+P(90,pts.length)+P(70,closed?1:0);
      var q;
      for(q=0;q<pts.length;q++)out+=P(10,pts[q][0].toFixed(6))+P(20,pts[q][1].toFixed(6));
      stats.lwpolyline++;
    }""",
"""    /* __acad3dV88: bulges is optional and parallel to pts. Group code 42 follows its vertex,
       which is where the DXF reference puts it, and is omitted entirely when the segment is
       straight - so a polyline with no arcs produces byte-identical output to before. */
    function poly(pts,closed,lay,bulges){
      out+=P(0,'LWPOLYLINE')+P(8,lay)+P(100,'AcDbEntity')+P(100,'AcDbPolyline')+P(90,pts.length)+P(70,closed?1:0);
      var q;
      for(q=0;q<pts.length;q++){
        out+=P(10,pts[q][0].toFixed(6))+P(20,pts[q][1].toFixed(6));
        var bq=bimBulgeAt(bulges,q);
        if(Math.abs(bq)>BIM_BULGE_EPS)out+=P(42,bq.toFixed(8));
      }
      stats.lwpolyline++;
    }""", 1))

# ---- 2. export: a sketch hands over its own vertices and bulges, not a flattened copy -------
reps.append(("""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        poly(bimFlattenSketch(o),o.closed!==false,lay);   /* __acad3dV88 */""",
"""      }else if(o.t==='sketch'&&o.pts&&o.pts.length>=2){
        /* __acad3dV88: DXF carries the arc itself. This is the one consumer that does NOT
           flatten, because the format it writes stores exactly what this app stores. */
        poly(o.pts,o.closed!==false,lay,o.bulges);""", 1))

# ---- 3. import: read code 42 --------------------------------------------------------------
reps.append(("""      }else if(t==='LWPOLYLINE'){
        var flags2=dxfNum(r.items,70,0);
        var xs=dxfAllNums(r.items,10),ys=dxfAllNums(r.items,20);
        var pts=[],k;for(k=0;k<Math.min(xs.length,ys.length);k++)pts.push([xs[k],ys[k]]);
        if(pts.length>=2)entities.push({type:'LWPOLYLINE',closed:!!(flags2&1),layer:layerName,color:colOverride,pts:pts});""",
"""      }else if(t==='LWPOLYLINE'){
        var flags2=dxfNum(r.items,70,0);
        var xs=dxfAllNums(r.items,10),ys=dxfAllNums(r.items,20);
        var pts=[],k;for(k=0;k<Math.min(xs.length,ys.length);k++)pts.push([xs[k],ys[k]]);
        /* __acad3dV88: a bulge belongs to the vertex it FOLLOWS, and straight vertices carry no
           42 at all, so the codes cannot be read as a parallel list - they are walked in
           document order alongside the 10s, which is the only reading that survives a file
           where some segments are arcs and some are not. */
        var bulges=null,vi=-1,ri;
        for(ri=0;ri<r.items.length;ri++){
          var code=r.items[ri][0];
          if(code===10)vi++;
          else if(code===42&&vi>=0){
            if(!bulges){bulges=[];for(k=0;k<pts.length;k++)bulges.push(0);}
            if(vi<bulges.length)bulges[vi]=parseFloat(r.items[ri][1])||0;
          }
        }
        if(pts.length>=2)entities.push({type:'LWPOLYLINE',closed:!!(flags2&1),layer:layerName,color:colOverride,pts:pts,bulges:bulges});""", 1))

# ---- 4. import: build the sketch with its bulges, and keep an ARC as an arc -----------------
reps.append(("""          }else if(e.type==='LWPOLYLINE'||e.type==='POLYLINE'){
            var pts=e.pts.map(function(p){return [p[0]*scale,p[1]*scale];});
            o=bimMakeImportedSketch(pts,baseY,!!e.closed);""",
"""          }else if(e.type==='LWPOLYLINE'||e.type==='POLYLINE'){
            var pts=e.pts.map(function(p){return [p[0]*scale,p[1]*scale];});
            /* __acad3dV88: bulge is scale-invariant (it is tan of a quarter of the swept
               angle), so it is carried across unscaled while the points are scaled. */
            o=bimMakeImportedSketch(pts,baseY,!!e.closed,e.bulges);""", 1))

reps.append(("""          }else if(e.type==='ARC'){
            var apts=[],a1=e.a1*Math.PI/180,a2=e.a2*Math.PI/180;
            if(a2<a1)a2+=Math.PI*2;
            var segN=Math.max(6,Math.round((a2-a1)/(Math.PI/16)));
            for(k=0;k<=segN;k++){var at=a1+(a2-a1)*(k/segN);apts.push([(e.c[0]+Math.cos(at)*e.r)*scale,(e.c[1]+Math.sin(at)*e.r)*scale]);}
            o=bimMakeImportedSketch(apts,baseY+(e.c[2]||0)*scale,false);""",
"""          }else if(e.type==='ARC'){
            /* __acad3dV88: an ARC is now STORED as an arc - two vertices and one bulge -
               instead of being tessellated into a fan of chords on the way in. DXF arcs are
               always counter-clockwise from a1 to a2, so the sweep is positive by definition
               and the bulge is tan(sweep/4). Before this phase an imported arc could never
               leave this app as an arc again. */
            var a1=e.a1*Math.PI/180,a2=e.a2*Math.PI/180;
            if(a2<a1)a2+=Math.PI*2;
            var sweep=a2-a1;
            var ap1=[(e.c[0]+Math.cos(a1)*e.r)*scale,(e.c[1]+Math.sin(a1)*e.r)*scale];
            var ap2=[(e.c[0]+Math.cos(a2)*e.r)*scale,(e.c[1]+Math.sin(a2)*e.r)*scale];
            o=bimMakeImportedSketch([ap1,ap2],baseY+(e.c[2]||0)*scale,false,[Math.tan(sweep/4),0]);""", 1))

# ---- 5. bimMakeImportedSketch accepts bulges -----------------------------------------------
OLD_MK = "  function bimMakeImportedSketch("
assert src.count(OLD_MK) == 1
i = src.index(OLD_MK)
j = src.index("\n  function ", i + 10)
print('--- bimMakeImportedSketch before ---')
print(src[i:j])

out = src
for old, new, want in reps:
    got = out.count(old)
    assert got == want, 'occurrence count %d (wanted %d) for: %s' % (got, want, old[:70])
    out = out.replace(old, new, want)

b1 = len(out.encode('utf-8'))
P.write_text(out, encoding='utf-8')
print('%d replacements' % len(reps))
print('bytes before %d  after %d  (+%d)' % (b0, b1, b1 - b0))
print('sha256 %s' % hashlib.sha256(out.encode('utf-8')).hexdigest())
