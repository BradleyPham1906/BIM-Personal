import { A3D } from '../core/state.js';
import { LIGHT } from '../core/mesh-primitives.js';
import { bimSunDayText, bimSunNow } from '../site/sun-position.js';
import { bimTerrainTin } from '../terrain/terrain-tin.js';
import { bimTerrainSuperseded } from '../terrain/grading.js';
import { bimLayerShown } from '../layers/layer-rules.js';
import { bimAwCtxCol } from '../site-analysis/analysis-workspace.js';
import { bimGlProjMatrix, bimHexToRgb } from './webgl.js';
import { bimSkCol } from './surface-kinds.js';
import { bimSceneSync } from './gpu-batches.js';
import { bimSunVector } from '../site/shadows.js';


  /* ================= __acad3dV194: the rendered view, its scene =================
     docs/research/research-rendered-view.md. What the rendered view draws, as plain numbers, with nothing of three.js
     here, so Node tests it. The model is V152's description (bimSceneSync: chunks of merged triangles and a table of
     each object's place, colour and transparency), read a third time, so a layer turned off, a level hidden, a colour
     lens and a section cut are in the picture as they are in the shaded view; the terrain's triangles are added, which
     that description does not carry. The camera is the view's own two matrices, so the picture lies exactly under the
     overlay and a click lands where it did. The sun is the site's (V171d), the moment studied or the clock's while it
     plays; where the site has no place yet, the shaded view's own light. */
  var BIM_RV_SEQ=0;
  var BIM_RV_SEL=[null,[0.306,0.631,1.0],[1.0,0.706,0.329]];   /* the shaded view's two selection colours */
  function bimRvLin(c){return c<=0.04045?c/12.92:Math.pow((c+0.055)/1.055,2.4);}
  /* a table row's colour as the picture takes it: linear, a selected object's drawn toward its selection colour */
  function bimRvRowColour(d,o){
    var r=d[o+4],g=d[o+5],b=d[o+6],s=BIM_RV_SEL[d[o+7]]||null;
    if(s){r=r*0.55+s[0]*0.45;g=g*0.55+s[1]*0.45;b=b*0.55+s[2]*0.45;}
    return [bimRvLin(r),bimRvLin(g),bimRvLin(b)];
  }
  /* what a chunk looks like now, in a few characters: its triangles' version and every row of its objects */
  function bimRvChunkSig(B,c){
    var d=B.data,h=0,i,o,k;
    for(i=0;i<c.ids.length;i++){o=B.slots[c.ids[i]]*8;for(k=0;k<8;k++)h=(h*31+Math.round(d[o+k]*1000))|0;
      if(B.roof&&B.roof.hasOwnProperty(c.ids[i])){o=B.roof[c.ids[i]]*8;for(k=0;k<8;k++)h=(h*31+Math.round(d[o+k]*1000))|0;}}   /* __acad3dV197 */
    return c.ver+':'+c.ids.length+':'+h;
  }
  /* a chunk's triangles for the picture: world positions and linear colours, the opaque ones and the see-through
     ones (with their transparency) apart, the hidden ones left out; its edges when asked */
  function bimRvChunkArrays(B,c,edges){
    var d=B.data,tri=c.tri,n=c.count||0,i,p,o,a,no=0,nt=0,ne=0,lin={},L,k,q,s;
    for(i=0;i<n;i++){a=d[tri[i*7+6]*8+3];if(a<0)continue;if(a<0.999)nt++;else no++;}
    var op={pos:new Float32Array(no*3),col:new Float32Array(no*3),n:no},tr={pos:new Float32Array(nt*3),col:new Float32Array(nt*4),n:nt},io=0,it=0,ed=null;
    for(i=0;i<n;i++){
      p=i*7;s=tri[p+6];o=s*8;a=d[o+3];
      if(a<0)continue;
      L=lin[s]||(lin[s]=bimRvRowColour(d,o));
      if(a<0.999){
        k=it*3;q=it*4;it++;
        tr.pos[k]=tri[p]+d[o];tr.pos[k+1]=tri[p+1]+d[o+1];tr.pos[k+2]=tri[p+2]+d[o+2];
        tr.col[q]=L[0];tr.col[q+1]=L[1];tr.col[q+2]=L[2];tr.col[q+3]=a;
      }else{
        k=io*3;io++;
        op.pos[k]=tri[p]+d[o];op.pos[k+1]=tri[p+1]+d[o+1];op.pos[k+2]=tri[p+2]+d[o+2];
        op.col[k]=L[0];op.col[k+1]=L[1];op.col[k+2]=L[2];
      }
    }
    if(edges&&c.ed&&c.ecount){
      for(i=0;i<c.ecount;i++)if(d[c.ed[i*4+3]*8+3]>=0)ne++;
      ed={pos:new Float32Array(ne*3),n:ne};k=0;
      for(i=0;i<c.ecount;i++){
        p=i*4;o=c.ed[p+3]*8;
        if(d[o+3]<0)continue;
        ed.pos[k]=c.ed[p]+d[o];ed.pos[k+1]=c.ed[p+1]+d[o+1];ed.pos[k+2]=c.ed[p+2]+d[o+2];k+=3;
      }
    }
    return {op:op,tr:tr,ed:ed};
  }
  /* a terrain's surface for the picture: its triangles as the 3D view drapes them, in its colour */
  function bimRvTerrainItem(o){
    var tin=bimTerrainTin(o),i,h=0,sel,hx,box;
    if(!tin||!tin.tris||!tin.tris.length)return null;
    if(!tin.tris.__rv)tin.tris.__rv=++BIM_RV_SEQ;   /* the cached triangles' own number: new when they are rebuilt */
    box=[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity];
    for(i=0;i<tin.H.length;i++){
      h=(h*31+Math.round(tin.H[i]*1000)+Math.round(tin.P[i][0]*1000)*7+Math.round(tin.P[i][1]*1000)*13)|0;
      if(tin.P[i][0]<box[0])box[0]=tin.P[i][0];if(tin.H[i]<box[1])box[1]=tin.H[i];if(tin.P[i][1]<box[2])box[2]=tin.P[i][1];
      if(tin.P[i][0]>box[3])box[3]=tin.P[i][0];if(tin.H[i]>box[4])box[4]=tin.H[i];if(tin.P[i][1]>box[5])box[5]=tin.P[i][1];
    }
    sel=(o.id===A3D.sel||(A3D.selSet&&A3D.selSet.indexOf(o.id)>=0));
    hx=sel?'#4ea1ff':(bimAwCtxCol(o)||bimSkCol(o)||o.col||'#b08559');   /* __acad3dV197 */
    return {key:'t'+o.id,sig:tin.tris.__rv+':'+tin.H.length+':'+h+':'+hx,terrain:tin,col:hx,box:box};
  }
  function bimRvTerrainArrays(it){
    var tin=it.terrain,T=tin.tris,n=T.length*3,pos=new Float32Array(n*3),col=new Float32Array(n*3),c=bimHexToRgb(it.col),
      L=[bimRvLin(c[0]),bimRvLin(c[1]),bimRvLin(c[2])],i,j,v,k=0;
    for(i=0;i<T.length;i++)for(j=0;j<3;j++){
      v=T[i][j];
      pos[k]=tin.P[v][0];pos[k+1]=tin.H[v];pos[k+2]=tin.P[v][1];
      col[k]=L[0];col[k+1]=L[1];col[k+2]=L[2];k+=3;
    }
    return {op:{pos:pos,col:col,n:n},tr:null,ed:null};
  }
  function bimRvBoxAdd(b,x){
    if(!x||!(x[0]<=x[3]))return b;
    if(!b)return [x[0],x[1],x[2],x[3],x[4],x[5]];
    if(x[0]<b[0])b[0]=x[0];if(x[1]<b[1])b[1]=x[1];if(x[2]<b[2])b[2]=x[2];
    if(x[3]>b[3])b[3]=x[3];if(x[4]>b[4])b[4]=x[4];if(x[5]>b[5])b[5]=x[5];
    return b;
  }
  /* the frame's part: the description brought up to date, and what the picture is made of: a part for each chunk and
     each terrain shown, each with a key and its look in a few characters, the box of them all, the faces */
  function bimRvPlan(edges){
    var F=bimSceneSync(),B=F.S,items=[],box=null,i,c,o,t,nt=0;
    for(i=0;i<B.chunks.length;i++){
      c=B.chunks[i];
      if(!c.rv)c.rv=++BIM_RV_SEQ;
      items.push({key:'c'+c.rv,sig:bimRvChunkSig(B,c)+(edges?':e':''),chunk:c});
      if(c.wb&&c.wb.f===B.frame)box=bimRvBoxAdd(box,c.wb);
    }
    for(i=0;i<A3D.objs.length;i++){
      o=A3D.objs[i];
      if(o.t!=='terrain'||!o.survey||!bimLayerShown(o)||bimTerrainSuperseded(o))continue;
      t=bimRvTerrainItem(o);
      if(t){items.push(t);box=bimRvBoxAdd(box,t.box);nt++;}
    }
    return {S:B,items:items,box:box,totalFaces:F.totalFaces,terrains:nt,edges:!!edges};
  }
  /* the arrays of one of the plan's parts, asked for only when the part is new or looks different */
  function bimRvBuild(plan,it){
    if(it.chunk)return bimRvChunkArrays(plan.S,it.chunk,plan.edges);
    if(it.terrain)return bimRvTerrainArrays(it);
    return null;
  }
  /* the view's camera as the picture takes it: camera to world (its right, up and back, then the eye) and the
     projection the shaded view uses, both column-major */
  function bimRvCamera(V,W,H,flat,dist){
    var r=V.r,u=V.u,d=V.d,e=V.eye,P=bimGlProjMatrix(W,H,flat,dist),p=[],i;
    for(i=0;i<16;i++)p.push(P[i]);
    return {world:[r[0],r[1],r[2],0,u[0],u[1],u[2],0,d[0],d[1],d[2],0,e[0],e[1],e[2],1],proj:p};
  }
  /* how far around what the camera looks at the shadows are kept sharp: the view's own width at that distance, never
     more than the model's size */
  function bimRvReach(dist,box){
    var r=Math.max(2,dist*0.6),m;
    if(box){m=Math.sqrt((box[3]-box[0])*(box[3]-box[0])+(box[4]-box[1])*(box[4]-box[1])+(box[5]-box[2])*(box[5]-box[2]))/2*1.2;if(m>2&&m<r)r=m;}
    return r;
  }
  /* the sun the picture is lit by: the site's at the moment studied, toward it; or the shaded view's light where the
     site has no place */
  function bimRvSun(){
    var s=null,v,st;
    try{s=bimSunNow();}catch(eS){console.warn('[BIM] Rendered view: the sun could not be worked out',eS);s=null;}
    if(!s||s.missing)return {dir:[LIGHT[0],LIGHT[1],LIGHT[2]],up:true,site:false,elev:null,text:'the shaded view\'s light: the site has no place yet (Properties, Site, Location)'};
    v=bimSunVector(s);st=s.settings||{};
    return {dir:v,up:v[1]>0.02,site:true,elev:s.elevation,
      text:(s.elevation>0?'the sun at '+st.time+' on '+bimSunDayText(st.date)+', altitude '+s.elevation.toFixed(1)+' deg':'night: the sun is down at '+st.time+' on '+bimSunDayText(st.date))};
  }
export {
  bimRvBoxAdd, bimRvBuild, bimRvCamera, bimRvChunkArrays, bimRvChunkSig, bimRvLin, bimRvPlan, bimRvReach,
  bimRvRowColour, bimRvSun, bimRvTerrainArrays, bimRvTerrainItem
};
