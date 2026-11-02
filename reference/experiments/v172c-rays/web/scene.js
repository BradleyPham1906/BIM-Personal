// V172c experiment: a box as the app's rays take it (box, triangles) and its faces but the bottom as sensors.
function box(x0,y0,z0,x1,y1,z1){
  var P=[[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]];
  var Q=[[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]],T=[],F=[];
  [[0,3,2,1]].concat(Q).forEach(function(q){T.push([P[q[0]],P[q[1]],P[q[2]]]);T.push([P[q[0]],P[q[2]],P[q[3]]]);});
  Q.forEach(function(q){var c=[0,0,0],k,e1,e2,n,L;for(k=0;k<4;k++){c[0]+=P[q[k]][0]/4;c[1]+=P[q[k]][1]/4;c[2]+=P[q[k]][2]/4;}
    e1=[P[q[1]][0]-P[q[0]][0],P[q[1]][1]-P[q[0]][1],P[q[1]][2]-P[q[0]][2]];e2=[P[q[2]][0]-P[q[0]][0],P[q[2]][1]-P[q[0]][1],P[q[2]][2]-P[q[0]][2]];
    n=[e1[1]*e2[2]-e1[2]*e2[1],e1[2]*e2[0]-e1[0]*e2[2],e1[0]*e2[1]-e1[1]*e2[0]];L=Math.sqrt(n[0]*n[0]+n[1]*n[1]+n[2]*n[2]);
    F.push({p:c,n:[n[0]/L,n[1]/L,n[2]/L]});});
  return {o:{box:[x0,y0,z0,x1,y1,z1],tris:T},f:F};
}
if(typeof module!=="undefined"&&module)module.exports=box;else self.box=box;
