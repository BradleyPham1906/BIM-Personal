  /* ================= __acad3dV137: the map on 3D terrain ================= */
  var BIM_DRAPE_ZREF=22,BIM_DRAPE_MAXT=36;
  /* the heights come from V127's bimTinHeightAt */
  /* the site context's surface, if it has one */
  function bimCtxTerrainObj(){
    var i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].t==='terrain'&&A3D.objs[i].context&&A3D.objs[i].context.kind==='terrain')return A3D.objs[i];
    return null;
  }
  /* context buildings onto the terrain (the lowest height under each footprint), or back onto the
     level; no undo step of its own, the caller's */
  function bimCtxStand(on){
    var ter=on?bimCtxTerrainObj():null,tin=ter?bimTerrainTin(ter):null,i,j,o,fp,h,y,n=0;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!o.context||o.context.kind!=='buildings')continue;
      y=0;
      if(tin){
        fp=o.context.standFp||o.context.footprint||[];h=null;   /* __acad3dV139: a part, on its building's ground */
        for(j=0;j<fp.length;j++){var hh=bimTinHeightAt(tin,fp[j][0],fp[j][1]);if(hh!==null&&(h===null||hh<h))h=hh;}
        if(h===null&&typeof o.context.ground==='number')h=o.context.ground;
        if(h!==null){y=Math.round(h*1000)/1000;n++;}
      }
      o.pos=[o.pos&&o.pos[0]||0,y,o.pos&&o.pos[2]||0];
      o.context.standY=y;
    }
    return n;
  }
  /* ---- GL: the surface, and the map draped on it ---- */
  function bimTerrainGlProg(G){
    if(G.ter)return G.ter.prog?G.ter:null;
    var gl=G.gl;
    G.ter={prog:null,bufs:{}};
    var vs=bimGlCompile(gl,gl.VERTEX_SHADER,'attribute vec3 aPos;attribute vec3 aNorm;attribute vec2 aMerc;'+
      'uniform mat4 uView;uniform mat4 uProj;uniform vec3 uLight;uniform vec2 uTile;uniform float uInv;'+
      'varying vec2 vUV;varying float vK;'+
      'void main(){vUV=(aMerc-uTile)*uInv;vK=0.5+0.5*abs(dot(normalize(aNorm),uLight));gl_Position=uProj*uView*vec4(aPos,1.0);}');
    /* uMode 0: the surface in its colour; 1: one tile, nothing drawn outside it */
    var fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,'precision mediump float;uniform sampler2D uTex;uniform float uMode;uniform vec3 uColor;'+
      'uniform float uAlpha;uniform vec4 uSub;varying vec2 vUV;varying float vK;'+
      'void main(){if(uMode<0.5){gl_FragColor=vec4(uColor*vK,1.0);return;}'+
      'if(vUV.x<0.0||vUV.x>1.0||vUV.y<0.0||vUV.y>1.0)discard;'+
      'vec3 c=texture2D(uTex,uSub.xy+vUV*(uSub.zw-uSub.xy)).rgb;'+
      'gl_FragColor=vec4(mix(uColor*vK,c*(0.62+0.38*vK),uAlpha),1.0);}');
    if(!vs||!fs)return null;
    var p=gl.createProgram();
    gl.attachShader(p,vs);gl.attachShader(p,fs);gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS)){console.warn('[BIM] terrain shader link failed: '+gl.getProgramInfoLog(p));return null;}
    G.ter={prog:p,bufs:{},pos:gl.getAttribLocation(p,'aPos'),norm:gl.getAttribLocation(p,'aNorm'),merc:gl.getAttribLocation(p,'aMerc'),
      view:gl.getUniformLocation(p,'uView'),proj:gl.getUniformLocation(p,'uProj'),light:gl.getUniformLocation(p,'uLight'),
      tile:gl.getUniformLocation(p,'uTile'),inv:gl.getUniformLocation(p,'uInv'),tex:gl.getUniformLocation(p,'uTex'),
      mode:gl.getUniformLocation(p,'uMode'),color:gl.getUniformLocation(p,'uColor'),alpha:gl.getUniformLocation(p,'uAlpha'),
      sub:gl.getUniformLocation(p,'uSub')};
    return G.ter;
  }
  /* a surface's triangles with smooth normals and each vertex's Mercator position (at BIM_DRAPE_ZREF,
     from a corner of its own, so the numbers stay small); kept until the survey or the place changes */
  var A3D_TER_DATA={};   /* __acad3dV154: a surface's arrays, for either engine */
  function bimTerrainMeshData(o,org){
    var tin=bimTerrainTin(o),tn=bimTrueNorthDeg(),key,D=A3D_TER_DATA[o.id],i,k,tr,nrm,pos=[],nor=[],mer=[],A,B,C,ux,uy,uz,vx,vy,vz,nx,ny,nz,L;
    if(!tin||!tin.tris.length)return null;
    key=(o.rev||0)+':'+o.survey.length+':'+(o.pos||[0,0,0]).join(',')+':'+tn+':'+(org?org.lat+','+org.lon:'-');
    if(D&&D.key===key)return D;
    nrm=tin.P.map(function(){return [0,0,0];});
    for(i=0;i<tin.tris.length;i++){
      tr=tin.tris[i];A=[tin.P[tr[0]][0],tin.H[tr[0]],tin.P[tr[0]][1]];B=[tin.P[tr[1]][0],tin.H[tr[1]],tin.P[tr[1]][1]];C=[tin.P[tr[2]][0],tin.H[tr[2]],tin.P[tr[2]][1]];
      ux=B[0]-A[0];uy=B[1]-A[1];uz=B[2]-A[2];vx=C[0]-A[0];vy=C[1]-A[1];vz=C[2]-A[2];
      nx=uy*vz-uz*vy;ny=uz*vx-ux*vz;nz=ux*vy-uy*vx;
      if(ny<0){nx=-nx;ny=-ny;nz=-nz;}
      for(k=0;k<3;k++){nrm[tr[k]][0]+=nx;nrm[tr[k]][1]+=ny;nrm[tr[k]][2]+=nz;}
    }
    var mx=null,ox=0,oy=0;
    if(org){
      mx=tin.P.map(function(p){var g=bimModelToGeo(p[0],p[1],org);return [bimLonToTileX(g[0],BIM_DRAPE_ZREF),bimLatToTileY(g[1],BIM_DRAPE_ZREF)];});
      ox=Math.floor(mx[0][0]);oy=Math.floor(mx[0][1]);
    }
    for(i=0;i<tin.tris.length;i++)for(k=0;k<3;k++){
      var v=tin.tris[i][k];
      pos.push(tin.P[v][0],tin.H[v],tin.P[v][1]);
      L=Math.sqrt(nrm[v][0]*nrm[v][0]+nrm[v][1]*nrm[v][1]+nrm[v][2]*nrm[v][2])||1;
      nor.push(nrm[v][0]/L,nrm[v][1]/L,nrm[v][2]/L);
      mer.push(mx?mx[v][0]-ox:0,mx?mx[v][1]-oy:0);
    }
    var lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,g;
    if(org)for(i=0;i<tin.P.length;i++){g=bimModelToGeo(tin.P[i][0],tin.P[i][1],org);lo0=Math.min(lo0,g[0]);lo1=Math.max(lo1,g[0]);la0=Math.min(la0,g[1]);la1=Math.max(la1,g[1]);}
    D=A3D_TER_DATA[o.id]={key:key,pos:new Float32Array(pos),nor:new Float32Array(nor),mer:new Float32Array(mer),count:pos.length/3,ox:ox,oy:oy,ext:org?[lo0,la0,lo1,la1]:null};
    return D;
  }
  function bimTerrainGlMesh(G,T,o,org){
    var D=bimTerrainMeshData(o,org),rec=T.bufs[o.id],gl=G.gl;
    if(!D)return null;
    if(rec&&rec.key===D.key)return rec;
    if(rec){gl.deleteBuffer(rec.pos);gl.deleteBuffer(rec.nor);gl.deleteBuffer(rec.mer);}
    function mk(a){var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,a,gl.STATIC_DRAW);return b;}
    rec=T.bufs[o.id]={key:D.key,pos:mk(D.pos),nor:mk(D.nor),mer:mk(D.mer),count:D.count,ox:D.ox,oy:D.oy,ext:D.ext};
    return rec;
  }
  /* the tiles over a surface's area: the view's zoom, lowered while more than BIM_DRAPE_MAXT */
  function bimDrapeTiles(ext,z,maxz){
    var x0,x1,y0,y1,n,T=[],x,y;
    z=Math.max(1,Math.min(maxz,z));
    for(;;){
      n=Math.pow(2,z);
      x0=Math.floor(bimLonToTileX(ext[0],z));x1=Math.floor(bimLonToTileX(ext[2],z));
      y0=Math.max(0,Math.floor(bimLatToTileY(ext[3],z)));y1=Math.min(n-1,Math.floor(bimLatToTileY(ext[1],z)));
      if((x1-x0+1)*(y1-y0+1)<=BIM_DRAPE_MAXT||z<=1)break;
      z--;
    }
    for(y=y0;y<=y1;y++)for(x=x0;x<=x1;x++)T.push({x:x,y:y,z:z});
    return T;
  }
  function bimTerrainDrawGl(G,V,W,H){
    A3D.lastTerrain3d=null;
    if(A3D_PLOT.on||bimCameraIsPlan())return;
    var list=[],i,o;
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o)&&!bimTerrainSuperseded(o))list.push(o);}   /* __acad3dV145 */
    if(!list.length)return;
    var T=bimTerrainGlProg(G);
    if(!T)return;
    var gl=G.gl,org=bimMapOrigin(),plan=bimMapPlan(V,W,H),rec,col,c,tiles,j,s,tex,sel,out=[];
    gl.useProgram(T.prog);
    gl.uniformMatrix4fv(T.view,false,bimGlViewMatrix(V));
    gl.uniformMatrix4fv(T.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
    gl.uniform3f(T.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.activeTexture(gl.TEXTURE0);gl.uniform1i(T.tex,0);
    gl.enableVertexAttribArray(T.pos);gl.enableVertexAttribArray(T.norm);gl.enableVertexAttribArray(T.merc);
    for(i=0;i<list.length;i++){
      o=list[i];
      rec=bimTerrainGlMesh(G,T,o,org);
      if(!rec)continue;
      sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
      col=bimHexToRgb(sel?'#4ea1ff':(o.col||'#b08559'));
      gl.uniform3f(T.color,col[0],col[1],col[2]);
      gl.bindBuffer(gl.ARRAY_BUFFER,rec.pos);gl.vertexAttribPointer(T.pos,3,gl.FLOAT,false,0,0);
      gl.bindBuffer(gl.ARRAY_BUFFER,rec.nor);gl.vertexAttribPointer(T.norm,3,gl.FLOAT,false,0,0);
      gl.bindBuffer(gl.ARRAY_BUFFER,rec.mer);gl.vertexAttribPointer(T.merc,2,gl.FLOAT,false,0,0);
      gl.uniform1f(T.mode,0);gl.uniform2f(T.tile,0,0);gl.uniform1f(T.inv,1);
      gl.drawArrays(gl.TRIANGLES,0,rec.count);
      c={id:o.id,triangles:rec.count/3,tiles:[],drawn:0,z:null};
      /* the map draped over it: each tile drawn over the whole surface, nothing outside the tile */
      if(plan.tiles.length&&rec.ext){
        tiles=bimDrapeTiles(rec.ext,plan.z,BIM_MAP_STYLES[plan.style].maxz);
        c.z=tiles.length?tiles[0].z:null;
        gl.uniform1f(T.mode,1);gl.uniform1f(T.alpha,plan.opacity);
        gl.depthMask(false);
        for(j=0;j<tiles.length;j++){
          s=bimMapSource(tiles[j],plan.tpl);tex=s?bimMapTex(gl,s.e):null;
          c.tiles.push({x:tiles[j].x,y:tiles[j].y,z:tiles[j].z,up:tex?s.up:null});
          if(!tex)continue;
          var sc=Math.pow(2,BIM_DRAPE_ZREF-tiles[j].z);
          gl.bindTexture(gl.TEXTURE_2D,tex);
          gl.uniform2f(T.tile,tiles[j].x*sc-rec.ox,tiles[j].y*sc-rec.oy);gl.uniform1f(T.inv,1/sc);
          gl.uniform4f(T.sub,s.u0,s.v0,s.u1,s.v1);
          gl.drawArrays(gl.TRIANGLES,0,rec.count);
          c.drawn++;
        }
        gl.depthMask(true);
        gl.bindTexture(gl.TEXTURE_2D,null);
      }
      out.push(c);
    }
    gl.disableVertexAttribArray(T.pos);gl.disableVertexAttribArray(T.norm);gl.disableVertexAttribArray(T.merc);
    A3D.lastTerrain3d=out;
  }
  /* ---- 2D: the surface's triangles, shaded, for the painter's sort ---- */
  function bimTerrainPolys(o,polys,V,W,H){
    var tin=bimTerrainTin(o),i,tr,w,pts,zs,k,sp;
    if(!tin)return;
    for(i=0;i<tin.tris.length;i++){
      tr=tin.tris[i];w=[];pts=[];zs=0;
      for(k=0;k<3;k++){w.push([tin.P[tr[k]][0],tin.H[tr[k]],tin.P[tr[k]][1]]);sp=toScreen(w[k],V,W,H);if(!sp)break;pts.push(sp);zs+=sp[2];}
      if(pts.length<3)continue;
      var n=faceNormal(w);if(n[1]<0)n=[-n[0],-n[1],-n[2]];
      polys.push({o:o,pts:pts,z:zs/3,n:n,col:o.col||'#b08559',lock:!bimLayerPickable(o),la:bimLayerAlpha(o),terrain:true});
    }
  }
  function bimGlRender(V,W,H){
    var G=bimGlInit();
    if(!G)return false;
    var gl=G.gl;
    var gs=cvScale(el.cv);
    var wDev=Math.max(1,Math.round(W*gs)),hDev=Math.max(1,Math.round(H*gs));
    if(G.cv.width!==wDev||G.cv.height!==hDev){G.cv.width=wDev;G.cv.height=hDev;}
    gl.viewport(0,0,wDev,hDev);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.clearColor(0.114,0.125,0.141,1);
    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    bimMapDrawGl(G,V,W,H);   /* __acad3dV132: the basemap, under everything */
    bimTerrainDrawGl(G,V,W,H);   /* __acad3dV137: the terrain in 3D, the map draped on it */
    if(A3D_GL_BATCH&&bimGbRender(G,V,W,H)){   /* __acad3dV152: the batches */
      var kb;for(kb in G.bufs)if(G.bufs.hasOwnProperty(kb)){bimGlDisposeBuffer(G,G.bufs[kb]);delete G.bufs[kb];}
      return true;
    }
    if(A3D_SCENE)bimSceneRelease();   /* __acad3dV153: object by object, the description given back */
    var draws=0;   /* __acad3dV152: counted, to set against the batches */
    gl.useProgram(G.prog);
    gl.uniformMatrix4fv(G.loc.view,false,bimGlViewMatrix(V));
    gl.uniformMatrix4fv(G.loc.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
    gl.uniform3f(G.loc.light,LIGHT[0],LIGHT[1],LIGHT[2]);
    gl.uniform3f(G.loc.eye,V.eye[0],V.eye[1],V.eye[2]);   /* __acad3dV154 */
    var live={},totalFaces=0,i,trans=[];   /* __acad3dV121 */
    A3D.lastGlAlpha={};
    for(i=0;i<A3D.objs.length;i++){
      var o=A3D.objs[i],m=meshOf(o);
      if(!m||!m.f||!m.f.length)continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(o))continue;
      live[o.id]=1;
      var rec=G.bufs[o.id];
      if(!rec||rec.meshRef!==m){
        if(rec)bimGlDisposeBuffer(G,rec);
        rec=G.bufs[o.id]=bimGlBuildObjBuffer(G,m);
      }
      totalFaces+=rec.faces;
      if(!rec.count)continue;
      /* __acad3dV121: a transparent layer's solids are drawn after every opaque one, blended and
         without writing depth, so what stands behind them shows through */
      var la=bimLayerAlpha(o);
      A3D.lastGlAlpha[o.id]=la;
      if(la<1){trans.push([o,rec,la]);continue;}
      bimGlDrawFaces(G,o,rec,1);draws++;
    }
    if(trans.length){
      gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);
      for(i=0;i<trans.length;i++){bimGlDrawFaces(G,trans[i][0],trans[i][1],trans[i][2]);draws++;}
      gl.depthMask(true);gl.disable(gl.BLEND);
    }
    // Edge outlines preserve the existing look, but only while the model is small enough that
    // they read as outlines rather than noise -- and they roughly double draw cost, so they are
    // exactly the right thing to drop first on a heavy import.
    if(totalFaces<=GL_EDGE_FACE_LIMIT){
      for(i=0;i<A3D.objs.length;i++){
        var o2=A3D.objs[i],rec2=G.bufs[o2.id];
        if(!rec2||!rec2.edge||!live[o2.id])continue;
        gl.uniform3f(G.loc.offset,o2.pos[0],o2.pos[1],o2.pos[2]);
        gl.uniform1f(G.loc.flatCol,1);
        gl.uniform1f(G.loc.pull,BIM_EDGE_PULL);   /* __acad3dV154 */
        var la2=bimLayerAlpha(o2);   /* __acad3dV121: the edges fade with their faces */
        gl.uniform1f(G.loc.alpha,la2);
        if(la2<1){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);}else gl.disable(gl.BLEND);
        if(A3D.sel===o2.id)gl.uniform3f(G.loc.color,0.306,0.631,1.0);
        else if(A3D.sel2===o2.id)gl.uniform3f(G.loc.color,1.0,0.706,0.329);
        else gl.uniform3f(G.loc.color,0.09,0.10,0.11);
        gl.bindBuffer(gl.ARRAY_BUFFER,rec2.edge);
        gl.enableVertexAttribArray(G.loc.pos);
        gl.vertexAttribPointer(G.loc.pos,3,gl.FLOAT,false,0,0);
        gl.disableVertexAttribArray(G.loc.norm);
        gl.vertexAttrib3f(G.loc.norm,0,1,0);
        gl.drawArrays(gl.LINES,0,rec2.edgeCount);draws++;
      }
      gl.disable(gl.BLEND);
      gl.uniform1f(G.loc.pull,0);
    }
    var k;
    for(k in G.bufs){
      if(G.bufs.hasOwnProperty(k)&&!live[k]){bimGlDisposeBuffer(G,G.bufs[k]);delete G.bufs[k];}
    }
    A3D.glFaces=totalFaces;
    A3D.glStats={mode:'object',draws:draws,chunks:0,rebuilt:0,rebuiltVerts:0,uploads:0,uploadBytes:0,objects:Object.keys(G.bufs).length};
    return true;
  }
  // Picking still needs screen-space polygons, but only when the user actually clicks --
  // rebuilding them every frame was the real cost, not the projection itself.
  function bimBuildPickPolys(){
    var V=camVecs(A3D.cam),W=cvW(),H=cvH(),polys=[],i,j,k;
    for(i=0;i<A3D.objs.length;i++){
      var ob=A3D.objs[i],m=meshOf(ob);if(!m)continue;
      if(!bimLayerShown(ob))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(ob))continue;
      var wv=[];
      for(j=0;j<m.v.length;j++)wv.push([m.v[j][0]+ob.pos[0],m.v[j][1]+ob.pos[1],m.v[j][2]+ob.pos[2]]);
      for(j=0;j<m.f.length;j++){
        var fc=m.f[j],pts=[],zs=0;
        for(k=0;k<fc.length;k++){var sp=toScreen(wv[fc[k]],V,W,H);pts.push(sp);zs+=sp[2];}
        polys.push({o:ob,pts:pts,z:zs/fc.length,lock:!bimLayerPickable(ob)});
      }
    }
    polys.sort(function(a,b){return b.z-a.z;});
    A3D.lastPolys=polys;
    return polys;
  }
  function paint(){
    var cv=el.cv;if(!cv||!el.ctx)return;
    A3D_LENS.cur=null;   /* __acad3dV136: the lens is worked out once per paint */
    /* __acad3dV72: scale the context by the device pixel ratio and keep every drawing call
       below in CSS pixels. Done here rather than once in size() because any ctx.setTransform
       or ctx.restore elsewhere in a frame would silently drop it, and a lost transform is a
       quarter-size drawing in the top-left corner -- loud, but only after it ships. The scratch
       canvas used for sheet capture has no __a3dScale, so this is the identity there. */
    var ctx=el.ctx,pxs=cvScale(cv);
    ctx.setTransform(pxs,0,0,pxs,0,0);
    var W=cv.width/pxs,H=cv.height/pxs,c=A3D.cam,V=camVecs(c),i,j,k;
    var capMode=!!A3D.sheetCapture;
    /* __acad3dV60: Phase 52a. Presentation mode needs per-object fill/line-weight/opacity/shadow,
       none of which the WebGL path can give (a fixed per-vertex color, GL line width mostly
       ignored/clamped to 1px by the spec, no shadow pass) -- which is exactly why the roadmap
       names native Canvas2D (createPattern/shadowBlur) for this phase rather than the GPU sink.
       So presentation mode forces the CPU polygon loop below, same as sheet-capture already does,
       rather than silently leaving WebGL in charge while presentation styling sits unreachable
       behind it. This is a real, visible trade (CPU vector-quality rendering instead of GPU-
       shaded triangles) made only when a person opts in, not a silent slowdown. */
    var glOn=(capMode||A3D.presentMode||bimPresentGraphics())?false:bimRender3D(V,W,H);   /* __acad3dV122; __acad3dV153: WebGPU or WebGL */
    if(capMode){ctx.fillStyle='#ffffff';ctx.fillRect(0,0,W,H);}
    else if(glOn){ctx.clearRect(0,0,W,H);}
    else{ctx.fillStyle='#1d2024';ctx.fillRect(0,0,W,H);}
    if(!capMode){
      if(!glOn)bimMapDraw2D(ctx,V,W,H);   /* __acad3dV132: the basemap; with WebGL on it is drawn there */
      bimMapFooterSync();
      ctx.strokeStyle='#282c31';ctx.lineWidth=1;ctx.beginPath();
      for(i=-12;i<=12;i+=2){
        var g1=toScreen([i,0,-12],V,W,H),g2=toScreen([i,0,12],V,W,H);
        ctx.moveTo(g1[0],g1[1]);ctx.lineTo(g2[0],g2[1]);
        g1=toScreen([-12,0,i],V,W,H);g2=toScreen([12,0,i],V,W,H);
        ctx.moveTo(g1[0],g1[1]);ctx.lineTo(g2[0],g2[1]);
      }
      ctx.stroke();
      /* __acad3dV110: the origin in Revit's colours and directions -- X red to the east, Y green to
         the NORTH (the model's -z), Z blue up. Before this the green line was drawn straight up
         and a blue one to the south, so the origin disagreed with the gizmo beside it. Drawn from
         one table, which a suite reads, so what is asserted is what is drawn. */
      var o0=toScreen([0,0,0],V,W,H),gzOa;
      ctx.lineWidth=1.4;
      for(gzOa=0;gzOa<A3D_ORIGIN_AXES.length;gzOa++){
        var gzOe=toScreen(A3D_ORIGIN_AXES[gzOa].to,V,W,H);
        ctx.strokeStyle=A3D_ORIGIN_AXES[gzOa].col;
        ctx.beginPath();ctx.moveTo(o0[0],o0[1]);ctx.lineTo(gzOe[0],gzOe[1]);ctx.stroke();
      }
    }
    /* __acad3dV63: in presentation mode a room's colour fill is drawn BEFORE the solids, so it
       sits under the model exactly as it now does in the vector exports -- an opaque room fill
       (possible since Phase 52a, and now hatchable) drawn last simply painted over every wall,
       column and dimension inside the room. Placed here rather than reordering the call below so
       the technical path keeps its exact existing draw order; and this is only reachable when
       presentation graphics are on, which forces glOn false (see the glOn line above), so it can
       never double-draw against the GPU path. __acad3dV122: on a sheet too. */
    drawTerrain(ctx,V,W,H);                  /* __acad3dV108: the ground, under everything */
    if(!capMode)drawSunShadows(ctx,V,W,H);   /* __acad3dV107: first, so everything else draws over it */
    if(!capMode)drawSimOverlays(ctx,V,W,H);  /* __acad3dV143: sun hours, ponds and flow lines */
    if(!capMode)bimEntDrawTurns(ctx,V,W,H);  /* __acad3dV169: the turning spaces of placed assets */
    if(!capMode)drawResultLayers(ctx,V,W,H); /* __acad3dV148: the results kept as layers, over the live ones */
    drawDiagrams(ctx,V,W,H,'under');         /* __acad3dV164: the site analysis's bands, fills and shadows */
    var presentRooms=bimPresentGraphics();   /* __acad3dV122 */
    if(presentRooms)drawRooms(ctx,V,W,H);
    var polys=[];
    if(glOn){
      // GPU drew the solids; lastPolys is rebuilt on demand by bimBuildPickPolys() when the
      // user actually clicks, which is what made the per-frame cost disappear.
      A3D.lastPolys=A3D.lastPolys||[];
    }else{
    for(i=0;i<A3D.objs.length;i++){
      var ob=A3D.objs[i],m=meshOf(ob);
      if(!m){if(ob.t==='terrain'&&ob.survey&&!bimCameraIsPlan()&&bimLayerShown(ob))bimTerrainPolys(ob,polys,V,W,H);continue;}   /* __acad3dV137 */
      if(!bimLayerShown(ob))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(ob))continue;
      var lcol=bimLensCol(ob),col=lcol||ob.col||(TYPES[ob.t]||{}).c||'#7f9db8';   /* __acad3dV136 */
      var wv=[];
      for(j=0;j<m.v.length;j++){wv.push([m.v[j][0]+ob.pos[0],m.v[j][1]+ob.pos[1],m.v[j][2]+ob.pos[2]]);}
      for(j=0;j<m.f.length;j++){
        var fc=m.f[j],pts=[],wpts=[],zs=0;
        for(k=0;k<fc.length;k++){
          var sp2=toScreen(wv[fc[k]],V,W,H);
          pts.push(sp2);zs+=sp2[2];wpts.push(wv[fc[k]]);
        }
        polys.push({o:ob,pts:pts,z:zs/fc.length,n:faceNormal(wpts),col:col,lens:!!lcol,lock:!bimLayerPickable(ob),la:bimLayerAlpha(ob)});   /* __acad3dV121, __acad3dV136 */
      }
    }
    polys.sort(function(a,b){return b.z-a.z;});
    /* __acad3dV60: Phase 52a -- Presentation mode consumes the Phase 51 graphic override data
       (fill, line color/weight, opacity, shadow) here, in the one face-draw loop every solid
       (wall/floor/ceiling/column/roof/stair/door/window) already funnels through. Deliberately
       OFF by default (A3D.presentMode starts false) -- when off, this whole block is skipped and the
       loop is BYTE-IDENTICAL to before this phase, so nobody sees any change unless they opt in.
       __acad3dV122: a sheet's viewports take it too, in the appearance the sheet is plotted in;
       they were left technical, and a sheet printed in one appearance showed in the other.
       Hatch PATTERN rendering is deliberately NOT consumed here -- the roadmap's own phase split
       puts "wires hatch/pattern into the BIM render" in Phase 53, not this one. */
    var presentOn=bimPresentGraphics();   /* __acad3dV122 */
    for(i=0;i<polys.length;i++){
      var pl=polys[i],kk=0.45+0.55*Math.abs(vdot(pl.n,LIGHT));
      if(!capMode&&A3D.sel===pl.o.id)kk=Math.min(1.35,kk+0.25);
      ctx.beginPath();ctx.moveTo(pl.pts[0][0],pl.pts[0][1]);
      for(j=1;j<pl.pts.length;j++)ctx.lineTo(pl.pts[j][0],pl.pts[j][1]);
      ctx.closePath();
      var rg=presentOn?bimResolveGraphics(pl.o,'presentation'):null;
      /* __acad3dV122: a canvas does not scale a shadow with its transform, so it is given in the
         canvas's own pixels -- the drawing's times its scale (pxs) */
      if(rg&&rg.shadow){ctx.shadowColor='rgba(0,0,0,0.45)';ctx.shadowBlur=10*pxs;ctx.shadowOffsetX=3*pxs;ctx.shadowOffsetY=4*pxs;}
      var baseFill=pl.lens?pl.col:((rg&&rg.fill!=='none')?rg.fill:pl.col);   /* __acad3dV136: the lens over Presentation's fill */
      ctx.fillStyle=shade(baseFill,kk);
      ctx.globalAlpha=pl.la*(rg?rg.opacity:1);   /* __acad3dV121: the layer's transparency */
      ctx.fill();
      if(rg&&rg.shadow){ctx.shadowColor='transparent';ctx.shadowBlur=0;ctx.shadowOffsetX=0;ctx.shadowOffsetY=0;}
      /* __acad3dV63 (Phase 53): the hatch goes on as a second fill of the SAME path, after the
         base fill and after the shadow has been cleared -- so the pattern sits on top of the
         object's own colour (a hatch is drawn over a poche, not instead of it) and does not get a
         drop shadow of its own, which would smear it. Skipped entirely when pattern is 'none',
         which is every object in every project that predates this phase. */
      var patFill=rg?bimCanvasPatternFill(ctx,rg):null;
      if(patFill){ctx.fillStyle=patFill;ctx.fill();}
      var baseStroke=capMode?(rg?rg.lineColor:'rgba(0,0,0,0.55)'):((A3D.sel===pl.o.id)?'#4ea1ff':((A3D.sel2===pl.o.id)?'#ffb454':(rg?rg.lineColor:'rgba(0,0,0,0.35)')));   /* __acad3dV122 */
      var baseLW=(!capMode&&(A3D.sel===pl.o.id||A3D.sel2===pl.o.id))?1.4:(rg?Math.max(0.3,Math.min(6,rg.lineWeight*BIM_LW_TO_PX)):0.7);
      ctx.strokeStyle=baseStroke;
      ctx.lineWidth=baseLW;
      ctx.stroke();
      ctx.globalAlpha=1;
      /* __acad3dV60: test-observable record of what was actually drawn for this face, read back
         via window.__a3dLastDrawStyle -- avoids fragile pixel/canvas sampling in the regression
         suite by exposing the exact style decision paint() made, not a rendered approximation of it. */
      pl.rBaseFill=baseFill;pl.rStroke=baseStroke;pl.rLineWidth=baseLW;pl.rOpacity=rg?rg.opacity:1;pl.rShadow=!!(rg&&rg.shadow);
      pl.rLayerAlpha=pl.la;   /* __acad3dV121 */
      // __acad3dV63: what the hatch actually resolved to, recorded the same way and for the same
      // reason as the fields above -- the suite asserts the decision, not sampled pixels.
      pl.rPattern=(rg&&patFill)?rg.pattern:'none';
      pl.rPatternColor=(rg&&patFill)?(rg.patternColor||'#555555'):null;
      pl.rPatternScale=(rg&&patFill)?(rg.patternScale||1):null;
    }
    A3D.lastPolys=polys;
    }
    drawGrids(ctx,V,W,H);
    drawDataLayers(ctx,V,W,H);     /* __acad3dV134: the public record, under the property lines */
    drawProperties(ctx,V,W,H);     /* __acad3dV103: under the model, like grids */
    drawAlignments(ctx,V,W,H);     /* __acad3dV127 */
    drawStationMark(ctx,V,W,H);
    drawHatches(ctx,V,W,H);        /* __acad3dV96: under the linework, as AutoCAD draws it */
    drawClines(ctx,V,W,H);         /* __acad3dV94: construction geometry, under the model */
    drawSketches(ctx,V,W,H);
    if(!presentRooms)drawRooms(ctx,V,W,H);
    drawDims(ctx,V,W,H);
    drawTextLabels(ctx,V,W,H);
    drawRoomTags(ctx,V,W,H);       /* __acad3dV101 */
    drawTribAreas(ctx,V,W,H);          /* __acad3dV106 */
    drawStructResults(ctx,V,W,H);      /* __acad3dV125: the analysis display */
    drawDiagrams(ctx,V,W,H,'over');    /* __acad3dV164: the site analysis's lines, symbols and words */
    drawAreaPlan(ctx,V,W,H);           /* __acad3dV105b */
    drawSunPath(ctx,V,W,H);            /* __acad3dV107 */
    drawRoomSchemeLegend(ctx,V,W,H);   /* __acad3dV105: the colour fill's legend, from what drawRooms just drew */
    drawLensLegend(ctx,V,W,H);         /* __acad3dV136: the lens's and the data layers' legend, below it */
    drawDiagramLegend(ctx,V,W,H);      /* __acad3dV164: the site analysis's, at the top right */
    drawNotes(ctx,V,W,H);          // __acad3dV82: the annotation overlay, above the model
    if(!capMode)drawSkLivePreview(ctx,V,W,H);   /* __acad3dV122: a tool's rubber band is not on the paper */
    if(!capMode){
      var faceNow=bimFaceCurrent();   /* __acad3dV123: read first, so a face that has lapsed lets the gizmo back */
      bimDrawGrips(ctx,V,W,H);
      bimDrawGizmo(ctx,V,W,H);   // __acad3dV76: after grips, so an arm never hides a grip
      bimDrawFaceMode(ctx,V,W,H,faceNow);
      drawNorthArrow(ctx,V,W,H);   /* __acad3dV103 */
      drawMarqueeRect(ctx);
      drawZoomWindow(ctx);          // __acad3dV83
      if(!A3D.flat)drawCube(ctx,W,H,V);
      else{A3D.cubePolys=[];A3D.homeRect=null;}   /* __acad3dV119: not drawn, not clickable */
      bimSyncTouchLenInput();
    }
    if(!capMode)bimAnimSync();   /* __acad3dV170: Play and Pause, shown when something can move */
    A3D.frames++;
  }

  var CORN=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]];
  var CFACES=[
    {n:'top',f:[7,6,2,3]},{n:'bottom',f:[0,1,5,4]},
    {n:'front',f:[4,5,6,7]},{n:'back',f:[1,0,3,2]},
    {n:'right',f:[5,1,2,6]},{n:'left',f:[0,4,7,3]}
  ];
