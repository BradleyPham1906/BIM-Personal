"""patch_phase164a.py -- V164: site analysis drawn in the model, the engine.

reference/research-site-analysis-in-model.md, section 7. The owner: "a live analysis that is
editable". Each analysis draws its diagram as elements of the model -- objects of their own kind,
'diag', on a layer of their own under Site analysis:
  live       an analysis lays its elements down again whenever it runs
  editable   select, move, turn, mirror, scale, restyle, relabel or delete an element; what the owner
             changed is kept through a run and can be reset, what they deleted stays deleted
  explained  Properties gives the element's reading, how it was worked out, and its source and date
  drawn      the colour under the model, the lines, symbols and words over it, a legend on the view
  apart      no mesh: schedules, quantities, the LOD checks and the exports pass them by
pushUndo gains a hold, so one run of many steps is one undo step.
"""
import hashlib, pathlib, sys

SRC = pathlib.Path('canvas_v10.html')
BASE = '7fac61cb6717f63cd883c9471ada85eca6608c26e67febc3a1edf8db10161e8a'   # the V163 build

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


ENGINE = r"""  /* ================= __acad3dV164: site analysis drawn in the model =================
     reference/research-site-analysis-in-model.md. The owner: "a live analysis that is editable".
     Each analysis draws its diagram as elements of the model -- objects of their own kind, 'diag',
     on a layer of their own under Site analysis -- so each can be selected, moved, turned, restyled,
     relabelled or deleted like anything drawn by hand, and each is live: the analysis lays it down
     again whenever it runs.

     An element keeps the analysis's own version of itself (gen). One the owner has changed -- moved,
     turned, restyled, relabelled -- no longer matches it, and a run leaves it as it is (marking it
     when the analysis would now draw it differently); one the owner deleted stays deleted; Reset
     gives either back to the analysis. That is worked out by comparison when a run comes, so no
     editing path has to report itself.

     An element: {t:'diag', name, layer, pos, dg:{a, k, g, s, lb, sym, info, gen}}
       a, k   the analysis and the element's key within it
       g      its geometry, in metres, [x, y, z] points about pos:
                line   pts, closed            segs   pts in pairs
                marks  pts (a path), marks [{p, t}] (dots with labels on it)
                live   {kind:'shadow', date, time, c, r}: drawn from the model each time, never stored
                bands  [{lv, col, pts}]: areas in classes (a road's noise), the higher class over
       s      stroke, fill, w (pixels), dash, op, fop (the fill's opacity), head (an arrowhead)
       lb     labels [{t, p, sz, col, al, pri}]: placed by priority, so none is drawn over another
       sym    a symbol {type:'noise'|'storm'|'dot', p, r, col, toward}
       info   {title, rows:[[label, value]], method, source, date}
     The colour -- bands, fills, shadows -- is drawn under the model, as the result layers are; the
     lines, symbols and words over it, so a building never hides what it is measured against.
     Diagram elements carry no mesh, so schedules, quantities, the LOD checks and the IFC, DXF and
     CityJSON exports, which read meshes and building types, pass them by. */
  var A3D_DG={hits:[],legend:null,warned:false,shadowCv:null,bandCv:null};
  var BIM_DG_AN=[
    {id:'frame',name:'Compass and distance',col:'#c9d3dd'},
    {id:'sun',name:'Sun paths',col:'#ffb347'},
    {id:'shadow',name:'Shadows',col:'#7c8db0'},
    {id:'wind',name:'Winds',col:'#7fd3e6'},
    {id:'views',name:'Views',col:'#8fd694'},
    {id:'noise',name:'Noise',col:'#f08a24'}];
  function bimDgAn(id){var i;for(i=0;i<BIM_DG_AN.length;i++)if(BIM_DG_AN[i].id===id)return BIM_DG_AN[i];return null;}
  function bimIsDiag(o){return !!(o&&o.t==='diag'&&o.dg&&o.dg.g);}
  function bimDgState(){
    A3D.site=A3D.site||{};
    var D=A3D.site.diag;
    if(!D||typeof D!=='object')D=A3D.site.diag={};
    if(!D.runs||typeof D.runs!=='object')D.runs={};
    if(!D.layers||typeof D.layers!=='object')D.layers={};
    return D;
  }
  function bimDgCore(dg){return JSON.stringify({g:dg.g,s:dg.s||{},lb:dg.lb||[],sym:dg.sym||null});}
  /* changed by the owner: moved, or not as the analysis drew it */
  function bimDgEdited(o){
    var q=o.pos||[0,0,0];
    return !!(q[0]||q[1]||q[2])||!o.dg.gen||bimDgCore(o.dg)!==o.dg.gen;
  }
  function bimDgW(o,p){var q=bimObjOffset(o);return [p[0]+q[0],(p[1]||0)+q[1],p[2]+q[2]];}
  function bimDgDiags(a){return A3D.objs.filter(function(x){return bimIsDiag(x)&&(!a||x.dg.a===a);});}
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
    return bimDgLayer(a,'Site analysis - '+A.name,A.col,'root',false);
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
      legend:run&&run.legend?run.legend:[],note:run&&run.note?run.note:'',source:run&&run.source?run.source:''};
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
    var dg=o.dg,g=dg.g,s=dg.s||{},a=bimLayerAlpha(o)*(s.op===undefined?1:s.op);
    if(g.kind==='live'){bimDgDrawShadow(ctx,V,W,H,o,a);return;}
    if(g.kind==='segs'||!g.pts||g.pts.length<3||!s.fill||!g.closed)return;
    ctx.save();bimDgPath(ctx,bimDgScreen(o,V,W,H),true);ctx.globalAlpha=a*(s.fop===undefined?0.35:s.fop);ctx.fillStyle=s.fill;ctx.fill();ctx.restore();
  }
  /* bands -- a road's noise classes -- of every element on one canvas, class by class, so where two
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
    P=bimDgScreen(o,V,W,H);
    ctx.globalAlpha=a;ctx.lineJoin='round';ctx.lineCap='butt';
    if(g.kind==='segs'){
      ctx.beginPath();
      for(i=0;i+1<P.length;i+=2){if(P[i][2]<=0.5||P[i+1][2]<=0.5)continue;ctx.moveTo(P[i][0],P[i][1]);ctx.lineTo(P[i+1][0],P[i+1][1]);hit.segs.push([P[i][0],P[i][1],P[i+1][0],P[i+1][1]]);}
      if(sel){ctx.strokeStyle='#ffd166';ctx.lineWidth=(s.w||1.4)+4;ctx.stroke();}
      if(s.stroke){ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.4;ctx.stroke();ctx.setLineDash([]);}
    }else if(P.length>=2){
      if(sel){bimDgPath(ctx,P,g.closed);ctx.setLineDash([]);ctx.strokeStyle='#ffd166';ctx.lineWidth=(s.w||1.5)+4;ctx.globalAlpha=Math.min(1,a+0.3);ctx.stroke();ctx.globalAlpha=a;}
      if(s.stroke){bimDgPath(ctx,P,g.closed);ctx.setLineDash(s.dash||[]);ctx.strokeStyle=s.stroke;ctx.lineWidth=s.w||1.5;ctx.stroke();ctx.setLineDash([]);}
      if(s.head&&P[P.length-1][2]>0.5&&P[P.length-2][2]>0.5){   /* an arrowhead at the end, on the screen */
        e=P[P.length-1];b=P[P.length-2];
        var ang=Math.atan2(e[1]-b[1],e[0]-b[0]),hl=9+(s.w||1.5)*2;
        ctx.beginPath();ctx.moveTo(e[0],e[1]);ctx.lineTo(e[0]-hl*Math.cos(ang-0.42),e[1]-hl*Math.sin(ang-0.42));ctx.lineTo(e[0]-hl*Math.cos(ang+0.42),e[1]-hl*Math.sin(ang+0.42));ctx.closePath();
        ctx.fillStyle=s.stroke||'#e8edf2';ctx.fill();
      }
      for(i=0;i+1<P.length;i++)if(P[i][2]>0.5&&P[i+1][2]>0.5)hit.segs.push([P[i][0],P[i][1],P[i+1][0],P[i+1][1]]);
      if(g.closed&&P.length>2&&P[0][2]>0.5&&P[P.length-1][2]>0.5)hit.segs.push([P[P.length-1][0],P[P.length-1][1],P[0][0],P[0][1]]);
    }
    if(g.marks)for(i=0;i<g.marks.length;i++){
      sp=toScreen(bimDgW(o,g.marks[i].p),V,W,H);if(sp[2]<=0.5)continue;
      ctx.globalAlpha=a;ctx.fillStyle=s.mark||'#ffd23f';ctx.beginPath();ctx.arc(sp[0],sp[1],sel?5.5:4.5,0,2*Math.PI);ctx.fill();
      hit.dots.push([sp[0],sp[1]]);
      if(g.marks[i].t)Q.push({hit:hit,t:g.marks[i].t,x:sp[0]+8,y:sp[1],col:s.markText||'#f4f1e3',sz:10,al:'left',pri:sel?0:4,a:a,sel:sel,cap:cap});
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
      var L=dg.lb[i];if(!L||!L.t||!L.p)continue;
      sp=toScreen(bimDgW(o,L.p),V,W,H);if(sp[2]<=0.5)continue;
      Q.push({hit:hit,t:L.t,x:sp[0]+(L.al==='left'?14:0),y:sp[1],col:L.col||s.stroke,sz:L.sz||11,al:L.al||'center',pri:sel?0:(L.pri||2),a:a,sel:sel,cap:cap});
    }
    ctx.globalAlpha=1;
    return hit;
  }
  /* the words, the most telling first: the compass points, then each analysis's own labels, then the
     hours along the sun's paths. One that would cover a word already placed tries a line above or
     below, then gives way -- a diagram is read by what it says, not by how much. The selection's are
     always drawn. */
  function bimDgPlaceLabels(ctx,Q){
    var placed=[],i,k;
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
      q.hit.boxes.push(bx);
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
  function bimDgCasters(gr,c,r){
    return bimShadowCasters(gr).filter(function(it){
      var o=objById(it.id),k;
      if(!o||o.context)return false;
      for(k=0;k<it.w.length;k+=Math.max(1,Math.floor(it.w.length/8))){var dx=it.w[k][0]-c[0],dz=it.w[k][2]-c[1];if(dx*dx+dz*dz<=r*r)return true;}
      return false;
    });
  }
  function bimDgDrawShadow(ctx,V,W,H,o,a){
    var L=o.dg.g.live,sun=L?bimDgSun(L.date,L.time):null;
    if(!sun)return;
    var sv=bimSunVector(sun),gr=bimShadowGround(),list=bimDgCasters(gr,L.c||[0,0],L.r||200);
    if(!list.length)return;
    var c2=bimDgOff(ctx,'shadowCv');
    c2.globalCompositeOperation='source-over';c2.fillStyle=(o.dg.s&&o.dg.s.fill)||'#5b6c8a';
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
      if(Q.length)bimDgPlaceLabels(ctx,Q);
    }catch(eD){
      console.warn('[BIM] The site analysis could not be drawn',eD);
      if(!A3D_DG.warned){A3D_DG.warned=true;a3dToast('The site analysis could not be drawn - see the console');}
    }
    ctx.restore();
  }
  /* what is under the pointer: a line, a dot, a label or a symbol of a diagram, drawn over the
     model and so picked before it. A band, a fill or a shadow is picked by its lines and words only,
     so it never covers the model it lies over. */
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
  /* turned, mirrored or scaled: the plan coordinates of every point, label and symbol */
  function bimDgTransformed(dg,tp){
    function P(p){var w=tp([p[0],p[2]]);return [w[0],p[1],w[1]];}
    var g=JSON.parse(JSON.stringify(dg.g)),lb=JSON.parse(JSON.stringify(dg.lb||[])),sym=dg.sym?JSON.parse(JSON.stringify(dg.sym)):null;
    if(g.pts)g.pts=g.pts.map(P);
    if(g.marks)g.marks.forEach(function(m){m.p=P(m.p);});
    if(g.bands)g.bands.forEach(function(B){B.pts=B.pts.map(P);});
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
    (g.bands||[]).forEach(function(B){(B.pts||[]).forEach(function(p){P.push(p);});});
    (o.dg.lb||[]).forEach(function(L){if(L.p)P.push(L.p);});
    if(o.dg.sym&&o.dg.sym.p)P.push(o.dg.sym.p);
    for(i=0;i<P.length;i++)P[i]=bimDgW(o,P[i]);
    return P;
  }
  /* ---- the legend, on the view: each analysis shown, its key and its source ----
     A key, not a list: each analysis's title, then its swatches with short names flowing in lines,
     then its source, shortened to fit. Not on a view under 620 px, a phone's: there it would cover
     the drawing and the tools, and each analysis's key is in its row in Analyze. */
  function bimDgFit(ctx,t,w){
    if(ctx.measureText(t).width<=w)return t;
    while(t.length>1&&ctx.measureText(t+'\u2026').width>w)t=t.slice(0,-1);
    return t+'\u2026';
  }
  function drawDiagramLegend(ctx,V,W,H){
    A3D_DG.legend=null;
    if(A3D.sheetCapture||A3D_PLOT.on)return;
    var D=bimDgState(),sr=bimSafeViewRect();
    if(D.legendOff||sr.w<620)return;
    var blocks=[],i;
    for(i=0;i<BIM_DG_AN.length;i++){
      var A=BIM_DG_AN[i],R=D.runs[A.id];
      if(!R)continue;
      if(!bimDgDiags(A.id).some(function(o){return bimLayerShown(o);}))continue;   /* a layer off or frozen, its own or one above it: none of it shown */
      blocks.push({title:A.name,rows:(R.legend||[]).slice(0,8),src:R.source||'',drawn:[]});
    }
    if(!blocks.length)return;
    ctx.save();
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
      ctx.globalAlpha=1;ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(X,Y,w,h);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(X+0.5,Y+0.5,w-1,h-1);
      ctx.beginPath();ctx.rect(X,Y,w,h);ctx.clip();
      ctx.textBaseline='middle';ctx.textAlign='left';
      for(i=0;i<ops.length;i++){
        var op=ops[i],ox=X+op.x,oy=Y+op.y;
        if(op.k==='t'){ctx.font='bold 11px sans-serif';ctx.fillStyle='#e8edf2';ctx.fillText(op.t,ox,oy);continue;}
        if(op.k==='s'){ctx.font='10px sans-serif';ctx.fillStyle='#9aa7b4';ctx.fillText(op.t,ox,oy);continue;}
        var rr=op.r;ctx.strokeStyle=rr.col;ctx.fillStyle=rr.col;ctx.lineWidth=2;
        if(rr.kind==='fill'){ctx.globalAlpha=0.75;ctx.fillRect(ox,oy-5,sw,10);ctx.globalAlpha=1;}
        else if(rr.kind==='dot'){ctx.beginPath();ctx.arc(ox+sw/2,oy,4,0,2*Math.PI);ctx.fill();}
        else{ctx.setLineDash(rr.kind==='dash'?[4,3]:[]);ctx.beginPath();ctx.moveTo(ox,oy);ctx.lineTo(ox+sw,oy);ctx.stroke();ctx.setLineDash([]);}
        ctx.font='11px sans-serif';ctx.fillStyle='#e8edf2';ctx.fillText(op.t,ox+sw+4,oy);
      }
      A3D_DG.legend={box:[X,Y,w,h],blocks:blocks.map(function(bb){return {title:bb.tt,rows:bb.drawn,src:bb.st||''};})};   /* what was drawn, as drawn */
    }catch(eL){console.warn('[BIM] The site analysis legend could not be drawn',eL);}
    ctx.restore();
  }
  /* ---- Properties: what it is, how it was worked out, how it looks ---- */
  function bimDgPropsHtml(o){
    var dg=o.dg,A=bimDgAn(dg.a)||{name:dg.a},info=dg.info||{},ed=bimDgEdited(o),s=dg.s||{},live=dg.g.kind==='live',h='',r='',i;
    h+='<div class="a3d-ptypehd"><div class="a3d-ptypeic">'+(a3drIcon('bim:analyses')||a3drIcon('box'))+'</div>'+
      '<div class="a3d-ptypetx"><div class="a3d-ptypename">'+bimEsc(o.name)+'</div><div class="a3d-ptypesub">'+bimEsc(bimObjTypeLabel(o))+'</div></div></div>';
    if(info.title)r+=bimPropText('What It Shows',info.title);
    (info.rows||[]).forEach(function(row){r+=bimPropText(row[0],row[1]);});
    h+=bimPropGroup('Reading',r);
    r='';
    if(info.method)r+=bimPropText('Method',info.method);
    if(info.source)r+=bimPropText('Source',info.source+(info.date?', '+info.date:''));
    h+=bimPropGroup('How It Was Worked Out',r);
    r='';
    if(!live)r+=bimPropRow('Line Colour','<input type="color" data-dgf="stroke" value="'+bimEsc(/^#[0-9a-f]{6}$/i.test(s.stroke||'')?s.stroke:'#c9d3dd')+'">');
    if(s.fill!==undefined||live)r+=bimPropRow('Fill Colour','<input type="color" data-dgf="fill" value="'+bimEsc(/^#[0-9a-f]{6}$/i.test(s.fill||'')?s.fill:'#5b6c8a')+'">');
    if(!live)r+=bimPropRow('Line Width (px)','<input type="number" min="0.5" max="12" step="0.5" data-dgf="w" value="'+(s.w||1.5)+'">');
    if(!live)r+=bimPropRow('Dashed','<input type="checkbox" data-dgf="dash"'+(s.dash&&s.dash.length?' checked':'')+'>');
    r+=bimPropRow('Opacity (%)','<input type="number" min="10" max="100" step="5" data-dgf="op" value="'+Math.round((s.op===undefined?1:s.op)*100)+'">');
    for(i=0;i<(dg.lb||[]).length;i++)if(dg.lb[i]&&dg.lb[i].t!==undefined)r+=bimPropRow(i?'Label '+(i+1):'Label','<input type="text" maxlength="120" data-dgf="lb:'+i+'" value="'+bimEsc(dg.lb[i].t)+'">');
    r+=bimPropRow('Layer','<select data-propf="layer">'+bimLayerOptionsHtml(o.layer||A3D.activeLayer)+'</select>');
    h+=bimPropGroup('Appearance',r);
    r=bimPropText('Status',dg.orphan?'Changed by you; the analysis no longer draws it':(!dg.gen?'Yours: a copy, which the analysis does not draw':(ed?'Changed by you: kept when the analysis runs again':'As the analysis drew it')));
    if(dg.newer)r+=bimPropText('Newer','The analysis would draw it differently now: Reset takes its version');
    r+=bimPropRow('','<button type="button" class="a3d-pedit" data-dgact="reset"'+((ed||dg.newer)&&dg.gen?'':' disabled')+'>Reset to the analysis</button> '+
      '<button type="button" class="a3d-pedit" data-dgact="rerun">Run the analysis again</button>');
    h+=bimPropGroup('Analysis',r);
    return h;
  }
  function bimDgSet(o,f,v){
    if(!bimIsDiag(o))return false;
    var s=o.dg.s=o.dg.s||{},n=parseFloat(v),li=String(f).indexOf('lb:')===0?parseInt(String(f).slice(3),10):-1;
    /* checked before the undo step, so a refused value leaves none */
    if((f==='stroke'||f==='fill')&&!/^#[0-9a-f]{6}$/i.test(String(v)))return false;
    if(f==='w'&&(!isFinite(n)||n<0.5||n>12)){a3dToast('A line width is 0.5 to 12 pixels');refreshProps();return false;}
    if(f==='op'&&(!isFinite(n)||n<10||n>100)){a3dToast('Opacity is 10 to 100%');refreshProps();return false;}
    if(li>=0&&!(o.dg.lb&&o.dg.lb[li]))return false;
    if(!(f==='stroke'||f==='fill'||f==='w'||f==='dash'||f==='op'||li>=0))return false;
    pushUndo();
    if(f==='stroke'||f==='fill')s[f]=String(v).toLowerCase();
    else if(f==='w')s.w=n;
    else if(f==='dash')s.dash=v?[6,4]:null;
    else if(f==='op')s.op=Math.round(n)/100;
    else o.dg.lb[li].t=String(v).slice(0,120);
    refreshProps();paint();saveSoon();
    return true;
  }
  function bimDgPropChange(ev){
    var e=ev.target,f=e&&e.getAttribute?e.getAttribute('data-dgf'):null,o;
    if(!f)return;
    o=objById(A3D.sel);
    if(!bimIsDiag(o))return;
    bimDgSet(o,f,e.type==='checkbox'?e.checked:e.value);
  }
  function bimDgPropClick(ev){
    var b=ev.target&&ev.target.closest?ev.target.closest('[data-dgact]'):null,o;
    if(!b||b.disabled)return;
    o=objById(A3D.sel);
    if(!bimIsDiag(o))return;
    if(b.getAttribute('data-dgact')==='reset')bimDgReset(o.id);
    else if(b.getAttribute('data-dgact')==='rerun')bimDgRunAll(o.dg.a);
  }
"""

