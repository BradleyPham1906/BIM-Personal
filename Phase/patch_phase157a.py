"""patch_phase157a.py -- V157: the whole surroundings (Site context C2).

The owner: "i want more context from the site than the current one. and the trees and roads and
tunnels, bridges railway and airports. currently we only have buildings." V133 asked OpenStreetMap
for roads, water, green and trees, but drew them flat -- centre lines and points -- so in 3D only
the buildings read. From the same free Overpass API (no key, the whole world):
- ROADS keep their centre line, the element as before, and gain a surface of their width (the width
  tag, else the lanes at 3.3 m, else a width by class), coloured by use: car road, pedestrian zone,
  footway, cycleway, path. On the terrain, the surface follows the ground point by point.
- BRIDGES (bridge=yes on a road or a railway) are raised to their deck, 6 m a layer (the layer tag,
  else one), a deck 0.8 m thick on piers every 30 m. TUNNELS (tunnel=yes) keep their centre line
  only, named as tunnels: nothing drawn on the ground over them.
- RAILWAYS (rail, light rail, narrow gauge, subway, tram, monorail) as their ballast, 3.2 m wide
  (2.6 for a tram); platforms raised 1 m.
- AIRPORTS: runways (45 m unless the tag says) and taxiways (18 m) at their width, aprons as a hard
  surface, the aerodrome's boundary as an outline.
- TREES stand as a trunk and a crown, from their height (8 m unless the tag says) and crown
  diameter (else 0.6 of the height); a tree row is a tree every 8 m along it.
- POWER: towers 25 m (or their height tag), the lines between them hung at 20 m.
- LAND USE (residential, commercial, retail, industrial, railway, construction) tints the ground.
Each kind has its own layer under Context and its own box in Properties, as V133's. The surface is
the element's mesh: picked, shaded, shadowed and saved with it."""
NAME = 'patch_phase157a.py'
BASE = '3564c6bf85d65cf0d288d6e9831bea406c50051622b6f451437aee67750f09e6'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: anchor count %d (want %d): %r' % (c, n, old[:80]))
    t = t.replace(old, new)


# ---- the kinds ----------------------------------------------------------------------------------------
rep("""  var BIM_CTX_KINDS=['buildings','roads','water','green','trees','terrain'];
  var BIM_CTX_LABEL={buildings:'Buildings',roads:'Roads',water:'Water',green:'Green',trees:'Trees',terrain:'Terrain'};
  var BIM_CTX_COL={buildings:'#c9ccd1',roads:'#8a8f98',water:'#4f8fd6',green:'#6dbb73',trees:'#3f9a52',terrain:'#b08559'};""",
    """  var BIM_CTX_KINDS=['buildings','roads','water','green','trees','rail','airports','power','landuse','terrain'];   /* __acad3dV157: rail, airports, power, land use */
  var BIM_CTX_LABEL={buildings:'Buildings',roads:'Roads',water:'Water',green:'Green',trees:'Trees',rail:'Railways',airports:'Airports',power:'Power',landuse:'Land use',terrain:'Terrain'};
  var BIM_CTX_COL={buildings:'#c9ccd1',roads:'#8a8f98',water:'#4f8fd6',green:'#6dbb73',trees:'#3f9a52',rail:'#8d7b68',airports:'#5d6168',power:'#b9bec6',landuse:'#d9cfb4',terrain:'#b08559'};""")
rep("""    if(feats)for(i=0;i<5;i++)if(k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;""",
    """    if(feats)for(i=0;i<BIM_CTX_KINDS.length;i++)if(BIM_CTX_KINDS[i]!=='terrain'&&k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;   /* __acad3dV157 */""")
rep("""    var k=st.kinds,bad=[],feats=null,trunc=false,i,j,f,o,c,n={buildings:0,roads:0,water:0,green:0,trees:0,terrain:0},ids=[],assumed=0,yards=0;""",
    """    var k=st.kinds,bad=[],feats=null,trunc=false,i,j,f,o,c,n={buildings:0,roads:0,water:0,green:0,trees:0,rail:0,airports:0,power:0,landuse:0,terrain:0},ids=[],assumed=0,yards=0,nb3={bridges:0,tunnels:0,surfaces:0};""")

