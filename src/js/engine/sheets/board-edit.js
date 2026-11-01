  /* ================= __acad3dV172b: Edit, on a board =================
     The board's own Edit. A figure moves by its handle or its body and sizes by its corner, and the
     drawing's own settings govern it as they govern a point being drawn (bimSnapPoint): Snap catches an
     edge on another figure's edge or the board's, within the same 12 px (pxThreshold); failing that, Grid
     puts the edges on the board's 12 columns and on rows of the same step; Ortho keeps a drag straight
     across or straight down. No setting of its own. The arrow keys move the figure in focus, Shift and the
     arrows size it. A board without a list is arranged as it is laid out on a wide screen, and is given its
     list by the first change; each change is one undo step, kept with the project. On a phone the figures
     are in reading order, and each one's menu moves it earlier or later. */
  var A3D_BRD={drag:null,mat:null,dlg:null,dlgFrom:null};
  /* the list Edit works on: the board's own, or the board as it is laid out (measured once a revision) */
  function bimBrdWorking(B){
    if(B.figs)return JSON.parse(JSON.stringify(B.figs));
    var key=B.kind+'|'+A3D_REV;
    if(!A3D_BRD.mat||A3D_BRD.mat.key!==key)A3D_BRD.mat={key:key,L:bimBrdMeasureDefault(B.kind)};
    return JSON.parse(JSON.stringify(A3D_BRD.mat.L));
  }
  function bimBrdFind(L,k){var i;for(i=0;i<L.length;i++)if(L[i].k===k)return L[i];return null;}
  function bimBrdNewK(L){var n=0;L.forEach(function(F){var m=/^f(\d+)$/.exec(F.k);if(m&&+m[1]>n)n=+m[1];});return 'f'+(n+1);}
  function bimBrdOrder(L){var o=[];bimBrdBands(L).forEach(function(D){D.f.forEach(function(F){o.push(F.k);});});return o;}
  function bimBrdBottom(L){var b=0;L.forEach(function(F){if(F.y+F.h>b)b=F.y+F.h;});return b;}
  /* a new list for the board: one undo step. off: the board's own figures taken off it (the three boards) */
  function bimBrdCommit(B,L,msg,focusK,off){
    var F=bimBrdFigsValid(L);
    if(!F){console.warn('[BIM] A board\'s new list was not a list; nothing changed');return false;}
    pushUndo();
    B.figs=F;
    if(B.kind!=='custom'){
      if(off)B.off=off;
      if(B.off&&!B.off.length)delete B.off;
    }
    saveSoon();
    bimBrdRedraw(focusK);
    if(msg)a3dToast(msg);
    return true;
  }
  function bimBrdRedraw(focusK){
    if(!A3D_CLB.open)return;
    bimClbOpen();
    if(focusK){
      var b=bimClbEl(),f=b&&b.querySelector('.a3d-clb-arr [data-brdk="'+focusK+'"]');
      if(f){try{f.focus({preventScroll:true});}catch(eF){}bimBrdReveal(f);}
    }
  }
  /* a figure brought into view in the board, if it is not */
  function bimBrdReveal(f){
    var b=bimClbEl();if(!b||!f)return;
    var r=f.getBoundingClientRect(),br=b.getBoundingClientRect();
    if(r.top<br.top+60||r.top>br.bottom-80)b.scrollTop+=r.top-br.top-90;
  }
  function bimBrdLabelOf(k){
    var b=bimClbEl(),f=b&&b.querySelector('.a3d-clb-arr [data-brdk="'+k+'"]'),n=f&&f.querySelector('.a3d-clb-fno');
    return n&&/^Fig\./.test(n.textContent)?n.textContent:'The figure';
  }
  /* ---- Edit on and off ---- */
  function bimBrdEdit(on){
    if(on&&!bimBrdRec()){a3dToast('Only a board in the set can be arranged: Show in Presentation puts it there');return false;}
    A3D_CLB.edit=!!on;
    bimBrdDlgClose();
    if(A3D_CLB.open)bimClbOpen();
    if(on)a3dToast('Edit: drag a figure, size it by its corner; Add a figure for any analysis');
    return true;
  }
  /* Escape: a dialog first, then Edit; false when neither was open */
  function bimBrdEsc(){
    if(A3D_BRD.dlg){bimBrdDlgClose();return true;}
    if(A3D_CLB.edit){bimBrdEdit(false);return true;}
    return false;
  }
  /* after an undo or a redo: the open board drawn again from the record it now has */
  function bimBrdRestored(){
    A3D_BRD.mat=null;
    if(!A3D_CLB.open)return;
    if(A3D_CLB.kind==='custom'&&!bimBoardById(A3D_CLB.cid)){bimClbClose();return;}
    bimClbOpen();
  }
  /* the drawing's snaps changed (F3, F9, F8, the status bar or Edit's own buttons) */
  function bimBrdSnapSync(){
    var b=bimClbEl(),i,B,s;
    if(!b)return;
    B=b.querySelectorAll('[data-brdsnap]');
    for(i=0;i<B.length;i++){s=B[i].getAttribute('data-brdsnap');B[i].setAttribute('aria-pressed',String(!!A3D_SNAP[s]));}
    s=b.querySelector('.a3d-clb-arrgrid');if(s)s.classList.toggle('on',!!A3D_SNAP.grid);
  }
  /* ---- the snaps, in the board's steps ---- */
  function bimBrdSnap(mode,F0,dx,dy,others,z){
    var th=A3D_SNAP.pxThreshold/(BIM_BRD_P0*(z||1)),R={x:F0.x,y:F0.y,w:F0.w,h:F0.h,guides:[]},xs=[0,12],ys=[0],i,o,best,lx=dx!==0||!A3D_SNAP.ortho,ly=dy!==0||!A3D_SNAP.ortho;
    if(A3D_SNAP.ortho){if(Math.abs(dx)>=Math.abs(dy))dy=0;else dx=0;lx=dx!==0;ly=dy!==0;}
    for(i=0;i<others.length;i++){o=others[i];xs.push(o.x,o.x+o.w);ys.push(o.y,o.y+o.h);}
    /* the nearest pair of a moving edge and an edge to catch: [shift, the edge caught, which moving edge] */
    function near(mv,to){
      var b=null,j,m,d;
      for(j=0;j<mv.length;j++)for(m=0;m<to.length;m++){d=to[m]-mv[j];if(Math.abs(d)<=th+1e-9&&(!b||Math.abs(d)<Math.abs(b[0])))b=[d,to[m],j];}
      return b;
    }
    if(mode==='move'){
      var nx=F0.x+dx,ny=F0.y+dy,sx=false,sy=false;
      if(A3D_SNAP.point){
        if(lx){best=near([nx,nx+F0.w],xs);if(best){nx+=best[0];sx=true;R.guides.push(['x',best[1],best[2]===1]);}}
        if(ly){best=near([ny,ny+F0.h],ys);if(best){ny+=best[0];sy=true;R.guides.push(['y',best[1],best[2]===1]);}}
      }
      if(A3D_SNAP.grid){if(!sx&&lx)nx=Math.round(nx);if(!sy&&ly)ny=Math.round(ny);}
      R.x=Math.max(0,Math.min(12-F0.w,nx));R.y=Math.max(0,ny);
    }else{
      var r=F0.x+F0.w+dx,bt=F0.y+F0.h+dy,ex=false,ey=false;
      if(A3D_SNAP.point){
        if(lx){best=near([r],xs);if(best){r+=best[0];ex=true;R.guides.push(['x',best[1],true]);}}
        if(ly){best=near([bt],ys);if(best){bt+=best[0];ey=true;R.guides.push(['y',best[1],true]);}}
      }
      if(A3D_SNAP.grid){if(!ex&&lx)r=Math.round(r);if(!ey&&ly)bt=Math.round(bt);}
      R.w=Math.max(1,Math.min(12-F0.x,r-F0.x));R.h=Math.max(0.25,bt-F0.y);
    }
    R.x=Math.round(R.x*10000)/10000;R.y=Math.round(R.y*10000)/10000;R.w=Math.round(R.w*10000)/10000;R.h=Math.round(R.h*10000)/10000;
    return R;
  }
  /* the edges caught, drawn while the drag lasts */
  function bimBrdGuides(arr,G){
    var old=arr.querySelectorAll('.a3d-clb-guide'),i,d,P=BIM_BRD_P0;
    for(i=0;i<old.length;i++)old[i].parentNode.removeChild(old[i]);
    (G||[]).forEach(function(g){
      d=document.createElement('div');
      d.className='a3d-clb-guide '+g[0];
      d.setAttribute('aria-hidden','true');
      if(g[0]==='x')d.style.left=bimBrdPx(g[1]*P-(g[2]?BIM_BRD_G:0))+'px';else d.style.top=bimBrdPx(g[1]*P-(g[2]?BIM_BRD_G:0))+'px';
      arr.appendChild(d);
    });
  }
  /* ---- dragging ---- */
  function bimBrdDown(ev){
    if(!bimBrdEditing()||A3D_CLB.narrow||(ev.button!==undefined&&ev.button>0))return;
    var t=ev.target,fig=t&&t.closest?t.closest('.a3d-clb-arr .a3d-clb-fig'):null;
    if(!fig||t.closest('[data-brdmenu]'))return;
    var rsz=!!t.closest('[data-brdrsz]'),grip=!!t.closest('[data-brdgrip]');
    if(!rsz&&!grip&&(ev.pointerType==='touch'||t.closest('a,input,select,textarea,button')))return;   /* a finger scrolls the board; it moves a figure by its handle */
    var B=bimBrdRec();if(!B)return;
    var L=bimBrdWorking(B),k=fig.getAttribute('data-brdk'),F=bimBrdFind(L,k),b=bimClbEl(),arr=fig.closest('.a3d-clb-arr');
    if(!F)return;
    A3D_BRD.drag={k:k,mode:rsz?'size':'move',x0:ev.clientX,y0:ev.clientY,s0:b?b.scrollTop:0,F0:{x:F.x,y:F.y,w:F.w,h:F.h},L:L,
      z:parseFloat(arr.style.getPropertyValue('--z'))||1,el:fig,arr:arr,pid:ev.pointerId,moved:false,cur:null};
    try{fig.setPointerCapture(ev.pointerId);}catch(eP){}
    fig.classList.add('drag');
    ev.preventDefault();
  }
  function bimBrdMoveEv(ev){
    var D=A3D_BRD.drag;if(!D||ev.pointerId!==D.pid)return;
    var b=bimClbEl(),br,dx,dy,R,P=BIM_BRD_P0;
    if(!D.moved&&Math.abs(ev.clientX-D.x0)<3&&Math.abs(ev.clientY-D.y0)<3)return;
    if(b){br=b.getBoundingClientRect();if(ev.clientY>br.bottom-36)b.scrollTop+=14;else if(ev.clientY<br.top+64)b.scrollTop-=14;bimClbTipHide(b);}
    dx=(ev.clientX-D.x0)/D.z/P;dy=(ev.clientY-D.y0+((b?b.scrollTop:0)-D.s0))/D.z/P;   /* the board scrolled under the pointer counts */
    D.moved=true;
    R=bimBrdSnap(D.mode,D.F0,dx,dy,D.L.filter(function(f){return f.k!==D.k;}),D.z);
    D.cur=R;
    if(D.mode==='move')D.el.style.transform='translate('+bimBrdPx((R.x-D.F0.x)*P)+'px,'+bimBrdPx((R.y-D.F0.y)*P)+'px)';
    else{D.el.style.width=bimBrdPx(R.w*P-BIM_BRD_G)+'px';D.el.style.height=bimBrdPx(R.h*P-BIM_BRD_G)+'px';}
    bimBrdGuides(D.arr,R.guides);
    ev.preventDefault();
  }
  function bimBrdUp(ev){
    var D=A3D_BRD.drag;if(!D||ev.pointerId!==D.pid)return;
    A3D_BRD.drag=null;
    try{D.el.releasePointerCapture(D.pid);}catch(eR){}
    D.el.classList.remove('drag');bimBrdGuides(D.arr,[]);
    if(!D.moved||!D.cur){D.el.style.transform='';return;}
    var R=D.cur,F=bimBrdFind(D.L,D.k),B=bimBrdRec();
    if(!F||!B)return;
    if(Math.abs(R.x-F.x)<1e-6&&Math.abs(R.y-F.y)<1e-6&&Math.abs(R.w-F.w)<1e-6&&Math.abs(R.h-F.h)<1e-6){bimClbOpen();return;}
    F.x=R.x;F.y=R.y;F.w=R.w;F.h=R.h;
    bimBrdCommit(B,D.L,null,D.k);
  }
  function bimBrdCancel(ev){
    var D=A3D_BRD.drag;if(!D||(ev&&ev.pointerId!==D.pid))return;
    A3D_BRD.drag=null;
    D.el.classList.remove('drag');D.el.style.transform='';bimBrdGuides(D.arr,[]);
    bimClbOpen();
  }
  /* ---- the keys, on the figure in focus ---- */
  function bimBrdNudge(k,dx,dy,size){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k),g=A3D_SNAP.grid;
    if(!F)return false;
    if(size){
      var r=F.x+F.w+dx,bt=F.y+F.h+dy;
      if(g){if(dx)r=Math.round(r);if(dy)bt=Math.round(bt);}
      F.w=Math.max(1,Math.min(12-F.x,r-F.x));F.h=Math.max(0.25,bt-F.y);
    }else{
      var nx=F.x+dx,ny=F.y+dy;
      if(g){if(dx)nx=Math.round(nx);if(dy)ny=Math.round(ny);}
      F.x=Math.max(0,Math.min(12-F.w,nx));F.y=Math.max(0,ny);
    }
    return bimBrdCommit(B,L,null,k);
  }
  function bimBrdKey(ev){
    if(!bimBrdEditing())return;
    var t=ev.target,k,dx=0,dy=0,st,r;
    if(t&&t.getAttribute&&t.getAttribute('data-brdname')){if(ev.key==='Enter'){ev.preventDefault();t.blur();}return;}
    if(!t||!t.classList||!t.classList.contains('a3d-clb-fig')||!t.closest('.a3d-clb-arr'))return;
    k=t.getAttribute('data-brdk');
    if(ev.key==='ArrowLeft')dx=-1;else if(ev.key==='ArrowRight')dx=1;else if(ev.key==='ArrowUp')dy=-1;else if(ev.key==='ArrowDown')dy=1;
    else if(ev.key==='Delete'||ev.key==='Backspace'){ev.preventDefault();bimBrdRemove(k);return;}
    else if(ev.key==='Enter'||ev.key===' '||ev.key==='ContextMenu'){ev.preventDefault();r=t.getBoundingClientRect();bimBrdMenu(k,r.left+16,r.top+16);return;}
    else return;
    ev.preventDefault();
    if(A3D_CLB.narrow){if(dy)bimBrdSwap(k,dy);return;}
    st=A3D_SNAP.grid?1:0.1;
    bimBrdNudge(k,dx*st,dy*st,ev.shiftKey);
  }
  /* ---- a figure's menu ---- */
  function bimBrdMenu(k,x,y){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k),ord,j,it;
    if(!F)return false;
    ord=bimBrdOrder(L);j=ord.indexOf(k);
    it=[[F.f==='text'?'The heading…':'Options…','opts'],['Fit the height to its content','fit'],['Duplicate','dup']];
    if(j>0||j<ord.length-1)it.push('-');
    if(j>0)it.push(['Earlier in reading order','earlier']);
    if(j>=0&&j<ord.length-1)it.push(['Later in reading order','later']);
    it.push('-',['Remove from the board','remove',true]);
    bimLtMenuOpen(x,y,it,function(a){bimBrdMenuDo(a,k);});
    return true;
  }
  function bimBrdMenuDo(a,k){
    if(a==='opts')return bimBrdOptsDlg(k);
    if(a==='fit')return bimBrdFit(k);
    if(a==='dup')return bimBrdDup(k);
    if(a==='earlier'||a==='later')return bimBrdSwap(k,a==='earlier'?-1:1);
    if(a==='remove')return bimBrdRemove(k);
    return false;
  }
  function bimBrdFit(k){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k);if(!F)return false;
    F.h=bimBrdNatH(F,F.w);
    if(A3D_SNAP.grid)F.h=Math.max(1,Math.ceil(F.y+F.h-1e-6)-F.y);
    return bimBrdCommit(B,L,'Fitted to its content',k);
  }
  function bimBrdDup(k){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k),N;
    if(!F)return false;
    N=JSON.parse(JSON.stringify(F));
    N.k=bimBrdNewK(L);N.y=bimBrdBottom(L);
    if(A3D_SNAP.grid)N.y=Math.ceil(N.y-1e-6);
    L.push(N);
    return bimBrdCommit(B,L,'Duplicated, below the others',N.k);
  }
  /* earlier or later in reading order: the two figures change places, each taking the other's place and size */
  function bimBrdSwap(k,d){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),ord=bimBrdOrder(L),j=ord.indexOf(k),m=j+d,a,b,t;
    if(j<0||m<0||m>=ord.length)return false;
    a=bimBrdFind(L,k);b=bimBrdFind(L,ord[m]);
    t={x:a.x,y:a.y,w:a.w,h:a.h};
    a.x=b.x;a.y=b.y;a.w=b.w;a.h=b.h;b.x=t.x;b.y=t.y;b.w=t.w;b.h=t.h;
    return bimBrdCommit(B,L,d<0?'Moved earlier':'Moved later',k);
  }
  function bimBrdRemove(k){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k),E,off=null,lab=bimBrdLabelOf(k);
    if(!F)return false;
    L=L.filter(function(x){return x.k!==k;});
    E=bimFigEntry(F.f);
    if(B.kind!=='custom'&&E&&E.kind===B.kind&&!E.kpis&&!L.some(function(x){return x.f===F.f;})){
      off=(B.off||[]).slice();if(off.indexOf(F.f)<0)off.push(F.f);
    }
    return bimBrdCommit(B,L,lab+' is off the board; Ctrl+Z brings it back',null,off);
  }
  /* a figure from the catalogue, below the others at its own width and height */
  function bimBrdAddFig(f,o){
    var B=bimBrdRec(),E=bimFigEntry(f);
    if(!B||!E){a3dToast(B?'There is no such figure':'Only a board in the set can be arranged');return null;}
    var L=bimBrdWorking(B),ctx={edit:false,narrow:false,caps:{},no:0},opts=bimBrdOpts(o),P=f==='text'?null:bimFigSrc(ctx,f,opts),F,off=null;
    if(f!=='text'&&!P){a3dToast(bimFigHint(E));return null;}
    F={k:bimBrdNewK(L),f:f,x:0,y:bimBrdBottom(L),w:f==='text'?12:bimFigSpan(P),h:1};
    if(f==='text'&&!opts.t)opts.t='A heading';
    if(Object.keys(opts).length)F.o=opts;
    if(A3D_SNAP.grid)F.y=Math.ceil(F.y-1e-6);
    F.h=bimBrdNatH(F,F.w);
    if(A3D_SNAP.grid)F.h=Math.max(1,Math.ceil(F.h-1e-6));
    L.push(F);
    if(B.off&&B.off.indexOf(f)>=0)off=B.off.filter(function(x){return x!==f;});
    bimBrdDlgClose();
    if(!bimBrdCommit(B,L,(f==='text'?'A heading':E.name)+' is on the board, below the others: drag it into place',F.k,off))return null;
    return F.k;
  }
  function bimBrdReset(){
    var B=bimBrdRec();
    if(!B||B.kind==='custom'||!B.figs)return false;
    pushUndo();
    delete B.figs;delete B.off;
    saveSoon();bimBrdRedraw();
    a3dToast(bimBoardLabel(B)+': its own figures in their own places again');
    return true;
  }
  function bimBrdOptsSet(k,o){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k);if(!F)return false;
    o=bimBrdOpts(o);
    if(F.f==='text'&&!o.t)o.t='A heading';
    if(Object.keys(o).length)F.o=o;else delete F.o;
    return bimBrdCommit(B,L,null,k);
  }
  /* ---- dialogs: options, and the catalogue ---- */
  function bimBrdDlgClose(){
    var d=A3D_BRD.dlg,f=A3D_BRD.dlgFrom;
    A3D_BRD.dlg=null;A3D_BRD.dlgFrom=null;
    if(d&&d.parentNode)d.parentNode.removeChild(d);
    if(f&&f.isConnected)try{f.focus({preventScroll:true});}catch(eF){}
  }
  function bimBrdDlgOpen(html,label,wide){
    bimBrdDlgClose();
    var d=document.createElement('div');
    A3D_BRD.dlgFrom=document.activeElement;
    d.className='a3d-clb a3d-clb-dlg';   /* the board's colours, and its charts' rules for the previews */
    d.setAttribute('role','dialog');d.setAttribute('aria-modal','true');d.setAttribute('aria-label',label);
    d.innerHTML='<div class="a3d-clb-dlgin'+(wide?' wide':'')+'">'+html+'</div>';
    document.body.appendChild(d);
    A3D_BRD.dlg=d;
    d.addEventListener('click',bimBrdDlgClick);
    d.addEventListener('submit',bimBrdDlgSubmit);
    d.addEventListener('keydown',function(ev){if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();bimBrdDlgClose();}});
    var first=d.querySelector('input,select,button:not([disabled])');
    if(first)try{first.focus({preventScroll:true});}catch(eF){}
    return d;
  }
  function bimBrdDlgClick(ev){
    var t=ev.target,a;
    if(t===A3D_BRD.dlg){bimBrdDlgClose();return;}   /* the scrim */
    a=t&&t.closest?t.closest('[data-brddlg],[data-brdaddf]'):null;
    if(!a)return;
    if(a.hasAttribute('data-brdaddf')){if(!a.disabled)bimBrdAddFig(a.getAttribute('data-brdaddf'));return;}
    if(a.getAttribute('data-brddlg')==='cancel')bimBrdDlgClose();
  }
  function bimBrdDlgSubmit(ev){
    var f=ev.target,k=f&&f.getAttribute('data-brdform'),o={},el;
    if(!k)return;
    ev.preventDefault();
    el=f.querySelector('[name="t"]');if(el)o.t=el.value;
    el=f.querySelector('[name="show"]');if(el&&el.value)o.show=el.value;
    el=f.querySelector('[name="cond"]');if(el&&el.value)o.cond=el.value;
    bimBrdDlgClose();
    bimBrdOptsSet(k,o);
  }
  function bimBrdOptsDlg(k){
    var B=bimBrdRec();if(!B)return false;
    var L=bimBrdWorking(B),F=bimBrdFind(L,k),E,o,h;
    if(!F)return false;
    E=bimFigEntry(F.f);o=F.o||{};
    function opt(v,t,cur){return '<option value="'+v+'"'+(v===(cur||'')?' selected':'')+'>'+bimClbE(t)+'</option>';}
    h='<form class="a3d-clb-dlgf" data-brdform="'+F.k+'"><h2 class="a3d-clb-h2">'+bimClbE(F.f==='text'?'The heading':'Options: '+(E?E.name:F.f))+'</h2>'+
      '<label>'+(F.f==='text'?'Heading':'Title, or empty for the figure\'s own')+'<input type="text" name="t" maxlength="200" value="'+bimClbE(o.t||'')+'"></label>'+
      (F.f!=='text'&&E&&!E.kpis?'<label>Show<select name="show">'+opt('','The chart; its numbers with Tables',o.show)+opt('table','Its numbers, as a table',o.show)+opt('both','The chart and its numbers',o.show)+'</select></label>':'')+
      (F.f==='lb.utci'?'<label>Condition<select name="cond">'+['sun_wind','shade_wind','sun_still','shade_still'].map(function(c){return opt(c,BIM_LB_COND[c],o.cond||'sun_wind');}).join('')+'</select></label>':'')+
      '<div class="a3d-clb-dlgb"><button type="button" class="a3d-clb-btn" data-brddlg="cancel">Cancel</button><button type="submit" class="a3d-clb-btn pri">Apply</button></div></form>';
    bimBrdDlgOpen(h,F.f==='text'?'The heading':'Options of '+(E?E.name:F.f));
    return true;
  }
  /* every figure the project can draw, by group, each with its preview; those without data say where it comes from */
  function bimBrdCatalogue(){
    if(!bimBrdRec()){a3dToast('Only a board in the set can be arranged');return false;}
    var ctx={edit:false,narrow:false,caps:{},no:0},groups={},order=[],h;
    bimFigCat().forEach(function(E){
      var P=E.f==='text'?null:bimFigSrc(ctx,E.f,null);
      if(!groups[E.cat]){groups[E.cat]=[];order.push(E.cat);}
      groups[E.cat].push([E,P]);
    });
    h='<div class="a3d-clb-dlghd"><h2 class="a3d-clb-h2">Add a figure</h2><p class="a3d-clb-dek">Any analysis the project has, from any board. It goes below the others at its own width; then drag it into place.</p></div><div class="a3d-clb-catl">';
    order.forEach(function(c){
      h+='<h3 class="a3d-clb-catg">'+bimClbE(c)+'</h3><div class="a3d-clb-catgrid">';
      groups[c].forEach(function(it){
        var E=it[0],P=it[1],ok=E.f==='text'||!!P,pv='';
        if(E.f==='text')pv='<div class="a3d-clb-catpv t" aria-hidden="true"><div class="a3d-clb-texth">A heading</div></div>';
        else if(P)pv='<div class="a3d-clb-catpv" aria-hidden="true"><div class="a3d-clb-catin">'+bimFigCardHtml({f:E.f},P,1)+'</div></div>';
        h+='<button type="button" class="a3d-clb-cat" data-brdaddf="'+E.f+'"'+(ok?'':' disabled')+'>'+pv+'<span class="a3d-clb-catn">'+bimClbE(E.name)+'</span>'+
          (ok?'':'<span class="a3d-clb-cath">'+bimClbE(bimFigHint(E))+'</span>')+'</button>';
      });
      h+='</div>';
    });
    h+='</div><div class="a3d-clb-dlgb"><button type="button" class="a3d-clb-btn" data-brddlg="cancel">Close</button></div>';
    bimBrdDlgOpen(h,'Add a figure',true);
    return true;
  }
  /* ---- boards of one's own ---- */
  function bimBrdNew(name,figs){
    var P=bimPresData(),n=0,id,r;
    P.boards.forEach(function(b){var m=/^board-c(\d+)$/.exec(b.id);if(m&&+m[1]>n)n=+m[1];});
    id='board-c'+(n+1);
    r=bimBrdKeep({id:id,kind:'custom'},{name:name||('Board '+(n+1)),figs:figs||[]});
    pushUndo();
    P.order=bimPresSeq().map(function(e){return e.id;});
    P.boards.push(r);P.order.push(id);
    saveSoon();bimPresPanelRefresh();
    return id;
  }
  /* a new board, opened in Edit with the catalogue */
  function bimBrdNewUi(name,figs){
    var id=bimBrdNew(name,figs);
    bimShellSetTab('presentation');
    if(!bimPresOpenBoard(id))return id;
    A3D_CLB.edit=true;bimClbOpen();
    a3dToast(bimBoardLabel(bimBoardById(id))+' is page '+(bimPresIndex(id)+1)+' of the set'+((figs&&figs.length)?'':': add its figures'));
    if(!figs||!figs.length)bimBrdCatalogue();
    return id;
  }
  /* a board copied as a board of one's own: one of the three as it is laid out, its indicators on top */
  function bimBrdDupBoard(id){
    var B=bimBoardById(id),L,top=0,add=[],ctx={edit:false,narrow:false,caps:{},no:0};
    if(!B)return null;
    L=bimBrdWorking(B);
    if(B.kind!=='custom'){
      bimFigCat().forEach(function(E){
        if(!E.kpis||E.kind!==B.kind||!bimFigSrc(ctx,E.f,null))return;
        var F={k:'',f:E.f,x:0,y:top,w:12,h:1};F.h=bimBrdNatH(F,12);add.push(F);top+=F.h;
      });
      L.forEach(function(F){F.y+=top;F.k='';});
      L=add.concat(L);
    }
    return bimBrdNewUi('Copy of '+bimBoardLabel(B),L);
  }
  function bimBrdRename(name){
    var B=bimBrdRec();
    name=String(name||'').replace(/\s+/g,' ').trim().slice(0,80);
    if(!B||B.kind!=='custom'||!name||name===B.name)return false;
    pushUndo();
    B.name=name;
    saveSoon();bimBrdRedraw();bimPresPanelRefresh();
    return true;
  }
  /* ---- the board's own listeners ---- */
  function bimBrdClick(ev){
    var t=ev.target,a=t&&t.closest?t.closest('[data-brd],[data-brdsnap],[data-brdmenu],[data-brdplace]'):null,s,r,f;
    if(!a)return;
    if(a.hasAttribute('data-brdmenu')){f=a.closest('.a3d-clb-fig');r=a.getBoundingClientRect();if(f)bimBrdMenu(f.getAttribute('data-brdk'),r.left,r.bottom+4);return;}
    if(a.hasAttribute('data-brdplace')){bimBrdAddFig(a.getAttribute('data-brdplace'));return;}
    if(a.hasAttribute('data-brdsnap')){
      s=a.getAttribute('data-brdsnap');
      A3D_SNAP[s]=!A3D_SNAP[s];
      a3dToast((s==='point'?'Object snap':(s==='grid'?'Grid snap':'Ortho'))+' '+(A3D_SNAP[s]?'on':'off')+' ('+(s==='point'?'F3':(s==='grid'?'F9':'F8'))+')');
      syncSnapPill();
      return;
    }
    s=a.getAttribute('data-brd');
    if(s==='edit')bimBrdEdit(!A3D_CLB.edit);
    else if(s==='done')bimBrdEdit(false);
    else if(s==='add')bimBrdCatalogue();
    else if(s==='addnew'){if(!A3D_CLB.edit){A3D_CLB.edit=true;bimClbOpen();}bimBrdCatalogue();}
    else if(s==='reset')bimBrdReset();
  }
  function bimBrdChange(ev){
    var t=ev.target;
    if(t&&t.getAttribute&&t.getAttribute('data-brdname'))bimBrdRename(t.value);
  }
  function bimBrdCtx(ev){
    if(!bimBrdEditing())return;
    var f=ev.target&&ev.target.closest?ev.target.closest('.a3d-clb-arr .a3d-clb-fig'):null;
    if(!f)return;
    ev.preventDefault();
    bimBrdMenu(f.getAttribute('data-brdk'),ev.clientX,ev.clientY);
  }
  function bimBrdWire(b){
    b.addEventListener('click',bimBrdClick);
    b.addEventListener('change',bimBrdChange);
    b.addEventListener('pointerdown',bimBrdDown);
    b.addEventListener('pointermove',bimBrdMoveEv);
    b.addEventListener('pointerup',bimBrdUp);
    b.addEventListener('pointercancel',bimBrdCancel);
    b.addEventListener('keydown',bimBrdKey);
    b.addEventListener('contextmenu',bimBrdCtx);
  }
