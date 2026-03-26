# EGOS Visual Identity & Brand Guidelines

> **Version:** 1.0.0 | **Updated:** 2026-03-26
> **Role:** Design system & brand expression for EGOS kernel and ecosystem

---

## Brand Essence

**Tagline:** "Governance is Infrastructure"

**Brand Character:** Data-driven authority + developer accessibility. We look like infrastructure should: clean, trustworthy, technical, no-nonsense.

**Personality:** Professional but human. We explain trade-offs. We show evidence. We're not selling snake oil.

---

## Color Palette

### Primary Colors (Authority & Trust)

| Name | Hex | RGB | Usage | Notes |
|------|-----|-----|-------|-------|
| **EGOS Black** | `#0A0E27` | 10, 14, 39 | Primary text, headers, dark mode background | Deep navy-black. Serious but not harsh. |
| **EGOS Navy** | `#1A2F5A` | 26, 47, 90 | Secondary backgrounds, cards, containers | Trust color. Enterprise-grade. |
| **EGOS Blue** | `#2563EB` | 37, 99, 235 | CTAs, links, highlights, active states | Governance-first energy. Clear action. |

### Secondary Colors (Trust & Evidence)

| Name | Hex | RGB | Usage | Notes |
|------|-----|-----|-------|-------|
| **Evidence Green** | `#10B981` | 16, 185, 145 | Success states, compliance passing, checkmarks | Rules followed. System healthy. |
| **Warning Amber** | `#F59E0B` | 245, 158, 11 | Drift detection, warnings, rule violations | "Pay attention." Not alarming, but clear. |
| **Danger Red** | `#EF4444` | 239, 68, 68 | Critical errors, governance blocks, failed rules | Only for actual failures (not general danger). |

### Neutral Colors (Readability & Structure)

| Name | Hex | RGB | Usage | Notes |
|------|-----|-----|-------|-------|
| **White (Primary)** | `#FFFFFF` | 255, 255, 255 | Light mode background | Clean, readable. |
| **Gray 50** | `#F9FAFB` | 249, 250, 251 | Light surfaces, alt backgrounds | Subtle contrast. |
| **Gray 200** | `#E5E7EB` | 229, 231, 235 | Borders, dividers, subtle separations | Doesn't distract. |
| **Gray 600** | `#4B5563` | 75, 85, 99 | Secondary text, muted labels | Readable but not primary. |
| **Gray 900** | `#111827` | 17, 24, 39 | Dark mode primary text | Accessible over all dark backgrounds. |

### Accent Colors (Data Visualization)

For charts, metrics, and evidence displays:

- **Data Blue** `#3B82F6` — Primary metrics
- **Data Purple** `#8B5CF6` — Secondary trends
- **Data Cyan** `#06B6D4` — Tertiary insights
- **Data Orange** `#F97316` — Anomalies/outliers
- **Data Pink** `#EC4899` — Alerts/highlights

---

## Typography

### Font Families

**Primary Font (Headers & UI):** Inter

- Weights: 400 (Regular), 500 (Medium), 600 (Semibold), 700 (Bold)
- Usage: Headlines, navigation, buttons, labels
- Rationale: Modern, neutral, excellent legibility at all sizes. Used by GitHub, Stripe, Vercel.

**Secondary Font (Body & Code):** JetBrains Mono

- Weights: 400 (Regular), 600 (Bold)
- Usage: Code blocks, governance rules, structured data, YAML/JSON
- Rationale: Technical but beautiful. Makes governance DNA readable.

**Fallback Stack:**
```css
/* Headers */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Code */
font-family: 'JetBrains Mono', 'SF Mono', Monaco, Menlo, monospace;
```

### Type Scale

| Level | Size | Weight | Line Height | Usage |
|-------|------|--------|------------|-------|
| **H1** | 48px | 700 (Bold) | 1.2 | Page titles, mission statements |
| **H2** | 36px | 600 (Semibold) | 1.25 | Section headers, major topics |
| **H3** | 28px | 600 (Semibold) | 1.3 | Subsections, feature names |
| **H4** | 22px | 600 (Semibold) | 1.35 | Component titles, callouts |
| **Body L** | 18px | 400 (Regular) | 1.6 | Large body text, introductions |
| **Body M** | 16px | 400 (Regular) | 1.6 | Standard paragraph text |
| **Body S** | 14px | 400 (Regular) | 1.5 | Secondary text, descriptions |
| **Label** | 12px | 500 (Medium) | 1.4 | UI labels, badges, metadata |
| **Code** | 14px | 400 (Regular) | 1.6 | Code blocks, governance rules |

