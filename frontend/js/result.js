/**
 * Assessment Result & Explainable Quality Analysis (SIH26111)
 * Renders sample metadata, honest prototype disclaimers, explainable parameter indicators,
 * warning signs for Farmer Mode, practical recommendations, and certified laboratory referral guidelines.
 */

let currentSampleData = null;

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const sampleId = urlParams.get('id');

  // Setup language button
  const langBtn = document.getElementById('result-lang-btn');
  if (langBtn) {
    langBtn.addEventListener('click', () => {
      I18N.toggleLanguage();
      if (currentSampleData) {
        renderAll(currentSampleData);
      }
    });
  }

  if (!sampleId) {
    showErrorState('No Sample ID specified. Please select a sample from History or Dashboard.');
    return;
  }

  await loadSampleResult(sampleId);
});

async function loadSampleResult(sampleId) {
  const loadingEl = document.getElementById('loading-state');
  const contentEl = document.getElementById('result-content');

  try {
    if (loadingEl) loadingEl.style.display = 'block';
    if (contentEl) contentEl.style.display = 'none';

    const sample = await API.getSampleDetail(sampleId);
    currentSampleData = sample;

    renderAll(sample);

    if (loadingEl) loadingEl.style.display = 'none';
    if (contentEl) contentEl.style.display = 'block';
  } catch (err) {
    if (loadingEl) loadingEl.style.display = 'none';
    showErrorState(`Unable to load sample assessment: ${err.message}`);
  }
}

function renderAll(sample) {
  renderSampleHeader(sample);
  renderAssessmentDetails(sample);
  renderWarningSignsOrIndicators(sample);
  renderRecommendations(sample);
}

function renderSampleHeader(sample) {
  const isTa = I18N.currentLang === 'ta';
  document.getElementById('res-sample-id').innerText = sample.sample_id;
  document.getElementById('res-sample-type').innerText = sample.sample_type;
  document.getElementById('res-sample-date').innerText = sample.sample_date;
  
  const notesEl = document.getElementById('res-sample-notes');
  if (notesEl) {
    notesEl.innerText = sample.notes || (isTa ? 'குறிப்புகள் எதுவும் இல்லை.' : 'No field notes provided.');
  }

  // Sample Image
  const imgBox = document.getElementById('res-image-box');
  const imgEl = document.getElementById('res-sample-img');
  if (imgBox && imgEl) {
    if (sample.image_path) {
      imgEl.src = sample.image_path;
      imgBox.style.display = 'block';
    } else {
      imgBox.style.display = 'none';
    }
  }
}

