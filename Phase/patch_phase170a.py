#!/usr/bin/env python3
"""V170a: the analyses in motion -- one clock, and the four motions drawn by the diagram engine: marching dashes
along flows, walks and transit; winds drawn on; the walk-distance rings growing outward and the layers revealed in
turn; the sun along its path with the shadows through the sun study's day. Still until Play; Pause keeps the moment.

Run from the repository root: python3 Phase/patch_phase170a.py
"""
import hashlib, pathlib, sys

SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('canvas_v10.html')
BASE = '55f7b5464bd58fbbe6286cb4d4e2ace62f86c173cce0c67dfcd96ec42fc4c7c3'   # V169

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
if sha != BASE:
    sys.exit('BASE mismatch: %s (expected %s)' % (sha, BASE))
s = raw.decode('utf-8')
before = len(raw)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        sys.exit('expected %d of %r, found %d' % (count, old[:90], n))
    s = s.replace(old, new)


# ---- the clock, the motions' settings, and what each motion draws ----
ANIM = r'''  /* ================= __acad3dV170: the analyses in motion =================
     reference/research-animation.md. Still until Play; Pause beside it whenever anything moves (WCAG 2.2.2),
     keeping the moment; Stop gives the still drawing back. The app opens still, which is what a device asking for
     reduced motion wants (2.3.3), and the device asking for it while it plays pauses it. One clock for every
     animated element, run by requestAnimationFrame while playing, so it stops while the page is hidden; a frame
     painted at most BIM_ANIM.fps times a second. Motion is a style of the element, s.anim: unset, its analysis's
     own (BIM_ANIM_AUTO); 'none', still. The still drawing is the stopped one, unchanged. Nothing the clock does is
     saved or undone: while the sun plays its time stands in for the study's in bimSunNow, the project's own stays.
     Sheets, prints and exports are drawn still. */
  var BIM_ANIM={fps:30,
    march:{speed:28,dash:6,gap:14},                              /* pixels a second along the line; a solid line's moving dashes, each and its gap plus twice the line's width */
    draw:{grow:1.6,hold:1.8,fade:0.6,rest:0.5,stagger:0.35},    /* seconds: a wind drawn on along its direction, held, faded, gone a moment; the next one later */
    ring:{mps:150,hold:2.2},                                     /* the ripple: metres a second of play, then held at the outermost ring */
    reveal:{step:0.45,fade:0.5},                                 /* at each Play: the analyses' layers coming in one after another, in Analyze's order */
    sun:{secs:24,hold:1.2,fill:'#5b6c8a'}};                      /* sunrise to sunset of the study's day, held at sunset; the moving shadow's colour */
  var BIM_ANIM_NAMES={march:'Marching dashes',draw:'Drawn on',ring:'Growing ring',sun:'Through the day',none:'Still'};
  /* each analysis's own: [analysis, an element's key or its start, the motion, a march's way: 'path' as drawn, else away from the site] */
  var BIM_ANIM_AUTO=[['frame','dist:','ring'],['wind','prevail:','draw'],
    ['flow','flow:','march','path'],['flow','exit:','march','path'],['views','view:','march','path'],['vehicles','entry:','march','path'],
    ['walk','w','march'],['needs','need:','march'],['transit','routes','march','path'],['transit','way:','march'],['transit','catch','march'],
    ['sun','now','sun'],['shadow','sh:','sun']];
  var A3D_ANIM={on:false,paused:false,t:0,last:0,painted:0,raf:0,playAt:0,sunTime:null,fr:null,can:false,c:null,dome:null,wired:false,key:'',frames:0};
  function bimAnimMod(t,p){return p>0?((t%p)+p)%p:0;}
  /* moving or paused: the moment drawn; never on a sheet, a print or an export */
  function bimAnimLive(){return (A3D_ANIM.on||A3D_ANIM.paused)&&!A3D.sheetCapture&&!A3D_PLOT.on;}
  /* the motions an element's geometry can take */
  function bimAnimKinds(o){
    var g=o.dg.g,k=g.kind,n=(g.pts||[]).length,L=[];
    if(k==='live'||g.bands)return L;
    if(k==='lines'?(g.lines||[]).length>0:n>=2)L.push('march');
    if(k!=='segs'&&k!=='lines'&&n>=2)L.push('draw');
    if(k!=='segs'&&k!=='lines'&&g.closed&&n>=3)L.push('ring');
    return L;
  }
  function bimAnimAuto(o){
    var dg=o.dg,i,A;
    for(i=0;i<BIM_ANIM_AUTO.length;i++){A=BIM_ANIM_AUTO[i];if(dg.a===A[0]&&String(dg.k).indexOf(A[1])===0)return A;}
    return null;
  }
  /* the element's motion: its own style, else its analysis's; null when still */
  function bimAnimMotion(o){
    var m=(o.dg.s||{}).anim,A;
    if(m==='none')return null;
    if(m&&m!=='sun'&&BIM_ANIM_NAMES[m]&&bimAnimKinds(o).indexOf(m)>=0)return m;
    A=bimAnimAuto(o);
    if(!A)return null;
    if(A[2]==='sun')return 'sun';
    return bimAnimKinds(o).indexOf(A[2])>=0?A[2]:null;
  }
  /* a ring's centre and radius in plan: the mean of its points, and their mean distance from it */
  function bimAnimRingOf(o){
    var P=o.dg.g.pts||[],cx=0,cz=0,r=0,i;
    if(P.length<3)return null;
    for(i=0;i<P.length;i++){cx+=P[i][0];cz+=P[i][2];}
    cx/=P.length;cz/=P.length;
    for(i=0;i<P.length;i++)r+=Math.sqrt((P[i][0]-cx)*(P[i][0]-cx)+(P[i][2]-cz)*(P[i][2]-cz));
    r/=P.length;
    return r>0?{c:[cx,cz],r:r}:null;
  }
  /* once a frame: the analyses shown, in Analyze's order; the rings' radii; what moves */
  function bimAnimFrame(){
    var F=A3D_ANIM.fr,L,seen={},j=0,i,m,a,R;
    if(F&&F.n===A3D.frames)return F;
    F=A3D_ANIM.fr={n:A3D.frames,order:{},idx:{},nd:{},rings:[],Rmax:0,any:false,sun:false,shadowDone:false};
    L=bimDgDiags();
    for(i=0;i<L.length;i++){
      if(!bimLayerShown(L[i]))continue;
      a=L[i].dg.a;seen[a]=true;m=bimAnimMotion(L[i]);
      if(!m)continue;
      if(m==='sun'){if(!bimAnimSunOk())continue;if(L[i].dg.g.kind!=='live')F.sun=true;}
      F.any=true;
      if(m==='ring'){R=bimAnimRingOf(L[i]);if(R){F.rings.push(R.r);if(R.r>F.Rmax)F.Rmax=R.r;}}
      if(m==='draw'){F.idx[L[i].id]=F.nd[a]||0;F.nd[a]=(F.nd[a]||0)+1;}
    }
    for(i=0;i<BIM_DG_AN.length;i++)if(seen[BIM_DG_AN[i].id])F.order[BIM_DG_AN[i].id]=j++;
    F.rings.sort(function(p,q){return p-q;});
    return F;
  }
  /* an analysis's share of its reveal at the last Play: 0 not yet, 1 in */
  function bimAnimReveal(a){
    var j=bimAnimFrame().order[a],R=BIM_ANIM.reveal,x;
    if(j===undefined)return 1;
    x=(A3D_ANIM.t-A3D_ANIM.playAt-j*R.step)/R.fade;
    return x<=0?0:(x>=1?1:x);
  }
  function bimAnimAlpha(o){return bimAnimLive()?bimAnimReveal(o.dg.a):1;}
  /* how far a ring has grown, 0 to 1: the ripple's front leaves each ring as it passes it, and is drawn by the
     smallest ring it has not reached */
  function bimAnimRingK(o){
    var R=bimAnimRingOf(o),F=bimAnimFrame(),B=BIM_ANIM.ring,w,i;
    if(!R||!(F.Rmax>0))return 1;
    w=bimAnimMod(A3D_ANIM.t,F.Rmax/B.mps+B.hold)*B.mps;
    if(w>=R.r)return 1;
    for(i=0;i<F.rings.length;i++)if(F.rings[i]>w+1e-6&&F.rings[i]<R.r-1e-6)return 0;
    return w/R.r;
  }
  function bimAnimScreen(o,V,W,H,k){
    var R=bimAnimRingOf(o),g=o.dg.g,P=[],i,p;
    if(!R)return bimDgScreen(o,V,W,H);
    for(i=0;i<(g.pts||[]).length;i++){p=g.pts[i];P.push(toScreen(bimDgW(o,[R.c[0]+(p[0]-R.c[0])*k,p[1],R.c[1]+(p[2]-R.c[1])*k]),V,W,H));}
    return P;
  }
  /* a wind drawn on: how far, 0 to 1, and its opacity; one after another within the analysis */
  function bimAnimDrawOf(o){
    var B=BIM_ANIM.draw,per=B.grow+B.hold+B.fade+B.rest,i=bimAnimFrame().idx[o.id]||0,p=bimAnimMod(A3D_ANIM.t-i*B.stagger,per),x;
    if(p<B.grow){x=p/B.grow;return {f:x*x*(3-2*x),a:1};}
    if(p<B.grow+B.hold)return {f:1,a:1};
    if(p<B.grow+B.hold+B.fade)return {f:1,a:1-(p-B.grow-B.hold)/B.fade};
    return {f:0,a:0};
  }
  /* what is drawn so far: the screen up to f of the way along the element -- a closed shape from the middle of
     its first and last points to its middle point (a wind's arrow, tail to tip), a line from its first point to
     its last; drawn whole where a point is behind the eye */
  function bimAnimClip(c,P,f,closed){
    var n=P.length,A,B,i,ux,uy,L,G,nx,ny,F;
    if(n<2)return;
    for(i=0;i<n;i++)if(P[i][2]<=0.5)return;
    A=closed?[(P[0][0]+P[n-1][0])/2,(P[0][1]+P[n-1][1])/2]:P[0];B=closed?P[Math.floor((n-1)/2)]:P[n-1];
    ux=B[0]-A[0];uy=B[1]-A[1];L=Math.sqrt(ux*ux+uy*uy);
    if(!(L>1e-6))return;
    ux/=L;uy/=L;nx=-uy;ny=ux;G=10*L+2000;F=[A[0]+ux*L*f,A[1]+uy*L*f];
    c.beginPath();c.moveTo(F[0]+nx*G,F[1]+ny*G);c.lineTo(F[0]-nx*G,F[1]-ny*G);c.lineTo(F[0]-nx*G-ux*G,F[1]-ny*G-uy*G);c.lineTo(F[0]+nx*G-ux*G,F[1]+ny*G-uy*G);c.closePath();
    c.clip();
  }
  /* a march: the dashes' offset; away from the site unless it has an arrowhead or its analysis says as drawn */
  function bimAnimMarchOff(){return -A3D_ANIM.t*BIM_ANIM.march.speed;}
  function bimAnimOut(o){var A=bimAnimAuto(o);return !(o.dg.s&&o.dg.s.head)&&!(A&&A[3]==='path');}
  function bimAnimCentre(){if(!A3D_ANIM.c)A3D_ANIM.c=bimDgSite().c;return A3D_ANIM.c;}   /* found once a Play */
  function bimAnimFar(o,p,c){var w=bimDgW(o,p);return (w[0]-c[0])*(w[0]-c[0])+(w[2]-c[1])*(w[2]-c[1]);}
  /* the screen points turned so a march goes away from the site: a line end to end, each pair of segments */
  function bimAnimOrient(o,P){
    var g=o.dg.g,W=g.pts||[],c,i,t;
    if(W.length<2||P.length!==W.length||g.closed)return P;
    c=bimAnimCentre();
    if(g.kind==='segs'){
      for(i=0;i+1<W.length;i+=2)if(bimAnimFar(o,W[i],c)>bimAnimFar(o,W[i+1],c)){t=P[i];P[i]=P[i+1];P[i+1]=t;}
      return P;
    }
    if(bimAnimFar(o,W[0],c)>bimAnimFar(o,W[W.length-1],c))P.reverse();
    return P;
  }
  function bimAnimOrientLine(o,Wl,lp){
    var c;
    if(Wl.length<2||lp.length!==Wl.length)return lp;
    c=bimAnimCentre();
    if(bimAnimFar(o,Wl[0],c)>bimAnimFar(o,Wl[Wl.length-1],c))lp.reverse();
    return lp;
  }
  /* a moving dash on a solid line: the line's colour lighter, or darker on a pale line */
  function bimAnimTint(hex){
    var m=/^#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(String(hex||'')),r,g,b,t;
    if(!m)return 'rgba(255,255,255,0.85)';
    r=parseInt(m[1],16);g=parseInt(m[2],16);b=parseInt(m[3],16);
    t=(0.2126*r+0.7152*g+0.0722*b)/255>0.72?[0,0.5]:[255,0.6];
    function q(v){return Math.round(v+(t[0]-v)*t[1]);}
    return 'rgb('+q(r)+','+q(g)+','+q(b)+')';
  }
  /* the path built, stroked: a dashed line's own dashes moved, a solid one's dashes laid over it */
  function bimAnimStroke(ctx,s,w,off){
    var dashed=!!(s.dash&&s.dash.length),M=BIM_ANIM.march;
    if(off!==null&&dashed)ctx.lineDashOffset=off;
    ctx.stroke();ctx.lineDashOffset=0;
    if(off===null||dashed)return;
    ctx.setLineDash([M.dash+2*w,M.gap+2*w]);ctx.lineDashOffset=off;ctx.strokeStyle=bimAnimTint(s.stroke);ctx.stroke();
    ctx.setLineDash([]);ctx.lineDashOffset=0;
  }
  /* the sun: its time while it plays, from sunrise to sunset of the study's day (all day under the midnight sun),
     held a moment at sunset; none without the site's place or in the polar night */
  function bimAnimSunOk(){var st=bimSunSettings();return bimSunNum(st.lat)&&bimSunNum(st.lon)&&bimSunNum(st.tz);}
  function bimAnimSunTime(){
    var st=bimSunSettings(),B=BIM_ANIM.sun,r,a,b,p;
    if(!bimAnimSunOk())return null;
    r=bimSunCalc(st.lat,st.lon,st.tz,st.date,'12:00');
    if(!r||r.polar==='night')return null;
    if(r.polar==='day'){a=0;b=1439;}else{a=Math.ceil(r.sunrise);b=Math.floor(r.sunset);}
    if(!(b>a))return null;
    p=bimAnimMod(A3D_ANIM.t,B.secs+B.hold);
    return bimHHMM(Math.floor(a+(b-a)*Math.min(1,p/B.secs)));
  }
  /* the sun moving along its path on the sun paths' dome, with its time; it stands in for "the sun now" */
  function bimAnimDrawSun(ctx,V,W,H,Q){
    var F=bimAnimFrame(),sun,D,S,sp,a;
    if(!F.sun||!A3D_ANIM.sunTime)return;
    sun=bimSunNow();
    if(!sun||sun.missing||!(sun.elevation>0))return;
    D=(bimDgState().runs.sun||{}).dome;
    if(D&&D.c&&D.R>0)S={c:D.c,y:D.y||0};
    else{S=A3D_ANIM.dome||(A3D_ANIM.dome=bimDgSite());D={R:S.Rc};}
    sp=toScreen(bimDgDome(S,D.R,sun),V,W,H);
    a=bimAnimReveal('sun');
    if(sp[2]<=0.5||!(a>0))return;
    ctx.save();ctx.globalAlpha=a;bimDgSym(ctx,sp,{type:'dot',r:6},'#e5484d',a);ctx.restore();
    Q.push({hit:{boxes:[]},t:A3D_ANIM.sunTime,x:sp[0],y:sp[1]-16,col:'#ff8a8f',sz:11,al:'center',pri:1,a:a,sel:false,cap:false});
    F.sunAt=[sp[0],sp[1]];
  }
'''
rep("  /* what is under the pointer: a line, a dot, a label or a symbol of a diagram, drawn over the\n",
    ANIM + "  /* what is under the pointer: a line, a dot, a label or a symbol of a diagram, drawn over the\n")

