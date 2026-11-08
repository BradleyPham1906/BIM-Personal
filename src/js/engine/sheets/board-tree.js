
  /* ================= __acad3dV174a: a board's element tree =================
     docs/research/research-presentation-boards.md, 4.1 to 4.3 and D1 to D5, D19. A board one designs keeps one
     tree of elements (B.els), the bottom of the list first: the order is the drawing order, the last drawn in front,
     as PDF, SVG, Figma and Penpot keep it. Every element has its box in millimetres on the board (1408 px across is
     400 mm, A3 landscape inside its 10 mm margins, as a board prints), an opacity, a blend mode, lock, hide and a mask
     flag; frames and groups have children. A figure of the board (V172b's list) is an element of the tree, 'fig',
     that names its figure: its place stays in the list, in columns, so every path that arranges figures is unchanged
     and a board made before V174 looks as it did (D19). The tree is made at the first change that needs it.
     Functions only, no tables made at load: a project is read before this file has run (bimPresValid). */
  function bimBtrPxMm(){return 3.52;}   /* px per mm: 1408 px over 400 mm */
  function bimBtrMax(){return {nodes:400,depth:8};}
  /* the W3C 16 under Figma's names, in Figma's order (D2), and Pass through for frames and groups (D3):
     [key, name, CSS and canvas keyword] */
  function bimBtrBlends(){
    return [['pass','Pass through',''],['normal','Normal','normal'],['darken','Darken','darken'],['multiply','Multiply','multiply'],
      ['color-burn','Color burn','color-burn'],['lighten','Lighten','lighten'],['screen','Screen','screen'],['color-dodge','Color dodge','color-dodge'],
      ['overlay','Overlay','overlay'],['soft-light','Soft light','soft-light'],['hard-light','Hard light','hard-light'],['difference','Difference','difference'],
      ['exclusion','Exclusion','exclusion'],['hue','Hue','hue'],['saturation','Saturation','saturation'],['color','Color','color'],['luminosity','Luminosity','luminosity']];
  }
  function bimBtrBlend(k){var L=bimBtrBlends(),i;for(i=0;i<L.length;i++)if(L[i][0]===k)return L[i];return null;}
  /* the kinds: [key, name, a container, can be a mask] */
  function bimBtrKinds(){
    return [['frame','Frame',1,0],['group','Group',1,0],['rect','Rectangle',0,1],['ellipse','Ellipse',0,1],['line','Line',0,1],
      ['poly','Polygon',0,1],['star','Star',0,1],['text','Text',0,0],['image','Image',0,1],['fig','Figure',0,0]];
  }
  function bimBtrKind(t){var L=bimBtrKinds(),i;for(i=0;i<L.length;i++)if(L[i][0]===t)return L[i];return null;}
  function bimBtrIsBox(n){return !!n&&(n.t==='frame'||n.t==='group');}
  function bimBtrMaskTypes(){return [['alpha','Alpha'],['vector','Vector'],['lum','Luminance']];}
  /* ---- the record ---- */
  function bimBtrNum(v,lo,hi,d){v=typeof v==='number'&&isFinite(v)?v:d;return Math.max(lo,Math.min(hi,Math.round(v*1000)/1000));}
  function bimBtrCol(v,d){
    if(v==='none')return 'none';
    if(typeof v==='string'&&/^#[0-9a-fA-F]{6}$/.test(v))return v.toLowerCase();
    return d;
  }
  /* one element, good or null; seen: the ids so far; depth: how deep it is */
  function bimBtrNode(n,seen,depth,cnt){
    var K,r,ch,i,c,bl;
    if(!n||typeof n!=='object'||typeof n.t!=='string')return null;
    K=bimBtrKind(n.t);if(!K)return null;
    if(cnt.n>=bimBtrMax().nodes)return null;
    if(typeof n.id!=='string'||!/^e\d{1,6}$/.test(n.id)||seen[n.id])return null;
    seen[n.id]=1;cnt.n++;
    r={id:n.id,t:n.t};
    if(typeof n.nm==='string'&&n.nm.replace(/\s+/g,''))r.nm=n.nm.replace(/\s+/g,' ').trim().slice(0,80);
    if(n.t==='fig'){
      if(typeof n.k!=='string'||!/^f\d{1,6}$/.test(n.k))return null;
      r.k=n.k;
    }else if(n.t!=='group'){
      r.x=bimBtrNum(n.x,-2000,20000,0);r.y=bimBtrNum(n.y,-2000,20000,0);
      if(n.t==='line'){r.w=bimBtrNum(n.w,-20000,20000,40);r.h=bimBtrNum(n.h,-20000,20000,0);}
      else{r.w=bimBtrNum(n.w,0.5,20000,40);r.h=bimBtrNum(n.h,0.5,20000,30);}
    }
    r.op=bimBtrNum(n.op,0,1,1);
    bl=bimBtrIsBox(n)?'pass':'normal';
    r.bm=(typeof n.bm==='string'&&bimBtrBlend(n.bm)&&(n.bm!=='pass'||bimBtrIsBox(n)))?n.bm:bl;
    if(n.lock===true)r.lock=true;
    if(n.hide===true)r.hide=true;
    if(K[3]&&(n.mask==='alpha'||n.mask==='vector'||n.mask==='lum'))r.mask=n.mask;
    if(n.t==='rect'||n.t==='ellipse'||n.t==='poly'||n.t==='star'||n.t==='frame'){
      r.fill=bimBtrCol(n.fill,n.t==='frame'?'#ffffff':'#c3c2b7');
      if(n.t!=='frame')r.fop=bimBtrNum(n.fop,0,1,1);
    }
    if(n.t==='rect'||n.t==='ellipse'||n.t==='poly'||n.t==='star'||n.t==='line'||n.t==='frame'){
      r.stroke=bimBtrCol(n.stroke,n.t==='line'?'#0b0b0b':'none');
      r.sw=bimBtrNum(n.sw,0,50,n.t==='line'?0.5:0.35);
    }
    if(n.t==='rect'||n.t==='frame')r.r=bimBtrNum(n.r,0,1000,0);
    if(n.t==='poly')r.n=Math.round(bimBtrNum(n.n,3,60,6));
    if(n.t==='star'){r.n=Math.round(bimBtrNum(n.n,3,60,5));r.ri=bimBtrNum(n.ri,0.05,0.95,0.38);}
    if(n.t==='line'){if(n.a0===true)r.a0=true;if(n.a1===true)r.a1=true;}
    if(n.t==='frame')r.clip=n.clip!==false;
    if(n.t==='text'){
      r.s=typeof n.s==='string'?n.s.slice(0,4000):'Text';
      r.fs=bimBtrNum(n.fs,4,400,14);
      r.fw=n.fw===700?700:400;
      r.al=(n.al==='center'||n.al==='right')?n.al:'left';
      r.col=bimBtrCol(n.col,'#0b0b0b');if(r.col==='none')r.col='#0b0b0b';
      r.fit=(n.fit==='auto-w'||n.fit==='fixed')?n.fit:'auto-h';
    }
    if(n.t==='image'){
      r.src=typeof n.src==='string'&&/^h[0-9a-f]{16}$/.test(n.src)?n.src:'';
      r.fit=(n.fit==='fit'||n.fit==='tile')?n.fit:'fill';
    }
    if(K[2]){
      if(depth>=bimBtrMax().depth)return null;
      ch=[];
      if(Array.isArray(n.ch))for(i=0;i<n.ch.length;i++){c=bimBtrNode(n.ch[i],seen,depth+1,cnt);if(c)ch.push(c);}
      if(n.t==='group'&&!ch.length)return null;   /* a group is its children: an empty one is nothing */
      r.ch=ch;
    }
    return r;
  }
  /* a board's tree as saved, good, or null when it has none; figs: its figures, to drop an element whose figure is gone */
  function bimBtrValid(L,figs){
    if(!Array.isArray(L))return null;
    var seen={},cnt={n:0},out=[],i,n;
    for(i=0;i<L.length;i++){n=bimBtrNode(L[i],seen,0,cnt);if(n)out.push(n);}
    return bimBtrSync(out,figs||[]);
  }
  /* ---- walking ---- */
  /* fn(node, parent or null, list, index, depth); a true return stops the walk */
  function bimBtrWalk(L,fn,par,depth){
    var i;depth=depth||0;
    for(i=0;i<L.length;i++){
      if(fn(L[i],par||null,L,i,depth))return true;
      if(L[i].ch&&bimBtrWalk(L[i].ch,fn,L[i],depth+1))return true;
    }
    return false;
  }
  /* {n, par, list, i, path: the ancestors, outermost first} or null */
  function bimBtrFind(L,id){
    var out=null,stack=[];
    (function go(list,par){
      var i;
      for(i=0;i<list.length&&!out;i++){
        if(list[i].id===id){out={n:list[i],par:par,list:list,i:i,path:stack.slice()};return;}
        if(list[i].ch){stack.push(list[i]);go(list[i].ch,list[i]);stack.pop();}
      }
    })(L,null);
    return out;
  }
  function bimBtrNewId(L){
    var m=0;
    bimBtrWalk(L,function(n){var r=/^e(\d+)$/.exec(n.id);if(r&&+r[1]>m)m=+r[1];});
    return 'e'+(m+1);
  }
  function bimBtrCount(L){var c=0;bimBtrWalk(L,function(){c++;});return c;}
  /* locked or hidden, by itself or by an ancestor (lock and hide cascade, 4.1) */
  function bimBtrEff(L,id){
    var f=bimBtrFind(L,id),r={lock:false,hide:false},i;
    if(!f)return r;
    for(i=0;i<f.path.length;i++){if(f.path[i].lock)r.lock=true;if(f.path[i].hide)r.hide=true;}
    if(f.n.lock)r.lock=true;if(f.n.hide)r.hide=true;
    return r;
  }
  /* ---- the figures ---- */
  /* a figure's box in mm, from its columns (V172b: x*P, w*P-G px) */
  function bimBtrFigBox(F,P,G){
    var k=bimBtrPxMm();
    return {x:F.x*P/k,y:F.y*P/k,w:(F.w*P-G)/k,h:(F.h*P-G)/k};
  }
  /* a box in mm back to a figure's columns */
  function bimBtrFigCols(b,P,G){
    var k=bimBtrPxMm();
    return {x:b.x*k/P,y:b.y*k/P,w:(b.w*k+G)/P,h:(b.h*k+G)/P};
  }
  /* the tree agrees with the figures: an element whose figure is gone is dropped, a figure with no element is put on
     top, in the order given (reading order); a figure named twice keeps its first element */
  function bimBtrSync(L,figs){
    var have={},seen={},drop=[];
    (figs||[]).forEach(function(F){if(F&&F.k)have[F.k]=1;});
    bimBtrWalk(L,function(n,par,list,i){
      if(n.t!=='fig')return;
      if(!have[n.k]||seen[n.k])drop.push(n.id);else seen[n.k]=1;
    });
    drop.forEach(function(id){bimBtrRemove(L,id);});
    (figs||[]).forEach(function(F){if(F&&F.k&&!seen[F.k]){seen[F.k]=1;L.push({id:bimBtrNewId(L),t:'fig',k:F.k,op:1,bm:'normal'});}});
    return L;
  }
  /* ---- the box of an element, in mm; figBox(k) gives a figure's ---- */
  function bimBtrBox(n,figBox){
    var b=null;
    if(n.t==='fig')return figBox?figBox(n.k):null;
    if(n.t==='group'){
      (n.ch||[]).forEach(function(c){var q=bimBtrBox(c,figBox);if(q)b=b?bimBtrUnion(b,q):q;});
      return b;
    }
    if(n.t==='line')return {x:Math.min(n.x,n.x+n.w),y:Math.min(n.y,n.y+n.h),w:Math.abs(n.w),h:Math.abs(n.h)};
    return {x:n.x,y:n.y,w:n.w,h:n.h};
  }
  function bimBtrUnion(a,b){
    var x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);
    return {x:x,y:y,w:Math.max(a.x+a.w,b.x+b.w)-x,h:Math.max(a.y+a.h,b.y+b.h)-y};
  }
  /* every element moved by dx, dy mm; a figure through moveFig(k, dx, dy) */
  function bimBtrShift(n,dx,dy,moveFig){
    if(n.t==='fig'){if(moveFig)moveFig(n.k,dx,dy);return;}
    if(typeof n.x==='number'){n.x=Math.round((n.x+dx)*1000)/1000;n.y=Math.round((n.y+dy)*1000)/1000;}
    (n.ch||[]).forEach(function(c){bimBtrShift(c,dx,dy,moveFig);});
  }
  /* ---- changing the tree: each works in place and returns true when it changed something ---- */
  function bimBtrRemove(L,id){
    var f=bimBtrFind(L,id);
    if(!f)return false;
    f.list.splice(f.i,1);
    if(f.par&&f.par.t==='group'&&!f.par.ch.length)bimBtrRemove(L,f.par.id);   /* a group left empty is gone */
    return true;
  }
  /* within its parent: 'forward', 'backward', 'front', 'back' (4.1) */
  function bimBtrReorder(L,id,how){
    var f=bimBtrFind(L,id),j;
    if(!f)return false;
    j=how==='forward'?f.i+1:how==='backward'?f.i-1:how==='front'?f.list.length-1:how==='back'?0:f.i;
    j=Math.max(0,Math.min(f.list.length-1,j));
    if(j===f.i)return false;
    f.list.splice(j,0,f.list.splice(f.i,1)[0]);
    return true;
  }
  /* the ids that share one parent, in their drawing order; null when they do not */
  function bimBtrSiblings(L,ids){
    var F=[],par,i,f;
    for(i=0;i<ids.length;i++){
      f=bimBtrFind(L,ids[i]);
      if(!f)return null;
      if(i===0)par=f.par;else if(f.par!==par)return null;
      F.push(f);
    }
    F.sort(function(a,b){return a.i-b.i;});
    return F;
  }
  /* the elements into a new group (or frame, around their bounds), where the topmost of them was; its id or null */
  function bimBtrGroup(L,ids,asFrame,figBox){
    var F=bimBtrSiblings(L,ids),list,top,g,b=null,i;
    if(!F||!F.length)return null;
    if(F[0].par&&F[0].par.t!=='frame'&&F[0].par.t!=='group')return null;
    list=F[0].list;top=F[F.length-1].i;
    g={id:bimBtrNewId(L),t:asFrame?'frame':'group',op:1,bm:'pass',ch:[]};
    for(i=0;i<F.length;i++){g.ch.push(F[i].n);var q=bimBtrBox(F[i].n,figBox);if(q)b=b?bimBtrUnion(b,q):q;}
    if(asFrame){
      if(!b)return null;
      g.x=Math.round(b.x*1000)/1000;g.y=Math.round(b.y*1000)/1000;g.w=Math.max(0.5,Math.round(b.w*1000)/1000);g.h=Math.max(0.5,Math.round(b.h*1000)/1000);
      g.fill='none';g.stroke='none';g.sw=0.35;g.r=0;g.clip=false;
    }
    list.splice(top+1,0,g);
    for(i=F.length-1;i>=0;i--)list.splice(F[i].i,1);
    return g.id;
  }
  /* a group or frame's children into its place; its opacity goes into theirs, its blend mode is let go (said by the caller) */
  function bimBtrUngroup(L,id){
    var f=bimBtrFind(L,id),ch;
    if(!f||!bimBtrIsBox(f.n))return false;
    ch=f.n.ch||[];
    if(f.n.op<1)ch.forEach(function(c){c.op=Math.round(c.op*f.n.op*1000)/1000;});
    Array.prototype.splice.apply(f.list,[f.i,1].concat(ch));
    if(f.par&&f.par.t==='group'&&!f.par.ch.length)bimBtrRemove(L,f.par.id);
    return true;
  }
  /* into a frame or group (pid) at index j (its end when j is not a number), or to the board with pid null; never into itself */
  function bimBtrMoveTo(L,id,pid,j){
    var f=bimBtrFind(L,id),p=pid?bimBtrFind(L,pid):null,dest,oldPar;
    if(!f||(pid&&(!p||!bimBtrIsBox(p.n))))return false;
    if(pid&&(pid===id||p.path.some(function(a){return a.id===id;})))return false;
    dest=p?p.n.ch:L;oldPar=f.par;
    f.list.splice(f.i,1);
    if(typeof j!=='number'||j>dest.length)j=dest.length;
    dest.splice(Math.max(0,j),0,f.n);
    if(oldPar&&oldPar.t==='group'&&!oldPar.ch.length)bimBtrRemove(L,oldPar.id);
    return true;
  }
  /* out of its group or frame: just above it in its parent's list */
  function bimBtrOut(L,id){
    var f=bimBtrFind(L,id),g;
    if(!f||!f.par)return false;
    g=bimBtrFind(L,f.par.id);
    return bimBtrMoveTo(L,id,g.par?g.par.id:null,g.i+1);
  }
  /* a deep copy with new ids, figures left out (a figure is on a board once); null when nothing is left */
  function bimBtrCopy(L,n){
    var next=+bimBtrNewId(L).slice(1);
    function cp(a){
      if(a.t==='fig')return null;
      var r=JSON.parse(JSON.stringify(a)),ch;
      r.id='e'+(next++);
      if(a.ch){ch=[];a.ch.forEach(function(c){var q=cp(c);if(q)ch.push(q);});r.ch=ch;if(a.t==='group'&&!ch.length)return null;}
      return r;
    }
    return cp(n);
  }
  /* ---- masks (4.3): in one list, a mask masks the siblings above it up to the next mask or the list's end; a hidden
     mask masks nothing. [{mask: node or null, items: [nodes]}], bottom first ---- */
  function bimBtrRuns(list){
    var runs=[],cur={mask:null,items:[]};
    list.forEach(function(n){
      if(n.mask){
        if(cur.mask||cur.items.length)runs.push(cur);
        cur={mask:n.hide?null:n,items:[]};
      }else cur.items.push(n);
    });
    if(cur.mask||cur.items.length)runs.push(cur);
    return runs;
  }
  /* what a click picks (4.1): the outermost unlocked, visible ancestor within the scope (a group entered, or the
     board), or the element itself when deep; null for a locked or hidden one */
  function bimBtrPick(L,id,scope,deep){
    var f=bimBtrFind(L,id),i,chain,e;
    if(!f)return null;
    e=bimBtrEff(L,id);
    if(e.hide||e.lock)return null;
    if(deep)return id;
    chain=f.path.map(function(a){return a.id;}).concat([id]);
    i=scope?chain.indexOf(scope):-1;
    if(scope&&i<0)i=-1;
    return chain[i+1]||id;
  }
export {
  bimBtrBlend, bimBtrBlends, bimBtrBox, bimBtrCopy, bimBtrCount, bimBtrEff, bimBtrFigBox, bimBtrFigCols,
  bimBtrFind, bimBtrGroup, bimBtrIsBox, bimBtrKind, bimBtrMaskTypes, bimBtrMax, bimBtrMoveTo, bimBtrNewId,
  bimBtrOut, bimBtrPick, bimBtrPxMm, bimBtrRemove, bimBtrReorder, bimBtrRuns, bimBtrShift, bimBtrSync,
  bimBtrUngroup, bimBtrUnion, bimBtrValid, bimBtrWalk
};
