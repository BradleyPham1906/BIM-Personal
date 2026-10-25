  /* ================= __acad3dV106: tributary areas and the column load takedown =================
     Our own arithmetic, stated so it can be checked by hand:
       - A column carries the slab of the level its top reaches (within 50 mm), in its building.
       - Its tributary area is the part of that level's floors and roofs nearer to it than to any
         other column carrying the same level: the perpendicular-bisector (Voronoi) cell, clipped
         to each slab outline. On a regular grid that is exactly the half-bay rule.
       - Floor load = tributary area x the level's dead and live load (kPa, set in Levels).
       - Axial load = its own floor load + the axial load of every column standing on it (same
         plan position within 50 mm, base at its top), taken down from the top.
       - Reported unfactored (D, L, D+L) and as 1.2D + 1.6L (ASCE 7 strength combination 2).
     Not included, and labelled where the numbers show: live load reduction (ASCE 7 4.7; leaving
     it out is conservative), column and beam self-weight, walls carrying floor load, slab
     openings, lateral load. A level with no load set leaves every total that needs it blank,
     never 0. */
  var BIM_TRIB_TOL=0.05;
  function bimTribLevel(id){var i;for(i=0;i<A3D.levels.length;i++)if(A3D.levels[i].id===id)return A3D.levels[i];return null;}
  /* Keeps the side of nx*x + nz*z = c where the value is <= c (Sutherland-Hodgman, one edge).
     A concave slab stays area-exact, because a half-plane is convex. */
  function bimClipHalfPlane(poly,nx,nz,c){
    var out=[],n=poly.length,i,a,b,da,db,t;
    for(i=0;i<n;i++){
      a=poly[i];b=poly[(i+1)%n];
      da=nx*a[0]+nz*a[1]-c;db=nx*b[0]+nz*b[1]-c;
      if(da<=0)out.push(a);
      if((da<0&&db>0)||(da>0&&db<0)){t=da/(da-db);out.push([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t]);}
    }
    return out;
  }
  /* The slabs a level holds up, in world plan coordinates: floors by their profile, roofs by their
     footprint -- roof load is taken on the horizontal projection. */
  function bimTribSlabs(levelId){
    var out=[],i,o,q,pts;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='solid'||!o.bim||bimObjectLevelId(o)!==levelId)continue;
      pts=o.bim.type==='floor'?o.bim.profile:(o.bim.type==='roof'?o.bim.footprint:null);
      if(!pts||pts.length<3)continue;
      q=bimObjOffset(o);
      out.push({id:o.id,name:o.name,pts:pts.map(function(p){return [p[0]+q[0],p[1]+q[2]];})});
    }
    return out;
  }
  function bimTribColumns(){
    var out=[],i,o,q,lv,b;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(!(o.t==='solid'&&o.bim&&o.bim.type==='column'&&o.bim.center))continue;
      q=bimObjOffset(o);lv=bimTribLevel(bimObjectLevelId(o));b=(o.bim.baseY||0)+q[1];
      out.push({id:o.id,name:o.name,x:o.bim.center[0]+q[0],z:o.bim.center[1]+q[2],base:b,top:b+(o.bim.height||0),
        level:lv,bldg:lv?lv.buildingId:null,area:0,cells:[],notes:[],missing:[],carriedBy:''});
    }
    out.sort(function(a,b){return a.id<b.id?-1:(a.id>b.id?1:0);});
    return out;
  }
  function bimTribSupported(c){
    var best=null,bd=BIM_TRIB_TOL,i,lv,d;
    for(i=0;i<A3D.levels.length;i++){
      lv=A3D.levels[i];
      if(c.bldg&&lv.buildingId&&lv.buildingId!==c.bldg)continue;
      d=Math.abs((lv.elev||0)-c.top);
      if(d<=bd){best=lv;bd=d;}
    }
    return best;
  }
  /* "B-3": the grid lines a point lies on (within 50 mm), letters before numbers, the way a column
     location mark reads. Blank off the grid. */
  function bimGridMark(x,z){
    var on=[],i,g,dx,dz,L;
    for(i=0;i<A3D.grids.length;i++){
      g=A3D.grids[i];dx=g.p2[0]-g.p1[0];dz=g.p2[1]-g.p1[1];L=Math.sqrt(dx*dx+dz*dz);
      if(L>1e-9&&Math.abs((x-g.p1[0])*dz-(z-g.p1[1])*dx)/L<=BIM_TRIB_TOL)on.push(String(g.name));
    }
    on.sort(function(a,b){var na=/^\d/.test(a),nb=/^\d/.test(b);if(na!==nb)return na?1:-1;return a<b?-1:(a>b?1:0);});
    return on.join('-');
  }
  function bimColumnLoads(){
    var cols=bimTribColumns(),byLvl={},res={rows:[],levels:[],cells:{}},i,j,k,m,c,d,u,lv,cell,slabs,sup,slabArea,onCols,twin,nx,nz,ca,low,both;
    var blank=function(v){return v==null?'':v;};
    for(i=0;i<cols.length;i++){
      c=cols[i];c.sup=bimTribSupported(c);
      if(c.sup)(byLvl['k'+c.sup.id]=byLvl['k'+c.sup.id]||[]).push(c);else c.notes.push('reaches no level');
    }
    for(i=0;i<A3D.levels.length;i++){
      lv=A3D.levels[i];slabs=bimTribSlabs(lv.id);sup=byLvl['k'+lv.id]||[];slabArea=0;onCols=0;
      for(k=0;k<slabs.length;k++)slabArea+=bimPolyArea(slabs[k].pts);
      for(j=0;j<sup.length;j++){
        c=sup[j];twin=null;
        for(k=0;k<j;k++)if(Math.abs(sup[k].x-c.x)<1e-6&&Math.abs(sup[k].z-c.z)<1e-6){twin=sup[k];break;}
        if(twin){c.notes.push('same place as '+twin.name+', which takes the area');continue;}
        if(!slabs.length)c.notes.push('no floor or roof on '+lv.name);
        for(k=0;k<slabs.length;k++){
          cell=slabs[k].pts.slice();
          for(m=0;m<sup.length&&cell.length>=3;m++){
            d=sup[m];nx=d.x-c.x;nz=d.z-c.z;
            if(d===c||(Math.abs(nx)<1e-6&&Math.abs(nz)<1e-6))continue;
            cell=bimClipHalfPlane(cell,nx,nz,nx*(c.x+d.x)/2+nz*(c.z+d.z)/2);
          }
          if(cell.length>=3){ca=bimPolyArea(cell);if(ca>1e-9){c.area+=ca;c.cells.push(cell);}}
        }
        onCols+=c.area;
      }
      if(slabs.length||sup.length)res.levels.push({levelId:lv.id,level:lv.name,slabArea:slabArea,onColumns:onCols,
        columns:sup.length,unsupported:Math.max(0,slabArea-onCols)});
    }
    for(i=0;i<cols.length;i++){
      c=cols[i];
      if(!c.sup){c.fD=0;c.fL=0;continue;}
      c.fD=c.sup.dl==null?null:c.area*c.sup.dl;c.fL=c.sup.ll==null?null:c.area*c.sup.ll;
      if(c.sup.dl==null||c.sup.ll==null)c.missing.push(c.sup.name);
    }
    /* the takedown: highest base first, so every column above is finished before the one under it */
    var order=cols.slice().sort(function(a,b){return b.base-a.base;});
    for(i=0;i<order.length;i++){
      c=order[i];c.aD=c.fD;c.aL=c.fL;
      for(j=0;j<i;j++){
        u=order[j];
        if(u.carriedBy||u.bldg!==c.bldg||Math.abs(u.base-c.top)>BIM_TRIB_TOL||Math.abs(u.x-c.x)>BIM_TRIB_TOL||Math.abs(u.z-c.z)>BIM_TRIB_TOL)continue;
        u.carriedBy=c.name;
        c.aD=(c.aD==null||u.aD==null)?null:c.aD+u.aD;
        c.aL=(c.aL==null||u.aL==null)?null:c.aL+u.aL;
        for(k=0;k<u.missing.length;k++)if(c.missing.indexOf(u.missing[k])<0)c.missing.push(u.missing[k]);
      }
    }
    for(i=0;i<cols.length;i++){
      c=cols[i];
      if(!c.carriedBy)for(k=0;k<A3D.objs.length;k++){
        d=A3D.objs[k];
        if(d.t==='solid'&&d.bim&&d.bim.type==='footing'&&(d.bim.hostId===c.id||d.hostId===c.id)){c.carriedBy=d.name;break;}
      }
      if(!c.carriedBy){
        low=null;
        for(k=0;k<A3D.levels.length;k++){lv=A3D.levels[k];if((!c.bldg||lv.buildingId===c.bldg)&&(low===null||(lv.elev||0)<low))low=lv.elev||0;}
        if(low!==null&&c.base>low+BIM_TRIB_TOL)c.notes.push('nothing under it');
      }
      if(c.missing.length)c.notes.push('loads not set on '+c.missing.join(', '));
      both=c.aD!=null&&c.aL!=null;
      res.rows.push({id:c.id,name:c.name,grid:bimGridMark(c.x,c.z),level:c.level?c.level.name:'-',
        supports:c.sup?c.sup.name:'',supportsId:c.sup?c.sup.id:'',tribArea:c.sup?c.area:'',
        floorD:blank(c.fD),floorL:blank(c.fL),axialD:blank(c.aD),axialL:blank(c.aL),
        service:both?c.aD+c.aL:'',factored:both?1.2*c.aD+1.6*c.aL:'',carriedBy:c.carriedBy,note:c.notes.join('; '),
        x:c.x,z:c.z,base:c.base});
      res.cells[c.id]=c.cells;
    }
    res.rows.sort(function(a,b){
      var ga=a.grid||('~'+a.name),gb=b.grid||('~'+b.name);
      if(ga!==gb)return ga<gb?-1:1;
      return b.base-a.base;
    });
    return res;
  }
  /* __acad3dV106: TRIBAREA. The slab on the ACTIVE level, cut into the cells of the columns that
     carry it (the ones below), each labelled with its column and area -- the numbers the Column
     Loads schedule uses, drawn from the same call. A view toggle for checking, not saved. */
