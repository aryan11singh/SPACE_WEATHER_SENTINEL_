"""
Mock API server for Space Weather Sentinel.
Serves all endpoints with simulated data — no real data or models needed.
"""
import json
import math
import random
import time
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

random.seed(42)

# ── helpers ──────────────────────────────────────────────────────────────────

def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _ts(offset_min=0):
    dt = datetime.now(timezone.utc) + timedelta(minutes=offset_min)
    return dt.strftime("%Y-%m-%d %H:%M")

def _sin_wave(t, period=60, amp=1.0, offset=0.0):
    return offset + amp * math.sin(2 * math.pi * t / period)

def _noisy(base, noise=0.1):
    return base + random.gauss(0, noise)

# ── mock data generators ──────────────────────────────────────────────────────

def metrics_payload(qs=None):
    t = time.time()
    bz   = round(_noisy(_sin_wave(t, 120, 8, -3), 1.5), 2)
    spd  = round(_noisy(_sin_wave(t, 200, 80, 420), 10), 1)
    dens = round(max(0.1, _noisy(5.5, 1.2)), 2)
    storm_risk = round(max(0, min(1, _noisy(0.18, 0.04))), 4)
    symh_future = round(_noisy(-22, 5), 1)
    flare_prob  = round(max(0, min(1, _noisy(0.07, 0.02))), 4)
    kp_val = round(max(0, min(9, _noisy(2.3, 0.4))), 1)

    return {
        "time": _now_iso(),
        "storm_risk_prob": storm_risk,
        "symh_future": symh_future,
        "dst_future": symh_future,
        "flare_mx_prob": flare_prob,
        "flare_source": "mock",
        "flare_class": "B",
        "flare_flux": 3.2e-7,
        "bz_gsm": bz,
        "flow_speed": spd,
        "proton_density": dens,
        "sep_time": _now_iso(),
        "sep_flux": 0.12,
        "sep_energy": ">10 MeV",
        "sep_level": 0,
        "sep_label": "S0",
        "sep_risk": "None",
        "drag_time": _now_iso(),
        "drag_dtc_pred_3h": round(_noisy(180, 20), 1),
        "drag_level": "Low",
        "drag_accel_mps2": 2.1e-8,
        "drag_density_kgm3": 4.5e-13,
        "drag_orbit_speed_ms": 7784.0,
        "drag_ballistic_coeff": 44.4,
        "drag_proxy_ok": True,
        "sat_impact_time": _now_iso(),
        "sat_impact_prob": round(max(0, min(1, _noisy(0.05, 0.02))), 4),
        "sat_impact_level": "Low",
        "feature_spec_version": "mock-1.0",
    }

def kp_payload():
    kp = round(max(0, min(9, _noisy(2.3, 0.5))), 1)
    return {
        "time": _now_iso(),
        "kp": kp,
        "station_count": 13,
    }

def series_payload(minutes=720):
    n = min(minutes, 720)
    times, sym, bz, speed = [], [], [], []
    for i in range(n):
        offset = -(n - i)
        times.append(_ts(offset))
        sym.append(round(_noisy(_sin_wave(i, 180, 25, -15), 4), 1))
        bz.append(round(_noisy(_sin_wave(i, 90, 7, -2), 1.5), 2))
        speed.append(round(max(250, _noisy(_sin_wave(i, 240, 90, 420), 15)), 1))
    return {"time": times, "sym_h": sym, "bz_gsm": bz, "flow_speed": speed}

def alerts_payload():
    return {
        "items": [
            {
                "type": "info",
                "title": "Space Weather Message Code: WATA20",
                "message": "Geomagnetic K-index of 2 expected. No significant activity.",
                "issued": _now_iso(),
            },
            {
                "type": "watch",
                "title": "Solar Wind Speed Advisory",
                "message": "Solar wind speed currently at 420 km/s. Monitoring for elevated activity.",
                "issued": _now_iso(),
            },
        ]
    }

def aurora_payload():
    return {
        "risk": "Low",
        "kp_threshold": 5,
        "north_now": "https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
        "south_now": "https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg",
        "north_forecast": "https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg",
        "south_forecast": "https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg",
    }

def dst_series_payload(hours=168):
    n = min(hours, 720)
    times, real, pred = [], [], []
    for i in range(n):
        offset_h = -(n - i)
        dt = datetime.now(timezone.utc) + timedelta(hours=offset_h)
        times.append(dt.strftime("%Y-%m-%d %H:%M"))
        r = round(_noisy(_sin_wave(i, 72, 30, -10), 5), 1)
        real.append(r)
        pred.append(round(r + _noisy(0, 3), 1))
    return {"time": times, "dst_real": real, "dst_pred": pred}

def dst_forecast_payload():
    times, vals = [], []
    for i in range(72):
        dt = datetime.now(timezone.utc) + timedelta(hours=i)
        times.append(dt.strftime("%Y-%m-%d %H:%M"))
        vals.append(round(_noisy(_sin_wave(i, 48, 20, -8), 4), 1))
    return {
        "time": times,
        "dst_forecast": vals,
        "source": "mock-lstm",
        "note": "72-hour Dst forecast (simulated)",
    }

def dst_outlook_payload():
    times, dst_min, p25, p75 = [], [], [], []
    for i in range(30):
        dt = datetime.now(timezone.utc) + timedelta(days=i)
        times.append(dt.strftime("%Y-%m-%d"))
        base = _noisy(_sin_wave(i, 27, 25, -15), 5)
        dst_min.append(round(base, 1))
        p25.append(round(base - 10, 1))
        p75.append(round(base + 10, 1))
    return {
        "time": times,
        "dst_min_forecast": dst_min,
        "climo_p25": p25,
        "climo_p75": p75,
        "summary": "Quiet to unsettled conditions expected over the next 30 days.",
    }

