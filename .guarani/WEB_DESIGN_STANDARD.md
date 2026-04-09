# EGOS Web Design Standard

**Sacred Code:** 000.111.369.963.1618  
**Version:** 1.0.0 | **Updated:** 2026-04-08  
**Applies to:** ALL EGOS web applications (852, Inteligência, Guard Brasil, etc.)

---

## 🎯 Philosophy

> **"Police Intelligence meets Open Source."**
> 
> Dark-first. Data-dense. Glassmorphism. Command-palette-driven.
> 
> Inspired by: Linear.app, Palantir, mempool.space, Vercel

---

## 🏗️ Architecture

```
components/
├── ui/           # shadcn/ui raw components (untouched)
├── primitives/   # EGOS-themed shadcn wrappers
├── blocks/       # Composed patterns (reusable)
├── layouts/      # Page layouts
└── tools/        # Tool-specific visualizations
```

---

## 🎨 Design Tokens (CSS Variables)

```css
:root {
  /* Core Colors */
  --egos-background: #050508;
  --egos-surface: rgba(255, 255, 255, 0.03);
  --egos-border: rgba(255, 255, 255, 0.06);
  --egos-border-hover: rgba(255, 255, 255, 0.12);
  
  /* Brand */
  --egos-primary: #13b6ec;
  --egos-primary-hover: #0e9fd1;
  --egos-secondary: #a855f7;
  --egos-success: #22c55e;
  --egos-danger: #ef4444;
  --egos-warning: #f59e0b;
  
  /* Text */
  --egos-text-primary: #f1f5f9;
  --egos-text-body: rgba(255, 255, 255, 0.87);
  --egos-text-secondary: #94a3b8;
  --egos-text-muted: #64748b;
  --egos-text-dim: #475569;
  
  /* Typography */
  --egos-font-sans: 'Space Grotesk', system-ui, sans-serif;
  --egos-font-mono: 'JetBrains Mono', monospace;
  
  /* Spacing (4pt grid) */
  --egos-space-1: 4px;
  --egos-space-2: 8px;
  --egos-space-3: 12px;
  --egos-space-4: 16px;
  --egos-space-6: 24px;
  --egos-space-8: 32px;
  
  /* Radius */
  --egos-radius-sm: 6px;
  --egos-radius-md: 10px;
  --egos-radius-lg: 12px;
  --egos-radius-xl: 16px;
  
  /* Transitions */
  --egos-transition-fast: 150ms ease;
  --egos-transition-base: 200ms ease;
}
```

---

## 🧱 Component Patterns

### 1. Glass Card (Primary Container)

```tsx
// components/primitives/GlassCard.tsx
import { cn } from '@/lib/utils';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  elevated?: boolean;
  hover?: boolean;
}

export function GlassCard({ 
  children, 
  className, 
  elevated = false,
  hover = false 
}: GlassCardProps) {
  return (
    <div className={cn(
      "bg-white/[0.03] border border-white/[0.06] rounded-xl p-5",
      elevated && "bg-[#050508]/85 border-white/[0.12] backdrop-blur-xl",
      hover && "hover:border-white/[0.12] transition-colors",
      className
    )}>
      {children}
    </div>
  );
}
```

### 2. Tool Result Card

```tsx
// Pattern for displaying tool results
// Use semantic border colors for tool types

const toolStyles = {
  hibp: 'border-l-red-500/50 bg-red-500/5',
  shodan: 'border-l-blue-500/50 bg-blue-500/5',
  image: 'border-l-purple-500/50 bg-purple-500/5',
  cnpj: 'border-l-emerald-500/50 bg-emerald-500/5',
  transparency: 'border-l-amber-500/50 bg-amber-500/5',
};
```

### 3. Command Palette Pattern

```tsx
// Cmd+K navigation — Linear-style
// Always implement for power users
```

---

## 🎭 shadcn/ui Integration

### Installation

```bash
npx shadcn-ui@latest init --yes --template next --base-color neutral
```

### Theme Configuration

