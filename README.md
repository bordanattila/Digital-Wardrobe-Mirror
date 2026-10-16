# Digital Wardrobe Mirror

[![Tests](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/test.yml/badge.svg)](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/test.yml)
[![Ruff](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/ruff.yml/badge.svg)](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/ruff.yml)

A smart digital wardrobe application that organizes clothing, checks local weather conditions, and recommends outfits based on what is already in your closet.

The long-term goal is to run the deterministic stack on a **Raspberry Pi 5 connected to a display behind a two-way mirror**, with optional LLM reasoning (local home model or cloud — undecided) for preference-heavy outfit requests.

The project is currently being developed as a **desktop prototype** before any Raspberry Pi or mirror hardware is introduced.

---

## Overview

Choosing an outfit every morning can take more time than it should. Digital Wardrobe Mirror is designed to simplify that process by combining a personal digital wardrobe with weather-aware outfit recommendations.

Users can upload pictures of their clothing (phone-oriented upload page), remove image backgrounds to transparent PNGs, browse the wardrobe, and receive outfit suggestions appropriate for the day's weather on a mirror-style dashboard.

The project follows a simple pipeline:

```text
Clothing Photos
      ↓
Background Removal (rembg → PNG with alpha)
      ↓
Digital Wardrobe (SQLite + processed images)
      ↓
Weather Data
      ↓
Outfit Selection (deterministic rules)
      ↓
Browser / Smart Mirror Interface
```

---

## Current Development Phase

### Phase 1 — Desktop Prototype

The first version is being developed entirely on a normal development machine.

The desktop prototype includes:

* FastAPI backend
* React + TypeScript / Vite frontend (`react-router`)
* SQLite database + Alembic migrations
* Wardrobe image uploads (`POST /api/wardrobe/upload`)
* Background removal via **rembg** (transparent PNG output)
* Clothing metadata (name, color, size, category, subcategory)
* Weather integration (OpenWeather + ipinfo for location)
* Weather-aware outfit suggestions (`GET /api/outfits/suggest`)
* Mirror UI (`/`), phone upload UI (`/upload`), full wardrobe UI (`/full-wardrobe`)

No Raspberry Pi hardware is required during this phase.

Once the software is stable, the application can be migrated to the Raspberry Pi and integrated into the physical smart mirror.

---

## Features

### Digital Wardrobe

Users can add clothing items to their personal wardrobe.

Each item currently stores:

* Name
* Color
* Size
* Category (e.g. `top`, `bottom`, `jacket`, `shoes`, `accessory`)
* Subcategory (e.g. `t-shirt`, `jeans`, `hoodie` — used by the outfit filter)
* Processed image filename

Season tags, temperature suitability fields, and richer tagging are planned later.

---

### Wardrobe Image Upload

Users upload photographs through the **`/upload`** page (intended for phone use). The mirror home screen does not host the upload form.

Uploaded originals are stored under `backend/wardrobe_images/original/`. After processing, the API serves cutouts from `backend/wardrobe_images/processed/`. The database stores the processed **filename** only (not an absolute filesystem path).

---

### Background Removal

Clothing photos are processed with **rembg** so wardrobe items appear as transparent PNGs against the dark mirror UI.

Processing also:

* Applies EXIF orientation (`ImageOps.exif_transpose`)
* Forces portrait when the frame is still landscape (common for phone shots whose EXIF was stripped)
* Always writes **`.png`** (JPEG cannot keep transparency)

```text
Original Photo
      ↓
Orient + optional portrait fix
      ↓
rembg cutout
      ↓
Transparent PNG
      ↓
Digital Wardrobe / Mirror cards
```

---

### Weather Integration

The backend retrieves **current** weather used by the outfit suggestion flow and mirror UI.

Fields available today:

* Temperature (°C and °F)
* Conditions description
* Weather icon code
* City (from IP geolocation of the **server** egress IP)

