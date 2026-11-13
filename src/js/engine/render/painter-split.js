  /* ================= __acad3dV200: the 2D view's faces cut small before they are sorted =================
     Without WebGL or WebGPU, and in presentation graphics, the model is painted face by face, the farthest
     first, each face placed by its average depth. A big face is then placed by a point far from most of it: a
     floor's middle is nearer the eye than a sofa standing at its far side, so the floor was painted over the
     sofa, and things vanished as the view turned. Each face is cut here into triangles, each sorted on its own,
     so the depth of the floor where the sofa stands is the one that counts. A side is cut while it is longer
     than BIM_PAINT_PX on the screen and BIM_PAINT_STEP in the model: small where the view is close, few where
     it is far, so a frame paints hundreds of pieces, not tens of thousands. Each piece keeps which of its
     sides lie on the face's own outline: those are stroked, the cuts are not. */
  var BIM_PAINT_STEP=0.1,BIM_PAINT_PX=40,BIM_PAINT_DEPTH=20,BIM_PAINT_BUDGET=20000;
  /* the face as triangles, its outline kept: fanned from its first corner when convex, its ears cut off one by
     one when not; null when it has no area or folds over itself */
  function bimPaintFan(w){
    var n=w.length,i,out=[];
    if(n<3)return null;
    if(n===3)return [{w:[w[0],w[1],w[2]],e:[true,true,true]}];
    var nn=bimPaintNormal(w),sg=bimPaintSigns(w,nn);
    if(!sg.neg||!sg.pos){
      for(i=1;i<n-1;i++)out.push({w:[w[0],w[i],w[i+1]],e:[i===1,true,i+1===n-1]});
      return out;
    }
    return bimPaintEars(w,nn);
  }
  function bimPaintNormal(w){   /* Newell's normal, unscaled: only its direction is used */
    var n=[0,0,0],i,a,b;
    for(i=0;i<w.length;i++){a=w[i];b=w[(i+1)%w.length];n[0]+=(a[1]-b[1])*(a[2]+b[2]);n[1]+=(a[2]-b[2])*(a[0]+b[0]);n[2]+=(a[0]-b[0])*(a[1]+b[1]);}
    return n;
  }
  /* the turn at b, going a, b, c, along the face's normal: positive where the outline turns the face's way */
  function bimPaintTurn(a,b,c,nn){
    return ((b[1]-a[1])*(c[2]-b[2])-(b[2]-a[2])*(c[1]-b[1]))*nn[0]+((b[2]-a[2])*(c[0]-b[0])-(b[0]-a[0])*(c[2]-b[2]))*nn[1]+((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))*nn[2];
  }
  function bimPaintSigns(w,nn){
    var i,n=w.length,x,r={pos:0,neg:0};
    for(i=0;i<n;i++){x=bimPaintTurn(w[i],w[(i+1)%n],w[(i+2)%n],nn);if(x>1e-12)r.pos++;else if(x<-1e-12)r.neg++;}
    return r;
  }
  /* a concave face by ear clipping: a corner that turns the face's way, with no other corner inside its
     triangle, is cut off; a side of the cut triangle is outline when it joins corners next to each other in
     the face as given */
  function bimPaintEars(w,nn){
    var idx=[],i,out=[],guard=0,n=w.length;
    for(i=0;i<n;i++)idx.push(i);
    while(idx.length>3&&guard++<n*n){
      var m=idx.length,cut=false;
      for(i=0;i<m;i++){
        var ia=idx[(i+m-1)%m],ib=idx[i],ic=idx[(i+1)%m],a=w[ia],b=w[ib],c=w[ic],k,inside=false;
        if(bimPaintTurn(a,b,c,nn)<=1e-12)continue;
        for(k=0;k<m;k++){
          var q=idx[k];if(q===ia||q===ib||q===ic)continue;
          if(bimPaintTurn(a,b,w[q],nn)>=0&&bimPaintTurn(b,c,w[q],nn)>=0&&bimPaintTurn(c,a,w[q],nn)>=0){inside=true;break;}
        }
        if(inside)continue;
        out.push({w:[a,b,c],e:[(ib-ia+n)%n===1,(ic-ib+n)%n===1,(ia-ic+n)%n===1]});
        idx.splice(i,1);cut=true;break;
      }
      if(!cut)return null;
    }
    if(idx.length===3)out.push({w:[w[idx[0]],w[idx[1]],w[idx[2]]],e:[(idx[1]-idx[0]+n)%n===1,(idx[2]-idx[1]+n)%n===1,(idx[0]-idx[2]+n)%n===1]});
    return out;
  }
  function bimPaintLen2(a,b){var x=a[0]-b[0],y=a[1]-b[1],z=a[2]-b[2];return x*x+y*y+z*z;}
  function bimPaintMid(a,b){return [(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2];}
  /* how far a side is too long: 0 when it is not (in the model, or on the screen when the screen is given),
     else its length squared on the screen, or in the model without one */
  function bimPaintLong(t,i,C){
    var j=(i+1)%3,m=bimPaintLen2(t.w[i],t.w[j]);
    if(m<=C.step2)return 0;
    if(!C.proj)return m;
    var p=t.s[i],q=t.s[j],dx=p[0]-q[0],dy=p[1]-q[1],d=dx*dx+dy*dy;
    return d>C.px2?d:0;
  }
  /* a piece wholly past one side of the view: never seen, so never cut (a corner behind the eye lands far off
     the screen, and its sides would look long enough to be cut to the last depth for nothing) */
  function bimPaintOff(t,C){
    if(!C.view)return false;
    var s=t.s,W=C.view[0],H=C.view[1];
    return (s[0][0]<0&&s[1][0]<0&&s[2][0]<0)||(s[0][0]>W&&s[1][0]>W&&s[2][0]>W)||
      (s[0][1]<0&&s[1][1]<0&&s[2][1]<0)||(s[0][1]>H&&s[1][1]>H&&s[2][1]>H);
  }
  /* a triangle halved across its longest too-long side while it has one, at most depth times: halving the
     longest side keeps the pieces near square, where cutting in four keeps a sliver a sliver (a wall's side
     seen along its length needed thousands) */
  function bimPaintCut(t,C,depth,out){
    var L0=0,L1=0,L2=0,i;
    if(depth>0&&C.budget.left>0&&!bimPaintOff(t,C)){L0=bimPaintLong(t,0,C);L1=bimPaintLong(t,1,C);L2=bimPaintLong(t,2,C);}
    if(!L0&&!L1&&!L2){out.push(t);C.budget.left--;return;}
    i=(L0>=L1&&L0>=L2)?0:(L1>=L2?1:2);
    var j=(i+1)%3,k=(i+2)%3,W=t.w,e=t.e,m=bimPaintMid(W[i],W[j]),sm=C.proj?C.proj(m):null;
    bimPaintCut({w:[W[i],m,W[k]],s:sm&&[t.s[i],sm,t.s[k]],e:[e[i],false,e[k]]},C,depth-1,out);
    bimPaintCut({w:[m,W[j],W[k]],s:sm&&[sm,t.s[j],t.s[k]],e:[e[i],e[j],false]},C,depth-1,out);
  }
  /* a face's pieces, its world corners in, each {w: its corners, s: their screen points when proj is given,
     e: which sides are outline}; null keeps the face whole (no area, or it folds over itself). budget is
     {left:n}, shared by the frame's faces; past it a face is only fanned. proj(p) gives a point's screen
     position (x, y, depth), as toScreen does; without it the sides are measured in the model only. view, the
     screen's [width, height], when given, leaves the pieces off it uncut. */
  function bimPaintPieces(w,budget,step,proj,view){
    var tris=bimPaintFan(w),out=[],i,s=step||BIM_PAINT_STEP,
      C={step2:s*s,px2:BIM_PAINT_PX*BIM_PAINT_PX,proj:proj||null,view:(proj&&view)||null,budget:budget||{left:Infinity}};
    if(!tris)return null;
    for(i=0;i<tris.length;i++){
      if(C.proj)tris[i].s=[C.proj(tris[i].w[0]),C.proj(tris[i].w[1]),C.proj(tris[i].w[2])];
      bimPaintCut(tris[i],C,BIM_PAINT_DEPTH,out);
    }
    return out;
  }
export { BIM_PAINT_BUDGET, bimPaintPieces };
