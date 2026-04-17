/* =========================================================
   SignalBytes — Premium Editorial Script
   Reading progress · Theme toggle · Mobile menu · Cookie consent
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

  window.addEventListener('scroll', () => {
    if (!rafPending) {
      rafPending = true;
      requestAnimationFrame(updateProgress);
    }
  }, { passive: true });
  updateProgress();


  /* -------- 2. Theme Toggle (dark default, persisted) -------- */
  const root = document.documentElement;
  const themeToggle = document.querySelector('.theme-toggle');

  // Apply stored theme (default: dark)
  const stored = localStorage.getItem('sb_theme');
  if (stored === 'light') {
    root.setAttribute('data-theme', 'light');
    if (themeToggle) themeToggle.setAttribute('aria-pressed', 'true');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = root.getAttribute('data-theme') === 'light';
      if (isLight) {
        root.removeAttribute('data-theme');
        themeToggle.setAttribute('aria-pressed', 'false');
        localStorage.setItem('sb_theme', 'dark');
      } else {
        root.setAttribute('data-theme', 'light');
        themeToggle.setAttribute('aria-pressed', 'true');
        localStorage.setItem('sb_theme', 'light');
      }
    });
  }


  /* -------- 3. Mobile Menu Toggle -------- */
  const menuBtn  = document.querySelector('.menu-btn');
  const pillars  = document.querySelector('.nav-pillars');
  const siteNav  = document.querySelector('.site-nav');

  if (menuBtn && pillars) {
    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = pillars.classList.toggle('mobile-open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    document.addEventListener('click', (e) => {
      if (siteNav && !siteNav.contains(e.target)) {
        pillars.classList.remove('mobile-open');
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Inject mobile-open styles dynamically so CSS stays lean
  const mobileStyle = document.createElement('style');
  mobileStyle.textContent = `
    @media (max-width: 1024px) {
      .nav-pillars.mobile-open {
        display: flex !important;
        flex-direction: column;
        position: absolute;
        top: 72px;
        right: 16px;
        min-width: 220px;
        padding: 10px;
        border-radius: 16px;
        background: var(--bg-raise);
        border: 1px solid var(--glass-border);
        box-shadow: 0 16px 40px rgba(5, 10, 18, 0.35);
        z-index: 950;
      }
      .nav-pillars.mobile-open a {
        padding: 12px 16px;
        text-align: left;
      }
    }
  `;
  document.head.appendChild(mobileStyle);


  /* -------- 4. Cookie Consent -------- */
  const banner = document.getElementById('cookie-banner');
  if (banner && !localStorage.getItem('sb_consent')) {
    // Small delay so banner animates in after page settles
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


  /* -------- 5. Smooth header hide on scroll down (subtle polish) -------- */
  let lastScroll = 0;
  const nav = document.querySelector('.site-nav');
  window.addEventListener('scroll', () => {
    const cur = window.pageYOffset;
    if (nav) {
      if (cur > 200 && cur > lastScroll) {
        nav.style.transform = 'translateY(-100%)';
      } else {
        nav.style.transform = 'translateY(0)';
      }
    }
    lastScroll = cur;
  }, { passive: true });
  if (nav) nav.style.transition = 'transform .35s cubic-bezier(.22,.61,.36,1)';

})();
