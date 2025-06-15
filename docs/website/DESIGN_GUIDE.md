---
title: Website Design Guide
version: 1.0.0
status: Active
date_created: 2025-04-09
date_modified: 2025-05-20
authors: [EGOS Team]
description: Outlines the core design directives and visual identity for the EGOS project website.
file_type: documentation
scope: application-website
primary_entity_type: design_guide
primary_entity_name: website_design_guide
tags: [website, design, ui, ux, visual_identity, style_guide]
---

<!-- 
@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - [MQP](../../reference/MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](../../../ROADMAP.md) - Main Project Roadmap
- Process Documentation:
  - [cross_reference_best_practices.md](../../governance/cross_reference_best_practices.md)
-->
  - docs/website/DESIGN_GUIDE.md

**Status:** Initial Draft
**Source Analysis:** `research/EGOS design GROK.txt`, `research/Análise e Refinamento do Projeto EGOS_.txt`, `research/Criaçao de site com IA.txt`, `research/Analise site design.txt`
**Related Plans:** `./DEVELOPMENT_PLAN.md`, `../../../ROADMAP.md`
**Date:** 2025-04-09

**Purpose:** This document outlines the core design directives and visual identity for the EGOS project website, aiming to reflect its unique philosophy of ethical, conscious, modular AI combined with art, beauty, and unconditional love.

---

## 1. Core Philosophy & Tone

* **Tone:** Human, artistic, fluid, democratic, economical, beautiful, loving, transparent, clear, trustworthy, innovative, profound but accessible.
* **Avoid:** Corporate jargon, clichés, hype, fake promises, purely technical or cold language.
* **Goal:** Convey the *spirit* and *soul* of EGOS, fostering connection and understanding, not just fu

## 2. Visual Identity Principles

* **Organic & Fluid:** Inspired by nature, mycelial networks, quantum phenomena. Avoid rigid, overly geometric structures unless they serve a specific conceptual purpose (e.g., representing base code/logic vs. emergent intelligence).
* **Luminous & Ethereal:** Light as a metaphor for consciousness and clarity. Use of gradients, soft glows, and translucency where appropriate.
* **Minimalist Elegance:** Focus on essential information, clean layouts, and purposeful use of space. "Less is more" if it enhances clarity and beauty.
* **Artistic Integration:** Seamlessly blend artistic elements (fractals, generative art, subtle textures) with informative content. Art should not be mere decoration but an integral part of the communication.
* **Conscious Modularity (Visualized):** Design should visually hint at the underlying modular architecture of EGOS without being overly technical. Perhaps through interconnected elements or a sense of building blocks forming a cohesive whole.

## 3. Color Palette (Ref: `colors.json` - TBD, Task: `RESEARCH-COLOR`)

* **Primary:** Deep Indigo/Cosmic Blue (trust, depth, wisdom) - e.g., `#2c3e50` (placeholder)
* **Secondary:** Luminous Teal/Aqua (innovation, clarity, flow) - e.g., `#1abc9c` (placeholder)
* **Accent:** Warm Gold/Amber (love, consciousness, value) - e.g., `#f1c40f` (placeholder)
* **Neutrals:** Soft Grays (e.g., `#ecf0f1`, `#bdc3c7`), Off-Whites (e.g., `#fdfdfd`), and a near-black for text (e.g., `#34495e`).
* **Gradients:** Utilize subtle gradients combining primary, secondary, and accent colors to create depth and a sense of luminosity.
* **Considerations:** High contrast for readability (WCAG AA). Palette should evoke both technological sophistication and organic warmth.

## 4. Typography (Ref: `fonts.json` - TBD, Task: `RESEARCH-FONT`)

* **Headings:** A modern, elegant sans-serif with a touch of personality. (e.g., Montserrat, Raleway, Open Sans - to be researched) - ensure good readability and variety of weights.
* **Body Text:** A highly legible sans-serif or serif font, optimized for screen reading. (e.g., Lato, Merriweather, Source Sans Pro - to be researched).
* **Code Snippets:** A clear monospaced font (e.g., Fira Code, Source Code Pro).
* **Hierarchy:** Establish clear typographic hierarchy using size, weight, and color to guide the user's eye and structure information.