def solar_wind_ml_payload():
    times, spd, dens, bz_vals = [], [], [], []
    for i in range(7):
        dt = datetime.now(timezone.utc) + timedelta(days=i)
        times.append(dt.strftime("%Y-%m-%d"))
        spd.append(round(_noisy(420 + i * 5, 20), 1))
        dens.append(round(max(0.5, _noisy(5.5, 1.0)), 2))
        bz_vals.append(round(_noisy(-2, 3), 2))
    return {
        "time": times,
        "speed": spd,
        "density": dens,
        "bz_gsm": bz_vals,
        "source": "mock-ml",
        "generated_at": _now_iso(),
    }

def enlil_payload():
    times, spd, dens, bz_vals = [], [], [], []
    for i in range(96):
        dt = datetime.now(timezone.utc) + timedelta(hours=i)
        times.append(dt.strftime("%Y-%m-%d %H:%M"))
        spd.append(round(_noisy(410 + i * 0.5, 25), 1))
        dens.append(round(max(0.5, _noisy(5.2, 1.2)), 2))
        bz_vals.append(round(_noisy(-1.5, 2.5), 2))
    return {
        "time": times,
        "speed": spd,
        "density": dens,
        "bz_gsm": bz_vals,
        "source": "mock-enlil",
        "generated_at": _now_iso(),
    }

def cme_payload():
    return {
        "event": {
            "start_time": (datetime.now(timezone.utc) - timedelta(hours=18)).isoformat(),
            "source_location": "N12W34",
            "active_region": 13456,
        },
        "features": {
            "speed": 780.0, "width": 120.0, "latitude": 12.0,
            "longitude": -34.0, "is_halo": 0,
        },
        "impact_prob": 0.31,
        "transit_hours": 52.4,
        "eta": (datetime.now(timezone.utc) + timedelta(hours=34)).isoformat(),
    }

def cme_climo_payload():
    probs = [0.08,0.09,0.11,0.13,0.15,0.17,0.18,0.16,0.14,0.12,0.10,0.09]
    return {
        "months": list(range(1, 13)),
        "probability": probs,
        "label": "Monthly Earth-impact probability (climatology)",
        "applies_to_years": [2026, 2027],
    }

def satellites_payload():
    return {
        "items": [
            {"id":"cubesat_3u","name":"CubeSat 3U","mass_kg":4.0,"area_m2":0.03,"cd":2.2,"alt_km":500},
            {"id":"cubesat_6u","name":"CubeSat 6U","mass_kg":12.0,"area_m2":0.05,"cd":2.2,"alt_km":500},
            {"id":"smallsat_100kg","name":"SmallSat 100 kg","mass_kg":100.0,"area_m2":1.0,"cd":2.2,"alt_km":550},
            {"id":"leo_500kg","name":"LEO Platform 500 kg","mass_kg":500.0,"area_m2":4.0,"cd":2.2,"alt_km":700},
            {"id":"leo_1000kg","name":"LEO Platform 1000 kg","mass_kg":1000.0,"area_m2":8.0,"cd":2.2,"alt_km":400},
        ]
    }

def health_payload():
    return {
        "status": "ok",
        "uptime_sec": int(time.time() % 86400),
        "models": {"storm": "ok", "symh": "ok", "flare": "ok", "drag": "ok"},
        "data_sources": {"omni_live": "mock", "kp": "mock", "xray": "mock"},
        "version": "mock-1.0",
    }

# ── router ────────────────────────────────────────────────────────────────────

ROUTES = {
    "/api/metrics":          lambda qs: metrics_payload(qs),
    "/api/kp":               lambda qs: kp_payload(),
    "/api/series":           lambda qs: series_payload(int(qs.get("minutes", ["720"])[0])),
    "/api/alerts":           lambda qs: alerts_payload(),
    "/api/aurora":           lambda qs: aurora_payload(),
    "/api/dst":              lambda qs: dst_series_payload(int(qs.get("hours", ["168"])[0])),
    "/api/dst-forecast":     lambda qs: dst_forecast_payload(),
    "/api/dst-outlook":      lambda qs: dst_outlook_payload(),
    "/api/solar-wind-ml":    lambda qs: solar_wind_ml_payload(),
    "/api/enlil":            lambda qs: enlil_payload(),
    "/api/cme":              lambda qs: cme_payload(),
    "/api/cme-climo":        lambda qs: cme_climo_payload(),
    "/api/cme-scenario":     lambda qs: cme_payload(),
    "/api/satellites":       lambda qs: satellites_payload(),
    "/api/health":           lambda qs: health_payload(),
}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence request logs

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        qs = parse_qs(parsed.query)

        # Serve static web files
        import os
        web_dir = os.path.join(os.path.dirname(__file__), "web")
        static_path = os.path.join(web_dir, path.lstrip("/")) if path else None

        if path in ("", "/"):
            static_path = os.path.join(web_dir, "index.html")

        if static_path and os.path.isfile(static_path):
            self._serve_file(static_path)
            return

        handler_fn = ROUTES.get(path)
        if handler_fn:
            try:
                data = handler_fn(qs)
                body = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self._cors()
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self._cors()
                self.end_headers()
                self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_file(self, path):
        import mimetypes
        mime, _ = mimetypes.guess_type(path)
        mime = mime or "application/octet-stream"
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    PORT = 8000
    print(f"Mock API + Web server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    server = ThreadingHTTPServer(("", PORT), Handler)
    server.serve_forever()
