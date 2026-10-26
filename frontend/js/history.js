/**
 * Sample History & Filtering (SIH26111)
 * Enables dairy farmers to review previous tests, search notes, filter by crop type, and inspect assessments.
 */

document.addEventListener('DOMContentLoaded', () => {
  setupHistoryFilters();
  loadSampleHistory();
});

let allSamples = [];

function setupHistoryFilters() {
  const searchInput = document.getElementById('search-input');
  const typeFilter = document.getElementById('type-filter');
  const attentionFilter = document.getElementById('attention-filter');

  if (searchInput) {
    searchInput.addEventListener('input', debounce(loadSampleHistory, 300));
  }
  if (typeFilter) {
    typeFilter.addEventListener('change', loadSampleHistory);
  }
  if (attentionFilter) {
    attentionFilter.addEventListener('change', loadSampleHistory);
  }
}

async function loadSampleHistory() {
  const tbody = document.getElementById('history-tbody');
  const countEl = document.getElementById('history-count');
  const loadingEl = document.getElementById('history-loading');

  const search = document.getElementById('search-input')?.value.trim();
  const sample_type = document.getElementById('type-filter')?.value;
  const attention_only = document.getElementById('attention-filter')?.checked;

  try {
    if (loadingEl) loadingEl.style.display = 'block';

    const samples = await API.getSamples({
      search: search || undefined,
      sample_type: sample_type !== 'All' ? sample_type : undefined,
      attention_only: attention_only || undefined
    });

    allSamples = samples;
    if (loadingEl) loadingEl.style.display = 'none';

    if (countEl) countEl.innerText = `${samples.length} sample(s) found`;

    if (!tbody) return;
    tbody.innerHTML = '';

    if (samples.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align:center; padding:36px; color:var(--text-muted);">
            No matching samples found. Click <strong>"New Sample Test"</strong> to register a feed or silage batch.
          </td>
        </tr>
      `;
      return;
    }

    samples.forEach(s => {
      const tr = document.createElement('tr');
      const phStr = s.ph !== null ? s.ph.toFixed(1) : '--';
      const moistStr = s.moisture !== null ? `${s.moisture.toFixed(1)}%` : '--';
      const tempStr = s.temperature !== null ? `${s.temperature.toFixed(1)}°C` : '--';

      let statusBadge = `<span class="status-chip success">🟢 Acceptable</span>`;
      if (s.lab_recommended) {
        statusBadge = `<span class="status-chip warning">⚠️ Attention / Lab Needed</span>`;
      }

      tr.innerHTML = `
        <td>
          <strong><a href="/result.html?id=${s.id}">${escapeHtml(s.sample_id)}</a></strong>
          ${s.image_path ? '<span title="Photo Attached">📷</span>' : ''}
        </td>
        <td>${escapeHtml(s.sample_type)}</td>
        <td>${escapeHtml(s.sample_date)}</td>
        <td>
          <div style="font-size:0.82rem; font-family:monospace;">
            pH: ${phStr} | M: ${moistStr} | T: ${tempStr}
          </div>
        </td>
        <td>${statusBadge}</td>
        <td>
          <span style="font-weight:700; color:var(--primary-dark);">
            ${s.quality_score !== null ? Math.round(s.quality_score) + '/100' : '--'}
          </span>
        </td>
        <td style="white-space:nowrap;">
          <a href="/result.html?id=${s.id}" class="btn btn-secondary btn-sm" style="margin-right:6px;">View Report</a>
          <button onclick="handleDeleteSample(${s.id}, '${escapeHtml(s.sample_id)}')" class="btn btn-secondary btn-sm" style="color:var(--danger);" title="Delete sample">🗑️</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    if (loadingEl) loadingEl.style.display = 'none';
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" style="color:var(--danger); text-align:center; padding:20px;">Failed to load history: ${escapeHtml(err.message)}</td></tr>`;
    }
  }
}

async function handleDeleteSample(id, code) {
  if (confirm(`Are you sure you want to delete sample "${code}"?`)) {
    try {
      await API.deleteSample(id);
      loadSampleHistory();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  }
}

function debounce(func, delay) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), delay);
  };
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
