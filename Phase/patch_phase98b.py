"""patch_phase98b.py -- __acad3dV98: every annotation can be touched.

REPORTED: "I can't touch or edit an annotation." Measured before this patch:
  * A dimension or a text label drawn INSIDE a room could not be clicked. pick() tested the
    model first and annotations last, so the room under the label took every click aimed at
    the label -- although the label is drawn on top of the room.
  * Angular, radius, diameter and leader annotations could not be clicked anywhere at all:
    bimPickDim returned early for every kind but 'linear'.
  * Pick ignored bimAnnotationVisible and bimObjectVisibleOnLevel, which draw honours, so an
    annotation hidden by its view or its level could still be picked where nothing was drawn.

The fix is the V82 rule applied to the class, not to one kind: what is drawn on top is picked
first. Annotations are drawn after the model, so they are tested before it -- right after the
note overlay, which is drawn above them. The pick shape of each kind comes from ONE function,
bimAnnotScreenShape, which reproduces exactly the pieces drawDims/drawDimExtras/
drawTextLabels put on screen, including the label boxes.
"""
import hashlib, pathlib

SRC = pathlib.Path('canvas_v10.html')
BASE = '68618e29dfe4921792df6c383d999f929cebe8ee9a3a9678e3d398b5cf6b5d0a'

txt = SRC.read_text(encoding='utf-8')
before = len(txt.encode('utf-8'))
assert hashlib.sha256(txt.encode('utf-8')).hexdigest() == BASE, 'baseline hash mismatch'

OLD_PICKS = """  function bimPickDim(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var best=null,bestD=8,i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='dim')continue;
      if(bimDimKind(o)!=='linear')continue;
      var lyr=bimLayerOf(o);
      if(lyr&&(lyr.visible===false||lyr.locked))continue;
      var ox=(o.pos&&o.pos[0])||0,oz=(o.pos&&o.pos[2])||0,y0=o.y+((o.pos&&o.pos[1])||0);
      var d1=toScreen([o.d1[0]+ox,y0,o.d1[1]+oz],V,W,H);
      var d2=toScreen([o.d2[0]+ox,y0,o.d2[1]+oz],V,W,H);
      var d=bimPointSegDist(x,y,d1[0],d1[1],d2[0],d2[1]);
      if(d<bestD){bestD=d;best=o;}
    }
    return best;
  }
  function bimPickText(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var i,o;
    for(i=A3D.objs.length-1;i>=0;i--){
      o=A3D.objs[i];
      if(o.t!=='text')continue;
      var lyr=bimLayerOf(o);
      if(lyr&&(lyr.visible===false||lyr.locked))continue;
      var ox=(o.pos&&o.pos[0])||0,oz=(o.pos&&o.pos[2])||0,y0=o.y+((o.pos&&o.pos[1])||0);
      var sp=toScreen([o.pt[0]+ox,y0,o.pt[1]+oz],V,W,H);
      ctx_measure_font();
      var tw=A3D_TEXT_MEASURE_CTX?A3D_TEXT_MEASURE_CTX.measureText(o.text).width:o.text.length*7;
      if(x>=sp[0]-4&&x<=sp[0]+tw+14&&y>=sp[1]-11&&y<=sp[1]+11)return o;
    }
    return null;
  }
"""