# ---- under the model: a fill revealed, grown or drawn on; the shadow through the day ----
rep("""    var dg=o.dg,g=dg.g,s=dg.s||{},a=bimLayerAlpha(o)*(s.op===undefined?1:s.op);
    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a);return;}
    if(g.kind==='segs'||!g.pts||g.pts.length<3||!s.fill||!g.closed)return;
    ctx.save();bimDgPath(ctx,bimDgScreen(o,V,W,H),true);ctx.globalAlpha=a*(s.fop===undefined?0.35:s.fop);ctx.fillStyle=s.fill;ctx.fill();ctx.restore();
  }
""", """    var dg=o.dg,g=dg.g,s=dg.s||{},a=bimLayerAlpha(o)*(s.op===undefined?1:s.op)*bimAnimAlpha(o),mo=bimAnimLive()?bimAnimMotion(o):null,P,k,an;   /* __acad3dV170 */
    if(!(a>0))return;
    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a,mo==='sun');return;}
    if(g.kind==='segs'||!g.pts||g.pts.length<3||!s.fill||!g.closed)return;
    if(mo==='ring'){k=bimAnimRingK(o);if(!(k>0))return;P=k<1?bimAnimScreen(o,V,W,H,k):bimDgScreen(o,V,W,H);}else P=bimDgScreen(o,V,W,H);
    ctx.save();
    if(mo==='draw'){an=bimAnimDrawOf(o);if(!(an.a>0)){ctx.restore();return;}a*=an.a;bimAnimClip(ctx,P,an.f,true);}
    bimDgPath(ctx,P,true);ctx.globalAlpha=a*(s.fop===undefined?0.35:s.fop);ctx.fillStyle=s.fill;ctx.fill();ctx.restore();
  }
""")
rep("      if(!i)a=bimLayerAlpha(o)*(s.fop===undefined?0.45:s.fop);\n",
    "      if(!i)a=bimLayerAlpha(o)*(s.fop===undefined?0.45:s.fop)*bimAnimAlpha(o);   /* __acad3dV170: revealed in turn */\n")
