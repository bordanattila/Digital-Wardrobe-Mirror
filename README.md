# Digital Wardrobe Mirror

[![Tests](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/test.yml/badge.svg)](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/test.yml)
[![Ruff](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/ruff.yml/badge.svg)](https://github.com/bordanattila/Digital-Wardrobe-Mirror/actions/workflows/ruff.yml)

A smart digital wardrobe application that organizes clothing, checks local weather conditions, and recommends outfits based on what is already in your closet.

The long-term goal is to run the deterministic stack on a **Raspberry Pi 5 connected to a display behind a two-way mirror**, with optional LLM reasoning (local home model or cloud — undecided) for preference-heavy outfit requests.

The project is currently being developed as a **desktop prototype** before any Raspberry Pi or mirror hardware is introduced.

---

## Overview

Choosing an outfit every morning can take more time than it should. Digital Wardrobe Mirror is designed to simplify that process by combining a personal digital wardrobe with weather-aware outfit recommendations.

Users can upload pictures of their clothing, remove the image backgrounds, organize the items in a virtual wardrobe, and receive outfit suggestions appropriate for the day's weather.

The project follows a simple pipeline:

```text
Clothing Photos
      ↓
Background Removal
      ↓
Digital Wardrobe
      ↓
Weather Data
      ↓
Outfit Selection
      ↓
Browser / Smart Mirror Interface
```

---

## Current Development Phase

### Phase 1 — Desktop Prototype

The first version is being developed entirely on a normal development machine.

The desktop prototype includes:

* FastAPI backend
* React/Vite frontend
* SQLite database
* Wardrobe image uploads
* Background removal
* Clothing metadata
* Weather integration
* Weather-aware outfit recommendations
* Browser-based user interface

No Raspberry Pi hardware is required during this phase.

Once the software is stable, the application can be migrated to the Raspberry Pi and integrated into the physical smart mirror.

---

## Features

### Digital Wardrobe

Users can add clothing items to their personal wardrobe.

Each item can eventually contain information such as:

* Clothing type
* Category
* Color
* Season
* Temperature suitability
* Image path
* Additional tags

Example categories may include:

```text
Tops
Bottoms
Shoes
Jackets
Sweaters
Accessories
```

---

### Wardrobe Image Upload

Users can upload photographs of clothing through the application.

Uploaded images are stored with the wardrobe and can be displayed visually when browsing clothing or viewing outfit recommendations.

---

### Background Removal

Clothing photos can have their backgrounds removed so that wardrobe items appear cleanly in the interface.

This allows clothing images to be displayed more naturally against the mirror or application background.

```text
Original Photo
      ↓
Background Removal
      ↓
Transparent Clothing Image
      ↓
Digital Wardrobe
```

---

### Weather Integration

The backend retrieves current weather information that can be used by the outfit recommendation system.

Relevant weather information may include:

* Temperature
* Feels-like temperature
* Weather conditions
* Precipitation
* Wind
* Daily forecast

---

### Outfit Recommendation Engine

Outfit recommendations are split into two layers.

**Deterministic (on-device):** weather, tags, and hard constraints are handled by the local outfit algorithm — no LLM required. Example: *47°F and raining → eliminate shorts, sandals, and light jackets; keep cool-weather and rain-compatible candidates.*

```text
Current Weather
      ↓
Determine Clothing Requirements
      ↓
Filter Wardrobe (rules / tags)
      ↓
Select Compatible Items
      ↓
Build Outfit
      ↓
Display Recommendation
```

For example, colder weather may prioritize long pants, sweaters, jackets, and closed shoes; warmer weather may prioritize T-shirts, shorts, and lightweight clothing.

**Reasoning (optional LLM):** higher-level requests — occasion, style relative to recent outfits, “not overdressed” — go to a local or cloud reasoning model. The Pi (or desktop prototype) builds a small structured context and sends that payload, for example:

```json
{
  "weather": {
    "temperature": 47,
    "condition": "rain"
  },
  "occasion": "casual dinner",
  "available_clothing": [
    "dark jeans",
    "navy chinos",
    "white oxford",
    "gray sweater",
    "brown boots"
  ],
  "recently_worn": [
    "dark jeans",
    "black hoodie"
  ]
}
```

Whether the reasoning model runs on a home PC (LM Studio / Ollama) or in the cloud (OpenAI / etc.) is still undecided.

---

## Technology Stack

### Backend

* Python
* FastAPI
* SQLite
* Uvicorn

The backend handles:

* Wardrobe data
* Image processing
* Weather data
* Deterministic outfit recommendation logic
* Optional structured reasoning requests to an LLM
* API endpoints

### Frontend

* React
* Vite
* JavaScript / JSX

The frontend provides the visual interface for:

* Uploading clothing
* Browsing the wardrobe
* Viewing weather information
* Displaying outfit recommendations

### Database

SQLite is used during the desktop prototype phase.

It provides a lightweight database for storing wardrobe information without requiring a separate database server.

---

## Project Structure

```text
DigitalWardrobeMirror/
│
├── .github/
│   └── workflows/
│       ├── ruff.yml
│       └── test.yml
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── routers/
│   │   │   ├── wardrobe.py
│   │   │   ├── weather.py
│   │   │   └── outfits.py
│   │   │
│   │   └── services/
│   │
│   ├── tests/
│   │   ├── test_database.py
│   │   └── test_background_service.py
│   │
│   └── wardrobe.db
│
├── frontend/
│   └── ...
│
├── assets/
│   └── wardrobe_images/
│
└── README.md
```

As development continues, additional services, models, schemas, components, and utilities can be added without changing the overall architecture.

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
│  SQLite wardrobe.db                          │
│  Weather service                             │
│  Outfit algorithm                            │
│  Camera / sensors                            │
│  Background removal                          │
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
                  ├─ Background Removal
                  ├─ Weather
                  ├─ Outfit Selection (deterministic)
                  └─ Reasoning request (optional LLM)
```

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd DigitalWardrobeMirror
```

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

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive API documentation will normally be available at:

```text
http://127.0.0.1:8000/docs
```

---

## Testing

Backend tests use **pytest**. From `backend/` with the virtual environment active:

```bash
pytest
```

GitHub Actions runs the same suite on every push and pull request to `main` (see the **Tests** badge at the top of this README). Lint and formatting are checked separately by the **Ruff** workflow.

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

Vite will display the local frontend address in the terminal.

---

## API Organization

The FastAPI application is divided into feature-specific routers.

### Wardrobe

```text
backend/app/routers/wardrobe.py
```

Responsible for operations such as:

* Adding clothing
* Retrieving wardrobe items
* Updating clothing
* Removing clothing
* Handling wardrobe images

### Weather

```text
backend/app/routers/weather.py
```

Responsible for retrieving and exposing weather information used by the application.

### Outfits

```text
backend/app/routers/outfits.py
```

Responsible for generating outfit recommendations: local rule-based selection from wardrobe and weather, plus optional structured reasoning requests to a local or cloud LLM.

---

## Development Roadmap

### Phase 1 — Desktop Prototype

Build and validate the complete software workflow.

```text
FastAPI
SQLite
Wardrobe Uploader
Background Removal
Weather
Outfit Algorithm
Browser UI
```

### Phase 2 — Improve Outfit Intelligence

Strengthen the **on-device** deterministic engine (tags, weather rules, rain, layering, recently worn, favorites, user feedback) so routine morning picks stay fast and local.

Separately, add an optional **reasoning path**: build structured context from wardrobe + weather + occasion, send it to a local or cloud LLM, and return suggestions for preference-heavy requests. Hosting choice (home PC vs cloud) remains open.

### Phase 3 — Smart Mirror Interface

Create a simplified full-screen interface designed specifically for mirror use.

Potential information displayed:

```text
Good Morning

72°F
Partly Cloudy

Today's Outfit

[ Shirt ]
[ Pants ]
[ Shoes ]

Today's Forecast
```

### Phase 4 — Raspberry Pi Deployment

Move the deterministic stack onto a Raspberry Pi 5 behind a two-way mirror. The Pi runs UI, API, database, weather, outfit algorithm, and related local services; reasoning requests (if enabled) go out to whichever model host is chosen.

```text
Raspberry Pi 5
     │
     ├── React / Mirror UI
     ├── FastAPI
     ├── SQLite wardrobe.db
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

CI: [Tests](https://github.com/bordanattila/DigitalWardrobeMirror/actions/workflows/test.yml) · [Ruff](https://github.com/bordanattila/DigitalWardrobeMirror/actions/workflows/ruff.yml)

The project is under active development. Features, architecture, and documentation may change as the prototype evolves.

---

## License

A license has not yet been selected for this project.
