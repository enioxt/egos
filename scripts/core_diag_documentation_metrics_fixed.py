#!/usr/bin/env python3
"""
EGOS Documentation Metrics Dashboard

This script analyzes the documentation ecosystem to generate metrics and insights
about documentation health, coverage, and quality.

Subsystem: KOIOS
Module ID: KOIOS-MTR-001
Status: Active


@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""

import datetime
import glob
import json
import logging
import os
import re
import sys
import math
import numpy as np
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Optional imports for semantic analysis - gracefully handle if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SEMANTIC_ANALYSIS_AVAILABLE = True
except ImportError:
    SEMANTIC_ANALYSIS_AVAILABLE = False
    logging.warning("Semantic analysis libraries not available. Install scikit-learn for enhanced analysis.")

# Try to import the KoiosLogger
try:
    from koios.logger import KoiosLogger
    logger = KoiosLogger("documentation_metrics")
except ImportError:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("documentation_metrics")

from doc_metrics_utils.doc_metrics_config import (
    SUBSYSTEM_COLORS,
    RELATIONSHIP_STYLES,
    SEMANTIC_CONFIG
)

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SCHEMA_PATH = os.path.join(ROOT_DIR, "docs", "schemas", "frontmatter_schema.json")
OUTPUT_DIR = os.path.join(ROOT_DIR, "docs", "metrics")






def parse_args():
    """Parse command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate documentation metrics dashboard"
    )
    parser.add_argument(
        "--output", 
        default=os.path.join(OUTPUT_DIR, "dashboard.html"),
        help="Output HTML file path"
    )
    parser.add_argument(
        "--json", 
        default=os.path.join(OUTPUT_DIR, "metrics.json"),
        help="Output JSON data file path"
    )
    parser.add_argument(
        "--network",
        default=os.path.join(OUTPUT_DIR, "network.html"),
        help="Output HTML network visualization file path"
    )
    parser.add_argument(
        "--semantic",
        default=os.path.join(OUTPUT_DIR, "semantic_analysis.html"),
        help="Output HTML semantic analysis file path"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run integration tests on the documentation system"
    )
    parser.add_argument(
        "--no-semantic",
        action="store_true",
        help="Disable semantic analysis even if libraries are available"
    )
    return parser.parse_args()


def load_schema() -> Dict[str, Any]:
    """Load the JSON schema for frontmatter validation."""
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Error loading schema: %s", e)
        return {}


def find_markdown_files() -> List[str]:
    """Find all Markdown files in the repository."""
    files = []
    
    # Exclude directories
    exclude_dirs = [".git", "venv", "__pycache__", "node_modules"]
    exclude_pattern = r"(/|\\)(" + "|".join(exclude_dirs) + r")(/|\\)"
    
    # Find all markdown files
    for ext in ["md", "mdc"]:
        pattern = os.path.join(ROOT_DIR, "**", f"*.{ext}")
        found = glob.glob(pattern, recursive=True)
        
        # Filter out excluded directories
        files.extend([
            f for f in found 
            if not re.search(exclude_pattern, f)
        ])
    
    return files


def extract_frontmatter(file_path: str) -> Optional[Dict[str, Any]]:
    """Extract YAML frontmatter from a markdown file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Look for frontmatter between --- markers
        frontmatter_match = re.match(r'^---\s*\n([\s\S]*?)\n---\s*\n', content)
        if not frontmatter_match:
            return None

        frontmatter_yaml = frontmatter_match.group(1)
        try:
            data = yaml.safe_load(frontmatter_yaml)
            if not isinstance(data, dict):
                return None
            
            # Add file path to metadata
            data["_file_path"] = file_path
            # Add relative path for display
            data["_rel_path"] = os.path.relpath(file_path, ROOT_DIR)
            
            return data
        except yaml.YAMLError:
            return None
    except Exception:
        return None


def extract_document_content(file_path: str) -> str:
    """Extract text content from a markdown file, excluding frontmatter.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Extracted text content without frontmatter and markdown formatting
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove frontmatter
        content = re.sub(r'^---\s*\n[\s\S]*?\n---\s*\n', '', content)
        
        # Remove markdown formatting (basic cleaning)
        content = re.sub(r'```[\s\S]*?```', '', content)  # Remove code blocks
        content = re.sub(r'\!\[.*?\]\(.*?\)', '', content)  # Remove images
        content = re.sub(r'\[.*?\]\(.*?\)', '\1', content)  # Replace links with text
        content = re.sub(r'[#*_~`]', '', content)  # Remove formatting characters
        
        return content.strip()
    except Exception as e:
        logger.warning(f"Error extracting content from {file_path}: {e}")
        return ""


