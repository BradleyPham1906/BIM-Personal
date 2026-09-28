// ==== IFC subset parser/importer prototype ====
// Supports: IFCBUILDINGSTOREY (-> Level), IFCWALL/IFCWALLSTANDARDCASE/IFCSLAB with a Body
// IFCSHAPEREPRESENTATION containing an IFCEXTRUDEDAREASOLID over IFCRECTANGLEPROFILEDEF or
// IFCARBITRARYCLOSEDPROFILEDEF(IFCPOLYLINE), extruded VERTICALLY (the overwhelmingly common
// case for architectural walls/slabs). Non-vertical extrusions, boolean-clipped solids, and
// advanced/faceted B-reps are explicitly reported as skipped, not silently mis-imported.

function ifcSplitTop(s){
  // Split a raw STEP argument-list string on top-level commas, respecting nested () and '...' strings.
  var out=[],depth=0,cur='',inStr=false,i;
  for(i=0;i<s.length;i++){
    var c=s[i];
    if(inStr){
      cur+=c;
      if(c==="'"){
        if(s[i+1]==="'"){cur+=s[i+1];i++;} else inStr=false;
      }
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
  if(raw==='$'||raw==='')return null;
  if(raw==='*')return null;
  if(raw.charAt(0)==='#')return {ref:parseInt(raw.slice(1),10)};
  if(raw.charAt(0)==='.'&&raw.charAt(raw.length-1)==='.')return raw.slice(1,-1);
  if(raw.charAt(0)==="'"){return raw.slice(1,-1).replace(/''/g,"'");}
  if(raw.charAt(0)==='('){
    var inner=raw.slice(1,-1);
    var parts=ifcSplitTop(inner);
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
      var c=body[j];
      if(inStr){
        if(c==="'"){ if(body[j+1]==="'"){j+=2;continue;} inStr=false; }
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

// ---- linear algebra: transforms are {origin:[x,y,z], x:[..],y:[..],z:[..]} orthonormal bases ----
function ifcIdentity(){return {origin:[0,0,0],x:[1,0,0],y:[0,1,0],z:[0,0,1]};}
function ifcVSub(a,b){return [a[0]-b[0],a[1]-b[1],a[2]-b[2]];}
function ifcVCross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function ifcVNorm(a){var l=Math.sqrt(a[0]*a[0]+a[1]*a[1]+a[2]*a[2])||1;return [a[0]/l,a[1]/l,a[2]/l];}
function ifcRotateVec(T,v){return [
  v[0]*T.x[0]+v[1]*T.y[0]+v[2]*T.z[0],
  v[0]*T.x[1]+v[1]*T.y[1]+v[2]*T.z[1],
  v[0]*T.x[2]+v[1]*T.y[2]+v[2]*T.z[2]
];}
function ifcApplyPoint(T,p){var r=ifcRotateVec(T,p);return [r[0]+T.origin[0],r[1]+T.origin[1],r[2]+T.origin[2]];}
function ifcCompose(outer,inner){
  return {
    origin: ifcApplyPoint(outer,inner.origin),
    x: ifcRotateVec(outer,inner.x),
    y: ifcRotateVec(outer,inner.y),
    z: ifcRotateVec(outer,inner.z)
  };
}

function ifcMakeResolver(byId){
  function get(ref){ return ref&&ref.ref!==undefined ? byId[ref.ref] : null; }

  function resolvePoint3(ref){
    var e=get(ref); if(!e||e.type!=='IFCCARTESIANPOINT')return [0,0,0];
    var c=e.args[0]||[0,0,0];
    return [c[0]||0,c[1]||0,c[2]||0];
  }
  function resolveDir(ref){
    var e=get(ref); if(!e||e.type!=='IFCDIRECTION')return null;
    var c=e.args[0]||[0,0,1];
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
    var yAxis=ifcVCross(zAxis,xAxis);
    return {origin:origin,x:xAxis,y:yAxis,z:zAxis};
  }
  function resolveAxis2Placement2D(ref){
    var e=get(ref);
    if(!e||e.type!=='IFCAXIS2PLACEMENT2D')return {origin:[0,0,0],x:[1,0,0],y:[0,1,0],z:[0,0,1]};
    var p2=get(e.args[0]); var loc=p2?(p2.args[0]||[0,0]):[0,0];
    var refDirE=get(e.args[1]);
    var rd=refDirE?(refDirE.args[0]||[1,0]):[1,0];
    var rl=Math.sqrt(rd[0]*rd[0]+rd[1]*rd[1])||1;
    var xa=[rd[0]/rl,rd[1]/rl,0], ya=[-xa[1],xa[0],0];
    return {origin:[loc[0]||0,loc[1]||0,0],x:xa,y:ya,z:[0,0,1]};
  }
  function worldPlacement(ref){
    var e=get(ref);
    if(!e||e.type!=='IFCLOCALPLACEMENT')return ifcIdentity();
    var rel=e.args[1]?resolveAxis2Placement3D(e.args[1]):ifcIdentity();
    if(e.args[0]){
      var parent=worldPlacement(e.args[0]);
      return ifcCompose(parent,rel);
    }
    return rel;
  }

  function resolveProfile2D(ref){
    var e=get(ref);
    if(!e)return {pts:null,reason:'missing profile'};
    if(e.type==='IFCRECTANGLEPROFILEDEF'){
      var pos=e.args[2]?resolveAxis2Placement2D(e.args[2]):{origin:[0,0,0],x:[1,0,0],y:[0,1,0]};
      var xd=e.args[3]||0,yd=e.args[4]||0,hx=xd/2,hy=yd/2;
      var local=[[-hx,-hy],[hx,-hy],[hx,hy],[-hx,hy]];
      var pts=local.map(function(p){
        return [pos.origin[0]+p[0]*pos.x[0]+p[1]*pos.y[0], pos.origin[1]+p[0]*pos.x[1]+p[1]*pos.y[1]];
      });
      return {pts:pts};
    }
    if(e.type==='IFCARBITRARYCLOSEDPROFILEDEF'){
      var curve=get(e.args[2]);
      if(curve&&curve.type==='IFCPOLYLINE'){
        var ptsRef=curve.args[0]||[];
        var pts2=ptsRef.map(function(pr){var pe=get(pr);var c=pe?(pe.args[0]||[0,0]):[0,0];return [c[0]||0,c[1]||0];});
        return {pts:pts2};
      }
      return {pts:null,reason:'unsupported outer curve type ('+(curve?curve.type:'?')+')'};
    }
    return {pts:null,reason:'unsupported profile type ('+e.type+')'};
  }

  // Resolve a wall/slab/column-like element's Body SweptSolid to a world-space vertical prism, if possible.
  function resolveVerticalExtrusion(elemId){
    var e=byId[elemId];
    if(!e)return {ok:false,reason:'entity not found'};
    var placementRef=e.args[5], repRef=e.args[6];
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
      if(!it)continue;
      if(it.type!=='IFCEXTRUDEDAREASOLID'){ continue; }
      var profRes=resolveProfile2D(it.args[0]);
      if(!profRes.pts)return {ok:false,reason:profRes.reason||'unsupported profile'};
      var solidPos=it.args[1]?resolveAxis2Placement3D(it.args[1]):ifcIdentity();
      var depth=it.args[3]||0;
      var full=ifcCompose(world,solidPos);
      if(Math.abs(full.z[2])<0.999)return {ok:false,reason:'non-vertical extrusion (sloped/rotated wall) not supported'};
      var baseZ=full.origin[2];
      var topZ=baseZ+depth*full.z[2];
      var height=Math.abs(topZ-baseZ);
      var profXY=profRes.pts.map(function(p){
        return [full.origin[0]+p[0]*full.x[0]+p[1]*full.y[0], full.origin[1]+p[0]*full.x[1]+p[1]*full.y[1]];
      });
      return {ok:true, profileXY:profXY, baseZ:Math.min(baseZ,topZ), height:height};
    }
    return {ok:false,reason:'no IFCEXTRUDEDAREASOLID item in Body representation'};
  }

  return {worldPlacement:worldPlacement, resolveVerticalExtrusion:resolveVerticalExtrusion, resolveProfile2D:resolveProfile2D};
}

// ==== TEST: minimal but structurally realistic IFC SPF sample ====
// Storey at elevation 3000mm; a wall on that storey, offset placement, rectangle profile 4000x200, extruded 2700mm.
var ifcSample = [
"ISO-10303-21;",
"HEADER;",
"ENDSEC;",
"DATA;",
"#1=IFCCARTESIANPOINT((0.,0.,0.));",
"#2=IFCDIRECTION((0.,0.,1.));",
"#3=IFCDIRECTION((1.,0.,0.));",
"#4=IFCAXIS2PLACEMENT3D(#1,#2,#3);",
"#5=IFCLOCALPLACEMENT($,#4);",
"#6=IFCBUILDINGSTOREY('2xGuidStorey',$,'Level 1',$,$,#5,$,'Level 1',.ELEMENT.,3000.);",
"#10=IFCCARTESIANPOINT((1000.,500.,0.));",
"#11=IFCDIRECTION((0.,0.,1.));",
"#12=IFCDIRECTION((1.,0.,0.));",
"#13=IFCAXIS2PLACEMENT3D(#10,#11,#12);",
"#14=IFCLOCALPLACEMENT(#5,#13);",
"#20=IFCAXIS2PLACEMENT2D(#1,#3);",
"#21=IFCRECTANGLEPROFILEDEF(.AREA.,$,#20,4000.,200.);",
"#22=IFCAXIS2PLACEMENT3D($,$,$);",
"#23=IFCDIRECTION((0.,0.,1.));",
"#24=IFCEXTRUDEDAREASOLID(#21,#22,#23,2700.);",
"#25=IFCSHAPEREPRESENTATION($,'Body','SweptSolid',(#24));",
"#26=IFCPRODUCTDEFINITIONSHAPE($,$,(#25));",
"#30=IFCWALLSTANDARDCASE('2xGuidWall',$,'Wall 1',$,$,#14,#26,$,$);",
"ENDSEC;",
"END-ISO-10303-21;"
].join('\n');

var byId=ifcTokenize(ifcSample);
console.log('Entities parsed:', Object.keys(byId).length);
var resolver=ifcMakeResolver(byId);

var PASS=0,FAIL=0;
function assert(name,cond,detail){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name+(detail?'  -- '+detail:''));}}

assert('tokenizer finds all 19 entity instances', Object.keys(byId).length===19);
assert('IFCBUILDINGSTOREY parsed with correct type', byId[6].type==='IFCBUILDINGSTOREY');
assert('IFCBUILDINGSTOREY.Name is at arg index 2 ("Level 1")', byId[6].args[2]==='Level 1');
assert('IFCBUILDINGSTOREY.Elevation is at arg index 9 (3000)', byId[6].args[9]===3000);

var res=resolver.resolveVerticalExtrusion(30);
console.log('Wall resolution result:', JSON.stringify(res));
assert('wall extrusion resolves ok (vertical, supported profile)', res.ok===true, res.reason);
if(res.ok){
  assert('wall base elevation = storey placement (0) -- solid Position is null/identity so local extrude starts at world origin z', Math.abs(res.baseZ-0)<1e-6, 'baseZ='+res.baseZ);
  assert('wall height = extrusion depth (2700)', Math.abs(res.height-2700)<1e-6, 'height='+res.height);
  assert('wall profile has 4 points (rectangle)', res.profileXY.length===4);
  // Wall local placement origin (1000,500) + profile centered rectangle 4000x200 -> world X spans [1000-2000,1000+2000]=[-1000,3000]
  var xs=res.profileXY.map(function(p){return p[0];});
  assert('profile world X extents match placement offset + rectangle half-width', Math.min.apply(null,xs)===-1000 && Math.max.apply(null,xs)===3000, 'xs='+JSON.stringify(xs));
}

// Negative test: a sloped (non-vertical) extrusion must be reported as unsupported, not silently mis-imported
var slopedSample = ifcSample
  .replace("#23=IFCDIRECTION((0.,0.,1.));", "#23=IFCDIRECTION((0.,0.,1.));")
  .replace("#22=IFCAXIS2PLACEMENT3D($,$,$);", "#22=IFCAXIS2PLACEMENT3D($,#40,$);")
  + "\n#40=IFCDIRECTION((1.,0.,1.));";
var byId2=ifcTokenize(slopedSample);
var resolver2=ifcMakeResolver(byId2);
var res2=resolver2.resolveVerticalExtrusion(30);
assert('sloped extrusion is correctly rejected as unsupported (not silently imported)', res2.ok===false && /non-vertical/.test(res2.reason), JSON.stringify(res2));

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');

// ---- ifcFindLengthScale: robustly find IFCPROJECT -> IFCUNITASSIGNMENT -> LENGTHUNIT scale ----
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
      var uref=units[k]; if(!uref||uref.ref===undefined)continue;
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
var unitsSample = ifcSample.replace("ENDSEC;\nEND-ISO-10303-21;",
  "#100=IFCSIUNIT(*,.LENGTHUNIT.,.MILLI.,.METRE.);\n"+
  "#101=IFCUNITASSIGNMENT((#100));\n"+
  "#102=IFCPROJECT('2xGuidProj',$,'Proj',$,$,$,$,$,#101);\n"+
  "ENDSEC;\nEND-ISO-10303-21;");
var byId3=ifcTokenize(unitsSample);
var scale3=ifcFindLengthScale(byId3);
var PASS3=(scale3===0.001)?1:0;
console.log(PASS3?'PASS  ifcFindLengthScale finds MILLI LENGTHUNIT -> 0.001':'FAIL  ifcFindLengthScale got '+scale3);

console.log('');
console.log('GRAND TOTAL: '+(PASS+PASS3)+' passed, '+(FAIL+(1-PASS3))+' failed');
process.exit((FAIL>0||PASS3!==1)?1:0);
