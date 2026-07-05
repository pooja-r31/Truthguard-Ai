/* TruthGuard AI — Shared JS utilities */

// Smooth scroll-reveal on feature cards
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.feature-card, .kpi-card, .step-card, .chart-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // Animate KPI counter numbers
  document.querySelectorAll('.kpi-value, .hero-stat-num').forEach(el => {
    const target = parseFloat(el.textContent.replace(/[^0-9.]/g, ''));
    if (!isNaN(target) && target > 0) {
      animateCounter(el, target, el.textContent.includes('%'));
    }
  });
});

function animateCounter(el, target, isPercent) {
  const duration = 1200;
  const start    = performance.now();
  const startVal = 0;

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased    = 1 - Math.pow(1 - progress, 3);
    const current  = startVal + (target - startVal) * eased;
    el.textContent = (isPercent ? current.toFixed(1) + '%' : Math.round(current).toString());
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}
