/* First-visit guidance for the public sandbox. No evaluation or graph data is stored here. */
(() => {
  'use strict';

  const STORAGE_KEY = 'faultline-tour-v1-complete';
  const steps = [
    {
      target: '#scenario',
      title: 'Pick a demo problem',
      description: 'Start with checkout. Its failure may come from a shared currency setting that the first map does not show.',
    },
    {
      target: '.control-actions',
      title: 'Break it, then investigate',
      description: 'Trigger fault changes the demo app. Investigate checks the current map. Inspect & learn checks evidence when a connection is missing.',
    },
    {
      target: '#health',
      title: 'See what stopped working',
      description: 'Checkout, refunds, and renewals run real checks in this demo. Restore app makes them healthy again.',
    },
    {
      target: '#graph-section',
      title: 'See the connection it learned',
      description: 'The live HydraDB graph shows which feature, service, and shared setting connect. Saved claims keep their evidence IDs.',
    },
    {
      target: '#results-section',
      title: 'Check whether it helped',
      description: 'The chart counts correct answers across controlled cases and compares this approach with unchanged and random baselines.',
    },
  ];

  const tour = document.getElementById('tour');
  const highlight = document.getElementById('tour-highlight');
  const card = document.getElementById('tour-card');
  const progress = document.getElementById('tour-progress');
  const title = document.getElementById('tour-title');
  const description = document.getElementById('tour-description');
  const back = document.getElementById('tour-back');
  const next = document.getElementById('tour-next');
  const skip = document.getElementById('tour-skip');
  let availableSteps = [];
  let current = -1;
  let previousFocus = null;

  function hasSeenTour() {
    try { return localStorage.getItem(STORAGE_KEY) === 'yes'; }
    catch { return false; }
  }

  function rememberTour() {
    try { localStorage.setItem(STORAGE_KEY, 'yes'); }
    catch { /* The tour still works when browser storage is unavailable. */ }
  }

  function position() {
    if (tour.hidden || current < 0) return;
    const target = document.querySelector(availableSteps[current].target);
    if (!target) return;
    const rect = target.getBoundingClientRect();
    const inset = 6;
    Object.assign(highlight.style, {
      left: `${Math.max(4, rect.left - inset)}px`,
      top: `${Math.max(4, rect.top - inset)}px`,
      width: `${Math.min(innerWidth - 8, rect.width + inset * 2)}px`,
      height: `${Math.min(innerHeight - 8, rect.height + inset * 2)}px`,
    });
    if (innerWidth > 760) {
      const below = rect.bottom + 16;
      const above = rect.top - card.offsetHeight - 16;
      card.style.top = `${below + card.offsetHeight < innerHeight - 16 ? below : Math.max(16, above)}px`;
      card.style.left = `${Math.min(innerWidth - card.offsetWidth - 16, Math.max(16, rect.left))}px`;
    }
  }

  function showStep() {
    const step = availableSteps[current];
    progress.textContent = `WORKSPACE TOUR / ${current + 1} OF ${availableSteps.length}`;
    title.textContent = step.title;
    description.textContent = step.description;
    back.hidden = current === 0;
    next.textContent = current === availableSteps.length - 1 ? 'Finish tour' : 'Next';
    const target = document.querySelector(step.target);
    target.scrollIntoView({ behavior: 'auto', block: 'center' });
    requestAnimationFrame(position);
    setTimeout(position, 230);
    next.focus();
  }

  function stop(remember = true) {
    if (tour.hidden) return;
    if (remember) rememberTour();
    tour.hidden = true;
    current = -1;
    availableSteps = [];
    previousFocus?.focus();
  }

  function start(force = false) {
    if (!force && hasSeenTour()) return;
    availableSteps = steps.filter(step => {
      const target = document.querySelector(step.target);
      return target && target.getClientRects().length > 0;
    });
    if (!availableSteps.length) return;
    previousFocus = document.activeElement;
    current = 0;
    tour.hidden = false;
    showStep();
  }

  next.addEventListener('click', () => {
    if (current === availableSteps.length - 1) stop();
    else { current += 1; showStep(); }
  });
  back.addEventListener('click', () => { current -= 1; showStep(); });
  skip.addEventListener('click', () => stop());
  document.addEventListener('keydown', event => {
    if (tour.hidden) return;
    if (event.key === 'Escape') { event.preventDefault(); stop(); }
    if (event.key === 'Tab') {
      const controls = [skip, back, next].filter(button => !button.hidden);
      const index = controls.indexOf(document.activeElement);
      if (event.shiftKey && index <= 0) { event.preventDefault(); controls.at(-1).focus(); }
      if (!event.shiftKey && index === controls.length - 1) { event.preventDefault(); controls[0].focus(); }
    }
  });
  window.addEventListener('resize', position);
  window.addEventListener('scroll', position, true);

  window.FaultlineTour = { start, stop, maybeStart: () => start(false) };
})();
