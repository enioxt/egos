---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: project-wide
primary_entity_type: documentation
primary_entity_name: readme
tags: [documentation]
---
---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

---
title: README
version: 1.0.0
status: Active
date_created: 2025-05-10
date_modified: 2025-05-10
authors: [EGOS Team]
description: 
file_type: documentation
scope: 
primary_entity_type: 
primary_entity_name: 
tags: []
---

@references:
<!-- @references: -->
- .windsurfrules
- CODE_OF_CONDUCT.md
- MQP.md
- README.md
- ROADMAP.md
- subsystems/AutoCrossRef/CROSSREF_STANDARD.md

  - [MQP](..\..\reference\MQP.md) - Master Quantum Prompt defining EGOS principles
  - [ROADMAP.md](../../..\..\ROADMAP.md) - Project roadmap and planning
- Other:
  - [MQP](..\..\reference\MQP.md)
  - docs/website/website_README.md



# EGOS Website

This is the official website for the EGOS (Ethical Governance Operating System) project, built with [Next.js](https://nextjs.org) and modern web technologies. The website serves as both documentation and demonstration of EGOS principles and subsystems.

## Features

### Key Features

*   **Core Principles**: Detailed explanations of the 10 EGOS principles.
*   **Modular Subsystems**: Overview of each EGOS subsystem (KOIOS, CRONOS, etc.).
*   **Interactive Roadmap**: View project progress and upcoming features.
*   **System Explorer Visualization**: (In Progress)
    *   Renders a network graph of EGOS components using Sigma.js (`@react-sigma/core`).
    *   Displays nodes representing files/modules and edges for cross-references.
    *   Nodes are colored based on their primary subsystem, with a legend provided.
    *   Features fixed node positions after layout, preventing movement on hover.
    *   Supports zoom and pan for graph exploration.
    *   Hovering over a node displays its label.
    *   Current data source is a static sample (`public/visualizations/static/graph-data.json`).
    *   **Known Issues**: Limited connection data displayed (due to sample data), minor visual flickering effect on hover.
*   **Responsive Design**: Adapts to different screen sizes.

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.




