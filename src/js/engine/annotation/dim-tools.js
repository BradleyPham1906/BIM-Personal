import { A3D, el } from '../core/state.js';
import { bimEnterDraftingMode, pushUndo } from '../drawing/plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimDimKind } from './dimensions.js';
import { bimLayerAlpha } from '../layers/layer-rules.js';
import { bimEsc } from '../layers/layer-manager.js';
import { bimUnitDef } from '../properties/palette.js';
import { toScreen } from '../io/import-entry.js';
import { paint } from '../map/terrain-3d.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV258: AutoCAD's dimension tools and style (D4) =================
     DIMBASELINE (DBA) and DIMCONTINUE (DCO) from a linear dimension, DIMORDINATE (DOR), and DIMSTYLE (D): one
     current style every dimension is drawn with, as AutoCAD's Standard style is, saved with the project
     (A3D.dimStyle). The style's precision and the project's display units give the label, which before this was
     always metres to two places.
     Geometry is pure (bimDimBaselineGeom, bimDimContinueGeom, bimDimOrdinateGeom, bimDimLabelText), tested without
     a canvas. A dimension measures along its reference's direction, as AutoCAD's baseline and continued
     dimensions take their first dimension's. */
  var BIM_DIMSTYLE_DEFAULT={textHeight:0,precision:2,suffix:true,arrow:'tick',arrowSize:0,extOffset:0,extBeyond:0,baselineSpacing:0.6};
  function bimDimStyleValid(s){
    var d=JSON.parse(JSON.stringify(BIM_DIMSTYLE_DEFAULT)),k;
    if(!s||typeof s!=='object')return d;
    for(k in d)if(d.hasOwnProperty(k)&&s[k]!==undefined){
      if(typeof d[k]==='number'){var v=+s[k];if(isFinite(v)&&v>=0)d[k]=v;}
      else if(typeof d[k]==='boolean')d[k]=!!s[k];
      else if(k==='arrow'&&/^(tick|arrow|dot)$/.test(s[k]))d[k]=s[k];
    }
    d.precision=Math.min(8,Math.round(d.precision));
    return d;
  }
  function bimDimStyle(){if(!A3D.dimStyle)A3D.dimStyle=bimDimStyleValid(null);return A3D.dimStyle;}
  /* A length as a dimension's text: the project's unit, the style's precision, the unit's name when asked. */
  function bimDimLabelText(len,st){
    st=st||bimDimStyle();
    var U=bimUnitDef(),v=(len*(U.scale||1)).toFixed(st.precision);
    return v+(st.suffix?' '+U.label:'');
  }
  /* The linear dimension a baseline or continued one follows: the selected one, else the last drawn. */
  function bimDimRef(){
    var o=objById(A3D.sel),i;
    if(o&&o.t==='dim'&&bimDimKind(o)==='linear')return o;
    for(i=A3D.objs.length-1;i>=0;i--)if(A3D.objs[i].t==='dim'&&bimDimKind(A3D.objs[i])==='linear')return A3D.objs[i];
    return null;
  }
  function bimDimFrame(ref){
    var dx=ref.d2[0]-ref.d1[0],dz=ref.d2[1]-ref.d1[1],L=Math.sqrt(dx*dx+dz*dz);
    if(L<1e-12){dx=ref.p2[0]-ref.p1[0];dz=ref.p2[1]-ref.p1[1];L=Math.sqrt(dx*dx+dz*dz)||1;}
    var u=[dx/L,dz/L],n=[ref.d1[0]-ref.p1[0],ref.d1[1]-ref.p1[1]],nl=Math.sqrt(n[0]*n[0]+n[1]*n[1]);
    /* the side the dimension line sits on; a dimension drawn on its points takes the left of its direction */
    var side=nl>1e-12?[n[0]/nl,n[1]/nl]:[-u[1],u[0]];
    return {u:u,n:side,off:nl};
  }
  /* DIMBASELINE: from the reference's first point to p, one spacing further out than the k-th before it. */
  function bimDimBaselineGeom(ref,p,k,spacing){
    var F=bimDimFrame(ref),a=ref.p1,t=(p[0]-a[0])*F.u[0]+(p[1]-a[1])*F.u[1],off=F.off+k*spacing;
    var d1=[a[0]+F.n[0]*off,a[1]+F.n[1]*off],d2=[d1[0]+F.u[0]*t,d1[1]+F.u[1]*t];
    return {p1:[a[0],a[1]],p2:[p[0],p[1]],d1:d1,d2:d2,length:Math.abs(t)};
  }
  /* DIMCONTINUE: from the last dimension's second point to p, on the same dimension line. */
  function bimDimContinueGeom(prev,p){
    var F=bimDimFrame(prev),t=(p[0]-prev.d2[0])*F.u[0]+(p[1]-prev.d2[1])*F.u[1];
    var d2=[prev.d2[0]+F.u[0]*t,prev.d2[1]+F.u[1]*t];
    return {p1:[prev.p2[0],prev.p2[1]],p2:[p[0],p[1]],d1:[prev.d2[0],prev.d2[1]],d2:d2,length:Math.abs(t)};
  }
  /* DIMORDINATE: a feature's X or Y from the origin, as the status bar reads them. A leader that runs more across
     than up the plan gives the Y datum, more up than across the X datum, as AutoCAD decides it. */
  function bimDimOrdinateGeom(f,e){
    var axis=Math.abs(e[0]-f[0])>=Math.abs(e[1]-f[1])?'y':'x';
    return {axis:axis,value:axis==='x'?f[0]:f[1],p1:[f[0],f[1]],d1:[e[0],e[1]]};
  }
  function bimAddDimObj(g,extra){
    A3D.counts.dim=(A3D.counts.dim||0)+1;
    var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'dim',name:'Dim_'+A3D.counts.dim,col:'#dfe4ea',pos:[0,0,0],
      y:bimGetActiveLevel().elev,levelId:A3D.activeLevel,layer:A3D.activeLayer,viewId:A3D.activeViewId},k;
    for(k in g)if(g.hasOwnProperty(k))o[k]=g[k];
    for(k in extra||{})if(extra.hasOwnProperty(k))o[k]=extra[k];
    A3D.objs.push(o);
    return o;
  }
  function startDimChainTool(kind){
    closeDlg();
    var ref=null;
    if(kind!=='ord'){
      ref=bimDimRef();
      if(!ref){a3dToast((kind==='base'?'DIMBASELINE':'DIMCONTINUE')+': draw or select a linear dimension first');return;}
    }
    bimEnterDraftingMode();
    A3D.sk={tool:'dim'+kind,pts:[],y:bimGetActiveLevel().elev,on:null,dimRef:ref?ref.id:null,dimPrev:ref?ref.id:null,dimK:1};
    a3dToast(kind==='ord'?'DIMORDINATE: specify the feature point':'Specify a second extension line origin (Enter or Esc to finish)');
    paint();
  }
  function bimIsDimChainTool(sk){return !!sk&&(sk.tool==='dimbase'||sk.tool==='dimcont'||sk.tool==='dimord');}
  function bimDimChainPoint(sk,p){
    var o;
    if(sk.tool==='dimord'){
      sk.pts.push([p[0],p[1]]);
      if(sk.pts.length<2){a3dToast('DIMORDINATE: specify the leader endpoint');paint();return;}
      pushUndo();
      o=bimAddDimObj(bimDimOrdinateGeom(sk.pts[0],sk.pts[1]),{dimKind:'ordinate'});
      sk.pts=[];
      A3D.sel=o.id;A3D.selSet=[o.id];
      refreshTree();paint();saveSoon();
      a3dToast('Ordinate dimension: '+o.axis.toUpperCase()+' = '+bimDimLabelText(o.value)+'; next feature, or Esc');
      return;
    }
    var ref=objById(sk.dimRef),prev=objById(sk.dimPrev);
    if(!ref||!prev){A3D.sk=null;a3dToast('The dimension it follows was deleted');paint();return;}
    var g=sk.tool==='dimbase'?bimDimBaselineGeom(ref,p,sk.dimK,bimDimStyle().baselineSpacing):bimDimContinueGeom(prev,p);
    if(!(g.length>1e-9)){a3dToast('That point is level with the last one: no length');return;}
    pushUndo();
    o=bimAddDimObj(g);
    sk.dimPrev=o.id;sk.dimK++;
    refreshTree();paint();saveSoon();
    a3dToast(o.name+': '+bimDimLabelText(g.length)+'; next point, or Enter to finish');
  }
  /* ---------- DIMSTYLE ---------- */
  function openDimStyleDlg(){
    closeDlg();
    var s=bimDimStyle(),U=bimUnitDef(),d=document.createElement('div');
    d.className='a3d-dlg';
    function num(k,label,step){return '<div class="a3d-dlgrow"><label>'+label+'</label><input type="number" min="0" step="'+(step||'any')+'" data-a3dds="'+k+'" value="'+s[k]+'"></div>';}
    d.innerHTML='<div class="a3d-dlghd">Dimension style: Standard</div><div class="a3d-dlgbody">'+
      num('precision','Decimal places',1)+
      '<div class="a3d-dlgrow"><label><input type="checkbox" data-a3dds="suffix"'+(s.suffix?' checked':'')+'> Show the unit ('+bimEsc(U.label)+')</label></div>'+
      num('textHeight','Text height on the plan, m (0: screen size)')+
      '<div class="a3d-dlgrow"><label>Arrowheads</label><select data-a3dds="arrow">'+
        [['tick','Architectural tick'],['arrow','Closed filled'],['dot','Dot']].map(function(a){return '<option value="'+a[0]+'"'+(s.arrow===a[0]?' selected':'')+'>'+a[1]+'</option>';}).join('')+'</select></div>'+
      num('arrowSize','Arrow size on the plan, m (0: screen size)')+
      num('extOffset','Offset from origin, m')+
      num('extBeyond','Extend beyond dimension line, m')+
      num('baselineSpacing','Baseline spacing, m')+
      '<div class="a3d-propnote">Every dimension is drawn with this style; a change redraws them all, as AutoCAD\'s Standard style does.</div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var n={},f=d.querySelectorAll('[data-a3dds]'),i;
      for(i=0;i<f.length;i++){var k=f[i].getAttribute('data-a3dds');n[k]=f[i].type==='checkbox'?f[i].checked:f[i].value;}
      pushUndo();
      A3D.dimStyle=bimDimStyleValid(n);
      closeDlg();paint();saveSoon();
      a3dToast('Dimension style changed: every dimension redrawn');
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
  }
  /* ---------- drawing a linear dimension with the style ---------- */
  function bimDrawLinearDim(ctx,o,sel,V,W,H){
    var st=bimDimStyle(),ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0,y0=o.y+oy;
    function S(p){return toScreen([p[0]+ox,y0,p[1]+oz],V,W,H);}
    /* extension lines: from the origin plus the offset to the dimension line plus the extension, along their own way */
    function ext(p,d){
      var dx=d[0]-p[0],dz=d[1]-p[1],L=Math.sqrt(dx*dx+dz*dz);
      if(L<1e-12)return [S(p),S(d)];
      var ux=dx/L,uz=dz/L;
      return [S([p[0]+ux*Math.min(st.extOffset,L),p[1]+uz*Math.min(st.extOffset,L)]),S([d[0]+ux*st.extBeyond,d[1]+uz*st.extBeyond])];
    }
    var e1=ext(o.p1,o.d1),e2=ext(o.p2,o.d2),d1=S(o.d1),d2=S(o.d2);
    ctx.save();
    ctx.globalAlpha*=bimLayerAlpha(o);
    var col=sel?'#4ea1ff':(/^#[0-9a-fA-F]{6}$/.test(o.color||'')?o.color:'#b8c0ca');
    ctx.strokeStyle=col;ctx.fillStyle=col;
    ctx.lineWidth=sel?1.4:1;
    ctx.beginPath();ctx.moveTo(e1[0][0],e1[0][1]);ctx.lineTo(e1[1][0],e1[1][1]);ctx.stroke();
    ctx.beginPath();ctx.moveTo(e2[0][0],e2[0][1]);ctx.lineTo(e2[1][0],e2[1][1]);ctx.stroke();
    ctx.beginPath();ctx.moveTo(d1[0],d1[1]);ctx.lineTo(d2[0],d2[1]);ctx.stroke();
    var tdx=d2[0]-d1[0],tdy=d2[1]-d1[1],tlen=Math.sqrt(tdx*tdx+tdy*tdy)||1,tux=tdx/tlen,tuy=tdy/tlen;
    /* the arrow size: metres on the plan when the style gives one, else 4 px as before */
    var ppm=Math.sqrt(Math.pow(S([o.d1[0]+1,o.d1[1]])[0]-d1[0],2)+Math.pow(S([o.d1[0]+1,o.d1[1]])[1]-d1[1],2));
    var a=st.arrowSize>0?Math.max(1,st.arrowSize*ppm):4;
    function head(px,py,dir){
      if(st.arrow==='tick'){ctx.beginPath();ctx.moveTo(px-tuy*a-tux*a,py+tux*a-tuy*a);ctx.lineTo(px+tuy*a+tux*a,py-tux*a+tuy*a);ctx.stroke();}
      else if(st.arrow==='dot'){ctx.beginPath();ctx.arc(px,py,a*0.5,0,Math.PI*2);ctx.fill();}
      else{
        var bx=px+dir*tux*a*2.2,by=py+dir*tuy*a*2.2;
        ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(bx-tuy*a*0.6,by+tux*a*0.6);ctx.lineTo(bx+tuy*a*0.6,by-tux*a*0.6);ctx.closePath();ctx.fill();
      }
    }
    head(d1[0],d1[1],1);head(d2[0],d2[1],-1);
    var label=bimDimLabelText(o.length,st),mx=(d1[0]+d2[0])/2,my=(d1[1]+d2[1])/2;
    if(st.textHeight>0){
      /* drawing text along the dimension line, kept reading left to right, a fifth of its height above the line */
      var px=st.textHeight*ppm,ang=Math.atan2(tuy,tux);
      if(ang>Math.PI/2)ang-=Math.PI;else if(ang<-Math.PI/2)ang+=Math.PI;
      if(px>=1.5){
        ctx.translate(mx,my);ctx.rotate(ang);
        ctx.font=px.toFixed(2)+'px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='alphabetic';
        ctx.fillStyle=sel?'#9ec1ff':(/^#[0-9a-fA-F]{6}$/.test(o.color||'')?o.color:'#dfe4ea');
        ctx.fillText(label,0,-px*0.2);
      }
    }else{
      ctx.font='11px system-ui,sans-serif';
      var tw=ctx.measureText(label).width;
      ctx.fillStyle='rgba(20,22,26,0.82)';
      ctx.fillRect(mx-tw/2-4,my-16,tw+8,14);
      ctx.fillStyle=sel?'#9ec1ff':'#dfe4ea';
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(label,mx,my-9);
    }
    ctx.restore();
  }
  /* An ordinate dimension: a leader with a jog from the feature to the text, and the X or Y it reads. */
  function bimDrawOrdinateDim(ctx,o,sel,S){
    var f=S(o.p1),e=S(o.d1),label=o.axis.toUpperCase()+' '+bimDimLabelText(o.value);
    var mid=o.axis==='y'?[f[0]+(e[0]-f[0])*0.6,f[1]]:[f[0],f[1]+(e[1]-f[1])*0.6];
    ctx.beginPath();ctx.moveTo(f[0],f[1]);ctx.lineTo(mid[0],mid[1]);ctx.lineTo(e[0],e[1]);ctx.stroke();
    return {label:label,at:[e[0]+(o.axis==='y'?(e[0]>=f[0]?1:-1)*24:0),e[1]+(o.axis==='x'?(e[1]>=f[1]?1:-1)*10:0)]};
  }
export {
  bimDimChainPoint, bimDimLabelText, bimDimStyle, bimDimStyleValid, bimDrawLinearDim, bimDrawOrdinateDim,
  bimIsDimChainTool, openDimStyleDlg, startDimChainTool
};
