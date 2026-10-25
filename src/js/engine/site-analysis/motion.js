  /* ================= __acad3dV170: the analyses in motion =================
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
  /* Play from still starts the clock at nothing, the layers coming in one after another; Play after Pause goes on
     from the moment kept */
  function bimAnimCan(){A3D_ANIM.fr=null;return bimAnimFrame().any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk());}
  function bimAnimPlay(on){
    if(on===undefined||on===null)on=!A3D_ANIM.on;
    on=!!on;
    if(on===A3D_ANIM.on)return true;
    if(on&&!bimAnimCan()){a3dToast('Nothing to play: show a site analysis layer, or the sun study in plan');return false;}
    A3D_ANIM.on=on;
    if(on){
      if(!A3D_ANIM.paused){A3D_ANIM.t=0;A3D_ANIM.playAt=0;}
      A3D_ANIM.paused=false;A3D_ANIM.c=null;A3D_ANIM.dome=null;A3D_ANIM.sunTime=bimAnimSunTime();
      bimAnimWire();A3D_ANIM.last=0;A3D_ANIM.painted=0;bimAnimRun();
    }else{A3D_ANIM.paused=true;bimAnimHalt();}
    paint();
    return true;
  }
  function bimAnimStop(){
    var was=A3D_ANIM.on||A3D_ANIM.paused;
    A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;
    bimAnimHalt();
    if(was)paint();
    return was;
  }
  function bimAnimRun(){if(!A3D_ANIM.raf&&A3D_ANIM.on&&!document.hidden)A3D_ANIM.raf=requestAnimationFrame(bimAnimTick);}
  function bimAnimHalt(){if(A3D_ANIM.raf){cancelAnimationFrame(A3D_ANIM.raf);A3D_ANIM.raf=0;}A3D_ANIM.last=0;}
  function bimAnimTick(ts){
    A3D_ANIM.raf=0;
    if(!A3D_ANIM.on||!A3D.on)return;
    if(A3D_ANIM.last)A3D_ANIM.t+=Math.min(0.1,Math.max(0,(ts-A3D_ANIM.last)/1000));   /* a slow frame moves it a tenth of a second at most, never a jump */
    A3D_ANIM.last=ts;
    if(!A3D_ANIM.painted||ts-A3D_ANIM.painted>=1000/BIM_ANIM.fps-2){
      A3D_ANIM.painted=ts;A3D_ANIM.sunTime=bimAnimSunTime();
      try{paint();A3D_ANIM.frames++;}
      catch(eA){console.warn('[BIM] A frame of the motion could not be drawn',eA);bimAnimPlay(false);a3dToast('The motion was paused: a frame could not be drawn - see the console');return;}
      if(!A3D_ANIM.on)return;
    }
    bimAnimRun();
  }
  /* the page hidden: the clock waits; the device asking for reduced motion while it plays: paused */
  function bimAnimWire(){
    if(A3D_ANIM.wired)return;
    A3D_ANIM.wired=true;
    document.addEventListener('visibilitychange',function(){if(document.hidden)bimAnimHalt();else bimAnimRun();});
    try{
      var mq=window.matchMedia?window.matchMedia('(prefers-reduced-motion: reduce)'):null,f;
      if(mq){
        f=function(){if(mq.matches&&A3D_ANIM.on){bimAnimPlay(false);a3dToast('Paused: the device asks for reduced motion');}};
        if(mq.addEventListener)mq.addEventListener('change',f);else if(mq.addListener)mq.addListener(f);
      }
    }catch(eM){console.warn('[BIM] The reduced-motion setting could not be followed',eM);}
  }
  /* Play and Pause shown whenever something can move, Stop while it is not still; nothing left to move, still */
  function bimAnimSync(){
    var F=bimAnimFrame(),can=F.any||!!(A3D.showSun&&bimCameraIsPlan()&&bimAnimSunOk()),moving=A3D_ANIM.on||A3D_ANIM.paused,g,b,x,key;
    A3D_ANIM.can=can;
    if(!can&&moving){A3D_ANIM.on=false;A3D_ANIM.paused=false;A3D_ANIM.t=0;A3D_ANIM.playAt=0;A3D_ANIM.sunTime=null;bimAnimHalt();moving=false;}
    g=document.getElementById('a3d-animgrp');b=document.getElementById('a3d-animplay');x=document.getElementById('a3d-animstop');
    if(!g||!b)return;
    key=(can?1:0)+':'+(A3D_ANIM.on?1:0)+':'+(moving?1:0);
    if(key!==A3D_ANIM.key){
      A3D_ANIM.key=key;
      g.hidden=!can;
      var bar=document.getElementById('a3d-statusbar');if(bar)bar.classList.toggle('a3d-hasanim',can);
      b.innerHTML=(A3D_ANIM.on?PILL_PAUSE:PILL_PLAY)+'<span>'+(A3D_ANIM.on?'PAUSE':'PLAY')+'</span>';
      b.setAttribute('aria-label',A3D_ANIM.on?'Pause':'Play');
      b.setAttribute('aria-pressed',A3D_ANIM.on?'true':'false');
      b.classList.toggle('on',!!A3D_ANIM.on);
      if(x)x.hidden=!moving;
    }
    var tt=A3D_ANIM.on?'Pause, keeping this moment'+(A3D_ANIM.sunTime?' (the sun at '+A3D_ANIM.sunTime+')':''):
      (A3D_ANIM.paused?'Play on from this moment':'Play the site analysis in motion: marching dashes, winds drawn on, rings growing, the layers in turn, the sun through the day');
    if(b.title!==tt)b.title=tt;
  }
  /* what is under the pointer: a line, a dot, a label or a symbol of a diagram, drawn over the
     model and so picked before it. A band, a fill or a shadow is picked here by its lines and words
     only, so it never covers the model it lies over; __acad3dV165: a band's inside, last of all
     (bimPickBand). */
  function bimPickDiag(x,y){
    var H=A3D_DG.hits,i,j,b;
    for(i=H.length-1;i>=0;i--){
      var o=objById(H[i].id);
      if(!o||!bimLayerPickable(o))continue;
      for(j=0;j<H[i].boxes.length;j++){b=H[i].boxes[j];if(x>=b[0]-2&&x<=b[0]+b[2]+2&&y>=b[1]&&y<=b[1]+b[3])return o;}
      for(j=0;j<H[i].dots.length;j++){var dx=x-H[i].dots[j][0],dy=y-H[i].dots[j][1];if(dx*dx+dy*dy<=64)return o;}
      for(j=0;j<H[i].segs.length;j++){var s=H[i].segs[j];if(bimPointSegDist(x,y,s[0],s[1],s[2],s[3])<=5)return o;}
    }
    return null;
  }
  /* __acad3dV165: a band -- a slope or aspect class, a pond, a flood zone, a road's noise -- picked by
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
    function P(p){var w=tp([p[0],p[2]]);return [w[0],p[1],w[1]];}
    var g=JSON.parse(JSON.stringify(dg.g)),lb=JSON.parse(JSON.stringify(dg.lb||[])),sym=dg.sym?JSON.parse(JSON.stringify(dg.sym)):null;
    if(g.pts)g.pts=g.pts.map(P);
    if(g.marks)g.marks.forEach(function(m){m.p=P(m.p);});
    if(g.bands)g.bands.forEach(function(B){if(B.pts)B.pts=B.pts.map(P);if(B.rings)B.rings=B.rings.map(function(Rg){return Rg.map(P);});});   /* __acad3dV165 */
    if(g.lines)g.lines=g.lines.map(function(Ln){return Ln.map(P);});
    lb.forEach(function(L){if(L.p)L.p=P(L.p);});
    if(sym&&sym.p)sym.p=P(sym.p);
    if(sym&&sym.toward)sym.toward=P(sym.toward);
    return {kind:'diag',g:g,lb:lb,sym:sym};
  }
  /* a copy made by Mirror or an array is the owner's own: a key of its own, and nothing to reset to */
  function bimDgCopy(o,g,copy,word){
    copy.t='diag';copy.name=String(o.name+' '+word).slice(0,80);
    copy.dg={a:o.dg.a,k:o.dg.k+'#'+copy.id,g:g.g,s:JSON.parse(JSON.stringify(o.dg.s||{})),lb:g.lb,sym:g.sym,info:JSON.parse(JSON.stringify(o.dg.info||{})),gen:''};
    return copy;
  }
  function bimDgBounds(o){
    var P=[],g=o.dg.g,i;
    if(g.kind==='live'&&g.live){var c=g.live.c||[0,0],r=g.live.r||20;P.push([c[0]-r,0,c[1]-r],[c[0]+r,0,c[1]+r]);}
    (g.pts||[]).forEach(function(p){P.push(p);});
    (g.marks||[]).forEach(function(m){P.push(m.p);});
    (g.bands||[]).forEach(function(B){(B.pts||[]).forEach(function(p){P.push(p);});(B.rings||[]).forEach(function(Rg){Rg.forEach(function(p){P.push(p);});});});   /* __acad3dV165 */
    (g.lines||[]).forEach(function(Ln){Ln.forEach(function(p){P.push(p);});});
    (o.dg.lb||[]).forEach(function(L){if(L.p)P.push(L.p);});
    if(o.dg.sym&&o.dg.sym.p)P.push(o.dg.sym.p);
    for(i=0;i<P.length;i++)P[i]=bimDgW(o,P[i]);
    return P;
  }
