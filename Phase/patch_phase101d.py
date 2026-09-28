"""patch_phase101d.py -- __acad3dV101: exports say what the plan says.

The three exporters (DXF, SVG, PDF sheet) each wrote a room's label themselves: name and area,
at the average of the vertices. So an export disagreed with the plan three ways once rooms had
numbers and tags -- no number, a point outside an L-shaped room, and a SECOND label under every
tag. The label text and point now come from one function each, the same ones the canvas uses,
the label is left out when the room is tagged, and a tag exports as its own text.

A copied room also gets the next free number rather than none.
"""
import hashlib, pathlib
SRC = pathlib.Path('canvas_v10.html')
BASE = '079fa52bfaf50c7cecca4ec90d44b7e126f7540ff79ea0b4b13755f897081a94'
txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'
EDITS = [
    ("""  function bimIsRoomTag(o){return !!(o&&o.t==='roomtag'&&o.pt&&o.roomId);}""",
     """  function bimIsRoomTag(o){return !!(o&&o.t==='roomtag'&&o.pt&&o.roomId);}
  /* A room's own label, for every place that writes one (plan exports). LOCAL coordinates, like
     the room's points, so an exporter treats it exactly as it treats them. */
  function bimRoomLabelText(o){return (o.number?o.number+' ':'')+o.name+' '+(o.area||0).toFixed(2)+'m2';}
  function bimRoomLabelPoint(o){
    var ip=bimInteriorPoint(o.pts);
    if(ip)return ip;
    var cx=0,cz=0,i;
    for(i=0;i<o.pts.length;i++){cx+=o.pts[i][0];cz+=o.pts[i][1];}
    return [cx/o.pts.length,cz/o.pts.length];
  }"""),
    ("""        text([cx/o.pts.length,cz/o.pts.length],o.name+' '+o.area.toFixed(2)+'m2',0.25,lay);""",
     """        if(!bimRoomTagged(o.id))text(bimRoomLabelPoint(o),bimRoomLabelText(o),0.25,lay);   /* __acad3dV101 */"""),
    ("""        text([cx/o.pts.length,cz/o.pts.length],o.name+' '+o.area.toFixed(2)+'m2',0.25,lay,o.id,rg);""",
     """        if(!bimRoomTagged(o.id))text(bimRoomLabelPoint(o),bimRoomLabelText(o),0.25,lay,o.id,rg);   /* __acad3dV101 */"""),
    ("""        txt([cx/o.pts.length,cz/o.pts.length],o.name+' '+o.area.toFixed(2)+'m2',3.0,o.id,o.y,rg);""",
     """        if(!bimRoomTagged(o.id))txt(bimRoomLabelPoint(o),bimRoomLabelText(o),3.0,o.id,o.y,rg);   /* __acad3dV101 */"""),
    ("""      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay);""",
     """      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay);
      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay);"""),
    ("""      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay,o.id,rg);""",
     """      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))text(o.pt,bimRoomTagText(o),0.25,lay,o.id,rg);
      }else if(o.t==='text'){
        text(o.pt,o.text,0.25,lay,o.id,rg);"""),
    ("""      }else if(o.t==='text'){
        txt(o.pt,o.text,3.0,o.id,o.y,rg);""",
     """      }else if(o.t==='roomtag'){   /* __acad3dV101 */
        if(bimAnnotDrawable(o))txt(o.pt,bimRoomTagText(o),3.0,o.id,o.y,rg);
      }else if(o.t==='text'){
        txt(o.pt,o.text,3.0,o.id,o.y,rg);"""),
    ("""        pts:o.pts.map(function(p){return [p[0]+dx,p[1]+dz];}),y:o.y,area:o.area,levelId:o.levelId,layer:o.layer};""",
     """        pts:o.pts.map(function(p){return [p[0]+dx,p[1]+dz];}),y:o.y,area:o.area,levelId:o.levelId,layer:o.layer,
        number:bimNextRoomNumber(o.levelId),dept:o.dept,occupancy:o.occupancy,finishFloor:o.finishFloor,
        finishWall:o.finishWall,finishCeiling:o.finishCeiling,finishBase:o.finishBase};   /* __acad3dV101 */"""),
]
for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)
SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
