"""patch_phase165a.py -- V165: site analysis in the model II, land and water: the engine.

reference/research-site-analysis-in-model.md, section 2. The land and water analyses draw what the
V164 engine did not hold:
  lines   several polylines in one element -- a contour level, the divides of the catchments
  rings   a band of several rings, holes and islands read even-odd -- a slope class is many areas
  groups  each analysis's bands on a canvas of their own, at its own opacity: slope under noise
          must not read as one map; a class's fill one path, so no hairline between its cells
  fill    a band takes its element's fill, so a class restyled in Properties is drawn restyled
  hidden  an analysis that covers the ground (slope, aspect) starts with its layer off: two
          coverages read as neither
  legend  with many analyses shown the key drops its sources, then its last blocks, naming how many
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '8443b9f531a762f90e397c6e8f117d63a4ebd8b7ac687020f9d31a11a831e097'   # the V164 build

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('baseline sha mismatch: %s' % sha)
txt = raw.decode('utf-8')


def rep(old, new, count=1):
    global txt
    n = txt.count(old)
    assert n == count, 'anchor count %d (wanted %d): %r' % (n, count, old[:80])
    txt = txt.replace(old, new)


# ---- the element's format: polylines, and bands of rings ----
rep("                bands  [{lv, col, pts}]: areas in classes (a road's noise), the higher class over\n",
    "                bands  [{lv, col, pts}]: areas in classes (a road's noise), the higher class over\n"
    "                       __acad3dV165: or {lv, col, rings:[[p...]...]}, an area of many parts, holes\n"
    "                       and islands read even-odd (a slope class); drawn in its element's fill\n"
    "                lines  lines [[p...]...]: several polylines (a contour level, the divides)\n")

# ---- an analysis that covers the ground starts hidden ----
rep("    return bimDgLayer(a,'Site analysis - '+A.name,A.col,'root',false);\n",
    "    return bimDgLayer(a,'Site analysis - '+A.name,A.col,'root',!!A.hidden);   /* __acad3dV165: a coverage starts hidden: one reads at a time */\n")

# ---- the bands: each analysis on its own canvas, a class one path ----
rep("""  /* bands -- a road's noise classes -- of every element on one canvas, class by class, so where two
     overlap the higher class shows; the context's buildings cut out, the colour lying on the ground
     between them; laid on the view at one opacity */
  function bimDgDrawBands(ctx,V,W,H,L){
    var T=[],c2,i,j,k,a=1,gy=0;
    for(i=0;i<L.length;i++){
      var o=L[i],s=o.dg.s||{},al=s.op===undefined?1:s.op;
      if(!i)a=bimLayerAlpha(o)*(s.fop===undefined?0.45:s.fop);
      for(j=0;j<o.dg.g.bands.length;j++){
        var B=o.dg.g.bands[j],P=[];
        if(!B||!B.pts||B.pts.length<3)continue;
        for(k=0;k<B.pts.length;k++)P.push(toScreen(bimDgW(o,B.pts[k]),V,W,H));
        T.push({P:P,col:B.col,lv:B.lv||0,al:al});
        gy=bimDgW(o,B.pts[0])[1];
      }
    }
    if(!T.length)return;
    T.sort(function(x,y){return x.lv-y.lv;});
    c2=bimDgOff(ctx,'bandCv');
    for(i=0;i<T.length;i++){bimDgPath(c2,T[i].P,true);c2.globalAlpha=T[i].al;c2.fillStyle=T[i].col;c2.fill('nonzero');}
""",
    """  /* bands -- a road's noise classes, a slope class -- each analysis's on a canvas of its own, class
     by class, so where two overlap the higher class shows; the context's buildings cut out, the
     colour lying on the ground between them; each analysis laid on the view at its own opacity.
     __acad3dV165: grouped by analysis, so slope and noise do not read as one map */
  function bimDgDrawBands(ctx,V,W,H,L){
    var G={},order=[],i;
    for(i=0;i<L.length;i++){var ga=L[i].dg.a;if(!G.hasOwnProperty(ga)){G[ga]=[];order.push(ga);}G[ga].push(L[i]);}
    for(i=0;i<order.length;i++)bimDgDrawBandGroup(ctx,V,W,H,G[order[i]]);
  }
  /* one ring as a sub-path of the path being built, broken where a point is behind the eye */
  function bimDgSub(c,P){
    var on=false,q;
    for(q=0;q<P.length;q++){
      if(P[q][2]<=0.5){on=false;continue;}
      if(on)c.lineTo(P[q][0],P[q][1]);else{c.moveTo(P[q][0],P[q][1]);on=true;}
    }
    c.closePath();
  }
  function bimDgDrawBandGroup(ctx,V,W,H,L){
    var T=[],c2,i,j,k,m,a=1,gy=0;
    for(i=0;i<L.length;i++){
      var o=L[i],s=o.dg.s||{},al=s.op===undefined?1:s.op;
      if(!i)a=bimLayerAlpha(o)*(s.fop===undefined?0.45:s.fop);
      for(j=0;j<o.dg.g.bands.length;j++){
        var B=o.dg.g.bands[j],R=B?(B.rings||(B.pts?[B.pts]:null)):null,PP=[];
        if(!R)continue;
        for(k=0;k<R.length;k++){
          if(!R[k]||R[k].length<3)continue;
          var P=[];for(m=0;m<R[k].length;m++)P.push(toScreen(bimDgW(o,R[k][m]),V,W,H));
          PP.push(P);gy=bimDgW(o,R[k][0])[1];
        }
        if(PP.length)T.push({PP:PP,col:(B.rings&&s.fill)?s.fill:B.col,lv:B.lv||0,al:al,eo:!!B.rings});
      }
    }
    if(!T.length)return;
    T.sort(function(x,y){return x.lv-y.lv;});
    c2=bimDgOff(ctx,'bandCv');
    for(i=0;i<T.length;i++){
      c2.beginPath();for(k=0;k<T[i].PP.length;k++)bimDgSub(c2,T[i].PP[k]);
      c2.globalAlpha=T[i].al;c2.fillStyle=T[i].col;c2.fill(T[i].eo?'evenodd':'nonzero');
      if(T[i].eo){c2.strokeStyle=T[i].col;c2.lineWidth=1;c2.stroke();}   /* over the hairline where two classes meet */
    }
""")

# ---- polylines: drawn, headed, picked by their segments ----
rep("""    if(g.kind==='segs'){
      ctx.beginPath();
      for(i=0;i+1<P.length;i+=2){""",
    """    if(g.kind==='lines'){   /* __acad3dV165: several polylines -- a contour level, the divides */
      var LL=g.lines||[],ln,lp;
      for(ln=0;ln<LL.length;ln++){
        lp=[];for(i=0;i<LL[ln].length;i++)lp.push(toScreen(bimDgW(o,LL[ln][i]),V,W,H));
        if(lp.length<2)continue;
        if(sel){bimDgPath(ctx,lp,g.closed);ctx.setLineDash([]);ctx.strokeStyle='#ffd166';ctx.lineWidth=(s.w||1.2)+4;ctx.globalAlpha=Math.min(1,a+0.3);ctx.stroke();ctx.globalAlpha=a;}
        if(s.stroke){bimDgPath(ctx,lp,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.2;ctx.stroke();ctx.setLineDash([]);}
        if(s.head&&!g.closed)bimDgHead(ctx,lp,s);
        for(i=0;i+1<lp.length;i++)if(lp[i][2]>0.5&&lp[i+1][2]>0.5)hit.segs.push([lp[i][0],lp[i][1],lp[i+1][0],lp[i+1][1]]);
        if(g.closed&&lp.length>2&&lp[0][2]>0.5&&lp[lp.length-1][2]>0.5)hit.segs.push([lp[lp.length-1][0],lp[lp.length-1][1],lp[0][0],lp[0][1]]);
      }
    }else if(g.kind==='segs'){
      ctx.beginPath();
      for(i=0;i+1<P.length;i+=2){""")
rep("""  /* the words, the most telling first: the compass points, then each analysis's own labels, then the""",
    """  /* an arrowhead at a polyline's end, on the screen, where the water or the wind runs out */
  function bimDgHead(ctx,P,s){
    var e=P[P.length-1],b=P[P.length-2];
    if(!(e[2]>0.5&&b[2]>0.5))return;
    var ang=Math.atan2(e[1]-b[1],e[0]-b[0]),hl=7+(s.w||1.2)*2;
    ctx.beginPath();ctx.moveTo(e[0],e[1]);ctx.lineTo(e[0]-hl*Math.cos(ang-0.42),e[1]-hl*Math.sin(ang-0.42));ctx.lineTo(e[0]-hl*Math.cos(ang+0.42),e[1]-hl*Math.sin(ang+0.42));ctx.closePath();
    ctx.fillStyle=s.stroke||'#e8edf2';ctx.fill();
  }
  /* the words, the most telling first: the compass points, then each analysis's own labels, then the""")

# ---- turned, mirrored or scaled; fitted to ----
rep("    if(g.bands)g.bands.forEach(function(B){B.pts=B.pts.map(P);});\n",
    "    if(g.bands)g.bands.forEach(function(B){if(B.pts)B.pts=B.pts.map(P);if(B.rings)B.rings=B.rings.map(function(Rg){return Rg.map(P);});});   /* __acad3dV165 */\n"
    "    if(g.lines)g.lines=g.lines.map(function(Ln){return Ln.map(P);});\n")
rep("    (g.bands||[]).forEach(function(B){(B.pts||[]).forEach(function(p){P.push(p);});});\n",
    "    (g.bands||[]).forEach(function(B){(B.pts||[]).forEach(function(p){P.push(p);});(B.rings||[]).forEach(function(Rg){Rg.forEach(function(p){P.push(p);});});});   /* __acad3dV165 */\n"
    "    (g.lines||[]).forEach(function(Ln){Ln.forEach(function(p){P.push(p);});});\n")

# ---- the legend: with many analyses shown, the sources go, then the last blocks, said so ----
rep("""    ctx.save();
    try{
      var pad=8,rowH=15,sw=12,maxW=Math.round(Math.min(300,Math.max(170,sr.w*0.3))),inner=maxW-2*pad,ops=[],y=pad,x,j,b,w=0;
      for(i=0;i<blocks.length;i++){
        b=blocks[i];if(i)y+=6;
        ctx.font='bold 11px sans-serif';
        var tt=bimDgFit(ctx,b.title,inner);ops.push({k:'t',t:tt,x:pad,y:y+rowH/2});b.tt=tt;w=Math.max(w,ctx.measureText(tt).width);y+=rowH;
        ctx.font='11px sans-serif';x=pad;
        for(j=0;j<b.rows.length;j++){
          var r=b.rows[j],nm=r.short||r.name,iw=sw+4+ctx.measureText(nm).width;
          if(x>pad&&x+iw>pad+inner){x=pad;y+=rowH;}
          ops.push({k:'r',r:r,t:nm,x:x,y:y+rowH/2});b.drawn.push(nm);w=Math.max(w,x+iw-pad);x+=iw+10;
        }
        if(b.rows.length)y+=rowH;
        if(b.src){ctx.font='10px sans-serif';var st=bimDgFit(ctx,b.src,inner);ops.push({k:'s',t:st,x:pad,y:y+rowH/2-1});b.st=st;w=Math.max(w,ctx.measureText(st).width);y+=rowH-2;}
      }
      w=Math.ceil(Math.min(maxW,w+2*pad));var h=y+pad,X=sr.x+sr.w-w-12,Y=sr.y+12;
      if(X+w>W-84&&Y<108)Y=108;   /* under the north arrow */
""",
    """    ctx.save();
    try{
      var pad=8,rowH=15,sw=12,maxW=Math.round(Math.min(300,Math.max(170,sr.w*0.3))),inner=maxW-2*pad,j,b;
      /* the key laid out for the first nb blocks, with or without their sources; __acad3dV165: what does
         not fit the view goes -- the sources first, then the last blocks, a line saying how many */
      var lay=function(withSrc,nb){
        var ops=[],y=pad,x,w=0,k;
        for(k=0;k<nb;k++){
          b=blocks[k];if(k)y+=6;b.drawn=[];b.tt='';b.st='';
          ctx.font='bold 11px sans-serif';
          var tt=bimDgFit(ctx,b.title,inner);ops.push({k:'t',t:tt,x:pad,y:y+rowH/2});b.tt=tt;w=Math.max(w,ctx.measureText(tt).width);y+=rowH;
          ctx.font='11px sans-serif';x=pad;
          for(j=0;j<b.rows.length;j++){
            var r=b.rows[j],nm=r.short||r.name,iw=sw+4+ctx.measureText(nm).width;
            if(x>pad&&x+iw>pad+inner){x=pad;y+=rowH;}
            ops.push({k:'r',r:r,t:nm,x:x,y:y+rowH/2});b.drawn.push(nm);w=Math.max(w,x+iw-pad);x+=iw+10;
          }
          if(b.rows.length)y+=rowH;
          if(withSrc&&b.src){ctx.font='10px sans-serif';var st=bimDgFit(ctx,b.src,inner);ops.push({k:'s',t:st,x:pad,y:y+rowH/2-1});b.st=st;w=Math.max(w,ctx.measureText(st).width);y+=rowH-2;}
        }
        if(nb<blocks.length){ctx.font='10px sans-serif';var mt=bimDgFit(ctx,'+ '+(blocks.length-nb)+' more: their keys are in Analyze',inner);y+=6;ops.push({k:'s',t:mt,x:pad,y:y+rowH/2-1});w=Math.max(w,ctx.measureText(mt).width);y+=rowH-2;}
        return {ops:ops,w:Math.ceil(Math.min(maxW,w+2*pad)),h:y+pad,src:withSrc,nb:nb};
      };
      var Y=sr.y+12;
      if(sr.x+sr.w-12>W-84&&Y<108)Y=108;   /* under the north arrow */
      var avail=sr.y+sr.h-12-Y,LY=lay(true,blocks.length);
      if(LY.h>avail)LY=lay(false,blocks.length);
      while(LY.h>avail&&LY.nb>1)LY=lay(false,LY.nb-1);
      var ops=LY.ops,w=LY.w,h=LY.h,X=sr.x+sr.w-w-12;
""")
rep("      A3D_DG.legend={box:[X,Y,w,h],blocks:blocks.map(function(bb){return {title:bb.tt,rows:bb.drawn,src:bb.st||''};})};   /* what was drawn, as drawn */\n",
    "      A3D_DG.legend={box:[X,Y,w,h],blocks:blocks.slice(0,LY.nb).map(function(bb){return {title:bb.tt,rows:bb.drawn,src:bb.st||''};}),more:blocks.length-LY.nb,sources:LY.src};   /* what was drawn, as drawn */\n")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