# ---- the query and the kind of each element ----------------------------------------------------------------
rep("""    if(k.trees)q.push('node["natural"="tree"]'+b+';');
    return q.length?'[out:json][timeout:25];('+q.join('')+');out geom;':'';""",
    """    if(k.trees)q.push('node["natural"="tree"]'+b+';','way["natural"="tree_row"]'+b+';');
    if(k.rail)q.push('way["railway"~"^(rail|light_rail|narrow_gauge|subway|tram|monorail|platform)$"]'+b+';');   /* __acad3dV157 */
    if(k.airports)q.push('way["aeroway"~"^(runway|taxiway|apron|aerodrome|helipad)$"]'+b+';','relation["aeroway"="aerodrome"]'+b+';');
    if(k.power)q.push('way["power"="line"]'+b+';','node["power"="tower"]'+b+';');
    if(k.landuse)q.push('way["landuse"~"^('+BIM_CTX_LANDUSE+')$"]'+b+';','relation["landuse"~"^('+BIM_CTX_LANDUSE+')$"]["type"="multipolygon"]'+b+';');
    return q.length?'[out:json][timeout:25];('+q.join('')+');out geom;':'';""")
rep("""    if(el.type==='node')return t.natural==='tree'?'trees':'';""",
    """    if(el.type==='node')return t.natural==='tree'?'trees':(t.power==='tower'?'power':'');   /* __acad3dV157 */
    if(t.railway&&/^(rail|light_rail|narrow_gauge|subway|tram|monorail|platform)$/.test(t.railway))return 'rail';
    if(t.aeroway&&/^(runway|taxiway|apron|aerodrome|helipad)$/.test(t.aeroway))return 'airports';
    if(t.power==='line')return 'power';
    if(t.natural==='tree_row')return 'trees';""")
rep("""    if(t.leisure==='park'||/^(grass|forest|meadow|recreation_ground|village_green)$/.test(t.landuse||'')||/^(wood|scrub|grassland)$/.test(t.natural||''))return 'green';
    return '';""", """    if(t.leisure==='park'||/^(grass|forest|meadow|recreation_ground|village_green)$/.test(t.landuse||'')||/^(wood|scrub|grassland)$/.test(t.natural||''))return 'green';
    if(t.landuse&&new RegExp('^('+BIM_CTX_LANDUSE+')$').test(t.landuse))return 'landuse';   /* __acad3dV157 */
    return '';""")
# closed ways that are areas: aprons, aerodromes, helipads, platforms and land use too
rep("""        if(cl&&(kind==='buildings'||kind==='green'||(kind==='water'&&!f.tags.waterway)))f.outer.push(g.slice(0,-1).map(M));""",
    """        if(cl&&(kind==='buildings'||kind==='green'||kind==='landuse'||(kind==='water'&&!f.tags.waterway)||
          (kind==='airports'&&/^(apron|aerodrome|helipad)$/.test(f.tags.aeroway||''))||(kind==='rail'&&f.tags.railway==='platform')))f.outer.push(g.slice(0,-1).map(M));   /* __acad3dV157 */""")

