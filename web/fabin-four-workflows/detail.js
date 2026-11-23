import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

// Engineering interpretation of the EXISTING one-bay synthetic snapshot.
// Layouts are illustrations, never bar-bending schedules or code certification.
const stage=document.getElementById('three-stage');
const state=document.getElementById('render-state');
const title=document.getElementById('member-title');
const metrics=document.getElementById('member-metrics');
const source=document.getElementById('member-steel');
const description=document.getElementById('member-description');
const memberNames={beam:'Beam B1–B4',column:'Column C1–C4',slab:'Slab S1'};
const views={'3d':'3D',elevation:'Elevation',plan:'Top / plan',section:'Section'};
let member='beam',view='3d',layout='recorded',model,renderer,scene,controls,perspective,ortho,activeCamera;
const origin=new THREE.Vector3(),axis=new THREE.Vector3(0,1,0);
const steel=new THREE.MeshStandardMaterial({color:0xc77926,roughness:.35,metalness:.25});
const linkSteel=new THREE.MeshStandardMaterial({color:0x168471,roughness:.55});
const concrete=new THREE.MeshStandardMaterial({color:0xb1c6d1,transparent:true,opacity:.22,depthWrite:false,side:THREE.DoubleSide});
const lineMat=new THREE.LineBasicMaterial({color:0x4c6877});
const labelNum=(x,n=3)=>Number(x).toFixed(n).replace('-', '−');
let group=new THREE.Group();