# the engine, at the same level as the site analysis it serves
rep("  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================\n",
    ENGINE + "  /* ================= __acad3dV158: Site analysis SA1, the workspace and the standard =================\n")

# one run of many steps, one undo step
rep("  function pushUndo(){\n    if(undoSuspend)return;\n",
    "  /* __acad3dV164: held while a run of many steps is under way, after the one snapshot it takes */\n"
    "  var bimUndoHold=false;\n"
    "  function pushUndo(){\n    if(undoSuspend||bimUndoHold)return;\n")

# picked after the notes, which are drawn over them, and before the dimensions and the model under them
rep("    var nt=bimPickNote(x,y);\n    if(nt)return nt;\n",
    "    var nt=bimPickNote(x,y);\n    if(nt)return nt;\n"
    "    var dgp=bimPickDiag(x,y);   /* __acad3dV164: the site analysis, drawn over the model */\n"
    "    if(dgp)return dgp;\n")

# paint: the colour under the model, the lines and words over it, the legend with the others
rep("drawResultLayers(ctx,V,W,H); /* __acad3dV148: the results kept as layers, over the live ones */\n",
    "drawResultLayers(ctx,V,W,H); /* __acad3dV148: the results kept as layers, over the live ones */\n"
    "    drawDiagrams(ctx,V,W,H,'under');         /* __acad3dV164: the site analysis's bands, fills and shadows */\n")
