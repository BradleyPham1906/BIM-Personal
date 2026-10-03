"""patch_phase133d.py -- V133: the map, from the owner's first use on a real site.

The owner opened the app as a file and turned the map on. Two things were wrong:
- The street map was "Access blocked" tiles. OpenStreetMap's volunteer tile servers now refuse a
  request with no Referer, and a page opened from a file sends none. The refusal is itself an
  image, so the page cannot tell it from a map. The street map is now CARTO's Voyager (OSM's data,
  free with credit, no key), with @2x tiles on a dense screen.
- The satellite looked blurry. The zoom was chosen in CSS pixels, so a Retina screen got tiles a
  level too coarse everywhere; and a tile drawn smaller than its pixels had no mipmaps. Now the
  zoom counts the screen's density (a template with {r} gets @2x tiles instead), and the cap on
  tiles grows with it; tiles are mipmapped. Past Esri's zoom 19 the imagery is stretched: that is
  the source's limit, said in the research note.
- Nominatim refusing a search (HTTP 403, for the same missing Referer) or being busy is said as
  such, instead of "could not be reached"."""
NAME = 'patch_phase133d.py'
BASE = 'c6a0a1da1945979bb54e3223d7d2c99ae355d7832c41276a91e111b8ccde9116'
import hashlib, pathlib, sys
P = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'canvas_v10.html')
raw = P.read_bytes()
h0 = hashlib.sha256(raw).hexdigest()
if h0 != BASE:
    sys.exit('ABORT: baseline %s, expected %s' % (h0, BASE))
t = raw.decode('utf-8')


def rep(old, new, n=1):
    global t
    c = t.count(old)
    if c != n:
        sys.exit('ABORT: %d occurrences, expected %d: %r' % (c, n, old[:90]))
    t = t.replace(old, new)


rep("""    street:{name:'Street (OpenStreetMap)',url:'https://tile.openstreetmap.org/{z}/{x}/{y}.png',maxz:19,
      credit:'\\u00a9 OpenStreetMap contributors',link:'https://www.openstreetmap.org/copyright'},""",
    """    /* __acad3dV133d: CARTO's Voyager, OSM's data. OpenStreetMap's own tile servers refuse a request
       with no Referer, which is every request from a page opened as a file. */
    street:{name:'Street (CARTO, OpenStreetMap data)',url:'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',maxz:19,
      credit:'\\u00a9 OpenStreetMap contributors \\u00a9 CARTO',link:'https://www.openstreetmap.org/copyright'},""")
# {r}: @2x tiles on a dense screen
rep("""    return tpl.split('{z}').join(String(z)).split('{x}').join(String(xx)).split('{y}').join(String(y));""",
    """    return tpl.split('{z}').join(String(z)).split('{x}').join(String(xx)).split('{y}').join(String(y))
      .split('{r}').join(bimMapDpr()>1.5?'@2x':'');   /* __acad3dV133d */""")
rep("""  function bimMapHost(url){""", """  /* __acad3dV133d: the screen's density, 1 to 2 */
  function bimMapDpr(){var d=window.devicePixelRatio||1;return d>2?2:(d<1?1:d);}
  function bimMapHost(url){""")
# the zoom in device pixels, unless the tiles are @2x already; the cap grows with the density
rep("""    var z=Math.round(Math.log(156543.03392*Math.cos(org.lat*BIM_D2R)/mpp)/Math.LN2),x0,x1,y0,y1,n;""",
    """    var dz=tpl.indexOf('{r}')>=0?1:bimMapDpr(),maxT=Math.round(BIM_MAP_MAXT*bimMapDpr());   /* __acad3dV133d */
    var z=Math.round(Math.log(156543.03392*Math.cos(org.lat*BIM_D2R)*dz/mpp)/Math.LN2),x0,x1,y0,y1,n;""")
rep("""      if((x1-x0+1)*(y1-y0+1)<=BIM_MAP_MAXT||z<=1)break;""",
    """      if((x1-x0+1)*(y1-y0+1)<=maxT||z<=1)break;""")
# mipmaps
rep("""      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,e.img);
      gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);""",
    """      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,e.img);
      /* __acad3dV133d: mipmaps, so a tile drawn smaller than its pixels is filtered, not sparkling */
      var tw=e.img.naturalWidth||e.img.width,th=e.img.naturalHeight||e.img.height;
      if(tw&&th&&!(tw&(tw-1))&&!(th&(th-1))){gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);e.mip=true;}
      else gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);""")
# Nominatim's refusals said as such
rep("""      if(!res.ok)throw new Error('HTTP '+res.status);
      return res.json();""", """      if(!res.ok)throw {http:res.status};   /* __acad3dV133d */
      return res.json();""")
rep("""      a3dToast('Address search failed: nominatim.openstreetmap.org could not be reached (offline, or it does not allow browser access)');
      return {found:false,q:q,error:String(err&&err.message?err.message:err)};""",
    """      var hs=err&&err.http;
      a3dToast('Address search failed: nominatim.openstreetmap.org '+(hs===403?'refused it (HTTP 403): it asks for the app to be opened from a website, not a file -- set the latitude and longitude in Properties instead':
        (hs===429?'is busy (HTTP 429): try again in a minute':(hs?'answered HTTP '+hs:'could not be reached (offline, or it does not allow browser access)'))));
      return {found:false,q:q,error:hs?'HTTP '+hs:String(err&&err.message?err.message:err)};""")
rep("""  window.__acad3dV133='""", """  window.__acad3dV133d='cartostreet,retinatiles,dprzoom,mipmaps,nominatimrefusal';
  window.__a3dMapDpr=function(){return bimMapDpr();};
  window.__a3dMapMipmapped=function(){var k,n=0,m=0;for(k in A3D_MAP.cache)if(A3D_MAP.cache.hasOwnProperty(k)&&A3D_MAP.cache[k].tex){n++;if(A3D_MAP.cache[k].mip)m++;}return {textures:n,mipmapped:m};};
  window.__acad3dV133='""")

out = t.encode('utf-8')
P.write_bytes(out)
print('%s: %d -> %d bytes, sha256 %s' % (NAME, len(raw), len(out), hashlib.sha256(out).hexdigest()))
