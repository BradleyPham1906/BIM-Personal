

  /* ================= __acad3dV229: A split grammar for facades, the pure part =================
     docs/research/research-algorithmic-design.md and docs/work-orders/v229/SPEC.md. Rules kept as data: sizes resolved in a
     split (absolute, relative, floating), a repeat to the nearest count, the rules checked before anything runs, and the
     derivation of a rectangle into named leaves with their paths. Each function is a work order, added below as it is
     built; none uses another file's names. */
function bimSgSizes(len, sizes) {
  if (!sizes || sizes.length === 0) return [];
  var totalAbsRel = 0;
  var floats = [];
  for (var i = 0; i < sizes.length; i++) {
    var s = sizes[i];
    if (typeof s === 'number') {
      var v = s < 0 ? 0 : s;
      totalAbsRel += v;
    } else if (s && typeof s === 'object' && s.rel !== undefined) {
      var r = s.rel < 0 ? 0 : s.rel;
      totalAbsRel += r * len;
    } else if (s && typeof s === 'object' && s.fl !== undefined) {
      var f = s.fl < 0 ? 0 : s.fl;
      floats.push(f);
    }
  }
  var remaining = Math.max(0, len - totalAbsRel);
  var sumF = 0;
  for (var j = 0; j < floats.length; j++) sumF += floats[j];
  var result = [];
  for (var k = 0; k < sizes.length; k++) {
    var s = sizes[k];
    if (typeof s === 'number') {
      var v = s < 0 ? 0 : s;
      result.push(v);
    } else if (s && typeof s === 'object' && s.rel !== undefined) {
      var r = s.rel < 0 ? 0 : s.rel;
      result.push(r * len);
    } else if (s && typeof s === 'object' && s.fl !== undefined) {
      var f = s.fl < 0 ? 0 : s.fl;
      var val = sumF > 0 ? (f / sumF) * remaining : 0;
      result.push(val);
    }
  }
  return result;
}
function bimSgSplit(len, sizes) {
  var totalAbs=0,totalRel=0,floatVals=[],floatIndices=[];
  for(var i=0;i<sizes.length;i++){var s=sizes[i];if(typeof s==='number'){totalAbs+=s<0?0:s}else if(s&&typeof s==='object'&&s.rel!==undefined){totalRel+=(s.rel<0?0:s.rel)*len}else if(s&&typeof s==='object'&&s.fl!==undefined){floatIndices.push(i);floatVals.push(s.fl<0?0:s.fl)}}var sumF=0;for(var j=0;j<floatVals.length;j++)sumF+=floatVals[j];var remaining=Math.max(0,len-totalAbs-totalRel);var floatSizes=[];for(var j=0;j<floatVals.length;j++)floatSizes.push(sumF>0?(floatVals[j]/sumF)*remaining:0);var runningTotal=0,result=[];for(var i=0;i<sizes.length;i++){var s=sizes[i],size;if(typeof s==='number'){size=s<0?0:s;if(runningTotal+size>len)size=len-runningTotal}else if(s&&typeof s==='object'&&s.rel!==undefined){size=(s.rel<0?0:s.rel)*len;if(runningTotal+size>len)size=len-runningTotal}else if(s&&typeof s==='object'&&s.fl!==undefined){var fi=floatIndices.indexOf(i);size=fi!==-1?floatSizes[fi]:0}else size=0;if(size<0)size=0;if(size>0){result.push({i:i,at:runningTotal,size:size});runningTotal+=size}if(runningTotal>=len-1e-9)break}return result}
function bimSgRepeat(len, size) {
  if (len <= 0 || size <= 0) return { n: 0, size: 0 };
  var n = Math.max(1, Math.floor(len / size + 0.5 + 1e-9));
  return { n: n, size: len / n };
}
