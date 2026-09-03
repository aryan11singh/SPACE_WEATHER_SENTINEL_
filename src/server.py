import argparse
import json
import math
import os
import re
import time
import gzip
import tempfile
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, timezone
from collections import deque
from io import StringIO
from urllib.request import urlopen, Request

# Reduce noisy TF logs in API server.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import pandas as pd
import joblib
import numpy as np
import lightgbm as lgb

from build_dataset import FEATURE_COLS, add_rolling_features
from config import CONFIG
from data_quality import compute_quality

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROTON_MASS_KG = 1.6726219e-27


def _resolve_dir(env_key: str, default_path: str, fallback_path: str | None = None) -> str:
    value = os.environ.get(env_key)
    if value:
        path = value if os.path.isabs(value) else os.path.join(ROOT, value)
        return os.path.abspath(path)
    if os.path.isdir(default_path):
        return default_path
    if fallback_path and os.path.isdir(fallback_path):
        return fallback_path
    return default_path


def _feature_spec_version() -> str | None:
    path = CONFIG.feature_spec_path
    if not path or not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        return spec.get("version")
    except Exception:
        return None


DATA_DIR = _resolve_dir("DATA_DIR", os.path.join(ROOT, "data", "processed"))
MODEL_DIR = _resolve_dir("MODEL_DIR", os.path.join(ROOT, "models"), os.path.join(ROOT, "models_deploy"))
WEB_DIR = _resolve_dir("WEB_DIR", os.path.join(ROOT, "web"))

REQUEST_TIMEOUT = CONFIG.request_timeout_sec
START_TIME = time.time()

_REQUEST_STATS = {
    "count": 0,
    "errors": 0,
    "last_error": None,
    "last_request_ts": None,
    "last_latency_ms": None,
    "avg_latency_ms": None,
}
_RATE_LIMIT_STATE: dict[str, dict[str, float]] = {}


def _init_logger() -> logging.Logger:
    logger_obj = logging.getLogger("space-weather-api")
    if logger_obj.handlers:
        return logger_obj
    logger_obj.setLevel(logging.INFO)
    candidates = [
        os.path.join(CONFIG.log_dir, "api.log"),
        os.path.join(ROOT, "api.log"),
        os.path.join("/tmp", "space-weather-api.log"),
    ]
    for path in candidates:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            handler = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3)
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger_obj.addHandler(handler)
            logger_obj.info("logging to %s", path)
            return logger_obj
        except OSError:
            continue
    logger_obj.addHandler(logging.NullHandler())
    return logger_obj


logger = _init_logger()

SOLAR_CSV = os.path.join(DATA_DIR, "omni.csv")
SOLAR_LIVE_CSV = os.path.join(DATA_DIR, "omni_live.csv")
KP_URL = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
XRAY_URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
SOLAR_CYCLE_OBS_URL = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
SOLAR_CYCLE_PRED_URL = "https://services.swpc.noaa.gov/json/solar-cycle/predicted-solar-cycle.json"
SEP_URLS = [
    "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json",
    "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-7-day.json",
]
AWW_URL = "https://services.swpc.noaa.gov/products/alerts.json"
AURORA_NOW_URLS = [
    "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json",
]
AURORA_FORECAST_URLS = [
    "https://services.swpc.noaa.gov/json/ovation_aurora_forecast.json",
    "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json",
]
_AURORA_CACHE = {"ts": 0, "payload": None}
_AWW_CACHE = {"ts": 0, "payload": None}
DONKI_CME_URL = "https://kauai.ccmc.gsfc.nasa.gov/DONKI/WS/get/CME"

CME_IMPACT_MODEL_PATH = os.path.join(MODEL_DIR, "cme_impact_model.txt")
CME_TRANSIT_MODEL_PATH = os.path.join(MODEL_DIR, "cme_transit_model.txt")
CME_META_PATH = os.path.join(MODEL_DIR, "cme_impact_model_meta.json")
CME_DATASET_PATH = os.path.join(DATA_DIR, "cme_impact_dataset.csv")

_CME_MODEL_CACHE = {"impact": None, "transit": None, "meta": None, "ts": 0}
_CME_CATEGORY_CACHE = {"maps": None, "ts": 0}
_CME_CLIMO_CACHE = {"payload": None, "ts": 0}
_CME_LIVE_CACHE = {"payload": None, "ts": 0}
_XRAY_CACHE = {"ts": 0, "payload": None}
_SEP_CACHE = {"ts": 0, "payload": None}
_DRAG_CACHE = {"ts": 0, "payload": None}
_SAT_IMPACT_CACHE = {"ts": 0, "payload": None}
_SAT_IMPACT_MEANS_CACHE = {"ts": 0, "means": None, "cols": None}
_SOLAR_CYCLE_CACHE = {"ts": 0, "payload": None}
_METRICS_CACHE = {"ts": 0, "payload": None}
_DST_SERIES_CACHE = {"ts": 0, "key": None, "payload": None}
_DST_MODEL_CACHE = {"model": None, "meta": None, "path": None, "meta_path": None, "ts": 0}
_DST_LABELS_CACHE = {"df": None, "path": None, "ts": 0}
_DST_FORECAST_CACHE = {"ts": 0, "key": None, "payload": None}
_DST_OUTLOOK_CACHE = {"ts": 0, "payload": None}
_HEALTH_FULL_CACHE = {"ts": 0, "payload": None}
_SW_ML_CACHE = {"ts": 0, "payload": None, "key": None}
_SW_MODEL_CACHE = {"model": None, "meta": None, "path": None, "meta_path": None, "ts": 0}
_ENLIL_CACHE = {"ts": 0, "payload": None}
_SAT_PRESETS_CACHE = {"ts": 0, "payload": None}

_DRAG_DENSITY_TABLE = [
    (200.0, 2.78e-11),
    (250.0, 7.00e-12),
    (300.0, 2.40e-12),
    (350.0, 9.50e-13),
    (400.0, 3.70e-13),
    (450.0, 1.60e-13),
    (500.0, 8.00e-14),
    (550.0, 4.00e-14),
    (600.0, 2.00e-14),
    (700.0, 7.00e-15),
    (800.0, 3.00e-15),
    (900.0, 1.00e-15),
    (1000.0, 5.00e-16),
]

ENLIL_BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/wsa_enlil/prod/"
SATELLITE_CONFIG_PATH = os.path.join(ROOT, "configs", "satellites.json")


def _read_tail_csv(path: str, rows: int) -> pd.DataFrame:
    if rows <= 0:
        raise ValueError("rows must be positive")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        header = f.readline()
        buffer = deque(maxlen=rows)
        for line in f:
            buffer.append(line)
    data = header + "".join(buffer)
    df = pd.read_csv(StringIO(data), parse_dates=["time"])
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
    return df


def _load_latest_window(minutes: int = 180) -> pd.DataFrame:
    sources = []
    if os.path.exists(SOLAR_LIVE_CSV):
        sources.append(SOLAR_LIVE_CSV)
    if os.path.exists(SOLAR_CSV):
        sources.append(SOLAR_CSV)
    if not sources:
        raise FileNotFoundError("No solar wind source found. Provide omni.csv or omni_live.csv.")

    rows = max(minutes, 120)
    best_df = None
    best_ts = None
    now = pd.Timestamp.utcnow().tz_localize(None)
    for source in sources:
        df = _read_tail_csv(source, rows).sort_values("time")
        if df.empty or "time" not in df.columns:
            continue
        df = df[df["time"] <= now]
        if df.empty:
            continue
        last_ts = df["time"].iloc[-1]
        if best_ts is None or last_ts > best_ts:
            best_ts = last_ts
            best_df = df

    if best_df is None:
        raise RuntimeError("No valid solar wind rows found in data sources.")
    return best_df


def _latest_hour_features(feature_cols: list[str], fill_values: dict | None = None):
    sources = []
    if os.path.exists(SOLAR_LIVE_CSV):
        sources.append(SOLAR_LIVE_CSV)
    if os.path.exists(SOLAR_CSV):
        sources.append(SOLAR_CSV)
    if not sources:
        raise FileNotFoundError("No solar wind source found.")

    best_tail = None
    best_score = -1
    best_ts = None
    for source in sources:
        tail = _read_tail_csv(source, 5000).sort_values("time")
        if "time" not in tail.columns or tail.empty:
            continue
        # Score by how many required columns are present.
        present = sum(1 for col in feature_cols if col in tail.columns)
        last_ts = tail["time"].iloc[-1] if "time" in tail.columns and not tail.empty else None
        if present > best_score:
            best_tail = tail
            best_score = present
            best_ts = last_ts
        elif present == best_score and last_ts is not None:
            if best_ts is None or last_ts > best_ts:
                best_tail = tail
                best_ts = last_ts

    if best_tail is None or best_tail.empty:
        return None, None

    tail = best_tail.set_index("time")
    hourly = tail.resample("1h").mean(numeric_only=True)
    if hourly.empty:
        return None, None
    row = hourly.iloc[-1].copy()
    ts = hourly.index[-1]

    # Derive calendar fields when needed.
    if "year" in feature_cols:
        row["year"] = ts.year
    if "doy" in feature_cols:
        row["doy"] = int(ts.dayofyear)
    if "hour" in feature_cols:
        row["hour"] = ts.hour
    if "minute" in feature_cols:
        row["minute"] = ts.minute

    # Fill missing with last valid values from the tail.
    for col in feature_cols:
        if col not in row.index:
            row[col] = np.nan
        if pd.isna(row[col]) and col in tail.columns:
            series = pd.to_numeric(tail[col], errors="coerce").dropna()
            if not series.empty:
                row[col] = series.iloc[-1]

    # Final fallback: fill any remaining missing with 0.0 so the model stays online.
    missing = [c for c in feature_cols if pd.isna(row.get(c))]
    if missing:
        for col in missing:
            if fill_values and col in fill_values and pd.notna(fill_values[col]):
                row[col] = float(fill_values[col])
            else:
                row[col] = 0.0
    return row, ts


