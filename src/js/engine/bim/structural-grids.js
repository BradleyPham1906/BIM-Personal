  /* ---------- Phase 42: structural grid datums ----------
     Grids are datums, not model elements: they live in A3D.grids rather than A3D.objs,
     span every level (a grid is a vertical plane in Revit, so it is stored as a plan
     line and drawn at whatever level is current) and are named in a continuing
     sequence the way Revit continues from the last placed grid. ---------- */
  function bimGridNextName(){
    var ex=A3D.grids.map(function(g){return g.name;});
    if(!ex.length)return 'A';
    var last=ex[ex.length-1];
    if(/^\d+$/.test(last))return String(parseInt(last,10)+1);
    if(/^[A-Z]+$/.test(last)){
      var a=last.split(''),i=a.length-1;
      while(i>=0){
        if(a[i]==='Z'){a[i]='A';i--;}
        else{a[i]=String.fromCharCode(a[i].charCodeAt(0)+1);return a.join('');}
      }
      return 'A'+a.join('');
    }
    return 'Grid '+(ex.length+1);
  }
  function bimSegIntersect(a1,a2,b1,b2){
    var r=[a2[0]-a1[0],a2[1]-a1[1]],q=[b2[0]-b1[0],b2[1]-b1[1]];
    var den=r[0]*q[1]-r[1]*q[0];
    if(Math.abs(den)<1e-12)return null;
    var qp=[b1[0]-a1[0],b1[1]-a1[1]];
    var t=(qp[0]*q[1]-qp[1]*q[0])/den,u=(qp[0]*r[1]-qp[1]*r[0])/den;
    if(t<-1e-9||t>1+1e-9||u<-1e-9||u>1+1e-9)return null;
    return [a1[0]+t*r[0],a1[1]+t*r[1]];
  }
  function bimGridSnapPoints(){
    var pts=[],i,j;
    for(i=0;i<A3D.grids.length;i++){
      var g=A3D.grids[i];
      pts.push([g.p1[0],g.p1[1]]);
      pts.push([g.p2[0],g.p2[1]]);
      for(j=i+1;j<A3D.grids.length;j++){
        var x=bimSegIntersect(g.p1,g.p2,A3D.grids[j].p1,A3D.grids[j].p2);
        if(x)pts.push(x);
      }
    }
    return pts;
  }
  function bimAddGrid(p1,p2){
    var dx=p2[0]-p1[0],dz=p2[1]-p1[1];
    if(Math.sqrt(dx*dx+dz*dz)<1e-6){a3dToast('Grid line is too short');return null;}
    pushUndo();
    var g={id:'grid-'+Date.now().toString(36)+'-'+(A3D.seq++),name:bimGridNextName(),
      p1:[p1[0],p1[1]],p2:[p2[0],p2[1]]};
    A3D.grids.push(g);
    refreshLevels();refreshTree();paint();saveSoon();
    a3dToast('Grid '+g.name+' placed');
    return g;
  }