rep("""  function bimDgDrawShadow(ctx,V,W,H,o,a){
    var L=o.dg.g.live,sun=L?bimDgSun(L.date,L.time):null;
    if(!sun)return;
    var sv=bimSunVector(sun),gr=bimShadowGround(),list=bimDgCasters(gr,L.c||[0,0],L.r||200,L.date);
    if(!list.length)return;
    var c2=bimDgOff(ctx,'shadowCv');
    c2.globalCompositeOperation='source-over';c2.fillStyle=(o.dg.s&&o.dg.s.fill)||'#5b6c8a';
""", """  function bimDgDrawShadow(ctx,V,W,H,o,a,day){
    var L=o.dg.g.live,mv=!!(day&&L&&A3D_ANIM.sunTime),dt=mv?bimSunSettings().date:(L&&L.date),sun;
    /* __acad3dV170: through the day, one shadow, at the sun's moment on the study's day */
    if(mv){var F=bimAnimFrame();if(F.shadowDone)return;F.shadowDone=true;}
    sun=L?(mv?bimDgSun(dt,A3D_ANIM.sunTime):bimDgSun(L.date,L.time)):null;
    if(!sun)return;
    var sv=bimSunVector(sun),gr=bimShadowGround(),list=bimDgCasters(gr,L.c||[0,0],L.r||200,dt);
    if(!list.length)return;
    var c2=bimDgOff(ctx,'shadowCv');
    c2.globalCompositeOperation='source-over';c2.fillStyle=mv?BIM_ANIM.sun.fill:((o.dg.s&&o.dg.s.fill)||'#5b6c8a');
""")

