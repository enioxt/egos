"""NEXUS Dependency Mapper Integration for File Reference Checker Ultra

This module provides integration with the NEXUS subsystem for enhancing
dependency analysis with cross-reference data and providing insights into system relationships.

@references: <!-- TO_BE_REPLACED -->, NEXUS dependency analysis standards
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import logging
import json
import uuid
import requests
import networkx as nx
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger("cross_reference_integration.nexus")

class NEXUSDependencyMapper:
    """
    Integrates with NEXUS subsystem to enhance dependency analysis with cross-reference data.
    
    This class provides methods for converting cross-references into dependency relationships,
    identifying potential impacts of changes, and generating visualizations of reference relationships.
    """
    
    def __init__(
        self, 
        dependency_mapping: bool = True,
        impact_analysis: bool = True,
        visualization: bool = True,
        api_endpoint: str = "http://localhost:8003/nexus/analyze",
        timeout_sec: int = 60
    ):
        """
        Initialize the NEXUS Dependency Mapper.
        
        Args:
            dependency_mapping: Whether to enable dependency mapping
            impact_analysis: Whether to enable impact analysis
            visualization: Whether to enable visualization generation
            api_endpoint: NEXUS API endpoint for dependency analysis
            timeout_sec: API request timeout in seconds
        """
        self.dependency_mapping = dependency_mapping
        self.impact_analysis = impact_analysis
        self.visualization = visualization
        self.api_endpoint = api_endpoint
        self.timeout_sec = timeout_sec
        self.dependency_graph = nx.DiGraph()
        logger.info(f"NEXUS Dependency Mapper initialized with features: " +
                   f"mapping={dependency_mapping}, impact_analysis={impact_analysis}, " +
                   f"visualization={visualization}")
    
    def map_dependency(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a reference to a dependency relationship.
        
        Args:
            reference_data: Reference data in standardized format
            
        Returns:
            Dependency mapping result in standardized format
        """
        reference_id = str(uuid.uuid4())
        source_file = reference_data.get("source_file", "")
        target_file = reference_data.get("target_file", "")
        reference_type = reference_data.get("reference_type", "")
        
        logger.debug(f"Mapping dependency from {source_file} to {target_file}")
        
        # Prepare dependency mapping result structure
        mapping_result = {
            "reference_id": reference_id,
            "validation_status": "valid",
            "validation_messages": [],
            "validator": "NEXUS",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "dependency_type": self._determine_dependency_type(reference_data),
                "dependency_strength": self._calculate_dependency_strength(reference_data),
                "impact_level": "none"
            }
        }
        
        try:
            # Try to connect to NEXUS API if available
            if self._is_api_available():
                api_result = self._call_nexus_api(reference_data)
                if api_result:
                    return api_result
            
            # Fallback to local dependency mapping if API is unavailable
            if self.dependency_mapping:
                mapping_result = self._perform_local_dependency_mapping(reference_data, mapping_result)
            
            # Perform impact analysis if enabled
            if self.impact_analysis:
                mapping_result = self._perform_impact_analysis(reference_data, mapping_result)
            
        except Exception as e:
            logger.error(f"Error during NEXUS dependency mapping: {str(e)}")
            mapping_result["validation_status"] = "warning"
            mapping_result["validation_messages"].append({
                "level": "warning",
                "code": "NXS-ERR-001",
                "message": f"Dependency mapping error: {str(e)}",
                "suggestion": "Review dependency manually"
            })
        
        return mapping_result
    
    def _is_api_available(self) -> bool:
        """Check if the NEXUS API is available."""
        try:
            response = requests.get(
                f"{self.api_endpoint}/health", 
                timeout=self.timeout_sec
            )
            return response.status_code == 200
        except:
            logger.warning("NEXUS API is not available, falling back to local dependency mapping")
            return False
    
    def _call_nexus_api(self, reference_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call the NEXUS API for dependency analysis.
        
        Args:
            reference_data: Reference data to analyze
            
        Returns:
            Dependency analysis result from API or None if API call fails
        """
        try:
            payload = {
                "reference": reference_data,
                "options": {
                    "dependency_mapping": self.dependency_mapping,
                    "impact_analysis": self.impact_analysis,
                    "visualization": self.visualization
                }
            }
            
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=self.timeout_sec
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"NEXUS API returned status code {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling NEXUS API: {str(e)}")
            return None
    
    def _perform_local_dependency_mapping(
        self, 
        reference_data: Dict[str, Any], 
        mapping_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform local dependency mapping when API is unavailable.
        
        Args:
            reference_data: Reference data to map
            mapping_result: Initial dependency mapping result structure
            
        Returns:
            Updated dependency mapping result
        """
        source_file = reference_data.get("source_file", "")
        target_file = reference_data.get("target_file", "")
        reference_type = reference_data.get("reference_type", "")
        
        if not source_file or not target_file:
            mapping_result["validation_status"] = "warning"
            mapping_result["validation_messages"].append({
                "level": "warning",
                "code": "NXS-MAP-001",
                "message": "Missing source or target file for dependency mapping",
                "suggestion": "Ensure both source and target files are specified"
            })
            return mapping_result
        
        # Add nodes and edge to dependency graph
        self.dependency_graph.add_node(source_file, type="source")
        self.dependency_graph.add_node(target_file, type="target")
        
        # Add edge with attributes
        dependency_type = self._determine_dependency_type(reference_data)
        dependency_strength = self._calculate_dependency_strength(reference_data)
        
        self.dependency_graph.add_edge(
            source_file, 
            target_file, 
            type=dependency_type,
            strength=dependency_strength,
            reference_type=reference_type
        )
        
        # Update mapping result with dependency information
        mapping_result["metadata"]["dependency_type"] = dependency_type
        mapping_result["metadata"]["dependency_strength"] = dependency_strength
        
        # Check for circular dependencies
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            if cycles:
                mapping_result["validation_status"] = "warning"
                mapping_result["validation_messages"].append({
                    "level": "warning",
                    "code": "NXS-CYC-001",
                    "message": f"Circular dependency detected: {' -> '.join(cycles[0])}",
                    "suggestion": "Review and refactor to eliminate circular dependencies"
                })
                mapping_result["metadata"]["circular_dependency"] = True
        except:
            # Simple cycles might not work on incomplete graphs
            pass
        
        return mapping_result
    
    def _perform_impact_analysis(
        self, 
        reference_data: Dict[str, Any], 
        mapping_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform impact analysis for a reference.
        
        Args:
            reference_data: Reference data to analyze
            mapping_result: Dependency mapping result to update
            
        Returns:
            Updated dependency mapping result with impact analysis
        """
        source_file = reference_data.get("source_file", "")
        target_file = reference_data.get("target_file", "")
        
        if not source_file or not target_file or not self.dependency_graph:
            return mapping_result
        
        # Calculate impact metrics
        impact_level = "none"
        impact_scope = []
        
        try:
            # Calculate downstream impact (files affected by changes to target_file)
            if target_file in self.dependency_graph:
                downstream = list(nx.descendants(self.dependency_graph, target_file))
                if downstream:
                    impact_scope.extend(downstream)
                    
                    # Determine impact level based on number of affected files
                    if len(downstream) > 10:
                        impact_level = "high"
                    elif len(downstream) > 5:
                        impact_level = "medium"
                    elif len(downstream) > 0:
                        impact_level = "low"
            
            # Update mapping result with impact analysis
            mapping_result["metadata"]["impact_level"] = impact_level
            mapping_result["metadata"]["impact_scope"] = impact_scope[:10]  # Limit to 10 files
            mapping_result["metadata"]["impact_count"] = len(impact_scope)
            
            # Add impact warning if significant
            if impact_level in ["medium", "high"]:
                mapping_result["validation_status"] = "warning"
                mapping_result["validation_messages"].append({
                    "level": "warning",
                    "code": "NXS-IMP-001",
                    "message": f"{impact_level.capitalize()} impact level: Changes may affect {len(impact_scope)} files",
                    "suggestion": "Review downstream dependencies before making changes"
                })
        
        except Exception as e:
            logger.error(f"Error during impact analysis: {str(e)}")
        
        return mapping_result
    
    def _determine_dependency_type(self, reference_data: Dict[str, Any]) -> str:
        """
        Determine the type of dependency based on reference data.
        
        Args:
            reference_data: Reference data to analyze
            
        Returns:
            Dependency type ("import", "documentation", "data", "configuration", "other")
        """
        reference_type = reference_data.get("reference_type", "")
        source_file = reference_data.get("source_file", "")
        target_file = reference_data.get("target_file", "")
        context = reference_data.get("context", "")
        
        # Default to "other"
        dependency_type = "other"
        
        # Check file extensions
        source_ext = Path(source_file).suffix.lower() if source_file else ""
        target_ext = Path(target_file).suffix.lower() if target_file else ""
        
        # Determine dependency type based on reference type and file extensions
        if reference_type == "import":
            dependency_type = "import"
        elif source_ext in [".md", ".rst", ".txt"] or target_ext in [".md", ".rst", ".txt"]:
            dependency_type = "documentation"
        elif source_ext in [".json", ".yaml", ".yml", ".csv", ".xml"] or target_ext in [".json", ".yaml", ".yml", ".csv", ".xml"]:
            dependency_type = "data"
        elif source_ext in [".ini", ".conf", ".config", ".env"] or target_ext in [".ini", ".conf", ".config", ".env"]:
            dependency_type = "configuration"
        
        return dependency_type
    
    def _calculate_dependency_strength(self, reference_data: Dict[str, Any]) -> float:
        """
        Calculate the strength of a dependency based on reference data.
        
        Args:
            reference_data: Reference data to analyze
            
        Returns:
            Dependency strength (0.0 to 1.0)
        """
        reference_type = reference_data.get("reference_type", "")
        context = reference_data.get("context", "")
        
        # Base strength by reference type
        base_strength = {
            "import": 0.8,
            "mention": 0.4,
            "link": 0.6,
            "include": 0.7,
            "require": 0.9
        }.get(reference_type, 0.5)
        
        # Adjust strength based on context
        if context:
            # Strong dependency indicators
            strong_indicators = ["required", "depends", "must", "critical", "essential"]
            # Weak dependency indicators
            weak_indicators = ["optional", "may", "might", "can", "alternative"]
            
            # Check for indicators in context
            for indicator in strong_indicators:
                if indicator.lower() in context.lower():
                    base_strength = min(base_strength + 0.2, 1.0)
                    break
                    
            for indicator in weak_indicators:
                if indicator.lower() in context.lower():
                    base_strength = max(base_strength - 0.2, 0.1)
                    break
        
        return round(base_strength, 2)
    
    def process_references_batch(self, references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of references to build a comprehensive dependency graph.
        
        Args:
            references: List of reference data in standardized format
            
        Returns:
            Dependency analysis results including graph metrics
        """
        # Process each reference
        mapping_results = []
        for reference in references:
            mapping_results.append(self.map_dependency(reference))
        
        # Calculate graph metrics
        metrics = self._calculate_graph_metrics()
        
        # Generate visualization if enabled
        visualization_data = None
        if self.visualization:
            visualization_data = self._generate_visualization_data()
        
        # Compile batch results
        return {
            "batch_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "reference_count": len(references),
            "mapping_results": mapping_results,
            "graph_metrics": metrics,
            "visualization_data": visualization_data
        }
    
    def _calculate_graph_metrics(self) -> Dict[str, Any]:
        """
        Calculate metrics for the dependency graph.
        
        Returns:
            Dictionary of graph metrics
        """
        if not self.dependency_graph or self.dependency_graph.number_of_nodes() == 0:
            return {
                "node_count": 0,
                "edge_count": 0,
                "density": 0.0,
                "connected_components": 0,
                "average_clustering": 0.0,
                "average_shortest_path": 0.0
            }
        
        try:
            # Basic metrics
            node_count = self.dependency_graph.number_of_nodes()
            edge_count = self.dependency_graph.number_of_edges()
            density = nx.density(self.dependency_graph)
            
            # Connected components
            undirected = self.dependency_graph.to_undirected()
            connected_components = nx.number_connected_components(undirected)
            
            # Clustering coefficient (only for undirected graph)
            average_clustering = nx.average_clustering(undirected)
            
            # Average shortest path (only if graph is connected)
            average_shortest_path = 0.0
            if connected_components == 1 and node_count > 1:
                average_shortest_path = nx.average_shortest_path_length(undirected)
            
            return {
                "node_count": node_count,
                "edge_count": edge_count,
                "density": round(density, 4),
                "connected_components": connected_components,
                "average_clustering": round(average_clustering, 4),
                "average_shortest_path": round(average_shortest_path, 4) if average_shortest_path > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating graph metrics: {str(e)}")
            return {
                "node_count": self.dependency_graph.number_of_nodes(),
                "edge_count": self.dependency_graph.number_of_edges(),
                "error": str(e)
            }
    
    def _generate_visualization_data(self) -> Dict[str, Any]:
        """
        Generate visualization data for the dependency graph.
        
        Returns:
            Visualization data in a format suitable for rendering
        """
        if not self.dependency_graph or self.dependency_graph.number_of_nodes() == 0:
            return {
                "nodes": [],
                "edges": []
            }
        
        # Convert graph to visualization format
        nodes = []
        edges = []
        
        # Add nodes
        for node in self.dependency_graph.nodes():
            node_type = self.dependency_graph.nodes[node].get("type", "unknown")
            nodes.append({
                "id": node,
                "label": Path(node).name,
                "type": node_type,
                "group": self._get_node_group(node)
            })
        
        # Add edges
        for source, target, data in self.dependency_graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": data.get("type", "other"),
                "strength": data.get("strength", 0.5)
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _get_node_group(self, node_path: str) -> str:
        """
        Determine the group for a node based on its path or extension.
        
        Args:
            node_path: Path of the node
            
        Returns:
            Group name for visualization
        """
        if not node_path:
            return "unknown"
        
        path = Path(node_path)
        extension = path.suffix.lower()
        
        # Group by extension
        if extension in [".py", ".pyc", ".pyd", ".pyo", ".pyw"]:
            return "python"
        elif extension in [".js", ".jsx", ".ts", ".tsx"]:
            return "javascript"
        elif extension in [".md", ".rst", ".txt"]:
            return "documentation"
        elif extension in [".json", ".yaml", ".yml", ".xml"]:
            return "data"
        elif extension in [".ini", ".conf", ".config", ".env"]:
            return "configuration"
        elif extension in [".html", ".htm", ".css", ".scss", ".sass"]:
            return "web"
        else:
            # Group by directory
            parts = path.parts
            if len(parts) > 1:
                if "docs" in parts or "documentation" in parts:
                    return "documentation"
                elif "tests" in parts or "test" in parts:
                    return "test"
                elif "config" in parts or "conf" in parts:
                    return "configuration"
                elif "data" in parts:
                    return "data"
            
            return "other"
    
    def generate_impact_analysis_report(self, file_path: str) -> Dict[str, Any]:
        """
        Generate an impact analysis report for a specific file.
        
        Args:
            file_path: Path of the file to analyze
            
        Returns:
            Impact analysis report
        """
        if not self.dependency_graph or file_path not in self.dependency_graph:
            return {
                "file": file_path,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "impact_level": "none",
                "affected_files": [],
                "dependency_chains": []
            }
        
        try:
            # Get downstream dependencies (files affected by changes to this file)
            downstream = list(nx.descendants(self.dependency_graph, file_path))
            
            # Determine impact level
            impact_level = "none"
            if len(downstream) > 10:
                impact_level = "high"
            elif len(downstream) > 5:
                impact_level = "medium"
            elif len(downstream) > 0:
                impact_level = "low"
            
            # Get dependency chains (paths from this file to affected files)
            dependency_chains = []
            for target in downstream[:10]:  # Limit to 10 targets for performance
                try:
                    paths = list(nx.all_simple_paths(self.dependency_graph, file_path, target, cutoff=5))
                    if paths:
                        dependency_chains.append({
                            "target": target,
                            "paths": [{"path": path, "length": len(path)} for path in paths[:3]]  # Limit to 3 paths per target
                        })
                except:
                    pass
            
            # Generate report
            return {
                "file": file_path,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "impact_level": impact_level,
                "affected_files_count": len(downstream),
                "affected_files": downstream[:20],  # Limit to 20 files
                "dependency_chains": dependency_chains
            }
            
        except Exception as e:
            logger.error(f"Error generating impact analysis report: {str(e)}")
            return {
                "file": file_path,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "impact_level": "unknown",
                "error": str(e)
            }