# ---- the meshes ------------------------------------------------------------------------------------------
rep("""  function bimCtxLayers(){""", """  /* ================= __acad3dV157: the surroundings in 3D =================
     A road, a railway or a runway keeps its centre line, the element; its surface is that
     element's mesh, built here: a strip of its width along the line, on the ground point by point,
     or a deck on piers for a bridge. */
  var BIM_CTX_LANDUSE='residential|commercial|retail|industrial|railway|construction';
  var BIM_ROAD_W={motorway:14,motorway_link:7,trunk:12,trunk_link:7,primary:11,primary_link:6,secondary:9,secondary_link:6,tertiary:8,tertiary_link:6,
    residential:7,unclassified:6,living_street:6,service:4,pedestrian:6,track:3,footway:2,path:1.5,cycleway:2,steps:2,bridleway:2,corridor:2};
  var BIM_ROAD_COL={car:'#6e737a',pedestrian:'#cdb98d',footway:'#8cbf86',cycleway:'#5fa8d3',path:'#a3b77e'};
  var BIM_LANDUSE_COL={residential:'#d9cfb4',commercial:'#d6b8b8',retail:'#d9b3c4',industrial:'#c4bccf',railway:'#bdb3a6',construction:'#cfc59a'};
  var BIM_CTX_DECK=6,BIM_CTX_DECK_T=0.8,BIM_CTX_PIER=30,BIM_CTX_TREE_H=8,BIM_CTX_TREE_STEP=8,BIM_CTX_TOWER_H=25,BIM_CTX_LINE_H=20,BIM_CTX_TREES_MAX=3000;
  /* the use a road is for, as UrbanEyes' street use: car road, pedestrian zone, footway, cycleway, path */
  function bimRoadUse(t){
    var h=t.highway||'';
    if(h==='pedestrian'||h==='living_street')return 'pedestrian';
    if(h==='footway'||h==='steps'||h==='corridor')return 'footway';
    if(h==='cycleway')return 'cycleway';
    if(h==='path'||h==='track'||h==='bridleway')return 'path';
    return 'car';
  }
  /* a width in metres from a width tag ("7", "7 m", "23'") */
  function bimTagMetres(v){
    var m=/^\\s*([0-9]*\\.?[0-9]+)\\s*(m|metres|meters|ft|feet|')?\\s*$/i.exec(String(v==null?'':v).replace(/,/g,'.'));
    if(!m)return null;
    var x=parseFloat(m[1]);if(m[2]&&/^(ft|feet|')$/i.test(m[2]))x*=0.3048;
    return x>0&&x<500?x:null;
  }
  function bimCtxWidth(kind,t){
    var w=bimTagMetres(t.width);
    if(w)return w;
    if(kind==='roads'){var L=parseFloat(t.lanes);if(isFinite(L)&&L>0&&L<20)return Math.max(2,L*3.3);return BIM_ROAD_W[t.highway]||5;}
    if(kind==='rail')return t.railway==='tram'?2.6:3.2;
    if(kind==='airports')return t.aeroway==='runway'?45:(t.aeroway==='taxiway'?18:10);
    return 4;
  }
  /* a strip of width w along pts, its corners mitred; yAt(x,z) the height under each point */
  function bimStripMesh(pts,w,yAt,lift){
    var n=pts.length,v=[],f=[],i,h=w/2,L=[],R=[];
    for(i=0;i<n;i++){
      var a=pts[Math.max(0,i-1)],b=pts[i],c=pts[Math.min(n-1,i+1)];
      var d1x=b[0]-a[0],d1z=b[1]-a[1],d2x=c[0]-b[0],d2z=c[1]-b[1],l1=Math.sqrt(d1x*d1x+d1z*d1z),l2=Math.sqrt(d2x*d2x+d2z*d2z);
      if(l1>1e-9){d1x/=l1;d1z/=l1;}else{d1x=d2x/(l2||1);d1z=d2z/(l2||1);}
      if(l2>1e-9){d2x/=l2;d2z/=l2;}else{d2x=d1x;d2z=d1z;}
      var nx=-(d1z+d2z),nz=d1x+d2x,ln=Math.sqrt(nx*nx+nz*nz);
      if(ln<1e-9){nx=-d1z;nz=d1x;ln=1;}
      nx/=ln;nz/=ln;
      var cs=nx*(-d1z)+nz*d1x,s=h/Math.max(0.35,Math.abs(cs));   /* the mitre, no longer than 1/0.35 of the half width */
      var y=yAt(b[0],b[1])+lift;
      L.push(v.length);v.push([b[0]+nx*s,y,b[1]+nz*s]);
      R.push(v.length);v.push([b[0]-nx*s,y,b[1]-nz*s]);
    }
    for(i=0;i+1<n;i++)f.push([L[i],L[i+1],R[i+1],R[i]]);
    return {v:v,f:f};
  }
  /* a bridge: the deck as a slab of thickness, on piers every BIM_CTX_PIER metres */
  function bimDeckMesh(pts,w,yAt,deck){
    var top=bimStripMesh(pts,w,function(x,z){return yAt(x,z)+deck;},0),n=top.v.length,v=top.v.slice(),f=[],i,j;
    for(i=0;i<n;i++)v.push([top.v[i][0],top.v[i][1]-BIM_CTX_DECK_T,top.v[i][2]]);
    top.f.forEach(function(q){f.push(q);f.push([q[3]+n,q[2]+n,q[1]+n,q[0]+n]);});
    for(i=0;i+2<n;i+=2){f.push([i,i+n,i+2+n,i+2]);f.push([i+3,i+3+n,i+1+n,i+1]);}   /* the two edges */
    f.push([0,1,1+n,n]);f.push([n-1,n-2,n-2+n,n-1+n]);   /* the two ends */
    var run=0,next=BIM_CTX_PIER/2;
    for(i=0;i+1<pts.length;i++){
      var dx=pts[i+1][0]-pts[i][0],dz=pts[i+1][1]-pts[i][1],L=Math.sqrt(dx*dx+dz*dz);
      while(next<=run+L){
        var tt=(next-run)/L,px=pts[i][0]+dx*tt,pz=pts[i][1]+dz*tt,g=yAt(px,pz),hgt=deck-BIM_CTX_DECK_T,s=Math.min(0.8,w/4),b0=v.length;
        if(hgt>0.5){
          for(j=0;j<8;j++)v.push([px+((j&1)?s:-s),g+((j&4)?hgt:0),pz+((j&2)?s:-s)]);
          f.push([b0,b0+1,b0+3,b0+2],[b0+4,b0+6,b0+7,b0+5],[b0,b0+4,b0+5,b0+1],[b0+2,b0+3,b0+7,b0+6],[b0,b0+2,b0+6,b0+4],[b0+1,b0+5,b0+7,b0+3]);
        }
        next+=BIM_CTX_PIER;
      }
      run+=L;
    }
    return {v:v,f:f};
  }
  /* a tree: a hexagonal trunk and a crown of 20 faces */
  function bimTreeMesh(x,z,y,h,cd){
    var v=[],f=[],i,r=Math.max(0.08,h*0.025),cr=Math.max(0.6,cd/2),cy=y+Math.max(h-cr,h*0.45),th=Math.max(0.5,cy-y);
    for(i=0;i<6;i++){var a=i*Math.PI/3;v.push([x+r*Math.cos(a),y,z+r*Math.sin(a)]);}
    for(i=0;i<6;i++){var a2=i*Math.PI/3;v.push([x+r*Math.cos(a2),y+th,z+r*Math.sin(a2)]);}
    for(i=0;i<6;i++){var j=(i+1)%6;f.push([i,j,j+6,i+6]);}
    var p=(1+Math.sqrt(5))/2,s=cr/Math.sqrt(1+p*p),b=v.length,
      ico=[[-1,p,0],[1,p,0],[-1,-p,0],[1,-p,0],[0,-1,p],[0,1,p],[0,-1,-p],[0,1,-p],[p,0,-1],[p,0,1],[-p,0,-1],[-p,0,1]],
      tri=[[0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],[1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],[3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],[4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1]];
    for(i=0;i<12;i++)v.push([x+ico[i][0]*s,cy+ico[i][1]*s,z+ico[i][2]*s]);
    for(i=0;i<20;i++)f.push([b+tri[i][0],b+tri[i][1],b+tri[i][2]]);
    return {v:v,f:f};
  }
  /* a pylon: a tapering four-sided tower */
  function bimTowerMesh(x,z,y,h){
    var v=[],f=[],a=2,b=0.5;
    v.push([x-a,y,z-a],[x+a,y,z-a],[x+a,y,z+a],[x-a,y,z+a],[x-b,y+h,z-b],[x+b,y+h,z-b],[x+b,y+h,z+b],[x-b,y+h,z+b]);
    f.push([0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]);
    return {v:v,f:f};
  }
  function bimCtxLayers(){""")

