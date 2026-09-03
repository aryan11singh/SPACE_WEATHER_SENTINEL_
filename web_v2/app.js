const API_BASE = (() => {
  if (window.location.protocol === 'file:') return 'http://localhost:8000';
  return '';
})();

function apiUrl(path) {
  return API_BASE ? `${API_BASE}${path}` : path;
}

const stormValue = document.getElementById('stormValue');
const symhValue = document.getElementById('symhValue');
const symhTrend = document.getElementById('symhTrend');
const flareValue = document.getElementById('flareValue');
const flareNote = document.getElementById('flareNote');
const flareClass = document.getElementById('flareClass');
const flareFlux = document.getElementById('flareFlux');
const stormBar = document.getElementById('stormBar');
const stormGauge = document.getElementById('stormGauge');
const timeStamp = document.getElementById('timeStamp');
const bzValue = document.getElementById('bzValue');
const speedValue = document.getElementById('speedValue');
const densityValue = document.getElementById('densityValue');
const refreshBtn = document.getElementById('refreshBtn');
const alertPanel = document.getElementById('alertPanel');
const alertBadge = document.getElementById('alertBadge');
const alertTitle = document.getElementById('alertTitle');
const alertMessage = document.getElementById('alertMessage');
const alertStorm = document.getElementById('alertStorm');
const alertSymh = document.getElementById('alertSymh');
const lastUpdate = document.getElementById('lastUpdate');
const dataAge = document.getElementById('dataAge');
const statusText = document.getElementById('statusText');
const statusPulse = document.getElementById('statusPulse');
const statusCard = document.getElementById('statusCard');
const bzBadge = document.getElementById('bzBadge');
const speedBadge = document.getElementById('speedBadge');
const symLast = document.getElementById('symLast');
const bzLast = document.getElementById('bzLast');
const speedLast = document.getElementById('speedLast');
const kpValue = document.getElementById('kpValue');
const kpTime = document.getElementById('kpTime');
const kpBar = document.getElementById('kpBar');
const chartSym = document.getElementById('chartSym');
const chartBz = document.getElementById('chartBz');
const chartSpeed = document.getElementById('chartSpeed');
const speedFoot = document.getElementById('speedFoot');
const bzFoot = document.getElementById('bzFoot');
const symFoot = document.getElementById('symFoot');
const kpFoot = document.getElementById('kpFoot');
const kpPill = document.getElementById('kpPill');
const chartSpeedFoot = document.getElementById('chartSpeedFoot');
const chartBzFoot = document.getElementById('chartBzFoot');
const chartSymFoot = document.getElementById('chartSymFoot');
const themeToggle = document.getElementById('themeToggle');
const themeLabel = document.getElementById('themeLabel');
const sepLevel = document.getElementById('sepLevel');
const sepLabel = document.getElementById('sepLabel');
const sepFlux = document.getElementById('sepFlux');
const sepEnergy = document.getElementById('sepEnergy');
const sepTime = document.getElementById('sepTime');
const sepNote = document.getElementById('sepNote');
const dragValue = document.getElementById('dragValue');
const dragLevel = document.getElementById('dragLevel');
const dragNote = document.getElementById('dragNote');
const dragAccelValue = document.getElementById('dragAccelValue');
const dragAccelNote = document.getElementById('dragAccelNote');
const dragBallistic = document.getElementById('dragBallistic');
const satPreset = document.getElementById('satPreset');
const satMass = document.getElementById('satMass');
const satArea = document.getElementById('satArea');
const satCd = document.getElementById('satCd');
const satAlt = document.getElementById('satAlt');
const chartDstCompare = document.getElementById('chartDstCompare');
const dstRange = document.getElementById('dstRange');
const dstRefreshBtn = document.getElementById('dstRefreshBtn');
const dstLast = document.getElementById('dstLast');
const chartDstFuture = document.getElementById('chartDstFuture');
const dstFutureNote = document.getElementById('dstFutureNote');
const dstFutureSource = document.getElementById('dstFutureSource');
const swRefreshBtn = document.getElementById('swRefreshBtn');
const swMlTime = document.getElementById('swMlTime');
const swMlSpeed = document.getElementById('swMlSpeed');
const swMlDensity = document.getElementById('swMlDensity');
const swMlBz = document.getElementById('swMlBz');
const chartEnlilSpeed = document.getElementById('chartEnlilSpeed');
const chartEnlilDensity = document.getElementById('chartEnlilDensity');
const chartEnlilBz = document.getElementById('chartEnlilBz');
const enlilTime = document.getElementById('enlilTime');
const enlilSpeedLast = document.getElementById('enlilSpeedLast');
const enlilDensityLast = document.getElementById('enlilDensityLast');
const enlilBzLast = document.getElementById('enlilBzLast');
const satImpactValue = document.getElementById('satImpactValue');
const satImpactLevel = document.getElementById('satImpactLevel');
const satImpactNote = document.getElementById('satImpactNote');
const auroraTime = document.getElementById('auroraTime');
const auroraRisk = document.getElementById('auroraRisk');
const refreshAuroraBtn = document.getElementById('refreshAuroraBtn');
const auroraNorthNowImg = document.getElementById('auroraNorthNowImg');
const auroraSouthNowImg = document.getElementById('auroraSouthNowImg');
const auroraNorthFcImg = document.getElementById('auroraNorthFcImg');
const auroraSouthFcImg = document.getElementById('auroraSouthFcImg');
const alertsGrid = document.getElementById('alertsGrid');
const refreshAlertsBtn = document.getElementById('refreshAlertsBtn');
const alertsCount = document.getElementById('alertsCount');
const gpsRisk = document.getElementById('gpsRisk');
const gpsSingleAcc = document.getElementById('gpsSingleAcc');
const gpsDualAcc = document.getElementById('gpsDualAcc');
const gpsTec = document.getElementById('gpsTec');
const gpsScint = document.getElementById('gpsScint');
const gpsNote = document.getElementById('gpsNote');
const satcomRisk = document.getElementById('satcomRisk');
const satcomUhf = document.getElementById('satcomUhf');
const satcomShf = document.getElementById('satcomShf');
const satcomStability = document.getElementById('satcomStability');
const satcomOutage = document.getElementById('satcomOutage');
const satcomNote = document.getElementById('satcomNote');
const refreshMediaBtn = document.getElementById('refreshMediaBtn');
const imgAurora = document.getElementById('imgAurora');
const imgSolarWind = document.getElementById('imgSolarWind');
const imgSwx = document.getElementById('imgSwx');
const imgSunspots = document.getElementById('imgSunspots');
const imgCoronal = document.getElementById('imgCoronal');
const imgFlares = document.getElementById('imgFlares');
const imgCcor1 = document.getElementById('imgCcor1');
const imgMag = document.getElementById('imgMag');
const imgGeospace = document.getElementById('imgGeospace');
const imgSynoptic = document.getElementById('imgSynoptic');
const chartTooltip = document.getElementById('chartTooltip');
const solarCyclePhase = document.getElementById('solarCyclePhase');
const solarCycleLabel = document.getElementById('solarCycleLabel');
const solarCycleF107 = document.getElementById('solarCycleF107');
const solarCycleSsn = document.getElementById('solarCycleSsn');
const solarCycleTime = document.getElementById('solarCycleTime');
const solarCycleBar = document.getElementById('solarCycleBar');

