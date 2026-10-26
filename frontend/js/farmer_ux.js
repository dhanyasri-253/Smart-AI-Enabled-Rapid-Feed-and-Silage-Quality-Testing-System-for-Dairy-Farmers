/**
 * SmartSilageAI - Farmer UX & Scientific Mode Controller (SIH26111)
 * Manages two user paths:
 *   A. Farmer Mode: Simple, guided multi-step form with everyday language, no lab report required.
 *   B. Scientific FQI Mode: Evaluates the frozen 11-feature RF pipeline without inventing tiers.
 * Full bilingual support (English / Tamil), accessibility, and touch-friendly controls.
 */

document.addEventListener('DOMContentLoaded', () => {
  initModeSwitcher();
  initFarmerWizard();
  initOptionTiles();
  initScientificForm();
  initLanguageToggle();
});

// State
const AppState = {
  currentMode: 'farmer', // 'farmer' | 'scientific'
  farmerStep: 1,
  totalFarmerSteps: 4,
  farmerData: {
    crop: 'Corn / Maize',
    harvest_timing: 'Recommended mid-milk line (50% grain dent, optimal moisture)',
    sealing_delay: 'Sealed quickly (within 0–4 hours of chopping)',
    storage_method: 'Silage Pit / Bunker Silo',
    inoculant_used: 'No inoculant used / None added',
    visible_mould: 'No mould visible / Clean forage',
    silage_color: 'Healthy olive green to golden/light brown',
    silage_odor: 'Pleasant, mildly acidic / fruity / yogurt-like (clean lactic)',
    temperature_feeling: 'Cool or normal ambient temperature',
    lab_report_available: false,
    ph: null,
    moisture: null,
    temperature: null,
    notes: '',
    save_sample: false
  },
  lastFarmerResult: null,
  lastSciResult: null
};

// -------------------------------------------------------------
// 1. Language Toggle Integration
// -------------------------------------------------------------
function initLanguageToggle() {
  const toggleBtns = document.querySelectorAll('.lang-toggle-btn');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      I18N.toggleLanguage();
      // Re-render results if already displayed
      if (AppState.lastFarmerResult) {
        renderFarmerResult(AppState.lastFarmerResult);
      }
      if (AppState.lastSciResult) {
        renderScientificResult(AppState.lastSciResult);
      }
    });
  });
}

// -------------------------------------------------------------
// 2. Mode Switcher (Farmer Mode vs Scientific Mode)
// -------------------------------------------------------------
function initModeSwitcher() {
  const tabFarmer = document.getElementById('tab-mode-farmer');
  const tabSci = document.getElementById('tab-mode-scientific');
  const farmerSection = document.getElementById('farmer-mode-section');
  const sciSection = document.getElementById('scientific-mode-section');
  const farmerResultBox = document.getElementById('farmer-result-panel');
  const sciResultBox = document.getElementById('scientific-result-panel');

  if (!tabFarmer || !tabSci) return;

  tabFarmer.addEventListener('click', () => switchMode('farmer'));
  tabSci.addEventListener('click', () => switchMode('scientific'));

  function switchMode(mode) {
    AppState.currentMode = mode;
    if (mode === 'farmer') {
      tabFarmer.classList.add('active');
      tabSci.classList.remove('active');
      farmerSection.style.display = 'block';
      sciSection.style.display = 'none';
      if (sciResultBox) sciResultBox.style.display = 'none';
    } else {
      tabSci.classList.add('active');
      tabFarmer.classList.remove('active');
      sciSection.style.display = 'block';
      farmerSection.style.display = 'none';
      if (farmerResultBox) farmerResultBox.style.display = 'none';
    }
    hideError();
  }
}

