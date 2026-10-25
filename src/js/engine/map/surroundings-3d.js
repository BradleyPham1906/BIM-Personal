  /* ================= __acad3dV157: the surroundings in 3D =================
     A road, a railway or a runway keeps its centre line, the element; its surface is that
     element's mesh, built here: a strip of its width along the line, on the ground point by point,
     or a deck on piers for a bridge. */
  var BIM_CTX_LANDUSE='residential|commercial|retail|industrial|railway|construction|'+   /* __acad3dV168: what LBCS's crosswalk reads */
    'education|institutional|civic_admin|religious|churchyard|cemetery|military|garages|landfill|brownfield|greenfield|farmland|field|farmyard|orchard|vineyard|allotments|plant_nursery|greenhouse_horticulture|aquaculture|quarry|port|school|flowerbed';
  /* __acad3dV168: the areas of amenities, leisure and tourism, land use too: a school's grounds, a car park, a pitch */
  var BIM_CTX_LAND_AREAS={amenity:'school|university|college|kindergarten|hospital|clinic|place_of_worship|townhall|library|fire_station|police|courthouse|prison|grave_yard|marketplace|theatre|cinema|arts_centre|community_centre|parking|bus_station|nursing_home',
    leisure:'playground|pitch|sports_centre|stadium|golf_course|garden|track|marina',tourism:'hotel|motel|museum|gallery|zoo|aquarium|theme_park|camp_site'};
  /* __acad3dV167: the widths are the registry's (app.context): bimRoadW */
  var BIM_ROAD_USE_LABEL={car:'car road',pedestrian:'pedestrian zone',footway:'footway',cycleway:'cycleway',path:'path'};
  var BIM_ROAD_COL={car:'#6e737a',pedestrian:'#cdb98d',footway:'#8cbf86',cycleway:'#5fa8d3',path:'#a3b77e'};
  var BIM_LANDUSE_COL={residential:'#d9cfb4',commercial:'#d6b8b8',retail:'#d9b3c4',industrial:'#c4bccf',railway:'#bdb3a6',construction:'#cfc59a'};
  var BIM_CTX_TREE_STEP=8,BIM_CTX_TREES_MAX=3000;   /* __acad3dV167: the decks, piers, trees, towers and lines are the registry's (app.context) */
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
    var m=/^\s*([0-9]*\.?[0-9]+)\s*(m|metres|meters|ft|feet|')?\s*$/i.exec(String(v==null?'':v).replace(/,/g,'.'));
    if(!m)return null;
    var x=parseFloat(m[1]);if(m[2]&&/^(ft|feet|')$/i.test(m[2]))x*=0.3048;
    return x>0&&x<500?x:null;
  }
  function bimCtxWidth(kind,t){
    var w=bimTagMetres(t.width);
    if(w)return w;
    if(kind==='roads'){var L=parseFloat(t.lanes);if(isFinite(L)&&L>0&&L<20)return Math.max(2,L*3.3);return bimRoadW()[t.highway]||5;}
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
  /* a bridge: the deck as a slab of thickness, on piers every bimCtxPier() metres */
  function bimDeckMesh(pts,w,yAt,deck){
    var top=bimStripMesh(pts,w,function(x,z){return yAt(x,z)+deck;},0),n=top.v.length,v=top.v.slice(),f=[],i,j;
    for(i=0;i<n;i++)v.push([top.v[i][0],top.v[i][1]-bimCtxDeckT(),top.v[i][2]]);
    top.f.forEach(function(q){f.push(q);f.push([q[3]+n,q[2]+n,q[1]+n,q[0]+n]);});
    for(i=0;i+2<n;i+=2){f.push([i,i+n,i+2+n,i+2]);f.push([i+3,i+3+n,i+1+n,i+1]);}   /* the two edges */
    f.push([0,1,1+n,n]);f.push([n-1,n-2,n-2+n,n-1+n]);   /* the two ends */
    var run=0,next=bimCtxPier()/2;
    for(i=0;i+1<pts.length;i++){
      var dx=pts[i+1][0]-pts[i][0],dz=pts[i+1][1]-pts[i][1],L=Math.sqrt(dx*dx+dz*dz);
      while(next<=run+L){
        var tt=(next-run)/L,px=pts[i][0]+dx*tt,pz=pts[i][1]+dz*tt,g=yAt(px,pz),hgt=deck-bimCtxDeckT(),s=Math.min(0.8,w/4),b0=v.length;
        if(hgt>0.5){
          for(j=0;j<8;j++)v.push([px+((j&1)?s:-s),g+((j&4)?hgt:0),pz+((j&2)?s:-s)]);
          f.push([b0,b0+1,b0+3,b0+2],[b0+4,b0+6,b0+7,b0+5],[b0,b0+4,b0+5,b0+1],[b0+2,b0+3,b0+7,b0+6],[b0,b0+2,b0+6,b0+4],[b0+1,b0+5,b0+7,b0+3]);
        }
        next+=bimCtxPier();
      }
      run+=L;
    }
    return {v:v,f:f};
  }
  /* a pylon: a tapering four-sided tower */
  function bimTowerMesh(x,z,y,h){
    var v=[],f=[],a=2,b=0.5;
    v.push([x-a,y,z-a],[x+a,y,z-a],[x+a,y,z+a],[x-a,y,z+a],[x-b,y+h,z-b],[x+b,y+h,z-b],[x+b,y+h,z+b],[x-b,y+h,z+b]);
    f.push([0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]);
    return {v:v,f:f};
  }
  function bimCtxLayers(){
    var par=bimLayerByName('Context')||bimLayerNew({name:'Context',color:'#9aa3ad'})||A3D.layers[0],L={},i,k,ly;
    for(i=0;i<BIM_CTX_KINDS.length;i++){
      k=BIM_CTX_KINDS[i];
      ly=bimLayerByName('Context '+k)||bimLayerNew({name:'Context '+k,color:BIM_CTX_COL[k],parent:par.id});
      L[k]=ly?ly.id:par.id;
    }
    return L;
  }
  function bimCtxCleanTags(t){
    var o={},k,n=0;
    for(k in t)if(t.hasOwnProperty(k)&&n<60){n++;o[String(k).slice(0,60)]=String(t[k]).slice(0,300);}
    return o;
  }
  function bimCtxErr(host,e){
    if(e&&(e.http===429||e.http===504))return host+' is busy (HTTP '+e.http+'): try again in a minute';
    if(e&&e.http)return host+' answered HTTP '+e.http;
    if(e&&e.bad)return host+' sent an answer that does not read';
    return host+' could not be reached (offline, or it does not allow browser access)';
  }
  /* CONTEXT: one press, one request to each source; what comes is placed in one undo step */
  function bimCtxFetch(){
    if(A3D_CTX.busy){a3dToast('The site context is already on its way');return null;}
    var a=bimCtxArea(),st=bimCtxSettings(),k=st.kinds,q,names=[],i;
    if(!a){a3dToast('Set the site latitude and longitude first, or find an address: the context is placed around the site');return null;}
    if(typeof fetch!=='function'){a3dToast('This browser cannot fetch the context');return null;}
    q=bimCtxQuery(a,k);
    if(!q&&!k.terrain){a3dToast('Tick at least one kind of context to get');return null;}
    for(i=0;i<BIM_CTX_KINDS.length;i++)if(k[BIM_CTX_KINDS[i]])names.push(BIM_CTX_LABEL[BIM_CTX_KINDS[i]].toLowerCase());
    A3D_CTX.busy=true;
    a3dToast('Getting the site context: '+names.join(', ')+', '+st.radius+' m around the '+(a.fromProperty?'property':'site')+' ...');
    var pOsm=q?bimCtxOverpass(q,st.overpass):Promise.resolve(null);   /* __acad3dV134d */
    var pTer=k.terrain?bimCtxTerrain(a):Promise.resolve(null);
    return Promise.all([pOsm,pTer]).then(function(r){
      A3D_CTX.busy=false;
      try{return bimCtxApply(a,st,r[0],r[1]);}
      catch(eA){console.warn('[BIM] site context',eA);a3dToast('The site context could not be placed - see the console');return {error:String(eA)};}
    },function(e){A3D_CTX.busy=false;console.warn('[BIM] site context',e);return {error:String(e)};});
  }
  /* __acad3dV134d: Overpass's public instances, the one set first, each asked with a plain GET until
     one answers; every failure kept, to be named if none does */
  var BIM_OVERPASS_MIRRORS=['https://overpass-api.de/api/interpreter','https://overpass.private.coffee/api/interpreter',
    'https://maps.mail.ru/osm/tools/overpass/api/interpreter','https://overpass.kumi.systems/api/interpreter'];
  function bimCtxOverpass(q,first){
    var list=[first],tried=[];
    BIM_OVERPASS_MIRRORS.forEach(function(u){if(list.indexOf(u)<0)list.push(u);});
    function one(i){
      if(i>=list.length)return Promise.resolve({ok:false,msgs:tried});
      var u=list[i];
      return fetch(u+(u.indexOf('?')<0?'?':'&')+'data='+encodeURIComponent(q)).then(function(r){
        if(!r.ok)throw {http:r.status};
        return r.text();
      }).then(function(tx){
        var js;
        try{js=JSON.parse(tx);}catch(eJ){throw {bad:true};}
        if(!js||!js.elements)throw {bad:true};
        return {ok:true,js:js,server:u,msgs:tried};
      },function(e){throw e;}).then(null,function(e){
        tried.push(bimCtxErr(bimMapHost(u),e));
        return one(i+1);
      });
    }
    return one(0);
  }
  function bimCtxApply(a,st,osm,ter){
    var k=st.kinds,bad=[],feats=null,trunc=false,i,j,f,o,c,n={buildings:0,roads:0,water:0,green:0,trees:0,rail:0,airports:0,power:0,landuse:0,terrain:0},ids=[],assumed=0,yards=0,nb3={bridges:0,tunnels:0,surfaces:0};
    if(osm){
      if(osm.ok){var fr=bimCtxFeatures(osm.js,a.org);feats=fr.features;trunc=fr.truncated;}
      else bad=bad.concat(osm.msgs&&osm.msgs.length?osm.msgs:[bimCtxErr(bimMapHost(st.overpass),osm.err)]);   /* __acad3dV134d: each server tried */
    }
    if(ter&&!ter.ok)bad.push(bimCtxErr('s3.amazonaws.com',ter.err));
    var terOk=!!(ter&&ter.ok);
    if(!feats&&!terOk){a3dToast('No site context: '+bad.join('; '));return {error:bad.join('; ')};}
    var repl={};
    if(feats)for(i=0;i<BIM_CTX_KINDS.length;i++)if(BIM_CTX_KINDS[i]!=='terrain'&&k[BIM_CTX_KINDS[i]])repl[BIM_CTX_KINDS[i]]=1;   /* __acad3dV157 */
    if(terOk)repl.terrain=1;
    var L=null,y0=bimShadowGround(),base=null,date=new Date().toISOString().slice(0,10);
    function ground(p){
      if(!terOk||base===null)return null;
      var gg2=bimModelToGeo(p[0],p[1],a.org),e2=bimCtxElevAt(ter,gg2[0],gg2[1]);
      return isFinite(e2)?Math.round((e2-base)*100)/100:null;
    }
    function hAt(x,z){   /* __acad3dV157: the ground under a point, when the context stands on the terrain */
      if(!st.onGround)return 0;
      var g2=ground([x,z]);return g2===null?0:g2;
    }
    function rec(kind,f2){return {kind:kind,source:'OpenStreetMap',credit:BIM_CTX_OSM_CREDIT,osm:f2.osm,id:f2.id,tags:bimCtxCleanTags(f2.tags),fetched:date};}
    function place(x,kind){x.layer=L[kind];x.col=BIM_CTX_COL[kind];x.locked=true;n[kind]++;ids.push(x.id);}
    var selWas=A3D.sel,setWas=(A3D.selSet||[]).slice();
    var pinfo=feats?bimCtxPairParts(feats):{of:{},has:{}},nParts=0,nWhole=0,lowParts=0;   /* __acad3dV139 */
    var nRoofs={},nNoRoof={};   /* __acad3dV140 */
    pushUndo();
    undoSuspend=true;
    try{
      /* what this fetch brings replaces what an earlier one brought, kind by kind */
      A3D.objs=A3D.objs.filter(function(x){return !(x.context&&repl[x.context.kind]);});
      if(A3D.sel&&!objById(A3D.sel)){A3D.sel=null;A3D.selSet=[];}
      L=bimCtxLayers();   /* new layers are not made current, so the current one stays */
      if(terOk){
        base=bimCtxDatum();
        if(base===null){
          var e0=bimCtxElevAt(ter,a.org.lon,a.org.lat);
          if(isFinite(e0)){base=Math.round(e0*100)/100;A3D.site.terrainBase=base;}
        }
        var pts=[],N=BIM_CTX_GRID,gx,gz,gg,ev;
        for(i=0;i<N;i++)for(j=0;j<N;j++){
          gx=a.cx-a.half+2*a.half*i/(N-1);gz=a.cz-a.half+2*a.half*j/(N-1);
          gg=bimModelToGeo(gx,gz,a.org);ev=bimCtxElevAt(ter,gg[0],gg[1]);
          if(isFinite(ev)&&base!==null)pts.push([gx,gz,Math.round((ev-base)*1000)/1000,'','Terrain Tiles']);
        }
        o=pts.length>=3?bimCreateTerrain(pts,{format:'Terrarium',units:'m',source:'AWS Terrain Tiles',zoom:ter.range.z},true):null;
        if(o){
          o.name='Terrain';o.layer=L.terrain;o.locked=true;
          o.context={kind:'terrain',source:'AWS Terrain Tiles',credit:BIM_CTX_TERRAIN_CREDIT+(ter.sources.length?' ('+ter.sources.join(', ')+')':''),
            zoom:ter.range.z,sources:ter.sources,datum:base,fetched:date};
          n.terrain=1;ids.push(o.id);
        }
      }
      for(i=0;feats&&i<feats.length;i++){
        f=feats[i];
        if(f.kind==='buildings'){
          var hh=bimOsmHeight(f.tags),rg=f.part?bimOsmPartRange(f.tags):{min:0,minFrom:'',h:hh.h,from:hh.from};   /* __acad3dV139 */
          if(!f.part&&pinfo.has[i]){nWhole++;continue;}   /* its parts stand for it */
          if(f.part&&rg.h-rg.min<0.01){lowParts++;continue;}
          for(j=0;j<f.outer.length;j++){
            var Pp=sketchCCW(f.outer[j]),mesh=null;
            if(Pp.length<3)continue;
            var rf=null;   /* __acad3dV140: the roof, from its tags */
            try{rf=bimOsmRoof(Pp,f.tags,y0+rg.min,rg.h-rg.min,rg.from);}catch(eR){console.warn('[BIM] roof',eR);rf={shape:String(f.tags['roof:shape']),why:'the roof could not be built'};}
            try{mesh=(rf&&rf.mesh)?rf.mesh:padMesh(Pp,y0+rg.min,rg.h-rg.min);}catch(eM){mesh=null;}
            if(!mesh)continue;
            var cx=0,cz=0,q2;
            for(q2=0;q2<Pp.length;q2++){cx+=Pp[q2][0];cz+=Pp[q2][1];}
            o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',pos:[0,0,0],mesh:mesh,
              name:String(f.tags.name||((f.tags['addr:housenumber']&&f.tags['addr:street'])?f.tags['addr:housenumber']+' '+f.tags['addr:street']:('Building '+(n.buildings+1)))).slice(0,60)};
            c=rec('buildings',f);c.height=Math.round(hh.h*100)/100;c.heightFrom=hh.from;c.footprint=Pp;
            c.ground=ground([cx/Pp.length,cz/Pp.length]);
            c.lod=f.part?'1.3':'1.2';   /* __acad3dV139 */
            if(rf&&rf.mesh){   /* __acad3dV140: LOD2 */
              c.roof=rf.info;c.lod='2.0';c.height=Math.round((rg.min+rf.total)*100)/100;
              nRoofs[rf.info.shape]=(nRoofs[rf.info.shape]||0)+1;
            }else if(rf&&rf.why){c.roofSkipped={shape:rf.shape,why:rf.why};nNoRoof[rf.shape]=(nNoRoof[rf.shape]||0)+1;}
            if(f.part){
              nParts++;c.buildingPart=true;
              if(rg.min>0){c.minHeight=Math.round(rg.min*100)/100;c.minFrom=rg.minFrom;}
              var pw=pinfo.of[i+'_'+j];
              if(pw){
                var pf=feats[pw.f];
                c.building={osm:pf.osm,id:pf.id,name:String(pf.tags.name||'').slice(0,60)};
                c.standFp=sketchCCW(pf.outer[pw.r]);
                if(!f.tags.name)o.name=String((pf.tags.name||('Building '+pf.osm+' '+pf.id))+' part').slice(0,60);
              }
            }
            if(f.inner.length){c.courtyards=f.inner.length;yards+=f.inner.length;c.holes=f.inner.map(function(r){return r.map(function(p){return [p[0],p[1]];});});}   /* __acad3dV168: the courtyards' outlines, for the ground covered */
            o.context=c;A3D.objs.push(o);place(o,'buildings');
            if(hh.from==='assumed')assumed++;
          }
        }else if(f.kind==='trees'&&(f.point||f.line)){   /* __acad3dV157: a tree, or a tree every 8 m along a row */
          var tp=f.point?[f.point]:bimCtxAlong(f.line.pts,BIM_CTX_TREE_STEP),th2=bimTagMetres(f.tags.height)||bimCtxTreeH(),cd2=bimTagMetres(f.tags.diameter_crown)||th2*bimEntCrownRatio(f.tags),lf2=bimEntLeafOf(f.tags);   /* __acad3dV169: the crown by leaf type */
          for(j=0;j<tp.length&&n.trees<BIM_CTX_TREES_MAX;j++){
            var gy=y0+(hAt(tp[j][0],tp[j][1]));
            o=bimAddPoint(tp[j][0],tp[j][1],gy,L.trees);
            o.name=String(f.tags.species||f.tags.genus||'Tree')+' '+(n.trees+1);o.context=rec('trees',f);
            o.context.height=th2;o.context.crown=Math.round(cd2*100)/100;o.context.leaf=lf2;
            if(!f.point)o.context.row=true;
            o.mesh=bimEntTreeMesh(tp[j][0],tp[j][1],gy,th2,cd2,lf2.type==='C').mesh;o.col=BIM_CTX_COL.trees;   /* __acad3dV169: a conifer a cone */
            place(o,'trees');
          }
        }else if(f.kind==='power'&&f.point){   /* __acad3dV157: a pylon */
          var tw=bimTagMetres(f.tags.height)||bimCtxTowerH(),gy2=y0+hAt(f.point[0],f.point[1]);
          o=bimAddPoint(f.point[0],f.point[1],gy2,L.power);
          o.name='Pylon '+(n.power+1);o.context=rec('power',f);o.context.height=tw;
          o.mesh=bimTowerMesh(f.point[0],f.point[1],gy2,tw);place(o,'power');
        }else{
          var label=f.tags.name||f.tags.ref||(BIM_CTX_LABEL[f.kind]+' '+(n[f.kind]+1));
          if(f.line){
            o=bimMakeImportedSketch(f.line.pts,f.kind==='power'?y0+bimCtxLineH():y0,f.line.closed);   /* __acad3dV157: a power line hung */
            if(o){o.name=String(label).slice(0,60);o.context=rec(f.kind,f);place(o,f.kind);bimCtxSurface(o,f,hAt,y0,nb3);}
          }
          for(j=0;j<f.outer.length+f.inner.length;j++){
            var ring=j<f.outer.length?f.outer[j]:f.inner[j-f.outer.length];
            if(ring.length<3)continue;
            o=bimMakeImportedSketch(ring,y0,true);
            if(!o)continue;
            o.name=String(label).slice(0,60);o.context=rec(f.kind,f);
            if(j>=f.outer.length)o.context.part='hole';
            place(o,f.kind);
            if(j<f.outer.length&&!f.inner.length)bimCtxArea3d(o,f,ring,hAt,y0,nb3);   /* __acad3dV157 */
          }
        }
      }
      if(st.onGround)bimCtxStand(true);   /* __acad3dV137: the buildings on the terrain */
      A3D.site.context=A3D.site.context||{};
      A3D.site.context.last={date:date,counts:n,radius:st.radius,errors:bad.slice(),truncated:trunc,server:osm&&osm.ok?bimMapHost(osm.server):null,std:bimStdStamp(BIM_STD_DATA.context.ts)};   /* __acad3dV167: std */
      if(nParts)A3D.site.context.last.parts=nParts;   /* __acad3dV139 */
      var nR=0,kR;for(kR in nRoofs)if(nRoofs.hasOwnProperty(kR))nR+=nRoofs[kR];
      if(nR)A3D.site.context.last.roofs=nR;   /* __acad3dV140 */
    }finally{undoSuspend=false;}
    /* the selection stays what it was: the surface maker selects what it makes */
    A3D.sel=objById(selWas)?selWas:null;A3D.sel2=null;
    A3D.selSet=setWas.filter(function(id){return !!objById(id);});
    refreshTree();refreshLayers();refreshProps();paint();saveSoon();
    var said=[],kk;
    for(i=0;i<BIM_CTX_KINDS.length;i++){kk=BIM_CTX_KINDS[i];if(repl[kk])said.push(n[kk]+' '+(kk==='terrain'?(n[kk]?'surface':'surfaces'):BIM_CTX_LABEL[kk].toLowerCase()));}
    a3dToast('Site context: '+said.join(', ')+(assumed?'; '+assumed+' building height'+(assumed===1?'':'s')+' assumed ('+bimCtxDefaultH()+' m)':'')+
      (yards?'; '+yards+' courtyard'+(yards===1?'':'s')+' filled':'')+(trunc?'; stopped at '+BIM_CTX_MAX_FEATURES+' features':'')+
      (nParts?'; '+nParts+' building part'+(nParts===1?'':'s')+' at their own heights (LOD1.3)':'')+   /* __acad3dV139 */
      (lowParts?'; '+lowParts+' part'+(lowParts===1?'':'s')+' with no height above '+(lowParts===1?'its':'their')+' base left out':'')+
      bimRoofCountText(nRoofs,nNoRoof)+   /* __acad3dV140 */
      (nb3.bridges?'; '+nb3.bridges+' bridge'+(nb3.bridges===1?'':'s')+' raised':'')+(nb3.tunnels?'; '+nb3.tunnels+' tunnel'+(nb3.tunnels===1?'':'s')+' below ground':'')+   /* __acad3dV157 */
      (bad.length?'; '+bad.join('; '):''));
    return {counts:n,ids:ids,errors:bad,truncated:trunc,assumed:assumed,courtyards:yards,parts:nParts,wholes:nWhole,lowParts:lowParts,roofs:nRoofs,notRoofed:nNoRoof,
      bridges:nb3.bridges,tunnels:nb3.tunnels,surfaces:nb3.surfaces};   /* __acad3dV157 */
  }
  /* __acad3dV157: points about every step metres along a line, evenly, both its ends among them (a
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
      c.bridge=true;c.deck=ly*bimCtxDeck();
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
  /* CONTEXTREMOVE: every context object, in one undo step */
  function bimCtxRemove(){
    var n=0,i;
    for(i=0;i<A3D.objs.length;i++)if(A3D.objs[i].context)n++;
    if(!n){a3dToast('There is no site context to remove');return 0;}
    pushUndo();
    A3D.objs=A3D.objs.filter(function(o){return !o.context;});
    if(A3D.sel&&!objById(A3D.sel)){A3D.sel=null;A3D.sel2=null;A3D.selSet=[];}
    refreshTree();refreshProps();paint();saveSoon();
    a3dToast('Site context removed: '+n+' object'+(n===1?'':'s'));
    return n;
  }
  /* the context's credits, for the line over the viewport; OSM's left out when the map already gives it */
  function bimCtxCreditHtml(skipOsm){
    var osm=false,ter=null,i,o,p=[];
    for(i=0;i<A3D.objs.length;i++){o=A3D.objs[i];if(!o.context)continue;if(o.context.kind==='terrain')ter=o.context;else osm=true;}
    if(osm&&!skipOsm)p.push('Context <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">\u00a9 OpenStreetMap contributors</a>');
    if(ter)p.push(bimEsc(ter.credit||BIM_CTX_TERRAIN_CREDIT));
    return p.join(' \u00b7 ');
  }