def calculate_document_similarity(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate similarity between documents using TF-IDF and cosine similarity.
    
    Args:
        documents: List of document metadata dictionaries with content
        
    Returns:
        Dictionary with similarity matrix and related data
    """
    if not SEMANTIC_ANALYSIS_AVAILABLE:
        logger.warning("Semantic analysis libraries not available. Skipping similarity calculation.")
        return {"available": False}
    
    try:
        # Extract document contents and IDs
        doc_contents = []
        doc_ids = []
        doc_titles = []
        doc_paths = []
        
        for doc in documents:
            if "_content" not in doc or not doc["_content"]:
                continue
                
            doc_contents.append(doc["_content"])
            doc_ids.append(doc.get("id", "unknown"))
            doc_titles.append(doc.get("title", "Untitled"))
            doc_paths.append(doc.get("_rel_path", ""))
        
        if not doc_contents:
            return {"available": False}
        
        # Calculate TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(doc_contents)
        
        # Calculate cosine similarity
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Get top terms for each document
        feature_names = vectorizer.get_feature_names_out()
        top_terms = []
        
        for i, doc in enumerate(doc_contents):
            if i >= len(tfidf_matrix.toarray()):
                continue
                
            tfidf_sorting = np.argsort(tfidf_matrix.toarray()[i]).flatten()[::-1]
            top_n = min(5, len(feature_names))  # Get top 5 terms or less
            doc_top_terms = [feature_names[idx] for idx in tfidf_sorting[:top_n]]
            top_terms.append(doc_top_terms)
        
        # Dimensionality reduction for visualization
        if len(doc_contents) > 2:
            try:
                # Use PCA first to reduce to 50 dimensions if we have many documents
                if tfidf_matrix.shape[0] > 50:
                    pca = PCA(n_components=min(50, tfidf_matrix.shape[0] - 1))
                    reduced_features = pca.fit_transform(tfidf_matrix.toarray())
                else:
                    reduced_features = tfidf_matrix.toarray()
                
                # Then use t-SNE to reduce to 2D for visualization
                tsne = TSNE(n_components=2, random_state=42)
                tsne_result = tsne.fit_transform(reduced_features)
                
                # Convert to list for JSON serialization
                tsne_result = tsne_result.tolist()
            except Exception as e:
                logger.warning(f"Error in dimensionality reduction: {e}")
                tsne_result = [[0, 0] for _ in range(len(doc_contents))]
        else:
            # Not enough documents for meaningful reduction
            tsne_result = [[0, 0] for _ in range(len(doc_contents))]
        
        return {
            "available": True,
            "similarity_matrix": similarity_matrix.tolist(),
            "document_ids": doc_ids,
            "document_titles": doc_titles,
            "document_paths": doc_paths,
            "top_terms": top_terms,
            "tsne_coordinates": tsne_result
        }
    except Exception as e:
        logger.error(f"Error calculating document similarity: {e}")
        return {"available": False}


def cluster_documents(documents: List[Dict[str, Any]], similarity_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cluster documents based on content similarity.
    
    Args:
        documents: List of document metadata dictionaries
        similarity_data: Output from calculate_document_similarity
        
    Returns:
        Dictionary with clustering results
    """
    if not SEMANTIC_ANALYSIS_AVAILABLE or not similarity_data.get("available", False):
        return {"available": False}
    
    try:
        # Extract the TSNE coordinates for clustering
        tsne_coordinates = np.array(similarity_data["tsne_coordinates"])
        
        if len(tsne_coordinates) < 3:  # Need at least 3 documents for meaningful clustering
            return {"available": False}
        
        # Determine optimal number of clusters (simplified method)
        max_clusters = min(10, len(tsne_coordinates) - 1)  # Max 10 clusters or n-1, whichever is smaller
        
        if max_clusters < 2:  # Need at least 2 clusters
            return {"available": False}
        
        # Use KMeans for clustering
        n_clusters = min(5, max_clusters)  # Default to 5 clusters or fewer if we don't have enough documents
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(tsne_coordinates).tolist()
        
        # Try DBSCAN as an alternative clustering method
        try:
            dbscan = DBSCAN(eps=0.5, min_samples=2)
            dbscan_labels = dbscan.fit_predict(tsne_coordinates).tolist()
            
            # Count number of clusters in DBSCAN result (excluding noise points labeled as -1)
            dbscan_clusters = len(set([x for x in dbscan_labels if x >= 0]))
            
            # If DBSCAN found a reasonable number of clusters, use it instead
            if 1 < dbscan_clusters < n_clusters:
                cluster_labels = dbscan_labels
        except Exception:
            # Fall back to KMeans results if DBSCAN fails
            pass
        
        # Map documents to clusters
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if i < len(similarity_data["document_ids"]):
                doc_id = similarity_data["document_ids"][i]
                doc_title = similarity_data["document_titles"][i]
                doc_path = similarity_data["document_paths"][i]
                
                clusters[str(label)].append({
                    "id": doc_id,
                    "title": doc_title,
                    "path": doc_path
                })
        
        # Extract top terms for each cluster
        cluster_terms = {}
        doc_id_to_index = {doc_id: i for i, doc_id in enumerate(similarity_data["document_ids"])}
        
        for label, docs in clusters.items():
            # Skip noise cluster from DBSCAN (labeled as -1)
            if label == "-1":
                continue
                
            # Collect all top terms from documents in this cluster
            all_terms = []
            for doc in docs:
                if doc["id"] in doc_id_to_index:
                    idx = doc_id_to_index[doc["id"]]
                    if idx < len(similarity_data["top_terms"]):
                        all_terms.extend(similarity_data["top_terms"][idx])
            
            # Count term frequencies and get top 5
            term_counter = Counter(all_terms)
            top_cluster_terms = [term for term, _ in term_counter.most_common(5)]
            cluster_terms[label] = top_cluster_terms
        
        return {
            "available": True,
            "cluster_labels": cluster_labels,
            "clusters": dict(clusters),  # Convert defaultdict to dict for JSON serialization
            "cluster_terms": cluster_terms
        }
    except Exception as e:
        logger.error(f"Error clustering documents: {e}")
        return {"available": False}


def analyze_documentation_coverage(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze documentation coverage across subsystems and document types.
    
    Args:
        documents: List of document metadata dictionaries
        
    Returns:
        Dictionary with coverage metrics
    """
    # Initialize coverage metrics
    coverage = {
        "subsystems": defaultdict(int),
        "doc_types": defaultdict(int),
        "subsystem_types": defaultdict(lambda: defaultdict(int)),
        "completion_status": defaultdict(int),
        "last_updated": defaultdict(list),
        "coverage_score": {}
    }
    
    # Required document types per subsystem (simplified example)
    required_docs = {
        "KOIOS": ["architecture", "user_guide", "api_reference", "tutorial"],
        "CRONOS": ["architecture", "user_guide", "api_reference"],
        "HARMONY": ["architecture", "user_guide", "integration_guide"],
        "ETHIK": ["architecture", "user_guide", "principles"],
        "NEXUS": ["architecture", "user_guide", "api_reference", "tutorial"],
        "MYCELIUM": ["architecture", "user_guide", "api_reference", "protocol_spec"],
        "CORUJA": ["architecture", "user_guide", "api_reference"]
    }
    
    # Count documents by subsystem and type
    for doc in documents:
        subsystem = doc.get("subsystem", "Unknown")
        doc_type = doc.get("type", "Unknown")
        status = doc.get("status", "Unknown")
        last_updated = doc.get("last_updated", None)
        
        coverage["subsystems"][subsystem] += 1
        coverage["doc_types"][doc_type] += 1
        coverage["subsystem_types"][subsystem][doc_type] += 1
        coverage["completion_status"][status] += 1
        
        if last_updated:
            coverage["last_updated"][subsystem].append({
                "date": last_updated,
                "title": doc.get("title", "Untitled"),
                "path": doc.get("_rel_path", "")
            })
    
    # Calculate coverage scores for each subsystem
    for subsystem, required in required_docs.items():
        if subsystem not in coverage["subsystem_types"]:
            coverage["coverage_score"][subsystem] = 0
            continue
            
        available_types = coverage["subsystem_types"][subsystem].keys()
        matched = sum(1 for doc_type in required if doc_type in available_types)
        score = (matched / len(required)) * 100 if required else 0
        coverage["coverage_score"][subsystem] = round(score, 1)
    
    # Convert defaultdicts to regular dicts for JSON serialization
    coverage["subsystems"] = dict(coverage["subsystems"])
    coverage["doc_types"] = dict(coverage["doc_types"])
    coverage["subsystem_types"] = {k: dict(v) for k, v in coverage["subsystem_types"].items()}
    coverage["completion_status"] = dict(coverage["completion_status"])
    coverage["last_updated"] = dict(coverage["last_updated"])
    
    return coverage