# ---- trees and towers at points, and the line and area elements' surfaces ------------------------------------
rep("""        }else if(f.kind==='trees'&&f.point){
          o=bimAddPoint(f.point[0],f.point[1],y0,L.trees);
          o.name='Tree '+(n.trees+1);o.context=rec('trees',f);place(o,'trees');
        }else{""", """        }else if(f.kind==='trees'&&(f.point||f.line)){   /* __acad3dV157: a tree, or a tree every 8 m along a row */
          var tp=f.point?[f.point]:bimCtxAlong(f.line.pts,BIM_CTX_TREE_STEP),th2=bimTagMetres(f.tags.height)||BIM_CTX_TREE_H,cd2=bimTagMetres(f.tags.diameter_crown)||th2*0.6;
          for(j=0;j<tp.length&&n.trees<BIM_CTX_TREES_MAX;j++){
            var gy=y0+(hAt(tp[j][0],tp[j][1]));
            o=bimAddPoint(tp[j][0],tp[j][1],gy,L.trees);
            o.name=String(f.tags.species||f.tags.genus||'Tree')+' '+(n.trees+1);o.context=rec('trees',f);
            o.context.height=th2;o.context.crown=Math.round(cd2*100)/100;
            if(!f.point)o.context.row=true;
            o.mesh=bimTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2);o.col=BIM_CTX_COL.trees;
            place(o,'trees');
          }
        }else if(f.kind==='power'&&f.point){   /* __acad3dV157: a pylon */
          var tw=bimTagMetres(f.tags.height)||BIM_CTX_TOWER_H,gy2=y0+hAt(f.point[0],f.point[1]);
          o=bimAddPoint(f.point[0],f.point[1],gy2,L.power);
          o.name='Pylon '+(n.power+1);o.context=rec('power',f);o.context.height=tw;
          o.mesh=bimTowerMesh(f.point[0],f.point[1],gy2,tw);place(o,'power');
        }else{""")
