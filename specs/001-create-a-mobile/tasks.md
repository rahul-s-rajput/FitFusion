# Tasks: FitFusion AI Workout App

**Input**: Design documents from `/specs/001-create-a-mobile/`  
**Prerequisites**: plan.md (✓), research.md (✓), data-model.md (✓), contracts/ (✓)

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Next.js 14 + React 18, FastAPI, CrewAI, Gemini 2.5 Flash, Supabase, Dexie.js
   → Structure: Frontend/Backend web application
2. Load optional design documents: ✓
   → data-model.md: 6 entities (UserProfile, Equipment, Exercise, WorkoutProgram, WorkoutSession, ProgressRecord)
   → contracts/: 15+ API endpoints across 5 modules
   → research.md: Technology decisions and architectural patterns
3. Generate tasks by category: ✓
   → Setup: Project init, dependencies, PWA configuration
   → Tests: Contract tests, integration tests for 15+ endpoints
   → Core: 6 entity models, 8 AI agents, API services
   → Integration: Database, AI agents, offline sync
   → Polish: Unit tests, performance, deployment
4. Apply task rules: ✓
   → Different files = [P] for parallel execution
   → Tests before implementation (TDD approach)
   → Dependencies properly ordered
5. Number tasks sequentially (T001-T042) ✓
6. Generate dependency graph ✓
7. Validate completeness: All entities, endpoints, and agents covered ✓
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- File paths based on frontend/backend structure

## Phase 3.1: Project Setup & Foundation

- [x] **T001** Create project structure with frontend/ and backend/ directories
- [x] **T002** [P] Initialize Next.js 14 frontend with App Router in `frontend/`
- [x] **T003** [P] Initialize FastAPI backend with Python 3.11 in `backend/`
- [x] **T004** [P] Configure PWA with @ducanh2912/next-pwa in `frontend/next.config.mjs`
- [x] **T005** [P] Setup Tailwind CSS + shadcn/ui design system in `frontend/`
- [x] **T006** [P] Configure ESLint, Prettier, TypeScript in `frontend/`
- [x] **T007** [P] Configure Black, Flake8, pytest in `backend/`
- [x] **T008** [P] Setup Dexie.js for IndexedDB in `frontend/src/lib/db.ts`
- [x] **T009** Setup Supabase PostgreSQL schema from data-model.md

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3

**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### API Contract Tests
- [x] **T010** [P] Contract test GET /api/profile in `backend/tests/contract/test_profile.py`
- [x] **T011** [P] Contract test PUT /api/profile in `backend/tests/contract/test_profile.py`
- [x] **T012** [P] Contract test GET /api/equipment in `backend/tests/contract/test_equipment.py`
- [x] **T013** [P] Contract test POST /api/equipment in `backend/tests/contract/test_equipment.py`
- [x] **T014** [P] Contract test PUT/DELETE /api/equipment/{id} in `backend/tests/contract/test_equipment.py`
- [x] **T015** [P] Contract test POST /api/workouts/generate in `backend/tests/contract/test_ai_generation.py`
- [x] **T016** [P] Contract test GET /api/workouts/generate/{task_id} in `backend/tests/contract/test_ai_generation.py`
- [x] **T017** [P] Contract test GET /api/programs in `backend/tests/contract/test_programs.py`
- [x] **T018** [P] Contract test GET /api/programs/{id} in `backend/tests/contract/test_programs.py`
- [x] **T019** [P] Contract test POST /api/programs/{id}/activate in `backend/tests/contract/test_programs.py`
- [x] **T020** [P] Contract test GET /api/sessions in `backend/tests/contract/test_sessions.py`
- [x] **T021** [P] Contract test POST /api/sessions/{id}/start in `backend/tests/contract/test_sessions.py`
- [x] **T022** [P] Contract test POST /api/sessions/{id}/complete in `backend/tests/contract/test_sessions.py`