Feels-like temperature, precipitation chance, wind, and multi-day forecast are not exposed yet.

---

### Outfit Recommendation Engine

Outfit recommendations are split into two layers.

**Deterministic (on-device, implemented):** weather and wardrobe subcategory/category allowlists filter candidates — no LLM required. Example: at or above 70°F prefer warm-weather pieces (`t-shirt`, `shorts`, …); below that prefer cool-weather pieces (`hoodie`, `jeans`, …). The suggest API returns matching tops, bottoms, and the current weather payload.

```text
Current Weather
      ↓
Choose warm- vs cool-weather allowlists
      ↓
Filter wardrobe items
      ↓
Return suggested tops + bottoms
      ↓
Mirror UI
```

**Reasoning (optional LLM, not implemented yet):** higher-level requests — occasion, style relative to recent outfits, “not overdressed” — will go to a local or cloud reasoning model with a small structured context payload. Hosting (home PC via LM Studio / Ollama vs cloud) is still undecided.

---

### UI surfaces

* **`/` (mirror)** — large-type dashboard for a display behind a two-way mirror (not touch-first). Side panels for clock, weather, and outfit suggestions; center left clear for reflection. Voice can later call the same suggest API.
* **`/upload`** — mobile-friendly clothing form + photo capture/upload.
* **`/full-wardrobe`** — browse inventory and delete items.

---

## Technology Stack

### Backend

* Python
* FastAPI
* SQLite
* Alembic (schema migrations)
* SQLAlchemy (models for Alembic; CRUD still uses sqlite3)
* Uvicorn
* Pillow
* rembg (background removal)

The backend handles:

* Wardrobe CRUD and image serving
* Image processing (orient, rembg, PNG save)
* Weather data
* Deterministic outfit suggestion logic
* API endpoints

### Frontend

* React 19
* TypeScript / TSX
* Vite
* react-router-dom

The frontend provides:

* Mirror dashboard
* Phone upload form
* Full wardrobe browser
* Dev proxy from Vite (`/api`, `/health`) → FastAPI on port 8000

### Database

SQLite is used during the desktop prototype phase (`digital_wardrobe_mirror.db` in `backend/`).

