# GreenQuest 🌲

> **Personalized outdoor micro-adventures using open-weight AI.**  
> *Hacktoberfest 2026 Open-Source AI Challenge Submission*

[![GreenQuest CI](https://github.com/greenquest/greenquest/actions/workflows/test.yml/badge.svg)](https://github.com/greenquest/greenquest/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-forest.svg)](LICENSE)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-forest.svg)](https://www.python.org/)
[![React: 18](https://img.shields.io/badge/React-18-forest.svg)](https://react.dev/)
[![Offline PWA](https://img.shields.io/badge/PWA-Offline%20Capable-amber.svg)](https://web.dev/progressive-web-apps/)

---

## 🍃 Project Vision & Philosophy

Modern screens command too much of our attention. **GreenQuest** is a mobile-first, offline-capable Progressive Web App (PWA) designed to get people **off** their devices and **into** local parks, community gardens, trails, waterfronts, and neighborhoods.

Users enter simple preferences (environment, time available, mood, energy level, companion, sensory focus). GreenQuest then generates a structured, bite-sized micro-adventure (15–60 minutes) featuring sensory prompts, tactile exploration steps, and leave-no-trace stewardship principles.

Once loaded, the entire application works **100% offline**:
- Assets are cached by a Service Worker.
- Missions, checklists, and completion history persist locally in browser storage.
- A dual-layer deterministic procedural fallback engine creates authentic quests even when AI servers or internet connections are completely unavailable.

---

## 🎨 Visual Identity

GreenQuest rejects generic AI dashboard aesthetics in favor of a calm, grounded nature companion:
- **Deep Forest Green** (`#1b382b`): Grounding foundation, header, and primary actions.
- **Warm Cream** (`#fbf8f1`): Soothing daylight background, paper-textured card surfaces.
- **Muted Sage** (`#8ea893`): Subtle botanical accents, borders, and calm sensory tags.
- **Restrained Amber** (`#d97736`): Sunlit highlights, active step indicators, and energy tags.
- Large tactile controls and high-contrast typography optimized for outdoor mobile use under bright sunlight.

---

## 🏛 Architecture & Tech Stack

```mermaid
graph TD
    subgraph Frontend ["Client (React + Vite + Tailwind CSS)"]
        UI["Tactile Preferences UI"] --> ActiveMission["Mission View & Checklist"]
        ActiveMission <--> LocalStorage["Local Persistence\n(IndexedDB/LocalStorage)"]
        SW["Service Worker (PWA Cache)"] -.-> UI
        ClientFallback["In-Browser Fallback Engine"] -.-> ActiveMission
    end

    subgraph Backend ["Backend (FastAPI)"]
        API["FastAPI /api/missions/generate"] --> StateMachine["State Machine Orchestrator"]
        
        StateMachine --> Planner["1. Planner Agent"]
        Planner --> Activity["2. Nature Activity Agent"]
        Activity --> Safety["3. Safety Validator Agent"]
        Safety --> RuleEngine{"Deterministic Guardrails"}

        RuleEngine -->|"Safe"| Success["Structured Mission JSON"]
        RuleEngine -->|"Retry < 2"| Activity
        RuleEngine -->|"Retries Exceeded"| FallbackEngine["Deterministic Fallback Engine"]
        
        StateMachine -.->|"Ollama Unreachable"| FallbackEngine
    end

    UI -->|"POST /generate"| API
    Success --> UI
    FallbackEngine --> UI
```

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Service Worker PWA.
- **Backend**: Python 3.11+, FastAPI, Pydantic v2, Pydantic-Settings, HTTPX, Pytest.
- **Local Inference Target**: Ollama with `gemma3:1b` (optimized for 16 GB RAM laptops with integrated graphics; no GPU needed).
- **Optional Hosted Inference**: OpenAI-compatible adapter for hosted open-weight models.
- **Deterministic Safeguards**: Zero-trust rule engine enforcing foraging bans, trespassing bans, water/cliff hazard filters, and Leave-No-Trace principles.
- **Deployment**: Render Blueprint (`render.yaml`).

---

## 🚀 Quickstart & Local Setup

### Prerequisites
- **Python 3.11+**
- **Node.js 20+** and **npm**
- *(Optional for AI inference)*: [Ollama](https://ollama.ai) installed with `gemma3:1b` (`ollama pull gemma3:1b`). If Ollama is not installed or running, GreenQuest seamlessly activates its deterministic fallback engine.

### 1. Clone & Configure
```bash
git clone https://github.com/greenquest/greenquest.git
cd greenquest
cp .env.example .env
```

### 2. Start Backend API
```bash
# Install backend dependencies
pip install -r requirements.txt

# Start FastAPI server with hot-reload
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: `http://localhost:8000/docs`

### 3. Start Frontend PWA
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 🧪 Automated Testing & Verification

GreenQuest includes an automated test suite verifying schemas, safety rules, providers, and API contracts.

### Run Backend Test Suite
```bash
python3 -m pytest -v backend/tests
```
**Results Verified (31/31 passing)**:
- `test_schemas.py`: Preference request bounds, sensory deduplication, step validation, serialization.
- `test_safety_rules.py`: Foraging/ingestion rejection, trespassing filter, hazardous water/cliff bans, wildlife harassment filter, leave-no-trace enforcement.
- `test_providers.py`: Deterministic fallback generator across all environments, Ollama unreachable handling, Hosted unconfigured handling.
- `test_orchestrator.py`: State machine execution, bounded retry loop, remediation injection, automated fallback triggers.
- `test_regression_ollama.py`: Gemma 3 1B structured format enforcement, JSON repair (quotes, trailing commas, step delimiters), duration harmonization, and timeout recovery.
- `test_api.py`: FastAPI `/api/health`, `/api/providers`, `/api/missions/sample`, and `/api/missions/generate`.

### Build & Verify Frontend PWA
```bash
cd frontend
npm run build
```
Compiles TypeScript with strict type checking and produces optimized static assets in `frontend/dist`.

---

## ⚡ Local Inference vs Hosted Deployment

To maintain transparency for users and evaluators, GreenQuest explicitly distinguishes between local inference and hosted deployment modes:

| Dimension | Local Development / Self-Hosted | Hosted Deployment (e.g. Render Free Tier) |
|---|---|---|
| **Model Execution** | Runs **locally** on your laptop/desktop via Ollama (`gemma3:1b`). | Free tier containers **do not** run Ollama or local LLM weights (no local GPU/Ollama daemon). |
| **Default Provider** | `MODEL_PROVIDER=ollama` | `MODEL_PROVIDER=fallback` (`FORCE_FALLBACK=true`) |
| **Privacy & Cost** | 100% private, 0 external API calls, 0 cost. | 100% free to host, 0 external API calls, instant responses. |
| **Optional Cloud LLM** | Can configure hosted API adapter if desired. | Can configure `MODEL_PROVIDER=hosted` with `HOSTED_API_KEY` (e.g., Together, Groq, OpenRouter). |
| **Visitor PWA Experience** | Direct connection to local FastAPI backend. | Visitors' browsers **do not** download or run LLM weights. If visitors lose internet connectivity, the PWA seamlessly transitions to the in-browser deterministic generator. |

---

## 🛡 Deterministic Safety Rules

LLMs are creative generators, not safety authorities. All outputs pass deterministic validation filters:
1. **Zero Wild Ingestion**: Strictly prohibits eating, chewing, or tasting berries, plants, mushrooms, fungi, or unpurified water.
2. **Zero Trespassing**: Prohibits private land entry, climbing fences, or wandering off public recreational paths.
3. **Terrain & Water Guard**: Rejects cliff edges, steep ascents, fast-flowing river crossings, and hazardous tree climbs.
4. **Wildlife Protection**: Prohibits touching, chasing, cornering, or feeding wild animals.
5. **Leave-No-Trace**: Enforces environmental stewardship principles in every mission.

---

## ☁️ Deployment (Render)

GreenQuest includes a zero-cost `render.yaml` blueprint:
- **Backend (`greenquest-api`)**: Python Web Service running FastAPI via Uvicorn. Configured out of the box with `MODEL_PROVIDER=fallback` and `FORCE_FALLBACK=true` so the service boots instantly on free compute without requiring external keys or GPU hardware.
- **Frontend (`greenquest-pwa`)**: Static Site building the Vite React PWA and serving static assets with client-side SPA routing (`/* -> /index.html`). Automatically connects to `greenquest-api` via Render's service discovery.

### Steps to Deploy to Render:
1. Fork or push this repository to your GitHub account.
2. Log in to the [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprint**.
4. Connect your GreenQuest repository.
5. Render will detect `render.yaml` and provision both services on the Free Plan.
6. *(Optional)*: To enable hosted AI generation on the deployed backend, navigate to `greenquest-api` -> **Environment** and set `MODEL_PROVIDER=hosted`, `HOSTED_API_KEY=<your_key>`, and `FORCE_FALLBACK=false`.

---

## ⚠️ Known Limitations & Resource Profile

- **CPU Latency with Gemma 3 1B**: On an average developer laptop (16 GB RAM, integrated graphics), local inference via Ollama takes ~20–25 seconds per mission. The frontend includes a responsive 35s timeout and loading indicator before triggering fallback.
- **Hardware Profile**: Tested and verified on Ubuntu Linux with 16 GB RAM and integrated graphics. Gemma 3 1B requires ~1.5 GB memory overhead in Ollama. Gemma 3 4B is optional and only recommended on machines with dedicated VRAM.
- **Offline Client Generation**: When entirely offline or disconnected from the backend, the PWA utilizes deterministic procedural templates tailored to your environment and mood, rather than running heavyweight in-browser WebGPU model weights.

---

## 📋 Hacktoberfest 2026 Checklist & Roadmap

- [x] Architecture design and API contracts (`docs/ARCHITECTURE.md`)
- [x] Deterministic safety guardrail engine (`backend/app/orchestrator/rules.py`)
- [x] Model-provider abstraction layer (`backend/app/providers/`)
- [x] Ollama integration for Gemma 3 1B with grammar constraints and JSON repair
- [x] Dual-layer deterministic fallback engine (backend + frontend in-browser)
- [x] State machine orchestrator with typed agents and bounded retries
- [x] Mobile-first React PWA with earth-toned design tokens
- [x] Step checklist with local storage persistence
- [x] Service worker offline asset caching (`sw.js`)
- [x] Comprehensive automated test suite (31 tests passing)
- [x] GitHub Actions automated CI (`.github/workflows/test.yml`)
- [x] MIT Open-Source License and full pre-release security/path audit
- [ ] *Next Task*: Real-world outdoor field testing with mobile devices and optional Gemma 3 4B latency benchmarking.

---

## 📄 License
[MIT License](LICENSE). Built with care for Hacktoberfest 2026 Open-Source AI Challenge.