rep("    drawStructResults(ctx,V,W,H);      /* __acad3dV125: the analysis display */\n",
    "    drawStructResults(ctx,V,W,H);      /* __acad3dV125: the analysis display */\n"
    "    drawDiagrams(ctx,V,W,H,'over');    /* __acad3dV164: the site analysis's lines, symbols and words */\n")
rep("    drawLensLegend(ctx,V,W,H);         /* __acad3dV136: the lens's and the data layers' legend, below it */\n",
    "    drawLensLegend(ctx,V,W,H);         /* __acad3dV136: the lens's and the data layers' legend, below it */\n"
    "    drawDiagramLegend(ctx,V,W,H);      /* __acad3dV164: the site analysis's, at the top right */\n")

# turned, mirrored, scaled
rep("    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};\n",
    "    if(bimIsDiag(o)){   /* __acad3dV164 */\n"
    "      if(o.dg.g.kind==='live')return {error:'A live shadow follows the sun and the model: it cannot be turned, mirrored or scaled'};\n"
    "      return bimDgTransformed(o.dg,transformPt);\n"
    "    }\n"
    "    if(o.t==='sketch')return {kind:'sketch',pts:o.pts.map(transformPt),y:o.y};\n")
rep("    else if(g.kind==='pos'){o.pos=g.pos;}\n",
    "    else if(g.kind==='pos'){o.pos=g.pos;}\n"
    "    else if(g.kind==='diag'){o.dg.g=g.g;o.dg.lb=g.lb;o.dg.sym=g.sym;}   /* __acad3dV164 */\n", 2)
