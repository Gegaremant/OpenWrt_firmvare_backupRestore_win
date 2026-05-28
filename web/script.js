// ==========================================
// OpenWRT Backup & Restore Tool - UI Scripts
// EN: Handles UI interactions, API calls to Python backend via PyWebView, and dynamic locale switching.
// RU: Обрабатывает взаимодействия с интерфейсом, API-вызовы к Python-бэкенду через PyWebView и динамическое переключение локалей.
// ==========================================
// --- UI Interactions / Взаимодействие с UI ---

// Tabs
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.add('hidden', 'active'));
        
        btn.classList.add('active');
        const target = document.getElementById(btn.dataset.target);
        target.classList.remove('hidden');
    });
});

// Settings Modal
const btnSettings = document.getElementById('btn-settings');
const settingsModal = document.getElementById('settings-modal');
const btnCloseSettings = document.getElementById('btn-close-settings');

btnSettings.addEventListener('click', () => settingsModal.classList.remove('hidden'));
btnCloseSettings.addEventListener('click', () => settingsModal.classList.add('hidden'));

// Theme Toggle
const themeBtns = document.querySelectorAll('.theme-btn');
themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        themeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        const theme = btn.dataset.theme;
        if (theme === 'system') {
            const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
        } else {
            document.documentElement.setAttribute('data-theme', theme);
        }
    });
});

// Init System Theme
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    document.documentElement.setAttribute('data-theme', 'dark');
}

// Opacity Slider
const opacitySlider = document.getElementById('opacity-slider');
const modalContent = document.querySelector('.modal-content');

opacitySlider.addEventListener('input', (e) => {
    document.body.style.opacity = e.target.value;
    modalContent.style.opacity = '0.3';
});
opacitySlider.addEventListener('change', (e) => {
    modalContent.style.opacity = '1';
});

// Logs Toggle
const btnToggleLogsList = document.querySelectorAll('.btn-toggle-logs');
const logPanel = document.getElementById('log-panel');
let logsVisible = false;

btnToggleLogsList.forEach(btn => {
    btn.addEventListener('click', async () => {
        logsVisible = !logsVisible;
        const txt = await pywebview.api.get_translation(logsVisible ? "btn_hide_logs" : "btn_show_logs");
        btnToggleLogsList.forEach(b => b.innerText = txt);
        if (logsVisible) {
            logPanel.classList.remove('hidden');
            await pywebview.api.resize_window(780, 720);
        } else {
            logPanel.classList.add('hidden');
            await pywebview.api.resize_window(780, 520);
        }
    });
});

document.getElementById('btn-clear-logs').addEventListener('click', () => {
    document.getElementById('log-textarea').value = '';
});

// --- PyWebView Integration ---

// Translate UI
async function translateUI() {
    const elements = document.querySelectorAll('[data-i18n]');
    for (let el of elements) {
        const key = el.getAttribute('data-i18n');
        const text = await pywebview.api.get_translation(key);
        if (text) el.innerText = text;
    }
    if (!logsVisible) {
        const txt = await pywebview.api.get_translation("btn_show_logs");
        document.querySelectorAll('.btn-toggle-logs').forEach(b => b.innerText = txt);
    }
}

// Language Toggle
const langRadios = document.querySelectorAll('input[name="lang"]');
langRadios.forEach(radio => {
    radio.addEventListener('change', async (e) => {
        await pywebview.api.change_language(e.target.value);
        translateUI();
    });
});

// Check Router IP
let checkTimeout;
const ipInput = document.getElementById('ip-input');
const ipStatus = document.getElementById('ip-status');

ipInput.addEventListener('input', () => {
    ipStatus.innerText = '⏳';
    ipStatus.style.color = 'inherit';
    clearTimeout(checkTimeout);
    checkTimeout = setTimeout(async () => {
        const isWrt = await pywebview.api.check_router_status(ipInput.value);
        if (isWrt) {
            ipStatus.innerText = '✅ OpenWrt';
            ipStatus.style.color = '#4ade80';
        } else {
            ipStatus.innerText = '❌';
            ipStatus.style.color = '#ff5555';
        }
    }, 1000);
});

// Browse Buttons
document.getElementById('btn-browse-dest').addEventListener('click', async () => {
    const folder = await pywebview.api.browse_dest_folder();
    if (folder) document.getElementById('dest-input').value = folder;
});

document.getElementById('btn-browse-fw').addEventListener('click', async () => {
    const file = await pywebview.api.browse_firmware_file();
    if (file) document.getElementById('fw-input').value = file;
});

// Actions
document.getElementById('btn-backup').addEventListener('click', () => {
    pywebview.api.start_backup(
        ipInput.value,
        document.getElementById('user-input').value,
        document.getElementById('pass-input').value,
        document.getElementById('dest-input').value,
        document.getElementById('chk-extract').checked
    );
});

document.getElementById('btn-restore').addEventListener('click', () => {
    pywebview.api.start_restore(
        ipInput.value,
        document.getElementById('user-input').value,
        document.getElementById('pass-input').value,
        document.getElementById('fw-input').value,
        document.getElementById('chk-keep').checked,
        document.getElementById('chk-force').checked
    );
});

// Open Links
document.getElementById('btn-github').addEventListener('click', () => pywebview.api.open_url('github'));
document.getElementById('btn-forum').addEventListener('click', () => pywebview.api.open_url('forum'));

// Expose JS functions to Python (Global scope)
window.update_log = function(text) {
    const ta = document.getElementById('log-textarea');
    ta.value += text + '\n';
    ta.scrollTop = ta.scrollHeight;
};

window.set_status = function(tab, text, isError) {
    const el = document.getElementById(`status-${tab}`);
    el.innerText = text;
    el.style.color = isError ? '#ff5555' : (document.documentElement.getAttribute('data-theme') === 'dark' ? '#3b8ed0' : '#1f538d');
};

// Startup: wait for pywebview to be injected
window.addEventListener('pywebviewready', async () => {
    const defaultIp = await pywebview.api.get_default_ip();
    ipInput.value = defaultIp;
    ipInput.dispatchEvent(new Event('input'));
    await translateUI();
});
