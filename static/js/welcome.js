/* ─────────────────────────────────────────
   welcome.js – Welcome Page Scripts
───────────────────────────────────────── */

// ── 1. VISITOR POPUP – show after 1.5s delay ──
window.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('popupOverlay');
  const closeBtn = document.getElementById('popupClose');

  // Show popup after 1.5 seconds
  setTimeout(() => {
    if (overlay) overlay.style.display = 'flex';
  }, 1500);

  // Close on X button
  if (closeBtn) {
    closeBtn.addEventListener('click', () => closePopup());
  }

  // Close on overlay click
  if (overlay) {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closePopup();
    });
  }
});

function closePopup() {
  const overlay = document.getElementById('popupOverlay');
  if (overlay) {
    overlay.style.opacity = '0';
    overlay.style.transition = 'opacity 0.3s ease';
    setTimeout(() => { overlay.style.display = 'none'; }, 300);
  }
}

// ── 2. VISITOR FORM SUBMIT ──
function handleVisitorSubmit(e) {
  e.preventDefault();
  const form    = document.getElementById('visitorForm');
  const success = document.getElementById('popupSuccess');

  form.style.display = 'none';
  success.style.display = 'block';

  // After 2.5s redirect to portal
  setTimeout(() => {
    closePopup();
    form.style.display = 'block';
    success.style.display = 'none';
    form.reset();
  }, 2500);
}

// ── 3. NAVBAR SCROLL EFFECT ──
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 40) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// ── 4. SMOOTH SCROLL FOR NAV LINKS ──
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── 5. SCROLL REVEAL ANIMATION ──
const revealElements = document.querySelectorAll(
  '.about-grid, .gallery-item, .achievement-card, .event-chip, .events-cta-box, .section-title, .section-desc, .section-tag'
);

revealElements.forEach(el => el.classList.add('reveal'));

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => {
        entry.target.classList.add('visible');
      }, i * 80);
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ── 6. HAMBURGER MENU (mobile) ──
const hamburger = document.getElementById('hamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    const links = document.querySelector('.nav-links');
    if (links) {
      const isOpen = links.style.display === 'flex';
      links.style.display = isOpen ? 'none' : 'flex';
      links.style.flexDirection = 'column';
      links.style.position = 'absolute';
      links.style.top = '64px';
      links.style.left = '0';
      links.style.right = '0';
      links.style.background = '#fff';
      links.style.padding = '16px 24px';
      links.style.borderBottom = '1px solid #e5e7eb';
      links.style.boxShadow = '0 8px 24px rgba(0,0,0,.1)';
      links.style.gap = '16px';
    }
  });
}
