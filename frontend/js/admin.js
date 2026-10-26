/**
 * Admin & Technical Diagnostics Logic (SIH26111)
 * Displays honest system verification and runs ML pipeline test dry-run.
 */

document.addEventListener('DOMContentLoaded', () => {
  loadAdminStatus();
  setupPipelineTestBtn();
});

async function loadAdminStatus() {
  try {
    const data = await API.getAdminStatus();

    document.getElementById('tech-problem').innerText = data.problem_statement;
    document.getElementById('tech-ministry').innerText = data.ministry;
    document.getElementById('tech-dataset-status').innerText = data.dataset_status;
    document.getElementById('tech-model-status').innerText = data.model_status;
    document.getElementById('tech-model-version').innerText = data.model_version;
    document.getElementById('tech-validation-status').innerText = data.validation_status;
    
    const dbInfo = data.active_database || {};
    document.getElementById('tech-database').innerText = 
      `${dbInfo.engine.toUpperCase()} (${dbInfo.database}) on ${dbInfo.host}:${dbInfo.port}`;

    const mlInfo = data.ml_pipeline || {};
    document.getElementById('tech-ml-loader').innerText = mlInfo.loader;
    document.getElementById('tech-ml-predictor').innerText = mlInfo.predictor;
    document.getElementById('tech-ml-path').innerText = mlInfo.target_model_file;
  } catch (err) {
    console.error('Failed to load admin status:', err);
  }
}

function setupPipelineTestBtn() {
  const testBtn = document.getElementById('run-test-pipeline-btn');
  const resultBox = document.getElementById('pipeline-test-result');

  if (!testBtn || !resultBox) return;

  testBtn.addEventListener('click', async () => {
    try {
      testBtn.disabled = true;
      testBtn.innerText = '⏳ Executing Pipeline Dry-Run...';

      const data = await API.testAdminPipeline();

      resultBox.style.display = 'block';
      resultBox.innerHTML = `
        <div style="background:#0f172a; color:#38bdf8; padding:16px; border-radius:8px; font-family:monospace; font-size:0.82rem; overflow-x:auto;">
          <div style="color:#4ade80; margin-bottom:8px; font-weight:bold;">✔ Pipeline Status: ${data.status}</div>
          <pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>
        </div>
      `;

      testBtn.disabled = false;
      testBtn.innerText = '✔ Re-run Pipeline Test';
    } catch (err) {
      resultBox.style.display = 'block';
      resultBox.innerHTML = `
        <div class="alert alert-danger">Dry-run test error: ${escapeHtml(err.message)}</div>
      `;
      testBtn.disabled = false;
      testBtn.innerText = 'Test ML Pipeline (Dry-Run)';
    }
  });
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
