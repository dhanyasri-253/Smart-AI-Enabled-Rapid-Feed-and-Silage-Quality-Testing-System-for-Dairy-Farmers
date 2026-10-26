/**
 * Farmer Dashboard Logic (SIH26111)
 * Loads high-level metrics, recent samples, and real-time model status.
 */

document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData();
});

async function loadDashboardData() {
  const loadingEl = document.getElementById('dash-loading');
  const contentEl = document.getElementById('dash-content');

  try {
    if (loadingEl) loadingEl.style.display = 'block';
    if (contentEl) contentEl.style.display = 'none';

    const data = await API.getDashboard();

    // Welcome greeting
    const nameEl = document.getElementById('dash-farmer-name');
    if (nameEl) nameEl.innerText = data.farmer_name;

    // Metrics
    document.getElementById('metric-total').innerText = data.total_samples;
    document.getElementById('metric-silage').innerText = data.silage_samples;
    document.getElementById('metric-feed').innerText = data.feed_samples;
    document.getElementById('metric-attention').innerText = data.attention_needed;

    // Model Status Banner
    const modelStatus = data.model_status || {};
    const modelBadge = document.getElementById('dash-model-badge');
    if (modelBadge) {
      modelBadge.innerText = modelStatus.model_status || 'Not yet trained';
      if (modelStatus.model_loaded) {
        modelBadge.className = 'status-chip success';
      } else {
        modelBadge.className = 'status-chip neutral';
      }
    }

    // Recent Samples
    const tbody = document.getElementById('recent-samples-tbody');
    if (tbody) {
      tbody.innerHTML = '';
      if (!data.recent_samples || data.recent_samples.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:24px; color:var(--text-muted);">No samples tested yet. Click "New Sample Test" to begin.</td></tr>`;
      } else {
        data.recent_samples.forEach(s => {
          const tr = document.createElement('tr');
          const ph = s.ph !== null ? s.ph.toFixed(1) : '--';
          const moisture = s.moisture !== null ? `${s.moisture.toFixed(1)}%` : '--';
          const temp = s.temperature !== null ? `${s.temperature.toFixed(1)}°C` : '--';

          let statusBadge = `<span class="status-chip success">🟢 Acceptable</span>`;
          if (s.lab_recommended) {
            statusBadge = `<span class="status-chip warning">⚠️ Attention Needed</span>`;
          }

          tr.innerHTML = `
            <td><strong><a href="/result.html?id=${s.id}">${escapeHtml(s.sample_id)}</a></strong></td>
            <td>${escapeHtml(s.sample_type)}</td>
            <td>${escapeHtml(s.sample_date)}</td>
            <td style="font-family:monospace; font-size:0.82rem;">pH: ${ph} | M: ${moisture} | T: ${temp}</td>
            <td>${statusBadge}</td>
            <td><a href="/result.html?id=${s.id}" class="btn btn-secondary btn-sm">Report</a></td>
          `;
          tbody.appendChild(tr);
        });
      }
    }

    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'block';
  } catch (err) {
    if (loadingEl) loadingEl.style.display = 'none';
    console.error('Failed to load dashboard:', err);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
