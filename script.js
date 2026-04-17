(function () {
  const docEl = document.documentElement;
  const themeToggle = document.getElementById('theme-toggle');
  const progressBar = document.getElementById('progress-bar');
  const navToggle = document.querySelector('.nav-toggle');
  const primaryNav = document.querySelector('.primary-nav');
  const tickerTrack = document.getElementById('ticker-track');
  const storageKey = 'signalbytes-theme';

  function setTheme(theme) {
    docEl.setAttribute('data-theme', theme);
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(theme === 'dark'));
      themeToggle.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    }
  }

  function initTheme() {
    const savedTheme = localStorage.getItem(storageKey);
    if (savedTheme === 'light' || savedTheme === 'dark') {
      setTheme(savedTheme);
      return;
    }

    setTheme('dark');
  }

  function updateProgressBar() {
    if (!progressBar) return;

    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
    progressBar.style.width = `${Math.min(progress, 100)}%`;
  }

  function initThemeToggle() {
    if (!themeToggle) return;

    themeToggle.addEventListener('click', function () {
      const nextTheme = docEl.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      localStorage.setItem(storageKey, nextTheme);
      setTheme(nextTheme);
    });
  }

  function initNav() {
    if (!navToggle || !primaryNav) return;

    navToggle.addEventListener('click', function () {
      const isOpen = primaryNav.classList.toggle('is-open');
      navToggle.setAttribute('aria-expanded', String(isOpen));
    });

    document.addEventListener('click', function (event) {
      if (!primaryNav.classList.contains('is-open')) return;
      if (primaryNav.contains(event.target) || navToggle.contains(event.target)) return;
      primaryNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 840) {
        primaryNav.classList.remove('is-open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function initTicker() {
    if (!tickerTrack) return;

    tickerTrack.addEventListener('mouseenter', function () {
      tickerTrack.style.animationPlayState = 'paused';
    });

    tickerTrack.addEventListener('mouseleave', function () {
      tickerTrack.style.animationPlayState = 'running';
    });
  }

  initTheme();
  initThemeToggle();
  initNav();
  initTicker();
  updateProgressBar();

  window.addEventListener('scroll', updateProgressBar, { passive: true });
  window.addEventListener('resize', updateProgressBar);
})();
