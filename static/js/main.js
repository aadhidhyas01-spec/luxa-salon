/* ══════════════════════════════════════════
   LUXA SALON — Main JavaScript
══════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

    // ── SCROLL REVEAL ──────────────────────────────────────────
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -60px 0px' });

    document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

    // ── ANIMATED COUNTERS ──────────────────────────────────────
    function animateCount(el, target, suffix) {
        const duration = 1800;
        const step = 16;
        const increment = target / (duration / step);
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = Math.floor(current).toLocaleString() + suffix;
        }, step);
    }

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const raw = el.dataset.count;
                const suffix = el.dataset.suffix || '';
                animateCount(el, parseFloat(raw), suffix);
                counterObserver.unobserve(el);
            }
        });
    }, { threshold: 0.4 });

    document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));

    // ── STAT ITEMS (hero + stats section) ─────────────────────
    // Animate hero stat numbers
    document.querySelectorAll('.hero-stat-number').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(10px)';
        setTimeout(() => {
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 1200);
    });

    // ── SALON CARD HOVER DEPTH ─────────────────────────────────
    document.querySelectorAll('.salon-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.zIndex = '10';
        });
        card.addEventListener('mouseleave', () => {
            card.style.zIndex = '';
        });
    });

    // ── TAB SWITCHING (salon detail) ───────────────────────────
    window.switchTab = function (evt, tabId) {
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        const el = document.getElementById(tabId);
        if (el) el.classList.add('active');
        evt.currentTarget.classList.add('active');
    };

    // ── STAR RATING INTERACTION ────────────────────────────────
    const ratingInputs = document.querySelectorAll('.star-rating-select input');
    const ratingLabels = document.querySelectorAll('.star-rating-select label');

    ratingInputs.forEach(input => {
        input.addEventListener('change', () => {
            const val = parseInt(input.value);
            ratingLabels.forEach((label, idx) => {
                // Labels are in reverse order (5, 4, 3, 2, 1)
                const labelVal = 5 - idx;
                label.style.color = labelVal <= val ? 'var(--primary)' : 'var(--text-muted)';
            });
        });
    });

    // ── FORM CONTROL FOCUS EFFECTS ─────────────────────────────
    document.querySelectorAll('.form-control').forEach(input => {
        const group = input.closest('.form-group');
        if (!group) return;

        input.addEventListener('focus', () => {
            group.style.transform = 'translateY(-1px)';
            group.style.transition = 'transform 0.2s ease';
        });

        input.addEventListener('blur', () => {
            group.style.transform = 'translateY(0)';
        });
    });

    // ── SMOOTH PAGE LOAD ───────────────────────────────────────
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease';
    requestAnimationFrame(() => {
        document.body.style.opacity = '1';
    });

    // ── BOOKING: STYLIST CARD SELECTION ───────────────────────
    document.querySelectorAll('.stylist-option-label').forEach(label => {
        const input = label.querySelector('input[type=radio]');
        if (!input) return;
        label.addEventListener('click', () => {
            document.querySelectorAll('.stylist-option-label').forEach(l => {
                l.style.borderColor = 'var(--border-light)';
                l.style.background = 'var(--bg-card)';
            });
            label.style.borderColor = 'var(--primary)';
            label.style.background = 'var(--primary-dim)';
        });
    });

    // ── NEIGHBORHOOD CARD HOVER PARALLAX ──────────────────────
    document.querySelectorAll('.neighborhood-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width - 0.5) * 8;
            const y = ((e.clientY - rect.top) / rect.height - 0.5) * 8;
            card.style.transform = `perspective(500px) rotateX(${-y}deg) rotateY(${x}deg) translateY(-4px)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    // ── FLASH MESSAGE CLOSE ────────────────────────────────────
    document.querySelectorAll('.close-alert').forEach(btn => {
        btn.addEventListener('click', () => {
            const alert = btn.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(20px)';
                setTimeout(() => alert.remove(), 300);
            }
        });
    });

});
