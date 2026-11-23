'use strict';

const tabs = {
  moment: 'Bending moment',
  shear: 'Shear force',
  axial: 'Axial force',
  torsion: 'Torsion',
  movement: 'Beam & column deflection',
  rebar: 'Reinforcement',
  reactions: 'Support reactions',
};

const ink = {
  frame: '#184359', slab: '#c9f0e8', positive: '#1464a0', negative: '#a7322d',
  axial: '#682b87', steel: '#965000', mesh: '#12685d', movement: '#8b3480',
};

const titles = {
  moment: 'Bending moment along the perimeter beams',
  shear: 'Shear force along the perimeter beams',
  axial: 'Axial compression in the four corner columns',
  torsion: 'Geometry of the planar gravity idealisation',
  movement: 'Elastic beam sag and column bending (each measured relative to its end chord)',
  rebar: 'Illustrative longitudinal bars and slab reinforcement',
  reactions: 'Vertical gravity reactions at the four fixed bases',
};

const number = (value, digits = 3) =>
  (Math.abs(value) < .5 * 10 ** -digits ? 0 : value).toFixed(digits).replace('-', '−');

function spatialView(model, active) {
  const {dimensions: d, actions: a, columns, beams, samples} = model;
  const map = Object.fromEntries(columns.map(c => [c.id, c]));
  const point = (x, y, z) => [475 + (x-y) * 65, 67 + (x+y) * 26 + (d.height-z) * 59];
  const corner = (id, z) => point(map[id].x, map[id].y, z);
  const top = id => corner(id, d.height);
  const base = id => corner(id, 0);
  const along = (id1, id2, t, z) => {
    const c = map[id1], e = map[id2];
    return point(c.x + (e.x-c.x)*t, c.y + (e.y-c.y)*t, z);
  };
  const xy = vals => vals.map(x => Number(x).toFixed(2)).join(',');
  const list = points => points.map(xy).join(' ');
  const stroke = (p, q, color, width = 2, options = '') =>
    `<line x1="${p[0]}" y1="${p[1]}" x2="${q[0]}" y2="${q[1]}" stroke="${color}" stroke-width="${width}" stroke-linecap="round" ${options}/>`;
  const line = (points, color, width = 2) =>
    `<polyline points="${list(points)}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linejoin="round"/>`;
  const polygon = (points, fill, outline = 'none', opacity = 1) =>
    `<polygon points="${list(points)}" fill="${fill}" stroke="${outline}" opacity="${opacity}"/>`;
  const label = (at, text, size = 16, weight = 'bold') =>
    `<text x="${at[0]}" y="${at[1]}" text-anchor="middle" font-size="${size}" font-weight="${weight}">${text}</text>`;
  const offset = ([x,y], dx, dy) => [x+dx,y+dy];
  const slab = polygon(model.slab.corners.map(top), ink.slab, ink.mesh, .68);
  const basePlane = polygon(model.slab.corners.map(base), '#eff8fc', '#a5c3d6');
  const members = columns.map(c => stroke(base(c.id),top(c.id),ink.frame,5)).join('') +
    slab + beams.map(b => stroke(top(b.start_column),top(b.end_column),ink.frame,4)).join('');
  const beamLabel = {B1:[46,-37],B2:[42,8],B3:[-38,7],B4:[-40,-37]};
  const columnLabel = {C1:[-29,9],C2:[42,9],C3:[42,5],C4:[-42,9]};
  const identifiers = columns.map(c => label(offset(base(c.id), ...columnLabel[c.id]), c.id)).join('') +
    beams.map(b => label(offset(along(b.start_column,b.end_column,.5,d.height),...beamLabel[b.id]),b.id)).join('') +
    label(offset(point(d.span_x/2,d.span_y/2,d.height),0,5),'S1');
  let result = '';
  if (active === 'moment' || active === 'shear') {
    const scale = active === 'moment' ? 2.8 : 2.35;
    for (const b of beams) {
      const from = b.start_column, to = b.end_column;
      const datum = samples.map(s => along(from,to,s.x/d.span_x,d.height));
      const curve = samples.map((s,i) => offset(datum[i],0,-s[active]*scale));
      for (let i = 1; i < curve.length; i++) {
        const color = (samples[i-1][active]+samples[i][active]) >= 0 ? ink.positive : ink.negative;
        result += polygon([datum[i-1],datum[i],curve[i],curve[i-1]],color,'none',.22);
        result += stroke(curve[i-1],curve[i],color,2.1);
      }
      result += stroke(datum[0],curve[0],ink.frame,1);
      result += stroke(datum.at(-1),curve.at(-1),ink.frame,1);
    }
  }
  if (active === 'axial') {
    for (const c of columns) {
      const start = top(c.id), end = base(c.id);
      const side = c.x === 0 && c.y === d.span_y ? -1 : 1;
      const p = offset(start,side*a.axial_roof*.56,0);
      const q = offset(end,side*a.axial_base*.56,0);
      result += polygon([start,p,q,end],ink.axial,'none',.23) + line([start,p,q,end],ink.axial,2);
    }
  }
  if (active === 'movement') {
    const magnification = 1400;
    for (const b of beams) {
      const points = samples.map(s => along(b.start_column,b.end_column,s.x/d.span_x,
        d.height + s.deflection_mm * magnification / 1000));
      result += line(points,ink.movement,3);
    }
    // Independently integrated M/EI column bending in each planar frame.
    // The geometry is magnified; zero roof translation is an assumption.
    const cf = model.column_flexure;
    if (cf) {
      for (const c of columns) {
        const points=cf.samples.map(s=>point(c.x + s.relative_flexure_mm*2500/1000,c.y,s.z_m));
        result += line(points,'#bd6b19',3);
      }
    }
  }
  if (active === 'reactions') {
    for (const c of columns) {
      const p = base(c.id), start = offset(p,0,43);
      result += stroke(start,p,ink.positive,3,'marker-end="url(#reaction-tip)"');
      result += label(offset(p,c.x === 0 ? -46 : 46,29),number(a.axial_base,4)+' kN',13);
    }
  }
  if (active === 'rebar') {
    const mx = model.rebar.groups.find(g => g.mark === 'Slab X').pieces_per_member;
    const my = model.rebar.groups.find(g => g.mark === 'Slab Y').pieces_per_member;
    for (let i=0; i<mx; i++) {
      const y = .025 + (d.span_y-.05)*i/(mx-1);
      result += stroke(point(.02,y,d.height),point(d.span_x-.02,y,d.height),ink.mesh,.85);
    }
    for (let i=0; i<my; i++) {
      const x = .025 + (d.span_x-.05)*i/(my-1);
      result += stroke(point(x,.02,d.height),point(x,d.span_y-.02,d.height),ink.mesh,.85);
    }
    for (const c of columns) {
      for (const dx of [-.09,.09]) for (const dy of [-.09,.09]) {
        result += stroke(point(c.x+dx,c.y+dy,.04),point(c.x+dx,c.y+dy,d.height-.04),ink.steel,1.65);
      }
    }
    for (const b of beams) {
      const c = map[b.start_column], e = map[b.end_column];
      const margin = (d.column/2 + .025)/d.span_x;
      for (const side of [-1,1]) for (const z of [d.height-.08,d.height-.36]) {
        const dx = b.axis === 'Y' ? side*.078 : 0;
        const dy = b.axis === 'X' ? side*.078 : 0;
        const p = point(c.x +(e.x-c.x)*margin+dx,c.y+(e.y-c.y)*margin+dy,z);
        const q = point(e.x +(c.x-e.x)*margin+dx,e.y+(c.y-e.y)*margin+dy,z);
        result += stroke(p,q,ink.steel,1.75);
      }
    }
  }
  // Numeric values follow each beam's local direction. Excluded DOFs are not zeroes.
  if (active === 'moment' || active === 'shear') {
    for (const b of beams) {
      const midPoint = along(b.start_column,b.end_column,.5,d.height);
      const value = active === 'moment' ? samples[20].moment : samples[0].shear;
      const units = active === 'moment' ? 'kN·m' : 'kN';
      result += label(offset(midPoint,0,-58),(active==='moment' ? 'Mmid ' : 'Vnear ')+number(value)+' '+units,13);
    }
  }
  if (active === 'movement') {
    result += label([475,450],'Beam '+number(samples[20].deflection_mm,5)+' mm (chord-relative)',15);
    if (model.column_flexure) result += label([475,478],'Column '+number(model.column_flexure.peak_chord_relative_mm,5)+' mm at 2.00 m (per plane)',15);
  }
  const notes = active === 'torsion' ? label([475,492],'Torsion was not calculated',21) :
    active === 'reactions' ? '' : label([475,490],'4.00 m × 4.00 m grid',16,'normal');
  return `<title id="frame-title">${titles[active]}</title><defs><marker id="reaction-tip" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10Z" fill="${ink.positive}"/></marker></defs>` +
    basePlane + members + result + identifiers + notes;
}