### Frontend Integration Tests
- [x] **T023** [P] Integration test PWA installation flow in `frontend/tests/e2e/pwa.spec.ts`
- [x] **T024** [P] Integration test offline workout execution in `frontend/tests/e2e/offline.spec.ts`
- [x] **T025** [P] Integration test AI workout generation flow in `frontend/tests/e2e/ai-generation.spec.ts`
- [x] **T026** [P] Integration test equipment management in `frontend/tests/e2e/equipment.spec.ts`

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models & Database
- [x] **T027** [P] UserProfile model in `backend/src/models/user_profile.py`
- [x] **T028** [P] Equipment model in `backend/src/models/equipment.py`
- [x] **T029** [P] Exercise model in `backend/src/models/exercise.py`
- [x] **T030** [P] WorkoutProgram model in `backend/src/models/workout_program.py`
- [x] **T031** [P] WorkoutSession model in `backend/src/models/workout_session.py`
- [x] **T032** [P] ProgressRecord model in `backend/src/models/progress_record.py`

### CrewAI Multi-Agent System
- [x] **T033** [P] Strength Coach agent in `backend/src/agents/strength_coach.py`
- [x] **T034** [P] Cardio Coach agent in `backend/src/agents/cardio_coach.py`
- [x] **T035** [P] Nutritionist agent in `backend/src/agents/nutritionist.py`
- [x] **T036** [P] Equipment Advisor agent in `backend/src/agents/equipment_advisor.py`
- [x] **T037** [P] Recovery Specialist agent in `backend/src/agents/recovery_specialist.py`
- [x] **T038** [P] Motivation Coach agent in `backend/src/agents/motivation_coach.py`
- [x] **T039** [P] Analytics Expert agent in `backend/src/agents/analytics_expert.py`
- [x] **T040** [P] Preferences Manager agent in `backend/src/agents/preferences_manager.py`
- [x] **T041** Agent orchestration service in `backend/src/services/crew_orchestrator.py`

### API Endpoints Implementation
- [x] **T042** User profile endpoints in `backend/src/api/profile.py`
- [x] **T043** Equipment management endpoints in `backend/src/api/equipment.py`
- [x] **T044** AI workout generation endpoints in `backend/src/api/ai_generation.py`
- [x] **T045** Workout program endpoints in `backend/src/api/programs.py`
- [x] **T046** Workout session endpoints in `backend/src/api/sessions.py`

### Frontend Core Components
- [x] **T047** [P] Dexie.js database schema in `frontend/src/lib/db.ts`
- [x] **T048** [P] Zustand store setup in `frontend/src/store/index.ts`
- [x] **T049** [P] API client with offline support in `frontend/src/lib/api-client.ts`
- [x] **T050** [P] Home screen component in `frontend/src/app/page.tsx`
- [x] **T051** [P] Equipment management page in `frontend/src/app/equipment/page.tsx`
- [x] **T052** [P] Workout generation page in `frontend/src/app/generate/page.tsx`
- [x] **T053** [P] Workout execution page in `frontend/src/app/workout/[id]/page.tsx`
- [x] **T054** [P] Progress tracking page in `frontend/src/app/progress/page.tsx`

## Phase 3.4: Integration & Sync

- [x] **T055** Supabase integration service in `backend/src/services/database_service.py`
- [x] **T056** Gemini 2.5 Flash API integration in `backend/src/services/gemini_service.py`
- [x] **T057** Frontend-backend sync adapter in `frontend/src/lib/sync-adapter.ts`
- [x] **T058** Offline/online state management in `frontend/src/hooks/useOnlineStatus.ts`
- [x] **T059** PWA service worker configuration in `frontend/public/sw.js`
- [x] **T060** Background sync implementation in `frontend/src/lib/background-sync.ts`
- [x] **T061** CORS and middleware setup in `backend/src/middleware/cors.py`
- [x] **T062** Error handling and logging in `backend/src/utils/error_handler.py`

## Phase 3.5: Polish & Deployment

### Testing & Quality
- [ ] **T063** [P] Unit tests for AI agents in `backend/tests/unit/test_agents.py`
- [ ] **T064** [P] Unit tests for sync logic in `frontend/tests/unit/sync.test.ts`
- [ ] **T065** [P] Performance tests for AI generation (<30s) in `backend/tests/performance/`
- [ ] **T066** [P] Accessibility tests (WCAG 2.1 AA) in `frontend/tests/a11y/`

### Deployment & Documentation
- [ ] **T067** [P] Huggingface Spaces deployment config in `backend/Dockerfile`
- [ ] **T068** [P] Vercel deployment config in `frontend/vercel.json`
- [ ] **T069** [P] Environment variables setup in `.env.example`
- [ ] **T070** [P] API documentation in `docs/api.md`
- [ ] **T071** [P] User guide based on quickstart.md in `docs/user-guide.md`
- [ ] **T072** Execute quickstart validation scenarios