```json
// components.json
{
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

### CSS Override (globals.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Override shadcn with EGOS tokens */
    --background: 240 10% 3%;
    --foreground: 210 40% 98%;
    --card: 240 10% 5%;
    --card-foreground: 210 40% 98%;
    --popover: 240 10% 5%;
    --popover-foreground: 210 40% 98%;
    --primary: 195 83% 50%;
    --primary-foreground: 240 10% 3%;
    --secondary: 240 4% 16%;
    --secondary-foreground: 210 40% 98%;
    --muted: 240 4% 16%;
    --muted-foreground: 215 20% 65%;
    --accent: 195 83% 50%;
    --accent-foreground: 240 10% 3%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 210 40% 98%;
    --border: 240 4% 20%;
    --input: 240 4% 20%;
    --ring: 195 83% 50%;
    --radius: 0.625rem;
  }
}

/* EGOS additions */
@layer components {
  .egos-glass {
    @apply bg-white/[0.03] border border-white/[0.06] backdrop-blur-xl;
  }
  
  .egos-glass-elevated {
    @apply bg-[#050508]/90 border border-white/[0.12] backdrop-blur-2xl;
  }
  
  .egos-text-gradient {
    @apply bg-gradient-to-r from-white to-[#13b6ec] bg-clip-text text-transparent;
  }
}
```

---

## 📏 Spacing System

| Token | Value | Usage |
|-------|-------|-------|
| `gap-1` | 4px | Tight spacing, icon gaps |
| `gap-2` | 8px | Default component gaps |
| `gap-4` | 16px | Section gaps |
| `p-4` | 16px | Card padding |
| `p-6` | 24px | Container padding |
| `p-8` | 32px | Section padding |

**RULE:** Never use arbitrary values (e.g., `w-[123px]`). Use 4pt increments.

---

## 🖼️ Typography

```tsx
// app/layout.tsx
import { Space_Grotesk, JetBrains_Mono } from 'next/font/google';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['300', '400', '500', '600', '700'],
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  weight: ['400', '500', '600'],
});
```

| Element | Class | Size | Weight |
|---------|-------|------|--------|
| Page Title | `text-3xl font-bold` | 30px | 700 |
| Section | `text-xl font-semibold` | 20px | 600 |
| Subsection | `text-lg font-semibold` | 18px | 600 |
| Body | `text-sm` | 14px | 400 |
| Caption | `text-xs` | 12px | 500 |
| Data | `font-mono text-xs` | 12px | 400 |

---

## ♿ Accessibility

- **Contrast:** WCAG AA minimum on all text
- **Focus rings:** `ring-2 ring-[#13b6ec] ring-offset-2`
- **Touch targets:** Minimum 40x40px (Fitts's Law)
- **Reduced motion:** Respect `prefers-reduced-motion`
- **Screen readers:** All shadcn components include proper ARIA

---

## 🚫 Anti-Patterns

| ❌ Don't | ✅ Do |
|----------|-------|
| Light mode | Dark-only with CSS variables |
| Magic numbers | 4pt grid system |
| Inline colors | CSS variable tokens |
| Decorative elements without function | Purpose-driven design |
| Modify shadcn/ui files directly | Extend via wrapper components |
| Import from `components/ui` everywhere | Build product-specific abstractions |

---

## 🔄 Migration Checklist

When updating existing EGOS apps:

- [ ] Replace arbitrary Tailwind values with 4pt grid
- [ ] Import Space Grotesk font
- [ ] Update CSS variables to EGOS tokens
- [ ] Apply glassmorphism to cards
- [ ] Add command palette (Cmd+K)
- [ ] Verify shadcn/ui components use EGOS theme
- [ ] Run accessibility audit

---

## 📚 References

- **EGOS Design Identity:** `.guarani/DESIGN_IDENTITY.md`
- **shadcn/ui docs:** https://ui.shadcn.com
- **Radix UI:** https://www.radix-ui.com
- **Linear.app:** https://linear.app (reference for density)
- **Tailwind CSS:** https://tailwindcss.com

---

> *"Consistency breeds trust. Every surface speaks the same language."*
