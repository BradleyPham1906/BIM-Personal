  function vsub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
  function vcross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function vdot(a,b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
  function vnorm(a){var l=Math.sqrt(vdot(a,a))||1;return [a[0]/l,a[1]/l,a[2]/l];}
  var LIGHT=vnorm([0.5,0.8,0.6]);
  function faceNormal(pts){
    var n=[0,0,0],i,p,q;
    for(i=0;i<pts.length;i++){
      p=pts[i];q=pts[(i+1)%pts.length];
      n[0]+=(p[1]-q[1])*(p[2]+q[2]);
      n[1]+=(p[2]-q[2])*(p[0]+q[0]);
      n[2]+=(p[0]-q[0])*(p[1]+q[1]);
    }
    return vnorm(n);
  }

  function mkMesh(v,f){return {v:v,f:f};}
  function mkBoxP(lx,ly,lz){
    var hx=lx/2,hy=ly/2,hz=lz/2;
    var v=[[-hx,-hy,-hz],[hx,-hy,-hz],[hx,hy,-hz],[-hx,hy,-hz],[-hx,-hy,hz],[hx,-hy,hz],[hx,hy,hz],[-hx,hy,hz]];
    var f=[[0,1,2,3],[5,4,7,6],[4,0,3,7],[1,5,6,2],[3,2,6,7],[4,5,1,0]];
    return mkMesh(v,f);
  }
  function mkCylP(r,h,ang,n){
    if(!ang||ang>360)ang=360;
    var full=ang>=360;
    var steps=full?n:Math.max(2,Math.round(n*ang/360));
    var m=full?steps:steps+1;
    var v=[],f=[],i,hh=h/2,bot=[],top=[];
    for(i=0;i<m;i++){
      var a=(i/steps)*(ang/180)*Math.PI;
      v.push([Math.cos(a)*r,-hh,Math.sin(a)*r]);
      v.push([Math.cos(a)*r,hh,Math.sin(a)*r]);
    }
    for(i=0;i<steps;i++){
      var j=full?(i+1)%steps:i+1;
      f.push([i*2,j*2,j*2+1,i*2+1]);
    }
    for(i=0;i<m;i++){bot.push(i*2);top.push((m-1-i)*2+1);}
    if(!full){
      var c0=v.length;
      v.push([0,-hh,0]);v.push([0,hh,0]);
      bot.push(c0);top.push(c0+1);
      f.push([0,1,c0+1,c0]);
      f.push([(m-1)*2,c0,c0+1,(m-1)*2+1]);
    }
    f.push(bot);f.push(top);
    return mkMesh(v,f);
  }
  function mkConeP(r1,r2,h,n){
    var v=[],f=[],i,hh=h/2,bot=[],top=[];
    var a1=r1>0.001,a2=r2>0.001;
    for(i=0;i<n;i++){
      var a=i/n*Math.PI*2;
      v.push([Math.cos(a)*(a1?r1:0.001),-hh,Math.sin(a)*(a1?r1:0.001)]);
      v.push([Math.cos(a)*(a2?r2:0.001),hh,Math.sin(a)*(a2?r2:0.001)]);
    }
    for(i=0;i<n;i++){
      var j=(i+1)%n;
      f.push([i*2,j*2,j*2+1,i*2+1]);
    }
    if(a1){for(i=0;i<n;i++)bot.push(i*2);f.push(bot);}
    if(a2){for(i=0;i<n;i++)top.push((n-1-i)*2+1);f.push(top);}
    return mkMesh(v,f);
  }
  function mkSphereP(r,rows,cols){
    var v=[],f=[],i,j;
    for(i=0;i<=rows;i++){
      var ph=-Math.PI/2+i/rows*Math.PI,y=Math.sin(ph)*r,rr=Math.cos(ph)*r;
      for(j=0;j<cols;j++){var th=j/cols*Math.PI*2;v.push([Math.cos(th)*rr,y,Math.sin(th)*rr]);}
    }
    for(i=0;i<rows;i++)for(j=0;j<cols;j++){
      var a2=i*cols+j,b2=i*cols+(j+1)%cols,c2=(i+1)*cols+(j+1)%cols,d2=(i+1)*cols+j;
      f.push([a2,b2,c2,d2]);
    }
    return mkMesh(v,f);
  }
  function mkEllipsoidP(r1,r2,rows,cols){
    var m=mkSphereP(1,rows,cols),i;
    for(i=0;i<m.v.length;i++){
      m.v[i][0]*=r2;m.v[i][1]*=r1;m.v[i][2]*=r2;
    }
    return m;
  }
  function mkTorusP(R,r,seg,tube){
    var v=[],f=[],i,j;
    for(i=0;i<seg;i++){
      var u=i/seg*Math.PI*2,cu=Math.cos(u),su=Math.sin(u);
      for(j=0;j<tube;j++){
        var t=j/tube*Math.PI*2,ct=Math.cos(t),st2=Math.sin(t);
        v.push([(R+r*ct)*cu,r*st2,(R+r*ct)*su]);
      }
    }
    for(i=0;i<seg;i++)for(j=0;j<tube;j++){
      var a3=i*tube+j,b3=((i+1)%seg)*tube+j,c3=((i+1)%seg)*tube+(j+1)%tube,d3=i*tube+(j+1)%tube;
      f.push([a3,b3,c3,d3]);
    }
    return mkMesh(v,f);
  }
  function mkPrismP(sides,cr,h){
    return mkCylP(cr,h,360,Math.max(3,Math.round(sides)));
  }
  function mkWedgeP(p){
    var ox=(p.Xmin+p.Xmax)/2,oy=(p.Ymin+p.Ymax)/2,oz=(p.Zmin+p.Zmax)/2;
    var v=[
      [p.Xmin-ox,p.Ymin-oy,p.Zmin-oz],[p.Xmax-ox,p.Ymin-oy,p.Zmin-oz],
      [p.Xmax-ox,p.Ymin-oy,p.Zmax-oz],[p.Xmin-ox,p.Ymin-oy,p.Zmax-oz],
      [p.X2min-ox,p.Ymax-oy,p.Z2min-oz],[p.X2max-ox,p.Ymax-oy,p.Z2min-oz],
      [p.X2max-ox,p.Ymax-oy,p.Z2max-oz],[p.X2min-ox,p.Ymax-oy,p.Z2max-oz]
    ];
    var f=[[3,2,1,0],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[3,0,4,7]];
    return mkMesh(v,f);
  }
  function mkTubeP(orr,irr,h,n){
    if(!(irr>0)||irr>=orr)return mkCylP(orr,h,360,n);
    var v=[],f=[],i,hh=h/2;
    for(i=0;i<n;i++){
      var a=i/n*Math.PI*2,c=Math.cos(a),s=Math.sin(a);
      v.push([c*orr,-hh,s*orr]);
      v.push([c*orr,hh,s*orr]);
      v.push([c*irr,-hh,s*irr]);
      v.push([c*irr,hh,s*irr]);
    }
    for(i=0;i<n;i++){
      var j=(i+1)%n;
      f.push([i*4,j*4,j*4+1,i*4+1]);
      f.push([i*4+3,j*4+3,j*4+2,i*4+2]);
      f.push([i*4+1,j*4+1,j*4+3,i*4+3]);
      f.push([i*4+2,j*4+2,j*4,i*4]);
    }
    return mkMesh(v,f);
  }

  /* Parameter names, defaults, and mesh builders for each primitive type. */
  var TYPES={
    box:{n:'Box',c:'#7f9db8',prm:[['Length',10],['Width',10],['Height',10]],
      mk:function(p){return mkBoxP(p.Length*SCALE,p.Height*SCALE,p.Width*SCALE);}},
    cyl:{n:'Cylinder',c:'#c0a377',prm:[['Radius',2],['Height',10],['Angle',360]],
      mk:function(p){return mkCylP(p.Radius*SCALE,p.Height*SCALE,p.Angle,20);}},
    sphere:{n:'Sphere',c:'#84b98c',prm:[['Radius',5]],
      mk:function(p){return mkSphereP(p.Radius*SCALE,9,16);}},
    cone:{n:'Cone',c:'#bd8a9b',prm:[['Radius1',2],['Radius2',4],['Height',10]],
      mk:function(p){return mkConeP(p.Radius1*SCALE,p.Radius2*SCALE,p.Height*SCALE,20);}},
    torus:{n:'Torus',c:'#9b8abd',prm:[['Radius1',10],['Radius2',2]],
      mk:function(p){return mkTorusP(p.Radius1*SCALE,p.Radius2*SCALE,16,10);}},
    tube:{n:'Tube',c:'#8f9db0',prm:[['OuterRadius',5],['InnerRadius',2],['Height',10]],
      mk:function(p){return mkTubeP(p.OuterRadius*SCALE,p.InnerRadius*SCALE,p.Height*SCALE,20);}},
    prism:{n:'Prism',c:'#b8a47f',prm:[['Polygon',6],['Circumradius',2],['Height',10]],
      mk:function(p){return mkPrismP(p.Polygon,p.Circumradius*SCALE,p.Height*SCALE);}},
    wedge:{n:'Wedge',c:'#7fb8b0',prm:[['Xmin',0],['Xmax',10],['Ymin',0],['Ymax',10],['Zmin',0],['Zmax',10],['X2min',2],['X2max',8],['Z2min',2],['Z2max',8]],
      mk:function(p){
        var q={},k;
        for(k in p)if(p.hasOwnProperty(k))q[k]=p[k]*SCALE;
        return mkWedgeP(q);
      }},
    ellipsoid:{n:'Ellipsoid',c:'#b87f7f',prm:[['Radius1',2],['Radius2',4]],
      mk:function(p){return mkEllipsoidP(p.Radius1*SCALE,p.Radius2*SCALE,9,16);}}
  };
  function prmDefaults(t){
    var tp=TYPES[t],o={},i;
    if(!tp)return o;
    for(i=0;i<tp.prm.length;i++)o[tp.prm[i][0]]=tp.prm[i][1];
    return o;
  }
  function mergePrm(t,given){
    var o=prmDefaults(t),k,v;
    if(given)for(k in given)if(given.hasOwnProperty(k)&&o.hasOwnProperty(k)){
      v=Number(given[k]);
      if(isFinite(v))o[k]=v;
    }
    return o;
  }
  /* Parameter validation. Returns error string or null. */
  function validatePrm(t,p){
    var k;
    for(k in p)if(p.hasOwnProperty(k)&&!isFinite(p[k]))return 'All parameters must be numbers';
    if(t==='tube'&&p.InnerRadius>=p.OuterRadius)return 'Inner radius must be smaller than outer radius';
    if(t==='prism'&&p.Polygon<3)return 'Polygon must have at least 3 sides';
    if(t==='cyl'&&(p.Angle<=0||p.Angle>360))return 'Angle must be between 0 and 360';
    if(t==='wedge'&&(p.Xmax<=p.Xmin||p.Ymax<=p.Ymin||p.Zmax<=p.Zmin))return 'Max bounds must be greater than min bounds';
    return null;
  }
  function meshOf(o){
    if(A3D.section&&A3D.section.cutMeshes&&A3D.section.cutMeshes.hasOwnProperty(o.id))return A3D.section.cutMeshes[o.id];
    if(o.mesh)return o.mesh;
    var key=o.t+'|'+JSON.stringify(o.prm||{});
    if(!A3D.meshes[key]){
      var tp=TYPES[o.t];
      if(!tp)return null;
      A3D.meshes[key]=tp.mk(mergePrm(o.t,o.prm));
    }
    return A3D.meshes[key];
  }
  function meshMinY(m){
    var y=1e9,i;
    for(i=0;i<m.v.length;i++)if(m.v[i][1]<y)y=m.v[i][1];
    return y;
  }

  function camVecs(c){
    var cy=Math.cos(c.yaw),sy=Math.sin(c.yaw),cp=Math.cos(c.pitch),sp=Math.sin(c.pitch);
    var d=[cp*sy,sp,cp*cy];
    var r=vnorm(vcross([0,1,0],d));
    var u=vcross(d,r);
    return {d:d,r:r,u:u,eye:[c.tx+d[0]*c.dist,c.ty+d[1]*c.dist,c.tz+d[2]*c.dist]};
  }