# ---- over the model: the lines, in motion ----
rep("""    if(g.kind==='live')return hit;
    sel=sel&&!cap;
    P=bimDgScreen(o,V,W,H);
""", """    if(g.kind==='live')return hit;
    sel=sel&&!cap;
    /* __acad3dV170: in motion -- revealed in turn; a ring grown so far, its words when it is whole; a wind drawn on;
       a march's dashes moved, away from the site or as drawn; the sun now gives way to the sun moving */
    var mo=bimAnimLive()?bimAnimMotion(o):null,rk=1,an=null,clip=false,lbOk=true,mOff=null;
    if(bimAnimLive())a*=bimAnimReveal(dg.a);
    if(!(a>0)||(mo==='sun'&&A3D_ANIM.sunTime&&bimAnimFrame().sun))return hit;
    if(mo==='ring'){rk=bimAnimRingK(o);if(!(rk>0))return hit;lbOk=rk>=1;}
    P=rk<1?bimAnimScreen(o,V,W,H,rk):bimDgScreen(o,V,W,H);
    if(mo==='march'){mOff=bimAnimMarchOff();if(bimAnimOut(o))P=bimAnimOrient(o,P);}
    if(mo==='draw'){an=bimAnimDrawOf(o);if(!(an.a>0))return hit;a*=an.a;lbOk=an.f>=1;ctx.save();clip=true;bimAnimClip(ctx,P,an.f,!!g.closed);}
""")
rep("        lp=[];for(i=0;i<LL[ln].length;i++)lp.push(toScreen(bimDgW(o,LL[ln][i]),V,W,H));\n",
    "        lp=[];for(i=0;i<LL[ln].length;i++)lp.push(toScreen(bimDgW(o,LL[ln][i]),V,W,H));\n"
    "        if(mOff!==null&&bimAnimOut(o)&&!g.closed)lp=bimAnimOrientLine(o,LL[ln],lp);   /* __acad3dV170 */\n")