Schema changes are managed with **Alembic**. The app does not create tables on startup — run migrations before starting the API (see [Getting Started](#getting-started)).

The `ClothingItem` table stores wardrobe metadata. Keep the SQLAlchemy model `__tablename__` in sync with the table name used in `database.py` (`ClothingItem`).

---

## Project Structure

```text
DigitalWardrobeMirror/
│
├── .github/
│   └── workflows/
│       ├── ruff.yml
│       └── test.yml            # backend pytest + frontend vitest
│
├── backend/
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/          # migration scripts
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py        # sqlite3 CRUD
│   │   ├── models/            # SQLAlchemy models (Alembic)
│   │   ├── schemas/
│   │   ├── routers/
│   │   │   ├── wardrobe.py
│   │   │   ├── weather.py
│   │   │   └── outfits.py
│   │   ├── services/
│   │   │   ├── background_service.py
│   │   │   ├── wardrobe_service.py
│   │   │   ├── weather_service.py
│   │   │   └── outfit_service.py
│   │   └── utils/
│   ├── tests/
│   ├── wardrobe_images/
│   │   ├── original/
│   │   └── processed/
│   ├── .env.example
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── digital_wardrobe_mirror.db   # created by Alembic (gitignored)
│
├── frontend/
│   ├── src/
│   │   ├── pages/             # mirror, upload, full_wardrobe
│   │   ├── api.ts
│   │   └── App.tsx            # routes: /, /upload, /full-wardrobe
│   └── ...
│
└── README.md
```

---

## Architecture

The long-term target puts the **full deterministic stack on a Raspberry Pi 5**. Local software owns the wardrobe, weather, rule-based outfit filtering, camera/sensors, background removal, and voice I/O. An LLM is used only for higher-level reasoning requests, via a small structured context payload.

Local vs cloud hosting for that reasoning model is still an open decision.

```text
                   DIGITAL WARDROBE MIRROR

┌──────────────────────────────────────────────┐
│               Raspberry Pi 5                 │
│                                              │
│  React / Mirror UI                           │
│  FastAPI                                     │
│  SQLite digital_wardrobe_mirror.db           │
│  Weather service                             │
│  Outfit algorithm                            │
│  Camera / sensors                            │
│  Background removal (rembg)                  │
│  Voice input/output                          │
│                                              │
│          ↓ reasoning request                 │
└──────────────────────┬───────────────────────┘
                       │
             ┌─────────┴──────────┐
             │                    │
             ▼                    ▼
      LOCAL HOME MODEL        CLOUD MODEL
      PC / workstation        OpenAI/etc.
      LM Studio / Ollama
```

During Phase 1, the same software runs as a **desktop prototype** (React/Vite UI ↔ FastAPI ↔ SQLite and services). Presentation, API, business logic, and persistence stay separated so components can be replaced later without redesigning the whole app.

```text
┌──────────────────────────────┐
│       React / Vite UI        │
└──────────────┬───────────────┘
               │
             HTTP
               │
┌──────────────▼───────────────┐
│           FastAPI            │
│                              │
│  Wardrobe | Weather | Outfit │
└──────────────┬───────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   SQLite DB      Services
                  │
                  ├─ Background Removal (rembg)
                  ├─ Weather
                  ├─ Outfit Selection (deterministic)
                  └─ Reasoning request (optional LLM, later)
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/bordanattila/Digital-Wardrobe-Mirror.git
cd Digital-Wardrobe-Mirror
```

(If your local folder is named `DigitalWardrobeMirror`, `cd` into that instead.)

---

## Backend

Move into the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux or WSL:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

`requirements.txt` includes **Pillow** and **`rembg[cpu]`** (installs `onnxruntime`). The first rembg run may download an ONNX model (one-time). For NVIDIA GPUs you can instead use `pip install "rembg[gpu]"`.

Copy the example environment file and add your weather API secrets:

```bash
cp .env.example .env
# Edit .env and set WEATHER_API_KEY and IP_INFO_TOKEN
```

Apply database migrations (required before the first API start, and after pulling new migrations):

```bash
alembic upgrade head
```

This creates `digital_wardrobe_mirror.db` and the `ClothingItem` table if needed. Always run Alembic commands from the `backend/` directory so the SQLite path in `alembic.ini` resolves correctly.

Useful Alembic commands:

```bash
alembic current          # show applied revision
alembic history          # list revisions
alembic revision --autogenerate -m "describe change"   # after editing app/models/
alembic upgrade head     # apply pending migrations
```

Review autogenerated revisions before applying them.

Start the FastAPI development server:

```bash
# Prefer localhost binding for local development
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Weather / privacy note

`GET /api/weather/` uses IP geolocation (ipinfo) based on the **server’s** egress IP, then fetches conditions from OpenWeather. That is appropriate for a single-user home/Pi setup. Do not forward client `X-Forwarded-For` addresses to a geo API if you later expose the service beyond localhost/LAN.

---

## Testing

### Backend

From `backend/` with the virtual environment active:

```bash
pytest
```

Background-removal tests **mock** `rembg.remove` so CI does not download models or run inference. `onnxruntime` must still be installed so importing `rembg` succeeds during collection.

### Frontend

From `frontend/`:

```bash
npm test
```

### CI

GitHub Actions runs **pytest** and **Vitest** on every push and pull request to `main`/`master` (see the **Tests** badge). Lint and formatting are checked separately by the **Ruff** workflow.

---

## Frontend

Open another terminal and move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Vite prints the local URL (typically `http://127.0.0.1:5173`). In development, leave `VITE_API_BASE_URL` empty so the Vite proxy forwards `/api` and `/health` to FastAPI on port 8000.

Routes:

| Path | Page |
|------|------|
| `/` | Mirror dashboard |
| `/upload` | Add clothing (phone) |
| `/full-wardrobe` | Full inventory |

---

## API Organization

The FastAPI application is divided into feature-specific routers. It is intended for localhost / home LAN use during the prototype — not as a public internet API.

### Wardrobe

```text
backend/app/routers/wardrobe.py
```

Prefix: `/api/wardrobe`

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | List items |
| `GET` | `/{id}` | Get one item |
| `PUT` | `/{id}` | Update metadata |
| `DELETE` | `/{id}` | Delete item (+ processed image cleanup) |
| `POST` | `/upload` | Create item from multipart form + image |
| `GET` | `/{id}/image` | Serve processed image file |

### Weather

```text
backend/app/routers/weather.py
```

Prefix: `/api/weather` — current conditions for the server location.

### Outfits

```text
backend/app/routers/outfits.py
```

Prefix: `/api/outfits`

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/suggest` | Weather + wardrobe → suggested tops/bottoms |

Also: `GET /health` and `GET /` on the app root.

---

## Development Roadmap

### Phase 1 — Desktop Prototype

Build and validate the complete software workflow.

```text
FastAPI
SQLite
Wardrobe Uploader
Background Removal (rembg)
Weather
Outfit Algorithm
Browser UI (mirror / upload / wardrobe)
```

### Phase 2 — Improve Outfit Intelligence

Strengthen the **on-device** deterministic engine (tags, weather rules, rain, layering, recently worn, favorites, user feedback) so routine morning picks stay fast and local.

Separately, add an optional **reasoning path**: build structured context from wardrobe + weather + occasion, send it to a local or cloud LLM, and return suggestions for preference-heavy requests. Hosting choice (home PC vs cloud) remains open.

### Phase 3 — Smart Mirror Interface

Create a simplified full-screen interface designed specifically for mirror use (voice-first interaction, center clear for reflection, glassmorphism polish).

### Phase 4 — Raspberry Pi Deployment

Move the deterministic stack onto a Raspberry Pi 5 behind a two-way mirror. Prefer **systemd** + journald logging for headless operation. The Pi runs UI, API, database, weather, outfit algorithm, and related local services; reasoning requests (if enabled) go out to whichever model host is chosen.

```text
Raspberry Pi 5
     │
     ├── React / Mirror UI
     ├── FastAPI
     ├── SQLite digital_wardrobe_mirror.db
     ├── Weather + outfit algorithm
     ├── Camera / sensors, background removal, voice (as added)
     │
     ├──→ optional: local home model (LM Studio / Ollama)
     └──→ optional: cloud model (OpenAI / etc.)
     │
     ▼
Monitor / Display → Two-Way Mirror
```

### Phase 5 — Advanced Features

Possible future additions include:

* Outfit history
* Clothing usage statistics
* Laundry status
* Favorite outfits
* Calendar-aware / dress-code recommendations
* Voice interaction
* Touch or gesture controls
* Automatic wardrobe categorization / clothing recognition
* Personalized recommendation learning
* Morning brief integration
* Image serving polish (`image_url` on DTOs, `Cache-Control`, thumbnails)

---

## Project Goals

Digital Wardrobe Mirror is both a practical smart-home project and an opportunity to explore the integration of:

* Full-stack web development
* Python APIs
* Computer vision and image processing
* External APIs
* Deterministic recommendation algorithms on-device
* Optional LLM reasoning with structured context
* Raspberry Pi / smart-mirror hardware
* AI-assisted software development

The project is intentionally built incrementally so software can be validated on a desktop before introducing hardware complexity.

---

## Status

**Current stage:** Phase 1 — Desktop Prototype

CI: [Tests](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/test.yml) · [Ruff](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/ruff.yml)

The project is under active development. Features, architecture, and documentation may change as the prototype evolves.

---

## License

A license has not yet been selected for this project.
