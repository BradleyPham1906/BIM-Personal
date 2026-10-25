  /* ================= __acad3dV98: the pick shape of an annotation =================

     What each annotation puts on screen, as pick geometry: segments (with the tolerance each
     one is picked at) and label boxes. Built from the same points, the same label anchors and
     the same fonts as drawDims / drawDimExtras / drawTextLabels, so an annotation is picked
     exactly where it is drawn -- including its label, which is the part people aim at.

     The reference circle of a radius or diameter dimension is deliberately NOT pickable: it is
     a dashed ghost drawn over the real arc, and letting it win would make the arc underneath
     unselectable. */
  function bimAnnotDrawable(o){
    if(!o||(o.t!=='dim'&&o.t!=='text'&&o.t!=='roomtag'))return false;
    if(o.t==='roomtag'&&!objById(o.roomId))return false;   /* __acad3dV101 */
    if(A3D.section)return false;
    /* __acad3dV121: shown, not pickable -- a locked layer is drawn. This read `locked` as hidden,
       and it decides whether a room tag is drawn, exported and counted: locking a layer took its
       tags off the canvas, the exports and every sheet, and brought the rooms' own labels back.
       Picking asks bimLayerPickable below. */
    if(!bimLayerShown(o))return false;
    if(!bimAnnotationVisible(o))return false;
    if(!bimObjectVisibleOnLevel(o))return false;
    return true;
  }
  function bimMeasureLabel(text,font){
    ctx_measure_font();
    if(!A3D_TEXT_MEASURE_CTX)return String(text).length*7;
    A3D_TEXT_MEASURE_CTX.font=font;
    var w=A3D_TEXT_MEASURE_CTX.measureText(String(text)).width;
    A3D_TEXT_MEASURE_CTX.font='12px system-ui,sans-serif';
    return w;
  }
  function bimAnnotScreenShape(o,V,W,H){
    var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
    var y0=(o.y||0)+oy;
    function S(p){return toScreen([p[0]+ox,y0,p[1]+oz],V,W,H);}
    var segs=[],boxes=[],i,tw,lp,label,bx;
    function seg(a,b,tol){segs.push([a[0],a[1],b[0],b[1],tol]);}
    if(o.t==='roomtag'){   /* __acad3dV101: the drawn box, from the one layout */
      var TL=bimRoomTagLayout(o,V,W,H);
      if(TL)boxes.push(TL.box);
      return {segs:segs,boxes:boxes};
    }
    if(o.t==='text'){
      var sp=S(o.pt);
      tw=bimMeasureLabel(o.text||'','12px system-ui,sans-serif');
      boxes.push([sp[0]-4,sp[1]-11,sp[0]+tw+14,sp[1]+11]);
      return {segs:segs,boxes:boxes};
    }
    var kind=bimDimKind(o);
    if(kind==='linear'){
      if(!o.p1||!o.p2||!o.d1||!o.d2)return {segs:segs,boxes:boxes};
      var p1=S(o.p1),p2=S(o.p2),d1=S(o.d1),d2=S(o.d2);
      seg(d1,d2,8);
      seg(p1,d1,5);seg(p2,d2,5);
      var mx=(d1[0]+d2[0])/2,my=(d1[1]+d2[1])/2;
      tw=bimMeasureLabel((o.length||0).toFixed(2)+' m','11px system-ui,sans-serif');
      boxes.push([mx-tw/2-4,my-16,mx+tw/2+4,my-2]);
    }else if(kind==='angular'){
      if(!o.vertex||!o.ap1||!o.ap2)return {segs:segs,boxes:boxes};
      var vtx=S(o.vertex);
      seg(vtx,S(o.ap1),6);seg(vtx,S(o.ap2),6);
      var prev=null,a;
      for(i=0;i<=24;i++){
        a=o.a1+o.sweep*(i/24);
        var cur=S([o.vertex[0]+Math.cos(a)*o.arcRadius,o.vertex[1]+Math.sin(a)*o.arcRadius]);
        if(prev)seg(prev,cur,8);
        prev=cur;
      }
      var midA=o.a1+o.sweep/2;
      lp=S([o.vertex[0]+Math.cos(midA)*o.arcRadius*1.25,o.vertex[1]+Math.sin(midA)*o.arcRadius*1.25]);
      label=(o.degrees||0).toFixed(1)+'\u00b0';
      tw=bimMeasureLabel(label,'11px system-ui,sans-serif');
      bx=lp[0]-tw/2;
      boxes.push([bx-4,lp[1]-8,bx+tw+4,lp[1]+7]);
    }else if(kind==='radius'||kind==='diameter'){
      if(!o.dStart||!o.dEdge)return {segs:segs,boxes:boxes};
      var st=S(o.dStart),ed=S(o.dEdge);
      seg(st,ed,8);
      lp=[(st[0]+ed[0])/2,(st[1]+ed[1])/2-10];
      label=(kind==='diameter'?'\u00d8':'R')+(o.value||0).toFixed(2);
      tw=bimMeasureLabel(label,'11px system-ui,sans-serif');
      bx=lp[0]-tw/2;
      boxes.push([bx-4,lp[1]-8,bx+tw+4,lp[1]+7]);
    }else if(kind==='leader'){
      if(!o.anchor||!o.elbow||!o.landing)return {segs:segs,boxes:boxes};
      var an=S(o.anchor),el2=S(o.elbow),la=S(o.landing);
      seg(an,el2,8);seg(el2,la,8);
      if(o.label){
        lp=[la[0]+(o.ldir<0?-4:4),la[1]-6];
        tw=bimMeasureLabel(o.label,'11px system-ui,sans-serif');
        bx=o.ldir<0?lp[0]-tw:lp[0];
        boxes.push([bx-4,lp[1]-8,bx+tw+4,lp[1]+7]);
      }
    }
    return {segs:segs,boxes:boxes};
  }
  /* Distance in pixels from (x,y) to an annotation, or Infinity when it is out of reach. A
     label box counts as a direct hit. */
  function bimAnnotHitDist(o,x,y,V,W,H){
    var sh=bimAnnotScreenShape(o,V,W,H),best=Infinity,i,s,b,d;
    for(i=0;i<sh.boxes.length;i++){
      b=sh.boxes[i];
      if(x>=b[0]&&x<=b[2]&&y>=b[1]&&y<=b[3])return 0;
    }
    for(i=0;i<sh.segs.length;i++){
      s=sh.segs[i];
      d=bimPointSegDist(x,y,s[0],s[1],s[2],s[3]);
      if(d<s[4]&&d<best)best=d;
    }
    return best;
  }
  function bimPickAnnotOfType(x,y,t){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var best=null,bestD=Infinity,i,o,d;
    /* Later in the list is drawn later, so it is on top and wins a tie. */
    for(i=A3D.objs.length-1;i>=0;i--){
      o=A3D.objs[i];
      if(o.t!==t||!bimAnnotDrawable(o)||!bimLayerPickable(o))continue;   /* __acad3dV121 */
      d=bimAnnotHitDist(o,x,y,V,W,H);
      if(d<bestD){bestD=d;best=o;}
    }
    return best;
  }
  function bimPickDim(x,y){return bimPickAnnotOfType(x,y,'dim');}
  function bimPickText(x,y){return bimPickAnnotOfType(x,y,'text');}
  /* Text is drawn after dimensions, so it is tested first. */
  function bimPickAnnotation(x,y){
    /* __acad3dV101: tags are drawn after text, so they are tested first */
    return bimPickAnnotOfType(x,y,'roomtag')||bimPickText(x,y)||bimPickDim(x,y);
  }
  var A3D_TEXT_MEASURE_CTX=null;
  function ctx_measure_font(){
    if(!A3D_TEXT_MEASURE_CTX&&el.cv)A3D_TEXT_MEASURE_CTX=el.cv.getContext('2d');
    if(A3D_TEXT_MEASURE_CTX)A3D_TEXT_MEASURE_CTX.font='12px system-ui,sans-serif';
  }
  function bimStrToBytes(s){
    var arr=new Uint8Array(s.length),i;
    for(i=0;i<s.length;i++)arr[i]=s.charCodeAt(i)&0xFF;
    return arr;
  }
  function bimPadNum(n,len){var s=String(n);while(s.length<len)s='0'+s;return s;}
  function bimBuildSimplePdf(width,height,rgbBytes){
    var chunks=[],offsets=[],pos=0;
    function push(x){
      var buf=(typeof x==='string')?bimStrToBytes(x):x;
      chunks.push(buf);
      pos+=buf.length;
    }
    function beginObj(n){offsets[n]=pos;push(n+' 0 obj\n');}
    push('%PDF-1.4\n%\xE2\xE3\xCF\xD3\n');
    beginObj(1);push('<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');
    beginObj(2);push('<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n');
    beginObj(3);push('<< /Type /Page /Parent 2 0 R /Resources << /XObject << /Im0 5 0 R >> >> /MediaBox [0 0 '+width+' '+height+'] /Contents 4 0 R >>\nendobj\n');
    var content='q\n'+width+' 0 0 '+height+' 0 0 cm\n/Im0 Do\nQ\n';
    var contentBytes=bimStrToBytes(content);
    beginObj(4);push('<< /Length '+contentBytes.length+' >>\nstream\n');push(contentBytes);push('\nendstream\nendobj\n');
    beginObj(5);
    push('<< /Type /XObject /Subtype /Image /Width '+width+' /Height '+height+' /ColorSpace /DeviceRGB /BitsPerComponent 8 /Length '+rgbBytes.length+' >>\nstream\n');
    push(rgbBytes);
    push('\nendstream\nendobj\n');
    var xrefStart=pos;
    var xref='xref\n0 6\n0000000000 65535 f \n',i;
    for(i=1;i<=5;i++)xref+=bimPadNum(offsets[i],10)+' 00000 n \n';
    push(xref);
    push('trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+xrefStart+'\n%%EOF');
    var total=0,j;
    for(j=0;j<chunks.length;j++)total+=chunks[j].length;
    var out=new Uint8Array(total),off=0;
    for(j=0;j<chunks.length;j++){out.set(chunks[j],off);off+=chunks[j].length;}
    return out;
  }
  function bimGetCanvasRGB(){
    var ctx2=el.cv.getContext('2d');
    var W=el.cv.width,H=el.cv.height;
    var imgData=ctx2.getImageData(0,0,W,H);
    var rgba=imgData.data;
    var rgb=new Uint8Array(W*H*3),i,j=0;
    for(i=0;i<rgba.length;i+=4){rgb[j++]=rgba[i];rgb[j++]=rgba[i+1];rgb[j++]=rgba[i+2];}
    return {w:W,h:H,rgb:rgb};
  }
  function bimTriggerDownload(bytes,filename,mime){
    var blob=new Blob([bytes],{type:mime});
    var url=URL.createObjectURL(blob);
    var a=document.createElement('a');
    a.href=url;a.download=filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function(){URL.revokeObjectURL(url);},1000);
  }
  function bimExportPNG(){
    try{
      var dataURL;
      try{dataURL=bimWithPlotPass(A3D.presentMode,function(){paint();return el.cv.toDataURL('image/png');});}   /* __acad3dV121: a plot */
      finally{paint();}
      var a=document.createElement('a');
      a.href=dataURL;a.download=bimFileStem()+'-plan.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      a3dToast('Exported '+bimFileStem()+'-plan.png');
    }catch(eP){console.warn('[BIM] PNG export failed: ',eP);a3dToast('PNG export failed: '+(eP&&eP.message?eP.message:eP));}
  }
  function bimExportPDF(){
    try{
      var cv;
      try{cv=bimWithPlotPass(A3D.presentMode,function(){paint();return bimGetCanvasRGB();});}   /* __acad3dV121: a plot */
      finally{paint();}
      var pdfBytes=bimBuildSimplePdf(cv.w,cv.h,cv.rgb);
      bimTriggerDownload(pdfBytes,bimFileStem()+'-plan.pdf','application/pdf');
      a3dToast('Exported '+bimFileStem()+'-plan.pdf ('+(pdfBytes.length/1024/1024).toFixed(1)+' MB, uncompressed)');
    }catch(eD){console.warn('[BIM] PDF export failed: ',eD);a3dToast('PDF export failed: '+(eD&&eD.message?eD.message:eD));}
  }
