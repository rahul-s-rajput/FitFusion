# Remaining Implementation Plan

Purpose: carry the new mobile-first workout experience across every core screen, consolidate navigation around the profile hub, and polish supporting flows so they match the redesigned saved workouts journey. Each task below notes the target files and follow-up checks to complete that alignment.

## Execution Plan
- Inventory remaining UX gaps across profile, equipment, and settings flows, then prioritise screens that block the mobile-first navigation story.
- Deliver profile-centric surfaces first (dashboard polish, analytics cleanup, achievements, history) to ensure `/profile` acts as the new hub before extending auxiliary routes.
- Layer in equipment maintenance and new settings deep-dives next so every quick action has a destination and reuse shared hero/section patterns for coherence.
- Close with a consistency sweep (route audits, import hygiene, inline comments) and run linting, capturing any follow-up QA notes in this document.

## Profile Hub & Navigation
- [x] Finalise `src/app/profile/page.tsx` as the central user dashboard; review data hooks to ensure it reads from `useUser`, `useProgress`, `useWorkout`, and `useEquipment` without redundant calculations.
- [x] Audit CTA links (buttons, quick actions) so they route to `/profile/progress`, `/profile/achievements`, `/settings`, and `/workouts/saved`; update `MobileBottomNav` and any components still hardcoding `/progress`.
- [x] Keep `/progress/page.tsx` exporting the relocated profile analytics screen for backward compatibility; smoke-test navigation from home -> profile -> progress to ensure shared hero and layout stay consistent on mobile.

## Profile Sub-screens
- [x] Clean the migrated analytics page at `src/app/profile/progress/page.tsx`; swap `setCurrentPage('progress')` for `'profile'`, tighten mock data typing, and remove stale imports.
- [x] Design new `/profile/achievements/page.tsx` showcasing badge history and streak commentary (reuse `PageHero`, `SectionHeader`, `QuickStatCard`); source data from `progress.achievements` with fallback copy.
- [x] Sketch `/profile/history/page.tsx` (timeline of sessions or PRs). Plan to reuse `Card` lists with timeline styling and add filters referencing the same `useProgressActions` store slice.

## Equipment Extensions
- [x] Add `/equipment/maintenance/page.tsx` detailing condition, service intervals, and reminders. Pull inventory from `useEquipment`, aggregate by `item.condition`, and reuse gradient hero for context.
- [x] Ensure `src/app/equipment/page.tsx` quick-actions navigate to both `suggestions` and new `maintenance` screens; remove any unused icon imports after adjustments.

## Settings Deep-Dives
- [x] Carve out `/settings/notifications/page.tsx` and `/settings/privacy/page.tsx` using shared hero plus panels. Move switch-and-toggle logic into small helper components if repetition grows.
- [x] Update call-to-action buttons in the main settings hub (e.g., "View guides") to open the new sub-screens where appropriate, keeping copy aligned with their focus.

## Consistency & Polish
- [x] Search the codebase for `'/progress'` strings to confirm only API routes remain; replace stray instances with `/profile` routes.
- [x] Trim unused icons/imports introduced during refactors (e.g., in `home`, `generate`, `equipment`). Run `rg` to spot zero-usage symbols before linting.
- [x] Add concise comments where logic is non-obvious (e.g., readiness score blending streak and program completion) without over-commenting.

## Validation & QA
- [x] Execute `npm run lint` once refactors land; document any pre-existing rule violations separately from new warnings.
- [ ] Manual QA checklist: `/`, `/generate`, `/profile`, `/profile/progress`, `/equipment`, `/equipment/maintenance`, `/settings`, `/settings/notifications`. Confirm bottom nav state, hero animations, and responsive stacking on a 390px width viewport.
- [x] Note open follow-ups in this doc after each milestone so we can iterate or create tickets as needed.

### Follow-ups
- Manual responsive QA still outstanding; schedule a device pass to confirm the new sub-screens animate smoothly at 390px width.