## 5. Layout & Spacing

* **Grid System:** Employ a flexible grid system (e.g., 12-column) for consistent alignment and responsiveness.
* **Whitespace:** Generous use of whitespace (macro and micro) to improve readability, reduce cognitive load, and create a sense of calm and focus.
* **Responsive Design:** Mobile-first approach. Ensure seamless experience across all devices (desktop, tablet, mobile).
* **Modularity in Layout:** Design components (cards, sections, call-to-action blocks) that can be reused and reconfigured across different pages while maintaining visual consistency.

## 6. Iconography & Imagery

* **Iconography:** Custom, minimalist icons that align with the organic/fluid aesthetic. SVG format for scalability. Icons should be intuitive and enhance comprehension.
* **Imagery:** Abstract, generative art, nature-inspired (mycelium, nebulae, fractals), or subtle representations of interconnectedness and consciousness. Avoid generic stock photos. High-quality and optimized for web.
* **Illustrations:** Consider custom illustrations to explain complex EGOS concepts in an accessible and visually appealing way.

## 7. UI Elements (Buttons, Forms, Navigation)

* **Buttons:** Clear visual hierarchy (primary, secondary, tertiary). Subtle hover and active states. Rounded corners for a softer feel.
* **Forms:** Simple, intuitive, and accessible. Clear labels, placeholder text, and validation messages.
* **Navigation:** Intuitive and predictable. Main navigation easily accessible. Consider breadcrumbs for deeper sections. Clear visual distinction for links.

## 8. Key Page/Section Concepts

* **Homepage:** A captivating entry point that immediately communicates EGOS's vision and invites exploration. Balance of art, core message, and clear navigation to key areas.
* **Philosophy/Principles Pages:** Visually serene and contemplative. Use typography and spacing to enhance the gravitas of the content.
* **Subsystems (ATLAS, ETHIK, etc.):** Each subsystem could have a distinct visual motif or color accent within the overall palette, while maintaining consistency. Interactive diagrams to explain architecture and flow.
* **Roadmap:** Visually engaging representation of the project's journey – perhaps a timeline or interactive flow past, present, future.
* **Community Section ("Join the Journey"):
  * Clear calls-to-action for contribution (code, docs, feedback).
  * Explanation of the $ETHIK token system (purpose, earning, utility - Requires clarification).
  * Direct links to GitHub repository, discussions, other community channels.
  * Potentially feature contributor spotlights or recent activity.

## 9. Interactivity & Animation

* **Subtlety:** Animations should be purposeful, enhance understanding, and guide the user, not distract.
* **Examples:**
  * Fade-in/subtle transitions on scroll.
  * Meaningful hover states on cards, links, buttons (e.g., slight scale, color change, revealing info).
  * Interactive diagrams (subsystems, roadmap) responding to user input.
  * Loading indicators for dynamic content.
* **Feedback:** Implement clear visual feedback for user actions (e.g., button clicks, form submissions).
* **Consider:** JS libraries like GSAP for complex animations if needed, but prioritize CSS transitions/animations for performance where possible.

## 10. Accessibility (WCAG AA Target)

* Ensure all design choices (color, typography, layout, interaction) meet WCAG AA guidelines.
* Provide text alternatives for non-text content (e.g., `alt` text for images, descriptions for complex visualizations).
* Ensure keyboard navigability and visible focus states for all interactive elements.
* Design interactive elements and custom visualizations accessibly (Requires research `RESEARCH-WCAG`). Verify with tools like WAVE and Axe.

## 11. Content Strategy Notes (Ref: Task WCS-1)

* Employ storytelling to make philosophical concepts engaging.
* Consider including links to external resources (e.g., UNESCO Ethics of AI) to add depth and credibility.
* Plan for dynamic content updates (Blog/News section via Headless CMS).

---
*This guide provides the initial direction. Visual design prototypes (Figma), UX research (Phase WUX), and technical research (Phase WR) will further refine these concepts.*