rep("    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' mirror';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}\n",
    "    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' mirror';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}\n"
    "    else if(g.kind==='diag')bimDgCopy(o,g,copy,'mirror');   /* __acad3dV164 */\n")
rep("    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' copy';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}\n    else return null;\n",
    "    else if(g.kind==='pos'){copy.t=o.t;copy.name=o.name+' copy';copy.pos=g.pos;if(o.prm)copy.prm=JSON.parse(JSON.stringify(o.prm));}\n"
    "    else if(g.kind==='diag')bimDgCopy(o,g,copy,'copy');   /* __acad3dV164 */\n    else return null;\n")

# fitted to, and the gizmo's centre
rep("      }else if(o.pts&&o.pts.length){\n        /* Sketches and rooms have no mesh.",
    "      }else if(bimIsDiag(o)){   /* __acad3dV164: a diagram's points, labels and symbols */\n"
    "        var dgb=bimDgBounds(o);\n"
    "        for(j=0;j<dgb.length;j++)for(k=0;k<3;k++){if(dgb[j][k]<mn[k])mn[k]=dgb[j][k];if(dgb[j][k]>mx[k])mx[k]=dgb[j][k];any=true;}\n"
    "      }else if(o.pts&&o.pts.length){\n        /* Sketches and rooms have no mesh.")

