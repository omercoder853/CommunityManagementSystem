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

  // ── Theme Toggle ─────────────────────────────────────────────────────────
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const darkIcon = document.querySelector('.dark-icon');
  const lightIcon = document.querySelector('.light-icon');

  function updateThemeIcons() {
    if (!themeToggleBtn) return;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    if (darkIcon) darkIcon.style.display = isDark ? 'inline-block' : 'none';
    if (lightIcon) lightIcon.style.display = isDark ? 'none' : 'inline-block';
  }

  if (themeToggleBtn) {
    updateThemeIcons();
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      updateThemeIcons();
    });
  }

  // ── Hero Parallax & Cursor Glow ──────────────────────────────────────────
  const heroSection = document.querySelector('.hero');
  const heroGlow = document.querySelector('.hero-cursor-glow');
  const heroShapes = document.querySelectorAll('.hero-shape');

  if (heroSection) {
    heroSection.addEventListener('mousemove', (e) => {
      const rect = heroSection.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      // Move glow smoothly
      if (heroGlow) {
        heroGlow.style.transform = `translate(${x}px, ${y}px) translate(-50%, -50%)`;
      }

      // Parallax shapes
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const moveX = (x - centerX) / 40;
      const moveY = (y - centerY) / 40;

      heroShapes.forEach((shape, index) => {
        const factor = index === 0 ? 1 : (index === 1 ? -1.5 : 2);
        shape.style.transform = `translate(${moveX * factor}px, ${moveY * factor}px)`;
      });
    });
    
    // Reset shapes on mouse leave
    heroSection.addEventListener('mouseleave', () => {
      heroShapes.forEach(shape => {
        shape.style.transform = `translate(0px, 0px)`;
      });
      if (heroGlow) {
        heroGlow.style.transform = `translate(50%, 50%) translate(-50%, -50%)`;
      }
    });
  }

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
  const revealEls = document.querySelectorAll('.community-card, .event-card, .announcement-card, .card, .step-card, .feature-block, .stat-card');
  if (revealEls.length && 'IntersectionObserver' in window) {
    revealEls.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(24px)';
      el.style.transition = 'opacity .6s cubic-bezier(0.2, 0.8, 0.2, 1), transform .6s cubic-bezier(0.2, 0.8, 0.2, 1)';
    });
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const delay = parseInt(entry.target.dataset.revealDelay || '0', 10);
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, delay);
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
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

  // ── Notification Logic ──────────────────────────────────────────────────
  const notifBtn = document.getElementById('notificationIconBtn');
  const notifMenu = document.getElementById('notificationDropdownMenu');
  const notifBadge = document.getElementById('notificationBadge');
  const notifList = document.getElementById('notificationList');
  const markReadBtn = document.getElementById('markNotificationsRead');

  if (notifBtn && notifMenu) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = notifMenu.classList.contains('is-open');
      notifMenu.classList.toggle('is-open', !isOpen);
      notifBtn.setAttribute('aria-expanded', String(!isOpen));
      if (!isOpen && notifList.innerHTML.includes('Yükleniyor')) {
        fetchNotifications();
      }
    });

    document.addEventListener('click', (e) => {
      if (!notifMenu.contains(e.target) && e.target !== notifBtn) {
        notifMenu.classList.remove('is-open');
        notifBtn.setAttribute('aria-expanded', 'false');
      }
    });

    if (markReadBtn) {
      markReadBtn.addEventListener('click', () => {
        fetch('/api/notifications/read/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          }
        }).then(res => res.json()).then(data => {
          if(data.status === 'ok') {
            if(notifBadge) notifBadge.style.display = 'none';
            fetchNotifications();
          }
        });
      });
    }

    // Initial fetch to show badge
    fetchNotifications(true);
  }

  function fetchNotifications(badgeOnly=false) {
    fetch('/api/notifications/')
      .then(res => res.json())
      .then(data => {
        if(notifBadge) {
          if (data.unread_count > 0) {
            notifBadge.textContent = data.unread_count;
            notifBadge.style.display = 'inline-block';
          } else {
            notifBadge.style.display = 'none';
          }
        }
        
        if (!badgeOnly && notifList) {
          if (data.notifications.length === 0) {
            notifList.innerHTML = '<div class="notification-empty" style="padding: 1rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">Bildiriminiz bulunmuyor.</div>';
            return;
          }
          let html = '';
          data.notifications.forEach(n => {
            const cls = n.is_read ? 'notification-item' : 'notification-item unread';
            const link = n.link ? n.link : '#';
            html += `<a href="${link}" class="${cls}">
                      <div class="notification-message">${n.message}</div>
                      <div class="notification-date">${n.date}</div>
                     </a>`;
          });
          notifList.innerHTML = html;
        }
      })
      .catch(err => console.error(err));
  }

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

});

