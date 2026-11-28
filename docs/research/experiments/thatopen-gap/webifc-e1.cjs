// e1: web-ifc 0.0.81 (npm pack, run unchanged). (a) axes and units of StreamAllMeshes output; (b) the writer.
const path=require('path'),fs=require('fs');
const pkg=process.argv[2], ifcPath=process.argv[3];
const W=require(path.join(pkg,'web-ifc-api-node.js'));
(async()=>{
  const api=new W.IfcAPI(); api.SetWasmPath(pkg+'/',true); await api.Init();
  console.log('version',api.GetVersion());
  const bytes=new Uint8Array(fs.readFileSync(ifcPath));
  for (const c2o of [false,true]){
    const mid=api.OpenModel(bytes,{COORDINATE_TO_ORIGIN:c2o});
    console.log('schema',api.GetModelSchema(mid),'C2O',c2o);
    api.StreamAllMeshes(mid,(m)=>{
      let mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];
      for(let i=0;i<m.geometries.size();i++){const g=m.geometries.get(i),G=api.GetGeometry(mid,g.geometryExpressID);
        const v=api.GetVertexArray(G.GetVertexData(),G.GetVertexDataSize()),t=g.flatTransformation;
        for(let k=0;k<v.length;k+=6){const x=v[k],y=v[k+1],z=v[k+2];const p=[t[0]*x+t[4]*y+t[8]*z+t[12],t[1]*x+t[5]*y+t[9]*z+t[13],t[2]*x+t[6]*y+t[10]*z+t[14]];
          for(let j=0;j<3;j++){mn[j]=Math.min(mn[j],p[j]);mx[j]=Math.max(mx[j],p[j]);}}
        G.delete();}
      console.log(' elem',m.expressID,api.GetNameFromTypeCode(api.GetLineType(mid,m.expressID)),'min',mn.map(n=>+n.toFixed(3)),'max',mx.map(n=>+n.toFixed(3)));
    });
    console.log(' coord',Array.from(api.GetCoordinationMatrix(mid)).map(n=>+n.toFixed(3)).join(','));
    api.CloseModel(mid);
  }
  // (b) writer: a minimal IFC4 project + wall with no geometry, then a wall missing its GlobalId
  const id=api.CreateModel({schema:'IFC4',name:'e1.ifc'});
  const S=W.IFC4;
  const proj=new S.IfcProject(api.CreateIFCGloballyUniqueId(id),null,new S.IfcLabel('P'),null,null,null,null,null,null);
  api.WriteLine(id,proj);
  const wall=new S.IfcWall(api.CreateIFCGloballyUniqueId(id),null,new S.IfcLabel('W'),null,null,null,null,null,null);
  api.WriteLine(id,wall);
  let bad='written';
  try{const w2=new S.IfcWall(null,null,null,null,null,null,null,null,null);api.WriteLine(id,w2);}catch(e){bad='threw '+e.message;}
  console.log('wall without GlobalId (required):',bad);
  const out=api.SaveModel(id); const txt=new TextDecoder().decode(out);
  console.log('saved bytes',out.length); console.log(txt.split('\n').filter(l=>/FILE_|IFCPROJECT|IFCWALL/.test(l)).join('\n'));
  const guid=api.CreateIFCGloballyUniqueId(id).value; console.log('guid',guid,guid.length);
  const back=api.OpenModel(out); console.log('reopened lines',api.GetAllLines(back).size());
})().catch(e=>{console.error('ERR',e);process.exit(1);});
