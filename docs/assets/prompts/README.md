# Asset Source Records

Every brand visual asset must have a reproducible source committed here.

## Why

The 2026-04-06 hero-shield.jpg failure (AI model rendered "1200x800px", "#10B981", "#0F172A" as visible text inside the artwork) happened because the prompt was not version-controlled and mixed scene description with technical parameters. See `~/.claude/commands/image-prompt.md` for the full prompting protocol that prevents this.

## Generation Methods

| Asset | Method | Source File | Output |
|-------|--------|-------------|--------|
| `guard-brasil-web/public/hero-shield.png` | HTML+Playwright | `scripts/assets/guard-hero.html` | 1000×700 PNG |
| `guard-brasil-web/public/og-image.png` | HTML+Playwright | `scripts/assets/guard-og.html` | 1200×630 PNG |
| `egos-hq/public/og-image.png` | HTML+Playwright | `scripts/assets/hq-og.html` | 1200×630 PNG |
| `guard-brasil-web/app/icon.svg` | Hand-written SVG | inline | scalable |
| `egos-hq/app/icon.svg` | Hand-written SVG | inline | scalable |

## Regenerating

```bash
cd /home/enio/egos/scripts/assets
python3 -m http.server 9981 &
# In Playwright (or any headless browser):
# 1. resize viewport to the target dimensions
# 2. navigate to http://localhost:9981/<file>.html
# 3. wait 2s for fonts to load
# 4. screenshot at exact dimensions
```

Brand tokens come from `docs/PRESENTATION_VISUAL_IDENTITY.md` (canonical SSOT).
Never invent colors. Never put hex values inside AI prompts.

## Why HTML+Playwright instead of AI generation

- Deterministic, version-controllable source (the HTML is the truth)
- Real fonts via Google Fonts (Inter, JetBrains Mono)
- Pixel-perfect typography and exact brand colors
- Zero risk of baked-in spec text, no AI hallucinations
- Editable in seconds (change one CSS variable)
- Free, no API cost, no rate limits

Use AI image generation only for: abstract textures, atmospheric backgrounds, illustration where typography and exact geometry don't matter.