### Text Styles

```css
/* Governance Rule (Important) */
.governance-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.6;
  color: #0A0E27; /* EGOS Black */
  background: #F9FAFB; /* Gray 50 */
  padding: 1rem;
  border-left: 4px solid #2563EB; /* EGOS Blue */
}

/* Evidence/Data Display */
.evidence-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #10B981; /* Evidence Green */
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

/* Status Badge (Passing) */
.status-passing {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #10B981; /* Evidence Green */
  background: rgba(16, 185, 145, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
}
```

---

## Logo & Wordmark

### Logo Usage

**EGOS Logo:** Fibonacci spiral in EGOS Blue (`#2563EB`), circular, 1:1 ratio.

- **Variations:**
  - Full logo (mark + wordmark) — for main branding
  - Mark only (spiral) — for favicon, app icons, small spaces
  - Horizontal lockup — for letterhead, social headers
  - Vertical stacked — for limited-width spaces (sidebars, mobile)

**Sacred Code Integration:** The spiral contains the Fibonacci sequence visually: `000.111.369.963.1618`

### Minimum Size

- Print/Web: 48px minimum width
- Favicon: 32px
- Social: 200px × 200px recommended

### Clear Space

Minimum 12px clearance on all sides. Don't crowd the logo.

### Color Variants

| Context | Color | Background |
|---------|-------|-----------|
| **Light backgrounds** | EGOS Blue `#2563EB` | White/Light gray |
| **Dark backgrounds** | White `#FFFFFF` | EGOS Black or Navy |
| **Error contexts** | Danger Red `#EF4444` | White background |
| **Success contexts** | Evidence Green `#10B981` | White background |
| **Grayscale** | Gray 600 `#4B5563` | For monochrome output |

---

## Visual Language

### Iconography

**Icon System:** Feather Icons (open-source, MIT)

- All icons 20px × 20px base size
- Stroke weight: 2px
- Rounded corners for approachability
- Colors: Match functional color (Green for success, Red for error, etc.)

**Custom Icons for EGOS:**
- Governance/Rules: Shield icon with checkmark
- Agent/Autonomy: Hexagon or robot head (rounded, not mechanical)
- Evidence/Data: Bar chart or graph
- Transparency: Eye icon or spotlight
- Community: People/Network icon

### Imagery Style

**Photography:** Technical, real, evidence-based.
- Show actual dashboards, logs, metrics (not staged scenes)
- Use screenshots from EGOS in action
- Include humans but focus on systems/output

**Illustrations:** Minimal, geometric, Fibonacci/spiral-based.
- Use SVG only
- Maintain 45-degree angles where possible
- Color: 1-2 colors max (Blue + Green or Blue + Navy)
- No cartoonish characters
- No fluff/decorative only

### Data Visualization (Charts & Graphs)

**Default Palette:**
```
Primary:    #2563EB (EGOS Blue)
Success:    #10B981 (Evidence Green)
Warning:    #F59E0B (Amber)
Error:      #EF4444 (Red)
Secondary:  #8B5CF6 (Purple)
Tertiary:   #06B6D4 (Cyan)
```

**Guidelines:**
- Line charts for trends over time (rules compliance, costs)
- Bar charts for comparisons (agent performance, provider costs)
- Pie/Donut only if 2-3 categories (avoid cluttered pie charts)
- Always include legend + values on-hover
- Use solid colors; avoid gradients for data viz

---

## Layout & Spacing

### Spacing System (8px Base)

| Multiple | Value | Usage |
|----------|-------|-------|
| **0.5x** | 4px | Micro-spacing (icon margins, tight groups) |
| **1x** | 8px | Default padding, small gaps |
| **1.5x** | 12px | Button padding, component spacing |
| **2x** | 16px | Section padding, standard gaps |
| **3x** | 24px | Large section padding, major breaks |
| **4x** | 32px | Page margins, hero spacing |
| **6x** | 48px | XL section breaks |

### Grid System

- **Web:** 12-column grid, 20px gutters
- **Mobile:** 4-column grid, 16px gutters
- **Container max-width:** 1280px

### Cards & Containers

- **Border radius:** 8px (standard), 12px (soft), 4px (code/data tight)
- **Box shadow:**
  - Subtle: `0 1px 3px rgba(0,0,0,0.1)`
  - Default: `0 4px 6px rgba(0,0,0,0.12)`
  - Elevated: `0 10px 15px rgba(0,0,0,0.15)`

