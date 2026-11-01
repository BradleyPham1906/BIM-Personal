// V172c experiment: numpy from the committed runtime, by Pyodide's own loadPackage (it checks the lock's SHA-256).
var R=process.argv[2];
(async function(){
  var py=await require(R+'/pyodide/0.29.5/pyodide.js').loadPyodide({indexURL:R+'/pyodide/0.29.5/'});
  var t=Date.now();await py.loadPackage('numpy',{messageCallback:function(m){console.log('  '+m);}});
  console.log('numpy loaded in',Date.now()-t,'ms:',py.runPython('import numpy as np\nnp.__version__ + " " + str(np.dot(np.ones((3,4)), np.arange(4.0)).tolist())'));
})().catch(function(e){console.error('FAILED',e.message);process.exit(1);});
