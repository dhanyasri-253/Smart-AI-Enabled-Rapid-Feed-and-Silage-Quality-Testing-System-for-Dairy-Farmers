/**
 * Farmer Authentication & Session Handler (SIH26111)
 */

document.addEventListener('DOMContentLoaded', () => {
  setupNavbarAuth();
  setupLoginForm();
  setupRegisterForm();
  setupDemoQuickButtons();
});

function setupNavbarAuth() {
  const farmer = API.getFarmer();
  const authNavContainer = document.getElementById('nav-auth-slot');
  if (!authNavContainer) return;

  if (farmer) {
    authNavContainer.innerHTML = `
      <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:0.85rem; font-weight:600; color:var(--text-main);">
          👨‍🌾 ${escapeHtml(farmer.name)}
        </span>
        <button onclick="API.logout()" class="btn btn-secondary btn-sm" title="Log out">
          Logout
        </button>
      </div>
    `;
  } else {
    authNavContainer.innerHTML = `
      <a href="/login.html" class="btn btn-secondary btn-sm">Login</a>
      <a href="/register.html" class="btn btn-primary btn-sm">Register</a>
    `;
  }

  // Mobile menu toggle
  const mobileToggle = document.getElementById('mobile-toggle');
  const navLinks = document.getElementById('nav-links');
  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }
}

function setupLoginForm() {
  const form = document.getElementById('login-form');
  if (!form) return;

  const alertBox = document.getElementById('login-alert');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const mobile = document.getElementById('mobile').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('submit-btn');

    if (!mobile || !password) {
      showAlert(alertBox, 'Please enter both mobile number and password.', 'danger');
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Signing in...';
      const data = await API.login(mobile, password);

      API.setToken(data.access_token);
      API.setFarmer(data.farmer);

      showAlert(alertBox, 'Login successful! Redirecting to Dashboard...', 'success');
      setTimeout(() => {
        window.location.href = '/dashboard.html';
      }, 700);
    } catch (err) {
      showAlert(alertBox, err.message || 'Login failed. Please check credentials.', 'danger');
      submitBtn.disabled = false;
      submitBtn.innerText = 'Sign In to Account';
    }
  });
}

function setupRegisterForm() {
  const form = document.getElementById('register-form');
  if (!form) return;

  const alertBox = document.getElementById('register-alert');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const mobile = document.getElementById('mobile').value.trim();
    const email = document.getElementById('email').value.trim();
    const location = document.getElementById('location').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = document.getElementById('submit-btn');

    if (!name || !mobile || !password) {
      showAlert(alertBox, 'Name, mobile number, and password are required.', 'danger');
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = 'Creating account...';
      const data = await API.register(name, mobile, password, email, location);

      API.setToken(data.access_token);
      API.setFarmer(data.farmer);

      showAlert(alertBox, 'Farmer registered successfully! Redirecting...', 'success');
      setTimeout(() => {
        window.location.href = '/dashboard.html';
      }, 700);
    } catch (err) {
      showAlert(alertBox, err.message || 'Registration failed.', 'danger');
      submitBtn.disabled = false;
      submitBtn.innerText = 'Complete Farmer Registration';
    }
  });
}

function setupDemoQuickButtons() {
  const quickDemoBtn = document.getElementById('quick-demo-login-btn');
  if (quickDemoBtn) {
    quickDemoBtn.addEventListener('click', () => {
      const mobileInput = document.getElementById('mobile');
      const passInput = document.getElementById('password');
      if (mobileInput && passInput) {
        mobileInput.value = '9876543210';
        passInput.value = 'farmer123';
        const form = document.getElementById('login-form');
        if (form) form.dispatchEvent(new Event('submit'));
      }
    });
  }
}

function showAlert(el, msg, type = 'info') {
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.innerHTML = msg;
  el.style.display = 'block';
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
