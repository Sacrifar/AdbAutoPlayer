# Frontend (SvelteKit + TypeScript)

- `src/lib/form/` — Dynamic JSON Schema form renderer; game settings are rendered entirely from Pydantic model schemas, not hardcoded components. A settings change usually needs no frontend edit — change the Pydantic model instead.
- `src/lib/stores.svelte.ts` — Global Svelte stores for app state (selected game, profile, running task, logs).
- `src/client/` — Auto-generated TypeScript client from PyTauri IPC definitions. **Never edit manually**; changes to Python IPC models regenerate it.
- SvelteKit is configured as a static SPA (no SSR); all routing is client-side for Tauri compatibility.
- Frontend listens for `log-message`, `task-completed` and `all-tasks-completed` events emitted from Python.

Checks: `pnpm check` (svelte-check + TS) and `pnpm prettier-write` from the repo root.