rep("        if(s.stroke){bimDgPath(ctx,lp,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.2;ctx.stroke();ctx.setLineDash([]);}\n",
    "        if(s.stroke){bimDgPath(ctx,lp,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.2;bimAnimStroke(ctx,s,s.w||1.2,mOff);ctx.setLineDash([]);}\n")
rep("      if(s.stroke){ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.4;ctx.stroke();ctx.setLineDash([]);}\n",
    "      if(s.stroke){ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.4;bimAnimStroke(ctx,s,s.w||1.4,mOff);ctx.setLineDash([]);}\n")
rep("      if(s.stroke){bimDgPath(ctx,P,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.5;ctx.stroke();ctx.setLineDash([]);}\n",
    "      if(s.stroke){bimDgPath(ctx,P,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.5;bimAnimStroke(ctx,s,s.w||1.5,mOff);ctx.setLineDash([]);}\n")
rep("      if(g.marks[i].t)Q.push(", "      if(g.marks[i].t&&lbOk)Q.push(")
rep("      var L=dg.lb[i];if(!L||!L.t||!L.p)continue;\n", "      var L=dg.lb[i];if(!L||!L.t||!L.p||!lbOk)continue;\n")
rep("""    ctx.globalAlpha=1;
    return hit;
  }
  /* the words, the most telling first:""", """    if(clip)ctx.restore();
    ctx.globalAlpha=1;
    return hit;
  }
  /* the words, the most telling first:""")