function renderAssessmentDetails(sample) {
  const assessment = sample.assessment;
  if (!assessment) return;

  const isTa = I18N.currentLang === 'ta';
  const breakdown = assessment.parameter_breakdown || {};
  const isFarmerMode = assessment.quality_category?.includes('Farmer Mode') || breakdown.mode === 'farmer_guided';

  // Badge Type
  const badgeType = document.getElementById('res-badge-type');
  if (badgeType) {
    if (isFarmerMode) {
      badgeType.innerText = isTa ? 'விவசாயி முறை வழிகாட்டுதல்' : 'Farmer Mode Screening Dossier';
      badgeType.style.background = '#dcfce7';
      badgeType.style.color = '#15803d';
    } else {
      badgeType.innerText = isTa ? 'பூர்வாங்க ஆய்வு அறிக்கை' : 'Preliminary Screening Dossier';
      badgeType.style.background = '#e0f2fe';
      badgeType.style.color = '#0369a1';
    }
  }

  // Status Category
  const catEl = document.getElementById('res-quality-category');
  if (catEl) {
    catEl.innerText = assessment.quality_category;
  }

  // Preliminary Field Tier
  const tierEl = document.getElementById('res-preliminary-tier');
  if (tierEl) {
    const tier = breakdown.preliminary_field_tier || (isFarmerMode ? (isTa ? 'விவசாயி வழிகாட்டுதல் நிறைவுற்றது' : 'Rule-Based Agronomic Screening') : 'Preliminary Screening Completed');
    tierEl.innerText = tier;
    tierEl.className = 'assessment-tier';
    if (tier.includes('Acceptable') || tier.includes('Agronomic')) {
      tierEl.classList.add('tier-acceptable');
    } else if (tier.includes('Caution') || tier.includes('Attention')) {
      tierEl.classList.add('tier-caution');
    } else {
      tierEl.classList.add('tier-spoilage');
    }
  }

  // Score
  const scoreCard = document.getElementById('res-score-card');
  const scoreEl = document.getElementById('res-quality-score');
  const scoreLabel = document.getElementById('res-score-label');
  const scoreScale = document.getElementById('res-score-scale');
  if (scoreEl && scoreCard) {
    if (assessment.quality_score !== null && !isNaN(assessment.quality_score)) {
      scoreEl.innerText = Math.round(assessment.quality_score);
      if (scoreLabel) scoreLabel.innerText = isTa ? 'பூர்வாங்க குறியீடு' : 'Preliminary Index';
      if (scoreScale) scoreScale.innerText = isTa ? 'அளவு: 0 - 100' : 'Scale: 0 to 100';
    } else {
      scoreEl.innerText = 'N/A';
      scoreEl.style.fontSize = '1.8rem';
      if (scoreLabel) scoreLabel.innerText = isTa ? 'விவசாயி முறை' : 'Farmer Mode';
      if (scoreScale) scoreScale.innerText = isTa ? 'ஆய்வக அறிக்கை இல்லை' : 'No Lab Report (Non-ML)';
    }
  }

  // Engine
  const modelEl = document.getElementById('res-model-version');
  if (modelEl) {
    modelEl.innerText = assessment.model_version || 'Heuristic-v1.0';
  }

  // Confidence / Validation Basis
  const confEl = document.getElementById('res-confidence');
  if (confEl) {
    confEl.innerText = assessment.confidence || 'Field Reference Screening';
  }

  // Disclaimer update
  const disclTitle = document.getElementById('res-disclaimer-title');
  const disclBody = document.getElementById('res-disclaimer-body');
  if (disclTitle && disclBody) {
    if (isFarmerMode) {
      disclTitle.innerText = isTa ? 'முக்கிய பாதுகாப்பு மற்றும் அறிவியல் அறிவிப்பு' : 'Important Health & Scientific Notice';
      disclBody.innerText = isTa 
        ? (breakdown.disclaimer_ta || I18N.t('resDisclaimerBody'))
        : (breakdown.disclaimer_en || I18N.t('resDisclaimerBody'));
    }
  }
}

