// InkSchedule - lógica compartida: sesión y modal de login/registro.
const API = 'http://localhost:8000/api';
const $ = id => document.getElementById(id);
let isLoginMode = true;

// Escapa texto antes de meterlo en innerHTML (evita inyección de HTML desde nombres/bios)
function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, c => (
        { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));
}

function injectAuthModal() {
    document.body.insertAdjacentHTML('beforeend', `
        <div id="auth-modal">
            <div class="card modal-content">
                <span class="close-btn" onclick="closeAuth()">✕</span>
                <h3 id="auth-title" style="margin-top: 0;">Inicia sesión</h3>
                <p id="auth-error" class="error-msg"></p>
                <input type="text" id="auth_user" placeholder="Nombre de usuario" autocomplete="username">
                <input type="email" id="auth_email" placeholder="Correo electrónico" autocomplete="email">
                <input type="password" id="auth_pass" placeholder="Contraseña" autocomplete="current-password">
                <button class="btn-primary" id="auth-submit-btn" onclick="ejecutarAuth()">Ingresar</button>
                <button class="btn-secondary" id="auth-toggle-btn" onclick="setAuthMode(!isLoginMode)"></button>
            </div>
        </div>
    `);
    ['auth_user', 'auth_email', 'auth_pass'].forEach(id => {
        $(id).addEventListener('keydown', e => { if (e.key === 'Enter') ejecutarAuth(); });
    });
}

function setAuthMode(login) {
    isLoginMode = login;
    $('auth-error').style.display = 'none';
    $('auth-title').textContent = login ? 'Inicia sesión' : 'Crea tu cuenta';
    $('auth_email').style.display = login ? 'none' : 'block';
    $('auth-submit-btn').textContent = login ? 'Ingresar' : 'Crear cuenta';
    $('auth-toggle-btn').textContent = login ? '¿No tienes cuenta? Regístrate' : '¿Ya tienes cuenta? Inicia sesión';
}

function openAuth(mode = 'login') {
    setAuthMode(mode === 'login');
    $('auth-modal').style.display = 'flex';
    $('auth_user').focus();
}

function closeAuth() {
    $('auth-modal').style.display = 'none';
}

async function ejecutarAuth() {
    const username = $('auth_user').value.trim();
    const password = $('auth_pass').value;
    const email = $('auth_email').value.trim();
    const errorBox = $('auth-error');
    errorBox.style.display = 'none';

    try {
        if (!isLoginMode) {
            const reg = await fetch(`${API}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            if (!reg.ok) throw new Error('register');
        }

        const res = await fetch(`${API}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (!res.ok) throw new Error('login');
        const data = await res.json();

        if (data.is_artist) {
            localStorage.setItem('ink_token', data.token);
            location.href = 'dashboard.html';
        } else {
            localStorage.setItem('client_token', data.token);
            localStorage.setItem('client_name', data.username);
            closeAuth();
            if (typeof window.onClientLogin === 'function') {
                window.onClientLogin();
            } else {
                location.href = 'feed.html';
            }
        }
    } catch (err) {
        if (err instanceof TypeError) {
            errorBox.textContent = 'No se pudo conectar con el servidor.';
        } else if (err.message === 'register') {
            errorBox.textContent = 'No se pudo crear la cuenta. Revisa los datos (el usuario puede estar en uso).';
        } else {
            errorBox.textContent = 'Usuario o contraseña incorrectos.';
        }
        errorBox.style.display = 'block';
    }
}

// Muestra u oculta los elementos del header según la sesión activa
function renderSessionNav() {
    const isArtist = !!localStorage.getItem('ink_token');
    const isClient = !!localStorage.getItem('client_token');
    const show = (id, on) => { const el = $(id); if (el) el.style.display = on ? 'inline' : 'none'; };

    show('nav-panel', isArtist);
    show('nav-status', isClient);
    show('nav-logout', isArtist || isClient);
    show('nav-login', !isArtist && !isClient);

    const status = $('nav-status');
    if (status) status.textContent = '¡Hola, ' + (localStorage.getItem('client_name') || 'artista') + '!';
}

function cerrarSesion() {
    ['ink_token', 'client_token', 'client_name'].forEach(k => localStorage.removeItem(k));
    location.href = 'index.html';
}

document.addEventListener('DOMContentLoaded', () => {
    injectAuthModal();
    setAuthMode(true);
    renderSessionNav();
});
