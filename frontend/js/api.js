/**
 * SmartSilageAI - Centralized API Service (SIH26111)
 * Handles HTTP requests, JWT/Bearer token management, and error handling.
 */

const API_BASE = '/api';

const API = {
  // Token Storage Helpers
  getToken() {
    return localStorage.getItem('smartsilage_token');
  },
  
  setToken(token) {
    localStorage.setItem('smartsilage_token', token);
  },

  getFarmer() {
    const raw = localStorage.getItem('smartsilage_farmer');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setFarmer(farmerObj) {
    localStorage.setItem('smartsilage_farmer', JSON.stringify(farmerObj));
  },

  logout() {
    localStorage.removeItem('smartsilage_token');
    localStorage.removeItem('smartsilage_farmer');
    window.location.href = '/login.html';
  },

  // HTTP Request Wrapper
  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = options.headers || {};

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // If payload is not FormData, set JSON content type
    if (options.body && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = data && data.detail ? data.detail : `HTTP Error ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async register(name, mobile, password, email = '', location = '') {
    return this.request('/register', {
      method: 'POST',
      body: JSON.stringify({ name, mobile, password, email, location })
    });
  },

  async login(mobile, password) {
    return this.request('/login', {
      method: 'POST',
      body: JSON.stringify({ mobile, password })
    });
  },

  async getProfile() {
    return this.request('/me');
  },

  // Sample Endpoints
  async createSample(formData) {
    return this.request('/samples', {
      method: 'POST',
      body: formData // Must be FormData for file attachment
    });
  },

  async getSamples(params = {}) {
    const query = new URLSearchParams();
    if (params.sample_type) query.append('sample_type', params.sample_type);
    if (params.search) query.append('search', params.search);
    if (params.attention_only) query.append('attention_only', 'true');
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/samples${qs}`);
  },

  async getSampleDetail(idOrCode) {
    return this.request(`/samples/${idOrCode}`);
  },

  async deleteSample(id) {
    return this.request(`/samples/${id}`, {
      method: 'DELETE'
    });
  },

  // Assessment Endpoints
  async rerunAssessment(sampleId) {
    return this.request('/assessment', {
      method: 'POST',
      body: JSON.stringify({ sample_id: sampleId })
    });
  },

  async getFarmerGuidance(payload) {
    return this.request('/assessment/farmer-guidance', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Scientific ML Prediction Endpoint (Frozen 11-feature RF pipeline)
  async predictFQI(payload) {
    // Hits POST /predict directly or /api/predict
    const url = window.location.origin ? (window.location.origin + '/predict') : '/predict';
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    const data = await response.json().catch(() => null);
    if (!response.ok) {
      let msg = `HTTP ${response.status}`;
      if (data && data.detail) {
        if (typeof data.detail === 'string') {
          msg = data.detail;
        } else if (Array.isArray(data.detail)) {
          msg = data.detail
            .map(d => {
              const loc = d.loc ? d.loc.filter(x => x !== 'body').join('.') : 'Parameter';
              return `${loc}: ${d.msg}`;
            })
            .join('; ');
        } else {
          msg = JSON.stringify(data.detail);
        }
      }
      throw new Error(msg);
    }
    return data;
  },

  // Dashboard & Admin
  async getDashboard() {
    return this.request('/dashboard');
  },

  async getAdminStatus() {
    return this.request('/admin/status');
  },

  async testAdminPipeline() {
    return this.request('/admin/test-pipeline', {
      method: 'POST'
    });
  }
};

// Expose API globally on window and globalThis for all browser scripts and event handlers
if (typeof window !== 'undefined') {
  window.API = API;
}
if (typeof globalThis !== 'undefined') {
  globalThis.API = API;
}


