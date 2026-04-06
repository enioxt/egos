# Guard Brasil Sandbox

> Reference implementation of the EGOS Auditable Live Sandbox pattern.
> Pattern SSOT: `docs/patterns/AUDITABLE_SANDBOX_PATTERN.md`

**Route:** `/sandbox`
**Dataset:** `public/sandbox-dataset.json` (39KB, 20 scenarios)

## Adapting for other products

Copy `sandbox-client.tsx`, update:
1. `API_URL` and endpoint path
2. `SCENARIO_META` with product-specific inputs and categories
3. `CATEGORY_COLORS` / `CATEGORY_BADGE_COLORS`
4. `SANDBOX_PRESETS` for target vertical
5. `page.tsx` metadata (title, description)
6. Regenerate `sandbox-dataset.json` against the new API
