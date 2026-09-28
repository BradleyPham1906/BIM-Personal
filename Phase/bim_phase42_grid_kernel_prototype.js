/* Phase 42 structural grid kernel prototype (ES5 style). */
function gridNextName(existing){
  /* Revit-style: continue the sequence of the last placed grid.
     Numeric names increment numerically; alphabetic roll A..Z,AA,AB.. */
  if(!existing.length)return 'A';
  var last=existing[existing.length-1];
  if(/^\d+$/.test(last))return String(parseInt(last,10)+1);
  if(/^[A-Z]+$/.test(last)){
    var s=last.split(''),i=s.length-1;
    while(i>=0){
      if(s[i]==='Z'){s[i]='A';i--;}
      else{s[i]=String.fromCharCode(s[i].charCodeAt(0)+1);return s.join('');}
    }
    return 'A'+s.join('');
  }
  return 'Grid '+(existing.length+1);
}
function segIntersect(a1,a2,b1,b2){
  var r=[a2[0]-a1[0],a2[1]-a1[1]],s=[b2[0]-b1[0],b2[1]-b1[1]];
  var den=r[0]*s[1]-r[1]*s[0];
  if(Math.abs(den)<1e-12)return null;               /* parallel */
  var qp=[b1[0]-a1[0],b1[1]-a1[1]];
  var t=(qp[0]*s[1]-qp[1]*s[0])/den;
  var u=(qp[0]*r[1]-qp[1]*r[0])/den;
  if(t<-1e-9||t>1+1e-9||u<-1e-9||u>1+1e-9)return null;
  return [a1[0]+t*r[0],a1[1]+t*r[1]];
}
function gridSnapPoints(grids){
  var pts=[],i,j;
  for(i=0;i<grids.length;i++){
    pts.push([grids[i].p1[0],grids[i].p1[1]]);
    pts.push([grids[i].p2[0],grids[i].p2[1]]);
    for(j=i+1;j<grids.length;j++){
      var x=segIntersect(grids[i].p1,grids[i].p2,grids[j].p1,grids[j].p2);
      if(x)pts.push(x);
    }
  }
  return pts;
}
module.exports={gridNextName:gridNextName,segIntersect:segIntersect,gridSnapPoints:gridSnapPoints};
