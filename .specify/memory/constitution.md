<!--
Sync Impact Report
- Version change: 2.1.1 → 2.2.0
- Modified principles: N/A (template placeholders replaced with concrete principles)
- Added principles:
  - Code Quality & Maintainability
  - Testing Discipline & Coverage
  - UX Consistency & Accessibility
  - Performance Targets & Budgets
- Added sections:
  - Additional Constraints & Standards
  - Development Workflow & Quality Gates
- Removed sections:
  - Placeholder Principle 5
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated to reference .specify/memory/constitution.md and Constitution v2.2.0)
  - .specify/templates/spec-template.md (✅ aligned; no constitution path references)
  - .specify/templates/tasks-template.md (✅ aligned; no constitution path references)
- Follow-up TODOs:
  - Set RATIFICATION_DATE (original adoption date) in YYYY-MM-DD.
-->

# FitFusion Constitution

## Core Principles

### Code Quality & Maintainability
- Code MUST be linted and formatted before merge. Configure and enforce formatters/linters in CI (e.g., ESLint/Prettier, Flake8/Black, etc. per tech stack).
- No new compiler/type/lint warnings are allowed on main. Warnings MUST be fixed or explicitly suppressed with rationale and scope.
- Cyclomatic complexity SHOULD remain ≤ 10 per function/method unless justified in the PR description with an alternative considered.
- Duplication MUST be eliminated proactively; if duplication is introduced to enable a refactor, it MUST be removed within the same PR or immediately following PR linked in the description.
- Public interfaces MUST be documented with usage examples or docstrings. Significant design decisions MUST include an ADR entry when applicable.
- All code changes REQUIRE at least one peer review approval. Self-approval is prohibited for non-trivial changes.
Rationale: High code quality reduces defect rate, speeds onboarding, and enables efficient refactoring.

### Testing Discipline & Coverage
- TDD is strongly encouraged: write failing tests before implementation. PRs MUST include tests for new behavior and bug fixes.
- Test pyramid MUST be respected: unit > integration > e2e. Contract tests are REQUIRED for public APIs.
- Minimum coverage thresholds (overall and changed lines) MUST be enforced by CI: overall ≥ 85%, changed lines ≥ 90%.
- Tests MUST be deterministic; flaky tests are disallowed. Any flake MUST be quarantined within 24 hours and resolved before the next release.
- CI MUST block merges if tests fail, coverage falls below thresholds, or tests are skipped without justification.
Rationale: Reliable tests provide safety nets enabling fast iteration.

### UX Consistency & Accessibility
- UI MUST adhere to a shared design system (components, spacing, typography, color tokens). Deviations require design review approval.
- Accessibility MUST meet WCAG 2.1 AA for supported platforms (semantic markup, contrast, focus order, keyboard nav, ARIA where appropriate).
- User-facing copy MUST be consistent in voice/tone; errors MUST be actionable and localized where i18n is supported.
- Navigation, layout patterns, and interaction states MUST be consistent across screens/pages.
- Performance aspects of UX (perceived latency, skeletons/spinners, progressive loading) MUST be addressed for operations exceeding 200ms.
Rationale: Consistency and accessibility improve user trust and task completion rates.

### Performance Targets & Budgets
- Each feature MUST define explicit performance budgets in plan.md (latency, memory, CPU, bundle size). Budgets MUST be tested in CI where feasible.
- Backend: p95 request latency < 200ms and p99 < 500ms under expected load unless otherwise specified in the plan.
- Frontend: initial route JS payload (gzipped) ≤ 200KB; subsequent route chunks ≤ 150KB; maintain 60 fps during typical interactions; images and heavy assets MUST be lazy-loaded.
- Database: queries MUST use appropriate indexes; no full table scans on hot paths; N+1 queries in hot paths are disallowed.
- Regressions beyond budgets MUST block merge or include a mitigation plan with tracking.
Rationale: Performance is a product feature and prevents scale-induced outages.

## Additional Constraints & Standards
- Security & Privacy: No plaintext secrets in the repo; dependency scanning at least monthly; PII must be minimized and access-controlled.
- Observability: Structured logs at INFO+ in production; traces/metrics for critical paths; error rates and latency SLIs MUST be visible on dashboards.
- Documentation: README and quickstart for new features; significant architecture decisions recorded as ADRs.

## Development Workflow & Quality Gates
- PR Gates (CI): format + lint + type-check + tests + coverage + a11y checks (for UI) + performance checks where available.
- No direct commits to main; all changes via PRs linked to tasks.
- Release Gates: zero critical/sev-1 defects open; no quarantined tests; performance/error budgets in compliance.

## Governance
Constitution supersedes other practices. All PRs and reviews MUST verify compliance with the principles and gates above.

Amendment Procedure:
- Propose a change via PR to this file with a Sync Impact Report.
- Classify version bump per Semantic Versioning for governance (below).
- Obtain approval from at least one technical lead and one design/QA representative when changes affect UX or testing.

Versioning Policy (for this constitution):
- MAJOR: Backward-incompatible governance changes or removal/redefinition of principles.
- MINOR: New principle/section added or materially expanded guidance. (This update)
- PATCH: Clarifications and non-semantic refinements.

Compliance Review:
- Periodic (at least quarterly) review of test coverage, a11y compliance, and performance dashboards.
- Violations MUST be tracked and remediated with explicit owners and due dates.

**Version**: 2.2.0 | **Ratified**: TODO | **Last Amended**: 2025-09-23
<!-- Previous: Version: 2.1.1 | Ratified: (unknown) | Last Amended: (unknown) -->