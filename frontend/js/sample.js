/**
 * Sample Creation & Submission Handler (SIH26111)
 * Supports field measurements, optional lab assays, sensory checks, image upload, and demo pre-fills.
 */

document.addEventListener('DOMContentLoaded', () => {
  setupSampleForm();
  setupImageDropzone();
  setupDemoPresets();
});

function setupSampleForm() {
  const form = document.getElementById('sample-form');
  if (!form) return;

  // Set default sample date to today
  const dateInput = document.getElementById('sample_date');
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const alertBox = document.getElementById('sample-alert');
    const submitBtn = document.getElementById('submit-sample-btn');

    const formData = new FormData();

    // Required / Core Fields
    const sampleType = document.getElementById('sample_type').value;
    const sampleDate = document.getElementById('sample_date').value;
    formData.append('sample_type', sampleType);
    if (sampleDate) formData.append('sample_date', sampleDate);

    // Field-level Measurements
    appendIfValid(formData, 'ph', document.getElementById('ph').value);
    appendIfValid(formData, 'moisture', document.getElementById('moisture').value);
    appendIfValid(formData, 'temperature', document.getElementById('temperature').value);

    // Optional Lab Assays
    appendIfValid(formData, 'crude_protein', document.getElementById('crude_protein').value);
    appendIfValid(formData, 'ndf', document.getElementById('ndf').value);
    appendIfValid(formData, 'adf', document.getElementById('adf').value);
    appendIfValid(formData, 'ash', document.getElementById('ash').value);

    // Sensory & Visual
    const odor = document.getElementById('visual_odor').value;
    const color = document.getElementById('visual_color').value;
    if (odor) formData.append('visual_odor', odor);
    if (color) formData.append('visual_color', color);

    // Notes
    const notes = document.getElementById('notes').value.trim();
    if (notes) formData.append('notes', notes);

    // Image file
    const fileInput = document.getElementById('sample_image');
    if (fileInput && fileInput.files && fileInput.files[0]) {
      formData.append('image', fileInput.files[0]);
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '⏳ Processing Rapid Assessment...';
      showAlert(alertBox, 'Uploading sample measurements and running preliminary screening...', 'info');

      const result = await API.createSample(formData);

      showAlert(alertBox, '✅ Sample registered! Loading preliminary assessment report...', 'success');
      setTimeout(() => {
        window.location.href = `/result.html?id=${result.id}`;
      }, 600);
    } catch (err) {
      showAlert(alertBox, `Submission Error: ${err.message}`, 'danger');
      submitBtn.disabled = false;
      submitBtn.innerHTML = '🚀 Submit for Rapid Quality Screening';
    }
  });
}

function appendIfValid(formData, key, val) {
  if (val !== undefined && val !== null && val.trim() !== '') {
    const num = parseFloat(val);
    if (!isNaN(num)) {
      formData.append(key, num.toString());
    }
  }
}

function setupImageDropzone() {
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('sample_image');
  const previewContainer = document.getElementById('preview-container');
  const previewImg = document.getElementById('preview-img');
  const removeBtn = document.getElementById('remove-preview-btn');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      fileInput.files = e.dataTransfer.files;
      displayImagePreview(fileInput.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      displayImagePreview(fileInput.files[0]);
    }
  });

  if (removeBtn) {
    removeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      fileInput.value = '';
      previewContainer.style.display = 'none';
      dropzone.style.display = 'block';
    });
  }

  function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewContainer.style.display = 'block';
      dropzone.style.display = 'none';
    };
    reader.readAsDataURL(file);
  }
}

function setupDemoPresets() {
  const btnGood = document.getElementById('preset-good-silage');
  const btnSpoiled = document.getElementById('preset-spoiled-silage');
  const btnHay = document.getElementById('preset-green-fodder');

  if (btnGood) {
    btnGood.addEventListener('click', () => {
      fillForm({
        sample_type: 'Corn Silage',
        ph: '3.9',
        moisture: '65.0',
        temperature: '25.0',
        crude_protein: '8.4',
        ndf: '44.0',
        adf: '26.5',
        ash: '4.8',
        visual_odor: 'Pleasant / Fruity Acidic',
        visual_color: 'Olive Green / Light Brown',
        notes: 'DEMO PRE-FILL: Freshly opened bunker silo, compacted well with tractor roller. Favorable lactic aroma.'
      });
    });
  }

  if (btnSpoiled) {
    btnSpoiled.addEventListener('click', () => {
      fillForm({
        sample_type: 'Corn Silage',
        ph: '5.2',
        moisture: '74.0',
        temperature: '42.0',
        crude_protein: '7.1',
        ndf: '52.0',
        adf: '33.0',
        ash: '6.2',
        visual_odor: 'Vinegar / Sharp Acetic',
        visual_color: 'Dark Brown / Surface Mold',
        notes: 'DEMO PRE-FILL: Top section of bunker with torn polythene sheet and water infiltration. Aerobically heating.'
      });
    });
  }

  if (btnHay) {
    btnHay.addEventListener('click', () => {
      fillForm({
        sample_type: 'Green Fodder / Hay',
        ph: '',
        moisture: '16.0',
        temperature: '24.0',
        crude_protein: '11.5',
        ndf: '56.0',
        adf: '34.0',
        ash: '7.5',
        visual_odor: 'Sweet / Fresh Hay',
        visual_color: 'Light Green',
        notes: 'DEMO PRE-FILL: Sun-cured oat/berseem dry fodder bale. Checked for moisture before stacking in shed.'
      });
    });
  }
}

function fillForm(data) {
  for (const [key, val] of Object.entries(data)) {
    const el = document.getElementById(key);
    if (el) el.value = val;
  }
  const alertBox = document.getElementById('sample-alert');
  showAlert(alertBox, `✨ Loaded Demo Preset: "${data.sample_type}" (${data.visual_odor})`, 'info');
}

function showAlert(el, msg, type = 'info') {
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.innerHTML = msg;
  el.style.display = 'block';
}