function renderWarningSignsOrIndicators(sample) {
  const isTa = I18N.currentLang === 'ta';
  const breakdown = (sample.assessment && sample.assessment.parameter_breakdown) || {};
  const isFarmerMode = breakdown.mode === 'farmer_guided' || (breakdown.warning_signs && breakdown.warning_signs.length > 0);

  const warningsSection = document.getElementById('res-warning-signs-section');
  const warningsList = document.getElementById('res-warning-signs-list');
  const indicatorsCard = document.getElementById('res-indicators-card');
  const tableBody = document.getElementById('indicators-tbody');

  if (isFarmerMode && breakdown.warning_signs) {
    // Render Warning Signs Cards
    if (warningsSection && warningsList) {
      warningsSection.style.display = 'block';
      warningsList.innerHTML = '';
      breakdown.warning_signs.forEach(s => {
        const card = document.createElement('div');
        card.className = `warning-card ${s.severity}`;
        const title = isTa ? (s.title_ta || s.title) : s.title;
        const desc = isTa ? (s.description_ta || s.description) : s.description;
        const cat = isTa ? (s.category_ta || s.category) : s.category;

        let icon = '🟢';
        if (s.severity === 'warning') icon = '🟡';
        if (s.severity === 'danger') icon = '🔴';

        card.innerHTML = `
          <div class="warning-card-header">
            <span class="warning-card-title">${icon} ${escapeHtml(title)}</span>
            <span style="font-size:0.72rem; font-weight:700; color:#64748b; text-transform:uppercase;">${escapeHtml(cat)}</span>
          </div>
          <p class="warning-card-desc">${escapeHtml(desc)}</p>
        `;
        warningsList.appendChild(card);
      });
    }

    // Hide or simplify indicators card if no numerical indicators
    if (indicatorsCard && (!breakdown.indicators || breakdown.indicators.length === 0)) {
      indicatorsCard.style.display = 'none';
    }
  } else {
    // Render Indicators Table
    if (warningsSection) warningsSection.style.display = 'none';
    if (indicatorsCard) indicatorsCard.style.display = 'block';

    if (tableBody) {
      tableBody.innerHTML = '';
      const indicators = breakdown.indicators || [];
      if (indicators.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:20px;">No numerical parameters recorded for this sample.</td></tr>`;
        return;
      }

      indicators.forEach(ind => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>
            <strong>${escapeHtml(ind.parameter)}</strong>
            <div style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(ind.category)}</div>
          </td>
          <td><strong>${escapeHtml(ind.measured_value)}</strong></td>
          <td><span style="color:var(--text-muted); font-size:0.85rem;">${escapeHtml(ind.reference_target)}</span></td>
          <td>
            <span class="status-chip ${ind.severity}">
              ${getStatusIcon(ind.severity)} ${escapeHtml(ind.status)}
            </span>
          </td>
          <td style="font-size:0.84rem; color:#334155; max-width:280px;">${escapeHtml(ind.explanation)}</td>
        `;
        tableBody.appendChild(tr);
      });
    }
  }
}

function renderRecommendations(sample) {
  const isTa = I18N.currentLang === 'ta';
  const container = document.getElementById('recommendations-list');
  if (!container) return;

  container.innerHTML = '';
  const breakdown = (sample.assessment && sample.assessment.parameter_breakdown) || {};
  let recs = [];

  if (isTa && breakdown.guidance_ta && breakdown.guidance_ta.length > 0) {
    recs = breakdown.guidance_ta;
  } else if (breakdown.guidance_en && breakdown.guidance_en.length > 0) {
    recs = breakdown.guidance_en;
  } else {
    recs = breakdown.recommendations || [];
  }

  if (recs.length === 0) {
    container.innerHTML = `<p style="font-size:0.88rem; color:var(--text-muted);">${isTa ? 'சிறப்பு நடவடிக்கைகள் எதுவும் கொடியிடப்படவில்லை. நல்ல தீவன நடைமுறைகளைப் பராமரிக்கவும்.' : 'No specific actions flagged. Maintain standard good feeding practices.'}</p>`;
    return;
  }

  recs.forEach(rec => {
    const item = document.createElement('div');
    item.className = 'recommendation-item';
    item.innerHTML = `
      <span class="rec-bullet">✔</span>
      <span>${escapeHtml(rec)}</span>
    `;
    container.appendChild(item);
  });

  // Lab Advisory
  const labBox = document.getElementById('lab-advisory-box');
  const labText = document.getElementById('lab-advisory-text');
  if (labBox && labText) {
    const reasons = isTa ? breakdown.lab_reasons_ta : breakdown.lab_reasons_en;
    const referral = isTa ? breakdown.referral_contacts_ta : breakdown.referral_contacts_en;

    if (reasons && reasons.length) {
      labBox.style.display = 'block';
      labText.innerHTML = `
        <p style="margin-bottom:8px;">${reasons.join('<br>')}</p>
        ${referral ? `<div style="font-size:0.82rem; color:#1e40af; border-top:1px dashed #bfdbfe; padding-top:6px;"><strong>${isTa ? 'பரிந்துரைக்கப்படும் மையங்கள்' : 'Accredited referral testing centers'}:</strong> ${escapeHtml(referral)}</div>` : ''}
      `;
    } else if (sample.assessment && sample.assessment.lab_recommended) {
      labBox.style.display = 'block';
      labText.innerHTML = `
        <strong>Action Needed:</strong> One or more measured parameters in this sample diverge from the optimal scientific baseline.
        To confirm nutritional adequacy and eliminate mycotoxin risk, please dispatch a 500g composite sample to an accredited 
        <strong>Krishi Vigyan Kendra (KVK)</strong>, State Animal Husbandry Laboratory, or Dairy Cooperative testing cell.
      `;
    } else {
      labBox.style.display = 'block';
      labText.innerHTML = `
        <strong>Routine Monitoring:</strong> This preliminary screening reflects favorable field metrics. However, for precise ration balancing in high-yielding dairy herds, periodic proximate wet-chemistry analysis remains recommended.
      `;
    }
  }
}

function getStatusIcon(severity) {
  if (severity === 'success') return '🟢';
  if (severity === 'warning') return '🟡';
  if (severity === 'danger') return '🔴';
  return '⚪';
}

function showErrorState(msg) {
  const contentEl = document.getElementById('result-content');
  const errorEl = document.getElementById('error-state');
  if (contentEl) contentEl.style.display = 'none';
  if (errorEl) {
    errorEl.style.display = 'block';
    errorEl.innerHTML = `
      <div class="card" style="text-align:center; padding:40px;">
        <h3 style="color:var(--danger); margin-bottom:10px;">Notice</h3>
        <p style="color:var(--text-muted); margin-bottom:20px;">${escapeHtml(msg)}</p>
        <a href="/history.html" class="btn btn-primary">Browse Sample History</a>
      </div>
    `;
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
