  /* ---- Zoom window ----
     Rubber-band a rectangle, un-project its corners onto the active level's plane, and frame that
     world box through the V79 safe-rectangle framing -- so what the user drew a box around lands
     where they can reach it rather than behind the tool dock.

     A rectangle whose corners will not un-project (the plane edge-on to the camera) is refused with
     a console warning rather than framed as a NaN box. */
  function bimStartZoomWindow(){
    if(A3D.sk){a3dToast('Finish the current tool first');return false;}
    A3D.zoomWindow=true;
    if(el.cv)el.cv.style.cursor='crosshair';
    a3dToast('Zoom window: drag a rectangle over the area to zoom into');
    paint();
    return true;
  }
  function bimCancelZoomWindow(){
    A3D.zoomWindow=false;
    if(el.cv)el.cv.style.cursor='';
    paint();
  }
  function bimApplyZoomWindow(x0,y0,x1,y1){
    var lvl=bimGetActiveLevel(),elev=lvl?lvl.elev:0;
    var lx=Math.min(x0,x1),rx=Math.max(x0,x1),ty=Math.min(y0,y1),by=Math.max(y0,y1);
    if(rx-lx<6||by-ty<6){a3dToast('That window was too small — drag a larger rectangle');return false;}
    var corners=[[lx,ty],[rx,ty],[rx,by],[lx,by]],i,pts=[];
    for(i=0;i<corners.length;i++){
      var g=groundPoint(corners[i][0],corners[i][1],elev);
      if(!g){
        console.warn('[BIM] Zoom window: the active level plane is edge-on to the camera, so the '+
                     'rectangle cannot be un-projected.');
        a3dToast('Tilt the view a little — the level plane is edge-on');
        return false;
      }
      pts.push(g);
    }
    var mn=[1e9,elev,1e9],mx=[-1e9,elev,-1e9];
    for(i=0;i<pts.length;i++){
      if(pts[i][0]<mn[0])mn[0]=pts[i][0];
      if(pts[i][0]>mx[0])mx[0]=pts[i][0];
      if(pts[i][2]<mn[2])mn[2]=pts[i][2];
      if(pts[i][2]>mx[2])mx[2]=pts[i][2];
    }
    bimFrameBounds({mn:mn,mx:mx});
    a3dToast('Zoomed to window');
    return true;
  }
  function drawZoomWindow(ctx){
    if(!drag||!drag.zwin||!drag.moved)return;
    ctx.save();
    ctx.strokeStyle='#4ea1ff';
    ctx.fillStyle='rgba(78,161,255,0.12)';
    ctx.lineWidth=1.3;
    ctx.setLineDash([5,4]);
    var rx=Math.min(drag.x0,drag.x),ry=Math.min(drag.y0,drag.y);
    ctx.fillRect(rx,ry,Math.abs(drag.x-drag.x0),Math.abs(drag.y-drag.y0));
    ctx.strokeRect(rx,ry,Math.abs(drag.x-drag.x0),Math.abs(drag.y-drag.y0));
    ctx.restore();
  }
  /* ---- Save image ----
     The viewport canvas itself, downloaded. Local-first: no server, no upload. */
  function bimSaveViewportPng(){
    if(!el.cv){a3dToast('No viewport to capture');return false;}
    try{
      var url=el.cv.toDataURL('image/png');
      var a=document.createElement('a');
      a.href=url;
      a.download=bimFileStem()+'-'+String(A3D.view||'view').replace(/[^\w\-]+/g,'_')+'.png';   /* __acad3dV115 */
      document.body.appendChild(a);a.click();document.body.removeChild(a);
      a3dToast('Saved '+a.download);
      return true;
    }catch(eI){
      console.warn('[BIM] Could not export the viewport as a PNG',eI);
      a3dToast('The viewport could not be saved as an image');
      return false;
    }
  }
  function bimWireRailStack(){
    var rail=document.getElementById('a3d-rail');
    if(!rail||rail.__a3dRailWired)return false;
    rail.__a3dRailWired=true;
    rail.addEventListener('click',function(ev){
      var m=ev.target&&ev.target.closest?ev.target.closest('[data-a3drumenu]'):null;
      if(m){ev.preventDefault();ev.stopPropagation();bimOpenRailMenu(m.getAttribute('data-a3drumenu'),m);return;}
      var a=ev.target&&ev.target.closest?ev.target.closest('[data-a3druact]'):null;
      if(a){
        ev.preventDefault();ev.stopPropagation();
        bimCloseRailPop();
        if(a.getAttribute('data-a3druact')==='capture')bimSaveViewportPng();
        return;
      }
    },true);
    document.addEventListener('click',function(ev){
      if(ev.target&&ev.target.closest&&(ev.target.closest('#a3d-rupop')||
         ev.target.closest('#a3d-railutil')))return;
      bimCloseRailPop();
    });
    /* Escape is handled in the app's own key chain (search __acad3dV83 in the Escape
       block), not here: that handler is registered at load and calls
       stopImmediatePropagation, so a second listener added later is never reached. */
    return true;
  }
