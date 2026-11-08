
  /* ================= __acad3dV174b: arranging a board's objects =================
     docs/research/research-presentation-boards.md, 4.4 and 5.4 (D7 to D11), and 11a (R4: a sub-layer is a group).
     Ported from the research's own experiments, which were measured against Chromium's flexbox (39 of 39) and timed:
     docs/research/experiments/v174-layout/align.js, spacing-snap.js and autolayout.js. Boxes are {x, y, w, h} in mm.
     - Align: to the selection's bounds, or, for one object, to the page (Figma's rule).
     - Distribute (three or more): the box with the least left edge and the one with the greatest right edge stay,
       the rest are spaced in equal gaps between them (D9).
     - Tidy up: sorted, the most common gap between all.
     - Smart spacing: while a drag lasts, the moving box catches another's edge or centre, or an equal gap beside a
       pair of neighbours, within the drawing's 12 screen px (D10).
     - Auto layout (D7, D8): a layer's objects on one board laid out in a row, a column or wrapped rows, with a gap
       (or Auto), padding, main and cross alignment; each object Fixed or Fill (css-flexbox-1's freeze loop), or out
       of the flow. The positions are computed here and written to the objects, so print and export never depend on
       the browser's flexbox. */
  function bimBalUnion(L){
    var x0=Infinity,y0=Infinity,x1=-Infinity,y1=-Infinity,i,b;
    for(i=0;i<L.length;i++){b=L[i];x0=Math.min(x0,b.x);y0=Math.min(y0,b.y);x1=Math.max(x1,b.x+b.w);y1=Math.max(y1,b.y+b.h);}
    return {x:x0,y:y0,w:x1-x0,h:y1-y0};
  }
  function bimBalEdge(e){
    return {left:['x','w',0],hcenter:['x','w',0.5],right:['x','w',1],top:['y','h',0],vcenter:['y','h',0.5],bottom:['y','h',1]}[e]||null;
  }
  /* new {x, y} for each box: aligned to the selection's bounds, or one box to the page */
  function bimBalAlign(boxes,edge,page){
    var E=bimBalEdge(edge),T,target;
    if(!E||!boxes.length)return boxes.map(function(b){return {x:b.x,y:b.y};});
    T=boxes.length===1&&page?page:bimBalUnion(boxes);
    target=T[E[0]]+T[E[1]]*E[2];
    return boxes.map(function(b){var r={x:b.x,y:b.y};r[E[0]]+=target-(b[E[0]]+b[E[1]]*E[2]);return r;});
  }
  function bimBalOrder(bb,key){var ix=bb.map(function(b,i){return i;});ix.sort(function(a,b){return key(bb[a])-key(bb[b])||a-b;});return ix;}
  /* equal gaps on an axis ('x' or 'y'); fewer than three boxes stay. {pos, step} */
  function bimBalDistribute(boxes,axis){
    var P=axis==='x'?'x':'y',S=axis==='x'?'w':'h',out=boxes.map(function(b){return {x:b.x,y:b.y};}),lo=0,hi=0,ix,i,span=0,first,last,step,pos;
    if(boxes.length<3)return {pos:out,step:null};
    for(i=1;i<boxes.length;i++){if(boxes[i][P]<boxes[lo][P])lo=i;if(boxes[i][P]+boxes[i][S]>boxes[hi][P]+boxes[hi][S])hi=i;}
    ix=bimBalOrder(boxes,function(b){return b[P];}).filter(function(k){return k!==lo&&k!==hi;});
    ix.unshift(lo);if(hi!==lo)ix.push(hi);
    first=boxes[ix[0]];last=boxes[ix[ix.length-1]];
    for(i=0;i<ix.length;i++)span+=boxes[ix[i]][S];
    step=(last[P]+last[S]-first[P]-span)/(ix.length-1);
    pos=first[P];
    for(i=0;i<ix.length;i++){out[ix[i]][P]+=pos-boxes[ix[i]][P];pos+=boxes[ix[i]][S]+step;}
    return {pos:out,step:step};
  }
  /* tidy up on an axis: sorted by the near edge, the most common gap (to 1 mm) between all, the first stays */
  function bimBalTidy(boxes,axis){
    var P=axis==='x'?'x':'y',S=axis==='x'?'w':'h',ix=bimBalOrder(boxes,function(b){return b[P];}),count={},best=null,i,g,out,pos;
    for(i=1;i<ix.length;i++){
      g=Math.round(boxes[ix[i]][P]-(boxes[ix[i-1]][P]+boxes[ix[i-1]][S]));
      count[g]=(count[g]||0)+1;
      if(best===null||count[g]>count[best]||(count[g]===count[best]&&g<best))best=g;
    }
    out=boxes.map(function(b){return {x:b.x,y:b.y};});pos=ix.length?boxes[ix[0]][P]:0;
    for(i=0;i<ix.length;i++){out[ix[i]][P]+=pos-boxes[ix[i]][P];pos+=boxes[ix[i]][S]+(best||0);}
    return {pos:out,gap:best};
  }
  /* ---- smart spacing (after Excalidraw's snapping.ts, MIT, read for the method) ---- */
  function bimBalOverlap(a0,a1,b0,b1){return a0<=b1&&b0<=a1;}
  /* once a drag starts: the gaps between the other boxes, and their edges and centres */
  function bimBalGaps(R){
    var H=[],V=[],xs=[],ys=[],S=R.slice(),i,j,a,b;
    S.sort(function(p,q){return p.x-q.x;});
    for(i=0;i<S.length;i++)for(j=i+1;j<S.length;j++){a=S[i];b=S[j];
      if(a.x+a.w<b.x&&bimBalOverlap(a.y,a.y+a.h,b.y,b.y+b.h))H.push({s:a,e:b,len:b.x-(a.x+a.w),o0:Math.max(a.y,b.y),o1:Math.min(a.y+a.h,b.y+b.h)});}
    S.sort(function(p,q){return p.y-q.y;});
    for(i=0;i<S.length;i++)for(j=i+1;j<S.length;j++){a=S[i];b=S[j];
      if(a.y+a.h<b.y&&bimBalOverlap(a.x,a.x+a.w,b.x,b.x+b.w))V.push({s:a,e:b,len:b.y-(a.y+a.h),o0:Math.max(a.x,b.x),o1:Math.min(a.x+a.w,b.x+b.w)});}
    R.forEach(function(o){xs.push(o.x,o.x+o.w/2,o.x+o.w);ys.push(o.y,o.y+o.h/2,o.y+o.h);});
    return {H:H,V:V,xs:xs,ys:ys};
  }
  /* one axis: the nearest catch, {d, kind, at, g}, for a box at [p, p+s] whose cross range is [c0, c1]; or null */
  function bimBalAxis(p,s,c0,c1,gaps,pts,th,axis){
    var best=null,bd=th+1e-9,i,g,d,k,m,mine=[p,p+s/2,p+s],sP,sS,eP,eS;
    for(i=0;i<pts.length;i++)for(k=0;k<3;k++){d=pts[i]-mine[k];if(Math.abs(d)<bd){bd=Math.abs(d);best={d:d,kind:'point',at:pts[i]};}}
    for(i=0;i<gaps.length;i++){
      g=gaps[i];
      if(!bimBalOverlap(c0,c1,g.o0,g.o1))continue;
      sP=axis==='x'?g.s.x:g.s.y;sS=axis==='x'?g.s.w:g.s.h;eP=axis==='x'?g.e.x:g.e.y;eS=axis==='x'?g.e.w:g.e.h;
      if(g.len>s){m=sP+sS+g.len/2;d=m-(p+s/2);if(Math.abs(d)<bd){bd=Math.abs(d);best={d:d,kind:'centre',g:g};}}
      d=(eP+eS+g.len)-p;if(Math.abs(d)<bd){bd=Math.abs(d);best={d:d,kind:'after',g:g};}
      d=(sP-g.len)-(p+s);if(Math.abs(d)<bd){bd=Math.abs(d);best={d:d,kind:'before',g:g};}
    }
    return best;
  }
  function bimBalSnap(B,G,th){
    return {x:bimBalAxis(B.x,B.w,B.y,B.y+B.h,G.H,G.xs,th,'x'),y:bimBalAxis(B.y,B.h,B.x,B.x+B.w,G.V,G.ys,th,'y')};
  }
  /* ---- auto layout (Figma's documented rules; css-flexbox-1's freeze loop for Fill) ---- */
  function bimBalNum(v,d){return typeof v==='number'&&isFinite(v)?v:d;}
  function bimBalClamp(v,lo,hi){if(typeof hi==='number'&&v>hi)v=hi;if(typeof lo==='number'&&v<lo)v=lo;return v;}
  /* css-flexbox-1 9.7, the grow case: Fixed items do not flex; Fill has a basis of 0 and grows by 1 */
  function bimBalFill(items,free0){
    var i,it,all,rem,sumF,total,cl,EPS=1e-9;
    for(i=0;i<items.length;i++){it=items[i];it.target=it.basis;it.frozen=!it.fill;}
    for(;;){
      all=true;for(i=0;i<items.length;i++)if(!items[i].frozen)all=false;
      if(all)break;
      rem=free0;sumF=0;
      for(i=0;i<items.length;i++){it=items[i];rem-=it.frozen?it.target:it.basis;if(!it.frozen)sumF+=1;}
      for(i=0;i<items.length;i++){it=items[i];if(!it.frozen)it.target=rem>0?it.basis+rem/sumF:it.basis;}
      total=0;
      for(i=0;i<items.length;i++){it=items[i];if(it.frozen)continue;cl=Math.max(0,bimBalClamp(it.target,it.min,it.max));it.viol=cl-it.target;total+=it.viol;it.target=cl;}
      for(i=0;i<items.length;i++){it=items[i];if(it.frozen)continue;
        if(Math.abs(total)<EPS)it.frozen=true;else if(total>0&&it.viol>EPS)it.frozen=true;else if(total<0&&it.viol<-EPS)it.frozen=true;}
    }
  }
  /* F: {dir 'row'|'column', wrap, gap (number or 'auto'), pad, alignMain, alignCross, sizeW, sizeH ('fixed'|'hug'), w, h,
     children:[{w, h, sizeW, sizeH ('fixed'|'fill'), hidden, absolute, x, y}]}. {w, h, kids:[{x, y, w, h} or null]},
     the kids' places from the frame's corner */
  function bimBalLayout(F){
    var row=F.dir!=='column',M=row?'w':'h',C=row?'h':'w',sMk=row?'sizeW':'sizeH',sCk=row?'sizeH':'sizeW',EPS=1e-9;
    var p=bimBalNum(F.pad,0),padM=2*p,padC=2*p,kids=F.children||[],out={w:0,h:0,kids:[]},flow=[],i,c,anyM=false,anyC=false;
    for(i=0;i<kids.length;i++){
      c=kids[i];out.kids.push(null);
      if(c.hidden)continue;
      if(c.absolute){out.kids[i]={x:bimBalNum(c.x,0),y:bimBalNum(c.y,0),w:bimBalNum(c.w,0),h:bimBalNum(c.h,0)};continue;}
      flow.push(i);
      if(c[sMk]==='fill')anyM=true;
      if(c[sCk]==='fill')anyC=true;
    }
    var sM=F[sMk]==='hug'?'hug':'fixed',sC=F[sCk]==='hug'?'hug':'fixed';
    if(sM==='hug'&&anyM)sM='fixed';   /* a Hug frame with a Fill child is Fixed on that axis */
    if(sC==='hug'&&anyC)sC='fixed';
    var outerM=sM==='fixed'?Math.max(padM,bimBalNum(F[M],0)):null,outerC=sC==='fixed'?Math.max(padC,bimBalNum(F[C],0)):null;
    var auto=F.gap==='auto',gap=auto?0:bimBalNum(F.gap,0),crossGap=Math.max(0,auto?0:gap),wrap=!!F.wrap&&sM==='fixed';
    var innerM=outerM===null?Infinity:outerM-padM,items=[],it;
    for(i=0;i<flow.length;i++){
      c=kids[flow[i]];
      it={idx:flow[i],c:c,fill:c[sMk]==='fill'};
      it.basis=it.fill?0:bimBalNum(c[M],0);it.hyp=it.basis;
      it.fillC=c[sCk]==='fill';it.cross=it.fillC?0:bimBalNum(c[C],0);
      items.push(it);
    }
    var lines=[],cur=[],used=0,add,li,L,j,maxLineM=0,gaps,sumM,lc;
    for(i=0;i<items.length;i++){
      add=items[i].hyp+(cur.length?gap:0);
      if(wrap&&cur.length&&used+add>innerM+EPS){lines.push(cur);cur=[];used=0;add=items[i].hyp;}
      cur.push(items[i]);used+=add;
    }
    if(cur.length||!lines.length)lines.push(cur);
    for(li=0;li<lines.length;li++){
      L=lines[li];gaps=L.length>1?gap*(L.length-1):0;
      if(innerM!==Infinity)bimBalFill(L,innerM-gaps);else for(j=0;j<L.length;j++)L[j].target=L[j].basis;
      sumM=gaps;for(j=0;j<L.length;j++)sumM+=L[j].target;
      L.sumM=sumM;if(sumM>maxLineM)maxLineM=sumM;
      lc=0;for(j=0;j<L.length;j++)if(L[j].cross>lc)lc=L[j].cross;
      L.cross=lc;
    }
    if(outerM===null){outerM=Math.max(padM,maxLineM+padM);innerM=outerM-padM;}
    var sumC=0;for(li=0;li<lines.length;li++)sumC+=lines[li].cross;
    sumC+=lines.length>1?crossGap*(lines.length-1):0;
    if(outerC===null)outerC=Math.max(padC,sumC+padC);
    var innerC=outerC-padC,posC=p,free,lead,between,n,g,posM,sizeC,offC,r;
    if(lines.length===1)lines[0].cross=innerC;
    else if(F.alignCross==='center')posC+=(innerC-sumC)/2;
    else if(F.alignCross==='end')posC+=innerC-sumC;
    for(li=0;li<lines.length;li++){
      L=lines[li];free=innerM-L.sumM;lead=0;between=gap;n=L.length;
      if(auto){between=n>1?Math.max(0,free/(n-1)):0;}
      else if(F.alignMain==='center')lead=free/2;
      else if(F.alignMain==='end')lead=free;
      posM=p+lead;
      for(j=0;j<n;j++){
        it=L[j];sizeC=it.fillC?L.cross:it.cross;offC=0;
        if(!it.fillC){if(F.alignCross==='center')offC=(L.cross-sizeC)/2;else if(F.alignCross==='end')offC=L.cross-sizeC;}
        r={};r[row?'x':'y']=posM;r[row?'y':'x']=posC+offC;r[M]=it.target;r[C]=sizeC;
        out.kids[it.idx]={x:r.x,y:r.y,w:r.w,h:r.h};
        posM+=it.target+between;
      }
      posC+=L.cross+crossGap;
    }
    out.w=row?outerM:outerC;out.h=row?outerC:outerM;
    return out;
  }
export { bimBalAlign, bimBalDistribute, bimBalGaps, bimBalLayout, bimBalSnap, bimBalTidy, bimBalUnion };
