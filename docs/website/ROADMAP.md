---
title: EGOS Website Roadmap
version: 1.1.0
status: Active
date_created: 2025-05-16
date_modified: 2025-05-19
authors: [EGOS Team, Cascade]
description: Specific roadmap for the EGOS project website, including detailed tasks and initiatives.
file_type: documentation
scope: apps/website
primary_entity_type: documentation
primary_entity_name: website_roadmap
tags: [website, planning, roadmap, feature-set, visualization, backlog]
---

@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - docs/website/ROADMAP.md

# EGOS Website Roadmap

**Status:** Active
**Last Updated:** 2025-05-19

This document outlines the development roadmap, planned features, and ongoing tasks specifically for the EGOS project website located in `apps/website`. It complements the [Main EGOS Project Roadmap](../../ROADMAP.md).

## Vision & Goals

*(To be populated - e.g., "To be the premier, accessible, and informative public portal for the EGOS initiative, showcasing its capabilities and fostering community engagement.")*

## Primary References
- [Master Quantum Prompt (MQP)](../../../core/MQP.md)
- [Roadmap Standardization Guidelines](../../docs/process/roadmap_standardization.md) <!-- Adjust path if necessary -->

## Legend

-   **Status:** To Do | In Progress | Done | Blocked
-   **Subsystem[s]:** Frontend | Backend | UI/UX | Infra | Docs | Core | etc.
-   **Task ID:** Unique identifier (e.g., WEB-001)
-   **Priority:** Critical | High | Medium | Low
-   **Description:** Clear description of the task.
-   **Dependencies:** Any blocking tasks (Task IDs).
-   **Principles:** Relevant EGOS principles (e.g., Modularity, Accessibility).

## Current Major Initiatives

