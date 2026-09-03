# Space Weather Monitoring & Solar Storm Risk Predicton

Real-data pipeline for 15-minute forecasting of geomagnetic storm risk and SYM/H (Dst proxy), with a live web UI dashboard.

## Data sources (real datasets)
- **Solar wind 1-minute** (solar wind + IMF + geomagnetic indices):
  - https://spdf.gsfc.nasa.gov/pub/data/omni/high_res_omni/
- **XRS flare reports** (event list):
  - https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/
- **Optional**: XRS 1-minute flux time series (large)
  - https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/

## Current status
- Solar wind 1-minute data (1995–2025) already downloaded into `data/omni/`.
- X-ray flare reports (1975–2016) already downloaded into `data/flare_reports/`.
- XRS 1-minute flux data is **optional** and very large.

## Pipeline
### 1) Parse 1-minute solar wind into CSV
```
python3 src/parse_omni.py --input-dir data/omni --output-csv data/processed/omni.csv
```

### 2) Build ML dataset (15-minute horizon)
```
python3 src/build_dataset.py \
  --omni-csv data/processed/omni.csv \
  --flare-reports-dir data/flare_reports \
  --output-csv data/processed/dataset.csv \
  --horizon-min 15
```

### 3) Train models
```
python3 src/train.py --data-csv data/processed/dataset.csv --model-dir models
```

### 3a) Full dataset training (out-of-core, Parquet shards)
If the dataset CSV is too large for memory, shard it into Parquet and train with streaming models:
```
python3 src/make_parquet_shards.py \
  --data-csv data/processed/dataset.csv \
  --out-dir data/processed/parquet \
  --train-end 2017-12-31 \
  --val-end 2021-12-31 \
  --chunksize 100000

python3 src/train_streaming.py \
  --parquet-dir data/processed/parquet \
  --model-dir models \
  --epochs 1 \
  --max-eval-rows 200000
```

### 3b) Stronger models (LightGBM over Parquet shards)
LightGBM tends to produce better non-linear decision boundaries and better storm risk probabilities.
```
python3 src/train_lgbm.py \
  --parquet-dir data/processed/parquet \
  --model-dir models \
  --rounds-per-shard 10 \
  --max-eval-rows 300000
```

### 4) Predict (fast inference)
Provide a CSV of the latest minute-by-minute solar-wind-like rows (at least 60 minutes of history for rolling features):
```
python3 src/predict.py --latest-csv data/latest_window.csv --model-dir models
```

## Web UI (real-time dashboard)
Start the server after training:
```
python3 src/server.py
```
Then open `http://localhost:8000` in a browser.

UI assets:
- Place `public/solar-system.mp4` (optional poster `public/solar-system.jpg`) for the animated background.

### Expose online (basic)
```
python3 src/server.py --host 0.0.0.0 --port 8000
```
Open the port in your firewall or put it behind a reverse proxy (recommended) for HTTPS.

## Live data updates (near real-time)
The dashboard reads `data/processed/omni.csv`. To keep it fresh, run the updater on a schedule:
```
python3 src/update_live_omni.py --output-csv data/processed/omni_live.csv
```

### Example cron (every 1 minute)
```
* * * * * cd /home/ai/project/ml\ model && /usr/bin/python3 src/update_live_omni.py --output-csv data/processed/omni_live.csv >> logs/live_update.log 2>&1
```

Notes:
- The live updater uses real-time solar wind feeds and approximates some fields not present in those feeds.

## Models
- **storm_model**: probability that SYM/H ≤ −50 nT within 15 minutes.
- **symh_model**: regression forecast of SYM/H at +15 minutes.
- **flare_model** (optional): probability of M/X flare within 15 minutes (labeled from flare reports).
- **flare_class** (nowcast): class inferred from X-ray flux (A/B/C/M/X).
- **sep_risk** (nowcast): S-scale derived from >10 MeV proton flux.

## Notes
- Inference is lightweight (tree-based models). With a cached feature window, predictions are millisecond-scale.
- The streaming trainer uses linear models to support out-of-core training; accuracy may differ from tree models.
- For stronger flare prediction, integrate XRS flux time series and add features.
- GNSS/satcom impact cards are heuristic mappings from storm/SEP/Kp levels, not a trained model.

