import Script from "next/script";

export default function Home() {
  const bgVideoSrc = process.env.NEXT_PUBLIC_BG_VIDEO || "";
  const bgVideoPoster = process.env.NEXT_PUBLIC_BG_VIDEO_POSTER || "";

  return (
    <>
      <div className="noise"></div>
      <div className="glow"></div>
      {bgVideoSrc ? (
        <video
          className="bg-video"
          autoPlay
          muted
          loop
          playsInline
          poster={bgVideoPoster || undefined}
        >
          <source src={bgVideoSrc} />
        </video>
      ) : null}
      <div className="video-overlay"></div>
      <div className="starfield layer-1"></div>
      <div className="starfield layer-2"></div>
      <div className="orbit"></div>
      <div className="atlas-layout">
        <aside className="atlas-sidebar">
          <div className="atlas-brand">
            <span className="atlas-leaf">●</span>
            <div>
              <strong>Sentinel Ops</strong>
              <span>Cluster Dashboard</span>
            </div>
          </div>
          <nav className="atlas-nav">
            <button type="button" className="atlas-nav-item active">Overview</button>
            <button type="button" className="atlas-nav-item">Metrics</button>
            <button type="button" className="atlas-nav-item">Alerts</button>
            <button type="button" className="atlas-nav-item">Data Feeds</button>
            <button type="button" className="atlas-nav-item">Models</button>
            <button type="button" className="atlas-nav-item">Settings</button>
          </nav>
          <div className="atlas-side-meta">
            <div className="atlas-meta-row">
              <span>Environment</span>
              <strong>Production</strong>
            </div>
            <div className="atlas-meta-row">
              <span>Region</span>
              <strong>US-East</strong>
            </div>
          </div>
        </aside>

        <main className="shell atlas-shell">
          <header className="hero">
            <div className="hero-copy">
              <p className="eyebrow">Space Center Analysis & Monitoring</p>
              <h1>ORBITAL MONITOR</h1>
              <p className="sub">Satellite tracking, space-weather telemetry, and risk forecasting for mission operations.</p>
              <div className="meta-strip">
                <div className="meta-item">
                  <span className="meta-label">Last update</span>
                  <span id="lastUpdate">--</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Data age</span>
                  <span id="dataAge">--</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Forecast horizon</span>
                  <span>24 h</span>
                </div>
              </div>
            </div>
            <div className="status-card" id="statusCard">
              <div className="status-row">
                <div className="pulse" id="statusPulse"></div>
                <span id="statusText">Live stream connected</span>
              </div>
              <p className="status-note">Solar wind + X-ray ingestion</p>
              <button className="theme-toggle" id="themeToggle" type="button" aria-label="Toggle theme">
                <span className="theme-dot"></span>
                <span id="themeLabel">Dark</span>
              </button>
            </div>
          </header>

          <section className="orbital-panel" id="satellites" aria-label="Satellite constellation overview">
          <div className="orbital-copy">
            <p className="eyebrow">Real-Time Constellation Layer</p>
            <h2>SATELLITE TRACKING SYSTEM</h2>
            <p>Glowing nodes represent satellites, lines represent relay paths, and pulse intensity indicates telemetry activity.</p>
            <div className="orbital-legend">
              <span className="legend-chip active">Active Satellite</span>
              <span className="legend-chip relay">Relay Node</span>
              <span className="legend-chip degraded">Degraded Signal</span>
              <span className="legend-chip anomaly">Anomaly Detected</span>
            </div>
          </div>

          <div className="orbital-canvas" role="img" aria-label="Animated orbital network around Earth">
            <div className="orbital-parallax layer-a"></div>
            <div className="orbital-parallax layer-b"></div>
            <div className="orbit-ring ring-1"></div>
            <div className="orbit-ring ring-2"></div>
            <div className="orbit-ring ring-3"></div>
            <div className="orbital-earth"></div>

            <span className="sat-link l1"></span>
            <span className="sat-link l2"></span>
            <span className="sat-link l3"></span>
            <span className="sat-link l4"></span>
            <span className="sat-link l5"></span>

            <div className="sat-node active n1"><span>GPS-A1</span></div>
            <div className="sat-node relay n2"><span>RELAY-7</span></div>
            <div className="sat-node active n3"><span>LEO-22</span></div>
            <div className="sat-node degraded n4"><span>WX-19</span></div>
            <div className="sat-node relay n5"><span>STAR-R6</span></div>
            <div className="sat-node anomaly n6"><span>POLAR-X</span></div>
            <div className="sat-node active n7"><span>GEO-C3</span></div>
          </div>
        </section>

        <section className="alert" id="alertPanel">
          <div className="alert-badge" id="alertBadge">NORMAL</div>
          <div>
            <h2 id="alertTitle">Systems nominal</h2>
            <p id="alertMessage">No immediate geomagnetic storm risk detected. Continue monitoring solar wind and Bz.</p>
          </div>
          <div className="alert-meta">
            <div>
              <span className="meta-label">Storm risk</span>
              <strong id="alertStorm">--</strong>
            </div>
            <div>
              <span className="meta-label">SYM/H +15</span>
              <strong id="alertSymh">--</strong>
            </div>
          </div>
        </section>

        <section className="grid" id="kpis">
          <article className="card primary">
            <div className="card-head">
              <span className="tag">Storm Risk</span>
              <span className="meta" id="timeStamp">--</span>
            </div>
            <div className="gauge" id="stormGauge" style={{ "--risk": 0 }}>
              <div className="gauge-inner">
                <div className="value" id="stormValue">--</div>
                <div className="unit">Probability</div>
              </div>
            </div>
            <div className="bar">
              <div className="bar-fill" id="stormBar"></div>
            </div>
            <p className="note">Threshold: SYM/H ≤ −50 nT within 24 hours.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Kp Index</span>
              <span className="meta" id="kpTime">--</span>
            </div>
            <div className="metric">
              <div className="value" id="kpValue">--</div>
              <div className="unit">0–9</div>
            </div>
            <div className="bar">
              <div className="bar-fill" id="kpBar"></div>
            </div>
            <p className="note">Planetary K-index from upstream feed (3-hour intervals).</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Dst (SYM/H)</span>
              <span className="meta">+24 h</span>
            </div>
            <div className="metric">
              <div className="value" id="symhValue">--</div>
              <div className="unit">nT</div>
              <span className="trend" id="symhTrend">--</span>
            </div>
            <p className="note">SYM/H is used as a Dst proxy for storm intensity.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Flare Risk</span>
              <span className="meta">M/X Class</span>
            </div>
            <div className="metric">
              <div className="value" id="flareValue">--</div>
              <div className="unit">Probability</div>
            </div>
            <div className="chip-row">
              <span className="chip" id="flareClass">Class --</span>
              <span className="chip" id="flareFlux">Flux --</span>
            </div>
            <p className="note" id="flareNote">Uses X-ray flare reports for labeling.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">SEP Risk</span>
              <span className="meta" id="sepTime">--</span>
            </div>
            <div className="metric">
              <div className="value" id="sepLevel">--</div>
              <div className="unit" id="sepLabel">S-scale</div>
            </div>
            <div className="chip-row">
              <span className="chip" id="sepFlux">-- pfu</span>
              <span className="chip" id="sepEnergy">--</span>
            </div>
            <p className="note" id="sepNote">&gt;10 MeV proton flux feed.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Drag Proxy</span>
              <span className="meta">+3 hr</span>
            </div>
            <div className="metric">
              <div className="value" id="dragValue">--</div>
              <div className="unit">DTC</div>
            </div>
            <div className="chip-row">
              <span className="chip" id="dragLevel">--</span>
              <span className="chip" id="dragNote">JB2008</span>
            </div>
            <p className="note">Thermospheric temperature correction proxy.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Satellite Drag</span>
              <span className="meta">+3 hr</span>
            </div>
            <div className="metric">
              <div className="value" id="dragAccelValue">--</div>
              <div className="unit">m/s²</div>
            </div>
            <div className="chip-row">
              <span className="chip" id="dragAccelNote">Density --</span>
              <span className="chip" id="dragBallistic">Bc --</span>
            </div>
            <div className="input-row">
              <label htmlFor="satPreset">Satellite</label>
              <select id="satPreset"></select>
            </div>
            <div className="input-grid">
              <label className="input-label">Mass (kg)
                <input id="satMass" type="number" min="0" step="0.1" />
              </label>
              <label className="input-label">Area (m²)
                <input id="satArea" type="number" min="0" step="0.001" />
              </label>
              <label className="input-label">Cd
                <input id="satCd" type="number" min="0.5" step="0.01" />
              </label>
              <label className="input-label">Altitude (km)
                <input id="satAlt" type="number" min="120" step="1" />
              </label>
            </div>
            <p className="note">Drag estimate uses DTC proxy + density lookup. Replace with real satellite values.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Satellite Impact</span>
              <span className="meta">+6 hr</span>
            </div>
            <div className="metric">
              <div className="value" id="satImpactValue">--</div>
              <div className="unit">Probability</div>
            </div>
            <div className="chip-row">
              <span className="chip" id="satImpactLevel">--</span>
              <span className="chip" id="satImpactNote">Anomaly model</span>
            </div>
            <p className="note">Risk estimated from historical anomaly events.</p>
          </article>

          <article className="card">
            <div className="card-head">
              <span className="tag">Live Solar Wind</span>
              <span className="meta">Latest minute</span>
            </div>
            <div className="triple">
              <div>
                <div className="label">Bz (GSM)</div>
                <div className="mini" id="bzValue">--</div>
              </div>
              <div>
                <div className="label">Speed</div>
                <div className="mini" id="speedValue">--</div>
              </div>
              <div>
                <div className="label">Density</div>
                <div className="mini" id="densityValue">--</div>
              </div>
            </div>
            <div className="chip-row">
              <span className="chip" id="bzBadge">Bz neutral</span>
              <span className="chip" id="speedBadge">Speed nominal</span>
            </div>
          </article>
        </section>

        <section className="guide-panel">
          <div>
            <h2>Satellite Prediction Setup</h2>
            <p>To calculate satellite drag, select a satellite model from the dropdown (or enter custom mass, area, Cd, and altitude) in the Satellite Drag card.</p>
          </div>
          <div className="guide-note">Model selection is required for accurate drag estimates.</div>
        </section>

        <section className="chart-panel" id="space-weather">
          <div className="chart-head">
            <div>
              <h2>Recent Conditions</h2>
              <p>Last 12 hours of SYM/H, Bz and solar wind speed.</p>
            </div>
            <button id="refreshBtn">Refresh</button>
          </div>
          <div className="chart-grid">
            <article className="chart-card">
              <div className="chart-title">
                <span>SYM/H (nT)</span>
                <span className="chart-value" id="symLast">--</span>
              </div>
              <canvas id="chartSym"></canvas>
            </article>
            <article className="chart-card">
              <div className="chart-title">
                <span>Bz GSM (nT)</span>
                <span className="chart-value" id="bzLast">--</span>
              </div>
              <canvas id="chartBz"></canvas>
            </article>
            <article className="chart-card">
              <div className="chart-title">
                <span>Solar wind speed (km/s)</span>
                <span className="chart-value" id="speedLast">--</span>
              </div>
              <canvas id="chartSpeed"></canvas>
            </article>
          </div>
        </section>

        <section className="chart-panel">
          <div className="chart-head">
            <div>
              <h2>Dst Forecast vs Observed</h2>
              <p>Overlay of model forecast and observed Dst for the period.</p>
            </div>
            <div className="chart-actions">
              <label className="select-label" htmlFor="dstRange">Range</label>
              <select id="dstRange" defaultValue="168">
                <option value="24">Last 24h</option>
                <option value="72">Last 3d</option>
                <option value="168">Last 7d</option>
                <option value="336">Last 14d</option>
                <option value="720">Last 30d</option>
              </select>
              <button id="dstRefreshBtn">Update</button>
            </div>
          </div>
          <div className="legend">
            <span className="legend-item"><span className="dot real"></span>Observed Dst</span>
            <span className="legend-item"><span className="dot pred"></span>Model forecast (+1h)</span>
          </div>
          <div className="chart-grid">
            <article className="chart-card">
              <div className="chart-title">
                <span>Dst (nT)</span>
                <span className="chart-value" id="dstLast">--</span>
              </div>
              <canvas id="chartDstCompare" className="chart-large"></canvas>
            </article>
            <article className="chart-card">
              <div className="chart-title">
                <span>Dst forecast (next 72h)</span>
                <span className="chart-value" id="dstFutureSource">--</span>
              </div>
              <canvas id="chartDstFuture" className="chart-large"></canvas>
              <p className="note" id="dstFutureNote">--</p>
            </article>
          </div>
        </section>

        <section className="chart-panel" id="cme-panel">
          <div className="chart-head">
            <div>
              <h2>CME Live Feed &amp; Climatology</h2>
              <p>Latest coronal mass ejection data and historical arrival statistics.</p>
            </div>
            <button id="cmeRefreshBtn">Refresh</button>
          </div>
          <div className="grid">
            <article className="card">
              <div className="card-head">
                <span className="tag">CME Live</span>
                <span className="meta" id="cmeLiveTime">--</span>
              </div>
              <div className="triple">
                <div>
                  <div className="label">Speed</div>
                  <div className="mini" id="cmeLiveSpeed">--</div>
                </div>
                <div>
                  <div className="label">Width</div>
                  <div className="mini" id="cmeLiveWidth">--</div>
                </div>
                <div>
                  <div className="label">Earth Prob</div>
                  <div className="mini" id="cmeLiveProb">--</div>
                </div>
              </div>
              <p className="note">Estimated arrival: <span id="cmeLiveEta">--</span></p>
            </article>

            <article className="card">
              <div className="card-head">
                <span className="tag">CME Climatology</span>
                <span className="meta" id="cmeClimoLast">--</span>
              </div>
              <canvas id="chartCmeClimo"></canvas>
              <p className="note" id="cmeClimoNote">Historical CME arrival rate.</p>
            </article>

            <article className="card">
              <div className="card-head">
                <span className="tag">CME Scenario</span>
                <span className="meta">What-if</span>
              </div>
              <div className="input-grid">
                <label className="input-label">Speed (km/s)
                  <input id="cmeSpeedInput" type="number" min="200" step="10" defaultValue="500" />
                </label>
                <label className="input-label">Width (°)
                  <input id="cmeWidthInput" type="number" min="0" max="360" step="5" defaultValue="60" />
                </label>
                <label className="input-label">Latitude (°)
                  <input id="cmeLatInput" type="number" min="-90" max="90" step="1" defaultValue="0" />
                </label>
                <label className="input-label">Longitude (°)
                  <input id="cmeLonInput" type="number" min="-180" max="180" step="1" defaultValue="0" />
                </label>
              </div>
              <div className="input-row" style={{ marginTop: 8 }}>
                <label htmlFor="cmeHaloInput">Halo CME</label>
                <input id="cmeHaloInput" type="checkbox" />
              </div>
              <div className="chip-row" style={{ marginTop: 8 }}>
                <span className="chip">Earth hit prob: <span id="cmeScenarioProb">--</span></span>
                <span className="chip">ETA: <span id="cmeScenarioEta">--</span></span>
              </div>
              <button id="cmeScenarioBtn" style={{ marginTop: 8 }}>Run Scenario</button>
            </article>
          </div>
        </section>

        <section className="chart-panel" id="dst-outlook-panel">
          <div className="chart-head">
            <div>
              <h2>Dst 30-Day Outlook</h2>
              <p>Extended geomagnetic storm intensity outlook.</p>
            </div>
            <button id="dstOutlookRefreshBtn">Refresh</button>
          </div>
          <div className="chart-grid">
            <article className="chart-card">
              <div className="chart-title">
                <span>Dst Outlook (nT)</span>
                <span className="chart-value" id="dstOutlookSummary">--</span>
              </div>
              <canvas id="chartDstOutlook" className="chart-large"></canvas>
              <p className="note" id="dstOutlookNote">--</p>
            </article>
          </div>
        </section>

        <section className="chart-panel" id="swml-panel">
          <div className="chart-head">
            <div>
              <h2>Solar Wind ML Charts</h2>
              <p>Machine-learning 24-hour solar wind forecast time series.</p>
            </div>
          </div>
          <div className="chart-grid">
            <article className="chart-card">
              <div className="chart-title">
                <span>ML Speed (km/s)</span>
                <span className="chart-value" id="swMlSpeedLast">--</span>
              </div>
              <canvas id="chartSwMlSpeed"></canvas>
            </article>
            <article className="chart-card">
              <div className="chart-title">
                <span>ML Density (cm⁻³)</span>
                <span className="chart-value" id="swMlDensityLast">--</span>
              </div>
              <canvas id="chartSwMlDensity"></canvas>
            </article>
            <article className="chart-card">
              <div className="chart-title">
                <span>ML Bz GSM (nT)</span>
                <span className="chart-value" id="swMlBzLast">--</span>
              </div>
              <canvas id="chartSwMlBz"></canvas>
            </article>
          </div>
        </section>

        <section className="chart-panel">
          <div className="chart-head">
            <div>
              <h2>Solar Wind Forecasts</h2>
              <p>ML 24‑hour forecast plus physics-based WSA‑Enlil 1–4 day outlook.</p>
            </div>
            <button id="swRefreshBtn">Refresh</button>
          </div>
          <div className="forecast-grid">
            <article className="forecast-card">
              <div className="chart-title">
                <span>ML 24h Forecast</span>
                <span className="chart-value" id="swMlTime">--</span>
              </div>
              <div className="triple">
                <div>
                  <div className="label">Speed</div>
                  <div className="mini" id="swMlSpeed">--</div>
                </div>
                <div>
                  <div className="label">Density</div>
                  <div className="mini" id="swMlDensity">--</div>
                </div>
                <div>
                  <div className="label">Bz GSM</div>
                  <div className="mini" id="swMlBz">--</div>
                </div>
              </div>
              <p className="note">Direct +24h ML prediction from OMNI history.</p>
            </article>
            <article className="forecast-card">
              <div className="chart-title">
                <span>WSA‑Enlil (1–4 days)</span>
                <span className="chart-value" id="enlilTime">--</span>
              </div>
              <div className="chart-grid">
                <article className="chart-card">
                  <div className="chart-title">
                    <span>Speed (km/s)</span>
                    <span className="chart-value" id="enlilSpeedLast">--</span>
                  </div>
                  <canvas id="chartEnlilSpeed"></canvas>
                </article>
                <article className="chart-card">
                  <div className="chart-title">
                    <span>Density (cm⁻³)</span>
                    <span className="chart-value" id="enlilDensityLast">--</span>
                  </div>
                  <canvas id="chartEnlilDensity"></canvas>
                </article>
                <article className="chart-card">
                  <div className="chart-title">
                    <span>Bz GSM (nT)</span>
                    <span className="chart-value" id="enlilBzLast">--</span>
                  </div>
                  <canvas id="chartEnlilBz"></canvas>
                </article>
              </div>
              <p className="note">Physics model forecast from NOAA WSA‑Enlil run.</p>
            </article>
          </div>
        </section>

        <section className="aurora-panel">
          <div className="chart-head">
            <div>
              <h2>Aurora Nowcast & Forecast</h2>
              <p>OVATION auroral oval intensity by hemisphere with ML‑aware risk cues.</p>
            </div>
            <div className="aurora-meta">
              <span id="auroraRisk">ML risk: --</span>
              <span id="auroraTime">--</span>
              <button id="refreshAuroraBtn">Refresh</button>
            </div>
          </div>
          <div className="aurora-grid">
            <article className="aurora-card">
              <div className="aurora-title">North Nowcast</div>
              <img id="auroraNorthNowImg" alt="Aurora nowcast north" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg" />
            </article>
            <article className="aurora-card">
              <div className="aurora-title">South Nowcast</div>
              <img id="auroraSouthNowImg" alt="Aurora nowcast south" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg" />
            </article>
            <article className="aurora-card">
              <div className="aurora-title">North Forecast</div>
              <img id="auroraNorthFcImg" alt="Aurora forecast north" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg" />
            </article>
            <article className="aurora-card">
              <div className="aurora-title">South Forecast</div>
              <img id="auroraSouthFcImg" alt="Aurora forecast south" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg" />
            </article>
          </div>
        </section>

        <section className="alerts-panel">
          <div className="chart-head">
            <div>
              <h2>Alerts, Watches & Warnings</h2>
              <p>Live space-weather bulletins.</p>
            </div>
            <div className="alerts-meta">
              <span id="alertsCount">--</span>
              <button id="refreshAlertsBtn">Refresh</button>
            </div>
          </div>
          <div className="alerts-grid" id="alertsGrid"></div>
        </section>

        <section className="gps-panel">
          <div className="chart-head">
            <div>
              <h2>Space Weather & GPS Systems</h2>
              <p>Live impact guidance for single/dual‑frequency GNSS positioning.</p>
            </div>
            <div className="gps-meta">
              <span id="gpsRisk">Risk: --</span>
            </div>
          </div>
          <div className="gps-grid">
            <article className="gps-card">
              <div className="gps-title">Single‑frequency accuracy</div>
              <div className="gps-value" id="gpsSingleAcc">--</div>
              <p className="gps-note">Quiet ionosphere: ~1m. Storms can push errors to tens of meters.</p>
            </article>
            <article className="gps-card">
              <div className="gps-title">Dual‑frequency accuracy</div>
              <div className="gps-value" id="gpsDualAcc">--</div>
              <p className="gps-note">Normally centimeters. Severe disturbances can cause loss of lock.</p>
            </article>
            <article className="gps-card">
              <div className="gps-title">Ionospheric TEC impact</div>
              <div className="gps-value" id="gpsTec">--</div>
              <p className="gps-note">Geomagnetic storms raise TEC, degrading position models.</p>
            </article>
            <article className="gps-card">
              <div className="gps-title">Scintillation risk</div>
              <div className="gps-value" id="gpsScint">--</div>
              <p className="gps-note">Equatorial post‑sunset bubbles can disrupt receiver lock.</p>
            </article>
          </div>
          <div className="gps-footer" id="gpsNote">--</div>
        </section>

        <section className="satcom-panel" id="comms">
          <div className="chart-head">
            <div>
              <h2>Satellite Communications</h2>
              <p>Predicted signal degradation and outage risk based on space weather conditions.</p>
            </div>
            <div className="satcom-meta">
              <span id="satcomRisk">Risk: --</span>
            </div>
          </div>
          <div className="satcom-grid">
            <article className="satcom-card">
              <div className="satcom-title">UHF (300 MHz – 3 GHz)</div>
              <div className="satcom-value" id="satcomUhf">--</div>
              <p className="satcom-note">More sensitive to ionospheric delay and scintillation.</p>
            </article>
            <article className="satcom-card">
              <div className="satcom-title">SHF (3 – 30 GHz)</div>
              <div className="satcom-value" id="satcomShf">--</div>
              <p className="satcom-note">Lower delay but can suffer scintillation/absorption in storms.</p>
            </article>
            <article className="satcom-card">
              <div className="satcom-title">Link Stability</div>
              <div className="satcom-value" id="satcomStability">--</div>
              <p className="satcom-note">Risk of fades, phase jitter, and loss of lock.</p>
            </article>
            <article className="satcom-card">
              <div className="satcom-title">Outage Probability (24 h)</div>
              <div className="satcom-value" id="satcomOutage">--</div>
              <p className="satcom-note">Estimated from geomagnetic + storm model risk.</p>
            </article>
          </div>
          <div className="satcom-footer" id="satcomNote">--</div>
        </section>

        <div className="lightbox" id="lightbox" aria-hidden="true">
          <button className="lightbox-close" id="lightboxClose" aria-label="Close">×</button>
          <img id="lightboxImg" alt="Full size view" />
        </div>

        <section className="gallery-panel" id="feeds">
          <div className="chart-head">
            <div>
              <h2>Solar & Geospace Feeds</h2>
              <p>Live imagery and diagnostic plots from public feeds.</p>
            </div>
            <button id="refreshMediaBtn">Refresh Media</button>
          </div>
          <div className="gallery-grid">
            <article className="gallery-card">
              <div className="gallery-title">Auroral Oval (North)</div>
              <img id="imgAurora" alt="Auroral oval forecast" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg" />
            </article>
            <article className="gallery-card wide">
              <div className="gallery-title">Solar Wind (ACE)</div>
              <img id="imgSolarWind" alt="Solar wind plot" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/ace-mag-swepam-2-hour.gif" />
            </article>
            <article className="gallery-card wide">
              <div className="gallery-title">SWX Overview</div>
              <img id="imgSwx" alt="Space weather overview plot" loading="lazy"
                   src="https://services.swpc.noaa.gov/experimental/images/swx-overview-large.gif" />
            </article>
            <article className="gallery-card">
              <div className="gallery-title">Sunspots (HMI 4500)</div>
              <img id="imgSunspots" alt="Sunspot regions (HMI continuum)" loading="lazy"
                   src="https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_4500.jpg" />
            </article>
            <article className="gallery-card">
              <div className="gallery-title">Coronal Holes (AIA 193)</div>
              <img id="imgCoronal" alt="Coronal holes (AIA 193)" loading="lazy"
                   src="https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg" />
            </article>
            <article className="gallery-card">
              <div className="gallery-title">Solar Flares (AIA 131)</div>
              <img id="imgFlares" alt="Solar flares (AIA 131)" loading="lazy"
                   src="https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0131.jpg" />
            </article>
            <article className="gallery-card">
              <div className="gallery-title">CME (CCOR-1)</div>
              <img id="imgCcor1" alt="Latest CCOR-1 CME image" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/animations/ccor1/latest.jpg" />
            </article>
            <article className="gallery-card wide">
              <div className="gallery-title">Magnetometer (Boulder)</div>
              <img id="imgMag" alt="Magnetometer plot" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/boulder-magnetometer.png" />
            </article>
            <article className="gallery-card wide">
              <div className="gallery-title">Geospace Kp/Dst</div>
              <img id="imgGeospace" alt="Geospace Kp/Dst plot" loading="lazy"
                   src="https://services.swpc.noaa.gov/images/geospace/geospace_1_day.png" />
            </article>
            <article className="gallery-card">
              <div className="gallery-title">Synoptic Map</div>
              <img id="imgSynoptic" alt="Synoptic solar map" loading="lazy"
                   src="/api/proxy-image?url=https%3A%2F%2Fgong.nso.edu%2Fdata%2Fmagmap%2Fcorona%2Fgong_synoptic_map.jpg" />
            </article>
          </div>
        </section>

        <section className="footer-grid">
          <div className="footer-head">
            <div>
              <h2>Real-Time Panels</h2>
              <p>Compact monitoring views for quick scanning.</p>
            </div>
          </div>
          <div className="footer-panels">
            <article className="footer-card">
              <div className="footer-title">
                <span>Solar wind speed</span>
                <span className="footer-value" id="speedFoot">--</span>
              </div>
              <canvas id="chartSpeedFoot"></canvas>
            </article>
            <article className="footer-card">
              <div className="footer-title">
                <span>Bz GSM</span>
                <span className="footer-value" id="bzFoot">--</span>
              </div>
              <canvas id="chartBzFoot"></canvas>
            </article>
            <article className="footer-card">
              <div className="footer-title">
                <span>SYM/H</span>
                <span className="footer-value" id="symFoot">--</span>
              </div>
              <canvas id="chartSymFoot"></canvas>
            </article>
            <article className="footer-card">
              <div className="footer-title">
                <span>Kp Index</span>
                <span className="footer-value" id="kpFoot">--</span>
              </div>
              <div className="kp-pill" id="kpPill">--</div>
              <p className="note">Planetary K-index snapshot.</p>
            </article>
          </div>
        </section>

        <section className="details-panel">
          <div className="chart-head">
            <div>
              <h2>Deep Dives</h2>
              <p>Open full details for satellite risk, Earth impacts, and solar activity.</p>
            </div>
          </div>
          <div className="details-grid">
            <a className="details-card" href="/solar-wind">
              <div className="details-title">Solar Wind & IMF</div>
              <p>Speed, density, Bz trends, shocks and pressure.</p>
            </a>
            <a className="details-card" href="/kp-dst">
              <div className="details-title">Kp / Dst / SYM-H</div>
              <p>Storm intensity and geomagnetic indices.</p>
            </a>
            <a className="details-card" href="/flares">
              <div className="details-title">Solar Flares</div>
              <p>X-ray flux + latest flare context.</p>
            </a>
            <a className="details-card" href="/protons">
              <div className="details-title">Radiation (Protons)</div>
              <p>Energetic particle environment for satellites.</p>
            </a>
            <a className="details-card" href="/cme">
              <div className="details-title">CMEs</div>
              <p>Latest coronagraph imagery and alerts.</p>
            </a>
            <a className="details-card" href="/aurora">
              <div className="details-title">Auroral Oval</div>
              <p>Current and forecast auroral activity.</p>
            </a>
            <a className="details-card" href="/magnetometers">
              <div className="details-title">Magnetometers</div>
              <p>Ground magnetic field disturbances.</p>
            </a>
          </div>
        </section>
        </main>
      </div>

      <div id="chartTooltip" className="chart-tooltip" aria-hidden="true"></div>

      <Script src="/app.js" strategy="afterInteractive" />
    </>
  );
}
