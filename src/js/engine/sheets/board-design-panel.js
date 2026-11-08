import { A3D_CLB, bimClbE, bimClbEl } from '../site-analysis/climate-board.js';
import { bimBrdEditing } from './board-figures.js';
import { bimBrdEdit } from './board-edit.js';
import {
  bimBtrBlends, bimBtrBox, bimBtrEff, bimBtrFind, bimBtrIsBox, bimBtrKind, bimBtrMaskTypes
} from './board-tree.js';
import {
  A3D_BDE, bimBdeAdd, bimBdeAddImage, bimBdeCommit, bimBdeDo, bimBdeEnter, bimBdeEsc, bimBdeFigBox,
  bimBdeInto, bimBdeName, bimBdeSel, bimBdeSet, bimBdeSync, bimBdeWork
} from './board-design-edit.js';


  /* ================= __acad3dV174a: the board's layers and properties, beside it in Edit =================
     One panel, over the board's right side on a wide screen and at the bottom on a phone: what can be added, the
     layer list (the front at the top, as Figma and QGIS list it; lock and hide on each row; a group or frame opens
     and folds), and the selection's properties: its box in millimetres, opacity, blend mode, mask, and its kind's
     own fields. The buttons under the list do what the keys do, for a finger. */
  function bimBdeIco(p){return '<svg viewBox="0 0 16 16" aria-hidden="true">'+p+'</svg>';}
  function bimBdeIcons(){
    if(bimBdeIcons.I)return bimBdeIcons.I;
    bimBdeIcons.I={
      lockOn:bimBdeIco('<rect x="3.5" y="7" width="9" height="7" rx="1.5"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" fill="none" stroke="currentColor" stroke-width="1.5"/>'),
      lockOff:bimBdeIco('<rect x="3.5" y="7" width="9" height="7" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0" fill="none" stroke="currentColor" stroke-width="1.3"/>'),
      eyeOn:bimBdeIco('<path d="M1.5 8s2.5-4.5 6.5-4.5S14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2"/>'),
      eyeOff:bimBdeIco('<path d="M1.5 8s2.5-4.5 6.5-4.5S14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8z" fill="none" stroke="currentColor" stroke-width="1.3" opacity=".45"/><path d="M2.5 13.5l11-11" stroke="currentColor" stroke-width="1.4"/>'),
      fold:bimBdeIco('<path d="M6 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6"/>'),
      open:bimBdeIco('<path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/>')
    };
    return bimBdeIcons.I;
  }
  function bimBdePanelClose(){
    var p=A3D_BDE.pnl;
    A3D_BDE.pnl=null;
    if(p&&p.parentNode)p.parentNode.removeChild(p);
  }
  function bimBdePanelEl(){
    var p=A3D_BDE.pnl;
    if(p&&p.isConnected)return p;
    p=A3D_BDE.pnl=document.createElement('aside');
    p.className='a3d-clb a3d-clb-dpnl';   /* the board's colours */
    p.setAttribute('aria-label','The board\'s layers and properties');
    p.addEventListener('click',bimBdePanelClick);
    p.addEventListener('change',bimBdePanelChange);
    p.addEventListener('keydown',function(ev){
      if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();if(!bimBdeEsc())bimBrdEdit(false);}
      else if(ev.key==='Enter'&&ev.target&&ev.target.tagName==='INPUT'){ev.preventDefault();ev.target.blur();}
    });
    document.body.appendChild(p);
    return p;
  }
  /* placed over the board's right side, under its bar; a phone's: the bottom of the screen */
  function bimBdePanelPlace(p){
    var b=bimClbEl(),r,bar;
    if(!b)return;
    if(A3D_CLB.narrow){p.classList.add('nar');p.style.cssText='';return;}
    p.classList.remove('nar');
    r=b.getBoundingClientRect();bar=b.querySelector('.a3d-clb-bar');
    var top=r.top+(bar?bar.getBoundingClientRect().height:44)+8;
    p.style.cssText='top:'+Math.round(top)+'px;right:'+Math.round(Math.max(8,window.innerWidth-r.right+12))+'px;max-height:'+Math.round(Math.max(160,r.bottom-top-12))+'px';
  }
  function bimBdeOpt(v,t,cur){return '<option value="'+bimClbE(v)+'"'+(String(v)===String(cur)?' selected':'')+'>'+bimClbE(t)+'</option>';}
  function bimBdeNumF(lab,name,v,step,min,max){
    return '<label class="a3d-clb-dfld"><span>'+lab+'</span><input type="number" data-bdf="'+name+'" value="'+(Math.round(v*100)/100)+'" step="'+step+'"'+(min!==undefined?' min="'+min+'"':'')+(max!==undefined?' max="'+max+'"':'')+'></label>';
  }
  function bimBdeColF(lab,name,v,none){
    var on=v&&v!=='none';
    return '<label class="a3d-clb-dfld col"><span>'+lab+'</span><input type="color" data-bdf="'+name+'" value="'+(on?v:'#000000')+'"'+(on?'':' disabled')+'>'+
      (none?'<input type="checkbox" data-bdf="'+name+':on" aria-label="'+bimClbE(lab)+' on"'+(on?' checked':'')+'>':'')+'</label>';
  }
  function bimBdeChkF(lab,name,on){return '<label class="a3d-clb-dfld chk"><input type="checkbox" data-bdf="'+name+'"'+(on?' checked':'')+'><span>'+lab+'</span></label>';}
  /* the list: the front at the top; rows indented by depth */
  function bimBdeRows(L,W,depth,boxes,par){
    var I=bimBdeIcons(),h='',i,n,sel,eff,mk=false;
    /* a row under a mask is marked so: the mask's run, from the bottom */
    var under={};
    for(i=0;i<L.length;i++){if(L[i].mask&&!L[i].hide)mk=true;else if(mk)under[L[i].id]=1;}
    for(i=L.length-1;i>=0;i--){
      n=L[i];sel=A3D_BDE.sel.indexOf(n.id)>=0;eff=bimBtrEff(W.els,n.id);
      if(bimBtrIsBox(n))boxes.push([n.id,new Array(depth+1).join('  ')+bimBdeName(n,W)]);
      h+='<li class="a3d-clb-drow'+(sel?' sel':'')+(eff.hide?' hid':'')+'" style="--d:'+depth+'">'+
        (bimBtrIsBox(n)?'<button type="button" class="a3d-clb-dic" data-bdfold="'+n.id+'" aria-label="'+(A3D_BDE.fold[n.id]?'Open ':'Fold ')+bimClbE(bimBdeName(n,W))+'" aria-expanded="'+!A3D_BDE.fold[n.id]+'">'+(A3D_BDE.fold[n.id]?I.fold:I.open)+'</button>':'<span class="a3d-clb-dic sp"></span>')+
        '<button type="button" class="a3d-clb-dnm" data-bdsel="'+n.id+'" aria-pressed="'+sel+'">'+(n.mask?'<b class="a3d-clb-dtag">Mask</b>':'')+(under[n.id]?'<span class="a3d-clb-dtag u">masked</span>':'')+
          '<span class="a3d-clb-dkd">'+bimClbE((bimBtrKind(n.t)||['',n.t])[1])+'</span> '+bimClbE(bimBdeName(n,W))+'</button>'+
        '<button type="button" class="a3d-clb-dic" data-bdtog="lock" data-bdid="'+n.id+'" aria-pressed="'+!!n.lock+'" aria-label="'+(n.lock?'Unlock ':'Lock ')+bimClbE(bimBdeName(n,W))+'" title="Lock">'+(n.lock?I.lockOn:I.lockOff)+'</button>'+
        '<button type="button" class="a3d-clb-dic" data-bdtog="hide" data-bdid="'+n.id+'" aria-pressed="'+!!n.hide+'" aria-label="'+(n.hide?'Show ':'Hide ')+bimClbE(bimBdeName(n,W))+'" title="Hide">'+(n.hide?I.eyeOff:I.eyeOn)+'</button></li>';
      if(n.ch&&!A3D_BDE.fold[n.id])h+=bimBdeRows(n.ch,W,depth+1,boxes,n);
    }
    return h;
  }
  function bimBdeProps(W,S){
    var h='',n,f,K,bl,b,act;
    act='<div class="a3d-clb-dacts" role="group" aria-label="Arrange">'+
      [['forward','Forward','Ctrl+]'],['backward','Backward','Ctrl+['],['front','To front','Ctrl+Shift+]'],['back','To back','Ctrl+Shift+['],
       ['group','Group','Ctrl+G'],['frame','Frame',''],['ungroup','Ungroup','Ctrl+Shift+G'],['enter','Go in','Enter'],['out','Out of its group','Shift+Enter'],
       ['dup','Duplicate','Ctrl+D'],['del','Delete','Delete']].map(function(a){
        return '<button type="button" class="a3d-clb-btn" data-bdact="'+a[0]+'"'+(a[2]?' title="'+a[2]+'"':'')+(a[0]==='del'?' data-danger="1"':'')+'>'+a[1]+'</button>';}).join('')+'</div>';
    if(!S.length)return '<p class="a3d-clb-dhint">Select an element on the board or in the list. Add puts a new one at the top of what is in view.</p>';
    if(S.length>1){
      return '<h3 class="a3d-clb-dh3">'+S.length+' selected</h3>'+act;
    }
    f=bimBtrFind(W.els,S[0]);n=f.n;K=bimBtrKind(n.t);
    h+='<h3 class="a3d-clb-dh3">'+bimClbE(K?K[1]:n.t)+'</h3>';
    h+='<label class="a3d-clb-dfld wide"><span>Name</span><input type="text" data-bdf="nm" maxlength="80" value="'+bimClbE(n.nm||'')+'" placeholder="'+bimClbE(bimBdeName(n,W))+'"></label>';
    if(typeof n.x==='number'){
      h+='<div class="a3d-clb-dgrid">'+bimBdeNumF('X mm','x',n.x,1)+bimBdeNumF('Y mm','y',n.y,1)+
        bimBdeNumF(n.t==='line'?'Run mm':'W mm','w',n.w,1,n.t==='line'?undefined:0.5)+bimBdeNumF(n.t==='line'?'Rise mm':'H mm','h',n.h,1,n.t==='line'?undefined:0.5)+'</div>';
    }else{b=bimBtrBox(n,bimBdeFigBox(W));if(b)h+='<p class="a3d-clb-dhint">'+Math.round(b.w)+' x '+Math.round(b.h)+' mm, at '+Math.round(b.x)+', '+Math.round(b.y)+(n.t==='fig'?'. Its handle and its corner move and size it, as before.':'')+'</p>';}
    bl=bimBtrBlends().filter(function(x){return x[0]!=='pass'||bimBtrIsBox(n);});
    h+='<div class="a3d-clb-dgrid">'+bimBdeNumF('Opacity %','op',n.op*100,5,0,100)+
      '<label class="a3d-clb-dfld"><span>Blend</span><select data-bdf="bm">'+bl.map(function(x){return bimBdeOpt(x[0],x[1],n.bm);}).join('')+'</select></label></div>';
    if(K&&K[3])h+='<label class="a3d-clb-dfld wide"><span>Mask the elements above it</span><select data-bdf="mask">'+bimBdeOpt('','Not a mask',n.mask||'')+
      bimBtrMaskTypes().map(function(m){return bimBdeOpt(m[0],m[1],n.mask||'');}).join('')+'</select></label>';
    if(n.fill!==undefined)h+='<div class="a3d-clb-dgrid">'+bimBdeColF('Fill','fill',n.fill,true)+(n.fop!==undefined?bimBdeNumF('Fill %','fop',n.fop*100,5,0,100):'')+'</div>';
    if(n.stroke!==undefined)h+='<div class="a3d-clb-dgrid">'+bimBdeColF('Stroke','stroke',n.stroke,true)+bimBdeNumF('Stroke mm','sw',n.sw,0.05,0,50)+'</div>';
    if(n.r!==undefined)h+=bimBdeNumF('Corner mm','r',n.r,0.5,0);
    if(n.t==='poly')h+=bimBdeNumF('Sides','n',n.n,1,3,60);
    if(n.t==='star')h+='<div class="a3d-clb-dgrid">'+bimBdeNumF('Points','n',n.n,1,3,60)+bimBdeNumF('Inner %','ri',n.ri*100,1,5,95)+'</div>';
    if(n.t==='line')h+='<div class="a3d-clb-dgrid">'+bimBdeChkF('Arrow at its start','a0',n.a0)+bimBdeChkF('Arrow at its end','a1',n.a1)+'</div>';
    if(n.t==='frame')h+=bimBdeChkF('Clip its content','clip',n.clip);
    if(n.t==='text'){
      h+='<label class="a3d-clb-dfld wide"><span>Text</span><textarea data-bdf="s" rows="3" maxlength="4000">'+bimClbE(n.s)+'</textarea></label>'+
        '<div class="a3d-clb-dgrid">'+bimBdeNumF('Size pt','fs',n.fs,1,4,400)+bimBdeColF('Colour','col',n.col,false)+
        '<label class="a3d-clb-dfld"><span>Align</span><select data-bdf="al">'+bimBdeOpt('left','Left',n.al)+bimBdeOpt('center','Centre',n.al)+bimBdeOpt('right','Right',n.al)+'</select></label>'+
        '<label class="a3d-clb-dfld"><span>Box</span><select data-bdf="fit">'+bimBdeOpt('auto-w','Auto width',n.fit)+bimBdeOpt('auto-h','Auto height',n.fit)+bimBdeOpt('fixed','Fixed size',n.fit)+'</select></label></div>'+
        bimBdeChkF('Bold','fw',n.fw===700);
    }
    if(n.t==='image')h+='<div class="a3d-clb-dgrid"><label class="a3d-clb-dfld"><span>Fit</span><select data-bdf="fit">'+bimBdeOpt('fill','Fill',n.fit)+bimBdeOpt('fit','Fit',n.fit)+bimBdeOpt('tile','Tile',n.fit)+'</select></label>'+
      '<button type="button" class="a3d-clb-btn" data-bdact="swapimg">Another image…</button></div>';
    return h+act;
  }
  function bimBdePanel(W){
    var p,S,boxes=[],h,into,sc,ss;
    if(!bimBrdEditing()){bimBdePanelClose();return;}
    p=bimBdePanelEl();
    S=bimBdeSel(W);
    sc=p.querySelector('.a3d-clb-dlist');ss=sc?sc.scrollTop:0;
    h='<div class="a3d-clb-dhd"><h2 class="a3d-clb-dh2">Layers</h2>'+(A3D_BDE.scope?'<button type="button" class="a3d-clb-btn" data-bdact="scopeout" title="Shift+Enter">Out of the group</button>':'')+'</div>'+
      '<div class="a3d-clb-dadd" role="group" aria-label="Add">'+[['rect','Rectangle'],['ellipse','Ellipse'],['line','Line'],['arrow','Arrow'],['poly','Polygon'],['star','Star'],['text','Text'],['frame','Frame'],['image','Image…']]
        .map(function(a){return '<button type="button" class="a3d-clb-btn" data-bdadd="'+a[0]+'">'+a[1]+'</button>';}).join('')+'</div>'+
      '<ul class="a3d-clb-dlist" role="list">'+bimBdeRows(W.els,W,0,boxes,null)+'</ul>';
    into=boxes.filter(function(x){return S.indexOf(x[0])<0;});
    h+='<div class="a3d-clb-dprops">'+bimBdeProps(W,S)+
      (S.length&&into.length?'<label class="a3d-clb-dfld wide"><span>Move into</span><select data-bdinto="1">'+bimBdeOpt('','A group or frame…','')+into.map(function(x){return bimBdeOpt(x[0],x[1],'');}).join('')+'</select></label>':'')+'</div>';
    p.innerHTML=h;
    sc=p.querySelector('.a3d-clb-dlist');if(sc&&ss)sc.scrollTop=ss;
    bimBdePanelPlace(p);
  }
  function bimBdePanelClick(ev){
    var t=ev.target,a=t&&t.closest?t.closest('[data-bdadd],[data-bdsel],[data-bdtog],[data-bdfold],[data-bdact]'):null,v,id;
    if(!a)return;
    if(a.hasAttribute('data-bdadd')){v=a.getAttribute('data-bdadd');if(v==='image')bimBdeAddImage();else bimBdeAdd(v);return;}
    if(a.hasAttribute('data-bdsel')){
      id=a.getAttribute('data-bdsel');
      if(ev.shiftKey||ev.ctrlKey||ev.metaKey)A3D_BDE.sel=A3D_BDE.sel.indexOf(id)>=0?A3D_BDE.sel.filter(function(x){return x!==id;}):A3D_BDE.sel.concat([id]);
      else A3D_BDE.sel=[id];
      bimBdeSync();return;
    }
    if(a.hasAttribute('data-bdtog')){bimBdeDo(a.getAttribute('data-bdtog'),[a.getAttribute('data-bdid')]);return;}
    if(a.hasAttribute('data-bdfold')){id=a.getAttribute('data-bdfold');if(A3D_BDE.fold[id])delete A3D_BDE.fold[id];else A3D_BDE.fold[id]=1;bimBdeSync();return;}
    v=a.getAttribute('data-bdact');
    if(v==='enter')bimBdeEnter(false);
    else if(v==='scopeout'){if(!bimBdeEnter(true)){A3D_BDE.scope=null;bimBdeSync();}}
    else if(v==='swapimg'){if(A3D_BDE.sel.length===1)bimBdeAddImage(A3D_BDE.sel[0]);}
    else bimBdeDo(v);
  }
  /* a field changed: one undo step for the element selected */
  function bimBdePanelChange(ev){
    var t=ev.target,f=t&&t.getAttribute&&t.getAttribute('data-bdf'),id=A3D_BDE.sel[0],o={},v,W,S;
    if(t&&t.hasAttribute&&t.hasAttribute('data-bdinto')){if(t.value)bimBdeInto(t.value);return;}
    if(!f)return;
    if(A3D_BDE.sel.length>1&&(f==='op'||f==='bm')){
      W=bimBdeWork();if(!W)return;S=bimBdeSel(W);
      S.forEach(function(x){var q=bimBtrFind(W.els,x);if(f==='op')q.n.op=Math.max(0,Math.min(1,(+t.value||0)/100));else if(t.value!=='pass'||bimBtrIsBox(q.n))q.n.bm=t.value;});
      bimBdeCommit(W,null,S);return;
    }
    if(!id)return;
    if(/:on$/.test(f)){f=f.slice(0,-3);o[f]=t.checked?((t.parentNode.querySelector('input[type=color]')||{}).value||'#000000'):'none';}
    else if(f==='op'||f==='fop'||f==='ri'){v=parseFloat(t.value);if(!isFinite(v))return;o[f]=Math.max(0,Math.min(1,v/100));}
    else if(f==='nm'){o.nm=t.value.replace(/\s+/g,' ').trim()||null;}
    else if(f==='bm'||f==='al'||f==='fit'||f==='fill'||f==='stroke'||f==='col'||f==='s')o[f]=t.value;
    else if(f==='mask')o.mask=t.value||null;
    else if(f==='a0'||f==='a1'||f==='clip')o[f]=t.checked?true:(f==='clip'?false:null);
    else if(f==='fw')o.fw=t.checked?700:400;
    else{v=parseFloat(t.value);if(!isFinite(v))return;o[f]=v;}
    bimBdeSet(id,o);
  }
  window.addEventListener('resize',function(){if(A3D_BDE.pnl&&A3D_BDE.pnl.isConnected)bimBdePanelPlace(A3D_BDE.pnl);});
export { bimBdePanel, bimBdePanelClose };