let latestSeries = null;
let latestKp = null;
let dstSeries = null;
let enlilSeries = null;
let dstForecastSeries = null;
let satPresets = [];
let satConfig = null;
let metricsTimer = null;
let lastDataTimestamp = null;
let metricsHealthy = false;
const CHART_PADDING = { left: 36, right: 16, top: 16, bottom: 24 };
const hoverState = { sym: null, bz: null, speed: null, dst: null };

function setText(el, value) {
  if (el) el.textContent = value;
}

function setClass(el, className, enabled) {
  if (el) el.classList.toggle(className, enabled);
}

function formatProb(p) {
  if (p === null || Number.isNaN(p)) return '--';
  return `${(p * 100).toFixed(1)}%`;
}

function formatNum(n, digits = 1) {
  if (n === null || Number.isNaN(n)) return '--';
  return Number(n).toFixed(digits);
}

function formatSci(n, digits = 2) {
  if (!Number.isFinite(n)) return '--';
  return Number(n).toExponential(digits);
}

function formatFlux(n) {
  if (n === null || Number.isNaN(n)) return '--';
  return Number(n).toExponential(2);
}

function formatSepLevel(level) {
  if (!Number.isFinite(level)) return '--';
  return `S${level}`;
}

function formatTimeLabel(ts) {
  if (!ts) return '--';
  const parsed = new Date(String(ts).replace(' ', 'T'));
  if (Number.isNaN(parsed.getTime())) return String(ts);
  return parsed.toLocaleString();
}

function setStatus(ok, text) {
  setText(statusText, text);
  setClass(statusPulse, 'off', !ok);
}

function setBadge(el, text, tone) {
  if (!el) return;
  el.textContent = text;
  el.classList.remove('good', 'warn', 'bad');
  if (tone) el.classList.add(tone);
}

function setTrend(el, diff) {
  if (!el) return;
  el.classList.remove('up', 'down');
  if (Number.isNaN(diff)) {
    el.textContent = '--';
    return;
  }
  if (diff > 1) {
    el.textContent = 'RISING';
    el.classList.add('up');
  } else if (diff < -1) {
    el.textContent = 'FALLING';
    el.classList.add('down');
  } else {
    el.textContent = 'STEADY';
  }
}

function updateLiveAge() {
  if (!metricsHealthy || !lastDataTimestamp) return;
  const ageMs = Date.now() - lastDataTimestamp.getTime();
  if (!Number.isFinite(ageMs) || ageMs < 0) return;
  const ageMin = ageMs / 60000;
  setText(dataAge, ageMin < 1 ? `${Math.round(ageMin * 60)} sec` : `${ageMin.toFixed(1)} min`);
  const ageLabel = ageMin < 1 ? `${Math.round(ageMin * 60)}s` : `${ageMin.toFixed(1)}m`;
  setStatus(true, `Live - updated ${ageLabel} ago`);
  statusCard?.classList.remove('warn', 'bad');
  if (ageMin > 30) {
    statusCard?.classList.add('bad');
  } else if (ageMin > 10) {
    statusCard?.classList.add('warn');
  }
}

function formatPhaseLabel(phase) {
  if (!Number.isFinite(phase)) return '--';
  if (phase < 0.33) return 'Rising';
  if (phase < 0.66) return 'Solar Max';
  return 'Declining';
}