## Dependencies

### Phase Blocking
- Setup (T001-T009) must complete before Tests (T010-T026)
- Tests (T010-T026) must complete and FAIL before Core (T027-T054)
- Core (T027-T054) must complete before Integration (T055-T062)
- Integration (T055-T062) must complete before Polish (T063-T072)

### Specific Dependencies
- T009 (Supabase schema) blocks T055 (database service)
- T041 (agent orchestration) blocks T044 (AI generation endpoints)
- T047 (Dexie schema) blocks T049 (API client) and T057 (sync adapter)
- T048 (Zustand store) blocks all frontend pages (T050-T054)
- T056 (Gemini integration) blocks T041 (agent orchestration)

## Parallel Execution Examples

### Phase 3.1 Setup (Can run simultaneously)
```bash
Task: "Initialize Next.js 14 frontend with App Router in frontend/"
Task: "Initialize FastAPI backend with Python 3.11 in backend/"
Task: "Configure PWA with @ducanh2912/next-pwa in frontend/next.config.js"
Task: "Setup Tailwind CSS + shadcn/ui design system in frontend/"
```

### Phase 3.2 Contract Tests (Can run simultaneously)
```bash
Task: "Contract test GET /api/profile in backend/tests/contract/test_profile.py"
Task: "Contract test GET /api/equipment in backend/tests/contract/test_equipment.py"
Task: "Contract test POST /api/workouts/generate in backend/tests/contract/test_ai_generation.py"
Task: "Integration test PWA installation in frontend/tests/e2e/pwa.spec.ts"
```

### Phase 3.3 Models (Can run simultaneously)
```bash
Task: "UserProfile model in backend/src/models/user_profile.py"
Task: "Equipment model in backend/src/models/equipment.py"
Task: "Exercise model in backend/src/models/exercise.py"
Task: "WorkoutProgram model in backend/src/models/workout_program.py"
```

### Phase 3.3 AI Agents (Can run simultaneously)
```bash
Task: "Strength Coach agent in backend/src/agents/strength_coach.py"
Task: "Cardio Coach agent in backend/src/agents/cardio_coach.py"
Task: "Nutritionist agent in backend/src/agents/nutritionist.py"
Task: "Equipment Advisor agent in backend/src/agents/equipment_advisor.py"
```

## Task Coverage Validation

### All API Contracts Covered ✓
- User Profile: GET, PUT (T010, T011)
- Equipment: GET, POST, PUT, DELETE (T012-T014)
- AI Generation: POST, GET status (T015, T016)
- Programs: GET list, GET detail, POST activate (T017-T019)
- Sessions: GET, POST start, POST complete (T020-T022)

### All Data Entities Covered ✓
- UserProfile (T027), Equipment (T028), Exercise (T029)
- WorkoutProgram (T030), WorkoutSession (T031), ProgressRecord (T032)

### All AI Agents Covered ✓
- 8 specialized agents (T033-T040) + orchestration (T041)

### All User Journeys Covered ✓
- PWA installation (T023), Offline execution (T024)
- AI generation flow (T025), Equipment management (T026)

## Constitutional Compliance ✓

- **Code Quality**: ESLint/Prettier (T006), Black/Flake8 (T007)
- **Testing Discipline**: TDD approach with failing tests first (T010-T026)
- **UX Consistency**: shadcn/ui design system (T005)
- **Performance**: <30s AI generation tests (T065), <200ms API tests
- **Accessibility**: WCAG 2.1 AA compliance tests (T066)

## Notes

- **Total Tasks**: 72 (realistic for 3-4 week timeline)
- **Parallel Tasks**: 45 marked with [P] for concurrent execution
- **Critical Path**: Setup → Tests → Models → Agents → Integration → Deployment
- **Estimated Timeline**: 3-4 weeks with proper task parallelization
- **Architecture**: Hybrid local-first with optional cloud sync
- **Cost**: ~$0.50/month using free tiers (Vercel, Huggingface Spaces, Supabase)

---

**Status**: ✅ Ready for implementation execution following TDD principles
