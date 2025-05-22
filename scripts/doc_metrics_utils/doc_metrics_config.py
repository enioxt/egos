# c:\EGOS\scripts\doc_metrics_utils\doc_metrics_config.py
"""Configuration constants for the EGOS Documentation Metrics Dashboard.

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

# Color schemes for network visualization
SUBSYSTEM_COLORS = {
    "KOIOS": "#3f51b5",  # Documentation system
    "CRONOS": "#009688",  # Time-related
    "HARMONY": "#4caf50",  # Integration
    "ETHIK": "#ff9800",  # Ethics system
    "NEXUS": "#e91e63",  # Core system
    "MYCELIUM": "#673ab7",  # Communication
    "AETHER": "#03a9f4",  # Environment/Deployment
    "ORION": "#8bc34a",   # User Interface / UX
    "LYRA": "#ffc107",    # AI / ML Models
    "ZENITH": "#9c27b0",  # Overall project / Meta
    "GENESIS": "#795548", # Data / Persistence
    "AEGIS": "#f44336",   # Security
    "KAIROS": "#2196f3",  # Build/CI/CD
    "IRIS": "#607d8b",    # Monitoring / Logging
    "Unknown": "#9e9e9e"  # Default for unknown
}

RELATIONSHIP_STYLES = {
    "mentions": {"color": "#2196f3", "style": "solid"},       # General mention
    "links_to": {"color": "#4caf50", "style": "solid"},       # Hyperlink
    "references": {"color": "#ff9800", "style": "dashed"},    # Code reference
    "depends_on": {"color": "#e91e63", "style": "dotted"},    # Dependency
    "relates_to": {"color": "#00bcd4", "style": "solid"},     # Generic relation
    "parent_of": {"color": "#8bc34a", "style": "solid"},      # Parent-child
    "child_of": {"color": "#8bc34a", "style": "solid"},       # Child-parent
    "see_also": {"color": "#673ab7", "style": "dashed"},      # Suggests further reading
    "uses_service": {"color": "#00796b", "style": "dotted"},  # Service usage
    "provides_service": {"color": "#c2185b", "style": "dotted"},# Service provision
    "unknown": {"color": "#9e9e9e", "style": "dashed"}        # Default for unknown
}

# Configuration for semantic analysis
SEMANTIC_CONFIG = {
    "tfidf_max_features": 5000,
    "kmeans_n_clusters": 10,  # Adjust based on expected number of topics
    "dbscan_eps": 0.5,
    "dbscan_min_samples": 3,
    "pca_n_components": 2,    # For 2D visualization
    "tsne_n_components": 2,   # For 2D visualization
    "tsne_perplexity": 30,
    "similarity_threshold": 0.1 # Threshold for considering documents similar
}
