  /* ================= __acad3dV107: shadows on the ground =================
     Each solid's mesh is projected along the sun's rays onto the ground plane (the lowest level's
     elevation) and the model's own plan footprint is cut out of the result, so a building never
     shades its own roof in plan. Floors lying on the ground (top within 0.5 m) neither cast nor
     hide shadows: a shadow falling across a ground slab is drawn on it, as if at ground level.
     Only the ground receives shadows -- not roofs, walls or other buildings -- and only in plan. */
  function bimSunVector(sun){
    var a=(sun.azimuth+bimTrueNorthDeg())*Math.PI/180,e=sun.elevation*Math.PI/180;
    return [Math.cos(e)*Math.sin(a),Math.sin(e),-Math.cos(e)*Math.cos(a)];
  }
  function bimShadowGround(){
    var g=null,i;
    for(i=0;i<A3D.levels.length;i++)if(g===null||(A3D.levels[i].elev||0)<g)g=A3D.levels[i].elev||0;
    return g===null?0:g;
  }
  function bimShadowCasters(g,date){   /* __acad3dV169: the date, for the trees' leaves */
    var out=[],i,k,o,q,v,w,top;
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='solid'||!o.mesh||!o.mesh.v||!o.mesh.f||!o.mesh.v.length)continue;
      if(!bimLayerShown(o))continue;   /* __acad3dV121 */
      q=bimObjOffset(o);v=o.mesh.v;w=[];top=-Infinity;
      for(k=0;k<v.length;k++){w.push([v[k][0]+q[0],v[k][1]+q[1],v[k][2]+q[2]]);if(w[k][1]>top)top=w[k][1];}
      if(o.bim&&o.bim.type==='floor'&&top<=g+0.5)continue;
      out.push({id:o.id,w:w,f:bimEntBare(o,date)?o.mesh.f.slice(0,o.asset.cf):o.mesh.f});
    }
    return out;
  }
  function bimShadowPoint(p,s,g){var h=Math.max(0,p[1]-g);return [p[0]-s[0]*h/s[1],p[2]-s[2]*h/s[1]];}
  /* Every face of every caster, projected by proj, filled as ONE nonzero path of triangles all
     wound the same way on screen, so overlapping faces union instead of cancelling. */
  function bimFillProjected(c,list,proj,V,W,H,g){
    var n=0,i,j,k,it,sp,f,a,b,d,cr,pp;
    c.beginPath();
    for(i=0;i<list.length;i++){
      it=list[i];sp=[];
      for(k=0;k<it.w.length;k++){pp=proj(it.w[k]);sp.push(toScreen([pp[0],g,pp[1]],V,W,H));}
      for(k=0;k<it.f.length;k++){
        f=it.f[k];
        if(!f||f.length<3)continue;
        for(j=1;j+1<f.length;j++){
          a=sp[f[0]];b=sp[f[j]];d=sp[f[j+1]];
          if(!a||!b||!d)continue;
          cr=(b[0]-a[0])*(d[1]-a[1])-(b[1]-a[1])*(d[0]-a[0]);
          if(Math.abs(cr)<1e-9)continue;
          c.moveTo(a[0],a[1]);
          if(cr>0){c.lineTo(b[0],b[1]);c.lineTo(d[0],d[1]);}else{c.lineTo(d[0],d[1]);c.lineTo(b[0],b[1]);}
          c.closePath();n++;
        }
      }
    }
    c.fill('nonzero');
    return n;
  }
  function drawSunShadows(ctx,V,W,H){
    A3D.lastShadows=null;
    if(!A3D.showSun||!bimCameraIsPlan())return;   /* __acad3dV119 */
    var sun=bimSunNow();
    if(sun.missing){A3D.lastShadows={missing:sun.missing};return;}
    if(!(sun.elevation>0)){A3D.lastShadows={night:true,elevation:sun.elevation,azimuth:sun.azimuth};return;}
    try{
      var s=bimSunVector(sun),g=bimShadowGround(),list=bimShadowCasters(g),cv=ctx.canvas,n;
      var oc=A3D.shadowCanvas||(A3D.shadowCanvas=document.createElement('canvas'));
      if(oc.width!==cv.width)oc.width=cv.width;
      if(oc.height!==cv.height)oc.height=cv.height;
      var c2=oc.getContext('2d');
      c2.setTransform(1,0,0,1,0,0);c2.clearRect(0,0,oc.width,oc.height);
      c2.setTransform(ctx.getTransform());
      c2.globalCompositeOperation='source-over';c2.fillStyle='#000000';
      n=bimFillProjected(c2,list,function(p){return bimShadowPoint(p,s,g);},V,W,H,g);
      c2.globalCompositeOperation='destination-out';
      bimFillProjected(c2,list,function(p){return [p[0],p[2]];},V,W,H,g);
      c2.globalCompositeOperation='source-over';
      ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.globalAlpha=0.32;ctx.drawImage(oc,0,0);ctx.restore();
      A3D.lastShadows={elevation:sun.elevation,azimuth:sun.azimuth,vector:s,ground:g,casters:list.length,triangles:n};
    }catch(e){
      console.warn('[BIM] shadows',e);
      if(!A3D.shadowWarned){A3D.shadowWarned=true;a3dToast('Shadows could not be drawn');}
    }
  }
  /* __acad3dV107: the sun path -- the sun's track on the solstices and the March equinox of the
     study year, hour dots, and the sun now -- as a polar diagram (altitude 90 at the centre, the
     horizon at the rim), turned so that its north is the plan's TRUE north, measured through the
     same projection as the north arrow. In plan only; a view toggle, not saved. */
  function drawSunPath(ctx,V,W,H){
    A3D.lastSunPath=null;
    if(!A3D.showSun||!bimCameraIsPlan()||A3D.sheetCapture)return;   /* __acad3dV119 */
    var st=bimSunStudy();   /* __acad3dV171d: a place tried; each date's own offset below */
    if(!bimSunNum(st.lat)||!bimSunNum(st.lon)||!bimSunNum(st.tz))return;
    ctx.save();
    try{
      var rad=Math.PI/180,tn=bimTrueNorthDeg()*rad,c=A3D.cam,i,k,p,q,sp,first,pts,top;
      var p0=toScreen([c.tx,0,c.tz],V,W,H),pn=toScreen([c.tx+Math.sin(tn),0,c.tz-Math.cos(tn)],V,W,H),
          pe=toScreen([c.tx+Math.sin(tn+Math.PI/2),0,c.tz-Math.cos(tn+Math.PI/2)],V,W,H);
      var nx=pn[0]-p0[0],ny=pn[1]-p0[1],ex=pe[0]-p0[0],ey=pe[1]-p0[1],nl=Math.sqrt(nx*nx+ny*ny),el=Math.sqrt(ex*ex+ey*ey);
      if(!(nl>1e-9&&el>1e-9))throw new Error('no plan direction');
      nx/=nl;ny/=nl;ex/=el;ey/=el;
      var sr=bimSafeViewRect(),R=66,pad=24,S=2*(R+pad),box=[sr.x+12,sr.y+sr.h-12-S-6,S,S+6],cx=box[0]+R+pad,cy=box[1]+R+pad+6;
      var at=function(az,alt){var r=R*(90-alt)/90,a=az*rad;return [cx+r*(Math.cos(a)*nx+Math.sin(a)*ex),cy+r*(Math.cos(a)*ny+Math.sin(a)*ey)];};
      ctx.globalAlpha=1;ctx.setLineDash([]);
      ctx.fillStyle='rgba(22,26,32,0.9)';ctx.fillRect(box[0],box[1],box[2],box[3]);
      ctx.strokeStyle='rgba(255,255,255,0.18)';ctx.lineWidth=1;ctx.strokeRect(box[0]+0.5,box[1]+0.5,box[2]-1,box[3]-1);
      ctx.strokeStyle='rgba(255,255,255,0.22)';
      for(k=0;k<3;k++){ctx.beginPath();ctx.arc(cx,cy,R*(90-k*30)/90,0,2*Math.PI);ctx.stroke();}
      ctx.font='10px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#c9d3dd';
      for(k=0;k<4;k++){p=at(k*90,-14);ctx.fillText(['N','E','S','W'][k],p[0],p[1]);}
      ctx.textAlign='left';
      ctx.fillText(Math.abs(st.lat).toFixed(2)+(st.lat>=0?' N  ':' S  ')+Math.abs(st.lon).toFixed(2)+(st.lon>=0?' E':' W'),box[0]+6,box[1]+9);
      var yr=String(st.date).slice(0,4),days=[[yr+'-06-21','#ffb347','Jun 21'],[yr+'-03-20','#e8d36a','Mar 20'],[yr+'-12-21','#8ab4f8','Dec 21']],paths=[];
      ctx.textAlign='right';
      for(k=0;k<days.length;k++){ctx.fillStyle=days[k][1];ctx.fillText(days[k][2],box[0]+box[2]-6,box[1]+9+k*11);}
      for(k=0;k<days.length;k++){
        pts=[];top=-90;first=true;
        ctx.strokeStyle=days[k][1];ctx.fillStyle=days[k][1];ctx.lineWidth=1.4;ctx.beginPath();
        for(i=0;i<1440;i+=10){
          sp=bimSunCalc(st.lat,st.lon,bimSunTzAt(st,days[k][0],'12:00'),days[k][0],bimPad2(i/60)+':'+bimPad2(i%60));
          if(!sp||!(sp.elevation>0)){first=true;continue;}
          pts.push([sp.azimuth,sp.elevation]);
          if(sp.elevation>top)top=sp.elevation;
          q=at(sp.azimuth,sp.elevation);
          if(first){ctx.moveTo(q[0],q[1]);first=false;}else ctx.lineTo(q[0],q[1]);
        }
        ctx.stroke();
        for(i=0;i<1440;i+=60){
          sp=bimSunCalc(st.lat,st.lon,bimSunTzAt(st,days[k][0],'12:00'),days[k][0],bimPad2(i/60)+':00');
          if(sp&&sp.elevation>0){q=at(sp.azimuth,sp.elevation);ctx.beginPath();ctx.arc(q[0],q[1],1.8,0,2*Math.PI);ctx.fill();}
        }
        paths.push({date:days[k][0],pts:pts,max:pts.length?top:null});
      }
      var now=bimSunNow(),sunPt=null;
      if(!now.missing&&now.elevation>0){
        q=at(now.azimuth,now.elevation);sunPt=[now.azimuth,now.elevation];
        ctx.beginPath();ctx.arc(q[0],q[1],4.5,0,2*Math.PI);ctx.fillStyle='#ffe066';ctx.fill();
        ctx.strokeStyle='rgba(0,0,0,0.8)';ctx.lineWidth=1.2;ctx.stroke();
      }
      if(bimAnimLive()&&A3D_ANIM.sunTime&&sunPt){ctx.textAlign='left';ctx.fillStyle='#ffe066';ctx.fillText((A3D_ANIM.sunDate?bimSunDayText(A3D_ANIM.sunDate,true)+' ':'')+A3D_ANIM.sunTime,box[0]+6,box[1]+box[3]-9);}   /* __acad3dV170: the time, while it plays; __acad3dV171d: the date through the year */
      A3D.lastSunPath={north:[nx,ny],east:[ex,ey],center:[cx,cy],radius:R,box:box,paths:paths,sun:sunPt};
    }catch(e){
      console.warn('[BIM] sun path',e);
      if(!A3D.sunPathWarned){A3D.sunPathWarned=true;a3dToast('The sun path could not be drawn');}
    }
    ctx.restore();
  }
  function bimToggleSun(){
    A3D.showSun=!A3D.showSun;
    paint();
    if(!A3D.showSun){a3dToast('Sun study off');return false;}
    var sun=bimSunNow(),st=sun.settings;
    if(sun.missing)a3dToast('Sun study: set the site '+sun.missing.join(', ')+' in Properties, with nothing selected (Site: Location)');
    else if(!bimCameraIsPlan())a3dToast('Sun study on: shadows and the sun path are drawn in plan');   /* __acad3dV119 */
    else if(!(sun.elevation>0))a3dToast('Sun study: the sun is below the horizon at '+st.time+' on '+st.date);
    else a3dToast('Sun study: '+st.time+' on '+st.date+', altitude '+sun.elevation.toFixed(1)+', azimuth '+sun.azimuth.toFixed(1)+' deg (NOAA)');
    return true;
  }
  function bimTribCentroid(cells){
    var W=0,X=0,Z=0,i,j,p,q,n,a,x,z,cr;
    for(i=0;i<cells.length;i++){
      p=cells[i];n=p.length;a=0;x=0;z=0;
      for(j=0;j<n;j++){q=p[(j+1)%n];cr=p[j][0]*q[1]-q[0]*p[j][1];a+=cr;x+=(p[j][0]+q[0])*cr;z+=(p[j][1]+q[1])*cr;}
      if(Math.abs(a)>1e-12){W+=Math.abs(a);X+=x/(3*a)*Math.abs(a);Z+=z/(3*a)*Math.abs(a);}
    }
    return W>0?[X/W,Z/W]:null;
  }
  function drawTribAreas(ctx,V,W,H){
    A3D.lastTribDrawn=null;
    if(!A3D.showTrib||A3D.section||A3D.sheetCapture)return;
    var lv=bimTribLevel(A3D.activeLevel),res,i,j,s,r,cells,sp,ok,ce,cp,txt,drawn=[],y;
    if(!lv)return;
    y=lv.elev||0;
    ctx.save();
    try{
      res=bimColumnLoads();
      ctx.font='11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
      for(i=0;i<res.rows.length;i++){
        r=res.rows[i];
        if(r.supportsId!==lv.id)continue;
        cells=res.cells[r.id]||[];
        ctx.setLineDash([6,4]);ctx.lineWidth=1.2;ctx.strokeStyle='#f0b429';
        for(j=0;j<cells.length;j++){
          sp=cells[j].map(function(p){return toScreen([p[0],y,p[1]],V,W,H);});
          ok=sp.every(function(q){return q&&isFinite(q[0])&&isFinite(q[1]);});
          if(!ok)continue;
          ctx.beginPath();ctx.moveTo(sp[0][0],sp[0][1]);
          for(s=1;s<sp.length;s++)ctx.lineTo(sp[s][0],sp[s][1]);
          ctx.closePath();ctx.stroke();
        }
        ce=bimTribCentroid(cells);cp=ce?toScreen([ce[0],y,ce[1]],V,W,H):null;
        if(cp){
          txt=r.name+'  '+Number(r.tribArea).toFixed(2)+' m²';
          ctx.setLineDash([]);ctx.lineWidth=3;ctx.strokeStyle='rgba(0,0,0,0.75)';ctx.strokeText(txt,cp[0],cp[1]);
          ctx.fillStyle='#ffe8a3';ctx.fillText(txt,cp[0],cp[1]);
        }
        drawn.push({id:r.id,name:r.name,area:r.tribArea,cells:cells.length});
      }
      A3D.lastTribDrawn={levelId:lv.id,items:drawn};
    }catch(e){
      console.warn('[BIM] tributary areas',e);
      if(!A3D.tribWarned){A3D.tribWarned=true;a3dToast('Tributary areas could not be drawn');}
    }
    ctx.restore();
  }
  /* __acad3dV105b: the area plan overlay. It reads bimLevelAreas, which is what the schedule and
     the toast read, so the ring on screen and the number in the schedule cannot disagree. */
  function bimToggleAreaPlan(){
    A3D.showArea=!A3D.showArea;
    paint();
    if(!A3D.showArea){a3dToast('Area plan hidden');return false;}
    var a=bimLevelAreas(A3D.activeLevel);
    if(a.gross===null)a3dToast('Area plan on '+a.level+': nothing to measure'+(a.note?' -- '+a.note:''));
    else a3dToast('Area plan on '+a.level+': gross '+a.gross.toFixed(2)+' m\u00b2, net '+a.net.toFixed(2)+
                  ' m\u00b2'+(a.efficiency===null?'':' ('+a.efficiency.toFixed(0)+'% efficient)')+
                  (a.occupants===null?'':', '+a.occupants+' occupant'+(a.occupants===1?'':'s')));
    return true;
  }
  function drawAreaPlan(ctx,V,W,H){
    A3D.lastAreaDrawn=null;
    if(!A3D.showArea||A3D.section||A3D.sheetCapture)return;
    var lv=bimLevelById(A3D.activeLevel);
    if(!lv)return;
    var a,y=lv.elev||0,i,j,sp,ok,cx,cz,cp,txt,p,s;
    ctx.save();
    try{
      a=bimLevelAreas(A3D.activeLevel);
      ctx.font='11px sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
      for(i=0;i<a.rings.length;i++){
        sp=[];ok=true;cx=0;cz=0;
        for(j=0;j<a.rings[i].pts.length;j++){
          p=a.rings[i].pts[j];
          cx+=p[0];cz+=p[1];
          s=toScreen([p[0],y,p[1]],V,W,H);
          if(!s||!isFinite(s[0])||!isFinite(s[1])){ok=false;break;}
          sp.push(s);
        }
        if(!ok||sp.length<3)continue;
        cx/=a.rings[i].pts.length;cz/=a.rings[i].pts.length;
        ctx.beginPath();ctx.moveTo(sp[0][0],sp[0][1]);
        for(j=1;j<sp.length;j++)ctx.lineTo(sp[j][0],sp[j][1]);
        ctx.closePath();
        ctx.fillStyle='rgba(90,209,160,0.10)';ctx.fill();
        ctx.setLineDash([9,5]);ctx.lineWidth=1.6;ctx.strokeStyle='#5ad1a0';ctx.stroke();
        cp=toScreen([cx,y,cz],V,W,H);
        if(cp&&isFinite(cp[0])&&isFinite(cp[1])){
          txt=a.rings[i].area.toFixed(2)+' m\u00b2 gross';
          ctx.setLineDash([]);ctx.lineWidth=3;ctx.strokeStyle='rgba(0,0,0,0.75)';ctx.strokeText(txt,cp[0],cp[1]);
          ctx.fillStyle='#d7fff0';ctx.fillText(txt,cp[0],cp[1]);
        }
      }
      A3D.lastAreaDrawn={levelId:a.levelId,rings:a.rings.length,gross:a.gross,net:a.net,
                         efficiency:a.efficiency,occupants:a.occupants,note:a.note};
    }catch(eAD){
      if(!A3D.areaWarned){A3D.areaWarned=true;a3dToast('The area plan could not be drawn');}
      console.warn('[BIM] Area plan draw failed: ',eAD);
    }
    ctx.restore();
  }