// ── Modals Logic ──────────────────────────────────────────────────────────
function openDynamicModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.style.display = 'flex';
    // Small delay to allow display:flex to apply before adding class for transition
    setTimeout(() => {
      modal.classList.add('is-active');
    }, 10);
    document.body.style.overflow = 'hidden';

    // Fetch data
    if (modalId === 'communityModal') {
      fetchCommunities();
    } else if (modalId === 'eventModal') {
      fetchEvents();
    }
  }
}

function closeDynamicModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('is-active');
    setTimeout(() => {
      modal.style.display = 'none';
    }, 300); // match CSS transition duration
    document.body.style.overflow = '';
  }
}

// Close modal on click outside
window.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    closeDynamicModal(e.target.id);
  }
});

function fetchCommunities() {
  const body = document.getElementById('communityModalBody');
  fetch('/api/recommendations/communities/')
    .then(res => res.json())
    .then(data => {
      if (data.communities.length === 0) {
        body.innerHTML = '<div style="text-align:center; padding: 2rem;">Henüz topluluk bulunmuyor.</div>';
        return;
      }
      let html = '';
      data.communities.forEach(c => {
        html += `<div class="dynamic-card">
                  <div class="dynamic-card-title">${c.name}</div>
                  <div class="dynamic-card-meta">
                    <span><i class="fa-solid fa-user-tie fa-xs"></i> ${c.director}</span>
                    <span><i class="fa-solid fa-users fa-xs"></i> ${c.member_count} Üye</span>
                    <span><i class="fa-solid fa-calendar-plus fa-xs"></i> ${c.founded_date}</span>
                  </div>
                  <div class="dynamic-card-desc">${c.description}</div>
                  <div style="margin-top: 1rem;">
                    <a href="/communities/${c.id}/" class="btn-sm btn-outline">Detayları Gör <i class="fa-solid fa-arrow-right fa-xs"></i></a>
                  </div>
                 </div>`;
      });
      body.innerHTML = html;
    })
    .catch(err => {
      body.innerHTML = '<div style="text-align:center; padding: 2rem; color: var(--danger);">Veri yüklenirken hata oluştu.</div>';
    });
}

function fetchEvents() {
  const body = document.getElementById('eventModalBody');
  fetch('/api/recommendations/events/')
    .then(res => res.json())
    .then(data => {
      if (data.events.length === 0) {
        body.innerHTML = '<div style="text-align:center; padding: 2rem;">Yaklaşan etkinlik bulunmuyor.</div>';
        return;
      }
      let html = '';
      data.events.forEach(e => {
        html += `<div class="dynamic-card">
                  <div class="dynamic-card-title">${e.title}</div>
                  <div class="dynamic-card-meta">
                    <span><i class="fa-solid fa-users fa-xs"></i> ${e.community}</span>
                    <span><i class="fa-solid fa-clock fa-xs"></i> ${e.date}</span>
                    <span><i class="fa-solid fa-location-dot fa-xs"></i> ${e.location_type}</span>
                  </div>
                  <div class="dynamic-card-desc">${e.description}</div>
                  <div style="margin-top: 1rem;">
                    <a href="/events/${e.id}/" class="btn-sm btn-outline">Etkinliğe Git <i class="fa-solid fa-arrow-right fa-xs"></i></a>
                  </div>
                 </div>`;
      });
      body.innerHTML = html;
    })
    .catch(err => {
      body.innerHTML = '<div style="text-align:center; padding: 2rem; color: var(--danger);">Veri yüklenirken hata oluştu.</div>';
    });
}