---

## Voice & Tone

### Messaging Principles

| Dimension | Profile | Example |
|-----------|---------|---------|
| **Formality** | Professional, not stiff | "Governance doesn't mean bottleneck." (not "Governance prevents efficiency issues.") |
| **Transparency** | Own limitations | "Pre-commit hooks catch *most* issues, not all." |
| **Authority** | Evidence-backed | "In 7 months of production use, our pre-commit rules caught 34 policy violations before merge." |
| **Accessibility** | Translate jargon | "Provenance signature" → "Signed proof of who changed this rule and when" |
| **Accountability** | Admit failures | "We missed this edge case. Here's what we're changing." |

### Key Messaging Pillars (Tones)

1. **Governance is Infrastructure** → Technical, authoritative
2. **Evidence Before Action** → Data-driven, measured
3. **Operators First, Agents Second** → Pragmatic, safety-conscious
4. **You Own Your Rules** → Empowering, anti-lock-in
5. **Multi-Repo, One Truth** → Unified, scalable

### What to Say / What Not to Say

| Do Say | Don't Say |
|--------|-----------|
| "Rules enforce safety" | "Rules prevent freedom" |
| "Auditable from day one" | "We guarantee 100% security" |
| "Caught by pre-commit" | "Magic AI protection" |
| "Community-evolved rules" | "We dictate governance" |
| "Evidence shows X is cheaper" | "Use this because we say so" |

### Tone Across Contexts

| Context | Tone | Example |
|---------|------|---------|
| **Documentation** | Clear, thorough, no fluff | "Pre-commit hooks validate rules before merge." |
| **Incident Reports** | Honest, not defensive | "We didn't catch this because rule Y was ambiguous. Here's the fix." |
| **Marketing/GTM** | Confident but not hypey | "One team, four repos, one governance DNA." |
| **Community/Discord** | Friendly but technical | "Great question! Here's why we chose symlinks over config files." |
| **Error Messages** | Actionable, specific | "Rule violation: agent can't delete files in /core. Use the update-core workflow instead." |

---

## Visual Hierarchy & Layout Patterns

### Documentation Pages

```
[EGOS Logo + Breadcrumb]
┌─────────────────────────────┐
│ H1: Page Title              │
│ (One-liner description)     │
└─────────────────────────────┘

[Table of Contents] [Main Content]

H2: Section 1
  Paragraph (body M)
  [Code block / Evidence box]

H3: Subsection
  Bullet list

H2: Section 2
  [Table]
  [Callout box - governance rule]
```

### Card Layout (Evidence Display)

```
┌─ EGOS Blue accent bar (4px left border)
│ H4: Metric Title
│ [Large number: 34 rules violated]
│ [Small label: Pre-commit catches (1 week)]
└─
```

### Status/Error Alerts

```
┌─────────────────────────────────┐
│ [Icon: checkmark/warning/X]     │
│ Status: Passed / Warning / Error│
│ Details: Human-readable message │
│ [Action link if needed]         │
└─────────────────────────────────┘
```

---

## Implementation Standards

### Web (HTML/CSS)

```html
<!-- Main container -->
<div class="egos-container">
  <header class="egos-header">
    <img src="/egos-logo.svg" alt="EGOS" class="egos-logo" />
  </header>

  <main class="egos-content">
    <h1 class="egos-h1">Governance is Infrastructure</h1>
    <p class="egos-body-m">Description here...</p>

    <div class="egos-rule-block">
      <code class="egos-code">DOMAIN_RULES.md content</code>
    </div>

    <div class="egos-status egos-status--passed">
      <span class="egos-status__icon">✓</span>
      <span class="egos-status__text">Rules enforced</span>
    </div>
  </main>
</div>
```

