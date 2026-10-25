  /* ---- the layers: Site analysis, and one under it for each analysis ---- */
  function bimDgLayerFind(id,name,parentId){
    var ly=id?bimLayerById(id):null;
    if(ly&&(ly.parent||null)===(parentId||null))return ly;
    var i;
    for(i=0;i<A3D.layers.length;i++)if(A3D.layers[i].name===name&&(A3D.layers[i].parent||null)===(parentId||null))return A3D.layers[i];
    return null;
  }
  function bimDgLayer(key,name,color,parentKey,hidden){
    var D=bimDgState(),pid=parentKey?(D.layers[parentKey]||null):null,ly=bimDgLayerFind(D.layers[key],name,pid),n=name,k=2;
    if(!ly){
      while(bimLayerByName(n)){n=name+' '+k;k++;}
      ly=bimLayerNew({name:n,color:color,parent:pid});
      if(!ly)return null;
      if(hidden)ly.visible=false;
    }
    D.layers[key]=ly.id;
    return ly;
  }
  function bimDgRoot(){return bimDgLayer('root','Site analysis','#9aa7b4',null,false);}
  function bimDgAnLayer(a){
    var A=bimDgAn(a);
    if(!bimDgRoot())return null;
    return bimDgLayer(a,'Site analysis - '+A.name,A.col,'root',!!A.hidden);   /* __acad3dV165: a coverage starts hidden: one reads at a time */
  }
  /* ---- laying an analysis down ----
     E: [{k, name, layer (a layer key of run.layers, or none for the analysis's own), g, s, lb, sym,
     info}]. What the owner changed is kept, what they deleted stays deleted, the rest is the
     analysis's again. run: {layers:{key:{name, col, hidden}}, legend, note, source}. */
  function bimDgPlace(a,E,run){
    var D=bimDgState(),R=D.runs[a]||{},prev=R.keys||[],have={},gone={},keys=[],L={},made=0,upd=0,kept=0,drop=0,i,k;
    bimDgDiags(a).forEach(function(x){if(!have.hasOwnProperty(x.dg.k))have[x.dg.k]=x;});
    prev.forEach(function(kk){if(!have.hasOwnProperty(kk))gone[kk]=1;});
    (R.gone||[]).forEach(function(kk){gone[kk]=1;});
    function lay(key){
      if(!key)key=a;
      if(!L.hasOwnProperty(key)){
        var sub=run&&run.layers&&run.layers[key],ly=(key===a)?bimDgAnLayer(a):bimDgLayer(key,sub?sub.name:key,sub?sub.col:bimDgAn(a).col,a,!!(sub&&sub.hidden));
        L[key]=ly?ly.id:null;
      }
      return L[key];
    }
    lay(a);   /* the analysis's layer first: its own sub-layers hang from it */
    if(run&&run.layers)for(k in run.layers)if(run.layers.hasOwnProperty(k))lay(k);
    for(i=0;i<E.length;i++){
      var e=E[i],x=have[e.k],core={g:e.g,s:e.s||{},lb:e.lb||[],sym:e.sym||null},gen=JSON.stringify(core);
      keys.push(e.k);
      if(gone[e.k])continue;
      if(x){
        if(bimDgEdited(x)){
          if(x.dg.gen!==gen)x.dg.newer=true;
          x.dg.gen=gen;x.dg.info=e.info||{};delete x.dg.orphan;kept++;
        }else{
          x.dg.g=core.g;x.dg.s=core.s;x.dg.lb=core.lb;x.dg.sym=core.sym;x.dg.gen=gen;x.dg.info=e.info||{};
          delete x.dg.newer;delete x.dg.orphan;x.name=String(e.name||x.name).slice(0,80);x.layer=lay(e.layer)||x.layer;upd++;
        }
        delete have[e.k];
      }else{
        A3D.objs.push({id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'diag',name:String(e.name||e.k).slice(0,80),layer:lay(e.layer),pos:[0,0,0],
          dg:{a:a,k:e.k,g:core.g,s:core.s,lb:core.lb,sym:core.sym,info:e.info||{},gen:gen}});
        made++;
      }
    }
    /* what the analysis no longer draws: gone, unless the owner changed it */
    for(k in have)if(have.hasOwnProperty(k)){
      if(bimDgEdited(have[k])){have[k].dg.orphan=true;kept++;}
      else{A3D.objs=A3D.objs.filter(function(x){return x!==have[k];});drop++;}
    }
    if(A3D.sel&&!objById(A3D.sel))A3D.sel=null;
    A3D.selSet=(A3D.selSet||[]).filter(function(id){return !!objById(id);});
    D.runs[a]={keys:keys,gone:Object.keys(gone).filter(function(kk){return keys.indexOf(kk)>=0;}),date:bimSaToday(),
      legend:run&&run.legend?run.legend:[],note:run&&run.note?run.note:'',source:run&&run.source?run.source:'',dome:run&&run.dome?run.dome:undefined,   /* __acad3dV170 */
      std:bimStdStamp(BIM_DG_STD[a]||[])};   /* __acad3dV167: the standards it used */
    return {made:made,updated:upd,kept:kept,dropped:drop,total:E.length};
  }
  /* Reset: the element as the analysis drew it, where it drew it */
  function bimDgReset(id){
    var o=objById(id);
    if(!bimIsDiag(o)||!o.dg.gen){a3dToast('That element is not the analysis\'s: there is nothing to reset it to');return false;}
    if(!bimDgEdited(o)&&!o.dg.newer){a3dToast(o.name+' is as the analysis drew it');return false;}
    pushUndo();
    var c=JSON.parse(o.dg.gen);
    o.dg.g=c.g;o.dg.s=c.s;o.dg.lb=c.lb;o.dg.sym=c.sym;o.pos=[0,0,0];delete o.dg.newer;
    refreshProps();paint();saveSoon();
    a3dToast(o.name+' is as the analysis drew it again');
    return true;
  }
  /* Reset a whole analysis: its layer as the analysis draws it -- what was deleted comes back, what
     was changed or copied goes. One undo step. */
  function bimDgResetAnalysis(a){
    var D=bimDgState(),held=bimUndoHold,r;
    if(!bimDgAn(a)||!D.runs[a]){a3dToast('That analysis has not run yet');return null;}
    if(!held){pushUndo();bimUndoHold=true;}
    try{
      A3D.objs=A3D.objs.filter(function(x){return !(bimIsDiag(x)&&x.dg.a===a);});
      D.runs[a].gone=[];D.runs[a].keys=[];
      r=bimDgRunAll(a);
    }finally{if(!held)bimUndoHold=false;}
    a3dToast(bimDgAn(a).name+': as the analysis draws it');
    return r?r[a]:null;
  }
  /* ---- drawing, in plan and in 3D ---- */
  function bimDgDrawText(ctx,t,x,y,col,sz,cap){
    ctx.font=(sz||11)+'px sans-serif';
    ctx.lineWidth=3;ctx.strokeStyle=cap?'rgba(255,255,255,0.9)':'rgba(15,18,22,0.85)';ctx.lineJoin='round';
    ctx.strokeText(t,x,y);
    ctx.fillStyle=cap?'#1d2329':(col||'#e8edf2');
    ctx.fillText(t,x,y);
    var w=ctx.measureText(t).width;
    return [x-(ctx.textAlign==='center'?w/2:(ctx.textAlign==='right'?w:0)),y-(sz||11)/2-2,w,(sz||11)+4];
  }
  function bimDgSym(ctx,sp,sym,col,a){
    var r=Math.max(6,sym.r||1),i,k;
    ctx.strokeStyle=col;ctx.fillStyle=col;ctx.setLineDash([]);
    if(sym.type==='dot'){ctx.beginPath();ctx.arc(sp[0],sp[1],r,0,2*Math.PI);ctx.fill();return r;}
    if(sym.type==='noise'){   /* sound arcs, either side of the source, turned towards the site */
      var d=sym.dir||0;
      ctx.lineWidth=2;
      for(k=1;k<=3;k++){
        ctx.globalAlpha=a*(1.1-k*0.22);
        ctx.beginPath();ctx.arc(sp[0],sp[1],r*k*0.7,d-0.9,d+0.9);ctx.stroke();
        ctx.beginPath();ctx.arc(sp[0],sp[1],r*k*0.7,d+Math.PI-0.9,d+Math.PI+0.9);ctx.stroke();
      }
      ctx.globalAlpha=a;ctx.beginPath();ctx.arc(sp[0],sp[1],2.5,0,2*Math.PI);ctx.fill();
      return r*2.1;
    }
    if(sym.type==='storm'){   /* three arms of a spiral, the planners' mark for storms */
      ctx.lineWidth=2.2;
      for(k=0;k<3;k++){
        ctx.beginPath();
        for(i=0;i<=24;i++){var th=k*2*Math.PI/3+i*0.17,rr=r*0.15+r*1.25*i/24,X=sp[0]+rr*Math.cos(th),Y=sp[1]+rr*Math.sin(th);if(i)ctx.lineTo(X,Y);else ctx.moveTo(X,Y);}
        ctx.stroke();
      }
      return r*1.4;
    }
    return 0;
  }
  function bimDgScreen(o,V,W,H){var P=[],g=o.dg.g,i;for(i=0;i<(g.pts||[]).length;i++)P.push(toScreen(bimDgW(o,g.pts[i]),V,W,H));return P;}
  /* a path over the screen points, broken where a point is behind the eye */
  function bimDgPath(c,P,closed){
    var on=false,q;
    c.beginPath();
    for(q=0;q<P.length;q++){
      if(P[q][2]<=0.5){on=false;continue;}
      if(on)c.lineTo(P[q][0],P[q][1]);else{c.moveTo(P[q][0],P[q][1]);on=true;}
    }
    if(closed)c.closePath();
  }
  /* a canvas the size of the view, cleared, with the view's transform: what is drawn on it is laid
     on the view at one opacity, so overlapping bands and shadows do not darken where they overlap */
  function bimDgOff(ctx,key){
    var cv=ctx.canvas,oc=A3D_DG[key]||(A3D_DG[key]=document.createElement('canvas'));
    if(oc.width!==cv.width)oc.width=cv.width;
    if(oc.height!==cv.height)oc.height=cv.height;
    var c2=oc.getContext('2d');
    c2.setTransform(1,0,0,1,0,0);c2.clearRect(0,0,oc.width,oc.height);
    if(ctx.getTransform)c2.setTransform(ctx.getTransform());
    return c2;
  }
  function bimDgBlit(ctx,c2,alpha){ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=Math.max(0,Math.min(1,alpha));ctx.drawImage(c2.canvas,0,0);ctx.restore();}
  /* under the model: a shadow, or a fill */
  function bimDgDrawUnder(ctx,V,W,H,o){
    var dg=o.dg,g=dg.g,s=dg.s||{},a=bimLayerAlpha(o)*(s.op===undefined?1:s.op)*bimAnimAlpha(o),mo=bimAnimLive()?bimAnimMotion(o):null,P,k,an;   /* __acad3dV170 */
    if(!(a>0))return;
    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a,mo==='sun');return;}
    if(g.kind==='segs'||!g.pts||g.pts.length<3||!s.fill||!g.closed)return;
    if(mo==='ring'){k=bimAnimRingK(o);if(!(k>0))return;P=k<1?bimAnimScreen(o,V,W,H,k):bimDgScreen(o,V,W,H);}else P=bimDgScreen(o,V,W,H);
    ctx.save();
    if(mo==='draw'){an=bimAnimDrawOf(o);if(!(an.a>0)){ctx.restore();return;}a*=an.a;bimAnimClip(ctx,P,an.f,true);}
    bimDgPath(ctx,P,true);ctx.globalAlpha=a*(s.fop===undefined?0.35:s.fop);ctx.fillStyle=s.fill;ctx.fill();ctx.restore();
  }
  /* bands -- a road's noise classes, a slope class -- each analysis's on a canvas of its own, class
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
      if(!i)a=bimLayerAlpha(o)*(s.fop===undefined?0.45:s.fop)*bimAnimAlpha(o);   /* __acad3dV170: revealed in turn */
      for(j=0;j<o.dg.g.bands.length;j++){
        var B=o.dg.g.bands[j],R=B?(B.rings||(B.pts?[B.pts]:null)):null,PP=[];
        if(!R)continue;
        for(k=0;k<R.length;k++){
          if(!R[k]||R[k].length<3)continue;
          var P=[];for(m=0;m<R[k].length;m++)P.push(toScreen(bimDgW(o,R[k][m]),V,W,H));
          PP.push(P);gy=bimDgW(o,R[k][0])[1];
        }
        if(PP.length)T.push({PP:PP,col:(B.rings&&s.fill)?s.fill:B.col,lv:B.lv||0,al:al,eo:!!B.rings,tex:B.tex||null,ink:B.ink||null});   /* __acad3dV168: tex */
      }
    }
    if(!T.length)return;
    T.sort(function(x,y){return x.lv-y.lv;});
    c2=bimDgOff(ctx,'bandCv');
    for(i=0;i<T.length;i++){
      c2.beginPath();for(k=0;k<T[i].PP.length;k++)bimDgSub(c2,T[i].PP[k]);
      c2.globalAlpha=T[i].al;c2.fillStyle=T[i].col;c2.fill(T[i].eo?'evenodd':'nonzero');
      if(T[i].tex){var tp=bimDgTex(c2,T[i].tex,T[i].ink);if(tp){c2.fillStyle=tp;c2.fill(T[i].eo?'evenodd':'nonzero');}}   /* __acad3dV168: the second cue */
      if(T[i].eo){c2.strokeStyle=T[i].col;c2.lineWidth=1;c2.stroke();}   /* over the hairline where two classes meet */
    }
    c2.globalAlpha=1;c2.globalCompositeOperation='destination-out';c2.beginPath();
    for(i=0;i<A3D.objs.length;i++){
      var b=A3D.objs[i],cx=b.context;
      if(!cx||cx.kind!=='buildings'||!cx.footprint||cx.footprint.length<3)continue;
      var q=bimObjOffset(b);
      for(j=0;j<cx.footprint.length;j++){var sp=toScreen([cx.footprint[j][0]+q[0],gy,cx.footprint[j][1]+q[2]],V,W,H);if(j)c2.lineTo(sp[0],sp[1]);else c2.moveTo(sp[0],sp[1]);}
      c2.closePath();
    }
    c2.fill();c2.globalCompositeOperation='source-over';
    bimDgBlit(ctx,c2,a);
  }
  /* over the model: the lines, arrowheads, marks and symbols, drawn; the words queued in Q, to be
     placed by priority (bimDgPlaceLabels); what is drawn is kept to pick */
  function bimDgDrawOver(ctx,V,W,H,o,sel,cap,Q){
    var dg=o.dg,g=dg.g,s=dg.s||{},a=bimLayerAlpha(o)*(s.op===undefined?1:s.op),hit={id:o.id,segs:[],dots:[],boxes:[]},P,i,sp,e,b;
    if(g.kind==='live')return hit;
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
    ctx.globalAlpha=a;ctx.lineJoin='round';ctx.lineCap='butt';
    if(g.kind==='lines'){   /* __acad3dV165: several polylines -- a contour level, the divides */
      var LL=g.lines||[],ln,lp;
      for(ln=0;ln<LL.length;ln++){
        lp=[];for(i=0;i<LL[ln].length;i++)lp.push(toScreen(bimDgW(o,LL[ln][i]),V,W,H));
        if(mOff!==null&&bimAnimOut(o)&&!g.closed)lp=bimAnimOrientLine(o,LL[ln],lp);   /* __acad3dV170 */
        if(lp.length<2)continue;
        if(s.fillOver&&g.closed&&lp.length>2){   /* __acad3dV168: filled over the model -- a building's lid */
          bimDgPath(ctx,lp,true);ctx.globalAlpha=a*(s.fo===undefined?0.85:s.fo);ctx.fillStyle=s.fillOver;ctx.fill();
          if(s.tex){var tq=bimDgTex(ctx,s.tex,s.ink);if(tq){ctx.fillStyle=tq;ctx.fill();}}
          ctx.globalAlpha=a;
        }
        if(sel){bimDgPath(ctx,lp,g.closed);ctx.setLineDash([]);ctx.strokeStyle='#ffd166';ctx.lineWidth=(s.w||1.2)+4;ctx.globalAlpha=Math.min(1,a+0.3);ctx.stroke();ctx.globalAlpha=a;}
        if(s.stroke){bimDgPath(ctx,lp,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.2;bimAnimStroke(ctx,s,s.w||1.2,mOff);ctx.setLineDash([]);}
        for(i=0;i+1<lp.length;i++)if(lp[i][2]>0.5&&lp[i+1][2]>0.5)hit.segs.push([lp[i][0],lp[i][1],lp[i+1][0],lp[i+1][1]]);
        if(g.closed&&lp.length>2&&lp[0][2]>0.5&&lp[lp.length-1][2]>0.5)hit.segs.push([lp[lp.length-1][0],lp[lp.length-1][1],lp[0][0],lp[0][1]]);
      }
    }else if(g.kind==='segs'){
      ctx.beginPath();
      for(i=0;i+1<P.length;i+=2){if(P[i][2]<=0.5||P[i+1][2]<=0.5)continue;ctx.moveTo(P[i][0],P[i][1]);ctx.lineTo(P[i+1][0],P[i+1][1]);hit.segs.push([P[i][0],P[i][1],P[i+1][0],P[i+1][1]]);}
      if(sel){ctx.strokeStyle='#ffd166';ctx.lineWidth=(s.w||1.4)+4;ctx.stroke();}
      if(s.stroke){ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.4;bimAnimStroke(ctx,s,s.w||1.4,mOff);ctx.setLineDash([]);}
    }else if(P.length>=2){
      if(sel){bimDgPath(ctx,P,g.closed);ctx.setLineDash([]);ctx.strokeStyle='#ffd166';ctx.lineWidth=(s.w||1.5)+4;ctx.globalAlpha=Math.min(1,a+0.3);ctx.stroke();ctx.globalAlpha=a;}
      if(s.stroke){bimDgPath(ctx,P,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.5;bimAnimStroke(ctx,s,s.w||1.5,mOff);ctx.setLineDash([]);}
      if(s.head&&P[P.length-1][2]>0.5&&P[P.length-2][2]>0.5){   /* an arrowhead at the end, on the screen */
        e=P[P.length-1];b=P[P.length-2];
        var ang=Math.atan2(e[1]-b[1],e[0]-b[0]),hl=9+(s.w||1.5)*2;
        ctx.beginPath();ctx.moveTo(e[0],e[1]);ctx.lineTo(e[0]-hl*Math.cos(ang-0.42),e[1]-hl*Math.sin(ang-0.42));ctx.lineTo(e[0]-hl*Math.cos(ang+0.42),e[1]-hl*Math.sin(ang+0.42));ctx.closePath();
        ctx.fillStyle=s.stroke||'#e8edf2';ctx.fill();
      }
      for(i=0;i+1<P.length;i++)if(P[i][2]>0.5&&P[i+1][2]>0.5)hit.segs.push([P[i][0],P[i][1],P[i+1][0],P[i+1][1]]);
      if(g.closed&&P.length>2&&P[0][2]>0.5&&P[P.length-1][2]>0.5)hit.segs.push([P[P.length-1][0],P[P.length-1][1],P[0][0],P[0][1]]);
    }
    if(sel&&g.bands){   /* __acad3dV165: a band selected -- a slope class has no line of its own -- its outline lit,
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
      ctx.globalAlpha=a;ctx.fillStyle=s.mark||'#ffd23f';ctx.beginPath();ctx.arc(sp[0],sp[1],sel?5.5:4.5,0,2*Math.PI);ctx.fill();
      hit.dots.push([sp[0],sp[1]]);
      if(g.marks[i].t&&lbOk)Q.push({hit:hit,t:g.marks[i].t,x:sp[0]+8,y:sp[1],col:s.markText||'#f4f1e3',sz:10,al:'left',pri:sel?0:4,a:a,sel:sel,cap:cap});
    }
    if(dg.sym&&dg.sym.p){
      sp=toScreen(bimDgW(o,dg.sym.p),V,W,H);
      if(sp[2]>0.5){
        var sy=dg.sym;
        if(sy.toward){var tw=toScreen(bimDgW(o,sy.toward),V,W,H);sy={type:sy.type,r:sy.r,dir:Math.atan2(tw[1]-sp[1],tw[0]-sp[0])};}
        ctx.globalAlpha=a;var rr=bimDgSym(ctx,sp,sy,dg.sym.col||s.stroke||'#e8edf2',a);
        if(sel){ctx.globalAlpha=1;ctx.strokeStyle='#ffd166';ctx.lineWidth=2;ctx.beginPath();ctx.arc(sp[0],sp[1],rr+3,0,2*Math.PI);ctx.stroke();}
        hit.boxes.push([sp[0]-rr,sp[1]-rr,2*rr,2*rr]);
      }
    }
    for(i=0;i<(dg.lb||[]).length;i++){
      var L=dg.lb[i];if(!L||!L.t||!L.p||!lbOk)continue;
      sp=toScreen(bimDgW(o,L.p),V,W,H);if(sp[2]<=0.5)continue;
      Q.push({hit:hit,t:L.t,x:sp[0]+(L.al==='left'?14:0),y:sp[1],col:L.col||s.stroke,sz:L.sz||11,al:L.al||'center',pri:sel?0:(L.pri||2),a:a,sel:sel,cap:cap});
    }
    if(clip)ctx.restore();
    ctx.globalAlpha=1;
    return hit;
  }
  /* the words, the most telling first: the compass points, then each analysis's own labels, then the
     hours along the sun's paths. One that would cover a word already placed tries a line above or
     below, then gives way -- a diagram is read by what it says, not by how much. The selection's are
     always drawn. */
  /* __acad3dV165: where the words keep clear of, as it is drawn over them later in the frame: the north
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
    for(i=0;i<Q.length;i++)Q[i].n=i;
    Q.sort(function(x,y){return x.pri-y.pri||x.n-y.n;});
    function free(b){for(var j=0;j<placed.length;j++){var p=placed[j];if(b[0]<p[0]+p[2]&&p[0]<b[0]+b[2]&&b[1]<p[1]+p[3]&&p[1]<b[1]+b[3])return false;}return true;}
    for(i=0;i<Q.length;i++){
      var q=Q[i],sz=q.sz||11,h=sz+4,w,x0,dy=null,tries=q.pri===0?[0]:[0,-h,h,-2*h,2*h];
      ctx.font=sz+'px sans-serif';w=ctx.measureText(q.t).width;
      x0=q.al==='left'?q.x:(q.al==='right'?q.x-w:q.x-w/2);
      for(k=0;k<tries.length;k++)if(q.pri===0||free([x0-2,q.y-h/2+tries[k],w+4,h])){dy=tries[k];break;}
      if(dy===null)continue;
      placed.push([x0-2,q.y-h/2+dy,w+4,h]);
      ctx.globalAlpha=q.a;ctx.textAlign=q.al;ctx.textBaseline='middle';
      var bx=bimDgDrawText(ctx,q.t,q.x,q.y+dy,q.col,sz,q.cap);
      if(q.sel){ctx.globalAlpha=1;ctx.strokeStyle='#ffd166';ctx.lineWidth=1;ctx.strokeRect(bx[0]-2,bx[1],bx[2]+4,bx[3]);}
      q.hit.boxes.push(bx);A3D_DG.labelBoxes.push(bx);   /* __acad3dV165 */
    }
    ctx.globalAlpha=1;
  }
  /* a shadow at its date and time, drawn from the model as it is now */
  function bimDgSun(date,time){
    var st=bimSunSettings();
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return null;
    var r=bimSunCalc(st.lat,st.lon,st.tz,date,time);
    return (r&&r.elevation>0)?r:null;
  }
  /* the project's own solids near the site: the context's buildings are what the site is set in */
  function bimDgCasters(gr,c,r,date){
    return bimShadowCasters(gr,date).filter(function(it){
      var o=objById(it.id),k;
      if(!o||o.context)return false;
      for(k=0;k<it.w.length;k+=Math.max(1,Math.floor(it.w.length/8))){var dx=it.w[k][0]-c[0],dz=it.w[k][2]-c[1];if(dx*dx+dz*dz<=r*r)return true;}
      return false;
    });
  }
  function bimDgDrawShadow(ctx,V,W,H,o,a,day){
    var L=o.dg.g.live,mv=!!(day&&L&&A3D_ANIM.sunTime),dt=mv?bimSunSettings().date:(L&&L.date),sun;
    /* __acad3dV170: through the day, one shadow, at the sun's moment on the study's day */
    if(mv){var F=bimAnimFrame();if(F.shadowDone)return;F.shadowDone=true;}
    sun=L?(mv?bimDgSun(dt,A3D_ANIM.sunTime):bimDgSun(L.date,L.time)):null;
    if(!sun)return;
    var sv=bimSunVector(sun),gr=bimShadowGround(),list=bimDgCasters(gr,L.c||[0,0],L.r||200,dt);
    if(!list.length)return;
    var c2=bimDgOff(ctx,'shadowCv');
    c2.globalCompositeOperation='source-over';c2.fillStyle=mv?BIM_ANIM.sun.fill:((o.dg.s&&o.dg.s.fill)||'#5b6c8a');
    bimFillProjected(c2,list,function(p){return bimShadowPoint(p,sv,gr);},V,W,H,gr);
    c2.globalCompositeOperation='destination-out';   /* not under the buildings themselves */
    bimFillProjected(c2,list,function(p){return [p[0],p[2]];},V,W,H,gr);
    c2.globalCompositeOperation='source-over';
    bimDgBlit(ctx,c2,a*((o.dg.s&&o.dg.s.fop!==undefined)?o.dg.s.fop:0.4));
  }
  /* pass 'under' before the model, 'over' after it */
  function drawDiagrams(ctx,V,W,H,pass){
    var over=pass!=='under',L=bimDgDiags(),cap=!!A3D.sheetCapture,sel={},bands=[],Q=[],i;
    if(over)A3D_DG.hits=[];
    if(!L.length)return;
    (A3D.selSet||[]).forEach(function(id){sel[id]=1;});if(A3D.sel)sel[A3D.sel]=1;
    ctx.save();
    try{
      for(i=0;i<L.length;i++){
        if(!bimLayerShown(L[i]))continue;
        if(over)A3D_DG.hits.push(bimDgDrawOver(ctx,V,W,H,L[i],!!sel[L[i].id],cap,Q));
        else if(L[i].dg.g.bands&&L[i].dg.g.bands.length)bands.push(L[i]);
        else bimDgDrawUnder(ctx,V,W,H,L[i]);
      }
      if(bands.length)bimDgDrawBands(ctx,V,W,H,bands);
      if(over&&bimAnimLive())bimAnimDrawSun(ctx,V,W,H,Q);   /* __acad3dV170 */
      if(over){A3D_DG.ly=bimDgLegendLayout(ctx,W,H);A3D_DG.lyCtx=ctx;A3D_DG.lyFrame=A3D.frames;}   /* __acad3dV165: the key first, for the words to keep clear of */
      if(Q.length)bimDgPlaceLabels(ctx,Q,bimDgKeepClear(W,H));
    }catch(eD){
      console.warn('[BIM] The site analysis could not be drawn',eD);
      if(!A3D_DG.warned){A3D_DG.warned=true;a3dToast('The site analysis could not be drawn - see the console');}
    }
    ctx.restore();
  }
