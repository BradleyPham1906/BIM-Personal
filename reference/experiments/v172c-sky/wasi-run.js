/* A run of a WASI command (wasi_snapshot_preview1) with stdin given as bytes and stdout, stderr gathered:
   only the twelve imports gendaymtx asks for; no files, no preopened folders. ES5. */
function bimWasiRun(module, args, stdin){
  var mem=null,inPos=0,out=[],err=[],code=0,EXIT={};
  stdin=stdin||new Uint8Array(0);
  function u8(){return new Uint8Array(mem.buffer);}
  function dv(){return new DataView(mem.buffer);}
  var enc=[],i,j,s,b;
  for(i=0;i<args.length;i++){s=unescape(encodeURIComponent(String(args[i])));b=[];for(j=0;j<s.length;j++)b.push(s.charCodeAt(j));b.push(0);enc.push(b);}
  function gather(fd,iovs,n,nw){
    var d=dv(),t=0,k,p,l,a=u8();
    for(k=0;k<n;k++){p=d.getUint32(iovs+8*k,true);l=d.getUint32(iovs+8*k+4,true);
      var c=a.slice(p,p+l);(fd===1?out:err).push(c);t+=l;}
    dv().setUint32(nw,t,true);return 0;
  }
  var W={
    args_sizes_get:function(pc,ps){var t=0;for(var k=0;k<enc.length;k++)t+=enc[k].length;var d=dv();d.setUint32(pc,enc.length,true);d.setUint32(ps,t,true);return 0;},
    args_get:function(pv,pb){var d=dv(),a=u8(),k;for(k=0;k<enc.length;k++){d.setUint32(pv+4*k,pb,true);a.set(enc[k],pb);pb+=enc[k].length;}return 0;},
    fd_write:function(fd,iovs,n,nw){if(fd!==1&&fd!==2)return 8;return gather(fd,iovs,n,nw);},
    fd_read:function(fd,iovs,n,nr){
      if(fd!==0)return 8;
      var d=dv(),a=u8(),t=0,k,p,l,m;
      for(k=0;k<n;k++){p=d.getUint32(iovs+8*k,true);l=d.getUint32(iovs+8*k+4,true);
        m=Math.min(l,stdin.length-inPos);if(m<=0)break;a.set(stdin.subarray(inPos,inPos+m),p);inPos+=m;t+=m;if(m<l)break;}
      dv().setUint32(nr,t,true);return 0;
    },
    fd_seek:function(fd,lo,whence,np){
      /* stdin only; the offset is an i64 (a BigInt where the engine passes one) */
      if(fd!==0)return 70;
      var off=typeof lo==='bigint'?Number(lo):lo,base=whence===0?0:whence===1?inPos:stdin.length,p=base+off;
      if(p<0||p>stdin.length)return 28;
      inPos=p;var d=dv();d.setUint32(np,p,true);d.setUint32(np+4,0,true);return 0;
    },
    fd_close:function(){return 0;},
    fd_fdstat_get:function(fd,st){if(fd>2)return 8;var d=dv(),k;for(k=0;k<24;k++)d.setUint8(st+k,0);d.setUint8(st,2);return 0;},
    fd_fdstat_set_flags:function(){return 0;},
    fd_prestat_get:function(){return 8;},
    fd_prestat_dir_name:function(){return 8;},
    path_open:function(){return 44;},
    proc_exit:function(c){code=c;throw EXIT;}
  };
  var inst=new WebAssembly.Instance(module,{wasi_snapshot_preview1:W});
  mem=inst.exports.memory;
  try{inst.exports._start();}catch(e){if(e!==EXIT)throw e;}
  function cat(L){var n=0,k,r,o=0;for(k=0;k<L.length;k++)n+=L[k].length;r=new Uint8Array(n);for(k=0;k<L.length;k++){r.set(L[k],o);o+=L[k].length;}return r;}
  return {code:code,stdout:cat(out),stderr:cat(err)};
}
if(typeof module!=='undefined')module.exports=bimWasiRun;
