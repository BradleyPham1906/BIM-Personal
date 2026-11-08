
  /* ================= __acad3dV173: ColorBrewer's ramps =================
     Color specifications and designs developed by Cynthia Brewer (colorbrewer.org), Apache
     License 2.0: the colours of each scheme at each class count, as
     axismaps/colorbrewer's colorbrewer_schemes.js gives them (read 2026-11-07), six hex digits a
     colour, written into this file by a script from that file, never typed. Credited in
     THIRD_PARTY_NOTICES.md. */
  var BIM_RAMP_ORDER=['YlOrRd','YlGnBu','Blues','Greens','Purples','Greys','RdBu','RdYlBu'];
  var BIM_RAMPS={
    YlOrRd:{label:'Yellow, orange, red',min:3,max:9,c:{3:'ffeda0feb24cf03b20',4:'ffffb2fecc5cfd8d3ce31a1c',5:'ffffb2fecc5cfd8d3cf03b20bd0026',6:'ffffb2fed976feb24cfd8d3cf03b20bd0026',7:'ffffb2fed976feb24cfd8d3cfc4e2ae31a1cb10026',8:'ffffccffeda0fed976feb24cfd8d3cfc4e2ae31a1cb10026',9:'ffffccffeda0fed976feb24cfd8d3cfc4e2ae31a1cbd0026800026'}},
    YlGnBu:{label:'Yellow, green, blue',min:3,max:9,c:{3:'edf8b17fcdbb2c7fb8',4:'ffffcca1dab441b6c4225ea8',5:'ffffcca1dab441b6c42c7fb8253494',6:'ffffccc7e9b47fcdbb41b6c42c7fb8253494',7:'ffffccc7e9b47fcdbb41b6c41d91c0225ea80c2c84',8:'ffffd9edf8b1c7e9b47fcdbb41b6c41d91c0225ea80c2c84',9:'ffffd9edf8b1c7e9b47fcdbb41b6c41d91c0225ea8253494081d58'}},
    Blues:{label:'Blues',min:3,max:9,c:{3:'deebf79ecae13182bd',4:'eff3ffbdd7e76baed62171b5',5:'eff3ffbdd7e76baed63182bd08519c',6:'eff3ffc6dbef9ecae16baed63182bd08519c',7:'eff3ffc6dbef9ecae16baed64292c62171b5084594',8:'f7fbffdeebf7c6dbef9ecae16baed64292c62171b5084594',9:'f7fbffdeebf7c6dbef9ecae16baed64292c62171b508519c08306b'}},
    Greens:{label:'Greens',min:3,max:9,c:{3:'e5f5e0a1d99b31a354',4:'edf8e9bae4b374c476238b45',5:'edf8e9bae4b374c47631a354006d2c',6:'edf8e9c7e9c0a1d99b74c47631a354006d2c',7:'edf8e9c7e9c0a1d99b74c47641ab5d238b45005a32',8:'f7fcf5e5f5e0c7e9c0a1d99b74c47641ab5d238b45005a32',9:'f7fcf5e5f5e0c7e9c0a1d99b74c47641ab5d238b45006d2c00441b'}},
    Purples:{label:'Purples',min:3,max:9,c:{3:'efedf5bcbddc756bb1',4:'f2f0f7cbc9e29e9ac86a51a3',5:'f2f0f7cbc9e29e9ac8756bb154278f',6:'f2f0f7dadaebbcbddc9e9ac8756bb154278f',7:'f2f0f7dadaebbcbddc9e9ac8807dba6a51a34a1486',8:'fcfbfdefedf5dadaebbcbddc9e9ac8807dba6a51a34a1486',9:'fcfbfdefedf5dadaebbcbddc9e9ac8807dba6a51a354278f3f007d'}},
    Greys:{label:'Greys',min:3,max:9,c:{3:'f0f0f0bdbdbd636363',4:'f7f7f7cccccc969696525252',5:'f7f7f7cccccc969696636363252525',6:'f7f7f7d9d9d9bdbdbd969696636363252525',7:'f7f7f7d9d9d9bdbdbd969696737373525252252525',8:'fffffff0f0f0d9d9d9bdbdbd969696737373525252252525',9:'fffffff0f0f0d9d9d9bdbdbd969696737373525252252525000000'}},
    RdBu:{label:'Red to blue (diverging)',min:3,max:11,c:{3:'ef8a62f7f7f767a9cf',4:'ca0020f4a58292c5de0571b0',5:'ca0020f4a582f7f7f792c5de0571b0',6:'b2182bef8a62fddbc7d1e5f067a9cf2166ac',7:'b2182bef8a62fddbc7f7f7f7d1e5f067a9cf2166ac',8:'b2182bd6604df4a582fddbc7d1e5f092c5de4393c32166ac',9:'b2182bd6604df4a582fddbc7f7f7f7d1e5f092c5de4393c32166ac',10:'67001fb2182bd6604df4a582fddbc7d1e5f092c5de4393c32166ac053061',11:'67001fb2182bd6604df4a582fddbc7f7f7f7d1e5f092c5de4393c32166ac053061'}},
    RdYlBu:{label:'Red, yellow, blue (diverging)',min:3,max:11,c:{3:'fc8d59ffffbf91bfdb',4:'d7191cfdae61abd9e92c7bb6',5:'d7191cfdae61ffffbfabd9e92c7bb6',6:'d73027fc8d59fee090e0f3f891bfdb4575b4',7:'d73027fc8d59fee090ffffbfe0f3f891bfdb4575b4',8:'d73027f46d43fdae61fee090e0f3f8abd9e974add14575b4',9:'d73027f46d43fdae61fee090ffffbfe0f3f8abd9e974add14575b4',10:'a50026d73027f46d43fdae61fee090e0f3f8abd9e974add14575b4313695',11:'a50026d73027f46d43fdae61fee090ffffbfe0f3f8abd9e974add14575b4313695'}}
  };
  function bimRampHex(s){var out=[],i;for(i=0;i+6<=s.length;i+=6)out.push('#'+s.slice(i,i+6));return out;}
  function bimRampMix(a,b,t){
    var p=parseInt(a.slice(1),16),q=parseInt(b.slice(1),16),r=[16,8,0].map(function(sh){var x=(p>>sh)&255,y=(q>>sh)&255;return Math.round(x+(y-x)*t);});
    return '#'+r.map(function(v){return (v<16?'0':'')+v.toString(16);}).join('');
  }
  /* k colours of a ramp, light to dark (or reversed): the scheme's own colours from 3 to its most;
     1 or 2 classes take the ends of its 3; above its most, its largest scheme mixed evenly between
     its colours (ColorBrewer has no scheme there, so its colourblind checks do not cover it) */
  function bimRampColours(name,k,rev){
    var R=BIM_RAMPS.hasOwnProperty(name)?BIM_RAMPS[name]:BIM_RAMPS.YlOrRd,out,big,i,t,j;
    k=Math.max(1,Math.round(+k||1));
    if(k>=R.min&&k<=R.max)out=bimRampHex(R.c[k]);
    else if(k<R.min){big=bimRampHex(R.c[R.min]);out=k===1?[big[big.length-1]]:[big[0],big[big.length-1]];}
    else{
      big=bimRampHex(R.c[R.max]);out=[];
      for(i=0;i<k;i++){t=i*(big.length-1)/(k-1);j=Math.min(big.length-2,Math.floor(t));out.push(bimRampMix(big[j],big[j+1],t-j));}
    }
    return rev?out.slice().reverse():out;
  }
export { BIM_RAMPS, BIM_RAMP_ORDER, bimRampColours };
