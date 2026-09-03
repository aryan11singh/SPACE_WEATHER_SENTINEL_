const API_BASE = (() => {
  if (window.location.protocol === 'file:') return 'http://localhost:8000';
  const host = window.location.hostname;
  if ((host === 'localhost' || host === '127.0.0.1') && window.location.port !== '8000') {
    return 'http://localhost:8000';
  }
  return '';
})();

function apiUrl(path) {
  return API_BASE ? `${API_BASE}${path}` : path;
}

const themeToggle = document.getElementById('themeToggle');
const themeLabel = document.getElementById('themeLabel');

const healthOverall = document.getElementById('healthOverall');
const healthTimestamp = document.getElementById('healthTimestamp');
const healthUptime = document.getElementById('healthUptime');
const healthErrorRate = document.getElementById('healthErrorRate');
const healthRequests = document.getElementById('healthRequests');
const healthLastError = document.getElementById('healthLastError');
const healthRefreshBtn = document.getElementById('healthRefreshBtn');

const modelList = document.getElementById('modelList');
const dataList = document.getElementById('dataList');
const apiList = document.getElementById('apiList');
const modelSummary = document.getElementById('modelSummary');
const dataSummary = document.getElementById('dataSummary');
const apiSummary = document.getElementById('apiSummary');
const modelDirNote = document.getElementById('modelDirNote');
const dataDirNote = document.getElementById('dataDirNote');

function setText(el, value) {
  if (el) el.textContent = value;
}

function setTheme(mode) {
  document.documentElement.setAttribute('data-theme', mode);
  localStorage.setItem('theme', mode);
  if (themeLabel) themeLabel.textContent = mode === 'light' ? 'Light' : 'Dark';
}

const savedTheme = localStorage.getItem('theme') || 'dark';
setTheme(savedTheme);

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    setTheme(current === 'dark' ? 'light' : 'dark');
  });
}

function formatDate(iso) {
  if (!iso) return '--';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

function formatSize(sizeMb) {
  if (sizeMb === null || sizeMb === undefined) return '--';
  return `${sizeMb.toFixed(2)} MB`;
}

function statusPill(status) {
  const span = document.createElement('span');
  span.className = 'status-pill';
  if (status === 'ok') {
    span.classList.add('status-ok');
    span.textContent = 'OK';
  } else if (status === 'warn') {
    span.classList.add('status-warn');
    span.textContent = 'WARN';
  } else {
    span.classList.add('status-bad');
    span.textContent = 'DOWN';
  }
  return span;
}

function renderRows(container, items, type = 'model') {
  if (!container) return;
  container.innerHTML = '';
  items.forEach((item) => {
    const row = document.createElement('div');
    row.className = 'health-row';

    const left = document.createElement('div');
    left.className = 'health-left';

    const name = document.createElement('div');
    name.className = 'health-name';
    name.textContent = item.name || item.endpoint || '--';

    const meta = document.createElement('div');
    meta.className = 'health-meta';
    if (type === 'api') {
      meta.textContent = `${item.path} · ${item.latency_ms !== null ? `${item.latency_ms} ms` : '--'}`;
    } else {
      const fileLabel = item.file ? `${item.file}` : item.path || '--';
      const sizeLabel = formatSize(item.size_mb);
      const timeLabel = formatDate(item.mtime);
      const reqLabel = item.required ? 'required' : 'optional';
      meta.textContent = `${fileLabel} · ${sizeLabel} · ${timeLabel} · ${reqLabel}`;
    }

    left.appendChild(name);
    left.appendChild(meta);

    const right = document.createElement('div');
    right.className = 'health-right';
    right.appendChild(statusPill(item.status || 'bad'));

    row.appendChild(left);
    row.appendChild(right);
    container.appendChild(row);
  });
}

async function fetchHealthFull() {
  let data;
  try {
    const res = await fetch(apiUrl('/api/health_full'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    setText(healthOverall, 'Service Offline');
    setText(healthTimestamp, String(err));
    return;
  }

  setText(healthOverall, data.ok ? 'All Systems Operational' : 'Degraded');
  setText(healthTimestamp, `Updated ${formatDate(data.timestamp)}`);
  const service = data.service || {};
  setText(healthUptime, service.uptime_sec ?? '--');
  setText(healthErrorRate, service.error_rate !== undefined ? `${(service.error_rate * 100).toFixed(2)}%` : '--');
  setText(healthRequests, service.requests?.count ?? '--');
  setText(healthLastError, service.requests?.last_error || 'None');

  setText(modelDirNote, data.model_dir ? `Model dir: ${data.model_dir}` : '--');
  setText(dataDirNote, data.data_dir ? `Data dir: ${data.data_dir}` : '--');

  const models = Array.isArray(data.models) ? data.models : [];
  const dataFiles = Array.isArray(data.data_files) ? data.data_files : [];
  renderRows(modelList, models, 'model');
  renderRows(dataList, dataFiles, 'data');

  const modelOk = models.filter(m => m.status === 'ok').length;
  const dataOk = dataFiles.filter(d => d.status === 'ok').length;
  setText(modelSummary, `${modelOk}/${models.length} OK`);
  setText(dataSummary, `${dataOk}/${dataFiles.length} OK`);
}

const apiEndpoints = [
  { name: 'Health', path: '/api/health' },
  { name: 'Metrics', path: '/api/metrics' },
  { name: 'Series (24h)', path: '/api/series?range=24h' },
  { name: 'Dst Series (24h)', path: '/api/dst_series?range=24h' },
  { name: 'Dst Forecast', path: '/api/dst_forecast?hours=72' },
  { name: 'Dst Outlook', path: '/api/dst_outlook' },
  { name: 'Solar Wind ML', path: '/api/solar_wind_ml?steps=1' },
  { name: 'Solar Wind Phys', path: '/api/solar_wind_phys' },
  { name: 'Kp', path: '/api/kp' },
  { name: 'Alerts', path: '/api/alerts' },
  { name: 'Aurora', path: '/api/aurora?mode=forecast' },
  { name: 'Solar Cycle', path: '/api/solar_cycle' }
];

async function checkEndpoint(endpoint) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  const start = performance.now();
  let status = 'bad';
  let latency = null;
  try {
    const res = await fetch(apiUrl(endpoint.path), { cache: 'no-store', signal: controller.signal });
    latency = Math.round(performance.now() - start);
    const isOk = res.ok;
    let payload = null;
    try {
      payload = await res.json();
    } catch (err) {
      payload = null;
    }
    if (isOk && !(payload && payload.error)) {
      status = latency > 2500 ? 'warn' : 'ok';
    }
  } catch (err) {
    status = 'bad';
  } finally {
    clearTimeout(timeout);
  }
  return {
    name: endpoint.name,
    path: endpoint.path,
    status,
    latency_ms: latency
  };
}

async function fetchApiStatus() {
  const results = await Promise.all(apiEndpoints.map(checkEndpoint));
  renderRows(apiList, results, 'api');
  const okCount = results.filter(r => r.status === 'ok').length;
  setText(apiSummary, `${okCount}/${results.length} OK`);
}

async function refreshAll() {
  await fetchHealthFull();
  await fetchApiStatus();
}

if (healthRefreshBtn) {
  healthRefreshBtn.addEventListener('click', refreshAll);
}

refreshAll();
setInterval(refreshAll, 60000);
