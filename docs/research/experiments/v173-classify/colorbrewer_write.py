# V173a: writes src/js/engine/map/colour-ramps.js from axismaps/colorbrewer's colorbrewer_schemes.js
# (https://raw.githubusercontent.com/axismaps/colorbrewer/master/colorbrewer_schemes.js), read as text,
# never run. Usage: python -I colorbrewer_write.py <colorbrewer_schemes.js> <out.js>
import re,sys
s=open(sys.argv[1],encoding='utf-8').read()
order=[('YlOrRd','Yellow, orange, red'),('YlGnBu','Yellow, green, blue'),('Blues','Blues'),('Greens','Greens'),('Purples','Purples'),('Greys','Greys'),('RdBu','Red to blue (diverging)'),('RdYlBu','Red, yellow, blue (diverging)')]
lines=[]
for name,label in order:
    m=re.search(r'\n'+name+r':\s*\{(.*?)\'properties\'',s,re.S)
    d={}
    for k,arr in re.findall(r'(\d+):\s*\[([^\]]*)\]',m.group(1)):
        d[int(k)]=''.join('%02x%02x%02x'%tuple(map(int,c)) for c in re.findall(r'rgb\((\d+),(\d+),(\d+)\)',arr))
    ks=sorted(d)
    assert ks[0]==3 and ks==list(range(3,ks[-1]+1)) and all(len(d[k])==6*k for k in ks)
    lines.append("    %s:{label:'%s',min:3,max:%d,c:{%s}}"%(name,label,ks[-1],','.join("%d:'%s'"%(k,d[k]) for k in ks)))
js='''
  /* ================= __acad3dV173: ColorBrewer's ramps =================
     Color specifications and designs developed by Cynthia Brewer (colorbrewer.org), Apache
     License 2.0: the colours of each scheme at each class count, as
     axismaps/colorbrewer's colorbrewer_schemes.js gives them (read 2026-11-07), six hex digits a
     colour, written into this file by a script from that file, never typed. Credited in
     THIRD_PARTY_NOTICES.md. */
  var BIM_RAMP_ORDER=[%s];
  var BIM_RAMPS={
%s
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
'''%(','.join("'%s'"%n for n,_ in order),',\n'.join(lines))
open(sys.argv[2],'w',encoding='utf-8',newline='\n').write(js)
