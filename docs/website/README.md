---
title: EGOS Website README
version: 1.0.0
status: Active
date_created: 2025-05-16
date_modified: 2025-05-16
authors: [EGOS Team, Cascade]
description: Overview and guide for the EGOS project website.
file_type: documentation
scope: apps/website
primary_entity_type: application
primary_entity_name: egos_website
tags: [website, nextjs, react, tailwindcss, documentation]
---

@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- ROADMAP.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - docs/website/README.md

# EGOS Project Website

## Overview

This directory (`apps/website`) contains the source code and configuration for the main EGOS project website. It serves as the primary public-facing interface for the EGOS initiative, providing information, resources, and potentially interactive experiences.

## Tech Stack

-   **Framework:** Next.js (React)
-   **Language:** TypeScript
-   **Styling:** Tailwind CSS
-   **UI Components:** Shadcn/UI (leveraging Radix UI & Lucide Icons) - See [EGOS UI Documentation](../../docs/system/EGOS_UI_Documentation.md)

## Key Features

*(To be populated - e.g., Public information portal, User dashboards, API interaction examples, Documentation access)*

## Development

### Prerequisites

-   Node.js (version as per project's `.nvmrc` or `package.json` engines)
-   npm or yarn (as per project standard)

### Setup & Running Locally

1.  Navigate to the `apps/website` directory:
    ```bash
    cd apps/website
    ```
2.  Install dependencies:
    ```bash
    npm install
    # or
    # yarn install
    ```
3.  Run the development server (typically):
    ```bash
    npm run dev
    # or
    # yarn dev
    ```
    The application should typically be available at `http://localhost:3000`.

## Deployment

*(To be populated - Details about the deployment process, environments, and platforms, or link to a dedicated deployment guide.)*

## Roadmap & Contribution

-   For specific plans and tasks related to this website, see the [Website Roadmap (ROADMAP.md)](ROADMAP.md).
-   For UI/UX standards and component details, refer to the [EGOS UI Documentation](../../docs/system/EGOS_UI_Documentation.md).

## Automated Testing

This website is a target for the project-wide [Automated QA & Site Integrity flow](../../ROADMAP.md#🚀-automated-qa--site-integrity) detailed in the main EGOS project roadmap.