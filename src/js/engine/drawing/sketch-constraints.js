  // ---- __acad3dV45: Sketch geometric constraints -- an original 2D constraint solver (damped
  // Gauss-Newton / Levenberg-Marquardt over a numeric central-difference Jacobian, a standard
  // textbook numerical method) applied to the points of the currently-selected sketch. This is
  // written from scratch for this app; it is not derived from or a port of any other CAD kernel.
  // Constraint kinds and what each one asserts about the sketch's own point array (refs are
  // indices into o.pts, value is only used by 'distance'/'angle'/'fixed'):
  //   coincident(p0,p1)              the two points are the same point
  //   horizontal(p0,p1)               p0-p1 has zero Z difference (a horizontal line in plan)
  //   vertical(p0,p1)                 p0-p1 has zero X difference (a vertical line in plan)
  //   distance(p0,p1,d)               |p0-p1| == d
  //   equal(p0,p1,p2,p3)              |p0-p1| == |p2-p3|
  //   parallel(p0,p1,p2,p3)           segment p0-p1 is parallel to segment p2-p3
  //   perpendicular(p0,p1,p2,p3)      segment p0-p1 is perpendicular to segment p2-p3
  //   angle(p0,p1,p2,p3,theta)        the angle between the two segments is theta (radians)
  // A 'fixed' kind also exists internally (pins one point to an exact X/Z) but is only ever added
  // transiently during a grip drag -- it drives the solve while the user's cursor is the source of
  // truth for that one point, and is never itself persisted as a stored constraint.
  function bimConResidual(kind,pts,refs,value){
    function P(i){return pts[i];}
    switch(kind){
      case 'coincident':{
        var a=P(refs[0]),b=P(refs[1]);
        return [a[0]-b[0],a[1]-b[1]];
      }
      case 'horizontal':{
        var a2=P(refs[0]),b2=P(refs[1]);
        return [a2[1]-b2[1]];
      }
      case 'vertical':{
        var a3=P(refs[0]),b3=P(refs[1]);
        return [a3[0]-b3[0]];
      }
      case 'distance':{
        var a4=P(refs[0]),b4=P(refs[1]);
        var d=Math.sqrt((a4[0]-b4[0])*(a4[0]-b4[0])+(a4[1]-b4[1])*(a4[1]-b4[1]));
        return [d-value];
      }
      case 'equal':{
        var a5=P(refs[0]),b5=P(refs[1]),c5=P(refs[2]),d5=P(refs[3]);
        var l1=Math.sqrt((a5[0]-b5[0])*(a5[0]-b5[0])+(a5[1]-b5[1])*(a5[1]-b5[1]));
        var l2=Math.sqrt((c5[0]-d5[0])*(c5[0]-d5[0])+(c5[1]-d5[1])*(c5[1]-d5[1]));
        return [l1-l2];
      }
      case 'parallel':{
        var a6=P(refs[0]),b6=P(refs[1]),c6=P(refs[2]),d6=P(refs[3]);
        var ux=b6[0]-a6[0],uz=b6[1]-a6[1],vx=d6[0]-c6[0],vz=d6[1]-c6[1];
        return [ux*vz-uz*vx];
      }
      case 'perpendicular':{
        var a7=P(refs[0]),b7=P(refs[1]),c7=P(refs[2]),d7=P(refs[3]);
        var ux2=b7[0]-a7[0],uz2=b7[1]-a7[1],vx2=d7[0]-c7[0],vz2=d7[1]-c7[1];
        return [ux2*vx2+uz2*vz2];
      }
      case 'angle':{
        var a8=P(refs[0]),b8=P(refs[1]),c8=P(refs[2]),d8=P(refs[3]);
        var ux3=b8[0]-a8[0],uz3=b8[1]-a8[1],vx3=d8[0]-c8[0],vz3=d8[1]-c8[1];
        var ang=Math.atan2(ux3*vz3-uz3*vx3,ux3*vx3+uz3*vz3);
        var diff=ang-value;
        while(diff>Math.PI)diff-=2*Math.PI;
        while(diff<-Math.PI)diff+=2*Math.PI;
        return [diff];
      }
      case 'fixed':{
        var a9=P(refs[0]);
        return [a9[0]-value[0],a9[1]-value[1]];
      }
      // ---- Ported (as residual formulas, not code) from FreeCAD's planegcs solver
      // (src/Mod/Sketcher/App/planegcs/Constraints.cpp) after a from-scratch survey of the real
      // FreeCAD source confirmed these specific formulas are small, self-contained, OCCT-free
      // pure math -- see canvas_v10_STATUS.md's "Real FreeCAD source audit via GitHub" section.
      // Adapted to this app's point-index/residual-vector convention (planegcs uses raw pointers
      // into a shared parameter array and a signed "scale" factor per constraint; here every
      // constraint is just an unscaled residual fed to the shared Gauss-Newton solver above).
      case 'pointonline':{
        // Point P constrained onto the line through A,B. Signed-area-over-length distance
        // formula (planegcs ConstraintPointOnLine::error), so the residual is a real physical
        // distance (meters) rather than an arbitrary unnormalized cross-product magnitude.
        var pP=P(refs[0]),pA=P(refs[1]),pB=P(refs[2]);
        var dx10=pB[0]-pA[0],dz10=pB[1]-pA[1];
        var len10=Math.sqrt(dx10*dx10+dz10*dz10)||1e-9;
        var area10=-pP[0]*dz10+pP[1]*dx10+pA[0]*pB[1]-pB[0]*pA[1];
        return [area10/len10];
      }
      case 'midpoint':{
        // Point M constrained to be the midpoint of A,B (planegcs MidpointOnLine, specialized to
        // our point-only sketch model rather than a generic point/line pair).
        var pM=P(refs[0]),pA2=P(refs[1]),pB2=P(refs[2]);
        return [pM[0]-(pA2[0]+pB2[0])/2,pM[1]-(pA2[1]+pB2[1])/2];
      }
      case 'symmetric_pt':{
        // P and Q symmetric about point C, i.e. C is the midpoint of P,Q.
        var pP2=P(refs[0]),pQ2=P(refs[1]),pC2=P(refs[2]);
        return [pP2[0]+pQ2[0]-2*pC2[0],pP2[1]+pQ2[1]-2*pC2[1]];
      }
      case 'symmetric_line':{
        // P and Q symmetric about line A,B: their midpoint lies on the line, and segment PQ is
        // perpendicular to it. Two independent residuals, same shape as planegcs's own
        // point-symmetric-about-line handling (a PointOnLine + a perpendicularity check).
        var pP3=P(refs[0]),pQ3=P(refs[1]),pA3=P(refs[2]),pB3=P(refs[3]);
        var mx3=(pP3[0]+pQ3[0])/2,mz3=(pP3[1]+pQ3[1])/2;
        var dx3=pB3[0]-pA3[0],dz3=pB3[1]-pA3[1];
        var len3=Math.sqrt(dx3*dx3+dz3*dz3)||1e-9;
        var area3=-mx3*dz3+mz3*dx3+pA3[0]*pB3[1]-pB3[0]*pA3[1];
        var onLine3=area3/len3;
        var perp3=(pQ3[0]-pP3[0])*dx3+(pQ3[1]-pP3[1])*dz3;
        return [onLine3,perp3];
      }
      default:
        return [];
    }
  }
  function bimConResidualCount(kind){
    if(kind==='coincident'||kind==='fixed'||kind==='midpoint'||kind==='symmetric_pt'||kind==='symmetric_line')return 2;
    return 1;
  }
  function bimConDot(a,b){var s=0,i;for(i=0;i<a.length;i++)s+=a[i]*b[i];return s;}
  function bimConMatATA(J,rows,cols){
    var out=[],i,j,k;
    for(i=0;i<cols;i++)out.push(new Array(cols).fill(0));
    for(k=0;k<rows;k++){
      for(i=0;i<cols;i++){
        var jik=J[k][i];
        if(jik===0)continue;
        for(j=0;j<cols;j++)out[i][j]+=jik*J[k][j];
      }
    }
    return out;
  }
  function bimConMatVecAT(J,r,rows,cols){
    var out=new Array(cols).fill(0),i,k;
    for(k=0;k<rows;k++){
      var rk=r[k];
      if(rk===0)continue;
      for(i=0;i<cols;i++)out[i]+=J[k][i]*rk;
    }
    return out;
  }
  // Gaussian elimination with partial pivoting; returns null (not a throw) on a singular system so
  // the damping-retry loop can back off lambda instead of crashing on an ill-conditioned step.
  function bimConSolveLinear(A,b){
    var n=b.length,i2;
    var M=A.map(function(row,i){return row.concat([b[i]]);});
    var col,r2,c2;
    for(col=0;col<n;col++){
      var piv=col,best=Math.abs(M[col][col]);
      for(r2=col+1;r2<n;r2++){if(Math.abs(M[r2][col])>best){best=Math.abs(M[r2][col]);piv=r2;}}
      if(best<1e-14)return null;
      if(piv!==col){var tmp=M[col];M[col]=M[piv];M[piv]=tmp;}
      var pv=M[col][col];
      for(c2=col;c2<=n;c2++)M[col][c2]/=pv;
      for(r2=0;r2<n;r2++){
        if(r2===col)continue;
        var f=M[r2][col];
        if(f===0)continue;
        for(c2=col;c2<=n;c2++)M[r2][c2]-=f*M[col][c2];
      }
    }
    var x=new Array(n);
    for(i2=0;i2<n;i2++)x[i2]=M[i2][n];
    return x;
  }
  // Flattens sketch points into a variable vector and runs damped Gauss-Newton until convergence
  // or a fail-safe iteration cap. Never returns a half-solved, silently-wrong result: it always
  // reports the final residual norm so the caller can decide whether the solve actually succeeded.
  function bimSolveSketchConstraints(ptsIn,constraints,opts){
    opts=opts||{};
    var maxIter=opts.maxIter||60,tol=opts.tol||1e-9,lambda0=opts.lambda||1e-3;
    var n=ptsIn.length,x=[],i;
    for(i=0;i<n;i++){x.push(ptsIn[i][0]);x.push(ptsIn[i][1]);}
    function unpack(xv){
      var pts=[],j;
      for(j=0;j<n;j++)pts.push([xv[j*2],xv[j*2+1]]);
      return pts;
    }
    function evalResiduals(xv){
      var pts=unpack(xv),r=[],c,k;
      for(c=0;c<constraints.length;c++){
        var cons=constraints[c];
        var rc=bimConResidual(cons.type,pts,cons.refs,cons.value);
        for(k=0;k<rc.length;k++)r.push(rc[k]);
      }
      return r;
    }
    var mSize=0;
    for(i=0;i<constraints.length;i++)mSize+=bimConResidualCount(constraints[i].type);
    if(mSize===0)return {pts:ptsIn.map(function(p){return p.slice();}),iterations:0,residualNorm:0};
    var lambda=lambda0,r=evalResiduals(x),normSq=bimConDot(r,r),iter;
    for(iter=0;iter<maxIter;iter++){
      if(normSq<tol)break;
      var h=1e-6,J=[],rr,v;
      for(rr=0;rr<mSize;rr++)J.push(new Array(2*n).fill(0));
      for(v=0;v<2*n;v++){
        var xp=x.slice();xp[v]+=h;
        var xm=x.slice();xm[v]-=h;
        var rp=evalResiduals(xp),rm=evalResiduals(xm);
        for(rr=0;rr<mSize;rr++)J[rr][v]=(rp[rr]-rm[rr])/(2*h);
      }
      var JT_J=bimConMatATA(J,mSize,2*n),JT_r=bimConMatVecAT(J,r,mSize,2*n);
      var tries=0,improved=false;
      while(tries<12&&!improved){
        var A=JT_J.map(function(row,ri){return row.map(function(val,ci){return val+(ri===ci?lambda*(val||1):0);});});
        var negJTr=JT_r.map(function(v2){return -v2;});
        var dx=bimConSolveLinear(A,negJTr);
        if(!dx){lambda*=4;tries++;continue;}
        var xNew=x.map(function(v3,idx){return v3+dx[idx];});
        var rNew=evalResiduals(xNew),normSqNew=bimConDot(rNew,rNew);
        if(normSqNew<normSq){
          x=xNew;r=rNew;normSq=normSqNew;
          lambda=Math.max(lambda/3,1e-12);
          improved=true;
        }else{lambda*=4;tries++;}
      }
      if(!improved)break;
    }
    if(!isFinite(normSq))return {error:'Solver diverged (non-finite residual)'};
    return {pts:unpack(x),iterations:iter,residualNorm:Math.sqrt(normSq)};
  }
  // Crude DOF estimate: 2 unknowns per point minus the number of independent-looking equation
  // rows. Not a rigorous rank analysis (that would need a real SVD) -- clearly an approximation,
  // like the "N constraints remaining" indicator most sketchers show.
  function bimEstimateSketchDOF(ptsCount,constraints){
    var eqCount=0,i;
    for(i=0;i<constraints.length;i++)eqCount+=bimConResidualCount(constraints[i].type);
    return Math.max(0,ptsCount*2-eqCount);
  }
  var A3D_CON_LABELS={coincident:'Coincident',horizontal:'Horizontal',vertical:'Vertical',distance:'Distance',equal:'Equal Length',parallel:'Parallel',perpendicular:'Perpendicular',angle:'Angle',pointonline:'Point on Line',midpoint:'Midpoint',symmetric_pt:'Symmetric (about point)',symmetric_line:'Symmetric (about line)'};
  var A3D_CON_NEED={coincident:2,horizontal:2,vertical:2,distance:2,equal:4,parallel:4,perpendicular:4,angle:4,pointonline:3,midpoint:3,symmetric_pt:3,symmetric_line:4};
  function bimSketchConstraintLabel(type){return A3D_CON_LABELS[type]||type;}
  function bimSketchConstraintDesc(o,c){
    var lbl=bimSketchConstraintLabel(c.type);
    var names=c.refs.map(function(idx){return 'P'+(idx+1);});
    if(c.type==='distance')return lbl+' ('+names[0]+'-'+names[1]+' = '+c.value.toFixed(3)+'m)';
    if(c.type==='angle')return lbl+' ('+names[0]+names[1]+'/'+names[2]+names[3]+' = '+(c.value*180/Math.PI).toFixed(2)+'°)';
    if(c.type==='pointonline')return lbl+' ('+names[0]+' on '+names[1]+'-'+names[2]+')';
    if(c.type==='midpoint')return lbl+' ('+names[0]+' = mid of '+names[1]+'-'+names[2]+')';
    if(c.type==='symmetric_pt')return lbl+' ('+names[0]+'-'+names[1]+' about '+names[2]+')';
    if(c.type==='symmetric_line')return lbl+' ('+names[0]+'-'+names[1]+' about '+names[2]+'-'+names[3]+')';
    if(c.refs.length===4)return lbl+' ('+names[0]+names[1]+' / '+names[2]+names[3]+')';
    return lbl+' ('+names[0]+'-'+names[1]+')';
  }
  // Re-solves a sketch's points against its stored constraints. When pinIdx is given (a grip
  // actively being dragged), a transient 'fixed' constraint anchors that one point at its current
  // (mouse-driven) location for this solve only -- it is never written into o.constraints. Applies
  // the solved points back to o.pts only when the solve actually converged; on an unsatisfiable or
  // non-finite result it leaves o.pts untouched and fails gracefully with a console warning and
  // (unless silent) a user-visible toast, per the "never a silently-wrong result" requirement.
  function bimResolveSketch(o,pinIdx,opts){
    opts=opts||{};
    if(!o||o.t!=='sketch'||!o.pts||!o.constraints||!o.constraints.length)return {ok:true,solved:false};
    var cons=o.constraints.slice();
    if(pinIdx!==undefined&&pinIdx!==null&&pinIdx>=0&&pinIdx<o.pts.length){
      cons.push({type:'fixed',refs:[pinIdx],value:[o.pts[pinIdx][0],o.pts[pinIdx][1]]});
    }
    var res=bimSolveSketchConstraints(o.pts,cons);
    if(res.error){
      console.warn('[BIM] Sketch constraint solve failed on "'+o.name+'": '+res.error);
      if(!opts.silent)a3dToast('Constraint solve failed: '+res.error);
      return {ok:false};
    }
    if(res.residualNorm>1e-3){
      console.warn('[BIM] Sketch "'+o.name+'" constraints could not be fully satisfied (residual '+res.residualNorm.toFixed(5)+') -- likely conflicting or over-constrained; leaving geometry unchanged.');
      if(!opts.silent)a3dToast('Constraints could not be fully satisfied (conflicting or over-constrained)');
      return {ok:false,residualNorm:res.residualNorm};
    }
    var i;
    for(i=0;i<o.pts.length;i++)o.pts[i]=[res.pts[i][0],res.pts[i][1]];
    return {ok:true,solved:true,residualNorm:res.residualNorm};
  }
  function bimAddSketchConstraint(o,type,refs,value){
    if(!o||o.t!=='sketch')return null;
    if(bimIsLocked(o)){a3dToast(o.name+' is pinned — unlock it to add constraints');return null;}
    var need=A3D_CON_NEED[type];
    if(!need||!refs||refs.length!==need){console.warn('[BIM] Rejected malformed constraint request (type='+type+', refs='+JSON.stringify(refs)+').');return null;}
    var i;
    for(i=0;i<refs.length;i++)if(refs[i]<0||refs[i]>=o.pts.length){a3dToast('Constraint point out of range');return null;}
    pushUndo();
    if(!o.constraints)o.constraints=[];
    var c={id:'con-'+Date.now().toString(36)+'-'+(A3D.seq++),type:type,refs:refs.slice(),value:value};
    o.constraints.push(c);
    var res=bimResolveSketch(o,null);
    if(!res.ok){
      o.constraints.pop();
      return null;
    }
    bimAfterSketchEdit(o);
    refreshTree();paint();saveSoon();
    a3dToast(bimSketchConstraintLabel(type)+' constraint added');
    return c;
  }
  function bimDeleteSketchConstraint(o,conId){
    if(!o||!o.constraints)return;
    var idx=-1,i;
    for(i=0;i<o.constraints.length;i++)if(o.constraints[i].id===conId){idx=i;break;}
    if(idx<0)return;
    pushUndo();
    o.constraints.splice(idx,1);
    bimResolveSketch(o,null,{silent:true});
    bimAfterSketchEdit(o);
    refreshTree();paint();saveSoon();
  }
  function startConstraintTool(type){
    var o=selSketch();
    if(!o){a3dToast('Select a sketch first, then pick a constraint tool');return;}
    if(bimIsLocked(o)){a3dToast(o.name+' is pinned — unlock it to add constraints');return;}
    if(o.pts.length<2){a3dToast(o.name+' needs at least 2 points to constrain');return;}
    closeDlg();
    bimEnterDraftingMode();
    A3D.conPick={type:type,need:A3D_CON_NEED[type],picked:[]};
    a3dToast(bimSketchConstraintLabel(type)+': click point 1 of '+A3D_CON_NEED[type]+' on '+o.name+' (Escape to cancel)');
    paint();
  }
  function cancelConstraintPick(){A3D.conPick=null;paint();}
  function bimFinishConstraintPick(){
    var cp=A3D.conPick,o=selSketch();
    A3D.conPick=null;
    if(!o||!cp)return;
    if(cp.type==='distance'||cp.type==='angle'){openConstraintValueDlg(cp.type,o,cp.picked.slice());return;}
    bimAddSketchConstraint(o,cp.type,cp.picked.slice());
  }
  function openConstraintValueDlg(kind,o,refs){
    closeDlg();
    var isAngle=(kind==='angle');
    var d=document.createElement('div');
    d.className='a3d-dlg';
    d.innerHTML='<div class="a3d-dlghd">'+(isAngle?'Angle Constraint':'Distance Constraint')+'</div><div class="a3d-dlgbody">'+
      '<div class="a3d-dlgrow"><label>'+(isAngle?'Angle (degrees)':'Distance (m)')+'</label><input type="number" step="any" data-a3dp="v" value="'+(isAngle?'45':'1')+'"></div>'+
      '<div id="a3d-dlgerr" class="a3d-dlgerr"></div></div>'+
      '<div class="a3d-dlgft"><button data-a3dlg="cancel">Cancel</button><button data-a3dlg="ok">OK</button></div>';
    el.root.appendChild(d);el.dlg=d;
    var vI=d.querySelector('[data-a3dp="v"]');
    function submit(){
      var v=parseFloat(vI.value);
      var eb=document.getElementById('a3d-dlgerr');
      if(!isFinite(v)){eb.textContent='Must be a number';return;}
      if(!isAngle&&v<=0){eb.textContent='Distance must be a positive number';return;}
      closeDlg();
      bimAddSketchConstraint(o,kind,refs,isAngle?(v*Math.PI/180):v);
    }
    d.addEventListener('click',function(ev){var b=ev.target&&ev.target.closest?ev.target.closest('[data-a3dlg]'):null;if(!b)return;if(b.getAttribute('data-a3dlg')==='ok')submit();else closeDlg();});
    d.addEventListener('keydown',function(ev){if(ev.key==='Enter'){ev.preventDefault();ev.stopPropagation();submit();}else if(ev.key==='Escape'){ev.preventDefault();ev.stopPropagation();closeDlg();}});
    vI.focus();vI.select();
  }
  function pick(x,y){
    var i;
    /* __acad3dV82: the annotation overlay is drawn ON TOP of the model, so it is picked first.
       Testing it after the solids would let a wall underneath swallow a click aimed at a note
       sitting over it. */
    var nt=bimPickNote(x,y);
    if(nt)return nt;
    var dgp=bimPickDiag(x,y);   /* __acad3dV164: the site analysis, drawn over the model */
    if(dgp)return dgp;
    /* __acad3dV98: then the dimensions and text, which are drawn above the model too. Testing
       them last let a room swallow a click on the label sitting inside it. */
    var an=bimPickAnnotation(x,y);
    if(an)return an;
    if(bimPickGpuWanted()){   /* __acad3dV156: a large model: the GPU says what is under the pointer */
      var gp=bimPickGpu(x,y);
      A3D.lastPickPath='gpu';
      if(gp.ok&&gp.o&&bimLayerPickable(gp.o))return gp.o;
      if(gp.ok&&!gp.o)return bimPickSketch(x,y);
    }
    A3D.lastPickPath='cpu';
    if(A3D_GL||A3D_GPU.engine==='webgpu')bimBuildPickPolys();
    for(i=A3D.lastPolys.length-1;i>=0;i--){
      if(A3D.lastPolys[i].lock)continue;
      if(inPoly(x,y,A3D.lastPolys[i].pts))return A3D.lastPolys[i].o;
    }
    return bimPickSketch(x,y);
  }
