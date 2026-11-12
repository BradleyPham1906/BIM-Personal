import { A3D } from '../core/state.js';
import { A3D_SNAP } from '../drawing/plan-mode-sketch.js';
import { bimPresentGraphics } from '../layers/plot-by-layers.js';
import { A3D_PLOT, bimLayerById, bimLayerEff } from '../layers/layer-rules.js';
import { bimClbE, bimClbRefresh } from '../site-analysis/climate-board.js';
import { bimProjectLabel } from '../ui/project-tabs.js';
import { A3D_SLIDESHOW } from './present.js';
import { bimPresIndex, bimPresSeq } from './boards.js';
import {
  BIM_BRD_G, BIM_BRD_P0, bimBoardLabel, bimBrdBands, bimBrdFigHtml, bimBrdOverlaps, bimBrdPx, bimFigSrc
} from './board-figures.js';
import {
  bimBobBlend, bimBobBm, bimBobBox, bimBobFigBox, bimBobFigMover, bimBobLayApply, bimBobPaint, bimBobPxMm,
  bimBobRuns, bimBobTr
} from './board-objects.js';
import { bimPgBoardPage } from './page-sizes.js';
import { A3D_BIMG, bimBimgMissing, bimBimgUrl } from './board-images.js';
import { bimLiveMarks, bimLiveShow } from './live-sources.js';
import { bimLbdHtml } from './live-board-draw.js';
import { bimBmapHtml } from './board-map.js';


  /* ================= __acad3dV174a: a board's objects, drawn =================
     docs/research/research-presentation-boards.md, 5.1 (D1: HTML and SVG, as the boards are) and 11a (R1 to R4).
     The objects are drawn in paint order (bimBobPaint: the layers from the bottom of the list up, the list's order
     within a layer). A layer that is off or frozen hides its objects; one set not to plot leaves them off paper (a
     print is built in a plot pass, bimWithPlotPass); a locked one fades them in Edit. Transparency and Blend, ByLayer
     or the object's own, are applied to each object, as AutoCAD applies a layer's transparency, and only in the
     Presentation appearance and in Present: the Technical appearance draws every object plain, as a technical plot
     leaves transparency out. Masks apply in both, being shapes: a mask clips the objects of its layer above it,
     vector by clip-path, alpha and luminance by mask-image (the mask's own shape as an SVG picture, mask-mode).
     The canvas is a sheet of paper in every theme (the print tokens) and an isolated root, so a blend mode over an
     empty part of the board blends with white, on screen as on paper. Paint order is the markup's, never a z-index. */
  function bimBdsPx(mm){return bimBrdPx(mm*bimBobPxMm());}
  /* the Presentation appearance, or Present: where transparency and blend modes are drawn (R2) */
  function bimBdsPres(){return bimPresentGraphics()||!!A3D_SLIDESHOW.on;}
  function bimBdsComp(n,ctx){
    var s='',a=1,B;
    if(ctx.pres){
      a=1-bimBobTr(n)/100;
      B=bimBobBlend(bimBobBm(n));
      if(B&&B[2]!=='normal')s+='mix-blend-mode:'+B[2]+';';
    }
    if(ctx.edit&&ctx.lk[n.id])a*=0.5;   /* a locked layer, faded as AutoCAD fades it on screen */
    if(a<1)s='opacity:'+Math.round(a*1000)/1000+';'+s;
    return s;
  }
  function bimBdsPos(b,ox,oy){return 'left:'+bimBdsPx(b.x-ox)+'px;top:'+bimBdsPx(b.y-oy)+'px;width:'+bimBdsPx(b.w)+'px;height:'+bimBdsPx(b.h)+'px;';}
  function bimBdsAttr(n,cls,ctx){
    return ' class="'+cls+(ctx.lk[n.id]?' lk':'')+'" data-bde="'+n.id+'"'+(ctx.edit?'':' aria-hidden="true"');
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
    var b=bimBobBox(n),W=bimBdsPx(b.w),H=bimBdsPx(b.h),k=bimBobPxMm(),s='',x0,y0,x1,y1,sw,col;
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
  /* ---- one object ---- */
  function bimBdsNode(n,ox,oy,ctx){
    var t=n.t,b,S,h,u,pd,Wp,Hp,Lv;
    if(t==='fig')return bimBdsFig(n,ox,oy,ctx);
    if(t==='tblock')return bimBdsTblock(n,ox,oy,ctx);   /* __acad3dV174c */
    if(t==='map'||t==='legend'||t==='north'||t==='sbar')return bimBmapHtml(n,ox,oy,ctx);   /* __acad3dV174d */
    if(t==='sched'||t==='kpi'||t==='rchart')return bimLbdHtml(n,ox,oy,ctx);   /* __acad3dV175b */
    if(t==='border')return '<div'+bimBdsAttr(n,'a3d-clb-dbdr',ctx)+' style="'+bimBdsPos(bimBobBox(n),ox,oy)+'border:'+bimBdsPx(n.sw)+'px solid #0b0b0b;'+bimBdsComp(n,ctx)+'"></div>';
    b=bimBobBox(n);
    if(t==='line'){   /* a level line's box is 0 high, and an SVG of no size is not painted: it grows by its stroke and heads */
      S=bimBdsShape(n,ctx.edit);
      pd=bimBrdPx(Math.max(8,bimBdsPx(n.sw)*4)+2);Wp=bimBrdPx(S[1]+2*pd);Hp=bimBrdPx(S[2]+2*pd);
      return '<svg'+bimBdsAttr(n,'a3d-clb-dshp ln',ctx)+' xmlns="http://www.w3.org/2000/svg" style="left:'+bimBrdPx(bimBdsPx(b.x-ox)-pd)+'px;top:'+bimBrdPx(bimBdsPx(b.y-oy)-pd)+'px;width:'+Wp+'px;height:'+Hp+'px;'+
        bimBdsComp(n,ctx)+'" viewBox="'+(-pd)+' '+(-pd)+' '+Wp+' '+Hp+'">'+S[0]+'</svg>';
    }
    if(t==='rect'||t==='ellipse'||t==='poly'||t==='star'){
      S=bimBdsShape(n,false);
      return '<svg'+bimBdsAttr(n,'a3d-clb-dshp',ctx)+' xmlns="http://www.w3.org/2000/svg" style="'+bimBdsPos(b,ox,oy)+bimBdsComp(n,ctx)+'" viewBox="0 0 '+Math.max(S[1],0.001)+' '+Math.max(S[2],0.001)+'" preserveAspectRatio="none">'+S[0]+'</svg>';
    }
    if(t==='text'){
      h='left:'+bimBdsPx(b.x-ox)+'px;top:'+bimBdsPx(b.y-oy)+'px;';
      if(n.fit!=='auto-w')h+='width:'+bimBdsPx(b.w)+'px;';
      if(n.fit==='fixed')h+='height:'+bimBdsPx(b.h)+'px;overflow:hidden;';
      h+='font-size:'+bimBrdPx(n.fs*0.352778*bimBobPxMm())+'px;font-weight:'+n.fw+';text-align:'+n.al+';color:'+n.col+';';
      Lv=n.bind?bimLiveShow(n,ctx.B||null,!!ctx.edit&&!A3D_PLOT.on):null;   /* __acad3dV175a: a live text's words, from the project now */
      return '<div'+bimBdsAttr(n,'a3d-clb-dtxt'+(n.fit==='auto-w'?' aw':'')+(Lv?' lv':''),ctx)+' style="'+h+(Lv&&Lv.hint?'font-size:'+bimBrdPx(Math.min(n.fs,9)*0.352778*bimBobPxMm())+'px;font-weight:400;font-style:italic;':'')+bimBdsComp(n,ctx)+'">'+bimClbE(Lv?Lv.s:n.s)+(Lv&&ctx.edit&&!A3D_PLOT.on?bimLiveMarks(Lv):'')+'</div>';
    }
    if(t==='image'){
      u=n.src?bimBimgUrl(n.src):null;
      h=bimBdsPos(b,ox,oy)+bimBdsComp(n,ctx);
      if(!u)return '<div'+bimBdsAttr(n,'a3d-clb-dimg ph',ctx)+' style="'+h+'"><span>'+(n.src&&!bimBimgMissing(n.src)?'Loading the image':'This image is not in this browser: open the project file it came in')+'</span></div>';
      h+='background-image:url(\''+u+'\');background-size:'+(n.fit==='fit'?'contain':n.fit==='tile'?'auto':'cover')+';background-repeat:'+(n.fit==='tile'?'repeat':'no-repeat')+';';
      return '<div'+bimBdsAttr(n,'a3d-clb-dimg',ctx)+' role="img" aria-label="'+bimClbE(n.nm||'Image')+'" style="'+h+'"></div>';
    }
    return '';
  }
  /* the CSS that masks a run: vector by its outline, alpha and luminance by its picture */
  function bimBdsMaskCss(m){
    var type=m.mask,url,sz='100% 100%',rep='no-repeat',S,svg;
    if(type==='vector'&&m.t!=='line'){
      if(m.t==='rect')return 'clip-path:inset(0'+(m.r>0?' round '+bimBdsPx(m.r)+'px':'')+');';
      if(m.t==='ellipse')return 'clip-path:ellipse(50% 50% at 50% 50%);';
      if(m.t==='poly'||m.t==='star')return 'clip-path:polygon('+bimBdsPts(m,100,100).map(function(p){return p[0]+'% '+p[1]+'%';}).join(',')+');';   /* in hundredths of its box */
      return 'clip-path:inset(0);';   /* an image's outline is its box */
    }
    if(m.t==='image'){
      url=m.src?bimBimgUrl(m.src):null;
      if(!url)return 'visibility:hidden;';   /* the picture that masks is not here: nothing it masks is shown */
      if(m.fit==='fit')sz='contain';else if(m.fit==='tile'){sz='auto';rep='repeat';}else sz='cover';
      url='url(\''+url+'\')';
    }else{
      S=bimBdsShape(m,false);
      svg='<svg xmlns="http://www.w3.org/2000/svg" width="'+Math.max(S[1],1)+'" height="'+Math.max(S[2],1)+'" viewBox="0 0 '+Math.max(S[1],0.001)+' '+Math.max(S[2],0.001)+'" preserveAspectRatio="none" overflow="visible">'+S[0]+'</svg>';
      url='url(\'data:image/svg+xml,'+encodeURIComponent(svg).replace(/'/g,'%27')+'\')';
    }
    return '-webkit-mask-image:'+url+';mask-image:'+url+';-webkit-mask-size:'+sz+';mask-size:'+sz+';-webkit-mask-repeat:'+rep+';mask-repeat:'+rep+';-webkit-mask-position:center;mask-position:center;'+
      'mask-mode:'+(type==='lum'?'luminance':'alpha')+';';
  }
  /* a figure of the board, where its list puts it, with its transparency and blend */
  function bimBdsFig(n,ox,oy,ctx){
    var F=ctx.figs[n.k];
    if(!F)return '';
    return bimBrdFigHtml(F.F,ctx,(oy*bimBobPxMm())/BIM_BRD_P0,F.over,{
      dx:-ox*bimBobPxMm(),num:F.no,cls:' a3d-clb-dfig'+(ctx.lk[n.id]?' lk':''),attr:' data-bde="'+n.id+'"',style:bimBdsComp(n,ctx)});
  }
  /* __acad3dV174c: a title block's fields, from the project and the board: ISO 7200's eight mandatory ones (legal
     owner, identification number, date of issue, sheet number, title, approval person, creator, document type), or a
     US title strip with the same facts, stacked */
  function bimBdsTblock(n,ox,oy,ctx){
    var tb=A3D.titleBlock||{},B=ctx.B,i=B?bimPresIndex(B.id):-1,N=bimPresSeq().length,dt=n.dt||bimBdsToday(),F,h,c,fs=bimBdsPx(2.4),fl=bimBdsPx(1.8);
    F=[['Title',B?bimBoardLabel(B):''],['Project',bimProjectLabel()],['Legal owner',tb.client||''],['Created by',tb.drawnBy||''],['Approved by',tb.checkedBy||''],
      ['Document type','Presentation board'],['Identification',n.num||''],['Date of issue',dt],['Sheet',i>=0?(i+1)+' of '+N:'']];
    c=function(f,big){return '<div class="a3d-clb-dtbc"><span style="font-size:'+fl+'px">'+bimClbE(f[0])+'</span><b style="font-size:'+(big?bimBdsPx(4):fs)+'px">'+bimClbE(f[1]||'-')+'</b></div>';};
    if(n.st==='us')h='<div class="a3d-clb-dtbs">'+F.map(function(f,j){return c(f,j===0);}).join('')+'</div>';
    else h='<div class="a3d-clb-dtbi">'+c(F[0],true)+'<div class="a3d-clb-dtbr">'+c(F[1])+c(F[2])+'</div><div class="a3d-clb-dtbr">'+c(F[3])+c(F[4])+c(F[5])+'</div>'+
      '<div class="a3d-clb-dtbr">'+c(F[6])+c(F[7])+c(F[8])+'</div></div>';
    return '<div'+bimBdsAttr(n,'a3d-clb-dtb',ctx)+' style="'+bimBdsPos(bimBobBox(n),ox,oy)+'border:'+bimBdsPx(0.5)+'px solid #0b0b0b;'+bimBdsComp(n,ctx)+'">'+h+'</div>';
  }
  function bimBdsToday(){var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2);}
  /* ---- the whole board ---- */
  function bimBdsFigBoxer(figs){
    var M={};
    figs.forEach(function(F){M[F.k]=F;});
    return function(k){var F=M[k];return F?bimBobFigBox(F,BIM_BRD_P0,BIM_BRD_G):null;};
  }
  /* what is drawn: the objects whose layer is on and thawed (and, on paper, plotted), in paint order; ctx.lk the
     locked ones */
  function bimBdsShown(L,ctx){
    var P=bimBobPaint(L),out=[];
    ctx.lk={};
    P.forEach(function(p){
      var ly=bimLayerById(p.ly),s=ly?bimLayerEff(ly):{on:true,frozen:false,locked:false,plot:true};
      if(!s.on||s.frozen||(A3D_PLOT.on&&!s.plot))return;
      if(s.locked&&!A3D_PLOT.on)ctx.lk[p.n.id]=1;
      out.push(p);
    });
    return out;
  }
  /* a board with objects: the arranged figures' section, drawn from them. ctx: {edit, narrow, caps, no} */
  function bimBdsHtml(B,figs,ctx){
    var L=B.objs||[],ov=ctx.edit?bimBrdOverlaps(figs):{k:{}},no=0,H=0,fb,h,body='',Wn;
    if(ctx.narrow&&B.lay){   /* __acad3dV174b: on a phone a stack's row is shown as a column, in reading order (D11) */
      Wn={objs:JSON.parse(JSON.stringify(L)),figs:JSON.parse(JSON.stringify(figs)),lay:B.lay};
      bimBobLayApply(Wn,bimBdsFigBoxer(Wn.figs),bimBobFigMover(Wn.figs),true);
      L=Wn.objs;figs=Wn.figs;
    }
    ctx.figBox=fb=bimBdsFigBoxer(figs);ctx.figs={};ctx.pres=bimBdsPres();ctx.allObjs=L;
    /* figures are numbered in reading order, as the bands number them */
    bimBrdBands(figs).forEach(function(D){D.f.forEach(function(F){
      var src=F.f==='text'?null:bimFigSrc(ctx,F.f,F.o||{});
      if(src&&!src.kpis)no++;
      ctx.figs[F.k]={F:F,over:!!ov.k[F.k],no:src&&!src.kpis?no:0};
    });});
    ctx.no=no;
    L.forEach(function(n){var b=bimBobBox(n,fb);if(b&&b.y+b.h>H)H=b.y+b.h;});
    var pg=bimPgBoardPage(B);   /* __acad3dV174c: a board with a page is that page */
    if(pg)H=pg.h;
    bimBobRuns(bimBdsShown(L,ctx)).forEach(function(R){
      var inner='',b,m=R.mask;
      if(!m){R.items.forEach(function(n){body+=bimBdsNode(n,0,0,ctx);});return;}
      b=bimBobBox(m);
      R.items.forEach(function(n){inner+=bimBdsNode(n,b.x,b.y,ctx);});
      body+='<div class="a3d-clb-dmask" data-bdmask="'+m.id+'" style="'+bimBdsPos(b,0,0)+bimBdsMaskCss(m)+'">'+inner+'</div>';
    });
    h='<section class="a3d-clb-arr a3d-clb-dsn'+(ctx.edit?' edit':'')+(pg?' pg':'')+'" aria-label="'+(pg?bimClbE('The board\'s page, '+pg.label):'The board')+'" style="height:'+bimBdsPx(H+(ctx.edit&&!pg?60:0))+'px'+
      (pg?';width:'+bimBdsPx(pg.w)+'px" data-w="'+bimBdsPx(pg.w):'')+'">';
    if(ctx.edit)h+='<div class="a3d-clb-arrgrid'+(A3D_SNAP.grid?' on':'')+'" aria-hidden="true" style="height:100%"></div>';
    h+='<div class="a3d-clb-dcv">'+body+'</div>';
    if(ctx.edit)h+='<div class="a3d-clb-dsel" aria-hidden="true"></div>';
    return h+'</section>';
  }
  /* an image that arrives from the database: the open board drawn again with it, and the thumbnails */
  A3D_BIMG.redraw=function(){bimClbRefresh();};
export { bimBdsAttr, bimBdsComp, bimBdsFigBoxer, bimBdsHtml, bimBdsPos, bimBdsPres, bimBdsPx, bimBdsToday };
