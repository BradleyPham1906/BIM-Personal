#!/usr/bin/env python3
"""patch_phase105c.py -- V105 room colour fill on the canvas: off by default; ROOMCOLOR cycles
Department, Occupancy, off; colours assigned to the project's values in name order; a legend
built from what drawRooms actually drew, so it cannot disagree with the plan."""
NAME = 'patch_phase105c.py'
BASE = 'e725e0c1584ebfa665855ddd44402f2337cb9ae9fc058bf36652a22c5aa9e7e1'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)
rep(r"""  /* 101, 102 ... on the first level, 201 ... on the second: the next free number in that
""", r"""  /* ================= __acad3dV105: room colour fill =================
     Off by default, so a drawing made before this phase looks exactly as it did. When on, each
     room is filled by the value of ONE of its fields, Department or Occupancy. Colours go to the
     values the whole project has, in name order, so a department is one colour on every level.
     The legend lists what the last paint drew, recorded by the pass that drew it, so it cannot
     disagree with the plan. Past twelve values the colours repeat, and the legend shows it. */
  var BIM_SCHEME_COLS=['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5','#d9d9d9','#bc80bd','#ccebc5','#ffed6f'];
  var BIM_SCHEME_ALPHA=0.5;   /* the canvas only: the technical plan draws rooms over the model */
  function bimRoomSchemeLabel(by){return by==='dept'?'Department':(by==='occupancy'?'Occupancy':'');}
  function bimRoomSchemeValue(o,by){
    if(!o||o.t!=='room'||(by!=='dept'&&by!=='occupancy'))return '';
    return String(o[by]==null?'':o[by]).replace(/\s+/g,' ').replace(/^ | $/g,'');
  }
  function bimRoomSchemeValues(by){
    var seen={},out=[],i,v;
    for(i=0;i<A3D.objs.length;i++){
      v=bimRoomSchemeValue(A3D.objs[i],by);
      if(v&&!seen['k'+v.toLowerCase()]){seen['k'+v.toLowerCase()]=1;out.push(v);}
    }
    out.sort(function(a,b){a=a.toLowerCase();b=b.toLowerCase();return a<b?-1:(a>b?1:0);});
    return out;
  }
  function bimRoomSchemeMap(by){
    var vals=bimRoomSchemeValues(by),m={},i;
    for(i=0;i<vals.length;i++)m['k'+vals[i].toLowerCase()]={name:vals[i],col:BIM_SCHEME_COLS[i%BIM_SCHEME_COLS.length]};
    return m;
  }
  function bimRoomSchemeEntry(o,map){
    var v=bimRoomSchemeValue(o,A3D.roomScheme);
    if(!v)return null;
    return (map||bimRoomSchemeMap(A3D.roomScheme))['k'+v.toLowerCase()]||null;
  }
  /* The vector sinks: the same colour, opaque, because both draw room fills under the model. */
  function bimRoomSchemeGraphics(o,rg,pres){
    var e=bimRoomSchemeEntry(o,null),g;
    if(!e)return rg;
    g=bimResolveGraphics(o,pres?'presentation':'technical');
    g.fill=e.col;g.explicit=true;
    return g;
  }
  /* One undo step of its own: without it, undoing the colour fill would also undo the edit
     before it, because the snapshot that edit pushed is the one carrying the old setting. */
  function bimSetRoomScheme(by){
    by=(by==='dept'||by==='occupancy')?by:'';
    if(by!==(A3D.roomScheme||'')){pushUndo();A3D.roomScheme=by;}
    paint();saveSoon();
    var n=by?bimRoomSchemeValues(by).length:0;
    a3dToast(!by?'Room colour fill off':('Rooms filled by '+bimRoomSchemeLabel(by)+' — '+(n?(n+' value'+(n===1?'':'s')):'no room has one yet')));
    return by;
  }
  function bimCycleRoomScheme(){   /* ROOMCOLOR: Department, then Occupancy, then off */
    return bimSetRoomScheme(A3D.roomScheme==='dept'?'occupancy':(A3D.roomScheme==='occupancy'?'':'dept'));
  }
  function drawRoomSchemeLegend(ctx,V,W,H){
    var lg=A3D.pendingRoomLegend;
    A3D.pendingRoomLegend=null;A3D.lastRoomLegend=null;
    if(!lg||!lg.by||!lg.items.length||A3D.sheetCapture)return;
    ctx.save();
    try{
      var sr=bimSafeViewRect(),i,rowH=16,pad=8,sw=11,w,tw,h,x,y,ry;
      var title='Rooms by '+bimRoomSchemeLabel(lg.by);
      var rows=lg.items.slice().sort(function(a,b){a=a.name.toLowerCase();b=b.name.toLowerCase();return a<b?-1:(a>b?1:0);}).map(function(it){
        var r=lg.by==='occupancy'?bimOccLoadRow(it.name):null;
        return {name:it.name,col:it.col,note:r?(r.m2.toFixed(2)+' m²/p '+r.basis):''};
      });
      ctx.font='11px sans-serif';ctx.textBaseline='middle';ctx.textAlign='left';   /* the tag pass leaves it centred */
      w=ctx.measureText(title).width;
      for(i=0;i<rows.length;i++){tw=sw+6+ctx.measureText(rows[i].name).width+(rows[i].note?10+ctx.measureText(rows[i].note).width:0);if(tw>w)w=tw;}
      w=Math.ceil(w+pad*2);h=pad*2+rowH*(rows.length+1);
      x=sr.x+12;y=sr.y+12;
      ctx.globalAlpha=1;
      ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(x,y,w,h);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(x+0.5,y+0.5,w-1,h-1);
      ctx.fillStyle='#e8edf2';ctx.fillText(title,x+pad,y+pad+rowH/2);
      for(i=0;i<rows.length;i++){
        ry=y+pad+rowH*(i+1);
        ctx.globalAlpha=BIM_SCHEME_ALPHA;ctx.fillStyle=rows[i].col;ctx.fillRect(x+pad,ry+(rowH-sw)/2,sw,sw);
        ctx.globalAlpha=1;ctx.fillStyle='#e8edf2';ctx.fillText(rows[i].name,x+pad+sw+6,ry+rowH/2);
        if(rows[i].note){ctx.fillStyle='#9aa7b4';ctx.fillText(rows[i].note,x+pad+sw+6+ctx.measureText(rows[i].name).width+10,ry+rowH/2);}
      }
      A3D.lastRoomLegend={by:lg.by,title:title,items:rows,box:[x,y,w,h],align:ctx.textAlign};
    }catch(e){
      console.warn('[BIM] room legend',e);
      if(!A3D.roomLegendWarned){A3D.roomLegendWarned=true;a3dToast('The room colour legend could not be drawn');}
    }
    ctx.restore();
  }
  /* 101, 102 ... on the first level, 201 ... on the second: the next free number in that
""")
rep(r"""  function drawRooms(ctx,V,W,H){
    if(A3D.section)return;
    var i,o;
""", r"""  function drawRooms(ctx,V,W,H){
    A3D.pendingRoomLegend={by:A3D.roomScheme||'',items:[]};   /* __acad3dV105: rebuilt by every paint that draws rooms */
    if(A3D.section)return;
    var i,o;
    var schemeMap=A3D.roomScheme?bimRoomSchemeMap(A3D.roomScheme):null,legendSeen={};   /* __acad3dV105 */
""")
rep(r"""      ctx.globalAlpha=rrg?rrg.opacity:1;
      ctx.fillStyle=sel?'rgba(78,161,255,0.16)':((rrg&&rrg.fill!=='none')?rrg.fill:'rgba(127,212,196,0.14)');
      ctx.fill();
""", r"""      /* __acad3dV105: a room colour fill, when one is on, is what this view was asked to show, so
         it wins over the presentation fill; the selection highlight still wins over both. */
      var se=schemeMap?bimRoomSchemeEntry(o,schemeMap):null;
      if(se&&!legendSeen['k'+se.name]){legendSeen['k'+se.name]=1;A3D.pendingRoomLegend.items.push({name:se.name,col:se.col});}
      var schemeCol=(se&&!sel)?se.col:null;
      var roomFill=sel?'rgba(78,161,255,0.16)':(schemeCol||((rrg&&rrg.fill!=='none')?rrg.fill:'rgba(127,212,196,0.14)'));
      ctx.globalAlpha=(rrg?rrg.opacity:1)*(schemeCol?BIM_SCHEME_ALPHA:1);
      ctx.fillStyle=roomFill;
      ctx.fill();
      ctx.globalAlpha=rrg?rrg.opacity:1;
""")
rep(r"""      A3D.lastRoomStyle[o.id]={fill:sel?'rgba(78,161,255,0.16)':((rrg&&rrg.fill!=='none')?rrg.fill:'rgba(127,212,196,0.14)'),
""", r"""      A3D.lastRoomStyle[o.id]={fill:roomFill,scheme:schemeCol,schemeValue:se?se.name:'',   /* __acad3dV105 */
""")
rep(r"""    drawRoomTags(ctx,V,W,H);       /* __acad3dV101 */
""", r"""    drawRoomTags(ctx,V,W,H);       /* __acad3dV101 */
    drawRoomSchemeLegend(ctx,V,W,H);   /* __acad3dV105: the colour fill's legend, from what drawRooms just drew */
""")
rep(r"""    ['TAGALLROOMS',['TAGALL'],'roomtagall','Tag every untagged room on the active level'],
""", r"""    ['TAGALLROOMS',['TAGALL'],'roomtagall','Tag every untagged room on the active level'],
    ['ROOMCOLOR',['COLORFILL','ROOMCOLOUR'],'roomcolor','Fill rooms by Department, then by Occupancy, then off'],   /* __acad3dV105 */
""")
rep(r"""    roomtagall:function(){bimTagAllRooms();},         /* __acad3dV101 */
""", r"""    roomtagall:function(){bimTagAllRooms();},         /* __acad3dV101 */
    roomcolor:function(){bimCycleRoomScheme();},       /* __acad3dV105 */
""")
rep(r"""    site:{name:'Site'},
""", r"""    site:{name:'Site'},
    roomScheme:'',   /* __acad3dV105: '' off, 'dept' or 'occupancy' -- the room colour fill */
""")
out = t.encode('utf-8')
P.write_bytes(out)
print('%s  bytes %d -> %d  sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
