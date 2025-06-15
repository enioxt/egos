@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - docs/website/docs/system/EGOS_UI_Documentation.md

﻿# EGOS UI Design System Documentation

This document outlines the UI/UX standards, components, and design patterns for the EGOS project website. It is derived from the project's Tailwind CSS configuration and global stylesheets.

## 1. Color Palette

Colors are defined using HSL values via CSS custom properties. The system supports light and dark modes.

### 1.1. Light Mode Colors

- **Background (`--background`):** `hsl(0 0% 100%)` (White)
- **Foreground (`--foreground`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue)
- **Card Background (`--card`):** `hsl(0 0% 100%)` (White)
- **Card Foreground (`--card-foreground`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue)
- **Popover Background (`--popover`):** `hsl(0 0% 100%)` (White)
- **Popover Foreground (`--popover-foreground`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue)
- **Primary (`--primary`):** `hsl(221.2 83.2% 53.3%)` (Bright Blue)
- **Primary Foreground (`--primary-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Secondary (`--secondary`):** `hsl(210 40% 96.1%)` (Light Gray)
- **Secondary Foreground (`--secondary-foreground`):** `hsl(222.2 47.4% 11.2%)` (Dark Blue)
- **Muted (`--muted`):** `hsl(210 40% 96.1%)` (Light Gray)
- **Muted Foreground (`--muted-foreground`):** `hsl(215.4 16.3% 46.9%)` (Gray)
- **Accent (`--accent`):** `hsl(210 40% 96.1%)` (Light Gray)
- **Accent Foreground (`--accent-foreground`):** `hsl(222.2 47.4% 11.2%)` (Dark Blue)
- **Destructive (`--destructive`):** `hsl(0 84.2% 60.2%)` (Bright Red)
- **Destructive Foreground (`--destructive-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Border (`--border`):** `hsl(214.3 31.8% 91.4%)` (Very Light Gray)
- **Input Background (`--input`):** `hsl(214.3 31.8% 91.4%)` (Very Light Gray)
- **Ring (`--ring`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue - for focus)

### 1.2. Dark Mode Colors

- **Background (`--background`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue)
- **Foreground (`--foreground`):** `hsl(210 40% 98%)` (Near White)
- **Card Background (`--card`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue)
- **Card Foreground (`--card-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Popover Background (`--popover`):** `hsl(222.2 84% 4.9%)` (Very Dark Blue)
- **Popover Foreground (`--popover-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Primary (`--primary`):** `hsl(217.2 91.2% 59.8%)` (Bright Blue)
- **Primary Foreground (`--primary-foreground`):** `hsl(222.2 47.4% 11.2%)` (Dark Blue)
- **Secondary (`--secondary`):** `hsl(217.2 32.6% 17.5%)` (Dark Grayish Blue)
- **Secondary Foreground (`--secondary-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Muted (`--muted`):** `hsl(217.2 32.6% 17.5%)` (Dark Grayish Blue)
- **Muted Foreground (`--muted-foreground`):** `hsl(215 20.2% 65.1%)` (Lighter Gray)
- **Accent (`--accent`):** `hsl(217.2 32.6% 17.5%)` (Dark Grayish Blue)
- **Accent Foreground (`--accent-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Destructive (`--destructive`):** `hsl(0 62.8% 30.6%)` (Darker Red)
- **Destructive Foreground (`--destructive-foreground`):** `hsl(210 40% 98%)` (Near White)
- **Border (`--border`):** `hsl(217.2 32.6% 17.5%)` (Dark Grayish Blue)
- **Input Background (`--input`):** `hsl(217.2 32.6% 17.5%)` (Dark Grayish Blue)
- **Ring (`--ring`):** `hsl(212.7 26.8% 83.9%)` (Light Grayish Blue - for focus)

## 2. Typography

- **Default Sans-serif Font Family:** `Inter` (Applied via `font-sans` Tailwind utility class defined in `tailwind.config.js`). This is the primary font for the UI.
- **Default Serif Font Family:** `Playfair Display` (Applied via `font-serif` Tailwind utility class).

### 2.1. Base Styles (from `globals.css`)

- **Body Text:** Default font size is likely `1rem` (16px) as per standard browser behavior unless overridden. Line height is `1.5` (`leading-normal` in Tailwind by default for body).
- **Links (`a`):** Default color inherited, no underline by default. `text-primary` and `hover:underline` often applied for explicit links (e.g., `link` variant of Button).

### 2.2. Common Typographic Utilities & Patterns (derived from UI components like Button, Card, Alert, Breadcrumb)

Many UI components leverage a consistent set of Tailwind utility classes for typography. The following patterns are frequently observed:

- **Font Sizes:**
  - `text-xs`: (0.75rem / 12px) - Used in `Badge` and `DropdownMenuShortcut`.
  - `text-sm`: (0.875rem / 14px) - Used in `Button`, `CardDescription`, `AlertDescription`.
  - `text-base`: (1rem / 16px) - Effective default body text size, typically set by Tailwind's preflight styles or browser defaults.
  - `text-lg`: (1.125rem / 18px) - *To be confirmed.*
  - `text-xl`: (1.25rem / 20px) - *To be confirmed.*
  - `text-2xl`: (1.5rem / 24px) - Used in `CardTitle`.
  - *Larger heading sizes (h1-h4 or `text-3xl`, `text-4xl`, etc.) to be documented based on global styles or specific page component usage.*

- **Font Weights:**
  - `font-light`: *To be confirmed.*
  - `font-normal`: Default weight for body text.
  - `font-medium`: Used in `Button`, `AlertTitle`.
  - `font-semibold`: Used in `CardTitle`.
  - `font-bold`: *To be confirmed.*
  - `font-extrabold`, `font-black`: *To be confirmed.*

- **Line Heights:**
  - `leading-none`: Used in `CardTitle`, `AlertTitle`.
  - `leading-tight`: Used in `CardTitle`, `AlertTitle` (implicitly via `tracking-tight` often paired).
  - `leading-snug`: *To be confirmed.*
  - `leading-normal`: Default for body text (1.5).
  - `leading-relaxed`: Used for paragraphs within `AlertDescription` (`[&_p]:leading-relaxed`).

- **Tracking (Letter Spacing):**
  - `tracking-tight`: Used in `CardTitle`, `AlertTitle`.

- **Text Colors:**
  - `text-foreground`: Primary text color, typically for body text and main content.
  - `text-muted-foreground`: For secondary or less emphasized text (e.g., `CardDescription`).
  - `text-primary`: Often used for links or primary action text.
  - `text-primary-foreground`: For text on `bg-primary` backgrounds.
  - `text-secondary-foreground`: For text on `bg-secondary` backgrounds.
  - `text-destructive`: For error messages or destructive action text.
  - `text-destructive-foreground`: For text on `bg-destructive` backgrounds.

- **Heading Elements (`h1`-`h6`):**
  - `h3` (`CardTitle`): `text-2xl font-semibold leading-none tracking-tight`.
  - `h5` (`AlertTitle`): `font-medium leading-none tracking-tight` (inherits size or uses browser default for h5 if not specified).
  - *Specific styles for other heading levels (h1, h2, h4, h6) should be applied using utility classes as needed, or defined in `globals.css` if a consistent global style is desired. Currently, no global h1-h6 styles are explicitly defined beyond Tailwind's defaults.*

These patterns are prevalent across most components in `src/components/ui/`. For instance, form elements, dropdowns, and navigation items generally adhere to these text sizes, weights, and color conventions.

## 3. Border Radius

A base radius unit is defined, and scaled for different component sizes.

- **Base Radius (`--radius`):** `0.5rem` (8px)
- **Tailwind `rounded-lg`:** `0.5rem` (8px)
- **Tailwind `rounded-md`:** `0.375rem` (6px)
- **Tailwind `rounded-sm`:** `0.25rem` (4px)

## 4. Layout

- **Container Max Width (`2xl` breakpoint):** `1400px`
- **Container Default Padding:** `2rem` (32px)
- **Fixed Header Height (`--header-height`):** `4rem` (64px)
- **General Content Container (`.content-container` class):**
  - Max Width: `1400px`
  - Horizontal Padding: `1.5rem` (24px)

## 5. Animation & Transitions

- **Keyframes:** `accordion-down`, `accordion-up`, `fade-in`, `draw`, `pulse-slow`
- **Animation Utilities:** `animate-accordion-down`, `animate-accordion-up`, `animate-fade-in`, `animate-draw`, `animate-pulse-slow`
- **Transition Durations:**
  - `--transition-fast: 150ms`
  - `--transition-medium: 300ms`
  - `--transition-slow: 500ms`
- Default easing for `transition-base` class: `cubic-bezier(0.4, 0, 0.2, 1)`

### 6.2. Card

The `Card` component is used to group related content and actions. It consists of several sub-components for structure.

**Location:** `src/components/ui/card.tsx`

**Sub-components & Styling:**

- **`Card`** (Root element):
  - Base Styles: `rounded-lg border bg-card text-card-foreground shadow-sm`
  - Background: `var(--card)`
  - Text Color: `var(--card-foreground)`
  - Border: `var(--border)`, `rounded-lg` (0.5rem / 8px)
  - Shadow: `shadow-sm`

- **`CardHeader`**:
  - Layout: `flex flex-col space-y-1.5`
  - Padding: `p-6` (1.5rem / 24px)

- **`CardTitle`** (renders as `<h3>`):
  - Typography: `text-2xl font-semibold leading-none tracking-tight` (1.5rem / 24px)

- **`CardDescription`** (renders as `<p>`):
  - Typography: `text-sm text-muted-foreground` (0.875rem / 14px)

- **`CardContent`**:
  - Padding: `p-6 pt-0` (1.5rem / 24px, no top padding)

- **`CardFooter`**:
  - Layout: `flex items-center`
  - Padding: `p-6 pt-0` (1.5rem / 24px, no top padding)

---

### 6.3. Breadcrumb

Navigational aid to show the user's current location within the site hierarchy.

**Location:** `src/components/ui/breadcrumb.tsx`

**Sub-components & Styling:**

- **`Breadcrumb`** (Root `<nav>`):
  - Layout: `flex flex-wrap items-center`

- **`BreadcrumbList`** (`<ol>`):
  - Layout: `flex flex-wrap items-center gap-1.5 sm:gap-2.5`

- **`BreadcrumbItem`** (`<li>`):
  - Layout: `inline-flex items-center gap-1.5`

- **`BreadcrumbLink`** (`<a>` or `Slot`):
  - Typography: `text-sm font-medium`
  - Interaction: `underline-offset-4 transition-colors hover:text-foreground hover:underline`. (Initial color is typically less prominent, e.g., inherited or explicitly set to a muted color).

- **`BreadcrumbPage`** (`<span>`, current page):
  - Typography: `text-sm font-medium`
  - Color: `text-foreground`

- **`BreadcrumbSeparator`** (`<span>`):
  - Color: `text-muted-foreground`
  - Default Icon: `ChevronRight` (`h-3.5 w-3.5`)

- **`BreadcrumbEllipsis`** (`<span>`):
  - Layout: `flex h-9 w-9 items-center justify-center`
  - Icon: `MoreHorizontal` (`h-4 w-4`)

---

### 6.4. Dropdown Menu

Provides interactive dropdown menus, often used for actions or selections, built upon Radix UI primitives.

**Location:** `src/components/ui/dropdown-menu.tsx`

**Key Styling & Structure:**

- **`DropdownMenuContent` / `DropdownMenuSubContent` (Popover Panel):**
  - Background & Text: `bg-popover`, `text-popover-foreground`
  - Border: `rounded-md`, `border`
  - Shadow: `shadow-lg`
  - Padding: `p-1` internally for items.
  - Animation: Uses Tailwind animation utilities for open/close states (e.g., `fade-in-0`, `zoom-in-95`).

- **`DropdownMenuItem`, `DropdownMenuCheckboxItem`, `DropdownMenuRadioItem`, `DropdownMenuSubTrigger` (Interactive Items):**
  - Typography: `text-sm`
  - Background: Transparent by default.
  - Interaction: `cursor-default`, `select-none`.
  - Focus/Open State: `focus:bg-accent`, `focus:text-accent-foreground`; `data-[state=open]:bg-accent` for triggers.
  - Disabled State: `data-[disabled]:opacity-50`, `data-[disabled]:pointer-events-none`.
  - `inset` prop common for `pl-8` padding to align text when icons/indicators are present.

- **Indicators (within `DropdownMenuCheckboxItem`, `DropdownMenuRadioItem`):**
  - `Check` icon (`lucide-react`): `h-4 w-4` for checkboxes.
  - `Circle` icon (`lucide-react`): `h-2 w-2 fill-current` for radio items.

- **`DropdownMenuLabel` (Non-interactive title within menu):**
  - Typography: `text-sm font-semibold`
  - Padding: `px-2 py-1.5`

- **`DropdownMenuSeparator`:**
  - Styling: `-mx-1 my-1 h-px bg-muted` (horizontal line)

- **`DropdownMenuShortcut` (For keyboard hints):**
  - Typography: `text-xs tracking-widest opacity-60`
  - Alignment: `ml-auto` (typically right-aligned)

---

### 6.5. Badge

Small, inline status indicators or labels.

**Location:** `src/components/ui/badge.tsx`

**Base Styling:**

- Layout: `inline-flex items-center`
- Shape: `rounded-full` (pill shape)
- Border: Default `border` (can be overridden by variants)
- Padding: `px-2.5 py-0.5`
- Typography: `text-xs font-semibold` (0.75rem / 12px)
- Focus: Uses `ring-ring` and `ring-offset-background`.
- Transitions: `transition-colors`

**Variants:**

- **`default`**:
  - Border: `border-transparent`
  - Background: `bg-primary`
  - Text: `text-primary-foreground`
  - Hover: `bg-primary/80`
- **`secondary`**:
  - Border: `border-transparent`
  - Background: `bg-secondary`
  - Text: `text-secondary-foreground`
  - Hover: `bg-secondary/80`
- **`destructive`**:
  - Border: `border-transparent`
  - Background: `bg-destructive`
  - Text: `text-destructive-foreground`
  - Hover: `bg-destructive/80`
- **`outline`**:
  - Border: Uses the default border.
  - Text: `text-foreground` (no specific background color)

---

### 6.6. Tabs

Allows content to be organized into selectable panels.

**Location:** `src/components/ui/tabs.tsx`

**Key Styling & Structure:**

- **`TabsList` (Container for tab triggers):**
  - Layout: `inline-flex h-9 items-center justify-center`
  - Background & Text (of the list itself): `bg-muted`, `text-muted-foreground`
  - Shape & Padding: `rounded-lg`, `p-1` (internal)

- **`TabsTrigger` (Individual tab button):**
  - Typography: `text-sm font-medium`
  - Shape & Padding: `rounded-md`, `px-3 py-1`
  - Transitions: `transition-all`
  - Focus: Standard focus ring styling.
  - Disabled State: `disabled:opacity-50`, `pointer-events-none`.
  - **Active State (`data-[state=active]`):**
    - Background: `bg-background`
    - Text: `text-foreground`
    - Shadow: `shadow` (subtle shadow to lift the active tab)
  - **Inactive State:** Text color defaults to `text-muted-foreground` (inherited from `TabsList`).

- **`TabsContent` (Content panel):**
  - Spacing: `mt-2` (margin-top to separate from `TabsList`)
  - Focus: Standard focus ring styling (applies if content is focusable).

---

## 6. Components

This section details the specific UI components used in the EGOS website. While not all components from `src/components/ui/` are exhaustively documented here, the following selection provides a comprehensive overview of the common styling patterns, typographic choices, and structural conventions. Other components in the directory are expected to largely adhere to these established patterns (e.g., use of theme colors like `primary`, `secondary`, `accent`, `muted`, `popover`; consistent focus and interaction states; and similar typographic scales).

### 6.1. Button

The `Button` component provides various styles and sizes for user actions. It's built using `class-variance-authority`.

**Location:** `src/components/ui/button.tsx`

**Base Styling:**

- Display: `inline-flex`, `items-center`, `justify-center`
- Spacing: `gap-2` (for icon and text)
- Text: `text-sm`, `font-medium`, `whitespace-nowrap`
- Border Radius: `rounded-md` (0.375rem / 6px)
- Transitions: `transition-colors`
- Focus: Uses `ring-ring` and `ring-offset-background` for visible focus rings.
- Disabled State: `opacity-50`, `pointer-events-none`
- SVG Icons: Default size `1rem` (16px), `shrink-0`.

**Variants:**

- **`default`**:
  - Background: `bg-primary` (varies by mode)
  - Text: `text-primary-foreground`
  - Hover: `bg-primary/90`
- **`destructive`**:
  - Background: `bg-destructive`
  - Text: `text-destructive-foreground`
  - Hover: `bg-destructive/90`
- **`outline`**:
  - Background: `bg-background`
  - Text: Default foreground, `hover:text-accent-foreground`
  - Border: `border border-input`
  - Hover: `bg-accent`
- **`secondary`**:
  - Background: `bg-secondary`
  - Text: `text-secondary-foreground`
  - Hover: `bg-secondary/80`
- **`ghost`**:
  - Background: Transparent
  - Text: Default foreground, `hover:text-accent-foreground`
  - Hover: `bg-accent`
- **`link`**:
  - Text: `text-primary`, `underline-offset-4`
  - Hover: `underline`

**Sizes:**

- **`default`**: Height `2.5rem` (40px), Padding `px-4 py-2`
- **`sm`**: Height `2.25rem` (36px), Padding `px-3`, `rounded-md`
- **`lg`**: Height `2.75rem` (44px), Padding `px-8`, `rounded-md`
- **`icon`**: Height `2.5rem` (40px), Width `2.5rem` (40px) (Square)

**Props:**

- Standard HTML button attributes.
- `variant`: "default" (default), "destructive", "outline", "secondary", "ghost", "link"
- `size`: "default" (default), "sm", "lg", "icon"
- `asChild`: `boolean` (default: `false`) - Allows rendering as a child component using `Slot`.

---
