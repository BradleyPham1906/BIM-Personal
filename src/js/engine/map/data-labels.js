import { A3D } from '../core/state.js';
import { bimPolyArea } from '../bim/rooms.js';
import { bimDgDrawText } from '../site-analysis/model-layers.js';
import { toScreen } from '../io/import-entry.js';
import { bimDataMask } from './data-filter-ui.js';
import { bimDataFeats, bimDataList } from './data-layers.js';
import { bimDataModel } from './find-open-data.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV173b: a data layer's labels =================
     A label is one field, or a template of fields and words such as {NAME} ({AREA} m2) (the owner's
     D12). An area is labelled at its pole of inaccessibility, the inside point furthest from every
     edge, by polylabel's method; a line at the middle of its length; a point beside it. Labels that
     would overlap one already drawn are dropped, the top layer's and the larger areas' first, as
     QGIS's "never overlap". Field text is drawn with fillText, never written into the page. */
  var A3D_DLAB={anchors:{}};
  var BIM_DLAB_MAX=2000;
  /* polylabel 2.1.0's method (mapbox/polylabel, ISC, Copyright (c) 2026 Mapbox; credited in
     THIRD_PARTY_NOTICES.md), in ES5: square cells over the outer ring's box, each cell's centre's
     signed distance to the outline, a queue by the most a cell could hold, split until no cell can
     beat the best by more than the precision. Version 2's block skipping and seeding are left out:
     the answer is the same, only slower on rings of thousands of points. rings[0] is the outer ring. */
  function bimPolyLabel(rings,precision){
    var minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity,o=rings[0],i,w,h,cell,best,bb,q=[],c,x,y,hh;
    precision=precision>0?precision:1;
    for(i=0;i<o.length;i++){if(o[i][0]<minX)minX=o[i][0];if(o[i][1]<minY)minY=o[i][1];if(o[i][0]>maxX)maxX=o[i][0];if(o[i][1]>maxY)maxY=o[i][1];}
    w=maxX-minX;h=maxY-minY;
    cell=Math.max(precision,Math.min(w,h));
    if(cell===precision)return {x:minX,y:minY,d:0};
    function segSq(px,py,ax,ay,bx,by){
      var dx=bx-ax,dy=by-ay,t;
      if(dx!==0||dy!==0){t=((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy);if(t>1){ax=bx;ay=by;}else if(t>0){ax+=dx*t;ay+=dy*t;}}
      dx=px-ax;dy=py-ay;return dx*dx+dy*dy;
    }
    function dist(px,py){
      var inside=false,m=Infinity,r,k,j,R,a,b;
      for(r=0;r<rings.length;r++){
        R=rings[r];
        for(k=0,j=R.length-1;k<R.length;j=k++){
          a=R[k];b=R[j];
          if((a[1]>py)!==(b[1]>py)&&px<(b[0]-a[0])*(py-a[1])/(b[1]-a[1])+a[0])inside=!inside;
          m=Math.min(m,segSq(px,py,a[0],a[1],b[0],b[1]));
        }
      }
      return m===0?0:(inside?1:-1)*Math.sqrt(m);
    }
    function mk(px,py,ph){var d=dist(px,py);return {x:px,y:py,h:ph,d:d,max:d+ph*Math.SQRT2};}
    function push(c){var k=q.length,p,t;q.push(c);while(k>0){p=(k-1)>>1;if(q[p].max>=q[k].max)break;t=q[p];q[p]=q[k];q[k]=t;k=p;}}
    function pop(){
      var top=q[0],last=q.pop(),k=0,l,r,m,t;
      if(q.length){q[0]=last;for(;;){l=2*k+1;r=l+1;m=k;if(l<q.length&&q[l].max>q[m].max)m=l;if(r<q.length&&q[r].max>q[m].max)m=r;if(m===k)break;t=q[m];q[m]=q[k];q[k]=t;k=m;}}
      return top;
    }
    /* the first guesses: the outer ring's centroid when inside, else its first point; then the box's centre */
    var A=0,cx=0,cy=0,f;
    for(i=0,x=o.length-1;i<o.length;x=i++){f=o[i][0]*o[x][1]-o[x][0]*o[i][1];cx+=(o[i][0]+o[x][0])*f;cy+=(o[i][1]+o[x][1])*f;A+=f*3;}
    best=A!==0?mk(cx/A,cy/A,0):null;
    if(!best||best.d<0)best=mk(o[0][0],o[0][1],0);
    bb=mk(minX+w/2,minY+h/2,0);
    if(bb.d>best.d)best=bb;
    hh=cell/2;
    for(x=minX;x<maxX;x+=cell)for(y=minY;y<maxY;y+=cell){c=mk(x+hh,y+hh,hh);if(c.max>best.d+precision)push(c);if(c.d>best.d)best=c;}
    var probes=0;
    while(q.length&&probes<20000){
      c=pop();
      if(c.max-best.d<=precision)break;
      hh=c.h/2;
      [[-hh,-hh],[hh,-hh],[-hh,hh],[hh,hh]].forEach(function(s){var n=mk(c.x+s[0],c.y+s[1],hh);probes++;if(n.max>best.d+precision)push(n);if(n.d>best.d)best=n;});
    }
    return {x:best.x,y:best.y,d:best.d};
  }
  /* a label's text: a template's {field}s filled, or one field's value; null when it has none */
  function bimDataLabelText(spec,props){
    var s=String(spec||''),out;
    function val(k){
      var v=props&&Object.prototype.hasOwnProperty.call(props,k)?props[k]:null;
      if(v===null||v===undefined)return '';
      if(typeof v==='number')return String(Math.round(v*100)/100);
      return String(v);
    }
    if(!s)return null;
    if(s.indexOf('{')<0)out=val(s);
    else out=s.replace(/\{([^{}]{1,80})\}/g,function(m,k){return val(k);});
    out=out.replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,120);
    return out?out:null;
  }
  /* where each feature is labelled, in model terms: kept with the layer's model cache */
  function bimDataAnchors(L,c){
    var m=A3D_DLAB.anchors[L.id],out=[],j,f,k,best,ba,a,len,l,s,t,seg,pts,d,rings;
    if(m&&m.c===c)return m.a;
    for(j=0;j<c.feats.length;j++){
      f=c.feats[j];a=null;
      if(f.rings.length){
        best=null;ba=-1;rings=[];
        for(k=0;k<f.rings.length;k++)if(!f.rings[k].hole){s=Math.abs(bimPolyArea(f.rings[k].pts));if(s>ba){ba=s;best=f.rings[k].pts;}}
        if(best){
          rings.push(best);
          for(k=0;k<f.rings.length;k++)if(f.rings[k].hole)rings.push(f.rings[k].pts);
          try{d=bimPolyLabel(rings,Math.max(0.25,Math.sqrt(ba)/100));a={x:d.x,z:d.y,kind:'area',pri:ba};}
          catch(e){console.warn('[BIM] label place',e);}
        }
      }else if(f.lines.length){
        pts=null;len=-1;
        for(k=0;k<f.lines.length;k++){l=0;for(s=1;s<f.lines[k].length;s++)l+=Math.hypot(f.lines[k][s][0]-f.lines[k][s-1][0],f.lines[k][s][1]-f.lines[k][s-1][1]);if(l>len){len=l;pts=f.lines[k];}}
        t=len/2;
        for(s=1;s<pts.length&&!a;s++){
          seg=Math.hypot(pts[s][0]-pts[s-1][0],pts[s][1]-pts[s-1][1]);
          if(t<=seg||s===pts.length-1){d=seg>0?Math.min(1,t/seg):0;a={x:pts[s-1][0]+(pts[s][0]-pts[s-1][0])*d,z:pts[s-1][1]+(pts[s][1]-pts[s-1][1])*d,kind:'line',pri:-1};}
          t-=seg;
        }
      }else if(f.points.length)a={x:f.points[0][0],z:f.points[0][1],kind:'point',pri:-2};
      out.push(a);
    }
    A3D_DLAB.anchors[L.id]={c:c,a:out};
    return out;
  }
  /* every shown layer's labels, after the features: the top layer first, then larger areas */
  function drawDataLabels(ctx,V,W,H,y){
    var L=bimDataList(),Q=[],placed=[],i,j,c,an,F,mask,t,p,b,wd,n=0,x0,free;
    A3D.lastDataLabels=0;
    for(i=L.length-1;i>=0;i--){
      if(!L[i].visible||!L[i].label)continue;
      c=bimDataModel(L[i]);
      if(!c)continue;
      an=bimDataAnchors(L[i],c);F=bimDataFeats(L[i].id);mask=bimDataMask(L[i]);
      var lq=[];
      for(j=0;j<c.feats.length;j++){
        if(!an[j]||(mask&&!mask.pass[c.feats[j].fi]))continue;
        t=bimDataLabelText(L[i].label,F[c.feats[j].fi]&&F[c.feats[j].fi].p);
        if(t)lq.push({t:t,a:an[j]});
      }
      lq.sort(function(u,v){return v.a.pri-u.a.pri;});
      Q=Q.concat(lq);
    }
    if(!Q.length)return;
    ctx.save();
    try{
      ctx.textBaseline='middle';ctx.font='11px sans-serif';
      free=function(bx){for(var k=0;k<placed.length;k++){var q=placed[k];if(bx[0]<q[0]+q[2]&&q[0]<bx[0]+bx[2]&&bx[1]<q[1]+q[3]&&q[1]<bx[1]+bx[3])return false;}return true;};
      for(i=0;i<Q.length&&n<BIM_DLAB_MAX;i++){
        p=toScreen([Q[i].a.x,y,Q[i].a.z],V,W,H);
        if(!p||!isFinite(p[0])||!isFinite(p[1])||p[0]<-50||p[1]<-20||p[0]>W+50||p[1]>H+20)continue;
        wd=ctx.measureText(Q[i].t).width;
        x0=Q[i].a.kind==='point'?p[0]+6:p[0]-wd/2;
        b=[x0-2,p[1]-8,wd+4,16];
        if(!free(b))continue;
        placed.push(b);
        ctx.textAlign=Q[i].a.kind==='point'?'left':'center';
        bimDgDrawText(ctx,Q[i].t,Q[i].a.kind==='point'?p[0]+6:p[0],p[1],'#e8edf2',11,false);
        n++;
      }
    }catch(e){
      console.warn('[BIM] data labels',e);
      if(!A3D.dataLabelWarned){A3D.dataLabelWarned=true;a3dToast('The data layer labels could not be drawn');}
    }
    ctx.restore();
    A3D.lastDataLabels=n;
  }
export { bimDataLabelText, bimPolyLabel, drawDataLabels };
