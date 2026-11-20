'use strict';
(async()=>{
const response=await fetch('results.json');if(!response.ok)throw Error('Snapshot not available');const r=await response.json();
const q=s=>document.querySelector(s), n=(x,d=3)=>Number(x).toLocaleString('en-IN',{minimumFractionDigits:d,maximumFractionDigits:d});
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const p=r.parameters,a=r.analysis;
const initial=r.provenance.source_mode==='initial_google_read_snapshot';
q('#source-state').textContent=(initial?'Initial Google Docs / Sheets snapshot read ':'Google Docs / Sheets snapshot read ')+new Date(r.provenance.read_at).toLocaleString('en-GB',{timeZone:'Asia/Kathmandu'})+' (Nepal). '+(initial?'Unattended Actions refresh is awaiting its Google credential setup.':'Both native exports were read twice and matched. This page changes after a successful refresh and deployment.');
const metrics=(id,items)=>q(id).innerHTML=items.map(([v,l])=>`<div class="metric"><strong>${esc(v)}</strong><span>${esc(l)}</span></div>`).join('');
metrics('#geometry-metrics',[[n(p.span_x,1)+' × '+n(p.span_y,1)+' m','Column-centre grid'],[n(p.column_height,1)+' m','Idealized column height'],['4 / 4 / 1','Columns / beams / slab']]);
metrics('#structure-metrics',[[n(a.total_load_kN)+' kN','Total gravity including columns'],[n(a.base_reaction_each_kN)+' kN','Reaction at each base'],[n(Math.max(a.x.joint_residual_kNm,a.y.joint_residual_kNm),9)+' kNm','Largest residual roof-joint moment']]);
const rows=[['Slab tributary area per beam','tributary_area_m2','m²'],['Slab area load','slab_load_kPa','kN/m²'],['Fixed-end moment magnitude','fixed_end_magnitude_kNm','kNm'],['Final end hogging magnitude','independent_hogging_kNm','kNm'],['Midspan sagging','midspan_sagging_kNm','kNm'],['Reaction per beam end','reaction_kN','kN'],['Moment-distribution sweeps','iterations','']];
q('#structure-table').innerHTML=rows.map(([label,k,u])=>`<tr><td>${label}</td><td>${n(a.x[k],k==='iterations'?0:4)}</td><td>${n(a.y[k],k==='iterations'?0:4)}</td><td>${u}</td></tr>`).join('');
q('#schedule-note').textContent=`${r.schedule.origin_date} to ${r.schedule.finish_date}. One crew: ${p.skilled_workers} skilled + ${p.helpers} helpers, ${p.shift_hours} hours per workday. ${r.schedule.native_kernel_verified?'The pinned native CPM kernel independently verified the sequence.':'The dated snapshot uses the verified calendar adapter; the native CPM verification runs in the experiment CI.'}`;
q('#schedule-table').innerHTML=r.schedule.activities.map(t=>`<tr><td>${esc(t.name)}</td><td>${t.elements.map(esc).join(', ')}</td><td>${t.active_duration} ${t.duration_basis==='calendar'?'calendar days':'workdays'}</td><td>${t.start}</td><td>${t.finish}</td></tr>`).join('');
q('#gantt').innerHTML=r.schedule.activities.map(t=>`<div class="gantt-row"><span>${esc(t.name)}</span><div class="track"><div title="${esc(t.start+' – '+t.finish)}" class="bar ${t.duration_basis==='calendar'?'wait':''}" style="left:${100*t.es/r.schedule.elapsed_days}%;width:${100*(t.ef-t.es)/r.schedule.elapsed_days}%"></div></div></div>`).join('');
metrics('#cost-metrics',[[n(r.concrete_m3)+' m³','Non-overlapping concrete volume'],['NPR '+n(r.concrete_subtotal_npr,0),'Concrete-only subtotal'],['Not calculated','Full building cost']]);
q('#cost-table').innerHTML=r.quantities.map(t=>`<tr><td>${esc(t.element)}</td><td>${n(t.quantity)}</td><td>${n(t.rate,0)}</td><td>${n(t.amount,0)}</td></tr>`).join('')+`<tr class="total"><td>Concrete subtotal</td><td>${n(r.concrete_m3)}</td><td></td><td>${n(r.concrete_subtotal_npr,0)}</td></tr>`;
q('#reuse-table').innerHTML=r.peer_methods.map(t=>`<tr><td><a href="https://github.com/${esc(t.repository)}/blob/${t.commit}/${t.contract}">${esc(t.workflow)}</a></td><td>${esc(t.reuse)}</td><td>${esc(t.runtime)}</td></tr>`).join('');
let view='iso';const svg=q('#building');
const scale=380/(p.span_x+p.span_y),planScale=Math.min(450/p.span_x,350/p.span_y);
const P=(x,y,z)=>view==='iso'?[345+(x-y)*scale,280+(x+y)*scale*.45-z*195/p.column_height]:[125+x*planScale,65+y*planScale];
const point=(x,y,z)=>P(x,y,z).join(',');
function draw(){
 let s='<title id="drawing-title">Four columns, four perimeter beams and one slab</title>';
 const corners=[[0,0],[p.span_x,0],[p.span_x,p.span_y],[0,p.span_y]];
 if(view==='iso'){
  s+=`<polygon points="${corners.map(([x,y])=>point(x,y,0)).join(' ')}" fill="#dfe9ee" stroke="#c3d2d9"/>`;
  for(const c of r.columns){const [x,y]=P(c.x,c.y,0),[xx,yy]=P(c.x,c.y,c.z1);s+=`<line data-element="${c.id}" tabindex="0" aria-label="Inspect ${c.id}" x1="${x}" y1="${y}" x2="${xx}" y2="${yy}" stroke="#50788e" stroke-width="14"/><text x="${x+12}" y="${y-6}" fill="#375867" font-size="15">${c.id}</text>`;}
 }
 const slabPts=corners.map(([x,y])=>point(x,y,p.column_height));s+=`<polygon data-element="S1" tabindex="0" aria-label="Inspect slab S1" points="${slabPts.join(' ')}" fill="#c3eee7" fill-opacity=".65" stroke="#0b9287" stroke-width="2"/>`;
 for(const b of r.beams){const c=r.columns.find(x=>x.id===b.start_column),d=r.columns.find(x=>x.id===b.end_column);const [x,y]=P(c.x,c.y,p.column_height),[xx,yy]=P(d.x,d.y,p.column_height);s+=`<line data-element="${b.id}" tabindex="0" aria-label="Inspect ${b.id}" x1="${x}" y1="${y}" x2="${xx}" y2="${yy}" stroke="#008c83" stroke-width="11"/><text x="${(x+xx)/2+9}" y="${(y+yy)/2-13}" fill="#00695f" font-size="15" font-weight="bold">${b.id}</text>`;}
 for(const c of r.columns){const [x,y]=P(c.x,c.y,p.column_height);s+=`<rect data-element="${c.id}" tabindex="0" aria-label="Inspect ${c.id}" x="${x-9}" y="${y-9}" width="18" height="18" rx="2" fill="#183f54"/>`;if(view==='plan')s+=`<text x="${x-28}" y="${y-18}" font-size="15" fill="#183f54">${c.id} · ${c.grid}</text>`;}
 const [cx,cy]=P(p.span_x/2,p.span_y/2,p.column_height);s+=`<text x="${cx}" y="${cy}" text-anchor="middle" fill="#006c63" font-size="21" font-weight="bold" pointer-events="none">S1</text><text x="${cx}" y="${cy+25}" text-anchor="middle" fill="#3c776f" font-size="15" pointer-events="none">${n(p.span_x,1)} × ${n(p.span_y,1)} m</text>`;
 svg.innerHTML=s;
 svg.querySelectorAll('[data-element]').forEach(el=>{el.addEventListener('click',()=>select(el.dataset.element));el.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();select(el.dataset.element);}});});
}
function select(id){let title,fields;if(id==='S1'){title='Slab S1';fields=[['Plan area',n(r.slab.area_m2)+' m²'],['Thickness',n(p.slab_thickness)+' m'],['Concrete',n(r.quantities[2].quantity)+' m³']];}else if(id.startsWith('C')){const c=r.columns.find(x=>x.id===id);title='Column '+id+' · '+c.grid;fields=[['Location',`${c.x}, ${c.y} m`],['Height',n(c.z1)+' m'],['Section',n(p.column_width)+' m square'],['Concrete',n(r.quantities[0].quantity/4)+' m³']];}else{const b=r.beams.find(x=>x.id===id);title='Beam '+id;fields=[['Joins',b.start_column+' / '+b.end_column],['Centre span',n(b.result.span_m)+' m'],['Clear length',n(b.result.clear_length_m)+' m'],['Concrete downstand',n(b.result.beam_downstand_m3)+' m³']];}q('#selection h3').textContent=title;q('#element-details').innerHTML='<dl>'+fields.map(([l,v])=>`<dt>${esc(l)}</dt><dd>${esc(v)}</dd>`).join('')+'</dl>';}
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{view=b.dataset.view;document.querySelectorAll('[data-view]').forEach(x=>x.classList.toggle('active',x===b));draw();}));
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-tab]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});document.querySelectorAll('.panel').forEach(x=>x.hidden=x.id!==b.dataset.tab);}));
draw();select('S1');
})().catch(error=>{document.querySelector('#source-state').textContent='This snapshot could not be loaded. Open the source data or retry the page.';console.error(error);});
