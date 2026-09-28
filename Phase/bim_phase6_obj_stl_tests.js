// ---- OBJ parser (Y-up, matches engine convention directly - no axis remap needed) ----
function objParse(text){
  var lines=text.split(/\r\n|\r|\n/),i;
  var verts=[]; // global vertex list [x,y,z]
  var groups=[]; // {name, faces:[[vi,vi,vi,...]]} (1-indexed refs into verts)
  var cur={name:'default',faces:[]};
  groups.push(cur);
  for(i=0;i<lines.length;i++){
    var ln=lines[i].trim();
    if(!ln||ln.charAt(0)==='#')continue;
    var parts=ln.split(/\s+/);
    var tag=parts[0];
    if(tag==='v'){
      verts.push([parseFloat(parts[1]),parseFloat(parts[2]),parseFloat(parts[3])]);
    }else if(tag==='g'||tag==='o'){
      var nm=parts.slice(1).join(' ')||('group'+(groups.length));
      if(cur.faces.length===0 && cur===groups[groups.length-1] && groups.length===1 && cur.name==='default'){
        cur.name=nm; // rename the still-empty default group instead of creating a redundant one
      }else{
        cur={name:nm,faces:[]};
        groups.push(cur);
      }
    }else if(tag==='f'){
      var idx=[],k;
      for(k=1;k<parts.length;k++){
        var vi=parseInt(parts[k].split('/')[0],10);
        if(!isFinite(vi))continue;
        if(vi<0)vi=verts.length+1+vi; // negative = relative index from end
        idx.push(vi);
      }
      if(idx.length>=3)cur.faces.push(idx);
    }
  }
  groups=groups.filter(function(g){return g.faces.length>0;});
  // Build compact local meshes per non-empty group
  var out=[];
  for(i=0;i<groups.length;i++){
    var g=groups[i],vmap={},lv=[],lf=[],j,k2;
    for(j=0;j<g.faces.length;j++){
      var face=g.faces[j],lface=[];
      for(k2=0;k2<face.length;k2++){
        var gi=face[k2];
        if(vmap[gi]===undefined){vmap[gi]=lv.length;lv.push(verts[gi-1]||[0,0,0]);}
        lface.push(vmap[gi]);
      }
      lf.push(lface);
    }
    out.push({name:g.name,v:lv,f:lf});
  }
  return {meshes:out,vertCount:verts.length};
}

// ---- STL parser: sniff ASCII vs binary, both supported ----
function stlIsBinary(buf){
  // Binary STL: 80-byte header + 4-byte uint32 triCount, then 50 bytes/tri. Verify file length matches exactly.
  if(buf.byteLength<84)return false;
  var dv=new DataView(buf);
  var triCount=dv.getUint32(80,true);
  var expected=84+triCount*50;
  if(expected===buf.byteLength)return true;
  // Fallback: if it doesn't start with the ASCII 'solid' keyword, treat as binary anyway (many binary files start with "solid" too, which is the classic gotcha this size-check avoids)
  return false;
}
function stlParseBinary(buf){
  var dv=new DataView(buf);
  var triCount=dv.getUint32(80,true);
  var v=[],f=[],off=84,i;
  for(i=0;i<triCount;i++){
    var base=off+i*50;
    var ax=dv.getFloat32(base+12,true),ay=dv.getFloat32(base+16,true),az=dv.getFloat32(base+20,true);
    var bx=dv.getFloat32(base+24,true),by=dv.getFloat32(base+28,true),bz=dv.getFloat32(base+32,true);
    var cx=dv.getFloat32(base+36,true),cy=dv.getFloat32(base+40,true),cz=dv.getFloat32(base+44,true);
    var i0=v.length;
    v.push([ax,ay,az],[bx,by,bz],[cx,cy,cz]);
    f.push([i0,i0+1,i0+2]);
  }
  return {v:v,f:f};
}
function stlParseAscii(text){
  var v=[],f=[],re=/vertex\s+([\-0-9.eE+]+)\s+([\-0-9.eE+]+)\s+([\-0-9.eE+]+)/g,m,tri=[];
  while((m=re.exec(text))){
    tri.push([parseFloat(m[1]),parseFloat(m[2]),parseFloat(m[3])]);
    if(tri.length===3){
      var i0=v.length;
      v.push(tri[0],tri[1],tri[2]);
      f.push([i0,i0+1,i0+2]);
      tri=[];
    }
  }
  return {v:v,f:f};
}