```css
/* Color Variables */
:root {
  --egos-black: #0A0E27;
  --egos-navy: #1A2F5A;
  --egos-blue: #2563EB;
  --egos-green: #10B981;
  --egos-amber: #F59E0B;
  --egos-red: #EF4444;
  --egos-white: #FFFFFF;
  --egos-gray-50: #F9FAFB;
  --egos-gray-200: #E5E7EB;
  --egos-gray-600: #4B5563;
}

/* Typography */
.egos-h1 {
  font-family: 'Inter', sans-serif;
  font-size: 48px;
  font-weight: 700;
  line-height: 1.2;
  color: var(--egos-black);
}

.egos-body-m {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.6;
  color: var(--egos-gray-600);
}

/* Governance Rule Block */
.egos-rule-block {
  background: var(--egos-gray-50);
  border-left: 4px solid var(--egos-blue);
  padding: 1rem;
  border-radius: 4px;
  margin: 1.5rem 0;
}

.egos-code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  color: var(--egos-black);
}

/* Status States */
.egos-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
}

.egos-status--passed {
  background: rgba(16, 185, 145, 0.1);
  color: var(--egos-green);
}

.egos-status--warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--egos-amber);
}

.egos-status--error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--egos-red);
}
```

### Dark Mode

```css
@media (prefers-color-scheme: dark) {
  :root {
    --egos-background: #0A0E27;
    --egos-surface: #1A2F5A;
    --egos-text-primary: #FFFFFF;
    --egos-text-secondary: #E5E7EB;
    --egos-border: #2D3E5F;
  }

  body {
    background: var(--egos-background);
    color: var(--egos-text-primary);
  }

  .egos-rule-block {
    background: var(--egos-surface);
    border-left-color: var(--egos-blue);
  }
}
```

---

## Brand Assets Checklist

| Asset | Format | Location | Status |
|-------|--------|----------|--------|
| Logo (full) | SVG | `/brand/egos-logo.svg` | TODO |
| Logo (mark) | SVG | `/brand/egos-mark.svg` | TODO |
| Logo (wordmark) | SVG | `/brand/egos-wordmark.svg` | TODO |
| Favicon | ICO/PNG | `/public/favicon.ico` | TODO |
| Color swatches | PDF/figma | `/brand/color-palette.pdf` | TODO |
| Typography guide | PDF | `/brand/typography-guide.pdf` | TODO |
| Component library | Figma | Shared link | TODO |
| Social templates | Figma | Shared link | TODO |
| Email signatures | HTML | `/brand/email-sig.html` | TODO |

---

## Usage Examples

### Website Header

Dark navy background, white text, blue accent on hover:
```
[EGOS Logo] EGOS — Governance Kernel
─────────────────────────────────────
Governance is Infrastructure
[Learn More →]
```

### GitHub Badge/Readme

```markdown
[![Built with EGOS](https://img.shields.io/badge/Built%20with-EGOS-2563EB?style=flat-square&logo=data:image/svg%2bxml;...)](https://github.com/enioxt/egos)
```

### Governance Rule Callout (Docs)

**Visual:** Navy card with blue left border, code font, evidence green checkmark.

```
┌─ EGOS Blue accent
│ 📋 Governance Rule
│ Agent cannot delete files in /core
│ Pre-commit enforcement ✓
└─
```

### Incident Report Header

```
[Danger Red background] [White text]
Incident #7 — Agent Hallucination
Rule: Frozen Zones | Status: CAUGHT + PREVENTED
```

---

## Accessibility

### Color Contrast Ratios

- All text vs background: 4.5:1 minimum (WCAG AA)
- Large text (18px+): 3:1 minimum
- UI components: 3:1 minimum

**Pass Check:** EGOS Blue (`#2563EB`) on White: **8.6:1** ✓

### Dark Mode Contrast

- Text on navy: WCAG AAA (7:1+)
- Links on navy: WCAG AA (4.5:1+)

### Dyslexia-Friendly

- Use serif/sans-serif (Inter is good)
- Avoid all-caps for body text
- Letter-spacing: 1.5+ for readability
- Line-height: 1.6+ for dense content

### Keyboard Navigation

- All interactive elements keyboard accessible (Tab order)
- Visible focus states (blue outline, 2px minimum)
- No time-dependent interactions

---

## Brand Evolution

This is a **living document**. Design decisions are guided by:

1. **Governance-First Identity** — Every visual choice must reinforce rules/infrastructure
2. **Data Readability** — Evidence and metrics must be crystal clear
3. **Technical Authority** — No fluff; we look like infrastructure
4. **Developer Accessibility** — We respect their time (clean, fast, no clutter)

Review and update quarterly based on user feedback and ecosystem evolution.

---

## Contact & Questions

For brand questions, visual assets, or design collaboration:
- GitHub: [@enioxt](https://github.com/enioxt)
- Discussion: `#design` in community channels

---

*EGOS = Orchestration Kernel for Governed AI Agents. Governed with clarity. Built with purpose.*
