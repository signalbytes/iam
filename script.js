/* =========================================================
   SignalBytes — Editorial Script
   Reading progress · Mobile menu · Cookie consent
   ========================================================= */

(function () {
  'use strict';

  /* -------- 1. Reading Progress Bar -------- */
  const progressBar = document.getElementById('progress-bar');
  let rafPending = false;

  function updateProgress() {
    rafPending = false;
    const doc = document.documentElement;
    const scrollTop = window.pageYOffset || doc.scrollTop;
    const height = doc.scrollHeight - doc.clientHeight;
    const pct = height > 0 ? Math.min(100, (scrollTop / height) * 100) : 0;
    if (progressBar) progressBar.style.width = pct + '%';
  }

  if (progressBar) {
    window.addEventListener('scroll', () => {
      if (!rafPending) {
        rafPending = true;
        requestAnimationFrame(updateProgress);
      }
    }, { passive: true });
    updateProgress();
  }


  /* -------- 2. Mobile Menu Toggle -------- */
  const nav     = document.querySelector('.site-nav');
  const toggle  = document.querySelector('.nav-toggle');

  if (toggle && nav) {
    toggle.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target)) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }


  /* -------- 3. Cookie Consent -------- */
  const banner = document.getElementById('cookie-banner');
  if (banner && !localStorage.getItem('sb_consent')) {
    setTimeout(() => { banner.style.display = 'block'; }, 800);
  }

  window.handleConsent = function (status) {
    localStorage.setItem('sb_consent', status);
    if (banner) banner.style.display = 'none';
    if (typeof gtag === 'function') {
      gtag('consent', 'update', {
        ad_storage: status,
        analytics_storage: status,
        ad_user_data: status,
        ad_personalization: status
      });
    }
  };

})();
