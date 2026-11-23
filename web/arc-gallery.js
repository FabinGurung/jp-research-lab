/* Progressive, keyboard-accessible curved galleries. No source links or records deleted. */
(function () {
  'use strict';
  const selector = '.grid, .lanes';
  function humanizeRecords(root) {
    root.querySelectorAll('.lane .code, .lane p').forEach(function (node) {
      const original = node.textContent.trim();
      if (!/[A-Z][A-Z0-9_]{29,}/.test(original) || node.dataset.humanized) return;
      node.dataset.humanized = 'true';
      const details = document.createElement('details');
      details.className = 'record-details';
      const summary = document.createElement('summary');
      summary.textContent = 'Show original technical status';
      const value = document.createElement('code');
      value.textContent = original;
      details.append(summary, value);
      const human = original.includes('Research state:') ? 'Research state · see original record below' :
        original.includes('Application:') ? 'Application record · see original status below' :
        original.includes('RESTORED_MAIN') ? 'Restored public research module' :
        'Research module · technical status available below';
      node.textContent = human;
      node.insertAdjacentElement('afterend', details);
    });
  }
  function install(stage, number) {
    const cards = Array.from(stage.children).filter(function (x) {
      return x.matches('article.card, article.lane');
    });
    if (cards.length < 2 || cards.length !== stage.children.length || stage.closest('.arc-stage')) return;
    const title = stage.closest('section')?.querySelector('h2')?.textContent?.trim() || 'Explore this collection';
    stage.classList.add('arc-stage');
    stage.setAttribute('role','region');
    stage.setAttribute('aria-label',title + ' — curved gallery');
    stage.setAttribute('tabindex','0');
    const toolbar = document.createElement('div');
    toolbar.className = 'arc-toolbar';
    const heading = document.createElement('span');
    heading.className = 'arc-title';
    heading.textContent = 'Curved gallery · drag or use the arrows';
    const actions = document.createElement('div');
    actions.className = 'arc-actions';
    const previous = document.createElement('button');
    previous.type = 'button'; previous.textContent = '← Previous'; previous.setAttribute('aria-label','Previous card');
    const count = document.createElement('span');
    count.className = 'arc-count'; count.setAttribute('aria-live','polite');
    const next = document.createElement('button');
    next.type = 'button'; next.textContent = 'Next →'; next.setAttribute('aria-label','Next card');
    const all = document.createElement('button');
    all.type = 'button'; all.textContent = 'View all cards'; all.setAttribute('aria-pressed','false');
    actions.append(previous,count,next,all); toolbar.append(heading,actions);
    stage.parentNode.insertBefore(toolbar,stage);
    let active=0, expanded=false, pointerX=null, dragged=false;
    function paint() {
      stage.classList.toggle('arc-expanded',expanded);
      all.textContent = expanded ? 'Return to gallery' : 'View all cards';
      all.setAttribute('aria-pressed',String(expanded));
      previous.disabled=expanded; next.disabled=expanded;
      count.textContent = expanded ? cards.length + ' cards' : (active+1) + ' / ' + cards.length;
      cards.forEach(function (card,i) {
        let delta=i-active;
        if (delta>cards.length/2) delta-=cards.length;
        if (delta< -cards.length/2) delta+=cards.length;
        const dist=Math.abs(delta);
        card.classList.toggle('is-current',dist===0);
        card.classList.toggle('is-neighbor',dist===1);
        card.classList.toggle('is-far',dist>1);
        card.style.zIndex=String(cards.length-dist);
        card.style.transform='translate(-50%, -50%) translateX('+ (delta*55) +'%) translateZ('+(-dist*175)+'px) rotateY('+(-delta*30)+'deg) scale('+(1-dist*.08)+')';
        card.setAttribute('aria-hidden',expanded ? 'false' : String(dist>0));
        card.querySelectorAll('a,button,input,select,textarea').forEach(function (control) {
          if (expanded || dist===0) control.removeAttribute('tabindex');
          else control.setAttribute('tabindex','-1');
        });
      });
      const height=Math.max(410,Math.min(900,cards[active].scrollHeight+70));
      stage.style.minHeight=expanded?'0px':height+'px';
    }
    function move(step) { active=(active+step+cards.length)%cards.length; paint(); }
    previous.addEventListener('click',function(){move(-1)});
    next.addEventListener('click',function(){move(1)});
    all.addEventListener('click',function(){expanded=!expanded;paint()});
    stage.addEventListener('keydown',function(e){
      if(expanded || !['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
      e.preventDefault();
      if(e.key==='Home')active=0; else if(e.key==='End')active=cards.length-1;
      else active=(active+(e.key==='ArrowRight'?1:-1)+cards.length)%cards.length;
      paint();
    });
    stage.addEventListener('pointerdown',function(e){
      if(expanded || e.button!==0 || e.target.closest('button,input,textarea,select'))return;
      pointerX=e.clientX;dragged=false;
    });
    stage.addEventListener('pointermove',function(e){
      if(pointerX===null)return;
      if(Math.abs(e.clientX-pointerX)>12){ dragged=true; stage.classList.add('is-dragging');}
    });
    stage.addEventListener('pointerup',function(e){
      if(pointerX===null)return;
      const dx=e.clientX-pointerX;pointerX=null;stage.classList.remove('is-dragging');
      if(Math.abs(dx)>48)move(dx<0?1:-1);
    });
    stage.addEventListener('pointercancel',function(){pointerX=null;stage.classList.remove('is-dragging')});
    stage.addEventListener('click',function(e){
      if(dragged && e.target.closest('a')){e.preventDefault();e.stopPropagation();dragged=false;return;}
      const card=e.target.closest('article.card,article.lane');
      if(!expanded && card && !card.classList.contains('is-current')){
        e.preventDefault(); active=cards.indexOf(card); paint();
      }
    },true);
    window.addEventListener('resize',paint);
    paint();
  }
  function start() {
    humanizeRecords(document);
    document.querySelectorAll(selector).forEach(install);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start);
  else start();
})();
