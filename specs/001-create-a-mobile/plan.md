
# Implementation Plan: FitFusion AI Workout App

**Branch**: `001-create-a-mobile` | **Date**: 2025-09-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-create-a-mobile/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
FitFusion is an AI-powered mobile-first PWA that generates personalized workout programs using CrewAI multi-agent orchestration. Users manage equipment inventory, receive tailored workout plans from specialized AI agents (Coach, Nutritionist, Equipment Advisor, etc.), and execute workouts with guided timers and progress tracking. The app features offline-first architecture with Next.js frontend and Python FastAPI backend using Gemini Flash 2.5 for AI generation.

## Technical Context
**Language/Version**: Python 3.10-3.13 (backend), TypeScript/JavaScript (frontend)  
**Primary Dependencies**: FastAPI, CrewAI, Next.js 14, Supabase, Gemini 2.5 Flash API, Tailwind CSS, shadcn/ui, Dexie.js, @ducanh2912/next-pwa  
**Storage**: Supabase PostgreSQL (persistent), IndexedDB/LocalForage (offline caching)  
**Testing**: pytest (backend), Playwright (frontend e2e), Jest (frontend unit)  
**Target Platform**: Android PWA (installable), Web browsers (mobile-first)
**Project Type**: web - determines frontend+backend structure  
**Performance Goals**: <200ms p95 API latency, 60fps UI animations, <200KB initial JS bundle  
**Constraints**: Offline-first capability, PWA installable, real-time sync, AI generation <30s  
**Scale/Scope**: Personal use (single user), ~15 core screens, 8 specialized AI agents, 6 data entities

**Architecture Details**: Full-stack application with Next.js frontend and Python FastAPI backend
- **Frontend**: Next.js (App Router), React 18, Tailwind CSS, shadcn/ui, Framer Motion, Zustand, IndexedDB
- **Backend**: FastAPI on Huggingface Spaces (FREE), CrewAI framework, Pydantic models, CORS middleware  
- **AI Integration**: CrewAI multi-agent system with Gemini 2.5 Flash (8 agents: Strength Coach, Cardio Coach, Nutritionist, Equipment Advisor, Recovery Specialist, Motivation Coach, Analytics Expert, Preferences Manager)
- **Database**: Supabase PostgreSQL with real-time subscriptions
- **Deployment**: Vercel (frontend - FREE), Huggingface Spaces (backend - FREE), Supabase (database - FREE tier 500MB)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Code Quality & Maintainability**: ✅ PASS
- ESLint/Prettier configured for frontend, Flake8/Black for backend
- TypeScript for frontend ensures no compiler warnings
- Public API interfaces will be documented with Pydantic models and OpenAPI
- Peer review required for all changes

**Testing Discipline & Coverage**: ✅ PASS  
- TDD approach: contract tests before implementation
- Test pyramid: Jest unit → Playwright e2e → pytest API integration
- Coverage targets: ≥85% overall, ≥90% changed lines
- Contract tests for all FastAPI endpoints

**UX Consistency & Accessibility**: ✅ PASS
- shadcn/ui design system with Tailwind tokens ensures consistency
- WCAG 2.1 AA compliance through semantic markup and ARIA
- Mobile-first PWA with consistent navigation patterns
- Performance budgets for 200ms+ operations (AI generation loading states)

**Performance Targets & Budgets**: ✅ PASS
- Backend: p95 < 200ms, p99 < 500ms API latency
- Frontend: ≤200KB initial bundle, 60fps animations with Framer Motion
- Database: Supabase indexes for all query paths, no N+1 with proper relations
- AI generation timeouts with queuing fallback

**Security & Privacy**: ✅ PASS
- API keys in environment variables, no plaintext secrets
- Supabase RLS policies for data access control
- Dependency scanning via automated tools

**Observability**: ✅ PASS
- Structured logging in FastAPI backend
- Performance monitoring for AI agent workflows
- Error tracking for offline/online sync failures

**No constitutional violations detected - Ready for Phase 0**

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Option 2 (Web application) - Frontend/Backend separation required for PWA + FastAPI architecture

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType windsurf`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- **Database & Sync Tasks (5-7)**: Supabase schema, RLS policies, offline sync implementation
- **AI Integration Tasks (6-8)**: CrewAI agents, Gemini API integration, agent orchestration
- **Core Components Tasks (8-10)**: React components, Zustand state, API clients
- **PWA Features Tasks (4-6)**: Service workers, offline caching, installation prompts
- **Testing & Quality Tasks (6-8)**: Contract tests, e2e tests, performance validation

**Ordering Strategy**:
- **Foundation First**: Database schema → API contracts → Core models
- **TDD Approach**: Contract tests before implementation
- **Dependency Order**: Backend APIs → Frontend services → UI components
- **Parallel Execution**: Mark independent tasks [P] for concurrent development

**Task Categories Breakdown**:
1. **Database & Sync (5-7 tasks)**:
   - Supabase PostgreSQL schema creation
   - Row Level Security (RLS) policies
   - Real-time subscription setup
   - IndexedDB offline cache implementation
   - Sync conflict resolution logic

2. **AI Integration (6-8 tasks)**:
   - CrewAI agent framework setup
   - 8 specialized AI agents (Coach, Nutritionist, Equipment Advisor, etc.)
   - Gemini Flash 2.5 API integration
   - Agent orchestration workflows
   - Error handling and retry logic
   - Progress reporting for long-running generations

3. **Core Components (8-10 tasks)**:
   - Next.js 14 App Router setup
   - shadcn/ui design system integration
   - Zustand state management
   - API client with offline support
   - Core React components (WorkoutCard, ExerciseModal, etc.)
   - Framer Motion animations

4. **PWA Features (4-6 tasks)**:
   - Service worker configuration
   - PWA manifest and installation
   - Offline-first caching strategy
   - Background sync implementation

5. **Testing & Quality (6-8 tasks)**:
   - pytest backend contract tests
   - Playwright frontend e2e tests
   - Jest unit tests
   - Performance budgets validation
   - Accessibility compliance testing

**Estimated Output**: 35-45 numbered, ordered tasks in tasks.md following TDD principles

**Realistic Timeline**: 3-4 weeks for full implementation with hybrid architecture

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.2.0 - See `.specify/memory/constitution.md`*
