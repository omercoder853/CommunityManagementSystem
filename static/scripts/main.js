/* CommHub — main.js */
'use strict';

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss alerts ──────────────────────────────────────────────────
  document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .4s ease, transform .4s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 420);
    }, 4000);
  });

  // ── Navbar scroll shadow ─────────────────────────────────────────────────
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.boxShadow = window.scrollY > 10
        ? '0 4px 20px rgba(0,0,0,.1)'
        : '0 1px 3px rgba(0,0,0,.08)';
    }, { passive: true });
  }

  // ── Profile dropdown (custom) ─────────────────────────────────────────────
  const profileBtn  = document.getElementById('profileIconBtn');
  const profileMenu = document.getElementById('profileDropdownMenu');
  if (profileBtn && profileMenu) {
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = profileMenu.classList.contains('is-open');
      profileMenu.classList.toggle('is-open', !isOpen);
      profileBtn.setAttribute('aria-expanded', String(!isOpen));
    });
    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!profileMenu.contains(e.target) && e.target !== profileBtn) {
        profileMenu.classList.remove('is-open');
        profileBtn.setAttribute('aria-expanded', 'false');
      }
    });
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        profileMenu.classList.remove('is-open');
        profileBtn.setAttribute('aria-expanded', 'false');
        profileBtn.focus();
      }
    });
  }


  // ── Animated counters (stats-bar) ─────────────────────────────────────────
  function animateCounter(el, target, duration = 1200) {
    const start = performance.now();
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target).toLocaleString('tr-TR');
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }

  const statNumbers = document.querySelectorAll('.stat-number[data-count]');
  if (statNumbers.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          animateCounter(el, parseInt(el.dataset.count, 10));
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    statNumbers.forEach(el => observer.observe(el));
  }

  // ── Scroll-reveal for cards ──────────────────────────────────────────────
  const revealEls = document.querySelectorAll('.community-card, .event-card, .announcement-card, .card');
  if (revealEls.length && 'IntersectionObserver' in window) {
    revealEls.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(18px)';
      el.style.transition = 'opacity .45s ease, transform .45s ease';
    });
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    revealEls.forEach(el => revealObserver.observe(el));
  }

  // ── Event location toggle (create event form) ───────────────────────────
  const locationSelect = document.getElementById('id_location_type');
  const meetLinkGroup  = document.getElementById('meet-link-group');
  if (locationSelect && meetLinkGroup) {
    function toggleMeetLink() {
      const isOnline = locationSelect.value === 'online';
      meetLinkGroup.style.display = isOnline ? '' : 'none';
      const meetInput = meetLinkGroup.querySelector('input');
      if (meetInput) meetInput.required = isOnline;
    }
    toggleMeetLink();
    locationSelect.addEventListener('change', toggleMeetLink);
  }

  // ── Tabs ────────────────────────────────────────────────────────────────
  document.querySelectorAll('.tabs').forEach(tabsEl => {
    const buttons = tabsEl.querySelectorAll('.tab-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        // Deactivate all
        buttons.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
        // Activate clicked
        btn.classList.add('active');
        const target = document.getElementById(btn.dataset.target);
        if (target) { target.style.display = ''; }
      });
    });
  });

  // ── Advisor request rejection modal ─────────────────────────────────────
  document.querySelectorAll('.btn-reject-request').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const reason = prompt('Red gerekçesi (isteğe bağlı):');
      const form = btn.closest('form');
      if (form) {
        let input = form.querySelector('input[name="reason"]');
        if (!input) {
          input = document.createElement('input');
          input.type = 'hidden';
          input.name = 'reason';
          form.appendChild(input);
        }
        input.value = reason || '';
        form.submit();
      }
    });
  });

  // ── Confirm delete/reject dialogs ────────────────────────────────────────
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

});