rep("""          if(f.line){
            o=bimMakeImportedSketch(f.line.pts,y0,f.line.closed);
            if(o){o.name=String(label).slice(0,60);o.context=rec(f.kind,f);place(o,f.kind);}
          }""", """          if(f.line){
            o=bimMakeImportedSketch(f.line.pts,f.kind==='power'?y0+BIM_CTX_LINE_H:y0,f.line.closed);   /* __acad3dV157: a power line hung */
            if(o){o.name=String(label).slice(0,60);o.context=rec(f.kind,f);place(o,f.kind);bimCtxSurface(o,f,hAt,y0,nb3);}
          }""")
rep("""            o.name=String(label).slice(0,60);o.context=rec(f.kind,f);
            if(j>=f.outer.length)o.context.part='hole';
            place(o,f.kind);""", """            o.name=String(label).slice(0,60);o.context=rec(f.kind,f);
            if(j>=f.outer.length)o.context.part='hole';
            place(o,f.kind);
            if(j<f.outer.length&&!f.inner.length)bimCtxArea3d(o,f,ring,hAt,y0,nb3);   /* __acad3dV157 */""")
# the height under a point: the terrain when the context stands on it
rep("""    function rec(kind,f2){return {kind:kind,source:'OpenStreetMap',""",
    """    function hAt(x,z){   /* __acad3dV157: the ground under a point, when the context stands on the terrain */
      if(!st.onGround)return 0;
      var g2=ground([x,z]);return g2===null?0:g2;
    }
    function rec(kind,f2){return {kind:kind,source:'OpenStreetMap',""")