function resultsFor(mode, model) {
  const a = model.actions, near = model.samples[0], mid = model.samples[20];
  const far = model.samples.at(-1);
  const beams = model.beams.map(b => b.id).join(', ');
  const columns = model.columns.map(c => c.id).join(', ');
  switch (mode) {
    case 'moment': return ['Positive sagging / negative hogging.',
      'Blue above the member denotes positive moment. Red below denotes negative moment. Column end moments are listed as magnitudes per plane.',
      [[beams, 'Near / midspan / far (kN·m)', [near, mid, far].map(s=>number(s.moment)).join(' / ')],
       [columns, 'Per-plane roof / base magnitude (kN·m)', number(a.column_moment_roof)+' / '+number(a.column_moment_base)],
       ['S1','Slab role','Tributary gravity loading']]];
    case 'shear': return ['Shear signs follow each beam’s local direction.',
      'Each beam runs from its listed start column to its end column. Blue and red denote positive and negative shear. Column shear is listed per plane.',
      [...model.beams.map(b=>[b.id, b.start_column+' → '+b.end_column, [near, mid, far].map(s=>number(s.shear)).join(' / ')+' kN']),
       [columns,'In-plane horizontal magnitude',number(a.column_shear)+' kN']]];
    case 'axial': return ['Compression in C1–C4.',
      'The purple strips widen toward the bases because each column carries its own weight in addition to the roof load.',
      [[columns,'Roof / base compression (kN)',number(a.axial_roof,4)+' / '+number(a.axial_base,4)],
       [beams,'Beam axial force','Outside the model'],['S1','Slab membrane forces','Outside the model']]];
    case 'torsion': return ['Torsion is outside the analysis.',
      'The experiment uses two planar gravity frames and distributes slab loads by tributary area. The model gives no member torque or slab twisting result.',
      [[beams,'Beam torsion','Outside the model'],[columns,'Column torsion','Outside the model'],['S1','Slab twisting moment','Outside the model']]];
    case 'movement': return ['Beam sag (purple) and column bending (orange), each relative to the member end chord.',
      'Beam curve magnified 1,400 times; column curve magnified 2,500 times. The column curve is the supplementary elastic no-sway in-plane derivation. Roof drift, column axial shortening and slab displacement remain unsolved.',
      [[beams,'Beam midspan chord-relative (mm)',number(mid.deflection_mm,5)],
       [columns,'Column max in-plane chord-relative (mm)',model.column_flexure ? number(model.column_flexure.peak_chord_relative_mm,5) : 'Unavailable'],
       [columns,'Column peak height (m from base)',model.column_flexure ? number(model.column_flexure.peak_z_m,2) : 'Unavailable'],
       [columns,'Roof translation','Zero by no-sway model assumption; not calculated drift'],
       [beams,'Beam ends relative to chord (mm)',number(near.deflection_mm)+' / '+number(far.deflection_mm)]]];
    case 'rebar': return ['Illustrative reinforcement takeoff.',
      'Brown shows longitudinal beam and column bars. Green shows the slab mat. Beam links and column ties are included in the takeoff.',
      [...model.rebar.groups.map(g=>[g.mark, g.pieces_per_member+' × Ø'+g.diameter_mm,number(g.length_per_piece_m)+' m']),
       ['Total','Theoretical steel mass',number(model.rebar.mass_kg,2)+' kg']]];
    case 'reactions': return ['Vertical reactions at fixed bases C1–C4.',
      'All four arrows point up. Per-plane horizontal shear and support couple magnitudes are listed separately.',
      [...model.columns.map(c=>[c.id,'Upward vertical reaction',number(a.axial_base,4)+' kN']),
       ['All bases','Vertical total',number(a.total_reaction,2)+' kN'],
       ['Each base','Horizontal shear / couple, per plane',number(a.column_shear)+' kN / '+number(a.column_moment_base)+' kN·m']]];
  }
}


