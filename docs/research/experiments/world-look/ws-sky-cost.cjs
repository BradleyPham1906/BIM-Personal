// ws-sky-cost.cjs: the relative cost of sky, cloud and rain techniques as full-screen WebGL2 passes, timed in
// headless Chromium (Playwright). Headless Chromium here renders WebGL through SwiftShader, on the CPU: the numbers
// are SOFTWARE RENDERING on this machine, useful only to rank the techniques against each other, never as a phone's
// or a GPU's frame time. Every shader below is written here from the method its source describes (none of the
// downloaded code is run): the app's gradient dome (rendered-core.js), an analytic sky in Preetham's form with a
// 4-octave gradient-noise cloud layer (the method of three.js r186 Sky.js), a per-pixel ray-marched single-scattering
// atmosphere (30 view steps x 8 light steps, Hillaire 2020 section 5 without its LUTs), the same march into a small
// sky-view texture (200 x 100 and 96 x 50, Hillaire's PC and iPhone 6s sizes) then sampled full screen, and N
// camera-near rain streaks as instanced quads.
// Usage: node ws-sky-cost.cjs > ws-sky-cost-results.json      2026-11-24
const { chromium } = require('playwright');
const PAGE = `<!doctype html><canvas id=c></canvas><script>
const VS='#version 300 es\\nout vec2 uv; void main(){ vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2); uv=p; gl_Position=vec4(p*2.0-1.0,0.0,1.0); }';
const HEAD='#version 300 es\\nprecision highp float; in vec2 uv; out vec4 o; uniform float t; uniform vec3 sun; uniform sampler2D lut;\\n'+
 'vec3 dirOf(vec2 q){ float az=q.x*6.2831853; float el=(q.y-0.35)*1.6; return normalize(vec3(cos(el)*cos(az),sin(el),cos(el)*sin(az))); }\\n';
const NOISE='vec2 g2(vec2 i){ vec3 p=fract(i.xyx*vec3(0.1031,0.1030,0.0973)); p+=dot(p,p.yzx+33.33); return fract((p.xx+p.yz)*p.zy)*2.0-1.0; }\\n'+
 'float nz(vec2 p){ vec2 i=floor(p),f=fract(p),u=f*f*f*(f*(f*6.0-15.0)+10.0); return mix(mix(dot(g2(i),f),dot(g2(i+vec2(1,0)),f-vec2(1,0)),u.x),mix(dot(g2(i+vec2(0,1)),f-vec2(0,1)),dot(g2(i+vec2(1,1)),f-vec2(1,1)),u.x),u.y)*1.6; }\\n'+
 'float fbm(vec2 p,float d){ float r=0.0,a=1.0; for(int i=0;i<4;i++){ r+=a*nz(p); a*=0.5; p=p*2.0+d; } return r; }\\n';
const ATM='const float Re=6360e3, Ra=6460e3; const vec3 bR=vec3(5.8e-6,13.5e-6,33.1e-6); const float bM=21e-6;\\n'+
 'vec2 rs(vec3 o,vec3 d,float r){ float b=dot(o,d),c=dot(o,o)-r*r,h=b*b-c; if(h<0.0) return vec2(1e9,-1e9); h=sqrt(h); return vec2(-b-h,-b+h); }\\n'+
 'vec3 march(vec3 d,int N,int L){ vec3 o=vec3(0,Re+2.0,0); float tm=rs(o,d,Ra).y; float ds=tm/float(N); vec3 sR=vec3(0),sM=vec3(0); float oR=0.0,oM=0.0;\\n'+
 ' for(int i=0;i<64;i++){ if(i>=N) break; vec3 p=o+d*(ds*(float(i)+0.5)); float h=length(p)-Re; float hr=exp(-h/8e3)*ds, hm=exp(-h/1.2e3)*ds; oR+=hr; oM+=hm;\\n'+
 '  float tl=rs(p,sun,Ra).y, dl=tl/float(L), lR=0.0,lM=0.0; for(int j=0;j<16;j++){ if(j>=L) break; vec3 q=p+sun*(dl*(float(j)+0.5)); float hl=length(q)-Re; lR+=exp(-hl/8e3)*dl; lM+=exp(-hl/1.2e3)*dl; }\\n'+
 '  vec3 tau=bR*(oR+lR)+bM*1.1*(oM+lM); vec3 att=exp(-tau); sR+=hr*att; sM+=hm*att; }\\n'+
 ' float mu=dot(d,sun); float pR=3.0/(16.0*3.14159)*(1.0+mu*mu); float g=0.76; float pM=3.0/(8.0*3.14159)*((1.0-g*g)*(1.0+mu*mu))/((2.0+g*g)*pow(1.0+g*g-2.0*g*mu,1.5));\\n'+
 ' return 20.0*(sR*bR*pR+sM*bM*pM); }\\n';
const FS={
 gradient: HEAD+'void main(){ float z=dirOf(uv).y; vec3 c=z>=0.0?mix(vec3(.77,.84,.91),vec3(.18,.42,.70),pow(z,0.6)):mix(vec3(.77,.84,.91),vec3(.56,.54,.5),pow(-z,0.4)); o=vec4(c,1); }',
 analytic_clouds: HEAD+NOISE+'void main(){ vec3 d=dirOf(uv); float z=max(d.y,0.0); float za=acos(z); float inv=1.0/(cos(za)+0.15*pow(93.885-za*57.2958,-1.253));\\n'+
  ' vec3 Fex=exp(-(vec3(5.8e-6,1.36e-5,3.03e-5)*8.4e3+vec3(2e-5)*1.25e3)*inv); float ct=dot(d,sun); vec3 Lin=pow((1.0-Fex)*(1.0+ct*ct),vec3(1.5)); vec3 c=Lin*0.5;\\n'+
  ' if(d.y>0.0){ vec2 cu=d.xz/(d.y*0.55)*0.2+t*0.00002; float n=clamp(fbm(cu*1000.0*0.001,t*0.006)*0.7+0.5,0.0,1.0); float reg=nz(cu*0.3)*0.37+0.5; float cov=clamp(0.5+(reg-0.5)*0.6,0.0,1.0);\\n'+
  '  float th=1.0-cov; float m=smoothstep(th,th+0.3,n); float dep=max(0.0,n-th); float be=exp(-4.0*dep); float sh=mix(0.45,1.0,clamp(be*(1.0-be*be)*2.6,0.0,1.0));\\n'+
  '  float sil=clamp(0.51/pow(1.49-ct*1.4,1.5),0.0,3.0); vec3 cc=vec3(0.8)*sh+vec3(1.0)*sil*m*(1.0-m)*2.4; float a=(1.0-exp(-dep*0.4*12.0)); c=mix(c,mix(c,cc,Fex),a); }\\n'+
  ' o=vec4(c,1); }',
 raymarch_fullscreen: HEAD+ATM+'void main(){ vec3 d=dirOf(uv); o=vec4(march(d,30,8),1); }',
 lut_build: HEAD+ATM+'void main(){ vec3 d=dirOf(uv); o=vec4(march(d,30,8),1); }',
 lut_build_mobile: HEAD+ATM+'void main(){ vec3 d=dirOf(uv); o=vec4(march(d,8,8),1); }',
 lut_sample: HEAD+'void main(){ o=vec4(texture(lut,uv).rgb,1); }'
};
const RAIN_VS='#version 300 es\\nuniform float t; uniform float n; out float a; void main(){ int id=gl_InstanceID; float fi=float(id);\\n'+
 ' vec3 seed=fract(vec3(fi*0.1031,fi*0.1030,fi*0.0973)*vec3(1.0,1.7,2.3)); vec3 p=seed*2.0-1.0; p.y=fract(seed.y-t*0.9)*2.0-1.0;\\n'+
 ' vec2 corner=vec2(float(gl_VertexID&1)*0.002,float((gl_VertexID>>1)&1)*0.06); gl_Position=vec4(p.xy+corner,0.5,1.0); a=0.25; }';
const RAIN_FS='#version 300 es\\nprecision mediump float; in float a; out vec4 o; void main(){ o=vec4(0.8,0.85,0.9,a); }';
function run(W,H){
  const cv=document.getElementById('c'); cv.width=W; cv.height=H; const gl=cv.getContext('webgl2',{antialias:false,preserveDrawingBuffer:false});
  if(!gl) return {error:'no webgl2'};
  const info={renderer:gl.getParameter(gl.RENDERER),vendor:gl.getParameter(gl.VENDOR)};
  const dbg=gl.getExtension('WEBGL_debug_renderer_info'); if(dbg) info.unmasked=gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL);
  function prog(vs,fs){ const p=gl.createProgram(); [[gl.VERTEX_SHADER,vs],[gl.FRAGMENT_SHADER,fs]].forEach(([k,s])=>{const sh=gl.createShader(k); gl.shaderSource(sh,s); gl.compileShader(sh); if(!gl.getShaderParameter(sh,gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh)); gl.attachShader(p,sh);}); gl.linkProgram(p); if(!gl.getProgramParameter(p,gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p)); return p; }
  const px=new Uint8Array(4); function sync(){ gl.readPixels(0,0,1,1,gl.RGBA,gl.UNSIGNED_BYTE,px); }
  function time(draw,frames){ draw(0); sync(); const t0=performance.now(); for(let f=1;f<=frames;f++){ draw(f); } sync(); return (performance.now()-t0)/frames; }
  const sunDir=[0.3,0.25,0.2]; const l=Math.hypot(...sunDir); sunDir.forEach((v,i)=>sunDir[i]=v/l);
  function full(name){ const p=prog(VS,FS[name]); return (f)=>{ gl.useProgram(p); gl.uniform1f(gl.getUniformLocation(p,'t'),f*16.7); gl.uniform3fv(gl.getUniformLocation(p,'sun'),sunDir); gl.drawArrays(gl.TRIANGLES,0,3); }; }
  const out={W,H,info,ms:{}}; const FR=20;
  gl.viewport(0,0,W,H);
  for(const k of ['gradient','analytic_clouds','raymarch_fullscreen']){ out.ms[k]=+time(full(k),k==='raymarch_fullscreen'?4:FR).toFixed(3); }
  // LUT: build into a small texture, then sample it full screen
  function lutCase(lw,lh,name){ const tex=gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D,tex); gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,lw,lh,0,gl.RGBA,gl.UNSIGNED_BYTE,null);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
    const fb=gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER,fb); gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,tex,0); gl.bindFramebuffer(gl.FRAMEBUFFER,null);
    const b=full(name), s=full('lut_sample');
    const build=(f)=>{ gl.bindFramebuffer(gl.FRAMEBUFFER,fb); gl.viewport(0,0,lw,lh); b(f); gl.bindFramebuffer(gl.FRAMEBUFFER,null); gl.viewport(0,0,W,H); };
    const tb=time(build,FR); const ts=time((f)=>{ gl.bindTexture(gl.TEXTURE_2D,tex); s(f); },FR);
    return {build_ms:+tb.toFixed(3),sample_ms:+ts.toFixed(3)}; }
  out.ms.lut_200x100=lutCase(200,100,'lut_build');
  out.ms.lut_96x50_mobile_steps=lutCase(96,50,'lut_build_mobile');
  // rain: N instanced streaks, alpha blended
  const rp=prog(RAIN_VS,RAIN_FS); gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  for(const N of [2000,10000,40000]){ out.ms['rain_'+N]=+time((f)=>{ gl.useProgram(rp); gl.uniform1f(gl.getUniformLocation(rp,'t'),f*0.016); gl.drawArraysInstanced(gl.TRIANGLE_STRIP,0,4,N); },FR).toFixed(3); }
  gl.disable(gl.BLEND);
  return out;
}
</script>`;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(PAGE);
  const out = { when: new Date().toISOString(), browser: browser.version(), note: 'SwiftShader software rendering on this machine; ranks techniques only, not a phone or GPU', runs: [] };
  for (const [W, H] of [[390, 844], [1280, 720]]) {
    for (let r = 0; r < 3; r++) out.runs.push(Object.assign({ run: r + 1 }, await page.evaluate(([w, h]) => run(w, h), [W, H])));
  }
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})();