// ==== TESTS ====
var PASS=0,FAIL=0;
function assert(name,cond){if(cond){PASS++;console.log('PASS  '+name);}else{FAIL++;console.log('FAIL  '+name);}}

// OBJ: a cube (8 verts, 6 quad faces) split across two named groups
var objSample=[
'# comment', 'o CubeBottom',
'v 0 0 0','v 1 0 0','v 1 1 0','v 0 1 0',
'v 0 0 1','v 1 0 1','v 1 1 1','v 0 1 1',
'f 1 2 3 4',
'g CubeSides',
'f 1 2 6 5','f 2 3 7 6','f 3 4 8 7','f 4 1 5 8',
'f 5 6 7 8'
].join('\n');
var objRes=objParse(objSample);
assert('OBJ parses into 2 named groups', objRes.meshes.length===2 && objRes.meshes[0].name==='CubeBottom' && objRes.meshes[1].name==='CubeSides');
assert('OBJ vertex count matches source (8)', objRes.vertCount===8);
assert('OBJ group faces re-indexed locally (no out-of-range refs)', objRes.meshes[1].f.every(function(fc){return fc.every(function(ix){return ix>=0&&ix<objRes.meshes[1].v.length;});}));
assert('OBJ total faces across groups = 6 (1 bottom + 4 sides + 1 top folded into CubeSides)', objRes.meshes[0].f.length+objRes.meshes[1].f.length===6);

// STL ASCII: single triangle
var stlAsciiSample=[
'solid test','facet normal 0 0 1','outer loop',
'vertex 0 0 0','vertex 1 0 0','vertex 0 1 0',
'endloop','endfacet','endsolid test'
].join('\n');
var stlA=stlParseAscii(stlAsciiSample);
assert('ASCII STL parses 1 triangle (3 verts, 1 face)', stlA.v.length===3 && stlA.f.length===1);

// STL binary: build a 2-triangle binary buffer programmatically and round-trip it
(function(){
  var triCount=2;
  var buf=new ArrayBuffer(84+triCount*50);
  var dv=new DataView(buf);
  dv.setUint32(80,triCount,true);
  function writeTri(base,pts){
    dv.setFloat32(base,0,true);dv.setFloat32(base+4,0,true);dv.setFloat32(base+8,1,true); // normal (unused by parser)
    var o=base+12,k;
    for(k=0;k<3;k++){dv.setFloat32(o,pts[k][0],true);dv.setFloat32(o+4,pts[k][1],true);dv.setFloat32(o+8,pts[k][2],true);o+=12;}
    dv.setUint16(base+48,0,true);
  }
  writeTri(84,[[0,0,0],[1,0,0],[0,1,0]]);
  writeTri(134,[[1,0,0],[1,1,0],[0,1,0]]);
  assert('binary STL sniff detects binary correctly', stlIsBinary(buf)===true);
  var parsed=stlParseBinary(buf);
  assert('binary STL parses 2 triangles (6 verts, 2 faces)', parsed.v.length===6 && parsed.f.length===2);
  assert('binary STL vertex coordinates round-trip correctly', parsed.v[3][0]===1 && parsed.v[3][1]===0 && parsed.v[3][2]===0);
})();

// Sniff should NOT classify a genuine short ASCII file as binary
(function(){
  var enc=Buffer.from(stlAsciiSample,'utf8');
  var ab=enc.buffer.slice(enc.byteOffset,enc.byteOffset+enc.byteLength);
  assert('ASCII STL is correctly NOT sniffed as binary', stlIsBinary(ab)===false);
})();

console.log('');
console.log('TOTAL: '+PASS+' passed, '+FAIL+' failed');
process.exit(FAIL>0?1:0);
