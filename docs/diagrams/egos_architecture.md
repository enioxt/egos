@references:
  - docs/diagrams/egos_architecture.md

```mermaid
graph TB
    classDef core fill:#f9d5e5,stroke:#333,stroke-width:2px
    classDef ethics fill:#d5eff9,stroke:#333,stroke-width:2px
    classDef integration fill:#e3f9d5,stroke:#333,stroke-width:2px
    classDef user fill:#f9f3d5,stroke:#333,stroke-width:2px
    
    %% Core System Components
    EGOS[EGOS Core System]:::core
    
    %% Ethical Components
    ATRIAN[ATRiAN Module<br>Ethical Core]:::ethics
    ETHIK[ETHIK Framework<br>Ethical Principles]:::ethics
    DEV[Distributed Ethical<br>Validator (DEV)]:::ethics
    
    %% Integration Components
    EAAS[Ethics as a Service<br>API]:::integration
    BLOCKCHAIN[Blockchain Integration<br>$ETHIK Token]:::integration
    DASHBOARD[Dashboard System]:::user
    WEBSITE[Project Website]:::user
    WORKFLOWS[Standardized Workflows]:::integration
    
    %% Relationships
    EGOS --> ATRIAN
    EGOS --> ETHIK
    EGOS --> DEV
    
    ATRIAN --> EAAS
    ATRIAN --- ETHIK
    
    DEV --- BLOCKCHAIN
    DEV --- ETHIK
    
    EAAS --- DASHBOARD
    BLOCKCHAIN --- DASHBOARD
    
    WEBSITE --- DASHBOARD
    WEBSITE --- EAAS
    
    WORKFLOWS --- EGOS
    
    %% External Interactions
    USER[Users & Systems]:::user
    API_CONSUMERS[API Consumers]:::user
    
    USER --- WEBSITE
    USER --- DASHBOARD
    API_CONSUMERS --- EAAS
    
    %% Use Cases
    HEALTHCARE[Healthcare AI]:::user
    FINANCE[Financial Services]:::user
    CONTENT[Content Moderation]:::user
    GOVERNMENT[Public Sector AI]:::user
    RESEARCH[Research Oversight]:::user
    
    EAAS --- HEALTHCARE
    EAAS --- FINANCE
    EAAS --- CONTENT
    EAAS --- GOVERNMENT
    EAAS --- RESEARCH
```