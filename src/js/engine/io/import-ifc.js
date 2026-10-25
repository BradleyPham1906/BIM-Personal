  // ---- IFC (STEP-text BIM format): subset covering IfcBuildingStorey + vertically-extruded IfcWall/IfcSlab ----
  function ifcSplitTop(s){
    var out=[],depth=0,cur='',inStr=false,i;
    for(i=0;i<s.length;i++){
      var c=s.charAt(i);
      if(inStr){
        cur+=c;
        if(c==="'"){if(s.charAt(i+1)==="'"){cur+=s.charAt(i+1);i++;}else inStr=false;}
        continue;
      }
      if(c==="'"){inStr=true;cur+=c;continue;}
      if(c==='('){depth++;cur+=c;continue;}
      if(c===')'){depth--;cur+=c;continue;}
      if(c===','&&depth===0){out.push(cur);cur='';continue;}
      cur+=c;
    }
    if(cur.trim().length)out.push(cur);
    return out.map(function(x){return x.trim();});
  }
  function ifcParseArg(raw){
    raw=raw.trim();
    if(raw==='$'||raw===''||raw==='*')return null;
    if(raw.charAt(0)==='#')return {ref:parseInt(raw.slice(1),10)};
    if(raw.charAt(0)==='.'&&raw.charAt(raw.length-1)==='.')return raw.slice(1,-1);
    if(raw.charAt(0)==="'")return raw.slice(1,-1).replace(/''/g,"'");
    if(raw.charAt(0)==='('){
      var parts=ifcSplitTop(raw.slice(1,-1));
      return parts.map(ifcParseArg);
    }
    var n=parseFloat(raw);
    if(isFinite(n)&&/^[\-+0-9.eE]+$/.test(raw))return n;
    return raw;
  }
  function ifcTokenize(text){
    var dataStart=text.indexOf('DATA;');
    var body=dataStart>=0?text.slice(dataStart+5):text;
    var re=/#(\d+)\s*=\s*([A-Z0-9_]+)\s*\(/g;
    var m,byId={};
    while((m=re.exec(body))){
      var id=parseInt(m[1],10),type=m[2],start=re.lastIndex;
      var depth=1,j=start,inStr=false;
      while(j<body.length&&depth>0){
        var c=body.charAt(j);
        if(inStr){
          if(c==="'"){if(body.charAt(j+1)==="'"){j+=2;continue;}inStr=false;}
          j++;continue;
        }
        if(c==="'"){inStr=true;j++;continue;}
        if(c==='(')depth++;
        else if(c===')')depth--;
        j++;
      }
      var argsRaw=body.slice(start,j-1);
      byId[id]={type:type,args:ifcSplitTop(argsRaw).map(ifcParseArg)};
      re.lastIndex=j;
    }
    return byId;
  }
  function ifcIdentity(){return {origin:[0,0,0],x:[1,0,0],y:[0,1,0],z:[0,0,1]};}
  function ifcVCross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
  function ifcVNorm(a){var l=Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])||1;return [a[0]/l,a[1]/l,a[2]/l];}
  function ifcRotateVec(T,v){return [
    v[0]*T.x[0]+v[1]*T.y[0]+v[2]*T.z[0],
    v[0]*T.x[1]+v[1]*T.y[1]+v[2]*T.z[1],
    v[0]*T.x[2]+v[1]*T.y[2]+v[2]*T.z[2]
  ];}
  function ifcApplyPoint(T,p){var r=ifcRotateVec(T,p);return [r[0]+T.origin[0],r[1]+T.origin[1],r[2]+T.origin[2]];}
  function ifcCompose(outer,inner){
    return {origin:ifcApplyPoint(outer,inner.origin),x:ifcRotateVec(outer,inner.x),y:ifcRotateVec(outer,inner.y),z:ifcRotateVec(outer,inner.z)};
  }
  function ifcMakeResolver(byId){
    function get(ref){return ref&&ref.ref!==undefined?byId[ref.ref]:null;}
    function resolvePoint3(ref){
      var e=get(ref);if(!e||e.type!=='IFCCARTESIANPOINT')return [0,0,0];
      var c=e.args[0]||[0,0,0];
      return [c[0]||0,c[1]||0,c[2]||0];
    }
    function resolveDir(ref){
      var e=get(ref);if(!e||e.type!=='IFCDIRECTION')return null;
      var c=(e.args[0]||[0,0,1]).slice();
      while(c.length<3)c.push(0);
      return ifcVNorm(c);
    }
    function resolveAxis2Placement3D(ref){
      var e=get(ref);
      if(!e||e.type!=='IFCAXIS2PLACEMENT3D')return ifcIdentity();
      var origin=resolvePoint3(e.args[0]);
      var zAxis=resolveDir(e.args[1])||[0,0,1];
      var xHint=resolveDir(e.args[2]);
      var xAxis;
      if(xHint){
        var d=xHint[0]*zAxis[0]+xHint[1]*zAxis[1]+xHint[2]*zAxis[2];
        xAxis=ifcVNorm([xHint[0]-zAxis[0]*d,xHint[1]-zAxis[1]*d,xHint[2]-zAxis[2]*d]);
      }else{
        xAxis=Math.abs(zAxis[2])<0.999?ifcVNorm(ifcVCross([0,0,1],zAxis)):[1,0,0];
      }
      return {origin:origin,x:xAxis,y:ifcVCross(zAxis,xAxis),z:zAxis};
    }
    function resolveAxis2Placement2D(ref){
      var e=get(ref);
      if(!e||e.type!=='IFCAXIS2PLACEMENT2D')return {origin:[0,0,0],x:[1,0,0],y:[0,1,0],z:[0,0,1]};
      var p2=get(e.args[0]);var loc=p2?(p2.args[0]||[0,0]):[0,0];
      var refDirE=get(e.args[1]);
      var rd=refDirE?(refDirE.args[0]||[1,0]):[1,0];
      var rl=Math.sqrt(rd[0]*rd[0]+rd[1]*rd[1])||1;
      var xa=[rd[0]/rl,rd[1]/rl,0],ya=[-xa[1],xa[0],0];
      return {origin:[loc[0]||0,loc[1]||0,0],x:xa,y:ya,z:[0,0,1]};
    }
    function worldPlacement(ref){
      var e=get(ref);
      if(!e||e.type!=='IFCLOCALPLACEMENT')return ifcIdentity();
      var rel=e.args[1]?resolveAxis2Placement3D(e.args[1]):ifcIdentity();
      if(e.args[0])return ifcCompose(worldPlacement(e.args[0]),rel);
      return rel;
    }
    function resolveProfile2D(ref){
      var e=get(ref);
      if(!e)return {pts:null,reason:'missing profile'};
      if(e.type==='IFCRECTANGLEPROFILEDEF'){
        var pos=e.args[2]?resolveAxis2Placement2D(e.args[2]):{origin:[0,0,0],x:[1,0,0],y:[0,1,0]};
        var xd=e.args[3]||0,yd=e.args[4]||0,hx=xd/2,hy=yd/2;
        var local=[[-hx,-hy],[hx,-hy],[hx,hy],[-hx,hy]];
        return {pts:local.map(function(p){return [pos.origin[0]+p[0]*pos.x[0]+p[1]*pos.y[0],pos.origin[1]+p[0]*pos.x[1]+p[1]*pos.y[1]];})};
      }
      if(e.type==='IFCARBITRARYCLOSEDPROFILEDEF'){
        var curve=get(e.args[2]);
        if(curve&&curve.type==='IFCPOLYLINE'){
          var ptsRef=curve.args[0]||[];
          return {pts:ptsRef.map(function(pr){var pe=get(pr);var c=pe?(pe.args[0]||[0,0]):[0,0];return [c[0]||0,c[1]||0];})};
        }
        return {pts:null,reason:'unsupported outer curve type ('+(curve?curve.type:'?')+')'};
      }
      return {pts:null,reason:'unsupported profile type ('+e.type+')'};
    }
    function resolveVerticalExtrusion(elemId){
      var e=byId[elemId];
      if(!e)return {ok:false,reason:'entity not found'};
      var placementRef=e.args[5],repRef=e.args[6];
      var world=placementRef?worldPlacement(placementRef):ifcIdentity();
      var pdShape=get(repRef);
      if(!pdShape||pdShape.type!=='IFCPRODUCTDEFINITIONSHAPE')return {ok:false,reason:'no product shape'};
      var reps=pdShape.args[2]||[];
      var bodyRep=null,i;
      for(i=0;i<reps.length;i++){
        var r=get(reps[i]);
        if(r&&r.type==='IFCSHAPEREPRESENTATION'&&(r.args[1]==='Body'||!bodyRep))bodyRep=r;
      }
      if(!bodyRep)return {ok:false,reason:'no Body representation'};
      var items=bodyRep.args[3]||[];
      for(i=0;i<items.length;i++){
        var it=get(items[i]);
        if(!it||it.type!=='IFCEXTRUDEDAREASOLID')continue;
        var profRes=resolveProfile2D(it.args[0]);
        if(!profRes.pts)return {ok:false,reason:profRes.reason||'unsupported profile'};
        var solidPos=it.args[1]?resolveAxis2Placement3D(it.args[1]):ifcIdentity();
        var depth=it.args[3]||0;
        var full=ifcCompose(world,solidPos);
        if(Math.abs(full.z[2])<0.999)return {ok:false,reason:'non-vertical extrusion (sloped/rotated element) not supported'};
        var baseZ=full.origin[2],topZ=baseZ+depth*full.z[2];
        var profXY=profRes.pts.map(function(p){return [full.origin[0]+p[0]*full.x[0]+p[1]*full.y[0],full.origin[1]+p[0]*full.x[1]+p[1]*full.y[1]];});
        return {ok:true,profileXY:profXY,baseZ:Math.min(baseZ,topZ),height:Math.abs(topZ-baseZ)};
      }
      return {ok:false,reason:'no IFCEXTRUDEDAREASOLID item in Body representation'};
    }
    return {worldPlacement:worldPlacement,resolveVerticalExtrusion:resolveVerticalExtrusion};
  }
  function ifcFindLengthScale(byId){
    var ids=Object.keys(byId),i;
    for(i=0;i<ids.length;i++){
      var e=byId[ids[i]];
      if(e.type!=='IFCPROJECT')continue;
      var ua=null,j;
      for(j=e.args.length-1;j>=0;j--){
        var cand=e.args[j];
        if(cand&&cand.ref!==undefined){var ce=byId[cand.ref];if(ce&&ce.type==='IFCUNITASSIGNMENT'){ua=ce;break;}}
      }
      if(!ua)continue;
      var units=ua.args[0]||[],k;
      for(k=0;k<units.length;k++){
        var uref=units[k];if(!uref||uref.ref===undefined)continue;
        var ue=byId[uref.ref];
        if(ue&&ue.type==='IFCSIUNIT'&&ue.args[1]==='LENGTHUNIT'){
          var prefix=ue.args[2];
          var scaleMap={MILLI:0.001,CENTI:0.01,DECI:0.1,DECA:10,HECTO:100,KILO:1000};
          return prefix&&scaleMap[prefix]!==undefined?scaleMap[prefix]:1;
        }
      }
    }
    return 1;
  }
  function bimImportIFC(text,filename){
    var byId;
    try{byId=ifcTokenize(text);}
    catch(eP){console.warn('[BIM] IFC parse failed:',eP);a3dToast('IFC import failed: could not parse '+filename);return;}
    var ids=Object.keys(byId);
    if(!ids.length){a3dToast('IFC import: no entities found in '+filename);return;}
    pushUndo();
    undoSuspend=true;
    var scale,levelsAdded=0,wallsAdded=0,slabsAdded=0,skipped=0,recoveredWalls=0,i;
    try{
      scale=ifcFindLengthScale(byId);
      var resolver=ifcMakeResolver(byId);
      var lyrWalls=addLayer('IFC Walls','#c7bfae'),lyrSlabs=addLayer('IFC Slabs','#9aa79a');
      for(i=0;i<ids.length;i++){
        var e=byId[ids[i]];
        if(e.type==='IFCBUILDINGSTOREY'){
          var nm=e.args[2]||('IFC Level '+(levelsAdded+1));
          var elev=e.args[9];
          if(typeof elev==='number'){
            A3D.levels.push({id:'lvl-'+Date.now().toString(36)+'-'+(A3D.seq++),name:nm+' (IFC)',elev:clampLevelElev(elev*scale),height:3});
            levelsAdded++;
          }
        }
      }
      for(i=0;i<ids.length;i++){
        var id2=parseInt(ids[i],10),e2=byId[id2];
        if(e2.type!=='IFCWALL'&&e2.type!=='IFCWALLSTANDARDCASE'&&e2.type!=='IFCSLAB')continue;
        var res=resolver.resolveVerticalExtrusion(id2);
        if(!res.ok){console.warn('[BIM] IFC element #'+id2+' ('+e2.type+') skipped: '+res.reason);skipped++;continue;}
        var profXZ=res.profileXY.map(function(p){return [p[0]*scale,p[1]*scale];});
        var mesh;
        try{mesh=padMesh(sketchCCW(profXZ),res.baseZ*scale,res.height*scale);}
        catch(eM){console.warn('[BIM] IFC solid build failed for #'+id2,eM);skipped++;continue;}
        if(!mesh||!mesh.f||mesh.f.length<4){skipped++;continue;}
        var isSlab=e2.type==='IFCSLAB';
        var cnt=isSlab?(A3D.counts.ifcslab=(A3D.counts.ifcslab||0)+1):(A3D.counts.ifcwall=(A3D.counts.ifcwall||0)+1);
        var bimData={type:isSlab?'floor':'wall',imported:true,ifcType:e2.type,name:e2.args[2]||null};
        if(!isSlab){
          var recovered=bimTryRecoverWallFromRectProfile(profXZ,res.baseZ*scale,res.height*scale);
          if(recovered){
            bimData.centerline=recovered.centerline;
            bimData.thickness=recovered.thickness;
            bimData.align=recovered.align;
            bimData.closed=recovered.closed;
            bimData.baseY=recovered.baseY;
            bimData.height=recovered.height;
            recoveredWalls++;
          }
        }
        var o={id:'a3d-'+Date.now().toString(36)+'-'+(A3D.seq++),t:'solid',
          name:(isSlab?'IFCSlab_':'IFCWall_')+cnt,col:isSlab?'#9aa79a':'#c7bfae',pos:[0,0,0],mesh:mesh,
          layer:(isSlab?lyrSlabs.id:lyrWalls.id),locked:true,
          bim:bimData};
        A3D.objs.push(o);
        if(isSlab)slabsAdded++;else wallsAdded++;
      }
    }finally{
      undoSuspend=false;
    }
    refreshTree();refreshLevels();refreshLayers();fitScene();paint();saveSoon();
    a3dToast('IFC import: '+levelsAdded+' level(s), '+wallsAdded+' wall(s) ('+recoveredWalls+' fully editable), '+slabsAdded+' slab(s), locked by default'+
      (skipped?'; '+skipped+' element(s) skipped (unsupported/non-vertical geometry)':''));
  }

