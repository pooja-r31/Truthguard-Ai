/* TruthGuard AI — Canvas Chart helpers (no external dependencies) */

function drawActivityChart(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx  = canvas.getContext('2d');
  const W    = canvas.width;
  const H    = canvas.height;

  // Simulated 7-day data
  const days  = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const scans = [12, 19, 8, 24, 17, 31, 22];
  const fakes = [4, 7, 3, 10, 6, 13, 9];

  const maxVal = Math.max(...scans) + 5;
  const padL = 40, padR = 20, padT = 20, padB = 35;
  const chartW = W - padL - padR;
  const chartH = H - padT - padB;
  const step   = chartW / (days.length - 1);

  ctx.clearRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padT + (chartH / 4) * i;
    ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(W - padR, y); ctx.stroke();
    ctx.fillStyle = 'rgba(160,172,190,0.5)';
    ctx.font = '10px Inter, sans-serif';
    ctx.fillText(Math.round(maxVal - (maxVal / 4) * i), 4, y + 4);
  }

  // Draw total scans area
  const gradScans = ctx.createLinearGradient(0, padT, 0, H - padB);
  gradScans.addColorStop(0, 'rgba(79,158,255,0.4)');
  gradScans.addColorStop(1, 'rgba(79,158,255,0.0)');

  ctx.beginPath();
  scans.forEach((v, i) => {
    const x = padL + i * step;
    const y = padT + chartH - (v / maxVal) * chartH;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.lineTo(padL + (days.length - 1) * step, H - padB);
  ctx.lineTo(padL, H - padB);
  ctx.closePath();
  ctx.fillStyle = gradScans;
  ctx.fill();

  // Draw fakes area
  const gradFakes = ctx.createLinearGradient(0, padT, 0, H - padB);
  gradFakes.addColorStop(0, 'rgba(248,113,113,0.35)');
  gradFakes.addColorStop(1, 'rgba(248,113,113,0.0)');

  ctx.beginPath();
  fakes.forEach((v, i) => {
    const x = padL + i * step;
    const y = padT + chartH - (v / maxVal) * chartH;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.lineTo(padL + (days.length - 1) * step, H - padB);
  ctx.lineTo(padL, H - padB);
  ctx.closePath();
  ctx.fillStyle = gradFakes;
  ctx.fill();

  // Draw lines
  function drawLine(data, color) {
    ctx.beginPath();
    data.forEach((v, i) => {
      const x = padL + i * step;
      const y = padT + chartH - (v / maxVal) * chartH;
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
    });
    ctx.strokeStyle = color; ctx.lineWidth = 2.5;
    ctx.lineJoin = 'round'; ctx.stroke();
  }
  drawLine(scans, '#4f9eff');
  drawLine(fakes, '#f87171');

  // Dots
  function drawDots(data, color) {
    data.forEach((v, i) => {
      const x = padL + i * step;
      const y = padT + chartH - (v / maxVal) * chartH;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, Math.PI * 2);
      ctx.fillStyle = color; ctx.fill();
    });
  }
  drawDots(scans, '#4f9eff');
  drawDots(fakes, '#f87171');

  // X labels
  ctx.fillStyle = 'rgba(160,172,190,0.7)';
  ctx.font = '11px Inter, sans-serif';
  ctx.textAlign = 'center';
  days.forEach((d, i) => {
    ctx.fillText(d, padL + i * step, H - 8);
  });

  // Legend
  ctx.font = '11px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillStyle = '#4f9eff'; ctx.fillRect(padL, 5, 10, 10);
  ctx.fillStyle = '#e8edf5'; ctx.fillText('Total Scans', padL + 14, 14);
  ctx.fillStyle = '#f87171'; ctx.fillRect(padL + 90, 5, 10, 10);
  ctx.fillStyle = '#e8edf5'; ctx.fillText('Fakes Found', padL + 104, 14);
}

function drawBreakdownChart(canvasId, deepfakes, fakeNews, real) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;

  const data   = [deepfakes || 0, fakeNews || 0, real || 0];
  const colors = ['#f87171', '#fbbf24', '#34d399'];
  const labels = ['Deepfakes', 'Fake News', 'Authentic'];
  const total  = data.reduce((a, b) => a + b, 0) || 1;

  const cx = W / 2, cy = H / 2 - 15;
  const radius = Math.min(W, H) / 2.5;

  ctx.clearRect(0, 0, W, H);

  let startAngle = -Math.PI / 2;
  data.forEach((val, i) => {
    const slice = (val / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius, startAngle, startAngle + slice);
    ctx.closePath();
    ctx.fillStyle = colors[i];
    ctx.fill();
    ctx.strokeStyle = 'rgba(8,11,20,0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();
    startAngle += slice;
  });

  // Center hole effect
  ctx.beginPath();
  ctx.arc(cx, cy, radius * 0.55, 0, Math.PI * 2);
  ctx.fillStyle = '#0e1322';
  ctx.fill();

  // Center text
  ctx.fillStyle = '#e8edf5';
  ctx.font = 'bold 22px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(total, cx, cy - 6);
  ctx.font = '11px Inter, sans-serif';
  ctx.fillStyle = '#a0acbe';
  ctx.fillText('Total', cx, cy + 12);

  // Legend
  const legendY = H - 55;
  data.forEach((val, i) => {
    const lx = (W / 3) * i + 10;
    ctx.fillStyle = colors[i];
    ctx.fillRect(lx, legendY, 10, 10);
    ctx.fillStyle = '#a0acbe';
    ctx.font = '10px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(labels[i], lx + 14, legendY + 9);
    ctx.fillStyle = '#e8edf5';
    ctx.font = 'bold 11px Inter, sans-serif';
    ctx.fillText(val, lx + 14, legendY + 22);
  });
}
