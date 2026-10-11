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
  pick    a band is picked by its inside, last -- after the model, the lines and words, the grids --
          and a selected band's outline is lit: a slope class has no line of its own to click
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

# ---- polylines: drawn, and picked by their segments ----
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
        for(i=0;i+1<lp.length;i++)if(lp[i][2]>0.5&&lp[i+1][2]>0.5)hit.segs.push([lp[i][0],lp[i][1],lp[i+1][0],lp[i+1][1]]);
        if(g.closed&&lp.length>2&&lp[0][2]>0.5&&lp[lp.length-1][2]>0.5)hit.segs.push([lp[lp.length-1][0],lp[lp.length-1][1],lp[0][0],lp[0][1]]);
      }
    }else if(g.kind==='segs'){
      ctx.beginPath();
      for(i=0;i+1<P.length;i+=2){""")

# ---- turned, mirrored or scaled; fitted to ----
rep("    if(g.bands)g.bands.forEach(function(B){B.pts=B.pts.map(P);});\n",
    "    if(g.bands)g.bands.forEach(function(B){if(B.pts)B.pts=B.pts.map(P);if(B.rings)B.rings=B.rings.map(function(Rg){return Rg.map(P);});});   /* __acad3dV165 */\n"
    "    if(g.lines)g.lines=g.lines.map(function(Ln){return Ln.map(P);});\n")
# ---- a band selected: its outline lit, as a line's is ----
rep("    if(g.marks)for(i=0;i<g.marks.length;i++){\n      sp=toScreen(bimDgW(o,g.marks[i].p),V,W,H);if(sp[2]<=0.5)continue;\n",
    """    if(sel&&g.bands){   /* __acad3dV165: a band selected -- a slope class has no line of its own -- its outline lit,
                           on a dark edge: the selection's yellow is near the fills' own (5 to 10% is #fecc5c) */
      ctx.beginPath();
      for(i=0;i<g.bands.length;i++){
        var Rb=g.bands[i]?(g.bands[i].rings||(g.bands[i].pts?[g.bands[i].pts]:[])):[],rb,qb,Pb;
        for(rb=0;rb<Rb.length;rb++){if(!Rb[rb]||Rb[rb].length<3)continue;Pb=[];for(qb=0;qb<Rb[rb].length;qb++)Pb.push(toScreen(bimDgW(o,Rb[rb][qb]),V,W,H));bimDgSub(ctx,Pb);}
      }
      ctx.setLineDash([]);ctx.globalAlpha=1;
      ctx.strokeStyle='#1b1f24';ctx.lineWidth=5;ctx.stroke();
      ctx.strokeStyle='#ffd166';ctx.lineWidth=2;ctx.stroke();ctx.globalAlpha=a;
    }
    if(g.marks)for(i=0;i<g.marks.length;i++){
      sp=toScreen(bimDgW(o,g.marks[i].p),V,W,H);if(sp[2]<=0.5)continue;
""")

# ---- a band picked by its inside, last: only where nothing else is under the pointer ----
rep("     model and so picked before it. A band, a fill or a shadow is picked by its lines and words only,\n     so it never covers the model it lies over. */\n",
    "     model and so picked before it. A band, a fill or a shadow is picked here by its lines and words\n"
    "     only, so it never covers the model it lies over; __acad3dV165: a band's inside, last of all\n"
    "     (bimPickBand). */\n")
rep("  /* turned, mirrored or scaled: the plan coordinates of every point, label and symbol */\n  function bimDgTransformed(dg,tp){\n",
    """  /* __acad3dV165: a band -- a slope or aspect class, a pond, a flood zone, a road's noise -- picked by
     its inside. The click asks it last, after the model, the lines and words over it and the grids, so
     a band never covers what lies on it; a class with no line of its own is still a click away. The
     top one: the analysis drawn last, then its highest class, as bimDgDrawBands lays them. */
  function bimPickBand(x,y){
    var L=bimDgDiags(),G={},order=[],V,W,H,i,j,k,m;
    for(i=0;i<L.length;i++){
      var o=L[i],gb=o.dg.g.bands;
      if(!gb||!gb.length||!bimLayerShown(o)||!bimLayerPickable(o))continue;
      if(!G.hasOwnProperty(o.dg.a)){G[o.dg.a]=[];order.push(o.dg.a);}
      for(j=0;j<gb.length;j++)if(gb[j])G[o.dg.a].push({o:o,B:gb[j],n:G[o.dg.a].length});
    }
    if(!order.length)return null;
    V=camVecs(A3D.cam);W=cvW();H=cvH();
    for(i=order.length-1;i>=0;i--){
      var T=G[order[i]].slice().sort(function(p,q){return ((q.B.lv||0)-(p.B.lv||0))||(q.n-p.n);});
      for(j=0;j<T.length;j++){
        var R=T[j].B.rings||(T[j].B.pts?[T[j].B.pts]:[]),inside=false;
        for(k=0;k<R.length;k++){
          if(!R[k]||R[k].length<3)continue;
          var P=[],front=true;
          for(m=0;m<R[k].length;m++){var sp=toScreen(bimDgW(T[j].o,R[k][m]),V,W,H);if(sp[2]<=0.5){front=false;break;}P.push(sp);}
          if(front&&inPoly(x,y,P))inside=!inside;   /* even-odd, as it is filled */
        }
        if(inside)return T[j].o;
      }
    }
    return null;
  }
  /* turned, mirrored or scaled: the plan coordinates of every point, label and symbol */
  function bimDgTransformed(dg,tp){
""")
rep("      if(gpk)refreshLevels();\n      /* __acad3dV134: under them all, the data layers */\n      A3D_DATA.sel=(o||gpk)?null:bimDataPick(xy[0],xy[1]);\n",
    "      if(gpk)refreshLevels();\n"
    "      /* __acad3dV165: under the grids, a band of the site analysis, by its inside */\n"
    "      var bpk=(o||gpk)?null:bimPickBand(xy[0],xy[1]);\n"
    "      if(bpk){o=bpk;A3D.sel=o.id;A3D.selSet=[o.id];}\n"
    "      /* __acad3dV134: under them all, the data layers */\n"
    "      A3D_DATA.sel=(o||gpk)?null:bimDataPick(xy[0],xy[1]);\n")
rep("    (g.bands||[]).forEach(function(B){(B.pts||[]).forEach(function(p){P.push(p);});});\n",
    "    (g.bands||[]).forEach(function(B){(B.pts||[]).forEach(function(p){P.push(p);});(B.rings||[]).forEach(function(Rg){Rg.forEach(function(p){P.push(p);});});});   /* __acad3dV165 */\n"
    "    (g.lines||[]).forEach(function(Ln){Ln.forEach(function(p){P.push(p);});});\n")

# ---- the legend: laid out before the words are placed, which keep clear of it; when the view is
#      short the sources go, then the analyses shown longest ago, said so ----
rep("  function drawDiagramLegend(ctx,V,W,H){\n    A3D_DG.legend=null;\n    if(A3D.sheetCapture||A3D_PLOT.on)return;\n    var D=bimDgState(),blocks=[],i,sr;\n    if(D.legendOff)return;\n    for(i=0;i<BIM_DG_AN.length;i++){\n      var A=BIM_DG_AN[i],R=D.runs[A.id];\n      if(!R)continue;\n      if(!bimDgDiags(A.id).some(function(o){return bimLayerShown(o);}))continue;   /* a layer off or frozen, its own or one above it: none of it shown */\n      blocks.push({title:A.name,rows:(R.legend||[]).slice(0,8),src:R.source||'',drawn:[]});\n    }\n    if(!blocks.length)return;\n    sr=bimSafeViewRect();   /* asked only with a key to place, as the other keys do: it warns when the chrome covers the view */\n    if(sr.w<620)return;   /* a phone's view: each analysis's row in Analyze carries its key */\n    ctx.save();\n    try{\n      var pad=8,rowH=15,sw=12,maxW=Math.round(Math.min(300,Math.max(170,sr.w*0.3))),inner=maxW-2*pad,ops=[],y=pad,x,j,b,w=0;\n      for(i=0;i<blocks.length;i++){\n        b=blocks[i];if(i)y+=6;\n        ctx.font='bold 11px sans-serif';\n        var tt=bimDgFit(ctx,b.title,inner);ops.push({k:'t',t:tt,x:pad,y:y+rowH/2});b.tt=tt;w=Math.max(w,ctx.measureText(tt).width);y+=rowH;\n        ctx.font='11px sans-serif';x=pad;\n        for(j=0;j<b.rows.length;j++){\n          var r=b.rows[j],nm=r.short||r.name,iw=sw+4+ctx.measureText(nm).width;\n          if(x>pad&&x+iw>pad+inner){x=pad;y+=rowH;}\n          ops.push({k:'r',r:r,t:nm,x:x,y:y+rowH/2});b.drawn.push(nm);w=Math.max(w,x+iw-pad);x+=iw+10;\n        }\n        if(b.rows.length)y+=rowH;\n        if(b.src){ctx.font='10px sans-serif';var st=bimDgFit(ctx,b.src,inner);ops.push({k:'s',t:st,x:pad,y:y+rowH/2-1});b.st=st;w=Math.max(w,ctx.measureText(st).width);y+=rowH-2;}\n      }\n      w=Math.ceil(Math.min(maxW,w+2*pad));var h=y+pad,X=sr.x+sr.w-w-12,Y=sr.y+12;\n      if(X+w>W-84&&Y<108)Y=108;   /* under the north arrow */\n",
    """  /* __acad3dV165: the key's layout, apart from its drawing, so the words placed before it can keep clear
     of its box. What does not fit a short view goes: the sources first, then whole analyses, those
     shown longest ago first, and a line says how many; the rest keep their order. When each analysis
     was last shown is noticed here, frame by frame, however its layer came on. */
  function bimDgLegendLayout(ctx,W,H){
    if(A3D.sheetCapture||A3D_PLOT.on)return null;
    var D=bimDgState(),blocks=[],i,sr,seen=A3D_DG.seen||(A3D_DG.seen={}),at=A3D_DG.at||(A3D_DG.at={}),tick=null;
    if(D.legendOff)return null;
    for(i=0;i<BIM_DG_AN.length;i++){
      var A=BIM_DG_AN[i],R=D.runs[A.id],on=!!R&&bimDgDiags(A.id).some(function(o){return bimLayerShown(o);});   /* a layer off or frozen, its own or one above it: none of it shown */
      if(on&&!seen[A.id]){if(tick===null)tick=A3D_DG.tick=(A3D_DG.tick||0)+1;at[A.id]=tick;}   /* shown again: the most recent */
      seen[A.id]=on;
      if(on)blocks.push({title:A.name,rows:(R.legend||[]).slice(0,8),src:R.source||'',drawn:[],at:at[A.id]||0,i:blocks.length});
    }
    if(!blocks.length)return null;
    sr=bimSafeViewRect();   /* asked only with a key to place, as the other keys do: it warns when the chrome covers the view */
    if(sr.w<620)return null;   /* a phone's view: each analysis's row in Analyze carries its key */
    ctx.save();
    try{
      var pad=8,rowH=15,sw=12,maxW=Math.round(Math.min(300,Math.max(170,sr.w*0.3))),inner=maxW-2*pad,j,b;
      var lay=function(withSrc,list){   /* the key for these blocks, with or without their sources */
        var ops=[],y=pad,x,w=0,k;
        for(k=0;k<list.length;k++){
          b=list[k];if(k)y+=6;b.drawn=[];b.tt='';b.st='';
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
        var mt='';
        if(list.length<blocks.length){ctx.font='10px sans-serif';mt=bimDgFit(ctx,'+ '+(blocks.length-list.length)+' more: their keys are in Analyze',inner);y+=6;ops.push({k:'s',t:mt,x:pad,y:y+rowH/2-1});w=Math.max(w,ctx.measureText(mt).width);y+=rowH-2;}
        return {ops:ops,w:Math.ceil(Math.min(maxW,w+2*pad)),h:y+pad,src:withSrc,list:list,mt:mt};
      };
      var Y=sr.y+12;
      if(sr.x+sr.w-12>W-84&&Y<108)Y=108;   /* under the north arrow */
      var avail=sr.y+sr.h-12-Y,LY=lay(true,blocks),gone={},n=0,
        drop=blocks.slice().sort(function(p,q){return (p.at-q.at)||(q.i-p.i);});
      if(LY.h>avail)LY=lay(false,blocks);
      while(LY.h>avail&&n<blocks.length-1){gone[drop[n++].i]=1;LY=lay(false,blocks.filter(function(bb){return !gone[bb.i];}));}
      LY.X=sr.x+sr.w-LY.w-12;LY.Y=Y;LY.all=blocks.length;
      return LY;
    }finally{ctx.restore();}
  }
  function drawDiagramLegend(ctx,V,W,H){
    A3D_DG.legend=null;
    var LY=(A3D_DG.lyCtx===ctx&&A3D_DG.lyFrame===A3D.frames)?A3D_DG.ly:bimDgLegendLayout(ctx,W,H);   /* laid out already this frame, as the words were placed */
    A3D_DG.lyCtx=null;
    if(!LY)return;
    ctx.save();
    try{
      var sw=12,ops=LY.ops,w=LY.w,h=LY.h,X=LY.X,Y=LY.Y,i;
""")
rep("      A3D_DG.legend={box:[X,Y,w,h],blocks:blocks.map(function(bb){return {title:bb.tt,rows:bb.drawn,src:bb.st||''};})};   /* what was drawn, as drawn */\n",
    "      A3D_DG.legend={box:[X,Y,w,h],blocks:LY.list.map(function(bb){return {title:bb.tt,rows:bb.drawn,src:bb.st||''};}),more:LY.all-LY.list.length,moreText:LY.mt,sources:LY.src};   /* what was drawn, as drawn */\n")

# ---- the words keep clear of what is drawn over them later in the frame ----
rep("  function bimDgPlaceLabels(ctx,Q){\n    var placed=[],i,k;\n",
    """  /* __acad3dV165: where the words keep clear of, as it is drawn over them later in the frame: the north
     arrow in plan, its N all round it; the view cube in 3D, with its home button; the key */
  function bimDgKeepClear(W,H){
    var B=[],L=A3D_DG.ly;
    if(A3D.sheetCapture)return B;
    if(bimCameraIsPlan())B.push([W-90,36,90,84]);
    if(!A3D.flat)B.push([W-130,8,130,116]);
    if(L)B.push([L.X,L.Y,L.w,L.h]);
    return B;
  }
  function bimDgPlaceLabels(ctx,Q,keep){
    var placed=(keep||[]).slice(),i,k;
    A3D_DG.labelBoxes=[];
""")
rep("      q.hit.boxes.push(bx);\n",
    "      q.hit.boxes.push(bx);A3D_DG.labelBoxes.push(bx);   /* __acad3dV165 */\n")
rep("      if(Q.length)bimDgPlaceLabels(ctx,Q);\n",
    "      if(over){A3D_DG.ly=bimDgLegendLayout(ctx,W,H);A3D_DG.lyCtx=ctx;A3D_DG.lyFrame=A3D.frames;}   /* __acad3dV165: the key first, for the words to keep clear of */\n"
    "      if(Q.length)bimDgPlaceLabels(ctx,Q,bimDgKeepClear(W,H));\n")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
