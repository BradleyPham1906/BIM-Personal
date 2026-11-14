  /* ================= __acad3dV203: Walkthrough W1, the physics (Jolt) =================
     The narrow adapter to Jolt Physics 1.1.1 (runtime/jolt, MIT; docs/research/research-walkthrough.md, D1;
     docs/work-orders/v203/SPEC.md part 4, C-04). Every function takes the world W (or Jolt itself, J, to make one) and
     uses no other engine name, so tests/unit/walk-physics.test.mjs drives it with the committed runtime file in Node.
     Loading the file and the frame belong to walk-mode.js.
     The model is static and is ONE Jolt mesh body: each element's triangles are kept under its key and signature, as
     the rendered view keeps them, and the body is rebuilt from all of them when one changes. Not one body per element:
     with the walker against a separate body, Jolt's stair walking climbs about twice its step (a 0.40 m curb, a 1 m
     block, with a 0.206 m step), while the same triangles in one mesh stop it (C-04's probe, the note's part 7).
     The walker is Jolt's CharacterVirtual moved by ExtendedUpdate (stairs up to the capsule's step, held to the floor
     0.3 m down, no slope steeper than the capsule's). Jolt's objects are not garbage collected: what the adapter makes
     once (vectors, filters) is kept on W and destroyed by bimWalkPhysFree; what it makes per call is destroyed before
     the call returns. Layers: 0 the model (static), 1 the walker (moving); the walker collides with both. */
  var BIM_WALK_G=9.81,BIM_WALK_JUMP=3.5,BIM_WALK_STICK=0.3;   /* m/s2; m/s, about 0.6 m up; m */

  /* a world: the interface, the filters and the vectors reused every frame */
  function bimWalkPhys(J){
    var pairs=new J.ObjectLayerPairFilterTable(2),bpi=new J.BroadPhaseLayerInterfaceTable(2,2),st=new J.JoltSettings(),ji,W;
    pairs.EnableCollision(0,1);pairs.EnableCollision(1,1);
    bpi.MapObjectToBroadPhaseLayer(0,new J.BroadPhaseLayer(0));bpi.MapObjectToBroadPhaseLayer(1,new J.BroadPhaseLayer(1));
    st.mObjectLayerPairFilter=pairs;st.mBroadPhaseLayerInterface=bpi;
    st.mObjectVsBroadPhaseLayerFilter=new J.ObjectVsBroadPhaseLayerFilterTable(bpi,2,pairs,2);
    ji=new J.JoltInterface(st);J.destroy(st);
    W={J:J,ji:ji,ps:ji.GetPhysicsSystem(),parts:{},n:0,tris:0,body:null,dirty:false,ch:null,cap:null,us:null,vy:0,
      bpf:new J.DefaultBroadPhaseLayerFilter(ji.GetObjectVsBroadPhaseLayerFilter(),1),
      olf:new J.DefaultObjectLayerFilter(ji.GetObjectLayerPairFilter(),1),bf:new J.BodyFilter(),sf:new J.ShapeFilter(),
      vel:new J.Vec3(0,0,0),g:new J.Vec3(0,-BIM_WALK_G,0),g0:new J.Vec3(0,0,0),at:new J.RVec3(0,0,0),rs:new J.RayCastSettings()};
    W.bi=W.ps.GetBodyInterface();
    return W;
  }
  /* an element's triangles (x, y, z for each corner, nine numbers a triangle) kept under its key; the same signature
     keeps what is there, another replaces it, no triangle removes it. The body follows at the next bimWalkPhysBuild.
     Answers the element's triangles. */
  function bimWalkPhysMesh(W,key,sig,pos){
    var old=W.parts[key],n=pos?Math.floor(pos.length/9):0;
    if(old&&old.sig===sig)return old.n;
    if(old)bimWalkPhysDrop(W,key);
    if(n<1)return 0;
    W.parts[key]={sig:sig,pos:pos,n:n};W.n++;W.tris+=n;W.dirty=true;
    return n;
  }
  function bimWalkPhysDrop(W,key){
    var b=W.parts[key];
    if(!b)return false;
    W.tris-=b.n;delete W.parts[key];W.n--;W.dirty=true;
    return true;
  }
  /* the one body from every element's triangles, when something changed since the last build; answers the triangles
     in it. About 0.25 s for 60,000 triangles here (experiment e01), so it is built on entering the walk and after an edit. */
  function bimWalkPhysBuild(W){
    var J=W.J,i=0,k,p,j,c,t,v,tl,ms,r,bcs,body;
    if(!W.dirty)return W.tris;
    if(W.body){W.bi.RemoveBody(W.body);W.bi.DestroyBody(W.body);W.body=null;}
    W.dirty=false;
    if(W.tris<1)return 0;
    tl=new J.TriangleList();tl.resize(W.tris);
    for(k in W.parts)if(W.parts.hasOwnProperty(k)){
      p=W.parts[k].pos;
      for(j=0;j<W.parts[k].n;j++,i++){t=tl.at(i);for(c=0;c<3;c++){v=t.get_mV(c);v.x=p[j*9+c*3];v.y=p[j*9+c*3+1];v.z=p[j*9+c*3+2];}}
    }
    ms=new J.MeshShapeSettings(tl,new J.PhysicsMaterialList());J.destroy(tl);
    ms.Sanitize();   /* degenerate triangles out */
    r=ms.Create();
    if(r.HasError()){J.destroy(ms);return 0;}
    bcs=new J.BodyCreationSettings(r.Get(),new J.RVec3(0,0,0),J.Quat.prototype.sIdentity(),J.EMotionType_Static,0);
    body=W.bi.CreateBody(bcs);J.destroy(bcs);J.destroy(ms);
    if(!body)return 0;
    W.body=body.GetID();
    W.bi.AddBody(W.body,J.EActivation_DontActivate);
    W.ps.OptimizeBroadPhase();
    return W.tris;
  }
  /* the elements as they are now: items [{key, sig}], pos(item) their triangles, asked only of new or changed ones;
     the ones gone are dropped; the body rebuilt when anything changed. Answers true when it was rebuilt. */
  function bimWalkPhysSync(W,items,pos){
    var seen={},i,it,b,k;
    for(i=0;i<items.length;i++){
      it=items[i];seen[it.key]=1;b=W.parts[it.key];
      if(!b||b.sig!==it.sig)bimWalkPhysMesh(W,it.key,it.sig,pos(it));
    }
    for(k in W.parts)if(W.parts.hasOwnProperty(k)&&!seen[k])bimWalkPhysDrop(W,k);
    if(!W.dirty)return false;
    bimWalkPhysBuild(W);
    return true;
  }
  /* the walker: a capsule (bimWalkCapsule's {half, r, step, slope}) standing with its feet at p */
  function bimWalkPhysChar(W,cap,p){
    var J=W.J,cs=new J.CharacterVirtualSettings(),inner=new J.CapsuleShapeSettings(cap.half,cap.r),
      off=new J.Vec3(0,cap.half+cap.r,0),up=new J.Vec3(0,1,0),rot,sr,pl,a;
    if(W.ch)bimWalkPhysCharFree(W);
    bimWalkPhysBuild(W);
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
  /* one frame: v = [vx, vy, vz] from bimWalkMove; mode 'walk' (gravity, a jump when asked and standing), 'fly' (no
     gravity, v as it is) or 'ghost' (through everything, the feet moved by v alone). Answers {p, ground}. */
  function bimWalkPhysStep(W,v,dt,mode,jump){
    var J=W.J,ch=W.ch,ground,p;
    if(!ch)return null;
    bimWalkPhysBuild(W);
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
    var J=W.J,o,d,ray,col,out=Infinity;
    bimWalkPhysBuild(W);
    o=new J.RVec3(from[0],from[1],from[2]);d=new J.Vec3(dir[0]*most,dir[1]*most,dir[2]*most);
    ray=new J.RRayCast(o,d);col=new J.CastRayClosestHitCollisionCollector();
    W.ps.GetNarrowPhaseQuery().CastRay(ray,W.rs,col,W.bpf,W.olf,W.bf,W.sf);
    if(col.HadHit())out=col.get_mHit().mFraction*most;
    J.destroy(col);J.destroy(ray);J.destroy(d);J.destroy(o);
    return out;
  }
  /* everything the world holds, and the world */
  function bimWalkPhysFree(W){
    var J=W.J;
    bimWalkPhysCharFree(W);
    if(W.body){W.bi.RemoveBody(W.body);W.bi.DestroyBody(W.body);W.body=null;}
    W.parts={};W.n=0;W.tris=0;
    [W.bpf,W.olf,W.bf,W.sf,W.vel,W.g,W.g0,W.at,W.rs].forEach(function(o){J.destroy(o);});
    J.destroy(W.ji);W.ji=W.ps=W.bi=null;
  }
