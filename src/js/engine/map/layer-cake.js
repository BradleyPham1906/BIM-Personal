import { A3D } from '../core/state.js';
import { A3D_PLOT, bimLayerById, bimLayerShown } from '../layers/layer-rules.js';
import { refreshLayers } from '../layers/analysis-data-rows.js';
import { bimDgDiags, bimIsDiag } from '../standards/registry.js';
import { bimDgDrawText } from '../site-analysis/model-layers.js';
import { refreshProps } from '../site-analysis/panel.js';
import { toScreen } from '../io/import-entry.js';
import { bimCtxSettings } from './site-context.js';
import { bimDataList } from './data-layers.js';
import { paint } from './terrain-3d.js';
import { setView } from '../editing/modify-toolbox.js';
import { bimShadowGround } from '../site/shadows.js';
import { bimCameraIsPlan } from '../views/saved-views.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';


  /* ================= __acad3dV173d: McHarg's layer cake =================
     McHarg's method (Design with Nature, 1969, as quoted in the research): each factor its own
     transparent map, stacked over the base. The owner's D13: the site analyses and the data layers
     lifted over the map, each to a height of its own, in an oblique view, its name beside it; the
     result layers stay in plan (they draw only there). The lift is applied where every point is
     placed (bimDgW for an analysis, drawDataLayers and bimDataPick for a data layer), so drawing and
     picking agree. The cake is a way of looking, like a view: neither saved nor undone. */
  var A3D_CAKE={on:false,memo:null};
  /* the tiers, bottom up, in the order paint draws them so a higher tier is drawn over a lower one:
     the site analysis layers first (drawDiagrams' under pass comes before the data layers), in the
     order drawDiagrams meets their elements, each counted only when one of its elements is shown by
     the drawer's own rule (bimLayerShown, which honours the parent group); then the shown data
     layers in their drawing order. Each {kind, id, name, lift} */
  function bimCakeTiers(){
    var out=[],L=bimDataList(),i,seen={},gap=bimCakeGap(),ly;
    if(!A3D_CAKE.on)return out;
    bimDgDiags().forEach(function(o){
      if(!o.layer||seen[o.layer]||!bimLayerShown(o))return;
      seen[o.layer]=1;ly=bimLayerById(o.layer);
      out.push({kind:'analysis',id:o.layer,name:String(ly&&ly.name||o.layer).replace(/^Site analysis - /,'')});
    });
    for(i=0;i<L.length;i++)if(L[i].visible)out.push({kind:'data',id:L[i].id,name:L[i].name});
    for(i=0;i<out.length;i++)out[i].lift=(i+1)*gap;
    return out;
  }
  /* the gap between tiers: a fifth of the site context's radius, 10 to 200 m */
  function bimCakeGap(){return Math.max(10,Math.min(200,bimCtxSettings().radius/5));}
  /* every point of an analysis asks for its lift: the tiers are read once a frame */
  function bimCakeLift(kind,id){
    if(!A3D_CAKE.on)return 0;
    var m=A3D_CAKE.memo,T,i;
    if(!m||m.frame!==A3D.frames){
      T=bimCakeTiers();m={frame:A3D.frames,lift:{}};
      for(i=0;i<T.length;i++)m.lift[T[i].kind+':'+T[i].id]=T[i].lift;
      A3D_CAKE.memo=m;
    }
    return m.lift.hasOwnProperty(kind+':'+id)?m.lift[kind+':'+id]:0;
  }
  /* an analysis element's lift: its layer's tier */
  function bimCakeLiftObj(o){return A3D_CAKE.on&&o&&o.layer?bimCakeLift('analysis',o.layer):0;}
  /* on or off; on, a plan turns to the oblique view, where the heights can be seen */
  function bimCakeSet(on){
    A3D_CAKE.on=on===undefined?!A3D_CAKE.on:!!on;
    A3D_CAKE.memo=null;
    var n=bimCakeTiers().length,ids=[],i,o;
    /* an analysis is for looking while it is lifted: let go of any that is selected */
    if(A3D_CAKE.on){
      for(i=0;i<(A3D.selSet||[]).length;i++){o=objById(A3D.selSet[i]);if(!bimIsDiag(o))ids.push(A3D.selSet[i]);}
      if(ids.length!==(A3D.selSet||[]).length){A3D.selSet=ids;if(A3D.sel&&bimIsDiag(objById(A3D.sel)))A3D.sel=ids[0]||null;refreshTree();refreshProps();}
    }
    if(A3D_CAKE.on&&bimCameraIsPlan())setView('iso');
    refreshLayers();paint();
    a3dToast(!A3D_CAKE.on?'Layer cake: off':n?'Layer cake: '+n+' layer'+(n===1?'':'s')+' lifted over the map, '+Math.round(bimCakeGap())+' m apart; the analyses are for looking until it is off':
      'Layer cake: no shown site analysis or data layer to lift');
    return A3D_CAKE.on;
  }
  /* each tier's frame and name, at the site context's square: drawn after the layers, never on paper */
  function drawLayerCake(ctx,V,W,H){
    A3D.lastCakeTiers=0;
    if(!A3D_CAKE.on||A3D.sheetCapture||A3D_PLOT.on)return;
    var T=bimCakeTiers(),r=bimCtxSettings().radius,y0=bimShadowGround(),i,k,c,p,pts;
    if(!T.length)return;
    ctx.save();
    try{
      for(i=0;i<T.length;i++){
        c=[[-r,-r],[r,-r],[r,r],[-r,r]];pts=[];
        for(k=0;k<4;k++){p=toScreen([c[k][0],y0+T[i].lift,c[k][1]],V,W,H);if(!p||!isFinite(p[0])||!isFinite(p[1]))break;pts.push(p);}
        if(pts.length<4)continue;
        ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);for(k=1;k<4;k++)ctx.lineTo(pts[k][0],pts[k][1]);ctx.closePath();
        ctx.globalAlpha=0.06;ctx.fillStyle='#e8edf2';ctx.fill();
        ctx.globalAlpha=0.45;ctx.strokeStyle='#e8edf2';ctx.lineWidth=1;ctx.setLineDash([4,4]);ctx.stroke();ctx.setLineDash([]);
        ctx.globalAlpha=1;ctx.textAlign='right';ctx.textBaseline='middle';
        p=pts[0][0]<pts[3][0]?pts[0]:pts[3];
        bimDgDrawText(ctx,T[i].name,p[0]-8,p[1],'#e8edf2',12,false);
        A3D.lastCakeTiers++;
      }
    }catch(e){
      console.warn('[BIM] layer cake',e);
      if(!A3D.cakeWarned){A3D.cakeWarned=true;a3dToast('The layer cake could not be drawn');}
    }
    ctx.restore();
  }
  /* the toggle in the Layers header */
  function bimCakeBtnHtml(){
    return '<button type="button" class="a3d-lycake'+(A3D_CAKE.on?' on':'')+'" data-lycake="1" aria-pressed="'+(A3D_CAKE.on?'true':'false')+
      '" title="Layer cake: lift the site analyses and data layers over the map, each to its own height">Layer cake</button>';
  }
export { A3D_CAKE, bimCakeBtnHtml, bimCakeLift, bimCakeLiftObj, bimCakeSet, bimCakeTiers, drawLayerCake };
