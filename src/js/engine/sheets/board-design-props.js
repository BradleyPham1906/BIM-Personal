import { bimLayerBlend, bimLayerById } from '../layers/layer-rules.js';
import { bimEsc, bimLayerOptionsHtml } from '../layers/layer-manager.js';
import { bimPropGroup, bimPropRow, bimPropText } from '../properties/palette.js';
import { bimBrdEditing } from './board-figures.js';
import {
  bimBobBlend, bimBobBlends, bimBobBox, bimBobFind, bimBobKind, bimBobLayer, bimBobMaskTypes
} from './board-objects.js';
import { bimBdsPres } from './board-design.js';
import {
  A3D_BDE, bimBdeAddImage, bimBdeDo, bimBdeFigBox, bimBdeName, bimBdeOwnsProps, bimBdeSel, bimBdeSet,
  bimBdeWork
} from './board-design-edit.js';


  /* ================= __acad3dV174a: a board's objects in the Layers tab and the Properties panel =================
     No panel of their own (the owner, 2026-11-08): a board's objects are listed in the Layers tab under the layer
     each is on, and the selected ones are shown in the Properties panel, as the model's objects are. Their Layer is
     chosen there, and their Transparency and Blend are ByLayer unless set (R2). */
  /* the rows of a layer's board objects, under its row in the Layers tab, while a board is drawn on */
  function bimBdeLyRows(lyId,depth,f){
    var W,h='';
    if(!bimBrdEditing())return '';
    W=bimBdeWork();if(!W)return '';
    W.objs.forEach(function(n){
      var ly=bimBobLayer(n),nm,sel;
      if(!ly||ly.id!==lyId)return;
      nm=bimBdeName(n,W);
      if(f&&String(nm).toLowerCase().indexOf(f)<0)return;
      sel=A3D_BDE.sel.indexOf(n.id)>=0;
      h+='<div class="a3d-lyobj a3d-lybo'+(sel?' sel':'')+'" data-lybo="'+bimEsc(n.id)+'" style="padding-left:'+(22+depth*14)+'px" title="'+bimEsc(nm)+' -- on the board">'+
        '<span class="a3d-lydot" style="background:'+bimEsc(n.fill&&n.fill!=='none'?n.fill:(n.stroke&&n.stroke!=='none'?n.stroke:(n.col||'#7f9db8')))+'"></span>'+
        '<span class="a3d-lynm">'+bimEsc(nm)+'</span><span class="a3d-lyty">'+(n.mask?'mask':'board '+bimEsc((bimBobKind(n.t)||['',n.t])[1].toLowerCase()))+'</span></div>';
    });
    return h;
  }
  function bimBdeLyCount(lyId){
    var W;
    if(!bimBrdEditing())return 0;
    W=bimBdeWork();if(!W)return 0;
    return W.objs.filter(function(n){var ly=bimBobLayer(n);return ly&&ly.id===lyId;}).length;
  }
  /* ---- the Properties panel ---- */
  function bimBdeOpt(v,t,cur){return '<option value="'+bimEsc(v)+'"'+(String(v)===String(cur)?' selected':'')+'>'+bimEsc(t)+'</option>';}
  function bimBdeNum(lab,name,v,step,min,max){
    return bimPropRow(lab,'<input type="number" data-bdf="'+name+'" value="'+(Math.round(v*100)/100)+'" step="'+step+'"'+(min!==undefined?' min="'+min+'"':'')+(max!==undefined?' max="'+max+'"':'')+'>');
  }
  function bimBdeCol(lab,name,v,none){
    var on=v&&v!=='none';
    return bimPropRow(lab,'<input type="color" data-bdf="'+name+'" value="'+(on?v:'#000000')+'"'+(on?'':' disabled')+'>'+
      (none?' <label class="a3d-bdechk"><input type="checkbox" data-bdf="'+name+':on"'+(on?' checked':'')+'> '+bimEsc(lab)+'</label>':''));
  }
  function bimBdeChk(lab,name,on){return bimPropRow(lab,'<input type="checkbox" data-bdf="'+name+'"'+(on?' checked':'')+'>');}
  function bimBdeBtn(a,label,title,danger){return '<button type="button" class="a3d-pedit" data-bdact="'+a+'"'+(title?' title="'+bimEsc(title)+'"':'')+(danger?' style="color:#ff8a80"':'')+'>'+bimEsc(label)+'</button>';}
  function bimBdePropsHtml(){
    var W=bimBdeWork(),S,n,K,h,lyId,same,trs,bms,ly,lt,lb,g='',fb,b;
    if(!W)return '';
    S=bimBdeSel(W);if(!S.length)return '';
    n=bimBobFind(W.objs,S[0]).n;K=bimBobKind(n.t);
    lyId=bimBobLayer(n)?bimBobLayer(n).id:'';
    same=function(k){return S.every(function(x){var q=bimBobFind(W.objs,x).n;return q[k]===n[k];});};
    h='<div class="a3d-ptypehd"><div class="a3d-ptypetx"><div class="a3d-ptypename">'+bimEsc(S.length>1?S.length+' board objects':bimBdeName(n,W))+'</div>'+
      '<div class="a3d-ptypesub">'+bimEsc(S.length>1?'On the board':'Board '+(K?K[1].toLowerCase():n.t))+'</div></div></div>';
    ly=bimLayerById(lyId);
    lt=ly&&isFinite(ly.transparency)?Math.min(90,+ly.transparency):0;lb=bimBobBlend(bimLayerBlend(ly));
    trs=same('tr')&&typeof n.tr==='number'?n.tr:'';
    bms=same('bm')&&n.bm?n.bm:'';
    g+=bimPropRow('Layer','<select data-bdf="layer">'+bimLayerOptionsHtml(S.every(function(x){var q=bimBobLayer(bimBobFind(W.objs,x).n);return q&&q.id===lyId;})?lyId:'')+'</select>');
    g+=bimPropRow('Transparency','<input type="number" data-bdf="tr" min="0" max="90" step="5" value="'+trs+'" placeholder="ByLayer ('+lt+')" title="Empty: ByLayer">');
    g+=bimPropRow('Blend','<select data-bdf="bm">'+bimBdeOpt('','ByLayer ('+(lb?lb[1]:'Normal')+')',bms)+bimBobBlends().map(function(x){return bimBdeOpt(x[0],x[1],bms);}).join('')+'</select>');
    if(!bimBdsPres())g+='<div class="a3d-pnote">Transparency and blend modes show in the Presentation appearance (Pres in the status bar) and in Present.</div>';
    h+=bimPropGroup('Graphics',g);
    if(S.length===1){
      g='';
      if(n.t==='fig'){
        fb=bimBdeFigBox(W);b=bimBobBox(n,fb);
        if(b)g+=bimPropText('Place (mm)',Math.round(b.x)+', '+Math.round(b.y)+'; '+Math.round(b.w)+' x '+Math.round(b.h),true)+'<div class="a3d-pnote">Its handle and its corner on the board move and size it.</div>';
      }else{
        g+=bimBdeNum('X (mm)','x',n.x,1)+bimBdeNum('Y (mm)','y',n.y,1)+
          bimBdeNum(n.t==='line'?'Run (mm)':'Width (mm)','w',n.w,1,n.t==='line'?undefined:0.5)+bimBdeNum(n.t==='line'?'Rise (mm)':'Height (mm)','h',n.h,1,n.t==='line'?undefined:0.5);
      }
      h+=bimPropGroup('Dimensions',g);
      g='';
      if(n.t!=='fig')g+=bimPropRow('Name','<input type="text" data-bdf="nm" maxlength="80" value="'+bimEsc(n.nm||'')+'" placeholder="'+bimEsc(bimBdeName(n,W))+'">');
      if(K&&K[2])g+=bimPropRow('Mask','<select data-bdf="mask">'+bimBdeOpt('','Not a mask',n.mask||'')+bimBobMaskTypes().map(function(m){return bimBdeOpt(m[0],m[1],n.mask||'');}).join('')+'</select>')+
        (n.mask?'<div class="a3d-pnote">It clips the objects of its layer drawn above it, up to the layer\'s next mask.</div>':'');
      if(n.fill!==undefined)g+=bimBdeCol('Fill','fill',n.fill,true)+bimBdeNum('Fill opacity (%)','fop',n.fop*100,5,0,100);
      if(n.stroke!==undefined)g+=bimBdeCol('Stroke','stroke',n.stroke,true)+bimBdeNum('Stroke (mm)','sw',n.sw,0.05,0,50);
      if(n.r!==undefined)g+=bimBdeNum('Corner (mm)','r',n.r,0.5,0);
      if(n.t==='poly')g+=bimBdeNum('Sides','n',n.n,1,3,60);
      if(n.t==='star')g+=bimBdeNum('Points','n',n.n,1,3,60)+bimBdeNum('Inner (%)','ri',n.ri*100,1,5,95);
      if(n.t==='line')g+=bimBdeChk('Arrow at its start','a0',n.a0)+bimBdeChk('Arrow at its end','a1',n.a1);
      if(n.t==='text'){
        g+=bimPropRow('Text','<textarea data-bdf="s" rows="3" maxlength="4000">'+bimEsc(n.s)+'</textarea>')+bimBdeNum('Size (pt)','fs',n.fs,1,4,400)+bimBdeCol('Colour','col',n.col,false)+
          bimPropRow('Align','<select data-bdf="al">'+bimBdeOpt('left','Left',n.al)+bimBdeOpt('center','Centre',n.al)+bimBdeOpt('right','Right',n.al)+'</select>')+
          bimPropRow('Box','<select data-bdf="fit">'+bimBdeOpt('auto-w','Auto width',n.fit)+bimBdeOpt('auto-h','Auto height',n.fit)+bimBdeOpt('fixed','Fixed size',n.fit)+'</select>')+
          bimBdeChk('Bold','fw',n.fw===700);
      }
      if(n.t==='image')g+=bimPropRow('Fit','<select data-bdf="fit">'+bimBdeOpt('fill','Fill',n.fit)+bimBdeOpt('fit','Fit',n.fit)+bimBdeOpt('tile','Tile',n.fit)+'</select>')+
        bimPropRow('Image',bimBdeBtn('swapimg','Another image…'));
      if(g)h+=bimPropGroup('Other',g);
    }
    h+=bimPropGroup('Draw order','<div class="a3d-bdeacts">'+bimBdeBtn('front','To front','Ctrl+Shift+]: within its layer')+bimBdeBtn('forward','Forward','Ctrl+]')+
      bimBdeBtn('backward','Backward','Ctrl+[')+bimBdeBtn('back','To back','Ctrl+Shift+[')+bimBdeBtn('dup','Duplicate','Ctrl+D')+bimBdeBtn('del','Delete','Delete',true)+'</div>'+
      '<div class="a3d-pnote">The layers set what is drawn over what: a layer higher in the Layers list is drawn over those below.</div>');
    return h;
  }
  /* once, on the panel's body: its board fields and buttons */
  function bimBdePropsWire(body){
    if(!body||body.getAttribute('data-bdewired'))return;
    body.setAttribute('data-bdewired','1');
    body.addEventListener('click',function(ev){
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-bdact]'):null,v;
      if(!a||!bimBdeOwnsProps())return;
      v=a.getAttribute('data-bdact');
      if(v==='swapimg'){if(A3D_BDE.sel.length===1)bimBdeAddImage(A3D_BDE.sel[0]);}
      else bimBdeDo(v);
    });
    body.addEventListener('change',function(ev){
      var t=ev.target,f=t&&t.getAttribute&&t.getAttribute('data-bdf'),o={},v;
      if(!f||!bimBdeOwnsProps())return;
      if(/:on$/.test(f)){f=f.slice(0,-3);o[f]=t.checked?((t.closest('.a3d-prow')||t.parentNode).querySelector('input[type=color]')||{}).value||'#000000':'none';}
      else if(f==='tr'){v=t.value.trim();if(v===''){o.tr=null;}else{v=+v;if(!isFinite(v))return;o.tr=Math.round(Math.max(0,Math.min(90,v)));}}
      else if(f==='bm'||f==='mask')o[f]=t.value||null;
      else if(f==='layer'){if(!t.value||!bimLayerById(t.value))return;o.layer=t.value;}
      else if(f==='fop'||f==='ri'){v=parseFloat(t.value);if(!isFinite(v))return;o[f]=Math.max(0,Math.min(1,v/100));}
      else if(f==='nm')o.nm=t.value.replace(/\s+/g,' ').trim()||null;
      else if(f==='al'||f==='fit'||f==='fill'||f==='stroke'||f==='col'||f==='s')o[f]=t.value;
      else if(f==='a0'||f==='a1')o[f]=t.checked?true:null;
      else if(f==='fw')o.fw=t.checked?700:400;
      else{v=parseFloat(t.value);if(!isFinite(v))return;o[f]=v;}
      bimBdeSet(null,o);
    });
  }
export { bimBdeLyCount, bimBdeLyRows, bimBdePropsHtml, bimBdePropsWire };