async function fetchSolarCycle() {
  if (!solarCyclePhase && !solarCycleBar) return;
  try {
    const res = await fetch(apiUrl('/api/solar_cycle'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    if (payload.error) throw new Error(payload.error);
    const phase = Number.isFinite(payload.phase) ? payload.phase : null;
    const current = payload.current || {};

    setText(solarCyclePhase, phase === null ? 'Unavailable' : `${Math.round(phase * 100)}%`);
    setText(solarCycleLabel, formatPhaseLabel(phase));
    setText(solarCycleF107, formatNum(current.f107, 1));
    setText(solarCycleSsn, formatNum(current.ssn, 0));
    setText(solarCycleTime, current.time || '--');
    if (solarCycleBar) {
      const width = phase === null ? 0 : Math.max(0, Math.min(1, phase)) * 100;
      solarCycleBar.style.width = `${width}%`;
    }
  } catch (err) {
    setText(solarCyclePhase, 'Unavailable');
    setText(solarCycleLabel, '--');
    setText(solarCycleF107, '--');
    setText(solarCycleSsn, '--');
    setText(solarCycleTime, '--');
    if (solarCycleBar) solarCycleBar.style.width = '0%';
  }
}

function showTooltip(event, title, rows) {
  if (!chartTooltip) return;
  const safeRows = rows || [];
  const body = safeRows.map(row => {
    return `<div class="tooltip-row"><span>${row.label}</span><span>${row.value}</span></div>`;
  }).join('');
  chartTooltip.innerHTML = `<div class="tooltip-title">${title}</div>${body}`;
  chartTooltip.classList.add('show');
  chartTooltip.setAttribute('aria-hidden', 'false');
  const offset = 16;
  let left = event.clientX + offset;
  let top = event.clientY + offset;
  const rect = chartTooltip.getBoundingClientRect();
  const maxLeft = window.innerWidth - rect.width - 8;
  const maxTop = window.innerHeight - rect.height - 8;
  if (left > maxLeft) left = event.clientX - rect.width - offset;
  if (top > maxTop) top = event.clientY - rect.height - offset;
  chartTooltip.style.left = `${Math.max(8, left)}px`;
  chartTooltip.style.top = `${Math.max(8, top)}px`;
}

function hideTooltip() {
  if (!chartTooltip) return;
  chartTooltip.classList.remove('show');
  chartTooltip.setAttribute('aria-hidden', 'true');
}

function buildMetricsUrl() {
  const params = new URLSearchParams();
  const cfg = satConfig || currentSatConfig();
  if (cfg) {
    if (cfg.id) params.set('sat_id', cfg.id);
    if (Number.isFinite(cfg.mass_kg)) params.set('mass_kg', cfg.mass_kg);
    if (Number.isFinite(cfg.area_m2)) params.set('area_m2', cfg.area_m2);
    if (Number.isFinite(cfg.cd)) params.set('cd', cfg.cd);
    if (Number.isFinite(cfg.alt_km)) params.set('alt_km', cfg.alt_km);
  }
  const qs = params.toString();
  const path = qs ? `/api/metrics?${qs}` : '/api/metrics';
  return apiUrl(path);
}

function parseInputValue(el) {
  if (!el) return null;
  const val = parseFloat(el.value);
  return Number.isFinite(val) ? val : null;
}

function currentSatConfig() {
  const mass = parseInputValue(satMass);
  const area = parseInputValue(satArea);
  const cd = parseInputValue(satCd);
  const alt = parseInputValue(satAlt);
  if (!Number.isFinite(mass) || !Number.isFinite(area) || !Number.isFinite(cd) || !Number.isFinite(alt)) {
    return null;
  }
  return {
    id: satPreset ? satPreset.value : 'custom',
    name: satPreset && satPreset.value !== 'custom' ? satPreset.options[satPreset.selectedIndex].textContent : 'Custom',
    mass_kg: mass,
    area_m2: area,
    cd,
    alt_km: alt
  };
}

function applySatPreset(preset) {
  if (!preset) return;
  if (satMass) satMass.value = preset.mass_kg;
  if (satArea) satArea.value = preset.area_m2;
  if (satCd) satCd.value = preset.cd;
  if (satAlt) satAlt.value = preset.alt_km;
  satConfig = {
    id: preset.id,
    name: preset.name,
    mass_kg: preset.mass_kg,
    area_m2: preset.area_m2,
    cd: preset.cd,
    alt_km: preset.alt_km
  };
}

function scheduleMetricsRefresh() {
  if (metricsTimer) clearTimeout(metricsTimer);
  metricsTimer = setTimeout(() => fetchMetrics(), 300);
}

async function loadSatellites() {
  if (!satPreset) return;
  let items = [];
  try {
    const res = await fetch(apiUrl('/api/satellites'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    items = payload.items || [];
  } catch (err) {
    items = [
      { id: 'cubesat_3u', name: 'CubeSat 3U (demo)', mass_kg: 4.0, area_m2: 0.03, cd: 2.2, alt_km: 500 },
      { id: 'cubesat_6u', name: 'CubeSat 6U (demo)', mass_kg: 12.0, area_m2: 0.05, cd: 2.2, alt_km: 500 },
      { id: 'smallsat_100kg', name: 'SmallSat 100 kg (demo)', mass_kg: 100.0, area_m2: 1.0, cd: 2.2, alt_km: 550 },
      { id: 'leo_platform_500kg', name: 'LEO Platform 500 kg (demo)', mass_kg: 500.0, area_m2: 4.0, cd: 2.2, alt_km: 700 },
      { id: 'leo_platform_1000kg', name: 'LEO Platform 1000 kg (demo)', mass_kg: 1000.0, area_m2: 8.0, cd: 2.2, alt_km: 400 }
    ];
  }
  satPresets = items;
  satPreset.innerHTML = '';
  items.forEach(item => {
    const option = document.createElement('option');
    option.value = item.id;
    option.textContent = item.name;
    satPreset.appendChild(option);
  });
  const customOption = document.createElement('option');
  customOption.value = 'custom';
  customOption.textContent = 'Custom';
  satPreset.appendChild(customOption);

  if (items.length) {
    satPreset.value = items[0].id;
    applySatPreset(items[0]);
  } else {
    satPreset.value = 'custom';
    satConfig = currentSatConfig();
  }

  satPreset.addEventListener('change', () => {
    const selected = satPreset.value;
    if (selected === 'custom') {
      satConfig = currentSatConfig();
    } else {
      const preset = satPresets.find(item => item.id === selected);
      applySatPreset(preset);
    }
    scheduleMetricsRefresh();
  });

  [satMass, satArea, satCd, satAlt].forEach(el => {
    if (!el) return;
    el.addEventListener('input', () => {
      if (satPreset && satPreset.value !== 'custom') {
        satPreset.value = 'custom';
      }
      satConfig = currentSatConfig();
      scheduleMetricsRefresh();
    });
  });

  scheduleMetricsRefresh();
}

async function fetchMetrics() {
  let data;
  try {
    const res = await fetch(buildMetricsUrl(), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    setStatus(false, 'Offline - awaiting data');
    setText(stormValue, '--');
    metricsHealthy = false;
    return;
  }

  setText(stormValue, formatProb(data.storm_risk_prob));
  setText(symhValue, formatNum(data.symh_future, 1));
  if (data.flare_mx_prob === null || Number.isNaN(data.flare_mx_prob)) {
    setText(flareValue, 'N/A');
    setText(flareNote, 'Flare model not loaded.');
  } else {
    setText(flareValue, formatProb(data.flare_mx_prob));
    if (data.flare_source === 'goes_xray') {
      setText(flareNote, 'Estimated from X-ray flux (proxy).');
    } else {
      setText(flareNote, 'Uses X-ray flare reports for labeling.');
    }
  }
  if (flareClass) {
    if (data.flare_class) {
      const tone = (data.flare_class === 'X' || data.flare_class === 'M')
        ? 'bad'
        : data.flare_class === 'C'
          ? 'warn'
          : 'good';
      setBadge(flareClass, `Class ${data.flare_class}`, tone);
    } else {
      setBadge(flareClass, 'Class --', null);
    }
  }
  if (flareFlux) {
    if (Number.isFinite(data.flare_flux)) {
      setBadge(flareFlux, `Flux ${formatFlux(data.flare_flux)} W/m^2`, null);
    } else {
      setBadge(flareFlux, 'Flux --', null);
    }
  }
  setText(bzValue, formatNum(data.bz_gsm, 2));
  setText(speedValue, formatNum(data.flow_speed, 0));
  setText(densityValue, formatNum(data.proton_density, 2));

  if (sepLevel) setText(sepLevel, formatSepLevel(data.sep_level));
  if (sepLabel) setText(sepLabel, data.sep_label || 'S-scale');
  if (sepFlux) {
    const tone = data.sep_level >= 3 ? 'bad' : data.sep_level >= 1 ? 'warn' : 'good';
    const text = Number.isFinite(data.sep_flux) ? `${formatFlux(data.sep_flux)} pfu` : '-- pfu';
    setBadge(sepFlux, text, Number.isFinite(data.sep_level) ? tone : null);
  }
  if (sepEnergy) setText(sepEnergy, data.sep_energy || '--');
  if (sepNote) {
    if (Number.isFinite(data.sep_flux)) {
      setText(sepNote, '>10 MeV proton flux snapshot.');
    } else {
      setText(sepNote, 'SEP feed unavailable.');
    }
  }
  if (sepTime) {
    setText(sepTime, data.sep_time ? new Date(data.sep_time).toLocaleString() : '--');
  }

  if (dragValue) {
    if (Number.isFinite(data.drag_dtc_pred_3h)) {
      setText(dragValue, formatNum(data.drag_dtc_pred_3h, 1));
    } else {
      setText(dragValue, '--');
    }
  }
  if (dragLevel) {
    if (data.drag_level) {
      const tone = data.drag_level === 'Low'
        ? 'good'
        : data.drag_level === 'Elevated'
          ? 'warn'
          : 'bad';
      setBadge(dragLevel, data.drag_level, tone);
    } else {
      setBadge(dragLevel, '--', null);
    }
  }
  if (dragNote) {
    if (!Number.isFinite(data.drag_dtc_pred_3h)) {
      setText(dragNote, 'Model offline');
    } else {
      setText(dragNote, 'JB2008');
    }
  }

  if (dragAccelValue) {
    if (Number.isFinite(data.drag_accel_mps2)) {
      setText(dragAccelValue, formatSci(data.drag_accel_mps2, 2));
    } else {
      setText(dragAccelValue, '--');
    }
  }
  if (dragAccelNote) {
    if (Number.isFinite(data.drag_density_kgm3)) {
      setText(dragAccelNote, `ρ ${formatSci(data.drag_density_kgm3, 2)} kg/m³`);
    } else if (data.drag_proxy_ok === false) {
      setText(dragAccelNote, 'Proxy offline');
    } else {
      setText(dragAccelNote, 'Density --');
    }
  }
  if (dragBallistic) {
    if (Number.isFinite(data.drag_ballistic_coeff)) {
      setText(dragBallistic, `Bc ${formatNum(data.drag_ballistic_coeff, 1)} kg/m²`);
    } else {
      setText(dragBallistic, 'Bc --');
    }
  }

  if (satImpactValue) {
    if (Number.isFinite(data.sat_impact_prob)) {
      setText(satImpactValue, formatProb(data.sat_impact_prob));
    } else {
      setText(satImpactValue, '--');
    }
  }
  if (satImpactLevel) {
    if (data.sat_impact_level) {
      const tone = data.sat_impact_level === 'Low'
        ? 'good'
        : data.sat_impact_level === 'Elevated'
          ? 'warn'
          : 'bad';
      setBadge(satImpactLevel, data.sat_impact_level, tone);
    } else {
      setBadge(satImpactLevel, '--', null);
    }
  }
  if (satImpactNote) {
    if (!Number.isFinite(data.sat_impact_prob)) {
      setText(satImpactNote, 'Impact model offline');
    } else {
      setText(satImpactNote, 'Historical anomaly classifier');
    }
  }

  const dataTime = new Date(data.time);
  setText(timeStamp, dataTime.toLocaleString());
  setText(lastUpdate, dataTime.toLocaleString());
  if (!Number.isNaN(dataTime.getTime())) {
    lastDataTimestamp = dataTime;
    metricsHealthy = true;
    updateLiveAge();
  } else {
    setText(dataAge, '--');
    setStatus(true, 'Live stream connected');
    statusCard?.classList.remove('warn', 'bad');
  }

  setText(alertStorm, formatProb(data.storm_risk_prob));
  setText(alertSymh, formatNum(data.symh_future, 1));

  const geoRisk = Number.isFinite(data.storm_risk_prob)
    ? Math.min(1, Math.max(0, data.storm_risk_prob))
    : 0;
  const sepLevelVal = Number.isFinite(data.sep_level) ? data.sep_level : null;
  const sepRisk = sepLevelVal !== null ? Math.min(1, Math.max(0, sepLevelVal / 5)) : 0;
  const flareClassVal = data.flare_class || null;
  const flareBoost = flareClassVal === 'X'
    ? 0.2
    : flareClassVal === 'M'
      ? 0.12
      : flareClassVal === 'C'
        ? 0.05
        : 0;
  const kpBoost = (latestKp !== null && Number.isFinite(latestKp))
    ? (latestKp >= 6 ? 0.1 : latestKp >= 4 ? 0.05 : 0)
    : 0;
  const commsRisk = Math.min(1, geoRisk + sepRisk * 0.4 + flareBoost + kpBoost);
  const gpsRiskScore = Math.min(1, Math.max(geoRisk, sepRisk * 0.6));

  if (auroraRisk) {
    const label = geoRisk >= 0.7 ? 'High' : geoRisk >= 0.4 ? 'Elevated' : 'Low';
    auroraRisk.textContent = `ML risk: ${label}`;
  }
  if (gpsRisk) {
    const label = gpsRiskScore >= 0.7 ? 'High' : gpsRiskScore >= 0.4 ? 'Elevated' : 'Low';
    gpsRisk.textContent = `Risk: ${label}`;
  }

  if (gpsSingleAcc) {
    const acc = gpsRiskScore >= 0.7 ? '10-50 m' : gpsRiskScore >= 0.4 ? '3-15 m' : '<= 1 m';
    gpsSingleAcc.textContent = acc;
  }
  if (gpsDualAcc) {
    const acc = gpsRiskScore >= 0.7 ? '0.3-3 m' : gpsRiskScore >= 0.4 ? '0.05-0.5 m' : '1-5 cm';
    gpsDualAcc.textContent = acc;
  }
  if (gpsTec) {
    const tec = gpsRiskScore >= 0.7 ? 'Severely enhanced' : gpsRiskScore >= 0.4 ? 'Enhanced' : 'Nominal';
    gpsTec.textContent = tec;
  }
  if (gpsScint) {
    const scint = (latestKp !== null && latestKp >= 6) ? 'High' :
      (latestKp !== null && latestKp >= 4) ? 'Moderate' : 'Low';
    gpsScint.textContent = scint;
  }
  if (gpsNote) {
    const note = gpsRiskScore >= 0.7
      ? 'Severe geomagnetic conditions. Expect positioning degradation and possible loss of lock.'
      : gpsRiskScore >= 0.4
        ? 'Disturbed ionosphere. Errors may rise; dual-freq recommended.'
        : 'Quiet conditions. Standard corrections should perform normally.';
    gpsNote.textContent = note;
  }

  if (satcomRisk) {
    const label = commsRisk >= 0.7 ? 'High' : commsRisk >= 0.4 ? 'Elevated' : 'Low';
    satcomRisk.textContent = `Risk: ${label}`;
  }
  if (satcomUhf) {
    const uhf = commsRisk >= 0.7 ? 'Severe fades likely' : commsRisk >= 0.4 ? 'Moderate fades' : 'Nominal';
    satcomUhf.textContent = uhf;
  }
  if (satcomShf) {
    const shf = commsRisk >= 0.7 ? 'Scintillation possible' : commsRisk >= 0.4 ? 'Minor disturbances' : 'Nominal';
    satcomShf.textContent = shf;
  }
  if (satcomStability) {
    const stability = commsRisk >= 0.7 ? 'Unstable' : commsRisk >= 0.4 ? 'Variable' : 'Stable';
    satcomStability.textContent = stability;
  }
  if (satcomOutage) {
    const outage = commsRisk >= 0.7 ? '5-20%' : commsRisk >= 0.4 ? '1-5%' : '<1%';
    satcomOutage.textContent = outage;
  }
  if (satcomNote) {
    const note = commsRisk >= 0.7
      ? 'High risk of attenuation/scintillation. Prepare for link management and redundancy.'
      : commsRisk >= 0.4
        ? 'Conditions may degrade UHF links; monitor SHF performance.'
        : 'Normal propagation expected. Standard link margins should be sufficient.';
    satcomNote.textContent = note;
  }
  const width = Math.min(100, Math.max(0, geoRisk * 100));
  if (stormBar) stormBar.style.width = `${width}%`;
  stormGauge?.style.setProperty('--risk', width.toFixed(1));
  if (data.storm_risk_prob > 0.7) {
    if (stormBar) stormBar.style.background = 'linear-gradient(90deg, #ffb347, #ff4e50)';
  } else {
    if (stormBar) stormBar.style.background = 'linear-gradient(90deg, #f5b942, #39d0ff)';
  }

  if (geoRisk >= 0.7) {
    if (alertPanel) alertPanel.style.borderColor = 'rgba(255, 107, 107, 0.6)';
    setText(alertBadge, 'SEVERE');
    if (alertBadge) {
      alertBadge.style.background = 'rgba(255, 107, 107, 0.15)';
      alertBadge.style.color = '#ff6b6b';
    }
    setText(alertTitle, 'High geomagnetic storm risk');
    setText(alertMessage, 'Potential satellite drag, comms disturbance, and radiation effects within 15 minutes.');
  } else if (geoRisk >= 0.4) {
    if (alertPanel) alertPanel.style.borderColor = 'rgba(245, 185, 66, 0.6)';
    setText(alertBadge, 'ELEVATED');
    if (alertBadge) {
      alertBadge.style.background = 'rgba(245, 185, 66, 0.15)';
      alertBadge.style.color = '#f5b942';
    }
    setText(alertTitle, 'Elevated storm potential');
    setText(alertMessage, 'Monitor solar wind speed and Bz. Prepare mitigation protocols.');
  } else {
    if (alertPanel) alertPanel.style.borderColor = 'rgba(71, 230, 161, 0.5)';
    setText(alertBadge, 'NORMAL');
    if (alertBadge) {
      alertBadge.style.background = 'rgba(71, 230, 161, 0.15)';
      alertBadge.style.color = '#47e6a1';
    }
    setText(alertTitle, 'Systems nominal');
    setText(alertMessage, 'No immediate geomagnetic storm risk detected. Continue monitoring.');
  }

  if (data.bz_gsm <= -5) {
    setBadge(bzBadge, 'Bz southward', 'bad');
  } else if (data.bz_gsm <= -2) {
    setBadge(bzBadge, 'Bz mildly south', 'warn');
  } else {
    setBadge(bzBadge, 'Bz neutral', 'good');
  }

  if (data.flow_speed >= 700) {
    setBadge(speedBadge, 'Speed very high', 'bad');
  } else if (data.flow_speed >= 550) {
    setBadge(speedBadge, 'Speed elevated', 'warn');
  } else {
    setBadge(speedBadge, 'Speed nominal', 'good');
  }
}

async function fetchKp() {
  let data;
  try {
    const res = await fetch(apiUrl('/api/kp'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    setText(kpValue, '--');
    setText(kpTime, '--');
    if (kpBar) kpBar.style.width = '0%';
    return;
  }

  setText(kpValue, Number.isFinite(data.kp) ? data.kp.toFixed(1) : '--');
  setText(kpTime, data.time ? new Date(data.time).toLocaleString() : '--');
  latestKp = Number.isFinite(data.kp) ? data.kp : null;
  const width = Number.isFinite(data.kp) ? Math.min(100, Math.max(0, (data.kp / 9) * 100)) : 0;
  if (kpBar) kpBar.style.width = `${width}%`;
  setText(kpFoot, Number.isFinite(data.kp) ? data.kp.toFixed(1) : '--');
  setText(kpPill, Number.isFinite(data.kp) ? `Kp ${data.kp.toFixed(1)}` : '--');
  if (kpPill) {
    kpPill.style.background = Number.isFinite(data.kp) && data.kp >= 6 ? 'rgba(255, 107, 107, 0.2)' :
      Number.isFinite(data.kp) && data.kp >= 4 ? 'rgba(245, 185, 66, 0.2)' : 'rgba(71, 230, 161, 0.2)';
  }
  if (data.kp >= 6) {
    if (kpBar) kpBar.style.background = 'linear-gradient(90deg, #ffb347, #ff4e50)';
  } else if (data.kp >= 4) {
    if (kpBar) kpBar.style.background = 'linear-gradient(90deg, #f5b942, #39d0ff)';
  } else {
    if (kpBar) kpBar.style.background = 'linear-gradient(90deg, #47e6a1, #39d0ff)';
  }
}

function getCtx(canvas) {
  if (!canvas) return null;
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, width: rect.width, height: rect.height };
}

function drawSeries(ctx, series, color, min, max, width, height, padding, dash = null, lineWidth = 2) {
  const range = max - min || 1;
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth;
  ctx.setLineDash(dash || []);
  ctx.lineJoin = 'round';
  ctx.lineCap = 'round';
  ctx.beginPath();
  let started = false;
  series.forEach((value, i) => {
    if (value === null || Number.isNaN(value)) {
      started = false;
      return;
    }
    const clamped = Math.max(min, Math.min(max, value));
    const x = padding.left + (i / (series.length - 1)) * (width - padding.left - padding.right);
    const y =
      padding.top +
      (1 - (clamped - min) / range) * (height - padding.top - padding.bottom);
    if (!started) {
      ctx.moveTo(x, y);
      started = true;
    } else {
      ctx.lineTo(x, y);
    }
  });
  ctx.stroke();
}

function getXForIndex(index, count, width, padding) {
  if (count <= 1) return padding.left;
  return padding.left + (index / (count - 1)) * (width - padding.left - padding.right);
}

function getYForValue(value, min, max, height, padding) {
  const range = max - min || 1;
  const clamped = Math.max(min, Math.min(max, value));
  return padding.top + (1 - (clamped - min) / range) * (height - padding.top - padding.bottom);
}

function drawCrosshair(ctx, x, height, padding) {
  ctx.save();
  ctx.strokeStyle = 'rgba(255,255,255,0.25)';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(x, padding.top);
  ctx.lineTo(x, height - padding.bottom);
  ctx.stroke();
  ctx.restore();
}

function drawDot(ctx, x, y, color) {
  ctx.save();
  ctx.fillStyle = color;
  ctx.strokeStyle = 'rgba(7, 10, 14, 0.8)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(x, y, 4, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.restore();
}

function renderChart(canvas, series, color, min, max, label, hoverIndex = null) {
  const ctxInfo = getCtx(canvas);
  if (!ctxInfo) return;
  const { ctx, width, height } = ctxInfo;
  const padding = CHART_PADDING;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = 'rgba(8, 12, 18, 0.5)';
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + i * ((height - padding.top - padding.bottom) / 4);
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
  }

  drawSeries(ctx, series, color, min, max, width, height, padding);
  if (hoverIndex !== null && series && series.length > 0) {
    const value = series[hoverIndex];
    if (value !== null && !Number.isNaN(value)) {
      const x = getXForIndex(hoverIndex, series.length, width, padding);
      const y = getYForValue(value, min, max, height, padding);
      drawCrosshair(ctx, x, height, padding);
      drawDot(ctx, x, y, color);
    }
  }

  // Axes labels (min/max) and parameter label
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.font = '11px "JetBrains Mono", monospace';
  ctx.fillText(max.toFixed(0), 6, padding.top + 6);
  ctx.fillText(min.toFixed(0), 6, height - padding.bottom + 12);
  if (label) {
    ctx.fillText(label, padding.left, 12);
  }
}

function calcRange(a, b, fallbackMin, fallbackMax) {
  const values = [];
  [a, b].forEach(series => {
    if (!series) return;
    series.forEach(v => {
      if (v !== null && !Number.isNaN(v)) values.push(v);
    });
  });
  if (!values.length) return { min: fallbackMin, max: fallbackMax };
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (min === max) {
    min -= 1;
    max += 1;
  }
  const pad = (max - min) * 0.1;
  return { min: min - pad, max: max + pad };
}

function renderDualChart(canvas, realSeries, predSeries, label, hoverIndex = null) {
  const ctxInfo = getCtx(canvas);
  if (!ctxInfo) return;
  const { ctx, width, height } = ctxInfo;
  const padding = CHART_PADDING;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = 'rgba(8, 12, 18, 0.5)';
  ctx.fillRect(0, 0, width, height);

  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + i * ((height - padding.top - padding.bottom) / 4);
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
  }

  const range = calcRange(realSeries, predSeries, -200, 50);
  drawSeries(ctx, realSeries, '#ff6b6b', range.min, range.max, width, height, padding, null, 2);
  drawSeries(ctx, predSeries, '#8be9fd', range.min, range.max, width, height, padding, [6, 4], 2);
  if (hoverIndex !== null) {
    const count = Math.max(realSeries?.length || 0, predSeries?.length || 0);
    if (count > 0) {
      const x = getXForIndex(hoverIndex, count, width, padding);
      drawCrosshair(ctx, x, height, padding);
      const realVal = realSeries ? realSeries[hoverIndex] : null;
      const predVal = predSeries ? predSeries[hoverIndex] : null;
      if (realVal !== null && !Number.isNaN(realVal)) {
        const yReal = getYForValue(realVal, range.min, range.max, height, padding);
        drawDot(ctx, x, yReal, '#ff6b6b');
      }
      if (predVal !== null && !Number.isNaN(predVal)) {
        const yPred = getYForValue(predVal, range.min, range.max, height, padding);
        drawDot(ctx, x, yPred, '#8be9fd');
      }
    }
  }

  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.font = '11px \"JetBrains Mono\", monospace';
  ctx.fillText(range.max.toFixed(0), 6, padding.top + 6);
  ctx.fillText(range.min.toFixed(0), 6, height - padding.bottom + 12);
  if (label) {
    ctx.fillText(label, padding.left, 12);
  }
}

function parseAuroraPayload(payload) {
  if (!payload) return [];
  const data = payload.data || payload;
  if (!Array.isArray(data)) return [];
  if (data.length === 0) return [];

  if (Array.isArray(data[0])) {
    return data.map(row => ({
      lat: Number(row[0]),
      lon: Number(row[1]),
      value: Number(row[2]),
    })).filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lon) && Number.isFinite(p.value));
  }

  if (typeof data[0] === 'object') {
    return data.map(row => ({
      lat: Number(row.lat ?? row.latitude ?? row.mlat ?? row.geo_lat),
      lon: Number(row.lon ?? row.longitude ?? row.mlon ?? row.geo_lon),
      value: Number(row.aurora ?? row.value ?? row.intensity ?? row.power),
    })).filter(p => Number.isFinite(p.lat) && Number.isFinite(p.lon) && Number.isFinite(p.value));
  }

  return [];
}

function auroraColor(value, maxValue) {
  const v = Math.max(0, Math.min(1, value / (maxValue || 1)));
  if (v < 0.4) return `rgba(70, 255, 178, ${0.2 + v * 0.8})`;
  if (v < 0.7) return `rgba(255, 214, 102, ${0.3 + v * 0.7})`;
  return `rgba(255, 107, 107, ${0.4 + v * 0.6})`;
}

function refreshAuroraImages() {
  const cacheBust = `?t=${Date.now()}`;
  if (auroraNorthNowImg) auroraNorthNowImg.src = `https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg${cacheBust}`;
  if (auroraSouthNowImg) auroraSouthNowImg.src = `https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg${cacheBust}`;
  if (auroraNorthFcImg) auroraNorthFcImg.src = `https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg${cacheBust}`;
  if (auroraSouthFcImg) auroraSouthFcImg.src = `https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg${cacheBust}`;
  if (auroraTime) auroraTime.textContent = `Updated ${new Date().toLocaleString()}`;
}

function renderAllCharts() {
  if (!latestSeries) return;
  renderChart(chartSym, latestSeries.sym, '#ff6b6b', -200, 50, 'SYM/H (nT)', hoverState.sym);
  renderChart(chartBz, latestSeries.bz, '#2ec4ff', -20, 20, 'Bz GSM (nT)', hoverState.bz);
  renderChart(chartSpeed, latestSeries.speed, '#47e6a1', 200, 900, 'Speed (km/s)', hoverState.speed);
  renderChart(chartSymFoot, latestSeries.sym, '#ff6b6b', -200, 50, 'SYM/H (nT)', null);
  renderChart(chartBzFoot, latestSeries.bz, '#2ec4ff', -20, 20, 'Bz GSM (nT)', null);
  renderChart(chartSpeedFoot, latestSeries.speed, '#47e6a1', 200, 900, 'Speed (km/s)', null);
}

function renderDstChart() {
  if (!dstSeries) return;
  renderDualChart(chartDstCompare, dstSeries.real, dstSeries.pred, 'Dst (nT)', hoverState.dst);
  const lastReal = lastValid(dstSeries.real);
  const lastPred = lastValid(dstSeries.pred);
  if (dstLast) {
    if (lastReal !== null) {
      dstLast.textContent = `${formatNum(lastReal, 1)} | fcst ${formatNum(lastPred, 1)}`;
    } else if (lastPred !== null) {
      dstLast.textContent = `fcst ${formatNum(lastPred, 1)}`;
    } else {
      dstLast.textContent = '--';
    }
  }
}

function renderDstForecast() {
  if (!dstForecastSeries) return;
  const range = calcRange(dstForecastSeries.pred, null, -200, 50);
  renderChart(chartDstFuture, dstForecastSeries.pred, '#2ec4ff', range.min, range.max, 'Dst Forecast (nT)');
  setText(dstFutureNote, `${dstForecastSeries.start} → ${dstForecastSeries.end}`);
  setText(dstFutureSource, dstForecastSeries.source || '--');
}

function renderEnlilCharts() {
  if (!enlilSeries) return;
  const speedRange = calcRange(enlilSeries.speed, null, 200, 900);
  const densityRange = calcRange(enlilSeries.density, null, 0, 30);
  const bzRange = calcRange(enlilSeries.bz, null, -20, 20);
  renderChart(chartEnlilSpeed, enlilSeries.speed, '#2ec4ff', speedRange.min, speedRange.max, 'Speed (km/s)');
  renderChart(chartEnlilDensity, enlilSeries.density, '#47e6a1', densityRange.min, densityRange.max, 'Density (cm⁻³)');
  renderChart(chartEnlilBz, enlilSeries.bz, '#ff6b6b', bzRange.min, bzRange.max, 'Bz GSM (nT)');

  setText(enlilSpeedLast, formatNum(lastValid(enlilSeries.speed), 0));
  setText(enlilDensityLast, formatNum(lastValid(enlilSeries.density), 2));
  setText(enlilBzLast, formatNum(lastValid(enlilSeries.bz), 2));
}

function lastValid(series) {
  for (let i = series.length - 1; i >= 0; i--) {
    const v = series[i];
    if (v !== null && !Number.isNaN(v)) return v;
  }
  return null;
}

function getHoverIndex(event, canvas, count) {
  if (!canvas || count <= 0) return null;
  const rect = canvas.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const usable = Math.max(1, rect.width - CHART_PADDING.left - CHART_PADDING.right);
  const clamped = Math.min(Math.max(x, CHART_PADDING.left), rect.width - CHART_PADDING.right);
  const ratio = (clamped - CHART_PADDING.left) / usable;
  return Math.round(ratio * (count - 1));
}

function bindHoverEvents(canvas, onMove, onLeave) {
  if (!canvas) return;
  canvas.addEventListener('pointermove', onMove);
  canvas.addEventListener('mousemove', onMove);
  canvas.addEventListener('pointerleave', onLeave);
  canvas.addEventListener('mouseleave', onLeave);
  canvas.addEventListener('touchend', onLeave);
}

function bindSyncedHover(canvas) {
  if (!canvas) return;
  const onMove = (event) => {
    if (!latestSeries) return;
    const count = latestSeries.sym?.length || 0;
    if (!count) return;
    const idx = getHoverIndex(event, canvas, count);
    if (idx === null) return;
    if (hoverState.sym !== idx || hoverState.bz !== idx || hoverState.speed !== idx) {
      hoverState.sym = idx;
      hoverState.bz = idx;
      hoverState.speed = idx;
      renderAllCharts();
    }
    const time = latestSeries.time?.[idx];
    showTooltip(event, 'Recent Conditions', [
      { label: 'Time', value: formatTimeLabel(time) },
      { label: 'SYM/H', value: `${formatNum(latestSeries.sym?.[idx], 1)} nT` },
      { label: 'Bz GSM', value: `${formatNum(latestSeries.bz?.[idx], 2)} nT` },
      { label: 'Speed', value: `${formatNum(latestSeries.speed?.[idx], 0)} km/s` }
    ]);
  };
  const onLeave = () => {
    if (hoverState.sym !== null || hoverState.bz !== null || hoverState.speed !== null) {
      hoverState.sym = null;
      hoverState.bz = null;
      hoverState.speed = null;
      renderAllCharts();
    }
    hideTooltip();
  };
  bindHoverEvents(canvas, onMove, onLeave);
}

function bindDstHover() {
  if (!chartDstCompare) return;
  const onMove = (event) => {
    if (!dstSeries) return;
    const count = Math.max(dstSeries.real?.length || 0, dstSeries.pred?.length || 0);
    if (count === 0) return;
    const idx = getHoverIndex(event, chartDstCompare, count);
    if (idx === null) return;
    if (hoverState.dst !== idx) {
      hoverState.dst = idx;
      renderDstChart();
    }
    const time = dstSeries.time?.[idx];
    const real = dstSeries.real?.[idx];
    const pred = dstSeries.pred?.[idx];
    showTooltip(event, 'Dst (nT)', [
      { label: 'Time', value: formatTimeLabel(time) },
      { label: 'Observed', value: `${formatNum(real, 1)} nT` },
      { label: 'Forecast', value: `${formatNum(pred, 1)} nT` }
    ]);
  };
  const onLeave = () => {
    if (hoverState.dst !== null) {
      hoverState.dst = null;
      renderDstChart();
    }
    hideTooltip();
  };
  bindHoverEvents(chartDstCompare, onMove, onLeave);
}

async function fetchSeries() {
    const res = await fetch(apiUrl('/api/series?minutes=720'), { cache: 'no-store' });
  const data = await res.json();
  if (data.error) return;

  const sym = data.sym_h.map(v => (v === null ? null : Number(v)));
  const bz = data.bz_gsm.map(v => (v === null ? null : Number(v)));
  const speed = data.flow_speed.map(v => (v === null ? null : Number(v)));

  const time = Array.isArray(data.time) ? data.time : [];
  latestSeries = { time, sym, bz, speed };
  renderAllCharts();

  const lastSym = lastValid(sym);
  const lastBz = lastValid(bz);
  const lastSpeed = lastValid(speed);
  setText(symLast, formatNum(lastSym, 1));
  setText(bzLast, formatNum(lastBz, 2));
  setText(speedLast, formatNum(lastSpeed, 0));
  setText(symFoot, formatNum(lastSym, 1));
  setText(bzFoot, formatNum(lastBz, 2));
  setText(speedFoot, formatNum(lastSpeed, 0));
  const prevSym = lastValid(sym.slice(0, -1));
  if (prevSym !== null && lastSym !== null) {
    setTrend(symhTrend, lastSym - prevSym);
  } else {
    setTrend(symhTrend, NaN);
  }
}

async function fetchDstSeries() {
  const hours = Number(dstRange?.value || 168);
  let data;
  try {
    const res = await fetch(apiUrl(`/api/dst_series?hours=${hours}&interp=1`), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    return;
  }
  const real = data.dst_true.map(v => (v === null ? null : Number(v)));
  const pred = data.dst_pred.map(v => (v === null ? null : Number(v)));
  const time = Array.isArray(data.time) ? data.time : [];
  dstSeries = { time, real, pred };
  renderDstChart();
}

async function fetchDstForecast() {
  if (!chartDstFuture) return;
  let data;
  try {
    const res = await fetch(apiUrl('/api/dst_forecast?hours=72'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    dstForecastSeries = null;
    return;
  }
  const pred = (data.dst_pred || []).map(v => (v === null ? null : Number(v)));
  dstForecastSeries = {
    time: data.time || [],
    pred,
    start: data.start || '--',
    end: data.end || '--',
    source: data.source || '--'
  };
  renderDstForecast();
}

async function fetchSolarWindMl() {
  let data;
  try {
    const res = await fetch(apiUrl('/api/solar_wind_ml?steps=1'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    setText(swMlTime, 'Unavailable');
    setText(swMlSpeed, '--');
    setText(swMlDensity, '--');
    setText(swMlBz, '--');
    return;
  }

  const time = data.time?.[0];
  const row = data.values?.[0] || {};
  setText(swMlTime, time ? `+${data.horizon_hours}h ${formatTimeLabel(time)}` : '--');
  setText(swMlSpeed, formatNum(row.flow_speed ?? row.vx_gse ?? row.vr ?? row.speed, 0));
  setText(swMlDensity, formatNum(row.proton_density ?? row.density ?? row.n, 2));
  setText(swMlBz, formatNum(row.bz_gsm ?? row.bz_gse ?? row.bz, 2));
}

async function fetchEnlilForecast() {
  let data;
  try {
    const res = await fetch(apiUrl('/api/solar_wind_phys'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
    if (data.error) throw new Error(data.error);
  } catch (err) {
    setText(enlilTime, 'Unavailable');
    enlilSeries = null;
    renderEnlilCharts();
    return;
  }
  const time = Array.isArray(data.time) ? data.time : [];
  enlilSeries = {
    time,
    speed: (data.speed || []).map(v => (v === null ? null : Number(v))),
    density: (data.density || []).map(v => (v === null ? null : Number(v))),
    bz: (data.bz || []).map(v => (v === null ? null : Number(v))),
  };
  if (enlilTime) {
    enlilTime.textContent = data.run_date ? `Run ${data.run_date}` : '--';
  }
  renderEnlilCharts();
}

refreshBtn.addEventListener('click', () => {
  fetchSeries();
  fetchMetrics();
  fetchKp();
  fetchSolarCycle();
  fetchDstForecast();
});
if (refreshAuroraBtn) refreshAuroraBtn.addEventListener('click', refreshAuroraImages);
window.addEventListener('resize', () => {
  renderAllCharts();
  renderDstChart();
  renderDstForecast();
  renderEnlilCharts();
});
if (dstRefreshBtn) dstRefreshBtn.addEventListener('click', fetchDstSeries);
if (dstRange) dstRange.addEventListener('change', fetchDstSeries);
if (swRefreshBtn) swRefreshBtn.addEventListener('click', () => {
  fetchSolarWindMl();
  fetchEnlilForecast();
});
bindSyncedHover(chartSym);
bindSyncedHover(chartBz);
bindSyncedHover(chartSpeed);
bindDstHover();

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

function refreshMedia() {
  const cacheBust = `?t=${Date.now()}`;
  if (imgAurora) imgAurora.src = `https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg${cacheBust}`;
  if (imgSolarWind) imgSolarWind.src = `https://services.swpc.noaa.gov/images/ace-mag-swepam-2-hour.gif${cacheBust}`;
  if (imgSwx) imgSwx.src = `https://services.swpc.noaa.gov/images/ace-epam-2-hour.gif${cacheBust}`;
  if (imgSunspots) imgSunspots.src = `https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_4500.jpg${cacheBust}`;
  if (imgCoronal) imgCoronal.src = `https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg${cacheBust}`;
  if (imgFlares) imgFlares.src = `https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0131.jpg${cacheBust}`;
  if (imgCcor1) {
    imgCcor1.src = `https://services.swpc.noaa.gov/images/animations/ccor1/latest.jpg${cacheBust}`;
    imgCcor1.onerror = () => {
      imgCcor1.removeAttribute('src');
    };
  }
  if (imgMag) imgMag.src = `https://services.swpc.noaa.gov/images/boulder-magnetometer.png${cacheBust}`;
  if (imgGeospace) imgGeospace.src = `https://services.swpc.noaa.gov/images/geospace/geospace_1_day.png${cacheBust}`;
  if (imgSynoptic) {
    const url = encodeURIComponent('https://gong.nso.edu/data/magmap/corona/gong_synoptic_map.jpg');
    imgSynoptic.src = apiUrl(`/api/proxy-image?url=${url}${cacheBust}`);
  }
}

if (refreshMediaBtn) refreshMediaBtn.addEventListener('click', refreshMedia);
if (refreshAlertsBtn) refreshAlertsBtn.addEventListener('click', fetchAlerts);
const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightboxImg');
const lightboxClose = document.getElementById('lightboxClose');

function openLightbox(src, alt) {
  if (!lightbox || !lightboxImg) return;
  lightboxImg.src = src;
  lightboxImg.alt = alt || 'Full size view';
  lightbox.classList.add('show');
  lightbox.setAttribute('aria-hidden', 'false');
}

function closeLightbox() {
  if (!lightbox) return;
  lightbox.classList.remove('show');
  lightbox.setAttribute('aria-hidden', 'true');
  if (lightboxImg) lightboxImg.src = '';
}

document.querySelectorAll('.gallery-card img, .aurora-card img').forEach(img => {
  img.addEventListener('click', () => {
    openLightbox(img.currentSrc || img.src, img.alt);
  });
});

if (lightboxClose) lightboxClose.addEventListener('click', closeLightbox);
if (lightbox) {
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });
}
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeLightbox();
});

function renderAlerts(items) {
  if (!alertsGrid) return;
  alertsGrid.innerHTML = '';
  if (!items || items.length === 0) {
    alertsGrid.innerHTML = '<div class="alert-card"><div class="alert-title">No active alerts.</div></div>';
    return;
  }
  items.slice(0, 12).forEach(item => {
    const card = document.createElement('div');
    card.className = 'alert-card';

    const badge = document.createElement('div');
    badge.className = `alert-badge ${item.level || 'info'}`;
    badge.textContent = (item.level || 'info').toUpperCase();

    const title = document.createElement('div');
    title.className = 'alert-title';
    title.textContent = item.headline || 'Space Weather Message';

    const meta = document.createElement('div');
    meta.className = 'alert-meta-row';
    if (item.issue_datetime) {
      const dt = new Date(item.issue_datetime);
      meta.textContent = `Issued: ${dt.toLocaleString()}`;
    } else {
      meta.textContent = 'Issued: --';
    }

    card.appendChild(badge);
    card.appendChild(title);
    card.appendChild(meta);
    alertsGrid.appendChild(card);
  });
}

async function fetchAlerts() {
  if (!alertsGrid) return;
  let payload;
  try {
    const res = await fetch(apiUrl('/api/alerts'), { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    payload = await res.json();
    if (payload.error) throw new Error(payload.error);
  } catch (err) {
    // Fallback: fetch directly from upstream feed if server can't reach the feed.
    try {
      const res = await fetch('https://services.swpc.noaa.gov/products/alerts.json', { cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const items = (Array.isArray(data) ? data : []).map(row => {
        const message = row.message || '';
        const headline = message.split('\n').find(line =>
          line.includes('ALERT:') || line.includes('WARNING:') || line.includes('WATCH:')
        ) || message.split('\n').find(line => line.trim()) || 'Space Weather Message';
        const level = /WARNING/i.test(headline) ? 'warning' :
          /WATCH/i.test(headline) ? 'watch' :
          /ALERT/i.test(headline) ? 'alert' : 'info';
        return {
          product_id: row.product_id,
          issue_datetime: row.issue_datetime,
          headline,
          level,
          message
        };
      });
      setText(alertsCount, `${items.length} items`);
      renderAlerts(items);
      return;
    } catch (err2) {
      setText(alertsCount, 'Alerts unavailable');
      renderAlerts([]);
      return;
    }
  }
  const items = payload.items || [];
  setText(alertsCount, `${items.length} items`);
  renderAlerts(items);
}

loadSatellites();
fetchMetrics();
fetchSeries();
fetchDstSeries();
fetchDstForecast();
fetchSolarWindMl();
fetchEnlilForecast();
fetchKp();
fetchSolarCycle();
refreshAuroraImages();
refreshMedia();
fetchAlerts();
setInterval(fetchMetrics, 5000);
setInterval(updateLiveAge, 15000);
setInterval(fetchSeries, 60000);
setInterval(fetchDstSeries, 300000);
setInterval(fetchDstForecast, 3600000);
setInterval(fetchSolarWindMl, 900000);
setInterval(fetchEnlilForecast, 3600000);
setInterval(fetchKp, 300000);
setInterval(fetchSolarCycle, 21600000);
setInterval(refreshAuroraImages, 300000);
setInterval(refreshMedia, 300000);
setInterval(fetchAlerts, 300000);
