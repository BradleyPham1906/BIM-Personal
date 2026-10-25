  /* ================= __acad3dV132: the map =================
     A basemap under the plan and the 3D ground: OpenStreetMap's street map, Esri's imagery, or the
     owner's own tiles. It is off until someone turns it on, so the app asks the network for nothing
     until asked. The site's latitude and longitude (V107) are model 0,0, as V108's survey base point
     is, and true north (V103) turns the model on the map. */
  var BIM_MAP_STYLES={
    /* __acad3dV133d: CARTO's Voyager, OSM's data. OpenStreetMap's own tile servers refuse a request
       with no Referer, which is every request from a page opened as a file. */
    /* __acad3dV133f: Esri's World Street Map. OSM's own servers answer a page opened as a file with
       "Access blocked" tiles, and CARTO's with "API KEY REQUIRED"; Esri's serve it, keyless. */
    street:{name:'Street (Esri World Street Map)',url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',maxz:19,
      credit:'Map: Esri, HERE, Garmin, USGS, \u00a9 OpenStreetMap contributors, and the GIS User Community',link:'https://www.arcgis.com/home/item.html?id=3b93337983e9436f8db950e38a8629af'},
    satellite:{name:'Satellite (Esri World Imagery)',url:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',maxz:19,
      credit:'Imagery: Esri, Maxar, Earthstar Geographics, and the GIS User Community',link:'https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a9'},
    custom:{name:'Custom tiles',url:'',maxz:19,credit:'',link:''}
  };
  var BIM_MAP_ORDER=['off','street','satellite','custom'];
  var BIM_MAP_MAXT=80,BIM_MAP_INFLIGHT=12,BIM_MAP_CACHE=400;
  var A3D_MAP={cache:{},n:0,inflight:0,frame:0,fail:{},rp:0,footKey:null};
  var BIM_WGS84_A=6378137,BIM_WGS84_E2=0.00669437999014,BIM_D2R=Math.PI/180;
  function bimMapSettings(){
    var m=(A3D.site&&A3D.site.map)||{};
    return {style:BIM_MAP_STYLES[m.style]?m.style:'off',
      opacity:(typeof m.opacity==='number'&&m.opacity>=0.1&&m.opacity<=1)?m.opacity:1,
      url:typeof m.url==='string'?m.url:'',credit:typeof m.credit==='string'?m.credit:''};
  }
  /* where the site is, or null while its latitude and longitude are not both set */
  function bimMapOrigin(){
    var s=bimSunSettings();
    if(!bimSunNum(s.lat)||!bimSunNum(s.lon))return null;
    return {lat:s.lat,lon:s.lon};
  }
  /* the ellipsoid's radii at a latitude: M along the meridian, N across it */
  function bimGeoRadii(lat){
    var s=Math.sin(lat*BIM_D2R),w=1-BIM_WGS84_E2*s*s;
    return {M:BIM_WGS84_A*(1-BIM_WGS84_E2)/Math.pow(w,1.5),N:BIM_WGS84_A/Math.sqrt(w)};
  }
  /* a model plan point (x, z) as [longitude, latitude]; null with no site place. A true azimuth az
     points along model (sin(az+tn), -cos(az+tn)), so east is (cos tn, sin tn), north (sin tn, -cos tn). */
  function bimModelToGeo(x,z,org){
    org=org||bimMapOrigin();
    if(!org)return null;
    var t=bimTrueNorthDeg()*BIM_D2R,c=Math.cos(t),s=Math.sin(t),R=bimGeoRadii(org.lat);
    var E=x*c+z*s,N=x*s-z*c;
    return [org.lon+E/(R.N*Math.cos(org.lat*BIM_D2R))/BIM_D2R,org.lat+N/R.M/BIM_D2R];
  }
  function bimGeoToModel(lon,lat,org){
    org=org||bimMapOrigin();
    if(!org)return null;
    var t=bimTrueNorthDeg()*BIM_D2R,c=Math.cos(t),s=Math.sin(t),R=bimGeoRadii(org.lat);
    var dl=lon-org.lon;
    dl=((dl+180)%360+360)%360-180;
    var E=dl*BIM_D2R*R.N*Math.cos(org.lat*BIM_D2R),N=(lat-org.lat)*BIM_D2R*R.M;
    return [E*c+N*s,E*s-N*c];
  }
  /* Web Mercator, on the slippy-map tile scheme every free tile server uses */
  function bimSinh(v){return (Math.exp(v)-Math.exp(-v))/2;}
  function bimLonToTileX(lon,z){return (lon+180)/360*Math.pow(2,z);}
  function bimLatToTileY(lat,z){
    var la=Math.max(-85.05112878,Math.min(85.05112878,lat))*BIM_D2R;
    return (1-Math.log(Math.tan(la)+1/Math.cos(la))/Math.PI)/2*Math.pow(2,z);
  }
  function bimTileXToLon(x,z){return x/Math.pow(2,z)*360-180;}
  function bimTileYToLat(y,z){return Math.atan(bimSinh(Math.PI*(1-2*y/Math.pow(2,z))))/BIM_D2R;}
  /* the URL template in force: '' for a custom style with no URL yet */
  function bimMapTemplate(st){
    st=st||bimMapSettings();
    if(st.style==='custom')return st.url;
    return BIM_MAP_STYLES[st.style]?BIM_MAP_STYLES[st.style].url:'';
  }
  function bimMapCredit(st){
    st=st||bimMapSettings();
    if(st.style==='custom')return st.credit;
    return BIM_MAP_STYLES[st.style]?BIM_MAP_STYLES[st.style].credit:'';
  }
  function bimMapTileUrl(tpl,x,y,z){
    var n=Math.pow(2,z),xx=((x%n)+n)%n;
    return tpl.split('{z}').join(String(z)).split('{x}').join(String(xx)).split('{y}').join(String(y))
      .split('{r}').join(bimMapDpr()>1.5?'@2x':'');   /* __acad3dV133d */
  }
  /* __acad3dV133d: the screen's density, 1 to 2 */
  function bimMapDpr(){var d=window.devicePixelRatio||1;return d>2?2:(d<1?1:d);}
  function bimMapHost(url){var m=/^[a-z]+:\/\/([^\/?#]+)/i.exec(url||'');return m?m[1]:'the tile server';}
  /* The tiles a view needs. The zoom is the view's metres per pixel -- exact in plan, and at the
     target in 3D -- lowered while the view would need more than BIM_MAP_MAXT tiles. The extent is the
     screen on the ground: the corners in plan; in 3D a grid of points, any past three camera
     distances from the target pulled in to it, so a view toward the horizon does not ask for the world. */
  function bimMapPlan(V,W,H){
    var st=bimMapSettings(),org=bimMapOrigin(),tpl=bimMapTemplate(st),r={style:st.style,z:null,tiles:[],reason:''};
    if(st.style==='off'){r.reason='off';return r;}
    if(!org){r.reason='place';return r;}
    if(!tpl){r.reason='url';return r;}
    var g=bimShadowGround(),pts=[],i,j,p,c=A3D.cam;
    if(A3D.flat){
      var cs=[[0,0],[W,0],[0,H],[W,H],[W/2,H/2]];
      for(i=0;i<cs.length;i++){p=groundPoint(cs[i][0],cs[i][1],g);if(p)pts.push(p);}
    }else{
      var tg=[c.tx,g,c.tz],R=Math.max(50,c.dist*3);
      pts.push(tg);
      for(i=0;i<=6;i++)for(j=0;j<=6;j++){
        p=groundPoint(W*i/6,H*j/6,g);
        if(!p)continue;
        var dx=p[0]-tg[0],dz=p[2]-tg[2],d=Math.sqrt(dx*dx+dz*dz);
        if(d>R)p=[tg[0]+dx*R/d,g,tg[2]+dz*R/d];
        pts.push(p);
      }
      if(pts.length<4)pts.push([tg[0]-R,g,tg[2]-R],[tg[0]+R,g,tg[2]+R],[tg[0]-R,g,tg[2]+R],[tg[0]+R,g,tg[2]-R]);
    }
    if(!pts.length){r.reason='side';return r;}   /* an elevation or a section looks along the ground: no ray meets it */
    var lo0=Infinity,lo1=-Infinity,la0=Infinity,la1=-Infinity,q;
    for(i=0;i<pts.length;i++){
      q=bimModelToGeo(pts[i][0],pts[i][2],org);
      lo0=Math.min(lo0,q[0]);lo1=Math.max(lo1,q[0]);la0=Math.min(la0,q[1]);la1=Math.max(la1,q[1]);
    }
    var mpp=Math.max(c.dist,0.5)/(H*1.2),maxz=BIM_MAP_STYLES[st.style].maxz;
    var dz=tpl.indexOf('{r}')>=0?1:bimMapDpr(),maxT=Math.round(BIM_MAP_MAXT*bimMapDpr());   /* __acad3dV133d */
    var z=Math.round(Math.log(156543.03392*Math.cos(org.lat*BIM_D2R)*dz/mpp)/Math.LN2),x0,x1,y0,y1,n;
    z=Math.max(1,Math.min(maxz,z));
    for(;;){
      n=Math.pow(2,z);
      x0=Math.floor(bimLonToTileX(lo0,z));x1=Math.floor(bimLonToTileX(lo1,z));
      y0=Math.max(0,Math.floor(bimLatToTileY(la1,z)));y1=Math.min(n-1,Math.floor(bimLatToTileY(la0,z)));
      if((x1-x0+1)*(y1-y0+1)<=maxT||z<=1)break;
      z--;
    }
    var cx=bimLonToTileX((lo0+lo1)/2,z),cy=bimLatToTileY((la0+la1)/2,z),T=[],x,y;
    for(y=y0;y<=y1;y++)for(x=x0;x<=x1;x++)T.push({x:x,y:y,z:z,k:(x+0.5-cx)*(x+0.5-cx)+(y+0.5-cy)*(y+0.5-cy)});
    T.sort(function(a,b){return a.k-b.k;});
    r.z=z;r.tiles=T;r.tpl=tpl;r.org=org;r.ground=g;r.opacity=st.opacity*(bimAwLook()?bimAwLook().fade:1);r.extent=[lo0,la0,lo1,la1];r.mpp=mpp;
    return r;
  }
  /* a tile's four corners on the model, at elevation y */
  function bimMapTileCorners(t,org,y){
    function C(tx,ty){var m=bimGeoToModel(bimTileXToLon(tx,t.z),bimTileYToLat(ty,t.z),org);return [m[0],y,m[1]];}
    return {nw:C(t.x,t.y),ne:C(t.x+1,t.y),se:C(t.x+1,t.y+1),sw:C(t.x,t.y+1)};
  }
  /* ---- the tile store ---- */
  function bimMapRepaintSoon(){
    if(A3D_MAP.rp)return;
    A3D_MAP.rp=setTimeout(function(){A3D_MAP.rp=0;try{if(A3D.on)paint();}catch(eP){console.warn('[BIM] map repaint',eP);}},40);
  }
  /* the stored tile; asked for when ask is set and there is room in flight */
  function bimMapEntry(t,tpl,ask){
    var url=bimMapTileUrl(tpl,t.x,t.y,t.z),e=A3D_MAP.cache[url];
    if(e){e.seen=A3D_MAP.frame;return e;}
    if(!ask||A3D_MAP.inflight>=BIM_MAP_INFLIGHT)return null;
    e={url:url,host:bimMapHost(url),state:'loading',img:new Image(),tex:null,texGl:null,seen:A3D_MAP.frame};
    A3D_MAP.cache[url]=e;A3D_MAP.n++;A3D_MAP.inflight++;
    /* asked with CORS, so a server that does not allow browser access fails here, rather than
       tainting the canvas or reaching the GPU */
    e.img.crossOrigin='anonymous';
    e.img.onload=function(){if(e.state!=='loading')return;e.state='ok';A3D_MAP.inflight--;bimMapRepaintSoon();};
    e.img.onerror=function(){
      if(e.state!=='loading')return;
      e.state='fail';A3D_MAP.inflight--;
      A3D_MAP.fail[e.host]=(A3D_MAP.fail[e.host]||0)+1;
      bimMapRepaintSoon();
    };
    e.img.src=url;
    return e;
  }
  function bimMapDrop(e){
    if(e.tex&&e.texGl){try{e.texGl.deleteTexture(e.tex);}catch(eD){}}
    e.tex=null;e.texGl=null;
    if(e.gtx){try{e.gtx.tex.destroy();}catch(eG){}if(e.gtx.dev===A3D_GPU.device)A3D_GPU.tileLive--;e.gtx=null;}   /* __acad3dV154 */
    if(e.state==='loading'){e.state='dropped';A3D_MAP.inflight=Math.max(0,A3D_MAP.inflight-1);}
    if(A3D_MAP.cache[e.url]===e){delete A3D_MAP.cache[e.url];A3D_MAP.n--;}
  }
  /* the least recently drawn go first; a tile still loading is kept */
  function bimMapEvict(){
    if(A3D_MAP.n<=BIM_MAP_CACHE)return;
    var L=[],k;
    for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)&&A3D_MAP.cache[k].state!=='loading')L.push(A3D_MAP.cache[k]);
    L.sort(function(a,b){return a.seen-b.seen;});
    for(k=0;k<L.length&&A3D_MAP.n>BIM_MAP_CACHE;k++)bimMapDrop(L[k]);
  }
  /* a new style or URL tries again what failed */
  function bimMapForgetFailures(){
    var k,L=[];
    for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)&&A3D_MAP.cache[k].state==='fail')L.push(A3D_MAP.cache[k]);
    for(k=0;k<L.length;k++)bimMapDrop(L[k]);
    A3D_MAP.fail={};A3D_MAP.footKey=null;
  }
  /* what to draw for a tile: the tile, or while it loads the nearest parent loaded, stretched */
  function bimMapSource(t,tpl){
    var e=bimMapEntry(t,tpl,true),d,s,px,py;
    if(e&&e.state==='ok')return {e:e,u0:0,v0:0,u1:1,v1:1,up:0};
    for(d=1;d<=4&&t.z-d>=0;d++){
      s=Math.pow(2,d);px=Math.floor(t.x/s);py=Math.floor(t.y/s);
      e=bimMapEntry({x:px,y:py,z:t.z-d},tpl,false);
      if(e&&e.state==='ok')return {e:e,u0:(t.x-px*s)/s,v0:(t.y-py*s)/s,u1:(t.x-px*s+1)/s,v1:(t.y-py*s+1)/s,up:d};
    }
    return null;
  }
  function bimMapRecord(path,plan,drawn,srcs){
    A3D.lastMapDrawn={path:path,style:plan.style,reason:plan.reason,z:plan.z,mpp:plan.mpp||null,extent:plan.extent||null,
      tiles:plan.tiles.map(function(t,i){return {x:t.x,y:t.y,z:t.z,up:srcs[i]?srcs[i].up:null};}),
      drawn:drawn,inflight:A3D_MAP.inflight,cached:A3D_MAP.n};
  }
  /* ---- drawing: WebGL ---- */
  function bimMapGlProg(G){
    if(G.map)return G.map.prog?G.map:null;
    var gl=G.gl;
    G.map={prog:null};
    var vs=bimGlCompile(gl,gl.VERTEX_SHADER,'attribute vec3 aPos;attribute vec2 aUV;uniform mat4 uView;uniform mat4 uProj;varying vec2 vUV;'+
      'void main(){vUV=aUV;gl_Position=uProj*uView*vec4(aPos,1.0);}');
    /* the opacity mixes the tile toward the background, so no blending state is needed */
    var fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,'precision mediump float;uniform sampler2D uTex;uniform float uAlpha;uniform vec3 uBg;uniform float uGrey;varying vec2 vUV;'+
      'void main(){vec3 c=texture2D(uTex,vUV).rgb;c=mix(c,vec3(dot(c,vec3(0.299,0.587,0.114))),uGrey);gl_FragColor=vec4(mix(uBg,c,uAlpha),1.0);}');   /* __acad3dV171b: the ground, and grey */
    if(!vs||!fs)return null;
    var p=gl.createProgram();
    gl.attachShader(p,vs);gl.attachShader(p,fs);gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS)){console.warn('[BIM] map shader link failed: '+gl.getProgramInfoLog(p));return null;}
    G.map={prog:p,buf:gl.createBuffer(),pos:gl.getAttribLocation(p,'aPos'),uv:gl.getAttribLocation(p,'aUV'),
      view:gl.getUniformLocation(p,'uView'),proj:gl.getUniformLocation(p,'uProj'),
      tex:gl.getUniformLocation(p,'uTex'),alpha:gl.getUniformLocation(p,'uAlpha'),bg:gl.getUniformLocation(p,'uBg'),grey:gl.getUniformLocation(p,'uGrey')};
    return G.map;
  }
  function bimMapTex(gl,e){
    if(e.tex&&e.texGl===gl)return e.tex;
    var tx=null;
    try{
      tx=gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D,tx);
      gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,e.img);
      /* __acad3dV133d: mipmaps, so a tile drawn smaller than its pixels is filtered, not sparkling */
      var tw=e.img.naturalWidth||e.img.width,th=e.img.naturalHeight||e.img.height;
      if(tw&&th&&!(tw&(tw-1))&&!(th&(th-1))){gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);e.mip=true;}
      else gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    }catch(eT){
      /* a tile the browser will not hand to the GPU: counted against its host, not drawn */
      if(tx)gl.deleteTexture(tx);
      e.state='fail';A3D_MAP.fail[e.host]=(A3D_MAP.fail[e.host]||0)+1;
      return null;
    }
    e.tex=tx;e.texGl=gl;
    return tx;
  }
  /* One quad per tile on the lowest level's plane, just under it, drawn first and without writing
     depth, so every solid draws over it; the solids' own matrices, so the two cannot drift apart. */
  function bimMapDrawGl(G,V,W,H){
    if(A3D_PLOT.on)return;
    A3D_MAP.frame++;
    var plan=bimMapPlan(V,W,H),srcs=[],drawn=0,i;
    var P=plan.tiles.length?bimMapGlProg(G):null,gl=G.gl;
    if(P){
      gl.useProgram(P.prog);
      gl.uniformMatrix4fv(P.view,false,bimGlViewMatrix(V));
      gl.uniformMatrix4fv(P.proj,false,bimGlProjMatrix(W,H,A3D.flat,A3D.cam.dist));
      gl.uniform1f(P.alpha,plan.opacity);
      var awM=bimAwBg(),awL=bimAwLook();gl.uniform3f(P.bg,awM[0],awM[1],awM[2]);gl.uniform1f(P.grey,awL?awL.grey:0);   /* __acad3dV171b */
      gl.activeTexture(gl.TEXTURE0);gl.uniform1i(P.tex,0);
      gl.depthMask(false);
      gl.bindBuffer(gl.ARRAY_BUFFER,P.buf);
      gl.enableVertexAttribArray(P.pos);gl.enableVertexAttribArray(P.uv);
      gl.vertexAttribPointer(P.pos,3,gl.FLOAT,false,20,0);
      gl.vertexAttribPointer(P.uv,2,gl.FLOAT,false,20,12);
      for(i=0;i<plan.tiles.length;i++){
        var s=bimMapSource(plan.tiles[i],plan.tpl),tex=s?bimMapTex(gl,s.e):null;
        srcs.push(tex?s:null);
        if(!tex)continue;
        var k=bimMapTileCorners(plan.tiles[i],plan.org,plan.ground-0.02);
        gl.bindTexture(gl.TEXTURE_2D,tex);
        gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([
          k.nw[0],k.nw[1],k.nw[2],s.u0,s.v0, k.ne[0],k.ne[1],k.ne[2],s.u1,s.v0, k.se[0],k.se[1],k.se[2],s.u1,s.v1,
          k.nw[0],k.nw[1],k.nw[2],s.u0,s.v0, k.se[0],k.se[1],k.se[2],s.u1,s.v1, k.sw[0],k.sw[1],k.sw[2],s.u0,s.v1]),gl.DYNAMIC_DRAW);
        gl.drawArrays(gl.TRIANGLES,0,6);
        drawn++;
      }
      gl.disableVertexAttribArray(P.pos);gl.disableVertexAttribArray(P.uv);
      gl.bindTexture(gl.TEXTURE_2D,null);
      gl.depthMask(true);
    }
    bimMapRecord('gl',plan,drawn,srcs);
    bimMapEvict();
  }
  /* ---- drawing: the 2D canvas (the presentation appearance, and the renderer without WebGL). In
     plan each tile is an image under an affine transform from three of its corners; a canvas has no
     perspective texture, so in 3D this renderer draws no map. ---- */
  function bimMapDraw2D(ctx,V,W,H){
    if(A3D_PLOT.on)return;
    A3D_MAP.frame++;
    var plan=bimMapPlan(V,W,H),srcs=[],drawn=0,i,pxs=cvScale(el.cv);
    if(!A3D.flat&&plan.tiles.length){plan.tiles=[];plan.reason='3d';}
    if(plan.tiles.length){
      ctx.save();
      ctx.globalAlpha=plan.opacity;
      if(bimAwLook())ctx.filter='grayscale(1)';   /* __acad3dV171b */
      for(i=0;i<plan.tiles.length;i++){
        var s=bimMapSource(plan.tiles[i],plan.tpl);
        srcs.push(s);
        if(!s)continue;
        var k=bimMapTileCorners(plan.tiles[i],plan.org,plan.ground),a=toScreen(k.nw,V,W,H),b=toScreen(k.ne,V,W,H),d=toScreen(k.sw,V,W,H);
        var iw=s.e.img.naturalWidth||256,ih=s.e.img.naturalHeight||256;
        ctx.setTransform(pxs*(b[0]-a[0]),pxs*(b[1]-a[1]),pxs*(d[0]-a[0]),pxs*(d[1]-a[1]),pxs*a[0],pxs*a[1]);
        try{ctx.drawImage(s.e.img,s.u0*iw,s.v0*ih,(s.u1-s.u0)*iw,(s.v1-s.v0)*ih,-0.002,-0.002,1.004,1.004);drawn++;}
        catch(eI){srcs[i]=null;}
      }
      ctx.restore();
    }
    bimMapRecord('2d',plan,drawn,srcs);
    bimMapEvict();
  }
  /* the credit line, and what did not load and from where: written only when it changes */
  function bimMapFooterHtml(){
    var st=bimMapSettings(),h='',k,bad=[];
    if(st.style==='off')return '';
    if(!bimMapOrigin())return '<span class="a3d-mapwarn">Map: set the site latitude and longitude, or find an address</span>';
    if(!bimMapTemplate(st))return '<span class="a3d-mapwarn">Map: give the custom tile URL</span>';
    var sd=BIM_MAP_STYLES[st.style],cr=bimMapCredit(st);
    h=(st.style!=='custom'&&sd.link)?('<a href="'+bimEsc(sd.link)+'" target="_blank" rel="noopener">'+bimEsc(cr)+'</a>')
      :bimEsc(cr||'Custom tiles: no credit given');
    for(k in A3D_MAP.fail)if(A3D_MAP.fail.hasOwnProperty(k))
      bad.push(k+': '+A3D_MAP.fail[k]+' tile'+(A3D_MAP.fail[k]===1?'':'s')+' did not load (offline, or the server does not allow browser access)');
    if(bad.length)h+=' <span class="a3d-mapwarn">'+bimEsc(bad.join('; '))+'</span>';
    return h;
  }
  function bimMapFooterSync(){
    var f=document.getElementById('a3d-mapattr');
    if(!f)return;
    var h=bimMapFooterHtml(),cc=bimCtxCreditHtml(h.indexOf('OpenStreetMap contributors')>=0);   /* __acad3dV133 */
    if(cc)h=h?h+' \u00b7 '+cc:cc;
    var dcr=bimDataCreditHtml();   /* __acad3dV134 */
    if(dcr)h=h?h+' \u00b7 '+dcr:dcr;
    if(h===A3D_MAP.footKey)return;
    A3D_MAP.footKey=h;
    f.innerHTML=h;
    f.hidden=!h;
  }
  /* one map setting, one undo step; refused with its reason, nothing changed */
  function bimMapSet(field,val){
    var st=bimMapSettings(),nv,v;
    if(field==='style'){
      nv=String(val==null?'off':val);
      if(nv!=='off'&&!BIM_MAP_STYLES[nv]){a3dToast('There is no map style called '+nv);refreshProps();return false;}
    }else if(field==='opacity'){
      v=parseFloat(val);
      if(!isFinite(v)||v<10||v>100){a3dToast('The map opacity is from 10 to 100%');refreshProps();return false;}
      nv=Math.round(v)/100;
    }else if(field==='url'){
      nv=String(val==null?'':val).replace(/^\s+|\s+$/g,'');
      if(nv&&(!/^https?:\/\/[^\s\/]+\/\S*$/i.test(nv)||nv.indexOf('{z}')<0||nv.indexOf('{x}')<0||nv.indexOf('{y}')<0)){
        a3dToast('A tile URL starts with https:// and has {z}, {x} and {y} in it, like https://tiles.example.org/{z}/{x}/{y}.png');
        refreshProps();return false;
      }
    }else if(field==='credit'){
      nv=String(val==null?'':val).replace(/\s+/g,' ').replace(/^ | $/g,'').slice(0,200);
    }else return false;
    if(st[field]===nv)return true;
    pushUndo();
    if(!A3D.site||typeof A3D.site!=='object')A3D.site={name:'Site'};
    A3D.site.map=A3D.site.map||{};
    A3D.site.map[field]=nv;
    if(field==='style'||field==='url')bimMapForgetFailures();
    refreshProps();paint();saveSoon();
    return true;
  }
