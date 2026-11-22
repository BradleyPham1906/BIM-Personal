import { A3D, el } from '../core/state.js';
import { bimEnterDraftingMode, bimObjOffset, pushUndo } from './plan-mode-sketch.js';
import { bimGetActiveLevel } from '../bim/levels-walls-floors.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { bimAwBgHex } from '../site-analysis/analysis-workspace.js';
import { toScreen } from '../io/import-entry.js';
import { paint } from '../map/terrain-3d.js';
import { bimBulgedArea, bimFlattenPoly, bimHasBulge } from './arc-storage.js';
import { bimAddHatch, bimHatchOutline, bimIsHatch } from './hatch.js';
import { bimCircleSketch } from './curve-walking.js';
import { saveSoon } from '../bim/region-regenerate.js';
import { bimObjectVisibleOnLevel } from '../views/saved-views.js';
import { refreshTree } from '../sheets/presentation-panel.js';
import { closeDlg } from '../ui/touch-input.js';
import { a3dToast, objById } from '../bim/csg-booleans.js';

  /* ================= __acad3dV265: hatch holes, DONUT and WIPEOUT =================
     A hatch may now have holes (o.holes: [{pts, bulges}]), filled even-odd, as AutoCAD fills a hatch with islands: a
     DXF or DWG hatch's inner boundaries become its holes (import-dxf.js), and DONUT is a solid hatch whose hole is
     its inner circle. WIPEOUT is a hatch with o.wipeout: it paints the background colour over the linework drawn
     before it (drawn after the plan's lines and before its dimensions and text, as AutoCAD keeps text over a
     wipeout), its frame shown only while selected. The geometry is pure (bimDonutRings, bimHatchHoleArea,
     bimPointInRing), tested without a canvas. */
  /* A ring's flattened points, for drawing and testing. */
  function bimHatchHoleRings(o){
    var out=[],i;
    for(i=0;o&&o.holes&&i<o.holes.length;i++){
      var h=o.holes[i];
      if(h&&h.pts&&h.pts.length>=2)out.push(bimFlattenPoly(h.pts,h.bulges||null,true));
    }
    return out;
  }
  function bimHatchHoleArea(o){
    var a=0,i;
    for(i=0;o&&o.holes&&i<o.holes.length;i++)a+=bimBulgedArea(o.holes[i].pts,o.holes[i].bulges||null,true);
    return a;
  }
  /* Is p inside the closed ring (even-odd)? */
  function bimPointInRing(p,ring){
    var inside=false,i,j;
    for(i=0,j=ring.length-1;i<ring.length;j=i++){
      var a=ring[i],b=ring[j];
      if(((a[1]>p[1])!==(b[1]>p[1]))&&(p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]))inside=!inside;
    }
    return inside;
  }
  /* DONUT: the outer circle, and the inner one as its hole when it has one (inner 0: a filled dot). */
  function bimDonutRings(c,inner,outer){
    var o=bimCircleSketch(c,outer/2);
    if(o.error)return null;
    var r={pts:o.pts,bulges:o.bulges,holes:[]};
    if(inner>1e-9&&inner<outer){var h=bimCircleSketch(c,inner/2);r.holes.push({pts:h.pts,bulges:h.bulges});}
    return r;
  }
  /* The background a wipeout paints: the plan's, or a sheet's white. */
  function bimWipeoutColor(){return A3D.sheetCapture?'#ffffff':bimAwBgHex();}
  /* The path of one ring, in screen space, added to the current path. */
  function bimRingPath(ctx,ring,o,V,W,H){
    var q=bimObjOffset(o),k,p;
    for(k=0;k<ring.length;k++){
      p=toScreen([ring[k][0]+q[0],(o.y||0)+q[1],ring[k][1]+q[2]],V,W,H);
      if(k)ctx.lineTo(p[0],p[1]);else ctx.moveTo(p[0],p[1]);
    }
    ctx.closePath();
  }
  function drawWipeouts(ctx,V,W,H){
    var i,o,ring;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!o.wipeout||!bimIsHatch(o)||!bimLayerShown(o)||!bimObjectVisibleOnLevel(o))continue;
      ring=bimHatchOutline(o);
      if(ring.length<3)continue;
      ctx.save();
      ctx.beginPath();bimRingPath(ctx,ring,o,V,W,H);
      ctx.fillStyle=bimWipeoutColor();ctx.fill();
      if(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0)){
        ctx.strokeStyle='#4ea1ff';ctx.lineWidth=1.4;ctx.setLineDash([6,4]);ctx.stroke();ctx.setLineDash([]);
      }
      ctx.restore();
    }
  }
  /* ---------- DONUT (DO) ---------- */
  var A3D_DONUT={inner:0.5,outer:1};
  function startDonutTool(){
    closeDlg();
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">Donut</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>Inside diameter, m (0: a filled dot)</label><input type="number" min="0" step="any" data-a3ddn="i" value="'+A3D_DONUT.inner+'"></div>'+
      '<div class="a3d-dlgrow"><label>Outside diameter, m</label><input type="number" min="0" step="any" data-a3ddn="o" value="'+A3D_DONUT.outer+'"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    function submit(){
      var a=parseFloat(d.querySelector('[data-a3ddn="i"]').value),b=parseFloat(d.querySelector('[data-a3ddn="o"]').value);
      if(!(b>0)||!(a>=0)||a>=b){d.querySelector('#a3d-dlgerr').textContent='The outside is more than zero and more than the inside';return;}
      A3D_DONUT.inner=a;A3D_DONUT.outer=b;
      closeDlg();bimEnterDraftingMode();
      A3D.sk={tool:'donut',pts:[],y:bimGetActiveLevel().elev,on:null};
      a3dToast('DONUT: specify the centre (Esc to finish)');
      paint();
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}ev.stopPropagation();});
  }
  function bimDonutPoint(sk,p){
    var r=bimDonutRings(p,A3D_DONUT.inner,A3D_DONUT.outer);
    if(!r)return null;
    pushUndo();
    var o=bimAddHatch(r.pts,r.bulges,sk.y,{pattern:'solid',patternColor:'#c8d2dc'});
    if(o){o.fill='#c8d2dc';o.name='Donut '+A3D.counts.hatch;if(r.holes.length)o.holes=r.holes;}
    refreshTree();paint();saveSoon();
    a3dToast('DONUT: next centre, or Esc');
    return o;
  }
  /* ---------- WIPEOUT ---------- */
  function startWipeoutTool(){
    var s=objById(A3D.sel);
    if(s&&s.t==='sketch'&&s.closed!==false&&s.pts&&(s.pts.length>2||bimHasBulge(s.bulges))){
      /* AutoCAD's Polyline option: a selected closed polyline becomes the frame */
      var q=bimObjOffset(s);
      pushUndo();
      var o=bimAddHatch(s.pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];}),s.bulges||null,(s.y||0)+q[1],{pattern:'none'});
      if(o){o.wipeout=true;o.name='Wipeout '+A3D.counts.hatch;o.layer=s.layer||o.layer;}
      refreshTree();paint();saveSoon();
      a3dToast('WIPEOUT made from the selected polyline');
      return o;
    }
    closeDlg();bimEnterDraftingMode();
    A3D.sk={tool:'wipeout',pts:[],y:bimGetActiveLevel().elev,on:null};
    a3dToast('WIPEOUT: specify the corners, then Enter (or select a closed polyline first)');
    paint();
    return null;
  }
  function bimWipeoutPoint(sk,p){
    sk.pts.push([p[0],p[1]]);
    a3dToast('WIPEOUT: next corner, or Enter to finish ('+sk.pts.length+' so far)');
    paint();
  }
  function bimWipeoutFinish(sk){
    A3D.sk=null;
    if(!sk||sk.pts.length<3){a3dToast('WIPEOUT: three or more corners');paint();return null;}
    pushUndo();
    var o=bimAddHatch(sk.pts,null,sk.y,{pattern:'none'});
    if(o){o.wipeout=true;o.name='Wipeout '+A3D.counts.hatch;}
    refreshTree();paint();saveSoon();
    a3dToast('WIPEOUT: the area is masked');
    return o;
  }
export {
  bimDonutPoint, bimHatchHoleRings, bimPointInRing, bimRingPath, bimWipeoutFinish, bimWipeoutPoint,
  drawWipeouts, startDonutTool, startWipeoutTool
};