def _load_cme_models():
    now = time.time()
    if _CME_MODEL_CACHE["impact"] and now - _CME_MODEL_CACHE["ts"] < 300:
        return _CME_MODEL_CACHE["impact"], _CME_MODEL_CACHE["transit"], _CME_MODEL_CACHE["meta"]

    impact = None
    transit = None
    meta = None
    if os.path.exists(CME_IMPACT_MODEL_PATH):
        impact = lgb.Booster(model_file=CME_IMPACT_MODEL_PATH)
    if os.path.exists(CME_TRANSIT_MODEL_PATH):
        transit = lgb.Booster(model_file=CME_TRANSIT_MODEL_PATH)
    if os.path.exists(CME_META_PATH):
        try:
            with open(CME_META_PATH, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = None

    _CME_MODEL_CACHE["impact"] = impact
    _CME_MODEL_CACHE["transit"] = transit
    _CME_MODEL_CACHE["meta"] = meta
    _CME_MODEL_CACHE["ts"] = now
    return impact, transit, meta


def _load_cme_category_maps():
    now = time.time()
    if _CME_CATEGORY_CACHE["maps"] and now - _CME_CATEGORY_CACHE["ts"] < 3600:
        return _CME_CATEGORY_CACHE["maps"]
    maps: dict[str, dict[str, int]] = {}
    if os.path.exists(CME_DATASET_PATH):
        df = pd.read_csv(CME_DATASET_PATH, usecols=["catalog", "cme_type"], dtype=str)
        for col in ("catalog", "cme_type"):
            series = df[col].fillna("").astype(str)
            cat = series.astype("category")
            maps[col] = {str(val): int(idx) for idx, val in enumerate(cat.cat.categories)}
    _CME_CATEGORY_CACHE["maps"] = maps
    _CME_CATEGORY_CACHE["ts"] = now
    return maps


def _encode_cme_features(features: dict, feature_cols: list[str], cat_maps: dict[str, dict[str, int]]):
    row = {}
    for col in feature_cols:
        if col in ("catalog", "cme_type"):
            raw = features.get(col)
            raw_key = "" if raw is None else str(raw)
            mapping = cat_maps.get(col, {})
            row[col] = mapping.get(raw_key, np.nan)
        else:
            row[col] = features.get(col, np.nan)
    return pd.DataFrame([row]).to_numpy(dtype=np.float32)


def _parse_source_location(loc: str):
    if not isinstance(loc, str) or not loc:
        return np.nan, np.nan
    match = re.match(r"^([NS])(\d{1,2})([EW])(\d{1,3})$", loc.strip())
    if match:
        lat = int(match.group(2)) * (1 if match.group(1) == "N" else -1)
        lon = int(match.group(4)) * (1 if match.group(3) == "W" else -1)
        return lat, lon
    match = re.match(r"^([NS])(\d{1,2})$", loc.strip())
    if match:
        lat = int(match.group(2)) * (1 if match.group(1) == "N" else -1)
        return lat, np.nan
    match = re.match(r"^([EW])(\d{1,3})$", loc.strip())
    if match:
        lon = int(match.group(2)) * (1 if match.group(1) == "W" else -1)
        return np.nan, lon
    return np.nan, np.nan


def _pick_cme_analysis(item: dict):
    analyses = item.get("cmeAnalyses") or []
    if not analyses:
        return {}
    for entry in analyses:
        if entry.get("isMostAccurate"):
            return entry
    return analyses[0]


def _build_cme_features_from_event(event: dict):
    analysis = _pick_cme_analysis(event)
    speed = pd.to_numeric(analysis.get("speed"), errors="coerce")
    half_angle = pd.to_numeric(analysis.get("halfAngle"), errors="coerce")
    lat = pd.to_numeric(analysis.get("latitude"), errors="coerce")
    lon = pd.to_numeric(analysis.get("longitude"), errors="coerce")
    if pd.isna(lat) or pd.isna(lon):
        src_lat, src_lon = _parse_source_location(event.get("sourceLocation"))
        if pd.isna(lat):
            lat = src_lat
        if pd.isna(lon):
            lon = src_lon
    width = half_angle * 2 if pd.notna(half_angle) else np.nan
    is_halo = 1 if pd.notna(width) and width >= 360 else 0
    transit_pred_hours = 149597870.7 / (speed * 3600.0) if pd.notna(speed) and speed > 0 else np.nan

    return {
        "speed": speed,
        "half_angle": half_angle,
        "width": width,
        "latitude": lat,
        "longitude": lon,
        "is_halo": is_halo,
        "active_region": pd.to_numeric(event.get("activeRegionNum"), errors="coerce"),
        "catalog": event.get("catalog"),
        "cme_type": analysis.get("type"),
        "transit_pred_hours": transit_pred_hours,
    }


def _predict_cme(features: dict):
    impact_model, transit_model, meta = _load_cme_models()
    if impact_model is None:
        return None
    feature_cols = meta.get("feature_cols") if meta else None
    if not feature_cols:
        feature_cols = [
            "speed",
            "half_angle",
            "width",
            "latitude",
            "longitude",
            "is_halo",
            "active_region",
            "catalog",
            "cme_type",
            "transit_pred_hours",
        ]
    cat_maps = _load_cme_category_maps()
    X = _encode_cme_features(features, feature_cols, cat_maps)
    impact_prob = float(impact_model.predict(X)[0])
    transit_hours = None
    if transit_model is not None and np.isfinite(impact_prob):
        transit_hours = float(transit_model.predict(X)[0])
    return impact_prob, transit_hours


def _fetch_latest_cme(days: int = 7):
    now = datetime.utcnow()
    start = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    url = f"{DONKI_CME_URL}?startDate={start}&endDate={end}"
    req = Request(url, headers={"User-Agent": "space-weather-sentinel/1.0"})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload:
        return None
    # pick latest event with valid speed/halfAngle
    def _ts(item):
        return pd.to_datetime(item.get("startTime"), errors="coerce")
    payload = sorted(payload, key=_ts)
    for item in reversed(payload):
        analysis = _pick_cme_analysis(item)
        speed = pd.to_numeric(analysis.get("speed"), errors="coerce")
        half_angle = pd.to_numeric(analysis.get("halfAngle"), errors="coerce")
        if pd.notna(speed) and pd.notna(half_angle):
            return item
    return payload[-1]


def _cme_live_payload():
    now = time.time()
    if _CME_LIVE_CACHE["payload"] and now - _CME_LIVE_CACHE["ts"] < 300:
        return _CME_LIVE_CACHE["payload"]

    event = _fetch_latest_cme()
    if not event:
        return {"error": "No CME events returned."}
    features = _build_cme_features_from_event(event)
    pred = _predict_cme(features)
    if pred is None:
        return {"error": "CME model not available."}
    impact_prob, transit_hours = pred
    start_time = pd.to_datetime(event.get("startTime"), errors="coerce")
    eta = None
    if pd.notna(start_time) and transit_hours is not None and np.isfinite(transit_hours):
        eta = (start_time + timedelta(hours=transit_hours)).isoformat()
    payload = {
        "event": {
            "start_time": start_time.isoformat() if pd.notna(start_time) else None,
            "source_location": event.get("sourceLocation"),
            "active_region": event.get("activeRegionNum"),
        },
        "features": features,
        "impact_prob": impact_prob,
        "transit_hours": transit_hours,
        "eta": eta,
    }
    _CME_LIVE_CACHE["payload"] = payload
    _CME_LIVE_CACHE["ts"] = now
    return payload


def _cme_climatology_payload():
    now = time.time()
    if _CME_CLIMO_CACHE["payload"] and now - _CME_CLIMO_CACHE["ts"] < 3600:
        return _CME_CLIMO_CACHE["payload"]
    if not os.path.exists(CME_DATASET_PATH):
        return {"error": "CME dataset not found."}
    df = pd.read_csv(CME_DATASET_PATH, parse_dates=["time"])
    df = df.dropna(subset=["time"])
    df["month"] = df["time"].dt.month
    probs = df.groupby("month")["earth_impact"].mean()
    series = [float(probs.get(m, np.nan)) for m in range(1, 13)]
    payload = {
        "months": list(range(1, 13)),
        "probability": series,
        "label": "Monthly Earth-impact probability (climatology)",
        "applies_to_years": [2026, 2027],
    }
    _CME_CLIMO_CACHE["payload"] = payload
    _CME_CLIMO_CACHE["ts"] = now
    return payload


def _cme_scenario_payload(qs):
    def _get_float(key, default=None):
        if key not in qs:
            return default
        try:
            return float(qs.get(key, [default])[0])
        except Exception:
            return default
    speed = _get_float("speed")
    half_angle = _get_float("half_angle")
    width = _get_float("width")
    lat = _get_float("latitude")
    lon = _get_float("longitude")
    is_halo = _get_float("is_halo")
    active_region = _get_float("active_region")
    catalog = qs.get("catalog", [None])[0]
    cme_type = qs.get("cme_type", [None])[0]

    if width is None and half_angle is not None:
        width = half_angle * 2
    if is_halo is None and width is not None:
        is_halo = 1 if width >= 360 else 0
    transit_pred_hours = 149597870.7 / (speed * 3600.0) if speed and speed > 0 else np.nan

    features = {
        "speed": speed,
        "half_angle": half_angle,
        "width": width,
        "latitude": lat,
        "longitude": lon,
        "is_halo": is_halo,
        "active_region": active_region,
        "catalog": catalog,
        "cme_type": cme_type,
        "transit_pred_hours": transit_pred_hours,
    }
    pred = _predict_cme(features)
    if pred is None:
        return {"error": "CME model not available."}
    impact_prob, transit_hours = pred
    return {
        "features": features,
        "impact_prob": impact_prob,
        "transit_hours": transit_hours,
    }


def _make_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("time").set_index("time")
    base = df[FEATURE_COLS].copy()
    feat_15 = add_rolling_features(df, window=15, prefix="w15")
    feat_60 = add_rolling_features(df, window=60, prefix="w60")
    features = pd.concat([base, feat_15, feat_60], axis=1)
    return features


def _prepare_input(bundle: dict, latest: pd.DataFrame):
    features = bundle["features"]
    X = latest[features]
    scaler = bundle.get("scaler")
    if scaler is None:
        return X
    X = X.fillna(0.0)
    X = X.to_numpy(dtype=np.float32)
    return scaler.transform(X)


def _predict_proba(bundle, X):
    model = bundle["model"]
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[:, 1]
    else:
        probs = model.predict(X)
    calibrator = bundle.get("calibrator")
    if calibrator is not None:
        probs = calibrator.predict(probs)
    return probs


def _predict_value(model, X):
    return model.predict(X)


def _predict_latest(sat_cfg: dict | None = None):
    cached = _METRICS_CACHE.get("payload")
    if cached and time.time() - _METRICS_CACHE.get("ts", 0) <= CONFIG.cache_ttl_sec:
        return cached
    latest_window = _load_latest_window(180)
    latest_window = _clean_series_values(latest_window)
    features = _make_features(latest_window)
    latest = features.iloc[-1:]

    storm = joblib.load(os.path.join(MODEL_DIR, "storm_model.joblib"))
    symh = joblib.load(os.path.join(MODEL_DIR, "symh_model.joblib"))
    storm_X = _prepare_input(storm, latest)
    symh_X = _prepare_input(symh, latest)
    storm_prob = float(_predict_proba(storm, storm_X)[0])
    symh_future = float(_predict_value(symh["model"], symh_X)[0])

    flare_prob = None
    flare_source = "model"
    flare_class = None
    flare_flux = None
    flare_path = os.path.join(MODEL_DIR, "flare_model.joblib")

    xray = None
    try:
        xray = _fetch_goes_xray()
        flare_flux = xray.get("flux")
        flare_class = _flux_to_flare_class(flare_flux)
    except Exception:
        xray = None

    if os.path.exists(flare_path):
        flare = joblib.load(flare_path)
        flare_X = _prepare_input(flare, latest)
        flare_prob = float(_predict_proba(flare, flare_X)[0])

    # Fallback: use X-ray flux proxy if model is missing or near-zero
    if (flare_prob is None or flare_prob < 1e-6) and flare_flux is not None:
        flux = flare_flux
        if flux >= 1e-4:
            flare_prob = 0.95  # X-class range
        elif flux >= 1e-5:
            flare_prob = 0.7   # M-class range
        elif flux >= 1e-6:
            flare_prob = 0.35  # C-class range
        elif flux >= 1e-7:
            flare_prob = 0.08  # B-class range
        else:
            flare_prob = 0.01  # A-class range
        flare_source = "goes_xray"

    sep_payload = None
    try:
        sep_payload = _fetch_sep()
    except Exception:
        sep_payload = None

    drag_payload = None
    try:
        drag_payload = _fetch_drag()
    except Exception:
        drag_payload = None

    sat_payload = None
    try:
        sat_payload = _fetch_sat_impact()
    except Exception:
        sat_payload = None

    current = latest_window.iloc[-1]
    # Use a wider tail for live values in case recent rows are all NaN.
    source = SOLAR_LIVE_CSV if os.path.exists(SOLAR_LIVE_CSV) else SOLAR_CSV
    live_tail = _read_tail_csv(source, 5000).sort_values("time")

    def _last_valid(col: str):
        if col not in live_tail.columns:
            return float("nan")
        series = pd.to_numeric(live_tail[col], errors="coerce")
        series = series.dropna()
        if series.empty:
            return float("nan")
        return float(series.iloc[-1])

    raw_time = current.get("time")
    time_utc = pd.to_datetime(raw_time, errors="coerce", utc=True)
    if pd.notna(time_utc):
        time_str = time_utc.isoformat().replace("+00:00", "Z")
    else:
        time_str = str(raw_time)
    payload = {
        "time": time_str,
        "storm_risk_prob": storm_prob,
        "symh_future": symh_future,
        "dst_future": symh_future,
        "flare_mx_prob": flare_prob,
        "flare_source": flare_source,
        "flare_class": flare_class,
        "flare_flux": flare_flux,
        "bz_gsm": _last_valid("bz_gsm"),
        "flow_speed": _last_valid("flow_speed"),
        "proton_density": _last_valid("proton_density"),
    }
    payload["feature_spec_version"] = _feature_spec_version()
    payload["drag_proxy_ok"] = drag_payload is not None
    _METRICS_CACHE["ts"] = time.time()
    _METRICS_CACHE["payload"] = payload
    if sep_payload:
        payload.update(
            {
                "sep_time": sep_payload.get("time"),
                "sep_flux": sep_payload.get("flux"),
                "sep_energy": sep_payload.get("energy"),
                "sep_level": sep_payload.get("level"),
                "sep_label": sep_payload.get("label"),
                "sep_risk": sep_payload.get("risk"),
            }
        )
    if drag_payload:
        payload.update(
            {
                "drag_time": drag_payload.get("time"),
                "drag_dtc_pred_3h": drag_payload.get("dtc_pred_3h"),
                "drag_level": drag_payload.get("level"),
            }
        )

    dtc_value = drag_payload.get("dtc_pred_3h") if drag_payload else None
    drag_est = _estimate_drag(sat_cfg, dtc_value)
    if drag_est:
        payload.update(
            {
                "drag_accel_mps2": drag_est.get("accel_mps2"),
                "drag_density_kgm3": drag_est.get("density_kgm3"),
                "drag_orbit_speed_ms": drag_est.get("orbital_speed_ms"),
                "drag_ballistic_coeff": drag_est.get("ballistic_coeff"),
                "drag_satellite": sat_cfg,
                "drag_proxy_ok": drag_payload is not None,
            }
        )
    if sat_payload:
        payload.update(
            {
                "sat_impact_time": sat_payload.get("time"),
                "sat_impact_prob": sat_payload.get("prob"),
                "sat_impact_level": sat_payload.get("level"),
            }
        )
    return payload


def _clean_series_values(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    for col in ("sym_h", "bz_gsm", "flow_speed"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    # Drop obvious sentinel/outlier values.
    if "flow_speed" in out.columns:
        out.loc[(out["flow_speed"] > 5000) | (out["flow_speed"] < 0), "flow_speed"] = np.nan
    if "bz_gsm" in out.columns:
        out.loc[out["bz_gsm"].abs() > 200, "bz_gsm"] = np.nan
    if "sym_h" in out.columns:
        out.loc[out["sym_h"].abs() > 2000, "sym_h"] = np.nan
    return out


def _series(minutes: int = 720):
    # Prefer live omni if it's recent; fallback to historical.
    sources = []
    if os.path.exists(SOLAR_LIVE_CSV):
        sources.append(SOLAR_LIVE_CSV)
    if os.path.exists(SOLAR_CSV):
        sources.append(SOLAR_CSV)
    if not sources:
        raise FileNotFoundError("No omni source found for series data.")

    now = pd.Timestamp.utcnow().tz_localize(None)
    scan_rows = max(minutes, 120) * 20
    df = pd.DataFrame()
    for source in sources:
        candidate = _read_tail_csv(source, scan_rows).sort_values("time")
        if candidate.empty:
            continue
        candidate = candidate[candidate["time"] <= now]
        candidate = _clean_series_values(candidate)
        # Require at least some non-null points for bz or speed.
        cols = [c for c in ("bz_gsm", "flow_speed") if c in candidate.columns]
        if cols and candidate[cols].notna().any(axis=None):
            df = candidate
            break
    if df.empty:
        raise RuntimeError("No valid series data available.")
    sym = df.get("sym_h")
    bz = df.get("bz_gsm")
    speed = df.get("flow_speed")

    if sym is None:
        sym = pd.Series([np.nan] * len(df))
    # Fallback: if SYM/H is missing, use Kyoto Dst as proxy (hourly forward-filled).
    if sym.isna().all():
        dst_csv = os.path.join(ROOT, "data", "indices", "kyoto", "dst_hourly.csv")
        if os.path.exists(dst_csv):
            try:
                dst_df = _load_dst_labels(dst_csv)
                aligned = dst_df.reindex(df["time"], method="ffill")["dst_kyoto"].to_numpy()
                sym = pd.Series(aligned, index=df.index)
            except Exception:
                pass
    if bz is None:
        bz = pd.Series([np.nan] * len(df))
    if speed is None:
        speed = pd.Series([np.nan] * len(df))

    mask = ~(sym.isna() & bz.isna() & speed.isna())
    df = df.loc[mask]
    sym = sym.loc[mask]
    bz = bz.loc[mask]
    speed = speed.loc[mask]

    if len(df) > minutes:
        df = df.tail(minutes)
        sym = sym.tail(minutes)
        bz = bz.tail(minutes)
        speed = speed.tail(minutes)

    return {
        "time": df["time"].dt.strftime("%Y-%m-%d %H:%M").tolist(),
        "sym_h": sym.astype(float).tolist(),
        "bz_gsm": bz.astype(float).tolist(),
        "flow_speed": speed.astype(float).tolist(),
    }


def _fetch_kp():
    req = Request(KP_URL, headers={"User-Agent": "space-weather-sentinel/1.0"})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if not payload:
        raise ValueError("Empty Kp payload")
    # New API: list-of-dicts  {"time_tag":..., "Kp":..., "station_count":...}
    if isinstance(payload[0], dict):
        latest = payload[-1]
        time_str = str(latest.get("time_tag", "")).replace(" ", "T")
        if time_str and not time_str.endswith("Z"):
            time_str += "Z"
        return {
            "time": time_str,
            "kp": float(latest["Kp"]),
            "station_count": int(latest["station_count"]) if latest.get("station_count") is not None else None,
        }
    # Legacy API: array-of-arrays  [["time_tag","Kp",...], [...], ...]
    if len(payload) < 2:
        raise ValueError("Empty Kp payload")
    header = payload[0]
    rows = payload[1:]
    idx_time = header.index("time_tag")
    idx_kp = header.index("Kp")
    idx_station = header.index("station_count") if "station_count" in header else None
    latest = rows[-1]
    return {
        "time": latest[idx_time].replace(" ", "T") + "Z",
        "kp": float(latest[idx_kp]),
        "station_count": int(latest[idx_station]) if idx_station is not None else None,
    }


def _is_long_xray_channel(value) -> bool:
    if value is None:
        return False
    s = str(value).strip().lower()
    if not s:
        return False
    s = s.replace(" ", "")
    s = s.replace("nm", "")
    s = s.replace("å", "a")
    s = s.replace("angstrom", "a")
    # X-ray long channel is 0.1-0.8 nm (1-8 Å).
    return "0.1-0.8" in s or "1-8" in s


def _parse_xray_payload(payload) -> list[dict]:
    records = []
    if not payload:
        return records

    if isinstance(payload, list) and payload and isinstance(payload[0], list):
        header = payload[0]
        rows = payload[1:]
        header_map = {str(name): idx for idx, name in enumerate(header)}
        idx_time = header_map.get("time_tag") or header_map.get("time") or header_map.get("timestamp")
        idx_energy = header_map.get("energy") or header_map.get("energy_range") or header_map.get("energy_channel")
        idx_flux = header_map.get("flux") or header_map.get("flux_short") or header_map.get("value")
        for row in rows:
            if not isinstance(row, list):
                continue
            time_tag = row[idx_time] if idx_time is not None and idx_time < len(row) else None
            energy = row[idx_energy] if idx_energy is not None and idx_energy < len(row) else None
            flux = row[idx_flux] if idx_flux is not None and idx_flux < len(row) else None
            records.append({"time_tag": time_tag, "energy": energy, "flux": flux})
        return records

    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        for row in payload:
            time_tag = row.get("time_tag") or row.get("time") or row.get("timestamp")
            energy = row.get("energy") or row.get("energy_range") or row.get("energy_channel")
            flux = row.get("flux") or row.get("flux_short") or row.get("value")
            records.append({"time_tag": time_tag, "energy": energy, "flux": flux})
    return records


def _pick_xray_record(records: list[dict]) -> dict | None:
    parsed = []
    for rec in records:
        time_tag = rec.get("time_tag")
        if not time_tag:
            continue
        time_dt = pd.to_datetime(time_tag, errors="coerce", utc=True)
        if pd.isna(time_dt):
            continue
        flux_val = rec.get("flux")
        try:
            flux_val = float(flux_val)
        except (TypeError, ValueError):
            flux_val = math.nan
        if not math.isfinite(flux_val) or flux_val < 0:
            flux_val = math.nan
        energy = rec.get("energy")
        parsed.append(
            {
                "time": time_dt,
                "flux": flux_val,
                "energy": energy,
                "is_long": _is_long_xray_channel(energy),
            }
        )

    if not parsed:
        return None

    # Prefer the latest long-channel record with a finite flux.
    long_valid = [item for item in parsed if item["is_long"] and math.isfinite(item["flux"])]
    if long_valid:
        latest_time = max(item["time"] for item in long_valid)
        latest = [item for item in long_valid if item["time"] == latest_time]
        return latest[-1]

    # Otherwise, fall back to any latest finite flux.
    valid = [item for item in parsed if math.isfinite(item["flux"])]
    if valid:
        latest_time = max(item["time"] for item in valid)
        latest = [item for item in valid if item["time"] == latest_time]
        return latest[-1]

    # Final fallback: just return the latest record.
    latest_time = max(item["time"] for item in parsed)
    latest = [item for item in parsed if item["time"] == latest_time]
    return latest[-1]


def _fetch_goes_xray():
    now = time.time()
    if _XRAY_CACHE["payload"] and now - _XRAY_CACHE["ts"] < 60:
        return _XRAY_CACHE["payload"]
    req = Request(XRAY_URL, headers={"User-Agent": "space-weather-sentinel/1.0"})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    records = _parse_xray_payload(payload)
    latest = _pick_xray_record(records)
    if not latest:
        raise ValueError("Empty X-ray payload")
    time_tag = latest["time"]
    flux = latest["flux"]
    if pd.isna(time_tag) or not math.isfinite(flux):
        raise ValueError("Invalid X-ray payload")
    out = {
        "time": time_tag.isoformat().replace("+00:00", "Z"),
        "flux": float(flux),
    }
    _XRAY_CACHE["payload"] = out
    _XRAY_CACHE["ts"] = now
    return out


def _flux_to_flare_class(flux: float | None) -> str | None:
    if flux is None or not math.isfinite(flux):
        return None
    if flux >= 1e-4:
        return "X"
    if flux >= 1e-5:
        return "M"
    if flux >= 1e-6:
        return "C"
    if flux >= 1e-7:
        return "B"
    return "A"


def _parse_energy_lower(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().lower()
    if not s:
        return None
    s = s.replace("mev", "")
    s = s.replace(" ", "")
    s = s.replace("–", "-")
    if s.startswith(">="):
        s = s[2:]
    if "-" in s:
        s = s.split("-", 1)[0]
    if s.endswith("+"):
        s = s[:-1]
    try:
        return float(s)
    except ValueError:
        return None


def _parse_sep_payload(payload) -> list[dict]:
    records = []
    if not payload:
        return records

    def _extract_list(row, header_map, keys):
        for key in keys:
            idx = header_map.get(key)
            if idx is not None and idx < len(row):
                return row[idx]
        return None

    if isinstance(payload[0], list):
        header = payload[0]
        rows = payload[1:]
        header_map = {str(name): idx for idx, name in enumerate(header)}
        for row in rows:
            if not isinstance(row, list):
                continue
            time_tag = _extract_list(row, header_map, ["time_tag", "time", "timestamp"])
            energy = _extract_list(row, header_map, ["energy", "energy_range", "energy_channel"])
            flux = _extract_list(row, header_map, ["flux", "flux_pfu", "value", "pfu"])
            records.append({"time_tag": time_tag, "energy": energy, "flux": flux})
        return records

    if isinstance(payload[0], dict):
        for row in payload:
            time_tag = row.get("time_tag") or row.get("time") or row.get("timestamp")
            energy = row.get("energy") or row.get("energy_range") or row.get("energy_channel")
            flux = row.get("flux") or row.get("flux_pfu") or row.get("value") or row.get("pfu")
            records.append({"time_tag": time_tag, "energy": energy, "flux": flux})
    return records


def _pick_sep_record(records: list[dict]) -> dict | None:
    parsed = []
    for rec in records:
        time_tag = rec.get("time_tag")
        if not time_tag:
            continue
        time_dt = pd.to_datetime(time_tag, errors="coerce", utc=True)
        if pd.isna(time_dt):
            continue
        flux = rec.get("flux")
        try:
            flux_val = float(flux)
        except (TypeError, ValueError):
            flux_val = math.nan
        if not math.isfinite(flux_val) or flux_val < 0:
            flux_val = math.nan
        energy_low = _parse_energy_lower(rec.get("energy"))
        parsed.append(
            {
                "time": time_dt,
                "flux": flux_val,
                "energy": rec.get("energy"),
                "energy_low": energy_low,
            }
        )

    if not parsed:
        return None

    # Prefer the most recent record that has a finite flux value.
    valid = [item for item in parsed if math.isfinite(item["flux"])]
    if valid:
        latest_time = max(item["time"] for item in valid)
        latest = [item for item in valid if item["time"] == latest_time]
    else:
        latest_time = max(item["time"] for item in parsed)
        latest = [item for item in parsed if item["time"] == latest_time]

    def _score(item):
        if item["energy_low"] is None:
            return 999.0
        return abs(item["energy_low"] - 10.0)

    return min(latest, key=_score)


def _sep_level(flux: float | None) -> tuple[int | None, str | None]:
    if flux is None or not math.isfinite(flux):
        return None, None
    if flux >= 100000:
        return 5, "S5 Extreme"
    if flux >= 10000:
        return 4, "S4 Severe"
    if flux >= 1000:
        return 3, "S3 Strong"
    if flux >= 100:
        return 2, "S2 Moderate"
    if flux >= 10:
        return 1, "S1 Minor"
    return 0, "S0 Quiet"


def _sep_risk(flux: float | None) -> float | None:
    if flux is None or not math.isfinite(flux):
        return None
    if flux <= 0:
        return 0.0
    return min(1.0, max(0.0, (math.log10(flux) - 1.0) / 4.0))


def _fetch_sep():
    now = time.time()
    if _SEP_CACHE["payload"] and now - _SEP_CACHE["ts"] < 120:
        return _SEP_CACHE["payload"]
    last_err = None
    for url in SEP_URLS:
        try:
            data = _fetch_url(url)
            records = _parse_sep_payload(data)
            rec = _pick_sep_record(records)
            if rec is None:
                raise ValueError("No SEP records parsed")
            flux = rec["flux"]
            level, label = _sep_level(flux)
            payload = {
                "time": rec["time"].isoformat().replace("+00:00", "Z"),
                "flux": flux if math.isfinite(flux) else None,
                "energy": rec["energy"],
                "level": level,
                "label": label,
                "risk": _sep_risk(flux),
            }
            _SEP_CACHE["payload"] = payload
            _SEP_CACHE["ts"] = now
            return payload
        except Exception as exc:
            last_err = exc
    raise last_err or RuntimeError("SEP fetch failed")


def _drag_level(value: float | None) -> str | None:
    if value is None or not math.isfinite(value):
        return None
    if value >= 100:
        return "Severe"
    if value >= 60:
        return "High"
    if value >= 30:
        return "Elevated"
    return "Low"


def _impact_level(prob: float | None) -> str | None:
    if prob is None or not math.isfinite(prob):
        return None
    if prob >= 0.7:
        return "High"
    if prob >= 0.4:
        return "Elevated"
    return "Low"


def _fetch_drag():
    now = time.time()
    if _DRAG_CACHE["payload"] and now - _DRAG_CACHE["ts"] < 300:
        return _DRAG_CACHE["payload"]
    model_path = os.path.join(MODEL_DIR, "drag_model.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError("Missing drag model")
    from predict_drag import predict as predict_drag

    indices_dir = os.path.join(ROOT, "data", "indices", "jb2008")
    swall_path = os.path.join(indices_dir, "SW-All.csv")
    payload = predict_drag(indices_dir, swall_path, MODEL_DIR)
    level = _drag_level(payload.get("dtc_pred_3h"))
    out = {
        "time": payload.get("time"),
        "dtc_pred_3h": payload.get("dtc_pred_3h"),
        "level": level,
    }
    _DRAG_CACHE["payload"] = out
    _DRAG_CACHE["ts"] = now
    return out


def _fetch_sat_impact():
    now = time.time()
    if _SAT_IMPACT_CACHE["payload"] and now - _SAT_IMPACT_CACHE["ts"] < 300:
        return _SAT_IMPACT_CACHE["payload"]

    model_path = os.path.join(MODEL_DIR, "sat_impact_model.txt")
    meta_path = os.path.join(MODEL_DIR, "sat_impact_model_meta.json")
    if not os.path.exists(model_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Missing satellite impact model or metadata")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    feature_cols = meta.get("feature_cols")
    if not feature_cols:
        raise ValueError("Satellite impact meta missing feature_cols")

    feature_means = _load_sat_impact_means(feature_cols, meta)
    row, ts = _latest_hour_features(feature_cols, fill_values=feature_means)
    if row is None or ts is None:
        raise ValueError("Not enough recent solar wind data for satellite impact")

    import lightgbm as lgb

    model = lgb.Booster(model_file=model_path)
    X = row[feature_cols].to_numpy(dtype=np.float32).reshape(1, -1)
    prob = float(model.predict(X)[0])
    level = _impact_level(prob)
    payload = {
        "time": pd.Timestamp(ts).isoformat(),
        "prob": prob,
        "level": level,
    }
    _SAT_IMPACT_CACHE["payload"] = payload
    _SAT_IMPACT_CACHE["ts"] = now
    return payload


def _load_dst_assets():
    candidates = [
        ("dst_lstm_realtime.keras", "dst_lstm_realtime_meta.json"),
        ("dst_lstm_attention.keras", "dst_lstm_attention_meta.json"),
    ]
    model_path = None
    meta_path = None
    for model_name, meta_name in candidates:
        mp = os.path.join(MODEL_DIR, model_name)
        mt = os.path.join(MODEL_DIR, meta_name)
        if os.path.exists(mp) and os.path.exists(mt):
            model_path = mp
            meta_path = mt
            break
    if model_path is None or meta_path is None:
        raise FileNotFoundError("Dst model or metadata missing")

    if (
        _DST_MODEL_CACHE["model"] is not None
        and _DST_MODEL_CACHE["path"] == model_path
        and _DST_MODEL_CACHE["meta_path"] == meta_path
    ):
        return _DST_MODEL_CACHE["model"], _DST_MODEL_CACHE["meta"]

    import tensorflow as tf

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model = tf.keras.models.load_model(model_path)
    _DST_MODEL_CACHE.update({"model": model, "meta": meta, "path": model_path, "meta_path": meta_path})
    return model, meta


def _load_dst_labels(dst_csv: str):
    if _DST_LABELS_CACHE["df"] is not None and _DST_LABELS_CACHE["path"] == dst_csv:
        return _DST_LABELS_CACHE["df"]
    from train_dst_lstm_attention import _load_dst_csv

    df = _load_dst_csv(dst_csv)
    _DST_LABELS_CACHE.update({"df": df, "path": dst_csv})
    return df


def _load_solar_wind_assets():
    candidates = [
        ("solar_wind_lstm_24h.keras", "solar_wind_lstm_24h_meta.json"),
        ("solar_wind_lstm.keras", "solar_wind_lstm_meta.json"),
    ]
    model_path = None
    meta_path = None
    for model_name, meta_name in candidates:
        mp = os.path.join(MODEL_DIR, model_name)
        mt = os.path.join(MODEL_DIR, meta_name)
        if os.path.exists(mp) and os.path.exists(mt):
            model_path = mp
            meta_path = mt
            break
    if model_path is None or meta_path is None:
        raise FileNotFoundError("Solar wind model or metadata missing")

    if (
        _SW_MODEL_CACHE["model"] is not None
        and _SW_MODEL_CACHE["path"] == model_path
        and _SW_MODEL_CACHE["meta_path"] == meta_path
    ):
        return _SW_MODEL_CACHE["model"], _SW_MODEL_CACHE["meta"]

    import tensorflow as tf

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model = tf.keras.models.load_model(model_path)
    _SW_MODEL_CACHE.update({"model": model, "meta": meta, "path": model_path, "meta_path": meta_path})
    return model, meta


def _load_hourly_omni_tail(omni_csv: str, hours: int) -> pd.DataFrame:
    minutes = max(hours * 60, 240)
    rows = minutes * 20
    df = _read_tail_csv(omni_csv, rows).sort_values("time")
    df = df.set_index("time").resample("1h").mean(numeric_only=True)
    return df


def _load_hourly_omni_tail_features(omni_csv: str, hours: int, feature_cols: list[str]) -> pd.DataFrame:
    minutes = max(hours * 60, 240)
    rows = minutes * 20
    df = _read_tail_csv(omni_csv, rows).sort_values("time")
    df = df.set_index("time").resample("1h").mean(numeric_only=True)
    # Ensure time features exist if requested.
    if "year" in feature_cols and "year" not in df.columns:
        df["year"] = df.index.year
    if "doy" in feature_cols and "doy" not in df.columns:
        df["doy"] = df.index.dayofyear
    if "hour" in feature_cols and "hour" not in df.columns:
        df["hour"] = df.index.hour
    return df


def _forecast_solar_wind_ml(steps: int = 1):
    now = time.time()
    key = ("steps", steps)
    if _SW_ML_CACHE["payload"] and now - _SW_ML_CACHE["ts"] < 120 and _SW_ML_CACHE["key"] == key:
        return _SW_ML_CACHE["payload"]

    model, meta = _load_solar_wind_assets()
    feature_cols = meta["feature_cols"]
    target_cols = meta["target_cols"]
    seq_len = int(meta["seq_len"])
    horizon = int(meta["horizon_hours"])
    mean = meta["mean"]
    std = meta["std"]
    interp_method = meta.get("interp_method", "time")

    omni_csv = SOLAR_CSV if os.path.exists(SOLAR_CSV) else SOLAR_LIVE_CSV
    if not omni_csv or not os.path.exists(omni_csv):
        raise FileNotFoundError("No solar wind source found for ML forecast.")

    df = _load_hourly_omni_tail_features(omni_csv, seq_len + horizon + 6, feature_cols)
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].interpolate(
        method="time" if interp_method == "time" else "spline",
        limit=24,
        limit_area="inside",
    )
    # Fill any remaining missing values with training means.
    for col in feature_cols:
        if col not in df.columns:
            df[col] = mean.get(col, 0.0)
        else:
            df[col] = df[col].fillna(mean.get(col, 0.0))

    if len(df) < seq_len:
        raise ValueError("Not enough history for ML forecast.")

    history = df.tail(seq_len).copy()
    current_time = history.index[-1]
    outputs = []
    for _ in range(steps):
        X = history[feature_cols].copy()
        for col in feature_cols:
            denom = std.get(col) or 1.0
            X[col] = (X[col] - mean.get(col, 0.0)) / denom
        preds = model.predict(np.expand_dims(X.to_numpy(dtype=np.float32), axis=0), verbose=0).reshape(-1)
        current_time = current_time + timedelta(hours=horizon)
        row = {"time": current_time}
        # build time features for next row if needed
        if "year" in feature_cols:
            row["year"] = current_time.year
        if "doy" in feature_cols:
            row["doy"] = int(current_time.dayofyear)
        if "hour" in feature_cols:
            row["hour"] = current_time.hour
        for col, val in zip(target_cols, preds):
            mu = mean.get(col)
            sigma = std.get(col)
            if mu is not None and sigma is not None:
                row[col] = float(val * sigma + mu)
            else:
                row[col] = float(val)
        outputs.append(row)

        next_row = {col: row.get(col, np.nan) for col in feature_cols}
        history = pd.concat([history.iloc[1:], pd.DataFrame(next_row, index=[current_time])], axis=0)

    payload = {
        "horizon_hours": horizon,
        "steps": steps,
        "target_cols": target_cols,
        "time": [r["time"].strftime("%Y-%m-%d %H:%M") for r in outputs],
        "values": [{k: v for k, v in r.items() if k not in ("time",)} for r in outputs],
    }
    _SW_ML_CACHE.update({"ts": now, "key": key, "payload": payload})
    return payload


def _parse_time_units(units: str, values: np.ndarray) -> list[pd.Timestamp]:
    if not units or "since" not in units:
        return []
    unit, origin = units.split("since", 1)
    unit = unit.strip().lower()
    origin = origin.strip()
    try:
        base = pd.to_datetime(origin)
    except Exception:
        return []
    # normalize unit to pandas
    if unit.startswith("hour"):
        delta = pd.to_timedelta(values, unit="h")
    elif unit.startswith("day"):
        delta = pd.to_timedelta(values, unit="D")
    elif unit.startswith("min"):
        delta = pd.to_timedelta(values, unit="m")
    else:
        return []
    return list(base + delta)


def _add_dst_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    if "flow_speed" in df.columns and "proton_density" in df.columns:
        df["v_np"] = df["flow_speed"] * df["proton_density"]
        df["v2_np"] = (df["flow_speed"] ** 2) * df["proton_density"]
    if "bz_gsm" in df.columns:
        df["bz_south"] = np.minimum(df["bz_gsm"], 0.0)
        df["bz_abs"] = np.abs(df["bz_gsm"])
    if "flow_speed" in df.columns and "bz_gsm" in df.columns:
        df["vbz_south"] = df["flow_speed"] * np.minimum(df["bz_gsm"], 0.0)
    return df


def _parse_cycle_rows(data: list[dict], kind: str) -> list[dict]:
    rows = []
    for row in data or []:
        tag = row.get("time-tag") or row.get("time_tag") or row.get("time")
        if not tag:
            continue
        ts = pd.to_datetime(tag, errors="coerce")
        if pd.isna(ts):
            continue
        item = {"time": ts.strftime("%Y-%m")}
        if kind == "observed":
            item["ssn"] = _safe_float(row.get("smoothed_ssn") or row.get("smoothed_swpc_ssn") or row.get("ssn"))
            item["f107"] = _safe_float(row.get("smoothed_f10.7") or row.get("f10.7") or row.get("f107"))
        else:
            item["ssn"] = _safe_float(row.get("predicted_ssn") or row.get("ssn"))
            item["f107"] = _safe_float(row.get("predicted_f10.7") or row.get("f10.7") or row.get("f107"))
            item["ssn_high"] = _safe_float(row.get("high25_ssn") or row.get("high_ssn") or row.get("high75_ssn"))
            item["ssn_low"] = _safe_float(row.get("low25_ssn") or row.get("low_ssn") or row.get("low75_ssn"))
        rows.append(item)
    return rows


def _fetch_solar_cycle():
    now = time.time()
    if _SOLAR_CYCLE_CACHE["payload"] and now - _SOLAR_CYCLE_CACHE["ts"] < 6 * 3600:
        return _SOLAR_CYCLE_CACHE["payload"]
    observed = _parse_cycle_rows(_fetch_url(SOLAR_CYCLE_OBS_URL), "observed")
    predicted = _parse_cycle_rows(_fetch_url(SOLAR_CYCLE_PRED_URL), "predicted")

    current_obs = next((row for row in reversed(observed) if row.get("f107") is not None or row.get("ssn") is not None), None)
    f107_vals = [row.get("f107") for row in observed + predicted if isinstance(row.get("f107"), (int, float)) and math.isfinite(row.get("f107"))]
    ssn_vals = [row.get("ssn") for row in observed + predicted if isinstance(row.get("ssn"), (int, float)) and math.isfinite(row.get("ssn"))]

    if f107_vals:
        min_val, max_val = min(f107_vals), max(f107_vals)
        current_val = current_obs.get("f107") if current_obs else None
    else:
        min_val, max_val = (min(ssn_vals), max(ssn_vals)) if ssn_vals else (0.0, 1.0)
        current_val = current_obs.get("ssn") if current_obs else None

    if current_val is None or not math.isfinite(current_val) or max_val == min_val:
        phase = None
    else:
        phase = float((current_val - min_val) / (max_val - min_val))

    payload = {
        "observed": observed[-36:] if len(observed) > 36 else observed,
        "predicted": predicted[:36] if predicted else [],
        "current": current_obs,
        "phase": phase,
    }
    _SOLAR_CYCLE_CACHE["payload"] = payload
    _SOLAR_CYCLE_CACHE["ts"] = now
    return payload


def _apply_solar_cycle_features(df: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    needed = {"solar_f107_smoothed", "solar_ssn_smoothed", "solar_cycle_phase"}
    if not any(col in feature_cols for col in needed):
        return df
    try:
        cycle = _fetch_solar_cycle()
    except Exception:
        return df

    rows = cycle.get("observed", []) + cycle.get("predicted", [])
    if not rows:
        return df
    cycle_df = pd.DataFrame(rows)
    cycle_df = cycle_df.dropna(subset=["time"])
    cycle_df = cycle_df.drop_duplicates(subset=["time"], keep="last")
    if cycle_df.empty:
        return df

    f107_vals = cycle_df["f107"].dropna().to_numpy()
    ssn_vals = cycle_df["ssn"].dropna().to_numpy()
    if len(f107_vals):
        min_val, max_val = float(f107_vals.min()), float(f107_vals.max())
        if max_val != min_val:
            cycle_df["solar_cycle_phase"] = (cycle_df["f107"] - min_val) / (max_val - min_val)
        else:
            cycle_df["solar_cycle_phase"] = 0.5
    elif len(ssn_vals):
        min_val, max_val = float(ssn_vals.min()), float(ssn_vals.max())
        if max_val != min_val:
            cycle_df["solar_cycle_phase"] = (cycle_df["ssn"] - min_val) / (max_val - min_val)
        else:
            cycle_df["solar_cycle_phase"] = 0.5
    else:
        cycle_df["solar_cycle_phase"] = 0.5

    cycle_df = cycle_df.rename(columns={"f107": "solar_f107_smoothed", "ssn": "solar_ssn_smoothed"})
    df = df.copy()
    df["month_key"] = df.index.to_period("M").astype(str)
    df = df.join(cycle_df.set_index("time"), on="month_key")
    df = df.drop(columns=["month_key"])
    return df


def _select_var(vars_dict: dict, candidates: list[str]):
    for name in candidates:
        if name in vars_dict:
            return name
    for key in vars_dict:
        lower = key.lower()
        for name in candidates:
            if name in lower:
                return key
    return None


def _fetch_enlil_forecast():
    now = time.time()
    if _ENLIL_CACHE["payload"] and now - _ENLIL_CACHE["ts"] < 3600:
        return _ENLIL_CACHE["payload"]

    def _get_text(url: str) -> str:
        req = Request(url, headers={"User-Agent": "space-weather-sentinel/1.0"})
        with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="ignore")

    listing = _get_text(ENLIL_BASE)
    dirs = sorted(set(re.findall(r"wsa_enlil\.(\d{8})/", listing)))
    if not dirs:
        raise ValueError("No ENLIL run directories found.")
    latest = dirs[-1]
    run_url = f"{ENLIL_BASE}wsa_enlil.{latest}/"
    run_listing = _get_text(run_url)

    # Prefer L1 evolution files.
    file_match = None
    file_kind = "evo"
    for pattern in (r"evo\.l1\.nc(?:\.gz)?", r"evo\.earth\.nc(?:\.gz)?"):
        file_match = re.search(pattern, run_listing)
        if file_match:
            break
    if not file_match:
        # Fallback: any evo*.nc
        file_match = re.search(r"evo[^\"\\s>]*\.nc(?:\.gz)?", run_listing)
    if not file_match:
        # Newer runs sometimes only ship suball files (Earth_* variables).
        file_match = re.search(r"wsa_enlil\.[^\"\\s>]*suball\.nc(?:\.gz)?", run_listing)
        if file_match:
            file_kind = "suball"
    if not file_match:
        raise ValueError("No ENLIL output file found in latest run.")

    filename = file_match.group(0)
    file_url = f"{run_url}{filename}"

    # Download to temp file
    req = Request(file_url, headers={"User-Agent": "space-weather-sentinel/1.0"})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        raw = resp.read()

    if filename.endswith(".gz"):
        raw = gzip.decompress(raw)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".nc") as tmp:
        tmp.write(raw)
        tmp_path = tmp.name

    try:
        from scipy.io import netcdf_file

        with netcdf_file(tmp_path, "r", mmap=False) as nc:
            vars_dict = nc.variables
            speed = density = bz = None
            if file_kind == "suball":
                # Use Earth_* variables from suball files.
                ref = getattr(nc, "REFDATE_CAL", None) or getattr(nc, "OBSDATE_CAL", None)
                if isinstance(ref, bytes):
                    ref = ref.decode("utf-8", errors="ignore")
                if not ref:
                    pdy = getattr(nc, "PDY", b"")
                    cyc = getattr(nc, "cyc", b"")
                    if isinstance(pdy, bytes):
                        pdy = pdy.decode("utf-8", errors="ignore")
                    if isinstance(cyc, bytes):
                        cyc = cyc.decode("utf-8", errors="ignore")
                    ref = f"{pdy}{cyc or '00'}"
                ref_ts = pd.to_datetime(ref, errors="coerce")
                if pd.isna(ref_ts):
                    raise ValueError("Unable to parse ENLIL suball reference time.")
                time_vals = np.array(vars_dict.get("Earth_TIME")[:]).astype(float)
                times = list(ref_ts + pd.to_timedelta(time_vals, unit="s"))

                def _read(var_name):
                    if var_name not in vars_dict:
                        return None
                    return np.array(vars_dict[var_name][:]).astype(float)

                v1 = _read("Earth_V1")
                v2 = _read("Earth_V2")
                v3 = _read("Earth_V3")
                if v1 is not None:
                    if v2 is None:
                        v2 = np.zeros_like(v1)
                    if v3 is None:
                        v3 = np.zeros_like(v1)
                    speed = np.sqrt(v1 ** 2 + v2 ** 2 + v3 ** 2)
                    med = np.nanmedian(speed)
                    if np.isfinite(med) and med > 2000:
                        speed = speed / 1000.0
                rho = _read("Earth_Density")
                if rho is not None:
                    med = np.nanmedian(rho)
                    if np.isfinite(med) and med < 1e-6:
                        rho = rho / PROTON_MASS_KG / 1e6
                    density = rho
                b3 = _read("Earth_B3")
                if b3 is not None:
                    med = np.nanmedian(np.abs(b3))
                    if np.isfinite(med) and med < 1e-3:
                        b3 = b3 * 1e9
                    bz = b3
                speed = speed.tolist() if speed is not None else None
                density = density.tolist() if density is not None else None
                bz = bz.tolist() if bz is not None else None
            else:
                time_var_name = _select_var(vars_dict, ["time"])
                if not time_var_name:
                    raise ValueError("ENLIL file missing time variable.")
                time_var = vars_dict[time_var_name]
                time_vals = np.array(time_var[:]).astype(float)
                times = _parse_time_units(getattr(time_var, "units", ""), time_vals)
                if not times:
                    raise ValueError("Unable to parse ENLIL time units.")

                speed_name = _select_var(vars_dict, ["vp", "vr", "speed", "flow_speed", "v"]) or ""
                density_name = _select_var(vars_dict, ["density", "rho", "n", "number_density"]) or ""
                bz_name = _select_var(vars_dict, ["bz", "b_z", "bz_gsm", "bz_gse"]) or ""

                def _series(var_name):
                    if not var_name or var_name not in vars_dict:
                        return None
                    data = np.array(vars_dict[var_name][:]).astype(float)
                    return data.tolist()

                speed = _series(speed_name)
                density = _series(density_name)
                bz = _series(bz_name)

        os.unlink(tmp_path)
    except Exception as exc:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise exc

    # Filter to next 4 days
    now_ts = pd.Timestamp.utcnow().tz_localize(None)
    end_ts = now_ts + pd.Timedelta(hours=96)
    filtered = [(t, i) for i, t in enumerate(times) if now_ts <= t <= end_ts]
    if not filtered:
        filtered = [(t, i) for i, t in enumerate(times)]
    idx = [i for _, i in filtered]
    out_times = [times[i] for i in idx]

    def _slice(series):
        if series is None:
            return None
        return [series[i] if i < len(series) else None for i in idx]

    payload = {
        "source": "WSA-Enlil (NOAA/NCEP)",
        "run_date": latest,
        "time": [t.strftime("%Y-%m-%d %H:%M") for t in out_times],
        "speed": _slice(speed),
        "density": _slice(density),
        "bz": _slice(bz),
    }
    _ENLIL_CACHE.update({"ts": now, "payload": payload})
    return payload


def _fetch_dst_series(hours: int, interp: bool):
    now = time.time()
    key = (hours, interp)
    if _DST_SERIES_CACHE["payload"] and now - _DST_SERIES_CACHE["ts"] < 60 and _DST_SERIES_CACHE["key"] == key:
        return _DST_SERIES_CACHE["payload"]

    import tensorflow as tf

    model, meta = _load_dst_assets()
    seq_len = int(meta.get("seq_len", 48))
    horizon = int(meta.get("horizon_hours", 1))
    mean = meta.get("mean", {})
    std = meta.get("std", {})
    feature_cols = meta.get("feature_cols")
    if not feature_cols:
        from train_dst_lstm_attention import FEATURE_COLS as DST_FEATURES

        feature_cols = DST_FEATURES

    # Load recent hourly solar wind and join Dst labels.
    extra_hours = hours + seq_len + horizon + 6
    omni_csv = SOLAR_CSV if os.path.exists(SOLAR_CSV) else SOLAR_LIVE_CSV
    if not omni_csv:
        raise FileNotFoundError("No solar wind source found.")

    df = _load_hourly_omni_tail(omni_csv, extra_hours)
    dst_csv = os.path.join(ROOT, "data", "indices", "kyoto", "dst_hourly.csv")
    if os.path.exists(dst_csv):
        dst_df = _load_dst_labels(dst_csv)
        df = df.join(dst_df[["dst_kyoto"]], how="left")
    else:
        df["dst_kyoto"] = np.nan

    if interp:
        # Fast time-based interpolation (much faster than spline).
        numeric_cols = df.select_dtypes(include=["number"]).columns
        df[numeric_cols] = df[numeric_cols].interpolate(
            method="time",
            limit=24,
            limit_area="inside",
        )

    df = _add_dst_derived_features(df)

    df = _apply_solar_cycle_features(df, feature_cols)

    # Ensure required feature columns exist and impute missing values using training means.
    for col in feature_cols:
        if col not in df.columns:
            df[col] = mean.get(col, 0.0)
        else:
            df[col] = df[col].fillna(mean.get(col, 0.0))

    # Drop rows still missing required features (should be rare after imputation)
    df = df.dropna(subset=feature_cols)
    if df.empty or len(df) < (seq_len + horizon + 1):
        raise ValueError("Not enough data to build prediction series")

    end_time = df.index.max()
    start_time = end_time - pd.Timedelta(hours=hours)
    df = df[df.index >= start_time - pd.Timedelta(hours=seq_len + horizon + 1)]

    # Standardize features with training statistics
    feat = df[feature_cols].copy()
    for col in feature_cols:
        denom = std.get(col) or 1.0
        feat[col] = (feat[col] - mean.get(col, 0.0)) / denom

    X = feat.to_numpy(dtype=np.float32)
    target_offset = seq_len - 1 + horizon
    end_index = len(X) - horizon
    if len(X) <= target_offset or end_index < (seq_len - 1):
        raise ValueError("Not enough rows after preprocessing for prediction series.")

    dataset = tf.keras.utils.timeseries_dataset_from_array(
        data=X,
        targets=None,
        sequence_length=seq_len,
        sequence_stride=1,
        sampling_rate=1,
        start_index=0,
        end_index=end_index,
        batch_size=256,
        shuffle=False,
    )
    ds = model.predict(dataset, verbose=0).reshape(-1)

    times = df.index[target_offset:]
    times = times[: len(ds)]
    mask = (times >= start_time) & (times <= end_time)
    times = times[mask]
    preds = ds[mask]
    real = df.loc[times, "dst_kyoto"].to_numpy()

    payload = {
        "time": [t.strftime("%Y-%m-%d %H:%M") for t in times],
        "dst_pred": [float(v) if np.isfinite(v) else None for v in preds],
        "dst_true": [float(v) if np.isfinite(v) else None for v in real],
        "start": start_time.strftime("%Y-%m-%d %H:%M"),
        "end": end_time.strftime("%Y-%m-%d %H:%M"),
    }
    _DST_SERIES_CACHE.update({"ts": now, "key": key, "payload": payload})
    return payload


def _fetch_dst_forecast(hours: int):
    now = time.time()
    hours = max(6, min(int(hours), 96))
    key = ("hours", hours)
    if _DST_FORECAST_CACHE["payload"] and now - _DST_FORECAST_CACHE["ts"] < 300 and _DST_FORECAST_CACHE["key"] == key:
        return _DST_FORECAST_CACHE["payload"]

    import tensorflow as tf

    model, meta = _load_dst_assets()
    seq_len = int(meta.get("seq_len", 48))
    horizon = int(meta.get("horizon_hours", 1))
    mean = meta.get("mean", {})
    std = meta.get("std", {})
    feature_cols = meta.get("feature_cols")
    if not feature_cols:
        from train_dst_lstm_attention import FEATURE_COLS as DST_FEATURES

        feature_cols = DST_FEATURES

    omni_csv = SOLAR_CSV if os.path.exists(SOLAR_CSV) else SOLAR_LIVE_CSV
    if not omni_csv:
        raise FileNotFoundError("No solar wind source found.")

    hist = _load_hourly_omni_tail(omni_csv, seq_len + 12)
    if hist.empty:
        raise ValueError("No recent solar wind data for Dst forecast")

    # Ensure time features exist for forecast.
    if "year" in feature_cols and "year" not in hist.columns:
        hist["year"] = hist.index.year
    if "doy" in feature_cols and "doy" not in hist.columns:
        hist["doy"] = hist.index.dayofyear
    if "hour" in feature_cols and "hour" not in hist.columns:
        hist["hour"] = hist.index.hour
    if "minute" in feature_cols and "minute" not in hist.columns:
        hist["minute"] = hist.index.minute

    # Fast interpolation for gaps.
    numeric_cols = hist.select_dtypes(include=["number"]).columns
    hist[numeric_cols] = hist[numeric_cols].interpolate(method="time", limit=24, limit_area="inside")

    hist = _add_dst_derived_features(hist)
    hist = _apply_solar_cycle_features(hist, feature_cols)

    for col in feature_cols:
        if col not in hist.columns:
            hist[col] = mean.get(col, 0.0)
        hist[col] = hist[col].fillna(mean.get(col, 0.0))

    hist = hist.dropna(subset=feature_cols)
    if len(hist) < seq_len:
        raise ValueError("Not enough data to build forecast window")

    last_time = hist.index.max()
    future_times = pd.date_range(last_time + pd.Timedelta(hours=1), periods=hours, freq="1h")
    future = pd.DataFrame(index=future_times)

    # Base time features.
    if "year" in feature_cols:
        future["year"] = future.index.year
    if "doy" in feature_cols:
        future["doy"] = future.index.dayofyear
    if "hour" in feature_cols:
        future["hour"] = future.index.hour
    if "minute" in feature_cols:
        future["minute"] = future.index.minute

    last_row = hist.iloc[-1]
    for col in feature_cols:
        if col not in future.columns:
            future[col] = last_row.get(col, mean.get(col, 0.0))

    source = "Persistence"
    try:
        enlil = _fetch_enlil_forecast()
        times = pd.to_datetime(enlil.get("time", []), errors="coerce")
        enlil_df = pd.DataFrame(
            {
                "time": times,
                "speed": enlil.get("speed"),
                "density": enlil.get("density"),
                "bz": enlil.get("bz"),
            }
        ).dropna(subset=["time"])
        if not enlil_df.empty:
            enlil_df = enlil_df.set_index("time").sort_index()
            enlil_df = enlil_df.resample("1h").mean().ffill()
            enlil_df = enlil_df.reindex(future_times, method="nearest", tolerance="2h")
            if "flow_speed" in feature_cols and "speed" in enlil_df:
                future["flow_speed"] = enlil_df["speed"].to_numpy()
            if "proton_density" in feature_cols and "density" in enlil_df:
                future["proton_density"] = enlil_df["density"].to_numpy()
            if "bz_gsm" in feature_cols and "bz" in enlil_df:
                future["bz_gsm"] = enlil_df["bz"].to_numpy()
            if "bz_gse" in feature_cols and "bz_gsm" in future:
                future["bz_gse"] = future["bz_gsm"]
            if "b_mag" in feature_cols and "bz_gsm" in future:
                future["b_mag"] = np.abs(future["bz_gsm"])
            if "bx_gse" in feature_cols:
                future["bx_gse"] = 0.0
            if "by_gse" in feature_cols:
                future["by_gse"] = 0.0
            if "by_gsm" in feature_cols:
                future["by_gsm"] = 0.0
            if "vx_gse" in feature_cols and "flow_speed" in future:
                future["vx_gse"] = -future["flow_speed"]
            if "vy_gse" in feature_cols:
                future["vy_gse"] = 0.0
            if "vz_gse" in feature_cols:
                future["vz_gse"] = 0.0
            if "flow_pressure" in feature_cols and "flow_speed" in future and "proton_density" in future:
                future["flow_pressure"] = 1.6726e-6 * future["proton_density"] * (future["flow_speed"] ** 2)
            source = "WSA-Enlil (NOAA/NCEP)"
    except Exception:
        pass

    combo = pd.concat([hist, future])
    combo = _add_dst_derived_features(combo)
    combo = _apply_solar_cycle_features(combo, feature_cols)

    for col in feature_cols:
        if col not in combo.columns:
            combo[col] = mean.get(col, 0.0)
        combo[col] = combo[col].fillna(mean.get(col, 0.0))

    feat = combo[feature_cols].copy()
    for col in feature_cols:
        denom = std.get(col) or 1.0
        feat[col] = (feat[col] - mean.get(col, 0.0)) / denom

    X = feat.to_numpy(dtype=np.float32)
    end_index = len(X) - horizon
    dataset = tf.keras.utils.timeseries_dataset_from_array(
        data=X,
        targets=None,
        sequence_length=seq_len,
        sequence_stride=1,
        sampling_rate=1,
        start_index=0,
        end_index=end_index,
        batch_size=256,
        shuffle=False,
    )
    preds = model.predict(dataset, verbose=0).reshape(-1)
    target_offset = seq_len - 1 + horizon
    times = combo.index[target_offset:]
    times = times[: len(preds)]
    mask = times > last_time
    out_times = times[mask]
    out_preds = preds[mask]

    payload = {
        "time": [t.strftime("%Y-%m-%d %H:%M") for t in out_times],
        "dst_pred": [float(v) if np.isfinite(v) else None for v in out_preds],
        "start": future_times[0].strftime("%Y-%m-%d %H:%M") if len(future_times) else None,
        "end": future_times[-1].strftime("%Y-%m-%d %H:%M") if len(future_times) else None,
        "last_observed": last_time.strftime("%Y-%m-%d %H:%M"),
        "source": source,
        "hours": hours,
    }
    _DST_FORECAST_CACHE.update({"ts": now, "key": key, "payload": payload})
    return payload


def _fetch_dst_outlook():
    now = time.time()
    if _DST_OUTLOOK_CACHE["payload"] and now - _DST_OUTLOOK_CACHE["ts"] < 3600:
        return _DST_OUTLOOK_CACHE["payload"]

    outlook_path = os.environ.get("DST_OUTLOOK_PATH")
    if outlook_path:
        path = outlook_path if os.path.isabs(outlook_path) else os.path.join(ROOT, outlook_path)
    else:
        path = os.path.join(DATA_DIR, "dst_outlook_30d.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        _DST_OUTLOOK_CACHE.update({"ts": now, "payload": payload})
        return payload

    # Fallback to CSV
    csv_path = os.path.join(DATA_DIR, "dst_outlook_30d.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError("Dst 30-day outlook not found.")

    df = pd.read_csv(csv_path)
    rows = df.to_dict(orient="records")
    payload = {"summary": {}, "rows": rows}
    _DST_OUTLOOK_CACHE.update({"ts": now, "payload": payload})
    return payload


def _load_sat_impact_means(feature_cols: list[str], meta: dict) -> dict:
    cached = _SAT_IMPACT_MEANS_CACHE.get("means")
    cached_cols = _SAT_IMPACT_MEANS_CACHE.get("cols")
    if cached is not None and cached_cols == feature_cols:
        return cached

    # Prefer stored means in metadata if present.
    meta_means = meta.get("feature_means")
    if isinstance(meta_means, dict):
        _SAT_IMPACT_MEANS_CACHE.update({"means": meta_means, "cols": feature_cols, "ts": time.time()})
        return meta_means

    csv_path = os.path.join(DATA_DIR, "sat_impact_dataset.csv")
    if not os.path.exists(csv_path):
        return {}

    sums = {col: 0.0 for col in feature_cols}
    counts = {col: 0 for col in feature_cols}
    try:
        for chunk in pd.read_csv(csv_path, usecols=feature_cols, chunksize=200000):
            for col in feature_cols:
                series = pd.to_numeric(chunk[col], errors="coerce")
                mask = series.notna()
                if mask.any():
                    sums[col] += float(series[mask].sum())
                    counts[col] += int(mask.sum())
    except Exception:
        return {}

    means = {col: (sums[col] / counts[col]) if counts[col] else 0.0 for col in feature_cols}
    _SAT_IMPACT_MEANS_CACHE.update({"means": means, "cols": feature_cols, "ts": time.time()})
    return means


def _stat_path(path: str) -> dict:
    if not path:
        return {"exists": False, "size_mb": None, "mtime": None}
    if os.path.exists(path):
        stat = os.stat(path)
        return {
            "exists": True,
            "size_mb": round(stat.st_size / 1_048_576, 2),
            "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        }
    return {"exists": False, "size_mb": None, "mtime": None}


def _fetch_health_full():
    now = time.time()
    if _HEALTH_FULL_CACHE["payload"] and now - _HEALTH_FULL_CACHE["ts"] < 30:
        return _HEALTH_FULL_CACHE["payload"]

    try:
        quality = compute_quality(SOLAR_LIVE_CSV if os.path.exists(SOLAR_LIVE_CSV) else SOLAR_CSV)
    except Exception as exc:
        quality = {"ok": False, "error": str(exc)}

    error_rate = 0.0
    if _REQUEST_STATS["count"] > 0:
        error_rate = _REQUEST_STATS["errors"] / _REQUEST_STATS["count"]

    service = {
        "ok": quality.get("ok", False),
        "uptime_sec": int(time.time() - START_TIME),
        "requests": _REQUEST_STATS,
        "error_rate": round(error_rate, 4),
        "quality": quality,
    }

    model_checks = [
        ("storm_model.joblib", "Storm risk (LGBM)", True),
        ("symh_model.joblib", "SYM/H forecast", True),
        ("flare_model.joblib", "Flare model", False),
        ("drag_model.joblib", "Satellite drag", False),
        ("dst_lstm_attention.keras", "Dst LSTM (attention)", True),
        ("dst_lstm_attention_meta.json", "Dst LSTM meta", True),
        ("dst_lstm_realtime.keras", "Dst realtime LSTM", False),
        ("dst_lstm_realtime_meta.json", "Dst realtime meta", False),
        ("solar_wind_lstm_24h.keras", "Solar wind 24h LSTM", True),
        ("solar_wind_lstm_24h_meta.json", "Solar wind 24h meta", True),
        ("solar_wind_lstm.keras", "Solar wind 6h LSTM", False),
        ("solar_wind_lstm_meta.json", "Solar wind 6h meta", False),
        ("sat_impact_model.txt", "Satellite impact LGBM", True),
        ("sat_impact_model_meta.json", "Satellite impact meta", True),
        ("cme_impact_model.txt", "CME impact LGBM", False),
        ("cme_transit_model.txt", "CME transit LGBM", False),
        ("cme_impact_model_meta.json", "CME impact meta", False),
    ]
    models = []
    all_required_ok = True
    for filename, label, required in model_checks:
        path = os.path.join(MODEL_DIR, filename)
        stat = _stat_path(path)
        status = "ok" if stat["exists"] else "missing"
        if required and not stat["exists"]:
            all_required_ok = False
        models.append(
            {
                "name": label,
                "file": filename,
                "path": path,
                "required": required,
                "status": status,
                **stat,
            }
        )

    data_checks = [
        (SOLAR_CSV, "OMNI (processed)", True),
        (SOLAR_LIVE_CSV, "OMNI (live)", False),
        (os.path.join(ROOT, "data", "indices", "kyoto", "dst_hourly.csv"), "Kyoto Dst hourly", True),
        (os.path.join(DATA_DIR, "dst_outlook_30d.json"), "Dst 30d outlook", False),
        (os.path.join(DATA_DIR, "sat_impact_dataset.csv"), "Satellite impact dataset", False),
        (os.path.join(DATA_DIR, "cme_impact_dataset.csv"), "CME impact dataset", False),
    ]
    data_files = []
    for path, label, required in data_checks:
        stat = _stat_path(path)
        status = "ok" if stat["exists"] else "missing"
        data_files.append(
            {
                "name": label,
                "path": path,
                "required": required,
                "status": status,
                **stat,
            }
        )

    payload = {
        "ok": service.get("ok", False) and all_required_ok,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "model_dir": MODEL_DIR,
        "data_dir": DATA_DIR,
        "models": models,
        "data_files": data_files,
    }
    _HEALTH_FULL_CACHE.update({"ts": now, "payload": payload})
    return payload


def _fetch_url(url: str):
    req = Request(url, headers={"User-Agent": "space-weather-sentinel/1.0"})
    with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_aurora():
    now = time.time()
    if _AURORA_CACHE["payload"] and now - _AURORA_CACHE["ts"] < 60:
        return _AURORA_CACHE["payload"]

    def _try_urls(urls):
        last_err = None
        for url in urls:
            try:
                data = _fetch_url(url)
                return {"url": url, "data": data}
            except Exception as exc:
                last_err = exc
        raise last_err or RuntimeError("Aurora fetch failed")

    now_payload = _try_urls(AURORA_NOW_URLS)
    forecast_payload = None
    try:
        forecast_payload = _try_urls(AURORA_FORECAST_URLS)
    except Exception:
        forecast_payload = None

    payload = {
        "now": now_payload,
        "forecast": forecast_payload,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _AURORA_CACHE["payload"] = payload
    _AURORA_CACHE["ts"] = now
    return payload


def _extract_headline(message: str) -> str:
    for line in message.splitlines():
        line = line.strip()
        if not line:
            continue
        if "ALERT:" in line or "WARNING:" in line or "WATCH:" in line:
            return line
    for line in message.splitlines():
        line = line.strip()
        if line:
            return line
    return "Space Weather Message"


def _classify_headline(headline: str) -> str:
    upper = headline.upper()
    if "WARNING" in upper:
        return "warning"
    if "WATCH" in upper:
        return "watch"
    if "ALERT" in upper:
        return "alert"
    return "info"


def _fetch_alerts():
    now = time.time()
    if _AWW_CACHE["payload"] and now - _AWW_CACHE["ts"] < 60:
        return _AWW_CACHE["payload"]
    data = _fetch_url(AWW_URL)
    items = []
    for row in data:
        message = row.get("message", "")
        headline = _extract_headline(message)
        items.append({
            "product_id": row.get("product_id"),
            "issue_datetime": row.get("issue_datetime"),
            "headline": headline,
            "level": _classify_headline(headline),
            "message": message,
        })
    items.sort(key=lambda x: x.get("issue_datetime") or "", reverse=True)
    payload = {"items": items[:50]}
    _AWW_CACHE["payload"] = payload
    _AWW_CACHE["ts"] = now
    return payload


def _safe_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_satellite_presets():
    now = time.time()
    if _SAT_PRESETS_CACHE["payload"] and now - _SAT_PRESETS_CACHE["ts"] < 300:
        return _SAT_PRESETS_CACHE["payload"]
    presets = []
    if os.path.exists(SATELLITE_CONFIG_PATH):
        try:
            with open(SATELLITE_CONFIG_PATH, "r", encoding="utf-8") as f:
                payload = json.load(f)
            presets = payload.get("presets") or []
        except Exception:
            presets = []
    if not presets:
        presets = [
            {"id": "cubesat_3u", "name": "CubeSat 3U (demo)", "mass_kg": 4.0, "area_m2": 0.03, "cd": 2.2, "alt_km": 500},
            {"id": "cubesat_6u", "name": "CubeSat 6U (demo)", "mass_kg": 12.0, "area_m2": 0.05, "cd": 2.2, "alt_km": 500},
            {"id": "smallsat_100kg", "name": "SmallSat 100 kg (demo)", "mass_kg": 100.0, "area_m2": 1.0, "cd": 2.2, "alt_km": 550},
            {"id": "leo_platform_500kg", "name": "LEO Platform 500 kg (demo)", "mass_kg": 500.0, "area_m2": 4.0, "cd": 2.2, "alt_km": 700},
            {"id": "leo_platform_1000kg", "name": "LEO Platform 1000 kg (demo)", "mass_kg": 1000.0, "area_m2": 8.0, "cd": 2.2, "alt_km": 400},
        ]
    _SAT_PRESETS_CACHE["payload"] = presets
    _SAT_PRESETS_CACHE["ts"] = now
    return presets


def _resolve_satellite_config(qs: dict):
    sat_id = (qs.get("sat_id", [None])[0] or qs.get("sat", [None])[0])
    preset = None
    if sat_id and sat_id != "custom":
        for item in _load_satellite_presets():
            if item.get("id") == sat_id:
                preset = dict(item)
                break

    cfg = preset or {}
    for key, field in (("mass_kg", "mass_kg"), ("area_m2", "area_m2"), ("cd", "cd"), ("alt_km", "alt_km")):
        val = _safe_float(qs.get(key, [None])[0])
        if val is not None:
            cfg[field] = val

    if not cfg:
        return None, None

    missing = [k for k in ("mass_kg", "area_m2", "cd", "alt_km") if not _safe_float(cfg.get(k))]
    if missing:
        return None, preset

    cfg["id"] = cfg.get("id", sat_id or "custom")
    cfg["name"] = cfg.get("name", "Custom")
    return cfg, preset


def _density_from_alt_km(alt_km: float) -> float:
    table = _DRAG_DENSITY_TABLE
    if alt_km <= table[0][0]:
        return table[0][1]
    for i in range(1, len(table)):
        a0, d0 = table[i - 1]
        a1, d1 = table[i]
        if alt_km <= a1:
            t = (alt_km - a0) / (a1 - a0)
            log_d = math.log(d0) + t * (math.log(d1) - math.log(d0))
            return float(math.exp(log_d))
    return table[-1][1]


def _density_scale_from_dtc(dtc: float | None) -> float:
    if dtc is None or not math.isfinite(dtc):
        return 1.0
    scale = math.exp(dtc / 120.0)
    return float(min(10.0, max(0.2, scale)))


def _orbital_speed_ms(alt_km: float) -> float:
    mu = 3.986004418e14
    r = 6371e3 + alt_km * 1000.0
    return math.sqrt(mu / r)


def _estimate_drag(cfg: dict | None, dtc: float | None):
    if not cfg:
        return None
    mass = _safe_float(cfg.get("mass_kg"))
    area = _safe_float(cfg.get("area_m2"))
    cd = _safe_float(cfg.get("cd"))
    alt = _safe_float(cfg.get("alt_km"))
    if not mass or not area or not cd or not alt:
        return None
    rho = _density_from_alt_km(alt) * _density_scale_from_dtc(dtc)
    v = _orbital_speed_ms(alt)
    accel = 0.5 * cd * (area / mass) * rho * v * v
    ballistic = mass / (cd * area)
    return {
        "accel_mps2": accel,
        "density_kgm3": rho,
        "orbital_speed_ms": v,
        "ballistic_coeff": ballistic,
    }


def _get_client_ip(handler) -> str:
    forwarded = handler.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return handler.client_address[0]


def _rate_limit_ok(ip: str) -> bool:
    if CONFIG.rate_limit_rps <= 0:
        return True
    now = time.time()
    state = _RATE_LIMIT_STATE.get(ip)
    if state is None:
        _RATE_LIMIT_STATE[ip] = {"tokens": float(CONFIG.rate_limit_burst - 1), "ts": now}
        return True
    tokens = state["tokens"] + (now - state["ts"]) * CONFIG.rate_limit_rps
    tokens = min(tokens, float(CONFIG.rate_limit_burst))
    if tokens < 1.0:
        state["tokens"] = tokens
        state["ts"] = now
        return False
    state["tokens"] = tokens - 1.0
    state["ts"] = now
    return True


def _check_api_key(handler) -> bool:
    if not CONFIG.require_api_key:
        return True
    expected = CONFIG.api_key
    if not expected:
        return False
    key = handler.headers.get("X-API-Key")
    auth = handler.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        key = auth.split(" ", 1)[1].strip()
    return key == expected


def _cors_origin(handler) -> str:
    if "*" in CONFIG.allowed_origins:
        return "*"
    origin = handler.headers.get("Origin")
    if origin and origin in CONFIG.allowed_origins:
        return origin
    return "null"


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        super().end_headers()

    def log_message(self, format, *args):
        logger.info("%s - %s", self.address_string(), format % args)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()

    def do_GET(self):
        self._request_start = time.time()
        _REQUEST_STATS["count"] += 1
        _REQUEST_STATS["last_request_ts"] = datetime.now(timezone.utc).isoformat()
        client_ip = _get_client_ip(self)
        if not _rate_limit_ok(client_ip):
            self._send_json({"error": "rate_limited"}, code=429)
            return
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api") and not _check_api_key(self):
            self._send_json({"error": "unauthorized"}, code=401)
            return
        if parsed.path == "/api/proxy-image":
            qs = parse_qs(parsed.query)
            url = qs.get("url", [None])[0]
            if not url:
                self.send_error(400, "Missing url")
                return
            try:
                req = Request(url, headers={"User-Agent": "space-weather-sentinel/1.0"})
                with urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                    content = resp.read()
                    ctype = resp.headers.get("Content-Type", "image/jpeg")
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as exc:
                self.send_error(502, f"Image proxy failed: {exc}")
            return
        if parsed.path == "/api/health":
            try:
                quality = compute_quality(SOLAR_LIVE_CSV if os.path.exists(SOLAR_LIVE_CSV) else SOLAR_CSV)
                error_rate = 0.0
                if _REQUEST_STATS["count"] > 0:
                    error_rate = _REQUEST_STATS["errors"] / _REQUEST_STATS["count"]
                payload = {
                    "ok": quality.get("ok", False),
                    "uptime_sec": int(time.time() - START_TIME),
                    "requests": _REQUEST_STATS,
                    "error_rate": round(error_rate, 4),
                    "quality": quality,
                }
                self._send_json(payload)
            except Exception as exc:
                _REQUEST_STATS["last_error"] = str(exc)
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/health_full":
            try:
                payload = _fetch_health_full()
                self._send_json(payload)
            except Exception as exc:
                _REQUEST_STATS["last_error"] = str(exc)
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/quality":
            try:
                payload = compute_quality(SOLAR_LIVE_CSV if os.path.exists(SOLAR_LIVE_CSV) else SOLAR_CSV)
                self._send_json(payload)
            except Exception as exc:
                _REQUEST_STATS["last_error"] = str(exc)
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/metrics":
            qs = parse_qs(parsed.query)
            try:
                sat_cfg, _ = _resolve_satellite_config(qs)
                payload = _predict_latest(sat_cfg)
                if not payload:
                    raise RuntimeError("No metrics payload generated.")
                self._send_json(payload)
            except Exception as exc:
                _REQUEST_STATS["last_error"] = str(exc)
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/satellites":
            try:
                payload = {"items": _load_satellite_presets()}
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/series":
            qs = parse_qs(parsed.query)
            minutes = int(qs.get("minutes", [720])[0])
            try:
                payload = _series(minutes)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/dst_series":
            qs = parse_qs(parsed.query)
            hours = int(qs.get("hours", [168])[0])
            interp = qs.get("interp", ["0"])[0] in ("1", "true", "True")
            try:
                payload = _fetch_dst_series(hours, interp)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/dst_forecast":
            qs = parse_qs(parsed.query)
            hours = int(qs.get("hours", [72])[0])
            try:
                payload = _fetch_dst_forecast(hours)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/dst_outlook":
            try:
                payload = _fetch_dst_outlook()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/cme_live":
            try:
                payload = _cme_live_payload()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/cme_climatology":
            try:
                payload = _cme_climatology_payload()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/cme_scenario":
            try:
                qs = parse_qs(parsed.query)
                payload = _cme_scenario_payload(qs)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/solar_wind_ml":
            qs = parse_qs(parsed.query)
            steps = int(qs.get("steps", [1])[0])
            try:
                payload = _forecast_solar_wind_ml(steps=steps)
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/solar_wind_phys":
            try:
                payload = _fetch_enlil_forecast()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/kp":
            try:
                payload = _fetch_kp()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/alerts":
            try:
                payload = _fetch_alerts()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/aurora":
            try:
                payload = _fetch_aurora()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return
        if parsed.path == "/api/solar_cycle":
            try:
                payload = _fetch_solar_cycle()
                self._send_json(payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, code=500)
            return

        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        return super().do_GET()

    def _send_json(self, payload, code=200):
        def _sanitize(obj):
            if isinstance(obj, float) and (obj != obj):
                return None
            if isinstance(obj, dict):
                return {k: _sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_sanitize(v) for v in obj]
            return obj

        body = json.dumps(_sanitize(payload)).encode("utf-8")
        try:
            if hasattr(self, "_request_start"):
                latency_ms = (time.time() - self._request_start) * 1000.0
                _REQUEST_STATS["last_latency_ms"] = round(latency_ms, 2)
                if _REQUEST_STATS["avg_latency_ms"] is None:
                    _REQUEST_STATS["avg_latency_ms"] = round(latency_ms, 2)
                else:
                    _REQUEST_STATS["avg_latency_ms"] = round(
                        0.9 * _REQUEST_STATS["avg_latency_ms"] + 0.1 * latency_ms, 2
                    )
            if code >= 400:
                _REQUEST_STATS["errors"] += 1
                _REQUEST_STATS["last_error"] = payload.get("error") if isinstance(payload, dict) else str(payload)
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", _cors_origin(self))
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except BrokenPipeError:
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Space weather dashboard server")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--web-dir", default=None, help="Directory to serve static web assets from")
    parser.add_argument("--disable-gpu", action="store_true", help="Force CPU-only inference (no GPU usage)")
    args = parser.parse_args()

    if args.disable_gpu:
        # Must be set before any TensorFlow import in this process.
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    web_dir = WEB_DIR
    if args.web_dir:
        web_dir = args.web_dir if os.path.isabs(args.web_dir) else os.path.join(ROOT, args.web_dir)
    if not os.path.isdir(web_dir):
        print(f"[warn] web dir not found: {web_dir}. Falling back to {WEB_DIR}")
        web_dir = WEB_DIR
    os.chdir(web_dir)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Server running on http://{args.host}:{args.port} (web dir: {web_dir})")
    server.serve_forever()
