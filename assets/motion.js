/* Progressive enhancement: all content and links work without JavaScript. */
(() => {
  'use strict';
  const body = document.body;
  if (!body.classList.contains('homepage')) return;
  const header = document.querySelector('.site-header');
  const hero = document.querySelector('.hero');
  const portrait = document.querySelector('.portrait');
  const orbit = document.querySelector('.orbit-art');
  const progress = document.querySelector('.reading-progress');
  const toggle = document.querySelector('.motion-toggle');
  const backTop = document.querySelector('.back-top');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = matchMedia('(hover: hover) and (pointer: fine)');
  const sections = [...document.querySelectorAll('main section[id]')];
  const navLinks = [...header.querySelectorAll('nav a[href^="#"]')];
  const chapters = {
    about: ['#315d47', '123, 151, 110'],
    research: ['#405b75', '114, 148, 170'],
    education: ['#65553e', '169, 150, 102'],
    projects: ['#315d47', '123, 151, 110'],
    honors: ['#756039', '183, 159, 93'],
    contact: ['#315d47', '123, 151, 110']
  };
  let preference = null;
  try { preference = localStorage.getItem('homepage-motion'); } catch { /* Storage is optional. */ }
  let enabled = !reduce.matches && preference !== 'off';
  let scrollFrame = 0;
  let pointerFrame = 0;
  let lastChapter = '';
  let pointerX = 0;
  let pointerY = 0;
  let card = null;

  const revealNodes = [...document.querySelectorAll('.section-heading, .about-copy, .research-intro, .research-grid article, .education-line, .study-grid > div, .project, .academic-honor, .honor-row, .additional-honors, .competition-progress')];
  let observer = null;
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    }, { threshold: 0.06, rootMargin: '0px 0px -24px 0px' });
    revealNodes.forEach(node => {
      node.dataset.reveal = '';
      observer.observe(node);
    });
    document.querySelectorAll('.research-grid article, .study-grid > div').forEach((node, i) => {
      node.style.setProperty('--reveal-delay', `${(i % 3) * 70}ms`);
    });
    body.classList.add('motion-ready');
  }

  function clearCard() {
    if (!card) return;
    ['--tilt-x', '--tilt-y', '--spot-x', '--spot-y', '--spot-opacity'].forEach(name => card.style.removeProperty(name));
    card = null;
  }

  function setMotion(value) {
    enabled = value && !reduce.matches;
    body.classList.toggle('motion-paused', !enabled);
    toggle.hidden = false;
    toggle.setAttribute('aria-pressed', String(enabled));
    const label = reduce.matches ? '系统已启用减少动态效果' : (enabled ? '关闭页面动效' : '开启页面动效');
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
    toggle.disabled = reduce.matches;
    if (!enabled) {
      portrait.style.removeProperty('--portrait-x');
      portrait.style.removeProperty('--portrait-y');
      hero.style.removeProperty('--hero-x');
      hero.style.removeProperty('--hero-y');
      body.style.removeProperty('--ambient-x');
      body.style.removeProperty('--ambient-y');
      orbit.style.removeProperty('--orbit-rotation');
      clearCard();
    }
    scheduleScroll();
  }

  function updateScroll() {
    scrollFrame = 0;
    const y = window.scrollY;
    const available = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${available > 0 ? Math.min(1, Math.max(0, y / available)) : 0})`;
    const heroBottom = hero.getBoundingClientRect().bottom;
    header.classList.toggle('is-light', heroBottom <= header.offsetHeight);
    backTop.hidden = y < 650;
    const line = header.offsetHeight + Math.min(180, innerHeight * .22);
    let current = '';
    for (const section of sections) {
      if (section.getBoundingClientRect().top <= line) current = section.id;
    }
    if (current !== lastChapter) {
      lastChapter = current;
      navLinks.forEach(link => {
        if (link.hash === `#${current}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      const [color, glow] = chapters[current] || chapters.about;
      body.style.setProperty('--chapter-color', color);
      body.style.setProperty('--chapter-glow', glow);
    }
    if (enabled && heroBottom > 0) orbit.style.setProperty('--orbit-rotation', `${-12 + Math.min(y, 900) * .035}deg`);
  }

  function scheduleScroll() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
  }

  function updatePointer() {
    pointerFrame = 0;
    if (!enabled || !pointer.matches) return;
    body.style.setProperty('--ambient-x', `${pointerX}px`);
    body.style.setProperty('--ambient-y', `${pointerY}px`);
    const bounds = hero.getBoundingClientRect();
    if (bounds.bottom > 0 && pointerY < bounds.bottom) {
      const nx = (pointerX - bounds.left) / bounds.width;
      const ny = (pointerY - bounds.top) / bounds.height;
      hero.style.setProperty('--hero-x', `${nx * 100}%`);
      hero.style.setProperty('--hero-y', `${ny * 100}%`);
      portrait.style.setProperty('--portrait-x', `${(nx - .5) * 12}px`);
      portrait.style.setProperty('--portrait-y', `${(ny - .5) * 10}px`);
    }
    if (card) {
      const b = card.getBoundingClientRect();
      const nx = Math.min(1, Math.max(0, (pointerX - b.left) / b.width));
      const ny = Math.min(1, Math.max(0, (pointerY - b.top) / b.height));
      card.style.setProperty('--tilt-x', `${(.5 - ny) * 3}deg`);
      card.style.setProperty('--tilt-y', `${(nx - .5) * 3}deg`);
      card.style.setProperty('--spot-x', `${nx * 100}%`);
      card.style.setProperty('--spot-y', `${ny * 100}%`);
      card.style.setProperty('--spot-opacity', '1');
    }
  }

  document.addEventListener('pointermove', event => {
    if (!enabled || !pointer.matches || event.pointerType === 'touch') return;
    pointerX = event.clientX;
    pointerY = event.clientY;
    const next = event.target.closest('.research-grid article');
    if (next !== card) { clearCard(); card = next; }
    if (!pointerFrame) pointerFrame = requestAnimationFrame(updatePointer);
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', () => {
    clearCard();
    portrait.style.removeProperty('--portrait-x');
    portrait.style.removeProperty('--portrait-y');
  });
  window.addEventListener('scroll', scheduleScroll, { passive: true });
  window.addEventListener('resize', scheduleScroll, { passive: true });
  window.addEventListener('pageshow', scheduleScroll);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(scrollFrame); scrollFrame = 0;
      cancelAnimationFrame(pointerFrame); pointerFrame = 0;
    } else scheduleScroll();
  });
  toggle.addEventListener('click', () => {
    preference = enabled ? 'off' : 'on';
    try { localStorage.setItem('homepage-motion', preference); } catch { /* Storage is optional. */ }
    setMotion(preference === 'on');
  });
  reduce.addEventListener('change', () => setMotion(preference !== 'off'));
  pointer.addEventListener('change', () => {
    clearCard();
    portrait.style.removeProperty('--portrait-x');
    portrait.style.removeProperty('--portrait-y');
  });
  setMotion(enabled);
})();
