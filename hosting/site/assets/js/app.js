/* ============================================
   EchoSmart — Main Application JS
   ============================================ */

const APP = {
  API_BASE: '/api',
  TOKEN_KEY: 'echosmart_token',
  USER_KEY: 'echosmart_user',
};

/* ---------- SVG Logo ---------- */
const LOGO_SVG = `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="16" cy="16" r="6" fill="#00E676"/>
  <path d="M16 4a12 12 0 0 1 12 12" stroke="#00E676" stroke-width="2" stroke-linecap="round" opacity=".7"/>
  <path d="M16 8a8 8 0 0 1 8 8" stroke="#00E676" stroke-width="2" stroke-linecap="round" opacity=".5"/>
  <path d="M16 24a12 12 0 0 1-12-12" stroke="#00E676" stroke-width="2" stroke-linecap="round" opacity=".3"/>
</svg>`;

/* ---------- API Helper ---------- */
async function apiCall(endpoint, data = null, method = 'POST') {
  const token = localStorage.getItem(APP.TOKEN_KEY);
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };
  if (data && method !== 'GET') {
    options.body = JSON.stringify(data);
  }

  const url = endpoint.startsWith('http') ? endpoint : `${APP.API_BASE}/${endpoint}`;

  try {
    const res = await fetch(url, options);
    const json = await res.json();
    if (!res.ok) throw new Error(json.error || json.message || 'Error del servidor');
    return json;
  } catch (err) {
    if (err.message === 'Failed to fetch') {
      throw new Error('No se pudo conectar al servidor');
    }
    throw err;
  }
}

/* ---------- Auth Functions ---------- */
async function login(email, password) {
  const data = await apiCall('auth.php', { action: 'login', email, password });
  if (data.token) {
    localStorage.setItem(APP.TOKEN_KEY, data.token);
    if (data.user) localStorage.setItem(APP.USER_KEY, JSON.stringify(data.user));
  }
  return data;
}

async function register(payload) {
  const data = await apiCall('auth.php', { action: 'register', ...payload });
  if (data.token) {
    localStorage.setItem(APP.TOKEN_KEY, data.token);
    if (data.user) localStorage.setItem(APP.USER_KEY, JSON.stringify(data.user));
  }
  return data;
}

async function logout() {
  try {
    await apiCall('auth.php', { action: 'logout' });
  } catch (_) { /* ignore */ }
  localStorage.removeItem(APP.TOKEN_KEY);
  localStorage.removeItem(APP.USER_KEY);
  window.location.href = 'login.html';
}

async function checkAuth() {
  const token = localStorage.getItem(APP.TOKEN_KEY);
  if (!token) return null;
  try {
    const data = await apiCall('auth.php', { action: 'me' });
    if (data.user) localStorage.setItem(APP.USER_KEY, JSON.stringify(data.user));
    return data.user || data;
  } catch (_) {
    return null;
  }
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem(APP.USER_KEY));
  } catch (_) { return null; }
}

function requireAuth() {
  const token = localStorage.getItem(APP.TOKEN_KEY);
  if (!token) {
    window.location.href = 'login.html';
    return false;
  }
  checkAuth().then(user => {
    if (!user) {
      localStorage.removeItem(APP.TOKEN_KEY);
      localStorage.removeItem(APP.USER_KEY);
      window.location.href = 'login.html';
    }
  });
  return true;
}

/* ---------- UI Helpers ---------- */
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || ''}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(40px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function showLoading() {
  if (document.getElementById('loading-overlay')) return;
  const overlay = document.createElement('div');
  overlay.id = 'loading-overlay';
  overlay.className = 'loading-overlay';
  overlay.innerHTML = '<div class="spinner"></div>';
  document.body.appendChild(overlay);
}

function hideLoading() {
  const el = document.getElementById('loading-overlay');
  if (el) el.remove();
}

/* ---------- Navigation ---------- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        closeMobileMenu();
      }
    });
  });
}

function initMobileMenu() {
  const btn = document.getElementById('mobile-menu-btn');
  const menu = document.getElementById('mobile-menu');
  if (!btn || !menu) return;

  const iconMenu = btn.querySelector('.icon-menu');
  const iconClose = btn.querySelector('.icon-close');

  btn.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('active');
    btn.setAttribute('aria-expanded', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
    if (iconMenu && iconClose) {
      iconMenu.style.display = isOpen ? 'none' : 'block';
      iconClose.style.display = isOpen ? 'block' : 'none';
    }
  });

  menu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', closeMobileMenu);
  });
}

function closeMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  const btn = document.getElementById('mobile-menu-btn');
  if (menu) menu.classList.remove('active');
  if (btn) {
    btn.setAttribute('aria-expanded', 'false');
    const iconMenu = btn.querySelector('.icon-menu');
    const iconClose = btn.querySelector('.icon-close');
    if (iconMenu) iconMenu.style.display = 'block';
    if (iconClose) iconClose.style.display = 'none';
  }
  document.body.style.overflow = '';
}

/* ---------- Form Handlers ---------- */
function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));

    if (!data.name || !data.email || !data.message) {
      showToast('Por favor completa todos los campos requeridos', 'error');
      return;
    }

    try {
      showLoading();
      await apiCall('contact.php', data);
      showToast('Mensaje enviado correctamente', 'success');
      form.reset();
    } catch (err) {
      showToast(err.message || 'Error al enviar el mensaje', 'error');
    } finally {
      hideLoading();
    }
  });
}