## Drag risk (JB2008 indices, 3-hour regression)
This optional pipeline predicts the JB2008 DTC (thermospheric temperature correction) 3 hours ahead as a drag-risk proxy.

### 1) Download official indices
```
python3 src/fetch_jb2008_indices.py --out-dir data/indices/jb2008 --with-swall
```

### 2) Build 3-hour drag dataset
```
python3 src/build_drag_dataset.py \
  --indices-dir data/indices/jb2008 \
  --swall-path data/indices/jb2008/SW-All.csv \
  --horizon-hours 3 \
  --out-csv data/processed/drag_dataset.csv
```

### 3) Train drag regression model
```
python3 src/train_drag_lgbm.py \
  --data-csv data/processed/drag_dataset.csv \
  --model-dir models \
  --train-end 2020-12-31
```

### 4) Predict latest drag proxy
```
python3 src/predict_drag.py \
  --indices-dir data/indices/jb2008 \
  --swall-path data/indices/jb2008/SW-All.csv \
  --model-dir models
```

Notes:
- DTC is a temperature correction term used by JB2008; it correlates with thermospheric density (drag).
- For satellite-specific drag, add orbit parameters (altitude, latitude, local solar time) and fit a density model directly.

## Satellite impact (anomaly classifier)
This pipeline labels satellite impact events using historical anomaly tables and trains a binary classifier.

### 1) Download anomaly datasets (NCEI + GOES EXIS)
```
mkdir -p /media/ai/DATADRIVE1/kl/data/impact/ncei
cd /media/ai/DATADRIVE1/kl/data/impact/ncei
wget -c https://www.ngdc.noaa.gov/stp/space-weather/satellite-data/spacecraft-anomalies/data/anom5j.xls
wget -c https://www.ngdc.noaa.gov/stp/space-weather/satellite-data/spacecraft-anomalies/data/tdrs5j.xls
wget -c https://www.ngdc.noaa.gov/stp/space-weather/satellite-data/spacecraft-anomalies/data/g16_g17_exs_spw.xlsx
wget -c https://www.ngdc.noaa.gov/stp/space-weather/satellite-data/spacecraft-anomalies/documentation/Readme_g16_g17_exs_spw_v2.pdf
```

### 2) Build satellite impact dataset
```
python3 src/build_satellite_impact_dataset.py \
  --omni-csv /media/ai/DATADRIVE1/kl/data/processed/omni.csv \
  --impact-dir /media/ai/DATADRIVE1/kl/data/impact/ncei \
  --out-csv /media/ai/DATADRIVE1/kl/data/processed/sat_impact_dataset.csv \
  --horizon-hours 6
```

### 3) Train satellite impact classifier
```
python3 src/train_sat_impact_lgbm.py \
  --data-csv /media/ai/DATADRIVE1/kl/data/processed/sat_impact_dataset.csv \
  --model-dir /media/ai/DATADRIVE1/kl/models \
  --label-col sat_impact_next_6h \
  --train-end 2017-12-31 \
  --val-end 2021-12-31
```

## Production Ops Notes
### Model assumptions & limitations
- Forecasts are statistical and inherit biases from OMNI + NOAA upstream feeds.
- Storm risk is calibrated for SYM/H ≤ −50 nT at +15 min; adjust thresholds per mission.
- GIC/GNSS/SATCOM impact panels are heuristic mappings and not certified advisories.
- Data latency and gaps can degrade prediction quality; check `/api/quality` regularly.

### Health, drift, and registry
- `/api/health` returns uptime, request stats, and data quality status.
- `/api/quality` exposes data gaps, missing rate, and optional drift score.
- Model metadata is appended to `models_deploy/registry.json` after training.
- Build a drift baseline with:
  `python3 src/compute_feature_baseline.py --omni-csv data/processed/omni.csv`

### Security & config
- Optional API key via `API_KEY` + `REQUIRE_API_KEY=1` (client uses `NEXT_PUBLIC_API_KEY`).
- CORS + security headers enabled in the API server and Next.js.
- Example reverse proxy: `configs/nginx.conf`

### Scheduling
- Example cron jobs are in `configs/cron.example`
