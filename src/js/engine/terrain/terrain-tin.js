  /* ================= __acad3dV108: terrain -- TIN, contours, earthwork =================
     A surface is its survey points and nothing else: the triangles are derived from them whenever
     they are needed (Delaunay, Bowyer-Watson), never stored beside them. Each triangle is a plane,
     so a contour crosses it as one straight segment, placed by linear interpolation along the two
     edges it cuts. Earthwork is measured on the same triangles against a flat pad -- the TIN prism
     method: over one triangle the height between surface and pad is linear, so the volume over
     any piece of it is the piece's area times the height at the piece's centroid; each triangle is
     cut to the pad outline, then split where the surface crosses the pad elevation. That is exact
     for the triangulated surface -- the surface itself is only as good as the survey. */
  function bimDelaunay(P){
    var n=P.length,i,k,t,a,b,c,minX=Infinity,minZ=Infinity,maxX=-Infinity,maxZ=-Infinity;
    if(n<3)return [];
    for(i=0;i<n;i++){
      if(P[i][0]<minX)minX=P[i][0];if(P[i][0]>maxX)maxX=P[i][0];
      if(P[i][1]<minZ)minZ=P[i][1];if(P[i][1]>maxZ)maxZ=P[i][1];
    }
    var d=Math.max(maxX-minX,maxZ-minZ)||1,mx=(minX+maxX)/2,mz=(minZ+maxZ)/2;
    var V=P.concat([[mx-100*d,mz-100*d],[mx+100*d,mz-100*d],[mx,mz+100*d]]);
    function circ(i0,i1,i2){
      var ax=V[i0][0],az=V[i0][1],bx=V[i1][0],bz=V[i1][1],cx=V[i2][0],cz=V[i2][1];
      var D=2*(ax*(bz-cz)+bx*(cz-az)+cx*(az-bz));
      if(Math.abs(D)<1e-12)return null;
      var a2=ax*ax+az*az,b2=bx*bx+bz*bz,c2=cx*cx+cz*cz;
      var ux=(a2*(bz-cz)+b2*(cz-az)+c2*(az-bz))/D,uz=(a2*(cx-bx)+b2*(ax-cx)+c2*(bx-ax))/D;
      return {x:ux,z:uz,r2:(ax-ux)*(ax-ux)+(az-uz)*(az-uz)};
    }
    var tris=[{v:[n,n+1,n+2],c:circ(n,n+1,n+2)}];
    for(i=0;i<n;i++){
      var px=V[i][0],pz=V[i][1],bad=[],keep=[],cnt={},key,cc,dd,nc;
      for(t=0;t<tris.length;t++){
        cc=tris[t].c;
        dd=(px-cc.x)*(px-cc.x)+(pz-cc.z)*(pz-cc.z);
        if(dd<cc.r2*(1-1e-12))bad.push(tris[t]);else keep.push(tris[t]);
      }
      for(t=0;t<bad.length;t++)for(k=0;k<3;k++){
        a=bad[t].v[k];b=bad[t].v[(k+1)%3];key=a<b?a+'_'+b:b+'_'+a;
        cnt[key]=(cnt[key]||0)+1;
      }
      for(t=0;t<bad.length;t++)for(k=0;k<3;k++){
        a=bad[t].v[k];b=bad[t].v[(k+1)%3];
        if(cnt[a<b?a+'_'+b:b+'_'+a]!==1)continue;
        nc=circ(a,b,i);
        if(nc)keep.push({v:[a,b,i],c:nc});
      }
      tris=keep;
      /* a true triangulation of i+1 points inside the super-triangle has 2i+3 triangles; far past
         that, it has come apart -- stop and say so rather than grow without end */
      if(tris.length>2*i+12)throw new Error('the triangulation came apart at point '+(i+1));
    }
    /* Every triangle is counter-clockwise and non-degenerate by construction: the super-triangle
       is, each new one is a boundary edge of the cavity kept in its old direction and closed at a
       point inside the cavity, to that edge's left, and circ() refuses a collinear three. So the
       only thing left to do is drop the triangles on the super-triangle's corners. */
    var out=[];
    for(t=0;t<tris.length;t++){
      a=tris[t].v[0];b=tris[t].v[1];c=tris[t].v[2];
      if(a<n&&b<n&&c<n)out.push([a,b,c]);
    }
    return out;
  }
  /* The derived triangles, cached against the survey they came from. The cache is not saved. */
  var BIM_TIN_CACHE={};
  function bimTerrainTin(o){
    if(!o||o.t!=='terrain'||!o.survey)return null;
    var key=(o.rev||0)+':'+o.survey.length+':'+(o.faces?o.faces.length:'-')+':'+JSON.stringify(o.breaklines||[])+':'+JSON.stringify(o.boundary||[]),
      c=BIM_TIN_CACHE[o.id],q=bimObjOffset(o);
    if(!c||c.key!==key)c=BIM_TIN_CACHE[o.id]=bimTinBuild(o,key);   /* __acad3dV144: own faces, breaklines, a boundary */
    var P=o.survey.map(function(s){return [s[0]+q[0],s[1]+q[2]];}),H=o.survey.map(function(s){return s[2]+q[1];});
    c.extra.forEach(function(e){P.push([e[0]+q[0],e[1]+q[2]]);H.push(e[2]+q[1]);});
    return {P:P,H:H,tris:c.tris,outside:c.outside,constraints:c.constraints,unforced:c.unforced,ownFaces:!!c.ownFaces,nSurvey:o.survey.length};
  }
  function bimTerrainRange(tin){
    var lo=Infinity,hi=-Infinity,i;
    for(i=0;i<tin.H.length;i++){if(tin.H[i]<lo)lo=tin.H[i];if(tin.H[i]>hi)hi=tin.H[i];}
    return [lo,hi];
  }
  /* The owner's interval, or one derived from the relief: the first of the usual steps giving
     at most twelve contours. */
  function bimTerrainInterval(o,tin){
    var v=parseFloat(o&&o.interval),r,raw,steps=[0.1,0.2,0.25,0.5,1,2,2.5,5,10,20,25,50,100],i;
    if(isFinite(v)&&v>0)return v;
    r=bimTerrainRange(tin);raw=Math.max(r[1]-r[0],0.1)/12;
    for(i=0;i<steps.length;i++)if(steps[i]>=raw)return steps[i];
    return 100;
  }
  /* Every multiple of step inside the surface's range; every fifth is an index contour. A vertex
     exactly at a level counts as above it, so a contour through a vertex is drawn once. */
  function bimContours(tin,step){
    var r=bimTerrainRange(tin),k0=Math.ceil(r[0]/step-1e-9),k1=Math.floor(r[1]/step+1e-9),out=[],k,t,e,lev,segs,tr,cr,a,b,ha,hb,u;
    if(!(step>0)||k1-k0>2000)return [];
    for(k=k0;k<=k1;k++){
      lev=k*step;segs=[];
      for(t=0;t<tin.tris.length;t++){
        tr=tin.tris[t];cr=[];
        for(e=0;e<3;e++){
          a=tr[e];b=tr[(e+1)%3];ha=tin.H[a]-lev;hb=tin.H[b]-lev;
          if((ha>=0)!==(hb>=0)){u=ha/(ha-hb);cr.push([tin.P[a][0]+(tin.P[b][0]-tin.P[a][0])*u,tin.P[a][1]+(tin.P[b][1]-tin.P[a][1])*u]);}
        }
        if(cr.length===2)segs.push(cr);
      }
      if(segs.length)out.push({level:lev,index:k%5===0,segs:segs});
    }
    return out;
  }
  function bimEarthCentroid(p){
    var a=0,x=0,z=0,i,j,cr;
    for(i=0;i<p.length;i++){j=(i+1)%p.length;cr=p[i][0]*p[j][1]-p[j][0]*p[i][1];a+=cr;x+=(p[i][0]+p[j][0])*cr;z+=(p[i][1]+p[j][1])*cr;}
    return Math.abs(a)<1e-15?null:[x/(3*a),z/(3*a)];
  }
  /* poly cut to one TIN triangle (counter-clockwise, so its inside is left of every edge). */
  function bimClipToTri(poly,tri,P){
    var k,a,b,nx,nz,out=poly;
    for(k=0;k<3&&out.length>=3;k++){
      a=P[tri[k]];b=P[tri[(k+1)%3]];nx=b[1]-a[1];nz=-(b[0]-a[0]);
      out=bimClipHalfPlane(out,nx,nz,nx*a[0]+nz*a[1]);
    }
    return out;
  }
  function bimCutFill(tin,pad,padY){
    var cut=0,fill=0,on=0,t,tr,A,B,C,piece,area,det,dB,dC,gx,gz,g0,cp,fp,cc,pa;
    for(t=0;t<tin.tris.length;t++){
      tr=tin.tris[t];
      piece=bimClipToTri(pad,tr,tin.P);
      if(piece.length<3)continue;
      area=bimPolyArea(piece);
      if(!(area>1e-12))continue;
      on+=area;
      A=tin.P[tr[0]];B=tin.P[tr[1]];C=tin.P[tr[2]];
      det=(B[0]-A[0])*(C[1]-A[1])-(C[0]-A[0])*(B[1]-A[1]);
      dB=tin.H[tr[1]]-tin.H[tr[0]];dC=tin.H[tr[2]]-tin.H[tr[0]];
      gx=(dB*(C[1]-A[1])-(B[1]-A[1])*dC)/det;
      gz=((B[0]-A[0])*dC-(C[0]-A[0])*dB)/det;
      g0=(tin.H[tr[0]]-padY)-gx*A[0]-gz*A[1];
      cp=bimClipHalfPlane(piece,-gx,-gz,g0);
      fp=bimClipHalfPlane(piece,gx,gz,-g0);
      if(cp.length>=3){cc=bimEarthCentroid(cp);if(cc)cut+=bimPolyArea(cp)*Math.max(0,gx*cc[0]+gz*cc[1]+g0);}
      if(fp.length>=3){cc=bimEarthCentroid(fp);if(cc)fill+=bimPolyArea(fp)*Math.max(0,-(gx*cc[0]+gz*cc[1]+g0));}
    }
    pa=bimPolyArea(pad);
    return {cut:cut,fill:fill,net:cut-fill,padArea:pa,onSurface:on,outside:Math.max(0,pa-on)};
  }
  /* Survey text: one point per line, columns in the order the owner names. A line that is not
     numbers where numbers belong -- a header, a note -- is skipped and reported by line number. */
  var BIM_SURVEY_FORMATS={PNEZD:['p','n','e','z','d'],PENZD:['p','e','n','z','d'],NEZ:['n','e','z'],ENZ:['e','n','z']};
  var BIM_SURVEY_UNITS={m:1,ft:0.3048,usft:1200/3937};
  function bimParseSurvey(text,fmt){
    var cols=BIM_SURVEY_FORMATS[fmt],rows=String(text==null?'':text).split(/\r?\n/),out=[],bad=[],i,k,line,parts,rec,ok,v,x;
    if(!cols)return {error:'Unknown column order '+fmt,points:[],bad:[]};
    for(i=0;i<rows.length;i++){
      line=rows[i].replace(/^\s+|\s+$/g,'');
      if(!line||/^[#;]/.test(line))continue;
      parts=line.split(/\s*[,\t;]\s*|\s+/);rec={};ok=true;
      for(k=0;k<cols.length;k++){
        v=parts[k];
        if(cols[k]==='d'){rec.d=parts.slice(k).join(' ');break;}
        if(cols[k]==='p'){rec.p=v==null?'':String(v);continue;}
        x=parseFloat(v);
        if(v==null||!isFinite(x)||!/^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/.test(v)){ok=false;break;}
        rec[cols[k]]=x;
      }
      if(ok&&isFinite(rec.n)&&isFinite(rec.e)&&isFinite(rec.z))out.push(rec);else bad.push(i+1);
    }
    return {points:out,bad:bad};
  }
  /* Survey north and east to model x and z, turned by True North exactly as a traverse is
     (project north is -Z); elevation above the base to model y. */
  function bimSurveyToModel(pts,units,base,tnDeg){
    var u=BIM_SURVEY_UNITS[units]||1,tn=(tnDeg||0)*Math.PI/180,ct=Math.cos(tn),st=Math.sin(tn);
    return pts.map(function(r){
      var dE=(r.e-base.e)*u,dN=(r.n-base.n)*u;
      return [dE*ct+dN*st,dE*st-dN*ct,(r.z-base.z)*u,r.p||'',r.d||''];
    });
  }