function initLoginForm() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = form.querySelector('[name="email"]').value.trim();
    const password = form.querySelector('[name="password"]').value;

    clearErrors(form);

    if (!email) return setError(form, 'email', 'El correo es requerido');
    if (!isValidEmail(email)) return setError(form, 'email', 'Correo inválido');
    if (!password) return setError(form, 'password', 'La contraseña es requerida');

    try {
      showLoading();
      await login(email, password);
      window.location.href = 'dashboard.html';
    } catch (err) {
      showToast(err.message || 'Credenciales incorrectas', 'error');
    } finally {
      hideLoading();
    }
  });
}

function initForgotPasswordForm() {
  const form = document.getElementById('forgot-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = form.querySelector('[name="email"]').value.trim();

    if (!email || !isValidEmail(email)) {
      showToast('Ingresa un correo electrónico válido', 'error');
      return;
    }

    try {
      showLoading();
      await apiCall('auth.php', { action: 'forgot-password', email });
      showToast('Se ha enviado un enlace de recuperación a tu correo', 'success');
    } catch (err) {
      showToast(err.message || 'Error al procesar la solicitud', 'error');
    } finally {
      hideLoading();
    }
  });
}

/* ---------- Register Steps ---------- */
function initRegisterForm() {
  const form = document.getElementById('register-form');
  if (!form) return;

  let currentStep = 1;

  window.nextStep = function () {
    if (currentStep === 1) {
      const serial = form.querySelector('[name="serial_number"]').value.trim();
      if (!validateSerial(serial)) {
        setError(form, 'serial_number', 'Formato inválido. Usa ES-YYYYMM-XXXX (ej: ES-202601-A1B2)');
        return;
      }
      clearErrors(form);
    }

    if (currentStep === 2) {
      const name = form.querySelector('[name="name"]').value.trim();
      const email = form.querySelector('[name="email"]').value.trim();
      const password = form.querySelector('[name="password"]').value;
      const confirm = form.querySelector('[name="password_confirm"]').value;

      clearErrors(form);
      if (!name) return setError(form, 'name', 'El nombre es requerido');
      if (!email || !isValidEmail(email)) return setError(form, 'email', 'Correo inválido');
      if (password.length < 8) return setError(form, 'password', 'Mínimo 8 caracteres');
      if (password !== confirm) return setError(form, 'password_confirm', 'Las contraseñas no coinciden');

      submitRegistration(form);
      return;
    }

    currentStep++;
    updateSteps(currentStep);
  };

  window.prevStep = function () {
    if (currentStep > 1) {
      currentStep--;
      updateSteps(currentStep);
    }
  };

  const pwInput = form.querySelector('[name="password"]');
  if (pwInput) {
    pwInput.addEventListener('input', () => updatePasswordStrength(pwInput.value));
  }
}

function updateSteps(step) {
  document.querySelectorAll('.step-dot').forEach((dot, i) => {
    dot.classList.remove('active', 'done');
    if (i + 1 === step) dot.classList.add('active');
    else if (i + 1 < step) dot.classList.add('done');
  });

  document.querySelectorAll('.step-content').forEach((el, i) => {
    el.classList.toggle('active', i + 1 === step);
  });
}

async function submitRegistration(form) {
  const payload = {
    serial_number: form.querySelector('[name="serial_number"]').value.trim(),
    full_name: form.querySelector('[name="name"]').value.trim(),
    email: form.querySelector('[name="email"]').value.trim(),
    password: form.querySelector('[name="password"]').value,
  };

  try {
    showLoading();
    await register(payload);
    updateSteps(3);
  } catch (err) {
    showToast(err.message || 'Error al registrar', 'error');
  } finally {
    hideLoading();
  }
}

function updatePasswordStrength(pw) {
  const bar = document.querySelector('.password-strength .bar');
  const text = document.querySelector('.strength-text');
  if (!bar) return;

  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw)) score++;
  if (/[0-9]/.test(pw)) score++;
  if (/[^A-Za-z0-9]/.test(pw)) score++;

  const levels = [
    { w: '0%', color: 'var(--border)', label: '' },
    { w: '20%', color: 'var(--alert-critical)', label: 'Muy débil' },
    { w: '40%', color: 'var(--alert-high)', label: 'Débil' },
    { w: '60%', color: 'var(--alert-medium)', label: 'Regular' },
    { w: '80%', color: 'var(--accent-cyan)', label: 'Fuerte' },
    { w: '100%', color: 'var(--accent-green)', label: 'Muy fuerte' },
  ];

  const level = levels[score] || levels[0];
  bar.style.width = level.w;
  bar.style.background = level.color;
  if (text) { text.textContent = level.label; text.style.color = level.color; }
}

/* ---------- Validation Helpers ---------- */
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validateSerial(serial) {
  return /^ES-\d{6}-[A-Z0-9]{4}$/.test(serial);
}

function setError(form, name, message) {
  const input = form.querySelector(`[name="${name}"]`);
  if (input) input.classList.add('error');
  const errEl = form.querySelector(`[data-error="${name}"]`);
  if (errEl) errEl.textContent = message;
}

function clearErrors(form) {
  form.querySelectorAll('.input.error').forEach(el => el.classList.remove('error'));
  form.querySelectorAll('.form-error').forEach(el => el.textContent = '');
}

/* ---------- Password Toggle ---------- */
function initPasswordToggles() {
  document.querySelectorAll('.toggle-password').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      if (!input) return;
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      btn.textContent = isPassword ? '🙈' : '👁';
    });
  });
}

/* ---------- Scroll animations ---------- */
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-slide');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.card, .section-header').forEach(el => observer.observe(el));
}

/* ---------- Init ---------- */
document.addEventListener('DOMContentLoaded', () => {
  initSmoothScroll();
  initMobileMenu();
  initPasswordToggles();
  initContactForm();
  initLoginForm();
  initRegisterForm();
  initForgotPasswordForm();
  initScrollAnimations();
});
