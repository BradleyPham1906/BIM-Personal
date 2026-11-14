  /* ================= __acad3dV203: Walkthrough W1, the physics (Jolt) =================
     The narrow adapter to Jolt Physics 1.1.1 (runtime/jolt, MIT; docs/research/research-walkthrough.md, D1;
     docs/work-orders/v203/SPEC.md part 4, C-04). Every function takes the world W (or Jolt itself, J, to make one) and
     uses no other engine name, so tests/unit/walk-physics.test.mjs drives it with the committed runtime file in Node.
     Loading the file and the frame belong to walk-mode.js.
     The model is static: one Jolt mesh body per element (its key and signature, as the rendered view keeps them),
     its triangles both sides solid. The walker is Jolt's CharacterVirtual moved by ExtendedUpdate (stairs up to the
     capsule's step, held to the floor 0.3 m down, no slope steeper than the capsule's). Jolt's objects are not
     garbage collected: what the adapter makes once (vectors, filters, settings) is kept on W and destroyed by
     bimWalkPhysFree; what it makes per call is destroyed before the call returns.
     Layers: 0 the model (static), 1 the walker (moving); the walker collides with both. */
  var BIM_WALK_G=9.81,BIM_WALK_JUMP=3.5,BIM_WALK_STICK=0.3;   /* m/s2; m/s, about 0.6 m up; m */

  /* a world: the interface, the filters and the vectors reused every frame */
  function bimWalkPhys(J){
    var pairs=new J.ObjectLayerPairFilterTable(2),bpi=new J.BroadPhaseLayerInterfaceTable(2,2),st=new J.JoltSettings(),ji,W;
    pairs.EnableCollision(0,1);pairs.EnableCollision(1,1);
    bpi.MapObjectToBroadPhaseLayer(0,new J.BroadPhaseLayer(0));bpi.MapObjectToBroadPhaseLayer(1,new J.BroadPhaseLayer(1));
    st.mObjectLayerPairFilter=pairs;st.mBroadPhaseLayerInterface=bpi;
    st.mObjectVsBroadPhaseLayerFilter=new J.ObjectVsBroadPhaseLayerFilterTable(bpi,2,pairs,2);
    ji=new J.JoltInterface(st);J.destroy(st);
    W={J:J,ji:ji,ps:ji.GetPhysicsSystem(),bodies:{},n:0,ch:null,cap:null,us:null,vy:0,dirty:false,
      bpf:new J.DefaultBroadPhaseLayerFilter(ji.GetObjectVsBroadPhaseLayerFilter(),1),
      olf:new J.DefaultObjectLayerFilter(ji.GetObjectLayerPairFilter(),1),bf:new J.BodyFilter(),sf:new J.ShapeFilter(),
      vel:new J.Vec3(0,0,0),g:new J.Vec3(0,-BIM_WALK_G,0),g0:new J.Vec3(0,0,0),at:new J.RVec3(0,0,0),rs:new J.RayCastSettings()};
    W.bi=W.ps.GetBodyInterface();
    return W;
  }
  /* an element's triangles (x, y, z for each corner, nine numbers a triangle) as one static body under its key;
     the same signature is kept, another replaces it, fewer than one triangle removes it. Answers the triangles kept. */
  function bimWalkPhysMesh(W,key,sig,pos){
    var J=W.J,old=W.bodies[key],n=pos?Math.floor(pos.length/9):0,tl,i,k,t,v,r,ms,shape,bcs,body;
    if(old&&old.sig===sig)return old.n;
    if(old)bimWalkPhysDrop(W,key);
    if(n<1)return 0;
    tl=new J.TriangleList();tl.resize(n);
    for(i=0;i<n;i++){t=tl.at(i);for(k=0;k<3;k++){v=t.get_mV(k);v.x=pos[i*9+k*3];v.y=pos[i*9+k*3+1];v.z=pos[i*9+k*3+2];}}
    ms=new J.MeshShapeSettings(tl,new J.PhysicsMaterialList());J.destroy(tl);
    ms.Sanitize();   /* degenerate triangles out */
    r=ms.Create();
    if(r.HasError()){J.destroy(ms);return 0;}
    shape=r.Get();
    bcs=new J.BodyCreationSettings(shape,new J.RVec3(0,0,0),J.Quat.prototype.sIdentity(),J.EMotionType_Static,0);
    body=W.bi.CreateBody(bcs);J.destroy(bcs);J.destroy(ms);
    if(!body)return 0;
    W.bi.AddBody(body.GetID(),J.EActivation_DontActivate);
    W.bodies[key]={sig:sig,id:body.GetID(),n:n};W.n++;W.dirty=true;
    return n;
  }
  function bimWalkPhysDrop(W,key){
    var b=W.bodies[key];
    if(!b)return false;
    W.bi.RemoveBody(b.id);W.bi.DestroyBody(b.id);
    delete W.bodies[key];W.n--;W.dirty=true;
    return true;
  }
  /* the elements as they are now: items [{key, sig}], pos(item) their triangles. Up to `most` new or changed elements
     are built a call, so a large model is built across frames; the ones gone are dropped. Answers how many still wait. */
  function bimWalkPhysSync(W,items,pos,most){
    var seen={},left=0,built=0,i,it,b,k;
    for(i=0;i<items.length;i++){
      it=items[i];seen[it.key]=1;b=W.bodies[it.key];
      if(b&&b.sig===it.sig)continue;
      if(built<most){bimWalkPhysMesh(W,it.key,it.sig,pos(it));built++;}else left++;
    }
    for(k in W.bodies)if(W.bodies.hasOwnProperty(k)&&!seen[k])bimWalkPhysDrop(W,k);
    if(W.dirty&&!left){W.ps.OptimizeBroadPhase();W.dirty=false;}
    return left;
  }
  /* the walker: a capsule (bimWalkCapsule's {half, r, step, slope}) standing with its feet at p */
  function bimWalkPhysChar(W,cap,p){
    var J=W.J,cs=new J.CharacterVirtualSettings(),inner=new J.CapsuleShapeSettings(cap.half,cap.r),
      off=new J.Vec3(0,cap.half+cap.r,0),up=new J.Vec3(0,1,0),rot,sr,pl,a;
    if(W.ch)bimWalkPhysCharFree(W);
    rot=new J.RotatedTranslatedShapeSettings(off,J.Quat.prototype.sIdentity(),inner);
    sr=rot.Create();
    cs.mMass=80;cs.mMaxSlopeAngle=cap.slope;cs.mUp=up;cs.mShape=sr.Get();
    pl=new J.Plane(J.Vec3.prototype.sAxisY(),-cap.r);cs.mSupportingVolume=pl;J.destroy(pl);   /* the setters copy */
    cs.mBackFaceMode=J.EBackFaceMode_CollideWithBackFaces;   /* a wall drawn either way round is solid */
    W.at.Set(p[0],p[1],p[2]);
    W.ch=new J.CharacterVirtual(cs,W.at,J.Quat.prototype.sIdentity(),W.ps);
    J.destroy(cs);J.destroy(rot);J.destroy(off);J.destroy(up);
    W.us=new J.ExtendedUpdateSettings();
    a=new J.Vec3(0,cap.step,0);W.us.mWalkStairsStepUp=a;J.destroy(a);
    a=new J.Vec3(0,-BIM_WALK_STICK,0);W.us.mStickToFloorStepDown=a;J.destroy(a);
    W.cap=cap;W.vy=0;
    return W.ch;
  }
  function bimWalkPhysCharFree(W){
    if(!W.ch)return;
    W.J.destroy(W.ch);W.ch=null;
    if(W.us){W.J.destroy(W.us);W.us=null;}
  }
  /* one frame: v = [vx, vy, vz] from bimWalkMove; mode 'walk' (gravity, jump when asked and standing), 'fly' (no
     gravity, v as it is) or 'ghost' (through everything, the feet moved by v alone). Answers {p, ground}. */
  function bimWalkPhysStep(W,v,dt,mode,jump){
    var J=W.J,ch=W.ch,ground,p;
    if(!ch)return null;
    if(mode==='ghost'){
      p=ch.GetPosition();
      W.at.Set(p.GetX()+v[0]*dt,p.GetY()+v[1]*dt,p.GetZ()+v[2]*dt);ch.SetPosition(W.at);
      W.vy=0;
      return {p:[W.at.GetX(),W.at.GetY(),W.at.GetZ()],ground:false};
    }
    ground=ch.GetGroundState()===J.EGroundState_OnGround;
    if(mode==='fly')W.vy=v[1];
    else if(ground)W.vy=jump?BIM_WALK_JUMP:0;
    else W.vy-=BIM_WALK_G*dt;
    W.vel.Set(v[0],W.vy,v[2]);ch.SetLinearVelocity(W.vel);
    ch.ExtendedUpdate(dt,mode==='fly'?W.g0:W.g,W.us,W.bpf,W.olf,W.bf,W.sf,W.ji.GetTempAllocator());
    p=ch.GetPosition();
    if(mode!=='fly'&&W.vy>0&&ch.GetLinearVelocity().GetY()<=0)W.vy=0;   /* a ceiling stops a jump */
    return {p:[p.GetX(),p.GetY(),p.GetZ()],ground:ch.GetGroundState()===J.EGroundState_OnGround};
  }
  /* the distance from `from` along the unit vector `dir` to the first surface of the model, up to `most` metres;
     Infinity when nothing is hit. For the third-person boom and the walker's start. */
  function bimWalkPhysRay(W,from,dir,most){
    var J=W.J,o=new J.RVec3(from[0],from[1],from[2]),d=new J.Vec3(dir[0]*most,dir[1]*most,dir[2]*most),
      ray=new J.RRayCast(o,d),col=new J.CastRayClosestHitCollisionCollector(),out=Infinity;
    W.ps.GetNarrowPhaseQuery().CastRay(ray,W.rs,col,W.bpf,W.olf,W.bf,W.sf);
    if(col.HadHit())out=col.get_mHit().mFraction*most;
    J.destroy(col);J.destroy(ray);J.destroy(d);J.destroy(o);
    return out;
  }
  /* everything the world holds, and the world */
  function bimWalkPhysFree(W){
    var J=W.J,k;
    bimWalkPhysCharFree(W);
    for(k in W.bodies)if(W.bodies.hasOwnProperty(k))bimWalkPhysDrop(W,k);
    [W.bpf,W.olf,W.bf,W.sf,W.vel,W.g,W.g0,W.at,W.rs].forEach(function(o){J.destroy(o);});
    J.destroy(W.ji);W.ji=W.ps=W.bi=null;
  }
