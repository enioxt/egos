---
title: "EGOS Website Design Patterns"
date: 2025-05-22
author: "EGOS Development Team"
status: "Active"
priority: "High"
tags: [website, design, patterns, reference, standardization]
---

# EGOS Website Design Patterns

## 1. Overview

This document provides a technical reference for the EGOS website design patterns, extracted from analyzing the existing codebase. It serves as the authoritative source for maintaining design consistency across new website components, including the Tool Registry System.

## 2. Component Framework

The EGOS website uses:
- React for component structure
- TypeScript for type safety
- Tailwind CSS for styling
- Radix UI components as a foundation
- Class Variance Authority (cva) for component variants

## 3. Color System

The website uses a design token system with these primary colors:

```css
/* Color variables extracted from the design system */
--primary: #3b82f6;          /* Blue-500 - Primary actions, links */
--primary-foreground: #fff;  /* Text on primary color */
--secondary: #6b7280;        /* Gray-500 - Secondary actions */
--secondary-foreground: #fff; /* Text on secondary color */
--accent: #f3f4f6;           /* Gray-100 - Hover states, highlights */
--accent-foreground: #111827; /* Text on accent color */
--destructive: #ef4444;      /* Red-500 - Error states, warnings */
--destructive-foreground: #fff; /* Text on destructive color */
--muted: #f3f4f6;            /* Gray-100 - Background for muted elements */
--muted-foreground: #6b7280; /* Gray-500 - Muted text */
--card: #fff;                /* Card backgrounds */
--card-foreground: #111827;  /* Text on cards */
```

Status colors:
- Active: `bg-green-500` (#10b981)
- Deprecated: `bg-yellow-500` (#f59e0b)
- Experimental: `bg-purple-500` (#8b5cf6)
- Planning: `bg-blue-500` (#3b82f6)
- Archived: `bg-gray-500` (#6b7280)

## 4. Typography

The website uses a consistent typography system:

```css
/* Base font */
font-family: 'Inter', sans-serif;

/* Heading scales */
h1: text-3xl (1.875rem) font-bold
h2: text-2xl (1.5rem) font-semibold
h3: text-xl (1.25rem) font-semibold
h4: text-lg (1.125rem) font-medium

/* Body text */
Base: text-base (1rem)
Small: text-sm (0.875rem)
Extra small: text-xs (0.75rem)

/* Line heights */
Tight: leading-tight (1.25)
Normal: leading-normal (1.5)
Relaxed: leading-relaxed (1.625)
```

## 5. Component Patterns

### 5.1 Buttons

Buttons follow a consistent pattern with multiple variants:

```tsx
// Default button - Primary action
<Button>Submit</Button>

// Secondary button - Less prominent action
<Button variant="secondary">Cancel</Button>

// Outline button - Tertiary action
<Button variant="outline">More Options</Button>

// Ghost button - Very subtle action
<Button variant="ghost">View Details</Button>

// Link button - Looks like a link
<Button variant="link">Learn More</Button>

// Icon button - Square button with just an icon
<Button variant="icon"><SearchIcon /></Button>
```

Button sizes:
- Default: `h-10 px-4 py-2`
- Small: `h-9 rounded-md px-3`
- Large: `h-11 rounded-md px-8`

### 5.2 Cards

Cards use a consistent structure:

```tsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Description text</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Main content goes here</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

Styling:
- Rounded corners: `rounded-lg`
- Border: `border`
- Shadow: `shadow-sm`
- Padding: `p-6` (with appropriate spacing between elements)

### 5.3 Form Controls

Form controls use consistent styling and behavior:

- Labels: `text-sm font-medium text-gray-700 mb-2`
- Inputs: `w-full p-2 border rounded focus:ring-2 focus:ring-primary`
- Select: `w-full p-2 border rounded`
- Error states: `border-red-500 text-red-500`

### 5.4 Layout

Common layout patterns:

- Grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`
- Flexbox: `flex items-center justify-between`
- Container: `container mx-auto px-4 sm:px-6 lg:px-8`
- Section: `py-12 md:py-16 lg:py-20`

### 5.5 Lists and Tables

- Lists: `space-y-4` for vertical spacing between items
- Table headers: `text-left font-medium text-gray-500 uppercase tracking-wider`
- Table cells: `px-6 py-4 whitespace-nowrap text-sm text-gray-900`

## 6. Responsive Design

The website follows these breakpoints:

```css
/* Breakpoints */
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

Key responsive patterns:
- Mobile-first approach
- Stack columns on mobile, side-by-side on larger screens
- Reduce padding and margins on smaller screens
- Adjust font sizes for readability on mobile

## 7. Animation

The website uses subtle animations for enhanced user experience:

- Transitions: `transition-colors`, `transition-transform`, `transition-opacity`
- Duration: `duration-200` or `duration-300` for most transitions
- Hover effects: Scale (`hover:scale-105`), color changes, shadows

## 8. Accessibility Patterns

- Interactive elements have visible focus states: `focus-visible:ring-2 focus-visible:ring-ring`
- Color contrast ratios follow WCAG AA guidelines
- Form elements have associated labels
- Images have alt text
- Semantic HTML is used throughout

## 9. Integration with Tool Registry Components

When integrating the Tool Registry components, follow these guidelines:

1. Replace custom styling with the appropriate component from the UI library
2. Use the design tokens for colors instead of hardcoded values
3. Follow the established patterns for layout, spacing, and typography
4. Ensure responsive behavior matches existing components
5. Maintain accessibility standards throughout

## 10. Examples

### Tool Card Component:

```tsx
// Before:
<div className="tool-card rounded-lg border p-4 hover:shadow-md transition-shadow">
  {/* Content */}
</div>

// After (using design system):
<Card className="tool-card hover:shadow-md transition-shadow">
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

### Tool Filters Panel:

```tsx
// Before:
<div className="filter-group mb-4">
  <label htmlFor="tool-search" className="block text-sm font-medium mb-2">
    Search
  </label>
  <input
    id="tool-search"
    type="text"
    className="w-full p-2 border rounded"
    placeholder="Search tools..."
  />
</div>

// After (using design system):
<div className="filter-group mb-4">
  <Label htmlFor="tool-search" className="mb-2">
    Search
  </Label>
  <Input
    id="tool-search"
    placeholder="Search tools..."
  />
</div>
```

✧༺❀༻∞ EGOS ∞༺❀༻✧