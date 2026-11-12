import { bimTrueNorthDeg } from '../survey/survey-arithmetic.js';
import { bimLayerBlend, bimLayerById } from '../layers/layer-rules.js';
import { bimEsc, bimLayerOptionsHtml } from '../layers/layer-manager.js';
import { bimPropGroup, bimPropRow, bimPropText } from '../properties/palette.js';
import { SHEET_SCALES } from './sheets.js';
import { bimBrdEditing } from './board-figures.js';
import {
  bimBobBlend, bimBobBlends, bimBobBox, bimBobFind, bimBobKind, bimBobLayer, bimBobMaskTypes
} from './board-objects.js';
import { bimBdsPres } from './board-design.js';
import { bimBmapFit, bimBmapSources } from './board-map.js';
import {
  A3D_BDE, bimBdeAddImage, bimBdeDo, bimBdeFigBox, bimBdeName, bimBdeOwnsProps, bimBdeSel, bimBdeSet,
  bimBdeWork
} from './board-design-edit.js';
import { bimBdeArrange, bimBdeLaySet } from './board-design-tools.js';
import { bimLvAct, bimLvOverride, bimLvPropsHtml, bimLvSetDp, bimLvSetText } from './live-edit.js';


  /* ================= __acad3dV174a: a board's objects in the Layers tab and the Properties panel =================
     No panel of their own (the owner, 2026-11-08): a board's objects are listed in the Layers tab under the layer
     each is on, and the selected ones are shown in the Properties panel, as the model's objects are. Their Layer is
     chosen there, and their Transparency and Blend are ByLayer unless set (R2). */
  /* the board's objects by layer, once for a render of the Layers tab: {W, by: {layer id: [objects]}}, or null when no
     board is being drawn on */
  function bimBdeLyIndex(){
    var W,by={};
    if(!bimBrdEditing())return null;
    W=bimBdeWork();if(!W)return null;
    W.objs.forEach(function(n){var ly=bimBobLayer(n);if(ly)(by[ly.id]||(by[ly.id]=[])).push(n);});
    return {W:W,by:by};
  }
  /* the rows of a layer's board objects, under its row in the Layers tab, while a board is drawn on */
  function bimBdeLyRows(lyId,depth,f,X){
    var W,h='';
    if(!X||!X.by[lyId])return '';
    W=X.W;
    X.by[lyId].forEach(function(n){
      var nm,sel;
      nm=bimBdeName(n,W);
      if(f&&String(nm).toLowerCase().indexOf(f)<0)return;
      sel=A3D_BDE.sel.indexOf(n.id)>=0;
      h+='<div class="a3d-lyobj a3d-lybo'+(sel?' sel':'')+'" data-lybo="'+bimEsc(n.id)+'" style="padding-left:'+(22+depth*14)+'px" title="'+bimEsc(nm)+' -- on the board">'+
        '<span class="a3d-lydot" style="background:'+bimEsc(n.fill&&n.fill!=='none'?n.fill:(n.stroke&&n.stroke!=='none'?n.stroke:(n.col||'#7f9db8')))+'"></span>'+
        '<span class="a3d-lynm">'+bimEsc(nm)+'</span><span class="a3d-lyty">'+(n.mask?'mask':'board '+bimEsc((bimBobKind(n.t)||['',n.t])[1].toLowerCase()))+'</span></div>';
    });
    return h;
  }
  function bimBdeLyCount(lyId,X){return X&&X.by[lyId]?X.by[lyId].length:0;}
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
      if(n.t==='border')g+=bimBdeNum('Line (mm)','sw',n.sw,0.05,0.1,5);   /* __acad3dV174c */
      g+=bimBdeMapProps(n,W);   /* __acad3dV174d */
      if(n.t==='tblock')g+=bimPropRow('Number','<input type="text" data-bdf="num" maxlength="40" value="'+bimEsc(n.num||'')+'">')+
        bimPropRow('Date of issue','<input type="date" data-bdf="dt" value="'+bimEsc(n.dt||'')+'">')+bimPropRow('Style','<select data-bdf="st">'+bimBdeOpt('iso','ISO 7200, at the bottom right',n.st)+bimBdeOpt('us','A title strip (US practice)',n.st)+'</select>')+
        '<div class="a3d-pnote">Its other fields come from the project (Project, Client, Drawn by, Checked by) and the board (its name, its place in the set).</div>';
      if(n.t==='poly')g+=bimBdeNum('Sides','n',n.n,1,3,60);
      if(n.t==='star')g+=bimBdeNum('Points','n',n.n,1,3,60)+bimBdeNum('Inner (%)','ri',n.ri*100,1,5,95);
      if(n.t==='line')g+=bimBdeChk('Arrow at its start','a0',n.a0)+bimBdeChk('Arrow at its end','a1',n.a1);
      if(n.t==='text'){
        g+=(n.bind&&n.bind.k==='num'?'':bimPropRow('Text','<textarea data-bdf="s" rows="3" maxlength="4000">'+bimEsc(n.s)+'</textarea>'))+bimBdeNum('Size (pt)','fs',n.fs,1,4,400)+bimBdeCol('Colour','col',n.col,false)+
          bimPropRow('Align','<select data-bdf="al">'+bimBdeOpt('left','Left',n.al)+bimBdeOpt('center','Centre',n.al)+bimBdeOpt('right','Right',n.al)+'</select>')+
          bimPropRow('Box','<select data-bdf="fit">'+bimBdeOpt('auto-w','Auto width',n.fit)+bimBdeOpt('auto-h','Auto height',n.fit)+bimBdeOpt('fixed','Fixed size',n.fit)+'</select>')+
          bimBdeChk('Bold','fw',n.fw===700);
      }
      if(n.t==='image')g+=bimPropRow('Fit','<select data-bdf="fit">'+bimBdeOpt('fill','Fill',n.fit)+bimBdeOpt('fit','Fit',n.fit)+bimBdeOpt('tile','Tile',n.fit)+'</select>')+
        bimPropRow('Image',bimBdeBtn('swapimg','Another image…'));
      if(g)h+=bimPropGroup('Other',g);
      h+=bimLvPropsHtml(n,W);   /* __acad3dV175a: a text's fields, its override, Reset and Unlink */
    }
    /* __acad3dV174b: align, distribute and tidy the selection; one object aligns to the page */
    h+=bimPropGroup('Arrange','<div class="a3d-bdeacts" role="group" aria-label="Align">'+bimBdeBtn('al-left','Left','Align left edges')+bimBdeBtn('al-hcenter','Centre','Align centres across')+
      bimBdeBtn('al-right','Right','Align right edges')+bimBdeBtn('al-top','Top','Align top edges')+bimBdeBtn('al-vcenter','Middle','Align middles')+bimBdeBtn('al-bottom','Bottom','Align bottom edges')+'</div>'+
      (S.length>=2?'<div class="a3d-bdeacts" role="group" aria-label="Distribute">'+(S.length>=3?bimBdeBtn('dist-x','Distribute across','Equal gaps between the outermost two')+bimBdeBtn('dist-y','Distribute down','Equal gaps between the outermost two'):'')+
        bimBdeBtn('tidy-x','Tidy across','The most common gap between all')+bimBdeBtn('tidy-y','Tidy down','The most common gap between all')+'</div>':'')+
      '<div class="a3d-pnote">'+(S.length===1?'One object aligns to the page.':'The selection aligns to its own bounds.')+' Dragging, an edge catches others\' edges, centres and equal gaps (Snap, F3).</div>');
    h+=bimBdeLayHtml(W,S,lyId);
    h+=bimPropGroup('Draw order','<div class="a3d-bdeacts">'+bimBdeBtn('front','To front','Ctrl+Shift+]: within its layer')+bimBdeBtn('forward','Forward','Ctrl+]')+
      bimBdeBtn('backward','Backward','Ctrl+[')+bimBdeBtn('back','To back','Ctrl+Shift+[')+bimBdeBtn('dup','Duplicate','Ctrl+D')+bimBdeBtn('del','Delete','Delete',true)+'</div>'+
      '<div class="a3d-pnote">The layers set what is drawn over what: a layer higher in the Layers list is drawn over those below.</div>');
    return h;
  }
  /* __acad3dV174b: the stack of the selection's layer on this board (R4: a sub-layer is the group), and the object's
     place in it */
  function bimBdeLayHtml(W,S,lyId){
    var ly=bimLayerById(lyId),L=W.lay[lyId],g,n=bimBobFind(W.objs,S[0]).n,al;
    if(!ly)return '';
    g=bimPropRow('Stack','<select data-bdl="dir">'+bimBdeOpt('','None: placed freely',L?L.dir:'')+bimBdeOpt('row','A row',L?L.dir:'')+bimBdeOpt('column','A column',L?L.dir:'')+bimBdeOpt('wrap','Rows that wrap',L?L.dir:'')+'</select>');
    if(L){
      al=function(name,cur){return '<select data-bdl="'+name+'">'+bimBdeOpt('start','Start',cur)+bimBdeOpt('center','Centre',cur)+bimBdeOpt('end','End',cur)+'</select>';};
      g+=bimPropRow('Gap (mm)','<input type="number" data-bdl="gap" step="1" value="'+(L.gap==='auto'?'':L.gap)+'" placeholder="Auto"'+(L.gap==='auto'?' disabled':'')+'> <label class="a3d-bdechk"><input type="checkbox" data-bdl="auto"'+(L.gap==='auto'?' checked':'')+'> Auto</label>')+
        bimPropRow('Padding (mm)','<input type="number" data-bdl="pad" min="0" step="1" value="'+L.pad+'">')+
        bimPropRow('Along',al('am',L.am))+bimPropRow('Across',al('ac',L.ac))+
        bimPropRow('Width','<select data-bdl="sw">'+bimBdeOpt('hug','Hug its objects',L.sw)+bimBdeOpt('fixed','Fixed',L.sw)+'</select>'+(L.sw==='fixed'?' <input type="number" data-bdl="w" min="1" step="1" value="'+L.w+'" aria-label="Width in mm">':''))+
        bimPropRow('Height','<select data-bdl="sh">'+bimBdeOpt('hug','Hug its objects',L.sh)+bimBdeOpt('fixed','Fixed',L.sh)+'</select>'+(L.sh==='fixed'?' <input type="number" data-bdl="h" min="1" step="1" value="'+L.h+'" aria-label="Height in mm">':''))+
        bimPropRow('Corner X (mm)','<input type="number" data-bdl="x" step="1" value="'+Math.round(L.x*100)/100+'">')+bimPropRow('Corner Y (mm)','<input type="number" data-bdl="y" step="1" value="'+Math.round(L.y*100)/100+'">');
      if(S.length===1)g+=bimPropRow('This object','<select data-bdf="lsize">'+bimBdeOpt('fixed','Fixed size',n.la?'':(n.lw==='fill'&&n.lh==='fill'?'fill':n.lw==='fill'?'fillw':n.lh==='fill'?'fillh':'fixed'))+
        (n.t!=='fig'&&n.t!=='line'?bimBdeOpt('fillw','Fill the width',n.lw==='fill'&&n.lh!=='fill'?'fillw':'')+bimBdeOpt('fillh','Fill the height',n.lh==='fill'&&n.lw!=='fill'?'fillh':'')+bimBdeOpt('fill','Fill both',n.lw==='fill'&&n.lh==='fill'?'fill':''):'')+
        bimBdeOpt('abs','Out of the stack',n.la?'abs':'')+'</select>');
      g+='<div class="a3d-pnote">The objects of '+bimEsc(ly.name)+' on this board, in their Draw order; drag one to another place in the stack. On a phone a row is shown as a column.</div>';
    }
    return bimPropGroup('Stack: layer '+ly.name,g);
  }
  /* __acad3dV174d: a map frame's view, scale and pan; the surround's frame and its own settings */
  function bimBdeMapProps(n,W){
    var g='',frames;
    if(n.t==='map'){
      g+=bimPropRow('View','<select data-bdf="src">'+bimBmapSources().map(function(s){var v=s.kind+':'+s.refId;return bimBdeOpt(v,s.label,n.src);}).join('')+'</select>');
      g+=bimPropRow('Scale','<select data-bdf="den">'+SHEET_SCALES.map(function(s){return bimBdeOpt(s.denom,s.label,n.den);}).join('')+
        (SHEET_SCALES.some(function(s){return s.denom===n.den;})?'':bimBdeOpt(n.den,'1:'+n.den,n.den))+'</select> '+bimBdeBtn('mapfit','Fit','The scale that shows the view whole'));
      g+=bimBdeNum('Pan across (m)','px',n.px,1)+bimBdeNum('Pan up (m)','py',n.py,1);
      g+='<div class="a3d-pnote">The site\'s shown data layers and the basemap are drawn in the frame, on screen and on paper; the basemap\'s credit is printed in its corner.</div>';
    }
    if(n.t==='legend'||n.t==='north'||n.t==='sbar'){
      frames=W.objs.filter(function(q){return q.t==='map';});
      g+=bimPropRow('Map frame','<select data-bdf="fr">'+frames.map(function(q){return bimBdeOpt(q.id,bimBdeName(q,W)+' ('+q.id+')',n.fr);}).join('')+'</select>');
    }
    if(n.t==='legend')g+=bimPropRow('Title','<input type="text" data-bdf="ttl" maxlength="80" value="'+bimEsc(n.ttl||'')+'">')+
      '<div class="a3d-pnote">It follows the data and result layers shown, in the Layers tab\'s order, with their sources\' credits; with none shown it is left off the page.</div>';
    if(n.t==='north')g+=bimPropRow('Points to','<select data-bdf="nk">'+bimBdeOpt('true','True north (the site\'s)',n.nk)+bimBdeOpt('plan','Plan north',n.nk)+'</select>')+
      bimBdeNum('Offset (degrees, clockwise)','off',n.off,0.5,-360,360)+'<div class="a3d-pnote">True north is the site\'s, '+bimTrueNorthDeg()+' degrees from plan north. For magnetic north, type the declination as the offset.</div>';
    if(n.t==='sbar')g+=bimPropRow('Units','<select data-bdf="un">'+bimBdeOpt('m','Metres and kilometres',n.un)+bimBdeOpt('ft','Feet and miles',n.un)+'</select>');
    return g;
  }
  /* once, on the panel's body: its board fields and buttons */
  function bimBdePropsWire(body){
    if(!body||body.getAttribute('data-bdewired'))return;
    body.setAttribute('data-bdewired','1');
    body.addEventListener('click',function(ev){
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-bdact]'):null,v,r;
      if(!a||!bimBdeOwnsProps())return;
      v=a.getAttribute('data-bdact');
      if(v==='swapimg'){if(A3D_BDE.sel.length===1)bimBdeAddImage(A3D_BDE.sel[0]);}
      else if(/^(al|dist|tidy)-/.test(v))bimBdeArrange(v);   /* __acad3dV174b */
      else if(/^lv-/.test(v)){r=a.getBoundingClientRect();bimLvAct(v,r.left,r.bottom+4);}   /* __acad3dV175a */
      else if(v==='mapfit'){var Wf=bimBdeWork(),q=Wf&&bimBobFind(Wf.objs,A3D_BDE.sel[0]);if(q&&q.n.t==='map')bimBdeSet(null,bimBmapFit(q.n));}   /* __acad3dV174d */
      else bimBdeDo(v);
    });
    body.addEventListener('change',function(ev){
      var t=ev.target,f=t&&t.getAttribute&&t.getAttribute('data-bdf'),o={},v,lf=t&&t.getAttribute&&t.getAttribute('data-bdl'),W,ly;
      if(lf&&bimBdeOwnsProps()){   /* __acad3dV174b: the layer's stack on this board */
        W=bimBdeWork();ly=W&&bimBobLayer(bimBobFind(W.objs,A3D_BDE.sel[0])?bimBobFind(W.objs,A3D_BDE.sel[0]).n:{});
        if(!ly)return;
        if(lf==='dir')o.dir=t.value||null;
        else if(lf==='auto')o.gap=t.checked?'auto':5;
        else if(lf==='am'||lf==='ac'||lf==='sw'||lf==='sh')o[lf]=t.value;
        else{v=parseFloat(t.value);if(!isFinite(v))return;o[lf]=v;}
        bimBdeLaySet(ly.id,o);return;
      }
      if(f==='lsize'&&bimBdeOwnsProps()){v=t.value;bimBdeSet(null,{lw:v==='fillw'||v==='fill'?'fill':null,lh:v==='fillh'||v==='fill'?'fill':null,la:v==='abs'?true:null});return;}
      if(!f||!bimBdeOwnsProps())return;
      if(f==='ov.s'){bimLvOverride(t.value);return;}   /* __acad3dV175a: words typed over a live text */
      if(f==='lv.dp'){bimLvSetDp(t.value);return;}
      if(f==='s'&&bimLvSetText(t.value))return;   /* a text's words, and the fields in them */
      if(/:on$/.test(f)){f=f.slice(0,-3);o[f]=t.checked?((t.closest('.a3d-prow')||t.parentNode).querySelector('input[type=color]')||{}).value||'#000000':'none';}
      else if(f==='tr'){v=t.value.trim();if(v===''){o.tr=null;}else{v=+v;if(!isFinite(v))return;o.tr=Math.round(Math.max(0,Math.min(90,v)));}}
      else if(f==='bm'||f==='mask')o[f]=t.value||null;
      else if(f==='layer'){if(!t.value||!bimLayerById(t.value))return;o.layer=t.value;}
      else if(f==='fop'||f==='ri'){v=parseFloat(t.value);if(!isFinite(v))return;o[f]=Math.max(0,Math.min(1,v/100));}
      else if(f==='nm')o.nm=t.value.replace(/\s+/g,' ').trim()||null;
      else if(f==='al'||f==='fit'||f==='fill'||f==='stroke'||f==='col'||f==='s'||f==='st'||f==='src'||f==='fr'||f==='ttl'||f==='nk'||f==='un'||f==='num')o[f]=t.value;
      else if(f==='dt'){if(!/^\d{4}-\d{2}-\d{2}$/.test(t.value))return;o.dt=t.value;}
      else if(f==='a0'||f==='a1')o[f]=t.checked?true:null;
      else if(f==='fw')o.fw=t.checked?700:400;
      else{v=parseFloat(t.value);if(!isFinite(v))return;o[f]=v;}
      bimBdeSet(null,o);
    });
  }
export { bimBdeBtn, bimBdeLyCount, bimBdeLyIndex, bimBdeLyRows, bimBdeOpt, bimBdePropsHtml, bimBdePropsWire };
