  // ---- __acad3dV37: ViewCube restyled to match Revit's. Revit's cube is a LIGHT solid cube with
  // dark uppercase face labels, a compass ring beneath it carrying N/E/S/W that rotates with the
  // camera, and a small house icon for Home rather than a text button. The previous version was
  // translucent grey with a "HOME" text box. Faces are drawn back-to-front by depth so the cube
  // reads as solid instead of showing through itself.
  function bimDrawCompass(ctx,cx,cy,r,V){
    // Project world North (-Z) and East (+X) into screen space so the ring turns with the camera.
    function proj(w){
      return [w[0]*V.r[0]+w[1]*V.r[1]+w[2]*V.r[2], -(w[0]*V.u[0]+w[1]*V.u[1]+w[2]*V.u[2])];
    }
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.strokeStyle='rgba(150,158,168,0.55)';
    ctx.lineWidth=1.2;
    ctx.stroke();
    var dirs=[{l:'N',w:[0,0,-1]},{l:'E',w:[1,0,0]},{l:'S',w:[0,0,1]},{l:'W',w:[-1,0,0]}];
    ctx.font='bold 8.5px system-ui,sans-serif';
    ctx.textAlign='center';ctx.textBaseline='middle';
    var i;
    for(i=0;i<dirs.length;i++){
      var d=proj(dirs[i].w);
      var len=Math.sqrt(d[0]*d[0]+d[1]*d[1]);
      if(len<0.08)continue; // direction is nearly edge-on; its label would sit on the centre
      var ux=d[0]/len,uy=d[1]/len;
      var lx=cx+ux*(r+7),ly=cy+uy*(r+7);
      ctx.fillStyle=(dirs[i].l==='N')?'#e06a5a':'#aab2bb';
      ctx.fillText(dirs[i].l,lx,ly);
      ctx.beginPath();
      ctx.moveTo(cx+ux*(r-3),cy+uy*(r-3));
      ctx.lineTo(cx+ux*r,cy+uy*r);
      ctx.strokeStyle=(dirs[i].l==='N')?'#e06a5a':'rgba(150,158,168,0.7)';
      ctx.lineWidth=1.4;ctx.stroke();
    }
    ctx.restore();
  }
  function bimDrawHomeIcon(ctx,x,y,size,hot){
    ctx.save();
    var h=size,w=size;
    ctx.beginPath();
    ctx.moveTo(x,y-h*0.5);
    ctx.lineTo(x+w*0.55,y-h*0.02);
    ctx.lineTo(x+w*0.34,y-h*0.02);
    ctx.lineTo(x+w*0.34,y+h*0.5);
    ctx.lineTo(x+w*0.12,y+h*0.5);
    ctx.lineTo(x+w*0.12,y+h*0.14);
    ctx.lineTo(x-w*0.12,y+h*0.14);
    ctx.lineTo(x-w*0.12,y+h*0.5);
    ctx.lineTo(x-w*0.34,y+h*0.5);
    ctx.lineTo(x-w*0.34,y-h*0.02);
    ctx.lineTo(x-w*0.55,y-h*0.02);
    ctx.closePath();
    ctx.fillStyle=hot?'#4ea1ff':'#c8ced6';
    ctx.fill();
    ctx.restore();
  }
  function drawCube(ctx,W,H,V){
    var cx=W-72,cy=68,s=25,i,j;
    var pts=[];
    for(i=0;i<8;i++){
      var p=CORN[i];
      var xc=p[0]*V.r[0]+p[1]*V.r[1]+p[2]*V.r[2];
      var yc=p[0]*V.u[0]+p[1]*V.u[1]+p[2]*V.u[2];
      var zc=p[0]*V.d[0]+p[1]*V.d[1]+p[2]*V.d[2];
      pts.push([cx+xc*s,cy-yc*s,zc]);
    }
    bimDrawCompass(ctx,cx,cy,s*1.72,V);
    A3D.cubePolys=[];
    // depth-sort visible faces so the cube reads as a solid object, as Revit's does
    var faces=[];
    for(i=0;i<CFACES.length;i++){
      var cf=CFACES[i],wpts=[],spts=[],zs=0;
      for(j=0;j<cf.f.length;j++){wpts.push(CORN[cf.f[j]]);spts.push(pts[cf.f[j]]);zs+=pts[cf.f[j]][2];}
      if(vdot(faceNormal(wpts),V.d)<=0.12)continue;
      faces.push({cf:cf,spts:spts,z:zs/cf.f.length});
    }
    faces.sort(function(a,b){return b.z-a.z;});
    for(i=0;i<faces.length;i++){
      var F=faces[i],sp=F.spts;
      ctx.beginPath();ctx.moveTo(sp[0][0],sp[0][1]);
      for(j=1;j<sp.length;j++)ctx.lineTo(sp[j][0],sp[j][1]);
      ctx.closePath();
      var hot=(A3D.view||'').toLowerCase()===F.cf.n;
      // Revit's cube is a light solid, not a translucent overlay
      ctx.fillStyle=hot?'#4e8fd0':'#e8ebee';
      ctx.fill();
      ctx.strokeStyle='#98a0aa';ctx.lineWidth=1;ctx.stroke();
      var lx=0,ly=0;
      for(j=0;j<sp.length;j++){lx+=sp[j][0];ly+=sp[j][1];}
      lx/=sp.length;ly/=sp.length;
      ctx.fillStyle=hot?'#ffffff':'#3d444c';
      ctx.font='bold 8px system-ui,sans-serif';
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillText(F.cf.n.toUpperCase(),lx,ly);
      A3D.cubePolys.push({n:F.cf.n,pts:sp});
    }
    // Home: a house icon beside the cube, as in Revit -- not a text button
    var hx=cx-s*2.05,hy=cy-s*1.35,hs=13;
    var hotHome=(A3D.view||'').toLowerCase()==='home';
    bimDrawHomeIcon(ctx,hx,hy,hs,hotHome);
    A3D.homeRect=[hx-hs*0.62,hy-hs*0.56,hs*1.24,hs*1.12];
  }
  function inPoly(x,y,pts){
    var inside=false,i,j;
    for(i=0,j=pts.length-1;i<pts.length;j=i++){
      var xi=pts[i][0],yi=pts[i][1],xj=pts[j][0],yj=pts[j][1];
      var hit=((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi);
      if(hit)inside=!inside;
    }
    return inside;
  }
  function bimPointSegDist(px,py,x1,y1,x2,y2){
    var dx=x2-x1,dy=y2-y1;
    var len2=dx*dx+dy*dy;
    var t=len2>1e-9?((px-x1)*dx+(py-y1)*dy)/len2:0;
    t=Math.max(0,Math.min(1,t));
    var cx=x1+t*dx,cy=y1+t*dy;
    var ex=px-cx,ey=py-cy;
    return Math.sqrt(ex*ex+ey*ey);
  }
  function bimPickSketch(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var best=null,bestD=8,i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='sketch')continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      /* __acad3dV88: pick against the FLATTENED curve. An arc picked on its chord would be
         selectable along a line it is not drawn on, and unselectable where it is. */
      /* __acad3dV94, collecting a V93 gap: a POINT has one vertex and therefore no
         segments, so the segment walk below could never reach it and a point was selectable
         from the tree and by marquee but not by clicking the thing itself. */
      if(bimIsPoint(o)){
        var pp=toScreen(bimWorldPt(o,o.pts[0],o.y),V,W,H);
        var dP=Math.sqrt((x-pp[0])*(x-pp[0])+(y-pp[1])*(y-pp[1]));
        if(dP<bestD){bestD=dP;best=o;}
        continue;
      }
      var pts=bimFlattenSketch(o),n=pts.length,segCount=(o.closed!==false)?n:n-1,k;
      for(k=0;k<segCount;k++){
        var a=pts[k],b=pts[(k+1)%n];
        // __acad3dV75: pick where the sketch is DRAWN, not where its local array says.
        var pa=toScreen(bimWorldPt(o,a,o.y),V,W,H),pb=toScreen(bimWorldPt(o,b,o.y),V,W,H);
        var d=bimPointSegDist(x,y,pa[0],pa[1],pb[0],pb[1]);
        if(d<bestD){bestD=d;best=o;}
      }
    }
    return best||bimPickCline(x,y)||bimPickRoom(x,y)||bimPickHatch(x,y)||bimPickProperty(x,y)||bimPickAlignment(x,y);   /* __acad3dV127: alignments after property lines; __acad3dV98: annotations are picked in pick(), first; __acad3dV103: property lines last */
  }
  /* __acad3dV94: picked on the piece that is DRAWN, which is the clipped segment -- the same
     one bimClineVisibleSeg hands the renderer, so a construction line is selectable exactly
     where it appears and nowhere else. */
  function bimPickCline(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var best=null,bestD=8,i,o,box=null;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsCline(o))continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      if(!box)box=bimDrawingExtent2D();
      var seg=bimClineVisibleSeg(o,box);
      if(!seg)continue;
      var pa=toScreen(bimWorldPt(o,seg[0],o.y),V,W,H);
      var pb=toScreen(bimWorldPt(o,seg[1],o.y),V,W,H);
      var d=bimPointSegDist(x,y,pa[0],pa[1],pb[0],pb[1]);
      if(d<bestD){bestD=d;best=o;}
    }
    return best;
  }
  /* __acad3dV96: a hatch is picked by clicking INSIDE it, like a room, and it is tested
     after rooms so a room label is never swallowed by a hatch lying under it. */
  function bimPickHatch(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var candidates=[],i,o,k;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!bimIsHatch(o))continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      var ring=bimHatchOutline(o);
      if(ring.length<3)continue;
      var sp=[];
      for(k=0;k<ring.length;k++)sp.push(toScreen(bimWorldPt(o,ring[k],o.y),V,W,H));
      if(bimPointInPoly([x,y],sp))candidates.push({o:o,area:bimPolyArea(sp)});
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return a.area-b.area;});
    return candidates[0].o;
  }
  function bimPickRoom(x,y){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH();
    var candidates=[],i,o;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='room')continue;
      if(!bimLayerPickable(o))continue;   /* __acad3dV121 */
      var ox=(o.pos&&o.pos[0])||0,oy=(o.pos&&o.pos[1])||0,oz=(o.pos&&o.pos[2])||0;
      var sp=o.pts.map(function(p){return toScreen([p[0]+ox,o.y+oy,p[1]+oz],V,W,H);});
      if(bimPointInPoly([x,y],sp))candidates.push({o:o,area:bimPolyArea(sp)});
    }
    if(!candidates.length)return null;
    candidates.sort(function(a,b){return a.area-b.area;});
    return candidates[0].o;
  }
  function bimGetEditablePoints(o){
    if(!o)return null;
    if(o.t==='sketch')return {pts:o.pts,y:o.y,kind:'sketch'};
    if(o.t==='solid'&&o.bim&&o.bim.type==='wall'&&o.bim.centerline)return {pts:o.bim.centerline,y:o.bim.baseY,kind:'wall'};
    var ap=bimAnnotGripPoints(o);   /* __acad3dV98 */
    if(ap)return {pts:ap,y:o.y||0,kind:'annot'};
    return null;
  }