function cylinder(a,b,diameter,material=steel) {
  const start=new THREE.Vector3(...a),end=new THREE.Vector3(...b);
  const delta=new THREE.Vector3().subVectors(end,start),length=delta.length();
  const mesh=new THREE.Mesh(new THREE.CylinderGeometry(diameter/2,diameter/2,length,10),material);
  mesh.position.copy(start).add(end).multiplyScalar(.5);
  mesh.quaternion.setFromUnitVectors(axis,delta.normalize());
  group.add(mesh);
}
function outline(points,diameter=.008,material=linkSteel) {
 for(let i=0;i<points.length;i++)cylinder(points[i],points[(i+1)%points.length],diameter,material);
}
function block(width,height,depth) {
 const box=new THREE.Mesh(new THREE.BoxGeometry(width,height,depth),concrete);
 group.add(box);
 const edges=new THREE.LineSegments(new THREE.EdgesGeometry(box.geometry),lineMat);
 edges.material.transparent=true;edges.material.opacity=.35;group.add(edges);
}
function displacementCurve(points,colour){
 const geom=new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p)));
 group.add(new THREE.Line(geom,new THREE.LineBasicMaterial({color:colour,linewidth:2})));
}
function sphere(p,r=.008,material=steel){
 const mesh=new THREE.Mesh(new THREE.SphereGeometry(r,12,8),material);mesh.position.set(...p);group.add(mesh);
}
const positions=(n,a,b)=>Array.from({length:n},(_,i)=>a+(b-a)*i/Math.max(1,n-1));
const banded=(len,end=.70)=> {
 const p=[];
 for(let x=.05;x<len-.05;x+= x<end || x>len-end ? .10 : .16)p.push(x);
 return p;
};
function hoopBeam(x,w,h,cover,withHook) {
 const y=h/2-cover,z=w/2-cover;
 outline([[x,-y,-z],[x,y,-z],[x,y,z],[x,-y,z]],.008);
 if(withHook) {
   // Schematic inward return, not a calculated 135-degree hook length.
   cylinder([x,y,z],[x,y-.045,z-.04],.008,linkSteel);
   cylinder([x,-y,-z],[x,-y+.045,-z+.04],.008,linkSteel);
 }
}
function drawBeam(isSection) {
 const len=isSection ? 0.12 : 3.70,w=model.dimensions.beam_width,h=model.dimensions.beam_depth;
 const cover=.03;
 block(len,h,w);
 const y=h/2-cover-.012,z=w/2-cover-.012;
 if(isSection) {
  for(const iy of [-1,1])for(const iz of [-1,1])sphere([.066,iy*y,iz*z],.013);
  hoopBeam(.02,w,h,cover,true);
 }else{
  for(const iy of [-1,1])for(const iz of [-1,1])
    cylinder([-len/2+.03,iy*y,iz*z],[len/2-.03,iy*y,iz*z],.016);
  const xs=layout==='recorded' ? positions(20,-len/2+.05,len/2-.05)
    : banded(len).map(x=>x-len/2);
  xs.forEach(x=>hoopBeam(x,w,h,cover,layout==='concept'));
  // Relative-chord beam bending, exaggerated 1,400-fold for visibility.
  const profile=model.samples.map(p=>[(p.x/model.dimensions.span_x-.5)*len,p.deflection_mm*1400/1000,w/2+.055]);
  displacementCurve(profile,0x94398e);
 }
}
function hoopColumn(y,w,cover,withHook) {
 const v=w/2-cover;
 outline([[-v,y,-v],[v,y,-v],[v,y,v],[-v,y,v]],.008);
 if(withHook){cylinder([v,y,v],[v-.045,y,v-.045],.008,linkSteel)}
}
function drawColumn(isSection){
 const h=isSection ? 0.12 : model.dimensions.height,w=model.dimensions.column;
 const cover=.035, a=w/2-cover-.012;
 block(w,h,w);
 if(isSection){
   for(const x of [-a,a])for(const z of [-a,a])sphere([x,.075,z],.013);
   hoopColumn(.015,w,cover,true);
 }else{
   for(const x of [-a,a])for(const z of [-a,a])
     cylinder([x,-h/2+.04,z],[x,h/2-.04,z],.016);
   const ys=layout==='recorded'?positions(16,-h/2+.10,h/2-.10)
    : banded(h,.62).map(v=>v-h/2);
   ys.forEach(y=>hoopColumn(y,w,cover,layout==='concept'));
   // Per-plane bending under zero roof translation, not overall drift.
   if(model.column_flexure){
    const points=model.column_flexure.samples.map(p=>[p.relative_flexure_mm*2500/1000,p.z_m-h/2,w/2+.05]);
    displacementCurve(points,0xc26920);
   }
 }
}
function drawSlab(isSection){
 const L=model.dimensions.span_x, W=model.dimensions.span_y, t=model.dimensions.slab;
 if(isSection){
   block(L,t,.10);
   // Section parallel to X: selected X bar is a longitudinal line;
   // orthogonal Y bars intersect the cut as individual circular sections.
   cylinder([-L/2+.02,.018,.055],[L/2-.02,.018,.055],.010,steel);
   for(const x of positions(21,-L/2+.025,L/2-.025))sphere([x,-.018,.057],.006,linkSteel);
 }else{
   block(L,t,W);
   const nX=model.rebar.groups.find(x=>x.mark==='Slab X').pieces_per_member;
   const nY=model.rebar.groups.find(x=>x.mark==='Slab Y').pieces_per_member;
   positions(nX,-W/2+.02,W/2-.02).forEach(z=>
      cylinder([-L/2+.02,-.018,z],[L/2-.02,-.018,z],.010,steel));
   positions(nY,-L/2+.02,L/2-.02).forEach(x=>
      cylinder([x,+.018,-W/2+.02],[x,+.018,W/2-.02],.010,linkSteel));
 }
}
function drawShape(){
 scene.remove(group);group=new THREE.Group();scene.add(group);
 if(member==='beam')drawBeam(view==='section');
 if(member==='column')drawColumn(view==='section');
 if(member==='slab')drawSlab(view==='section');
 setCamera();
}
function setCamera(){
 const span=view==='section' && member!=='slab' ? .68 : member==='column' ? 3.4 : member==='beam' ? 4.2 : 5.2;
 const aspect=Math.max(.7,stage.clientWidth/Math.max(1,stage.clientHeight));
 ortho.left=-span*aspect/2;ortho.right=span*aspect/2;
 ortho.top=span/2;ortho.bottom=-span/2;ortho.updateProjectionMatrix();
 perspective.aspect=aspect;perspective.updateProjectionMatrix();
 activeCamera=view==='3d'?perspective:ortho;
 controls.object=activeCamera;
 controls.target.copy(origin);controls.enableRotate=view==='3d';
 controls.enablePan=view==='3d';
 controls.enableZoom=true;
 activeCamera.up.set(0,1,0);
 // Frame the member more closely in perspective. Orthographic measurements
 // and all displacement/steel geometry remain untouched.
 const dist=view==='3d' ? Math.max(3.1,span*1.15) : Math.max(4,span*1.9);
 if(view==='3d') activeCamera.position.set(dist*.75,dist*.65,dist*.9);
 if(view==='elevation')activeCamera.position.set(0,0,dist);
 if(view==='plan'){activeCamera.up.set(0,0,-1);activeCamera.position.set(0,dist,0)}
 if(view==='section'){
   if(member==='column'){activeCamera.up.set(0,0,-1);activeCamera.position.set(0,dist,0)}
   else if(member==='slab')activeCamera.position.set(0,0,dist);
   else activeCamera.position.set(dist,0,0);
 }
 activeCamera.lookAt(origin);controls.update();
}
function metric(name,value){
 const card=document.createElement('div'),k=document.createElement('span'),v=document.createElement('strong');
 card.className='detail-metric';k.textContent=name;v.textContent=value;
 card.append(k,v);metrics.append(card);
}
function showResults(){
 title.textContent=memberNames[member]+' — '+views[view];
 metrics.replaceChildren();
 const a=model.actions,cf=model.column_flexure,mid=model.samples[20];
 if(member==='beam'){
  metric('Beam section','250 × 450 mm');metric('Centreline span','4.00 m');
  metric('Midspan moment','+'+labelNum(mid.moment)+' kN·m');
  metric('Chord-relative sag',labelNum(mid.deflection_mm,5)+' mm');
  description.textContent='Four perimeter beams have identical symmetric gravity results. The purple deflection curve is magnified 1,400-fold. The calculated beam line is relative to its end chord and is not total storey displacement.';
  source.textContent='Original illustrative takeoff: 4 longitudinal Ø16 bars and 20 Ø8 links per beam. Two top and two bottom bars are placed inside closed stirrups in this view.';
 } else if(member==='column'){
  metric('Column section','300 × 300 mm');metric('Height','3.00 m');
  metric('Base axial',labelNum(a.axial_base,4)+' kN');
  metric('Peak in-plane flexure',cf?labelNum(cf.peak_chord_relative_mm,5)+' mm':'Unavailable');
  metric('Peak height',cf?labelNum(cf.peak_z_m,2)+' m':'Unavailable');
  metric('Roof sway / translation','0 in assumed no-sway model');
  description.textContent='The derived curve is bending displacement relative to the fixed-end chord in EACH separate planar frame. The orange bending curve is magnified 2,500-fold and peaks 2.00 m above the base; no overall drift, global joint movement or column shortening was analysed.';
  source.textContent='Original illustrative takeoff: 4 vertical Ø16 bars and 16 Ø8 closed ties per column. End-region tie spacing and joint confinement require a separate design verification.';
 } else {
  metric('Slab panel','4.00 × 4.00 m');metric('Thickness','150 mm');
  metric('Recorded mat','Ø10, 21 bars each way');
  metric('Slab deflection','Not analysed');
  description.textContent='S1 is a tributary gravity-load panel, not a finite-element slab. Two orthogonal single-mat bar directions are offset slightly in the graphic so both remain visible.';
  source.textContent='Original illustrative takeoff: 21 bars × Ø10 in X, 21 bars × Ø10 in Y. This is not a top-and-bottom reinforcement design and cannot establish crack control, development lengths or capacity.';
 }
 if(layout==='concept'){
  const extra=document.createElement('p');
  extra.textContent='The displayed closer confinement/end-zone detailing is a geometric concept only: bar counts and mass differ from the recorded takeoff. Spacing, 135° hooks, joint steel and anchorage require an NBC design check.';
  source.append(extra);
 } else {
  const extra=document.createElement('p');
  extra.textContent='The published total illustrative steel mass is '+labelNum(model.rebar.mass_kg,2)+' kg for all members combined; this is not a design BBS.';
  source.append(extra);
 }
}
function setSelection(){
 document.querySelectorAll('[data-member]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.member===member)));
 document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
 document.querySelectorAll('[data-layout]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.layout===layout)));
 drawShape();showResults();
}
async function boot(){
 const r=await fetch('frame-results.json');
 if(!r.ok)throw Error('Frame snapshot unavailable');
 model=await r.json();
 if(!model.column_flexure)throw Error('Column flexure result missing from build');
 scene=new THREE.Scene();
 scene.background=new THREE.Color(0xe8f0f4);
 scene.add(new THREE.HemisphereLight(0xffffff,0x627986,2.2));
 const directional=new THREE.DirectionalLight(0xffffff,2.2);directional.position.set(5,8,6);scene.add(directional);
 try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:false})}
 catch(e){state.textContent='WebGL unavailable — use the frame results table';return}
 renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));
 stage.append(renderer.domElement);
 perspective=new THREE.PerspectiveCamera(42,1,.05,500);
 ortho=new THREE.OrthographicCamera(-4,4,4,-4,.01,500);
 controls=new OrbitControls(perspective,renderer.domElement);
 controls.enableDamping=true;
 const resize=()=>{
  const w=Math.max(1,stage.clientWidth),h=Math.max(1,stage.clientHeight);
  renderer.setSize(w,h,false);setCamera();
 };
 const watch=new ResizeObserver(resize);watch.observe(stage);
 document.querySelectorAll('[data-member]').forEach(b=>b.addEventListener('click',()=>{member=b.dataset.member;view='3d';setSelection()}));
 document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;setSelection()}));
 document.querySelectorAll('[data-layout]').forEach(b=>b.addEventListener('click',()=>{layout=b.dataset.layout;setSelection()}));
 resize();setSelection();
 renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,activeCamera)});
 state.textContent='Three.js active · Synthetic, not an approved design';
}
boot().catch(err=>{
 state.textContent='3D detail unavailable — the original frame viewer is still accessible';
 console.error('Member detail renderer:',err);
});
