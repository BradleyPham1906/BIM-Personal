import { A3D_SNAP } from '../drawing/plan-mode-sketch.js';
import { bimClbE, bimClbRefresh } from '../site-analysis/climate-board.js';
import {
  BIM_BRD_G, BIM_BRD_P0, bimBrdBands, bimBrdFigHtml, bimBrdOverlaps, bimBrdPx, bimFigSrc
} from './board-figures.js';
import {
  bimBtrBlend, bimBtrBox, bimBtrFigBox, bimBtrIsBox, bimBtrPxMm, bimBtrRuns, bimBtrWalk
} from './board-tree.js';
import { A3D_BIMG, bimBimgMissing, bimBimgUrl } from './board-images.js';


  /* ================= __acad3dV174a: a designed board, drawn =================
     docs/research/research-presentation-boards.md, 5.1 (D1: HTML and SVG, as the boards are), 4.2 and 5.3 (D3, D5).
     The tree is drawn in its order, the first element at the back. The browser composites: opacity, mix-blend-mode
     with the W3C keywords, isolation. In CSS an opacity under 1, a blend mode, a mask or a clip-path each make a
     stacking context, and a stacking context isolates, so a group set to Pass through is drawn with no element of its
     own, its children straight onto what is beneath; a group or frame with a mode or an opacity is one isolated
     element. Paint order is the markup's order, never a z-index. The canvas is painted with the page's colour inside
     the isolated root, so a Multiply over an empty part of the board darkens the page, on screen and on paper.
     Masks: a mask masks the siblings above it (bimBtrRuns); vector by clip-path, alpha and luminance by mask-image
     (mask-mode), the mask's own shape drawn as an SVG image. */
  function bimBdsPx(mm){return bimBrdPx(mm*bimBtrPxMm());}
  function bimBdsComp(n,iso){
    var s='',B=bimBtrBlend(n.bm);
    if(n.op<1)s+='opacity:'+n.op+';';
    if(B&&B[2]&&B[2]!=='normal')s+='mix-blend-mode:'+B[2]+';';
    if(iso)s+='isolation:isolate;';
    return s;
  }
  /* a group or frame is drawn on its own when it has a mode other than Pass through, or an opacity (D3) */
  function bimBdsIsolated(n){return bimBtrIsBox(n)&&(n.bm!=='pass'||n.op<1);}
  function bimBdsPos(b,ox,oy){return 'left:'+bimBdsPx(b.x-ox)+'px;top:'+bimBdsPx(b.y-oy)+'px;width:'+bimBdsPx(b.w)+'px;height:'+bimBdsPx(b.h)+'px;';}
  function bimBdsAttr(n,cls,ctx){
    return ' class="'+cls+(n.lock?' lk':'')+'" data-bde="'+n.id+'"'+(ctx.edit?'':' aria-hidden="true"');
  }
  /* ---- the shapes, as SVG markup inside a box W x H px ---- */
  function bimBdsPts(n,W,H){
    var P=[],N=n.t==='star'?n.n*2:n.n,i,a,r;
    for(i=0;i<N;i++){
      a=-Math.PI/2+i*2*Math.PI/N;
      r=n.t==='star'&&i%2?n.ri:1;
      P.push([bimBrdPx(W/2+W/2*r*Math.cos(a)),bimBrdPx(H/2+H/2*r*Math.sin(a))]);
    }
    return P;
  }
  function bimBdsPaint(n){
    var s=' fill="'+(n.fill&&n.fill!=='none'?n.fill:'none')+'"';
    if(n.fill&&n.fill!=='none'&&n.fop<1)s+=' fill-opacity="'+n.fop+'"';
    if(n.stroke&&n.stroke!=='none'&&n.sw>0)s+=' stroke="'+n.stroke+'" stroke-width="'+bimBdsPx(n.sw)+'"';
    return s;
  }
  /* a line's arrowhead at (x1, y1), coming from (x0, y0) */
  function bimBdsArrow(x0,y0,x1,y1,sw,col){
    var L=Math.sqrt((x1-x0)*(x1-x0)+(y1-y0)*(y1-y0))||1,ux=(x1-x0)/L,uy=(y1-y0)/L,s=Math.max(8,sw*4),hw=s*0.45;
    var bx=x1-ux*s,by=y1-uy*s;
    return '<polygon fill="'+col+'" points="'+bimBrdPx(x1)+','+bimBrdPx(y1)+' '+bimBrdPx(bx-uy*hw)+','+bimBrdPx(by+ux*hw)+' '+bimBrdPx(bx+uy*hw)+','+bimBrdPx(by-ux*hw)+'"/>';
  }
  /* the shape alone: [markup, W, H] at its box's origin; a line's from its corner */
  function bimBdsShape(n,hit){
    var b=bimBtrBox(n),W=bimBdsPx(b.w),H=bimBdsPx(b.h),k=bimBtrPxMm(),s='',x0,y0,x1,y1,sw,col;
    if(n.t==='rect'){var R=Math.min(bimBdsPx(n.r),W/2,H/2);s='<rect x="0" y="0" width="'+W+'" height="'+H+'"'+(R>0?' rx="'+R+'"':'')+bimBdsPaint(n)+'/>';}
    else if(n.t==='ellipse')s='<ellipse cx="'+bimBrdPx(W/2)+'" cy="'+bimBrdPx(H/2)+'" rx="'+bimBrdPx(W/2)+'" ry="'+bimBrdPx(H/2)+'"'+bimBdsPaint(n)+'/>';
    else if(n.t==='poly'||n.t==='star')s='<polygon points="'+bimBdsPts(n,W,H).map(function(p){return p.join(',');}).join(' ')+'"'+bimBdsPaint(n)+'/>';
    else if(n.t==='line'){
      x0=bimBrdPx((n.x-b.x)*k);y0=bimBrdPx((n.y-b.y)*k);x1=bimBrdPx((n.x+n.w-b.x)*k);y1=bimBrdPx((n.y+n.h-b.y)*k);
      sw=bimBdsPx(n.sw);col=n.stroke&&n.stroke!=='none'?n.stroke:'none';
      s='<line x1="'+x0+'" y1="'+y0+'" x2="'+x1+'" y2="'+y1+'" stroke="'+col+'" stroke-width="'+sw+'" stroke-linecap="butt"/>';
      if(col!=='none'){if(n.a1)s+=bimBdsArrow(x0,y0,x1,y1,sw,col);if(n.a0)s+=bimBdsArrow(x1,y1,x0,y0,sw,col);}
      if(hit)s+='<line class="a3d-clb-dhit" x1="'+x0+'" y1="'+y0+'" x2="'+x1+'" y2="'+y1+'" stroke="transparent" stroke-width="14"/>';
    }
    return [s,W,H];
  }
  /* ---- one element ---- */
  function bimBdsNode(n,ox,oy,ctx){
    if(n.hide)return '';
    var t=n.t,b,S,h,u;
    if(t==='group'||t==='frame')return bimBdsBox(n,ox,oy,ctx);
    if(t==='fig')return bimBdsFig(n,ox,oy,ctx);
    b=bimBtrBox(n);
    if(t==='rect'||t==='ellipse'||t==='poly'||t==='star'||t==='line'){
      S=bimBdsShape(n,ctx.edit);
      return '<svg'+bimBdsAttr(n,'a3d-clb-dshp'+(t==='line'?' ln':''),ctx)+' xmlns="http://www.w3.org/2000/svg" style="'+bimBdsPos(b,ox,oy)+bimBdsComp(n,false)+'" viewBox="0 0 '+Math.max(S[1],0.001)+' '+Math.max(S[2],0.001)+'" preserveAspectRatio="none">'+S[0]+'</svg>';
    }
    if(t==='text'){
      h='left:'+bimBdsPx(b.x-ox)+'px;top:'+bimBdsPx(b.y-oy)+'px;';
      if(n.fit!=='auto-w')h+='width:'+bimBdsPx(b.w)+'px;';
      if(n.fit==='fixed')h+='height:'+bimBdsPx(b.h)+'px;overflow:hidden;';
      h+='font-size:'+bimBrdPx(n.fs*0.352778*bimBtrPxMm())+'px;font-weight:'+n.fw+';text-align:'+n.al+';color:'+n.col+';';
      return '<div'+bimBdsAttr(n,'a3d-clb-dtxt'+(n.fit==='auto-w'?' aw':''),ctx)+' style="'+h+bimBdsComp(n,false)+'">'+bimClbE(n.s)+'</div>';
    }
    if(t==='image'){
      u=n.src?bimBimgUrl(n.src):null;
      h=bimBdsPos(b,ox,oy)+bimBdsComp(n,false);
      if(!u)return '<div'+bimBdsAttr(n,'a3d-clb-dimg ph',ctx)+' style="'+h+'"><span>'+(n.src&&!bimBimgMissing(n.src)?'Loading the image':'This image is not in this browser: open the project file it came in')+'</span></div>';
      h+='background-image:url(\''+u+'\');background-size:'+(n.fit==='fit'?'contain':n.fit==='tile'?'auto':'cover')+';background-repeat:'+(n.fit==='tile'?'repeat':'no-repeat')+';';
      return '<div'+bimBdsAttr(n,'a3d-clb-dimg',ctx)+' role="img" aria-label="'+bimClbE(n.nm||'Image')+'" style="'+h+'"></div>';
    }
    return '';
  }
  /* a frame (its box, fill and clip) or a group; drawn as its own element only when it must be */
  function bimBdsBox(n,ox,oy,ctx){
    var iso=bimBdsIsolated(n),b,s,inner;
    if(n.t==='group'){
      if(!iso)return bimBdsList(n.ch,ox,oy,ctx);
      b=bimBtrBox(n,ctx.figBox);if(!b)return '';
      return '<div'+bimBdsAttr(n,'a3d-clb-dgrp',ctx)+' style="'+bimBdsPos(b,ox,oy)+bimBdsComp(n,true)+'">'+bimBdsList(n.ch,b.x,b.y,ctx)+'</div>';
    }
    b=bimBtrBox(n);
    s=bimBdsPos(b,ox,oy)+bimBdsComp(n,iso);
    if(n.fill&&n.fill!=='none')s+='background:'+n.fill+';';
    if(n.stroke&&n.stroke!=='none'&&n.sw>0)s+='box-shadow:inset 0 0 0 '+bimBdsPx(n.sw)+'px '+n.stroke+';';
    if(n.r>0)s+='border-radius:'+bimBdsPx(n.r)+'px;';
    if(n.clip)s+='overflow:hidden;';
    inner=bimBdsList(n.ch,b.x,b.y,ctx);
    return '<div'+bimBdsAttr(n,'a3d-clb-dfrm',ctx)+' style="'+s+'">'+inner+'</div>';
  }
  /* a list of siblings, in runs: a run under a mask is one masked element */
  function bimBdsList(L,ox,oy,ctx){
    var h='';
    bimBtrRuns(L||[]).forEach(function(R){
      var inner='',b,m=R.mask;
      if(!m){R.items.forEach(function(n){h+=bimBdsNode(n,ox,oy,ctx);});return;}
      b=bimBtrBox(m);
      R.items.forEach(function(n){inner+=bimBdsNode(n,b.x,b.y,ctx);});
      h+='<div class="a3d-clb-dmask" data-bdmask="'+m.id+'" style="'+bimBdsPos(b,ox,oy)+bimBdsMaskCss(m)+'">'+inner+'</div>';
    });
    return h;
  }
  /* the CSS that masks a run: vector by its outline, alpha and luminance by its picture */
  function bimBdsMaskCss(m){
    var type=m.mask,url,sz='100% 100%',rep='no-repeat',S,svg;
    if(type==='vector'&&m.t!=='line'){
      if(m.t==='rect')return 'clip-path:inset(0'+(m.r>0?' round '+bimBdsPx(m.r)+'px':'')+');';
      if(m.t==='ellipse')return 'clip-path:ellipse(50% 50% at 50% 50%);';
      if(m.t==='poly'||m.t==='star'){
        return 'clip-path:polygon('+bimBdsPts(m,100,100).map(function(p){return p[0]+'% '+p[1]+'%';}).join(',')+');';   /* in hundredths of its box */
      }
      return 'clip-path:inset(0);';   /* an image's outline is its box */
    }
    if(m.t==='image'){
      url=m.src?bimBimgUrl(m.src):null;
      if(!url)return 'visibility:hidden;';   /* the picture that masks is not here: nothing it masks is shown */
      if(m.fit==='fit')sz='contain';else if(m.fit==='tile'){sz='auto';rep='repeat';}else sz='cover';
      url='url(\''+url+'\')';
    }else{
      S=bimBdsShape(m,false);
      svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+Math.max(S[1],1)+'" height="'+Math.max(S[2],1)+'" viewBox="0 0 '+Math.max(S[1],0.001)+' '+Math.max(S[2],0.001)+'" preserveAspectRatio="none" overflow="visible">'+
        (m.op<1?'<g opacity="'+m.op+'">'+S[0]+'</g>':S[0])+'</svg>';
      url='url(\'data:image/svg+xml,'+encodeURIComponent(svg).replace(/'/g,'%27')+'\')';
    }
    return '-webkit-mask-image:'+url+';mask-image:'+url+';-webkit-mask-size:'+sz+';mask-size:'+sz+';-webkit-mask-repeat:'+rep+';mask-repeat:'+rep+';-webkit-mask-position:center;mask-position:center;'+
      'mask-mode:'+(type==='lum'?'luminance':'alpha')+';'+(type==='lum'?'-webkit-mask-source-type:luminance;':'');
  }
  /* a figure of the board, where its list puts it, with its element's opacity and mode */
  function bimBdsFig(n,ox,oy,ctx){
    var F=ctx.figs[n.k];
    if(!F)return '';
    return bimBrdFigHtml(F.F,ctx,(oy*bimBtrPxMm())/BIM_BRD_P0,F.over,{
      dx:-ox*bimBtrPxMm(),num:F.no,cls:' a3d-clb-dfig'+(n.lock?' lk':''),attr:' data-bde="'+n.id+'"',style:bimBdsComp(n,false)});
  }
  /* ---- the whole board ---- */
  /* the board's height in mm: its lowest element, and its figures' */
  function bimBdsBottom(els,figBox){
    var bot=0;
    bimBtrWalk(els,function(n){var b=n.t==='group'?null:bimBtrBox(n,figBox);if(b&&b.y+b.h>bot)bot=b.y+b.h;});
    return bot;
  }
  function bimBdsFigBoxer(figs){
    var M={};
    figs.forEach(function(F){M[F.k]=F;});
    return function(k){var F=M[k];return F?bimBtrFigBox(F,BIM_BRD_P0,BIM_BRD_G):null;};
  }
  /* a board with a tree: the arranged figures' section, drawn from the tree. ctx: {edit, narrow, caps, no} */
  function bimBdsHtml(B,figs,ctx){
    var els=B.els||[],ov=ctx.edit?bimBrdOverlaps(figs):{k:{}},no=0,H,h;
    ctx.figBox=bimBdsFigBoxer(figs);ctx.figs={};
    /* figures are numbered in reading order, as the bands number them */
    bimBrdBands(figs).forEach(function(D){D.f.forEach(function(F){
      var src=F.f==='text'?null:bimFigSrc(ctx,F.f,F.o||{});
      if(src&&!src.kpis)no++;
      ctx.figs[F.k]={F:F,over:!!ov.k[F.k],no:src&&!src.kpis?no:0};
    });});
    ctx.no=no;
    H=bimBdsBottom(els,ctx.figBox);
    h='<section class="a3d-clb-arr a3d-clb-dsn'+(ctx.edit?' edit':'')+'" aria-label="The board" style="height:'+bimBdsPx(H+(ctx.edit?60:0))+'px">';
    if(ctx.edit)h+='<div class="a3d-clb-arrgrid'+(A3D_SNAP.grid?' on':'')+'" aria-hidden="true" style="height:100%"></div>';
    h+='<div class="a3d-clb-dcv">'+bimBdsList(els,0,0,ctx)+'</div>';
    if(ctx.edit)h+='<div class="a3d-clb-dsel" aria-hidden="true"></div>';
    return h+'</section>';
  }
  /* an image that arrives from the database: the open board drawn again with it, and the thumbnails */
  A3D_BIMG.redraw=function(){bimClbRefresh();};
export { bimBdsFigBoxer, bimBdsHtml, bimBdsPos, bimBdsPx };