NEW_PICKS = """  /* ================= __acad3dV98: the pick shape of an annotation =================

     What each annotation puts on screen, as pick geometry: segments (with the tolerance each
     one is picked at) and label boxes. Built from the same points, the same label anchors and
     the same fonts as drawDims / drawDimExtras / drawTextLabels, so an annotation is picked
     exactly where it is drawn -- including its label, which is the part people aim at.

     The reference circle of a radius or diameter dimension is deliberately NOT pickable: it is
     a dashed ghost drawn over the real arc, and letting it win would make the arc underneath
     unselectable. */
  function bimAnnotDrawable(o){
    if(!o||(o.t!=='dim'&&o.t!=='text'))return false;
    if(A3D.section)return false;
    var lyr=bimLayerOf(o);
    if(lyr&&(lyr.visible===false||lyr.locked))return false;
    if(!bimAnnotationVisible(o))return false;
    if(!bimObjectVisibleOnLevel(o))return false;
    return true;
  }
  function bimMeasureLabel(text,font){
    ctx_measure_font();
    if(!A3D_TEXT_MEASURE_CTX)return String(text).length*7;
    A3D_TEXT_MEASURE_CTX.font=font;
    var w=A3D_TEXT_MEASURE_CTX.measureText(String(text)).width;
    A3D_TEXT_MEASURE_CTX.font='12px system-ui,sans-serif';
    return w;
  }
  function bimAnnotScreenShape(o,V,W,H){
    var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
    var y0=(o.y||0)+oy;
    function S(p){return toScreen([p[0]+ox,y0,p[1]+oz],V,W,H);}
    var segs=[],boxes=[],i,tw,lp,label,bx;
    function seg(a,b,tol){segs.push([a[0],a[1],b[0],b[1],tol]);}
    if(o.t==='text'){
      var sp=S(o.pt);
      tw=bimMeasureLabel(o.text||'','12px system-ui,sans-serif');
      boxes.push([sp[0]-4,sp[1]-11,sp[0]+tw+14,sp[1]+11]);
      return {segs:segs,boxes:boxes};
    }
    var kind=bimDimKind(o);
    if(kind==='linear'){
      if(!o.p1||!o.p2||!o.d1||!o.d2)return {segs:segs,boxes:boxes};
      var p1=S(o.p1),p2=S(o.p2),d1=S(o.d1),d2=S(o.d2);
      seg(d1,d2,8);
      seg(p1,d1,5);seg(p2,d2,5);
      var mx=(d1[0]+d2[0])/2,my=(d1[1]+d2[1])/2;
      tw=bimMeasureLabel((o.length||0).toFixed(2)+' m','11px system-ui,sans-serif');
      boxes.push([mx-tw/2-4,my-16,mx+tw/2+4,my-2]);
    }else if(kind==='angular'){
      if(!o.vertex||!o.ap1||!o.ap2)return {segs:segs,boxes:boxes};
      var vtx=S(o.vertex);
      seg(vtx,S(o.ap1),6);seg(vtx,S(o.ap2),6);
      var prev=null,a;
      for(i=0;i<=24;i++){
        a=o.a1+o.sweep*(i/24);
        var cur=S([o.vertex[0]+Math.cos(a)*o.arcRadius,o.vertex[1]+Math.sin(a)*o.arcRadius]);
        if(prev)seg(prev,cur,8);
        prev=cur;
      }
      var midA=o.a1+o.sweep/2;
      lp=S([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25]);
      label=(o.degrees||0).toFixed(1)+'\\u00b0';
      tw=bimMeasureLabel(label,'11px system-ui,sans-serif');
      bx=lp[0]-tw/2;
      boxes.push([bx-4,lp[1]-8,bx+tw+4,lp[1]+7]);
    }else if(kind==='radius'||kind==='diameter'){
      if(!o.dStart||!o.dEdge)return {segs:segs,boxes:boxes};
      var st=S(o.dStart),ed=S(o.dEdge);
      seg(st,ed,8);
      lp=[(st[0]+ed[0])/2,(st[1]+ed[1])/2-10];
      label=(kind==='diameter'?'\\u00d8':'R')+(o.value||0).toFixed(2);
      tw=bimMeasureLabel(label,'11px system-ui,sans-serif');
      bx=lp[0]-tw/2;
      boxes.push([bx-4,lp[1]-8,bx+tw+4,lp[1]+7]);
    }else if(kind==='leader'){
      if(!o.anchor||!o.elbow||!o.landing)return {segs:segs,boxes:boxes};
      var an=S(o.anchor),el2=S(o.elbow),la=S(o.landing);
      seg(an,el2,8);seg(el2,la,8);
      if(o.label){
        lp=[la[0]+(o.ldir<0?-4:4),la[1]-6];
        tw=bimMeasureLabel(o.label,'11px system-ui,sans-serif');
        bx=o.ldir<0?lp[0]-tw:lp[0];
        boxes.push([bx-4,lp[1]-8,bx+tw+4,lp[1]+7]);
      }
    }
    return {segs:segs,boxes:boxes};
  }
  /* Distance in pixels from (x,y) to an annotation, or Infinity when it is out of reach. A
     label box counts as a direct hit. */
  function bimAnnotHitDist(o,x,y,V,W,H){
    var sh=bimAnnotScreenShape(o,V,W,H),best=Infinity,i,s,b,d;
    for(i=0;i<sh.boxes.length;i++){
      b=sh.boxes[i];
      if(x>=b[0]&&x<=b[2]&&y>=b[1]&&y<=b[3])return 0;
    }
    for(i=0;i<sh.segs.length;i++){
      s=sh.segs[i];
      d=bimPointSegDist(x,y,s[0],s[1],s[2],s[3]);
      if(d<s[4]&&d<best)best=d;
    }
    return best;
  }
  function bimPickAnnotOfType(x,y,t){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var best=null,bestD=Infinity,i,o,d;
    /* Later in the list is drawn later, so it is on top and wins a tie. */
    for(i=A3D.objs.length-1;i>=0;i--){
      o=A3D.objs[i];
      if(o.t!==t||!bimAnnotDrawable(o))continue;
      d=bimAnnotHitDist(o,x,y,V,W,H);
      if(d<bestD){bestD=d;best=o;}
    }
    return best;
  }
  function bimPickDim(x,y){return bimPickAnnotOfType(x,y,'dim');}
  function bimPickText(x,y){return bimPickAnnotOfType(x,y,'text');}
  /* Text is drawn after dimensions, so it is tested first. */
  function bimPickAnnotation(x,y){return bimPickText(x,y)||bimPickDim(x,y);}
"""

EDITS = [
    (OLD_PICKS, NEW_PICKS),
    ("""    var nt=bimPickNote(x,y);
    if(nt)return nt;
    if(A3D_GL)bimBuildPickPolys();""",
     """    var nt=bimPickNote(x,y);
    if(nt)return nt;
    /* __acad3dV98: then the dimensions and text, which are drawn above the model too. Testing
       them last let a room swallow a click on the label sitting inside it. */
    var an=bimPickAnnotation(x,y);
    if(an)return an;
    if(A3D_GL)bimBuildPickPolys();"""),
    ("""    return best||bimPickCline(x,y)||bimPickRoom(x,y)||bimPickHatch(x,y)||bimPickDim(x,y)||bimPickText(x,y);""",
     """    return best||bimPickCline(x,y)||bimPickRoom(x,y)||bimPickHatch(x,y);   /* __acad3dV98: annotations are picked in pick(), first */"""),
]

for old, new in EDITS:
    assert txt.count(old) == 1, 'anchor count %d for %r' % (txt.count(old), old[:70])
    txt = txt.replace(old, new, 1)

SRC.write_text(txt, encoding='utf-8')
after = len(txt.encode('utf-8'))
print('bytes %d -> %d' % (before, after))
print('sha256 %s' % hashlib.sha256(txt.encode('utf-8')).hexdigest())
