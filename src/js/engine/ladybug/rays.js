  /* ================= __acad3dV172c: the sky's program and the rays, in the Ladybug worker =================
     reference/research-ladybug-sun-radiation.md (5b, 6). These functions are not called by the engine: the worker is
     made from their text (bimLbStart), so each reads nothing but its arguments and the worker's globals.
     - bimLbWasiRun: a WASI command (wasi_snapshot_preview1) run with stdin given and stdout, stderr gathered; the
       twelve imports Radiance's gendaymtx asks for, no files, no folders (reference/experiments/v172c-sky/).
     - bimLbBvhBuild, bimLbBvhBlocked: an any-hit ray test over a bounding-volume hierarchy of the model's
       triangles: the same Moller-Trumbore test and thresholds as V143's bimRayTri (|det| under 1e-12 misses, a hit
       beyond 1e-6), split at the median of the longest axis, leaves of up to four. Measured against the app's own
       rays: the same answer for 362,440 rays; 20,000 faces in about 3 s (reference/experiments/v172c-rays/).
     - bimLbStudyVecs, bimLbStudyRows: Ladybug's directions turned into the app's frame and north, and the rows of a
       study's matrix: the cosine where a direction is seen (radiation, as Radiance's rcontrib gives Ladybug), or 1
       where the sun is (direct sun hours). */
  function bimLbWasiRun(module,args,stdin){
    var mem=null,inPos=0,out=[],err=[],code=0,EXIT={},enc=[],i,j,s,b;
    stdin=stdin||new Uint8Array(0);
    function u8(){return new Uint8Array(mem.buffer);}
    function dv(){return new DataView(mem.buffer);}
    for(i=0;i<args.length;i++){s=unescape(encodeURIComponent(String(args[i])));b=[];for(j=0;j<s.length;j++)b.push(s.charCodeAt(j));b.push(0);enc.push(b);}
    function gather(fd,iovs,n,nw){
      var d=dv(),t=0,k,p,l,a=u8();
      for(k=0;k<n;k++){p=d.getUint32(iovs+8*k,true);l=d.getUint32(iovs+8*k+4,true);(fd===1?out:err).push(a.slice(p,p+l));t+=l;}
      dv().setUint32(nw,t,true);return 0;
    }
    var W={
      args_sizes_get:function(pc,ps){var t=0,k,d=dv();for(k=0;k<enc.length;k++)t+=enc[k].length;d.setUint32(pc,enc.length,true);d.setUint32(ps,t,true);return 0;},
      args_get:function(pv,pb){var d=dv(),a=u8(),k;for(k=0;k<enc.length;k++){d.setUint32(pv+4*k,pb,true);a.set(enc[k],pb);pb+=enc[k].length;}return 0;},
      fd_write:function(fd,iovs,n,nw){if(fd!==1&&fd!==2)return 8;return gather(fd,iovs,n,nw);},
      fd_read:function(fd,iovs,n,nr){
        if(fd!==0)return 8;
        var d=dv(),a=u8(),t=0,k,p,l,m;
        for(k=0;k<n;k++){p=d.getUint32(iovs+8*k,true);l=d.getUint32(iovs+8*k+4,true);
          m=Math.min(l,stdin.length-inPos);if(m<=0)break;a.set(stdin.subarray(inPos,inPos+m),p);inPos+=m;t+=m;if(m<l)break;}
        dv().setUint32(nr,t,true);return 0;
      },
      fd_seek:function(fd,lo,whence,np){
        if(fd!==0)return 70;
        var off=typeof lo==='bigint'?Number(lo):lo,base=whence===0?0:whence===1?inPos:stdin.length,p=base+off,d;
        if(p<0||p>stdin.length)return 28;
        inPos=p;d=dv();d.setUint32(np,p,true);d.setUint32(np+4,0,true);return 0;
      },
      fd_close:function(){return 0;},
      fd_fdstat_get:function(fd,st){if(fd>2)return 8;var d=dv(),k;for(k=0;k<24;k++)d.setUint8(st+k,0);d.setUint8(st,2);return 0;},
      fd_fdstat_set_flags:function(){return 0;},
      fd_prestat_get:function(){return 8;},
      fd_prestat_dir_name:function(){return 8;},
      path_open:function(){return 44;},
      proc_exit:function(c){code=c;throw EXIT;}
    };
    var inst=new WebAssembly.Instance(module,{wasi_snapshot_preview1:W});
    mem=inst.exports.memory;
    try{inst.exports._start();}catch(e){if(e!==EXIT)throw e;}
    function cat(L){var n=0,k,r,o=0;for(k=0;k<L.length;k++)n+=L[k].length;r=new Uint8Array(n);for(k=0;k<L.length;k++){r.set(L[k],o);o+=L[k].length;}return r;}
    return {code:code,stdout:cat(out),stderr:cat(err)};
  }
  /* T: the triangles, nine numbers each (x, y, z of three corners) */
  function bimLbBvhBuild(T){
    var n=T.length/9,C=new Float64Array(n*3),idx=new Int32Array(n),i,k,B=[],L=[],R=[],S=[],N=[];
    for(i=0;i<n;i++){for(k=0;k<3;k++)C[i*3+k]=(T[i*9+k]+T[i*9+3+k]+T[i*9+6+k])/3;idx[i]=i;}
    function node(a,b){
      var id=N.length,bx=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity],cb=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity],j,q,t,v,ax,ex,part,m,l,r;
      N.push(0);L.push(-1);R.push(-1);S.push(a);
      for(j=a;j<b;j++){t=idx[j];
        for(q=0;q<9;q++){v=T[t*9+q];ax=q%3;if(v<bx[ax])bx[ax]=v;if(v>bx[ax+3])bx[ax+3]=v;}
        for(q=0;q<3;q++){if(C[t*3+q]<cb[q])cb[q]=C[t*3+q];if(C[t*3+q]>cb[q+3])cb[q+3]=C[t*3+q];}}
      for(q=0;q<6;q++)B[id*6+q]=bx[q];
      if(b-a<=4){N[id]=b-a;return id;}
      ax=0;ex=cb[3]-cb[0];if(cb[4]-cb[1]>ex){ax=1;ex=cb[4]-cb[1];}if(cb[5]-cb[2]>ex)ax=2;
      part=Array.prototype.slice.call(idx.subarray(a,b));
      part.sort(function(u,w){return C[u*3+ax]-C[w*3+ax];});
      for(j=0;j<part.length;j++)idx[a+j]=part[j];
      m=(a+b)>>1;l=node(a,m);r=node(m,b);L[id]=l;R[id]=r;
      return id;
    }
    if(n)node(0,n);
    return {T:T,idx:idx,B:new Float64Array(B),L:new Int32Array(L),R:new Int32Array(R),S:new Int32Array(S),N:new Int32Array(N),stack:new Int32Array(256)};
  }
  /* is the ray from o along d stopped by a triangle ahead of o? */
  function bimLbBvhBlocked(H,o,d){
    if(!H.N.length)return false;
    var st=H.stack,sp=0,B=H.B,T=H.T,id,k,q,t0,t1,a,c,tt,miss,dk,ok,iv,j,tr,
        inv=[Math.abs(d[0])<1e-12?0:1/d[0],Math.abs(d[1])<1e-12?0:1/d[1],Math.abs(d[2])<1e-12?0:1/d[2]],
        e1x,e1y,e1z,e2x,e2y,e2z,px,py,pz,det,id2,sx,sy,sz,u,v,qx,qy,qz;
    st[sp++]=0;
    while(sp){
      id=st[--sp];t0=0;t1=Infinity;miss=false;q=id*6;
      for(k=0;k<3&&!miss;k++){
        dk=d[k];ok=o[k];iv=inv[k];
        if(Math.abs(dk)<1e-12){if(ok<B[q+k]||ok>B[q+k+3])miss=true;continue;}
        a=(B[q+k]-ok)*iv;c=(B[q+k+3]-ok)*iv;if(a>c){tt=a;a=c;c=tt;}
        if(a>t0)t0=a;if(c<t1)t1=c;if(t0>t1)miss=true;
      }
      if(miss)continue;
      if(H.L[id]>=0){st[sp++]=H.L[id];st[sp++]=H.R[id];continue;}
      for(j=H.S[id];j<H.S[id]+H.N[id];j++){
        tr=H.idx[j]*9;
        e1x=T[tr+3]-T[tr];e1y=T[tr+4]-T[tr+1];e1z=T[tr+5]-T[tr+2];e2x=T[tr+6]-T[tr];e2y=T[tr+7]-T[tr+1];e2z=T[tr+8]-T[tr+2];
        px=d[1]*e2z-d[2]*e2y;py=d[2]*e2x-d[0]*e2z;pz=d[0]*e2y-d[1]*e2x;det=e1x*px+e1y*py+e1z*pz;
        if(Math.abs(det)<1e-12)continue;
        id2=1/det;sx=o[0]-T[tr];sy=o[1]-T[tr+1];sz=o[2]-T[tr+2];u=(sx*px+sy*py+sz*pz)*id2;
        if(u<0||u>1)continue;
        qx=sy*e1z-sz*e1y;qy=sz*e1x-sx*e1z;qz=sx*e1y-sy*e1x;v=(d[0]*qx+d[1]*qy+d[2]*qz)*id2;
        if(v<0||u+v>1)continue;
        if((e2x*qx+e2y*qy+e2z*qz)*id2>1e-6)return true;
      }
    }
    return false;
  }
  /* Ladybug's directions (x east, y north, z up) into the app's (x east, y up, -z north), turned by the site's true
     north as bimSunVector turns the sun; with ground, the sky's patches then each reversed, as Ladybug's
     sky_intersection_matrix orders them */
  function bimLbStudyVecs(V,tn,ground){
    var out=[],i,e,a,x,y,z,L,r=Math.PI/180;
    for(i=0;i<V.length;i++){
      x=V[i][0];y=V[i][1];z=V[i][2];L=Math.sqrt(x*x+y*y+z*z)||1;
      e=Math.asin(Math.max(-1,Math.min(1,z/L)));a=Math.atan2(x,y)+tn*r;
      out.push([Math.cos(e)*Math.sin(a),Math.sin(e),-Math.cos(e)*Math.cos(a)]);
    }
    if(ground){L=out.length;for(i=0;i<L;i++)out.push([-out[i][0],-out[i][1],-out[i][2]]);}
    return out;
  }
  /* rows a..b of the matrix: S holds six numbers a sensor (the point, already off its face, and the unit normal) */
  function bimLbStudyRows(H,S,V,a,b,cosine){
    var nv=V.length,M=new Float64Array((b-a)*nv),i,j,o,n,c,v;
    for(i=a;i<b;i++){
      o=[S[i*6],S[i*6+1],S[i*6+2]];n=[S[i*6+3],S[i*6+4],S[i*6+5]];
      for(j=0;j<nv;j++){v=V[j];c=n[0]*v[0]+n[1]*v[1]+n[2]*v[2];
        if(c>0&&!bimLbBvhBlocked(H,o,v))M[(i-a)*nv+j]=cosine?c:1;}
    }
    return M;
  }
