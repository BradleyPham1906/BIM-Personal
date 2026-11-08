import { A3D } from '../core/state.js';
import { bimIdbGet, bimIdbPut, bimIdbPutMany } from '../core/idb-store.js';
import { a3dToast } from '../bim/csg-booleans.js';


  /* ================= __acad3dV174a: a board's images, kept once =================
     docs/research/research-presentation-boards.md, D4, and app-code-audit.md 6. The undo stack copies the whole
     project 50 times, so an image is never inline in a board: an element keeps its hash ('h' and 16 hex digits),
     and the image is kept once in the browser's database under 'img:<hash>', 4 MB at most. While the app runs, a
     loaded image is in memory as its data URL, for the project file, and as an object URL, for the page. An image
     is never removed when its element is: an undo can bring the element back. A project file carries the images its
     boards use (envelope field imgs), and opening one puts them back in the database. */
  var A3D_BIMG={data:{},url:{},wait:{},missing:{},redraw:null};
  function bimBimgLimit(){return 4*1024*1024;}
  function bimBimgTypes(){return ['image/png','image/jpeg','image/gif','image/webp'];}
  /* a hash of the data URL: two 32-bit FNV-1a passes, the second seeded otherwise; enough to name a file kept once */
  function bimBimgHash(s){
    var a=0x811c9dc5,b=0x01000193^s.length,i,c;
    for(i=0;i<s.length;i++){
      c=s.charCodeAt(i);
      a^=c;a=Math.imul?Math.imul(a,16777619):(a*16777619)|0;
      b^=c;b=Math.imul?Math.imul(b,2246822519|0):(b*2246822519)|0;
    }
    function hx(v){return ('0000000'+(v>>>0).toString(16)).slice(-8);}
    return 'h'+hx(a)+hx(b);
  }
  function bimBimgOk(d){
    if(typeof d!=='string'||d.length>Math.ceil(bimBimgLimit()*4/3)+64)return false;
    var m=/^data:([a-z\/+]+);base64,/.exec(d);
    return !!m&&bimBimgTypes().indexOf(m[1])>=0;
  }
  /* a data URL into memory: its object URL made once */
  function bimBimgKeep(h,d){
    A3D_BIMG.data[h]=d;delete A3D_BIMG.missing[h];
    if(A3D_BIMG.url[h])return;
    try{
      var m=/^data:([a-z\/+]+);base64,(.*)$/.exec(d),bin=atob(m[2]),u=new Uint8Array(bin.length),i;
      for(i=0;i<bin.length;i++)u[i]=bin.charCodeAt(i);
      A3D_BIMG.url[h]=URL.createObjectURL(new Blob([u],{type:m[1]}));
    }catch(eU){A3D_BIMG.url[h]=d;console.warn('[BIM] An image could not be given an object URL; its data is used',eU);}
  }
  /* what the page draws for an image: its URL, or null while it loads or when it is missing (missing: true) */
  function bimBimgUrl(h){
    if(A3D_BIMG.url[h])return A3D_BIMG.url[h];
    if(h&&!A3D_BIMG.missing[h])bimBimgLoad([h]);
    return null;
  }
  function bimBimgMissing(h){return !!A3D_BIMG.missing[h];}
  /* from the database, then done(); the board drawn again when one arrives */
  function bimBimgLoad(hs,done){
    var need=hs.filter(function(h){return h&&!A3D_BIMG.data[h]&&!A3D_BIMG.missing[h];}),left;
    if(!need.length){if(done)setTimeout(done,0);return;}
    left=need.length;
    need.forEach(function(h){
      if(A3D_BIMG.wait[h]){A3D_BIMG.wait[h].push(fin);return;}
      A3D_BIMG.wait[h]=[fin];
      bimIdbGet('img:'+h,function(err,v){
        var W=A3D_BIMG.wait[h]||[];
        delete A3D_BIMG.wait[h];
        if(!err&&v&&bimBimgOk(v.data))bimBimgKeep(h,v.data);
        else{A3D_BIMG.missing[h]=1;console.warn('[BIM] A board image is not in this browser\'s database: '+h,err||'');}
        W.forEach(function(f){f();});
        if(A3D_BIMG.redraw)try{A3D_BIMG.redraw();}catch(eR){console.warn('[BIM] The board could not be drawn again after an image loaded',eR);}
      });
    });
    function fin(){left--;if(left===0&&done)done();}
  }
  /* a file the user picked: refused over 4 MB or not an image; cb(hash, width, height) once it is kept */
  function bimBimgAdd(file,cb){
    if(!file){return;}
    if(bimBimgTypes().indexOf(file.type)<0){a3dToast(file.name+' is not a PNG, JPEG, GIF or WebP image');return;}
    if(file.size>bimBimgLimit()){a3dToast(file.name+' is over 4 MB: a board keeps images up to 4 MB');return;}
    var fr=new FileReader();
    fr.onerror=function(){console.warn('[BIM] An image could not be read',fr.error);a3dToast(file.name+' could not be read');};
    fr.onload=function(){
      var d=fr.result,h;
      if(!bimBimgOk(d)){a3dToast(file.name+' could not be read as an image');return;}
      h=bimBimgHash(d);
      bimBimgKeep(h,d);
      bimIdbPut('img:'+h,{data:d,saved:Date.now(),v:1},function(err){
        if(err){console.warn('[BIM] An image could not be kept in the browser\'s database',err);a3dToast('The image is on the board, but the browser would not keep it: it is lost at the next reload. Save the project as a file to keep it.');}
      });
      var im=new Image();
      im.onload=function(){cb(h,im.naturalWidth||1,im.naturalHeight||1);};
      im.onerror=function(){cb(h,4,3);};
      im.src=A3D_BIMG.url[h];
    };
    fr.readAsDataURL(file);
  }
  /* every image the boards of the set use */
  function bimBimgUsed(){
    var out=[],P=A3D.pres;
    if(!P||!Array.isArray(P.boards))return out;
    P.boards.forEach(function(B){
      if(B&&Array.isArray(B.objs))B.objs.forEach(function(n){if(n.t==='image'&&n.src&&out.indexOf(n.src)<0)out.push(n.src);});
    });
    return out;
  }
  /* for the project file: the images in memory, and how many are not */
  function bimBimgForFile(){
    var used=bimBimgUsed(),out={},lost=0;
    used.forEach(function(h){if(A3D_BIMG.data[h])out[h]=A3D_BIMG.data[h];else lost++;});
    if(lost){console.warn('[BIM] '+lost+' board image(s) were not loaded and are not in the project file');a3dToast(lost+' board image'+(lost===1?' is':'s are')+' not in this browser and not in the file');}
    return used.length?out:null;
  }
  /* from a project file: each good image kept, in memory and in the database */
  function bimBimgFromFile(map){
    var puts={},n=0,h;
    if(!map||typeof map!=='object')return 0;
    for(h in map)if(map.hasOwnProperty(h)&&/^h[0-9a-f]{16}$/.test(h)&&bimBimgOk(map[h])&&bimBimgHash(map[h])===h){
      bimBimgKeep(h,map[h]);puts['img:'+h]={data:map[h],saved:Date.now(),v:1};n++;
    }
    if(n)bimIdbPutMany(puts,function(err){if(err)console.warn('[BIM] The project file\'s images could not be kept in the browser\'s database',err);});
    return n;
  }
export {
  A3D_BIMG, bimBimgAdd, bimBimgForFile, bimBimgFromFile, bimBimgHash, bimBimgLoad, bimBimgMissing, bimBimgOk,
  bimBimgUrl, bimBimgUsed
};