function highlightsFor(mode, model) {
  const a=model.actions, near=model.samples[0], mid=model.samples[20], far=model.samples.at(-1);
  switch(mode) {
    case 'moment': return [
      ['Near end, B1–B4',number(near.moment)+' kN·m'],
      ['Midspan, B1–B4',number(mid.moment)+' kN·m'],
      ['Far end, B1–B4',number(far.moment)+' kN·m'],
      ['Column roof / base, per plane',number(a.column_moment_roof)+' / '+number(a.column_moment_base)+' kN·m']];
    case 'shear': return [
      ['Near end, B1–B4',number(near.shear)+' kN'],
      ['Midspan, B1–B4',number(mid.shear)+' kN'],
      ['Far end, B1–B4',number(far.shear)+' kN'],
      ['Column horizontal shear, per plane',number(a.column_shear)+' kN']];
    case 'axial': return [
      ['Column roof compression',number(a.axial_roof,4)+' kN'],
      ['Column base compression',number(a.axial_base,4)+' kN'],
      ['One-bay beam axial','Not calculated'],
      ['Slab membrane force','Not calculated']];
    case 'reactions': return [
      ['Each of C1–C4, vertical',number(a.axial_base,4)+' kN up'],
      ['All four bases',number(a.total_reaction,3)+' kN up'],
      ['Horizontal shear, each plane',number(a.column_shear)+' kN'],
      ['Base couple, each plane',number(a.column_moment_base)+' kN·m']];
    case 'movement': return [
      ['Beam midspan chord-relative',number(mid.deflection_mm,5)+' mm'],
      ['Column peak chord-relative',model.column_flexure ? number(model.column_flexure.peak_chord_relative_mm,5)+' mm' : 'Unavailable'],
      ['Column peak above base',model.column_flexure ? number(model.column_flexure.peak_z_m,2)+' m' : 'Unavailable'],
      ['Global roof drift / slab deflection','Not calculated']];
    case 'torsion': return [
      ['Beam torsion','Not calculated'],['Column torsion','Not calculated'],
      ['Slab twisting','Not calculated'],['Analysis scope','Two planar gravity frames']];
    case 'rebar': return [
      ['Illustrative frame steel',number(model.rebar.mass_kg,2)+' kg'],
      ['Slab bars, each direction','21 × Ø10 mm'],
      ['Design certification','Not provided'],['Purchasing schedule','Not provided']];
  }
}

