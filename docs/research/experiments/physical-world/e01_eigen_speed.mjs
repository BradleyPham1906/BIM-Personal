/* e01: how big a symmetric eigenproblem plain ES5-style JS solves fast enough (cyclic Jacobi, and
   subspace iteration on a banded matrix). Data only, not a suite. Run: node e01_eigen_speed.mjs */
function jacobi(A0){var n=A0.length,A=A0.map(function(r){return r.slice();}),V=[],i,j,k,sweep;
  for(i=0;i<n;i++){V.push(new Array(n).fill(0));V[i][i]=1;}
  for(sweep=0;sweep<60;sweep++){var off=0;for(i=0;i<n;i++)for(j=i+1;j<n;j++)off+=A[i][j]*A[i][j];if(off<1e-22)break;
    for(i=0;i<n;i++)for(j=i+1;j<n;j++){if(Math.abs(A[i][j])<1e-300)continue;
      var th=(A[j][j]-A[i][i])/(2*A[i][j]),t=(th>=0?1:-1)/(Math.abs(th)+Math.sqrt(th*th+1)),c=1/Math.sqrt(t*t+1),s=t*c;
      for(k=0;k<n;k++){var aki=A[k][i],akj=A[k][j];A[k][i]=c*aki-s*akj;A[k][j]=s*aki+c*akj;}
      for(k=0;k<n;k++){var aik=A[i][k],ajk=A[j][k];A[i][k]=c*aik-s*ajk;A[j][k]=s*aik+c*ajk;}
      for(k=0;k<n;k++){var vki=V[k][i],vkj=V[k][j];V[k][i]=c*vki-s*vkj;V[k][j]=s*vki+c*vkj;}}
  }return {d:A.map(function(r,i){return r[i];}),V:V,sweeps:sweep};}
/* a shear building of n storeys: k each, m each; exact w_r = 2 sqrt(k/m) sin((2r-1)pi/(2(2n+1))) */
function shear(n,k){var K=[],i;for(i=0;i<n;i++){K.push(new Array(n).fill(0));}
  for(i=0;i<n;i++){K[i][i]=(i<n-1?2:1)*k;if(i>0){K[i][i-1]=-k;K[i-1][i]=-k;}}return K;}
var rows=[];
[10,30,60,120,240].forEach(function(n){var K=shear(n,1000),t=Date.now(),r=jacobi(K),ms=Date.now()-t;
  var d=r.d.slice().sort(function(a,b){return a-b;}),ex=2*Math.sqrt(1000)*Math.sin(Math.PI/(2*(2*n+1)));
  rows.push({n:n,ms:ms,sweeps:r.sweeps,w1:Math.sqrt(d[0]),w1exact:ex,relErr:Math.abs(Math.sqrt(d[0])-ex)/ex});});
console.log('node',process.version);console.table(rows);