# Properties
rep("      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */\n      return;\n    }\n",
    "      bimRenderInto(el.propsbody,bimModelPropsHtml());   /* __acad3dV118 */\n      return;\n    }\n"
    "    if(bimIsDiag(o)){bimRenderInto(el.propsbody,bimDgPropsHtml(o));return;}   /* __acad3dV164: a site analysis element */\n")
rep("  function bimObjTypeLabel(o){\n",
    "  function bimObjTypeLabel(o){\n"
    "    if(bimIsDiag(o))return 'Site analysis : '+((bimDgAn(o.dg.a)||{}).name||'Diagram');   /* __acad3dV164 */\n")
rep("    /* __acad3dV125: the Structural and Analysis pages */\n",
    "    /* __acad3dV164: a site analysis element's appearance, Reset and Run again */\n"
    "    if(el.propsbody)el.propsbody.addEventListener('change',function(ev){\n"
    "      try{bimDgPropChange(ev);}catch(eDC){console.warn('[BIM] Site analysis element edit failed',eDC);a3dToast('That could not be changed - see the console');}\n"
    "    });\n"
    "    if(el.propsbody)el.propsbody.addEventListener('click',function(ev){\n"
    "      try{bimDgPropClick(ev);}catch(eDK){console.warn('[BIM] Site analysis element action failed',eDK);a3dToast('That did not work - see the console');}\n"
    "    });\n"
    "    /* __acad3dV125: the Structural and Analysis pages */\n")

out = txt.encode('utf-8')
SRC.write_bytes(out)
print('wrote %s: %d bytes, sha256 %s' % (SRC, len(out), hashlib.sha256(out).hexdigest()))
