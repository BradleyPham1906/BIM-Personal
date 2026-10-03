"""patch_phase132a.py -- V132: the map, its engine.

- Georeferencing: the site's latitude and longitude (V107) are model 0,0 and true north (V103) turns
  the model on the earth; metres become degrees through the WGS84 ellipsoid's radii at the site.
- Web Mercator tiles: the zoom from the view's metres per pixel, the extent from the screen on the
  ground, at most 80 tiles, nearest the centre first.
- A tile store: Image elements with crossOrigin, at most 12 in flight, about 400 kept, a loading
  tile drawn from its parent meanwhile, a failure counted against its host.
- Drawing: a textured quad per tile in WebGL, under every solid; an affine-transformed image per
  tile on the 2D canvas, in plan. Never on paper.
- The credit line over the viewport, with what did not load and why.
- The settings live in A3D.site.map, so undo, the project file and the browser store keep them."""
NAME = 'patch_phase132a.py'
BASE = '14630df8e1b0b95de2f917793cbb76fc652cd16a7cedba5dcbf8d10ef3739e7f'
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


ENGINE = r"""  /* ================= __acad3dV132: the map =================
     A basemap under the plan and the 3D ground: OpenStreetMap's street map, Esri's imagery, or the
     owner's own tiles. It is off until someone turns it on, so the app asks the network for nothing
     until asked. The site's latitude and longitude (V107) are model 0,0, as V108's survey base point
     is, and true north (V103) turns the model on the map. */
  var BIM_MAP_STYLES={
    street:{name:'Street (OpenStreetMap)',url:'https://tile.openstreetmap.org/{z}/{x}/{y}.png',maxz:19,
      credit:'© OpenStreetMap contributors',link:'https://www.openstreetmap.org/copyright'},
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
    return tpl.split('{z}').join(String(z)).split('{x}').join(String(xx)).split('{y}').join(String(y));
  }
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
    var z=Math.round(Math.log(156543.03392*Math.cos(org.lat*BIM_D2R)/mpp)/Math.LN2),x0,x1,y0,y1,n;
    z=Math.max(1,Math.min(maxz,z));
    for(;;){
      n=Math.pow(2,z);
      x0=Math.floor(bimLonToTileX(lo0,z));x1=Math.floor(bimLonToTileX(lo1,z));
      y0=Math.max(0,Math.floor(bimLatToTileY(la1,z)));y1=Math.min(n-1,Math.floor(bimLatToTileY(la0,z)));
      if((x1-x0+1)*(y1-y0+1)<=BIM_MAP_MAXT||z<=1)break;
      z--;
    }
    var cx=bimLonToTileX((lo0+lo1)/2,z),cy=bimLatToTileY((la0+la1)/2,z),T=[],x,y;
    for(y=y0;y<=y1;y++)for(x=x0;x<=x1;x++)T.push({x:x,y:y,z:z,k:(x+0.5-cx)*(x+0.5-cx)+(y+0.5-cy)*(y+0.5-cy)});
    T.sort(function(a,b){return a.k-b.k;});
    r.z=z;r.tiles=T;r.tpl=tpl;r.org=org;r.ground=g;r.opacity=st.opacity;r.extent=[lo0,la0,lo1,la1];r.mpp=mpp;
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
    var fs=bimGlCompile(gl,gl.FRAGMENT_SHADER,'precision mediump float;uniform sampler2D uTex;uniform float uAlpha;varying vec2 vUV;'+
      'void main(){vec3 c=texture2D(uTex,vUV).rgb;gl_FragColor=vec4(mix(vec3(0.114,0.125,0.141),c,uAlpha),1.0);}');
    if(!vs||!fs)return null;
    var p=gl.createProgram();
    gl.attachShader(p,vs);gl.attachShader(p,fs);gl.linkProgram(p);
    if(!gl.getProgramParameter(p,gl.LINK_STATUS)){console.warn('[BIM] map shader link failed: '+gl.getProgramInfoLog(p));return null;}
    G.map={prog:p,buf:gl.createBuffer(),pos:gl.getAttribLocation(p,'aPos'),uv:gl.getAttribLocation(p,'aUV'),
      view:gl.getUniformLocation(p,'uView'),proj:gl.getUniformLocation(p,'uProj'),
      tex:gl.getUniformLocation(p,'uTex'),alpha:gl.getUniformLocation(p,'uAlpha')};
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
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
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
    var h=bimMapFooterHtml();
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
"""

rep("""  function bimGlRender(V,W,H){""", ENGINE + """  function bimGlRender(V,W,H){""")

# WebGL: right after the clear, before the solids' program
rep("""    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    gl.useProgram(G.prog);""", """    gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
    bimMapDrawGl(G,V,W,H);   /* __acad3dV132: the basemap, under everything */
    gl.useProgram(G.prog);""")

# the 2D canvas: after the background, before the grid; and the credit line
rep("""    else{ctx.fillStyle='#1d2024';ctx.fillRect(0,0,W,H);}
    if(!capMode){
      ctx.strokeStyle='#282c31';""", """    else{ctx.fillStyle='#1d2024';ctx.fillRect(0,0,W,H);}
    if(!capMode){
      if(!glOn)bimMapDraw2D(ctx,V,W,H);   /* __acad3dV132: the basemap; with WebGL on it is drawn there */
      bimMapFooterSync();
      ctx.strokeStyle='#282c31';""")

# the credit line's element, over the viewport
rep("""      '<div id="a3d-dock"></div>'+""", """      '<div id="a3d-mapattr" class="a3d-mapattr" hidden></div>'+   /* __acad3dV132: the map's credit */
      '<div id="a3d-dock"></div>'+""")

rep("""body.light-theme .a3d-uerr{color:#b3261e}""", """body.light-theme .a3d-uerr{color:#b3261e}
.a3d-mapattr{position:absolute;right:6px;bottom:2px;z-index:5;max-width:62%;font-size:10.5px;line-height:1.35;color:#c9d1d9;background:rgba(20,22,26,.78);padding:1px 6px;border-radius:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.a3d-mapattr[hidden]{display:none}
.a3d-mapattr a{color:#9cc4ff;text-decoration:none}
.a3d-mapattr a:hover{text-decoration:underline}
.a3d-mapwarn{color:#ffb454}
.a3d-sheetview.open~#a3d-mapattr{display:none}
body.light-theme .a3d-mapattr{background:rgba(255,255,255,.85);color:#24292f}
body.light-theme .a3d-mapattr a{color:#0b5cad}
body.light-theme .a3d-mapwarn{color:#9a5b00}
@media(max-width:720px),(max-height:500px){.a3d-mapattr{top:4px;bottom:auto;left:6px;right:auto;max-width:70%}}""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
