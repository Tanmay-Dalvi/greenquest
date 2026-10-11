# GreenQuest Hacktoberfest 2026 Implementation Checklist
*Deadline: October 11, 2026, 11:59 PM PDT (October 12, 2026, 12:29 PM IST)*

---

## Phase 1: Environment & Foundations [COMPLETED / IN PROGRESS]
- [x] Environment inspection (OS, Python 3.14, Node v24, pip, git, Ollama check)
- [x] Initialize Git repository with main branch
- [x] Architecture design document (`docs/ARCHITECTURE.md`)
- [x] Project checklist (`docs/CHECKLIST.md`)
- [x] Core dependencies defined (`requirements.txt`, `package.json`)
- [x] Environment configuration template (`.env.example`)
- [x] Version control rules (`.gitignore`)
- [x] Render deployment blueprint (`render.yaml`)
- [x] GitHub Actions automated CI testing (`.github/workflows/test.yml`)

## Phase 2: Backend Architecture & Vertical Slice [IN PROGRESS]
- [ ] Pydantic Schemas (`backend/app/models/mission.py`)
  - [ ] Preference request schema
  - [ ] Micro-adventure mission response schema
  - [ ] Step checklist schema
  - [ ] Generator metadata schema
- [ ] Model Provider Layer (`backend/app/providers/`)
  - [ ] `ModelProvider` abstract base class (`base.py`)
  - [ ] `OllamaProvider` with Gemma 3 1B client & timeouts (`ollama.py`)
  - [ ] `HostedProvider` optional adapter (`hosted.py`)
  - [ ] `DeterministicFallbackProvider` for offline & unreachable models (`fallback.py`)
- [ ] Orchestrator State Machine (`backend/app/orchestrator/`)
  - [ ] Execution state & observability log (`state.py`)
  - [ ] Deterministic safety rules (`rules.py`)
  - [ ] Planner agent (`agents/planner.py`)
  - [ ] Nature activity agent (`agents/nature_activity.py`)
  - [ ] Safety validator agent (`agents/safety.py`)
  - [ ] State machine controller with bounded retries (`machine.py`)
- [ ] FastAPI Endpoints (`backend/app/api/routes.py`, `backend/app/main.py`)
  - [ ] `POST /api/missions/generate`
  - [ ] `GET /api/health`
  - [ ] `GET /api/providers`
- [ ] Automated Backend Test Suite (`backend/tests/`)
  - [ ] `test_schemas.py`
  - [ ] `test_safety_rules.py`
  - [ ] `test_providers.py`
  - [ ] `test_orchestrator.py`
  - [ ] `test_api.py`

## Phase 3: Mobile-First Frontend Vertical Slice [PENDING]
- [ ] Setup Vite + React + TypeScript + Tailwind CSS
- [ ] Outdoor color palette: Forest green, warm cream, muted sage, restrained amber
- [ ] Tactile preference selector (Environment, Duration, Mood, Energy, Senses)
- [ ] Mission display card with sensory prompt & leave-no-trace notice
- [ ] Interactive step checklist with instant checkbox toggle
- [ ] Local persistence (IndexedDB / LocalStorage) for offline missions & checklist state
- [ ] PWA web app manifest (`manifest.json`) and service worker (`sw.js`)
- [ ] Offline indicator & fallback generator integration
- [ ] History drawer to view past saved explorations

## Phase 4: Verification, Polish & Documentation [PENDING]
- [ ] Run full test suite (`pytest`)
- [ ] Build and test frontend (`npm run build`)
- [ ] Verify vertical slice end-to-end
- [ ] Update `README.md` with setup instructions, screenshots/demos, and run commands
- [ ] Commit changes with clear Git history

