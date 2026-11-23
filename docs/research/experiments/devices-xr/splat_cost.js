// Our own measurement: CPU cost of splat operations on 1,000,000 synthetic splats (ES5-style loops).
var N = 1000000, RUNS = 5;
var pos = new Float32Array(N*3), rgba = new Uint8Array(N*4);
var seed = 12345; function rnd(){ seed = (seed + 0x6D2B79F5) | 0; var t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
for (var i=0;i<N;i++){ pos[3*i]=rnd()*40-20; pos[3*i+1]=rnd()*10; pos[3*i+2]=rnd()*40-20; rgba[4*i]=rnd()*255; rgba[4*i+1]=rnd()*255; rgba[4*i+2]=rnd()*255; rgba[4*i+3]=255; }
function time(label, f){ var t=[]; for (var r=0;r<RUNS;r++){ var a=process.hrtime.bigint(); f(); t.push(Number(process.hrtime.bigint()-a)/1e6); } t.sort(function(a,b){return a-b;}); console.log(label+': median '+t[2].toFixed(1)+' ms, min '+t[0].toFixed(1)+', max '+t[4].toFixed(1)); }
var eye=[3,1.6,-2], key=new Int32Array(N), counts=new Uint32Array(65536), order=new Uint32Array(N);
time('16-bit counting sort by squared distance', function(){
  var mn=Infinity,mx=-Infinity,d2=new Float32Array(N);
  for (var i=0;i<N;i++){ var dx=pos[3*i]-eye[0],dy=pos[3*i+1]-eye[1],dz=pos[3*i+2]-eye[2]; var d=dx*dx+dy*dy+dz*dz; d2[i]=d; if(d<mn)mn=d; if(d>mx)mx=d; }
  var s=65535/(mx-mn||1); counts.fill(0);
  for (i=0;i<N;i++){ var k=65535-((d2[i]-mn)*s|0); key[i]=k; counts[k]++; }
  var acc=0; for (var b=0;b<65536;b++){ var c=counts[b]; counts[b]=acc; acc+=c; }
  for (i=0;i<N;i++) order[counts[key[i]]++]=i;
});
time('comparison sort (Array.prototype.sort) by squared distance, ties by index', function(){
  var d2=new Float64Array(N), idx=new Array(N);
  for (var i=0;i<N;i++){ var dx=pos[3*i]-eye[0],dy=pos[3*i+1]-eye[1],dz=pos[3*i+2]-eye[2]; d2[i]=dx*dx+dy*dy+dz*dz; idx[i]=i; }
  idx.sort(function(a,b){ return (d2[b]-d2[a]) || (a-b); });
});
var sel=new Uint8Array(N);
time('box selection (axis-aligned in the splat frame)', function(){
  var x0=-2,x1=2,y0=0,y1=3,z0=-2,z1=2;
  for (var i=0;i<N;i++){ var x=pos[3*i],y=pos[3*i+1],z=pos[3*i+2]; sel[i]=(x>=x0&&x<=x1&&y>=y0&&y<=y1&&z>=z0&&z<=z1)?1:0; }
});
time('sphere selection (pinch point, radius 0.5 m)', function(){
  var cx=1,cy=1.2,cz=1,r2=0.25;
  for (var i=0;i<N;i++){ var dx=pos[3*i]-cx,dy=pos[3*i+1]-cy,dz=pos[3*i+2]-cz; sel[i]=(dx*dx+dy*dy+dz*dz<=r2)?1:0; }
});
time('colour match to a reference splat (per channel within 0.2), whole cloud', function(){
  var r=rgba[0],g=rgba[1],b=rgba[2],t=0.2*255;
  for (var i=0;i<N;i++){ sel[i]=(Math.abs(rgba[4*i]-r)<=t&&Math.abs(rgba[4*i+1]-g)<=t&&Math.abs(rgba[4*i+2]-b)<=t)?1:0; }
});
// grow selection by position and colour: uniform grid hash, BFS from a seed
var cell=0.25, gx=Math.ceil(40/cell), gy=Math.ceil(10/cell), gz=Math.ceil(40/cell), cellOf=new Int32Array(N), start, next=new Int32Array(N);
time('build grid (0.25 m cells) for growing', function(){
  start=new Int32Array(gx*gy*gz).fill(-1);
  for (var i=0;i<N;i++){ var cx=Math.min(gx-1,((pos[3*i]+20)/cell)|0), cy=Math.min(gy-1,(pos[3*i+1]/cell)|0), cz=Math.min(gz-1,((pos[3*i+2]+20)/cell)|0); var c=(cx*gy+cy)*gz+cz; cellOf[i]=c; next[i]=start[c]; start[c]=i; }
});
time('grow from one seed: neighbours within 0.25 m and colour within 0.2 (random data, so it stays small)', function(){
  sel.fill(0); var q=[0]; sel[0]=1; var t=0.2*255, r2=cell*cell, n=0;
  while(q.length){ var i=q.pop(); n++; var c=cellOf[i], cz=c%gz, cy=((c/gz)|0)%gy, cx=(c/(gz*gy))|0;
    for (var ax=-1;ax<=1;ax++) for (var ay=-1;ay<=1;ay++) for (var az=-1;az<=1;az++){ var X=cx+ax,Y=cy+ay,Z=cz+az; if(X<0||Y<0||Z<0||X>=gx||Y>=gy||Z>=gz) continue;
      for (var j=start[(X*gy+Y)*gz+Z]; j>=0; j=next[j]){ if(sel[j]) continue; var dx=pos[3*j]-pos[3*i],dy=pos[3*j+1]-pos[3*i+1],dz=pos[3*j+2]-pos[3*i+2]; if(dx*dx+dy*dy+dz*dz>r2) continue;
        if(Math.abs(rgba[4*j]-rgba[4*i])<=t&&Math.abs(rgba[4*j+1]-rgba[4*i+1])<=t&&Math.abs(rgba[4*j+2]-rgba[4*i+2])<=t){ sel[j]=1; q.push(j); } } } }
  if (!time.reported){ console.log('  grown to '+n+' splats'); time.reported=1; }
});
console.log('node '+process.version+', '+require('os').cpus()[0].model+', '+require('os').cpus().length+' cpus');
