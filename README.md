# BioScale

BioScale estimates phenotypic (biological) age from lifestyle and health inputs, with SHAP-based explanations, served through a FastAPI backend and a Next.js web interface.

## Overview

BioScale is a research-oriented toolkit for lifestyle-based phenotypic age estimation. The project combines:

- **Machine learning** — trained regressors and calibration logic for phenotypic age
- **A REST API** — `/predict` and `/health` endpoints for programmatic use
- **A web frontend** — an interactive tool for entering inputs and viewing results

The model is trained and validated on harmonized NHANES survey data (see [Data](#data) below).

## Repository structure

```
BioScale/
├── frontend/              # Next.js 14 + TypeScript + Tailwind UI
│   ├── app/               # Routes: /, /tool, /methods
│   ├── components/        # UI components and phenotypic-age tool
│   └── lib/               # API client (NEXT_PUBLIC_API_BASE_URL)
├── bioscale/              # Python ML pipeline and API
│   ├── src/bioscale/      # Core package (models, calibration, API)
│   ├── src/tests/         # Pytest suite
│   ├── backend/           # FastAPI app (backend/api/app.py) and NHANES ETL
│   ├── models/            # Trained model artifacts (e.g. lifestyle_regressor.joblib)
│   └── data/              # Raw, interim, and processed NHANES data
├── backend/               # Dockerfile for containerized API deployment
├── data/                  # Additional shared data artifacts
├── requirements.txt       # Python dependencies (root-level)
├── .env.example           # Backend/shared env template (MODEL_VERSION)
└── API_DOCUMENTATION.md   # API reference
```

## Getting started

### Prerequisites

- **Node.js** 18+ and npm (frontend)
- **Python** 3.11+ and pip (backend / ML)

### Frontend (local)

```bash
cd frontend
npm install
cp .env.example .env.local   # or create .env.local manually on Windows
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` to your backend origin (default: `http://localhost:8000`).

Production build check:

```bash
npm run build
npm start
```

### Backend (local)

From the repository root:

```bash
cd bioscale
pip install -r ../requirements.txt
```

**PowerShell:**

```powershell
$env:PYTHONPATH = "src"
uvicorn bioscale.api.main:app --reload --host 0.0.0.0 --port 8000
```

**bash:**

```bash
export PYTHONPATH=src
uvicorn bioscale.api.main:app --reload --host 0.0.0.0 --port 8000
```

An alternate entry point lives at `backend/api/app.py`:

```bash
uvicorn backend.api.app:app --reload --host 0.0.0.0 --port 8000
```

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Optional: copy the root `.env.example` to `.env` and set `MODEL_VERSION` if you override defaults.

### Run tests

From `bioscale/` with `PYTHONPATH=src`:

```bash
python -m pytest src/tests/ -q
```

## Data

BioScale uses **NHANES** (National Health and Nutrition Examination Survey) public-use files for training and ETL.

| Location | What it contains | In git? |
|----------|------------------|---------|
| `bioscale/data/raw/` | NHANES `.xpt` / lab / questionnaire files | Large raw files are **gitignored**; obtain via the ETL docs |
| `bioscale/data/processed/` | Harmonized tables for modeling | Small processed outputs may be committed |
| `bioscale/data/interim/` | Pipeline intermediate outputs | **Gitignored** — regenerate via ETL |
| `bioscale/models/` | Trained joblib artifacts | Committed when present |
| `data/` | Shared artifacts (e.g. SHAP samples) | Selective |

To download and prepare NHANES data, follow **[bioscale/backend/etl/README.md](bioscale/backend/etl/README.md)**.