### 1. Ensuring Comprehensive QA Coverage
    - **Description:** Actively support and integrate with the project-wide "Automated QA & Site Integrity" flow (see [Main EGOS Roadmap Tasks QA-FLOW-001 to QA-FLOW-005](../../ROADMAP.md#🚀-automated-qa--site-integrity)).
    - **Objective:** Ensure all critical user paths, functionalities, and content on this website are continuously tested.
    - **Key Tasks:**
        - Identify and document critical user flows and API endpoints specific to the website for inclusion in the QA suite.
        - Prioritize and address bugs identified by the QA flow that impact website stability, usability, or content accuracy.

### 2. Foundation & Initial Feature Set Implementation
    - **Description:** Develop and launch the core features required for the website's initial operational capability.
    - **Status:** Planning / In Progress

    #### 2.1. Landing Page & Core Setup

    | Status | Subsystem[s] | Task ID | Priority | Description                                                                                                | Dependencies | Principles                |
    | :----- | :----------- | :------ | :------- | :--------------------------------------------------------------------------------------------------------- | :----------- | :------------------------ |
    | Done   | Frontend, UI/UX | WEB-001 | Critical | Migrate core landing page components (Header, Hero, Principles, Subsystems, CTA, Footer) from `lovable` project. | -            | Modularity, Preservation |
    | Done   | Frontend, UI/UX | WEB-002 | High     | Set up Shadcn/UI and Tailwind CSS configuration.                                                        | -            | Modularity                |
    | Done   | Frontend, UI/UX | WEB-003 | High     | Integrate migrated components into the main landing page (`src/app/page.tsx`).                             | WEB-001      | Modularity                |
    | Done   | Frontend, UI/UX | WEB-005 | High     | Fix SVG components and animations for visual elements.                                                   | WEB-002      | Universal Accessibility  |
    | Done   | Frontend, UI/UX | WEB-004 | Medium   | Test and verify the appearance and functionality of the landing page components.                           | WEB-003      | Integrated Ethics        |
    | To Do  | Frontend, I18n | WEB-006 | Low      | Implementar suporte a internacionalização (i18n) para português e inglês.                                  | WEB-004      | Universal Accessibility  |

    #### 2.2. Cross-Reference Network Visualization

    | Status | Subsystem[s] | Task ID | Priority | Description | Dependencies | Principles |
    | :----- | :----------- | :------ | :------- | :---------- | :----------- | :--------- |
    | Done | Frontend, UI/UX | VIS-INT-001 | High | Refactor System Explorer to use @react-sigma/core for better structure and modularity | - | Conscious Modularity |
    | Done | Frontend, UI/UX | VIS-INT-002 | High | Implement proper layout with fixed header and content spacing | VIS-INT-001 | Universal Accessibility |
    | Done | Frontend, UI/UX | VIS-INT-003 | Medium | Add zoom and fullscreen controls to the visualization | VIS-INT-001 | Universal Accessibility |
    | In Progress | Frontend, UI/UX | VIS-INT-004 | Medium | Improve node hover behavior and visual appearance | VIS-INT-001 | Universal Accessibility |
    | To Do | Frontend, UI/UX | VIS-INT-005 | Medium | Add legend for subsystem colors | VIS-INT-001 | Universal Accessibility |
    | To Do | Frontend, Data | VIS-INT-006 | High | Integrate complete cross-reference data | VIS-INT-001 | Systemic Cartography |
    | Done   | Frontend, KOIOS | VIS-001 | High | Integrate Sigma.js visualization component for the cross-reference network | WEB-003 | Conscious Modularity, Systemic Cartography |
    | Done   | Frontend, KOIOS | VIS-002 | High | Create dynamic graph data handling and force-directed layout | VIS-001 | Systemic Cartography |
    | Done   | Frontend, UI/UX | VIS-003 | Medium | Design and implement visualization homepage section with preview | VIS-001 | Integrated Ethics, Universal Accessibility |
    | Done   | Documentation | VIS-004 | Medium | Document the visualization implementation and components | VIS-001, VIS-002 | Reciprocal Trust, Evolutionary Preservation |
    | To Do  | Frontend, UI/UX | VIS-005 | Medium | Add filtering capabilities by subsystem, file type, and reference count | VIS-002 | Universal Accessibility |
    | To Do  | Frontend, UX | VIS-006 | Low | Implement search functionality within the visualization | VIS-002 | Universal Accessibility |
    | To Do  | Frontend, Performance | VIS-007 | Low | Optimize visualization for large datasets with WebGL rendering | VIS-002 | Universal Accessibility, Conscious Modularity |
    | To Do  | Frontend, MYCELIUM | VIS-008 | Medium | Implement cross-references between website content sections | VIS-003 | Conscious Modularity, Systemic Cartography |

### 3. Detailed Planned Tasks & Enhancements (Backlog)

*   **VIS-006**: Implement Search Functionality for Visualization
    *   **Description**: Add search input to highlight nodes, potentially with connected node highlighting.
    *   **Status**: Planned (Deferred)
    *   **Priority**: Medium
    *   **Effort**: Medium
    *   **References**: `website/src/app/system-explorer/visualization/page.tsx`
*   **VIS-007**: Optimize Visualization for Large Datasets
    *   **Description**: Implement performance enhancements like WebGL rendering, progressive loading, optimized layouts.
    *   **Status**: Planned (Deferred)
    *   **Priority**: Medium
    *   **Effort**: Large
    *   **References**: `website/src/components/SystemGraph.tsx`, `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-iii-a`
*   **VIS-008**: Implement Website Cross-References
    *   **Description**: Create meaningful `mdc:` links between different content sections (docs, principles, blog) to enhance navigation and reflect MYCELIUM interconnection.
    *   **Status**: Planned (Deferred)
    *   **Priority**: Medium
    *   **Effort**: Medium
    *   **References**: `research/Aprimorando o site EGOS_.txt`
*   **WEB-GEN-001**: Replace Placeholder Visualization Image
    *   **Description**: Capture a screenshot of the actual, working visualization and replace the placeholder SVG used in previews (e.g., homepage).
    *   **Status**: Planned (Deferred)
    *   **Priority**: Low
    *   **Effort**: Small
*   **WEB-DESIGN-001**: Refine Dark Mode Palette & Contrast
    *   **Description**: Enhance the dark mode theme focusing on WCAG 2.2 AA contrast, strategic accent color use, and overall visual coherence, reflecting EGOS principles.
    *   **Status**: ⏳ In Progress (Initial palette defined)
    *   **Priority**: High
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-ii-a`
*   **WEB-DESIGN-002**: Evaluate & Refine Website Typography
    *   **Description**: Assess current fonts for legibility in dark mode. Implement `text-wrap: balance` / `pretty`. Ensure clear typographic hierarchy.
    *   **Status**: Planned
    *   **Priority**: Medium
    *   **Effort**: Small
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-ii-a`
*   **WEB-DESIGN-003**: Review & Enhance Iconography
    *   **Description**: Ensure consistency, clarity, and semantic meaning of SVG icons. Consider subtle microinteractions for interactive icons.
    *   **Status**: Planned
    *   **Priority**: Low
    *   **Effort**: Small
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-ii-a`
*   **WEB-VIZ-002**: Evaluate Alternatives for System Explorer Visualization
    *   **Description**: Research and compare alternative WebGL libraries (Ogma, KeyLines, Cytoscape.js, react-force-graph) against Sigma.js v3 for visualizing the complex EGOS structure, considering performance, features (3D, layouts), and licensing.
    *   **Status**: Planned
    *   **Priority**: Medium
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-iii-a`
*   **WEB-VIZ-003**: Design Visual Metaphors for Ethical Principles
    *   **Description**: Develop abstract visual representations (icons, shapes) for core EGOS ethical principles, ensuring they are used contextually with clear explanations.
    *   **Status**: Planned
    *   **Priority**: Medium
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-iii-b`
*   **WEB-UX-001**: Implement Functional Microinteractions
    *   **Description**: Add subtle, performant microinteractions for feedback (hovers, clicks, loading states, form validation) prioritizing clarity and accessibility.
    *   **Status**: Planned
    *   **Priority**: Medium
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-iv-a`
*   **WEB-UX-002**: Implement Performant Animations & Transitions
    *   **Description**: Introduce subtle scroll effects or page transitions, focusing on performance (CSS transforms/opacity, `prefers-reduced-motion`).
    *   **Status**: Planned
    *   **Priority**: Low
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-iv-b`
*   **WEB-AI-001**: Plan Ethical AI-Powered Search/Q&A
    *   **Description**: Research and design an ethical AI-enhanced search or Q&A feature for the website, considering data privacy and transparency.
    *   **Status**: Planned
    *   **Priority**: Low
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-v-a`
*   **WEB-A11Y-001**: Conduct WCAG 2.2 Accessibility Audit
    *   **Description**: Perform a thorough audit of the website against WCAG 2.2 guidelines, covering semantic HTML, ARIA, keyboard navigation, contrast, etc. Document findings and create remediation tasks.
    *   **Status**: ⏳ In Progress (Starting preliminary checks)
    *   **Priority**: High
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-vi-b`
*   **WEB-SEC-001**: Implement Robust Content Security Policy (CSP)
    *   **Description**: Define and implement a strict CSP, potentially using nonces, to mitigate XSS risks. Address challenges specific to Next.js implementation.
    *   **Status**: Planned
    *   **Priority**: High
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-vi-c`
*   **WEB-PRIV-001**: Implement Privacy-First Analytics
    *   **Description**: Replace or supplement existing analytics with a privacy-respecting solution (e.g., Plausible, Fathom, self-hosted PostHog). Ensure ethical data collection practices.
    *   **Status**: Planned
    *   **Priority**: High
    *   **Effort**: Medium
    *   **References**: `strategic-thinking/research/Aprimorando o site EGOS_.txt#section-vi-d` <!-- Corrected reference based on common patterns -->

## Bug Fixes & Technical Debt

*(This section will be populated with specific bugs identified, including those from the automated QA flow, and technical debt items.)*

---
*This roadmap is for the `apps/website` component of the EGOS project.*