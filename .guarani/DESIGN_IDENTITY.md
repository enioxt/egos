# EGOS Design Identity — Unified Visual System

**Sacred Code:** 000.111.369.963.1618
**Version:** 1.0.0 | **Updated:** 2026-03-06
**Applies to:** ALL EGOS surfaces (egos.ia.br, inteligencia.egos.ia.br, Hacash Explorer, etc.)

---

## Philosophy

> **"Police Intelligence meets Open Source."**
> Dark-first. Data-dense. Glassmorphism. Inspired by Palantir, Linear, and mempool.space.
> Every pixel serves a purpose. No decoration without function.

---

## Typography

| Role | Font | Weight | Fallback |
|------|------|--------|----------|
| **Primary** | Space Grotesk | 300-700 | system-ui, sans-serif |
| **Monospace** | JetBrains Mono | 400-600 | monospace |
| **Import** | `@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap')` | | |

| Use | Size | Weight | Color |
|-----|------|--------|-------|
| Page title (h1) | 28-32px | 700 | `#f1f5f9` |
| Section heading (h2) | 20-24px | 600 | `#f1f5f9` |
| Subsection (h3) | 16-18px | 600 | `#e2e8f0` |
| Body text | 14-15px | 400 | `rgba(255,255,255,0.87)` |
| Caption/label | 12-13px | 500 | `#94a3b8` |
| Muted/dim | 11-12px | 400 | `#64748b` |
| Monospace data | 11-13px | 400 | `#13b6ec` |

---

## Color Palette

### Core (from `branding/colors.json`)

| Token | Hex | Usage |
|-------|-----|-------|
| `background` | `#050508` | Page background, app shell |
| `surface` | `rgba(255,255,255,0.03)` | Card backgrounds, sections |
| `border` | `rgba(255,255,255,0.06)` | Card borders, dividers |
| `primary` | `#13b6ec` | Links, CTAs, accent elements, active states |
| `primary-hover` | `#0e9fd1` | Link/button hover |
| `secondary` | `#a855f7` | Tags, badges, secondary accents |
| `success` | `#22c55e` | Positive indicators, online status |
| `danger` | `#ef4444` | Errors, deletions, critical alerts |
| `warning` | `#f59e0b` | Warnings, pending states |
| `info` | `#3b82f6` | Informational badges |

### Text Hierarchy

| Token | Value | Usage |
|-------|-------|-------|
| `text-primary` | `#f1f5f9` | Headings, important text |
| `text-body` | `rgba(255,255,255,0.87)` | Body text |
| `text-secondary` | `#94a3b8` | Labels, descriptions |
| `text-muted` | `#64748b` | Timestamps, metadata |
| `text-dim` | `#475569` | Disabled, placeholder |

### Surface Opacity Scale

| Level | Value | Usage |
|-------|-------|-------|
| Hover | `rgba(255,255,255,0.04)` | Hover backgrounds |
| Active | `rgba(255,255,255,0.06)` | Active/selected items |
| Elevated | `rgba(255,255,255,0.08)` | Elevated surfaces, popovers |
| Border subtle | `rgba(255,255,255,0.06)` | Card borders |
| Border medium | `rgba(255,255,255,0.12)` | Input borders |
| Border strong | `rgba(255,255,255,0.20)` | Focus borders |

---

## Glassmorphism

```css
/* Standard card */
background: rgba(255, 255, 255, 0.03);
border: 1px solid rgba(255, 255, 255, 0.06);
border-radius: 12px;
backdrop-filter: blur(12px);

/* Elevated card (modals, popovers) */
background: rgba(5, 5, 8, 0.85);
border: 1px solid rgba(255, 255, 255, 0.12);
backdrop-filter: blur(20px);

/* Top bar / sticky elements */
background: rgba(5, 5, 8, 0.85);
backdrop-filter: blur(12px);
border-bottom: 1px solid rgba(255, 255, 255, 0.04);
```

---

## Spacing (4pt Grid)

| Use | Value | CSS |
|-----|-------|-----|
| Tight gap | 4px | `gap-1` |
| Default gap | 8px | `gap-2` |
| Section gap | 16px | `gap-4` |
| Container padding | 24-32px | `p-6` / `p-8` |
| Section margin | 32-48px | `my-8` / `my-12` |
| Border radius (small) | 8px | `rounded-lg` |
| Border radius (medium) | 12px | `rounded-xl` |
| Border radius (large) | 16px | `rounded-2xl` |

**RULE:** Never use magic numbers. Use 4pt grid increments.

---

## Components

### Buttons

```css
/* Primary CTA */
background: #13b6ec;
color: #050508;
font-weight: 600;
border-radius: 8px;
padding: 10px 20px;

/* Ghost/Secondary */
background: transparent;
border: 1px solid rgba(255,255,255,0.12);
color: rgba(255,255,255,0.7);

/* Hover: lighten by 0.04 alpha */
```

### Cards

```css
background: rgba(255,255,255,0.03);
border: 1px solid rgba(255,255,255,0.06);
border-radius: 12px;
padding: 20px;
/* Hover: border-color rgba(255,255,255,0.12) */
```

### Gradient Accents

```css
/* Hero text gradient */
background: linear-gradient(135deg, #ffffff 30%, #13b6ec 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;

/* Glow effect (subtle) */
box-shadow: 0 0 40px rgba(19, 182, 236, 0.08);
```

---

## Accessibility

- **Contrast:** All text meets WCAG AA on `#050508` background
- **Libras:** VLibras widget included on public surfaces
- **Focus rings:** `outline: 2px solid #13b6ec; outline-offset: 2px`
- **Min hit area:** 40x40px (Fitts's Law)
- **Reduced motion:** Respect `prefers-reduced-motion`

---

## Anti-Patterns

- NO light mode (dark only)
- NO magic pixel values (use 4pt grid)
- NO inline colors outside the palette
- NO decorative elements without function
- NO fonts other than Space Grotesk + JetBrains Mono
- NO border-radius > 16px (keeps enterprise feel)

---

## Migration Checklist (Intelink → EGOS Identity)

When migrating inteligencia.egos.ia.br to this identity:

- [ ] Replace slate-950/900/800 backgrounds with `#050508` + glass surfaces
- [ ] Replace blue-600 primary with `#13b6ec` (cyan)
- [ ] Add Space Grotesk import (currently uses system fonts)
- [ ] Apply glassmorphism to cards (backdrop-filter)
- [ ] Update gradient accents to cyan/white
- [ ] Ensure VLibras widget is present
- [ ] Verify WCAG AA contrast ratios

---

*"Consistency breeds trust. Every surface speaks the same language."*