rep("""  /* CONTEXTREMOVE: every context object, in one undo step */""", """  /* __acad3dV157: points about every step metres along a line, evenly, both its ends among them (a
     row's length read back from latitude and longitude is never quite whole) */
  function bimCtxAlong(pts,step){
    var out=[],i,run=0,tot=0,n,k=0,d;
    for(i=0;i+1<pts.length;i++)tot+=Math.sqrt(Math.pow(pts[i+1][0]-pts[i][0],2)+Math.pow(pts[i+1][1]-pts[i][1],2));
    if(!(tot>0))return pts.length?[[pts[0][0],pts[0][1]]]:[];
    n=Math.max(1,Math.round(tot/step));d=tot/n;
    for(i=0;i+1<pts.length;i++){
      var dx=pts[i+1][0]-pts[i][0],dz=pts[i+1][1]-pts[i][1],L=Math.sqrt(dx*dx+dz*dz);
      while(k<=n&&(k*d<=run+L+1e-9||(i+2===pts.length))){var tt=L>0?Math.min(1,(k*d-run)/L):0;out.push([pts[i][0]+dx*tt,pts[i][1]+dz*tt]);k++;}
      run+=L;
    }
    return out;
  }
  /* a line element's surface: a road, a railway, a runway or taxiway; a bridge raised; a tunnel none */
  function bimCtxSurface(o,f,hAt,y0,nb3){
    var t=f.tags,k=f.kind,pts=f.line.pts,c=o.context;
    if(!(k==='roads'||k==='rail'||(k==='airports'&&/^(runway|taxiway)$/.test(t.aeroway||''))))return;
    if(k==='rail'&&t.railway==='platform')return;
    var w=bimCtxWidth(k,t);c.width=Math.round(w*100)/100;
    if(k==='roads'){c.use=bimRoadUse(t);o.col=BIM_ROAD_COL[c.use];}
    if(t.tunnel&&t.tunnel!=='no'){c.tunnel=true;o.name=('Tunnel: '+o.name).slice(0,60);nb3.tunnels++;return;}
    function yAt(x,z){return y0+hAt(x,z);}
    if(t.bridge&&t.bridge!=='no'){
      var ly=parseFloat(t.layer);if(!isFinite(ly)||ly<1)ly=1;
      c.bridge=true;c.deck=ly*BIM_CTX_DECK;
      o.mesh=bimDeckMesh(pts,w,yAt,c.deck);o.name=('Bridge: '+o.name).slice(0,60);nb3.bridges++;
    }else o.mesh=bimStripMesh(pts,w,yAt,k==='rail'?0.08:(k==='airports'?0.03:0.05));
    nb3.surfaces++;
  }
  /* an area element's surface: an apron, a helipad, a platform, a land use tint */
  function bimCtxArea3d(o,f,ring,hAt,y0,nb3){
    var t=f.tags,k=f.kind,P=sketchCCW(ring),cx=0,cz=0,i,h=0.02,lift=0.01;
    if(k==='landuse'){o.col=BIM_LANDUSE_COL[t.landuse]||BIM_CTX_COL.landuse;lift=0;}   /* a tint at the ground, under the roads */
    else if(k==='airports'&&/^(apron|helipad)$/.test(t.aeroway||'')){lift=0.02;}
    else if(k==='rail'&&t.railway==='platform'){h=1;lift=0;}
    else return;
    if(P.length<3)return;
    for(i=0;i<P.length;i++){cx+=P[i][0];cz+=P[i][1];}
    try{o.mesh=padMesh(P,y0+hAt(cx/P.length,cz/P.length)+lift,h);nb3.surfaces++;}catch(eA){}
  }
  /* CONTEXTREMOVE: every context object, in one undo step */""")
# the counts the message and the result carry
rep("""    return {counts:n,ids:ids,errors:bad,truncated:trunc,assumed:assumed,courtyards:yards,parts:nParts,wholes:nWhole,lowParts:lowParts,roofs:nRoofs,notRoofed:nNoRoof};""",
    """    return {counts:n,ids:ids,errors:bad,truncated:trunc,assumed:assumed,courtyards:yards,parts:nParts,wholes:nWhole,lowParts:lowParts,roofs:nRoofs,notRoofed:nNoRoof,
      bridges:nb3.bridges,tunnels:nb3.tunnels,surfaces:nb3.surfaces};   /* __acad3dV157 */""")
rep("""      bimRoofCountText(nRoofs,nNoRoof)+   /* __acad3dV140 */""",
    """      bimRoofCountText(nRoofs,nNoRoof)+   /* __acad3dV140 */
      (nb3.bridges?'; '+nb3.bridges+' bridge'+(nb3.bridges===1?'':'s')+' raised':'')+(nb3.tunnels?'; '+nb3.tunnels+' tunnel'+(nb3.tunnels===1?'':'s')+' below ground':'')+   /* __acad3dV157 */""")
rep("""    CONTEXT:'neighbours neighbors surrounding buildings osm openstreetmap overpass roads streets water rivers parks trees terrain elevation contours ground giraffe',   /* __acad3dV133 */""",
    """    CONTEXT:'neighbours neighbors surrounding buildings osm openstreetmap overpass roads streets water rivers parks trees terrain elevation contours ground giraffe railway railways train tram subway bridges tunnels airport runway power pylons land use infrastructure',   /* __acad3dV133; __acad3dV157 */""")
rep("""  window.__acad3dV156='seencount,""", """  window.__acad3dV157='railkind,airportkind,powerkind,landusekind,roadsurface,roaduse,bridgedeck,piers,tunnels,trees3d,treerows,pylons,drapedsurfaces';
  window.__acad3dV156='seencount,""")
rep("""  var BIM_APP_VERSION={v:'V156',date:'2026-10-04'};   /* __acad3dV156 */""",
    """  var BIM_APP_VERSION={v:'V157',date:'2026-10-04'};   /* __acad3dV157 */""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