// -------------------------------------------------------------
// 3. Option Tiles (Large touch targets with checkmark)
// -------------------------------------------------------------
function initOptionTiles() {
  const groups = document.querySelectorAll('.option-cards-grid');
  groups.forEach(group => {
    const tiles = group.querySelectorAll('.option-tile');
    tiles.forEach(tile => {
      tile.addEventListener('click', () => {
        const radio = tile.querySelector('input[type="radio"]');
        if (radio) {
          radio.checked = true;
          tiles.forEach(t => t.classList.remove('selected'));
          tile.classList.add('selected');

          // Trigger change event on radio for listeners
          radio.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
    });
  });
}

// -------------------------------------------------------------
// 4. Farmer Mode Wizard (Steps 1 to 4)
// -------------------------------------------------------------
function initFarmerWizard() {
  const wizardForm = document.getElementById('farmer-wizard-form');
  const btnNext = document.getElementById('btn-wizard-next');
  const btnPrev = document.getElementById('btn-wizard-prev');
  const btnStartAgain = document.getElementById('btn-wizard-reset');
  const btnCancel = document.getElementById('btn-wizard-cancel');
  const progressBar = document.getElementById('wizard-progress-bar');
  const stepIndicators = document.querySelectorAll('.wizard-step');
  const stepPanels = document.querySelectorAll('.wizard-step-panel');

  if (!wizardForm) return;

  // Next Step / Submit Handler
  if (btnNext) {
    btnNext.addEventListener('click', async () => {
      if (AppState.farmerStep < AppState.totalFarmerSteps) {
        goToStep(AppState.farmerStep + 1);
      } else {
        // Final Step: Submit Farmer Mode
        await submitFarmerAssessment();
      }
    });
  }

  // Previous Step Handler
  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      if (AppState.farmerStep > 1) {
        goToStep(AppState.farmerStep - 1);
      }
    });
  }

  // Start Again Handler
  if (btnStartAgain) {
    btnStartAgain.addEventListener('click', () => {
      resetFarmerWizard();
    });
  }

  // Cancel Handler
  if (btnCancel) {
    btnCancel.addEventListener('click', () => {
      resetFarmerWizard();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // Allow clicking on completed or active step circles
  stepIndicators.forEach(stepBtn => {
    stepBtn.addEventListener('click', () => {
      const targetStep = parseInt(stepBtn.getAttribute('data-step'), 10);
      if (targetStep && targetStep <= AppState.totalFarmerSteps) {
        goToStep(targetStep);
      }
    });
  });

  function goToStep(step) {
    AppState.farmerStep = step;

    // Update Step Panels
    stepPanels.forEach(panel => {
      const panelStep = parseInt(panel.getAttribute('data-step'), 10);
      if (panelStep === step) {
        panel.style.display = 'block';
      } else {
        panel.style.display = 'none';
      }
    });

    // Update Progress Circles
    stepIndicators.forEach(indicator => {
      const indStep = parseInt(indicator.getAttribute('data-step'), 10);
      indicator.classList.remove('active', 'completed');
      if (indStep === step) {
        indicator.classList.add('active');
      } else if (indStep < step) {
        indicator.classList.add('completed');
      }
    });

    // Update Connecting Bar Width
    if (progressBar) {
      const pct = ((step - 1) / (AppState.totalFarmerSteps - 1)) * 100;
      progressBar.style.width = `${pct}%`;
    }

    // Update Buttons
    if (btnPrev) {
      btnPrev.style.display = step > 1 ? 'inline-flex' : 'none';
    }
    if (btnNext) {
      if (step === AppState.totalFarmerSteps) {
        btnNext.innerHTML = I18N.t('btnGetGuidance');
        btnNext.className = 'btn-wizard btn-wizard-next' ;
      } else {
        btnNext.innerHTML = I18N.t('btnNext');
        btnNext.className = 'btn-wizard btn-wizard-next';
      }
    }

    // Scroll gently to top of form card
    const card = document.getElementById('farmer-mode-section');
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function resetFarmerWizard() {
    wizardForm.reset();
    initOptionTiles();
    goToStep(1);
    const resultBox = document.getElementById('farmer-result-panel');
    if (resultBox) resultBox.style.display = 'none';
    hideError();
  }
}

// -------------------------------------------------------------
// 5. Submit Farmer Mode Assessment
// -------------------------------------------------------------
async function submitFarmerAssessment() {
  hideError();
  showLoading(I18N.t('loadingGuidance'));

  // Collect radio choices
  const getRadioVal = (name, fallback) => {
    const el = document.querySelector(`input[name="${name}"]:checked`);
    return el ? el.value : fallback;
  };

  const crop = getRadioVal('farmer_crop', 'Corn / Maize');
  const harvestTiming = getRadioVal('farmer_harvest', 'Recommended mid-milk line (50% grain dent, optimal moisture)');
  const delay = getRadioVal('farmer_delay', 'Sealed quickly (within 0–4 hours of chopping)');
  const storage = getRadioVal('farmer_storage', 'Silage Pit / Bunker Silo');
  const inoculant = getRadioVal('farmer_inoculant', 'No inoculant used / None added');
  const mould = getRadioVal('farmer_mould', 'No mould visible / Clean forage');
  const color = getRadioVal('farmer_color', 'Healthy olive green to golden/light brown');
  const odor = getRadioVal('farmer_odor', 'Pleasant, mildly acidic / fruity / yogurt-like (clean lactic)');
  const warmth = getRadioVal('farmer_warmth', 'Cool or normal ambient temperature');
  const hasLab = getRadioVal('farmer_has_lab', 'no') === 'yes';

  // Optional tool fields
  const phVal = document.getElementById('farmer_ph')?.value?.trim();
  const moistureVal = document.getElementById('farmer_moisture')?.value?.trim();
  const tempVal = document.getElementById('farmer_temp')?.value?.trim();
  const notesVal = document.getElementById('farmer_notes')?.value?.trim() || '';
  const saveSampleVal = document.getElementById('farmer_save_sample')?.checked || false;

  const payload = {
    crop,
    harvest_timing: harvestTiming,
    sealing_delay: delay,
    storage_method: storage,
    inoculant_used: inoculant,
    visible_mould: mould,
    silage_color: color,
    silage_odor: odor,
    temperature_feeling: warmth,
    lab_report_available: hasLab,
    ph: phVal ? parseFloat(phVal) : null,
    moisture: moistureVal ? parseFloat(moistureVal) : null,
    temperature: tempVal ? parseFloat(tempVal) : null,
    notes: notesVal,
    save_sample: saveSampleVal
  };

  try {
    const apiClient = (typeof window !== 'undefined' && window.API) ? window.API : (typeof API !== 'undefined' ? API : null);

    // Resilient safeguard: ensure getFarmerGuidance exists on apiClient even if an older cached api.js was retained by browser
    if (apiClient && typeof apiClient.getFarmerGuidance !== 'function') {
      apiClient.getFarmerGuidance = async function(p) {
        if (typeof this.request === 'function') {
          return this.request('/assessment/farmer-guidance', {
            method: 'POST',
            body: JSON.stringify(p)
          });
        }
        const token = (this.getToken && typeof this.getToken === 'function')
          ? this.getToken()
          : (typeof localStorage !== 'undefined' ? localStorage.getItem('smartsilage_token') : null);
        const resp = await fetch('/api/assessment/farmer-guidance', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          body: JSON.stringify(p)
        });
        const d = await resp.json().catch(() => null);
        if (!resp.ok) {
          throw new Error(d && d.detail ? (typeof d.detail === 'string' ? d.detail : JSON.stringify(d.detail)) : `HTTP Error ${resp.status}`);
        }
        return d;
      };
    }

    if (!apiClient || typeof apiClient.getFarmerGuidance !== 'function') {
      throw new Error("API client is unavailable. Please refresh your browser.");
    }

    const result = await apiClient.getFarmerGuidance(payload);
    hideLoading();
    if (!result || !result.summary) {
      throw new Error("Received empty or invalid guidance response from server.");
    }
    AppState.lastFarmerResult = result;
    renderFarmerResult(result);
  } catch (err) {
    hideLoading();
    showError("Farmer Guidance Error", err.message);
  }
}

// -------------------------------------------------------------
// 6. Render Farmer Guidance Result
// -------------------------------------------------------------
function renderFarmerResult(result) {
  const panel = document.getElementById('farmer-result-panel');
  if (!panel) return;

  const isTa = I18N.currentLang === 'ta';

  // Summary Table
  const summaryBox = document.getElementById('farmer-summary-content');
  if (summaryBox && result.summary) {
    summaryBox.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 0.85rem;">
        <div><strong>${isTa ? 'பயிர்' : 'Crop'}:</strong> ${escapeHtml(result.summary.crop)}</div>
        <div><strong>${isTa ? 'அறுவடை பருவம்' : 'Harvest Stage'}:</strong> ${escapeHtml(result.summary.harvest_timing)}</div>
        <div><strong>${isTa ? 'அடைப்பு தாமதம்' : 'Sealing Delay'}:</strong> ${escapeHtml(result.summary.sealing_delay)}</div>
        <div><strong>${isTa ? 'சேமிப்பு முறை' : 'Storage Method'}:</strong> ${escapeHtml(result.summary.storage_method)}</div>
        <div><strong>${isTa ? 'சேர்க்கை' : 'Inoculant'}:</strong> ${escapeHtml(result.summary.inoculant_used)}</div>
        <div><strong>${isTa ? 'தோற்றம்/பூஞ்சை' : 'Mould Observation'}:</strong> ${escapeHtml(result.summary.visible_mould)}</div>
        <div><strong>${isTa ? 'வாசனை' : 'Odor Profile'}:</strong> ${escapeHtml(result.summary.silage_odor)}</div>
        <div><strong>${isTa ? 'நிறம்' : 'Colour'}:</strong> ${escapeHtml(result.summary.silage_color)}</div>
      </div>
    `;
  }

  // Warning Signs List
  const warningList = document.getElementById('farmer-warnings-list');
  if (warningList) {
    warningList.innerHTML = '';
    const signs = result.warning_signs || [];
    signs.forEach(s => {
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
      warningList.appendChild(card);
    });
  }

  // Guidance List
  const guidanceList = document.getElementById('farmer-guidance-list');
  if (guidanceList) {
    guidanceList.innerHTML = '';
    const items = isTa ? result.guidance_ta : result.guidance_en;
    (items || []).forEach(step => {
      const div = document.createElement('div');
      div.style.cssText = 'display:flex; align-items:flex-start; gap:10px; margin-bottom:8px; font-size:0.88rem;';
      div.innerHTML = `
        <span style="color:#059669; font-weight:bold; font-size:1.1rem; line-height:1;">✔</span>
        <span>${escapeHtml(step)}</span>
      `;
      guidanceList.appendChild(div);
    });
  }

  // Lab Advisory
  const labBox = document.getElementById('farmer-lab-advisory-content');
  if (labBox) {
    const reasons = isTa ? result.lab_reasons_ta : result.lab_reasons_en;
    const referral = isTa ? result.referral_contacts_ta : result.referral_contacts_en;
    labBox.innerHTML = `
      <p style="font-size:0.86rem; color:#1e3a8a; margin-bottom:8px;">
        ${reasons && reasons.length ? reasons.join('<br>') : ''}
      </p>
      <div style="font-size:0.82rem; color:#1e40af; border-top:1px dashed #bfdbfe; padding-top:6px;">
        <strong>${isTa ? 'பரிந்துரைக்கப்படும் மையங்கள்' : 'Accredited referral testing centers'}:</strong> ${escapeHtml(referral)}
      </div>
    `;
  }

  // Non-ML Disclaimer Notice
  const disclaimerEl = document.getElementById('farmer-disclaimer-text');
  if (disclaimerEl) {
    disclaimerEl.textContent = isTa ? result.disclaimer_ta : result.disclaimer_en;
  }

  // Saved Sample Banner if applicable
  const saveNotice = document.getElementById('farmer-saved-notice');
  if (saveNotice) {
    if (result.sample_id) {
      saveNotice.style.display = 'block';
      saveNotice.innerHTML = `
        <span>✅</span>
        <span>${I18N.t('sampleSavedSuccess')} <strong>${escapeHtml(result.sample_id)}</strong></span>
        <a href="/history.html" style="margin-left:12px; color:#15803d; font-weight:700; text-decoration:underline;">
          ${isTa ? 'பதிவேட்டில் பார்க்கவும்' : 'View in History ➜'}
        </a>
      `;
    } else {
      saveNotice.style.display = 'none';
    }
  }

  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// -------------------------------------------------------------
// 7. Scientific FQI Mode Form & Prediction
// -------------------------------------------------------------
function initScientificForm() {
  const form = document.getElementById('scientific-fqi-form');
  const btnPredict = document.getElementById('btn-sci-predict');
  const btnReset = document.getElementById('btn-sci-reset');
  const btnFillPreset = document.getElementById('btn-sci-fill-preset');

  if (!form) return;

  // Typical research trial values
  const presetData = {
    sci_dm_f: 33.5,
    sci_cp_f: 8.2,
    sci_ash_f: 4.6,
    sci_wsc_f: 8.5,
    sci_starch_f: 29.0,
    sci_method: 'bags',
    sci_inhoculant: 'ho',
    sci_dose: 's',
    sci_delay: 'D0',
    sci_fao_class: 'ea',
    sci_maturity: 'mh'
  };

  if (btnFillPreset) {
    btnFillPreset.addEventListener('click', () => {
      for (const [id, val] of Object.entries(presetData)) {
        const el = document.getElementById(id);
        if (el) el.value = val;
      }
      hideError();
    });
  }

  if (btnReset) {
    btnReset.addEventListener('click', () => {
      form.reset();
      const resultBox = document.getElementById('scientific-result-panel');
      if (resultBox) resultBox.style.display = 'none';
      hideError();
    });
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    // Verify all 11 required features
    const numFields = [
      { id: 'sci_dm_f', name: 'Fresh Dry Matter (dm.f)' },
      { id: 'sci_cp_f', name: 'Crude Protein (cp.f)' },
      { id: 'sci_ash_f', name: 'Total Ash (ash.f)' },
      { id: 'sci_wsc_f', name: 'Water-Soluble Carbs (wsc.f)' },
      { id: 'sci_starch_f', name: 'Starch Content (starch.f)' }
    ];

    for (const f of numFields) {
      const el = document.getElementById(f.id);
      const val = el ? el.value.trim() : '';
      if (val === '' || isNaN(Number(val))) {
        showError(
          I18N.t('errFillAllML'),
          `${I18N.t('errMissingNum')} "${f.name}".`
        );
        if (el) el.focus();
        return;
      }
    }

    const payload = {
      'dm.f': parseFloat(document.getElementById('sci_dm_f').value),
      'cp.f': parseFloat(document.getElementById('sci_cp_f').value),
      'ash.f': parseFloat(document.getElementById('sci_ash_f').value),
      'wsc.f': parseFloat(document.getElementById('sci_wsc_f').value),
      'starch.f': parseFloat(document.getElementById('sci_starch_f').value),
      'method': document.getElementById('sci_method').value,
      'inhoculant': document.getElementById('sci_inhoculant').value,
      'dose': document.getElementById('sci_dose').value,
      'delay': document.getElementById('sci_delay').value,
      'fao.class': document.getElementById('sci_fao_class').value,
      'maturity': document.getElementById('sci_maturity').value
    };

    showLoading(I18N.t('loadingPredict'));

    try {
      const result = await API.predictFQI(payload);
      hideLoading();
      AppState.lastSciResult = { ...result, inputs: payload };
      renderScientificResult(AppState.lastSciResult);
    } catch (err) {
      hideLoading();
      showError("Scientific Prediction Failed", err.message);
    }
  });
}

// -------------------------------------------------------------
// 8. Render Scientific FQI Result (No fake tiers, honest limits)
// -------------------------------------------------------------
function renderScientificResult(result) {
  const panel = document.getElementById('scientific-result-panel');
  if (!panel) return;

  const isTa = I18N.currentLang === 'ta';

  // Numerical predicted score
  const scoreEl = document.getElementById('sci-fqi-value');
  if (scoreEl) {
    scoreEl.textContent = typeof result.predicted_fqi === 'number' 
      ? result.predicted_fqi.toFixed(2) 
      : result.predicted_fqi;
  }

  // Inputs table
  const tbody = document.getElementById('sci-inputs-tbody');
  if (tbody && result.inputs) {
    tbody.innerHTML = '';
    for (const [key, val] of Object.entries(result.inputs)) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="font-family:monospace; font-weight:700; color:#0f172a;">${escapeHtml(key)}</td>
        <td style="font-weight:600; color:#0369a1;">${escapeHtml(String(val))}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  // Research disclaimer
  const disclEl = document.getElementById('sci-disclaimer-text');
  if (disclEl) {
    disclEl.textContent = I18N.t('resSciDisclaimerBody');
  }

  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// -------------------------------------------------------------
// Utilities: Loading, Error, Escape
// -------------------------------------------------------------
function showLoading(msg) {
  const el = document.getElementById('app-loading-state');
  const txt = document.getElementById('app-loading-msg');
  if (txt && msg) txt.textContent = msg;
  if (el) el.style.display = 'block';
}

function hideLoading() {
  const el = document.getElementById('app-loading-state');
  if (el) el.style.display = 'none';
}

function showError(title, message) {
  const box = document.getElementById('app-error-box');
  const tEl = document.getElementById('app-error-title');
  const mEl = document.getElementById('app-error-message');
  if (tEl) tEl.textContent = title;
  if (mEl) mEl.textContent = message;
  if (box) {
    box.style.display = 'block';
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

function hideError() {
  const box = document.getElementById('app-error-box');
  if (box) box.style.display = 'none';
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