async function mount() {
  const entries = Object.entries(tabs);
  const box = document.querySelector('#frame-tabs');
  const panel = document.querySelector('#frame-panel');
  const key = document.querySelector('#frame-key');
  const {searchParams} = new URL(location.href);
  const response = await fetch('frame-results.json');
  if (!response.ok) throw new Error('Frame results unavailable');
  const model = await response.json();
  const buttons = entries.map(([id,text]) => {
    const button = Object.assign(document.createElement('button'), {type:'button',id:'view-'+id,textContent:text});
    button.dataset.view = id;
    button.setAttribute('role','tab');
    button.setAttribute('aria-controls',panel.id);
    box.append(button);
    return button;
  });

  function show(mode, updateUrl) {
    for (const b of buttons) {
      const selected = b.dataset.view === mode;
      b.setAttribute('aria-selected',String(selected));
      b.tabIndex = selected ? 0 : -1;
    }
    panel.setAttribute('aria-labelledby','view-'+mode);
    panel.dataset.active = mode;
    document.querySelector('#frame-drawing').innerHTML = spatialView(model, mode);
    const highlights = document.querySelector('#frame-highlights');
    highlights.replaceChildren();
    for (const [label,value] of highlightsFor(mode,model)) {
      const card=document.createElement('div');
      card.className='frame-stat';
      const name=document.createElement('span');
      name.textContent=label;
      const output=document.createElement('strong');
      output.textContent=value;
      card.append(name,output);
      highlights.append(card);
    }
    const [headline, detail, rows] = resultsFor(mode,model);
    const strong = document.createElement('strong');
    strong.textContent = headline;
    key.replaceChildren(strong, document.createTextNode(' '+detail));
    const table = document.createElement('table');
    const headings = table.createTHead().insertRow();
    for (const name of ['Element or group', 'Quantity', 'Result']) {
      const th = document.createElement('th');
      th.scope = 'col';
      th.textContent = name;
      headings.append(th);
    }
    const body = table.createTBody();
    for (const fields of rows) {
      const row = body.insertRow();
      for (const value of fields) row.insertCell().textContent = value;
    }
    document.querySelector('#frame-values').replaceChildren(table);
    if (updateUrl) {
      const url = new URL(location.href);
      url.searchParams.set('view',mode);
      history.replaceState(null,'',url);
    }
  }

  buttons.forEach((button,i) => {
    button.onclick = () => show(button.dataset.view,true);
    button.onkeydown = event => {
      const target = {ArrowRight:(i+1)%buttons.length,ArrowLeft:(i+buttons.length-1)%buttons.length,
        Home:0,End:buttons.length-1}[event.key];
      if (target === undefined) return;
      event.preventDefault();
      buttons[target].focus();
      show(buttons[target].dataset.view,true);
    };
  });
  show(Object.hasOwn(tabs,searchParams.get('view')) ? searchParams.get('view') : 'moment',false);
}

mount().catch(() => {
  document.querySelector('#frame-key').textContent = 'Frame results could not be loaded. Reload this page or open the four-workflow experiment.';
});