rep("      if(over){A3D_DG.ly=bimDgLegendLayout(ctx,W,H);A3D_DG.lyCtx=ctx;A3D_DG.lyFrame=A3D.frames;}",
    "      if(over&&bimAnimLive())bimAnimDrawSun(ctx,V,W,H,Q);   /* __acad3dV170 */\n"
    "      if(over){A3D_DG.ly=bimDgLegendLayout(ctx,W,H);A3D_DG.lyCtx=ctx;A3D_DG.lyFrame=A3D.frames;}")

# ---- the sun paths keep their dome, for the sun moving on it ----
rep("""      {name:'An hour',short:'hour',col:'#ffd23f',kind:'dot'},{name:'The sun now',short:'now',col:'#e5484d',kind:'dot'}],source:'NOAA solar position equations'}};""",
    """      {name:'An hour',short:'hour',col:'#ffd23f',kind:'dot'},{name:'The sun now',short:'now',col:'#e5484d',kind:'dot'}],source:'NOAA solar position equations',dome:{c:S.c,y:S.y,R:R}}};   /* __acad3dV170: the dome */""")
rep("      legend:run&&run.legend?run.legend:[],note:run&&run.note?run.note:'',source:run&&run.source?run.source:'',\n",
    "      legend:run&&run.legend?run.legend:[],note:run&&run.note?run.note:'',source:run&&run.source?run.source:'',dome:run&&run.dome?run.dome:undefined,   /* __acad3dV170 */\n")

# ---- the sun's moment: the clock's while it plays, the study's otherwise ----
rep("""  function bimSunNow(){
    var st=bimSunSettings(),miss=[],r;
""", """  function bimSunNow(saved){
    var st=bimSunSettings(),miss=[],r;
    if(!saved&&A3D_ANIM.sunTime&&bimAnimLive())st.time=A3D_ANIM.sunTime;   /* __acad3dV170: the sun while it plays; the project's time stays */
""")
rep("    loc+=bimPropText('Sun',bimSunText(bimSunNow()));", "    loc+=bimPropText('Sun',bimSunText(bimSunNow(true)));")
rep("    a3dToast('Sun: '+bimSunText(bimSunNow()));", "    a3dToast('Sun: '+bimSunText(bimSunNow(true)));")
rep("      A3D.lastSunPath={north:[nx,ny]",
    "      if(bimAnimLive()&&A3D_ANIM.sunTime&&sunPt){ctx.textAlign='left';ctx.fillStyle='#ffe066';ctx.fillText(A3D_ANIM.sunTime,box[0]+6,box[1]+box[3]-9);}   /* __acad3dV170: the time, while it plays */\n"
    "      A3D.lastSunPath={north:[nx,ny]")

out = s.encode('utf-8')
na0 = sum(1 for c in raw.decode('utf-8') if ord(c) > 127)
na1 = sum(1 for c in s if ord(c) > 127)
if na1 > na0:
    sys.exit('the patch added %d non-ASCII characters' % (na1 - na0))
SRC.write_bytes(out)
print('bytes', before, '->', len(out))
print('sha256', hashlib.sha256(out).hexdigest())
