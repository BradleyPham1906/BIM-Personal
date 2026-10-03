"""patch_phase137a.py -- V137: the map on 3D terrain.

- A terrain surface (V108) is drawn in 3D: its TIN as a shaded GL mesh, smooth normals, in the
  surface's colour. Plan views keep V108's contours (and the flat basemap).
- With the map on, the basemap is draped over it: the tiles over the surface's area, at the view's
  zoom (lowered while more than 36 would be needed), each drawn over the whole mesh with its
  texture placed by every vertex's Web Mercator position and anything outside the tile discarded. A
  tile still loading shows its loaded parent, stretched, as on the flat map.
- The 2D renderer draws the surface's triangles, shaded, in 3D views.
- Context buildings stand on the terrain (a Site Context setting, on unless turned off): each is
  raised to the lowest terrain height under its footprint, when a fetch places it and when the
  setting changes, in one undo step."""
NAME = 'patch_phase137a.py'
BASE = '170a93b676579f1451db50f0eda126ad6ee716133b69a164a259fd3f5892bd78'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def esc(s):
    return ''.join(ch if ord(ch) < 128 else '\\u%04x' % ord(ch) for ch in s)


def rep(old, new, n=1):
    global t
    new = esc(new)
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


ENGINE = r"""  /* ================= __acad3dV137: the map on 3D terrain ================= */
  var BIM_DRAPE_ZREF=22,BIM_DRAPE_MAXT=36;
  /* the height of a TIN at a plan point, or null outside it */
  function bimTinHeightAt(tin,x,z){
    var t,tr,A,B,C,d,l1,l2,l3;
    for(t=0;t<tin.tris.length;t++){
      tr=tin.tris[t];A=tin.P[tr[0]];B=tin.P[tr[1]];C=tin.P[tr[2]];
      d=(B[1]-C[1])*(A[0]-C[0])+(C[0]-B[0])*(A[1]-C[1]);
      if(Math.abs(d)<1e-12)continue;
      l1=((B[1]-C[1])*(x-C[0])+(C[0]-B[0])*(z-C[1]))/d;
      l2=((C[1]-A[1])*(x-C[0])+(A[0]-C[0])*(z-C[1]))/d;
      l3=1-l1-l2;
      if(l1>=-1e-9&&l2>=-1e-9&&l3>=-1e-9)return l1*tin.H[tr[0]]+l2*tin.H[tr[1]]+l3*tin.H[tr[2]];
    }
    return null;
  }
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
        fp=o.context.footprint||[];h=null;
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
  function bimTerrainGlMesh(G,T,o,org){
    var tin=bimTerrainTin(o),tn=bimTrueNorthDeg(),key,rec=T.bufs[o.id],gl=G.gl,i,k,tr,nrm,pos=[],nor=[],mer=[],A,B,C,ux,uy,uz,vx,vy,vz,nx,ny,nz,L;
    if(!tin||!tin.tris.length)return null;
    key=(o.rev||0)+':'+o.survey.length+':'+(o.pos||[0,0,0]).join(',')+':'+tn+':'+(org?org.lat+','+org.lon:'-');
    if(rec&&rec.key===key)return rec;
    if(rec){gl.deleteBuffer(rec.pos);gl.deleteBuffer(rec.nor);gl.deleteBuffer(rec.mer);}
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
    function mk(a){var b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(a),gl.STATIC_DRAW);return b;}
    var lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,g;
    if(org)for(i=0;i<tin.P.length;i++){g=bimModelToGeo(tin.P[i][0],tin.P[i][1],org);lo0=Math.min(lo0,g[0]);lo1=Math.max(lo1,g[0]);la0=Math.min(la0,g[1]);la1=Math.max(la1,g[1]);}
    rec=T.bufs[o.id]={key:key,pos:mk(pos),nor:mk(nor),mer:mk(mer),count:pos.length/3,ox:ox,oy:oy,ext:org?[lo0,la0,lo1,la1]:null};
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
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(o.t==='terrain'&&o.survey&&bimLayerShown(o))list.push(o);}
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
"""

rep("""  function bimGlRender(V,W,H){""", ENGINE + """  function bimGlRender(V,W,H){""")
rep("""    bimMapDrawGl(G,V,W,H);   /* __acad3dV132: the basemap, under everything */""",
    """    bimMapDrawGl(G,V,W,H);   /* __acad3dV132: the basemap, under everything */
    bimTerrainDrawGl(G,V,W,H);   /* __acad3dV137: the terrain in 3D, the map draped on it */""")
rep("""      var ob=A3D.objs[i],m=meshOf(ob);if(!m)continue;
      if(!bimLayerShown(ob))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(ob))continue;
      var lcol=""", """      var ob=A3D.objs[i],m=meshOf(ob);
      if(!m){if(ob.t==='terrain'&&ob.survey&&!bimCameraIsPlan()&&bimLayerShown(ob))bimTerrainPolys(ob,polys,V,W,H);continue;}   /* __acad3dV137 */
      if(!bimLayerShown(ob))continue;   /* __acad3dV121 */
      if(!bimObjectVisibleOnLevel(ob))continue;
      var lcol=""")
# the setting
rep("""    return {radius:(typeof c.radius==='number'&&c.radius>=50&&c.radius<=1000)?c.radius:150,kinds:k,
      overpass:(typeof c.overpass==='string'&&c.overpass)?c.overpass:BIM_OVERPASS_URL};""",
    """    return {radius:(typeof c.radius==='number'&&c.radius>=50&&c.radius<=1000)?c.radius:150,kinds:k,
      overpass:(typeof c.overpass==='string'&&c.overpass)?c.overpass:BIM_OVERPASS_URL,
      onGround:c.onGround!==false};   /* __acad3dV137: buildings on the terrain */""")
rep("""      if(nv===st.overpass)return true;
    }else return false;""", """      if(nv===st.overpass)return true;
    }else if(field==='onGround'){   /* __acad3dV137 */
      nv=!!val&&val!=='false'&&val!=='0';
      if(nv===st.onGround)return true;
    }else return false;""")
rep("""    if(kk){A3D.site.context.kinds=A3D.site.context.kinds||{};A3D.site.context.kinds[kk]=nv;}
    else A3D.site.context[field]=nv;
    refreshProps();saveSoon();""", """    if(kk){A3D.site.context.kinds=A3D.site.context.kinds||{};A3D.site.context.kinds[kk]=nv;}
    else A3D.site.context[field]=nv;
    if(field==='onGround'){   /* __acad3dV137: in the same undo step */
      var nst=bimCtxStand(nv);paint();
      a3dToast(nv?(nst?'Context buildings stand on the terrain: '+nst:'No context terrain to stand the buildings on: get it with CONTEXT'):'Context buildings back on the level');
    }
    refreshProps();saveSoon();""")
rep("""      A3D.site.context=A3D.site.context||{};
      A3D.site.context.last={date:date,counts:n,""", """      if(st.onGround)bimCtxStand(true);   /* __acad3dV137: the buildings on the terrain */
      A3D.site.context=A3D.site.context||{};
      A3D.site.context.last={date:date,counts:n,""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
